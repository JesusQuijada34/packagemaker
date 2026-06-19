#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Installation functions for the updater system.
"""
import os
import sys
from PyQt6.QtWidgets import QApplication
from .core import log, _rXml, _rXml_r, _fR, _fR_exe
from .windows import ModernUpdaterWindow, IFLAPPInstallerWindow, EXEInstallerWindow, LicenseTermsDialog

# --- LEVIATHAN UI CHECK ---
try:
    from leviathan_ui import InmersiveSplash
    HAS_LEVIATHAN = True
except ImportError:
    HAS_LEVIATHAN = False


def install_iflapp(iflapp_path, target_dir=None, silent=False):
    """Instala un archivo .iflapp en el directorio especificado.
    
    Args:
        iflapp_path: Ruta al archivo .iflapp
        target_dir: Directorio destino (opcional)
        silent: Si True, no muestra interfaz gráfica
    
    Returns:
        tuple: (success: bool, message: str)
    """
    from .workers import IFLAPPInstallerWorker
    
    if not os.path.exists(iflapp_path):
        return False, f"Archivo no encontrado: {iflapp_path}"
    
    if silent:
        # Modo silencioso: sin interfaz
        worker = IFLAPPInstallerWorker(iflapp_path, target_dir or os.path.join(os.getcwd(), "installed_app"))
        
        # Ejecutar síncronamente
        try:
            worker.run()
            return True, "Instalación completada"
        except Exception as e:
            return False, str(e)
    else:
        # Modo GUI: mostrar ventana
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Mostrar splash
        splash = None
        if HAS_LEVIATHAN:
            try:
                splash = InmersiveSplash(
                    brand="IFLAPP Installer",
                    tagline="Instalando paquete...",
                    accent="#2486ff",
                    duration=1500
                )
                splash.show()
                QApplication.processEvents()
            except Exception as e:
                log(f"[Splash Error] {e}")
        
        window = IFLAPPInstallerWindow(iflapp_path, target_dir)
        
        if splash:
            splash.finish(window)
        
        window.show()
        
        if not QApplication.instance():
            sys.exit(app.exec())
        
        return True, "Ventana mostrada"


def update_app(silent=False, accept_license=False, cache_in_memory=True):
    """Verifica y realiza actualizaciones de la aplicación.
    
    Prioridad:
    1. Busca ejecutable setup (.exe) con formato de packagemaker
    2. Si no existe, usa paquete .iflapp como alternativa
    
    Args:
        silent: Si True, no muestra interfaz gráfica
        accept_license: Si True, acepta términos automáticamente (modo silent)
        cache_in_memory: Si True, usa caché en memoria para descargas
    
    Returns:
        bool: True si se actualizó correctamente
    """
    app_data = _rXml("details.xml")
    if not app_data:
        log("[ERROR] No se pudo leer details.xml")
        return False
    
    remote_version = _rXml_r(app_data["author"], app_data["app"])
    if not remote_version or remote_version == app_data["version"]:
        log(f"[INFO] Ya estás en la última versión: {app_data['version']}")
        return False
    
    log(f"[INFO] Actualización disponible: {app_data['version']} -> {remote_version}")
    
    # PRIORIDAD 1: Buscar ejecutable setup
    exe_url, exe_filename = _fR_exe(
        app_data["author"], 
        app_data["app"], 
        remote_version, 
        app_data["platform"], 
        app_data["publisher"]
    )
    
    if exe_url:
        log(f"[EXE] Setup encontrado: {exe_filename}")
        return _update_from_exe(app_data, exe_url, exe_filename, silent, accept_license, cache_in_memory)
    
    # PRIORIDAD 2: Buscar paquete .iflapp como alternativa
    log("[IFLAPP] Buscando paquete alternativo...")
    url = _fR(app_data["author"], app_data["app"], remote_version, app_data["platform"], app_data["publisher"])
    
    if not url:
        log("[ERROR] No se encontró ni .exe ni .iflapp")
        return False
    
    log(f"[IFLAPP] Usando paquete: {url}")
    return _update_from_iflapp(app_data, url, silent)


def _update_from_exe(app_data, exe_url, exe_filename, silent=False, accept_license=False, cache_in_memory=True):
    """Realiza actualización desde ejecutable setup."""
    from .workers import EXEInstallerWorker
    
    app_name = app_data.get("app", "Aplicación")
    
    if silent:
        if not accept_license:
            log("[ERROR] Modo silencioso requiere --accept-license para setup .exe")
            return False
        
        log(f"[EXE] Iniciando instalación silenciosa de {exe_filename}...")
        # Modo silencioso sin GUI
        worker = EXEInstallerWorker(exe_url, exe_filename, cache_in_memory)
        try:
            worker.run()
            return True
        except Exception as e:
            log(f"[EXE ERROR] {e}")
            return False
    
    # Modo GUI: Mostrar splash -> Términos de licencia -> Instalador
    app = QApplication(sys.argv)
    
    # Mostrar splash inicial
    splash = None
    if HAS_LEVIATHAN:
        try:
            splash = InmersiveSplash(
                brand="System Updater",
                tagline=f"Actualización disponible para {app_name}",
                accent="#2486ff",
                icon_path="details.xml".replace("details.xml", "app/app-icon.ico") if os.path.exists("details.xml".replace("details.xml", "app/app-icon.ico")) else None,
                duration=1500
            )
            splash.show()
            QApplication.processEvents()
        except Exception as e:
            log(f"[Splash Error] {e}")
    
    # Cerrar splash y mostrar términos de licencia
    if splash:
        splash.close()
    
    # Mostrar diálogo de términos de licencia
    license_dialog = LicenseTermsDialog(app_name=app_name)
    license_result = {"accepted": False}
    
    def on_accept():
        license_result["accepted"] = True
    
    def on_reject():
        license_result["accepted"] = False
        app.quit()
    
    license_dialog.accepted.connect(on_accept)
    license_dialog.rejected.connect(on_reject)
    license_dialog.show()
    app.exec()
    
    if not license_result["accepted"]:
        log("[LICENSE] Términos rechazados. Cancelando actualización.")
        return False
    
    log("[LICENSE] Términos aceptados. Continuando instalación...")
    
    # Mostrar ventana de instalación del .exe
    install_window = EXEInstallerWindow(exe_url, exe_filename, cache_in_memory=cache_in_memory)
    install_window.show()
    app.exec()
    
    return True


def _update_from_iflapp(app_data, url, silent=False):
    """Realiza actualización desde paquete .iflapp (método alternativo)."""
    if silent:
        log(f"Actualizando a través de .iflapp...")
        app = QApplication(sys.argv)
        window = ModernUpdaterWindow(app_data, url)
        window.show()
        app.exec()
        return True
    else:
        app = QApplication(sys.argv)
        
        # Mostrar splash
        splash = None
        if HAS_LEVIATHAN:
            try:
                splash = InmersiveSplash(
                    brand="System Updater",
                    tagline=f"Actualizando {app_data['app']}...",
                    accent="#2486ff",
                    icon_path="details.xml".replace("details.xml", "app/app-icon.ico") if os.path.exists("details.xml".replace("details.xml", "app/app-icon.ico")) else None,
                    duration=2000
                )
                splash.show()
                QApplication.processEvents()
            except Exception as e:
                log(f"[Splash Error] {e}")
        
        window = ModernUpdaterWindow(app_data, url)
        
        if splash:
            splash.finish(window)
        
        window.show()
        app.exec()
        return True
