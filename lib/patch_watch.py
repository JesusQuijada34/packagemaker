# -*- coding: utf-8 -*-
"""Vigilancia de parches: avisa de commits nuevos sin tocar la instalación.

Primera etapa de **Q-013 / F-006** (issue del propietario, «que updater.py
notificara en segundo plano estando compilado o no sobre nuevos commits y
parches de seguridad»). Esta etapa es **sólo de lectura**: consulta la rama
``main`` del repositorio con un ``GET`` anónimo, compara con el commit local y
devuelve un estado. No descarga, no compila, no reemplaza archivos y no escribe
credenciales; la descarga y la aplicación del parche llegan en una etapa
posterior, cuando exista verificación de integridad y reinicio controlado.

Qué sale del equipo: una petición ``GET`` a ``api.github.com`` sin token y sin
datos del usuario. Nada del proyecto, ni rutas, ni credenciales.

Se desactiva con ``PM_PATCH_CHECK=0`` (lo usa la suite) o con el ajuste
``patch_check_enabled`` de ``data/pm.data``, y se salta por completo en modo
red «uso medido».
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional

REPO = "JesusQuijada34/packagemaker"
BRANCH = "main"
API_URL = f"https://api.github.com/repos/{REPO}/commits/{BRANCH}"
USER_AGENT = "InfluentPackageMaker-patch-watch"
DISABLE_ENV = "PM_PATCH_CHECK"
STATE_FILE = "patch_state.json"
DEFAULT_INTERVAL_HOURS = 6.0

NETWORK_UNRESTRICTED = "unrestricted"
NETWORK_METERED = "metered"

STATUS_DISABLED = "disabled"
STATUS_METERED = "metered"
STATUS_OFFLINE = "offline"
STATUS_UP_TO_DATE = "up_to_date"
STATUS_AVAILABLE = "available"
STATUS_UNKNOWN = "unknown"


class PatchWatchError(RuntimeError):
    """La consulta al repositorio no se pudo completar."""


@dataclass(frozen=True)
class Commit:
    sha: str
    message: str = ""
    date: str = ""

    @property
    def short(self) -> str:
        return self.sha[:7]


@dataclass(frozen=True)
class PatchStatus:
    kind: str
    local: str = ""
    remote: str = ""
    message: str = ""
    detail: str = ""
    checked_at: float = 0.0

    @property
    def has_patch(self) -> bool:
        return self.kind == STATUS_AVAILABLE

    @property
    def short_remote(self) -> str:
        return self.remote[:7]


def is_frozen() -> bool:
    """True cuando el programa corre compilado (PyInstaller, Nuitka, zipapp)."""
    return bool(getattr(sys, "frozen", False)) or hasattr(sys, "_MEIPASS") or bool(
        getattr(sys, "compiled", False)
    )


def disabled_by_env() -> bool:
    return os.environ.get(DISABLE_ENV, "1").strip() == "0"


def resolve_network_mode(value: object = None) -> str:
    """Normaliza el modo de red; sin preferencia se usa «sin restricción»."""
    if value is None:
        try:
            from lib.pm_data import get_pm_data

            value = get_pm_data().get_user("network_mode", NETWORK_UNRESTRICTED)
        except Exception:
            value = NETWORK_UNRESTRICTED
    text = str(value or "").strip().lower()
    if text in {NETWORK_METERED, "metered", "uso medido", "medido"}:
        return NETWORK_METERED
    return NETWORK_UNRESTRICTED


def _app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def state_path(root: Optional[os.PathLike] = None) -> Path:
    base = Path(root) if root is not None else _app_root()
    return base / "data" / STATE_FILE


def read_state(path: Optional[os.PathLike] = None) -> Dict[str, Any]:
    target = Path(path) if path is not None else state_path()
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def write_state(values: Dict[str, Any], path: Optional[os.PathLike] = None) -> bool:
    """Escribe el estado tolerando una instalación de sólo lectura."""
    target = Path(path) if path is not None else state_path()
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        merged = read_state(target)
        merged.update(values)
        target.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    except OSError:
        return False


def last_check(path: Optional[os.PathLike] = None) -> float:
    try:
        return float(read_state(path).get("last_check") or 0.0)
    except (TypeError, ValueError):
        return 0.0


def should_check(
    interval_hours: float = DEFAULT_INTERVAL_HOURS,
    path: Optional[os.PathLike] = None,
    now: Optional[float] = None,
) -> bool:
    moment = time.time() if now is None else float(now)
    previous = last_check(path)
    if previous <= 0:
        return True
    interval = max(0.0, float(interval_hours)) * 3600.0
    return moment - previous >= interval


def _git_dir(root: Path) -> Optional[Path]:
    marker = root / ".git"
    if marker.is_dir():
        return marker
    if marker.is_file():
        try:
            text = marker.read_text(encoding="utf-8").strip()
        except OSError:
            return None
        if text.startswith("gitdir:"):
            target = Path(text.split(":", 1)[1].strip())
            return target if target.is_absolute() else (root / target)
    return None


def _git_head(root: Path) -> str:
    """Commit de ``HEAD`` leyendo ``.git`` directamente (sin lanzar git)."""
    git_dir = _git_dir(root)
    if git_dir is None:
        return ""
    try:
        head = (git_dir / "HEAD").read_text(encoding="utf-8").strip()
    except OSError:
        return ""
    if not head.startswith("ref:"):
        return head if len(head) >= 7 else ""
    ref = head.split(":", 1)[1].strip()
    for candidate in (git_dir / ref, git_dir / "refs" / "heads" / "main"):
        try:
            sha = candidate.read_text(encoding="utf-8").strip()
        except OSError:
            continue
        if sha:
            return sha
    try:  # Repositorio empaquetado: la referencia vive en packed-refs.
        for line in (git_dir / "packed-refs").read_text(encoding="utf-8").splitlines():
            if line.endswith(f" {ref}"):
                return line.split(" ", 1)[0]
    except OSError:
        pass
    return ""


def local_commit(
    root: Optional[os.PathLike] = None, path: Optional[os.PathLike] = None
) -> str:
    """Commit de referencia local: parche aplicado, si lo hay, o ``HEAD``."""
    applied = str(read_state(path).get("applied_commit") or "").strip()
    if applied:
        return applied
    return _git_head(Path(root) if root is not None else _app_root())


def parse_commit_payload(payload: Any) -> Commit:
    if not isinstance(payload, dict):
        raise PatchWatchError("respuesta inesperada del repositorio")
    sha = str(payload.get("sha") or "").strip()
    if len(sha) < 7:
        raise PatchWatchError("la respuesta no trae un commit válido")
    commit = payload.get("commit") if isinstance(payload.get("commit"), dict) else {}
    message = str(commit.get("message") or "").strip().splitlines()
    author = commit.get("author") if isinstance(commit.get("author"), dict) else {}
    return Commit(
        sha=sha,
        message=message[0] if message else "",
        date=str(author.get("date") or ""),
    )


def _default_opener(url: str, timeout: float):
    request = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"}
    )
    return urllib.request.urlopen(request, timeout=timeout)


def fetch_latest_commit(
    opener: Optional[Callable[..., Any]] = None, timeout: float = 8.0
) -> Commit:
    """Lee el último commit de ``main``. Sólo ``GET``; nunca envía credenciales."""
    fetch = opener or _default_opener
    try:
        with fetch(API_URL, timeout=timeout) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        raise PatchWatchError(f"HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise PatchWatchError(str(getattr(exc, "reason", exc))) from exc
    try:
        payload = json.loads(raw.decode("utf-8") if isinstance(raw, bytes) else str(raw))
    except (ValueError, UnicodeDecodeError) as exc:
        raise PatchWatchError("respuesta ilegible del repositorio") from exc
    return parse_commit_payload(payload)


def check_for_patch(
    root: Optional[os.PathLike] = None,
    *,
    opener: Optional[Callable[..., Any]] = None,
    enabled: bool = True,
    network_mode: object = None,
    timeout: float = 8.0,
    path: Optional[os.PathLike] = None,
    now: Optional[float] = None,
) -> PatchStatus:
    """Estado del parche sin modificar nada de la instalación."""
    moment = time.time() if now is None else float(now)
    if not enabled or disabled_by_env():
        return PatchStatus(STATUS_DISABLED, checked_at=moment)
    if resolve_network_mode(network_mode) == NETWORK_METERED:
        return PatchStatus(STATUS_METERED, checked_at=moment)
    try:
        latest = fetch_latest_commit(opener=opener, timeout=timeout)
    except PatchWatchError as exc:
        return PatchStatus(STATUS_OFFLINE, detail=str(exc), checked_at=moment)

    local = local_commit(root, path)
    write_state({"last_check": moment, "last_remote": latest.sha}, path)
    if not local:
        return PatchStatus(
            STATUS_UNKNOWN,
            remote=latest.sha,
            message=latest.message,
            detail="no se pudo determinar el commit local",
            checked_at=moment,
        )
    kind = STATUS_UP_TO_DATE if local == latest.sha else STATUS_AVAILABLE
    return PatchStatus(
        kind,
        local=local,
        remote=latest.sha,
        message=latest.message,
        checked_at=moment,
    )


def mark_applied(sha: str, path: Optional[os.PathLike] = None) -> bool:
    """Marca el commit aplicado (lo usará la etapa de instalación del parche)."""
    value = str(sha or "").strip()
    if len(value) < 7:
        return False
    return write_state({"applied_commit": value, "applied_at": time.time()}, path)
