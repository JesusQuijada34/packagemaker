# -*- coding: utf-8 -*-
"""Regresiones del backlog de reportes técnicos (issue #4).

Cubre con código real:

- ``R-dd68f3f4``: la salida de compilación en Termux/Android usa Download.
- ``R-f478fbef``: empaquetar ``.iflapp`` no exige cerrar el proyecto abierto.
- ``R-e2d317ce``: el gestor de apps solo lista proyectos fuente.
- ``R-e1a87de9``: los ajustes guardados se releen del almacén persistente.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

DETAILS = """<?xml version="1.0" encoding="utf-8"?>
<app>
  <publisher>Influent</publisher>
  <app>demo</app>
  <name>demo</name>
  <version>1.0.0</version>
  <platform>Danenone</platform>
  <author>JesusQuijada34</author>
</app>
"""


def _make_project(base: Path, name: str) -> Path:
    project = base / name
    project.mkdir(parents=True, exist_ok=True)
    (project / "details.xml").write_text(DETAILS, encoding="utf-8")
    (project / "app").mkdir(exist_ok=True)
    (project / "app" / "demo.py").write_text("print('hola')\n", encoding="utf-8")
    return project


class CompileOutputDirectoryTests(unittest.TestCase):
    """R-dd68f3f4: Termux/Android exporta al almacenamiento compartido."""

    def test_termux_and_android_target_shared_download(self):
        from lib.platform_detect import compile_output_directory

        for os_name in ("termux", "android"):
            path = compile_output_directory(os_name)
            self.assertTrue(
                "Download" in path or "downloads" in path,
                f"{os_name} debería exportar a Download, no a {path}",
            )

    def test_desktop_keeps_the_historical_output_path(self):
        from lib.platform_detect import compile_output_directory

        for os_name in ("linux", "windows", "darwin"):
            path = compile_output_directory(os_name)
            self.assertIn("Documents", path)
            self.assertIn("Compiled", path)


class OpenProjectPackagingTests(unittest.TestCase):
    """R-f478fbef: un proyecto abierto no bloquea el empaquetado."""

    def test_pack_iflapp_succeeds_with_open_source_files(self):
        from lib.iflapp_format import pack_iflapp, read_iflapp_header, verify_iflapp

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = _make_project(root, "Influent.demo.v1.0.0-26.05-20.13-Danenone")
            artifact = root / "Influent.demo.v1.0.0-26.05-20.13-Danenone.iflapp"

            handles = [
                open(project / "details.xml", "rb"),
                open(project / "app" / "demo.py", "rb"),
            ]
            try:
                produced = pack_iflapp(project, artifact)
            finally:
                for handle in handles:
                    handle.close()

            self.assertTrue(produced.is_file())
            self.assertTrue((project / "details.xml").is_file())
            self.assertTrue((project / "app" / "demo.py").is_file())
            self.assertEqual(read_iflapp_header(produced).identity()["app"], "demo")
            self.assertTrue(verify_iflapp(produced)["valid"])


class ProjectListingTests(unittest.TestCase):
    """R-e2d317ce: el gestor no lista artefactos de compilación."""

    def test_list_projects_ignores_build_outputs_and_non_projects(self):
        from lib.project_locator import list_projects

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            real = _make_project(base, "Influent.demo.v1.0.0-26.05-20.13-Danenone")

            # Artefactos que antes aparecían como si fueran proyectos.
            for artifact in ("dist", "build", "releases", "__pycache__", ".git"):
                folder = base / artifact
                folder.mkdir()
                (folder / "details.xml").write_text(DETAILS, encoding="utf-8")
            nuitka = base / "demo.build"
            nuitka.mkdir()
            (nuitka / "details.xml").write_text(DETAILS, encoding="utf-8")
            (base / "sin-metadatos").mkdir()

            self.assertEqual(list_projects(base), [real])

    def test_tui_manager_listing_uses_the_filtered_view(self):
        from lib import tui

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            real = _make_project(base, "Influent.demo.v1.0.0-26.05-20.13-Danenone")
            (base / "dist").mkdir()
            (base / "dist" / "details.xml").write_text(DETAILS, encoding="utf-8")

            self.assertEqual(tui._list_projects(base), [real])
            self.assertEqual(tui._list_projects(base / "no-existe"), [])


class SettingsPersistenceTests(unittest.TestCase):
    """R-e1a87de9: los ajustes se guardan y se releen del almacén real."""

    def test_saved_settings_are_read_back(self):
        import packagemaker as pm
        from lib import pm_data

        with tempfile.TemporaryDirectory() as tmp:
            store = pm_data.PMDataStore(Path(tmp) / "pm.data")
            previous = pm_data._store
            pm_data._store = store
            try:
                saved = pm.save_app_config({
                    "BASE_DIR": str(Path(tmp) / "proyectos"),
                    "Fluthin_APPS": str(Path(tmp) / "apps"),
                    "LANGUAGE": "EN",
                    "auto_translate": False,
                    "notifications_enabled": True,
                })
                reloaded = pm.load_app_config()
            finally:
                pm_data._store = previous

            self.assertTrue(saved)
            self.assertEqual(reloaded["BASE_DIR"], str(Path(tmp) / "proyectos"))
            self.assertEqual(reloaded["Fluthin_APPS"], str(Path(tmp) / "apps"))
            self.assertEqual(reloaded["LANGUAGE"], "en")
            self.assertFalse(reloaded["auto_translate"])
            self.assertTrue(reloaded["notifications_enabled"])

            # El valor también sobrevive a una instancia nueva del almacén.
            fresh = pm_data.PMDataStore(Path(tmp) / "pm.data")
            self.assertEqual(fresh.get_user("language"), "en")
            self.assertEqual(fresh.get_user("base_dir"), str(Path(tmp) / "proyectos"))


if __name__ == "__main__":
    unittest.main()
