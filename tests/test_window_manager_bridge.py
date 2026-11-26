"""Pruebas de los puentes con el gestor de ventanas y utilidades asociadas."""

import unittest

from PyQt6.QtCore import QPoint, QRect, Qt

from lib import window_manager_bridge
from lib.window_manager_bridge import (
    WindowManagerBridge,
    cursor_for_edges,
    detect_resize_edges,
    snap_geometry,
)

QT_AVAILABLE = window_manager_bridge.PYQT6_AVAILABLE


@unittest.skipUnless(QT_AVAILABLE, "Qt no disponible en este entorno")
class ResizeEdgeTests(unittest.TestCase):
    def setUp(self):
        self.rect = QRect(0, 0, 200, 100)

    def test_center_has_no_edges(self):
        self.assertIsNone(detect_resize_edges(QPoint(100, 50), self.rect))

    def test_left_edge(self):
        self.assertEqual(
            detect_resize_edges(QPoint(1, 50), self.rect), Qt.Edge.LeftEdge
        )

    def test_right_edge(self):
        self.assertEqual(
            detect_resize_edges(QPoint(199, 50), self.rect), Qt.Edge.RightEdge
        )

    def test_top_left_corner_combines_edges(self):
        edges = detect_resize_edges(QPoint(1, 1), self.rect)
        self.assertTrue(edges & Qt.Edge.TopEdge)
        self.assertTrue(edges & Qt.Edge.LeftEdge)

    def test_bottom_right_corner_combines_edges(self):
        edges = detect_resize_edges(QPoint(199, 99), self.rect)
        self.assertTrue(edges & Qt.Edge.BottomEdge)
        self.assertTrue(edges & Qt.Edge.RightEdge)

    def test_custom_margin_shrinks_hit_area(self):
        self.assertIsNone(detect_resize_edges(QPoint(3, 50), self.rect, margin=2))


@unittest.skipUnless(QT_AVAILABLE, "Qt no disponible en este entorno")
class CursorTests(unittest.TestCase):
    def test_no_edges_has_no_cursor(self):
        self.assertIsNone(cursor_for_edges(None))

    def test_horizontal_edges(self):
        self.assertEqual(
            cursor_for_edges(Qt.Edge.LeftEdge), Qt.CursorShape.SizeHorCursor
        )

    def test_diagonal_edges(self):
        edges = Qt.Edge.LeftEdge | Qt.Edge.TopEdge
        self.assertEqual(cursor_for_edges(edges), Qt.CursorShape.SizeFDiagCursor)


@unittest.skipUnless(QT_AVAILABLE, "Qt no disponible en este entorno")
class SnapTests(unittest.TestCase):
    def setUp(self):
        self.available = QRect(0, 0, 1920, 1080)

    def test_top_snaps_to_maximized(self):
        geo = snap_geometry(QPoint(500, 1), self.available, 10)
        self.assertEqual(geo, QRect(self.available))

    def test_left_snaps_to_half(self):
        geo = snap_geometry(QPoint(1, 400), self.available, 10)
        self.assertEqual(geo.width(), 960)
        self.assertEqual(geo.left(), 0)

    def test_right_snaps_to_half(self):
        geo = snap_geometry(QPoint(1919, 400), self.available, 10)
        self.assertEqual(geo.width(), 960)
        self.assertEqual(geo.left(), 960)

    def test_center_does_not_snap(self):
        self.assertIsNone(snap_geometry(QPoint(900, 400), self.available, 10))


class BridgeToggleTests(unittest.TestCase):
    class _FakeWindow:
        def __init__(self):
            self.calls = []

        def windowHandle(self):
            return None

        def isMaximized(self):
            return False

        def showMaximized(self):
            self.calls.append("maximized")

        def showNormal(self):
            self.calls.append("normal")

    def test_toggle_uses_show_maximized_without_helper(self):
        window = self._FakeWindow()
        bridge = WindowManagerBridge(window, None)
        bridge.toggle_maximize()
        self.assertEqual(window.calls, ["maximized"])

    def test_toggle_prefers_window_helper(self):
        window = self._FakeWindow()
        window.toggle_frameless_maximize = lambda: window.calls.append("helper")
        bridge = WindowManagerBridge(window, None)
        bridge.toggle_maximize()
        self.assertEqual(window.calls, ["helper"])


