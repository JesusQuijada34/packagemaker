"""Integración con el shell nativo del SO para paquetes ``.iflapp`` / ``.asksome``.

Expone, sin descifrar ni descomprimir el payload, la información que el sistema
operativo necesita para mostrar metadatos y vistas previas de iconos al pasar el
cursor (hover) y en el panel de propiedades:

* :func:`package_info` — identidad, formato y recuento de ficheros de la cabecera.
* :func:`export_icon_preview` — vuelca el icono a PNG para el *thumbnailer*.
* :func:`install_shell_integration` — registra la asociación de tipo MIME y el
  generador de miniaturas (``.thumbnailer`` en freedesktop, ``.reg`` en Windows).

Todo el módulo es puro salvo la escritura de los ficheros de integración, de modo
que es verificable sin GUI ni red.
"""
from __future__ import annotations

import base64
import sys
from pathlib import Path
from typing import Dict, List, Optional

IFLAPP_MIME = "application/x-iflapp"
ASKSOME_MIME = "application/x-asksome"
MIME_TYPES = (IFLAPP_MIME, ASKSOME_MIME)


def detect_kind(path: Path | str) -> str:
    """Devuelve ``"iflapp"``, ``"asksome"`` o ``"unknown"`` según la cabecera."""
    target = Path(path)
    if not target.is_file():
        return "unknown"
    data = target.read_bytes()[:16]
    if data.startswith(b"ASKSOME1\x00"):
        return "asksome"
    if data.startswith(b"IFLAPP"):
        return "iflapp"
    return "unknown"


def _asksome_header(path: Path) -> Dict:
    from lib.blindcubeEngine.asksome_format import read_asksome_header

    return read_asksome_header(path)


def _iflapp_reader(path: Path):
    from lib.blindcubeEngine.iflapp_reader import IflappReader

    return IflappReader(path)


def package_info(path: Path | str) -> Dict:
    """Resumen de cabecera listo para el panel de propiedades del SO.

    No descifra el payload: para ``.asksome`` cifrado la información sigue
    disponible porque la cabecera va en claro.
    """
    target = Path(path).resolve()
    kind = detect_kind(target)
    if kind == "unknown":
        raise ValueError(f"No es un paquete .iflapp/.asksome: {target}")

    if kind == "iflapp":
        info = _iflapp_reader(target).info()
        return {
            "path": str(target),
            "kind": "iflapp",
            "format": info.format,
            "format_version": info.format_version,
            "compression": info.compression,
            "encryption": info.encryption,
            "file_count": info.file_count,
            "icon_bytes": info.icon_bytes,
            "identity": dict(info.identity),
            "mime_type": IFLAPP_MIME,
        }

    header = _asksome_header(target)
    metadata = dict(header.get("metadata", {}))
    icon = header.get("icon", "")
    return {
        "path": str(target),
        "kind": "asksome",
        "format": header.get("format", "asksome"),
        "format_version": header.get("format_version", 1),
        "compression": header.get("compression", ""),
        "encryption": header.get("encryption", "none"),
        "file_count": len(header.get("manifest", [])),
        "icon_bytes": len(base64.b64decode(icon)) if icon else 0,
        "identity": {
            "publisher": metadata.get("publisher", ""),
            "app": metadata.get("app", ""),
            "name": metadata.get("name", ""),
            "version": metadata.get("version", ""),
            "platform": metadata.get("platform", ""),
            "signer": metadata.get("signer", ""),
        },
        "mime_type": ASKSOME_MIME,
    }


def icon_bytes(path: Path | str) -> Optional[bytes]:
    """Devuelve los bytes del icono de la cabecera, o ``None`` si no hay."""
    target = Path(path)
    kind = detect_kind(target)
    if kind == "iflapp":
        return _iflapp_reader(target).icon_bytes()
    if kind == "asksome":
        encoded = _asksome_header(target).get("icon", "")
        return base64.b64decode(encoded) if encoded else None
    return None


def export_icon_preview(
    path: Path | str,
    out_dir: Path | str,
    *,
    size: int = 256,
) -> Optional[Path]:
    """Vuelca el icono a PNG en ``out_dir`` para el generador de miniaturas.

    Requiere Pillow para redimensionar; sin él, si el icono ya es PNG se copia
    tal cual y en cualquier otro caso se devuelve ``None``.
    """
    data = icon_bytes(path)
    if not data:
        return None
    target = Path(out_dir)
    target.mkdir(parents=True, exist_ok=True)
    destination = target / f"{Path(path).stem}-{size}.png"
    is_png = data[:8] == b"\x89PNG\r\n\x1a\n"
    try:
        from io import BytesIO

        from PIL import Image

        with Image.open(BytesIO(data)) as image:
            image.convert("RGBA").resize((size, size)).save(destination, "PNG")
        return destination
    except (ImportError, OSError, ValueError):
        # Sin Pillow, o icono no reconocido: sólo se puede reenviar si ya es PNG.
        if is_png:
            destination.write_bytes(data)
            return destination
        return None


