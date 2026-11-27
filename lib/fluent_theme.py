"""Organized Fluent styles and animated controls shared by the desktop UI."""

import os
import sys
from typing import Optional

from lib import qss_loader
from lib.design_tokens import (
    ACCENT,
    AVATAR_FONT_SIZE,
    AVATAR_RADIUS,
    BORDER,
    BUTTON_HEIGHT,
    BUTTON_PADDING_H,
    CARD_RADIUS,
    CONTENT_BG,
    CONTROL_RADIUS,
    FONT_STACK,
    GLASS_BG,
    GLASS_BORDER,
    GLASS_BORDER_TOP,
    INPUT_HEIGHT,
    INPUT_PADDING,
    PILL_RADIUS,
    SECTION_LABEL_SIZE,
    SIDEBAR_BG,
    SIDEBAR_ICON_INSET,
    SIDEBAR_TEXT_GRAY,
    SURFACE,
    TEXT,
    TEXT_DIM,
    TEXT_LIGHT,
    TEXT_MUTED,
    TEXT_MUTED_LIGHT,
    TITLEBAR_BG,
    TITLE_SIZE,
    WINDOW_BG,
    WINDOW_RADIUS,
    accent_states,
    checkbox_qss,
    with_alpha,
    destructive_button_qss,
    input_qss,
    mono_value_qss,
    primary_button_qss,
    radio_qss,
    secondary_button_qss,
    slider_qss,
)

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont, QFontDatabase, QGuiApplication
    from PyQt6.QtWidgets import QCheckBox
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False


if PYQT6_AVAILABLE:
    class FluentCheckBox(QCheckBox):
        """Native Qt checkbox rendered by the shared application-level QSS."""
else:
    class FluentCheckBox:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("FluentCheckBox requires PyQt6.")

# Extracted styles stay grouped by the interface area that owns them.
WINDOW_CHROME_STYLES = {
    'packagemaker_001': 'background:transparent;border:none;',
    'packagemaker_003': f'background:{SIDEBAR_BG};border-right:1px solid #333333;',
    'packagemaker_004': f"color:{TEXT};font-size:20px;font-weight:600;font-family:{FONT_STACK};letter-spacing:0.3px;background:transparent;border:none;",
    'packagemaker_005': 'QWidget{background-color:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.09);border-radius:10px;margin-top:10px;}',
    'packagemaker_006': 'border:none;background:transparent;color:#888;font-weight:bold;font-size:11px;text-transform:uppercase;',
    'packagemaker_007': 'background:transparent;color:#bbb;font-size:12px;line-height:1.2;border:none;',
    'packagemaker_008': f'background:{CONTENT_BG};border:none;',
    'packagemaker_010': 'QMainWindow{background:\x00QSS_SLOT_0\x00;border:none;border-radius:\x00QSS_SLOT_1\x00px;}',
    'packagemaker_065': 'color:\x00QSS_SLOT_0\x00;font-weight:600;',
    'packagemaker_066': "QPushButton{background-color:transparent;color:#c7ced8;text-align:left;padding-left:17px;border:none;border-left:\x00QSS_SLOT_0\x00px solid transparent;border-radius:9px;font-family:'Segoe UI Variable Display','Segoe UI',sans-serif;font-size:15px;font-weight:500;}QPushButton:hover{background-color:rgba(255,255,255,0.06);color:#ffffff;}QPushButton:checked{background-color:rgba(255,255,255,0.08);color:#ffffff;border-left:\x00QSS_SLOT_1\x00px solid \x00QSS_SLOT_2\x00;}QPushButton:focus{outline:none;}",
    'packagemaker_067': 'QPushButton{background:rgba(255,255,255,0.04);color:#f3f5f8;border:1px solid rgba(255,255,255,0.08);border-radius:8px;font-weight:700;}QPushButton:hover{background:rgba(255,255,255,0.08);}',
    'packagemaker_068': 'QWidget{background-color:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.09);border-radius:10px;margin-top:10px;}',
    'packagemaker_069': 'QPushButton{background-color:\x00QSS_SLOT_0\x00;color:white;font-weight:600;font-size:14px;border-radius:6px;border:none;}QPushButton:hover{background-color:\x00QSS_SLOT_1\x00;}QPushButton:pressed{background-color:\x00QSS_SLOT_2\x00;}QPushButton:disabled{background-color:#333;color:#666;}',
}

