# -*- coding: utf-8 -*-
"""Página de Reportes: envía bugs al repositorio con la cuenta del usuario.

El usuario describe el problema, adjunta lo que quiera y pulsa Enviar. La
aplicación añade el entorno (SO, versión, commit, Python, Qt…) y publica un
issue en GitHub firmado con el token que ya está autenticado, así que no hay
que escribir reportes a mano en el navegador.

Los fallos que la aplicación captura sola no pasan por aquí: se envían (o se
encolan) desde ``lib/crash_capture.py``. Esta página además muestra esa cola
para que el usuario decida si la manda.

Todo el color sale de ``lib/design_tokens`` y todo el texto de ``tr()``.
"""

from __future__ import annotations

import html
from typing import List, Optional, Tuple

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QCheckBox,
        QComboBox,
        QFrame,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPlainTextEdit,
        QPushButton,
        QScrollArea,
        QVBoxLayout,
        QWidget,
    )

    PYQT6_AVAILABLE = True
except ImportError:  # pragma: no cover - entorno sin Qt (CLI headless)
    PYQT6_AVAILABLE = False

    # El CLI headless importa ``packagemaker`` sin PyQt6: la clase debe poder
    # definirse igualmente, así que hereda de ``object`` en ese caso.
    class QWidget:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            pass

from lib import crash_capture, github_issue_reporter, report_queue, report_telemetry
from lib.design_tokens import (
    ACCENT,
    BORDER,
    CONTENT_PADDING,
    DANGER_TEXT,
    DIVIDER,
    TEXT,
    TEXT_DIM,
    TEXT_SOFT,
    WARNING,
    card_qss,
    input_qss,
    scrollbar_qss,
    secondary_button_qss,
)
from lib.page_action_bar import install_page_action_bar, make_action_button

from lib.i18n import tr


def _t(key: str, **kwargs) -> str:
    """Traduce y sustituye marcadores (``tr`` no acepta kwargs)."""
    text = tr(key)
    return text.format(**kwargs) if kwargs else text


def _environment_html(markdown: str) -> str:
    """Convierte la tabla markdown del entorno en una tabla HTML para ``QLabel``.

    ``environment_markdown()`` sirve para pegar el entorno en un issue, pero en
    la página se mostraba con los pipes en crudo. Qt renderiza un subconjunto de
    HTML: se construye una tabla de dos columnas con la misma información.
    """
    rows: List[List[str]] = []
    for raw in markdown.splitlines():
        line = raw.strip()
        if not (line.startswith("|") and line.endswith("|")):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if cells and all(set(cell) <= {"-", ":", " "} for cell in cells):
            continue
        if cells:
            rows.append(cells)
    if not rows:
        return ""

    width = max(len(row) for row in rows)
    parts = ["<table width='100%' cellspacing='0' cellpadding='6'>"]
    for index, row in enumerate(rows):
        cells = row + [""] * (width - len(row))
        parts.append("<tr>")
        for cell_index, cell in enumerate(cells):
            if index == 0:
                style = (
                    f"color:{TEXT_DIM};font-size:11px;font-weight:600;"
                    f"border-bottom:1px solid {BORDER};text-align:left;"
                )
            else:
                color = TEXT if cell_index == 0 else TEXT_SOFT
                weight = "600" if cell_index == 0 else "400"
                style = (
                    f"color:{color};font-size:12px;font-weight:{weight};"
                    f"border-bottom:1px solid {DIVIDER};text-align:left;"
                )
            parts.append(f"<td style=\"{style}\">{html.escape(cell)}</td>")
        parts.append("</tr>")
    parts.append("</table>")
    return "".join(parts)


KIND_KEYS = ("bug", "crash", "suggestion")

MAX_DESCRIPTION_CHARS = 8000


