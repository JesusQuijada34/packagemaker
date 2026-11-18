# -*- coding: utf-8 -*-
"""blindcubeEngine — BlindCube v2, motor estándar de PackageMaker.

Stack actual: Python 3.14, Nuitka y Leviathan UI / PyQt6+, compatible con
``.MEXF``. Produce un contenedor ``.blindkpkg`` (LZMA con *magic bytes* y
cabecera JSON), pensado para apps de escritorio, tiendas y servidores.

Es el motor por defecto y el recomendado para compilaciones modernas. La lógica
real del contenedor (compresión, cabecera y cifrado de extremo a extremo) vive
en ``container``.
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
from lib.blindcubeEngine import container
from lib.blindcubeEngine.container import (
    FORMAT_EXTENSION,
    MAGIC,
    BlindCubeError,
    pack,
    pack_directory,
    read_header,
    unpack,
)

ENGINE_ID = "blindcube"
DISPLAY_NAME = "BlindCube v2"

ENGINE = register_engine(
    BuildEngine(
        id=ENGINE_ID,
        display_name=DISPLAY_NAME,
        role=ENGINE_ROLE_COMPILER,
        status="standard",
        python_version="3.14",
        backend="nuitka",
        stack="Python 3.14, Nuitka, Leviathan UI / PyQt6+, compatible con .MEXF",
        description="Sandbox multi-OS con cifrado de extremo a extremo. "
        "Ideal para apps de escritorio, tiendas y servidores.",
        format_extension=FORMAT_EXTENSION,
        compression="lzma",
        magic=MAGIC,
        selectable=True,
    )
)


def environment(
    workdir: Path, requirements_path: Optional[Path] = None
) -> EngineEnvironment:
    """Entorno efímero del motor BlindCube v2."""
    return EngineEnvironment(ENGINE, Path(workdir), requirements_path=requirements_path)


__all__ = [
    "ENGINE_ID",
    "DISPLAY_NAME",
    "ENGINE",
    "FORMAT_EXTENSION",
    "MAGIC",
    "BlindCubeError",
    "container",
    "pack",
    "unpack",
    "pack_directory",
    "read_header",
    "environment",
]
