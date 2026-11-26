# -*- coding: utf-8 -*-
"""Configuración: una sola barra de acciones y retroceso siempre con nombre.

Issue #14 (JesusQuijada34): la página de Configuración mostraba **dos** barras
—la de la página y la cabecera propia del panel— y, tras cualquier
retraducción, la flecha de retroceso de los detalles aparecía sin nombre porque
``SettingsPanel.retranslate()`` reconstruía los títulos con una lista fija que
no incluía la tarjeta de Privacidad.
"""

import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

pytest.importorskip("PyQt6.QtWidgets")

from PyQt6.QtWidgets import QApplication, QPushButton, QWidget  # noqa: E402

import lib.i18n as i18n  # noqa: E402
from lib import pm_data  # noqa: E402

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


def _pump(app, seconds=0.5):
    """Deja correr la animación de deslizamiento del navegador."""
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        app.processEvents()
        time.sleep(0.01)


def _config_page(window):
    return window.settings_panel.parentWidget()


def test_settings_page_has_a_single_action_bar(window):
    page = _config_page(window)
    bars = [
        child for child in page.findChildren(QWidget)
        if child.objectName() == "PageActionBar"
    ]
    assert len(bars) == 1
    assert bars[0] is window.config_action_bar
    # La cabecera duplicada del panel ya no existe.
    names = {child.objectName() for child in page.findChildren(QWidget)}
    assert "SettingsCapsule" not in names
    assert "SettingsHeader" not in names


def test_root_bar_shows_only_the_page_title(window):
    assert window.config_bar_title.text() == i18n.tr("sidebar.config")
    assert window.config_back_btn.isHidden()
    assert window.config_confirm_btn.isHidden()


def test_detail_sets_title_back_and_confirm(window):
    panel = window.settings_panel
    panel._open("privacy")
    assert window.config_bar_title.text() == i18n.tr("config.section_privacy")
    assert not window.config_back_btn.isHidden()
    assert i18n.tr("config.title") in window.config_back_btn.text()
    assert not window.config_confirm_btn.isHidden()
    assert window.config_confirm_btn.text() == i18n.tr("config.confirm")


def test_single_choice_detail_has_no_confirm_button(window):
    panel = window.settings_panel
    panel._open("language")
    assert window.config_bar_title.text() == i18n.tr("config.section_language")
    assert window.config_confirm_btn.isHidden()


def test_going_back_restores_the_root_bar(window):
    panel = window.settings_panel
    panel._open("privacy")
    _pump(QApplication.instance())
    window.config_back_btn.click()
    _pump(QApplication.instance())
    assert window.config_bar_title.text() == i18n.tr("config.title")
    assert window.config_back_btn.isHidden()
    assert window.config_confirm_btn.isHidden()
    assert panel.navigator.depth() == 0


def test_retranslate_keeps_every_card_title(window):
    """Regresión: Privacidad quedaba fuera de la lista fija de títulos."""
    panel = window.settings_panel
    panel.retranslate()
    assert "privacy" in panel._titles
    assert panel._titles["privacy"] == i18n.tr("config.section_privacy")
    for key, title_key in panel._title_keys.items():
        if not title_key:
            continue
        card = panel._cards[key]
        assert card.title_lbl.text() == i18n.tr(title_key)


def test_back_button_keeps_its_name_after_retranslate(window):
    """El reporte: tras retraducir, la flecha de Privacidad quedaba sin texto."""
    panel = window.settings_panel
    panel.retranslate()
    panel._open("privacy")
    text = window.config_back_btn.text()
    assert window.config_bar_title.text() == i18n.tr("config.section_privacy")
    assert text.strip("\u2039 ").strip() == i18n.tr("config.title")


def test_navigation_signal_reports_title_depth_and_confirm(window):
    panel = window.settings_panel
    seen = []
    panel.navigationChanged.connect(lambda t, d, c: seen.append((t, d, c)))
    panel._open("privacy")
    assert seen[-1] == (i18n.tr("config.section_privacy"), 1, i18n.tr("config.confirm"))
    _pump(QApplication.instance())
    panel.go_back()
    assert seen[-1] == (i18n.tr("config.title"), 0, "")


def test_language_change_retranslates_bar_and_cards(window):
    panel = window.settings_panel
    panel._open("privacy")
    _pump(QApplication.instance())
    try:
        assert i18n.i18n.load_translation("en")
        window.apply_ui_language()
        assert window.config_bar_title.text() == i18n.tr("config.section_privacy")
        assert window.config_bar_title.text() == "Privacy"
        assert window.config_back_btn.text().strip("\u2039 ").strip() == "Settings"
        assert panel._cards["privacy"].title_lbl.text() == "Privacy"
    finally:
        i18n.i18n.load_translation("es")
        window.apply_ui_language()
    assert window.config_bar_title.text() == "Privacidad"


def test_back_click_is_ignored_while_animating(window):
    """Doble pulsación durante el deslizamiento: no deja la barra desfasada."""
    panel = window.settings_panel
    panel._open("privacy")
    panel.go_back()
    _pump(QApplication.instance())
    assert panel.navigator.depth() == 1
    assert window.config_bar_title.text() == i18n.tr("config.section_privacy")
    panel.go_back()
    _pump(QApplication.instance())
    assert panel.navigator.depth() == 0
    assert window.config_bar_title.text() == i18n.tr("config.title")


def test_confirm_button_returns_to_the_root(window):
    panel = window.settings_panel
    panel._open("general")
    _pump(QApplication.instance())
    window.config_confirm_btn.click()
    _pump(QApplication.instance())
    assert panel.navigator.depth() == 0
    assert isinstance(window.config_confirm_btn, QPushButton)
    assert window.config_confirm_btn.isHidden()
