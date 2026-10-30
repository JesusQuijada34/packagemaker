# -*- coding: utf-8 -*-
"""Registro de compiladores para PackageMaker.

Se exponen varios backends, con dos **embebidos** (se ejecutan dentro del mismo
intérprete Python, sin lanzar el binario como proceso externo):

* ``nuitka``      — traduce a C/C++ y enlaza contra libpython (binario nativo,
  blindaje fuerte). Es el backend recomendado por defecto.
* ``pyinstaller`` — empaqueta bytecode + intérprete (rápido, amplia
  compatibilidad, extracción trivial).
* ``zipapp``      — usa ``zipapp`` de la biblioteca estándar para producir un
  ``.pyz`` portable; siempre disponible, sin dependencias externas.
* ``cxfreeze``    — congela el proyecto con ``cx_Freeze`` (herramienta externa).
* ``pyoxidizer``  — genera un binario Rust autocontenido (herramienta externa).

Todos comparten exactamente la misma firma de :meth:`CompilerBackend.compile`
y el mismo conjunto de parámetros (icono, onefile, datos, imports ocultos,
exclusiones), de modo que el resto del programa no distingue cuál se usa.

``resolve_backend`` degrada de forma controlada si el backend preferido no está
instalado, cayendo a Nuitka y después a PyInstaller.
"""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
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
    """Interfaz común para todos los compiladores embebidos."""

    name = "base"
    display_name = "Base"
    pip_packages: Sequence[str] = ()
    embedded = True

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
# PyInstaller (embebido)
# --------------------------------------------------------------------------- #
class PyInstallerBackend(CompilerBackend):
    name = "pyinstaller"
    display_name = "PyInstaller (embebido)"
    pip_packages = ("pyinstaller",)

    def module_name(self) -> Optional[str]:
        return "PyInstaller"

    def is_available(self) -> bool:
        return importlib.util.find_spec("PyInstaller") is not None

    def version(self) -> str:
        try:
            from lib.pyinstaller_embedded import pyi_version

            return pyi_version
        except Exception:
            return super().version()

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
# Nuitka (embebido, por defecto)
# --------------------------------------------------------------------------- #
class NuitkaBackend(CompilerBackend):
    """Compila a C/C++ y produce un binario nativo, sin subproceso externo.

    Nuitka no reescribe el código Python: lo traduce a C y lo enlaza contra
    libpython, lo que endurece el binario frente a la extracción trivial del
    bytecode (a diferencia de un archivo empaquetado por PyInstaller).
    """

    name = "nuitka"
    display_name = "Nuitka (C/C++ nativo, embebido)"
    pip_packages = ("nuitka", "ordered-set", "zstandard")

    def module_name(self) -> Optional[str]:
        return "nuitka"

    def version(self) -> str:
        try:
            from lib.nuitka_embedded import nuitka_version

            return nuitka_version
        except Exception:
            return super().version()

    def compile(self, **kwargs) -> Optional[str]:
        from lib.nuitka_embedded import get_nuitka

        nk = get_nuitka()
        if not nk.is_available():
            self.last_error = "Nuitka no está disponible como librería."
            return None
        result = nk.compile_to_exe(
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
            self.last_error = nk.get_last_error()
        return result

    def cleanup(self) -> None:
        try:
            from lib.nuitka_embedded import get_nuitka

            get_nuitka().cleanup()
        except Exception:
            pass


# --------------------------------------------------------------------------- #
# zipapp (stdlib, siempre disponible)
# --------------------------------------------------------------------------- #
class ZipappBackend(CompilerBackend):
    """Empaqueta el proyecto como ejecutable ``.pyz`` con ``zipapp``.

    Es el único backend que **no** necesita ninguna dependencia externa: usa la
    biblioteca estándar. No produce un binario nativo (requiere el intérprete
    del sistema), así que se ofrece como alternativa ligera y reproducible.
    """

    name = "zipapp"
    display_name = "zipapp (stdlib, .pyz portable)"
    pip_packages: Sequence[str] = ()

    def module_name(self) -> Optional[str]:
        return "zipapp"

    def version(self) -> str:
        return f"stdlib {sys.version_info.major}.{sys.version_info.minor}"

    def compile(self, **kwargs) -> Optional[str]:
        import zipapp

        script_path = Path(kwargs["script_path"]).resolve()
        output_dir = Path(kwargs["output_dir"]).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        output_name = kwargs["output_name"]
        target = output_dir / f"{output_name}.pyz"

        source_root = script_path.parent
        main = script_path.name
        try:
            zipapp.create_archive(
                source_root,
                target=target,
                main=f"{main[:-3] if main.endswith('.py') else main}:main"
                if _defines_main(script_path)
                else main,
                interpreter="/usr/bin/env python3",
                compressed=True,
            )
        except Exception as exc:
            self.last_error = f"zipapp falló: {exc}"
            return None
        if not target.is_file():
            self.last_error = "zipapp no generó el archivo esperado"
            return None
        return str(target)


def _defines_main(script_path: Path) -> bool:
    """Indica si el script define una función ``main`` invocable."""
    try:
        import ast

        tree = ast.parse(script_path.read_text(encoding="utf-8"))
    except Exception:
        return False
    return any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "main"
        for node in tree.body
    )


