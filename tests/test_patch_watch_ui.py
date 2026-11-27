# -*- coding: utf-8 -*-
"""Vigilancia de parches en la ventana real (Q-013/F-006, primera etapa).

Comprueba el cableado: la tarjeta de Configuración, el guardado del ajuste, el
hilo daemon que no bloquea la interfaz y el aviso en la barra de estado. La
red se sustituye por un ``check_for_patch`` falso: estos tests nunca salen del
equipo.
"""

import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

pytest.importorskip("PyQt6.QtWidgets")

from PyQt6.QtWidgets import QApplication, QCheckBox, QLabel, QPushButton  # noqa: E402

import lib.i18n as i18n  # noqa: E402
from lib import patch_watch, pm_data  # noqa: E402

_APP = None


def _ensure_app():
    global _APP
    if _APP is None:
        _APP = QApplication.instance() or QApplication(sys.argv)
    return _APP


@pytest.fixture(scope="session")
def qt_app():
    app = _ensure_app()
    i18n.i18n.initialize(app, "es")
    return app


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr(pm_data, "_data_dir", lambda: tmp_path)
    store = pm_data.PMDataStore(path=tmp_path / "pm.data")
    monkeypatch.setattr(pm_data, "_store", store)
    return store


@pytest.fixture()
def window(qt_app, isolated_store, monkeypatch):
    # El conftest desactiva la vigilancia para toda la suite; aquí se prueba,
    # así que se quita el interruptor y se sustituye la red.
    monkeypatch.delenv(patch_watch.DISABLE_ENV, raising=False)
    import packagemaker as pm

    win = pm.PackageTodoGUI()
    yield win
    win.close()
    qt_app.processEvents()


def _status(kind, **kwargs):
    return patch_watch.PatchStatus(kind, **kwargs)


def _pump(app, seconds=0.3):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        app.processEvents()
        time.sleep(0.01)


def test_card_exposes_the_patch_controls(window):
    assert isinstance(window.conf_patch_check, QCheckBox)
    assert isinstance(window.conf_patch_status, QLabel)
    button = window.settings_panel.widgets["conf_patch_check_now"]
    assert isinstance(button, QPushButton)
    assert button.text()
    # Activado por defecto: el propietario pidió el aviso en segundo plano.
    assert window.conf_patch_check.isChecked() is True


def test_toggle_is_saved_with_the_rest_of_the_settings(window, isolated_store):
    window.conf_patch_check.setChecked(False)
    values = window._collect_user_settings_from_form()
    assert values["patch_check_enabled"] is False
    window._save_app_config_compact(quiet=True)
    assert isolated_store.get_user("patch_check_enabled") is False


def test_manual_check_updates_the_card_and_the_status_bar(window, monkeypatch):
    monkeypatch.setattr(
        patch_watch,
        "check_for_patch",
        lambda **kwargs: _status(
            patch_watch.STATUS_AVAILABLE,
            local="1" * 40,
            remote="abcdef1234",
            message="fix: parche de seguridad",
        ),
    )
    window._check_patches_now()
    window._patch_thread.join(timeout=5)
    _pump(_ensure_app())

    assert window._patch_status.kind == patch_watch.STATUS_AVAILABLE
    assert "abcdef1" in window.conf_patch_status.text()
    assert "parche de seguridad" in window.conf_patch_status.text()
    assert window.status_bar.currentMessage()


def test_patch_available_uses_the_notification_when_enabled(window, monkeypatch):
    calls = []
    monkeypatch.setattr(window, "_notify_user", lambda *a, **k: calls.append(a) or True)
    window._on_patch_checked(
        _status(patch_watch.STATUS_AVAILABLE, remote="f" * 40, message="fix: algo")
    )
    assert calls and calls[0][0] == "info"

    calls.clear()
    window._on_patch_checked(_status(patch_watch.STATUS_UP_TO_DATE, remote="f" * 40))
    assert calls == []


def test_startup_check_respects_the_interval(window, monkeypatch):
    monkeypatch.setattr(patch_watch, "should_check", lambda *a, **k: False)
    window._patch_thread = None
    window._start_patch_watch()
    assert window._patch_thread is None


def test_environment_switch_blocks_every_check(window, monkeypatch):
    monkeypatch.setenv(patch_watch.DISABLE_ENV, "0")
    window._patch_thread = None
    window._start_patch_watch(force=True)
    assert window._patch_thread is None


def test_worker_never_raises_on_unexpected_errors(window, monkeypatch):
    def boom(**kwargs):
        raise RuntimeError("fallo inesperado")

    monkeypatch.setattr(patch_watch, "check_for_patch", boom)
    window._patch_watch_worker(True, "unrestricted")
    _pump(_ensure_app())
    assert window._patch_status.kind == patch_watch.STATUS_OFFLINE
    assert "fallo inesperado" in window._patch_status.detail


def test_status_text_is_translated(window):
    i18n.i18n.load_translation("es")
    spanish = window._patch_status_text(_status(patch_watch.STATUS_UP_TO_DATE))
    i18n.i18n.load_translation("en")
    english = window._patch_status_text(_status(patch_watch.STATUS_UP_TO_DATE))
    i18n.i18n.load_translation("es")
    assert spanish and english and spanish != english

    available = window._patch_status_text(
        _status(patch_watch.STATUS_AVAILABLE, remote="0123456789", message="fix: x")
    )
    assert "0123456" in available and "fix: x" in available
    assert window._patch_status_text(_status(patch_watch.STATUS_METERED))


def test_language_switch_rebuilds_the_patch_status(window, monkeypatch):
    window._on_patch_checked(_status(patch_watch.STATUS_UP_TO_DATE))
    i18n.i18n.load_translation("es")
    window.apply_ui_language()
    spanish = window.conf_patch_status.text()
    i18n.i18n.load_translation("en")
    window.apply_ui_language()
    english = window.conf_patch_status.text()
    i18n.i18n.load_translation("es")
    window.apply_ui_language()
    assert spanish != english
