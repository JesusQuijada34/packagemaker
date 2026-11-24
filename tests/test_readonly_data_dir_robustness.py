# -*- coding: utf-8 -*-
"""Un ``data/`` no escribible no debe tumbar el gestor portable ni el editor.

Regresiones de R-4a7c2e91 y R-8f1d3b62: ``PythonPortableManager.__init__``
creaba ``data/pmCodeEditor/packages`` sin ``try/except`` y el guardado de
``editor_config.json`` hacía ``mkdir()`` dentro de slots de Qt. En una
instalación de solo lectura (Program Files, AppImage, ``/opt``) eso abortaba el
IDE y el panel del editor.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _blocked_parent(tmp_path: Path) -> Path:
    """Ruta cuyo padre es un archivo: ``mkdir`` lanza ``OSError`` siempre."""
    blocker = tmp_path / "blocker"
    blocker.write_text("no soy un directorio", encoding="utf-8")
    return blocker


class TestPortableManagerReadOnlyDataDir:
    def test_construction_survives_unwritable_base_dir(self, tmp_path):
        pytest.importorskip("PyQt6.QtWidgets")
        from lib.python_portable_manager import PythonPortableManager

        manager = PythonPortableManager(base_dir=_blocked_parent(tmp_path) / "pmCodeEditor")
        assert manager.installations == {}
        assert manager.get_installed_versions() == []

    def test_save_config_reports_failure_without_raising(self, tmp_path):
        pytest.importorskip("PyQt6.QtWidgets")
        from lib.python_portable_manager import PythonPortableManager

        manager = PythonPortableManager(base_dir=_blocked_parent(tmp_path) / "pmCodeEditor")
        assert manager._save_config() is False

    def test_python_dir_that_is_a_file_is_ignored(self, tmp_path):
        pytest.importorskip("PyQt6.QtWidgets")
        from lib.python_portable_manager import PythonPortableManager

        manager = PythonPortableManager(base_dir=tmp_path)
        manager.python_dir.write_text("archivo, no carpeta", encoding="utf-8")
        manager._discover_installations()
        assert manager.installations == {}


class TestEditorConfigReadOnlyDataDir:
    def test_dashboard_load_ignores_unreadable_config(self, tmp_path, monkeypatch):
        pytest.importorskip("PyQt6.QtWidgets")
        import lib.pm_dashboard as dashboard

        monkeypatch.setattr(
            dashboard, "EDITOR_CONFIG_PATH", _blocked_parent(tmp_path) / "editor_config.json"
        )
        window = dashboard.DashboardWindow()
        try:
            assert isinstance(window.config, dict)
        finally:
            window.deleteLater()

    def test_dashboard_save_config_does_not_raise(self, tmp_path, monkeypatch):
        pytest.importorskip("PyQt6.QtWidgets")
        import lib.pm_dashboard as dashboard

        window = dashboard.DashboardWindow()
        try:
            monkeypatch.setattr(
                dashboard,
                "EDITOR_CONFIG_PATH",
                _blocked_parent(tmp_path) / "editor_config.json",
            )
            assert window.save_config() is False
        finally:
            window.deleteLater()

    def test_editor_load_and_save_survive_unreadable_config(self, tmp_path, monkeypatch):
        pytest.importorskip("PyQt6.QtWidgets")
        import pmCodeEditor

        monkeypatch.setattr(
            pmCodeEditor, "EDITOR_CONFIG_PATH", _blocked_parent(tmp_path) / "editor_config.json"
        )
        window = pmCodeEditor.EditorWindow()
        try:
            assert window._save_editor_config({"default_interpreter": "x"}) is False
        finally:
            window.deleteLater()
