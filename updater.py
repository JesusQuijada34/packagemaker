#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PackageMaker Updater - Main Entry Point

This script provides the main entry point for the PackageMaker updater system.
It imports core functionality from lib.coreUpdater and provides CLI/GUI interfaces.
"""
import sys
import os
import argparse
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QFont, QIcon, QPixmap, QColor, QGuiApplication
from PyQt6.QtCore import Qt

# Import core updater module
from lib.coreUpdater import (
    log,
    _rXml,
    _rXml_r,
    _fR,
    _fR_exe,
    XML_PATH,
    LOG_PATH,
    GITHUB_API,
    SystemTrayIcon,
    KillerLogic,
    InstallerWorker,
    IFLAPPInstallerWorker,
    EXEInstallerWorker,
    ModernUpdaterWindow,
    IFLAPPInstallerWindow,
    LicenseTermsDialog,
    EXEInstallerWindow,
    install_iflapp,
    update_app,
    get_tray_icon,
    set_tray_icon,
    get_updater_window,
    set_updater_window,
)


class UpdaterInfoWindow(QMainWindow):
    """Main GUI window that shows updater details when opened."""
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(600, 450)
        self.init_ui()
        self.center()
    
    def center(self):
        screen = QGuiApplication.primaryScreen()
        if screen:
            self.move(screen.availableGeometry().center() - self.rect().center())
    
    def init_ui(self):
        central = QWidget()
        central.setObjectName("Central")
        central.setStyleSheet("""
            QWidget#Central { 
                background: rgba(18, 24, 34, 0.95); 
                border: 1px solid rgba(255,255,255,0.1); 
                border-radius: 16px; 
            }
            QPushButton {
                background: #2486ff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover { background: #1a6fd4; }
        """)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("🔄 PackageMaker Updater")
        title.setStyleSheet("font-family: 'Segoe UI'; font-weight: 700; font-size: 24px; color: white;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Version info
        try:
            app_data = _rXml(XML_PATH)
            if app_data:
                version_text = f"""
                <div style='color: #aaa; font-size: 14px; text-align: center;'>
                    <p><b>Aplicación:</b> {app_data.get('app', 'N/A')}</p>
                    <p><b>Versión Actual:</b> {app_data.get('version', 'N/A')}</p>
                    <p><b>Plataforma:</b> {app_data.get('platform', 'N/A')}</p>
                    <p><b>Autor:</b> {app_data.get('author', 'N/A')}</p>
                    <p><b>Publisher:</b> {app_data.get('publisher', 'N/A')}</p>
                </div>
                """
            else:
                version_text = "<p style='color: #ff5252; text-align: center;'>No se pudo leer details.xml</p>"
        except Exception as e:
            version_text = f"<p style='color: #ff5252; text-align: center;'>Error: {e}</p>"
        
        info_label = QLabel(version_text)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Buttons
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(10)
        
        self.btn_check = QPushButton("🔍 Verificar Actualizaciones")
        self.btn_check.clicked.connect(self.check_updates)
        btn_layout.addWidget(self.btn_check)
        
        self.btn_update = QPushButton("⬇️ Actualizar Ahora")
        self.btn_update.clicked.connect(self.run_update)
        btn_layout.addWidget(self.btn_update)
        
        self.btn_exit = QPushButton("❌ Salir")
        self.btn_exit.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid rgba(255,255,255,0.2);
                color: #aaa;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.1);
                color: white;
            }
        """)
        self.btn_exit.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_exit)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
    
    def check_updates(self):
        """Check for updates and show result."""
        try:
            app_data = _rXml(XML_PATH)
            if not app_data:
                self.show_message("Error", "No se pudo leer details.xml")
                return
            
            remote_version = _rXml_r(app_data["author"], app_data["app"])
            if not remote_version:
                self.show_message("Información", "No se pudo verificar la versión remota")
                return
            
            if remote_version == app_data["version"]:
                self.show_message("✅ Actualizado", f"Ya tienes la última versión: {app_data['version']}")
            else:
                self.show_message("🔄 Actualización Disponible", 
                    f"Versión actual: {app_data['version']}\nNueva versión: {remote_version}")
        except Exception as e:
            self.show_message("Error", str(e))
    
    def run_update(self):
        """Run the update process."""
        try:
            success = update_app(silent=False, accept_license=False, cache_in_memory=True)
            if not success:
                self.show_message("Información", "No se encontraron actualizaciones o el proceso fue cancelado")
        except Exception as e:
            self.show_message("Error", str(e))
    
    def show_message(self, title, message):
        """Show a simple message dialog."""
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()


def show_info_gui():
    """Show the updater info GUI."""
    app = QApplication.instance() or QApplication(sys.argv)
    window = UpdaterInfoWindow()
    window.show()
    sys.exit(app.exec())


def main():
    """Punto de entrada principal con soporte CLI."""
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
        print("Influent Updater v2.1")
        print("Soporta: Actualizaciones OTA (EXE > IFLAPP), instalación .iflapp, caché en memoria")
        return
    
    if args.install:
        # Instalar archivo .iflapp
        success, msg = install_iflapp(args.install, args.target, args.silent)
        if args.silent:
            print(f"{'OK' if success else 'ERROR'}: {msg}")
        sys.exit(0 if success else 1)
    
    if args.check:
        # Solo verificar actualizaciones
        app_data = _rXml(XML_PATH)
        if not app_data:
            print("ERROR: No se pudo leer details.xml")
            sys.exit(1)
        
        remote = _rXml_r(app_data["author"], app_data["app"])
        if remote and remote != app_data["version"]:
            # Verificar si hay .exe disponible
            exe_url, exe_filename = _fR_exe(
                app_data["author"], app_data["app"], 
                remote, app_data["platform"], app_data["publisher"]
            )
            if exe_url:
                print(f"UPDATE_AVAILABLE: {app_data['version']} -> {remote}")
                print(f"TYPE: EXE_SETUP")
                print(f"FILENAME: {exe_filename}")
                print(f"DOWNLOAD_URL: {exe_url}")
                sys.exit(0)
            
            # Verificar .iflapp como alternativa
            url = _fR(app_data["author"], app_data["app"], remote, app_data["platform"], app_data["publisher"])
            if url:
                print(f"UPDATE_AVAILABLE: {app_data['version']} -> {remote}")
                print(f"TYPE: IFLAPP_PACKAGE")
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