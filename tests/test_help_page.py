# -*- coding: utf-8 -*-
"""Página de ayuda global (Q-021, issue #11).

El propietario pidió «un apartado de ayuda relacionado con toda la app». Estos
tests fijan lo que puede romperse sin tocar el engine: el manifiesto del addon,
los textos en los 14 catálogos, el buscador y la retraducción.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

pytest.importorskip("PyQt6.QtWidgets")

from PyQt6.QtWidgets import QApplication  # noqa: E402

import lib.i18n as i18n  # noqa: E402
from lib import addons_engine  # noqa: E402

_APP = None


def _ensure_app():
    """Qt aborta el proceso si la QApplication se recolecta a mitad de test."""
    global _APP
    if _APP is None:
        _APP = QApplication.instance() or QApplication(sys.argv)
    return _APP


@pytest.fixture()
def qt_app():
    app = _ensure_app()
    i18n.i18n.initialize(app, "es")
    return app


@pytest.fixture()
def page(qt_app):
    from lib.help_page import HelpPage

    widget = HelpPage()
    yield widget
    widget.deleteLater()


def _flat(data, prefix=""):
    out = {}
    for key, value in data.items():
        if isinstance(value, dict):
            out.update(_flat(value, prefix + key + "."))
        else:
            out[prefix + key] = value
    return out


def test_manifest_is_shipped_and_valid():
    addons = {
        addon.id: addon
        for addon in addons_engine.load_addons(ROOT / "addons", strict=True)
    }
    assert "help" in addons
    addon = addons["help"]
    assert addon.section == "tools"
    assert addon.builder == "build_help_page"
    assert addon.icon == "help"
    assert addon.label == "sidebar.help"


def test_help_icon_exists():
    from lib import app_icons

    assert "help" in app_icons.ICONS_SVG


def test_every_catalog_defines_the_help_texts():
    from lib.help_page import TOPIC_IDS

    needed = [
        "sidebar.help",
        "sidebar_desc.8",
        "help.intro",
        "help.search_placeholder",
        "help.empty",
    ]
    for topic_id in TOPIC_IDS:
        needed.append(f"help.topics.{topic_id}.title")
        needed.append(f"help.topics.{topic_id}.body")

    catalogs = {
        path.stem: _flat(json.loads(path.read_text(encoding="utf-8")))
        for path in sorted((ROOT / "lang").glob("*.json"))
    }
    missing = {
        name: [key for key in needed if key not in flat]
        for name, flat in catalogs.items()
    }
    assert all(not keys for keys in missing.values()), missing


def test_page_builds_every_topic(page):
    from lib.help_page import TOPIC_IDS

    assert page.topic_ids() == list(TOPIC_IDS)
    assert page.visible_topic_ids() == list(TOPIC_IDS)
    assert page.bar_title.text() == i18n.tr("sidebar.help")
    assert page.empty_label.isHidden()


def test_search_filters_by_title_and_body(page):
    from lib.help_page import TOPIC_IDS

    page.search_input.setText("Nuitka")
    assert page.visible_topic_ids() == ["build"]

    page.search_input.setText("HMAC")
    assert page.visible_topic_ids() == ["harden"]

    page.search_input.setText("issu")  # cuerpo del tema de reportes
    assert page.visible_topic_ids() == ["report"]

    page.search_input.clear()
    assert page.visible_topic_ids() == list(TOPIC_IDS)


def test_search_without_matches_shows_the_empty_state(page):
    page.search_input.setText("zzzz-no-existe")
    assert page.visible_topic_ids() == []
    assert not page.empty_label.isHidden()

    page.search_input.clear()
    assert page.empty_label.isHidden()


def test_retranslate_follows_the_active_language(page):
    try:
        assert page.bar_title.text() == "Ayuda"
        assert i18n.i18n.load_translation("en")
        page.retranslate()
        assert page.bar_title.text() == "Help"
        assert page.search_input.placeholderText() == "Search help"
        assert page._cards["build"][1].text() == "Build a package"
    finally:
        i18n.i18n.load_translation("es")
        page.retranslate()
    assert page.bar_title.text() == "Ayuda"
