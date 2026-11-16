# -*- coding: utf-8 -*-
"""Efectos de ventana Leviathan, maximizado frameless y escala DPI."""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, Optional, TYPE_CHECKING

try:
    from PyQt6.QtCore import QObject, QRect
    from PyQt6.QtGui import QFont
    from PyQt6.QtWidgets import QApplication, QWidget
    PYQT6_AVAILABLE = True
except (ImportError, SyntaxError):
    PYQT6_AVAILABLE = False

    class QObject:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            pass

        def setParent(self, *args, **kwargs):
            pass

    class QWidget:  # type: ignore[no-redef]
        pass

    class QApplication:  # type: ignore[no-redef]
        @staticmethod
        def instance(): return None

try:
    from leviathan_ui import WipeWindow
    LEVIATHAN_WIPE_AVAILABLE = True
except (ImportError, SyntaxError):
    LEVIATHAN_WIPE_AVAILABLE = False

    class WipeWindow(QObject):
        """Respaldo sin efectos cuando ``leviathan_ui`` no está instalado.

        Conserva el contrato de la librería real (``create``/``set_*``/``apply``
        encadenables y ``apply`` devolviendo el propio objeto) para que
        ``window.window_effects`` nunca quede en ``None`` y el control de radio
        siga operando. Sin esto, en un entorno sin ``leviathan_ui`` la ventana
        maximizada conservaba el radio y las esquinas quedaban transparentes.
        """

        def __init__(self, parent=None):
            super().__init__(parent)
            self._mode = "polished"
            self._radius = FIXED_WINDOW_RADIUS
            self._blur = FIXED_BLUR_INTENSITY

        @classmethod
        def create(cls):
            return cls()

        def set_mode(self, mode, *args, **kwargs):
            self._mode = mode
            return self

        def set_radius(self, radius, *args, **kwargs):
            self._radius = int(radius)
            return self

        def set_blur(self, blur, *args, **kwargs):
            self._blur = blur
            return self

        def apply(self, widget=None, *args, **kwargs):
            if widget is not None:
                self.setParent(widget)
            return self

if TYPE_CHECKING:
    pass

# Título fijo de ventana (no se personaliza desde pm.data)
APP_TITLE_PREFIX = "Influent Package Maker"

# Desenfoque y radio de esquinas son parte del lenguaje visual, no ajustes del
# usuario: se aplican siempre con estos valores (igual que los radios de los
# controles). Antes eran deslizadores en Configuración y permitían dejar la
# ventana ilegible.
FIXED_BLUR_INTENSITY = 14
FIXED_WINDOW_RADIUS = 12

DISPLAY_MODE_SPECS: Dict[str, Dict[str, Any]] = {
    "GhostBlur (Cristal)": {"mode": "ghostBlur", "radius": 12, "blur": 14},
    "Acrylic": {"mode": "ghost", "radius": 10, "blur": 10},
    "Mica": {"mode": "polished", "radius": 8, "blur": 0},
    "Sólido": {"mode": "polished", "radius": 4, "blur": 0},
}


def fixed_window_title(version: str, suffix: str = "") -> str:
    base = f"{APP_TITLE_PREFIX} v{version}"
    return f"{base} - {suffix}" if suffix else base


def _wipe_filters(window: QWidget):
    """Devuelve los ``WipeWindow`` anclados a *window* (filtros de efecto).

    ``WipeWindow.apply()`` hace ``setParent(widget)`` e
    ``installEventFilter(widget)``, así que cada efecto activo aparece como hijo
    de la ventana. Se recorren los hijos para detectar también filtros huérfanos
    (los que perdieron la referencia en ``window_effects``), que de otro modo
    seguirían pintando el tinte blanco.
    """
    try:
        children = window.children()
    except Exception:
        return []
    return [child for child in children if isinstance(child, WipeWindow)]


def _release_effects(window: QWidget) -> None:
    """Retira todos los filtros de efectos WipeWindow de la ventana.

    ``WipeWindow.apply()`` instala un filtro de eventos sobre la ventana y
    ``WipeWindow.create()`` devuelve un objeto **nuevo** en cada llamada. Si no
    se retira el filtro anterior, cada maximizar/restaurar deja uno más pintando
    el tinte blanco de ``ghostBlur`` y la ventana se vuelve progresivamente
    blanca. Se limpian tanto el efecto rastreado como cualquier huérfano.
    """
    previous = getattr(window, "window_effects", None)
    if previous is not None:
        _detach_filter(window, previous)
        window.window_effects = None

    for orphan in _wipe_filters(window):
        _detach_filter(window, orphan)


def _detach_filter(window: QWidget, effect: Any) -> None:
    try:
        window.removeEventFilter(effect)
    except Exception:
        pass
    try:
        effect.setParent(None)
    except Exception:
        pass


