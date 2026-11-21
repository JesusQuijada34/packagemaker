# -*- coding: utf-8 -*-
"""Núcleo de motores de PackageMaker (Fase 1 de bugs.txt).

Cada motor vive en su propio paquete bajo ``lib/`` (``makeselfEngine``,
``flatcubeEngine``, ``blindcubeEngine``) y declara de forma aislada su stack,
su versión de Python, su backend de compilación y el formato de salida. Este
módulo reúne la base común, el registro y el entorno virtual efímero que cada
motor prepara a partir de ``lib/requirements.txt``.

El diseño separa el **plan** (``EngineEnvironment.plan``) de la **ejecución**
(``EngineEnvironment.prepare``) para poder inspeccionar qué haría un motor sin
tocar el disco ni la red.
"""
from __future__ import annotations

import json
import lzma
import struct
import sys
import venv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

ENGINE_ROLE_GENERATOR = "generator"
ENGINE_ROLE_COMPILER = "compiler"

_HEADER_MAGIC_LEN = 8
_HEADER_LEN_FMT = "<I"


class EngineError(RuntimeError):
    """Error al resolver o preparar un motor de compilación."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_requirements(requirements_path: Optional[Path] = None) -> List[str]:
    """Lee las dependencias de ``lib/requirements.txt`` sin comentarios.

    Se ignoran las líneas vacías y las que empiezan por ``#`` (las directivas
    ``-r`` también se descartan porque no son paquetes instalables directos).
    """
    path = Path(requirements_path) if requirements_path else _repo_root() / "lib" / "requirements.txt"
    if not path.is_file():
        return []
    packages: List[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        packages.append(line)
    return packages


@dataclass(frozen=True)
class BuildEngine:
    """Descripción inmutable de un motor."""

    id: str
    display_name: str
    role: str
    status: str
    python_version: str
    backend: Optional[str]
    stack: str
    description: str
    format_extension: str = ""
    compression: str = ""
    magic: bytes = b""
    selectable: bool = False
    notes: str = ""

    @property
    def is_legacy(self) -> bool:
        return self.status == "legacy"

    def header(self, *, payload_len: int, meta: Optional[Dict] = None) -> bytes:
        """Construye la cabecera con *magic bytes* y longitud del payload.

        Formato: ``[MAGIC 8B][payload_len uint32 LE][JSON meta]``. El bloque
        JSON queda separado del binario por su propia longitud explícita, de
        modo que el contenedor es auto-descriptivo y verificable.
        """
        if not self.magic:
            raise EngineError(f"El motor '{self.id}' no define formato contenedor")
        blob = json.dumps(
            {
                "engine": self.id,
                "extension": self.format_extension,
                "compression": self.compression,
                **(meta or {}),
            },
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return self.magic.ljust(_HEADER_MAGIC_LEN, b"\x00") + struct.pack(
            _HEADER_LEN_FMT, payload_len
        ) + struct.pack(_HEADER_LEN_FMT, len(blob)) + blob

    def pack(self, payload: bytes, *, meta: Optional[Dict] = None) -> bytes:
        """Empaqueta un payload con la cabecera del motor y su compresión.

        Un motor sin *magic bytes* propio (p. ej. FlatCube, cuyo ``.flatkpkg``
        es un ZIP) devuelve el payload tal cual: el formato de archivo ya es su
        propio contenedor auto-descriptivo.
        """
        data = payload
        if self.compression == "lzma":
            data = lzma.compress(payload, format=lzma.FORMAT_ALONE, preset=6)
        elif self.compression == "zlib":
            import zlib

            data = zlib.compress(payload)
        elif self.compression not in ("", "none", "zip"):
            raise EngineError(f"Compresión no soportada: {self.compression}")
        if not self.magic:
            return data
        return self.header(payload_len=len(payload), meta=meta) + data

    def read_header(self, raw: bytes) -> Tuple[Dict, int]:
        """Lee la cabecera y devuelve ``(meta, offset_payload)``."""
        if not self.magic:
            raise EngineError(f"El motor '{self.id}' no define formato contenedor")
        expected = self.magic.ljust(_HEADER_MAGIC_LEN, b"\x00")
        if not raw.startswith(expected):
            raise EngineError("Magic bytes del contenedor no coinciden")
        base = _HEADER_MAGIC_LEN
        if len(raw) < base + 8:
            raise EngineError("Cabecera del contenedor truncada")
        (payload_len,) = struct.unpack(_HEADER_LEN_FMT, raw[base : base + 4])
        (blob_len,) = struct.unpack(_HEADER_LEN_FMT, raw[base + 4 : base + 8])
        end = base + 8 + blob_len
        if end > len(raw):
            raise EngineError("Cabecera del contenedor truncada")
        try:
            meta = json.loads(raw[base + 8 : end].decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise EngineError(f"Cabecera del contenedor ilegible: {exc}") from exc
        if not isinstance(meta, dict):
            raise EngineError("La cabecera del contenedor no es un objeto JSON")
        meta["payload_len"] = payload_len
        return meta, end


@dataclass
class EngineEnvironment:
    """Entorno virtual efímero de un motor.

    El plan describe los pasos (crear el venv, instalar dependencias y, si
    procede, descargar el intérprete del motor). ``prepare`` los ejecuta sobre
    un directorio de trabajo y ``moon_fix`` regenera la estructura del proyecto.
    """

    engine: BuildEngine
    workdir: Path
    requirements: Sequence[str] = field(default_factory=list)
    requirements_path: Optional[Path] = None

    def __post_init__(self) -> None:
        self.workdir = Path(self.workdir)
        if not self.requirements:
            self.requirements = load_requirements(self.requirements_path)

    @property
    def venv_dir(self) -> Path:
        return self.workdir / "venv"

    @property
    def python_executable(self) -> Path:
        if sys.platform.startswith("win"):
            return self.venv_dir / "Scripts" / "python.exe"
        return self.venv_dir / "bin" / "python"

    def plan(self) -> Dict:
        """Describe los pasos sin ejecutarlos (inspeccionable y testeable)."""
        return {
            "engine": self.engine.id,
            "python_version": self.engine.python_version,
            "backend": self.engine.backend,
            "venv_dir": str(self.venv_dir),
            "requirements": list(self.requirements),
            "download_python": self.engine.python_version
            != f"{sys.version_info.major}.{sys.version_info.minor}",
            "steps": [
                "download_python" if self.engine.python_version
                != f"{sys.version_info.major}.{sys.version_info.minor}" else "use_system_python",
                "create_venv",
                "install_requirements",
            ],
        }

    def prepare(self, *, with_pip: bool = True) -> Path:
        """Crea el entorno virtual e instala las dependencias del motor."""
        self.workdir.mkdir(parents=True, exist_ok=True)
        builder = venv.EnvBuilder(with_pip=with_pip, clear=False)
        builder.create(str(self.venv_dir))
        if self.requirements and with_pip:
            import subprocess

            subprocess.check_call(
                [str(self.python_executable), "-m", "pip", "install", *self.requirements],
                stdout=subprocess.DEVNULL,
            )
        return self.venv_dir

    def moon_fix(self, project_path: Path, **kwargs) -> Dict:
        """Regeneración efervescente: repara la estructura del proyecto.

        Delega en el motor de generación (``makeselfEngine``), que restaura
        carpetas, ``details.xml`` y los ficheros faltantes sin sobrescribir los
        guiones existentes.
        """
        from lib.makeselfEngine.templates import repair_project_from_templates

        return repair_project_from_templates(Path(project_path), **kwargs)


_REGISTRY: Dict[str, BuildEngine] = {}


def register_engine(engine: BuildEngine) -> BuildEngine:
    """Registra un motor; el último registro con un id gana."""
    if engine.id in _REGISTRY:
        raise EngineError(f"El motor '{engine.id}' ya está registrado")
    _REGISTRY[engine.id] = engine
    return engine


def get_engine(engine_id: str) -> BuildEngine:
    try:
        return _REGISTRY[engine_id]
    except KeyError:
        raise EngineError(f"Motor desconocido: {engine_id}") from None


def available_engines() -> Dict[str, BuildEngine]:
    return dict(_REGISTRY)


def selectable_engines() -> List[BuildEngine]:
    """Motores que el usuario elige de forma explícita antes de compilar."""
    return [e for e in _REGISTRY.values() if e.selectable]


def resolve_engine(engine_id: Optional[str]) -> BuildEngine:
    """Devuelve el motor pedido o el estándar seleccionable por defecto."""
    if engine_id:
        return get_engine(engine_id)
    for engine in selectable_engines():
        if engine.status == "standard":
            return engine
    for engine in selectable_engines():
        return engine
    raise EngineError("No hay motores seleccionables registrados")
