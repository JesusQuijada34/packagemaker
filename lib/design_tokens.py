# -*- coding: utf-8 -*-
"""Tokens de diseño y QSS del híbrido macOS + UWP.

Un solo lugar para la paleta, radios, espaciados y tipografía. Las páginas y
los widgets piden aquí sus estilos en vez de escribir colores a mano, de modo
que un cambio de acento o de radio se propaga a toda la interfaz.

Estructura visual:
- **macOS**: radios amplios en ventana/barra (12px), píldoras, títulos
  semibold, sidebar con margen superior para el "semáforo".
- **UWP**: materiales oscuros, inputs de borde sutil, foco de 2px en azul,
  controles planos sin degradados.

Sin dependencias de PyQt6: sólo devuelve cadenas QSS y números.
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# Paleta
# --------------------------------------------------------------------------- #
ACCENT = "#0078D4"
ACCENT_HOVER = "#1084D8"
ACCENT_PRESSED = "#005FB8"

WINDOW_BG = "#1C1C1E"
SURFACE = "#2D2D2D"
SURFACE_HOVER = "#3A3A3C"
BORDER = "#444444"
DIVIDER = "#333333"

SIDEBAR_BG = "rgba(40, 40, 40, 0.85)"
SIDEBAR_BG_SOLID = "#282828"

TEXT = "#FFFFFF"
TEXT_MUTED = "#DDDDDD"
TEXT_DIM = "#8E8E93"

DANGER = "#FF453A"
DANGER_SOFT = "rgba(255, 69, 58, 0.16)"
DANGER_TEXT = "#FF6B60"

# --------------------------------------------------------------------------- #
# Geometría
# --------------------------------------------------------------------------- #
WINDOW_RADIUS = 12
CONTROL_RADIUS = 6
CARD_RADIUS = 8
PILL_RADIUS = 18

SIDEBAR_MIN_WIDTH = 240
SIDEBAR_MAX_WIDTH = 260
SIDEBAR_TOP_MARGIN = 48
SIDEBAR_PADDING = 16
SIDEBAR_ITEM_HEIGHT = 40
SIDEBAR_ICON_INSET = 16
SIDEBAR_ICON_TEXT_GAP = 12

CONTENT_PADDING = 32
TITLE_SIZE = 20
TITLE_BOTTOM_MARGIN = 24

INPUT_HEIGHT = 38
INPUT_PADDING = 10
FORM_ROW_GAP = 16

BUTTON_HEIGHT = 36
BUTTON_PADDING_H = 24

SECTION_LABEL_SIZE = 12

# --------------------------------------------------------------------------- #
# Tipografía
# --------------------------------------------------------------------------- #
FONT_STACK = "'Segoe UI Variable Display','SF Pro Display','Segoe UI','Inter Regular',sans-serif"
MONO_STACK = "'Cascadia Code','Consolas','JetBrains Mono','DejaVu Sans Mono',monospace"


# --------------------------------------------------------------------------- #
# Constructores QSS
# --------------------------------------------------------------------------- #
def window_qss(accent: str = ACCENT) -> str:
    """Fondo de ventana y reglas globales de foco."""
    return f"""
    QMainWindow, QDialog {{ background-color: {WINDOW_BG}; }}
    QWidget:focus, QPushButton:focus, QCheckBox:focus,
    QRadioButton:focus, QComboBox:focus, QListWidget:focus,
    QSlider:focus, QLineEdit:focus {{ outline: none; }}
    """


def input_qss(accent: str = ACCENT) -> str:
    """Inputs y combos: borde sutil y foco de 2px en el acento."""
    return f"""
    QLineEdit, QComboBox, QPlainTextEdit, QTextEdit {{
        background-color: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: {CONTROL_RADIUS}px;
        padding: 0 {INPUT_PADDING}px;
        color: {TEXT};
        font-family: {FONT_STACK};
        font-size: 14px;
        min-height: {INPUT_HEIGHT - 2}px;
        selection-background-color: {accent};
    }}
    QLineEdit:hover, QComboBox:hover {{ border-color: #5A5A5C; }}
    QLineEdit:focus, QComboBox:focus {{ border: 2px solid {accent}; }}
    QLineEdit:disabled, QComboBox:disabled {{ color: {TEXT_DIM}; background: #242426; }}
    """


def combo_qss(accent: str = ACCENT) -> str:
    """Combo plano con chevron minimalista a la derecha."""
    return (
        input_qss(accent)
        + f"""
    QComboBox::drop-down {{
        border: none;
        width: 28px;
        subcontrol-origin: padding;
        subcontrol-position: center right;
    }}
    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid {TEXT_MUTED};
        width: 0; height: 0;
        margin-right: 8px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: {CONTROL_RADIUS}px;
        color: {TEXT};
        selection-background-color: {accent};
        outline: none;
    }}
    """
    )


def primary_button_qss(accent: str = ACCENT) -> str:
    """Botón primario en píldora (macOS/UWP)."""
    return f"""
    QPushButton {{
        background-color: {accent};
        color: {TEXT};
        border: none;
        border-radius: {PILL_RADIUS}px;
        padding: 0 {BUTTON_PADDING_H}px;
        font-family: {FONT_STACK};
        font-size: 13px;
        font-weight: 600;
    }}
    QPushButton:hover {{ background-color: {ACCENT_HOVER}; }}
    QPushButton:pressed {{ background-color: {ACCENT_PRESSED}; }}
    QPushButton:disabled {{ background-color: #3A3A3C; color: {TEXT_DIM}; }}
    """


def secondary_button_qss() -> str:
    """Botón secundario: superficie gris con borde sutil."""
    return f"""
    QPushButton {{
        background-color: {SURFACE};
        color: {TEXT};
        border: 1px solid {BORDER};
        border-radius: {CONTROL_RADIUS}px;
        padding: 0 16px;
        font-family: {FONT_STACK};
        font-size: 13px;
        font-weight: 500;
    }}
    QPushButton:hover {{ background-color: {SURFACE_HOVER}; }}
    QPushButton:pressed {{ background-color: #242426; }}
    QPushButton:disabled {{ color: {TEXT_DIM}; }}
    """


def destructive_button_qss() -> str:
    """Botón destructivo: rojo suave, texto rojo."""
    return f"""
    QPushButton {{
        background-color: {DANGER_SOFT};
        color: {DANGER_TEXT};
        border: 1px solid rgba(255, 69, 58, 0.35);
        border-radius: {CONTROL_RADIUS}px;
        padding: 0 16px;
        font-family: {FONT_STACK};
        font-size: 13px;
        font-weight: 600;
    }}
    QPushButton:hover {{ background-color: rgba(255, 69, 58, 0.28); }}
    QPushButton:pressed {{ background-color: rgba(255, 69, 58, 0.4); }}
    """


def checkbox_qss(accent: str = ACCENT) -> str:
    """Checkbox estilo macOS: cuadrado de 4px con tick blanco sobre acento."""
    return f"""
    QCheckBox {{
        color: {TEXT_MUTED};
        font-family: {FONT_STACK};
        font-size: 13px;
        spacing: 8px;
        background: transparent;
        border: none;
    }}
    QCheckBox::indicator {{
        width: 18px; height: 18px;
        border-radius: 4px;
        border: 1px solid #6E6E73;
        background: transparent;
    }}
    QCheckBox::indicator:hover {{ border-color: {accent}; }}
    QCheckBox::indicator:pressed {{ background: rgba(0, 120, 212, 0.24); border-color: {accent}; }}
    QCheckBox::indicator:checked {{ background: {accent}; border-color: {accent}; }}
    QCheckBox::indicator:disabled {{ background: #333; border-color: #555; }}
    QCheckBox:disabled {{ color: #777; }}
    """


def radio_qss(accent: str = ACCENT) -> str:
    """Radio UWP: círculo gris con punto interior de acento."""
    return f"""
    QRadioButton {{
        color: {TEXT_MUTED};
        font-family: {FONT_STACK};
        font-size: 13px;
        spacing: 8px;
        background: transparent;
    }}
    QRadioButton::indicator {{
        width: 18px; height: 18px;
        border-radius: 10px;
        border: 2px solid #8E8E93;
        background: transparent;
    }}
    QRadioButton::indicator:hover {{ border-color: {TEXT}; }}
    QRadioButton::indicator:checked {{
        border: 5px solid {accent};
        background: {SURFACE};
    }}
    QRadioButton:disabled {{ color: #777; }}
    """


def slider_qss(accent: str = ACCENT) -> str:
    """Slider estilo macOS: pista fina y pulgar blanco de 16px."""
    return f"""
    QSlider::groove:horizontal {{
        height: 4px;
        background: {BORDER};
        border-radius: 2px;
        margin: 0 2px;
    }}
    QSlider::sub-page:horizontal {{
        background: {accent};
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background: #FFFFFF;
        width: 16px;
        height: 16px;
        margin: -6px 0;
        border-radius: 8px;
        border: 1px solid rgba(0, 0, 0, 0.25);
    }}
    QSlider::handle:horizontal:hover {{ background: #F2F2F7; }}
    QSlider::handle:horizontal:pressed {{ background: #E5E5EA; }}
    """


def section_label_qss() -> str:
    """Etiqueta de sección: mayúsculas, 12px, atenuada."""
    return (
        f"color:{TEXT_DIM};font-size:{SECTION_LABEL_SIZE}px;font-weight:600;"
        f"letter-spacing:1px;text-transform:uppercase;background:transparent;"
        f"font-family:{FONT_STACK};"
    )


def title_qss() -> str:
    """Título de página: 20px semibold."""
    return (
        f"color:#F5F7FB;font-size:{TITLE_SIZE}px;font-weight:600;"
        f"background:transparent;font-family:{FONT_STACK};"
    )


def mono_value_qss() -> str:
    """Valor monoespaciado para la información del sistema."""
    return f"color:#C7C7CC;font-size:12px;font-family:{MONO_STACK};background:transparent;"


def sidebar_qss(dark: bool = True, accent: str = ACCENT) -> str:
    """Barra lateral: fondo translúcido, borde de 1px y margen para el semáforo."""
    if dark:
        bg, border, text = SIDEBAR_BG, DIVIDER, TEXT_MUTED
    else:
        bg, border, text = "rgba(242,242,247,0.9)", "#D1D1D6", "#1C1C1E"
    return f"""
    QWidget#NavigationSidebar {{
        background: {bg};
        border-right: 1px solid {border};
    }}
    QWidget#NavigationSidebar QPushButton {{
        color: {text};
        text-align: left;
        padding-left: {SIDEBAR_ICON_INSET}px;
        border: none;
        border-left: 3px solid transparent;
        border-radius: {CONTROL_RADIUS}px;
        font-family: {FONT_STACK};
        font-size: 14px;
        font-weight: 500;
    }}
    QWidget#NavigationSidebar QPushButton:hover {{ background: rgba(255,255,255,0.06); }}
    QWidget#NavigationSidebar QPushButton:checked {{
        background: rgba(255,255,255,0.10);
        border-left: 3px solid {accent};
        color: {TEXT};
    }}
    """


def card_qss() -> str:
    """Tarjeta/panel con radio de macOS."""
    return (
        f"QWidget#PageActionBar, QFrame#Card, QWidget#Card {{"
        f"background: rgba(255,255,255,0.04);"
        f"border: 1px solid rgba(255,255,255,0.08);"
        f"border-radius: {WINDOW_RADIUS}px; }}"
    )
