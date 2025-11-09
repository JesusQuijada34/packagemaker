import os
import sys
import platform
import threading
import requests
import zipfile
import xml.etree.ElementTree as ET
import warnings
from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets, QtWebChannel, QtGui

# Suprimir advertencias de pkg_resources
warnings.filterwarnings("ignore", category=UserWarning, message=".*pkg_resources.*")

try:
    from win10toast_click import ToastNotifier
    WIN10TOAST_AVAILABLE = True
    print("[DEBUG] win10toast_click importado correctamente")
except ImportError as e:
    WIN10TOAST_AVAILABLE = False
    ToastNotifier = None
    print(f"[DEBUG] Error importando win10toast_click: {e}")
except Exception as e:
    WIN10TOAST_AVAILABLE = False
    ToastNotifier = None
    print(f"[DEBUG] Error inesperado importando win10toast_click: {e}")

# --- Configuración ---
APP_TITLE = "Packagemaker Updater"
REMOTE_XML = "https://raw.githubusercontent.com/JesusQuijada34/packagemaker/main/details.xml"
LOCAL_XML = "details.xml"
GITHUB_REPO = "JesusQuijada34/packagemaker"
ICON_PATH = "app/updater-icon.ico"
TEMPLATES_DIR = "templates"

# --- Utilidades ---
def leer_version_xml(ruta_o_texto, remoto=False):
    try:
        if remoto:
            text = ruta_o_texto
        else:
            if not os.path.exists(ruta_o_texto):
                return ""
            with open(ruta_o_texto, "r", encoding="utf-8") as f:
                text = f.read()
        root = ET.fromstring(text)
        return root.findtext("version", "")
    except Exception as e:
        print("Error leyendo XML:", e)
        return ""

def descargar_y_extraer(url, destino, progreso_cb=None, stop_event=None):
    try:
        r = requests.get(url, stream=True, timeout=20)
        if r.status_code != 200:
            print("Código http inesperado:", r.status_code)
            return False
        total = int(r.headers.get("content-length", 0))
        descargado = 0
        with open(destino, "wb") as f:
            for chunk in r.iter_content(8192):
                if stop_event and stop_event.is_set():
                    return False
                if chunk:
                    f.write(chunk)
                    descargado += len(chunk)
                    if total and progreso_cb:
                        progreso_cb(int(descargado * 100 / total))
        with zipfile.ZipFile(destino, "r") as z:
            z.extractall(".")
        os.remove(destino)
        return True
    except Exception as e:
        print("Error descarga o extracción:", e)
        return False

def detectar_plataforma():
    sysplat = platform.system().lower()
    if "win" in sysplat:
        return "windows-x64"
    elif "linux" in sysplat:
        return "linux-x64"
    elif "darwin" in sysplat:
        return "macos-x64"
    return "source"

def obtener_url_release(version):
    try:
        r = requests.get(f"https://api.github.com/repos/{GITHUB_REPO}/releases/tags/{version}", timeout=10)
        if r.status_code != 200:
            return None
        data = r.json()
        plat = detectar_plataforma()
        for asset in data.get("assets", []):
            if plat in asset["name"]:
                return asset["browser_download_url"]
    except Exception as e:
        print("Error obteniendo release URL:", e)
    return f"https://github.com/{GITHUB_REPO}/archive/refs/tags/{version}.zip"

