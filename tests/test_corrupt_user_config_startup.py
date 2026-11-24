# -*- coding: utf-8 -*-
"""Ciclo 43: una configuración local corrupta no debe abortar el arranque.

Cubre tres fallos descubiertos en la auditoría interna:

- ``R-4a7f2c93``: ``base_dir``/``fluthin_apps`` guardados como objeto, lista o
  número reventaban en ``os.makedirs`` (``TypeError``) al importar
  ``packagemaker``; una cadena con byte NUL lanzaba ``ValueError``.
- ``R-8d3e6b15``: un ``language`` no textual reventaba en
  ``i18n.load_translation`` (``AttributeError: 'dict' object has no attribute
  'lower'``).
- ``R-2f5c9a71``: un ``custom_accent_color`` que no es ``#RRGGBB`` reventaba al
  construir una notificación con acción ``primary`` (``ValueError`` en el
  parseo hexadecimal) y el slot de Qt abortaba el proceso.
"""

import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib import pm_data  # noqa: E402
from lib.pm_data import PMDataStore, coerce_text  # noqa: E402


@pytest.fixture
def qt_app():
    QtWidgets = pytest.importorskip("PyQt6.QtWidgets")
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    yield app
    app.processEvents()


def _store(tmp_path, user):
    path = tmp_path / "pm.data"
    path.write_text(
        json.dumps({"schema_version": 1, "user": user}), encoding="utf-8"
    )
    return PMDataStore(path)


class TestTextCoercion:
    def test_coerce_text_keeps_only_strings(self):
        assert coerce_text("C:/proyectos") == "C:/proyectos"
        assert coerce_text("", "fallback") == ""
        for value in ({"x": 1}, [1], 5, True, None):
            assert coerce_text(value, "fallback") == "fallback"

    @pytest.mark.parametrize("value", [{"x": 1}, [1], 5, True, None])
    def test_non_text_paths_never_reach_os_makedirs(self, tmp_path, value):
        store = _store(tmp_path, {"base_dir": value, "fluthin_apps": value})
        config = store.to_legacy_app_config()
        assert config["BASE_DIR"] == ""
        assert config["Fluthin_APPS"] == ""
        # Lo que hace ``packagemaker`` al importar: no debe lanzar.
        os.makedirs(config["BASE_DIR"] or str(tmp_path / "fallback"), exist_ok=True)

    def test_text_paths_are_preserved(self, tmp_path):
        store = _store(
            tmp_path, {"base_dir": str(tmp_path), "fluthin_apps": "/tmp/fluthin"}
        )
        config = store.to_legacy_app_config()
        assert config["BASE_DIR"] == str(tmp_path)
        assert config["Fluthin_APPS"] == "/tmp/fluthin"

    @pytest.mark.parametrize("value", ["\x00", "  ", {"x": 1}, [1]])
    def test_corrupt_paths_are_repaired_by_the_loader(
        self, tmp_path, monkeypatch, value
    ):
        store = _store(tmp_path, {"base_dir": value, "fluthin_apps": value})
        monkeypatch.setattr(pm_data, "_store", store)
        config = pm_data.load_merged_app_config(
            legacy_config_path=tmp_path / "missing.json",
            default_base_dir=str(tmp_path / "projects"),
            default_fluthin=str(tmp_path / "apps"),
        )
        assert config["BASE_DIR"] == str(tmp_path / "projects")
        assert config["Fluthin_APPS"] == str(tmp_path / "apps")
        assert store.get_user("base_dir") == str(tmp_path / "projects")

    def test_non_text_legacy_settings_are_not_imported(self, tmp_path, monkeypatch):
        store = _store(tmp_path, {})
        monkeypatch.setattr(pm_data, "_store", store)
        legacy = tmp_path / "settings.json"
        legacy.write_text(
            json.dumps(
                {
                    "BASE_DIR": {"x": 1},
                    "Fluthin_APPS": [1],
                    "LANGUAGE": {"a": 1},
                    "dpi_scale": 2,
                }
            ),
            encoding="utf-8",
        )
        config = pm_data.load_merged_app_config(
            legacy_config_path=legacy,
            default_base_dir=str(tmp_path / "projects"),
            default_fluthin=str(tmp_path / "apps"),
        )
        assert config["BASE_DIR"] == str(tmp_path / "projects")
        assert config["Fluthin_APPS"] == str(tmp_path / "apps")
        assert config["LANGUAGE"] == "es"
        assert config["dpi_scale"] == 2


