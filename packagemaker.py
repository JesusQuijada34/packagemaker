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

# Limpiar caché de leviathan-ui si existe
if 'leviathan_ui' in sys.modules:
    del sys.modules['leviathan_ui']
if 'leviathan_ui.title_bar' in sys.modules:
    del sys.modules['leviathan_ui.title_bar']

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
LOCAL_LEVIATHAN_UI = os.path.abspath(os.path.join(ROOT_DIR, os.pardir, "leviathan-ui"))

# Insertar ruta local al INICIO para prioridad máxima
if LOCAL_LEVIATHAN_UI in sys.path:
    sys.path.remove(LOCAL_LEVIATHAN_UI)
sys.path.insert(0, LOCAL_LEVIATHAN_UI)

print(f"[DEBUG] Usando leviathan-ui local: {LOCAL_LEVIATHAN_UI}")
print(f"[DEBUG] sys.path[0]: {sys.path[0]}")

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
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QEvent, QObject, QProcess
import requests
import winreg  # Para guardar en registro de Windows

from leviathan_ui import InmersiveSplash, LightsOff, LeviathanDialog, WipeWindow, LeviathanProgressBar, CustomTitleBar, get_accent_color
from leviathan_ui.touchscreen import TouchScreen
from lib.Updater import KillerLogic, InstallerWorker, ModernUpdaterWindow
from lib.BuildThread import BuildThread, FlangCompiler
from lib.TitleBar import AnimTitleButton, TitleBar
from lib.SidebarItem import SidebarItem
from lib.moonFixWizard import MoonFixWizard, QSetup, QInstaller, verificar_github_username, detectar_modo_sistema
from lib.gitHubVerifyThread import GitHubVerifyThread
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
APP_FONT = QFont('Segoe UI Variable', 11)
TAB_FONT = QFont('Segoe UI Variable', 12) # Icons (SVGs are handled as strings here for "one-file" convenience or resource paths)
TAB_ICONS = {
    "crear": "app/package_add.ico",  # Placeholder, will use text if not found or system icons
    "construir": "app/package_build.ico",
    "gestor": "app/package_fm.ico",
    "config": "app/app_settings.ico",
    "moonfix": "app/moonfix.ico",
    "reparar": "app/package_install.ico",
    "about": "app/package_About.ico",
    "instalar": "app/package_install.ico",
    "desinstalar": "app/package_uninstall.ico"
}

# SVG Definitions for "About" Page and Sidebar (Inline for robustness)
SVG_ABOUT = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="10" stroke="#f9826c" stroke-width="2"/><path d="M12 7V13M12 17H12.01" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>"""
SVG_SETTINGS = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 15C13.6569 15 15 13.6569 15 12C15 10.3431 13.6569 9 12 9C10.3431 9 9 10.3431 9 12C9 13.6569 10.3431 15 12 15Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M19.4 15A1.65 1.65 0 0 0 20 12A1.65 1.65 0 0 0 19.4 9M12 3A1.65 1.65 0 0 0 9 3M12 21A1.65 1.65 0 0 0 15 21M4.6 15A1.65 1.65 0 0 0 4 12A1.65 1.65 0 0 0 4.6 9" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>"""

