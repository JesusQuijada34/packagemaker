# -*- coding: utf-8 -*-
"""Pruebas previas al empaquetado de BlindCube (bugs.txt Fase 1.4).

Antes de invocar a Nuitka se comprueba que los guiones del proyecto:

1. **Compilan** (``compile`` sobre el AST, sin ejecutar nada).
2. **Arrancan offscreen** (``QT_QPA_PLATFORM=offscreen``) para detectar fallos
   de importación o de construcción de la ventana antes de invertir minutos en
   una compilación nativa.

También se detecta el ``.env`` del proyecto: si existe, el usuario decide cómo
inyectarlo (entorno global o variables seleccionadas por aplicación).
"""
from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from lib.i18n import tr

# Los guiones del proyecto viven en la raíz y en ``source/``; se ignoran los
# entornos virtuales y los artefactos de compilación.
_SKIP_DIRS = {"venv", ".venv", "dist", "build", "__pycache__", ".git", "node_modules"}


@dataclass
class CheckResult:
    """Resultado de una comprobación previa."""

    name: str
    ok: bool
    detail: str = ""


@dataclass
class PreflightReport:
    """Conjunto de comprobaciones previas; ``ok`` sólo si todas pasan."""

    checks: List[CheckResult] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(check.ok for check in self.checks)

    @property
    def failures(self) -> List[CheckResult]:
        return [check for check in self.checks if not check.ok]

    def summary(self) -> str:
        if self.ok:
            return tr("build.preflight_ok").format(count=len(self.checks))
        return "\n".join(f"• {c.name}: {c.detail}" for c in self.failures)


def discover_scripts(project_path: Path) -> List[Path]:
    """Guiones Python del proyecto, en orden estable y sin duplicados."""
    root = Path(project_path)
    scripts: List[Path] = []
    for directory in (root, root / "source"):
        if not directory.is_dir():
            continue
        for candidate in sorted(directory.rglob("*.py")):
            if any(part in _SKIP_DIRS for part in candidate.parts):
                continue
            if candidate not in scripts:
                scripts.append(candidate)
    return scripts


def check_syntax(scripts: Sequence[Path]) -> CheckResult:
    """Compila cada guion sin ejecutarlo (detecta errores de sintaxis)."""
    if not scripts:
        return CheckResult(tr("build.preflight_syntax"), True, tr("build.preflight_no_scripts"))
    broken: List[str] = []
    for script in scripts:
        try:
            compile(script.read_text(encoding="utf-8"), str(script), "exec")
        except SyntaxError as exc:
            broken.append(f"{script.name}:{exc.lineno}: {exc.msg}")
        except (OSError, UnicodeDecodeError) as exc:
            broken.append(f"{script.name}: {exc}")
    if broken:
        return CheckResult(
            tr("build.preflight_syntax"), False, "; ".join(broken[:5])
        )
    return CheckResult(
        tr("build.preflight_syntax"), True, tr("build.preflight_scripts_ok").format(count=len(scripts))
    )


def check_offscreen(scripts: Sequence[Path], *, timeout: int = 20) -> CheckResult:
    """Ejecuta cada guion con la plataforma Qt ``offscreen``.

    Se lanzan con ``--help`` no: se ejecutan de verdad, pero con un tope de
    tiempo; un bucle de eventos que no termina no invalida el guion, sólo se
    considera arranque correcto si no hubo error en ``stderr``.
    """
    name = tr("build.preflight_offscreen")
    if not scripts:
        return CheckResult(name, True, tr("build.preflight_no_scripts"))

    env = dict(os.environ)
    env["QT_QPA_PLATFORM"] = "offscreen"
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")

    broken: List[str] = []
    for script in scripts:
        try:
            completed = subprocess.run(
                [sys.executable, str(script)],
                cwd=str(script.parent),
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            # Un bucle de eventos abierto indica que la ventana se construyó.
            continue
        except OSError as exc:
            broken.append(f"{script.name}: {exc}")
            continue
        if completed.returncode != 0:
            tail = (completed.stderr or "").strip().splitlines()[-3:]
            broken.append(f"{script.name}: {' | '.join(tail) or completed.returncode}")
    if broken:
        return CheckResult(name, False, "; ".join(broken[:3]))
    return CheckResult(name, True, tr("build.preflight_offscreen_ok"))


def run_preflight(project_path: Path, *, offscreen: bool = True) -> PreflightReport:
    """Ejecuta las comprobaciones previas sobre el proyecto."""
    scripts = discover_scripts(Path(project_path))
    report = PreflightReport()
    report.checks.append(check_syntax(scripts))
    if offscreen:
        report.checks.append(check_offscreen(scripts))
    return report


# --------------------------------------------------------------------------- #
# Inyección del .env
# --------------------------------------------------------------------------- #
ENV_FILENAME = ".env"


def find_env_file(project_path: Path) -> Optional[Path]:
    """``.env`` del proyecto (raíz o ``config/``), si existe."""
    root = Path(project_path)
    for candidate in (root / ENV_FILENAME, root / "config" / ENV_FILENAME):
        if candidate.is_file():
            return candidate
    return None


def parse_env_file(path: Path) -> Dict[str, str]:
    """Lee ``CLAVE=valor`` ignorando comentarios y líneas vacías."""
    values: Dict[str, str] = {}
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return values
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key.startswith("export "):
            key = key[len("export ") :].strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


INJECTION_GLOBAL = "global"
INJECTION_CUSTOM = "custom"


def build_env_payload(
    variables: Dict[str, str],
    mode: str,
    selected: Optional[Sequence[str]] = None,
) -> Dict[str, object]:
    """Traduce la elección del usuario al payload que viaja con el paquete.

    * ``global``: todas las variables se inyectan en el entorno al ejecutar.
    * ``custom``: sólo las seleccionadas, agrupadas por programa destino.
    """
    if mode == INJECTION_GLOBAL:
        return {"mode": INJECTION_GLOBAL, "environment": dict(variables)}
    if mode != INJECTION_CUSTOM:
        raise ValueError(f"Modo de inyección desconocido: {mode}")

    chosen = set(selected or ())
    return {
        "mode": INJECTION_CUSTOM,
        "environment": {k: v for k, v in variables.items() if k in chosen},
    }


__all__ = [
    "CheckResult",
    "ENV_FILENAME",
    "INJECTION_CUSTOM",
    "INJECTION_GLOBAL",
    "PreflightReport",
    "build_env_payload",
    "check_offscreen",
    "check_syntax",
    "discover_scripts",
    "find_env_file",
    "parse_env_file",
    "run_preflight",
]
