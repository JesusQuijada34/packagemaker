"""
Updater mejorado para Influent Package Maker
- Notificaciones nativas de Windows en tiempo real
- Manejo de errores con leviathan-ui
"""
import os
import sys
import time
import shutil
import zipfile
import traceback
import subprocess
import requests
from pathlib import Path
try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QProgressBar
    from PyQt6.QtGui import QFont, QIcon, QPixmap, QColor
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QObject
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    class QThread: pass
    class pyqtSignal:
        def __init__(self, *args): pass
        def connect(self, func): pass
        def emit(self, *args): pass
    class QObject: pass
    class QMainWindow:
        def __init__(self, *args, **kwargs): pass
    class QWidget:
        def __init__(self, *args, **kwargs): pass
    class QProgressBar:
        def __init__(self, *args, **kwargs): pass

# Leviathan UI
try:
    from leviathan_ui import WipeWindow, CustomTitleBar, LeviathanProgressBar, LeviathanDialog
    HAS_LEVIATHAN = True
except (ImportError, SyntaxError):
    HAS_LEVIATHAN = False
    class LeviathanDialog:
        @staticmethod
        def launch(*args, **kwargs): print(f"[MOCK] LeviathanDialog: {args}")
    class LeviathanProgressBar: pass

# Notificaciones nativas de Windows
try:
    import winreg
    from winrt.windows.ui.notifications import ToastNotificationManager, ToastNotification
    from winrt.windows.data.xml.dom import XmlDocument
    HAS_WIN_TOAST = True
except ImportError:
    HAS_WIN_TOAST = False

# Notificaciones alternativas con plyer
try:
    from plyer import notification
    HAS_PLYER = True
except ImportError:
    HAS_PLYER = False

class ToastNotifier:
    """Manejador de notificaciones nativas de Windows (Toast)."""
    
    APP_ID = "Influent.PackageMaker.Updater"
    
    @classmethod
    def _get_notifier(cls):
        """Obtiene el administrador de notificaciones."""
        if not HAS_WIN_TOAST:
            return None
        try:
            return ToastNotificationManager.create_toast_notifier(cls.APP_ID)
        except Exception:
            return None
    
    @classmethod
    def notify(cls, title: str, message: str, icon_type: str = "info"):
        """
        Muestra una notificación nativa de Windows.
        
        Args:
            title: Título de la notificación
            message: Mensaje de la notificación
            icon_type: Tipo de icono (info, warning, error, success)
        """
        # Intentar notificación nativa de Windows 10/11
        if HAS_WIN_TOAST:
            try:
                notifier = cls._get_notifier()
                if notifier:
                    # Mapear tipos a iconos de Windows
                    icon_map = {
                        "info": "uri://{0}ms-resource://{0}/Files/Assets/Square44x44Logo.png".format(cls.APP_ID),
                        "warning": "warning",
                        "error": "error",
                        "success": "checkmark"
                    }
                    
                    xml_content = f"""<?xml version="1.0" encoding="utf-8"?>
<toast>
    <visual>
        <binding template="ToastGeneric">
            <text>{title}</text>
            <text>{message}</text>
        </binding>
    </visual>
</toast>"""
                    
                    xml_doc = XmlDocument()
                    xml_doc.load_xml(xml_content)
                    toast = ToastNotification(xml_doc)
                    notifier.show(toast)
                    return True
            except Exception as e:
                print(f"[ToastNotifier] Error nativo: {e}")
        
        # Fallback a plyer
        if HAS_PLYER:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_name="Package Maker Updater",
                    timeout=5
                )
                return True
            except Exception as e:
                print(f"[ToastNotifier] Error plyer: {e}")
        
        # Último fallback: imprimir a consola
        print(f"[NOTIFICATION] {title}: {message}")
        return False
    
    @classmethod
    def notify_progress(cls, title: str, message: str, progress: int):
        """Notificación con progreso (Windows 10/11)."""
        if HAS_WIN_TOAST and 0 <= progress <= 100:
            try:
                notifier = cls._get_notifier()
                if notifier:
                    xml_content = f"""<?xml version="1.0" encoding="utf-8"?>
<toast>
    <visual>
        <binding template="ToastGeneric">
            <text>{title}</text>
            <text>{message}</text>
            <progress value="{progress}" status="{progress}% completado" title="Descargando..."/>
        </binding>
    </visual>
</toast>"""
                    xml_doc = XmlDocument()
                    xml_doc.load_xml(xml_content)
                    toast = ToastNotification(xml_doc)
                    notifier.show(toast)
                    return True
            except Exception:
                pass
        
        # Fallback sin progreso
        return cls.notify(title, message)


