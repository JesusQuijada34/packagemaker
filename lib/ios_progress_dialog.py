# -*- coding: utf-8 -*-
"""Diálogo de progreso estilo iOS con blur temporal y fundido.

Pensado para operaciones largas (crear proyecto, compilar, verificar):
- Oscurece el fondo detrás del diálogo y aplica un desenfoque temporal.
- El texto de estado es el título de la barra.
- Barra de progreso marquee mientras la duración es desconocida; si el
  entorno es lento se cambia a progreso en vivo con valor real.
- Aparece y desaparece con un fundido (fade) suave.
"""

from __future__ import annotations

from typing import Optional

try:
    from PyQt6.QtCore import (
        QEasingCurve,
        QEvent,
        QPropertyAnimation,
        Qt,
        QTimer,
    )
    from PyQt6.QtGui import QColor, QPainter
    from PyQt6.QtWidgets import (
        QApplication,
        QDialog,
        QGraphicsOpacityEffect,
        QLabel,
        QProgressBar,
        QVBoxLayout,
        QWidget,
    )

    PYQT6_AVAILABLE = True
except ImportError:  # pragma: no cover - entorno sin Qt
    PYQT6_AVAILABLE = False

    class QDialog:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            pass


# A partir de este tiempo (ms) sin progreso reportado se asume entorno lento
# y la barra pasa de marquee indeterminado a progreso en vivo.
SLOW_ENVIRONMENT_MS = 2500

DIALOG_WIDTH = 380
DIALOG_HEIGHT = 150
FADE_MS = 220


class _DimOverlay(QWidget):
    """Capa que oscurece el fondo detrás del diálogo."""

    def __init__(self, parent: QWidget, alpha: int = 140):
        super().__init__(parent)
        self._alpha = alpha
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

    def paintEvent(self, event):  # noqa: N802 (API Qt)
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, self._alpha))
        painter.end()


