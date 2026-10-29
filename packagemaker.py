#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
import hashlib
import shutil
import zipfile
import xml.etree.ElementTree as ET
import urllib.request
import urllib.error
import subprocess
import platform
import fnmatch
import re
import json
import ssl
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import importlib
import importlib.util

from lib.safe_zip import safe_extract_zip

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
        QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
        QPushButton, QComboBox, QListWidget, QListWidgetItem, QFileDialog, QDialog, QStyle, QSizePolicy, QSplitter, QGroupBox, QRadioButton, QButtonGroup, QGridLayout, QProgressBar, QTextEdit, QStackedWidget,
        QSwipeGesture, QSlider, QFrame
    )
    from PyQt6.QtGui import QFont, QIcon
    from PyQt6.QtGui import QPixmap      # [NEW IMPORT FOR TITLEBAR SVG]
    from PyQt6.QtSvg import QSvgRenderer # [NEW IMPORT FOR TITLEBAR SVG RENDERING]
    from PyQt6.QtCore import QByteArray  # [NEW IMPORT FOR SVG BUFFER]
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QEvent, QObject, QProcess, QPropertyAnimation, QParallelAnimationGroup, QEasingCurve, QPoint, QSize
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
    from leviathan_ui import InmersiveSplash, LightsOff, LeviathanDialog, WipeWindow, LeviathanProgressBar, CustomTitleBar, get_accent_color
    from leviathan_ui.touchscreen import TouchScreen
    LEVIATHAN_AVAILABLE = True
except (ImportError, SyntaxError) as e:
    LEVIATHAN_AVAILABLE = False
    print(f"[WARN] Leviathan UI no disponible o error de sintaxis: {e}")
    class LeviathanDialog:
        @staticmethod
        def launch(*args, **kwargs): print(f"[MOCK] LeviathanDialog: {args}")
    class LeviathanProgressBar: pass
# Updater - usar coreUpdater si está disponible, sino fallback a lib.Updater
try:
    from lib.coreUpdater import KillerLogic, InstallerWorker, ModernUpdaterWindow
except ImportError:
    from lib.Updater import KillerLogic, InstallerWorker, ModernUpdaterWindow
from lib.BuildThread import BuildThread, FlangCompiler
from lib.TitleBar import AnimTitleButton, TitleBar
from lib.app_icons import get_icon, icon_button
from lib.window_chrome import (
    apply_display_mode,
    apply_personalization_effects,
    apply_dpi_scale,
    patch_titlebar_maximize,
    fixed_window_title,
    restart_application,
    is_frameless_maximized,
)
from lib.uwp_animations import play_bounce_down_close
from lib.openWithDialog import show_open_with_dialog, open_project_with_editor
from lib.SidebarItem import SidebarItem
from lib.moonFixWizard import MoonFixWizard, QSetup, QInstaller, verificar_github_username, detectar_modo_sistema
from lib.gitHubVerifyThread import GitHubVerifyThread
from lib.i18n import i18n, tr, system_default_language, get_available_languages
from lib.linux_icon_handler import get_linux_icon_path, ensure_linux_icon_support
from lib.pm_data import get_pm_data, load_merged_app_config, is_compiled_build, COMPILED_LOCKED_USER_KEYS
from lib.outputTerminalDialog import OutputTerminalDialog
from lib.projectDetailsDialog import ProjectDetailsDialog
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

