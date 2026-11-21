# -*- coding: utf-8 -*-
"""Modo inmersivo de la barra de título (bugs.txt Fase 2.2).

Tres pulsaciones seguidas sobre la barra de título:

1. El frame pasa a primer plano (``WindowStaysOnTopHint``), por encima del resto
   de aplicaciones.
2. La barra se oculta deslizándose hacia arriba y reaparece al acercar el ratón
   al borde superior.
3. El botón de maximizar se convierte en "salir de pantalla completa" con un
   icono SVG de flecha hacia abajo a la izquierda.

``ClickStreak`` es lógica pura (sin Qt) para poder probar el conteo; el resto
sólo se ejecuta cuando hay PyQt6.
"""
from __future__ import annotations

from typing import Optional

TRIPLE_CLICK = 3
DEFAULT_INTERVAL_MS = 600

# Flecha hacia abajo a la izquierda: el mismo trazo que usa Windows para salir
# de pantalla completa.
EXIT_FULLSCREEN_SVG = b"""\
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M9 15H15M9 15V9M9 15L16 8" stroke="#ffffff" stroke-width="1.2"/>
</svg>
"""


class ClickStreak:
    """Cuenta pulsaciones consecutivas separadas por menos de ``interval_ms``."""

    def __init__(self, target: int = TRIPLE_CLICK, interval_ms: int = DEFAULT_INTERVAL_MS):
        self.target = int(target)
        self.interval_ms = int(interval_ms)
        self._count = 0
        self._last_ms: Optional[int] = None

    @property
    def count(self) -> int:
        return self._count

    def register(self, timestamp_ms: int) -> bool:
        """Registra una pulsación y dice si se alcanzó el objetivo."""
        if self._last_ms is not None and timestamp_ms - self._last_ms > self.interval_ms:
            self._count = 0
        self._count += 1
        self._last_ms = int(timestamp_ms)
        if self._count >= self.target:
            self.reset()
            return True
        return False

    def reset(self) -> None:
        self._count = 0
        self._last_ms = None


def is_immersive(window) -> bool:
    return bool(getattr(window, "_pm_immersive", False))


def _set_stays_on_top(window, enabled: bool) -> None:
    from PyQt6.QtCore import Qt

    flag = Qt.WindowType.WindowStaysOnTopHint
    was_visible = window.isVisible()
    geometry = window.geometry()
    window.setWindowFlag(flag, enabled)
    if was_visible:
        window.setGeometry(geometry)
        window.show()


