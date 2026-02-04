"""!/usr/bin/env/python"""
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
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QListWidget, QListWidgetItem, QFileDialog, QDialog, QStyle, QSizePolicy, QSplitter, QGroupBox, QRadioButton, QButtonGroup, QGridLayout, QProgressBar, QTextEdit, QStackedWidget,
    QCheckBox, QMessageBox, QInputDialog
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtGui import QPixmap      # [NEW IMPORT FOR TITLEBAR SVG]
from PyQt5.QtSvg import QSvgRenderer # [NEW IMPORT FOR TITLEBAR SVG RENDERING]
from PyQt5.QtCore import QByteArray  # [NEW IMPORT FOR SVG BUFFER]
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QEvent, QObject, QProcess
import requests
from leviathan_ui import InmersiveSplash, LightsOff, LeviathanDialog, WipeWindow, LeviathanProgressBar, CustomTitleBar, get_accent_color

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
APP_FONT = QFont('Roboto', 13)
TAB_FONT = QFont('Roboto', 12) # Icons (SVGs are handled as strings here for "one-file" convenience or resource paths)
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
# Note: The 'transition' property is a CSS feature supported by browsers, but it is NOT supported/stable in PyQt5 stylesheets.
# PyQt5 ignores 'transition' and related CSS3 properties—they have no effect and can be safely omitted.
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
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QObject

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

class KillerLogic:
    @staticmethod
    def kill_target(target_name):
        log(f"Matando procesos de: {target_name}")
        try:
            if sys.platform == "win32":
                subprocess.call(f"taskkill /F /IM {target_name}.exe", shell=True)
                subprocess.call(f"taskkill /F /IM {target_name}", shell=True) 
            else:
                subprocess.call(f"pkill -9 -f {target_name}", shell=True)
        except Exception as e:
            log(f"Kill error: {e}")

class InstallerWorker(QObject):
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(int)
    status = pyqtSignal(str)

    def __init__(self, url, app_data):
        super().__init__()
        self.url = url
        self.app = app_data["app"]
        self._running = True

    def run(self):
        temp_zip = "pending_update.zip"
        ext_dir = "update_temp_extracted"
        try:
            self.status.emit("Conectando con el servidor...")
            r = requests.get(self.url, stream=True)
            total = int(r.headers.get("content-length", 0))
            down = 0
            with open(temp_zip, "wb") as f:
                for chunk in r.iter_content(8192):
                    if not self._running: return
                    f.write(chunk)
                    down += len(chunk)
                    if total: self.progress.emit(int(down * 100 / total))

            self.status.emit("Descomprimiendo actualización...")
            if os.path.exists(ext_dir): shutil.rmtree(ext_dir)
            with zipfile.ZipFile(temp_zip, "r") as z:
                z.extractall(ext_dir)

            self.status.emit("Cerrando aplicación principal...")
            KillerLogic.kill_target(self.app)
            time.sleep(2) 

            self.status.emit("Sobrescribiendo sistema...")
            for root, dirs, files in os.walk(ext_dir):
                rel = os.path.relpath(root, ext_dir)
                dest_fold = rel if rel != "." else "."
                if dest_fold != "." and not os.path.exists(dest_fold):
                    os.makedirs(dest_fold)
                for file in files:
                    src = os.path.join(root, file)
                    dst = os.path.join(dest_fold, file)
                    if os.path.abspath(dst) == os.path.abspath(sys.argv[0]): continue 
                    if os.path.exists(dst):
                        try: os.remove(dst)
                        except: # Rename strategy for locked files
                            try: os.rename(dst, dst + f".old.{int(time.time())}")
                            except: continue
                    try: shutil.move(src, dst)
                    except: pass

            try: shutil.rmtree(ext_dir)
            except: pass
            try: os.remove(temp_zip)
            except: pass
            
            self.status.emit("Finalizando...")
            self.finished.emit(True, "OK")

        except Exception as e:
            log(traceback.format_exc())
            self.finished.emit(False, str(e))

class ModernUpdaterWindow(QMainWindow):
    def __init__(self, app_data, url):
        super().__init__()
        self.app_data = app_data
        self.url = url
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(480, 320)
        if HAS_LEVIATHAN:
            WipeWindow.create().set_mode("ghostBlur").apply(self)
        self.init_ui()
        self.center()
        QTimer.singleShot(500, self.start_install)

    def center(self):
        self.move(QApplication.desktop().availableGeometry().center() - self.rect().center())

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
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        c_lay.addWidget(self.icon_lbl)
        
        self.lbl_main = QLabel(f"Actualizando {self.app_data['app']}")
        self.lbl_main.setAlignment(Qt.AlignCenter)
        self.lbl_main.setStyleSheet("font-family: 'Segoe UI'; font-weight: 700; font-size: 18px; color: white;")
        c_lay.addWidget(self.lbl_main)
        
        self.lbl_status = QLabel("Preparando...")
        self.lbl_status.setAlignment(Qt.AlignCenter)
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
                        app.exec_()
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

def verificar_github_username(username):
    url = f"https://api.github.com/users/{username}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return True, "Usuario válido"
        elif response.status_code == 404:
            return False, "Usuario no encontrado"
        else:
            return False, f"Error API: {response.status_code}"
    except Exception as e:
        return False, f"Error de conexión: {str(e)}"

