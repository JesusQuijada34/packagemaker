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


# --- .mexf: compilador y paso opcional del build con rutas ilegibles -------- #

_MEXF_DETAILS = """<?xml version="1.0" encoding="utf-8"?>
<app>
  <publisher>Influent</publisher>
  <app>demo</app>
  <name>demo</name>
  <version>1.0.0</version>
  <platform>AlphaCube</platform>
  <author>JesusQuijada34</author>
</app>
"""


def _make_mexf_project(directory: Path) -> Path:
    project = directory / "mexfproj"
    (project / ".mexf").mkdir(parents=True)
    (project / ".mexf" / "main.mexf").write_text(
        "format: mexf\nversion: 1\nmetadata:\n  id: demo\n  name: demo\n  version: v1.0\n"
        "runtime:\n  launcher: argv\ncommands: []\n",
        encoding="utf-8",
    )
    (project / "details.xml").write_text(_MEXF_DETAILS, encoding="utf-8")
    return project


@_UNREADABLE_SKIP
def test_mexf_read_details_converts_permission_error(tmp_path):
    from lib.mexf_compiler import MexfCompileError, read_project_details

    project = _make_mexf_project(tmp_path)
    project.chmod(0)
    try:
        with pytest.raises(MexfCompileError):
            read_project_details(project)
    finally:
        project.chmod(0o755)


@_UNREADABLE_SKIP
def test_mexf_compiler_run_skips_unreadable_root(tmp_path):
    from lib.mexf_compiler import MexfCompiler

    project = _make_mexf_project(tmp_path)
    project.chmod(0)
    try:
        compiler = MexfCompiler(project, tmp_path / "out")
        result = compiler.run()
    finally:
        project.chmod(0o755)

    assert result is None
    assert "No se pudo leer" in compiler.last_error


@_UNREADABLE_SKIP
def test_mexf_compile_project_converts_permission_error(tmp_path):
    from lib.mexf_compiler import MexfCompileError, compile_mexf_project

    project = _make_mexf_project(tmp_path)
    project.chmod(0)
    try:
        with pytest.raises(MexfCompileError):
            compile_mexf_project(project, tmp_path / "demo.asksome")
    finally:
        project.chmod(0o755)


@_UNREADABLE_SKIP
def test_buildthread_mexf_step_skips_unreadable_dir(tmp_path):
    from lib.blindcubeEngine.BuildThread import FlangCompiler

    project = _make_mexf_project(tmp_path)
    project.chmod(0)
    logs = []
    fake = type("Fake", (), {})()
    fake.repo_path = project
    fake.output_path = tmp_path
    fake.last_error = ""
    fake.log = logs.append
    try:
        result = FlangCompiler._compile_mexf_if_present(fake)
    finally:
        project.chmod(0o755)

    assert result is None
    assert "No se pudo leer .mexf" in fake.last_error


@_UNREADABLE_SKIP
def test_mexf_compile_without_readable_icon_still_builds(tmp_path):
    from lib.mexf_compiler import compile_mexf_project

    project = _make_mexf_project(tmp_path)
    app_dir = project / "app"
    app_dir.mkdir()
    app_dir.chmod(0)
    try:
        result = compile_mexf_project(project, tmp_path / "demo.asksome")
    finally:
        app_dir.chmod(0o755)

    assert result.output.is_file()


# --- CLI: creación, reparación y compilación sin permisos ------------------- #
#
# ``R-4a7e2c91``: ``create`` terminaba con ``PermissionError`` y traceback cuando
# la carpeta base no era escribible.
# ``R-6c9d3f52``: ``moonfix``/``repair`` hacían lo mismo con un proyecto de solo
# lectura al que le faltaba una subcarpeta.
# ``R-8e2b7d64``: ``compile``/``--buildthis`` dejaban escapar el ``OSError`` de
# ``dist/`` (la QThread del build también lo filtraba).

def _make_cli_project(base: Path) -> Path:
    project = base / "Influent.demo.v1.0.0-26.11-00.00-Danenone"
    project.mkdir(parents=True)
    (project / "details.xml").write_text(DETAILS, encoding="utf-8")
    (project / "demo.py").write_text("print('hi')\n", encoding="utf-8")
    return project


def test_create_project_reports_unwritable_base_dir(tmp_path, capsys):
    from lib.cliHandler import handle_cli_action

    base = tmp_path / "projects"
    base.mkdir()
    denied = PermissionError(13, "denegado", str(base))
    with patch(
        "lib.makeselfEngine.template_engine.create_project_from_templates",
        side_effect=denied,
    ):
        with pytest.raises(SystemExit) as excinfo:
            handle_cli_action(
                "create_project",
                {
                    "path": str(base),
                    "name": "Demo",
                    "shortname": "demo",
                    "publisher": "Influent",
                    "author": "Tester",
                },
                None,
                headless=True,
            )

    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "[ERROR] No se pudo crear el proyecto" in captured.out
    assert "Traceback" not in captured.out + captured.err


def test_repair_project_reports_unreadable_project(tmp_path, capsys):
    from lib.cliHandler import handle_cli_action

    project = _make_cli_project(tmp_path / "projects")
    denied = PermissionError(13, "denegado", str(project / "docs"))
    with patch(
        "lib.makeselfEngine.template_engine.repair_project_from_templates",
        side_effect=denied,
    ):
        with pytest.raises(SystemExit) as excinfo:
            handle_cli_action(
                "repair_project",
                {
                    "path": str(project.parent),
                    "name": "Demo",
                    "shortname": "demo",
                    "publisher": "Influent",
                },
                None,
                headless=True,
            )

    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "[ERROR] No se pudo reparar el proyecto" in captured.out
    assert "Traceback" not in captured.out + captured.err


@pytest.mark.parametrize("action", ["buildthis", "compile_project"])
def test_compile_reports_filesystem_error_without_traceback(tmp_path, capsys, action):
    from lib.cliHandler import handle_cli_action

    project = _make_cli_project(tmp_path / "projects")
    output = tmp_path / "out"
    denied = PermissionError(13, "denegado", str(project / "dist"))
    data = {"path": str(project)}
    if action == "compile_project":
        data = {
            "path": str(project.parent),
            "name": "Demo",
            "shortname": "demo",
            "publisher": "Influent",
        }

    with patch(
        "lib.blindcubeEngine.BuildThread.FlangCompiler.compile_binaries",
        side_effect=denied,
    ), patch(
        "lib.platform_detect.compile_output_directory",
        return_value=str(output),
    ):
        with pytest.raises(SystemExit) as excinfo:
            handle_cli_action(
                action,
                data,
                None,
                headless=True,
                output=str(output),
                sandbox=False,
            )

    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "[ERROR] La compilación falló por un problema del sistema de archivos" in captured.out
    assert "Traceback" not in captured.out + captured.err


def test_compile_binary_translates_unwritable_build_dir(tmp_path):
    from lib.blindcubeEngine.BuildThread import FlangCompiler

    project = _make_cli_project(tmp_path / "projects")
    compiler = FlangCompiler(
        project,
        tmp_path / "out",
        log_callback=lambda _msg: None,
        compiler_name="zipapp",
        sandbox=False,
    )
    script = {"path": project / "demo.py", "name": "demo", "icon": None}
    with patch(
        "lib.blindcubeEngine.BuildThread.tempfile.mkdtemp",
        side_effect=PermissionError(13, "denegado"),
    ):
        assert compiler._compile_binary(script, windowed=False) is False

    assert "No se pudo preparar el directorio de compilación" in compiler.last_error
