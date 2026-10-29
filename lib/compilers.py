# -*- coding: utf-8 -*-
"""Registro de compiladores para PackageMaker.

Sustituye el flujo rígido de PyInstaller por una capa de backends
intercambiables. Se soportan:

* ``nuitka``      — compilación a C/C++ (binario nativo, blindaje fuerte).
* ``pyinstaller`` — backend histórico embebido (compatibilidad).
* ``cx_freeze``   — empaquetado alternativo multiplataforma.
* ``pyoxidizer``  — binario Rust-embed para despliegues avanzados.

Cada backend implementa la misma interfaz :class:`CompilerBackend`, de modo que
``FlangCompiler`` puede delegar la compilación sin conocer la herramienta.
"""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

DEFAULT_COMPILER = "nuitka"


class CompilerUnavailableError(RuntimeError):
    """El backend solicitado no está instalado ni es instalable."""


class CompilationError(RuntimeError):
    """La compilación falló en el backend seleccionado."""


# --------------------------------------------------------------------------- #
# Interfaz base
# --------------------------------------------------------------------------- #
class CompilerBackend:
    """Interfaz común para todos los compiladores."""

    name = "base"
    display_name = "Base"
    pip_packages: Sequence[str] = ()
    external_tools: Sequence[str] = ()

    def __init__(self, log_callback=None):
        self._log_callback = log_callback
        self.last_error = ""

    def log(self, message: str) -> None:
        if self._log_callback:
            self._log_callback(message)

    # -- disponibilidad --------------------------------------------------- #
    def module_name(self) -> Optional[str]:
        return None

    def is_available(self) -> bool:
        module = self.module_name()
        if module and importlib.util.find_spec(module) is None:
            return False
        for tool in self.external_tools:
            if shutil.which(tool) is None:
                return False
        return True

    def version(self) -> str:
        module = self.module_name()
        if not module:
            return "no aplicable"
        try:
            imported = __import__(module)
            return getattr(imported, "__version__", "desconocida")
        except Exception:
            return "desconocida"

    # -- compilación ------------------------------------------------------ #
    def compile(  # pragma: no cover - delegado a subclases
        self,
        *,
        script_path: str,
        output_name: str,
        output_dir: str,
        icon_path: Optional[str] = None,
        windowed: bool = True,
        onefile: bool = True,
        add_data: Optional[List[Tuple[str, str]]] = None,
        hidden_imports: Optional[List[str]] = None,
        excludes: Optional[List[str]] = None,
        build_dir: Optional[str] = None,
        cwd: Optional[str] = None,
    ) -> Optional[str]:
        raise NotImplementedError

    def cleanup(self) -> None:
        return None


# --------------------------------------------------------------------------- #
# PyInstaller (histórico, embebido)
# --------------------------------------------------------------------------- #
class PyInstallerBackend(CompilerBackend):
    name = "pyinstaller"
    display_name = "PyInstaller (embebido)"
    pip_packages = ("pyinstaller",)

    def module_name(self) -> Optional[str]:
        return "PyInstaller"

    def is_available(self) -> bool:
        return importlib.util.find_spec("PyInstaller") is not None

    def compile(self, **kwargs) -> Optional[str]:
        from lib.pyinstaller_embedded import get_pyinstaller

        pyi = get_pyinstaller()
        if not pyi.is_available():
            self.last_error = "PyInstaller no está disponible como librería."
            return None
        result = pyi.compile_to_exe(
            script_path=kwargs["script_path"],
            output_name=kwargs["output_name"],
            output_dir=kwargs["output_dir"],
            icon_path=kwargs.get("icon_path"),
            windowed=kwargs.get("windowed", True),
            onefile=kwargs.get("onefile", True),
            add_data=kwargs.get("add_data"),
            hidden_imports=kwargs.get("hidden_imports"),
            excludes=kwargs.get("excludes"),
            build_dir=kwargs.get("build_dir"),
            cwd=kwargs.get("cwd"),
        )
        if result is None:
            self.last_error = pyi.get_last_error()
        return result

    def cleanup(self) -> None:
        try:
            from lib.pyinstaller_embedded import get_pyinstaller

            get_pyinstaller().cleanup()
        except Exception:
            pass


