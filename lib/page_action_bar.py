# -*- coding: utf-8 -*-
"""Barra de acciones superior estilo macOS, independiente por página.

Cada página de la aplicación coloca su propia barra en la parte **superior**
del contenido: el título de la página a la izquierda y sus botones de acción
alineados a la derecha, con el aspecto de píldora translúcida de macOS.

La barra es autocontenida: recibe los botones que le pertenecen y no comparte
ningún widget con otras páginas, de modo que los controles de una página nunca
quedan enlazados (ni sobrescritos) por los de otra.
"""

from __future__ import annotations

import html
import re
from typing import Sequence, Tuple

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

    PYQT6_AVAILABLE = True
except ImportError:  # pragma: no cover - entorno sin Qt
    PYQT6_AVAILABLE = False

    class QWidget:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            pass


from lib.design_tokens import (
    BORDER,
    TEXT_DIM,
    BUTTON_HEIGHT,
    FONT_STACK,
    SURFACE,
    SURFACE_HOVER,
    SURFACE_PRESSED,
    TITLE_SIZE,
    WINDOW_RADIUS,
    accent_states,
    active_accent,
    destructive_button_qss,
    primary_button_qss,
    secondary_button_qss,
)
from lib.activity_bar import ActivityBar
from lib.hover_animation import enable_hover_fade


ACCENT_COLOR = active_accent()
ACCENT_HOVER = accent_states(ACCENT_COLOR)[1]

# Color de resalte al pasar el ratón por cada tipo de botón. La animación parte
# del fondo declarado en el QSS del propio botón.
HOVER_COLORS = {
    "primary": ACCENT_HOVER,
    "secondary": SURFACE_HOVER,
    "destructive": "rgba(255, 69, 58, 0.28)",
}

# Geometría de la barra. Los botones van en la parte superior de cada página,
# con la misma altura y radios en todas (ver tests/test_page_action_bar.py).
BAR_HEIGHT = 48
BUTTON_MIN_WIDTH = 96
TITLE_FONT_PX = TITLE_SIZE

# Colores macOS translúcidos.
STYLE_PRIMARY = primary_button_qss(ACCENT_COLOR)
STYLE_SECONDARY = secondary_button_qss(ACCENT_COLOR)
STYLE_DESTRUCTIVE = destructive_button_qss()
STYLE_TITLE = (
    f"color:#f5f7fb;font-size:{TITLE_FONT_PX}px;font-weight:600;"
    f"background:transparent;font-family:{FONT_STACK};"
)


def make_action_button(text: str, kind: str = "primary", icon=None) -> "QPushButton":
    """Crea un botón de la barra con el estilo macOS pedido.

    ``kind`` es uno de ``primary`` (azul), ``secondary`` (gris translúcido) o
    ``destructive`` (rojo translúcido).
    """
    btn = QPushButton(text)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    btn.setFixedHeight(BUTTON_HEIGHT)
    btn.setMinimumWidth(BUTTON_MIN_WIDTH)
    style = {
        "primary": STYLE_PRIMARY,
        "secondary": STYLE_SECONDARY,
        "destructive": STYLE_DESTRUCTIVE,
    }.get(kind, STYLE_SECONDARY)
    btn.setStyleSheet(style)
    if icon is not None:
        try:
            btn.setIcon(icon)
        except Exception:
            pass
    enable_hover_fade(btn, HOVER_COLORS.get(kind, SURFACE_HOVER))
    return btn


def make_icon_button(icon, tooltip: str = "", size: int = 34) -> "QPushButton":
    """Botón circular que sólo muestra un icono (redes sociales, acciones)."""
    btn = QPushButton()
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    btn.setFixedSize(size, size)
    btn.setToolTip(tooltip or "")
    btn.setStyleSheet(
        f"QPushButton{{background:{SURFACE};border:1px solid {BORDER};"
        f"border-radius:{size // 2}px;}}"
        f"QPushButton:hover{{background:{SURFACE_HOVER};}}"
        f"QPushButton:pressed{{background:{SURFACE_PRESSED};}}"
    )
    if icon is not None:
        try:
            btn.setIcon(icon)
        except Exception:
            pass
    enable_hover_fade(btn, SURFACE_HOVER)
    return btn


