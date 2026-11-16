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

from pathlib import Path

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

# Fondos translúcidos para que el efecto Mica/Acrylic (Leviathan WipeWindow)
# se vea a través de ellos. Deben seguir siendo lo bastante opacos para que el
# texto conserve contraste sobre cualquier fondo de escritorio.
TITLEBAR_BG = "rgba(40, 40, 40, 0.85)"
CONTENT_BG = "rgba(28, 28, 30, 0.82)"

TEXT = "#FFFFFF"
TEXT_MUTED = "#DDDDDD"
TEXT_DIM = "#8E8E93"

# --- Paleta de la barra lateral -------------------------------------------- #
# El texto y los iconos usan **el mismo gris oscuro** en ambos temas: antes el
# modo oscuro los pintaba en blanco y el claro en gris, y el usuario quiere un
# tratamiento uniforme. La selección se distingue por el fondo y por el
# indicador azul, no por cambiar el color del texto.
SIDEBAR_TEXT_GRAY = "#6E6E73"
SIDEBAR_ICON_LIGHT = SIDEBAR_TEXT_GRAY
SIDEBAR_ICON_DARK = SIDEBAR_TEXT_GRAY
SIDEBAR_TEXT_LIGHT = SIDEBAR_TEXT_GRAY
SIDEBAR_TEXT_DARK = SIDEBAR_TEXT_GRAY
SIDEBAR_TEXT_SELECTED_LIGHT = SIDEBAR_TEXT_GRAY
SIDEBAR_TEXT_SELECTED_DARK = SIDEBAR_TEXT_GRAY

TEXT_LIGHT = "#000000"
TEXT_MUTED_LIGHT = "#000000"

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
# Indicador de selección: barra corta y redondeada pegada al borde izquierdo,
# centrada verticalmente (no un ``border-left`` de altura completa).
SIDEBAR_INDICATOR_WIDTH = 3
SIDEBAR_INDICATOR_HEIGHT = 18

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
FONT_STACK = "'Roboto','Segoe UI Variable Display','SF Pro Display','Segoe UI','Inter Regular',sans-serif"
MONO_STACK = "'Cascadia Code','Consolas','JetBrains Mono','DejaVu Sans Mono',monospace"


# --------------------------------------------------------------------------- #
# Constructores QSS
# --------------------------------------------------------------------------- #
def shade_color(color: str, factor: float) -> str:
    """Aclara (``factor > 1``) u oscurece (``factor < 1``) un ``#RRGGBB``.

    Devuelve la entrada sin cambios si no es un color reconocible, para que un
    valor raro del usuario no rompa la hoja de estilos.
    """
    try:
        red = int(color[1:3], 16)
        green = int(color[3:5], 16)
        blue = int(color[5:7], 16)
    except (ValueError, IndexError):
        return color
    clamp = lambda v: max(0, min(255, int(v * factor)))
    return f"#{clamp(red):02X}{clamp(green):02X}{clamp(blue):02X}"


def tint_color(color: str, amount: float) -> str:
    """Mezcla ``color`` hacia blanco en la proporción ``amount`` (0..1).

    Se usa para fondos tenues del acento (hover del botón secundario, badges).
    Multiplicar los canales saturaba a cian/blanco puro en lugar de aclarar.
    """
    try:
        red = int(color[1:3], 16)
        green = int(color[3:5], 16)
        blue = int(color[5:7], 16)
    except (ValueError, IndexError):
        return color
    amount = max(0.0, min(1.0, amount))
    blend = lambda channel: int(channel + (255 - channel) * amount)
    return f"#{blend(red):02X}{blend(green):02X}{blend(blue):02X}"


def with_alpha(color: str, alpha: float) -> str:
    """Convierte ``#RRGGBB`` en ``rgba(r, g, b, alpha)`` (para fondos suaves)."""
    try:
        red = int(color[1:3], 16)
        green = int(color[3:5], 16)
        blue = int(color[5:7], 16)
    except (ValueError, IndexError):
        return color
    return f"rgba({red}, {green}, {blue}, {max(0.0, min(1.0, alpha)):.2f})"


