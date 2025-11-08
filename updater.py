import os
import sys
import io
import zipfile
import shutil
import subprocess
import platform
import xml.etree.ElementTree as ET
import threading
import time

# --------- PyQt5 Import/Installer ---------
def ensure_pyqt5():
    try:
        from PyQt5 import QtWidgets, QtGui, QtCore
        return QtWidgets, QtGui, QtCore
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "PyQt5"])
        from PyQt5 import QtWidgets, QtGui, QtCore
        return QtWidgets, QtGui, QtCore

QtWidgets, QtGui, QtCore = ensure_pyqt5()

# --------- Chromium OS Styled Notification ---------
def chromium_notification_qt(msg, title="Packagemaker", duration=6000, icon_path=None, with_buttons=False):
    qss_chrome = """
QWidget#notifBG {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 #fff, stop:1 #eaeaeaff);
    border: 1.5px solid #dadce0;
    border-radius: 15px;
    color: #212121;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 14.2px;
}
QLabel#titleLabel {
    font-size: 16.8px;
    font-weight: bold;
    color: #424242;
    margin-bottom: 4px;
}
QLabel#iconLabel {
    qproperty-alignment: AlignVCenter | AlignLeft;
}
QPushButton {
    min-width: 82px;
    min-height: 28px;
    border-radius: 8px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #eaf1fb, stop:1 #dbeafe);
    border: 1.2px solid #adbde3;
    color: #2150a1;
    font-weight: 500;
    padding: 3px 9px;
    transition: background 0.2s, color 0.2s;
}
QPushButton:hover {
    background: #d1e4fa;
    color: #174378;
    border: 1.2px solid #568ef9;
}
QPushButton:pressed {
    background: #b7cdf6;
    color: #13436d;
}
"""

    class ChromeOSNotification(QtWidgets.QWidget):
        def __init__(self, title, msg, icon_path=None, timeout=6000, parent=None, with_buttons=False):
            super().__init__(parent)
            self.setObjectName("notifBG")
            self.setWindowFlags(
                QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            self.setStyleSheet(qss_chrome)

            main_layout = QtWidgets.QHBoxLayout(self)
            main_layout.setContentsMargins(20, 17, 20, 17)
            icon_label = QtWidgets.QLabel()
            icon_label.setObjectName("iconLabel")
            if icon_path and os.path.isfile(icon_path):
                pixmap = QtGui.QPixmap(icon_path)
                icon_label.setPixmap(
                    pixmap.scaled(42, 42, QtCore.Qt.KeepAspectRatio,
                                  QtCore.Qt.SmoothTransformation))
            else:
                pm = QtGui.QPixmap(42, 42)
                pm.fill(QtCore.Qt.transparent)
                painter = QtGui.QPainter(pm)
                painter.setRenderHint(QtGui.QPainter.Antialiasing)
                painter.setBrush(QtGui.QBrush(QtGui.QColor("#c8dafc")))
                painter.setPen(QtCore.Qt.NoPen)
                painter.drawEllipse(0, 0, 42, 42)
                painter.end()
                icon_label.setPixmap(pm)
            main_layout.addWidget(icon_label)

            content_vbox = QtWidgets.QVBoxLayout()
            lbl_title = QtWidgets.QLabel(title)
            lbl_title.setObjectName("titleLabel")
            content_vbox.addWidget(lbl_title)
            lbl_msg = QtWidgets.QLabel(msg)
            lbl_msg.setWordWrap(True)
            lbl_msg.setStyleSheet("margin-bottom:5px; margin-top:2px;")
            content_vbox.addWidget(lbl_msg)

            if with_buttons:
                btn_hbox = QtWidgets.QHBoxLayout()
                btn_ok = QtWidgets.QPushButton("Aceptar")
                btn_ok.setCursor(QtCore.Qt.PointingHandCursor)
                btn_ok.clicked.connect(self.close)
                btn_hbox.addStretch(1)
                btn_hbox.addWidget(btn_ok)
                btn_hbox.addStretch(1)
                content_vbox.addLayout(btn_hbox)

            main_layout.addLayout(content_vbox)

            self.adjustSize()

            screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
            x = screen.right() - self.width() - 36
            y = screen.bottom() - self.height() - 44
            self.move(x, y)

            QtCore.QTimer.singleShot(timeout, self.close)

    def show_notification():
        app = QtWidgets.QApplication.instance()
        created = False
        if not app:
            app = QtWidgets.QApplication([])
            created = True
        notif = ChromeOSNotification(title, msg, icon_path=icon_path, timeout=duration, with_buttons=with_buttons)
        notif.show()
        if created:
            timer = QtCore.QTimer()
            timer.timeout.connect(app.quit)
            timer.setSingleShot(True)
            timer.start(duration + 800)
            app.exec_()

    threading.Thread(target=show_notification, daemon=True).start()

# --------- Requests Ensure ---------
def ensure_requests():
    try:
        import requests
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "requests"])
        import requests
    return requests

