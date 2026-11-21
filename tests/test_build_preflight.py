# -*- coding: utf-8 -*-
"""Regresiones de las pruebas previas y de la inyección del .env (Fase 1.4)."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_discover_scripts_finds_root_and_source(tmp_path):
    from lib.build_preflight import discover_scripts

    (tmp_path / "app.py").write_text("print(1)\n", encoding="utf-8")
    (tmp_path / "source").mkdir()
    (tmp_path / "source" / "helper.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "venv").mkdir()
    (tmp_path / "venv" / "ignored.py").write_text("x = 1\n", encoding="utf-8")

    names = [p.name for p in discover_scripts(tmp_path)]
    assert names == ["app.py", "helper.py"]


def test_syntax_check_passes_on_valid_scripts(tmp_path):
    from lib.build_preflight import check_syntax

    script = tmp_path / "ok.py"
    script.write_text("def f():\n    return 1\n", encoding="utf-8")
    result = check_syntax([script])
    assert result.ok


def test_syntax_check_reports_line_and_message(tmp_path):
    from lib.build_preflight import check_syntax

    script = tmp_path / "broken.py"
    script.write_text("def f(:\n", encoding="utf-8")
    result = check_syntax([script])
    assert not result.ok
    assert "broken.py:1" in result.detail


def test_syntax_check_without_scripts_is_not_a_failure(tmp_path):
    from lib.build_preflight import check_syntax

    assert check_syntax([]).ok


def test_offscreen_check_detects_import_errors(tmp_path):
    from lib.build_preflight import check_offscreen

    script = tmp_path / "boom.py"
    script.write_text("import modulo_que_no_existe\n", encoding="utf-8")
    result = check_offscreen([script], timeout=30)
    assert not result.ok
    assert "boom.py" in result.detail


def test_offscreen_check_accepts_clean_script(tmp_path):
    from lib.build_preflight import check_offscreen

    script = tmp_path / "fine.py"
    script.write_text("print('ok')\n", encoding="utf-8")
    assert check_offscreen([script], timeout=30).ok


def test_preflight_report_aggregates_failures(tmp_path):
    from lib.build_preflight import run_preflight

    (tmp_path / "bad.py").write_text("def f(:\n", encoding="utf-8")
    report = run_preflight(tmp_path, offscreen=False)
    assert not report.ok
    assert len(report.failures) == 1
    assert report.summary()


def test_env_file_found_in_root_and_config(tmp_path):
    from lib.build_preflight import find_env_file

    assert find_env_file(tmp_path) is None
    (tmp_path / "config").mkdir()
    env = tmp_path / "config" / ".env"
    env.write_text("A=1\n", encoding="utf-8")
    assert find_env_file(tmp_path) == env


def test_parse_env_ignores_comments_and_quotes(tmp_path):
    from lib.build_preflight import parse_env_file

    env = tmp_path / ".env"
    env.write_text(
        "# comentario\n\nA=1\nB=\"dos\"\nexport C='tres'\nSIN_IGUAL\n",
        encoding="utf-8",
    )
    assert parse_env_file(env) == {"A": "1", "B": "dos", "C": "tres"}


def test_global_payload_carries_every_variable():
    from lib.build_preflight import INJECTION_GLOBAL, build_env_payload

    payload = build_env_payload({"A": "1", "B": "2"}, INJECTION_GLOBAL)
    assert payload["mode"] == "global"
    assert payload["environment"] == {"A": "1", "B": "2"}


def test_custom_payload_only_carries_selected_variables():
    from lib.build_preflight import INJECTION_CUSTOM, build_env_payload

    payload = build_env_payload({"A": "1", "B": "2"}, INJECTION_CUSTOM, ["B"])
    assert payload["environment"] == {"B": "2"}


def test_unknown_injection_mode_is_rejected():
    from lib.build_preflight import build_env_payload

    with pytest.raises(ValueError):
        build_env_payload({"A": "1"}, "inventado")


def test_build_thread_persists_env_payload_into_settings(tmp_path):
    from lib.BuildThread import BuildThread

    thread = BuildThread(
        "acme", "demo", "1.0", "Danenone",
        env_payload={"mode": "global", "environment": {"TOKEN": "x"}},
    )
    settings = tmp_path / "config" / "settings.json"
    settings.parent.mkdir()
    settings.write_text(json.dumps({"build": {"scripts": ["app"]}}), encoding="utf-8")

    thread._persist_env_payload(tmp_path)

    data = json.loads(settings.read_text(encoding="utf-8"))
    assert data["environment"] == {"mode": "global", "environment": {"TOKEN": "x"}}
    assert data["build"] == {"scripts": ["app"]}


def test_build_thread_preflight_can_be_disabled():
    from lib.BuildThread import BuildThread

    assert BuildThread("a", "b", "1.0", "Danenone", preflight=False).preflight is False
    assert BuildThread("a", "b", "1.0", "Danenone").preflight is True


def test_env_dialog_rows_expose_key_and_weight():
    from lib.env_injection_dialog import env_rows

    rows = env_rows(["API_KEY", "DEBUG"])
    assert [row["key"] for row in rows] == ["API_KEY", "DEBUG"]
    assert all(row["checked"] for row in rows)
    assert all(row["weight"] > 0 for row in rows)


def test_app_icon_prefers_app_directory(tmp_path):
    from lib.env_injection_dialog import app_icon_for

    (tmp_path / "app").mkdir()
    icon = tmp_path / "app" / "demo-icon.ico"
    icon.write_bytes(b"\x00")
    assert app_icon_for(tmp_path, "demo") == icon


def test_env_dialog_returns_global_payload(tmp_path):
    pytest.importorskip("PyQt6.QtWidgets")
    from PyQt6.QtWidgets import QApplication, QWidget

    app = QApplication.instance() or QApplication([])
    assert app is not None

    from lib.env_injection_dialog import EnvInjectionDialog

    parent = QWidget()
    dialog = EnvInjectionDialog(parent, {"A": "1", "B": "2"}, tmp_path, "demo")
    dialog._confirm()
    payload = dialog.payload()
    assert payload["mode"] == "global"
    assert payload["environment"] == {"A": "1", "B": "2"}
    dialog.deleteLater()
    parent.deleteLater()


def test_env_dialog_custom_mode_filters_variables(tmp_path):
    pytest.importorskip("PyQt6.QtWidgets")
    from PyQt6.QtWidgets import QApplication, QWidget

    app = QApplication.instance() or QApplication([])
    assert app is not None

    from lib.env_injection_dialog import EnvInjectionDialog

    parent = QWidget()
    dialog = EnvInjectionDialog(parent, {"A": "1", "B": "2"}, tmp_path, "demo")
    dialog._custom_radio.setChecked(True)
    dialog._checks["A"].setChecked(False)
    dialog._confirm()
    payload = dialog.payload()
    assert payload["mode"] == "custom"
    assert payload["environment"] == {"B": "2"}
    dialog.deleteLater()
    parent.deleteLater()


def test_build_flow_asks_env_only_for_external_projects():
    source = (ROOT / "packagemaker.py").read_text(encoding="utf-8")
    start = source.index("def _ask_env_injection")
    body = source[start : source.index("def _build_controls")]
    assert "if not custom_path:" in body
    assert "find_env_file" in body
    assert "ask_env_injection" in body


def test_build_thread_runs_preflight_before_compiling():
    source = (ROOT / "lib" / "BuildThread.py").read_text(encoding="utf-8")
    assert source.index("run_preflight") < source.index("compiler = FlangCompiler(")