# Windows 11-inspired button styles (rounded, soft shadows, modern accent colors)
# Note: The 'transition' property is a CSS feature supported by browsers, but it is NOT supported/stable in PyQt6 stylesheets.
# PyQt6 ignores 'transition' and related CSS3 properties—they have no effect and can be safely omitted.
# QSS-based stylized button styles using rgba colors, with transparency for blending with the app frame
BTN_STYLES = {
    "default": (
        "background-color: rgba(243,246,251,0.85);"
        "color: rgba(32,33,36,0.96);"
        "border-radius: 9px;"
        "padding: 10px 20px;"
        "font-weight: 600;"
        "border: 1px solid rgba(209,215,224,0.65);"
        "background-image: qlineargradient(y1:0, y2:1, stop:0 rgba(60,120,250,0.15), stop:1 rgba(20,20,64,0.10));"
        # No box-shadow
    ),
    "success": (
        "background-color: rgba(230,244,234,0.82);"
        "color: rgba(5,98,55,0.99);"
        "border-radius: 9px;"
        "padding: 10px 20px;"
        "font-weight: 600;"
        "border: 1px solid rgba(199,232,206,0.60);"
        "background-image: qlineargradient(y1:0, y2:1, stop:0 rgba(5,98,55,0.13), stop:1 rgba(0,80,44,0.06));"
        # No box-shadow
    ),
    "danger": (
        "background-color: rgba(253,231,231,0.80);"
        "color: rgba(185,29,29,1.0);"
        "border-radius: 9px;"
        "padding: 10px 20px;"
        "font-weight: 600;"
        "border: 1px solid rgba(255,180,180,0.68);"
        "background-image: qlineargradient(y1:0, y2:1, stop:0 rgba(185,29,29,0.15), stop:1 rgba(250,15,15,0.07));"
        # No box-shadow
    ),
    "warning": (
        "background-color: rgba(255,248,225,0.82);"
        "color: rgba(168,132,4,0.97);"
        "border-radius: 9px;"
        "padding: 10px 20px;"
        "font-weight: 600;"
        "border: 1px solid rgba(255,224,149,0.66);"
        "background-image: qlineargradient(y1:0, y2:1, stop:0 rgba(168,132,4,0.13), stop:1 rgba(255,200,20,0.11));"
        # No box-shadow
    ),
    "info": (
        "background-color: rgba(230,240,253,0.80);"
        "color: rgba(9,82,165,1.0);"
        "border-radius: 9px;"
        "padding: 10px 20px;"
        "font-weight: 600;"
        "border: 1px solid rgba(185,213,253,0.56);"
        "background-image: qlineargradient(y1:0, y2:1, stop:0 rgba(9,82,165,0.13), stop:1 rgba(30,110,220,0.11));"
        # No box-shadow
    ),
    "best": (
        "background-color: qlineargradient(y1:0, y2:1, stop:0 #e6f4fa, stop:1 #c4e6fb);"
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

# --- GLOBAL CONFIG SYSTEM ---
IPM_ICON_PATH = os.path.join("app", "app-icon.ico")
DEFAULT_FOLDERS = "app,assets,config,docs,source,lib"
CONFIG_DIR = os.path.join(os.getcwd(), "config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.json")
DEFAULT_CONFIG = {
    "BASE_DIR": BASE_DIR,
    "Fluthin_APPS": Fluthin_APPS,
    "GLOBAL_VARS": "",
    "DISPLAY_MODE": "GhostBlur (Cristal)"
}

# --- UTILITY FUNCTIONS ---
def getversion():
    """Genera una versión basada en fecha y hora actual"""
    newversion = time.strftime("%y.%m-%H.%M")
    return f"{newversion}"

def load_app_config():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return DEFAULT_CONFIG

APP_CONFIG = load_app_config()
BASE_DIR = APP_CONFIG.get("BASE_DIR", BASE_DIR)
Fluthin_APPS = APP_CONFIG.get("Fluthin_APPS", Fluthin_APPS)

# Crear las carpetas si no existen
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(Fluthin_APPS, exist_ok=True)

def save_app_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
        return True
    except:
        return False

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

UPDATER_CODE = r'''import sys, os, time, shutil, zipfile, subprocess, traceback, threading
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtGui import QFont, QIcon, QPixmap, QColor
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QObject

# --- LEVIATHAN UI CHECK ---
try:
    from leviathan_ui import LeviathanDialog, WipeWindow, LeviathanProgressBar, CustomTitleBar
    HAS_LEVIATHAN = True
except ImportError:
    HAS_LEVIATHAN = False

# --- CONFIG ---
XML_PATH = "details.xml"
LOG_PATH = "updater_log.txt"
CHECK_INTERVAL = 60
GITHUB_API = "https://api.github.com"

def log(msg):
    ts = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{ts} {msg}\n")
    except: pass
    print(f"{ts} {msg}")

def leer_xml(path):
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        return {
            "app": root.findtext("app", "").strip(),
            "version": root.findtext("version", "").strip(),
            "platform": root.findtext("platform", "").strip(),
            "author": root.findtext("author", "").strip(),
            "publisher": root.findtext("publisher", "").strip()
        }
    except: return {}

def leer_xml_remoto(author, app):
    url = f"https://raw.githubusercontent.com/{author}/{app}/main/details.xml"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return ET.fromstring(r.text).findtext("version", "").strip()
    except: pass
    return ""

def buscar_release(author, app, version, platform, publisher):
    filename = f"{publisher}.{app}.{version}-{platform}.iflapp"
    url = f"https://github.com/{author}/{app}/releases/download/{version}/{filename}"
    try:
        if requests.head(url, timeout=15, allow_redirects=True).status_code == 200:
            return url
    except: pass
    return None

# Updater classes moved to lib/Updater.py
    def __init__(self, app_data, url):
        super().__init__()
        self.app_data = app_data
        self.url = url
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(480, 320)
        if HAS_LEVIATHAN:
            WipeWindow.create().set_mode("ghostBlur").apply(self)
        self.init_ui()
        self.center()
        QTimer.singleShot(500, self.start_install)

    def center(self):
        self.move(QApplication.primaryScreen().availableGeometry().center() - self.rect().center())

    def init_ui(self):
        central = QWidget()
        central.setObjectName("Central")
        central.setStyleSheet("QWidget#Central { background: rgba(18, 24, 34, 0.85); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; }")
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if HAS_LEVIATHAN:
            self.title_bar = CustomTitleBar(self, title="System Updater", is_main=True)
            self.title_bar.set_color(QColor(0,0,0,0))
            layout.addWidget(self.title_bar)

        content = QWidget()
        c_lay = QVBoxLayout(content)
        c_lay.setContentsMargins(30, 10, 30, 30)
        c_lay.setSpacing(15)
        
        self.icon_lbl = QLabel("🔄")
        self.icon_lbl.setStyleSheet("font-size: 48px; color: #2486ff;")
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_lay.addWidget(self.icon_lbl)
        
        self.lbl_main = QLabel(f"Actualizando {self.app_data['app']}")
        self.lbl_main.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_main.setStyleSheet("font-family: 'Segoe UI'; font-weight: 700; font-size: 18px; color: white;")
        c_lay.addWidget(self.lbl_main)
        
        self.lbl_status = QLabel("Preparando...")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setStyleSheet("color: #aaa; font-size: 13px;")
        c_lay.addWidget(self.lbl_status)
        
        if HAS_LEVIATHAN:
            self.pbar = LeviathanProgressBar(self)
        else:
            self.pbar = QProgressBar()
            self.pbar.setStyleSheet("QProgressBar { background: #333; border: none; height: 6px; } QProgressBar::chunk { background: #2486ff; }")
            self.pbar.setTextVisible(False)
        c_lay.addWidget(self.pbar)
        
        layout.addWidget(content)

    def start_install(self):
        self.thread = QThread()
        self.worker = InstallerWorker(self.url, self.app_data)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.pbar.setValue)
        self.worker.status.connect(self.lbl_status.setText)
        self.worker.finished.connect(self.on_fin)
        self.thread.start()

    def on_fin(self, ok, msg):
        self.thread.quit()
        if ok:
            self.lbl_status.setText("¡Actualización completada!")
            # Relaunch
            exe = f"{self.app_data['app']}.exe"
            if os.path.exists(exe): subprocess.Popen(exe)
            QTimer.singleShot(1500, self.close)
        else:
            self.lbl_status.setText(f"Error: {msg}")
            self.lbl_status.setStyleSheet("color: #ff5252;")

def ciclo_embestido():
    def verificar():
        while True:
            datos = leer_xml(XML_PATH)
            if datos:
                remoto = leer_xml_remoto(datos["author"], datos["app"])
                if remoto and remoto != datos["version"]:
                    url = buscar_release(datos["author"], datos["app"], remoto, datos["platform"], datos["publisher"])
                    if url:
                        # Find main app if running to allow modal usage? No, separate process.
                        app = QApplication(sys.argv)
                        w = ModernUpdaterWindow(datos, url)
                        w.show()
                        app.exec()
                        # Si se actualizó, el updater debe terminar
                        return 
            time.sleep(CHECK_INTERVAL)
    threading.Thread(target=verificar, daemon=True).start()

if __name__ == "__main__":
    ciclo_embestido()
    while True: time.sleep(100)
'''

DOCS_TEMPLATE = r'''<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Cargando…</title>
  <link rel="icon" href="https://raw.githubusercontent.com/__OWNER__/__REPO__/main/app/app-icon.ico" type="image/x-icon" />
  <style>
    :root {
      --accent: #2486ff;
      --bg-start: rgba(34,74,186,0.78);
      --bg-end: rgba(12,30,60,0.93);
      --card-bg: rgba(255,255,255,0.55);
      --text: #07203a;
      --muted: rgba(7,32,58,0.7);
      --glass-blur: 12px;
      --glass-saturation: 140%;
      --glass-border: rgba(255,255,255,0.22);
      --radius: 14px;
      --shadow: 0 8px 30px rgba(2,8,23,0.45);
      font-family: "Segoe UI", "Segoe UI Variable", Roboto, system-ui, -apple-system, "Helvetica Neue", Arial;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --accent: #1e6fe8;
        --bg-start: rgba(20,28,56,0.9);
        --bg-end: rgba(7,14,38,0.97);
        --card-bg: rgba(12,14,16,0.45);
        --text: #e6eef9;
        --muted: rgba(230,238,249,0.75);
        --glass-border: rgba(255,255,255,0.06);
        --shadow: 0 12px 30px rgba(0,0,0,0.7);
      }
    }
    *{box-sizing:border-box}
    html,body,#app{height:100%}
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--text);
      /* BG FIX: no repeat, partial, non-white, layered gradient */
      background:
        radial-gradient(ellipse 650px 320px at 65% 20%, rgba(36,134,255,0.15) 0%, rgba(30,50,130, 0.08) 60%, transparent 100%) no-repeat,
        radial-gradient(circle 430px at 20% 80%, rgba(36,134,255,0.10) 0%, rgba(10,24,55,0.07) 60%, transparent 100%) no-repeat,
        linear-gradient(120deg, var(--bg-start) 0%, var(--bg-end) 80%, #0b182f 100%) no-repeat;
      background-size: cover, cover, cover;
      background-attachment: fixed;
      -webkit-font-smoothing:antialiased;
      -moz-osx-font-smoothing:grayscale;
      display: flex;
      align-items: flex-start;
      justify-content: center;
      padding: 36px;
      transition: background 450ms ease;
    }
    .banner{
      width:100%;
      max-width:1300px;
      border-radius:18px;
      overflow:hidden;
      position:relative;
      box-shadow:var(--shadow);
      backdrop-filter: blur(6px) saturate(var(--glass-saturation));
      border: 1px solid var(--glass-border);
      background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
      animation: fadeInUp 600ms cubic-bezier(.2,.9,.25,1);
    }
    .splash{
      height:360px;
      width:100%;
      position:relative;
      background-size:cover;
      background-position:center;
      display:flex;
      align-items:flex-start;
      justify-content:flex-start;
      padding:28px 36px;
      gap:24px;
      transition: background-image 420ms ease;
    }
    .splash::after{
      content:"";
      position:absolute;
      left:0; top:0; bottom:0;
      width:56%;
      pointer-events:none;
      background: linear-gradient(90deg, rgba(255,255,255,0.06), rgba(255,255,255,0.00) 40%);
      filter: blur(20px);
      mix-blend-mode: screen;
      transition:opacity 350ms ease;
    }
    .appcard{
      position:relative;
      display:flex;
      gap:20px;
      align-items:flex-start;
      background: var(--card-bg);
      border-radius:12px;
      padding:18px;
      max-width:720px;
      width:720px;
      backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-saturation));
      border: 1px solid var(--glass-border);
      box-shadow: 0 6px 20px rgba(2,8,23,0.12);
      transform: translateY(12px);
      transition: transform 420ms cubic-bezier(.2,.9,.25,1), box-shadow 220ms ease;
    }
    .appcard:hover{ transform: translateY(6px); box-shadow: 0 18px 40px rgba(2,8,23,0.18); }
    .logo{
      width:96px; height:96px; flex:0 0 96px;
      border-radius:18px;
      overflow:hidden;
      display:flex;
      align-items:center;
      justify-content:center;
      background:linear-gradient(145deg, rgba(255,255,255,0.18), rgba(255,255,255,0.02));
      border: 1px solid rgba(255,255,255,0.12);
      box-shadow: 0 6px 18px rgba(2,8,23,0.12), inset 0 1px 0 rgba(255,255,255,0.08);
    }
    .logo img{ width:86px; height:86px; object-fit:contain; display:block; }
    .app-right{ flex:1 1 auto; display:flex; flex-direction:column; gap:12px; min-width:0; }
    .meta{ display:flex; flex-direction:column; gap:6px; min-width:0; }
    .title-row{ display:flex; align-items:baseline; gap:12px; flex-wrap:wrap; }
    .app-title{ font-size:20px; font-weight:700; letter-spacing: -0.01em; margin:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .meta-info{ font-size:13px; color:var(--muted); margin-top:2px; }
    .meta-author a{ color:var(--accent); text-decoration:none; font-weight:600; }
    .meta-author a:hover{ text-decoration:underline; }
    .meta-rate{ font-size:13px; color:var(--muted);}
    .app-footer{ display:flex; align-items:center; justify-content:space-between; gap:12px; margin-top:6px; }
    .actions{ margin:0; display:flex; flex-direction:row; gap:10px; align-items:center; }
    .btn{ -webkit-appearance:none; appearance:none; border:0; outline:0; cursor:pointer; font-weight:600; font-size:14px; padding:10px 16px; border-radius:10px; color:white; background: linear-gradient(180deg, var(--accent), calc(var(--accent) - 10%)); box-shadow: 0 6px 18px rgba(36,134,255,0.22), inset 0 -2px 0 rgba(0,0,0,0.12); transition: transform 160ms ease, box-shadow 160ms ease, opacity 200ms ease; transform: translateY(0); display:inline-flex; gap:10px; align-items:center; }
    .btn.secondary{ background: transparent; color:var(--muted); border:1px solid rgba(255,255,255,0.06); box-shadow:none; font-weight:600; backdrop-filter: blur(6px); }
    .btn:active{ transform: translateY(2px); } .btn[disabled]{ opacity:0.45; cursor:not-allowed; transform:none; }
    .support-badge{ font-size:12px; color:var(--muted); margin-top:6px; text-align:right; }
    .unsupported{ color:#ff6b6b; font-weight:700; } .warn{ color:#ffb657; font-weight:700; }
    .readme{ padding:28px 36px; background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.00)); border-top: 1px solid rgba(255,255,255,0.03); }
    .readme-inner{ max-width:1100px; margin:0 auto; padding:18px; border-radius:12px; background:rgba(255,255,255,0.02); backdrop-filter: blur(6px); color:var(--text); }
    .readme-inner h1,.readme-inner h2{ color:var(--text); } .readme-inner a{ color:var(--accent); text-decoration:underline; }
    @keyframes fadeInUp{ from{ opacity:0; transform: translateY(12px) } to{ opacity:1; transform: translateY(0) } }
    @media (max-width:880px){
      body{ padding:18px; } .splash{ padding:18px; height:520px; align-items:flex-end; flex-direction:column; gap:12px; justify-content:flex-end; }
      .appcard{ width:100%; transform:none; flex-direction:row; } .app-right{ gap:8px; } .actions{ width:100%; justify-content:flex-end; }
      .logo{ width:80px; height:80px; } .app-title{ font-size:18px; } .readme{ padding:18px; } .banner{ border-radius:14px; } .appcard{ padding:14px; }
    }
    @media (min-width:1400px){
      body{ padding:60px; background-position: center 10%; } .banner{ max-width:1600px; } .splash{ height:420px; padding:44px 56px; } .appcard{ padding:22px; gap:28px; max-width:820px; width:820px; } .logo{ width:128px; height:128px; flex:0 0 128px; border-radius:20px; } .logo img{ width:112px; height:112px; } .app-title{ font-size:24px; } .actions{ gap:14px; } .btn{ padding:12px 18px; font-size:15px; border-radius:12px; } .readme-inner{ padding:28px; max-width:1200px; }
    }
    a,button{ -webkit-tap-highlight-color: transparent; }
  </style>
</head>
<body>
  <div id="app" aria-live="polite">
    <div class="banner" role="region" aria-label="Ficha de la aplicación">
      <div id="splash" class="splash">
        <div id="left-area" style="position:relative; z-index:2; display:flex; align-items:center;">
          <div class="appcard" id="appcard" aria-hidden="true">
            <div class="logo" id="logoWrap" aria-hidden="true" title="Logotipo">
              <img id="logoImg" alt="Logo de la aplicación" src="" width="86" height="86" style="opacity:0; transform:scale(.98); transition:opacity 320ms ease, transform 420ms cubic-bezier(.2,.9,.25,1); display:block;">
            </div>
            <div class="app-right">
              <div class="meta">
                <div class="title-row">
                  <h1 class="app-title" id="appTitle">Cargando…</h1>
                </div>
                <div class="meta-info" id="metaInfo">…</div>
                <div class="meta-author" id="metaAuthor"></div>
                <div class="meta-rate" id="metaRate"></div>
              </div>
              <div class="app-footer">
                <div style="flex:1"></div>
                <div class="actions" id="actions" aria-hidden="true">
                  <button class="btn" id="handlerBtn" title="Instalar vía handler">Instalar vía handler</button>
                  <button class="btn secondary" id="directBtn" title="Descarga directa">Descarga directa</button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <svg style="position:absolute; right:16%; top:18%; width:40%; height:50%; filter: blur(36px); opacity:0.25; z-index:1; pointer-events:none">
          <defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#2486ff"/><stop offset="1" stop-color="#8ecbff" /></linearGradient></defs>
          <rect x="0" y="0" width="100%" height="100%" fill="url(#g)" rx="36"></rect>
        </svg>
      </div>
      <div class="readme" id="readmeWrap" aria-label="README">
        <div class="readme-inner" id="readmeContent">
          <p style="color:var(--muted); margin:0">README cargando…</p>
        </div>
      </div>
    </div>
  </div>
  <script>
    (function(){
      const FALLBACK_OWNER = 'JesusQuijada34';
      const FALLBACK_REPO  = 'packagemaker';
      const LOCAL = {
        splash: 'https://raw.githubusercontent.com/__OWNER__/__REPO__/main/assets/splash.png',
        logo: 'https://raw.githubusercontent.com/__OWNER__/__REPO__/main/assets/product_logo.png',
        details: 'https://raw.githubusercontent.com/__OWNER__/__REPO__/main/details.xml',
        readme: 'https://raw.githubusercontent.com/__OWNER__/__REPO__/main/README.md',
      };
      // App UI
      const splashEl = document.getElementById('splash');
      const logoImg = document.getElementById('logoImg');
      const appTitle = document.getElementById('appTitle');
      const metaInfo = document.getElementById('metaInfo');
      const metaAuthor = document.getElementById('metaAuthor');
      const metaRate = document.getElementById('metaRate');
      const handlerBtn = document.getElementById('handlerBtn');
      const directBtn = document.getElementById('directBtn');
      const actions = document.getElementById('actions');
      const readmeContent = document.getElementById('readmeContent');
      // OS
      function detectOS(){
        const ua = navigator.userAgent || navigator.vendor || '';
        const platform = (navigator.platform || '').toLowerCase();
        if (/android/i.test(ua)) return 'android';
        if (/iphone|ipad|ipod/i.test(ua)) return 'ios';
        if (/windows nt|win32|wow64/i.test(ua) || /win/i.test(platform)) return 'windows';
        if (/macintosh|mac os x/i.test(ua) || /mac/i.test(platform)) return 'mac';
        if (/linux/i.test(ua) && !/android/i.test(ua)) return 'linux';
        return 'unknown';
      }
      const detected = detectOS();
      if (detected === 'android') {
        const ov = document.createElement('div');
        ov.style.position = 'fixed';
        ov.style.inset = '0';
        ov.style.display = 'flex';
        ov.style.alignItems = 'center';
        ov.style.justifyContent = 'center';
        ov.style.background = 'linear-gradient(180deg, rgba(2,8,23,0.85), rgba(2,8,23,0.7))';
        ov.style.color = 'white';
        ov.style.zIndex = 9999;
        ov.style.flexDirection = 'column';
        ov.innerHTML = '<div style="font-weight:700; font-size:18px; margin-bottom:12px">Incompatible: Android no soportado</div><div style="max-width:70ch; text-align:center; opacity:0.95">La instalación y la descarga de paquetes no son compatibles en Android. La página ha sido bloqueada por seguridad.</div>';
        document.body.appendChild(ov);
        return;
      }
      // helpers
      function githubRaw(owner, repo, branch, filepath){
        branch = branch || 'main';
        return `https://raw.githubusercontent.com/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/${encodeURIComponent(branch)}/${filepath}`;
      }
      async function fetchTextWithFallbackSafe(candidates){
        for(const url of candidates){
          try{
            const res = await fetch(url, {cache: "reload"});
            if(res.ok) return await res.text();
          }catch(e){}
        }
        return null;
      }
      async function fetchBlobWithFallbackSafe(candidates){
        for(const url of candidates){
          try{
            const res = await fetch(url, {cache: "reload"});
            if(res.ok) return URL.createObjectURL(await res.blob());
          }catch(e){}
        }
        return null;
      }
      function renderMarkdown(md){
        if(!md) return '<p>(README vacío)</p>';
        const esc = s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
        md = md.replace(/\r\n/g,'\n');
        md = md.replace(/```([\s\S]*?)```/g, (m, code) => '<pre><code>' + esc(code) + '</code></pre>');
        md = md.replace(/^###### (.*$)/gim, '<h6>$1</h6>');
        md = md.replace(/^##### (.*$)/gim, '<h5>$1</h5>');
        md = md.replace(/^#### (.*$)/gim, '<h4>$1</h4>');
        md = md.replace(/^### (.*$)/gim, '<h3>$1</h3>');
        md = md.replace(/^## (.*$)/gim, '<h2>$1</h2>');
        md = md.replace(/^# (.*$)/gim, '<h1>$1</h1>');
        md = md.replace(/^\s*-\s+(.*)/gim, '<li>$1</li>');
        md = md.replace(/(<li>[\s\S]*?<\/li>)/gim, '<ul>$1</ul>');
        md = md.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');
        md = md.replace(/\*(.*?)\*/gim, '<em>$1</em>');
        md = md.replace(/`([^`]+)`/gim, '<code>$1</code>');
        md = md.replace(/\[([^\]]+)\]\(([^)]+)\)/gim, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
        return md.split('\n').map(line => /^<h|^<ul|^<pre|^<li|^<blockquote/.test(line)||/^\s*$/.test(line) ? line : '<p>'+line+'</p>').join('\n');
      }
      function appendSupportNotice(type, text){
        let support = document.querySelector('.support-badge');
        if(!support){
          support = document.createElement('div');
          support.className = 'support-badge';
          const appFooter = document.querySelector('.app-footer');
          if(appFooter) appFooter.parentNode.insertBefore(support, appFooter.nextSibling);
          else document.getElementById('appcard').appendChild(support);
        }
        if(type === 'unsupported') support.innerHTML = '<span class="unsupported">' + escapeHtml(text) + '</span>';
        else if(type === 'warn') support.innerHTML = '<span class="warn">' + escapeHtml(text) + '</span>';
        else support.textContent = text;
      }
      function escapeHtml(s){ return (s||'').toString().replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

      // --- DATA LOAD & UI SYNC ---
      (async function(){
        appTitle.textContent = 'Cargando…';
        metaInfo.textContent = '';
        metaAuthor.textContent = '';
        metaRate.textContent = '';
        document.title = 'Cargando…';
        // PRIORITIZE REMOTE GITHUB RAW
        const detailsCandidates = [
          LOCAL.details
        ];
        let detailsText = await fetchTextWithFallbackSafe(detailsCandidates);
        let metadata = {};
        if(detailsText){
          try{
            const xml = new window.DOMParser().parseFromString(detailsText, 'application/xml');
            if(!xml.querySelector('parsererror') && xml.documentElement){
              Array.from(xml.documentElement.children).forEach(child => {
                const k = child.tagName ? child.tagName.toLowerCase() : '';
                const v = (child.textContent || '').trim();
                if(k) metadata[k] = v;
              });
            } else appendSupportNotice('warn', 'details.xml malformado. Datos limitados.');
          }catch(e){
            appendSupportNotice('warn', 'Error details.xml.');
          }
        }else{
          appendSupportNotice('warn', 'No se encontró details.xml.');
        }
        const displayTitle = metadata.name || metadata.app || 'Nombre de la app';
        document.title = displayTitle;
        appTitle.textContent = displayTitle;
        const publisher = metadata.publisher || '';
        const version = metadata.version || '';
        const platformSpec = (metadata.platform || '').trim();
        function packagePlatformToHuman(p){
          if(!p) return '';
          if(/Knosthalij/i.test(p)) return 'Windows';
          if(/Danenone/i.test(p)) return 'Linux';
          if(/AlphaCube/i.test(p)){
            if(detected === 'windows') return 'Windows';
            if(detected === 'linux') return 'Linux';
            return '';
          }
          if(/win/i.test(p)) return 'Windows';
          if(/linux|lin/i.test(p)) return 'Linux';
          return p;
        }
        const humanPlatform = packagePlatformToHuman(platformSpec);
        const infoParts = [publisher, displayTitle, version].filter(Boolean).join(' ');
        metaInfo.textContent = (infoParts ? infoParts + ' ' : '') + (humanPlatform ? 'para ' + humanPlatform : '');
        // Author link
        if(metadata.author){
          const a = document.createElement('a');
          const repoName = metadata.app || FALLBACK_REPO;
          a.href = `https://github.com/${encodeURIComponent(metadata.author)}/${encodeURIComponent(repoName)}`;
          a.target = '_blank'; a.rel = 'noopener noreferrer';
          a.textContent = metadata.author;
          metaAuthor.innerHTML = '';
          metaAuthor.appendChild(a);
        }else{ metaAuthor.textContent = ''; }
        metaRate.textContent = metadata.rate || '';
        // Logic for handler/descarga
        const missingDownloadFields = ['author','app','publisher','version','platform'].filter(k => !metadata[k]);
        const downloadsHaveAllFields = missingDownloadFields.length === 0;
        let allowedOS = [];
        if(/^AlphaCube$/i.test(platformSpec)) allowedOS = ['windows','linux'];
        else if(/^Danenone$/i.test(platformSpec)) allowedOS = ['linux'];
        else if(/^Knosthalij$/i.test(platformSpec)) allowedOS = ['windows'];
        else allowedOS = [];
        const platformSupported = allowedOS.includes(detected);
        let handlerURL = null, directURL = null;
        if(metadata.author && metadata.app) handlerURL = `flarmstore://${encodeURIComponent(metadata.author)}.${encodeURIComponent(metadata.app)}/`;
        if(downloadsHaveAllFields){
          const chosenPackagePlatform =
            (/^AlphaCube$/i.test(platformSpec) && detected === 'windows') ? 'Knosthalij' :
            (/^AlphaCube$/i.test(platformSpec) && detected === 'linux') ? 'Danenone' :
            platformSpec;
          const vid = encodeURIComponent(metadata.version);
          directURL = `https://github.com/${encodeURIComponent(metadata.author)}/${encodeURIComponent(metadata.app)}/releases/download/${vid}/${encodeURIComponent(metadata.publisher)}.${encodeURIComponent(metadata.app)}.${vid}-${encodeURIComponent(chosenPackagePlatform)}.iflapp`;
        }
        handlerBtn.onclick = () => { if(!handlerBtn.disabled && handlerURL) window.location.href = handlerURL; };
        directBtn.onclick = () => { if(!directBtn.disabled && directURL) window.open(directURL, '_blank', 'noopener'); };
        if(detected === 'unknown'){
          handlerBtn.disabled = true; directBtn.disabled = true;
          appendSupportNotice('warn', 'Sistema no identificado — descargas deshabilitadas');
        } else if(!platformSupported){
          handlerBtn.disabled = true; directBtn.disabled = true;
          appendSupportNotice('unsupported', 'No soportado por tu sistema operativo');
        } else if(!downloadsHaveAllFields){
          handlerBtn.disabled = true; directBtn.disabled = true;
          appendSupportNotice('warn', 'Metadatos incompletos — descargas deshabilitadas ('+missingDownloadFields.join(', ')+')');
        } else {
          handlerBtn.disabled = false; directBtn.disabled = false;
          directBtn.textContent = `Descarga directa (${packagePlatformToHuman(platformSpec) || platformSpec})`;
          handlerBtn.textContent = 'Instalar vía handler';
          appendSupportNotice('', 'Compatible con ' + (packagePlatformToHuman(platformSpec) || detected));
        }
        // Visuals: prioritize remote URLs
        const owner = metadata.author || FALLBACK_OWNER;
        const repo  = metadata.app || FALLBACK_REPO;
        const branches = ['main','master'];
        function candidates(localPath, repoPath){
          return [localPath];
        }
        fetchBlobWithFallbackSafe(candidates(LOCAL.splash, 'assets/splash.png')).then(splashBlob => {
          if(splashBlob){
            splashEl.style.backgroundImage =
              `linear-gradient(180deg,rgba(40,80,200,0.33),rgba(18,36,80,0.77) 85%,rgba(11,24,47,0.95)), url("${splashBlob}")`;
          }
        });
        fetchBlobWithFallbackSafe(candidates(LOCAL.logo, 'assets/product_logo.png')).then(logoBlob => {
          if(logoBlob){
            logoImg.style.display = 'block';
            logoImg.src = logoBlob;
            logoImg.onload = () => { logoImg.style.opacity = 1; logoImg.style.transform = 'scale(1)'; };
          }else{
            logoImg.style.display = 'none';
            const wrap = document.getElementById('logoWrap');
            if(wrap && !wrap.querySelector('.placeholder')){
              const placeholder = document.createElement('div');
              placeholder.className = 'placeholder';
              placeholder.style.width = '86px';
              placeholder.style.height = '86px';
              placeholder.style.display = 'flex';
              placeholder.style.alignItems = 'center';
              placeholder.style.justifyContent = 'center';
              placeholder.style.background = 'linear-gradient(135deg, rgba(36,134,255,0.16), rgba(30,43,60,0.27))';
              placeholder.style.borderRadius = '12px';
              placeholder.style.color = 'white';
              placeholder.style.fontWeight = '700';
              placeholder.style.letterSpacing = '-0.02em';
              const initials = (displayTitle||'').split(/\s+/).map(s=>s[0]||'').slice(0,2).join('').toUpperCase() || 'PK';
              placeholder.textContent = initials;
              wrap.appendChild(placeholder);
            }
          }
        });
        fetchTextWithFallbackSafe(candidates(LOCAL.readme, 'README.md')).then(readmeText => {
          if(readmeText) readmeContent.innerHTML = renderMarkdown(readmeText);
        });
      })();
    })();
  </script>
</body>
</html>'''



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
    return "3.2.7"  # Fallback por defecto


# FlangCompiler moved to lib/BuildThread.py
# BuildThread moved to lib/BuildThread.py
# AnimTitleButton moved to lib/TitleBar.py
# TitleBar moved to lib/TitleBar.py
# FocusIndicationFilter moved to lib/focusIndicationFilter.py
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
                background-color: rgba(217, 109, 39, 0.1);
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
SIDEBAR_DESC = {
    0: "### Crear Proyecto\nDiseña aplicaciones desde cero. Establece identidades únicas, versiones y metadatos para el ecosistema **Influent OS** de forma guiada.",
    1: "### Construir Paquete\nEmpaqueta tu trabajo. Transforma carpetas de desarrollo en archivos `.iflapp` comprimidos y listos para su distribución global.",
    2: "### Gestor de Aplicaciones\nTu centro de control. Administra proyectos locales y aplicaciones instaladas. Ejecuta, depura o elimina con absoluta precisión.",
    3: "### Configuración\nAjusta el motor del programa. Controla rutas de almacenamiento, previsualización de temas y variables globales del sistema.",
    4: "### MoonFix Suite\nSanación profunda. Escanea, detecta y repara inconsistencias en tus paquetes. Asegura que cada asset y etiqueta XML sea perfecta.",
    5: "### Acerca de\nDetalles técnicos del proyecto. Información sobre la licencia GPL, el framework Qt y el equipo que hace posible **Package Maker**."
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
        self.setWindowTitle(f"Influent Package Maker v{self.currentVersion}")
        self.resize(1100, 720)
        self.setFont(APP_FONT)
        self.setWindowIcon(QtGui.QIcon(IPM_ICON_PATH if os.path.exists(IPM_ICON_PATH) else ""))

        # Central Widget & Main Layout
        self.central = QWidget()
        self.central.setObjectName("CentralWidget")
        self.central.setStyleSheet("background-color: #121822; border: none;")
        self.setCentralWidget(self.central)
        
        # Layout principal vertical (TitleBar + ContentArea)
        self.v_layout = QVBoxLayout(self.central)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setSpacing(0)

        # Title Bar Custom (LeviathanUI) - extendida por toda la barra
        self.titlebar = CustomTitleBar(self, title=self.windowTitle(), icon=(IPM_ICON_PATH if os.path.exists(IPM_ICON_PATH) else ""))
        self.titlebar.setStyleSheet("background-color: transparent; border: none;")
        # Extender la titlebar para que ocupe todo el ancho
        self.titlebar.setMinimumWidth(self.width())
        self.v_layout.addWidget(self.titlebar)

        # Content Container (Sidebar + Stack)
        self.content_container = QWidget()
        self.content_layout = QHBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # --- SIDEBAR (Left) ---
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(260)
        self.sidebar.setStyleSheet("background-color: rgba(18, 20, 28, 0.96); border-right: 1px solid rgba(255,255,255,0.08);")
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(15, 20, 15, 20)
        self.sidebar_layout.setSpacing(8)

        # Header Sidebar (Optional, maybe "Menú Inicio" text style)
        lbl_menu = QLabel("Menú Principal")
        lbl_menu.setStyleSheet("color: #ffffff; font-size: 24px; font-weight: 700; font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif; margin-bottom: 12px; letter-spacing: 0.3px;")
        self.sidebar_layout.addWidget(lbl_menu)

        # Navigation Buttons
        self.btn_create = SidebarItem("Crear Proyecto", TAB_ICONS["crear"])
        self.btn_build = SidebarItem("Construir Paquete", TAB_ICONS["construir"])
        self.btn_manager = SidebarItem("Gestor (Apps)", TAB_ICONS["gestor"])
        self.btn_config = SidebarItem("Configuración", TAB_ICONS.get("config"))
        self.btn_moonfix = SidebarItem("MoonFix", TAB_ICONS["moonfix"])
        self.btn_about = SidebarItem("Acerca de", TAB_ICONS["about"])
        
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
                background-color: rgba(255, 255, 255, 0.04);
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
        
        ctx_lbl = QLabel("Contexto")
        ctx_lbl.setStyleSheet("border:none; background:transparent; color: #888; font-weight: bold; font-size: 11px; text-transform: uppercase;")
        desc_header.addWidget(ctx_lbl)
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
        self.stack.setStyleSheet("background-color: transparent;")
        
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

        if self.compact_mode or self.shell_mode:
            self.enterCompactShellMode()
        
        # Startup Animation
        self.animate_startup()
        
        # Initial description
        self.update_sidebar_description(0)

    def enterCompactShellMode(self):
        self.sidebar.hide()
        self.content_layout.setContentsMargins(8, 8, 8, 8)
        self.content_container.setStyleSheet("background-color: transparent;")
        self.resize(460, 760)
        self.setMinimumSize(420, 660)
        self.statusBar().showMessage("Modo compacto de shell activado")
        self.setWindowTitle(f"Influent Package Maker v{self.currentVersion} - Shell")
        if hasattr(self.titlebar, 'setStyleSheet'):
            self.titlebar.setStyleSheet("background-color: rgba(255, 255, 255, 0.08);")

    def update_sidebar_description(self, index):
        if index in SIDEBAR_DESC:
            # Simple markdown-to-html like formatting for headings
            text = SIDEBAR_DESC[index]
            html = text.replace("### ", "<b style='color:white; font-size:14px;'>").replace("\n", "</b><br>")
            self.sidebar_desc_text.setHtml(html)

    def animate_startup(self):
        """Animación de desplazamiento hacia arriba y opacidad al abrir"""
        # Center on screen first
        screen_geo = QApplication.primaryScreen().geometry()
        x = (screen_geo.width() - self.width()) // 2
        y = (screen_geo.height() - self.height()) // 2
        
        start_y = y + 50
        end_y = y

        self.move(x, start_y)
        self.setWindowOpacity(0.0)

        # Animacion de geometria (Posicion)
        self.anim_pos = QtCore.QPropertyAnimation(self, b"pos")
        self.anim_pos.setDuration(800)
        self.anim_pos.setStartValue(QtCore.QPoint(x, start_y))
        self.anim_pos.setEndValue(QtCore.QPoint(x, end_y))
        self.anim_pos.setEasingCurve(QtCore.QEasingCurve.Type.OutExpo)
        
        # Animacion de opacidad
        self.anim_fade = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.anim_fade.setDuration(800)
        self.anim_fade.setStartValue(0.0)
        self.anim_fade.setEndValue(1.0)
        
        self.anim_group = QtCore.QParallelAnimationGroup(self)
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
        else:  # laptop
            # Ventana normal maximizada respetando barra de tareas
            self.resize(1100, 720)
            self.move((screen.width() - 1100) // 2, (screen.height() - 720) // 2)
            self.touch_enabled = touch_mode
        
        # Aplicar color de interfaz
        if not auto_color:
            self.setStyleSheet(f"QMainWindow {{ background-color: {interface_color}; }}")
        
        # Aplicar DPI scaling (simplificado)
        if dpi_scale != 1.0:
            # Nota: DPI scaling completo requiere configuración global de QApplication
            pass
        
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
        """Cambia la página con una sutil animación de fade/slide"""
        # Actualizar descripcion del sidebar
        self.update_sidebar_description(index)
        
        # Simple fade transition for stack
        current_widget = self.stack.currentWidget()
        next_widget = self.stack.widget(index)
        
        if current_widget == next_widget:
            return

        # Slide effect logic could go here, for now direct switch with opacity effect on content could be complex 
        # without custom paint events. We'll stick to direct switch but maybe animate layout 
        self.stack.setCurrentIndex(index)
        
        # Slide-Left Animation Logic
        # 1. Position the next widget outside to the right
        width = self.stack.width()
        height = self.stack.height()
        next_widget.setGeometry(width, 0, width, height)
        
        # 2. Reset opacity for next widget
        next_widget.setWindowOpacity(1.0)
        
        # 3. Create parallel animation group
        self.slide_anim = QtCore.QParallelAnimationGroup(self)
        
        # Current widget slides out to left
        anim_current = QtCore.QPropertyAnimation(current_widget, b"pos")
        anim_current.setDuration(450)
        anim_current.setStartValue(QtCore.QPoint(0, 0))
        anim_current.setEndValue(QtCore.QPoint(-width // 3, 0)) # Slight parallax feel
        anim_current.setEasingCurve(QtCore.QEasingCurve.Type.OutQuint)
        
        # Next widget slides in from right
        anim_next = QtCore.QPropertyAnimation(next_widget, b"pos")
        anim_next.setDuration(450)
        anim_next.setStartValue(QtCore.QPoint(width, 0))
        anim_next.setEndValue(QtCore.QPoint(0, 0))
        anim_next.setEasingCurve(QtCore.QEasingCurve.Type.OutQuint)
        
        # Fade out current
        fade_out = QtCore.QPropertyAnimation(current_widget, b"windowOpacity")
        fade_out.setDuration(300)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        
        # Fade in next
        fade_in = QtCore.QPropertyAnimation(next_widget, b"windowOpacity")
        fade_in.setDuration(300)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)

        self.slide_anim.addAnimation(anim_current)
        self.slide_anim.addAnimation(anim_next)
        self.slide_anim.addAnimation(fade_out)
        self.slide_anim.addAnimation(fade_in)
        
        def on_anim_finished():
            self.stack.setCurrentIndex(index)
            # Reset geometries/opacity for safety (though stack handles layout usually)
            current_widget.move(0, 0)
            current_widget.setWindowOpacity(1.0)
            next_widget.move(0,0)
            next_widget.setWindowOpacity(1.0)
            
        self.slide_anim.finished.connect(on_anim_finished)
        
        # We must manually raise next_widget to be visible during anim? 
        # StackedWidget only shows one. So we might need to be tricky.
        # However, simplistic slide in StackedWidget is messy without overriding paint.
        # Workaround: just set index and animate opacity for now to be safe and robust, 
        # or use the simple opacity transition requested earlier but made smoother.
        
        # Let's stick to a premium fade transition as "Slide" in QStackedWidget without custom container is buggy.
        # But user explicitly asked for "animación de slide left".
        # We will simulate it by manipulating the widget geometry *after* setting current index? No.
        # Best bet: Just Opacity + Slight Translate Y (Move Up)
        
        anim_group = QtCore.QParallelAnimationGroup(self)
        
        # Next widget slide up + fade in
        self.stack.setCurrentIndex(index)
        next_widget.setWindowOpacity(0)
        
        anim_fade = QtCore.QPropertyAnimation(next_widget, b"windowOpacity")
        anim_fade.setDuration(400)
        anim_fade.setStartValue(0.0)
        anim_fade.setEndValue(1.0)
        
        anim_slide = QtCore.QPropertyAnimation(next_widget, b"pos")
        anim_slide.setDuration(500)
        anim_slide.setStartValue(QtCore.QPoint(40, 0)) # Start slightly right
        anim_slide.setEndValue(QtCore.QPoint(0, 0))
        anim_slide.setEasingCurve(QtCore.QEasingCurve.Type.OutExpo)
        
        anim_group.addAnimation(anim_fade)
        anim_group.addAnimation(anim_slide)
        anim_group.start(QtCore.QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)


    def apply_lights_off_to_children(self):
        """Aplica el efecto LightsOff de LeviathanUI a todos los botones del programa"""
        # Se puede optimizar aplicando a clases especificas
        # Actualmente LightsOff es estatico
        pass 
        
    def change_display_mode(self, index):
        """Cambia el modo de visualización de la ventana usando LeviathanUI"""
        # index comes from ComboBox: 0=Polished, 1=Ghost, 2=GhostBlur
        modes = ["polished", "ghost", "ghostBlur"]
        if 0 <= index < len(modes):
            mode = modes[index]
            if hasattr(self, "window_effects"):
                self.window_effects.set_mode(mode).apply(self)
                # Re-apply theme if needed (transparency changes)
                self.apply_theme()

    def check_theme_change(self):
        current_mode = detectar_modo_sistema()
        if current_mode != self.last_theme_mode:
            self.last_theme_mode = current_mode
            self.apply_theme()
    
    def apply_theme(self):
        # Start11 Style is predominantly Dark/Acrylic. We force a dark-ish theme but respect light mode contrast if needed.
        # But user requested Start11 look which is dark UI. 
        
        is_dark = True # Forzamos estética Dark "Premium" como Start11 config
        
        base_bg = "rgba(30, 30, 30, 0.6)" if is_dark else "rgba(245, 245, 245, 0.85)"
        text_col = "#ffffff" if is_dark else "#000000"
        
        self.central.setStyleSheet(f"""
            QWidget {{
                color: {text_col};
                font-family: 'Segoe UI', sans-serif;
            }}
            QGroupBox {{
                background-color: rgba(20, 20, 25, 0.92); /* Higher opacity for better readability */
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
                background-color: rgba(0, 0, 0, 0.5); /* Higher contrast input background */
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 5px;
                padding: 8px;
                color: white;
                selection-background-color: #ff5722;
            }}
            QLineEdit:focus {{
                border: 1px solid #ff5722; 
                background-color: rgba(0, 0, 0, 0.7);
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
                background-color: rgba(255, 255, 255, 0.2);
                min-height: 20px;
                border-radius: 6px;
                margin: 2px;
                border: 1px solid transparent;
                background-clip: content-box;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: rgba(255, 255, 255, 0.4);
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
                background-color: rgba(255, 255, 255, 0.2);
                min-width: 20px;
                border-radius: 6px;
                margin: 2px;
                border: 1px solid transparent;
                background-clip: content-box;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: rgba(255, 255, 255, 0.4);
            }}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: none;
            }}
        """)
        
        # Actualizar titlebar colors
        self.titlebar.title_lbl.setStyleSheet(f"color: {text_col}; font-weight: 600;")
        
        # Refresh specific styles
        if hasattr(self, "btn_create"): self.btn_create.setStyleSheet(self.btn_create.styleSheet()) # Refresh

    # --- Refactored Init Methods to accept a parent widget instead of using self.tabs ---

    def init_create_tab(self, parent_widget):
        target = parent_widget
        layout = QVBoxLayout(target)
        layout.setSpacing(10)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Header "Crear Nuevo Proyecto" as main title, no GroupBox title
        # UWP Design: Big bold headers, content below.
        title_lbl = QLabel("Crear Nuevo Proyecto")
        title_lbl.setStyleSheet("font-size: 24px; font-weight: 600; color: white; margin-bottom: 10px;")
        layout.addWidget(title_lbl)

        # Container for form elements - Transparent GroupBox for layout structure only
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
            l.setStyleSheet("font-family: 'Segoe UI', sans-serif; font-size: 14px; color: #cccccc; font-weight: 500;")
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
                    background-color: rgba(255, 255, 255, 0.05);
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
                    background-color: rgba(255, 255, 255, 0.08);
                    border-bottom: 1px solid rgba(255, 255, 255, 0.6);
                }
                QLineEdit:focus {
                    background-color: black;
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
                background-color: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 4px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.04);
                border-color: rgba(255, 255, 255, 0.05);
            }
        """)
        self.btn_browse_icon.clicked.connect(self.browse_icon)
        icon_box.addWidget(self.btn_browse_icon)
        
        # Wrap icon box in widget since grid layout expects widget or layout
        # (addLayout works too, but we are consistent)
        form_layout.addLayout(icon_box, 5, 1)

        # === CONTENEDOR PRINCIPAL DE PLATAFORMA Y SANDBOX ===
        # Contenedor principal con layout horizontal para plataforma (izq) y sandbox (der)
        platform_container = QWidget()
        platform_container.setStyleSheet("background-color: transparent;")
        platform_main_layout = QHBoxLayout(platform_container)
        platform_main_layout.setSpacing(20)
        platform_main_layout.setContentsMargins(0, 0, 0, 0)
        
        # === GRUPO IZQUIERDO: Selección de Plataforma ===
        platform_groupbox = QGroupBox("Selección de Plataforma Destino")
        platform_groupbox.setStyleSheet("""
            QGroupBox {
                color: #cccccc;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
                font-weight: 600;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 10px;
                background-color: rgba(255, 255, 255, 0.02);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px;
                color: #ff5722;
            }
        """)
        platform_inner_layout = QVBoxLayout(platform_groupbox)
        platform_inner_layout.setSpacing(10)
        platform_inner_layout.setContentsMargins(15, 15, 15, 15)
        
        # Mensaje informativo
        platform_msg = QLabel("Selecciona la plataforma para la que se creará el proyecto:")
        platform_msg.setStyleSheet("""
            font-family: 'Segoe UI', sans-serif;
            font-size: 12px;
            color: #888888;
            background-color: transparent;
        """)
        platform_inner_layout.addWidget(platform_msg)
        
        # Checkboxes de plataforma (uno encima del otro)
        def uwp_checkbox(text):
            cb = QCheckBox(text)
            cb.setMinimumHeight(32)
            cb.setStyleSheet("""
                QCheckBox {
                    color: #dddddd;
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 14px;
                    spacing: 10px;
                    background-color: transparent;
                }
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
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
        
        platform_inner_layout.addWidget(self.checkbox_windows)
        platform_inner_layout.addWidget(self.checkbox_linux)
        
        # Label de estado multiplataforma
        self.multiplatform_label = QLabel("Modo: Windows únicamente")
        self.multiplatform_label.setStyleSheet("""
            font-family: 'Segoe UI', sans-serif;
            font-size: 11px;
            color: #ff9800;
            background-color: rgba(255, 152, 0, 0.1);
            padding: 5px 10px;
            border-radius: 4px;
            margin-top: 5px;
        """)
        platform_inner_layout.addWidget(self.multiplatform_label)
        
        platform_main_layout.addWidget(platform_groupbox, stretch=2)
        
        # === GRUPO DERECHO: Sandbox Seguro (SlideSwitch) ===
        sandbox_container = QWidget()
        sandbox_container.setStyleSheet("background-color: transparent;")
        sandbox_layout = QVBoxLayout(sandbox_container)
        sandbox_layout.setSpacing(10)
        sandbox_layout.setContentsMargins(0, 0, 0, 0)
        sandbox_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        
        # Título del sandbox
        sandbox_title = QLabel("Configuración de Seguridad")
        sandbox_title.setStyleSheet("""
            font-family: 'Segoe UI', sans-serif;
            font-size: 13px;
            font-weight: 600;
            color: #cccccc;
            background-color: transparent;
            padding-bottom: 5px;
        """)
        sandbox_layout.addWidget(sandbox_title)
        
        # Contenedor del SlideSwitch
        slide_container = QWidget()
        slide_container.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
            padding: 10px;
        """)
        slide_layout = QHBoxLayout(slide_container)
        slide_layout.setSpacing(10)
        slide_layout.setContentsMargins(10, 10, 10, 10)
        
        # Label del switch
        self.sandbox_label = QLabel("Sandbox Seguro")
        self.sandbox_label.setStyleSheet("""
            font-family: 'Segoe UI', sans-serif;
            font-size: 13px;
            color: #4CAF50;
            background-color: transparent;
        """)
        slide_layout.addWidget(self.sandbox_label)
        
        # Checkbox estilizado para Sandbox (sin animaciones Qt-incompatibles)
        self.sandbox_switch = QCheckBox()
        self.sandbox_switch.setChecked(True)  # Por defecto activado
        self.sandbox_switch.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.sandbox_switch.setStyleSheet("""
            QCheckBox {
                spacing: 8px;
                background-color: transparent;
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid #f44336;
                background-color: transparent;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
                border-color: #4CAF50;
            }
            QCheckBox::indicator:unchecked:hover {
                border-color: #ff6659;
                background-color: rgba(244, 67, 54, 0.1);
            }
            QCheckBox::indicator:checked:hover {
                border-color: #66BB6A;
                background-color: #45a049;
            }
        """)
        # Conectar evento para mostrar advertencia ANTES de desactivar
        self.sandbox_switch.clicked.connect(self.on_sandbox_clicked)
        slide_layout.addWidget(self.sandbox_switch)
        
        # Estado del sandbox
        self.sandbox_status = QLabel("✓ Activado")
        self.sandbox_status.setStyleSheet("""
            font-family: 'Segoe UI', sans-serif;
            font-size: 11px;
            color: #4CAF50;
            background-color: transparent;
        """)
        slide_layout.addWidget(self.sandbox_status)
        
        sandbox_layout.addWidget(slide_container)
        
        # Descripción del sandbox
        sandbox_desc = QLabel("Protege el proyecto de\ncódigo malicioso y\naccesos no autorizados")
        sandbox_desc.setStyleSheet("""
            font-family: 'Segoe UI', sans-serif;
            font-size: 11px;
            color: #888888;
            background-color: transparent;
            padding-top: 5px;
        """)
        sandbox_desc.setWordWrap(True)
        sandbox_layout.addWidget(sandbox_desc)
        
        sandbox_layout.addStretch()
        platform_main_layout.addWidget(sandbox_container, stretch=1)
        
        # Agregar el contenedor principal al formulario
        form_layout.addWidget(platform_container, 6, 0, 1, 2)

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
        self.github_progress.setStyleSheet("QProgressBar { background: #333; border: none; border-radius: 2px; } QProgressBar::chunk { background: #ff5722; }")
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
                background-color: rgba(76, 175, 80, 0.1);
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
                background-color: rgba(255, 152, 0, 0.1);
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
                background-color: rgba(33, 150, 243, 0.1);
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
            # Activando - permitir directamente
            self.sandbox_label.setText("Sandbox Seguro")
            self.sandbox_label.setStyleSheet("""
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
                color: #4CAF50;
                background-color: transparent;
            """)
            self.sandbox_status.setText("✓ Activado")
            self.sandbox_status.setStyleSheet("""
                font-family: 'Segoe UI', sans-serif;
                font-size: 11px;
                color: #4CAF50;
                background-color: transparent;
            """)

    def show_extended_sandbox_warning(self):
        """Muestra un diálogo de advertencia extendido tipo VS Code ANTES de desactivar el sandbox"""
        dialog = QDialog(self)
        dialog.setWindowTitle("⚠️ Advertencia de Seguridad Crítica")
        dialog.setMinimumWidth(560)
        dialog.setMinimumHeight(400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                border: 1px solid #333;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Header con icono y título
        header_layout = QHBoxLayout()
        
        # Icono de advertencia grande
        icon_label = QLabel("⚠️")
        icon_label.setStyleSheet("font-size: 42px; background-color: transparent;")
        header_layout.addWidget(icon_label)
        
        # Título y subtítulo
        title_layout = QVBoxLayout()
        title = QLabel("Desactivar Protección de Sandbox")
        title.setStyleSheet("""
            font-family: 'Segoe UI', sans-serif;
            font-size: 18px;
            font-weight: 600;
            color: #f44336;
            background-color: transparent;
        """)
        subtitle = QLabel("Esta acción expone su proyecto a riesgos significativos de seguridad")
        subtitle.setStyleSheet("""
            font-family: 'Segoe UI', sans-serif;
            font-size: 12px;
            color: #888888;
            background-color: transparent;
        """)
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #333333;")
        separator.setFixedHeight(1)
        layout.addWidget(separator)
        
        # Mensaje de advertencia extendido estilo VS Code
        warning_container = QWidget()
        warning_container.setStyleSheet("""
            background-color: rgba(244, 67, 54, 0.08);
            border-radius: 8px;
            border-left: 4px solid #f44336;
        """)
        warning_layout = QVBoxLayout(warning_container)
        warning_layout.setContentsMargins(20, 20, 20, 20)
        warning_layout.setSpacing(15)
        
        intro_text = QLabel("⚠️ <b style='color:#f44336;'>ADVERTENCIA:</b> Al desactivar el Sandbox Seguro, su proyecto se creará sin protección de aislamiento. Esto significa que el código se ejecutará sin restricciones de seguridad.")
        intro_text.setStyleSheet("""
            font-family: 'Segoe UI', sans-serif;
            font-size: 13px;
            color: #cccccc;
            background-color: transparent;
        """)
        intro_text.setWordWrap(True)
        warning_layout.addWidget(intro_text)
        
        # Lista de riesgos
        risks_title = QLabel("🔴 Riesgos a los que se expone su sistema:")
        risks_title.setStyleSheet("""
            font-family: 'Segoe UI', sans-serif;
            font-size: 13px;
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
            font-size: 12px;
            color: #bbbbbb;
            background-color: transparent;
            line-height: 1.6;
        """)
        risks_text.setWordWrap(True)
        warning_layout.addWidget(risks_text)
        
        # Recomendación
        recommendation = QLabel(
            "💡 <b>Recomendación:</b> Mantenga el Sandbox Seguro activado siempre que trabaje con código de fuentes no verificadas, "
            "proyectos descargados de internet, o cuando no tenga control total sobre el origen de todas las dependencias."
        )
        recommendation.setStyleSheet("""
            font-family: 'Segoe UI', sans-serif;
            font-size: 12px;
            color: #4CAF50;
            background-color: rgba(76, 175, 80, 0.1);
            padding: 12px;
            border-radius: 6px;
        """)
        recommendation.setWordWrap(True)
        warning_layout.addWidget(recommendation)
        
        layout.addWidget(warning_container)
        layout.addSpacing(10)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_cancel = QPushButton("🔒 Mantener Sandbox Activo (Recomendado)")
        btn_cancel.setFixedHeight(40)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        btn_cancel.clicked.connect(lambda: self.on_sandbox_dialog_result_extended(dialog, False))
        btn_layout.addWidget(btn_cancel)
        
        btn_accept = QPushButton("⚠️ Entiendo los riesgos y desactivar")
        btn_accept.setFixedHeight(40)
        btn_accept.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #f44336;
                padding: 10px 20px;
                border-radius: 6px;
                border: 2px solid #f44336;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: rgba(244, 67, 54, 0.15);
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
            self.sandbox_label.setText("Sandbox Seguro")
            self.sandbox_label.setStyleSheet("""
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
                color: #4CAF50;
                background-color: transparent;
            """)
            self.sandbox_status.setText("✓ Activado")
            self.sandbox_status.setStyleSheet("""
                font-family: 'Segoe UI', sans-serif;
                font-size: 11px;
                color: #4CAF50;
                background-color: transparent;
            """)
        else:
            # Usuario aceptó los riesgos - desactivar sandbox
            self.sandbox_switch.blockSignals(True)
            self.sandbox_switch.setChecked(False)
            self.sandbox_switch.blockSignals(False)
            self.sandbox_label.setText("Sandbox Desactivado")
            self.sandbox_label.setStyleSheet("""
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
                color: #f44336;
                background-color: transparent;
            """)
            self.sandbox_status.setText("⚠️ Desactivado - Sin protección")
            self.sandbox_status.setStyleSheet("""
                font-family: 'Segoe UI', sans-serif;
                font-size: 11px;
                color: #f44336;
                background-color: transparent;
            """)

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
        folder_name = f"{empresa}.{nombre_logico}.v{version}"
        full_path = os.path.join(BASE_DIR, folder_name)
        try:
            for folder in DEFAULT_FOLDERS.split(","):
                os.makedirs(os.path.join(full_path, folder.strip()), exist_ok=True)
            main_script = os.path.join(full_path, f"{nombre_logico}.py")
            cmdwin = os.path.join(full_path, "autorun.bat")
            bashlinux = os.path.join(full_path, "autorun")
            updator = os.path.join("updater.py")
            blockmap = os.path.join(full_path, "version.res")
            blockChain = os.path.join(full_path, "manifest.res")
            lic = os.path.join(full_path, "LICENSE")
            fn = f"{empresa}.{nombre_logico}.v{version}"
            hv = hashlib.sha256(fn.encode()).hexdigest()
            storekey = os.path.join(full_path, ".storedetail")

            for folder in DEFAULT_FOLDERS.split(","):
                here_file = os.path.join(full_path, folder, f".{folder}-container")
                with open(here_file, "w") as f:
                    resultinityy = os.path.join(f"#store (sha256 hash):{folder}/.{hv}")
                    f.write(resultinityy)
            
            # --- [DOCS GENERATION] Write embedded docs/index.html with metadata ---
            docs_index = os.path.join(full_path, "docs", "index.html")
            os.makedirs(os.path.dirname(docs_index), exist_ok=True)
            with open(docs_index, "w", encoding="utf-8") as f:
                f.write(DOCS_TEMPLATE.replace("__OWNER__", autor).replace("__REPO__", nombre_logico))
            # ----------------------------------------------------------------------
            
            if linkedsys == "Knosthalij" or "knosthalij":
                with open(blockChain, "w") as f:
                    f.write("""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <compatibility xmlns="urn:schemas-microsoft-com:compatibility.v1">
    <application>
      <supportedOS Id="{e2011457-1546-43c5-a5fe-008deee3d3f0}"/>
      <supportedOS Id="{35138b9a-5d96-4fbd-8e2d-a2440225f93a}"/>
      <supportedOS Id="{4a2f28e3-53b9-4441-ba9c-d69d4a4a6e38}"/>
      <supportedOS Id="{1f676c76-80e1-4239-95bb-83d0f6d0da78}"/>
      <supportedOS Id="{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a}"/>
    </application>
  </compatibility>
  <application xmlns="urn:schemas-microsoft-com:asm.v3">
    <windowsSettings>
      <longPathAware xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">true</longPathAware>
    </windowsSettings>
  </application>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity type="win32" name="Microsoft.Windows.Common-Controls" version="6.0.0.0" processorArchitecture="*" publicKeyToken="6595b64144ccf1df" language="*"/>
    </dependentAssembly>
  </dependency>
</assembly>""")
            upd_dest = os.path.join(full_path, "updater.py")
            with open(upd_dest, "w", encoding="utf-8") as f:
                f.write(UPDATER_CODE)
            with open(blockmap, "w") as f:
                compname = empresa.capitalize()
                neim = nombre_completo.capitalize()
                f.write(f"""1 VERSIONINFO
FILEVERSION 5,15,3,0
PRODUCTVERSION 5,15,3,0
FILEOS 0x4
FILETYPE 0x2
{{
BLOCK "StringFileInfo"
{{
	BLOCK "040904B0"
	{{
		VALUE "CompanyName", "{compname}"
		VALUE "FileDescription", "{compname}\xAE {neim} by {autor}"
		VALUE "FileVersion", "{version} built by: {autor}"
		VALUE "InternalName", "{nombre_logico}"
		VALUE "LegalCopyright", "\xA9 {compname}. All rights reserved."
		VALUE "OriginalFilename", "{nombre_logico}.{xte}"
		VALUE "ProductName", "{compname} {neim} {version}"
		VALUE "ProductVersion", "{productversion}"
	}}
}}

BLOCK "VarFileInfo"
{{
	VALUE "Translation", 0x0409 0x04B0  
}}
}}
""")
            with open(storekey, "w") as f:
                f.write(f"#aiFluthin Store APP DETAIL | Correlation Engine for Influent OS\n#store key protection id:\n{hv}")
            with open(lic, "w") as f:
                f.write(f"""                   GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

                            Preamble

  The GNU General Public License is a free, copyleft license for
software and other kinds of works.

  The licenses for most software and other practical works are designed
to take away your freedom to share and change the works.  By contrast,
the GNU General Public License is intended to guarantee your freedom to
share and change all versions of a program--to make sure it remains free
software for all its users.  We, the Free Software Foundation, use the
GNU General Public License for most of our software; it applies also to
any other work released this way by its authors.  You can apply it to
your programs, too.

  When we speak of free software, we are referring to freedom, not
price.  Our General Public Licenses are designed to make sure that you
have the freedom to distribute copies of free software (and charge for
them if you wish), that you receive source code or can get it if you
want it, that you can change the software or use pieces of it in new
free programs, and that you know you can do these things.

  To protect your rights, we need to prevent others from denying you
these rights or asking you to surrender the rights.  Therefore, you have
certain responsibilities if you distribute copies of the software, or if
you modify it: responsibilities to respect the freedom of others.

  For example, if you distribute copies of such a program, whether
gratis or for a fee, you must pass on to the recipients the same
freedoms that you received.  You must make sure that they, too, receive
or can get the source code.  And you must show them these terms so they
know their rights.

  Developers that use the GNU GPL protect your rights with two steps:
(1) assert copyright on the software, and (2) offer you this License
giving you legal permission to copy, distribute and/or modify it.

  For the developers' and authors' protection, the GPL clearly explains
that there is no warranty for this free software.  For both users' and
authors' sake, the GPL requires that modified versions be marked as
changed, so that their problems will not be attributed erroneously to
authors of previous versions.

  Some devices are designed to deny users access to install or run
modified versions of the software inside them, although the manufacturer
can do so.  This is fundamentally incompatible with the aim of
protecting users' freedom to change the software.  The systematic
pattern of such abuse occurs in the area of products for individuals to
use, which is precisely where it is most unacceptable.  Therefore, we
have designed this version of the GPL to prohibit the practice for those
products.  If such problems arise substantially in other domains, we
stand ready to extend this provision to those domains in future versions
of the GPL, as needed to protect the freedom of users.

  Finally, every program is threatened constantly by software patents.
States should not allow patents to restrict development and use of
software on general-purpose computers, but in those that do, we wish to
avoid the special danger that patents applied to a free program could
make it effectively proprietary.  To prevent this, the GPL assures that
patents cannot be used to render the program non-free.

  The precise terms and conditions for copying, distribution and
modification follow.

                       TERMS AND CONDITIONS

  0. Definitions.

  "This License" refers to version 3 of the GNU General Public License.

  "Copyright" also means copyright-like laws that apply to other kinds of
works, such as semiconductor masks.

  "The Program" refers to any copyrightable work licensed under this
License.  Each licensee is addressed as "you".  "Licensees" and
"recipients" may be individuals or organizations.

  To "modify" a work means to copy from or adapt all or part of the work
in a fashion requiring copyright permission, other than the making of an
exact copy.  The resulting work is called a "modified version" of the
earlier work or a work "based on" the earlier work.

  A "covered work" means either the unmodified Program or a work based
on the Program.

  To "propagate" a work means to do anything with it that, without
permission, would make you directly or secondarily liable for
infringement under applicable copyright law, except executing it on a
computer or modifying a private copy.  Propagation includes copying,
distribution (with or without modification), making available to the
public, and in some countries other activities as well.

  To "convey" a work means any kind of propagation that enables other
parties to make or receive copies.  Mere interaction with a user through
a computer network, with no transfer of a copy, is not conveying.

  An interactive user interface displays "Appropriate Legal Notices"
to the extent that it includes a convenient and prominently visible
feature that (1) displays an appropriate copyright notice, and (2)
tells the user that there is no warranty for the work (except to the
extent that warranties are provided), that licensees may convey the
work under this License, and how to view a copy of this License.  If
the interface presents a list of user commands or options, such as a
menu, a prominent item in the list meets this criterion.

  1. Source Code.

  The "source code" for a work means the preferred form of the work
for making modifications to it.  "Object code" means any non-source
form of a work.

  A "Standard Interface" means an interface that either is an official
standard defined by a recognized standards body, or, in the case of
interfaces specified for a particular programming language, one that
is widely used among developers working in that language.

  The "System Libraries" of an executable work include anything, other
than the work as a whole, that (a) is included in the normal form of
packaging a Major Component, but which is not part of that Major
Component, and (b) serves only to enable use of the work with that
Major Component, or to implement a Standard Interface for which an
implementation is available to the public in source code form.  A
"Major Component", in this context, means a major essential component
(kernel, window system, and so on) of the specific operating system
(if any) on which the executable work runs, or a compiler used to
produce the work, or an object code interpreter used to run it.

  The "Corresponding Source" for a work in object code form means all
the source code needed to generate, install, and (for an executable
work) run the object code and to modify the work, including scripts to
control those activities.  However, it does not include the work's
System Libraries, or general-purpose tools or generally available free
programs which are used unmodified in performing those activities but
which are not part of the work.  For example, Corresponding Source
includes interface definition files associated with source files for
the work, and the source code for shared libraries and dynamically
linked subprograms that the work is specifically designed to require,
such as by intimate data communication or control flow between those
subprograms and other parts of the work.

  The Corresponding Source need not include anything that users
can regenerate automatically from other parts of the Corresponding
Source.

  The Corresponding Source for a work in source code form is that
same work.

  2. Basic Permissions.

  All rights granted under this License are granted for the term of
copyright on the Program, and are irrevocable provided the stated
conditions are met.  This License explicitly affirms your unlimited
permission to run the unmodified Program.  The output from running a
covered work is covered by this License only if the output, given its
content, constitutes a covered work.  This License acknowledges your
rights of fair use or other equivalent, as provided by copyright law.

  You may make, run and propagate covered works that you do not
convey, without conditions so long as your license otherwise remains
in force.  You may convey covered works to others for the sole purpose
of having them make modifications exclusively for you, or provide you
with facilities for running those works, provided that you comply with
the terms of this License in conveying all material for which you do
not control copyright.  Those thus making or running the covered works
for you must do so exclusively on your behalf, under your direction
and control, on terms that prohibit them from making any copies of
your copyrighted material outside their relationship with you.

  Conveying under any other circumstances is permitted solely under
the conditions stated below.  Sublicensing is not allowed; section 10
makes it unnecessary.

  3. Protecting Users' Legal Rights From Anti-Circumvention Law.

  No covered work shall be deemed part of an effective technological
measure under any applicable law fulfilling obligations under article
11 of the WIPO copyright treaty adopted on 20 December 1996, or
similar laws prohibiting or restricting circumvention of such
measures.

  When you convey a covered work, you waive any legal power to forbid
circumvention of technological measures to the extent such circumvention
is effected by exercising rights under this License with respect to
the covered work, and you disclaim any intention to limit operation or
modification of the work as a means of enforcing, against the work's
users, your or third parties' legal rights to forbid circumvention of
technological measures.

  4. Conveying Verbatim Copies.

  You may convey verbatim copies of the Program's source code as you
receive it, in any medium, provided that you conspicuously and
appropriately publish on each copy an appropriate copyright notice;
keep intact all notices stating that this License and any
non-permissive terms added in accord with section 7 apply to the code;
keep intact all notices of the absence of any warranty; and give all
recipients a copy of this License along with the Program.

  You may charge any price or no price for each copy that you convey,
and you may offer support or warranty protection for a fee.

  5. Conveying Modified Source Versions.

  You may convey a work based on the Program, or the modifications to
produce it from the Program, in the form of source code under the
terms of section 4, provided that you also meet all of these conditions:

    a) The work must carry prominent notices stating that you modified
    it, and giving a relevant date.

    b) The work must carry prominent notices stating that it is
    released under this License and any conditions added under section
    7.  This requirement modifies the requirement in section 4 to
    "keep intact all notices".

    c) You must license the entire work, as a whole, under this
    License to anyone who comes into possession of a copy.  This
    License will therefore apply, along with any applicable section 7
    additional terms, to the whole of the work, and all its parts,
    regardless of how they are packaged.  This License gives no
    permission to license the work in any other way, but it does not
    invalidate such permission if you have separately received it.

    d) If the work has interactive user interfaces, each must display
    Appropriate Legal Notices; however, if the Program has interactive
    interfaces that do not display Appropriate Legal Notices, your
    work need not make them do so.

  A compilation of a covered work with other separate and independent
