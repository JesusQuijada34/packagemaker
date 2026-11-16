#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Prueba del diálogo "Abrir con" (indicador de selección y animaciones).

Antes era un script de demostración que llamaba a ``app.exec()``: bajo pytest
eso bloqueaba el proceso para siempre. Ahora construye el diálogo, comprueba lo
básico y lo cierra sin entrar en el bucle de eventos.
"""

import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

pytest.importorskip("PyQt6.QtWidgets")


@pytest.fixture(scope="module")
def qapp():
    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app
    app.processEvents()


def test_dialog_constructs_with_project_metadata(qapp):
    from lib.openWithDialog import OpenWithDialog

    dialog = OpenWithDialog(
        parent=None,
        project_path="/tmp/test-project",
        project_name="Test Project",
    )
    try:
        dialog.show()
        qapp.processEvents()
        assert dialog.windowTitle()
    finally:
        dialog.close()
        qapp.processEvents()


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
