#!/usr/bin/env python3
"""
FlangCompiler IT - Compilador y empaquetador automático para el ecosistema Flarm.
Versión Unificada (Multiplataforma)

Este script automatiza la compilación de binarios (usando PyInstaller) y la creación
de paquetes de release para Windows (Knosthalij) y Linux (Danenone) a partir de
repositorios de código fuente.

Características:
- Análisis de details.xml para obtener metadatos y determinar el script principal.
- Compilación condicional basada en la plataforma especificada (AlphaCube, Knosthalij, Danenone).
- Generación de binarios ejecutables para cada script encontrado.
- Creación de paquetes con estructura correcta para cada plataforma.
- Exclusión inteligente de archivos innecesarios (requirements.txt, .sh, .bat, etc.).
- Soporte para generación de scripts de compilación cruzada (build_linux.sh en Windows, build_windows.bat en Linux).

Uso:
    python compiler_full.py <ruta_repositorio> [--output <ruta_salida>]

Ejemplo:
    python compiler_full.py /home/ubuntu/flarmhandler --output /home/ubuntu/releases
"""

import os
import sys
import shutil
import subprocess
import xml.etree.ElementTree as ET
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import platform
import threading
import fnmatch
import zipfile
import re
import json
import urllib.request
import urllib.error
import ssl
import tempfile

try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QLabel, QPushButton, QFileDialog, 
                                QTextEdit, QFrame, QGraphicsDropShadowEffect, QSizePolicy)
    from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QObject, QSize, QTimer, QEvent, QThread
    from PyQt5.QtGui import QColor, QFont, QIcon, QPainter, QPainterPath, QLinearGradient
    from PyQt5.QtSvg import QSvgWidget
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QLabel, QPushButton, QFileDialog, 
                                QTextEdit, QFrame, QGraphicsDropShadowEffect, QSizePolicy, QProgressBar, QMessageBox)
    HAS_PYQT5 = True
except ImportError:
    HAS_PYQT5 = False

class InteractiveFolderSelector:
    """Selector de carpetas interactivo multiplataforma (Windows/Linux)."""
    def __init__(self):
        self.current_path = Path(os.getcwd()).resolve()
        self.selected_idx = 0
        self.message = ""

    def _get_key(self):
        """Lee una tecla pulsada sin esperar enter (Cross-platform)."""
        if os.name == 'nt':
            import msvcrt
            key = msvcrt.getch()
            if key == b'\xe0': # Arrow keys prefix
                key = msvcrt.getch()
                if key == b'H': return 'UP'
                if key == b'P': return 'DOWN'
            if key == b'\r': return 'ENTER'
            if key == b' ': return 'SPACE'
            if key == b'\x08': return 'BACKSPACE'
            if key == b'\x1b': return 'ESC'
            return None
        else:
            import tty, termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
                if ch == '\x1b': # Escape sequence
                    seq = sys.stdin.read(2)
                    if seq == '[A': return 'UP'
                    if seq == '[B': return 'DOWN'
                    return 'ESC'
                if ch == '\r': return 'ENTER'
                if ch == ' ': return 'SPACE'
                if ch == '\x7f': return 'BACKSPACE' # Backspace on Mac/Linux often 127
                return None
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def get_subdirs(self):
        # Retorna lista de tuplas (nombre_mostrar, objeto_path, es_accion)
        items = []
        # Opción para seleccionar el directorio actual
        items.append(("[ SELECCIONAR ESTA CARPETA ]", self.current_path, True))
        
        # Opción para subir de nivel
        if self.current_path.parent != self.current_path:
            items.append((".. (Subir nivel)", self.current_path.parent, False))
            
        # Subdirectorios
        try:
            for d in sorted([d for d in self.current_path.iterdir() if d.is_dir() and not d.name.startswith('.')], key=lambda x: x.name):
                items.append((d.name, d, False))
        except Exception as e:
            self.message = f"[ERROR] No se puede leer directorio: {e}"
            
        return items

    def run(self) -> Optional[Path]:
        while True:
            # Limpiar pantalla cross-platform
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("==========================================")
            print("   SELECTOR DE PROYECTO FLANGCOMPILER")
            print("==========================================")
            print(f"Ruta Actual: {self.current_path}")
            print("------------------------------------------")
            print("[ARRIBA/ABAJO] Navegar   [ENTER] Accionar")
            print("[ESC] Salir")
            print("------------------------------------------")

            items = self.get_subdirs()
            
            # Ajustar índice si cambia la lista
            if self.selected_idx >= len(items):
                self.selected_idx = len(items) - 1
            
            # Paginación simple
            max_lines = 15
            start = 0
            if self.selected_idx > max_lines - 1:
                start = self.selected_idx - (max_lines - 1)
            
            visible_items = items[start : start + max_lines]

            for i, item in enumerate(visible_items):
                name, path, is_action = item
                real_idx = start + i
                prefix = " > " if real_idx == self.selected_idx else "   "
                print(f"{prefix}{name}")
            
            print("------------------------------------------")
            if self.message:
                print(self.message)

            key = self._get_key()
            
            if key == 'UP':
                self.selected_idx = max(0, self.selected_idx - 1)
            elif key == 'DOWN':
                self.selected_idx = min(len(items) - 1, self.selected_idx + 1)
            elif key == 'ENTER':
                name, path, is_action = items[self.selected_idx]
                
                if is_action:
                    # Es la acción de seleccionar actual
                    # Verificar details.xml
                    if (path / "details.xml").exists():
                        return path
                    else:
                        self.message = "[!] Advertencia: No se detectó details.xml aquí. Pulsa ENTER de nuevo para confirmar."
                        # Hack simple para confirmación: si el mensaje ya es ese, retornamos
                        if self.message == "[!] Advertencia: No se detectó details.xml aquí. Pulsa ENTER de nuevo para confirmar.":
                             return path
                        return path # Retornamos de una vez por ahora para no complicar
                else:
                    # Es navegación (subir o bajar)
                    self.current_path = path
                    self.selected_idx = 0
                    self.message = ""
                    
            elif key == 'ESC':
                return None

def update_project_files(repo_path: Path):
    """Actualiza README.md, CHANGELOG.md, RELEASE_NOTES.md y lib/requirements.txt."""
    print(f"[INFO] Actualizando archivos del proyecto en {repo_path}...")
    
    # 1. Update requirements.txt
    lib_dir = repo_path / "lib"
    lib_dir.mkdir(exist_ok=True)
    req_file = lib_dir / "requirements.txt"
    
    imports = set()
    for py_file in repo_path.glob("**/*.py"):
        if "venv" in str(py_file) or ".git" in str(py_file): continue
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("import ") or line.startswith("from "):
                        parts = line.split()
                        if len(parts) > 1:
                            module = parts[1].split('.')[0]
                            # Filtro básico de stdlib
                            if module not in ['os', 'sys', 're', 'json', 'pathlib', 'subprocess', 'threading', 'platform', 'shutil', 'typing', 'urllib', 'ssl', 'tempfile', 'xml', 'PyQt5']: 
                                imports.add(module)
        except: pass
    
    try:
        with open(req_file, 'w', encoding='utf-8') as f:
            for imp in sorted(imports):
                f.write(f"{imp}\n")
        print(f"[OK] lib/requirements.txt actualizado ({len(imports)} dependencias detectadas).")
    except Exception as e:
        print(f"[WARN] No se pudo actualizar requirements.txt: {e}")

    # 2. Update MD files (Asegurar existencia)
    for md in ["README.md", "CHANGELOG.md", "RELEASE_NOTES.md"]:
        md_path = repo_path / md
        if not md_path.exists():
            try:
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(f"# {md[:-3]}\n\nGenerado automáticamente por FlangCompiler IT.\n")
                print(f"[OK] {md} creado.")
            except: pass
        else:
            print(f"[OK] {md} verificado.")

