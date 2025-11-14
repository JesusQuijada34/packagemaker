# Compare remote store detail file, with the local xml for a search new release!
# Is wrote in this blame file:
import sys
import os
import requests
import zipfile
import shutil
import subprocess
import xml.etree.ElementTree as ET
import threading
import time
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QProgressBar
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QCoreApplication

XML_PATH = "details.xml"
CHECK_INTERVAL = 60
GITHUB_API = "https://api.github.com"

STYLE = """
QWidget {
    background-color: #f7f7fa;
    color: #222;
    font-family: -apple-system, BlinkMacSystemFont, "San Francisco", "Segoe UI", "Helvetica Neue", Arial;
    border-radius: 14px;
}
QLabel {
    color: #222;
    font-size: 16px;
    letter-spacing: 0.01em;
}
QPushButton {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6bb6ff, stop:1 #58e2bc);
    color: #fff;
    border-radius: 16px;
    padding: 10px 0;
    font-size: 17px;
    font-weight: 600;
    min-height: 40px;
    margin-top: 18px;
    margin-bottom: 8px;
    border: none;
    box-shadow: 0 1px 2px rgba(60,60,67,.06);
    transition: background 0.24s cubic-bezier(.4,0,.2,1);
    outline: none;
}
QPushButton:hover, QPushButton:focus {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4c9bee, stop:1 #45ce8c);
    color: #ffffff;
}
QPushButton:pressed {
    background: #f0f3f7;
    color: #222;
}
QProgressBar {
    border-radius: 11px;
    border: 1px solid #b8b8c6;
    background: #f6f7fa;
    min-height: 22px;
    font-size: 14px;
    color: #043d53;
}
QProgressBar::chunk {
    background-color: #6bb6ff;
    border-radius: 11px;
}
"""

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
    except Exception:
        return {}

def hay_conexion():
    try:
        requests.get(GITHUB_API, timeout=5)
        return True
    except Exception:
        return False

def buscar_release(author, app, version, platform):
    url = f"{GITHUB_API}/repos/{author}/{app}/releases/tags/{version}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        assets = r.json().get("assets", [])
        for a in assets:
            name = a.get("name", "")
            if name == f"{app}-{version}-{platform}.iflapp":
                return a.get("browser_download_url")
        return None
    except Exception:
        return None