class FocusIndicationFilter(QObject):
    """Filtro de eventos para simular el indicador de foco estilo UWP."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.indicator = QWidget(None) # Ventana independiente (tool window) o overlay
        self.indicator.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint | Qt.WindowTransparentForInput | Qt.NoDropShadowWindowHint)
        self.indicator.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.indicator.setAttribute(Qt.WA_ShowWithoutActivating)
        # Color por defecto (se actualizará con el tema)
        self.indicator.setStyleSheet("background-color: #f9826c; border-radius: 2px;") 
        self.indicator.hide()
        self.current_widget = None

    def eventFilter(self, obj, event):
        if event.type() == QEvent.FocusIn:
            if isinstance(str(type(obj)), str) and ("QLineEdit" in str(type(obj)) or "QTextEdit" in str(type(obj)) or "QListWidget" in str(type(obj))):
                 self.update_indicator(obj)
        elif event.type() == QEvent.FocusOut:
             if obj == self.current_widget:
                 self.indicator.hide()
                 self.current_widget = None
        elif event.type() == QEvent.Move or event.type() == QEvent.Resize:
             if obj == self.current_widget:
                 self.update_indicator(obj)
        
        return super().eventFilter(obj, event)



    def update_indicator(self, widget):
        self.current_widget = widget
        rect = widget.rect()
        # Convertir posicion local a global
        global_pos = widget.mapToGlobal(rect.topLeft())
        
        # Geometría de la barra vertical: a la izquierda, alto del widget, ancho 4px
        # Ajuste fino: un poco separado
        x = global_pos.x() - 6 
        y = global_pos.y() + 4
        h = rect.height() - 8
        w = 4
        
        self.indicator.setGeometry(x, y, w, h)
        self.indicator.show()
        # Asegurar que esté encima
        self.indicator.raise_()

def getversion():
    newversion = time.strftime("%y.%m-%H.%M")
    return f"{newversion}"

class MoonFixWizard(QDialog):
    """Asistente de reparación estilo Setup que procesa múltiples proyectos en una sola ventana."""
    def __init__(self, parent, projects_with_issues):
        super().__init__(parent)
        self.projects = projects_with_issues
        self.current_project_index = 0
        self.results = {} # Store modified data per project index
        
        # Configuración de Ventana - REMOVED WindowStaysOnTopHint to avoid 'zombie' modal issues
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Responsive sizing: requested even more compact (-30px from 390 = 360)
        self.resize(720, 360)
        
        # Ensure it cleans up properly
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        # Initial position: centered horizontally, slightly higher vertically
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        start_x = (screen.width() - self.width()) // 2
        start_y = (screen.height() - self.height()) // 2 - 20
        self.move(max(0, start_x), max(0, start_y))
        
        # State for dragging
        self._dragging = False
        self._drag_pos = QtCore.QPoint()
        
        # Keyboard focus removal - more aggressive
        self.setFocusPolicy(Qt.NoFocus)
        self.setStyleSheet("""
            * { outline: none; }
            QWidget:focus { border: none; outline: none; }
            QPushButton:focus { outline: none; border: none; }
            QLineEdit:focus { border: 1px solid #1e88e5; background: rgba(0,0,0,0.2); }
            QPushButton#uwp_next {
                background-color: #0078d4;
                color: white;
                border-radius: 4px;
                font-weight: 600;
                font-size: 13px;
                border: 1px solid rgba(255,255,255,0.1);
                padding: 0 15px;
            }
            QPushButton#uwp_next:hover { background-color: #106ebe; }
            QPushButton#uwp_next:pressed { background-color: #005a9e; }
            QPushButton#uwp_next:disabled { background-color: #333; color: #777; }
        """)
        
        # Entrance state
        self.setWindowOpacity(0)
        
        # Animation references to prevent GC
        self._active_anims = []
        
        # Efecto de ventana Leviathan
        self.window_effects = WipeWindow.create().set_mode("ghostBlur").set_radius(20).apply(self)
        
        # Support for Asset Packs
        self.setAcceptDrops(True)
        self._temp_assets = {} # Store extracted paths temporarily

        self.init_ui()
        
    def showEvent(self, event):
        """Smooth entrance animation."""
        # Ensure it starts at 0 opacity and slightly offset before super() makes it visible
        self.setWindowOpacity(0)
        target_pos = self.pos()
        self.move(target_pos.x(), target_pos.y() + 40)
        
        super().showEvent(event)
        
        # Fade in + Slide Up
        self.anim_fade = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.anim_fade.setDuration(600)
        self.anim_fade.setStartValue(0)
        self.anim_fade.setEndValue(1)
        self.anim_fade.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        
        self.anim_pos = QtCore.QPropertyAnimation(self, b"pos")
        self.anim_pos.setDuration(600)
        self.anim_pos.setStartValue(self.pos())
        self.anim_pos.setEndValue(target_pos)
        self.anim_pos.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        
        # Store to prevent GC
        self._active_anims = [self.anim_fade, self.anim_pos]
        
        self.anim_fade.start()
        self.anim_pos.start()
        
    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Barra de título personalizada
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(45)
        self.title_bar.setStyleSheet("background: transparent; border-bottom: 1px solid rgba(255,255,255,0.05);")
        t_layout = QHBoxLayout(self.title_bar)
        t_layout.setContentsMargins(20, 0, 10, 0)
        
        t_icon = QLabel("🌙")
        t_icon.setStyleSheet("font-size: 18px;")
        t_layout.addWidget(t_icon)
        
        self.t_title = QLabel("MoonFix Setup Wizard")
        self.t_title.setStyleSheet("color: white; font-weight: bold; font-family: 'Segoe UI'; font-size: 13px;")
        t_layout.addWidget(self.t_title)
        t_layout.addStretch()
        
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(32, 32)
        btn_close.setStyleSheet("QPushButton { background: transparent; color: #888; border-radius: 16px; font-size: 16px; } QPushButton:hover { background: #e81123; color: white; }")
        btn_close.clicked.connect(self.reject)
        t_layout.addWidget(btn_close)
        
        self.main_layout.addWidget(self.title_bar)
        
        # Drag Logic for custom title bar
        def title_press(event):
            if event.button() == Qt.LeftButton:
                self._dragging = True
                self._drag_pos = event.globalPos() - self.pos()
                event.accept()

        def title_move(event):
            if self._dragging and event.buttons() & Qt.LeftButton:
                self.move(event.globalPos() - self._drag_pos)
                event.accept()

        def title_release(event):
            self._dragging = False

        self.title_bar.mousePressEvent = title_press
        self.title_bar.mouseMoveEvent = title_move
        self.title_bar.mouseReleaseEvent = title_release

        # Stack de Páginas
        self.stack = QStackedWidget()
        self.stack.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.stack)

        # 1. Página de Introducción
        self.page_intro = self.create_page_intro()
        self.stack.addWidget(self.page_intro)

        # 2. Páginas de Proyectos
        for i, proj in enumerate(self.projects):
            page = self.create_project_page(i, proj)
            self.stack.addWidget(page)

        # 3. Página Final
        self.page_done = self.create_page_done()
        self.stack.addWidget(self.page_done)

        # Barra de navegación inferior
        self.nav_bar = QWidget()
        self.nav_bar.setFixedHeight(60)
        self.nav_bar.setStyleSheet("background: rgba(0,0,0,0.2); border-top: 1px solid rgba(255,255,255,0.05);")
        nav_layout = QHBoxLayout(self.nav_bar)
        nav_layout.setContentsMargins(40, 0, 40, 0)
        
        self.lbl_step = QLabel(f"Página 1 de {len(self.projects) + 2}")
        self.lbl_step.setStyleSheet("background: transparent; color: #888; font-size: 11px; font-family: 'Segoe UI Variable Text';")
        nav_layout.addWidget(self.lbl_step)
        nav_layout.addStretch()
        
        self.btn_next = QPushButton("Empezar")
        self.btn_next.setObjectName("uwp_next")
        self.btn_next.setFixedSize(120, 36)
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.clicked.connect(self.go_next)
        nav_layout.addWidget(self.btn_next)
        
        self.main_layout.addWidget(self.nav_bar)

    def create_page_intro(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 25, 40, 25)
        layout.setSpacing(15)

        title = QLabel("Optimización de Proyectos")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: white; font-family: 'Segoe UI Variable Display';")
        layout.addWidget(title)

        desc = QLabel(
            f"Se han detectado <b>{len(self.projects)}</b> proyectos que requieren atención inmediata.\n\n"
            "MoonFix corregirá automáticamente las claves inválidas y normalizará las versiones."
        )
        desc.setStyleSheet("color: #bbb; font-size: 14px; line-height: 1.5;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        layout.addStretch()
        
        warning_box = QWidget()
        warning_box.setStyleSheet("background: transparent; border: 1px solid rgba(255, 152, 0, 0.2); border-radius: 8px;")
        w_layout = QHBoxLayout(warning_box)
        w_icon = QLabel("⚠️")
        w_text = QLabel("Asegúrate de tener conexión a internet si necesitas verificar perfiles de GitHub.")
        w_text.setStyleSheet("color: #ffb74d; font-size: 13px;")
        w_layout.addWidget(w_icon)
        w_layout.addWidget(w_text)
        layout.addWidget(warning_box)
        
        return page

    # --- DRAG & DROP FOR ASSET PACKS ---
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                f = url.toLocalFile().lower()
                if f.endswith(".ipm-assetpck") or f.endswith(".ipm-iconpck"):
                    event.acceptProposedAction()
                    return
        super().dragEnterEvent(event)

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(".ipm-assetpck"):
                self.process_ipm_assetpck(path)
            elif path.lower().endswith(".ipm-iconpck"):
                self.process_ipm_iconpck(path)
        super().dropEvent(event)

    def process_ipm_iconpck(self, file_path):
        """Parser for *.ipm-iconpck (ZIP containing multiple .ico files)"""
        try:
            temp_dir = tempfile.mkdtemp(prefix="ipm_icons_")
            with zipfile.ZipFile(file_path, 'r') as z:
                z.extractall(temp_dir)
                
                proj_idx = self.stack.currentIndex() - 1
                if proj_idx < 0: return

                applied = 0
                # Mapping: filename in zip -> ui field
                mapping = {
                    "app-icon.ico": "extra_icon",
                    "updater-icon.ico": "extra_icon_updater",
                    "product_logo.png": "extra_icon" # Fallback
                }
                
                for zip_fn, ui_key in mapping.items():
                    full_p = os.path.join(temp_dir, zip_fn)
                    if os.path.exists(full_p):
                        target = self.results[proj_idx]["inputs"].get(ui_key)
                        if target:
                            target.setText(full_p)
                            applied += 1
                
                if applied > 0:
                    self.statusBar().showMessage(f"Icon Pack aplicado: {applied} iconos vinculados.")
                else:
                    self.statusBar().showMessage("Icon Pack cargado, pero no se encontraron nombres de archivos válidos.")
        except Exception as e:
            LeviathanDialog.launch(self, "Error de Icon Pack", str(e), mode="error")

    def process_ipm_assetpck(self, file_path):
        """Binary parser for *.ipm-assetpck (ZIP format with internal JSON)"""
        try:
            temp_dir = tempfile.mkdtemp(prefix="ipm_assets_")
            with zipfile.ZipFile(file_path, 'r') as z:
                if 'metadata.json' not in z.namelist():
                    LeviathanDialog.launch(self, "Asset Pack", "El paquete no contiene metadata.json válida.", mode="error")
                    return
                
                z.extractall(temp_dir)
                meta_path = os.path.join(temp_dir, 'metadata.json')
                with open(meta_path, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                
                # Mapping: json_key -> ui_field_suffix
                mapping = {
                    "splash": "extra_splash",
                    "storelogo": "extra_icon",
                    "setuplabel": "extra_splash_setup"
                }

                current_idx = self.stack.currentIndex()
                proj_idx = current_idx - 1 
                
                if proj_idx < 0 or proj_idx >= len(self.projects):
                    return

                applied_count = 0
                for json_key, ui_key in mapping.items():
                    filename = meta.get(json_key)
                    if filename:
                        src_img_p = os.path.join(temp_dir, filename)
                        if os.path.exists(src_img_p):
                            # Convert to standard PNG and Rename
                            ext_map = {"extra_splash": "splash.png", "extra_icon": "product_logo.png", "extra_splash_setup": "splash_Setup.png"}
                            dest_name = ext_map[ui_key]
                            dest_path = os.path.join(temp_dir, f"converted_{dest_name}")
                            
                            # Conversion Engine (Supports any format Qt supports)
                            pix = QPixmap(src_img_p)
                            if not pix.isNull():
                                pix.save(dest_path, "PNG")
                                
                                # Update UI field
                                target_edit = self.results[proj_idx]["inputs"].get(ui_key)
                                if target_edit:
                                    target_edit.setText(dest_path)
                                    applied_count += 1
                
                if applied_count > 0:
                    self.statusBar().showMessage(f"Asset Pack aplicado: {applied_count} imágenes convertidas y vinculadas.")
                else:
                    self.statusBar().showMessage("Asset Pack cargado, pero no hay campos faltantes compatibles.")
        except Exception as e:
            LeviathanDialog.launch(self, "Error de Pack", f"No se pudo parsear el Asset Pack: {str(e)}", mode="error")

    def create_project_page(self, index, proj_data):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(10)
        
        path = proj_data["path"]
        name = os.path.basename(path)
        
        # Header with Icon
        header = QHBoxLayout()
        icon_lbl = QLabel()
        icon_lbl.setFixedSize(60, 60)
        
        icon_path = os.path.join(path, "app", "app-icon.ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(os.getcwd(), "app", "app-icon.ico")
            
        if os.path.exists(icon_path):
            icon_lbl.setPixmap(QPixmap(icon_path).scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            icon_lbl.setStyleSheet("background: transparent; border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; color: white; font-size: 24px;")
            icon_lbl.setText("")
            icon_lbl.setAlignment(Qt.AlignCenter)
        
        title_vbox = QVBoxLayout()
        t_name = QLabel(name)
        t_name.setStyleSheet("font-size: 24px; font-weight: 600; color: white; font-family: 'Segoe UI Variable Display';")
        t_path = QLabel(path)
        t_path.setStyleSheet("font-size: 11px; color: rgba(255,255,255,0.5); font-family: 'Segoe UI Variable Text';")
        t_path.setWordWrap(True)
        title_vbox.addWidget(t_name)
        title_vbox.addWidget(t_path)
        
        header.addWidget(icon_lbl)
        header.addSpacing(15)
        header.addLayout(title_vbox)
        header.addStretch()
        
        # Issues Summary Badge - UWP Card Style
        issues_box = QWidget()
        issues_box.setStyleSheet("background: rgba(255, 255, 255, 0.04); border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);")
        i_layout = QVBoxLayout(issues_box)
        i_layout.setContentsMargins(15, 10, 15, 10)
        i_layout.setSpacing(4)
        
        i_title = QLabel("INCONSISTENCIAS")
        i_title.setStyleSheet("color: #ff9800; font-size: 9px; font-weight: bold; letter-spacing: 1.5px; font-family: 'Segoe UI Variable Text';")
        i_layout.addWidget(i_title)
        
        # Restore full issue list for "learning"
        for issue in proj_data["issues"]:
            desc = issue.get("desc", issue.get("type", "Error"))
            if issue["type"] == "missing_dir": desc = f"Falta directorio: {issue['path']}"
            elif issue["type"] == "missing_xml": desc = "Archivo details.xml ausente"
            elif issue["type"] == "missing_script": desc = "Script principal no encontrado"
            elif issue["type"] == "missing_icon": desc = "Icono de app (*.ico) faltante"
            elif issue["type"] == "missing_logo": desc = "Logotipo product_logo.png faltante"
            elif issue["type"] == "missing_icon_updater": desc = "Icono de updater (*.ico) faltante"
            elif issue["type"] == "dirty_version": desc = f"Versión '{issue.get('val','')}' no normalizada"
            elif issue["type"] == "missing_splash": desc = "Splash PNG faltante"
            elif issue["type"] == "missing_splash_setup": desc = "Banner de Setup faltante"
            
            i_lbl = QLabel(f"• {desc}")
            i_lbl.setStyleSheet("color: #bbb; font-size: 11px; font-family: 'Segoe UI Variable Text';")
            i_lbl.setWordWrap(True)
            i_layout.addWidget(i_lbl)
        
        header.addWidget(issues_box)
        
        layout.addLayout(header)
        layout.addSpacing(5)
        
        # Form Container
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        form_content = QWidget()
        form_layout = QGridLayout(form_content)
        form_layout.setColumnStretch(1, 1)
        form_layout.setContentsMargins(5, 5, 5, 5)
        form_layout.setVerticalSpacing(10)
        
        # XML Data Extraction
        xml_path = os.path.join(path, "details.xml")
        xml_data = {}
        if os.path.exists(xml_path):
            try:
                tree = ET.parse(xml_path)
                root = tree.getroot()
                xml_data = {child.tag: child.text for child in root if child.text}
            except: pass

        self.results[index] = {"inputs": {}, "is_invalid": any(i["type"] == "invalid_package" for i in proj_data["issues"])}
        
        EDIT_QSS = """
            QLineEdit { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); border-bottom: 1px solid rgba(255,255,255,0.4); border-radius: 4px; color: white; padding: 0 12px; font-family: 'Segoe UIVariable Text'; font-size: 13px; }
            QLineEdit:hover { background: rgba(255,255,255,0.08); border-bottom: 1px solid rgba(255,255,255,0.6); }
            QLineEdit:focus { border: 1px solid rgba(255,255,255,0.1); border-bottom: 2px solid #0078D4; background: rgba(0,0,0,0.3); }
        """
        
        RADIO_QSS = """
            QRadioButton { color: white; spacing: 8px; font-size: 11px; }
            QRadioButton::indicator { width: 14px; height: 14px; border-radius: 8px; border: 2px solid rgba(255,255,255,0.3); background: rgba(0,0,0,0.1); }
            QRadioButton::indicator:checked { background: #0078d4; border: 2px solid #0078d4; }
            QRadioButton::indicator:hover { border: 2px solid rgba(255,255,255,0.5); }
        """

        fields_def = [
            ("publisher", "Organización:"), ("app", "ID Interno (Slug):"), 
            ("name", "Nombre Público:"), ("version", "Versión:"), 
            ("author", "Autor (GitHub):"), ("platform", "Plataforma Base:")
        ]

        current_row = 0
        for key, label_text in fields_def:
            value = str(xml_data.get(key, "")).strip()
            is_generic = value.lower() in ["1.0", "myorg", "appid", "public name", "unknown", "none", ""]
            is_invalid_v = key == "version" and "-" in value 
            
            should_show = self.results[index]["is_invalid"] or is_generic or is_invalid_v
            
            if key == "platform":
                if should_show:
                    lbl = QLabel(label_text)
                    lbl.setStyleSheet("color: #aaa; font-weight: 500;")
                    form_layout.addWidget(lbl, current_row, 0)
                    
                    p_box = QHBoxLayout()
                    p_group = QButtonGroup(page)
                    rad_win = QRadioButton("Windows")
                    rad_lin = QRadioButton("Linux")
                    rad_multi = QRadioButton("Multi")
                    for r in [rad_win, rad_lin, rad_multi]:
                        r.setStyleSheet(RADIO_QSS)
                        p_group.addButton(r)
                        p_box.addWidget(r)
                    
                    if "win" in value.lower(): rad_win.setChecked(True)
                    elif "lin" in value.lower(): rad_lin.setChecked(True)
                    else: rad_multi.setChecked(True)
                    form_layout.addLayout(p_box, current_row, 1)
                    
                    class PlatformProxy:
                        def __init__(self, w, l, m): self.w, self.l, self.m = w, l, m
                        def text(self):
                            if self.w.isChecked(): return "Windows"
                            if self.l.isChecked(): return "Linux"
                            return "Multiplataforma"
                        def setText(self, t):
                            if "win" in t.lower(): self.w.setChecked(True)
                            elif "lin" in t.lower(): self.l.setChecked(True)
                            else: self.m.setChecked(True)
                    self.results[index]["inputs"][key] = PlatformProxy(rad_win, rad_lin, rad_multi)
                    current_row += 1
                else:
                    class FixedProxy:
                        def __init__(self, v): self.v = v
                        def text(self): return self.v
                        def setText(self, t): self.v = t
                    self.results[index]["inputs"][key] = FixedProxy(value)
                continue

            if should_show:
                lbl = QLabel(label_text)
                lbl.setStyleSheet("color: #aaa; font-weight: 500;")
                edit = QLineEdit(value)
                edit.setFixedHeight(30)
                edit.setStyleSheet(EDIT_QSS)
                if not value or is_generic:
                    edit.setPlaceholderText("Campo obligatorio...")
                    edit.setStyleSheet(edit.styleSheet() + "QLineEdit { border-left: 3px solid #f44336; }")
                
                form_layout.addWidget(lbl, current_row, 0)
                form_layout.addWidget(edit, current_row, 1)
                self.results[index]["inputs"][key] = edit
                
                if key == "version":
                    def on_v_change(txt, idx=index):
                        v_cl = self.clean_version_str(txt)
                        inputs = self.results[idx]["inputs"]
                        if "author" in inputs and not inputs["author"].text(): inputs["author"].setText("JesusQuijada34")
                        if "publisher" in inputs and not inputs["publisher"].text(): inputs["publisher"].setText("Influent")
                        if "app" in inputs and (not inputs["app"].text() or "appid" in inputs["app"].text().lower()):
                             inputs["app"].setText(f"app-v{v_cl.replace('.','')}")
                    edit.textChanged.connect(on_v_change)
                current_row += 1
            else:
                class FixedProxy:
                    def __init__(self, v): self.v = v
                    def text(self): return self.v
                    def setText(self, t): self.v = t
                self.results[index]["inputs"][key] = FixedProxy(value)

        missing_icons = [i for i in proj_data["issues"] if "icon" in i["type"] or "logo" in i["type"]]
        missing_assets = [i for i in proj_data["issues"] if "splash" in i["type"]]
        
        if missing_icons or missing_assets:
            pack_box = QHBoxLayout()
            pack_box.setSpacing(10)
            btn_pack_css = "QPushButton { background: #0078d4; color: white; border-radius: 4px; padding: 6px 15px; font-weight: 600; font-family: 'Segoe UI Variable Text'; font-size: 11px; border: 1px solid rgba(255,255,255,0.1); } QPushButton:hover { background: #106ebe; border-color: rgba(255,255,255,0.2); }"
            
            if missing_icons:
                btn_i = QPushButton("Subir Icon Pack")
                btn_i.setStyleSheet(btn_pack_css)
                btn_i.setCursor(Qt.PointingHandCursor)
                btn_i.clicked.connect(lambda: self.upload_icon_pack(index))
                pack_box.addWidget(btn_i)
            if missing_assets:
                btn_a = QPushButton("Subir Asset Pack")
                btn_a.setStyleSheet(btn_pack_css.replace("#0078d4", "#28a745"))
                btn_a.setCursor(Qt.PointingHandCursor)
                btn_a.clicked.connect(lambda: self.upload_asset_pack(index))
                pack_box.addWidget(btn_a)
            pack_box.addStretch()
            form_layout.addLayout(pack_box, current_row, 1)
            current_row += 1

        # Hidden Proxies for assets (handled via Pack Uploads)
        for i in proj_data["issues"]:
            if i["type"] in ["missing_icon", "missing_icon_updater", "missing_logo", "missing_splash", "missing_splash_setup"]:
                key_map = {"missing_icon": "icon", "missing_icon_updater": "icon_updater", "missing_logo": "logo", "missing_splash": "splash", "missing_splash_setup": "splash_setup"}
                k = key_map[i["type"]]
                
                class HiddenProxy:
                    def __init__(self): self.val = ""
                    def text(self): return self.val
                    def setText(self, t): self.val = t
                
                # Only Create if it doesn't exist
                if f"extra_{k}" not in self.results[index]["inputs"]:
                    self.results[index]["inputs"][f"extra_{k}"] = HiddenProxy()

        scroll.setWidget(form_content)
        layout.addWidget(scroll)
        
        # GitHub Verification row
        gh_btn = QPushButton("Verificar GitHub")
        gh_btn.setFixedHeight(30)
        gh_btn.setStyleSheet("QPushButton { background: #333; color: white; border-radius: 5px; font-size: 11px; }")
        gh_status = QLabel("Pendiente")
        gh_status.setStyleSheet("color: #777; font-size: 10px;")
        def verify_gh(idx=index, status_lbl=gh_status):
            user = self.results[idx]["inputs"]["author"].text().strip()
            ok, msg = verificar_github_username(user)
            status_lbl.setText("✅ OK" if ok else f"❌ {msg}")
            status_lbl.setStyleSheet(f"color: {'#4caf50' if ok else '#f44336'}; font-size: 10px;")
        gh_btn.clicked.connect(verify_gh)
        layout.addSpacing(5)
        gh_row = QHBoxLayout()
        gh_row.addWidget(gh_btn)
        gh_row.addWidget(gh_status)
        gh_row.addStretch()
        layout.addLayout(gh_row)
        
        return page

    def create_page_done(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignCenter)

        icon = QLabel("✨")
        icon.setStyleSheet("font-size: 60px;")
        layout.addWidget(icon)

        title = QLabel("Ecosistema Sanado")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        layout.addWidget(title)

        self.done_desc = QLabel("Se han procesado todos los proyectos exitosamente y sus configuraciones han sido normalizadas.")
        self.done_desc.setStyleSheet("color: #aaa; font-size: 15px;")
        self.done_desc.setWordWrap(True)
        self.done_desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.done_desc)
        
        return page

    def clean_version_str(self, v):
        if not v: return "1.0.0"
        prohibited = ["danenone", "knosthalij", "keystone", "windows", "linux", "darwin", "macos", "win", "nix"]
        parts = re.split(r'([-_])', v)
        new_parts = []
        for p in parts:
            if p.lower() in prohibited:
                continue
            new_parts.append(p)
        res = "".join(new_parts)
        res = re.sub(r'[-_]{2,}', '-', res)
        res = res.strip('-_')
        return res if res else "1.0.0"

    def go_next(self):
        curr = self.stack.currentIndex()
        
        # Validation for project pages
        if 0 < curr < self.stack.count() - 1:
            idx = curr - 1
            # Check mandatory fields (Skip extra_ assets as they are hidden/optional-via-pack)
            inputs = self.results[idx]["inputs"]
            for k, edit in inputs.items():
                if k.startswith("extra_"): continue # Skip asset validation here
                if not edit.text().strip():
                    LeviathanDialog.launch(self, "Campo Requerido", f"El campo '{k}' es obligatorio para continuar.", mode="warning")
                    return
            
            # Apply fixes for this project
            self.apply_project_fixes(idx)

        if curr < self.stack.count() - 1:
            self.fade_to_page(curr + 1)
            self.update_nav()
        else:
            self.accept()

    def fade_to_page(self, index):
        """Transición suave con opacidad y desplazamiento lateral (W11 Inspired)."""
        old_widget = self.stack.currentWidget()
        new_widget = self.stack.widget(index)
        
        # Clean previous page anims
        for a in self._active_anims:
            if a.state() == QtCore.QAbstractAnimation.Running:
                a.stop()
        self._active_anims.clear()
        
        # Setup opacity effect for both to avoid flickering
        eff_new = QtWidgets.QGraphicsOpacityEffect(new_widget)
        new_widget.setGraphicsEffect(eff_new)
        
        self.stack.setCurrentIndex(index)
        new_widget.show() # Ensure it's active
        new_widget.raise_()
        
        anim = QtCore.QPropertyAnimation(eff_new, b"opacity")
        anim.setDuration(450)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.setEasingCurve(QtCore.QEasingCurve.OutQuart)
        
        # Slide for the new page
        final_pos = QtCore.QPoint(0, 0)
        new_widget.move(20, 0) 
        anim_pos = QtCore.QPropertyAnimation(new_widget, b"pos")
        anim_pos.setDuration(450)
        anim_pos.setStartValue(new_widget.pos())
        anim_pos.setEndValue(final_pos)
        anim_pos.setEasingCurve(QtCore.QEasingCurve.OutQuart)
        
        # Store references and start
        self._active_anims.extend([anim, anim_pos])
        anim.start()
        anim_pos.start()
        
        # Ensure all controls are repainted
        new_widget.update()
        QtWidgets.QApplication.processEvents()

    def update_nav(self):
        curr = self.stack.currentIndex()
        total = self.stack.count()
        self.lbl_step.setText(f"Página {curr + 1} de {total}")
        
        # Reset to UWP accent for all states, changing only text/icons
        if curr == 0:
            self.btn_next.setText("Empezar")
        elif curr == total - 1:
            self.btn_next.setText("Finalizar")
        else:
            self.btn_next.setText("Siguiente →")

    def apply_project_fixes(self, idx):
        proj = self.projects[idx]
        path = proj["path"]
        inputs = self.results[idx]["inputs"]
        
        # Extract metadata from inputs
        publisher = inputs.get("publisher").text().strip() or "Influent"
        app_id = inputs.get("app").text().strip() or os.path.basename(path)
        name_public = inputs.get("name").text().strip() or app_id.capitalize()
        version_raw = inputs.get("version").text().strip() or "1.0.0"
        author = inputs.get("author").text().strip() or "Unknown"
        platform_sel = inputs.get("platform").text().strip() or "Knosthalij"

        # Auto-Versioning Logic (Sync with requested -YY.MM-HH.MM format)
        v_clean = self.clean_version_str(version_raw)
        
        # Calculate timestamp: YY.MM-HH.MM
        now = time.localtime()
        ts = time.strftime("%y.%m-%H.%M", now)
        
        v_so = f"{v_clean}-{ts}"
        v_final = f"{v_so}-{platform_sel}"

        # 1. Folders Reconstruction
        required_dirs = ["app", "assets", "config", "docs", "source", "lib"]
        for d in required_dirs:
            os.makedirs(os.path.join(path, d), exist_ok=True)
            # Create container markers
            marker = os.path.join(path, d, f".{d}-container")
            if not os.path.exists(marker):
                hv = hashlib.sha256(f"{publisher}.{app_id}.v{v_final}".encode()).hexdigest()
                with open(marker, "w") as f:
                    f.write(f"#store (sha256 hash):{d}/.{hv}")

        # 2. XML Reconstruction
        xml_data = {
            "publisher": publisher,
            "app": app_id,
            "name": name_public,
            "version": f"v{v_so}",
            "author": author,
            "platform": platform_sel,
            "correlationid": hashlib.sha256(f"{publisher}.{app_id}.v{v_final}".encode()).hexdigest(),
            "rate": "PERSONAL USE"
        }
        
        root = ET.Element("app")
        for k, v in xml_data.items():
            ET.SubElement(root, k).text = str(v)
            
        from xml.dom import minidom
        try:
            xml_str = ET.tostring(root, 'utf-8')
            pretty = minidom.parseString(xml_str).toprettyxml(indent="  ")
            pretty = "\n".join([line for line in pretty.split('\n') if line.strip()])
            with open(os.path.join(path, "details.xml"), "w", encoding="utf-8") as f:
                f.write(pretty)
        except Exception as e: print(f"Error saving XML: {e}")

        # 3. Structural Files Reconstruction (The "Núcleo" Connection)
        
        # Main Script
        main_script = os.path.join(path, f"{app_id}.py")
        if not os.path.exists(main_script):
            with open(main_script, "w", encoding="utf-8") as f:
                f.write(f"#!/usr/bin/env python\n# -*- coding: utf-8 -*-\n# App: {name_public}\n# publisher: {publisher}\n# name: {app_id}\n# version: IO-{v_final}\n\ndef main(args):\n    print('Hello from {name_public}')\n    return 0\n\nif __name__ == '__main__':\n    import sys\n    sys.exit(main(sys.argv))\n")

        # README.md
        readme_path = os.path.join(path, "README.md")
        if not os.path.exists(readme_path):
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(f"# {publisher} {name_public}\n\nReconstruido por MoonFix Suite.\n\n## Uso\npython {app_id}.py\n")

        # LICENSE (GPLv3)
        lic_path = os.path.join(path, "LICENSE")
        if not os.path.exists(lic_path):
            with open(lic_path, "w", encoding="utf-8") as f:
                f.write("GNU GENERAL PUBLIC LICENSE\nVersion 3, 29 June 2007\n\n(Licencia restaurada por MoonFix)\n")

        # Docs Index
        docs_idx = os.path.join(path, "docs", "index.html")
        if not os.path.exists(docs_idx) or os.path.getsize(docs_idx) < 500:
            with open(docs_idx, "w", encoding="utf-8") as f:
                f.write(DOCS_TEMPLATE.replace("const FALLBACK_OWNER = 'JesusQuijada34';", f"const FALLBACK_OWNER = '{author}';").replace("const FALLBACK_REPO  = 'packagemaker';", f"const FALLBACK_REPO  = '{app_id}';"))

        # Resource placeholders
        for res_f in ["version.res", "manifest.res", ".storedetail"]:
            res_p = os.path.join(path, res_f)
            if not os.path.exists(res_p):
                with open(res_p, "w") as f: f.write(f"# MoonFix Resource: {res_f}")

        # Requirements
        req_p = os.path.join(path, "lib", "requirements.txt")
        if not os.path.exists(req_p):
            with open(req_p, "w") as f: f.write("# Dependencias\n")

        # 4. Asset Restoration
        # App Icon & Logo
        icon_src = inputs.get("extra_icon").text().strip() if inputs.get("extra_icon") else ""
        logo_src = inputs.get("extra_logo").text().strip() if inputs.get("extra_logo") else ""
        
        if icon_src and os.path.exists(icon_src):
            shutil.copy(icon_src, os.path.join(path, "app", "app-icon.ico"))
        
        if logo_src and os.path.exists(logo_src):
            shutil.copy(logo_src, os.path.join(path, "app", "product_logo.png"))
        elif icon_src and os.path.exists(icon_src):
            # Fallback if logo is missing but icon is provided (convert or just copy as placeholder)
            shutil.copy(icon_src, os.path.join(path, "app", "product_logo.png"))
        
        # Updater Icon
        upd_icon_src = inputs.get("extra_icon_updater").text().strip() if inputs.get("extra_icon_updater") else ""
        if upd_icon_src and os.path.exists(upd_icon_src):
            shutil.copy(upd_icon_src, os.path.join(path, "app", "updater-icon.ico"))
        
        splash_src = inputs.get("extra_splash").text().strip() if inputs.get("extra_splash") else ""
        if splash_src and os.path.exists(splash_src):
            shutil.copy(splash_src, os.path.join(path, "assets", "splash.png"))

        splash_setup_src = inputs.get("extra_splash_setup").text().strip() if inputs.get("extra_splash_setup") else ""
        if splash_setup_src and os.path.exists(splash_setup_src):
            shutil.copy(splash_setup_src, os.path.join(path, "assets", "splash_Setup.png"))

    def upload_icon_pack(self, index):
        f, _ = QFileDialog.getOpenFileName(self, "Seleccionar Icon Pack", "", "Icon Pack (*.ipm-iconpck)")
        if f: self.process_ipm_iconpck(f)

    def upload_asset_pack(self, index):
        f, _ = QFileDialog.getOpenFileName(self, "Seleccionar Asset Pack", "", "Asset Pack (*.ipm-assetpck)")
        if f: self.process_ipm_assetpck(f)

    def reject(self):
        """Slide down exit animation (Windows 11 style)."""
        if hasattr(self, "_closing") and self._closing: return
        self._closing = True
        
        self.exit_group = QtCore.QParallelAnimationGroup(self)
        target_y = self.pos().y() + 100
        
        self.exit_anim_pos = QtCore.QPropertyAnimation(self, b"pos")
        self.exit_anim_pos.setDuration(350)
        self.exit_anim_pos.setStartValue(self.pos())
        self.exit_anim_pos.setEndValue(QtCore.QPoint(self.pos().x(), target_y))
        self.exit_anim_pos.setEasingCurve(QtCore.QEasingCurve.InBack)
        
        self.exit_anim_fade = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.exit_anim_fade.setDuration(300)
        self.exit_anim_fade.setStartValue(self.windowOpacity())
        self.exit_anim_fade.setEndValue(0.0)
        
        self.exit_group.addAnimation(self.exit_anim_pos)
        self.exit_group.addAnimation(self.exit_anim_fade)
        self.exit_group.finished.connect(super().reject)
        self.exit_group.finished.connect(self.deleteLater) # Explicit memory cleanup
        self.exit_group.start()

    def accept(self):
        """Slide down exit animation for success (Windows 11 style)."""
        if hasattr(self, "_closing") and self._closing: return
        self._closing = True
        
        self.exit_group = QtCore.QParallelAnimationGroup(self)
        target_y = self.pos().y() + 100
        
        self.exit_anim_pos = QtCore.QPropertyAnimation(self, b"pos")
        self.exit_anim_pos.setDuration(350)
        self.exit_anim_pos.setStartValue(self.pos())
        self.exit_anim_pos.setEndValue(QtCore.QPoint(self.pos().x(), target_y))
        self.exit_anim_pos.setEasingCurve(QtCore.QEasingCurve.InBack)
        
        self.exit_anim_fade = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.exit_anim_fade.setDuration(300)
        self.exit_anim_fade.setStartValue(self.windowOpacity())
        self.exit_anim_fade.setEndValue(0.0)
        
        self.exit_group.addAnimation(self.exit_anim_pos)
        self.exit_group.addAnimation(self.exit_anim_fade)
        self.exit_group.finished.connect(super().accept)
        self.exit_group.finished.connect(self.deleteLater) # Explicit memory cleanup
        self.exit_group.start()

# Aliases to satisfy the user request for QSetup/QInstaller names
QSetup = MoonFixWizard
QInstaller = MoonFixWizard

def verificar_github_username(username):
    """Verifica si un username de GitHub existe. Si no hay internet, deja pasar el username."""
    if not username or not username.strip():
        return False, "El username no puede estar vacío"
    username = username.strip()
    url = f"https://api.github.com/users/{username}"
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                return True, "Username válido"
            else:
                return False, f"Username no encontrado (código: {response.status})"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False, "El username no existe en GitHub"
        else:
            return False, f"Error al verificar: {e.code}"
    except urllib.error.URLError as e:
        # Si no hay internet, se permite el username
        return True, "Conexión a internet no disponible, se permite el username"
    except Exception as e:
        return False, f"Error inesperado: {str(e)}"

def detectar_modo_sistema():
    """Detecta el modo claro/oscuro del sistema operativo"""
    if sys.platform.startswith("win"):
        # Windows: leer del registro
        try:
            if winreg:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
                )
                try:
                    value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                    winreg.CloseKey(key)
                    return value == 0  # 0 = oscuro, 1 = claro
                except FileNotFoundError:
                    # Si no existe la clave, asumir modo claro
                    return False
            else:
                # Fallback: usar la paleta de Qt
                app = QApplication.instance()
                if app:
                    palette = app.palette()
                    return palette.color(QtGui.QPalette.Window).lightness() < 128
                return False
        except Exception:
            # Fallback: usar la paleta de Qt
            app = QApplication.instance()
            if app:
                palette = app.palette()
                return palette.color(QtGui.QPalette.Window).lightness() < 128
            return False
    elif sys.platform.startswith("linux"):
        # Linux: intentar con gsettings (GNOME) o xfconf (XFCE)
        try:
            # Intentar gsettings primero (GNOME)
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                theme = result.stdout.strip().lower()
                return "dark" in theme
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            pass
        
        try:
            # Intentar xfconf (XFCE)
            result = subprocess.run(
                ["xfconf-query", "-c", "xsettings", "-p", "/Net/ThemeName"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                theme = result.stdout.strip().lower()
                return "dark" in theme
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            pass
        
        # Fallback: leer archivo de configuración
        try:
            theme_file = os.path.expanduser("~/.config/gtk-3.0/settings.ini")
            if os.path.exists(theme_file):
                with open(theme_file, 'r') as f:
                    content = f.read().lower()
                    return "dark" in content
        except Exception:
            pass
        
        # Último fallback: usar la paleta de Qt
        app = QApplication.instance()
        if app:
            palette = app.palette()
            return palette.color(QtGui.QPalette.Window).lightness() < 128
        return False
    else:
        # Otros sistemas: usar la paleta de Qt
        app = QApplication.instance()
        if app:
            palette = app.palette()
            return palette.color(QtGui.QPalette.Window).lightness() < 128
        return False

class GitHubVerifyThread(QThread):
    """Thread para verificar username de GitHub"""
    finished = pyqtSignal(bool, str) # bool success, str message_or_url
    
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
    
    def run(self):
        valido, resultado = verificar_github_username(self.username)
        # resultado será el URL si es valido, o mensaje de error si no
        self.finished.emit(valido, resultado)

class FlangCompiler:
    """Compilador principal unificado para el ecosistema Fluthin (Version Robusta)."""

    def __init__(self, repo_path: Path, output_path: Optional[Path] = None, log_callback=None):
        self.repo_path = Path(repo_path).resolve()
        self.output_path = Path(output_path or "./releases").resolve()
        self.log_callback = log_callback
        self.details_xml_path = self.repo_path / "details.xml"
        self.metadata = {}
        self.scripts = []
        self.platform_type = None
        self.current_platform = platform.system()
        self.venv_path = None

        self.output_path.mkdir(parents=True, exist_ok=True)
        self.log(f"[FlangCompiler IT] Inicializado en: {self.repo_path}")
        self.log(f"[FlangCompiler IT] Plataforma actual: {self.current_platform}")

    def log(self, msg):
        if self.log_callback:
            self.log_callback(msg)
        print(msg)

    def _check_pyinstaller_installed(self) -> bool:
        try:
            result = subprocess.run(
                ["pyinstaller", "--version"],
                capture_output=True,
                text=True,
                timeout=20
            )
            if result.returncode == 0:
                self.log(f"[INFO] PyInstaller encontrado: {result.stdout.strip()}")
                return True
            return False
        except Exception as e:
            self.log(f"[INFO] PyInstaller no encontrado (check simple): {e}")
            return False

    def _install_pyinstaller_linux(self) -> bool:
        self.log("[INFO] 🔧 Instalando PyInstaller en Linux...")
        install_script = """#!/bin/bash
echo "🔧 Instalando python3-full, python3-venv y pipx..."
sudo apt install -y python3-full python3-venv pipx

echo "🔧 Configurando pipx..."
pipx ensurepath

VENV_DIR="$HOME/venv-pyinstaller"
if [ ! -d "$VENV_DIR" ]; then
    echo "🧪 Creando entorno virtual en $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
else
    echo "🔁 El entorno virtual ya existe en $VENV_DIR."
fi

echo "🚀 Activando entorno virtual..."
source "$VENV_DIR/bin/activate"

echo "📦 Instalando PyInstaller..."
pip install --upgrade pip
pip install pyinstaller

echo "✅ PyInstaller instalado. Versión:"
pyinstaller --version
"""
        try:
            script_path = Path(tempfile.gettempdir()) / "install_pyinstaller.sh"
            with open(script_path, 'w', newline='\n') as f:
                f.write(install_script)
            os.chmod(script_path, 0o755)
            
            self.log(f"[INFO] Ejecutando script de instalación: {script_path}")
            result = subprocess.run(["bash", str(script_path)], capture_output=False, text=True)
            
            try: script_path.unlink()
            except: pass
            
            if result.returncode != 0:
                self.log(f"[ERROR] Error durante la instalación de PyInstaller")
                return False
            
            venv_dir = Path.home() / "venv-pyinstaller"
            self.venv_path = venv_dir
            if not venv_dir.exists():
                self.log(f"[ERROR] El entorno virtual no fue creado en {venv_dir}")
                return False
                
            pyinstaller_path = venv_dir / "bin" / "pyinstaller"
            if not pyinstaller_path.exists():
                self.log(f"[ERROR] PyInstaller no fue instalado en {pyinstaller_path}")
                return False
                
            self.log(f"[OK] ✅ PyInstaller instalado correctamente en {venv_dir}")
            return True
        except Exception as e:
            self.log(f"[ERROR] Excepción durante la instalación de PyInstaller: {e}")
            return False

    def _ensure_pyinstaller(self) -> bool:
        if self._check_pyinstaller_installed():
            return True
        if self.current_platform == "Linux":
            self.log("[INFO] PyInstaller no encontrado. Iniciando instalación automática...")
            return self._install_pyinstaller_linux()
        else:
            self.log("[ERROR] PyInstaller no encontrado. Instale: pip install pyinstaller")
            return False

    def parse_details_xml(self) -> bool:
        if not self.details_xml_path.exists():
            self.log(f"[ERROR] No details.xml found in {self.repo_path}")
            return False
        try:
            tree = ET.parse(self.details_xml_path)
            root = tree.getroot()
            
            # Extraer metadatos con fallbacks robustos
            self.metadata = {
                'publisher': root.findtext('publisher') or root.findtext('empresa') or 'Unknown',
                'app': root.findtext('app') or root.findtext('name') or 'Unknown',
                'name': root.findtext('name') or root.findtext('titulo') or 'Unknown',
                'version': root.findtext('version') or 'v1.0',
                'platform': root.findtext('platform') or root.findtext('plataforma') or 'AlphaCube',
                'author': root.findtext('author') or root.findtext('autor') or 'Unknown',
            }
            self.platform_type = self.metadata['platform']
            self.log(f"[INFO] Metadatos cargados: {self.metadata}")
            return True
        except Exception as e:
            self.log(f"[ERROR] Error al parsear details.xml: {e}")
            return False

    def _find_icon(self, script_name: str) -> Optional[Path]:
        """
        Busca el icono para un script.
        Reglas:
        1. Script Main puede usar 'app-icon.ico' (default) o '{appname}-icon.ico'.
        2. Otros scripts DEBEN usar '{scriptname}-icon.ico'.
        """
        app_dir = self.repo_path / "app"
        if not app_dir.exists(): return None
        
        # 1. Buscar icono específico: {nombre_script}-icon.ico
        # Prioridad alta para todos
        specific_icon = app_dir / f"{script_name}-icon.ico"
        if specific_icon.exists():
            return specific_icon
            
        # 2. Fallback SOLO para el script principal
        if script_name == self.metadata['app']:
            default_icon = app_dir / "app-icon.ico"
            if default_icon.exists():
                return default_icon
                
        return None

    def find_scripts(self) -> bool:
        main_script = f"{self.metadata['app']}.py"
        main_script_path = self.repo_path / main_script
        
        if main_script_path.exists():
            icon_path = self._find_icon(self.metadata['app'])
            self.scripts.append({
                'name': self.metadata['app'],
                'path': main_script_path,
                'icon': icon_path,
                'is_main': True,
            })
            self.log(f"[INFO] Main script: {main_script} | Icon: {icon_path.name if icon_path else 'None'}")
        
        for file in self.repo_path.glob("*.py"):
            # Exclude main script, system scripts, and internal tools
            if file.name != main_script and not file.name.startswith("_") and file.name not in ["packagemaker.py"]:
                icon_path = self._find_icon(file.stem)
                
                self.scripts.append({
                    'name': file.stem,
                    'path': file,
                    'icon': icon_path,
                    'is_main': False,
                })
                icon_name = icon_path.name if icon_path else 'None'
                self.log(f"[INFO] Secondary script: {file.name} | Icon: {icon_name}")
        
        return len(self.scripts) > 0

    def should_compile_for_platform(self, target_platform: str) -> bool:
        if self.platform_type == "AlphaCube": return True
        if self.platform_type == "Knosthalij": return target_platform == "Windows"
        if self.platform_type == "Danenone": return target_platform == "Linux"
        return False

    def compile_binaries(self, target_platform: str) -> bool:
        if not self.should_compile_for_platform(target_platform):
            return True
        if target_platform == "Windows" and self.current_platform != "Windows":
             self.log(f"[SKIP] Cannot compile Windows on {self.current_platform}")
             return True
        if target_platform == "Linux" and self.current_platform != "Linux":
             self.log(f"[SKIP] Cannot compile Linux on {self.current_platform}")
             return True

        if not self._ensure_pyinstaller(): return False

        self.log(f"--- / --- - WORKING FOR SQUAREROOM - --- / ---")
        self.log(f"[INFO] Iniciando compilación para {target_platform}...")
        for script in self.scripts:
            self.log(f"[INFO] Compilando script: {script['name']}...")
            if target_platform == "Windows":
                if not self._compile_windows_binary(script): return False
            elif target_platform == "Linux":
                if not self._compile_linux_binary(script): return False
        return True

    def _compile_windows_binary(self, script: Dict) -> bool:
        script_path = script['path']
        script_name = script['name']
        
        pyinstaller_cmd = "pyinstaller"
        if self.venv_path and self.current_platform == "Linux":
            pyinstaller_cmd = str(self.venv_path / "bin" / "pyinstaller")
            
        cmd = [
            pyinstaller_cmd, "--onefile", "--windowed", "--name", script_name,
            "--add-data", "assets;assets", "--add-data", "app;app",
        ]
        if script['icon']:
            cmd.extend(["--icon", str(script['icon'])])
        cmd.append(str(script_path))

        try:
            self.log(f"[DEBUG] Ejecutando PyInstaller para {script_name}...")
            result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True)
            if result.returncode != 0:
                self.log(f"[ERROR] Falló PyInstaller:\n{result.stderr}")
                return False
            self.log(f"[OK] {script_name} compilado.")
            return True
        except Exception as e:
            self.log(f"[ERROR] Excepción PyInstaller: {e}")
            return False

    def _compile_linux_binary(self, script: Dict) -> bool:
        script_path = script['path']
        script_name = script['name']
        
        pyinstaller_cmd = "pyinstaller"
        if self.venv_path: # Linux venv
            pyinstaller_cmd = str(self.venv_path / "bin" / "pyinstaller")

        cmd = [
            pyinstaller_cmd, "--onefile", "--name", script_name,
            "--add-data", "assets:assets", "--add-data", "app:app",
            str(script_path)
        ]
        
        try:
            self.log(f"[DEBUG] Ejecutando PyInstaller para {script_name}...")
            result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True)
            if result.returncode != 0:
                self.log(f"[ERROR] Falló PyInstaller:\n{result.stderr}")
                return False
            self.log(f"[OK] {script_name} compilado.")
            return True
        except Exception as e:
            self.log(f"[ERROR] Excepción PyInstaller: {e}")
            return False

    def create_package(self, target_platform: str) -> bool:
        if not self.should_compile_for_platform(target_platform): return True
        
        platform_suffix = "Knosthalij" if target_platform == "Windows" else "Danenone"
        package_name = f"{self.metadata['publisher']}.{self.metadata['app']}.{self.metadata['version']}.{platform_suffix}"
        package_path = self.output_path / package_name
        package_path.mkdir(parents=True, exist_ok=True)
        
        self.log(f"[INFO] Creando paquete en: {package_path}")
        self._copy_package_files(package_path, target_platform)
        self._update_and_copy_details_xml(package_path, platform_suffix)
        return True

    def _copy_package_files(self, package_path: Path, target_platform: str) -> None:
        exclude_patterns = ["requirements.txt", "*.pyc", "__pycache__", ".git", ".gitignore", "build", "dist", "*.spec", "*.py"]
        # Include logic to copy dirs like app, assets...
        for item in self.repo_path.iterdir():
            if any(fnmatch.fnmatch(item.name, p) for p in exclude_patterns): continue
            
            dest = package_path / item.name
            if item.is_dir():
                if dest.exists(): shutil.rmtree(dest)
                try:
                    shutil.copytree(item, dest, ignore=shutil.ignore_patterns(*exclude_patterns))
                except Exception as e:
                     self.log(f"[WARN] Error copiando {item.name}: {e}")
            elif item.is_file():
                try: shutil.copy2(item, dest)
                except: pass
                
        # Move binaries
        dist_dir = self.repo_path / "dist"
        if dist_dir.exists():
            for binary in dist_dir.iterdir():
                if target_platform == "Windows" and binary.suffix == ".exe":
                    shutil.copy2(binary, package_path / binary.name)
                elif target_platform == "Linux" and binary.suffix == "":
                    shutil.copy2(binary, package_path / binary.name)
                    try: (package_path / binary.name).chmod(0o755)
                    except: pass

    def _update_and_copy_details_xml(self, package_path: Path, platform_suffix: str) -> None:
        try:
            tree = ET.parse(self.details_xml_path)
            root = tree.getroot()
            pe = root.find('platform')
            if pe is None: pe = ET.SubElement(root, 'platform')
            pe.text = platform_suffix
            tree.write(package_path / "details.xml", encoding='utf-8', xml_declaration=True)
        except Exception as e:
            self.log(f"[ERROR] Updating XML: {e}")

    def compress_to_iflapp(self, package_path: Path, output_file: Path) -> bool:
        self.log(f"[INFO] Creando .iflapp: {output_file.name}")
        try:
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(package_path):
                    for file in files:
                        fp = Path(root) / file
                        arcname = fp.relative_to(package_path)
                        zipf.write(fp, arcname)
            return True
        except Exception as e:
            self.log(f"[ERROR] Zip failed: {e}")
            return False

    def run(self, build_mode="portable") -> Optional[Path]:
        if not self.parse_details_xml(): return None
        if not self.find_scripts(): 
            self.log("[WARN] No scripts found")
            return None
        
        platforms_to_compile = []
        if self.current_platform == "Windows":
             if self.should_compile_for_platform("Windows"): platforms_to_compile.append("Windows")
        elif self.current_platform == "Linux":
             if self.should_compile_for_platform("Linux"): platforms_to_compile.append("Linux")
        
        if not platforms_to_compile:
            self.log("[WARN] Nothing to compile for this platform/config.")
            return None
            
        final_iflapp = None
        
        for platform_name in platforms_to_compile:
            if not self.compile_binaries(platform_name): return None
            if not self.create_package(platform_name): return None
            
            platform_suffix = "Knosthalij" if platform_name == "Windows" else "Danenone"
            package_name = f"{self.metadata['publisher']}.{self.metadata['app']}.{self.metadata['version']}.{platform_suffix}"
            last_package_path = self.output_path / package_name
            
            iflapp_name = f"{self.metadata['publisher']}.{self.metadata['app']}.{self.metadata['version']}-{platform_suffix}.iflapp"
            iflapp_path = self.output_path / iflapp_name
            
            if self.compress_to_iflapp(last_package_path, iflapp_path):
                final_iflapp = iflapp_path
                self.log(f"[SUCCESS] Package created: {iflapp_path}")
                
        return final_iflapp

class BuildThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, empresa, nombre, version, plataforma, parent=None, custom_path=None, build_mode="portable"):
        super().__init__(parent)
        self.empresa = empresa
        self.nombre = nombre
        self.version = version
        self.plataforma = plataforma # "Windows", "Linux", etc.
        self.custom_path = custom_path
        self.build_mode = build_mode
        self.curiosity_phrases = [
            "Sabías que el primer error de software fue causado por una polilla real atrapada en una computadora?",
            "Sabías que Python lleva el nombre de la serie de televisión Monty Python's Flying Circus?",
            "Sabías que el modo oscuro consume menos energía en pantallas OLED?",
            "Sabías que el código de la misión Apolo 11 contenía chistes escondidos?",
            "Sabías que 'Hello World' se convirtió en tradición gracias a Brian Kernighan?",
            "Sabías que el primer lenguaje de programación fue creado por Ada Lovelace?",
            "Sabías que el 90% del código de los coches modernos es software?",
            "Sabías que Linux está presente en el 100% de las 500 supercomputadoras más potentes?",
            "Sabías que el primer dominio registrado fue symbolics.com en 1985?",
            "Sabías que se estima que hay más de 20 millones de desarrolladores en el mundo?"
        ]
        self._curiosity_timer = None

    def emit_random_curiosity(self):
        import random
        phrase = random.choice(self.curiosity_phrases)
        self.progress.emit(f"💡 {phrase}")

    def run(self):
        # Iniciar con una frase de curiosidad
        self.emit_random_curiosity()
        
        # Reconstruct folder path
        p_map = {"Windows": "Knosthalij", "Linux": "Danenone", "Multiplataforma": "AlphaCube"}
        plat_suffix = p_map.get(self.plataforma, "AlphaCube")
        
        repo_path = None
        if self.custom_path:
             repo_path = Path(self.custom_path)
             if not repo_path.exists():
                 self.error.emit(f"No se encontró la carpeta personalizada: {self.custom_path}")
                 return
        else:
            folder = f"{self.empresa}.{self.nombre}.v{self.version}-{plat_suffix}"
            repo_path = Path(BASE_DIR) / folder
            
            if not repo_path.exists():
                self.error.emit(f"No se encontró la carpeta: {folder}")
                return

        compiler = FlangCompiler(repo_path, Path(BASE_DIR), log_callback=self.handle_compiler_log)
        result = compiler.run(build_mode=self.build_mode)
        
        if result:
            self.finished.emit(f"✅ Paquete construido con éxito: {result.name}")
        else:
            self.error.emit("Falló la compilación. Verifique los logs y los iconos .ico")

    def handle_compiler_log(self, msg):
        # Cada vez que hay un log del compilador, damos la oportunidad de soltar una curiosidad
        # si ha pasado suficiente tiempo (ej. 10 segundos)
        self.progress.emit(msg)
        if not hasattr(self, '_last_phrase_time'): self._last_phrase_time = time.time()
        if time.time() - self._last_phrase_time > 8:
            import random
            self.progress.emit(f"💡 {random.choice(self.curiosity_phrases)}")
            self._last_phrase_time = time.time()

from PyQt5.QtWidgets import QComboBox

# === BEGIN CUSTOM TITLE BAR CLASS ===
class AnimTitleButton(QPushButton):
    """Boton de titulo con animación de fondo suave (UWP Style)"""
    def __init__(self, icon_svg, hover_color, parent=None):
        super().__init__(parent)
        self.setFixedSize(46, 32)
        self.setIconSize(QtCore.QSize(16, 16))
        self.setFlat(True)
        self.hover_color = hover_color
        self.default_color = QtGui.QColor(0, 0, 0, 0) # Transparent
        
        # Load SVG to QIcon
        pm = QtGui.QPixmap()
        pm.loadFromData(icon_svg)
        self.setIcon(QIcon(pm))
        
        # Animación background
        self._bg_color = self.default_color
        self.anim = QtCore.QVariantAnimation(self)
        self.anim.setDuration(150)
        self.anim.setStartValue(self.default_color)
        self.anim.setEndValue(QtGui.QColor(self.hover_color))
        self.anim.valueChanged.connect(self._update_bg)

    def _update_bg(self, color):
        self._bg_color = color
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.fillRect(self.rect(), self._bg_color)
        super().paintEvent(event)

    def enterEvent(self, event):
        self.anim.setDirection(QtCore.QAbstractAnimation.Forward)
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.anim.setDirection(QtCore.QAbstractAnimation.Backward)
        self.anim.start()
        super().leaveEvent(event)


class TitleBar(QWidget):  # [Refactored: UWP Animated TitleBar]
    """Custom non-native title bar with UWP-style animated buttons."""

    def __init__(self, parent=None, app_icon=None, title=""):
        super().__init__(parent)
        self._parent = parent
        self.setFixedHeight(40) # Slightly taller for UWP feel
        self.setObjectName("customTitleBar")
        self._drag_active = False
        self._drag_offset = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 0, 0)
        layout.setSpacing(10)

        # Icon
        if app_icon:
            icon_lbl = QLabel()
            icon_lbl.setPixmap(app_icon.pixmap(20, 20))
            icon_lbl.setFixedSize(20, 20)
            layout.addWidget(icon_lbl)

        # Title
        self.title_label = QLabel(title)
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        # Font will be inherited from main window or set by stylesheet
        self.title_label.setStyleSheet("font-size: 13px; font-weight: 500; font-family: 'Segoe UI'; color: #eeeeee;")
        layout.addWidget(self.title_label)
        
        layout.addStretch()

        self.setMouseTracking(True)

        # Botones de control (UWP Style: Min, Max/Restore, Close)
        btnc = QWidget()
        btnl = QHBoxLayout(btnc)
        btnl.setContentsMargins(0, 0, 0, 0)
        btnl.setSpacing(0) # Attached buttons

        # SVGs (White/Light Gray for Dark Mode)
        # Minimize (Line at bottom)
        self.svg_min = b'''
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <line x1="7" y1="12" x2="17" y2="12" stroke="#ffffff" stroke-width="1"/>
        </svg>
        '''
        # Maximize (Square)
        self.svg_max = b'''
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="7.5" y="7.5" width="9" height="9" stroke="#ffffff" stroke-width="1" fill="none"/>
        </svg>
        '''
        # Close (X)
        self.svg_close = b'''
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M7 7L17 17M17 7L7 17" stroke="#ffffff" stroke-width="1.2"/>
        </svg>
        '''
        
        # Buttons
        self.btn_min = AnimTitleButton(self.svg_min, "rgba(255, 255, 255, 0.1)")
        self.btn_max = AnimTitleButton(self.svg_max, "rgba(255, 255, 255, 0.1)")
        self.btn_close = AnimTitleButton(self.svg_close, "#e81123") # Standard Red Close
        
        btnl.addWidget(self.btn_min)
        btnl.addWidget(self.btn_max)
        btnl.addWidget(self.btn_close)
        layout.addWidget(btnc)

        # Logic
        self.btn_min.clicked.connect(lambda: self.window().showMinimized())
        self.btn_close.clicked.connect(lambda: self.window().close())
        
        # Maximize/Restore Toggle Logic
        def toggle_maximize():
            win = self.window()
            if win.isMaximized():
                win.showNormal()
                # Update icon to Maximize
                # (For simplicity we keep same icon or could toggle svg)
            else:
                win.showMaximized()
                # Update icon to Restore (Overlapping squares)

        self.btn_max.clicked.connect(toggle_maximize)

        # Drag Logic
        def is_maximized():
            return self.window().isMaximized()

        def mousePressEvent(event):
            if event.button() == Qt.LeftButton and not is_maximized():
                # Check if click is not on buttons (handled by their own events, but QWidget consumes?)
                # Since buttons are children, they get events first.
                self._drag_active = True
                self._drag_offset = event.globalPos() - self.window().frameGeometry().topLeft()
            event.accept()

        def mouseMoveEvent(event):
            if self._drag_active and not is_maximized():
                self.window().move(event.globalPos() - self._drag_offset)
            event.accept()

        def mouseReleaseEvent(event):
            if event.button() == Qt.LeftButton:
                self._drag_active = False
                self._drag_offset = None
            event.accept()
            
        def mouseDoubleClickEvent(event):
             if event.button() == Qt.LeftButton:
                toggle_maximize()

        self.mousePressEvent = mousePressEvent
        self.mouseMoveEvent = mouseMoveEvent
        self.mouseReleaseEvent = mouseReleaseEvent
        self.mouseDoubleClickEvent = mouseDoubleClickEvent



class OutputTerminalDialog(QDialog):
    """Dialogo de terminal para mostrar salida de scripts"""
    def __init__(self, script_path, interpreter, parent=None):
        super().__init__(parent)
        self.script_path = script_path
        self.interpreter = interpreter
        self.interpreter = interpreter
        # Fix: Ensure Qt.Dialog flag is present so self.window() in TitleBar returns THIS dialog, not the parent main window
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(900, 600)
        self.init_ui()
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        self.start_process()

    def init_ui(self):
        # Fondo y borde
        self.container = QWidget(self)
        self.container.setObjectName("TerminalContainer")
        self.container.setStyleSheet("""
            #TerminalContainer {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 8px;
            }
        """)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.container)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Barra de titulo
        self.titlebar = TitleBar(self, title=f"Terminal: {os.path.basename(self.script_path)}")
        self.titlebar.setStyleSheet("background-color: #161b22; border-top-left-radius: 8px; border-top-right-radius: 8px;")
        layout.addWidget(self.titlebar)

        # Area de texto de terminal
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setFont(QFont("Consolas", 10))
        self.terminal_output.setStyleSheet("""
            QTextEdit {
                background-color: #0d1117;
                color: #c9d1d9;
                border: none;
                padding: 10px;
                selection-background-color: #58a6ff;
                selection-color: #0d1117;
            }
        """)
        layout.addWidget(self.terminal_output)
        
        # Barra estado inferior
        self.status_bar = QLabel("Iniciando...")
        self.status_bar.setStyleSheet("color: #8b949e; padding: 5px 10px; border-top: 1px solid #30363d; font-family: Segoe UI; font-size: 11px;")
        layout.addWidget(self.status_bar)

    def start_process(self):
        self.terminal_output.append(f"<span style='color: #8b949e;'>$ {self.interpreter} \"{self.script_path}\"</span><br>")
        self.status_bar.setText("Ejecutando script...")
        self.process.start(self.interpreter, [self.script_path])
        
        # Setup working directory to script dir
        self.process.setWorkingDirectory(os.path.dirname(self.script_path))

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode('utf-8', errors='replace')
        self.terminal_output.moveCursor(QtGui.QTextCursor.End)
        self.terminal_output.insertPlainText(data)
        self.terminal_output.moveCursor(QtGui.QTextCursor.End)

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode('utf-8', errors='replace')
        self.terminal_output.moveCursor(QtGui.QTextCursor.End)
        # Estilo rojo para errores
        self.terminal_output.insertHtml(f"<span style='color: #ff7b72;'>{data}</span>")
        self.terminal_output.moveCursor(QtGui.QTextCursor.End)

    def handle_finished(self, exit_code, exit_status):
        color = "#3fb950" if exit_code == 0 else "#ff7b72"
        msg = "Completado con éxito" if exit_code == 0 else f"Falló con código {exit_code}"
        self.terminal_output.append(f"<br><span style='color: {color}; font-weight:bold;'>Process finished: {msg}</span>")
        self.status_bar.setText(f"Estado: {msg}")


def get_github_style(is_dark):
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

class ProjectDetailsDialog(QDialog):
    """Dialogo detallado para gestión de proyectos/apps"""
    def __init__(self, parent, pkg_data, is_app=False, manager_ref=None):
        super().__init__(parent)
        self.pkg = pkg_data
        self.is_app = is_app
        self.manager = manager_ref 
        # Fix: Ensure Qt.Dialog flag is present
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(550, 450) # Reduced size slightly
        self.init_ui()

    def init_ui(self):
        self.container = QWidget(self)
        self.container.setObjectName("DetailsContainer")
        # Base container style
        self.container.setStyleSheet("""
            #DetailsContainer {
                background-color: #ffffff;
                border: 1px solid #d1d5da;
                border-radius: 8px;
            }
        """)
        
        is_dark = detect_dark = detectar_modo_sistema()
        if is_dark:
             self.container.setStyleSheet("""
            #DetailsContainer {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 8px;
                color: #c9d1d9;
            }
            QLabel { color: #c9d1d9; font-family: 'Segoe UI', sans-serif; }
            QListWidget { 
                background-color: #161b22; 
                border: 1px solid #30363d; 
                color: #c9d1d9; 
                border-radius: 6px;
                padding: 4px;
            }
            QListWidget::item { 
                padding: 5px; 
            }
            QListWidget::item:selected {
                background-color: #1f2428;
                border: 1px solid #58a6ff;
                border-radius: 4px;
            }
        """)
        else:
            # Light mode styles for list
            self.container.setStyleSheet(self.container.styleSheet() + """
            QListWidget {
                background-color: #f6f8fa;
                border: 1px solid #e1e4e8;
                color: #24292e;
                border-radius: 6px;
                padding: 4px;
            }
            QListWidget::item { padding: 5px; }
            QListWidget::item:selected {
                background-color: #e1e4e8;
                border: 1px solid #0366d6;
                border-radius: 4px;
            }
            """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.container)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title Bar
        title = f"App: {self.pkg.get('titulo', 'Unknown')}" if self.is_app else f"Proyecto: {self.pkg.get('titulo', 'Unknown')}"
        icon_path = self.pkg.get("icon")
        icon_pm = QIcon(icon_path) if icon_path else None
        
        self.titlebar = CustomTitleBar(self, title=title, icon=icon_path or "")
        # Usamos el estilo nativo de LeviathanUI
        # self.titlebar.setStyleSheet(...)
        layout.addWidget(self.titlebar)

        # Contenido
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        # Info Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        # Icono grande
        icon_lbl = QLabel()
        pm = QPixmap(icon_path) if icon_path else QPixmap(80, 80)
        if not icon_path: pm.fill(Qt.transparent)
        icon_lbl.setPixmap(pm.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_lbl.setFixedSize(80, 80)
        header_layout.addWidget(icon_lbl)
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        title_lbl = QLabel(f"<h2 style='margin:0; font-size: 20px;'>{self.pkg.get('titulo')}</h2>")
        title_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        ver = self.pkg.get('version', '0.0')
        pub = self.pkg.get('empresa', 'Unknown').capitalize()
        categ = self.pkg.get('rating', 'Unknown') if not self.is_app else "Instalado"
        
        # Determine colors for meta text
        color_pub = "#58a6ff" if is_dark else "#0366d6"
        color_meta = "#8b949e" if is_dark else "#586069"
        
        meta_html = f"<span style='color:{color_pub}; font-weight:bold;'>{pub}</span> &bull; <span style='color:{color_meta};'>{ver}</span> &bull; <span style='color:{color_meta};'>{categ}</span>"
        meta_lbl = QLabel(meta_html)
        meta_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        folder_path = self.pkg.get('folder', '')
        # Truncate path if too long for display nicely
        short_path = (folder_path[:60] + '...') if len(folder_path) > 60 else folder_path
        
        folder_lbl = QLabel(short_path)
        folder_lbl.setToolTip(folder_path)
        folder_lbl.setStyleSheet(f"color: {color_meta}; font-size: 11px;")
        folder_lbl.setWordWrap(True)
        folder_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)

        info_layout.addWidget(title_lbl)
        info_layout.addWidget(meta_lbl)
        info_layout.addWidget(folder_lbl)
        info_layout.addStretch()
        
        header_layout.addLayout(info_layout)
        header_layout.addStretch() # Push everything to left
        content_layout.addLayout(header_layout)

        content_layout.addWidget(QLabel("<b>Scripts ejecutables:</b>"))
        
        self.scripts_list = QListWidget()
        self.scripts_list.setIconSize(QtCore.QSize(20,20))
        # Populamos
        if os.path.exists(self.pkg["folder"]):
            for root, _, files in os.walk(self.pkg["folder"]):
                for f in files:
                    if f.endswith(".py"):
                        full_p = os.path.join(root, f)
                        rel_p = os.path.relpath(full_p, self.pkg["folder"])
                        item = QListWidgetItem(QIcon("app/python-icon.png"), rel_p) # Placeholder icon if null
                        item.setData(QtCore.Qt.UserRole, full_p)
                        self.scripts_list.addItem(item)
        
        # Limit list height to avoid taking too much space
        self.scripts_list.setFixedHeight(120)
        content_layout.addWidget(self.scripts_list)

        content_layout.addWidget(self.scripts_list)

        # Botones de accion
        # Obtener estilos GitHub
        action_style, normal_style = get_github_style(is_dark)

        # Helper/Closure para botones
        def mk_btn(text, is_primary=False, icon_str=None):
            btn = QPushButton(text)
            btn.setFixedHeight(36)
            # No establecemos font aquí porque el stylesheet lo maneja mejor para coherencia
            if icon_str and icon_str in TAB_ICONS:
                # Opcional: Podríamos no usar iconos para ser mas fiel al estilo "limpio" de GitHub, 
                # pero los conservamos por usabilidad.
                btn.setIcon(QIcon(TAB_ICONS[icon_str]))
            
            btn.setStyleSheet(action_style if is_primary else normal_style)
            return btn
        
        self.btn_run = mk_btn("Ejecutar", is_primary=False, icon_str="construir")
        self.btn_run.clicked.connect(self.run_selected_script)
        
        # Layout principal de botones
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        # Botones izquierdos
        btn_layout.addWidget(self.btn_run)

        if self.is_app:
            self.btn_uninstall = mk_btn("Desinstalar", is_primary=False, icon_str="desinstalar")
            self.btn_uninstall.clicked.connect(self.uninstall_action)
            btn_layout.addWidget(self.btn_uninstall)
        else:
            self.btn_install = mk_btn("Instalar", is_primary=False, icon_str="instalar")
            self.btn_install.clicked.connect(self.install_action)
            
            self.btn_delete = mk_btn("Eliminar", is_primary=False, icon_str="desinstalar")
            self.btn_delete.clicked.connect(self.delete_action)
            
            btn_layout.addWidget(self.btn_install)
            btn_layout.addWidget(self.btn_delete)
        
        content_layout.addLayout(btn_layout)

        # Boton de compilar (Solo para proyectos locales)
        if not self.is_app:
            content_layout.addSpacing(10)
            self.btn_compile = mk_btn("Compilar Proyecto", is_primary=True, icon_str="construir")
            self.btn_compile.setFixedHeight(40) 
            self.btn_compile.clicked.connect(self.compile_action)
            content_layout.addWidget(self.btn_compile)
        
        self.lbl_status = QLabel("")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        
        content_layout.addWidget(self.lbl_status) # Add status label below buttons
        content_layout.addStretch()
        layout.addLayout(content_layout)

    def run_selected_script(self):
        item = self.scripts_list.currentItem()
        if not item:
            return
        script_path = item.data(QtCore.Qt.UserRole)
        
        python = find_python_executable()
        if not python:
             LeviathanDialog.launch(self, "Python no encontrado", "No se detectó una instalación de Python válida para ejecutar el script.", mode="error")
             return
             
        # Abrir terminal
        self.terminal = OutputTerminalDialog(script_path, python, self)
        self.terminal.exec_()
    
    def install_action(self):
        # Logica de buscar .iflapp y descomprimir
        found = False
        base_name = self.pkg.get("name", "")
        # Busqueda laxa
        valid_file = None
        for f in os.listdir(BASE_DIR):
            if (f.endswith(".iflapp") or f.endswith(".iflappb")) and self.pkg['name'] in f:
                valid_file = os.path.join(BASE_DIR, f)
                break
        
        if valid_file:
            target_dir = os.path.join(Fluthin_APPS, self.pkg['name'])
            try:
                os.makedirs(target_dir, exist_ok=True)
                with zipfile.ZipFile(valid_file, 'r') as zf:
                    zf.extractall(target_dir)
                LeviathanDialog.launch(self, "Éxito", "App instalada correctamente.", mode="success")
                if hasattr(self.manager, "load_manager_lists"): self.manager.load_manager_lists()
            except Exception as e:
                LeviathanDialog.launch(self, "Error", str(e), mode="error")
            else:
                LeviathanDialog.launch(self, "No encontrado", "No se encontró el paquete compilado (.iflapp) en la carpeta de proyectos. Primero compílalo.", mode="warning")

    def uninstall_action(self):
         def do_uninstall(res):
             if res == "SÍ":
                 try:
                     shutil.rmtree(self.pkg["folder"])
                     self.accept()
                     if hasattr(self.manager, "load_manager_lists"): self.manager.load_manager_lists()
                 except Exception as e:
                     LeviathanDialog.launch(self, "Error", str(e), mode="error")
         
         LeviathanDialog.launch(self, "Desinstalar", "¿Estás seguro de eliminar esta app?", mode="warning", buttons=["SÍ", "NO"], callback=do_uninstall)

    def delete_action(self):
         def do_delete(res):
             if res == "SÍ":
                 try:
                     shutil.rmtree(self.pkg["folder"])
                     self.accept()
                     if hasattr(self.manager, "load_manager_lists"): self.manager.load_manager_lists()
                 except Exception as e:
                     LeviathanDialog.launch(self, "Error", str(e), mode="error")

         LeviathanDialog.launch(self, "Eliminar", "¿Estás seguro de eliminar este proyecto y todos sus archivos? Esta acción no se puede deshacer.", mode="error", buttons=["SÍ", "NO"], callback=do_delete)

    def compile_action(self):
        # Trigger compilation using BuildThread
        self.btn_compile.setEnabled(False)
        self.lbl_status.setText("Compilando...")
        
        # Extract metadata
        empresa = self.pkg.get('empresa', 'influent')
        nombre = self.pkg.get('app', self.pkg.get('name', 'unknown')) # Try internal name first
        version = self.pkg.get('version', '1.0').replace("v", "").split("-")[0]
        plataforma = self.pkg.get('platform', 'Windows')
        
        # Build Mode Dialog? Assume Portable default for Manager quick compile
        self.build_thread = BuildThread(empresa, nombre, version, plataforma, parent=self, custom_path=self.pkg.get('folder'), build_mode="portable")
        self.build_thread.progress.connect(lambda msg: self.lbl_status.setText(msg))
        self.build_thread.finished.connect(self.on_compile_finished)
        self.build_thread.error.connect(lambda msg: self.lbl_status.setText(f"Error: {msg}"))
        self.build_thread.start()

    def on_compile_finished(self, msg):
        self.lbl_status.setText(msg)
        self.btn_compile.setEnabled(True)
        LeviathanDialog.launch(self, "Compilación", msg, mode="info")

class SidebarItem(QPushButton):
    """Boton de navegación lateral estilo Start11"""
    def __init__(self, text, icon_path, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(50)
        self.setIconSize(QtCore.QSize(24, 24))
        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #b0b0b0;
                text-align: left;
                padding-left: 17px; /* Compensate for border */
                border: none;
                border-left: 3px solid transparent; /* Anti-jump reserve */
                outline: none;
                border-radius: 8px;
                font-family: 'Segoe UI Variable Display', 'Segoe UI', sans-serif;
                font-size: 15px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.05);
                color: #ffffff;
            }
            QPushButton:checked {
                background-color: rgba(255, 255, 255, 0.08);
                color: #ffffff;
                border-left: 3px solid #ff5722; /* Start11 Orange Accent */
            }
            QPushButton:focus {
                border: none;
                outline: none;
            }
        """)

