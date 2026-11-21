# -*- coding: utf-8 -*-
"""Coreografía de arranque y modo inmersivo (bugs.txt Fase 2.2)."""

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.immersive_titlebar import (  # noqa: E402
    EXIT_FULLSCREEN_SVG,
    TRIPLE_CLICK,
    ClickStreak,
    is_immersive,
)
from lib.startup_sequence import (  # noqa: E402
    CODE_INTERNAL_ERROR,
    CODE_LOGIN_REQUIRED,
    CODE_OK,
    collect_internal_errors,
    plan_startup,
)


class TestStartupPlan:
    def test_clean_start_runs_the_full_sequence(self):
        plan = plan_startup(has_session=True)
        assert [step.name for step in plan.steps] == ["splash", "main"]
        assert plan.exit_code == CODE_OK
        assert plan.main_window_visible is True
        assert plan.landing_required is False

    def test_missing_session_requires_the_landing(self):
        plan = plan_startup(has_session=False)
        assert plan.landing_required is True
        assert plan.exit_code == CODE_LOGIN_REQUIRED
        assert plan.main_window_visible is False

    def test_internal_errors_block_the_main_window(self):
        plan = plan_startup(has_session=True, internal_errors=["details.xml roto"])
        assert plan.exit_code == CODE_INTERNAL_ERROR
        assert plan.internal_errors == ["details.xml roto"]
        assert plan.main_window_visible is False

    def test_blank_errors_are_ignored(self):
        plan = plan_startup(has_session=True, internal_errors=["  ", ""])
        assert plan.internal_errors == []
        assert plan.exit_code == CODE_OK

    def test_step_order_is_splash_landing_errors_main(self):
        plan = plan_startup(has_session=False, internal_errors=["boom"])
        assert [step.name for step in plan.steps] == ["splash", "landing", "internal", "main"]

    def test_splash_is_always_the_first_step(self):
        assert plan_startup(has_session=False, internal_errors=["x"]).steps[0].name == "splash"

    def test_login_required_override(self):
        assert plan_startup(has_session=True, login_required=True).landing_required is True
        assert plan_startup(has_session=False, login_required=False).landing_required is False

    def test_step_lookup(self):
        plan = plan_startup(has_session=True)
        assert plan.step("main").code == CODE_OK
        assert plan.step("nope") is None


class TestCollectInternalErrors:
    def test_writable_directories_report_nothing(self, tmp_path):
        assert collect_internal_errors(str(tmp_path), str(tmp_path / "apps")) == []

    def test_unwritable_directory_is_reported(self, tmp_path):
        blocked = tmp_path / "blocked"
        blocked.write_text("not a directory", encoding="utf-8")
        errors = collect_internal_errors(str(blocked / "sub"))
        assert errors and "BASE_DIR" in errors[0]

    def test_missing_templates_are_reported(self, monkeypatch):
        from lib.makeselfEngine import templates

        monkeypatch.setattr(templates, "templates_available", lambda: False)
        errors = collect_internal_errors()
        assert any("plantillas" in error for error in errors)

    def test_probe_file_is_removed(self, tmp_path):
        collect_internal_errors(str(tmp_path))
        assert not (tmp_path / ".pm_write_probe").exists()


class TestClickStreak:
    def test_three_fast_clicks_fire_once(self):
        streak = ClickStreak()
        assert streak.register(0) is False
        assert streak.register(120) is False
        assert streak.register(240) is True
        assert streak.count == 0

    def test_slow_clicks_restart_the_count(self):
        streak = ClickStreak(interval_ms=300)
        streak.register(0)
        streak.register(2000)
        assert streak.count == 1
        assert streak.register(2100) is False

    def test_reset_clears_the_streak(self):
        streak = ClickStreak()
        streak.register(0)
        streak.register(10)
        streak.reset()
        assert streak.register(20) is False
        assert streak.count == 1

    def test_target_is_three(self):
        assert TRIPLE_CLICK == 3

    def test_exit_icon_is_an_svg(self):
        assert b"<svg" in EXIT_FULLSCREEN_SVG
        assert b"path" in EXIT_FULLSCREEN_SVG


@pytest.fixture
def qt_app():
    QtWidgets = pytest.importorskip("PyQt6.QtWidgets")
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    yield app
    app.processEvents()


