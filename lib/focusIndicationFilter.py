#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Focus Indication Filter for Package Maker
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QObject, QEvent, QPoint, QRect, Qt
from PyQt6.QtGui import QColor, QPainter


class FocusIndicationFilter(QObject):
    """Filtro de eventos para simular el indicador de foco estilo UWP."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.indicator = QWidget(None)  # Ventana independiente (tool window) o overlay
        self.indicator.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowTransparentForInput | Qt.WindowType.NoDropShadowWindowHint)
        self.indicator.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.indicator.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        # Color por defecto (se actualizará con el tema)
        self.indicator.setStyleSheet("background-color: #f9826c; border-radius: 2px;")
        self.indicator.hide()
        self.current_widget = None

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.FocusIn:
            if isinstance(str(type(obj)), str) and ("QLineEdit" in str(type(obj)) or "QTextEdit" in str(type(obj)) or "QListWidget" in str(type(obj))):
                 self.update_indicator(obj)
        elif event.type() == QEvent.Type.FocusOut:
             if obj == self.current_widget:
                 self.indicator.hide()
                 self.current_widget = None
        elif event.type() == QEvent.Type.Move or event.type() == QEvent.Type.Resize:
             if obj == self.current_widget:
                 self.update_indicator(obj)

        return super().eventFilter(obj, event)

    def update_indicator(self, widget):
        self.current_widget = widget
        rect = widget.rect()
        # Convertir posicion local a global
        global_pos = widget.mapToGlobal(rect.topLeft())

        # Geometría de la barra vertical: a la izquierda, alto del widget, ancho 4px
        # Ajuste fino: un poco separado
        x = global_pos.x() - 6
        y = global_pos.y() + 4
        h = rect.height() - 8
        w = 4

        self.indicator.setGeometry(x, y, w, h)
        self.indicator.show()
        # Asegurar que esté encima
        self.indicator.raise_()