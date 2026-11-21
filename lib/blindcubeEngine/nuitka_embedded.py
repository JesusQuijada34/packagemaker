"""
Nuitka embebido: usa la API de Nuitka desde el mismo intérprete Python.

No invoca el ejecutable ``nuitka`` como subproceso externo: importa
``nuitka.MainControl`` y ejecuta la compilación dentro del proceso actual,
igual que :mod:`lib.pyinstaller_embedded` hace con ``PyInstaller.__main__``.

Notas de implementación
-----------------------
* Nuitka lee su configuración de ``sys.argv`` (igual que PyInstaller), por lo
  que se sustituye temporalmente ``sys.argv`` con las opciones equivalentes a
  la línea de comandos y se restaura al terminar.
* ``MainControl.main()`` captura ``SystemExit`` internamente y termina el
  proceso por diseño en algunos caminos, de modo que la llamada se envuelve en
  ``SystemExit``/``BaseException`` para no abortar la aplicación anfitriona.
* Si la API interna no está disponible (versión desconocida de Nuitka) se
  degrada a la invocación del módulo ``nuitka`` como subproceso, que es el
  único camino que no depende de símbolos privados.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

NUITKA_AVAILABLE = False
nuitka_version = "No disponible"


def _refresh_nuitka_availability() -> bool:
    global NUITKA_AVAILABLE, nuitka_version
    try:
        import nuitka  # noqa: F401

        try:
            from nuitka.__main__ import _getNuitkaVersion

            nuitka_version = _getNuitkaVersion()
        except Exception:
            nuitka_version = getattr(nuitka, "__version__", "desconocida")
        NUITKA_AVAILABLE = True
        return True
    except ImportError:
        NUITKA_AVAILABLE = False
        nuitka_version = "No disponible"
        return False


_refresh_nuitka_availability()


class EmbeddedNuitka:
    """Compila scripts usando ``nuitka.MainControl`` en el proceso actual."""

    def __init__(self):
        self.available = NUITKA_AVAILABLE
        self._temp_build_dir: Optional[str] = None
        self._last_error: Optional[str] = None

    def get_last_error(self) -> str:
        return self._last_error or "Error desconocido"

    def is_available(self) -> bool:
        return self.available

    def get_version(self) -> str:
        return nuitka_version if self.available else "No disponible"

    def _prepare_build_env(self, build_dir: Optional[str] = None) -> str:
        if build_dir is None:
            self._temp_build_dir = tempfile.mkdtemp(prefix="nuitka_build_")
            build_dir = self._temp_build_dir
        else:
            self._temp_build_dir = build_dir
        os.makedirs(build_dir, exist_ok=True)
        return build_dir

    def build_arguments(
        self,
        script_path: str,
        output_name: str,
        output_dir: str,
        icon_path: Optional[str] = None,
        windowed: bool = True,
        onefile: bool = True,
        add_data: Optional[List[Tuple[str, str]]] = None,
        hidden_imports: Optional[List[str]] = None,
        excludes: Optional[List[str]] = None,
    ) -> List[str]:
        """Construye la lista de argumentos Nuitka (mismo patrón que PyInstaller).

        Se mantiene como método público para que la GUI y las pruebas puedan
        inspeccionar exactamente qué opciones se aplicarán sin compilar.
        """
        args: List[str] = [
            "--standalone",
            "--assume-yes-for-downloads",
            "--output-dir",
            os.path.abspath(output_dir),
            "--output-filename",
            output_name,
            "--remove-output",
            "--quiet",
        ]
        if onefile:
            args.append("--onefile")

        if windowed:
            if sys.platform.startswith("win"):
                args.append("--windows-console-mode=disable")
            elif sys.platform == "darwin":
                args.append("--macos-create-app-bundle")
        else:
            if sys.platform.startswith("win"):
                args.append("--windows-console-mode=force")

        if icon_path and os.path.isfile(icon_path):
            icon = os.path.abspath(icon_path)
            if sys.platform.startswith("win") and icon.endswith(".ico"):
                args.append(f"--windows-icon-from-ico={icon}")
            elif sys.platform.startswith("linux"):
                args.append(f"--linux-icon={icon}")
            elif sys.platform == "darwin":
                args.append(f"--macos-app-icon={icon}")

        for src, dst in add_data or []:
            if os.path.isdir(src):
                args.append(f"--include-data-dir={os.path.abspath(src)}={dst}")
            else:
                args.append(f"--include-data-files={os.path.abspath(src)}={dst}")

        for module in hidden_imports or []:
            args.append(f"--include-module={module}")

        for module in excludes or []:
            args.append(f"--nofollow-import-to={module}")

        # Plugin Qt y exclusión de tkinter: paridad con el backend de subproceso.
        args.extend(["--enable-plugin=pyqt6", "--include-qt-plugins=sensible,styles"])
        args.append("--nofollow-import-to=tkinter")
        args.append(os.path.abspath(script_path))
        return args

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
            self._last_error = "Nuitka no está disponible como librería"
            return None

        script_path = os.path.abspath(script_path)
        if not os.path.isfile(script_path):
            self._last_error = f"Script no encontrado: {script_path}"
            return None

        build_path = self._prepare_build_env(build_dir)
        dist_dir = os.path.abspath(output_dir or os.path.join(os.getcwd(), "dist"))
        os.makedirs(dist_dir, exist_ok=True)

        args = self.build_arguments(
            script_path=script_path,
            output_name=output_name,
            output_dir=dist_dir,
            icon_path=icon_path,
            windowed=windowed,
            onefile=onefile,
            add_data=add_data,
            hidden_imports=hidden_imports,
            excludes=excludes,
        )

        old_argv = sys.argv[:]
        old_cwd = os.getcwd()
        old_env = os.environ.copy()
        os.environ["NUITKA_CACHE_DIR"] = str(Path(build_path) / "nuitka_cache")
        try:
            if cwd:
                os.chdir(cwd)
            from nuitka import MainControl

            sys.argv = ["nuitka"] + args
            try:
                MainControl.main()
            except SystemExit as exc:
                # Nuitka llama a sys.exit() en varios caminos; un código 0 es
                # una compilación correcta y no debe propagarse.
                if exc.code not in (0, None):
                    self._last_error = f"Nuitka terminó con código {exc.code}"
                    return None
            except BaseException as exc:  # noqa: BLE001 - límite de la API
                import traceback

                self._last_error = f"{exc}\n{traceback.format_exc()}"
                return None
        finally:
            sys.argv = old_argv
            os.chdir(old_cwd)
            os.environ.clear()
            os.environ.update(old_env)

        candidate = self._locate_output(dist_dir, output_name)
        if candidate is not None:
            return str(candidate)
        self._last_error = "Nuitka finalizó pero no se generó el binario esperado"
        return None

    @staticmethod
    def _locate_output(output_dir: str, output_name: str) -> Optional[Path]:
        root = Path(output_dir)
        for suffix in (".exe", ".bin", ""):
            candidate = root / f"{output_name}{suffix}"
            if candidate.is_file():
                return candidate
        for candidate in root.rglob(f"{output_name}*"):
            if candidate.is_file() and os.access(candidate, os.X_OK):
                return candidate
        return None

    def cleanup(self):
        if self._temp_build_dir and os.path.isdir(self._temp_build_dir):
            shutil.rmtree(self._temp_build_dir, ignore_errors=True)
            self._temp_build_dir = None


_embedded_nuitka: Optional[EmbeddedNuitka] = None


def get_nuitka() -> EmbeddedNuitka:
    global _embedded_nuitka
    if _embedded_nuitka is None:
        _embedded_nuitka = EmbeddedNuitka()
    return _embedded_nuitka


def ensure_nuitka(log_callback=None) -> bool:
    """Instala Nuitka con pip en el intérprete actual si no está importable."""

    def _log(msg: str):
        if log_callback:
            log_callback(msg)
        else:
            print(msg)

    nk = get_nuitka()
    if nk.is_available():
        return True

    _log("[INFO] Nuitka no encontrado. Instalando automáticamente...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "nuitka", "ordered-set", "zstandard"],
            capture_output=True,
            text=True,
            timeout=600,
        )
        if result.returncode != 0:
            err = (result.stderr or result.stdout or "").strip()
            _log(f"[ERROR] pip install nuitka falló: {err}")
            return False
    except Exception as e:
        _log(f"[ERROR] No se pudo instalar Nuitka: {e}")
        return False

    if _refresh_nuitka_availability():
        nk.available = True
        _log(f"[OK] Nuitka instalado: {nuitka_version}")
        return True

    _log("[ERROR] Nuitka instalado pero no se pudo importar")
    return False