class FlangCompiler:
    """Compilador principal unificado para el ecosistema Flarm."""

    def __init__(self, repo_path: str, output_path: Optional[str] = None, progress_callback=None):
        """
        Inicializa el compilador.

        Args:
            repo_path: Ruta al repositorio a compilar.
            output_path: Ruta de salida para los paquetes (por defecto: ./releases).
            progress_callback: Función para reportar progreso (0-100).
        """
        self.repo_path = Path(repo_path).resolve()
        self.output_path = Path(output_path or "./releases").resolve()
        self.progress_callback = progress_callback
        self.details_xml_path = self.repo_path / "details.xml"
        self.metadata = {}
        self.scripts = []
        self.platform_type = None
        self.current_platform = platform.system()  # 'Windows', 'Linux', 'Darwin'
        self.venv_path = None  # Path to virtual environment if created

        # Crear directorio de salida
        self.output_path.mkdir(parents=True, exist_ok=True)

        print(f"[FlangCompiler IT] Inicializado en: {self.repo_path}")
        print(f"[FlangCompiler IT] Plataforma actual: {self.current_platform}")

    def _report_progress(self, value: int):
        if self.progress_callback:
            self.progress_callback(value)

    def _check_pyinstaller_installed(self) -> bool:
        """
        Verifica si PyInstaller está instalado en el sistema.
        
        Returns:
            True si PyInstaller está disponible, False en caso contrario.
        """
        try:
            result = subprocess.run(
                ["pyinstaller", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"[INFO] PyInstaller encontrado: {result.stdout.strip()}")
                return True
            return False
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            print(f"[INFO] PyInstaller no encontrado: {e}")
            return False

    def _install_pyinstaller_linux(self) -> bool:
        """
        Instala PyInstaller en Linux usando un entorno virtual.
        
        Returns:
            True si la instalación fue exitosa, False en caso contrario.
        """
        print("[INFO] 🔧 Instalando PyInstaller en Linux...")
        
        # Crear script de instalación bash
        install_script = """#!/bin/bash
echo "🔧 Instalando python3-full, python3-venv y pipx..."
sudo apt install -y python3-full python3-venv pipx

echo "🔧 Configurando pipx..."
pipx ensurepath

VENV_DIR="$HOME/venv-pyinstaller"
if [ ! -d "$VENV_DIR" ]; then
    echo "🧪 Creando entorno virtual en $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
else
    echo "🔁 El entorno virtual ya existe en $VENV_DIR."
fi

echo "🚀 Activando entorno virtual..."
source "$VENV_DIR/bin/activate"

echo "📦 Instalando PyInstaller..."
pip install --upgrade pip
pip install pyinstaller

echo "✅ PyInstaller instalado. Versión:"
pyinstaller --version

echo "🎉 Entorno listo. Puedes usar PyInstaller dentro del entorno virtual."
"""
        
        try:
            # Crear archivo temporal para el script
            script_path = Path(tempfile.gettempdir()) / "install_pyinstaller.sh"
            
            with open(script_path, 'w', newline='\n') as f:
                f.write(install_script)
            
            # Hacer el script ejecutable
            os.chmod(script_path, 0o755)
            
            print(f"[INFO] Ejecutando script de instalación: {script_path}")
            
            # Ejecutar el script
            result = subprocess.run(
                ["bash", str(script_path)],
                capture_output=False,
                text=True
            )
            
            # Limpiar script temporal
            try:
                script_path.unlink()
            except Exception:
                pass
            
            if result.returncode != 0:
                print(f"[ERROR] Error durante la instalación de PyInstaller")
                return False
            
            # Verificar que el entorno virtual fue creado
            venv_dir = Path.home() / "venv-pyinstaller"
            self.venv_path = venv_dir
            
            if not venv_dir.exists():
                print(f"[ERROR] El entorno virtual no fue creado en {venv_dir}")
                return False
            
            # Verificar que PyInstaller fue instalado
            pyinstaller_path = venv_dir / "bin" / "pyinstaller"
            if not pyinstaller_path.exists():
                print(f"[ERROR] PyInstaller no fue instalado en {pyinstaller_path}")
                return False
            
            print(f"[OK] ✅ PyInstaller instalado correctamente en {venv_dir}")
            return True
                
        except Exception as e:
            print(f"[ERROR] Excepción durante la instalación de PyInstaller: {e}")
            return False

    def _ensure_pyinstaller(self) -> bool:
        """
        Asegura que PyInstaller esté disponible. Si no está instalado en Linux,
        lo instala automáticamente.
        
        Returns:
            True si PyInstaller está disponible, False en caso contrario.
        """
        # Verificar si PyInstaller ya está instalado
        if self._check_pyinstaller_installed():
            return True
        
        # Si no está instalado y estamos en Linux, intentar instalarlo
        if self.current_platform == "Linux":
            print("[INFO] PyInstaller no encontrado. Iniciando instalación automática...")
            return self._install_pyinstaller_linux()
        else:
            print(f"[ERROR] PyInstaller no encontrado y la instalación automática solo está disponible en Linux.")
            print(f"[ERROR] Por favor, instale PyInstaller manualmente: pip install pyinstaller")
            return False

    def parse_details_xml(self) -> bool:
        """
        Analiza el archivo details.xml y extrae metadatos.

        Returns:
            True si el análisis fue exitoso, False en caso contrario.
        """
        if not self.details_xml_path.exists():
            print(f"[ERROR] No se encontró details.xml en {self.repo_path}")
            return False

        try:
            tree = ET.parse(self.details_xml_path)
            root = tree.getroot()

            # Extraer metadatos
            self.metadata = {
                'publisher': root.findtext('publisher', 'Unknown'),
                'app': root.findtext('app', 'Unknown'),
                'name': root.findtext('name', 'Unknown'),
                'version': root.findtext('version', 'v1.0'),
                'platform': root.findtext('platform', 'AlphaCube'),
                'author': root.findtext('author', 'Unknown'),
                'rate': root.findtext('rate', 'Todas las edades'),
            }

            self.platform_type = self.metadata['platform']

            print(f"[INFO] Metadatos extraídos:")
            print(f"  - Publicador: {self.metadata['publisher']}")
            print(f"  - Aplicación: {self.metadata['app']}")
            print(f"  - Versión: {self.metadata['version']}")
            print(f"  - Plataforma: {self.platform_type}")

            return True

        except ET.ParseError as e:
            print(f"[ERROR] Error al parsear details.xml: {e}")
            return False

    def find_scripts(self) -> bool:
        """
        Identifica los scripts Python en la raíz del repositorio.

        Returns:
            True si se encontraron scripts, False en caso contrario.
        """
        # Buscar el script principal basado en el campo 'app' del XML
        main_script = f"{self.metadata['app']}.py"
        main_script_path = self.repo_path / main_script

        if main_script_path.exists():
            self.scripts.append({
                'name': self.metadata['app'],
                'path': main_script_path,
                'icon': self._find_icon(self.metadata['app']),
                'is_main': True,
            })
            print(f"[INFO] Script principal encontrado: {main_script}")
        else:
            print(f"[WARN] Script principal no encontrado: {main_script}")

        # Buscar scripts secundarios en la raíz
        for file in self.repo_path.glob("*.py"):
            if file.name != main_script and not file.name.startswith("_") and file.name != "compiler_full.py":
                script_name = file.stem
                self.scripts.append({
                    'name': script_name,
                    'path': file,
                    'icon': self._find_icon(script_name),
                    'is_main': False,
                })
                print(f"[INFO] Script secundario encontrado: {file.name}")

        return len(self.scripts) > 0

    def _find_icon(self, script_name: str) -> Optional[Path]:
        """
        Busca el icono correspondiente a un script.

        Args:
            script_name: Nombre del script (sin extensión).

        Returns:
            Ruta al icono si existe, None en caso contrario.
        """
        app_dir = self.repo_path / "app"
        if not app_dir.exists():
            return None

        # Buscar icono específico del script
        icon_path = app_dir / f"{script_name}-icon.ico"
        if icon_path.exists():
            return icon_path

        # Para el script principal, buscar app-icon.ico
        if script_name == self.metadata['app']:
            icon_path = app_dir / "app-icon.ico"
            if icon_path.exists():
                return icon_path

        return None

    def should_compile_for_platform(self, target_platform: str) -> bool:
        """
        Determina si se debe compilar para una plataforma específica.

        Args:
            target_platform: Plataforma de destino ('Windows', 'Linux').

        Returns:
            True si se debe compilar, False en caso contrario.
        """
        if self.platform_type == "AlphaCube":
            # AlphaCube compila para ambas plataformas
            return True
        elif self.platform_type == "Knosthalij":
            # Knosthalij solo compila para Windows
            return target_platform == "Windows"
        elif self.platform_type == "Danenone":
            # Danenone solo compila para Linux
            return target_platform == "Linux"
        else:
            print(f"[WARN] Plataforma desconocida: {self.platform_type}")
            return False

    def compile_binaries(self, target_platform: str) -> bool:
        """
        Compila los scripts a binarios para la plataforma especificada.

        Args:
            target_platform: Plataforma de destino ('Windows', 'Linux').

        Returns:
            True si la compilación fue exitosa, False en caso contrario.
        """
        if not self.should_compile_for_platform(target_platform):
            print(f"[INFO] Compilación para {target_platform} no requerida (plataforma: {self.platform_type})")
            return True

        if target_platform == "Windows" and self.current_platform != "Windows":
            print(f"[SKIP] No se puede compilar para Windows desde {self.current_platform}. Se omite.")
            return True # Retornamos True para no detener el proceso global

        if target_platform == "Linux" and self.current_platform != "Linux":
            print(f"[SKIP] No se puede compilar para Linux desde {self.current_platform}. Se omite.")
            return True

        # Asegurar que PyInstaller esté disponible
        if not self._ensure_pyinstaller():
            print("[ERROR] No se puede continuar sin PyInstaller.")
            return False

        print(f"[INFO] Iniciando compilación para {target_platform}...")

        for script in self.scripts:
            print(f"[INFO] Compilando script: {script['name']}...")
            if target_platform == "Windows":
                if not self._compile_windows_binary(script):
                    return False
            elif target_platform == "Linux":
                if not self._compile_linux_binary(script):
                    return False

        return True

    def _compile_windows_binary(self, script: Dict) -> bool:
        """
        Compila un script a un ejecutable de Windows (.exe).
        """
        script_path = script['path']
        script_name = script['name']
        icon_arg = ""

        if script['icon']:
            icon_arg = f"--icon {script['icon']}"

        # Comando de compilación
        # Construir comando como lista para mejor manejo de argumentos
        # Usar PyInstaller del entorno virtual si está disponible
        pyinstaller_cmd = "pyinstaller"
        if self.venv_path and self.current_platform == "Linux":
            pyinstaller_cmd = str(self.venv_path / "bin" / "pyinstaller")
        
        cmd = [
            pyinstaller_cmd,
            "--onefile",
            "--windowed",
            "--name", script_name,
            "--add-data", "assets;assets",
            "--add-data", "app;app",
        ]
        
        if script['icon']:
            cmd.extend(["--icon", str(script['icon'])])
            
        cmd.append(str(script_path))

        print(f"[DEBUG] Ejecutando PyInstaller para {script_name}...")

        try:
            # Usar shell=False y pasar lista
            # El usuario pidió "debug pero sin mostrar la salida del pyinstaller"
            # Así que mostramos que estamos trabajando pero ocultamos stdout a menos que falle
            print(f"[DEBUG] Ejecutando PyInstaller (Salida oculta)...")
            result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"[ERROR] Falló PyInstaller para {script_name}:\n{result.stderr}")
                return False
            
            # Si hay éxito, no mostramos el stdout gigante de pyinstaller
            print(f"[OK] {script_name} compilado correctamente.")
            return True
        except Exception as e:
            print(f"[ERROR] Excepción al ejecutar PyInstaller: {e}")
            return False

    def _compile_linux_binary(self, script: Dict) -> bool:
        """
        Compila un script a un ejecutable de Linux.
        """
        script_path = script['path']
        script_name = script['name']

        # Comando de compilación (sin icono para Linux, separador :)
        # Construir comando como lista
        # Usar PyInstaller del entorno virtual si está disponible
        pyinstaller_cmd = "pyinstaller"
        if self.venv_path:
            pyinstaller_cmd = str(self.venv_path / "bin" / "pyinstaller")
        
        cmd = [
            pyinstaller_cmd,
            "--onefile",
            "--name", script_name,
            "--add-data", "assets:assets",
            "--add-data", "app:app",
            str(script_path)
        ]

        print(f"[DEBUG] Ejecutando PyInstaller para {script_name}...")

        try:
            print(f"[DEBUG] Ejecutando PyInstaller (Salida oculta)...")
            result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"[ERROR] Falló PyInstaller para {script_name}:\n{result.stderr}")
                return False
            print(f"[OK] {script_name} compilado correctamente.")
            return True
        except Exception as e:
            print(f"[ERROR] Excepción al ejecutar PyInstaller: {e}")
            return False

    def _generate_windows_build_commands(self) -> bool:
        """
        Genera comandos de compilación para Windows (batch script).
        """
        build_script_path = self.output_path / "build_windows.bat"

        with open(build_script_path, 'w') as f:
            f.write("@echo off\n")
            f.write("REM FlangCompiler IT - Comandos de compilación para Windows\n\n")

            for script in self.scripts:
                script_path = script['path']
                script_name = script['name']
                icon_arg = ""

                if script['icon']:
                    icon_arg = f"--icon {script['icon']}"

                cmd = (
                    f"pyinstaller --onefile --windowed --name {script_name} "
                    f"--add-data \"assets;assets\" --add-data \"app;app\" "
                    f"{icon_arg} {script_path}"
                )

                f.write(f"echo Compilando {script_name}...\n")
                f.write(f"{cmd}\n\n")

        print(f"[INFO] Archivo de compilación generado: {build_script_path}")
        return True

    def _generate_linux_build_commands(self) -> bool:
        """
        Genera comandos de compilación para Linux (bash script).
        """
        build_script_path = self.output_path / "build_linux.sh"

        with open(build_script_path, 'w', newline='\n') as f:
            f.write("#!/bin/bash\n")
            f.write("# FlangCompiler IT - Comandos de compilación para Linux\n\n")

            for script in self.scripts:
                script_path = script['path']
                script_name = script['name']

                cmd = (
                    f"pyinstaller --onefile --name {script_name} "
                    f"--add-data \"assets:assets\" --add-data \"app:app\" "
                    f"{script_path}"
                )

                f.write(f"echo 'Compilando {script_name}...'\n")
                f.write(f"{cmd}\n\n")

        # Intentar hacer el script ejecutable (puede fallar en Windows, no es crítico)
        try:
            os.chmod(build_script_path, 0o755)
        except Exception:
            pass
            
        print(f"[INFO] Archivo de compilación generado: {build_script_path}")
        return True

    def create_package(self, target_platform: str) -> bool:
        """
        Crea un paquete con los binarios compilados.

        Args:
            target_platform: Plataforma de destino ('Windows', 'Linux').

        Returns:
            True si la creación fue exitosa, False en caso contrario.
        """
        if not self.should_compile_for_platform(target_platform):
            return True

        print(f"[INFO] Creando paquete para {target_platform}...")

        # Determinar el sufijo de plataforma
        platform_suffix = "Knosthalij" if target_platform == "Windows" else "Danenone"

        # Nombre del paquete: publisher.app.version.platform
        package_name = f"{self.metadata['publisher']}.{self.metadata['app']}.{self.metadata['version']}.{platform_suffix}"
        package_path = self.output_path / package_name

        # Crear directorio del paquete
        package_path.mkdir(parents=True, exist_ok=True)

        # Copiar archivos relevantes
        self._copy_package_files(package_path, target_platform)

        # Copiar y actualizar details.xml
        self._update_and_copy_details_xml(package_path, platform_suffix)

        print(f"[INFO] Paquete creado: {package_path}")
        return True

    def _parse_gitignore(self) -> List[str]:
        """
        Lee el archivo .gitignore y devuelve una lista de patrones.
        """
        gitignore_path = self.repo_path / ".gitignore"
        patterns = []
        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Normalizar patrones para fnmatch (aproximación simple)
                            # Eliminar barras iniciales/finales para coincidir con nombres de archivo/dir
                            clean_line = line.strip('/')
                            if clean_line:
                                patterns.append(clean_line)
                print(f"[INFO] .gitignore encontrado. Patrones cargados: {len(patterns)}")
            except Exception as e:
                print(f"[WARN] Error leyendo .gitignore: {e}")
        return patterns

    def _copy_package_files(self, package_path: Path, target_platform: str) -> None:
        """
        Copia los archivos relevantes al paquete.
        """
        # Archivos a excluir por defecto
        exclude_patterns = [
            "requirements.txt",
            "*.sh" if target_platform == "Windows" else "*.bat",
            "*.pyc",
            "__pycache__",
            ".git",
            ".gitignore",
            "build",
            "dist",
            "*.spec",
            "compiler_full.py",
            "compiler.py",
            "linux_compiler.py",
            "windows_compiler.py"
        ]

        # Agregar patrones del .gitignore
        exclude_patterns.extend(self._parse_gitignore())

        # Agregar *.py para eliminar scripts del paquete compilado
        # (El usuario solicitó eliminar scripts después de compilar)
        exclude_patterns.append("*.py")

        # Función auxiliar para verificar si un nombre debe ser ignorado
        def is_ignored(name):
            for pattern in exclude_patterns:
                if fnmatch.fnmatch(name, pattern):
                    return True
            return False

        # Copiar archivos del repositorio
        for item in self.repo_path.iterdir():
            # Verificar si el archivo/directorio está ignorado
            if is_ignored(item.name):
                continue

            if item.name in ["details.xml", "README.md", "LICENSE", "CHANGELOG.md"]:
                if item.is_file():
                    shutil.copy2(item, package_path / item.name)
            elif item.is_dir() and item.name not in ["releases"]: # releases ya debería estar ignorado por lógica o .gitignore, pero por seguridad
                # Copiar directorios (assets, app, etc.)
                dest_dir = package_path / item.name
                if dest_dir.exists():
                    shutil.rmtree(dest_dir)
                
                # Usar shutil.ignore_patterns que soporta globs
                # Nota: shutil.ignore_patterns crea una función que usa fnmatch
                try:
                    shutil.copytree(item, dest_dir, ignore=shutil.ignore_patterns(*exclude_patterns))
                except Exception as e:
                    print(f"[WARN] Error copiando directorio {item.name}: {e}")

        # Mover binarios compilados desde dist/ al paquete
        dist_dir = self.repo_path / "dist"
        if dist_dir.exists():
            for binary in dist_dir.iterdir():
                # En Windows copiamos .exe, en Linux binarios sin extensión
                if target_platform == "Windows" and binary.suffix == ".exe":
                     shutil.copy2(binary, package_path / binary.name)
                elif target_platform == "Linux" and binary.suffix == "":
                     shutil.copy2(binary, package_path / binary.name)
                     # Asegurar permisos de ejecución
                     (package_path / binary.name).chmod(0o755)

        print(f"[INFO] Archivos copiados al paquete (Scripts Python excluidos)")

    def _update_and_copy_details_xml(self, package_path: Path, platform_suffix: str) -> None:
        """
        Copia y actualiza el details.xml con la plataforma correcta.
        """
        try:
            tree = ET.parse(self.details_xml_path)
            root = tree.getroot()

            # Actualizar la rama 'platform'
            platform_elem = root.find('platform')
            if platform_elem is not None:
                platform_elem.text = platform_suffix
            else:
                platform_elem = ET.SubElement(root, 'platform')
                platform_elem.text = platform_suffix

            # Guardar el XML actualizado
            output_xml_path = package_path / "details.xml"
            tree.write(output_xml_path, encoding='utf-8', xml_declaration=True)

            print(f"[INFO] details.xml actualizado con plataforma: {platform_suffix}")

        except Exception as e:
            print(f"[ERROR] Error actualizando details.xml: {e}")

    def compress_to_iflapp(self, package_path: Path, output_file: Path) -> bool:
        """
        Comprime el directorio del paquete en un archivo .iflapp (zip).
        """
        print(f"[INFO] Empaquetando {package_path.name} en .iflapp...")
        try:
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(package_path):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(package_path)
                        zipf.write(file_path, arcname)
            print(f"[OK] Archivo .iflapp creado: {output_file}")
            return True
        except Exception as e:
            print(f"[ERROR] Error creando .iflapp: {e}")
            return False

    def run(self) -> Optional[Path]:
        """
        Ejecuta el flujo completo. Retorna la ruta del paquete creado (directorio) si es exitoso.
        """
        self._report_progress(5)
        # Paso 1: Analizar details.xml
        if not self.parse_details_xml():
            return None
        
        self._report_progress(10)

        # Paso 2: Encontrar scripts
        if not self.find_scripts():
            print(f"[WARN] No se encontraron scripts Python")
            return None
            
        self._report_progress(15)

        # Paso 3: Compilar binarios y crear paquetes
        platforms_to_compile = []
        
        # Lógica estricta de plataforma
        if self.current_platform == "Windows":
            if self.should_compile_for_platform("Windows"):
                platforms_to_compile.append("Windows")
        elif self.current_platform == "Linux":
            if self.should_compile_for_platform("Linux"):
                platforms_to_compile.append("Linux")
        
        if not platforms_to_compile:
            print("[WARN] No hay plataformas compatibles para compilar.")
            return None

        last_package_path = None
        total_steps = len(platforms_to_compile) * 2 # Compilar + Crear paquete
        current_step = 0
        
        for platform_name in platforms_to_compile:
            # Calcular progreso base (20% a 90%)
            progress_base = 20 + (current_step / total_steps) * 70
            self._report_progress(int(progress_base))
            
            if not self.compile_binaries(platform_name):
                print(f"[WARN] Error compilando para {platform_name}")
                return None
            
            current_step += 1
            progress_base = 20 + (current_step / total_steps) * 70
            self._report_progress(int(progress_base))

            if not self.create_package(platform_name):
                print(f"[WARN] Error creando paquete para {platform_name}")
                return None
            
            current_step += 1
            
            # Determinar ruta del paquete creado
            platform_suffix = "Knosthalij" if platform_name == "Windows" else "Danenone"
            package_name = f"{self.metadata['publisher']}.{self.metadata['app']}.{self.metadata['version']}.{platform_suffix}"
            last_package_path = self.output_path / package_name
            
            # Comprimir a .iflapp
            iflapp_name = f"{package_name}.iflapp"
            iflapp_path = self.output_path / iflapp_name
            if not self.compress_to_iflapp(last_package_path, iflapp_path):
                 print(f"[WARN] Error comprimiendo paquete para {platform_name}")
                 return None

        self._report_progress(100)
        print(f"[INFO] Proceso de compilación completado.")
        return iflapp_path