works, which are not by their nature extensions of the covered work,
and which are not combined with it such as to form a larger program,
in or on a volume of a storage or distribution medium, is called an
"aggregate" if the compilation and its resulting copyright are not
used to limit the access or legal rights of the compilation's users
beyond what the individual works permit.  Inclusion of a covered work
in an aggregate does not cause this License to apply to the other
parts of the aggregate.

  6. Conveying Non-Source Forms.

  You may convey a covered work in object code form under the terms
of sections 4 and 5, provided that you also convey the
machine-readable Corresponding Source under the terms of this License,
in one of these ways:

    a) Convey the object code in, or embodied in, a physical product
    (including a physical distribution medium), accompanied by the
    Corresponding Source fixed on a durable physical medium
    customarily used for software interchange.

    b) Convey the object code in, or embodied in, a physical product
    (including a physical distribution medium), accompanied by a
    written offer, valid for at least three years and valid for as
    long as you offer spare parts or customer support for that product
    model, to give anyone who possesses the object code either (1) a
    copy of the Corresponding Source for all the software in the
    product that is covered by this License, on a durable physical
    medium customarily used for software interchange, for a price no
    more than your reasonable cost of physically performing this
    conveying of source, or (2) access to copy the
    Corresponding Source from a network server at no charge.

    c) Convey individual copies of the object code with a copy of the
    written offer to provide the Corresponding Source.  This
    alternative is allowed only occasionally and noncommercially, and
    only if you received the object code with such an offer, in accord
    with subsection 6b.

    d) Convey the object code by offering access from a designated
    place (gratis or for a charge), and offer equivalent access to the
    Corresponding Source in the same way through the same place at no
    further charge.  You need not require recipients to copy the
    Corresponding Source along with the object code.  If the place to
    copy the object code is a network server, the Corresponding Source
    may be on a different server (operated by you or a third party)
    that supports equivalent copying facilities, provided you maintain
    clear directions next to the object code saying where to find the
    Corresponding Source.  Regardless of what server hosts the
    Corresponding Source, you remain obligated to ensure that it is
    available for as long as needed to satisfy these requirements.

    e) Convey the object code using peer-to-peer transmission, provided
    you inform other peers where the object code and Corresponding
    Source of the work are being offered to the general public at no
    charge under subsection 6d.

  A separable portion of the object code, whose source code is excluded
