# -*- coding: utf-8 -*-
"""Efectos de ventana Leviathan, maximizado frameless y escala DPI."""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, Optional, TYPE_CHECKING

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QWidget

from leviathan_ui import WipeWindow

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QMainWindow

# Título fijo de ventana (no se personaliza desde pm.data)
APP_TITLE_PREFIX = "Influent Package Maker"

DISPLAY_MODE_SPECS: Dict[str, Dict[str, Any]] = {
    "GhostBlur (Cristal)": {"mode": "ghostBlur", "radius": 12, "blur": 14},
    "Acrylic": {"mode": "ghost", "radius": 10, "blur": 10},
    "Mica": {"mode": "polished", "radius": 8, "blur": 0},
    "Sólido": {"mode": "polished", "radius": 4, "blur": 0},
}


def fixed_window_title(version: str, suffix: str = "") -> str:
    base = f"{APP_TITLE_PREFIX} v{version}"
    return f"{base} - {suffix}" if suffix else base


def apply_display_mode(window: QWidget, display_name: str) -> Any:
    """Aplica modo Leviathan WipeWindow a la ventana principal."""
    # Clear existing effects before applying new ones to prevent accumulation
    if hasattr(window, 'window_effects') and window.window_effects:
        try:
            window.window_effects = None
        except Exception:
            pass

    spec = DISPLAY_MODE_SPECS.get(display_name, DISPLAY_MODE_SPECS["GhostBlur (Cristal)"])
    builder = WipeWindow.create().set_mode(spec["mode"]).set_radius(int(spec.get("radius", 12)))
    blur = spec.get("blur", 0)
    if blur and hasattr(builder, "set_blur"):
        try:
            builder = builder.set_blur(int(blur))
        except Exception:
            pass
    effects = builder.apply(window)
    window.window_effects = effects
    return effects


def apply_personalization_effects(window: QWidget, blur_intensity: int, window_radius: int) -> None:
    """Ajusta blur/radio según personalización (requiere effects activos)."""
    effects = getattr(window, "window_effects", None)
    if not effects:
        return
    try:
        if hasattr(effects, "set_radius"):
            effects.set_radius(int(window_radius))
        if blur_intensity > 0 and hasattr(effects, "set_blur"):
            effects.set_blur(int(blur_intensity))
        effects.apply(window)
    except Exception:
        pass


def patch_titlebar_maximize(titlebar, window: QWidget) -> None:
    """Reemplaza maximizado nativo (falla en ventanas frameless)."""
    if not hasattr(titlebar, "btn_max"):
        return
    try:
        titlebar.btn_max.clicked.disconnect()
    except TypeError:
        pass
    titlebar.btn_max.clicked.connect(lambda: toggle_frameless_maximize(window))


def toggle_frameless_maximize(window: QWidget) -> None:
    if getattr(window, "_pm_maximized", False):
        window._pm_maximized = False
        restore = getattr(window, "_pm_restore_geometry", None)
        if restore and restore.isValid():
            window.setGeometry(restore)
        else:
            window.showNormal()
        reapply = getattr(window, "_pm_reapply_display_mode", None)
        if callable(reapply):
            reapply()
        return

    geo = window.geometry()
    if geo.isValid() and geo.width() > 0:
        window._pm_restore_geometry = QRect(geo)
    screen = window.screen() or QApplication.primaryScreen()
    if screen:
        window.setGeometry(screen.availableGeometry())
    window._pm_maximized = True
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
