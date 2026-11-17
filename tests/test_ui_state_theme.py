"""Regression checks for real checkbox state and theme-aware desktop UI."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def source(name):
    return (ROOT / name).read_text(encoding="utf-8")


def test_checkbox_uses_native_painting_and_shared_root_stylesheet():
    theme = source("lib/fluent_theme.py")
    tokens = source("lib/design_tokens.py")
    stylesheet = source("source/qss/qcheckbox.qss")
    entrypoint = source("packagemaker.py")
    checkbox_class = theme.split("class FluentCheckBox", 1)[1].split("\nelse:", 1)[0]

    assert "def paintEvent" not in checkbox_class
    assert "qcheckbox" in tokens
    assert 'image: url("__CHECK_ICON__")' in stylesheet
    assert 'image: url("__PARTIAL_ICON__")' in stylesheet
    assert "app.setStyleSheet(checkbox_stylesheet" in entrypoint


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
