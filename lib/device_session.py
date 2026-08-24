# -*- coding: utf-8 -*-
"""Persistencia binaria de una sesión opaca de PackageMaker."""
from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any, Optional

MAGIC = b"PMGH1\0"


def session_path() -> Path:
    root = Path(__file__).resolve().parent.parent / "data"
    root.mkdir(parents=True, exist_ok=True)
    return root / "github.session"


def save_session(ticket: str, profile: dict[str, Any], expires_in: int) -> bool:
    """Guarda un ticket temporal y perfil mínimo como archivo binario privado.

    El ticket no es una contraseña ni un access token de GitHub. Se escribe con
    permisos 0600 y de forma atómica para evitar archivos parciales.
    """
    ticket = str(ticket).strip()
    login = str(profile.get("login", "")).strip()
    if not ticket or not login or expires_in <= 0:
        return False
    payload = {
        "ticket": ticket,
        "profile": {
            "login": login,
            "id": profile.get("id"),
            "name": profile.get("name") or login,
            "avatar_url": profile.get("avatar_url", ""),
            "html_url": profile.get("html_url", f"https://github.com/{login}"),
        },
        "expires_at": int(time.time()) + int(expires_in),
    }
    data = MAGIC + json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    target = session_path()
    fd, temp_name = tempfile.mkstemp(prefix="github.session.", dir=str(target.parent))
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, target)
        try:
            os.chmod(target, 0o600)
        except OSError:
            pass
        return True
    except OSError:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        return False


def load_session() -> Optional[dict[str, Any]]:
    target = session_path()
    try:
        raw = target.read_bytes()
        if not raw.startswith(MAGIC):
            raise ValueError("formato inválido")
        payload = json.loads(raw[len(MAGIC):].decode("utf-8"))
        if int(payload.get("expires_at", 0)) <= int(time.time()):
            clear_session()
            return None
        if not payload.get("ticket") or not payload.get("profile", {}).get("login"):
            raise ValueError("sesión incompleta")
        return payload
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        clear_session()
        return None


def clear_session() -> None:
    try:
        session_path().unlink(missing_ok=True)
    except OSError:
        pass
