# -*- coding: utf-8 -*-
"""Application Frame Host: única ventana superior de Package Maker.

El host se muestra primero con el splash como primer frame. La ventana de la
aplicación se construye después, dentro del mismo frame, y nunca se presenta
como una segunda ventana independiente. El diseño sigue el patrón
ApplicationFrameWindow/Frame de UWP: una raíz estable que aloja las páginas.
"""
from __future__ import annotations

from PyQt6.QtCore import QEvent, Qt, QTimer
from PyQt6.QtWidgets import QMainWindow, QSizePolicy, QStackedWidget, QWidget


class ApplicationFrameHost(QMainWindow):
    """Ventana raíz persistente que hospeda splash y aplicación principal."""

    def __init__(self, splash: QWidget, *, title: str, icon=None, size=(1024, 720), parent=None):
        super().__init__(parent)
        self.setObjectName("PackageMakerApplicationFrameHost")
        self.setWindowTitle(str(title))
        if icon is not None:
            self.setWindowIcon(icon)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setAutoFillBackground(True)
        self.resize(*size)

        self._stack = QStackedWidget(self)
        self._stack.setObjectName("ApplicationFrame")
        self._stack.setContentsMargins(0, 0, 0, 0)
        self._stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setCentralWidget(self._stack)

        self._splash = splash
        self._main_widget = None
        self._closing = False
        # El splash es una página del frame, no una segunda ventana flotante.
        self._splash.setParent(self._stack)
        self._splash.setWindowFlags(Qt.WindowType.Widget)
        self._splash.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._stack.addWidget(self._splash)
        self._stack.setCurrentWidget(self._splash)

    @property
    def main_widget(self):
        return self._main_widget

    @property
    def splash_widget(self):
        return self._splash

    def show_splash(self) -> None:
        """Publica el frame con el splash antes de construir la UI pesada."""
        self._stack.setCurrentWidget(self._splash)
        self.show()
        self.raise_()
        self._splash.show()

    def mount_main_widget(self, widget: QWidget) -> None:
        """Monta la ventana principal como contenido del frame existente."""
        if widget is None:
            raise ValueError("main widget cannot be None")
        if self._main_widget is widget:
            self._stack.setCurrentWidget(widget)
            return
        if self._main_widget is not None:
            self._stack.removeWidget(self._main_widget)
            self._main_widget.removeEventFilter(self)
            self._main_widget.setParent(None)

        self._main_widget = widget
        # QMainWindow pasa a ser un widget de contenido, no una ventana top-level.
        widget.setParent(self._stack)
        widget.setWindowFlags(Qt.WindowType.Widget)
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        widget.installEventFilter(self)
        self._stack.addWidget(widget)
        widget.hide()

    def reveal_main(self) -> None:
        """Cambia del splash al contenido principal sin crear otra ventana."""
        if self._main_widget is None:
            return
        self._stack.setCurrentWidget(self._main_widget)
        self._splash.hide()
        self._main_widget.show()
        self._main_widget.raise_()

    def eventFilter(self, watched, event):
        if watched is self._main_widget and event.type() == QEvent.Type.Close:
            # El botón Cerrar pertenece al contenido. Cerrar el contenido debe
            # cerrar el único frame top-level para no dejar una ventana vacía.
            if not self._closing:
                QTimer.singleShot(0, self.close)
        return super().eventFilter(watched, event)

    def closeEvent(self, event):
        self._closing = True
        widget = self._main_widget
        if widget is not None and widget.isVisible():
            try:
                widget.removeEventFilter(self)
                widget.close()
            except RuntimeError:
                pass
        super().closeEvent(event)
