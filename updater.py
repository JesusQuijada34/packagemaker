import sys, os, time, shutil, zipfile, subprocess, traceback, threading
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtGui import QFont, QIcon, QPixmap, QColor, QGuiApplication
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QObject

# --- LEVIATHAN UI CHECK ---
try:
    from leviathan_ui import LeviathanDialog, WipeWindow, LeviathanProgressBar, CustomTitleBar, InmersiveSplash, InmojiTrx
    HAS_LEVIATHAN = True
except ImportError:
    HAS_LEVIATHAN = False

# --- IMPORTS ADICIONALES ---
import argparse
import tempfile
import re
from io import BytesIO

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

def _rXml(path):
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

def _rXml_r(author, app):
    url = f"https://raw.githubusercontent.com/{author}/{app}/main/details.xml"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return ET.fromstring(r.text).findtext("version", "").strip()
    except: pass
    return ""

def _fR(author, app, version, platform, publisher):
    filename = f"{publisher}.{app}.{version}-{platform}.iflapp"
    url = f"https://github.com/{author}/{app}/releases/download/{version}/{filename}"
    try:
        if requests.head(url, timeout=15, allow_redirects=True).status_code == 200:
            return url
    except: pass
    return None


def _fR_exe(author, app, version, platform, publisher):
    """Busca ejecutable setup con formato: Publisher.App-Version-Platform.exe"""
    # Formato largo de packagemaker: Publisher.App-Version-Platform.exe
    exe_patterns = [
        f"{publisher}.{app}-{version}-{platform}.exe",
        f"{publisher}.{app}.{version}-{platform}.exe",
        f"{publisher}-{app}-{version}-{platform}.exe",
        f"{app}-{version}-{platform}.exe",
        f"{publisher}.{app}-Setup-{version}.exe",
        f"{app}-Setup-{version}.exe",
        f"{publisher}.{app}-{version}.exe",
    ]
    
    for filename in exe_patterns:
        url = f"https://github.com/{author}/{app}/releases/download/{version}/{filename}"
        try:
            r = requests.head(url, timeout=15, allow_redirects=True)
            if r.status_code == 200:
                log(f"[EXE] Setup encontrado: {filename}")
                return url, filename
        except: pass
    
    return None, None


# --- CACHE EN MEMORIA ---
_memory_cache = {}

def cache_get(key):
    """Obtiene valor de caché en memoria."""
    return _memory_cache.get(key)

def cache_set(key, value):
    """Guarda valor en caché en memoria."""
    _memory_cache[key] = value

def cache_clear():
    """Limpia caché en memoria."""
    _memory_cache.clear()

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
        self.setWindowFlags(Qt.WindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint))
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(480, 320)
        if HAS_LEVIATHAN:
            WipeWindow.create().set_mode("ghostBlur").apply(self)
        self.init_ui()
        self.center()
        QTimer.singleShot(500, self.start_install)

    def center(self):
        screen = QGuiApplication.primaryScreen()
        if screen:
            self.move(screen.availableGeometry().center() - self.rect().center())

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

