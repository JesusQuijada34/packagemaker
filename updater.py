#!/usr/bin/env python3
"""
Packagemaker updater rewritten using PyQt5.

Features:
- Frameless, animated window (fade in/out).
- Background thread that checks remote details.xml periodically.
- Download worker with progress reporting and extraction.
- Notification and Auto-update switches (QCheckBox) and callbacks.
- Safe backup before replacing files.

Dependencies: PyQt5, requests, Pillow (optional for icons).
"""
import os
import sys
import time
import zipfile
import shutil
import requests
import subprocess
import platform
import xml.etree.ElementTree as ET
from functools import partial

from PyQt5 import QtCore, QtGui, QtWidgets

REMOTE_XML = "https://raw.githubusercontent.com/JesusQuijada34/packagemaker/main/details.xml"
LOCAL_XML = "details.xml"


class UpdateChecker(QtCore.QThread):
    update_found = QtCore.pyqtSignal(str, str)  # version, platform
    status = QtCore.pyqtSignal(str)
    error = QtCore.pyqtSignal(str)

    def __init__(self, interval=180, parent=None):
        super().__init__(parent)
        self.interval = interval
        self._stopped = False

    def stop(self):
        self._stopped = True

    def run(self):
        # First quick check, then periodic
        while not self._stopped:
            try:
                self.status.emit("Comprobando actualizaciones...")
                local = leer_version(LOCAL_XML)
                remote = leer_version_remota()
                if remote and remote != local:
                    # try candidate platform names
                    for plat in detect_platform_names():
                        if self._stopped:
                            return
                        url = f"https://github.com/JesusQuijada34/packagemaker/releases/download/{remote}/packagemaker-{remote}-{plat}.zip"
                        try:
                            r = requests.head(url, timeout=6)
                            if r.status_code == 200:
                                self.update_found.emit(remote, plat)
                                return
                        except Exception:
                            pass
                # nothing found
                self.status.emit("Sin actualizaciones")
            except Exception as e:
                self.error.emit(str(e))
            # wait interval with small sleeps to allow stop
            waited = 0
            while waited < self.interval and not self._stopped:
                time.sleep(1)
                waited += 1


