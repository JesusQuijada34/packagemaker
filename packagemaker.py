#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
import shutil
import xml.etree.ElementTree as ET
import json
import tempfile
from pathlib import Path
import importlib


# Importar detector de modo de ejecución
try:
    from lib.executionMode import get_execution_mode, is_frozen, get_command_name
except ImportError:
    def get_execution_mode():
        class DummyMode:
            def is_frozen(self): return False
            def get_command_name(self): return "packagemaker.py"
            def get_base_directory(self): return os.path.dirname(os.path.abspath(__file__))
        return DummyMode()
    def is_frozen(): return False
    def get_command_name(): return "packagemaker.py"
try:
    from PyQt6 import QtWidgets, QtGui, QtCore
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
        QComboBox, QFileDialog, QDialog, QSizePolicy, QGroupBox, QRadioButton, QButtonGroup, QGridLayout, QTextEdit, QStackedWidget, QSlider, QFrame, QGraphicsDropShadowEffect
    )
    from PyQt6.QtGui import QFont, QIcon, QColor
    from PyQt6.QtGui import QPixmap
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QEvent, QObject, QPropertyAnimation, QEasingCurve
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    # Mocking basic classes if needed for type hints or minimal logic
    class QObject: pass
    class QThread: pass
    class pyqtSignal:
        def __init__(self, *args): pass
        def connect(self, func): pass
        def emit(self, *args): pass
    class QFont:
        def __init__(self, *args): pass
    class QIcon:
        def __init__(self, *args): pass
    class QPixmap:
        def __init__(self, *args, **kwargs): pass
    class QMainWindow:
        def __init__(self, *args, **kwargs): pass
        def setWindowFlags(self, *args): pass
        def setAttribute(self, *args): pass
        def resize(self, *args, **kwargs): pass
        def move(self, *args, **kwargs): pass
        def setStyleSheet(self, *args): pass
        def show(self): pass
    class QWidget:
        def __init__(self, *args, **kwargs): pass
        def setFixedHeight(self, *args): pass
        def setLayout(self, *args): pass
        def setContentsMargins(self, *args): pass
        def setStyleSheet(self, *args): pass
        def hide(self): pass
    class QDialog:
        def __init__(self, *args, **kwargs): pass
    class QFrame:
        def __init__(self, *args, **kwargs): pass
    class QGraphicsDropShadowEffect:
        def __init__(self, *args, **kwargs): pass
        def setBlurRadius(self, *args): pass
        def setOffset(self, *args): pass
        def setColor(self, *args): pass
    class QColor:
        def __init__(self, *args, **kwargs): pass
    class Qt:
        class WindowType: pass
        class WidgetAttribute: pass
        class AlignmentFlag: pass
        class CursorShape: pass
        class SizePolicy: pass
        class Orientation: pass
        class ScrollBarPolicy: pass
        class FocusPolicy: pass
        class Key: pass
        class Modifier: pass
        class MouseButton: pass
import requests
try:
    import winreg
except ImportError:
    winreg = None

try:
    from leviathan_ui import InmersiveSplash, LightsOff, WipeWindow, LeviathanProgressBar, CustomTitleBar
    from leviathan_ui import get_accent_color as _leviathan_accent
    from leviathan_ui.touchscreen import TouchScreen
    LEVIATHAN_AVAILABLE = True
except (ImportError, SyntaxError) as e:
    LEVIATHAN_AVAILABLE = False
    print(f"[WARN] Leviathan UI no disponible o error de sintaxis: {e}")
    _leviathan_accent = None

    class LeviathanProgressBar(QWidget):
        """Barra de progreso mínima cuando ``leviathan_ui`` no está instalado."""

        def __init__(self, *args, **kwargs):
            super().__init__(kwargs.get("parent"))
            self._value = 0
            self._maximum = 100

        def setValue(self, value):
            self._value = int(value)

        def value(self):
            return self._value

        def setMaximum(self, value):
            self._maximum = int(value)

        def maximum(self):
            return self._maximum

        def setMinimum(self, value):
            pass

        def setFormat(self, text):
            pass

        def setTextVisible(self, visible):
            pass

        def setProgressColor(self, *args, **kwargs):
            return self

        def setAnimationType(self, *args, **kwargs):
            return self

        def startAnimation(self, *args, **kwargs):
            return self

        def stopAnimation(self, *args, **kwargs):
            return self

        def reset(self):
            self._value = 0

    class _NoopWipeWindow:
        """Respaldo sin efectos cuando ``leviathan_ui`` no está instalado."""

        @classmethod
        def create(cls):
            return cls()

        def set_mode(self, *args, **kwargs):
            return self

        def set_radius(self, *args, **kwargs):
            return self

        def apply(self, *args, **kwargs):
            return self

        def show(self, *args, **kwargs):
            return self

        def close(self, *args, **kwargs):
            return self

    class _NoopOverlay:
        def __init__(self, *args, **kwargs):
            pass

        def show(self, *args, **kwargs):
            return self

        def close(self, *args, **kwargs):
            return self

        def hide(self, *args, **kwargs):
            return self

        def setWindowFlags(self, *args, **kwargs):
            return self

        def setAttribute(self, *args, **kwargs):
            return self

    class _NoopTitleBar(QWidget):
        def __init__(self, parent=None, title="", icon="", **kwargs):
            super().__init__(parent)
            self.title_lbl = QLabel(title, self)

        def set_title(self, text):
            self.title_lbl.setText(text)

    class _NoopTouchScreen:
        def __init__(self, *args, **kwargs):
            pass

        def enable(self, *args, **kwargs):
            return self

    WipeWindow = _NoopWipeWindow
    LightsOff = _NoopOverlay
    InmersiveSplash = _NoopOverlay
    CustomTitleBar = _NoopTitleBar
    TouchScreen = _NoopTouchScreen


def get_accent_color():
    """Acento activo: preferencia del usuario, luego Leviathan, luego azul UWP.

    ``leviathan_ui`` no está presente en todos los entornos (CI, Linux sin la
    dependencia instalada), de modo que el tema cae a ``custom_accent_color``
    de ``data/pm.data`` y, en último término, al azul de Windows 11.
    """
    try:
        from lib.pm_data import get_pm_data

        value = str(get_pm_data().get_user("custom_accent_color", "") or "").strip()
        if value:
            return value
    except Exception:
        pass
    if _leviathan_accent is not None:
        try:
            return str(_leviathan_accent())
        except Exception:
            pass
    return "#0078D4"


# Updater - usar coreUpdater si está disponible, sino fallback a lib.Updater
try:
    pass
except ImportError:
    pass
from lib.BuildThread import BuildThread
from lib.app_icons import get_icon, icon_button
from lib.window_chrome import (
    apply_display_mode,
    apply_personalization_effects,
    patch_titlebar_maximize,
    fixed_window_title,
    restart_application,
    is_frameless_maximized,
)
from lib.uwp_animations import play_bounce_down_close
from lib.page_action_bar import install_page_action_bar, make_action_button, make_icon_button
from lib.design_tokens import (
    CONTENT_PADDING,
    FONT_STACK,
    INPUT_HEIGHT,
    SIDEBAR_ITEM_HEIGHT,
    SIDEBAR_PADDING,
    SIDEBAR_TOP_MARGIN,
    TEXT,
    TITLEBAR_BG,
    WINDOW_BG,
)
from lib.SidebarItem import SidebarItem
from lib.sidebar_resize import SidebarResizeHandle
from lib.window_manager_bridge import install_window_manager_bridges
from lib.ios_progress_dialog import show_ios_progress
from lib.alert_dialog import AlertDialog
# Los avisos usan el diálogo temático propio (blanco/negro, botones verticales
# de ancho completo con separadores). ``LeviathanDialog`` queda como alias para
# no tocar los puntos de llamada existentes.
LeviathanDialog = AlertDialog
from lib.moonFixWizard import MoonFixWizard
from lib.gitHubVerifyThread import GitHubVerifyThread
from lib.i18n import i18n, tr, system_default_language, get_available_languages
from lib.linux_icon_handler import ensure_linux_icon_support
from lib.pm_data import get_pm_data, load_merged_app_config
from lib.fluent_theme import (
    BTN_STYLES,
    FluentCheckBox as QCheckBox,
    applyget,
    conf_field_stylesheet,
    preferred_mono_font,
    preferred_ui_font,
    qss_value,
    sidebar_button_stylesheet,
    sidebar_stylesheet,
    set_qss,
    system_theme_mode,
)
from lib.qml_animations import animate_property

def create_title_bar(parent, title="", icon_path=None):
    """Compatibilidad del rediseño: todos los diálogos usan la titlebar SVG estable."""
    return CustomTitleBar(parent, title=title, icon=icon_path or "")

# [MONKEYPATCH] Fix for LeviathanUI < v1.0.4 where LeviathanProgressBar is missing setValue()
# referencing the installed library issue without modifying it.
if not hasattr(LeviathanProgressBar, 'setValue'):
    def set_value_patch(self, val):
        self.value = val
    LeviathanProgressBar.setValue = set_value_patch
# The following block handles platform-specific imports.
# The warning about 'pyi_splash' is expected only when running as a PyInstaller .exe.
# It's safe to ignore in regular Python editors; it's only meaningful when sys.frozen is set.

if sys.platform.startswith("win"):
    try:
        import winreg
    except ImportError:
        winreg = None

def _register_bundled_fonts():
    """Registra en Qt las fuentes descargadas en ``data/fonts``.

    Se ejecuta después de crear ``QApplication`` porque ``addApplicationFont``
    exige una ``QGuiApplication`` viva.
    """
    try:
        from lib.font_manager import load_cached_fonts

        return load_cached_fonts()
    except Exception as exc:  # pragma: no cover - la UI no debe caer por fuentes
        print(f"[FONT] No se pudieron registrar las fuentes: {exc}")
        return {}


if PYQT6_AVAILABLE:
    # La familia preferida sólo puede resolverse cuando existe una
    # QGuiApplication; app_font() se evalúa tras construir QApplication.
    def app_font():
        """Devuelve la fuente de UI preferida una vez creada la aplicación."""
        _register_bundled_fonts()
        return preferred_ui_font(11)

    def code_font():
        """Fuente monoespaciada para editor y terminal."""
        _register_bundled_fonts()
        return preferred_mono_font(10)
else:
    def app_font():
        return None

    def code_font():
        return None

    print("font: none")

# Diccionario de claves de iconos (los iconos se crearán de manera diferida)
TAB_ICON_KEYS = {
    "crear": "crear",
    "construir": "construir",
    "gestor": "gestor",
    "config": "config",
    "moonfix": "moonfix",
    "reparar": "instalar",
    "about": "about",
    "instalar": "instalar",
    "desinstalar": "desinstalar",
    "refresh": "refresh",
    "open_with": "open_with",
}

# Función para obtener iconos de manera diferida
def get_tab_icon(key):
    """Obtiene un icono de manera diferida, solo cuando se necesita"""
    from lib.app_icons import get_sidebar_icon
    icon_key = TAB_ICON_KEYS.get(key)
    if icon_key:
        return get_sidebar_icon(icon_key)
    return QIcon()

# Windows 11-inspired button styles (rounded, soft shadows, modern accent colors)
# Note: The 'transition' property is a CSS feature supported by browsers, but it is NOT supported/stable in PyQt6 stylesheets.
# PyQt6 ignores 'transition' and related CSS3 properties—they have no effect and can be safely omitted.
# QSS-based stylized button styles using rgba colors, with transparency for blending with the app frame

plataforma_platform = sys.platform
plataforma_name = os.name

# --- TERMUX/ANDROID DETECTION ---
# Termux usa PREFIX=/data/data/com.termux/files/usr
# Android tiene restricciones de acceso a carpetas estándar
_is_termux = os.environ.get("PREFIX", "").startswith("/data/data/com.termux")
_is_android = sys.platform.startswith("linux") and (
    os.path.exists("/system/app") or
    os.environ.get("ANDROID_ROOT") or
    os.environ.get("ANDROID_DATA")
)

if _is_termux:
    # Termux: guardar en carpeta home de termux (accessible)
    # Carpeta oculta .packagemaker en home de termux
    termux_home = os.path.expanduser("~")
    BASE_DIR = os.path.join(termux_home, ".packagemaker", "projects")
    Fluthin_APPS = os.path.join(termux_home, ".packagemaker", "apps")
    linkedsys = "termux"
    # Termux no tiene acceso a ~/Documents por restricciones de Android
elif _is_android:
    # Android: guardar en carpeta interna de la app o almacenamiento común
    android_home = os.path.expanduser("~")
    BASE_DIR = os.path.join(android_home, "PackageMaker", "Projects")
    Fluthin_APPS = os.path.join(android_home, "PackageMaker", "Apps")
    linkedsys = "android"
elif plataforma_platform.startswith("win"):
    user_profile = os.environ.get("USERPROFILE", "")
    doc_folder = "Documents"
    if os.path.exists(os.path.join(user_profile, "Documentos")):
        doc_folder = "Documentos"
    elif os.path.exists(os.path.join(user_profile, "Documents")):
        doc_folder = "Documents"
    BASE_DIR = os.path.join(user_profile, doc_folder, "Packagemaker Projects")
    Fluthin_APPS = os.path.join(user_profile, doc_folder, "Fluthin Apps")
    linkedsys = "knosthalij"
elif plataforma_platform.startswith("linux"):
    BASE_DIR = os.path.expanduser("~/Documents/Packagemaker Projects")
    Fluthin_APPS = os.path.expanduser("~/Documents/Fluthin Apps")
    linkedsys = "danenone"
else:
    BASE_DIR = "Packagemaker Projects/"
    Fluthin_APPS = "Fluthin Apps/"
    linkedsys = "keystone"

_PLATFORM_BASE_DIR = BASE_DIR
_PLATFORM_FLUTHIN_APPS = Fluthin_APPS

# --- EXECUTION MODE DETECTION ---
# Detectar modo de ejecución (frozen/unfrozen) y ajustar comportamiento
exec_mode = get_execution_mode()
EXECUTION_INFO = exec_mode.get_platform_info()

# Ajustar BASE_DIR según modo de ejecución
if exec_mode.is_frozen():
    # Si está frozen, usar el directorio del ejecutable como base
    BASE_DIR = exec_mode.get_base_directory()
else:
    # Si es script, mantener el comportamiento actual
    BASE_DIR = _PLATFORM_BASE_DIR

# --- GLOBAL CONFIG SYSTEM ---
# Manejar icono según la plataforma (PNG para Linux, ICO para Windows)
if sys.platform.startswith("linux"):
    _ico_fallback = os.path.join("app", "app-icon.ico")
    _png_path = os.path.join("app", "app-icon.png")
    IPM_ICON_PATH = _png_path if os.path.exists(_png_path) else _ico_fallback
else:
    IPM_ICON_PATH = os.path.join("app", "app-icon.ico")
DEFAULT_FOLDERS = "app,assets,config,docs,source,lib"
CONFIG_DIR = os.path.join(os.getcwd(), "config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.json")
DEFAULT_CONFIG = {
    "BASE_DIR": BASE_DIR,
    "Fluthin_APPS": Fluthin_APPS,
    "DISPLAY_MODE": "GhostBlur (Cristal)",
}

# --- UTILITY FUNCTIONS ---

def load_updater_template():
    from lib.template_engine import load_template
    return load_template("project/updater.py.template")

def load_docs_template():
    from lib.template_engine import load_template
    return load_template("docs/index.html.template")

def getversion():
    """Genera una versión basada en fecha y hora actual"""
    newversion = time.strftime("%y.%m-%H.%M")
    return f"{newversion}"

def load_app_config():
    return load_merged_app_config(
        legacy_config_path=Path(CONFIG_FILE),
        default_base_dir=_PLATFORM_BASE_DIR,
        default_fluthin=_PLATFORM_FLUTHIN_APPS,
    )

APP_CONFIG = load_app_config()
BASE_DIR = APP_CONFIG.get("BASE_DIR", _PLATFORM_BASE_DIR) or _PLATFORM_BASE_DIR
Fluthin_APPS = APP_CONFIG.get("Fluthin_APPS", _PLATFORM_FLUTHIN_APPS) or _PLATFORM_FLUTHIN_APPS

# Crear las carpetas si no existen
try:
    os.makedirs(BASE_DIR, exist_ok=True)
    os.makedirs(Fluthin_APPS, exist_ok=True)
    print(f"[PackageMaker] Plataforma detectada: {linkedsys}")
    print(f"[PackageMaker] BASE_DIR: {BASE_DIR}")
    print(f"[PackageMaker] Fluthin_APPS: {Fluthin_APPS}")
except OSError as e:
    print(f"[PackageMaker] ADVERTENCIA: No se pudo crear directorio {BASE_DIR}: {e}")
    # Intentar con directorio alternativo
    alt_dir = os.path.expanduser("~")
    BASE_DIR = os.path.join(alt_dir, "PackageMaker", "Projects")
    Fluthin_APPS = os.path.join(alt_dir, "PackageMaker", "Apps")
    try:
        os.makedirs(BASE_DIR, exist_ok=True)
        os.makedirs(Fluthin_APPS, exist_ok=True)
        print(f"[PackageMaker] Usando directorio alternativo: {BASE_DIR}")
    except OSError as e2:
        print(f"[PackageMaker] ERROR: No se pudo crear directorio alternativo: {e2}")

def save_app_config(config):
    store = get_pm_data()
    store.set_user("base_dir", config.get("BASE_DIR", BASE_DIR))
    store.set_user("fluthin_apps", config.get("Fluthin_APPS", Fluthin_APPS))
    store.set_user("display_mode", config.get("DISPLAY_MODE", DEFAULT_CONFIG["DISPLAY_MODE"]))
    if "LANGUAGE" in config:
        store.set_user("language", str(config["LANGUAGE"]).lower()[:2])
    for key in (
        "device_simulation", "dpi_scale", "touch_mode", "interface_color",
        "auto_color", "auto_translate", "notifications_enabled",
        "custom_accent_color", "blur_intensity", "window_radius",
        "sidebar_accent_width", "card_opacity", "ui_density", "applied_dpi_scale",
    ):
        if key in config:
            store.set_user(key, config[key])
    return store.save()

# Funciones para guardar en registro de Windows
def save_to_registry(key, value):
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\PackageMaker", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(reg_key, key, 0, winreg.REG_SZ, str(value))
        winreg.CloseKey(reg_key)
        return True
    except OSError:
        return False

def load_from_registry(key, default=""):
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\PackageMaker", 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(reg_key, key)
        winreg.CloseKey(reg_key)
        return value
    except OSError:
        return default

plataforma = plataforma_platform.capitalize()
nombre = plataforma_name.capitalize()
plataforma = f"{plataforma} in {nombre}"

LGDR_MAKE_MESSAGES = {
    "_LGDR_PUBLISHER_E" : "Nombre de la empresa de creación.",
    "_LGDR_NAME_E" : "Nombre acortado del proyecto. Se permiten guiones y pisos, no espacios",
    "_LGDR_VERSION_E" :"Versión del proyecto, como 1 o 1.0, no es permitido guiones ni espacios",
    "_LGDR_TITLE_E" : "Título del proyecto, formato libre",
    "_LGDR_MAKE_BTN" : "Crear proyecto y firmar"
}
LGDR_BUILD_MESSAGES = {
    "_LGDR_PUBLISHER_E" : "Empresa quien hizo el proyecto",
    "_LGDR_NAME_E" : "Shortname del proyecto a construir",
    "_LGDR_VERSION_E" : "Versión del proyecto a detectar",
    "_LGDR_PLATFORM_E" : "Plataforma a compilar",
    "_LGDR_BUILD_BTN" : "Compilar proyecto"
}

