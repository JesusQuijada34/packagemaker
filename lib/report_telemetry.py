# -*- coding: utf-8 -*-
"""Datos de entorno que acompañan a un reporte de bug.

Lo que se envía aquí sale de la máquina del usuario, así que la regla es
recolectar sólo lo que sirve para diagnosticar y nunca lo que identifica a la
persona: ni rutas, ni nombre de usuario del sistema, ni variables de entorno,
ni credenciales. ``sanitize`` se aplica al texto libre antes de publicarlo.
"""

from __future__ import annotations

import platform
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

_REPO_ROOT = Path(__file__).resolve().parent.parent

# Rutas absolutas POSIX y Windows (con o sin comillas).
_ABSOLUTE_PATH_RE = re.compile(r"(?<![\w:/~])(?:[A-Za-z]:\\[^\s'\"]+|/(?:[\w.\-]+/)*[\w.\-]+)")
# Valores con pinta de credencial dentro de texto libre.
_SECRET_RE = re.compile(r"(?i)\b(token|password|passwd|secret|api[_-]?key)\b(\s*[=:]\s*)\S+")

_MAX_TEXT_CHARS = 20000

#: El commit no cambia mientras la aplicación corre, pero el panel de Reportes
#: llama a ``collect_environment()`` en cada refresco (y al construirse). Sin
#: memoizar, cada refresco lanzaba ``git rev-parse`` y en Windows ese proceso
#: se paga durante el arranque.
_git_commit_cache: Dict[str, str] = {}


def sanitize(text: str, home: Optional[str] = None) -> str:
    """Quita rutas absolutas y credenciales de un texto libre."""
    value = str(text or "")
    home_path = home or _home()
    if home_path and home_path not in ("~", "/"):
        value = value.replace(home_path, "~")
        value = value.replace(home_path.replace("\\", "/"), "~")
    value = _SECRET_RE.sub(r"\1\2<redacted>", value)
    value = _ABSOLUTE_PATH_RE.sub("<path>", value)
    return value[:_MAX_TEXT_CHARS]


def _home() -> str:
    try:
        return str(Path.home())
    except Exception:
        return ""


def _app_version() -> str:
    try:
        from lib.cliHandler import __version__

        return str(__version__ or "desconocida")
    except Exception:
        return "desconocida"


def _git_commit() -> str:
    """Commit del repo si se ejecuta desde el árbol de trabajo.

    Sin ``git`` o en una instalación congelada no hay commit que reportar: es
    un dato informativo, no un requisito. Se consulta una sola vez por sesión.
    """
    if "value" in _git_commit_cache:
        return _git_commit_cache["value"]
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(_REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        commit = (result.stdout or "").strip()
        commit = commit if re.fullmatch(r"[0-9a-f]{4,40}", commit) else ""
    except (OSError, subprocess.SubprocessError):
        commit = ""
    _git_commit_cache["value"] = commit
    return commit


def _os_version() -> str:
    """Versión legible del SO sin tocar datos personales."""
    try:
        if sys.platform.startswith("win"):
            return platform.version() or platform.release()
        if sys.platform == "darwin":
            return platform.mac_ver()[0] or platform.release()
        # Linux: el nombre de la distribución vive en os-release.
        for path in ("/etc/os-release", "/usr/lib/os-release"):
            try:
                for line in Path(path).read_text(encoding="utf-8").splitlines():
                    if line.startswith("PRETTY_NAME="):
                        return line.split("=", 1)[1].strip().strip('"')
            except OSError:
                continue
        return platform.release()
    except Exception:
        return "desconocida"


def _is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False)) or hasattr(sys, "_MEIPASS")


def _qt_version() -> str:
    try:
        from PyQt6.QtCore import QT_VERSION_STR

        return str(QT_VERSION_STR)
    except Exception:
        return ""


def _ui_language() -> str:
    """Idioma con el que el usuario está viendo la aplicación."""
    try:
        from lib.i18n import i18n

        return str(i18n.get_current_lang() or "")
    except Exception:
        return ""


def collect_environment() -> Dict[str, Any]:
    """Instantánea del entorno para adjuntar al reporte.

    No incluye rutas de usuario, nombre de usuario del SO, hostname ni
    variables de entorno.
    """
    try:
        cpu_count = __import__("os").cpu_count() or 0
    except Exception:
        cpu_count = 0
    return {
        "app_version": _app_version(),
        "commit": _git_commit(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "os": platform.system(),
        "os_version": _os_version(),
        "architecture": platform.machine(),
        "qt_version": _qt_version(),
        "distribution": "congelada" if _is_frozen() else "código fuente",
        "cpu_count": cpu_count,
        "language": _ui_language(),
    }


def _env_label(key: str, fallback: str) -> str:
    """Traduce una etiqueta del entorno; sin i18n usa el español."""
    try:
        from lib.i18n import tr

        translated = tr(f"env.{key}")
        return fallback if translated == f"env.{key}" else translated
    except Exception:
        return fallback


def environment_markdown(environment: Dict[str, Any]) -> str:
    """Tabla markdown con el entorno, lista para pegar en un issue.

    Las etiquetas salen en el idioma con el que el usuario ve la aplicación: la
    tabla se mostraba en español aunque la interfaz estuviera en otro idioma.
    """
    labels = (
        ("app_version", "PackageMaker"),
        ("commit", "Commit"),
        ("python_version", "Python"),
        ("python_implementation", _env_label("implementation", "Implementación")),
        ("os", _env_label("os", "Sistema operativo")),
        ("os_version", _env_label("os_version", "Versión del SO")),
        ("architecture", _env_label("architecture", "Arquitectura")),
        ("qt_version", "Qt"),
        ("distribution", _env_label("distribution", "Distribución")),
        ("cpu_count", _env_label("cpu_count", "Núcleos de CPU")),
        ("language", _env_label("language", "Idioma")),
    )
    rows = [
        f"| {label} | {environment.get(key) or '—'} |"
        for key, label in labels
        if environment.get(key) not in (None, "")
    ]
    header = f"| {_env_label('field', 'Dato')} | {_env_label('value', 'Valor')} |"
    return "\n".join([header, "|---|---|"] + rows)


def fingerprint(kind: str, message: str) -> str:
    """Huella estable de un fallo, para no abrir un issue por cada repetición."""
    import hashlib

    raw = f"{kind}|{message}|{_app_version()}".encode("utf-8", "replace")
    return hashlib.sha256(raw).hexdigest()[:16]
