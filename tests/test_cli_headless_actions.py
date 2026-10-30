"""Regresión: las acciones de shell del CLI no deben llegar a ``window.show()``.

``--list-hardening`` devolvía un booleano desde el helper y el flujo principal
seguía como si fuera una ventana, terminando en
``AttributeError: 'bool' object has no attribute 'show'``. Estas pruebas fijan
que la acción se reconoce como "sin GUI" y que el flujo principal tolera un
valor que no es ventana.
"""
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

# Acciones que se resuelven sin instanciar ninguna ventana.
HEADLESS_ACTIONS = (
    "shellpatch_install",
    "show_version",
    "list_compilers",
    "list_hardening",
    "inspect_iflapp",
    "list_fonts",
    "download_fonts",
)


class CliHeadlessActionTests(unittest.TestCase):
    def test_main_treats_list_hardening_as_headless(self):
        source = (ROOT / "packagemaker.py").read_text(encoding="utf-8")
        for action in HEADLESS_ACTIONS:
            self.assertIn(f"'{action}'", source, f"{action} no está en la lista headless")

    def test_main_guards_against_non_window_results(self):
        source = (ROOT / "packagemaker.py").read_text(encoding="utf-8")
        self.assertIn('hasattr(window, "show")', source)

    def test_list_hardening_helper_returns_bool(self):
        from lib.cliHandler import HardeningReportHelper

        with patch.object(HardeningReportHelper, "report", return_value=True):
            from lib.cliHandler import handle_cli_action

            self.assertTrue(handle_cli_action("list_hardening", None, None))


if __name__ == "__main__":
    unittest.main()