class IOSProgressDialog(QDialog):
    """Diálogo modal tipo iOS: título de estado + barra + blur + fundido."""

    def __init__(self, parent: Optional[QWidget], title: str = "", message: str = ""):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setFixedSize(DIALOG_WIDTH, DIALOG_HEIGHT)

        self._indeterminate = True
        self._blur_builder = None
        self._overlay = None
        self._fade = None

        self._build_ui(title, message)
        self._slow_timer = QTimer(self)
        self._slow_timer.setSingleShot(True)
        self._slow_timer.timeout.connect(self._on_slow_environment)

    # -- construcción -------------------------------------------------
    def _build_ui(self, title: str, message: str) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self.card = QWidget(self)
        self.card.setObjectName("IOSProgressCard")
        self.card.setStyleSheet(
            """
            QWidget#IOSProgressCard {
                background: rgba(28, 28, 30, 235);
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 16px;
            }
            QLabel#IOSProgressTitle {
                color: #ffffff;
                font-size: 15px;
                font-weight: 600;
                background: transparent;
            }
            QLabel#IOSProgressMessage {
                color: rgba(235, 235, 245, 0.72);
                font-size: 12px;
                background: transparent;
            }
            QProgressBar {
                background: rgba(255, 255, 255, 0.12);
                border: none;
                border-radius: 3px;
                height: 6px;
                text-align: center;
                color: transparent;
            }
            QProgressBar::chunk {
                background: #0a84ff;
                border-radius: 3px;
            }
            """
        )
        outer.addWidget(self.card)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(22, 20, 22, 20)
        card_layout.setSpacing(10)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("IOSProgressTitle")
        self.title_label.setWordWrap(True)
        card_layout.addWidget(self.title_label)

        self.message_label = QLabel(message)
        self.message_label.setObjectName("IOSProgressMessage")
        self.message_label.setWordWrap(True)
        card_layout.addWidget(self.message_label)

        self.progress = QProgressBar()
        self.progress.setFixedHeight(6)
        self.progress.setTextVisible(False)
        self.set_indeterminate(True)
        card_layout.addWidget(self.progress)

        card_layout.addStretch()

    # -- estado -------------------------------------------------------
    def set_title(self, text: str) -> None:
        """El texto de estado es el título de la barra del diálogo."""
        self.title_label.setText(text)
        self.setWindowTitle(text)

    def set_message(self, text: str) -> None:
        self.message_label.setText(text)

    def set_indeterminate(self, enabled: bool = True) -> None:
        self._indeterminate = bool(enabled)
        if self._indeterminate:
            self.progress.setRange(0, 0)
        else:
            self.progress.setRange(0, 100)

    def set_progress(self, value: int, maximum: int = 100) -> None:
        """Reporta progreso real; sale del modo marquee automáticamente."""
        if self._indeterminate:
            self.set_indeterminate(False)
        self.progress.setMaximum(max(1, int(maximum)))
        self.progress.setValue(int(value))

    def _on_slow_environment(self) -> None:
        """Entorno lento: marquee tanteado con progreso en vivo."""
        if not self._indeterminate:
            return
        self.set_message("El entorno es lento; midiendo el progreso real...")
        self.progress.setRange(0, 0)
        self.progress.setProperty("slow", True)

    def start_slow_watchdog(self) -> None:
        self._slow_timer.start(SLOW_ENVIRONMENT_MS)

    def stop_slow_watchdog(self) -> None:
        self._slow_timer.stop()

    # -- efectos ------------------------------------------------------
    def _apply_blur(self) -> None:
        """Blur temporal (macOS advantage) sobre el diálogo."""
        try:
            from leviathan_ui import WipeWindow

            self._blur_builder = WipeWindow.create().set_mode("ghostBlur").set_radius(16)
            self._blur_builder.apply(self)
        except Exception:
            self._blur_builder = None

    def _create_overlay(self) -> None:
        parent = self.parent()
        if parent is None:
            return
        self._overlay = _DimOverlay(parent)
        self._overlay.setGeometry(parent.rect())
        self._overlay.show()
        self._overlay.raise_()

    def _center_on_parent(self) -> None:
        parent = self.parent()
        if parent is None:
            return
        geo = parent.frameGeometry()
        self.move(
            geo.center().x() - self.width() // 2,
            geo.center().y() - self.height() // 2,
        )

    def _fade_in(self) -> None:
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        self._fade = QPropertyAnimation(effect, b"opacity", self)
        self._fade.setDuration(FADE_MS)
        self._fade.setStartValue(0.0)
        self._fade.setEndValue(1.0)
        self._fade.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._fade.start()

    def showEvent(self, event):  # noqa: N802 (API Qt)
        super().showEvent(event)
        self._create_overlay()
        self._apply_blur()
        self._center_on_parent()
        self._fade_in()
        self.start_slow_watchdog()

    def closeEvent(self, event):  # noqa: N802 (API Qt)
        self.stop_slow_watchdog()
        if self._overlay is not None:
            self._overlay.hide()
            self._overlay.deleteLater()
            self._overlay = None
        super().closeEvent(event)

    def finish(self, delay_ms: int = 0) -> None:
        """Cierra el diálogo con fundido de salida."""
        if delay_ms > 0:
            QTimer.singleShot(delay_ms, self._fade_out_and_close)
        else:
            self._fade_out_and_close()

    def _fade_out_and_close(self) -> None:
        effect = self.graphicsEffect()
        if effect is None:
            self.accept()
            return
        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(FADE_MS)
        anim.setStartValue(effect.opacity())
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.InCubic)
        anim.finished.connect(self.accept)
        anim.start()
        self._fade = anim


def show_ios_progress(parent, title: str, message: str = "") -> IOSProgressDialog:
    """Crea y muestra el diálogo iOS con fundido de entrada."""
    dialog = IOSProgressDialog(parent, title, message)
    dialog.show()
    QApplication.processEvents()
    return dialog
