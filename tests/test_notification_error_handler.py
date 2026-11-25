# -*- coding: utf-8 -*-
"""La notificación de error copia al portapapeles aunque falte ``pyperclip``.

``pyperclip`` no es una dependencia del proyecto. Antes se importaba al llamar
a ``error_handler``, así que la propia notificación de error lanzaba
``ImportError`` (y desde un slot de Qt habría abortado la aplicación).
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lib.notificationSystem as notifications


class _Manager:
    def __init__(self):
        self.calls = []

    def error(self, title, message, duration=0, actions=None, **kwargs):
        self.calls.append((title, message, actions))
        return "notification"


class _Clipboard:
    def __init__(self):
        self.text = None

    def setText(self, text):
        self.text = text


def _prepare(monkeypatch, clipboard):
    manager = _Manager()
    monkeypatch.setattr(notifications, "get_notification_manager", lambda: manager)
    monkeypatch.setattr(notifications, "QApplication", type("_App", (), {"clipboard": staticmethod(lambda: clipboard)}))
    monkeypatch.setitem(sys.modules, "pyperclip", None)
    confirmations = []
    monkeypatch.setattr(notifications, "success", lambda *a, **k: confirmations.append((a, k)))
    return manager, confirmations


def test_error_handler_uses_the_qt_clipboard_without_pyperclip(monkeypatch):
    clipboard = _Clipboard()
    manager, confirmations = _prepare(monkeypatch, clipboard)

    widget = notifications.error_handler("Error", "fallo", "detalle")
    assert widget == "notification"

    action = manager.calls[0][2][0]
    action.callback()

    assert clipboard.text == "fallo\ndetalle"
    assert confirmations


def test_error_handler_survives_a_missing_clipboard(monkeypatch):
    manager, confirmations = _prepare(monkeypatch, None)

    notifications.error_handler("Error", "fallo")
    action = manager.calls[0][2][0]
    action.callback()

    assert confirmations == []
