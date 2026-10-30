# -*- coding: utf-8 -*-
"""Dropper autoextraíble y capa de compatibilidad para paquetes ``.iflapp``.

Un *dropper* es un lanzador legítimo autoextraíble: un pequeño programa que
lleva un ``.iflapp`` adjunto y, al ejecutarse, lo extrae a un directorio temporal
y arranca la aplicación. Se usa para distribuir un paquete como un único
ejecutable sin depender de que el usuario tenga PackageMaker instalado.

El stub generado es autónomo (sólo biblioteca estándar) e incluye:

* lectura de la cabecera ``.iflapp`` v2 con recuperación por cola redundante;
* compatibilidad con el contenedor ZIP histórico;
* extracción segura (sin traversal ni enlaces);
* arranque del binario o del script principal del paquete.
"""

from __future__ import annotations

import base64
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional

from lib.iflapp_format import (
    IflappError,
    read_iflapp_header,
    sniff_format,
    verify_iflapp,
)

DROPPER_MARKER = b"#==IFLAPP-DROPPER-PAYLOAD==\n"
DROPPER_END = b"#==IFLAPP-DROPPER-END==\n"
STUB_NAME = "iflapp_dropper_stub.py"


def _stub_source() -> str:
    """Código del stub autoextraíble (autónomo, sólo biblioteca estándar).

    El payload se adjunta codificado en base64 sobre líneas comentadas, de modo
    que el dropper completo sigue siendo un archivo Python válido y ejecutable
    con ``python dropper.run`` sin perder el formato binario original.
    """
    return '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stub autoextraíble generado por Influent Package Maker."""
import base64, hashlib, hmac, io, json, lzma, os, shutil, stat, struct, subprocess, sys, tarfile, tempfile, zipfile

MARKER = b"#==IFLAPP-DROPPER-PAYLOAD==\\n"
END = b"#==IFLAPP-DROPPER-END==\\n"
MAGIC = b"IFLAPP2\\x00"
TRAILER = b"IFLAPPTR"


def _load_payload():
    with open(os.path.abspath(sys.argv[0]), "rb") as handle:
        blob = handle.read()
    start = blob.find(MARKER)
    if start < 0:
        raise SystemExit("Dropper corrupto: no se encontró el payload adjunto.")
    body = blob[start + len(MARKER):]
    stop = body.find(END)
    if stop >= 0:
        body = body[:stop]
    chunks = []
    for line in body.splitlines():
        if line.startswith(b"#"):
            chunks.append(line[1:].strip())
    try:
        return base64.b64decode(b"".join(chunks))
    except Exception as exc:
        raise SystemExit("Dropper corrupto: payload base64 inválido (%s)." % exc)


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _keystream(key, nonce, length):
    out = bytearray()
    counter = 0
    while len(out) < length:
        out.extend(hmac.new(key, nonce + counter.to_bytes(8, "big"), hashlib.sha256).digest())
        counter += 1
    return bytes(out[:length])


def _xor(data, stream):
    return bytes(a ^ b for a, b in zip(data, stream))


def _decrypt(data, password, params):
    mode = params.get("encryption", "none")
    if mode == "none":
        return data
    if not password:
        raise SystemExit("El paquete está cifrado; se requiere contraseña.")
    salt = base64.b64decode(params["salt"])
    nonce = base64.b64decode(params["nonce"])
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, params.get("iterations", 200000), 32)
    if mode == "hmac-sha256-ctr":
        plain = _xor(data, _keystream(key, nonce, len(data)))
        if params.get("mac") and not hmac.compare_digest(params["mac"], hmac.new(key, nonce + plain, hashlib.sha256).hexdigest()):
            raise SystemExit("Firma del payload inválida.")
        return plain
    raise SystemExit("Modo de cifrado no soportado por el stub: " + mode)