# --------------------------------------------------------------------------- #
# Nuitka
# --------------------------------------------------------------------------- #
class NuitkaBackend(CompilerBackend):
    """Compila a C/C++ y produce un binario nativo.

    Nuitka no reescribe el código Python: lo traduce a C y lo enlaza contra
    libpython, lo que endurece el binario frente a la extracción trivial del
    bytecode (a diferencia de un archivo empaquetado por PyInstaller).
    """

    name = "nuitka"
    display_name = "Nuitka (C/C++ nativo)"
    pip_packages = ("nuitka", "ordered-set", "zstandard")

    def module_name(self) -> Optional[str]:
        return "nuitka"

    def is_available(self) -> bool:
        if importlib.util.find_spec("nuitka") is not None:
            return True
        return shutil.which("nuitka") is not None

    def _base_command(self) -> List[str]:
        if importlib.util.find_spec("nuitka") is not None:
            return [sys.executable, "-m", "nuitka"]
        executable = shutil.which("nuitka")
        if not executable:
            raise CompilerUnavailableError("Nuitka no está instalado.")
        return [executable]

    def compile(self, **kwargs) -> Optional[str]:
        script_path = os.path.abspath(kwargs["script_path"])
        output_name = kwargs["output_name"]
        output_dir = os.path.abspath(kwargs["output_dir"])
        onefile = kwargs.get("onefile", True)
        windowed = kwargs.get("windowed", True)
        os.makedirs(output_dir, exist_ok=True)

        command = self._base_command()
        command.append("--standalone" if onefile else "--standalone")
        command.append("--assume-yes-for-downloads")
        command.append(f"--output-dir={output_dir}")
        command.append(f"--output-filename={output_name}")
        command.append("--remove-output")
        command.append("--quiet")

        if onefile:
            command.append("--onefile")

        if windowed:
            if sys.platform.startswith("win"):
                command.append("--windows-console-mode=disable")
            elif sys.platform == "darwin":
                command.append("--macos-create-app-bundle")
        else:
            if sys.platform.startswith("win"):
                command.append("--windows-console-mode=force")

        icon = kwargs.get("icon_path")
        if icon and os.path.isfile(icon):
            if sys.platform.startswith("win") and icon.endswith(".ico"):
                command.append(f"--windows-icon-from-ico={os.path.abspath(icon)}")
            elif sys.platform.startswith("linux"):
                command.append(f"--linux-icon={os.path.abspath(icon)}")
            elif sys.platform == "darwin":
                command.append(f"--macos-app-icon={os.path.abspath(icon)}")

        for src, dst in kwargs.get("add_data") or []:
            if os.path.isdir(src):
                command.append(f"--include-data-dir={os.path.abspath(src)}={dst}")
            else:
                command.append(f"--include-data-files={os.path.abspath(src)}={dst}")

        for module in kwargs.get("hidden_imports") or []:
            command.append(f"--include-module={module}")

        for module in kwargs.get("excludes") or []:
            command.append(f"--nofollow-import-to={module}")

        # Datos y plugin de Qt cuando el proyecto usa PyQt6.
        command.extend(["--enable-plugin=pyqt6", "--include-qt-plugins=sensible,styles"])
        command.append("--nofollow-import-to=tkinter")
        command.append(script_path)

        build_dir = kwargs.get("build_dir")
        cwd = kwargs.get("cwd") or os.path.dirname(script_path) or os.getcwd()
        env = os.environ.copy()
        if build_dir:
            env["NUITKA_CACHE_DIR"] = str(Path(build_dir) / "nuitka_cache")

        self.log(f"[nuitka] {' '.join(command)}")
        try:
            process = subprocess.run(
                command,
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                timeout=7200,
            )
        except FileNotFoundError as exc:
            self.last_error = f"Nuitka no ejecutable: {exc}"
            return None
        except subprocess.TimeoutExpired:
            self.last_error = "Nuitka excedió el tiempo máximo de compilación."
            return None

        if process.returncode != 0:
            self.last_error = (process.stderr or process.stdout or "fallo desconocido").strip()[-4000:]
            return None

        candidate = self._locate_output(output_dir, output_name)
        if candidate is None:
            self.last_error = "Nuitka finalizó pero no se encontró el binario esperado."
            return None
        return str(candidate)

    @staticmethod
    def _locate_output(output_dir: str, output_name: str) -> Optional[Path]:
        root = Path(output_dir)
        for suffix in (".exe", ".bin", ""):
            candidate = root / f"{output_name}{suffix}"
            if candidate.is_file():
                return candidate
        # Nuitka onefile puede anidar el binario en un subdirectorio.
        for candidate in root.rglob(f"{output_name}*"):
            if candidate.is_file() and os.access(candidate, os.X_OK):
                return candidate
        return None


