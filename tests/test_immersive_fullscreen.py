# -*- coding: utf-8 -*-
"""R-7e3a1b95 (issue #17): pantalla completa real y barra que entra y sale.

El reporte del propietario describía tres síntomas del modo inmersivo: la
titlebar no aparecía al tocar el borde superior, el icono de salir nunca se veía
(la barra quedaba oculta para siempre) y la ventana no cubría la franja de la
barra de tareas.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib import immersive_titlebar as immersive  # noqa: E402

pytest.importorskip("PyQt6.QtWidgets")
pytest.importorskip("PyQt6.QtTest")

from PyQt6.QtCore import QEvent, QRect, Qt  # noqa: E402
from PyQt6.QtTest import QTest  # noqa: E402
from PyQt6.QtWidgets import QApplication, QWidget  # noqa: E402

SCREEN = QRect(0, 0, 800, 800)
TASKBAR = 60
AVAILABLE = QRect(0, 0, 800, SCREEN.height() - TASKBAR)
SETTLE_MS = 350


class _StubScreen:
    """Pantalla con una barra de tareas de 60 px, como en Windows."""

    def geometry(self):
        return QRect(SCREEN)

    def availableGeometry(self):
        return QRect(AVAILABLE)


class _Harness:
    def __init__(self):
        self.window = QWidget()
        self.window.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.window.resize(640, 480)
        self.titlebar = QWidget(self.window)
        self.titlebar.setFixedHeight(34)
        self.screen = _StubScreen()
        self.window.screen = lambda: self.screen
        self.window.toggle_frameless_maximize = self._toggle_maximize
        self.controller = immersive.install_immersive_titlebar(self.window, self.titlebar)
        self.window.show()
        QTest.qWait(20)

    def _toggle_maximize(self):
        maximized = not bool(getattr(self.window, "_pm_maximized", False))
        self.window._pm_maximized = maximized
        self.window.setGeometry(QRect(AVAILABLE) if maximized else QRect(40, 40, 640, 480))


@pytest.fixture
def harness(monkeypatch):
    monkeypatch.setattr(immersive, "_cursor_y", lambda: 400)
    built = _Harness()
    yield built
    built.controller.exit()
    built.window.close()
    built.window.deleteLater()
    QTest.qWait(10)


def _settle():
    QTest.qWait(SETTLE_MS)


def _contains(outer, inner):
    return inner.left() >= outer.left() and inner.top() >= outer.top() and (
        inner.right() <= outer.right() and inner.bottom() <= outer.bottom()
    )


class TestFullscreenCoversTheTaskbar:
    def test_entering_immersive_covers_the_whole_screen(self, harness):
        harness.controller.enter()

        assert harness.window.geometry() == SCREEN
        assert harness.window.geometry().bottom() == SCREEN.bottom()

    def test_exiting_immersive_returns_to_the_available_area(self, harness):
        harness.controller.enter()
        harness.controller.exit()

        assert harness.window.geometry() == AVAILABLE

    def test_a_window_covering_the_taskbar_stays_within_the_screen(self, harness):
        harness.controller.enter()

        assert _contains(SCREEN, harness.window.geometry())


class TestTopEdgeReveal:
    def test_pointer_at_the_top_edge_reveals_the_hidden_titlebar(self, harness, monkeypatch):
        harness.controller.enter()
        _settle()
        assert harness.titlebar.isHidden() is True

        monkeypatch.setattr(immersive, "_cursor_y", lambda: immersive.TOP_EDGE_THRESHOLD - 1)
        harness.controller.poll_pointer()
        _settle()

        assert harness.titlebar.isHidden() is False

    def test_pointer_below_the_bar_conceals_it_again(self, harness, monkeypatch):
        harness.controller.enter()
        _settle()
        monkeypatch.setattr(immersive, "_cursor_y", lambda: 2)
        harness.controller.poll_pointer()
        _settle()
        assert harness.titlebar.isHidden() is False

        monkeypatch.setattr(immersive, "_cursor_y", lambda: 400)
        harness.controller.poll_pointer()
        _settle()

        assert harness.titlebar.isHidden() is True

    def test_leaving_the_titlebar_conceals_it(self, harness, monkeypatch):
        harness.controller.enter()
        _settle()
        monkeypatch.setattr(immersive, "_cursor_y", lambda: 2)
        harness.controller.poll_pointer()
        _settle()
        assert harness.titlebar.isHidden() is False

        # El cursor baja al contenido: sale de la barra y deja el borde superior.
        monkeypatch.setattr(immersive, "_cursor_y", lambda: 400)
        QApplication.sendEvent(harness.titlebar, QEvent(QEvent.Type.Leave))
        _settle()

        assert harness.titlebar.isHidden() is True

    def test_revealing_cancels_the_hide_animation(self, harness, monkeypatch):
        monkeypatch.setattr(immersive, "_cursor_y", lambda: 2)
        harness.controller.enter()
        # El cursor ya está en el borde: la barra no debe quedarse oculta
        # porque una animación de ocultado obsoleta imponga su estado final.
        harness.controller.poll_pointer()
        _settle()

        assert harness.titlebar.isHidden() is False

    def test_pointer_below_the_bar_does_not_reveal_it(self, harness, monkeypatch):
        harness.controller.enter()
        _settle()
        monkeypatch.setattr(immersive, "_cursor_y", lambda: AVAILABLE.height() - 1)
        harness.controller.poll_pointer()
        _settle()

        assert harness.titlebar.isHidden() is True


class TestPointerWatcherLifecycle:
    def test_pointer_polling_runs_only_in_immersive_mode(self, harness):
        assert harness.controller._pointer_timer is not None
        assert harness.controller._pointer_timer.isActive() is False

        harness.controller.enter()
        assert harness.controller._pointer_timer.isActive() is True

        harness.controller.exit()
        assert harness.controller._pointer_timer.isActive() is False

    def test_polling_outside_immersive_mode_is_a_noop(self, harness, monkeypatch):
        monkeypatch.setattr(immersive, "_cursor_y", lambda: 2)
        harness.controller.poll_pointer()
        _settle()

        assert harness.titlebar.isHidden() is False
