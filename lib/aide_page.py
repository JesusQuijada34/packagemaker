# -*- coding: utf-8 -*-
"""Página AIDE: asistente que responde sobre el repositorio con la cuenta del usuario.

El usuario escribe una petición, opcionalmente adjunta contexto del proyecto y
recibe una respuesta. El backend (``lib/aide_backend.py``) decide si usa
Copilot con el SDK oficial o un endpoint compatible con OpenAI. Cuando ningún
proveedor está disponible, la página lo dice en claro en vez de fingir que
funciona.

Todo el color sale de ``lib/design_tokens`` y todo el texto de ``tr()``.
"""

from __future__ import annotations

from typing import Dict, Optional

try:
    from PyQt6.QtCore import pyqtSignal
    from PyQt6.QtWidgets import (
        QCheckBox,
        QComboBox,
        QLabel,
        QLineEdit,
        QPlainTextEdit,
        QPushButton,
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

    def pyqtSignal(*args, **kwargs):  # type: ignore[no-redef]
        return None


from lib import aide_backend
from lib.design_tokens import CONTENT_PADDING
from lib.i18n import tr


def _t(key: str, **kwargs) -> str:
    text = tr(key)
    return text.format(**kwargs) if kwargs else text


class AidePage(QWidget):
    """Página del asistente AIDE."""

    # ``ask_async`` responde desde un hilo daemon y Qt sólo permite tocar
    # widgets desde el hilo de la GUI. El backend entrega aquí y el sinal
    # cruza al hilo correcto por conexión en cola.
    answered = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings = aide_backend.get_settings()
        self._busy = False
        self.answered.connect(self._on_answer)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            CONTENT_PADDING, CONTENT_PADDING, CONTENT_PADDING, CONTENT_PADDING
        )

        title = QLabel(_t("aide.title"))
        title.setWordWrap(True)
        layout.addWidget(title)

        self.provider_combo = QComboBox()
        self.provider_combo.addItem(_t("aide.provider_copilot"), "copilot")
        self.provider_combo.addItem(_t("aide.provider_openai"), "openai")
        index = self.provider_combo.findData(str(self._settings.get("provider")))
        if index >= 0:
            self.provider_combo.setCurrentIndex(index)
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        layout.addWidget(self.provider_combo)

        # Credenciales del endpoint propio: sin estos campos la opción OpenAI
        # era inalcanzable (el backend siempre respondía «sin URL» / «sin clave»).
        self.endpoint_input = QLineEdit(str(self._settings.get("endpoint") or ""))
        self.endpoint_input.setPlaceholderText("https://api.example.com/v1")
        self.endpoint_input.editingFinished.connect(self._on_credentials_changed)
        layout.addWidget(self.endpoint_input)

        self.key_input = QLineEdit()
        # Nunca se reescribe la clave guardada en el widget: sólo se envía si el
        # usuario escribe una nueva.
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setPlaceholderText(_t("aide.api_key_placeholder"))
        self.key_input.editingFinished.connect(self._on_credentials_changed)
        layout.addWidget(self.key_input)

        self.model_input = QLineEdit(str(self._settings.get("model") or ""))
        self.model_input.setPlaceholderText(aide_backend.DEFAULT_MODEL)
        self.model_input.editingFinished.connect(self._on_credentials_changed)
        layout.addWidget(self.model_input)

        self.status = QLabel("")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)

        self.prompt_input = QPlainTextEdit()
        self.prompt_input.setPlaceholderText(_t("aide.placeholder"))
        self.key_input.setPlaceholderText(_t("aide.api_key_placeholder"))
        self.prompt_input.setMinimumHeight(90)
        layout.addWidget(self.prompt_input)

        self.context_check = QCheckBox(_t("aide.attach_context"))
        self.context_check.setChecked(bool(self._settings.get("send_context")))
        self.context_check.toggled.connect(self._on_context_toggled)
        layout.addWidget(self.context_check)

        self.send_button = QPushButton(_t("aide.send"))
        self.send_button.clicked.connect(self._on_send)
        layout.addWidget(self.send_button)

        self.answer_view = QPlainTextEdit()
        self.answer_view.setReadOnly(True)
        layout.addWidget(self.answer_view)

        self._refresh_state()

    # --- estado ---------------------------------------------------------
    def _refresh_state(self) -> None:
        self._settings = aide_backend.get_settings()
        state = aide_backend.availability(self._settings)
        if state.ok:
            self.status.setText(_t("aide.ready"))
            self.send_button.setEnabled(not self._busy)
        else:
            self.status.setText(_t(f"aide.state_{state.reason}"))
            self.send_button.setEnabled(False)

    def _on_provider_changed(self, _index: int) -> None:
        provider = self.provider_combo.currentData()
        if provider:
            aide_backend.save_settings(aide_provider=str(provider))
            self._refresh_state()

    def _on_credentials_changed(self) -> None:
        values = {
            "aide_endpoint": self.endpoint_input.text().strip(),
            "aide_model": self.model_input.text().strip() or aide_backend.DEFAULT_MODEL,
        }
        typed_key = self.key_input.text().strip()
        if typed_key:
            values["aide_api_key"] = typed_key
            self.key_input.clear()
        aide_backend.save_settings(**values)
        self._refresh_state()

    def _on_context_toggled(self, checked: bool) -> None:
        aide_backend.save_settings(aide_send_context=bool(checked))

    # --- envío ----------------------------------------------------------
    def _project_root(self) -> str:
        try:
            from lib.pm_data import get_pm_data

            return str(get_pm_data().get_user("last_project_root", "") or "")
        except Exception:
            return ""

    def _collect_files(self) -> Optional[Dict[str, str]]:
        if not self.context_check.isChecked():
            return None
        root = self._project_root()
        return aide_backend.collect_project_context(root) if root else None

    def _on_send(self) -> None:
        message = self.prompt_input.toPlainText().strip()
        if not message:
            self.status.setText(_t("aide.empty_prompt"))
            return
        self._busy = True
        self.send_button.setEnabled(False)
        self.status.setText(_t("aide.thinking"))
        aide_backend.ask_async(
            message,
            self.answered.emit,
            files=self._collect_files(),
            app_version=_t("app.version"),
        )

    def _on_answer(self, answer: aide_backend.Answer) -> None:
        self._busy = False
        self.send_button.setEnabled(True)
        if answer.ok:
            self.answer_view.setPlainText(answer.text)
            self.status.setText(
                _t("aide.answer_from", provider=answer.provider, model=answer.model)
            )
        else:
            reason = f"aide.state_{answer.error}"
            translated = tr(reason)
            if translated != reason:
                self.status.setText(translated)
            else:
                self.status.setText(_t("aide.error", error=answer.error))

    # --- i18n -----------------------------------------------------------
    def retranslate(self) -> None:
        """Reaplica los textos propios tras cambiar de idioma."""
        self.provider_combo.setItemText(0, _t("aide.provider_copilot"))
        self.provider_combo.setItemText(1, _t("aide.provider_openai"))
        self.prompt_input.setPlaceholderText(_t("aide.placeholder"))
        self.context_check.setText(_t("aide.attach_context"))
        self.send_button.setText(_t("aide.send"))
        self._refresh_state()
