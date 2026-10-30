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
    ACCENT,
    BORDER,
    BUTTON_HEIGHT,
    FONT_STACK,
    SURFACE,
    SURFACE_HOVER,
    TITLE_SIZE,
    WINDOW_RADIUS,
    destructive_button_qss,
    primary_button_qss,
    secondary_button_qss,
)

# Geometría de la barra. Los botones van en la parte superior de cada página,
# con la misma altura y radios en todas (ver tests/test_page_action_bar.py).
BAR_HEIGHT = 48
BUTTON_MIN_WIDTH = 96
TITLE_FONT_PX = TITLE_SIZE

# Colores macOS translúcidos.
STYLE_PRIMARY = primary_button_qss(ACCENT)
STYLE_SECONDARY = secondary_button_qss()
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
        f"QPushButton:pressed{{background:#242426;}}"
    )
    if icon is not None:
        try:
            btn.setIcon(icon)
        except Exception:
            pass
    return btn


def install_page_action_bar(
    parent_layout,
    title: str,
    buttons: Sequence["QPushButton"] = (),
) -> Tuple["QWidget", "QLabel"]:
    """Inserta una barra de acciones al principio de ``parent_layout``.

    Devuelve ``(bar, title_label)`` para que la página pueda actualizar el
    texto (traducciones en tiempo real) o reparentar sus botones.
    """
    bar = QWidget()
    bar.setObjectName("PageActionBar")
    bar.setFixedHeight(BAR_HEIGHT)
    bar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    bar.setStyleSheet(
        f"QWidget#PageActionBar{{background:rgba(255,255,255,0.04);"
        f"border:1px solid rgba(255,255,255,0.07);border-radius:{WINDOW_RADIUS}px;}}"
    )

    row = QHBoxLayout(bar)
    row.setContentsMargins(16, 0, 12, 0)
    row.setSpacing(8)

    title_lbl = QLabel(title)
    title_lbl.setStyleSheet(STYLE_TITLE)
    row.addWidget(title_lbl)
    row.addStretch()

    for btn in buttons:
        row.addWidget(btn)

    parent_layout.insertWidget(0, bar)
    return bar, title_lbl
