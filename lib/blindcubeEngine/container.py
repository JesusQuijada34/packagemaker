# -*- coding: utf-8 -*-
"""Contenedor BlindCube v2 (``.blindkpkg``).

Formato: ``[MAGIC 8B][payload_len u32 LE][meta_len u32 LE][meta JSON][payload]``.

El payload va comprimido con **LZMA** y, opcionalmente, cifrado de extremo a
extremo (AES-256-GCM si ``cryptography`` está instalado; si no, un flujo
HMAC-SHA256 en modo contador *encrypt-then-MAC* con solo la stdlib). BlindCube es
el motor estándar (Python 3.14, Nuitka, Leviathan UI / PyQt6+), pensado para
apps de escritorio, tiendas y servidores.

Este módulo es autocontenido: no importa ``iflapp_format`` ni otros motores.
"""
from __future__ import annotations

import hashlib
import hmac
import io
import json
import lzma
import os
import struct
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

MAGIC = b"BLINDCUB"
FORMAT_EXTENSION = ".blindkpkg"
_MAGIC_LEN = 8
_LEN_FMT = "<I"


class BlindCubeError(RuntimeError):
    """Error al leer o escribir un contenedor ``.blindkpkg``."""


# --------------------------------------------------------------------------- #
# Cifrado (stdlib por defecto; AES-256-GCM si está disponible)
# --------------------------------------------------------------------------- #
def _try_aesgcm():
    try:  # pragma: no cover - depende del entorno
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        return AESGCM
    except Exception:
        return None


def _derive_key(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000, dklen=32)


def _keystream(key: bytes, nonce: bytes, length: int) -> bytes:
    blocks = bytearray()
    counter = 0
    while len(blocks) < length:
        blocks.extend(
            hmac.new(key, nonce + counter.to_bytes(8, "big"), hashlib.sha256).digest()
        )
        counter += 1
    return bytes(blocks[:length])


def _xor(data: bytes, stream: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(data, stream))


def _encrypt(data: bytes, password: Optional[str]) -> Tuple[bytes, Dict]:
    if not password:
        return data, {"encryption": "none"}
    salt = os.urandom(16)
    key = _derive_key(password, salt)
    aesgcm = _try_aesgcm()
    if aesgcm is not None:  # pragma: no cover - depende del entorno
        nonce = os.urandom(12)
        blob = aesgcm(key).encrypt(nonce, data, None)
        return blob, {
            "encryption": "aes-256-gcm",
            "salt": salt.hex(),
            "nonce": nonce.hex(),
        }
    nonce = os.urandom(16)
    cipher = _xor(data, _keystream(key, nonce, len(data)))
    mac = hmac.new(key, nonce + cipher, hashlib.sha256).hexdigest()
    return cipher, {
        "encryption": "hmac-sha256-ctr",
        "salt": salt.hex(),
        "nonce": nonce.hex(),
        "mac": mac,
    }


def _decrypt(data: bytes, password: Optional[str], params: Dict) -> bytes:
    mode = params.get("encryption", "none")
    if mode == "none":
        return data
    if not password:
        raise BlindCubeError("El contenedor está cifrado; se requiere contraseña.")
    salt = bytes.fromhex(params["salt"])
    key = _derive_key(password, salt)
    if mode == "aes-256-gcm":  # pragma: no cover - depende del entorno
        aesgcm = _try_aesgcm()
        if aesgcm is None:
            raise BlindCubeError("Se requiere 'cryptography' para abrir AES-256-GCM.")
        try:
            return aesgcm(key).decrypt(bytes.fromhex(params["nonce"]), data, None)
        except Exception as exc:
            raise BlindCubeError("Contraseña incorrecta o payload corrupto.") from exc
    if mode == "hmac-sha256-ctr":
        nonce = bytes.fromhex(params["nonce"])
        expected = params.get("mac", "")
        actual = hmac.new(key, nonce + data, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, actual):
            raise BlindCubeError("Contraseña incorrecta o payload corrupto.")
        return _xor(data, _keystream(key, nonce, len(data)))
    raise BlindCubeError(f"Cifrado no soportado: {mode}")


# --------------------------------------------------------------------------- #
# Cabecera y contenedor
# --------------------------------------------------------------------------- #
def build_header(payload_len: int, meta: Dict) -> bytes:
    blob = json.dumps(meta, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return (
        MAGIC.ljust(_MAGIC_LEN, b"\x00")
        + struct.pack(_LEN_FMT, payload_len)
        + struct.pack(_LEN_FMT, len(blob))
        + blob
    )


def read_header(container: bytes) -> Tuple[Dict, int]:
    """Lee la cabecera y devuelve ``(meta, offset_payload)``."""
    expected = MAGIC.ljust(_MAGIC_LEN, b"\x00")
    if not container.startswith(expected):
        raise BlindCubeError("Magic bytes del contenedor no coinciden")
    base = _MAGIC_LEN
    (payload_len,) = struct.unpack(_LEN_FMT, container[base : base + 4])
    (blob_len,) = struct.unpack(_LEN_FMT, container[base + 4 : base + 8])
    blob = container[base + 8 : base + 8 + blob_len]
    meta = json.loads(blob.decode("utf-8"))
    meta["payload_len"] = payload_len
    return meta, base + 8 + blob_len


def pack(
    payload: bytes,
    *,
    meta: Optional[Dict] = None,
    password: Optional[str] = None,
) -> bytes:
    """Empaqueta un payload: LZMA + cabecera (y cifrado opcional)."""
    compressed = lzma.compress(payload, format=lzma.FORMAT_ALONE, preset=6)
    encrypted, crypto = _encrypt(compressed, password)
    header_meta = {
        "engine": "blindcube",
        "extension": FORMAT_EXTENSION,
        "compression": "lzma",
        **crypto,
        **(meta or {}),
    }
    return build_header(len(payload), header_meta) + encrypted


def unpack(container: bytes, *, password: Optional[str] = None) -> Tuple[Dict, bytes]:
    """Lee el contenedor y devuelve ``(meta, payload)``."""
    meta, offset = read_header(container)
    encrypted = container[offset:]
    compressed = _decrypt(encrypted, password, meta)
    payload = lzma.decompress(compressed, format=lzma.FORMAT_ALONE)
    return meta, payload


def pack_directory(
    source_dir: Path,
    output_path: Path,
    *,
    meta: Optional[Dict] = None,
    password: Optional[str] = None,
) -> Path:
    """Empaqueta ``source_dir`` (ZIP en memoria) en un ``.blindkpkg``."""
    source_dir = Path(source_dir)
    if not source_dir.is_dir():
        raise BlindCubeError(f"No existe el directorio a empaquetar: {source_dir}")
    buffer = io.BytesIO()
    entries: List[str] = []
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source_dir.rglob("*")):
            if path.is_file():
                arcname = str(path.relative_to(source_dir)).replace("\\", "/")
                archive.write(path, arcname)
                entries.append(arcname)
    manifest = {"entries": entries, **(meta or {})}
    blob = pack(buffer.getvalue(), meta=manifest, password=password)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(blob)
    return output_path


__all__ = [
    "MAGIC",
    "FORMAT_EXTENSION",
    "BlindCubeError",
    "build_header",
    "read_header",
    "pack",
    "unpack",
    "pack_directory",
]
