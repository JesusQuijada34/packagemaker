"""Regresión R-7e2d9c14: el CLI arranca sin la dependencia ``requests``.

``packagemaker.py`` importaba ``requests`` en el nivel superior, aunque sólo la
descarga de iconos por URL la usa. En una máquina sin esa dependencia el
programa abortaba con ``ImportError`` antes de leer los argumentos, de modo que
ni siquiera ``--app-version`` funcionaba.
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
def blocked_requests(tmp_path: Path) -> Path:
    """Directorio con un ``requests`` que simula la dependencia ausente."""
    (tmp_path / "requests.py").write_text(
        'raise ImportError("requests no instalado")\n', encoding="utf-8"
    )
    return tmp_path


def _run(args, pythonpath: Path, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(pythonpath), str(REPO_ROOT), env.get("PYTHONPATH", "")]
    ).strip(os.pathsep)
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    return subprocess.run(
        [sys.executable, str(ENTRY), *args],
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
    )


def test_cli_runs_without_requests(blocked_requests: Path):
    result = _run(["--app-version"], blocked_requests)
    assert result.returncode == 0, result.stderr
    assert "Influent Package Maker" in result.stdout
    assert "Traceback" not in result.stderr


def test_headless_list_works_without_requests(blocked_requests: Path):
    result = _run(["--list-engines"], blocked_requests)
    assert result.returncode == 0, result.stderr
    assert "Traceback" not in result.stderr
