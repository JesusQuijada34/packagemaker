import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from lib import iflapp_format
from lib.dropper import create_dropper, read_dropper_header
from lib.hardware_sandbox import HardwareSandbox
from lib import compilers


def _make_package(root: Path, *, password=None) -> Path:
    package = root / "pkg"
    package.mkdir(parents=True)
    (package / "details.xml").write_text("<app><app>demo</app></app>", encoding="utf-8")
    script = package / "demo.py"
    script.write_text("import sys\nprint('dropper-ok')\nsys.exit(0)\n", encoding="utf-8")
    out = root / "demo.iflapp"
    iflapp_format.pack_iflapp(package, out, identity={"app": "demo"}, password=password)
    return out


class DropperTests(unittest.TestCase):
    def test_dropper_is_valid_python_and_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = _make_package(root)
            dropper = create_dropper(package, root / "demo.run")
            self.assertTrue(dropper.is_file())
            header = read_dropper_header(dropper)
            self.assertEqual(header.identity()["app"], "demo")
            result = subprocess.run(
                [sys.executable, str(dropper), "--keep"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("dropper-ok", result.stdout)

    def test_dropper_with_encrypted_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = _make_package(root, password="pw")
            dropper = create_dropper(package, root / "demo.run")
            result = subprocess.run(
                [sys.executable, str(dropper), "--password", "pw", "--keep"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)


class CompilerBackendTests(unittest.TestCase):
    def test_available_backends_reports_expected_names(self):
        report = compilers.available_backends()
        self.assertIn("nuitka", report)
        self.assertIn("pyinstaller", report)
        self.assertTrue(all("available" in info for info in report.values()))

    def test_unknown_backend_raises(self):
        with self.assertRaises(compilers.CompilerUnavailableError):
            compilers.get_backend("does-not-exist")


class HardwareSandboxTests(unittest.TestCase):
    def test_sandbox_selects_a_backend_and_runs(self):
        sandbox = HardwareSandbox()
        info = sandbox.describe()
        self.assertIn("selected", info)
        self.assertIn("backends", info)
        with tempfile.TemporaryDirectory() as tmp:
            workspace = sandbox.prepare_workspace(Path(tmp), writable=True)
            try:
                result = sandbox.run([sys.executable, "-c", "print('sandbox-ok')"], workspace)
                self.assertIn("sandbox-ok", result.stdout)
            finally:
                sandbox.cleanup(workspace)


if __name__ == "__main__":
    unittest.main()
