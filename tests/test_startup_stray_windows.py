# -*- coding: utf-8 -*-
"""R-6c4d1f87: las tarjetas de configuración no deben abrir ventanas vacías.

Un ``QLabel`` sin padre es una ventana de nivel superior: llamar a
``setVisible(True)`` sobre él antes de añadirlo al layout lo muestra como una
ventana vacía de 640x480 que desaparece al reparentarlo. En Windows se veían
varias ventanas pequeñas abriéndose y cerrándose antes del splash.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pytest.importorskip("PyQt6.QtWidgets")

from PyQt6.QtWidgets import QApplication, QWidget  # noqa: E402

from lib.settings_cards import SettingsCard, SettingsOptionRow  # noqa: E402
from lib.settings_panel import SettingsPanel  # noqa: E402

_APP = None


def _ensure_app():
    """Conserva una referencia a la QApplication durante la sesión de pruebas."""
    global _APP
    _APP = QApplication.instance() or QApplication([])
    return _APP


@pytest.fixture
def shown_windows(monkeypatch):
    """Widgets sin padre que se mostraron como ventana durante la prueba."""
    recorded = []
    original = QWidget.setVisible

    def spy(self, value):
        if value and self.isWindow() and self.parent() is None:
            recorded.append(type(self).__name__)
        return original(self, value)

    monkeypatch.setattr(QWidget, "setVisible", spy)
    return recorded


def test_card_with_subtitle_shows_no_window(shown_windows):
    _ensure_app()
    card = SettingsCard("General", subtitle="Rutas y traducción")
    try:
        assert shown_windows == []
        assert card.subtitle_lbl.parent() is card
    finally:
        card.deleteLater()


def test_card_without_subtitle_shows_no_window(shown_windows):
    _ensure_app()
    card = SettingsCard("General")
    try:
        assert shown_windows == []
        assert card.subtitle_lbl.isHidden() is True
    finally:
        card.deleteLater()


def test_checked_option_row_shows_no_window(shown_windows):
    _ensure_app()
    row = SettingsOptionRow("Español", "es", checked=True)
    try:
        assert shown_windows == []
        assert row.check_lbl.parent() is row
        assert row.check_lbl.isHidden() is False
    finally:
        row.deleteLater()


def test_settings_panel_build_shows_no_window(shown_windows):
    _ensure_app()
    host = QWidget()
    panel = SettingsPanel(
        host,
        {"base_dir": "/tmp/proyectos", "fluthin_apps": "/tmp/apps", "language": "es"},
    )
    try:
        assert shown_windows == []
    finally:
        panel.deleteLater()
        host.deleteLater()
