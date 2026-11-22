# -*- coding: utf-8 -*-
"""Regresiones de ``scripts/watch_and_act.py``."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import watch_and_act  # noqa: E402


def _commit(sha="a" * 40, message="fix: algo"):
    return {
        "sha": sha,
        "short": sha[:7],
        "message": message,
        "author": "openhands",
        "date": "2026-11-22T00:00:00Z",
    }


@pytest.fixture
def state_file(tmp_path, monkeypatch):
    path = tmp_path / "watch.json"
    monkeypatch.setattr(watch_and_act, "STATE_PATH", path)
    return path


def test_state_round_trips(state_file):
    assert watch_and_act.load_state() == {}
    watch_and_act.save_state({"sha": "x" * 40})
    assert watch_and_act.load_state()["sha"] == "x" * 40


def test_corrupt_state_is_treated_as_empty(state_file):
    state_file.write_text("{no es json", encoding="utf-8")
    assert watch_and_act.load_state() == {}


def test_actions_run_once_per_commit(state_file, monkeypatch):
    acted = []
    monkeypatch.setattr(watch_and_act.watch_main, "latest_commit", lambda r, b: _commit())
    monkeypatch.setattr(watch_and_act.watch_main, "notify", lambda *a: None)

    def counting_tests(root):
        acted.append(root)
        return 0, "751 passed"

    monkeypatch.setattr(watch_and_act, "run_tests", counting_tests)

    assert watch_and_act.main(["--once", "--run-tests", "--root", str(ROOT)]) == 0
    assert len(acted) == 1
    assert json.loads(state_file.read_text(encoding="utf-8"))["sha"] == "a" * 40

    assert watch_and_act.main(["--once", "--run-tests", "--root", str(ROOT)]) == 0
    assert len(acted) == 1, "el mismo commit no debe relanzar la suite"


def test_failing_suite_triggers_a_notification(state_file, monkeypatch):
    notified = []
    monkeypatch.setattr(watch_and_act.watch_main, "latest_commit", lambda r, b: _commit())
    monkeypatch.setattr(watch_and_act.watch_main, "notify", lambda t, b: notified.append(t))
    monkeypatch.setattr(watch_and_act, "run_tests", lambda root: (1, "3 failed, 748 passed"))

    assert watch_and_act.main(["--once", "--run-tests"]) == 0
    assert notified and "tests" in notified[0]


def test_ask_sends_the_prompt_to_the_resolved_conversation(state_file, monkeypatch):
    sent = []
    monkeypatch.setattr(watch_and_act.watch_main, "latest_commit", lambda r, b: _commit())
    monkeypatch.setattr(watch_and_act.oh_chat, "resolve_conversation", lambda explicit: "conv-1")
    monkeypatch.setattr(
        watch_and_act.oh_chat, "send_message", lambda cid, text, run=True: sent.append((cid, text))
    )

    assert watch_and_act.main(["--once", "--ask", "continua con bugs.md"]) == 0
    assert sent == [("conv-1", "continua con bugs.md")]


def test_ask_failure_does_not_kill_the_watcher(state_file, monkeypatch, capsys):
    monkeypatch.setattr(watch_and_act.watch_main, "latest_commit", lambda r, b: _commit())

    def boom(explicit):
        raise watch_and_act.oh_chat.ApiError("sin clave")

    monkeypatch.setattr(watch_and_act.oh_chat, "resolve_conversation", boom)
    assert watch_and_act.main(["--once", "--ask", "hola"]) == 0
    assert "no se pudo enviar" in capsys.readouterr().err


def test_network_error_returns_one(state_file, monkeypatch, capsys):
    def boom(repo, branch):
        raise TimeoutError("sin red")

    monkeypatch.setattr(watch_and_act.watch_main, "latest_commit", boom)
    assert watch_and_act.main(["--once"]) == 1
    assert "red" in capsys.readouterr().err.lower()