def _runner_script(python: str, root: Path) -> str:
    return (
        "#!/bin/sh\n"
        f'PYTHONPATH="{root}" exec "{python}" -m lib.native_shell --thumbnail "$@";\n'
    )


def write_thumbnailer(
    directory: Path | str,
    *,
    python: Optional[str] = None,
    root: Optional[Path | str] = None,
) -> Path:
    """Escribe un ``.thumbnailer`` de freedesktop que genera PNG de 256 px."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    root = Path(root) if root else Path(__file__).resolve().parent.parent
    python = python or sys.executable
    runner = directory / "packagemaker-thumbnailer"
    runner.write_text(_runner_script(python, root), encoding="utf-8")
    runner.chmod(0o755)
    thumbnailer = directory / "packagemaker.thumbnailer"
    thumbnailer.write_text(
        "[Thumbnailer Entry]\n"
        f"TryExec={python}\n"
        f"Exec={runner} %i %o %s\n"
        f"MimeType={';'.join(MIME_TYPES)};\n",
        encoding="utf-8",
    )
    return thumbnailer


def write_desktop_entry(
    directory: Path | str,
    *,
    exec_cmd: str,
    icon: str = "application-x-executable",
    name: str = "PackageMaker Package",
) -> Path:
    """Escribe un ``.desktop`` que asocia los tipos MIME de los paquetes."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    entry = directory / "packagemaker-package.desktop"
    entry.write_text(
        "[Desktop Entry]\n"
        "Type=Application\n"
        f"Name={name}\n"
        f"Exec={exec_cmd} %f\n"
        f"Icon={icon}\n"
        f"MimeType={';'.join(MIME_TYPES)};\n"
        "NoDisplay=true\n"
        "Terminal=false\n",
        encoding="utf-8",
    )
    return entry


def _registry_scaffold() -> str:
    """Plantilla ``.reg`` que asocia los tipos MIME y el generador de iconos."""
    lines = ["Windows Registry Editor Version 5.00", ""]
    for mime, ext in ((IFLAPP_MIME, ".iflapp"), (ASKSOME_MIME, ".asksome")):
        lines += [
            f"[HKEY_CLASSES_ROOT\\{ext}]",
            f'@="{mime}"',
            "",
            f"[HKEY_CLASSES_ROOT\\{mime}\\DefaultIcon]",
            '@="%1"',
            "",
        ]
    return "\n".join(lines) + "\n"


def install_shell_integration(
    *,
    target_dir: Optional[Path | str] = None,
    platform_name: Optional[str] = None,
) -> Dict[str, List[str]]:
    """Registra la integración del shell y devuelve las rutas escritas.

    En Linux/macOS (freedesktop) escribe el ``.thumbnailer`` y el ``.desktop``;
    en Windows genera un ``.reg`` para importar manualmente. Nunca lanza si el
    directorio destino no se puede escribir: informa en la lista ``skipped``.
    """
    platform_name = platform_name or sys.platform
    written: List[str] = []
    skipped: List[str] = []

    if platform_name.startswith("win"):
        directory = Path(target_dir) if target_dir else Path.cwd()
        try:
            directory.mkdir(parents=True, exist_ok=True)
            reg = directory / "packagemaker-shell.reg"
            reg.write_text(_registry_scaffold(), encoding="utf-16")
            written.append(str(reg))
        except OSError as exc:
            skipped.append(f"{directory}: {exc}")
        return {"written": written, "skipped": skipped}

    base = Path(target_dir) if target_dir else Path.home() / ".local" / "share"
    try:
        thumbnailer = write_thumbnailer(base / "thumbnailers")
        written.append(str(thumbnailer))
        desktop = write_desktop_entry(
            base / "applications",
            exec_cmd="packagemaker",
        )
        written.append(str(desktop))
    except OSError as exc:
        skipped.append(f"{base}: {exc}")
    return {"written": written, "skipped": skipped}


def _thumbnail_main(argv: List[str]) -> int:
    """Entrada del generador de miniaturas: ``--thumbnail IN OUT SIZE``."""
    if len(argv) < 3:
        print("uso: -m lib.native_shell --thumbnail IN OUT SIZE", file=sys.stderr)
        return 2
    source, destination = argv[0], argv[1]
    try:
        size = int(argv[2])
    except (IndexError, ValueError):
        size = 256
    png = export_icon_preview(source, Path(destination).parent, size=size)
    if not png:
        return 1
    if png != Path(destination):
        Path(destination).write_bytes(png.read_bytes())
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--thumbnail":
        raise SystemExit(_thumbnail_main(args[1:]))
    if args and args[0] == "--info":
        import json

        print(json.dumps(package_info(args[1]), indent=2, ensure_ascii=False))
        raise SystemExit(0)
    print("uso: -m lib.native_shell --thumbnail IN OUT SIZE | --info FILE", file=sys.stderr)
    raise SystemExit(2)
