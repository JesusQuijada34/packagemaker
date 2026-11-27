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


class CompileOnlySourceRemovalTests(unittest.TestCase):
    """Q-004/F-001: `compile-only` no deja fuentes legibles en el paquete.

    El `.pyc` O2 se escribe en la ubicación clásica (junto al `.py`), que Python
    importa sin fuente. La única excepción son los builds `zipapp`, que
    empaquetan módulos `.py` por definición, y el `updater.py` obligatorio del
    contrato de estructura del paquete.
    """

    def _package(self, tmp: str) -> Path:
        root = Path(tmp)
        (root / "app.py").write_text("print('hola')\n", encoding="utf-8")
        (root / "helpers").mkdir()
        (root / "helpers" / "mod.py").write_text("VALUE = 1\n", encoding="utf-8")
        (root / "updater.py").write_text("print('updater')\n", encoding="utf-8")
        return root

    def test_compile_to_bytecode_removes_the_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "app.py"
            script.write_text("print('hola')\n", encoding="utf-8")
            report = hardening.compile_to_bytecode(script)
            self.assertTrue(report.applied, report.detail)
            self.assertFalse(script.exists())
            self.assertTrue(Path(report.artifacts[0]).is_file())

    def test_compile_to_bytecode_can_keep_the_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "app.py"
            script.write_text("print('hola')\n", encoding="utf-8")
            report = hardening.compile_to_bytecode(script, remove_source=False)
            self.assertTrue(report.applied, report.detail)
            self.assertTrue(script.is_file())
            self.assertTrue(Path(report.artifacts[0]).is_file())

    def test_apply_all_removes_project_sources_but_keeps_updater(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._package(tmp)
            reports = hardening.apply_all(package_dir=root, methods=["compile-only"])
            self.assertTrue(reports[0].applied, reports[0].detail)
            self.assertFalse((root / "app.py").exists())
            self.assertFalse((root / "helpers" / "mod.py").exists())
            self.assertTrue((root / "app.pyc").is_file())
            self.assertTrue((root / "helpers" / "mod.pyc").is_file())
            self.assertTrue((root / "updater.py").is_file())

    def test_apply_all_keeps_sources_for_zipapp_builds(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._package(tmp)
            reports = hardening.apply_all(
                package_dir=root, methods=["compile-only"], remove_source=False
            )
            self.assertTrue(reports[0].applied, reports[0].detail)
            self.assertTrue((root / "app.py").is_file())
            self.assertTrue((root / "helpers" / "mod.py").is_file())

    def test_apply_hardening_keeps_sources_when_the_backend_is_zipapp(self):
        import types

        from lib.blindcubeEngine.BuildThread import FlangCompiler

        with tempfile.TemporaryDirectory() as tmp:
            root = self._package(tmp)
            thread = FlangCompiler(
                Path(tmp) / "repo",
                output_path=Path(tmp) / "out",
                sandbox=False,
                hardening=["compile-only"],
            )
            thread._backend = types.SimpleNamespace(name="zipapp")
            thread.apply_hardening(root)
            self.assertTrue((root / "app.py").is_file())

    def test_apply_hardening_removes_sources_for_native_backends(self):
        import types

        from lib.blindcubeEngine.BuildThread import FlangCompiler

        with tempfile.TemporaryDirectory() as tmp:
            root = self._package(tmp)
            thread = FlangCompiler(
                Path(tmp) / "repo",
                output_path=Path(tmp) / "out",
                sandbox=False,
                hardening=["compile-only"],
            )
            thread._backend = types.SimpleNamespace(name="nuitka")
            thread.apply_hardening(root)
            self.assertFalse((root / "app.py").exists())
            self.assertTrue((root / "app.pyc").is_file())
            self.assertTrue((root / "updater.py").is_file())

    def test_digest_manifests_describe_the_tree_after_compile_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._package(tmp)
            reports = hardening.apply_all(
                package_dir=root, methods=hardening.method_names()
            )
            self.assertEqual([report.method for report in reports], hardening.method_names())

            integrity = json.loads((root / ".iflapp.integrity").read_text(encoding="utf-8"))
            integrity_paths = {entry["path"] for entry in integrity["files"]}
            self.assertNotIn("app.py", integrity_paths)
            self.assertIn("app.pyc", integrity_paths)
            self.assertIn("updater.py", integrity_paths)

            checksum_path = root.with_suffix(root.suffix + ".manifest.json")
            checksum = json.loads(checksum_path.read_text(encoding="utf-8"))
            checksum_paths = {entry["path"] for entry in checksum["files"]}
            self.assertNotIn("app.py", checksum_paths)
            self.assertIn("app.pyc", checksum_paths)
