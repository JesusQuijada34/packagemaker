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


def _safe_member(name: str) -> str:
    name = name.replace("\\", "/")
    if name.startswith("/") or name.startswith("../") or "/../" in name or name == "..":
        raise AsksomeError(f"ruta no segura: {name}")
    return name


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


def read_asksome_header(path: Path | str) -> dict:
    data = Path(path).read_bytes()
    if not data.startswith(MAGIC) or len(data) < len(MAGIC) + 4:
        raise AsksomeError("cabecera .asksome inválida")
    size = int.from_bytes(data[len(MAGIC):len(MAGIC) + 4], "little")
    try:
        return json.loads(data[len(MAGIC) + 4:len(MAGIC) + 4 + size])
    except (ValueError, json.JSONDecodeError) as exc:
        raise AsksomeError("cabecera .asksome corrupta") from exc


def verify_asksome(path: Path | str) -> dict:
    data = Path(path).read_bytes()
    header = read_asksome_header(path)
    start = len(MAGIC) + 4 + len(_canonical(header))
    payload = data[start:]
    if hashlib.sha256(payload).hexdigest() != header.get("payload_sha256"):
        raise AsksomeError("digest del payload no coincide")
    expected = header.get("signature", "")
    unsigned = dict(header)
    unsigned.pop("signature", None)
    actual = hmac.new(KEY, _canonical(unsigned) + payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, actual):
        raise AsksomeError("firma .asksome no válida")
    return header


def extract_asksome(path: Path | str, destination: Path | str, *, password: str | None = None) -> list[Path]:
    header = verify_asksome(path)
    data = Path(path).read_bytes()
    start = len(MAGIC) + 4 + len(_canonical(header))
    payload = data[start:]
    if header.get("encryption", "none") != "none":
        from lib import iflapp_format

        payload = iflapp_format._decrypt_payload(payload, password, header.get("encryption_params", {}))
    raw = lzma.decompress(payload, format=lzma.FORMAT_ALONE)
    target = Path(destination)
    target.mkdir(parents=True, exist_ok=True)
    files = []
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r") as tar:
        for member in tar.getmembers():
            name = _safe_member(member.name)
            if member.issym() or member.islnk():
                raise AsksomeError("enlaces no permitidos")
            if member.isdir():
                (target / name).mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                output = target / name
                output.parent.mkdir(parents=True, exist_ok=True)
                source = tar.extractfile(member)
                output.write_bytes(source.read())
                files.append(output)
    return files
