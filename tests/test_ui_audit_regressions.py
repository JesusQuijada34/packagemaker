"""Regresiones de la auditoría de UI: sidebar, page fade, idiomas y ajustes.

Cada test corresponde a un bug real encontrado al recorrer el código, no a una
preferencia de estilo.
"""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def qapp():
    """QApplication viva durante todo el módulo (si se recolecta, Qt aborta)."""
    qt = pytest.importorskip("PyQt6.QtWidgets")
    app = qt.QApplication.instance() or qt.QApplication([])
    yield app
    app.processEvents()


def source(name):
    return (ROOT / name).read_text(encoding="utf-8")


# --- Bug real: --compact / --shell-mode crasheaba --------------------------- #

def test_enter_compact_shell_mode_exists_and_is_called():
    text = source("packagemaker.py")
    assert "def enterCompactShellMode(self)" in text
    # La llamada debe seguir existiendo; el método es lo que faltaba.
    assert "self.enterCompactShellMode()" in text


def test_enter_compact_shell_mode_collapses_sidebar(qapp):
    import packagemaker as pm

    win = pm.PackageTodoGUI(compact_mode=True)
    try:
        assert win.sidebar_collapsed is True
    finally:
        win.close()
        qapp.processEvents()


# --- Bug real: ítem seleccionado invisible en tema claro -------------------- #

def test_sidebar_item_selected_text_follows_theme():
    text = source("lib/SidebarItem.py")
    assert "TEXT_COLORS" in text
    assert "def set_dark(self, dark)" in text
    # El color seleccionado ya no es siempre blanco: depende del tema.
    assert "SIDEBAR_TEXT_SELECTED_LIGHT" in text
    assert "SIDEBAR_TEXT_SELECTED_DARK" in text


def test_sidebar_item_light_text_and_icon_are_gray(qapp):
    """En modo claro el texto y el icono del sidebar van en gris."""
    from lib.SidebarItem import SidebarItem
    from lib.design_tokens import SIDEBAR_ICON_LIGHT, SIDEBAR_TEXT_LIGHT

    item = SidebarItem("x", dark=False)
    qss = item.styleSheet().lower()
    base_block = qss.split(":hover")[0].split("{")[1].split("}")[0]
    checked_block = qss.split(":checked")[1].split("}")[0]
    assert "#ffffff" not in base_block
    assert SIDEBAR_TEXT_LIGHT.lower() in base_block
    assert "#ffffff" not in checked_block
    assert SIDEBAR_ICON_LIGHT.lower() != "#ffffff"


def test_sidebar_text_and_icon_are_the_same_gray_in_both_themes(qapp):
    """El texto y el icono usan el mismo gris oscuro en claro y en oscuro."""
    from lib.design_tokens import (
        SIDEBAR_ICON_DARK,
        SIDEBAR_ICON_LIGHT,
        SIDEBAR_TEXT_DARK,
        SIDEBAR_TEXT_GRAY,
        SIDEBAR_TEXT_LIGHT,
    )
    from lib.SidebarItem import SidebarItem

    assert SIDEBAR_ICON_DARK == SIDEBAR_ICON_LIGHT == SIDEBAR_TEXT_GRAY
    assert SIDEBAR_TEXT_DARK == SIDEBAR_TEXT_LIGHT == SIDEBAR_TEXT_GRAY
    assert SIDEBAR_TEXT_GRAY.lower() != "#ffffff"
    for dark in (True, False):
        item = SidebarItem("x", dark=dark)
        assert SIDEBAR_TEXT_GRAY.lower() in item.styleSheet().lower()


def test_sidebar_indicator_is_blue_and_transitions_on_toggle(qapp):
    """El indicador azul aparece con una transición al cambiar de página.

    Los ítems son ``autoExclusive``: no se pueden desmarcar directamente, así
    que el deseleccionado se produce al marcar otro ítem del mismo grupo.
    """
    from PyQt6.QtCore import QEventLoop, QTimer
    from PyQt6.QtWidgets import QButtonGroup

    from lib.SidebarItem import SidebarItem

    group = QButtonGroup()
    first = SidebarItem("Config")
    second = SidebarItem("Build")
    group.addButton(first, 0)
    group.addButton(second, 1)

    assert first._indicator_progress == 0.0
    first.setChecked(True)
    loop = QEventLoop()
    QTimer.singleShot(300, loop.quit)
    loop.exec()
    assert first._indicator_progress == 1.0

    # Marcar el segundo desmarca el primero y su indicador se desvanece.
    second.setChecked(True)
    loop = QEventLoop()
    QTimer.singleShot(300, loop.quit)
    loop.exec()
    assert first._indicator_progress == 0.0
    assert second._indicator_progress == 1.0
    # La animación se reutiliza (no se recrea en cada transición).
    assert first._indicator_animation is not None


