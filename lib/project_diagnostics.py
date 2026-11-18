# -*- coding: utf-8 -*-
"""Diagnóstico de proyectos PackageMaker para MoonFix.

Extraído del monolito ``packagemaker.py`` (Fase 1.1 de ``bugs.txt``): la
detección de inconsistencias de un proyecto es lógica pura sobre el sistema de
archivos y ``details.xml``, sin dependencia de la GUI. El wizard de MoonFix la
consume a través de la lista de incidencias que devuelve.

Cada incidencia es un ``dict`` con una clave ``type`` y, según el caso,
``path``/``name``/``desc``/``old``.
"""

from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from typing import Dict, List

REQUIRED_DIRS = ["app", "assets", "config", "docs", "source", "lib"]

# Incidencias que por sí solas obligan a abrir el wizard de reparación.
CRITICAL_STRUCTURAL = [
    "missing_dir",
    "invalid_package",
    "missing_xml",
    "missing_script",
    "dirty_version",
]

ICON_ISSUES = ["missing_icon", "missing_icon_updater"]

# El sufijo de plataforma pertenece al nombre, no a la versión: si aparece en
# ``version`` el nombre se considera sucio y hay que normalizarlo.
_PROHIBITED_VERSION_MARKERS = [
    "danenone",
    "knosthalij",
    "keystone",
    "windows",
    "linux",
    "darwin",
    "macos",
]


def check_project_issues(project_path: str) -> List[Dict[str, str]]:
    """Devuelve las incidencias estructurales y de assets de un proyecto.

    Sólo reporta problemas que merecen el wizard: si únicamente faltan assets
    opcionales (README, LICENSE, splash) y no hay daño estructural ni iconos
    ausentes, devuelve una lista vacía para no marcar proyectos sanos.
    """
    issues: List[Dict[str, str]] = []

    missing_dirs = [
        d for d in REQUIRED_DIRS if not os.path.exists(os.path.join(project_path, d))
    ]
    if len(missing_dirs) == len(REQUIRED_DIRS):
        issues.append({"type": "invalid_package", "desc": "Faltan todos los recursos estructurales"})
    else:
        for d in missing_dirs:
            issues.append({"type": "missing_dir", "path": d})

    xml_path = os.path.join(project_path, "details.xml")
    requires_wizard = False

    if not os.path.exists(xml_path):
        issues.append({"type": "missing_xml"})
        requires_wizard = True
    else:
        try:
            root = ET.parse(xml_path).getroot()
            data = {child.tag: (child.text or "").strip() for child in root}

            app_id = data.get("app")
            if app_id:
                script_path = os.path.join(project_path, f"{app_id}.py")
                if not os.path.exists(script_path):
                    issues.append({"type": "missing_script", "name": f"{app_id}.py"})
                    requires_wizard = True

            version = data.get("version", "")
            if version:
                lower = version.lower()
                if any(p in lower for p in _PROHIBITED_VERSION_MARKERS) or "-" not in version:
                    issues.append({"type": "dirty_version", "old": version})
                    requires_wizard = True

            if not os.path.exists(os.path.join(project_path, "README.md")):
                issues.append({"type": "missing_readme"})
            if not os.path.exists(os.path.join(project_path, "LICENSE")):
                issues.append({"type": "missing_license"})

            if not os.path.exists(os.path.join(project_path, "app", "app-icon.ico")):
                issues.append({"type": "missing_icon"})
            if not os.path.exists(os.path.join(project_path, "app", "product_logo.png")):
                issues.append({"type": "missing_logo"})
            if os.path.exists(os.path.join(project_path, "updater.py")):
                if not os.path.exists(os.path.join(project_path, "app", "updater-icon.ico")):
                    issues.append({"type": "missing_icon_updater"})

            if not os.path.exists(os.path.join(project_path, "assets", "splash.png")):
                issues.append({"type": "missing_splash"})
            if not os.path.exists(os.path.join(project_path, "assets", "splash_Setup.png")):
                issues.append({"type": "missing_splash_setup"})

        except (ET.ParseError, OSError):
            issues.append({"type": "corrupt_xml"})
            requires_wizard = True

    has_critical = any(i["type"] in CRITICAL_STRUCTURAL for i in issues)
    has_missing_icons = any(i["type"] in ICON_ISSUES for i in issues)

    if not requires_wizard and not has_critical and not has_missing_icons:
        return []

    return issues
