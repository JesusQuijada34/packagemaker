"""Pruebas de los puentes con el gestor de ventanas y utilidades asociadas."""

import unittest

from PyQt6.QtCore import QPoint, QRect, Qt

from lib.window_manager_bridge import (
    WindowManagerBridge,
    cursor_for_edges,
    detect_resize_edges,
    snap_geometry,
)


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


if __name__ == "__main__":
    unittest.main()
