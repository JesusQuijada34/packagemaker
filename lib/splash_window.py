# -*- coding: utf-8 -*-
"""Splash integrado estilo UWP: ventana frameless con el icono centrado.

Extraído del monolito ``packagemaker.py`` (Fase 1.1 de ``bugs.txt``) para que el
índice quede limpio. No depende de PackageMaker: sólo de Qt y del acento que se
le pasa explícitamente, de modo que se puede importar sin ciclos.
"""
from __future__ import annotations

import os

from lib.design_tokens import ACCENT
from lib.fluent_theme import splash_container_stylesheet

try:
    from PyQt6.QtCore import QEasingCurve, Qt, QPropertyAnimation, pyqtSignal
    from PyQt6.QtGui import QPixmap
    from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
except ImportError:  # pragma: no cover - entorno sin GUI

    class _NoopSignal:
        def __init__(self, *args, **kwargs):
            pass

        def connect(self, *args, **kwargs):
            pass

        def emit(self, *args, **kwargs):
            pass

    def pyqtSignal(*args, **kwargs):  # type: ignore
        return _NoopSignal()

    class QWidget:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

    class QLabel(QWidget):  # type: ignore
        pass

    class QVBoxLayout(QWidget):  # type: ignore
        pass

    class QPixmap:  # type: ignore
        pass

    class QPropertyAnimation:  # type: ignore
        pass

    class QEasingCurve:  # type: ignore
        class Type:
            OutCubic = 0

    class Qt:  # type: ignore
        class WindowType:
            FramelessWindowHint = 0
            WindowStaysOnTopHint = 0

        class WidgetAttribute:
            WA_TranslucentBackground = 0

        class AspectRatioMode:
            KeepAspectRatio = 0

        class TransformationMode:
            SmoothTransformation = 0

        class AlignmentFlag:
            AlignCenter = 0


class IntegratedSplash(QWidget):
    """Splash integrado estilo UWP - minimalista con solo icono centrado."""

    finished = pyqtSignal()

    def __init__(self, parent=None, icon_path=None, title="Package Maker", accent=None):
        super().__init__(parent)
        self.parent = parent
        self.accent = str(accent or ACCENT)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(0, 0, parent.width(), parent.height())
        self.setStyleSheet(splash_container_stylesheet(self.accent))

        container = QWidget(self)
        container.setObjectName("SplashContainer")
        container.setGeometry(0, 0, self.width(), self.height())

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()

        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if icon_path and os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    180, 180,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.icon_label.setPixmap(scaled)
        layout.addWidget(self.icon_label)

        layout.addStretch()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.parent:
            self.setGeometry(0, 0, self.parent.width(), self.parent.height())
            container = self.findChild(QWidget, "SplashContainer")
            if container:
                container.setGeometry(0, 0, self.width(), self.height())

    def show_splash(self):
        """Muestra el splash sin temporizador: actúa como compuerta lógica.

        Permanece visible hasta que la validación de sesión decide si hay que
        revelar el landing o entrar directamente al IDE (``finish``).
        """
        self.show()
        self.raise_()

    def finish(self):
        """Cierra el splash con el desvanecido (lo llama la compuerta de sesión)."""
        self._finish_splash()

    def _finish_splash(self):
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(600)
        self.fade_anim.setStartValue(1.0)
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_anim.finished.connect(self._close_and_emit)
        self.fade_anim.start()

    def _close_and_emit(self):
        self.hide()
        self.finished.emit()
        self.deleteLater()
