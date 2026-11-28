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
import os
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
def _no_isolated_builds():
    """Desactiva el entorno aislado de build durante la suite.

    Los tests que compilan de verdad deben usar el backend embebido: crear un
    venv por proyecto e instalar dependencias haría la suite lenta y dependiente
    de la red. El aislamiento tiene sus propias pruebas en
    ``tests/test_build_sandbox.py``.
    """
    from lib.blindcubeEngine import build_sandbox

    previous = os.environ.get(build_sandbox.DISABLE_ENV)
    os.environ[build_sandbox.DISABLE_ENV] = "0"
    yield
    if previous is None:
        os.environ.pop(build_sandbox.DISABLE_ENV, None)
    else:
        os.environ[build_sandbox.DISABLE_ENV] = previous


@pytest.fixture(scope="session", autouse=True)
def _no_patch_watch():
    """Desactiva la vigilancia de parches durante la suite.

    La ventana real se construye decenas de veces en los tests; sin este
    interruptor cada construcción lanzaría un ``GET`` a ``api.github.com``.
    La vigilancia tiene sus propias pruebas en ``tests/test_patch_watch.py``.
    """
    from lib import patch_watch

    previous = os.environ.get(patch_watch.DISABLE_ENV)
    os.environ[patch_watch.DISABLE_ENV] = "0"
    yield
    if previous is None:
        os.environ.pop(patch_watch.DISABLE_ENV, None)
    else:
        os.environ[patch_watch.DISABLE_ENV] = previous


@pytest.fixture(scope="session", autouse=True)
def _no_single_instance_guard():
    """Desactiva la instancia única durante la suite.

    Varios tests arrancan la aplicación de verdad por subproceso; sin este
    interruptor un arranque anterior todavía vivo rechazaría al siguiente. La
    guarda tiene sus propias pruebas en ``tests/test_single_instance.py``.
    """
    from lib import single_instance

    previous = os.environ.get(single_instance.DISABLE_ENV)
    os.environ[single_instance.DISABLE_ENV] = "0"
    yield
    if previous is None:
        os.environ.pop(single_instance.DISABLE_ENV, None)
    else:
        os.environ[single_instance.DISABLE_ENV] = previous


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
