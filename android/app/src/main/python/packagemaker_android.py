"""Núcleo PackageMaker ejecutable dentro de Android mediante Chaquopy.

La generación y validación de proyectos se ejecuta localmente. La generación de
binarios de escritorio que depende de PyInstaller/toolchains externos permanece
en el servidor SSH configurado por la aplicación.
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict

from lib.projectFactory import create_full_project
from lib.template_engine import repair_project_from_templates

REQUIRED_DIRS = ("app", "assets", "config", "docs", "source", "lib")


def create_project(root: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Crea un proyecto completo usando las plantillas originales."""
    publisher = metadata.get("publisher", metadata.get("empresa", "influent"))
    app_id = metadata.get("app", "myapp")
    version = metadata.get("version", "1.0.0")
    platform = metadata.get("platform", "Knosthalij")
    folder = f"{publisher}.{app_id}.{version}-{platform}"
    project_path = Path(root) / folder
    result = create_full_project(project_path, metadata, base_dir=root)
    return {"ok": True, "folder": folder, "path": str(project_path), "files": result["created_files"], "hash": result["hash"], "version": result["version"]}


def repair_project(path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    result = repair_project_from_templates(
        Path(path),
        metadata.get("publisher", metadata.get("empresa", "influent")),
        metadata.get("app", "myapp"),
        metadata.get("name", metadata.get("app", "myapp")),
        metadata.get("author", "Unknown"),
        metadata.get("platform", "Knosthalij"),
        metadata.get("version", "1.0.0"),
        metadata.get("description", "Reparado por PackageMaker Android"),
    )
    return {"ok": True, "path": str(path), "repaired": result.get("repaired", [])}


def validate_project(path: str) -> Dict[str, Any]:
    project = Path(path)
    missing = [name for name in REQUIRED_DIRS if not (project / name).is_dir()]
    details = project / "details.xml"
    valid = project.is_dir() and not missing and details.is_file()
    return {"ok": valid, "path": str(project), "missing": missing, "has_details": details.is_file(), "message": "Proyecto válido" if valid else "Faltan componentes del proyecto"}


def package_project(path: str, output: str) -> Dict[str, Any]:
    """Genera un .iflapp localmente; no compila binarios de escritorio."""
    project = Path(path).resolve()
    destination = Path(output).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    validation = validate_project(str(project))
    if not validation["ok"]:
        raise ValueError(json.dumps(validation, ensure_ascii=False))
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for item in project.rglob("*"):
            if item.is_file():
                archive.write(item, item.relative_to(project).as_posix())
    return {"ok": True, "path": str(destination), "bytes": destination.stat().st_size, "compiled": False, "message": "Paquete .iflapp generado; los binarios se compilan por SSH"}


def capabilities() -> Dict[str, Any]:
    return {"python": True, "create": True, "repair": True, "validate": True, "package": True, "desktop_binary_compile": False, "remote_compile": True}


def dispatch(action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if action == "capabilities":
        return capabilities()
    if action == "create":
        return create_project(payload["root"], payload.get("metadata", {}))
    if action == "repair":
        return repair_project(payload["path"], payload.get("metadata", {}))
    if action == "validate":
        return validate_project(payload["path"])
    if action == "package":
        return package_project(payload["path"], payload["output"])
    raise ValueError(f"Acción Python desconocida: {action}")


def main(action: str, payload_json: str) -> str:
    return json.dumps(dispatch(action, json.loads(payload_json or "{}")), ensure_ascii=False)
