# -*- coding: utf-8 -*-
"""Pruebas de las transiciones de hover y de la coherencia de los tokens."""

import importlib.util
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_APP = None


def _ensure_app():
    """Crea (y conserva) la QApplication: sin referencia, Qt la recolecta."""
    global _APP
    from PyQt6.QtWidgets import QApplication

    _APP = QApplication.instance() or QApplication([])
    return _APP


class HoverQssTests(unittest.TestCase):
    """La animación debe tocar sólo la regla ``:hover`` pura."""

    def _patch(self, qss, color="rgba(9, 9, 9, 0.500)"):
        from lib.hover_animation import _with_hover_background

        return _with_hover_background(qss, color)

    def test_only_hover_rule_is_rewritten(self):
        qss = (
            "QPushButton{background:#2D2D2D;color:white;}"
            "QPushButton:hover{background:#3A3A3C;}"
            "QPushButton:pressed{background:#242426;}"
        )
        out = self._patch(qss)
        self.assertIn("background:#2D2D2D", out)
        self.assertIn("background:#242426", out)
        self.assertIn("rgba(9, 9, 9, 0.500)", out)
        self.assertNotIn("#3A3A3C", out)

    def test_checked_hover_is_left_untouched(self):
        qss = (
            "QPushButton{background:transparent;}"
            "QPushButton:hover{background:rgba(255,255,255,0.07);}"
            "QPushButton:checked:hover{background:rgba(255,255,255,0.12);}"
        )
        out = self._patch(qss)
        compact = out.replace(" ", "")
        self.assertIn("rgba(255,255,255,0.12)", compact)
        self.assertIn("rgba(9,9,9,0.500)", compact)

    def test_hover_rule_is_created_when_missing(self):
        out = self._patch("QPushButton{background:#2D2D2D;}")
        self.assertIn(":hover", out)
        self.assertIn("rgba(9, 9, 9, 0.500)", out)

    def test_blend_midpoint(self):
        from lib.hover_animation import _blend

        self.assertEqual(_blend("#000000", "#FFFFFF", 0.5), "rgba(128, 128, 128, 1.000)")


class HoverWidgetTests(unittest.TestCase):
    def test_action_buttons_get_a_fade(self):
        if importlib.util.find_spec("PyQt6.QtWidgets") is None:
            self.skipTest("PyQt6 no disponible")
        _ensure_app()
        from lib.page_action_bar import make_action_button, make_icon_button

        for kind in ("primary", "secondary", "destructive"):
            btn = make_action_button("x", kind)
            self.assertIsNotNone(getattr(btn, "_hover_fade", None))
        self.assertIsNotNone(getattr(make_icon_button(None), "_hover_fade", None))

    def test_sidebar_item_fade_skips_selected_item(self):
        if importlib.util.find_spec("PyQt6.QtWidgets") is None:
            self.skipTest("PyQt6 no disponible")
        _ensure_app()
        from lib.SidebarItem import SidebarItem

        item = SidebarItem("Config")
        fade = getattr(item, "_hover_fade", None)
        self.assertIsNotNone(fade)
        item.setChecked(True)
        fade._animate(1.0)
        self.assertFalse(fade._hovered)


class TokenConsistencyTests(unittest.TestCase):
    """No deben quedar colores de la paleta antigua en la interfaz."""

    ROOT = Path(__file__).resolve().parent.parent

    # Paleta antigua que ya no debe aparecer en la interfaz. Se permite en
    # design_tokens.py (histórico) y en los tests.
    LEGACY = ("#ff5722", "#3a3f4b")

    def test_no_legacy_orange_in_ui_sources(self):
        offenders = []
        for path in list(self.ROOT.glob("lib/*.py")) + [
            self.ROOT / "packagemaker.py",
            self.ROOT / "pmCodeEditor.py",
        ]:
            if path.name == "design_tokens.py":
                continue
            text = path.read_text(encoding="utf-8")
            if any(color in text for color in self.LEGACY):
                offenders.append(path.name)
        self.assertEqual(offenders, [], f"colores antiguos en: {offenders}")

    def test_sidebar_item_uses_tokens(self):
        from lib.SidebarItem import SidebarItem
        from lib.design_tokens import SIDEBAR_ITEM_HEIGHT

        if importlib.util.find_spec("PyQt6.QtWidgets") is None:
            self.skipTest("PyQt6 no disponible")
        _ensure_app()
        item = SidebarItem("x")
        self.assertEqual(item.height(), SIDEBAR_ITEM_HEIGHT)

    def test_content_and_titlebar_are_translucent(self):
        from lib.design_tokens import CONTENT_BG, TITLEBAR_BG

        for value in (CONTENT_BG, TITLEBAR_BG):
            self.assertTrue(value.startswith("rgba("), value)
            self.assertNotEqual(value.split(",")[-1].strip().rstrip(")"), "1.0")


class EditorAccentTests(unittest.TestCase):
    def test_editor_uses_active_accent(self):
        import pmCodeEditor as ed

        # El naranja antiguo ya no está fijo: se interpola el acento activo.
        self.assertIn(ed.EDITOR_ACCENT, ed.DARK_QSS)
        self.assertNotIn("{EDITOR_ACCENT}", ed.DARK_QSS)

    def test_editor_shades_are_derived(self):
        import pmCodeEditor as ed

        self.assertNotEqual(ed.EDITOR_ACCENT_HOVER, ed.EDITOR_ACCENT)
        self.assertNotEqual(ed.EDITOR_ACCENT_PRESSED, ed.EDITOR_ACCENT)


if __name__ == "__main__":
    unittest.main()
