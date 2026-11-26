# -*- coding: utf-8 -*-
"""Retraducción en vivo de la interfaz.

Las páginas se construyen una sola vez con ``tr()``, así que cambiar de idioma
sólo retraducía los pocos widgets que ``apply_ui_language()`` conocía. En vez
de reconstruir las páginas —lo que borraría lo que el usuario lleva escrito en
los formularios— este módulo resuelve el texto visible de cada widget a su
clave y lo vuelve a traducir en el idioma activo.

La resolución es por valor: se indexan las traducciones de *todos* los idiomas,
de modo que da igual si el texto está en español, inglés o japonés; siempre se
encuentra la clave. Los textos que no son una traducción (rutas, versiones,
números, nombres propios) no están en el índice y se dejan intactos.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple

_INDEX_CACHE: Optional[Dict[str, str]] = None
_TEMPLATE_CACHE: Optional[List[Tuple["re.Pattern[str]", str]]] = None


def _lang_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "lang"


def _flatten(data, prefix: str = "") -> Iterator[Tuple[str, str]]:
    for key, value in data.items():
        full = f"{prefix}{key}"
        if isinstance(value, dict):
            yield from _flatten(value, full + ".")
        elif isinstance(value, str):
            yield full, value


def _canonical_keys() -> Optional[set]:
    """Claves del catálogo español, que es la lista canónica de claves.

    Sólo se indexan textos de claves que existen aquí: una clave sobrante en
    otro catálogo (p. ej. una entrada plana ``report.auto_send`` dentro del
    objeto ``report``) no debe ganar el índice por valor y devolver una clave
    que el catálogo activo resuelve al texto del idioma equivocado.
    """
    try:
        data = json.loads((_lang_dir() / "es.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    data.pop("_meta", None)
    return {key for key, _text in _flatten(data)}


def reverse_index() -> Dict[str, str]:
    """Mapa ``texto traducido`` -> ``clave`` para todos los idiomas.

    Cuando dos claves comparten el mismo texto gana la primera por orden
    alfabético de fichero, que es determinista y basta: el resultado visible es
    el mismo para ambas.
    """
    global _INDEX_CACHE
    if _INDEX_CACHE is not None:
        return _INDEX_CACHE

    canonical = _canonical_keys()
    index: Dict[str, str] = {}
    for path in sorted(_lang_dir().glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        data.pop("_meta", None)
        for key, text in _flatten(data):
            if canonical is not None and key not in canonical:
                continue
            if not text.strip():
                continue
            index.setdefault(text, key)
            # Los textos con salto de línea se comparan también sin él: Qt
            # devuelve el texto tal cual, pero algunos builders lo recortan.
            collapsed = " ".join(text.split())
            if collapsed != text:
                index.setdefault(collapsed, key)
    _INDEX_CACHE = index
    return index


def invalidate_cache() -> None:
    global _INDEX_CACHE, _TEMPLATE_CACHE
    _INDEX_CACHE = None
    _TEMPLATE_CACHE = None


_PLACEHOLDER = re.compile(r"\{[A-Za-z_][A-Za-z0-9_]*\}")


def template_index() -> List[Tuple["re.Pattern[str]", str]]:
    """Plantillas de traducción (``Versión {version}``) listas para comparar.

    Los textos construidos con ``tr(...).format(...)`` no aparecen tal cual en
    los ficheros de idioma, así que se indexan como expresión regular.
    """
    global _TEMPLATE_CACHE
    if _TEMPLATE_CACHE is not None:
        return _TEMPLATE_CACHE

    entries: List[Tuple[re.Pattern[str], str]] = []
    seen = set()
    canonical = _canonical_keys()
    for path in sorted(_lang_dir().glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        data.pop("_meta", None)
        for key, text in _flatten(data):
            if canonical is not None and key not in canonical:
                continue
            if not _PLACEHOLDER.search(text) or (key, text) in seen:
                continue
            seen.add((key, text))
            pattern = "".join(
                ".+?" if _PLACEHOLDER.fullmatch(part) else re.escape(part)
                for part in re.split(r"(\{[A-Za-z_][A-Za-z0-9_]*\})", text)
            )
            entries.append((re.compile(f"^{pattern}$", re.DOTALL), key))
    # Las plantillas más largas primero: "Versión {version}" antes que "{x}".
    entries.sort(key=lambda item: -len(item[0].pattern))
    _TEMPLATE_CACHE = entries
    return entries


def key_for(text: str) -> Optional[str]:
    """Clave de traducción cuyo valor es ``text``, si la hay."""
    if not text:
        return None
    index = reverse_index()
    found = index.get(text)
    if found is None:
        found = index.get(" ".join(text.split()))
    if found is not None:
        return found
    for pattern, key in template_index():
        if pattern.match(text):
            return key
    return None


def _real_attr(widget, name: str) -> bool:
    """¿``name`` existe de verdad en el widget?

    ``hasattr`` no sirve: clases como ``WipeWindow`` implementan ``__getattr__``
    para devolver un manejador que lanza ``AttributeError``, así que todo
    atributo "existe" hasta que se llama. Se exige que venga de la clase.
    """
    for klass in type(widget).__mro__:
        if name in vars(klass):
            return True
    return False


def _text_slots(widget) -> List[Tuple[str, object, object]]:
    """Propiedades de texto de un widget: ``(nombre, getter, setter)``.

    Se omiten los valores que escribe el usuario (``QLineEdit.text``,
    editores de texto) para no pisar nunca su contenido; de ellos sólo se
    retraduce el marcador de posición.
    """
    slots: List[Tuple[str, object, object]] = []

    if (
        _real_attr(widget, "text")
        and _real_attr(widget, "setText")
        and not _real_attr(widget, "toPlainText")
        and not _is_editable_field(widget)
    ):
        slots.append(("text", widget.text, widget.setText))

    if _real_attr(widget, "placeholderText") and _real_attr(widget, "setPlaceholderText"):
        slots.append(("placeholder", widget.placeholderText, widget.setPlaceholderText))

    if _real_attr(widget, "toolTip") and _real_attr(widget, "setToolTip"):
        slots.append(("tooltip", widget.toolTip, widget.setToolTip))

    return slots


def _is_editable_field(widget) -> bool:
    try:
        from PyQt6.QtWidgets import (
            QComboBox,
            QLineEdit,
            QPlainTextEdit,
            QTextEdit,
        )
    except ImportError:  # pragma: no cover - sin Qt no hay UI que traducir
        return False
    return isinstance(widget, (QLineEdit, QTextEdit, QPlainTextEdit, QComboBox))


def _combo_items(widget) -> List[Tuple[int, str]]:
    from PyQt6.QtWidgets import QComboBox

    if not isinstance(widget, QComboBox):
        return []
    return [(i, widget.itemText(i)) for i in range(widget.count())]


def _tab_items(widget) -> List[Tuple[int, str]]:
    from PyQt6.QtWidgets import QTabWidget

    if not isinstance(widget, QTabWidget):
        return []
    return [(i, widget.tabText(i)) for i in range(widget.count())]


def retranslate_widget(widget) -> int:
    """Retraduce un widget. Devuelve cuántos textos cambiaron."""
    from lib.i18n import tr

    changed = 0
    for _name, getter, setter in _text_slots(widget):
        try:
            current = getter()
        except (RuntimeError, AttributeError):
            return changed  # widget C++ destruido o atributo falso
        key = key_for(current)
        if key is None:
            continue
        target = tr(key)
        if target and target != current:
            setter(target)
            changed += 1

    from PyQt6.QtWidgets import QComboBox

    if isinstance(widget, QComboBox):
        for i, current in _combo_items(widget):
            key = key_for(current)
            if key is None:
                continue
            target = tr(key)
            if target and target != current:
                widget.setItemText(i, target)
                changed += 1

    for i, current in _tab_items(widget):
        key = key_for(current)
        if key is None:
            continue
        target = tr(key)
        if target and target != current:
            widget.setTabText(i, target)
            changed += 1

    return changed


def retranslate_tree(root) -> int:
    """Retraduce ``root`` y todos sus descendientes."""
    total = retranslate_widget(root)
    for child in root.findChildren(object):
        if not _real_attr(child, "metaObject"):
            continue
        try:
            total += retranslate_widget(child)
        except (RuntimeError, AttributeError):
            continue  # widget destruido a mitad del recorrido
    return total
