# -*- coding: utf-8 -*-
"""makeselfEngine — motor de generación de proyectos (Fase 1 de bugs.txt).

Se encarga de la creación inicial: plantillas base, estructura de carpetas y
validación del formato canónico. No compila binarios; prepara el proyecto que
luego consumen los motores de compilación.

La lógica real vive aquí:

* ``naming``    — la ley de nombres canónicos (autoridad de ``ProjectNameFormatter``).
* ``templates`` — creación y reparación de proyectos desde ``src/templates``.

``lib/projectNameFormatter`` y ``lib/template_engine`` son fachadas de
compatibilidad que reexportan estos módulos.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from lib.engine_core import (
    ENGINE_ROLE_GENERATOR,
    BuildEngine,
    EngineEnvironment,
    register_engine,
)
from lib.makeselfEngine import naming, templates
from lib.makeselfEngine.naming import ProjectNameFormatter
from lib.makeselfEngine.templates import (
    build_variables,
    create_project_from_templates,
    normalize_platform,
    repair_project_from_templates,
    templates_available,
)

ENGINE_ID = "makeself"
DISPLAY_NAME = "MakeSelf"

ENGINE = register_engine(
    BuildEngine(
        id=ENGINE_ID,
        display_name=DISPLAY_NAME,
        role=ENGINE_ROLE_GENERATOR,
        status="standard",
        python_version="3.14",
        backend=None,
        stack="Plantillas base, estructura de carpetas y validación de formato canónico",
        description="Creación inicial de proyectos de Package Maker.",
        selectable=False,
    )
)


def create_project(project_path: Path, **kwargs) -> Dict[str, Any]:
    """Crea un proyecto completo a partir de las plantillas canónicas."""
    return create_project_from_templates(Path(project_path), **kwargs)


def repair_project(project_path: Path, **kwargs) -> Dict[str, Any]:
    """Repara un proyecto existente (Moon Fix) desde las plantillas."""
    return repair_project_from_templates(Path(project_path), **kwargs)


def validate_canonical_name(name: str) -> bool:
    """Comprueba que un nombre de carpeta cumple la ley de nombres canónicos."""
    return ProjectNameFormatter.parse_project_folder(name) is not None


def environment(
    workdir: Path, requirements_path: Optional[Path] = None
) -> EngineEnvironment:
    """Entorno efímero del motor de generación."""
    return EngineEnvironment(ENGINE, Path(workdir), requirements_path=requirements_path)


__all__ = [
    "ENGINE_ID",
    "DISPLAY_NAME",
    "ENGINE",
    "ProjectNameFormatter",
    "build_variables",
    "create_project",
    "create_project_from_templates",
    "repair_project",
    "repair_project_from_templates",
    "templates_available",
    "normalize_platform",
    "validate_canonical_name",
    "environment",
    "naming",
    "templates",
]
