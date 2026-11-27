# -*- coding: utf-8 -*-
"""Regresión R-6b4d2f81: las ventanas del updater no se podían construir.

``lib/coreUpdater/windows.py`` usaba ``Qt.WindowFlags(...)`` (que no existe en
PyQt6), pasaba ``is_main=True`` a un ``CustomTitleBar`` que no lo acepta y
llamaba a ``set_color()``, un método que la librería no expone. Las cuatro
ventanas morían al construirse, así que la actualización con interfaz nunca
llegaba a abrirse.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

pytest.importorskip("PyQt6.QtWidgets", reason="PyQt6 no instalado")

from PyQt6.QtCore import Qt  # noqa: E402
from PyQt6.QtWidgets import QApplication  # noqa: E402

_APP = None


def _ensure_app() -> QApplication:
    global _APP
    _APP = QApplication.instance() or QApplication([])
    return _APP


def _assert_frameless(window) -> None:
    assert window.windowFlags() & Qt.WindowType.FramelessWindowHint


def test_modern_updater_window_constructs():
    _ensure_app()
    from lib.coreUpdater import windows

    window = windows.ModernUpdaterWindow(
        {"app": "demo", "version": "v1.0-26.11-10.05", "platform": "Danenone"},
        "https://example.invalid/demo.zip",
    )
    try:
        _assert_frameless(window)
        assert window.lbl_status is not None
    finally:
        window.close()
        window.deleteLater()


def test_iflapp_installer_window_constructs(tmp_path):
    _ensure_app()
    from lib.coreUpdater import windows

    window = windows.IFLAPPInstallerWindow("demo.iflapp", str(tmp_path))
    try:
        _assert_frameless(window)
    finally:
        window.close()
        window.deleteLater()


def test_license_terms_dialog_constructs():
    _ensure_app()
    from lib.coreUpdater import windows

    dialog = windows.LicenseTermsDialog(app_name="Demo", license_text="Términos")
    try:
        _assert_frameless(dialog)
    finally:
        dialog.close()
        dialog.deleteLater()


def test_exe_installer_window_constructs():
    _ensure_app()
    from lib.coreUpdater import windows

    window = windows.EXEInstallerWindow("https://example.invalid/setup.exe", "setup.exe")
    try:
        _assert_frameless(window)
    finally:
        window.close()
        window.deleteLater()
