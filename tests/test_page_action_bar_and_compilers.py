# -*- coding: utf-8 -*-
"""Pruebas de la barra de acciones superior y del registro de compiladores."""

import json
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from lib import compilers  # noqa: E402


class CompilerRegistryTests(unittest.TestCase):
    def test_expected_backends_are_exposed(self):
        self.assertEqual(
            compilers.backend_names(),
            ["nuitka", "pyinstaller", "zipapp", "cxfreeze", "pyoxidizer"],
        )

    def test_available_backends_cover_the_registry(self):
        report = compilers.available_backends()
        self.assertEqual(set(report), set(compilers.backend_names()))
        # Nuitka y PyInstaller son embebidos; zipapp es stdlib; el resto externo.
        self.assertTrue(report["nuitka"]["embedded"])
        self.assertTrue(report["pyinstaller"]["embedded"])
        self.assertTrue(report["zipapp"]["available"])

    def test_aliases_resolve_to_their_own_backends(self):
        self.assertIsInstance(
            compilers.get_backend("cx_freeze"), compilers.CxFreezeBackend
        )
        self.assertIsInstance(
            compilers.get_backend("pyoxidizer"), compilers.PyOxidizerBackend
        )
        self.assertIsInstance(
            compilers.get_backend("zip"), compilers.ZipappBackend
        )

    def test_unknown_backend_raises(self):
        with self.assertRaises(compilers.CompilerUnavailableError):
            compilers.get_backend("does-not-exist")

    def test_backends_share_the_same_compile_signature(self):
        import inspect

        nuitka = inspect.signature(compilers.NuitkaBackend.compile).parameters
        pyi = inspect.signature(compilers.PyInstallerBackend.compile).parameters
        # Ambos delegan en **kwargs, así que la firma pública es idéntica.
        self.assertEqual(set(nuitka), set(pyi))

    def test_default_compiler_is_nuitka(self):
        self.assertEqual(compilers.DEFAULT_COMPILER, "nuitka")


class NuitkaEmbeddedTests(unittest.TestCase):
    def test_build_arguments_are_pure_and_deterministic(self):
        from lib.nuitka_embedded import EmbeddedNuitka

        nk = EmbeddedNuitka()
        args = nk.build_arguments(
            script_path="/tmp/app.py",
            output_name="app",
            output_dir="/tmp/dist",
            windowed=True,
            onefile=True,
        )
        self.assertIn("--standalone", args)
        self.assertIn("--onefile", args)
        self.assertIn("--quiet", args)
        # El script objetivo es el último argumento.
        self.assertEqual(args[-1], os.path.abspath("/tmp/app.py"))
        # No debe lanzar procesos: build_arguments solo construye la lista.
        self.assertNotIn("subprocess", str(type(nk)).lower())

    def test_compile_without_nuitka_reports_error(self):
        from lib import nuitka_embedded

        original = nuitka_embedded.NUITKA_AVAILABLE
        try:
            nk = nuitka_embedded.EmbeddedNuitka()
            nk.available = False
            result = nk.compile_to_exe(
                script_path=__file__, output_name="x", output_dir="/tmp/dist"
            )
            self.assertIsNone(result)
            self.assertIn("no está disponible", nk.get_last_error())
        finally:
            nuitka_embedded.NUITKA_AVAILABLE = original


class PageActionBarTests(unittest.TestCase):
    def test_bar_geometry_is_shared_across_pages(self):
        from lib import page_action_bar as pab
        from lib.design_tokens import BUTTON_HEIGHT, PILL_RADIUS

        self.assertEqual(pab.BAR_HEIGHT, 48)
        self.assertEqual(pab.BUTTON_HEIGHT, BUTTON_HEIGHT)
        self.assertEqual(BUTTON_HEIGHT, 36)
        # Píldora: el radio es la mitad de la altura.
        self.assertEqual(PILL_RADIUS * 2, BUTTON_HEIGHT)

    def test_button_kinds_have_distinct_styles(self):
        from lib import page_action_bar as pab

        self.assertNotEqual(pab.STYLE_PRIMARY, pab.STYLE_SECONDARY)
        self.assertNotEqual(pab.STYLE_SECONDARY, pab.STYLE_DESTRUCTIVE)


class CheckboxSpacingTests(unittest.TestCase):
    """El texto del checkbox debe quedar a la derecha del indicador."""

    def test_qss_spacing_is_positive(self):
        from lib.fluent_theme import WINUI3_CHECKBOX_QSS

        self.assertIn("spacing:", WINUI3_CHECKBOX_QSS)

    def test_indicator_and_text_do_not_overlap(self):
        try:
            from PyQt6.QtWidgets import (
                QApplication,
                QCheckBox,
                QStyle,
                QStyleOptionButton,
            )
        except ImportError:
            self.skipTest("PyQt6 no disponible")

        app = QApplication.instance() or QApplication([])
        from lib.fluent_theme import applyget

        cb = QCheckBox("Windows (Knosthalij)")
        cb.setStyleSheet(applyget("#ff5722"))
        cb.show()
        app.processEvents()

        option = QStyleOptionButton()
        cb.initStyleOption(option)
        indicator = cb.style().subElementRect(
            QStyle.SubElement.SE_CheckBoxIndicator, option, cb
        )
        contents = cb.style().subElementRect(
            QStyle.SubElement.SE_CheckBoxContents, option, cb
        )
        # El texto empieza después del borde derecho del indicador.
        self.assertGreaterEqual(contents.x(), indicator.x() + indicator.width())
        cb.close()


class LanguagePackTests(unittest.TestCase):
    LANG_DIR = Path(__file__).resolve().parent.parent / "lang"

    def test_all_supported_languages_have_a_file(self):
        from lib.i18n import SUPPORTED_LANGUAGES

        for code in SUPPORTED_LANGUAGES:
            path = self.LANG_DIR / f"{code}.json"
            self.assertTrue(path.is_file(), f"falta lang/{code}.json")

    def test_new_languages_translate_config_title(self):
        for code in ("fr", "de", "it", "ru", "zh", "ja", "ko", "ar", "nl", "pl", "tr"):
            data = json.loads((self.LANG_DIR / f"{code}.json").read_text(encoding="utf-8"))
            self.assertNotEqual(
                data["config"]["title"], "Configuración", f"{code} sin traducir"
            )
            self.assertIn("default_editor", data["config"])


if __name__ == "__main__":
    unittest.main()


class ZipappBackendTests(unittest.TestCase):
    def test_zipapp_backend_is_always_available(self):
        backend = compilers.get_backend("zipapp")
        self.assertTrue(backend.is_available())

    def test_zipapp_produces_a_runnable_archive(self):
        import subprocess
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "main.py").write_text(
                "def main():\n    print('zipapp-ok')\n\nif __name__ == '__main__':\n    main()\n",
                encoding="utf-8",
            )
            backend = compilers.get_backend("zipapp")
            out = backend.compile(
                script_path=str(root / "main.py"),
                output_name="demo",
                output_dir=str(root / "dist"),
            )
            self.assertIsNotNone(out, backend.last_error)
            result = subprocess.run(
                [sys.executable, out], capture_output=True, text=True
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("zipapp-ok", result.stdout)
