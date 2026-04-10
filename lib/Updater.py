import os
import sys
import time
import shutil
import zipfile
import traceback
import subprocess
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtGui import QFont, QIcon, QPixmap, QColor
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QObject

try:
    from leviathan_ui import WipeWindow, CustomTitleBar, LeviathanProgressBar
    HAS_LEVIATHAN = True
except ImportError:
    HAS_LEVIATHAN = False

class KillerLogic:
    @staticmethod
    def kill_target(target_name):
        print(f"Matando procesos de: {target_name}")
        try:
            if sys.platform == "win32":
                subprocess.call(f"taskkill /F /IM {target_name}.exe", shell=True)
                subprocess.call(f"taskkill /F /IM {target_name}", shell=True)
            else:
                subprocess.call(f"pkill -9 -f {target_name}", shell=True)
        except Exception as e:
            print(f"Kill error: {e}")

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
                    if not self._running:
                        return
                    f.write(chunk)
                    down += len(chunk)
                    if total:
                        self.progress.emit(int(down * 100 / total))

            self.status.emit("Descomprimiendo actualización...")
            if os.path.exists(ext_dir):
                shutil.rmtree(ext_dir)
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
                    if os.path.abspath(dst) == os.path.abspath(sys.argv[0]):
                        continue
                    if os.path.exists(dst):
                        try:
                            os.remove(dst)
                        except:
                            try:
                                os.rename(dst, dst + f".old.{int(time.time())}")
                            except:
                                continue
                    try:
                        shutil.move(src, dst)
                    except:
                        pass

            try:
                shutil.rmtree(ext_dir)
            except:
                pass
            try:
                os.remove(temp_zip)
            except:
                pass

            self.status.emit("Finalizando...")
            self.finished.emit(True, "OK")

        except Exception as e:
            traceback.print_exc()
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
        screen = QApplication.primaryScreen()
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
            exe = f"{self.app_data['app']}.exe"
            if os.path.exists(exe):
                subprocess.Popen(exe)
            QTimer.singleShot(1500, self.close)
        else:
            self.lbl_status.setText(f"Error: {msg}")
            self.lbl_status.setStyleSheet("color: #ff5252;")