# --- Bridge JS <-> Python para pantalla de descarga ---
class DownloadBridge(QtCore.QObject):
    setProgress = QtCore.pyqtSignal(int)
    setStatus = QtCore.pyqtSignal(str)
    setStage = QtCore.pyqtSignal(str)
    downloadComplete = QtCore.pyqtSignal(bool)

    def __init__(self, view):
        super().__init__()
        self.view = view
        self.stop_event = threading.Event()
        self.url_release = None
        self.download_screen = None

    def iniciar_descarga(self, url):
        self.url_release = url
        self.stop_event.clear()
        self.setStage.emit("download")
        self.setStatus.emit("Conectando al servidor...")
        
        def worker():
            # Fase 1: Descarga
            self.setStage.emit("download")
            ok = descargar_y_extraer(
                self.url_release, 
                "update.zip",
                                     progreso_cb=lambda p: self.setProgress.emit(p),
                stop_event=self.stop_event
            )
            
            if not ok or self.stop_event.is_set():
                self.downloadComplete.emit(False)
                return
            
            # Fase 2: Extracción
            self.setStage.emit("extract")
            self.setStatus.emit("Extrayendo archivos...")
            self.setProgress.emit(100)
            
            # La extracción ya se hace en descargar_y_extraer
            self.downloadComplete.emit(True)
        
        threading.Thread(target=worker, daemon=True).start()

    @QtCore.pyqtSlot()
    def cancelar(self):
        self.stop_event.set()
        self.setStatus.emit("Cancelando...")

# --- Bridge JS <-> Python para notificación inicial ---
class NotificationBridge(QtCore.QObject):
    iniciarDescarga = QtCore.pyqtSignal()
    
    def __init__(self, view, download_screen):
        super().__init__()
        self.view = view
        self.download_screen = download_screen

    @QtCore.pyqtSlot()
    def instalar(self):
        self.iniciarDescarga.emit()

    @QtCore.pyqtSlot()
    def cerrar(self):
        self.view.close()