class IFLAPPInstallerWindow(QMainWindow):
    """Ventana para instalar archivos .iflapp en un contenedor."""
    
    finished = pyqtSignal(bool, str)
    
    def __init__(self, iflapp_path, target_dir=None, parent=None):
        super().__init__(parent)
        self.iflapp_path = iflapp_path
        self.target_dir = target_dir or os.path.join(os.getcwd(), "installed_app")
        self.setWindowFlags(Qt.WindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint))
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(480, 280)
        if HAS_LEVIATHAN:
            WipeWindow.create().set_mode("ghostBlur").apply(self)
        self.init_ui()
        self.center()
        QTimer.singleShot(500, self.start_installation)
    
    def center(self):
        screen = QGuiApplication.primaryScreen()
        if screen:
            self.move(screen.availableGeometry().center() - self.rect().center())
    
    def init_ui(self):
        central = QWidget()
        central.setObjectName("Central")
        central.setStyleSheet("QWidget#Central { background: rgba(18, 24, 34, 0.85); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; }")
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if HAS_LEVIATHAN:
            self.title_bar = CustomTitleBar(self, title="Instalador IFLAPP", is_main=True)
            self.title_bar.set_color(QColor(0,0,0,0))
            layout.addWidget(self.title_bar)
        
        content = QWidget()
        c_lay = QVBoxLayout(content)
        c_lay.setContentsMargins(30, 10, 30, 30)
        c_lay.setSpacing(15)
        
        self.icon_lbl = QLabel("📦")
        self.icon_lbl.setStyleSheet("font-size: 48px;")
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_lay.addWidget(self.icon_lbl)
        
        self.lbl_main = QLabel("Instalando paquete...")
        self.lbl_main.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_main.setStyleSheet("font-family: 'Segoe UI'; font-weight: 700; font-size: 18px; color: white;")
        c_lay.addWidget(self.lbl_main)
        
        self.lbl_status = QLabel(f"Destino: {self.target_dir}")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setStyleSheet("color: #aaa; font-size: 13px;")
        c_lay.addWidget(self.lbl_status)
        
        if HAS_LEVIATHAN:
            self.pbar = LeviathanProgressBar(self)
        else:
            self.pbar = QProgressBar()
            self.pbar.setStyleSheet("QProgressBar { background: #333; border: none; height: 6px; } QProgressBar::chunk { background: #2486ff; }")
            self.pbar.setTextVisible(False)
        self.pbar.setValue(0)
        c_lay.addWidget(self.pbar)
        
        layout.addWidget(content)
    
    def start_installation(self):
        """Inicia la instalación del archivo .iflapp."""
        self.thread = QThread()
        self.worker = IFLAPPInstallerWorker(self.iflapp_path, self.target_dir)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.pbar.setValue)
        self.worker.status.connect(self.lbl_status.setText)
        self.worker.finished.connect(self.on_finished)
        self.thread.start()
    
    def on_finished(self, ok, msg):
        self.thread.quit()
        if ok:
            self.lbl_status.setText("¡Instalación completada!")
            self.lbl_main.setText("Paquete instalado")
            self.icon_lbl.setText("✅")
            QTimer.singleShot(2000, self.close)
        else:
            self.lbl_status.setText(f"Error: {msg}")
            self.lbl_status.setStyleSheet("color: #ff5252;")
        self.finished.emit(ok, msg)


class IFLAPPInstallerWorker(QObject):
    """Worker para instalar archivos .iflapp en segundo plano."""
    
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    
    def __init__(self, iflapp_path, target_dir):
        super().__init__()
        self.iflapp_path = iflapp_path
        self.target_dir = target_dir
    
    def run(self):
        try:
            self.status.emit("Extrayendo paquete...")
            
            # Crear directorio destino si no existe
            os.makedirs(self.target_dir, exist_ok=True)
            
            # Extraer archivo .iflapp (zip)
            with zipfile.ZipFile(self.iflapp_path, 'r') as zf:
                files = zf.namelist()
                total = len(files)
                for i, file in enumerate(files):
                    zf.extract(file, self.target_dir)
                    self.progress.emit(int((i + 1) * 100 / total))
            
            self.status.emit("Configurando aplicación...")
            
            # Verificar details.xml
            details_path = os.path.join(self.target_dir, "details.xml")
            if os.path.exists(details_path):
                tree = ET.parse(details_path)
                root = tree.getroot()
                app_name = root.findtext("app", "Aplicación")
                self.status.emit(f"{app_name} instalado correctamente")
            
            self.progress.emit(100)
            self.finished.emit(True, "OK")
            
        except Exception as e:
            log(traceback.format_exc())
            self.finished.emit(False, str(e))


