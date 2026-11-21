"""Contenedor determinista y seguro para artefactos compilados desde .mexf."""
from __future__ import annotations

import base64
import hashlib
import hmac
import io
import json
import lzma
import os
import tarfile
from pathlib import Path
from typing import Any

MAGIC = b"ASKSOME1\x00"
KEY = b"Influent.asksome.local.integrity.key"


class AsksomeError(ValueError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def _safe_member_target(destination: Path, member_name: str) -> Path:
    """Resuelve una entrada del TAR dentro de *destination* o lanza ``AsksomeError``.

    Rechaza rutas absolutas POSIX, rutas con unidad de Windows (``C:\\...``,
    ``C:x``), componentes ``..`` y cualquier resolución que escape del destino.
    """
    normalized = member_name.replace("\\", "/")
    if not normalized or normalized in (".", ".."):
        raise AsksomeError(f"ruta no segura: {member_name!r}")
    if normalized.startswith("/") or (
        len(normalized) >= 2 and normalized[0].isalpha() and normalized[1] == ":"
    ):
        raise AsksomeError(f"ruta absoluta no permitida: {member_name!r}")
    parts = [part for part in normalized.split("/") if part not in ("", ".")]
    if not parts or any(part == ".." for part in parts):
        raise AsksomeError(f"ruta no segura: {member_name!r}")
    target = destination.joinpath(*parts)
    try:
        target.resolve().relative_to(destination)
    except ValueError as exc:
        raise AsksomeError(f"la entrada escapa del destino: {member_name!r}") from exc
    return target


_HEADER_TEXT_FIELDS = (
    "format",
    "launcher",
    "compression",
    "encryption",
    "payload_sha256",
    "signature",
    "icon",
)


def _validate_header(header: dict) -> None:
    for field in _HEADER_TEXT_FIELDS:
        if field in header and not isinstance(header[field], str):
            raise AsksomeError(f"cabecera .asksome inválida: {field} debe ser texto")
    if "format_version" in header and not isinstance(header["format_version"], int):
        raise AsksomeError("cabecera .asksome inválida: format_version debe ser entero")
    if not isinstance(header.get("metadata", {}), dict):
        raise AsksomeError("cabecera .asksome inválida: metadata debe ser un objeto")
    manifest = header.get("manifest", [])
    if not isinstance(manifest, list) or not all(isinstance(item, dict) for item in manifest):
        raise AsksomeError("cabecera .asksome inválida: manifest debe ser una lista de objetos")
    if not isinstance(header.get("encryption_params", {}), dict):
        raise AsksomeError("cabecera .asksome inválida: encryption_params debe ser un objeto")


def _read_container(path: Path | str) -> tuple[bytes, dict, int]:
    """Devuelve ``(archivo, cabecera, offset_del_payload)`` validando la cabecera."""
    data = Path(path).read_bytes()
    header_start = len(MAGIC) + 4
    if not data.startswith(MAGIC) or len(data) < header_start:
        raise AsksomeError("cabecera .asksome inválida")
    size = int.from_bytes(data[len(MAGIC):header_start], "little")
    header_end = header_start + size
    if size <= 0 or header_end > len(data):
        raise AsksomeError("cabecera .asksome truncada")
    try:
        header = json.loads(data[header_start:header_end])
    except (ValueError, UnicodeDecodeError) as exc:
        raise AsksomeError("cabecera .asksome corrupta") from exc
    if not isinstance(header, dict):
        raise AsksomeError("cabecera .asksome inválida: se esperaba un objeto")
    _validate_header(header)
    return data, header, header_end


def read_asksome_header(path: Path | str) -> dict:
    return _read_container(path)[1]


def _verified_payload(path: Path | str) -> tuple[dict, bytes]:
    data, header, start = _read_container(path)
    payload = data[start:]
    if hashlib.sha256(payload).hexdigest() != header.get("payload_sha256"):
        raise AsksomeError("digest del payload no coincide")
    expected = header.get("signature", "")
    unsigned = dict(header)
    unsigned.pop("signature", None)
    actual = hmac.new(KEY, _canonical(unsigned) + payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, actual):
        raise AsksomeError("firma .asksome no válida")
    return header, payload


def verify_asksome(path: Path | str) -> dict:
    return _verified_payload(path)[0]


def extract_asksome(path: Path | str, destination: Path | str, *, password: str | None = None) -> list[Path]:
    header, payload = _verified_payload(path)
    if header.get("encryption", "none") != "none":
        from lib import iflapp_format

        payload = iflapp_format._decrypt_payload(payload, password, header.get("encryption_params", {}))
    try:
        raw = lzma.decompress(payload, format=lzma.FORMAT_ALONE)
    except (lzma.LZMAError, EOFError) as exc:
        raise AsksomeError("payload .asksome corrupto") from exc
    target = Path(destination)
    target.mkdir(parents=True, exist_ok=True)
    target = target.resolve()
    files = []
    try:
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r") as tar:
            for member in tar.getmembers():
                if member.issym() or member.islnk():
                    raise AsksomeError("enlaces no permitidos")
                output = _safe_member_target(target, member.name)
                if member.isdir():
                    output.mkdir(parents=True, exist_ok=True)
                elif member.isfile():
                    output.parent.mkdir(parents=True, exist_ok=True)
                    if output.is_symlink():
                        raise AsksomeError(f"el destino ya contiene un symlink: {member.name!r}")
                    source = tar.extractfile(member)
                    if source is None:
                        raise AsksomeError(f"no se pudo leer la entrada: {member.name!r}")
                    output.write_bytes(source.read())
                    files.append(output)
    except AsksomeError:
        raise
    except tarfile.TarError as exc:
        raise AsksomeError("payload .asksome corrupto") from exc
    return files


def _tar_bytes(root: Path) -> tuple[bytes, list[dict[str, Any]]]:
    manifest = []
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w", format=tarfile.PAX_FORMAT) as tar:
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            rel = path.relative_to(root).as_posix()
            info = tar.gettarinfo(str(path), arcname=rel)
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            info.mtime = 0
            info.mode = 0o755 if os.access(path, os.X_OK) else 0o644
            with path.open("rb") as handle:
                data = handle.read()
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
            manifest.append({"path": rel, "sha256": hashlib.sha256(data).hexdigest(), "size": len(data)})
    return stream.getvalue(), manifest


def pack_asksome(staging_dir: Path | str, output_file: Path | str, *, metadata: dict | None = None, launcher: str = "launcher.py", password: str | None = None, icon: bytes | None = None) -> Path:
    root = Path(staging_dir).resolve()
    if not root.is_dir():
        raise AsksomeError(f"No existe staging: {root}")
    tar_data, manifest = _tar_bytes(root)
    payload = lzma.compress(tar_data, format=lzma.FORMAT_ALONE, preset=6)
    # El cifrado reutiliza exactamente la cripto del contenedor .iflapp
    # (AES-256-GCM si hay ``cryptography``, si no HMAC-SHA256-CTR), de modo que
    # la cabecera del .asksome describe el modo real aplicado.
    from lib import iflapp_format

    payload, encryption = iflapp_format._encrypt_payload(payload, password)
    header = {"format": "asksome", "format_version": 1, "launcher": launcher, "manifest": manifest, "metadata": metadata or {}, "compression": "lzma", "encryption": encryption.get("encryption", "none"), "encryption_params": encryption, "payload_sha256": hashlib.sha256(payload).hexdigest()}
    # El icono viaja en claro (base64) para que el shell pueda mostrarlo al
    # pasar el cursor sin descifrar el payload.
    if icon:
        header["icon"] = base64.b64encode(icon).decode("ascii")
    signature = hmac.new(KEY, _canonical(header) + payload, hashlib.sha256).hexdigest()
    header["signature"] = signature
    header_bytes = _canonical(header)
    out = Path(output_file)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(MAGIC + len(header_bytes).to_bytes(4, "little") + header_bytes + payload)
    return out


