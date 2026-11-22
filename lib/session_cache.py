# -*- coding: utf-8 -*-
"""Caché cifrada de la sesión de GitHub.

``data/pm.data`` guarda el token en claro porque es un JSON legible, y una
lectura fallida de ese archivo dejaba la sesión "a medias": la muralla de login
aparecía aunque hubiera token guardado. Este módulo mantiene una copia cifrada
del token y del perfil en ``data/session.cache`` con una clave derivada de la
máquina, de modo que:

* el arranque puede restaurar la sesión sin volver a pedir el token;
* el token nunca queda en claro en el fichero de caché;
* si ``pm.data`` se corrompe o no se puede leer, la caché cifrada sigue
  permitiendo entrar.

Sólo usa la biblioteca estándar (``hmac``/``hashlib``/``json``) con la misma
construcción HMAC-SHA256 en modo contador que ``lib.iflapp_format``, para no
añadir dependencias.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import platform
import uuid
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from lib.pm_data import _data_dir

_MAGIC = b"PMSESS1\x00"
_NONCE_LEN = 16
_KEY_LEN = 32
_ITERATIONS = 120_000


def _cache_path() -> Path:
    return _data_dir() / "session.cache"


def _machine_secret() -> bytes:
    """Material estable de la máquina para derivar la clave de cifrado.

    Combina el identificador de nodo, el usuario del SO, el nombre de equipo y
    la ruta de datos. No es un secreto fuerte, pero basta para que la caché no
    sea un JSON legible ni portable entre máquinas.
    """
    parts = [
        str(uuid.getnode()),
        os.environ.get("USER") or os.environ.get("USERNAME") or "",
        platform.node(),
        str(_data_dir()),
    ]
    return "\x1f".join(parts).encode("utf-8", "replace")


def _derive_key(salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", _machine_secret(), salt, _ITERATIONS, _KEY_LEN)


def _keystream(key: bytes, nonce: bytes, length: int) -> bytes:
    blocks = []
    counter = 0
    while sum(len(b) for b in blocks) < length:
        blocks.append(hmac.new(key, nonce + counter.to_bytes(8, "big"), hashlib.sha256).digest())
        counter += 1
    return b"".join(blocks)[:length]


def _xor(data: bytes, stream: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(data, stream))


def _encrypt(plaintext: bytes) -> bytes:
    nonce = os.urandom(_NONCE_LEN)
    key = _derive_key(nonce)
    ciphertext = _xor(plaintext, _keystream(key, nonce, len(plaintext)))
    tag = hmac.new(key, nonce + ciphertext, hashlib.sha256).digest()
    return _MAGIC + nonce + tag + ciphertext


def _decrypt(blob: bytes) -> Optional[bytes]:
    if not blob.startswith(_MAGIC):
        return None
    body = blob[len(_MAGIC):]
    if len(body) < _NONCE_LEN + 32:
        return None
    nonce = body[:_NONCE_LEN]
    tag = body[_NONCE_LEN:_NONCE_LEN + 32]
    ciphertext = body[_NONCE_LEN + 32:]
    key = _derive_key(nonce)
    expected = hmac.new(key, nonce + ciphertext, hashlib.sha256).digest()
    if not hmac.compare_digest(tag, expected):
        return None
    return _xor(ciphertext, _keystream(key, nonce, len(ciphertext)))


def save_session(token: str, profile: Dict[str, Any]) -> bool:
    """Guarda la sesión cifrada. Devuelve ``True`` si se escribió."""
    if not token:
        return False
    payload = json.dumps(
        {"token": token, "profile": profile or {}}, ensure_ascii=False
    ).encode("utf-8")
    try:
        path = _cache_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(_encrypt(payload))
        return True
    except OSError:
        return False


def load_session() -> Optional[Tuple[str, Dict[str, Any]]]:
    """Devuelve ``(token, profile)`` de la caché, o ``None`` si no hay."""
    path = _cache_path()
    if not path.is_file():
        return None
    try:
        plaintext = _decrypt(path.read_bytes())
    except OSError:
        return None
    if not plaintext:
        return None
    try:
        data = json.loads(plaintext.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    token = str(data.get("token", "") or "")
    if not token:
        return None
    profile = data.get("profile")
    return token, dict(profile) if isinstance(profile, dict) else {}


def clear_session() -> None:
    """Elimina la caché cifrada de sesión."""
    try:
        _cache_path().unlink(missing_ok=True)
    except OSError:
        pass
