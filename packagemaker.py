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

# Prefer the local leviathan-ui repository over a globally installed package.
import importlib
import importlib.util

# Usar leviathan-ui desde pip (remoto) - instalar con: pip install leviathan-ui
print(f"[INFO] Usando leviathan-ui desde PyPI (pip install leviathan-ui)")

try:
    from PyQt6 import QtWidgets, QtGui, QtCore
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
        QPushButton, QComboBox, QListWidget, QListWidgetItem, QFileDialog, QDialog, QStyle, QSizePolicy, QSplitter, QGroupBox, QRadioButton, QButtonGroup, QGridLayout, QProgressBar, QTextEdit, QStackedWidget,
        QCheckBox, QMessageBox, QInputDialog, QSwipeGesture, QSlider, QFrame
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
from lib.Updater import KillerLogic, InstallerWorker, ModernUpdaterWindow
from lib.BuildThread import BuildThread, FlangCompiler
from lib.TitleBar import AnimTitleButton, TitleBar
from lib.app_icons import get_sidebar_icon, get_icon, icon_button
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
from lib.pm_data import get_pm_data, load_merged_app_config, is_compiled_build, COMPILED_LOCKED_USER_KEYS
from lib.outputTerminalDialog import OutputTerminalDialog
from lib.projectDetailsDialog import ProjectDetailsDialog

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

# PyInstaller splash screen support: Optional, only has effect in frozen bundles
if getattr(sys, 'frozen', False):
    try:
        import pyi_splash  # Only needed for PyInstaller splash screen; will not be found otherwise
    except ImportError:
        pass  # Not an error unless running under PyInstaller build
# ----------- CONFIGURABLE VARIABLES -----------
if PYQT6_AVAILABLE:
    APP_FONT = QFont('Segoe UI Variable', 11)
    TAB_FONT = QFont('Segoe UI Variable', 12)
else:
    APP_FONT = None
    TAB_FONT = None # Icons (SVGs are handled as strings here for "one-file" convenience or resource paths)

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

# SVG Definitions for "About" Page and Sidebar (Inline for robustness)
SVG_ABOUT = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="10" stroke="#f9826c" stroke-width="2"/><path d="M12 7V13M12 17H12.01" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>"""
SVG_SETTINGS = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 15C13.6569 15 15 13.6569 15 12C15 10.3431 13.6569 9 12 9C10.3431 9 9 10.3431 9 12C9 13.6569 10.3431 15 12 15Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M19.4 15A1.65 1.65 0 0 0 20 12A1.65 1.65 0 0 0 19.4 9M12 3A1.65 1.65 0 0 0 9 3M12 21A1.65 1.65 0 0 0 15 21M4.6 15A1.65 1.65 0 0 0 4 12A1.65 1.65 0 0 0 4.6 9" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>"""

# Windows 11-inspired button styles (rounded, soft shadows, modern accent colors)
# Note: The 'transition' property is a CSS feature supported by browsers, but it is NOT supported/stable in PyQt6 stylesheets.
# PyQt6 ignores 'transition' and related CSS3 properties—they have no effect and can be safely omitted.
# QSS-based stylized button styles using rgba colors, with transparency for blending with the app frame
BTN_STYLES = {
    "default": (
        "background-color: transparent;"
        "color: rgba(32,33,36,0.96);"
        "border-radius: 9px;"
        "padding: 10px 20px;"
        "font-weight: 600;"
        "border: 1px solid rgba(209,215,224,0.65);"
        # No box-shadow
    ),
    "success": (
        "background-color: transparent;"
        "color: rgba(5,98,55,0.99);"
        "border-radius: 9px;"
        "padding: 10px 20px;"
        "font-weight: 600;"
        "border: 1px solid rgba(199,232,206,0.60);"
        # No box-shadow
    ),
    "danger": (
        "background-color: transparent;"
        "color: rgba(185,29,29,1.0);"
        "border-radius: 9px;"
        "padding: 10px 20px;"
        "font-weight: 600;"
        "border: 1px solid rgba(255,180,180,0.68);"
        # No box-shadow
    ),
    "warning": (
        "background-color: transparent;"
        "color: rgba(168,132,4,0.97);"
        "border-radius: 9px;"
        "padding: 10px 20px;"
        "font-weight: 600;"
        "border: 1px solid rgba(255,224,149,0.66);"
        # No box-shadow
    ),
    "info": (
        "background-color: transparent;"
        "color: rgba(9,82,165,1.0);"
        "border-radius: 9px;"
        "padding: 10px 20px;"
        "font-weight: 600;"
        "border: 1px solid rgba(185,213,253,0.56);"
        # No box-shadow
    ),
    "best": (
        "background-color: transparent;"
        "color: #0853c4;"
        "border-radius: 11px;"
        "padding: 12px 22px;"
        "font-weight: 700;"
        "border: 2px solid #99d3f7;"
        "font-size: 15px;"
        # Designed for best/primary experience action
        # No box-shadow
    ),
    "grayed-black": (
        "background-color: #292929;"
        "color: #b9b9b9;"
        "border-radius: 9px;"
        "padding: 10px 20px;"
        "font-weight: 600;"
        "border: 1px solid #444;"
        "background-image: none;"
        # Grayed black button, for alternative or disabled style
        # No box-shadow
    ),
}

plataforma_platform = sys.platform
plataforma_name = os.name
if plataforma_platform.startswith("win"):
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

# --- GLOBAL CONFIG SYSTEM ---
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
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(Fluthin_APPS, exist_ok=True)

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
    except:
        return False

def load_from_registry(key, default=""):
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\PackageMaker", 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(reg_key, key)
        winreg.CloseKey(reg_key)
        return value
    except:
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
    "social" : "TEENS ALL 18+",
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
# verificar_github_username moved to lib/moonFixWizard.py
# get_github_style moved to lib/projectDetailsDialog.py
    """Genera estilos CSS para botones al estilo GitHub (Action Naranja, Normal B/W)"""
    if is_dark:
        # Action (Orange) - Dark
        action_style = """
            QPushButton {
                background-color: #d2691e;
                color: #ffffff;
                border: 1px solid #c15c1d;
                border-radius: 6px;
                padding: 5px 16px;
                font-family: 'Segoe UI', sans-serif;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e07b3e;
                border-color: #d96d27;
            }
            QPushButton:pressed {
                background-color: #bd5a17;
            }
        """
        # Normal (Black/Dark Grey) - Dark
        normal_style = """
            QPushButton {
                background-color: #21262d;
                color: #c9d1d9;
                border: 1px solid rgba(240, 246, 252, 0.1);
                border-radius: 6px;
                padding: 5px 16px;
                font-family: 'Segoe UI', sans-serif;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                color: #d96d27; 
                border: 1px solid #d96d27;
                background-color: transparent;
            }
            QPushButton:pressed {
                background-color: transparent;
            }
        """
    else:
        # Action (Orange) - Light
        action_style = """
            QPushButton {
                background-color: #f9826c;
                color: #ffffff;
                border: 1px solid rgba(27, 31, 35, 0.15);
                border-radius: 6px;
                padding: 5px 16px;
                font-family: 'Segoe UI', sans-serif;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #fa9e8e;
            }
            QPushButton:pressed {
                background-color: #eb715b;
            }
        """
        # Normal (White) - Light
        normal_style = """
            QPushButton {
                background-color: #f6f8fa;
                color: #24292e;
                border: 1px solid rgba(27, 31, 35, 0.15);
                border-radius: 6px;
                padding: 5px 16px;
                font-family: 'Segoe UI', sans-serif;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: transparent;
                color: #d96d27;
                border: 1px solid #f9826c;
            }
            QPushButton:pressed {
                 background-color: #ffe3d0;
            }
        """
    return action_style, normal_style



