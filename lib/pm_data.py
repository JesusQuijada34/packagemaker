# -*- coding: utf-8 -*-
"""
Persistencia de configuración de PackageMaker en data/pm.data (JSON).
Separa valores editables por el usuario y metadatos de solo lectura (build/compilado).
"""

from __future__ import annotations

import json
import os
import sys
import uuid
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Optional

# Personalización visual bloqueada en ejecutable compilado (definir antes del build)
COMPILED_LOCKED_USER_KEYS = frozenset({
    "custom_accent_color",
    "blur_intensity",
    "window_radius",
    "sidebar_accent_width",
    "card_opacity",
    "ui_density",
})

# Cambios que requieren reiniciar la aplicación
RESTART_REQUIRED_KEYS = frozenset({
    "dpi_scale",
})

DEFAULT_USER: Dict[str, Any] = {
    "language": "es",
    "auto_translate": True,
    "base_dir": "",
    "fluthin_apps": "",
    "display_mode": "GhostBlur (Cristal)",
    "touch_mode": False,
    "dpi_scale": 1.0,
    "applied_dpi_scale": 1.0,
    "device_simulation": "laptop",
    "interface_color": "#0d1117",
    "auto_color": True,
    "notifications_enabled": False,
    "default_editor": "",
    "custom_accent_color": "#ff5722",
    "blur_intensity": 14,
    "window_radius": 12,
    "sidebar_accent_width": 3,
    "card_opacity": 0.08,
    "ui_density": "normal",
}

_store: Optional["PMDataStore"] = None


def _app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def _data_dir() -> Path:
    d = _app_root() / "data"
    d.mkdir(parents=True, exist_ok=True)
    return d


def pm_data_path() -> Path:
    return _data_dir() / "pm.data"


def is_compiled_build() -> bool:
    return bool(getattr(sys, "frozen", False))


