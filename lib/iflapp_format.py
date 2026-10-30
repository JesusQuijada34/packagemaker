# -*- coding: utf-8 -*-
"""Formato binario ``.iflapp`` v2 (contenedor blindado).

Reemplaza el ZIP histórico por un contenedor propio con cabecera indexada.
La cabecera se escribe en claro y contiene el icono, los metadatos
(``details.xml``) y el manifiesto de archivos, de modo que un lector puede
mostrar la identidad del paquete **sin descifrar ni descomprimir** la carga
útil.

Disposición del archivo::

    [MAGIC 8B][header_len uint32 LE][CABECERA JSON (rellena a header_len)]
    [ICONO][DETAILS][FIRMA][PAYLOAD]

La cabecera JSON declara los desplazamientos absolutos de cada sección. El
``payload`` es un TAR comprimido con LZMA y opcionalmente cifrado con un flujo
de clave derivado de HMAC-SHA256 en modo contador (encrypt-then-MAC). Si el
paquete ``cryptography`` está instalado se prefiere AES-256-GCM. Todo el
mecanismo funciona con la biblioteca estándar.

Este módulo no depende de PyQt6 ni de terceros obligatorios.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import io
import json
import lzma
import os
import struct
import tarfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

MAGIC = b"IFLAPP2\x00"
TRAILER_MAGIC = b"IFLAPPTR"
FORMAT_NAME = "iflapp"
FORMAT_VERSION = 2
HEADER_ALIGN = 4096
_FLAG_COMPRESSED = 0x01
_FLAG_ENCRYPTED = 0x02
_FLAG_SIGNED = 0x04

DEFAULT_SIGNING_KEY = b"Influent.iflapp.default.integrity.key"


class IflappError(ValueError):
    """Error de formato o de integridad de un contenedor ``.iflapp``."""


class IflappSignatureError(IflappError):
    """La firma o el HMAC de integridad no coincide."""


# --------------------------------------------------------------------------- #
# Utilidades internas
# --------------------------------------------------------------------------- #
def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _as_bytes(value, *, what: str) -> bytes:
    """Normaliza un blob de cabecera: acepta ``bytes`` o una ruta a archivo.

    ``icon`` y ``details`` se documentan como bytes, pero desde la GUI es fácil
    pasar una ruta. Sin esta coerción el error sería un ``TypeError`` críptico
    en ``len(icon)``.
    """
    if value is None:
        return b""
    if isinstance(value, (bytes, bytearray)):
        return bytes(value)
    path = Path(value)
    if path.is_file():
        return path.read_bytes()
    raise IflappError(f"{what} debe ser bytes o una ruta existente: {value!r}")


def _align_up(value: int, alignment: int) -> int:
    if alignment <= 1:
        return value
    return ((value + alignment - 1) // alignment) * alignment


def _keystream(key: bytes, nonce: bytes, length: int) -> bytes:
    """Flujo de clave HMAC-SHA256 en modo contador (estándar, sin terceros).

    Cada bloque es ``HMAC-SHA256(key, nonce || counter_be64)``. Es un cifrado
    de flujo simétrico determinista; la confidencialidad se complementa con el
    HMAC de autenticación calculado por separado (encrypt-then-MAC).
    """
    blocks = bytearray()
    counter = 0
    while len(blocks) < length:
        blocks.extend(hmac.new(key, nonce + counter.to_bytes(8, "big"), hashlib.sha256).digest())
        counter += 1
    return bytes(blocks[:length])


def _xor(data: bytes, stream: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(data, stream))


def _derive_key(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000, dklen=32)


def _try_aesgcm():
    try:  # pragma: no cover - depende del entorno
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        return AESGCM
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# Modelo de cabecera
# --------------------------------------------------------------------------- #
@dataclass
class IflappHeader:
    """Cabecera legible sin descomprimir ni descifrar el payload."""

    raw: Dict
    icon: bytes = b""
    details: bytes = b""

    @property
    def format_version(self) -> int:
        return int(self.raw.get("format_version", 0))

    @property
    def compression(self) -> str:
        return str(self.raw.get("payload", {}).get("compression", "none"))

    @property
    def encryption(self) -> str:
        return str(self.raw.get("payload", {}).get("encryption", "none"))

    @property
    def manifest(self) -> List[Dict]:
        return list(self.raw.get("manifest", []))

    @property
    def file_count(self) -> int:
        return int(self.raw.get("payload", {}).get("file_count", len(self.manifest)))

    def identity(self) -> Dict[str, str]:
        """Identidad del paquete tomada de la cabecera (sin descompilar)."""
        return {
            "publisher": self.raw.get("publisher", ""),
            "app": self.raw.get("app", ""),
            "name": self.raw.get("name", ""),
            "version": self.raw.get("version", ""),
            "author": self.raw.get("author", ""),
            "platform": self.raw.get("platform", ""),
            "created": self.raw.get("created", ""),
            "generator": self.raw.get("generator", ""),
        }

    def details_text(self) -> str:
        try:
            return self.details.decode("utf-8")
        except UnicodeDecodeError:
            return self.details.decode("latin-1", errors="replace")


# --------------------------------------------------------------------------- #
# Detección de formato
# --------------------------------------------------------------------------- #
def sniff_format(path: Path | str) -> str:
    """Devuelve ``iflapp2``, ``zip`` o ``unknown``."""
    try:
        with open(path, "rb") as handle:
            head = handle.read(8)
            if head == MAGIC:
                return "iflapp2"
            if head[:2] == b"PK":
                return "zip"
            # La cabecera delantera puede estar dañada; comprobar la cola.
            handle.seek(0, os.SEEK_END)
            total = handle.tell()
            handle.seek(max(0, total - 256))
            if TRAILER_MAGIC in handle.read():
                return "iflapp2"
    except OSError:
        return "unknown"
    return "unknown"


def is_iflapp_v2(path: Path | str) -> bool:
    return sniff_format(path) == "iflapp2"


def is_valid_container(path: Path | str) -> bool:
    """Acepta el formato v2 y, por compatibilidad, el ZIP histórico."""
    return sniff_format(path) in ("iflapp2", "zip")


# --------------------------------------------------------------------------- #
# Empaquetado (payload TAR + compresión + cifrado)
# --------------------------------------------------------------------------- #
def _iter_package_files(package_dir: Path) -> Iterable[Tuple[Path, str]]:
    for root, dirs, files in os.walk(package_dir):
        dirs.sort()
        for name in sorted(files):
            full = Path(root) / name
            rel = full.relative_to(package_dir).as_posix()
            yield full, rel


def _build_payload(package_dir: Path) -> Tuple[bytes, List[Dict]]:
    """Empaqueta *package_dir* en un TAR y devuelve (bytes_tar, manifiesto)."""
    buffer = io.BytesIO()
    manifest: List[Dict] = []
    with tarfile.open(fileobj=buffer, mode="w", format=tarfile.PAX_FORMAT) as tar:
        for full, rel in _iter_package_files(package_dir):
            info = tar.gettarinfo(str(full), arcname=rel)
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            info.mtime = 0
            try:
                with open(full, "rb") as handle:
                    tar.addfile(info, handle)
            except OSError as exc:
                raise IflappError(f"No se pudo leer {rel}: {exc}") from exc
            manifest.append(
                {
                    "path": rel,
                    "size": info.size,
                    "mode": int(info.mode),
                    "sha256": _sha256(full.read_bytes()),
                }
            )
    return buffer.getvalue(), manifest


def _compress(data: bytes, codec: str) -> bytes:
    if codec == "none":
        return data
    if codec == "lzma":
        return lzma.compress(data, format=lzma.FORMAT_ALONE, preset=6)
    raise IflappError(f"Códec de compresión no soportado: {codec!r}")


def _decompress(data: bytes, codec: str) -> bytes:
    if codec == "none":
        return data
    if codec == "lzma":
        return lzma.decompress(data, format=lzma.FORMAT_ALONE)
    raise IflappError(f"Códec de compresión no soportado: {codec!r}")


def _encrypt_payload(data: bytes, password: Optional[str]) -> Tuple[bytes, Dict]:
    if not password:
        return data, {"encryption": "none"}
    salt = os.urandom(16)
    nonce = os.urandom(12)
    key = _derive_key(password, salt)
    aes = _try_aesgcm()
    if aes is not None:
        sealed = aes(key).encrypt(nonce, data, None)
        return sealed, {
            "encryption": "aes-256-gcm",
            "kdf": "pbkdf2-sha256",
            "iterations": 200_000,
            "salt": base64.b64encode(salt).decode("ascii"),
            "nonce": base64.b64encode(nonce).decode("ascii"),
        }
    stream = _keystream(key, nonce, len(data))
    mac = hmac.new(key, nonce + data, hashlib.sha256).hexdigest()
    return _xor(data, stream), {
        "encryption": "hmac-sha256-ctr",
        "kdf": "pbkdf2-sha256",
        "iterations": 200_000,
        "salt": base64.b64encode(salt).decode("ascii"),
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "mac": mac,
    }


def _decrypt_payload(data: bytes, password: Optional[str], params: Dict) -> bytes:
    mode = params.get("encryption", "none")
    if mode == "none":
        return data
    if not password:
        raise IflappError("El paquete está cifrado y no se proporcionó contraseña.")
    salt = base64.b64decode(params["salt"])
    nonce = base64.b64decode(params["nonce"])
    key = _derive_key(password, salt)
    if mode == "aes-256-gcm":
        aes = _try_aesgcm()
        if aes is None:
            raise IflappError("Se requiere el paquete 'cryptography' para abrir AES-256-GCM.")
        return aes(key).decrypt(nonce, data, None)
    if mode == "hmac-sha256-ctr":
        expected = params.get("mac", "")
        actual = hmac.new(key, nonce + _xor(data, _keystream(key, nonce, len(data))), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, actual):
            raise IflappSignatureError("El MAC del payload cifrado no coincide.")
        return _xor(data, _keystream(key, nonce, len(data)))
    raise IflappError(f"Modo de cifrado no soportado: {mode!r}")


# --------------------------------------------------------------------------- #
# Firma
# --------------------------------------------------------------------------- #
def _canonical_signing_bytes(header: Dict, payload_digest: str) -> bytes:
    """Entrada de firma: cabecera sin el valor de firma + digest del payload."""
    trimmed = json.loads(json.dumps(header))
    sig = trimmed.get("sections", {}).get("signature")
    if isinstance(sig, dict):
        sig.pop("value", None)
    canonical = json.dumps(trimmed, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return canonical + b"\n" + payload_digest.encode("ascii")


def _sign(header: Dict, payload_digest: str, key: bytes) -> Dict:
    message = _canonical_signing_bytes(header, payload_digest)
    return {"alg": "hmac-sha256", "value": hmac.new(key, message, hashlib.sha256).hexdigest()}


def _verify(header: Dict, payload_digest: str, key: bytes) -> bool:
    sig = header.get("sections", {}).get("signature")
    if not isinstance(sig, dict) or sig.get("alg") != "hmac-sha256":
        return False
    expected = sig.get("value", "")
    actual = _sign(header, payload_digest, key)["value"]
    return hmac.compare_digest(expected, actual)


# --------------------------------------------------------------------------- #
# Escritura del contenedor
# --------------------------------------------------------------------------- #
def _build_header_blob(header: Dict, header_len: int) -> bytes:
    blob = json.dumps(header, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if len(blob) > header_len:
        raise IflappError("La cabecera excede el tamaño reservado.")
    return blob + b" " * (header_len - len(blob))


def pack_iflapp(
    package_dir: Path | str,
    output_file: Path | str,
    *,
    icon: Optional[bytes] = None,
    icon_name: str = "app-icon.ico",
    details: Optional[bytes] = None,
    details_name: str = "details.xml",
    identity: Optional[Dict[str, str]] = None,
    compression: str = "lzma",
    password: Optional[str] = None,
    signing_key: bytes = DEFAULT_SIGNING_KEY,
    generator: str = "Influent Package Maker",
) -> Path:
    """Crea un ``.iflapp`` v2 a partir de *package_dir*."""
    package_dir = Path(package_dir)
    output_file = Path(output_file)
    if not package_dir.is_dir():
        raise IflappError(f"No existe la carpeta de paquete: {package_dir}")

    tar_bytes, manifest = _build_payload(package_dir)
    if not manifest:
        raise IflappError("El paquete está vacío; no se generó ningún .iflapp.")

    if details is None:
        candidate = package_dir / details_name
        if candidate.is_file():
            details = candidate.read_bytes()
    if icon is None:
        for candidate in (package_dir / "app" / icon_name, package_dir / icon_name):
            if candidate.is_file():
                icon = candidate.read_bytes()
                break
    icon = _as_bytes(icon, what="icon")
    details = _as_bytes(details, what="details")

    compressed = _compress(tar_bytes, compression)
    payload_bytes, enc_params = _encrypt_payload(compressed, password)
    payload_digest = _sha256(payload_bytes)

    meta = dict(identity or {})
    flags = 0
    if compression != "none":
        flags |= _FLAG_COMPRESSED
    if enc_params["encryption"] != "none":
        flags |= _FLAG_ENCRYPTED
    flags |= _FLAG_SIGNED

    header_len = HEADER_ALIGN
    header: Dict = {}
    for _ in range(8):
        sections_start = 8 + 4 + header_len
        icon_off = sections_start
        details_off = icon_off + len(icon)
        signature_off = details_off + len(details)
        payload_off = signature_off + 64  # firma hex sha256 = 64 bytes

        header = {  # type: ignore[assignment]
            "format": FORMAT_NAME,
            "format_version": FORMAT_VERSION,
            "generator": generator,
            "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "flags": flags,
            "publisher": meta.get("publisher", ""),
            "app": meta.get("app", ""),
            "name": meta.get("name", ""),
            "version": meta.get("version", ""),
            "author": meta.get("author", ""),
            "platform": meta.get("platform", ""),
            "correlationid": meta.get("correlationid", ""),
            "sections": {
                "icon": {"name": icon_name, "offset": icon_off, "size": len(icon), "sha256": _sha256(icon)},
                "details": {
                    "name": details_name,
                    "offset": details_off,
                    "size": len(details),
                    "sha256": _sha256(details),
                },
                "signature": {"alg": "hmac-sha256", "offset": signature_off, "size": 64, "value": ""},
            },
            "payload": {
                "offset": payload_off,
                "size": len(payload_bytes),
                "sha256": payload_digest,
                "raw_size": len(tar_bytes),
                "compression": compression,
                "file_count": len(manifest),
                **enc_params,
            },
            "manifest": manifest,
        }
        blob = _build_header_blob(header, header_len)
        if len(blob) <= header_len:
            break
        header_len = _align_up(len(blob) + 64, HEADER_ALIGN)

    signature = _sign(header, payload_digest, signing_key)
    header["sections"]["signature"]["value"] = signature["value"]
    header_blob = _build_header_blob(header, header_len)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "wb") as handle:
        handle.write(MAGIC)
        handle.write(struct.pack("<I", header_len))
        handle.write(header_blob)
        handle.write(icon)
        handle.write(details)
        handle.write(signature["value"].encode("ascii"))
        handle.write(payload_bytes)
        # Cola redundante: permite recuperar la cabecera aunque la parte
        # delantera se corrompa (resistencia a daño parcial).
        handle.write(TRAILER_MAGIC)
        handle.write(struct.pack("<I", header_len))
        handle.write(header_blob)
        handle.write(signature["value"].encode("ascii"))
    return output_file


# --------------------------------------------------------------------------- #
# Lectura de cabecera (sin descomprimir ni descifrar)
# --------------------------------------------------------------------------- #
def read_iflapp_header(path: Path | str, *, include_blobs: bool = True) -> IflappHeader:
    """Lee la cabecera y devuelve icono y metadatos sin tocar el payload."""
    path = Path(path)
    with open(path, "rb") as handle:
        magic = handle.read(len(MAGIC))
        if magic == MAGIC:
            (header_len,) = struct.unpack("<I", handle.read(4))
            if header_len <= 0 or header_len > 64 * 1024 * 1024:
                raise IflappError("Longitud de cabecera inválida.")
            blob = handle.read(header_len)
        else:
            # Recuperación: la cabecera delantera está dañada; usar la cola.
            trailer = _read_trailer(handle)
            if trailer is None:
                raise IflappError("El archivo no es un contenedor .iflapp v2.")
            header_len, blob = trailer
        try:
            header = json.loads(blob.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise IflappError(f"Cabecera JSON corrupta: {exc}") from exc

        icon = details = b""
        if include_blobs:
            icon = _read_section(handle, header, "icon")
            details = _read_section(handle, header, "details")
    return IflappHeader(raw=header, icon=icon, details=details)


def _read_trailer(handle) -> Optional[Tuple[int, bytes]]:
    """Localiza la cabecera redundante al final del contenedor."""
    handle.seek(0, os.SEEK_END)
    total = handle.tell()
    handle.seek(max(0, total - 256))
    tail = handle.read()
    index = tail.rfind(TRAILER_MAGIC)
    if index < 0:
        return None
    start = total - len(tail) + index + len(TRAILER_MAGIC)
    handle.seek(start)
    raw_len = handle.read(4)
    if len(raw_len) != 4:
        return None
    (header_len,) = struct.unpack("<I", raw_len)
    if header_len <= 0 or header_len > 64 * 1024 * 1024:
        return None
    return header_len, handle.read(header_len)


def _read_section(handle, header: Dict, key: str) -> bytes:
    section = header.get("sections", {}).get(key)
    if not isinstance(section, dict):
        return b""
    size = int(section.get("size", 0))
    if size <= 0:
        return b""
    offset = int(section.get("offset", 0))
    handle.seek(offset)
    data = handle.read(size)
    expected = section.get("sha256")
    if expected and _sha256(data) != expected:
        raise IflappError(f"La sección {key!r} no coincide con su digest.")
    return data


def verify_iflapp(path: Path | str, *, signing_key: bytes = DEFAULT_SIGNING_KEY) -> Dict:
    """Verifica estructura, digests y firma sin extraer el payload."""
    path = Path(path)
    header = read_iflapp_header(path, include_blobs=False)
    size = path.stat().st_size
    payload = header.raw.get("payload", {})
    payload_off = int(payload.get("offset", 0))
    payload_size = int(payload.get("size", 0))
    if payload_off + payload_size > size:
        raise IflappError("El payload declarado excede el tamaño del archivo.")
    with open(path, "rb") as handle:
        handle.seek(payload_off)
        payload_bytes = handle.read(payload_size)
    digest = _sha256(payload_bytes)
    if digest != payload.get("sha256"):
        raise IflappError("El digest del payload no coincide.")
    signed = _verify(header.raw, digest, signing_key)
    if not signed:
        raise IflappSignatureError("La firma del paquete no es válida.")
    return {
        "valid": True,
        "signed": signed,
        "format_version": header.format_version,
        "file_count": header.file_count,
        "identity": header.identity(),
        "payload_size": payload_size,
        "raw_size": int(payload.get("raw_size", 0)),
        "compression": header.compression,
        "encryption": header.encryption,
    }


# --------------------------------------------------------------------------- #
# Extracción
# --------------------------------------------------------------------------- #
def _safe_member_target(destination: Path, member_name: str) -> Path:
    normalized = member_name.replace("\\", "/")
    if not normalized or normalized == ".":
        return destination
    if normalized.startswith("/") or (len(normalized) >= 2 and normalized[0].isalpha() and normalized[1] == ":"):
        raise IflappError(f"Ruta absoluta no permitida: {member_name!r}")
    parts = [part for part in normalized.split("/") if part not in ("", ".")]
    if any(part == ".." for part in parts):
        raise IflappError(f"Path traversal detectado: {member_name!r}")
    target = destination.joinpath(*parts)
    try:
        target.resolve().relative_to(destination)
    except ValueError as exc:
        raise IflappError(f"La entrada escapa del destino: {member_name!r}") from exc
    return target


def read_iflapp_payload(path: Path | str, *, password: Optional[str] = None) -> bytes:
    """Devuelve el TAR descomprimido (y descifrado si aplica) en memoria."""
    path = Path(path)
    header = read_iflapp_header(path, include_blobs=False)
    payload = header.raw.get("payload", {})
    payload_off = int(payload.get("offset", 0))
    payload_size = int(payload.get("size", 0))
    with open(path, "rb") as handle:
        handle.seek(payload_off)
        stored = handle.read(payload_size)
    if payload.get("sha256") and _sha256(stored) != payload["sha256"]:
        raise IflappError("El digest del payload no coincide.")
    decrypted = _decrypt_payload(stored, password, payload)
    return _decompress(decrypted, payload.get("compression", "none"))


def extract_iflapp(
    path: Path | str,
    destination: Path | str,
    *,
    password: Optional[str] = None,
    verify_signature: bool = True,
    signing_key: bytes = DEFAULT_SIGNING_KEY,
) -> List[Path]:
    """Extrae un ``.iflapp`` v2 (o ZIP histórico) en *destination*."""
    path = Path(path)
    fmt = sniff_format(path)
    if fmt == "zip":
        return _extract_legacy_zip(path, destination)
    if fmt != "iflapp2":
        raise IflappError(f"Formato de contenedor no reconocido: {path}")

    if verify_signature:
        verify_iflapp(path, signing_key=signing_key)

    destination_path = Path(destination)
    destination_path.mkdir(parents=True, exist_ok=True)
    destination_path = destination_path.resolve()

    tar_bytes = read_iflapp_payload(path, password=password)
    extracted: List[Path] = []
    with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode="r") as tar:
        members = tar.getmembers()
        for member in members:
            if member.issym() or member.islnk():
                raise IflappError(f"Enlaces no permitidos en el paquete: {member.name!r}")
            if not (member.isfile() or member.isdir()):
                continue
            target = _safe_member_target(destination_path, member.name)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                extracted.append(target)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            source = tar.extractfile(member)
            if source is None:
                continue
            with target.open("wb") as output:
                output.write(source.read())
            mode = member.mode & 0o777
            if mode:
                try:
                    os.chmod(target, mode)
                except OSError:
                    pass
            extracted.append(target)
    return extracted


def _extract_legacy_zip(path: Path, destination: Path | str) -> List[Path]:
    """Compatibilidad: extrae el ZIP histórico con las salvaguardas de lib.safe_zip."""
    import zipfile

    from lib.safe_zip import safe_extract_zip

    with zipfile.ZipFile(path, "r") as archive:
        return safe_extract_zip(archive, destination)


def list_iflapp(path: Path | str) -> List[Dict]:
    """Lista el contenido usando sólo la cabecera (sin descomprimir)."""
    path = Path(path)
    if sniff_format(path) == "zip":
        import zipfile

        with zipfile.ZipFile(path, "r") as archive:
            return [{"path": info.filename, "size": info.file_size} for info in archive.infolist()]
    header = read_iflapp_header(path, include_blobs=False)
    return header.manifest


def export_header_assets(path: Path | str, out_dir: Path | str) -> Dict[str, Optional[str]]:
    """Extrae sólo el icono y los detalles leídos de la cabecera."""
    header = read_iflapp_header(path)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written: Dict[str, Optional[str]] = {"icon": None, "details": None}
    icon_name = header.raw.get("sections", {}).get("icon", {}).get("name", "app-icon.ico")
    details_name = header.raw.get("sections", {}).get("details", {}).get("name", "details.xml")
    if header.icon:
        icon_path = out / Path(icon_name).name
        icon_path.write_bytes(header.icon)
        written["icon"] = str(icon_path)
    if header.details:
        details_path = out / Path(details_name).name
        details_path.write_bytes(header.details)
        written["details"] = str(details_path)
    return written