class DownloadWorker(QtCore.QThread):
    progress = QtCore.pyqtSignal(int)  # percent
    status = QtCore.pyqtSignal(str)
    finished_ok = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(str)

    def __init__(self, url, parent=None):
        super().__init__(parent)
        self.url = url
        self._stopped = False

    def run(self):
        destino = "update.zip"
        backup_dir = "backup_embestido"
        try:
            # create backup
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir, exist_ok=True)
            for f in os.listdir("."):
                if f in (backup_dir, destino):
                    continue
                if os.path.isfile(f):
                    shutil.copy2(f, os.path.join(backup_dir, f))

            self.status.emit("Descargando actualización...")
            resp = requests.get(self.url, stream=True, timeout=20)
            total = int(resp.headers.get("content-length", 0))
            downloaded = 0
            chunk_size = 8192
            with open(destino, "wb") as fh:
                for chunk in resp.iter_content(chunk_size=chunk_size):
                    if self._stopped:
                        return
                    if not chunk:
                        continue
                    fh.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = int(downloaded * 100 / total)
                        self.progress.emit(pct)

            self.status.emit("Instalando actualización...")
            # extract
            with zipfile.ZipFile(destino, "r") as z:
                z.extractall(".")
            try:
                os.remove(destino)
            except Exception:
                pass

            # optionally launch new executable
            if not sys.argv[0].endswith(".py"):
                executable = "packagemaker.exe" if os.name == "nt" else "./packagemaker"
                if os.path.exists(executable):
                    try:
                        subprocess.Popen([executable], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    except Exception:
                        pass

            self.finished_ok.emit()
        except Exception as e:
            # attempt restore backup best-effort
            try:
                for f in os.listdir(backup_dir):
                    src = os.path.join(backup_dir, f)
                    if os.path.isfile(src):
                        shutil.copy2(src, f)
            except Exception:
                pass
            self.error.emit(str(e))


def detect_platform_names():
    sysplat = platform.system().lower()
    names = []
    if "windows" in sysplat:
        names += ["windows-x64", "windows"]
    elif "linux" in sysplat:
        names += ["linux-x64", "linux"]
    elif "darwin" in sysplat or "mac" in sysplat:
        names += ["macos-x64", "macos"]
    names += ["knosthalij", "danenone"]
    out = []
    seen = set()
    for n in names:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def leer_version(path):
    try:
        if not os.path.exists(path):
            return ""
        tree = ET.parse(path)
        return tree.getroot().findtext("version", "")
    except Exception:
        return ""


def leer_version_remota():
    try:
        r = requests.get(REMOTE_XML, timeout=10)
        if r.status_code != 200:
            return ""
        root = ET.fromstring(r.text)
        return root.findtext("version", "")
    except Exception:
        return ""


class UpdaterWindow(QtWidgets.QWidget):
    # Callbacks the host app can set
    on_update_available = None  # func(version, platform)
    on_install_started = None  # func()
    on_install_finished = None  # func(success: bool)

    def __init__(self):
        super().__init__(None, QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowTitle("Packagemaker Updater")
        self.resize(480, 280)

        # UI elements
        self.main = QtWidgets.QFrame(self)
        self.main.setObjectName("main")
        self.main.setStyleSheet("#main{background:#071216;border-radius:10px;color:#dfeee6}")
        self.main.setGeometry(0, 0, 480, 280)

        # title bar
        self.title_label = QtWidgets.QLabel("Packagemaker Updater", self.main)
        self.title_label.setStyleSheet("color:#7ef5a1; font-weight:bold; font-size:14px")
        self.title_label.move(12, 10)

        self.close_btn = QtWidgets.QPushButton("✕", self.main)
        self.close_btn.setStyleSheet("background:transparent;color:#d0d0d0;border:none;font-size:14px")
        self.close_btn.setGeometry(440, 8, 32, 24)
        self.close_btn.clicked.connect(self.close_and_stop)

        # status / detail
        self.status_label = QtWidgets.QLabel("Iniciando verificación...", self.main)
        self.status_label.setWordWrap(True)
        self.status_label.setGeometry(12, 48, 456, 40)
        self.status_label.setStyleSheet("color:#9fe6b9;font-size:13px")

        self.detail_label = QtWidgets.QLabel("", self.main)
        self.detail_label.setWordWrap(True)
        self.detail_label.setGeometry(12, 96, 456, 40)
        self.detail_label.setStyleSheet("color:#bcded2;font-size:12px")

        # progress
        self.progress = QtWidgets.QProgressBar(self.main)
        self.progress.setGeometry(12, 150, 456, 18)
        self.progress.setValue(0)

        # switches (notification & auto-update)
        self.notify_cb = QtWidgets.QCheckBox("Notificarme", self.main)
        self.notify_cb.setGeometry(12, 175, 120, 22)
        self.notify_cb.setChecked(True)
        self.notify_cb.stateChanged.connect(self._on_notify_changed)

        self.auto_cb = QtWidgets.QCheckBox("Descarga automática", self.main)
        self.auto_cb.setGeometry(140, 175, 160, 22)
        self.auto_cb.setChecked(False)
        self.auto_cb.stateChanged.connect(self._on_auto_changed)

        # buttons
        self.install_btn = QtWidgets.QPushButton("Instalar", self.main)
        self.install_btn.setGeometry(340, 200, 120, 36)
        self.install_btn.setEnabled(False)
        self.install_btn.clicked.connect(self.install_clicked)

        self.later_btn = QtWidgets.QPushButton("Ahora no", self.main)
        self.later_btn.setGeometry(200, 200, 120, 36)
        self.later_btn.clicked.connect(self.close_and_stop)

        # animation for opacity
        self.anim = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(300)

        # state
        self.release_url = None
        self.checker = UpdateChecker(interval=180)
        self.checker.update_found.connect(self._on_update_found)
        self.checker.status.connect(self._set_status)
        self.checker.error.connect(self._set_error)
        self.checker.start()

        # position bottom-right
        QtCore.QTimer.singleShot(50, self.place_bottom_right)
        QtCore.QTimer.singleShot(100, self.fade_in)

        # for dragging
        self._drag_pos = None

    # Dragging handling
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() & QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def place_bottom_right(self):
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        w = self.width()
        h = self.height()
        x = screen.width() - w - 20
        y = screen.height() - h - 40
        self.move(x, y)

    def fade_in(self):
        self.setWindowOpacity(0.0)
        self.show()
        self.anim.stop()
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.start()

    def fade_out_and_close(self):
        self.anim.stop()
        self.anim.setStartValue(self.windowOpacity())
        self.anim.setEndValue(0.0)
        self.anim.finished.connect(self.close)
        self.anim.start()

    def close_and_stop(self):
        try:
            self.checker.stop()
        except Exception:
            pass
        self.fade_out_and_close()

    # UpdateChecker callbacks
    def _on_update_found(self, version, plataforma):
        self.status_label.setText(f"Actualización disponible: {version} ({plataforma})")
        local_v = leer_version(LOCAL_XML) or "desconocida"
        self.detail_label.setText(f"Versión instalada: {local_v}\nVersión remota: {version}\nPlataforma: {plataforma}")
        self.release_url = f"https://github.com/JesusQuijada34/packagemaker/releases/download/{version}/packagemaker-{version}-{plataforma}.zip"
        self.install_btn.setEnabled(True)
        # callback for host
        try:
            if callable(self.on_update_available):
                self.on_update_available(version, plataforma)
        except Exception:
            pass
        # if auto-update enabled, start download
        if self.auto_cb.isChecked():
            self.install_clicked()

    def _set_status(self, text):
        self.status_label.setText(text)

    def _set_error(self, text):
        self.status_label.setText(f"Error: {text}")

    # switches callbacks
    def _on_notify_changed(self, state):
        # this can be used to enable/disable system notifications in the host app
        # Expose a callback or simply store the value
        self.notify_enabled = bool(state)

    def _on_auto_changed(self, state):
        self.auto_enabled = bool(state)

    def install_clicked(self):
        if not self.release_url:
            self.status_label.setText("URL de release no encontrada")
            return
        self.install_btn.setEnabled(False)
        # callback
        try:
            if callable(self.on_install_started):
                self.on_install_started()
        except Exception:
            pass

        self.dl_worker = DownloadWorker(self.release_url)
        self.dl_worker.progress.connect(self._on_download_progress)
        self.dl_worker.status.connect(self._set_status)
        self.dl_worker.finished_ok.connect(self._on_install_success)
        self.dl_worker.error.connect(self._on_install_error)
        self.dl_worker.start()

    def _on_download_progress(self, pct):
        self.progress.setValue(pct)

    def _on_install_success(self):
        self.status_label.setText("Actualización instalada correctamente.")
        try:
            if callable(self.on_install_finished):
                self.on_install_finished(True)
        except Exception:
            pass
        QtCore.QTimer.singleShot(1500, self.close_and_stop)

    def _on_install_error(self, msg):
        self.status_label.setText(f"Error instalando: {msg}")
        try:
            if callable(self.on_install_finished):
                self.on_install_finished(False)
        except Exception:
            pass
        self.install_btn.setEnabled(True)


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = UpdaterWindow()

    # Example of registering callbacks
    def cb_update_available(v, p):
        print(f"Update available: {v} for {p}")

    def cb_install_started():
        print("Install started")

    def cb_install_finished(success):
        print("Install finished", success)

    w.on_update_available = cb_update_available
    w.on_install_started = cb_install_started
    w.on_install_finished = cb_install_finished

    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
import customtkinter as ctk
import tkinter as tk
import threading
import time
import requests
import os
import zipfile
import shutil
import sys
import subprocess
import xml.etree.ElementTree as ET
from PIL import Image, ImageTk
import platform
from functools import partial

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

REMOTE_XML = "https://raw.githubusercontent.com/JesusQuijada34/packagemaker/main/details.xml"
LOCAL_XML = "details.xml"
SOUND_PATH = "assets/afterdelay.wav"
CLOSE_ICON_PATH = "assets/close-btn.png"

# Try to import winsound only on Windows; otherwise set to None
try:
    if os.name == "nt":
        import winsound  # type: ignore
    else:
        winsound = None
except Exception:
    winsound = None


class PackagemakerUpdater(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Packagemaker Updater")
        self.geometry("460x260")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color="#0b1220")
        self.alpha = 0.0
        self.attributes("-alpha", self.alpha)

        self.stop_event = threading.Event()
        self.check_thread = None

        # fonts
        roboto_path = os.path.join(os.getcwd(), "Roboto-Regular.ttf")
        self.roboto = ctk.CTkFont(family="Roboto", size=13) if os.path.exists(roboto_path) else ctk.CTkFont(family="Segoe UI", size=13)

        # Title bar frame (for drag and close)
        self.title_bar = tk.Frame(self, bg="#07101a", height=48)
        self.title_bar.pack(fill="x", side="top")
        self.title_bar.bind("<ButtonPress-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.on_move)

        # Close button (image optional)
        if os.path.exists(CLOSE_ICON_PATH):
            try:
                img = Image.open(CLOSE_ICON_PATH).resize((20, 20))
                self.close_icon = ImageTk.PhotoImage(img)
                self.close_btn = tk.Button(self.title_bar, image=self.close_icon, bd=0, bg="#07101a", activebackground="#07101a", command=self.close_and_stop)
            except Exception:
                self.close_btn = tk.Button(self.title_bar, text="✕", bd=0, bg="#07101a", fg="#d0d0d0", command=self.close_and_stop)
        else:
            self.close_btn = tk.Button(self.title_bar, text="✕", bd=0, bg="#07101a", fg="#d0d0d0", command=self.close_and_stop)
        self.close_btn.pack(side="right", padx=8, pady=8)

        # Title label
        self.title_label = ctk.CTkLabel(self.title_bar, text="Packagemaker Updater", font=ctk.CTkFont(size=14, weight="bold"), text_color="#7ef5a1", fg_color="#07101a")
        self.title_label.pack(side="left", padx=12)

        # Main content
        self.container = ctk.CTkFrame(self, fg_color="#09131a", corner_radius=10)
        self.container.pack(fill="both", expand=True, padx=12, pady=(8,12))

        self.status_label = ctk.CTkLabel(self.container, text="Iniciando verificación...", font=self.roboto, text_color="#9fe6b9", wraplength=400, justify="left")
        self.status_label.pack(anchor="w", padx=12, pady=(12,2))

        self.detail_label = ctk.CTkLabel(self.container, text="", font=ctk.CTkFont(size=12), text_color="#bcded2", wraplength=420, justify="left")
        self.detail_label.pack(anchor="w", padx=12, pady=(0,8))

        # Progress bar and percentage
        self.progress = ctk.CTkProgressBar(self.container, width=420)
        self.progress.set(0.0)
        self.progress.pack(padx=12, pady=(6,4))
        self.progress_label = ctk.CTkLabel(self.container, text="", font=self.roboto, text_color="#bcded2")
        self.progress_label.pack(anchor="e", padx=12)

        # Buttons
        btn_frame = ctk.CTkFrame(self.container, fg_color="#09131a", corner_radius=0)
        btn_frame.pack(fill="x", pady=(8,6), padx=8)

        self.install_btn = ctk.CTkButton(btn_frame, text="Instalar", command=self.install_clicked, fg_color="#2ecc71", text_color="white", width=120)
        self.later_btn = ctk.CTkButton(btn_frame, text="Ahora no", command=self.close_and_stop, fg_color="#3c3f44", text_color="#2ecc71", width=120)
        self.install_btn.pack(side="right", padx=(6,12), pady=6)
        self.later_btn.pack(side="right", padx=(6,0), pady=6)
        self.install_btn.configure(state="disabled")  # enabled only when update available

        # place on bottom-right with small slide-in animation
        self.update_idletasks()
        self.place_bottom_right()
        self.slide_in()

        # animated checking dots
        self.dots = 0
        self.animating_check = True
        self.animate_check_label()

        # sound
        self.play_sound_delayed()

        # start background check
        self.after(500, self.start_periodic_check)

    # window movement helpers
    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def on_move(self, event):
        x = self.winfo_pointerx() - self._x
        y = self.winfo_pointery() - self._y
        self.geometry(f"+{x}+{y}")

    def place_bottom_right(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{sw - w - 20}+{sh - h - 40}")

    def slide_in(self):
        # simple fade + alpha increase
        def step():
            if self.alpha < 1.0:
                self.alpha += 0.08
                self.attributes("-alpha", min(self.alpha, 1.0))
                self.after(20, step)
            else:
                self.attributes("-alpha", 1.0)
        step()

    def fade_out_and_hide(self, callback=None):
        def step():
            if self.alpha > 0.0:
                self.alpha -= 0.08
                self.attributes("-alpha", max(self.alpha, 0.0))
                self.after(20, step)
            else:
                self.withdraw()
                if callback:
                    callback()
        step()

    def close_and_stop(self):
        # stop background thread gracefully then destroy
        self.stop_event.set()
        self.fade_out_and_hide(callback=self.destroy)

    def play_sound_delayed(self, delay_ms=200):
        if winsound and os.path.exists(SOUND_PATH):
            # play asynchronously after a tiny delay
            self.after(delay_ms, lambda: winsound.PlaySound(SOUND_PATH, winsound.SND_FILENAME | winsound.SND_ASYNC))

    def animate_check_label(self):
        if self.animating_check:
            self.dots = (self.dots + 1) % 4
            dots_str = "." * self.dots
            self.status_label.configure(text=f"Comprobando actualizaciones{dots_str}")
            self.after(600, self.animate_check_label)

    def start_periodic_check(self, interval=180):
        # interval in seconds; default 3 minutes (180)
        if self.check_thread and self.check_thread.is_alive():
            return
        self.stop_event.clear()
        self.check_thread = threading.Thread(target=self._check_loop, args=(interval,), daemon=True)
        self.check_thread.start()

    def _check_loop(self, interval):
        # fast first check then wait interval
        while not self.stop_event.is_set():
            try:
                local = leer_version(LOCAL_XML)
                remote = leer_version_remota()
                if remote and remote != local:
                    # decide platform options to try
                    candidate_platforms = self.detect_platform_names()
                    for plataforma in candidate_platforms:
                        if self.stop_event.is_set():
                            return
                        existe = self.verify_release(remote, plataforma)
                        if existe:
                            # update UI with found release
                            self.after(0, partial(self.show_update, remote, plataforma))
                            # stop loop and keep UI for user action
                            return
                # nothing new
                self.after(0, lambda: self.status_label.configure(text="Sin actualizaciones" if remote else "No se pudo comprobar la versión remota"))
            except Exception as e:
                self.after(0, lambda: self.status_label.configure(text=f"Error comprobando: {e}"))
            # wait with cancellation
            for _ in range(int(interval)):
                if self.stop_event.is_set():
                    return
                time.sleep(1)

    def detect_platform_names(self):
        # ajusta la lista de nombres que uses en tus releases
        sysplat = platform.system().lower()
        arch = platform.machine().lower()
        names = []
        if "windows" in sysplat:
            names.append("windows-x64")
            names.append("windows")
        elif "linux" in sysplat:
            names.append("linux-x64")
            names.append("linux")
        elif "darwin" in sysplat or "mac" in sysplat:
            names.append("macos-x64")
            names.append("macos")
        # fallback / previously used names
        names.extend(["knosthalij", "danenone"])
        # dedupe while preserving order
        seen = set()
        out = []
        for n in names:
            if n not in seen:
                seen.add(n)
                out.append(n)
        return out

    def show_update(self, version, plataforma):
        self.animating_check = False
        self.status_label.configure(text=f"Actualización disponible: {version} ({plataforma})")
        local_v = leer_version(LOCAL_XML) or "desconocida"
        self.detail_label.configure(text=f"Versión instalada: {local_v}\nVersión remota: {version}\nPlataforma: {plataforma}")
        self.release_url = f"https://github.com/JesusQuijada34/packagemaker/releases/download/{version}/packagemaker-{version}-{plataforma}.zip"
        self.install_btn.configure(state="normal")
        # keep window visible and focused with a gentle pop
        self.deiconify()
        self.slide_in()

    def verify_release(self, version, plataforma):
        base = "https://github.com/JesusQuijada34/packagemaker/releases/download"
        nombre = f"packagemaker-{version}-{plataforma}.zip"
        url = f"{base}/{version}/{nombre}"
        try:
            r = requests.head(url, timeout=6)
            return r.status_code == 200
        except Exception:
            return False

    def install_clicked(self):
        # launch download/install in background
        self.install_btn.configure(state="disabled")
        threading.Thread(target=self._download_and_install, daemon=True).start()

    def _download_and_install(self):
        url = getattr(self, "release_url", None)
        if not url:
            self.after(0, lambda: self.status_label.configure(text="URL de release no encontrada"))
            self.install_btn.configure(state="normal")
            return

        destino = "update.zip"
        backup_dir = "backup_embestido"
        try:
            # create backup
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir, exist_ok=True)
            for f in os.listdir("."):
                if f in (backup_dir, destino):
                    continue
                if os.path.isfile(f):
                    shutil.copy2(f, os.path.join(backup_dir, f))

            # download with progress
            self.after(0, lambda: self.status_label.configure(text="Descargando actualización..."))
            resp = requests.get(url, stream=True, timeout=20)
            total = int(resp.headers.get("content-length", 0))
            downloaded = 0
            chunk_size = 8192
            with open(destino, "wb") as fh:
                for chunk in resp.iter_content(chunk_size=chunk_size):
                    if not chunk:
                        continue
                    fh.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = downloaded / total
                        self.after(0, lambda p=pct: self.progress.set(p))
                        self.after(0, lambda p=pct: self.progress_label.configure(text=f"{int(p*100)}%"))
            # extract
            self.after(0, lambda: self.status_label.configure(text="Instalando actualización..."))
            with zipfile.ZipFile(destino, "r") as z:
                z.extractall(".")
            os.remove(destino)

            # try to launch new binary if present and not running as a script
            if not sys.argv[0].endswith(".py"):
                executable = "packagemaker.exe" if os.name == "nt" else "./packagemaker"
                if os.path.exists(executable):
                    try:
                        subprocess.Popen([executable], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    except Exception:
                        pass

            self.after(0, lambda: self.status_label.configure(text="Actualización instalada correctamente."))
            self.after(2000, self.close_and_stop)
        except Exception as e:
            self.after(0, lambda: self.status_label.configure(text=f"Error instalando: {e}"))
            # restore backup if failure happens (best-effort)
            try:
                for f in os.listdir(backup_dir):
                    src = os.path.join(backup_dir, f)
                    if os.path.isfile(src):
                        shutil.copy2(src, f)
            except Exception:
                pass
            self.after(0, lambda: self.install_btn.configure(state="normal"))


# helper functions
def leer_version(path):
    try:
        if not os.path.exists(path):
            return ""
        tree = ET.parse(path)
        return tree.getroot().findtext("version", "")
    except Exception:
        return ""


def leer_version_remota():
    try:
        r = requests.get(REMOTE_XML, timeout=10)
        if r.status_code != 200:
            return ""
        root = ET.fromstring(r.text)
        return root.findtext("version", "")
    except Exception:
        return ""


if __name__ == "__main__":
    app = PackagemakerUpdater()
    app.mainloop()