class LicenseTermsDialog(QMainWindow):
    """Diálogo de aceptación de términos de licencia."""
    
    accepted = pyqtSignal()
    rejected = pyqtSignal()
    
    def __init__(self, app_name="Aplicación", license_text=None, parent=None):
        super().__init__(parent)
        self.app_name = app_name
        self.setWindowFlags(Qt.WindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint))
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(600, 450)
        if HAS_LEVIATHAN:
            WipeWindow.create().set_mode("ghostBlur").apply(self)
        self.init_ui(license_text)
        self.center()
    
    def center(self):
        screen = QGuiApplication.primaryScreen()
        if screen:
            self.move(screen.availableGeometry().center() - self.rect().center())
    
    def init_ui(self, license_text):
        from PyQt6.QtWidgets import QTextEdit, QPushButton, QHBoxLayout, QCheckBox
        
        central = QWidget()
        central.setObjectName("Central")
        central.setStyleSheet("""
            QWidget#Central { 
                background: rgba(18, 24, 34, 0.95); 
                border: 1px solid rgba(255,255,255,0.1); 
                border-radius: 16px; 
            }
            QPushButton {
                background: #2486ff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover { background: #1a6fd4; }
            QPushButton:disabled { background: #555; color: #888; }
            QPushButton#rejectBtn {
                background: transparent;
                border: 1px solid rgba(255,255,255,0.2);
                color: #aaa;
            }
            QPushButton#rejectBtn:hover { 
                background: rgba(255,255,255,0.1); 
                color: white;
            }
            QTextEdit {
                background: rgba(0,0,0,0.3);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                color: #ddd;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                padding: 10px;
            }
            QCheckBox {
                color: #ddd;
                font-size: 13px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #2486ff;
            }
            QCheckBox::indicator:checked {
                background: #2486ff;
            }
        """)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if HAS_LEVIATHAN:
            self.title_bar = CustomTitleBar(self, title="Términos de Licencia", is_main=True)
            self.title_bar.set_color(QColor(0,0,0,0))
            layout.addWidget(self.title_bar)
        
        content = QWidget()
        c_lay = QVBoxLayout(content)
        c_lay.setContentsMargins(30, 20, 30, 30)
        c_lay.setSpacing(15)
        
        # Título
        lbl_title = QLabel(f"📜 Términos de Licencia - {self.app_name}")
        lbl_title.setStyleSheet("font-family: 'Segoe UI'; font-weight: 700; font-size: 16px; color: white;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_lay.addWidget(lbl_title)
        
        # Texto de licencia
        default_license = f"""Licencia de Uso de {self.app_name}

Al instalar o utilizar este software, usted acepta los siguientes términos:

1. CONCESIÓN DE LICENCIA
   Se otorga una licencia no exclusiva para usar este software.

2. RESTRICCIONES
   - No distribuir sin autorización
   - No realizar ingeniería inversa
   - No eliminar avisos de copyright

3. ACTUALIZACIONES
   Este software puede conectarse a servidores para verificar actualizaciones.

4. EXENCIÓN DE RESPONSABILIDAD
   El software se proporciona "tal cual" sin garantías.

5. PRIVACIDAD
   No se recolecta información personal sin consentimiento.

Para continuar con la instalación, debe aceptar estos términos."""
        
        self.txt_license = QTextEdit()
        self.txt_license.setReadOnly(True)
        self.txt_license.setText(license_text or default_license)
        self.txt_license.setMinimumHeight(200)
        c_lay.addWidget(self.txt_license)
        
        # Checkbox de aceptación
        self.chk_accept = QCheckBox("He leído y acepto los términos de licencia")
        self.chk_accept.stateChanged.connect(self.on_accept_changed)
        c_lay.addWidget(self.chk_accept)
        
        # Botones
        btn_layout = QHBoxLayout()
        
        self.btn_reject = QPushButton("Rechazar y Salir")
        self.btn_reject.setObjectName("rejectBtn")
        self.btn_reject.clicked.connect(self.on_reject)
        btn_layout.addWidget(self.btn_reject)
        
        btn_layout.addStretch()
        
        self.btn_accept = QPushButton("Aceptar y Continuar ✓")
        self.btn_accept.setEnabled(False)
        self.btn_accept.clicked.connect(self.on_accept)
        btn_layout.addWidget(self.btn_accept)
        
        c_lay.addLayout(btn_layout)
        layout.addWidget(content)
    
    def on_accept_changed(self, state):
        self.btn_accept.setEnabled(state == Qt.CheckState.Checked.value)
    
    def on_accept(self):
        self.accepted.emit()
        self.close()
    
    def on_reject(self):
        self.rejected.emit()
        self.close()


class EXEInstallerWorker(QObject):
    """Worker para descargar e instalar ejecutable setup."""
    
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    
    def __init__(self, url, filename, cache_in_memory=True):
        super().__init__()
        self.url = url
        self.filename = filename
        self.cache_in_memory = cache_in_memory
        self._running = True
        self.temp_exe_path = None
    
    def run(self):
        try:
            cache_key = f"exe_download_{self.url}"
            
            # Verificar caché en memoria
            if self.cache_in_memory:
                cached_data = cache_get(cache_key)
                if cached_data:
                    log("[CACHE] Usando ejecutable en caché de memoria")
                    self.status.emit("Usando caché de memoria...")
                    exe_data = cached_data
                else:
                    # Descargar a memoria
                    self.status.emit("Descargando instalador...")
                    r = requests.get(self.url, stream=True, timeout=60)
                    total = int(r.headers.get("content-length", 0))
                    
                    chunks = []
                    downloaded = 0
                    for chunk in r.iter_content(65536):  # 64KB chunks
                        if not self._running:
                            return
                        chunks.append(chunk)
                        downloaded += len(chunk)
                        if total:
                            self.progress.emit(int(downloaded * 50 / total))  # 0-50% descarga
                    
                    exe_data = b"".join(chunks)
                    cache_set(cache_key, exe_data)
                    log(f"[CACHE] Guardado en memoria: {len(exe_data)} bytes")
            else:
                # Descarga tradicional a archivo
                self.status.emit("Descargando instalador...")
                r = requests.get(self.url, stream=True, timeout=60)
                total = int(r.headers.get("content-length", 0))
                
                exe_data = BytesIO()
                downloaded = 0
                for chunk in r.iter_content(65536):
                    if not self._running:
                        return
                    exe_data.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        self.progress.emit(int(downloaded * 50 / total))
                exe_data = exe_data.getvalue()
            
            self.progress.emit(50)
            self.status.emit("Preparando instalación...")
            
            # Escribir a archivo temporal
            temp_dir = tempfile.gettempdir()
            self.temp_exe_path = os.path.join(temp_dir, self.filename)
            
            with open(self.temp_exe_path, "wb") as f:
                f.write(exe_data)
            
            log(f"[EXE] Guardado temporalmente: {self.temp_exe_path}")
            
            self.progress.emit(60)
            self.status.emit("Ejecutando instalador en modo silencioso...")
            
            # Ejecutar con --silent
            if sys.platform == "win32":
                # Windows: ejecutar con /SILENT o /VERYSILENT
                cmd = [self.temp_exe_path, "/SILENT", "/NORESTART", "/CLOSEAPPLICATIONS"]
            else:
                # Linux/Mac: ejecutar con --silent
                cmd = [self.temp_exe_path, "--silent"]
            
            # Ejecutar y esperar
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False
            )
            
            self.progress.emit(75)
            self.status.emit("Instalando... (esto puede tardar unos minutos)")
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self.progress.emit(100)
                self.status.emit("Instalación completada")
                log("[EXE] Instalación exitosa")
                self.finished.emit(True, "OK")
            else:
                error_msg = stderr.decode("utf-8", errors="ignore")[:200] if stderr else f"Código: {process.returncode}"
                log(f"[EXE] Error: {error_msg}")
                self.finished.emit(False, f"Error en instalador: {error_msg}")
            
            # Limpiar archivo temporal
            try:
                if self.temp_exe_path and os.path.exists(self.temp_exe_path):
                    os.remove(self.temp_exe_path)
                    log(f"[EXE] Temporal eliminado: {self.temp_exe_path}")
            except: pass
            
        except Exception as e:
            log(traceback.format_exc())
            self.finished.emit(False, str(e))


