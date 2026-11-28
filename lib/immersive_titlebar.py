# -*- coding: utf-8 -*-
"""Modo inmersivo de la barra de título (bugs.txt Fase 2.2).

Tres pulsaciones seguidas sobre la barra de título:

1. El frame pasa a primer plano (``WindowStaysOnTopHint``) y cubre la pantalla
   completa, incluida la franja de la barra de tareas.
2. La barra se oculta deslizándose hacia arriba y reaparece al acercar el ratón
   al borde superior; al abandonarla vuelve a ocultarse.
3. El botón de maximizar se convierte en "salir de pantalla completa" con un
   icono SVG de flecha hacia abajo a la izquierda.

``ClickStreak`` es lógica pura (sin Qt) para poder probar el conteo; el resto
sólo se ejecuta cuando hay PyQt6.
"""
from __future__ import annotations

from typing import Optional

from lib.i18n import tr

TRIPLE_CLICK = 3
DEFAULT_INTERVAL_MS = 600

# Franja del borde superior (px) que revela la barra oculta.
TOP_EDGE_THRESHOLD = 8
# Frecuencia (ms) con la que se consulta el cursor mientras el modo inmersivo
# está activo. Escuchar ``MouseMove`` no basta: el puntero está sobre las
# páginas de contenido y Qt no entrega movimientos pasivos a widgets sin
# ``WA_MouseTracking``, así que un filtro de la ventana nunca los veía.
POINTER_POLL_MS = 80

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


def _cursor_y() -> int:
    """Coordenada Y global del puntero."""
    from PyQt6.QtGui import QCursor

    return QCursor.pos().y()