def _header(data):
    if data[:8] == MAGIC:
        (length,) = struct.unpack("<I", data[8:12])
        return json.loads(data[12:12 + length].decode("utf-8"))
    index = data.rfind(TRAILER)
    if index >= 0:
        (length,) = struct.unpack("<I", data[index + 8:index + 12])
        return json.loads(data[index + 12:index + 12 + length].decode("utf-8"))
    raise SystemExit("Cabecera .iflapp no reconocida.")


def _safe(dest, name):
    name = name.replace("\\\\", "/")
    if name.startswith("/") or (len(name) >= 2 and name[1] == ":"):
        raise SystemExit("Ruta absoluta en paquete: " + name)
    parts = [p for p in name.split("/") if p not in ("", ".")]
    if any(p == ".." for p in parts):
        raise SystemExit("Path traversal en paquete: " + name)
    return os.path.join(dest, *parts)


def _extract_v2(data, dest, password):
    header = _header(data)
    payload = header["payload"]
    stored = data[payload["offset"]:payload["offset"] + payload["size"]]
    if payload.get("sha256") and _sha(stored) != payload["sha256"]:
        raise SystemExit("El payload no coincide con su digest.")
    raw = _decrypt(stored, password, payload)
    if payload.get("compression") == "lzma":
        raw = lzma.decompress(raw, format=lzma.FORMAT_ALONE)
    files = []
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r") as tar:
        for member in tar.getmembers():
            if member.issym() or member.islnk():
                raise SystemExit("Enlaces no permitidos en el paquete.")
            target = _safe(dest, member.name)
            if member.isdir():
                os.makedirs(target, exist_ok=True)
                continue
            if not member.isfile():
                continue
            os.makedirs(os.path.dirname(target), exist_ok=True)
            source = tar.extractfile(member)
            with open(target, "wb") as output:
                output.write(source.read())
            files.append(target)
    return files, header


def _extract_zip(data, dest):
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        tmp.write(data)
        zip_path = tmp.name
    try:
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(dest)
    finally:
        os.unlink(zip_path)
    return [], {"app": "", "name": ""}


def _launch(dest, header):
    app = header.get("app") or header.get("name") or ""
    roots = [dest, os.path.join(dest, "bin"), os.path.join(dest, "app")]
    candidates = []
    # 1) El nombre declarado en la cabecera.
    if app:
        for root in roots:
            candidates += [os.path.join(root, app), os.path.join(root, app + ".exe"), os.path.join(root, app + ".py")]
    # 2) Puntos de entrada habituales cuando la cabecera no nombra el binario.
    for root in roots:
        for stem in ("main", "app", "run", "__main__", "start"):
            candidates += [os.path.join(root, stem), os.path.join(root, stem + ".exe"), os.path.join(root, stem + ".py")]
    for candidate in candidates:
        if os.path.isfile(candidate):
            if candidate.endswith(".py"):
                return subprocess.call([sys.executable, candidate])
            os.chmod(candidate, os.stat(candidate).st_mode | stat.S_IEXEC)
            return subprocess.call([candidate])
    # 3) Respaldo: primer script o ejecutable en la raíz extraída.
    for entry in sorted(os.listdir(dest)):
        full = os.path.join(dest, entry)
        if not os.path.isfile(full):
            continue
        if entry.endswith(".py"):
            return subprocess.call([sys.executable, full])
        if os.access(full, os.X_OK):
            return subprocess.call([full])
    print("Paquete extraído en: " + dest)
    return 0


