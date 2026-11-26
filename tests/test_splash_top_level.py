# -*- coding: utf-8 -*-
"""F-003: el splash es una ventana de nivel superior anterior a la interfaz.

Como ventana hija translúcida, Qt creaba ventanas nativas auxiliares en Windows
(avisos ``must be a top level window`` y varias ventanas vacías antes del primer
fotograma). El arranque debe pintar el splash sin padre y antes de construir la
ventana principal.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pytest.importorskip("PyQt6.QtWidgets")

from PyQt6.QtCore import Qt  # noqa: E402
from PyQt6.QtWidgets import QApplication, QWidget  # noqa: E402

from lib.splash_window import IntegratedSplash  # noqa: E402

_APP = None


def _ensure_app():
    """Conserva la QApplication viva durante toda la sesión de pruebas."""
    global _APP
    _APP = QApplication.instance() or QApplication([])
    return _APP


def test_splash_without_parent_is_a_top_level_window():
    _ensure_app()
    splash = IntegratedSplash()
    try:
        assert splash.parent() is None
        assert splash.isWindow() is True
        flags = splash.windowFlags()
        assert flags & Qt.WindowType.FramelessWindowHint
        assert flags & Qt.WindowType.WindowStaysOnTopHint
        assert splash.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    finally:
        splash.deleteLater()


def test_top_level_splash_covers_the_available_screen():
    app = _ensure_app()
    splash = IntegratedSplash()
    try:
        expected = app.primaryScreen().availableGeometry()
        assert splash.geometry() == expected
        container = splash.findChild(QWidget, "SplashContainer")
        assert container is not None
        assert (container.width(), container.height()) == (splash.width(), splash.height())
    finally:
        splash.deleteLater()


def test_resizing_a_top_level_splash_keeps_its_position():
    app = _ensure_app()
    splash = IntegratedSplash()
    try:
        origin = app.primaryScreen().availableGeometry().topLeft()
        splash.show_splash()
        splash.resize(320, 200)
        app.processEvents()
        assert (splash.width(), splash.height()) == (320, 200)
        assert splash.geometry().topLeft() == origin
        container = splash.findChild(QWidget, "SplashContainer")
        assert (container.width(), container.height()) == (320, 200)
    finally:
        splash.hide()
        splash.deleteLater()


def test_parented_splash_keeps_the_overlay_behaviour():
    _ensure_app()
    host = QWidget()
    host.resize(640, 480)
    splash = IntegratedSplash(parent=host)
    try:
        assert splash.parent() is host
        assert splash.isWindow() is False
        assert (splash.width(), splash.height()) == (640, 480)
    finally:
        splash.deleteLater()
        host.deleteLater()


def test_splash_takes_the_accent_it_receives():
    _ensure_app()
    splash = IntegratedSplash(accent="#123456")
    try:
        assert splash.accent == "#123456"
        assert "#123456" in splash.styleSheet()
    finally:
        splash.deleteLater()


def test_main_paints_the_splash_before_building_the_window():
    text = (ROOT / "packagemaker.py").read_text(encoding="utf-8")
    body = text[text.index("\ndef main("):]
    splash_at = body.index("splash = IntegratedSplash(")
    shown_at = body.index("splash.show_splash()")
    window_at = body.index("main_window = PackageTodoGUI()")
    assert splash_at < shown_at < window_at
    assert "parent=main_window" not in body
    # La ventana principal se revela debajo del splash y éste vuelve a subir.
    assert body.index("splash.raise_()", window_at) > window_at


def test_internal_error_path_closes_the_splash_first():
    text = (ROOT / "packagemaker.py").read_text(encoding="utf-8")
    body = text[text.index("\ndef main("):]
    error_branch = body.index("if startup_plan.internal_errors:")
    close_at = body.index("splash.close()", error_branch)
    report_at = body.index("show_startup_error(", error_branch)
    assert close_at < report_at


def test_updater_splash_is_top_level_without_parent():
    """El updater sufre el mismo defecto: su splash tampoco debe ser hijo."""
    _ensure_app()
    import updater

    splash = updater.IntegratedSplash()
    try:
        assert splash.parent() is None
        assert splash.isWindow() is True
        assert splash.windowFlags() & Qt.WindowType.FramelessWindowHint
        assert splash.width() > 0 and splash.height() > 0
    finally:
        splash.deleteLater()


PROBE = '''
import atexit, shutil, sys, tempfile
from pathlib import Path

# Aísla data/pm.data para no tocar el almacén real del repositorio.
_root = Path(tempfile.mkdtemp(prefix="pm-splash-probe-"))
atexit.register(lambda: shutil.rmtree(_root, ignore_errors=True))
from lib import pm_data

_store = pm_data.PMDataStore(_root / "pm.data")
_store.set_user("base_dir", str(_root / "proyectos"))
_store.set_user("fluthin_apps", str(_root / "apps"))
_store.save()
pm_data._store = _store

sys.argv = ["packagemaker.py"]
import packagemaker as pm
from PyQt6.QtWidgets import QApplication

state = {"splash": None, "visible": None, "order": []}


class ProbeSplash(pm.IntegratedSplash):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        state["splash"] = self

    def show_splash(self):
        state["order"].append("splash")
        super().show_splash()


pm.IntegratedSplash = ProbeSplash


class ProbeGUI(pm.PackageTodoGUI):
    def __init__(self, *args, **kwargs):
        splash = state["splash"]
        state["visible"] = bool(splash is not None and splash.isVisible() and splash.isWindow())
        state["order"].append("gui")
        super().__init__(*args, **kwargs)


pm.PackageTodoGUI = ProbeGUI
QApplication.exec = lambda self: 0

try:
    pm.main()
except SystemExit as exc:
    state["exit"] = exc.code

print("ORDER=", state["order"])
print("SPLASH_VISIBLE_AT_BUILD=", int(bool(state["visible"])))
print("SPLASH_TOP_LEVEL=", int(bool(state["splash"] is not None and state["splash"].isWindow())))
print("SPLASH_PARENT=", state["splash"].parent() if state["splash"] else "none")
print("EXIT=", state.get("exit"))
'''


def test_splash_is_visible_when_the_main_window_is_built(tmp_path):
    """El arranque real pinta el splash antes de construir ``PackageTodoGUI``."""
    import os
    import subprocess

    script = tmp_path / "probe_splash.py"
    script.write_text(PROBE, encoding="utf-8")
    env = dict(
        os.environ,
        QT_QPA_PLATFORM="offscreen",
        DISPLAY=os.environ.get("DISPLAY") or ":0",
        PYTHONPATH=str(ROOT),
    )
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        timeout=300,
        env=env,
        cwd=str(ROOT),
    )
    assert result.returncode == 0, result.stderr[-3000:]
    assert "ORDER= ['splash', 'gui']" in result.stdout
    assert "SPLASH_VISIBLE_AT_BUILD= 1" in result.stdout
    assert "SPLASH_TOP_LEVEL= 1" in result.stdout
    assert "SPLASH_PARENT= None" in result.stdout
    assert "EXIT= 0" in result.stdout

