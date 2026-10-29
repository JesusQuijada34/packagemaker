# -*- coding: utf-8 -*-
"""Efecto parcial de fondo para diálogos: atenuado + desenfoque.

A diferencia de un simple oscurecido, esta capa desenfoca el contenido de la
ventana principal y lo atenúa suavemente, de modo que el diálogo destaca sin
tapar por completo lo que hay detrás.
"""

from __future__ import annotations

from typing import Optional

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QColor, QPainter
    from PyQt6.QtWidgets import QGraphicsBlurEffect, QWidget

    PYQT6_AVAILABLE = True
except ImportError:  # pragma: no cover - entorno sin Qt
    PYQT6_AVAILABLE = False

    class QWidget:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            pass


OVERLAY_ALPHA = 96
OVERLAY_BLUR_RADIUS = 14


class PartialEffectOverlay(QWidget):
    """Capa parcial: atenúa y desenfoca el contenido detrás de un diálogo."""

    def __init__(self, parent: QWidget, alpha: int = OVERLAY_ALPHA):
        super().__init__(parent)
        self._alpha = alpha
        self._blur = None
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setGeometry(parent.rect())
        self._apply_blur()

    def _apply_blur(self) -> None:
        """Desenfoque del contenido de la ventana principal."""
        try:
            from leviathan_ui import WipeWindow

            # ghostBlur difumina el contenido de debajo (Windows).
            self._blur = (
                WipeWindow.create()
                .set_mode("ghostBlur")
                .set_radius(0)
                .set_blur(OVERLAY_BLUR_RADIUS)
                .apply(self)
            )
            return
        except Exception:
            self._blur = None
        # Fallback multiplataforma: QGraphicsBlurEffect sobre la capa.
        try:
            effect = QGraphicsBlurEffect(self)
            effect.setBlurRadius(OVERLAY_BLUR_RADIUS)
            self.setGraphicsEffect(effect)
        except Exception:
            pass

    def paintEvent(self, event):  # noqa: N802 (API Qt)
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, self._alpha))
        painter.end()

    def resize_to_parent(self) -> None:
        parent = self.parent()
        if parent is not None:
            self.setGeometry(parent.rect())

    def teardown(self) -> None:
        """Quita la capa y su efecto de forma segura e idempotente."""
        try:
            self.hide()
            self.deleteLater()
        except RuntimeError:
            pass


def install_partial_effect(dialog, parent: Optional[QWidget]):
    """Coloca la capa parcial sobre ``parent`` y la devuelve.

    Devuelve ``None`` si no hay padre o no hay Qt disponible.
    """
    if not PYQT6_AVAILABLE or parent is None:
        return None
    overlay = PartialEffectOverlay(parent)
    overlay.show()
    overlay.raise_()
    return overlay