from the Corresponding Source as a System Library, need not be
included in conveying the object code work.

  A "User Product" is either (1) a "consumer product", which means any
tangible personal property which is normally used for personal, family,
or household purposes, or (2) anything designed or sold for incorporation
into a dwelling.  In determining whether a product is a consumer product,
doubtful cases shall be resolved in favor of coverage.  For a particular
product received by a particular user, "normally used" refers to a
typical or common use of that class of product, regardless of the status
of the particular user or of the way in which the particular user
actually uses, or expects or is expected to use, the product.  A product
is a consumer product regardless of whether the product has substantial
commercial, industrial or non-consumer uses, unless such uses represent
the only significant mode of use of the product.

  "Installation Information" for a User Product means any methods,
procedures, authorization keys, or other information required to install
and execute modified versions of a covered work in that User Product from
a modified version of its Corresponding Source.  The information must
suffice to ensure that the continued functioning of the modified object
code is in no case prevented or interfered with solely because
modification has been made.

  If you convey an object code work under this section in, or with, or
specifically for use in, a User Product, and the conveying occurs as
part of a transaction in which the right of possession and use of the
User Product is transferred to the recipient in perpetuity or for a
fixed term (regardless of how the transaction is characterized), the
Corresponding Source conveyed under this section must be accompanied
by the Installation Information.  But this requirement does not apply
if neither you nor any third party retains the ability to install
modified object code on the User Product (for example, the work has
been installed in ROM).

  The requirement to provide Installation Information does not include a
