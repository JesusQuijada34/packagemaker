# -*- coding: utf-8 -*-
"""
Internacionalización para PackageMaker.
- Traducciones por clave en lang/<código>.json
- Caché y traducción automática en data/pm.data
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional

from PyQt6.QtCore import QCoreApplication, QLocale, QTranslator

SUPPORTED_LANGUAGES = {
    "es": "Español",
    "en": "English",
    "pt": "Português",
    "fr": "Français",
    "de": "Deutsch",
    "it": "Italiano",
    "ru": "Русский",
    "zh": "中文",
    "ja": "日本語",
}

_translation_cache: Dict[str, Dict[str, str]] = {}
_ui_refresh_callbacks = []


def _app_root() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _get_lang_dir() -> str:
    return os.path.join(_app_root(), "lang")


def _load_lang_file(lang_code: str) -> Dict[str, Any]:
    if lang_code in _translation_cache:
        return _translation_cache[lang_code]
    lang_dir = _get_lang_dir()
    file_path = os.path.join(lang_dir, f"{lang_code}.json")
    data: Dict[str, Any] = {}
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
    except Exception as e:
        print(f"[i18n] Error cargando {file_path}: {e}")
    _translation_cache[lang_code] = data
    return data


def _flatten_translations(data: Dict[str, Any], prefix: str = "") -> Dict[str, str]:
    result: Dict[str, str] = {}
    for key, value in data.items():
        if key.startswith("_"):
            continue
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            result.update(_flatten_translations(value, full_key))
        else:
            result[full_key] = str(value)
    return result


def _auto_translate_google(text: str, source: str, target: str) -> Optional[str]:
    if not text or source == target:
        return text
    q = urllib.parse.quote(text)
    url = (
        "https://translate.googleapis.com/translate_a/single"
        f"?client=gtx&sl={source}&tl={target}&dt=t&q={q}"
    )
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "PackageMaker/1.0"},
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        if payload and payload[0]:
            parts = [p[0] for p in payload[0] if p[0]]
            return "".join(parts) if parts else None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, IndexError, KeyError):
        return None
    return None


class I18nManager:
    _instance: Optional["I18nManager"] = None
    _translator: Optional[QTranslator] = None
    _current_lang: str = "es"
    _app: Optional[QCoreApplication] = None
    _auto_translate: bool = True
    _flat_es: Dict[str, str] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, app: QCoreApplication, lang: str = "es", auto_translate: bool = True):
        self._app = app
        self._auto_translate = auto_translate
        self._flat_es = _flatten_translations(_load_lang_file("es"))
        self.load_translation(lang)

    def set_auto_translate(self, enabled: bool) -> None:
        self._auto_translate = enabled

    def load_translation(self, lang: str) -> bool:
        if not self._app:
            return False
        lang = (lang or "es").lower()[:2]
        if self._translator:
            self._app.removeTranslator(self._translator)
            self._translator = None
        self._current_lang = lang
        _load_lang_file(lang)
        if lang == "es":
            self._notify_ui_refresh()
            return True
        base_dir = _app_root()
        qm_path = os.path.join(base_dir, "translations", f"packagemaker_{lang}.qm")
        if os.path.exists(qm_path):
            self._translator = QTranslator()
            if self._translator.load(qm_path):
                self._app.installTranslator(self._translator)
        self._notify_ui_refresh()
        return True

    def _lookup_key(self, key: str) -> Optional[str]:
        lang_data = _load_lang_file(self._current_lang)
        flat = _flatten_translations(lang_data)
        if key in flat:
            return flat[key]
        if self._current_lang != "es":
            es_flat = _flatten_translations(_load_lang_file("es"))
            if key in es_flat:
                return es_flat[key]
        return None

    def _lookup_by_spanish_text(self, text: str) -> Optional[str]:
        for k, v in self._flat_es.items():
            if v == text:
                return self._lookup_key(k)
        flat = _flatten_translations(_load_lang_file(self._current_lang))
        return flat.get(text)

    def _cache_get(self, key: str) -> Optional[str]:
        try:
            from lib.pm_data import get_pm_data
            return get_pm_data().get_translation_cache(self._current_lang).get(key)
        except Exception:
            return None

    def _cache_set(self, key: str, value: str) -> None:
        try:
            from lib.pm_data import get_pm_data
            store = get_pm_data()
            store.set_translation_cache_entry(self._current_lang, key, value)
            store.save()
        except Exception:
            pass

    def translate(self, text: str, context: str = "@default") -> str:
        if not text:
            return text
        is_key = "." in text and not text.startswith(" ") and len(text) < 120

        if is_key:
            resolved = self._lookup_key(text)
            if resolved:
                return resolved
            source = self._flat_es.get(text, text)
        else:
            if self._current_lang == "es":
                return text
            source = text
            for k, v in self._flat_es.items():
                if v == text:
                    resolved = self._lookup_key(k)
                    if resolved:
                        return resolved
                    text = k
                    is_key = True
                    break

        if self._current_lang == "es":
            return source if is_key else text

        cache_key = text if is_key else f"__text__:{source}"
        cached = self._cache_get(cache_key)
        if cached:
            return cached

        by_text = self._lookup_by_spanish_text(source)
        if by_text:
            return by_text

        if self._translator and self._app:
            qt_t = self._app.translate(context, source)
            if qt_t != source:
                return qt_t

        if self._auto_translate:
            auto = _auto_translate_google(source, "es", self._current_lang)
            if auto:
                self._cache_set(cache_key, auto)
                return auto

        return source

    def get_current_lang(self) -> str:
        return self._current_lang

    def get_supported_languages(self) -> dict:
        return SUPPORTED_LANGUAGES.copy()

    def register_ui_refresh(self, callback) -> None:
        if callback not in _ui_refresh_callbacks:
            _ui_refresh_callbacks.append(callback)

    def _notify_ui_refresh(self) -> None:
        for cb in list(_ui_refresh_callbacks):
            try:
                cb()
            except Exception as e:
                print(f"[i18n] UI refresh error: {e}")


i18n = I18nManager()


def tr(text: str, context: str = "@default") -> str:
    return i18n.translate(text, context)


def get_available_languages() -> list:
    return [(code, name) for code, name in SUPPORTED_LANGUAGES.items()]


def system_default_language() -> str:
    loc = QLocale.system().name().lower()
    code = loc.split("_")[0] if loc else "es"
    return code if code in SUPPORTED_LANGUAGES else "es"
