# -*- coding: utf-8 -*-
"""Regresión de la traducción automática (R-8c2f4b17).

El traductor de Google devuelve ``[[[texto, ...], ...], ...]``. Un portal
cautivo, un proxy o un cambio de API puede contestar 200 con un escalar o con
listas de números; ``_auto_translate_google`` indexaba esa respuesta sin
validarla y ``TypeError`` escapaba hasta el slot de Qt que llamó a ``tr()``,
abortando la interfaz al cambiar de idioma.

La red se sustituye por una respuesta fija: sin este doble no hay forma
determinista de simular el cuerpo que devuelve el servidor.
"""

import io

import pytest

from lib import i18n


class _FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        return False


def _serve(monkeypatch, body: bytes):
    monkeypatch.setattr(
        i18n.urllib.request,
        "urlopen",
        lambda *_args, **_kwargs: _FakeResponse(body),
    )


@pytest.mark.parametrize("body", [b"5", b"true", b'"texto"', b"null", b"[1, 2]", b"[[5]]", b"[]"])
def test_unexpected_translator_payload_returns_none(monkeypatch, body):
    _serve(monkeypatch, body)
    assert i18n._auto_translate_google("hola", "es", "en") is None


def test_translator_payload_is_joined(monkeypatch):
    _serve(monkeypatch, b'[[["Hello ", "Hola ", null, null], ["world!", "mundo!", null, null]]]')
    assert i18n._auto_translate_google("Hola mundo!", "es", "en") == "Hello world!"


def test_translate_survives_unexpected_payload(monkeypatch):
    _serve(monkeypatch, b"5")
    manager = i18n.i18n
    previous_lang = manager._current_lang
    previous_auto = manager._auto_translate
    manager._current_lang = "en"
    manager._auto_translate = True
    try:
        assert manager.translate("Cadena sin traducción local zz9") == "Cadena sin traducción local zz9"
    finally:
        manager._current_lang = previous_lang
        manager._auto_translate = previous_auto