class EXEInstallerWindow(QMainWindow):
    """Ventana para instalar ejecutable setup descargado."""
    
    finished = pyqtSignal(bool, str)
    
    def __init__(self, url, filename, parent=None, cache_in_memory=True):
        super().__init__(parent)
        self.url = url
        self.filename = filename
        self.cache_in_memory = cache_in_memory
        self.setWindowFlags(Qt.WindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint))
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(480, 280)
        if HAS_LEVIATHAN:
            WipeWindow.create().set_mode("ghostBlur").apply(self)
        self.init_ui()
        self.center()
        QTimer.singleShot(500, self.start_installation)
    
    def center(self):
        screen = QGuiApplication.primaryScreen()
        if screen:
            self.move(screen.availableGeometry().center() - self.rect().center())
    
    def init_ui(self):
        central = QWidget()
        central.setObjectName("Central")
        central.setStyleSheet("QWidget#Central { background: rgba(18, 24, 34, 0.85); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; }")
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if HAS_LEVIATHAN:
            self.title_bar = CustomTitleBar(self, title="Instalador Setup", is_main=True)
            self.title_bar.set_color(QColor(0,0,0,0))
            layout.addWidget(self.title_bar)
        
        content = QWidget()
        c_lay = QVBoxLayout(content)
        c_lay.setContentsMargins(30, 10, 30, 30)
        c_lay.setSpacing(15)
        
        self.icon_lbl = QLabel("📥")
        self.icon_lbl.setStyleSheet("font-size: 48px;")
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_lay.addWidget(self.icon_lbl)
        
        self.lbl_main = QLabel("Instalando desde setup...")
        self.lbl_main.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_main.setStyleSheet("font-family: 'Segoe UI'; font-weight: 700; font-size: 18px; color: white;")
        c_lay.addWidget(self.lbl_main)
        
        self.lbl_status = QLabel(f"Archivo: {self.filename}")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setStyleSheet("color: #aaa; font-size: 13px;")
        c_lay.addWidget(self.lbl_status)
        
        if HAS_LEVIATHAN:
            self.pbar = LeviathanProgressBar(self)
        else:
            self.pbar = QProgressBar()
            self.pbar.setStyleSheet("QProgressBar { background: #333; border: none; height: 6px; } QProgressBar::chunk { background: #2486ff; }")
            self.pbar.setTextVisible(False)
        self.pbar.setValue(0)
        c_lay.addWidget(self.pbar)
        
        layout.addWidget(content)
    
    def start_installation(self):
        self.thread = QThread()
        self.worker = EXEInstallerWorker(self.url, self.filename, self.cache_in_memory)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.pbar.setValue)
        self.worker.status.connect(self.lbl_status.setText)
        self.worker.finished.connect(self.on_finished)
        self.thread.start()
    
    def on_finished(self, ok, msg):
        self.thread.quit()
        if ok:
            self.lbl_status.setText("¡Instalación completada!")
            self.lbl_main.setText("Setup instalado")
            self.icon_lbl.setText("✅")
            QTimer.singleShot(2000, self.close)
        else:
            self.lbl_status.setText(f"Error: {msg}")
            self.lbl_status.setStyleSheet("color: #ff5252;")
        self.finished.emit(ok, msg)


