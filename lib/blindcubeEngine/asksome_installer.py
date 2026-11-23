"""Instalador y desinstalador de artefactos ``.asksome``.

Un ``.asksome`` compilado desde ``.mexf`` se instala extrayendo su payload
firmado en ``<install_root>/<app_id>/``, registrando la instalación (hashes,
manifiesto, accesos directos) en ``install.json`` y creando los accesos directos
del escritorio. Genera además el removedor autónomo ``removeme.py`` y,
opcionalmente, un removedor nativo (``removeme.exe`` en Windows / ``removeme.elf``
en Linux) compilado con la jerarquía de backends de ``lib.compilers``. La
desinstalación es el proceso inverso y admite modo silencioso para ejecutarse
desde el removedor o desde la CLI.

Los accesos directos son multiplataforma: en Linux se generan archivos
``.desktop``; en Windows se intenta un ``.lnk`` vía PowerShell y, si no está
disponible, se degrada a un lanzador ``.cmd``. El registro de instalación
permite purgar exactamente lo que se creó.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from lib.blindcubeEngine.asksome_format import extract_asksome, verify_asksome
from lib.file_ops import list_directory, path_is_dir, path_is_file

RECORD_NAME = "install.json"
REMOVEME_NAME = "removeme.py"
REMOVEME_STEM = "removeme"


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
    remover: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


_REQUIRED_TEXT_FIELDS = (
    "app_id",
    "name",
    "version",
    "install_dir",
    "artifact",
    "artifact_sha256",
    "launcher",
)
_OPTIONAL_TEXT_FIELDS = ("installed_at", "remover")


def _record_from_mapping(data: Dict[str, Any]) -> InstallRecord:
    """Construye un ``InstallRecord`` validando los tipos de sus campos.

    ``InstallRecord(**data)`` acepta cualquier tipo porque el dataclass no
    valida, así que un ``install.json`` editado a mano con ``"shortcuts": 5``
    producía un registro que reventaba más tarde al iterarlo. Los campos de
    texto obligatorios deben ser cadenas; los opcionales y las colecciones se
    degradan a su valor por defecto para que la desinstalación siga funcionando.
    """
    if not isinstance(data, dict):
        raise TypeError("el registro no es un objeto")
    values: Dict[str, Any] = {}
    for field_name in _REQUIRED_TEXT_FIELDS:
        value = data.get(field_name)
        if not isinstance(value, str):
            raise TypeError(f"{field_name} debe ser texto")
        values[field_name] = value
    for field_name in _OPTIONAL_TEXT_FIELDS:
        value = data.get(field_name, "")
        values[field_name] = value if isinstance(value, str) else ""
    shortcuts = data.get("shortcuts", [])
    values["shortcuts"] = [str(item) for item in shortcuts] if isinstance(shortcuts, list) else []
    files = data.get("files", [])
    values["files"] = [str(item) for item in files] if isinstance(files, list) else []
    metadata = data.get("metadata", {})
    values["metadata"] = dict(metadata) if isinstance(metadata, dict) else {}
    return InstallRecord(**values)


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


_APP_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")


def _safe_app_id(metadata: Dict[str, Any]) -> str:
    raw = str(metadata.get("id") or metadata.get("app") or "asksome.app").strip()
    cleaned = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in raw)
    # ``.`` y ``..`` son componentes de ruta, no identificadores: usarlos como
    # carpeta de instalación apuntaría a la raíz o a su directorio padre.
    if not cleaned.strip("."):
        return "asksome.app"
    return cleaned


def _validated_app_id(app_id: object) -> str:
    """Valida un ``app_id`` recibido por API/CLI antes de tocar el disco.

    Debe ser un único componente de ruta (sin separadores, sin ``..`` y sin
    unidad de Windows) para que la instalación no escape de su raíz.
    """
    text = str(app_id or "").strip()
    if text in (".", "..") or not _APP_ID_PATTERN.match(text):
        raise AsksomeInstallError(f"Identificador de app inválido: {app_id!r}")
    return text


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


def _desktop_exec_quote(value: object) -> str:
    """Cita un argumento del campo ``Exec`` según la especificación Desktop Entry.

    Sin las comillas, una ruta con espacios se parte en varios argumentos y el
    lanzador intenta ejecutar la ruta truncada. Los caracteres reservados dentro
    de comillas y los códigos de campo (``%``) también se escapan.
    """
    text = str(value)
    for char in ("\\", '"', "`", "$"):
        text = text.replace(char, "\\" + char)
    text = text.replace("%", "%%")
    return f'"{text}"'


def _desktop_text(value: object) -> str:
    """Aplana un valor de texto para que no inyecte claves nuevas en el .desktop."""
    return " ".join(str(value).split())


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
        f"Name={_desktop_text(record.name)}\n"
        f"Comment={_desktop_text(f'Instalado por PackageMaker ({record.version})')}\n"
        f"Exec={_desktop_exec_quote(sys.executable)} {_desktop_exec_quote(launcher)}\n"
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
    password: str | None = None,
    removeme_binary: bool = False,
    backend: str | None = None,
    log_callback=None,
) -> InstallRecord:
    """Instala un ``.asksome`` verificando su firma antes de extraer.

    Con ``removeme_binary=True`` se compila además un removedor nativo
    (``removeme.exe``/``removeme.elf``) junto al script ``removeme.py``; si no
    hay backend disponible se conserva únicamente el script.
    """
    source = Path(artifact).resolve()
    if not source.is_file():
        raise AsksomeInstallError(f"No existe el artefacto: {source}")

    header = verify_asksome(source)
    metadata = dict(header.get("metadata", {}))
    app_id = _validated_app_id(_safe_app_id(metadata))

    root = Path(install_root).resolve()
    try:
        root.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise AsksomeInstallError(
            f"No se pudo preparar la raíz de instalación {root}: {exc}"
        ) from exc
    target = root / app_id
    try:
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True)
    except OSError as exc:
        raise AsksomeInstallError(
            f"No se pudo preparar el destino de instalación {target}: {exc}"
        ) from exc

    try:
        extracted = extract_asksome(source, target, password=password)
    except OSError as exc:
        raise AsksomeInstallError(
            f"No se pudo extraer el artefacto en {target}: {exc}"
        ) from exc
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

    _write_removeme(target, record)
    record.remover = REMOVEME_NAME
    if removeme_binary:
        binary = compile_removeme_binary(
            target, preferred_backend=backend, log_callback=log_callback
        )
        if binary is not None:
            record.remover = binary.name

    (target / RECORD_NAME).write_text(
        json.dumps(record.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return record


def read_record(app_id: str, install_root: Path | str) -> InstallRecord:
    name = _validated_app_id(app_id)
    path = Path(install_root).resolve() / name / RECORD_NAME
    if not path.is_file():
        raise AsksomeInstallError(f"No hay registro de instalación para {app_id}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise AsksomeInstallError(f"Registro de instalación ilegible para {app_id}: {exc}") from exc
    try:
        return _record_from_mapping(data)
    except TypeError as exc:
        raise AsksomeInstallError(f"Registro de instalación inválido para {app_id}: {exc}") from exc


def build_removeme(
    app_id: str,
    install_root: Path | str,
    *,
    preferred_backend: str | None = None,
    log_callback=None,
) -> Optional[Path]:
    """Compila el removedor de una instalación existente a su binario nativo.

    Reescribe ``removeme.py`` desde el registro y lo compila a
    ``removeme.exe``/``removeme.elf``. Actualiza el campo ``remover`` del
    registro y devuelve la ruta del binario (o ``None`` si no se pudo compilar).
    """
    root = Path(install_root).resolve()
    target = root / _validated_app_id(app_id)
    record = read_record(app_id, install_root)
    _write_removeme(target, record)
    binary = compile_removeme_binary(
        target, preferred_backend=preferred_backend, log_callback=log_callback
    )
    if binary is None:
        return None
    record.remover = binary.name
    (target / RECORD_NAME).write_text(
        json.dumps(record.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return binary


def list_installed(install_root: Path | str) -> List[InstallRecord]:
    root = Path(install_root)
    if not path_is_dir(root):
        return []
    records = []
    for entry in list_directory(root):
        record_path = entry / RECORD_NAME
        if path_is_dir(entry) and path_is_file(record_path):
            try:
                records.append(_record_from_mapping(json.loads(record_path.read_text(encoding="utf-8"))))
            except (OSError, ValueError, TypeError):
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
    target = root / _validated_app_id(app_id)
    if not target.is_dir():
        if silent:
            return []
        raise AsksomeInstallError(f"No está instalado: {app_id}")

    removed: List[str] = []
    record_path = target / RECORD_NAME
    if record_path.is_file():
        try:
            record = _record_from_mapping(json.loads(record_path.read_text(encoding="utf-8")))
        except (OSError, ValueError, TypeError):
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

Es autónomo: no necesita el repositorio de PackageMaker ni importar ``lib``.
Lee su propio ``install.json`` cuando existe y, si no, usa los accesos directos
incrustados en el momento de la instalación.

Uso:
    removeme                   # desinstala; usa GUI si hay entorno gráfico
    removeme --silent          # sin salida ni GUI; no falla si ya no existe
    removeme --console         # fuerza la salida por consola
    removeme --gui             # fuerza la interfaz gráfica (si PyQt6 está disponible)
    removeme --keep-shortcuts  # conserva los accesos directos
"""
import argparse
import json
import os
import shutil
import sys
from pathlib import Path

