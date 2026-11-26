# -*- coding: utf-8 -*-
"""El updater silencioso con ``.iflapp`` no debe abrir ninguna ventana (Q-015).

``_update_from_iflapp`` ignoraba ``silent``: creaba una ``QApplication``, una
``ModernUpdaterWindow`` y bloqueaba en ``app.exec()``. En una máquina sin
pantalla la actualización desatendida no instalaba nada y aun así devolvía
``True``. El modo silencioso debe descargar el paquete, instalarlo con
``install_iflapp(..., silent=True)`` sobre el directorio actual y devolver el
resultado real.
"""
import sys
from pathlib import Path

import pytest

pytest.importorskip("PyQt6.QtWidgets")

from lib.coreUpdater import installer  # noqa: E402


def _forbid_qt(monkeypatch):
    def explode(*args, **kwargs):
        raise AssertionError("el modo silencioso no debe crear interfaces Qt")

    monkeypatch.setattr(installer, "QApplication", explode)
    monkeypatch.setattr(installer, "ModernUpdaterWindow", explode)


def test_silent_iflapp_update_installs_without_qt(monkeypatch, tmp_path):
    package = tmp_path / "update.iflapp"
    package.write_bytes(b"PK\x05\x06" + b"\x00" * 18)
    calls = {}

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        installer, "_download_iflapp_package", lambda url: str(package)
    )

    def fake_install(iflapp_path, target_dir=None, silent=False):
        calls.update(path=iflapp_path, target=target_dir, silent=silent)
        return True, "Instalación completada"

    monkeypatch.setattr(installer, "install_iflapp", fake_install)
    _forbid_qt(monkeypatch)

    ok = installer._update_from_iflapp(
        {"app": "Demo"}, "https://example.invalid/demo.iflapp", silent=True
    )

    assert ok is True
    assert calls == {
        "path": str(package),
        "target": str(tmp_path),
        "silent": True,
    }
    assert not package.exists(), "el paquete temporal debe borrarse al terminar"


def test_silent_iflapp_update_reports_install_failure(monkeypatch, tmp_path):
    package = tmp_path / "update.iflapp"
    package.write_bytes(b"PK\x05\x06" + b"\x00" * 18)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        installer, "_download_iflapp_package", lambda url: str(package)
    )
    monkeypatch.setattr(
        installer,
        "install_iflapp",
        lambda *a, **k: (False, "paquete corrupto"),
    )
    _forbid_qt(monkeypatch)

    ok = installer._update_from_iflapp(
        {"app": "Demo"}, "https://example.invalid/demo.iflapp", silent=True
    )

    assert ok is False
    assert not package.exists()


def test_silent_iflapp_update_reports_download_failure(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    def broken_download(url):
        raise OSError("sin red")

    monkeypatch.setattr(installer, "_download_iflapp_package", broken_download)
    monkeypatch.setattr(
        installer,
        "install_iflapp",
        lambda *a, **k: (_ for _ in ()).throw(
            AssertionError("no se debe instalar sin descargar")
        ),
    )
    _forbid_qt(monkeypatch)

    ok = installer._update_from_iflapp(
        {"app": "Demo"}, "https://example.invalid/demo.iflapp", silent=True
    )

    assert ok is False


def test_graphical_iflapp_update_still_opens_the_window(monkeypatch, tmp_path):
    created = {}

    class FakeApp:
        def __init__(self, argv):
            created["app"] = argv

        def exec(self):
            return 0

    class FakeWindow:
        def __init__(self, app_data, url):
            created["window"] = url

        def show(self):
            created["shown"] = True

    monkeypatch.setattr(installer, "QApplication", FakeApp)
    monkeypatch.setattr(installer, "ModernUpdaterWindow", FakeWindow)
    monkeypatch.setattr(installer, "HAS_LEVIATHAN", False)

    ok = installer._update_from_iflapp(
        {"app": "Demo"}, "https://example.invalid/demo.iflapp", silent=False
    )

    assert ok is True
    assert created["window"] == "https://example.invalid/demo.iflapp"
    assert created["shown"] is True


def test_download_helper_writes_the_remote_package(monkeypatch, tmp_path):
    payload = b"contenido del paquete"

    class FakeResponse:
        def __init__(self):
            self._done = False

        def read(self, size=-1):
            if self._done:
                return b""
            self._done = True
            return payload

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    monkeypatch.setattr(
        installer.urllib.request, "urlopen", lambda url, timeout=60: FakeResponse()
    )

    path = installer._download_iflapp_package(
        "https://example.invalid/demo.iflapp", dest_dir=str(tmp_path)
    )

    assert Path(path).parent == tmp_path
    assert Path(path).suffix == ".iflapp"
    assert Path(path).read_bytes() == payload


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
