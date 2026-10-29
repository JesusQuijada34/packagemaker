# -*- coding: utf-8 -*-
"""Métodos de blindaje para paquetes y binarios de PackageMaker.

Cada método es independiente y se puede aplicar en cualquier combinación. El
objetivo es endurecer el artefacto sin depender de una sola técnica:

* ``strip``        — elimina símbolos de depuración del binario.
* ``upx``          — comprime el ejecutable cuando UPX está disponible.
* ``checksum``     — incrusta un manifiesto de digests junto al artefacto.
* ``anti-debug``   — inyecta un guardián de depuración en el arranque.
* ``obfuscate``    — ofusca cadenas sensibles del código fuente Python.
* ``resource``     — adjunta metadatos/icono a binarios PE mediante ``objcopy``.

El módulo usa sólo la biblioteca estándar y degrada con elegancia cuando la
herramienta externa no está instalada: cada método devuelve un informe con su
estado en lugar de fallar.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence

HARDENING_VERSION = 1

_STRING_LITERAL = re.compile(r'(?<![\w.])("([^"\\\n]|\\.)*"|\'([^\'\\\n]|\\.)*\')')

# Guardián de depuración mínimo, inyectable en el arranque del paquete.
ANTI_DEBUG_GUARD = '''\
# --- Influent Package Maker: guardián de depuración ---
def _iflapp_guard():
    import sys
    if sys.gettrace() is not None:
        raise SystemExit("Ejecución bajo depurador no permitida.")
    try:
        import ctypes
        if sys.platform.startswith("win"):
            if ctypes.windll.kernel32.IsDebuggerPresent():
                raise SystemExit("Depurador detectado.")
        elif sys.platform.startswith("linux"):
            with open("/proc/self/status", "r", encoding="utf-8", errors="ignore") as handle:
                for line in handle:
                    if line.startswith("TracerPid:") and line.split(":")[1].strip() != "0":
                        raise SystemExit("Depurador detectado.")
    except SystemExit:
        raise
    except Exception:
        pass


_iflapp_guard()
'''


@dataclass
class HardeningReport:
    """Resultado de aplicar un método de blindaje."""

    method: str
    applied: bool
    detail: str = ""
    artifacts: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, object]:
        return {
            "method": self.method,
            "applied": self.applied,
            "detail": self.detail,
            "artifacts": list(self.artifacts),
        }


def method_names() -> List[str]:
    """Nombres canónicos de los métodos de blindaje soportados."""
    return ["strip", "upx", "checksum", "anti-debug", "obfuscate", "resource"]


def _run(argv: Sequence[str], *, timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(argv, capture_output=True, text=True, timeout=timeout)


def strip_binary(binary: Path | str) -> HardeningReport:
    """Elimina símbolos de depuración con ``strip`` (o ``llvm-strip``)."""
    binary = Path(binary)
    tool = shutil.which("strip") or shutil.which("llvm-strip")
    if not tool:
        return HardeningReport("strip", False, "herramienta 'strip' no disponible")
    if not binary.is_file():
        return HardeningReport("strip", False, f"no existe el binario: {binary}")
    before = binary.stat().st_size
    try:
        proc = _run([tool, "--strip-all", str(binary)])
    except (OSError, subprocess.SubprocessError) as exc:
        return HardeningReport("strip", False, str(exc))
    if proc.returncode != 0:
        return HardeningReport("strip", False, (proc.stderr or proc.stdout).strip()[:400])
    after = binary.stat().st_size
    return HardeningReport(
        "strip",
        True,
        f"tamaño {before} -> {after} bytes",
        [str(binary)],
    )


def upx_compress(binary: Path | str) -> HardeningReport:
    """Comprime el ejecutable con UPX si está instalado."""
    binary = Path(binary)
    tool = shutil.which("upx") or shutil.which("upx-ucl")
    if not tool:
        return HardeningReport("upx", False, "UPX no disponible")
    if not binary.is_file():
        return HardeningReport("upx", False, f"no existe el binario: {binary}")
    before = binary.stat().st_size
    try:
        proc = _run([tool, "--best", "--lzma", str(binary)])
    except (OSError, subprocess.SubprocessError) as exc:
        return HardeningReport("upx", False, str(exc))
    if proc.returncode != 0:
        return HardeningReport("upx", False, (proc.stderr or proc.stdout).strip()[:400])
    after = binary.stat().st_size
    return HardeningReport("upx", True, f"tamaño {before} -> {after} bytes", [str(binary)])


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_checksum_manifest(
    target: Path | str,
    output: Optional[Path | str] = None,
) -> HardeningReport:
    """Escribe un manifiesto de integridad junto al artefacto.

    Si *target* es un directorio se recorren todos sus archivos; si es un
    archivo se registra sólo él. El manifiesto incluye un digest global para
    verificación en un solo paso.
    """
    target = Path(target)
    if not target.exists():
        return HardeningReport("checksum", False, f"no existe: {target}")

    entries: List[Dict[str, str]] = []
    if target.is_dir():
        for path in sorted(target.rglob("*")):
            if path.is_file():
                entries.append(
                    {"path": path.relative_to(target).as_posix(), "sha256": _sha256_file(path)}
                )
    else:
        entries.append({"path": target.name, "sha256": _sha256_file(target)})

    global_digest = hashlib.sha256(
        json.dumps(entries, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    manifest = {
        "hardening_version": HARDENING_VERSION,
        "target": target.name,
        "algorithm": "sha256",
        "global": global_digest,
        "files": entries,
    }
    output = Path(output) if output else target.with_suffix(target.suffix + ".manifest.json")
    output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return HardeningReport(
        "checksum",
        True,
        f"{len(entries)} archivos, digest global {global_digest[:16]}…",
        [str(output)],
    )


def inject_anti_debug(script: Path | str) -> HardeningReport:
    """Inyecta el guardián de depuración al inicio de un script Python."""
    script = Path(script)
    if not script.is_file():
        return HardeningReport("anti-debug", False, f"no existe el script: {script}")
    text = script.read_text(encoding="utf-8")
    if "_iflapp_guard()" in text:
        return HardeningReport("anti-debug", True, "guardián ya presente", [str(script)])
    script.write_text(ANTI_DEBUG_GUARD + "\n" + text, encoding="utf-8")
    return HardeningReport("anti-debug", True, "guardián inyectado", [str(script)])


def obfuscate_strings(source: Path | str, *, output: Optional[Path | str] = None) -> HardeningReport:
    """Ofusca literales de cadena sustituyéndolos por base64 decodificado.

    Es una transformación reversible y conserva la semántica: cada literal se
    reemplaza por ``__import__('base64').b64decode(...).decode()``. No pretende
    ser criptografía; eleva el coste de la inspección casual del código.
    """
    source = Path(source)
    if not source.is_file():
        return HardeningReport("obfuscate", False, f"no existe el fuente: {source}")
    text = source.read_text(encoding="utf-8")
    if "b64decode(" in text:
        return HardeningReport("obfuscate", False, "el fuente ya está ofuscado", [str(source)])

    counter = {"n": 0}

    def _replace(match: re.Match) -> str:
        literal = match.group(0)
        try:
            value = eval(literal)  # noqa: S307 - literal validado por el patrón
        except Exception:
            return literal
        if not isinstance(value, str) or len(value) < 8:
            return literal
        counter["n"] += 1
        encoded = base64.b64encode(value.encode("utf-8")).decode("ascii")
        return f"__import__('base64').b64decode('{encoded}').decode('utf-8')"

    new_text = _STRING_LITERAL.sub(_replace, text)
    output = Path(output) if output else source
    output.write_text(new_text, encoding="utf-8")
    return HardeningReport(
        "obfuscate",
        counter["n"] > 0,
        f"{counter['n']} literales ofuscados",
        [str(output)],
    )


def attach_resource(binary: Path | str, icon: Optional[Path | str] = None) -> HardeningReport:
    """Adjunta el icono a un binario PE con ``objcopy`` cuando es posible.

    ``objcopy`` sólo puede inyectar secciones de recursos en binarios PE
    preparados; cuando la operación no es viable el método se marca como no
    aplicado y el flujo continúa.
    """
    binary = Path(binary)
    tool = shutil.which("objcopy") or shutil.which("llvm-objcopy")
    if not tool:
        return HardeningReport("resource", False, "objcopy no disponible")
    if not binary.is_file():
        return HardeningReport("resource", False, f"no existe el binario: {binary}")
    if icon is None:
        return HardeningReport("resource", False, "no se indicó icono")
    icon = Path(icon)
    if not icon.is_file():
        return HardeningReport("resource", False, f"no existe el icono: {icon}")
    try:
        proc = _run([tool, "--add-section", f".iflapp.ico={icon}", str(binary)])
    except (OSError, subprocess.SubprocessError) as exc:
        return HardeningReport("resource", False, str(exc))
    if proc.returncode != 0:
        return HardeningReport("resource", False, (proc.stderr or proc.stdout).strip()[:400])
    return HardeningReport("resource", True, "sección .iflapp.ico añadida", [str(binary)])


def apply_all(
    *,
    binary: Optional[Path | str] = None,
    script: Optional[Path | str] = None,
    package_dir: Optional[Path | str] = None,
    icon: Optional[Path | str] = None,
    methods: Optional[Sequence[str]] = None,
    log_callback=None,
) -> List[HardeningReport]:
    """Aplica los métodos de blindaje solicitados y devuelve sus informes.

    Los métodos que no aplican al artefacto disponible se registran como no
    aplicados en lugar de interrumpir el flujo.
    """
    selected = [m for m in (methods or method_names())]
    reports: List[HardeningReport] = []

    def _log(message: str) -> None:
        if log_callback:
            log_callback(message)

    for method in selected:
        try:
            if method == "strip" and binary:
                report = strip_binary(binary)
            elif method == "upx" and binary:
                report = upx_compress(binary)
            elif method == "checksum" and package_dir:
                report = write_checksum_manifest(package_dir)
            elif method == "anti-debug" and script:
                report = inject_anti_debug(script)
            elif method == "obfuscate" and script:
                report = obfuscate_strings(script)
            elif method == "resource" and binary:
                report = attach_resource(binary, icon)
            else:
                report = HardeningReport(method, False, "artefacto no aplicable")
        except Exception as exc:  # el blindaje nunca debe abortar la compilación
            report = HardeningReport(method, False, f"error: {exc}")
        reports.append(report)
        status = "OK" if report.applied else "OMITIDO"
        _log(f"[harden:{method}] {status} — {report.detail}")
    return reports


def available_methods() -> Dict[str, bool]:
    """Estado de disponibilidad de las herramientas de cada método."""
    return {
        "strip": bool(shutil.which("strip") or shutil.which("llvm-strip")),
        "upx": bool(shutil.which("upx") or shutil.which("upx-ucl")),
        "checksum": True,
        "anti-debug": True,
        "obfuscate": True,
        "resource": bool(shutil.which("objcopy") or shutil.which("llvm-objcopy")),
    }
