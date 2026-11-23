# -*- coding: utf-8 -*-
"""Configuración local corrupta no debe impedir arrancar la interfaz.

Ciclo 24. Cubre dos fallos de arranque descubiertos en la auditoría:

- ``R-9c1e5b74``: un ``data/pm.data`` con valores no numéricos en
  ``sidebar_width``/``sidebar_accent_width``/``card_opacity``/``dpi_scale``
  reventaba en ``int()``/``float()`` al construir la ventana principal.
- ``R-2b7d4a90``: ``pmCodeEditor.find_flarm_project`` propagaba
  ``PermissionError`` (carpeta de proyectos ilegible), ``JSONDecodeError``
  (``package_config.json`` truncado) o ``AttributeError`` (JSON que no es
  objeto) al arrancar el editor con un nombre de proyecto.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib import pm_data  # noqa: E402
from lib.pm_data import PMDataStore  # noqa: E402

try:
    from PyQt6.QtWidgets import QApplication
except ImportError:  # pragma: no cover
    QApplication = None

_UNREADABLE_SKIP = unittest.skipIf(
    os.name == "nt" or (hasattr(os, "geteuid") and os.geteuid() == 0),
    reason="los permisos POSIX no bloquean la lectura en Windows ni como root",
)

_APP = None


def _ensure_app():
    global _APP
    if QApplication is None:
        raise unittest.SkipTest("PyQt6 no disponible")
    if _APP is None:
        _APP = QApplication.instance() or QApplication([])
    return _APP


class CoercionTests(unittest.TestCase):
    def test_coerce_int_accepts_numeric_text(self):
        self.assertEqual(pm_data.coerce_int("4", 3), 4)
        self.assertEqual(pm_data.coerce_int(3.9, 3), 3)
        self.assertEqual(pm_data.coerce_int(True, 3), 1)

    def test_coerce_int_falls_back_to_default(self):
        for value in ("tres", [1], None, {"a": 1}):
            with self.subTest(value=value):
                self.assertEqual(pm_data.coerce_int(value, 7), 7)

    def test_coerce_float_falls_back_to_default(self):
        self.assertEqual(pm_data.coerce_float("opaco", 0.08), 0.08)
        self.assertEqual(pm_data.coerce_float(None, 1.0), 1.0)
        self.assertAlmostEqual(pm_data.coerce_float("0.25", 1.0), 0.25)

    def test_store_numeric_getters_ignore_corrupt_values(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "pm.data"
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "user": {
                            "sidebar_width": "ocho",
                            "sidebar_accent_width": [3],
                            "card_opacity": "opaco",
                            "dpi_scale": None,
                        },
                    }
                ),
                encoding="utf-8",
            )
            store = PMDataStore(path)
            self.assertEqual(store.get_user_int("sidebar_width", 260), 260)
            self.assertEqual(store.get_user_int("sidebar_accent_width", 3), 3)
            self.assertAlmostEqual(store.get_user_float("card_opacity", 0.08), 0.08)
            self.assertAlmostEqual(store.get_user_float("dpi_scale", 1.0), 1.0)


@unittest.skipIf(QApplication is None, "PyQt6 no disponible")
class SettingsPanelRobustnessTests(unittest.TestCase):
    def setUp(self):
        _ensure_app()

    def test_non_numeric_personalization_values_do_not_break_panel(self):
        from PyQt6.QtWidgets import QWidget

        from lib.settings_panel import SettingsPanel

        host = QWidget()
        with tempfile.TemporaryDirectory() as temp_dir:
            payloads = [
                {"sidebar_accent_width": "tres"},
                {"card_opacity": "opaco"},
                {"card_opacity": None},
                {"sidebar_accent_width": [1]},
                {"sidebar_accent_width": {"v": 2}, "card_opacity": {"v": 0.2}},
            ]
            for payload in payloads:
                with self.subTest(payload=payload):
                    user = dict(payload, base_dir=temp_dir, fluthin_apps=temp_dir)
                    panel = SettingsPanel(host, user)
                    self.assertEqual(panel.widgets["conf_sidebar_accent_slider"].value(), 3)
                    self.assertEqual(panel.widgets["conf_card_opacity_slider"].value(), 8)


@unittest.skipIf(QApplication is None, "PyQt6 no disponible")
class FindFlarmProjectTests(unittest.TestCase):
    def _patch_home(self, home):
        original = os.path.expanduser

        def fake_expanduser(path):
            if path == "~":
                return str(home)
            if path.startswith("~/"):
                return str(home / path[2:])
            return original(path)

        patcher = mock.patch.object(os.path, "expanduser", fake_expanduser)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_corrupt_package_config_is_ignored(self):
        import pmCodeEditor

        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            self._patch_home(home)
            base = home / "Documents" / "Packagemaker Projects"
            project = base / "roto"
            project.mkdir(parents=True)
            (project / "package_config.json").write_text("{no es json", encoding="utf-8")
            self.assertIsNone(pmCodeEditor.find_flarm_project("demo"))

    def test_non_object_package_config_is_ignored(self):
        import pmCodeEditor

        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            self._patch_home(home)
            base = home / "Documents" / "Packagemaker Projects"
            project = base / "lista"
            project.mkdir(parents=True)
            (project / "package_config.json").write_text("[1, 2]", encoding="utf-8")
            self.assertIsNone(pmCodeEditor.find_flarm_project("demo"))

    def test_non_text_fields_do_not_break_the_search(self):
        import pmCodeEditor

        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            self._patch_home(home)
            base = home / "Documents" / "Packagemaker Projects"
            project = base / "numerico"
            project.mkdir(parents=True)
            (project / "package_config.json").write_text(
                json.dumps({"titulo": 5, "empresa": None, "id": ["x"]}), encoding="utf-8"
            )
            self.assertIsNone(pmCodeEditor.find_flarm_project("demo"))

    def test_valid_package_config_still_matches(self):
        import pmCodeEditor

        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            self._patch_home(home)
            base = home / "Documents" / "Packagemaker Projects"
            project = base / "influent.demo.v1.0.0-26.11-10.00-AlphaCube"
            project.mkdir(parents=True)
            (project / "package_config.json").write_text(
                json.dumps({"titulo": "Demo", "empresa": "Influent", "id": "demo"}),
                encoding="utf-8",
            )
            self.assertEqual(str(project), pmCodeEditor.find_flarm_project("Demo"))

    @_UNREADABLE_SKIP
    def test_unreadable_projects_folder_returns_none(self):
        import pmCodeEditor

        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            self._patch_home(home)
            base = home / "Documents" / "Packagemaker Projects"
            base.mkdir(parents=True)
            os.chmod(base, 0o000)
            try:
                self.assertIsNone(pmCodeEditor.find_flarm_project("demo"))
            finally:
                os.chmod(base, 0o755)


if __name__ == "__main__":
    unittest.main()
