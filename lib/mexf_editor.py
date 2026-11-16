"""Núcleo del editor ``.mexf``: verificación de sintaxis y compilación interactiva.

Separa la lógica del widget para poder probarla sin GUI. ``lint_source`` valida
texto YAML v1 (o JSON legacy) y devuelve diagnósticos con número de línea, de
modo que el editor resalte el error en el punto exacto. ``compile_source``
empaqueta el texto directamente a ``.asksome`` usando un proyecto temporal.
"""
from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:  # pragma: no cover - entorno sin PyYAML
    yaml = None

from lib.mexf_parser import MexfError, _legacy_to_v1, validate_mexf


@dataclass
class LintIssue:
    line: int
    column: int
    message: str
    severity: str = "error"

    def as_dict(self) -> Dict[str, Any]:
        return {"line": self.line, "column": self.column, "message": self.message, "severity": self.severity}


def _find_mark(text: str, problem: str) -> tuple[int, int]:
    """Localiza ``problem`` en ``text`` y devuelve ``(línea, columna)`` en base 1."""
    for index, line in enumerate(text.splitlines(), 1):
        column = line.find(problem)
        if column != -1:
            return index, column + 1
    return 1, 1


def _path_to_line(text: str, path: str) -> tuple[int, int]:
    """Traduce una ruta tipo ``metadata.id`` al número de línea/columna aproximado."""
    if not path:
        return 1, 1
    leaf = path.split("[")[0].split(".")[-1]
    if not leaf:
        return 1, 1
    for index, line in enumerate(text.splitlines(), 1):
        stripped = line.lstrip()
        if stripped.startswith(f"{leaf}:") or stripped.startswith(f"- {leaf}:"):
            column = line.find(leaf) + 1
            return index, column
    return 1, 1


def lint_source(text: str) -> List[LintIssue]:
    """Valida el texto ``.mexf`` y devuelve los problemas encontrados.

    Un texto válido devuelve una lista vacía. Los errores de sintaxis YAML
    apuntan a la línea/columna que reporta el analizador; los de contrato usan
    la ruta del diagnóstico para localizar la clave.
    """
    if yaml is None:
        return [LintIssue(1, 1, "PyYAML no está instalado; no se puede validar el YAML.")]

    try:
        raw = json.loads(text)
    except json.JSONDecodeError:
        raw = None

    if raw is not None and isinstance(raw, dict):
        data = _legacy_to_v1(raw) if "extensions" in raw or "shell_commands" in raw else raw
    else:
        try:
            loaded = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            mark = getattr(exc, "problem_mark", None)
            message = getattr(exc, "problem", None) or str(exc)
            if mark is not None:
                return [LintIssue(mark.line + 1, mark.column + 1, message)]
            return [LintIssue(1, 1, message)]
        if not isinstance(loaded, dict):
            return [LintIssue(1, 1, "El documento .mexf debe ser un objeto YAML.")]
        data = loaded

    issues = []
    for diagnostic in validate_mexf(data):
        line, column = _path_to_line(text, diagnostic.path)
        issues.append(LintIssue(line, column, diagnostic.message, diagnostic.severity))
    return issues


def is_valid_source(text: str) -> bool:
    return not [issue for issue in lint_source(text) if issue.severity == "error"]


def compile_source(
    text: str,
    output_file: Path | str,
    *,
    details: Optional[Dict[str, str]] = None,
) -> Path:
    """Empaqueta el texto del editor a ``.asksome`` sin necesidad de un proyecto.

    Construye un proyecto temporal con ``details.xml`` sintético (o el
    proporcionado) y delega en el compilador real, de modo que el editor
    interactivo use exactamente el mismo camino que el build.
    """
    from lib.mexf_compiler import compile_mexf_project

    issues = lint_source(text)
    errors = [issue for issue in issues if issue.severity == "error"]
    if errors:
        first = errors[0]
        raise MexfError(f"línea {first.line}: {first.message}")

    info = details or {"publisher": "Influent", "app": "mexf-editor", "name": "MEXF Editor", "version": "v1.0"}
    with tempfile.TemporaryDirectory(prefix="mexf-editor-") as tmp:
        root = Path(tmp)
        (root / ".mexf").mkdir(parents=True)
        (root / ".mexf" / "main.mexf").write_text(text, encoding="utf-8")
        (root / "details.xml").write_text(
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<app>\n"
            f"  <publisher>{info.get('publisher', 'Influent')}</publisher>\n"
            f"  <app>{info.get('app', 'mexf-editor')}</app>\n"
            f"  <name>{info.get('name', 'MEXF Editor')}</name>\n"
            f"  <version>{info.get('version', 'v1.0')}</version>\n"
            f"  <platform>{info.get('platform', 'AlphaCube')}</platform>\n"
            "</app>\n",
            encoding="utf-8",
        )
        return compile_mexf_project(root, output_file).output
