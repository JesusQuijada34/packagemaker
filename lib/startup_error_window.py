# -*- coding: utf-8 -*-
"""Ventana solitaria de error de arranque (bugs.txt Fase 2.2).

Cuando el arranque falla antes de que exista la ventana principal, el splash no
puede simplemente desaparecer: se convierte en esta ventana, con la misma barra
de título personalizada del resto de la aplicación, un título centrado y un
subtítulo con el error interno enriquecido.

Se destruye con ``destroy()`` tras devolver el código de salida, para no dejar
frames huérfanos encima de otras aplicaciones.
"""
from __future__ import annotations

import sys
from typing import Optional

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QApplication,
        QFrame,
        QLabel,
        QPushButton,
        QScrollArea,
        QVBoxLayout,
        QWidget,
    )

    PYQT6_AVAILABLE = True
except (ImportError, SyntaxError):  # pragma: no cover - entorno sin GUI
    PYQT6_AVAILABLE = False

    class QWidget:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            pass

    class QLabel(QWidget):  # type: ignore[no-redef]
        pass

    class QPushButton(QWidget):  # type: ignore[no-redef]
        pass

    class QFrame(QWidget):  # type: ignore[no-redef]
        pass

    class QScrollArea(QWidget):  # type: ignore[no-redef]
        pass

    class QVBoxLayout(QWidget):  # type: ignore[no-redef]
        pass

    class QApplication:  # type: ignore[no-redef]
        @staticmethod
        def instance():
            return None

        def __init__(self, *args, **kwargs):
            pass

        def exec(self):
            return 0

    class Qt:  # type: ignore[no-redef]
        class AlignmentFlag:
            AlignCenter = 0

        class WindowType:
            FramelessWindowHint = 0


from lib.fluent_theme import error_container_stylesheet
from lib.i18n import tr

EXIT_CODE_INTERNAL_ERROR = 1


class StartupErrorWindow(QWidget):
    """Ventana frameless con barra de título propia y el error enriquecido."""

    def __init__(self, title: str, detail: str, *, icon_path: Optional[str] = None, accent: Optional[str] = None):
        super().__init__()
        self.setObjectName("StartupErrorWindow")
        self.setWindowTitle(str(title))
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.resize(720, 460)

        self._title = str(title)
        self._detail = str(detail)
        self._icon_path = icon_path
        self._accent = accent
        self.titlebar = None
        self.title_label = None
        self.detail_label = None
        self.btn_close = None

        if not PYQT6_AVAILABLE:
            return

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.titlebar = self._build_titlebar()
        if self.titlebar is not None:
            layout.addWidget(self.titlebar)

        body = QFrame()
        body.setObjectName("StartupErrorBody")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(48, 32, 48, 32)
        body_layout.setSpacing(16)

        self.title_label = QLabel(self._title)
        self.title_label.setObjectName("StartupErrorTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)
        body_layout.addWidget(self.title_label)

        scroll = QScrollArea()
        scroll.setObjectName("StartupErrorScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.detail_label = QLabel(self._detail)
        self.detail_label.setObjectName("StartupErrorDetail")
        self.detail_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.detail_label.setWordWrap(True)
        self.detail_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        scroll.setWidget(self.detail_label)
        body_layout.addWidget(scroll, 1)

        self.btn_close = QPushButton(tr("common.close"))
        self.btn_close.setObjectName("StartupErrorClose")
        self.btn_close.clicked.connect(self.close)
        body_layout.addWidget(self.btn_close, 0, Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(body, 1)
        self.setStyleSheet(error_container_stylesheet(self._accent or "#0078D4"))

    def _build_titlebar(self):
        try:
            from lib import leviathan_bridge

            titlebar_cls = leviathan_bridge.attribute("CustomTitleBar")
        except (ImportError, AttributeError):
            return None
        bar = titlebar_cls(self, title=self._title, icon=self._icon_path or "")
        bar.btn_max.hide()
        return bar

    def destroy(self) -> None:
        """Cierra y libera el frame para que no quede encima de otras ventanas."""
        try:
            self.close()
        finally:
            self.deleteLater()


def show_startup_error(title: str, detail: str, *, icon_path: Optional[str] = None, accent: Optional[str] = None) -> int:
    """Muestra la ventana de error y devuelve el código de salida.

    Si no hay PyQt6 disponible el error se escribe en ``stderr`` y se devuelve
    el mismo código: el arranque nunca se queda colgado sin explicación.
    """
    if not PYQT6_AVAILABLE:
        print(f"{title}\n\n{detail}", file=sys.stderr)
        return EXIT_CODE_INTERNAL_ERROR

    app = QApplication.instance() or QApplication(sys.argv[:1])
    window = StartupErrorWindow(title, detail, icon_path=icon_path, accent=accent)
    window.show()
    app.exec()
    window.destroy()
    return EXIT_CODE_INTERNAL_ERROR
