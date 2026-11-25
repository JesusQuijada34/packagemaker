# -*- coding: utf-8 -*-
"""UI de la página de Reportes: formulario, validación y envío simulado."""

import sys
import unittest
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

pytest.importorskip("PyQt6.QtWidgets")

from PyQt6.QtWidgets import QApplication  # noqa: E402

from lib import github_issue_reporter, report_queue  # noqa: E402
from lib.report_page import ReportPage  # noqa: E402

_APP = None


def _ensure_app():
    global _APP
    if _APP is None:
        _APP = QApplication.instance() or QApplication(sys.argv)
    return _APP


@pytest.fixture()
def page():
    _ensure_app()
    widget = ReportPage()
    yield widget
    widget.deleteLater()


@pytest.fixture()
def isolated_queue(tmp_path, monkeypatch):
    path = tmp_path / "queue.json"
    monkeypatch.setattr(report_queue, "_queue_path", lambda: path)
    return path


def test_page_builds_with_all_sections(page):
    assert page.title_input is not None
    assert page.description_input is not None
    assert page.kind_combo.count() == 3
    assert page.send_btn.text()
    assert "PackageMaker" in page.env_label.text()


def test_empty_form_is_rejected(page):
    assert page.build_report() is None
    assert page.feedback.text(), "debe explicar qué falta"


def test_form_without_description_is_rejected(page):
    page.title_input.setText("Algo falla")
    assert page.build_report() is None


def test_valid_form_builds_report(page):
    page.title_input.setText("Algo falla")
    page.description_input.setPlainText("Paso X y ocurre Y")
    page.include_logs.setChecked(False)
    report = page.build_report()
    assert report is not None
    assert report.title == "Algo falla"
    assert report.kind == "bug"
    assert report.environment is not None


def test_kind_combo_selects_report_kind(page):
    page.kind_combo.setCurrentIndex(2)
    page.title_input.setText("Idea")
    page.description_input.setPlainText("Podría añadirse…")
    report = page.build_report()
    assert report.kind == "suggestion"


def test_send_without_session_does_not_call_api(page, isolated_queue, monkeypatch):
    calls = []
    monkeypatch.setattr(github_issue_reporter, "has_session", lambda: False)
    monkeypatch.setattr(
        github_issue_reporter, "create_issue", lambda *a, **k: calls.append(1)
    )
    page.title_input.setText("t")
    page.description_input.setPlainText("d")
    page._on_send_clicked()
    assert calls == []
    assert page.feedback.text()


def test_send_success_clears_form(page, isolated_queue, monkeypatch):
    monkeypatch.setattr(github_issue_reporter, "has_session", lambda: True)
    monkeypatch.setattr(
        github_issue_reporter,
        "create_issue",
        lambda report, **k: github_issue_reporter.Result(
            ok=True, issue_number=15, url="https://example/15"
        ),
    )
    page.title_input.setText("t")
    page.description_input.setPlainText("d")
    page._on_send_clicked()
    assert page.title_input.text() == ""
    assert "15" in page.feedback.text()


def test_failed_send_is_queued(page, isolated_queue, monkeypatch):
    monkeypatch.setattr(github_issue_reporter, "has_session", lambda: True)
    monkeypatch.setattr(
        github_issue_reporter,
        "create_issue",
        lambda report, **k: github_issue_reporter.Result(ok=False, error="sin red"),
    )
    page.title_input.setText("t")
    page.description_input.setPlainText("d")
    page._on_send_clicked()
    assert report_queue.count() == 1


def test_resend_queue_uses_real_sender(page, isolated_queue, monkeypatch):
    report_queue.enqueue({"title": "pendiente", "description": "d"})
    sent = []

    def _fake_create(report, **kwargs):
        sent.append(report.title)
        return github_issue_reporter.Result(ok=True, issue_number=3)

    monkeypatch.setattr(github_issue_reporter, "has_session", lambda: True)
    monkeypatch.setattr(github_issue_reporter, "create_issue", _fake_create)
    page._on_resend_queue()
    assert sent == ["pendiente"]
    assert report_queue.count() == 0


def test_retranslate_keeps_state(page):
    page.title_input.setText("texto escrito")
    page.retranslate()
    assert page.title_input.text() == "texto escrito"


if __name__ == "__main__":
    unittest.main()