# --- Pantalla de descarga en pantalla completa ---
class DownloadScreen(QtWebEngineWidgets.QWebEngineView):
    def __init__(self, url_release):
        super().__init__()
        self.setWindowTitle(APP_TITLE + " - Descargando")
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        # Pantalla completa - adaptarse a cualquier resolución
        screen = QtWidgets.QApplication.primaryScreen()
        if screen:
            geometry = screen.geometry()
            self.setGeometry(geometry)
            print(f"[DEBUG] Pantalla completa configurada: {geometry.width()}x{geometry.height()}")
        else:
            # Fallback a pantalla completa por defecto
            self.showFullScreen()
            print("[DEBUG] Pantalla completa usando showFullScreen()")
        
        self.channel = QtWebChannel.QWebChannel()
        self.bridge = DownloadBridge(self)
        self.channel.registerObject("bridge", self.bridge)
        self.page().setWebChannel(self.channel)
        
        html = self._html_template()
        self.setHtml(html, QtCore.QUrl("qrc:///"))
        
        # Conectar señales
        self.bridge.setProgress.connect(lambda p: self.page().runJavaScript(f"setProgress({p})"))
        self.bridge.setStatus.connect(lambda s: self.page().runJavaScript(f"setStatus({repr(s)})"))
        self.bridge.setStage.connect(lambda s: self.page().runJavaScript(f"setStage({repr(s)})"))
        self.bridge.downloadComplete.connect(lambda ok: self.page().runJavaScript(f"onComplete({str(ok).lower()})"))
        
        # No iniciar automáticamente, esperar a que el usuario acepte desde la notificación
    
    def _html_template(self):
        template_path = os.path.join(TEMPLATES_DIR, "download.html")
        try:
            if os.path.exists(template_path):
                with open(template_path, "r", encoding="utf-8") as f:
                    html = f.read()
                return html.replace("{APP_TITLE}", APP_TITLE)
            else:
                print(f"[DEBUG] Template no encontrado: {template_path}, usando template embebido")
                return self._html_template_embebido()
        except Exception as e:
            print(f"[DEBUG] Error leyendo template: {e}, usando template embebido")
            return self._html_template_embebido()
    
    def _html_template_embebido(self):
        return """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<script src="qrc:///qtwebchannel/qwebchannel.js"></script>
<style>
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}
body {{
    font-family: 'Google Sans', 'Roboto', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    width: 100vw;
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    position: relative;
}}
.background-pattern {{
    position: absolute;
    width: 100%;
    height: 100%;
    opacity: 0.1;
    background-image: 
        radial-gradient(circle at 20% 50%, rgba(255,255,255,0.3) 0%, transparent 50%),
        radial-gradient(circle at 80% 80%, rgba(255,255,255,0.2) 0%, transparent 50%);
    animation: pulse 8s ease-in-out infinite;
}}
@keyframes pulse {{
    0%, 100% {{ opacity: 0.1; }}
    50% {{ opacity: 0.15; }}
}}
.container {{
    position: relative;
    z-index: 1;
    text-align: center;
    color: white;
    max-width: 600px;
    padding: 40px;
    animation: fadeInUp 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}}
@keyframes fadeInUp {{
    from {{
        opacity: 0;
        transform: translateY(30px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}
.icon-container {{
    width: 120px;
    height: 120px;
    margin: 0 auto 40px;
    position: relative;
    animation: float 3s ease-in-out infinite;
}}
@keyframes float {{
    0%, 100% {{ transform: translateY(0px); }}
    50% {{ transform: translateY(-10px); }}
}}
.icon-circle {{
    width: 120px;
    height: 120px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}}
.icon-circle svg {{
    width: 64px;
    height: 64px;
    color: white;
}}
.spinner {{
    position: absolute;
    width: 120px;
    height: 120px;
    border: 3px solid rgba(255, 255, 255, 0.2);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    display: none;
}}
@keyframes spin {{
    to {{ transform: rotate(360deg); }}
}}
.spinner.active {{
    display: block;
}}
.title {{
    font-size: 32px;
    font-weight: 500;
    margin-bottom: 16px;
    letter-spacing: -0.5px;
}}
.subtitle {{
    font-size: 18px;
    opacity: 0.9;
    margin-bottom: 48px;
    font-weight: 400;
}}
.status-text {{
    font-size: 16px;
    opacity: 0.8;
    margin-bottom: 32px;
    min-height: 24px;
    transition: opacity 0.3s;
}}
.progress-container {{
    margin: 40px 0;
}}
.progress-bar-wrapper {{
    width: 100%;
    height: 8px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    overflow: hidden;
    position: relative;
    margin-bottom: 16px;
}}
.progress-bar {{
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, #00e676, #00bcd4);
    border-radius: 4px;
    transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}}
.progress-bar::after {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    background: linear-gradient(
        90deg,
        transparent,
        rgba(255, 255, 255, 0.3),
        transparent
    );
    animation: shimmer 2s infinite;
}}
@keyframes shimmer {{
    0% {{ transform: translateX(-100%); }}
    100% {{ transform: translateX(100%); }}
}}
.progress-percent {{
    font-size: 24px;
    font-weight: 500;
    margin-top: 8px;
}}
.cancel-btn {{
    margin-top: 32px;
    padding: 12px 32px;
    background: rgba(255, 255, 255, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 24px;
    color: white;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s;
    backdrop-filter: blur(10px);
}}
.cancel-btn:hover {{
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}}
.cancel-btn:active {{
    transform: translateY(0);
}}
.success-icon {{
    display: none;
    width: 120px;
    height: 120px;
    margin: 0 auto 40px;
    animation: scaleIn 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}}
@keyframes scaleIn {{
    from {{
        opacity: 0;
        transform: scale(0.5);
    }}
    to {{
        opacity: 1;
        transform: scale(1);
    }}
}}
.success-icon.show {{
    display: block;
}}
.error-icon {{
    display: none;
    width: 120px;
    height: 120px;
    margin: 0 auto 40px;
    animation: scaleIn 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}}
.error-icon.show {{
    display: block;
}}
.stage-indicator {{
    display: flex;
    justify-content: center;
    gap: 12px;
    margin-top: 24px;
}}
.stage-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.3);
    transition: all 0.3s;
}}
.stage-dot.active {{
    background: white;
    width: 24px;
    border-radius: 4px;
}}
</style>
</head>
<body>
<div class="background-pattern"></div>
<div class="container">
    <div class="icon-container">
        <div class="icon-circle" id="mainIcon">
            <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
        </div>
        <div class="spinner" id="spinner"></div>
        <div class="success-icon" id="successIcon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M8 12l2 2 4-4"/>
            </svg>
        </div>
        <div class="error-icon" id="errorIcon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 8v4M12 16h.01"/>
            </svg>
        </div>
    </div>
    <h1 class="title">{0}</h1>
    <p class="subtitle">Actualización disponible</p>
    <div class="status-text" id="statusText">Preparando descarga...</div>
    <div class="progress-container">
        <div class="progress-bar-wrapper">
            <div class="progress-bar" id="progressBar"></div>
        </div>
        <div class="progress-percent" id="progressPercent">0%</div>
    </div>
    <div class="stage-indicator">
        <div class="stage-dot" id="dot1"></div>
        <div class="stage-dot" id="dot2"></div>
    </div>
    <button class="cancel-btn" onclick="bridge.cancelar()" id="cancelBtn">Cancelar</button>
</div>
<script>
new QWebChannel(qt.webChannelTransport, function(channel) {{
    window.bridge = channel.objects.bridge;
}});
let currentProgress = 0;
function setProgress(p) {{
    currentProgress = p;
    document.getElementById('progressBar').style.width = p + '%';
    document.getElementById('progressPercent').textContent = p + '%';
}}
function setStatus(text) {{
    document.getElementById('statusText').textContent = text;
}}
function setStage(stage) {{
    const spinner = document.getElementById('spinner');
    const mainIcon = document.getElementById('mainIcon');
    if (stage === 'download') {{
        spinner.classList.add('active');
        mainIcon.style.display = 'none';
        document.getElementById('dot1').classList.add('active');
        document.getElementById('dot2').classList.remove('active');
    }} else if (stage === 'extract') {{
        spinner.classList.remove('active');
        mainIcon.style.display = 'flex';
        document.getElementById('dot1').classList.remove('active');
        document.getElementById('dot2').classList.add('active');
    }}
}}
function onComplete(success) {{
    const spinner = document.getElementById('spinner');
    const mainIcon = document.getElementById('mainIcon');
    const successIcon = document.getElementById('successIcon');
    const errorIcon = document.getElementById('errorIcon');
    const cancelBtn = document.getElementById('cancelBtn');
    
    spinner.classList.remove('active');
    mainIcon.style.display = 'none';
    
    if (success) {{
        successIcon.classList.add('show');
        setStatus('¡Actualización completada!');
        cancelBtn.textContent = 'Cerrar';
        cancelBtn.onclick = function() {{ window.close(); }};
        setTimeout(() => {{ window.close(); }}, 2000);
    }} else {{
        errorIcon.classList.add('show');
        setStatus('Error en la descarga');
        cancelBtn.textContent = 'Cerrar';
        cancelBtn.onclick = function() {{ window.close(); }};
    }}
}}
</script>
</body>
</html>
""".format(APP_TITLE)

