"""Regresión: ``--app-version`` debe reportar la versión canónica (R-9e2a5c73).

El entrypoint importaba ``version.VERSION`` (módulo inexistente) y caía en un
valor fijo ``3.2.7``; el comando de versión se quedaba obsoleto en cada release
y no coincidía con ``details.xml``. Además ``show_version`` imprimía ``vv``.
"""

from __future__ import annotations

import subprocess
import sys
import xml.etree.ElementTree as ET
from io import StringIO
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]


def _canonical_version() -> str:
    root = ET.parse(REPO_ROOT / "details.xml").getroot()
    return (root.findtext("version") or "").strip().lstrip("vV")


def test_app_version_reports_details_xml_version():
    result = subprocess.run(
        [sys.executable, "packagemaker.py", "--app-version"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == f"Influent Package Maker v{_canonical_version()}"


def test_show_version_does_not_duplicate_the_v_prefix():
    from lib.cliHandler import handle_cli_action

    output = StringIO()
    with patch("sys.stdout", output):
        assert handle_cli_action("show_version", None, None) is True
    first_line = output.getvalue().splitlines()[0]
    assert first_line == f"Influent Package Maker v{_canonical_version()}"
    assert "vv" not in first_line
