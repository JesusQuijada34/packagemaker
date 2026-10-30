# -*- coding: utf-8 -*-
"""Handler de lectura de ``.iflapp`` por cabecera.

Expone una API pequeña y estable para leer la identidad de un paquete
(icono, ``details.xml`` y manifiesto) **sin descifrar ni descomprimir** el
payload. Está pensado para consumirse desde el CLI, la GUI y pruebas.

Uso::

    from lib.iflapp_reader import IflappReader

    reader = IflappReader("Paquete.iflapp")
    print(reader.summary())
    reader.export_assets("./salida")
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from lib.iflapp_format import (
    DEFAULT_SIGNING_KEY,
    IflappError,
    IflappHeader,
    export_header_assets,
    list_iflapp,
    read_iflapp_header,
    sniff_format,
    verify_iflapp,
)


@dataclass
class IflappInfo:
    """Resumen legible de un paquete, derivado sólo de su cabecera."""

    path: str
    format: str
    format_version: int
    compression: str
    encryption: str
    file_count: int
    icon_bytes: int
    identity: Dict[str, str]
    manifest: List[Dict]

    def as_dict(self) -> Dict:
        return {
            "path": self.path,
            "format": self.format,
            "format_version": self.format_version,
            "compression": self.compression,
            "encryption": self.encryption,
            "file_count": self.file_count,
            "icon_bytes": self.icon_bytes,
            "identity": self.identity,
            "manifest": self.manifest,
        }

    def summary(self) -> str:
        ident = self.identity
        lines = [
            f"Paquete    : {self.path}",
            f"Formato    : {self.format} v{self.format_version} "
            f"({self.compression}/{self.encryption})",
            f"Publisher  : {ident.get('publisher', '')}",
            f"App        : {ident.get('app', '')} ({ident.get('name', '')})",
            f"Version    : {ident.get('version', '')}",
            f"Autor      : {ident.get('author', '')}",
            f"Plataforma : {ident.get('platform', '')}",
            f"Icono      : {self.icon_bytes} bytes",
            f"Archivos   : {self.file_count}",
        ]
        return "\n".join(lines)


class IflappReader:
    """Lector de sólo cabecera para contenedores ``.iflapp``."""

    def __init__(self, path: Path | str):
        self.path = Path(path)
        if not self.path.is_file():
            raise IflappError(f"No existe el archivo: {self.path}")

    @property
    def format(self) -> str:
        return sniff_format(self.path)

    def header(self, include_blobs: bool = True) -> IflappHeader:
        """Cabecera con icono y ``details.xml`` (sin tocar el payload)."""
        return read_iflapp_header(self.path, include_blobs=include_blobs)

    def info(self) -> IflappInfo:
        fmt = self.format
        header = read_iflapp_header(self.path)
        return IflappInfo(
            path=str(self.path),
            format="iflapp2" if fmt == "iflapp2" else fmt,
            format_version=header.format_version,
            compression=header.compression,
            encryption=header.encryption,
            file_count=header.file_count,
            icon_bytes=len(header.icon),
            identity=header.identity(),
            manifest=header.manifest,
        )

    def icon_bytes(self) -> bytes:
        return self.header().icon

    def details_xml(self) -> str:
        return self.header().details_text()

    def manifest(self) -> List[Dict]:
        return list_iflapp(self.path)

    def verify(self, signing_key: bytes = DEFAULT_SIGNING_KEY) -> Dict:
        """Verifica estructura y firma del contenedor (sin extraerlo)."""
        return verify_iflapp(self.path, signing_key=signing_key)

    def export_assets(self, out_dir: Path | str) -> Dict[str, Optional[str]]:
        """Exporta icono y detalles leídos de la cabecera a *out_dir*."""
        return export_header_assets(self.path, out_dir)

    def read_icon_png(self) -> Optional[bytes]:
        """Devuelve el icono convertido a PNG si Pillow está disponible.

        El icono se lee de la cabecera; la conversión es local y no requiere
        descomprimir el paquete.
        """
        raw = self.icon_bytes()
        if not raw:
            return None
        try:
            import io

            from PIL import Image

            with Image.open(io.BytesIO(raw)) as image:
                buffer = io.BytesIO()
                image.convert("RGBA").save(buffer, format="PNG")
                return buffer.getvalue()
        except Exception:
            return None
