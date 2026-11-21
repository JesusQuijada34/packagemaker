# -*- coding: utf-8 -*-
"""Acceso único a ``leviathan-ui`` con copia vendorizada (bugs.txt Fase 2.1).

``leviathan-ui`` se distribuye en PyPI, pero el proyecto necesita probarlo
localmente y, sobre todo, arrancar cuando el paquete no está instalado (CI,
Linux sin la dependencia). La copia de ``lib/leviathan_ui`` tiene prioridad y la
distribución instalada queda como respaldo.

Todo el código de PackageMaker debe resolver el framework por aquí en lugar de
importar ``leviathan_ui`` directamente.
"""
from __future__ import annotations

import importlib
import os
from types import ModuleType
from typing import Any, List, Optional

VENDORED = "lib.leviathan_ui"
INSTALLED = "leviathan_ui"
# Escape hatch para reproducir el escenario sin la copia local (empaquetado,
# CI que valida los respaldos no-op). No se usa en la ejecución normal.
DISABLE_VENDORED_ENV = "PACKAGEMAKER_NO_VENDORED_FRAMEWORK"


def framework(prefer_vendored: bool = True) -> Optional[ModuleType]:
    """Módulo del framework: copia local primero, distribución después.

    ``prefer_vendored=False`` resuelve sólo la distribución instalada; lo usan
    los artefactos que se copian a proyectos empaquetados (``updater.py``),
    donde la copia vendorizada del repositorio no viaja.
    """
    skip_vendored = not prefer_vendored or bool(os.environ.get(DISABLE_VENDORED_ENV))
    names = (INSTALLED,) if skip_vendored else (VENDORED, INSTALLED)
    for name in names:
        try:
            return importlib.import_module(name)
        except ImportError:
            continue
    return None


def is_available(prefer_vendored: bool = True) -> bool:
    return framework(prefer_vendored) is not None


def attribute(name: str) -> Any:
    """Atributo del framework (``WipeWindow``, ``CustomTitleBar``, ...)."""
    module = framework()
    if module is None:
        raise ImportError("leviathan-ui no está disponible")
    return getattr(module, name)


def submodule(name: str) -> ModuleType:
    """Submódulo del framework (``touchscreen``, ``progress_bar``, ...)."""
    module = framework()
    if module is None:
        raise ImportError("leviathan-ui no está disponible")
    return importlib.import_module(f"{module.__name__}.{name}")


def names(*requested: str) -> List[Any]:
    """Varios atributos de una vez, en el orden solicitado."""
    return [attribute(name) for name in requested]


__all__ = ["INSTALLED", "VENDORED", "attribute", "framework", "is_available", "names", "submodule"]
