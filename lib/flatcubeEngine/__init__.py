# -*- coding: utf-8 -*-
"""flatcubeEngine — FlatCube v1, motor legacy de PackageMaker.

Stack histórico: Python 3.10, PyInstaller y PyQt4/PyQt5 (incompatible con
Leviathan UI / PyQt6). Produce un contenedor ``.flatkpkg`` (ZIP con sandbox
básico), pensado para entornos portables o viajes.

El motor sigue disponible para inspección, pero ya no se mantiene: el flujo
moderno usa ``blindcubeEngine``.

La lógica real del contenedor vive en ``container`` (ZIP autocontenido).
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from lib.engine_core import (
    ENGINE_ROLE_COMPILER,
    BuildEngine,
    EngineEnvironment,
    register_engine,
)
from lib.flatcubeEngine import container
from lib.flatcubeEngine.container import (
    FORMAT_EXTENSION,
    FlatCubeError,
    pack,
    pack_directory,
    read_manifest,
    unpack,
)

ENGINE_ID = "flatcube"
DISPLAY_NAME = "FlatCube v1"

ENGINE = register_engine(
    BuildEngine(
        id=ENGINE_ID,
        display_name=DISPLAY_NAME,
        role=ENGINE_ROLE_COMPILER,
        status="legacy",
        python_version="3.10",
        backend="pyinstaller",
        stack="Python 3.10, PyInstaller, PyQt4/PyQt5 (incompatible con Leviathan UI / PyQt6)",
        description="Sandbox básico. Ideal para entornos portables o viajes.",
        format_extension=FORMAT_EXTENSION,
        compression="zip",
        selectable=True,
        notes="Legacy / sin soporte",
    )
)


def environment(
    workdir: Path, requirements_path: Optional[Path] = None
) -> EngineEnvironment:
    """Entorno efímero del motor FlatCube v1."""
    return EngineEnvironment(ENGINE, Path(workdir), requirements_path=requirements_path)


__all__ = [
    "ENGINE_ID",
    "DISPLAY_NAME",
    "ENGINE",
    "FORMAT_EXTENSION",
    "FlatCubeError",
    "container",
    "pack",
    "unpack",
    "pack_directory",
    "read_manifest",
    "environment",
]