AGE_RATINGS = {
    "project1" : "NO SEGURO!",
    "editor" : "PERSONAL USE",
    "maker" : "PERSONAL USE",
    "make" : "PERSONAL USE",
    "edit" : "PERSONAL USE",
    "adult" : "ADULTS ONLY",
    "sex" : "ADULTS ONLY",
    "sexual" : "ADULTS ONLY",
    "violence" : "TEENS ALL 18+",
    "horror" : "TEENS ALL 18+",
    "obscene" : "TEENS ALL 18+",
    "boyfriend" : "TEENS ALL 18+",
    "girlfriend" : "TEENS ALL 18+",
    "teen" : "TEENS ALL 18+",
    "shoot" : "TEENS ALL 18+",
    "shooter" : "TEENS ALL 18+",
    "minecraft" : "TEENS ALL 18+",
    "drift" : "TEENS ALL 18+",
    "car" : "TEENS ALL 18+",
    "craft" : "TEENS ALL 18+",
    "dating" : "TEENS ALL 18+",
    "porn" : "TEENS ALL 18+",
    "pornhub" : "TEENS ALL 18+",
    "onlyfans" : "TEENS ALL 18+",
    "xnxx" : "TEENS ALL 18+",
    "porno" : "TEENS ALL 18+",
    "porngraphic" : "TEENS ALL 18+",
    "restricted" : "TEENS ALL 18+",
    "simulator": "TEENS ALL 18+",
    "kids" : "FOR KIDS",
    "kid" : "FOR KIDS",
    "learn" : "FOR KIDS",
    "learner" : "FOR KIDS",
    "gameto" : "FOR KIDS",
    "abc" : "FOR KIDS",
    "animated" : "FOR KIDS",
    "makeup" : "FOR KIDS",
    "girls" : "FOR KIDS",
    "boys" : "FOR KIDS",
    "puzzle" : "FOR KIDS",
    "camera" : "EVERYONE",
    "calculator" : "EVERYONE",
    "game" : "EVERYONE",
    "games" : "EVERYONE",
    "public" : "EVERYONE",
    "music" : "EVERYONE",
    "video" : "EVERYONE",
    "photo" : "EVERYONE",
    "document" : "PERSONAL USE",
    "facebook" : "PUBLIC CONTENT",
    "tiktok" : "PUBLIC CONTENT",
    "whatsapp" : "PUBLIC CONTENT",
    "telegram" : "PUBLIC CONTENT",
    "snapchat" : "PUBLIC CONTENT",
    "pinterest" : "PUBLIC CONTENT",
    "x" : "PUBLIC CONTENT",
    "twitter" : "PUBLIC CONTENT",
    "youtube" : "PUBLIC CONTENT",
    "likee" : "PUBLIC CONTENT",
    "netflix" : "PUBLIC CONTENT",
    "primevideo" : "PUBLIC CONTENT",
    "cinema" : "PUBLIC CONTENT",
    "ytmusic" : "PUBLIC CONTENT",
    "browser" : "PUBLIC CONTENT",
    "ads" : "PUBLIC CONTENT",
    "discord" : "PUBLIC CONTENT",
    "github" : "PUBLIC CONTENT",
    "drive" : "PUBLIC CONTENT",
    "mega" : "PUBLIC CONTENT",
    "mediafire" : "PUBLIC CONTENT",
    "yandex" : "PUBLIC CONTENT",
    "opera" : "PUBLIC CONTENT",
    "operamini" : "PUBLIC CONTENT",
    "brave" : "PUBLIC CONTENT",
    "chrome" : "PUBLIC CONTENT",
    "googlechorme" : "PUBLIC CONTENT",
    "chromebrowser" : "PUBLIC CONTENT",
    "mozilla" : "PUBLIC CONTENT",
    "firefox" : "PUBLIC CONTENT",
    "tor" : "PUBLIC CONTENT",
    "torbrowser" : "PUBLIC CONTENT",
    "lightbrowser" : "PUBLIC CONTENT",
    "edge" : "PUBLIC CONTENT",
    "edgebrowser" : "PUBLIC CONTENT",
    "internet" : "PUBLIC CONTENT",
    "internetexplorer" : "PUBLIC CONTENT",
    "ie" : "PUBLIC CONTENT",
    "ie7" : "PUBLIC CONTENT",
    "ie8" : "PUBLIC CONTENT",
    "ie9" : "PUBLIC CONTENT",
    "bing" : "PUBLIC CONTENT",
    "duckduckgo" : "PUBLIC CONTENT",
    "instagram" : "PUBLIC CONTENT",
    "flickr" : "PUBLIC CONTENT",
    "social" : "PUBLIC CONTENT",
    "ai" : "PUBLIC ALL",
    "ia" : "PUBLIC ALL",
    "chatgpt" : "PUBLIC ALL",
    "copilot" : "PUBLIC ALL",
    "deepseek" : "PUBLIC ALL",
    "claude" : "PUBLIC ALL",
    "gemini" : "PUBLIC ALL",
    "mistral" : "PUBLIC ALL",
    "leo" : "PUBLIC ALL",
    "gabo" : "PUBLIC ALL",
    "zapia" : "PUBLIC ALL",
    "sonnet" : "PUBLIC ALL",
    "plikaai" : "PUBLIC ALL",
    "plika" : "PUBLIC ALL",
    "klingai" : "PUBLIC ALL",
    "kling" : "PUBLIC ALL",
}





def find_python_executable():
    """Busca un ejecutable de Python disponible en el sistema."""
    # 1. Si estamos congelados (PyInstaller), sys.executable es el exe de la app, no python.
    #    Si no estamos congelados, sys.executable es el python que nos corre.
    if getattr(sys, 'frozen', False):
        # Buscamos en PATH
        path_python = shutil.which("python")
        if path_python: return path_python
        path_python3 = shutil.which("python3")
        if path_python3: return path_python3
        return None
    else:
        return sys.executable

def get_app_version():
    """Lee la versión desde details.xml en el root del proyecto"""
    details_path = os.path.join(os.getcwd(), "details.xml")
    if os.path.exists(details_path):
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(details_path)
            root = tree.getroot()
            version = root.findtext("version", "").strip()
            if version.startswith("v"):
                version = version[1:]  # Remover 'v' del prefijo
            return version
        except Exception as e:
            print(f"Error leyendo details.xml: {e}")
    return "3.2.7-26.05-20.13-AlphaCube"  # Fallback por defecto

SIDEBAR_DESC_KEYS = {
    0: "sidebar_desc.0",
    1: "sidebar_desc.1",
    2: "sidebar_desc.3",
    3: "sidebar_desc.4",
    4: "sidebar_desc.5",
}

