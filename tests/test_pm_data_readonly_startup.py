# -*- coding: utf-8 -*-
"""El arranque no debe caer si ``data/`` no se puede crear o leer (R-4d8a6c12).

``_data_dir()`` creaba la carpeta con ``mkdir`` sin protección: en una
instalación de solo lectura sin ``data/`` la primera llamada a ``get_pm_data()``
—que ocurre al resolver el acento o el idioma— abortaba el programa. Si la
carpeta existía pero era ilegible, ``PMDataStore.load()`` lanzaba
``PermissionError`` en ``Path.is_file()`` (Python 3.13).
"""
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from lib import pm_data

_UNREADABLE_SKIP = pytest.mark.skipif(
    os.name == "nt" or (hasattr(os, "geteuid") and os.geteuid() == 0),
    reason="los permisos POSIX no bloquean la escritura en Windows ni como root",
)


def _restore(path: Path, mode: int = 0o755) -> None:
    try:
        path.chmod(mode)
    except OSError:
        pass


@_UNREADABLE_SKIP
def test_data_dir_tolerates_readonly_app_root(tmp_path):
    app = tmp_path / "app"
    app.mkdir()
    app.chmod(0o555)
    try:
        with patch.object(pm_data, "_app_root", return_value=app):
            assert pm_data._data_dir() == app / "data"
            assert pm_data.pm_data_path() == app / "data" / "pm.data"
    finally:
        _restore(app)


@_UNREADABLE_SKIP
def test_store_loads_with_unreadable_data_dir(tmp_path):
    app = tmp_path / "app"
    app.mkdir()
    data = app / "data"
    data.mkdir()
    data.chmod(0o000)
    try:
        with patch.object(pm_data, "_app_root", return_value=app):
            store = pm_data.PMDataStore()
            assert store.get_user("language") == pm_data.DEFAULT_USER["language"]
            assert store.save() is False
    finally:
        _restore(data)


@_UNREADABLE_SKIP
def test_merged_config_tolerates_unreadable_legacy_dir(tmp_path):
    app = tmp_path / "app"
    app.mkdir()
    legacy_dir = app / "config"
    legacy_dir.mkdir()
    legacy_dir.chmod(0o000)
    try:
        with patch.object(pm_data, "_app_root", return_value=app), patch.object(
            pm_data, "_store", pm_data.PMDataStore(tmp_path / "pm.data")
        ):
            merged = pm_data.load_merged_app_config()
        assert isinstance(merged, dict)
    finally:
        _restore(legacy_dir)


def test_default_store_still_round_trips(tmp_path):
    path = tmp_path / "pm.data"
    store = pm_data.PMDataStore(path)
    store.set_user("language", "en")
    assert store.save() is True
    assert pm_data.PMDataStore(path).get_user("language") == "en"