# --------------------------------------------------------------------------- #
# cx_Freeze
# --------------------------------------------------------------------------- #
class CxFreezeBackend(CompilerBackend):
    name = "cx_freeze"
    display_name = "cx_Freeze"
    pip_packages = ("cx_Freeze",)

    def module_name(self) -> Optional[str]:
        return "cx_Freeze"

    def is_available(self) -> bool:
        return importlib.util.find_spec("cx_Freeze") is not None or shutil.which("cxfreeze") is not None

    def compile(self, **kwargs) -> Optional[str]:
        script_path = os.path.abspath(kwargs["script_path"])
        output_name = kwargs["output_name"]
        output_dir = os.path.abspath(kwargs["output_dir"])
        build_dir = kwargs.get("build_dir") or tempfile.mkdtemp(prefix="cxfreeze_")
        os.makedirs(output_dir, exist_ok=True)

        includes = ",".join(kwargs.get("hidden_imports") or [])
        excludes = ",".join(kwargs.get("excludes") or [])

        setup_script = Path(build_dir) / "cxfreeze_setup.py"
        setup_script.write_text(
            "\n".join(
                [
                    "from cx_Freeze import setup, Executable",
                    "import sys",
                    "build_exe_options = {",
                    f"    'build_exe': {str(Path(build_dir) / 'build')!r},",
                    f"    'includes': [m for m in {includes!r}.split(',') if m],",
                    f"    'excludes': [m for m in {excludes!r}.split(',') if m],",
                    "    'include_files': [],",
                    "}",
                    "base = None",
                    f"exe = Executable({script_path!r}, base=base, target_name={output_name!r})",
                    "setup(name='iflapp', version='1.0', options={'build_exe': build_exe_options}, executables=[exe])",
                ]
            ),
            encoding="utf-8",
        )

        command = [sys.executable, str(setup_script), "build_exe"]
        self.log(f"[cx_freeze] {' '.join(command)}")
        try:
            process = subprocess.run(
                command,
                cwd=kwargs.get("cwd") or os.path.dirname(script_path) or os.getcwd(),
                capture_output=True,
                text=True,
                timeout=7200,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            self.last_error = f"cx_Freeze no ejecutable: {exc}"
            return None

        if process.returncode != 0:
            self.last_error = (process.stderr or process.stdout or "fallo desconocido").strip()[-4000:]
            return None

        built_root = Path(build_dir) / "build"
        exe_name = f"{output_name}.exe" if sys.platform.startswith("win") else output_name
        candidate = built_root / exe_name
        if not candidate.is_file():
            self.last_error = "cx_Freeze no generó el ejecutable esperado."
            return None
        destination = Path(output_dir) / exe_name
        shutil.copy2(candidate, destination)
        return str(destination)


# --------------------------------------------------------------------------- #
# PyOxidizer
# --------------------------------------------------------------------------- #
class PyOxidizerBackend(CompilerBackend):
    name = "pyoxidizer"
    display_name = "PyOxidizer (embed Rust)"
    external_tools = ("pyoxidizer",)

    def is_available(self) -> bool:
        return shutil.which("pyoxidizer") is not None

    def version(self) -> str:
        executable = shutil.which("pyoxidizer")
        if not executable:
            return "no instalado"
        try:
            result = subprocess.run([executable, "--version"], capture_output=True, text=True, timeout=15)
            return (result.stdout or result.stderr).strip() or "desconocida"
        except Exception:
            return "desconocida"

    def compile(self, **kwargs) -> Optional[str]:
        executable = shutil.which("pyoxidizer")
        if not executable:
            self.last_error = "PyOxidizer no está instalado (requiere Rust y el binario pyoxidizer)."
            return None
        script_path = os.path.abspath(kwargs["script_path"])
        output_dir = os.path.abspath(kwargs["output_dir"])
        build_dir = kwargs.get("build_dir") or tempfile.mkdtemp(prefix="pyoxidizer_")
        config = Path(build_dir) / "pyoxidizer.bzl"
        config.write_text(
            "\n".join(
                [
                    "def make_exe():",
                    "    dist = default_python_distribution()",
                    "    policy = dist.make_python_packaging_policy()",
                    "    python_config = dist.make_python_interpreter_config()",
                    f"    python_config.run_module = {Path(script_path).stem!r}",
                    "    exe = dist.to_python_executable(",
                    "        name=" + repr(kwargs["output_name"]) + ",",
                    "        packaging_policy=policy,",
                    "        config=python_config,",
                    "    )",
                    f"    exe.add_python_resources(exe.pip_install([{str(Path(script_path).parent)!r}]))",
                    "    return exe",
                    "",
                    "def make_install(exe):",
                    "    files = FileManifest()",
                    "    files.add_python_resource('.', exe)",
                    "    return files",
                    "",
                    "register_target('install', make_install(make_exe()))",
                ]
            ),
            encoding="utf-8",
        )
        self.log(f"[pyoxidizer] build en {config}")
        try:
            process = subprocess.run(
                [executable, "build", "--path", build_dir],
                capture_output=True,
                text=True,
                timeout=7200,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            self.last_error = f"PyOxidizer no ejecutable: {exc}"
            return None
        if process.returncode != 0:
            self.last_error = (process.stderr or process.stdout or "fallo desconocido").strip()[-4000:]
            return None
        exe_name = f"{kwargs['output_name']}.exe" if sys.platform.startswith("win") else kwargs["output_name"]
        for candidate in Path(build_dir).rglob(exe_name):
            destination = Path(output_dir) / exe_name
            shutil.copy2(candidate, destination)
            return str(destination)
        self.last_error = "PyOxidizer no generó el ejecutable esperado."
        return None


_BACKENDS: Dict[str, type] = {
    "nuitka": NuitkaBackend,
    "pyinstaller": PyInstallerBackend,
    "cx_freeze": CxFreezeBackend,
    "cxfreeze": CxFreezeBackend,
    "pyoxidizer": PyOxidizerBackend,
}


def backend_names() -> List[str]:
    """Nombres canónicos de los backends disponibles."""
    return ["nuitka", "pyinstaller", "cx_freeze", "pyoxidizer"]


def get_backend(name: str, log_callback=None) -> CompilerBackend:
    key = (name or DEFAULT_COMPILER).strip().lower()
    if key not in _BACKENDS:
        raise CompilerUnavailableError(f"Compilador desconocido: {name!r}")
    return _BACKENDS[key](log_callback=log_callback)


def available_backends(log_callback=None) -> Dict[str, Dict[str, object]]:
    """Mapa de backends con estado de disponibilidad y versión."""
    report: Dict[str, Dict[str, object]] = {}
    for name in backend_names():
        backend = get_backend(name, log_callback=log_callback)
        report[name] = {
            "display_name": backend.display_name,
            "available": backend.is_available(),
            "version": backend.version() if backend.is_available() else "no instalado",
            "pip_packages": list(backend.pip_packages),
        }
    return report


def resolve_backend(preferred: Optional[str] = None, log_callback=None) -> CompilerBackend:
    """Devuelve el backend preferido o el primer sustituto disponible.

    Se conserva ``pyinstaller`` como último recurso para no romper flujos
    existentes cuando Nuitka todavía no está instalado.
    """
    order: List[str] = []
    if preferred:
        order.append(preferred.strip().lower())
    order.append(DEFAULT_COMPILER)
    order.extend(["pyinstaller", "cx_freeze", "pyoxidizer"])

    seen = set()
    for name in order:
        if not name or name in seen:
            continue
        seen.add(name)
        try:
            backend = get_backend(name, log_callback=log_callback)
        except CompilerUnavailableError:
            continue
        if backend.is_available():
            return backend
    raise CompilerUnavailableError(
        "No hay ningún compilador disponible. Instala Nuitka o PyInstaller."
    )


def ensure_backend(name: str, log_callback=None) -> bool:
    """Instala las dependencias pip del backend si falta el módulo principal."""
    backend = get_backend(name, log_callback=log_callback)

    def _log(message: str) -> None:
        if log_callback:
            log_callback(message)
        else:
            print(message)

    if backend.is_available():
        return True
    if not backend.pip_packages:
        _log(f"[ERROR] {backend.display_name} requiere herramientas externas no instalables por pip.")
        return False

    _log(f"[INFO] {backend.display_name} no encontrado. Instalando dependencias...")
    try:
        process = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", *backend.pip_packages],
            capture_output=True,
            text=True,
            timeout=900,
        )
    except Exception as exc:
        _log(f"[ERROR] No se pudo instalar {backend.display_name}: {exc}")
        return False
    if process.returncode != 0:
        _log(f"[ERROR] pip falló: {(process.stderr or process.stdout).strip()[-1500:]}")
        return False
    if backend.is_available():
        _log(f"[OK] {backend.display_name} instalado ({backend.version()}).")
        return True
    _log(f"[ERROR] {backend.display_name} instalado pero no importable.")
    return False
