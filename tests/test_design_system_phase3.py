# -*- coding: utf-8 -*-
"""Fase 3.1: acento corporativo, hoja global y arreglos del sidebar."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib import design_tokens as tokens  # noqa: E402
from lib import fluent_theme as theme  # noqa: E402
from lib.hover_animation import _with_hover_background, _is_pure_hover  # noqa: E402


@pytest.fixture
def qt_app():
    QtWidgets = pytest.importorskip("PyQt6.QtWidgets")
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    yield app
    app.processEvents()


class TestCorporateAccent:
    def test_default_accent_is_the_brand_orange(self):
        assert tokens.ACCENT == "#FF6B00"

    def test_accent_states_are_derived_from_the_orange(self):
        base, hover, pressed = tokens.accent_states()
        assert base == tokens.ACCENT
        assert hover != base and pressed != base

    def test_focus_ring_shares_the_accent(self):
        assert tokens.FOCUS_RING == tokens.ACCENT

    def test_custom_accent_still_wins(self):
        base, hover, pressed = tokens.accent_states("#00A0FF")
        assert base == "#00A0FF"
        assert hover != base and pressed != base

    def test_no_hardcoded_windows_blue_left_in_the_theme(self):
        for name in ("qcheckbox.qss", "qwidget.qss", "qlineedit.qss", "qpushbutton.qss"):
            text = (ROOT / "source" / "qss" / name).read_text(encoding="utf-8").lower()
            assert "0, 120, 212" not in text and "0,120,212" not in text, name
            assert "#0078d4" not in text, name

    def test_pm_data_default_accent_comes_from_the_token(self):
        from lib import pm_data

        assert pm_data.DEFAULT_USER.get("custom_accent_color") == tokens.ACCENT

    def test_entrypoint_falls_back_to_the_token(self):
        text = (ROOT / "packagemaker.py").read_text(encoding="utf-8")
        assert '"#0078D4"' not in text
        assert "return ACCENT" in text

    def test_sidebar_indicator_uses_the_active_accent(self, qt_app):
        from lib.SidebarItem import SidebarItem

        item = SidebarItem("Crear", dark=True)
        item.set_accent("#123456")
        assert item._accent == "#123456"
        item.set_accent("")
        assert item._accent == "#123456"

    def test_checkbox_qss_resolves_the_soft_accent(self):
        qss = tokens.checkbox_qss("#FF6B00")
        assert "__ACCENT_SOFT__" not in qss
        assert "__ACCENT__" not in qss

    def test_sidebar_qss_resolves_the_soft_accent(self):
        for dark in (True, False):
            qss = theme.sidebar_stylesheet(dark, "#FF6B00")
            assert "__ACCENT_SOFT__" not in qss
            assert "__ACCENT__" not in qss

    def test_sidebar_button_qss_resolves_the_soft_accent(self):
        for dark in (True, False):
            qss = theme.sidebar_button_stylesheet(dark, "#FF6B00", 3)
            assert "__ACCENT_SOFT__" not in qss
            assert "__ACCENT__" not in qss


class TestGlobalStylesheet:
    def test_global_stylesheet_covers_inputs_buttons_and_checkboxes(self):
        qss = theme.global_stylesheet("#FF6B00", dark=True)
        assert "QLineEdit" in qss
        assert "QPushButton" in qss
        assert "QCheckBox" in qss

    def test_global_stylesheet_is_balanced_and_fully_rendered(self):
        qss = theme.global_stylesheet("#FF6B00", dark=False)
        assert qss.count("{") == qss.count("}")
        assert "__" not in qss

    def test_entrypoint_installs_it_at_startup(self):
        text = (ROOT / "packagemaker.py").read_text(encoding="utf-8")
        # Arranque (GUI y CLI) y reaplicado del tema comparten la hoja raíz.
        assert text.count("app.setStyleSheet(global_stylesheet(") == 3

    def test_theme_reapply_reuses_the_same_stylesheet(self):
        text = (ROOT / "packagemaker.py").read_text(encoding="utf-8")
        block = text.split("def apply_theme", 1)[1].split("def ", 1)[0]
        assert "global_stylesheet(accent, dark)" in block
        assert "application_stylesheet(" not in block


class TestSidebarHoverFlicker:
    def test_only_pure_hover_rules_are_rewritten(self):
        assert _is_pure_hover("QPushButton:hover") is True
        assert _is_pure_hover("QPushButton:checked:hover") is False
        assert _is_pure_hover("QPushButton::indicator:hover") is False

    def test_checked_hover_keeps_its_selection_colour(self):
        qss = (
            "QPushButton { background-color: transparent; }"
            "QPushButton:hover { background-color: rgba(255,255,255,0.06); }"
            "QPushButton:checked:hover { background-color: rgba(255,255,255,0.12); }"
        )
        patched = _with_hover_background(qss, "rgba(255, 107, 0, 0.500)")
        checked = patched.split("QPushButton:checked:hover", 1)[1]
        assert "rgba(255, 107, 0, 0.500)" not in checked.split("}", 1)[0]

    def test_repeated_frames_do_not_reapply_the_same_stylesheet(self, qt_app):
        from PyQt6.QtWidgets import QPushButton

        from lib.hover_animation import enable_hover_fade

        button = QPushButton("x")
        button.setStyleSheet(
            "QPushButton { background-color: transparent; }"
            "QPushButton:hover { background-color: rgba(255,255,255,0.06); }"
        )
        fade = enable_hover_fade(button, "rgba(255, 255, 255, 0.12)")
        assert fade is not None
        fade._base_qss = button.styleSheet()
        fade._base_color = "rgba(255, 255, 255, 0.06)"
        fade._set_progress(0.5)
        applied = []
        fade._widget.setStyleSheet = lambda qss: applied.append(qss)
        fade._set_progress(0.5)
        assert applied == []

    def test_leaving_always_returns_to_the_base_state(self, qt_app):
        from PyQt6.QtWidgets import QPushButton

        from lib.hover_animation import enable_hover_fade

        button = QPushButton("x")
        button.setStyleSheet(
            "QPushButton { background-color: transparent; }"
            "QPushButton:hover { background-color: rgba(255,255,255,0.06); }"
        )
        fade = enable_hover_fade(button, "rgba(255, 255, 255, 0.12)", only_when=lambda: False)
        fade._animate(1.0)
        assert fade._hovered is False
        fade._animate(0.0)
        assert fade._hovered is False


class TestCollapsedSidebar:
    def test_collapsed_sidebar_keeps_icons_and_hides_the_login_card(self):
        text = (ROOT / "packagemaker.py").read_text(encoding="utf-8")
        block = text.split("def _apply_sidebar_state", 1)[1].split("def enterCompactShellMode", 1)[0]
        assert "btn.set_compact(collapsed)" in block
        assert "self.github_card.setVisible(not collapsed)" in block
        assert "btn.setVisible(not collapsed)" not in block

    def test_compact_item_hides_text_and_keeps_a_tooltip(self, qt_app):
        from lib.SidebarItem import SidebarItem

        item = SidebarItem("Construir", dark=True)
        item.set_compact(True)
        assert item.text() == ""
        assert item.toolTip() == "Construir"
        item.set_compact(False)
        assert item.text() == "Construir"
        assert item.toolTip() == ""

    def test_compact_style_centres_the_icon(self, qt_app):
        from lib.SidebarItem import SidebarItem

        item = SidebarItem("Config", dark=True)
        item.set_compact(True)
        assert "text-align: center" in item.styleSheet()


class TestTranslationsComplete:
    def test_no_mixed_language_left_in_the_startup_strings(self):
        import json

        for code in ("es", "en"):
            data = json.loads((ROOT / "lang" / f"{code}.json").read_text(encoding="utf-8"))
            assert set(data["startup"]) >= {"internal_error_title", "internal_error_body"}
