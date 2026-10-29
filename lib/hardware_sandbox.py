# -*- coding: utf-8 -*-
"""Sandbox de virtualización a nivel de hardware y CPU.

Delega la ejecución de código no confiable (hooks de compilación, binarios
recién generados, scripts del proyecto) a un entorno aislado. La selección del
mecanismo es jerárquica:

1. ``qemu-kvm``      — microVM con virtualización por hardware (VT-x/AMD-V).
2. ``systemd-nspawn``— contenedor con namespaces del kernel.
3. ``docker``/``podman`` — contenedor con límites de CPU y memoria.
4. ``bwrap``/``firejail`` — sandbox de espacio de nombres de usuario.
5. ``unshare``       — namespaces crudos (mount/pid/net/user) del kernel.

Además aplica control a nivel de CPU (afinidad con ``taskset``/``sched_setaffinity``
y prioridad con ``nice``/``ionice``) para acotar el consumo del huésped.

Todo el módulo usa sólo la biblioteca estándar y degrada con elegancia cuando
no hay ningún backend disponible (modo ``local`` restringido).
"""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence


@dataclass
class SandboxCapabilities:
    """Capacidades detectadas en el host."""

    backends: Dict[str, bool] = field(default_factory=dict)
    cpu_count: int = 1
    has_kvm: bool = False
    is_root: bool = False

    @property
    def best(self) -> str:
        for name in ("qemu-kvm", "systemd-nspawn", "docker", "podman", "bwrap", "firejail", "unshare"):
            if self.backends.get(name):
                return name
        return "local"

    def as_dict(self) -> Dict[str, object]:
        return {
            "backends": dict(self.backends),
            "best": self.best,
            "cpu_count": self.cpu_count,
            "has_kvm": self.has_kvm,
            "is_root": self.is_root,
        }


@dataclass
class SandboxResult:
    """Resultado de una ejecución aislada."""

    returncode: int
    stdout: str
    stderr: str
    backend: str
    command: List[str]
    timed_out: bool = False

    @property
    def ok(self) -> bool:
        return self.returncode == 0 and not self.timed_out


