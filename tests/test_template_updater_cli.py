# -*- coding: utf-8 -*-
"""Regresión Q-017: el ``updater.py`` de los proyectos nuevos no tenía CLI.

La plantilla sólo arrancaba la vigilancia en segundo plano y terminaba en
``while True: time.sleep(100)``, así que ``--check``, ``--install`` y
``--version`` se ignoraban y el proceso no terminaba nunca. Estos casos
ejecutan el updater real de un proyecto creado con las plantillas.
"""

from __future__ import annotations

import os
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.makeselfEngine.template_engine import (  # noqa: E402
    create_project_from_templates,
    templates_available,
)

pytestmark = pytest.mark.skipif(
    not templates_available(),
    reason="sin plantillas de proyecto (bundle sin src/templates)",
)

TIMEOUT = 30
LOCAL_VERSION = "v1.0-26.11-10.05"
REMOTE_VERSION = "v1.1-26.12-10.00"


def _project(tmp_path: Path) -> Path:
    target = tmp_path / f"influent.demo.{LOCAL_VERSION}-Danenone"
    create_project_from_templates(
        target,
        publisher="Influent",
        app_id="demo",
        name="Demo",
        author="JesusQuijada34",
        platform="Danenone",
        version_base="1.0",
        description="Demo",
        timestamp="26.11-10.05",
    )
    return target


def _fake_requests(tmp_path: Path, remote_version: str) -> Path:
    """Módulo ``requests`` falso: sin red, respuestas deterministas."""
    module = tmp_path / "fake_requests"
    module.mkdir()
    (module / "requests.py").write_text(
        f'''
REMOTE_XML = "<app><version>{remote_version}</version></app>"


class _Response:
    def __init__(self, status_code=200, text="", headers=None):
        self.status_code = status_code
        self.text = text
        self.headers = headers or {{}}

    def iter_content(self, size=8192):
        yield self.text.encode("utf-8")


def get(url, *args, **kwargs):
    if url.endswith("details.xml"):
        return _Response(200, REMOTE_XML)
    return _Response(200, "", {{"content-length": "0"}})


def head(url, *args, **kwargs):
    return _Response(200 if url.endswith(".iflapp") else 404)
''',
        encoding="utf-8",
    )
    return module


def _blocked_pyqt6(tmp_path: Path) -> Path:
    module = tmp_path / "fake_pyqt6"
    (module / "PyQt6").mkdir(parents=True)
    (module / "PyQt6" / "__init__.py").write_text(
        'raise ImportError("PyQt6 no instalado")\n', encoding="utf-8"
    )
    return module


def _run(project: Path, args, pythonpath: Path | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    paths = [str(project)]
    if pythonpath is not None:
        paths.insert(0, str(pythonpath))
    env["PYTHONPATH"] = os.pathsep.join(paths + [env.get("PYTHONPATH", "")]).strip(os.pathsep)
    return subprocess.run(
        [sys.executable, "updater.py", *args],
        cwd=str(project),
        env=env,
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
    )


def test_version_and_check_terminate(tmp_path: Path):
    project = _project(tmp_path)
    version = _run(project, ["--version"])
    assert version.returncode == 0, version.stderr
    assert "Influent Updater" in version.stdout

    check = _run(project, ["--check"], _fake_requests(tmp_path, REMOTE_VERSION))
    assert check.returncode == 0, check.stderr
    assert f"UPDATE_AVAILABLE: {LOCAL_VERSION} -> {REMOTE_VERSION}" in check.stdout
    assert "TYPE: IFLAPP_PACKAGE" in check.stdout
    assert f"Influent.demo.{REMOTE_VERSION}-Danenone.iflapp" in check.stdout


def test_check_reports_no_update_when_versions_match(tmp_path: Path):
    project = _project(tmp_path)
    check = _run(project, ["--check"], _fake_requests(tmp_path, LOCAL_VERSION))
    assert check.returncode == 0, check.stderr
    assert "NO_UPDATE" in check.stdout


def test_install_zip_replaces_project_files(tmp_path: Path):
    project = _project(tmp_path)
    package = tmp_path / "update.zip"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("demo.py", "print('version nueva')\n")
        archive.writestr("config/settings.json", '{"version": 2}')

    result = _run(project, ["--install", str(package)])
    assert result.returncode == 0, result.stderr
    assert "OK:" in result.stdout
    assert "version nueva" in (project / "demo.py").read_text(encoding="utf-8")
    assert '"version": 2' in (project / "config" / "settings.json").read_text(encoding="utf-8")


def test_install_rejects_non_zip_container(tmp_path: Path):
    project = _project(tmp_path)
    package = tmp_path / "demo.iflapp"
    package.write_bytes(b"IFLAPP2\x00\x00" + b"\x00" * 64)

    result = _run(project, ["--install", str(package)])
    assert result.returncode == 1
    assert "ERROR:" in result.stdout
    assert "no es un .zip" in result.stdout


def test_no_arguments_without_pyqt6_exits_instead_of_hanging(tmp_path: Path):
    project = _project(tmp_path)
    result = _run(project, [], _blocked_pyqt6(tmp_path))
    assert result.returncode == 1
    assert "necesita PyQt6" in result.stderr
