# -*- coding: utf-8 -*-
"""Diálogo de alerta temático con botones verticales de ancho completo.

Reemplazo de ``LeviathanDialog`` para los avisos de la aplicación:

- El fondo del diálogo es blanco o negro según el tema del sistema.
- Los botones ocupan todo el ancho y se apilan en vertical, separados por
  finas líneas divisorias.
- Cada botón responde a los estados normal, hover, pressed, disabled y
  default (el botón principal resaltado).
"""

from __future__ import annotations

from typing import Callable, List, Optional, Sequence

from lib.dialog_effect import install_partial_effect

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QDialog,
        QFrame,
        QLabel,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )

    PYQT6_AVAILABLE = True
except ImportError:  # pragma: no cover - entorno sin Qt
    PYQT6_AVAILABLE = False

    class QDialog:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            pass

        def exec(self):  # noqa: A003 - API Qt
            return 0


DIALOG_WIDTH = 400
ICON_FOR_MODE = {
    "info": "ℹ",
    "success": "✓",
    "warning": "⚠",
    "error": "✕",
    "question": "?",
    "confirm": "?",
}
ACCENT_FOR_MODE = {
    "info": "#0a84ff",
    "success": "#30d158",
    "warning": "#ff9f0a",
    "error": "#ff453a",
    "question": "#0a84ff",
    "confirm": "#0a84ff",
}

# Palabras que marcan el botón de aceptación en una lista explícita.
ACCEPT_WORDS = {
    "si",
    "sí",
    "yes",
    "y",
    "ok",
    "aceptar",
    "continuar",
    "guardar",
    "entendido",
    "de acuerdo",
}


def _is_accept_text(text: str) -> bool:
    return text.strip().lower().rstrip(".") in ACCEPT_WORDS


def _is_dark() -> bool:
    """Tema activo del sistema (``True`` = oscuro)."""
    try:
        from lib.fluent_theme import system_theme_mode

        return system_theme_mode() == "dark"
    except Exception:
        return True


def _palette(dark: bool) -> dict:
    """Colores del diálogo según el tema: negro u blanco."""
    if dark:
        return {
            "bg": "#1c1c1e",
            "border": "rgba(255, 255, 255, 0.12)",
            "title": "#ffffff",
            "message": "rgba(235, 235, 245, 0.72)",
            "separator": "rgba(255, 255, 255, 0.10)",
            "btn": "#1c1c1e",
            "btn_text": "#ffffff",
            "btn_hover": "rgba(255, 255, 255, 0.08)",
            "btn_pressed": "rgba(255, 255, 255, 0.16)",
            "btn_disabled": "rgba(255, 255, 255, 0.30)",
        }
    return {
        "bg": "#ffffff",
        "border": "rgba(0, 0, 0, 0.12)",
        "title": "#1c1c1e",
        "message": "rgba(60, 60, 67, 0.72)",
        "separator": "rgba(0, 0, 0, 0.10)",
        "btn": "#ffffff",
        "btn_text": "#1c1c1e",
        "btn_hover": "rgba(0, 0, 0, 0.06)",
        "btn_pressed": "rgba(0, 0, 0, 0.12)",
        "btn_disabled": "rgba(0, 0, 0, 0.30)",
    }


