# -*- coding: utf-8 -*-
"""Diálogo de inyección del ``.env`` (bugs.txt Fase 1.4).

Si el proyecto trae un ``.env``, antes de empaquetar se pregunta cómo debe
viajar:

* **Parcial** — todas las variables se inyectan en el entorno global al
  ejecutar el programa.
* **Personalizado** — se elige variable a variable; cada fila muestra una
  casilla, el icono de la aplicación (en Linux se empareja por el sufijo
  ``-icon.ico`` dentro de ``app/``), el nombre del programa y su peso.

El diálogo reutiliza el efecto parcial (atenuado + desenfoque) del resto de
alertas y devuelve el payload que consume el empaquetador.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Sequence

from lib.dialog_effect import install_partial_effect
from lib.i18n import tr

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QIcon
    from PyQt6.QtWidgets import (
        QCheckBox,
        QDialog,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QRadioButton,
        QScrollArea,
        QVBoxLayout,
        QWidget,
    )

    PYQT6_AVAILABLE = True
except ImportError:  # pragma: no cover - entorno sin Qt
    PYQT6_AVAILABLE = False

CARD_RADIUS = 18


def _is_dark() -> bool:
    try:
        from lib.fluent_theme import system_theme_mode

        return system_theme_mode() == "dark"
    except Exception:
        return True


def _palette(dark: bool) -> Dict[str, str]:
    if dark:
        return {
            "bg": "#1c1c1e",
            "border": "rgba(255, 255, 255, 0.12)",
            "title": "#ffffff",
            "message": "rgba(235, 235, 245, 0.72)",
            "row": "rgba(255, 255, 255, 0.05)",
            "text": "#ffffff",
            "accent": "#0078D4",
        }
    return {
        "bg": "#ffffff",
        "border": "rgba(0, 0, 0, 0.12)",
        "title": "#1c1c1e",
        "message": "rgba(60, 60, 67, 0.72)",
        "row": "rgba(0, 0, 0, 0.04)",
        "text": "#1c1c1e",
        "accent": "#0078D4",
    }


def app_icon_for(project_path: Path, app_name: str) -> Optional[Path]:
    """Icono de la aplicación: ``<app>-icon.ico`` en ``app/`` o en la raíz."""
    root = Path(project_path)
    stems = [f"{app_name}-icon", "app-icon", "icon"]
    for directory in (root / "app", root):
        for stem in stems:
            for suffix in (".ico", ".png"):
                candidate = directory / f"{stem}{suffix}"
                if candidate.is_file():
                    return candidate
    return None


def env_rows(variables: Sequence[str]) -> List[Dict[str, object]]:
    """Filas del chooser: casilla, nombre del programa y peso."""
    return [
        {"key": key, "label": key, "weight": 1, "checked": True}
        for key in variables
    ]


if PYQT6_AVAILABLE:

    class EnvInjectionDialog(QDialog):
        """Elección del método de inyección del ``.env``."""

        def __init__(
            self,
            parent: Optional[QWidget],
            variables: Dict[str, str],
            project_path: Path,
            app_name: str = "app",
        ):
            super().__init__(parent)
            self._variables = dict(variables)
            self._project_path = Path(project_path)
            self._app_name = app_name
            self._mode: Optional[str] = None
            self._selected: List[str] = []
            self._overlay = None
            self._checks: Dict[str, QCheckBox] = {}

            self.setWindowTitle(tr("build.env_title"))
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog
            )
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.setModal(True)
            self.setMinimumWidth(520)
            self._build_ui()

        def _build_ui(self) -> None:
            pal = _palette(_is_dark())
            outer = QVBoxLayout(self)
            outer.setContentsMargins(0, 0, 0, 0)

            card = QWidget(self)
            card.setObjectName("EnvCard")
            card.setStyleSheet(
                f"""
                QWidget#EnvCard {{
                    background: {pal['bg']};
                    border: 1px solid {pal['border']};
                    border-radius: {CARD_RADIUS}px;
                }}
                QLabel {{ color: {pal['text']}; }}
                QRadioButton, QCheckBox {{ color: {pal['text']}; }}
                """
            )
            outer.addWidget(card)

            layout = QVBoxLayout(card)
            layout.setContentsMargins(28, 26, 28, 20)
            layout.setSpacing(14)

            title = QLabel(tr("build.env_title"))
            title.setStyleSheet("font-size: 17px; font-weight: 600;")
            layout.addWidget(title)

            message = QLabel(tr("build.env_message"))
            message.setWordWrap(True)
            message.setStyleSheet(f"color: {pal['message']};")
            layout.addWidget(message)

            self._global_radio = QRadioButton(tr("build.env_global"))
            self._global_radio.setToolTip(tr("build.env_global_hint"))
            self._custom_radio = QRadioButton(tr("build.env_custom"))
            self._custom_radio.setToolTip(tr("build.env_custom_hint"))
            self._global_radio.setChecked(True)
            layout.addWidget(self._global_radio)
            layout.addWidget(self._custom_radio)

            self._scroll = QScrollArea()
            self._scroll.setWidgetResizable(True)
            self._scroll.setVisible(False)
            self._scroll.setMaximumHeight(220)
            self._scroll.setStyleSheet("QScrollArea { border: none; }")
            self._scroll.setWidget(self._build_chooser(pal))
            layout.addWidget(self._scroll)

            self._custom_radio.toggled.connect(self._scroll.setVisible)

            buttons = QHBoxLayout()
            buttons.addStretch()
            cancel = QPushButton(tr("common.cancel"))
            cancel.setCursor(Qt.CursorShape.PointingHandCursor)
            cancel.clicked.connect(self.reject)
            confirm = QPushButton(tr("common.ok"))
            confirm.setCursor(Qt.CursorShape.PointingHandCursor)
            confirm.setDefault(True)
            confirm.clicked.connect(self._confirm)
            buttons.addWidget(cancel)
            buttons.addWidget(confirm)
            layout.addLayout(buttons)

        def _build_chooser(self, pal: Dict[str, str]) -> QWidget:
            container = QWidget()
            rows = QVBoxLayout(container)
            rows.setContentsMargins(0, 0, 0, 0)
            rows.setSpacing(6)

            icon_path = app_icon_for(self._project_path, self._app_name)
            icon = QIcon(str(icon_path)) if icon_path else QIcon()

            for key in self._variables:
                row = QWidget()
                row.setStyleSheet(
                    f"background: {pal['row']}; border-radius: 10px;"
                )
                row_layout = QHBoxLayout(row)
                row_layout.setContentsMargins(10, 6, 10, 6)
                row_layout.setSpacing(10)

                check = QCheckBox()
                check.setChecked(True)
                self._checks[key] = check
                row_layout.addWidget(check)

                badge = QLabel()
                badge.setFixedSize(18, 18)
                if not icon.isNull():
                    badge.setPixmap(icon.pixmap(18, 18))
                row_layout.addWidget(badge)

                label = QLabel(f"{key}  ·  {self._app_name}")
                row_layout.addWidget(label, 1)

                weight = QLabel(str(env_rows([key])[0]["weight"]))
                weight.setStyleSheet(f"color: {pal['message']};")
                row_layout.addWidget(weight)

                rows.addWidget(row)
            rows.addStretch()
            return container

        def _confirm(self) -> None:
            from lib.build_preflight import INJECTION_CUSTOM, INJECTION_GLOBAL

            if self._global_radio.isChecked():
                self._mode = INJECTION_GLOBAL
                self._selected = list(self._variables)
            else:
                self._mode = INJECTION_CUSTOM
                self._selected = [
                    key for key, check in self._checks.items() if check.isChecked()
                ]
            self.accept()

        def payload(self) -> Dict[str, object]:
            """Payload elegido; lista vacía si se canceló."""
            from lib.build_preflight import build_env_payload

            if self._mode is None:
                return {}
            return build_env_payload(self._variables, self._mode, self._selected)

        # -- ciclo de vida --------------------------------------------
        def showEvent(self, event):  # noqa: N802 (API Qt)
            super().showEvent(event)
            self._overlay = install_partial_effect(self, self.parent())
            self._center_on_parent()

        def _teardown(self) -> None:
            overlay, self._overlay = self._overlay, None
            if overlay is not None:
                overlay.teardown()

        def _center_on_parent(self) -> None:
            parent = self.parent()
            if parent is None:
                return
            geo = parent.frameGeometry()
            self.adjustSize()
            self.move(
                geo.center().x() - self.width() // 2,
                geo.center().y() - self.height() // 2,
            )

        def closeEvent(self, event):  # noqa: N802 (API Qt)
            self._teardown()
            super().closeEvent(event)

        def accept(self) -> None:
            self._teardown()
            super().accept()

        def reject(self) -> None:
            self._teardown()
            super().reject()

else:  # pragma: no cover - entorno sin Qt

    class EnvInjectionDialog:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            raise RuntimeError("PyQt6 no está disponible")

        def exec(self):  # noqa: A003
            return 0

        def payload(self):
            return {}


def ask_env_injection(
    parent,
    variables: Dict[str, str],
    project_path: Path,
    app_name: str = "app",
) -> Dict[str, object]:
    """Muestra el diálogo y devuelve el payload (``{}`` si se cancela)."""
    if not variables:
        return {}
    dialog = EnvInjectionDialog(parent, variables, project_path, app_name)
    dialog.exec()
    return dialog.payload()


__all__ = [
    "EnvInjectionDialog",
    "app_icon_for",
    "ask_env_injection",
    "env_rows",
]
