# -*- coding: utf-8 -*-
"""Q-032: el splash vive dentro de la ventana principal (patrón UWP).

El propietario pidió en el issue #15 que el splash deje de ser una ventana
propia a pantalla completa: debe dibujarse **dentro** de la ventana, con su
marco y su tamaño final desde el primer fotograma, con la interfaz construida
detrás, y retirarse sin abrir ni cerrar ninguna ventana adicional.

El modo de nivel superior se conserva sólo para el splash suelto (el del
``updater.py`` y el que se puede construir sin anfitrión). Como hijo translúcido
Qt creaba ventanas nativas auxiliares en Windows (avisos ``must be a top level
window`` y ventanas vacías), así que el overlay hijo no es translúcido.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pytest.importorskip("PyQt6.QtWidgets")

from PyQt6.QtCore import Qt  # noqa: E402
from PyQt6.QtWidgets import QApplication, QGraphicsOpacityEffect, QWidget  # noqa: E402

from lib.splash_window import IntegratedSplash  # noqa: E402

_APP = None


def _ensure_app():
    """Conserva la QApplication viva durante toda la sesión de pruebas."""
    global _APP
    _APP = QApplication.instance() or QApplication([])
    return _APP


# ── Modo overlay: hijo de la ventana principal (arranque Q-032) ──────────────


def test_hosted_splash_is_a_child_overlay_not_a_window():
    _ensure_app()
    host = QWidget()
    host.resize(1024, 720)
    splash = IntegratedSplash(parent=host)
    try:
        assert splash.parent() is host
        assert splash.isWindow() is False
        # Sin fondo translúcido: el overlay debe ser opaco para no crear
        # ventanas nativas auxiliares en Windows y para que su QSS pinte.
        assert not splash.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        assert splash.testAttribute(Qt.WidgetAttribute.WA_StyledBackground)
    finally:
        splash.deleteLater()
        host.deleteLater()


def test_hosted_splash_covers_the_content_area_and_follows_resize():
    app = _ensure_app()
    host = QWidget()
    host.resize(1024, 720)
    host.show()
    splash = IntegratedSplash(parent=host)
    try:
        assert (splash.width(), splash.height()) == (1024, 720)
        host.resize(900, 600)
        app.processEvents()
        assert (splash.width(), splash.height()) == (900, 600)
        container = splash.findChild(QWidget, "SplashContainer")
        assert container is not None
        assert (container.width(), container.height()) == (900, 600)
    finally:
        splash.deleteLater()
        host.deleteLater()


def test_hosted_splash_is_raised_above_its_siblings():
    app = _ensure_app()
    host = QWidget()
    host.resize(640, 480)
    cover = QWidget(host)
    cover.setGeometry(0, 0, 640, 480)
    host.show()
    cover.show()
    splash = IntegratedSplash(parent=host)
    try:
        splash.show_splash()
        app.processEvents()
        assert splash.isVisible()
        top = host.childAt(host.rect().center())
        assert top is not None
        assert top is splash or splash.isAncestorOf(top)
    finally:
        splash.deleteLater()
        host.deleteLater()


def test_hosted_splash_fades_with_a_graphics_effect():
    app = _ensure_app()
    host = QWidget()
    host.resize(640, 480)
    host.show()
    splash = IntegratedSplash(parent=host)
    try:
        splash.show_splash()
        app.processEvents()
        splash.finish()
        # ``windowOpacity`` no hace nada en un widget hijo: el fundido tiene
        # que ir por un efecto de opacidad gráfica.
        effect = splash.graphicsEffect()
        assert isinstance(effect, QGraphicsOpacityEffect)
        assert effect.opacity() <= 1.0
    finally:
        splash.deleteLater()
        host.deleteLater()


def test_hosted_splash_hides_without_destroying_the_object():
    """``destroy()`` sobre un hijo borraba el objeto C++ y rompía el arranque."""
    import time

    app = _ensure_app()
    host = QWidget()
    host.resize(640, 480)
    host.show()
    splash = IntegratedSplash(parent=host)
    splash.show_splash()
    app.processEvents()

    seen = {}

    def _on_finished():
        # Debe seguir siendo un objeto C++ válido al emitir ``finished``.
        seen["alive"] = splash.width() > 0
        seen["visible"] = splash.isVisible()

    splash.finished.connect(_on_finished)
    splash.finish()

    deadline = time.perf_counter() + 3.0
    while "alive" not in seen and time.perf_counter() < deadline:
        app.processEvents()
        time.sleep(0.01)

    assert seen.get("alive") is True
    assert seen.get("visible") is False
    host.deleteLater()


# ── Modo suelto: ventana de nivel superior (updater y respaldo) ──────────────


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


def test_splash_takes_the_accent_it_receives():
    _ensure_app()
    splash = IntegratedSplash(accent="#123456")
    try:
        assert splash.accent == "#123456"
        assert "#123456" in splash.styleSheet()
    finally:
        splash.deleteLater()


def test_updater_splash_is_top_level_without_parent():
    """El updater conserva su splash suelto: se construye sin anfitrión."""
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


# ── Coreografía de ``main`` ─────────────────────────────────────────────────


def test_main_attaches_the_splash_to_the_main_window():
    text = (ROOT / "packagemaker.py").read_text(encoding="utf-8")
    body = text[text.index("\ndef main("):]
    window_at = body.index("main_window = PackageTodoGUI()")
    splash_at = body.index("splash = IntegratedSplash(")
    show_at = body.index("main_window.show()")
    splash_show_at = body.index("splash.show_splash()")
    assert window_at < splash_at < show_at < splash_show_at
    # El splash es hijo de la ventana: nada de crear una segunda ventana para
    # el arranque.
    assert "parent=main_window.content_container" in body
    assert "splash.raise_()" in body[splash_show_at:]


def test_internal_error_path_does_not_show_an_empty_window():
    text = (ROOT / "packagemaker.py").read_text(encoding="utf-8")
    body = text[text.index("\ndef main("):]
    error_branch = body.index("if startup_plan.internal_errors:")
    report_at = body.index("show_startup_error(", error_branch)
    window_at = body.index("main_window = PackageTodoGUI()")
    # Un fallo de arranque se reporta antes de construir la ventana: nunca se
    # ve un marco vacío (riesgo declarado en Q-032).
    assert report_at < window_at
    assert "splash.close()" not in body


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

state = {"splash": None, "gui": None, "order": [], "visible": None}


class ProbeSplash(pm.IntegratedSplash):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        state["splash"] = self

    def show_splash(self):
        state["order"].append("splash")
        state["visible"] = bool(self.isVisible())
        super().show_splash()


pm.IntegratedSplash = ProbeSplash


class ProbeGUI(pm.PackageTodoGUI):
    def __init__(self, *args, **kwargs):
        state["gui"] = self
        state["order"].append("gui")
        super().__init__(*args, **kwargs)


pm.PackageTodoGUI = ProbeGUI
QApplication.exec = lambda self: 0

try:
    pm.main()
except SystemExit as exc:
    state["exit"] = exc.code

splash = state["splash"]
print("ORDER=", state["order"])
print("SPLASH_IS_WINDOW=", int(bool(splash is not None and splash.isWindow())))
print("SPLASH_IN_MAIN_WINDOW=", int(bool(
    splash is not None and state["gui"] is not None
    and splash.parent() is state["gui"].content_container
)))
print("SPLASH_VISIBLE_ON_SHOW=", int(bool(state["visible"])))
print("EXIT=", state.get("exit"))
'''


def test_startup_uses_one_window_with_the_splash_inside(tmp_path):
    """Arranque real: una sola ventana, con el splash como hijo suyo."""
    import os
    import subprocess

    script = tmp_path / "probe_splash.py"
    script.write_text(PROBE, encoding="utf-8")
    env = dict(
        os.environ,
        QT_QPA_PLATFORM="offscreen",
        DISPLAY=os.environ.get("DISPLAY") or ":0",
        PYTHONPATH=str(ROOT),
        PM_SPLASH_MIN_SECONDS="0",
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
    assert "ORDER= ['gui', 'splash']" in result.stdout
    assert "SPLASH_IS_WINDOW= 0" in result.stdout
    assert "SPLASH_IN_MAIN_WINDOW= 1" in result.stdout
    assert "SPLASH_VISIBLE_ON_SHOW= 1" in result.stdout
    assert "EXIT= 0" in result.stdout