requests = ensure_requests()

APP_ICON = "app/updater-icon.ico"
REPO = "jesusquijada34/packagemaker"
LOCAL_VERSION = "v3.1.0-25.10-11.04-knosthalij"
SCRIPT_NAME = "updater"

def instalar_requisitos():
    req_path = os.path.join("lib", "requirements.txt")
    if os.path.isfile(req_path):
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--user", "-r", req_path])
        except Exception as e:
            chromium_notification_qt(f"Error instalando requisitos: {e}", "Updater Error", with_buttons=True)

def discover_python_association():
    if platform.system().lower() != "windows":
        return None
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, ".py")
        python_file_class, _ = winreg.QueryValueEx(key, "")
        winreg.CloseKey(key)
        if not python_file_class:
            return None
        cmd_key_path = f"{python_file_class}\\shell\\open\\command"
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, cmd_key_path)
        open_cmd, _ = winreg.QueryValueEx(key, "")
        winreg.CloseKey(key)
        if '"' in open_cmd:
            parts = open_cmd.split('"')
            for p in parts:
                if p.lower().endswith("python.exe") and os.path.isfile(p):
                    return p
        if ".exe" in open_cmd.lower():
            start = open_cmd.lower().find("python")
            end = open_cmd.find(".exe", start)
            if end != -1:
                path = open_cmd[:end+4].strip('"').strip()
                if os.path.isfile(path):
                    return path
        return None
    except Exception:
        return None

def find_python_exec_windows():
    python_exe = sys.executable
    associated = discover_python_association()
    if associated and os.path.isfile(associated):
        return associated
    try:
        import winreg
        for key in [
            r"SOFTWARE\Python\PythonCore",
            r"SOFTWARE\WOW6432Node\Python\PythonCore",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\python.exe",
        ]:
            try:
                reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key)
                i = 0
                while True:
                    subver = winreg.EnumKey(reg, i)
                    subkey = winreg.OpenKey(reg, subver)
                    try:
                        install_path, _ = winreg.QueryValueEx(subkey, "InstallPath")
                        exec_path = os.path.join(install_path, "python.exe")
                        if os.path.isfile(exec_path):
                            return exec_path
                    except OSError:
                        pass
                    i += 1
            except Exception:
                continue
    except Exception:
        pass
    return python_exe

def find_python_exec_linux():
    if getattr(sys, "frozen", False):
        return os.path.abspath(sys.argv[0])
    for exe in ["python3", "python"]:
        path = shutil.which(exe)
        if path:
            return path
    return sys.executable

def obtener_cmd_ejecucion():
    fullname = os.path.abspath(sys.argv[0])
    if getattr(sys, "frozen", False):
        return f"\"{fullname}\""
    else:
        plat = platform.system().lower()
        if "windows" in plat:
            exe = discover_python_association()
            if not exe or not os.path.isfile(exe):
                exe = find_python_exec_windows()
            return f"\"{exe}\" \"{fullname}\""
        elif "linux" in plat:
            exe = find_python_exec_linux()
            return f"\"{exe}\" \"{fullname}\""
        else:
            exe = shutil.which("python3") or shutil.which("python") or sys.executable
            return f"\"{exe}\" \"{fullname}\""

def verificar_integridad(nombre="update"):
    ruta = os.path.abspath(sys.argv[0])
    if getattr(sys, "frozen", False):
        return os.path.isfile(ruta) and os.access(ruta, os.X_OK)
    else:
        return os.path.isfile(ruta)

