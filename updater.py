#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PackageMaker Updater - Main Entry Point

This script provides the main entry point for the PackageMaker updater system.
It imports core functionality from lib.coreUpdater and provides CLI/GUI interfaces.
"""
import sys
import argparse
import importlib
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
from PyQt6.QtGui import QGuiApplication, QPixmap
from PyQt6.QtCore import Qt, QEasingCurve, pyqtSignal, QTimer, QPropertyAnimation

from lib.app_icons import icon_button

try:
    from leviathan_ui import WipeWindow
    LEVIATHAN_AVAILABLE = True
except (ImportError, SyntaxError):
    LEVIATHAN_AVAILABLE = False

    class WipeWindow:
        """Respaldo sin efectos cuando ``leviathan_ui`` no está instalado.

        El updater se copia a todos los proyectos empaquetados y también se usa
        en modo headless (``--version``/``--check``/``--install``); sin este
        respaldo, la ausencia de la dependencia opcional abortaba con
        ``ImportError`` antes de parsear los argumentos.
        """

        def __init__(self, parent=None):
            self._parent = parent

        @classmethod
        def create(cls):
            return cls()

        def set_mode(self, *args, **kwargs):
            return self

        def set_radius(self, *args, **kwargs):
            return self

        def set_blur(self, *args, **kwargs):
            return self

        def apply(self, *args, **kwargs):
            return self

        def show(self, *args, **kwargs):
            return self

        def close(self, *args, **kwargs):
            return self


# Import core updater module
from lib.coreUpdater import (
    _rXml,
    _rXml_r,
    _fR,
    _fR_exe,
    XML_PATH,
    install_iflapp,
    update_app,
)

width = 450
height = 200
SPLASH_DURATION_MS = 5000


if sys.platform.startswith("linux"):
    _ico_fallback = os.path.join("app", "updater-icon.ico")
    _png_path = os.path.join("app", "updater-icon.png")
    iconPath = _png_path if os.path.exists(_png_path) else _ico_fallback
else:
    iconPath = os.path.join("app", "updater-icon.ico")

class UpdaterInfoWindow(QMainWindow):
    """Main GUI window that shows updater details when opened."""
    
    def __init__(self):
        super().__init__()
        self.accent = str(get_accent_color())
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(f"""
            * {{
                outline: none;
            }}
            QWidget#Central {{ 
                background: transparent; 
                border: 1px solid {self.accent}; 
                border-radius: 5px; 
            }}
            QPushButton {{
                font-family: 'SF Pro';
                font-weight: 500;
                font-size: 12px;
                background: transparent;
                border-radius: 5px; 
                border: 1px solid gray;
                color: gray;
                padding: 12px 12px;
                border-bottom: 3px solid gray;
            }}
            QPushButton:hover {{
                border: 1px solid {self.accent};
                border-bottom: 3px solid {self.accent};
            }}
            QPushButton:pressed {{
                color: white;
                border: 1px solid {self.accent};
                background: {self.accent};
                border-bottom: 3px solid gray;
            }}
            QLabel {{
                font-family: 'SF Pro';
                font-weight: 700;
                font-size: 24px;
                color: black;
            }}
        """)
        wpwnd = WipeWindow.create()
        wpwnd.set_mode("ghostBlur")
        wpwnd.set_radius(5)
        wpwnd.apply(self)
        self.resize(width, height)
        self.init_ui()
        self.center()
    
    def center(self):
        screen = QGuiApplication.primaryScreen().geometry()
        w = int(width * 1.01)
        h = int(height * 1.57)
        x = (screen.width() - w)
        y = (screen.height() - h)
        if screen:
            from lib.qml_animations import animate_property
            self.move(x, y)
            self.setWindowOpacity(0.0)
            animate_property(
                self,
                "windowOpacity",
                0.0,
                1.0,
                800,
                QEasingCurve.Type.OutExpo,
            )
    
    def init_ui(self):
        central = QWidget()
        central.setObjectName("Central")
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        title = QLabel("Influent FireCube Updater")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        try:
            app_data = _rXml(XML_PATH)
            if app_data:
                version_text = f"""
                <div style='color: gray; font-size: 14px; text-align: center;'>
                    <p>Update <b>{app_data.get('publisher', 'N/A')} {app_data.get('name', 'N/A')}</b> ?</p>
                    <p>Local Package Version is <b>{app_data.get('version', 'N/A')}</b> and it's created by <b>{app_data.get('author', 'N/A')}</b></p>
                    <p>Package for <b>{app_data.get('platform', 'N/A')}</b></p>
                    <p></p>
                </div>
                """
            else:
                version_text = "<p style='color: orange; text-align: center;'>Could not read details.xml</p>"
        except Exception as e:
            version_text = f"<p style='color: red; text-align: center;'>Error: {e}</p>"
        
        info_label = QLabel(version_text)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        self.btn_update = QPushButton("Update")
        icon_button(self.btn_update, "download", 18)
        self.btn_update.clicked.connect(self.update)
        btn_layout.addWidget(self.btn_update)
        
        self.btn_exit = QPushButton("Exit")
        icon_button(self.btn_exit, "right", 18)
        self.btn_exit.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_exit)
        layout.addLayout(btn_layout)
        layout.addStretch()

    def on_splash_finished(self) -> None:
        UpdaterInfoWindow.show(self)

    def closeEvent(self, event):
        from lib.uwp_animations import play_bounce_down_close
        if getattr(self, "_force_close", False):
            super().closeEvent(event)
            return
        event.ignore()
        play_bounce_down_close(self, on_finished=lambda: self._finish_close(), drop_px=80)

    def _finish_close(self):
        self._force_close = True
        self.close()

    def update(self):
        try:
            app_data = _rXml(XML_PATH)
            if not app_data:
                self.show_message("error", "Read error", "Could not read details.xml")
                return
            
            remote_version = _rXml_r(app_data["author"], app_data["app"])
            if not remote_version:
                self.show_message("error", "Mirror error", "Could not verify the remote version")
                return
            
            if remote_version == app_data["version"]:
                self.show_message("success", "Great!", f"You already have the latest version: {app_data['version']}")
            else:
                self.show_message("info", "Update Available",
                                  f"Current version: {app_data['version']}\nNew version: {remote_version}")
                try:
                    success = update_app(silent=False, accept_license=False, cache_in_memory=True)
                    if not success:
                        self.show_message("warning", "Warning", "No updates were found or the process was cancelled")
                except Exception as e:
                    self.show_message("error", "Error",  str(e))
    
        except Exception as e:
            self.show_message("error", "Exception error", str(e))
    
    def show_message(self, mode, title, msg):
        """Show a simple message dialog."""
        from lib.alert_dialog import AlertDialog
        aD = AlertDialog
        aD.launch(self, title, str(msg), mode=mode)
        return

class IntegratedSplash(QWidget):
    """Splash integrado estilo UWP - minimalista con solo icono centrado"""

    finished = pyqtSignal()

    def __init__(self, parent=None, icon_path=None, title="appKnob"):
        super().__init__(parent)
        self.parent = parent
        self.accent = str(get_accent_color())
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(0, 0, parent.width(), parent.height())
        self.setStyleSheet(f"""
            QWidget#SplashContainer {{
                background-color: {self.accent};
                border-radius: 5px;
            }}
        """)

        container = QWidget(self)
        container.setObjectName("SplashContainer")
        container.setGeometry(0, 0, self.width(), self.height())

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()

        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if icon_path and os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(128, 128, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.icon_label.setPixmap(scaled)
        layout.addWidget(self.icon_label)

        layout.addStretch()

        self.splash_timer = QTimer(self)
        self.splash_timer.timeout.connect(self._finish_splash)
        self.splash_timer.setSingleShot(True)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.parent:
            self.setGeometry(0, 0, self.parent.width(), self.parent.height())
            container = self.findChild(QWidget, "SplashContainer")
            if container:
                container.setGeometry(0, 0, self.width(), self.height())

    def start(self, delay_ms=5000):
        self.show()
        self.raise_()
        self.splash_timer.start(delay_ms)

    def _finish_splash(self):
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(600)
        self.fade_anim.setStartValue(1.0)
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_anim.finished.connect(self._close_and_emit)
        self.fade_anim.start()

    def _close_and_emit(self):
        self.hide()
        self.finished.emit()
        self.deleteLater()

def get_accent_color():
    try:
        from leviathan_ui import get_accent_color as _leviathan_accent
    except (ImportError, SyntaxError):
        return "#0078D4"
    try:
        return str(_leviathan_accent())
    except Exception:
        return "#0078D4"

def show_info_gui():
    app = QApplication.instance() or QApplication(sys.argv)
    window = UpdaterInfoWindow()
    def on_splash_finished():
        if getattr(sys, "frozen", False) and os.environ.get("_PYI_SPLASH_IPC"):
            try:
                importlib.import_module("pyi_splash").close()
            except (ImportError, OSError):
                pass
        window.on_splash_finished()
    window.show()
    splash = IntegratedSplash(
        parent=window,
        icon_path=iconPath if os.path.exists(iconPath) else None,
        title="Influent FireCube Updater",
    )
    splash.finished.connect(on_splash_finished)
    splash.start(SPLASH_DURATION_MS)
    sys.exit(app.exec())

def main():
    parser = argparse.ArgumentParser(
        description="Updater e instalador para Influent Package Maker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  updater.py                          Mostrar GUI con información del updater
  updater.py --check                 Verificar actualizaciones
  updater.py --silent --accept-license  Actualizar silenciosamente (acepta términos)
  updater.py --install app.iflapp    Instalar paquete .iflapp
  updater.py --install app.iflapp --target "C:/Apps/MiApp" --silent

Modos de actualización:
  1. Busca ejecutable setup (.exe) con formato packagemaker
  2. Si no existe, usa paquete .iflapp como alternativa
  3. Caché en memoria para descargas rápidas
        """
    )
    
    parser.add_argument("--check", action="store_true", help="Verificar si hay actualizaciones disponibles")
    parser.add_argument("--silent", action="store_true", help="Ejecutar sin interfaz gráfica")
    parser.add_argument("--accept-license", action="store_true", help="Aceptar términos de licencia automáticamente (requiere --silent)")
    parser.add_argument("--no-cache", action="store_true", help="Deshabilitar caché en memoria")
    parser.add_argument("--install", metavar="FILE", help="Instalar archivo .iflapp")
    parser.add_argument("--target", metavar="DIR", help="Directorio destino para instalación")
    parser.add_argument("--version", action="store_true", help="Mostrar versión del updater")
    
    args = parser.parse_args()
    
    if args.version:
        print("Influent FireCube Updater v2.1")
        return
    
    if args.install:
        success, msg = install_iflapp(args.install, args.target, args.silent)
        if args.silent:
            print(f"{'OK' if success else 'ERROR'}: {msg}")
        sys.exit(0 if success else 1)
    
    if args.check:
        app_data = _rXml(XML_PATH)
        if not app_data:
            print("ERROR: No se pudo leer details.xml")
            sys.exit(1)
        
        remote = _rXml_r(app_data["author"], app_data["app"])
        if remote and remote != app_data["version"]:
            exe_url, exe_filename = _fR_exe(
                app_data["author"], app_data["app"], 
                remote, app_data["platform"], app_data["publisher"]
            )
            if exe_url:
                print(f"UPDATE_AVAILABLE: {app_data['version']} -> {remote}")
                print("TYPE: EXE_SETUP")
                print(f"FILENAME: {exe_filename}")
                print(f"DOWNLOAD_URL: {exe_url}")
                sys.exit(0)
            
            # Verificar .iflapp como alternativa
            url = _fR(app_data["author"], app_data["app"], remote, app_data["platform"], app_data["publisher"])
            if url:
                print(f"UPDATE_AVAILABLE: {app_data['version']} -> {remote}")
                print("TYPE: IFLAPP_PACKAGE")
                print(f"DOWNLOAD_URL: {url}")
                sys.exit(0)
        
        print("NO_UPDATE: Ya tienes la versión más reciente")
        sys.exit(0)
    
    # Verificar compatibilidad de argumentos
    if args.accept_license and not args.silent:
        print("ERROR: --accept-license requiere --silent")
        sys.exit(1)
    
    # Modo updater automático (sin argumentos específicos) o --silent
    if args.silent:
        # Modo silencioso
        success = update_app(
            silent=True, 
            accept_license=args.accept_license,
            cache_in_memory=not args.no_cache
        )
        sys.exit(0 if success else 1)
    else:
        # Si no hay argumentos específicos, mostrar GUI con información
        if len(sys.argv) == 1:
            show_info_gui()
            
        else:
            # Modo GUI interactivo para actualización
            success = update_app(
                silent=False,
                accept_license=False,
                cache_in_memory=not args.no_cache
            )
            sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