class ReportPage(QWidget):
    """Página de reportes dentro de ``QStackedWidget`` principal."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("ReportPage")
        # Mismo tratamiento que el resto de páginas: el fondo lo pinta el
        # contenedor de la pila y esta página no añade una capa propia.
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._attachment_text = ""
        self._attachment_name = ""

        outer = QVBoxLayout(self)
        outer.setContentsMargins(
            CONTENT_PADDING, CONTENT_PADDING, CONTENT_PADDING, CONTENT_PADDING
        )
        outer.setSpacing(10)

        # Barra de acciones superior, igual que el resto de páginas.
        self.send_btn = make_action_button(tr("report.send"), kind="primary")
        self.send_btn.clicked.connect(self._on_send_clicked)
        self.refresh_btn = make_action_button(tr("report.refresh"), kind="secondary")
        self.refresh_btn.clicked.connect(self.refresh_status)

        self.action_bar, self.bar_title = install_page_action_bar(
            outer,
            tr("sidebar.report"),
            [self.refresh_btn, self.send_btn],
        )

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll.setStyleSheet(
            "QScrollArea{background:transparent;border:none;}" + scrollbar_qss()
        )
        # El viewport de un QScrollArea pinta el color base de la paleta si no
        # se hace transparente; esa banda no coincidía con el resto de la
        # página (issue #10).
        self.scroll.viewport().setAutoFillBackground(False)
        self.scroll.viewport().setStyleSheet("background:transparent;")
        outer.addWidget(self.scroll, 1)

        body = QWidget()
        body.setObjectName("ReportBody")
        body.setStyleSheet("background:transparent;")
        self.scroll.setWidget(body)

        # Dos columnas: a la izquierda se escribe el reporte y a la derecha se
        # consulta el estado, así no hay que bajar para enviar.
        columns = QHBoxLayout(body)
        columns.setContentsMargins(0, 0, 0, 0)
        columns.setSpacing(16)

        self.left_column = QVBoxLayout()
        self.left_column.setSpacing(16)
        self.right_column = QVBoxLayout()
        self.right_column.setSpacing(16)

        self.session_card = self._build_session_card()
        self.form_card = self._build_form_card()
        self.queue_card = self._build_queue_card()
        self.environment_card = self._build_environment_card()

        self.left_column.addWidget(self.session_card)
        self.left_column.addWidget(self.form_card)
        self.left_column.addStretch(1)

        self.right_column.addWidget(self.queue_card)
        self.right_column.addWidget(self.environment_card)
        self.right_column.addStretch(1)

        columns.addLayout(self.left_column, 3)
        columns.addLayout(self.right_column, 2)

        self.refresh_status()

    # ── construcción ────────────────────────────────────────────────────────

    def _card(self, title_key: str, hint_key: str = "") -> Tuple[QFrame, QVBoxLayout]:
        card = QFrame()
        card.setObjectName("ReportCard")
        card.setStyleSheet(card_qss())
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        title = QLabel(tr(title_key))
        title.setStyleSheet(f"color:{TEXT};font-size:15px;font-weight:600;")
        layout.addWidget(title)

        if hint_key:
            hint = QLabel(tr(hint_key))
            hint.setWordWrap(True)
            hint.setStyleSheet(f"color:{TEXT_DIM};font-size:12px;")
            layout.addWidget(hint)

        card._title_label = title  # type: ignore[attr-defined]
        return card, layout

    def _build_session_card(self) -> QFrame:
        card, layout = self._card("report.session_title", "report.session_hint")
        self.session_label = QLabel("")
        self.session_label.setWordWrap(True)
        self.session_label.setStyleSheet("font-size:12px;")
        layout.addWidget(self.session_label)

        self.auto_send = QCheckBox(tr("report.auto_send"))
        self.auto_send.setChecked(crash_capture.auto_report_enabled())
        self.auto_send.toggled.connect(self._on_auto_send_toggled)
        layout.addWidget(self.auto_send)

        auto_hint = QLabel(tr("report.auto_send_hint"))
        auto_hint.setWordWrap(True)
        auto_hint.setStyleSheet(f"color:{TEXT_DIM};font-size:12px;")
        layout.addWidget(auto_hint)
        self._auto_hint = auto_hint
        return card

    def _build_form_card(self) -> QFrame:
        card, layout = self._card("report.form_title", "report.form_hint")

        self.kind_combo = QComboBox()
        self.kind_combo.setStyleSheet(input_qss())
        self._kind_labels = [
            tr("report.kind.bug"),
            tr("report.kind.crash"),
            tr("report.kind.suggestion"),
        ]
        self.kind_combo.addItems(self._kind_labels)
        layout.addWidget(self.kind_combo)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText(tr("report.title_placeholder"))
        self.title_input.setMaxLength(160)
        self.title_input.setStyleSheet(input_qss())
        layout.addWidget(self.title_input)

        self.description_input = QPlainTextEdit()
        self.description_input.setPlaceholderText(tr("report.description_placeholder"))
        self.description_input.setMinimumHeight(140)
        self.description_input.setStyleSheet(input_qss())
        layout.addWidget(self.description_input)

        self.include_logs = QCheckBox(tr("report.include_logs"))
        self.include_logs.setChecked(True)
        layout.addWidget(self.include_logs)

        self.attach_label = QLabel("")
        self.attach_label.setWordWrap(True)
        self.attach_label.setStyleSheet(f"color:{TEXT_DIM};font-size:12px;")
        layout.addWidget(self.attach_label)

        row = QHBoxLayout()
        self.attach_btn = QPushButton(tr("report.attach"))
        self.attach_btn.setStyleSheet(secondary_button_qss())
        self.attach_btn.clicked.connect(self._on_attach_clicked)
        row.addWidget(self.attach_btn)
        self.clear_attach_btn = QPushButton(tr("report.attach_clear"))
        self.clear_attach_btn.setStyleSheet(secondary_button_qss())
        self.clear_attach_btn.clicked.connect(self._on_clear_attachment)
        self.clear_attach_btn.setEnabled(False)
        row.addWidget(self.clear_attach_btn)
        row.addStretch(1)
        layout.addLayout(row)

        self.feedback = QLabel("")
        self.feedback.setWordWrap(True)
        self.feedback.setStyleSheet("font-size:12px;")
        layout.addWidget(self.feedback)
        return card

    def _build_queue_card(self) -> QFrame:
        card, layout = self._card("report.queue_title", "report.queue_hint")
        self.queue_label = QLabel("")
        self.queue_label.setWordWrap(True)
        self.queue_label.setStyleSheet("font-size:12px;")
        layout.addWidget(self.queue_label)

        row = QHBoxLayout()
        self.resend_btn = QPushButton(tr("report.queue_resend"))
        self.resend_btn.setStyleSheet(secondary_button_qss())
        self.resend_btn.clicked.connect(self._on_resend_queue)
        row.addWidget(self.resend_btn)
        self.discard_btn = QPushButton(tr("report.queue_discard"))
        self.discard_btn.setStyleSheet(secondary_button_qss())
        self.discard_btn.clicked.connect(self._on_discard_queue)
        row.addWidget(self.discard_btn)
        row.addStretch(1)
        layout.addLayout(row)
        return card

    def _build_environment_card(self) -> QFrame:
        card, layout = self._card("report.env_title", "report.env_hint")
        self.env_label = QLabel("")
        self.env_label.setWordWrap(True)
        self.env_label.setTextFormat(Qt.TextFormat.RichText)
        self.env_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.env_label.setStyleSheet(f"font-size:12px;color:{TEXT_SOFT};")
        layout.addWidget(self.env_label)
        return card

    # ── estado ──────────────────────────────────────────────────────────────

    def refresh_status(self) -> None:
        """Actualiza sesión, cola y entorno visible."""
        try:
            connected = github_issue_reporter.has_session()
        except Exception:
            connected = False

        if connected:
            self.session_label.setText(tr("report.session_connected"))
            self.session_label.setStyleSheet(f"color:{ACCENT};font-size:12px;")
        else:
            self.session_label.setText(tr("report.session_missing"))
            self.session_label.setStyleSheet(f"color:{WARNING};font-size:12px;")

        pending = report_queue.count()
        self.queue_label.setText(
            _t("report.queue_count", count=pending) if pending else tr("report.queue_empty")
        )
        self.resend_btn.setEnabled(bool(pending) and connected)
        self.discard_btn.setEnabled(bool(pending))

        try:
            environment = report_telemetry.collect_environment()
            markdown = report_telemetry.environment_markdown(environment)
            self.env_label.setText(_environment_html(markdown) or markdown)
        except Exception:
            self.env_label.setText("—")

        self.attach_label.setText(
            _t("report.attach_selected", name=self._attachment_name)
            if self._attachment_name
            else tr("report.attach_none")
        )
        self.clear_attach_btn.setEnabled(bool(self._attachment_name))

    # ── acciones ────────────────────────────────────────────────────────────

    def _selected_kind(self) -> str:
        index = self.kind_combo.currentIndex()
        if 0 <= index < len(KIND_KEYS):
            return KIND_KEYS[index]
        return "bug"

    def _on_attach_clicked(self) -> None:
        try:
            from PyQt6.QtWidgets import QFileDialog

            path, _ = QFileDialog.getOpenFileName(self, tr("report.attach"), "")
        except Exception:
            return
        if not path:
            return
        try:
            from pathlib import Path

            file_path = Path(path)
            if file_path.stat().st_size > github_issue_reporter.MAX_ATTACHMENT_BYTES:
                self._set_feedback(tr("report.attach_too_big"), error=True)
                return
            self._attachment_text = file_path.read_text(encoding="utf-8", errors="replace")
            self._attachment_name = file_path.name
            self._set_feedback(_t("report.attach_ok", name=file_path.name), error=False)
        except OSError:
            self._set_feedback(tr("report.attach_failed"), error=True)
            return
        self.refresh_status()

    def _on_auto_send_toggled(self, enabled: bool) -> None:
        try:
            from lib.pm_data import get_pm_data

            store = get_pm_data()
            store.set_user("auto_report_errors", bool(enabled))
            store.save()
        except Exception:
            pass

    def _on_clear_attachment(self) -> None:
        self._attachment_text = ""
        self._attachment_name = ""
        self._set_feedback("", error=False)
        self.refresh_status()

    def _set_feedback(self, text: str, *, error: bool) -> None:
        self.feedback.setText(text)
        self.feedback.setStyleSheet(
            f"color:{DANGER_TEXT if error else ACCENT};font-size:12px;"
        )

    def build_report(self) -> Optional[github_issue_reporter.Report]:
        """Valida el formulario y arma el reporte. ``None`` si no es válido."""
        title = self.title_input.text().strip()
        description = self.description_input.toPlainText().strip()

        if not title:
            self._set_feedback(tr("report.error_title"), error=True)
            return None
        if not description:
            self._set_feedback(tr("report.error_description"), error=True)
            return None

        attachments: List[Tuple[str, str]] = []
        if self._attachment_name and self._attachment_text:
            attachments.append((self._attachment_name, self._attachment_text))

        if self.include_logs.isChecked():
            pending = report_queue.pending()
            if pending:
                lines = [
                    f"- {entry.get('title', '')} ({entry.get('kind', '')})"
                    for entry in pending[:20]
                ]
                attachments.append(
                    ("colaL_reportes.txt", "\n".join(lines))
                )

        return github_issue_reporter.Report(
            title=title,
            description=description,
            kind=self._selected_kind(),
            labels=[self._selected_kind()],
            attachments=attachments,
            environment=report_telemetry.collect_environment(),
        )

    def _on_send_clicked(self) -> None:
        if not github_issue_reporter.has_session():
            self._set_feedback(tr("report.error_no_session"), error=True)
            return

        report = self.build_report()
        if report is None:
            return

        result = github_issue_reporter.create_issue(report)
        if result.ok:
            self.title_input.clear()
            self.description_input.clear()
            # Se limpia el adjunto sin pasar por el slot: ése borraría el
            # mensaje de éxito que se muestra justo después.
            self._attachment_text = ""
            self._attachment_name = ""
            if result.deduplicated:
                self._set_feedback(
                    _t("report.sent_duplicate", number=result.issue_number), error=False
                )
            else:
                self._set_feedback(
                    _t("report.sent_ok", number=result.issue_number), error=False
                )
        else:
            report_queue.enqueue(
                {
                    "title": report.title,
                    "description": report.description,
                    "kind": report.kind,
                    "attachments": report.attachments,
                }
            )
            self._set_feedback(
                _t("report.sent_queued", error=result.error), error=True
            )
        self.refresh_status()

    def _on_resend_queue(self) -> None:
        def _sender(entry) -> bool:
            report = github_issue_reporter.Report(
                title=str(entry.get("title", "")),
                description=str(entry.get("description", "")),
                kind=str(entry.get("kind", "bug")),
                attachments=list(entry.get("attachments", []) or []),
                environment=entry.get("environment") or None,
                fingerprint=str(entry.get("fingerprint", "") or ""),
                traceback_text=str(entry.get("traceback", "") or ""),
            )
            return github_issue_reporter.create_issue(report).ok

        outcome = report_queue.drain(_sender)
        self._set_feedback(
            _t("report.queue_result", sent=outcome["sent"], failed=outcome["failed"]),
            error=bool(outcome["failed"]),
        )
        self.refresh_status()

    def _on_discard_queue(self) -> None:
        report_queue.clear()
        self._set_feedback(tr("report.queue_cleared"), error=False)
        self.refresh_status()

    def retranslate(self) -> None:
        """Reaplica los textos propios (los fijos no los ve ``live_i18n``)."""
        self.bar_title.setText(tr("sidebar.report"))
        self.send_btn.setText(tr("report.send"))
        self.refresh_btn.setText(tr("report.refresh"))
        self.kind_combo.setItemText(0, tr("report.kind.bug"))
        self.kind_combo.setItemText(1, tr("report.kind.crash"))
        self.kind_combo.setItemText(2, tr("report.kind.suggestion"))
        self.title_input.setPlaceholderText(tr("report.title_placeholder"))
        self.description_input.setPlaceholderText(tr("report.description_placeholder"))
        self.include_logs.setText(tr("report.include_logs"))
        self.auto_send.setText(tr("report.auto_send"))
        self._auto_hint.setText(tr("report.auto_send_hint"))
        self.attach_btn.setText(tr("report.attach"))
        self.clear_attach_btn.setText(tr("report.attach_clear"))
        self.resend_btn.setText(tr("report.queue_resend"))
        self.discard_btn.setText(tr("report.queue_discard"))
        self.refresh_status()
