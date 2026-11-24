# -*- coding: utf-8 -*-
"""Motor del IDE de proyectos ``iflapp``: escaneo, compilación y depurador."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.iflapp_ide import (  # noqa: E402
    compile_project,
    debug_script,
    detect_hidden_imports,
    find_scripts,
    run_script,
    scan_project,
    trace_script,
)

DETAILS = """<app>
  <publisher>Tesla-Inc</publisher>
  <app>demo</app>
  <name>Demo</name>
  <version>v1.0-26.05-20.13-Danenone</version>
  <author>Jesus</author>
  <platform>Danenone</platform>
  <description>Demo</description>
  <year>2026</year>
</app>
"""

SETTINGS = {"build": {"scripts": ["demo.py"]}}

MAIN = """import os
import json


def saluda(nombre):
    mensaje = f"hola {nombre}"
    return mensaje


print(saluda("mundo"))
"""


class IdeProjectTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "proyecto"
        (self.root / "config").mkdir(parents=True)
        (self.root / "app").mkdir()
        (self.root / "details.xml").write_text(DETAILS, encoding="utf-8")
        (self.root / "config" / "settings.json").write_text(json.dumps(SETTINGS), encoding="utf-8")
        (self.root / "demo.py").write_text(MAIN, encoding="utf-8")
        (self.root / "app" / "demo-icon.ico").write_bytes(b"ico")

    def tearDown(self):
        self._tmp.cleanup()

    def test_scan_reads_metadata_and_structure(self):
        project = scan_project(self.root)
        self.assertEqual(project.metadata["app"], "demo")
        self.assertEqual(project.metadata["publisher"], "Tesla-Inc")
        self.assertEqual(project.scripts, ["demo.py"])
        self.assertEqual(project.entry, "demo.py")
        self.assertFalse(project.missing)
        self.assertTrue(project.icon.endswith("demo-icon.ico"))

    def test_scan_reports_missing_structure(self):
        (self.root / "config" / "settings.json").unlink()
        project = scan_project(self.root)
        self.assertIn("config/settings.json", project.missing)

    def test_scan_rejects_non_directory(self):
        with self.assertRaises(FileNotFoundError):
            scan_project(self.root / "no-existe")

    def test_find_scripts_falls_back_to_root_files(self):
        (self.root / "config" / "settings.json").unlink()
        (self.root / "otro.py").write_text("print(1)\n", encoding="utf-8")
        (self.root / "updater.py").write_text("print(1)\n", encoding="utf-8")
        scripts = find_scripts(self.root)
        self.assertIn("demo.py", scripts)
        self.assertIn("otro.py", scripts)
        self.assertNotIn("updater.py", scripts)

    def test_find_scripts_tolerates_non_object_build_settings(self):
        for build in ([], "texto", None, 5):
            with self.subTest(build=build):
                (self.root / "config" / "settings.json").write_text(
                    json.dumps({"build": build}), encoding="utf-8"
                )
                scripts = find_scripts(self.root)
                self.assertIn("demo.py", scripts)
                project = scan_project(self.root)
                self.assertEqual(project.scripts, ["demo.py"])

    def test_detect_hidden_imports(self):
        imports = detect_hidden_imports(self.root / "demo.py")
        self.assertIn("os", imports)
        self.assertIn("json", imports)

    def test_as_dict_is_json_serialisable(self):
        payload = json.dumps(scan_project(self.root).as_dict())
        self.assertIn("demo", payload)


class IdeCompileTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "proyecto"
        self.root.mkdir(parents=True)
        (self.root / "demo.py").write_text("def main():\n    print('ok')\n\nmain()\n", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_compile_with_zipapp_produces_artifact(self):
        outcome = compile_project(self.root, backend="zipapp", output_dir=self.root / "dist")
        self.assertEqual(outcome.backend, "zipapp")
        self.assertTrue(outcome.ok, outcome.failures)
        self.assertTrue(Path(outcome.outputs[0]).is_file())

    def test_compile_missing_script_fails(self):
        (self.root / "demo.py").unlink()
        outcome = compile_project(self.root, backend="zipapp", output_dir=self.root / "dist")
        self.assertFalse(outcome.ok)
        self.assertTrue(outcome.failures)


class IdeRunTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.script = Path(self._tmp.name) / "demo.py"
        self.script.write_text(MAIN, encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_run_script_captures_output(self):
        code, output = run_script(self.script)
        self.assertEqual(code, 0)
        self.assertIn("hola mundo", output)

    def test_run_script_reports_failure(self):
        (self.script).write_text("raise SystemExit(3)\n", encoding="utf-8")
        code, _ = run_script(self.script)
        self.assertEqual(code, 3)


class IdeDebugTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.script = Path(self._tmp.name) / "demo.py"
        self.script.write_text(MAIN, encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_trace_records_stops(self):
        stops = trace_script(self.script, max_stops=50)
        self.assertTrue(stops)
        self.assertTrue(all(stop.line > 0 for stop in stops))

    def test_breakpoint_limits_stops_to_that_line(self):
        stops = trace_script(self.script, breakpoints=[6], max_stops=50)
        self.assertTrue(stops)
        self.assertTrue(all(stop.line == 6 for stop in stops))

    def test_debug_script_surfaces_syntax_error(self):
        self.script.write_text("def :\n", encoding="utf-8")
        outcome = debug_script(self.script)
        self.assertFalse(outcome.ok)

    def test_debug_script_reports_runtime_error(self):
        self.script.write_text("def f():\n    return 1/0\n\nf()\n", encoding="utf-8")
        outcome = debug_script(self.script)
        self.assertFalse(outcome.ok)
        self.assertIn("ZeroDivisionError", outcome.error)

    def test_debug_script_reports_system_exit(self):
        self.script.write_text("raise SystemExit(3)\n", encoding="utf-8")
        outcome = debug_script(self.script)
        self.assertFalse(outcome.ok)
        self.assertIn("SystemExit", outcome.error)

    def test_debug_script_run_mode_captures_output(self):
        outcome = debug_script(self.script, run=True)
        self.assertTrue(outcome.ok)
        self.assertIn("hola mundo", outcome.output)


_UNREADABLE_SKIP = unittest.skipIf(
    os.name == "nt" or (hasattr(os, "geteuid") and os.geteuid() == 0),
    "los permisos POSIX no bloquean la lectura en Windows ni como root",
)


class IdeUnreadablePathTests(unittest.TestCase):
    """Un proyecto con rutas bloqueadas debe poder escanearse igual (R-7b4e2c19)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "proyecto"
        (self.root / "config").mkdir(parents=True)
        (self.root / "app").mkdir()
        (self.root / "details.xml").write_text(DETAILS, encoding="utf-8")
        (self.root / "config" / "settings.json").write_text(
            json.dumps(SETTINGS), encoding="utf-8"
        )
        (self.root / "demo.py").write_text(MAIN, encoding="utf-8")
        (self.root / "app" / "demo-icon.ico").write_bytes(b"ico")

    def tearDown(self):
        for path in (
            self.root / "app",
            self.root / "config",
            self.root / "details.xml",
            self.root,
        ):
            try:
                path.chmod(0o755)
            except OSError:
                pass
        self._tmp.cleanup()

    @_UNREADABLE_SKIP
    def test_scan_tolerates_unreadable_details_xml(self):
        (self.root / "details.xml").chmod(0o000)
        project = scan_project(self.root)
        self.assertEqual(project.metadata, {})
        self.assertIn("demo.py", project.scripts)
        self.assertEqual(project.entry, "demo.py")

    @_UNREADABLE_SKIP
    def test_scan_tolerates_unreadable_config_directory(self):
        (self.root / "config").chmod(0o000)
        project = scan_project(self.root)
        self.assertIn("demo.py", project.scripts)
        self.assertIn("config/settings.json", project.missing)

    @_UNREADABLE_SKIP
    def test_scan_tolerates_unreadable_app_directory(self):
        (self.root / "app").chmod(0o000)
        project = scan_project(self.root)
        self.assertIsNone(project.icon)
        self.assertEqual(project.metadata["app"], "demo")


if __name__ == "__main__":
    unittest.main()