# Clases que dependen de PyQt5 - solo se definen si está disponible
if HAS_PYQT5:
    class CompilationWorker(QThread):
        """Hilo de trabajo para la compilación asíncrona."""
        finished = pyqtSignal(bool, str)
        progress = pyqtSignal(int)

        def __init__(self, repo_path, output_path):
            super().__init__()
            self.repo_path = repo_path
            self.output_path = output_path
            self.compiler = None

        def run(self):
            self.compiler = FlangCompiler(self.repo_path, self.output_path, progress_callback=self.progress.emit)
            result_path = self.compiler.run()
            self.finished.emit(result_path is not None, str(result_path) if result_path else "")


    class StreamRedirector(QObject):
        """Redirige stdout/stderr a una señal Qt."""
        text_written = pyqtSignal(str)

        def write(self, text):
            self.text_written.emit(str(text))

        def flush(self):
            pass

    class Win11Button(QPushButton):
        """Botón estilo Windows 11 (Accent Color)."""
        def __init__(self, text, parent=None, is_primary=True):
            super().__init__(text, parent)
            self.setCursor(Qt.PointingHandCursor)
            self.setFixedHeight(36)
            self.setFont(QFont("Segoe UI Variable Display", 9))
            
            self.is_primary = is_primary
            self.update_style()

        def update_style(self):
            if self.is_primary:
                # Estilo Accent (Azul)
                self.setStyleSheet("""
                    QPushButton {
                        background-color: #0078D4;
                        color: white;
                        border-radius: 4px;
                        border: 1px solid #0078D4;
                        padding: 0 16px;
                    }
                    QPushButton:hover {
                        background-color: #1084D9;
                        border: 1px solid #1084D9;
                    }
                    QPushButton:pressed {
                        background-color: #006CC1;
                        border: 1px solid #006CC1;
                    }
                    QPushButton:disabled {
                        background-color: #333333;
                        color: #888888;
                        border: 1px solid #333333;
                    }
                """)
            else:
                # Estilo Standard (Gris Oscuro)
                self.setStyleSheet("""
                    QPushButton {
                        background-color: #2D2D2D;
                        color: white;
                        border-radius: 4px;
                        border: 1px solid #3D3D3D;
                        padding: 0 16px;
                    }
                    QPushButton:hover {
                        background-color: #3D3D3D;
                        border: 1px solid #4D4D4D;
                    }
                    QPushButton:pressed {
                        background-color: #262626;
                        border: 1px solid #262626;
                    }
                """)

    class TitleBarButton(QPushButton):
        """Botón de barra de título (Min, Max, Close)."""
        def __init__(self, icon_path, parent=None, is_close=False):
            super().__init__(parent)
            self.setFixedSize(46, 32)
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(10, 10))
            self.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                }
                QPushButton:hover {
                    background-color: %s;
                }
                QPushButton:pressed {
                    background-color: %s;
                }
            """ % ("#C42B1C" if is_close else "#333333", "#B32415" if is_close else "#262626"))

    class OutputTerminal(QTextEdit):
        """Terminal de solo salida para logs del compilador."""

        def __init__(self, parent=None):
            super().__init__(parent)
            self.setReadOnly(True)  # Solo lectura
            self.setStyleSheet("""
                QTextEdit { 
                    background-color: #012456; 
                    border-radius: 4px; 
                    border: 1px solid #333333;
                    padding: 10px;
                    color: #CCCCCC;
                    font-family: 'Consolas', 'Lucida Console', monospace;
                    font-size: 14px;
                }
            """)
            self.append("[INFO] Terminal de salida inicializada.")
            self.append("[INFO] Esperando selección de proyecto...\n")

        def write_output(self, text):
            """Método para escribir salida programática (logs) con soporte ANSI."""
            from PyQt5.QtGui import QTextCharFormat, QColor
            
            # Mover al final
            cursor = self.textCursor()
            cursor.movePosition(cursor.End)
            
            # Si no estamos en una línea nueva, insertar salto
            if cursor.positionInBlock() > 0:
                cursor.insertText("\n")
            
            # Parsear y aplicar colores ANSI
            ansi_pattern = re.compile(r'\[([A-ZÉÍ]+)\]')
            parts = ansi_pattern.split(text)
            
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    # Texto normal
                    cursor.insertText(part)
                else:
                    # Es un tag de color
                    fmt = QTextCharFormat()
                    fmt.setFontWeight(700)  # Bold
                    
                    if part == "INFO":
                        fmt.setForeground(QColor("#3B9CFF"))  # Azul
                        cursor.insertText(f"[{part}]", fmt)
                    elif part in ["OK", "ÉXITO"]:
                        fmt.setForeground(QColor("#00D26A"))  # Verde
                        cursor.insertText(f"[{part}]", fmt)
                    elif part == "WARN":
                        fmt.setForeground(QColor("#FFB627"))  # Amarillo
                        cursor.insertText(f"[{part}]", fmt)
                    elif part in ["ERROR", "CRÍTICO"]:
                        fmt.setForeground(QColor("#FF4444"))  # Rojo
                        cursor.insertText(f"[{part}]", fmt)
                    else:
                        cursor.insertText(f"[{part}]")
            
            self.setTextCursor(cursor)
            self.ensureCursorVisible()

    class CompilerGUI(QMainWindow):
        """Interfaz gráfica estilo Windows 11 para el compilador."""
        def __init__(self):
            super().__init__()
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint)
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.resize(950, 650)
            
            self.repo_path = ""
            self.output_path = ""
            self.compiler_thread = None
            
            self.init_ui()
            
            # Redirigir stdout
            self.redirector = StreamRedirector()
            self.redirector.text_written.connect(self.append_log)
            sys.stdout = self.redirector
            sys.stderr = self.redirector

        def init_ui(self):
            # Widget central (Fondo Mica simulado)
            self.central_widget = QWidget()
            self.central_widget.setObjectName("CentralWidget")
            self.central_widget.setStyleSheet("""
                #CentralWidget {
                    background-color: #202020;
                    border: 1px solid #333333;
                    border-radius: 8px;
                }
                QLabel { color: #FFFFFF; font-family: 'Segoe UI Variable Display'; }
                QTextEdit { 
                    background-color: #0C0C0C; 
                    border-radius: 4px; 
                    border: 1px solid #333333;
                    padding: 10px;
                    color: #CCCCCC;
                    font-family: 'Consolas';
                    font-size: 13px;
                }
            """)
            self.setCentralWidget(self.central_widget)
            
            # Layout principal
            main_layout = QVBoxLayout(self.central_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)

            # --- Barra de Título ---
            title_bar = QHBoxLayout()
            title_bar.setContentsMargins(16, 0, 0, 0)
            title_bar.setSpacing(0)
            
            # Icono y Título
            app_icon = QSvgWidget("assets/ui/win11_terminal.svg")
            app_icon.setFixedSize(16, 16)
            title_bar.addWidget(app_icon)
            
            title_bar.addSpacing(12)
            
            title_label = QLabel("Flarm Package Compiler")
            title_label.setFont(QFont("Segoe UI Variable Display", 9))
            title_label.setStyleSheet("color: #FFFFFF;")
            title_bar.addWidget(title_label)
            
            title_bar.addStretch()
            
            # Botones de ventana
            min_btn = TitleBarButton("assets/ui/win11_min.svg")
            min_btn.clicked.connect(self.showMinimized)
            
            self.max_btn = TitleBarButton("assets/ui/win11_max.svg")
            self.max_btn.clicked.connect(self.toggle_maximized)
            
            close_btn = TitleBarButton("assets/ui/win11_close.svg", is_close=True)
            close_btn.clicked.connect(self.close)
            
            title_bar.addWidget(min_btn)
            title_bar.addWidget(self.max_btn)
            title_bar.addWidget(close_btn)
            
            # Contenedor de la barra de título para eventos de arrastre
            self.title_bar_widget = QWidget()
            self.title_bar_widget.setLayout(title_bar)
            self.title_bar_widget.setFixedHeight(32)
            main_layout.addWidget(self.title_bar_widget)

            # --- Área de Contenido ---
            content_layout = QHBoxLayout()
            content_layout.setContentsMargins(24, 12, 24, 24)
            content_layout.setSpacing(24)
            
            # Panel Izquierdo (Configuración)
            left_panel = QVBoxLayout()
            left_panel.setSpacing(20)
            
            # Header Sección
            config_header = QLabel("Configuración")
            config_header.setFont(QFont("Segoe UI Variable Display", 14, QFont.Bold))
            left_panel.addWidget(config_header)

            # Grupo Repositorio
            repo_group = QVBoxLayout()
            repo_group.setSpacing(8)
            repo_label = QLabel("Repositorio de Origen")
            repo_label.setStyleSheet("color: #CCCCCC; font-size: 13px;")
            repo_group.addWidget(repo_label)
            
            repo_row = QHBoxLayout()
            self.repo_display = QLabel("Seleccionar carpeta...")
            self.repo_display.setStyleSheet("""
                background-color: #2D2D2D; 
                border-radius: 4px; 
                padding: 8px 12px; 
                color: #AAAAAA;
                border: 1px solid #3D3D3D;
            """)
            self.repo_display.setFixedHeight(36)
            repo_row.addWidget(self.repo_display, 1)
            
            repo_btn = Win11Button("Examinar", is_primary=False)
            repo_btn.setIcon(QIcon("assets/ui/win11_folder.svg"))
            repo_btn.clicked.connect(self.select_repo)
            repo_row.addWidget(repo_btn)
            
            repo_group.addLayout(repo_row)
            left_panel.addLayout(repo_group)
            
            # Grupo Salida
            out_group = QVBoxLayout()
            out_group.setSpacing(8)
            out_label = QLabel("Directorio de Salida")
            out_label.setStyleSheet("color: #CCCCCC; font-size: 13px;")
            out_group.addWidget(out_label)
            
            out_row = QHBoxLayout()
            self.out_display = QLabel("./releases")
            self.out_display.setStyleSheet("""
                background-color: #2D2D2D; 
                border-radius: 4px; 
                padding: 8px 12px; 
                color: #FFFFFF;
                border: 1px solid #3D3D3D;
            """)
            self.out_display.setFixedHeight(36)
            out_row.addWidget(self.out_display, 1)
            
            out_btn = Win11Button("Cambiar", is_primary=False)
            out_btn.setIcon(QIcon("assets/ui/win11_folder.svg"))
            out_btn.clicked.connect(self.select_output)
            out_row.addWidget(out_btn)
            
            out_group.addLayout(out_row)
            left_panel.addLayout(out_group)
            
            left_panel.addStretch()
            
            # Botón Compilar
            self.compile_btn = Win11Button("Iniciar Compilación", is_primary=True)
            self.compile_btn.setFixedHeight(40)
            self.compile_btn.setFont(QFont("Segoe UI Variable Display", 10, QFont.Bold))
            self.compile_btn.clicked.connect(self.start_compilation)
            self.compile_btn.setEnabled(False)
            left_panel.addWidget(self.compile_btn)
            
            # Barra de Progreso
            self.progress_bar = QProgressBar()
            self.progress_bar.setFixedHeight(6)
            self.progress_bar.setTextVisible(False)
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    background-color: #2D2D2D;
                    border-radius: 3px;
                    border: none;
                }
                QProgressBar::chunk {
                    background-color: #0078D4;
                    border-radius: 3px;
                }
            """)
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
            left_panel.addWidget(self.progress_bar)

            content_layout.addLayout(left_panel, 3)

            # Panel Derecho (Terminal)
            right_panel = QVBoxLayout()
            right_panel.setSpacing(12)
            
            log_header = QLabel("Salida de Terminal")
            log_header.setFont(QFont("Segoe UI Variable Display", 14, QFont.Bold))
            right_panel.addWidget(log_header)
            
            self.log_area = OutputTerminal()
            right_panel.addWidget(self.log_area)
            
            content_layout.addLayout(right_panel, 7)
            
            main_layout.addLayout(content_layout)

            # Permitir mover la ventana desde la barra de título
            self.old_pos = None

        def toggle_maximized(self):
            """Alterna entre ventana maximizada y normal."""
            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized()

        def changeEvent(self, event):
            """Maneja cambios de estado de la ventana."""
            if event.type() == QEvent.WindowStateChange:
                if self.isMaximized():
                    # Sin bordes cuando está maximizada
                    self.central_widget.setStyleSheet("""
                        #CentralWidget {
                            background-color: #202020;
                            border: none;
                            border-radius: 0px;
                        }
                        QLabel { color: #FFFFFF; font-family: 'Segoe UI Variable Display'; }
                        QTextEdit { 
                            background-color: #0C0C0C; 
                            border-radius: 4px; 
                            border: 1px solid #333333;
                            padding: 10px;
                            color: #CCCCCC;
                            font-family: 'Consolas';
                            font-size: 13px;
                        }
                    """)
                else:
                    # Con bordes cuando está en modo normal
                    self.central_widget.setStyleSheet("""
                        #CentralWidget {
                            background-color: #202020;
                            border: 1px solid #333333;
                            border-radius: 8px;
                        }
                        QLabel { color: #FFFFFF; font-family: 'Segoe UI Variable Display'; }
                        QTextEdit { 
                            background-color: #0C0C0C; 
                            border-radius: 4px; 
                            border: 1px solid #333333;
                            padding: 10px;
                            color: #CCCCCC;
                            font-family: 'Consolas';
                            font-size: 13px;
                        }
                    """)
            super().changeEvent(event)

        def mousePressEvent(self, event):
            # Solo permitir arrastrar desde la barra superior (aprox 40px)
            if event.button() == Qt.LeftButton and event.y() < 40:
                self.old_pos = event.globalPos()

        def mouseMoveEvent(self, event):
            if self.old_pos:
                delta = QPoint(event.globalPos() - self.old_pos)
                self.move(self.x() + delta.x(), self.y() + delta.y())
                self.old_pos = event.globalPos()

        def mouseReleaseEvent(self, event):
            if event.button() == Qt.LeftButton:
                self.old_pos = None

        def validate_project_xml(self, repo_path):
            """Valida que el proyecto tenga un details.xml válido con todos los campos requeridos."""
            details_xml = Path(repo_path) / "details.xml"
            
            if not details_xml.exists():
                self.log("[ERROR] No se encontró el archivo details.xml en el proyecto.")
                self.log("[ERROR] El proyecto fue rechazado.")
                return False
            
            try:
                tree = ET.parse(details_xml)
                root = tree.getroot()
                
                # Verificar que el root sea <app>
                if root.tag != 'app':
                    self.log("[ERROR] El archivo details.xml debe tener <app> como elemento raíz.")
                    self.log("[ERROR] El proyecto fue rechazado.")
                    return False
                
                # Campos requeridos según la estructura real
                required_fields = {
                    'publisher': 'Editor/Publicador',
                    'app': 'Nombre de la aplicación',
                    'name': 'Nombre completo',
                    'version': 'Versión',
                    'correlationid': 'ID de correlación',
                    'rate': 'Clasificación',
                    'author': 'Autor',
                    'platform': 'Plataforma'
                }
                
                missing_fields = []
                empty_fields = []
                
                for field, description in required_fields.items():
                    element = root.find(field)
                    if element is None:
                        missing_fields.append(f"  - {field} ({description})")
                    elif not element.text or element.text.strip() == "":
                        empty_fields.append(f"  - {field} ({description})")
                
                if missing_fields or empty_fields:
                    self.log("[ERROR] El archivo details.xml está incompleto:")
                    if missing_fields:
                        self.log("[ERROR] Campos faltantes:")
                        for field in missing_fields:
                            self.log(f"[ERROR] {field}")
                    if empty_fields:
                        self.log("[ERROR] Campos vacíos:")
                        for field in empty_fields:
                            self.log(f"[ERROR] {field}")
                    self.log("[ERROR] El proyecto fue rechazado.")
                    return False
                
                # Verificar que exista el script principal ({app}.py)
                app_name = root.findtext('app', '').strip()
                if app_name:
                    main_script = Path(repo_path) / f"{app_name}.py"
                    if not main_script.exists():
                        self.log(f"[ERROR] No se encontró el script principal: {app_name}.py")
                        self.log("[ERROR] El proyecto fue rechazado.")
                        return False
                    else:
                        self.log(f"[OK] Script principal encontrado: {app_name}.py")
                
                self.log("[OK] Validación de details.xml exitosa.")
                self.log(f"[INFO] Proyecto: {root.findtext('name', 'Unknown')}")
                self.log(f"[INFO] Versión: {root.findtext('version', 'Unknown')}")
                self.log(f"[INFO] Plataforma: {root.findtext('platform', 'Unknown')}")
                self.log(f"[INFO] Autor: {root.findtext('author', 'Unknown')}")
                return True
                
            except ET.ParseError as e:
                self.log(f"[ERROR] Error al parsear details.xml: {e}")
                self.log("[ERROR] El archivo XML está mal formado.")
                self.log("[ERROR] El proyecto fue rechazado.")
                return False
            except Exception as e:
                self.log(f"[ERROR] Error inesperado al validar XML: {e}")
                self.log("[ERROR] El proyecto fue rechazado.")
                return False

        def select_repo(self):
            folder = QFileDialog.getExistingDirectory(self, "Seleccionar Repositorio")
            if folder:
                self.log(f"[INFO] Validando proyecto: {os.path.basename(folder)}")
                
                # Validar XML antes de aceptar el proyecto
                if self.validate_project_xml(folder):
                    self.repo_path = folder
                    self.repo_display.setText(os.path.basename(folder))
                    self.repo_display.setStyleSheet("""
                        background-color: #2D2D2D; 
                        border-radius: 4px; 
                        padding: 8px 12px; 
                        color: #FFFFFF;
                        border: 1px solid #3D3D3D;
                    """)
                    self.compile_btn.setEnabled(True)
                    self.log(f"[OK] Proyecto aceptado y listo para compilar.\n")
                else:
                    self.repo_display.setText("Proyecto inválido - Seleccionar otro...")
                    self.repo_display.setStyleSheet("""
                        background-color: #2D2D2D; 
                        border-radius: 4px; 
                        padding: 8px 12px; 
                        color: #FF4444;
                        border: 1px solid #FF4444;
                    """)
                    self.compile_btn.setEnabled(False)
                    self.log("[WARN] Por favor selecciona un proyecto válido.\n")

        def select_output(self):
            folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de Salida")
            if folder:
                self.output_path = folder
                self.out_display.setText(os.path.basename(folder))
                self.log(f"Salida seleccionada: {folder}")

        def log(self, message):
            print(message) # Esto va al redirector

        def append_log(self, text):
            # Usar el método especial de la terminal
            self.log_area.write_output(text)

        def start_compilation(self):
            # Esta función se supone que pertenece a una clase, pero estaba usando variables de ámbito global (como parser y args).
            # Asumiremos que self.repo_path y self.output_path están definidos previamente en la clase.

            # Aquí solo debe lanzar la compilación para GUI; no debe hacer lógica de CLI/argumentos
            if not self.repo_path:
                self.log("[ERROR] Debe seleccionar un proyecto primero.")
                return

            if not self.output_path:
                self.output_path = Path("./releases").resolve()

            # Aquí continúa con la compilación usando los paths seleccionados
            self.log("[INFO] Iniciando compilación en GUI...")
            
            # Deshabilitar UI
            self.compile_btn.setEnabled(False)
            self.compile_btn.setText("Compilando...")
            self.progress_bar.setValue(0)
            
            # Iniciar Worker
            self.worker = CompilationWorker(self.repo_path, self.output_path)
            self.worker.progress.connect(self.update_progress)
            self.worker.finished.connect(self.compilation_finished)
            self.worker.start()

        def update_progress(self, value):
            self.progress_bar.setValue(value)

        def compilation_finished(self, success, result_path):
            self.compile_btn.setEnabled(True)
            self.compile_btn.setText("Iniciar Compilación")
            
            if success and result_path:
                self.log("[OK] Compilación finalizada correctamente.")
                self.progress_bar.setValue(100)
                
                # Preguntar dónde guardar el archivo final
                save_path, _ = QFileDialog.getSaveFileName(
                    self, 
                    "Guardar Paquete Compilado", 
                    os.path.basename(result_path), 
                    "Flarm App Package (*.iflapp)"
                )
                
                if save_path:
                    try:
                        shutil.move(result_path, save_path)
                        self.log(f"[INFO] Paquete guardado en: {save_path}")
                        QMessageBox.information(self, "Éxito", f"Paquete guardado exitosamente en:\n{save_path}")
                    except Exception as e:
                        self.log(f"[ERROR] No se pudo mover el archivo: {e}")
                        QMessageBox.warning(self, "Error", f"No se pudo guardar el archivo en la ubicación seleccionada:\n{e}")
                else:
                    self.log("[INFO] Guardado cancelado por el usuario. El archivo permanece en la carpeta de salida temporal.")
                    
            else:
                self.log("[ERROR] Error durante la compilación.")
                self.progress_bar.setValue(0)


