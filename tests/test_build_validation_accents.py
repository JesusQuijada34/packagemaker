# -*- coding: utf-8 -*-
"""La puerta estricta debe aceptar los nombres que la ley de nombres admite.

``validate_build_fields`` juzgaba el texto tal cual, mientras
``ProjectNameFormatter`` translitera los acentos (``Jesús`` → ``Jesus``,
``Ñandú`` → ``Nandu``). Un fabricante o nombre interno con acentos quedaba
bloqueado en «Crear proyecto» y en «Compilar» con «usa solo letras, números o
guiones», aunque el nombre canónico resultante fuera perfectamente válido.
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


@pytest.mark.parametrize(
    "publisher", ["Jesús", "jesús", "Ñandú-Labs", "Andrés"]
)
def test_accented_publishers_are_accepted(publisher):
    assert validate(publisher, "mycoolapp", "1.0", "AlphaCube") == []


@pytest.mark.parametrize("app_id", ["Ñandú", "café", "Añejo"])
def test_accented_app_ids_are_accepted(app_id):
    assert validate("Influent", app_id, "1.0") == []


def test_accented_fields_match_the_canonical_name():
    """El validador acepta exactamente lo que el formatter sabe normalizar."""
    from lib.projectNameFormatter import ProjectNameFormatter

    folder = ProjectNameFormatter.format_project_folder(
        "Jesús", "Ñandú", "1.0", "AlphaCube", timestamp="26.11-06.00"
    )
    assert folder == "Jesus.nandu.v1.0-26.11-06.00-AlphaCube"
    assert validate("Jesús", "Ñandú", "1.0", "AlphaCube") == []


def test_unsafe_segments_are_still_rejected():
    assert fields(validate("in fluent", "mycoolapp", "1.0")) == ["empresa"]
    assert fields(validate("My Company.", "mycoolapp", "1.0")) == ["empresa"]
    assert fields(validate("a_b", "mycoolapp", "1.0")) == ["empresa"]
    assert fields(validate("Influent", "my app", "1.0")) == ["nombre"]


def test_combining_marks_alone_still_count_as_empty():
    # Una marca combinante suelta desaparece al transliterar: es un campo vacío.
    assert fields(validate("\u0301", "mycoolapp", "1.0")) == ["empresa"]


def test_accented_creation_produces_a_canonical_folder(tmp_path):
    """Reproducción del flujo real: crear con acentos deja un nombre canónico."""
    from lib.makeselfEngine.template_engine import (
        create_project_from_templates,
        templates_available,
    )

    if not templates_available():
        pytest.skip("plantillas no disponibles en este bundle")

    project = tmp_path / "Jesus.nandu.v1.0-26.11-06.00-AlphaCube"
    create_project_from_templates(
        project,
        "Jesús",
        "Ñandú",
        "Ñandú App",
        "Jesus",
        "AlphaCube",
        version_base="1.0",
        timestamp="26.11-06.00",
    )
    details = (project / "details.xml").read_text(encoding="utf-8")
    assert "<publisher>Jesus</publisher>" in details
    assert "<app>nandu</app>" in details
    # Los metadatos escritos vuelven a pasar la puerta estricta al compilar.
    assert validate("Jesus", "nandu", "1.0", "AlphaCube") == []
