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
import hmac
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
    return [
        "strip",
        "upx",
        "checksum",
        "anti-debug",
        "obfuscate",
        "resource",
        "sign",
        "integrity",
        "compile-only",
        "rename-symbols",
    ]


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
    """Adjunta el icono como sección ``.iflapp.ico`` con ``objcopy``.

    Es una incrustación de sección cruda (válida en ELF y aceptada por
    ``objcopy`` en PE). No sustituye el recurso de icono nativo de Windows: para
    eso el icono debe pasarse al compilador (Nuitka ``--windows-icon-from-ico``).
    Cuando la operación no es viable el método se marca como no aplicado y el
    flujo continúa.
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


def sign_binary(
    binary: Path | str,
    *,
    signing_key: bytes = b"",
    output: Optional[Path | str] = None,
) -> HardeningReport:
    """Adjunta una firma HMAC-SHA256 al binario (sidecar ``.sig``).

    Es un *sello de integridad*, no una firma Authenticode: sirve para que el
    dropper y el lector puedan verificar que el artefacto no se alteró. Cuando
    hay ``osslsigncode`` disponible se intenta además la firma Authenticode.
    """
    binary = Path(binary)
    if not binary.is_file():
        return HardeningReport("sign", False, f"no existe el binario: {binary}")
    digest = hashlib.sha256(binary.read_bytes()).hexdigest()
    key = signing_key or b"influent-hardening-signature"
    mac = hmac.new(key, binary.read_bytes(), hashlib.sha256).hexdigest()
    sig_path = Path(output) if output else binary.with_suffix(binary.suffix + ".sig")
    payload = {
        "file": binary.name,
        "sha256": digest,
        "hmac_sha256": mac,
        "alg": "hmac-sha256",
        "hardening_version": HARDENING_VERSION,
    }
    sig_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    artifacts = [str(sig_path)]
    detail = "sello HMAC-SHA256 generado"
    tool = shutil.which("osslsigncode")
    if tool and binary.suffix.lower() == ".exe":
        signed = binary.with_suffix(".signed.exe")
        proc = _run([tool, "sign", "-in", str(binary), "-out", str(signed)])
        if proc.returncode == 0:
            artifacts.append(str(signed))
            detail += "; Authenticode aplicado"
    return HardeningReport("sign", True, detail, artifacts)


def embed_integrity_manifest(package_dir: Path | str) -> HardeningReport:
    """Escribe un manifiesto de integridad recursivo (``.iflapp.integrity``).

    A diferencia de ``checksum``, incluye tamaños y una raíz Merkle simple que
    permite verificar el conjunto completo con un único valor.
    """
    package_dir = Path(package_dir)
    if not package_dir.is_dir():
        return HardeningReport("integrity", False, f"no existe el directorio: {package_dir}")
    entries: List[Dict[str, object]] = []
    leaves: List[str] = []
    for path in sorted(package_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(package_dir).as_posix()
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        entries.append({"path": rel, "size": len(data), "sha256": digest})
        leaves.append(digest)
    root = hashlib.sha256("".join(sorted(leaves)).encode("ascii")).hexdigest()
    manifest = {
        "hardening_version": HARDENING_VERSION,
        "root_sha256": root,
        "count": len(entries),
        "files": entries,
    }
    out = package_dir / ".iflapp.integrity"
    out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return HardeningReport("integrity", True, f"raíz Merkle {root[:16]}…", [str(out)])


def compile_to_bytecode(script: Path | str, *, optimize: int = 2) -> HardeningReport:
    """Compila un script a ``.pyc`` optimizado (sin fuentes legibles)."""
    script = Path(script)
    if not script.is_file():
        return HardeningReport("compile-only", False, f"no existe el script: {script}")
    import py_compile

    target = script.with_suffix(".pyc")
    try:
        py_compile.compile(str(script), cfile=str(target), doraise=True, optimize=optimize)
    except py_compile.PyCompileError as exc:
        return HardeningReport("compile-only", False, str(exc))
    return HardeningReport("compile-only", True, f"bytecode optimizado (O{optimize})", [str(target)])


def rename_symbols(binary: Path | str) -> HardeningReport:
    """Elimina símbolos locales y de depuración (``strip --strip-all``).

    Complementa ``strip`` (que quita la tabla de símbolos) borrando además los
    nombres locales, lo que dificulta la ingeniería inversa del binario.
    """
    binary = Path(binary)
    tool = shutil.which("strip") or shutil.which("llvm-strip")
    if not tool:
        return HardeningReport("rename-symbols", False, "strip no disponible")
    if not binary.is_file():
        return HardeningReport("rename-symbols", False, f"no existe el binario: {binary}")
    proc = _run([tool, "--strip-all", "--strip-unneeded", str(binary)])
    if proc.returncode != 0:
        return HardeningReport("rename-symbols", False, (proc.stderr or proc.stdout).strip()[:400])
    return HardeningReport("rename-symbols", True, "símbolos locales eliminados", [str(binary)])


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
            elif method == "sign" and binary:
                report = sign_binary(binary)
            elif method == "integrity" and package_dir:
                report = embed_integrity_manifest(package_dir)
            elif method == "compile-only" and script:
                report = compile_to_bytecode(script)
            elif method == "rename-symbols" and binary:
                report = rename_symbols(binary)
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
        "sign": True,
        "integrity": True,
        "compile-only": True,
        "rename-symbols": bool(shutil.which("strip") or shutil.which("llvm-strip")),
    }
