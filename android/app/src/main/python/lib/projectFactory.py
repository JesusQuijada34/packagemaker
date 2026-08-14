#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Project Factory - Creacion de proyectos PackageMaker via plantillas externas.
"""

import hashlib
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

from lib.template_engine import (
    DEFAULT_FOLDERS,
    build_variables,
    create_project_from_templates,
    get_templates_root,
    getversion,
    load_template,
    render_template,
    save_pretty_xml_from_string,
    write_details_xml,
    write_template,
    detect_rating,
)

try:
    from packagemaker import BASE_DIR, save_xml_pretty
except ImportError:
    BASE_DIR = os.path.join(os.path.expanduser("~"), "Documents", "Packagemaker Projects")

    def save_xml_pretty(element, filepath, encoding="utf-8"):
        from xml.dom import minidom
        import xml.etree.ElementTree as ET

        root = element.getroot() if hasattr(element, "getroot") else element
        rough = ET.tostring(root, encoding)
        reparsed = minidom.parseString(rough)
        pretty = reparsed.toprettyxml(indent="  ")
        lines = [line for line in pretty.split("\n") if line.strip()]
        Path(filepath).write_text("\n".join(lines) + "\n", encoding=encoding)
        return True


AGE_RATINGS = {
    "adult": "Adultos +18",
    "mature": "Adultos +18",
    "violence": "Adolescentes +16",
    "teen": "Adolescentes +13",
    "kids": "Ninos +7",
    "family": "Todas las edades",
    "edu": "Todas las edades",
    "education": "Todas las edades",
}


def create_project_structure(base_path, folders=None):
    folders = folders or DEFAULT_FOLDERS
    created = []
    for folder in folders:
        folder_path = os.path.join(base_path, folder.strip() if isinstance(folder, str) else folder)
        os.makedirs(folder_path, exist_ok=True)
        created.append(folder_path)
    return created


def create_container_markers(base_path, hash_val, folders=None):
    folders = folders or DEFAULT_FOLDERS
    variables = {"HASH": hash_val, "FOLDER": ""}
    created = []
    for folder in folders:
        folder_name = folder.strip() if isinstance(folder, str) else folder
        variables["FOLDER"] = folder_name
        marker_path = os.path.join(base_path, folder_name, f".{folder_name}-container")
        marker_path = Path(marker_path)
        marker_path.parent.mkdir(parents=True, exist_ok=True)
        marker_path.write_text(
            render_template("project/container.marker.template", variables),
            encoding="utf-8",
        )
        created.append(str(marker_path))
    return created


def create_details_xml(
    path,
    empresa,
    nombre_logico,
    nombre_completo,
    version,
    autor,
    plataforma_seleccionada,
    vso=None,
    rating=None,
    description="",
):
    version_base = version.split("-")[0] if "-" in str(version) else str(version)
    if vso:
        version_base = str(vso).lstrip("v").split("-")[0]

    variables = build_variables(
        empresa,
        nombre_logico,
        nombre_completo,
        autor,
        plataforma_seleccionada,
        version_base=version_base,
        description=description,
    )
    if rating:
        variables["RATE"] = rating

    return write_details_xml(Path(path), variables)


def create_main_script(path, app_id, template=None):
    variables = build_variables("influent", app_id, app_id, "author", "Knosthalij")
    script_path = Path(path) / f"{app_id}.py"
    if template:
        script_path.write_text(template, encoding="utf-8")
    else:
        write_template(script_path, "project/main.py.template", variables)
    return str(script_path)


def create_docs_index(path, owner, repo, template=None):
    docs_dir = Path(path) / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    variables = {"OWNER": owner, "REPO": repo}
    content = template if template else render_template("docs/index.html.template", variables)
    docs_index = docs_dir / "index.html"
    docs_index.write_text(content, encoding="utf-8")
    return str(docs_index)


def create_manifest_res(path, linkedsys_platform="knosthalij"):
    if linkedsys_platform.lower() not in ("knosthalij", "windows", "alphacube"):
        return None
    out = Path(path) / "manifest.res"
    out.write_text(load_template("project/manifest.res.template"), encoding="utf-8")
    return str(out)


def create_version_res(path, empresa, nombre_completo, nombre_logico, version, autor, xte="exe"):
    variables = build_variables(empresa, nombre_logico, nombre_completo, autor, "Knosthalij")
    variables.update(
        {
            "FILE_VERSION": version,
            "XTE": xte,
            "COMPANY": empresa.capitalize(),
            "FILE_DESCRIPTION": f"{empresa.capitalize()} {nombre_completo} by {autor}",
            "PRODUCT_VERSION": version.split("-")[0] if "-" in version else version,
        }
    )
    out = Path(path) / "version.res"
    write_template(out, "project/version.res.template", variables)
    return str(out)


def create_updater_script(path, template=None):
    updater_path = Path(path) / "updater.py"
    content = template if template else load_template("project/updater.py.template")
    updater_path.write_text(content, encoding="utf-8")
    return str(updater_path)


def create_store_detail(path, hash_val):
    variables = {"CORRELATIONID": hash_val}
    out = Path(path) / ".storedetail"
    write_template(out, "project/storedetail.template", variables)
    return str(out)


def create_license(path, license_type="MIT"):
    variables = build_variables("influent", "app", "App", "author", "Knosthalij")
    out = Path(path) / "LICENSE"
    if license_type.upper() != "MIT":
        out.write_text(f"{license_type} License\n\nCopyright (c) {variables['YEAR']}\n", encoding="utf-8")
    else:
        write_template(out, "project/LICENSE.template", variables)
    return str(out)


def create_readme(path, metadata):
    variables = build_variables(
        metadata.get("publisher", metadata.get("empresa", "influent")),
        metadata.get("app", "app"),
        metadata.get("name", "App"),
        metadata.get("author", "Unknown"),
        metadata.get("platform", "Knosthalij"),
        description=metadata.get("description", ""),
    )
    variables["VERSION_FULL"] = metadata.get("version", variables["VERSION_FULL"])
    out = Path(path) / "README.md"
    write_template(out, "project/README.md.template", variables)
    return str(out)


def create_autorun_scripts(path, nombre_logico, extension="py"):
    variables = build_variables("influent", nombre_logico, nombre_logico, "author", "Knosthalij")
    win_path = Path(path) / "autorun.bat"
    linux_path = Path(path) / "autorun"
    write_template(win_path, "project/autorun.bat.template", variables)
    write_template(linux_path, "project/autorun.template", variables)
    return str(win_path), str(linux_path)


def create_full_project(project_path, metadata, base_dir=None):
    """Crea proyecto completo usando src/templates/."""
    metadata = dict(metadata)
    empresa = metadata.get("empresa", metadata.get("publisher", "influent"))
    app_id = metadata.get("app", "myapp")
    name = metadata.get("name", app_id)
    version_base = metadata.get("version", "1.0.0")
    if "-" in str(version_base) and not str(version_base).startswith("v"):
        version_base = str(version_base).split("-")[0]
    author = metadata.get("author", "unknown")
    platform = metadata.get("platform", "Knosthalij")
    description = metadata.get("description", "")

    result = create_project_from_templates(
        Path(project_path),
        empresa,
        app_id,
        name,
        author,
        platform,
        version_base=version_base,
        description=description,
    )

    created_files = result["files"]
    return {
        "path": result["path"],
        "hash": result["hash"],
        "version": result["variables"]["VERSION_FULL"],
        "created_files": created_files,
        "templates_root": str(get_templates_root()),
    }


createProject = create_full_project
