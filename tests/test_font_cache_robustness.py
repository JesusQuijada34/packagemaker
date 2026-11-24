"""Regresión R-3b6f9d24: una caché de fuentes no escribible no tumba nada.

``data/fonts`` se creaba con ``mkdir()`` dentro de ``cached_path()``, así que
una instalación de solo lectura (``Program Files`` en Windows, ``/usr`` en
Linux, ``data`` sin permisos) hacía que ``--list-fonts`` y ``--download-fonts``
terminaran en traceback y que la descarga desde Configuración abortara la
aplicación al lanzar ``PermissionError`` dentro de un slot de Qt.
"""

from __future__ import annotations

import pytest

from lib import font_manager
from lib.cliHandler import FontReportHelper


def _use_install_root(monkeypatch, root):
    """Apunta la raíz de instalación a ``root`` sin depender de ``__file__`` real."""
    (root / "lib").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(font_manager, "__file__", str(root / "lib" / "font_manager.py"))


@pytest.fixture
def read_only_root(tmp_path, monkeypatch):
    """Raíz donde ``data`` es un archivo: ``data/fonts`` nunca se puede crear."""
    root = tmp_path / "install"
    root.mkdir()
    (root / "data").write_text("no es una carpeta", encoding="utf-8")
    _use_install_root(monkeypatch, root)
    return root


@pytest.fixture
def offline(monkeypatch):
    def fail(*_args, **_kwargs):
        raise AssertionError("no se debe intentar descargar sin caché escribible")

    monkeypatch.setattr(font_manager, "_fetch", fail)


def test_reads_do_not_create_the_cache_directory(tmp_path, monkeypatch):
    root = tmp_path / "install"
    _use_install_root(monkeypatch, root)

    assert not font_manager.font_cache_dir(create=False).exists()
    assert not font_manager.cached_path("inter", create=False).parent.exists()
    assert not (root / "data" / "fonts").exists()


def test_unwritable_cache_reports_fonts_as_absent(read_only_root):
    assert font_manager.is_cached("inter") is False

    report = font_manager.available_fonts_report()

    assert set(report) == set(font_manager.FONT_REGISTRY)
    assert all(info["cached"] is False for info in report.values())
    assert all(info["path"] is None for info in report.values())


def test_ensure_fonts_degrades_to_none(read_only_root):
    assert font_manager.ensure_fonts(["inter", "roboto"], download=False) == {
        "inter": None,
        "roboto": None,
    }


def test_download_font_skips_the_network_when_cache_is_unwritable(read_only_root, offline):
    assert font_manager.download_font("inter") is None


def test_license_notice_and_qt_registration_degrade(read_only_root):
    assert font_manager.write_license_notice() is None
    assert isinstance(font_manager.load_cached_fonts(), dict)


def test_license_notice_is_still_written_in_a_writable_cache(tmp_path, monkeypatch):
    _use_install_root(monkeypatch, tmp_path / "install")

    notice = font_manager.write_license_notice()

    assert notice is not None
    assert notice.is_file()
    assert "Roboto" in notice.read_text(encoding="utf-8")


def test_cli_list_fonts_survives_read_only_cache(read_only_root, capsys):
    assert FontReportHelper.report() is True

    output = capsys.readouterr().out
    assert "AUSENTE" in output


def test_cli_download_fonts_reports_unwritable_cache(read_only_root, offline, capsys):
    assert FontReportHelper.download({"keys": "inter"}) is False

    output = capsys.readouterr().out
    assert "no se pudieron obtener: inter" in output.lower()
    assert "Traceback" not in output


def test_settings_font_download_slot_does_not_abort(read_only_root, offline, capsys):
    import packagemaker

    class _Status:
        def __init__(self):
            self.text = ""

        def setText(self, text):
            self.text = text

    class _Panel:
        conf_fonts_status = _Status()
        conf_fonts_labels = {}

    panel = _Panel()
    packagemaker.PackageTodoGUI._download_ui_fonts(panel)

    assert panel.conf_fonts_status.text
    assert "Traceback" not in capsys.readouterr().err
