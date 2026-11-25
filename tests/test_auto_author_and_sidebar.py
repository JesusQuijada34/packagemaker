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
        # El orden lo fija addons/*.yaml: las páginas de trabajo arriba,
        # herramientas después y "Acerca de" al final. No hay página de IDE.
        ids = [a.id for a in win._addons]
        assert ids == ["create", "build", "config", "moonfix", "report", "aide", "about"]
        assert win.sidebar_group.button(len(ids) - 1).text() == pm.tr("sidebar.about")
        assert win.sidebar_group.button(len(ids)) is None
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


def test_build_tab_forces_explicit_engine_choice(qapp):
    """La pestaña Compilar exige elegir FlatCube v1 o BlindCube v2."""
    import packagemaker as pm

    win = pm.PackageTodoGUI()
    try:
        ids = [win.engine_combo.itemData(i) for i in range(win.engine_combo.count())]
        assert ids == ["blindcube", "flatcube"]
        # BlindCube v2 (estándar) va preseleccionado; el combo nunca queda vacío.
        assert win.engine_combo.currentData() == "blindcube"
        assert win._selected_engine().id == "blindcube"
        # El motor legacy se marca en la etiqueta (texto traducido).
        from lib.i18n import tr

        legacy_index = win.engine_combo.findData("flatcube")
        assert tr("build.engine_legacy") in win.engine_combo.itemText(legacy_index)
    finally:
        win.close()
        qapp.processEvents()


def test_engine_registry_and_containers():
    """Los 3 motores se registran y sus contenedores hacen round-trip."""
    from lib import blindcubeEngine, flatcubeEngine, makeselfEngine
    from lib.engines import available_engines, compiler_engines, resolve_engine

    assert set(available_engines()) == {"makeself", "flatcube", "blindcube"}
    assert [e.id for e in compiler_engines()] == ["blindcube", "flatcube"]
    assert resolve_engine(None).id == "blindcube"

    # BlindCube v2: cabecera con magic bytes + LZMA.
    payload = b"package-maker" * 50
    container = blindcubeEngine.pack(payload, meta={"app": "demo"})
    assert container.startswith(b"BLINDCUB")
    meta, restored = blindcubeEngine.unpack(container)
    assert restored == payload
    assert meta["app"] == "demo"

    # FlatCube v1: el .flatkpkg es un ZIP, sin cabecera propia.
    zip_bytes = b"PK\x03\x04demo"
    assert flatcubeEngine.pack(zip_bytes) == zip_bytes

    # MakeSelf valida la ley de nombres canónicos.
    assert makeselfEngine.validate_canonical_name("Influent.demo.v1.0-24.01-10.00-AlphaCube")
    assert not makeselfEngine.validate_canonical_name("Influent.demo")