PROJECT_CREATION_STYLES = {
    'packagemaker_011': 'font-size:24px;font-weight:600;color:white;margin-bottom:10px;background:transparent;',
    'packagemaker_012': 'QGroupBox{border:none;margin-top:0px;background:transparent;}',
    'packagemaker_013': 'QPushButton{background-color:transparent;border:1px solid rgba(255,255,255,0.08);border-radius:4px;color:white;font-weight:bold;}QPushButton:hover{background-color:transparent;}QPushButton:pressed{background-color:transparent;border-color:rgba(255,255,255,0.05);}',
    'packagemaker_014': 'background-color:transparent;',
    'packagemaker_015': "font-family:'Segoe UI',sans-serif;font-size:10px;color:#ff9800;background-color:transparent;padding:3px 7px;border-radius:4px;margin-top:2px;border:none;",
    'packagemaker_016': 'margin-left:10px;',
    'packagemaker_017': 'font-size:32px;background-color:transparent;',
    'packagemaker_018': "font-family:'Segoe UI',sans-serif;font-size:16px;font-weight:600;color:#f44336;background-color:transparent;",
    'packagemaker_019': "font-family:'Segoe UI',sans-serif;font-size:11px;color:#888888;background-color:transparent;",
    'packagemaker_020': 'background-color:transparent;',
    'packagemaker_021': 'background-color:transparent;',
    'packagemaker_022': 'background-color:transparent;',
    'packagemaker_023': "font-family:'Segoe UI',sans-serif;font-size:12px;color:#cccccc;background-color:transparent;",
    'packagemaker_024': "font-family:'Segoe UI',sans-serif;font-size:12px;font-weight:600;color:#ff9800;background-color:transparent;",
    'packagemaker_025': "font-family:'Segoe UI',sans-serif;font-size:11px;color:#bbbbbb;background-color:transparent;line-height:1.0;",
    'packagemaker_026': "font-family:'Segoe UI',sans-serif;font-size:11px;color:#4CAF50;background-color:transparent;padding:1px;border-radius:6px;",
    'packagemaker_027': "QPushButton{background-color:#4CAF50;color:white;padding:0 16px;border-radius:6px;font-family:'Segoe UI',sans-serif;font-size:12px;font-weight:600;}QPushButton:hover{background-color:#45a049;}",
    'packagemaker_028': "QPushButton{background-color:transparent;color:#f44336;padding:0 16px;border-radius:6px;border:1.5px solid #f44336;font-family:'Segoe UI',sans-serif;font-size:12px;font-weight:600;}QPushButton:hover{background-color:transparent;}",
    'packagemaker_071': "font-family:'Inter Regular';font-size:14px;color:#cccccc;font-weight:500;background:transparent;",
    'packagemaker_072': input_qss(ACCENT),
    'packagemaker_073': checkbox_qss(ACCENT),
    'packagemaker_074': "font-family:'Segoe UI',sans-serif;font-size:11px;color:#4CAF50;background-color:transparent;padding:5px 10px;border-radius:4px;margin-top:5px;",
    'packagemaker_075': 'color:#c62828;',
    'packagemaker_076': 'color:#c62828;',
    'packagemaker_077': 'color:#388e3c;',
    'packagemaker_089': 'QWidget#CentralWidget{background-color:transparent;border:1px solid rgba(255,255,255,0.1);border-radius:16px;}',
    'packagemaker_090': 'color:white;font-size:24px;font-weight:bold;margin-bottom:10px;',
    'packagemaker_091': 'color:#aaa;font-size:13px;margin-bottom:20px;',
    'packagemaker_092': 'color:white;font-weight:600;',
    'packagemaker_093': 'QLineEdit{background-color:transparent;color:white;border:2px solid rgba(255,255,255,0.2);border-radius:8px;padding:12px;font-size:14px;}QLineEdit:focus{border:2px solid #2486ff;}',
    'packagemaker_094': 'color:white;font-weight:600;',
    'packagemaker_095': 'QLineEdit{background-color:transparent;color:white;border:2px solid rgba(255,255,255,0.2);border-radius:8px;padding:12px;font-size:14px;}QLineEdit:focus{border:2px solid #2486ff;}',
    'packagemaker_096': 'color:white;font-weight:600;',
    'packagemaker_097': 'QLineEdit{background-color:transparent;color:white;border:2px solid rgba(255,255,255,0.2);border-radius:8px;padding:12px;font-size:14px;}QLineEdit:focus{border:2px solid #2486ff;}',
    'packagemaker_098': 'color:white;font-weight:600;',
    'packagemaker_099': 'QLineEdit{background-color:transparent;color:white;border:2px solid rgba(255,255,255,0.2);border-radius:8px;padding:12px;font-size:14px;}QLineEdit:focus{border:2px solid #2486ff;}',
    'packagemaker_100': 'color:white;font-weight:600;',
    'packagemaker_101': 'QTextEdit{background-color:transparent;color:white;border:2px solid rgba(255,255,255,0.2);border-radius:8px;padding:12px;font-size:14px;}QTextEdit:focus{border:2px solid #2486ff;}',
    'packagemaker_154': "font-family:'Segoe UI',sans-serif;font-size:11px;color:#ff9800;background-color:transparent;padding:5px 10px;border-radius:4px;margin-top:5px;",
    'packagemaker_155': 'color:#c62828;',
    'packagemaker_158': "font-family:'Segoe UI',sans-serif;font-size:11px;color:#2196F3;background-color:transparent;padding:5px 10px;border-radius:4px;margin-top:5px;",
}

BUILD_AND_INSTALL_STYLES = {
    'packagemaker_029': 'font-size:24px;font-weight:600;color:white;margin-bottom:10px;background:transparent;',
    'packagemaker_030': 'QGroupBox{border:none;margin-top:0px;background:transparent;}',
    'packagemaker_031': 'margin-top:8px;',
    'packagemaker_032': 'QPushButton{background-color:transparent;border:1px solid rgba(255,255,255,0.08);border-radius:4px;color:white;font-weight:bold;}QPushButton:hover{background-color:transparent;}QPushButton:pressed{background-color:transparent;border-color:rgba(255,255,255,0.05);}',
    'packagemaker_033': 'color:#aaa;margin-left:10px;background-color:transparent;',
    'packagemaker_034': primary_button_qss(ACCENT),
    'packagemaker_078': "font-family:'Inter Regular';font-size:14px;color:#cccccc;font-weight:500;background:transparent;",
    'packagemaker_079': input_qss(ACCENT),
    'packagemaker_080': radio_qss(ACCENT),
    'packagemaker_104': 'QWidget#CentralWidget{background-color:transparent;border:1px solid rgba(255,255,255,0.1);border-radius:16px;}',
    'packagemaker_105': 'color:white;font-size:22px;font-weight:bold;margin-bottom:10px;',
    'packagemaker_106': 'color:#aaa;font-size:14px;margin-bottom:20px;',
    'packagemaker_107': "QTextEdit{background-color:transparent;color:#0f0;font-family:'Consolas','Courier New',monospace;border:2px solid rgba(0,255,0,0.3);border-radius:8px;padding:10px;font-size:13px;}",
    'packagemaker_110': 'QWidget#CentralWidget{background-color:transparent;border:1px solid rgba(255,255,255,0.1);border-radius:16px;}',
    'packagemaker_111': 'color:white;font-size:24px;font-weight:bold;margin-bottom:10px;',
    'packagemaker_112': 'color:#aaa;font-size:14px;margin-bottom:20px;',
    'packagemaker_113': 'QGroupBox{color:white;font-weight:bold;border:2px solid rgba(255,255,255,0.2);border-radius:8px;margin-top:10px;padding-top:15px;}QGroupBox::title{subcontrol-origin:margin;left:10px;padding:0 5px;}',
    'packagemaker_114': checkbox_qss(ACCENT),
    'packagemaker_115': checkbox_qss(ACCENT),
    'packagemaker_116': checkbox_qss(ACCENT),
    'packagemaker_117': "QTextEdit{background-color:transparent;color:#0f0;font-family:'Consolas','Courier New',monospace;border:2px solid rgba(0,255,0,0.3);border-radius:8px;padding:10px;font-size:13px;}",
    'packagemaker_156': 'QLineEdit{color:#888;font-style:italic;}',
}