def existe_integracion_inicio(nombre="PackagemakerUpdater"):
    sistema = platform.system().lower()
    if "windows" in sistema:
        try:
            import winreg
            clave = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                   r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
            valor, tipo = winreg.QueryValueEx(clave, nombre)
            winreg.CloseKey(clave)
            return valor is not None and valor.strip() != ""
        except Exception:
            return False
    elif "linux" in sistema:
        desktop_file = os.path.join(os.path.expanduser("~/.config/autostart"), f"{nombre}.desktop")
        return os.path.isfile(desktop_file)
    elif "darwin" in sistema:
        plist_file = os.path.join(os.path.expanduser("~/Library/LaunchAgents"), f"com.{nombre.lower()}.plist")
        return os.path.isfile(plist_file)
    return False

def registrar_inicio(nombre="PackagemakerUpdater"):
    sistema = platform.system().lower()
    ruta = os.path.abspath(sys.argv[0])
    is_frozen = getattr(sys, "frozen", False)
    cmd_ejec = obtener_cmd_ejecucion()
    registrado = False

    if "windows" in sistema:
        try:
            import winreg
            clave = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                   r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(clave, nombre, 0, winreg.REG_SZ, cmd_ejec)
            winreg.CloseKey(clave)
            registrado = True

            try:
                import winshell
                from win32com.client import Dispatch
                startup_dir = os.path.join(os.environ.get('APPDATA'), r"Microsoft\Windows\Start Menu\Programs\Startup")
                os.makedirs(startup_dir, exist_ok=True)
                lnk_path = os.path.join(startup_dir, f"{nombre}.lnk")
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(lnk_path)
                exe = cmd_ejec.split()[0].strip('"')
                shortcut.Targetpath = exe
                shortcut.Arguments = ' '.join(cmd_ejec.split()[1:])
                shortcut.WorkingDirectory = os.path.dirname(ruta)
                if os.path.isfile(APP_ICON):
                    shortcut.IconLocation = os.path.abspath(APP_ICON)
                shortcut.save()
            except Exception as lnkexc:
                print(f"[Updater] No pudo crear acceso directo autostart: {lnkexc}")
            try:

            # Refresca Explorer para iconos, etc.
            subprocess.run("taskkill /f /im explorer.exe", shell=True)
            subprocess.run("start explorer.exe", shell=True)
        except Exception as e:
            print(f"[Updater] Error registro Windows: {e}")
    elif "linux" in sistema:
        user_dir = os.path.expanduser("~/.config/autostart")
        os.makedirs(user_dir, exist_ok=True)
        desktop_file = os.path.join(user_dir, f"{nombre}.desktop")
        contenido = f"""[Desktop Entry]
Type=Application
Exec={cmd_ejec}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name={nombre}
Comment=AutoStart {nombre}
"""
        try:
            with open(desktop_file, "w") as f:
                f.write(contenido)
            os.chmod(desktop_file, 0o755)
            registrado = True
            subprocess.run(["update-desktop-database", os.path.dirname(desktop_file)], check=False)
        except Exception as e:
            print(f"[Updater] Error registro Linux: {e}")
    elif "darwin" in sistema:  # macOS
        plist_dir = os.path.expanduser("~/Library/LaunchAgents")
        os.makedirs(plist_dir, exist_ok=True)
        plist_file = os.path.join(plist_dir, f"com.{nombre.lower()}.plist")
        cmd_list = []
        if is_frozen:
            cmd_list = [os.path.abspath(sys.argv[0])]
        else:
            exe = shutil.which("python3") or sys.executable
            cmd_list = [exe, os.path.abspath(sys.argv[0])]
        plist_args = "".join([f"<string>{item}</string>\n        " for item in cmd_list])
        contenido = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.{nombre.lower()}</string>
    <key>ProgramArguments</key>
    <array>
        {plist_args}
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
"""
        try:
            with open(plist_file, "w") as f:
                f.write(contenido)
            os.chmod(plist_file, 0o644)
            subprocess.run(["launchctl", "unload", plist_file], check=False)
            subprocess.run(["launchctl", "load", plist_file], check=False)
            registrado = True
        except Exception as e:
            print(f"[Updater] Error registro macOS: {e}")

    return registrado

def mostrar_notificacion_estilo_chromium(msg, title="Packagemaker"):
    """
    Muestra una notificación multiplataforma, con fallback seguro.
    En Windows maneja excepciones de plyer y usa notificador alternativo Qt si es necesario, con estilo Chrome OS.
    """
    sistema = platform.system().lower()
    ok = False

    # plyer puede fallar si no existe systray o por bug shell_notify en balloon_tip, lo atrapamos:
    if notification is not None:
        try:
            notification.notify(
                title=title,
                message=msg,
                app_icon=APP_ICON if os.path.isfile(APP_ICON) else None,
                timeout=7
            )
            ok = True
        except Exception as e:
            print(f"[Updater] Error de plyer al mostrar notificación: {e!r}")
            ok = False  # Explicitly reset

    # Fallback: Qt notification con look Chrome OS
    if not ok:
        chromium_notification_qt(msg, title=title, duration=6300)

def refrescar_entorno_sistema():
    sistema = platform.system().lower()
    if "windows" in sistema:
        try:
            subprocess.run("taskkill /f /im explorer.exe", shell=True)
            subprocess.run("start explorer.exe", shell=True)
        except Exception as e:
            print(f"[Updater] Error refrescando explorer.exe: {e}")
    elif "linux" in sistema:
        try:
            subprocess.run(["xdg-desktop-menu", "forceupdate"], check=False)
            subprocess.run(["update-desktop-database"], check=False)
        except Exception as e:
            print(f"[Updater] Error refrescando entorno Linux: {e}")
    elif "darwin" in sistema:
        try:
            subprocess.run(["killall", "Dock"], check=False)
        except Exception as e:
            print(f"[Updater] Error refrescando Dock: {e}")

def check_and_update():
    xml_url = f"https://raw.githubusercontent.com/{REPO}/main/details.xml"
    try:
        remote_xml = requests.get(xml_url).text
        root = ET.fromstring(remote_xml)
        remote_version = root.find("version").text.strip()
        sistema = platform.system().lower()
        sufijo = "danenone" if "linux" in sistema else "knosthalij"
        release_name = f"packagemaker-{remote_version}.zip"
        release_url = f"https://github.com/{REPO}/releases/download/{remote_version}/{release_name}"

        if remote_version != LOCAL_VERSION:
            r = requests.head(release_url)
            if r.status_code == 200:
                descargar_y_extraer_release(release_url)
                mostrar_notificacion_estilo_chromium(f"Se ha actualizado a {remote_version}", "Packagemaker Actualizado")
                refrescar_entorno_sistema()
    except Exception as e:
        print(f"[Updater] Error: {e}")

def descargar_y_extraer_release(url):
    r = requests.get(url, stream=True)
    buffer = io.BytesIO()
    for chunk in r.iter_content(chunk_size=1024):
        if chunk:
            buffer.write(chunk)

    temp_dir = "_temp_update"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    with zipfile.ZipFile(buffer) as z:
        z.extractall(temp_dir)

    reemplazar_archivos(temp_dir, os.getcwd())
    shutil.rmtree(temp_dir)

def reemplazar_archivos(origen, destino):
    for root_dir, _, files in os.walk(origen):
        for file in files:
            ruta_origen = os.path.join(root_dir, file)
            ruta_relativa = os.path.relpath(ruta_origen, origen)
            ruta_destino = os.path.join(destino, ruta_relativa)
            os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
            shutil.copy2(ruta_origen, ruta_destino)

if __name__ == "__main__":
    instalar_requisitos()
    if not verificar_integridad(SCRIPT_NAME):
        print("[Updater] El archivo updater no está presente/integrado correctamente.")
        sys.exit(1)
    registrado = registrar_inicio(SCRIPT_NAME)
    if registrado:
        mostrar_notificacion_estilo_chromium("Integración del actualizador completada y activa.", "Packagemaker Updater")
        refrescar_entorno_sistema()
    else:
        mostrar_notificacion_estilo_chromium("La aplicación se ha iniciado, pero no se pudo registrar el inicio automático.", "Packagemaker")
    check_and_update()
