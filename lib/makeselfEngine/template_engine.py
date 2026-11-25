# -*- coding: utf-8 -*-
"""Fachada de compatibilidad del motor de plantillas.

La autoridad vive en ``lib/makeselfEngine/templates.py``. Este módulo reexporta
su API para no romper a los módulos históricos que importan desde aquí.
"""
from __future__ import annotations

from lib.makeselfEngine.templates import (  # noqa: F401
    AGE_RATINGS,
    DEFAULT_FOLDERS,
    build_variables,
    create_project_from_templates,
    detect_rating,
    get_templates_root,
    getversion,
    load_template,
    normalize_platform,
    numeric_version,
    render_template,
    repair_project_from_templates,
    save_pretty_xml_from_string,
    templates_available,
    write_details_xml,
    write_template,
)

__all__ = [
    "AGE_RATINGS",
    "DEFAULT_FOLDERS",
    "build_variables",
    "create_project_from_templates",
    "detect_rating",
    "get_templates_root",
    "getversion",
    "load_template",
    "normalize_platform",
    "numeric_version",
    "render_template",
    "repair_project_from_templates",
    "save_pretty_xml_from_string",
    "templates_available",
    "write_details_xml",
    "write_template",
]
