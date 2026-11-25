# -*- coding: utf-8 -*-
"""El aviso de sobrescritura del asistente mira la carpeta que se va a crear.

El diálogo comprobaba ``rutaBase/nombreProyecto`` pero escribía en la carpeta
canónica ``publisher.app.vX.x-YY.MM-HH.MM-Plataforma``, así que el aviso nunca
aparecía y un proyecto existente se sobrescribía en silencio (perdiendo el
guion del usuario).
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pytest.importorskip("PyQt6.QtWidgets")

import packagemaker as pm  # noqa: E402
import lib.projectNameFormatter as formatter  # noqa: E402

TIMESTAMP = "26.11-05.00"
FOLDER = "Acme.demo.v1.0.0-26.11-05.00-Knosthalij"


class _Dialog:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


def _answers(monkeypatch, answer):
    calls = []

    def launch(parent, title, message, mode="info", **kwargs):
        calls.append({"title": title, "message": message, "mode": mode})
        return answer

    monkeypatch.setattr(pm.LeviathanDialog, "launch", staticmethod(launch))
    monkeypatch.setattr(
        formatter.ProjectNameFormatter,
        "get_timestamp",
        staticmethod(lambda: TIMESTAMP),
    )
    return calls


def _create(base):
    pm.PackageTodoGUI._ejecutarCreacionProyecto(
        object(),  # self: el método sólo usa el padre para los avisos
        str(base),
        "Demo",
        "1.0.0",
        "JesusQuijada34",
        "Acme",
        "",
        _Dialog(),
    )


def test_existing_project_is_not_overwritten_without_confirmation(tmp_path, monkeypatch):
    calls = _answers(monkeypatch, 0)
    project = tmp_path / FOLDER
    project.mkdir()
    script = project / "demo.py"
    script.write_text("print('codigo del usuario')\n", encoding="utf-8")

    _create(tmp_path)

    assert script.read_text(encoding="utf-8") == "print('codigo del usuario')\n"
    assert [call["mode"] for call in calls] == ["question"]
    assert FOLDER in calls[0]["message"]


def test_existing_project_is_overwritten_after_confirmation(tmp_path, monkeypatch):
    calls = _answers(monkeypatch, 1)
    project = tmp_path / FOLDER
    project.mkdir()
    script = project / "demo.py"
    script.write_text("print('codigo del usuario')\n", encoding="utf-8")

    _create(tmp_path)

    assert "codigo del usuario" not in script.read_text(encoding="utf-8")
    assert [call["mode"] for call in calls] == ["question", "success"]


def test_new_project_is_created_without_asking(tmp_path, monkeypatch):
    calls = _answers(monkeypatch, 0)

    _create(tmp_path)

    assert (tmp_path / FOLDER / "demo.py").is_file()
    assert [call["mode"] for call in calls] == ["success"]
