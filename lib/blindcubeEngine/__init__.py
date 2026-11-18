# -*- coding: utf-8 -*-
"""blindcubeEngine — BlindCube v2, motor estándar de PackageMaker.

Stack actual: Python 3.14, Nuitka y Leviathan UI / PyQt6+, compatible con
``.MEXF``. Produce un contenedor ``.blindkpkg`` (LZMA con *magic bytes* y
cabecera JSON), pensado para apps de escritorio, tiendas y servidores.

Es el motor por defecto y el recomendado para compilaciones modernas.
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
        format_extension=".blindkpkg",
        compression="lzma",
        magic=b"BLINDCUB",
        selectable=True,
    )
)


def pack(payload: bytes, *, meta: Optional[Dict] = None) -> bytes:
    """Empaqueta un payload en el contenedor ``.blindkpkg`` (LZMA + cabecera)."""
    return ENGINE.pack(payload, meta=meta)


def unpack(container: bytes) -> tuple[Dict, bytes]:
    """Lee el contenedor ``.blindkpkg`` y devuelve ``(meta, payload)``."""
    import lzma

    meta, offset = ENGINE.read_header(container)
    compressed = container[offset:]
    payload = lzma.decompress(compressed, format=lzma.FORMAT_ALONE)
    return meta, payload


def environment(
    workdir: Path, requirements_path: Optional[Path] = None
) -> EngineEnvironment:
    """Entorno efímero del motor BlindCube v2."""
    return EngineEnvironment(ENGINE, Path(workdir), requirements_path=requirements_path)