SIDEBAR_DESC = {
    0: "### Crear Proyecto\nDiseña aplicaciones desde cero. Establece identidades únicas, versiones y metadatos para el ecosistema **Influent OS** de forma guiada.",
    1: "### Construir Paquete\nEmpaqueta tu trabajo. Transforma carpetas de desarrollo en archivos `.iflapp` comprimidos y listos para su distribución global.",
    2: "### Gestor de Aplicaciones\nTu centro de control. Administra proyectos locales y aplicaciones instaladas. Ejecuta, depura o elimina con absoluta precisión.",
    3: "### Configuración\nAjusta el motor del programa. Controla rutas de almacenamiento, previsualización de temas y variables globales del sistema.",
    4: "### MoonFix Suite\nSanación profunda. Escanea, detecta y repara inconsistencias en tus paquetes. Asegura que cada asset y etiqueta XML sea perfecta.",
    5: "### Acerca de\nDetalles técnicos del proyecto. Información sobre la licencia GPL, el framework Qt y el equipo que hace posible **Package Maker**."
}

class PackageTodoGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- VERSION UPDATE 3.2.6 ---
        self.current_version = "3.2.6"
        
        # Aplicar estética Premium de LeviathanUI (WipeWindow)
        # Usamos ghostBlur como solicitado
        self.window_effects = WipeWindow.create().set_mode("ghostBlur").set_radius(12).apply(self)

        self.setWindowTitle(f"Influent Package Maker v{self.current_version}")
        self.resize(1100, 720)
        self.setFont(APP_FONT)
        self.setWindowIcon(QtGui.QIcon(IPM_ICON_PATH if os.path.exists(IPM_ICON_PATH) else ""))

        # Central Widget & Main Layout
        self.central = QWidget()
        self.central.setObjectName("CentralWidget")
        self.central.setStyleSheet("background-color: transparent;") 
        self.setCentralWidget(self.central)
        
        # Layout principal vertical (TitleBar + ContentArea)
        self.v_layout = QVBoxLayout(self.central)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setSpacing(0)

        # Title Bar Custom (LeviathanUI)
        self.titlebar = CustomTitleBar(self, title=self.windowTitle(), icon=(IPM_ICON_PATH if os.path.exists(IPM_ICON_PATH) else ""))
        self.titlebar.setStyleSheet("background-color: transparent;") # Dejar que el blur del fondo actue o poner un semi-transparente
        self.v_layout.addWidget(self.titlebar)

        # Content Container (Sidebar + Stack)
        self.content_container = QWidget()
        self.content_layout = QHBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # --- SIDEBAR (Left) ---
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(260)
        self.sidebar.setStyleSheet("background-color: rgba(20, 20, 20, 0.6); border-right: 1px solid rgba(255,255,255,0.08);")
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(15, 20, 15, 20)
        self.sidebar_layout.setSpacing(8)

        # Header Sidebar (Optional, maybe "Menú Inicio" text style)
        lbl_menu = QLabel("Menú Principal")
        lbl_menu.setStyleSheet("color: #ffffff; font-size: 22px; font-weight: bold; font-family: 'Segoe UI'; margin-bottom: 10px;")
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
        self.sidebar_desc_text.setFrameShape(QtWidgets.QFrame.NoFrame)
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
        
        # Startup Animation
        self.animate_startup()
        
        # Initial description
        self.update_sidebar_description(0)

    def update_sidebar_description(self, index):
        if index in SIDEBAR_DESC:
            # Simple markdown-to-html like formatting for headings
            text = SIDEBAR_DESC[index]
            html = text.replace("### ", "<b style='color:white; font-size:14px;'>").replace("\n", "</b><br>")
            self.sidebar_desc_text.setHtml(html)

    def animate_startup(self):
        """Animación de desplazamiento hacia arriba y opacidad al abrir"""
        # Center on screen first
        screen_geo = QApplication.desktop().screenGeometry()
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
        self.anim_pos.setEasingCurve(QtCore.QEasingCurve.OutExpo)
        
        # Animacion de opacidad
        self.anim_fade = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.anim_fade.setDuration(800)
        self.anim_fade.setStartValue(0.0)
        self.anim_fade.setEndValue(1.0)
        
        self.anim_group = QtCore.QParallelAnimationGroup(self)
        self.anim_group.addAnimation(self.anim_pos)
        self.anim_group.addAnimation(self.anim_fade)
        self.anim_group.start()

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
        anim_current.setEasingCurve(QtCore.QEasingCurve.OutQuint)
        
        # Next widget slides in from right
        anim_next = QtCore.QPropertyAnimation(next_widget, b"pos")
        anim_next.setDuration(450)
        anim_next.setStartValue(QtCore.QPoint(width, 0))
        anim_next.setEndValue(QtCore.QPoint(0, 0))
        anim_next.setEasingCurve(QtCore.QEasingCurve.OutQuint)
        
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
        anim_slide.setEasingCurve(QtCore.QEasingCurve.OutExpo)
        
        anim_group.addAnimation(anim_fade)
        anim_group.addAnimation(anim_slide)
        anim_group.start(QtCore.QAbstractAnimation.DeleteWhenStopped)


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
            l.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
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
        self.btn_browse_icon.setCursor(Qt.PointingHandCursor)
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

        # Fila 6 Platform
        l_plat = uwp_label("Plataforma Destino:")
        l_plat.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        l_plat.setStyleSheet(l_plat.styleSheet() + "margin-top: 8px;")
        form_layout.addWidget(l_plat, 6, 0)
        
        # Radios
        self.platform_group = QButtonGroup()
        plat_layout = QHBoxLayout()
        plat_layout.setSpacing(20)
        plat_layout.setContentsMargins(0, 5, 0, 0) # Top margin to align with label text vertically if needed
        
        def uwp_radio(text):
            r = QRadioButton(text)
            r.setMinimumHeight(30)
            # UWP Radio: Circle with dot. 
            r.setStyleSheet("""
                QRadioButton {
                    color: #ddd;
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 14px;
                    spacing: 8px;
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
                /* Inner dot is handled by checking mechanism or image usually, 
                   but Qt unchecked/checked bg works for simple flat style */
            """)
            return r

        self.radio_windows = uwp_radio("Windows")
        self.radio_windows.setChecked(True)
        self.radio_linux = uwp_radio("Linux")
        self.radio_multiplataforma = uwp_radio("Multiplataforma")
        
        self.platform_group.addButton(self.radio_windows)
        self.platform_group.addButton(self.radio_linux)
        self.platform_group.addButton(self.radio_multiplataforma)
        
        plat_layout.addWidget(self.radio_windows)
        plat_layout.addWidget(self.radio_linux)
        plat_layout.addWidget(self.radio_multiplataforma)
        plat_layout.addStretch()
        
        form_layout.addLayout(plat_layout, 6, 1)

        layout.addWidget(form_group)

        # Action Area
        layout.addSpacing(20)
        action_layout = QHBoxLayout()
        
        self.create_status = QLabel("")
        self.create_status.setStyleSheet("color: #aaa; margin-left: 10px;")
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
        self.btn_create_action.setCursor(Qt.PointingHandCursor)
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
             p.setRenderHint(QtGui.QPainter.Antialiasing)
             path = QtGui.QPainterPath()
             path.addEllipse(0, 0, size, size)
             p.setClipPath(path)
             p.drawPixmap(0, 0, size, size, pixmap)
             p.end()
             self.avatar_label.setPixmap(target)
        except Exception as e:
             print(f"Error descargando avatar: {e}")

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
        self.radio_windows.setEnabled(False)
        self.radio_linux.setEnabled(False)
        self.radio_multiplataforma.setEnabled(False)
        
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
        self.radio_windows.setEnabled(True)
        self.radio_linux.setEnabled(True)
        self.radio_multiplataforma.setEnabled(True)
        
        if not valido:
            self.create_status.setStyleSheet("color:#c62828;")
            self.create_status.setText(f"❌ Error: {mensaje}. Por favor, especifica un username válido que exista en GitHub.")
            self.statusBar().showMessage("Verificación fallida")
            return
        
        # Si la verificación fue exitosa, continuar con la creación del proyecto
        autor = self.input_autor.text().strip()
        
        # Obtener plataforma seleccionada
        if self.radio_windows.isChecked():
            plataforma_seleccionada = "Knosthalij"
            xte = "exe"
        elif self.radio_linux.isChecked():
            plataforma_seleccionada = "Danenone"
            xte = "appImage"
        else:
            plataforma_seleccionada = "AlphaCube"
            xte = "nrdPkg"
        
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
        form_layout.setSpacing(15)
        form_layout.setColumnMinimumWidth(0, 160)
        form_layout.setColumnStretch(1, 1)
        
        # UWP Style Definition for Controls
        # Labels: Segoe UI, 14px, #cccccc
        def uwp_label(text):
            l = QLabel(text)
            l.setStyleSheet("font-family: 'Segoe UI', sans-serif; font-size: 14px; color: #cccccc; font-weight: 500;")
            l.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            return l
            
        def uwp_input(placeholder, read_only=False):
            line = QLineEdit()
            line.setPlaceholderText(placeholder)
            line.setReadOnly(read_only)
            line.setFixedHeight(35)
            # UWP Style (Shared with Create Tab)
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
        l_mode.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        l_mode.setStyleSheet(l_mode.styleSheet() + "margin-top: 8px;")
        form_layout.addWidget(l_mode, 4, 0)
        
        self.build_mode_group = QButtonGroup()
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(20)
        mode_layout.setContentsMargins(0, 5, 0, 0)
        
        def uwp_radio(text):
            r = QRadioButton(text)
            r.setMinimumHeight(30)
            r.setStyleSheet("""
                QRadioButton {
                    color: #ddd;
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 14px;
                    spacing: 8px;
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
        self.btn_select_folder.setCursor(Qt.PointingHandCursor)
        self.btn_select_folder.setFixedSize(40, 35)
        self.btn_select_folder.setStyleSheet("""
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
        self.btn_select_folder.clicked.connect(self.select_custom_folder)
        custom_box.addWidget(self.btn_select_folder)
        
        form_layout.addLayout(custom_box, 5, 1)

        layout.addWidget(form_group)
        
        layout.addSpacing(20)

        # Action Area
        action_layout = QHBoxLayout()
        
        self.build_status = QLabel("")
        self.build_status.setStyleSheet("color: #aaa; margin-left: 10px;")
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
        self.btn_build.setCursor(Qt.PointingHandCursor)
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
        
        self.build_thread = BuildThread(empresa, nombre, version_full, platformLineEdit, parent=self, custom_path=custom_path, build_mode=build_mode)
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
        title_lbl.setStyleSheet("font-size: 24px; font-weight: 600; color: white; margin-bottom: 5px;")
        layout.addWidget(title_lbl)
        
        # Main Splitter
        splitter = QSplitter(Qt.Horizontal)
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
            lbl.setStyleSheet("font-family: 'Segoe UI'; font-size: 16px; font-weight: 600; color: #e0e0e0;")
            vbox.addWidget(lbl)
            
            # Styled ListWidget
            list_widget.setIconSize(QtCore.QSize(36, 36))
            list_widget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
            list_widget.setFocusPolicy(Qt.NoFocus)
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
            btn.setCursor(Qt.PointingHandCursor)
            
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
            item.setData(QtCore.Qt.UserRole, p)
            self.projects_list.addItem(item)
        apps = self.get_package_list(Fluthin_APPS)
        for a in apps:
            icon = QIcon(a["icon"]) if a["icon"] else self.style().standardIcon(QStyle.SP_DesktopIcon)
            text = a['empresa'].capitalize()
            text = f"{text} {a['titulo']} | {a['version']}"
            item = QListWidgetItem(icon, text)
            item.setData(QtCore.Qt.UserRole, a)
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
             comp_pub.setCaseSensitivity(Qt.CaseInsensitive)
             comp_pub.setFilterMode(Qt.MatchContains) # Busqueda recursiva/flexible
             self.input_build_empresa.setCompleter(comp_pub)

             comp_name = QtWidgets.QCompleter(names, self)
             comp_name.setCaseSensitivity(Qt.CaseInsensitive)
             comp_name.setFilterMode(Qt.MatchContains) # Busqueda recursiva/flexible
             self.input_build_nombre.setCompleter(comp_name)

    def on_project_double_click(self, item):
        pkg = item.data(QtCore.Qt.UserRole)
        dlg = ProjectDetailsDialog(self, pkg, is_app=False, manager_ref=self)
        dlg.exec_()

    def on_app_double_click(self, item):
        pkg = item.data(QtCore.Qt.UserRole)
        dlg = ProjectDetailsDialog(self, pkg, is_app=True, manager_ref=self)
        dlg.exec_()

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
        pkg = item.data(QtCore.Qt.UserRole)
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
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
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
            new_config = {
                "BASE_DIR": self.conf_base_dir.text().strip(),
                "Fluthin_APPS": Fluthin_APPS, # Mantener actual
                "GLOBAL_VARS": self.conf_vars.toPlainText().strip(),
                "DISPLAY_MODE": APP_CONFIG.get("DISPLAY_MODE", "GhostBlur (Cristal)")
            }
            if save_app_config(new_config):
                # Update global BASE_DIR
                global BASE_DIR
                BASE_DIR = new_config["BASE_DIR"]
                LeviathanDialog.launch(self, "Configuración", "Los cambios han sido guardados en config\\settings.json exitosamente.", mode="success")
            else:
                LeviathanDialog.launch(self, "Configuración", "Error al escribir el archivo de configuración.", mode="error")

        # Save Button
        vbox.addSpacing(20)
        btn_save = QPushButton("Guardar Configuración")
        btn_save.setFixedHeight(40)
        btn_save.setCursor(Qt.PointingHandCursor)
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
        btn_sel.setCursor(Qt.PointingHandCursor)
        btn_sel.setStyleSheet("QPushButton { background-color: rgba(255,255,255,0.1); color: white; border-radius: 4px; } QPushButton:hover { background-color: rgba(255,255,255,0.2); }")
        btn_sel.clicked.connect(self.mf_browse)
        
        s_box.addWidget(self.mf_input)
        s_box.addWidget(btn_sel)
        layout.addLayout(s_box)
        
        layout.addStretch()
        
        # Action Button
        btn_scan = QPushButton("Iniciar Diagnóstico de MoonFix")
        btn_scan.setFixedHeight(45)
        btn_scan.setCursor(Qt.PointingHandCursor)
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
        if wizard.exec_() == QDialog.Accepted:
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
            logo_lbl.setAlignment(Qt.AlignCenter)
            
        title_box = QVBoxLayout()
        t_main = QLabel("Influent Package Maker")
        t_main.setStyleSheet("font-size: 28px; font-weight: bold; color: white; font-family: 'Segoe UI Variable Display';")
        t_ver = QLabel(f"Versión {self.current_version}")
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
        l3, v3 = spec_item("Framework:", f"Qt {QtCore.qVersion()} (PyQt5)")
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
        btn_github.setCursor(Qt.PointingHandCursor)
        # Open URL logic
        
        btn_telegram = QPushButton("Telegram")
        btn_telegram.setStyleSheet("background-color: #0088cc; color: white; border: none; border-radius: 4px; padding: 8px 16px;")
        btn_telegram.setCursor(Qt.PointingHandCursor)
        
        footer.addWidget(btn_github)
        footer.addWidget(btn_telegram)
        footer.addStretch()
        
        layout.addLayout(footer)


def main():
    app = QApplication(sys.argv)
    app.setFont(APP_FONT)
    
    # Splash Screen Inmersivo de LeviathanUI
    # User requested app/app-icon.ico and marquee progress
    splash = InmersiveSplash(title="Package Maker", logo="app/app-icon.ico" if os.path.exists("app/app-icon.ico") else "")
    
    # Configure phrases
    splash.set_phrases([None])
    
    # Configure output splash
    # marquee=True makes the progress bar indeterminate/animated
    splash.set_progress_mode(marquee=True) 

    def start_app():
        w = PackageTodoGUI()
        # Adjuntar splash de salida
        splash.attach_to_window(w, exit_phrases=[None])
        w.show()
        if getattr(sys, 'frozen', False):
            try:
                import pyi_splash
                pyi_splash.close()
            except ImportError:
                pass
                
    splash.on_finish(start_app)
    splash.launch()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
