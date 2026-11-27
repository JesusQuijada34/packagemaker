# -*- coding: utf-8 -*-
"""Regresión R-3a9c6e28: la interfaz del updater nace en el hilo de trabajo.

``ciclo_embestido()`` lanzaba ``verificar()`` en un hilo y era ahí donde se
construía la ``QApplication``. Qt exige que la interfaz viva en el hilo
principal; en Windows eso puede abortar el proceso o dejar la ventana de
instalación sin pintar.

El caso carga la plantilla real con un PyQt6 falso que anota en qué hilo se
construye la ``QApplication`` y la ventana.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
import threading
import time
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "src" / "templates" / "project" / "updater.py.template"

APP_THREADS: list = []
WINDOW_THREADS: list = []
PENDING_SLOTS: list = []


class _Callable:
    """Objeto llamable que acepta cualquier atributo (stub de Qt)."""

    def __call__(self, *args, **kwargs):
        return None

    def __getattr__(self, name):
        return _Callable()


class _Nested:
    """Espacio de nombres encadenable: ``Qt.WindowType.FramelessWindowHint``."""

    def __getattr__(self, name):
        return _Nested()


class _Widget:
    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        return _Callable()


class _Signal:
    """Señal diferida: imita la conexión encolada entre hilos de Qt."""

    def __init__(self, *args):
        self._slots = []

    def connect(self, slot):
        self._slots.append(slot)

    def emit(self, *args):
        for slot in list(self._slots):
            PENDING_SLOTS.append((slot, args))


class _QApplication(_Widget):
    _instance = None

    def __init__(self, *args, **kwargs):
        APP_THREADS.append(threading.current_thread())
        _QApplication._instance = self

    @classmethod
    def instance(cls):
        return cls._instance

    @classmethod
    def primaryScreen(cls):
        return None

    def exec(self):
        deadline = time.time() + 10
        while time.time() < deadline:
            if PENDING_SLOTS:
                slot, args = PENDING_SLOTS.pop(0)
                slot(*args)
                continue
            if WINDOW_THREADS:
                return 0
            time.sleep(0.01)
        return 0

    def quit(self):
        pass


class _QMainWindow(_Widget):
    def __init__(self, *args, **kwargs):
        WINDOW_THREADS.append(threading.current_thread())


class _QTimer(_Widget):
    @staticmethod
    def singleShot(*args, **kwargs):
        return None


def _install_fake_qt(monkeypatch):
    qt = types.ModuleType("PyQt6")
    widgets = types.ModuleType("PyQt6.QtWidgets")
    gui = types.ModuleType("PyQt6.QtGui")
    core = types.ModuleType("PyQt6.QtCore")

    widgets.QApplication = _QApplication
    widgets.QMainWindow = _QMainWindow
    widgets.QWidget = _Widget
    widgets.QVBoxLayout = _Widget
    widgets.QLabel = _Widget
    widgets.QProgressBar = _Widget

    gui.QFont = _Widget
    gui.QIcon = _Widget
    gui.QPixmap = _Widget
    gui.QColor = _Widget

    core.Qt = _Nested()
    core.QThread = _Widget
    core.QObject = _Widget
    core.QTimer = _QTimer
    core.pyqtSignal = _Signal

    monkeypatch.setitem(sys.modules, "PyQt6", qt)
    monkeypatch.setitem(sys.modules, "PyQt6.QtWidgets", widgets)
    monkeypatch.setitem(sys.modules, "PyQt6.QtGui", gui)
    monkeypatch.setitem(sys.modules, "PyQt6.QtCore", core)


def _load_template():
    loader = importlib.machinery.SourceFileLoader("pm_template_updater", str(TEMPLATE))
    spec = importlib.util.spec_from_loader("pm_template_updater", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    # leviathan_ui puede estar instalado en el entorno; la ventana se prueba
    # con los stubs de Qt, no con la librería real.
    module.HAS_LEVIATHAN = False
    return module


@pytest.fixture(autouse=True)
def _clean_state():
    APP_THREADS.clear()
    WINDOW_THREADS.clear()
    PENDING_SLOTS.clear()
    yield
    APP_THREADS.clear()
    WINDOW_THREADS.clear()
    PENDING_SLOTS.clear()


def _update():
    return {
        "datos": {
            "app": "demo",
            "version": "v1.0-26.11-10.05",
            "platform": "Danenone",
            "author": "JesusQuijada34",
            "publisher": "Influent",
        },
        "remoto": "v1.1-26.12-10.00",
        "tipo": "IFLAPP_PACKAGE",
        "url": "https://example.invalid/demo.iflapp",
        "nombre": "demo.iflapp",
    }


def test_watcher_mode_builds_gui_on_main_thread(tmp_path, monkeypatch):
    _install_fake_qt(monkeypatch)
    module = _load_template()
    module.CHECK_INTERVAL = 0.01
    monkeypatch.setattr(module, "check_update", _update)
    monkeypatch.chdir(tmp_path)

    app = module.QApplication([])
    module.ciclo_embestido(app)

    deadline = time.time() + 10
    while not WINDOW_THREADS and time.time() < deadline:
        if PENDING_SLOTS:
            slot, args = PENDING_SLOTS.pop(0)
            slot(*args)
        else:
            time.sleep(0.01)

    main_thread = threading.main_thread()
    assert APP_THREADS == [main_thread], "la QApplication sólo puede nacer en el hilo principal"
    assert WINDOW_THREADS, "no se abrió la ventana de instalación"
    assert all(t is main_thread for t in WINDOW_THREADS), "ventana fuera del hilo principal"


def test_verificar_does_not_create_qapplication(tmp_path, monkeypatch):
    _install_fake_qt(monkeypatch)
    module = _load_template()
    monkeypatch.setattr(module, "check_update", _update)
    monkeypatch.chdir(tmp_path)

    datos, url = module.verificar()

    assert datos["app"] == "demo"
    assert url == "https://example.invalid/demo.iflapp"
    assert APP_THREADS == [], "verificar() no debe crear la QApplication"