def apply_display_mode(window: QWidget, display_name: str) -> Any:
    """Aplica modo Leviathan WipeWindow a la ventana principal."""
    # Retirar el filtro anterior antes de crear uno nuevo para no acumular tintes.
    _release_effects(window)

    spec = DISPLAY_MODE_SPECS.get(display_name, DISPLAY_MODE_SPECS["GhostBlur (Cristal)"])
    # Maximizada, las esquinas deben ser rectas: un radio dejaría transparentes
    # las cuatro esquinas (se vería el escritorio detrás).
    radius = 0 if getattr(window, "_pm_maximized", False) else FIXED_WINDOW_RADIUS
    builder = WipeWindow.create().set_mode(spec["mode"]).set_radius(radius)
    if hasattr(builder, "set_blur"):
        try:
            builder = builder.set_blur(FIXED_BLUR_INTENSITY)
        except Exception:
            pass
    effects = builder.apply(window)
    window.window_effects = effects
    return effects


def apply_personalization_effects(window: QWidget, blur_intensity=None, window_radius=None) -> None:
    """Ajusta el desenfoque y radio fijos (los argumentos se ignoran).

    Se conserva la firma por compatibilidad con llamadas antiguas que pasaban
    los valores guardados en ``data/pm.data``. No vuelve a llamar a ``apply``:
    el filtro de eventos ya está instalado y reinstalarlo lo duplicaría (Qt no
    deduplica los filtros), acumulando tintes en cada maximizar.
    """
    effects = getattr(window, "window_effects", None)
    if not effects:
        return
    # Maximizada las esquinas van rectas (radio 0); si no, se ven transparentes.
    radius = 0 if getattr(window, "_pm_maximized", False) else FIXED_WINDOW_RADIUS
    try:
        if hasattr(effects, "set_radius"):
            effects.set_radius(radius)
        if hasattr(effects, "set_blur"):
            effects.set_blur(FIXED_BLUR_INTENSITY)
    except Exception:
        pass


def set_window_radius(window: QWidget, radius: int) -> None:
    """Cambia el radio de las esquinas del efecto activo y repinta.

    Al maximizar hay que pasar a radio 0: un radio distinto de cero deja las
    cuatro esquinas sin pintar (transparentes) y se ve el escritorio a través
    de ellas, que es el fallo de opacidad al maximizar.
    """
    effects = getattr(window, "window_effects", None)
    if effects is None or not hasattr(effects, "set_radius"):
        return
    try:
        effects.set_radius(int(radius))
        window.update()
    except Exception:
        pass


def patch_titlebar_maximize(titlebar, window: QWidget) -> None:
    """Reemplaza maximizado nativo (falla en ventanas frameless)."""
    # El doble clic en la barra y el menú del sistema del puente llaman a
    # ``window.toggle_frameless_maximize``; sin este enlace caían al
    # ``showMaximized()`` nativo, que sobre una ventana frameless y translúcida
    # dejaba ver el escritorio (el fallo de opacidad al maximizar).
    window.toggle_frameless_maximize = lambda: toggle_frameless_maximize(window)
    if not hasattr(titlebar, "btn_max"):
        return
    try:
        titlebar.btn_max.clicked.disconnect()
    except TypeError:
        pass
    titlebar.btn_max.clicked.connect(lambda: toggle_frameless_maximize(window))


def toggle_frameless_maximize(window: QWidget) -> None:
    maximized = bool(getattr(window, "_pm_maximized", False))
    if maximized:
        window._pm_maximized = False
        restore = getattr(window, "_pm_restore_geometry", None)
        if restore and restore.isValid():
            window.setGeometry(restore)
        else:
            window.showNormal()
        # Recuperar las esquinas redondeadas al restaurar.
        set_window_radius(window, FIXED_WINDOW_RADIUS)
        reapply = getattr(window, "_pm_reapply_display_mode", None)
        if callable(reapply):
            reapply()
        return

    geo = window.geometry()
    if geo.isValid() and geo.width() > 0:
        window._pm_restore_geometry = QRect(geo)
    screen = window.screen() or QApplication.primaryScreen()
    if screen:
        # Preserve the last non-maximized size and avoid reapplying the same
        # display styling repeatedly; the visual state is already refreshed from
        # the single reapply callback and should not be chained on each toggle.
        window.setGeometry(screen.availableGeometry())
    window._pm_maximized = True
    # Esquinas rectas mientras está maximizado: el radio dejaría transparentes
    # las esquinas y se vería el escritorio detrás.
    set_window_radius(window, 0)
    reapply = getattr(window, "_pm_reapply_display_mode", None)
    if callable(reapply):
        reapply()


def is_frameless_maximized(window: QWidget) -> bool:
    return bool(getattr(window, "_pm_maximized", False))


def apply_dpi_scale(scale: float, base_font: Optional[QFont] = None) -> float:
    """Escala la fuente de la aplicación. Devuelve escala aplicada."""
    scale = max(0.75, min(2.0, float(scale)))
    app = QApplication.instance()
    if not app:
        return scale
    font = QFont(base_font or app.font())
    base_pt = 10.0
    if base_font and base_font.pointSizeF() > 0:
        base_pt = base_font.pointSizeF()
    elif app.font().pointSizeF() > 0:
        base_pt = app.font().pointSizeF()
    font.setPointSizeF(max(8.0, base_pt * scale))
    app.setFont(font)
    return scale


def restart_application() -> None:
    """Reinicia el proceso de PackageMaker."""
    python = sys.executable
    argv = [python] + sys.argv
    os.execv(python, argv)
