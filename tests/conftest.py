"""Configuración compartida de la suite.

Conserva una referencia viva a la ``QApplication`` durante toda la sesión. Sin
ella, un test que la crea en una variable local (patrón ``QApplication([])`` en
un ``unittest.TestCase``) la deja recolectar y Qt queda en un estado en el que
las animaciones de los tests siguientes ya no avanzan; el resultado depende del
orden de recolección. La app se crea de forma perezosa para no forzar PyQt6 en
los tests que no lo necesitan.

También redirige ``data/pm.data`` a una carpeta temporal: varios tests
construyen la GUI real y guardan ajustes, y sin este límite el ``base_dir`` del
usuario terminaba apuntando a la carpeta temporal de pytest, así que el CLI
creaba los proyectos dentro de ``/tmp`` tras ejecutar la suite.
"""

import atexit
import shutil
import tempfile
from pathlib import Path

import pytest

_APP = None


def _install_isolated_store():
    """Sustituye el almacén global por uno dentro de una carpeta temporal."""
    try:
        from lib import pm_data
    except Exception:  # pragma: no cover - entorno sin el paquete lib
        return None
    root = Path(tempfile.mkdtemp(prefix="packagemaker-tests-"))
    atexit.register(lambda: shutil.rmtree(root, ignore_errors=True))
    store = pm_data.PMDataStore(root / "pm.data")
    store.set_user("base_dir", str(root / "proyectos"))
    store.set_user("fluthin_apps", str(root / "apps"))
    store.save()
    pm_data._store = store
    return store


_SESSION_STORE = _install_isolated_store()


@pytest.fixture(scope="session", autouse=True)
def _qt_app():
    global _APP
    try:
        from PyQt6.QtWidgets import QApplication
    except Exception:
        yield None
        return
    _APP = QApplication.instance() or QApplication([])
    yield _APP
