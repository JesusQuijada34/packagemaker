# -*- coding: utf-8 -*-
"""Entorno de compilación aislado por proyecto (Q-019).

Cada proyecto compila dentro de su propio entorno virtual, creado con el
intérprete del sistema en ``<proyecto>/build/pm-sandbox/<backend>/venv``. El
entorno instala las dependencias del proyecto y las del backend, comprueba que
el backend se importa dentro del entorno y ejecuta el compilador como
subproceso; así la compilación no comparte los módulos del proceso de
PackageMaker. El binario se copia después fuera del entorno.

El modo de red **uso medido** (``metered``) desactiva el aislamiento y compila
con el backend embebido: no descarga nada, pero exige el Python del sistema.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

NETWORK_UNRESTRICTED = "unrestricted"
NETWORK_METERED = "metered"
NETWORK_MODES = (NETWORK_UNRESTRICTED, NETWORK_METERED)

# Interruptor de emergencia para pruebas y entornos sin red.
DISABLE_ENV = "PM_BUILD_ISOLATION"

SANDBOX_DIRNAME = "pm-sandbox"
SANDBOX_PARENT = "build"

_ISOLATABLE_BACKENDS = ("nuitka", "pyinstaller")
_BACKEND_MODULES = {"nuitka": "nuitka", "pyinstaller": "PyInstaller"}
_DISPLAY_NAMES = {
    "nuitka": "Nuitka (C/C++ nativo, entorno aislado)",
    "pyinstaller": "PyInstaller (entorno aislado)",
}
_REQUIREMENT_FILES = ("requirements.txt", "lib/requirements.txt")
_MARKER = "installed.json"

_VENV_TIMEOUT = 900
_PIP_TIMEOUT = 1800
_COMPILE_TIMEOUT = 3600
_CHECK_TIMEOUT = 120


def resolve_network_mode(value: object) -> str:
    """Normaliza el modo de red; cualquier valor raro cae en ``unrestricted``."""
    text = str(value or "").strip().lower()
    if text in {"metered", "medido", "uso medido", "measured", "ahorro", "low"}:
        return NETWORK_METERED
    return NETWORK_UNRESTRICTED


def isolation_enabled(network_mode: object = NETWORK_UNRESTRICTED, env=None) -> bool:
    """Indica si se puede compilar en un entorno aislado."""
    environment = os.environ if env is None else env
    flag = str(environment.get(DISABLE_ENV, "")).strip().lower()
    if flag in {"0", "false", "no", "off"}:
        return False
    # Un ejecutable congelado no puede crear un venv con ``sys.executable``.
    if getattr(sys, "frozen", False):
        return False
    return resolve_network_mode(network_mode) == NETWORK_UNRESTRICTED


def network_mode_from_preferences() -> str:
    """Modo de red guardado en Configuración (por defecto, sin restricción)."""
    try:
        from lib.pm_data import get_pm_data

        return resolve_network_mode(get_pm_data().get_user("network_mode", NETWORK_UNRESTRICTED))
    except Exception:
        return NETWORK_UNRESTRICTED


def project_requirements(project_path: Path) -> Tuple[str, ...]:
    """Dependencias declaradas por el proyecto, sin comentarios ni líneas vacías."""
    root = Path(project_path)
    for relative in _REQUIREMENT_FILES:
        candidate = root / relative
        if not candidate.is_file():
            continue
        try:
            lines = candidate.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            return ()
        return tuple(
            line.strip()
            for line in lines
            if line.strip() and not line.strip().startswith("#")
        )
    return ()


@dataclass(frozen=True)
class SandboxPlan:
    """Descripción inspeccionable del entorno aislado de un proyecto."""

    project_path: Path
    root: Path
    venv_dir: Path
    interpreter: Path
    backend: str
    requirements: Tuple[str, ...]
    network_mode: str
    base_python: str

    def as_dict(self) -> Dict[str, object]:
        return {
            "project": str(self.project_path),
            "root": str(self.root),
            "venv": str(self.venv_dir),
            "interpreter": str(self.interpreter),
            "backend": self.backend,
            "requirements": list(self.requirements),
            "network": self.network_mode,
        }


def plan_sandbox(
    project_path: Path,
    *,
    backend: str = "nuitka",
    network_mode: object = NETWORK_UNRESTRICTED,
    base_python: Optional[str] = None,
) -> SandboxPlan:
    """Plan del entorno aislado; ``build/pm-sandbox`` ya queda fuera del paquete."""
    root_project = Path(project_path).resolve()
    root = root_project / SANDBOX_PARENT / SANDBOX_DIRNAME / (backend or "nuitka")
    venv_dir = root / "venv"
    interpreter = venv_dir / ("Scripts/python.exe" if sys.platform.startswith("win") else "bin/python")
    return SandboxPlan(
        project_path=root_project,
        root=root,
        venv_dir=venv_dir,
        interpreter=interpreter,
        backend=(backend or "nuitka").strip().lower(),
        requirements=project_requirements(root_project),
        network_mode=resolve_network_mode(network_mode),
        base_python=base_python or sys.executable,
    )


class BuildSandbox:
    """Entorno virtual del proyecto y compilación por subproceso."""

    def __init__(
        self,
        plan: SandboxPlan,
        *,
        log: Optional[Callable[[str], None]] = None,
        runner: Optional[Callable[..., object]] = None,
    ):
        self.plan = plan
        self.last_error = ""
        self._log = log or (lambda _message: None)
        self._runner = runner or subprocess.run
        self._prepared = False

    # -- preparación ------------------------------------------------------ #
    def _packages(self) -> List[str]:
        from lib.blindcubeEngine.compilers import get_backend

        packages: List[str] = list(self.plan.requirements)
        try:
            backend_packages = list(get_backend(self.plan.backend).pip_packages)
        except Exception:
            backend_packages = []
        for package in backend_packages:
            if package not in packages:
                packages.append(package)
        return packages

    def _run(self, argv: Sequence[str], *, timeout: int) -> Tuple[bool, str]:
        try:
            proc = self._runner(list(argv), capture_output=True, text=True, timeout=timeout)
        except (OSError, subprocess.SubprocessError, ValueError) as exc:
            return False, f"{type(exc).__name__}: {exc}"
        output = f"{getattr(proc, 'stdout', '') or ''}{getattr(proc, 'stderr', '') or ''}".strip()
        if getattr(proc, "returncode", 1) != 0:
            return False, output[-1500:] or f"código {proc.returncode}"
        return True, output

    def _marker_path(self) -> Path:
        return self.plan.root / _MARKER

    def _installed_packages(self) -> List[str]:
        try:
            data = json.loads(self._marker_path().read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return []
        packages = data.get("packages") if isinstance(data, dict) else None
        return [str(item) for item in packages] if isinstance(packages, list) else []

    def _write_marker(self, packages: Sequence[str]) -> None:
        try:
            self._marker_path().write_text(
                json.dumps({"packages": list(packages)}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError:
            pass

    def prepare(self) -> bool:
        """Crea el venv, instala dependencias y comprueba el backend."""
        self.last_error = ""
        try:
            self.plan.root.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            self.last_error = f"no se pudo crear el entorno aislado: {exc}"
            return False

        if not self.plan.interpreter.is_file():
            self._log(f"[INFO] Creando entorno aislado en {self.plan.venv_dir}...")
            ok, detail = self._run(
                [self.plan.base_python, "-m", "venv", str(self.plan.venv_dir)],
                timeout=_VENV_TIMEOUT,
            )
            if not ok:
                self.last_error = f"no se pudo crear el venv: {detail}"
                return False

        packages = self._packages()
        if packages and self._installed_packages() != packages:
            self._log(f"[INFO] Instalando dependencias en el entorno aislado ({len(packages)})...")
            ok, detail = self._run(
                [
                    str(self.plan.interpreter),
                    "-m",
                    "pip",
                    "install",
                    "--disable-pip-version-check",
                    *packages,
                ],
                timeout=_PIP_TIMEOUT,
            )
            if not ok:
                self.last_error = f"pip install falló: {detail}"
                return False
            self._write_marker(packages)

        module = _BACKEND_MODULES.get(self.plan.backend, self.plan.backend)
        ok, detail = self._run(
            [str(self.plan.interpreter), "-c", f"import {module}"],
            timeout=_CHECK_TIMEOUT,
        )
        if not ok:
            self.last_error = f"{module} no se importa en el entorno aislado: {detail}"
            return False
        self._prepared = True
        return True

    # -- compilación ------------------------------------------------------ #
    def _venv_has_pyqt6(self) -> bool:
        return any(
            requirement.split("=")[0].split(">")[0].split("<")[0].strip().lower()
            in {"pyqt6", "pyqt6-qt6"}
            for requirement in self.plan.requirements
        )

    def _nuitka_arguments(self, **kwargs) -> List[str]:
        from lib.blindcubeEngine.nuitka_embedded import EmbeddedNuitka

        accepted = {
            key: kwargs[key]
            for key in (
                "script_path",
                "output_name",
                "output_dir",
                "icon_path",
                "windowed",
                "onefile",
                "add_data",
                "hidden_imports",
                "excludes",
            )
            if key in kwargs
        }
        args = EmbeddedNuitka().build_arguments(**accepted)
        if self._venv_has_pyqt6():
            return args
        # ``build_arguments`` decide el plugin por el entorno del proceso; el
        # venv puede no tener PyQt6 y Nuitka abortaría al pedirle el plugin.
        return [
            arg
            for arg in args
            if not arg.startswith("--enable-plugin=pyqt6")
            and not arg.startswith("--include-qt-plugins")
        ]

    def _pyinstaller_arguments(self, *, build_dir: Path, **kwargs) -> List[str]:
        add_data = kwargs.get("add_data") or []
        hidden_imports = kwargs.get("hidden_imports") or []
        excludes = set(kwargs.get("excludes") or ())
        excludes.update({"matplotlib", "numpy", "scipy", "pandas", "sklearn", "tf", "keras"})
        args = [
            "--onefile" if kwargs.get("onefile", True) else "--onedir",
            "--name",
            str(kwargs["output_name"]),
            "--distpath",
            os.path.abspath(str(kwargs["output_dir"])),
            "--workpath",
            str(build_dir / "work"),
            "--specpath",
            str(build_dir / "spec"),
            "--noconfirm",
            "--windowed" if kwargs.get("windowed", True) else "--console",
        ]
        icon_path = kwargs.get("icon_path")
        if icon_path and os.path.isfile(str(icon_path)):
            args.extend(["--icon", os.path.abspath(str(icon_path))])
        for source, destination in add_data:
            args.extend(["--add-data", f"{os.path.abspath(str(source))}{os.pathsep}{destination}"])
        for module in hidden_imports:
            args.extend(["--hidden-import", str(module)])
        for module in sorted(excludes):
            args.extend(["--exclude-module", str(module)])
        args.append(os.path.abspath(str(kwargs["script_path"])))
        return args

    def _artifact(self, output_dir: Path, output_name: str) -> Optional[Path]:
        for candidate in (
            output_dir / output_name,
            output_dir / f"{output_name}.exe",
            output_dir / f"{output_name}.bin",
        ):
            if candidate.is_file():
                return candidate
        return None

    def compile(self, **kwargs) -> Optional[str]:
        """Compila el guion dentro del entorno aislado y devuelve el binario."""
        if not self._prepared and not self.prepare():
            return None
        script_path = Path(str(kwargs["script_path"])).resolve()
        if not script_path.is_file():
            self.last_error = f"Script no encontrado: {script_path}"
            return None
        output_dir = Path(str(kwargs["output_dir"])).resolve()
        build_dir = Path(str(kwargs.get("build_dir") or self.plan.root / "build"))
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            build_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            self.last_error = f"no se pudo preparar la salida: {exc}"
            return None

        options = dict(kwargs)
        options.pop("build_dir", None)
        options["script_path"] = str(script_path)
        options["output_dir"] = str(output_dir)
        module = _BACKEND_MODULES.get(self.plan.backend, self.plan.backend)
        if self.plan.backend == "pyinstaller":
            args = self._pyinstaller_arguments(build_dir=build_dir, **options)
        else:
            args = self._nuitka_arguments(**options)

        self._log(f"[INFO] Compilando en el entorno aislado ({self.plan.backend})...")
        ok, detail = self._run([str(self.plan.interpreter), "-m", module, *args], timeout=_COMPILE_TIMEOUT)
        if not ok:
            hint = ""
            if self.plan.backend == "nuitka" and "patchelf" in detail:
                hint = (
                    " (Nuitka --onefile en Linux necesita patchelf: "
                    "'sudo apt install patchelf' y repetir el build)"
                )
            self.last_error = f"{self.plan.backend} falló en el entorno aislado: {detail}{hint}"
            return None
        artifact = self._artifact(output_dir, str(kwargs["output_name"]))
        if artifact is None:
            self.last_error = f"{self.plan.backend} no generó el binario esperado en {output_dir}"
            return None
        return str(artifact)

    def purge(self) -> None:
        """Elimina el entorno aislado del proyecto."""
        from lib.file_ops import remove_tree

        remove_tree(self.plan.root)


class IsolatedBackend:
    """Backend envuelto que compila dentro del entorno aislado del proyecto.

    Si el entorno no se puede preparar o la compilación falla, delega en el
    backend embebido para que el build no se quede sin salida.
    """

    def __init__(
        self,
        inner,
        *,
        project_path: Path,
        network_mode: object = NETWORK_UNRESTRICTED,
        log_callback: Optional[Callable[[str], None]] = None,
        sandbox_factory: Optional[Callable[[SandboxPlan], BuildSandbox]] = None,
    ):
        self.inner = inner
        self.name = inner.name
        self.display_name = _DISPLAY_NAMES.get(inner.name, inner.display_name)
        self.pip_packages = tuple(getattr(inner, "pip_packages", ()))
        self.embedded = False
        self._project_path = Path(project_path)
        self._network_mode = resolve_network_mode(network_mode)
        self._log = log_callback or (lambda _message: None)
        self._sandbox_factory = sandbox_factory or (lambda plan: BuildSandbox(plan, log=log_callback))
        self._sandbox: Optional[BuildSandbox] = None
        self._sandbox_failed = False
        self._last_error = ""

    @property
    def last_error(self) -> str:
        return self._last_error or getattr(self.inner, "last_error", "")

    @last_error.setter
    def last_error(self, value: str) -> None:
        self._last_error = value

    def is_available(self) -> bool:
        return self.inner.is_available()

    def version(self) -> str:
        return self.inner.version()

    def _open_sandbox(self) -> Optional[BuildSandbox]:
        if self._sandbox is not None:
            return self._sandbox
        if self._sandbox_failed:
            return None
        plan = plan_sandbox(
            self._project_path,
            backend=self.name,
            network_mode=self._network_mode,
        )
        sandbox = self._sandbox_factory(plan)
        if not sandbox.prepare():
            self._sandbox_failed = True
            self._log(
                f"[WARN] Entorno aislado no disponible ({sandbox.last_error}); "
                "se compila con el backend embebido."
            )
            return None
        self._sandbox = sandbox
        return sandbox

    def compile(self, **kwargs) -> Optional[str]:
        sandbox = self._open_sandbox()
        if sandbox is not None:
            result = sandbox.compile(**kwargs)
            if result:
                return result
            self._log(
                f"[WARN] La compilación aislada falló ({sandbox.last_error}); "
                "se reintenta con el backend embebido."
            )
        return self.inner.compile(**kwargs)

    def cleanup(self) -> None:
        self.inner.cleanup()


def wrap_backend(
    backend,
    project_path: Path,
    *,
    network_mode: object = None,
    log_callback: Optional[Callable[[str], None]] = None,
    sandbox_factory: Optional[Callable[[SandboxPlan], BuildSandbox]] = None,
):
    """Envuelve el backend con el entorno aislado cuando el modo de red lo permite."""
    name = getattr(backend, "name", "")
    if name not in _ISOLATABLE_BACKENDS:
        return backend
    mode = network_mode_from_preferences() if network_mode is None else resolve_network_mode(network_mode)
    if not isolation_enabled(mode):
        if log_callback:
            log_callback(
                "[INFO] Modo de red de uso medido: se compila con el backend embebido "
                f"({name}). Necesita el Python del sistema instalado; sin conexión, "
                "instala el backend con pip y repite el build."
            )
        return backend
    return IsolatedBackend(
        backend,
        project_path=project_path,
        network_mode=mode,
        log_callback=log_callback,
        sandbox_factory=sandbox_factory,
    )


__all__ = [
    "BuildSandbox",
    "DISABLE_ENV",
    "IsolatedBackend",
    "NETWORK_METERED",
    "NETWORK_MODES",
    "NETWORK_UNRESTRICTED",
    "SandboxPlan",
    "isolation_enabled",
    "network_mode_from_preferences",
    "plan_sandbox",
    "project_requirements",
    "resolve_network_mode",
    "wrap_backend",
]
