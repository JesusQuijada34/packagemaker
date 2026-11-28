# -*- coding: utf-8 -*-
"""Instancia única de la aplicación (issue #25 / R-3d6a8f25).

Dos ventanas a la vez reescriben el mismo ``data/pm.data`` con
``PMDataStore.save()`` (que guarda el archivo entero: la última descarta los
ajustes de la otra) y comparten la carpeta de build del proyecto, así que dos
compilaciones simultáneas se pisan.

El cerrojo es un bloqueo **del sistema operativo** sobre un archivo (``flock``
en POSIX, ``msvcrt.locking`` en Windows). El kernel lo libera al terminar el
proceso, incluso si muere de golpe: no hay cerrojos huérfanos que bloqueen el
programa para siempre ni PIDs reciclados que se confundan con una instancia
viva. Dentro del archivo se guarda el PID del dueño, sólo para poder decir cuál
es la instancia que ya está abierta.

Se desactiva con ``PM_SINGLE_INSTANCE=0`` (lo usa la suite) y
``PM_SINGLE_INSTANCE_DIR`` cambia la carpeta del cerrojo (también para pruebas).
"""

from __future__ import annotations

import atexit
import os
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

DISABLE_ENV = "PM_SINGLE_INSTANCE"
DIR_ENV = "PM_SINGLE_INSTANCE_DIR"
APP_NAME = "Influent Package Maker"
LOCK_NAME = "packagemaker.lock"
# Rechazar un segundo arranque es el resultado esperado, no un fallo del
# programa: el proceso sale limpio para no asustar a los lanzadores.
EXIT_ALREADY_RUNNING = 0
_OFF_VALUES = {"0", "no", "false", "off"}
# El primer byte reserva la región que se bloquea; el PID se escribe después.
_RESERVED = b"\n"
_OWNER_WAIT_SECONDS = 0.5
_UNSUPPORTED_ERRNOS = {
    getattr(os, "EOPNOTSUPP", -1),
    getattr(os, "ENOLCK", -1),
    getattr(os, "EINVAL", -1),
}

_HELD: Dict[Path, "InstanceLock"] = {}


def enabled() -> bool:
    """Indica si la guarda está activa (por defecto sí)."""
    value = os.environ.get(DISABLE_ENV, "1")
    return value.strip().lower() not in _OFF_VALUES


def _user_key() -> str:
    try:
        return f"u{os.getuid()}"
    except AttributeError:  # Windows no tiene os.getuid()
        name = os.environ.get("USERNAME") or os.environ.get("USER") or "user"
        return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in name)


def lock_path() -> Path:
    """Ruta del cerrojo: una por usuario para que dos instalaciones no choquen."""
    override = os.environ.get(DIR_ENV)
    base = Path(override) if override else Path(tempfile.gettempdir())
    return base / f"{APP_NAME.replace(' ', '-').lower()}-{_user_key()}.lock"


def read_pid(path: Path) -> Optional[int]:
    """PID guardado en el cerrojo, o ``None`` si falta o está corrupto."""
    try:
        text = Path(path).read_text(encoding="utf-8").strip()
    except (OSError, UnicodeDecodeError):
        return None
    try:
        return int(text)
    except ValueError:
        return None


def _try_lock(fd: int) -> Optional[bool]:
    """Intenta bloquear el archivo.

    Devuelve ``True`` si se tomó, ``False`` si otra instancia lo retiene y
    ``None`` si el sistema de archivos no soporta el bloqueo (se deja arrancar
    antes que impedir el uso del programa por un problema del entorno).
    """
    try:
        if os.name == "nt":
            import msvcrt

            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as exc:
        if exc.errno in _UNSUPPORTED_ERRNOS:
            return None
        return False
    return True


def _write_pid(fd: int, pid: int) -> None:
    payload = str(pid).encode("ascii")
    os.lseek(fd, len(_RESERVED), os.SEEK_SET)
    os.write(fd, payload)
    os.ftruncate(fd, len(_RESERVED) + len(payload))


def _wait_for_owner(path: Path) -> Optional[int]:
    deadline = time.monotonic() + _OWNER_WAIT_SECONDS
    while True:
        owner = read_pid(path)
        if owner is not None or time.monotonic() >= deadline:
            return owner
        time.sleep(0.02)


@dataclass
class InstanceLock:
    """Resultado de ``claim()``: el cerrojo tomado o el dueño que lo retiene."""

    path: Path
    acquired: bool
    owner_pid: Optional[int] = None
    holds_file: bool = False
    fd: Optional[int] = field(default=None, repr=False, compare=False)

    def release(self) -> None:
        """Cierra el descriptor (el kernel suelta el bloqueo) y retira el archivo."""
        if not self.holds_file:
            return
        self.holds_file = False
        _HELD.pop(self.path, None)
        if self.fd is not None:
            try:
                os.close(self.fd)
            except OSError:
                pass
            self.fd = None
        try:
            self.path.unlink()
        except OSError:
            pass

    def __enter__(self) -> "InstanceLock":
        return self

    def __exit__(self, *exc_info) -> None:
        self.release()


def claim(path: Optional[Path] = None, pid: Optional[int] = None) -> InstanceLock:
    """Toma el cerrojo de instancia única.

    Devuelve siempre un ``InstanceLock``; ``acquired`` es ``False`` sólo cuando
    otra instancia viva lo retiene, y entonces ``owner_pid`` dice cuál es.
    """
    target = Path(path) if path is not None else lock_path()
    pid = os.getpid() if pid is None else int(pid)

    if not enabled():
        return InstanceLock(path=target, acquired=True, owner_pid=pid)

    held = _HELD.get(target)
    if held is not None and held.holds_file:
        # Este mismo proceso ya tiene el cerrojo: no se autobloquea.
        return held

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(target, os.O_RDWR | os.O_CREAT, 0o600)
    except OSError:
        return InstanceLock(path=target, acquired=True, owner_pid=pid)

    try:
        if os.fstat(fd).st_size == 0:
            os.write(fd, _RESERVED)
        status = _try_lock(fd)
        if status is False:
            os.close(fd)
            return InstanceLock(
                path=target, acquired=False, owner_pid=_wait_for_owner(target)
            )
        if status is None:
            os.close(fd)
            return InstanceLock(path=target, acquired=True, owner_pid=pid)
        _write_pid(fd, pid)
    except OSError:
        os.close(fd)
        return InstanceLock(path=target, acquired=True, owner_pid=pid)

    lock = InstanceLock(target, acquired=True, owner_pid=pid, holds_file=True, fd=fd)
    _HELD[target] = lock
    atexit.register(lock.release)
    return lock


def already_running_message(owner_pid: Optional[int]) -> str:
    pid = str(owner_pid) if owner_pid else "desconocido"
    return (
        f"{APP_NAME} ya está en ejecución (PID {pid}). "
        "Cierra esa ventana antes de abrir otra."
    )


def claim_or_exit(stream=None) -> InstanceLock:
    """Toma el cerrojo o termina el proceso avisando de la instancia viva."""
    lock = claim()
    if not lock.acquired:
        print(
            already_running_message(lock.owner_pid),
            file=stream if stream is not None else sys.stderr,
        )
        sys.exit(EXIT_ALREADY_RUNNING)
    return lock
