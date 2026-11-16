"""Instalador y desinstalador de artefactos ``.asksome``.

Un ``.asksome`` compilado desde ``.mexf`` se instala extrayendo su payload
firmado en ``<install_root>/<app_id>/``, registrando la instalación (hashes,
manifiesto, accesos directos) en ``install.json`` y creando los accesos directos
del escritorio. La desinstalación es el proceso inverso y admite modo silencioso
para ejecutarse desde ``removeme.py`` o desde la CLI.

Los accesos directos son multiplataforma: en Linux se generan archivos
``.desktop``; en Windows se intenta un ``.lnk`` vía PowerShell y, si no está
disponible, se degrada a un lanzador ``.cmd``. El registro de instalación
permite purgar exactamente lo que se creó.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from lib.asksome_format import extract_asksome, verify_asksome

RECORD_NAME = "install.json"
REMOVEME_NAME = "removeme.py"


class AsksomeInstallError(RuntimeError):
    """Error al instalar o desinstalar un artefacto ``.asksome``."""


@dataclass
class InstallRecord:
    app_id: str
    name: str
    version: str
    install_dir: str
    artifact: str
    artifact_sha256: str
    launcher: str
    shortcuts: List[str] = field(default_factory=list)
    files: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    installed_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _safe_app_id(metadata: Dict[str, Any]) -> str:
    raw = str(metadata.get("id") or metadata.get("app") or "asksome.app").strip()
    cleaned = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in raw)
    return cleaned or "asksome.app"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def default_shortcut_dirs() -> List[Path]:
    """Carpetas donde crear accesos directos, según la plataforma."""
    home = Path.home()
    if sys.platform.startswith("win"):
        appdata = os.environ.get("APPDATA")
        base = Path(appdata) if appdata else home / "AppData" / "Roaming"
        return [base / "Microsoft" / "Windows" / "Start Menu" / "Programs"]
    if sys.platform == "darwin":
        return [home / "Applications"]
    return [home / ".local" / "share" / "applications"]


def _write_linux_desktop(target: Path, record: InstallRecord) -> Optional[Path]:
    try:
        target.mkdir(parents=True, exist_ok=True)
    except OSError:
        return None
    entry = target / f"{record.app_id}.desktop"
    launcher = Path(record.install_dir) / record.launcher
    body = (
        "[Desktop Entry]\n"
        "Type=Application\n"
        f"Name={record.name}\n"
        f"Comment=Instalado por PackageMaker ({record.version})\n"
        f"Exec={sys.executable} {launcher}\n"
        "Terminal=false\n"
    )
    entry.write_text(body, encoding="utf-8")
    entry.chmod(entry.stat().st_mode | stat.S_IXUSR)
    return entry


def _write_windows_shortcut(target: Path, record: InstallRecord) -> Optional[Path]:
    try:
        target.mkdir(parents=True, exist_ok=True)
    except OSError:
        return None
    launcher = Path(record.install_dir) / record.launcher
    entry = target / f"{record.app_id}.cmd"
    entry.write_text(f'@echo off\r\n"{sys.executable}" "{launcher}" %*\r\n', encoding="utf-8")
    return entry


def create_shortcuts(record: InstallRecord, shortcut_dirs: Optional[List[Path]] = None) -> List[str]:
    """Crea los accesos directos y devuelve sus rutas (las que se pudieron crear)."""
    dirs = shortcut_dirs if shortcut_dirs is not None else default_shortcut_dirs()
    created: List[str] = []
    for directory in dirs:
        writer = _write_windows_shortcut if sys.platform.startswith("win") else _write_linux_desktop
        entry = writer(Path(directory), record)
        if entry is not None:
            created.append(str(entry))
    return created


def install_asksome(
    artifact: Path | str,
    install_root: Path | str,
    *,
    create_desktop_shortcuts: bool = True,
    shortcut_dirs: Optional[List[Path]] = None,
) -> InstallRecord:
    """Instala un ``.asksome`` verificando su firma antes de extraer."""
    source = Path(artifact).resolve()
    if not source.is_file():
        raise AsksomeInstallError(f"No existe el artefacto: {source}")

    header = verify_asksome(source)
    metadata = dict(header.get("metadata", {}))
    app_id = _safe_app_id(metadata)

    root = Path(install_root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    target = root / app_id
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)

    extracted = extract_asksome(source, target)
    files = sorted(str(Path(item).relative_to(target)) for item in extracted)

    record = InstallRecord(
        app_id=app_id,
        name=str(metadata.get("name") or app_id),
        version=str(metadata.get("version") or ""),
        install_dir=str(target),
        artifact=str(source),
        artifact_sha256=_sha256_file(source),
        launcher=str(header.get("launcher", "launcher.py")),
        files=files,
        metadata=metadata,
        installed_at=_utcnow(),
    )

    if create_desktop_shortcuts:
        record.shortcuts = create_shortcuts(record, shortcut_dirs)

    (target / RECORD_NAME).write_text(
        json.dumps(record.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_removeme(target, record)
    return record


def read_record(app_id: str, install_root: Path | str) -> InstallRecord:
    path = Path(install_root).resolve() / app_id / RECORD_NAME
    if not path.is_file():
        raise AsksomeInstallError(f"No hay registro de instalación para {app_id}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return InstallRecord(**data)


def list_installed(install_root: Path | str) -> List[InstallRecord]:
    root = Path(install_root)
    if not root.is_dir():
        return []
    records = []
    for entry in sorted(root.iterdir()):
        record_path = entry / RECORD_NAME
        if entry.is_dir() and record_path.is_file():
            try:
                records.append(InstallRecord(**json.loads(record_path.read_text(encoding="utf-8"))))
            except (OSError, json.JSONDecodeError, TypeError):
                continue
    return records


def uninstall_asksome(
    app_id: str,
    install_root: Path | str,
    *,
    silent: bool = False,
) -> List[str]:
    """Purga un ``.asksome`` instalado: accesos directos, archivos y registro.

    Devuelve las rutas eliminadas. Con ``silent=True`` no falla si ya no existe.
    """
    root = Path(install_root).resolve()
    target = root / app_id
    if not target.is_dir():
        if silent:
            return []
        raise AsksomeInstallError(f"No está instalado: {app_id}")

    removed: List[str] = []
    record_path = target / RECORD_NAME
    if record_path.is_file():
        try:
            record = InstallRecord(**json.loads(record_path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError, TypeError):
            record = None
        if record:
            for shortcut in record.shortcuts:
                shortcut_path = Path(shortcut)
                if shortcut_path.is_file():
                    shortcut_path.unlink()
                    removed.append(str(shortcut_path))

    shutil.rmtree(target)
    removed.append(str(target))
    return removed


_REMOVEME_TEMPLATE = '''#!/usr/bin/env python3
"""Desinstalador generado por PackageMaker para {app_id}.

Uso:
    python removeme.py            # elimina este paquete instalado
    python removeme.py --silent   # sin error si ya no existe
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, {repo_root!r})
from lib.asksome_installer import uninstall_asksome


def main(argv=None):
    parser = argparse.ArgumentParser(description="Desinstalar {name}")
    parser.add_argument("--silent", action="store_true", help="No fallar si ya no existe")
    args = parser.parse_args(argv)
    install_root = Path(__file__).resolve().parent.parent
    removed = uninstall_asksome({app_id!r}, install_root, silent=args.silent)
    if not args.silent:
        for item in removed:
            print(f"eliminado: {{item}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def _write_removeme(target: Path, record: InstallRecord) -> Path:
    script = target / REMOVEME_NAME
    repo_root = str(Path(__file__).resolve().parent.parent)
    script.write_text(
        _REMOVEME_TEMPLATE.format(
            app_id=record.app_id, name=record.name, repo_root=repo_root
        ),
        encoding="utf-8",
    )
    return script
