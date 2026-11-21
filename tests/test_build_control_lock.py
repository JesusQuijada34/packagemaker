# -*- coding: utf-8 -*-
"""Regresiones del bloqueo de controles durante el empaquetado (Fase 1.3).

Los botones seguían activos mientras compilaba, así que se podía lanzar un
segundo empaquetado o cambiar el motor a mitad del proceso. Además el hilo
intercalaba frases de "curiosidades" aleatorias en lugar del progreso real.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_build_thread_has_no_random_phrases():
    source = (ROOT / "lib" / "blindcubeEngine" / "BuildThread.py").read_text(encoding="utf-8")
    assert "curiosity_phrases" not in source
    assert "emit_random_curiosity" not in source
    assert "curiosity_prefix" not in source
    assert "import random" not in source


def test_compiler_log_is_forwarded_verbatim():
    source = (ROOT / "lib" / "blindcubeEngine" / "BuildThread.py").read_text(encoding="utf-8")
    start = source.index("def handle_compiler_log")
    body = source[start : start + 400]
    assert "self.progress.emit(msg)" in body
    assert "random" not in body


def test_main_window_blocks_controls_while_building():
    source = (ROOT / "packagemaker.py").read_text(encoding="utf-8")
    assert "def _set_build_running" in source
    start = source.index("def _set_build_running")
    body = source[start : source.index("def _on_build_progress")]
    assert "setEnabled(not running)" in body


def test_finished_and_error_unblock_controls():
    source = (ROOT / "packagemaker.py").read_text(encoding="utf-8")
    for handler in ("_on_build_finished", "_on_build_error"):
        start = source.index(f"def {handler}")
        body = source[start : start + 400]
        assert "self._set_build_running(False)" in body, handler


def test_build_start_unblocks_only_after_validation():
    """La compilación no debe arrancar si los datos no son válidos."""
    source = (ROOT / "packagemaker.py").read_text(encoding="utf-8")
    start = source.index("def build_package_action")
    body = source[start : source.index("def _build_controls")]
    assert body.index("validate_build_fields") < body.index("_set_build_running(True)")
    assert body.index("_selected_engine") < body.index("_set_build_running(True)")


class _FakeControl:
    def __init__(self):
        self.enabled = True

    def setEnabled(self, value):  # noqa: N802 - firma de Qt
        self.enabled = value


def test_set_build_running_toggles_every_control(monkeypatch):
    pytest.importorskip("PyQt6.QtWidgets")
    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    assert app is not None

    controls = [_FakeControl() for _ in range(4)]

    import types

    from packagemaker import PackageTodoGUI

    class FakeProgress:
        def __init__(self):
            self.visible = None
            self.marquee = None

        def setVisible(self, value):  # noqa: N802
            self.visible = value

        def setMarquee(self, value):  # noqa: N802
            self.marquee = value

    class Harness:
        def __init__(self):
            self.build_progress = FakeProgress()

        def _build_controls(self):
            return controls

    harness = Harness()
    harness._set_build_running = types.MethodType(
        PackageTodoGUI._set_build_running, harness
    )

    harness._set_build_running(True)
    assert all(not c.enabled for c in controls)
    assert harness.build_progress.visible is True

    harness._set_build_running(False)
    assert all(c.enabled for c in controls)
    assert harness.build_progress.visible is False