def install_iflapp(iflapp_path, target_dir=None, silent=False):
    """Instala un archivo .iflapp en el directorio especificado.
    
    Args:
        iflapp_path: Ruta al archivo .iflapp
        target_dir: Directorio destino (opcional)
        silent: Si True, no muestra interfaz gráfica
    
    Returns:
        tuple: (success: bool, message: str)
    """
    if not os.path.exists(iflapp_path):
        return False, f"Archivo no encontrado: {iflapp_path}"
    
    if silent:
        # Modo silencioso: sin interfaz
        worker = IFLAPPInstallerWorker(iflapp_path, target_dir or os.path.join(os.getcwd(), "installed_app"))
        
        # Ejecutar síncronamente
        try:
            worker.run()
            return True, "Instalación completada"
        except Exception as e:
            return False, str(e)
    else:
        # Modo GUI: mostrar ventana
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Mostrar splash
        splash = None
        if HAS_LEVIATHAN:
            try:
                splash = InmersiveSplash(
                    brand="IFLAPP Installer",
                    tagline="Instalando paquete...",
                    accent="#2486ff",
                    duration=1500
                )
                splash.show()
                QApplication.processEvents()
            except Exception as e:
                log(f"[Splash Error] {e}")
        
        window = IFLAPPInstallerWindow(iflapp_path, target_dir)
        
        if splash:
            splash.finish(window)
        
        window.show()
        
        if not QApplication.instance():
            sys.exit(app.exec())
        
        return True, "Ventana mostrada"


