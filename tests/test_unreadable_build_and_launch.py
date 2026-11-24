# -*- coding: utf-8 -*-
"""Empaquetado y lanzadores no deben caer con rutas inaccesibles.

En Python 3.13 ``Path.exists()``/``is_file()``/``is_dir()`` propagan
``PermissionError`` cuando el directorio padre no es accesible. Tres puntos de
entrada del usuario lo daban por hecho y la excepción escapaba de un slot de Qt
o del ``run()`` de una QThread, donde PyQt6 aborta el proceso:

* iniciar el empaquetado de una carpeta de proyecto inaccesible
  (``find_env_file`` desde el botón y ``BuildThread.run``);
* el botón «Ejecutar» del gestor de aplicaciones
  (``ProjectDetailsDialog._run_installed_app``);
* «Abrir carpeta» de la TUI cuando no hay abridor instalado
  (``xdg-open`` ausente en sistemas mínimos).
"""
import os
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

_UNREADABLE_SKIP = pytest.mark.skipif(
    os.name == "nt" or (hasattr(os, "geteuid") and os.geteuid() == 0),
    reason="los permisos POSIX no bloquean la lectura en Windows ni como root",
)


def _project_with_locked_parent(tmp_path: Path) -> tuple:
    locked = tmp_path / "locked"
    project = locked / "acme.demo.v1.0-26.05-20.13-AlphaCube"
    project.mkdir(parents=True)
    (project / "details.xml").write_text("<app/>", encoding="utf-8")
    locked.chmod(0o000)
    return locked, project


def _unlock(path: Path) -> None:
    try:
        path.chmod(0o755)
    except OSError:
        pass


@_UNREADABLE_SKIP
def test_find_env_file_tolerates_unreadable_project(tmp_path):
    from lib.blindcubeEngine.build_preflight import find_env_file

    locked, project = _project_with_locked_parent(tmp_path)
    try:
        assert find_env_file(project) is None
    finally:
        _unlock(locked)


@_UNREADABLE_SKIP
def test_app_icon_for_tolerates_unreadable_project(tmp_path):
    from lib.env_injection_dialog import app_icon_for

    locked, project = _project_with_locked_parent(tmp_path)
    try:
        assert app_icon_for(project, "demo") is None
    finally:
        _unlock(locked)


@_UNREADABLE_SKIP
def test_build_thread_reports_unreadable_custom_path(tmp_path):
    from lib.blindcubeEngine.BuildThread import BuildThread

    locked, project = _project_with_locked_parent(tmp_path)
    thread = BuildThread("acme", "demo", "1.0", "AlphaCube", custom_path=str(project))
    errors = []
    thread.error.connect(errors.append)
    try:
        thread.run()  # antes: PermissionError dentro de QThread.run
    finally:
        _unlock(locked)
    assert errors, "el build debe informar por la señal error"
    assert "No se encontró la carpeta personalizada" in errors[0]


@_UNREADABLE_SKIP
def test_run_installed_app_reports_unreadable_dir(tmp_path):
    from lib import projectDetailsDialog as dialog_module

    installed = tmp_path / "installed"
    target = installed / "demo"
    target.mkdir(parents=True)
    target.chmod(0o000)

    class Stub:
        fluthin_apps = str(installed)
        pkg = {"name": "demo"}

    messages = []
    with patch.object(
        dialog_module, "warning", lambda *args, **kwargs: messages.append(args)
    ):
        try:
            dialog_module.ProjectDetailsDialog._run_installed_app(Stub())
        finally:
            _unlock(target)
    assert messages, "el slot debe avisar en vez de propagar PermissionError"


def test_tui_open_folder_survives_missing_opener(tmp_path, monkeypatch):
    from lib import tui

    def missing_opener(*args, **kwargs):
        raise FileNotFoundError("xdg-open")

    monkeypatch.setattr(tui.subprocess, "Popen", missing_opener)
    monkeypatch.setattr(tui, "_pause", lambda: None)

    out = StringIO()
    with redirect_stdout(out):
        tui._open_folder(tmp_path)  # antes: FileNotFoundError con traceback
    assert "No se pudo abrir la carpeta" in out.getvalue()


def test_tui_open_folder_opens_accessible_folder(tmp_path, monkeypatch):
    from lib import tui

    calls = []
    monkeypatch.setattr(
        tui.subprocess, "Popen", lambda args, **kwargs: calls.append(args)
    )
    monkeypatch.setattr(tui, "_pause", lambda: None)
    monkeypatch.setattr(tui.sys, "platform", "linux")

    with redirect_stdout(StringIO()):
        tui._open_folder(tmp_path)

    assert calls and calls[0][0] == "xdg-open"
    assert calls[0][1] == str(tmp_path.resolve())
