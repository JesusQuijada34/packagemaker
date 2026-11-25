"""Regresión R-7a5d2c94: el programa arranca sin la dependencia ``PyQt6``.

``packagemaker.py`` decide entre GUI, TUI y CLI según ``PYQT6_AVAILABLE``, pero
varios módulos de interfaz declaraban un respaldo incompleto en su ``except
ImportError`` (sólo ``QWidget``, o ningún ``pyqtSignal``). El import de nivel
superior abortaba con ``NameError`` antes de leer los argumentos, así que ni
``--app-version`` ni la TUI funcionaban en una máquina sin PyQt6 (o con las
bibliotecas de sistema de Qt incompletas).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
ENTRY = REPO_ROOT / "packagemaker.py"


@pytest.fixture()
def blocked_pyqt6(tmp_path: Path) -> Path:
    """Directorio con un ``PyQt6`` que simula la dependencia ausente."""
    package = tmp_path / "PyQt6"
    package.mkdir()
    (package / "__init__.py").write_text(
        'raise ImportError("PyQt6 no instalado")\n', encoding="utf-8"
    )
    return tmp_path


def _run(args, pythonpath: Path, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(pythonpath), str(REPO_ROOT), env.get("PYTHONPATH", "")]
    ).strip(os.pathsep)
    env.pop("QT_QPA_PLATFORM", None)
    return subprocess.run(
        [sys.executable, str(ENTRY), *args],
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
    )


def test_cli_runs_without_pyqt6(blocked_pyqt6: Path):
    result = _run(["--app-version"], blocked_pyqt6)
    assert result.returncode == 0, result.stderr
    assert "Influent Package Maker" in result.stdout
    assert "Traceback" not in result.stderr
    assert "NameError" not in result.stderr


def test_no_stray_font_debug_output(blocked_pyqt6: Path):
    result = _run(["--app-version"], blocked_pyqt6)
    assert "font: none" not in result.stderr


@pytest.mark.parametrize(
    "flag",
    ["--list-compilers", "--list-engines", "--list-hardening", "--list-fonts"],
)
def test_headless_actions_work_without_pyqt6(blocked_pyqt6: Path, flag: str):
    result = _run([flag], blocked_pyqt6)
    assert result.returncode == 0, result.stderr
    assert "Traceback" not in result.stderr
    assert result.stdout.strip()


def test_ui_modules_import_without_pyqt6(blocked_pyqt6: Path):
    modules = [
        "lib.settings_cards",
        "lib.settings_panel",
        "lib.github_login_landing",
        "lib.github_profile_card",
        "lib.pm_dashboard",
        "lib.iflapp_ide_dialog",
    ]
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(blocked_pyqt6), str(REPO_ROOT), env.get("PYTHONPATH", "")]
    ).strip(os.pathsep)
    result = subprocess.run(
        [sys.executable, "-c", "import " + ", ".join(modules)],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, result.stderr
    assert "NameError" not in result.stderr
