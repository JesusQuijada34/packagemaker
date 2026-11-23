# -*- coding: utf-8 -*-
"""Regresiones del guardado automático de Configuración.

Cubren, con código real:

- una ruta de proyecto imposible ya no aborta la aplicación desde el slot de
  guardado (``OSError`` sin capturar dentro de Qt);
- guardar una ruta o un aviso no repinta el tema ni retraduce la interfaz, y un
  cambio de apariencia lo repinta una sola vez;
- la selección de motor no se pierde al guardar ajustes.
"""

import os
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="module")
def qapp():
    qt = pytest.importorskip("PyQt6.QtWidgets")
    app = qt.QApplication.instance() or qt.QApplication([])
    yield app
    app.processEvents()


@pytest.fixture
def isolated_store(tmp_path, monkeypatch):
    from lib import pm_data

    monkeypatch.setattr(pm_data, "_data_dir", lambda: tmp_path)
    store = pm_data.PMDataStore(path=tmp_path / "pm.data")
    monkeypatch.setattr(pm_data, "_store", store)
    return store


@pytest.fixture
def window(qapp, isolated_store):
    import packagemaker as pm

    win = pm.PackageTodoGUI()
    yield win
    win.close()
    qapp.processEvents()


class TestEnsureConfigDirectories:
    """``ensure_config_directories`` traduce el fallo en un mensaje."""

    def test_creates_missing_directories(self, tmp_path):
        from packagemaker import ensure_config_directories

        target = tmp_path / "proyectos" / "anidado"
        assert ensure_config_directories(str(target)) is None
        assert target.is_dir()

    def test_reports_uncreatable_path_without_raising(self, tmp_path):
        from packagemaker import ensure_config_directories

        blocker = tmp_path / "archivo"
        blocker.write_text("x", encoding="utf-8")
        error = ensure_config_directories(str(blocker / "sub"))
        assert error is not None
        assert str(blocker) in error

    def test_ignores_empty_values(self):
        from packagemaker import ensure_config_directories

        assert ensure_config_directories("", None, "   ") is None


class TestSettingsReapplyPlan:
    """Sólo se repinta lo que cambió de verdad."""

    BASE = {
        "accent": "#FF6B00",
        "accent_width": 3,
        "density": "normal",
        "display_mode": "GhostBlur (Cristal)",
        "font_family": "",
    }

    def _plan(self, before, after, language_changed=False):
        from packagemaker import settings_reapply_plan

        return settings_reapply_plan(
            before, after, language_changed=language_changed
        )

    def test_unchanged_state_repaints_nothing(self):
        plan = self._plan(dict(self.BASE), dict(self.BASE))
        assert plan == {"language": False, "theme": False, "personalization": False}

    def test_density_change_repaints_theme_once(self):
        after = dict(self.BASE, density="compact")
        plan = self._plan(dict(self.BASE), after)
        assert plan["theme"] is True
        assert plan["personalization"] is False

    def test_display_mode_change_uses_personalization_only(self):
        after = dict(self.BASE, display_mode="Solid")
        plan = self._plan(dict(self.BASE), after)
        assert plan["personalization"] is True
        assert plan["theme"] is False

    def test_language_change_is_independent_of_appearance(self):
        plan = self._plan(dict(self.BASE), dict(self.BASE), language_changed=True)
        assert plan["language"] is True
        assert plan["theme"] is False


class TestAppearanceState:
    """La firma de apariencia ignora rutas y avisos."""

    def test_paths_and_notifications_are_not_appearance(self, isolated_store):
        import packagemaker as pm

        before = pm.settings_appearance_state(isolated_store)
        isolated_store.set_user("base_dir", "/tmp/otro-proyecto")
        isolated_store.set_user("notifications_enabled", True)
        assert pm.settings_appearance_state(isolated_store) == before

    def test_density_and_accent_are_appearance(self, isolated_store):
        import packagemaker as pm

        before = pm.settings_appearance_state(isolated_store)
        isolated_store.set_user("ui_density", "compact")
        isolated_store.set_user("custom_accent_color", "#123456")
        after = pm.settings_appearance_state(isolated_store)
        assert after["density"] == "compact"
        assert after["accent"] == "#123456"
        assert after != before


class TestSettingsAutosave:
    """El guardado real del panel no lanza ni repinta de más."""

    def test_config_page_has_no_save_button(self, window):
        """Configuración guarda sola: no debe reaparecer un botón Guardar."""
        import packagemaker as pm

        assert not hasattr(window, "config_action_bar")
        save_label = pm.tr("save")
        buttons = [
            button.text()
            for button in window.settings_panel.findChildren(pm.QPushButton)
        ]
        assert save_label not in buttons

    def test_uncreatable_path_reports_instead_of_aborting(self, window, tmp_path):
        blocker = tmp_path / "archivo"
        blocker.write_text("x", encoding="utf-8")
        window.conf_base_dir.setText(str(blocker / "sub"))
        window._save_app_config_compact(quiet=True)  # no debe lanzar
        assert "No se pudo guardar" in window.reporter.last_message

    def test_path_only_save_does_not_repaint_theme(self, window, tmp_path):
        started = time.perf_counter()
        window.apply_theme()
        theme_cost = time.perf_counter() - started

        window.conf_base_dir.setText(str(tmp_path / "proyectos"))
        started = time.perf_counter()
        window._save_app_config_compact(quiet=True)
        elapsed = time.perf_counter() - started

        # Reaplicar el tema completo (lo que hacía cada guardado, dos veces)
        # cuesta un orden de magnitud más que guardar sólo una ruta.
        assert theme_cost > 0.005
        assert elapsed < theme_cost / 2

    def test_engine_choice_survives_an_autosave(self, window):
        index = window.engine_combo.findData("flatcube")
        assert index >= 0
        window.engine_combo.setCurrentIndex(index)
        window.conf_notifications.setChecked(True)
        window._save_app_config_compact(quiet=True)
        assert window.engine_combo.currentData() == "flatcube"
