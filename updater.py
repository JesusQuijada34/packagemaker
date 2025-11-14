import sys, os, requests, shutil, subprocess, xml.etree.ElementTree as ET
import threading, time, traceback
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

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

class UpdaterWindow(QWidget):
    def __init__(self, app, version, platform, url):
        super().__init__()
        self.app = app
        self.version = version
        self.platform = platform
        self.url = url
        self.setWindowTitle("Actualizador IPM")
        self.setFixedSize(460, 240)
        self.setStyleSheet(STYLE)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("Actualizador IPM")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        info = QLabel(f"📦 {self.app}\n🔄 Nueva versión: {self.version}\n🖥️ Plataforma: {self.platform}")
        info.setFont(QFont("Segoe UI", 12))
        layout.addWidget(info)

        btn = QPushButton("Actualizar ahora")
        btn.clicked.connect(self.instalar)
        layout.addWidget(btn)

        self.setLayout(layout)
        self.show()

    def instalar(self):
        destino = "update.zip"
        try:
            log("🔐 Respaldando archivos…")
            if not os.path.exists("backup_embestido"):
                os.mkdir("backup_embestido")
            for f in os.listdir("."):
                if f not in ["backup_embestido", destino] and os.path.isfile(f):
                    shutil.copy2(f, f"backup_embestido/{f}")
            log("✅ Respaldo completado.")

            log(f"⬇️ Descargando desde {self.url}")
            r = requests.get(self.url, stream=True)
            with open(destino, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)

            shutil.unpack_archive(destino, ".")
            os.remove(destino)
            log("✅ Archivos actualizados.")

            if not sys.argv[0].endswith(".py"):
                exe = f"{self.app}.exe" if os.name == "nt" else f"./{self.app}"
                if os.path.exists(exe):
                    log(f"🚀 Ejecutando {exe}")
                    subprocess.Popen(exe)
            else:
                log("🔁 Reiniciando script embestido…")
                subprocess.Popen([sys.executable, __file__])
            self.close()
        except Exception as e:
            log(f"❌ Error durante instalación: {e}")
            log(traceback.format_exc())
            self.close()

def ciclo_embestido():
    def verificar():
        while True:
            if not hay_conexion():
                log("🌐 Sin conexión. Esperando…")
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