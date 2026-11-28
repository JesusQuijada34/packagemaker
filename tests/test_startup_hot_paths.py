# -*- coding: utf-8 -*-
"""Tramos calientes del arranque: i18n, QSS y telemetría del entorno.

Issue #19 (R-6d1e4a83): en el equipo del reporte la fase «ventana» consume
10,32 s. Estas pruebas fijan dos propiedades que no dependen de la máquina: la
construcción no repite trabajo cuadrático al traducir ni vuelve a leer del disco
lo que no ha cambiado, y la ventana deja medidos sus tramos internos para que
el siguiente reporte automático diga exactamente dónde se pierde el tiempo.
"""

import os
from pathlib import Path


def test_translation_lookup_flattens_the_catalog_once(monkeypatch):
    """``tr()`` no debe aplanar el catálogo completo en cada llamada."""
    from lib import i18n as mod

    calls = []
    real = mod._flatten_translations

    def spy(data, prefix=""):
        calls.append(id(data))
        return real(data, prefix)

    monkeypatch.setattr(mod, "_flatten_translations", spy)
    monkeypatch.setattr(mod, "_flat_cache", {})
    monkeypatch.setattr(mod.i18n, "_current_lang", "es")

    mod.i18n._lookup_key("sidebar.create")
    warm = len(calls)
    assert warm >= 1

    for _ in range(25):
        mod.i18n._lookup_key("sidebar.create")
        mod.i18n.translate("sidebar.create")

    assert len(calls) == warm, "el catálogo se volvió a aplanar en cada consulta"


def test_flat_cache_reacts_to_a_replaced_catalog(monkeypatch):
    """Recargar el catálogo debe invalidar el aplanado memorizado."""
    from lib import i18n as mod

    monkeypatch.setattr(mod, "_flat_cache", {})
    monkeypatch.setattr(mod, "_translation_cache", dict(mod._translation_cache))
    monkeypatch.setattr(mod.i18n, "_current_lang", "es")

    mod._translation_cache["es"] = {"a.b": "primero"}
    assert mod.i18n._lookup_key("a.b") == "primero"

    mod._translation_cache["es"] = {"a.b": "segundo"}
    assert mod.i18n._lookup_key("a.b") == "segundo"


def test_qss_reads_an_unchanged_file_once(monkeypatch):
    """Cada widget pedía su QSS al disco; el fichero no cambia en ejecución."""
    from lib import qss_loader

    target = qss_loader.QSS_DIR / "qcheckbox.qss"
    monkeypatch.setattr(qss_loader, "_TEXT_CACHE", {})

    reads = []
    real = Path.read_text

    def spy(self, *args, **kwargs):
        reads.append(Path(self))
        return real(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", spy)

    first = qss_loader.read_qss_file("qcheckbox")
    second = qss_loader.read_qss_file("qcheckbox")

    assert first == second
    assert sum(1 for path in reads if path == target) == 1


def test_qss_cache_reloads_when_the_file_changes(monkeypatch, tmp_path):
    """Un QSS editado debe releerse: la caché va por estado del fichero."""
    from lib import qss_loader

    monkeypatch.setattr(qss_loader, "QSS_DIR", tmp_path)
    monkeypatch.setattr(qss_loader, "_TEXT_CACHE", {})

    path = tmp_path / "qtest.qss"
    path.write_text("QWidget { color: red; }", encoding="utf-8")
    assert "red" in qss_loader.read_qss_file("qtest")

    # El tamaño cambia (red → blue), así que la clave de estado también.
    path.write_text("QWidget { color: blue; }", encoding="utf-8")
    os.utime(path, None)
    assert "blue" in qss_loader.read_qss_file("qtest")


def test_environment_probes_git_once_per_session(monkeypatch):
    """``collect_environment()`` se llama varias veces por sesión."""
    from lib import report_telemetry as telemetry

    monkeypatch.setattr(telemetry, "_git_commit_cache", {})

    calls = []

    class _Result:
        stdout = "abc1234\n"

    def fake_run(*args, **kwargs):
        calls.append(args)
        return _Result()

    monkeypatch.setattr(telemetry.subprocess, "run", fake_run)

    first = telemetry.collect_environment()
    second = telemetry.collect_environment()

    assert first["commit"] == "abc1234"
    assert second["commit"] == "abc1234"
    assert len(calls) == 1, "cada reporte volvía a lanzar git rev-parse"


def test_window_construction_records_subphases(_qt_app):
    """La fase «ventana» debe desglosarse para el reporte de tirones."""
    import packagemaker as pm

    window = pm.PackageTodoGUI()
    try:
        phases = window.startup_subphases()
        names = [name for name, _seconds in phases]
        for expected in ("ventana_paginas", "ventana_tema", "ventana_landing"):
            assert expected in names
        assert all(seconds >= 0 for _name, seconds in phases)
    finally:
        window.deleteLater()
