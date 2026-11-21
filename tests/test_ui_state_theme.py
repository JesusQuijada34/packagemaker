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
    # La hoja raíz única instala también el QSS del checkbox (Fase 3.1).
    assert "app.setStyleSheet(global_stylesheet" in entrypoint
    assert "checkbox_stylesheet(accent, text)" in theme


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
    theme = source("lib/fluent_theme.py")
    assert "system_theme_mode()" in text
    assert "paletteChanged" in text
    assert "colorSchemeChanged" in text
    assert "sidebar_stylesheet(dark, accent)" in text
    assert "sidebar_button_stylesheet(dark, accent, border_w)" in text
    # La titlebar toma su QSS de un helper central, no de un literal en línea.
    assert "titlebar_label_stylesheet(text_col)" in text
    assert "titlebar_chrome_stylesheet(base_bg, radius)" in text
    assert "background:transparent; color:{text_col}" in theme


def test_window_opens_with_rounded_corners_from_tokens():
    """Al abrir, las cuatro esquinas van redondeadas y salen de los tokens.

    La ventana es frameless y translúcida: el redondeo tiene que pintarse en el
    QMainWindow, la titlebar (arriba) y la barra de estado (abajo). Si el radio
    fuera un literal suelto dejaría de seguir al token ``WINDOW_RADIUS``.
    """
    from lib import qss_loader
    from lib.design_tokens import WINDOW_RADIUS
    from lib.fluent_theme import status_bar_stylesheet, titlebar_chrome_stylesheet

    qwidget = source("source/qss/qwidget.qss")
    assert "@role: window-root" in qwidget
    assert "border-radius: __WINDOW_RADIUS__px" in qwidget

    rendered = qss_loader.qss(
        "qwidget", role="window-root",
        WINDOW_BG="#1C1C1E", WINDOW_RADIUS=WINDOW_RADIUS,
    )
    assert f"border-radius: {WINDOW_RADIUS}px" in rendered

    titlebar = titlebar_chrome_stylesheet("#1C1C1E", WINDOW_RADIUS)
    assert f"border-top-left-radius:{WINDOW_RADIUS}px" in titlebar
    assert f"border-top-right-radius:{WINDOW_RADIUS}px" in titlebar

    status = status_bar_stylesheet(WINDOW_RADIUS)
    assert f"border-bottom-left-radius:{WINDOW_RADIUS}px" in status
    assert f"border-bottom-right-radius:{WINDOW_RADIUS}px" in status

    # Maximizada el radio se colapsa a 0 en los tres sitios.
    assert "border-top-left-radius:0px" in titlebar_chrome_stylesheet("#1C1C1E", 0)
    assert "border-bottom-left-radius:0px" in status_bar_stylesheet(0)
