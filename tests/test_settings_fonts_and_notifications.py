# -*- coding: utf-8 -*-
"""Fase 3.3: fuente manual y notificaciones nativas.

Cubre con código real las dos piezas que el panel de tarjetas ya exponía pero
que no llegaban al usuario: la fuente elegida a mano no se guardaba ni se
aplicaba, y el ajuste de notificaciones no cambiaba el canal de los avisos.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture
def qt_app():
    QtWidgets = pytest.importorskip("PyQt6.QtWidgets")
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    yield app
    app.processEvents()


@pytest.fixture
def store(tmp_path, monkeypatch):
    from lib import pm_data

    data = pm_data.PMDataStore(tmp_path / "pm.data")
    monkeypatch.setattr(pm_data, "_store", data)
    return data


class TestManualFontSelection:
    def test_panel_lists_the_automatic_option_and_the_cache(self, qt_app):
        from lib.settings_panel import SettingsPanel

        panel = SettingsPanel(None, {"ui_font_family": ""})
        assert "" in panel._font_rows
        assert panel._font_rows[""].is_checked()

    def test_choosing_a_font_marks_only_that_row(self, qt_app):
        from lib.settings_panel import SettingsPanel

        panel = SettingsPanel(None, {"ui_font_family": ""})
        families = [key for key in panel._font_rows if key]
        if not families:
            pytest.skip("no hay fuentes en caché")
        chosen = []
        panel.fontChosen.connect(chosen.append)
        panel._font_rows[families[0]].chosen.emit(families[0])
        assert chosen == [families[0]]
        assert panel._font_rows[families[0]].is_checked()
        assert not panel._font_rows[""].is_checked()

    def test_entrypoint_persists_and_applies_the_choice(self):
        text = (ROOT / "packagemaker.py").read_text(encoding="utf-8")
        assert "fontChosen.connect(self._on_font_family_chosen)" in text
        start = text.index("def _on_font_family_chosen")
        body = text[start : text.index("def _on_config_language_changed")]
        assert 'set_user("ui_font_family"' in body
        assert "app.setFont(font)" in body

    def test_app_font_honours_the_stored_family(self, qt_app, store):
        import packagemaker as pm

        store.set_user("ui_font_family", "")
        automatic = pm.app_font()
        assert automatic is not None
        # Una familia inexistente cae al aspecto automático en vez de dejar la
        # interfaz con una tipografía que no existe en la máquina.
        store.set_user("ui_font_family", "Familia Que No Existe 12345")
        assert pm.app_font().family() == automatic.family()


class TestNativeNotifications:
    def test_reporter_uses_the_notifier_when_it_answers(self):
        from lib.report import Reporter

        shown = []
        dialogs = []

        class Bar:
            def showMessage(self, text):
                shown.append(text)

        reporter = Reporter(
            status_bar=Bar(),
            dialog_launcher=lambda *a, **k: dialogs.append((a, k)),
            notifier=lambda mode, title, message: shown.append((mode, title)) or True,
        )
        reporter.error("Fallo", "no se pudo compilar")

        assert dialogs == []
        assert shown[-1] == ("error", "Fallo")

    def test_reporter_falls_back_to_the_dialog(self):
        from lib.report import Reporter

        dialogs = []
        reporter = Reporter(
            dialog_launcher=lambda parent, title, message, mode="info": dialogs.append(
                (title, message, mode)
            ),
            notifier=lambda *a: False,
        )
        reporter.error("Fallo", "no se pudo compilar")
        assert dialogs == [("Fallo", "no se pudo compilar", "error")]

    def test_notifications_setting_controls_the_channel(self, qt_app, store):
        import packagemaker as pm

        calls = []
        monkeypatch_target = pm.PackageTodoGUI._notify_user
        store.set_user("notifications_enabled", False)
        assert monkeypatch_target(object(), "error", "Fallo", "detalle") is False
        store.set_user("notifications_enabled", True)

        import lib.notificationSystem as notifications

        manager = notifications.get_notification_manager()
        original = manager.notify
        manager.notify = lambda *a, **k: calls.append((a, k))
        try:
            delivered = monkeypatch_target(object(), "error", "Fallo", "detalle")
        finally:
            manager.notify = original

        assert delivered is True
        assert calls and calls[0][0][:2] == ("Fallo", "detalle")
