# -*- coding: utf-8 -*-
"""R-7c4a1e95: guardar ajustes no debe re-pulir hojas de estilo idénticas.

Reaplicar el tema tras guardar volvía a llamar a ``setStyleSheet`` con la misma
hoja en la página central y en el resto de widgets. Qt re-pule entonces todo el
árbol aunque no cambie un píxel: medido en offscreen, ~120 ms por guardado de
apariencia (frente a ~5 ms con la hoja idempotente). El guardado de archivos no
era el culpable (``store.save`` tarda ~0,5 ms).
"""

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PyQt6.QtWidgets")

from PyQt6.QtCore import QEvent, QObject  # noqa: E402
from PyQt6.QtWidgets import QApplication, QWidget  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app
    app.processEvents()


@pytest.fixture
def isolated_store(tmp_path, monkeypatch):
    from lib import pm_data

    monkeypatch.setattr(pm_data, "_data_dir", lambda: tmp_path)
    store = pm_data.PMDataStore(path=tmp_path / "pm.data")
    monkeypatch.setattr(pm_data, "_store", store)
    return store


@pytest.fixture
def window(qapp, isolated_store):
    import packagemaker as pm

    win = pm.PackageTodoGUI()
    yield win
    win.close()
    qapp.processEvents()


class _StyleCounter(QWidget):
    """Widget real que cuenta los eventos ``StyleChange`` de Qt."""

    def __init__(self):
        super().__init__()
        self.style_changes = 0

    def event(self, event):
        if event.type() == QEvent.Type.StyleChange:
            self.style_changes += 1
        return super().event(event)


class _StyleFilter(QObject):
    def __init__(self):
        super().__init__()
        self.style_changes = 0

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.StyleChange:
            self.style_changes += 1
        return False


def test_set_qss_skips_an_identical_stylesheet(qapp):
    from lib.fluent_theme import set_qss

    widget = _StyleCounter()
    widget.show()
    qapp.processEvents()

    set_qss(widget, "color: red;")
    qapp.processEvents()
    assert widget.style_changes == 1

    set_qss(widget, "color: red;")
    qapp.processEvents()
    assert widget.style_changes == 1

    set_qss(widget, "color: blue;")
    qapp.processEvents()
    assert widget.style_changes == 2
    assert widget.styleSheet() == "color: blue;"


def test_set_qss_append_keeps_accumulating_and_stays_idempotent(qapp):
    from lib.fluent_theme import set_qss

    widget = _StyleCounter()
    widget.show()
    qapp.processEvents()

    set_qss(widget, "color: red;")
    set_qss(widget, "font-size: 11px;", append=True)
    qapp.processEvents()

    assert "color: red;" in widget.styleSheet()
    assert "font-size: 11px;" in widget.styleSheet()

    changes = widget.style_changes
    set_qss(widget, widget.styleSheet())
    qapp.processEvents()

    assert widget.style_changes == changes


def test_accent_width_save_does_not_repolish_the_page(qapp, window, isolated_store):
    import packagemaker as pm

    filter_ = _StyleFilter()
    window.central.installEventFilter(filter_)

    slider = window.conf_sidebar_accent_slider
    previous = slider.value()
    new_value = previous + 1 if previous < slider.maximum() else previous - 1
    slider.setValue(new_value)
    qapp.processEvents()
    assert filter_.style_changes == 0

    window._save_app_config_compact(quiet=True)
    qapp.processEvents()

    # El ajuste sí se guardó y la apariencia cambió: el plan pide reaplicar el
    # tema. Lo que ya no ocurre es reinstalar la hoja idéntica de la página.
    assert isolated_store.get_user_int("sidebar_accent_width", 3) == new_value
    assert pm.settings_appearance_state(isolated_store)["accent_width"] == new_value
    assert filter_.style_changes == 0


def test_real_accent_change_still_repaints(qapp, window, isolated_store):
    filter_ = _StyleFilter()
    window.central.installEventFilter(filter_)
    before = window.central.styleSheet()

    isolated_store.set_user("custom_accent_color", "#12AB34")
    window.apply_theme()
    qapp.processEvents()

    assert filter_.style_changes >= 1
    assert window.central.styleSheet() != before