PACKAGE_MANAGER_STYLES = {
    'packagemaker_035': 'font-size:24px;font-weight:600;color:white;margin-bottom:5px;background:transparent;',
    'packagemaker_036': 'QSplitter::handle{background-color:transparent;}',
    'packagemaker_037': 'color:#aaa;margin-top:5px;',
    'packagemaker_081': "font-family:'Segoe UI';font-size:16px;font-weight:600;color:#e0e0e0;background-color:transparent;",
    'packagemaker_082': f"QListWidget{{background-color:transparent;border:1px solid rgba(255,255,255,0.05);border-radius:{CARD_RADIUS}px;padding:5px;outline:none;}}QListWidget::item{{background-color:transparent;border-radius:{CONTROL_RADIUS}px;padding:8px;margin-bottom:2px;color:{TEXT_MUTED};font-family:{FONT_STACK};font-size:14px;}}QListWidget::item:hover{{background-color:rgba(255,255,255,0.05);}}QListWidget::item:selected{{background-color:rgba(255,255,255,0.08);border-left:3px solid {ACCENT};color:{TEXT};}}",
    'packagemaker_083': "QPushButton{background-color:\x00QSS_SLOT_0\x00;color:\x00QSS_SLOT_1\x00;border:\x00QSS_SLOT_2\x00;border-radius:4px;font-weight:600;font-size:13px;font-family:'Segoe UI',sans-serif;padding:0 15px;}QPushButton:hover{background-color:\x00QSS_SLOT_3\x00;}QPushButton:pressed{background-color:\x00QSS_SLOT_4\x00;opacity:0.8;}",
}

CONFIGURATION_STYLES = {
    'packagemaker_038': f'color:{TEXT_DIM};font-size:{SECTION_LABEL_SIZE}px;font-weight:600;letter-spacing:1px;margin-top:24px;margin-bottom:12px;background:transparent;text-transform:uppercase;',
    'packagemaker_039': f'color:{TEXT_MUTED};font-size:13px;background:transparent;font-family:{FONT_STACK};',
    'packagemaker_040': 'font-size:22px;font-weight:600;color:white;',
    'packagemaker_041': 'QFrame{background:rgba(255,152,0,0.12);border:1px solid rgba(255,152,0,0.35);border-radius:6px;}',
    'packagemaker_042': 'color:#ffcc80;font-size:12px;background:transparent;',
    'packagemaker_043': 'QScrollArea{background:transparent;border:none;}',
    'packagemaker_044': 'background:transparent;',
    'packagemaker_046': 'QPushButton{background:rgba(255,255,255,0.08);color:white;border-radius:4px;padding:0 12px;}QPushButton:hover{background:rgba(255,255,255,0.14);}',
    'packagemaker_049': checkbox_qss(ACCENT),
    'packagemaker_050': f'color:{TEXT_DIM};font-size:11px;background:transparent;',
    'packagemaker_052': destructive_button_qss(),
    'packagemaker_084': f'color:{TEXT_DIM};font-size:{SECTION_LABEL_SIZE}px;font-family:{FONT_STACK};',
    'packagemaker_085': mono_value_qss(),
}

MAINTENANCE_STYLES = {
    'packagemaker_053': 'font-size:22px;font-weight:600;color:white;background:transparent;',
    'packagemaker_054': 'color:#9aa4b2;font-size:12px;background:transparent;',
    'packagemaker_055': checkbox_qss(ACCENT),
    'packagemaker_056': input_qss(ACCENT),
    'packagemaker_057': secondary_button_qss(),
    'packagemaker_058': 'QPushButton{background:#a371f7;color:white;font-weight:600;font-size:12px;border:none;border-radius:4px;}QPushButton:hover{background:#b084f9;}',
    'packagemaker_120': 'QWidget#CentralWidget{background-color:transparent;border:1px solid rgba(255,255,255,0.1);border-radius:16px;}',
    'packagemaker_121': 'color:white;font-size:24px;font-weight:bold;margin-bottom:10px;',
    'packagemaker_122': 'color:#aaa;font-size:14px;margin-bottom:10px;',
    'packagemaker_123': 'color:#888;font-size:13px;margin-bottom:20px;',
    'packagemaker_124': 'QGroupBox{color:white;font-weight:bold;border:2px solid rgba(255,255,255,0.2);border-radius:8px;margin-top:10px;padding-top:15px;}QGroupBox::title{subcontrol-origin:margin;left:10px;padding:0 5px;}',
    'packagemaker_125': checkbox_qss(ACCENT),
    'packagemaker_126': checkbox_qss(ACCENT),
    'packagemaker_127': checkbox_qss(ACCENT),
    'packagemaker_128': checkbox_qss(ACCENT),
    'packagemaker_129': "QTextEdit{background-color:transparent;color:#0ff;font-family:'Consolas','Courier New',monospace;border:2px solid rgba(0,255,255,0.3);border-radius:8px;padding:10px;font-size:13px;}",
}

