# -*- coding: utf-8 -*-
"""R-8d3f6a21: el backend Nuitka embebido no podía compilar.

Nuitka 4.x rechaza las opciones de salida separadas por espacio
(``--output-dir DIR``) y aborta si se pide una familia de plugins Qt que la
instalación no trae (``styles``). Además, importar ``nuitka.MainControl``
fuera de su ``__main__`` lanza ``AssertionError`` y la excepción escapaba de
``compile_to_exe``. Estas pruebas fijan el contrato de los argumentos, el
reporte de versión y la degradación a subproceso.
"""

import importlib.util
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.blindcubeEngine import nuitka_embedded  # noqa: E402

_QT_PLUGIN_META = {"sensible", "all", "none", "qml"}


def _build_args(**overrides):
    params = {
        "script_path": "/tmp/app.py",
        "output_name": "app",
        "output_dir": "/tmp/dist",
        "windowed": True,
        "onefile": True,
    }
    params.update(overrides)
    return nuitka_embedded.EmbeddedNuitka().build_arguments(**params)


def _qt_plugin_families():
    try:
        from PyQt6.QtCore import QLibraryInfo

        plugins = Path(
            QLibraryInfo.path(QLibraryInfo.LibraryPath.PluginsPath)
        )
    except Exception:
        return None
    if not plugins.is_dir():
        return None
    return {entry.name for entry in plugins.iterdir() if entry.is_dir()}


class NuitkaArgumentTests(unittest.TestCase):
    def test_output_options_use_the_equals_syntax(self):
        args = _build_args()
        self.assertIn(f"--output-dir={os.path.abspath('/tmp/dist')}", args)
        self.assertIn("--output-filename=app", args)
        # Nuitka 4.x aborta con la forma separada por espacio.
        self.assertNotIn("--output-dir", args)
        self.assertNotIn("--output-filename", args)

    def test_requested_qt_plugin_families_exist(self):
        args = _build_args()
        requested = [
            arg.split("=", 1)[1]
            for arg in args
            if arg.startswith("--include-qt-plugins=")
        ]
        families = {
            family
            for value in requested
            for family in value.split(",")
            if family and family not in _QT_PLUGIN_META
        }
        available = _qt_plugin_families()
        if available is None:
            self.skipTest("PyQt6 no está instalado: no se puede validar la familia")
        unknown = sorted(families - available)
        self.assertEqual(unknown, [], f"Familias Qt inexistentes: {unknown}")

    def test_version_is_reported_when_nuitka_is_installed(self):
        if importlib.util.find_spec("nuitka") is None:
            self.skipTest("Nuitka no está instalado")
        self.assertRegex(nuitka_embedded.nuitka_version, r"^\d+\.\d+")

    def test_build_arguments_stay_deterministic(self):
        self.assertEqual(_build_args(), _build_args())
        self.assertEqual(_build_args(windowed=False)[-1], os.path.abspath("/tmp/app.py"))


class NuitkaFallbackTests(unittest.TestCase):
    def test_compile_falls_back_to_subprocess_when_api_import_fails(self):
        nk = nuitka_embedded.EmbeddedNuitka()
        nk.available = True

        def _fake_embedded():
            raise AssertionError("states.is_full_compat is not None")

        def _fake_subprocess(args, cwd=None, env=None):
            target = Path(nk_output_dir) / nk_output_name
            target.write_bytes(b"bin")
            return True, ""

        nk_output_dir = "/tmp/pm-nuitka-fallback"
        nk_output_name = "app"
        os.makedirs(nk_output_dir, exist_ok=True)
        try:
            with mock.patch.object(
                nuitka_embedded.EmbeddedNuitka,
                "_resolve_embedded_main",
                side_effect=_fake_embedded,
            ), mock.patch.object(
                nuitka_embedded.EmbeddedNuitka,
                "_run_subprocess_compiler",
                side_effect=_fake_subprocess,
            ):
                result = nk.compile_to_exe(
                    script_path=__file__,
                    output_name=nk_output_name,
                    output_dir=nk_output_dir,
                    build_dir="/tmp/pm-nuitka-build",
                )
            self.assertEqual(result, os.path.join(nk_output_dir, nk_output_name))
        finally:
            target = Path(nk_output_dir) / nk_output_name
            if target.exists():
                target.unlink()

    def test_compile_reports_the_subprocess_error_without_raising(self):
        nk = nuitka_embedded.EmbeddedNuitka()
        nk.available = True
        with mock.patch.object(
            nuitka_embedded.EmbeddedNuitka,
            "_resolve_embedded_main",
            side_effect=AssertionError("sin API interna"),
        ), mock.patch.object(
            nuitka_embedded.EmbeddedNuitka,
            "_run_subprocess_compiler",
            return_value=(False, "FATAL: pyqt6: Error"),
        ):
            result = nk.compile_to_exe(
                script_path=__file__,
                output_name="app",
                output_dir="/tmp/pm-nuitka-failure",
                build_dir="/tmp/pm-nuitka-build",
            )
        self.assertIsNone(result)
        self.assertIn("FATAL: pyqt6: Error", nk.get_last_error())


if __name__ == "__main__":
    unittest.main()
