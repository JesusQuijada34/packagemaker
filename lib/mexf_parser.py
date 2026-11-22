"""Parser seguro y versionado para extensiones ``.mexf``.

El formato YAML v1 es declarativo: los comandos se representan como argv y no
se ejecutan durante el parseo. Los documentos JSON históricos se detectan y se
pueden migrar explícitamente, sin cambiar su significado silenciosamente.
"""
from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Literal

try:
    import yaml
except ImportError:  # pragma: no cover - mensaje de entorno
    yaml = None


class MexfError(ValueError):
    """Error de sintaxis o contrato de un documento .mexf."""


@dataclass(frozen=True)
class Diagnostic:
    message: str
    path: str = ""
    severity: str = "error"


@dataclass(frozen=True)
class MexfDocument:
    data: Dict[str, Any]
    source_format: Literal["yaml-v1", "legacy-json"]
    source_path: str = ""

    @property
    def metadata(self) -> Dict[str, Any]:
        return self.data.get("metadata", {})


def detect_mexf_format(path: Path | str) -> Literal["yaml-v1", "legacy-json", "unknown"]:
    try:
        raw = Path(path).read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        return "unknown"
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        if yaml is None:
            return "unknown"
        try:
            value = yaml.safe_load(raw)
        except Exception:
            return "unknown"
    if isinstance(value, dict) and value.get("format") == "mexf" and value.get("version") == 1:
        return "yaml-v1"
    if isinstance(value, dict) and any(k in value for k in ("extensions", "file_associations", "context_menus")):
        return "legacy-json"
    return "unknown"


def _require_mapping(value: Any, name: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise MexfError(f"{name} debe ser un objeto YAML.")
    return value


def validate_mexf(data: Dict[str, Any], *, project_root: Path | None = None) -> List[Diagnostic]:
    diagnostics: List[Diagnostic] = []
    if data.get("format") != "mexf":
        diagnostics.append(Diagnostic("format debe ser 'mexf'.", "format"))
    if data.get("version") != 1:
        diagnostics.append(Diagnostic("version debe ser 1.", "version"))
    try:
        metadata = _require_mapping(data.get("metadata"), "metadata")
        for key in ("id", "name", "version"):
            if not isinstance(metadata.get(key), str) or not metadata[key].strip():
                diagnostics.append(Diagnostic(f"metadata.{key} es obligatorio.", f"metadata.{key}"))
    except MexfError as exc:
        diagnostics.append(Diagnostic(str(exc), "metadata"))
    ids = set()
    for section in ("triggers", "commands"):
        values = data.get(section, [])
        if not isinstance(values, list):
            diagnostics.append(Diagnostic(f"{section} debe ser una lista.", section))
            continue
        for index, item in enumerate(values):
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                diagnostics.append(Diagnostic("cada entrada necesita un id.", f"{section}[{index}]"))
                continue
            if item["id"] in ids:
                diagnostics.append(Diagnostic(f"id duplicado: {item['id']}", f"{section}[{index}].id"))
            ids.add(item["id"])
            if section == "commands" and not isinstance(item.get("executable"), str):
                diagnostics.append(Diagnostic("command.executable es obligatorio.", f"{section}[{index}]"))
            if section == "commands" and not isinstance(item.get("args", []), list):
                diagnostics.append(Diagnostic("command.args debe ser una lista argv.", f"{section}[{index}].args"))
    for section in ("file_associations", "context_menus", "registry"):
        if section in data and not isinstance(data[section], list):
            diagnostics.append(Diagnostic(f"{section} debe ser una lista.", section))
    for section in ("shortcuts", "environments", "runtime"):
        if section in data and not isinstance(data[section], dict):
            diagnostics.append(Diagnostic(f"{section} debe ser un objeto.", section))
    assets = data.get("assets", [])
    if not isinstance(assets, list):
        diagnostics.append(Diagnostic("assets debe ser una lista.", "assets"))
    elif project_root:
        root = project_root.resolve()
        for index, item in enumerate(assets):
            if not isinstance(item, dict) or not isinstance(item.get("path"), str):
                diagnostics.append(Diagnostic("cada asset necesita path.", f"assets[{index}]"))
                continue
            candidate = (root / item["path"]).resolve()
            if root not in candidate.parents and candidate != root:
                diagnostics.append(Diagnostic("asset fuera de la raíz del proyecto.", f"assets[{index}].path"))
    return diagnostics


def parse_mexf(path: Path | str, *, project_root: Path | None = None) -> MexfDocument:
    source = Path(path)
    try:
        raw = source.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise MexfError(f"El documento .mexf no está en UTF-8: {exc}") from exc
    fmt = detect_mexf_format(source)
    if fmt == "legacy-json":
        data = json.loads(raw)
        return MexfDocument(_legacy_to_v1(data), "legacy-json", str(source))
    if fmt != "yaml-v1":
        if yaml is None:
            raise MexfError("PyYAML es necesario para leer .mexf YAML.")
        raise MexfError("Formato .mexf desconocido; se esperaba YAML v1 o JSON legacy.")
    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise MexfError("El documento .mexf debe ser un objeto YAML.")
    # Los assets se resuelven por defecto contra el directorio del propio
    # documento; el compilador pasa la raíz real del proyecto.
    errors = validate_mexf(data, project_root=project_root or source.parent)
    if errors:
        raise MexfError("; ".join(f"{e.path}: {e.message}" for e in errors))
    return MexfDocument(data, "yaml-v1", str(source))


def _legacy_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _legacy_to_v1(data: Dict[str, Any]) -> Dict[str, Any]:
    metadata = {
        "id": str(data.get("app_id") or "legacy.mexf"),
        "name": str(data.get("app_name") or "Legacy MEXF"),
        "version": str(data.get("version") or "1.0"),
    }
    commands = []
    for item in _legacy_list(data.get("shell_commands")):
        if isinstance(item, dict) and item.get("name") and item.get("path"):
            commands.append({"id": str(item["name"]), "executable": str(item["path"]), "args": []})
    associations = data.get("file_associations", data.get("extensions", []))
    shortcuts = data.get("shortcuts", {})
    return {"format": "mexf", "version": 1, "metadata": metadata, "runtime": {"launcher": "argv"}, "triggers": [], "commands": commands, "file_associations": copy.deepcopy(_legacy_list(associations)), "context_menus": copy.deepcopy(_legacy_list(data.get("context_menus"))), "shortcuts": copy.deepcopy(shortcuts if isinstance(shortcuts, dict) else {}), "environments": {}, "assets": []}


def canonicalize_mexf(document: MexfDocument | Dict[str, Any]) -> bytes:
    data = document.data if isinstance(document, MexfDocument) else document
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def migrate_legacy_mexf(path: Path | str, output_path: Path | str) -> Path:
    document = parse_mexf(path)
    if document.source_format != "legacy-json":
        raise MexfError("Sólo se pueden migrar documentos JSON legacy.")
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if yaml is None:
        raise MexfError("PyYAML es necesario para escribir la migración YAML.")
    target.write_text(yaml.safe_dump(document.data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return target