ABOUT_STYLES = {
    'packagemaker_059': f"font-size:{TITLE_SIZE}px;font-weight:600;color:{TEXT};font-family:{FONT_STACK};",
    'packagemaker_060': f'font-size:14px;color:{TEXT_DIM};background:transparent;',
    'packagemaker_061': f'color:{TEXT_MUTED};font-size:14px;line-height:1.5;background:transparent;',
    'packagemaker_062': 'background-color:#333;color:white;border:none;border-radius:4px;padding:8px 16px;',
    'packagemaker_063': 'background-color:#0088cc;color:white;border:none;border-radius:4px;padding:8px 16px;',
    'packagemaker_086': f'background-color:{ACCENT};border-radius:32px;color:white;font-weight:bold;font-size:24px;',
    'packagemaker_087': f'color:{TEXT_DIM};font-weight:600;font-size:12px;background:transparent;',
    'packagemaker_088': mono_value_qss(),
}

PACKAGE_INSTALL_STYLES = {
    'packagemaker_132': 'QWidget#CentralWidget{background-color:transparent;border:1px solid rgba(255,255,255,0.1);border-radius:16px;}',
    'packagemaker_133': 'color:white;font-size:24px;font-weight:bold;margin-bottom:10px;',
    'packagemaker_134': 'color:#aaa;font-size:14px;margin-bottom:20px;',
    'packagemaker_135': "QTextEdit{background-color:transparent;color:#0f0;font-family:'Consolas','Courier New',monospace;border:2px solid rgba(0,255,0,0.3);border-radius:8px;padding:10px;font-size:13px;}",
}

MEXF_STYLES = {
    'packagemaker_138': 'QWidget#CentralWidget{background-color:transparent;border:1px solid rgba(255,255,255,0.1);border-radius:16px;}',
    'packagemaker_139': 'color:white;font-size:22px;font-weight:bold;margin-bottom:10px;',
    'packagemaker_140': 'color:#aaa;font-size:14px;margin-bottom:20px;',
    'packagemaker_141': "QTextEdit{background-color:transparent;color:#0f0;font-family:'Consolas','Courier New',monospace;border:2px solid rgba(0,255,0,0.3);border-radius:8px;padding:10px;font-size:13px;}",
    'packagemaker_144': 'QWidget#CentralWidget{background-color:transparent;border:1px solid rgba(255,255,255,0.1);border-radius:16px;}',
    'packagemaker_145': 'color:white;font-size:22px;font-weight:bold;margin-bottom:10px;',
    'packagemaker_146': 'color:#aaa;font-size:13px;margin-bottom:20px;',
    'packagemaker_147': 'color:white;font-weight:600;',
    'packagemaker_148': 'QLineEdit{background-color:transparent;color:white;border:2px solid rgba(255,255,255,0.2);border-radius:8px;padding:12px;font-size:14px;}QLineEdit:focus{border:2px solid #2486ff;}',
    'packagemaker_149': 'color:white;font-weight:600;',
    'packagemaker_150': 'QTextEdit{background-color:transparent;color:white;border:2px solid rgba(255,255,255,0.2);border-radius:8px;padding:12px;font-size:14px;}QTextEdit:focus{border:2px solid #2486ff;}',
    'packagemaker_151': 'color:#888;font-size:12px;margin-top:10px;',
    'packagemaker_157': 'color:white;background-color:transparent;border:1px solid rgba(255,255,255,0.1);border-radius:8px;padding:15px;font-size:13px;',
}

SHARED_DIALOG_STYLES = {
    'packagemaker_002': 'background-color:transparent;border:none;border-radius:5px;',
    'packagemaker_064': 'QWidget#SplashContainer{background-color:#1a1a1a;border-radius:0px;}',
}

STYLE_GROUPS = (
    WINDOW_CHROME_STYLES,
    PROJECT_CREATION_STYLES,
    BUILD_AND_INSTALL_STYLES,
    PACKAGE_MANAGER_STYLES,
    CONFIGURATION_STYLES,
    MAINTENANCE_STYLES,
    ABOUT_STYLES,
    PACKAGE_INSTALL_STYLES,
    MEXF_STYLES,
    SHARED_DIALOG_STYLES,
)
INLINE_STYLES = {key: stylesheet for group in STYLE_GROUPS for key, stylesheet in group.items()}

WINUI3_CHECKBOX_QSS = INLINE_STYLES["packagemaker_073"]


def qss_value(value, conversion=None, format_spec=""):
    """Apply Python f-string conversion/formatting to a QSS placeholder."""
    if conversion == "r":
        value = repr(value)
    elif conversion == "a":
        value = ascii(value)
    elif conversion == "s":
        value = str(value)
    return format(value, format_spec)


