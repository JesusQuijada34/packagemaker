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

    def test_sidebar_item_hover_does_not_repolish(self):
        """Regresión del parpadeo azul/gris: el resalte se pinta, no se
        reescribe la hoja de estilo en cada fotograma (cada ``setStyleSheet``
        fuerza un re-polish y el ítem cambiaba de color a destiempo)."""
        if importlib.util.find_spec("PyQt6.QtWidgets") is None:
            self.skipTest("PyQt6 no disponible")
        _ensure_app()
        from lib.SidebarItem import SidebarItem

        item = SidebarItem("Config")
        calls = []
        item.setStyleSheet = calls.append  # type: ignore[method-assign]
        item._animate_hover(1.0)
        for value in (0.0, 0.25, 0.5, 0.75, 1.0):
            item.hoverProgress = value
        self.assertEqual(calls, [], "el hover no debe reaplicar el QSS")

    def test_sidebar_item_skips_hover_when_selected(self):
        if importlib.util.find_spec("PyQt6.QtWidgets") is None:
            self.skipTest("PyQt6 no disponible")
        _ensure_app()
        from lib.SidebarItem import SidebarItem

        item = SidebarItem("Config")
        item.setChecked(True)
        item._animate_hover(1.0)
        self.assertEqual(item.hoverProgress, 0.0)

    def test_sidebar_selection_uses_accent_not_hardcoded_blue(self):
        if importlib.util.find_spec("PyQt6.QtWidgets") is None:
            self.skipTest("PyQt6 no disponible")
        _ensure_app()
        from lib.SidebarItem import SidebarItem
        from lib.design_tokens import with_alpha

        item = SidebarItem("Config")
        item.set_accent("#E81123")
        qss = item.styleSheet()
        self.assertIn(with_alpha("#E81123", 0.18), qss)
        self.assertNotIn("0, 120, 212", qss)

    def test_sidebar_default_width_is_wider(self):
        from lib.design_tokens import SIDEBAR_MAX_WIDTH
        from lib.pm_data import DEFAULT_USER

        self.assertGreaterEqual(SIDEBAR_MAX_WIDTH, 270)
        self.assertEqual(DEFAULT_USER["sidebar_width"], SIDEBAR_MAX_WIDTH)

    def test_animation_object_survives_repeated_hover(self):
        """Regresión: ``DeleteWhenStopped`` destruía el objeto C++ y el
        siguiente ``stop()`` lanzaba
        ``RuntimeError: wrapped C/C++ object ... has been deleted``."""
        if importlib.util.find_spec("PyQt6.QtWidgets") is None:
            self.skipTest("PyQt6 no disponible")
        app = _ensure_app()
        from lib.hover_animation import enable_hover_fade
        from PyQt6.QtCore import QEventLoop, QTimer
        from PyQt6.QtWidgets import QPushButton

        btn = QPushButton("x")
        btn.setStyleSheet("QPushButton{background:#2D2D2D;}QPushButton:hover{background:#3A3A3C;}")
        fade = enable_hover_fade(btn, "rgba(255,255,255,0.10)")
        self.assertIsNotNone(fade)
        animation = fade._animation
        # Varios ciclos completos: hay que dejar que la animación *termine*,
        # que es cuando el patrón antiguo liberaba el objeto C++.
        for _ in range(5):
            fade._animate(1.0)
            loop = QEventLoop()
            QTimer.singleShot(250, loop.quit)
            loop.exec()
            fade._animate(0.0)
            loop = QEventLoop()
            QTimer.singleShot(250, loop.quit)
            loop.exec()
            app.processEvents()
        self.assertIs(fade._animation, animation, "la animación debe reutilizarse")


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


class AccentStateTests(unittest.TestCase):
    """El acento del usuario debe propagarse también a hover y pressed."""

    def test_default_blue_keeps_curated_states(self):
        from lib.design_tokens import ACCENT, ACCENT_HOVER, ACCENT_PRESSED, accent_states

        self.assertEqual(accent_states(ACCENT), (ACCENT, ACCENT_HOVER, ACCENT_PRESSED))
        self.assertEqual(accent_states(""), (ACCENT, ACCENT_HOVER, ACCENT_PRESSED))

    def test_custom_accent_derives_states(self):
        from lib.design_tokens import accent_states

        base, hover, pressed = accent_states("#E81123")
        self.assertEqual(base, "#E81123")
        self.assertNotEqual(hover, base)
        self.assertNotEqual(pressed, base)
        # hover aclara, pressed oscurece.
        self.assertGreater(int(hover[1:3], 16), int(base[1:3], 16))
        self.assertLess(int(pressed[1:3], 16), int(base[1:3], 16))

    def test_primary_button_states_follow_the_accent(self):
        from lib.design_tokens import primary_button_qss

        qss = primary_button_qss("#E81123")
        self.assertIn("background-color: #E81123", qss)
        # Ya no quedan azules fijos del tema por defecto.
        self.assertNotIn("#1084D8", qss)
        self.assertNotIn("#005FB8", qss)

    def test_uwp_button_uses_accent_and_flat_radius(self):
        from lib.design_tokens import uwp_button_qss

        qss = uwp_button_qss("#E81123")
        self.assertIn("background:#E81123", qss)
        self.assertIn("border-radius:4px", qss)

    def test_color_helpers_are_safe_on_bad_input(self):
        from lib.design_tokens import shade_color, tint_color, with_alpha

        self.assertEqual(shade_color("nope", 1.2), "nope")
        self.assertEqual(tint_color("", 0.5), "")
        self.assertEqual(with_alpha("bad", 0.5), "bad")

    def test_active_accent_reads_user_preference(self):
        from lib.design_tokens import active_accent

        # Sin preferencia configurada cae al acento por defecto.
        self.assertTrue(active_accent().startswith("#"))


class AccentPropagationTests(unittest.TestCase):
    """Las hojas de estilo raíz deben derivar los estados del acento activo."""

    def test_applyget_states_follow_the_accent(self):
        from lib.fluent_theme import applyget

        qss = applyget("#E81123", dark=True)
        self.assertIn("#E81123", qss)
        self.assertNotIn("#1084D8", qss)
        self.assertNotIn("#005FB8", qss)

    def test_application_stylesheet_states_follow_the_accent(self):
        from lib.fluent_theme import application_stylesheet

        qss = application_stylesheet(True, "#E81123")
        self.assertNotIn("#1084D8", qss)
        self.assertNotIn("#005FB8", qss)

    def test_splash_stylesheet_accepts_accent(self):
        from lib.fluent_theme import splash_stylesheet

        self.assertIn("#E81123", splash_stylesheet("#E81123"))

    def test_action_bar_styles_are_accent_aware(self):
        from lib import page_action_bar as pab

        self.assertIn(pab.ACCENT_COLOR, pab.STYLE_PRIMARY)
        self.assertNotEqual(pab.STYLE_PRIMARY, pab.STYLE_SECONDARY)


if __name__ == "__main__":
    unittest.main()
