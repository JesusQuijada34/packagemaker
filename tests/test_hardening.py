import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from lib import hardening


class HardeningTests(unittest.TestCase):
    def test_method_names_and_availability(self):
        self.assertEqual(
            hardening.method_names(),
            ["strip", "upx", "checksum", "anti-debug", "obfuscate", "resource"],
        )
        status = hardening.available_methods()
        self.assertTrue(status["checksum"])
        self.assertTrue(status["anti-debug"])
        self.assertTrue(status["obfuscate"])

    def test_checksum_manifest_is_written_and_stable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text("alpha", encoding="utf-8")
            (root / "b.txt").write_text("beta", encoding="utf-8")
            report = hardening.write_checksum_manifest(root)
            self.assertTrue(report.applied)
            manifest = Path(report.artifacts[0])
            self.assertTrue(manifest.is_file())
            first = manifest.read_text(encoding="utf-8")
            hardening.write_checksum_manifest(root)
            self.assertEqual(first, manifest.read_text(encoding="utf-8"))

    def test_anti_debug_guard_is_idempotent_and_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "app.py"
            script.write_text("print('guarded')\n", encoding="utf-8")
            self.assertTrue(hardening.inject_anti_debug(script).applied)
            second = hardening.inject_anti_debug(script)
            self.assertTrue(second.applied)
            self.assertEqual(script.read_text(encoding="utf-8").count("_iflapp_guard()"), 2)
            result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("guarded", result.stdout)

    def test_obfuscate_preserves_semantics(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "app.py"
            script.write_text("VALUE = 'a-very-long-secret-value'\nprint(VALUE)\n", encoding="utf-8")
            report = hardening.obfuscate_strings(script)
            self.assertTrue(report.applied)
            self.assertIn("b64decode", script.read_text(encoding="utf-8"))
            result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("a-very-long-secret-value", result.stdout)

    def test_apply_all_never_raises_on_missing_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            reports = hardening.apply_all(package_dir=Path(tmp), methods=hardening.method_names())
            self.assertEqual(len(reports), len(hardening.method_names()))
            self.assertTrue(all(isinstance(r.applied, bool) for r in reports))

    def test_strip_reports_missing_tool_or_binary(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = hardening.strip_binary(Path(tmp) / "missing")
            self.assertFalse(report.applied)


if __name__ == "__main__":
    unittest.main()