APP_ID = {app_id!r}
NAME = {name!r}
EMBEDDED_SHORTCUTS = {shortcuts!r}


def _self_file():
    """Ruta real de este removedor (script, zipapp o binario congelado)."""
    argv0 = (sys.argv[0] or "").strip()
    if argv0:
        try:
            candidate = Path(argv0).resolve()
        except OSError:
            candidate = None
        if candidate is not None and candidate.is_file():
            return candidate
    here = Path(__file__).resolve()
    # Dentro de un zipapp ``__file__`` vive en el archivo; su padre es el archivo.
    if here.parent.is_file():
        return here.parent
    return here


def _install_dir():
    """Carpeta de instalación: la que contiene a este removedor."""
    if getattr(sys, "frozen", False) or hasattr(sys, "_MEIPASS"):
        return Path(sys.executable).resolve().parent
    return _self_file().parent


def _shortcuts(target):
    record = target / {record_name!r}
    if record.is_file():
        try:
            data = json.loads(record.read_text(encoding="utf-8"))
            return list(data.get("shortcuts") or EMBEDDED_SHORTCUTS)
        except (OSError, ValueError):
            pass
    return list(EMBEDDED_SHORTCUTS)


class _ConsoleReporter:
    """Informa por consola; silencioso con ``--silent``."""

    def __init__(self, quiet):
        self.quiet = quiet

    def start(self, total):
        pass

    def step(self, done, total, message):
        if not self.quiet and message:
            print(message)

    def finish(self, removed):
        pass


