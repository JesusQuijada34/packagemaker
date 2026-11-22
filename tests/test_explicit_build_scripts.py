import json
import tempfile
import unittest
from pathlib import Path

from lib.blindcubeEngine.BuildThread import FlangCompiler


class ExplicitBuildScriptsTests(unittest.TestCase):
    def _project(self, root: Path, settings: dict | None = None) -> Path:
        project = root / "project"
        project.mkdir()
        (project / "details.xml").write_text(
            "<app><publisher>Influent</publisher><app>foundstore</app><version>v1.2</version><platform>Danenone</platform></app>",
            encoding="utf-8",
        )
        (project / "foundstore.py").write_text("print('main')", encoding="utf-8")
        (project / "test_foundstore_ui.py").write_text("print('test')", encoding="utf-8")
        if settings is not None:
            config = project / "config"
            config.mkdir()
            (config / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
        return project

    def test_declared_scripts_limit_compilation_to_the_application_entry_point(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project = self._project(root, {"build": {"scripts": ["foundstore"]}})
            compiler = FlangCompiler(project, root / "output")

            self.assertTrue(compiler.parse_details_xml())
            self.assertTrue(compiler.find_scripts())
            self.assertEqual([script["name"] for script in compiler.scripts], ["foundstore"])

    def test_invalid_declared_script_name_rejects_the_build_selection(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project = self._project(root, {"build": {"scripts": ["../foundstore"]}})
            compiler = FlangCompiler(project, root / "output")

            self.assertFalse(compiler.find_scripts())
            self.assertIn("no seguro", compiler.last_error)

    def test_non_object_settings_fall_back_to_script_discovery(self):
        for settings in ([], "texto", 5, {"build": "texto"}):
            with self.subTest(settings=settings), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                project = self._project(root, settings)
                compiler = FlangCompiler(project, root / "output")

                self.assertIsNone(compiler.scripts_to_compile)
                self.assertTrue(compiler.parse_details_xml())
                self.assertTrue(compiler.find_scripts())
                self.assertEqual(
                    sorted(script["name"] for script in compiler.scripts),
                    ["foundstore", "test_foundstore_ui"],
                )


if __name__ == "__main__":
    unittest.main()