class KillerLogic:
    """Lógica para terminar procesos de forma segura."""
    
    @staticmethod
    def kill_target(target_name):
        """Termina procesos por nombre (Windows/Linux/macOS)."""
        print(f"[KillerLogic] Terminando procesos de: {target_name}")
        killed = []
        
        try:
            if sys.platform == "win32":
                # Intentar primero sin /F (suave)
                result = subprocess.run(
                    ["taskkill", "/IM", f"{target_name}.exe"],
                    capture_output=True,
                    shell=False
                )
                if result.returncode == 0:
                    killed.append(f"{target_name}.exe")
                
                # Forzar si es necesario
                subprocess.run(
                    ["taskkill", "/F", "/IM", f"{target_name}.exe"],
                    capture_output=True,
                    shell=False
                )
                subprocess.run(
                    ["taskkill", "/F", "/IM", target_name],
                    capture_output=True,
                    shell=False
                )
                
            elif sys.platform == "darwin":  # macOS
                result = subprocess.run(
                    ["pkill", "-f", target_name],
                    capture_output=True,
                    shell=False
                )
                if result.returncode == 0:
                    killed.append(target_name)
                    
            else:  # Linux
                result = subprocess.run(
                    ["pkill", "-9", "-f", target_name],
                    capture_output=True,
                    shell=False
                )
                if result.returncode == 0:
                    killed.append(target_name)
            
            if killed:
                print(f"[KillerLogic] Procesos terminados: {killed}")
                return True
            return False
            
        except Exception as e:
            print(f"[KillerLogic] Error: {e}")
            return False

