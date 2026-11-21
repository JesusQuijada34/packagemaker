"""Regresiones del updater sin ``leviathan_ui`` (R-4d7b2e91).

``updater.py`` se copia a todos los proyectos empaquetados y también se usa en
modo headless (``--version``, ``--check``, ``--install``). Importaba
``leviathan_ui`` de forma incondicional, así que en una máquina sin esa
dependencia opcional abortaba con ``ImportError`` antes de leer los argumentos.
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


def _run(args, pythonpath: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(pythonpath), str(REPO_ROOT), env.get("PYTHONPATH", "")]
    ).strip(os.pathsep)
    return subprocess.run(
        [sys.executable, str(UPDATER), *args],
        cwd=str(REPO_ROOT),
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