def _apply_bar_shadow(bar) -> None:
    """Sombra suave bajo la barra superior (relieve del cristal, Fase 3.2)."""
    if not PYQT6_AVAILABLE:
        return
    try:
        from lib.settings_cards import apply_soft_shadow

        apply_soft_shadow(bar, blur=18, offset=4, alpha=90)
    except Exception:
        pass


SUBTITLE_STYLE = (
    f"color:{TEXT_DIM};font-size:12px;background:transparent;"
    f"font-family:{FONT_STACK};padding:0 2px;"
)


_BOLD = re.compile(r"\*\*(.+?)\*\*")
_CODE = re.compile(r"`([^`]+)`")


def inline_markup(text: str) -> str:
    """Markdown mínimo de los catálogos: ``**negrita**`` y `` `código` ``.

    El ``QLabel`` del subtítulo no interpreta Markdown, así que los asteriscos
    salían literales en la página de creación («el ecosistema **Influent OS**»).
    El texto se escapa antes de convertirlo: los catálogos no son HTML.
    """
    escaped = html.escape(text or "", quote=False)
    escaped = _BOLD.sub(r"<b>\1</b>", escaped)
    return _CODE.sub(r'<span style="font-family:monospace">\1</span>', escaped)


def set_action_bar_subtitle(bar, text: str) -> None:
    """Pone la descripción de la página bajo su título, fuera de la píldora.

    El texto vive en un ``QLabel`` propio colocado **después** de la barra, de
    modo que no comparte el fondo translúcido ni el borde de la misma.
    """
    label = getattr(bar, "subtitle_label", None)
    if label is None:
        return
    label.setText(inline_markup(text) if text else "")
    label.setVisible(bool(text))


def install_page_action_bar(
    parent_layout,
    title: str,
    buttons: Sequence["QPushButton"] = (),
) -> Tuple["QWidget", "QLabel"]:
    """Inserta una barra de acciones al principio de ``parent_layout``.

    Devuelve ``(bar, title_label)`` para que la página pueda actualizar el
    texto (traducciones en tiempo real) o reparentar sus botones. La barra
    expone además ``subtitle_label`` para la descripción de la página, que se
    dibuja debajo del título y fuera del recuadro de la barra.
    """
    bar = QWidget()
    bar.setObjectName("PageActionBar")
    bar.setFixedHeight(BAR_HEIGHT)
    bar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    bar.setStyleSheet(
        f"QWidget#PageActionBar{{background:rgba(255,255,255,0.04);"
        f"border:1px solid rgba(255,255,255,0.07);border-radius:{WINDOW_RADIUS}px;}}"
    )
    _apply_bar_shadow(bar)

    row = QHBoxLayout(bar)
    row.setContentsMargins(16, 0, 12, 0)
    row.setSpacing(8)

    title_lbl = QLabel(title)
    title_lbl.setStyleSheet(STYLE_TITLE)
    row.addWidget(title_lbl)
    row.addStretch()

    for btn in buttons:
        row.addWidget(btn)

    subtitle = QLabel("")
    subtitle.setObjectName("PageActionSubtitle")
    subtitle.setWordWrap(True)
    subtitle.setStyleSheet(SUBTITLE_STYLE)
    subtitle.setVisible(False)
    bar.subtitle_label = subtitle

    activity = ActivityBar(bar)
    activity.setObjectName("PageActivityBar")
    bar.activity_bar = activity

    owner = parent_layout.parentWidget()
    if owner is not None:
        owner._pm_action_bar = bar

    parent_layout.insertWidget(0, bar)
    parent_layout.insertWidget(1, activity)
    parent_layout.insertWidget(2, subtitle)
    return bar, title_lbl


def set_action_bar_busy(bar, busy: bool) -> None:
    """Despierta o apacigua el marquee de la barra (trabajo en segundo plano)."""
    activity = getattr(bar, "activity_bar", None)
    if activity is None:
        return
    if busy:
        activity.start()
    else:
        activity.stop()