def test_sidebar_indicator_animation_is_reused_not_deleted(qapp):
    """Regresión: la animación del indicador no debe destruirse al terminar."""
    from PyQt6.QtCore import QEventLoop, QTimer
    from PyQt6.QtWidgets import QButtonGroup

    from lib.SidebarItem import SidebarItem

    group = QButtonGroup()
    items = [SidebarItem(name) for name in ("A", "B")]
    for index, item in enumerate(items):
        group.addButton(item, index)

    # La animación se crea de forma perezosa en el primer toggle y luego se
    # reutiliza; ninguna debe recrearse ni destruirse.
    seen = {}
    for index in (0, 1, 0, 1, 0):
        items[index].setChecked(True)
        loop = QEventLoop()
        QTimer.singleShot(250, loop.quit)
        loop.exec()
        for position, item in enumerate(items):
            animation = item._indicator_animation
            if animation is None:
                continue
            if position in seen:
                assert animation is seen[position]
            else:
                seen[position] = animation
    assert set(seen) == {0, 1}


def test_sidebar_item_dark_text_and_icon_share_the_gray(qapp):
    """En modo oscuro el texto y el icono ya no son blanco puro."""
    from lib.SidebarItem import SidebarItem
    from lib.design_tokens import SIDEBAR_ICON_DARK, SIDEBAR_TEXT_DARK

    item = SidebarItem("x", dark=True)
    qss = item.styleSheet().lower()
    base_block = qss.split(":hover")[0].split("{")[1].split("}")[0]
    assert SIDEBAR_TEXT_DARK.lower() in base_block
    assert "#ffffff" not in base_block
    assert SIDEBAR_ICON_DARK.lower() != "#ffffff"


def test_sidebar_item_indicator_is_short_and_centered():
    text = source("lib/SidebarItem.py")
    assert "SIDEBAR_INDICATOR_HEIGHT" in text
    assert "drawRoundedRect" in text
    assert "def paintEvent" in text


def test_sidebar_button_stylesheet_uses_the_uniform_gray():
    """El QSS del sidebar pinta el texto con el gris uniforme en ambos temas."""
    text = source("lib/fluent_theme.py")
    assert "SIDEBAR_TEXT_GRAY" in text
    # El sidebar_stylesheet ya no impone un border-left a los botones.
    sidebar_fn = text.split("def sidebar_stylesheet")[1].split("def sidebar_button_stylesheet")[0]
    assert "border-left:3px solid" not in sidebar_fn
    # El texto seleccionado ya no cambia de color: es el mismo gris.
    button_fn = text.split("def sidebar_button_stylesheet")[1].split("def checkbox_stylesheet")[0]
    assert "selected_text" not in button_fn
    assert "color:{SIDEBAR_TEXT_GRAY}" in button_fn


# --- Bug real: el fundido de página no se veía ni se limpiaba --------------- #

def test_page_switch_uses_opacity_effect_not_window_opacity():
    text = source("packagemaker.py")
    switch = text.split("def switch_page")[1].split("def _fade_in_widget")[0]
    assert "QGraphicsOpacityEffect" in switch
    # ``windowOpacity`` sobre un widget hijo no tiene efecto visual.
    assert "setWindowOpacity" not in switch


def test_page_fade_cleans_up_on_fast_switching(qapp):
    from PyQt6.QtWidgets import QGraphicsOpacityEffect
    import packagemaker as pm

    win = pm.PackageTodoGUI()
    try:
        for i in (1, 2, 3, 4, 0, 1, 2):
            win.switch_page(i)
        win._clear_page_fade()
        leftovers = [
            i for i in range(win.stack.count())
            if isinstance(win.stack.widget(i).graphicsEffect(), QGraphicsOpacityEffect)
        ]
        assert leftovers == []
    finally:
        win.close()
        qapp.processEvents()


# --- Bug real: ajustes que permitían dejar la ventana ilegible -------------- #

def test_blur_and_radius_are_fixed_constants():
    text = source("lib/window_chrome.py")
    assert "FIXED_BLUR_INTENSITY" in text
    assert "FIXED_WINDOW_RADIUS" in text
    assert "def apply_personalization_effects(window: QWidget, blur_intensity=None, window_radius=None)" in text


def test_config_form_has_no_blur_or_radius_sliders():
    text = source("packagemaker.py")
    assert "conf_blur_slider" not in text
    assert "conf_radius_slider" not in text


# --- Bug real: idiomas ofrecidos sin traducción local ----------------------- #

def test_available_languages_come_from_local_files():
    from lib.i18n import get_available_languages

    langs = get_available_languages()
    codes = [code for code, _ in langs]
    assert "es" in codes and "en" in codes
    for code in codes:
        assert (ROOT / "lang" / f"{code}.json").exists(), f"falta lang/{code}.json"
    # Español e inglés primero.
    assert codes[0] == "es"


def test_all_lang_files_have_the_same_keys():
    def flat(d, pre=""):
        out = {}
        for k, v in d.items():
            if k.startswith("_"):
                continue
            fk = f"{pre}.{k}" if pre else k
            if isinstance(v, dict):
                out.update(flat(v, fk))
            else:
                out[fk] = v
        return out

    base = set(flat(json.loads((ROOT / "lang" / "es.json").read_text(encoding="utf-8"))))
    for path in sorted((ROOT / "lang").glob("*.json")):
        keys = set(flat(json.loads(path.read_text(encoding="utf-8"))))
        assert not (base - keys), f"{path.name} no tiene: {sorted(base - keys)}"


def test_dead_slider_keys_removed_from_translations():
    for path in sorted((ROOT / "lang").glob("*.json")):
        cfg = json.loads(path.read_text(encoding="utf-8")).get("config", {})
        assert "blur_intensity" not in cfg, path.name
        assert "window_radius" not in cfg, path.name
