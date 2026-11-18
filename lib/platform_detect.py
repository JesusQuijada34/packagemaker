# -*- coding: utf-8 -*-
"""Detección de plataforma autoritativa de PackageMaker.

La ley de nombres admite **tres** plataformas canónicas: ``Danenone`` (Linux),
``Knosthalij`` (Windows) y ``AlphaCube`` (multiplataforma). Antes cada módulo
adivinaba el sistema por su cuenta y aparecían tokens que la ley no reconoce
(``termux``, ``android``, ``keystone``, ``StoneCube``), lo que producía nombres
no canónicos y ``ValueError`` al validar.

Este módulo es la **única fuente** de verdad:

* ``detect_os()``   — sistema real (``windows``/``linux``/``android``/``termux``/``darwin``/``unknown``).
* ``canonical_platform()`` — traduce ese sistema a ``Danenone``/``Knosthalij``/``AlphaCube``.
* ``base_directories()``   — carpetas de proyectos y apps según el entorno.
* ``normalize_platform()`` — normaliza alias de UI a la plataforma canónica.

Android y Termux son entornos Linux, así que su plataforma canónica es
``Danenone``: el sufijo del nombre **pertenece al sistema de destino**, no al
runtime concreto donde corre PackageMaker.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

CANONICAL_PLATFORMS: Tuple[str, ...] = ("Danenone", "Knosthalij", "AlphaCube")

# Alias aceptados (minúsculas) -> plataforma canónica.
_PLATFORM_ALIASES: Dict[str, str] = {
    "win": "Knosthalij",
    "win32": "Knosthalij",
    "win64": "Knosthalij",
    "windows": "Knosthalij",
    "knosthalij": "Knosthalij",
    "linux": "Danenone",
    "linux2": "Danenone",
    "danenone": "Danenone",
    "android": "Danenone",
    "termux": "Danenone",
    "darwin": "Danenone",
    "macos": "Danenone",
    "mac": "Danenone",
    "all": "AlphaCube",
    "multi": "AlphaCube",
    "multiplataforma": "AlphaCube",
    "alphacube": "AlphaCube",
    "alpha": "AlphaCube",
}


@dataclass(frozen=True)
class PlatformInfo:
    """Resultado de la detección, inmutable y serializable."""

    os_name: str  # windows / linux / android / termux / darwin / unknown
    platform: str  # Danenone / Knosthalij / AlphaCube
    base_dir: str  # carpeta de proyectos
    apps_dir: str  # carpeta de apps ("Fluthin Apps")
    icon_path: str  # icono según el SO (.png en Linux, .ico en Windows)


def detect_os() -> str:
    """Devuelve el sistema real donde corre PackageMaker.

    Orden de prioridad: Termux y Android se comprueban primero porque ambos
    reportan ``sys.platform == "linux"`` y hay que distinguirlos para elegir la
    carpeta de trabajo accesible.
    """
    if os.environ.get("PREFIX", "").startswith("/data/data/com.termux"):
        return "termux"
    if sys.platform.startswith("linux") and (
        os.path.exists("/system/app")
        or os.environ.get("ANDROID_ROOT")
        or os.environ.get("ANDROID_DATA")
    ):
        return "android"
    if sys.platform.startswith("win"):
        return "windows"
    if sys.platform == "darwin":
        return "darwin"
    if sys.platform.startswith("linux"):
        return "linux"
    return "unknown"


def canonical_platform(os_name: Optional[str] = None) -> str:
    """Traduce un sistema a la plataforma canónica de la ley de nombres.

    ``windows`` → ``Knosthalij``; todo lo demás (Linux, Android, Termux, macOS,
    desconocido) → ``Danenone``.
    """
    name = (os_name or detect_os()).lower()
    return "Knosthalij" if name.startswith("win") else "Danenone"


def normalize_platform(platform_text: str) -> str:
    """Convierte una etiqueta de UI/alias a la plataforma canónica.

    Lanza ``ValueError`` si la etiqueta no es reconocible, para que un nombre no
    canónico nunca llegue a construirse en silencio.
    """
    value = str(platform_text or "").strip().lower()
    if value in _PLATFORM_ALIASES:
        return _PLATFORM_ALIASES[value]
    raise ValueError(
        "Plataforma no compatible. Use Danenone, Knosthalij o AlphaCube."
    )


def _windows_documents_dir() -> Path:
    profile = os.environ.get("USERPROFILE", "")
    for folder in ("Documentos", "Documents"):
        candidate = os.path.join(profile, folder)
        if os.path.exists(candidate):
            return Path(candidate)
    return Path(profile) / "Documents"


def base_directories(os_name: Optional[str] = None) -> Tuple[str, str]:
    """Devuelve ``(base_dir, apps_dir)`` para el sistema detectado.

    Cada entorno guarda en una carpeta accesible: Termux/Android dentro del
    home de la app (sin acceso a ``~/Documents``); Windows en Documentos
    (respetando la localización ``Documentos``/``Documents``); Linux/macOS en
    ``~/Documents``.
    """
    name = (os_name or detect_os()).lower()
    if name == "termux":
        home = Path(os.path.expanduser("~"))
        return (
            str(home / ".packagemaker" / "projects"),
            str(home / ".packagemaker" / "apps"),
        )
    if name == "android":
        home = Path(os.path.expanduser("~"))
        return (str(home / "PackageMaker" / "Projects"), str(home / "PackageMaker" / "Apps"))
    if name.startswith("win"):
        docs = _windows_documents_dir()
        return (
            str(docs / "Packagemaker Projects"),
            str(docs / "Fluthin Apps"),
        )
    if name in ("linux", "darwin"):
        docs = Path(os.path.expanduser("~/Documents"))
        return (str(docs / "Packagemaker Projects"), str(docs / "Fluthin Apps"))
    return ("Packagemaker Projects/", "Fluthin Apps/")


def _icon_path(os_name: str) -> str:
    if os_name.startswith("win"):
        return os.path.join("app", "app-icon.ico")
    ico = os.path.join("app", "app-icon.ico")
    png = os.path.join("app", "app-icon.png")
    return png if os.path.exists(png) else ico


def detect_platform_info() -> PlatformInfo:
    """Reúne la detección completa en un único objeto."""
    os_name = detect_os()
    base_dir, apps_dir = base_directories(os_name)
    return PlatformInfo(
        os_name=os_name,
        platform=canonical_platform(os_name),
        base_dir=base_dir,
        apps_dir=apps_dir,
        icon_path=_icon_path(os_name),
    )


__all__ = [
    "CANONICAL_PLATFORMS",
    "PlatformInfo",
    "detect_os",
    "canonical_platform",
    "normalize_platform",
    "base_directories",
    "detect_platform_info",
]
