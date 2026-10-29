# -*- coding: utf-8 -*-
"""Tirador para redimensionar el sidebar manualmente (estilo VS Code).

El ancho se ajusta arrastrando el borde; el resultado se comunica por
``on_resized`` para que la ventana lo persista entre sesiones.
"""

from __future__ import annotations

from typing import Callable, Optional

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QWidget

    PYQT6_AVAILABLE = True
except ImportError:  # pragma: no cover - entorno sin Qt
    PYQT6_AVAILABLE = False

    class QWidget:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            pass

    class Qt:  # type: ignore[no-redef]
        class CursorShape:
            SplitHCursor = None

            class _Mouse:
                LeftButton = None

            MouseButton = _Mouse


DEFAULT_MIN_WIDTH = 150
DEFAULT_MAX_WIDTH = 480
HANDLE_WIDTH = 5


class SidebarResizeHandle(QWidget):
    """Franja arrastrable que fija el ancho del sidebar."""

    def __init__(
        self,
        sidebar: QWidget,
        min_width: int = DEFAULT_MIN_WIDTH,
        max_width: int = DEFAULT_MAX_WIDTH,
        on_resized: Optional[Callable[[int], None]] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.sidebar = sidebar
        self.min_width = int(min_width)
        self.max_width = int(max_width)
        self.on_resized = on_resized
        self._dragging = False
        self._start_x = 0
        self._start_width = 0

        self.setFixedWidth(HANDLE_WIDTH)
        self.setCursor(Qt.CursorShape.SplitHCursor)
        self.setObjectName("SidebarResizeHandle")
        self.setStyleSheet(
            """
            QWidget#SidebarResizeHandle { background: transparent; }
            QWidget#SidebarResizeHandle:hover { background: rgba(255, 255, 255, 0.16); }
            """
        )

    # -- arrastre -----------------------------------------------------
    def mousePressEvent(self, event):  # noqa: N802 (API Qt)
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._start_x = int(event.globalPosition().x())
            self._start_width = int(self.sidebar.width())
            event.accept()

    def mouseMoveEvent(self, event):  # noqa: N802 (API Qt)
        if not self._dragging:
            return
        delta = int(event.globalPosition().x()) - self._start_x
        self._apply_width(self._start_width + delta)
        event.accept()

    def mouseReleaseEvent(self, event):  # noqa: N802 (API Qt)
        if event.button() == Qt.MouseButton.LeftButton and self._dragging:
            self._dragging = False
            self._apply_width(int(self.sidebar.width()), notify=True)
            event.accept()

    def _apply_width(self, width: int, notify: bool = False) -> int:
        width = max(self.min_width, min(self.max_width, int(width)))
        self.sidebar.setMinimumWidth(width)
        self.sidebar.setMaximumWidth(width)
        if notify and callable(self.on_resized):
            self.on_resized(width)
        return width

    def set_width(self, width: int) -> int:
        """Aplica un ancho concreto (p. ej. restaurado de la configuración)."""
        return self._apply_width(width)
