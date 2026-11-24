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

from lib import qss_loader

# --------------------------------------------------------------------------- #
# Paleta
# --------------------------------------------------------------------------- #
# Acento corporativo: el naranja de la marca (bugs.txt Fase 3.1). Sustituye al
# azul de Windows 11 en focos de teclado, bordes activos y selección.
ACCENT = "#FF6B00"
ACCENT_HOVER = "#FF8324"
ACCENT_PRESSED = "#D95A00"

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

# Acabado "Liquid Glass" de la tarjeta de login: superficie translúcida con el
# borde superior iluminado, para que reaccione al fondo del escritorio.
GLASS_BG = "rgba(255, 255, 255, 0.10)"
GLASS_BORDER = "rgba(255, 255, 255, 0.18)"
GLASS_BORDER_TOP = "rgba(255, 255, 255, 0.42)"

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

# --- Estados semánticos ---------------------------------------------------- #
# Centralizan los colores que los asistentes (p. ej. el wizard de MoonFix)
# escribían a mano en su QSS en línea. Un control de estado pide su color aquí
# en vez de incrustar el literal.
SUCCESS = "#28A745"          # acción correcta (fondo de botón)
SUCCESS_TEXT = "#4CAF50"     # confirmación en texto
ERROR_TEXT = "#F44336"       # error en texto
WARNING = "#FF9800"          # encabezado de aviso
WARNING_SOFT = "#FFB74D"     # aviso atenuado
CLOSE_HOVER = "#E81123"      # fondo del botón de cerrar al pasar el ratón

# --- Grises neutros de apoyo ----------------------------------------------- #
SURFACE_ELEVATED = "#333333"  # superficie elevada / control deshabilitado
SURFACE_PRESSED = "#242426"   # fondo de control al pulsar
TEXT_FAINT = "#777777"        # texto deshabilitado o muy tenue
TEXT_TERTIARY = "#888888"     # etiquetas atenuadas
TEXT_ALT = "#AAAAAA"          # descripciones de apoyo
TEXT_SOFT = "#BBBBBB"         # texto secundario suave
TITLEBAR_TEXT = "#EEEEEE"     # rótulo del título de la barra superior

# Anillo de foco del indicador de navegación por teclado. Comparte el acento
# corporativo para que el foco y la selección hablen el mismo idioma visual.
FOCUS_RING = ACCENT

# --------------------------------------------------------------------------- #
# Geometría
# --------------------------------------------------------------------------- #
WINDOW_RADIUS = 12
CONTROL_RADIUS = 6
CARD_RADIUS = 8
PILL_RADIUS = 18

SIDEBAR_MIN_WIDTH = 250
SIDEBAR_MAX_WIDTH = 270
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

# Avatar del landing: el tamaño vive aquí y el QSS deriva el radio y el
# tamaño de fuente de estos tokens. Antes el radio era un literal (``44px``)
# en ``qlabel.qss`` y cambiar ``AVATAR_SIZE`` no movía el círculo.
AVATAR_SIZE = 88
AVATAR_RADIUS = AVATAR_SIZE // 2
AVATAR_ICON_SIZE = 46
AVATAR_FONT_SIZE = 30

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


def normalize_accent(value: object, default: str = ACCENT) -> str:
    """Devuelve *value* si es un color ``#RRGGBB``; si no, *default*.

    El acento se guarda en ``pm.data`` y se interpola en QSS y en el cálculo
    del hover de los botones: un valor corrupto (texto libre, lista, ``""``)
    reventaba al parsear el hexadecimal dentro de un slot de Qt.
    """
    text = str(value or "").strip()
    if (
        len(text) == 7
        and text.startswith("#")
        and all(ch in "0123456789abcdefABCDEF" for ch in text[1:])
    ):
        return text
    return default


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
            return normalize_accent(value, default)
    except Exception:
        pass
    return default


def window_qss(accent: str = ACCENT) -> str:
    """Fondo de ventana y reglas globales de foco."""
    return qss_loader.qss("qmainwindow", WINDOW_BG=WINDOW_BG)


def input_qss(accent: str = ACCENT) -> str:
    """Inputs y combos: borde sutil y foco de 2px en el acento."""
    return qss_loader.qss(
        "qlineedit",
        role="component",
        SURFACE=SURFACE,
        BORDER=BORDER,
        CONTROL_RADIUS=CONTROL_RADIUS,
        INPUT_PADDING=INPUT_PADDING,
        INPUT_MIN_HEIGHT=INPUT_HEIGHT - 2,
        TEXT=TEXT,
        TEXT_DIM=TEXT_DIM,
        FONT_STACK=FONT_STACK,
        ACCENT=accent,
    )


def combo_qss(accent: str = ACCENT) -> str:
    """Combo plano con chevron minimalista a la derecha."""
    return input_qss(accent) + qss_loader.qss(
        "qcombobox",
        role="component",
        SURFACE=SURFACE,
        BORDER=BORDER,
        CONTROL_RADIUS=CONTROL_RADIUS,
        TEXT=TEXT,
        TEXT_MUTED=TEXT_MUTED,
        ACCENT=accent,
    )


