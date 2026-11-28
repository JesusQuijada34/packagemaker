# -*- coding: utf-8 -*-
"""Barra de actividad marquee y subtítulo de la barra de acciones (issue #11)."""

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from lib import activity_bar as ab  # noqa: E402
from lib import page_action_bar as pab  # noqa: E402


@pytest.fixture()
def _app(_qt_app):
    return _qt_app


def test_activity_bar_starts_idle_and_toggles(_app):
    bar = ab.ActivityBar()
    assert bar.height() == ab.BAR_HEIGHT
    assert bar.is_active() is False

    bar.start()
    assert bar.is_active() is True

    bar.stop()
    assert bar.is_active() is False


def test_activity_bar_start_is_idempotent(_app):
    bar = ab.ActivityBar()
    bar.start()
    bar.start()
    assert bar.is_active() is True
    bar.stop()


def test_action_bar_carries_activity_bar_and_subtitle(_app):
    page = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(page)
    action_bar, title = pab.install_page_action_bar(layout, "Título")

    assert title.text() == "Título"
    assert action_bar.activity_bar.is_active() is False
    # El subtítulo nace oculto: cada página lo rellena al mostrarse.
    assert action_bar.subtitle_label.isHidden()

    pab.set_action_bar_subtitle(action_bar, "Detalle de la página")
    assert action_bar.subtitle_label.text() == "Detalle de la página"
    assert not action_bar.subtitle_label.isHidden()

    pab.set_action_bar_busy(action_bar, True)
    assert action_bar.activity_bar.is_active() is True
    pab.set_action_bar_busy(action_bar, False)
    assert action_bar.activity_bar.is_active() is False


def test_subtitle_lives_outside_the_pill(_app):
    """El subtítulo es un hermano de la barra, no un hijo: no hereda su fondo."""
    page = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(page)
    action_bar, _title = pab.install_page_action_bar(layout, "Título")

    subtitle = action_bar.subtitle_label
    assert subtitle.parent() is page
    assert subtitle is not action_bar
    assert layout.indexOf(subtitle) == layout.indexOf(action_bar) + 2


def test_subtitle_renders_the_catalog_markdown(_app):
    """R-8b5c1d47: los catálogos usan ``**negrita**`` y `` `código` ``.

    El QLabel no interpreta Markdown, así que los asteriscos y las comillas
    invertidas salían literales en la descripción de la página de creación.
    """
    page = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(page)
    action_bar, _title = pab.install_page_action_bar(layout, "Título")

    pab.set_action_bar_subtitle(
        action_bar, "Metadatos para el ecosistema **Influent OS** con `.iflapp`."
    )
    text = action_bar.subtitle_label.text()
    assert "<b>Influent OS</b>" in text
    assert "**" not in text
    assert "`" not in text
    assert "monospace" in text


def test_subtitle_escapes_html_and_leaves_plain_text_alone(_app):
    page = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(page)
    action_bar, _title = pab.install_page_action_bar(layout, "Título")

    pab.set_action_bar_subtitle(action_bar, "Usa <ruta> y 1 < 2")
    assert "<ruta>" not in action_bar.subtitle_label.text()
    assert "&lt;ruta&gt;" in action_bar.subtitle_label.text()

    pab.set_action_bar_subtitle(action_bar, "Detalle de la página")
    assert action_bar.subtitle_label.text() == "Detalle de la página"


def test_activity_bar_paints_in_both_states(_app):
    """Pintar no debe lanzar ni en reposo ni animada."""
    from PyQt6.QtGui import QPixmap

    bar = ab.ActivityBar()
    bar.resize(240, ab.BAR_HEIGHT)
    pixmap = QPixmap(240, ab.BAR_HEIGHT)

    bar.render(pixmap)
    idle = pixmap.toImage()

    bar.start()
    bar._advance()
    bar.render(pixmap)
    active = pixmap.toImage()

    assert idle.pixelColor(0, 0) != active.pixelColor(0, 0)
    bar.stop()
