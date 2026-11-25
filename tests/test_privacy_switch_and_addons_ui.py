# -*- coding: utf-8 -*-
"""Interfaz: switch de privacidad y sidebar construido desde addons."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

pytest.importorskip("PyQt6.QtWidgets")

from PyQt6.QtWidgets import QApplication  # noqa: E402

import lib.i18n as i18n  # noqa: E402
from lib import pm_data  # noqa: E402

_APP = None


def _ensure_app():
    """Qt aborta el proceso si la QApplication se recolecta a mitad de test."""
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
def window(qt_app, isolated_store):
    import packagemaker as pm

    win = pm.PackageTodoGUI()
    yield win
    win.close()
    qt_app.processEvents()


# --- switch de privacidad ---------------------------------------------------
def test_switch_exists_and_defaults_to_enabled(window):
    assert window.conf_telemetry.isChecked()
    assert not window.conf_telemetry_endpoint.isChecked()


def test_switch_is_persisted_as_auto_report_errors(window):
    window.conf_telemetry.setChecked(False)
    window.conf_telemetry_endpoint.setChecked(True)
    values = window._collect_user_settings_from_form()
    assert values["auto_report_errors"] is False
    assert values["telemetry_enabled"] is True


def test_switch_reflects_stored_value(qt_app, isolated_store):
    isolated_store.set_user("auto_report_errors", False)
    isolated_store.save()
    import packagemaker as pm

    win = pm.PackageTodoGUI()
    try:
        assert not win.conf_telemetry.isChecked()
    finally:
        win.close()
        qt_app.processEvents()


def test_disabling_switch_stops_crash_capture(window, isolated_store):
    from lib import crash_capture

    window.conf_telemetry.setChecked(False)
    for key, value in window._collect_user_settings_from_form().items():
        isolated_store.set_user(key, value)
    isolated_store.save()
    assert crash_capture.auto_report_enabled() is False


def test_privacy_card_is_registered(window):
    panel = window.settings_panel
    assert "privacy" in panel._cards
    assert "conf_telemetry" in panel.widgets


# --- sidebar desde addons ---------------------------------------------------
def test_pages_follow_addon_order(window):
    ids = [addon.id for addon in window._addons]
    assert window.stack.count() == len(ids)
    for index, addon_id in enumerate(ids):
        assert window.stack.widget(index) is getattr(window, f"page_{addon_id}")


def test_buttons_exist_per_addon(window):
    buttons = window.sidebar_group.buttons()
    for addon in window._addons:
        assert getattr(window, f"btn_{addon.id}") in buttons


def test_description_comes_from_manifest(window):
    window.update_sidebar_description(window._addon_index["aide"])
    assert "AIDE" in window.sidebar_desc_text.toPlainText()


def test_switching_to_aide_shows_its_page(window):
    from lib.aide_page import AidePage

    window.switch_page(window._addon_index["aide"])
    assert isinstance(window.stack.currentWidget(), AidePage)


def test_report_page_is_still_reachable(window):
    assert window.page_report is not None
    window.switch_page(window._addon_index["report"])
    assert window.stack.currentWidget() is window.page_report


def test_missing_builder_yields_error_page_not_crash(window):
    from lib.addons_engine import Addon

    fake = Addon(
        id="fantasma",
        order=99,
        section="tools",
        label="sidebar.about",
        icon="about",
        builder="build_no_existe",
    )
    assert window._addon_error_page(fake, RuntimeError("boom")) is not None


def test_aide_module_is_importable_without_qt():
    # El CLI headless importa estos módulos sin PyQt6.
    source = (ROOT / "lib" / "aide_page.py").read_text(encoding="utf-8")
    assert "PYQT6_AVAILABLE" in source
    assert "class QWidget" in source


# --- página AIDE ------------------------------------------------------------
def test_page_disables_send_when_no_provider(qt_app, isolated_store):
    from lib.aide_page import AidePage

    page = AidePage()
    try:
        assert not page.send_button.isEnabled()
        assert page.status.text()
    finally:
        page.deleteLater()


def test_empty_prompt_does_not_call_backend(qt_app, isolated_store, monkeypatch):
    from lib import aide_backend
    from lib.aide_page import AidePage

    called = []
    monkeypatch.setattr(aide_backend, "ask_async", lambda *a, **k: called.append(True))
    page = AidePage()
    try:
        page.prompt_input.setPlainText("   ")
        page._on_send()
        assert called == []
        assert "Escribe" in page.status.text()
    finally:
        page.deleteLater()


def test_answer_is_shown_on_success(qt_app, isolated_store):
    from lib import aide_backend
    from lib.aide_page import AidePage

    page = AidePage()
    try:
        page._on_answer(
            aide_backend.Answer(True, text="respuesta", provider="copilot", model="m")
        )
        assert page.answer_view.toPlainText() == "respuesta"
        assert "copilot" in page.status.text()
    finally:
        page.deleteLater()


def test_error_is_shown_on_failure(qt_app, isolated_store):
    from lib import aide_backend
    from lib.aide_page import AidePage

    page = AidePage()
    try:
        page._on_answer(aide_backend.Answer(False, error="sin red"))
        assert "sin red" in page.status.text()
    finally:
        page.deleteLater()


def test_retranslate_keeps_labels(qt_app, isolated_store):
    from lib.aide_page import AidePage

    page = AidePage()
    try:
        page.retranslate()
        assert page.send_button.text()
        assert page.context_check.text()
    finally:
        page.deleteLater()


def test_provider_choice_is_saved(qt_app, isolated_store):
    from lib import aide_backend
    from lib.aide_page import AidePage

    page = AidePage()
    try:
        index = page.provider_combo.findData("openai")
        page.provider_combo.setCurrentIndex(index)
        assert aide_backend.get_settings()["provider"] == "openai"
    finally:
        page.deleteLater()


def test_answer_from_worker_thread_reaches_the_gui(qt_app, isolated_store, monkeypatch):
    """``ask_async`` responde desde otro hilo: debe entregarse por señal.

    Tocar widgets desde el hilo del backend es un fallo real (Qt no lo permite
    y aborta o corrompe el estado). Aquí se comprueba que el resultado llega.
    """
    from lib import aide_backend
    from lib.aide_page import AidePage

    monkeypatch.setattr(
        aide_backend,
        "ask",
        lambda *a, **k: aide_backend.Answer(True, text="desde el hilo", provider="p"),
    )
    page = AidePage()
    try:
        page.prompt_input.setPlainText("hola")
        page._on_send()
        for _ in range(200):
            qt_app.processEvents()
            if page.answer_view.toPlainText() == "desde el hilo":
                break
            import time

            time.sleep(0.01)
        assert page.answer_view.toPlainText() == "desde el hilo"
        assert page.send_button.isEnabled()
    finally:
        page.deleteLater()


def test_telemetry_url_makes_error_reporter_active(window, isolated_store):
    """El switch de "servidor propio" sólo sirve si la URL llega al reporter."""
    from lib import errorReporter

    window.conf_telemetry_endpoint.setChecked(True)
    window.conf_telemetry_url.setText("https://errores.example.com/report")
    for key, value in window._collect_user_settings_from_form().items():
        isolated_store.set_user(key, value)
    isolated_store.save()
    assert errorReporter.is_enabled() is True

    window.conf_telemetry_endpoint.setChecked(False)
    isolated_store.set_user("telemetry_enabled", False)
    isolated_store.save()
    assert errorReporter.is_enabled() is False


def test_telemetry_url_is_reloaded_into_the_form(qt_app, isolated_store):
    isolated_store.set_user("telemetry_endpoint", "https://mio.example.com/x")
    isolated_store.save()
    import packagemaker as pm

    win = pm.PackageTodoGUI()
    try:
        assert win.conf_telemetry_url.text() == "https://mio.example.com/x"
    finally:
        win.close()
        qt_app.processEvents()


def test_api_key_is_saved_but_never_shown(qt_app, isolated_store):
    from lib import aide_backend
    from lib.aide_page import AidePage

    page = AidePage()
    try:
        page.key_input.setText("sk-secreta")
        page._on_credentials_changed()
        assert aide_backend.get_settings()["api_key"] == "sk-secreta"
        assert page.key_input.text() == "", "la clave no debe quedar en el campo"
    finally:
        page.deleteLater()


def test_saving_endpoint_and_key_enables_openai(qt_app, isolated_store):
    from lib import aide_backend
    from lib.aide_page import AidePage

    page = AidePage()
    try:
        page.provider_combo.setCurrentIndex(page.provider_combo.findData("openai"))
        page.endpoint_input.setText("https://api.example.com/v1")
        page.key_input.setText("sk-1")
        page._on_credentials_changed()
        assert aide_backend.availability().ok is True
        assert page.send_button.isEnabled()
    finally:
        page.deleteLater()


def test_empty_endpoint_keeps_send_disabled(qt_app, isolated_store):
    from lib import aide_backend
    from lib.aide_page import AidePage

    page = AidePage()
    try:
        page.provider_combo.setCurrentIndex(page.provider_combo.findData("openai"))
        page.endpoint_input.setText("")
        page.key_input.setText("sk-1")
        page._on_credentials_changed()
        assert aide_backend.availability().reason == "no_endpoint"
        assert not page.send_button.isEnabled()
    finally:
        page.deleteLater()


def test_closed_window_does_not_write_into_the_next_store(qt_app, tmp_path):
    """Cerrar la ventana debe cancelar el autoguardado pendiente.

    Si el temporizador sobrevive, dispara más tarde y escribe los ajustes de la
    ventana cerrada en el almacén activo en ese momento.
    """
    import time

    from lib import pm_data
    import packagemaker as pm

    first = pm_data.PMDataStore(tmp_path / "uno" / "pm.data")
    first.set_user("base_dir", str(tmp_path / "uno" / "proyectos"))
    first.save()
    original = pm_data._store
    pm_data._store = first
    try:
        win = pm.PackageTodoGUI()
        win.conf_base_dir.setText(str(tmp_path / "ajena"))
        win.close()
        qt_app.processEvents()

        second = pm_data.PMDataStore(tmp_path / "dos" / "pm.data")
        second.set_user("base_dir", str(tmp_path / "dos" / "proyectos"))
        second.save()
        pm_data._store = second

        deadline = time.time() + 1.5
        while time.time() < deadline:
            qt_app.processEvents()
            time.sleep(0.01)

        assert second.get_user("base_dir") == str(tmp_path / "dos" / "proyectos")
    finally:
        pm_data._store = original


def test_pending_change_is_saved_on_close(qt_app, tmp_path):
    """El arreglo no debe perder el último ajuste: se guarda al cerrar."""
    import packagemaker as pm
    from lib import pm_data

    store = pm_data.PMDataStore(tmp_path / "pm.data")
    store.set_user("base_dir", str(tmp_path / "inicial"))
    store.save()
    original = pm_data._store
    pm_data._store = store
    try:
        win = pm.PackageTodoGUI()
        win.conf_base_dir.setText(str(tmp_path / "nuevo"))
        win.close()
        qt_app.processEvents()
        assert store.get_user("base_dir") == str(tmp_path / "nuevo")
    finally:
        pm_data._store = original