# --- Notificación inicial ---
class NotificationWindow(QtWebEngineWidgets.QWebEngineView):
    def __init__(self, version_local, version_remota, url_release, download_screen):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        # Tamaño responsive para la notificación
        self.resize(450, 200)
        self.download_screen = download_screen
        
        self.channel = QtWebChannel.QWebChannel()
        self.bridge = NotificationBridge(self, download_screen)
        self.channel.registerObject("bridge", self.bridge)
        self.page().setWebChannel(self.channel)
        
        html = self._html_template(version_local, version_remota)
        self.setHtml(html, QtCore.QUrl("qrc:///"))

        # Conectar señal
        self.bridge.iniciarDescarga.connect(self._iniciar_descarga)
    
    def _iniciar_descarga(self):
        self.hide()
        self.download_screen.show()
        # Iniciar descarga automáticamente cuando se muestra la pantalla
        QtCore.QTimer.singleShot(300, lambda: self.download_screen.bridge.iniciar_descarga(self.download_screen.bridge.url_release))

    def _html_template(self, v_local, v_remota):
        template_path = os.path.join(TEMPLATES_DIR, "notification.html")
        try:
            if os.path.exists(template_path):
                with open(template_path, "r", encoding="utf-8") as f:
                    html = f.read()
                return html.replace("{APP_TITLE}", APP_TITLE).replace("{V_LOCAL}", v_local or 'N/A').replace("{V_REMOTA}", v_remota or 'N/A')
            else:
                print(f"[DEBUG] Template no encontrado: {template_path}, usando template embebido")
                return self._html_template_embebido(v_local, v_remota)
        except Exception as e:
            print(f"[DEBUG] Error leyendo template: {e}, usando template embebido")
            return self._html_template_embebido(v_local, v_remota)
    
    def _html_template_embebido(self, v_local, v_remota):
        # Inspirado en notificadores ChromeOS y Material Design
        return """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<script src="qrc:///qtwebchannel/qwebchannel.js"></script>
<style>
body {
    margin:0; padding:0;
    font-family: 'Google Sans', 'Segoe UI', 'Roboto', Arial, sans-serif;
    background: transparent;
    min-height:100vh;
    min-width:100vw;
}
.notification {
    position: fixed;
    right: 40px; bottom: 32px;
    background: rgba(38,50,56,0.97);
    border-radius: 16px 16px 16px 8px;
    box-shadow: 0 10px 32px 0 rgba(0,0,0,0.28);
    padding: 28px 32px 24px 24px;
    color: #fff;
    width: 410px;
    max-width: 90vw;
    display: flex;
    flex-direction: row;
    align-items: flex-start;
    overflow: visible;
    border-left: 4px solid #00bcd4;
    animation: fadein .6s cubic-bezier(.4,0,.2,1);
}
@keyframes fadein {
    from {opacity:0;transform:translateY(24px);}
    to   {opacity:1;transform:translateY(0);}
}
.icon-area {
    flex-shrink:0;
    margin-right: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 54px;
}
.icon-area svg {
    width:46px;
    height:46px;
    margin-bottom:8px;
}
.text-area {
    flex: 1 1 auto;
    display: flex;
    flex-direction: column;
}
.title {
    font-size:1.22rem;
    font-weight: 600;
    letter-spacing:0.01em;
    margin-bottom:6px;
    color:#fff;
}
.versinfo {
    font-size:0.93rem;
    color:#B2EBF2;
    margin-bottom:10px;
    letter-spacing:0.01em;
}
#msg {
    margin-bottom: 18px;
    font-size: 1.03rem;
    min-height: 21px;
    color:#ECEFF1;
}
.progress {
    width: 100%;
    height: 7px;
    background: #263238;
    border-radius: 5px;
    margin-bottom: 18px;
    overflow: hidden;
    box-shadow: 0 2px 12px #003d4d33 inset;
}
.progress span {
    display: block;
    height: 100%;
    width: 0;
    background: linear-gradient(90deg, #00e6ff 0%, #39ffe7 100%);
    transition: width .36s cubic-bezier(.4,0,.2,1);
}
.button-area {
    display: flex;
    flex-direction: row;
    justify-content: flex-end;
    margin-top: 1px;
    gap:4px;
}
button {
    padding:8px 18px;
    border:none;
    border-radius:8px;
    background:#00bcd4;
    color: #fff;
    font-size: .99rem;
    font-weight: 500;
    box-shadow:0 2px 8px #00bcd422;
    cursor:pointer;
    margin-right: 0;
    margin-left: 0;
    outline:none;
    transition:background .24s;
}
button:hover {
    background: #008fa3;
}
button:active {
    background: #00bcd4;
}
.msg-primary { color:#fff; font-weight:500; }
.msg-success { color: #00e676; }
.msg-error { color: #ff5252; }
.msg-warning { color: #ffe082; }
.check-mark {
    display:none;
    align-items:center;
    justify-content:center;
    margin-bottom:8px;
}
#checkicon {
    color: #00e676;
    width:46px;height:46px;
}
.check-error {
    display:none;
    align-items:center;
    justify-content:center;
    margin-bottom:8px;
}
#erroricon {
    color: #ff5252;
    width:46px;height:46px;
}
@media (max-width:510px) {
    .notification {
        left:12px; right:12px; width:auto; max-width:96vw; 
        padding-right:12px; padding-left:10px;
    }
    .icon-area { width: 34px; }
    .icon-area svg { width:32px; height:32px; }
}
</style>
</head>
<body>
<div class="notification">
    <div class="icon-area">
        <div id="initicon">
            <svg viewBox="0 0 48 48" fill="none">
                <rect x="7" y="9" width="34" height="30" rx="7" fill="#00BCD4" opacity="0.75"/>
                <rect x="12" y="6" width="24" height="30" rx="8" fill="#39FFE7" opacity="0.5"/>
                <rect x="17" y="2" width="14" height="34" rx="7" fill="#E1F7FA" opacity="0.80"/>
            </svg>
        </div>
        <div class="check-mark" id="checkarea">
            <svg id="checkicon" fill="none" viewBox="0 0 48 48">
                <circle cx="24" cy="24" r="22" fill="#fff" opacity="0.18"/>
                <path d="M14 26 l7 7 l13-15" stroke="#00e676" stroke-width="4" fill="none"
                 stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
        <div class="check-error" id="errorarea">
            <svg id="erroricon" fill="none" viewBox="0 0 48 48">
                <circle cx="24" cy="24" r="22" fill="#fff" opacity="0.16"/>
                <path d="M16 16 l16 16M32 16 l-16 16"
                 stroke="#ff5252" stroke-width="4" fill="none"
                 stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
    </div>
    <div class="text-area">
        <span class="title">{0}</span>
        <div class="versinfo">Versión local: <b>{1}</b> &nbsp;•&nbsp; Disponible: <b>{2}</b></div>
        <div id="msg">¿Deseas actualizar ahora?</div>
        <div class="progress"><span id="bar"></span></div>
        <div class="button-area">
            <button onclick="bridge.instalar()" id="btn-actualizar">Actualizar ahora</button>
            <button onclick="bridge.cancelar()" id="btn-cancelar">Cancelar</button>
            <button onclick="bridge.cerrar()"  id="btn-masltrd">Más tarde</button>
        </div>
    </div>
</div>
<script>
new QWebChannel(qt.webChannelTransport, function(channel) { window.bridge = channel.objects.bridge; });
function setMessage(html){
    document.getElementById('msg').innerHTML = html;
}
function setProgress(p){
    document.getElementById('bar').style.width = p + '%';
}
function showCheckmark(){
    document.getElementById('initicon').style.display = "none";
    document.getElementById('checkarea').style.display = "flex";
    document.getElementById('errorarea').style.display = "none";
    // disable buttons after update
    document.getElementById('btn-actualizar').disabled = true;
    document.getElementById('btn-actualizar').style.opacity = 0.5;
}
function showError(){
    document.getElementById('initicon').style.display = "none";
    document.getElementById('checkarea').style.display = "none";
    document.getElementById('errorarea').style.display = "flex";
    document.getElementById('btn-actualizar').disabled = false;
    document.getElementById('btn-actualizar').style.opacity = 1;
}
</script>
</body></html>
""".format(APP_TITLE, v_local or 'N/A', v_remota or 'N/A')

    def show_bottom_right(self):
        # Ajuste para multi-monitor y escalado
        screen = QtWidgets.QApplication.primaryScreen()
        if hasattr(screen, "availableGeometry"):
            rect = screen.availableGeometry()
            self.move(rect.right() - self.width() - 18, rect.bottom() - self.height() - 18)
        else:
            self.move(40, 40)
        self.show()