# --------------------------------------------------------------------------- #
# cx_Freeze (herramienta externa)
# --------------------------------------------------------------------------- #
class CxFreezeBackend(CompilerBackend):
    """Congela el proyecto con ``cx_Freeze`` (``cxfreeze`` o ``-m cx_Freeze``)."""

    name = "cxfreeze"
    display_name = "cx_Freeze (binario congelado)"
    pip_packages = ("cx_Freeze",)
    embedded = False

    def module_name(self) -> Optional[str]:
        return "cx_Freeze"

    def compile(self, **kwargs) -> Optional[str]:
        output_dir = Path(kwargs["output_dir"]).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        target = output_dir / kwargs["output_name"]
        exe = shutil.which("cxfreeze")
        if exe:
            argv = [exe, str(Path(kwargs["script_path"]).resolve()), "--target-dir", str(target)]
        else:
            argv = [
                sys.executable, "-m", "cx_Freeze",
                str(Path(kwargs["script_path"]).resolve()),
                "--target-dir", str(target),
            ]
        if kwargs.get("icon_path"):
            argv += ["--icon", str(kwargs["icon_path"])]
        for module in kwargs.get("hidden_imports") or []:
            argv += ["--include-modules", module]
        for module in kwargs.get("excludes") or []:
            argv += ["--exclude-modules", module]
        try:
            proc = _run_compiler(argv, cwd=kwargs.get("cwd"))
        except Exception as exc:
            self.last_error = f"cx_Freeze no se pudo ejecutar: {exc}"
            return None
        if proc.returncode != 0:
            self.last_error = (proc.stderr or proc.stdout or "").strip()[-1500:]
            return None
        return str(_first_executable(target)) or str(target)


# --------------------------------------------------------------------------- #
# PyOxidizer (herramienta externa)
# --------------------------------------------------------------------------- #
class PyOxidizerBackend(CompilerBackend):
    """Empaqueta el proyecto con ``pyoxidizer`` en un binario Rust autocontenido."""

    name = "pyoxidizer"
    display_name = "PyOxidizer (binario Rust autocontenido)"
    pip_packages: Sequence[str] = ()
    embedded = False

    def module_name(self) -> Optional[str]:
        return None

    def is_available(self) -> bool:
        return shutil.which("pyoxidizer") is not None

    def version(self) -> str:
        exe = shutil.which("pyoxidizer")
        if not exe:
            return "no instalado"
        try:
            proc = _run_compiler([exe, "--version"])
            return (proc.stdout or proc.stderr or "").strip().splitlines()[0] or "desconocida"
        except Exception:
            return "desconocida"

    def compile(self, **kwargs) -> Optional[str]:
        exe = shutil.which("pyoxidizer")
        if not exe:
            self.last_error = "pyoxidizer no está en PATH."
            return None
        script_path = Path(kwargs["script_path"]).resolve()
        output_dir = Path(kwargs["output_dir"]).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        config = output_dir / "pyoxidizer.bzl"
        config.write_text(_pyoxidizer_config(script_path, kwargs["output_name"]), encoding="utf-8")
        try:
            proc = _run_compiler(
                [exe, "build", "--path", str(output_dir)],
                cwd=str(output_dir),
                timeout=1800,
            )
        except Exception as exc:
            self.last_error = f"pyoxidizer no se pudo ejecutar: {exc}"
            return None
        if proc.returncode != 0:
            self.last_error = (proc.stderr or proc.stdout or "").strip()[-1500:]
            return None
        binary = _first_executable(output_dir / "build")
        if binary is None:
            self.last_error = "pyoxidizer no generó ningún binario"
            return None
        return str(binary)


