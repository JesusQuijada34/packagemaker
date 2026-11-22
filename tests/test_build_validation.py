# -*- coding: utf-8 -*-
"""Regresiones de la validación estricta antes de compilar (bugs.txt Fase 1.1).

El formulario de compilación rellenaba los huecos con ``influent``,
``mycoolapp`` y ``1.0``, así que al dejar un campo vacío el sistema compilaba
con los datos del proyecto anterior en vez de bloquearse.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def validate(*args):
    from lib.blindcubeEngine.build_validation import validate_build_fields

    return validate_build_fields(*args)


def fields(errors):
    return [error.field for error in errors]


def test_all_empty_fields_are_reported():
    assert fields(validate("", "", "")) == ["empresa", "nombre", "version"]


def test_only_missing_version_is_reported():
    assert fields(validate("influent", "mycoolapp", "")) == ["version"]


def test_whitespace_only_counts_as_empty():
    assert fields(validate("   ", "  ", "  ")) == ["empresa", "nombre", "version"]


def test_valid_data_passes():
    assert validate("influent", "mycoolapp", "1.0", "Danenone") == []


@pytest.mark.parametrize("version", ["1", "v2", "1.0", "3.2.7", "10.20.30"])
def test_free_form_numeric_versions_are_accepted(version):
    """El campo es libre: ``normalize_version_base`` completa el menor."""
    assert validate("influent", "mycoolapp", version) == []


@pytest.mark.parametrize(
    "version",
    [
        "1.0-26.11-22.00",
        "v1.0-26.11-22.00",
        "3.2.7-26.05-20.13",
        "v3.2.7-26.05-20.13-AlphaCube",
    ],
)
def test_canonical_versions_with_timestamp_are_accepted(version):
    """La versión exacta de ``details.xml`` no debe bloquear la compilación.

    El campo se rellena a veces pegando el valor canónico completo
    (``v1.0-26.11-22.00``); el validador lo rechazaba como «X.x» aunque
    ``ProjectNameFormatter`` y ``normalize_version_base`` lo aceptan.
    """
    assert validate("influent", "mycoolapp", version) == []


@pytest.mark.parametrize(
    "version", ["1.0-26.11", "1.0-2026.11-22.00", "1.0-26.11-22.00-StoneCube"]
)
def test_malformed_timestamp_versions_are_rejected(version):
    assert fields(validate("influent", "mycoolapp", version)) == ["version"]


def test_canonical_version_normalizes_to_base_for_the_build():
    from lib.projectNameFormatter import ProjectNameFormatter

    assert ProjectNameFormatter.normalize_version_base("v1.0-26.11-22.00") == "1.0"
    assert ProjectNameFormatter.normalize_version_base("3.2.7-26.05-20.13") == "3.2.7"


@pytest.mark.parametrize("version", ["abc", "uno", "1.x", "v", "-1"])
def test_non_numeric_versions_are_rejected(version):
    assert fields(validate("influent", "mycoolapp", version)) == ["version"]


@pytest.mark.parametrize("publisher", ["in fluent", "in.fluent", "acme!", "a/b"])
def test_unsafe_publisher_segments_are_rejected(publisher):
    assert fields(validate(publisher, "mycoolapp", "1.0")) == ["empresa"]


def test_unknown_platform_is_rejected():
    assert fields(validate("influent", "mycoolapp", "1.0", "Windows XP")) == [
        "plataforma"
    ]


def test_platform_aliases_are_accepted():
    assert validate("influent", "mycoolapp", "1.0", "Linux") == []


def test_messages_are_human_readable():
    from lib.blindcubeEngine.build_validation import format_errors

    text = format_errors(validate("", "", ""))
    assert text.count("•") == 3
    assert "{" not in text and "}" not in text


def test_build_action_does_not_inherit_ghost_values():
    """``build_package_action`` ya no cae a ``mycoolapp``/``influent``."""
    source = (ROOT / "packagemaker.py").read_text(encoding="utf-8")
    build = source.split("def build_package_action")[1].split("def _on_build_progress")[0]
    assert 'or "influent"' not in build
    assert 'or "mycoolapp"' not in build
    assert "validate_build_fields" in build


def test_create_action_does_not_inherit_ghost_values():
    source = (ROOT / "packagemaker.py").read_text(encoding="utf-8")
    create = source.split("def on_github_verification_finished")[1].split("def ")[0]
    assert 'or "influent"' not in create
    assert 'or "mycoolapp"' not in create
    assert "validate_build_fields" in create
