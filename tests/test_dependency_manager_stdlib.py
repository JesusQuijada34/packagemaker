"""Regresiones del detector de dependencias del editor (R-1c93e4b7).

``detect_imports_from_source`` clasificaba módulos de la biblioteca estándar
ausentes de la lista histórica (``hmac``, ``asyncio``, ``email``, ``tomllib``…)
como dependencias de PyPI: el editor las escribía en ``requirements.txt`` e
intentaba instalarlas con ``pip``.
"""

from __future__ import annotations

import sys
from pathlib import Path

from lib.dependency_manager import detect_imports_from_source


def test_stdlib_imports_are_ignored():
    source = "\n".join(
        [
            "import hmac",
            "import asyncio",
            "import ctypes",
            "import email",
            "import decimal",
            "import tomllib",
            "import sysconfig",
            "import operator",
            "import shlex",
            "import signal",
            "from os.path import join",
            "from concurrent.futures import ThreadPoolExecutor",
            "from xml.etree import ElementTree",
        ]
    )
    assert detect_imports_from_source(source) == set()


def test_third_party_imports_are_kept():
    source = "\n".join(
        [
            "import hmac",
            "import requests",
            "from PIL import Image",
            "from cryptography.fernet import Fernet",
        ]
    )
    assert detect_imports_from_source(source) == {"requests", "PIL", "cryptography"}


def test_local_modules_are_excluded(tmp_path: Path):
    (tmp_path / "helpers.py").write_text("VALUE = 1\n", encoding="utf-8")
    package = tmp_path / "mypkg"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    script = tmp_path / "app.py"
    script.write_text(
        "import helpers\nfrom mypkg import thing\nimport requests\n", encoding="utf-8"
    )

    found = detect_imports_from_source(
        script.read_text(encoding="utf-8"), script_path=str(script)
    )
    assert found == {"requests"}


def test_ide_bundled_modules_are_excluded():
    source = "import PyQt6\nfrom PyQt6.QtCore import Qt\nimport leviathan_ui\nimport requests\n"
    assert detect_imports_from_source(source, exclude_pyqt=True) == {"requests"}


def test_pyqt_can_be_kept_explicitly():
    source = "from PyQt6.QtCore import Qt\nimport leviathan_ui\nimport requests\n"
    assert detect_imports_from_source(source, exclude_pyqt=False) == {
        "PyQt6",
        "leviathan_ui",
        "requests",
    }


def test_stdlib_authority_is_available_in_this_interpreter():
    # La corrección depende de ``sys.stdlib_module_names`` (3.10+); el proyecto
    # ya exige intérpretes modernos, pero la prueba documenta la dependencia.
    assert "hmac" in sys.stdlib_module_names