def set_qss(widget, stylesheet, values=(), append=False):
    """Apply a centralized stylesheet or a named extracted QSS template."""
    if isinstance(stylesheet, str) and stylesheet in INLINE_STYLES:
        stylesheet = INLINE_STYLES[stylesheet]
        for index, value in enumerate(values):
            stylesheet = stylesheet.replace(f"\x00QSS_SLOT_{index}\x00", str(value))
    elif values:
        raise ValueError("QSS values were supplied for a non-template stylesheet.")

    if append:
        current = widget.styleSheet().rstrip()
        stylesheet = f"{current}\n{stylesheet}" if current else stylesheet
    # Reinstalar la misma hoja no cambia un píxel y obliga a Qt a re-pulir el
    # widget y sus hijos (~35 ms medidos en la página central). Reaplicar el
    # tema tras guardar ajustes se notaba como congelación por este trabajo.
    if widget.styleSheet() == stylesheet:
        return
    widget.setStyleSheet(stylesheet)


def preferred_ui_font(size=11):
    """Return the first preferred UI font installed on the host.

    Roboto remains the project preference; Inter and SF Pro are useful native
    fallbacks on systems where Roboto is not installed.

    ``QFontDatabase.families()`` requires a live ``QGuiApplication``, so the
    query is skipped when no application exists yet and a default ``QFont`` is
    returned instead. Callers that need the preferred family must run after the
    application is constructed.

    Las fuentes descargadas por :mod:`lib.font_manager` tienen prioridad sobre
    las del sistema, de modo que la interfaz se ve igual en cualquier máquina.
    """
    if not PYQT6_AVAILABLE:
        return None
    if QGuiApplication.instance() is None:
        return QFont("sans-serif", int(size))

    family = _preferred_family()
    if family:
        return QFont(family, int(size))
    return QFont("sans-serif", int(size))


def _preferred_family():
    """Familia de UI preferida: caché del proyecto primero, luego el sistema."""
    try:
        from lib.font_manager import UI_PREFERENCE, resolve_family

        family = resolve_family(UI_PREFERENCE, kind="ui")
        if family:
            return family
    except Exception:
        pass

    installed = {family.casefold(): family for family in QFontDatabase.families()}
    for candidate in ("Roboto", "Inter Regular", "Inter", "SF Pro Display", "SF Pro", "Segoe UI Variable", "Segoe UI"):
        if candidate.casefold() in installed:
            return installed[candidate.casefold()]
    return None


def preferred_mono_font(size=10):
    """Fuente monoespaciada preferida (JetBrains Mono si está disponible)."""
    if not PYQT6_AVAILABLE:
        return None
    if QGuiApplication.instance() is None:
        return QFont("monospace", int(size))

    try:
        from lib.font_manager import MONO_PREFERENCE, resolve_family

        family = resolve_family(MONO_PREFERENCE, kind="mono")
        if family:
            return QFont(family, int(size))
    except Exception:
        pass

    installed = {family.casefold(): family for family in QFontDatabase.families()}
    for candidate in ("JetBrains Mono", "Cascadia Mono", "Consolas", "DejaVu Sans Mono"):
        if candidate.casefold() in installed:
            return QFont(installed[candidate.casefold()], int(size))
    return QFont("monospace", int(size))


def system_theme_mode():
    """Return ``dark`` or ``light`` using Qt's system color scheme first."""
    if not PYQT6_AVAILABLE:
        return "light"
    app = QGuiApplication.instance()
    if app is not None:
        try:
            hints = app.styleHints()
            if hasattr(hints, "colorScheme"):
                scheme = hints.colorScheme()
                if scheme == Qt.ColorScheme.Dark:
                    return "dark"
                if scheme == Qt.ColorScheme.Light:
                    return "light"
        except (AttributeError, RuntimeError):
            pass
        try:
            return "dark" if app.palette().color(app.palette().ColorRole.Window).lightness() < 128 else "light"
        except (AttributeError, RuntimeError):
            pass
    if sys.platform.startswith("win"):
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as key:
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return "light" if int(value) else "dark"
        except (ImportError, OSError, ValueError):
            pass
    return "dark" if "dark" in os.environ.get("GTK_THEME", "").casefold() else "light"


def sidebar_stylesheet(dark, accent="#0078d4"):
    """Theme-aware sidebar frame and navigation button styles.

    Los botones del sidebar ya no usan ``border-left``: el indicador de
    selección lo pinta ``SidebarItem`` (barra corta y centrada). Aquí sólo
    quedan el marco, el botón de colapso y la tarjeta de contexto.
    """
    return qss_loader.qss(
        "qwidget",
        role="sidebar-frame-dark" if dark else "sidebar-frame-light",
        SIDEBAR_BG=SIDEBAR_BG,
        SIDEBAR_TEXT_GRAY=SIDEBAR_TEXT_GRAY,
        CARD_RADIUS=CARD_RADIUS,
        FONT_STACK=FONT_STACK,
        ACCENT=accent,
        ACCENT_SOFT=with_alpha(accent, 0.16),
    )


def sidebar_button_stylesheet(dark, accent="#0078d4", border_width=3):
    """Return an explicit stylesheet for one sidebar navigation button.

    El texto usa el mismo gris en ambos temas (ver ``SIDEBAR_TEXT_GRAY``); la
    selección se marca con el fondo y con el indicador que pinta
    ``SidebarItem``, no cambiando el color del texto.
    """
    return qss_loader.qss(
        "qwidget",
        role="sidebar-button-dark" if dark else "sidebar-button-light",
        SIDEBAR_TEXT_GRAY=SIDEBAR_TEXT_GRAY,
        SIDEBAR_ICON_INSET=SIDEBAR_ICON_INSET,
        BORDER_WIDTH=int(border_width),
        CONTROL_RADIUS=CONTROL_RADIUS,
        FONT_STACK=FONT_STACK,
        ACCENT=accent,
        ACCENT_SOFT=with_alpha(accent, 0.16),
    )


def checkbox_stylesheet(accent=ACCENT, color=TEXT_MUTED, size=13):
    """Return the shared checkbox QSS loaded from the central asset."""
    return checkbox_qss(accent, color, size)


