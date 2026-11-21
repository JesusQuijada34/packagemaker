"""Regresión: la cabecera .iflapp debe coincidir con su details.xml (R-2a7f6b41).

``create_package`` reescribe ``<platform>`` con la plataforma objetivo, pero la
cabecera del contenedor conservaba la plataforma declarada del proyecto. Un
proyecto ``AlphaCube`` compilado en Linux producía un ``.iflapp`` cuyo
``--inspect`` mostraba ``AlphaCube`` y, en el mismo contenedor, un
``details.xml`` con ``Danenone``.
"""

from __future__ import annotations

from lib.BuildThread import package_identity

METADATA = {
    "publisher": "Influent",
    "app": "demo",
    "name": "Demo",
    "version": "v1.0-26.11-14.10",
    "platform": "AlphaCube",
    "author": "JesusQuijada34",
}


def test_packaged_platform_overrides_declared_platform():
    details = b"<app><platform>Danenone</platform><name>demo</name></app>"
    identity = package_identity(METADATA, details)
    assert identity["platform"] == "Danenone"
    assert identity["publisher"] == "Influent"
    assert identity["app"] == "demo"
    # El diccionario original no se muta.
    assert METADATA["platform"] == "AlphaCube"


def test_missing_details_keeps_metadata():
    assert package_identity(METADATA, None)["platform"] == "AlphaCube"


def test_corrupt_details_keeps_metadata():
    assert package_identity(METADATA, b"<app><platform>")["platform"] == "AlphaCube"


def test_details_without_platform_keeps_metadata():
    assert package_identity(METADATA, b"<app><name>demo</name></app>")["platform"] == "AlphaCube"
