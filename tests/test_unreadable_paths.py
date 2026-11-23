# -*- coding: utf-8 -*-
"""Rutas sin permisos: ningún comando debe terminar en traceback.

Auditoría del ciclo 23. En Python 3.13 ``Path.exists()``/``is_file()``/
``iterdir()`` propagan ``PermissionError`` cuando el directorio padre no es
accesible, así que las rutas que vienen del usuario necesitan traducirse a un
mensaje legible. Cubre:

- ``R-4c7a9e13``: ``--inspect-extract`` con un destino bloqueado.
- ``R-8e2b5c43``: ``--list-asksome`` con una raíz de instalación ilegible.
- ``R-3d9f1a76``: ``compile``/TUI con la carpeta base ilegible.
- ``R-6c1e8b52``: ``--buildthis``/``--ide-run``/``--shell-info`` con rutas
  ilegibles.
- ``R-7b3e9c28``: ``--install-asksome`` con un artefacto ilegible.
- ``R-5a9d2f74``: abrir una carpeta genérica o lanzar MoonFix por lotes sobre
  una carpeta ilegible.
- ``R-2f8a4d61``: ``remove_tree`` lanzaba ``PermissionError`` pese a prometer
  que no lanza.
"""
import io
import os
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]

_UNREADABLE_SKIP = pytest.mark.skipif(
    os.name == "nt" or (hasattr(os, "geteuid") and os.geteuid() == 0),
    reason="los permisos POSIX no bloquean la lectura en Windows ni como root",
)

DETAILS = """<?xml version="1.0" encoding="utf-8"?>
<app>
  <publisher>Influent</publisher>
  <app>demo</app>
  <name>demo</name>
  <version>1.0.0</version>
  <platform>Danenone</platform>
  <author>JesusQuijada34</author>
</app>
"""


def _make_iflapp(directory: Path, name: str = "demo.iflapp") -> Path:
    from lib.blindcubeEngine import iflapp_format

    source = directory / "src"
    source.mkdir(exist_ok=True)
    (source / "app.py").write_text("print('hi')\n", encoding="utf-8")
    return iflapp_format.pack_iflapp(
        source,
        directory / name,
        icon=b"ICON",
        details=DETAILS.encode("utf-8"),
    )


def _make_asksome(directory: Path, name: str = "demo.asksome") -> Path:
    from lib.blindcubeEngine.asksome_format import pack_asksome

    staging = directory / "staging"
    staging.mkdir(exist_ok=True)
    (staging / "launcher.py").write_text("print('hi')\n", encoding="utf-8")
    return pack_asksome(staging, directory / name, metadata={"app": "demo"})


def _make_project(directory: Path) -> Path:
    project = directory / "proj"
    project.mkdir()
    (project / "details.xml").write_text(DETAILS, encoding="utf-8")
    (project / "app.py").write_text("print('hi')\n", encoding="utf-8")
    return project


# --- file_ops: los envoltorios no propagan PermissionError ------------------ #

def test_path_helpers_swallow_permission_errors(tmp_path):
    from lib import file_ops

    target = tmp_path / "cualquiera"
    target.write_text("x", encoding="utf-8")
    denied = PermissionError(13, "denegado", str(target))
    with patch.object(Path, "exists", side_effect=denied), \
            patch.object(Path, "is_file", side_effect=denied), \
            patch.object(Path, "is_dir", side_effect=denied), \
            patch.object(Path, "iterdir", side_effect=denied):
        assert file_ops.path_exists(target) is False
        assert file_ops.path_is_file(target) is False
        assert file_ops.path_is_dir(target) is False
        assert file_ops.list_directory(target) == []


def test_remove_tree_keeps_its_no_raise_contract(tmp_path):
    from lib import file_ops

    target = tmp_path / "bloqueado"
    target.mkdir()
    with patch.object(
        file_ops.os, "lstat", side_effect=PermissionError(13, "denegado", str(target))
    ):
        assert file_ops.remove_tree(target) is False
    assert target.is_dir()


# --- Listado de proyectos e instalaciones ----------------------------------- #

@_UNREADABLE_SKIP
def test_project_listing_ignores_unreadable_base_dir(tmp_path):
    from lib.project_locator import iter_projects, list_projects, locate_project

    base = tmp_path / "projects"
    base.mkdir()
    project = base / "influent.demo.v1.0-26.11-00.00-Knosthalij"
    project.mkdir()
    (project / "details.xml").write_text(DETAILS, encoding="utf-8")
    base.chmod(0)
    try:
        assert iter_projects(base) == []
        assert list_projects(base) == []
        assert locate_project(base, publisher="influent", app_id="demo") is None
    finally:
        base.chmod(0o755)


@_UNREADABLE_SKIP
def test_list_installed_ignores_unreadable_root(tmp_path):
    from lib.blindcubeEngine.asksome_installer import list_installed

    root = tmp_path / "root"
    entry = root / "influent.demo"
    entry.mkdir(parents=True)
    (entry / "install.json").write_text('{"app_id": "influent.demo"}', encoding="utf-8")
    root.chmod(0)
    try:
        assert list_installed(root) == []
    finally:
        root.chmod(0o755)


def test_list_installed_cli_reports_empty_root(tmp_path, capsys):
    from lib.cliHandler import AsksomeInstallHelper

    root = tmp_path / "root"
    root.mkdir()
    with patch.object(Path, "iterdir", side_effect=PermissionError(13, "denegado")):
        assert AsksomeInstallHelper.list_installed({"install_root": str(root)}) is True
    assert "Sin artefactos .asksome instalados" in capsys.readouterr().out


