# -*- coding: utf-8 -*-
"""Motor del IDE de proyectos ``iflapp``.

Reúne, sin GUI, todo lo que el editor visual necesita:

* :func:`scan_project` — inspecciona la carpeta del proyecto (metadatos de
  ``details.xml``, guiones a compilar, presencia de ``.mexf``, icono y
  estructura obligatoria).
* :func:`compile_project` — compila los guiones con los motores base de
  ``packagemaker`` (``lib.compilers``), reutilizando el backend preferido y
  detectando los imports ocultos con ``ast``.
* :func:`trace_script` / :func:`debug_script` — depurador de guiones por línea,
  con puntos de ruptura y captura de variables locales (``sys.settrace``).

El módulo no importa PyQt6: la interfaz vive en ``lib.iflapp_ide_dialog``.
"""
from __future__ import annotations

import ast
import json
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

STRUCTURE_REQUIRED = ("details.xml", "config/settings.json")
SKIP_SCRIPTS = {"updater.py", "removeme.py"}


@dataclass
class IfappProject:
    """Vista de solo lectura de un proyecto ``iflapp`` en disco."""

    root: Path
    metadata: Dict[str, str] = field(default_factory=dict)
    scripts: List[str] = field(default_factory=list)
    entry: Optional[str] = None
    has_mexf: bool = False
    icon: Optional[str] = None
    missing: List[str] = field(default_factory=list)

    @property
    def app(self) -> str:
        return self.metadata.get("app", self.root.name)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "root": str(self.root),
            "metadata": dict(self.metadata),
            "scripts": list(self.scripts),
            "entry": self.entry,
            "has_mexf": self.has_mexf,
            "icon": self.icon,
            "missing": list(self.missing),
        }


def read_details(root: Path) -> Dict[str, str]:
    """Lee ``details.xml`` y normaliza las claves de metadatos."""
    path = Path(root) / "details.xml"
    if not path.is_file():
        return {}
    try:
        node = ET.parse(path).getroot()
    except ET.ParseError:
        return {}
    return {
        "publisher": node.findtext("publisher") or node.findtext("empresa") or "Unknown",
        "app": node.findtext("app") or node.findtext("name") or "Unknown",
        "name": node.findtext("name") or node.findtext("titulo") or "Unknown",
        "version": node.findtext("version") or "v1.0",
        "platform": node.findtext("platform") or node.findtext("plataforma") or "AlphaCube",
        "author": node.findtext("author") or node.findtext("autor") or "Unknown",
    }


def _declared_scripts(root: Path) -> List[str]:
    """Guiones declarados en ``config/settings.json`` (``build.scripts``)."""
    settings = Path(root) / "config" / "settings.json"
    if not settings.is_file():
        return []
    try:
        data = json.loads(settings.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    scripts = data.get("build", {}).get("scripts") if isinstance(data, dict) else None
    if not isinstance(scripts, list):
        return []
    return [str(item) for item in scripts if str(item).strip()]


def find_scripts(root: Path) -> List[str]:
    """Guiones a compilar: los declarados o todos los ``.py`` de la raíz."""
    declared = _declared_scripts(root)
    if declared:
        return declared
    root = Path(root)
    found = []
    for candidate in sorted(root.glob("*.py")):
        if candidate.name in SKIP_SCRIPTS or candidate.name.startswith("_"):
            continue
        found.append(candidate.name)
    return found


def find_icon(root: Path, app: str) -> Optional[str]:
    """Localiza el icono del proyecto (específico de la app antes que genérico)."""
    stems = [f"{app}-icon", "app-icon", "icon"]
    for directory in (Path(root) / "app", Path(root)):
        for stem in stems:
            for ext in (".ico", ".png"):
                candidate = directory / f"{stem}{ext}"
                if candidate.is_file():
                    return str(candidate)
    return None


def scan_project(root: Path | str) -> IfappProject:
    """Inspecciona un proyecto y devuelve su vista normalizada."""
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"No es una carpeta de proyecto: {root}")
    metadata = read_details(root)
    scripts = find_scripts(root)
    entry = scripts[0] if scripts else (f"{metadata.get('app', 'app')}.py")
    missing = [item for item in STRUCTURE_REQUIRED if not (root / item).exists()]
    return IfappProject(
        root=root,
        metadata=metadata,
        scripts=scripts,
        entry=entry if (root / entry).is_file() else None,
        has_mexf=(root / ".mexf").is_dir(),
        icon=find_icon(root, metadata.get("app", "app")),
        missing=missing,
    )


def detect_hidden_imports(script: Path | str) -> List[str]:
    """Extrae los módulos importados de un guion para el backend de compilación."""
    try:
        tree = ast.parse(Path(script).read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return []
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            modules.add(node.module.split(".")[0])
    return sorted(modules)


@dataclass
class CompileOutcome:
    """Resultado de compilar los guiones de un proyecto."""

    backend: str
    outputs: List[str] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)
    log: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return bool(self.outputs) and not self.failures

    def as_dict(self) -> Dict[str, Any]:
        return {
            "backend": self.backend,
            "outputs": list(self.outputs),
            "failures": list(self.failures),
            "log": list(self.log),
        }


