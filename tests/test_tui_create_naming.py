# -*- coding: utf-8 -*-
"""El TUI debe sobrevivir a una versión de un solo componente.

Tras crear el proyecto, ``_screen_create`` recalculaba el nombre de la carpeta
con ``version.strip().split("-")[0]`` y los slugs en minúsculas. Con una versión
como ``2`` el formatter lanzaba ``ValueError`` y mataba el TUI justo después de
haber creado el proyecto; además el nombre mostrado no coincidía con la carpeta
real (el formatter conserva la capitalización del publisher).
"""
import unittest
from pathlib import Path
from unittest.mock import patch

from lib import tui


class TuiCreateNamingTests(unittest.TestCase):
    def _run_create(self, version, empresa="Influent", slug="demo-app"):
        # Orden de los campos en ``_screen_create``: publisher, slug, nombre
        # visible, versión, autor e icono opcional.
        answers = [empresa, slug, "Demo App", version, "Jesus", ""]

        def fake_prompt(label, default=""):
            return answers.pop(0) if answers else default

        ok_calls = []
        warn_calls = []

        with patch("lib.tui._clear"), patch("lib.tui._banner"), \
             patch("lib.tui._prompt", side_effect=fake_prompt), \
             patch("lib.tui._prompt_choice", return_value=0), \
             patch("lib.tui._prompt_bool", return_value=True), \
             patch("lib.tui._run_live", return_value=0), \
             patch("lib.tui._find_python", return_value="python"), \
             patch("lib.tui._base_dir", return_value=Path("/projects")), \
             patch("lib.tui._pause"), \
             patch("lib.tui._ok", side_effect=lambda msg: ok_calls.append(msg)), \
             patch("lib.tui._warn", side_effect=lambda msg: warn_calls.append(msg)):
            tui._screen_create()

        return ok_calls, warn_calls

    def test_single_component_version_does_not_crash(self):
        ok_calls, warn_calls = self._run_create("2")

        self.assertFalse(warn_calls, warn_calls)
        self.assertEqual(len(ok_calls), 1, ok_calls)
        self.assertIn("Influent.demo-app.v2.0-", ok_calls[0])
        self.assertIn("Knosthalij", ok_calls[0])

    def test_publisher_capitalization_is_preserved(self):
        ok_calls, _ = self._run_create("1.0.0", empresa="JesusQuijada")

        self.assertIn("JesusQuijada.demo-app.v1.0.0-", ok_calls[0])

    def test_formatter_error_is_reported_not_raised(self):
        with patch(
            "lib.tui.ProjectNameFormatter.format_project_folder",
            side_effect=ValueError("nombre inválido"),
        ):
            ok_calls, warn_calls = self._run_create("1.0.0")

        self.assertFalse(ok_calls)
        self.assertEqual(len(warn_calls), 1, warn_calls)
        self.assertIn("nombre inválido", warn_calls[0])


if __name__ == "__main__":
    unittest.main()