class UpdaterWindow(QWidget):
    def __init__(self, appname, version, platform, url):
        super().__init__()
        self.app = appname
        self.version = version
        self.platform = platform
        self.url = url
        self.setWindowTitle("Actualizador IPM")
        # Establecer icono, si falla, no inicia
        try:
            icon_path = "app/updater-icon"
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
            elif getattr(sys, 'frozen', False):  # .exe
                exe_dir = os.path.dirname(sys.executable)
                alt_icon = os.path.join(exe_dir, "app", "updater-icon")
                if os.path.exists(alt_icon):
                    self.setWindowIcon(QIcon(alt_icon))
                else:
                    raise RuntimeError("icon not found")
            else:
                raise RuntimeError("icon not found")
        except Exception:
            # Si no puede el icono, no inicia
            QCoreApplication.quit()
            sys.exit(1)
        # macos/ios-like size and rounded widget
        self.setFixedSize(390, 320)
        self.setStyleSheet(STYLE)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(14)
        layout.setContentsMargins(30, 22, 30, 14)

        title = QLabel("Actualizador IPM")
        title.setFont(QFont("San Francisco", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        info = QLabel(f"<span style='font-size:17px;'><b>📦 {self.app}</b></span><br>"
                      f"<span style='font-size:15px;'>🔄 Nueva versión: <b>{self.version}</b></span><br>"
                      f"<span style='font-size:15px;'>🖥️ Plataforma: <b>{self.platform}</b></span>")
        info.setFont(QFont("San Francisco", 15))
        info.setAlignment(Qt.AlignCenter)
        info.setWordWrap(True)
        layout.addWidget(info)

        self.statusLabel = QLabel("")
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.statusLabel.setWordWrap(True)
        self.statusLabel.setFont(QFont("San Francisco", 13))
        layout.addWidget(self.statusLabel)
        
        self.progressBar = QProgressBar()
        self.progressBar.setValue(0)
        self.progressBar.setVisible(False)
        layout.addWidget(self.progressBar)

        btn = QPushButton("Actualizar ahora")
        btn.clicked.connect(self.instalar)
        layout.addWidget(btn)

        self.setLayout(layout)
        self.show()

    def instalar(self):
        destino = "update.iflapp"
        try:
            self.statusLabel.setText("⬇️ Descargando actualización…")
            QApplication.processEvents()
            with requests.get(self.url, stream=True) as r:
                r.raise_for_status()  # Abort on HTTP error
                total_length = int(r.headers.get('content-length', 0))
                dl = 0
                with open(destino, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            dl += len(chunk)
                            if total_length:
                                pct = int(dl * 100 / total_length)
                                self.progressBar.setValue(pct)
                                self.progressBar.setVisible(True)
                                QApplication.processEvents()
            self.statusLabel.setText("⏳ Instalando actualización…")
            self.progressBar.setVisible(True)
            QApplication.processEvents()
            # Descomprimir con progreso y reemplazar archivos
            with zipfile.ZipFile(destino, "r") as zip_ref:
                files = zip_ref.infolist()
                total = len(files)
                for i, info in enumerate(files, 1):
                    extract_path = info.filename
                    # Remover si existe y no es directorio ZIP - sobreescribir todo
                    if os.path.exists(extract_path):
                        if os.path.isfile(extract_path):
                            try:
                                os.remove(extract_path)
                            except Exception:
                                pass
                        elif os.path.isdir(extract_path) and not info.is_dir():
                            try:
                                shutil.rmtree(extract_path)
                            except Exception:
                                pass
                    zip_ref.extract(info, ".")
                    progress = int(i * 100 / total)
                    self.progressBar.setValue(progress)
                    self.statusLabel.setText(f"⏳ Actualizando… ({i}/{total})")
                    QApplication.processEvents()
            try:
                os.remove(destino)
            except Exception:
                pass
            self.statusLabel.setText("✅ Actualización realizada.")
            self.progressBar.setValue(100)
            QApplication.processEvents()
            # Lógica para reiniciar/ejecutar el app
            app_path = f"{self.app}.exe" if os.name == "nt" else f"./{self.app}"
            if not sys.argv[0].endswith(".py") and os.path.exists(app_path):
                subprocess.Popen([app_path])
            elif sys.argv[0].endswith(".py"):
                subprocess.Popen([sys.executable, os.path.abspath(__file__)])
            time.sleep(1.4)
            self.close()
        except Exception as e:
            self.statusLabel.setText("❌ Error durante la actualización.")
            self.progressBar.setVisible(False)
            QApplication.processEvents()
            time.sleep(1.7)
            self.close()

def verificar():
    while True:
        if not hay_conexion():
            time.sleep(30)
            continue
        datos = leer_xml(XML_PATH)
        if not datos:
            time.sleep(CHECK_INTERVAL)
            continue
        url = buscar_release(datos["author"], datos["app"], datos["version"], datos["platform"])
        if url:
            app = QApplication(sys.argv)
            ventana = UpdaterWindow(datos["app"], datos["version"], datos["platform"], url)
            app.exec_()
            return
        time.sleep(CHECK_INTERVAL)
threading.Thread(target=verificar, daemon=True).start()

if __name__ == "__main__":
    datos = leer_xml(XML_PATH)
    print(f"""searching for a fluthin package...\ngit::{datos["author"]}/{datos["app"]} {datos["version"]}/{datos["platform"]}\nhttps://github.com/{datos["author"]}/{datos["app"]}/""")
    verificar()
    while True:
        time.sleep(300)
