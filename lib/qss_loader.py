# -*- coding: utf-8 -*-
"""Carga de hojas QSS por control desde ``source/qss/{qtcontrolid}.qss``.

Cada control Qt tiene su propio fichero en ``source/qss`` y ahí vive **todo** su
estilo; el código Python no escribe reglas a mano. Los ficheros son plantillas:
llevan marcadores ``__NOMBRE__`` que :func:`render` sustituye por los valores de
``design_tokens`` (paleta, radios, tipografía y el acento del SO).

Un mismo control puede tener varias variantes; se separan con marcadores de
sección::

    /* @role: primary */
    QPushButton { ... }
    /* @role: secondary */
    QPushButton { ... }

``read_qss("qpushbutton", role="primary")`` devuelve sólo ese bloque.

Sin dependencias de PyQt6: sólo lee y devuelve cadenas.
"""

from __future__ import annotations

import re
from pathlib import Path

QSS_DIR = Path(__file__).resolve().parent.parent / "source" / "qss"

_ROLE_RE = re.compile(r"/\*\s*@role:\s*([\w-]+)\s*\*/")


def available_controls() -> list[str]:
    """Nombres de control con fichero QSS (sin extensión), ordenados."""
    if not QSS_DIR.is_dir():
        return []
    return sorted(path.stem for path in QSS_DIR.glob("*.qss"))


def read_qss_file(control: str, role: str | None = None) -> str:
    """Devuelve el QSS de *control* (y, si se indica, de su variante *role*).

    Si el fichero define variantes y no se pide ninguna, lanza ``ValueError``
    para no devolver una hoja con varias variantes mezcladas. Lanza
    ``FileNotFoundError`` si el control no tiene fichero, para que un nombre mal
    escrito falle pronto en vez de devolver un estilo vacío.
    """
    path = QSS_DIR / f"{control}.qss"
    if not path.is_file():
        raise FileNotFoundError(f"No hay QSS para el control '{control}': {path}")
    text = path.read_text(encoding="utf-8")
    if role is not None:
        return _extract_role(text, role)
    if _ROLE_RE.search(text):
        raise ValueError(f"'{control}' define variantes; indica un rol")
    return text.strip("\n")


def _extract_role(text: str, role: str) -> str:
    """Extrae el bloque de la variante *role* (hasta el siguiente marcador)."""
    matches = list(_ROLE_RE.finditer(text))
    for index, match in enumerate(matches):
        if match.group(1) != role:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        return text[start:end].strip("\n")
    raise KeyError(f"El control no define el rol '{role}'")


def render(template: str, values: dict | None = None) -> str:
    """Sustituye los marcadores ``__NOMBRE__`` de *template* por *values*.

    Se usa ``str.replace`` (no ``str.format``) porque las hojas contienen llaves
    CSS que ``format`` interpretaría como campos.
    """
    for token, value in (values or {}).items():
        template = template.replace(f"__{token}__", str(value))
    return template


def qss(control: str, role: str | None = None, **values) -> str:
    """Atajo: lee el QSS de *control*/*role* y resuelve sus marcadores."""
    return render(read_qss_file(control, role), values)
