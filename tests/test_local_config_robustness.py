# -*- coding: utf-8 -*-
"""Configuraciones locales con forma no-objeto no deben tumbar la aplicación.

Regresiones de R-4e7c2b91 (caché de sesión e idioma) y R-9a3d6f20 (config del
editor y de «Abrir con»): un JSON válido que no era un objeto reventaba en
``.get()``/``.items()`` durante el arranque o al abrir un proyecto.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lib.i18n as i18n  # noqa: E402
import lib.session_cache as session_cache  # noqa: E402


class TestSessionCacheShapes:
    def _write(self, tmp_path, payload, monkeypatch):
        monkeypatch.setattr(session_cache, "_cache_path", lambda: tmp_path / "session.cache")
        (tmp_path / "session.cache").write_bytes(
            session_cache._encrypt(json.dumps(payload).encode("utf-8"))
        )

    def test_non_object_payload_is_discarded(self, tmp_path, monkeypatch):
        self._write(tmp_path, ["no", "es", "un", "perfil"], monkeypatch)
        assert session_cache.load_session() is None

    def test_non_object_profile_falls_back_to_empty_dict(self, tmp_path, monkeypatch):
        self._write(tmp_path, {"token": "tok", "profile": ["login"]}, monkeypatch)
        assert session_cache.load_session() == ("tok", {})

    def test_valid_session_still_round_trips(self, tmp_path, monkeypatch):
        monkeypatch.setattr(session_cache, "_cache_path", lambda: tmp_path / "session.cache")
        assert session_cache.save_session("tok", {"login": "ana"})
        assert session_cache.load_session() == ("tok", {"login": "ana"})


class TestLanguageFileShapes:
    def test_non_object_language_file_is_ignored(self, tmp_path, monkeypatch):
        (tmp_path / "es.json").write_text("[]", encoding="utf-8")
        monkeypatch.setattr(i18n, "_get_lang_dir", lambda: str(tmp_path))
        monkeypatch.setattr(i18n, "_translation_cache", {})
        assert i18n._load_lang_file("es") == {}
        assert i18n._flatten_translations(i18n._load_lang_file("es")) == {}

    def test_nested_dictionary_still_flattens(self, tmp_path, monkeypatch):
        (tmp_path / "en.json").write_text('{"a": {"b": "B"}}', encoding="utf-8")
        monkeypatch.setattr(i18n, "_get_lang_dir", lambda: str(tmp_path))
        monkeypatch.setattr(i18n, "_translation_cache", {})
        assert i18n._flatten_translations(i18n._load_lang_file("en")) == {"a.b": "B"}

    def test_flatten_ignores_non_object(self):
        assert i18n._flatten_translations([1, 2]) == {}


class TestPortableManagerConfigShapes:
    def test_malformed_config_does_not_break_construction(self, tmp_path):
        pytest.importorskip("PyQt6.QtWidgets")
        from lib.python_portable_manager import PythonPortableManager

        payloads = [
            [],
            "texto",
            {"installations": []},
            {"installations": {"3.12": "x"}},
            {"installations": {"3.12": {"path": 1, "python_exe": 2, "pip_exe": 3}}},
        ]
        for payload in payloads:
            (tmp_path / "config.json").write_text(json.dumps(payload), encoding="utf-8")
            manager = PythonPortableManager(base_dir=tmp_path)
            assert manager.installations == {}

    def test_valid_installation_is_loaded(self, tmp_path):
        pytest.importorskip("PyQt6.QtWidgets")
        from lib.python_portable_manager import PythonPortableManager

        (tmp_path / "config.json").write_text(
            json.dumps(
                {
                    "installations": {
                        "3.12": {
                            "path": str(tmp_path / "python312"),
                            "python_exe": str(tmp_path / "python312" / "python.exe"),
                            "pip_exe": str(tmp_path / "python312" / "pip.exe"),
                            "is_installed": True,
                            "size_mb": 12,
                        }
                    }
                }
            ),
            encoding="utf-8",
        )
        manager = PythonPortableManager(base_dir=tmp_path)
        assert manager.installations["3.12"].is_installed is True


class TestDashboardConfigShapes:
    def test_non_object_config_falls_back_to_defaults(self, tmp_path, monkeypatch):
        pytest.importorskip("PyQt6.QtWidgets")
        import lib.pm_dashboard as dashboard

        config_path = tmp_path / "editor_config.json"
        config_path.write_text("[]", encoding="utf-8")
        monkeypatch.setattr(dashboard, "EDITOR_CONFIG_PATH", config_path)
        window = dashboard.DashboardWindow()
        try:
            assert isinstance(window.config, dict)
            assert window.config["recent_projects"] == []
        finally:
            window.deleteLater()

    def test_non_list_recents_are_ignored(self, tmp_path, monkeypatch):
        pytest.importorskip("PyQt6.QtWidgets")
        import lib.pm_dashboard as dashboard

        config_path = tmp_path / "editor_config.json"
        config_path.write_text(json.dumps({"recent_projects": 5}), encoding="utf-8")
        monkeypatch.setattr(dashboard, "EDITOR_CONFIG_PATH", config_path)
        window = dashboard.DashboardWindow()
        try:
            assert window.recent_list.count() == 0
            window._add_to_recent(str(tmp_path))
            assert window.config["recent_projects"] == [str(tmp_path)]
        finally:
            window.deleteLater()

    def test_non_string_interpreter_is_ignored(self, tmp_path, monkeypatch):
        pytest.importorskip("PyQt6.QtWidgets")
        import lib.pm_dashboard as dashboard

        config_path = tmp_path / "editor_config.json"
        for payload in (123, ["x"], {"a": 1}):
            config_path.write_text(
                json.dumps({"default_interpreter": payload}), encoding="utf-8"
            )
            monkeypatch.setattr(dashboard, "EDITOR_CONFIG_PATH", config_path)
            window = dashboard.DashboardWindow()
            try:
                assert isinstance(window.python_path, str) and window.python_path
            finally:
                window.deleteLater()


class TestEditorConfigShapes:
    """El editor usa el mismo ``editor_config.json`` que el panel."""

    def test_non_object_config_is_ignored(self, tmp_path, monkeypatch):
        pytest.importorskip("PyQt6.QtWidgets")
        import pmCodeEditor

        config_path = tmp_path / "editor_config.json"
        for payload in ([], "texto", 42):
            config_path.write_text(json.dumps(payload), encoding="utf-8")
            monkeypatch.setattr(pmCodeEditor, "EDITOR_CONFIG_PATH", config_path)
            window = pmCodeEditor.EditorWindow()
            try:
                assert isinstance(window.python_path, str) and window.python_path
            finally:
                window.deleteLater()

    def test_non_string_interpreter_is_ignored(self, tmp_path, monkeypatch):
        pytest.importorskip("PyQt6.QtWidgets")
        import pmCodeEditor

        config_path = tmp_path / "editor_config.json"
        for payload in (["x"], {"a": 1}):
            config_path.write_text(
                json.dumps({"default_interpreter": payload}), encoding="utf-8"
            )
            monkeypatch.setattr(pmCodeEditor, "EDITOR_CONFIG_PATH", config_path)
            window = pmCodeEditor.EditorWindow()
            try:
                assert isinstance(window.python_path, str) and window.python_path
            finally:
                window.deleteLater()


class TestProjectConfigShapes:
    def test_malformed_document_is_ignored(self, tmp_path):
        from lib.projectConfig import ProjectConfig

        config = ProjectConfig(str(tmp_path))
        for payload in ([], "texto", 42, {"projects": []}, {"editors": "x"}):
            config.config_file.write_text(json.dumps(payload), encoding="utf-8")
            assert config.get_project_editor("/proyecto") is None
            assert config.get_editor_path("code") is None
            config.set_project_editor("/proyecto", "code")
            config.set_editor_path("code", "/usr/bin/code")
            assert config.get_project_editor("/proyecto") == "code"
            assert config.get_editor_path("code") == "/usr/bin/code"
            config.remove_project_editor("/proyecto")
            assert config.get_project_editor("/proyecto") is None
