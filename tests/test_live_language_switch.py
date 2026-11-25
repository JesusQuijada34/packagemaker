# -*- coding: utf-8 -*-
"""Cambiar de idioma debe retraducir la interfaz en el acto (R-8a3f1c72).

El reporte del propietario: al pasar a inglés sólo cambiaban el sidebar, su
descripción, el interruptor de sandbox y el selector de motor; las páginas de
creación, compilación, configuración y «Acerca de» seguían en español.

Estos tests usan la ventana real y cuentan cuántos textos visibles quedan sin
traducir. Se permite una lista corta de marcas y valores que son iguales en
todos los idiomas por diseño.
"""

import os
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PyQt6.QtWidgets")

from PyQt6.QtWidgets import (  # noqa: E402
    QApplication,
    QCheckBox,
    QComboBox,
    QGroupBox,
    QLabel,
    QPushButton,
    QRadioButton,
    QTabWidget,
)

_APP = None


def _app():
    global _APP
    if QApplication.instance() is None:
        _APP = QApplication([])
    return QApplication.instance()


# Nombres propios, marcas, licencia y valores: iguales en todos los idiomas.
_ALLOWED = {
    "influent package maker",
    "influent package maker v3.2.7-26.05-20.13",
    "blindcube",
    "blindcube v2.1",
    "gnu gpl v3",
    "qt 6.12.1 (pyqt6)",
    "jesus daviel",
    "moonfix",
    "aide",
    "linux",
    "windows (knosthalij)",
    "linux (danenone)",
    "general",
    "framework:",
}


def _visible_texts(win):
    widgets = (
        win.findChildren(QLabel)
        + win.findChildren(QPushButton)
        + win.findChildren(QCheckBox)
        + win.findChildren(QRadioButton)
        + win.findChildren(QGroupBox)
    )
    texts = {}
    for w in widgets:
        try:
            t = (w.text() or "").strip()
        except (RuntimeError, AttributeError):
            continue
        if t:
            texts[id(w)] = t
    for combo in win.findChildren(QComboBox):
        for i in range(combo.count()):
            texts[(id(combo), i)] = combo.itemText(i).strip()
    for tabs in win.findChildren(QTabWidget):
        for i in range(tabs.count()):
            texts[(id(tabs), i)] = tabs.tabText(i).strip()
    return {k: v for k, v in texts.items() if v}


def _untranslated(win):
    """Textos que siguen en español tras cambiar a inglés."""
    import lib.i18n as i18n

    i18n.i18n.load_translation("es")
    win.apply_ui_language()
    before = _visible_texts(win)

    i18n.i18n.load_translation("en")
    win.apply_ui_language()
    after = _visible_texts(win)

    stuck = []
    for key, text in before.items():
        if after.get(key) != text:
            continue  # sí cambió
        lowered = text.lower()
        if lowered in _ALLOWED:
            continue
        if not re.search(r"[A-Za-zÁÉÍÓÚáéíóúñÑ]{3,}", text):
            continue
        if text.startswith(("http", "/", "C:", "~")):
            continue
        # Valores crudos del sistema (ids, rutas, versiones, nombres de clave)
        if re.fullmatch(r"[0-9a-fA-F-]{8,}", text) or " " not in text and "_" in text:
            continue
        if re.fullmatch(r"[\d.\-+]+", text):
            continue
        stuck.append(text)
    return stuck, before


@pytest.fixture(scope="module")
def window():
    _app()
    import lib.i18n as i18n
    import packagemaker as pm

    previous = i18n.i18n.get_current_lang()
    i18n.i18n.initialize(QApplication.instance(), "es")
    win = pm.PackageTodoGUI()
    yield win
    # Dejar el idioma como estaba: otros tests comparan textos y fallarían.
    i18n.i18n.load_translation(previous)
    win.close()


def test_switching_language_retranslates_almost_everything(window):
    stuck, before = _untranslated(window)
    assert before, "la ventana no expone textos: el test no probaría nada"
    assert len(stuck) <= 3, f"quedan {len(stuck)} textos sin traducir: {stuck}"


def test_pages_keep_the_users_typed_text(window):
    """Retraducir no debe pisar lo que el usuario escribió en un campo."""
    from PyQt6.QtWidgets import QLineEdit

    import lib.i18n as i18n

    field = window.findChild(QLineEdit, "") or None
    if field is None:
        fields = [f for f in window.findChildren(QLineEdit) if not f.isReadOnly()]
        field = fields[0] if fields else None
    if field is None:
        pytest.skip("la ventana no tiene campos editables")

    i18n.i18n.load_translation("es")
    field.setText("mi empresa S.L.")
    i18n.i18n.load_translation("en")
    window.apply_ui_language()
    assert field.text() == "mi empresa S.L."


def test_reverse_index_resolves_every_language():
    """El índice inverso encuentra la clave venga el texto en el idioma que venga."""
    from lib import live_i18n

    live_i18n.invalidate_cache()
    assert live_i18n.key_for("Diagnosticar") == "moonfix.scan"
    assert live_i18n.key_for("Diagnose") == "moonfix.scan"
    assert live_i18n.key_for("診断") == "moonfix.scan"
    assert live_i18n.key_for("texto que no es una traducción") is None


def test_templates_are_resolved_not_left_in_spanish():
    """«Versión 3.2.7…» es una plantilla: también debe retraducirse."""
    from lib import live_i18n

    live_i18n.invalidate_cache()
    assert live_i18n.key_for("Versión 3.2.7-26.05-20.13") == "about.version"
    assert live_i18n.key_for("Version 3.2.7-26.05-20.13") == "about.version"