@unittest.skipUnless(QT_AVAILABLE, "Qt no disponible en este entorno")
class TitlebarCursorTests(unittest.TestCase):
    """Bug real: el cursor se quedaba en redimensionado sobre la titlebar."""

    class _FakeTitlebar:
        def __init__(self, geometry):
            self._geometry = geometry
            self._visible = True

        def isVisible(self):
            return self._visible

        def geometry(self):
            return self._geometry

    class _CursorWindow:
        """Ventana mínima que registra las llamadas de cursor."""

        def __init__(self):
            self.cursor_calls = []
            self.maximized = False

        def isMaximized(self):
            return self.maximized

        def setCursor(self, cursor):
            self.cursor_calls.append(("set", cursor))

        def unsetCursor(self):
            self.cursor_calls.append(("unset", None))

        def rect(self):
            return QRect(0, 0, 200, 100)

    def test_titlebar_hit_test_detects_position(self):
        window = self._CursorWindow()
        titlebar = self._FakeTitlebar(QRect(0, 0, 200, 30))
        bridge = WindowManagerBridge(window, titlebar)
        self.assertTrue(bridge._position_over_titlebar(QPoint(100, 15)))
        self.assertFalse(bridge._position_over_titlebar(QPoint(100, 60)))

    def test_no_titlebar_never_reports_hit(self):
        window = self._CursorWindow()
        bridge = WindowManagerBridge(window, None)
        self.assertFalse(bridge._position_over_titlebar(QPoint(100, 5)))

    def test_hidden_titlebar_never_reports_hit(self):
        window = self._CursorWindow()
        titlebar = self._FakeTitlebar(QRect(0, 0, 200, 30))
        titlebar._visible = False
        bridge = WindowManagerBridge(window, titlebar)
        self.assertFalse(bridge._position_over_titlebar(QPoint(100, 5)))

    def test_reset_cursor_restores_the_default_arrow(self):
        window = self._CursorWindow()
        bridge = WindowManagerBridge(window, None)
        bridge._hover_edges = Qt.Edge.TopEdge
        bridge._reset_cursor()
        self.assertIsNone(bridge._hover_edges)
        self.assertIn(("unset", None), window.cursor_calls)

    def test_leaving_an_edge_resets_the_cursor(self):
        """Al salir del borde el cursor vuelve a la flecha, no se queda pegado."""
        from PyQt6.QtCore import QEvent
        from PyQt6.QtGui import QMouseEvent

        window = self._CursorWindow()
        bridge = WindowManagerBridge(window, None)
        # Entra en el borde izquierdo: cursor de redimensionado horizontal.
        bridge._hover_edges = Qt.Edge.LeftEdge
        move_center = QMouseEvent(
            QEvent.Type.MouseMove,
            QPoint(100, 50).toPointF(),
            QPoint(100, 50).toPointF(),
            Qt.MouseButton.NoButton,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
        )
        bridge.eventFilter(window, move_center)
        self.assertIsNone(bridge._hover_edges)
        self.assertIn(("unset", None), window.cursor_calls)