class InstallerWorker(QObject):
    """Worker thread para instalación de actualizaciones."""
    
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    error_signal = pyqtSignal(str, str)  # title, message

    def __init__(self, url, app_data, show_notifications=True):
        super().__init__()
        self.url = url
        self.app = app_data["app"]
        self.app_name = app_data.get("name", self.app)
        self._running = True
        self._show_notifications = show_notifications
        self._temp_zip = "pending_update.zip"
        self._ext_dir = "update_temp_extracted"
        
    def _cleanup(self):
        """Limpia archivos temporales."""
        for path in [self._ext_dir, self._temp_zip]:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                elif os.path.isfile(path):
                    os.remove(path)
            except Exception as e:
                print(f"[InstallerWorker] Cleanup warning: {e}")
    
    def _notify(self, title: str, message: str, icon_type: str = "info"):
        """Envía notificación si están habilitadas."""
        if self._show_notifications:
            ToastNotifier.notify(title, message, icon_type)
    
    def _notify_progress(self, title: str, message: str, progress: int):
        """Envía notificación de progreso."""
        if self._show_notifications:
            ToastNotifier.notify_progress(title, message, progress)

    def run(self):
        """Ejecuta el proceso de instalación."""
        try:
            # Notificación de inicio
            self._notify(
                f"Actualizando {self.app_name}",
                "Conectando con el servidor...",
                "info"
            )
            
            self.status.emit("Conectando con el servidor...")
            
            # Descarga con timeout y reintentos
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    r = requests.get(self.url, stream=True, timeout=30)
                    r.raise_for_status()
                    break
                except requests.RequestException as e:
                    if attempt == max_retries - 1:
                        raise Exception(f"No se pudo conectar después de {max_retries} intentos: {e}")
                    time.sleep(2 ** attempt)  # Backoff exponencial
            
            total = int(r.headers.get("content-length", 0))
            if total == 0:
                raise Exception("El servidor no proporcionó el tamaño del archivo")
            
            downloaded = 0
            last_progress = 0
            
            self.status.emit("Descargando actualización...")
            
            with open(self._temp_zip, "wb") as f:
                for chunk in r.iter_content(8192):
                    if not self._running:
                        self._cleanup()
                        return
                    
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        progress = int(downloaded * 100 / total)
                        
                        # Emitir progreso cada 5%
                        if progress - last_progress >= 5:
                            self.progress.emit(progress)
                            self._notify_progress(
                                f"Descargando {self.app_name}",
                                f"{progress}% completado",
                                progress
                            )
                            last_progress = progress
            
            # Notificación de descompresión
            self._notify(
                f"Actualizando {self.app_name}",
                "Descomprimiendo archivos...",
                "info"
            )
            self.status.emit("Descomprimiendo actualización...")
            
            # Limpia directorio anterior si existe
            self._cleanup()
            
            # Extrae ZIP
            with zipfile.ZipFile(self._temp_zip, "r") as z:
                z.extractall(self._ext_dir)
            
            # Verifica que se extrajo algo
            if not os.path.exists(self._ext_dir) or not os.listdir(self._ext_dir):
                raise Exception("El archivo de actualización está vacío o corrupto")
            
            # Notificación de cierre de app
            self._notify(
                f"Actualizando {self.app_name}",
                "Cerrando aplicación principal...",
                "warning"
            )
            self.status.emit("Cerrando aplicación principal...")
            
            KillerLogic.kill_target(self.app)
            time.sleep(2)
            
            # Instalación
            self.status.emit("Instalando archivos...")
            files_installed = 0
            files_failed = 0
            
            for root, dirs, files in os.walk(self._ext_dir):
                rel = os.path.relpath(root, self._ext_dir)
                dest_fold = rel if rel != "." else "."
                
                if dest_fold != "." and not os.path.exists(dest_fold):
                    os.makedirs(dest_fold, exist_ok=True)
                
                for file in files:
                    if not self._running:
                        return
                        
                    src = os.path.join(root, file)
                    dst = os.path.join(dest_fold, file)
                    
                    # No sobrescribir el ejecutable del updater
                    if os.path.abspath(dst) == os.path.abspath(sys.argv[0]):
                        continue
                    
                    try:
                        # Backup si existe
                        if os.path.exists(dst):
                            backup = dst + f".backup.{int(time.time())}"
                            os.rename(dst, backup)
                        
                        shutil.move(src, dst)
                        files_installed += 1
                        
                    except Exception as e:
                        print(f"[InstallerWorker] Error instalando {file}: {e}")
                        files_failed += 1
            
            # Notificación final
            if files_failed == 0:
                self._notify(
                    f"{self.app_name} actualizado",
                    f"Se instalaron {files_installed} archivos correctamente",
                    "success"
                )
            else:
                self._notify(
                    f"{self.app_name} actualizado con advertencias",
                    f"Instalados: {files_installed}, Fallidos: {files_failed}",
                    "warning"
                )
            
            self.status.emit("Finalizando...")
            
            # Limpieza final
            self._cleanup()
            
            self.finished.emit(True, f"Instalación completada: {files_installed} archivos")

        except requests.RequestException as e:
            error_msg = f"Error de conexión: {e}"
            self._notify("Error de actualización", error_msg, "error")
            self.error_signal.emit("Error de conexión", error_msg)
            self.finished.emit(False, error_msg)
            
        except zipfile.BadZipFile:
            error_msg = "El archivo de actualización está corrupto"
            self._notify("Error de actualización", error_msg, "error")
            self.error_signal.emit("Archivo corrupto", error_msg)
            self._cleanup()
            self.finished.emit(False, error_msg)
            
        except PermissionError as e:
            error_msg = f"Error de permisos: {e}. Ejecuta como administrador."
            self._notify("Error de permisos", error_msg, "error")
            self.error_signal.emit("Permisos insuficientes", error_msg)
            self.finished.emit(False, error_msg)
            
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            traceback.print_exc()
            self._notify("Error de actualización", error_msg, "error")
            self.error_signal.emit("Error", error_msg)
            self._cleanup()
            self.finished.emit(False, error_msg)

