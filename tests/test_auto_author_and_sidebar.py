# -*- coding: utf-8 -*-
"""Regresiones de la Fase 1 de bugs.txt: sidebar sin IDE y autor automático.

Cubre, con código real:

- el sidebar ya no ofrece la pestaña "IDE de Proyectos" (pmCodeEditor la cubre);
- el campo Autor de la creación se sincroniza con el username de GitHub de la
  sesión y no admite escritura manual.
"""

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="module")
def qapp():
    qt = pytest.importorskip("PyQt6.QtWidgets")
    app = qt.QApplication.instance() or qt.QApplication([])
    yield app
    app.processEvents()


@pytest.fixture
def isolated_store(tmp_path, monkeypatch):
    """Aísla pm_data para no tocar la sesión real de GitHub."""
    from lib import pm_data

    monkeypatch.setattr(pm_data, "_data_dir", lambda: tmp_path)
    store = pm_data.PMDataStore(path=tmp_path / "pm.data")
    monkeypatch.setattr(pm_data, "_store", store)
    return store


def test_sidebar_has_no_ide_page(qapp):
    import packagemaker as pm

    win = pm.PackageTodoGUI()
    try:
        assert not hasattr(win, "btn_ide")
        assert not hasattr(win, "page_ide")
        assert not hasattr(win, "init_ide_tab")
        # El grupo sigue teniendo una sola pestaña "Acerca de" al final.
        assert win.sidebar_group.button(4).text() == pm.tr("sidebar.about")
        assert win.sidebar_group.button(5) is None
    finally:
        win.close()
        qapp.processEvents()


def test_author_field_is_readonly_and_follows_session(qapp, isolated_store):
    import packagemaker as pm
    from lib import github_identity

    win = pm.PackageTodoGUI()
    try:
        # Sin sesión: campo vacío y bloqueado.
        assert win.input_autor.isReadOnly()
        assert not win.input_autor.isEnabled()
        assert win.input_autor.text() == ""

        # Con sesión: el autor es el login autenticado, sin escritura manual.
        github_identity.save_profile(
            github_identity.GitHubProfile(login="JesusQuijada34")
        )
        win._refresh_author_field()
        assert win.input_autor.text() == "JesusQuijada34"

        # Al cerrar sesión vuelve a quedar vacío.
        github_identity.clear_identity()
        win._refresh_author_field()
        assert win.input_autor.text() == ""
    finally:
        win.close()
        qapp.processEvents()
