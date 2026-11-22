# -*- coding: utf-8 -*-
"""Regresión de i18n (Fase 2.3 de ``bugs.txt``).

Los diccionarios de idioma ya no pueden quedar a medias: toda clave que usa
``tr()`` debe tener una traducción propia (distinta del inglés) en cada idioma
no inglés, y todos los ficheros deben compartir el mismo conjunto de claves.
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANG_DIR = ROOT / "lang"

# Nombres propios, marcas y cadenas que son idénticas en inglés por diseño.
_IDENTICAL_BY_DESIGN = {
    "common.ok",
    "app.title",
    "about.version",
    "build.button",
    "common.version",
    "create.form.placeholder_version",
    "create.platform.linux",
    "create.platform.windows",
    "dashboard.platform_linux",
    "dashboard.platform_windows",
    "moonfix.title",
    "sidebar.moonfix",
    "config.notifications",
    "build.version",
    "dialog.project_version",
    "interpreter.version_label",
    "dashboard.name",
    "config.density_normal",
    "iflapp_ide.backend",
    "common.no",
    "iflapp_ide.debug",
    "app.context",
    "config.density_compact",
    "dashboard.platform",
    "editor.project_header",
    "window.close",
    "window.maximize",
    "window.minimize",
    "window.restore",
    "common.close",
    "common.version",
    "common.error",
    "common.warning",
    "common.yes",
    "common.no",
    "common.select_folder",
    # Palabras idénticas en estos idiomas (File/Project/Folder/Backend).
    "dialog.file_info",
    "dialog.project_info",
    "dialog.folder_info",
    "editor.project_header_value",
    # Etiquetas de la TUI que son la misma palabra en varios idiomas
    # (Action/Option/Mode/Version/App) o nombres de plataforma canónicos.
    "tui.action",
    "tui.actions",
    "tui.app_col",
    "tui.mode",
    "tui.mode_col",
    "tui.option",
    "tui.platform_col",
    "tui.platform_linux",
    "tui.platform_windows",
    "tui.version_col",
    "tui.help_title",
    # "Framework" se escribe igual en varios idiomas de destino.
    "about.framework",
    # Cognados reales (Version/System/Name/Project/No) y el nombre del
    # intérprete, que no se traduce.
    "tui.about_python",
    "tui.about_version",
    "tui.about_system",
    "tui.name_col",
    "tui.project_col",
    "tui.project_header",
    "tui.no",
}

_NON_ENGLISH = ["fr", "de", "it", "pt", "nl", "pl", "tr", "ru", "ja", "ko", "zh", "ar"]


def _flatten(data, prefix=""):
    flat = {}
    for key, value in data.items():
        if key.startswith("_"):
            continue
        full = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            flat.update(_flatten(value, full))
        else:
            flat[full] = value
    return flat


def _load(code):
    return _flatten(json.loads((LANG_DIR / f"{code}.json").read_text(encoding="utf-8")))


def _used_keys():
    used = set()
    for path in list(ROOT.glob("*.py")) + list(ROOT.glob("lib/*.py")):
        text = path.read_text(encoding="utf-8")
        # Ambas comillas: media interfaz llama tr('clave') y el regex anterior
        # sólo veía las de comilla doble, dejando pasar claves sin traducir.
        used.update(re.findall(r"""tr\(\s*["']([^"']+)["']""", text))
    # Claves que se resuelven por índice (descripciones del sidebar).
    used.update({f"sidebar_desc.{index}" for index in (0, 1, 3, 4, 5)})
    return used


class CuratedTranslationTests(unittest.TestCase):
    def test_every_used_key_has_a_real_translation(self):
        en = _load("en")
        used = _used_keys()
        offenders = {}
        for code in _NON_ENGLISH:
            catalog = _load(code)
            untranslated = sorted(
                key
                for key in used
                if key in catalog
                and key in en
                and catalog[key] == en[key]
                and key not in _IDENTICAL_BY_DESIGN
            )
            if untranslated:
                offenders[code] = untranslated
        self.assertEqual(offenders, {}, f"claves sin traducir: {offenders}")

    def test_all_language_files_share_the_same_keys(self):
        base = set(_load("es"))
        for code in _NON_ENGLISH:
            keys = set(_load(code))
            self.assertFalse(base - keys, f"{code}.json carece de claves: {sorted(base - keys)}")

    def test_curated_module_covers_the_regression(self):
        from tools.translations_curated import CURATED

        for code in _NON_ENGLISH:
            self.assertIn(code, CURATED, f"falta el idioma {code} en CURATED")
            self.assertGreater(len(CURATED[code]), 100, f"{code} tiene muy pocas curadas")

    def test_curated_alone_translates_the_dashboard_error(self):
        """Generar desde cero (sin reinyectar el JSON) debe dar la traducción.

        El generador mezcla el ``lang/<code>.json`` existente, así que una clave
        puesta sólo en el JSON sobrevive a la regeneración. Pero un checkout
        limpio o un fichero borrado parten de es+en+``TRANSLATIONS``+``CURATED``;
        si la traducción sólo vive en el JSON, ahí se pierde y cae al inglés.
        """
        from tools import generate_lang_files as gen
        from tools.translations_curated import CURATED

        source = json.loads((LANG_DIR / "es.json").read_text(encoding="utf-8"))
        fallback = json.loads((LANG_DIR / "en.json").read_text(encoding="utf-8"))
        english = _load("en")["dashboard.create_failed"]

        for code in _NON_ENGLISH:
            merged = gen._deep_merge(source, fallback)
            merged = gen._deep_merge(merged, gen.TRANSLATIONS[code])
            merged = gen._deep_merge(merged, gen._nest(CURATED.get(code, {})))
            translated = merged["dashboard"]["create_failed"]
            self.assertNotEqual(
                translated,
                english,
                f"{code} caería al inglés sin el JSON previo: añade "
                f"dashboard.create_failed a CURATED[{code!r}]",
            )


if __name__ == "__main__":
    unittest.main()
