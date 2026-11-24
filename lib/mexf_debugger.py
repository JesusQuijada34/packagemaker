# -*- coding: utf-8 -*-
"""Motor del *debugger* para documentos ``.mexf``.

Interpreta el plan declarativo de un ``.mexf`` (lista ``commands``) paso a paso,
con puntos de ruptura, ejecución real de cada comando argv (sin *shell*) e
inspección de variables (metadatos, entorno y resultado del último comando).

El motor es puro respecto a la GUI: se puede conducir desde pruebas o desde el
editor. La ejecución se delega en un ``runner`` inyectable; el predeterminado
usa :func:`subprocess.run` con ``shell=False`` y captura la salida, de modo que
el editor no interpola comandos de shell.
"""
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

Runner = Callable[..., Tuple[int, str]]


@dataclass
class DebugFrame:
    """Resultado de ejecutar (o simular) un comando del plan."""

    command_id: str
    executable: str
    args: List[str]
    status: str = "pending"  # pending | ok | failed | skipped
    returncode: Optional[int] = None
    output: str = ""
    index: int = 0

    @property
    def failed(self) -> bool:
        return self.status == "failed"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "id": self.command_id,
            "executable": self.executable,
            "args": list(self.args),
            "status": self.status,
            "returncode": self.returncode,
            "output": self.output,
        }


def default_runner(
    executable: str,
    args: List[str],
    *,
    env: Optional[Dict[str, str]] = None,
    cwd: Optional[str] = None,
    timeout: Optional[float] = None,
) -> Tuple[int, str]:
    """Ejecuta ``argv`` sin *shell* y devuelve ``(código, salida combinada)``."""
    try:
        completed = subprocess.run(
            [executable, *args],
            capture_output=True,
            text=True,
            env=env,
            cwd=cwd,
            timeout=timeout,
            shell=False,
            check=False,
        )
    except FileNotFoundError as exc:
        return 127, str(exc)
    except subprocess.TimeoutExpired:
        return 124, "tiempo de ejecución agotado"
    except (OSError, ValueError) as exc:
        # Permiso de ejecución ausente, formato no ejecutable, ``cwd``
        # inaccesible o un byte NUL en el argv/entorno: el comando no llegó a
        # lanzarse. ``subprocess`` señala el último caso con ``ValueError``.
        return 126, str(exc)
    output = (completed.stdout or "") + (completed.stderr or "")
    return completed.returncode, output


def load_commands(document: Any) -> List[Dict[str, Any]]:
    """Extrae la lista de comandos de un documento ``.mexf`` o de su ``data``."""
    data = getattr(document, "data", document)
    commands = data.get("commands") if isinstance(data, dict) else []
    if not isinstance(commands, list):
        commands = []
    normalized: List[Dict[str, Any]] = []
    for index, item in enumerate(commands):
        if not isinstance(item, dict) or not item.get("id"):
            continue
        args = item.get("args")
        env = item.get("env")
        cwd = item.get("cwd")
        normalized.append(
            {
                "id": str(item["id"]),
                "executable": str(item.get("executable") or ""),
                "args": [str(arg) for arg in args] if isinstance(args, list) else [],
                "env": {str(k): str(v) for k, v in env.items()} if isinstance(env, dict) else {},
                "cwd": str(cwd) if cwd else None,
                "on_error": str(item.get("on_error") or "stop"),
                "index": index,
            }
        )
    return normalized