@unittest.skipUnless(QT_AVAILABLE, "Qt no disponible en este entorno")
class MaximizedDragTests(unittest.TestCase):
    """R-6a1f8c23: arrastrar la titlebar maximizada no debe mover la ventana.

    El comportamiento aprobado en Q-011/F-004 es restaurar la ventana a su
    tamaño normal bajo el cursor y sólo entonces iniciar el arrastre. Un clic
    suelto, en cambio, no debe desmaximizarla.
    """

    class _FakeTitlebar:
        def __init__(self):
            self._drag_active = False
            self._drag_offset = None

    class _DragWindow:
        def __init__(self, maximized=True):
            self._pm_maximized = maximized
            self._geometry = QRect(0, 0, 1920, 1080)
            self._pm_restore_geometry = QRect(400, 200, 1000, 700)
            self.moves = []

        def geometry(self):
            return QRect(self._geometry)

        def frameGeometry(self):
            return QRect(self._geometry)

        def setGeometry(self, geo):
            self._geometry = QRect(geo)
            self.moves.append(QRect(geo))

        def isMaximized(self):
            return False

        def isFullScreen(self):
            return False

        def windowHandle(self):
            return None

        def screen(self):
            return None

        def showNormal(self):
            self._geometry = QRect(self._pm_restore_geometry)

        def showMaximized(self):
            pass

        def toggle_frameless_maximize(self):
            self._pm_maximized = False
            self._geometry = QRect(self._pm_restore_geometry)

    @staticmethod
    def _press(global_x, global_y=12):
        from PyQt6.QtCore import QEvent
        from PyQt6.QtGui import QMouseEvent

        local = QPoint(global_x, global_y)
        return QMouseEvent(
            QEvent.Type.MouseButtonPress,
            local.toPointF(),
            local.toPointF(),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )

    @staticmethod
    def _move(global_x, global_y=12, held=True):
        from PyQt6.QtCore import QEvent
        from PyQt6.QtGui import QMouseEvent

        local = QPoint(global_x, global_y)
        buttons = Qt.MouseButton.LeftButton if held else Qt.MouseButton.NoButton
        return QMouseEvent(
            QEvent.Type.MouseMove,
            local.toPointF(),
            local.toPointF(),
            Qt.MouseButton.NoButton,
            buttons,
            Qt.KeyboardModifier.NoModifier,
        )

    def _bridge(self, window, move_returns=True):
        titlebar = self._FakeTitlebar()
        bridge = WindowManagerBridge(window, titlebar)
        bridge._wire_titlebar()
        calls = []
        bridge.start_system_move = lambda: calls.append("move") or move_returns
        return bridge, titlebar, calls

    def test_press_alone_on_maximized_titlebar_does_not_restore(self):
        window = self._DragWindow()
        bridge, titlebar, calls = self._bridge(window)

        titlebar.mousePressEvent(self._press(960))

        self.assertTrue(window._pm_maximized)
        self.assertEqual(window.moves, [])
        self.assertEqual(calls, [])

    def test_small_jitter_does_not_restore(self):
        window = self._DragWindow()
        bridge, titlebar, calls = self._bridge(window)

        titlebar.mousePressEvent(self._press(960))
        bridge.eventFilter(titlebar, self._move(961))

        self.assertTrue(window._pm_maximized)
        self.assertEqual(calls, [])

    def test_hover_without_the_button_held_does_not_restore(self):
        window = self._DragWindow()
        bridge, titlebar, calls = self._bridge(window)

        titlebar.mousePressEvent(self._press(960))
        bridge.eventFilter(titlebar, self._move(1100, held=False))

        self.assertTrue(window._pm_maximized)
        self.assertEqual(calls, [])
        self.assertIsNone(bridge._pending_drag)

    def test_drag_from_maximized_restores_before_moving(self):
        window = self._DragWindow()
        bridge, titlebar, calls = self._bridge(window)

        titlebar.mousePressEvent(self._press(960))
        bridge.eventFilter(titlebar, self._move(980))

        self.assertFalse(window._pm_maximized)
        self.assertEqual(len(window.moves), 1)
        geo = window.moves[0]
        self.assertEqual((geo.width(), geo.height()), (1000, 700))
        self.assertEqual(calls, ["move"])

    def test_restore_keeps_the_cursor_over_the_same_relative_position(self):
        window = self._DragWindow()
        bridge, titlebar, calls = self._bridge(window)

        # Pulsación en el 75 % del ancho: la ventana restaurada debe quedar
        # colocada para que el cursor siga en ese mismo 75 % de su titlebar.
        titlebar.mousePressEvent(self._press(1440))
        bridge.eventFilter(titlebar, self._move(1460))

        geo = window.moves[0]
        self.assertEqual(geo.x(), 1440 - int(0.75 * 1000))
        self.assertEqual(geo.width(), 1000)

    def test_restored_window_stays_inside_the_screen(self):
        window = self._DragWindow()
        window._pm_restore_geometry = QRect(0, 0, 1800, 900)
        bridge, titlebar, calls = self._bridge(window)

        titlebar.mousePressEvent(self._press(1919))
        bridge.eventFilter(titlebar, self._move(1939))

        geo = window.moves[0]
        self.assertGreaterEqual(geo.x(), 0)
        self.assertLessEqual(geo.right(), 1919)

    def test_press_on_normal_window_does_not_restore(self):
        window = self._DragWindow(maximized=False)
        bridge, titlebar, calls = self._bridge(window)

        titlebar.mousePressEvent(self._press(500))

        self.assertEqual(window.moves, [])
        self.assertEqual(calls, ["move"])
        self.assertFalse(titlebar._drag_active)

    def test_failed_system_move_falls_back_to_manual_drag(self):
        window = self._DragWindow()
        bridge, titlebar, calls = self._bridge(window, move_returns=False)

        titlebar.mousePressEvent(self._press(960))
        bridge.eventFilter(titlebar, self._move(980))

        self.assertTrue(titlebar._drag_active)
        self.assertIsNotNone(titlebar._drag_offset)


@unittest.skipUnless(QT_AVAILABLE, "Qt no disponible en este entorno")
class ImmersiveDoubleClickTests(unittest.TestCase):
    """R-2f8b6a31: en pantalla completa el doble clic no debe restaurar.

    El tercer gesto es el que sale del modo inmersivo; si el doble clic
    restaurara la ventana, quedaría una ventana normal sin barra de título.
    """

    _app = None

    @classmethod
    def _ensure_app(cls):
        from PyQt6.QtWidgets import QApplication

        cls._app = QApplication.instance() or QApplication([])

    def _window(self):
        from PyQt6.QtWidgets import QWidget

        self._ensure_app()
        window = QWidget()
        window.resize(400, 300)
        titlebar = QWidget(window)
        calls = []
        window.toggle_frameless_maximize = lambda: calls.append("toggle")
        bridge = WindowManagerBridge(window, titlebar)
        bridge.install()
        return window, titlebar, calls

    @staticmethod
    def _double_click(titlebar):
        from PyQt6.QtCore import QEvent, QPointF
        from PyQt6.QtGui import QMouseEvent
        from PyQt6.QtWidgets import QApplication

        local = QPointF(5.0, 5.0)
        event = QMouseEvent(
            QEvent.Type.MouseButtonDblClick,
            local,
            QPointF(titlebar.mapToGlobal(local.toPoint())),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        QApplication.sendEvent(titlebar, event)

    def test_double_click_toggles_the_window(self):
        _window, titlebar, calls = self._window()
        self._double_click(titlebar)
        self.assertEqual(calls, ["toggle"])

    def test_double_click_in_fullscreen_does_not_toggle(self):
        window, titlebar, calls = self._window()
        window._pm_immersive = True
        self._double_click(titlebar)
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
