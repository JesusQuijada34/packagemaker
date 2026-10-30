import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
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

    def test_qemu_not_advertised_without_guest_assets(self):
        """Sin kernel/initrd no se puede arrancar un huésped: no debe anunciarse."""
        from lib import hardware_sandbox

        with patch.object(hardware_sandbox, "_qemu_guest_assets", return_value=None), \
                patch.object(hardware_sandbox.shutil, "which", return_value="/usr/bin/qemu-system-x86_64"), \
                patch.object(hardware_sandbox.Path, "exists", return_value=True), \
                patch.object(hardware_sandbox.os, "access", return_value=True):
            capabilities = hardware_sandbox.detect_capabilities()
        self.assertFalse(capabilities.backends["qemu-kvm"])

    def test_qemu_command_uses_kvm_and_shares_workspace(self):
        from lib import hardware_sandbox

        sandbox = HardwareSandbox(backend="qemu-kvm")
        sandbox.capabilities.cpu_count = 2
        with patch.object(hardware_sandbox, "_qemu_guest_assets", return_value=("/boot/vmlinuz", "/boot/initrd.img")):
            command = sandbox._qemu_command(["/usr/bin/python", "x.py"], Path("/tmp/ws"))
        self.assertEqual(command[0], "qemu-system-x86_64")
        self.assertIn("-enable-kvm", command)
        self.assertIn("-kernel", command)
        joined = " ".join(command)
        self.assertIn("mount_tag=workspace", joined)

    def test_qemu_without_assets_returns_error_result(self):
        from lib import hardware_sandbox

        sandbox = HardwareSandbox(backend="qemu-kvm")
        with patch.object(hardware_sandbox, "_qemu_guest_assets", return_value=None):
            result = sandbox.run([sys.executable, "-c", "print(1)"], Path("/tmp"))
        self.assertEqual(result.returncode, 127)
        self.assertIn("kernel/initrd", result.stderr)


class SandboxVerificationTests(unittest.TestCase):
    def test_verify_in_sandbox_exposes_lib_on_pythonpath(self):
        """El script aislado importa ``lib``; el entorno debe exponer el repo."""
        from lib.BuildThread import FlangCompiler
        from lib import iflapp_format

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "proj"
            (project / "app").mkdir(parents=True)
            (project / "app" / "app-icon.ico").write_bytes(b"\x00\x00\x01\x00" + b"i" * 32)
            (project / "details.xml").write_text("<app><name>demo</name></app>", encoding="utf-8")
            (project / "main.py").write_text("print('x')", encoding="utf-8")
            releases = root / "releases"
            compiler = FlangCompiler(project, output_path=releases, log_callback=lambda _m: None)
            package = releases / "demo.iflapp"
            iflapp_format.pack_iflapp(project, package, identity={"app": "demo"})
            self.assertTrue(compiler.verify_in_sandbox(package))


if __name__ == "__main__":
    unittest.main()