class ImmersiveTitleBar:
    """Controlador del modo inmersivo para una ventana y su titlebar."""

    def __init__(self, window, titlebar, *, slide_ms: int = 220):
        self.window = window
        self.titlebar = titlebar
        self.slide_ms = int(slide_ms)
        self.streak = ClickStreak()
        self._animation = None
        self._titlebar_hidden = False
        self._pointer_timer = None
        self._expanded = False
        self._expanded_geometry = None
        self._titlebar_filter = None
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
        self._install_pointer_timer()

        btn_max = getattr(self.titlebar, "btn_max", None)
        if btn_max is not None:
            try:
                btn_max.clicked.disconnect()
            except TypeError:
                pass
            btn_max.clicked.connect(self._on_maximize_clicked)

    def _install_pointer_timer(self) -> None:
        if self._pointer_timer is not None:
            return
        from PyQt6.QtCore import QObject, QTimer

        parent = self.window if isinstance(self.window, QObject) else None
        timer = QTimer(parent)
        timer.setInterval(POINTER_POLL_MS)
        timer.timeout.connect(self.poll_pointer)
        self._pointer_timer = timer

    # -- acciones ----------------------------------------------------
    def toggle(self) -> None:
        if is_immersive(self.window):
            self.exit()
        else:
            self.enter()

    def enter(self) -> None:
        window, titlebar = self.window, self.titlebar
        self._ensure_maximized()
        window._pm_immersive = True
        _set_stays_on_top(window, True)
        self._cover_screen()
        self._swap_max_button(immersive=True)
        if self._pointer_timer is not None:
            self._pointer_timer.start()
        if titlebar is not None:
            self._set_titlebar_hidden(True)

    def exit(self) -> None:
        window, titlebar = self.window, self.titlebar
        window._pm_immersive = False
        if self._pointer_timer is not None:
            self._pointer_timer.stop()
        _set_stays_on_top(window, False)
        self._restore_screen()
        self._swap_max_button(immersive=False)
        if titlebar is not None:
            self._set_titlebar_hidden(False)

    def _ensure_maximized(self) -> None:
        """Pantalla completa exige que la ventana ocupe la pantalla.

        Sin esto, un modo inmersivo iniciado desde una ventana normal dejaba
        una ventana pequeña sin barra de título.
        """
        window = self.window
        if getattr(window, "_pm_maximized", False):
            return
        try:
            if window.isMaximized() or window.isFullScreen():
                return
        except (RuntimeError, AttributeError):
            pass
        toggle = getattr(window, "toggle_frameless_maximize", None)
        if callable(toggle):
            toggle()
        else:
            window.showMaximized()

    # -- pantalla completa real --------------------------------------
    def _screen(self):
        from PyQt6.QtWidgets import QApplication

        try:
            screen = self.window.screen()
        except (RuntimeError, AttributeError):
            screen = None
        return screen or QApplication.primaryScreen()

    def _cover_screen(self) -> None:
        """Cubre también la franja de la barra de tareas.

        ``toggle_frameless_maximize`` ajusta la ventana al *área disponible*,
        que excluye la barra de tareas: en modo inmersivo quedaba una franja
        inferior que seguía reaccionando (R-7e3a1b95).
        """
        screen = self._screen()
        if screen is None:
            return
        from PyQt6.QtCore import QRect

        self._expanded_geometry = QRect(self.window.geometry())
        self._expanded = True
        self.window.setGeometry(screen.geometry())

    def _restore_screen(self) -> None:
        """Devuelve la ventana al estado que tenía antes de cubrir la pantalla."""
        if not self._expanded:
            return
        self._expanded = False
        window = self.window
        if getattr(window, "_pm_maximized", False):
            screen = self._screen()
            if screen is not None:
                window.setGeometry(screen.availableGeometry())
            return
        geometry = self._expanded_geometry
        if geometry is not None and geometry.isValid() and geometry.width() > 0:
            window.setGeometry(geometry)

    # -- barra deslizante --------------------------------------------
    def reveal_titlebar(self) -> None:
        """Devuelve la barra cuando el ratón toca el borde superior."""
        if not is_immersive(self.window) or self.titlebar is None:
            return
        self._set_titlebar_hidden(False)

    def conceal_titlebar(self) -> None:
        """Oculta la barra cuando el ratón la abandona."""
        if not is_immersive(self.window) or self.titlebar is None:
            return
        self._set_titlebar_hidden(True)

    def _set_titlebar_hidden(self, hidden: bool) -> None:
        if hidden == self._titlebar_hidden:
            return
        self._titlebar_hidden = hidden
        if self.titlebar is not None:
            self._slide(self.titlebar, hide=hidden)

    def poll_pointer(self) -> None:
        """Revela u oculta la barra según la posición del puntero."""
        if not is_immersive(self.window) or self.titlebar is None:
            return
        screen = self._screen()
        if screen is None:
            return
        y = _cursor_y()
        if y <= screen.geometry().top() + TOP_EDGE_THRESHOLD:
            self.reveal_titlebar()
        elif not self._titlebar_hidden and y > self._titlebar_bottom():
            self.conceal_titlebar()

    def _titlebar_bottom(self) -> int:
        """Coordenada Y global del borde inferior de la barra desplegada."""
        from PyQt6.QtCore import QPoint

        height = int(getattr(self.titlebar, "_pm_full_height", 0) or self.titlebar.height())
        return self.titlebar.mapToGlobal(QPoint(0, height)).y()

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
            btn_max.setToolTip(tr("window.exit_fullscreen"))
        else:
            if self._default_max_icon is not None and not self._default_max_icon.isNull():
                btn_max.setIcon(self._default_max_icon)
            btn_max.setToolTip(self._default_tooltip)

    def _slide(self, widget, *, hide: bool) -> None:
        from PyQt6.QtCore import QEasingCurve, QPropertyAnimation

        full_height = int(getattr(widget, "_pm_full_height", 0) or widget.height())
        if full_height <= 0:
            widget.setMaximumHeight(0 if hide else 16777215)
            widget.setVisible(not hide)
            return
        widget._pm_full_height = full_height
        widget.setMaximumHeight(full_height)
        widget.show()
        start, end = (full_height, 0) if hide else (0, full_height)

        # Una animación anterior que siga viva terminaría ocultando la barra
        # recién revelada (o al contrario): se detiene antes de sustituirla.
        previous = self._animation
        self._animation = None
        if previous is not None:
            try:
                previous.stop()
            except RuntimeError:
                pass

        animation = QPropertyAnimation(widget, b"maximumHeight", widget)
        animation.setDuration(self.slide_ms)
        animation.setStartValue(start)
        animation.setEndValue(end)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.finished.connect(lambda: self._finish_slide(widget, hidden=hide))
        self._animation = animation
        animation.start()

    def _finish_slide(self, widget, *, hidden: bool) -> None:
        # Una animación obsoleta no debe imponer su estado final.
        if hidden != self._titlebar_hidden:
            return
        if hidden:
            widget.hide()
        else:
            widget.setMaximumHeight(16777215)


def _make_titlebar_filter(controller):
    """Cuenta las pulsaciones de la barra y oculta la barra al abandonarla.

    Qt entrega un triple clic como pulsación, doble clic y pulsación. Si el
    doble clic reiniciara la cuenta, el tercer gesto nunca llegaría al máximo
    (R-2f8b6a31); por eso se registra como el segundo gesto y se deja pasar
    para que el doble clic siga maximizando o restaurando.
    """
    from PyQt6.QtCore import QEvent, QObject, Qt

    class TitleBarFilter(QObject):
        def eventFilter(self, obj, event):  # noqa: N802 (API Qt)
            etype = event.type()
            if etype == QEvent.Type.Leave:
                if is_immersive(controller.window):
                    controller.conceal_titlebar()
                return False
            if etype not in (QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonDblClick):
                return False
            if event.button() != Qt.MouseButton.LeftButton:
                return False
            if controller.streak.register(event.timestamp()):
                controller.toggle()
                return True
            return False

    return TitleBarFilter(controller.titlebar)


def install_immersive_titlebar(window, titlebar) -> ImmersiveTitleBar:
    controller = ImmersiveTitleBar(window, titlebar)
    controller.install()
    window.immersive_titlebar = controller
    return controller
