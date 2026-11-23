# -*- coding: utf-8 -*-
"""Reporte opcional de errores (telemetría) — desactivado por defecto.

El envío sólo ocurre si el usuario lo activó explícitamente **y** configuró un
endpoint. Se ejecuta en un hilo aparte con un tiempo límite corto, de modo que
un servidor lento o caído nunca bloquea la interfaz.

Privacidad: el cuerpo se compone únicamente con la versión de la aplicación, la
versión de Python, la plataforma, el tipo/mensaje de la excepción y la traza
**saneada**. Nunca se envían variables de entorno, credenciales, nombres de
usuario ni rutas absolutas: ``sanitize()`` sustituye la ruta del usuario y
cualquier ruta absoluta por marcadores.
"""

from __future__ import annotations

import json
import os
import platform
import re
import sys
import threading
import traceback
import urllib.request
from typing import Any, Callable, Dict, Optional

# Claves de configuración en ``data/pm.data`` (preferencias del usuario).
SETTING_ENABLED = "telemetry_enabled"
SETTING_ENDPOINT = "telemetry_endpoint"
SETTING_CONSENT = "telemetry_consent_at"

_TIMEOUT_SECONDS = 5.0
_MAX_TRACEBACK_CHARS = 8000

# Ruta absoluta POSIX o Windows, con o sin comillas.
_ABSOLUTE_PATH_RE = re.compile(
    r"(?<![\w:/~])(?:[A-Za-z]:\\[^\s'\"]+|/(?:[\w.\-]+/)*[\w.\-]+)"
)
# Valores con pinta de credencial dentro de un texto libre.
_SECRET_RE = re.compile(
    r"(?i)\b(token|password|passwd|secret|api[_-]?key)\b(\s*[=:]\s*)\S+"
)


def _settings() -> Dict[str, Any]:
    try:
        from lib.pm_data import get_pm_data

        store = get_pm_data()
        return {
            SETTING_ENABLED: bool(store.get_user(SETTING_ENABLED, False)),
            SETTING_ENDPOINT: str(store.get_user(SETTING_ENDPOINT, "") or "").strip(),
        }
    except Exception:
        return {SETTING_ENABLED: False, SETTING_ENDPOINT: ""}


def is_enabled() -> bool:
    """Sólo con consentimiento explícito *y* un endpoint configurado."""
    config = _settings()
    return bool(config.get(SETTING_ENABLED) and config.get(SETTING_ENDPOINT))


def sanitize(text: str, home: Optional[str] = None) -> str:
    """Elimina rutas absolutas y credenciales de un texto libre."""
    value = str(text or "")
    home_path = home or os.path.expanduser("~")
    if home_path and home_path not in ("~", "/"):
        value = value.replace(home_path, "~")
    value = _SECRET_RE.sub(r"\1\2<redacted>", value)
    value = _ABSOLUTE_PATH_RE.sub("<path>", value)
    return value[:_MAX_TRACEBACK_CHARS]


def _app_version() -> str:
    try:
        from lib.cliHandler import __version__

        return str(__version__ or "desconocida")
    except Exception:
        return "desconocida"


def build_payload(
    exc_type: type, exc_value: BaseException, exc_tb, home: Optional[str] = None
) -> Dict[str, Any]:
    """Construye el cuerpo del reporte ya saneado."""
    raw_traceback = "".join(
        traceback.format_exception(exc_type, exc_value, exc_tb)
    )
    return {
        "app": "Influent Package Maker",
        "version": _app_version(),
        "python": platform.python_version(),
        "platform": platform.system(),
        "exception": getattr(exc_type, "__name__", str(exc_type)),
        "message": sanitize(str(exc_value), home=home),
        "traceback": sanitize(raw_traceback, home=home),
    }


def _default_sender(endpoint: str, payload: Dict[str, Any]) -> None:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=_TIMEOUT_SECONDS):
        pass


def report_exception(
    exc_type: type,
    exc_value: BaseException,
    exc_tb,
    sender: Optional[Callable[[str, Dict[str, Any]], None]] = None,
) -> bool:
    """Envía el reporte en segundo plano. Devuelve si se programó el envío.

    Cualquier fallo de red o de configuración se ignora: el reporte de errores
    nunca debe convertirse en un error nuevo para el usuario.
    """
    config = _settings()
    endpoint = str(config.get(SETTING_ENDPOINT) or "")
    if not (config.get(SETTING_ENABLED) and endpoint):
        return False
    try:
        payload = build_payload(exc_type, exc_value, exc_tb)
    except Exception:
        return False

    send = sender or _default_sender

    def _worker() -> None:
        try:
            send(endpoint, payload)
        except Exception:
            pass

    try:
        threading.Thread(target=_worker, name="pm-telemetry", daemon=True).start()
    except Exception:
        return False
    return True


def install_excepthook(
    sender: Optional[Callable[[str, Dict[str, Any]], None]] = None,
) -> None:
    """Encadena el reporte al ``sys.excepthook`` sin alterar su comportamiento."""
    previous = sys.excepthook

    def _hook(exc_type, exc_value, exc_tb):
        try:
            report_exception(exc_type, exc_value, exc_tb, sender=sender)
        finally:
            previous(exc_type, exc_value, exc_tb)

    sys.excepthook = _hook