def update_app(silent=False, accept_license=False, cache_in_memory=True):
    """Verifica y realiza actualizaciones de la aplicación.
    
    Prioridad:
    1. Busca ejecutable setup (.exe) con formato de packagemaker
    2. Si no existe, usa paquete .iflapp como alternativa
    
    Args:
        silent: Si True, no muestra interfaz gráfica
        accept_license: Si True, acepta términos automáticamente (modo silent)
        cache_in_memory: Si True, usa caché en memoria para descargas
    
    Returns:
        bool: True si se actualizó correctamente
    """
    app_data = _rXml(XML_PATH)
    if not app_data:
        log("[ERROR] No se pudo leer details.xml")
        return False
    
    remote_version = _rXml_r(app_data["author"], app_data["app"])
    if not remote_version or remote_version == app_data["version"]:
        log(f"[INFO] Ya estás en la última versión: {app_data['version']}")
        return False
    
    log(f"[INFO] Actualización disponible: {app_data['version']} -> {remote_version}")
    
    # PRIORIDAD 1: Buscar ejecutable setup
    exe_url, exe_filename = _fR_exe(
        app_data["author"], 
        app_data["app"], 
        remote_version, 
        app_data["platform"], 
        app_data["publisher"]
    )
    
    if exe_url:
        log(f"[EXE] Setup encontrado: {exe_filename}")
        return _update_from_exe(app_data, exe_url, exe_filename, silent, accept_license, cache_in_memory)
    
    # PRIORIDAD 2: Buscar paquete .iflapp como alternativa
    log("[IFLAPP] Buscando paquete alternativo...")
    url = _fR(app_data["author"], app_data["app"], remote_version, app_data["platform"], app_data["publisher"])
    
    if not url:
        log("[ERROR] No se encontró ni .exe ni .iflapp")
        return False
    
    log(f"[IFLAPP] Usando paquete: {url}")
    return _update_from_iflapp(app_data, url, silent)


def _update_from_exe(app_data, exe_url, exe_filename, silent=False, accept_license=False, cache_in_memory=True):
    """Realiza actualización desde ejecutable setup."""
    app_name = app_data.get("app", "Aplicación")
    
    if silent:
        if not accept_license:
            log("[ERROR] Modo silencioso requiere --accept-license para setup .exe")
            return False
        
        log(f"[EXE] Iniciando instalación silenciosa de {exe_filename}...")
        # Modo silencioso sin GUI
        worker = EXEInstallerWorker(exe_url, exe_filename, cache_in_memory)
        try:
            worker.run()
            return True
        except Exception as e:
            log(f"[EXE ERROR] {e}")
            return False
    
    # Modo GUI: Mostrar splash -> Términos de licencia -> Instalador
    app = QApplication(sys.argv)
    
    # Mostrar splash inicial
    splash = None
    if HAS_LEVIATHAN:
        try:
            splash = InmersiveSplash(
                brand="System Updater",
                tagline=f"Actualización disponible para {app_name}",
                accent="#2486ff",
                icon_path=XML_PATH.replace("details.xml", "app/app-icon.ico") if os.path.exists(XML_PATH.replace("details.xml", "app/app-icon.ico")) else None,
                duration=1500
            )
            splash.show()
            QApplication.processEvents()
        except Exception as e:
            log(f"[Splash Error] {e}")
    
    # Cerrar splash y mostrar términos de licencia
    if splash:
        splash.close()
    
    # Mostrar diálogo de términos de licencia
    license_dialog = LicenseTermsDialog(app_name=app_name)
    license_result = {"accepted": False}
    
    def on_accept():
        license_result["accepted"] = True
    
    def on_reject():
        license_result["accepted"] = False
        app.quit()
    
    license_dialog.accepted.connect(on_accept)
    license_dialog.rejected.connect(on_reject)
    license_dialog.show()
    app.exec()
    
    if not license_result["accepted"]:
        log("[LICENSE] Términos rechazados. Cancelando actualización.")
        return False
    
    log("[LICENSE] Términos aceptados. Continuando instalación...")
    
    # Mostrar ventana de instalación del .exe
    install_window = EXEInstallerWindow(exe_url, exe_filename, cache_in_memory=cache_in_memory)
    install_window.show()
    app.exec()
    
    return True


def _update_from_iflapp(app_data, url, silent=False):
    """Realiza actualización desde paquete .iflapp (método alternativo)."""
    if silent:
        log(f"Actualizando a través de .iflapp...")
        app = QApplication(sys.argv)
        window = ModernUpdaterWindow(app_data, url)
        window.show()
        app.exec()
        return True
    else:
        app = QApplication(sys.argv)
        
        # Mostrar splash
        splash = None
        if HAS_LEVIATHAN:
            try:
                splash = InmersiveSplash(
                    brand="System Updater",
                    tagline=f"Actualizando {app_data['app']}...",
                    accent="#2486ff",
                    icon_path=XML_PATH.replace("details.xml", "app/app-icon.ico") if os.path.exists(XML_PATH.replace("details.xml", "app/app-icon.ico")) else None,
                    duration=2000
                )
                splash.show()
                QApplication.processEvents()
            except Exception as e:
                log(f"[Splash Error] {e}")
        
        window = ModernUpdaterWindow(app_data, url)
        
        if splash:
            splash.finish(window)
        
        window.show()
        app.exec()
        return True