def _pyoxidizer_config(script_path: Path, output_name: str) -> str:
    return (
        'def make_exe():\n'
        '    dist = default_python_distribution()\n'
        '    policy = dist.make_python_packaging_policy()\n'
        '    python_config = dist.make_python_interpreter_config()\n'
        f'    python_config.run_filename = r"{script_path}"\n'
        '    exe = dist.to_python_executable(\n'
        f'        name="{output_name}",\n'
        '        packaging_policy=policy,\n'
        '        config=python_config,\n'
        '    )\n'
        f'    exe.add_python_resources(exe.pip_install([r"{script_path.parent}"]))\n'
        '    return exe\n'
        '\n'
        'def make_install(exe):\n'
        '    files = FileManifest()\n'
        '    files.add_python_resource(".", exe)\n'
        '    return files\n'
        '\n'
        'register_target("exe", make_exe)\n'
        'register_target("install", make_install, depends=["exe"], default=True)\n'
        'resolve_targets()\n'
    )


def _run_compiler(argv: Sequence[str], *, cwd: Optional[str] = None, timeout: int = 1800):
    return subprocess.run(
        list(argv),
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
    )


def _first_executable(root: Path) -> Optional[Path]:
    """Primer archivo ejecutable bajo *root* (búsqueda superficial)."""
    if not root.exists():
        return None
    for candidate in sorted(root.rglob("*")):
        if candidate.is_file() and os.access(candidate, os.X_OK) and not candidate.suffix in (".py", ".bzl", ".txt", ".json"):
            return candidate
    return None


_BACKENDS: Dict[str, type] = {
    "nuitka": NuitkaBackend,
    "pyinstaller": PyInstallerBackend,
    "zipapp": ZipappBackend,
    "cxfreeze": CxFreezeBackend,
    "pyoxidizer": PyOxidizerBackend,
}

# Alias históricos que aún no son backends propios.
_ALIASES: Dict[str, str] = {
    "cx_freeze": "cxfreeze",
    "zip": "zipapp",
    "pyz": "zipapp",
}


def backend_names() -> List[str]:
    """Nombres canónicos de los backends disponibles."""
    return ["nuitka", "pyinstaller", "zipapp", "cxfreeze", "pyoxidizer"]


def get_backend(name: str, log_callback=None) -> CompilerBackend:
    key = (name or DEFAULT_COMPILER).strip().lower()
    key = _ALIASES.get(key, key)
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
            "embedded": backend.embedded,
        }
    return report


def resolve_backend(preferred: Optional[str] = None, log_callback=None) -> CompilerBackend:
    """Devuelve el backend preferido o el primer sustituto disponible.

    Nuitka es el preferido; PyInstaller queda como respaldo por compatibilidad.
    """
    order: List[str] = []
    if preferred:
        order.append(preferred.strip().lower())
    order.append(DEFAULT_COMPILER)
    order.append("pyinstaller")
    # zipapp usa la biblioteca estándar: garantiza que siempre haya un backend.
    order.append("zipapp")

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
