# -*- coding: utf-8 -*-
"""Pantalla inicial y cliente de emparejamiento de PackageMaker."""
from __future__ import annotations

import os
import threading
import time
import webbrowser
from typing import Any, Optional

import requests
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout

from lib.device_session import clear_session, load_session, save_session

DEFAULT_BASE_URL = "https://packagemaker.onrender.com"


class DeviceLinkWorker(QThread):
    session_ready = pyqtSignal(dict)
    link_error = pyqtSignal(str)
    status_changed = pyqtSignal(str)

    def __init__(self, base_url: str, code: str, parent=None):
        super().__init__(parent)
        self.base_url = base_url.rstrip("/")
        self.code = code.strip().upper()
        self._cancel = threading.Event()

    def cancel(self):
        self._cancel.set()

    def run(self):
        deadline = time.monotonic() + 15 * 60
        while time.monotonic() < deadline and not self._cancel.is_set():
            try:
                response = requests.post(
                    f"{self.base_url}/api/linkdevice/poll",
                    json={"code": self.code},
                    timeout=12,
                    headers={"Accept": "application/json", "Cache-Control": "no-store"},
                )
                if response.status_code == 202:
                    self.status_changed.emit("Código reconocido. Esperando la sesión de GitHub…")
                    self._cancel.wait(2)
                    continue
                if response.status_code == 200:
                    payload = response.json()
                    if payload.get("status") == "complete":
                        self.session_ready.emit(payload)
                        return
                if response.status_code == 410:
                    raise RuntimeError("El código de emparejamiento expiró")
                if response.status_code == 404:
                    raise RuntimeError("El código no es válido o ya fue utilizado")
                raise RuntimeError("El servidor devolvió una respuesta inesperada")
            except requests.RequestException as error:
                self.status_changed.emit("Esperando conexión con Render…")
                self._cancel.wait(4)
            except (RuntimeError, ValueError) as error:
                self.link_error.emit(str(error))
                return
        if not self._cancel.is_set():
            self.link_error.emit("El código expiró. Abre el sitio de vinculación para generar otro.")


class DeviceLinkDialog(QDialog):
    """Gate de inicio: la app no avanza hasta tener una sesión vinculada o salir."""

    def __init__(self, parent=None, base_url: Optional[str] = None):
        super().__init__(parent)
        self.setWindowTitle("Vincular PackageMaker")
        self.setMinimumSize(480, 340)
        self.setStyleSheet(
            "QDialog { background:#0d1117; color:#f0f6fc; }"
            "QLabel { color:#f0f6fc; }"
            "QLineEdit { background:#161b22; color:#f0f6fc; border:1px solid #30363d; "
            "border-radius:12px; padding:12px; font:700 22px monospace; letter-spacing:2px; }"
            "QLineEdit:focus { border:1px solid #ff7b72; }"
            "QPushButton { background:#ff7b72; color:#0d1117; border:0; border-radius:12px; "
            "padding:11px 16px; font-weight:800; }"
            "QPushButton:hover { background:#ffa198; }"
            "QPushButton:disabled { background:#30363d; color:#8b949e; }"
        )
        self.base_url = (base_url or os.getenv("PM_RENDER_AUTH_BASE_URL", DEFAULT_BASE_URL)).rstrip("/")
        self.session_payload: dict[str, Any] = {}
        self.worker: Optional[DeviceLinkWorker] = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 30, 32, 28)
        layout.setSpacing(14)

        eyebrow = QLabel("PRIMER ARRANQUE")
        eyebrow.setStyleSheet("color:#ff7b72; font-size:11px; font-weight:900; letter-spacing:1px;")
        layout.addWidget(eyebrow)
        title = QLabel("Vincula tu PackageMaker")
        title.setStyleSheet("font-size:27px; font-weight:900; letter-spacing:-.5px;")
        layout.addWidget(title)
        subtitle = QLabel(
            "Abre el sitio, conecta GitHub y escribe aquí el código de emparejamiento. "
            "La contraseña nunca entra en la aplicación."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color:#9da7b3; font-size:13px;")
        layout.addWidget(subtitle)

        self.open_button = QPushButton("Abrir packagemaker.onrender.com/linkdevice")
        self.open_button.clicked.connect(self.open_link_page)
        layout.addWidget(self.open_button)

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("XXXX-XXXX")
        self.code_input.setMaxLength(9)
        self.code_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.code_input.textChanged.connect(lambda value: self.code_input.setText(value.upper()))
        layout.addWidget(self.code_input)

        self.status_label = QLabel("Cuando el sitio muestre el código, escríbelo aquí.")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color:#9da7b3; padding:4px 0;")
        layout.addWidget(self.status_label)
        layout.addStretch()

        buttons = QHBoxLayout()
        buttons.addStretch()
        self.exit_button = QPushButton("Salir")
        self.exit_button.setStyleSheet("QPushButton { background:#21262d; color:#f0f6fc; border:1px solid #30363d; }")
        self.exit_button.clicked.connect(self.reject)
        self.link_button = QPushButton("Vincular")
        self.link_button.clicked.connect(self.start_link)
        buttons.addWidget(self.exit_button)
        buttons.addWidget(self.link_button)
        layout.addLayout(buttons)

    def open_link_page(self):
        if not webbrowser.open(f"{self.base_url}/linkdevice", new=2):
            self.status_label.setText("No se pudo abrir el navegador. Copia la dirección manualmente.")
        else:
            self.status_label.setText("Autoriza GitHub en el navegador y espera a que aparezca el código.")

    def start_link(self):
        code = self.code_input.text().strip().upper()
        if len(code.replace("-", "")) != 8:
            self.status_label.setText("Escribe el código completo de ocho caracteres.")
            return
        self.link_button.setEnabled(False)
        self.open_button.setEnabled(False)
        self.code_input.setEnabled(False)
        self.status_label.setText("Validando el código con Render…")
        self.worker = DeviceLinkWorker(self.base_url, code, self)
        self.worker.status_changed.connect(self.status_label.setText)
        self.worker.session_ready.connect(self.on_session_ready)
        self.worker.link_error.connect(self.on_link_error)
        self.worker.start()

    def on_session_ready(self, payload: dict):
        profile = payload.get("profile") or {}
        session = payload.get("session") or {}
        if not save_session(session.get("ticket", ""), profile, int(session.get("expires_in", 0))):
            self.on_link_error("No se pudo guardar la sesión local de forma segura")
            return
        self.session_payload = {"profile": profile, "session": session}
        self.status_label.setText(f"Vinculación exitosa como @{profile.get('login', 'usuario')}.")
        self.accept()

    def on_link_error(self, message: str):
        self.status_label.setText(message)
        self.link_button.setEnabled(True)
        self.open_button.setEnabled(True)
        self.code_input.setEnabled(True)

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait(1500)
        event.accept()


def require_device_link(parent=None) -> bool:
    cached = load_session()
    if cached:
        base_url = os.getenv("PM_RENDER_AUTH_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
        try:
            response = requests.post(
                f"{base_url}/api/linkdevice/session",
                json={"ticket": cached["ticket"]},
                timeout=8,
                headers={"Accept": "application/json", "Cache-Control": "no-store"},
            )
            if response.status_code == 200 and response.json().get("status") == "valid":
                return True
            if response.status_code == 401:
                clear_session()
        except requests.RequestException:
            # La caché local permite arrancar durante una caída temporal; las
            # operaciones que necesiten GitHub seguirán requiriendo servidor.
            return True
    dialog = DeviceLinkDialog(parent)
    return dialog.exec() == QDialog.DialogCode.Accepted
