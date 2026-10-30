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
    # El color seleccionado ya no es siempre blanco: en claro usa el acento.
    assert "selected" in text and "ACCENT" in text


def test_sidebar_item_light_selected_color_is_not_white(qapp):
    from lib.SidebarItem import SidebarItem

    item = SidebarItem("x", dark=False)
    qss = item.styleSheet().lower()
    checked_block = qss.split(":checked")[1].split("}")[0]
    assert "#ffffff" not in checked_block
    assert "#0078d4" in checked_block


def test_sidebar_item_indicator_is_short_and_centered():
    text = source("lib/SidebarItem.py")
    assert "SIDEBAR_INDICATOR_HEIGHT" in text
    assert "drawRoundedRect" in text
    assert "def paintEvent" in text


def test_sidebar_button_stylesheet_selected_text_is_theme_aware():
    text = source("lib/fluent_theme.py")
    assert "selected_text" in text
    # El sidebar_stylesheet ya no impone un border-left a los botones.
    sidebar_fn = text.split("def sidebar_stylesheet")[1].split("def sidebar_button_stylesheet")[0]
    assert "border-left:3px solid" not in sidebar_fn


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
