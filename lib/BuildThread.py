import os
import sys
import time
import shutil
import zipfile
import subprocess
import platform
import fnmatch
import hashlib
import requests
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Optional
from PyQt6.QtCore import QThread, pyqtSignal

from lib.pyinstaller_embedded import get_pyinstaller, ensure_pyinstaller

class FlangCompiler:
    """Compilador principal unificado para el ecosistema Fluthin (Version Robusta)."""

    def __init__(self, repo_path: Path, output_path: Optional[Path] = None, log_callback=None):
        self.repo_path = Path(repo_path).resolve()
        self.output_path = Path(output_path or "./releases").resolve()
        self.log_callback = log_callback
        self.details_xml_path = self.repo_path / "details.xml"
        self.metadata = {}
        self.scripts = []
        self.platform_type = None
        self.current_platform = platform.system()
        self.scripts_to_compile = None
        self.last_error = ""

        self.output_path.mkdir(parents=True, exist_ok=True)
        self.log(f"[FlangCompiler IT] Inicializado en: {self.repo_path}")
        self.log(f"[FlangCompiler IT] Plataforma actual: {self.current_platform}")

    def log(self, msg):
        if self.log_callback:
            self.log_callback(msg)

    def _check_pyinstaller_installed(self) -> bool:
        pyi = get_pyinstaller()
        if pyi.is_available():
            self.log(f"[INFO] PyInstaller embebido: {pyi.get_version()}")
            return True
        return False

    def _ensure_pyinstaller(self) -> bool:
        if self._check_pyinstaller_installed():
            return True
        self.log("[INFO] PyInstaller no encontrado. Iniciando instalación automática...")
        if ensure_pyinstaller(log_callback=self.log):
            return True
        self.last_error = "No se pudo instalar PyInstaller automáticamente."
        self.log("[ERROR] No se pudo instalar PyInstaller automáticamente")
        return False

    def parse_details_xml(self) -> bool:
        if not self.details_xml_path.exists():
            self.log(f"[ERROR] No details.xml found in {self.repo_path}")
            return False
        try:
            tree = ET.parse(self.details_xml_path)
            root = tree.getroot()
            self.metadata = {
                'publisher': root.findtext('publisher') or root.findtext('empresa') or 'Unknown',
                'app': root.findtext('app') or root.findtext('name') or 'Unknown',
                'name': root.findtext('name') or root.findtext('titulo') or 'Unknown',
                'version': root.findtext('version') or 'v1.0',
                'platform': root.findtext('platform') or root.findtext('plataforma') or 'AlphaCube',
                'author': root.findtext('author') or root.findtext('autor') or 'Unknown',
            }
            self.platform_type = self.metadata['platform']
            self.log(f"[INFO] Metadatos cargados: {self.metadata}")
            return True
        except Exception as e:
            self.last_error = str(e)
            self.log(f"[ERROR] Error al parsear details.xml: {e}")
            return False

    def _find_icon(self, script_name: str):
        app_dir = self.repo_path / "app"
        if not app_dir.exists():
            return None
        specific_icon = app_dir / f"{script_name}-icon.ico"
        if specific_icon.exists():
            return specific_icon
        if script_name == self.metadata['app']:
            default_icon = app_dir / "app-icon.ico"
            if default_icon.exists():
                return default_icon
        return None

    def _detect_hidden_imports(self, script_path: Path) -> list:
        hidden_imports = []
        try:
            content = script_path.read_text(encoding="utf-8")
            if "PyQt6" in content:
                hidden_imports.append("PyQt6")
            if "leviathan_ui" in content:
                hidden_imports.append("leviathan_ui")
            if "requests" in content:
                hidden_imports.append("requests")
        except OSError:
            pass
        return hidden_imports

    def find_scripts(self) -> bool:
        if self.scripts_to_compile:
            self.scripts = []
            app_dir = self.repo_path / "app"
            for script_name in self.scripts_to_compile:
                script_path = self.repo_path / f"{script_name}.py"
                if not script_path.exists() and app_dir.exists():
                    script_path = app_dir / f"{script_name}.py"
                if script_path.exists():
                    icon_path = self._find_icon(script_name)
                    self.scripts.append({
                        "name": script_name,
                        "path": script_path,
                        "icon": icon_path,
                        "is_main": script_name == self.metadata.get("app"),
                    })
                    self.log(f"[INFO] Script seleccionado: {script_name}")
            if not self.scripts:
                self.last_error = "No se encontraron los scripts indicados en scripts_to_compile."
                self.log("[ERROR] No se encontraron scripts para compilar.")
            return len(self.scripts) > 0

        main_script = f"{self.metadata['app']}.py"
        main_script_path = self.repo_path / main_script
        # Also check in app/ subdirectory
        app_dir = self.repo_path / "app"
        if not main_script_path.exists() and app_dir.exists():
            main_script_path = app_dir / main_script
        if main_script_path.exists():
            icon_path = self._find_icon(self.metadata['app'])
            self.scripts.append({
                'name': self.metadata['app'],
                'path': main_script_path,
                'icon': icon_path,
                'is_main': True,
            })
            self.log(f"[INFO] Main script: {main_script} | Icon: {icon_path.name if icon_path else 'None'}")
        # Search for secondary scripts in root and app/ subdirectory
        search_paths = [self.repo_path]
        if app_dir.exists():
            search_paths.append(app_dir)
        for search_path in search_paths:
            for file in search_path.glob("*.py"):
                if file.name != main_script and not file.name.startswith("_") and file.name not in ["packagemaker.py"]:
                    # Avoid duplicates if same file found in both locations
                    if any(s['path'] == file for s in self.scripts):
                        continue
                    icon_path = self._find_icon(file.stem)
                    self.scripts.append({
                        'name': file.stem,
                        'path': file,
                        'icon': icon_path,
                        'is_main': False,
                    })
                    icon_name = icon_path.name if icon_path else 'None'
                    self.log(f"[INFO] Secondary script: {file.name} | Icon: {icon_name}")
        if not self.scripts:
            self.last_error = "No se encontraron scripts .py para compilar en el proyecto."
            self.log("[ERROR] No se encontraron scripts para compilar.")
        return len(self.scripts) > 0

    def should_compile_for_platform(self, target_platform: str) -> bool:
        if self.platform_type == "AlphaCube":
            return True
        if self.platform_type == "Knosthalij":
            return target_platform == "Windows"
        if self.platform_type == "Danenone":
            return target_platform == "Linux"
        return False

    def compile_binaries(self, target_platform: str) -> bool:
        if not self.should_compile_for_platform(target_platform):
            return True
        if target_platform == "Windows" and self.current_platform != "Windows":
            self.log(f"[SKIP] Cannot compile Windows on {self.current_platform}")
            return True
        if target_platform == "Linux" and self.current_platform != "Linux":
            self.log(f"[SKIP] Cannot compile Linux on {self.current_platform}")
            return True
        if not self._ensure_pyinstaller():
            return False
        self.log("--- / --- - WORKING FOR SQUAREROOM - --- / ---")
        self.log(f"[INFO] Iniciando compilación para {target_platform}...")
        for script in self.scripts:
            self.log(f"[INFO] Compilando script: {script['name']}...")
            if target_platform == "Windows":
                if not self._compile_windows_binary(script):
                    return False
            elif target_platform == "Linux":
                if not self._compile_linux_binary(script):
                    return False
        return True

    def _prepare_pyinstaller_data_dirs(self):
        assets_dir = self.repo_path / "assets"
        app_dir = self.repo_path / "app"
        assets_dir.mkdir(exist_ok=True)
        app_dir.mkdir(exist_ok=True)
        (assets_dir / ".assets-container").touch(exist_ok=True)
        (app_dir / ".app-container").touch(exist_ok=True)
        return assets_dir, app_dir

    def _compile_windows_binary(self, script: Dict) -> bool:
        return self._compile_binary(script, windowed=True)

    def _compile_linux_binary(self, script: Dict) -> bool:
        return self._compile_binary(script, windowed=False)

    def _compile_binary(self, script: Dict, windowed: bool) -> bool:
        script_path = script["path"]
        script_name = script["name"]
        assets_dir, app_dir = self._prepare_pyinstaller_data_dirs()
        add_data = [(str(assets_dir), "assets"), (str(app_dir), "app")]
        hidden_imports = self._detect_hidden_imports(script_path)

        pyi = get_pyinstaller()
        if not pyi.is_available():
            self.last_error = "PyInstaller no disponible"
            self.log("[ERROR] PyInstaller no disponible")
            return False

        dist_dir = self.repo_path / "dist"
        dist_dir.mkdir(exist_ok=True)
        build_dir = tempfile.mkdtemp(prefix="pyi_build_")

        try:
            self.log(f"[DEBUG] Compilando {script_name} con PyInstaller embebido...")
            exe_path = pyi.compile_to_exe(
                script_path=str(script_path),
                output_name=script_name,
                output_dir=str(dist_dir),
                icon_path=str(script["icon"]) if script["icon"] else None,
                windowed=windowed,
                onefile=True,
                add_data=add_data,
                hidden_imports=hidden_imports,
                build_dir=build_dir,
                cwd=str(self.repo_path),
            )
            if exe_path and os.path.exists(exe_path):
                if not windowed:
                    try:
                        os.chmod(exe_path, 0o755)
                    except OSError:
                        pass
                self.log(f"[OK] {script_name} compilado.")
                return True
            self.last_error = pyi.get_last_error()
            self.log(f"[ERROR] {self.last_error}")
            return False
        except Exception as e:
            self.last_error = str(e)
            self.log(f"[ERROR] Excepción PyInstaller: {e}")
            return False
        finally:
            pyi.cleanup()
            shutil.rmtree(build_dir, ignore_errors=True)

    def create_package(self, target_platform: str) -> bool:
        if not self.should_compile_for_platform(target_platform):
            return True
        platform_suffix = "Knosthalij" if target_platform == "Windows" else "Danenone"
        package_name = f"{self.metadata['publisher']}.{self.metadata['app']}.{self.metadata['version']}.{platform_suffix}"
        package_path = self.output_path / package_name
        package_path.mkdir(parents=True, exist_ok=True)
        self.log(f"[INFO] Creando paquete en: {package_path}")
        self._copy_package_files(package_path, target_platform)
        self._update_and_copy_details_xml(package_path, platform_suffix)
        return True

    def _copy_package_files(self, package_path: Path, target_platform: str) -> None:
        exclude_patterns = ["requirements.txt", "*.pyc", "__pycache__", ".git", ".gitignore", "build", "dist", "*.spec", "*.py"]
        for item in self.repo_path.iterdir():
            if any(fnmatch.fnmatch(item.name, p) for p in exclude_patterns):
                continue
            dest = package_path / item.name
            if item.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                try:
                    shutil.copytree(item, dest, ignore=shutil.ignore_patterns(*exclude_patterns))
                except Exception as e:
                    self.log(f"[WARN] Error copiando {item.name}: {e}")
            elif item.is_file():
                try:
                    shutil.copy2(item, dest)
                except:
                    pass
        dist_dir = self.repo_path / "dist"
        if dist_dir.exists():
            for binary in dist_dir.iterdir():
                if target_platform == "Windows" and binary.suffix == ".exe":
                    shutil.copy2(binary, package_path / binary.name)
                elif target_platform == "Linux" and binary.suffix == "":
                    shutil.copy2(binary, package_path / binary.name)
                    try:
                        (package_path / binary.name).chmod(0o755)
                    except:
                        pass

    def _update_and_copy_details_xml(self, package_path: Path, platform_suffix: str) -> None:
        """Actualiza y copia details.xml con formateo correcto."""
        try:
            tree = ET.parse(self.details_xml_path)
            root = tree.getroot()
            pe = root.find('platform')
            if pe is None:
                pe = ET.SubElement(root, 'platform')
            pe.text = platform_suffix
            
            # Formatear y guardar XML
            self._save_pretty_xml(tree, package_path / "details.xml")
        except Exception as e:
            self.log(f"[ERROR] Updating XML: {e}")
    
    def _save_pretty_xml(self, tree, filepath):
        """Guarda un XML formateado con indentación."""
        from xml.dom import minidom
        
        root = tree.getroot() if hasattr(tree, 'getroot') else tree
        rough_string = ET.tostring(root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        pretty = reparsed.toprettyxml(indent="  ")
        
        # Eliminar líneas vacías
        lines = [line for line in pretty.split('\n') if line.strip()]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    def compress_to_iflapp(self, package_path: Path, output_file: Path) -> bool:
        self.log(f"[INFO] Creando .iflapp: {output_file.name}")
        try:
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(package_path):
                    for file in files:
                        fp = Path(root) / file
                        arcname = fp.relative_to(package_path)
                        zipf.write(fp, arcname)
            return True
        except Exception as e:
            self.log(f"[ERROR] Zip failed: {e}")
            return False

    def run(self, build_mode="portable") -> Optional[Path]:
        if not self.parse_details_xml():
            return None
        if not self.find_scripts():
            self.log("[WARN] No scripts found")
            return None
        platforms_to_compile = []
        if self.current_platform == "Windows":
            if self.should_compile_for_platform("Windows"):
                platforms_to_compile.append("Windows")
        elif self.current_platform == "Linux":
            if self.should_compile_for_platform("Linux"):
                platforms_to_compile.append("Linux")
        if not platforms_to_compile:
            self.log("[WARN] Nothing to compile for this platform/config.")
            return None
        final_iflapp = None
        for platform_name in platforms_to_compile:
            if not self.compile_binaries(platform_name):
                return None
            if not self.create_package(platform_name):
                return None
            platform_suffix = "Knosthalij" if platform_name == "Windows" else "Danenone"
            package_name = f"{self.metadata['publisher']}.{self.metadata['app']}.{self.metadata['version']}.{platform_suffix}"
            last_package_path = self.output_path / package_name
            iflapp_name = f"{self.metadata['publisher']}.{self.metadata['app']}.{self.metadata['version']}-{platform_suffix}.iflapp"
            iflapp_path = self.output_path / iflapp_name
            if self.compress_to_iflapp(last_package_path, iflapp_path):
                final_iflapp = iflapp_path
                self.log(f"[SUCCESS] Package created: {iflapp_path}")
        return final_iflapp

class BuildThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, empresa, nombre, version, plataforma, parent=None, custom_path=None, base_dir=None, build_mode="portable"):
        super().__init__(parent)
        self.empresa = empresa
        self.nombre = nombre
        self.version = version
        self.plataforma = plataforma
        self.custom_path = custom_path
        self.build_mode = build_mode
        self.base_dir = base_dir
        self.curiosity_phrases = [
            "Sabias que el primer error de software fue causado por una polilla real atrapada en una computadora?",
            "Sabias que Python lleva el nombre de la serie de television Monty Python's Flying Circus?",
            "Sabias que el modo oscuro consume menos energia en pantallas OLED?",
            "Sabias que el codigo de la mision Apolo 11 contenia chistes escondidos?",
            "Sabias que 'Hello World' se convirtio en tradicion gracias a Brian Kernighan?",
            "Sabias que el primer lenguaje de programacion fue creado por Ada Lovelace?",
            "Sabias que el 90% del codigo de los coches modernos es software?",
            "Sabias que Linux esta presente en el 100% de las 500 supercomputadoras mas potentes?",
            "Sabias que el primer dominio registrado fue symbolics.com en 1985?",
            "Sabias que se estima que hay mas de 20 millones de desarrolladores en el mundo?"
        ]
        self._curiosity_timer = None

    def emit_random_curiosity(self):
        import random
        phrase = random.choice(self.curiosity_phrases)
        self.progress.emit(f"Curiosidad: {phrase}")

    def run(self):
        self.emit_random_curiosity()
        p_map = {"Windows": "Knosthalij", "Linux": "Danenone", "Multiplataforma": "AlphaCube"}
        plat_suffix = p_map.get(self.plataforma, "AlphaCube")
        repo_path = None
        if self.custom_path:
            repo_path = Path(self.custom_path)
            if not repo_path.exists():
                self.error.emit(f"No se encontró la carpeta personalizada: {self.custom_path}")
                return
        else:
            folder = f"{self.empresa}.{self.nombre}.v{self.version}-{plat_suffix}"
            base_dir = self.base_dir or Path.cwd()
            repo_path = Path(base_dir) / folder
            if not repo_path.exists():
                self.error.emit(f"No se encontró la carpeta: {folder}")
                return
        compiler = FlangCompiler(repo_path, Path(self.base_dir or Path.cwd()), log_callback=self.handle_compiler_log)
        result = compiler.run(build_mode=self.build_mode)
        if result:
            self.finished.emit(f"Paquete construido con exito: {result.name}")
        else:
            error_message = compiler.last_error or "Fallo la compilacion. Verifique los logs y los iconos .ico"
            self.error.emit(error_message)

    def handle_compiler_log(self, msg):
        self.progress.emit(msg)
        if not hasattr(self, '_last_phrase_time'):
            self._last_phrase_time = time.time()
        if time.time() - self._last_phrase_time > 8:
            import random
            self.progress.emit(f"Curiosidad: {random.choice(self.curiosity_phrases)}")
            self._last_phrase_time = time.time()
