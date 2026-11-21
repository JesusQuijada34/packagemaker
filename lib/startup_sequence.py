# -*- coding: utf-8 -*-
"""Coreografía de arranque de PackageMaker (bugs.txt Fase 2.2).

El orden es estricto y cada paso puede cortar el arranque con un código:

1. **Splash** — se pinta de inmediato, antes de la UI pesada.
2. **Landing de GitHub** — si hace falta login, código ``1``.
3. **Verificación de errores internos** — si hay errores, código ``1`` abre la
   ventana de reporte; si no, código ``0`` continúa.
4. **Ventana principal**.

Este módulo no importa Qt: la GUI consume las decisiones y sólo se encarga de
pintarlas.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional

CODE_OK = 0
CODE_LOGIN_REQUIRED = 1
CODE_INTERNAL_ERROR = 1


@dataclass(frozen=True)
class StartStep:
    """Un paso de la coreografía con su código de salida."""

    name: str
    code: int = CODE_OK
    detail: str = ""

    @property
    def blocks_startup(self) -> bool:
        """``True`` si el paso detiene el arranque (login o error interno)."""
        return self.code != CODE_OK


@dataclass(frozen=True)
class StartupPlan:
    """Decisión completa del arranque, calculada antes de pintar nada."""

    steps: List[StartStep]

    @property
    def landing_required(self) -> bool:
        return any(step.name == "landing" and step.blocks_startup for step in self.steps)

    @property
    def internal_errors(self) -> List[str]:
        return [step.detail for step in self.steps if step.name == "internal" and step.blocks_startup]

    @property
    def exit_code(self) -> int:
        """Primer código distinto de cero, o ``0`` si todo está en orden."""
        for step in self.steps:
            if step.code != CODE_OK:
                return step.code
        return CODE_OK

    @property
    def main_window_visible(self) -> bool:
        """La ventana principal sólo se revela si ningún paso la bloquea."""
        return self.exit_code == CODE_OK

    def step(self, name: str) -> Optional[StartStep]:
        for step in self.steps:
            if step.name == name:
                return step
        return None


def plan_startup(
    has_session: bool,
    internal_errors: Optional[List[str]] = None,
    *,
    login_required: Optional[bool] = None,
) -> StartupPlan:
    """Calcula la coreografía: splash → landing → errores → ventana principal.

    ``has_session`` indica si hay credenciales usables; ``internal_errors`` son
    los fallos detectados antes de pintar la UI (p. ej. ``details.xml`` roto).
    """
    needs_login = (not has_session) if login_required is None else bool(login_required)
    errors = [str(error) for error in (internal_errors or []) if str(error).strip()]

    steps = [StartStep(name="splash")]
    if needs_login:
        steps.append(StartStep(name="landing", code=CODE_LOGIN_REQUIRED, detail="login_required"))
    if errors:
        steps.append(StartStep(name="internal", code=CODE_INTERNAL_ERROR, detail="\n".join(errors)))
    steps.append(StartStep(name="main"))
    return StartupPlan(steps=steps)


def collect_internal_errors(base_dir: Optional[str] = None, fluthin_dir: Optional[str] = None) -> List[str]:
    """Reúne los fallos que impiden arrancar con garantías.

    Se ejecuta antes de pintar la ventana principal: si devuelve algo, el
    arranque se corta con código ``1`` y el splash se transforma en la ventana
    de reporte. Nunca lanza: cada comprobación se traduce a un mensaje.
    """
    errors: List[str] = []

    try:
        from lib.makeselfEngine.templates import templates_available

        if not templates_available():
            errors.append("No se encontraron las plantillas de proyecto (source/templates).")
    except Exception as exc:  # pragma: no cover - depende del bundle
        errors.append(f"No se pudieron cargar las plantillas: {exc}")

    for label, path in (("BASE_DIR", base_dir), ("Fluthin_APPS", fluthin_dir)):
        if not path:
            continue
        try:
            os.makedirs(path, exist_ok=True)
            probe = os.path.join(path, ".pm_write_probe")
            with open(probe, "w", encoding="utf-8") as handle:
                handle.write("ok")
            os.remove(probe)
        except OSError as exc:
            errors.append(f"{label} no es escribible ({path}): {exc}")

    return errors