class ModernUpdaterWindow(QMainWindow):
    """Ventana principal del updater con UI moderna y manejo de errores."""
    
    def __init__(self, app_data, url, show_notifications=True):
        super().__init__()
        self.app_data = app_data
        self.url = url
        self._show_notifications = show_notifications
        self._has_error = False
        
        # Notificación inicial
        if self._show_notifications:
            ToastNotifier.notify(
                "Package Maker Updater",
                f"Iniciando actualización de {app_data.get('name', app_data['app'])}",
                "info"
            )
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(480, 320)
        
        if HAS_LEVIATHAN:
            WipeWindow.create().set_mode("ghostBlur").apply(self)
        
        self.init_ui()
        self.center()
        QTimer.singleShot(500, self.start_install)

    def center(self):
        """Centra la ventana en la pantalla."""
        screen = QApplication.primaryScreen()
        if screen:
            self.move(screen.availableGeometry().center() - self.rect().center())

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        central = QWidget()
        central.setObjectName("Central")
        central.setStyleSheet(
            "QWidget#Central { background: rgba(18, 24, 34, 0.85); "
            "border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; }"
        )
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        if HAS_LEVIATHAN:
            self.title_bar = CustomTitleBar(self, title="System Updater")
            self.title_bar.set_color(QColor(0, 0, 0, 0))
            layout.addWidget(self.title_bar)

        content = QWidget()
        c_lay = QVBoxLayout(content)
        c_lay.setContentsMargins(30, 10, 30, 30)
        c_lay.setSpacing(15)

        self.icon_lbl = QLabel("🔄")
        self.icon_lbl.setStyleSheet("font-size: 48px; color: #2486ff;")
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_lay.addWidget(self.icon_lbl)

        app_name = self.app_data.get('name', self.app_data['app'])
        self.lbl_main = QLabel(f"Actualizando {app_name}")
        self.lbl_main.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_main.setStyleSheet(
            "font-family: 'Segoe UI'; font-weight: 700; font-size: 18px; color: white;"
        )
        c_lay.addWidget(self.lbl_main)

        self.lbl_status = QLabel("Preparando...")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setStyleSheet("color: #aaa; font-size: 13px;")
        c_lay.addWidget(self.lbl_status)

        if HAS_LEVIATHAN:
            self.pbar = LeviathanProgressBar(self)
        else:
            self.pbar = QProgressBar()
            self.pbar.setStyleSheet(
                "QProgressBar { background: #333; border: none; height: 6px; } "
                "QProgressBar::chunk { background: #2486ff; }"
            )
            self.pbar.setTextVisible(False)
        c_lay.addWidget(self.pbar)

        layout.addWidget(content)

    def start_install(self):
        """Inicia el proceso de instalación."""
        self.thread = QThread()
        self.worker = InstallerWorker(
            self.url, 
            self.app_data, 
            show_notifications=self._show_notifications
        )
        self.worker.moveToThread(self.thread)
        
        # Conectar señales
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.pbar.setValue)
        self.worker.status.connect(self.lbl_status.setText)
        self.worker.finished.connect(self.on_fin)
        self.worker.error_signal.connect(self.on_error)
        
        self.thread.start()

    def on_error(self, title: str, message: str):
        """Maneja errores mostrando LeviathanDialog si está disponible."""
        self._has_error = True
        
        # Notificación de error
        if self._show_notifications:
            ToastNotifier.notify(title, message, "error")
        
        # Usar LeviathanDialog si está disponible
        if HAS_LEVIATHAN:
            try:
                LeviathanDialog.launch(
                    self,
                    title,
                    message,
                    mode="error"
                )
            except Exception as e:
                print(f"[ModernUpdaterWindow] Error mostrando dialog: {e}")

    def on_fin(self, ok, msg):
        """Callback cuando finaliza la instalación."""
        self.thread.quit()
        
        if ok:
            self.lbl_status.setText("¡Actualización completada!")
            self.icon_lbl.setText("✅")
            self.icon_lbl.setStyleSheet("font-size: 48px; color: #22c55e;")
            
            # Notificación de éxito
            if self._show_notifications:
                ToastNotifier.notify(
                    "Actualización completada",
                    f"{self.app_data.get('name', self.app_data['app'])} se actualizó correctamente",
                    "success"
                )
            
            # Reiniciar aplicación
            exe = f"{self.app_data['app']}.exe"
            if os.path.exists(exe):
                try:
                    subprocess.Popen(exe, shell=False)
                except Exception as e:
                    print(f"[ModernUpdaterWindow] Error reiniciando: {e}")
            
            QTimer.singleShot(1500, self.close)
            
        else:
            self.lbl_status.setText(f"Error: {msg}")
            self.lbl_status.setStyleSheet("color: #ff5252;")
            self.icon_lbl.setText("❌")
            self.icon_lbl.setStyleSheet("font-size: 48px; color: #ff5252;")
            
            # Mostrar error con LeviathanDialog si no se mostró ya
            if not self._has_error and HAS_LEVIATHAN:
                try:
                    LeviathanDialog.launch(
                        self,
                        "Error de actualización",
                        msg,
                        mode="error"
                    )
                except Exception as e:
                    print(f"[ModernUpdaterWindow] Error mostrando dialog: {e}")

    def closeEvent(self, event):
        """Maneja el cierre de la ventana."""
        if hasattr(self, 'worker'):
            self.worker._running = False
        if hasattr(self, 'thread') and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait(1000)
        event.accept()