def application_stylesheet(dark: bool = True, accent: str = ACCENT) -> str:
    """QSS raíz para controles nuevos y superficies compartidas.

    Los widgets nuevos sólo declaran ``objectName`` y heredan estas reglas;
    así no se crean hojas de estilo locales que se queden obsoletas al cambiar
    de tema. Las reglas salen de ``source/qss`` (roles ``base``).
    """
    surface = SURFACE if dark else "#FFFFFF"
    page = WINDOW_BG if dark else "#F5F7FB"
    text = TEXT if dark else TEXT_LIGHT
    muted = TEXT_MUTED if dark else TEXT_MUTED_LIGHT
    border = BORDER if dark else "#D1D1D6"
    glass_bg = GLASS_BG if dark else "rgba(255, 255, 255, 0.72)"
    glass_border = GLASS_BORDER if dark else "rgba(15, 23, 42, 0.14)"
    glass_border_top = GLASS_BORDER_TOP if dark else "rgba(255, 255, 255, 0.95)"
    _, accent_hover, accent_pressed = accent_states(accent)
    common = {
        "SURFACE": surface,
        "CARD_SURFACE": surface,
        "CARD_BORDER": border,
        "GLASS_BG": glass_bg,
        "GLASS_BORDER": glass_border,
        "GLASS_BORDER_TOP": glass_border_top,
        "AVATAR_RADIUS": AVATAR_RADIUS,
        "AVATAR_FONT_SIZE": AVATAR_FONT_SIZE,
        "PAGE": page,
        "TEXT": text,
        "LABEL": text,
        "MUTED": muted,
        "BORDER": border,
        "ACCENT": accent,
        "ACCENT_HOVER": accent_hover,
        "ACCENT_PRESSED": accent_pressed,
        "FONT_STACK": FONT_STACK,
        "CONTROL_RADIUS": CONTROL_RADIUS,
        "CARD_RADIUS": CARD_RADIUS,
        "PILL_RADIUS": PILL_RADIUS,
        "INPUT_MIN_HEIGHT": INPUT_HEIGHT - 2,
        "BUTTON_HEIGHT": BUTTON_HEIGHT,
    }
    return "\n".join(
        [
            qss_loader.qss("qwidget", role="base", **common),
            qss_loader.qss("qlineedit", role="base", **common),
            qss_loader.qss("qpushbutton", role="base", **common),
            qss_loader.qss("qwidget", role="landing", **common),
            qss_loader.qss("qframe", role="landing", **common),
            qss_loader.qss("qlabel", role="landing", **common),
            qss_loader.qss("qpushbutton", role="landing", **common),
            qss_loader.qss("qlineedit", role="landing", **common),
            qss_loader.qss("qlabel", role="profile", **common),
            qss_loader.qss("qpushbutton", role="profile", **common),
            qss_loader.qss("qlabel", role="ide", **common),
            qss_loader.qss("qlistwidget", role="ide", **common),
        ]
    )


def global_stylesheet(accent: str = ACCENT, dark: Optional[bool] = None) -> str:
    """Hoja de estilo raíz única de la aplicación (bugs.txt Fase 3.1).

    Antes el arranque sólo aplicaba la hoja del checkbox y cada página se
    estilaba por su cuenta; ahora ``main`` instala **una** hoja global y los
    widgets nuevos heredan de ella declarando sólo su ``objectName``. El tema
    se resuelve del sistema cuando no se indica.
    """
    if dark is None:
        dark = system_theme_mode() != "light"
    text = TEXT if dark else TEXT_LIGHT
    return application_stylesheet(dark, accent) + "\n" + checkbox_stylesheet(accent, text)


def apply_global_stylesheet(app, accent: str = ACCENT, dark: Optional[bool] = None) -> bool:
    """Instala la hoja global sólo si cambió el acento o el tema.

    Reinstalar la misma hoja en ``QApplication`` obliga a Qt a re-pulir todos
    los widgets (~185 ms medidos en offscreen) sin cambiar un solo píxel, y se
    notaba como congelación al aplicar ajustes que no tocan la paleta.
    Devuelve ``True`` si la hoja se volvió a aplicar.
    """
    if dark is None:
        dark = system_theme_mode() != "light"
    key = (str(accent), bool(dark))
    if getattr(app, "_pm_global_stylesheet_key", None) == key:
        return False
    app.setStyleSheet(global_stylesheet(accent, dark))
    app._pm_global_stylesheet_key = key
    return True


def splash_titlebar_stylesheet():
    return """
        QWidget#SharedSplash QWidget#customTitleBar {
            background: rgba(25, 30, 39, 0.96);
            border: none;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }
        QWidget#SharedSplash QLabel#titleLabel {
            color: #f3f5f8;
            background: transparent;
        }
    """


def titlebar_chrome_stylesheet(base_bg: str, radius: int = WINDOW_RADIUS) -> str:
    """Fondo del chrome de la titlebar, con las esquinas superiores redondeadas.

    Centraliza el QSS que antes se escribía en línea al reaplicar el tema. La
    titlebar ocupa el borde superior de la ventana frameless, así que redondear
    sus esquinas superiores es lo que elimina las esquinas cuadradas al abrir.
    Maximizada, el radio se pasa a 0 (esquinas rectas, como el overlay).
    """
    return (
        f"QWidget {{ background-color:{base_bg}; border:none;"
        f" border-top-left-radius:{int(radius)}px;"
        f" border-top-right-radius:{int(radius)}px; }}"
        " QLabel { background:transparent; border:none; }"
    )


