"""Regression checks for real checkbox state and theme-aware desktop UI."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def source(name):
    return (ROOT / name).read_text(encoding="utf-8")


def test_checkbox_uses_authoritative_qt_state_and_events():
    text = source("lib/fluent_theme.py")
    assert "checkStateChanged" in text
    assert "self.checkState()" in text
    assert "setCheckState" not in text or "checkStateChanged" in text
    assert "QPropertyAnimation(self, b\"checkProgress\", self)" in text
    assert "Qt.CheckState.PartiallyChecked" in text


def test_theme_and_font_have_system_fallbacks():
    text = source("lib/fluent_theme.py")
    assert "def system_theme_mode" in text
    assert "colorScheme" in text
    assert "AppsUseLightTheme" in text
    assert "def preferred_ui_font" in text
    for family in ("Roboto", "Inter Regular", "SF Pro Display"):
        assert family in text


def test_sidebar_and_titlebar_are_theme_aware_and_transparent():
    text = source("packagemaker.py")
    assert "system_theme_mode()" in text
    assert "paletteChanged" in text
    assert "colorSchemeChanged" in text
    assert "sidebar_stylesheet(dark, accent)" in text
    assert "sidebar_button_stylesheet(dark, accent, border_w)" in text
    assert "background:transparent; color:{text_col}" in text
