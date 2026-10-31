# -*- coding: utf-8 -*-
"""Puentes con el gestor de ventanas del sistema operativo.

Conecta la barra de título propia con las acciones nativas del WM
(mover, redimensionar por bordes, maximizar, menú del sistema y snap),
de modo que gestos y pulsaciones se comporten como en una ventana nativa.
"""

from __future__ import annotations

import sys
from typing import Optional

try:
    from PyQt6.QtCore import QEvent, QObject, QPoint, QRect, Qt
    from PyQt6.QtGui import QCursor
    from PyQt6.QtWidgets import QMenu, QWidget

    PYQT6_AVAILABLE = True
except ImportError:  # pragma: no cover - entorno sin Qt
    PYQT6_AVAILABLE = False

    class QWidget:  # type: ignore[no-redef]
        pass

    class QObject:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            pass

    class QEvent:  # type: ignore[no-redef]
        class Type:
            MouseButtonPress = None
            MouseMove = None
            MouseButtonRelease = None

    class Qt:  # type: ignore[no-redef]
        class MouseButton:
            LeftButton = None
            RightButton = None

        class Edge:
            TopEdge = 1
            LeftEdge = 2
            RightEdge = 4
            BottomEdge = 8


RESIZE_MARGIN = 6


def detect_resize_edges(pos: QPoint, rect: QRect, margin: int = RESIZE_MARGIN):
    """Devuelve la combinación de bordes a redimensionar según la posición.

    ``None`` cuando el punto no está sobre ningún borde, lo que permite
    decidir entre redimensionar o dejar pasar el evento.
    """
    if not PYQT6_AVAILABLE:
        return None
    edges = None
    if pos.x() <= rect.left() + margin:
        edges = Qt.Edge.LeftEdge
    elif pos.x() >= rect.right() - margin:
        edges = Qt.Edge.RightEdge
    if pos.y() <= rect.top() + margin:
        edges = (edges | Qt.Edge.TopEdge) if edges is not None else Qt.Edge.TopEdge
    elif pos.y() >= rect.bottom() - margin:
        edges = (edges | Qt.Edge.BottomEdge) if edges is not None else Qt.Edge.BottomEdge
    return edges


def cursor_for_edges(edges) -> Optional[object]:
    """Cursor adecuado para los bordes detectados."""
    if not PYQT6_AVAILABLE or edges is None:
        return None
    left = bool(edges & Qt.Edge.LeftEdge)
    right = bool(edges & Qt.Edge.RightEdge)
    top = bool(edges & Qt.Edge.TopEdge)
    bottom = bool(edges & Qt.Edge.BottomEdge)
    if (left and top) or (right and bottom):
        return Qt.CursorShape.SizeFDiagCursor
    if (right and top) or (left and bottom):
        return Qt.CursorShape.SizeBDiagCursor
    if left or right:
        return Qt.CursorShape.SizeHorCursor
    return Qt.CursorShape.SizeVerCursor


def snap_geometry(pos: QPoint, available: QRect, drag_start_y: int) -> Optional[QRect]:
    """Calcula la geometría de snap (Aero Snap) al soltar cerca de un borde.

    Devuelve ``None`` si el punto no activa ningún snap.
    """
    if not PYQT6_AVAILABLE:
        return None
    threshold = 12
    if pos.y() <= available.top() + threshold:
        return QRect(available)
    if pos.x() <= available.left() + threshold:
        return QRect(
            available.left(),
            available.top(),
            available.width() // 2,
            available.height(),
        )
    if pos.x() >= available.right() - threshold:
        return QRect(
            available.left() + available.width() // 2,
            available.top(),
            available.width() // 2,
            available.height(),
        )
    return None