def titlebar_label_stylesheet(text_col: str) -> str:
    """Texto del título de la titlebar según el tema."""
    return (
        f"background:transparent; color:{text_col};"
        f" font-family:{FONT_STACK}; font-weight:600;"
    )


def titlebar_background_stylesheet(base_bg: str = TITLEBAR_BG) -> str:
    """Fondo plano de la titlebar en la construcción inicial (sin radio).

    Centraliza el QSS que antes se escribía en línea en ``packagemaker.py``; el
    redondeo de las esquinas superiores lo aplica ``titlebar_chrome_stylesheet``
    al mostrar la ventana.
    """
    return f"background-color:{base_bg}; border:none;"


def status_bar_stylesheet(radius: int = WINDOW_RADIUS) -> str:
    """Barra de estado oscura, translúcida y con las esquinas inferiores curvas."""
    return (
        "QStatusBar{background:rgba(255,255,255,0.04);color:#c7ced8;"
        "border-top:1px solid rgba(255,255,255,0.08);font-size:12px;"
        f"padding:2px 10px; border-bottom-left-radius:{int(radius)}px;"
        f" border-bottom-right-radius:{int(radius)}px;}}"
        " QStatusBar::item{border:none;}"
    )


def transparent_logo_stylesheet() -> str:
    """Marco transparente con relleno para el logo con sombra."""
    return "background: transparent; border: none; padding: 6px;"


def splash_container_stylesheet(accent: str = ACCENT) -> str:
    """Fondo de acento del splash integrado, como plantilla parametrizada."""
    return (
        f"QWidget#SplashContainer {{ background-color:{accent};"
        " border-radius: 0px; }"
    )


def error_container_stylesheet(accent: str = ACCENT) -> str:
    """Ventana solitaria de error de arranque (bugs.txt Fase 2.2).

    El fondo de acento del splash no sirve para leer un traceback; aquí el
    acento queda como filete superior y el resto usa la superficie oscura del
    tema con el detalle en monoespaciada.
    """
    return (
        "QWidget#StartupErrorWindow {"
        f" background-color:{SURFACE}; border-top:3px solid {accent}; }}"
        " QFrame#StartupErrorBody {"
        f" background-color:{SURFACE}; border:none; }}"
        " QLabel#StartupErrorTitle {"
        f" color:{TEXT}; font-size:22px; font-weight:600;"
        " font-family:'Segoe UI Variable','Segoe UI',sans-serif; }"
        " QLabel#StartupErrorDetail {"
        f" color:{TEXT_DIM}; font-size:12px;"
        " font-family:'Cascadia Mono','Consolas',monospace;"
        f" background-color:{WINDOW_BG}; border:1px solid {BORDER};"
        f" border-radius:{CONTROL_RADIUS}px; padding:12px; }}"
        " QScrollArea#StartupErrorScroll {"
        " background:transparent; border:none; }"
        " QPushButton#StartupErrorClose {"
        f" background-color:{accent}; color:#ffffff; border:none;"
        f" border-radius:{CONTROL_RADIUS}px; padding:8px 28px;"
        " font-size:13px; font-weight:600; }"
        " QPushButton#StartupErrorClose:hover {"
        f" background-color:{accent}; }}"
    )


def conf_field_stylesheet(readonly=False):
    values = {
        "SURFACE": SURFACE,
        "BORDER": BORDER,
        "CONTROL_RADIUS": CONTROL_RADIUS,
        "TEXT": TEXT,
        "TEXT_DIM": TEXT_DIM,
        "TEXT_MUTED": TEXT_MUTED,
        "INPUT_PADDING": INPUT_PADDING,
        "INPUT_MIN_HEIGHT": INPUT_HEIGHT - 2,
        "ACCENT": ACCENT,
    }
    fields = qss_loader.qss(
        "qlineedit", role="readonly" if readonly else "field", **values
    )
    if readonly:
        return fields
    return fields + qss_loader.qss("qcombobox", role="field", **values)


BTN_STYLES = {'default': 'background-color: transparent;color: rgba(32,33,36,0.96);border-radius: 9px;padding: '
            '10px 20px;font-weight: 600;border: 1px solid rgba(209,215,224,0.65);',
 'success': 'background-color: transparent;color: rgba(5,98,55,0.99);border-radius: 9px;padding: '
            '10px 20px;font-weight: 600;border: 1px solid rgba(199,232,206,0.60);',
 'danger': 'background-color: transparent;color: rgba(185,29,29,1.0);border-radius: 9px;padding: '
           '10px 20px;font-weight: 600;border: 1px solid rgba(255,180,180,0.68);',
 'warning': 'background-color: transparent;color: rgba(168,132,4,0.97);border-radius: 9px;padding: '
            '10px 20px;font-weight: 600;border: 1px solid rgba(255,224,149,0.66);',
 'info': 'background-color: transparent;color: rgba(9,82,165,1.0);border-radius: 9px;padding: 10px '
         '20px;font-weight: 600;border: 1px solid rgba(185,213,253,0.56);',
 'best': 'background-color: transparent;color: #0853c4;border-radius: 11px;padding: 12px '
         '22px;font-weight: 700;border: 2px solid #99d3f7;font-size: 15px;',
 'grayed-black': 'background-color: #292929;color: #b9b9b9;border-radius: 9px;padding: 10px '
                 '20px;font-weight: 600;border: 1px solid #444;background-image: none;'}