# El bloque global principal (main) debería permanecer fuera de la clase, así:
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="FlangCompiler IT - Empaquetador y compilador unificado para Flarm")
    parser.add_argument("repo_path", nargs="?", help="Ruta al repositorio del proyecto")
    parser.add_argument("--output", help="Ruta de salida para los paquetes.")
    parser.add_argument("--gui", action="store_true", help="Forzar modo GUI.")
    parser.add_argument("--cli", action="store_true", help="Forzar modo CLI interactivo.")

    args = parser.parse_args()

    # 1. Modo CLI Directo (Argumentos explícitos)
    if args.repo_path:
        print("--- FlangCompiler IT (Modo CLI Directo) ---")
        compiler = FlangCompiler(args.repo_path, args.output)
        success = compiler.run()
        sys.exit(0 if success else 1)

    # 2. Determinar si usar GUI o Interactivo
    use_gui = False
    
    if args.gui:
        use_gui = True
    elif HAS_PYQT5 and not args.cli:
        # Por defecto usar GUI si está disponible y no se forzó CLI
        use_gui = True
    
    # 3. Intentar lanzar GUI
    if use_gui:
        if HAS_PYQT5:
            print("[DEBUG] Iniciando GUI (PyQt5)...")
            app = QApplication(sys.argv)
            font = QFont("Segoe UI Variable Display", 9)
            app.setFont(font)
            window = CompilerGUI()
            window.show()
            sys.exit(app.exec_())
        else:
            print("[WARN] Se solicitó GUI pero PyQt5 no está instalado.")
            print("[INFO] Cayendo al modo CLI Interactivo...")
            # Fallback a interactivo

    # 4. Modo CLI Interactivo (Selector de Carpetas)
    print("[INFO] Iniciando Selector Interactivo de Carpetas...")
    
    selector = InteractiveFolderSelector()
    repo_path = selector.run()
    
    if not repo_path:
        print("[INFO] Operación cancelada por el usuario.")
        sys.exit(0)
    
    print(f"[INFO] Carpeta seleccionada: {repo_path}")
    
    # Actualizar archivos del proyecto antes de compilar
    update_project_files(repo_path)
    
    # Validate that current directory has details.xml
    details_xml = repo_path / "details.xml"
    if not details_xml.exists():
        print(f"[ERROR] No se encontró details.xml en el directorio seleccionado: {repo_path}")
        print("[ERROR] El directorio no es un proyecto Flarm válido.")
        print("")
        print("Opciones:")
        print("  1. Ejecuta nuevamente y selecciona la carpeta correcta.")
        print("  2. Crea un archivo details.xml en la carpeta.")
        sys.exit(1)
    
    # Create temp directory for build artifacts
    temp_output = tempfile.mkdtemp(prefix="flangcompiler_")
    
    # Final output will be parent directory
    parent_dir = str(Path(repo_path).parent)
    
    print(f"[INFO] Directorio de proyecto: {repo_path}")
    print(f"[INFO] Directorio temporal de compilación: {temp_output}")
    print(f"[INFO] Directorio de salida final: {parent_dir}")
    print("")
    print("--- Iniciando Compilación ---")
    print("")
    
    try:
        # Run compilation
        compiler = FlangCompiler(repo_path, temp_output)
        result_path = compiler.run()
        
        if result_path:
            # Move .iflapp to parent directory
            final_path = Path(parent_dir) / result_path.name
            
            # If file already exists in parent, remove it first
            if final_path.exists():
                final_path.unlink()
            
            shutil.move(str(result_path), str(final_path))
            
            print("")
            print("=" * 60)
            print("[OK] ¡Compilación exitosa!")
            print(f"[OK] Paquete creado: {final_path}")
            print("=" * 60)
            
            # Cleanup temp directory
            shutil.rmtree(temp_output, ignore_errors=True)
            print(f"[INFO] Directorio temporal limpiado")
            sys.exit(0)
        else:
            print("")
            print("[ERROR] La compilación falló. Revisa los mensajes anteriores.")
            # Cleanup temp directory even on failure
            shutil.rmtree(temp_output, ignore_errors=True)
            print(f"[INFO] Directorio temporal limpiado")
            sys.exit(1)
            
    except Exception as e:
        print("")
        print(f"[ERROR] Error durante la compilación: {e}")
        # Cleanup temp directory on exception
        shutil.rmtree(temp_output, ignore_errors=True)
        print(f"[INFO] Directorio temporal limpiado")
        sys.exit(1)
