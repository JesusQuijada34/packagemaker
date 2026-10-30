import os
import json
import sys
import time
import shutil
import platform
import fnmatch
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Optional, List

from lib.projectNameFormatter import ProjectNameFormatter

# requests con fallback a urllib
try:
    import requests
except ImportError:
    requests = None

try:
    from PyQt6.QtCore import QThread, pyqtSignal
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    class QThread:
        def __init__(self, *args, **kwargs): pass
    class pyqtSignal:
        def __init__(self, *args, **kwargs): pass
        def connect(self, func): pass
        def emit(self, *args, **kwargs): pass

from lib import iflapp_format
from lib.compilers import (
    CompilerUnavailableError,
    available_backends,
    ensure_backend,
    resolve_backend,
)
from lib.hardware_sandbox import HardwareSandbox

class FlangCompiler:
    """Compilador principal unificado para el ecosistema Fluthin (Version Robusta)."""

    def __init__(
        self,
        repo_path: Path,
        output_path: Optional[Path] = None,
        log_callback=None,
        compiler_name: Optional[str] = None,
        sandbox: bool = True,
        package_password: Optional[str] = None,
        signing_key: Optional[bytes] = None,
        build_dropper: bool = False,
        hardening: Optional[List[str]] = None,
    ):
        self.repo_path = Path(repo_path).resolve()
        self.output_path = Path(output_path or "./releases").resolve()
        self.log_callback = log_callback
        self.details_xml_path = self.repo_path / "details.xml"
        self.metadata = {}
        self.scripts = []
        self.platform_type = None
        self.current_platform = platform.system()
        self.last_error = ""
        self.scripts_to_compile = self._load_scripts_to_compile()
        self.compiler_name = compiler_name
        self._backend = None
        self.package_password = package_password
        self.signing_key = signing_key or iflapp_format.DEFAULT_SIGNING_KEY
        self.build_dropper = build_dropper
        self.hardening_methods = list(hardening) if hardening else []
        self.sandbox_enabled = sandbox
        self._sandbox = HardwareSandbox(log_callback=self.log) if sandbox else None

        self.output_path.mkdir(parents=True, exist_ok=True)
        self.log(f"[FlangCompiler IT] Inicializado en: {self.repo_path}")
        self.log(f"[FlangCompiler IT] Plataforma actual: {self.current_platform}")
        if self._sandbox:
            self.log(f"[FlangCompiler IT] Sandbox: {self._sandbox.backend}")

    def log(self, msg):
        if self.log_callback:
            self.log_callback(msg)

    def _load_scripts_to_compile(self) -> Optional[List[str]]:
        """Carga una lista opcional de entry points desde config/settings.json.

        Sin la clave se conserva el descubrimiento histórico de todos los scripts.
        Si la clave está presente, sólo se compilan los nombres declarados para
        evitar publicar pruebas, utilidades o prototipos como binarios de la app.
        """
        settings_path = self.repo_path / "config" / "settings.json"
        if not settings_path.is_file():
            return None
        try:
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            self.last_error = f"No se pudo leer config/settings.json: {error}"
            self.log(f"[ERROR] {self.last_error}")
            return []
        build = settings.get("build")
        if not isinstance(build, dict) or "scripts" not in build:
            return None
        scripts = build.get("scripts")
        if not isinstance(scripts, list) or not scripts:
            self.last_error = "config/settings.json debe declarar build.scripts como una lista no vacía."
            self.log(f"[ERROR] {self.last_error}")
            return []
        normalized = []
        for script in scripts:
            if not isinstance(script, str) or not script or any(char in script for char in "/\\") or script != Path(script).stem:
                self.last_error = "build.scripts contiene un nombre de script no seguro."
                self.log(f"[ERROR] {self.last_error}")
                return []
            normalized.append(script)
        return normalized

    def _check_pyinstaller_installed(self) -> bool:
        """Compatibilidad: indica si el backend PyInstaller está disponible."""
        from lib.compilers import PyInstallerBackend

        return PyInstallerBackend().is_available()

    def _ensure_pyinstaller(self) -> bool:
        """Compatibilidad: garantiza el backend PyInstaller."""
        if self._check_pyinstaller_installed():
            return True
        self.log("[INFO] PyInstaller no encontrado. Iniciando instalación automática...")
        if ensure_backend("pyinstaller", log_callback=self.log):
            return True
        self.last_error = "No se pudo instalar PyInstaller automáticamente."
        self.log("[ERROR] No se pudo instalar PyInstaller automáticamente")
        return False

    def describe_compilers(self) -> dict:
        """Informe de compiladores disponibles para la interfaz y el CLI."""
        return available_backends(log_callback=self.log)

    def _ensure_compiler(self):
        """Resuelve y garantiza un backend de compilación operativo.

        Prioriza el backend solicitado (``compiler_name``), cae a Nuitka y, si
        no está disponible, intenta instalarlo; PyInstaller queda como último
        recurso de compatibilidad.
        """
        if self._backend is not None and self._backend.is_available():
            return self._backend
        preferred = self.compiler_name
        try:
            self._backend = resolve_backend(preferred, log_callback=self.log)
            self.log(f"[INFO] Compilador seleccionado: {self._backend.display_name}")
            return self._backend
        except CompilerUnavailableError:
            pass

        target = (preferred or "nuitka").strip().lower()
        self.log(f"[INFO] Compilador {target!r} no disponible; instalando dependencias...")
        if ensure_backend(target, log_callback=self.log):
            self._backend = resolve_backend(target, log_callback=self.log)
            self.log(f"[INFO] Compilador seleccionado: {self._backend.display_name}")
            return self._backend

        # Último recurso: PyInstaller histórico.
        if ensure_backend("pyinstaller", log_callback=self.log):
            self._backend = resolve_backend("pyinstaller", log_callback=self.log)
            self.log(f"[WARN] Usando compilador de respaldo: {self._backend.display_name}")
            return self._backend

        self.last_error = "No hay ningún compilador disponible (Nuitka, PyInstaller, cx_Freeze)."
        self.log(f"[ERROR] {self.last_error}")
        return None

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
        if self.scripts_to_compile is not None:
            self.scripts = []
            if not self.scripts_to_compile:
                if not self.last_error:
                    self.last_error = "No se declararon scripts de compilación."
                self.log(f"[ERROR] {self.last_error}")
                return False
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
            self.last_error = (
                f"La plataforma del proyecto ({self.platform_type}) no permite "
                f"compilar para {target_platform}."
            )
            self.log(f"[ERROR] {self.last_error}")
            return False
        if target_platform == "Windows" and self.current_platform != "Windows":
            self.last_error = (
                f"No se puede compilar para Windows desde {self.current_platform}; "
                "se requiere un runner Windows."
            )
            self.log(f"[ERROR] {self.last_error}")
            return False
        if target_platform == "Linux" and self.current_platform != "Linux":
            self.last_error = (
                f"No se puede compilar para Linux desde {self.current_platform}; "
                "se requiere un runner Linux."
            )
            self.log(f"[ERROR] {self.last_error}")
            return False
        backend = self._ensure_compiler()
        if backend is None:
            return False
        self.log("--- / --- - WORKING FOR SQUAREROOM - --- / ---")
        self.log(f"[INFO] Iniciando compilación para {target_platform} con {backend.display_name}...")
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
        # cliHandler y otros módulos cargan details.xml relativo a la raíz del bundle.
        # Incluirlo explícitamente es necesario para ejecutables onefile/frozen.
        if self.details_xml_path.is_file():
            add_data.append((str(self.details_xml_path), "."))
        hidden_imports = self._detect_hidden_imports(script_path)

        backend = self._ensure_compiler()
        if backend is None:
            return False

        dist_dir = self.repo_path / "dist"
        dist_dir.mkdir(exist_ok=True)
        build_dir = tempfile.mkdtemp(prefix=f"{backend.name}_build_")
        # Cada compilador puede limpiar su salida entre ejecuciones; compilar en
        # un directorio aislado y acumular el binario en `dist` que consume
        # create_package().
        script_dist_dir = Path(build_dir) / "dist"
        script_dist_dir.mkdir(parents=True, exist_ok=True)

        try:
            self.log(f"[DEBUG] Compilando {script_name} con {backend.display_name}...")
            
            # Preparar icono: convertir ICO a PNG en Linux si es necesario
            icon_to_use = script["icon"]
            if icon_to_use and sys.platform.startswith("linux") and str(icon_to_use).endswith(".ico"):
                try:
                    from lib.linux_icon_handler import convert_ico_to_png
                    png_icon = str(icon_to_use).replace(".ico", ".png")
                    if convert_ico_to_png(str(icon_to_use), png_icon):
                        icon_to_use = Path(png_icon)
                        self.log(f"[INFO] Icono convertido a PNG: {png_icon}")
                except Exception as e:
                    self.log(f"[WARNING] Error al convertir icono a PNG: {e}")
            
            exe_path = backend.compile(
                script_path=str(script_path),
                output_name=script_name,
                output_dir=str(script_dist_dir),
                icon_path=str(icon_to_use) if icon_to_use else None,
                windowed=windowed,
                onefile=True,
                add_data=add_data,
                hidden_imports=hidden_imports,
                build_dir=build_dir,
                cwd=str(self.repo_path),
            )
            if exe_path and os.path.exists(exe_path):
                accumulated_exe = dist_dir / Path(exe_path).name
                shutil.copy2(exe_path, accumulated_exe)
                if not windowed:
                    try:
                        os.chmod(accumulated_exe, 0o755)
                    except OSError:
                        pass
                self.log(f"[OK] {script_name} compilado.")
                return True
            self.last_error = backend.last_error or "El compilador no generó el binario esperado."
            self.log(f"[ERROR] {self.last_error}")
            return False
        except Exception as e:
            self.last_error = str(e)
            self.log(f"[ERROR] Excepción del compilador: {e}")
            return False
        finally:
            backend.cleanup()
            shutil.rmtree(build_dir, ignore_errors=True)

    def create_package(self, target_platform: str) -> bool:
        if not self.should_compile_for_platform(target_platform):
            self.last_error = (
                f"La plataforma del proyecto ({self.platform_type}) no permite "
                f"crear un paquete para {target_platform}."
            )
            self.log(f"[ERROR] {self.last_error}")
            return False
        # Usar ProjectNameFormatter para formato consistente
        platform_suffix = "Knosthalij" if target_platform == "Windows" else "Danenone"
        package_name = ProjectNameFormatter.format_package_folder(
            self.metadata['publisher'],
            self.metadata['app'],
            self.metadata['version'],
            platform_suffix
        )
        package_path = self.output_path / package_name
        package_path.mkdir(parents=True, exist_ok=True)
        self.log(f"[INFO] Creando paquete en: {package_path}")
        self._copy_package_files(package_path, target_platform)
        self._update_and_copy_details_xml(package_path, platform_suffix)

        expected_suffix = ".exe" if target_platform == "Windows" else ""
        compiled_names = sorted(item.name for item in (self.repo_path / "dist").iterdir()) if (self.repo_path / "dist").is_dir() else []
        packaged_names = sorted(item.name for item in package_path.iterdir())
        self.log(f"[DEBUG] Binarios acumulados en dist: {compiled_names}")
        self.log(f"[DEBUG] Entradas copiadas al paquete: {packaged_names}")
        expected_binaries = []
        missing_binaries = []
        for script in self.scripts:
            binary_name = f"{script['name']}{expected_suffix}"
            candidates = [package_path / binary_name, package_path / "bin" / binary_name]
            binary_path = next((candidate for candidate in candidates if candidate.is_file()), None)
            if binary_path is None:
                missing_binaries.append(binary_name)
            else:
                expected_binaries.append(binary_path)
        if missing_binaries:
            self.log(f"[DEBUG] Binarios faltantes: {missing_binaries}")
        if not expected_binaries or missing_binaries:
            self.last_error = (
                f"El paquete para {target_platform} no contiene todos los binarios "
                "compilados esperados."
            )
            self.log(f"[ERROR] {self.last_error}")
            shutil.rmtree(package_path, ignore_errors=True)
            return False
        return True

    def optimize_binaries(self) -> bool:
        """Optimiza los binarios generados (Placeholder para compatibilidad con CLI)."""
        self.log("[INFO] Optimización de binarios no implementada aún.")
        return True

    def _load_gitignore_patterns(self) -> List[str]:
        """Carga los patrones de .gitignore si existe."""
        patterns = [
            "requirements.txt", "*.pyc", "__pycache__", ".git", ".gitignore", 
            "build", "dist", "*.spec", "*.py", ".idea", ".vscode", ".github"
        ]
        gitignore_path = self.repo_path / ".gitignore"
        if gitignore_path.exists():
            try:
                with open(gitignore_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            # Normalizar patrones para fnmatch
                            p = line
                            if p.startswith("/"): p = p[1:]
                            if p.endswith("/"): p = p[:-1]
                            if p not in patterns:
                                patterns.append(p)
                self.log(f"[INFO] .gitignore cargado ({len(patterns)} patrones)")
            except Exception as e:
                self.log(f"[WARN] No se pudo leer .gitignore: {e}")
        return patterns

    def _should_exclude(self, name: str, patterns: List[str]) -> bool:
        """Verifica si un archivo o directorio debe ser excluido."""
        for p in patterns:
            if fnmatch.fnmatch(name, p) or fnmatch.fnmatch(name, f"*/{p}"):
                return True
            # Manejar directorios recursivos en gitignore
            if "/" in p:
                parts = p.split("/")
                if name == parts[0] or name == parts[-1]:
                    return True
        return False

    def _copy_package_files(self, package_path: Path, target_platform: str) -> None:
        exclude_patterns = self._load_gitignore_patterns()
        
        def ignore_func(directory, contents):
            return [c for c in contents if self._should_exclude(c, exclude_patterns)]

        for item in self.repo_path.iterdir():
            if self._should_exclude(item.name, exclude_patterns):
                continue
                
            dest = package_path / item.name
            if item.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                try:
                    shutil.copytree(item, dest, ignore=ignore_func)
                except Exception as e:
                    self.log(f"[WARN] Error copiando {item.name}: {e}")
            elif item.is_file():
                try:
                    shutil.copy2(item, dest)
                except OSError:
                    pass
        # Los archivos estructurales de PackageMaker son parte del contrato del paquete.
        # Se copian explícitamente después de aplicar .gitignore para evitar que un
        # proyecto excluya accidentalmente sus propios metadatos MoonFix.
        mandatory_paths = [
            Path(".storedetail"), Path("version.res"), Path("autorun"),
            Path("autorun.bat"), Path("updater.py"), Path("config/settings.json"),
            Path("app/.app-container"), Path("assets/.assets-container"),
            Path("config/.config-container"), Path("docs/.docs-container"),
            Path("source/.source-container"), Path("lib/.lib-container"),
        ]
        if (self.repo_path / "manifest.res").exists():
            mandatory_paths.append(Path("manifest.res"))
        for relative in mandatory_paths:
            source = self.repo_path / relative
            destination = package_path / relative
            if source.is_file():
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
            elif source.is_dir():
                destination.mkdir(parents=True, exist_ok=True)

        dist_dir = self.repo_path / "dist"
        if dist_dir.exists():
            for binary in dist_dir.iterdir():
                if (target_platform == "Windows" and binary.suffix == ".exe") or (target_platform == "Linux" and binary.suffix == ""):
                    destination = package_path / binary.name
                    # `app`, `config` y otros nombres pueden coincidir con
                    # carpetas obligatorias del contrato Fluthin.
                    if destination.exists() and destination.is_dir():
                        destination = package_path / "bin" / binary.name
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(binary, destination)
                    try:
                        destination.chmod(0o755)
                    except OSError:
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
        """Crea el contenedor binario ``.iflapp`` v2 (reemplaza al ZIP histórico)."""
        self.log(f"[INFO] Creando .iflapp blindado: {output_file.name}")
        try:
            if not package_path.is_dir():
                self.last_error = f"No existe la carpeta de paquete: {package_path}"
                self.log(f"[ERROR] {self.last_error}")
                return False

            details_bytes = None
            details_path = package_path / "details.xml"
            if details_path.is_file():
                details_bytes = details_path.read_bytes()

            icon_bytes = None
            icon_name = "app-icon.ico"
            for candidate in (package_path / "app" / "app-icon.ico", package_path / "app-icon.ico"):
                if candidate.is_file():
                    icon_bytes = candidate.read_bytes()
                    break

            iflapp_format.pack_iflapp(
                package_path,
                output_file,
                icon=icon_bytes,
                icon_name=icon_name,
                details=details_bytes,
                identity=self.metadata,
                password=self.package_password,
                signing_key=self.signing_key,
            )

            report = iflapp_format.verify_iflapp(output_file, signing_key=self.signing_key)
            if report.get("file_count", 0) <= 0:
                self.last_error = "El contenedor .iflapp generado está vacío."
                self.log(f"[ERROR] {self.last_error}")
                output_file.unlink(missing_ok=True)
                return False

            header = iflapp_format.read_iflapp_header(output_file, include_blobs=False)
            names = {entry["path"] for entry in header.manifest}
            if "details.xml" not in names:
                self.last_error = "El archivo .iflapp no contiene details.xml."
                self.log(f"[ERROR] {self.last_error}")
                output_file.unlink(missing_ok=True)
                return False

            self.log(
                f"[OK] Contenedor firmado ({report['file_count']} archivos, "
                f"{header.compression}, {header.encryption})."
            )
            return True
        except Exception as e:
            self.last_error = str(e)
            self.log(f"[ERROR] Empaquetado fallido: {e}")
            return False

    def create_dropper(self, iflapp_path: Path, output_file: Optional[Path] = None) -> Optional[Path]:
        """Genera un dropper autoextraíble a partir del ``.iflapp`` validado."""
        from lib.dropper import create_dropper

        output_file = output_file or Path(iflapp_path).with_suffix(".run")
        try:
            create_dropper(iflapp_path, output_file, password=self.package_password)
            self.log(f"[OK] Dropper autoextraíble generado: {output_file.name}")
            return output_file
        except Exception as e:
            self.log(f"[WARN] No se pudo generar el dropper: {e}")
            return None

    def apply_hardening(self, package_path: Path) -> List:
        """Aplica los métodos de blindaje solicitados sobre el paquete.

        Se ejecuta antes del empaquetado final, cuando el árbol del paquete ya
        está construido y los binarios existen en disco.
        """
        from lib import hardening as hardening_mod

        if not self.hardening_methods:
            return []

        binaries = [
            candidate
            for candidate in Path(package_path).rglob("*")
            if candidate.is_file()
            and candidate.suffix.lower() in (".exe", "")
            and candidate.parent.name in ("bin", package_path.name)
        ]
        binary = binaries[0] if binaries else None
        icon = None
        for candidate in (Path(package_path) / "app" / "app-icon.ico", Path(package_path) / "app-icon.ico"):
            if candidate.is_file():
                icon = candidate
                break
        script = next(
            (candidate for candidate in Path(package_path).rglob("*.py") if candidate.is_file()),
            None,
        )
        return hardening_mod.apply_all(
            binary=binary,
            script=script,
            package_dir=package_path,
            icon=icon,
            methods=self.hardening_methods,
            log_callback=self.log,
        )

    def verify_in_sandbox(self, iflapp_path: Path) -> bool:
        """Valida el paquete en un entorno virtualizado a nivel de hardware/CPU.

        La extracción y la comprobación del arranque se delegan al sandbox; la
        fuente original nunca se expone directamente al código del paquete.
        """
        if not self._sandbox:
            self.log("[INFO] Sandbox desactivado; se omite la verificación aislada.")
            return True

        info = self._sandbox.describe()
        self.log(
            f"[INFO] Verificando paquete en sandbox '{info['selected']}' "
            f"(virtualización hardware: {info['hardware_virtualization']})."
        )
        workspace = None
        try:
            workspace = self._sandbox.prepare_workspace(self.output_path, writable=True)
            extract_script = Path(workspace) / "_iflapp_verify.py"
            extract_script.write_text(
                "\n".join(
                    [
                        "import sys",
                        "from lib.iflapp_format import extract_iflapp, verify_iflapp, read_iflapp_header",
                        "pkg = sys.argv[1]",
                        "dest = sys.argv[2]",
                        "verify_iflapp(pkg)",
                        "extract_iflapp(pkg, dest)",
                        "header = read_iflapp_header(pkg, include_blobs=False)",
                        "print('IFLAPP_OK', header.file_count, header.identity().get('app', ''))",
                    ]
                ),
                encoding="utf-8",
            )
            # El script aislado importa ``lib.iflapp_format``; hay que exponer el
            # directorio de PackageMaker en el entorno del sandbox.
            project_root = Path(__file__).resolve().parent.parent
            sandbox_env = {"PYTHONPATH": os.pathsep.join(
                [str(project_root), os.environ.get("PYTHONPATH", "")]
            ).rstrip(os.pathsep)}
            result = self._sandbox.run(
                [sys.executable, str(extract_script), str(iflapp_path), str(Path(workspace) / "unpacked")],
                workspace,
                env=sandbox_env,
            )
            if result.ok and "IFLAPP_OK" in result.stdout:
                self.log(f"[OK] Verificación en sandbox correcta ({result.backend}).")
                return True
            self.log(f"[WARN] Verificación en sandbox incompleta: {result.stderr.strip()[:400]}")
            return False
        except Exception as e:
            self.log(f"[WARN] Sandbox no disponible para verificación: {e}")
            return False
        finally:
            if workspace:
                self._sandbox.cleanup(workspace)

    def _cleanup_build_artifacts(self):
        """Limpia archivos generados por PyInstaller en el proyecto original."""
        self.log("[INFO] Limpiando archivos de compilación...")
        dist_dir = self.repo_path / "dist"
        build_dir = self.repo_path / "build"
        
        # Eliminar carpetas dist y build si existen
        for folder in [dist_dir, build_dir]:
            if folder.exists() and folder.is_dir():
                try:
                    shutil.rmtree(folder)
                    self.log(f"[INFO] Carpeta eliminada: {folder.name}")
                except Exception as e:
                    self.log(f"[WARN] No se pudo eliminar {folder.name}: {e}")
        
        # Eliminar archivos .spec
        for spec_file in self.repo_path.glob("*.spec"):
            try:
                spec_file.unlink()
                self.log(f"[INFO] Archivo eliminado: {spec_file.name}")
            except Exception as e:
                self.log(f"[WARN] No se pudo eliminar {spec_file.name}: {e}")

    def _cleanup_package_folder(self, package_path: Path, iflapp_path: Path):
        """Elimina la carpeta temporal del paquete tras crear el `.iflapp`."""
        if package_path.exists() and package_path.is_dir() and iflapp_path.exists():
            try:
                shutil.rmtree(package_path)
                self.log(f"[INFO] Carpeta del paquete eliminada: {package_path.name}")
                self.log(f"[INFO] Solo queda el archivo .iflapp: {iflapp_path.name}")
            except OSError as exc:
                self.log(f"[WARN] No se pudo eliminar la carpeta del paquete {package_path.name}: {exc}")

    def cleanup_processed_project(self, iflapp_path: Path, allow_delete: bool = False) -> bool:
        """Elimina el proyecto fuente solo cuando el llamador lo autoriza.

        La conservación es el comportamiento seguro por defecto. Incluso con
        autorización, el archivo ``.iflapp`` debe existir, ser un contenedor
        válido (v2 o ZIP histórico) y quedar fuera del directorio fuente.
        """
        source_path = self.repo_path.resolve()
        artifact_path = Path(iflapp_path).resolve()
        if not allow_delete:
            self.log("[INFO] Proyecto fuente conservado; la eliminación requiere autorización explícita.")
            return False
        if not artifact_path.is_file() or not iflapp_format.is_valid_container(artifact_path):
            self.log("[WARN] Se conserva el proyecto: el archivo .iflapp no es válido.")
            return False
        if source_path == artifact_path.parent or source_path in artifact_path.parents:
            self.log("[WARN] Se conserva el proyecto: el .iflapp está dentro de la carpeta fuente.")
            return False
        try:
            shutil.rmtree(source_path)
            self.log(f"[INFO] Proyecto procesado eliminado: {source_path.name}")
            return True
        except OSError as exc:
            self.log(f"[WARN] No se pudo eliminar el proyecto procesado {source_path.name}: {exc}")
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
        try:
            for platform_name in platforms_to_compile:
                if not self.compile_binaries(platform_name):
                    return None
                if not self.create_package(platform_name):
                    return None
                platform_suffix = "Knosthalij" if platform_name == "Windows" else "Danenone"

                # Usar ProjectNameFormatter para formato consistente
                package_name = ProjectNameFormatter.format_package_folder(
                    self.metadata['publisher'],
                    self.metadata['app'],
                    self.metadata['version'],
                    platform_suffix
                )
                last_package_path = self.output_path / package_name

                # Blindaje opcional del árbol de paquete antes de empaquetar.
                if self.hardening_methods:
                    self.apply_hardening(last_package_path)
                
                iflapp_name = ProjectNameFormatter.format_iflapp_filename(
                    self.metadata['publisher'],
                    self.metadata['app'],
                    self.metadata['version'],
                    platform_suffix
                )
                iflapp_path = self.output_path / iflapp_name
                
                if self.compress_to_iflapp(last_package_path, iflapp_path):
                    final_iflapp = iflapp_path
                    self.log(f"[SUCCESS] Package created: {iflapp_path}")
                    # Verificar el contenedor en el sandbox antes de publicarlo.
                    self.verify_in_sandbox(iflapp_path)
                    if self.build_dropper:
                        self.create_dropper(iflapp_path)
                    # Limpiar la carpeta temporal y el proyecto fuente tras validar el .iflapp.
                    self._cleanup_package_folder(last_package_path, iflapp_path)
                    self.cleanup_processed_project(iflapp_path)
        finally:
            # Limpiar siempre al finalizar, sea éxito o error
            self._cleanup_build_artifacts()
            
        return final_iflapp

class BuildThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(
        self,
        empresa,
        nombre,
        version,
        plataforma,
        parent=None,
        custom_path=None,
        base_dir=None,
        build_mode="portable",
        compiler_name=None,
        sandbox=True,
        build_dropper=False,
        hardening=None,
    ):
        super().__init__(parent)
        self.empresa = empresa
        self.nombre = nombre
        self.version = version
        self.plataforma = plataforma
        self.custom_path = custom_path
        self.build_mode = build_mode
        self.base_dir = base_dir
        self.compiler_name = compiler_name
        self.sandbox = sandbox
        self.build_dropper = build_dropper
        self.hardening = list(hardening) if hardening else []
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
        compiler = FlangCompiler(
            repo_path,
            Path(self.base_dir or Path.cwd()),
            log_callback=self.handle_compiler_log,
            compiler_name=self.compiler_name,
            sandbox=self.sandbox,
            build_dropper=self.build_dropper,
            hardening=self.hardening,
        )
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
