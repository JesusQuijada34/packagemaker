# -*- coding: utf-8 -*-
"""Metadatos y lanzadores de los proyectos generados (plantillas).

Tres defectos reales de los artefactos que produce ``create_project_from_templates``:

- ``version.res`` declaraba ``FILEVERSION``/``PRODUCTVERSION`` fijos a
  ``5,15,3,0``, así que todos los paquetes mostraban esa versión en Windows.
- El CLI ``create`` pasaba el *shortname* como nombre visible, y ``--name``
  se perdía en ``details.xml``, el README y el ``ProductName``.
- ``autorun``/``autorun.bat`` llamaban a ``/usr/bin/python3 ./app.py``: una
  ruta que no existe en todas las plataformas y un ``.py`` que el paquete no
  incluye (el artefacto compilado es ``app`` o ``app.pyz``). Además el guion se
  generaba sin permiso de ejecución.
"""

import io
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from lib.cliHandler import handle_cli_action
from lib.makeselfEngine.templates import (
    create_project_from_templates,
    repair_project_from_templates,
)

TIMESTAMP = "26.11-10.00"


def _create(tmp: Path, version: str = "2.4.1", name: str = "Demo App") -> Path:
    project = tmp / "Influent.demo.v2.4.1-26.11-10.00-Danenone"
    create_project_from_templates(
        project,
        "Influent",
        "demo",
        name,
        "Jesus",
        "Danenone",
        version_base=version,
        timestamp=TIMESTAMP,
    )
    return project


class NumericVersionTests(unittest.TestCase):
    def test_four_word_fields(self):
        from lib.makeselfEngine.templates import numeric_version

        self.assertEqual(numeric_version("1.0.0"), "1,0,0,0")
        self.assertEqual(numeric_version("2.4"), "2,4,0,0")
        self.assertEqual(numeric_version("v3.2.7-26.05-20.13"), "3,2,7,26")

    def test_components_are_clamped_to_word_range(self):
        from lib.makeselfEngine.templates import numeric_version

        self.assertEqual(numeric_version("70000.1"), "65535,1,0,0")
        # Un componente absurdamente largo no debe reventar al convertirlo.
        self.assertEqual(numeric_version("9" * 5000 + ".1"), "65535,1,0,0")

    def test_without_numbers_falls_back_to_zeroes(self):
        from lib.makeselfEngine.templates import numeric_version

        self.assertEqual(numeric_version(""), "0,0,0,0")
        self.assertEqual(numeric_version(None), "0,0,0,0")


class VersionResourceTests(unittest.TestCase):
    def test_fileversion_matches_project_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = _create(Path(tmp))
            text = (project / "version.res").read_text(encoding="utf-8")
            self.assertIn("FILEVERSION 2,4,1,0", text)
            self.assertIn("PRODUCTVERSION 2,4,1,0", text)
            self.assertIn('VALUE "ProductVersion", "2.4.1"', text)
            self.assertNotIn("5,15,3,0", text)

    def test_two_component_version_is_padded(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = _create(Path(tmp), version="1.0")
            text = (project / "version.res").read_text(encoding="utf-8")
            self.assertIn("FILEVERSION 1,0,0,0", text)
            self.assertIn('VALUE "ProductVersion", "1.0"', text)


class CliVisibleNameTests(unittest.TestCase):
    def test_create_keeps_the_name_option(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            with redirect_stdout(io.StringIO()):
                handle_cli_action(
                    "create_project",
                    {
                        "path": str(base),
                        "name": "Demo App",
                        "shortname": "demo",
                        "publisher": "Influent",
                        "version": "2.4.1",
                        "platform": "linux",
                        "author": "Jesus",
                    },
                    None,
                    headless=True,
                )

            project = next(base.glob("Influent.demo.*"))
            # El nombre de carpeta sigue saliendo del shortname canónico.
            self.assertTrue(project.name.startswith("Influent.demo.v2.4.1-"))
            root = ET.parse(project / "details.xml").getroot()
            self.assertEqual(root.findtext("name"), "Demo App")
            self.assertEqual(root.findtext("app"), "demo")
            self.assertIn("Demo App", (project / "README.md").read_text(encoding="utf-8"))
            self.assertIn(
                "Demo App", (project / "version.res").read_text(encoding="utf-8")
            )


class AutorunTests(unittest.TestCase):
    def test_autorun_is_executable(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = _create(Path(tmp))
            mode = (project / "autorun").stat().st_mode
            self.assertTrue(mode & stat.S_IXUSR)

    def test_autorun_prefers_the_compiled_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = _create(Path(tmp))
            binary = project / "demo"
            binary.write_text("#!/bin/sh\necho binary-ran\n", encoding="utf-8")
            binary.chmod(0o755)

            result = subprocess.run(
                ["sh", str(project / "autorun")],
                capture_output=True,
                text=True,
                cwd=str(project),
                timeout=60,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("binary-ran", result.stdout)

    def test_autorun_runs_the_zipapp_when_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = _create(Path(tmp))
            (project / "demo.pyz").write_bytes(b"not-a-real-zipapp")

            text = (project / "autorun").read_text(encoding="utf-8")

            self.assertIn("./demo.pyz", text)
            self.assertNotIn("/usr/bin/python3", text)

    @unittest.skipUnless(shutil.which("python3"), "sin python3 en PATH")
    def test_autorun_falls_back_to_the_source_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = _create(Path(tmp))

            result = subprocess.run(
                ["sh", str(project / "autorun")],
                capture_output=True,
                text=True,
                cwd=str(project),
                timeout=60,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Hola desde demo", result.stdout)

    def test_repair_makes_an_existing_autorun_executable(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = _create(Path(tmp))
            autorun = project / "autorun"
            autorun.chmod(0o644)

            repair_project_from_templates(
                project,
                "Influent",
                "demo",
                "Demo App",
                "Jesus",
                "Danenone",
                version_base="2.4.1",
                timestamp=TIMESTAMP,
            )

            self.assertTrue(autorun.stat().st_mode & stat.S_IXUSR)


if __name__ == "__main__":
    unittest.main()
