import sys, os, requests, zipfile, shutil, subprocess, xml.etree.ElementTree as ET
import threading, time, traceback
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

REMOTE_XML = "https://raw.githubusercontent.com/JesusQuijada34/packagemaker/main/details.xml"
LOCAL_XML = "details.xml"
CHECK_INTERVAL = 60  # segundos
LOG_PATH = "updater_log.txt"

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
QPushButton#source {
    background-color: #3c3f44;
    color: #2ecc71;
}
QPushButton#source:hover {
    background-color: #4b4f55;
}
"""

def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {msg}\n")
    print(f"{timestamp} {msg}")

class UpdaterWindow(QWidget):
    def __init__(self, version, plataforma):
        super().__init__()
        self.version = version
        self.plataforma = plataforma
        self.release_url = f"https://github.com/JesusQuijada34/packagemaker/releases/download/{version}/packagemaker-{version}-{plataforma}.zip"
        self.source_url = f"https://github.com/JesusQuijada34/packagemaker/archive/refs/tags/{version}.zip"
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Packagemaker Updater")
        self.setFixedSize(460, 240)
        self.setStyleSheet(QSS_STYLE)

        layout = QVBoxLayout()

        title = QLabel("Packagemaker Updater")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        info = QLabel(f"🧩 Versión actual: {leer_version(LOCAL_XML)}\n🚀 Nueva versión: {self.version}\n🖥️ Plataforma: {self.plataforma}")
        info.setFont(QFont("Segoe UI", 12))
        layout.addWidget(info)

        btns = QHBoxLayout()
        binario_btn = QPushButton("Actualizar binario")
        source_btn = QPushButton("Descargar source-code")
        source_btn.setObjectName("source")
        binario_btn.clicked.connect(self.instalar_binario)
        source_btn.clicked.connect(self.descargar_source)
        btns.addWidget(binario_btn)
        btns.addWidget(source_btn)
        layout.addLayout(btns)

        self.setLayout(layout)
        self.show()

    def instalar_binario(self):
        destino = "update.zip"
        try:
            log("Iniciando respaldo embestido…")
            if not os.path.exists("backup_embestido"):
                os.mkdir("backup_embestido")
            for f in os.listdir("."):
                if f not in ["backup_embestido", destino] and os.path.isfile(f):
                    shutil.copy2(f, f"backup_embestido/{f}")
            log("Respaldo completado.")

            log(f"Descargando release desde {self.release_url}")
            r = requests.get(self.release_url, stream=True)
            with open(destino, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            log("Descarga completada.")

            with zipfile.ZipFile(destino, "r") as zip_ref:
                zip_ref.extractall(".")
            os.remove(destino)
            log("Archivos reemplazados.")

            if not sys.argv[0].endswith(".py"):
                ejecutable = "packagemaker.exe" if os.name == "nt" else "./packagemaker"
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

    def descargar_source(self):
        log(f"Abriendo source-code: {self.source_url}")
        subprocess.Popen(["start", self.source_url], shell=True)
        self.close()

def leer_version(path):
    try:
        tree = ET.parse(path)
        return tree.getroot().findtext("version", "").strip()
    except Exception as e:
        log(f"Error leyendo versión local: {e}")
        return ""

def leer_version_remota():
    try:
        r = requests.get(REMOTE_XML, timeout=10)
        root = ET.fromstring(r.text)
        return root.findtext("version", "").strip()
    except Exception as e:
        log(f"Error leyendo versión remota: {e}")
        return ""

def verificar_release(version, plataforma):
    url = f"https://github.com/JesusQuijada34/packagemaker/releases/download/{version}/packagemaker-{version}-{plataforma}.zip"
    try:
        r = requests.head(url, timeout=5)
        log(f"Verificando release: {url} → {r.status_code}")
        return r.status_code == 200
    except Exception as e:
        log(f"Error verificando release: {e}")
        return False

def ciclo_silencioso():
    def verificar():
        while True:
            try:
                local = leer_version(LOCAL_XML)
                remoto = leer_version_remota()
                log(f"Versión local: {local} | Versión remota: {remoto}")
                if remoto and remoto != local:
                    for plataforma in ["knosthalij", "danenone"]:
                        if verificar_release(remoto, plataforma):
                            log(f"Actualización disponible para {plataforma}")
                            app = QApplication(sys.argv)
                            ventana = UpdaterWindow(remoto, plataforma)
                            app.exec_()
                            return
                else:
                    log("No hay actualizaciones.")
            except Exception as e:
                log(f"Error en ciclo de verificación: {e}")
                log(traceback.format_exc())
            time.sleep(CHECK_INTERVAL)
    threading.Thread(target=verificar, daemon=True).start()

if __name__ == "__main__":
    log("Packagemaker Updater iniciado en modo silencioso.")
    ciclo_silencioso()
    while True:
        time.sleep(3600)