def main():
    password = None
    if "--password" in sys.argv:
        password = sys.argv[sys.argv.index("--password") + 1]
    data = _load_payload()
    workdir = tempfile.mkdtemp(prefix="iflapp_run_")
    try:
        if data[:2] == b"PK":
            _extract_zip(data, workdir)
            header = {"app": "", "name": ""}
        else:
            _extract_v2(data, workdir, password)
            header = _header(data)
        return _launch(workdir, header)
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
'''


def create_dropper(
    iflapp_path: Path | str,
    output_path: Path | str,
    *,
    password: Optional[str] = None,
    verify: bool = True,
) -> Path:
    """Genera un dropper autoextraíble con *iflapp_path* adjunto.

    El payload se codifica en base64 sobre líneas comentadas para que el
    dropper resultante siga siendo un archivo Python válido y ejecutable.

    Args:
        iflapp_path: contenedor ``.iflapp`` (v2 o ZIP histórico).
        output_path: ruta del dropper resultante (normalmente ``*.run``).
        password: reservado para compatibilidad; el cifrado se resuelve en
            tiempo de ejecución con ``--password``.
        verify: verificar la firma del contenedor antes de adjuntarlo.
    """
    iflapp_path = Path(iflapp_path)
    output_path = Path(output_path)
    if not iflapp_path.is_file():
        raise IflappError(f"No existe el paquete: {iflapp_path}")
    if verify and sniff_format(iflapp_path) == "iflapp2":
        verify_iflapp(iflapp_path)

    encoded = base64.b64encode(iflapp_path.read_bytes()).decode("ascii")
    payload_lines = [("#" + encoded[i : i + 76]) for i in range(0, len(encoded), 76)]
    stub = _stub_source().encode("utf-8")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as handle:
        handle.write(stub)
        handle.write(b"\n")
        handle.write(DROPPER_MARKER)
        for line in payload_lines:
            handle.write(line.encode("ascii") + b"\n")
        handle.write(DROPPER_END)
    mode = output_path.stat().st_mode
    output_path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return output_path


def dropper_payload_offset(path: Path | str) -> int:
    """Devuelve el desplazamiento del payload dentro de un dropper."""
    data = Path(path).read_bytes()
    index = data.rfind(DROPPER_MARKER)
    if index < 0:
        raise IflappError("El archivo no contiene un payload de dropper.")
    return index + len(DROPPER_MARKER)


def read_dropper_header(path: Path | str):
    """Lee la cabecera del ``.iflapp`` adjunto sin extraerlo."""
    data = Path(path).read_bytes()
    index = data.rfind(DROPPER_MARKER)
    if index < 0:
        raise IflappError("El archivo no contiene un payload de dropper.")
    body = data[index + len(DROPPER_MARKER):]
    stop = body.find(DROPPER_END)
    if stop >= 0:
        body = body[:stop]
    chunks = [line[1:].strip() for line in body.splitlines() if line.startswith(b"#")]
    payload = base64.b64decode(b"".join(chunks))
    temp_dir = Path(tempfile.mkdtemp(prefix="iflapp_dropper_"))
    temp_file = temp_dir / "embedded.iflapp"
    temp_file.write_bytes(payload)
    try:
        return read_iflapp_header(temp_file)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def run_dropper(path: Path | str, *, extra_args: Optional[List[str]] = None) -> int:
    """Ejecuta un dropper ya construido (para pruebas o CI)."""
    return subprocess.call([sys.executable, str(path), *(extra_args or [])])


def compatibility_report() -> dict:
    """Informe de compatibilidad del entorno para construir droppers."""
    return {
        "platform": sys.platform,
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "has_lzma": "lzma" in sys.builtin_module_names or _module_available("lzma"),
        "has_tarfile": _module_available("tarfile"),
        "supports_iflapp_v2": True,
        "supports_legacy_zip": True,
        "signing": "hmac-sha256",
        "compression": ["lzma", "none"],
        "encryption": ["none", "hmac-sha256-ctr", "aes-256-gcm"],
    }


def _module_available(name: str) -> bool:
    import importlib.util

    return importlib.util.find_spec(name) is not None


def encode_payload_b64(path: Path | str) -> str:
    """Utilidad para incrustar un ``.iflapp`` en texto (scripts/documentos)."""
    return base64.b64encode(Path(path).read_bytes()).decode("ascii")
