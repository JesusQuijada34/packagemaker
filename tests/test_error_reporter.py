# -*- coding: utf-8 -*-
"""Mejora aprobada Q-001: reporte de errores opcional y desactivado por defecto.

Verifica con el código real que:

- sin consentimiento no se envía nada;
- el cuerpo no filtra rutas absolutas, el nombre de usuario ni credenciales;
- un fallo del emisor no se propaga;
- el ``excepthook`` encadenado conserva el comportamiento original.
"""

import sys
import threading
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture
def store(tmp_path, monkeypatch):
    from lib import pm_data

    data_store = pm_data.PMDataStore(path=tmp_path / "pm.data")
    monkeypatch.setattr(pm_data, "_store", data_store)
    return data_store


def _raise_and_capture():
    try:
        raise RuntimeError("boom")
    except RuntimeError:
        return sys.exc_info()


def test_disabled_by_default(store):
    from lib import errorReporter

    sent = []
    assert errorReporter.is_enabled() is False
    assert errorReporter.report_exception(*_raise_and_capture(), sender=sent.append) is False
    time.sleep(0.05)
    assert sent == []


def test_enabled_without_endpoint_stays_off(store):
    from lib import errorReporter

    store.set_user(errorReporter.SETTING_ENABLED, True)
    assert errorReporter.is_enabled() is False


def test_enabled_report_is_sanitized(store):
    from lib import errorReporter

    store.set_user(errorReporter.SETTING_ENABLED, True)
    store.set_user(errorReporter.SETTING_ENDPOINT, "https://example.invalid/report")

    captured = []
    done = threading.Event()

    def sender(endpoint, payload):
        captured.append((endpoint, payload))
        done.set()

    assert errorReporter.report_exception(*_raise_and_capture(), sender=sender) is True
    assert done.wait(2.0), "el envío no se programó"
    endpoint, payload = captured[0]
    assert endpoint == "https://example.invalid/report"
    assert payload["exception"] == "RuntimeError"
    assert payload["message"] == "boom"
    assert "<path>" in payload["traceback"]
    assert str(Path.home()) not in payload["traceback"]
    assert "password" not in payload["traceback"].lower()


def test_sender_failure_is_swallowed(store):
    from lib import errorReporter

    store.set_user(errorReporter.SETTING_ENABLED, True)
    store.set_user(errorReporter.SETTING_ENDPOINT, "https://example.invalid/report")
    done = threading.Event()

    def sender(endpoint, payload):
        done.set()
        raise OSError("sin red")

    assert errorReporter.report_exception(*_raise_and_capture(), sender=sender) is True
    assert done.wait(2.0)
    time.sleep(0.05)  # deja que el hilo consuma la excepción


def test_sanitize_redacts_paths_and_secrets():
    from lib import errorReporter

    text = (
        "Fallo en C:\\Users\\Jesus\\proyecto\\app.py y en /home/jesus/app.py "
        "con token=abc123 password: hunter2"
    )
    cleaned = errorReporter.sanitize(text, home="/home/jesus")
    assert "C:\\Users\\Jesus" not in cleaned
    assert "/home/jesus" not in cleaned
    assert "abc123" not in cleaned
    assert "hunter2" not in cleaned
    assert "<path>" in cleaned
    assert "<redacted>" in cleaned


def test_excepthook_chain_preserves_original(store):
    from lib import errorReporter

    calls = []
    original = sys.excepthook
    try:
        sys.excepthook = lambda *info: calls.append(info[0])
        errorReporter.install_excepthook(sender=lambda *a: None)
        exc_info = _raise_and_capture()
        sys.excepthook(*exc_info)
    finally:
        sys.excepthook = original
    assert calls == [RuntimeError]
