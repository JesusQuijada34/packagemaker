# -*- coding: utf-8 -*-
"""Aislamiento de los motores de compilación (bugs.txt Fase 1.2).

Cada motor declara su backend y de dónde salen las dependencias que debe
instalar dentro de su entorno virtual:

* **BlindCube v2** compila con Nuitka y toma como base ``lib/requirements.txt``.
* **FlatCube v1** compila con PyInstaller e instala explícitamente los
  requerimientos dentro del entorno virtual del proyecto.

El módulo sólo describe y prepara el entorno; no lanza compilaciones. Así se
puede inspeccionar el plan en la CLI headless y en los tests sin efectos.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from lib import engines
from lib.engine_core import BuildEngine, EngineError, load_requirements

# Backend exigido por cada motor: no se permite que BlindCube caiga a
# PyInstaller ni que FlatCube use Nuitka, porque cada uno produce un contenedor
# distinto (``.blindkpkg`` vs ``.flatkpkg``).
ENGINE_BACKENDS = {
    engines.BLINDCUBE_ID: "nuitka",
    engines.FLATCUBE_ID: "pyinstaller",
}

_PROJECT_REQUIREMENTS = ("requirements.txt", "lib/requirements.txt")


@dataclass(frozen=True)
class EnginePlan:
    """Plan de aislamiento de un motor, inspeccionable sin ejecutar nada."""

    engine_id: str
    backend: str
    python_version: str
    venv_dir: Path
    packages: List[str]

    def as_dict(self) -> Dict[str, object]:
        return {
            "engine": self.engine_id,
            "backend": self.backend,
            "python": self.python_version,
            "venv": str(self.venv_dir),
            "packages": list(self.packages),
        }


def project_requirements(project_path: Path) -> Path:
    """Devuelve el ``requirements.txt`` del proyecto, o el de ``lib/`` si falta."""
    root = Path(project_path)
    for relative in _PROJECT_REQUIREMENTS:
        candidate = root / relative
        if candidate.is_file():
            return candidate
    return Path(__file__).resolve().parent / "requirements.txt"


def resolve_backend_for(engine: BuildEngine) -> str:
    """Backend que el motor debe usar, sin permitir la caída silenciosa."""
    return ENGINE_BACKENDS.get(engine.id) or engine.backend or "nuitka"


def plan_engine(
    engine_id: str,
    workdir: Path,
    project_path: Optional[Path] = None,
) -> EnginePlan:
    """Construye el plan de aislamiento del motor solicitado.

    BlindCube toma ``lib/requirements.txt``; FlatCube prefiere el
    ``requirements.txt`` del propio proyecto para instalar sus dependencias en
    el entorno virtual del proyecto.
    """
    engine = engines.get_engine(engine_id)
    if engine_id == engines.FLATCUBE_ID and project_path is not None:
        requirements_path = project_requirements(project_path)
    else:
        requirements_path = Path(__file__).resolve().parent / "requirements.txt"

    return EnginePlan(
        engine_id=engine.id,
        backend=resolve_backend_for(engine),
        python_version=engine.python_version,
        venv_dir=Path(workdir) / f"venv-{engine.id}",
        packages=load_requirements(requirements_path),
    )


def engine_environment(
    engine_id: str,
    workdir: Path,
    project_path: Optional[Path] = None,
):
    """Entorno ``EngineEnvironment`` del motor con sus dependencias resueltas."""
    packages = plan_engine(engine_id, workdir, project_path)
    if engine_id == engines.BLINDCUBE_ID:
        from lib import blindcubeEngine as package
    elif engine_id == engines.FLATCUBE_ID:
        from lib import flatcubeEngine as package
    elif engine_id == engines.MAKESELF_ID:
        from lib import makeselfEngine as package
    else:
        raise EngineError(f"Motor desconocido: {engine_id}")

    env = package.environment(Path(workdir))
    env.requirements = list(packages.packages)
    return env


__all__ = [
    "ENGINE_BACKENDS",
    "EnginePlan",
    "engine_environment",
    "plan_engine",
    "project_requirements",
    "resolve_backend_for",
]