class ImmersiveTitleBar:
    """Controlador del modo inmersivo para una ventana y su titlebar."""

    def __init__(self, window, titlebar, *, slide_ms: int = 220):
        self.window = window
        self.titlebar = titlebar
        self.slide_ms = int(slide_ms)
        self.streak = ClickStreak()
        self._animation = None
        self._default_max_icon = getattr(getattr(titlebar, "btn_max", None), "icon", lambda: None)()
        self._default_tooltip = getattr(getattr(titlebar, "btn_max", None), "toolTip", lambda: "")()

    # -- instalación -------------------------------------------------
    def install(self) -> None:
        if self.titlebar is None:
            return
        # Un filtro de eventos ve la pulsación antes que el manejador del
        # puente de ventanas, así el triple clic no arranca además un
        # ``startSystemMove``.
        self.titlebar.setMouseTracking(True)
        self._titlebar_filter = _make_titlebar_filter(self)
        self.titlebar.installEventFilter(self._titlebar_filter)
        self._watcher = _make_top_edge_watcher(self)
        self.window.installEventFilter(self._watcher)

        btn_max = getattr(self.titlebar, "btn_max", None)
        if btn_max is not None:
            try:
                btn_max.clicked.disconnect()
            except TypeError:
                pass
            btn_max.clicked.connect(self._on_maximize_clicked)

    # -- acciones ----------------------------------------------------
    def toggle(self) -> None:
        if is_immersive(self.window):
            self.exit()
        else:
            self.enter()

    def enter(self) -> None:
        window, titlebar = self.window, self.titlebar
        window._pm_immersive = True
        _set_stays_on_top(window, True)
        self._swap_max_button(immersive=True)
        if titlebar is not None:
            self._slide(titlebar, hide=True)

    def exit(self) -> None:
        window, titlebar = self.window, self.titlebar
        window._pm_immersive = False
        _set_stays_on_top(window, False)
        self._swap_max_button(immersive=False)
        if titlebar is not None:
            self._slide(titlebar, hide=False)

    def reveal_titlebar(self) -> None:
        """Devuelve la barra cuando el ratón toca el borde superior."""
        if not is_immersive(self.window) or self.titlebar is None:
            return
        if self.titlebar.isVisible() and self.titlebar.height() > 0:
            return
        self._slide(self.titlebar, hide=False)

    def conceal_titlebar(self) -> None:
        if not is_immersive(self.window) or self.titlebar is None:
            return
        self._slide(self.titlebar, hide=True)

    def _on_maximize_clicked(self) -> None:
        if is_immersive(self.window):
            self.exit()
            return
        toggle = getattr(self.window, "toggle_frameless_maximize", None)
        if callable(toggle):
            toggle()
        elif self.window.isMaximized():
            self.window.showNormal()
        else:
            self.window.showMaximized()

    def _swap_max_button(self, *, immersive: bool) -> None:
        btn_max = getattr(self.titlebar, "btn_max", None)
        if btn_max is None:
            return
        from PyQt6.QtGui import QIcon, QPixmap

        if immersive:
            pixmap = QPixmap()
            pixmap.loadFromData(EXIT_FULLSCREEN_SVG)
            btn_max.setIcon(QIcon(pixmap))
            btn_max.setToolTip("Salir de pantalla completa")
        else:
            if self._default_max_icon is not None and not self._default_max_icon.isNull():
                btn_max.setIcon(self._default_max_icon)
            btn_max.setToolTip(self._default_tooltip)

    def _slide(self, widget, *, hide: bool) -> None:
        from PyQt6.QtCore import QEasingCurve, QPropertyAnimation

        full_height = int(getattr(widget, "_pm_full_height", 0) or widget.height())
        widget._pm_full_height = full_height
        if hide:
            widget.setMaximumHeight(full_height)
            widget.show()
            start, end = full_height, 0
        else:
            widget.setMaximumHeight(full_height)
            widget.show()
            start, end = 0, full_height

        animation = QPropertyAnimation(widget, b"maximumHeight", widget)
        animation.setDuration(self.slide_ms)
        animation.setStartValue(start)
        animation.setEndValue(end)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        if hide:
            animation.finished.connect(lambda: widget.hide())
        else:
            animation.finished.connect(lambda: widget.setMaximumHeight(16777215))
        self._animation = animation
        animation.start()


def _make_titlebar_filter(controller):
    """Cuenta las pulsaciones de la barra y dispara el modo inmersivo."""
    from PyQt6.QtCore import QEvent, QObject, Qt

    class TitleBarFilter(QObject):
        def eventFilter(self, obj, event):  # noqa: N802 (API Qt)
            etype = event.type()
            if etype == QEvent.Type.MouseButtonDblClick:
                controller.streak.reset()
                return False
            if etype == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                if controller.streak.register(event.timestamp()):
                    controller.toggle()
                    return True
            return False

    return TitleBarFilter(controller.titlebar)


def _make_top_edge_watcher(controller):
    """Devuelve un ``QObject`` que revela la barra al tocar el borde superior."""
    from PyQt6.QtCore import QEvent, QObject

    class TopEdgeWatcher(QObject):
        def eventFilter(self, obj, event):  # noqa: N802 (API Qt)
            if event.type() == QEvent.Type.MouseMove and is_immersive(controller.window):
                if event.position().y() <= 6:
                    controller.reveal_titlebar()
            return False

    return TopEdgeWatcher(controller.window)


def install_immersive_titlebar(window, titlebar) -> ImmersiveTitleBar:
    controller = ImmersiveTitleBar(window, titlebar)
    controller.install()
    window.immersive_titlebar = controller
    return controller
