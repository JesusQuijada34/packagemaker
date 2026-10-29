"""Regresión: la fuente de UI no debe consultarse antes de QGuiApplication.

``QFontDatabase.families()`` aborta con "Must construct a QGuiApplication
before accessing QFontDatabase" cuando no hay aplicación viva. El arranque de
``packagemaker`` resolvía la fuente a nivel de módulo, antes de crear
``QApplication``, por lo que el warning aparecía en cada inicio.
"""
import os
import subprocess
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PyQt6.QtGui import QFontDatabase, QGuiApplication
    from PyQt6.QtWidgets import QApplication

    from lib.fluent_theme import PYQT6_AVAILABLE, preferred_ui_font

    QT_READY = PYQT6_AVAILABLE
except ImportError:  # PyQt6 y sus librerías de sistema son opcionales.
    QT_READY = False

ROOT = Path(__file__).resolve().parents[1]
WARNING = "Must construct a QGuiApplication before accessing QFontDatabase"


@unittest.skipUnless(QT_READY, "PyQt6 no está disponible en este entorno")
class PreferredFontApplicationGuardTests(unittest.TestCase):
    def test_importing_the_app_emits_no_font_database_warning(self):
        """Importar ``packagemaker`` no debe disparar el warning de Qt."""
        env = dict(os.environ, QT_QPA_PLATFORM="offscreen")
        result = subprocess.run(
            [sys.executable, "-c", "import packagemaker"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        self.assertNotIn(WARNING, result.stderr)

    def test_preferred_font_without_application_returns_fallback(self):
        """Sin QGuiApplication debe devolver el fallback, no consultar la BD."""
        if QGuiApplication.instance() is not None:
            self.skipTest("otra prueba ya construyó una QGuiApplication")
        font = preferred_ui_font(11)
        self.assertIsNotNone(font)
        self.assertEqual(font.pointSize(), 11)

    def test_preferred_font_with_application_uses_real_families(self):
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)
        font = preferred_ui_font(12)
        self.assertIsNotNone(font)
        self.assertEqual(font.pointSize(), 12)
        installed = {name.casefold() for name in QFontDatabase.families()}
        if font.family() != "sans-serif":
            self.assertIn(font.family().casefold(), installed)

    def test_module_import_does_not_touch_font_database(self):
        """El módulo no debe resolver la fuente al importarse."""
        source = (ROOT / "packagemaker.py").read_text(encoding="utf-8")
        self.assertNotIn("APP_FONT = preferred_ui_font", source)
        self.assertIn("def app_font(", source)


if __name__ == "__main__":
    unittest.main()
