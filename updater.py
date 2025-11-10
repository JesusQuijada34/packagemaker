import sys, os, requests, zipfile, shutil, subprocess, xml.etree.ElementTree as ET
import threading, time, traceback
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QLineEdit
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

XML_PATH = "details.xml"
CHECK_INTERVAL = 60
LOG_PATH = "updater_log.txt"
PLATFORMS = ["alpha", "knosthalij", "danenone"]

QSS_STYLE = """
QWidget {
    background-color: #0d1117;
    color: #2ecc71;
    font-family: "Segoe UI";
}
QPushButton {
    background-color: #2ecc71;
    color: white;
    border-radius: 6px;
    padding: 6px 12px;
}
QPushButton:hover {
    background-color: #27ae60;
}
QLineEdit {
    background-color: #1c1f26;
    color: #2ecc71;
    border: 1px solid #2ecc71;
    border-radius: 4px;
    padding: 4px;
}
"""

def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {msg}\n")
    print(f"{timestamp} {msg}")

def leer_app_y_version(path):
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        app = root.findtext("app", "").strip()
        version = root.findtext("version", "").strip()
        author = root.findtext("author", "")
        return app, version, author
    except Exception as e:
        log(f"Error leyendo XML: {e}")
        return "", ""

def verificar_release(username, app, version, platform):
    base = f"https://github.com/{username}/{app}/releases/download/{version}"
    urls = [
        f"{base}/{app}-{version}-{platform}.iflapp",
        f"{base}/{app}-{version}-{platform}.iflappb"
    ]
    for url in urls:
        try:
            r = requests.head(url, timeout=5)
            log(f"Verificando release: {url} → {r.status_code}")
            if r.status_code == 200:
                return True, url
        except Exception as e:
            log(f"Error verificando release: {e}")
    return False, ""

class UsernamePrompt(QWidget):
    def __init__(self, app, version):
        super().__init__()
        self.app = app
        self.version = version
        self.setWindowTitle("GitHub Username")
        self.setFixedSize(400, 180)
        self.setStyleSheet(QSS_STYLE)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("🔍 Repositorio no encontrado")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        info = QLabel(f"App: {self.app}\nVersión: {self.version}")
        info.setFont(QFont("Segoe UI", 11))
        layout.addWidget(info)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Ingresa tu GitHub username")
        layout.addWidget(self.username_input)

        btn = QPushButton("Buscar")
        btn.clicked.connect(self.buscar_release)
        layout.addWidget(btn)

        self.setLayout(layout)
        self.show()

    def buscar_release(self):
        username = self.username_input.text().strip()
        for platform in PLATFORMS:
            ok, url = verificar_release(username, self.app, self.version, platform)
            if ok:
                self.close()
                ventana = UpdaterWindow(username, self.app, self.version, platform, url)
                ventana.show()
                return
        log("❌ Release no encontrado con ese username.")
        self.username_input.setText("")

class UpdaterWindow(QWidget):
    def __init__(self, username, app, version, platform, url):
        super().__init__()
        self.username = username
        self.app = app
        self.version = version
        self.platform = platform
        self.url = url
        self.setWindowTitle("Actualizador IPM")
        self.setFixedSize(460, 240)
        self.setStyleSheet(QSS_STYLE)
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
            log("Iniciando respaldo embestido…")
            if not os.path.exists("backup_embestido"):
                os.mkdir("backup_embestido")
            for f in os.listdir("."):
                if f not in ["backup_embestido", destino] and os.path.isfile(f):
                    shutil.copy2(f, f"backup_embestido/{f}")
            log("Respaldo completado.")

            log(f"Descargando release desde {self.url}")
            r = requests.get(self.url, stream=True)
            with open(destino, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            log("Descarga completada.")

            with zipfile.ZipFile(destino, "r") as zip_ref:
                zip_ref.extractall(".")
            os.remove(destino)
            log("Archivos reemplazados.")

            if not sys.argv[0].endswith(".py"):
                ejecutable = f"{self.app}.exe" if os.name == "nt" else f"./{self.app}"
                if os.path.exists(ejecutable):
                    log(f"Ejecutando binario: {ejecutable}")
                    subprocess.Popen(ejecutable)
            else:
                log("Reiniciando script embestido…")
                subprocess.Popen([sys.executable, __file__])
            self.close()
        except Exception as e:
            log(f"❌ Error durante instalación: {e}")
            log(traceback.format_exc())
            self.close()

def ciclo_verificacion():
    def verificar():
        while True:
            app, version, author = leer_app_y_version(XML_PATH)
            if not app or not version or not author:
                log("❌ No se pudo leer app/version del XML.")
                time.sleep(CHECK_INTERVAL)
                continue

            log(f"App: {app} | Versión: {version}")
            default_user = root.findtext("author")
            for platform in PLATFORMS:
                ok, url = verificar_release(default_user, app, version, platform)
                if ok:
                    log(f"✅ Actualización encontrada para {platform}.")
                    app_qt = QApplication(sys.argv)
                    ventana = UpdaterWindow(default_user, app, version, platform, url)
                    app_qt.exec_()
                    return
            log("❌ Repositorio no encontrado. Solicitando username.")
            app_qt = QApplication(sys.argv)
            prompt = UsernamePrompt(app, version)
            app_qt.exec_()
            return
            time.sleep(CHECK_INTERVAL)
    threading.Thread(target=verificar, daemon=True).start()

if __name__ == "__main__":
    log("Actualizador IPM iniciado en modo silencioso.")
    ciclo_verificacion()
    while True:
        time.sleep(3600)
