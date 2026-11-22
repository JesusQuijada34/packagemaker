# -*- coding: utf-8 -*-
"""Regresiones de ``scripts/watch_main.py`` (vigilancia de ``main``)."""

import io
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import watch_main  # noqa: E402


def _payload(sha="a" * 40, message="fix: algo", author="openhands"):
    return {
        "sha": sha,
        "commit": {
            "message": message,
            "author": {"name": author},
            "committer": {"date": "2026-11-22T00:00:00Z"},
        },
    }


class _FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_latest_commit_parses_the_api_shape(monkeypatch):
    seen = {}

    def fake_urlopen(request, timeout=None):
        seen["url"] = request.full_url
        seen["accept"] = request.get_header("Accept")
        return _FakeResponse(json.dumps(_payload()).encode())

    monkeypatch.setattr(watch_main.urllib.request, "urlopen", fake_urlopen)

    commit = watch_main.latest_commit("owner/repo", "main")

    assert commit["short"] == "a" * 7
    assert commit["message"] == "fix: algo"
    assert "/repos/owner/repo/commits/main" in seen["url"]
    assert seen["accept"] == "application/vnd.github+json"


def test_token_prefers_the_github_token_variable(monkeypatch):
    for name in watch_main.TOKEN_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("OH_GIT_CREDENTIAL_ACCESS_TOKEN_GITHUB", "segundo")
    assert watch_main.token() == "segundo"
    monkeypatch.setenv("GITHUB_TOKEN", "primero")
    assert watch_main.token() == "primero"


def test_workflow_status_degrades_when_actions_is_unavailable(monkeypatch):
    import urllib.error

    def fake_urlopen(request, timeout=None):
        raise urllib.error.HTTPError(request.full_url, 404, "Not Found", None, None)

    monkeypatch.setattr(watch_main.urllib.request, "urlopen", fake_urlopen)
    assert watch_main.workflow_status("owner/repo", "main") == []


def test_describe_includes_commit_and_ci_lines():
    state = {
        "commit": {
            "sha": "b" * 40,
            "short": "bbbbbbb",
            "message": "docs: algo",
            "author": "openhands",
            "date": "2026-11-22T00:00:00Z",
        },
        "runs": [{"name": "Tests", "status": "completed", "conclusion": "success", "sha": "bbbbbbb"}],
        "items": {"issues": 2, "pulls": 1},
    }
    text = watch_main.describe(state)
    assert "bbbbbbb" in text and "docs: algo" in text
    assert "CI Tests: completed/success" in text
    assert "2 issues, 1 PRs" in text


def test_main_once_returns_zero_on_success(monkeypatch, capsys):
    monkeypatch.setattr(watch_main, "report", lambda repo, branch, show_items: {
        "commit": {
            "sha": "c" * 40,
            "short": "ccccccc",
            "message": "chore: algo",
            "author": "openhands",
            "date": "2026-11-22T00:00:00Z",
        }
    })
    assert watch_main.main(["--once"]) == 0
    assert "ccccccc" in capsys.readouterr().out


def test_main_reports_network_errors_with_exit_code_one(monkeypatch, capsys):
    def boom(*args, **kwargs):
        raise TimeoutError("sin red")

    monkeypatch.setattr(watch_main, "report", boom)
    assert watch_main.main(["--once"]) == 1
    assert "red" in capsys.readouterr().err.lower()
