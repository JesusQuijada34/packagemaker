"""Diálogo del editor ``.mexf`` con verificación de sintaxis en tiempo real.

Reutiliza el núcleo de ``lib.mexf_editor`` (lint y compilación) y añade una
interfaz PyQt6: editor de texto, panel de diagnósticos y botón de compilación
interactiva a ``.asksome``. En entornos sin PyQt6 expone un marcador que informa
la falta de GUI, igual que el resto del proyecto.
"""
from __future__ import annotations

import os

try:
    from PyQt6.QtWidgets import (
        QDialog,
        QVBoxLayout,
        QHBoxLayout,
        QLabel,
        QPlainTextEdit,
        QPushButton,
        QListWidget,
        QListWidgetItem,
        QFileDialog,
        QSplitter,
    )
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtGui import QFont
    PYQT6_AVAILABLE = True
except ImportError:  # pragma: no cover - entorno sin GUI
    PYQT6_AVAILABLE = False

    class QDialog:  # type: ignore
        def __init__(self, *args, **kwargs):
            raise ImportError("El editor .mexf requiere PyQt6.")

from lib.design_tokens import ACCENT
from lib.i18n import tr
from lib.mexf_editor import compile_source, lint_source

DEFAULT_TEMPLATE = """format: mexf
version: 1
metadata:
  id: influent.mi-app
  name: Mi App
  version: v1.0
runtime:
  launcher: argv
commands: []
triggers: []
"""


class MexfEditorDialog(QDialog):
    """Editor de documentos ``.mexf`` con lint y compilación a ``.asksome``."""

    def __init__(self, parent=None, source: str = "", file_path: str | None = None):
        super().__init__(parent)
        self.setWindowTitle(tr("mexf_editor.title"))
        self.resize(900, 620)
        self.file_path = file_path
        self._build_ui(source)

    def _build_ui(self, source: str) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        header = QLabel(self.file_path or tr("mexf_editor.untitled"))
        header.setStyleSheet(f"color: {ACCENT}; font-weight: bold;")
        layout.addWidget(header)

        splitter = QSplitter(Qt.Orientation.Vertical)
        self.editor = QPlainTextEdit()
        self.editor.setFont(QFont("Cascadia Code, Consolas, monospace", 10))
        self.editor.setPlainText(source or DEFAULT_TEMPLATE)
        splitter.addWidget(self.editor)

        self.diagnostics = QListWidget()
        splitter.addWidget(self.diagnostics)
        splitter.setSizes([460, 140])
        layout.addWidget(splitter)

        buttons = QHBoxLayout()
        self.status = QLabel(tr("mexf_editor.ready"))
        self.status.setStyleSheet("color: #888;")
        buttons.addWidget(self.status)
        buttons.addStretch()

        self.btn_check = QPushButton(tr("mexf_editor.check"))
        self.btn_check.clicked.connect(self.run_lint)
        buttons.addWidget(self.btn_check)

        self.btn_compile = QPushButton(tr("mexf_editor.compile"))
        self.btn_compile.clicked.connect(self.run_compile)
        buttons.addWidget(self.btn_compile)

        self.btn_close = QPushButton(tr("common.close"))
        self.btn_close.clicked.connect(self.reject)
        buttons.addWidget(self.btn_close)
        layout.addLayout(buttons)

        # Verificación en tiempo real con un pequeño retardo para no analizar
        # en cada pulsación.
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(400)
        self._timer.timeout.connect(self.run_lint)
        self.editor.textChanged.connect(self._timer.start)
        self.run_lint()

    def run_lint(self) -> bool:
        self.diagnostics.clear()
        issues = lint_source(self.editor.toPlainText())
        for issue in issues:
            item = QListWidgetItem(f"L{issue.line}:{issue.column}  {issue.message}")
            item.setData(Qt.ItemDataRole.UserRole, issue.line)
            self.diagnostics.addItem(item)
        if issues:
            self.status.setText(tr("mexf_editor.issues").format(count=len(issues)))
            return False
        self.status.setText(tr("mexf_editor.valid"))
        return True

    def run_compile(self) -> None:
        if not self.run_lint():
            return
        target, _ = QFileDialog.getSaveFileName(
            self, tr("mexf_editor.save_as"), self._default_output(), "Asksome (*.asksome)"
        )
        if not target:
            return
        try:
            output = compile_source(self.editor.toPlainText(), target)
        except Exception as exc:  # noqa: BLE001 - se muestra al usuario
            self.status.setText(tr("mexf_editor.compile_failed").format(error=exc))
            return
        self.status.setText(tr("mexf_editor.compiled").format(path=output))

    def _default_output(self) -> str:
        if self.file_path:
            return os.path.splitext(self.file_path)[0] + ".asksome"
        return os.path.join(os.path.expanduser("~"), "mexf-editor.asksome")


def open_mexf_editor(parent=None, file_path: str | None = None) -> "MexfEditorDialog":
    """Abre el editor cargando el archivo indicado si existe."""
    source = ""
    if file_path and os.path.isfile(file_path):
        with open(file_path, encoding="utf-8-sig") as handle:
            source = handle.read()
    dialog = MexfEditorDialog(parent, source=source, file_path=file_path)
    dialog.exec()
    return dialog
