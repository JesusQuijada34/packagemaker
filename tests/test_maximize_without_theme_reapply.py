# -*- coding: utf-8 -*-
"""R-7c4a1e95: maximizar o restaurar no debe reaplicar el tema completo.

Cada gesto llamaba a ``apply_theme``, que reinstala la hoja global de la
aplicación (``QApplication.setStyleSheet``) y obliga a Qt a re-pulir todos los
widgets: medido en offscreen, ~260 ms de congelación en cada maximizar o
restaurar. En ese gesto sólo cambia el radio de las esquinas.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pytest.importorskip("PyQt6.QtWidgets")

from PyQt6.QtWidgets import QApplication  # noqa: E402

import packagemaker  # noqa: E402
from lib.design_tokens import WINDOW_RADIUS  # noqa: E402

_APP = None
_WINDOW = None


def _window():
    """Ventana principal real, construida una sola vez para toda la prueba."""
    global _APP, _WINDOW
    _APP = QApplication.instance() or QApplication([])
    if _WINDOW is None:
        _WINDOW = packagemaker.PackageTodoGUI()
        _WINDOW.show()
        _APP.processEvents()
    return _WINDOW


def test_maximize_and_restore_do_not_reapply_the_theme(monkeypatch):
    window = _window()
    theme_calls = []
    global_sheets = []

    monkeypatch.setattr(
        packagemaker.PackageTodoGUI,
        "apply_theme",
        lambda self: theme_calls.append(1),
    )
    original_set_style_sheet = QApplication.setStyleSheet

    def spy(self, sheet):
        global_sheets.append(sheet or "")
        return original_set_style_sheet(self, sheet)

    monkeypatch.setattr(QApplication, "setStyleSheet", spy)

    if getattr(window, "_pm_maximized", False):
        window.toggle_frameless_maximize()

    window.toggle_frameless_maximize()
    assert window._pm_maximized is True
    assert "border-radius:0px" in window.styleSheet()
    assert "border-top-left-radius:0px" in window.titlebar.styleSheet()

    window.toggle_frameless_maximize()
    assert window._pm_maximized is False
    rounded = f"border-radius:{WINDOW_RADIUS}px"
    assert rounded in window.styleSheet()
    assert f"border-top-left-radius:{WINDOW_RADIUS}px" in window.titlebar.styleSheet()

    assert theme_calls == []
    assert global_sheets == []


def test_display_mode_change_does_not_repolish_the_app(monkeypatch):
    """Cambiar de modo de visualización no cambia la paleta: no hay re-pulido."""
    window = _window()
    window.apply_theme()

    global_sheets = []
    original_set_style_sheet = QApplication.setStyleSheet

    def spy(self, sheet):
        global_sheets.append(sheet or "")
        return original_set_style_sheet(self, sheet)

    monkeypatch.setattr(QApplication, "setStyleSheet", spy)
    window._apply_display_mode_by_name("GhostBlur (Cristal)")
    assert global_sheets == []

