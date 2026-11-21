# -*- coding: utf-8 -*-
"""Bootloader de splash compartido para proyectos compilados con PackageMaker.

Este módulo es **autocontenido**: se copia a la carpeta ``lib/`` de cada
proyecto ``iflapp`` durante la compilación (Fase 3) y sólo depende de la
biblioteca estándar y, opcionalmente, de PyQt6. Nunca importa módulos de
PackageMaker, de modo que el proyecto compilado puede ejecutarse por sí solo.

Uso (código inyectado automáticamente por :mod:`lib.bootloader_injection`)::

    from lib.splash_bootloader import bootloader as _pm_splash
    _pm_splash.arm(__file__)          # tras los imports
    _pm_splash.start(app)             # al crear la QApplication
    _pm_splash.finish(app)            # al revelar la ventana principal

El splash replica el patrón ``IntegratedSplash``: una ventana frameless del
mismo tamaño que la principal, con el fondo del color de acento del SO y el
icono del paquete centrado. Se desvanece en cuanto la ventana principal se ha
dibujado (o por un temporizador de seguridad).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

DEFAULT_ACCENT = "#0078D4"  # Azul de Windows 11
DEFAULT_ICON = "app/app-icon.ico"
# Iconos alternativos que un proyecto puede declarar si no hay ``app-icon``.
_ICON_CANDIDATES = (
    "app/app-icon.ico",
    "app/app-icon.png",
    "app/icon.png",
    "assets/product_logo.png",
    "assets/splash.png",
)
_SAFETY_TIMEOUT_MS = 6000
_SLIDE_DURATION_MS = 420
_SLIDE_OFFSET = 36
_SPLASH_RADIUS = 14

try:  # pragma: no cover - depende del entorno
    from PyQt6 import QtCore, QtGui, QtWidgets

    PYQT6_AVAILABLE = True
except Exception:  # pragma: no cover
    PYQT6_AVAILABLE = False


def system_accent_color() -> str:
    """Color de acento del SO, o el azul de Windows 11 si no se puede leer.

    Windows: ``HKCU\\Software\\Microsoft\\Windows\\DWM\\AccentColor`` (ABGR).
    GNOME: ``gsettings get org.gnome.desktop.interface accent-color`` o, en su
    defecto, ``gtk-theme``. En cualquier otro caso, el azul UWP.
    """
    if sys.platform.startswith("win"):
        try:
            import winreg  # type: ignore

            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\DWM",
            ) as key:
                value, _ = winreg.QueryValueEx(key, "AccentColor")
            # El registro guarda ABGR; se reordena a RRGGBB.
            r = value & 0xFF
            g = (value >> 8) & 0xFF
            b = (value >> 16) & 0xFF
            return f"#{r:02X}{g:02X}{b:02X}"
        except Exception:
            return DEFAULT_ACCENT
    if sys.platform.startswith("linux"):
        try:
            import subprocess

            out = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "accent-color"],
                capture_output=True,
                text=True,
                timeout=3,
            ).stdout.strip().strip("'")
            gnome = {
                "blue": "#3584E4",
                "teal": "#2190A4",
                "green": "#3A944A",
                "yellow": "#C88800",
                "orange": "#ED5B00",
                "red": "#E62D42",
                "pink": "#D56199",
                "purple": "#9141AC",
                "slate": "#6F8396",
            }
            if out in gnome:
                return gnome[out]
        except Exception:
            pass
    return DEFAULT_ACCENT


def _resolve_icon(script_file: str | None) -> str | None:
    """Primer icono disponible del proyecto, relativo a la raíz del guion."""
    roots = []
    if script_file:
        roots.append(Path(script_file).resolve().parent)
    roots.append(Path.cwd())
    for root in roots:
        for candidate in _ICON_CANDIDATES:
            path = root / candidate
            if path.is_file():
                return str(path)
    return None


class SplashBootloader:
    """Gestiona el ciclo de vida del splash (crear, mostrar, desvanecer)."""

    def __init__(self):
        self._script_file: str | None = None
        self._icon_path: str | None = None
        self._accent: str = DEFAULT_ACCENT
        self._widget = None
        self._fade = None
        self._slide = None
        self._safety = None

    def arm(self, script_file: str | None = None) -> "SplashBootloader":
        """Registra el contexto del splash. No necesita Qt todavía."""
        self._script_file = script_file
        self._icon_path = _resolve_icon(script_file)
        self._accent = system_accent_color()
        return self

    def start(self, app=None) -> bool:
        """Muestra el splash. Devuelve ``False`` si Qt no está disponible."""
        if not PYQT6_AVAILABLE or self._widget is not None:
            return False
        self._widget = self._build_widget()
        if self._widget is None:
            return False
        widget = self._widget
        # Entra deslizándose desde abajo con un fundido: la geometría y la
        # opacidad se animan juntas para que la apertura no sea un salto seco.
        widget.setWindowOpacity(0.0)
        target = widget.pos()
        widget.move(target.x(), target.y() + _SLIDE_OFFSET)
        widget.show()
        widget.raise_()
        self._animate_slide(target, fade_in=True)
        self._safety = QtCore.QTimer()
        self._safety.setSingleShot(True)
        self._safety.timeout.connect(self.finish)
        self._safety.start(_SAFETY_TIMEOUT_MS)
        return True

    def _animate_slide(self, target_pos, *, fade_in: bool) -> None:
        """Anima ``pos`` y ``windowOpacity`` hacia el estado estable."""
        widget = self._widget
        if widget is None:
            return
        try:
            self._slide = QtCore.QPropertyAnimation(widget, b"pos")
            self._slide.setDuration(_SLIDE_DURATION_MS)
            self._slide.setStartValue(widget.pos())
            self._slide.setEndValue(target_pos)
            self._slide.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)
            self._slide.start()
            if fade_in:
                self._fade = QtCore.QPropertyAnimation(widget, b"windowOpacity")
                self._fade.setDuration(_SLIDE_DURATION_MS)
                self._fade.setStartValue(0.0)
                self._fade.setEndValue(1.0)
                self._fade.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)
                self._fade.start()
        except Exception:
            widget.setWindowOpacity(1.0)

    def finish(self, app=None) -> None:
        """Desvanece el splash y lo cierra (idempotente)."""
        if self._widget is None:
            return
        widget = self._widget
        self._widget = None
        if self._safety is not None:
            self._safety.stop()
            self._safety = None
        try:
            self._fade = QtCore.QPropertyAnimation(widget, b"windowOpacity")
            self._fade.setDuration(450)
            self._fade.setStartValue(1.0)
            self._fade.setEndValue(0.0)
            self._fade.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)
            self._fade.finished.connect(widget.close)
            self._fade.start()
        except Exception:
            widget.close()

    # -- construcción de la ventana -------------------------------------
    def _build_widget(self):
        try:
            widget = QtWidgets.QWidget()
            widget.setWindowFlags(
                QtCore.Qt.WindowType.FramelessWindowHint
                | QtCore.Qt.WindowType.WindowStaysOnTopHint
            )
            widget.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
            widget.setStyleSheet(
                f"QWidget#PmSplash {{ background-color: {self._accent};"
                f" border-radius: {_SPLASH_RADIUS}px; }}"
            )

            container = QtWidgets.QWidget(widget)
            container.setObjectName("PmSplash")
            layout = QtWidgets.QVBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addStretch()

            label = QtWidgets.QLabel()
            label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            if self._icon_path and os.path.exists(self._icon_path):
                pixmap = QtGui.QPixmap(self._icon_path)
                if not pixmap.isNull():
                    label.setPixmap(
                        pixmap.scaled(
                            180,
                            180,
                            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                            QtCore.Qt.TransformationMode.SmoothTransformation,
                        )
                    )
            layout.addWidget(label)
            layout.addStretch()

            screen = QtWidgets.QApplication.primaryScreen()
            rect = screen.availableGeometry() if screen is not None else QtCore.QRect(0, 0, 1000, 650)
            widget.resize(max(640, rect.width() // 2), max(420, rect.height() // 2))
            container.resize(widget.size())
            widget._pm_container = container  # evita el GC del contenedor
            return widget
        except Exception:
            return None


# Singleton que consume el código inyectado.
bootloader = SplashBootloader()
