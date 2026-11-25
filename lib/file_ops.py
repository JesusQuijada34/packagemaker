# -*- coding: utf-8 -*-
"""Operaciones de ficheros robustas frente a bloqueos del sistema operativo.

En Windows los procesos hijos (Nuitka, PyInstaller) mantienen descriptores
abiertos sobre los binarios recién creados. El hilo de compilación intentaba
mover o borrar esos directorios inmediatamente y recibía ``WinError 32``
("El proceso no tiene acceso al archivo porque está siendo utilizado por otro
proceso"). Aquí se reintenta con una espera creciente hasta que el bloqueo
desaparece, en lugar de fallar o silenciar el error con ``ignore_errors``.
"""
from __future__ import annotations

import errno
import os
import shutil
import stat
import sys
import time
from pathlib import Path
from typing import Optional, Union

PathLike = Union[str, os.PathLike]

# Códigos que indican un fichero en uso (Windows ``WinError 32``/33 y los
# equivalentes POSIX ``EBUSY``/``ETXTBSY``). Sólo estos se reintentan: un
# ``ENOENT`` o un permiso denegado real no mejora esperando.
_BUSY_ERRNOS = {errno.EBUSY, errno.ETXTBSY, errno.EACCES, errno.EPERM}
_BUSY_WINERRORS = {5, 32, 33}


def path_exists(path: PathLike) -> bool:
    """``True`` si *path* existe; un error de permiso cuenta como "no existe".

    Desde Python 3.13 ``Path.exists()`` propaga ``PermissionError`` cuando el
    directorio padre no es accesible, así que las comprobaciones de rutas que
    vienen del usuario (CLI, carpetas de proyectos) necesitan este envoltorio
    para no terminar en un traceback.
    """
    try:
        return Path(path).exists()
    except OSError:
        return False


def path_is_file(path: PathLike) -> bool:
    """``Path.is_file()`` sin lanzar ante un error de permiso."""
    try:
        return Path(path).is_file()
    except OSError:
        return False


def path_is_dir(path: PathLike) -> bool:
    """``Path.is_dir()`` sin lanzar ante un error de permiso."""
    try:
        return Path(path).is_dir()
    except OSError:
        return False


def list_directory(path: PathLike) -> list[Path]:
    """Hijos ordenados de *path*; ``[]`` si no es un directorio legible."""
    try:
        return sorted(Path(path).iterdir())
    except OSError:
        return []


def is_file_lock_error(exc: BaseException) -> bool:
    """¿El error se debe a que otro proceso mantiene el fichero abierto?"""
    if not isinstance(exc, OSError):
        return False
    if getattr(exc, "winerror", None) in _BUSY_WINERRORS:
        return True
    return exc.errno in _BUSY_ERRNOS


def _retry(func, *args, attempts: int = 8, delay: float = 0.15, **kwargs):
    """Ejecuta ``func`` reintentando sólo ante bloqueos de fichero."""
    last_error: Optional[BaseException] = None
    wait = delay
    for attempt in range(attempts):
        try:
            return func(*args, **kwargs)
        except OSError as exc:
            if not is_file_lock_error(exc):
                raise
            last_error = exc
            if attempt == attempts - 1:
                break
            time.sleep(wait)
            wait = min(wait * 1.6, 1.0)
    raise last_error  # type: ignore[misc]


def _clear_readonly(func, path, _exc_info) -> None:
    """``onexc``/``onerror`` de ``rmtree``: quita el bit de sólo lectura y reintenta.

    En Windows los binarios copiados pueden quedar marcados como sólo lectura;
    sin este paso ``rmtree`` falla con ``PermissionError``. Si el reintento
    vuelve a fallar, el error se propaga: ``rmtree`` lo interpreta como un
    fallo real y ``_retry`` puede esperar a que se libere el fichero. Tragarse
    ese error hacía que ``remove_tree`` informara de un borrado que no ocurrió.
    """
    mode = os.stat(path).st_mode
    os.chmod(path, mode | stat.S_IWRITE)
    func(path)


