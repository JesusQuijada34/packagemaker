# -*- coding: utf-8 -*-
"""Tests del diagnóstico de proyectos extraído a ``lib.project_diagnostics``.

Fase 1.1 de ``bugs.txt``: ``PackageTodoGUI.check_project_issues`` se movió a un
módulo dedicado. Estos tests ejercen la función real sobre proyectos de verdad
en disco, no mocks.
"""

import tempfile
import unittest
from pathlib import Path

from lib.project_diagnostics import check_project_issues


def _write_details_xml(path: Path, app: str = "myapp", version: str = "3.2.7-26.05"):
    (path / "details.xml").write_text(
        "<?xml version='1.0' encoding='utf-8'?>\n"
        "<project>\n"
        f"  <app>{app}</app>\n"
        f"  <version>{version}</version>\n"
        "  <publisher>influent</publisher>\n"
        "</project>\n",
        encoding="utf-8",
    )


class HealthyProjectTests(unittest.TestCase):
    def test_fully_healthy_project_reports_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for d in ("app", "assets", "config", "docs", "source", "lib"):
                (root / d).mkdir()
            _write_details_xml(root)
            (root / "myapp.py").write_text("print('hi')\n", encoding="utf-8")
            (root / "README.md").write_text("readme\n", encoding="utf-8")
            (root / "LICENSE").write_text("MIT\n", encoding="utf-8")
            (root / "app" / "app-icon.ico").write_bytes(b"ico")
            (root / "app" / "product_logo.png").write_bytes(b"png")
            (root / "assets" / "splash.png").write_bytes(b"png")
            (root / "assets" / "splash_Setup.png").write_bytes(b"png")

            self.assertEqual(check_project_issues(str(root)), [])

    def test_only_optional_assets_missing_does_not_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for d in ("app", "assets", "config", "docs", "source", "lib"):
                (root / d).mkdir()
            _write_details_xml(root)
            (root / "myapp.py").write_text("print('hi')\n", encoding="utf-8")
            # Icons present so no structural trigger; README/LICENSE/splash missing.
            (root / "app" / "app-icon.ico").write_bytes(b"ico")

            self.assertEqual(check_project_issues(str(root)), [])


class StructuralIssueTests(unittest.TestCase):
    def test_missing_dirs_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "app").mkdir()
            (root / "assets").mkdir()
            _write_details_xml(root)
            (root / "myapp.py").write_text("print('hi')\n", encoding="utf-8")

            issues = check_project_issues(str(root))
            types = [i["type"] for i in issues]
            self.assertIn("missing_dir", types)
            missing = [i["path"] for i in issues if i["type"] == "missing_dir"]
            self.assertIn("config", missing)
            self.assertIn("lib", missing)

    def test_all_dirs_missing_is_invalid_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            issues = check_project_issues(tmp)
            self.assertIn("invalid_package", [i["type"] for i in issues])

    def test_missing_xml_triggers_wizard(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for d in ("app", "assets", "config", "docs", "source", "lib"):
                (root / d).mkdir()
            issues = check_project_issues(str(root))
            self.assertIn("missing_xml", [i["type"] for i in issues])

    def test_dirty_version_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for d in ("app", "assets", "config", "docs", "source", "lib"):
                (root / d).mkdir()
            _write_details_xml(root, version="1.0.0-Windows")
            (root / "myapp.py").write_text("print('hi')\n", encoding="utf-8")

            issues = check_project_issues(str(root))
            self.assertIn("dirty_version", [i["type"] for i in issues])

    def test_version_without_platform_suffix_is_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for d in ("app", "assets", "config", "docs", "source", "lib"):
                (root / d).mkdir()
            _write_details_xml(root, version="3.2.7-26.05")
            (root / "myapp.py").write_text("print('hi')\n", encoding="utf-8")
            (root / "app" / "app-icon.ico").write_bytes(b"ico")

            issues = check_project_issues(str(root))
            self.assertNotIn("dirty_version", [i["type"] for i in issues])

    def test_missing_main_script_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for d in ("app", "assets", "config", "docs", "source", "lib"):
                (root / d).mkdir()
            _write_details_xml(root, app="ghost")
            # no ghost.py on disk
            issues = check_project_issues(str(root))
            self.assertIn("missing_script", [i["type"] for i in issues])

    def test_corrupt_xml_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for d in ("app", "assets", "config", "docs", "source", "lib"):
                (root / d).mkdir()
            (root / "details.xml").write_text("<project><app>oops", encoding="utf-8")

            issues = check_project_issues(str(root))
            self.assertIn("corrupt_xml", [i["type"] for i in issues])

    def test_missing_icon_triggers_wizard(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for d in ("app", "assets", "config", "docs", "source", "lib"):
                (root / d).mkdir()
            _write_details_xml(root)
            (root / "myapp.py").write_text("print('hi')\n", encoding="utf-8")
            # no app-icon.ico
            issues = check_project_issues(str(root))
            self.assertIn("missing_icon", [i["type"] for i in issues])


class DelegationTests(unittest.TestCase):
    def test_monolith_delegates_to_module(self):
        src = Path(__file__).resolve().parents[1] / "packagemaker.py"
        text = src.read_text(encoding="utf-8")
        self.assertIn("from lib.project_diagnostics import check_project_issues", text)


if __name__ == "__main__":
    unittest.main()