# --- CLI: inspect-extract --------------------------------------------------- #

def test_export_header_assets_translates_oserror(tmp_path):
    from lib.blindcubeEngine import iflapp_format

    artifact = _make_iflapp(tmp_path)
    blocker = tmp_path / "blocker"
    blocker.write_text("no soy un directorio", encoding="utf-8")
    with pytest.raises(iflapp_format.IflappError):
        iflapp_format.export_header_assets(artifact, blocker)


def test_inspect_extract_reports_blocked_destination(tmp_path, capsys):
    from lib.cliHandler import PackageInspectHelper

    artifact = _make_iflapp(tmp_path)
    blocker = tmp_path / "blocker"
    blocker.write_text("no soy un directorio", encoding="utf-8")
    assert PackageInspectHelper.inspect(
        {"path": str(artifact), "extract": str(blocker)}
    ) is False
    captured = capsys.readouterr()
    assert "[ERROR]" in captured.out
    assert "Traceback" not in captured.out + captured.err


# --- CLI: artefactos y guiones ilegibles ------------------------------------ #

def test_asksome_reader_translates_oserror(tmp_path):
    from lib.blindcubeEngine import asksome_format

    artifact = _make_asksome(tmp_path)
    with patch.object(
        Path, "read_bytes", side_effect=PermissionError(13, "denegado", str(artifact))
    ):
        with pytest.raises(asksome_format.AsksomeError):
            asksome_format.read_asksome_header(artifact)


@_UNREADABLE_SKIP
def test_install_asksome_rejects_unreadable_artifact(tmp_path, capsys):
    from lib.cliHandler import AsksomeInstallHelper

    locked = tmp_path / "locked"
    locked.mkdir()
    artifact = _make_asksome(locked)
    locked.chmod(0)
    try:
        assert AsksomeInstallHelper.install(
            {"path": str(artifact), "install_root": str(tmp_path / "root")}
        ) is False
    finally:
        locked.chmod(0o755)
    captured = capsys.readouterr()
    assert "no es accesible" in captured.out
    assert "Traceback" not in captured.out + captured.err


@_UNREADABLE_SKIP
def test_shell_info_rejects_unreadable_target(tmp_path, capsys):
    from lib.cliHandler import NativeShellHelper

    locked = tmp_path / "locked"
    locked.mkdir()
    artifact = _make_asksome(locked)
    locked.chmod(0)
    try:
        assert NativeShellHelper.info({"path": str(artifact)}) is False
    finally:
        locked.chmod(0o755)
    captured = capsys.readouterr()
    assert "no es accesible" in captured.out
    assert "Traceback" not in captured.out + captured.err


@_UNREADABLE_SKIP
def test_ide_run_rejects_unreadable_script(tmp_path, capsys):
    from lib.cliHandler import IflappIdeHelper

    locked = tmp_path / "locked"
    locked.mkdir()
    script = locked / "app.py"
    script.write_text("print('hi')\n", encoding="utf-8")
    locked.chmod(0)
    try:
        assert IflappIdeHelper.execute({"path": str(script)}) is False
    finally:
        locked.chmod(0o755)
    captured = capsys.readouterr()
    assert "no es accesible" in captured.out
    assert "Traceback" not in captured.out + captured.err


@_UNREADABLE_SKIP
def test_buildthis_rejects_unreadable_project(tmp_path, capsys):
    from lib.cliHandler import handle_cli_action

    project = _make_project(tmp_path)
    project.chmod(0)
    try:
        with pytest.raises(SystemExit) as excinfo:
            with redirect_stdout(io.StringIO()) as out:
                handle_cli_action(
                    "buildthis",
                    str(project),
                    None,
                    headless=True,
                    output=str(tmp_path / "out"),
                )
        assert excinfo.value.code == 1
        assert "no es un proyecto válido" in out.getvalue()
    finally:
        project.chmod(0o755)


# --- GUI: carpetas ilegibles ------------------------------------------------ #

def test_dashboard_generic_open_survives_unreadable_folder(tmp_path):
    from lib import pm_dashboard

    opened = []
    fake = type("Fake", (), {})()
    fake._launch_editor_func = lambda *args: opened.append(args)
    fake.python_path = "python"

    with patch.object(
        pm_dashboard.os, "listdir", side_effect=PermissionError(13, "denegado")
    ):
        pm_dashboard.DashboardWindow._open_as_generic_project(fake, str(tmp_path))

    assert opened and opened[0][0] is None


def test_moonfix_batch_scan_reports_unreadable_folder(tmp_path, monkeypatch):
    import packagemaker as pm

    shown = []

    class FakeDialog:
        @staticmethod
        def launch(*args, **kwargs):
            shown.append((args, kwargs))

    class FakeInput:
        @staticmethod
        def text():
            return str(tmp_path)

    class FakeCheck:
        @staticmethod
        def isChecked():
            return True

    fake = type("Fake", (), {})()
    fake.mf_input = FakeInput()
    fake.mf_batch_mode = FakeCheck()

    monkeypatch.setattr(pm, "LeviathanDialog", FakeDialog)
    monkeypatch.setattr(
        pm.os, "listdir", lambda _path: (_ for _ in ()).throw(PermissionError(13, "denegado"))
    )

    pm.PackageTodoGUI.mf_start_scan(fake)

    assert shown and shown[0][1].get("mode") == "error"
