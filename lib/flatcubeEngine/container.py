# -*- coding: utf-8 -*-
"""Contenedor FlatCube v1 (``.flatkpkg``).

El ``.flatkpkg`` es un **ZIP** auto-descriptivo: no lleva cabecera propia porque
el propio formato de archivo ya describe su contenido. FlatCube es el motor
legacy (Python 3.10, PyInstaller, PyQt4/PyQt5), pensado para entornos portables
o viajes donde no se necesita cifrado.

Este módulo contiene la lógica real del motor: empaquetar un directorio de
aplicación en un ``.flatkpkg`` y volver a leerlo, sin depender de otros motores.
"""
from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

FORMAT_EXTENSION = ".flatkpkg"
MANIFEST_NAME = "flatcube.manifest.json"


class FlatCubeError(RuntimeError):
    """Error al leer o escribir un contenedor ``.flatkpkg``."""


def pack(payload: bytes, *, meta: Optional[Dict] = None) -> bytes:
    """Devuelve el payload tal cual: el ZIP ya es su propio contenedor."""
    return payload


def unpack(container: bytes) -> Tuple[Dict, bytes]:
    """Lee un ``.flatkpkg`` y devuelve ``(manifest, payload_bytes)``."""
    if not _looks_like_zip(container):
        raise FlatCubeError("El contenedor no es un ZIP (.flatkpkg) válido")
    manifest: Dict = {}
    try:
        with zipfile.ZipFile(io.BytesIO(container)) as archive:
            if MANIFEST_NAME in archive.namelist():
                manifest = json.loads(archive.read(MANIFEST_NAME).decode("utf-8"))
    except (zipfile.BadZipFile, OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FlatCubeError(f"Contenedor .flatkpkg ilegible: {exc}") from exc
    if not isinstance(manifest, dict):
        raise FlatCubeError("El manifiesto del contenedor no es un objeto JSON")
    return manifest, container


def pack_directory(
    source_dir: Path,
    output_path: Path,
    *,
    meta: Optional[Dict] = None,
    compression: int = zipfile.ZIP_DEFLATED,
) -> Path:
    """Empaqueta ``source_dir`` en un ``.flatkpkg`` (ZIP) y escribe el manifiesto.

    El manifiesto guarda la lista de entradas y los metadatos del motor para que
    el contenedor sea inspeccionable sin descomprimir del todo.
    """
    source_dir = Path(source_dir)
    if not source_dir.is_dir():
        raise FlatCubeError(f"No existe el directorio a empaquetar: {source_dir}")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    entries: List[str] = []
    with zipfile.ZipFile(output_path, "w", compression=compression) as archive:
        for path in sorted(source_dir.rglob("*")):
            if path.is_file():
                arcname = str(path.relative_to(source_dir)).replace("\\", "/")
                archive.write(path, arcname)
                entries.append(arcname)
        manifest = {
            "engine": "flatcube",
            "format": FORMAT_EXTENSION,
            "compression": "zip",
            "entries": entries,
            **(meta or {}),
        }
        archive.writestr(MANIFEST_NAME, json.dumps(manifest, indent=2, sort_keys=True))
    return output_path


def read_manifest(container: bytes) -> Dict:
    """Devuelve solo el manifiesto del ``.flatkpkg``."""
    manifest, _ = unpack(container)
    return manifest


def _looks_like_zip(data: bytes) -> bool:
    return len(data) >= 4 and data[:4] == b"PK\x03\x04"


__all__ = [
    "FORMAT_EXTENSION",
    "MANIFEST_NAME",
    "FlatCubeError",
    "pack",
    "unpack",
    "pack_directory",
    "read_manifest",
]