def accent_states(accent: str = ACCENT) -> tuple[str, str, str]:
    """Devuelve ``(base, hover, pressed)`` coherentes con *accent*.

    Para el azul por defecto se conservan los valores curados de Windows 11; con
    un acento personalizado, hover y pressed se derivan del propio color. Antes
    eran azules fijos y el acento del usuario sólo teñía el estado base.
    """
    value = (accent or "").strip()
    if not value:
        return ACCENT, ACCENT_HOVER, ACCENT_PRESSED
    if value.upper() == ACCENT.upper():
        return ACCENT, ACCENT_HOVER, ACCENT_PRESSED
    return value, shade_color(value, 1.12), shade_color(value, 0.82)


def active_accent(default: str = ACCENT) -> str:
    """Acento activo según la preferencia del usuario y, si no, *default*.

    Fuente única para las páginas y diálogos que antes repetían su propio
    ``_accent()``. El paso por ``leviathan_ui`` vive en
    ``packagemaker.get_accent_color`` (nivel de aplicación); aquí basta la
    preferencia guardada en ``pm_data``.
    """
    try:
        from lib.pm_data import get_pm_data

        value = str(get_pm_data().get_user("custom_accent_color", "") or "").strip()
        if value:
            return value
    except Exception:
        pass
    return default


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
    base, hover, pressed = accent_states(accent)
    return f"""
    QPushButton {{
        background-color: {base};
        color: {TEXT};
        border: none;
        border-radius: {PILL_RADIUS}px;
        padding: 0 {BUTTON_PADDING_H}px;
        font-family: {FONT_STACK};
        font-size: 13px;
        font-weight: 600;
    }}
    QPushButton:hover {{ background-color: {hover}; }}
    QPushButton:pressed {{ background-color: {pressed}; }}
    QPushButton:disabled {{ background-color: #3A3A3C; color: {TEXT_DIM}; }}
    """


def secondary_button_qss(accent: str = ACCENT) -> str:
    """Botón secundario: superficie gris con borde sutil; realce tenue del acento."""
    soft = with_alpha(accent, 0.16)
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
    QPushButton:hover {{ background-color: {SURFACE_HOVER}; border-color: {accent}; }}
    QPushButton:pressed {{ background-color: {soft}; }}
    QPushButton:disabled {{ color: {TEXT_DIM}; }}
    """


def uwp_button_qss(accent: str = ACCENT) -> str:
    """Botón de acción con geometría UWP: esquinas de 4px y acento del sistema.

    Se usa en los controles secundarios del panel de configuración para
    mantener la coherencia con el instalador (flarmhandler) sin arrastrar la
    píldora de macOS.
    """
    base, hover, pressed = accent_states(accent)
    return (
        f"QPushButton{{background:{base};color:{TEXT};border:none;"
        f"border-radius:4px;font-weight:600;font-family:{FONT_STACK};}}"
        f"QPushButton:hover{{background:{hover};}}"
        f"QPushButton:pressed{{background:{pressed};}}"
        f"QPushButton:disabled{{background:#3A3A3C;color:{TEXT_DIM};}}"
    )


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


_ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
_CHECKBOX_QSS = (_ASSETS_DIR / "checkbox.qss").read_text(encoding="utf-8")


def checkbox_qss(accent: str = ACCENT, color: str = TEXT_MUTED, size: int = 13) -> str:
    """Load the shared checkbox QSS and resolve theme-specific values."""
    replacements = {
        "__ACCENT__": str(accent),
        "__TEXT_COLOR__": str(color),
        "__FONT_STACK__": FONT_STACK,
        "__FONT_SIZE__": str(int(size)),
        "__CHECK_ICON__": str((_ASSETS_DIR / "icons" / "checkbox-check.svg").resolve()).replace("\\", "/"),
        "__PARTIAL_ICON__": str((_ASSETS_DIR / "icons" / "checkbox-indeterminate.svg").resolve()).replace("\\", "/"),
    }
    stylesheet = _CHECKBOX_QSS
    for token, value in replacements.items():
        stylesheet = stylesheet.replace(token, value)
    return stylesheet


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
