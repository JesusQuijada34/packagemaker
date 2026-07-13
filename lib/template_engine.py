"""
Motor de plantillas para proyectos PackageMaker.
Carga archivos desde src/templates/ y sustituye variables __NOMBRE__.
"""

import hashlib
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from string import Template
from typing import Any, Dict, List, Optional
from xml.dom import minidom

from lib.projectNameFormatter import ProjectNameFormatter

DEFAULT_FOLDERS = ("app", "assets", "config", "docs", "source", "lib")

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


def get_templates_root() -> Path:
    """Raiz de plantillas: repo o bundle PyInstaller (_MEIPASS)."""
    candidates = []
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        candidates.append(Path(sys._MEIPASS) / "src" / "templates")
    here = Path(__file__).resolve().parent.parent
    candidates.append(here / "src" / "templates")
    if getattr(sys, "frozen", False):
        candidates.append(Path(sys.executable).resolve().parent / "src" / "templates")
    for path in candidates:
        if path.is_dir():
            return path
    return candidates[1]


def getversion() -> str:
    return time.strftime("%y.%m-%H.%M")


def _safe_substitute(content: str, variables: Dict[str, str]) -> str:
    """Sustituye __CLAVE__ en el texto."""
    result = content
    for key, value in variables.items():
        result = result.replace(f"__{key}__", str(value))
    return result


def load_template(relative_path: str) -> str:
    path = get_templates_root() / relative_path.replace("\\", "/")
    if not path.is_file():
        raise FileNotFoundError(f"Plantilla no encontrada: {path}")
    return path.read_text(encoding="utf-8")


def render_template(relative_path: str, variables: Dict[str, str]) -> str:
    return _safe_substitute(load_template(relative_path), variables)


def write_template(output_path: Path, relative_path: str, variables: Dict[str, str]) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_template(relative_path, variables), encoding="utf-8")
    return output_path


def save_pretty_xml_from_string(xml_content: str, filepath: Path) -> bool:
    """Formatea XML compatible (indentacion, sin lineas vacias)."""
    try:
        wrapped = xml_content.strip()
        if not wrapped.startswith("<?xml"):
            wrapped = f'<?xml version="1.0" encoding="UTF-8"?>\n{wrapped}'
        reparsed = minidom.parseString(wrapped.encode("utf-8"))
        pretty = reparsed.toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")
        lines = [line for line in pretty.splitlines() if line.strip()]
        filepath.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return True
    except Exception as exc:
        print(f"[template_engine] Error formateando XML: {exc}")
        return False


def detect_rating(app_id: str, name: str) -> str:
    text = f"{app_id} {name}".lower()
    for keyword, rate in AGE_RATINGS.items():
        if keyword in text:
            return rate
    return "Todas las edades"


def build_variables(
    publisher: str,
    app_id: str,
    name: str,
    author: str,
    platform: str,
    version_base: str = "1.0.0",
    description: str = "",
    license_year: Optional[str] = None,
) -> Dict[str, str]:
    """Construye todas las variables __*__ para plantillas de proyecto."""
    publisher_slug = ProjectNameFormatter.normalize_publisher(publisher)
    app_slug = ProjectNameFormatter.normalize_app_id(app_id)
    display_name = name.strip() or app_slug
    author_val = author.strip() or "Unknown"
    plat = ProjectNameFormatter.normalize_platform(platform)

    version_vso = ProjectNameFormatter.format_version_vso(version_base)
    version_full = ProjectNameFormatter.format_version_full(version_base, platform)
    
    # Usar ProjectNameFormatter para el nombre de carpeta
    folder_key = ProjectNameFormatter.format_project_folder(publisher, app_id, version_base, platform)
    
    correlation_id = hashlib.sha256(folder_key.encode()).hexdigest()
    rating = detect_rating(app_slug, display_name)
    year = license_year or time.strftime("%Y")
    xte = "exe" if plat in ("Knosthalij", "AlphaCube") else "appImage"
    product_version = version_base.split("-")[0] if "-" in version_base else version_base
    company = publisher_slug.capitalize()

    return {
        "PUBLISHER": publisher_slug.capitalize(),
        "APP": app_slug,
        "NAME": display_name,
        "VERSION": version_vso,
        "VERSION_VSO": version_vso,
        "VERSION_FULL": version_full,
        "VERSION_BASE": version_base,
        "AUTHOR": author_val,
        "PLATFORM": plat,
        "DESCRIPTION": description or f"Aplicacion creada con PackageMaker",
        "YEAR": year,
        "CORRELATIONID": correlation_id,
        "RATE": rating,
        "HASH": correlation_id,
        "OWNER": author_val,
        "REPO": app_slug,
        "FOLDER": "",  # se rellena por archivo container
        "COMPANY": company,
        "FILE_DESCRIPTION": f"{company} {display_name} by {author_val}",
        "FILE_VERSION": version_full,
        "INTERNAL_NAME": app_slug,
        "LEGAL_COPYRIGHT": f"(c) {company}. All rights reserved.",
        "ORIGINAL_FILENAME": f"{app_slug}.{xte}",
        "PRODUCT_NAME": f"{company} {display_name} {version_full}",
        "PRODUCT_VERSION": product_version,
        "XTE": xte,
    }


def normalize_platform(platform_text: str) -> str:
    """Convierte etiquetas de UI (Windows/Linux/Multi) a plataforma PackageMaker."""
    p = (platform_text or "").strip().lower()
    if "win" in p or p in ("knosthalij", "windows"):
        return "Knosthalij"
    if "lin" in p or "danen" in p or p == "linux":
        return "Danenone"
    if "multi" in p or "alpha" in p:
        return "AlphaCube"
    return platform_text.strip() if platform_text else "Knosthalij"


