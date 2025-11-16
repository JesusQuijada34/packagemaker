import sys, os, requests, shutil, subprocess, xml.etree.ElementTree as ET
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
            "author": root.findtext("author", "").strip()
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

def buscar_release(author, app, version, platform):
    url = f"{GITHUB_API}/repos/{author}/{app}/releases/tags/{version}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            log(f"❌ Release {version} no encontrado en {author}/{app}")
            return None
        assets = r.json().get("assets", [])
        target = f"{app}-{version}-{platform}.iflapp"
        for a in assets:
            if a.get("name") == target:
                return a.get("browser_download_url")
        log("❌ Asset no encontrado en release.")
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

            log(f"📖 App: {datos['app']} | Versión local: {datos['version']} | Plataforma: {datos['platform']}")
            remoto = leer_xml_remoto(datos["author"], datos["app"])
            if remoto and remoto != datos["version"]:
                log(f"🔄 Nueva versión remota: {remoto}")
                url = buscar_release(datos["author"], datos["app"], remoto, datos["platform"])
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
        time.sleep(3600)
