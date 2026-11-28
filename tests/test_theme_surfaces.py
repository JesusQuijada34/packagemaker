"""R-5a7d2f16 / Q-026: sidebar translúcido y pintado por tema.

El sidebar llevaba ``WA_TranslucentBackground``, que activa
``WA_NoSystemBackground`` y anula su fondo QSS: el panel quedaba transparente y
el blanco translúcido que pide el propietario nunca se pintaba.
"""

import re
from pathlib import Path

from lib import design_tokens as tokens
from lib import fluent_theme as theme

ROOT = Path(__file__).resolve().parents[1]


def _alpha(rgba: str) -> float:
    match = re.search(r",\s*([0-9.]+)\s*\)$", rgba)
    assert match, rgba
    return float(match.group(1))


def test_sidebar_surfaces_are_translucent_within_the_requested_range():
    for value in (tokens.SIDEBAR_BG, tokens.SIDEBAR_BG_LIGHT):
        assert value.startswith("rgba("), value
        assert 0.3 <= _alpha(value) <= 0.5, value


def test_sidebar_inverts_white_and_dark_with_the_theme():
    light = theme.sidebar_stylesheet(False, "#0078D4")
    dark = theme.sidebar_stylesheet(True, "#0078D4")
    assert tokens.SIDEBAR_BG_LIGHT in light
    assert tokens.SIDEBAR_BG not in light
    assert tokens.SIDEBAR_BG in dark


def test_sidebar_qss_has_no_hardcoded_light_background():
    qss = (ROOT / "source" / "qss" / "qwidget.qss").read_text(encoding="utf-8")
    assert "rgba(242,242,247" not in qss
    assert "rgba(242, 242, 247" not in qss


def test_applyget_selects_the_sidebar_background_per_theme():
    def rule(sheet):
        return sheet.split("QWidget#NavigationSidebar", 1)[1].split("}", 1)[0]

    assert tokens.SIDEBAR_BG_LIGHT in rule(theme.applyget("#0078D4", False))
    assert tokens.SIDEBAR_BG in rule(theme.applyget("#0078D4", True))


def test_sidebar_is_not_translucent_at_widget_level():
    """``WA_TranslucentBackground`` anula el fondo QSS del sidebar."""
    text = (ROOT / "packagemaker.py").read_text(encoding="utf-8")
    block = text.split("self.sidebar.setObjectName", 1)[1].split(
        "self.sidebar_layout", 1
    )[0]
    assert "setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground" not in block
    assert "setAttribute(Qt.WidgetAttribute.WA_StyledBackground" in block


def _sidebar_edge_color(sidebar):
    image = sidebar.grab().toImage()
    return image.pixelColor(image.width() - 1, image.height() // 2)


def test_sidebar_edge_is_white_on_dark_and_gray_on_light(_qt_app):
    """R-9b5d3e72 (issue #21): el borde del sidebar debe distinguirse del fondo.

    El propietario pide gris en el tema claro y blanco en el oscuro; con
    ``#333333`` sobre un fondo ``#1C1C1E`` el separador era invisible.
    """
    from PyQt6.QtWidgets import QApplication

    import packagemaker

    app = QApplication.instance() or _qt_app
    window = packagemaker.PackageTodoGUI()
    window.resize(1024, 720)
    window.show()
    app.processEvents()
    try:
        # Sin ``processEvents`` entre medias: el vigilante de tema del sistema
        # reajustaría ``last_theme_mode`` y volvería a pintar el tema real.
        window.last_theme_mode = "dark"
        window.apply_theme()
        dark_edge = _sidebar_edge_color(window.sidebar)
        assert dark_edge.name().lower() == tokens.SIDEBAR_BORDER_DARK.lower()
        assert dark_edge.red() > 240, "el borde oscuro no es blanco"

        window.last_theme_mode = "light"
        window.apply_theme()
        light_edge = _sidebar_edge_color(window.sidebar)
        assert light_edge.name().lower() == tokens.SIDEBAR_BORDER_LIGHT.lower()
        assert light_edge.red() < 235, "el borde claro debe seguir siendo gris"
    finally:
        window.close()
        app.processEvents()


def test_sidebar_paints_its_translucent_background(_qt_app):
    from PyQt6.QtWidgets import QApplication

    import packagemaker

    app = QApplication.instance() or _qt_app
    window = packagemaker.PackageTodoGUI()
    window.resize(1024, 720)
    window.show()
    app.processEvents()
    try:
        # Sin ``processEvents`` entre medias: el vigilante de tema del sistema
        # reajustaría ``last_theme_mode`` y volvería a pintar el tema real.
        window.last_theme_mode = "light"
        window.apply_theme()
        assert tokens.SIDEBAR_BG_LIGHT in window.sidebar.styleSheet()
        window.last_theme_mode = "dark"
        window.apply_theme()
        assert tokens.SIDEBAR_BG in window.sidebar.styleSheet()

        image = window.sidebar.grab().toImage()
        corner = image.pixelColor(image.width() - 5, image.height() - 5)
        assert corner.alpha() > 0, "el sidebar no pinta su fondo QSS"
    finally:
        window.close()
        app.processEvents()