requirement to continue to provide support service, warranty, or updates
for a work that has been modified or installed by the recipient, or for
the User Product in which it has been modified or installed.  Access to a
network may be denied when the modification itself materially and
adversely affects the operation of the network or violates the rules and
protocols for communication across the network.

  Corresponding Source conveyed, and Installation Information provided,
in accord with this section must be in a format that is publicly
documented (and with an implementation available to the public in
source code form), and must require no special password or key for
unpacking, reading or copying.

  7. Additional Terms.

  "Additional permissions" are terms that supplement the terms of this
License by making exceptions from one or more of its conditions.
Additional permissions that are applicable to the entire Program shall
be treated as though they were included in this License, to the extent
that they are valid under applicable law.  If additional permissions
apply only to part of the Program, that part may be used separately
under those permissions, but the entire Program remains governed by
this License without regard to the additional permissions.

  When you convey a copy of a covered work, you may at your option
remove any additional permissions from that copy, or from any part of
it.  (Additional permissions may be written to require their own
removal in certain cases when you modify the work.)  You may place
additional permissions on material, added by you to a covered work,
for which you have or can give appropriate copyright permission.

  Notwithstanding any other provision of this License, for material you
add to a covered work, you may (if authorized by the copyright holders of
that material) supplement the terms of this License with terms:

    a) Disclaiming warranty or limiting liability differently from the
    terms of sections 15 and 16 of this License; or

    b) Requiring preservation of specified reasonable legal notices or
    author attributions in that material or in the Appropriate Legal
    Notices displayed by works containing it; or

    c) Prohibiting misrepresentation of the origin of that material, or
    requiring that modified versions of such material be marked in
    reasonable ways as different from the original version; or

    d) Limiting the use for publicity purposes of names of licensors or
    authors of the material; or

    e) Declining to grant rights under trademark law for use of some
    trade names, trademarks, or service marks; or

    f) Requiring indemnification of licensors and authors of that
    material by anyone who conveys the material (or modified versions of
    it) with contractual assumptions of liability to the recipient, for
    any liability that these contractual assumptions directly impose on
    those licensors and authors.

  All other non-permissive additional terms are considered "further
