# -*- coding: utf-8 -*-
"""La TUI no debe caer con rutas sin permisos (R-9a4c1e27).

En Python 3.13 ``Path.exists()`` propaga ``PermissionError`` cuando el
directorio padre no es accesible. Las pantallas de la TUI comprobaban con
``Path.exists()`` las rutas escritas por el usuario, así que una carpeta
bloqueada terminaba en traceback. ``_safe_exists`` traduce el fallo a
«no existe» y las pantallas muestran su mensaje normal.
"""
import io
import os
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import pytest

from lib import tui

_UNREADABLE_SKIP = pytest.mark.skipif(
    os.name == "nt" or (hasattr(os, "geteuid") and os.geteuid() == 0),
    reason="los permisos POSIX no bloquean la lectura en Windows ni como root",
)


def _locked_dir(tmp_path: Path) -> Path:
    locked = tmp_path / "locked"
    locked.mkdir()
    (locked / "details.xml").write_text("<app/>", encoding="utf-8")
    locked.chmod(0o000)
    return locked


def _unlock(path: Path) -> None:
    try:
        path.chmod(0o755)
    except OSError:
        pass


@_UNREADABLE_SKIP
def test_safe_exists_treats_permission_error_as_missing(tmp_path):
    locked = _locked_dir(tmp_path)
    try:
        assert tui._safe_exists(locked / "details.xml") is False
        assert tui._safe_exists(tmp_path) is True
    finally:
        _unlock(locked)


@_UNREADABLE_SKIP
def test_get_version_survives_unreadable_cwd(tmp_path):
    locked = _locked_dir(tmp_path)
    try:
        with patch.object(tui.os, "getcwd", return_value=str(locked)):
            assert tui._get_version() == "3.x"
    finally:
        _unlock(locked)


@_UNREADABLE_SKIP
def test_show_details_xml_reports_missing_without_traceback(tmp_path):
    locked = _locked_dir(tmp_path)
    output = io.StringIO()
    try:
        with patch.object(tui, "_pause"), redirect_stdout(output):
            tui._show_details_xml(locked)
    finally:
        _unlock(locked)
    assert tui.tr("tui.details_not_found") in output.getvalue()


@_UNREADABLE_SKIP
def test_screen_build_rejects_unreadable_manual_path(tmp_path):
    locked = _locked_dir(tmp_path)
    output = io.StringIO()
    try:
        with (
            patch.object(tui, "_clear"),
            patch.object(tui, "_banner"),
            patch.object(tui, "_pause"),
            patch.object(tui, "_base_dir", return_value=locked),
            patch.object(tui, "_prompt", return_value=str(locked / "proj")),
            redirect_stdout(output),
        ):
            tui._screen_build()
    finally:
        _unlock(locked)
    assert tui.tr("tui.invalid_project_path") in output.getvalue()


@_UNREADABLE_SKIP
def test_screen_moonfix_rejects_unreadable_manual_path(tmp_path):
    locked = _locked_dir(tmp_path)
    output = io.StringIO()
    try:
        with (
            patch.object(tui, "_clear"),
            patch.object(tui, "_banner"),
            patch.object(tui, "_pause"),
            patch.object(tui, "_base_dir", return_value=locked),
            patch.object(tui, "_prompt", return_value=str(locked / "proj")),
            redirect_stdout(output),
        ):
            tui._screen_moonfix()
    finally:
        _unlock(locked)
    assert tui.tr("tui.invalid_path") in output.getvalue()


@_UNREADABLE_SKIP
def test_project_actions_survives_unreadable_project(tmp_path):
    locked = _locked_dir(tmp_path)
    try:
        with (
            patch.object(tui, "_clear"),
            patch.object(tui, "_banner"),
            patch.object(tui, "_pause"),
            patch.object(tui, "_print_menu"),
            patch.object(tui, "_select_menu", return_value=0),
        ):
            tui._project_actions(locked)
    finally:
        _unlock(locked)


def test_list_projects_skips_entries_that_cannot_be_statted(tmp_path):
    good = tmp_path / "good"
    good.mkdir()

    class _Unstatable:
        name = "boom"

        def stat(self):
            raise PermissionError("sin acceso")

    with patch.object(tui, "list_projects", return_value=[good, _Unstatable()]):
        assert tui._list_projects(tmp_path) == [good]
