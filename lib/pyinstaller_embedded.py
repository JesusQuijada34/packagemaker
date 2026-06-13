"""
PyInstaller embebido: usa la API de PyInstaller desde el mismo intérprete Python.
No invoca el ejecutable pyinstaller como subproceso externo.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

PYINSTALLER_AVAILABLE = False
pyi_version = "No disponible"


def _refresh_pyinstaller_availability() -> bool:
    global PYINSTALLER_AVAILABLE, pyi_version
    try:
        import PyInstaller
        pyi_version = PyInstaller.__version__
        PYINSTALLER_AVAILABLE = True
        return True
    except ImportError:
        PYINSTALLER_AVAILABLE = False
        pyi_version = "No disponible"
        return False


_refresh_pyinstaller_availability()


class EmbeddedPyInstaller:
    """Compila scripts usando PyInstaller.__main__.run() en el proceso actual."""

    def __init__(self):
        self.available = PYINSTALLER_AVAILABLE
        self._temp_build_dir: Optional[str] = None
        self._last_error: Optional[str] = None

    def get_last_error(self) -> str:
        return self._last_error or "Error desconocido"

    def is_available(self) -> bool:
        return self.available

    def get_version(self) -> str:
        return pyi_version if self.available else "No disponible"

    def _prepare_build_env(self, build_dir: Optional[str] = None) -> str:
        if build_dir is None:
            self._temp_build_dir = tempfile.mkdtemp(prefix="pyi_build_")
            build_dir = self._temp_build_dir
        else:
            self._temp_build_dir = build_dir
        os.makedirs(build_dir, exist_ok=True)
        os.makedirs(os.path.join(build_dir, "spec"), exist_ok=True)
        os.makedirs(os.path.join(build_dir, "work"), exist_ok=True)
        return build_dir

    def compile_to_exe(
        self,
        script_path: str,
        output_name: str,
        output_dir: Optional[str] = None,
        icon_path: Optional[str] = None,
        windowed: bool = True,
        onefile: bool = True,
        add_data: Optional[List[Tuple[str, str]]] = None,
        hidden_imports: Optional[List[str]] = None,
        excludes: Optional[List[str]] = None,
        build_dir: Optional[str] = None,
        cwd: Optional[str] = None,
    ) -> Optional[str]:
        self._last_error = None
        if not self.available:
            self._last_error = "PyInstaller no está disponible como librería"
            return None

        script_path = os.path.abspath(script_path)
        if not os.path.isfile(script_path):
            self._last_error = f"Script no encontrado: {script_path}"
            return None

        build_path = self._prepare_build_env(build_dir)
        dist_dir = os.path.abspath(output_dir or os.path.join(os.getcwd(), "dist"))
        os.makedirs(dist_dir, exist_ok=True)

        args = [
            "--onefile" if onefile else "--onedir",
            "--name",
            output_name,
            "--distpath",
            dist_dir,
            "--workpath",
            os.path.join(build_path, "work"),
            "--specpath",
            os.path.join(build_path, "spec"),
            "--noconfirm",
        ]
        if windowed:
            args.append("--windowed")
        else:
            args.append("--console")
            # En Linux, optimizar búsqueda de libpython
            if sys.platform.startswith("linux"):
                args.extend([
                    "--bootloader-ignore-signals",
                    "--copy-metadata=PyInstaller",
                ])
        if icon_path and os.path.isfile(icon_path):
            # Convertir ICO a PNG en Linux si es necesario
            if sys.platform.startswith("linux") and icon_path.endswith(".ico"):
                try:
                    from lib.linux_icon_handler import convert_ico_to_png
                    png_path = icon_path.replace(".ico", ".png")
                    if convert_ico_to_png(icon_path, png_path):
                        icon_path = png_path
                except Exception:
                    pass
            args.extend(["--icon", os.path.abspath(icon_path)])
        if add_data:
            for src, dst in add_data:
                args.extend(["--add-data", f"{os.path.abspath(src)}{os.pathsep}{dst}"])
        if hidden_imports:
            for imp in hidden_imports:
                args.extend(["--hidden-import", imp])
        
        # Agregar excludes por defecto para acelerar compilación
        default_excludes = ["matplotlib", "numpy", "scipy", "pandas", "sklearn", "tf", "keras"]
        if excludes is None:
            excludes = default_excludes
        else:
            excludes.extend(default_excludes)
        
        for exc in set(excludes):  # Usar set para evitar duplicados
            args.extend(["--exclude-module", exc])
        
        args.append(script_path)

        old_argv = sys.argv[:]
        old_cwd = os.getcwd()
        try:
            if cwd:
                os.chdir(cwd)
            from PyInstaller import __main__ as pyi_main

            sys.argv = ["pyinstaller"] + args
            pyi_main.run()
        except Exception as e:
            import traceback
            self._last_error = f"{str(e)}\n{traceback.format_exc()}"
            return None
        finally:
            sys.argv = old_argv
            os.chdir(old_cwd)

        exe_name = output_name + (".exe" if sys.platform == "win32" else "")
        final_exe_path = os.path.join(dist_dir, exe_name)
        if os.path.isfile(final_exe_path):
            return final_exe_path
        self._last_error = "PyInstaller finalizó pero no se generó el ejecutable esperado"
        return None

    def cleanup(self):
        if self._temp_build_dir and os.path.isdir(self._temp_build_dir):
            shutil.rmtree(self._temp_build_dir, ignore_errors=True)
            self._temp_build_dir = None


_embedded_pyinstaller: Optional[EmbeddedPyInstaller] = None


def get_pyinstaller() -> EmbeddedPyInstaller:
    global _embedded_pyinstaller
    if _embedded_pyinstaller is None:
        _embedded_pyinstaller = EmbeddedPyInstaller()
    return _embedded_pyinstaller


def ensure_pyinstaller(log_callback=None) -> bool:
    """Instala PyInstaller con pip en el intérprete actual si no está importable."""

    def _log(msg: str):
        if log_callback:
            log_callback(msg)
        else:
            print(msg)

    pyi = get_pyinstaller()
    if pyi.is_available():
        return True

    _log("[INFO] PyInstaller no encontrado. Instalando automáticamente...")
    try:
        import subprocess

        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pyinstaller"],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            err = (result.stderr or result.stdout or "").strip()
            _log(f"[ERROR] pip install pyinstaller falló: {err}")
            return False
    except Exception as e:
        _log(f"[ERROR] No se pudo instalar PyInstaller: {e}")
        return False

    if _refresh_pyinstaller_availability():
        pyi.available = True
        _log(f"[OK] PyInstaller instalado: {pyi_version}")
        return True

    _log("[ERROR] PyInstaller instalado pero no se pudo importar")
    return False
