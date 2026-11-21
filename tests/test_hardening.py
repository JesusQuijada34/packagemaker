import subprocess
import sys
import json
import tempfile
import unittest
from pathlib import Path

from lib.blindcubeEngine import hardening


class HardeningTests(unittest.TestCase):
    def test_method_names_and_availability(self):
        self.assertEqual(
            hardening.method_names(),
            [
                "strip",
                "upx",
                "checksum",
                "anti-debug",
                "obfuscate",
                "resource",
                "sign",
                "integrity",
                "compile-only",
                "rename-symbols",
            ],
        )
        status = hardening.available_methods()
        self.assertTrue(status["checksum"])
        self.assertTrue(status["anti-debug"])
        self.assertTrue(status["obfuscate"])
        self.assertTrue(status["sign"])
        self.assertTrue(status["integrity"])
        self.assertTrue(status["compile-only"])

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


class NewHardeningMethodTests(unittest.TestCase):
    def test_sign_writes_a_verifiable_seal(self):
        import hashlib
        import hmac

        with tempfile.TemporaryDirectory() as tmp:
            binary = Path(tmp) / "demo.bin"
            binary.write_bytes(b"\x7fELF" + b"\x00" * 64)
            report = hardening.sign_binary(binary)
            self.assertTrue(report.applied, report.detail)
            seal = json.loads(Path(report.artifacts[0]).read_text(encoding="utf-8"))
            expected = hmac.new(
                b"influent-hardening-signature", binary.read_bytes(), hashlib.sha256
            ).hexdigest()
            self.assertEqual(seal["hmac_sha256"], expected)

    def test_integrity_manifest_records_a_merkle_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text("uno", encoding="utf-8")
            (root / "b.txt").write_text("dos", encoding="utf-8")
            report = hardening.embed_integrity_manifest(root)
            self.assertTrue(report.applied, report.detail)
            manifest = json.loads((root / ".iflapp.integrity").read_text(encoding="utf-8"))
            self.assertEqual(manifest["count"], 2)
            self.assertEqual(len(manifest["root_sha256"]), 64)

    def test_compile_only_emits_optimized_bytecode(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "app.py"
            script.write_text("print('hola')\n", encoding="utf-8")
            report = hardening.compile_to_bytecode(script)
            self.assertTrue(report.applied, report.detail)
            self.assertTrue(Path(report.artifacts[0]).is_file())


class ObfuscateRobustnessTests(unittest.TestCase):
    SCRIPT = '''"""Docstring del modulo con "una cita larga" dentro."""
from typing import Literal

name = "mundo"
mensaje = ("parte uno " "parte dos")
print(f"Hola {name}")
print(mensaje)


def saluda(valor="valor por defecto"):
    """Docstring de la funcion con "comillas" largas."""
    return valor


print(saluda())
clave = "alfa"
match clave:
    case "alfabeto largo":
        print("patron")
    case _:
        print("otro")
anotado: Literal["literal largo"] = "literal largo"
print(anotado)
'''

    def test_obfuscate_keeps_valid_python_for_concatenation_and_fstrings(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "app.py"
            script.write_text(self.SCRIPT, encoding="utf-8")
            expected = subprocess.run(
                [sys.executable, str(script)], capture_output=True, text=True
            )
            self.assertEqual(expected.returncode, 0, expected.stderr)

            report = hardening.obfuscate_strings(script)
            self.assertTrue(report.applied, report.detail)
            result = subprocess.run(
                [sys.executable, str(script)], capture_output=True, text=True
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, expected.stdout)

    def test_obfuscate_skips_docstrings_fstrings_patterns_and_literal_annotations(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "app.py"
            script.write_text(self.SCRIPT, encoding="utf-8")
            hardening.obfuscate_strings(script)
            text = script.read_text(encoding="utf-8")
            self.assertIn('"""Docstring del modulo con "una cita larga" dentro."""', text)
            self.assertIn('"""Docstring de la funcion con "comillas" largas."""', text)
            self.assertIn('print(f"Hola {name}")', text)
            self.assertIn('case "alfabeto largo":', text)
            self.assertIn('Literal["literal largo"]', text)
            self.assertIn("b64decode", text)

    def test_obfuscate_refuses_unparsable_source_without_touching_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "app.py"
            broken = "print('sin cerrar'\n"
            script.write_text(broken, encoding="utf-8")
            report = hardening.obfuscate_strings(script)
            self.assertFalse(report.applied)
            self.assertEqual(script.read_text(encoding="utf-8"), broken)