class TestLanguageCoercion:
    @pytest.mark.parametrize("value", [{"a": 1}, [1], 5])
    def test_non_text_language_falls_back_to_spanish(self, tmp_path, value):
        store = _store(tmp_path, {"language": value})
        assert store.to_legacy_app_config()["LANGUAGE"] == "es"

    def test_load_translation_accepts_corrupt_language(self, qt_app, monkeypatch):
        from lib.i18n import I18nManager

        monkeypatch.setattr(I18nManager, "_instance", None)
        manager = I18nManager()
        manager.initialize(qt_app, "es")
        assert manager.load_translation({"a": 1}) is True
        assert manager.get_current_lang() == "es"

    def test_unknown_language_code_falls_back_to_spanish(self, qt_app, monkeypatch):
        from lib.i18n import I18nManager

        monkeypatch.setattr(I18nManager, "_instance", None)
        manager = I18nManager()
        manager.initialize(qt_app, "es")
        manager.load_translation("xx")
        assert manager.get_current_lang() == "es"


class TestAccentRobustness:
    @pytest.mark.parametrize(
        "value, expected",
        [
            ("#FF6B00", "#FF6B00"),
            ("#0078d4", "#0078d4"),
            ("FF6B00", "DEFAULT"),
            ("#FF6B0", "DEFAULT"),
            ("#FF6B00AA", "DEFAULT"),
            ("azul", "DEFAULT"),
            ("", "DEFAULT"),
            (None, "DEFAULT"),
            ({"a": 1}, "DEFAULT"),
            ([1], "DEFAULT"),
        ],
    )
    def test_normalize_accent(self, value, expected):
        from lib.design_tokens import ACCENT, normalize_accent

        if expected == "DEFAULT":
            expected = ACCENT
        assert normalize_accent(value) == expected

    def test_active_accent_ignores_corrupt_preference(self, tmp_path, monkeypatch):
        from lib.design_tokens import ACCENT, active_accent

        monkeypatch.setattr(
            pm_data, "_store", _store(tmp_path, {"custom_accent_color": "azul"})
        )
        assert active_accent() == ACCENT

    def test_active_accent_keeps_valid_preference(self, tmp_path, monkeypatch):
        from lib.design_tokens import active_accent

        monkeypatch.setattr(
            pm_data, "_store", _store(tmp_path, {"custom_accent_color": "#123ABC"})
        )
        assert active_accent() == "#123ABC"

    def test_darken_color_ignores_invalid_values(self, qt_app):
        from lib.notificationSystem import NotificationData, NotificationWidget

        widget = NotificationWidget(NotificationData(title="t", message="m"))
        assert widget._darken_color("azul", 0.9) == "azul"
        assert widget._darken_color("", 0.9) == ""
        assert widget._darken_color("#FF6B00", 0.9) == "#e56000"
        assert widget._darken_color("#FFF", 0.9) == "#e5e5e5"
        assert widget._darken_color("#FF6B00AA", 0.9) == "#e56000"

    def test_primary_action_notification_survives_corrupt_accent(
        self, qt_app, monkeypatch
    ):
        from lib import notificationSystem

        monkeypatch.setitem(
            notificationSystem.NotificationWidget.COLORS["info"], "accent", "azul"
        )
        data = notificationSystem.NotificationData(
            title="Error",
            message="Detalle",
            actions=[
                notificationSystem.NotificationAction("Copiar", lambda: None, "primary")
            ],
        )
        widget = notificationSystem.NotificationWidget(data)
        assert widget is not None