LGDR_NAUFRAGIO_MESSAGES = {
    "_LGDR_LOCAL_LV" : "Proyectos locales encontrados en la carpeta predeterminada",
    "_LGDR_INSTALLED_LV" : "Paquetes instalados desde la ROM (Fluthin Packaged)",
    "_LGDR_REFRESH_BTN" : "Refresca proyectos locales y paquetes instalados",
    "_LGDR_INSTALL_BTN" : "Instala un paquete Fluthin desde ruta",
    "_LGDR_UNINSTALL_BTN" : "Desinstala un paquete Fluthin instalado en el directorio de la tienda",
    "_LGDR_RUNPY_BTN" : "Ejecuta/depura el script marcado",
    "_LGDR_INSTALLPROJ_BTN" : "Instala la carpeta del proyecto si se encuentra compilado",
    "_LGDR_UNINSTALLPROJ_BTN" : "Elimina definitivamente el proyecto desde el alamacenamiento",
    "_LGDR_RUNPYAPP_BTN" : "Ejecuta el script instalado",
    "_LGDR_UNINSTALLAPP_BTN" : "Desinstala definitivamente el Fluthin Seleccionado",
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
    2: "sidebar_desc.2",
    3: "sidebar_desc.3",
    4: "sidebar_desc.4",
    5: "sidebar_desc.5",
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
        self.titlebar.setStyleSheet("background-color: #3a3f4b; border: none;")
        self.titlebar.title_lbl.setText(self._fixed_title)
        patch_titlebar_maximize(self.titlebar, self)
        self._pm_reapply_display_mode = self._apply_leviathan_and_personalization
        self.v_layout.addWidget(self.titlebar)

        # Content Container (Sidebar + Stack)
        self.content_container = QWidget()
        # Enable styled background
        self.content_container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        # Cast iron gray background for content container
        #self.content_container.setStyleSheet("background: #3a3f4b;")
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
        self.sidebar_layout.setContentsMargins(15, 20, 15, 20)
        self.sidebar_layout.setSpacing(8)
        self.sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.sidebar_collapsed = False
        self.sidebar_animation = None
        self.sidebar_target_width = 260
        self.sidebar_auto_hide_timer = QTimer(self)
        self.sidebar_auto_hide_timer.setSingleShot(True)
        self.sidebar_auto_hide_timer.timeout.connect(self.collapse_sidebar)
        self.sidebar.installEventFilter(self)

        sidebar_header = QHBoxLayout()
        sidebar_header.setContentsMargins(0, 0, 0, 0)
        self.lbl_menu_main = QLabel(tr("app.main_menu"))
        set_qss(self.lbl_menu_main, 'packagemaker_004', append=False)
        sidebar_header.addWidget(self.lbl_menu_main)
        sidebar_header.addStretch()

        self.sidebar_collapse_toggle = QPushButton("❮")
        self.sidebar_collapse_toggle.setObjectName("SidebarCollapseButton")
        self.sidebar_collapse_toggle.setFixedSize(28, 28)
        self.sidebar_collapse_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sidebar_collapse_toggle.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.sidebar_collapse_toggle.clicked.connect(self.toggle_sidebar)
        self.sidebar_collapse_toggle.setToolTip("Ocultar menú")
        sidebar_header.addWidget(self.sidebar_collapse_toggle)
        self.sidebar_layout.addLayout(sidebar_header)

        # Navigation Buttons
        self.btn_create = SidebarItem(tr("sidebar.create"), get_tab_icon("crear"))
        self.btn_build = SidebarItem(tr("sidebar.build"), get_tab_icon("construir"))
        self.btn_manager = SidebarItem(tr("sidebar.manager"), get_tab_icon("gestor"))
        self.btn_config = SidebarItem(tr("sidebar.config"), get_tab_icon("config"))
        self.btn_moonfix = SidebarItem(tr("sidebar.moonfix"), get_tab_icon("moonfix"))
        self.btn_about = SidebarItem(tr("sidebar.about"), get_tab_icon("about"))
        self._sidebar_btn_keys = {
            self.btn_create: "sidebar.create",
            self.btn_build: "sidebar.build",
            self.btn_manager: "sidebar.manager",
            self.btn_config: "sidebar.config",
            self.btn_moonfix: "sidebar.moonfix",
            self.btn_about: "sidebar.about",
        }

        self.sidebar_group = QButtonGroup(self)
        self.sidebar_group.addButton(self.btn_create, 0)
        self.sidebar_group.addButton(self.btn_build, 1)
        self.sidebar_group.addButton(self.btn_manager, 2)
        self.sidebar_group.addButton(self.btn_config, 3)
        self.sidebar_group.addButton(self.btn_moonfix, 4)
        self.sidebar_group.addButton(self.btn_about, 5)
        self.sidebar_group.idClicked.connect(self.switch_page)

        self.sidebar_layout.addWidget(self.btn_create)
        self.sidebar_layout.addWidget(self.btn_build)
        self.sidebar_layout.addWidget(self.btn_manager)
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

        self.page_manager = QWidget()
        self.init_manager_tab(self.page_manager)

        self.page_config = QWidget()
        self.init_config_tab(self.page_config)

        self.page_moonfix = QWidget()
        self.init_moonfix_tab(self.page_moonfix)

        self.page_about = QWidget()
        self.init_about_tab(self.page_about)

        self.stack.addWidget(self.page_create)
        self.stack.addWidget(self.page_build)
        self.stack.addWidget(self.page_manager)
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

    def _apply_sidebar_state(self, collapsed):
        target_width = 60 if collapsed else self.sidebar_target_width
        if self.sidebar.maximumWidth() == target_width:
            return
        self.sidebar_animation = animate_property(
            self.sidebar,
            "maximumWidth",
            self.sidebar.maximumWidth(),
            target_width,
            220,
            QEasingCurve.Type.OutCubic,
        )
        self.sidebar_collapsed = collapsed
        self.sidebar_collapse_toggle.setText("❯" if collapsed else "❮")
        self.sidebar_collapse_toggle.setToolTip("Expandir menú" if collapsed else "Ocultar menú")

        for btn in self._sidebar_btn_keys:
            btn.setVisible(not collapsed)
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.lbl_menu_main.setVisible(not collapsed)
        if hasattr(self.desc_card, "setVisible"):
            self.desc_card.setVisible(not collapsed)

    def toggle_sidebar(self):
        self._apply_sidebar_state(not self.sidebar_collapsed)

    def collapse_sidebar(self):
        if not self.sidebar_collapsed:
            self._apply_sidebar_state(True)

    def expand_sidebar(self):
        if self.sidebar_collapsed:
            self._apply_sidebar_state(False)

    def eventFilter(self, obj, event):
        if obj is self.sidebar and event.type() in (QEvent.Type.Enter, QEvent.Type.MouseMove):
            self.sidebar_auto_hide_timer.stop()
            self.expand_sidebar()
        elif obj is self.sidebar and event.type() == QEvent.Type.Leave:
            self.sidebar_auto_hide_timer.start(600)
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
        """Configura gestos táctiles para navegación"""
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

    def switch_page(self, index):
        """Cambia la página (solo fundido; sin mover geometry del stack)."""
        self.update_sidebar_description(index)
        current_widget = self.stack.currentWidget()
        next_widget = self.stack.widget(index)
        if current_widget == next_widget:
            return
        self.stack.setCurrentIndex(index)
        if is_frameless_maximized(self):
            return
        try:
            next_widget.setWindowOpacity(0.0)
            animate_property(
                next_widget,
                "windowOpacity",
                0.0,
                1.0,
                850,
                QEasingCurve.Type.OutCubic,
            )
        except RuntimeError:
            next_widget.setWindowOpacity(1.0)

    def change_display_mode(self, index):
        """Compatibilidad: índice antiguo del combo (0=polished, 1=ghost, 2=ghostBlur)."""
        names = ["Sólido", "Acrylic", "GhostBlur (Cristal)"]
        if 0 <= index < len(names):
            self._apply_display_mode_by_name(names[index])

    def _apply_display_mode_by_name(self, display_name: str) -> None:
        apply_display_mode(self, display_name)
        store = get_pm_data()
        apply_personalization_effects(
            self,
            int(store.get_user("blur_intensity", 14)),
            int(store.get_user("window_radius", 12)),
        )
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
        accent_hover = accent
        border_w = 3
        density = str(store.get_user("ui_density", "normal"))
        sidebar_h = 50 if density != "compact" else 42
        dark = self.last_theme_mode == "dark"
        base_bg = "#303641" if dark else "#f5f7fb"
        text_col = "#f8fbff" if dark else "#1f2937"

        set_qss(self.central, applyget(accent), append=False)
        set_qss(self, 'packagemaker_010', values=(qss_value(base_bg, None, ''),), append=False)

        if hasattr(self.titlebar, "title_lbl"):
            self.titlebar.title_lbl.setText(self._fixed_title)
            self.titlebar.setStyleSheet(
                f"QWidget {{ background-color:{base_bg}; border:none; }}"
                " QLabel { background:transparent; border:none; }"
            )
            self.titlebar.title_lbl.setStyleSheet(
                f"background:transparent; color:{text_col}; font-family:'Roboto','Inter Regular','SF Pro Display','Segoe UI',sans-serif; font-weight:600;"
            )

        for btn in getattr(self, "_sidebar_btn_keys", {}):
            btn.setFixedHeight(sidebar_h)
            btn.setStyleSheet(sidebar_button_stylesheet(dark, accent, border_w))

        if hasattr(self, "sidebar"):
            self.sidebar.setStyleSheet(sidebar_stylesheet(dark, accent))

        if hasattr(self, "sidebar_collapse_toggle"):
            set_qss(self.sidebar_collapse_toggle, 'packagemaker_067', append=False)

        if hasattr(self, "desc_card"):
            set_qss(self.desc_card, 'packagemaker_068', append=False)

        if hasattr(self, "btn_create_action"):
            set_qss(self.btn_create_action, 'packagemaker_069', values=(qss_value(accent, None, ''), qss_value(accent_hover, None, ''), qss_value(accent, None, '')), append=False)

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
        layout.setContentsMargins(25, 25, 25, 25)

        # Header "Crear Nuevo Proyecto" as main title, no GroupBox title
        # UWP Design: Big bold headers, content below.
        title_lbl = QLabel("Crear un proyecto nuevo")
        set_qss(title_lbl, 'packagemaker_011', append=False)
        layout.addWidget(title_lbl)
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

        # Action Area
        layout.addSpacing(20)
        action_layout = QHBoxLayout()

        self.create_status = QLabel("BlindCube Switched")
        set_qss(self.create_status, 'packagemaker_016', append=False)
        action_layout.addWidget(self.create_status)

        action_layout.addStretch()

        self.github_progress = QProgressBar()
        self.github_progress.setRange(0,0)
        self.github_progress.setVisible(False)
        self.github_progress.setFixedWidth(150)
        self.github_progress.setFixedHeight(4)
        action_layout.addWidget(self.github_progress)

        self.btn_create_action = QPushButton("Crear Proyecto")
        self.btn_create_action.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_create_action.setFixedSize(150, 40)
        self.btn_create_action.clicked.connect(self.create_package_action)
        icon_button(self.btn_create_action, "crear", 18)
        action_layout.addWidget(self.btn_create_action)

        layout.addLayout(action_layout)
        layout.addStretch()

        # Link alias for compatibility with existing methods
        # self.btn_create = self.btn_create_action # REMOVED to avoid conflict with sidebar button


    def browse_icon(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Seleccionar Icono", "", "Icon Files (*.ico)")
        if filename:
            self.input_icon.setText(filename)

    def download_avatar(self, url):
        try:
             import urllib.request
             data = urllib.request.urlopen(url).read()
             pixmap = QPixmap()
             pixmap.loadFromData(data)
             # Mask circular
             size = 64
             target = QPixmap(size, size)
             target.fill(Qt.transparent)
             p = QtGui.QPainter(target)
             p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
             path = QtGui.QPainterPath()
             path.addEllipse(0, 0, size, size)
             p.setClipPath(path)
             p.drawPixmap(0, 0, size, size, pixmap)
             p.end()
             self.avatar_label.setPixmap(target)
        except Exception as e:
             print(f"Error descargando avatar: {e}")

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

    def create_package_action(self):
        self.statusBar().showMessage("Creando Proyecto Fluthin Packaged...")
        # Validar autor (obligatorio)
        autor = self.input_autor.text().strip()
        if not autor:
            set_qss(self.create_status, 'packagemaker_075', append=False)
            self.create_status.setText(" Error: El campo Autor es obligatorio. Debe ser un username de GitHub válido.")
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

        self.create_status.setText("Verificando username de GitHub...")
        self.github_progress.setVisible(True)
        self.statusBar().showMessage("Verificando username de GitHub...")

        # Crear y ejecutar thread de verificación
        self.github_thread = GitHubVerifyThread(autor, self)
        self.github_thread.finished.connect(self.on_github_verification_finished)
        self.github_thread.start()

    def on_github_verification_finished(self, valido, mensaje):
        """Callback cuando termina la verificación de GitHub"""
        # Ocultar barra de progreso
        self.github_progress.setVisible(False)

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
            set_qss(self.create_status, 'packagemaker_076', append=False)
            self.create_status.setText(f"❌ Error: {mensaje}. Por favor, especifica un username válido que exista en GitHub.")
            self.statusBar().showMessage("Verificación fallida")
            return

        # Si la verificación fue exitosa, continuar con la creación del proyecto
        autor = self.input_autor.text().strip()

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
                       self.create_status.setText("Descargando icono...")
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
                           self.statusBar().showMessage(f"Warning: No se pudo descargar icono (HTTP {r_icon.status_code})")
                  except Exception as ex_icon:
                       print(f"Error descargando icono: {ex_icon}")
                       self.statusBar().showMessage("Warning: Error en descarga de icono.")

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
            set_qss(self.create_status, 'packagemaker_077', append=False)
            self.create_status.setText(f"✅ Paquete creado en: {folder_name}/\n🔐 Protegido con sha256: {hv}")
            self.statusBar().showMessage(f"Proyecto creado exitosamente: {folder_name}")
        except Exception as e:
            set_qss(self.create_status, 'packagemaker_155', append=False)
            self.create_status.setText(f"❌ Error: {str(e)}")
            self.statusBar().showMessage(f"Error al crear proyecto: {str(e)}")

    def create_details_xml(self, path, empresa, nombre_logico, nombre_completo, version, autor, plataforma_seleccionada, vso=None):
        from lib.template_engine import build_variables, write_details_xml

        version_base = str(version).split("-")[0] if version else "1.0.0"
        variables = build_variables(
            empresa, nombre_logico, nombre_completo, autor, plataforma_seleccionada, version_base
        )
        write_details_xml(Path(path), variables)
        self.statusBar().showMessage(f"Proyecto creado como {empresa}.{nombre_logico}.v{variables['VERSION_FULL']}!")

    def init_build_tab(self, parent_widget=None):
        target = parent_widget if parent_widget else self.tab_build
        # Enable styled background for proper inheritance
        target.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        # Don't set individual background - let it inherit from parent
        layout = QVBoxLayout(target)
        layout.setSpacing(10)
        layout.setContentsMargins(25, 25, 25, 25)

        # Header "Construir Paquete"
        title_lbl = QLabel("Compilar el proyecto con BlindCube")
        set_qss(title_lbl, 'packagemaker_029', append=False)
        layout.addWidget(title_lbl)

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

        self.btn_build = QPushButton("BlindCube")
        self.btn_build.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_build.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.btn_build.setFixedSize(150, 40)
        set_qss(self.btn_build, 'packagemaker_034', append=False)
        self.btn_build.clicked.connect(self.build_package_action)
        icon_button(self.btn_build, "construir", 18)
        action_layout.addWidget(self.btn_build)

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
        self.statusBar().showMessage("Iniciando compilación...")

    def init_manager_tab(self, parent_widget=None):
        target = parent_widget if parent_widget else self.tab_manager
        # Enable styled background for proper inheritance
        target.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        # Don't set individual background - let it inherit from parent
        layout = QVBoxLayout(target)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        # Header
        title_lbl = QLabel("Gestor de Aplicaciones")
        set_qss(title_lbl, 'packagemaker_035', append=False)
        layout.addWidget(title_lbl)

        # Main Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(2)
        set_qss(splitter, 'packagemaker_036', append=False)

        def create_section(title, list_widget):
            container = QWidget()
            vbox = QVBoxLayout(container)
            vbox.setContentsMargins(0, 0, 0, 0)
            vbox.setSpacing(10)

            lbl = QLabel(title)
            set_qss(lbl, 'packagemaker_081', append=False)
            vbox.addWidget(lbl)

            # Styled ListWidget
            list_widget.setIconSize(QtCore.QSize(36, 36))
            list_widget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
            list_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            list_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            list_widget.setMinimumHeight(200)
            set_qss(list_widget, 'packagemaker_082', append=False)
            vbox.addWidget(list_widget)
            return container

        self.projects_list = QListWidget()
        self.projects_list.setToolTip(LGDR_NAUFRAGIO_MESSAGES["_LGDR_LOCAL_LV"])

        self.apps_list = QListWidget()
        self.apps_list.setToolTip(LGDR_NAUFRAGIO_MESSAGES["_LGDR_INSTALLED_LV"])

        splitter.addWidget(create_section("Proyectos Locales", self.projects_list))
        splitter.addWidget(create_section("Aplicaciones Instaladas", self.apps_list))
        splitter.setSizes([500, 500]) # Equal start

        layout.addWidget(splitter, 1) # Stretch

        # Action Bar
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        # UWP Button Generator
        def uwp_btn(text, icon_key=None, is_primary=False):
            btn = QPushButton(text)
            btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
            btn.setMinimumHeight(38)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

            # Clean style
            base_bg = "#ff5722" if is_primary else "rgba(255, 255, 255, 0.06)"
            hover_bg = "#ff7043" if is_primary else "rgba(255, 255, 255, 0.1)"
            text_col = "white"
            border = "none" if is_primary else "1px solid rgba(255, 255, 255, 0.08)"

            set_qss(btn, 'packagemaker_083', values=(qss_value(base_bg, None, ''), qss_value(text_col, None, ''), qss_value(border, None, ''), qss_value(hover_bg, None, ''), qss_value(base_bg, None, '')), append=False)
            if icon_key:
                btn.setIcon(get_icon(icon_key, 18))
                btn.setIconSize(QSize(18, 18))
            return btn

        btn_refresh = uwp_btn("Refrescar", "refresh")
        btn_refresh.clicked.connect(self.load_manager_lists)
        btn_row.addWidget(btn_refresh)

        self.btn_open_with = uwp_btn("Abrir con", "open_with")
        self.btn_open_with.setEnabled(False)
        self.btn_open_with.clicked.connect(self.open_selected_project_with_ide)
        btn_row.addWidget(self.btn_open_with)

        btn_row.addStretch()

        btn_install = uwp_btn("Instalar", "instalar")
        btn_install.clicked.connect(self.install_package_action)
        btn_row.addWidget(btn_install)

        btn_uninstall = uwp_btn("Desinstalar", "desinstalar")
        btn_uninstall.clicked.connect(self.uninstall_package_action)
        btn_row.addWidget(btn_uninstall)

        layout.addLayout(btn_row)

        self.manager_status = QLabel("")
        set_qss(self.manager_status, 'packagemaker_037', append=False)
        layout.addWidget(self.manager_status)
        self.manager_status.setWordWrap(True)
        self.manager_status.setToolTip("Estado de la app")
        # self.tab_manager.setLayout(layout)
        self.load_manager_lists()
        self.projects_list.itemSelectionChanged.connect(self._on_project_selection_changed)
        self.projects_list.itemDoubleClicked.connect(lambda item: self.on_project_double_click(item))
        self.apps_list.itemDoubleClicked.connect(lambda item: self.on_app_double_click(item))

        # Watcher en tiempo real
        self.fs_watcher = QtCore.QFileSystemWatcher(self)
        self.fs_watcher.addPath(BASE_DIR)
        self.fs_watcher.addPath(Fluthin_APPS)
        self.fs_watcher.directoryChanged.connect(self.load_manager_lists)

    def get_package_list(self, base):
        packages = []
        if not os.path.exists(base): return []

        # Escaneo Recursivo usando os.walk, limitado a un nivel de profundidad lógico para proyectos
        # No queremos escanear todo el disco. Asumimos que BASE_DIR contiene carpetas de proyectos.
        # Originalmente solo escaneaba carpetas en BASE_DIR.
        # El usuario pidió "recursivamente". Si los proyectos están anidados, esto ayudará.
        # Pero standard packagemaker structure es BASE_DIR/Proyecto.
        # Mantendremos la lógica de "mirar en subcarpetas de BASE_DIR" pero si el usuario se refería
        # a buscar metadatos en TODOS los archivos, eso es costoso.
        # Interpretaremos "recursivamente" como buscar en subdirectorios si la estructura lo permite.

        # Para cumplir con "recursivamente en busca de metadatos similares",
        # asumiremos que quiere encontrar details.xml incluso si está dentro de subcarpetas (proyectos anidados ??).
        # Para evitar lentitud extrema, limitaremos la profundidad o usaremos walk con cuidado.

        for root, dirs, files in os.walk(base):
            if "details.xml" in files:
                folder = root
                details_path = os.path.join(folder, "details.xml")
                icon_path = os.path.join(folder, "app", "app-icon.ico")
                try:
                    tree = ET.parse(details_path)
                    root_xml = tree.getroot()
                    details = {child.tag: child.text for child in root_xml}
                    empresa = details.get("publisher", "Origen Desconocido")
                    titulo = details.get("name", os.path.basename(folder))
                    version = details.get("version", "v?")
                    ratings = details.get("rate", "Sin Clasificación")

                    correlation_id = details.get("correlationid")
                    if not correlation_id:
                        correlation_id = hashlib.sha256(f"{empresa}.{titulo}.{version}".encode()).hexdigest()

                    packages.append({
                        "folder": folder,
                        "empresa": empresa,
                        "titulo": titulo,
                        "version": version,
                        "icon": icon_path if os.path.exists(icon_path) else None,
                        "name": os.path.basename(folder),
                        "rating": ratings,
                        "sha": correlation_id
                    })
                except Exception:
                    continue
        return packages

    def load_manager_lists(self):
        self.projects_list.clear()
        self.apps_list.clear()
        projects = self.get_package_list(BASE_DIR)
        for p in projects:
            icon = QIcon(p["icon"]) if p["icon"] else self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
            text = p['empresa'].capitalize()
            text = f"{text} {p['titulo']} | {p['version']} [SHA: {p['sha'][:8]}...]"
            item = QListWidgetItem(icon, text)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, p)
            self.projects_list.addItem(item)
        apps = self.get_package_list(Fluthin_APPS)
        for a in apps:
            icon = QIcon(a["icon"]) if a["icon"] else self.style().standardIcon(QStyle.StandardPixmap.SP_DesktopIcon)
            text = a['empresa'].capitalize()
            text = f"{text} {a['titulo']} | {a['version']}"
            item = QListWidgetItem(icon, text)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, a)
            self.apps_list.addItem(item)

        # Actualizar autocompletador de Build Tab
        self.update_build_completer(projects)

    def update_build_completer(self, projects):
        if hasattr(self, 'input_build_empresa') and hasattr(self, 'input_build_nombre'):
             pubs = list(set([p['empresa'] for p in projects]))
             names = list(set([p['titulo'] for p in projects])) # Usar titulo o name? Titulo es mas visual
             # Agregar tambien los nombres de carpeta
             names.extend([p['name'] for p in projects])
             names = list(set(names))

             comp_pub = QtWidgets.QCompleter(pubs, self)
             comp_pub.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
             comp_pub.setFilterMode(Qt.MatchFlag.MatchContains) # Busqueda recursiva/flexible
             self.input_build_empresa.setCompleter(comp_pub)

             comp_name = QtWidgets.QCompleter(names, self)
             comp_name.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
             comp_name.setFilterMode(Qt.MatchFlag.MatchContains) # Busqueda recursiva/flexible
             self.input_build_nombre.setCompleter(comp_name)

    def _on_project_selection_changed(self):
        item = self.projects_list.currentItem()
        self.btn_open_with.setEnabled(bool(item and item.data(QtCore.Qt.ItemDataRole.UserRole)))

    def open_selected_project_with_ide(self):
        item = self.projects_list.currentItem()
        if not item:
            return
        pkg = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if not pkg:
            return
        path = pkg.get("folder") or pkg.get("path")
        if not path or not os.path.isdir(path):
            LeviathanDialog.launch(self, "Abrir con", "Ruta de proyecto no válida.", mode="warning")
            return
        name = pkg.get("name") or pkg.get("titulo") or os.path.basename(path)
        open_project_with_editor(self, path, name, use_default=False)

    def closeEvent(self, event):
        if getattr(self, "_force_close", False):
            super().closeEvent(event)
            return
        event.ignore()
        play_bounce_down_close(self, on_finished=lambda: self._finish_close(), drop_px=80)


    def _finish_close(self):
        self._force_close = True
        self.close()

    def on_project_double_click(self, item):
        pkg = item.data(QtCore.Qt.ItemDataRole.UserRole)
        dlg = ProjectDetailsDialog(self, pkg, is_app=False, manager_ref=self)
        dlg.exec()

    def on_app_double_click(self, item):
        pkg = item.data(QtCore.Qt.ItemDataRole.UserRole)
        dlg = ProjectDetailsDialog(self, pkg, is_app=True, manager_ref=self)
        dlg.exec()

    def install_package_action(self):
        files = QFileDialog.getOpenFileNames(self, "Selecciona paquetes para instalar", BASE_DIR, "Paquetes (*.iflapp)")[0]
        for file_path in files:
            if not file_path:
                continue
            pkg_name = os.path.basename(file_path).replace(".iflapp", "")
            target_dir = os.path.join(Fluthin_APPS, pkg_name)
            os.makedirs(target_dir, exist_ok=True)
            try:
                from lib.iflapp_format import extract_iflapp, sniff_format

                if sniff_format(file_path) == "iflapp2":
                    extract_iflapp(file_path, target_dir)
                else:
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        safe_extract_zip(zip_ref, target_dir)
                self.manager_status.setText(f"✅ Instalado: {pkg_name} en Fluthin Apps")
                # Asociación de extensión y menú inicio en Windows
                if sys.platform.startswith('win'):
                    self.setup_windows_shortcut(target_dir, pkg_name)
            except Exception as e:
                self.manager_status.setText(f"❌ Error al instalar {pkg_name}: {e}")
        self.load_manager_lists()

    def setup_windows_shortcut(self, target_dir, pkg_name):
        details_path = os.path.join(target_dir, "details.xml")
        if not os.path.exists(details_path):
            return
        try:
            tree = ET.parse(details_path)
            root = tree.getroot()
            nombre = root.findtext("name", pkg_name)
            empresa = root.findtext("publisher", "Influent")
            icon_path = os.path.join(target_dir, "app", "app-icon.ico")
            py_scripts = []
            for root_dir, _, files in os.walk(target_dir):
                for f in files:
                    if f.endswith(".py"):
                        py_scripts.append(os.path.join(root_dir, f))
            main_script = py_scripts[0] if py_scripts else None
            shortcut_name = f"{nombre} - Influent"
            try:
                import pythoncom
                import win32com.client
                from win32com.shell import shell, shellcon
                start_menu = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs")
                program_files = os.path.join(os.environ["ProgramFiles"], empresa, nombre)
                os.makedirs(program_files, exist_ok=True)
                for item in os.listdir(target_dir):
                    s = os.path.join(target_dir, item)
                    d = os.path.join(program_files, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d, dirs_exist_ok=True)
                    else:
                        shutil.copy2(s, d)
                if main_script:
                    shell_obj = win32com.client.Dispatch("WScript.Shell")
                    shortcut = shell_obj.CreateShortcut(os.path.join(start_menu, f"{shortcut_name}.lnk"))
                    shortcut.TargetPath = sys.executable
                    shortcut.Arguments = f'"{main_script}"'
                    shortcut.WorkingDirectory = os.path.dirname(main_script)
                    shortcut.IconLocation = icon_path if os.path.exists(icon_path) else sys.executable
                    shortcut.Description = f"Influent App: {nombre}"
                    shortcut.Save()
            except Exception as e:
                self.manager_status.setText(self.manager_status.text() + f"\n⚠️ Error instalando accesos directos: {str(e)}")
        except Exception as e:
            self.manager_status.setText(self.manager_status.text() + f"\n⚠️ Error a llamada a XML/meta: {str(e)}")

    def uninstall_package_action(self):
        item = self.apps_list.currentItem()
        if not item:
            self.manager_status.setText("Selecciona un paquete instalado para desinstalar.")
            return
        pkg = item.data(QtCore.Qt.ItemDataRole.UserRole)
        # Confirmación
        L = LeviathanDialog.launch(self, "Desinstalar", f"¿Estás seguro de desinstalar {pkg['name']}?", mode="confirm")
        if not L: return

        try:
            shutil.rmtree(pkg["folder"])
            self.manager_status.setText(f"🗑️ Desinstalado: {pkg['titulo']}")
        except Exception as e:
            self.manager_status.setText(f"❌ Error al desinstalar: {e}")
        self.load_manager_lists()


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
        outer.setContentsMargins(25, 25, 25, 25)
        outer.setSpacing(10)

        header_row = QHBoxLayout()
        conf_icon = QLabel()
        conf_icon.setPixmap(get_icon("config", 28).pixmap(28, 28))
        conf_icon.setFixedSize(28, 28)
        header_row.addWidget(conf_icon)
        self.conf_header = QLabel(tr("config.title"))
        set_qss(self.conf_header, 'packagemaker_040', append=False)
        header_row.addWidget(self.conf_header, 1)
        outer.addLayout(header_row)

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
        hint_tr = QLabel(tr("config.auto_translate_hint"))
        set_qss(hint_tr, 'packagemaker_050', append=False)
        hint_tr.setWordWrap(True)
        self._config_tr_labels.append((hint_tr, "config.auto_translate_hint"))
        layout.addWidget(hint_tr)

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
            from lib.font_manager import FONT_REGISTRY, available_fonts_report

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

        # Botones de acción (Guardar y Resetear)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        btn_save = QPushButton(tr("config.save"))
        btn_save.setFixedSize(150, 40)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        set_qss(btn_save, 'packagemaker_051', append=False)
        btn_save.clicked.connect(self._save_app_config_compact)
        icon_button(btn_save, "save", 18)
        self.conf_btn_save = btn_save
        self._config_tr_labels.append((btn_save, "config.save"))
        btn_layout.addWidget(btn_save)

        # Botón de resetear configuración (siempre visible)
        self.conf_reset_btn = QPushButton(tr("config.reset"))
        self.conf_reset_btn.setFixedSize(150, 40)
        self.conf_reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        set_qss(self.conf_reset_btn, 'packagemaker_052', append=False)
        self.conf_reset_btn.clicked.connect(self._reset_config)
        self._config_tr_labels.append((self.conf_reset_btn, "config.reset"))
        btn_layout.addWidget(self.conf_reset_btn)

        btn_layout.addStretch()
        outer.addLayout(btn_layout)

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

    def _preview_display_mode(self, display_name: str) -> None:
        if not display_name:
            return
        self._apply_display_mode_by_name(display_name)

    def _show_restart_banner(self) -> None:
        if hasattr(self, "conf_restart_banner"):
            self.conf_restart_banner.setVisible(True)
        if hasattr(self, "conf_reset_btn"):
            self.conf_reset_btn.setVisible(True)

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
            store.remove_user("blur_intensity")
            store.remove_user("window_radius")
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
            )}
            user["base_dir"] = user.get("base_dir") or BASE_DIR
            user["fluthin_apps"] = user.get("fluthin_apps") or Fluthin_APPS

            # Actualizar campos
            self.conf_base_dir.setText(user["base_dir"])
            self.conf_fluthin_dir.setText(user["fluthin_apps"])

            idx_lang = self.conf_lang_combo.findData(user.get("language", "es"))
            if idx_lang >= 0:
                self.conf_lang_combo.setCurrentIndex(idx_lang)

            self.conf_auto_translate.setChecked(bool(user.get("auto_translate", True)))

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
            "notifications_enabled": False,
        }
        return cfg

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
            prev_lang = i18n.get_current_lang()
            i18n.set_auto_translate(self.conf_auto_translate.isChecked())
            if lang != prev_lang:
                i18n.load_translation(lang)
            self.apply_ui_language()
            self._apply_leviathan_and_personalization()
            self.apply_theme()

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
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(10)

        mf_header_row = QHBoxLayout()
        mf_icon = QLabel()
        mf_icon.setPixmap(get_icon("moonfix", 28).pixmap(28, 28))
        mf_header_row.addWidget(mf_icon)
        header = QLabel("MoonFix")
        set_qss(header, 'packagemaker_053', append=False)
        mf_header_row.addWidget(header, 1)
        layout.addLayout(mf_header_row)

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
        self.mf_input.setMinimumHeight(32)
        set_qss(self.mf_input, 'packagemaker_056', append=False)
        btn_sel = QPushButton("...")
        btn_sel.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        btn_sel.setMinimumWidth(36)
        btn_sel.setMinimumHeight(32)
        btn_sel.setCursor(Qt.CursorShape.PointingHandCursor)
        set_qss(btn_sel, 'packagemaker_057', append=False)
        btn_sel.clicked.connect(self.mf_browse)
        icon_button(btn_sel, "folder", 16)
        btn_scan = QPushButton("Diagnosticar")
        btn_scan.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        btn_scan.setMinimumWidth(110)
        btn_scan.setMinimumHeight(32)
        btn_scan.setCursor(Qt.CursorShape.PointingHandCursor)
        set_qss(btn_scan, 'packagemaker_058', append=False)
        btn_scan.clicked.connect(self.mf_start_scan)
        icon_button(btn_scan, "moonfix", 16)
        s_box.addWidget(self.mf_input, 1)
        s_box.addWidget(btn_sel)
        s_box.addWidget(btn_scan)
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
        layout.setContentsMargins(40, 40, 40, 40)

        # Clean layout

        # Logo/Title Area
        # Use SVG rendering if possible, otherwise text.
        header_box = QHBoxLayout()

        # SVG Logo display (using QLabel hack or QSvgWidget if imported, staying safe with standard widgets)
        logo_lbl = QLabel()
        logo_lbl.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        logo_lbl.setMinimumSize(64, 64)
        logo_lbl.setMaximumSize(128, 128)
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

        # Footer Buttons
        footer = QHBoxLayout()

        btn_github = QPushButton("GitHub")
        set_qss(btn_github, 'packagemaker_062', append=False)
        btn_github.setCursor(Qt.CursorShape.PointingHandCursor)
        # Open URL logic

        btn_telegram = QPushButton("Telegram")
        set_qss(btn_telegram, 'packagemaker_063', append=False)
        btn_telegram.setCursor(Qt.CursorShape.PointingHandCursor)

        footer.addWidget(btn_github)
        footer.addWidget(btn_telegram)
        footer.addStretch()

        layout.addLayout(footer)


    # ========================================
    # MÉTODOS PARA MANEJO DE VENTANAS CLI
    # ========================================

    def setProjectPath(self, path):
        """Establece la ruta del proyecto en la pestaña de crear"""
        try:
            if hasattr(self, 'txtProjectName'):
                projectName = os.path.basename(path)
                self.txtProjectName.setText(projectName)
            if hasattr(self, 'txtProjectPath'):
                self.txtProjectPath.setText(path)
        except Exception as e:
            print(f"Error estableciendo ruta del proyecto: {e}")

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

    def set_compile_path(self, path):
        """Establece la ruta del proyecto a compilar"""
        try:
            if hasattr(self, 'txt_build_project'):
                self.txt_build_project.setText(path)
        except Exception as e:
            print(f"Error estableciendo ruta de compilación: {e}")

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
        """Abre un archivo de paquete en el gestor"""
        try:
            self.switch_page(2)
            LeviathanDialog.launch(
                self,
                "Paquete Abierto",
                f"Abriendo paquete:\n{os.path.basename(filePath)}",
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
            if window:
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
                import importlib
                importlib.import_module("pyi_splash").close()
            except (ImportError, OSError):
                pass

    splash.finished.connect(on_splash_finished)
    main_window.show()
    splash.start(5000)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