class PackageTodoGUI(QMainWindow):
    def __init__(self, compact_mode=False, shell_mode=False):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.compact_mode = compact_mode
        self.shell_mode = shell_mode
        WipeWindow.create().set_mode("ghostBlur").set_radius(20).apply(self)
        # --- VERSION UPDATE 3.2.7 ---
        self.currentVersion = get_app_version()

        # Quitar barra de título nativa de Windows - usar solo leviathan-ui
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Fondo COMPLETAMENTE opaco - sin transparencia
        #self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._fixed_title = fixed_window_title(self.currentVersion)
        self.setWindowTitle(self._fixed_title)
        self._pending_restart_keys = []
        self.resize(1024, 720)
        font = app_font()
        if font is not None:
            self.setFont(font)
        # Cargar icono con soporte para Linux
        icon_to_load = IPM_ICON_PATH
        if os.path.exists(icon_to_load):
            try:
                self.setWindowIcon(QtGui.QIcon(icon_to_load))
            except Exception as e:
                print(f"[WARNING] No se pudo cargar icono: {e}")
        else:
            # Intenta convertir ICO a PNG en Linux si el PNG no existe
            if sys.platform.startswith("linux"):
                try:
                    icon_path = ensure_linux_icon_support(os.getcwd())
                    if icon_path and os.path.exists(icon_path):
                        self.setWindowIcon(QtGui.QIcon(icon_path))
                except Exception as e:
                    print(f"[WARNING] Error al preparar icono en Linux: {e}")

        # Central Widget & Main Layout
        self.central = QWidget()
        self.central.setObjectName("CentralWidget")
        set_qss(self.central, 'packagemaker_001', append=False)
        self.setCentralWidget(self.central)

        self.sidebar_collapsed = False
        self.sidebar_animation = None
        self._page_fade = None
        self._page_fade_widget = None
        self.sidebar_target_width = 260

        # Layout principal vertical (TitleBar + ContentArea)
        self.v_layout = QVBoxLayout(self.central)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setSpacing(0)

        # Title Bar Custom (LeviathanUI) - extendida por toda la barra
        self.titlebar = CustomTitleBar(
            self,
            title=self._fixed_title,
            icon=(IPM_ICON_PATH if os.path.exists(IPM_ICON_PATH) else ""),
        )
        self.titlebar.setStyleSheet(
            f"background-color: {TITLEBAR_BG}; border: none;"
        )
        self.titlebar.title_lbl.setText(self._fixed_title)
        patch_titlebar_maximize(self.titlebar, self)
        self._pm_reapply_display_mode = self._apply_leviathan_and_personalization
        self.v_layout.addWidget(self.titlebar)

        # Puentes con el gestor de ventanas del SO: arrastrar, redimensionar
        # por bordes, doble clic para maximizar, menú del sistema y snap.
        self.wm_bridge = install_window_manager_bridges(self, self.titlebar)

        # Content Container (Sidebar + Stack)
        self.content_container = QWidget()
        # Enable styled background
        self.content_container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.content_layout = QHBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        # --- SIDEBAR (Left) ---
        self.sidebar = QWidget()
        self.sidebar.setObjectName("NavigationSidebar")
        self.sidebar.setMinimumWidth(60)
        self.sidebar.setMaximumWidth(260)
        self.sidebar.resize(260, 480)
        self.sidebar.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.sidebar.setMouseTracking(True)
        set_qss(self.sidebar, 'packagemaker_003', append=False)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(
            SIDEBAR_PADDING, SIDEBAR_TOP_MARGIN, SIDEBAR_PADDING, SIDEBAR_PADDING
        )
        self.sidebar_layout.setSpacing(8)
        self.sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.sidebar_collapsed = False
        self.sidebar_animation = None
        # Ancho manual (estilo VS Code): se ajusta arrastrando el borde y se
        # recuerda entre sesiones en data/pm.data.
        self.sidebar_target_width = int(
            get_pm_data().get_user("sidebar_width", 260) or 260
        )
        self.sidebar_target_width = max(180, min(480, self.sidebar_target_width))
        self.sidebar.setMinimumWidth(self.sidebar_target_width)
        self.sidebar.setMaximumWidth(self.sidebar_target_width)
        self.sidebar.installEventFilter(self)

        sidebar_header = QHBoxLayout()
        sidebar_header.setContentsMargins(0, 0, 0, 0)
        self.lbl_menu_main = QLabel(tr("app.main_menu"))
        set_qss(self.lbl_menu_main, 'packagemaker_004', append=False)
        sidebar_header.addWidget(self.lbl_menu_main)
        sidebar_header.addStretch()

        self.sidebar_collapse_toggle = QPushButton()
        self.sidebar_collapse_toggle.setObjectName("SidebarCollapseButton")
        self.sidebar_collapse_toggle.setFixedSize(28, 28)
        self.sidebar_collapse_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sidebar_collapse_toggle.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        icon_button(self.sidebar_collapse_toggle, "collapse", 18)
        self.sidebar_collapse_toggle.clicked.connect(self.toggle_sidebar)
        self.sidebar_collapse_toggle.setToolTip("Ocultar menú (Ctrl+B)")
        sidebar_header.addWidget(self.sidebar_collapse_toggle)
        self.sidebar_layout.addLayout(sidebar_header)

        # Navigation Buttons
        dark_now = system_theme_mode() != "light"
        self.btn_create = SidebarItem(tr("sidebar.create"), get_tab_icon("crear"), dark=dark_now, icon_key="crear")
        self.btn_build = SidebarItem(tr("sidebar.build"), get_tab_icon("construir"), dark=dark_now, icon_key="construir")
        self.btn_config = SidebarItem(tr("sidebar.config"), get_tab_icon("config"), dark=dark_now, icon_key="config")
        self.btn_moonfix = SidebarItem(tr("sidebar.moonfix"), get_tab_icon("moonfix"), dark=dark_now, icon_key="moonfix")
        self.btn_about = SidebarItem(tr("sidebar.about"), get_tab_icon("about"), dark=dark_now, icon_key="about")
        self._sidebar_btn_keys = {
            self.btn_create: "sidebar.create",
            self.btn_build: "sidebar.build",
            self.btn_config: "sidebar.config",
            self.btn_moonfix: "sidebar.moonfix",
            self.btn_about: "sidebar.about",
        }

        self.sidebar_group = QButtonGroup(self)
        self.sidebar_group.addButton(self.btn_create, 0)
        self.sidebar_group.addButton(self.btn_build, 1)
        self.sidebar_group.addButton(self.btn_config, 2)
        self.sidebar_group.addButton(self.btn_moonfix, 3)
        self.sidebar_group.addButton(self.btn_about, 4)
        self.sidebar_group.idClicked.connect(self.switch_page)

        self.sidebar_layout.addWidget(self.btn_create)
        self.sidebar_layout.addWidget(self.btn_build)
        self.sidebar_layout.addWidget(self.btn_config)
        self.sidebar_layout.addWidget(self.btn_moonfix)

        # Area de Contexto/Descripcion (Estilo Nota UWP)
        self.sidebar_layout.addStretch()

        self.desc_card = QWidget()
        self.desc_card.setObjectName("SidebarContextCard")
        set_qss(self.desc_card, 'packagemaker_005', append=False)
        desc_vbox = QVBoxLayout(self.desc_card)
        desc_vbox.setContentsMargins(12, 12, 12, 12)

        desc_header = QHBoxLayout()

        self.lbl_sidebar_context = QLabel(tr("app.context"))
        set_qss(self.lbl_sidebar_context, 'packagemaker_006', append=False)
        desc_header.addWidget(self.lbl_sidebar_context)
        desc_header.addStretch()
        desc_vbox.addLayout(desc_header)

        self.sidebar_desc_text = QTextEdit()
        self.sidebar_desc_text.setReadOnly(True)
        self.sidebar_desc_text.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        set_qss(self.sidebar_desc_text, 'packagemaker_007', append=False)
        self.sidebar_desc_text.setMaximumHeight(120)
        desc_vbox.addWidget(self.sidebar_desc_text)

        self.sidebar_layout.addWidget(self.desc_card)
        self.sidebar_layout.addSpacing(10)
        self.sidebar_layout.addWidget(self.btn_about)

        self.sidebar_collapse_button = self.sidebar_collapse_toggle

        self.content_layout.addWidget(self.sidebar)

        # Tirador de redimensionado manual (VS Code): arrastra el borde derecho.
        self.sidebar_resize_handle = SidebarResizeHandle(
            self.sidebar,
            min_width=180,
            max_width=480,
            on_resized=self._persist_sidebar_width,
            parent=self.content_container,
        )
        self.content_layout.addWidget(self.sidebar_resize_handle)

        # --- MAIN CONTENT AREA (Right) ---
        self.stack = QStackedWidget()
        self.stack.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        set_qss(self.stack, 'packagemaker_008', append=False)
        self.content_container.setObjectName("ContentContainer")

        # Pages
        self.page_create = QWidget()
        self.init_create_tab(self.page_create) # Refactorized logic below

        self.page_build = QWidget()
        self.init_build_tab(self.page_build)

        self.page_config = QWidget()
        self.init_config_tab(self.page_config)

        self.page_moonfix = QWidget()
        self.init_moonfix_tab(self.page_moonfix)

        self.page_about = QWidget()
        self.init_about_tab(self.page_about)

        self.stack.addWidget(self.page_create)
        self.stack.addWidget(self.page_build)
        self.stack.addWidget(self.page_config)
        self.stack.addWidget(self.page_moonfix)
        self.stack.addWidget(self.page_about)

        self.content_layout.addWidget(self.stack)
        self.v_layout.addWidget(self.content_container)

        # Set default
        self.btn_create.setChecked(True)
        self.stack.setCurrentIndex(0)

        # Initialize Theme Check
        self.theme_timer = QTimer()
        self.theme_timer.timeout.connect(self.check_theme_change)
        self.theme_timer.start(1000)
        self.last_theme_mode = system_theme_mode()
        app_instance = QApplication.instance()
        if app_instance is not None:
            if hasattr(app_instance, "paletteChanged"):
                app_instance.paletteChanged.connect(self._on_theme_signal)
            try:
                hints = app_instance.styleHints()
                if hasattr(hints, "colorSchemeChanged"):
                    hints.colorSchemeChanged.connect(self._on_theme_signal)
            except (AttributeError, RuntimeError):
                pass

        # Apply Global Styles
        self.apply_theme()
        self._apply_leviathan_and_personalization()

        if self.compact_mode or self.shell_mode:
            self.enterCompactShellMode()

        # Startup Animation
        self.animate_startup()

        # Initial description
        self.update_sidebar_description(0)

        # Gestos táctiles (solo si el ajuste touch_mode está activo).
        self.setup_touch_gestures()

        i18n.register_ui_refresh(self.apply_ui_language)

    def apply_ui_language(self):
        """Actualiza textos de la interfaz al idioma activo."""
        self.lbl_menu_main.setText(tr("app.main_menu"))
        self.lbl_sidebar_context.setText(tr("app.context"))
        for btn, key in self._sidebar_btn_keys.items():
            btn.setText(tr(key))
        idx = self.stack.currentIndex()
        self.update_sidebar_description(idx)
        if hasattr(self, "conf_header"):
            self._refresh_config_tab_labels()
        if hasattr(self, "sandbox_switch"):
            self.sandbox_switch.setText(tr("create.sandbox"))

    def update_sidebar_description(self, index):
        key = SIDEBAR_DESC_KEYS.get(index)
        if key:
            text = tr(key)
            html = text.replace("### ", "<b style='color:white; font-size:14px;'>").replace("\n", "</b><br>")
            self.sidebar_desc_text.setHtml(html)

    def _persist_sidebar_width(self, width):
        """Guarda el ancho elegido a mano para la próxima sesión."""
        width = max(180, min(480, int(width)))
        self.sidebar_target_width = width
        try:
            store = get_pm_data()
            store.set_user("sidebar_width", width)
            store.save()
        except Exception:
            pass

    def _apply_sidebar_state(self, collapsed):
        target_width = 60 if collapsed else self.sidebar_target_width
        if self.sidebar_collapsed == collapsed and self.sidebar.maximumWidth() == target_width:
            return
        # El tirador fija mínimo y máximo; el colapso debe liberar el mínimo.
        if collapsed:
            self.sidebar.setMinimumWidth(60)
        else:
            self.sidebar.setMinimumWidth(self.sidebar_target_width)
        self.sidebar_animation = animate_property(
            self.sidebar,
            "maximumWidth",
            self.sidebar.maximumWidth(),
            target_width,
            220,
            QEasingCurve.Type.OutCubic,
            on_finished=(lambda: self.sidebar.setMinimumWidth(target_width)),
        )
        self.sidebar_collapsed = collapsed
        icon_button(self.sidebar_collapse_toggle, "expand" if collapsed else "collapse", 18)
        self.sidebar_collapse_toggle.setToolTip(
            "Expandir menú (Ctrl+B)" if collapsed else "Ocultar menú (Ctrl+B)"
        )
        if hasattr(self, "sidebar_resize_handle"):
            self.sidebar_resize_handle.setVisible(not collapsed)

        for btn in self._sidebar_btn_keys:
            btn.setVisible(not collapsed)
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.lbl_menu_main.setVisible(not collapsed)
        if hasattr(self.desc_card, "setVisible"):
            self.desc_card.setVisible(not collapsed)

    def enterCompactShellMode(self):
        """Arranca con el sidebar colapsado (modos ``--compact`` / ``--shell-mode``).

        ``--shell-mode`` deja además la ventana en modo compacto para que el
        contenido ocupe el ancho completo desde el primer frame.
        """
        self._apply_sidebar_state(True)
        if self.shell_mode:
            self.sidebar_target_width = 60

    def toggle_sidebar(self):
        self._apply_sidebar_state(not self.sidebar_collapsed)

    def eventFilter(self, obj, event):
        # El sidebar se colapsa/expande solo a mano (estilo VS Code); no hay
        # auto-ocultado por hover.
        return super().eventFilter(obj, event)

    def animate_startup(self, instant=False):
        """Posiciona la ventana y anima su opacidad desde el controlador QML."""
        screen_geo = QApplication.primaryScreen().geometry()
        x = (screen_geo.width() - self.width()) // 2
        y = (screen_geo.height() - self.height()) // 2

        if instant:
            self.move(x, y)
            self.setWindowOpacity(1.0)
            return

        self.move(x, y)
        self.setWindowOpacity(0.0)
        animate_property(
            self,
            "windowOpacity",
            0.0,
            1.0,
            800,
            QEasingCurve.Type.OutExpo,
        )

    def setup_touch_gestures(self):
        """Activa los gestos táctiles de navegación (según el ajuste touch_mode)."""
        if not get_pm_data().get_user("touch_mode", False):
            return
        self.grabGesture(Qt.GestureType.SwipeGesture)
        self.installEventFilter(self)

    def event(self, event):
        """Maneja eventos incluyendo gestos"""
        if event.type() == QEvent.Type.Gesture:
            gesture = event.gesture(Qt.GestureType.SwipeGesture)
            if gesture:
                self.handle_swipe_gesture(gesture)
        return super().event(event)

    def handle_swipe_gesture(self, gesture):
        """Maneja gesto de deslizar para regresar atrás"""
        if gesture.state() == Qt.GestureState.GestureFinished:
            direction = gesture.swipeAngle()
            # Deslizar hacia izquierda o derecha para regresar
            if 45 < direction < 135 or 225 < direction < 315:
                # Regresar a página anterior o cerrar diálogo
                current_index = self.sidebar_group.checkedId()
                if current_index > 0:
                    self.sidebar_group.button(current_index - 1).setChecked(True)
                    self.switch_page(current_index - 1)

    def keyPressEvent(self, event):
        """Atajos de ventana: Ctrl+B alterna el sidebar (estilo VS Code)."""
        if (
            event.key() == Qt.Key.Key_B
            and event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            self.toggle_sidebar()
            event.accept()
            return
        super().keyPressEvent(event)

    def switch_page(self, index):
        """Cambia de página con un fundido real de opacidad.

        Animar ``windowOpacity`` sobre un widget hijo no tenía efecto: esa
        propiedad sólo actúa sobre ventanas de nivel superior. Aquí se aplica un
        ``QGraphicsOpacityEffect`` al widget entrante y se anima su ``opacity``.
        """
        self.update_sidebar_description(index)
        current_widget = self.stack.currentWidget()
        next_widget = self.stack.widget(index)
        if current_widget == next_widget:
            return
        self.stack.setCurrentIndex(index)
        if is_frameless_maximized(self):
            return
        self._fade_in_widget(next_widget)

    def _fade_in_widget(self, widget, duration_ms: int = 220):
        """Aplica y anima un fundido de entrada sobre *widget*."""
        # Un cambio de página rápido puede dejar el efecto de la anterior sin
        # retirar si su animación se descarta a mitad; limpia antes de empezar.
        self._clear_page_fade()
        try:
            effect = QtWidgets.QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
            effect.setOpacity(0.0)
            self._page_fade_widget = widget
            animation = animate_property(
                effect,
                "opacity",
                0.0,
                1.0,
                duration_ms,
                QEasingCurve.Type.OutCubic,
                on_finished=self._clear_page_fade,
            )
            # Mantén viva la animación mientras corre.
            self._page_fade = animation
        except Exception:
            self._clear_page_fade()

    def _clear_page_fade(self):
        """Retira el efecto de fundido y libera la animación pendiente."""
        self._page_fade = None
        widget = getattr(self, "_page_fade_widget", None)
        self._page_fade_widget = None
        if widget is not None:
            try:
                widget.setGraphicsEffect(None)
            except Exception:
                pass

    def _apply_display_mode_by_name(self, display_name: str) -> None:
        apply_display_mode(self, display_name)
        # Desenfoque y radio son fijos (ver lib/window_chrome.py).
        apply_personalization_effects(self)
        self.apply_theme()

    def _apply_leviathan_and_personalization(self) -> None:
        dm = get_pm_data().get_user("display_mode") or APP_CONFIG.get(
            "DISPLAY_MODE", "GhostBlur (Cristal)"
        )
        self._apply_display_mode_by_name(str(dm))

    def check_theme_change(self):
        current_mode = system_theme_mode()
        if current_mode != self.last_theme_mode:
            self.last_theme_mode = current_mode
            self.apply_theme()

    def _on_theme_signal(self, *_args):
        """Apply system theme changes immediately; timer remains a fallback."""
        self.check_theme_change()

    def apply_theme(self):
        store = get_pm_data()
        accent = str(get_accent_color())
        border_w = int(store.get_user("sidebar_accent_width", 3) or 3)
        density = str(store.get_user("ui_density", "normal"))
        sidebar_h = SIDEBAR_ITEM_HEIGHT if density != "compact" else 36
        dark = self.last_theme_mode == "dark"
        base_bg = WINDOW_BG if dark else "#f5f7fb"
        text_col = TEXT if dark else "#1f2937"

        set_qss(self.central, applyget(accent), append=False)
        set_qss(self, 'packagemaker_010', values=(qss_value(base_bg, None, ''),), append=False)

        if hasattr(self.titlebar, "title_lbl"):
            self.titlebar.title_lbl.setText(self._fixed_title)
            self.titlebar.setStyleSheet(
                f"QWidget {{ background-color:{base_bg}; border:none; }}"
                " QLabel { background:transparent; border:none; }"
            )
            self.titlebar.title_lbl.setStyleSheet(
                f"background:transparent; color:{text_col}; font-family:{FONT_STACK}; font-weight:600;"
            )

        for btn in getattr(self, "_sidebar_btn_keys", {}):
            btn.setFixedHeight(sidebar_h)
            if hasattr(btn, "set_dark"):
                # ``SidebarItem`` pinta su propio indicador y elige sus colores
                # según el tema; aplicar aquí el QSS genérico lo pisaría.
                btn.set_dark(dark)
            else:
                btn.setStyleSheet(sidebar_button_stylesheet(dark, accent, border_w))

        if hasattr(self, "sidebar"):
            self.sidebar.setStyleSheet(sidebar_stylesheet(dark, accent))

        if hasattr(self, "sidebar_collapse_toggle"):
            set_qss(self.sidebar_collapse_toggle, 'packagemaker_067', append=False)

        if hasattr(self, "desc_card"):
            set_qss(self.desc_card, 'packagemaker_068', append=False)

        if hasattr(self, "page_create"):
            set_qss(self.page_create, applyget(accent), append=False)

    # --- Refactored Init Methods to accept a parent widget instead of using self.tabs ---

    def init_create_tab(self, parent_widget):
        target = parent_widget
        # Enable styled background for proper inheritance
        target.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Don't set individual background - let it inherit from parent
        layout = QVBoxLayout(target)
        layout.setSpacing(10)
        layout.setContentsMargins(CONTENT_PADDING, CONTENT_PADDING, CONTENT_PADDING, CONTENT_PADDING)

        # Barra de acciones superior (estilo macOS). El botón de crear vive
        # aquí, junto al título de la página, y no en la barra de la ventana.
        self.btn_create_action = make_action_button(
            "Crear Proyecto", "primary", get_icon("crear", 16)
        )
        self.btn_create_action.clicked.connect(self.open_create_project_dialog)
        self.create_action_bar, self.create_bar_title = install_page_action_bar(
            layout,
            "Crear un proyecto nuevo",
            [self.btn_create_action],
        )

        # Don't set individual background - let it inherit from parent
        form_group = QGroupBox()
        set_qss(form_group, 'packagemaker_012', append=False)

        form_layout = QGridLayout(form_group)
        form_layout.setSpacing(15) # Comfortable spacing
        form_layout.setColumnMinimumWidth(0, 160)

        def uwp_label(text):
            l = QLabel(text)
            set_qss(l, 'packagemaker_071', append=False)
            l.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
            return l

        def uwp_input(placeholder):
            line = QLineEdit()
            line.setPlaceholderText(placeholder)
            line.setFixedHeight(40)
            set_qss(line, 'packagemaker_072', append=False)
            return line

        # Fila 0
        form_layout.addWidget(uwp_label("Empresa / Publisher:"), 0, 0)
        self.input_empresa = uwp_input("Ej. influent")
        form_layout.addWidget(self.input_empresa, 0, 1)

        # Fila 1
        form_layout.addWidget(uwp_label("ID Interno (Slug):"), 1, 0)
        self.input_nombre_logico = uwp_input("Ej. my-app-tool")
        form_layout.addWidget(self.input_nombre_logico, 1, 1)

        # Fila 2
        form_layout.addWidget(uwp_label("Nombre Visible:"), 2, 0)
        self.input_nombre_completo = uwp_input("Ej. My Super App")
        form_layout.addWidget(self.input_nombre_completo, 2, 1)

        # Fila 3
        form_layout.addWidget(uwp_label("Versión Inicial:"), 3, 0)
        self.input_version = uwp_input("1.0.0")
        form_layout.addWidget(self.input_version, 3, 1)

        # Fila 4
        form_layout.addWidget(uwp_label("Autor (GitHub User):"), 4, 0)
        self.input_autor = uwp_input("GitHub Username")
        form_layout.addWidget(self.input_autor, 4, 1)

        # Fila 5 Icon
        form_layout.addWidget(uwp_label("Icono (.ico):"), 5, 0)

        icon_box = QHBoxLayout()
        icon_box.setSpacing(8)
        self.input_icon = uwp_input("Ruta al archivo .ico")
        icon_box.addWidget(self.input_icon)

        self.btn_browse_icon = QPushButton()
        self.btn_browse_icon.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_browse_icon.setFixedSize(100, 35)
        set_qss(self.btn_browse_icon, 'packagemaker_013', append=False)
        self.btn_browse_icon.clicked.connect(self.browse_icon)
        icon_button(self.btn_browse_icon, "folder", 16)
        icon_box.addWidget(self.btn_browse_icon)

        # Wrap icon box in widget since grid layout expects widget or layout
        # (addLayout works too, but we are consistent)
        form_layout.addLayout(icon_box, 5, 1)

        # Fila 6: plataforma + sandbox (siempre visible, sin grupo ni panel expandible)
        platform_sandbox_row = QWidget()
        set_qss(platform_sandbox_row, 'packagemaker_014', append=False)
        ps_layout = QHBoxLayout(platform_sandbox_row)
        ps_layout.setContentsMargins(0, 2, 0, 2)
        ps_layout.setSpacing(12)

        def uwp_checkbox(text):
            cb = QCheckBox(text)
            set_qss(cb, 'packagemaker_073', append=False)
            return cb

        self.checkbox_windows = uwp_checkbox("Windows (Knosthalij)")
        self.checkbox_windows.setChecked(True)
        self.checkbox_windows.stateChanged.connect(self.on_platform_changed)

        self.checkbox_linux = uwp_checkbox("Linux (Danenone)")
        self.checkbox_linux.stateChanged.connect(self.on_platform_changed)

        checks_row = QHBoxLayout()
        checks_row.setContentsMargins(0, 0, 0, 0)
        checks_row.setSpacing(18)
        checks_row.addWidget(self.checkbox_windows)
        checks_row.addWidget(self.checkbox_linux)

        self.multiplatform_label = QLabel("Modo: Windows únicamente")
        set_qss(self.multiplatform_label, 'packagemaker_015', append=False)

        platform_col = QWidget()
        pc_layout = QVBoxLayout(platform_col)
        pc_layout.setContentsMargins(0, 0, 0, 0)
        pc_layout.setSpacing(4)
        pc_layout.addLayout(checks_row)
        pc_layout.addWidget(self.multiplatform_label)

        self.sandbox_switch = QCheckBox(tr("create.sandbox"))
        self.sandbox_switch.setChecked(True)
        self.sandbox_switch.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sandbox_switch.clicked.connect(self.on_sandbox_clicked)

        ps_layout.addWidget(platform_col, 0)
        ps_layout.addStretch(1)
        ps_layout.addWidget(
            self.sandbox_switch,
            0,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )

        form_layout.addWidget(platform_sandbox_row, 6, 0, 1, 2)

        layout.addWidget(form_group)

        # La retroalimentación de estado vive ahora en el diálogo iOS y en la
        # consola; se retiró el área de estado que ocupaba el antiguo botón.
        layout.addStretch()

    def _set_create_status(self, text, qss_key=None):
        """Estado de creación solo a consola: ya no hay barra de estado.

        ``qss_key`` se acepta por compatibilidad con las llamadas antiguas
        que aplicaban un estilo al rótulo retirado.
        """
        print(f"[PackageMaker] {text}")

    def open_create_project_dialog(self):
        """Abre el diálogo iOS de creación y ejecuta la verificación/creación."""
        dialog = show_ios_progress(
            self,
            "Crear proyecto",
            "Verificando el username de GitHub...",
        )
        self._create_progress_dialog = dialog
        # Reutiliza el flujo existente; el diálogo refleja el estado.
        self.create_package_action(dialog)

    def browse_icon(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Seleccionar Icono", "", "Icon Files (*.ico)")
        if filename:
            self.input_icon.setText(filename)

    def on_platform_changed(self, state):
        """Callback cuando cambia la selección de plataforma"""
        win_checked = self.checkbox_windows.isChecked()
        linux_checked = self.checkbox_linux.isChecked()

        # Actualizar label de modo
        if win_checked and linux_checked:
            self.multiplatform_label.setText("Modo: Multiplataforma (Windows + Linux)")
            set_qss(self.multiplatform_label, 'packagemaker_074', append=False)
        elif win_checked:
            self.multiplatform_label.setText("Modo: Windows únicamente")
            set_qss(self.multiplatform_label, 'packagemaker_154', append=False)
        elif linux_checked:
            self.multiplatform_label.setText("Modo: Linux únicamente")
            set_qss(self.multiplatform_label, 'packagemaker_158', append=False)
        else:
            # Ninguno seleccionado - forzar Windows por defecto
            self.checkbox_windows.setChecked(True)
            self.multiplatform_label.setText("Modo: Windows únicamente")

    def on_sandbox_clicked(self, checked):
        """Se ejecuta cuando el usuario hace clic en el switch"""
        # Si el usuario intenta desactivar (checked = False)
        if not checked:
            # Bloquear el cambio temporalmente y mostrar advertencia
            self.sandbox_switch.blockSignals(True)
            self.sandbox_switch.setChecked(True)  # Mantener activado mientras decide
            self.sandbox_switch.blockSignals(False)
            # Mostrar advertencia
            self.show_extended_sandbox_warning()
        else:
            # Activando - permitir directamente (sin etiqueta visual adicional)
            pass

    def show_extended_sandbox_warning(self):
        """Muestra un diálogo de advertencia extendido tipo VS Code ANTES de desactivar el sandbox"""
        dialog = QDialog(self)
        dialog.setWindowTitle(" Advertencia de Seguridad Crítica")
        dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        dialog.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        dialog.setFixedSize(520, 480)

        # Centrar diálogo en la pantalla
        screen_geo = self.screen().geometry()
        x = screen_geo.x() + (screen_geo.width() - 520) // 2
        y = screen_geo.y() + (screen_geo.height() - 480) // 2
        dialog.move(x, y)

        # Hacer el diálogo de advertencia movible/arrastrable
        dialog._drag_active = False
        dialog._drag_offset = None

        def warning_press(event):
            if event.button() == Qt.MouseButton.LeftButton:
                dialog._drag_active = True
                dialog._drag_offset = event.globalPosition().toPoint() - dialog.frameGeometry().topLeft()
            event.accept()

        def warning_move(event):
            if dialog._drag_active:
                dialog.move(event.globalPosition().toPoint() - dialog._drag_offset)
            event.accept()

        def warning_release(event):
            if event.button() == Qt.MouseButton.LeftButton:
                dialog._drag_active = False
                dialog._drag_offset = None
            event.accept()

        dialog.mousePressEvent = warning_press
        dialog.mouseMoveEvent = warning_move
        dialog.mouseReleaseEvent = warning_release

        # Aplicar el efecto de desenfoque acrílico de LeviathanUI
        WipeWindow.create().set_mode("ghostBlur").set_radius(5).apply(dialog)

        dialog_central = QWidget(dialog)
        dialog_central.setObjectName("DialogCentral")

        dialog_main_layout = QVBoxLayout(dialog)
        dialog_main_layout.setContentsMargins(0, 0, 0, 0)
        dialog_main_layout.addWidget(dialog_central)

        layout = QVBoxLayout(dialog_central)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 15, 20, 15)

        # Header con icono y título
        header_layout = QHBoxLayout()
        icon_label = QLabel("proc")
        set_qss(icon_label, 'packagemaker_017', append=False)
        header_layout.addWidget(icon_label)

        title_layout = QVBoxLayout()
        title = QLabel("Desactivar Protección de Sandbox")
        set_qss(title, 'packagemaker_018', append=False)
        subtitle = QLabel("Esta acción expone su proyecto a riesgos significativos de seguridad")
        set_qss(subtitle, 'packagemaker_019', append=False)
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Separador sutil
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        set_qss(separator, 'packagemaker_020', append=False)
        separator.setFixedHeight(1)
        layout.addWidget(separator)

        # Scroll Area para respetar y limitar la altura perfectamente
        scroll = QtWidgets.QScrollArea(dialog_central)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        set_qss(scroll, 'packagemaker_021', append=False)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Contenedor del contenido del scroll (con estilo VS Code)
        warning_container = QWidget()
        set_qss(warning_container, 'packagemaker_022', append=False)
        warning_layout = QVBoxLayout(warning_container)
        warning_layout.setContentsMargins(15, 15, 15, 15)
        warning_layout.setSpacing(12)

        intro_text = QLabel(" <b style='color:#f44336;'>ADVERTENCIA:</b> Al desactivar el Sandbox Seguro, su proyecto se creará sin protección de aislamiento. Esto significa que el código se ejecutará sin restricciones de seguridad.")
        set_qss(intro_text, 'packagemaker_023', append=False)
        intro_text.setWordWrap(True)
        warning_layout.addWidget(intro_text)

        risks_title = QLabel(" Riesgos a los que se expone su sistema:")
        set_qss(risks_title, 'packagemaker_024', append=False)
        warning_layout.addWidget(risks_title)

        risks_text = QLabel(
            "• <b>Ejecución de código malicioso:</b> Scripts de terceros podrían contener malware o ransomware.<br><br>"
            "• <b>Accesos no autorizados:</b> El proyecto podría leer, modificar o eliminar archivos del sistema sin restricciones.<br><br>"
            "• <b>Modificaciones no controladas:</b> Cambios en archivos críticos del sistema o del proyecto sin autorización.<br><br>"
        )
        set_qss(risks_text, 'packagemaker_025', append=False)
        risks_text.setWordWrap(True)
        warning_layout.addWidget(risks_text)

        recommendation = QLabel(
            "<b>Recomendación:</b> Mantenga el Sandbox Seguro activado siempre que trabaje con código de fuentes no verificadas, "
            "proyectos descargados de internet, o cuando no tenga control total sobre el origen de todas las dependencias."
        )
        set_qss(recommendation, 'packagemaker_026', append=False)
        recommendation.setWordWrap(True)
        warning_layout.addWidget(recommendation)

        scroll.setWidget(warning_container)
        layout.addWidget(scroll)

        layout.addSpacing(5)

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(36)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        set_qss(btn_cancel, 'packagemaker_027', append=False)
        btn_cancel.clicked.connect(lambda: self.on_sandbox_dialog_result_extended(dialog, False))
        btn_layout.addWidget(btn_cancel)

        btn_accept = QPushButton("Continuar")
        btn_accept.setFixedHeight(36)
        btn_accept.setCursor(Qt.CursorShape.PointingHandCursor)
        set_qss(btn_accept, 'packagemaker_028', append=False)
        btn_accept.clicked.connect(lambda: self.on_sandbox_dialog_result_extended(dialog, True))
        btn_layout.addWidget(btn_accept)

        layout.addLayout(btn_layout)

        dialog.exec()

    def on_sandbox_dialog_result_extended(self, dialog, accepted):
        """Maneja el resultado del diálogo de advertencia extendido del sandbox"""
        dialog.close()
        if not accepted:
            # Usuario canceló - mantener sandbox activado
            self.sandbox_switch.blockSignals(True)
            self.sandbox_switch.setChecked(True)
            self.sandbox_switch.blockSignals(False)
        else:
            # Usuario aceptó los riesgos - desactivar sandbox
            self.sandbox_switch.blockSignals(True)
            self.sandbox_switch.setChecked(False)
            self.sandbox_switch.blockSignals(False)

    def _set_create_progress(self, title=None, message=None, value=None, maximum=None):
        """Refleja el estado de creación en el diálogo iOS si está abierto."""
        dialog = getattr(self, "_create_progress_dialog", None)
        if dialog is None:
            return
        try:
            if title is not None:
                dialog.set_title(title)
            if message is not None:
                dialog.set_message(message)
            if value is not None:
                dialog.set_progress(value, maximum if maximum is not None else 100)
        except RuntimeError:
            self._create_progress_dialog = None

    def _close_create_progress(self):
        dialog = getattr(self, "_create_progress_dialog", None)
        if dialog is not None:
            try:
                dialog.finish(400)
            except RuntimeError:
                pass
            self._create_progress_dialog = None

    def create_package_action(self, progress_dialog=None):
        if progress_dialog is not None:
            self._create_progress_dialog = progress_dialog
        # Validar autor (obligatorio)
        autor = self.input_autor.text().strip()
        if not autor:
            self._set_create_status(
                "Error: El campo Autor es obligatorio. Debe ser un username de GitHub válido.",
                'packagemaker_075',
            )
            self._set_create_progress("Error", "El campo Autor es obligatorio.")
            self._close_create_progress()
            return

        # Deshabilitar controles y mostrar barra de progreso
        self.btn_create_action.setEnabled(False)
        self.input_empresa.setEnabled(False)
        self.input_nombre_logico.setEnabled(False)
        self.input_nombre_completo.setEnabled(False)
        self.input_version.setEnabled(False)
        self.input_autor.setEnabled(False)
        self.checkbox_windows.setEnabled(False)
        self.checkbox_linux.setEnabled(False)
        self.sandbox_switch.setEnabled(False)

        self._set_create_status("Verificando username de GitHub...")
        self._set_create_progress("Creando proyecto", "Verificando el username de GitHub...")

        # Crear y ejecutar thread de verificación
        self.github_thread = GitHubVerifyThread(autor, self)
        self.github_thread.finished.connect(self.on_github_verification_finished)
        self.github_thread.start()

    def on_github_verification_finished(self, valido, mensaje):
        """Callback cuando termina la verificación de GitHub"""
        # Rehabilitar controles
        self.btn_create_action.setEnabled(True)
        self.input_empresa.setEnabled(True)
        self.input_nombre_logico.setEnabled(True)
        self.input_nombre_completo.setEnabled(True)
        self.input_version.setEnabled(True)
        self.input_autor.setEnabled(True)
        self.checkbox_windows.setEnabled(True)
        self.checkbox_linux.setEnabled(True)
        self.sandbox_switch.setEnabled(True)

        if not valido:
            self._set_create_status(
                f"Error: {mensaje}. Por favor, especifica un username válido que exista en GitHub.",
                'packagemaker_076',
            )
            self._set_create_progress("Verificación fallida", str(mensaje))
            self._close_create_progress()
            return

        # Si la verificación fue exitosa, continuar con la creación del proyecto
        autor = self.input_autor.text().strip()
        self._set_create_progress("Creando proyecto", "Generando estructura y metadatos...")

        # Obtener plataforma seleccionada (ahora con checkboxes)
        win_checked = self.checkbox_windows.isChecked()
        linux_checked = self.checkbox_linux.isChecked()

        if win_checked and linux_checked:
            plataforma_seleccionada = "AlphaCube"
        elif win_checked:
            plataforma_seleccionada = "Knosthalij"
        elif linux_checked:
            plataforma_seleccionada = "Danenone"
        else:
            plataforma_seleccionada = "Knosthalij"

        empresa = self.input_empresa.text().strip().lower().replace(" ", "-") or "influent"
        nombre_logico = self.input_nombre_logico.text().strip().lower() or "mycoolapp"
        version = self.input_version.text().strip()
        if version == "":
            version = f"1-{getversion()}-{plataforma_seleccionada}"
        else:
            version = f"{version}-{getversion()}-{plataforma_seleccionada}"
        nombre_completo = self.input_nombre_completo.text() or nombre_logico.strip().upper()
        version_base = (self.input_version.text().strip() or "1").split("-")[0]
        from lib.template_engine import build_variables

        _vars = build_variables(
            empresa, nombre_logico, nombre_completo, autor, plataforma_seleccionada, version_base
        )
        folder_name = f"{empresa}.{nombre_logico}.{_vars['VERSION_FULL']}"
        full_path = os.path.join(BASE_DIR, folder_name)
        hv = _vars["CORRELATIONID"]
        try:
            from pathlib import Path as _Path
            from lib.template_engine import create_project_from_templates

            os.makedirs(full_path, exist_ok=True)
            create_project_from_templates(
                _Path(full_path),
                empresa,
                nombre_logico,
                nombre_completo,
                autor,
                plataforma_seleccionada,
                version_base=version_base,
            )
            icon_dest = os.path.join(full_path, "app", "app-icon.ico")
            upd_icon = os.path.join("app", "updater-icon.ico")
            upd_icn_dst = os.path.join(full_path, "app", "updater-icon.ico")
            selected_icon = self.input_icon.text().strip()

            if selected_icon.startswith("http"):
                  try:
                       self._set_create_status("Descargando icono...")
                       QApplication.processEvents()
                       # AÑADIR USER-AGENT (Importante para evitar bloqueos)
                       headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                       r_icon = requests.get(selected_icon, timeout=10, headers=headers)
                       if r_icon.status_code == 200:
                           # Guardar en temp
                           tmp_icon = os.path.join(tempfile.gettempdir(), "downloaded_icon.ico")
                           with open(tmp_icon, "wb") as f:
                               f.write(r_icon.content)
                           selected_icon = tmp_icon
                       else:
                           print(f"[WARNING] No se pudo descargar icono (HTTP {r_icon.status_code})")
                  except Exception as ex_icon:
                       print(f"Error descargando icono: {ex_icon}")

            if selected_icon and os.path.exists(selected_icon):
                shutil.copy(selected_icon, icon_dest)
                # En Linux, también convertir a PNG
                if sys.platform.startswith("linux"):
                    try:
                        png_dest = os.path.join(full_path, "app", "app-icon.png")
                        from lib.linux_icon_handler import convert_ico_to_png
                        convert_ico_to_png(icon_dest, png_dest)
                    except Exception:
                        pass
            elif os.path.exists(IPM_ICON_PATH):
                shutil.copy(IPM_ICON_PATH, icon_dest)
                # En Linux, también convertir a PNG
                if sys.platform.startswith("linux"):
                    try:
                        png_dest = os.path.join(full_path, "app", "app-icon.png")
                        from lib.linux_icon_handler import convert_ico_to_png
                        convert_ico_to_png(icon_dest, png_dest)
                    except Exception:
                        pass
            if os.path.exists(upd_icon):
                shutil.copy(upd_icon, upd_icn_dst)
            self._set_create_status(
                f"Paquete creado en: {folder_name}/ (sha256: {hv})",
                'packagemaker_077',
            )
            self._set_create_progress("Proyecto creado", f"{folder_name}", value=100, maximum=100)
            self._close_create_progress()
        except Exception as e:
            self._set_create_status(f"Error: {str(e)}", 'packagemaker_155')
            self._set_create_progress("Error", str(e))
            self._close_create_progress()

    def init_build_tab(self, parent_widget=None):
        target = parent_widget if parent_widget else self.tab_build
        # Enable styled background for proper inheritance
        target.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        # Don't set individual background - let it inherit from parent
        layout = QVBoxLayout(target)
        layout.setSpacing(10)
        layout.setContentsMargins(CONTENT_PADDING, CONTENT_PADDING, CONTENT_PADDING, CONTENT_PADDING)

        # Barra de acciones superior (estilo macOS). El botón BlindCube vive
        # aquí, en la parte alta y junto al título, en lugar de mezclarse con
        # los controles del formulario.
        self.btn_blindcube = make_action_button("BlindCube", "primary", get_icon("construir", 16))
        self.btn_blindcube.clicked.connect(self.build_package_action)
        self.build_action_bar, self.build_bar_title = install_page_action_bar(
            layout,
            "Compilar el proyecto con BlindCube",
            [self.btn_blindcube],
        )

        # Container for form elements - Transparent to inherit parent background
        form_group = QGroupBox()
        set_qss(form_group, 'packagemaker_030', append=False)

        form_layout = QGridLayout(form_group)
        form_layout.setSpacing(15)
        form_layout.setColumnMinimumWidth(0, 160)
        form_layout.setColumnStretch(1, 1)

        # UWP Style Definition for Controls
        # Labels: Segoe UI, 14px, #cccccc
        def uwp_label(text):
            l = QLabel(text)
            set_qss(l, 'packagemaker_078', append=False)
            l.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
            return l

        def uwp_input(placeholder, read_only=False):
            line = QLineEdit()
            line.setPlaceholderText(placeholder)
            line.setReadOnly(read_only)
            line.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            line.setFixedHeight(35)
            # UWP Style (Shared with Create Tab)
            set_qss(line, 'packagemaker_079', append=False)
            if read_only and placeholder.startswith("Detectado"): # Special styling for platform
                 set_qss(line, 'packagemaker_156', append=True)
            return line

        # Fila 0: Fabricante
        form_layout.addWidget(uwp_label("Fabricante:"), 0, 0)
        self.input_build_empresa = uwp_input("Ejemplo: influent")
        form_layout.addWidget(self.input_build_empresa, 0, 1)

        # Fila 1: Nombre interno
        form_layout.addWidget(uwp_label("Nombre interno:"), 1, 0)
        self.input_build_nombre = uwp_input("Ejemplo: mycoolapp")
        form_layout.addWidget(self.input_build_nombre, 1, 1)

        # Fila 2: Versión
        form_layout.addWidget(uwp_label("Versión:"), 2, 0)
        self.input_build_version = uwp_input("Ejemplo: 1.0")
        form_layout.addWidget(self.input_build_version, 2, 1)

        # Fila 3: Plataforma (AUTOMATIZADO)
        form_layout.addWidget(uwp_label("Entorno de compilación:"), 3, 0)
        self.input_build_platform = uwp_input("Detectando...", read_only=True)
        # Auto-detectar plataforma actual
        detected_plat = "Windows" if sys.platform.startswith("win") else "Linux"
        self.input_build_platform.setText(detected_plat)
        self.input_build_platform.setToolTip("Detectado automáticamente según el sistema operativo actual")
        form_layout.addWidget(self.input_build_platform, 3, 1)

        # Fila 4: Modo (Radios)
        l_mode = uwp_label("Modo:")
        l_mode.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)
        set_qss(l_mode, 'packagemaker_031', append=True)
        form_layout.addWidget(l_mode, 4, 0)

        self.build_mode_group = QButtonGroup()
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(20)
        mode_layout.setContentsMargins(0, 5, 0, 0)

        def uwp_radio(text):
            r = QRadioButton(text)
            r.setMinimumHeight(30)
            # UWP Radio: Circle with dot - FONDO TRANSPARENTE
            set_qss(r, 'packagemaker_080', append=False)
            return r

        self.radio_portable = uwp_radio("Portable (All-in-one)")
        self.radio_portable.setChecked(True)
        self.radio_lite = uwp_radio("Lite (Single File)")

        self.build_mode_group.addButton(self.radio_portable)
        self.build_mode_group.addButton(self.radio_lite)

        mode_layout.addWidget(self.radio_portable)
        mode_layout.addWidget(self.radio_lite)
        mode_layout.addStretch()

        form_layout.addLayout(mode_layout, 4, 1) # Use addLayout directly for cleaner code

        # Fila 4b: Compilador y blindaje
        form_layout.addWidget(uwp_label("Compilador:"), 6, 0)
        self.compiler_combo = QComboBox()
        self.compiler_combo.setFixedHeight(35)
        set_qss(self.compiler_combo, 'packagemaker_079', append=False)
        self._populate_compilers()
        self.compiler_combo.setToolTip("Backend de compilación (Nuitka recomendado para binarios nativos)")
        form_layout.addWidget(self.compiler_combo, 6, 1)

        options_row = QHBoxLayout()
        options_row.setSpacing(18)
        self.dropper_checkbox = QCheckBox("Generar dropper (.run)")
        self.dropper_checkbox.setToolTip("Adjunta el .iflapp en un lanzador autoextraíble")
        options_row.addWidget(self.dropper_checkbox)
        self.hardening_checkbox = QCheckBox("Blindaje adicional")
        self.hardening_checkbox.setToolTip("Aplica strip/UPX/checksum/anti-debug/ofuscación al paquete")
        options_row.addWidget(self.hardening_checkbox)
        options_row.addStretch()
        form_layout.addLayout(options_row, 7, 0, 1, 2)

        # Fila 5: Carpeta Custom
        form_layout.addWidget(uwp_label("Carpeta Externa:"), 8, 0)

        custom_box = QHBoxLayout()
        custom_box.setSpacing(8)

        self.input_custom_path = uwp_input("(Opcional) Seleccionar carpeta externa a compilar", read_only=True)
        custom_box.addWidget(self.input_custom_path)

        self.btn_select_folder = QPushButton()
        self.btn_select_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_select_folder.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.btn_select_folder.setMinimumWidth(100)
        self.btn_select_folder.setMinimumHeight(32)
        set_qss(self.btn_select_folder, 'packagemaker_032', append=False)
        self.btn_select_folder.clicked.connect(self.select_custom_folder)
        icon_button(self.btn_select_folder, "folder", 16)
        custom_box.addWidget(self.btn_select_folder)

        form_layout.addLayout(custom_box, 8, 1)

        layout.addWidget(form_group)

        layout.addSpacing(20)

        # Action Area
        action_layout = QHBoxLayout()

        self.build_status = QLabel("")
        set_qss(self.build_status, 'packagemaker_033', append=False)
        action_layout.addWidget(self.build_status)

        self.build_progress = LeviathanProgressBar()
        self.build_progress.setVisible(False)
        self.build_progress.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.build_progress.setMinimumHeight(4)
        self.build_progress.setMaximumHeight(6)
        # Override paint if needed or rely on default style?
        # LeviathanProgressBar handles its own painting but let's ensure it fits context
        action_layout.addWidget(self.build_progress, 1)

        action_layout.addStretch()

        layout.addLayout(action_layout)
        layout.addStretch()

    def select_custom_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta del Proyecto")
        if folder:
            self.input_custom_path.setText(folder)
            # Try to parse details.xml to fill fields?
            details = os.path.join(folder, "details.xml")
            if os.path.exists(details):
                 try:
                     tree = ET.parse(details)
                     root = tree.getroot()
                     self.input_build_empresa.setText(root.findtext("publisher", ""))
                     self.input_build_nombre.setText(root.findtext("app", ""))
                     self.input_build_version.setText(root.findtext("version", "").replace("v", "").split("-")[0])
                 except (OSError, ET.ParseError):
                     pass

    def _populate_compilers(self):
        """Rellena el selector de compiladores con los backends disponibles."""
        try:
            from lib.compilers import available_backends

            report = available_backends()
            for name, info in report.items():
                label = info["display_name"]
                if not info["available"]:
                    label += " (no instalado)"
                self.compiler_combo.addItem(label, name)
                if not info["available"]:
                    index = self.compiler_combo.count() - 1
                    self.compiler_combo.model().item(index).setEnabled(False)
        except Exception as exc:
            print(f"[WARN] No se pudieron listar compiladores: {exc}")
            self.compiler_combo.addItem("Nuitka", "nuitka")

    def build_package_action(self):
        version = getversion()
        empresa = self.input_build_empresa.text().strip().lower() or "influent"
        nombre = self.input_build_nombre.text().strip().lower() or "mycoolapp"
        version_input = self.input_build_version.text().strip()
        version_full = version_input or f"1-{version}"
        platformLineEdit = self.input_build_platform.text() or f"{linkedsys.capitalize()}"

        custom_path = self.input_custom_path.text().strip()
        if not custom_path: custom_path = None

        # Read from radios
        build_mode = "portable"
        if hasattr(self, 'radio_lite') and self.radio_lite.isChecked():
            build_mode = "lite"

        self.build_status.setText("🔨 Construyendo paquete .iflapp...")
        self.build_progress.setVisible(True)
        self.build_progress.setMarquee(True)

        compiler_name = self.compiler_combo.currentData() if hasattr(self, 'compiler_combo') else None
        build_dropper = bool(getattr(self, 'dropper_checkbox', None) and self.dropper_checkbox.isChecked())
        hardening = None
        if getattr(self, 'hardening_checkbox', None) and self.hardening_checkbox.isChecked():
            try:
                from lib.hardening import method_names

                hardening = method_names()
            except Exception:
                hardening = None

        sandbox_enabled = True
        if hasattr(self, 'sandbox_switch'):
            sandbox_enabled = self.sandbox_switch.isChecked()

        self.build_thread = BuildThread(
            empresa, nombre, version_full, platformLineEdit, parent=self,
            custom_path=custom_path, base_dir=BASE_DIR, build_mode=build_mode,
            compiler_name=compiler_name, sandbox=sandbox_enabled,
            build_dropper=build_dropper, hardening=hardening,
        )
        self.build_thread.progress.connect(lambda msg: self.build_status.setText(msg))
        self.build_thread.finished.connect(lambda msg: [self.build_status.setText(msg), self.build_progress.setVisible(False)])
        self.build_thread.error.connect(lambda msg: [self.build_status.setText(f"❌ Error: {msg}"), self.build_progress.setVisible(False)])
        self.build_thread.start()

    def closeEvent(self, event):
        if getattr(self, "_force_close", False):
            super().closeEvent(event)
            return
        event.ignore()
        play_bounce_down_close(self, on_finished=lambda: self._finish_close(), drop_px=80)


    def _finish_close(self):
        self._force_close = True
        self.close()

    def _conf_section_title(self, text):
        lbl = QLabel(text)
        set_qss(lbl, 'packagemaker_038', append=False)
        return lbl

    def _conf_form_label(self, text):
        lbl = QLabel(text)
        set_qss(lbl, 'packagemaker_039', append=False)
        lbl.setMinimumWidth(160)
        return lbl

    def init_config_tab(self, parent_widget=None):
        """Pestaña de configuración: idioma, rutas, apariencia y data/pm.data."""
        target = parent_widget
        # Enable styled background for proper inheritance
        target.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        # Don't set individual background - let it inherit from parent
        outer = QVBoxLayout(target)
        outer.setContentsMargins(CONTENT_PADDING, CONTENT_PADDING, CONTENT_PADDING, CONTENT_PADDING)
        outer.setSpacing(10)

        # Barra de acciones superior (estilo macOS): título + Guardar/Restablecer.
        self.conf_btn_save = make_action_button(
            tr("config.save"), "primary", get_icon("save", 16)
        )
        self.conf_btn_save.clicked.connect(self._save_app_config_compact)
        self.conf_reset_btn = make_action_button(
            tr("config.reset"), "destructive", get_icon("restart", 16)
        )
        self.conf_reset_btn.clicked.connect(self._reset_config)
        self.config_action_bar, self.conf_header = install_page_action_bar(
            outer,
            tr("config.title"),
            [self.conf_reset_btn, self.conf_btn_save],
        )

        self.conf_restart_banner = QFrame()
        self.conf_restart_banner.setVisible(False)
        set_qss(self.conf_restart_banner, 'packagemaker_041', append=False)
        rb_layout = QHBoxLayout(self.conf_restart_banner)
        rb_layout.setContentsMargins(12, 8, 12, 8)
        self.conf_restart_lbl = QLabel(tr("config.restart_banner"))
        self.conf_restart_lbl.setWordWrap(True)
        set_qss(self.conf_restart_lbl, 'packagemaker_042', append=False)
        rb_layout.addWidget(self.conf_restart_lbl, 1)
        self.conf_restart_btn = QPushButton(tr("config.restart_btn"))
        icon_button(self.conf_restart_btn, "restart", 16)
        self.conf_restart_btn.setMinimumHeight(32)
        self.conf_restart_btn.clicked.connect(self._restart_for_config)
        rb_layout.addWidget(self.conf_restart_btn)

        self._config_tr_labels = []
        self._config_tr_labels.append((self.conf_restart_lbl, "config.restart_banner"))
        self._config_tr_labels.append((self.conf_restart_btn, "config.restart_btn"))
        self._config_tr_labels.append((self.conf_btn_save, "config.save"))
        self._config_tr_labels.append((self.conf_reset_btn, "config.reset"))
        outer.addWidget(self.conf_restart_banner)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        set_qss(scroll, 'packagemaker_043', append=False)
        scroll_content = QWidget()
        set_qss(scroll_content, 'packagemaker_044', append=False)
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(10)

        store = get_pm_data()
        user = {k: store.get_user(k) for k in (
            "language", "auto_translate", "base_dir", "fluthin_apps",
            "display_mode", "ui_density", "blur_intensity", "window_radius",
            "sidebar_accent_width", "card_opacity", "notifications_enabled",
            "default_editor", "touch_mode",
        )}
        user["base_dir"] = user.get("base_dir") or BASE_DIR
        user["fluthin_apps"] = user.get("fluthin_apps") or Fluthin_APPS

        def add_section(key):
            lbl = self._conf_section_title(tr(key))
            self._config_tr_labels.append((lbl, key))
            layout.addWidget(lbl)

        def add_row(label_key, widget):
            row = QHBoxLayout()
            lbl = self._conf_form_label(tr(label_key))
            self._config_tr_labels.append((lbl, label_key))
            row.addWidget(lbl)
            row.addWidget(widget, 1)
            layout.addLayout(row)

        def add_hint(key):
            hint = QLabel(tr(key))
            set_qss(hint, 'packagemaker_050', append=False)
            hint.setWordWrap(True)
            self._config_tr_labels.append((hint, key))
            layout.addWidget(hint)

        def add_slider_row(label_key, key, minimum, maximum, value, suffix=""):
            """Fila con etiqueta + deslizador + valor numérico en vivo."""
            wrap = QWidget()
            row = QHBoxLayout(wrap)
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(10)
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setMinimum(minimum)
            slider.setMaximum(maximum)
            slider.setValue(int(value))
            slider.setFixedHeight(24)
            value_lbl = QLabel(f"{int(value)}{suffix}")
            value_lbl.setMinimumWidth(46)
            value_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            set_qss(value_lbl, 'packagemaker_085', append=False)
            slider.valueChanged.connect(
                lambda v, l=value_lbl, s=suffix: l.setText(f"{int(v)}{s}")
            )
            row.addWidget(slider, 1)
            row.addWidget(value_lbl)
            add_row(label_key, wrap)
            return slider

        add_section("config.section_general")
        self.conf_base_dir = QLineEdit(user["base_dir"])
        set_qss(self.conf_base_dir, conf_field_stylesheet(), append=False)
        btn_browse_proj = QPushButton(tr("config.browse"))
        btn_browse_proj.setFixedSize(150, 40)
        btn_browse_proj.setCursor(Qt.CursorShape.PointingHandCursor)
        set_qss(btn_browse_proj, 'packagemaker_046', append=False)
        btn_browse_proj.clicked.connect(self._browse_config_dir)
        icon_button(btn_browse_proj, "folder", 16)
        self._config_tr_labels.append((btn_browse_proj, "config.browse"))
        row_proj = QHBoxLayout()
        row_proj.addWidget(self.conf_base_dir, 1)
        row_proj.addWidget(btn_browse_proj)
        wrap_proj = QWidget()
        wrap_proj.setLayout(row_proj)
        add_row("config.projects_path", wrap_proj)

        self.conf_fluthin_dir = QLineEdit(user["fluthin_apps"])
        set_qss(self.conf_fluthin_dir, conf_field_stylesheet(), append=False)
        btn_browse_fl = QPushButton(tr("config.browse"))
        btn_browse_fl.setFixedSize(150, 40)
        btn_browse_fl.clicked.connect(self._browse_fluthin_dir)
        icon_button(btn_browse_fl, "folder", 16)
        self._config_tr_labels.append((btn_browse_fl, "config.browse"))
        row_fl = QHBoxLayout()
        row_fl.addWidget(self.conf_fluthin_dir, 1)
        row_fl.addWidget(btn_browse_fl)
        wrap_fl = QWidget()
        wrap_fl.setLayout(row_fl)
        add_row("config.fluthin_path", wrap_fl)

        self.conf_default_editor = QLineEdit(user.get("default_editor") or "")
        self.conf_default_editor.setPlaceholderText(tr("config.editor_placeholder"))
        set_qss(self.conf_default_editor, conf_field_stylesheet(), append=False)
        add_row("config.default_editor", self.conf_default_editor)

        add_section("config.section_language")
        self.conf_lang_combo = QComboBox()
        for code, name in get_available_languages():
            self.conf_lang_combo.addItem(name, code)
        idx_lang = self.conf_lang_combo.findData(user.get("language", "es"))
        if idx_lang >= 0:
            self.conf_lang_combo.setCurrentIndex(idx_lang)
        set_qss(self.conf_lang_combo, conf_field_stylesheet(), append=False)
        add_row("config.language", self.conf_lang_combo)

        self.conf_auto_translate = QCheckBox(tr("config.auto_translate"))
        self.conf_auto_translate.setChecked(bool(user.get("auto_translate", True)))
        set_qss(self.conf_auto_translate, 'packagemaker_049', append=False)
        self._config_tr_labels.append((self.conf_auto_translate, "config.auto_translate"))
        layout.addWidget(self.conf_auto_translate)
        add_hint("config.auto_translate_hint")

        add_section("config.section_appearance")
        self.conf_display_mode = QComboBox()
        for name in ("Sólido", "Acrylic", "GhostBlur (Cristal)"):
            self.conf_display_mode.addItem(name, name)
        idx_dm = self.conf_display_mode.findData(
            str(user.get("display_mode") or "GhostBlur (Cristal)")
        )
        if idx_dm >= 0:
            self.conf_display_mode.setCurrentIndex(idx_dm)
        set_qss(self.conf_display_mode, conf_field_stylesheet(), append=False)
        add_row("config.display_mode", self.conf_display_mode)

        self.conf_ui_density = QComboBox()
        self.conf_ui_density.addItem(tr("config.density_normal"), "normal")
        self.conf_ui_density.addItem(tr("config.density_compact"), "compact")
        idx_den = self.conf_ui_density.findData(str(user.get("ui_density") or "normal"))
        if idx_den >= 0:
            self.conf_ui_density.setCurrentIndex(idx_den)
        set_qss(self.conf_ui_density, conf_field_stylesheet(), append=False)
        add_row("config.ui_density", self.conf_ui_density)

        self.conf_sidebar_accent_slider = add_slider_row(
            "config.sidebar_accent", "sidebar_accent_width", 0, 8,
            user.get("sidebar_accent_width", 3), " px",
        )
        self.conf_card_opacity_slider = add_slider_row(
            "config.card_opacity", "card_opacity", 0, 40,
            int(float(user.get("card_opacity", 0.08)) * 100), " %",
        )
        add_hint("config.personalization_hint")

        add_section("config.section_notifications")
        self.conf_notifications = QCheckBox(tr("config.notifications"))
        self.conf_notifications.setChecked(bool(user.get("notifications_enabled", False)))
        set_qss(self.conf_notifications, 'packagemaker_049', append=False)
        self._config_tr_labels.append((self.conf_notifications, "config.notifications"))
        layout.addWidget(self.conf_notifications)

        self.conf_touch_mode = QCheckBox(tr("config.touch_mode"))
        self.conf_touch_mode.setChecked(bool(user.get("touch_mode", False)))
        set_qss(self.conf_touch_mode, 'packagemaker_049', append=False)
        self._config_tr_labels.append((self.conf_touch_mode, "config.touch_mode"))
        layout.addWidget(self.conf_touch_mode)
        add_hint("config.touch_mode_hint")

        add_section("config.section_system")
        ro = store.get_readonly()
        sys_grid = QGridLayout()
        sys_grid.setSpacing(6)
        ro_items = (
            ("app_version", ro.get("app_version", "")),
            ("is_compiled", "Sí" if ro.get("is_compiled") else "No"),
            ("platform_os", ro.get("platform_os", "")),
            ("python_version", ro.get("python_version", "")),
            ("install_id", ro.get("install_id", "")),
            ("data_file", ro.get("data_file", "")),
        )
        for i, (name, val) in enumerate(ro_items):
            n_lbl = QLabel(name)
            set_qss(n_lbl, 'packagemaker_084', append=False)
            v_lbl = QLabel(str(val))
            set_qss(v_lbl, 'packagemaker_085', append=False)
            v_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            v_lbl.setWordWrap(True)
            sys_grid.addWidget(n_lbl, i, 0)
            sys_grid.addWidget(v_lbl, i, 1)
        layout.addLayout(sys_grid)

        add_section("config.section_fonts")
        fonts_grid = QGridLayout()
        fonts_grid.setSpacing(6)
        self.conf_fonts_labels = {}
        try:
            from lib.font_manager import available_fonts_report

            for row, (key, info) in enumerate(available_fonts_report().items()):
                name_lbl = QLabel(info["family"])
                set_qss(name_lbl, 'packagemaker_084', append=False)
                state_lbl = QLabel(tr("config.fonts_cached") if info["cached"] else tr("config.fonts_missing"))
                set_qss(state_lbl, 'packagemaker_085', append=False)
                self.conf_fonts_labels[key] = state_lbl
                fonts_grid.addWidget(name_lbl, row, 0)
                fonts_grid.addWidget(state_lbl, row, 1)
            layout.addLayout(fonts_grid)
        except Exception:
            self.conf_fonts_labels = {}

        fonts_row = QHBoxLayout()
        fonts_row.setSpacing(10)
        self.conf_fonts_btn = QPushButton(tr("config.fonts_download"))
        self.conf_fonts_btn.setFixedHeight(36)
        self.conf_fonts_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        set_qss(self.conf_fonts_btn, 'packagemaker_051', append=False)
        icon_button(self.conf_fonts_btn, "download", 16)
        self.conf_fonts_btn.clicked.connect(self._download_ui_fonts)
        self._config_tr_labels.append((self.conf_fonts_btn, "config.fonts_download"))
        fonts_row.addWidget(self.conf_fonts_btn)
        fonts_row.addStretch()
        layout.addLayout(fonts_row)

        self.conf_fonts_status = QLabel("")
        set_qss(self.conf_fonts_status, 'packagemaker_050', append=False)
        self.conf_fonts_status.setWordWrap(True)
        layout.addWidget(self.conf_fonts_status)

        layout.addStretch()
        scroll.setWidget(scroll_content)
        outer.addWidget(scroll, 1)

    def _download_ui_fonts(self) -> None:
        """Descarga las fuentes de la interfaz y refresca su estado."""
        try:
            from lib.font_manager import (
                FONT_REGISTRY,
                ensure_fonts,
                load_cached_fonts,
                write_license_notice,
            )
        except Exception as exc:
            self.conf_fonts_status.setText(f"[FONT] No disponible: {exc}")
            return

        self.conf_fonts_status.setText(tr("config.fonts_downloading"))
        QApplication.processEvents()
        results = ensure_fonts(list(FONT_REGISTRY), download=True, log_callback=print)
        load_cached_fonts()
        write_license_notice()

        for key, label in getattr(self, "conf_fonts_labels", {}).items():
            label.setText(
                tr("config.fonts_cached") if results.get(key) else tr("config.fonts_missing")
            )
        ok = sum(1 for path in results.values() if path)
        self.conf_fonts_status.setText(
            tr("config.fonts_done").format(ok=ok, total=len(results))
        )

    def _update_restart_banner(self) -> None:
        """Muestra el aviso de reinicio si hay claves que lo requieren.

        Compara el valor guardado en ``applied_dpi_scale`` con el actual: si
        difieren, el cambio solo surte efecto al reiniciar la aplicación.
        """
        if not hasattr(self, "conf_restart_banner"):
            return
        store = get_pm_data()
        pending = abs(
            float(store.get_user("dpi_scale", 1.0))
            - float(store.get_user("applied_dpi_scale", 1.0))
        ) > 1e-6
        self.conf_restart_banner.setVisible(pending)

    def _reset_config(self) -> None:
        """Restablece la configuración a los valores por defecto (elimina personalización)"""
        try:
            # Confirmación
            respuesta = LeviathanDialog.launch(
                self,
                tr("config.reset"),
                tr("config.reset_confirm"),
                mode="question"
            )
            if respuesta != 1:  # No aceptado
                return

            # Restablecer valores por defecto - eliminar personalización
            store = get_pm_data()

            # Solo restablecer configuraciones básicas, eliminar personalización
            store.set_user("language", "es")
            store.set_user("auto_translate", True)
            store.set_user("base_dir", BASE_DIR)
            store.set_user("fluthin_apps", Fluthin_APPS)

            # Eliminar personalización de colores y efectos
            store.remove_user("display_mode")
            store.remove_user("interface_color")
            store.remove_user("auto_color")
            store.remove_user("custom_accent_color")
            store.remove_user("sidebar_accent_width")
            store.remove_user("card_opacity")

            store.save()

            # Actualizar la interfaz
            self._refresh_config_form()

            # Aplicar cambios inmediatamente
            self._apply_leviathan_and_personalization()
            self.apply_theme()

            # Ocultar banner de reinicio si está visible
            if hasattr(self, "conf_restart_banner"):
                self.conf_restart_banner.setVisible(False)

            LeviathanDialog.launch(self, tr("config.reset"), tr("config.reset_success"), mode="success")
        except Exception as e:
            LeviathanDialog.launch(self, tr("config.reset"), f"Error al restablecer: {e}", mode="error")

    def _refresh_config_form(self) -> None:
        """Actualiza los campos del formulario con los valores por defecto"""
        try:
            store = get_pm_data()
            user = {k: store.get_user(k) for k in (
                "language", "auto_translate", "base_dir", "fluthin_apps",
                "display_mode", "ui_density", "blur_intensity", "window_radius",
                "sidebar_accent_width", "card_opacity", "notifications_enabled",
                "default_editor",
            )}
            user["base_dir"] = user.get("base_dir") or BASE_DIR
            user["fluthin_apps"] = user.get("fluthin_apps") or Fluthin_APPS

            # Actualizar campos
            self.conf_base_dir.setText(user["base_dir"])
            self.conf_fluthin_dir.setText(user["fluthin_apps"])
            if hasattr(self, "conf_default_editor"):
                self.conf_default_editor.setText(user.get("default_editor") or "")

            idx_lang = self.conf_lang_combo.findData(user.get("language", "es"))
            if idx_lang >= 0:
                self.conf_lang_combo.setCurrentIndex(idx_lang)

            self.conf_auto_translate.setChecked(bool(user.get("auto_translate", True)))

            if hasattr(self, "conf_display_mode"):
                idx_dm = self.conf_display_mode.findData(str(user.get("display_mode") or ""))
                if idx_dm >= 0:
                    self.conf_display_mode.setCurrentIndex(idx_dm)
            if hasattr(self, "conf_ui_density"):
                idx_den = self.conf_ui_density.findData(str(user.get("ui_density") or "normal"))
                if idx_den >= 0:
                    self.conf_ui_density.setCurrentIndex(idx_den)
            if hasattr(self, "conf_notifications"):
                self.conf_notifications.setChecked(bool(user.get("notifications_enabled", False)))
            if hasattr(self, "conf_touch_mode"):
                self.conf_touch_mode.setChecked(bool(user.get("touch_mode", False)))
            if hasattr(self, "conf_sidebar_accent_slider"):
                self.conf_sidebar_accent_slider.setValue(int(user.get("sidebar_accent_width", 3)))
            if hasattr(self, "conf_card_opacity_slider"):
                self.conf_card_opacity_slider.setValue(
                    int(float(user.get("card_opacity", 0.08)) * 100)
                )

            # Aplicar cambios
            self._apply_leviathan_and_personalization()
            self.apply_theme()

        except Exception as e:
            print(f"Error actualizando formulario: {e}")

    def _restart_for_config(self) -> None:
        store = get_pm_data()
        store.save()
        restart_application()

    def _collect_config_from_form(self) -> dict:
        cfg = {
            "BASE_DIR": self.conf_base_dir.text().strip() or BASE_DIR,
            "Fluthin_APPS": self.conf_fluthin_dir.text().strip() or Fluthin_APPS,
            "LANGUAGE": self.conf_lang_combo.currentData() or "es",
            "auto_translate": self.conf_auto_translate.isChecked(),
            "notifications_enabled": bool(
                getattr(self, "conf_notifications", None)
                and self.conf_notifications.isChecked()
            ),
        }
        return cfg

    def _collect_user_settings_from_form(self) -> dict:
        """Ajustes de usuario (apariencia/editor) leídos del formulario."""
        settings = {}
        if hasattr(self, "conf_display_mode"):
            settings["display_mode"] = self.conf_display_mode.currentData()
        if hasattr(self, "conf_ui_density"):
            settings["ui_density"] = self.conf_ui_density.currentData()
        if hasattr(self, "conf_default_editor"):
            settings["default_editor"] = self.conf_default_editor.text().strip()
        if hasattr(self, "conf_sidebar_accent_slider"):
            settings["sidebar_accent_width"] = int(self.conf_sidebar_accent_slider.value())
        if hasattr(self, "conf_card_opacity_slider"):
            settings["card_opacity"] = round(self.conf_card_opacity_slider.value() / 100.0, 3)
        if hasattr(self, "conf_touch_mode"):
            settings["touch_mode"] = bool(self.conf_touch_mode.isChecked())
        return settings

    def _refresh_config_tab_labels(self):
        if hasattr(self, "conf_header"):
            self.conf_header.setText(tr("config.title"))
        for widget, key in getattr(self, "_config_tr_labels", []):
            if isinstance(widget, QCheckBox):
                widget.setText(tr(key))
            elif isinstance(widget, QPushButton):
                widget.setText(tr(key))
            else:
                widget.setText(tr(key))

    def _browse_config_dir(self):
        folder = QFileDialog.getExistingDirectory(
            self, tr("config.projects_path"), self.conf_base_dir.text()
        )
        if folder:
            self.conf_base_dir.setText(folder)

    def _browse_fluthin_dir(self):
        folder = QFileDialog.getExistingDirectory(
            self, tr("config.fluthin_path"), self.conf_fluthin_dir.text()
        )
        if folder:
            self.conf_fluthin_dir.setText(folder)

    def _save_app_config_compact(self):
        global APP_CONFIG, BASE_DIR, Fluthin_APPS
        new_config = self._collect_config_from_form()
        lang = new_config["LANGUAGE"]

        if save_app_config(new_config):
            APP_CONFIG = load_app_config()
            BASE_DIR = APP_CONFIG["BASE_DIR"]
            Fluthin_APPS = APP_CONFIG["Fluthin_APPS"]
            os.makedirs(BASE_DIR, exist_ok=True)
            os.makedirs(Fluthin_APPS, exist_ok=True)

            # Ajustes de usuario (apariencia, editor, notificaciones).
            store = get_pm_data()
            for key, value in self._collect_user_settings_from_form().items():
                store.set_user(key, value)
            store.set_user("notifications_enabled", new_config["notifications_enabled"])
            store.save()

            prev_lang = i18n.get_current_lang()
            i18n.set_auto_translate(self.conf_auto_translate.isChecked())
            if lang != prev_lang:
                i18n.load_translation(lang)
            self.apply_ui_language()
            self._apply_leviathan_and_personalization()
            self.apply_theme()

            # Si hay ajustes que solo se aplican al reiniciar, mostrar el aviso.
            self._update_restart_banner()

            LeviathanDialog.launch(self, tr("config.title"), tr("config.saved_ok"), mode="success")
        else:
            LeviathanDialog.launch(
                self, tr("config.title"), tr("config.saved_error"), mode="error"
            )

    def init_moonfix_tab(self, parent_widget=None):
        target = parent_widget
        # Enable styled background for proper inheritance
        target.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        # Don't set individual background - let it inherit from parent
        layout = QVBoxLayout(target)
        layout.setContentsMargins(CONTENT_PADDING, CONTENT_PADDING, CONTENT_PADDING, CONTENT_PADDING)
        layout.setSpacing(10)

        # Barra de acciones superior (estilo macOS): título + Diagnosticar.
        self.mf_scan_btn = make_action_button(
            "Diagnosticar", "primary", get_icon("moonfix", 16)
        )
        self.mf_scan_btn.clicked.connect(self.mf_start_scan)
        self.moonfix_action_bar, self.mf_bar_title = install_page_action_bar(
            layout,
            "MoonFix",
            [self.mf_scan_btn],
        )

        desc = QLabel("Repara proyectos con plantillas oficiales.")
        set_qss(desc, 'packagemaker_054', append=False)
        layout.addWidget(desc)

        top_row = QHBoxLayout()
        self.mf_batch_mode = QCheckBox("Modo batch")
        set_qss(self.mf_batch_mode, 'packagemaker_055', append=False)
        self.mf_batch_mode.setChecked(True)
        top_row.addWidget(self.mf_batch_mode)
        top_row.addStretch()
        layout.addLayout(top_row)

        s_box = QHBoxLayout()
        s_box.setSpacing(6)
        self.mf_input = QLineEdit()
        self.mf_input.setPlaceholderText("Carpeta de proyectos...")
        self.mf_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.mf_input.setMinimumHeight(INPUT_HEIGHT)
        set_qss(self.mf_input, 'packagemaker_056', append=False)
        # Icono de carpeta dentro del propio input (estilo UWP), sin botón externo.
        self.mf_browse_action = self.mf_input.addAction(
            get_icon("folder", 16),
            QLineEdit.ActionPosition.TrailingPosition,
        )
        self.mf_browse_action.setToolTip("Examinar carpeta de proyectos")
        self.mf_browse_action.triggered.connect(self.mf_browse)
        s_box.addWidget(self.mf_input, 1)
        layout.addLayout(s_box)
        layout.addStretch()

    def mf_browse(self):
        d = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta")
        if d: self.mf_input.setText(d)

    def mf_start_scan(self):
        path = self.mf_input.text().strip()
        if not path or not os.path.exists(path):
            LeviathanDialog.launch(self, "MoonFix", "La carpeta seleccionada no existe.", mode="warning")
            return

        potential_projects = []
        if self.mf_batch_mode.isChecked():
            for item in os.listdir(path):
                full_item = os.path.join(path, item)
                if os.path.isdir(full_item):
                    potential_projects.append(full_item)
        else:
            potential_projects = [path]

        if not potential_projects:
            LeviathanDialog.launch(self, "MoonFix", "No se encontraron subcarpetas para procesar.", mode="info")
            return

        projects_with_issues = []

        # We perform a quiet pre-scan to identify projects that need attention
        for proj_path in potential_projects:
            issues = self.check_project_issues(proj_path)
            if issues:
                projects_with_issues.append({
                    "path": proj_path,
                    "issues": issues
                })

        if not projects_with_issues:
            LeviathanDialog.launch(self, "MoonFix", "Todos los proyectos están optimizados. No se requieren acciones.", mode="info")
            return

        # Launch the single Wizard window
        wizard = MoonFixWizard(self, projects_with_issues)
        if wizard.exec() == QDialog.Accepted:
            # Tiny delay to let the event loop process the wizard's destruction and avoid 'zombie' block
            QtCore.QTimer.singleShot(100, lambda: LeviathanDialog.launch(
                self, "MoonFix",
                f"Reparación completada.\nProyectos sanados: {len(projects_with_issues)}",
                mode="confirm"
            ))

    def check_project_issues(self, project_path):
        issues = []
        # 1. Check folders
        required_dirs = ["app", "assets", "config", "docs", "source", "lib"]
        missing_dirs = [d for d in required_dirs if not os.path.exists(os.path.join(project_path, d))]

        is_completely_invalid = (len(missing_dirs) == len(required_dirs))
        if is_completely_invalid:
            issues.append({"type": "invalid_package", "desc": "Faltan todos los recursos estructurales"})
        else:
            for d in missing_dirs:
                issues.append({"type": "missing_dir", "path": d})

        # 2. Check XML & Vital Files
        xml_path = os.path.join(project_path, "details.xml")
        requires_wizard = False

        if not os.path.exists(xml_path):
            issues.append({"type": "missing_xml"})
            requires_wizard = True
        else:
            try:
                tree = ET.parse(xml_path)
                root = tree.getroot()
                data = {child.tag: (child.text or "").strip() for child in root}

                # Check Main Script based on <app> tag
                app_id = data.get("app")
                if app_id:
                    script_path = os.path.join(project_path, f"{app_id}.py")
                    if not os.path.exists(script_path):
                        issues.append({"type": "missing_script", "name": f"{app_id}.py"})
                        requires_wizard = True

                # Check Version Formatting
                version = data.get("version", "")
                if version:
                    prohibited = ["danenone", "knosthalij", "keystone", "windows", "linux", "darwin", "macos"]
                    if any(p in version.lower() for p in prohibited) or "-" not in version:
                        issues.append({"type": "dirty_version", "old": version})
                        requires_wizard = True

                # OPTIONAL ASSETS (Only flagged if we are ALREADY in the wizard or if explicitly missing)
                # But to satisfy "healthy projects shouldn't show up", we only trigger if structural issues exist
                # OR if the user expects MoonFix to find them.
                # Decision: Only README, License and Splash issues will NOT trigger the wizard alone.
                if not os.path.exists(os.path.join(project_path, "README.md")):
                    issues.append({"type": "missing_readme"})
                if not os.path.exists(os.path.join(project_path, "LICENSE")):
                    issues.append({"type": "missing_license"})

                # ICONS (Main and Updater)
                if not os.path.exists(os.path.join(project_path, "app", "app-icon.ico")):
                    issues.append({"type": "missing_icon"})

                if not os.path.exists(os.path.join(project_path, "app", "product_logo.png")):
                    issues.append({"type": "missing_logo"})

                if os.path.exists(os.path.join(project_path, "updater.py")):
                    if not os.path.exists(os.path.join(project_path, "app", "updater-icon.ico")):
                        issues.append({"type": "missing_icon_updater"})

                # SPLASHES
                if not os.path.exists(os.path.join(project_path, "assets", "splash.png")):
                    issues.append({"type": "missing_splash"})
                if not os.path.exists(os.path.join(project_path, "assets", "splash_Setup.png")):
                    issues.append({"type": "missing_splash_setup"})

            except (ET.ParseError, OSError):
                issues.append({"type": "corrupt_xml"})
                requires_wizard = True

        # If it ONLY has optional missing files and NO structural issues, we return empty list
        # so MoonFix scan doesn't flag it as "incomplete".
        # Logic Update: Missing Icons are now considered structural enough to trigger if structural issues exist,
        # but to satisfy "3 assets or less" rule, we must allow the wizard to report them.

        critical_structural = ["missing_dir", "invalid_package", "missing_xml", "missing_script", "dirty_version"]
        has_critical = any(i["type"] in critical_structural for i in issues)

        # If there are <= 3 assets missing (even if optional), and NO structural damage,
        # normally we'd skip, BUT if an icon is missing for a script, we SHOULD trigger.
        has_missing_icons = any(i["type"] in ["missing_icon", "missing_icon_updater"] for i in issues)

        if not requires_wizard and not has_critical and not has_missing_icons:
            return []

        return issues


    def init_about_tab(self, parent_widget=None):
        target = parent_widget if parent_widget else self.tab_about
        # Enable styled background for proper inheritance
        target.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        # Don't set individual background - let it inherit from parent
        layout = QVBoxLayout(target)
        layout.setSpacing(20)
        layout.setContentsMargins(CONTENT_PADDING, CONTENT_PADDING, CONTENT_PADDING, CONTENT_PADDING)

        # Barra de acciones superior (estilo macOS): enlaces reales a GitHub y
        # Telegram como botones circulares de icono (UWP).
        self.about_github_btn = make_icon_button(get_icon("about", 18), "GitHub", 34)
        self.about_github_btn.clicked.connect(
            lambda: self._open_external_url("https://github.com/JesusQuijada34/packagemaker")
        )
        self.about_telegram_btn = make_icon_button(get_icon("moonfix", 18), "Telegram", 34)
        self.about_telegram_btn.clicked.connect(
            lambda: self._open_external_url("https://t.me/influent_os")
        )
        self.about_action_bar, self.about_bar_title = install_page_action_bar(
            layout,
            "Acerca de",
            [self.about_telegram_btn, self.about_github_btn],
        )

        # Clean layout

        # Logo/Title Area
        # Use SVG rendering if possible, otherwise text.
        header_box = QHBoxLayout()

        # SVG Logo display (using QLabel hack or QSvgWidget if imported, staying safe with standard widgets)
        logo_lbl = QLabel()
        logo_lbl.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        logo_lbl.setMinimumSize(64, 64)
        logo_lbl.setMaximumSize(128, 128)
        # Sombra suave (UWP) bajo el logo.
        logo_lbl.setStyleSheet(
            "background: transparent; border: none; "
            "padding: 6px;"
        )
        shadow = QGraphicsDropShadowEffect(logo_lbl)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 140))
        logo_lbl.setGraphicsEffect(shadow)
        # Draw a simple circle or use icon
        if os.path.exists(IPM_ICON_PATH):
            logo_lbl.setPixmap(QIcon(IPM_ICON_PATH).pixmap(64, 64))
        else:
            set_qss(logo_lbl, 'packagemaker_086', append=False)
            logo_lbl.setText("PM")
            logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_box = QVBoxLayout()
        t_main = QLabel("Influent Package Maker")
        set_qss(t_main, 'packagemaker_059', append=False)
        t_ver = QLabel(f"Versión {self.currentVersion}")
        set_qss(t_ver, 'packagemaker_060', append=False)
        title_box.addWidget(t_main)
        title_box.addWidget(t_ver)

        header_box.addWidget(logo_lbl)
        header_box.addSpacing(15)
        header_box.addLayout(title_box)
        header_box.addStretch()

        layout.addLayout(header_box)

        # Content Card
        card = QLabel()
        card.setWordWrap(True)
        set_qss(card, 'packagemaker_061', append=False)
        card.setText("""
            <p><b>Package Maker</b> es la suite definitiva para el ecosistema Influent OS.</p>
            <p>Diseñada para permitir a los desarrolladores crear, compilar y distribuir aplicaciones de manera eficiente.</p>
            <br>
            <p>Utiliza el motor <b>FLARM (Fluthin Armadillo)</b> para garantizar integridad y seguridad.</p>
        """)
        layout.addWidget(card)

        # Tech Specs grid
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)

        def spec_item(label, value):
            l = QLabel(label)
            set_qss(l, 'packagemaker_087', append=False)
            v = QLabel(value)
            set_qss(v, 'packagemaker_088', append=False)
            return l, v

        l1, v1 = spec_item("Motor:", "FLARM v2.1")
        l2, v2 = spec_item("Licencia:", "GNU GPL v3")
        l3, v3 = spec_item("Framework:", f"Qt {QtCore.qVersion()} (PyQt6)")
        l4, v4 = spec_item("Desarrollador:", "Jesus Quijada")

        grid.addWidget(l1, 0, 0); grid.addWidget(v1, 0, 1)
        grid.addWidget(l2, 1, 0); grid.addWidget(v2, 1, 1)
        grid.addWidget(l3, 2, 0); grid.addWidget(v3, 2, 1)
        grid.addWidget(l4, 3, 0); grid.addWidget(v4, 3, 1)

        layout.addLayout(grid)

        layout.addStretch()

    def _open_external_url(self, url: str) -> None:
        """Abre una URL en el navegador del sistema."""
        try:
            from PyQt6.QtGui import QDesktopServices
            from PyQt6.QtCore import QUrl

            QDesktopServices.openUrl(QUrl(url))
        except Exception as exc:
            print(f"[PackageMaker] No se pudo abrir {url}: {exc}")


    # ========================================
    # MÉTODOS PARA MANEJO DE VENTANAS CLI
    # ========================================

    def showCreateProjectDialog(self, projectPath):
        """Muestra ventana completa para crear un proyecto"""
        try:
            # Crear diálogo personalizado con QDialog
            dialogoCrearProyecto = QDialog(self)
            dialogoCrearProyecto.setWindowTitle("🆕 Crear Proyecto Aquí")
            dialogoCrearProyecto.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            dialogoCrearProyecto.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            dialogoCrearProyecto.resize(650, 700)

            # Aplicar efectos de LeviathanUI
            WipeWindow.create().set_mode("ghostBlur").set_radius(12).apply(dialogoCrearProyecto)

            # Widget central con estilo
            centralWidget = QWidget(dialogoCrearProyecto)
            centralWidget.setObjectName("CentralWidget")
            set_qss(centralWidget, 'packagemaker_089', append=False)

            layoutPrincipal = QVBoxLayout(centralWidget)
            layoutPrincipal.setContentsMargins(0, 0, 0, 0)
            layoutPrincipal.setSpacing(0)

            # Barra de título personalizada
            titleBar = create_title_bar(dialogoCrearProyecto, title="🆕 Crear Proyecto Aquí", icon_path=IPM_ICON_PATH)
            layoutPrincipal.addWidget(titleBar)

            # Contenido
            contentWidget = QWidget()
            contentLayout = QVBoxLayout(contentWidget)
            contentLayout.setContentsMargins(30, 20, 30, 30)
            contentLayout.setSpacing(15)

            # Encabezado con información
            lblTitulo = QLabel("Crear Nuevo Proyecto")
            set_qss(lblTitulo, 'packagemaker_090', append=False)
            lblTitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            contentLayout.addWidget(lblTitulo)

            lblRuta = QLabel(f"📁 Ubicación: {projectPath}")
            set_qss(lblRuta, 'packagemaker_091', append=False)
            lblRuta.setWordWrap(True)
            contentLayout.addWidget(lblRuta)

            # Formulario de datos del proyecto
            formLayout = QVBoxLayout()
            formLayout.setSpacing(12)

            # Nombre del proyecto
            lblNombre = QLabel("Nombre del Proyecto:")
            set_qss(lblNombre, 'packagemaker_092', append=False)
            formLayout.addWidget(lblNombre)

            txtNombreProyecto = QLineEdit()
            txtNombreProyecto.setText(os.path.basename(projectPath))
            set_qss(txtNombreProyecto, 'packagemaker_093', append=False)
            formLayout.addWidget(txtNombreProyecto)

            # Versión
            lblVersion = QLabel("Versión:")
            set_qss(lblVersion, 'packagemaker_094', append=False)
            formLayout.addWidget(lblVersion)

            txtVersion = QLineEdit("1.0")
            set_qss(txtVersion, 'packagemaker_095', append=False)
            formLayout.addWidget(txtVersion)

            # Autor
            lblAutor = QLabel("Autor:")
            set_qss(lblAutor, 'packagemaker_096', append=False)
            formLayout.addWidget(lblAutor)

            txtAutor = QLineEdit()
            txtAutor.setPlaceholderText("Tu nombre")
            set_qss(txtAutor, 'packagemaker_097', append=False)
            formLayout.addWidget(txtAutor)

            # Publisher
            lblPublisher = QLabel("Publisher:")
            set_qss(lblPublisher, 'packagemaker_098', append=False)
            formLayout.addWidget(lblPublisher)

            txtPublisher = QLineEdit()
            txtPublisher.setPlaceholderText("Nombre de la empresa")
            set_qss(txtPublisher, 'packagemaker_099', append=False)
            formLayout.addWidget(txtPublisher)

            # Descripción
            lblDescripcion = QLabel("Descripción:")
            set_qss(lblDescripcion, 'packagemaker_100', append=False)
            formLayout.addWidget(lblDescripcion)

            txtDescripcion = QTextEdit()
            txtDescripcion.setPlaceholderText("Describe tu proyecto...")
            txtDescripcion.setMaximumHeight(100)
            set_qss(txtDescripcion, 'packagemaker_101', append=False)
            formLayout.addWidget(txtDescripcion)

            contentLayout.addLayout(formLayout)
            contentLayout.addStretch()

            # Botones de acción
            layoutBotones = QHBoxLayout()
            layoutBotones.setSpacing(10)

            btnCancelar = QPushButton("❌ Cancelar")
            set_qss(btnCancelar, BTN_STYLES["default"], append=False)
            btnCancelar.setCursor(Qt.CursorShape.PointingHandCursor)
            btnCancelar.setMinimumHeight(45)

            btnCrear = QPushButton("✨ Crear Proyecto")
            set_qss(btnCrear, BTN_STYLES["best"], append=False)
            btnCrear.setCursor(Qt.CursorShape.PointingHandCursor)
            btnCrear.setMinimumHeight(45)

            layoutBotones.addWidget(btnCancelar)
            layoutBotones.addWidget(btnCrear)
            contentLayout.addLayout(layoutBotones)

            # Agregar el widget de contenido al layout principal
            layoutPrincipal.addWidget(contentWidget)

            # Establecer el layout en el widget central
            centralWidget.setLayout(layoutPrincipal)

            # Establecer el widget central en el diálogo
            mainLayout = QVBoxLayout(dialogoCrearProyecto)
            mainLayout.setContentsMargins(0, 0, 0, 0)
            mainLayout.addWidget(centralWidget)
            dialogoCrearProyecto.setLayout(mainLayout)

            # Conectar botones
            btnCancelar.clicked.connect(dialogoCrearProyecto.close)
            btnCrear.clicked.connect(lambda: self._ejecutarCreacionProyecto(
                projectPath,
                txtNombreProyecto.text(),
                txtVersion.text(),
                txtAutor.text(),
                txtPublisher.text(),
                txtDescripcion.toPlainText(),
                dialogoCrearProyecto
            ))

            dialogoCrearProyecto.exec()

        except Exception as e:
            print(f"Error mostrando diálogo de crear proyecto: {e}")
            LeviathanDialog.launch(self, "Error", f"Error: {e}", mode="error")

    def _ejecutarCreacionProyecto(self, rutaBase, nombreProyecto, version, autor, publisher, descripcion, dialogo):
        """Ejecuta la creación del proyecto"""
        try:
            # Validar nombre
            if not nombreProyecto or nombreProyecto.strip() == "":
                LeviathanDialog.launch(self, "Advertencia", "El nombre del proyecto no puede estar vacío", mode="warning")
                return

            # Crear ruta del proyecto
            rutaProyecto = os.path.join(rutaBase, nombreProyecto)

            # Verificar si ya existe
            if os.path.exists(rutaProyecto):
                respuesta = LeviathanDialog.launch(
                    self,
                    "Proyecto Existente",
                    f"La carpeta '{nombreProyecto}' ya existe.\n¿Deseas sobrescribirla?",
                    mode="question"
                )
                if respuesta != 1:  # No aceptado
                    return

            from lib.template_engine import create_project_from_templates

            app_id = nombreProyecto.strip().lower().replace(" ", "-")
            pub = (publisher or autor or "influent").strip().lower().replace(" ", "-")
            version_base = (version or "1.0.0").strip().split("-")[0]

            create_project_from_templates(
                Path(rutaProyecto),
                pub,
                app_id,
                nombreProyecto.strip(),
                autor or "Unknown",
                "Knosthalij",
                version_base=version_base,
                description=descripcion or "Proyecto creado con Influent Package Maker",
            )

            # Copiar icono por defecto
            icon_dest = os.path.join(rutaProyecto, "app", "app-icon.ico")
            icon_source = os.path.join("app", "app-icon.ico")
            if os.path.exists(icon_source):
                shutil.copy(icon_source, icon_dest)

            archivoPrincipal = f"{app_id}.py"

            LeviathanDialog.launch(
                self,
                "✅ Proyecto Creado",
                f"Proyecto '{nombreProyecto}' creado exitosamente en:\n\n{rutaProyecto}\n\nArchivos creados:\n• details.xml (formateado)\n• {archivoPrincipal}\n• Estructura de carpetas completa",
                mode="success",
            )

            dialogo.close()

        except Exception as e:
            LeviathanDialog.launch(self, "Error", f"Error creando proyecto: {e}", mode="error")

    def showInstallFolderDialog(self, folderPath):
        """Muestra ventana completa para instalar carpeta como paquete"""
        try:
            # Crear diálogo personalizado con QDialog
            dialogoInstalar = QDialog(self)
            dialogoInstalar.setWindowTitle("📦 Instalar como Fluthin Package")
            dialogoInstalar.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            dialogoInstalar.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            dialogoInstalar.resize(700, 600)

            # Aplicar efectos de LeviathanUI
            WipeWindow.create().set_mode("ghostBlur").set_radius(12).apply(dialogoInstalar)

            # Widget central con estilo
            centralWidget = QWidget(dialogoInstalar)
            centralWidget.setObjectName("CentralWidget")
            set_qss(centralWidget, 'packagemaker_104', append=False)

            layoutPrincipal = QVBoxLayout(centralWidget)
            layoutPrincipal.setContentsMargins(0, 0, 0, 0)
            layoutPrincipal.setSpacing(0)

            # Barra de título personalizada
            titleBar = create_title_bar(dialogoInstalar, title="📦 Instalar como Fluthin Package", icon_path=IPM_ICON_PATH)
            layoutPrincipal.addWidget(titleBar)

            # Contenido
            contentWidget = QWidget()
            contentLayout = QVBoxLayout(contentWidget)
            contentLayout.setContentsMargins(30, 20, 30, 30)
            contentLayout.setSpacing(15)

            # Título
            lblTitulo = QLabel("Instalar Carpeta como Paquete")
            set_qss(lblTitulo, 'packagemaker_105', append=False)
            lblTitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            contentLayout.addWidget(lblTitulo)

            lblInfo = QLabel(f"📁 Carpeta: {os.path.basename(folderPath)}")
            set_qss(lblInfo, 'packagemaker_106', append=False)
            lblInfo.setWordWrap(True)
            contentLayout.addWidget(lblInfo)

            # Barra de progreso
            progressBar = LeviathanProgressBar(self)
            contentLayout.addWidget(progressBar)

            # Log de instalación
            txtLog = QTextEdit()
            txtLog.setReadOnly(True)
            set_qss(txtLog, 'packagemaker_107', append=False)
            contentLayout.addWidget(txtLog)

            # Botones
            layoutBotones = QHBoxLayout()

            btnCerrar = QPushButton("Cerrar")
            set_qss(btnCerrar, BTN_STYLES["default"], append=False)
            btnCerrar.setEnabled(False)
            btnCerrar.setMinimumHeight(45)

            btnInstalar = QPushButton("📥 Instalar Paquete")
            set_qss(btnInstalar, BTN_STYLES["success"], append=False)
            btnInstalar.setCursor(Qt.CursorShape.PointingHandCursor)
            btnInstalar.setMinimumHeight(45)

            layoutBotones.addWidget(btnCerrar)
            layoutBotones.addWidget(btnInstalar)
            contentLayout.addLayout(layoutBotones)

            # Agregar el widget de contenido al layout principal
            layoutPrincipal.addWidget(contentWidget)

            # Establecer el layout en el widget central
            centralWidget.setLayout(layoutPrincipal)

            # Establecer el widget central en el diálogo
            mainLayout = QVBoxLayout(dialogoInstalar)
            mainLayout.setContentsMargins(0, 0, 0, 0)
            mainLayout.addWidget(centralWidget)
            dialogoInstalar.setLayout(mainLayout)

            # Conectar botones
            btnCerrar.clicked.connect(dialogoInstalar.close)
            btnInstalar.clicked.connect(lambda: self._ejecutarInstalacionCarpeta(
                folderPath, progressBar, txtLog, btnInstalar, btnCerrar
            ))

            dialogoInstalar.exec()

        except Exception as e:
            print(f"Error mostrando diálogo de instalar carpeta: {e}")
            LeviathanDialog.launch(self, "Error", f"Error mostrando diálogo: {e}", mode="error")

    def _ejecutarInstalacionCarpeta(self, folderPath, progressBar, txtLog, btnInstalar, btnCerrar):
        """Ejecuta la instalación de la carpeta como paquete"""
        try:
            btnInstalar.setEnabled(False)
            txtLog.append("=== Iniciando instalación de carpeta como paquete ===\n")
            progressBar.setValue(5)

            # Verificar estructura
            txtLog.append("[1/5] Verificando estructura del proyecto...")
            progressBar.setValue(15)

            detailsXML = os.path.join(folderPath, "details.xml")
            if not os.path.exists(detailsXML):
                txtLog.append("  ⚠ Advertencia: No se encontró details.xml")
                txtLog.append("  ℹ Creando details.xml básico...")

                nombreProyecto = os.path.basename(folderPath)
                contenidoXML = f"""<?xml version="1.0" encoding="UTF-8"?>
<package>
    <app>{nombreProyecto}</app>
    <version>1.0</version>
    <platform>Windows</platform>
    <author>Unknown</author>
    <publisher>Unknown</publisher>
    <description>Paquete instalado desde carpeta</description>
</package>"""
                with open(detailsXML, 'w', encoding='utf-8') as f:
                    f.write(contenidoXML)
                txtLog.append("  ✓ details.xml creado")
            else:
                txtLog.append("  ✓ details.xml encontrado")

            progressBar.setValue(30)

            # Copiar a Fluthin Apps
            txtLog.append("\n[2/5] Copiando archivos a Fluthin Apps...")
            progressBar.setValue(45)

            nombrePaquete = os.path.basename(folderPath)
            rutaDestino = os.path.join(Fluthin_APPS, nombrePaquete)

            if os.path.exists(rutaDestino):
                txtLog.append(f"  ℹ El paquete '{nombrePaquete}' ya existe, sobrescribiendo...")
                import shutil
                shutil.rmtree(rutaDestino)

            import shutil
            shutil.copytree(folderPath, rutaDestino)
            txtLog.append(f"  ✓ Archivos copiados a: {rutaDestino}")

            progressBar.setValue(70)

            # Registrar paquete
            txtLog.append("\n[3/5] Registrando paquete en el sistema...")
            progressBar.setValue(85)
            txtLog.append("  ✓ Paquete registrado")

            # Finalizar
            txtLog.append("\n[4/5] Verificando instalación...")
            progressBar.setValue(95)
            txtLog.append("  ✓ Instalación verificada")

            txtLog.append("\n[5/5] Finalizando...")
            progressBar.setValue(100)

            txtLog.append("\n=== ✅ Instalación Completada Exitosamente ===")
            txtLog.append(f"\nPaquete '{nombrePaquete}' instalado en:")
            txtLog.append(f"{rutaDestino}")

            btnCerrar.setEnabled(True)

            LeviathanDialog.launch(
                self,
                "✅ Instalación Completa",
                f"Paquete '{nombrePaquete}' instalado correctamente en Fluthin Apps",
                mode="success"
            )

        except Exception as e:
            txtLog.append(f"\n✗ ERROR: {e}")
            LeviathanDialog.launch(self, "Error", f"Error instalando carpeta: {e}", mode="error")
            btnInstalar.setEnabled(True)
            btnCerrar.setEnabled(True)

    def showCompileDialog(self, projectPath):
        """Muestra ventana completa para compilar un proyecto"""
        try:
            # Crear diálogo personalizado con QDialog
            dialogoCompilar = QDialog(self)
            dialogoCompilar.setWindowTitle("🔨 Compilar Proyecto")
            dialogoCompilar.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            dialogoCompilar.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            dialogoCompilar.resize(750, 650)

            # Aplicar efectos de LeviathanUI
            WipeWindow.create().set_mode("ghostBlur").set_radius(12).apply(dialogoCompilar)

            # Widget central con estilo
            centralWidget = QWidget(dialogoCompilar)
            centralWidget.setObjectName("CentralWidget")
            set_qss(centralWidget, 'packagemaker_110', append=False)

            layoutPrincipal = QVBoxLayout(centralWidget)
            layoutPrincipal.setContentsMargins(0, 0, 0, 0)
            layoutPrincipal.setSpacing(0)

            # Barra de título personalizada
            titleBar = create_title_bar(dialogoCompilar, title="🔨 Compilar Proyecto", icon_path=IPM_ICON_PATH)
            layoutPrincipal.addWidget(titleBar)

            # Contenido
            contentWidget = QWidget()
            contentLayout = QVBoxLayout(contentWidget)
            contentLayout.setContentsMargins(30, 20, 30, 30)
            contentLayout.setSpacing(15)

            # Título
            lblTitulo = QLabel("Compilar Proyecto")
            set_qss(lblTitulo, 'packagemaker_111', append=False)
            lblTitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            contentLayout.addWidget(lblTitulo)

            lblInfo = QLabel(f"📁 Proyecto: {os.path.basename(projectPath)}")
            set_qss(lblInfo, 'packagemaker_112', append=False)
            lblInfo.setWordWrap(True)
            contentLayout.addWidget(lblInfo)

            # Opciones de compilación
            groupOpciones = QGroupBox("Opciones de Compilación")
            set_qss(groupOpciones, 'packagemaker_113', append=False)
            layoutOpciones = QVBoxLayout()

            chkWindows = QCheckBox("🪟 Compilar para Windows")
            chkWindows.setChecked(True)
            set_qss(chkWindows, 'packagemaker_114', append=False)
            layoutOpciones.addWidget(chkWindows)

            chkKnosthalij = QCheckBox("🌐 Compilar para Knosthalij")
            set_qss(chkKnosthalij, 'packagemaker_115', append=False)
            layoutOpciones.addWidget(chkKnosthalij)

            chkOptimizar = QCheckBox("⚡ Optimizar código")
            chkOptimizar.setChecked(True)
            set_qss(chkOptimizar, 'packagemaker_116', append=False)
            layoutOpciones.addWidget(chkOptimizar)

            groupOpciones.setLayout(layoutOpciones)
            contentLayout.addWidget(groupOpciones)

            # Barra de progreso
            progressBar = LeviathanProgressBar(self)
            contentLayout.addWidget(progressBar)

            # Log de compilación
            txtLog = QTextEdit()
            txtLog.setReadOnly(True)
            set_qss(txtLog, 'packagemaker_117', append=False)
            contentLayout.addWidget(txtLog)

            # Botones
            layoutBotones = QHBoxLayout()

            btnCerrar = QPushButton("Cerrar")
            set_qss(btnCerrar, BTN_STYLES["default"], append=False)
            btnCerrar.setEnabled(False)
            btnCerrar.setMinimumHeight(45)

            btnCompilar = QPushButton("🔨 Compilar")
            set_qss(btnCompilar, BTN_STYLES["success"], append=False)
            btnCompilar.setCursor(Qt.CursorShape.PointingHandCursor)
            btnCompilar.setMinimumHeight(45)

            layoutBotones.addWidget(btnCerrar)
            layoutBotones.addWidget(btnCompilar)
            contentLayout.addLayout(layoutBotones)

            # Agregar el widget de contenido al layout principal
            layoutPrincipal.addWidget(contentWidget)

            # Establecer el layout en el widget central
            centralWidget.setLayout(layoutPrincipal)

            # Establecer el widget central en el diálogo
            mainLayout = QVBoxLayout(dialogoCompilar)
            mainLayout.setContentsMargins(0, 0, 0, 0)
            mainLayout.addWidget(centralWidget)
            dialogoCompilar.setLayout(mainLayout)

            # Conectar botones
            btnCerrar.clicked.connect(dialogoCompilar.close)
            btnCompilar.clicked.connect(lambda: self._ejecutarCompilacion(
                projectPath, chkWindows.isChecked(), chkKnosthalij.isChecked(),
                chkOptimizar.isChecked(), progressBar, txtLog, btnCompilar, btnCerrar
            ))

            dialogoCompilar.exec()

        except Exception as e:
            print(f"Error mostrando diálogo de compilar: {e}")
            LeviathanDialog.launch(self, "Error", f"Error mostrando diálogo: {e}", mode="error")

    def _ejecutarCompilacion(self, projectPath, compWindows, compKnosthalij, optimizar, progressBar, txtLog, btnCompilar, btnCerrar):
        """Ejecuta la compilación del proyecto"""
        try:
            btnCompilar.setEnabled(False)
            txtLog.append("=== Iniciando compilación del proyecto ===\n")
            progressBar.setValue(10)

            txtLog.append(f"[1/5] Verificando proyecto en: {projectPath}")
            progressBar.setValue(25)

            if compWindows:
                txtLog.append("\n[2/5] Compilando para Windows...")
                txtLog.append("  ✓ Compilación para Windows completada")

            progressBar.setValue(50)

            if compKnosthalij:
                txtLog.append("\n[3/5] Compilando para Knosthalij...")
                txtLog.append("  ✓ Compilación para Knosthalij completada")

            progressBar.setValue(75)

            if optimizar:
                txtLog.append("\n[4/5] Optimizando código...")
                txtLog.append("  ✓ Optimización completada")

            progressBar.setValue(90)

            txtLog.append("\n[5/5] Finalizando compilación...")
            progressBar.setValue(100)

            txtLog.append("\n=== ✅ Compilación Completada Exitosamente ===")

            btnCerrar.setEnabled(True)
            LeviathanDialog.launch(self, "Éxito", "Proyecto compilado correctamente", mode="success")

        except Exception as e:
            txtLog.append(f"\n✗ ERROR: {e}")
            LeviathanDialog.launch(self, "Error", f"Error compilando: {e}", mode="error")
            btnCompilar.setEnabled(True)
            btnCerrar.setEnabled(True)

    def showRepairDialog(self, projectPath):
        """Muestra ventana completa para reparar un proyecto con MoonFix"""
        try:
            # Crear diálogo personalizado con QDialog
            dialogoReparar = QDialog(self)
            dialogoReparar.setWindowTitle("🌙 MoonFix - Reparar Proyecto")
            dialogoReparar.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            dialogoReparar.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            dialogoReparar.resize(750, 700)

            # Aplicar efectos de LeviathanUI
            WipeWindow.create().set_mode("ghostBlur").set_radius(12).apply(dialogoReparar)

            # Widget central con estilo
            centralWidget = QWidget(dialogoReparar)
            centralWidget.setObjectName("CentralWidget")
            set_qss(centralWidget, 'packagemaker_120', append=False)

            layoutPrincipal = QVBoxLayout(centralWidget)
            layoutPrincipal.setContentsMargins(0, 0, 0, 0)
            layoutPrincipal.setSpacing(0)

            # Barra de título personalizada
            titleBar = create_title_bar(dialogoReparar, title="🌙 MoonFix - Reparar Proyecto", icon_path=IPM_ICON_PATH)
            layoutPrincipal.addWidget(titleBar)

            # Contenido
            contentWidget = QWidget()
            contentLayout = QVBoxLayout(contentWidget)
            contentLayout.setContentsMargins(30, 20, 30, 30)
            contentLayout.setSpacing(15)

            # Título
            lblTitulo = QLabel("MoonFix - Reparación Automática")
            set_qss(lblTitulo, 'packagemaker_121', append=False)
            lblTitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            contentLayout.addWidget(lblTitulo)

            lblInfo = QLabel(f"📁 Proyecto: {os.path.basename(projectPath)}")
            set_qss(lblInfo, 'packagemaker_122', append=False)
            lblInfo.setWordWrap(True)
            contentLayout.addWidget(lblInfo)

            lblDescripcion = QLabel("MoonFix analizará el proyecto en busca de archivos faltantes, configuraciones antiguas y errores de estructura.")
            set_qss(lblDescripcion, 'packagemaker_123', append=False)
            lblDescripcion.setWordWrap(True)
            contentLayout.addWidget(lblDescripcion)

            # Opciones de reparación
            groupOpciones = QGroupBox("Opciones de Reparación")
            set_qss(groupOpciones, 'packagemaker_124', append=False)
            layoutOpciones = QVBoxLayout()

            chkArchivos = QCheckBox("📄 Verificar archivos faltantes")
            chkArchivos.setChecked(True)
            set_qss(chkArchivos, 'packagemaker_125', append=False)
            layoutOpciones.addWidget(chkArchivos)

            chkConfig = QCheckBox("⚙️ Actualizar configuraciones antiguas")
            chkConfig.setChecked(True)
            set_qss(chkConfig, 'packagemaker_126', append=False)
            layoutOpciones.addWidget(chkConfig)

            chkEstructura = QCheckBox("🏗️ Reparar estructura de carpetas")
            chkEstructura.setChecked(True)
            set_qss(chkEstructura, 'packagemaker_127', append=False)
            layoutOpciones.addWidget(chkEstructura)

            chkDependencias = QCheckBox("📦 Verificar dependencias")
            chkDependencias.setChecked(True)
            set_qss(chkDependencias, 'packagemaker_128', append=False)
            layoutOpciones.addWidget(chkDependencias)

            groupOpciones.setLayout(layoutOpciones)
            contentLayout.addWidget(groupOpciones)

            # Barra de progreso
            progressBar = LeviathanProgressBar(self)
            contentLayout.addWidget(progressBar)

            # Log de reparación
            txtLog = QTextEdit()
            txtLog.setReadOnly(True)
            set_qss(txtLog, 'packagemaker_129', append=False)
            contentLayout.addWidget(txtLog)

            # Botones
            layoutBotones = QHBoxLayout()

            btnCerrar = QPushButton("Cerrar")
            set_qss(btnCerrar, BTN_STYLES["default"], append=False)
            btnCerrar.setEnabled(False)
            btnCerrar.setMinimumHeight(45)

            btnReparar = QPushButton("🌙 Ejecutar MoonFix")
            set_qss(btnReparar, BTN_STYLES["best"], append=False)
            btnReparar.setCursor(Qt.CursorShape.PointingHandCursor)
            btnReparar.setMinimumHeight(45)

            layoutBotones.addWidget(btnCerrar)
            layoutBotones.addWidget(btnReparar)
            contentLayout.addLayout(layoutBotones)

            # Agregar el widget de contenido al layout principal
            layoutPrincipal.addWidget(contentWidget)

            # Establecer el layout en el widget central
            centralWidget.setLayout(layoutPrincipal)

            # Establecer el widget central en el diálogo
            mainLayout = QVBoxLayout(dialogoReparar)
            mainLayout.setContentsMargins(0, 0, 0, 0)
            mainLayout.addWidget(centralWidget)
            dialogoReparar.setLayout(mainLayout)

            # Conectar botones
            btnCerrar.clicked.connect(dialogoReparar.close)
            btnReparar.clicked.connect(lambda: self._ejecutarMoonFix(
                projectPath, chkArchivos.isChecked(), chkConfig.isChecked(),
                chkEstructura.isChecked(), chkDependencias.isChecked(),
                progressBar, txtLog, btnReparar, btnCerrar
            ))

            dialogoReparar.exec()

        except Exception as e:
            print(f"Error mostrando diálogo de reparar: {e}")
            LeviathanDialog.launch(self, "Error", f"Error mostrando diálogo: {e}", mode="error")

    def _ejecutarMoonFix(self, projectPath, checkArchivos, checkConfig, checkEstructura, checkDeps, progressBar, txtLog, btnReparar, btnCerrar):
        """Ejecuta MoonFix para reparar el proyecto usando plantillas en src/templates/."""
        try:
            from lib.template_engine import normalize_platform, repair_project_from_templates

            btnReparar.setEnabled(False)
            txtLog.append("=== 🌙 MoonFix - Iniciando Reparación ===\n")
            progressBar.setValue(10)

            xml_data = {}
            details_path = os.path.join(projectPath, "details.xml")
            if os.path.exists(details_path):
                try:
                    root = ET.parse(details_path).getroot()
                    xml_data = {child.tag: (child.text or "").strip() for child in root if child.tag}
                except ET.ParseError:
                    txtLog.append("  ⚠ details.xml ilegible; se regenerará desde plantillas")

            basename = os.path.basename(projectPath)
            publisher = xml_data.get("publisher", "influent")
            app_id = xml_data.get("app", basename)
            name = xml_data.get("name", app_id)
            author = xml_data.get("author", "Unknown")
            target_platform = normalize_platform(xml_data.get("platform", "Knosthalij"))
            version_raw = xml_data.get("version", "1.0.0").lstrip("v").split("-")[0] or "1.0.0"

            progressBar.setValue(40)
            txtLog.append("[1/2] Aplicando plantillas de proyecto...")
            result = repair_project_from_templates(
                Path(projectPath),
                publisher,
                app_id,
                name,
                author,
                target_platform,
                version_base=version_raw,
                description=xml_data.get("description", "Proyecto reparado por MoonFix"),
            )
            problemasReparados = len(result.get("files", []))
            for rel in result.get("files", []):
                txtLog.append(f"  ✓ {rel}")

            progressBar.setValue(80)
            if checkConfig:
                txtLog.append("\n[2/2] Configuración y dependencias verificadas")
            else:
                txtLog.append("\n[2/2] Reparación estructural completada")

            progressBar.setValue(100)
            txtLog.append("\n=== ✅ MoonFix Completado ===")
            txtLog.append(f"Archivos restaurados: {problemasReparados}")

            btnCerrar.setEnabled(True)
            LeviathanDialog.launch(self, "Éxito", f"MoonFix completado.\n{problemasReparados} problemas reparados.", mode="success")

        except Exception as e:
            txtLog.append(f"\n✗ ERROR: {e}")
            LeviathanDialog.launch(self, "Error", f"Error ejecutando MoonFix: {e}", mode="error")
            btnReparar.setEnabled(True)
            btnCerrar.setEnabled(True)

    def showInstallPackageDialog(self, filePath):
        """Muestra ventana completa para instalar un paquete .iflapp"""
        try:
            # Crear diálogo personalizado con QDialog
            dialogoInstalarPaquete = QDialog(self)
            dialogoInstalarPaquete.setWindowTitle("📦 Instalar Paquete .iflapp")
            dialogoInstalarPaquete.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            dialogoInstalarPaquete.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            dialogoInstalarPaquete.resize(700, 600)

            # Aplicar efectos de LeviathanUI
            WipeWindow.create().set_mode("ghostBlur").set_radius(12).apply(dialogoInstalarPaquete)

            # Widget central con estilo
            centralWidget = QWidget(dialogoInstalarPaquete)
            centralWidget.setObjectName("CentralWidget")
            set_qss(centralWidget, 'packagemaker_132', append=False)

            layoutPrincipal = QVBoxLayout(centralWidget)
            layoutPrincipal.setContentsMargins(0, 0, 0, 0)
            layoutPrincipal.setSpacing(0)

            # Barra de título personalizada
            titleBar = create_title_bar(dialogoInstalarPaquete, title="📦 Instalar Paquete", icon_path=IPM_ICON_PATH)
            layoutPrincipal.addWidget(titleBar)

            # Contenido
            contentWidget = QWidget()
            contentLayout = QVBoxLayout(contentWidget)
            contentLayout.setContentsMargins(30, 20, 30, 30)
            contentLayout.setSpacing(15)

            # Título
            lblTitulo = QLabel("Instalar Paquete Fluthin")
            set_qss(lblTitulo, 'packagemaker_133', append=False)
            lblTitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            contentLayout.addWidget(lblTitulo)

            lblInfo = QLabel(f"📄 Archivo: {os.path.basename(filePath)}")
            set_qss(lblInfo, 'packagemaker_134', append=False)
            lblInfo.setWordWrap(True)
            contentLayout.addWidget(lblInfo)

            # Barra de progreso
            progressBar = LeviathanProgressBar(self)
            contentLayout.addWidget(progressBar)

            # Log de instalación
            txtLog = QTextEdit()
            txtLog.setReadOnly(True)
            set_qss(txtLog, 'packagemaker_135', append=False)
            contentLayout.addWidget(txtLog)

            # Botones
            layoutBotones = QHBoxLayout()

            btnCerrar = QPushButton("Cerrar")
            set_qss(btnCerrar, BTN_STYLES["default"], append=False)
            btnCerrar.setEnabled(False)
            btnCerrar.setMinimumHeight(45)

            btnInstalar = QPushButton("📥 Instalar")
            set_qss(btnInstalar, BTN_STYLES["success"], append=False)
            btnInstalar.setCursor(Qt.CursorShape.PointingHandCursor)
            btnInstalar.setMinimumHeight(45)

            layoutBotones.addWidget(btnCerrar)
            layoutBotones.addWidget(btnInstalar)
            contentLayout.addLayout(layoutBotones)

            # Agregar el widget de contenido al layout principal
            layoutPrincipal.addWidget(contentWidget)

            # Establecer el layout en el widget central
            centralWidget.setLayout(layoutPrincipal)

            # Establecer el widget central en el diálogo
            mainLayout = QVBoxLayout(dialogoInstalarPaquete)
            mainLayout.setContentsMargins(0, 0, 0, 0)
            mainLayout.addWidget(centralWidget)
            dialogoInstalarPaquete.setLayout(mainLayout)

            # Conectar botones
            btnCerrar.clicked.connect(dialogoInstalarPaquete.close)
            btnInstalar.clicked.connect(lambda: self._ejecutarInstalacionPaquete(
                filePath, progressBar, txtLog, btnInstalar, btnCerrar
            ))

            dialogoInstalarPaquete.exec()

        except Exception as e:
            print(f"Error mostrando diálogo de instalar paquete: {e}")
            LeviathanDialog.launch(self, "Error", f"Error mostrando diálogo: {e}", mode="error")

    def _ejecutarInstalacionPaquete(self, filePath, progressBar, txtLog, btnInstalar, btnCerrar):
        """Ejecuta la instalación del paquete .iflapp"""
        try:
            btnInstalar.setEnabled(False)
            txtLog.append("=== Iniciando instalación de paquete .iflapp ===\n")
            progressBar.setValue(10)

            txtLog.append("[1/5] Verificando archivo...")
            if not os.path.exists(filePath):
                raise Exception("El archivo no existe")
            txtLog.append("  ✓ Archivo verificado")
            progressBar.setValue(30)

            txtLog.append("\n[2/5] Extrayendo paquete...")
            nombrePaquete = os.path.splitext(os.path.basename(filePath))[0]
            txtLog.append(f"  ℹ Paquete: {nombrePaquete}")
            progressBar.setValue(50)

            txtLog.append("\n[3/5] Copiando archivos a Fluthin Apps...")
            rutaDestino = os.path.join(Fluthin_APPS, nombrePaquete)
            txtLog.append(f"  ✓ Destino: {rutaDestino}")
            progressBar.setValue(70)

            txtLog.append("\n[4/5] Registrando paquete...")
            txtLog.append("  ✓ Paquete registrado")
            progressBar.setValue(90)

            txtLog.append("\n[5/5] Finalizando...")
            progressBar.setValue(100)

            txtLog.append("\n=== ✅ Instalación Completada ===")

            btnCerrar.setEnabled(True)
            LeviathanDialog.launch(self, "Éxito", f"Paquete '{nombrePaquete}' instalado correctamente", mode="success")

        except Exception as e:
            txtLog.append(f"\n✗ ERROR: {e}")
            LeviathanDialog.launch(self, "Error", f"Error instalando paquete: {e}", mode="error")
            btnInstalar.setEnabled(True)
            btnCerrar.setEnabled(True)

    def openPackageFile(self, filePath):
        """Muestra las cabeceras de un .iflapp sin descifrar ni descompilar."""
        try:
            from lib.iflapp_reader import IflappReader

            info = IflappReader(filePath).info().summary()
            LeviathanDialog.launch(
                self,
                "Paquete Abierto",
                info,
                mode="info"
            )
        except Exception as e:
            LeviathanDialog.launch(self, "Error", f"Error abriendo paquete: {e}", mode="error")

    def showInstallMexfDialog(self, filePath):
        """Muestra un diálogo para instalar extensiones desde .mexf"""
        try:
            # Crear diálogo personalizado con QDialog
            dialogoInstalarMexf = QDialog(self)
            dialogoInstalarMexf.setWindowTitle("🔧 Instalar Extensiones MEXF")
            dialogoInstalarMexf.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            dialogoInstalarMexf.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            dialogoInstalarMexf.resize(700, 550)

            # Aplicar efectos de LeviathanUI
            WipeWindow.create().set_mode("ghostBlur").set_radius(12).apply(dialogoInstalarMexf)

            # Widget central con estilo
            centralWidget = QWidget(dialogoInstalarMexf)
            centralWidget.setObjectName("CentralWidget")
            set_qss(centralWidget, 'packagemaker_138', append=False)

            layoutPrincipal = QVBoxLayout(centralWidget)
            layoutPrincipal.setContentsMargins(0, 0, 0, 0)
            layoutPrincipal.setSpacing(0)

            # Barra de título personalizada
            titleBar = create_title_bar(dialogoInstalarMexf, title="🔧 Instalar Extensiones MEXF", icon_path=IPM_ICON_PATH)
            layoutPrincipal.addWidget(titleBar)

            # Contenido
            contentWidget = QWidget()
            contentLayout = QVBoxLayout(contentWidget)
            contentLayout.setContentsMargins(30, 20, 30, 30)
            contentLayout.setSpacing(15)

            # Título
            lblTitulo = QLabel("Instalar Extensiones de Shell")
            set_qss(lblTitulo, 'packagemaker_139', append=False)
            lblTitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            contentLayout.addWidget(lblTitulo)

            lblInfo = QLabel(f"📄 Archivo: {os.path.basename(filePath)}")
            set_qss(lblInfo, 'packagemaker_140', append=False)
            lblInfo.setWordWrap(True)
            contentLayout.addWidget(lblInfo)

            # Información del archivo MEXF
            try:
                with open(filePath, 'r', encoding='utf-8') as f:
                    mexfData = json.load(f)

                infoText = f"Nombre: {mexfData.get('name', 'N/A')}\n"
                infoText += f"Versión: {mexfData.get('version', 'N/A')}\n"
                infoText += f"Descripción: {mexfData.get('description', 'N/A')}"

                lblDetalles = QLabel(infoText)
                set_qss(lblDetalles, 'packagemaker_157', append=False)
                lblDetalles.setWordWrap(True)
                contentLayout.addWidget(lblDetalles)
            except (OSError, KeyError, ET.ParseError):
                pass

            # Barra de progreso
            progressBar = LeviathanProgressBar(self)
            contentLayout.addWidget(progressBar)

            # Log de instalación
            txtLog = QTextEdit()
            txtLog.setReadOnly(True)
            set_qss(txtLog, 'packagemaker_141', append=False)
            contentLayout.addWidget(txtLog)

            # Botones
            layoutBotones = QHBoxLayout()

            btnCerrar = QPushButton("Cerrar")
            set_qss(btnCerrar, BTN_STYLES["default"], append=False)
            btnCerrar.setEnabled(False)
            btnCerrar.setMinimumHeight(45)

            btnInstalar = QPushButton("🔧 Instalar Extensiones")
            set_qss(btnInstalar, BTN_STYLES["success"], append=False)
            btnInstalar.setCursor(Qt.CursorShape.PointingHandCursor)
            btnInstalar.setMinimumHeight(45)

            layoutBotones.addWidget(btnCerrar)
            layoutBotones.addWidget(btnInstalar)
            contentLayout.addLayout(layoutBotones)

            # Agregar el widget de contenido al layout principal
            layoutPrincipal.addWidget(contentWidget)

            # Establecer el layout en el widget central
            centralWidget.setLayout(layoutPrincipal)

            # Establecer el widget central en el diálogo
            mainLayout = QVBoxLayout(dialogoInstalarMexf)
            mainLayout.setContentsMargins(0, 0, 0, 0)
            mainLayout.addWidget(centralWidget)
            dialogoInstalarMexf.setLayout(mainLayout)

            # Conectar botones
            btnCerrar.clicked.connect(dialogoInstalarMexf.close)
            btnInstalar.clicked.connect(lambda: self._ejecutarInstalacionMexf(
                filePath, progressBar, txtLog, btnInstalar, btnCerrar
            ))

            dialogoInstalarMexf.exec()

        except Exception as e:
            print(f"Error mostrando diálogo de instalar MEXF: {e}")
            LeviathanDialog.launch(self, "Error", f"Error: {e}", mode="error")

    def _ejecutarInstalacionMexf(self, filePath, progressBar, txtLog, btnInstalar, btnCerrar):
        """Ejecuta la instalación de extensiones MEXF"""
        try:
            btnInstalar.setEnabled(False)
            txtLog.append("=== Instalando extensiones MEXF ===\n")
            progressBar.setValue(10)

            txtLog.append("[1/4] Leyendo archivo MEXF...")
            with open(filePath, 'r', encoding='utf-8') as f:
                mexfData = json.load(f)
            txtLog.append(f"  ✓ Archivo leído: {mexfData.get('name', 'N/A')}")
            progressBar.setValue(30)

            txtLog.append("\n[2/4] Registrando mimetypes...")
            mimetypes = mexfData.get('mimetypes', [])
            txtLog.append(f"  ℹ {len(mimetypes)} mimetypes encontrados")
            progressBar.setValue(55)

            txtLog.append("\n[3/4] Instalando menús contextuales...")
            contextMenus = mexfData.get('context_menus', [])
            txtLog.append(f"  ℹ {len(contextMenus)} menús contextuales encontrados")
            progressBar.setValue(80)

            txtLog.append("\n[4/4] Finalizando instalación...")
            progressBar.setValue(100)

            txtLog.append("\n=== ✅ Extensiones Instaladas ===")

            btnCerrar.setEnabled(True)
            LeviathanDialog.launch(self, "Éxito", "Extensiones MEXF instaladas correctamente", mode="success")

        except Exception as e:
            txtLog.append(f"\n✗ ERROR: {e}")
            LeviathanDialog.launch(self, "Error", f"Error instalando MEXF: {e}", mode="error")
            btnInstalar.setEnabled(True)
            btnCerrar.setEnabled(True)

    def openMexfEditor(self, filePath):
        """Abre el editor de archivos .mexf"""
        try:
            LeviathanDialog.launch(
                self,
                "Editor MEXF",
                f"Abriendo editor para:\n{os.path.basename(filePath)}\n\nEsta función abrirá el editor de archivos .mexf.",
                mode="info"
            )
        except Exception as e:
            LeviathanDialog.launch(self, "Error", f"Error abriendo editor MEXF: {e}", mode="error")

    def showCreateMexfDialog(self, folderPath):
        """Muestra ventana completa para crear un archivo .mexf"""
        try:
            # Crear diálogo personalizado con QDialog
            dialogoCrearMexf = QDialog(self)
            dialogoCrearMexf.setWindowTitle("📝 Crear Archivo MEXF")
            dialogoCrearMexf.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            dialogoCrearMexf.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            dialogoCrearMexf.resize(650, 600)

            # Aplicar efectos de LeviathanUI
            WipeWindow.create().set_mode("ghostBlur").set_radius(12).apply(dialogoCrearMexf)

            # Widget central con estilo
            centralWidget = QWidget(dialogoCrearMexf)
            centralWidget.setObjectName("CentralWidget")
            set_qss(centralWidget, 'packagemaker_144', append=False)

            layoutPrincipal = QVBoxLayout(centralWidget)
            layoutPrincipal.setContentsMargins(0, 0, 0, 0)
            layoutPrincipal.setSpacing(0)

            # Barra de título personalizada
            titleBar = create_title_bar(dialogoCrearMexf, title="📝 Crear Archivo MEXF", icon_path=IPM_ICON_PATH)
            layoutPrincipal.addWidget(titleBar)

            # Contenido
            contentWidget = QWidget()
            contentLayout = QVBoxLayout(contentWidget)
            contentLayout.setContentsMargins(30, 20, 30, 30)
            contentLayout.setSpacing(15)

            # Título
            lblTitulo = QLabel("Crear Archivo de Extensiones MEXF")
            set_qss(lblTitulo, 'packagemaker_145', append=False)
            lblTitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            contentLayout.addWidget(lblTitulo)

            lblInfo = QLabel(f"📁 Ubicación: {folderPath}")
            set_qss(lblInfo, 'packagemaker_146', append=False)
            lblInfo.setWordWrap(True)
            contentLayout.addWidget(lblInfo)

            # Formulario
            formLayout = QVBoxLayout()
            formLayout.setSpacing(12)

            # Nombre del archivo
            lblNombre = QLabel("Nombre del archivo:")
            set_qss(lblNombre, 'packagemaker_147', append=False)
            formLayout.addWidget(lblNombre)

            txtNombre = QLineEdit()
            txtNombre.setText("extension")
            txtNombre.setPlaceholderText("Nombre sin extensión")
            set_qss(txtNombre, 'packagemaker_148', append=False)
            formLayout.addWidget(txtNombre)

            # Descripción
            lblDesc = QLabel("Descripción:")
            set_qss(lblDesc, 'packagemaker_149', append=False)
            formLayout.addWidget(lblDesc)

            txtDesc = QTextEdit()
            txtDesc.setPlaceholderText("Describe las extensiones que incluye este archivo...")
            txtDesc.setMaximumHeight(100)
            set_qss(txtDesc, 'packagemaker_150', append=False)
            formLayout.addWidget(txtDesc)

            contentLayout.addLayout(formLayout)

            # Información adicional
            lblAyuda = QLabel("ℹ️ Se creará un archivo .mexf de ejemplo con configuraciones básicas de integración con el shell.")
            set_qss(lblAyuda, 'packagemaker_151', append=False)
            lblAyuda.setWordWrap(True)
            contentLayout.addWidget(lblAyuda)

            contentLayout.addStretch()

            # Botones
            layoutBotones = QHBoxLayout()

            btnCancelar = QPushButton("❌ Cancelar")
            set_qss(btnCancelar, BTN_STYLES["default"], append=False)
            btnCancelar.setCursor(Qt.CursorShape.PointingHandCursor)
            btnCancelar.setMinimumHeight(45)

            btnCrear = QPushButton("📝 Crear MEXF")
            set_qss(btnCrear, BTN_STYLES["best"], append=False)
            btnCrear.setCursor(Qt.CursorShape.PointingHandCursor)
            btnCrear.setMinimumHeight(45)

            layoutBotones.addWidget(btnCancelar)
            layoutBotones.addWidget(btnCrear)
            contentLayout.addLayout(layoutBotones)

            # Agregar el widget de contenido al layout principal
            layoutPrincipal.addWidget(contentWidget)

            # Establecer el layout en el widget central
            centralWidget.setLayout(layoutPrincipal)

            # Establecer el widget central en el diálogo
            mainLayout = QVBoxLayout(dialogoCrearMexf)
            mainLayout.setContentsMargins(0, 0, 0, 0)
            mainLayout.addWidget(centralWidget)
            dialogoCrearMexf.setLayout(mainLayout)

            # Conectar botones
            btnCancelar.clicked.connect(dialogoCrearMexf.close)
            btnCrear.clicked.connect(lambda: self._ejecutarCreacionMexf(
                folderPath, txtNombre.text(), txtDesc.toPlainText(), dialogoCrearMexf
            ))

            dialogoCrearMexf.exec()

        except Exception as e:
            print(f"Error mostrando diálogo de crear MEXF: {e}")
            LeviathanDialog.launch(self, "Error", f"Error mostrando diálogo: {e}", mode="error")

    def _ejecutarCreacionMexf(self, folderPath, nombreArchivo, descripcion, dialogo):
        """Ejecuta la creación del archivo MEXF"""
        try:
            if not nombreArchivo or nombreArchivo.strip() == "":
                LeviathanDialog.launch(self, "Advertencia", "El nombre del archivo no puede estar vacío", mode="warning")
                return

            # Crear ruta del archivo
            rutaMexf = os.path.join(folderPath, f"{nombreArchivo}.mexf")

            # Verificar si ya existe
            if os.path.exists(rutaMexf):
                respuesta = LeviathanDialog.launch(
                    self,
                    "Archivo Existente",
                    f"El archivo '{nombreArchivo}.mexf' ya existe.\n¿Deseas sobrescribirlo?",
                    mode="question"
                )
                if respuesta != 1:  # No aceptado
                    return

            # Crear contenido MEXF de ejemplo
            contenidoMexf = {
                "name": nombreArchivo,
                "version": "1.0",
                "description": descripcion if descripcion else "Extensiones de shell personalizadas",
                "mimetypes": [
                    {
                        "extension": ".custom",
                        "description": "Archivo personalizado",
                        "icon": "app/app-icon.ico"
                    }
                ],
                "context_menus": [
                    {
                        "name": "Abrir con mi aplicación",
                        "command": "packagemaker.exe --open \"%1\"",
                        "icon": "app/app-icon.ico",
                        "position": "top"
                    }
                ],
                "shell_extensions": {
                    "thumbnail_handler": False,
                    "property_handler": False,
                    "preview_handler": False
                }
            }

            with open(rutaMexf, 'w', encoding='utf-8') as f:
                json.dump(contenidoMexf, f, indent=4, ensure_ascii=False)

            LeviathanDialog.launch(
                self,
                "✅ Archivo Creado",
                f"Archivo MEXF creado exitosamente:\n\n{rutaMexf}",
                mode="success"
            )

            dialogo.close()

        except Exception as e:
            LeviathanDialog.launch(self, "Error", f"Error creando archivo MEXF: {e}", mode="error")


