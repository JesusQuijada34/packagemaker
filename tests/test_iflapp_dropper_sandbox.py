import base64
import subprocess
import sys
import tempfile
import unittest
import zipfile
from unittest.mock import patch
from pathlib import Path

from lib.blindcubeEngine import iflapp_format
from lib.blindcubeEngine.dropper import (
    DROPPER_END,
    DROPPER_MARKER,
    create_dropper,
    read_dropper_header,
)
from lib.blindcubeEngine.iflapp_format import IflappError
from lib.blindcubeEngine.hardware_sandbox import HardwareSandbox
from lib.blindcubeEngine import compilers


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

    def test_dropper_launches_generic_main_entrypoint(self):
        # Regresión: con un ``main.py`` (sin ``app`` en la cabecera) el stub no
        # encontraba punto de entrada y sólo imprimía la ruta de extracción.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = root / "pkg"
            package.mkdir(parents=True)
            (package / "details.xml").write_text("<app><name>Demo</name></app>", encoding="utf-8")
            (package / "main.py").write_text("print('main-entrypoint-ok')\n", encoding="utf-8")
            out = root / "demo.iflapp"
            iflapp_format.pack_iflapp(package, out)
            dropper = create_dropper(out, root / "demo.run")
            result = subprocess.run(
                [sys.executable, str(dropper)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("main-entrypoint-ok", result.stdout)

    def test_dropper_launches_zipapp_entrypoint(self):
        # Regresión: el backend zipapp produce ``<guion>.pyz``. El stub no lo
        # reconocía como punto de entrada y el respaldo lanzaba un guion
        # auxiliar del paquete (``updater.py``), que no es la aplicación.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = root / "pkg"
            package.mkdir(parents=True)
            (package / "details.xml").write_text("<app><app>demo</app></app>", encoding="utf-8")
            with zipfile.ZipFile(package / "demo.pyz", "w") as archive:
                archive.writestr("__main__.py", "print('zipapp-entrypoint-ok')\n")
            (package / "aaa_updater.py").write_text(
                "print('wrong-entrypoint')\n", encoding="utf-8"
            )
            out = root / "demo.iflapp"
            iflapp_format.pack_iflapp(package, out, identity={"app": "demo"})
            dropper = create_dropper(out, root / "demo.run")
            result = subprocess.run(
                [sys.executable, str(dropper)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("zipapp-entrypoint-ok", result.stdout)
            self.assertNotIn("wrong-entrypoint", result.stdout)

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

    @staticmethod
    def _replace_embedded_payload(dropper: Path, payload: bytes) -> Path:
        data = dropper.read_bytes()
        start = data.find(DROPPER_MARKER) + len(DROPPER_MARKER)
        end = data.find(DROPPER_END)
        encoded = base64.b64encode(payload).decode("ascii")
        lines = [("#" + encoded[i:i + 76]).encode("ascii") for i in range(0, len(encoded), 76)]
        corrupted = dropper.with_name(dropper.stem + "-corrupt.run")
        corrupted.write_bytes(data[:start] + b"\n".join(lines) + b"\n" + data[end:])
        return corrupted

    def test_corrupt_embedded_package_reports_clean_error(self):
        """Un ``.run`` con el ``.iflapp`` alterado no debe escupir un traceback."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = _make_package(root)
            dropper = create_dropper(package, root / "demo.run")
            corrupted = self._replace_embedded_payload(dropper, b"IFLAPP2\x00" + b"\xff" * 48)
            result = subprocess.run(
                [sys.executable, str(corrupted)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("Traceback", result.stderr)
            self.assertIn(".iflapp", result.stderr)

    def test_truncated_embedded_package_reports_clean_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = _make_package(root)
            dropper = create_dropper(package, root / "demo.run")
            corrupted = self._replace_embedded_payload(dropper, b"IFLAPP2\x00\x05\x00\x00\x00")
            result = subprocess.run(
                [sys.executable, str(corrupted)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("Traceback", result.stderr)
            self.assertIn("truncada", result.stderr)

    def test_password_without_value_reports_clean_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = _make_package(root)
            dropper = create_dropper(package, root / "demo.run")
            result = subprocess.run(
                [sys.executable, str(dropper), "--password"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("Traceback", result.stderr)
            self.assertIn("Falta el valor de --password", result.stderr)

    def test_read_dropper_header_rejects_corrupt_base64(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = _make_package(root)
            dropper = create_dropper(package, root / "demo.run")
            data = dropper.read_bytes()
            index = data.find(DROPPER_MARKER) + len(DROPPER_MARKER)
            broken = root / "broken.run"
            broken.write_bytes(data[:index] + b"#!!!!not-base64!!!!\n")
            with self.assertRaises(IflappError):
                read_dropper_header(broken)


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
        from lib.blindcubeEngine import hardware_sandbox

        with patch.object(hardware_sandbox, "_qemu_guest_assets", return_value=None), \
                patch.object(hardware_sandbox.shutil, "which", return_value="/usr/bin/qemu-system-x86_64"), \
                patch.object(hardware_sandbox.Path, "exists", return_value=True), \
                patch.object(hardware_sandbox.os, "access", return_value=True):
            capabilities = hardware_sandbox.detect_capabilities()
        self.assertFalse(capabilities.backends["qemu-kvm"])

    def test_qemu_command_uses_kvm_and_shares_workspace(self):
        from lib.blindcubeEngine import hardware_sandbox

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
        from lib.blindcubeEngine import hardware_sandbox

        sandbox = HardwareSandbox(backend="qemu-kvm")
        with patch.object(hardware_sandbox, "_qemu_guest_assets", return_value=None):
            result = sandbox.run([sys.executable, "-c", "print(1)"], Path("/tmp"))
        self.assertEqual(result.returncode, 127)
        self.assertIn("kernel/initrd", result.stderr)


class SandboxVerificationTests(unittest.TestCase):
    def test_verify_in_sandbox_exposes_lib_on_pythonpath(self):
        """El script aislado importa ``lib``; el entorno debe exponer el repo."""
        from lib.blindcubeEngine.BuildThread import FlangCompiler
        from lib.blindcubeEngine import iflapp_format

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