def main():
    """Punto de entrada principal con soporte CLI."""
    parser = argparse.ArgumentParser(
        description="Updater e instalador para Influent Package Maker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  updater.py --check                    Verificar actualizaciones
  updater.py --silent --accept-license  Actualizar silenciosamente (acepta términos)
  updater.py --install app.iflapp     Instalar paquete .iflapp
  updater.py --install app.iflapp --target "C:/Apps/MiApp" --silent
  
Modos de actualización:
  1. Busca ejecutable setup (.exe) con formato packagemaker
  2. Si no existe, usa paquete .iflapp como alternativa
  3. Caché en memoria para descargas rápidas
        """
    )
    
    parser.add_argument("--check", action="store_true", help="Verificar si hay actualizaciones disponibles")
    parser.add_argument("--silent", action="store_true", help="Ejecutar sin interfaz gráfica")
    parser.add_argument("--accept-license", action="store_true", help="Aceptar términos de licencia automáticamente (requiere --silent)")
    parser.add_argument("--no-cache", action="store_true", help="Deshabilitar caché en memoria")
    parser.add_argument("--install", metavar="FILE", help="Instalar archivo .iflapp")
    parser.add_argument("--target", metavar="DIR", help="Directorio destino para instalación")
    parser.add_argument("--version", action="store_true", help="Mostrar versión del updater")
    
    args = parser.parse_args()
    
    if args.version:
        print("Influent Updater v2.1")
        print("Soporta: Actualizaciones OTA (EXE > IFLAPP), instalación .iflapp, caché en memoria")
        return
    
    if args.install:
        # Instalar archivo .iflapp
        success, msg = install_iflapp(args.install, args.target, args.silent)
        if args.silent:
            print(f"{'OK' if success else 'ERROR'}: {msg}")
        sys.exit(0 if success else 1)
    
    if args.check:
        # Solo verificar actualizaciones
        app_data = _rXml(XML_PATH)
        if not app_data:
            print("ERROR: No se pudo leer details.xml")
            sys.exit(1)
        
        remote = _rXml_r(app_data["author"], app_data["app"])
        if remote and remote != app_data["version"]:
            # Verificar si hay .exe disponible
            exe_url, exe_filename = _fR_exe(
                app_data["author"], app_data["app"], 
                remote, app_data["platform"], app_data["publisher"]
            )
            if exe_url:
                print(f"UPDATE_AVAILABLE: {app_data['version']} -> {remote}")
                print(f"TYPE: EXE_SETUP")
                print(f"FILENAME: {exe_filename}")
                print(f"DOWNLOAD_URL: {exe_url}")
                sys.exit(0)
            
            # Verificar .iflapp como alternativa
            url = _fR(app_data["author"], app_data["app"], remote, app_data["platform"], app_data["publisher"])
            if url:
                print(f"UPDATE_AVAILABLE: {app_data['version']} -> {remote}")
                print(f"TYPE: IFLAPP_PACKAGE")
                print(f"DOWNLOAD_URL: {url}")
                sys.exit(0)
        
        print("NO_UPDATE: Ya tienes la versión más reciente")
        sys.exit(0)
    
    # Verificar compatibilidad de argumentos
    if args.accept_license and not args.silent:
        print("ERROR: --accept-license requiere --silent")
        sys.exit(1)
    
    # Modo updater automático (sin argumentos específicos) o --silent
    if args.silent:
        # Modo silencioso
        success = update_app(
            silent=True, 
            accept_license=args.accept_license,
            cache_in_memory=not args.no_cache
        )
        sys.exit(0 if success else 1)
    else:
        # Modo GUI interactivo
        success = update_app(
            silent=False,
            accept_license=False,
            cache_in_memory=not args.no_cache
        )
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()