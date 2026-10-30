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

from typing import Iterable, Optional, Sequence, Tuple

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

    PYQT6_AVAILABLE = True
except ImportError:  # pragma: no cover - entorno sin Qt
    PYQT6_AVAILABLE = False

    class QWidget:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            pass


# Geometría de la barra. Valores explícitos para que el alto y los márgenes
# sean idénticos en todas las páginas (ver tests/test_page_action_bar.py).
BAR_HEIGHT = 44
BUTTON_HEIGHT = 30
BUTTON_MIN_WIDTH = 96
BUTTON_RADIUS = 15
TITLE_FONT_PX = 15

# Colores macOS translúcidos.
STYLE_PRIMARY = (
    "QPushButton{background:#0a84ff;color:#ffffff;border:none;border-radius:%dpx;"
    "padding:0 16px;font-size:13px;font-weight:600;}"
    "QPushButton:hover{background:#3395ff;}"
    "QPushButton:pressed{background:#0060df;}"
    "QPushButton:disabled{background:rgba(120,120,128,0.32);color:rgba(255,255,255,0.5);}"
) % BUTTON_RADIUS
STYLE_SECONDARY = (
    "QPushButton{background:rgba(120,120,128,0.24);color:#ffffff;border:none;"
    "border-radius:%dpx;padding:0 16px;font-size:13px;font-weight:500;}"
    "QPushButton:hover{background:rgba(120,120,128,0.36);}"
    "QPushButton:pressed{background:rgba(120,120,128,0.48);}"
) % BUTTON_RADIUS
STYLE_DESTRUCTIVE = (
    "QPushButton{background:rgba(255,69,58,0.22);color:#ff6b60;border:none;"
    "border-radius:%dpx;padding:0 16px;font-size:13px;font-weight:600;}"
    "QPushButton:hover{background:rgba(255,69,58,0.34);}"
    "QPushButton:pressed{background:rgba(255,69,58,0.46);}"
) % BUTTON_RADIUS
STYLE_TITLE = (
    "color:#f5f7fb;font-size:%dpx;font-weight:600;background:transparent;" % TITLE_FONT_PX
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
        "QWidget#PageActionBar{background:rgba(255,255,255,0.04);"
        "border:1px solid rgba(255,255,255,0.07);border-radius:12px;}"
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