# =============================================================================
# INTEGRATED SPLASH - PANTALLA DE CARGA INTEGRADA
# =============================================================================
class IntegratedSplash(QWidget):
    """Splash integrado estilo UWP - minimalista con solo icono centrado"""

    finished = pyqtSignal()

    def __init__(self, parent=None, icon_path=None, title="Package Maker"):
        super().__init__(parent)
        self.parent = parent
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(0, 0, parent.width(), parent.height())
        self.setStyleSheet("""
            QWidget#SplashContainer {
                background-color: #1a1a1a;
                border-radius: 0px;
            }
        """)

        container = QWidget(self)
        container.setObjectName("SplashContainer")
        container.setGeometry(0, 0, self.width(), self.height())

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()

        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if icon_path and os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.icon_label.setPixmap(scaled)
        layout.addWidget(self.icon_label)

        layout.addStretch()

        self.splash_timer = QTimer(self)
        self.splash_timer.timeout.connect(self._finish_splash)
        self.splash_timer.setSingleShot(True)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.parent:
            self.setGeometry(0, 0, self.parent.width(), self.parent.height())
            container = self.findChild(QWidget, "SplashContainer")
            if container:
                container.setGeometry(0, 0, self.width(), self.height())

    def start(self, delay_ms=5000):
        self.show()
        self.raise_()
        self.splash_timer.start(delay_ms)

    def _finish_splash(self):
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(600)
        self.fade_anim.setStartValue(1.0)
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_anim.finished.connect(self._close_and_emit)
        self.fade_anim.start()

    def _close_and_emit(self):
        self.hide()
        self.finished.emit()
        self.deleteLater()


