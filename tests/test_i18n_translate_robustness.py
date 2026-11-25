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


@pytest.fixture(autouse=True)
def _clean_cooldowns():
    reset = getattr(i18n, "_reset_auto_translate_cooldowns", lambda: None)
    reset()
    yield
    reset()


def test_non_utf8_response_returns_none(monkeypatch):
    """Un cuerpo que no es UTF-8 (portal cautivo en latin-1) no debe lanzar.

    ``UnicodeDecodeError`` escapaba hasta ``tr()`` y abortaba la construcción de
    la ventana.
    """
    _serve(monkeypatch, b"\xff\xfe<html>Proxy</html>")
    assert i18n._auto_translate_google("hola", "es", "en") is None


def test_truncated_response_returns_none(monkeypatch):
    import http.client

    def _broken(*_args, **_kwargs):
        raise http.client.IncompleteRead(b"[[[", 20)

    monkeypatch.setattr(i18n.urllib.request, "urlopen", _broken)
    assert i18n._auto_translate_google("hola", "es", "en") is None


def test_repeated_transport_failures_are_cooldown_limited(monkeypatch):
    """Sin red, la misma cadena no debe pagar el timeout en cada ``tr()``."""
    attempts = {"count": 0}

    def _offline(*_args, **_kwargs):
        attempts["count"] += 1
        raise i18n.urllib.error.URLError("sin conexión")

    monkeypatch.setattr(i18n.urllib.request, "urlopen", _offline)
    for _ in range(4):
        assert i18n._auto_translate_google("hola", "es", "en") is None
    assert attempts["count"] == 1


def test_cooldown_expires_and_retries(monkeypatch):
    attempts = {"count": 0}

    def _counting(*_args, **_kwargs):
        attempts["count"] += 1
        raise i18n.urllib.error.URLError("sin conexión")

    monkeypatch.setattr(i18n.urllib.request, "urlopen", _counting)
    assert i18n._auto_translate_google("hola", "es", "en") is None
    i18n._auto_translate_cooldowns[("es", "en")] = 0.0
    assert i18n._auto_translate_google("hola", "es", "en") is None
    assert attempts["count"] == 2


def test_cooldown_is_per_language(monkeypatch):
    """Un idioma en enfriamiento no bloquea los demás."""
    def _offline(*_args, **_kwargs):
        raise i18n.urllib.error.URLError("sin conexión")

    monkeypatch.setattr(i18n.urllib.request, "urlopen", _offline)
    assert i18n._auto_translate_google("hola", "es", "en") is None
    _serve(monkeypatch, b'[[["Hallo", "hola", null, null]]]')
    assert i18n._auto_translate_google("hola", "es", "de") == "Hallo"


def test_parse_failure_keeps_retrying(monkeypatch):
    """Una respuesta 200 con formato inesperado no activa el enfriamiento."""
    _serve(monkeypatch, b"5")
    assert i18n._auto_translate_google("hola", "es", "en") is None
    assert i18n._auto_translate_cooldowns == {}


def test_translate_survives_offline(monkeypatch):
    def _offline(*_args, **_kwargs):
        raise i18n.urllib.error.URLError("sin conexión")

    monkeypatch.setattr(i18n.urllib.request, "urlopen", _offline)
    manager = i18n.i18n
    previous_lang = manager._current_lang
    previous_auto = manager._auto_translate
    manager._current_lang = "en"
    manager._auto_translate = True
    try:
        assert manager.translate("Cadena sin traducción local zz11") == "Cadena sin traducción local zz11"
    finally:
        manager._current_lang = previous_lang
        manager._auto_translate = previous_auto


class _FakeApp:
    def removeTranslator(self, *_args):
        return True

    def installTranslator(self, *_args):
        return True


def test_explicit_language_change_resets_cooldown(monkeypatch, tmp_path):
    """Elegir idioma reintenta de inmediato aunque estuviera en enfriamiento."""
    manager = i18n.i18n
    previous_app = manager._app
    previous_lang = manager._current_lang
    monkeypatch.setattr(i18n, "_app_root", lambda: str(tmp_path))
    manager._app = _FakeApp()
    manager._current_lang = "es"
    i18n._auto_translate_cooldowns[("es", "en")] = 10 ** 12
    try:
        assert manager.load_translation("en") is True
        assert i18n._auto_translate_cooldowns == {}
    finally:
        manager._app = previous_app
        manager._current_lang = previous_lang