class PMDataStore:
    """Lectura/escritura de data/pm.data."""

    SCHEMA_VERSION = 1

    def __init__(self, path: Optional[Path] = None):
        self.path = path or pm_data_path()
        self._data: Dict[str, Any] = {}
        self.load()

    def load(self) -> Dict[str, Any]:
        if self.path.is_file():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._data = {}
        else:
            self._data = {}
        self._ensure_structure()
        self._refresh_readonly()
        return self._data

    def _ensure_structure(self) -> None:
        if "schema_version" not in self._data:
            self._data["schema_version"] = self.SCHEMA_VERSION
        self._data.setdefault("user", {})
        self._data.setdefault("readonly", {})
        self._data.setdefault("translation_cache", {})
        user = self._data["user"]
        for key, val in DEFAULT_USER.items():
            if key not in user:
                user[key] = deepcopy(val)

    def _refresh_readonly(self) -> None:
        root = _app_root()
        ro = self._data["readonly"]
        ro["is_compiled"] = is_compiled_build()
        ro["app_version"] = self._detect_app_version()
        ro["executable_path"] = str(Path(sys.executable).resolve())
        ro["platform_os"] = sys.platform
        ro["python_version"] = sys.version.split()[0]
        ro["data_file"] = str(self.path.resolve())
        ro["app_root"] = str(root)
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            ro["bundle_path"] = str(sys._MEIPASS)
        else:
            ro["bundle_path"] = ""
        if "install_id" not in ro or not ro["install_id"]:
            ro["install_id"] = str(uuid.uuid4())

    def _detect_app_version(self) -> str:
        details = _app_root() / "details.xml"
        if details.is_file():
            try:
                import xml.etree.ElementTree as ET
                root = ET.parse(details).getroot()
                v = (root.findtext("version") or "").strip()
                if v.startswith("v"):
                    v = v[1:]
                if v:
                    return v
            except Exception:
                pass
        return "0.0.0"

    def save(self) -> bool:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._refresh_readonly()
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
            return True
        except OSError:
            return False

    def get_user(self, key: str, default: Any = None) -> Any:
        return self._data.get("user", {}).get(key, default)

    def set_user(self, key: str, value: Any) -> None:
        self._data.setdefault("user", {})[key] = value

    def remove_user(self, key: str) -> None:
        """Elimina una clave de la configuración del usuario."""
        if "user" in self._data and key in self._data["user"]:
            del self._data["user"][key]

    def get_readonly(self) -> Dict[str, Any]:
        self._refresh_readonly()
        return dict(self._data.get("readonly", {}))

    def is_key_editable(self, key: str) -> bool:
        if key in COMPILED_LOCKED_USER_KEYS and is_compiled_build():
            return False
        return True

    def get_translation_cache(self, lang: str) -> Dict[str, str]:
        return dict(self._data.get("translation_cache", {}).get(lang, {}))

    def set_translation_cache_entry(self, lang: str, key: str, text: str) -> None:
        tc = self._data.setdefault("translation_cache", {})
        lang_map = tc.setdefault(lang, {})
        lang_map[key] = text

    def merge_translation_cache(self, lang: str, entries: Dict[str, str]) -> None:
        tc = self._data.setdefault("translation_cache", {})
        tc.setdefault(lang, {}).update(entries)

    def migrate_from_legacy_config(self, legacy: Dict[str, Any]) -> None:
        """Importa config/settings.json antiguo una sola vez."""
        mapping = {
            "BASE_DIR": "base_dir",
            "Fluthin_APPS": "fluthin_apps",
            "DISPLAY_MODE": "display_mode",
            "LANGUAGE": "language",
            "device_simulation": "device_simulation",
            "dpi_scale": "dpi_scale",
            "touch_mode": "touch_mode",
            "interface_color": "interface_color",
            "auto_color": "auto_color",
            "auto_translate": "auto_translate",
        }
        for old, new in mapping.items():
            if old in legacy and legacy[old] is not None:
                self.set_user(new, legacy[old])
        if legacy.get("LANGUAGE"):
            self.set_user("language", str(legacy["LANGUAGE"]).lower()[:2])

    def to_legacy_app_config(self) -> Dict[str, Any]:
        """Compatibilidad con código que espera BASE_DIR en mayúsculas."""
        u = self._data.get("user", {})
        return {
            "BASE_DIR": u.get("base_dir", ""),
            "Fluthin_APPS": u.get("fluthin_apps", ""),
            "DISPLAY_MODE": u.get("display_mode", DEFAULT_USER["display_mode"]),
            "LANGUAGE": u.get("language", "es"),
            "device_simulation": u.get("device_simulation", "laptop"),
            "dpi_scale": u.get("dpi_scale", 1.0),
            "touch_mode": u.get("touch_mode", False),
            "interface_color": u.get("interface_color", "#0d1117"),
            "auto_color": u.get("auto_color", True),
            "auto_translate": u.get("auto_translate", True),
            "notifications_enabled": u.get("notifications_enabled", False),
            "custom_accent_color": u.get("custom_accent_color", "#ff5722"),
            "blur_intensity": u.get("blur_intensity", 14),
            "window_radius": u.get("window_radius", 12),
            "sidebar_accent_width": u.get("sidebar_accent_width", 3),
            "card_opacity": u.get("card_opacity", 0.08),
            "ui_density": u.get("ui_density", "normal"),
            "applied_dpi_scale": u.get("applied_dpi_scale", 1.0),
        }


def get_pm_data() -> PMDataStore:
    global _store
    if _store is None:
        _store = PMDataStore()
    return _store


def load_merged_app_config(
    legacy_config_path: Optional[Path] = None,
    default_base_dir: str = "",
    default_fluthin: str = "",
) -> Dict[str, Any]:
    """Carga pm.data y migra settings.json si hace falta."""
    store = get_pm_data()
    u = store._data.get("user", {})
    if not u.get("base_dir") and default_base_dir:
        store.set_user("base_dir", default_base_dir)
    if not u.get("fluthin_apps") and default_fluthin:
        store.set_user("fluthin_apps", default_fluthin)

    legacy_path = legacy_config_path or (_app_root() / "config" / "settings.json")
    if legacy_path.is_file():
        try:
            with open(legacy_path, "r", encoding="utf-8") as f:
                legacy = json.load(f)
            store.migrate_from_legacy_config(legacy)
            store.save()
        except (json.JSONDecodeError, OSError):
            pass

    store.save()
    return store.to_legacy_app_config()
