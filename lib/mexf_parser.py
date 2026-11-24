"""Parser seguro y versionado para extensiones ``.mexf``.

El formato YAML v1 es declarativo: los comandos se representan como argv y no
se ejecutan durante el parseo. Los documentos JSON históricos se detectan y se
pueden migrar explícitamente, sin cambiar su significado silenciosamente.
"""
from __future__ import annotations

import base64
import copy
import datetime
import json
import math
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


def _classify_mexf_text(raw: str) -> Literal["yaml-v1", "legacy-json", "unknown"]:
    """Clasifica el texto de un ``.mexf`` sin volver a leer el archivo.

    ``legacy-json`` exige que el texto sea JSON real: un YAML con las mismas
    claves (``extensions``/``file_associations``/``context_menus``) no se puede
    entregar a ``json.loads`` y debe quedarse en ``unknown``.
    """
    is_json = True
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        is_json = False
        if yaml is None:
            return "unknown"
        try:
            value = yaml.safe_load(raw)
        except Exception:
            return "unknown"
    if not isinstance(value, dict):
        return "unknown"
    if value.get("format") == "mexf" and value.get("version") == 1:
        return "yaml-v1"
    if is_json and any(k in value for k in ("extensions", "file_associations", "context_menus")):
        return "legacy-json"
    return "unknown"


def detect_mexf_format(path: Path | str) -> Literal["yaml-v1", "legacy-json", "unknown"]:
    try:
        raw = Path(path).read_text(encoding="utf-8-sig")
    except (UnicodeDecodeError, OSError):
        return "unknown"
    return _classify_mexf_text(raw)


def _require_mapping(value: Any, name: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise MexfError(f"{name} debe ser un objeto YAML.")
    return value


def _json_safe(value: Any, _active: set | None = None) -> Any:
    """Normaliza un valor YAML a tipos serializables como JSON.

    ``yaml.safe_load`` produce objetos que ``json.dumps`` no sabe escribir
    (fechas, ``set``, ``bytes``, tuplas) y admite alias recursivos que JSON no
    puede representar. El contenedor ``.mexf`` es JSON canónico, así que el
    documento se normaliza al leerlo en vez de fallar al empaquetarlo.
    """
    if _active is None:
        _active = set()
    if isinstance(value, dict):
        marker = id(value)
        if marker in _active:
            raise MexfError("El documento .mexf contiene una referencia circular.")
        _active.add(marker)
        try:
            return {str(key): _json_safe(item, _active) for key, item in value.items()}
        finally:
            _active.discard(marker)
    if isinstance(value, (list, tuple)):
        marker = id(value)
        if marker in _active:
            raise MexfError("El documento .mexf contiene una referencia circular.")
        _active.add(marker)
        try:
            return [_json_safe(item, _active) for item in value]
        finally:
            _active.discard(marker)
    if isinstance(value, (set, frozenset)):
        marker = id(value)
        if marker in _active:
            raise MexfError("El documento .mexf contiene una referencia circular.")
        _active.add(marker)
        try:
            items = [_json_safe(item, _active) for item in value]
        finally:
            _active.discard(marker)
        return sorted(items, key=repr)
    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return value.isoformat()
    if isinstance(value, (bytes, bytearray)):
        return base64.b64encode(bytes(value)).decode("ascii")
    if isinstance(value, float) and not math.isfinite(value):
        # JSON no admite NaN/Infinity (YAML ``.nan``/``.inf`` o ``1e400`` en
        # el JSON legacy): se conserva el texto del escalar para que la salida
        # ``--shell-plan-json`` y el ``.mexf`` canónico sigan siendo JSON válido.
        return str(value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


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
    except OSError as exc:
        raise MexfError(f"No se pudo leer el documento .mexf {source}: {exc}") from exc
    fmt = _classify_mexf_text(raw)
    if fmt == "legacy-json":
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise MexfError(f"El documento .mexf JSON no es válido: {exc}") from exc
        if not isinstance(data, dict):
            raise MexfError("El documento .mexf debe ser un objeto JSON.")
        return MexfDocument(_json_safe(_legacy_to_v1(data)), "legacy-json", str(source))
    if fmt != "yaml-v1":
        if yaml is None:
            raise MexfError("PyYAML es necesario para leer .mexf YAML.")
        raise MexfError("Formato .mexf desconocido; se esperaba YAML v1 o JSON legacy.")
    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise MexfError("El documento .mexf debe ser un objeto YAML.")
    data = _json_safe(data)
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
    return json.dumps(_json_safe(data), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


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
