#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Worker classes for background installation tasks.
"""
import os
import sys
import shutil
import zipfile
import time
import traceback
from io import BytesIO
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from .core import log, KillerLogic, cache_get, cache_set

# requests con fallback a urllib
try:
    import requests
except ImportError:
    requests = None

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
            
            if requests:
                r = requests.get(self.url, stream=True)
                total = int(r.headers.get("content-length", 0))
                down = 0
                with open(temp_zip, "wb") as f:
                    for chunk in r.iter_content(8192):
                        if not self._running: return
                        f.write(chunk)
                        down += len(chunk)
                        if total: self.progress.emit(int(down * 100 / total))
            else:
                # Fallback usando urllib
                import urllib.request
                with urllib.request.urlopen(self.url, timeout=60) as response:
                    total = int(response.headers.get("Content-Length", 0))
                    down = 0
                    with open(temp_zip, "wb") as f:
                        while True:
                            chunk = response.read(8192)
                            if not chunk or not self._running: break
                            f.write(chunk)
                            down += len(chunk)
                            if total: self.progress.emit(int(down * 100 / total))

            self.status.emit("Descomprimiendo actualización...")
            if os.path.exists(ext_dir): shutil.rmtree(ext_dir)
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
                    if os.path.abspath(dst) == os.path.abspath(sys.argv[0]): continue 
                    if os.path.exists(dst):
                        try: os.remove(dst)
                        except: # Rename strategy for locked files
                            try: os.rename(dst, dst + f".old.{int(time.time())}")
                            except: continue
                    try: shutil.move(src, dst)
                    except: pass

            # Sincronizar plantillas antes de borrar
            try:
                from .installer import sync_templates_to_local
                self.status.emit("Sincronizando plantillas...")
                sync_ok, sync_msg, sync_files = sync_templates_to_local()
                if sync_ok and sync_files:
                    log(f"[UPDATE] Plantillas sincronizadas: {len(sync_files)} archivos")
                elif not sync_ok:
                    log(f"[UPDATE] Sincronización de plantillas: {sync_msg}")
            except Exception as sync_err:
                log(f"[UPDATE] Error sincronizando plantillas: {sync_err}")

            try: shutil.rmtree(ext_dir)
            except: pass
            try: os.remove(temp_zip)
            except: pass
            
            self.status.emit("Finalizando...")
            self.finished.emit(True, "OK")

        except Exception as e:
            log(traceback.format_exc())
            self.finished.emit(False, str(e))


class IFLAPPInstallerWorker(QObject):
    """Worker para instalar archivos .iflapp en segundo plano."""
    
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    
    def __init__(self, iflapp_path, target_dir):
        super().__init__()
        self.iflapp_path = iflapp_path
        self.target_dir = target_dir
    
    def run(self):
        try:
            self.status.emit("Extrayendo paquete...")
            
            # Crear directorio destino si no existe
            os.makedirs(self.target_dir, exist_ok=True)
            
            # Extraer archivo .iflapp (zip)
            with zipfile.ZipFile(self.iflapp_path, 'r') as zf:
                files = zf.namelist()
                total = len(files)
                for i, file in enumerate(files):
                    zf.extract(file, self.target_dir)
                    self.progress.emit(int((i + 1) * 100 / total))
            
            self.status.emit("Configurando aplicación...")
            
            # Verificar details.xml
            import xml.etree.ElementTree as ET
            details_path = os.path.join(self.target_dir, "details.xml")
            if os.path.exists(details_path):
                tree = ET.parse(details_path)
                root = tree.getroot()
                app_name = root.findtext("app", "Aplicación")
                self.status.emit(f"{app_name} instalado correctamente")
            
            self.progress.emit(100)
            self.finished.emit(True, "OK")
            
        except Exception as e:
            log(traceback.format_exc())
            self.finished.emit(False, str(e))


class EXEInstallerWorker(QObject):
    """Worker para descargar e instalar ejecutable setup."""
    
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    
    def __init__(self, url, filename, cache_in_memory=True):
        super().__init__()
        self.url = url
        self.filename = filename
        self.cache_in_memory = cache_in_memory
        self._running = True
        self.temp_exe_path = None
    
    def run(self):
        import subprocess
        import tempfile
        
        try:
            cache_key = f"exe_download_{self.url}"
            
            # Verificar caché en memoria
            if self.cache_in_memory:
                cached_data = cache_get(cache_key)
                if cached_data:
                    log("[CACHE] Usando ejecutable en caché de memoria")
                    self.status.emit("Usando caché de memoria...")
                    exe_data = cached_data
                else:
                    # Descargar a memoria
                    self.status.emit("Descargando instalador...")
                    if requests:
                        r = requests.get(self.url, stream=True, timeout=60)
                        total = int(r.headers.get("content-length", 0))
                        
                        chunks = []
                        downloaded = 0
                        for chunk in r.iter_content(65536):  # 64KB chunks
                            if not self._running:
                                return
                            chunks.append(chunk)
                            downloaded += len(chunk)
                            if total:
                                self.progress.emit(int(downloaded * 50 / total))  # 0-50% descarga
                        
                        exe_data = b"".join(chunks)
                    else:
                        # Fallback usando urllib
                        import urllib.request
                        with urllib.request.urlopen(self.url, timeout=60) as response:
                            total = int(response.headers.get("Content-Length", 0))
                            chunks = []
                            downloaded = 0
                            while True:
                                chunk = response.read(65536)
                                if not chunk or not self._running:
                                    break
                                chunks.append(chunk)
                                downloaded += len(chunk)
                                if total:
                                    self.progress.emit(int(downloaded * 50 / total))
                            exe_data = b"".join(chunks)
                    
                    cache_set(cache_key, exe_data)
                    log(f"[CACHE] Guardado en memoria: {len(exe_data)} bytes")
            else:
                # Descarga tradicional a archivo
                self.status.emit("Descargando instalador...")
                temp_file = os.path.join(tempfile.gettempdir(), f"download_{os.getpid()}.tmp")
                
                if requests:
                    r = requests.get(self.url, stream=True, timeout=60)
                    total = int(r.headers.get("content-length", 0))
                    
                    downloaded = 0
                    with open(temp_file, "wb") as f:
                        for chunk in r.iter_content(65536):
                            if not self._running:
                                return
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total:
                                self.progress.emit(int(downloaded * 50 / total))
                    with open(temp_file, "rb") as f:
                        exe_data = f.read()
                else:
                    # Fallback usando urllib
                    import urllib.request
                    def reporthook(block_num, block_size, total_size):
                        if total_size > 0:
                            self.progress.emit(int(block_num * block_size * 50 / total_size))
                    urllib.request.urlretrieve(self.url, temp_file, reporthook)
                    with open(temp_file, "rb") as f:
                        exe_data = f.read()
            
            self.progress.emit(50)
            self.status.emit("Preparando instalación...")
            
            # Escribir a archivo temporal
            temp_dir = tempfile.gettempdir()
            self.temp_exe_path = os.path.join(temp_dir, self.filename)
            
            with open(self.temp_exe_path, "wb") as f:
                f.write(exe_data)
            
            log(f"[EXE] Guardado temporalmente: {self.temp_exe_path}")
            
            self.progress.emit(60)
            self.status.emit("Ejecutando instalador en modo silencioso...")
            
            # Ejecutar con --silent
            if sys.platform == "win32":
                # Windows: ejecutar con /SILENT o /VERYSILENT
                cmd = [self.temp_exe_path, "/SILENT", "/NORESTART", "/CLOSEAPPLICATIONS"]
            else:
                # Linux/Mac: ejecutar con --silent
                cmd = [self.temp_exe_path, "--silent"]
            
            # Ejecutar y esperar
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False
            )
            
            self.progress.emit(75)
            self.status.emit("Instalando... (esto puede tardar unos minutos)")
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self.progress.emit(100)
                self.status.emit("Instalación completada")
                log("[EXE] Instalación exitosa")
                self.finished.emit(True, "OK")
            else:
                error_msg = stderr.decode("utf-8", errors="ignore")[:200] if stderr else f"Código: {process.returncode}"
                log(f"[EXE] Error: {error_msg}")
                self.finished.emit(False, f"Error en instalador: {error_msg}")
            
            # Limpiar archivo temporal
            try:
                if self.temp_exe_path and os.path.exists(self.temp_exe_path):
                    os.remove(self.temp_exe_path)
                    log(f"[EXE] Temporal eliminado: {self.temp_exe_path}")
            except: pass
            
        except Exception as e:
            log(traceback.format_exc())
            self.finished.emit(False, str(e))
