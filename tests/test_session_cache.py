# -*- coding: utf-8 -*-
"""Caché cifrada de sesión y arranque sin red (§3.2 de bugs.txt).

El bug reportado: ``pm.data`` mostraba la muralla de login aunque hubiera
sesión, y al pulsar cargaba datos viejos. La corrección guarda una copia
cifrada del token y del perfil y la usa para restaurar la sesión, incluso sin
red. Estos tests ejercitan el código real (cifrado, respaldo, distinción entre
credencial inválida y falta de conexión) sin tocar la red.
"""

import urllib.error

import pytest


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    """Aísla pm.data y la caché de sesión en un directorio temporal."""
    from lib import pm_data, session_cache

    monkeypatch.setattr(pm_data, "_data_dir", lambda: tmp_path)
    monkeypatch.setattr(session_cache, "_data_dir", lambda: tmp_path)
    store = pm_data.PMDataStore(path=tmp_path / "pm.data")
    monkeypatch.setattr(pm_data, "_store", store)
    return tmp_path


def test_session_cache_roundtrip_and_no_plaintext(isolated):
    from lib import session_cache

    assert session_cache.save_session("ghp_secret_token", {"login": "octocat", "name": "Octo"})
    loaded = session_cache.load_session()
    assert loaded is not None
    token, profile = loaded
    assert token == "ghp_secret_token"
    assert profile["login"] == "octocat"

    raw = (isolated / "session.cache").read_bytes()
    assert b"ghp_secret_token" not in raw
    assert b"octocat" not in raw


def test_session_cache_rejects_tampered_blob(isolated):
    from lib import session_cache

    session_cache.save_session("ghp_token", {"login": "octocat"})
    path = isolated / "session.cache"
    blob = bytearray(path.read_bytes())
    blob[-1] ^= 0xFF  # altera el último byte del criptograma
    path.write_bytes(bytes(blob))
    assert session_cache.load_session() is None


def test_clear_session_removes_cache(isolated):
    from lib import session_cache

    session_cache.save_session("ghp_token", {"login": "octocat"})
    assert session_cache.load_session() is not None
    session_cache.clear_session()
    assert session_cache.load_session() is None


def test_persist_and_restore_repopulates_pm_data(isolated):
    from lib import github_identity
    from lib.github_identity import GitHubProfile

    profile = GitHubProfile(login="JesusQuijada34", name="Jesus Quijada", email="j@x.io")
    github_identity.persist_session("ghp_live", profile)

    # Simula que pm.data perdió la sesión (lectura fallida o clave ausente).
    store = github_identity._store()
    for key in (
        github_identity.TOKEN_KEY,
        github_identity.LOGIN_KEY,
        github_identity.NAME_KEY,
        github_identity.EMAIL_KEY,
    ):
        store.remove_user(key)
    store.save()
    assert not github_identity.load_profile().login

    restored = github_identity.restore_cached_session()
    assert restored is not None
    assert restored.login == "JesusQuijada34"
    assert github_identity.load_token() == "ghp_live"
    assert github_identity.has_cached_session()


def test_load_token_falls_back_to_encrypted_cache(isolated):
    from lib import github_identity, session_cache

    session_cache.save_session("ghp_from_cache", {"login": "octocat"})
    # pm.data sin token: el respaldo cifrado debe responder.
    assert github_identity.load_token() == "ghp_from_cache"


def test_clear_identity_also_clears_encrypted_cache(isolated):
    from lib import github_identity
    from lib.github_identity import GitHubProfile

    github_identity.persist_session("ghp_live", GitHubProfile(login="octocat"))
    github_identity.clear_identity()
    assert github_identity.load_token() == ""
    assert not github_identity.has_cached_session()


def test_network_failure_is_offline_not_invalid_credential(monkeypatch):
    """Sin red, el token no se trata como inválido (no se borra la sesión)."""
    from lib import github_identity

    def boom(*_args, **_kwargs):
        raise urllib.error.URLError("network down")

    monkeypatch.setattr(github_identity.urllib.request, "urlopen", boom)
    with pytest.raises(github_identity.GitHubOfflineError):
        github_identity.fetch_profile("ghp_token")
    # La subclase sigue siendo capturable como error de identidad.
    assert issubclass(github_identity.GitHubOfflineError, github_identity.GitHubIdentityError)


def test_has_cached_session_requires_token_and_login(isolated):
    from lib import github_identity, session_cache

    assert not github_identity.has_cached_session()
    session_cache.save_session("ghp_token", {"login": ""})
    assert not github_identity.has_cached_session()
    session_cache.save_session("ghp_token", {"login": "octocat"})
    assert github_identity.has_cached_session()


def test_landing_reset_and_reveal_api(isolated):
    """El landing expone la secuencia de cierre de sesión (fase 3.2)."""
    pytest.importorskip("PyQt6.QtWidgets")
    from lib.github_login_landing import GitHubLoginLanding

    landing = GitHubLoginLanding()
    try:
        landing.username_input.setText("octocat")
        landing.token_input.setText("ghp_token")
        landing.reset_to_initial_state()
        assert landing.username_input.text() == ""
        assert landing.token_input.text() == ""
        assert landing.login_button.isEnabled()
        assert hasattr(landing, "reveal")
    finally:
        landing.close()
