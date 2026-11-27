# -*- coding: utf-8 -*-
"""Tarjeta «Extensiones» de Configuración (Q-022).

Cubre la segunda mitad de la aprobación: instalar un manifiesto ``.yaml`` del
sidebar desde la interfaz, con validación previa y sin tocar el directorio de
la aplicación.
"""

import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

pytest.importorskip("PyQt6.QtWidgets")

from PyQt6.QtWidgets import QApplication  # noqa: E402

import lib.i18n as i18n  # noqa: E402
from lib import settings_panel as settings_panel_module  # noqa: E402
from lib.settings_panel import SettingsPanel  # noqa: E402

_APP = None


def _ensure_app():
    """Qt aborta el proceso si la QApplication se recolecta a mitad de test."""
    global _APP
    if _APP is None:
        _APP = QApplication.instance() or QApplication(sys.argv)
    return _APP


@pytest.fixture(scope="session")
def qt_app():
    app = _ensure_app()
    i18n.i18n.initialize(app, "es")
    return app


class FakeHost:
    def build_extra_page(self):
        return None


@pytest.fixture()
def user_dir(tmp_path, monkeypatch):
    directory = tmp_path / "user-addons"
    monkeypatch.setenv("PM_USER_ADDONS_DIR", str(directory))
    return directory


@pytest.fixture()
def panel(qt_app, user_dir):
    widget = SettingsPanel(host=FakeHost(), user={})
    yield widget
    widget.deleteLater()
    qt_app.processEvents()


def _manifest(path: Path, body: str) -> Path:
    path.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")
    return path


VALID = """
id: extra
section: tools
order: 30
label: sidebar.extra
icon: help
builder: build_extra_page
"""


def _choose(monkeypatch, path):
    chosen = str(path) if isinstance(path, Path) else path
    monkeypatch.setattr(
        settings_panel_module.QFileDialog,
        "getOpenFileName",
        staticmethod(lambda *args, **kwargs: (chosen, "")),
    )


def test_card_is_registered(panel):
    assert "addons" in panel._cards
    assert panel._titles["addons"] == i18n.tr("config.section_addons")
    assert "conf_addons_install" in panel.widgets


def test_install_copies_the_manifest_and_updates_the_list(panel, monkeypatch, tmp_path, user_dir):
    _choose(monkeypatch, _manifest(tmp_path / "extra.yaml", VALID))
    panel._install_addon()
    assert (user_dir / "extra.yaml").is_file()
    assert "extra" in panel.widgets["conf_addons_list"].text()
    assert i18n.tr("config.addons_ok") in panel.widgets["conf_addons_status"].text()


def test_invalid_manifest_shows_the_reason_and_copies_nothing(
    panel, monkeypatch, tmp_path, user_dir
):
    source = _manifest(tmp_path / "config.yaml", VALID.replace("id: extra", "id: config"))
    _choose(monkeypatch, source)
    panel._install_addon()
    assert not user_dir.exists()
    status = panel.widgets["conf_addons_status"].text()
    assert i18n.tr("config.addons_error") in status
    assert "incluido" in status
    assert panel.widgets["conf_addons_list"].text() == i18n.tr("config.addons_none")


def test_cancelling_the_dialog_changes_nothing(panel, monkeypatch, user_dir):
    _choose(monkeypatch, "")
    panel._install_addon()
    assert not user_dir.exists()
    assert panel.widgets["conf_addons_status"].text() == ""
