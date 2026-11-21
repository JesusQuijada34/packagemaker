# -*- coding: utf-8 -*-
"""Regresión: el backend zipapp debe poder empaquetarse.

``ZipappBackend`` entrega ``<guion>.pyz``, no un binario nativo. El pipeline
``FlangCompiler`` sólo aceptaba ``<guion>``/``<guion>.exe``, así que la
compilación terminaba con "binarios faltantes" y nunca producía paquete: el
backend de reserva (siempre disponible) quedaba inservible.
"""

import sys
import tempfile
import unittest
from pathlib import Path

from lib.BuildThread import FlangCompiler
from lib.iflapp_format import read_iflapp_header, verify_iflapp

TARGET = "Windows" if sys.platform.startswith("win") else "Linux"


def _make_project(root: Path) -> Path:
    project = root / "project"
    project.mkdir()
    (project / "details.xml").write_text(
        "<app><publisher>Influent</publisher><app>portableapp</app>"
        "<version>v1.0</version><platform>AlphaCube</platform></app>",
        encoding="utf-8",
    )
    (project / "portableapp.py").write_text("print('portable')\n", encoding="utf-8")
    return project


class ZipappPackagingTests(unittest.TestCase):
    def test_zipapp_artifact_is_copied_and_accepted_by_create_package(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project = _make_project(root)
            output = root / "output"
            compiler = FlangCompiler(project, output, compiler_name="zipapp", sandbox=False)

            self.assertTrue(compiler.parse_details_xml())
            self.assertTrue(compiler.find_scripts())
            self.assertTrue(compiler.compile_binaries(TARGET), compiler.last_error)
            self.assertTrue(compiler.create_package(TARGET), compiler.last_error)

            package_dir = next(path for path in output.iterdir() if path.is_dir())
            self.assertTrue((package_dir / "portableapp.pyz").is_file())

    def test_zipapp_package_reaches_the_iflapp_manifest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project = _make_project(root)
            output = root / "output"
            compiler = FlangCompiler(project, output, compiler_name="zipapp", sandbox=False)

            self.assertTrue(compiler.parse_details_xml())
            self.assertTrue(compiler.find_scripts())
            self.assertTrue(compiler.compile_binaries(TARGET), compiler.last_error)
            self.assertTrue(compiler.create_package(TARGET), compiler.last_error)

            package_dir = next(path for path in output.iterdir() if path.is_dir())
            iflapp = output / "portable.iflapp"
            self.assertTrue(compiler.compress_to_iflapp(package_dir, iflapp), compiler.last_error)
            self.assertTrue(verify_iflapp(iflapp)["valid"])
            names = {entry["path"] for entry in read_iflapp_header(iflapp, include_blobs=False).manifest}
            self.assertIn("portableapp.pyz", names)

    def test_missing_artifacts_still_abort_packaging(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project = _make_project(root)
            compiler = FlangCompiler(project, root / "output", compiler_name="zipapp", sandbox=False)

            self.assertTrue(compiler.parse_details_xml())
            self.assertTrue(compiler.find_scripts())
            # Sin ejecutar compile_binaries no hay `dist`: el contrato del
            # paquete debe seguir rechazando la compilación.
            self.assertFalse(compiler.create_package(TARGET))


if __name__ == "__main__":
    unittest.main()