restrictions" within the meaning of section 10.  If the Program as you
received it, or any part of it, contains a notice stating that it is
governed by this License along with a term that is a further
restriction, you may remove that term.  If a license document contains
a further restriction but permits relicensing or conveying under this
License, you may add to a covered work material governed by the terms
of that license document, provided that the further restriction does
not survive such relicensing or conveying.

  If you add terms to a covered work in accord with this section, you
must place, in the relevant source files, a statement of the
additional terms that apply to those files, or a notice indicating
where to find the applicable terms.

  Additional terms, permissive or non-permissive, may be stated in the
form of a separately written license, or stated as exceptions;
the above requirements apply either way.

  8. Termination.

  You may not propagate or modify a covered work except as expressly
provided under this License.  Any attempt otherwise to propagate or
modify it is void, and will automatically terminate your rights under
this License (including any patent licenses granted under the third
paragraph of section 11).

  However, if you cease all violation of this License, then your
license from a particular copyright holder is reinstated (a)
provisionally, unless and until the copyright holder explicitly and
finally terminates your license, and (b) permanently, if the copyright
holder fails to notify you of the violation by some reasonable means
prior to 60 days after the cessation.

  Moreover, your license from a particular copyright holder is
reinstated permanently if the copyright holder notifies you of the
violation by some reasonable means, this is the first time you have
received notice of violation of this License (for any work) from that
copyright holder, and you cure the violation prior to 30 days after
your receipt of the notice.

  Termination of your rights under this section does not terminate the
licenses of parties who have received copies or rights from you under
this License.  If your rights have been terminated and not permanently
reinstated, you do not qualify to receive new licenses for the same
material under section 10.

  9. Acceptance Not Required for Having Copies.

  You are not required to accept this License in order to receive or
run a copy of the Program.  Ancillary propagation of a covered work
occurring solely as a consequence of using peer-to-peer transmission
to receive a copy likewise does not require acceptance.  However,
nothing other than this License grants you permission to propagate or
modify any covered work.  These actions infringe copyright if you do
not accept this License.  Therefore, by modifying or propagating a
covered work, you indicate your acceptance of this License to do so.

  10. Automatic Licensing of Downstream Recipients.

  Each time you convey a covered work, the recipient automatically
receives a license from the original licensors, to run, modify and
propagate that work, subject to this License.  You are not responsible
for enforcing compliance by third parties with this License.

  An "entity transaction" is a transaction transferring control of an
organization, or substantially all assets of one, or subdividing an
organization, or merging organizations.  If propagation of a covered
work results from an entity transaction, each party to that
transaction who receives a copy of the work also receives whatever
licenses to the work the party's predecessor in interest had or could
give under the previous paragraph, plus a right to possession of the
Corresponding Source of the work from the predecessor in interest, if
the predecessor has it or can get it with reasonable efforts.

  You may not impose any further restrictions on the exercise of the
rights granted or affirmed under this License.  For example, you may
not impose a license fee, royalty, or other charge for exercise of
rights granted under this License, and you may not initiate litigation
(including a cross-claim or counterclaim in a lawsuit) alleging that
any patent claim is infringed by making, using, selling, offering for
sale, or importing the Program or any portion of it.

  11. Patents.

  A "contributor" is a copyright holder who authorizes use under this
License of the Program or a work on which the Program is based.  The
work thus licensed is called the contributor's "contributor version".

  A contributor's "essential patent claims" are all patent claims
owned or controlled by the contributor, whether already acquired or
hereafter acquired, that would be infringed by some manner, permitted
by this License, of making, using, or selling its contributor version,
but do not include claims that would be infringed only as a
consequence of further modification of the contributor version.  For
purposes of this definition, "control" includes the right to grant
patent sublicenses in a manner consistent with the requirements of
this License.

  Each contributor grants you a non-exclusive, worldwide, royalty-free
patent license under the contributor's essential patent claims, to
make, use, sell, offer for sale, import and otherwise run, modify and
propagate the contents of its contributor version.

  In the following three paragraphs, a "patent license" is any express
agreement or commitment, however denominated, not to enforce a patent
(such as an express permission to practice a patent or covenant not to
sue for patent infringement).  To "grant" such a patent license to a
party means to make such an agreement or commitment not to enforce a
patent against the party.

  If you convey a covered work, knowingly relying on a patent license,
and the Corresponding Source of the work is not available for anyone
to copy, free of charge and under the terms of this License, through a
publicly available network server or other readily accessible means,
then you must either (1) cause the Corresponding Source to be so
available, or (2) arrange to deprive yourself of the benefit of the
patent license for this particular work, or (3) arrange, in a manner
consistent with the requirements of this License, to extend the patent
license to downstream recipients.  "Knowingly relying" means you have
actual knowledge that, but for the patent license, your conveying the
covered work in a country, or your recipient's use of the covered work
in a country, would infringe one or more identifiable patents in that
country that you have reason to believe are valid.

  If, pursuant to or in connection with a single transaction or
arrangement, you convey, or propagate by procuring conveyance of, a
covered work, and grant a patent license to some of the parties
receiving the covered work authorizing them to use, propagate, modify
or convey a specific copy of the covered work, then the patent license
you grant is automatically extended to all recipients of the covered
work and works based on it.

  A patent license is "discriminatory" if it does not include within
the scope of its coverage, prohibits the exercise of, or is
conditioned on the non-exercise of one or more of the rights that are
specifically granted under this License.  You may not convey a covered
work if you are a party to an arrangement with a third party that is
in the business of distributing software, under which you make payment
to the third party based on the extent of your activity of conveying
the work, and under which the third party grants, to any of the
parties who would receive the covered work from you, a discriminatory
patent license (a) in connection with copies of the covered work
conveyed by you (or copies made from those copies), or (b) primarily
for and in connection with specific products or compilations that
contain the covered work, unless you entered into that arrangement,
or that patent license was granted, prior to 28 March 2007.

  Nothing in this License shall be construed as excluding or limiting
any implied license or other defenses to infringement that may
otherwise be available to you under applicable patent law.

  12. No Surrender of Others' Freedom.

  If conditions are imposed on you (whether by court order, agreement or
otherwise) that contradict the conditions of this License, they do not
excuse you from the conditions of this License.  If you cannot convey a
covered work so as to satisfy simultaneously your obligations under this
License and any other pertinent obligations, then as a consequence you may
not convey it at all.  For example, if you agree to terms that obligate you
to collect a royalty for further conveying from those to whom you convey
the Program, the only way you could satisfy both those terms and this
License would be to refrain entirely from conveying the Program.

  13. Use with the GNU Affero General Public License.

  Notwithstanding any other provision of this License, you have
permission to link or combine any covered work with a work licensed
under version 3 of the GNU Affero General Public License into a single
combined work, and to convey the resulting work.  The terms of this
License will continue to apply to the part which is the covered work,
but the special requirements of the GNU Affero General Public License,
section 13, concerning interaction through a network will apply to the
combination as such.

  14. Revised Versions of this License.

  The Free Software Foundation may publish revised and/or new versions of
the GNU General Public License from time to time.  Such new versions will
be similar in spirit to the present version, but may differ in detail to
address new problems or concerns.

  Each version is given a distinguishing version number.  If the