class MexfDebugger:
    """Conduce el plan ``.mexf`` con puntos de ruptura y ejecución por pasos."""

    def __init__(
        self,
        document: Any,
        *,
        runner: Optional[Runner] = None,
        environment: Optional[Dict[str, str]] = None,
        dry_run: bool = False,
        timeout: Optional[float] = None,
    ):
        data = getattr(document, "data", document) if not isinstance(document, dict) else document
        metadata = data.get("metadata")
        environments = data.get("environments")
        self.metadata: Dict[str, Any] = dict(metadata) if isinstance(metadata, dict) else {}
        self.commands = load_commands(document)
        self.runner = runner or default_runner
        self.environment = (
            {str(k): str(v) for k, v in environments.items()}
            if isinstance(environments, dict)
            else {}
        )
        self.environment.update(environment or {})
        self.dry_run = dry_run
        self.timeout = timeout
        self.breakpoints: List[str] = []
        self.frames: List[DebugFrame] = []
        self.pc = 0
        self.state = "idle"  # idle | paused | finished
        self.error: Optional[str] = None
        self._paused_pc: Optional[int] = None

    # ── Puntos de ruptura ────────────────────────────────────────────────
    def set_breakpoint(self, command_id: str, enabled: bool = True) -> None:
        if enabled and command_id not in self.breakpoints:
            self.breakpoints.append(command_id)
        elif not enabled and command_id in self.breakpoints:
            self.breakpoints.remove(command_id)

    def toggle_breakpoint(self, command_id: str) -> bool:
        if command_id in self.breakpoints:
            self.breakpoints.remove(command_id)
            return False
        self.breakpoints.append(command_id)
        return True

    def clear_breakpoints(self) -> None:
        self.breakpoints.clear()

    # ── Control de ejecución ─────────────────────────────────────────────
    def start(self) -> "MexfDebugger":
        self.frames = []
        self.pc = 0
        self.error = None
        self._paused_pc = None
        self.state = "paused" if self.commands else "finished"
        return self

    def step(self) -> Optional[DebugFrame]:
        """Ejecuta exactamente un comando, ignorando los puntos de ruptura."""
        if self.pc >= len(self.commands):
            self.state = "finished"
            return None
        frame = self._execute(self.commands[self.pc])
        self.frames.append(frame)
        self.pc += 1
        self._paused_pc = None
        if frame.failed and self._stops_on_error(frame):
            self.state = "finished"
            self.error = f"el comando {frame.command_id} falló con código {frame.returncode}"
        elif self.pc >= len(self.commands):
            self.state = "finished"
        else:
            self.state = "paused"
        return frame

    def resume(self) -> Optional[DebugFrame]:
        """Ejecuta hasta el siguiente punto de ruptura o el final."""
        if self.state == "idle":
            self.start()
        last: Optional[DebugFrame] = None
        while self.pc < len(self.commands):
            command = self.commands[self.pc]
            if command["id"] in self.breakpoints and self.pc != self._paused_pc:
                self._paused_pc = self.pc
                self.state = "paused"
                return last
            frame = self._execute(command)
            self.frames.append(frame)
            self.pc += 1
            self._paused_pc = None
            last = frame
            if frame.failed and self._stops_on_error(frame):
                self.state = "finished"
                self.error = f"el comando {frame.command_id} falló con código {frame.returncode}"
                return frame
        self.state = "finished"
        return last

    def run(self) -> List[DebugFrame]:
        """Ejecuta el plan completo desde el principio."""
        self.start()
        self.resume()
        return self.frames

    # ── Inspección ───────────────────────────────────────────────────────
    def current_command(self) -> Optional[Dict[str, Any]]:
        if self.pc < len(self.commands):
            return self.commands[self.pc]
        return None

    def variables(self) -> Dict[str, Any]:
        last = self.frames[-1] if self.frames else None
        return {
            "metadata": dict(self.metadata),
            "environments": dict(self.environment),
            "pc": self.pc,
            "total": len(self.commands),
            "state": self.state,
            "last_returncode": last.returncode if last else None,
            "error": self.error,
        }

    # ── Interno ──────────────────────────────────────────────────────────
    def _stops_on_error(self, frame: DebugFrame) -> bool:
        command = next((c for c in self.commands if c["id"] == frame.command_id), None)
        return bool(command) and command["on_error"] != "continue"

    def _execute(self, command: Dict[str, Any]) -> DebugFrame:
        frame = DebugFrame(
            command_id=command["id"],
            executable=command["executable"],
            args=list(command["args"]),
            index=command["index"],
        )
        if self.dry_run:
            frame.status = "skipped"
            frame.output = "(simulado)"
            return frame
        if not command["executable"]:
            frame.status = "failed"
            frame.returncode = 126
            frame.output = "comando sin ejecutable declarado"
            return frame
        env = dict(os.environ)
        env.update(self.environment)
        env.update(command["env"])
        cwd = command["cwd"] or None
        returncode, output = self.runner(
            command["executable"],
            command["args"],
            env=env,
            cwd=cwd,
            timeout=self.timeout,
        )
        frame.returncode = returncode
        frame.output = output
        frame.status = "ok" if returncode == 0 else "failed"
        return frame


def debug_document(
    document: Any,
    *,
    runner: Optional[Runner] = None,
    dry_run: bool = False,
    environment: Optional[Dict[str, str]] = None,
) -> List[DebugFrame]:
    """Atajo: ejecuta el plan completo y devuelve sus cuadros."""
    return MexfDebugger(
        document, runner=runner, dry_run=dry_run, environment=environment
    ).run()


def parse_and_debug(
    path: Path | str,
    *,
    runner: Optional[Runner] = None,
    dry_run: bool = False,
) -> List[DebugFrame]:
    """Carga un ``.mexf`` desde disco y depura su plan."""
    from lib.mexf_parser import parse_mexf

    source = Path(path)
    project_root = source.parent.parent if source.parent.name == ".mexf" else source.parent
    return debug_document(parse_mexf(source, project_root=project_root), runner=runner, dry_run=dry_run)
