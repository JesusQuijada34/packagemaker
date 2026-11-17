# -*- coding: utf-8 -*-
"""Los QSS viven en ``source/qss/{qtcontrolid}.qss`` y se leen con el loader.

Estos tests fijan el contrato: un fichero por control, variantes por rol y
resolución de marcadores ``__NOMBRE__``.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_qss_dir_has_a_file_per_control():
    from lib import qss_loader

    controls = qss_loader.available_controls()
    for expected in ("qmainwindow", "qpushbutton", "qlineedit", "qcheckbox", "qlabel"):
        assert expected in controls, f"falta source/qss/{expected}.qss"


def test_read_qss_file_strips_role_markers_when_single_role():
    from lib import qss_loader

    text = qss_loader.read_qss_file("qcheckbox")
    assert "@role" not in text
    assert "QCheckBox::indicator" in text


def test_read_qss_file_requires_role_when_variants_exist():
    from lib import qss_loader

    try:
        qss_loader.read_qss_file("qpushbutton")
    except ValueError as exc:
        assert "variantes" in str(exc)
    else:  # pragma: no cover - sólo si se rompe el contrato
        raise AssertionError("qpushbutton define variantes; debía exigir un rol")


def test_roles_are_isolated():
    from lib import qss_loader

    primary = qss_loader.read_qss_file("qpushbutton", "primary")
    secondary = qss_loader.read_qss_file("qpushbutton", "secondary")
    assert "border-radius: __PILL_RADIUS__px" in primary
    assert "border-radius: __CONTROL_RADIUS__px" in secondary
    assert primary != secondary


def test_unknown_control_raises():
    from lib import qss_loader

    try:
        qss_loader.read_qss_file("qnosuchcontrol")
    except FileNotFoundError:
        pass
    else:  # pragma: no cover
        raise AssertionError("un control inexistente debía lanzar FileNotFoundError")


def test_render_resolves_markers_without_touching_css_braces():
    from lib import qss_loader

    out = qss_loader.render("QWidget { color: __ACCENT__; }", {"ACCENT": "#E81123"})
    assert out == "QWidget { color: #E81123; }"


def test_every_builder_resolves_all_markers():
    """Ningún builder debe devolver un marcador ``__NOMBRE__`` sin resolver."""
    import re

    from lib import design_tokens as tokens
    from lib import fluent_theme as theme

    builders = [
        tokens.window_qss(),
        tokens.input_qss(),
        tokens.combo_qss(),
        tokens.primary_button_qss(),
        tokens.secondary_button_qss(),
        tokens.uwp_button_qss(),
        tokens.destructive_button_qss(),
        tokens.checkbox_qss(),
        tokens.radio_qss(),
        tokens.slider_qss(),
        tokens.section_label_qss(),
        tokens.title_qss(),
        tokens.mono_value_qss(),
        tokens.card_qss(),
        tokens.sidebar_qss(True, tokens.ACCENT),
        tokens.sidebar_qss(False, tokens.ACCENT),
        theme.applyget("#0078D4", True),
        theme.applyget("#0078D4", False),
        theme.application_stylesheet(True, "#0078D4"),
        theme.application_stylesheet(False, "#0078D4"),
        theme.conf_field_stylesheet(),
        theme.conf_field_stylesheet(readonly=True),
        theme.sidebar_stylesheet(True),
        theme.sidebar_button_stylesheet(True),
        theme.checkbox_stylesheet(),
    ]
    for index, sheet in enumerate(builders):
        assert sheet, f"builder {index} devolvió una hoja vacía"
        leftover = re.findall(r"__[A-Z_]+__", sheet)
        assert not leftover, f"builder {index} deja marcadores: {leftover[:3]}"
