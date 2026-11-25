# -*- coding: utf-8 -*-
"""Barra de actividad fina bajo la barra de acciones.

Sustituye al diálogo con barra de progreso: la barra está siempre presente,
inactiva, y empieza a deslizarse cuando hay trabajo en segundo plano
(guardar ajustes, aplicar un cambio, empaquetar...). Es combinable con el
acento de la aplicación y nunca bloquea la interfaz.
"""

from __future__ import annotations

from lib.design_tokens import ACCENT, active_accent

try:
    from PyQt6.QtCore import QTimer, Qt
    from PyQt6.QtGui import QColor, QPainter
    from PyQt6.QtWidgets import QWidget

    PYQT6_AVAILABLE = True
except ImportError:  # pragma: no cover - entorno sin Qt (CLI headless)
    PYQT6_AVAILABLE = False

    class QWidget:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            pass


BAR_HEIGHT = 3
# Fracción del ancho que ocupa el segmento que se desliza.
SEGMENT_RATIO = 0.28
STEP_MS = 16
STEP_RATIO = 0.012


class ActivityBar(QWidget):
    """Barra marquee fina: inactiva en reposo, animada con trabajo pendiente."""

    def __init__(self, parent=None, accent: str | None = None):
        super().__init__(parent)
        self._accent = QColor(accent or active_accent() or ACCENT)
        self._offset = 0.0
        self._active = False
        self._timer = None
        if not PYQT6_AVAILABLE:
            return
        self.setFixedHeight(BAR_HEIGHT)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._timer = QTimer(self)
        self._timer.setInterval(STEP_MS)
        self._timer.timeout.connect(self._advance)

    # -- estado ----------------------------------------------------------- #
    def is_active(self) -> bool:
        return self._active

    def set_accent(self, accent: str) -> None:
        self._accent = QColor(accent or ACCENT)
        self.update()

    def start(self) -> None:
        """Despierta el marquee; idempotente."""
        if not PYQT6_AVAILABLE or self._active:
            return
        self._active = True
        if self._timer is not None:
            self._timer.start()
        self.update()

    def stop(self) -> None:
        """Vuelve al reposo; la barra sigue visible pero quieta."""
        if not PYQT6_AVAILABLE:
            return
        self._active = False
        if self._timer is not None:
            self._timer.stop()
        self.update()

    # -- pintura ---------------------------------------------------------- #
    def _advance(self) -> None:
        self._offset = (self._offset + STEP_RATIO) % 1.0
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802 - nombre impuesto por Qt
        if not PYQT6_AVAILABLE:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        width = self.width()
        height = self.height()

        track = QColor(self._accent)
        track.setAlpha(28 if self._active else 16)
        painter.fillRect(0, 0, width, height, track)

        if not self._active:
            return

        segment = max(24, int(width * SEGMENT_RATIO))
        # El recorrido empieza fuera del borde izquierdo para que el segmento
        # entre y salga en lugar de aparecer cortado.
        span = width + segment
        x = int(self._offset * span) - segment

        color = QColor(self._accent)
        painter.fillRect(x, 0, segment, height, color)
        painter.end()