TITLE_BAR_STYLESHEET = f"""
    QWidget#SharedTitleBar {{
        background-color: {TITLEBAR_BG};
        border: none;
    }}
    QLabel#SharedTitleLabel {{
        color: #f3f5f8;
        font-family: {FONT_STACK};
        font-size: 13px;
        font-weight: 500;
        background: transparent;
    }}
    QLabel#SharedIconFallback {{
        color: {ACCENT};
        font-size: 20px;
        font-weight: 600;
        background: transparent;
    }}
    QPushButton#TitleMinimizeButton, QPushButton#TitleMaximizeButton,
    QPushButton#TitleCloseButton {{
        color: #f3f5f8;
        background: transparent;
        border: none;
        border-radius: 0;
        font-size: 13px;
        padding: 0;
    }}
    QPushButton#TitleMinimizeButton:hover,
    QPushButton#TitleMaximizeButton:hover {{
        background: rgba(255, 255, 255, 0.12);
    }}
    QPushButton#TitleCloseButton:hover {{
        background: #c42b1c;
    }}
"""


def splash_stylesheet(accent: str = ACCENT) -> str:
    """QSS del splash compartido, con el acento del sistema en el icono."""
    return f"""
    QWidget#SharedSplash {{
        background-color: #202630;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 12px;
    }}
    QLabel#SplashIconFallback {{
        color: {accent};
        font-size: 72px;
        font-weight: 300;
        background: transparent;
    }}
    QLabel#SplashTitle {{
        color: #f3f5f8;
        font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif;
        font-size: 17px;
        font-weight: 600;
        background: transparent;
    }}
    """ + splash_titlebar_stylesheet()


SPLASH_STYLESHEET = splash_stylesheet()


def applyget(accent: str, dark: bool = True) -> str:
    """Hoja raíz del ``central``: ensambla los roles ``root`` por control.

    En tema claro el gris por defecto queda ilegible sobre el fondo claro: se
    conmutan los textos al negro y se conserva el resto del QSS.
    """
    text = TEXT if dark else "#000000"
    label = "#cccccc" if dark else "#1f2937"
    page = WINDOW_BG if dark else "#F5F7FB"
    card_surface = SURFACE if dark else "#FFFFFF"
    card_border = BORDER if dark else "#D1D1D6"
    glass_bg = GLASS_BG if dark else "rgba(255, 255, 255, 0.72)"
    glass_border = GLASS_BORDER if dark else "rgba(15, 23, 42, 0.14)"
    glass_border_top = GLASS_BORDER_TOP if dark else "rgba(255, 255, 255, 0.95)"
    muted = TEXT_DIM if dark else label
    group_text = "#f3f5f8" if dark else "#000000"
    stack_text = "#bbb" if dark else "#333333"
    scroll_handle = "rgba(255, 255, 255, 0.24)" if dark else "rgba(0, 0, 0, 0.28)"
    scroll_handle_hover = "rgba(255, 255, 255, 0.38)" if dark else "rgba(0, 0, 0, 0.42)"
    disabled_bg = "#3A3A3C" if dark else "#d8dae0"
    line_hover = "#5A5A5C" if dark else "#b9bcc4"
    _, accent_hover, accent_pressed = accent_states(accent)
    values = {
        "ACCENT": accent,
        "ACCENT_HOVER": accent_hover,
        "ACCENT_PRESSED": accent_pressed,
        "WINDOW_BG": WINDOW_BG,
        "SIDEBAR_BG": SIDEBAR_BG,
        "SURFACE": SURFACE,
        "BORDER": BORDER,
        "CARD_SURFACE": card_surface,
        "CARD_BORDER": card_border,
        "GLASS_BG": glass_bg,
        "GLASS_BORDER": glass_border,
        "GLASS_BORDER_TOP": glass_border_top,
        "AVATAR_RADIUS": AVATAR_RADIUS,
        "AVATAR_FONT_SIZE": AVATAR_FONT_SIZE,
        "PAGE": page,
        "TEXT": text,
        "LABEL": text,
        "MUTED": muted,
        "GROUP_TEXT": group_text,
        "STACK_TEXT": stack_text,
        "SCROLL_HANDLE": scroll_handle,
        "SCROLL_HANDLE_HOVER": scroll_handle_hover,
        "DISABLED_BG": disabled_bg,
        "LINE_HOVER": line_hover,
        "FONT_STACK": FONT_STACK,
        "CARD_RADIUS": CARD_RADIUS,
        "CONTROL_RADIUS": CONTROL_RADIUS,
        "PILL_RADIUS": PILL_RADIUS,
        "BUTTON_PADDING_H": BUTTON_PADDING_H,
        "INPUT_PADDING": INPUT_PADDING,
        "INPUT_MIN_HEIGHT": INPUT_HEIGHT - 2,
        "BUTTON_HEIGHT": BUTTON_HEIGHT,
        "TEXT_DIM": TEXT_DIM,
    }
    parts = [
        qss_loader.qss("qwidget", role="root", **values),
        qss_loader.qss("qcombobox", role="root", **values),
        qss_loader.qss("qwidget", role="landing", **values),
        qss_loader.qss("qframe", role="landing", **values),
        qss_loader.qss("qlabel", role="landing", **values),
        qss_loader.qss("qpushbutton", role="landing", **values),
        qss_loader.qss("qlineedit", role="landing", **values),
        qss_loader.qss("qlabel", role="profile", **values),
        qss_loader.qss("qpushbutton", role="profile", **values),
        qss_loader.qss("qgroupbox", role="root", **values),
        qss_loader.qss("qhboxlayout", role="root", **values),
        qss_loader.qss("qlineedit", role="root", **values),
        qss_loader.qss("qscrollbar", role="root", **values),
        qss_loader.qss("qlabel", role="root", **values),
        qss_loader.qss("qstackedwidget", role="root", **values),
        qss_loader.qss("qpushbutton", role="root", **values),
        slider_qss(accent),
        qss_loader.qss("qprogressbar", role="root", **values),
    ]
    return "\n".join(parts)
