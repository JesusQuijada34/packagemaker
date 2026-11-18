# -*- coding: utf-8 -*-
"""flatcubeEngine — FlatCube v1, motor legacy de PackageMaker.

Stack histórico: Python 3.10, PyInstaller y PyQt4/PyQt5 (incompatible con
Leviathan UI / PyQt6). Produce un contenedor ``.flatkpkg`` (ZIP con sandbox
básico), pensado para entornos portables o viajes.

El motor sigue disponible para inspección, pero ya no se mantiene: el flujo
moderno usa ``blindcubeEngine``.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from lib.engine_core import (
    ENGINE_ROLE_COMPILER,
    BuildEngine,
    EngineEnvironment,
    register_engine,
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
        format_extension=".flatkpkg",
        compression="zip",
        selectable=True,
        notes="Legacy / sin soporte",
    )
)


def pack(payload: bytes, *, meta: Optional[Dict] = None) -> bytes:
    """Empaqueta un payload ZIP en el contenedor ``.flatkpkg``."""
    return ENGINE.pack(payload, meta=meta)


def environment(
    workdir: Path, requirements_path: Optional[Path] = None
) -> EngineEnvironment:
    """Entorno efímero del motor FlatCube v1."""
    return EngineEnvironment(ENGINE, Path(workdir), requirements_path=requirements_path)