def compile_project(
    root: Path | str,
    *,
    backend: Optional[str] = None,
    output_dir: Optional[Path | str] = None,
    log: Optional[Callable[[str], None]] = None,
) -> CompileOutcome:
    """Compila los guiones del proyecto con el backend preferido.

    Reutiliza ``lib.compilers`` tal cual: el IDE no reimplementa la compilación,
    solo elige el guion de entrada y los imports ocultos.
    """
    from lib.compilers import CompilerUnavailableError, resolve_backend

    project = scan_project(root)
    target_dir = Path(output_dir).expanduser().resolve() if output_dir else project.root / "dist"
    target_dir.mkdir(parents=True, exist_ok=True)

    outcome = CompileOutcome(backend=backend or "auto")

    def _log(message: str) -> None:
        outcome.log.append(str(message))
        if log:
            log(message)

    try:
        engine = resolve_backend(backend, log_callback=_log)
    except CompilerUnavailableError as exc:
        outcome.failures.append(str(exc))
        _log(f"[ERROR] {exc}")
        return outcome

    outcome.backend = engine.name
    scripts = project.scripts or ([project.entry] if project.entry else [])
    if not scripts:
        outcome.failures.append("El proyecto no declara ningún guion que compilar.")
        _log("[ERROR] Sin guiones.")
        return outcome

    for script_name in scripts:
        script_path = project.root / script_name
        if not script_path.is_file():
            outcome.failures.append(f"Guion no encontrado: {script_name}")
            _log(f"[ERROR] Guion no encontrado: {script_path}")
            continue
        output_name = script_path.stem
        _log(f"[INFO] Compilando {script_name} con {engine.display_name}...")
        try:
            produced = engine.compile(
                script_path=str(script_path),
                output_name=output_name,
                output_dir=str(target_dir),
                icon_path=project.icon,
                windowed=True,
                onefile=True,
                hidden_imports=detect_hidden_imports(script_path),
                excludes=None,
                cwd=str(project.root),
            )
        except Exception as exc:  # noqa: BLE001 - se informa al usuario
            produced = None
            _log(f"[ERROR] {script_name}: {exc}")
        if produced:
            outcome.outputs.append(str(produced))
            _log(f"[OK] {produced}")
        else:
            message = getattr(engine, "last_error", "") or f"backend {engine.name} no produjo salida"
            outcome.failures.append(f"{script_name}: {message}")
            _log(f"[ERROR] {script_name}: {message}")
    return outcome


@dataclass
class TraceStop:
    """Parada del depurador de guiones: línea, función y variables locales."""

    line: int
    function: str
    locals: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {"line": self.line, "function": self.function, "locals": dict(self.locals)}


class _TraceAbort(Exception):
    """Se lanza al alcanzar el límite de paradas para cortar la ejecución."""


def trace_script(
    path: Path | str,
    *,
    breakpoints: Optional[Sequence[int]] = None,
    max_stops: int = 500,
) -> List[TraceStop]:
    """Ejecuta un guion bajo ``sys.settrace`` y registra sus paradas.

    Con ``breakpoints`` solo se detiene en esas líneas; sin él registra cada
    línea ejecutada (limitado por ``max_stops``).
    """
    source = Path(path)
    code = compile(source.read_text(encoding="utf-8"), str(source), "exec")
    targets = set(breakpoints) if breakpoints else None
    stops: List[TraceStop] = []
    abort = {"hit": False}

    def _local(frame, event, arg):
        if event == "line" and (targets is None or frame.f_lineno in targets):
            stops.append(TraceStop(frame.f_lineno, frame.f_code.co_name, dict(frame.f_locals)))
            if len(stops) >= max_stops:
                abort["hit"] = True
                raise _TraceAbort()
        return _local

    def _global(frame, event, arg):
        return _local if event == "call" else None

    namespace = {"__name__": "__main__", "__file__": str(source)}
    sys.settrace(_global)
    try:
        exec(code, namespace)  # noqa: S102 - ejecución deliberada del guion
    except _TraceAbort:
        pass
    finally:
        sys.settrace(None)
    return stops


@dataclass
class DebugOutcome:
    """Resultado de depurar un guion: paradas, salida y error."""

    stops: List[TraceStop] = field(default_factory=list)
    output: str = ""
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "stops": [stop.as_dict() for stop in self.stops],
            "output": self.output,
            "error": self.error,
        }


def debug_script(
    path: Path | str,
    *,
    breakpoints: Optional[Sequence[int]] = None,
    max_stops: int = 500,
    run: bool = False,
    timeout: Optional[float] = 30,
) -> DebugOutcome:
    """Depura un guion: por línea (traza) o ejecutándolo y capturando la salida."""
    if run:
        from lib.mexf_debugger import default_runner

        code, output = default_runner(sys.executable, [str(path)], timeout=timeout)
        return DebugOutcome(stops=[], output=output, error=None if code == 0 else f"código {code}")
    try:
        stops = trace_script(path, breakpoints=breakpoints, max_stops=max_stops)
    except (OSError, SyntaxError) as exc:
        return DebugOutcome(error=str(exc))
    return DebugOutcome(stops=stops)


def run_script(
    path: Path | str,
    argv: Optional[Sequence[str]] = None,
    *,
    timeout: Optional[float] = 30,
) -> Tuple[int, str]:
    """Ejecuta un guion con el intérprete actual y devuelve ``(código, salida)``."""
    from lib.mexf_debugger import default_runner

    return default_runner(sys.executable, [str(path), *list(argv or [])], timeout=timeout)