class _GuiReporter:
    """Progreso en vivo con PyQt6; el llamador cae a consola si no está disponible."""

    def __init__(self):
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import QApplication, QProgressDialog

        self._app = QApplication.instance() or QApplication([])
        self._dialog = QProgressDialog("Preparando la desinstalación...", None, 0, 100)
        self._dialog.setWindowTitle("Desinstalando " + NAME)
        self._dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self._dialog.setMinimumDuration(0)
        self._dialog.setValue(1)
        self._app.processEvents()

    def start(self, total):
        pass

    def step(self, done, total, message):
        if message:
            self._dialog.setLabelText(message)
        self._dialog.setValue(int(done * 100 / max(total, 1)))
        self._app.processEvents()

    def finish(self, removed):
        self._dialog.setValue(100)
        self._app.processEvents()
        self._dialog.close()


def _display_available():
    if sys.platform.startswith("win") or sys.platform == "darwin":
        return True
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def _make_reporter(args):
    if args.silent:
        return _ConsoleReporter(quiet=True)
    if args.gui or (not args.console and _display_available()):
        try:
            return _GuiReporter()
        except Exception:
            pass
    return _ConsoleReporter(quiet=False)


def _remove(target, keep_shortcuts, reporter):
    items = [] if keep_shortcuts else _shortcuts(target)
    total = len(items) + 1
    reporter.start(total)
    removed = []
    done = 0
    for item in items:
        path = Path(item)
        done += 1
        if path.is_file():
            path.unlink()
            removed.append(str(path))
            reporter.step(done, total, "eliminado: " + str(path))
        else:
            reporter.step(done, total, "")
    if target.is_dir():
        shutil.rmtree(target)
        removed.append(str(target))
        reporter.step(total, total, "eliminado: " + str(target))
    reporter.finish(removed)
    return removed