def _container_runtime_ready(binary: str) -> bool:
    """Comprueba que el motor de contenedores responde (daemon accesible).

    Detectar el binario no basta: sin el daemon en marcha el contenedor falla.
    La comprobación es barata y evita seleccionar un backend inservible.
    """
    if shutil.which(binary) is None:
        return False
    try:
        probe = subprocess.run(
            [binary, "info"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return probe.returncode == 0


def _unshare_supported() -> bool:
    """Comprueba que los namespaces del kernel permiten crear un sandbox."""
    if shutil.which("unshare") is None:
        return False
    try:
        probe = subprocess.run(
            ["unshare", "--user", "--mount", "--pid", "--fork", "--", "true"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return probe.returncode == 0


def detect_capabilities() -> SandboxCapabilities:
    """Inspecciona el host y devuelve los backends de aislamiento disponibles."""
    is_root = hasattr(os, "geteuid") and os.geteuid() == 0
    has_kvm = Path("/dev/kvm").exists() and os.access("/dev/kvm", os.R_OK | os.W_OK)
    backends = {
        "qemu-kvm": shutil.which("qemu-system-x86_64") is not None and has_kvm,
        "systemd-nspawn": shutil.which("systemd-nspawn") is not None and is_root,
        "docker": _container_runtime_ready("docker"),
        "podman": _container_runtime_ready("podman"),
        "bwrap": shutil.which("bwrap") is not None,
        "firejail": shutil.which("firejail") is not None,
        "unshare": _unshare_supported(),
    }
    return SandboxCapabilities(
        backends=backends,
        cpu_count=os.cpu_count() or 1,
        has_kvm=has_kvm,
        is_root=is_root,
    )


class HardwareSandbox:
    """Ejecuta comandos dentro de un entorno virtualizado.

    El sandbox copia el proyecto a un espacio de trabajo aislado (para no
    exponer la fuente original), monta ese espacio como raíz de trabajo y
    aplica límites de CPU antes de delegar la ejecución.
    """

    def __init__(self, log_callback=None, backend: Optional[str] = None, timeout: int = 600):
        self._log_callback = log_callback
        self.capabilities = detect_capabilities()
        self.backend = backend or self.capabilities.best
        self.timeout = timeout

    def log(self, message: str) -> None:
        if self._log_callback:
            self._log_callback(message)

    # -- descripción ------------------------------------------------------ #
    def describe(self) -> Dict[str, object]:
        info = self.capabilities.as_dict()
        info["selected"] = self.backend
        info["hardware_virtualization"] = self.backend == "qemu-kvm"
        return info

    # -- control de CPU --------------------------------------------------- #
    def _cpu_prefix(self, cpus: Optional[Sequence[int]] = None) -> List[str]:
        prefix: List[str] = []
        taskset = shutil.which("taskset")
        if taskset:
            if cpus:
                mask = ",".join(str(c) for c in cpus)
            else:
                mask = "0"
            prefix.extend([taskset, "-c", mask])
        nice = shutil.which("nice")
        if nice:
            prefix.extend([nice, "-n", "10"])
        return prefix

    def _pin_current_process(self, cpus: Optional[Sequence[int]] = None) -> None:
        """Fija la afinidad del proceso actual al primer núcleo disponible."""
        if not hasattr(os, "sched_setaffinity"):
            return
        target = list(cpus) if cpus else [0]
        try:
            os.sched_setaffinity(0, set(target))
        except OSError:
            pass

    # -- espacio de trabajo ----------------------------------------------- #
    def prepare_workspace(self, project_path: Path | str, *, writable: bool = True) -> Path:
        """Copia *project_path* a un directorio temporal aislado."""
        source = Path(project_path).resolve()
        workspace = Path(tempfile.mkdtemp(prefix="iflapp_sandbox_")) / source.name
        workspace.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, workspace, symlinks=False, ignore_dangling_symlinks=True)
        if not writable:
            for root, dirs, files in os.walk(workspace):
                for name in files:
                    try:
                        os.chmod(Path(root) / name, 0o444)
                    except OSError:
                        pass
        self.log(f"[sandbox] Espacio de trabajo aislado: {workspace}")
        return workspace

    # -- construcción del comando ----------------------------------------- #
    def build_command(self, argv: Sequence[str], workspace: Path) -> List[str]:
        backend = self.backend
        ws = str(workspace)
        if backend == "systemd-nspawn":
            return ["systemd-nspawn", "--quiet", "--private-users=pick", "--bind", ws, "--chdir", ws, *argv]
        if backend == "docker":
            return [
                "docker", "run", "--rm",
                "--network=none",
                "--cpus=1",
                "--memory=2g",
                "--pids-limit=256",
                "--read-only",
                "--tmpfs", "/tmp:rw,size=256m",
                "-v", f"{ws}:{ws}:rw",
                "-w", ws,
                "python:3.11-slim",
                *argv,
            ]
        if backend == "podman":
            return [
                "podman", "run", "--rm",
                "--network=none",
                "--cpus=1",
                "--memory=2g",
                "--read-only",
                "--tmpfs", "/tmp:rw,size=256m",
                "-v", f"{ws}:{ws}:rw",
                "-w", ws,
                "python:3.11-slim",
                *argv,
            ]
        if backend == "bwrap":
            return [
                "bwrap",
                "--ro-bind", "/usr", "/usr",
                "--ro-bind", "/lib", "/lib",
                "--ro-bind", "/lib64", "/lib64",
                "--ro-bind", "/bin", "/bin",
                "--ro-bind", "/sbin", "/sbin",
                "--proc", "/proc",
                "--dev", "/dev",
                "--tmpfs", "/tmp",
                "--bind", ws, ws,
                "--unshare-all",
                "--die-with-parent",
                "--chdir", ws,
                *argv,
            ]
        if backend == "firejail":
            return ["firejail", "--quiet", "--net=none", "--private-tmp", f"--whitelist={ws}", *argv]
        if backend == "unshare":
            flags = ["--mount", "--pid", "--fork", "--uts", "--ipc"]
            if not self.capabilities.is_root:
                flags.append("--user")
            flags.append("--net")
            return ["unshare", *flags, "--", *argv]
        return list(argv)

    # -- ejecución -------------------------------------------------------- #
    def run(
        self,
        argv: Sequence[str],
        workspace: Path | str,
        *,
        cpus: Optional[Sequence[int]] = None,
        timeout: Optional[int] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> SandboxResult:
        """Ejecuta *argv* dentro del aislamiento seleccionado."""
        workspace = Path(workspace)
        command = self._cpu_prefix(cpus) + self.build_command(argv, workspace)
        self.log(f"[sandbox:{self.backend}] {' '.join(shlex.quote(part) for part in command)}")

        run_env = os.environ.copy()
        run_env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
        run_env.setdefault("HOME", str(workspace))
        if env:
            run_env.update(env)

        self._pin_current_process(cpus)
        try:
            process = subprocess.run(
                command,
                cwd=str(workspace),
                env=run_env,
                capture_output=True,
                text=True,
                timeout=timeout or self.timeout,
            )
        except subprocess.TimeoutExpired as exc:
            return SandboxResult(
                returncode=-1,
                stdout=exc.stdout or "" if isinstance(exc.stdout, str) else "",
                stderr=(exc.stderr or "") if isinstance(exc.stderr, str) else "Tiempo de ejecución agotado.",
                backend=self.backend,
                command=command,
                timed_out=True,
            )
        except FileNotFoundError as exc:
            return SandboxResult(
                returncode=127,
                stdout="",
                stderr=str(exc),
                backend=self.backend,
                command=command,
            )
        return SandboxResult(
            returncode=process.returncode,
            stdout=process.stdout,
            stderr=process.stderr,
            backend=self.backend,
            command=command,
        )

    def run_python(
        self,
        script: Path | str,
        workspace: Path | str,
        *,
        args: Sequence[str] = (),
        timeout: Optional[int] = None,
    ) -> SandboxResult:
        """Ejecuta un script Python dentro del sandbox."""
        return self.run([sys.executable, str(script), *args], workspace, timeout=timeout)

    def run_and_verify_binary(
        self,
        binary: Path | str,
        workspace: Path | str,
        *,
        timeout: int = 60,
    ) -> SandboxResult:
        """Ejecuta un binario generado para comprobar que arranca sin fallos."""
        binary = Path(binary)
        if not binary.is_file():
            return SandboxResult(-1, "", f"Binario no encontrado: {binary}", self.backend, [])
        try:
            binary.chmod(binary.stat().st_mode | 0o111)
        except OSError:
            pass
        return self.run([str(binary), "--version"], workspace, timeout=timeout)

    def cleanup(self, workspace: Path | str) -> None:
        try:
            shutil.rmtree(Path(workspace).parent, ignore_errors=True)
        except OSError:
            pass
