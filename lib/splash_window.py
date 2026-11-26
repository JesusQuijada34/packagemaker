# -*- coding: utf-8 -*-
"""Splash integrado estilo UWP: ventana frameless con el icono centrado.

Extraído del monolito ``packagemaker.py`` (Fase 1.1 de ``bugs.txt``) para que el
índice quede limpio. No depende de PackageMaker: sólo de Qt y del acento que se
le pasa explícitamente, de modo que se puede importar sin ciclos.

Sin padre el splash es una **ventana de nivel superior** que ocupa la pantalla
disponible. Es lo que exige la coreografía de arranque (F-003): pintarlo antes
de construir la interfaz. Como ventana hija translúcida, Qt creaba ventanas
nativas auxiliares en Windows (avisos ``must be a top level window`` y ventanas
vacías apareciendo y desapareciendo antes del primer fotograma).
"""
from __future__ import annotations

import os

from lib.design_tokens import ACCENT
from lib.fluent_theme import splash_container_stylesheet

try:
    from PyQt6.QtCore import QEasingCurve, Qt, QPropertyAnimation, pyqtSignal
    from PyQt6.QtGui import QPixmap
    from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
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

    class QApplication:  # type: ignore
        @staticmethod
        def instance():
            return None

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
        self._host = parent
        self.title = title
        self.accent = str(accent or ACCENT)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._sync_geometry()
        self.setStyleSheet(splash_container_stylesheet(self.accent))

        container = QWidget(self)
        container.setObjectName("SplashContainer")
        container.setGeometry(0, 0, self.width(), self.height())
        self._container = container

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

    def _sync_geometry(self):
        """Sitúa el splash según tenga o no ventana anfitriona.

        Sin padre ocupa la pantalla disponible (el desvanecido se ve como una
        cortina). Con padre conserva el modo de superposición heredado, que ya
        no usa el arranque de la aplicación.
        """
        if self._host is not None:
            self.setGeometry(0, 0, self._host.width(), self._host.height())
            return
        screen = None
        try:
            screen = self.screen()
        except Exception:  # pragma: no cover - respaldo sin Qt
            screen = None
        if screen is not None:
            self.setGeometry(screen.availableGeometry())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        container = getattr(self, "_container", None)
        if container is not None:
            container.setGeometry(0, 0, self.width(), self.height())

    def show_splash(self):
        """Muestra el splash sin temporizador: actúa como compuerta lógica.

        Permanece visible hasta que la validación de sesión decide si hay que
        revelar el landing o entrar directamente al IDE (``finish``). Se sube y
        se activa porque es una ventana de nivel superior creada antes que la
        ventana principal.
        """
        self.show()
        self.raise_()
        try:
            self.activateWindow()
        except Exception:  # pragma: no cover - gestor de ventanas sin foco
            pass

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
        # Libera la ventana nativa antes de que Qt borre el objeto: sin esto
        # Windows puede dejar la ventana por capas del splash colgada.
        try:
            self.destroy()
        except Exception:  # pragma: no cover - respaldo sin Qt
            pass
        self.deleteLater()