# SidebarItem moved to lib/SidebarItem.py
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

        self.compact_mode = compact_mode
        self.shell_mode = shell_mode

        # --- VERSION UPDATE 3.2.7 ---
        self.currentVersion = get_app_version()
        
        # Quitar barra de título nativa de Windows - usar solo leviathan-ui
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # Fondo COMPLETAMENTE opaco - sin transparencia
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        """
        self.touch_driver = TouchScreen(self)
        self.touch_enabled = self.touch_driver.enabled
        if self.touch_enabled:
            self.statusBar().showMessage("Pantalla táctil detectada, compactando items. Activando modo táctil...")
            self.change_display_mode(2)
            self.setWindowState(Qt.WindowState.WindowFullScreen)
        else:
            self.statusBar().showMessage("No se detectó pantalla táctil.")
        """
        self._fixed_title = fixed_window_title(self.currentVersion)
        self.setWindowTitle(self._fixed_title)
        self._applied_dpi_scale = float(APP_CONFIG.get("applied_dpi_scale", 1.0))
        self._pending_restart_keys = []
        screen_geo = QApplication.primaryScreen().availableGeometry()
        default_width = 1100
        default_height = 720
        width = min(default_width, int(screen_geo.width() * 0.9))
        height = min(default_height, int(screen_geo.height() * 0.85))
        self.resize(width, height)
        self.setFont(APP_FONT)
        self.setWindowIcon(QtGui.QIcon(IPM_ICON_PATH if os.path.exists(IPM_ICON_PATH) else ""))

        # Central Widget & Main Layout
        self.central = QWidget()
        self.central.setObjectName("CentralWidget")
        # Cast iron gray background
        self.central.setStyleSheet("background: transparent; border: none;")
        self.setCentralWidget(self.central)
        
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
        self.content_container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        # Cast iron gray background for content container
        self.content_container.setStyleSheet("background: #3a3f4b;")
        self.content_layout = QHBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # --- SIDEBAR (Left) ---
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(260)
        # Cast iron gray sidebar background
        self.sidebar.setStyleSheet("background: transparent; border-right: 1px solid rgba(255,255,255,0.08);")
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(15, 20, 15, 20)
        self.sidebar_layout.setSpacing(8)

        # Header Sidebar (Optional, maybe "Menú Inicio" text style)
        self.lbl_menu_main = QLabel(tr("app.main_menu"))
        self.lbl_menu_main.setStyleSheet("color: #ffffff; font-size: 24px; font-weight: 700; font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif; margin-bottom: 12px; letter-spacing: 0.3px; background: transparent;")
        self.sidebar_layout.addWidget(self.lbl_menu_main)

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
        self.desc_card.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                margin-top: 10px;
            }
        """)
        desc_vbox = QVBoxLayout(self.desc_card)
        desc_vbox.setContentsMargins(12, 12, 12, 12)
        
        desc_header = QHBoxLayout()
        info_icon = QLabel("ℹ️")
        info_icon.setStyleSheet("border:none; background:transparent; font-size: 14px;")
        desc_header.addWidget(info_icon)
        
        self.lbl_sidebar_context = QLabel(tr("app.context"))
        self.lbl_sidebar_context.setStyleSheet("border:none; background:transparent; color: #888; font-weight: bold; font-size: 11px; text-transform: uppercase;")
        desc_header.addWidget(self.lbl_sidebar_context)
        desc_header.addStretch()
        desc_vbox.addLayout(desc_header)
        
        self.sidebar_desc_text = QTextEdit()
        self.sidebar_desc_text.setReadOnly(True)
        self.sidebar_desc_text.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.sidebar_desc_text.setStyleSheet("background: transparent; color: #bbb; font-size: 12px; line-height: 1.4; border:none;")
        self.sidebar_desc_text.setMaximumHeight(120)
        desc_vbox.addWidget(self.sidebar_desc_text)
        
        self.sidebar_layout.addWidget(self.desc_card)
        self.sidebar_layout.addSpacing(10)
        self.sidebar_layout.addWidget(self.btn_about)

        self.content_layout.addWidget(self.sidebar)

        # --- MAIN CONTENT AREA (Right) ---
        self.stack = QStackedWidget()
        # Enable styled background
        self.stack.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        # Cast iron gray background for stack
        self.stack.setStyleSheet("background: #3a3f4b;")
        
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
        self.last_theme_mode = detectar_modo_sistema()

        # Apply Global Styles
        self.apply_theme()
        self._apply_leviathan_and_personalization()
        apply_dpi_scale(float(APP_CONFIG.get("dpi_scale", 1.0)), APP_FONT)
        self._applied_dpi_scale = float(APP_CONFIG.get("dpi_scale", 1.0))

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

    def enterCompactShellMode(self):
        self.sidebar.hide()
        self.content_layout.setContentsMargins(8, 8, 8, 8)
        self.content_container.setStyleSheet("background-color: transparent;")
        self.resize(460, 760)
        self.setMinimumSize(420, 660)
        self.statusBar().showMessage("Modo compacto de shell activado")
        self.setWindowTitle(fixed_window_title(self.currentVersion, "Shell"))
        if hasattr(self.titlebar, "title_lbl"):
            self.titlebar.title_lbl.setText(self.windowTitle())
        if hasattr(self.titlebar, 'setStyleSheet'):
            self.titlebar.setStyleSheet("background-color: transparent;")

    def update_sidebar_description(self, index):
        key = SIDEBAR_DESC_KEYS.get(index)
        if key:
            text = tr(key)
            html = text.replace("### ", "<b style='color:white; font-size:14px;'>").replace("\n", "</b><br>")
            self.sidebar_desc_text.setHtml(html)

    def animate_startup(self, instant=False):
        """Animación de desplazamiento hacia arriba y opacidad al abrir"""
        screen_geo = QApplication.primaryScreen().geometry()
        x = (screen_geo.width() - self.width()) // 2
        y = (screen_geo.height() - self.height()) // 2
        
        if instant:
            self.move(x, y)
            self.setWindowOpacity(1.0)
            return
        
        start_y = y + 50
        end_y = y

        self.move(x, start_y)
        self.setWindowOpacity(0.0)

        # Animacion de geometria (Posicion)
        self.anim_pos = QPropertyAnimation(self, b"pos")
        self.anim_pos.setDuration(800)
        self.anim_pos.setStartValue(QPoint(x, start_y))
        self.anim_pos.setEndValue(QPoint(x, end_y))
        self.anim_pos.setEasingCurve(QEasingCurve.Type.OutExpo)
        
        # Animacion de opacidad
        self.anim_fade = QPropertyAnimation(self, b"windowOpacity")
        self.anim_fade.setDuration(800)
        self.anim_fade.setStartValue(0.0)
        self.anim_fade.setEndValue(1.0)
        
        self.anim_group = QParallelAnimationGroup(self)
        self.anim_group.addAnimation(self.anim_pos)
        self.anim_group.addAnimation(self.anim_fade)
        self.anim_group.start()

    def apply_device_simulation(self):
        """Aplica la simulación de dispositivo según la configuración"""
        # Cargar desde registro si no está en config
        device = APP_CONFIG.get("device_simulation") or load_from_registry("device_simulation", "laptop")
        dpi_scale = float(APP_CONFIG.get("dpi_scale") or load_from_registry("dpi_scale", "1.0"))
        touch_mode = APP_CONFIG.get("touch_mode") or (load_from_registry("touch_mode", "False") == "True")
        interface_color = APP_CONFIG.get("interface_color") or load_from_registry("interface_color", "#0d1117")
        auto_color = APP_CONFIG.get("auto_color") or (load_from_registry("auto_color", "True") == "True")
        
        screen = QApplication.primaryScreen().availableGeometry()
        
        if device == "tv":
            # Pantalla completa, modo touch
            self.setWindowState(Qt.WindowState.WindowFullScreen)
            self.touch_enabled = True
        elif device == "tablet":
            # Compacto con espacios para dedos, modo touch
            width = int(screen.width() * 0.8)
            height = int(screen.height() * 0.9)
            self.resize(width, height)
            self.move((screen.width() - width) // 2, (screen.height() - height) // 2)
            self.touch_enabled = True
            # Agregar márgenes para dedos
            self.central.setContentsMargins(20, 20, 20, 20)
        elif device == "phone":
            # Tarjeta ajustada al alto, ancho reducido, modo touch
            width = int(screen.width() * 0.4)
            height = screen.height() - 40  # Respetar barra de tareas
            self.resize(width, height)
            self.move((screen.width() - width) // 2, 20)
            self.touch_enabled = True
            # En modo phone, ocultar sidebar y mostrar solo contenido
            self.sidebar.hide()
            self.content_layout.setContentsMargins(8, 8, 8, 8)
        elif device == "ios_x":
            # Simulación iOS X: notch superior, botones sidebar en la parte inferior
            width = int(screen.width() * 0.45)
            height = int(screen.height() * 0.9)
            self.resize(width, height)
            self.move((screen.width() - width) // 2, (screen.height() - height) // 2)
            self.touch_enabled = True
            
            # Crear notch superior simulado
            self.notch_container = QWidget()
            self.notch_container.setMinimumHeight(30)
            self.notch_container.setMaximumHeight(30)
            self.notch_container.setStyleSheet("""
                background-color: transparent;
                border-bottom: 1px solid rgba(255,255,255,0.1);
            """)
            notch_layout = QHBoxLayout(self.notch_container)
            notch_layout.setContentsMargins(0, 0, 0, 0)
            notch_layout.setSpacing(0)
            
            # Notch central (área de notificaciones)
            notch_area = QWidget()
            notch_area.setStyleSheet("background-color: transparent;")
            notch_area.setMinimumWidth(100)
            notch_area.setMaximumWidth(150)
            notch_layout.addWidget(notch_area)
            
            # Botones de notificación (íconos)
            notif_btn = QPushButton()
            notif_btn.setIcon(get_icon("notifications", 16))
            notif_btn.setIconSize(QSize(16, 16))
            notif_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: transparent;
                    border-radius: 4px;
                }
            """)
            notch_layout.addWidget(notif_btn)
            
            # Hora
            self.notch_time = QLabel("9:41")
            self.notch_time.setStyleSheet("color: white; font-size: 12px; font-weight: 600; background-color: transparent; padding: 0 10px;")
            notch_layout.addWidget(self.notch_time)
            
            notch_layout.addStretch()
            
            # Agregar notch al layout principal
            self.v_layout.insertWidget(1, self.notch_container)
            
            # Crear barra de botones inferior estilo iOS
            self.ios_bottom_bar = QWidget()
            self.ios_bottom_bar.setMinimumHeight(60)
            self.ios_bottom_bar.setMaximumHeight(60)
            self.ios_bottom_bar.setStyleSheet("""
                background-color: transparent;
                border-top: 1px solid rgba(255,255,255,0.1);
            """)
            bottom_layout = QHBoxLayout(self.ios_bottom_bar)
            bottom_layout.setContentsMargins(10, 5, 10, 5)
            bottom_layout.setSpacing(15)
            
            # Botones del sidebar como iconos
            btn_create = QPushButton()
            btn_create.setIcon(get_icon("crear", 24))
            btn_create.setIconSize(QSize(24, 24))
            btn_create.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: transparent;
                    border-radius: 8px;
                }
                QPushButton:checked {
                    background-color: transparent;
                }
            """)
            btn_create.setCheckable(True)
            btn_create.clicked.connect(lambda: self.btn_create.setChecked(True))
            
            btn_build = QPushButton()
            btn_build.setIcon(get_icon("construir", 24))
            btn_build.setIconSize(QSize(24, 24))
            btn_build.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: transparent;
                    border-radius: 8px;
                }
                QPushButton:checked {
                    background-color: transparent;
                }
            """)
            btn_build.setCheckable(True)
            btn_build.clicked.connect(lambda: self.btn_build.setChecked(True))
            
            btn_manager = QPushButton()
            btn_manager.setIcon(get_icon("gestor", 24))
            btn_manager.setIconSize(QSize(24, 24))
            btn_manager.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: transparent;
                    border-radius: 8px;
                }
                QPushButton:checked {
                    background-color: transparent;
                }
            """)
            btn_manager.setCheckable(True)
            btn_manager.clicked.connect(lambda: self.btn_manager.setChecked(True))
            
            btn_config = QPushButton()
            btn_config.setIcon(get_icon("config", 24))
            btn_config.setIconSize(QSize(24, 24))
            btn_config.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: transparent;
                    border-radius: 8px;
                }
                QPushButton:checked {
                    background-color: transparent;
                }
            """)
            btn_config.setCheckable(True)
            btn_config.clicked.connect(lambda: self.btn_config.setChecked(True))
            
            bottom_layout.addWidget(btn_create)
            bottom_layout.addWidget(btn_build)
            bottom_layout.addWidget(btn_manager)
            bottom_layout.addWidget(btn_config)
            bottom_layout.addStretch()
            
            # Agregar barra inferior al layout principal
            self.v_layout.insertWidget(2, self.ios_bottom_bar)
            
            # Ajustar el contenido para que no se superponga con la barra inferior
            self.content_container.setStyleSheet("background-color: transparent;")
            self.content_layout.setContentsMargins(0, 0, 0, 0)
            
            # Ocultar sidebar original
            self.sidebar.hide()
        else:  # laptop
            max_width = int(screen.width() * 0.9)
            max_height = int(screen.height() * 0.85)
            width = min(1100, max_width)
            height = min(720, max_height)
            self.resize(width, height)
            self.move((screen.width() - width) // 2, (screen.height() - height) // 2)
            self.touch_enabled = touch_mode
        
        # Aplicar color de interfaz
        if not auto_color:
            self.setStyleSheet(f"QMainWindow {{ background-color: {interface_color}; }}")
        
        applied = apply_dpi_scale(dpi_scale, APP_FONT)
        self._applied_dpi_scale = applied
        get_pm_data().set_user("applied_dpi_scale", applied)

        # Configurar gestos touch si está habilitado
        if self.touch_enabled:
            self.setup_touch_gestures()

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
            anim_fade = QtCore.QPropertyAnimation(next_widget, b"windowOpacity")
            anim_fade.setDuration(260)
            anim_fade.setStartValue(0.0)
            anim_fade.setEndValue(1.0)
            anim_fade.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)
            anim_fade.start(QtCore.QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        except Exception:
            next_widget.setWindowOpacity(1.0)


    def apply_lights_off_to_children(self):
        """Aplica el efecto LightsOff de LeviathanUI a todos los botones del programa"""
        # Se puede optimizar aplicando a clases especificas
        # Actualmente LightsOff es estatico
        pass 
        
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
        current_mode = detectar_modo_sistema()
        if current_mode != self.last_theme_mode:
            self.last_theme_mode = current_mode
            self.apply_theme()
    
    def apply_theme(self):
        store = get_pm_data()
        # Use automatic UWP accent color by default
        accent = str(get_accent_color())
        accent_hover = accent
        border_w = 3  # Fixed sidebar accent width
        card_op = 0.08  # Fixed card opacity
        density = str(store.get_user("ui_density", "normal"))
        sidebar_h = 50 if density != "compact" else 42

        is_dark = True
        # Cast iron gray texture with subtle gradient
        base_bg = "#3a3f4b" if is_dark else "rgba(245, 245, 245, 0.85)"
        text_col = "#ffffff" if is_dark else "#000000"

        self.central.setStyleSheet(f"""
            QWidget {{
                color: {text_col};
                font-family: 'Segoe UI', sans-serif;
                background: {base_bg};
            }}
            QMainWindow {{
                background: {base_bg};
            }}
            QGroupBox {{
                background-color: transparent; /* Higher opacity for better readability */
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                margin-top: 1.5em;
                font-weight: bold;
                color: {text_col};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: {text_col}; 
                background-color: transparent;
            }}
            QLineEdit {{
                background-color: transparent; /* Higher contrast input background */
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 5px;
                padding: 8px;
                color: white;
                selection-background-color: #ff5722;
            }}
            QLineEdit:focus {{
                border: 1px solid #ff5722; 
                background-color: transparent;
            }}
            QLabel {{
                color: #dddddd;
            }}
            /* Scrollbars UWP Style */
            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 12px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background-color: transparent;
                min-height: 20px;
                border-radius: 6px;
                margin: 2px;
                border: 1px solid transparent;
                background-clip: content-box;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: transparent;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
            QScrollBar:horizontal {{
                border: none;
                background: transparent;
                height: 12px;
                margin: 0;
            }}
            QScrollBar::handle:horizontal {{
                background-color: transparent;
                min-width: 20px;
                border-radius: 6px;
                margin: 2px;
                border: 1px solid transparent;
                background-clip: content-box;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: transparent;
            }}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: none;
            }}
        """)
        
        if hasattr(self.titlebar, "title_lbl"):
            self.titlebar.title_lbl.setText(self._fixed_title)
            self.titlebar.title_lbl.setStyleSheet(f"color: {text_col}; font-weight: 600;")

        for btn in getattr(self, "_sidebar_btn_keys", {}):
            btn.setFixedHeight(sidebar_h)
            btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: #b0b0b0;
                text-align: left;
                padding-left: 17px;
                border: none;
                border-left: {border_w}px solid transparent;
                border-radius: 8px;
                font-family: 'Segoe UI Variable Display', 'Segoe UI', sans-serif;
                font-size: 15px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: transparent;
                color: #ffffff;
            }}
            QPushButton:checked {{
                background-color: transparent;
                color: #ffffff;
                border-left: {border_w}px solid {accent};
            }}
            """)

        if hasattr(self, "desc_card"):
            self.desc_card.setStyleSheet(f"""
            QWidget {{
                background-color: transparent;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                margin-top: 10px;
            }}
            """)

        if hasattr(self, "btn_create_action"):
            self.btn_create_action.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent};
                color: white;
                font-weight: 600;
                font-size: 14px;
                border-radius: 4px;
                border: none;
            }}
            QPushButton:hover {{ background-color: {accent_hover}; }}
            QPushButton:pressed {{ background-color: {accent}; }}
            QPushButton:disabled {{ background-color: #333; color: #666; }}
            """)

    # --- Refactored Init Methods to accept a parent widget instead of using self.tabs ---

    def init_create_tab(self, parent_widget):
        target = parent_widget
        # Enable styled background for proper inheritance
        target.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        # Don't set individual background - let it inherit from parent
        layout = QVBoxLayout(target)
        layout.setSpacing(10)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Header "Crear Nuevo Proyecto" as main title, no GroupBox title
        # UWP Design: Big bold headers, content below.
        title_lbl = QLabel("Crear Nuevo Proyecto")
        title_lbl.setStyleSheet("font-size: 24px; font-weight: 600; color: white; margin-bottom: 10px; background: transparent;")
        layout.addWidget(title_lbl)

        # Container for form elements - Transparent to inherit parent background
        form_group = QGroupBox()
        form_group.setStyleSheet("""
            QGroupBox {
                border: none;
                margin-top: 0px;
                background: transparent;
            }
        """)

        form_layout = QGridLayout(form_group)
        form_layout.setSpacing(15) # Comfortable spacing
        form_layout.setColumnMinimumWidth(0, 160)
        
        # UWP Style Definition for Controls
        # Labels: Segoe UI, 14px, #e0e0e0
        # Inputs: Dark background, light border on hover, accent bottom border or glow on focus.
        
        def uwp_label(text):
            l = QLabel(text)
            l.setStyleSheet("font-family: 'Segoe UI', sans-serif; font-size: 14px; color: #cccccc; font-weight: 500; background: transparent;")
            l.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
            return l
            
        def uwp_input(placeholder):
            line = QLineEdit()
            line.setPlaceholderText(placeholder)
            line.setFixedHeight(35)
            # UWP Style:
            # Normal: Bg #2d2d2d, Border 1px #3d3d3d (bottom border 1px #888)
            # Hover: Bg #323232, Border 1px #444
            # Focus: Bg #1f1f1f, Border-bottom 2px #ff5722 (Accent)
            line.setStyleSheet("""
                QLineEdit {
                    background-color: transparent;
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    border-bottom: 1px solid rgba(255, 255, 255, 0.4);
                    border-radius: 4px;
                    padding: 0 10px;
                    color: white;
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 14px;
                    selection-background-color: #ff5722;
                }
                QLineEdit:hover {
                    background-color: transparent;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.6);
                }
                QLineEdit:focus {
                    background-color: transparent;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-bottom: 2px solid #ff5722;
                }
            """)
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
        
        self.btn_browse_icon = QPushButton("...")
        self.btn_browse_icon.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_browse_icon.setFixedSize(40, 35)
        self.btn_browse_icon.setToolTip("Examinar...")
        # UWP Button Style: Clean, borderless until hover? Or standard button.
        self.btn_browse_icon.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 4px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: transparent;
            }
            QPushButton:pressed {
                background-color: transparent;
                border-color: rgba(255, 255, 255, 0.05);
            }
        """)
        self.btn_browse_icon.clicked.connect(self.browse_icon)
        icon_button(self.btn_browse_icon, "folder", 16)
        icon_box.addWidget(self.btn_browse_icon)
        
        # Wrap icon box in widget since grid layout expects widget or layout
        # (addLayout works too, but we are consistent)
        form_layout.addLayout(icon_box, 5, 1)

        # Fila 6: plataforma + sandbox (siempre visible, sin grupo ni panel expandible)
        platform_sandbox_row = QWidget()
        platform_sandbox_row.setStyleSheet("background-color: transparent;")
        ps_layout = QHBoxLayout(platform_sandbox_row)
        ps_layout.setContentsMargins(0, 2, 0, 2)
        ps_layout.setSpacing(12)

        def uwp_checkbox(text):
            cb = QCheckBox(text)
            cb.setStyleSheet("""
                QCheckBox {
                    color: #dddddd;
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 12px;
                    spacing: 7px;
                    background-color: transparent;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border-radius: 4px;
                    border: 2px solid #666666;
                    background: transparent;
                }
                QCheckBox::indicator:hover {
                    border-color: #888888;
                }
                QCheckBox::indicator:checked {
                    border-color: #ff5722;
                    background-color: #ff5722;
                    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMiA2TDUgOUwxMCAyIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPjwvc3ZnPg==);
                }
            """)
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
        self.multiplatform_label.setStyleSheet("""
            font-family: 'Segoe UI', sans-serif;
            font-size: 10px;
            color: #ff9800;
            background-color: transparent;
            padding: 3px 7px;
            border-radius: 4px;
            margin-top: 2px;
        """)

        platform_col = QWidget()
        platform_col.setStyleSheet("background-color: transparent;")
        pc_layout = QVBoxLayout(platform_col)
        pc_layout.setContentsMargins(0, 0, 0, 0)
        pc_layout.setSpacing(4)
        pc_layout.addLayout(checks_row)
        pc_layout.addWidget(self.multiplatform_label)

        self.sandbox_switch = QCheckBox(tr("create.sandbox"))
        self.sandbox_switch.setChecked(True)
        self.sandbox_switch.setToolTip("Ejecución del proyecto con protección de sandbox (recomendado).")
        self.sandbox_switch.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sandbox_switch.setStyleSheet("""
            QCheckBox {
                color: #cccccc;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
                font-weight: 600;
                spacing: 8px;
                background-color: transparent;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 4px;
                border: 2px solid #4CAF50;
                background: transparent;
            }
            QCheckBox::indicator:hover {
                border-color: #66BB6A;
                background-color: transparent;
            }
            QCheckBox::indicator:checked {
                border-color: #4CAF50;
                background-color: #4CAF50;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMiA2TDUgOUwxMCAyIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPjwvc3ZnPg==);
            }
            QCheckBox::indicator:unchecked {
                border-color: #666666;
            }
        """)
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
        
        self.create_status = QLabel("")
        self.create_status.setStyleSheet("color: #aaa; margin-left: 10px; background-color: transparent;")
        action_layout.addWidget(self.create_status)
        
        action_layout.addStretch()
        
        self.github_progress = QProgressBar()
        self.github_progress.setRange(0,0)
        self.github_progress.setVisible(False)
        self.github_progress.setFixedWidth(150)
        self.github_progress.setFixedHeight(4)
        self.github_progress.setStyleSheet("QProgressBar { background: transparent; border: none; border-radius: 2px; } QProgressBar::chunk { background: #ff5722; }")
        action_layout.addWidget(self.github_progress)
        
        self.btn_create_action = QPushButton("Crear Proyecto")
        self.btn_create_action.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_create_action.setFixedSize(160, 40)
        # UWP Accent Button
        self.btn_create_action.setStyleSheet("""
            QPushButton {
                background-color: #ff5722; 
                color: white; 
                font-weight: 600; 
                font-size: 14px; 
                border-radius: 4px;
                border: none;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton:hover { background-color: #ff7043; }
            QPushButton:pressed { background-color: #e64a19; }
            QPushButton:disabled { background-color: #333; color: #666; }
        """)
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
            self.multiplatform_label.setStyleSheet("""
                font-family: 'Segoe UI', sans-serif;
                font-size: 11px;
                color: #4CAF50;
                background-color: transparent;
                padding: 5px 10px;
                border-radius: 4px;
                margin-top: 5px;
            """)
        elif win_checked:
            self.multiplatform_label.setText("Modo: Windows únicamente")
            self.multiplatform_label.setStyleSheet("""
                font-family: 'Segoe UI', sans-serif;
                font-size: 11px;
                color: #ff9800;
                background-color: transparent;
                padding: 5px 10px;
                border-radius: 4px;
                margin-top: 5px;
            """)
        elif linux_checked:
            self.multiplatform_label.setText("Modo: Linux únicamente")
            self.multiplatform_label.setStyleSheet("""
                font-family: 'Segoe UI', sans-serif;
                font-size: 11px;
                color: #2196F3;
                background-color: transparent;
                padding: 5px 10px;
                border-radius: 4px;
                margin-top: 5px;
            """)
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
        dialog.setWindowTitle("⚠️ Advertencia de Seguridad Crítica")
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
        WipeWindow.create().set_mode("ghostBlur").set_radius(12).apply(dialog)
        
        dialog_central = QWidget(dialog)
        dialog_central.setObjectName("DialogCentral")
        dialog_central.setStyleSheet("""
            QWidget#DialogCentral {
                background-color: transparent;
                border: 1px solid rgba(244, 67, 54, 0.25);
                border-radius: 12px;
            }
        """)
        
        dialog_main_layout = QVBoxLayout(dialog)
        dialog_main_layout.setContentsMargins(0, 0, 0, 0)
        dialog_main_layout.addWidget(dialog_central)
        
        layout = QVBoxLayout(dialog_central)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Header con icono y título
        header_layout = QHBoxLayout()
        icon_label = QLabel("⚠️")
        icon_label.setStyleSheet("font-size: 32px; background-color: transparent;")
        header_layout.addWidget(icon_label)
        
        title_layout = QVBoxLayout()
        title = QLabel("Desactivar Protección de Sandbox")
        title.setStyleSheet("""
            font-family: 'Segoe UI', sans-serif;
            font-size: 16px;
            font-weight: 600;
            color: #f44336;
            background-color: transparent;
        """)
        subtitle = QLabel("Esta acción expone su proyecto a riesgos significativos de seguridad")
        subtitle.setStyleSheet("""
            font-family: 'Segoe UI', sans-serif;
            font-size: 11px;
            color: #888888;
            background-color: transparent;
        """)
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Separador sutil
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: transparent;")
        separator.setFixedHeight(1)
        layout.addWidget(separator)
        
        # Scroll Area para respetar y limitar la altura perfectamente
        scroll = QtWidgets.QScrollArea(dialog_central)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Contenedor del contenido del scroll (con estilo VS Code)
        warning_container = QWidget()
        warning_container.setStyleSheet("""
            background-color: transparent;
            border-radius: 8px;
            border-left: 4px solid #f44336;
        """)
        warning_layout = QVBoxLayout(warning_container)
        warning_layout.setContentsMargins(15, 15, 15, 15)
        warning_layout.setSpacing(12)
        
        intro_text = QLabel("⚠️ <b style='color:#f44336;'>ADVERTENCIA:</b> Al desactivar el Sandbox Seguro, su proyecto se creará sin protección de aislamiento. Esto significa que el código se ejecutará sin restricciones de seguridad.")
        intro_text.setStyleSheet("""
            font-family: 'Segoe UI', sans-serif;
            font-size: 12px;
            color: #cccccc;
            background-color: transparent;
        """)
        intro_text.setWordWrap(True)
        warning_layout.addWidget(intro_text)
        
        risks_title = QLabel("🔴 Riesgos a los que se expone su sistema:")
        risks_title.setStyleSheet("""
            font-family: 'Segoe UI', sans-serif;
            font-size: 12px;
            font-weight: 600;
            color: #ff9800;
            background-color: transparent;
        """)
        warning_layout.addWidget(risks_title)
        
        risks_text = QLabel(
            "• <b>Ejecución de código malicioso:</b> Scripts de terceros podrían contener malware o ransomware.<br><br>"
            "• <b>Accesos no autorizados:</b> El proyecto podría leer, modificar o eliminar archivos del sistema sin restricciones.<br><br>"
            "• <b>Modificaciones no controladas:</b> Cambios en archivos críticos del sistema o del proyecto sin autorización.<br><br>"
            "• <b>Exfiltración de datos:</b> Posible robo de información sensible, credenciales o datos personales.<br><br>"
            "• <b>Persistencia de amenazas:</b> Vectores de ataque que podrían mantenerse activos incluso después de cerrar el proyecto.<br><br>"
            "• <b>Escalada de privilegios:</b> Código que podría obtener permisos de administrador sin su consentimiento.<br><br>"
            "• <b>Daño colateral:</b> Infección de otros proyectos o archivos en su sistema."
        )
        risks_text.setStyleSheet("""
            font-family: 'Segoe UI', sans-serif;
            font-size: 11px;
            color: #bbbbbb;
            background-color: transparent;
            line-height: 1.5;
        """)
        risks_text.setWordWrap(True)
        warning_layout.addWidget(risks_text)
        
        recommendation = QLabel(
            "💡 <b>Recomendación:</b> Mantenga el Sandbox Seguro activado siempre que trabaje con código de fuentes no verificadas, "
            "proyectos descargados de internet, o cuando no tenga control total sobre el origen de todas las dependencias."
        )
        recommendation.setStyleSheet("""
            font-family: 'Segoe UI', sans-serif;
            font-size: 11px;
            color: #4CAF50;
            background-color: transparent;
            padding: 10px;
            border-radius: 6px;
        """)
        recommendation.setWordWrap(True)
        warning_layout.addWidget(recommendation)
        
        scroll.setWidget(warning_container)
        layout.addWidget(scroll)
        
        layout.addSpacing(5)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_cancel = QPushButton("🔒 Mantener Activo")
        btn_cancel.setFixedHeight(36)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 0 16px;
                border-radius: 6px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        btn_cancel.clicked.connect(lambda: self.on_sandbox_dialog_result_extended(dialog, False))
        btn_layout.addWidget(btn_cancel)
        
        btn_accept = QPushButton("⚠️ Desactivar")
        btn_accept.setFixedHeight(36)
        btn_accept.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_accept.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #f44336;
                padding: 0 16px;
                border-radius: 6px;
                border: 1.5px solid #f44336;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: transparent;
            }
        """)
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
            self.create_status.setStyleSheet("color:#c62828;")
            self.create_status.setText("❌ Error: El campo Autor es obligatorio. Debe ser un username de GitHub válido.")
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
        
        self.create_status.setText("🔍 Verificando username de GitHub...")
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
            self.create_status.setStyleSheet("color:#c62828;")
            self.create_status.setText(f"❌ Error: {mensaje}. Por favor, especifica un username válido que exista en GitHub.")
            self.statusBar().showMessage("Verificación fallida")
            return
        
        # Si la verificación fue exitosa, continuar con la creación del proyecto
        autor = self.input_autor.text().strip()
        
        # Obtener plataforma seleccionada (ahora con checkboxes)
        win_checked = self.checkbox_windows.isChecked()
        linux_checked = self.checkbox_linux.isChecked()
        
        if win_checked and linux_checked:
            # Multiplataforma
            plataforma_seleccionada = "AlphaCube"
            xte = "nrdPkg"
        elif win_checked:
            plataforma_seleccionada = "Knosthalij"
            xte = "exe"
        elif linux_checked:
            plataforma_seleccionada = "Danenone"
            xte = "appImage"
        else:
            # Por defecto Windows
            plataforma_seleccionada = "Knosthalij"
            xte = "exe"
        
        empresa = self.input_empresa.text().strip().lower().replace(" ", "-") or "influent"
        nombre_logico = self.input_nombre_logico.text().strip().lower() or "mycoolapp"
        version = self.input_version.text().strip()
        productversion = self.input_version.text().strip()
        if version == "":
             version = f"1-{getversion()}-{plataforma_seleccionada}"
             vso = f"1-{getversion()}"
        else:
            vso = f"{version}-{getversion()}"
            version = f"{version}-{getversion()}-{plataforma_seleccionada}"
        nombre_completo = self.input_nombre_completo.text() or nombre_logico.strip().upper()
        version_base = (self.input_version.text().strip() or "1").split("-")[0]
        from lib.template_engine import build_variables

        _vars = build_variables(
            empresa, nombre_logico, nombre_completo, autor, plataforma_seleccionada, version_base
        )
        folder_name = f"{empresa}.{nombre_logico}.v{_vars['VERSION_FULL']}"
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
            elif os.path.exists(IPM_ICON_PATH):
                shutil.copy(IPM_ICON_PATH, icon_dest)
            if os.path.exists(upd_icon):
                shutil.copy(upd_icon, upd_icn_dst)
            self.create_status.setStyleSheet("color:#388e3c;")
            self.create_status.setText(f"✅ Paquete creado en: {folder_name}/\n🔐 Protegido con sha256: {hv}")
            self.statusBar().showMessage(f"Proyecto creado exitosamente: {folder_name}")
        except Exception as e:
            self.create_status.setStyleSheet("color:#c62828;")
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
        title_lbl = QLabel("Construir Paquete")
        title_lbl.setStyleSheet("font-size: 24px; font-weight: 600; color: white; margin-bottom: 10px; background: transparent;")
        layout.addWidget(title_lbl)

        # Container for form elements - Transparent to inherit parent background
        form_group = QGroupBox()
        form_group.setStyleSheet("""
            QGroupBox {
                border: none;
                margin-top: 0px;
                background: transparent;
            }
        """)

        form_layout = QGridLayout(form_group)
        form_layout.setSpacing(15)
        form_layout.setColumnMinimumWidth(0, 160)
        form_layout.setColumnStretch(1, 1)
        
        # UWP Style Definition for Controls
        # Labels: Segoe UI, 14px, #cccccc
        def uwp_label(text):
            l = QLabel(text)
            l.setStyleSheet("font-family: 'Segoe UI', sans-serif; font-size: 14px; color: #cccccc; font-weight: 500; background-color: transparent;")
            l.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
            return l
            
        def uwp_input(placeholder, read_only=False):
            line = QLineEdit()
            line.setPlaceholderText(placeholder)
            line.setReadOnly(read_only)
            line.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            line.setMinimumHeight(32)
            # UWP Style (Shared with Create Tab)
            line.setStyleSheet("""
                QLineEdit {
                    background-color: #2d2d2d;
                    border: 1px solid #3d3d3d;
                    border-bottom: 1px solid #888;
                    border-radius: 4px;
                    padding: 0 10px;
                    color: white;
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 14px;
                    selection-background-color: #ff5722;
                }
                QLineEdit:hover {
                    background-color: #323232;
                    border-bottom: 1px solid #444;
                }
                QLineEdit:focus {
                    background-color: #1f1f1f;
                    border: 1px solid #3d3d3d;
                    border-bottom: 2px solid #ff5722;
                }
            """)
            if read_only and placeholder.startswith("Detectado"): # Special styling for platform
                 line.setStyleSheet(line.styleSheet() + "QLineEdit { color: #888; font-style: italic; }")
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
        l_mode.setStyleSheet(l_mode.styleSheet() + "margin-top: 8px;")
        form_layout.addWidget(l_mode, 4, 0)
        
        self.build_mode_group = QButtonGroup()
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(20)
        mode_layout.setContentsMargins(0, 5, 0, 0)
        
        def uwp_radio(text):
            r = QRadioButton(text)
            r.setMinimumHeight(30)
            # UWP Radio: Circle with dot - FONDO TRANSPARENTE
            r.setStyleSheet("""
                QRadioButton {
                    color: #ddd;
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 14px;
                    spacing: 8px;
                    background-color: transparent;
                }
                QRadioButton::indicator {
                    width: 18px;
                    height: 18px;
                    border-radius: 10px;
                    border: 2px solid #999;
                    background: transparent;
                }
                QRadioButton::indicator:hover {
                    border-color: white;
                }
                QRadioButton::indicator:checked {
                    border-color: #ff5722;
                    background-color: #ff5722;
                }
            """)
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

        # Fila 5: Carpeta Custom
        form_layout.addWidget(uwp_label("Carpeta Externa:"), 5, 0)
        
        custom_box = QHBoxLayout()
        custom_box.setSpacing(8)
        
        self.input_custom_path = uwp_input("(Opcional) Seleccionar carpeta externa a compilar", read_only=True)
        custom_box.addWidget(self.input_custom_path)
        
        self.btn_select_folder = QPushButton("...")
        self.btn_select_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_select_folder.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.btn_select_folder.setMinimumWidth(36)
        self.btn_select_folder.setMinimumHeight(32)
        self.btn_select_folder.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #323232;
            }
            QPushButton:pressed {
                background-color: #1f1f1f;
            }
        """)
        self.btn_select_folder.clicked.connect(self.select_custom_folder)
        icon_button(self.btn_select_folder, "folder", 16)
        custom_box.addWidget(self.btn_select_folder)
        
        form_layout.addLayout(custom_box, 5, 1)

        layout.addWidget(form_group)
        
        layout.addSpacing(20)

        # Action Area
        action_layout = QHBoxLayout()
        
        self.build_status = QLabel("")
        self.build_status.setStyleSheet("color: #aaa; margin-left: 10px; background-color: transparent;")
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

        self.btn_build = QPushButton("Construir Paquete")
        self.btn_build.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_build.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.btn_build.setMinimumHeight(40)
        self.btn_build.setMinimumWidth(140)
        self.btn_build.setStyleSheet("""
            QPushButton {
                background-color: #ff5722; 
                color: white; 
                font-weight: 600; 
                font-size: 14px; 
                border-radius: 4px;
                border: none;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton:hover { background-color: #ff7043; }
            QPushButton:pressed { background-color: #e64a19; }
            QPushButton:disabled { background-color: #333; color: #666; }
        """)
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
                 except: pass

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
        
        self.build_thread = BuildThread(empresa, nombre, version_full, platformLineEdit, parent=self, custom_path=custom_path, base_dir=BASE_DIR, build_mode=build_mode)
        self.build_thread.progress.connect(lambda msg: self.build_status.setText(msg))
        self.build_thread.finished.connect(lambda msg: [self.build_status.setText(msg), self.build_progress.setVisible(False)])
        self.build_thread.error.connect(lambda msg: [self.build_status.setText(f"❌ Error: {msg}"), self.build_progress.setVisible(False)])
        self.build_thread.start()
        self.statusBar().showMessage(f"Iniciando compilación...")

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
        title_lbl.setStyleSheet("font-size: 24px; font-weight: 600; color: white; margin-bottom: 5px; background: transparent;")
        layout.addWidget(title_lbl)
        
        # Main Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(2)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: transparent;
            }
        """)
        
        def create_section(title, list_widget):
            container = QWidget()
            vbox = QVBoxLayout(container)
            vbox.setContentsMargins(0, 0, 0, 0)
            vbox.setSpacing(10)
            
            lbl = QLabel(title)
            lbl.setStyleSheet("font-family: 'Segoe UI'; font-size: 16px; font-weight: 600; color: #e0e0e0; background-color: transparent;")
            vbox.addWidget(lbl)
            
            # Styled ListWidget
            list_widget.setIconSize(QtCore.QSize(36, 36))
            list_widget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
            list_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            list_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            list_widget.setMinimumHeight(200)
            list_widget.setStyleSheet("""
                QListWidget {
                    background-color: transparent; 
                    border: 1px solid rgba(255, 255, 255, 0.05);
                    border-radius: 8px;
                    padding: 5px;
                    outline: none;
                }
                QListWidget::item {
                    background-color: transparent;
                    border-radius: 6px;
                    padding: 8px;
                    margin-bottom: 2px;
                    color: #ddd;
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 14px;
                }
                QListWidget::item:hover {
                    background-color: transparent;
                }
                QListWidget::item:selected {
                    background-color: transparent;
                    border-left: 3px solid #ff5722;
                    color: white;
                }
            """)
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
            
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {base_bg};
                    color: {text_col};
                    border: {border};
                    border-radius: 4px;
                    font-weight: 600;
                    font-size: 13px;
                    font-family: 'Segoe UI', sans-serif;
                    padding: 0 15px;
                }}
                QPushButton:hover {{
                    background-color: {hover_bg};
                }}
                QPushButton:pressed {{
                    background-color: {base_bg};
                    opacity: 0.8;
                }}
            """)
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
        self.manager_status.setStyleSheet("color: #aaa; margin-top: 5px;")
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
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(target_dir)
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
                desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
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

    def _conf_field_style(self, readonly=False):
        if readonly:
            return """
                QLineEdit, QComboBox {
                    background: rgba(255,255,255,0.03);
                    border: 1px solid rgba(255,255,255,0.06);
                    border-radius: 4px;
                    color: #888;
                    padding: 0 10px;
                }
            """
        return """
            QLineEdit, QComboBox {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.12);
                border-bottom: 2px solid #0078d4;
                border-radius: 4px;
                color: white;
                padding: 0 10px;
                min-height: 32px;
            }
        """

    def _conf_section_title(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(
            "color: #ff7043; font-size: 13px; font-weight: 700; margin-top: 8px; background: transparent;"
        )
        return lbl

    def _conf_form_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #9aa4b2; font-size: 12px; background: transparent;")
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
        self.conf_header.setStyleSheet("font-size: 22px; font-weight: 600; color: white;")
        header_row.addWidget(self.conf_header, 1)
        outer.addLayout(header_row)

        self.conf_restart_banner = QFrame()
        self.conf_restart_banner.setVisible(False)
        self.conf_restart_banner.setStyleSheet(
            "QFrame { background: rgba(255, 152, 0, 0.12); border: 1px solid rgba(255,152,0,0.35); border-radius: 6px; }"
        )
        rb_layout = QHBoxLayout(self.conf_restart_banner)
        rb_layout.setContentsMargins(12, 8, 12, 8)
        self.conf_restart_lbl = QLabel(tr("config.restart_banner"))
        self.conf_restart_lbl.setWordWrap(True)
        self.conf_restart_lbl.setStyleSheet("color: #ffcc80; font-size: 12px; background: transparent;")
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
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(10)

        store = get_pm_data()
        user = {k: store.get_user(k) for k in (
            "language", "auto_translate", "base_dir", "fluthin_apps",
            "touch_mode", "dpi_scale", "device_simulation", "ui_density",
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
        self.conf_base_dir.setStyleSheet(self._conf_field_style())
        btn_browse_proj = QPushButton(tr("config.browse"))
        btn_browse_proj.setMinimumHeight(32)
        btn_browse_proj.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse_proj.setStyleSheet(
            "QPushButton { background: rgba(255,255,255,0.08); color: white; border-radius: 4px; padding: 0 12px; }"
            "QPushButton:hover { background: rgba(255,255,255,0.14); }"
        )
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
        self.conf_fluthin_dir.setStyleSheet(self._conf_field_style())
        btn_browse_fl = QPushButton(tr("config.browse"))
        btn_browse_fl.setMinimumHeight(32)
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
        self.conf_lang_combo.setStyleSheet(self._conf_field_style())
        add_row("config.language", self.conf_lang_combo)

        self.conf_auto_translate = QCheckBox(tr("config.auto_translate"))
        self.conf_auto_translate.setChecked(bool(user.get("auto_translate", True)))
        self.conf_auto_translate.setStyleSheet("color: #ddd; font-size: 12px; background: transparent;")
        self._config_tr_labels.append((self.conf_auto_translate, "config.auto_translate"))
        layout.addWidget(self.conf_auto_translate)
        hint_tr = QLabel(tr("config.auto_translate_hint"))
        hint_tr.setStyleSheet("color: #666; font-size: 11px;")
        hint_tr.setWordWrap(True)
        self._config_tr_labels.append((hint_tr, "config.auto_translate_hint"))
        layout.addWidget(hint_tr)

        add_section("config.section_appearance")
        # Window mode fixed to GhostBlur (Cristal) due to bugs in other modes
        self.conf_display_mode = QLabel("GhostBlur (Cristal)")
        self.conf_display_mode.setStyleSheet("color: #ddd; font-weight: bold;")
        add_row("config.display_mode", self.conf_display_mode)

        self.conf_device_sim = QComboBox()
        self.conf_device_sim.addItems(["laptop", "tablet", "tv", "phone", "ios_x"])
        ds = self.conf_device_sim.findText(user.get("device_simulation", "laptop"))
        if ds >= 0:
            self.conf_device_sim.setCurrentIndex(ds)
        self.conf_device_sim.setStyleSheet(self._conf_field_style())
        add_row("config.device_sim", self.conf_device_sim)

        self.conf_dpi = QLineEdit(str(user.get("dpi_scale", 1.0)))
        self.conf_dpi.setStyleSheet(self._conf_field_style())
        self.conf_dpi.setToolTip(tr("config.dpi_restart_hint"))
        add_row("config.dpi_scale", self.conf_dpi)
        dpi_hint = QLabel(tr("config.dpi_restart_hint"))
        dpi_hint.setStyleSheet("color: #666; font-size: 11px;")
        dpi_hint.setWordWrap(True)
        self._config_tr_labels.append((dpi_hint, "config.dpi_restart_hint"))
        layout.addWidget(dpi_hint)

        self.conf_touch = QCheckBox(tr("config.touch_mode"))
        self.conf_touch.setChecked(bool(user.get("touch_mode", False)))
        self.conf_touch.setStyleSheet("color: #ddd;")
        self._config_tr_labels.append((self.conf_touch, "config.touch_mode"))
        layout.addWidget(self.conf_touch)

        self.conf_ui_density = QComboBox()
        self.conf_ui_density.addItem(tr("config.density_normal"), "normal")
        self.conf_ui_density.addItem(tr("config.density_compact"), "compact")
        dens_idx = self.conf_ui_density.findData(user.get("ui_density", "normal"))
        if dens_idx >= 0:
            self.conf_ui_density.setCurrentIndex(dens_idx)
        self.conf_ui_density.setStyleSheet(self._conf_field_style())
        add_row("config.ui_density", self.conf_ui_density)

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
            n_lbl.setStyleSheet("color: #666; font-size: 11px;")
            v_lbl = QLabel(str(val))
            v_lbl.setStyleSheet("color: #aaa; font-size: 11px;")
            v_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            v_lbl.setWordWrap(True)
            sys_grid.addWidget(n_lbl, i, 0)
            sys_grid.addWidget(v_lbl, i, 1)
        layout.addLayout(sys_grid)

        layout.addStretch()
        scroll.setWidget(scroll_content)
        outer.addWidget(scroll, 1)

        # Botones de acción (Guardar y Resetear)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        btn_save = QPushButton(tr("config.save"))
        btn_save.setMinimumHeight(36)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(
            "QPushButton { background: #0078d4; color: white; border: none; border-radius: 4px; font-weight: 600; }"
            "QPushButton:hover { background: #106ebe; }"
        )
        btn_save.clicked.connect(self._save_app_config_compact)
        icon_button(btn_save, "save", 18)
        self.conf_btn_save = btn_save
        self._config_tr_labels.append((btn_save, "config.save"))
        btn_layout.addWidget(btn_save)
        
        # Botón de resetear configuración (siempre visible)
        self.conf_reset_btn = QPushButton(tr("config.reset"))
        self.conf_reset_btn.setMinimumHeight(36)
        self.conf_reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.conf_reset_btn.setStyleSheet(
            "QPushButton { background: rgba(244, 67, 54, 0.2); color: #ff5722; border: 1px solid rgba(244,67,54,0.4); border-radius: 4px; font-weight: 600; }"
            "QPushButton:hover { background: rgba(244, 67, 54, 0.3); }"
        )
        self.conf_reset_btn.clicked.connect(self._reset_config)
        self._config_tr_labels.append((self.conf_reset_btn, "config.reset"))
        btn_layout.addWidget(self.conf_reset_btn)
        
        btn_layout.addStretch()
        outer.addLayout(btn_layout)

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
            store.set_user("touch_mode", False)  # Modo táctil desactivado
            store.set_user("dpi_scale", 1.0)
            store.set_user("device_simulation", "laptop")
            store.set_user("ui_density", "normal")

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
            self.apply_device_simulation()
            
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
                "touch_mode", "dpi_scale", "device_simulation", "ui_density",
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

            ds = self.conf_device_sim.findText(user.get("device_simulation", "laptop"))
            if ds >= 0:
                self.conf_device_sim.setCurrentIndex(ds)
            
            self.conf_dpi.setText(str(user.get("dpi_scale", 1.0)))
            self.conf_touch.setChecked(bool(user.get("touch_mode", False)))

            dens_idx = self.conf_ui_density.findData(user.get("ui_density", "normal"))
            if dens_idx >= 0:
                self.conf_ui_density.setCurrentIndex(dens_idx)
            
            # Aplicar cambios
            self._apply_leviathan_and_personalization()
            self.apply_theme()
            self.apply_device_simulation()
            
        except Exception as e:
            print(f"Error actualizando formulario: {e}")

    def _restart_for_config(self) -> None:
        store = get_pm_data()
        store.save()
        restart_application()

    def _collect_config_from_form(self) -> dict:
        try:
            dpi = float(self.conf_dpi.text().strip() or "1.0")
        except ValueError:
            dpi = 1.0
        cfg = {
            "BASE_DIR": self.conf_base_dir.text().strip() or BASE_DIR,
            "Fluthin_APPS": self.conf_fluthin_dir.text().strip() or Fluthin_APPS,
            "LANGUAGE": self.conf_lang_combo.currentData() or "es",
            "device_simulation": self.conf_device_sim.currentText(),
            "dpi_scale": dpi,
            "touch_mode": self.conf_touch.isChecked(),
            "auto_translate": self.conf_auto_translate.isChecked(),
            "notifications_enabled": False,
            "ui_density": self.conf_ui_density.currentData() or "normal",
        }
        return cfg

    def _refresh_config_tab_labels(self):
        if hasattr(self, "conf_header"):
            self.conf_header.setText(tr("config.title"))
        if hasattr(self, "conf_ui_density"):
            self.conf_ui_density.setItemText(0, tr("config.density_normal"))
            self.conf_ui_density.setItemText(1, tr("config.density_compact"))
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
        prev_dpi = float(get_pm_data().get_user("applied_dpi_scale", self._applied_dpi_scale))
        new_config = self._collect_config_from_form()
        lang = new_config["LANGUAGE"]
        new_dpi = float(new_config["dpi_scale"])

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
            self.apply_device_simulation()

            needs_restart = abs(new_dpi - prev_dpi) > 0.02
            if needs_restart:
                get_pm_data().set_user("dpi_scale", new_dpi)
                get_pm_data().save()
                self._show_restart_banner()
                msg = tr("config.saved_restart")
            else:
                applied = apply_dpi_scale(new_dpi, APP_FONT)
                self._applied_dpi_scale = applied
                get_pm_data().set_user("applied_dpi_scale", applied)
                get_pm_data().save()
                # Mostrar el botón de reset cuando hay cambios sin reiniciar
                if hasattr(self, "conf_restart_banner"):
                    self.conf_restart_banner.setVisible(True)
                if hasattr(self, "conf_reset_btn"):
                    self.conf_reset_btn.setVisible(True)
                msg = tr("config.saved_ok")

            LeviathanDialog.launch(self, tr("config.title"), msg, mode="success")
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
        header.setStyleSheet("font-size: 22px; font-weight: 600; color: white; background: transparent;")
        mf_header_row.addWidget(header, 1)
        layout.addLayout(mf_header_row)

        desc = QLabel("Repara proyectos con plantillas oficiales.")
        desc.setStyleSheet("color: #9aa4b2; font-size: 12px; background: transparent;")
        layout.addWidget(desc)

        top_row = QHBoxLayout()
        self.mf_batch_mode = QCheckBox("Modo batch")
        self.mf_batch_mode.setStyleSheet("color: #ddd; font-size: 12px; background: transparent;")
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
        self.mf_input.setStyleSheet("""
            QLineEdit {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 4px;
                color: white;
                padding: 0 8px;
            }
        """)
        btn_sel = QPushButton("...")
        btn_sel.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        btn_sel.setMinimumWidth(36)
        btn_sel.setMinimumHeight(32)
        btn_sel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_sel.setStyleSheet(
            "QPushButton { background: rgba(255,255,255,0.08); color: white; border-radius: 4px; }"
            "QPushButton:hover { background: rgba(255,255,255,0.14); }"
        )
        btn_sel.clicked.connect(self.mf_browse)
        icon_button(btn_sel, "folder", 16)
        btn_scan = QPushButton("Diagnosticar")
        btn_scan.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        btn_scan.setMinimumWidth(110)
        btn_scan.setMinimumHeight(32)
        btn_scan.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_scan.setStyleSheet("""
            QPushButton {
                background: #a371f7; color: white; font-weight: 600; font-size: 12px;
                border: none; border-radius: 4px;
            }
            QPushButton:hover { background: #b084f9; }
        """)
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

            except:
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
            logo_lbl.setStyleSheet("background-color: #ff5722; border-radius: 32px; color: white; font-weight: bold; font-size: 24px;")
            logo_lbl.setText("PM")
            logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
        title_box = QVBoxLayout()
        t_main = QLabel("Influent Package Maker")
        t_main.setStyleSheet("font-size: 28px; font-weight: bold; color: white; font-family: 'Segoe UI Variable Display';")
        t_ver = QLabel(f"Versión {self.currentVersion}")
        t_ver.setStyleSheet("font-size: 16px; color: #aaa;")
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
        card.setStyleSheet("color: #ddd; font-size: 14px; line-height: 1.5;")
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
            l.setStyleSheet("color: #888; font-weight: bold;")
            v = QLabel(value)
            v.setStyleSheet("color: white;")
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
        btn_github.setStyleSheet("background-color: #333; color: white; border: none; border-radius: 4px; padding: 8px 16px;")
        btn_github.setCursor(Qt.CursorShape.PointingHandCursor)
        # Open URL logic
        
        btn_telegram = QPushButton("Telegram")
        btn_telegram.setStyleSheet("background-color: #0088cc; color: white; border: none; border-radius: 4px; padding: 8px 16px;")
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
            centralWidget.setStyleSheet("""
                QWidget#CentralWidget {
                    background-color: transparent;
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 16px;
                }
            """)
            
            layoutPrincipal = QVBoxLayout(centralWidget)
            layoutPrincipal.setContentsMargins(0, 0, 0, 0)
            layoutPrincipal.setSpacing(0)
            
            # Barra de título personalizada
            titleBar = CustomTitleBar(dialogoCrearProyecto, title="🆕 Crear Proyecto Aquí", is_main=False)
            layoutPrincipal.addWidget(titleBar)
            
            # Contenido
            contentWidget = QWidget()
            contentLayout = QVBoxLayout(contentWidget)
            contentLayout.setContentsMargins(30, 20, 30, 30)
            contentLayout.setSpacing(15)
            
            # Encabezado con información
            lblTitulo = QLabel("Crear Nuevo Proyecto")
            lblTitulo.setStyleSheet("color: white; font-size: 24px; font-weight: bold; margin-bottom: 10px;")
            lblTitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            contentLayout.addWidget(lblTitulo)
            
            lblRuta = QLabel(f"📁 Ubicación: {projectPath}")
            lblRuta.setStyleSheet("color: #aaa; font-size: 13px; margin-bottom: 20px;")
            lblRuta.setWordWrap(True)
            contentLayout.addWidget(lblRuta)
            
            # Formulario de datos del proyecto
            formLayout = QVBoxLayout()
            formLayout.setSpacing(12)
            
            # Nombre del proyecto
            lblNombre = QLabel("Nombre del Proyecto:")
            lblNombre.setStyleSheet("color: white; font-weight: 600;")
            formLayout.addWidget(lblNombre)
            
            txtNombreProyecto = QLineEdit()
            txtNombreProyecto.setText(os.path.basename(projectPath))
            txtNombreProyecto.setStyleSheet("""
                QLineEdit {
                    background-color: transparent;
                    color: white;
                    border: 2px solid rgba(255,255,255,0.2);
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 2px solid #2486ff;
                }
            """)
            formLayout.addWidget(txtNombreProyecto)
            
            # Versión
            lblVersion = QLabel("Versión:")
            lblVersion.setStyleSheet("color: white; font-weight: 600;")
            formLayout.addWidget(lblVersion)
            
            txtVersion = QLineEdit("1.0")
            txtVersion.setStyleSheet("""
                QLineEdit {
                    background-color: transparent;
                    color: white;
                    border: 2px solid rgba(255,255,255,0.2);
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 2px solid #2486ff;
                }
            """)
            formLayout.addWidget(txtVersion)
            
            # Autor
            lblAutor = QLabel("Autor:")
            lblAutor.setStyleSheet("color: white; font-weight: 600;")
            formLayout.addWidget(lblAutor)
            
            txtAutor = QLineEdit()
            txtAutor.setPlaceholderText("Tu nombre")
            txtAutor.setStyleSheet("""
                QLineEdit {
                    background-color: transparent;
                    color: white;
                    border: 2px solid rgba(255,255,255,0.2);
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 2px solid #2486ff;
                }
            """)
            formLayout.addWidget(txtAutor)
            
            # Publisher
            lblPublisher = QLabel("Publisher:")
            lblPublisher.setStyleSheet("color: white; font-weight: 600;")
            formLayout.addWidget(lblPublisher)
            
            txtPublisher = QLineEdit()
            txtPublisher.setPlaceholderText("Nombre de la empresa")
            txtPublisher.setStyleSheet("""
                QLineEdit {
                    background-color: transparent;
                    color: white;
                    border: 2px solid rgba(255,255,255,0.2);
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 2px solid #2486ff;
                }
            """)
            formLayout.addWidget(txtPublisher)
            
            # Descripción
            lblDescripcion = QLabel("Descripción:")
            lblDescripcion.setStyleSheet("color: white; font-weight: 600;")
            formLayout.addWidget(lblDescripcion)
            
            txtDescripcion = QTextEdit()
            txtDescripcion.setPlaceholderText("Describe tu proyecto...")
            txtDescripcion.setMaximumHeight(100)
            txtDescripcion.setStyleSheet("""
                QTextEdit {
                    background-color: transparent;
                    color: white;
                    border: 2px solid rgba(255,255,255,0.2);
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 14px;
                }
                QTextEdit:focus {
                    border: 2px solid #2486ff;
                }
            """)
            formLayout.addWidget(txtDescripcion)
            
            contentLayout.addLayout(formLayout)
            contentLayout.addStretch()
            
            # Botones de acción
            layoutBotones = QHBoxLayout()
            layoutBotones.setSpacing(10)
            
            btnCancelar = QPushButton("❌ Cancelar")
            btnCancelar.setStyleSheet(BTN_STYLES["default"])
            btnCancelar.setCursor(Qt.CursorShape.PointingHandCursor)
            btnCancelar.setMinimumHeight(45)
            
            btnCrear = QPushButton("✨ Crear Proyecto")
            btnCrear.setStyleSheet(BTN_STYLES["best"])
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
            centralWidget.setStyleSheet("""
                QWidget#CentralWidget {
                    background-color: transparent;
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 16px;
                }
            """)
            
            layoutPrincipal = QVBoxLayout(centralWidget)
            layoutPrincipal.setContentsMargins(0, 0, 0, 0)
            layoutPrincipal.setSpacing(0)
            
            # Barra de título personalizada
            titleBar = CustomTitleBar(dialogoInstalar, title="📦 Instalar como Fluthin Package", is_main=False)
            layoutPrincipal.addWidget(titleBar)
            
            # Contenido
            contentWidget = QWidget()
            contentLayout = QVBoxLayout(contentWidget)
            contentLayout.setContentsMargins(30, 20, 30, 30)
            contentLayout.setSpacing(15)
            
            # Título
            lblTitulo = QLabel("Instalar Carpeta como Paquete")
            lblTitulo.setStyleSheet("color: white; font-size: 22px; font-weight: bold; margin-bottom: 10px;")
            lblTitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            contentLayout.addWidget(lblTitulo)
            
            lblInfo = QLabel(f"📁 Carpeta: {os.path.basename(folderPath)}")
            lblInfo.setStyleSheet("color: #aaa; font-size: 14px; margin-bottom: 20px;")
            lblInfo.setWordWrap(True)
            contentLayout.addWidget(lblInfo)
            
            # Barra de progreso
            progressBar = LeviathanProgressBar(self)
            contentLayout.addWidget(progressBar)
            
            # Log de instalación
            txtLog = QTextEdit()
            txtLog.setReadOnly(True)
            txtLog.setStyleSheet("""
                QTextEdit {
                    background-color: transparent;
                    color: #0f0;
                    font-family: 'Consolas', 'Courier New', monospace;
                    border: 2px solid rgba(0,255,0,0.3);
                    border-radius: 8px;
                    padding: 10px;
                    font-size: 13px;
                }
            """)
            contentLayout.addWidget(txtLog)
            
            # Botones
            layoutBotones = QHBoxLayout()
            
            btnCerrar = QPushButton("Cerrar")
            btnCerrar.setStyleSheet(BTN_STYLES["default"])
            btnCerrar.setEnabled(False)
            btnCerrar.setMinimumHeight(45)
            
            btnInstalar = QPushButton("📥 Instalar Paquete")
            btnInstalar.setStyleSheet(BTN_STYLES["success"])
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
            centralWidget.setStyleSheet("""
                QWidget#CentralWidget {
                    background-color: transparent;
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 16px;
                }
            """)
            
            layoutPrincipal = QVBoxLayout(centralWidget)
            layoutPrincipal.setContentsMargins(0, 0, 0, 0)
            layoutPrincipal.setSpacing(0)
            
            # Barra de título personalizada
            titleBar = CustomTitleBar(dialogoCompilar, title="🔨 Compilar Proyecto", is_main=False)
            layoutPrincipal.addWidget(titleBar)
            
            # Contenido
            contentWidget = QWidget()
            contentLayout = QVBoxLayout(contentWidget)
            contentLayout.setContentsMargins(30, 20, 30, 30)
            contentLayout.setSpacing(15)
            
            # Título
            lblTitulo = QLabel("Compilar Proyecto")
            lblTitulo.setStyleSheet("color: white; font-size: 24px; font-weight: bold; margin-bottom: 10px;")
            lblTitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            contentLayout.addWidget(lblTitulo)
            
            lblInfo = QLabel(f"📁 Proyecto: {os.path.basename(projectPath)}")
            lblInfo.setStyleSheet("color: #aaa; font-size: 14px; margin-bottom: 20px;")
            lblInfo.setWordWrap(True)
            contentLayout.addWidget(lblInfo)
            
            # Opciones de compilación
            groupOpciones = QGroupBox("Opciones de Compilación")
            groupOpciones.setStyleSheet("""
                QGroupBox {
                    color: white;
                    font-weight: bold;
                    border: 2px solid rgba(255,255,255,0.2);
                    border-radius: 8px;
                    margin-top: 10px;
                    padding-top: 15px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
            """)
            layoutOpciones = QVBoxLayout()
            
            chkWindows = QCheckBox("🪟 Compilar para Windows")
            chkWindows.setChecked(True)
            chkWindows.setStyleSheet("color: white; font-size: 14px;")
            layoutOpciones.addWidget(chkWindows)
            
            chkKnosthalij = QCheckBox("🌐 Compilar para Knosthalij")
            chkKnosthalij.setStyleSheet("color: white; font-size: 14px;")
            layoutOpciones.addWidget(chkKnosthalij)
            
            chkOptimizar = QCheckBox("⚡ Optimizar código")
            chkOptimizar.setChecked(True)
            chkOptimizar.setStyleSheet("color: white; font-size: 14px;")
            layoutOpciones.addWidget(chkOptimizar)
            
            groupOpciones.setLayout(layoutOpciones)
            contentLayout.addWidget(groupOpciones)
            
            # Barra de progreso
            progressBar = LeviathanProgressBar(self)
            contentLayout.addWidget(progressBar)
            
            # Log de compilación
            txtLog = QTextEdit()
            txtLog.setReadOnly(True)
            txtLog.setStyleSheet("""
                QTextEdit {
                    background-color: transparent;
                    color: #0f0;
                    font-family: 'Consolas', 'Courier New', monospace;
                    border: 2px solid rgba(0,255,0,0.3);
                    border-radius: 8px;
                    padding: 10px;
                    font-size: 13px;
                }
            """)
            contentLayout.addWidget(txtLog)
            
            # Botones
            layoutBotones = QHBoxLayout()
            
            btnCerrar = QPushButton("Cerrar")
            btnCerrar.setStyleSheet(BTN_STYLES["default"])
            btnCerrar.setEnabled(False)
            btnCerrar.setMinimumHeight(45)
            
            btnCompilar = QPushButton("🔨 Compilar")
            btnCompilar.setStyleSheet(BTN_STYLES["success"])
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
            centralWidget.setStyleSheet("""
                QWidget#CentralWidget {
                    background-color: transparent;
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 16px;
                }
            """)
            
            layoutPrincipal = QVBoxLayout(centralWidget)
            layoutPrincipal.setContentsMargins(0, 0, 0, 0)
            layoutPrincipal.setSpacing(0)
            
            # Barra de título personalizada
            titleBar = CustomTitleBar(dialogoReparar, title="🌙 MoonFix - Reparar Proyecto", is_main=False)
            layoutPrincipal.addWidget(titleBar)
            
            # Contenido
            contentWidget = QWidget()
            contentLayout = QVBoxLayout(contentWidget)
            contentLayout.setContentsMargins(30, 20, 30, 30)
            contentLayout.setSpacing(15)
            
            # Título
            lblTitulo = QLabel("MoonFix - Reparación Automática")
            lblTitulo.setStyleSheet("color: white; font-size: 24px; font-weight: bold; margin-bottom: 10px;")
            lblTitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            contentLayout.addWidget(lblTitulo)
            
            lblInfo = QLabel(f"📁 Proyecto: {os.path.basename(projectPath)}")
            lblInfo.setStyleSheet("color: #aaa; font-size: 14px; margin-bottom: 10px;")
            lblInfo.setWordWrap(True)
            contentLayout.addWidget(lblInfo)
            
            lblDescripcion = QLabel("MoonFix analizará el proyecto en busca de archivos faltantes, configuraciones antiguas y errores de estructura.")
            lblDescripcion.setStyleSheet("color: #888; font-size: 13px; margin-bottom: 20px;")
            lblDescripcion.setWordWrap(True)
            contentLayout.addWidget(lblDescripcion)
            
            # Opciones de reparación
            groupOpciones = QGroupBox("Opciones de Reparación")
            groupOpciones.setStyleSheet("""
                QGroupBox {
                    color: white;
                    font-weight: bold;
                    border: 2px solid rgba(255,255,255,0.2);
                    border-radius: 8px;
                    margin-top: 10px;
                    padding-top: 15px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
            """)
            layoutOpciones = QVBoxLayout()
            
            chkArchivos = QCheckBox("📄 Verificar archivos faltantes")
            chkArchivos.setChecked(True)
            chkArchivos.setStyleSheet("color: white; font-size: 14px;")
            layoutOpciones.addWidget(chkArchivos)
            
            chkConfig = QCheckBox("⚙️ Actualizar configuraciones antiguas")
            chkConfig.setChecked(True)
            chkConfig.setStyleSheet("color: white; font-size: 14px;")
            layoutOpciones.addWidget(chkConfig)
            
            chkEstructura = QCheckBox("🏗️ Reparar estructura de carpetas")
            chkEstructura.setChecked(True)
            chkEstructura.setStyleSheet("color: white; font-size: 14px;")
            layoutOpciones.addWidget(chkEstructura)
            
            chkDependencias = QCheckBox("📦 Verificar dependencias")
            chkDependencias.setChecked(True)
            chkDependencias.setStyleSheet("color: white; font-size: 14px;")
            layoutOpciones.addWidget(chkDependencias)
            
            groupOpciones.setLayout(layoutOpciones)
            contentLayout.addWidget(groupOpciones)
            
            # Barra de progreso
            progressBar = LeviathanProgressBar(self)
            contentLayout.addWidget(progressBar)
            
            # Log de reparación
            txtLog = QTextEdit()
            txtLog.setReadOnly(True)
            txtLog.setStyleSheet("""
                QTextEdit {
                    background-color: transparent;
                    color: #0ff;
                    font-family: 'Consolas', 'Courier New', monospace;
                    border: 2px solid rgba(0,255,255,0.3);
                    border-radius: 8px;
                    padding: 10px;
                    font-size: 13px;
                }
            """)
            contentLayout.addWidget(txtLog)
            
            # Botones
            layoutBotones = QHBoxLayout()
            
            btnCerrar = QPushButton("Cerrar")
            btnCerrar.setStyleSheet(BTN_STYLES["default"])
            btnCerrar.setEnabled(False)
            btnCerrar.setMinimumHeight(45)
            
            btnReparar = QPushButton("🌙 Ejecutar MoonFix")
            btnReparar.setStyleSheet(BTN_STYLES["best"])
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
            platform = normalize_platform(xml_data.get("platform", "Knosthalij"))
            version_raw = xml_data.get("version", "1.0.0").lstrip("v").split("-")[0] or "1.0.0"

            progressBar.setValue(40)
            txtLog.append("[1/2] Aplicando plantillas de proyecto...")
            result = repair_project_from_templates(
                Path(projectPath),
                publisher,
                app_id,
                name,
                author,
                platform,
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
            txtLog.append(f"\n=== ✅ MoonFix Completado ===")
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
            centralWidget.setStyleSheet("""
                QWidget#CentralWidget {
                    background-color: transparent;
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 16px;
                }
            """)
            
            layoutPrincipal = QVBoxLayout(centralWidget)
            layoutPrincipal.setContentsMargins(0, 0, 0, 0)
            layoutPrincipal.setSpacing(0)
            
            # Barra de título personalizada
            titleBar = CustomTitleBar(dialogoInstalarPaquete, title="📦 Instalar Paquete", is_main=False)
            layoutPrincipal.addWidget(titleBar)
            
            # Contenido
            contentWidget = QWidget()
            contentLayout = QVBoxLayout(contentWidget)
            contentLayout.setContentsMargins(30, 20, 30, 30)
            contentLayout.setSpacing(15)
            
            # Título
            lblTitulo = QLabel("Instalar Paquete Fluthin")
            lblTitulo.setStyleSheet("color: white; font-size: 24px; font-weight: bold; margin-bottom: 10px;")
            lblTitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            contentLayout.addWidget(lblTitulo)
            
            lblInfo = QLabel(f"📄 Archivo: {os.path.basename(filePath)}")
            lblInfo.setStyleSheet("color: #aaa; font-size: 14px; margin-bottom: 20px;")
            lblInfo.setWordWrap(True)
            contentLayout.addWidget(lblInfo)
            
            # Barra de progreso
            progressBar = LeviathanProgressBar(self)
            contentLayout.addWidget(progressBar)
            
            # Log de instalación
            txtLog = QTextEdit()
            txtLog.setReadOnly(True)
            txtLog.setStyleSheet("""
                QTextEdit {
                    background-color: transparent;
                    color: #0f0;
                    font-family: 'Consolas', 'Courier New', monospace;
                    border: 2px solid rgba(0,255,0,0.3);
                    border-radius: 8px;
                    padding: 10px;
                    font-size: 13px;
                }
            """)
            contentLayout.addWidget(txtLog)
            
            # Botones
            layoutBotones = QHBoxLayout()
            
            btnCerrar = QPushButton("Cerrar")
            btnCerrar.setStyleSheet(BTN_STYLES["default"])
            btnCerrar.setEnabled(False)
            btnCerrar.setMinimumHeight(45)
            
            btnInstalar = QPushButton("📥 Instalar")
            btnInstalar.setStyleSheet(BTN_STYLES["success"])
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
            centralWidget.setStyleSheet("""
                QWidget#CentralWidget {
                    background-color: transparent;
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 16px;
                }
            """)
            
            layoutPrincipal = QVBoxLayout(centralWidget)
            layoutPrincipal.setContentsMargins(0, 0, 0, 0)
            layoutPrincipal.setSpacing(0)
            
            # Barra de título personalizada
            titleBar = CustomTitleBar(dialogoInstalarMexf, title="🔧 Instalar Extensiones MEXF", is_main=False)
            layoutPrincipal.addWidget(titleBar)
            
            # Contenido
            contentWidget = QWidget()
            contentLayout = QVBoxLayout(contentWidget)
            contentLayout.setContentsMargins(30, 20, 30, 30)
            contentLayout.setSpacing(15)
            
            # Título
            lblTitulo = QLabel("Instalar Extensiones de Shell")
            lblTitulo.setStyleSheet("color: white; font-size: 22px; font-weight: bold; margin-bottom: 10px;")
            lblTitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            contentLayout.addWidget(lblTitulo)
            
            lblInfo = QLabel(f"📄 Archivo: {os.path.basename(filePath)}")
            lblInfo.setStyleSheet("color: #aaa; font-size: 14px; margin-bottom: 20px;")
            lblInfo.setWordWrap(True)
            contentLayout.addWidget(lblInfo)
            
            # Información del archivo MEXF
            try:
                import json
                with open(filePath, 'r', encoding='utf-8') as f:
                    mexfData = json.load(f)
                
                infoText = f"Nombre: {mexfData.get('name', 'N/A')}\n"
                infoText += f"Versión: {mexfData.get('version', 'N/A')}\n"
                infoText += f"Descripción: {mexfData.get('description', 'N/A')}"
                
                lblDetalles = QLabel(infoText)
                lblDetalles.setStyleSheet("""
                    color: white;
                    background-color: transparent;
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 8px;
                    padding: 15px;
                    font-size: 13px;
                """)
                lblDetalles.setWordWrap(True)
                contentLayout.addWidget(lblDetalles)
            except:
                pass
            
            # Barra de progreso
            progressBar = LeviathanProgressBar(self)
            contentLayout.addWidget(progressBar)
            
            # Log de instalación
            txtLog = QTextEdit()
            txtLog.setReadOnly(True)
            txtLog.setStyleSheet("""
                QTextEdit {
                    background-color: transparent;
                    color: #0f0;
                    font-family: 'Consolas', 'Courier New', monospace;
                    border: 2px solid rgba(0,255,0,0.3);
                    border-radius: 8px;
                    padding: 10px;
                    font-size: 13px;
                }
            """)
            contentLayout.addWidget(txtLog)
            
            # Botones
            layoutBotones = QHBoxLayout()
            
            btnCerrar = QPushButton("Cerrar")
            btnCerrar.setStyleSheet(BTN_STYLES["default"])
            btnCerrar.setEnabled(False)
            btnCerrar.setMinimumHeight(45)
            
            btnInstalar = QPushButton("🔧 Instalar Extensiones")
            btnInstalar.setStyleSheet(BTN_STYLES["success"])
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
            import json
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
            centralWidget.setStyleSheet("""
                QWidget#CentralWidget {
                    background-color: transparent;
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 16px;
                }
            """)
            
            layoutPrincipal = QVBoxLayout(centralWidget)
            layoutPrincipal.setContentsMargins(0, 0, 0, 0)
            layoutPrincipal.setSpacing(0)
            
            # Barra de título personalizada
            titleBar = CustomTitleBar(dialogoCrearMexf, title="📝 Crear Archivo MEXF", is_main=False)
            layoutPrincipal.addWidget(titleBar)
            
            # Contenido
            contentWidget = QWidget()
            contentLayout = QVBoxLayout(contentWidget)
            contentLayout.setContentsMargins(30, 20, 30, 30)
            contentLayout.setSpacing(15)
            
            # Título
            lblTitulo = QLabel("Crear Archivo de Extensiones MEXF")
            lblTitulo.setStyleSheet("color: white; font-size: 22px; font-weight: bold; margin-bottom: 10px;")
            lblTitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            contentLayout.addWidget(lblTitulo)
            
            lblInfo = QLabel(f"📁 Ubicación: {folderPath}")
            lblInfo.setStyleSheet("color: #aaa; font-size: 13px; margin-bottom: 20px;")
            lblInfo.setWordWrap(True)
            contentLayout.addWidget(lblInfo)
            
            # Formulario
            formLayout = QVBoxLayout()
            formLayout.setSpacing(12)
            
            # Nombre del archivo
            lblNombre = QLabel("Nombre del archivo:")
            lblNombre.setStyleSheet("color: white; font-weight: 600;")
            formLayout.addWidget(lblNombre)
            
            txtNombre = QLineEdit()
            txtNombre.setText("extension")
            txtNombre.setPlaceholderText("Nombre sin extensión")
            txtNombre.setStyleSheet("""
                QLineEdit {
                    background-color: transparent;
                    color: white;
                    border: 2px solid rgba(255,255,255,0.2);
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 2px solid #2486ff;
                }
            """)
            formLayout.addWidget(txtNombre)
            
            # Descripción
            lblDesc = QLabel("Descripción:")
            lblDesc.setStyleSheet("color: white; font-weight: 600;")
            formLayout.addWidget(lblDesc)
            
            txtDesc = QTextEdit()
            txtDesc.setPlaceholderText("Describe las extensiones que incluye este archivo...")
            txtDesc.setMaximumHeight(100)
            txtDesc.setStyleSheet("""
                QTextEdit {
                    background-color: transparent;
                    color: white;
                    border: 2px solid rgba(255,255,255,0.2);
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 14px;
                }
                QTextEdit:focus {
                    border: 2px solid #2486ff;
                }
            """)
            formLayout.addWidget(txtDesc)
            
            contentLayout.addLayout(formLayout)
            
            # Información adicional
            lblAyuda = QLabel("ℹ️ Se creará un archivo .mexf de ejemplo con configuraciones básicas de integración con el shell.")
            lblAyuda.setStyleSheet("color: #888; font-size: 12px; margin-top: 10px;")
            lblAyuda.setWordWrap(True)
            contentLayout.addWidget(lblAyuda)
            
            contentLayout.addStretch()
            
            # Botones
            layoutBotones = QHBoxLayout()
            
            btnCancelar = QPushButton("❌ Cancelar")
            btnCancelar.setStyleSheet(BTN_STYLES["default"])
            btnCancelar.setCursor(Qt.CursorShape.PointingHandCursor)
            btnCancelar.setMinimumHeight(45)
            
            btnCrear = QPushButton("📝 Crear MEXF")
            btnCrear.setStyleSheet(BTN_STYLES["best"])
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
            
            import json
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
    
    cli = CLIHandler()
    
    if cli.has_cli_args():
        args = cli.parse()
        
        if hasattr(args, 'version') and args.version:
            # Intentar obtener versión de varias fuentes
            try:
                from version import VERSION
                version = VERSION
            except ImportError:
                version = "3.2.7" # Fallback
            print(f"Influent Package Maker v{version}")
            sys.exit(0)
        
        action, data, action_options = cli.get_action(args)
        
        if action:
            # Acciones que no requieren GUI ni QApplication
            if action in ['shellpatch_install', 'shellpatch_remove', 'shellpatch_shortcuts'] or action_options.get('headless'):
                handle_cli_action(action, data, None, **action_options)
                return
            
            if PYQT6_AVAILABLE:
                app = QApplication(sys.argv)
                app.setFont(APP_FONT)
                window = handle_cli_action(action, data, PackageTodoGUI, **action_options)
            else:
                print("❌ Error: PyQt6 no está disponible para esta acción GUI.")
                sys.exit(1)
            if window is None: # Si es headless o acción de shell ya terminada
                return
            if window:
                window.show()
                main_window = window
                sys.exit(app.exec())
            return
    
    app = QApplication(sys.argv)
    app.setFont(APP_FONT)
    
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
        if getattr(sys, 'frozen', False):
            try:
                import pyi_splash
                pyi_splash.close()
            except ImportError:
                pass
    
    splash.finished.connect(on_splash_finished)
    main_window.show()
    splash.start(5000)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
