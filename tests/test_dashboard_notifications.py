# -*- coding: utf-8 -*-
"""El asistente de proyecto avisa con notificaciones, no con dialogos secos.

Fase 3.3 de ``bugs.txt``: sustituir las alertas rudimentarias por las
notificaciones animadas del sistema. Se comprueba que cada ruta de error del
asistente llama al aviso y que sigue habiendo respaldo si el manager falla.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pytest.importorskip("PyQt6.QtWidgets")

from PyQt6.QtWidgets import QApplication  # noqa: E402

import lib.pm_dashboard as dashboard  # noqa: E402
import lib.notificationSystem as notifications  # noqa: E402

_APP = None


def _app():
    global _APP
    if QApplication.instance() is None:
        _APP = QApplication([])
    return QApplication.instance()


@pytest.fixture
def wizard():
    _app()
    return dashboard.NewProjectWizard()


def _record(monkeypatch):
    calls = []
    monkeypatch.setattr(notifications, "warning", lambda t, m, **k: calls.append(("warning", t, m)))
    monkeypatch.setattr(notifications, "error", lambda t, m, **k: calls.append(("error", t, m)))
    return calls


def test_missing_fields_raise_a_warning_notification(wizard, monkeypatch):
    calls = _record(monkeypatch)
    wizard.input_publisher.setText("")
    wizard.create_project()
    assert calls and calls[0][0] == "warning"
    assert wizard.project_path is None


def test_invalid_name_raises_an_error_notification(wizard, monkeypatch):
    calls = _record(monkeypatch)
    wizard.input_publisher.setText("Acme")
    wizard.input_app.setText("app")
    wizard.input_name.setText("Nombre")
    wizard.input_version.setText("no-es-version")
    wizard.create_project()
    assert calls and calls[0][0] == "error"


def test_existing_folder_raises_a_warning(wizard, monkeypatch, tmp_path):
    calls = _record(monkeypatch)
    import lib.projectNameFormatter as formatter

    monkeypatch.setattr(
        formatter.ProjectNameFormatter,
        "format_project_folder",
        staticmethod(lambda *a, **k: "acme.app.v1.0.0-26.05-20.13-Knosthalij"),
    )
    (tmp_path / "acme.app.v1.0.0-26.05-20.13-Knosthalij").mkdir()
    wizard.input_publisher.setText("Acme")
    wizard.input_app.setText("app")
    wizard.input_name.setText("Nombre")
    wizard.input_location.setText(str(tmp_path))
    wizard.create_project()
    assert calls and calls[0][0] == "warning"
    assert "existe" in calls[0][2].lower()


def test_template_failure_raises_an_error_notification(wizard, monkeypatch, tmp_path):
    calls = _record(monkeypatch)

    def boom(*args, **kwargs):
        raise FileNotFoundError("sin plantillas")

    monkeypatch.setattr(
        "lib.makeselfEngine.template_engine.create_project_from_templates", boom
    )
    wizard.input_publisher.setText("Acme")
    wizard.input_app.setText("app")
    wizard.input_name.setText("Nombre")
    wizard.input_location.setText(str(tmp_path))
    wizard.create_project()
    assert calls and calls[0][0] == "error"
    assert "plantillas" in calls[0][2]


def test_notification_failure_falls_back_to_the_dialog(wizard, monkeypatch):
    seen = []

    def boom(*args, **kwargs):
        raise RuntimeError("sin pantalla")

    monkeypatch.setattr(notifications, "warning", boom)
    monkeypatch.setattr(
        dashboard.QMessageBox, "warning", lambda *a, **k: seen.append(a[1:])
    )
    wizard.input_publisher.setText("")
    wizard.create_project()
    assert seen, "sin notificacion debe salir el dialogo de respaldo"