def primary_button_qss(accent: str = ACCENT) -> str:
    """Botón primario en píldora (macOS/UWP)."""
    base, hover, pressed = accent_states(accent)
    return qss_loader.qss(
        "qpushbutton",
        role="primary",
        ACCENT=base,
        ACCENT_HOVER=hover,
        ACCENT_PRESSED=pressed,
        TEXT=TEXT,
        TEXT_DIM=TEXT_DIM,
        PILL_RADIUS=PILL_RADIUS,
        BUTTON_PADDING_H=BUTTON_PADDING_H,
        FONT_STACK=FONT_STACK,
    )


def secondary_button_qss(accent: str = ACCENT) -> str:
    """Botón secundario: superficie gris con borde sutil; realce tenue del acento."""
    return qss_loader.qss(
        "qpushbutton",
        role="secondary",
        SURFACE=SURFACE,
        SURFACE_HOVER=SURFACE_HOVER,
        BORDER=BORDER,
        CONTROL_RADIUS=CONTROL_RADIUS,
        TEXT=TEXT,
        TEXT_DIM=TEXT_DIM,
        ACCENT=accent,
        ACCENT_SOFT=with_alpha(accent, 0.16),
        FONT_STACK=FONT_STACK,
    )


def uwp_button_qss(accent: str = ACCENT) -> str:
    """Botón de acción con geometría UWP: esquinas de 4px y acento del sistema.

    Se usa en los controles secundarios del panel de configuración para
    mantener la coherencia con el instalador (flarmhandler) sin arrastrar la
    píldora de macOS.
    """
    base, hover, pressed = accent_states(accent)
    return qss_loader.qss(
        "qpushbutton",
        role="uwp",
        ACCENT=base,
        ACCENT_HOVER=hover,
        ACCENT_PRESSED=pressed,
        TEXT=TEXT,
        TEXT_DIM=TEXT_DIM,
        FONT_STACK=FONT_STACK,
    )


def destructive_button_qss() -> str:
    """Botón destructivo: rojo suave, texto rojo."""
    return qss_loader.qss(
        "qpushbutton",
        role="destructive",
        DANGER_SOFT=DANGER_SOFT,
        DANGER_TEXT=DANGER_TEXT,
        CONTROL_RADIUS=CONTROL_RADIUS,
        FONT_STACK=FONT_STACK,
    )


_ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def checkbox_qss(accent: str = ACCENT, color: str = TEXT_MUTED, size: int = 13) -> str:
    """Load the shared checkbox QSS and resolve theme-specific values."""
    return qss_loader.qss(
        "qcheckbox",
        ACCENT=accent,
        ACCENT_SOFT=with_alpha(accent, 0.24),
        TEXT_COLOR=color,
        FONT_STACK=FONT_STACK,
        FONT_SIZE=int(size),
        CHECK_ICON=str((_ASSETS_DIR / "icons" / "checkbox-check.svg").resolve()).replace("\\", "/"),
        PARTIAL_ICON=str((_ASSETS_DIR / "icons" / "checkbox-indeterminate.svg").resolve()).replace("\\", "/"),
    )


def radio_qss(accent: str = ACCENT) -> str:
    """Radio UWP: círculo gris con punto interior de acento."""
    return qss_loader.qss(
        "qradiobutton",
        TEXT_MUTED=TEXT_MUTED,
        FONT_STACK=FONT_STACK,
        TEXT=TEXT,
        SURFACE=SURFACE,
        ACCENT=accent,
    )


def slider_qss(accent: str = ACCENT) -> str:
    """Slider estilo macOS: pista fina y pulgar blanco de 16px."""
    return qss_loader.qss("qslider", BORDER=BORDER, ACCENT=accent)


def section_label_qss() -> str:
    """Etiqueta de sección: mayúsculas, 12px, atenuada."""
    return qss_loader.qss(
        "qlabel",
        role="section",
        TEXT_DIM=TEXT_DIM,
        SECTION_LABEL_SIZE=SECTION_LABEL_SIZE,
        FONT_STACK=FONT_STACK,
    )


def title_qss() -> str:
    """Título de página: 20px semibold."""
    return qss_loader.qss(
        "qlabel", role="title", TITLE_SIZE=TITLE_SIZE, FONT_STACK=FONT_STACK
    )


def mono_value_qss() -> str:
    """Valor monoespaciado para la información del sistema."""
    return qss_loader.qss("qlabel", role="mono", MONO_STACK=MONO_STACK)


def sidebar_qss(dark: bool = True, accent: str = ACCENT) -> str:
    """Barra lateral: fondo translúcido, borde de 1px y margen para el semáforo."""
    return qss_loader.qss(
        "qwidget",
        role="sidebar-dark" if dark else "sidebar-light",
        SIDEBAR_BG=SIDEBAR_BG,
        DIVIDER=DIVIDER,
        TEXT_MUTED=TEXT_MUTED,
        TEXT=TEXT,
        SIDEBAR_ICON_INSET=SIDEBAR_ICON_INSET,
        CONTROL_RADIUS=CONTROL_RADIUS,
        FONT_STACK=FONT_STACK,
        ACCENT=accent,
        ACCENT_SOFT=with_alpha(accent, 0.16),
    )


def card_qss() -> str:
    """Tarjeta/panel con radio de macOS."""
    return qss_loader.qss("qframe", role="card", WINDOW_RADIUS=WINDOW_RADIUS)
