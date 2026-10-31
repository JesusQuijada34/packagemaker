# -*- coding: utf-8 -*-
"""Localiza proyectos de PackageMaker leyendo sus metadatos.

El nombre de la carpeta lleva la marca temporal del momento de creación, así que
reconstruirlo a mano (``publisher.app.v1.0-...``) casi nunca coincide con el
proyecto real. En vez de adivinar el nombre, este módulo recorre ``base_dir`` y
lee ``details.xml`` de cada candidato.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def read_metadata(details_path: Path) -> Dict[str, str]:
    """Devuelve los metadatos de un ``details.xml`` o ``{}`` si no se puede leer."""
    try:
        root = ET.parse(details_path).getroot()
    except (OSError, ET.ParseError):
        return {}
    return {
        "publisher": (root.findtext("publisher") or root.findtext("empresa") or "").strip(),
        "app": (root.findtext("app") or root.findtext("name") or "").strip(),
        "platform": (root.findtext("platform") or root.findtext("plataforma") or "").strip(),
        "version": (root.findtext("version") or "").strip(),
    }


def iter_projects(base_dir) -> List[Tuple[Path, Dict[str, str]]]:
    """Lista ``(carpeta, metadatos)`` de cada subcarpeta con ``details.xml``."""
    base = Path(base_dir)
    if not base.is_dir():
        return []
    projects = []
    for item in sorted(base.iterdir()):
        details = item / "details.xml"
        if item.is_dir() and details.is_file():
            projects.append((item, read_metadata(details)))
    return projects


def locate_project(
    base_dir,
    publisher: Optional[str] = None,
    app_id: Optional[str] = None,
    platform: Optional[str] = None,
) -> Optional[Path]:
    """Devuelve la carpeta del proyecto que mejor coincide con los metadatos.

    La comparación no distingue mayúsculas. Sin ``app_id`` devuelve el proyecto
    más reciente; ante varios candidatos también gana el más reciente.
    """
    candidates = []
    for path, meta in iter_projects(base_dir):
        if app_id and meta.get("app", "").lower() != str(app_id).lower():
            continue
        if publisher and meta.get("publisher", "").lower() != str(publisher).lower():
            continue
        if platform and meta.get("platform", "").lower() != str(platform).lower():
            continue
        try:
            mtime = path.stat().st_mtime
        except OSError:
            mtime = 0
        candidates.append((mtime, path))
    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1]


def describe_available(base_dir) -> str:
    """Resumen legible de los proyectos disponibles, para mensajes de error."""
    projects = iter_projects(base_dir)
    if not projects:
        return "(no hay proyectos con details.xml en la carpeta base)"
    lines = []
    for path, meta in projects:
        app = meta.get("app") or "?"
        publisher = meta.get("publisher") or "?"
        platform = meta.get("platform") or "?"
        lines.append(f"  - {path.name}  [{publisher}.{app} / {platform}]")
    return "\n".join(lines)