def write_details_xml(project_path: Path, variables: Dict[str, str]) -> bool:
    """Escribe details.xml formateado desde plantilla."""
    raw = render_template("project/details.xml.template", variables)
    return save_pretty_xml_from_string(raw, Path(project_path) / "details.xml")


def create_project_from_templates(
    project_path: Path,
    publisher: str,
    app_id: str,
    name: str,
    author: str,
    platform: str,
    version_base: str = "1.0.0",
    description: str = "",
) -> Dict[str, Any]:
    """
    Crea un proyecto completo usando plantillas en src/templates/.
    Retorna metadatos del proyecto creado.
    """
    project_path = Path(project_path)
    project_path.mkdir(parents=True, exist_ok=True)

    variables = build_variables(
        publisher, app_id, name, author, platform, version_base, description
    )
    created: List[str] = []

    for folder in DEFAULT_FOLDERS:
        (project_path / folder).mkdir(exist_ok=True)
        marker_vars = {**variables, "FOLDER": folder}
        marker_path = project_path / folder / f".{folder}-container"
        marker_path.write_text(
            render_template("project/container.marker.template", marker_vars),
            encoding="utf-8",
        )
        created.append(str(marker_path.relative_to(project_path)))

    mappings = [
        ("project/main.py.template", project_path / f"{variables['APP']}.py"),
        ("project/README.md.template", project_path / "README.md"),
        ("project/LICENSE.template", project_path / "LICENSE"),
        ("project/updater.py.template", project_path / "updater.py"),
        ("project/autorun.bat.template", project_path / "autorun.bat"),
        ("project/autorun.template", project_path / "autorun"),
        ("project/storedetail.template", project_path / ".storedetail"),
        ("project/version.res.template", project_path / "version.res"),
        ("config/settings.json.template", project_path / "config" / "settings.json"),
        ("lib/requirements.txt.template", project_path / "lib" / "requirements.txt"),
        ("docs/index.html.template", project_path / "docs" / "index.html"),
    ]

    if variables["PLATFORM"] in ("Knosthalij", "AlphaCube"):
        mappings.append(
            ("project/manifest.res.template", project_path / "manifest.res")
        )

    for rel_template, out_path in mappings:
        write_template(out_path, rel_template, variables)
        created.append(str(out_path.relative_to(project_path)))

    (project_path / "assets" / ".assets-container").touch(exist_ok=True)
    (project_path / "app" / ".app-container").touch(exist_ok=True)

    write_details_xml(project_path, variables)
    created.append("details.xml")

    return {
        "path": str(project_path),
        "variables": variables,
        "files": created,
        "hash": variables["CORRELATIONID"],
    }


def repair_project_from_templates(
    project_path: Path,
    publisher: str,
    app_id: str,
    name: str,
    author: str,
    platform: str,
    version_base: str = "1.0.0",
    description: str = "",
) -> Dict[str, Any]:
    """
    Repara un proyecto existente: restaura carpetas, details.xml y archivos faltantes
    usando plantillas en src/templates/ (no sobrescribe scripts existentes salvo XML).
    """
    project_path = Path(project_path)
    plat = normalize_platform(platform)
    variables = build_variables(
        publisher, app_id, name, author, plat, version_base, description or "Reparado por MoonFix"
    )
    repaired: List[str] = []

    for folder in DEFAULT_FOLDERS:
        folder_path = project_path / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        marker_path = folder_path / f".{folder}-container"
        if not marker_path.exists():
            marker_vars = {**variables, "FOLDER": folder}
            marker_path.write_text(
                render_template("project/container.marker.template", marker_vars),
                encoding="utf-8",
            )
            repaired.append(str(marker_path.relative_to(project_path)))

    write_details_xml(project_path, variables)
    repaired.append("details.xml")

    optional_files = [
        ("project/main.py.template", project_path / f"{variables['APP']}.py"),
        ("project/README.md.template", project_path / "README.md"),
        ("project/LICENSE.template", project_path / "LICENSE"),
        ("project/updater.py.template", project_path / "updater.py"),
        ("project/autorun.bat.template", project_path / "autorun.bat"),
        ("project/autorun.template", project_path / "autorun"),
        ("project/storedetail.template", project_path / ".storedetail"),
        ("project/version.res.template", project_path / "version.res"),
        ("config/settings.json.template", project_path / "config" / "settings.json"),
        ("lib/requirements.txt.template", project_path / "lib" / "requirements.txt"),
    ]
    if variables["PLATFORM"] in ("Knosthalij", "AlphaCube"):
        optional_files.append(
            ("project/manifest.res.template", project_path / "manifest.res")
        )

    for rel_template, out_path in optional_files:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if not out_path.exists():
            write_template(out_path, rel_template, variables)
            repaired.append(str(out_path.relative_to(project_path)))

    docs_path = project_path / "docs" / "index.html"
    docs_path.parent.mkdir(parents=True, exist_ok=True)
    if not docs_path.exists() or docs_path.stat().st_size < 500:
        write_template(docs_path, "docs/index.html.template", variables)
        repaired.append(str(docs_path.relative_to(project_path)))

    for touch in (
        project_path / "assets" / ".assets-container",
        project_path / "app" / ".app-container",
    ):
        touch.parent.mkdir(parents=True, exist_ok=True)
        if not touch.exists():
            touch.touch()
            repaired.append(str(touch.relative_to(project_path)))

    return {
        "path": str(project_path),
        "variables": variables,
        "files": repaired,
        "hash": variables["CORRELATIONID"],
    }
