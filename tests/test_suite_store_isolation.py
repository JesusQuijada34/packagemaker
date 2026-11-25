# -*- coding: utf-8 -*-
"""La suite no escribe en el ``data/pm.data`` real del usuario.

Varios tests construyen la GUI real y guardan ajustes. Sin un almacén aislado,
``base_dir`` quedaba apuntando a la carpeta temporal de pytest y el CLI creaba
los proyectos dentro de ``/tmp`` después de ejecutar las pruebas.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib import pm_data  # noqa: E402


def test_session_store_is_not_the_real_data_file():
    store = pm_data.get_pm_data()
    real = (pm_data._app_root() / "data" / "pm.data").resolve()
    assert Path(store.path).resolve() != real


def test_session_base_dir_lives_in_the_test_sandbox():
    base_dir = pm_data.get_pm_data().get_user("base_dir")
    assert "packagemaker-tests-" in str(base_dir)
    assert str(base_dir) != str(pm_data.DEFAULT_USER["base_dir"])


def test_saving_the_session_store_does_not_touch_the_real_file():
    real = pm_data._app_root() / "data" / "pm.data"
    before = real.stat().st_mtime_ns if real.is_file() else None

    store = pm_data.get_pm_data()
    store.set_user("sidebar_width", 300)
    assert store.save()

    after = real.stat().st_mtime_ns if real.is_file() else None
    assert after == before
