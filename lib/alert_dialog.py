# -*- coding: utf-8 -*-
"""Diálogo de alerta temático estilo iOS/UWP.

Reemplazo de ``LeviathanDialog`` para los avisos de la aplicación:

- Tarjeta con esquinas redondeadas sobre un efecto parcial (blur + atenuado).
- Icono de confirmación en **círculo relleno** con el glifo en blanco, no un
  emoji ni un glifo suelto.
- Los botones **flotan**: sin líneas divisorias y sin ocupar todo el ancho.
  Con un solo botón se muestra centrado en píldora; con dos, se alinean a la
  derecha (UWP) con el principal a la derecha.
- ``outline: none`` en ``:focus`` para eliminar el borde punteado de Qt.
"""

from __future__ import annotations

from typing import Callable, List, Optional, Sequence

from lib.dialog_effect import install_partial_effect

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QDialog,
        QHBoxLayout,
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
CARD_RADIUS = 16
ICON_DIAMETER = 48
PILL_RADIUS = 18

ICON_FOR_MODE = {
    "info": "i",
    "success": "✓",
    "warning": "!",
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
    """Colores del diálogo según el tema: negro o blanco."""
    if dark:
        return {
            "bg": "#1c1c1e",
            "border": "rgba(255, 255, 255, 0.12)",
            "title": "#ffffff",
            "message": "rgba(235, 235, 245, 0.72)",
            "btn_text": "#ffffff",
            "ghost_hover": "rgba(255, 255, 255, 0.06)",
            "ghost_pressed": "rgba(255, 255, 255, 0.12)",
            "btn_disabled": "rgba(255, 255, 255, 0.30)",
        }
    return {
        "bg": "#ffffff",
        "border": "rgba(0, 0, 0, 0.12)",
        "title": "#1c1c1e",
        "message": "rgba(60, 60, 67, 0.72)",
        "btn_text": "#1c1c1e",
        "ghost_hover": "rgba(0, 0, 0, 0.05)",
        "ghost_pressed": "rgba(0, 0, 0, 0.10)",
        "btn_disabled": "rgba(0, 0, 0, 0.30)",
    }


class AlertDialog(QDialog):
    """Alerta modal con icono circular y botones en píldora que flotan."""

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
                border-radius: {CARD_RADIUS}px;
            }}
            """
        )
        outer.addWidget(card)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 26, 28, 18)
        card_layout.setSpacing(0)

        # Icono en círculo relleno con el glifo en blanco.
        icon_label = QLabel(ICON_FOR_MODE[self._mode])
        icon_label.setObjectName("AlertIcon")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedSize(ICON_DIAMETER, ICON_DIAMETER)
        icon_label.setStyleSheet(
            f"QLabel#AlertIcon{{background:{self._accent};color:#ffffff;"
            f"border:none;border-radius:{ICON_DIAMETER // 2}px;"
            f"font-size:24px;font-weight:700;}}"
        )
        card_layout.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignHCenter)

        # Título
        title_label = QLabel(title)
        title_label.setObjectName("AlertTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)
        title_label.setStyleSheet(
            f"QLabel#AlertTitle{{color:{pal['title']};font-size:17px;"
            f"font-weight:600;background:transparent;margin-top:14px;}}"
        )
        card_layout.addWidget(title_label)

        # Mensaje
        msg_label = QLabel(message)
        msg_label.setObjectName("AlertMessage")
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet(
            f"QLabel#AlertMessage{{color:{pal['message']};font-size:13px;"
            f"background:transparent;margin-top:8px;}}"
        )
        card_layout.addWidget(msg_label)

        card_layout.addSpacing(22)

        # Botones: flotan, sin separadores ni líneas duras.
        default_index = self._default_index()
        card_layout.addLayout(self._make_button_row(pal, default_index))

    def _default_index(self) -> int:
        """Índice del botón principal (el que acepta)."""
        for index, text in enumerate(self._buttons):
            if _is_accept_text(text):
                return index
        return len(self._buttons) - 1

    def _make_button_row(self, pal: dict, default_index: int) -> QHBoxLayout:
        """Un solo botón centrado (iOS); dos o más alineados a la derecha (UWP)."""
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        # Margen inferior del diálogo: el botón no toca el borde de la tarjeta.
        if len(self._buttons) == 1:
            row.addStretch()
            row.addWidget(self._make_button(self._buttons[0], 0 == default_index, pal))
            row.addStretch()
        else:
            row.addStretch()
            for index, text in enumerate(self._buttons):
                row.addWidget(self._make_button(text, index == default_index, pal))
        return row

    def _make_button(self, text: str, is_default: bool, pal: dict) -> QPushButton:
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setMinimumHeight(40)
        btn.setMinimumWidth(96)
        btn.setDefault(is_default)
        btn.setAutoDefault(False)
        if is_default:
            background = self._accent
            color = "#ffffff"
            hover = "rgba(255, 255, 255, 0.18)"
            pressed = "rgba(0, 0, 0, 0.16)"
        else:
            background = "transparent"
            color = pal["btn_text"]
            hover = pal["ghost_hover"]
            pressed = pal["ghost_pressed"]
        btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {background};
                color: {color};
                border: none;
                border-radius: {PILL_RADIUS}px;
                font-size: 14px;
                font-weight: 600;
                padding: 8px 20px;
            }}
            QPushButton:hover {{ background: {hover}; }}
            QPushButton:pressed {{ background: {pressed}; }}
            QPushButton:focus {{ outline: none; }}
            QPushButton:disabled {{ color: {pal['btn_disabled']}; }}
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