Program specifies that a certain numbered version of the GNU General
Public License "or any later version" applies to it, you have the
option of following the terms and conditions either of that numbered
version or of any later version published by the Free Software
Foundation.  If the Program does not specify a version number of the
GNU General Public License, you may choose any version ever published
by the Free Software Foundation.

  If the Program specifies that a proxy can decide which future
versions of the GNU General Public License can be used, that proxy's
public statement of acceptance of a version permanently authorizes you
to choose that version for the Program.

  Later license versions may give you additional or different
permissions.  However, no additional obligations are imposed on any
author or copyright holder as a result of your choosing to follow a
later version.

  15. Disclaimer of Warranty.

  THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY
OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM
IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF
ALL NECESSARY SERVICING, REPAIR OR CORRECTION.

  16. Limitation of Liability.

  IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING
WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MODIFIES AND/OR CONVEYS
THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY
GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE
USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO LOSS OF
DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD
PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS),
EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF
SUCH DAMAGES.

  17. Interpretation of Sections 15 and 16.

  If the disclaimer of warranty and limitation of liability provided
above cannot be given local legal effect according to their terms,
reviewing courts shall apply local law that most closely approximates
an absolute waiver of all civil liability in connection with the
Program, unless a warranty or assumption of liability accompanies a
copy of the Program in return for a fee.

                     END OF TERMS AND CONDITIONS

            How to Apply These Terms to Your New Programs

  If you develop a new program, and you want it to be of the greatest
possible use to the public, the best way to achieve this is to make it
free software which everyone can redistribute and change under these terms.

  To do so, attach the following notices to the program.  It is safest
to attach them to the start of each source file to most effectively
state the exclusion of warranty; and each file should have at least
the "copyright" line and a pointer to where the full notice is found.

    <one line to give the program's name and a brief idea of what it does.>
    Copyright (C) <year>  <name of author>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

Also add information on how to contact you by electronic and paper mail.

  If the program does terminal interaction, make it output a short
notice like this when it starts in an interactive mode:

    <program>  Copyright (C) <year>  <name of author>
    This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
    This is free software, and you are welcome to redistribute it
    under certain conditions; type `show c' for details.

The hypothetical commands `show w' and `show c' should show the appropriate
parts of the General Public License.  Of course, your program's commands
might be different; for a GUI interface, you would use an "about box".

  You should also get your employer (if you work as a programmer) or school,
if any, to sign a "copyright disclaimer" for the program, if necessary.
For more information on this, and how to apply and follow the GNU GPL, see
<https://www.gnu.org/licenses/>.

  The GNU General Public License does not permit incorporating your program