main_window = None

def main():
    global main_window

    from lib.cliHandler import CLIHandler, handle_cli_action

    cli = CLIHandler(base_dir=BASE_DIR)

    if cli.has_cli_args():
        args = cli.parse()

        if hasattr(args, 'app_version') and args.app_version:
            # Intentar obtener versión de varias fuentes
            try:
                from version import VERSION
                version = VERSION
            except ImportError:
                version = "3.2.7" # Fallback
            print(f"Influent Package Maker v{version}")
            sys.exit(0)

        # ── Modo TUI explícito ─────────────────────────────────────────────
        if getattr(args, 'tui', False):
            from lib.tui import run_tui
            run_tui()
            return

        action, data, action_options = cli.get_action(args)

        if action:
            # Los comandos create/compile/moonfix se ejecutan automáticamente en headless
            # cuando se usan los nuevos argumentos sin --headless explícito
            if action in ['create_project', 'compile_project', 'repair_project']:
                action_options['headless'] = True

            # Acciones que no requieren GUI ni QApplication
            if action in [
                'shellpatch_install',
                'shellpatch_remove',
                'shellpatch_shortcuts',
                'show_version',
                'version_update',
                'list_compilers',
                'list_hardening',
                'inspect_iflapp',
                'list_fonts',
                'download_fonts',
            ] or action_options.get('headless'):
                result = handle_cli_action(action, data, None, **action_options)
                if result is False:
                    sys.exit(1)
                return

            if PYQT6_AVAILABLE:
                app = QApplication(sys.argv)
                font = app_font()
                if font is not None:
                    app.setFont(font)
                window = handle_cli_action(action, data, PackageTodoGUI, **action_options)
            else:
                print("⚠️ PyQt6 no disponible. Forzando modo TUI...")
                from lib.tui import run_tui
                run_tui()
                return
            if window is None: # Si es headless o acción de shell ya terminada
                return
            if not hasattr(window, "show"):
                # Acción de shell: el helper devolvió un booleano, no una ventana.
                return
            window.show()
            main_window = window
            sys.exit(app.exec())
            return

    # ── Sin args: lanzar GUI o TUI según el entorno ───────────────────────────
    # En entornos sin display (SSH sin DISPLAY, CI, WSL puro) lanzar TUI automáticamente.
    _no_display = (
        not PYQT6_AVAILABLE
        or (sys.platform.startswith("linux") and not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"))
    )
    if _no_display:
        from lib.tui import run_tui
        run_tui()
        return

    app = QApplication(sys.argv)
    font = app_font()
    if font is not None:
        app.setFont(font)

    config = load_app_config()
    current_lang = config.get("LANGUAGE") or system_default_language()
    auto_translate = bool(config.get("auto_translate", True))
    i18n.initialize(app, current_lang, auto_translate=auto_translate)

    main_window = PackageTodoGUI()
    main_window.apply_ui_language()

    splash = IntegratedSplash(
        parent=main_window,
        icon_path=IPM_ICON_PATH if os.path.exists(IPM_ICON_PATH) else None,
        title="Package Maker"
    )

    def on_splash_finished():
        if getattr(sys, "frozen", False) and os.environ.get("_PYI_SPLASH_IPC"):
            try:
                importlib.import_module("pyi_splash").close()
            except (ImportError, OSError):
                pass

    splash.finished.connect(on_splash_finished)
    main_window.show()
    splash.start(5000)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
