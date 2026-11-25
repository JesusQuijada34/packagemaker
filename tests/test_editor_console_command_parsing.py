"""Regresión R-3a8f6b25: la consola del editor no aborta con comillas sin cerrar.

El campo de entrada de la consola es un slot de Qt. ``shlex.split`` lanza
``ValueError`` cuando las comillas no cierran, la excepción escapaba del slot y
PyQt6 abortaba el proceso del editor (perdiendo el trabajo sin guardar).
"""

from __future__ import annotations

import pytest

pytest.importorskip("PyQt6.QtWidgets")

from pmCodeEditor import ConsolePanel  # noqa: E402


@pytest.fixture()
def console(_qt_app):
    panel = ConsolePanel()
    panel._python_path = "python"
    yield panel
    panel.deleteLater()


def test_split_still_raises_for_callers_that_validate(console):
    with pytest.raises(ValueError):
        console._normalize_shell_command_list('python "sin cerrar')


def test_run_command_reports_invalid_quotes(console):
    assert console.run_command('python "sin cerrar') is False
    assert "Comando no válido" in console.output.toPlainText()


def test_execute_input_reports_invalid_quotes(console):
    console.input_field.setText('pip install "paquete')
    console._execute_input()
    assert "Comando no válido" in console.output.toPlainText()
    assert console._process is None


def test_valid_commands_are_unchanged(console):
    assert console._normalize_shell_command_list("!echo hola") == ["sh", "-c", "echo hola"]
    assert console._normalize_shell_command_list("pip install foo") == [
        "python",
        "-m",
        "pip",
        "install",
        "foo",
    ]