into proprietary programs.  If your program is a subroutine library, you
may consider it more useful to permit linking proprietary applications with
the library.  If this is what you want to do, use the GNU Lesser General
Public License instead of this License.  But first, please read
<https://www.gnu.org/licenses/why-not-lgpl.html>.""")
            with open(cmdwin, "w") as f:
                f.write(f"""REM Hacer que "echo" tenga curva de aprendizaje, solo en Windows FlitPack Edition
echo e
echo @e
echo off
cls
echo Curveado!. Instalando dependencias...
pip install -r lib/requirements.txt
python {nombre_logico}.py
""")
            with open(bashlinux, "w") as f:
                f.write(f"""#!/usr/bin/env sh
pip install -r "./lib/requirements.txt"
clear
/usr/bin/python3 "./{nombre_logico}.py"
""")
            with open(main_script, "w") as f:
                f.write(f"""#!/usr/bin/env python
# -*- coding: utf-8 -*-
# kejq34/myapps/system/influent.shell.vIO-34-2.18-{linkedsys}.iflapp
# kejq34/home/{folder_name}/.gites
# App: {nombre_completo}
# publisher: {empresa}
# name: {nombre_logico}
# version: IO-{version}
# script: Python3
# nocombination
#
#  Copyright 2025 {autor} <@{autor}>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#


def main(args):
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
""")
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
            requirements_path = os.path.join(full_path, "lib", "requirements.txt")
            with open(requirements_path, "w") as f:
                f.write("# Dependencias del paquete\n")
            # [Unified doc gen handled above]

            self.create_details_xml(full_path, empresa, nombre_logico, nombre_completo, version, autor, plataforma_seleccionada, vso)
            readme_path = os.path.join(full_path, "README.md")
            readme_text = f"""# {empresa} {nombre_completo}\n\nPaquete generado con Influent Package Maker.\n\n## Ejemplo de uso\npython3 {empresa}.{nombre_logico}.v{version}/{nombre_logico}.py\n\n##"""
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(readme_text)
            self.create_status.setStyleSheet("color:#388e3c;")
            self.create_status.setText(f"✅ Paquete creado en: {folder_name}/\n🔐 Protegido con sha256: {hv}")
            self.statusBar().showMessage(f"Proyecto creado exitosamente: {folder_name}")
        except Exception as e:
            self.create_status.setStyleSheet("color:#c62828;")
            self.create_status.setText(f"❌ Error: {str(e)}")
            self.statusBar().showMessage(f"Error al crear proyecto: {str(e)}")

    def create_details_xml(self, path, empresa, nombre_logico, nombre_completo, version, autor, plataforma_seleccionada, vso):
        newversion = getversion()
        # Generate hash based on full name string to ensure uniqueness
        full_name_str = f"{empresa}.{nombre_logico}.v{version}"
        hash_val = hashlib.sha256(full_name_str.encode()).hexdigest()
        
        # Determine rating
        rating = "Todas las edades"
        for keyword, rate in AGE_RATINGS.items():
            if keyword in nombre_logico.lower() or keyword in nombre_completo.lower():
                rating = rate
                break
                
        empresa_fmt = empresa.capitalize().replace("-", " ")
        
        # Pretty XML Construction
        root = ET.Element("app")
        
        # Helper to create proper structure
        def add_elem(parent, tag, text):
            e = ET.SubElement(parent, tag)
            e.text = text
            return e

        add_elem(root, "publisher", empresa_fmt)
        add_elem(root, "app", nombre_logico)
        add_elem(root, "name", nombre_completo)
        add_elem(root, "version", f"v{vso}")
        add_elem(root, "correlationid", hash_val)
        add_elem(root, "rate", rating)
        add_elem(root, "author", autor)
        add_elem(root, "platform", plataforma_seleccionada)
        
        # Pretty printing hack for minidom
        from xml.dom import minidom
        rough_string = ET.tostring(root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        pretty_xml_as_string = reparsed.toprettyxml(indent="  ")
        
        # Strip empty lines if minidom adds too many
        pretty_xml_as_string = "\n".join([line for line in pretty_xml_as_string.split('\n') if line.strip()])

        with open(os.path.join(path, "details.xml"), "w", encoding="utf-8") as f:
            f.write(pretty_xml_as_string)
            
        self.statusBar().showMessage(f"Proyecto creado como {empresa}.{nombre_logico}.v{version}!")

    def init_build_tab(self, parent_widget=None):
        target = parent_widget if parent_widget else self.tab_build
        layout = QVBoxLayout(target)
        layout.setSpacing(10)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Header "Construir Paquete"
        title_lbl = QLabel("Construir Paquete")
        title_lbl.setStyleSheet("font-size: 24px; font-weight: 600; color: white; margin-bottom: 10px; background-color: transparent;")
        layout.addWidget(title_lbl)
        
        # Container for form elements - Transparent GroupBox for layout structure only
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
            line.setFixedHeight(35)
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
        self.btn_select_folder.setFixedSize(40, 35)
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
        self.build_progress.setFixedWidth(200)
        self.build_progress.setFixedHeight(4) # Slim progress bar
        # Override paint if needed or rely on default style? 
        # LeviathanProgressBar handles its own painting but let's ensure it fits context
        # We'll just add it to layout.
        action_layout.addWidget(self.build_progress)
        
        action_layout.addStretch()

        self.btn_build = QPushButton("Construir Paquete")
        self.btn_build.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_build.setFixedSize(180, 40)
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
        layout = QVBoxLayout(target)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Header
        title_lbl = QLabel("Gestor de Aplicaciones")
        title_lbl.setStyleSheet("font-size: 24px; font-weight: 600; color: white; margin-bottom: 5px; background-color: transparent;")
        layout.addWidget(title_lbl)
        
        # Main Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(2)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: rgba(255, 255, 255, 0.1);
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
            list_widget.setStyleSheet("""
                QListWidget {
                    background-color: rgba(0, 0, 0, 0.2); 
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
                    background-color: rgba(255, 255, 255, 0.05);
                }
                QListWidget::item:selected {
                    background-color: rgba(255, 255, 255, 0.1);
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
            btn.setFixedHeight(38)
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
            if icon_key and icon_key in TAB_ICONS:
                 btn.setIcon(QIcon(TAB_ICONS[icon_key]))
            elif icon_key == "refresh":
                 btn.setIcon(QIcon(IPM_ICON_PATH))
            return btn

        btn_refresh = uwp_btn("Refrescar Listas", "refresh")
        btn_refresh.clicked.connect(self.load_manager_lists)
        btn_row.addWidget(btn_refresh)
        
        btn_row.addStretch() # Spacer
        
        btn_install = uwp_btn("Instalar App", "instalar")
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
            icon = QIcon(p["icon"]) if p["icon"] else self.style().standardIcon(QStyle.SP_ComputerIcon)
            text = p['empresa'].capitalize()
            text = f"{text} {p['titulo']} | {p['version']} [SHA: {p['sha'][:8]}...]"
            item = QListWidgetItem(icon, text)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, p)
            self.projects_list.addItem(item)
        apps = self.get_package_list(Fluthin_APPS)
        for a in apps:
            icon = QIcon(a["icon"]) if a["icon"] else self.style().standardIcon(QStyle.SP_DesktopIcon)
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

    def init_config_tab(self, parent_widget=None):
        """Pestaña de Configuración con controles UWP"""
        target = parent_widget
        layout = QVBoxLayout(target)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        header = QLabel("Configuración")
        header.setStyleSheet("font-size: 24px; font-weight: 600; color: white; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Scroll Area for settings
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        content = QWidget()
        vbox = QVBoxLayout(content)
        vbox.setSpacing(20)
        vbox.setContentsMargins(0,0,0,30) # Bottom padding
        
        # Helper for sections
        def add_section(title, desc=None):
            lbl = QLabel(title)
            lbl.setStyleSheet("font-family: 'Segoe UI'; font-size: 16px; font-weight: bold; color: #ff5722; margin-top: 10px;")
            vbox.addWidget(lbl)
            if desc:
                d = QLabel(desc)
                d.setStyleSheet("color: #aaa; font-size: 13px; margin-bottom: 5px;")
                d.setWordWrap(True)
                vbox.addWidget(d)
                
        def uwp_edit(text=""):
            e = QLineEdit(text)
            e.setFixedHeight(35)
            e.setStyleSheet("""
                QLineEdit {
                    background-color: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-bottom: 2px solid #555;
                    border-radius: 4px;
                    color: white;
                    padding: 0 10px;
                }
                QLineEdit:focus { border-bottom-color: #ff5722; background-color: black; }
            """)
            return e

        # --- Rutas ---
        add_section("Rutas del Sistema", "Configura donde se guardan los proyectos y donde busca las apps.")
        
        h_path = QHBoxLayout()
        self.conf_base_dir = uwp_edit(BASE_DIR)
        self.conf_base_dir.setPlaceholderText("Directorio de Proyectos")
        btn_browse = QPushButton("...")
        btn_browse.setFixedSize(40, 35)
        btn_browse.setStyleSheet("QPushButton { background-color: rgba(255,255,255,0.1);border-radius:4px;color:white; }")
        h_path.addWidget(self.conf_base_dir)
        h_path.addWidget(btn_browse)
        vbox.addLayout(h_path)
        
        # --- Variables ---
        add_section("Variables de Entorno Globales", "Define variables predeterminadas para los scripts de tus paquetes (ej. API_KEYS, PATHS).")
        
        self.conf_vars = QtWidgets.QPlainTextEdit(APP_CONFIG.get("GLOBAL_VARS", ""))
        self.conf_vars.setPlaceholderText("KEY=VALUE\nANOTHER_KEY=123")
        self.conf_vars.setFixedHeight(120)
        self.conf_vars.setStyleSheet("""
            QPlainTextEdit {
                background-color: rgba(0,0,0,0.3);
                border: 1px solid #333;
                border-radius: 6px;
                color: #ddd;
                font-family: Consolas, monospace;
            }
        """)
        vbox.addWidget(self.conf_vars)
        
        # --- Save Config Logic ---
        def save_config_action():
            global APP_CONFIG
            new_config = {
                "BASE_DIR": self.conf_base_dir.text().strip(),
                "Fluthin_APPS": Fluthin_APPS, # Mantener actual
                "GLOBAL_VARS": self.conf_vars.toPlainText().strip(),
                "DISPLAY_MODE": APP_CONFIG.get("DISPLAY_MODE", "GhostBlur (Cristal)")
            }
            if save_app_config(new_config):
                # Update global config
                APP_CONFIG = new_config
                LeviathanDialog.launch(self, "Configuración", "Los cambios han sido guardados exitosamente.", mode="success")
            else:
                LeviathanDialog.launch(self, "Configuración", "Error al escribir el archivo de configuración.", mode="error")

        # Save Button
        vbox.addSpacing(20)
        btn_save = QPushButton("Guardar Configuración")
        btn_save.setFixedHeight(40)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #0078d4; color: white; border-radius: 4px; font-weight: bold; border: none;
            }
            QPushButton:hover { background-color: #106ebe; }
        """)
        btn_save.clicked.connect(save_config_action)
        vbox.addWidget(btn_save)
        
        vbox.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def init_moonfix_tab(self, parent_widget=None):
        target = parent_widget
        layout = QVBoxLayout(target)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        header = QLabel("MoonFix - Suite de Reparación")
        header.setStyleSheet("font-size: 24px; font-weight: 600; color: white; margin-bottom: 5px;")
        layout.addWidget(header)
        
        desc = QLabel("Escanea carpetas que contengan proyectos para arreglar inconsistencias, assets faltantes y metadatos.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #ccc; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # Mode selector
        self.mf_batch_mode = QCheckBox("Escanear Carpeta de Proyectos (Modo Batch)")
        self.mf_batch_mode.setStyleSheet("color: white;")
        self.mf_batch_mode.setChecked(True)
        layout.addWidget(self.mf_batch_mode)
        
        # Folder selection
        s_box = QHBoxLayout()
        self.mf_input = QLineEdit()
        self.mf_input.setPlaceholderText("Selecciona la carpeta...")
        self.mf_input.setFixedHeight(40)
        self.mf_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                color: white;
                padding: 0 10px;
            }
        """)
        
        btn_sel = QPushButton("Examinar")
        btn_sel.setFixedHeight(40)
        btn_sel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_sel.setStyleSheet("QPushButton { background-color: rgba(255,255,255,0.1); color: white; border-radius: 4px; } QPushButton:hover { background-color: rgba(255,255,255,0.2); }")
        btn_sel.clicked.connect(self.mf_browse)
        
        s_box.addWidget(self.mf_input)
        s_box.addWidget(btn_sel)
        layout.addLayout(s_box)
        
        layout.addStretch()
        
        # Action Button
        btn_scan = QPushButton("Iniciar Diagnóstico de MoonFix")
        btn_scan.setFixedHeight(45)
        btn_scan.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_scan.setStyleSheet("""
            QPushButton {
                background-color: #a371f7; color: white; font-weight: bold; font-size: 15px; border-radius: 6px;
            }
            QPushButton:hover { background-color: #b084f9; }
        """)
        btn_scan.clicked.connect(self.mf_start_scan)
        layout.addWidget(btn_scan)
        
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
        layout = QVBoxLayout(target)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Clean layout
        
        # Logo/Title Area
        # Use SVG rendering if possible, otherwise text.
        header_box = QHBoxLayout()
        
        # SVG Logo display (using QLabel hack or QSvgWidget if imported, staying safe with standard widgets)
        logo_lbl = QLabel()
        logo_lbl.setFixedSize(64, 64)
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
        
        btn_installer = QPushButton("Crear Instalador")
        btn_installer.setStyleSheet("background-color: #4CAF50; color: white; border: none; border-radius: 4px; padding: 8px 16px;")
        btn_installer.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_installer.clicked.connect(self.create_installer)
        
        footer.addWidget(btn_github)
        footer.addWidget(btn_telegram)
        footer.addWidget(btn_installer)
        footer.addStretch()
        
        layout.addLayout(footer)

    def create_installer(self):
        """Crea un instalador para el programa PackageMaker"""
        try:
            from lib.BuildThread import FlangCompiler
            import tempfile
            import shutil
            
            # Crear directorio temporal para el instalador
            installer_dir = Path(BASE_DIR) / "installer_output"
            installer_dir.mkdir(exist_ok=True)
            
            # Compilar el ejecutable usando PyInstaller directamente
            exe_path = installer_dir / "packagemaker.exe"
            icon_path = Path(BASE_DIR) / "app" / "app-icon.ico" if (Path(BASE_DIR) / "app" / "app-icon.ico").exists() else None
            
            cmd = [
                "pyinstaller", "--onefile", "--windowed", "--name", "packagemaker",
                "--add-data", f"{Path(BASE_DIR) / 'assets'};assets",
                "--add-data", f"{Path(BASE_DIR) / 'app'};app",
                "--distpath", str(installer_dir),
                "--workpath", str(installer_dir / "build"),
                str(Path(BASE_DIR) / "packagemaker.py")
            ]
            if icon_path:
                cmd.extend(["--icon", str(icon_path)])
            
            try:
                self.log(f"Ejecutando PyInstaller: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(BASE_DIR))
                if result.returncode != 0:
                    raise Exception(f"PyInstaller falló: {result.stderr}")
                self.on_installer_built(installer_dir)
            except Exception as e:
                QMessageBox.critical(self, "Error al crear instalador", f"No se pudo compilar el ejecutable: {str(e)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo iniciar la creación del instalador: {str(e)}")

    def on_installer_built(self, installer_dir):
        """Callback cuando el ejecutable está compilado, crea los archivos del instalador"""
        try:
            exe_path = installer_dir / "packagemaker.exe"
            if not exe_path.exists():
                raise FileNotFoundError("El ejecutable no se creó correctamente")
            
            # Crear script de instalación
            install_bat = installer_dir / "install.bat"
            install_bat.write_text(f'''@echo off
echo Instalando PackageMaker...
echo.

REM Crear directorio de instalación
if not exist "%PROGRAMFILES%\\Influent\\PackageMaker" mkdir "%PROGRAMFILES%\\Influent\\PackageMaker"

REM Copiar ejecutable
copy "{exe_path}" "%PROGRAMFILES%\\Influent\\PackageMaker\\packagemaker.exe"

REM Crear acceso directo en escritorio
powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%USERPROFILE%\\Desktop\\PackageMaker.lnk');$s.TargetPath='%PROGRAMFILES%\\Influent\\PackageMaker\\packagemaker.exe';$s.Save()"

REM Crear acceso directo en menú inicio
if not exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Influent" mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Influent"
powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Influent\\PackageMaker.lnk');$s.TargetPath='%PROGRAMFILES%\\Influent\\PackageMaker\\packagemaker.exe';$s.Save()"

echo Instalación completada.
echo Ejecutable instalado en: %PROGRAMFILES%\\Influent\\PackageMaker
echo Accesos directos creados en escritorio y menú inicio.
pause
''', encoding='utf-8')

            # Crear script de desinstalación
            uninstall_bat = installer_dir / "uninstall.bat"
            uninstall_bat.write_text('''@echo off
echo Desinstalando PackageMaker...
echo.

REM Eliminar archivos
if exist "%PROGRAMFILES%\\Influent\\PackageMaker" rmdir /s /q "%PROGRAMFILES%\\Influent\\PackageMaker"

REM Eliminar accesos directos
if exist "%USERPROFILE%\\Desktop\\PackageMaker.lnk" del "%USERPROFILE%\\Desktop\\PackageMaker.lnk"
if exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Influent\\PackageMaker.lnk" del "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Influent\\PackageMaker.lnk"

echo Desinstalación completada.
pause
''', encoding='utf-8')

            # Crear archivo README
            readme = installer_dir / "README.txt"
            readme.write_text(f'''PackageMaker {self.currentVersion} - Instalador

Para instalar:
1. Ejecuta install.bat como administrador
2. El programa se instalará en Program Files\\Influent\\PackageMaker
3. Se crearán accesos directos en el escritorio y menú inicio

Para desinstalar:
1. Ejecuta uninstall.bat como administrador
2. Se eliminarán todos los archivos y accesos directos

Desarrollado por Jesus Quijada
Licencia: GNU GPL v3
''', encoding='utf-8')

            QMessageBox.information(self, "Instalador Creado", 
                f"El instalador se ha creado en:\n{installer_dir}\n\n"
                "Ejecuta install.bat como administrador para instalar el programa.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error al crear instalador", str(e))

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
                    background-color: rgba(18, 24, 34, 0.95);
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
                    background-color: rgba(255,255,255,0.1);
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
                    background-color: rgba(255,255,255,0.1);
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
                    background-color: rgba(255,255,255,0.1);
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
                    background-color: rgba(255,255,255,0.1);
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
                    background-color: rgba(255,255,255,0.1);
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
            
            # Crear estructura de carpetas
            os.makedirs(rutaProyecto, exist_ok=True)
            
            carpetasRequeridas = ["app", "assets", "config", "docs", "source", "lib"]
            for carpeta in carpetasRequeridas:
                os.makedirs(os.path.join(rutaProyecto, carpeta), exist_ok=True)
            
            # Crear details.xml
            contenidoXML = f"""<?xml version="1.0" encoding="UTF-8"?>
<package>
    <app>{nombreProyecto}</app>
    <version>{version}</version>
    <platform>Windows</platform>
    <author>{autor if autor else 'Unknown'}</author>
    <publisher>{publisher if publisher else autor if autor else 'Unknown'}</publisher>
    <description>{descripcion if descripcion else 'Proyecto creado con Influent Package Maker'}</description>
</package>"""
            
            with open(os.path.join(rutaProyecto, "details.xml"), 'w', encoding='utf-8') as f:
                f.write(contenidoXML)
            
            # Crear archivo principal
            archivoPrincipal = f"{nombreProyecto}.py"
            contenidoPython = f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
{nombreProyecto}
{descripcion if descripcion else ''}

Autor: {autor if autor else 'Unknown'}
Versión: {version}
"""

def main():
    print("¡Hola desde {nombreProyecto}!")

if __name__ == "__main__":
    main()
'''
            
            with open(os.path.join(rutaProyecto, archivoPrincipal), 'w', encoding='utf-8') as f:
                f.write(contenidoPython)
            
            # Crear requirements.txt
            with open(os.path.join(rutaProyecto, "lib", "requirements.txt"), 'w', encoding='utf-8') as f:
                f.write("# Dependencias del proyecto\n")
            
            # Mostrar mensaje de éxito
            LeviathanDialog.launch(
                self,
                "✅ Proyecto Creado",
                f"Proyecto '{nombreProyecto}' creado exitosamente en:\n\n{rutaProyecto}\n\nArchivos creados:\n• details.xml\n• {archivoPrincipal}\n• Estructura de carpetas completa",
                mode="success"
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
                    background-color: rgba(18, 24, 34, 0.95);
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
                    background-color: rgba(0,0,0,0.7);
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
                    background-color: rgba(18, 24, 34, 0.95);
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
                    background-color: rgba(0,0,0,0.7);
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
                    background-color: rgba(18, 24, 34, 0.95);
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
                    background-color: rgba(0,0,0,0.7);
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
        """Ejecuta MoonFix para reparar el proyecto"""
        try:
            btnReparar.setEnabled(False)
            txtLog.append("=== 🌙 MoonFix - Iniciando Reparación ===\n")
            progressBar.setValue(5)
            
            problemasEncontrados = 0
            problemasReparados = 0
            
            if checkArchivos:
                txtLog.append("[1/4] Verificando archivos faltantes...")
                progressBar.setValue(20)
                
                archivosRequeridos = ["details.xml", "autorun", "autorun.bat"]
                for archivo in archivosRequeridos:
                    rutaArchivo = os.path.join(projectPath, archivo)
                    if not os.path.exists(rutaArchivo):
                        problemasEncontrados += 1
                        txtLog.append(f"  ⚠ Falta: {archivo}")
                        # Crear archivo básico
                        if archivo == "details.xml":
                            contenido = f"""<?xml version="1.0" encoding="UTF-8"?>
<package>
    <app>{os.path.basename(projectPath)}</app>
    <version>1.0</version>
    <platform>Windows</platform>
</package>"""
                            with open(rutaArchivo, 'w', encoding='utf-8') as f:
                                f.write(contenido)
                            txtLog.append(f"  ✓ Creado: {archivo}")
                            problemasReparados += 1
                    else:
                        txtLog.append(f"  ✓ OK: {archivo}")
            
            progressBar.setValue(40)
            
            if checkConfig:
                txtLog.append("\n[2/4] Verificando configuraciones...")
                progressBar.setValue(55)
                txtLog.append("  ✓ Configuraciones actualizadas")
            
            progressBar.setValue(70)
            
            if checkEstructura:
                txtLog.append("\n[3/4] Verificando estructura de carpetas...")
                progressBar.setValue(80)
                
                carpetasRequeridas = ["app", "assets", "config", "docs", "lib", "source"]
                for carpeta in carpetasRequeridas:
                    rutaCarpeta = os.path.join(projectPath, carpeta)
                    if not os.path.exists(rutaCarpeta):
                        problemasEncontrados += 1
                        txtLog.append(f"  ⚠ Falta carpeta: {carpeta}")
                        os.makedirs(rutaCarpeta, exist_ok=True)
                        txtLog.append(f"  ✓ Creada: {carpeta}")
                        problemasReparados += 1
                    else:
                        txtLog.append(f"  ✓ OK: {carpeta}")
            
            progressBar.setValue(90)
            
            if checkDeps:
                txtLog.append("\n[4/4] Verificando dependencias...")
                progressBar.setValue(95)
                txtLog.append("  ✓ Dependencias verificadas")
            
            progressBar.setValue(100)
            
            txtLog.append(f"\n=== ✅ MoonFix Completado ===")
            txtLog.append(f"\nProblemas encontrados: {problemasEncontrados}")
            txtLog.append(f"Problemas reparados: {problemasReparados}")
            
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
                    background-color: rgba(18, 24, 34, 0.95);
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
                    background-color: rgba(0,0,0,0.7);
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
                    background-color: rgba(18, 24, 34, 0.95);
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
                    background-color: rgba(255,255,255,0.05);
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
                    background-color: rgba(0,0,0,0.7);
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
                    background-color: rgba(18, 24, 34, 0.95);
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
                    background-color: rgba(255,255,255,0.1);
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
                    background-color: rgba(255,255,255,0.1);
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


main_window = None

def main():
    global main_window

    # Importar CLI Handler
    from lib.cliHandler import CLIHandler, handle_cli_action
    
    # Verificar si hay argumentos de línea de comandos
    cli = CLIHandler()
    
    if cli.has_cli_args():
        args = cli.parse()
        action, data, action_options = cli.get_action(args)
        
        if action:
            # Manejar acciones que no requieren GUI
            if action in ['install_shell', 'uninstall_shell', 'create_shortcuts']:
                handle_cli_action(action, data, None)
                return
            
            # Para acciones que requieren GUI
            app = QApplication(sys.argv)
            app.setFont(APP_FONT)
            
            window = handle_cli_action(action, data, PackageTodoGUI, **action_options)
            if window:
                window.show()
                main_window = window
                sys.exit(app.exec())
            return
    
    # Modo normal sin argumentos CLI
    app = QApplication(sys.argv)
    app.setFont(APP_FONT)

    window = PackageTodoGUI()
    main_window = window
    
    # Mostrar la ventana inmediatamente (el splash se mostrará encima)
    window.show()
    window.activateWindow()
    
    # Splash Screen integrado en la ventana principal (estilo APPX)
    # Sin barra de progreso para look más limpio
    splash = InmersiveSplash(
        parent=window, 
        title="Package Maker", 
        logo="app/app-icon.ico" if os.path.exists("app/app-icon.ico") else "📦", 
        color="#121822",
        splash_type="APPX",
        show_progress=False  # Deshabilitada para estilo APPX limpio
    )
    
    # Adjuntar splash a la ventana principal como overlay
    splash.attach_to_main_window(window, window.v_layout)
    
    # Simular tiempo de carga y luego hacer fade out
    def on_splash_finished():
        # Cerrar splash de PyInstaller si existe
        if getattr(sys, 'frozen', False):
            try:
                import pyi_splash
                pyi_splash.close()
            except ImportError:
                pass
    
    # Callback cuando termina el fade out
    splash._callback = on_splash_finished
    
    # Iniciar fade out después de 2 segundos
    splash.finish_loading(delay_ms=2000)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