def main(argv=None):
    parser = argparse.ArgumentParser(description="Desinstalar " + NAME)
    parser.add_argument("--silent", action="store_true", help="Sin salida ni GUI; no fallar si ya no existe")
    parser.add_argument("--console", action="store_true", help="Forzar la salida por consola")
    parser.add_argument("--gui", action="store_true", help="Forzar la interfaz gráfica")
    parser.add_argument("--keep-shortcuts", action="store_true", help="No retirar accesos directos")
    args = parser.parse_args(argv)

    target = _install_dir()
    if not target.is_dir():
        if args.silent:
            return 0
        print("no existe: " + str(target), file=sys.stderr)
        return 1

    _remove(target, args.keep_shortcuts, _make_reporter(args))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def removeme_binary_name() -> str:
    """Nombre del removedor binario según la plataforma (``removeme.exe``/``.elf``)."""
    if sys.platform.startswith("win"):
        return f"{REMOVEME_STEM}.exe"
    if sys.platform == "darwin":
        return f"{REMOVEME_STEM}.app"
    return f"{REMOVEME_STEM}.elf"


def _write_removeme(target: Path, record: InstallRecord) -> Path:
    script = target / REMOVEME_NAME
    script.write_text(
        _REMOVEME_TEMPLATE.format(
            app_id=record.app_id,
            name=record.name,
            shortcuts=list(record.shortcuts),
            record_name=RECORD_NAME,
        ),
        encoding="utf-8",
    )
    script.chmod(script.stat().st_mode | stat.S_IXUSR)
    return script


def compile_removeme_binary(
    target: Path | str,
    *,
    preferred_backend: str | None = None,
    log_callback=None,
) -> Optional[Path]:
    """Compila ``removeme.py`` a un binario nativo ``removeme.exe``/``removeme.elf``.

    Usa la jerarquía de backends de ``lib.compilers`` (Nuitka → PyInstaller →
    zipapp). Devuelve la ruta del binario escrito en *target*, o ``None`` si no
    se pudo compilar (en cuyo caso queda el script ``removeme.py``).
    """
    from lib.blindcubeEngine.compilers import CompilerUnavailableError, get_backend, resolve_backend

    target = Path(target)
    script = target / REMOVEME_NAME
    if not script.is_file():
        return None

    def _log(message: str) -> None:
        if log_callback:
            log_callback(message)

    # Cadena de respaldo real: ``resolve_backend`` sólo comprueba que el módulo
    # sea importable, pero un backend puede estar instalado y aun así fallar al
    # compilar (p. ej. Nuitka con una versión de Python no soportada). Se prueba
    # cada candidato y se usa el primero que produzca un binario.
    candidates: List[str] = []
    for name in (preferred_backend, "nuitka", "pyinstaller", "zipapp"):
        if name and name not in candidates:
            candidates.append(name)
    try:
        resolved = resolve_backend(preferred_backend, log_callback=log_callback)
        if resolved.name not in candidates:
            candidates.insert(0, resolved.name)
    except CompilerUnavailableError as exc:
        _log(f"[WARN] Sin backend preferido para el removedor: {exc}")

    binary_name = removeme_binary_name()
    build_dir = Path(tempfile.mkdtemp(prefix="pm-removeme-"))
    staging = build_dir / "src"
    staging.mkdir()
    # Compilar desde un staging que contiene sólo el removedor: así el zipapp
    # no arrastra el resto del paquete y el binario queda autocontenido.
    staged_script = staging / REMOVEME_NAME
    shutil.copy2(script, staged_script)
    try:
        for name in candidates:
            try:
                backend = get_backend(name, log_callback=log_callback)
            except CompilerUnavailableError:
                continue
            if not backend.is_available():
                continue
            try:
                produced = backend.compile(
                    script_path=str(staged_script),
                    output_name=REMOVEME_STEM,
                    output_dir=str(build_dir / "out"),
                    windowed=False,
                    onefile=True,
                    excludes=["PyQt6", "PyQt5", "tkinter"],
                    build_dir=str(build_dir / "work"),
                )
            except Exception as exc:  # noqa: BLE001 - se prueba el siguiente backend
                _log(f"[WARN] Backend {name} falló al compilar el removedor: {exc}")
                continue
            if not produced:
                _log(f"[WARN] Backend {name} no produjo el removedor: {backend.last_error}")
                continue
            final = target / binary_name
            shutil.copy2(produced, final)
            final.chmod(final.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            return final
        _log("[WARN] Ningún backend pudo compilar el removedor; queda removeme.py")
        return None
    finally:
        shutil.rmtree(build_dir, ignore_errors=True)
