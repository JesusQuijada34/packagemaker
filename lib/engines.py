# -*- coding: utf-8 -*-
"""Fachada de motores de PackageMaker (Fase 1 de bugs.txt).

Importa los tres paquetes de motor para que se registren y expone una API
única al resto de la aplicación (GUI, CLI headless y tests). Importar este
módulo es la forma canónica de poblar el registro.
"""
from __future__ import annotations

from typing import Dict, List

from lib import blindcubeEngine, flatcubeEngine, makeselfEngine  # noqa: F401
from lib.engine_core import (
    ENGINE_ROLE_COMPILER,
    ENGINE_ROLE_GENERATOR,
    BuildEngine,
    EngineEnvironment,
    EngineError,
    available_engines,
    get_engine,
    register_engine,
    resolve_engine,
    selectable_engines,
)

# Nombres canónicos de los dos motores de compilación que el usuario elige de
# forma explícita antes de compilar.
FLATCUBE_ID = flatcubeEngine.ENGINE_ID
BLINDCUBE_ID = blindcubeEngine.ENGINE_ID
MAKESELF_ID = makeselfEngine.ENGINE_ID


def compiler_engines() -> List[BuildEngine]:
    """Motores de compilación seleccionables (FlatCube v1 / BlindCube v2)."""
    return [e for e in selectable_engines() if e.role == ENGINE_ROLE_COMPILER]


def describe_engines() -> List[Dict[str, str]]:
    """Descripción plana para la CLI headless y la GUI."""
    rows = []
    for engine in available_engines().values():
        rows.append(
            {
                "id": engine.id,
                "name": engine.display_name,
                "role": engine.role,
                "status": engine.status,
                "python": engine.python_version,
                "backend": engine.backend or "—",
                "format": engine.format_extension or "—",
                "notes": engine.notes or engine.description,
            }
        )
    return rows


__all__ = [
    "BuildEngine",
    "EngineEnvironment",
    "EngineError",
    "available_engines",
    "get_engine",
    "register_engine",
    "resolve_engine",
    "selectable_engines",
    "compiler_engines",
    "describe_engines",
    "FLATCUBE_ID",
    "BLINDCUBE_ID",
    "MAKESELF_ID",
    "ENGINE_ROLE_COMPILER",
    "ENGINE_ROLE_GENERATOR",
]
