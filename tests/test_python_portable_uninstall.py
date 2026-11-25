# -*- coding: utf-8 -*-
"""Desinstalar un Python portable no puede mentir ni romper la GUI.

``PythonPortableManager.uninstall_version`` usaba
``shutil.rmtree(..., ignore_errors=True)``: devolvía ``True`` ("Python X
desinstalado") aunque la carpeta siguiera en disco, y borraba el registro de la
instalación, que volvía a aparecer en el siguiente descubrimiento. Además
``Path.exists()`` propagaba ``PermissionError`` desde un slot de Qt.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.python_portable_manager import PythonPortableManager

_POSIX_ONLY = unittest.skipIf(
    os.name == "nt" or (hasattr(os, "geteuid") and os.geteuid() == 0),
    "los permisos POSIX no bloquean la lectura en Windows ni como root",
)


class UninstallVersionTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.manager = PythonPortableManager(base_dir=Path(self._tmp.name))
        self.folder = self.manager.python_dir / "python312"
        self.folder.mkdir(parents=True, exist_ok=True)
        (self.folder / "python.exe").write_bytes(b"x")
        self.manager._discover_installations()
        self.assertIn("3.12", self.manager.installations)
        self.addCleanup(self._restore, self.manager.python_dir)

    @staticmethod
    def _restore(path: Path, mode: int = 0o755) -> None:
        try:
            path.chmod(mode)
        except OSError:
            pass

    def test_removes_the_tree_and_the_record(self):
        self.assertTrue(self.manager.uninstall_version("3.12"))
        self.assertFalse(self.folder.exists())
        self.assertNotIn("3.12", self.manager.installations)

    def test_unknown_version_returns_false(self):
        self.assertFalse(self.manager.uninstall_version("9.9"))

    @_POSIX_ONLY
    def test_blocked_tree_reports_failure_and_keeps_the_record(self):
        os.chmod(self.manager.python_dir, 0o500)
        try:
            self.assertFalse(self.manager.uninstall_version("3.12"))
        finally:
            self._restore(self.manager.python_dir)

        self.assertTrue(self.folder.exists())
        self.assertIn("3.12", self.manager.installations)

    @_POSIX_ONLY
    def test_unreadable_parent_does_not_raise(self):
        os.chmod(self.manager.python_dir, 0o000)
        try:
            self.assertFalse(self.manager.uninstall_version("3.12"))
        finally:
            self._restore(self.manager.python_dir)

        self.assertIn("3.12", self.manager.installations)


if __name__ == "__main__":
    unittest.main()
