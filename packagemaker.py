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
    QPushButton, QComboBox, QListWidget, QListWidgetItem, QFileDialog, QDialog, QStyle, QSizePolicy, QSplitter, QGroupBox, QRadioButton, QButtonGroup, QGridLayout, QProgressBar, QTextEdit
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtGui import QPixmap      # [NEW IMPORT FOR TITLEBAR SVG]
from PyQt5.QtSvg import QSvgRenderer # [NEW IMPORT FOR TITLEBAR SVG RENDERING]
from PyQt5.QtCore import QByteArray  # [NEW IMPORT FOR SVG BUFFER]
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QEvent, QObject, QProcess
import requests
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
TAB_FONT = QFont('Roboto', 12) #, QFont.Bold)
BUTTON_FONT = QFont('Roboto', 12, QFont.Bold)
TAB_ICONS = {
    "crear": "./app/package_add.ico",
    "construir": "./app/package_build.ico",
    "gestor": "./app/package_fm.ico",
    "about": "./app/package_about.ico",
    "instalar": "./app/package_install.ico",
    "desinstalar": "./app/package_uninstall.ico",
}
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

# Crear las carpetas si no existen
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(Fluthin_APPS, exist_ok=True)

IPM_ICON_PATH = "app/app-icon.ico"
DEFAULT_FOLDERS = "app,assets,config,docs,source,lib"

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