# --- Función para mostrar notificación del sistema con icono y callback ---
def mostrar_notificacion_sistema(titulo, mensaje, callback_instalar=None, callback_cerrar=None):
    print(f"[DEBUG] Intentando mostrar notificación: {titulo}")
    if WIN10TOAST_AVAILABLE and ToastNotifier:
        try:
            # Verificar si el icono existe
            icon_path = ICON_PATH if os.path.exists(ICON_PATH) else None
            print(f"[DEBUG] Icono path: {icon_path}, existe: {icon_path is not None and os.path.exists(icon_path) if icon_path else False}")
            
            toaster = ToastNotifier()
            print("[DEBUG] ToastNotifier creado")
            
            # Función callback cuando se hace clic en la notificación
            # Usar un enfoque más simple sin callback para evitar errores de WNDPROC
            def on_notification_click():
                print("[DEBUG] Notificación clickeada")
                try:
                    if callback_instalar:
                        # Ejecutar callback en un thread separado para evitar problemas
                        threading.Thread(target=callback_instalar, daemon=True).start()
                except Exception as e:
                    print(f"[DEBUG] Error en callback: {e}")
                    import traceback
                    traceback.print_exc()
            
            print("[DEBUG] Mostrando toast...")
            # Los errores de WNDPROC son internos de win10toast_click y no afectan la funcionalidad
            # Se muestran pero la notificación funciona correctamente
            try:
                toaster.show_toast(
                    title=titulo,
                    msg=mensaje + "\n\nHaz clic para actualizar",
                    icon_path=icon_path,
                    duration=None,  # No desaparece automáticamente
                    threaded=True,
                    callback_on_click=on_notification_click
                )
                print("[DEBUG] Toast mostrado (nota: errores de WNDPROC son internos y no afectan funcionalidad)")
            except Exception as toast_error:
                print(f"[DEBUG] Error al mostrar toast: {toast_error}")
                raise
        except TypeError as e:
            print(f"[DEBUG] TypeError en notificación (posible problema con win10toast_click): {e}")
            print(f"[DEBUG] Notificación fallback: {titulo} - {mensaje}")
        except Exception as e:
            print(f"[DEBUG] Error mostrando notificación: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
    else:
        # Fallback si win10toast no está disponible
        print(f"[DEBUG] win10toast no disponible, fallback: {titulo} - {mensaje}")

# --- Clase para System Tray Icon ---
class UpdaterTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = parent
        self.download_screen = None
        self.notif_window = None
        
        # Configurar icono
        icon_path = ICON_PATH if os.path.exists(ICON_PATH) else None
        if icon_path:
            self.setIcon(QtGui.QIcon(icon_path))
        else:
            # Icono por defecto
            app = QtWidgets.QApplication.instance()
            if app:
                self.setIcon(app.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon))
            else:
                # Si no hay aplicación, crear un icono simple
                pixmap = QtGui.QPixmap(16, 16)
                pixmap.fill(QtGui.QColor(100, 150, 200))
                self.setIcon(QtGui.QIcon(pixmap))
        
        self.setToolTip(APP_TITLE)
        
        # Crear menú contextual
        menu = QtWidgets.QMenu()
        
        action_check = menu.addAction("Verificar actualizaciones ahora")
        action_check.triggered.connect(self.verificar_actualizaciones)
        
        menu.addSeparator()
        
        action_about = menu.addAction("Acerca de")
        action_about.triggered.connect(self.mostrar_acerca_de)
        
        action_quit = menu.addAction("Salir")
        action_quit.triggered.connect(self.salir)
        
        self.setContextMenu(menu)
        
        # Conectar señal de activación (clic en el icono)
        self.activated.connect(self.on_tray_icon_activated)
        
        # Timer para verificar actualizaciones cada 1 minuto
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.verificar_actualizaciones)
        self.timer.start(60000)  # 60000 ms = 1 minuto
        
        print("[DEBUG] System Tray Icon creado, monitoreo cada 1 minuto")
    
    def on_tray_icon_activated(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.DoubleClick:
            self.verificar_actualizaciones()
    
    def verificar_actualizaciones(self):
        print("[DEBUG] Verificando actualizaciones...")
        try:
            local_ver = leer_version_xml(LOCAL_XML)
            print(f"[DEBUG] Versión local: {local_ver}")
            
            try:
                txt_remota = requests.get(REMOTE_XML, timeout=10).text
            except Exception as e:
                print(f"[DEBUG] Error obteniendo XML remoto: {e}")
                return
            
            remota_ver = leer_version_xml(txt_remota, remoto=True)
            print(f"[DEBUG] Versión remota: {remota_ver}")
            
            if remota_ver and remota_ver != local_ver:
                print(f"[DEBUG] Actualización disponible: {local_ver} -> {remota_ver}")
                self.mostrar_actualizacion_disponible(local_ver, remota_ver)
            else:
                print("[DEBUG] No hay actualizaciones disponibles")
        except Exception as e:
            print(f"[DEBUG] Error verificando actualizaciones: {e}")
            import traceback
            traceback.print_exc()
    
    def mostrar_actualizacion_disponible(self, local_ver, remota_ver):
        url = obtener_url_release(remota_ver)
        print(f"[DEBUG] URL de release: {url}")
        
        # Crear pantalla de descarga
        self.download_screen = DownloadScreen(url)
        self.download_screen.bridge.url_release = url
        self.download_screen.hide()
        
        # Crear ventana de notificación
        self.notif_window = NotificationWindow(local_ver, remota_ver, url, self.download_screen)
        
        # Función callback para iniciar descarga desde notificación
        def iniciar_desde_notificacion():
            print("[DEBUG] Callback iniciar_desde_notificacion ejecutado")
            self.notif_window.bridge.iniciarDescarga.emit()
        
        # Mostrar notificación del sistema con callback
        mostrar_notificacion_sistema(
            f"{APP_TITLE}",
            f"Actualización disponible: {remota_ver}\nVersión actual: {local_ver or 'N/A'}\n\nHaz clic para actualizar",
            callback_instalar=iniciar_desde_notificacion
        )
        
        # Mostrar también la ventana de notificación
        self.notif_window.show_bottom_right()
    
    def mostrar_acerca_de(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("Acerca de")
        msg.setText(f"{APP_TITLE}\n\nMonitoreando actualizaciones cada 1 minuto.")
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.exec_()
    
    def salir(self):
        print("[DEBUG] Saliendo de la aplicación...")
        QtWidgets.QApplication.quit()

# --- Flujo principal ---
def main():
    print("[DEBUG] Iniciando aplicación...")
    app = QtWidgets.QApplication(sys.argv)
    
    # Verificar si el sistema soporta system tray
    if not QtWidgets.QSystemTrayIcon.isSystemTrayAvailable():
        print("[DEBUG] System tray no disponible, mostrando mensaje")
        QtWidgets.QMessageBox.critical(None, APP_TITLE, 
            "El sistema no soporta system tray.\nLa aplicación no puede ejecutarse.")
        sys.exit(1)
    
    # Evitar que la aplicación se cierre cuando se cierra la última ventana
    app.setQuitOnLastWindowClosed(False)
    
    print("[DEBUG] QApplication creado")
    
    # Crear system tray icon
    tray_icon = UpdaterTrayIcon(app)
    tray_icon.show()
    
    print("[DEBUG] System Tray Icon mostrado")
    
    # Verificar actualizaciones al inicio
    tray_icon.verificar_actualizaciones()
    
    print("[DEBUG] Iniciando loop de eventos (aplicación en segundo plano)...")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
