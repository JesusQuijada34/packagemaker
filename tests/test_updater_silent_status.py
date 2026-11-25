# -*- coding: utf-8 -*-
"""El updater silencioso debe informar del resultado real de la instalación.

``updater.py --install <paquete> --silent`` imprimía ``OK: Instalación
completada`` y salía con código 0 aunque el ``.iflapp`` estuviera corrupto: el
worker capturaba la excepción, emitía ``finished(False, ...)`` y nadie leía ese
resultado. Lo mismo ocurría con los setup ``.exe`` en modo silencioso.
"""
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PyQt6.QtCore import QCoreApplication
except ImportError:  # pragma: no cover
    QCoreApplication = None


def _ensure_app():
    """Los ``QObject`` con señales necesitan una ``QCoreApplication`` viva."""
    if QCoreApplication is None:
        raise unittest.SkipTest("PyQt6 no disponible")
    return QCoreApplication.instance() or QCoreApplication([])


class IflappInstallStatusTests(unittest.TestCase):
    def setUp(self):
        self._app = _ensure_app()
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base = Path(self._tmp.name)

    def test_corrupt_package_is_reported_as_failure(self):
        from lib.coreUpdater.installer import install_iflapp

        broken = self.base / "broken.iflapp"
        broken.write_bytes(b"NOTAZIP")

        ok, message = install_iflapp(
            str(broken), str(self.base / "target"), silent=True
        )

        self.assertFalse(ok, "un paquete ilegible no puede darse por instalado")
        self.assertTrue(message)
        self.assertIn("zip", message.lower())

    def test_missing_package_is_reported_as_failure(self):
        from lib.coreUpdater.installer import install_iflapp

        ok, message = install_iflapp(
            str(self.base / "nope.iflapp"), str(self.base / "target"), silent=True
        )

        self.assertFalse(ok)
        self.assertIn("no encontrado", message.lower())

    def test_valid_legacy_zip_still_installs(self):
        from lib.coreUpdater.installer import install_iflapp

        package = self.base / "good.iflapp"
        with zipfile.ZipFile(package, "w") as zf:
            zf.writestr("details.xml", "<package><app>demo</app></package>")
            zf.writestr("app/main.py", "print('hi')\n")

        target = self.base / "target"
        ok, message = install_iflapp(str(package), str(target), silent=True)

        self.assertTrue(ok, message)
        self.assertTrue((target / "details.xml").is_file())
        self.assertTrue((target / "app" / "main.py").is_file())

    def test_worker_run_returns_false_and_keeps_the_error(self):
        from lib.coreUpdater.workers import IFLAPPInstallerWorker

        broken = self.base / "broken.iflapp"
        broken.write_bytes(b"NOTAZIP")
        worker = IFLAPPInstallerWorker(str(broken), str(self.base / "target"))

        self.assertIs(worker.run(), False)
        self.assertTrue(worker.error)


if __name__ == "__main__":
    unittest.main()
