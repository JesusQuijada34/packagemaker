"""Configuración compartida de la suite.

Conserva una referencia viva a la ``QApplication`` durante toda la sesión. Sin
ella, un test que la crea en una variable local (patrón ``QApplication([])`` en
un ``unittest.TestCase``) la deja recolectar y Qt queda en un estado en el que
las animaciones de los tests siguientes ya no avanzan; el resultado depende del
orden de recolección. La app se crea de forma perezosa para no forzar PyQt6 en
los tests que no lo necesitan.
"""

import pytest

_APP = None


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
