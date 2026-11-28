# -*- coding: utf-8 -*-
"""Q-029: los campos de AIDE viven también en Configuración.

La página AIDE guardaba proveedor, endpoint, modelo y clave en su propia barra.
El propietario los pidió en Configuración, así que la tarjeta nueva y la página
comparten el mismo almacén (``aide_backend.save_settings``). Estas pruebas usan
la ventana real y comprueban que no hay dos fuentes de verdad ni fugas de la
clave hacia un widget.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

pytest.importorskip("PyQt6.QtWidgets")

from PyQt6.QtWidgets import QApplication, QLineEdit  # noqa: E402

import lib.i18n as i18n  # noqa: E402
from lib import pm_data  # noqa: E402

_APP = None


def _ensure_app():
    global _APP
    if _APP is None:
        _APP = QApplication.instance() or QApplication(sys.argv)
    return _APP


@pytest.fixture(scope="session")
def qt_app():
    app = _ensure_app()
    i18n.i18n.initialize(app, "es")
    return app


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr(pm_data, "_data_dir", lambda: tmp_path)
    store = pm_data.PMDataStore(path=tmp_path / "pm.data")
    monkeypatch.setattr(pm_data, "_store", store)
    return store


@pytest.fixture()
def window(qt_app, isolated_store):
    import packagemaker as pm

    win = pm.PackageTodoGUI()
    yield win
    win.close()
    qt_app.processEvents()


def test_settings_card_exposes_the_aide_fields(window):
    panel = window.settings_panel
    assert "aide" in panel._cards
    for name in (
        "conf_aide_provider",
        "conf_aide_endpoint",
        "conf_aide_model",
        "conf_aide_key",
        "conf_aide_send_context",
    ):
        assert name in panel.widgets, f"falta el control {name}"
    assert panel._cards["aide"].subtitle_lbl.text()


def test_card_is_between_privacy_and_addons(window):
    keys = list(window.settings_panel._cards)
    assert keys.index("privacy") < keys.index("aide") < keys.index("addons")


def test_editing_the_endpoint_saves_it(window, isolated_store):
    from lib import aide_backend

    panel = window.settings_panel
    panel._aide_endpoint.setText("https://api.example.com/v1")
    panel._on_aide_field_changed()
    assert aide_backend.get_settings()["endpoint"] == "https://api.example.com/v1"
    assert isolated_store.get_user("aide_endpoint") == "https://api.example.com/v1"


def test_typing_a_key_saves_it_and_never_shows_it(window):
    from lib import aide_backend

    panel = window.settings_panel
    panel._aide_key.setText("sk-secreta")
    panel._on_aide_field_changed()
    assert aide_backend.get_settings()["api_key"] == "sk-secreta"
    assert panel._aide_key.text() == ""
    assert panel._aide_key.echoMode() == QLineEdit.EchoMode.Password
    assert "guardada" in panel._aide_key.placeholderText().lower()


def test_provider_and_context_are_saved(window):
    from lib import aide_backend

    panel = window.settings_panel
    panel._aide_provider.setCurrentIndex(panel._aide_provider.findData("openai"))
    assert aide_backend.get_settings()["provider"] == "openai"
    panel._aide_context.setChecked(True)
    assert aide_backend.get_settings()["send_context"] is True


def test_card_emits_the_shared_settings_signal(window):
    panel = window.settings_panel
    received = []
    panel.aideSettingsChanged.connect(lambda: received.append(True))
    panel._aide_endpoint.setText("https://otro.example.com")
    panel._on_aide_field_changed()
    assert received, "la página AIDE no se enteraría del cambio"


def test_page_picks_up_what_the_card_saved(window):
    from lib import aide_backend

    panel = window.settings_panel
    page = window.page_aide
    panel._aide_endpoint.setText("https://config.example.com/v1")
    panel._aide_model.setText("modelo-config")
    panel._on_aide_field_changed()
    page.refresh_settings()
    assert page.endpoint_input.text() == "https://config.example.com/v1"
    assert page.model_input.text() == "modelo-config"
    assert aide_backend.get_settings()["endpoint"] == "https://config.example.com/v1"


def test_refresh_does_not_copy_the_stored_key_into_the_page(window):
    from lib import aide_backend

    aide_backend.save_settings(aide_api_key="sk-guardada")
    window.page_aide.refresh_settings()
    assert window.page_aide.key_input.text() == ""
    assert "guardada" in window.page_aide.key_input.placeholderText().lower()


def test_retranslate_keeps_the_aide_card_in_the_new_language(window):
    panel = window.settings_panel
    i18n.i18n.load_translation("en")
    try:
        panel.retranslate()
        assert "AIDE" in panel._cards["aide"].title_lbl.text()
        assert panel._aide_context.text() == i18n.tr("config.aide_send_context")
        assert panel._aide_provider.itemText(0) == i18n.tr("aide.provider_copilot")
    finally:
        i18n.i18n.load_translation("es")
        panel.retranslate()
