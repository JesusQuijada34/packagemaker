# -*- coding: utf-8 -*-
"""Lectura de fuentes Python respetando la codificación declarada (PEP 263).

Python acepta fuentes que no están en UTF-8 siempre que la primera o la segunda
línea declaren la codificación (``# -*- coding: cp1252 -*-``). El motor leía
siempre con ``encoding="utf-8"``, así que un proyecto guardado por un editor de
Windows en ANSI lanzaba ``UnicodeDecodeError`` desde un slot de Qt (PyQt6
aborta el proceso) o desde el CLI (traceback).

Aquí se detecta la codificación como lo hace el propio intérprete y se conserva
al reescribir el archivo, de modo que la declaración siga siendo válida.
"""
from __future__ import annotations

import io
import tokenize
from pathlib import Path
from typing import Tuple


class SourceEncodingError(Exception):
    """El archivo no se puede decodificar como fuente Python válida."""


def read_python_source(path: Path | str) -> Tuple[str, str]:
    """Devuelve ``(texto, codificación)`` del fuente.

    Lanza :class:`SourceEncodingError` si la codificación declarada no existe o
    si el contenido no se puede decodificar con ella; ``OSError`` se propaga
    para que el llamador decida.
    """
    data = Path(path).read_bytes()
    try:
        encoding, _ = tokenize.detect_encoding(io.BytesIO(data).readline)
    except SyntaxError as exc:
        raise SourceEncodingError(f"declaración de codificación inválida: {exc}") from exc
    try:
        return data.decode(encoding), encoding
    except (UnicodeDecodeError, LookupError) as exc:
        raise SourceEncodingError(f"no se pudo decodificar como {encoding}: {exc}") from exc


__all__ = ["SourceEncodingError", "read_python_source"]
