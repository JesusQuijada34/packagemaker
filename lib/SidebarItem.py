# -*- coding: utf-8 -*-
"""Ítem de navegación lateral con indicador de selección propio.

El indicador es una barra corta y redondeada pegada al borde izquierdo y
centrada verticalmente, en vez del ``border-left`` de altura completa. El color
del texto sigue al tema (claro/oscuro) para que el ítem seleccionado no quede
invisible sobre el fondo claro.
"""

from __future__ import annotations

import os

try:
    from PyQt6.QtCore import QRect, QSize, Qt
    from PyQt6.QtGui import QColor, QIcon, QPainter
    from PyQt6.QtWidgets import QPushButton

    PYQT6_AVAILABLE = True
except ImportError:  # pragma: no cover - entorno sin Qt
    PYQT6_AVAILABLE = False

    class QPushButton:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            pass

        def setFixedHeight(self, *args):
            pass

        def setIconSize(self, *args):
            pass

        def setIcon(self, *args):
            pass

    class QIcon:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            pass

    QPainter = None  # type: ignore[assignment]
    QRect = None  # type: ignore[assignment]
    QColor = None  # type: ignore[assignment]


from lib.design_tokens import (
    ACCENT,
    CONTROL_RADIUS,
    FONT_STACK,
    SIDEBAR_ICON_INSET,
    SIDEBAR_INDICATOR_HEIGHT,
    SIDEBAR_INDICATOR_WIDTH,
    SIDEBAR_ITEM_HEIGHT,
    TEXT,
    TEXT_MUTED,
)
from lib.hover_animation import enable_hover_fade

# Paletas por tema para el texto del ítem (normal, seleccionado).
TEXT_COLORS = {
    True: {"normal": TEXT_MUTED, "selected": TEXT},
    False: {"normal": "#334155", "selected": ACCENT},
}
HOVER_COLORS = {
    True: {"bg": "rgba(255, 255, 255, 0.07)", "selected_bg": "rgba(255, 255, 255, 0.12)"},
    False: {"bg": "rgba(15, 23, 42, 0.07)", "selected_bg": "rgba(0, 120, 212, 0.18)"},
}


class SidebarItem(QPushButton):
    """Botón de navegación lateral con modo compacto Fluent."""

    def __init__(self, text, icon=None, parent=None, dark=True):
        super().__init__(text, parent)
        self._label_text = text
        self._compact = False
        self._dark = bool(dark)
        self.setFixedHeight(SIDEBAR_ITEM_HEIGHT)
        self.setIconSize(QSize(24, 24))
        if isinstance(icon, QIcon):
            self.setIcon(icon)
        elif icon and os.path.exists(str(icon)):
            self.setIcon(QIcon(str(icon)))
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style()
        # El ítem seleccionado ya tiene su propio color; no se anima su fondo.
        self._hover_fade = enable_hover_fade(
            self,
            HOVER_COLORS[self._dark]["bg"],
            only_when=lambda: not self.isChecked(),
        )

    def set_label_text(self, text):
        self._label_text = text
        self.setText("" if self._compact else text)
        self.setToolTip(text if self._compact else "")

    def set_compact(self, compact):
        self._compact = bool(compact)
        self.set_label_text(self._label_text)
        self._apply_style()
        fade = getattr(self, "_hover_fade", None)
        if fade is not None:
            fade.refresh()

    def set_dark(self, dark):
        """Ajusta los colores al tema activo (claro u oscuro)."""
        dark = bool(dark)
        if dark == self._dark:
            return
        self._dark = dark
        self._apply_style()
        fade = getattr(self, "_hover_fade", None)
        if fade is not None:
            fade.set_hover_color(HOVER_COLORS[dark]["bg"])

    def _apply_style(self):
        palette = TEXT_COLORS[self._dark]
        hover = HOVER_COLORS[self._dark]
        # El indicador lo pinta ``paintEvent``; el QSS deja el borde libre.
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {palette['normal']};
                text-align: left;
                padding: 0 10px 0 {SIDEBAR_ICON_INSET}px;
                border: none;
                border-radius: {CONTROL_RADIUS}px;
                font-family: {FONT_STACK};
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {hover['bg']};
                color: {palette['selected']};
            }}
            QPushButton:checked {{
                background-color: {hover['selected_bg']};
                color: {palette['selected']};
            }}
            QPushButton:focus {{
                outline: none;
            }}
        """)
        if self._compact:
            self.setStyleSheet(self.styleSheet() + """
                QPushButton {
                    text-align: center;
                    padding: 0;
                }
            """)

    # -- indicador de selección ---------------------------------------
    def paintEvent(self, event):  # noqa: N802 (API Qt)
        super().paintEvent(event)
        if not self.isChecked() or not PYQT6_AVAILABLE:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(ACCENT))
        y = (self.height() - SIDEBAR_INDICATOR_HEIGHT) // 2
        painter.drawRoundedRect(
            QRect(0, y, SIDEBAR_INDICATOR_WIDTH, SIDEBAR_INDICATOR_HEIGHT),
            SIDEBAR_INDICATOR_WIDTH / 2,
            SIDEBAR_INDICATOR_WIDTH / 2,
        )
        painter.end()