class WindowManagerBridge(QObject):
    """Instala los puentes nativos sobre una ventana frameless y su titlebar."""

    def __init__(self, window: QWidget, titlebar: Optional[QWidget] = None):
        super().__init__(window if isinstance(window, QObject) else None)
        self.window = window
        self.titlebar = titlebar
        self._hover_edges = None
        self._enabled = PYQT6_AVAILABLE

    def _position_over_titlebar(self, pos: QPoint) -> bool:
        """``True`` si *pos* (coordenadas de la ventana) cae sobre la titlebar.

        La titlebar vive en el borde superior, dentro del margen de
        redimensionado; sin esta comprobación basta pasar el ratón por encima
        para que la ventana adopte el cursor de redimensionado vertical.
        """
        titlebar = self.titlebar
        if titlebar is None:
            return False
        try:
            if not titlebar.isVisible():
                return False
            geometry = titlebar.geometry()
            return geometry.contains(pos)
        except (RuntimeError, AttributeError):
            return False

    # -- instalación -------------------------------------------------
    def install(self) -> None:
        if not self._enabled:
            return
        self.window.setMouseTracking(True)
        self.window.installEventFilter(self)
        if self.titlebar is not None:
            # La titlebar es hija de la ventana y hereda su cursor cuando no
            # define uno propio; sin vigilarla, el cursor de redimensionado se
            # quedaba pegado al pasar el ratón por encima.
            try:
                self.titlebar.setMouseTracking(True)
                self.titlebar.installEventFilter(self)
            except (RuntimeError, AttributeError):
                pass
            self._wire_titlebar()

    def _wire_titlebar(self) -> None:
        titlebar = self.titlebar
        original_press = getattr(titlebar, "mousePressEvent", None)

        def on_press(event):
            if event.button() == Qt.MouseButton.LeftButton:
                self.start_system_move()
                event.accept()
                return
            if event.button() == Qt.MouseButton.RightButton:
                self.show_system_menu(event.globalPosition().toPoint())
                event.accept()
                return
            if callable(original_press):
                original_press(event)

        def on_double(event):
            if event.button() == Qt.MouseButton.LeftButton:
                self.toggle_maximize()

        titlebar.mousePressEvent = on_press
        titlebar.mouseDoubleClickEvent = on_double

    # -- acciones nativas --------------------------------------------
    def start_system_move(self) -> bool:
        handle = self.window.windowHandle()
        if handle is not None and hasattr(handle, "startSystemMove"):
            try:
                if handle.startSystemMove():
                    return True
            except (RuntimeError, TypeError):
                pass
        return False

    def start_system_resize(self, edges) -> bool:
        handle = self.window.windowHandle()
        if handle is not None and hasattr(handle, "startSystemResize"):
            try:
                if handle.startSystemResize(edges):
                    return True
            except (RuntimeError, TypeError):
                pass
        return False

    def toggle_maximize(self) -> None:
        toggle = getattr(self.window, "toggle_frameless_maximize", None)
        if callable(toggle):
            toggle()
            return
        if self.window.isMaximized():
            self.window.showNormal()
        else:
            self.window.showMaximized()

    def show_system_menu(self, global_pos: QPoint) -> None:
        if sys.platform.startswith("win"):
            if self._send_windows_system_menu():
                return
        menu = QMenu(self.window)
        menu.addAction("Restaurar", self.window.showNormal)
        menu.addAction("Minimizar", self.window.showMinimized)
        menu.addAction("Maximizar", self.toggle_maximize)
        menu.addSeparator()
        menu.addAction("Cerrar", self.window.close)
        menu.exec(global_pos)

    def _send_windows_system_menu(self) -> bool:
        try:
            import ctypes

            hwnd = int(self.window.winId())
            WM_NCRBUTTONUP = 0x00A5
            HTCAPTION = 2
            ctypes.windll.user32.PostMessageW(hwnd, WM_NCRBUTTONUP, HTCAPTION, 0)
            return True
        except Exception:
            return False

    # -- filtro de eventos -------------------------------------------
    def eventFilter(self, obj, event):  # noqa: N802 (API Qt)
        if not self._enabled:
            return False
        if obj is not self.window and obj is not self.titlebar:
            return False
        if obj is self.titlebar:
            # La titlebar nunca redimensiona: al pasar el ratón por ella el
            # cursor debe volver a la flecha normal (heredaba el de la ventana).
            if event.type() in (QEvent.Type.MouseMove, QEvent.Type.Enter):
                self._reset_cursor()
            return False
        etype = event.type()
        if etype == QEvent.Type.MouseMove:
            if self.window.isMaximized():
                if self._hover_edges is not None:
                    self._reset_cursor()
                return False
            pos = event.position().toPoint()
            if self._position_over_titlebar(pos):
                # La titlebar no redimensiona: moverla es cosa de
                # ``start_system_move``. Sin esto el cursor quedaba en
                # redimensionado al pasar por encima.
                if self._hover_edges is not None:
                    self._reset_cursor()
                return False
            edges = detect_resize_edges(pos, self.window.rect())
            if edges != self._hover_edges:
                self._hover_edges = edges
                if edges is None:
                    # Al abandonar el borde hay que devolver el cursor normal;
                    # antes se quedaba pegado y parecía un fallo del titlebar.
                    self._reset_cursor()
                else:
                    cursor = cursor_for_edges(edges)
                    if cursor is not None:
                        self.window.setCursor(QCursor(cursor))
        elif etype == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton and not self.window.isMaximized():
                pos = event.position().toPoint()
                if self._position_over_titlebar(pos):
                    return False
                edges = detect_resize_edges(pos, self.window.rect())
                if edges is not None:
                    self.start_system_resize(edges)
        elif etype == QEvent.Type.MouseButtonRelease:
            self._reset_cursor()
        return False

    def _reset_cursor(self) -> None:
        """Devuelve el cursor de la ventana a la flecha normal."""
        self._hover_edges = None
        try:
            self.window.unsetCursor()
        except (RuntimeError, AttributeError):
            pass


def install_window_manager_bridges(window: QWidget, titlebar: Optional[QWidget] = None) -> WindowManagerBridge:
    """Atajo: crea, instala y devuelve el puente con el gestor de ventanas."""
    bridge = WindowManagerBridge(window, titlebar)
    bridge.install()
    return bridge
