# -*- coding: utf-8 -*-
"""Splash integrado estilo UWP: ventana frameless con el icono centrado.

Extraído del monolito ``packagemaker.py`` (Fase 1.1 de ``bugs.txt``) para que el
índice quede limpio. No depende de PackageMaker: sólo de Qt y del acento que se
le pasa explícitamente, de modo que se puede importar sin ciclos.

Con padre el splash es un **overlay hijo** del área de contenido de esa ventana
(Q-032, patrón UWP): la ventana conserva su marco y su tamaño final desde el
primer fotograma, la interfaz se construye detrás y el splash se retira sin
abrir ni cerrar ninguna ventana adicional.

Sin padre el splash es una **ventana de nivel superior** que ocupa la pantalla
disponible; es el modo que usa el ``updater.py``. Como ventana hija translúcida,
Qt creaba ventanas nativas auxiliares en Windows (avisos ``must be a top level
window`` y ventanas vacías antes del primer fotograma), así que el overlay hijo
es opaco.
"""
from __future__ import annotations

import os

from lib.design_tokens import ACCENT
from lib.fluent_theme import splash_container_stylesheet

try:
    from PyQt6.QtCore import QEasingCurve, QEvent, Qt, QPropertyAnimation, pyqtSignal
    from PyQt6.QtGui import QPixmap
    from PyQt6.QtWidgets import (
        QApplication,
        QGraphicsOpacityEffect,
        QLabel,
        QVBoxLayout,
        QWidget,
    )
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

    class QGraphicsOpacityEffect(QWidget):  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

        def setOpacity(self, value):  # noqa: N802 - API de Qt
            pass

        def opacity(self):
            return 1.0

    class QEvent:  # type: ignore
        class Type:
            Resize = 0

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
    """Splash integrado estilo UWP - minimalista con solo icono centrado.

    Con ``parent`` es un overlay opaco que cubre el área de contenido de esa
    ventana; sin ``parent`` es una ventana de nivel superior a pantalla
    completa.
    """

    finished = pyqtSignal()

    def __init__(self, parent=None, icon_path=None, title="Package Maker", accent=None):
        super().__init__(parent)
        self._host = parent
        self.title = title
        self.accent = str(accent or ACCENT)
        self._fade_effect = None
        if parent is None:
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
            )
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        else:
            # Opaco a propósito: un hijo translúcido obliga a Qt a crear
            # ventanas nativas auxiliares en Windows.
            self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
            parent.installEventFilter(self)
        self._sync_geometry()
        self.setStyleSheet(splash_container_stylesheet(self.accent))

        container = QWidget(self)
        container.setObjectName("SplashContainer")
        container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
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

        Con anfitrión cubre su rectángulo completo (marco aparte); sin padre
        ocupa la pantalla disponible para que el desvanecido se vea como una
        cortina.
        """
        if self._host is not None:
            self.setGeometry(self._host.rect())
            self._sync_container()
            return
        screen = None
        try:
            screen = self.screen()
        except Exception:  # pragma: no cover - respaldo sin Qt
            screen = None
        if screen is not None:
            self.setGeometry(screen.availableGeometry())
            self._sync_container()

    def _sync_container(self):
        """Ajusta el contenedor al tamaño actual del splash.

        Un widget oculto no recibe ``resizeEvent`` hasta que se muestra, así
        que la geometría se sincroniza también aquí.
        """
        container = getattr(self, "_container", None)
        if container is not None:
            container.setGeometry(0, 0, self.width(), self.height())

    def eventFilter(self, obj, event):
        if obj is self._host and event.type() == QEvent.Type.Resize:
            self._sync_geometry()
            self.raise_()
        return super().eventFilter(obj, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._sync_container()

    def show_splash(self):
        """Muestra el splash sin temporizador: actúa como compuerta lógica.

        Permanece visible hasta que la validación de sesión decide si hay que
        revelar el landing o entrar directamente al IDE (``finish``). Con
        anfitrión se ajusta a su área y se sube sobre las páginas; sin él se
        activa como ventana propia.
        """
        if self._host is not None:
            self._sync_geometry()
        self.show()
        self.raise_()
        if self._host is None:
            try:
                self.activateWindow()
            except Exception:  # pragma: no cover - gestor de ventanas sin foco
                pass

    def finish(self):
        """Cierra el splash con el desvanecido (lo llama la compuerta de sesión)."""
        self._finish_splash()

    def _finish_splash(self):
        if self._host is not None:
            # ``windowOpacity`` no afecta a un widget hijo: el fundido tiene
            # que ir por un efecto de opacidad gráfica.
            effect = QGraphicsOpacityEffect(self)
            effect.setOpacity(1.0)
            self.setGraphicsEffect(effect)
            self._fade_effect = effect
            self.fade_anim = QPropertyAnimation(effect, b"opacity", self)
        else:
            self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(600)
        self.fade_anim.setStartValue(1.0)
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_anim.finished.connect(self._close_and_emit)
        self.fade_anim.start()

    def _close_and_emit(self):
        self.hide()
        if self._host is not None:
            self.fade_anim.setTargetObject(None)
            self.setGraphicsEffect(None)
            self._fade_effect = None
        else:
            # Libera la ventana nativa antes de que Qt borre el objeto: sin
            # esto Windows puede dejar la ventana por capas del splash colgada.
            try:
                self.destroy()
            except Exception:  # pragma: no cover - respaldo sin Qt
                pass
        self.finished.emit()
        self.deleteLater()