def _tree_exists(path: Path) -> Optional[bool]:
    """``True``/``False``, o ``None`` si el sistema no deja comprobarlo."""
    try:
        os.lstat(path)
    except FileNotFoundError:
        return False
    except OSError:
        return None
    return True


def remove_tree(path: PathLike, *, attempts: int = 8, delay: float = 0.15) -> bool:
    """Borra un árbol de directorios esperando a que se liberen los ficheros.

    Devuelve ``True`` si el árbol ya no existe al terminar. No lanza: el
    llamador decide qué hacer con un directorio temporal que no se pudo borrar.
    """
    target = Path(path)
    exists = _tree_exists(target)
    if exists is None:
        return False
    if not exists:
        return True

    def _rm() -> None:
        # ``onexc`` existe desde Python 3.12; en versiones anteriores el
        # equivalente se llama ``onerror``.
        if sys.version_info >= (3, 12):
            shutil.rmtree(target, onexc=_clear_readonly)
        else:  # pragma: no cover - entorno antiguo
            shutil.rmtree(target, onerror=_clear_readonly)

    try:
        _retry(_rm, attempts=attempts, delay=delay)
    except OSError:
        return _tree_exists(target) is False
    # ``shutil.rmtree`` no lanza si el ``onexc`` consumió el fallo, así que el
    # éxito sólo se confirma comprobando que el árbol ya no está.
    return _tree_exists(target) is False


def copy_file(source: PathLike, destination: PathLike) -> Path:
    """Copia preservando metadatos y reintentando si el destino está bloqueado."""
    src, dst = Path(source), Path(destination)
    dst.parent.mkdir(parents=True, exist_ok=True)
    _retry(shutil.copy2, src, dst)
    return dst


def _copytree(source: Path, destination: Path, ignore, dirs_exist_ok: bool) -> None:
    """``shutil.copytree`` que convierte un bloqueo agrupado en reintentable.

    ``copytree`` acumula los fallos por entrada y lanza ``shutil.Error`` (que no
    lleva ``errno``); si alguno de esos fallos es un fichero en uso hay que
    volver a intentarlo en vez de rendirse en la primera pasada.
    """
    try:
        shutil.copytree(
            source, destination, ignore=ignore, dirs_exist_ok=dirs_exist_ok
        )
    except shutil.Error as exc:
        for _src, _dst, why in exc.args[0]:
            if is_file_lock_error(why):
                raise why
        raise


def copy_tree(
    source: PathLike,
    destination: PathLike,
    *,
    ignore=None,
    dirs_exist_ok: bool = True,
    attempts: int = 8,
    delay: float = 0.15,
) -> Path:
    """Copia un árbol reintentando mientras el destino siga bloqueado.

    ``dirs_exist_ok`` por defecto permite refrescar una carpeta que ya existe
    (el paquete de una compilación anterior) sin borrarla antes.
    """
    src, dst = Path(source), Path(destination)
    dst.parent.mkdir(parents=True, exist_ok=True)
    _retry(
        _copytree,
        src,
        dst,
        ignore,
        dirs_exist_ok,
        attempts=attempts,
        delay=delay,
    )
    return dst


def move_path(source: PathLike, destination: PathLike) -> Path:
    """Mueve (renombra o copia+borra) tolerando bloqueos transitorios."""
    src, dst = Path(source), Path(destination)
    dst.parent.mkdir(parents=True, exist_ok=True)

    def _move() -> None:
        try:
            os.replace(src, dst)
        except OSError as exc:
            if exc.errno == errno.EXDEV:
                shutil.move(str(src), str(dst))
            else:
                raise

    _retry(_move)
    return dst


def replace_file(source: PathLike, destination: PathLike) -> Path:
    """Sustituye ``destination`` por ``source`` de forma atómica y tolerante."""
    src, dst = Path(source), Path(destination)
    _retry(os.replace, src, dst)
    return dst


__all__ = [
    "copy_file",
    "copy_tree",
    "is_file_lock_error",
    "list_directory",
    "move_path",
    "path_exists",
    "path_is_dir",
    "path_is_file",
    "remove_tree",
    "replace_file",
]