UPDATER_CODE = r'''import sys, os, requests, shutil, subprocess, xml.etree.ElementTree as ET
import threading, time, traceback
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QThread, QObject, pyqtSignal
# La clase InstallerWorker se integrará a continuación

XML_PATH = "details.xml"
LOG_PATH = "updater_log.txt"
CHECK_INTERVAL = 60
GITHUB_API = "https://api.github.com"

STYLE = """
QWidget { background-color: #0d1117; color: #2ecc71; font-family: "Segoe UI"; }
QPushButton { background-color: #2ecc71; color: white; border-radius: 6px; padding: 6px 12px; }
QPushButton:hover { background-color: #27ae60; }
"""

def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {msg}\n")
    print(f"{timestamp} {msg}")

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
    except Exception as e:
        log(f"❌ Error leyendo XML: {e}")
        return {}

def hay_conexion():
    try:
        requests.get(GITHUB_API, timeout=5)
        return True
    except:
        return False

def leer_xml_remoto(author, app):
    url = f"https://raw.githubusercontent.com/{author}/{app}/main/details.xml"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            root = ET.fromstring(r.text)
            return root.findtext("version", "").strip()
    except Exception as e:
        log(f"❌ Error leyendo XML remoto: {e}")
    return ""

def buscar_release(author, app, version, platform, publisher):
    url = f"{GITHUB_API}/repos/{author}/{app}/releases/tags/{version}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            log(f"❌ Release {version} no encontrado en {author}/{app}")
            return None
        assets = r.json().get("assets", [])
        target = f"{publisher}.{app}.{version}-{platform}.iflapp"
        log(f"🔍 Buscando asset: {target}")
        for a in assets:
            if a.get("name") == target:
                return a.get("browser_download_url")
        log(f"❌ Asset no encontrado en release. Esperado: {target}")
        return None
    except Exception as e:
        log(f"❌ Error consultando GitHub API: {e}")
        return None

# --- CLASE INSTALLER WORKER INTEGRADA ---
class InstallerWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    
    def __init__(self, url, app, platform):
        super().__init__()
        self.url = url
        self.app = app
        self.platform = platform

    def run(self):
        destino = "update.zip"
        try:
            log("🔐 Respaldando archivos…")
            if not os.path.exists("backup_embestido"):
                os.mkdir("backup_embestido")
            
            # Copiar solo archivos, excluyendo el directorio de backup y el archivo de destino
            for f in os.listdir("."):
                if f not in ["backup_embestido", destino] and os.path.isfile(f):
                    shutil.copy2(f, f"backup_embestido/{f}")
            log("✅ Respaldo completado.")

            log(f"⬇️ Descargando desde {self.url}")
            r = requests.get(self.url, stream=True)
            r.raise_for_status() # Lanza una excepción para códigos de estado HTTP erróneos

            total_size = int(r.headers.get('content-length', 0))
            bytes_downloaded = 0
            
            with open(destino, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
                    bytes_downloaded += len(chunk)
                    if total_size > 0:
                        percent = int((bytes_downloaded / total_size) * 100)
                        self.progress.emit(percent)
            
            self.progress.emit(100) # Asegurar que el progreso llegue al 100%
            log("✅ Descarga completada.")

            log("📦 Descomprimiendo archivos…")
            shutil.unpack_archive(destino, ".")
            os.remove(destino)
            log("✅ Archivos actualizados.")

            # Lógica de reinicio
            if not sys.argv[0].endswith(".py"):
                exe = f"{self.app}.exe" if os.name == "nt" else f"./{self.app}"
                if os.path.exists(exe):
                    log(f"🚀 Ejecutando {exe}")
                    subprocess.Popen(exe)
            else:
                log("🔁 Reiniciando script embestido...")
                # El reinicio del script embestido es complejo en un worker,
                # lo ideal es que el hilo principal se encargue de esto
                # o que el worker sepa que debe terminar la aplicación actual.
                # Por ahora, solo logueamos.
                pass
            
            self.finished.emit()

        except Exception as e:
            log(f"❌ Error durante instalación: {e}")
            log(traceback.format_exc())
            self.error.emit(f"Error de instalación: {e}")

# --- FIN CLASE INSTALLER WORKER INTEGRADA ---

class UpdaterWindow(QWidget):
    update_finished = pyqtSignal() # Señal para manejar el cierre de la ventana después de la actualización

    def __init__(self, app, version, platform, url):
        super().__init__()
        self.app = app
        self.version = version
        self.platform = platform
        self.url = url
        
        # Eliminar el borde nativo y permitir transparencia
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setWindowTitle("Actualizador de Flarm App")
        self.setFixedSize(460, 280) # Aumentar un poco el tamaño para el title bar
        self.setStyleSheet(STYLE)
        self.init_ui()
        
        # Variables para el arrastre de la ventana
        self._start_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._start_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self._start_pos is not None and event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self._start_pos)

    def mouseReleaseEvent(self, event):
        self._start_pos = None

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0) # Eliminar márgenes del layout principal

        # --- Title Bar (Custom) ---
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(40)
        self.title_bar.setStyleSheet("background-color: #161b22;") # Un color ligeramente diferente para el title bar
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 0, 0)
        title_layout.setSpacing(0)

        title_label = QLabel("Flarm Updater")
        title_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        # Botones de control (con iconos SVG)
        self.btn_minimize = QPushButton()
        self.btn_close = QPushButton()
        
        # Cargar iconos SVG (usando QPixmap para SVG)
        # Se asume que los archivos SVG están en el mismo directorio
        min_pm = os.path.join("assets", "min.svg")
        close_pm = os.path.join("assets", "close.svg")
        minimize_pixmap = QPixmap(min_pm)
        close_pixmap = QPixmap(close_pm)
        
        self.btn_minimize.setIcon(QIcon(minimize_pixmap))
        self.btn_close.setIcon(QIcon(close_pixmap))
        
        self.btn_minimize.setFixedSize(40, 40)
        self.btn_close.setFixedSize(40, 40)
        
        # Estilos para los botones (solo hover)
        self.btn_minimize.setStyleSheet("QPushButton { border: none; background-color: transparent; } QPushButton:hover { background-color: #30363d; }")
        self.btn_close.setStyleSheet("QPushButton { border: none; background-color: transparent; } QPushButton:hover { background-color: #e81123; }")

        self.btn_minimize.clicked.connect(self.showMinimized)
        self.btn_close.clicked.connect(self.close)

        title_layout.addWidget(self.btn_minimize)
        title_layout.addWidget(self.btn_close)
        
        main_layout.addWidget(self.title_bar)

        # --- Content Area ---
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Flarm Updater")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        info = QLabel(f"📦 {self.app}\n🔄 Nueva versión: {self.version}\n🖥️ Plataforma: {self.platform}")
        info.setFont(QFont("Segoe UI", 12))
        layout.addWidget(info)

        self.progress_label = QLabel("Listo para actualizar.")
        self.progress_label.setFont(QFont("Roboto", 10))
        layout.addWidget(self.progress_label)

        self.btn = QPushButton("Actualizar ahora")
        self.btn.clicked.connect(self.instalar)
        layout.addWidget(self.btn)

        main_layout.addWidget(content_widget)
        self.show()
        self.update_finished.connect(self.close) # Conectar la señal de finalización al cierre de la ventana

    def instalar(self):
        self.btn.setEnabled(False)
        self.progress_label.setText("Iniciando descarga...")

        self.thread = QThread()
        self.worker = InstallerWorker(self.url, self.app, self.platform)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.on_update_finished)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.error.connect(self.on_error)
        self.worker.progress.connect(self.on_progress)

        self.thread.start()

    def on_progress(self, percent):
        self.progress_label.setText(f"Descargando... {percent}%")

    def on_error(self, message):
        self.progress_label.setText(f"ERROR: {message}")
        self.btn.setEnabled(True)
        # Aquí se podría añadir un QMessageBox para notificar al usuario
        # Cerrar la ventana en caso de error grave
        self.update_finished.emit()

    def on_update_finished(self):
        self.progress_label.setText("Actualización completada. Reiniciando...")
        # Emitir la señal para cerrar la ventana, lo que debe ocurrir después de que el worker haya terminado
        self.update_finished.emit()

def ciclo_embestido():
    def verificar():
        while True:
            if not hay_conexion():
                log("🌐 Sin conexión. Esperando...")
                time.sleep(30)
                continue

            datos = leer_xml(XML_PATH)
            if not datos:
                time.sleep(CHECK_INTERVAL)
                continue

            log(f"📖 App: {datos['app']} | Versión local: {datos['version']} | Plataforma: {datos['platform']} | Publisher: {datos.get('publisher', 'N/A')}")
            remoto = leer_xml_remoto(datos["author"], datos["app"])
            if remoto and remoto != datos["version"]:
                log(f"🔄 Nueva versión remota: {remoto}")
                url = buscar_release(datos["author"], datos["app"], remoto, datos["platform"], datos.get("publisher", ""))
                if url:
                    log("✅ Actualización encontrada.")
                    app = QApplication(sys.argv)
                    ventana = UpdaterWindow(datos["app"], remoto, datos["platform"], url)
                    app.exec_()
                    return
                else:
                    log("❌ No se encontró asset para la plataforma.")
            else:
                log("ℹ️ No hay actualizaciones.")
            time.sleep(CHECK_INTERVAL)
    threading.Thread(target=verificar, daemon=True).start()

if __name__ == "__main__":
    log("🕶️ Actualizador IPM iniciado en modo silencioso.")
    ciclo_embestido()
    while True:
        time.sleep(3600)'''

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
class TitleBar(QWidget):  # [NEW CLASS: FULL CUSTOM TITLE BAR]
    """Custom non-native title bar with SVG buttons and context menu."""

    def __init__(self, parent=None, app_icon=None, title=""):
        super().__init__(parent)
        self._parent = parent
        self.setFixedHeight(38)
        self.setObjectName("customTitleBar")
        self._drag_active = False
        self._drag_offset = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 8, 0)
        layout.setSpacing(8)

        if app_icon:
            icon_lbl = QLabel()
            icon_lbl.setPixmap(app_icon.pixmap(20, 20))
            icon_lbl.setFixedSize(22, 22)
            layout.addWidget(icon_lbl)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.title_label)

        self.setMouseTracking(True)  # Necesario para rastrear el mouse para "señalizar" drag

        # Botones de control
        btnc = QWidget()
        btnl = QHBoxLayout(btnc)
        btnl.setContentsMargins(0, 0, 0, 0)
        btnl.setSpacing(6)

        self.svg_min = b'''
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="6" y="12" width="12" height="2" rx="1" fill="#333"/>
        </svg>
        '''
        self.svg_max = b'''
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="6" y="6" width="12" height="12" rx="2" fill="none" stroke="#333" stroke-width="2"/>
        </svg>
        '''
        self.svg_close = b'''
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <line x1="7" y1="7" x2="17" y2="17" stroke="#E81123" stroke-width="2" stroke-linecap="round"/>
            <line x1="17" y1="7" x2="7" y2="17" stroke="#E81123" stroke-width="2" stroke-linecap="round"/>
        </svg>
        '''
        self.btn_min = self._make_btn(self.svg_min)
        self.btn_max = self._make_btn(self.svg_max)
        self.btn_close = self._make_btn(self.svg_close)
        btnl.addWidget(self.btn_min)
        btnl.addWidget(self.btn_max)
        btnl.addWidget(self.btn_close)
        self.layout().addWidget(btnc)

        # -- Botones --
        self.btn_min.clicked.connect(lambda: self.window().showMinimized())
        self.btn_max.clicked.connect(lambda: self.window().showMaximized())
        self.btn_close.clicked.connect(lambda: self.window().close())

        # MENU
        self.menu = QtWidgets.QMenu(self)
        # (Estilos y acciones omitidos... igual que antes)

        # Arrastre: Señales y detención del drag con mouse events
        # Usaremos mouse event handlers para emitir/gestionar los eventos de mover
        # El "drag" ocurre sólo si no está maximizado!
        def is_maximized():
            return self.window().isMaximized()

        def mousePressEvent(event):
            if event.button() == Qt.LeftButton and not is_maximized():
                self._drag_active = True
                self._drag_offset = event.globalPos() - self.window().frameGeometry().topLeft()
            event.accept()
            QWidget.mousePressEvent(self, event)  # Llama base

        def mouseMoveEvent(event):
            if self._drag_active and not is_maximized():
                self.window().move(event.globalPos() - self._drag_offset)
            event.accept()
            QWidget.mouseMoveEvent(self, event)

        def mouseReleaseEvent(event):
            if event.button() == Qt.LeftButton:
                self._drag_active = False
                self._drag_offset = None
            event.accept()
            QWidget.mouseReleaseEvent(self, event)

        self.mousePressEvent = mousePressEvent
        self.mouseMoveEvent = mouseMoveEvent
        self.mouseReleaseEvent = mouseReleaseEvent

        # Ahora, para maximizar a cualquier resolución: 
        # showMaximized() siempre ocupa toda la pantalla disponible, sin importar el tamaño actual, 
        # y puedes restaurar con showNormal().
        # Los botones maximizan/restauran según el estado
        def toggle_maximize():
            win = self.window()
            if win.isMaximized():
                win.showNormal()
            else:
                win.showMaximized()
        self.btn_max.clicked.disconnect()
        self.btn_max.clicked.connect(toggle_maximize)

        # Opcional: hacer doble click en la barra también maximiza/restaura:
        def mouseDoubleClickEvent(event):
            if event.button() == Qt.LeftButton:
                toggle_maximize()
            event.accept()
        self.mouseDoubleClickEvent = mouseDoubleClickEvent

        # Preferible limpiar el cursor siempre (no tamaña ni resize)
        self.setCursor(Qt.ArrowCursor)

        # QSS uses palette-based colors for auto dark/light support, only override highlight color
        # Fix for NameError: Use hardcoded color values to avoid missing variables
        self.menu.setStyleSheet("""
            QMenu {
                background: #f8f9fa;
                border: 1px solid #d4d4d4;
                color: #212529;
            }
            QMenu::item {
                padding: 6px 28px 6px 28px;
                background: transparent;
            }
            QMenu::item:selected {
                background: #e5f1fb;
                color: #212529;
            }
        """)

    def _make_btn(self, svg_bytes):
        icon = self._svg_icon(svg_bytes)
        b = QPushButton()
        b.setFlat(True)
        b.setFixedSize(36, 28)
        b.setIcon(icon)
        b.setIconSize(QtCore.QSize(14, 14))
        # Eliminate (or debug) unwanted background/border issues - ensure no background is set:
        # Important: default QPushButton *does* show a flat red bg on Windows for QPixmap with alpha, if 'background' property gets brushed by theme/style or if SVGs themselves have no real transparency/white/rect.
        # Try forcing transparent or explicit background:
        b.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 4px;
                background: transparent;
            }
            QPushButton:pressed, QPushButton:hover {
                background: #e5e5e5;
            }
        """)
        return b

    def _svg_icon(self, svg_bytes):
        r = QSvgRenderer(QByteArray(svg_bytes))
        # Create ARGB pixmap, with full transparency (not default opaque)
        pix = QPixmap(16, 16)
        pix.fill(Qt.transparent)  # Explicitly clear to transparent!
        p = QtGui.QPainter(pix)
        # Sometimes, SVGs can include a <rect> with no fill, or use white as the background.
        # If SVG has an explicit fill on the elements with a nontransparent or red color, it will show up.
        r.render(p)
        p.end()
        return QIcon(pix)

    def _toggle_max(self):
        if self._parent.isMaximized():
            self._parent.showNormal()
        else:
            self._parent.showMaximized()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._press_pos = e.globalPos()
            self._start_geom = self._parent.geometry()

    def mouseMoveEvent(self, e):
        if self._press_pos and (e.buttons() & Qt.LeftButton):
            delta = e.globalPos() - self._press_pos
            self._parent.setGeometry(self._start_geom.translated(delta))

    def mouseDoubleClickEvent(self, e):
        self._toggle_max()

    def contextMenuEvent(self, e):
        self.menu.exec_(e.globalPos())
# === END CUSTOM TITLE BAR CLASS ===

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
        
        self.titlebar = TitleBar(self, app_icon=icon_pm, title=title)
        # Ajuste de estilo titlebar segun tema
        bg_tb = "#161b22" if is_dark else "#f6f8fa"
        fg_tb = "#c9d1d9" if is_dark else "#24292e"
        self.titlebar.setStyleSheet(f"""
            QWidget#customTitleBar {{
                background-color: {bg_tb}; 
                border-top-left-radius: 8px; 
                border-top-right-radius: 8px; 
                border-bottom: 1px solid #d1d5da;
            }}
            QLabel {{ color: {fg_tb}; font-weight: bold; }}
        """)
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
             QtWidgets.QMessageBox.critical(self, "Python no encontrado", "No se detectó una instalación de Python válida para ejecutar el script.")
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
                QtWidgets.QMessageBox.information(self, "Exito", "App instalada correctamente.")
                if hasattr(self.manager, "load_manager_lists"): self.manager.load_manager_lists()
            except Exception as e:
                 QtWidgets.QMessageBox.critical(self, "Error", str(e))
        else:
             QtWidgets.QMessageBox.warning(self, "No encontrado", "No se encontró el paquete compilado (.iflapp) en la carpeta de proyectos. Primero compílalo.")

    def uninstall_action(self):
         reply = QtWidgets.QMessageBox.question(self, "Desinstalar", "¿Estás seguro de eliminar esta app?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
         if reply == QtWidgets.QMessageBox.Yes:
             try:
                 shutil.rmtree(self.pkg["folder"])
                 self.accept()
                 if hasattr(self.manager, "load_manager_lists"): self.manager.load_manager_lists()
             except Exception as e:
                 QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def delete_action(self):
         reply = QtWidgets.QMessageBox.question(self, "Eliminar", "¿Estás seguro de eliminar este proyecto y todos sus archivos? Esta acción no se puede deshacer.", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
         if reply == QtWidgets.QMessageBox.Yes:
             try:
                 shutil.rmtree(self.pkg["folder"])
                 self.accept()
                 if hasattr(self.manager, "load_manager_lists"): self.manager.load_manager_lists()
             except Exception as e:
                 QtWidgets.QMessageBox.critical(self, "Error", str(e))

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
        QtWidgets.QMessageBox.information(self, "Compilación", msg)

class PackageTodoGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        self.setWindowTitle(f"Influent Package Maker for {plataforma} | QT5 Edition")
        self.resize(1200, 750)
        self.setFont(APP_FONT)
        self.setWindowIcon(QtGui.QIcon(IPM_ICON_PATH if os.path.exists(IPM_ICON_PATH) else ""))

        self.central = QWidget()
        self.v_layout = QVBoxLayout(self.central)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setSpacing(0)

        icon = QtGui.QIcon(IPM_ICON_PATH) if os.path.exists(IPM_ICON_PATH) else None
        self.titlebar = TitleBar(self, app_icon=icon, title=self.windowTitle())
        self.v_layout.addWidget(self.titlebar)

        self.main_container = QWidget()
        self.main_layout = QVBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.v_layout.addWidget(self.main_container)

        self.tabs = QTabWidget()
        self.tabs.setFont(TAB_FONT)
        self.main_layout.addWidget(self.tabs)

        self.setCentralWidget(self.central)

        self.layout = self.main_layout
        self.init_tabs()
        self.apply_theme()

        self.theme_timer = QTimer()
        self.theme_timer.timeout.connect(self.check_theme_change)
        self.theme_timer.start(1000)
        self.last_theme_mode = detectar_modo_sistema()

    def check_theme_change(self):
        """Verifica si el tema del sistema ha cambiado"""
        current_mode = detectar_modo_sistema()
        if current_mode != self.last_theme_mode:
            self.last_theme_mode = current_mode
            self.apply_theme()
    
    def apply_theme(self):
        """Aplica el tema naranja estilo GitHub con modo claro/oscuro automático"""
        is_dark = detectar_modo_sistema()
        
        # Tema Naranja estilo GitHub - Modo Claro
        theme_light = {
            "bg": "#ffffff",
            "fg": "#24292e",
            "border": "#e1e4e8",
            "input_bg": "#ffffff",
            "input_border": "#d1d5da",
            "button_default": "#f96c6c",  # Naranja GitHub
            "button_hover": "#fa4e4e",
            "button_text": "#ffffff",
            "group_bg": "#ffffff",
        }
        
        # Tema Naranja estilo GitHub - Modo Oscuro
        theme_dark = {
            "bg": "#0d1117",
            "fg": "#c9d1d9",
            "border": "#30363d",
            "input_bg": "#161b22",
            "input_border": "#21262d",
            "button_default": "#ff3932",  # Naranja GitHub
            "button_hover": "#d31e18",
            "button_text": "#ffffff",
            "group_bg": "#0d1117",
        }
        
        theme = theme_dark if is_dark else theme_light
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme["bg"]};
                color: {theme["fg"]};
            }}
            QWidget {{
                background-color: {theme["bg"]};
                color: {theme["fg"]};
            }}
            QTabWidget::pane {{
                border: 1px solid {theme["border"]};
                background-color: {theme["bg"]};
            }}
            QTabBar::tab {{
                background-color: {theme["group_bg"]};
                color: {theme["fg"]};
                padding: 10px;
                border: 1px solid {theme["border"]};
                border-bottom: none;
                border-radius: 6px 6px 0 0;
            }}
            QTabBar::tab:selected {{
                background-color: {theme["bg"]};
                border-bottom: 2px solid {theme["button_default"]};
            }}
            QGroupBox {{
                background-color: {theme["group_bg"]};
                color: {theme["fg"]};
                border: 1px solid {theme["border"]};
                border-radius: 6px;
                padding: 10px;
                margin-top: 10px;
                font-weight: bold;
            }}
            QLabel {{
                color: {theme["fg"]};
                font-size: 15px;
            }}
            QLineEdit {{
                background-color: transparent;
                color: {theme["fg"]};
                border: 1px solid {theme["input_border"]};
                border-radius: 6px;
                padding: 6px 30px;
                width: 50px;
            }}
            QLineEdit:focus {{
                border: 2px solid {theme["button_default"]};
                background-color: transparent;
            }}
            QLineEdit:hover {{
                background-color: transparent;
            }}
            QRadioButton {{
                color: {theme["fg"]};
                spacing: 8px;
            }}
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 6px;
                border: 2px solid {theme["input_border"]};
                background-color: transparent;
            }}
            QRadioButton::indicator:hover {{
                border: 2px solid {theme["button_default"]};
                background-color: {theme["group_bg"]};
            }}
            QRadioButton::indicator:checked {{
                border: 2px solid {theme["button_default"]};
                background-color: {theme["button_default"]};
            }}
            QRadioButton::indicator:checked:hover {{
                background-color: {theme["button_hover"]};
            }}
            QPushButton {{
                background-color: {theme["button_default"]};
                color: {theme["button_text"]};
                border: none;
                border-radius: 6px;
                padding: 10px 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme["button_hover"]};
            }}
            QListWidget {{
                background-color: {theme["input_bg"]};
                color: {theme["fg"]};
                font-size: 12px;
                border-radius: 5px;
                border: 1px solid {theme["border"]};
            }}
            QStatusBar {{
                background-color: {theme["group_bg"]};
                color: {theme["fg"]};
                border-top: 1px solid {theme["border"]};
            }}
            QProgressBar::chunk {{
                background-color: {theme["button_default"]};
                border-radius: 5px;
            }}

        /* MODERN SCROLLBAR STYLE */
        QScrollBar:vertical {{
            border: none;
            background: {theme["bg"]};
            width: 10px;
            margin: 0px 0px 0px 0px;
        }}
        QScrollBar::handle:vertical {{
            background: {theme["input_border"]};
            min-height: 20px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {theme["button_default"]};
        }}
        QScrollBar::add-line:vertical {{
            height: 0px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }}
        QScrollBar::sub-line:vertical {{
            height: 0px;
            subcontrol-position: top;
            subcontrol-origin: margin;
        }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}
        
        QScrollBar:horizontal {{
            border: none;
            background: {theme["bg"]};
            height: 10px;
            margin: 0px 0px 0px 0px;
        }}
        QScrollBar::handle:horizontal {{
            background: {theme["input_border"]};
            min-width: 20px;
            border-radius: 5px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {theme["button_default"]};
        }}
        QScrollBar::add-line:horizontal {{
            width: 0px;
            subcontrol-position: right;
            subcontrol-origin: margin;
        }}
        QScrollBar::sub-line:horizontal {{
            width: 0px;
            subcontrol-position: left;
            subcontrol-origin: margin;
        }}
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: none;
        }}
    """)

    def init_tabs(self):
        self.tab_create = QWidget()
        self.tabs.addTab(self.tab_create, QIcon(TAB_ICONS["crear"]), "Crear Proyecto")
        self.init_create_tab()
        self.tab_build = QWidget()
        self.tabs.addTab(self.tab_build, QIcon(TAB_ICONS["construir"]), "Construir Paquete")
        self.init_build_tab()
        self.tab_manager = QWidget()
        self.tabs.addTab(self.tab_manager, QIcon(TAB_ICONS["gestor"]), "Gestor de Proyectos")
        self.init_manager_tab()
        self.tab_about = QWidget()
        self.tabs.addTab(self.tab_about, QIcon(TAB_ICONS["about"]), "Acerca de")
        self.init_about_tab()
        self.statusBar().showMessage("Preparable!...")

        # Icono de ventana por defecto
        if os.path.exists(IPM_ICON_PATH):
            self.setWindowIcon(QIcon(IPM_ICON_PATH))

        # Instalar filtro de foco global estilo UWP
        self.focus_filter = FocusIndicationFilter(self)
        app = QApplication.instance()
        if app:
            app.installEventFilter(self.focus_filter)


    def init_create_tab(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        form_group = QGroupBox("Detalles del Proyecto")
        # Usamos un Layout con columnas definidas para "Label a izq, Input a derecha"
        form_layout = QGridLayout(form_group)
        form_layout.setSpacing(8)
        # Columna 0 (Labels): Ancho fijo o minimo para alineacion bonita
        form_layout.setColumnMinimumWidth(0, 140)
        # Columna 1 (Inputs): Stretch para que se peguen al borde
        form_layout.setColumnStretch(1, 1)

        # Fila 0: Empresa
        label1 = QLabel("Nombre de la Empresa:")
        label1.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        form_layout.addWidget(label1, 0, 0)
        self.input_empresa = QLineEdit()
        self.input_empresa.setPlaceholderText("Ejemplo: influent")
        self.input_empresa.setToolTip(LGDR_MAKE_MESSAGES["_LGDR_PUBLISHER_E"])
        # Eliminamos MaximumWidth para que ocupe todo el espacio
        self.input_empresa.setFixedHeight(35)
        self.input_empresa.setMaximumWidth(450)
        form_layout.addWidget(self.input_empresa, 0, 1)
        
        # Fila 1: Nombre logico
        label2 = QLabel("Nombre Interno (sin espacios):")
        label2.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        form_layout.addWidget(label2, 1, 0)
        self.input_nombre_logico = QLineEdit()
        self.input_nombre_logico.setPlaceholderText("Ejemplo: my-app")
        self.input_nombre_logico.setToolTip(LGDR_MAKE_MESSAGES["_LGDR_NAME_E"])
        self.input_nombre_logico.setFixedHeight(35)
        self.input_nombre_logico.setMaximumWidth(450)
        form_layout.addWidget(self.input_nombre_logico, 1, 1)
        
        # Fila 2: Nombre visual
        label3 = QLabel("Nombre Visual del Producto:")
        label3.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        form_layout.addWidget(label3, 2, 0)
        self.input_nombre_completo = QLineEdit()
        self.input_nombre_completo.setPlaceholderText("Ejemplo: My Super App")
        self.input_nombre_completo.setToolTip(LGDR_MAKE_MESSAGES["_LGDR_TITLE_E"])
        self.input_nombre_completo.setFixedHeight(35)
        self.input_nombre_completo.setMaximumWidth(450)
        form_layout.addWidget(self.input_nombre_completo, 2, 1)
        
        # Fila 3: Version
        label4 = QLabel("Versión Inicial:")
        label4.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        form_layout.addWidget(label4, 3, 0)
        self.input_version = QLineEdit()
        self.input_version.setPlaceholderText("Ejemplo: 1.0")
        self.input_version.setToolTip(LGDR_MAKE_MESSAGES["_LGDR_VERSION_E"])
        self.input_version.setFixedHeight(35)
        self.input_version.setMaximumWidth(450)
        form_layout.addWidget(self.input_version, 3, 1)

        # Fila 4: Autor
        label5 = QLabel("Autor (GitHub Username):")
        label5.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        form_layout.addWidget(label5, 4, 0)
        self.input_autor = QLineEdit()
        self.input_autor.setPlaceholderText("Ejemplo: JesusQuijada34")
        self.input_autor.setToolTip("Username de GitHub (obligatorio)")
        self.input_autor.setFixedHeight(35)
        self.input_autor.setMaximumWidth(450)
        form_layout.addWidget(self.input_autor, 4, 1)

        # Fila 5: Icono (distribuida igual)
        label_ico = QLabel("Icono del Proyecto:")
        label_ico.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        form_layout.addWidget(label_ico, 5, 0)
        
        ico_widget = QWidget()
        ico_widget.setMaximumWidth(450)
        ico_layout = QHBoxLayout(ico_widget)
        ico_layout.setContentsMargins(0, 0, 0, 0)
        ico_layout.setSpacing(5) # Espacio entre input y boton
        self.input_icon = QLineEdit()
        self.input_icon.setPlaceholderText("Ruta .ico local o URL de imagen (https://...)")
        self.input_icon.setFixedHeight(35)
        ico_layout.addWidget(self.input_icon)
        
        self.btn_browse_icon = QPushButton("Examinar")
        self.btn_browse_icon.setCursor(Qt.PointingHandCursor)
        self.btn_browse_icon.setFixedWidth(120)
        self.btn_browse_icon.setFixedHeight(35)
        self.btn_browse_icon.clicked.connect(self.browse_icon)
        # Estilo "mini" pero acorde al tema
        # self.btn_browse_icon.setStyleSheet(BTN_STYLES["info"] + "padding: 4px; font-size: 11px;")
        ico_layout.addWidget(self.btn_browse_icon)
        
        form_layout.addWidget(ico_widget, 5, 1)
        
        # Fila 6: Plataforma (Radios)
        label6 = QLabel("Plataforma Objetivo:")
        label6.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        # Margin top para alinear con el grupo de radios
        label6.setStyleSheet("margin-top: 5px;") 
        form_layout.addWidget(label6, 6, 0, Qt.AlignTop)

        
        self.platform_group = QButtonGroup()
        platform_layout = QHBoxLayout()
        platform_layout.setSpacing(12)
        platform_layout.setContentsMargins(0, 0, 0, 0)
        
        self.radio_windows = QRadioButton("Windows")
        self.radio_windows.setChecked(True)
        self.radio_windows.setMinimumHeight(40)  # No se achique más allá de 40 px al hacer resize
        self.radio_windows.setStyleSheet("""
            QRadioButton {
                padding: 6px 10px;
                border: 2px solid transparent;
                border-radius: 6px;
                background-color: transparent;
                min-height: 40px;  /* Garantiza altura mínima visual */
            }
            QRadioButton:hover {
                background-color: rgba(108, 249, 237, 0.1);
                border-color: rgba(108, 249, 230, 0.3);
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #d1d5da;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #6cf9e6;
                background-color: #6ceff9;
            }
        """)
        
        self.radio_linux = QRadioButton("Linux")
        self.radio_linux.setMinimumHeight(40)
        self.radio_linux.setStyleSheet("""
            QRadioButton {
                padding: 6px 10px;
                border: 2px solid transparent;
                border-radius: 6px;
                background-color: transparent;
                min-height: 40px;
            }
            QRadioButton:hover {
                background-color: rgba(249, 247, 108, 0.1);
                border-color: rgba(249, 235, 108, 0.3);
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #d1d5da;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #e4f96c;
                background-color: #f9f76c;
            }
        """)
        
        self.radio_multiplataforma = QRadioButton("Multiplataforma")
        self.radio_multiplataforma.setMinimumHeight(40)
        self.radio_multiplataforma.setStyleSheet("""
            QRadioButton {
                padding: 6px 10px;
                border: 2px solid transparent;
                border-radius: 6px;
                background-color: transparent;
                min-height: 40px;
            }
            QRadioButton:hover {
                background-color: rgba(108, 249, 108, 0.1);
                border-color: rgba(108, 249, 115, 0.3);
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #d1d5da;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #6cf978;
                background-color: #83f96c;
            }
        """)
        
        self.platform_group.addButton(self.radio_windows)
        self.platform_group.addButton(self.radio_linux)
        self.platform_group.addButton(self.radio_multiplataforma)
        platform_layout.addWidget(self.radio_windows)
        platform_layout.addWidget(self.radio_linux)
        platform_layout.addWidget(self.radio_multiplataforma)
        
        platform_widget = QWidget()
        platform_widget.setLayout(platform_layout)
        form_layout.addWidget(platform_widget, 6, 1)
        
        # Fila 7: Info
        info_label = QLabel("ℹ️ Un proyecto bien configurado garantiza una mejor distribución y compatibilidad.<br>Asegurese de que el Autor coincida con su usuario de GitHub para las actualizaciones.")
        info_label.setStyleSheet("color: #6a737d; font-size: 11px; padding: 10px 0px; border-top: 1px solid #eee; margin-top: 10px;")
        info_label.setWordWrap(True)
        form_layout.addWidget(info_label, 7, 0, 1, 2)
        
        self.btn_create = QPushButton("Crear Proyecto")
        self.btn_create.setFont(BUTTON_FONT)
        self.btn_create.setToolTip(LGDR_MAKE_MESSAGES["_LGDR_MAKE_BTN"])
        self.btn_create.setIcon(QIcon(TAB_ICONS["crear"]))
        self.btn_create.setMinimumHeight(45)
        self.btn_create.setMinimumWidth(300)
        # Boton centrado y ancho completo relativo al form
        self.btn_create.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_create.clicked.connect(self.create_package_action)
        
        # Progress Bar (Hidden by default)
        self.github_progress = QProgressBar()
        self.github_progress.setRange(0, 0) # Indeterminate
        self.github_progress.setTextVisible(False)
        self.github_progress.setFixedHeight(4)
        self.github_progress.setVisible(False)
        self.github_progress.setStyleSheet("QProgressBar { border: none; background: #e1e4e8; border-radius: 2px; } QProgressBar::chunk { background: #f96c6c; border-radius: 2px; }")
        
        # Status
        self.create_status = QLabel("")
        self.create_status.setAlignment(Qt.AlignCenter)

        layout.addWidget(form_group)
        layout.addWidget(self.btn_create)
        layout.addWidget(self.github_progress)
        layout.addWidget(self.create_status)
        layout.addStretch()
        self.tab_create.setLayout(layout)
        self.statusBar().showMessage("Preparando entorno...")

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
        self.btn_create.setEnabled(False)
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
        self.btn_create.setEnabled(True)
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
        full_name = f"{empresa}.{nombre_logico}.v{version}"
        hash_val = hashlib.sha256(full_name.encode()).hexdigest()
        rating = "Todas las edades"
        for keyword, rate in AGE_RATINGS.items():
            if keyword in nombre_logico.lower() or keyword in nombre_completo.lower():
                rating = rate
                break
        empresa = empresa.capitalize().replace("-", " ")
        root = ET.Element("app")
        ET.SubElement(root, "publisher").text = empresa
        ET.SubElement(root, "app").text = nombre_logico
        ET.SubElement(root, "name").text = nombre_completo
        ET.SubElement(root, "version").text = f"v{vso}"
        ET.SubElement(root, "correlationid").text = hash_val
        ET.SubElement(root, "rate").text = rating
        ET.SubElement(root, "author").text = autor
        ET.SubElement(root, "platform").text = plataforma_seleccionada
        tree = ET.ElementTree(root)
        tree.write(os.path.join(path, "details.xml"))
        self.statusBar().showMessage(f"Proyecto creado como {empresa}.{nombre_logico}.v{version}!")

    def init_build_tab(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        form_group = QGroupBox("Construir Paquete")
        form_layout = QGridLayout(form_group)
        form_layout.setSpacing(8)
        form_layout.setColumnMinimumWidth(0, 140)
        form_layout.setColumnStretch(1, 1)
        
        # Fila 0: Fabricante
        label1 = QLabel("Fabricante:")
        label1.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        form_layout.addWidget(label1, 0, 0)
        self.input_build_empresa = QLineEdit()
        self.input_build_empresa.setPlaceholderText("Ejemplo: influent")
        self.input_build_empresa.setMaximumWidth(450)
        self.input_build_empresa.setFixedHeight(35)
        form_layout.addWidget(self.input_build_empresa, 0, 1)

        # Fila 1: Nombre interno
        label2 = QLabel("Nombre interno:")
        label2.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        form_layout.addWidget(label2, 1, 0)
        self.input_build_nombre = QLineEdit()
        self.input_build_nombre.setPlaceholderText("Ejemplo: mycoolapp")
        self.input_build_nombre.setMaximumWidth(450)
        self.input_build_nombre.setFixedHeight(35)
        form_layout.addWidget(self.input_build_nombre, 1, 1)

        # Fila 2: Versión
        label3 = QLabel("Versión:")
        label3.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        form_layout.addWidget(label3, 2, 0)
        self.input_build_version = QLineEdit()
        self.input_build_version.setPlaceholderText("Ejemplo: 1.0")
        self.input_build_version.setMaximumWidth(450)
        self.input_build_version.setFixedHeight(35)
        form_layout.addWidget(self.input_build_version, 2, 1)

        # Fila 3: Plataforma (AUTOMATIZADO)
        label4 = QLabel("Entorno de compilación:")
        label4.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        form_layout.addWidget(label4, 3, 0)
        self.input_build_platform = QLineEdit()
        self.input_build_platform.setReadOnly(True)
        # Auto-detectar plataforma actual
        detected_plat = "Windows" if sys.platform.startswith("win") else "Linux"
        self.input_build_platform.setText(detected_plat)
        self.input_build_platform.setToolTip("Detectado automáticamente según el sistema operativo actual")
        self.input_build_platform.setMaximumWidth(450)
        self.input_build_platform.setFixedHeight(35)
        self.input_build_platform.setStyleSheet("background-color: rgba(128, 128, 128, 0.1); border-style: dashed;")
        form_layout.addWidget(self.input_build_platform, 3, 1)

        # Fila 4: Modo (Radios)
        label5 = QLabel("Modo:")
        label5.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        label5.setStyleSheet("margin-top: 5px;")
        form_layout.addWidget(label5, 4, 0, Qt.AlignTop)
        
        self.build_mode_group = QButtonGroup()
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(12)
        mode_layout.setContentsMargins(0,0,0,0)
        
        self.radio_portable = QRadioButton("Portable (All-in-one)")
        self.radio_portable.setChecked(True)
        self.radio_portable.setMinimumHeight(40)
        self.radio_lite = QRadioButton("Lite (Single File)") 
        self.radio_lite.setMinimumHeight(40)
        
        # Apply same style as create tab
        radio_style = """
            QRadioButton {
                padding: 6px 10px;
                border: 2px solid transparent;
                border-radius: 6px;
                background-color: transparent;
                min-height: 40px;
            }
            QRadioButton:hover {
                background-color: rgba(108, 249, 237, 0.1);
                border-color: rgba(108, 249, 230, 0.3);
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #d1d5da;
                border-radius: 9px;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #6cf9e6;
                background-color: #6ceff9;
            }
        """
        self.radio_portable.setStyleSheet(radio_style)
        self.radio_lite.setStyleSheet(radio_style)
        
        self.build_mode_group.addButton(self.radio_portable)
        self.build_mode_group.addButton(self.radio_lite)
        
        mode_layout.addWidget(self.radio_portable)
        mode_layout.addWidget(self.radio_lite)
        mode_widget = QWidget()
        mode_widget.setLayout(mode_layout)
        
        form_layout.addWidget(mode_widget, 4, 1)

        # Fila 5: Carpeta Custom
        label6 = QLabel("Carpeta Externa:")
        label6.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        form_layout.addWidget(label6, 5, 0)
        
        custom_widget = QWidget()
        custom_widget.setMaximumWidth(450)
        cw_layout = QHBoxLayout(custom_widget)
        cw_layout.setContentsMargins(0,0,0,0)
        cw_layout.setSpacing(5)
        
        self.input_custom_path = QLineEdit()
        self.input_custom_path.setPlaceholderText("(Opcional) Seleccionar carpeta externa a compilar")
        self.input_custom_path.setReadOnly(True)
        self.input_custom_path.setFixedHeight(35)
        cw_layout.addWidget(self.input_custom_path)
        
        self.btn_select_folder = QPushButton("...")
        self.btn_select_folder.setFixedWidth(40)
        self.btn_select_folder.setFixedHeight(35)
        self.btn_select_folder.clicked.connect(self.select_custom_folder)
        cw_layout.addWidget(self.btn_select_folder)
        
        form_layout.addWidget(custom_widget, 5, 1)

        self.btn_build = QPushButton("Construir paquete .iflapp")
        self.btn_build.setFont(BUTTON_FONT)
        self.btn_build.setIcon(QIcon(TAB_ICONS["construir"]))
        self.btn_build.setMaximumWidth(350)
        self.btn_build.clicked.connect(self.build_package_action)

        self.build_status = QLabel("")
        layout.addWidget(form_group)
        layout.addWidget(self.btn_build)
        layout.addWidget(self.build_status)
        layout.addStretch()
        self.tab_build.setLayout(layout)

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
        self.build_thread = BuildThread(empresa, nombre, version_full, platformLineEdit, parent=self, custom_path=custom_path, build_mode=build_mode)
        self.build_thread.progress.connect(lambda msg: self.build_status.setText(msg))
        self.build_thread.finished.connect(lambda msg: self.build_status.setText(msg))
        self.build_thread.error.connect(lambda msg: self.build_status.setText(f"❌ Error: {msg}"))
        self.build_thread.start()
        self.statusBar().showMessage(f"Iniciando compilación...")

    def init_manager_tab(self):
        layout = QVBoxLayout()
        splitter = QSplitter(Qt.Horizontal)
        proj_group = QGroupBox("Proyectos locales")
        proj_layout = QVBoxLayout(proj_group)
        self.projects_list = QListWidget()
        self.projects_list.setIconSize(QtCore.QSize(32, 32))
        self.projects_list.setAlternatingRowColors(False)
        self.projects_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.projects_list.setToolTip(LGDR_NAUFRAGIO_MESSAGES["_LGDR_LOCAL_LV"])
        # Ensure expandable policy
        self.projects_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        proj_layout.addWidget(self.projects_list)
        splitter.addWidget(proj_group)

        apps_group = QGroupBox("Apps instaladas")
        apps_layout = QVBoxLayout(apps_group)
        self.apps_list = QListWidget()
        self.apps_list.setIconSize(QtCore.QSize(32, 32))
        self.apps_list.setAlternatingRowColors(False)
        self.apps_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.apps_list.setToolTip(LGDR_NAUFRAGIO_MESSAGES["_LGDR_INSTALLED_LV"])
        # Ensure expandable policy
        self.apps_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        apps_layout.addWidget(self.apps_list)
        splitter.addWidget(apps_group)

        splitter.setSizes([1, 1])
        # Add splitter with Stretch Factor 1 to take all available vertical space
        layout.addWidget(splitter, 1)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.setContentsMargins(0, 5, 0, 0)
        
        # Obtener estilos github
        is_dark = detectar_modo_sistema()
        action_style, normal_style = get_github_style(is_dark)

        btn_refresh = QPushButton("Refrescar listas")
        # No establecemos font aquí porque el stylesheet lo maneja mejor para coherencia
        #btn_refresh.setFont(BUTTON_FONT) 
        btn_refresh.setStyleSheet(normal_style)
        btn_refresh.setIcon(QIcon(IPM_ICON_PATH))
        btn_refresh.setToolTip(LGDR_NAUFRAGIO_MESSAGES["_LGDR_REFRESH_BTN"])
        btn_refresh.setMinimumHeight(38)
        btn_refresh.clicked.connect(self.load_manager_lists)
        btn_row.addWidget(btn_refresh)

        btn_install = QPushButton("Instalar paquete")
        #btn_install.setFont(BUTTON_FONT)
        btn_install.setStyleSheet(normal_style) # Usamos normal en vez de "success" para mantener consistencia GW/BW requested
        btn_install.setIcon(QIcon(TAB_ICONS["instalar"]))
        btn_install.setToolTip(LGDR_NAUFRAGIO_MESSAGES["_LGDR_INSTALL_BTN"])
        btn_install.setMinimumHeight(38)
        btn_install.clicked.connect(self.install_package_action)
        btn_row.addWidget(btn_install)

        btn_uninstall = QPushButton("Desinstalar paquete")
        #btn_uninstall.setFont(BUTTON_FONT)
        btn_uninstall.setStyleSheet(normal_style) # Usamos normal en vez de "danger" para mantener consistencia GW/BW requested
        btn_uninstall.setIcon(QIcon(TAB_ICONS["desinstalar"]))
        btn_uninstall.setToolTip(LGDR_NAUFRAGIO_MESSAGES["_LGDR_UNINSTALL_BTN"])
        btn_uninstall.setMinimumHeight(38)
        btn_uninstall.clicked.connect(self.uninstall_package_action)
        btn_row.addWidget(btn_uninstall)
        layout.addLayout(btn_row)

        self.manager_status = QLabel("")
        self.manager_status.setWordWrap(True)
        self.manager_status.setToolTip("Estado de la app")
        layout.addWidget(self.manager_status)
        self.tab_manager.setLayout(layout)
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
        try:
            shutil.rmtree(pkg["folder"])
            self.manager_status.setText(f"🗑️ Desinstalado: {pkg['titulo']}")
        except Exception as e:
            self.manager_status.setText(f"❌ Error al desinstalar: {e}")
        self.load_manager_lists()

    def init_about_tab(self):
        # Creamos un widget contenedor y le ponemos el layout como antes
        container_widget = QWidget()
        layout = QVBoxLayout(container_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título principal
        title_label = QLabel("<h1 style='color: #f9826c;'>Influent Package Maker</h1>")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Subtítulo
        subtitle_label = QLabel("<h3>Suite Todo en Uno para Creación y Gestión de Paquetes</h3>")
        subtitle_label.setAlignment(QtCore.Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #8b949e; margin-bottom: 20px;")
        layout.addWidget(subtitle_label)
        
        # Descripción
        desc_text = (
            "<div style='font-size: 14px; line-height: 1.6; display: flex; gap:8px;'>"
            "<span style='vertical-align: middle;'>"
            "<svg width='24' height='24' style='vertical-align:middle;margin-right:4px;' viewBox='0 0 24 24' fill='none'><circle cx='12' cy='12' r='10' fill='#f9826c'/><text x='12' y='16' text-anchor='middle' font-size='13' fill='white' font-family='Segoe UI, Arial' font-weight='bold'>IPM</text></svg>"
            "</span>"
            "<span>"
            "Herramienta completa para crear, empaquetar, instalar y <b>gestionar proyectos Influent Fluthin Apps</b> "
            "<span style='color:#f9826c;'>(.iflapp)</span> con una interfaz moderna y fácil de usar. "
            "Diseñada para desarrolladores que buscan una solución todo-en-uno para el ciclo de vida completo de sus aplicaciones."
            "</span></div>"
        )
        desc_label = QLabel(desc_text)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Características principales
        features_text = (
            "<h3 style='color: #f9826c;'><svg width='22' height='22' style='vertical-align:middle;margin-right:5px;' viewBox='0 0 24 24' fill='none'><path d='M12 17.5l3.09 1.91a1 1 0 0 0 1.45-1.05l-.59-3.47 2.52-2.32a1 1 0 0 0-.55-1.72l-3.49-.32-1.45-3.21a1 1 0 0 0-1.82 0l-1.45 3.21-3.5.32a1 1 0 0 0-.55 1.72l2.53 2.32-.59 3.47A1 1 0 0 0 8.91 19.4L12 17.5z' fill='#f9826c'/><circle cx='12' cy='12' r='10' stroke='#f9826c' stroke-width='1.5' fill='none'/></svg>Características Principales</h3>"
            "<ul style='line-height: 2; padding-left: 12px;'>"
            "<li><svg width='16' height='16' style='vertical-align:middle;margin-right:4px;' viewBox='0 0 20 20'><rect x='2' y='4' width='16' height='12' rx='2' fill='#6de075'/></svg> <b>Creación de Proyectos:</b> Genera estructuras de proyectos completas con todas las carpetas necesarias <span style='color: #a371f7;'>(app, assets, config, docs, source, lib)</span></li>"
            "<li><svg width='16' height='16' style='vertical-align:middle;margin-right:4px;' viewBox='0 0 20 20'><circle cx='10' cy='10' r='8' fill='#24292e'/><path d='M10 10l3-3-3-3v6z' fill='#fff'/></svg> <b>Verificación de GitHub:</b> Valida automáticamente que el username de GitHub exista antes de crear el proyecto</li>"
            "<li><svg width='16' height='16' style='vertical-align:middle;margin-right:4px;' viewBox='0 0 20 20'><rect x='3' y='5' width='14' height='10' rx='2' fill='#58a6ff'/><rect x='7' y='9' width='6' height='2' rx='1' fill='#fff'/></svg> <b>Empaquetado:</b> Construye paquetes <span style='color:#f9826c;'>.iflapp</span> listos para distribución</li>"
            "<li><svg width='16' height='16' style='vertical-align:middle;margin-right:4px;' viewBox='0 0 20 20'><rect x='4' y='4' width='12' height='12' rx='3' fill='#ffcd38'/></svg> <b>Gestor de Proyectos:</b> Visualiza y gestiona todos tus proyectos locales e instalados desde una interfaz unificada</li>"
            "<li><svg width='16' height='16' style='vertical-align:middle;margin-right:4px;' viewBox='0 0 20 20'><path d='M4 8 L16 8 M4 12 L16 12' stroke='#f9826c' stroke-width='2'/></svg> <b>Instalación/Desinstalación:</b> Instala paquetes comprimidos o desinstala proyectos con un solo clic</li>"
            "<li><svg width='16' height='16' style='vertical-align:middle;margin-right:4px;' viewBox='0 0 20 20'><rect x='4' y='4' width='12' height='12' rx='3' fill='#a371f7'/><path d='M8 8h4v4H8z' fill='#fff'/></svg> <b>Ejecución de Scripts:</b> Ejecuta scripts Python directamente desde la interfaz</li>"
            "<li><svg width='16' height='16' style='vertical-align:middle;margin-right:4px;' viewBox='0 0 20 20'><circle cx='10' cy='10' r='8' fill='#24292e'/><text x='10' y='14' text-anchor='middle' font-size='9' fill='#fff' font-family='monospace'>SHA</text></svg> <b>Protección SHA256:</b> Cada proyecto incluye protección mediante hash SHA256</li>"
            "<li><svg width='16' height='16' style='vertical-align:middle;margin-right:4px;' viewBox='0 0 20 20'><rect x='4' y='9' width='10' height='4' rx='1' fill='#3fb950'/><rect x='8' y='5' width='4' height='4' rx='1' fill='#3fb950'/></svg> <b>Accesos Directos:</b> Crea accesos directos en Windows automáticamente</li>"
            "<li><svg width='16' height='16' style='vertical-align:middle;margin-right:4px;' viewBox='0 0 20 20'><rect x='4' y='4' width='12' height='12' rx='5' fill='#22272e'/><circle cx='10' cy='10' r='3' fill='#f9826c'/></svg> <b>Interfaz Moderna:</b> Tema oscuro con acentos naranjas, adaptable al modo del sistema</li>"
            "<li><svg width='16' height='16' style='vertical-align:middle;margin-right:4px;' viewBox='0 0 20 20'><rect x='2' y='8' width='4' height='4' rx='2' fill='#f9826c'/><rect x='8' y='2' width='4' height='4' rx='2' fill='#58a6ff'/><rect x='14' y='8' width='4' height='4' rx='2' fill='#3fb950'/></svg> <b>Multiplataforma:</b> Soporte para Windows, Linux y proyectos multiplataforma</li>"
            "</ul>"
        )
        features_label = QLabel(features_text)
        features_label.setWordWrap(True)
        layout.addWidget(features_label)
        
        # Información técnica
        tech_text = (
            "<h3 style='color: #f9826c;'><svg width='20' height='20' style='vertical-align:middle;margin-right:4px;' viewBox='0 0 20 20' fill='none'><rect x='3' y='3' width='14' height='14' rx='3' fill='#21262d'/><path d='M10 6v4l3 2' stroke='#f9826c' stroke-width='2' stroke-linecap='round'/></svg>Información Técnica</h3>"
            "<ul style='line-height: 2;'>"
            "<li><svg width='14' height='14' style='vertical-align:middle;margin-right:3px;' viewBox='0 0 20 20'><rect x='3' y='3' width='14' height='14' rx='3' fill='#a371f7'/></svg> <b>Framework:</b> PyQt5</li>"
            "<li><svg width='14' height='14' style='vertical-align:middle;margin-right:3px;' viewBox='0 0 20 20'><circle cx='10' cy='10' r='7' fill='#ffd33d'/></svg> <b>Lenguaje:</b> Python 3</li>"
            "<li><svg width='14' height='14' style='vertical-align:middle;margin-right:3px;' viewBox='0 0 20 20'><rect x='5' y='7' width='10' height='6' rx='2' fill='#58a6ff'/></svg> <b>Formato de Paquetes:</b> .iflapp (ZIP comprimido)</li>"
            "<li><svg width='14' height='14' style='vertical-align:middle;margin-right:3px;' viewBox='0 0 20 20'><circle cx='10' cy='10' r='6' fill='#3fb950'/></svg> <b>Estructura:</b> Basada en el sistema Influent OS</li>"
            "<li><svg width='14' height='14' style='vertical-align:middle;margin-right:3px;' viewBox='0 0 20 20'><rect x='4' y='10' width='12' height='3' rx='1' fill='#636e7b'/></svg> <b>Licencia:</b> GNU General Public License v3</li>"
            "</ul>"
        )
        tech_label = QLabel(tech_text)
        tech_label.setWordWrap(True)
        layout.addWidget(tech_label)
        
        # Información de contacto y enlaces
        contact_text = (
            "<h3 style='color: #f9826c;'><svg width='20' height='20' style='vertical-align:middle;margin-right:4px;' viewBox='0 0 20 20'><circle cx='10' cy='10' r='8' fill='#58a6ff'/><rect x='9' y='6' width='2' height='5' rx='1' fill='#fff'/><rect x='9' y='12' width='2' height='2' rx='1' fill='#fff'/></svg>Contacto y Enlaces</h3>"
            "<p style='line-height: 2;'>"
            "<b>Desarrollador Principal:</b><br>"
            "<svg width='14' height='14' style='vertical-align:middle;margin-right:3px;' viewBox='0 0 20 20'><circle cx='10' cy='8' r='4' fill='#f9826c'/><rect x='4' y='13' width='12' height='4' rx='2' fill='#8b949e'/></svg> <a href='https://t.me/JesusQuijada34/' style='color: #58a6ff; text-decoration: none;'>"
            "Jesus Quijada (@JesusQuijada34)</a><br><br>"
            "<b>Colaborador:</b><br>"
            "<svg width='14' height='14' style='vertical-align:middle;margin-right:3px;' viewBox='0 0 20 20'><rect x='3' y='3' width='14' height='14' rx='3' fill='#a371f7'/><text x='10' y='14' font-size='8' text-anchor='middle' fill='white'>C</text></svg> <a href='https://t.me/MkelCT/' style='color: #58a6ff; text-decoration: none;'>"
            "MkelCT18 (@MkelCT)</a><br><br>"
            "<b>Repositorio GitHub:</b><br>"
            "<svg width='14' height='14' style='vertical-align:middle;margin-right:3px;' viewBox='0 0 20 20'><circle cx='10' cy='10' r='8' fill='#22272e'/><path d='M7 10c-.6.6-1.6.6-1.6.6s0-1.2 1.6-1.6c.6-.2 1.2.2 1.2.2s.6-.4 1.2-.2c1.6.4 1.6 1.6 1.6 1.6s-1 .0-1.6-.6m-2 .6v1.6m8-1.6v1.6' stroke='#fff' stroke-width='.8' fill='none'/></svg> <a href='https://github.com/jesusquijada34/packagemaker/' "
            "style='color: #58a6ff; text-decoration: none;'>github.com/jesusquijada34/packagemaker</a><br><br>"
            "<b>Telegram:</b><br>"
            "<svg width='14' height='14' style='vertical-align:middle;margin-right:3px;' viewBox='0 0 20 20'><polygon points='2,10 18,2 16,18 10,14 6,16' fill='#58a6ff'/></svg> <a href='https://t.me/JesusQuijada34/' style='color: #58a6ff; text-decoration: none;'>"
            "t.me/JesusQuijada34</a><br>"
            "</p>"
        )
        contact_label = QLabel(contact_text)
        contact_label.setWordWrap(True)
        contact_label.setOpenExternalLinks(True)
        layout.addWidget(contact_label)
        
        # Versión y copyright
        version_text = (
            "<p style='text-align: center; color: #8b949e; margin-top: 30px; padding-top: 20px; "
            "border-top: 1px solid #30363d;'>"
            f"<svg width='15' height='15' style='vertical-align:middle;margin-right:4px;' viewBox='0 0 20 20'><rect x='2' y='5' width='16' height='10' rx='4' fill='#a371f7'/><rect x='7' y='7' width='6' height='6' rx='2' fill='#fff'/></svg> "
            f"Versión: {getversion()}<br>"
            "<svg width='13' height='13' style='vertical-align:middle;margin-right:3px;' viewBox='0 0 20 20'><rect x='2' y='14' width='16' height='4' rx='2' fill='#8b949e'/><rect x='8' y='2' width='4' height='10' rx='2' fill='#8b949e'/></svg> "
            "Copyright © 2025 Jesus Quijada<br>"
            "<svg width='15' height='15' style='vertical-align:middle;margin-right:3px;' viewBox='0 0 20 20'><path d='M6 7h8v6H6z' stroke='#f9826c' stroke-width='1.4' fill='none'/><rect x='4' y='4' width='12' height='12' rx='2' stroke='#f9826c' stroke-width='1.4' fill='none'/></svg> "
            "Bajo licencia GNU GPL v3"
            "<p>"
            "POWERED BY FLUTHIN ARMADILLO ENGINE (FLARM)"
            "</p>"
            "SERVER DEDICATED IN FLARM STORE"
            "</p>"
        )
        version_label = QLabel(version_text)
        version_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(version_label)
        
        layout.addStretch()
        
        # Hacemos desplazable el contenido con QScrollArea
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container_widget)
        scroll.setFrameStyle(0)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Aplicar estilo MacOSX-like si es posible (QSS)
        try:
            scroll.setStyleSheet("""
                QScrollArea {
                    border: none;
                    background: #f5f5f7;
                    border-radius: 8px;
                }
                QScrollBar:vertical, QScrollBar:horizontal {
                    background: transparent;
                    width: 10px;
                    margin: 2px;
                    border-radius: 6px;
                }
                QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #e2e8f9, stop:0.5 #bacef8, stop:1 #c8d0e7);
                    min-height: 36px;
                    min-width: 36px;
                    border-radius: 6px;
                    border: 1px solid #d3d6e4;
                    margin: 2px;
                }
                QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover,
                QScrollBar::handle:vertical:pressed, QScrollBar::handle:horizontal:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #b7d7fa, stop:1 #5caefb);
                    border: 1.1px solid #98c6fa;
                }
                QScrollBar::add-line, QScrollBar::sub-line {
                    background: none;
                    border: none;
                    height: 0px;
                    width: 0px;
                }
                QScrollBar::add-page, QScrollBar::sub-page {
                    background: none;
                }
                QScrollBar {
                    border-radius: 6px;
                    background: transparent;
                }
            """)
        except Exception:
            pass

        # Limpiamos el layout de la pestaña por si acaso
        if self.tab_about.layout() is not None:
            # Remove the old layout and widgets
            old_layout = self.tab_about.layout()
            while old_layout.count():
                item = old_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
            QtWidgets.QWidget().setLayout(old_layout)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        self.tab_about.setLayout(main_layout)

def main():
    app = QApplication(sys.argv)
    app.setFont(APP_FONT)
    w = PackageTodoGUI()
    w.show()
    if getattr(sys, 'frozen', False):
        try:
            pyi_splash.close()
        except ImportError:
            pass
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