class AlertDialog(QDialog):
    """Alerta modal con botones verticales de ancho completo."""

    def __init__(
        self,
        parent: Optional[QWidget],
        title: str,
        message: str,
        mode: str = "info",
        buttons: Optional[Sequence[str]] = None,
    ):
        super().__init__(parent)
        self._mode = mode if mode in ICON_FOR_MODE else "info"
        self._accent = ACCENT_FOR_MODE[self._mode]
        self._buttons = list(buttons) if buttons else self._default_buttons(self._mode)
        self._clicked: Optional[str] = None

        self.setWindowTitle(title)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setMinimumWidth(DIALOG_WIDTH)

        self._build_ui(title, message)
        self._center_on_parent()
        self._overlay = None

    @staticmethod
    def _default_buttons(mode: str) -> List[str]:
        if mode in ("question", "confirm"):
            return ["Cancelar", "Aceptar"]
        return ["Entendido"]

    # -- construcción -------------------------------------------------
    def _build_ui(self, title: str, message: str) -> None:
        dark = _is_dark()
        pal = _palette(dark)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QWidget(self)
        card.setObjectName("AlertCard")
        card.setStyleSheet(
            f"""
            QWidget#AlertCard {{
                background: {pal['bg']};
                border: 1px solid {pal['border']};
                border-radius: 14px;
            }}
            """
        )
        outer.addWidget(card)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # Cabecera: icono + título
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(24, 22, 24, 6)
        header_layout.setSpacing(8)

        icon_label = QLabel(ICON_FOR_MODE[self._mode])
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(
            f"color: {self._accent}; font-size: 30px; font-weight: 700; background: transparent;"
        )
        header_layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)
        title_label.setStyleSheet(
            f"color: {pal['title']}; font-size: 16px; font-weight: 600; background: transparent;"
        )
        header_layout.addWidget(title_label)

        card_layout.addWidget(header)

        # Mensaje
        msg_label = QLabel(message)
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet(
            f"color: {pal['message']}; font-size: 13px; background: transparent;"
        )
        msg_wrap = QWidget()
        msg_layout = QVBoxLayout(msg_wrap)
        msg_layout.setContentsMargins(24, 6, 24, 18)
        msg_layout.addWidget(msg_label)
        card_layout.addWidget(msg_wrap)

        # Botones: ancho completo, verticales, con separadores
        default_index = self._default_index()
        for index, text in enumerate(self._buttons):
            is_default = index == default_index
            card_layout.addWidget(self._make_separator(pal))
            card_layout.addWidget(self._make_button(text, is_default, pal))

    def _default_index(self) -> int:
        """Índice del botón principal (el que acepta)."""
        for index, text in enumerate(self._buttons):
            if _is_accept_text(text):
                return index
        return len(self._buttons) - 1

    def _make_separator(self, pal: dict) -> QFrame:
        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet(f"background: {pal['separator']}; border: none;")
        return line

    def _make_button(self, text: str, is_default: bool, pal: dict) -> QPushButton:
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setMinimumHeight(48)
        btn.setDefault(is_default)
        btn.setAutoDefault(False)
        color = self._accent if is_default else pal["btn_text"]
        weight = 600 if is_default else 500
        btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {pal['btn']};
                color: {color};
                border: none;
                border-radius: 0px;
                font-size: 14px;
                font-weight: {weight};
                padding: 12px 16px;
            }}
            QPushButton:hover {{
                background: {pal['btn_hover']};
            }}
            QPushButton:pressed {{
                background: {pal['btn_pressed']};
            }}
            QPushButton:disabled {{
                color: {pal['btn_disabled']};
            }}
            """
        )
        btn.clicked.connect(lambda _=False, t=text: self._on_clicked(t))
        return btn

    # -- comportamiento ----------------------------------------------
    def _on_clicked(self, text: str) -> None:
        self._clicked = text
        self.accept()

    def clicked_text(self) -> Optional[str]:
        return self._clicked

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

    # -- efecto parcial + ciclo de vida -------------------------------
    def showEvent(self, event):  # noqa: N802 (API Qt)
        super().showEvent(event)
        self._overlay = install_partial_effect(self, self.parent())
        self._center_on_parent()

    def _teardown(self) -> None:
        """Quita el efecto parcial una sola vez, cierre como cierre.

        ``QDialog.accept()`` no dispara ``closeEvent``; sin esto la capa
        parcial se quedaría pegada sobre la ventana principal.
        """
        overlay = self._overlay
        self._overlay = None
        if overlay is not None:
            overlay.teardown()

    def closeEvent(self, event):  # noqa: N802 (API Qt)
        self._teardown()
        super().closeEvent(event)

    def accept(self) -> None:
        self._teardown()
        super().accept()

    def reject(self) -> None:
        self._teardown()
        super().reject()

    def done(self, result: int) -> None:
        self._teardown()
        super().done(result)

    @staticmethod
    def launch(
        parent,
        title: str,
        message: str,
        mode: str = "info",
        buttons: Optional[Sequence[str]] = None,
        callback: Optional[Callable[[str], None]] = None,
    ):
        """Compatibilidad con ``LeviathanDialog.launch``.

        Devuelve ``1`` si se aceptó el botón principal, ``0`` en caso contrario.
        El ``callback`` recibe el texto del botón pulsado.
        """
        dialog = AlertDialog(parent, title, message, mode, buttons)
        dialog.exec()
        text = dialog.clicked_text()
        if callback is not None:
            try:
                callback(text if text is not None else "")
            except Exception:
                pass
        # Sólo el botón principal (Aceptar/SI) cuenta como aceptación.
        if text is not None and _is_accept_text(text):
            return 1
        return 0


def pm_alert(parent, title: str, message: str, mode: str = "info", buttons=None):
    """Muestra una alerta modal y devuelve el texto del botón pulsado."""
    dialog = AlertDialog(parent, title, message, mode, buttons)
    dialog.exec()
    return dialog.clicked_text()


def pm_confirm(parent, title: str, message: str, mode: str = "question") -> bool:
    """Alerta de confirmación: ``True`` si el usuario acepta."""
    return AlertDialog.launch(parent, title, message, mode=mode) == 1


# Nombre de compatibilidad: los módulos que importaban ``LeviathanDialog``
# pueden seguir usando ``AlertDialog`` con la misma interfaz ``launch``.
LeviathanDialog = AlertDialog


if __name__ == "__main__":  # pragma: no cover - prueba manual
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    print(pm_alert(None, "Prueba", "Mensaje de prueba", mode="info"))
