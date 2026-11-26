# -*- coding: utf-8 -*-
"""Higiene de los catálogos de idioma (R-4c1a9e72).

Los catálogos tuvieron entradas planas sobrantes (``"report.auto_send"`` dentro
del objeto ``report``, ``"form.author_placeholder"`` dentro de ``create``) que
al aplanarse colisionaban con claves reales o creaban claves inexistentes.
Dos consecuencias visibles:

- la casilla de envío automático de la página de Reportes se quedaba en inglés
  al cambiar de idioma, porque el texto inglés ganaba el índice inverso bajo una
  clave sobrante que el catálogo destino devolvía igual;
- el marcador del campo Autor se resolvía por una clave plana en lugar de la
  anidada.

Estos tests fijan la invariante de los datos y la del índice inverso.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

LANG_DIR = ROOT / "lang"


def _flatten(data, prefix=""):
    out = {}
    for key, value in data.items():
        if isinstance(value, dict):
            out.update(_flatten(value, prefix + key + "."))
        elif isinstance(value, str):
            out[prefix + key] = value
    return out


def _catalogs():
    return {
        path.stem: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(LANG_DIR.glob("*.json"))
    }


def _raw_keys(node, prefix=""):
    """Claves tal como están escritas, incluidas las que llevan punto."""
    for key, value in node.items():
        yield prefix, key
        if isinstance(value, dict):
            yield from _raw_keys(value, prefix + key + ".")


def test_no_catalog_has_flat_keys_with_dots():
    offenders = {}
    for name, data in _catalogs().items():
        bad = [f"{prefix}{key}" for prefix, key in _raw_keys(data) if "." in key]
        if bad:
            offenders[name] = bad
    assert offenders == {}, f"claves planas sobrantes en los catálogos: {offenders}"


def test_every_catalog_defines_the_spanish_keys():
    catalogs = _catalogs()
    canonical = set(_flatten(catalogs["es"]))
    missing = {
        name: sorted(canonical - set(_flatten(data)))
        for name, data in catalogs.items()
        if canonical - set(_flatten(data))
    }
    assert missing == {}, f"claves sin traducir en algún catálogo: {missing}"


def test_author_placeholder_is_translated_in_every_language():
    catalogs = _catalogs()
    spanish = _flatten(catalogs["es"])["create.form.author_placeholder"]
    stuck = {
        name: flat["create.form.author_placeholder"]
        for name, data in catalogs.items()
        if name != "es"
        for flat in [_flatten(data)]
        if flat["create.form.author_placeholder"] == spanish
    }
    assert stuck == {}, f"el marcador de Autor sigue en español: {stuck}"


def test_reverse_index_only_returns_canonical_keys():
    from lib import live_i18n

    live_i18n.invalidate_cache()
    canonical = set(_flatten(_catalogs()["es"]))
    index = live_i18n.reverse_index()
    assert index, "el índice inverso está vacío"
    stray = {text: key for text, key in index.items() if key not in canonical}
    assert stray == {}, f"el índice devuelve claves inexistentes: {stray}"


def test_english_auto_send_text_retranslates_to_each_language():
    from lib import live_i18n

    catalogs = {name: _flatten(data) for name, data in _catalogs().items()}
    english = catalogs["en"]["report.auto_send"]
    live_i18n.invalidate_cache()

    assert live_i18n.key_for(english) == "report.auto_send"
    for name in ("de", "fr", "ja", "zh"):
        translated = catalogs[name]["report.auto_send"]
        assert translated != english, f"{name} no traduce el envío automático"
        key = live_i18n.key_for(translated)
        assert key == "report.auto_send", f"{name}: {translated!r} -> {key}"
