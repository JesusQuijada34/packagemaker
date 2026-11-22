# -*- coding: utf-8 -*-
"""Regresiones de ``scripts/oh_chat.py`` (control de OpenHands por terminal)."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import oh_chat  # noqa: E402


@pytest.fixture(autouse=True)
def _api_key(monkeypatch):
    monkeypatch.setenv("OPENHANDS_API_KEY", "clave-de-prueba")


def test_api_key_prefers_the_cloud_variable(monkeypatch):
    monkeypatch.setenv("OPENHANDS_CLOUD_API_KEY", "nube")
    assert oh_chat.api_key() == "nube"
    monkeypatch.delenv("OPENHANDS_CLOUD_API_KEY")
    assert oh_chat.api_key() == "clave-de-prueba"
    monkeypatch.delenv("OPENHANDS_API_KEY")
    with pytest.raises(oh_chat.ApiError):
        oh_chat.api_key()


def test_send_message_posts_the_expected_payload(monkeypatch):
    calls = []

    def fake_cloud(path, *, method="GET", payload=None):
        calls.append((path, method, payload))
        return None

    monkeypatch.setattr(oh_chat, "cloud", fake_cloud)
    oh_chat.send_message("abc", "hola mundo")

    path, method, payload = calls[0]
    assert path == "/api/v1/app-conversations/abc/send-message"
    assert method == "POST"
    assert payload == {
        "role": "user",
        "content": [{"type": "text", "text": "hola mundo"}],
        "run": True,
    }


def test_agent_server_rejects_a_conversation_without_runtime(monkeypatch):
    with pytest.raises(oh_chat.ApiError) as error:
        oh_chat.agent_server({"sandbox_status": "PAUSED"})
    assert "PAUSED" in str(error.value)


def test_messages_flattens_text_blocks(monkeypatch):
    monkeypatch.setattr(
        oh_chat,
        "conversation_record",
        lambda _id: {
            "conversation_url": "https://sandbox/api/conversations/abc",
            "session_api_key": "secreta",
        },
    )

    def fake_request(url, **kwargs):
        assert kwargs["headers"]["X-Session-API-Key"] == "secreta"
        assert "kind=MessageEvent" in url
        return {
            "items": [
                {
                    "source": "agent",
                    "timestamp": "t1",
                    "llm_message": {
                        "role": "assistant",
                        "content": [
                            {"type": "text", "text": "primera "},
                            {"type": "text", "text": "parte"},
                        ],
                    },
                },
                {
                    "source": "agent",
                    "timestamp": "t2",
                    "llm_message": {"role": "assistant", "content": [{"type": "image"}]},
                },
            ]
        }

    monkeypatch.setattr(oh_chat, "_request", fake_request)
    result = oh_chat.messages("abc", 10)

    assert len(result) == 1
    assert result[0]["text"] == "primera parte"
    assert result[0]["role"] == "assistant"


def test_resolve_conversation_refuses_to_guess_between_several(monkeypatch, capsys):
    monkeypatch.delenv("OH_CONVERSATION_ID", raising=False)
    monkeypatch.setattr(
        oh_chat,
        "cloud",
        lambda path, **kwargs: {
            "items": [
                {"id": "uno", "execution_status": "running", "title": "a"},
                {"id": "dos", "execution_status": "running", "title": "b"},
            ]
        },
    )
    with pytest.raises(oh_chat.ApiError):
        oh_chat.resolve_conversation(None)
    assert "uno" in capsys.readouterr().err


def test_resolve_conversation_uses_the_environment(monkeypatch):
    monkeypatch.setenv("OH_CONVERSATION_ID", "fija")
    assert oh_chat.resolve_conversation(None) == "fija"


def test_main_reports_api_errors_with_exit_code_one(monkeypatch, capsys):
    def boom(*args, **kwargs):
        raise oh_chat.ApiError("sin clave")

    monkeypatch.setattr(oh_chat, "resolve_conversation", boom)
    assert oh_chat.main(["read"]) == 1
    assert "sin clave" in capsys.readouterr().err


def test_status_summarises_the_record(monkeypatch):
    monkeypatch.setattr(
        oh_chat,
        "conversation_record",
        lambda _id: {
            "id": "abc",
            "title": "tarea",
            "sandbox_status": "RUNNING",
            "execution_status": "idle",
            "selected_branch": "main",
            "selected_repository": "owner/repo",
            "conversation_ui_url": "https://panel/canvas/conversations/abc",
        },
    )
    summary = oh_chat.status("abc")
    assert summary["execution"] == "idle"
    assert summary["repo"] == "owner/repo"