class TestImmersiveTitleBar:
    def _window(self, widget_cls):
        window = widget_cls()
        window.resize(600, 400)
        titlebar = widget_cls(window)
        titlebar.setFixedHeight(34)
        return window, titlebar

    def test_triple_click_enters_and_exits_immersive(self, qt_app):
        from PyQt6.QtWidgets import QWidget

        from lib.immersive_titlebar import install_immersive_titlebar

        window, titlebar = self._window(QWidget)
        controller = install_immersive_titlebar(window, titlebar)
        assert is_immersive(window) is False

        controller.enter()
        assert is_immersive(window) is True
        controller.exit()
        assert is_immersive(window) is False

    def test_max_button_switches_to_exit_fullscreen_icon(self, qt_app):
        from PyQt6.QtWidgets import QPushButton, QWidget

        from lib.immersive_titlebar import install_immersive_titlebar

        window = QWidget()
        titlebar = QWidget(window)
        btn_max = QPushButton(titlebar)
        titlebar.btn_max = btn_max
        controller = install_immersive_titlebar(window, titlebar)

        controller.enter()
        assert "pantalla completa" in btn_max.toolTip().lower()
        controller.exit()
        assert "pantalla completa" not in btn_max.toolTip().lower()

    def test_max_click_exits_immersive_instead_of_maximizing(self, qt_app):
        from PyQt6.QtWidgets import QPushButton, QWidget

        from lib.immersive_titlebar import install_immersive_titlebar

        window = QWidget()
        titlebar = QWidget(window)
        titlebar.btn_max = QPushButton(titlebar)
        controller = install_immersive_titlebar(window, titlebar)

        controller.enter()
        titlebar.btn_max.click()
        assert is_immersive(window) is False

    def test_top_edge_reveals_the_titlebar(self, qt_app):
        from PyQt6.QtWidgets import QWidget

        from lib.immersive_titlebar import install_immersive_titlebar

        window, titlebar = self._window(QWidget)
        controller = install_immersive_titlebar(window, titlebar)
        controller.enter()
        titlebar.hide()
        controller.reveal_titlebar()
        assert controller._animation is not None
        assert titlebar.isHidden() is False

    def test_conceal_is_a_noop_outside_immersive(self, qt_app):
        from PyQt6.QtWidgets import QWidget

        from lib.immersive_titlebar import install_immersive_titlebar

        window, titlebar = self._window(QWidget)
        controller = install_immersive_titlebar(window, titlebar)
        controller.conceal_titlebar()
        assert is_immersive(window) is False


class TestStartupErrorWindow:
    def test_window_shows_title_and_detail(self, qt_app):
        from lib.startup_error_window import StartupErrorWindow

        window = StartupErrorWindow("Error interno", "Traceback:\n  boom")
        assert window.title_label.text() == "Error interno"
        assert "boom" in window.detail_label.text()
        window.destroy()

    def test_window_has_custom_titlebar_and_no_maximize(self, qt_app):
        from lib.startup_error_window import StartupErrorWindow

        window = StartupErrorWindow("Error", "detalle")
        assert window.titlebar is not None
        assert window.titlebar.btn_max.isHidden()
        window.destroy()

    def test_destroy_closes_the_window(self, qt_app):
        from lib.startup_error_window import StartupErrorWindow

        window = StartupErrorWindow("Error", "detalle")
        window.show()
        window.destroy()
        assert window.isVisible() is False


class TestErrorTranslations:
    @pytest.mark.parametrize("code", ["es", "en", "pt", "fr", "de", "it", "nl", "pl", "ru", "tr", "ar", "ja", "ko", "zh"])
    def test_every_language_has_the_internal_error_title(self, code):
        import json

        data = json.loads((ROOT / "lang" / f"{code}.json").read_text(encoding="utf-8"))
        assert data["startup"]["internal_error_title"].strip()
        assert data["startup"]["internal_error_body"].strip()


class TestErrorStylesheet:
    def test_stylesheet_targets_the_error_window(self):
        from lib.fluent_theme import error_container_stylesheet

        qss = error_container_stylesheet()
        assert "StartupErrorWindow" in qss
        assert "StartupErrorDetail" in qss
        assert qss.count("{") == qss.count("}")

    def test_stylesheet_uses_the_accent(self):
        from lib.fluent_theme import error_container_stylesheet

        assert "#ff6a00" in error_container_stylesheet("#ff6a00")


class TestMainWiring:
    def test_main_checks_internal_errors_before_building_the_ui(self):
        text = (ROOT / "packagemaker.py").read_text(encoding="utf-8")
        plan_at = text.index("plan_startup(")
        ui_at = text.index("main_window = PackageTodoGUI()")
        assert plan_at < ui_at
        assert "show_startup_error" in text

    def test_main_installs_the_immersive_titlebar(self):
        text = (ROOT / "packagemaker.py").read_text(encoding="utf-8")
        assert "install_immersive_titlebar(self, self.titlebar)" in text

    def test_no_module_imports_leviathan_directly(self):
        offenders = []
        for path in (ROOT / "lib").rglob("*.py"):
            if "__pycache__" in path.parts or path.parts[-2] == "leviathan_ui":
                continue
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith(("from leviathan_ui", "import leviathan_ui")):
                    offenders.append(f"{path.relative_to(ROOT)}: {line.strip()}")
        assert offenders == []


def test_startup_error_window_module_lints_clean():
    import subprocess

    result = subprocess.run(
        [sys.executable, "-m", "pyflakes", "lib/startup_sequence.py", "lib/startup_error_window.py", "lib/immersive_titlebar.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_no_leftover_probe_files():
    assert not os.path.exists(ROOT / ".pm_write_probe")
