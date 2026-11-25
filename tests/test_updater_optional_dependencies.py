"""Regresiones del updater sin ``leviathan_ui`` (R-4d7b2e91).

``updater.py`` se copia a todos los proyectos empaquetados y también se usa en
modo headless (``--version``, ``--check``, ``--install``). Importaba
``leviathan_ui`` de forma incondicional, así que en una máquina sin esa
dependencia opcional abortaba con ``ImportError`` antes de leer los argumentos.

Cubre además R-9d5c1e73: el mismo problema con ``PyQt6``, que se importaba en el
nivel superior del updater y de ``lib/coreUpdater/workers.py``.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("PyQt6.QtWidgets")

REPO_ROOT = Path(__file__).resolve().parents[1]
UPDATER = REPO_ROOT / "updater.py"


@pytest.fixture()
def blocked_leviathan(tmp_path: Path) -> Path:
    """Directorio con un ``leviathan_ui`` que simula la dependencia ausente."""
    stub = tmp_path / "leviathan_ui.py"
    stub.write_text('raise ImportError("leviathan_ui no instalado")\n', encoding="utf-8")
    return tmp_path


def _run(args, pythonpath: Path, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(pythonpath), str(REPO_ROOT), env.get("PYTHONPATH", "")]
    ).strip(os.pathsep)
    return subprocess.run(
        [sys.executable, str(UPDATER), *args],
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_version_works_without_leviathan_ui(blocked_leviathan: Path):
    result = _run(["--version"], blocked_leviathan)
    assert result.returncode == 0, result.stderr
    assert "Influent FireCube Updater v2.1" in result.stdout


def test_argument_validation_works_without_leviathan_ui(blocked_leviathan: Path):
    result = _run(["--accept-license"], blocked_leviathan)
    assert result.returncode == 1
    assert "--accept-license requiere --silent" in result.stdout


def test_accent_and_wipe_window_fallbacks(blocked_leviathan: Path):
    code = (
        "import updater;"
        "print(updater.LEVIATHAN_AVAILABLE);"
        "print(updater.get_accent_color());"
        "w = updater.WipeWindow.create();"
        "print(w.set_mode('ghostBlur').set_radius(5).apply(None) is w)"
    )
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(blocked_leviathan), str(REPO_ROOT), env.get("PYTHONPATH", "")]
    ).strip(os.pathsep)
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    assert lines[0] == "False"
    assert lines[1] == "#0078D4"
    assert lines[2] == "True"


@pytest.fixture()
def blocked_pyqt6(tmp_path: Path) -> Path:
    """Directorio con un paquete ``PyQt6`` que simula la dependencia ausente."""
    package = tmp_path / "PyQt6"
    package.mkdir()
    (package / "__init__.py").write_text(
        'raise ImportError("PyQt6 no instalado")\n', encoding="utf-8"
    )
    return tmp_path


def test_version_works_without_pyqt6(blocked_pyqt6: Path):
    result = _run(["--version"], blocked_pyqt6)
    assert result.returncode == 0, result.stderr
    assert "Influent FireCube Updater v2.1" in result.stdout


def test_argument_validation_works_without_pyqt6(blocked_pyqt6: Path):
    result = _run(["--accept-license"], blocked_pyqt6)
    assert result.returncode == 1
    assert "--accept-license requiere --silent" in result.stdout


def test_headless_check_without_pyqt6(blocked_pyqt6: Path, tmp_path: Path):
    result = _run(["--check"], blocked_pyqt6, cwd=tmp_path)
    assert result.returncode == 1
    assert "ERROR: No se pudo leer details.xml" in result.stdout
    assert "Traceback" not in result.stderr


def test_silent_install_without_pyqt6(blocked_pyqt6: Path, tmp_path: Path):
    bad = tmp_path / "roto.iflapp"
    bad.write_bytes(b"no es un paquete")
    result = _run(["--install", str(bad), "--silent"], blocked_pyqt6, cwd=tmp_path)
    assert result.returncode == 1
    assert "ERROR:" in result.stdout
    assert "Traceback" not in result.stderr


def test_gui_request_explains_missing_pyqt6(blocked_pyqt6: Path):
    result = _run([], blocked_pyqt6)
    assert result.returncode == 1
    assert "necesita PyQt6" in result.stderr


def test_gui_install_explains_missing_pyqt6(blocked_pyqt6: Path, tmp_path: Path):
    bad = tmp_path / "roto.iflapp"
    bad.write_bytes(b"no es un paquete")
    result = _run(["--install", str(bad)], blocked_pyqt6, cwd=tmp_path)
    assert result.returncode == 1
    assert "necesita PyQt6" in result.stderr
