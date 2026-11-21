"""Pruebas de la identidad de GitHub (§5.4).

No se usa red: ``_request`` se sustituye por un doble que devuelve cargas
controladas, de modo que se ejercita el camino real de parseo, guardado en
``pm_data`` y derivación del firmante/clave.
"""

import pytest


@pytest.fixture
def store(tmp_path, monkeypatch):
    """Aísla el almacén pm_data en un directorio temporal."""
    from lib import pm_data

    monkeypatch.setattr(pm_data, "_data_dir", lambda: tmp_path)
    store = pm_data.PMDataStore(path=tmp_path / "pm.data")
    monkeypatch.setattr(pm_data, "_store", store)
    return store


def test_profile_derives_signer_and_key():
    from lib.github_identity import GitHubProfile

    profile = GitHubProfile(login="JesusQuijada34", name="Jesus Quijada")
    assert profile.display_name() == "Jesus Quijada"
    assert profile.signer_name() == "JesusQuijada34"
    assert profile.signing_key() == b"Influent.github.JesusQuijada34"


def test_guest_profile_has_no_signer():
    from lib.github_identity import GitHubProfile

    profile = GitHubProfile()
    assert profile.signer_name() == ""
    assert profile.signing_key() == b""
    assert profile.display_name() == "Invitado"


def test_save_and_load_profile_roundtrip(store):
    from lib.github_identity import GitHubProfile, load_profile, save_profile, save_token

    save_token("ghp_secret")
    save_profile(GitHubProfile(login="octocat", name="The Octocat", avatar_url="https://x/a.png"))
    loaded = load_profile()
    assert loaded.login == "octocat"
    assert loaded.name == "The Octocat"
    assert loaded.authenticated is True


def test_fetch_profile_uses_token_and_stores(store, monkeypatch):
    from lib import github_identity

    captured = {}

    def fake_request(url, token="", *, timeout=10.0):
        captured["url"] = url
        captured["token"] = token
        return {"login": "octocat", "name": "The Octocat", "avatar_url": "https://x/a.png"}

    monkeypatch.setattr(github_identity, "_request", fake_request)
    profile = github_identity.fetch_profile("ghp_token")
    assert profile.login == "octocat"
    assert profile.authenticated is True
    assert captured["url"].endswith("/user")
    assert captured["token"] == "ghp_token"
    assert github_identity.load_profile().login == "octocat"


def test_fetch_profile_without_token_uses_public_login(store, monkeypatch):
    from lib import github_identity

    github_identity.save_profile(github_identity.GitHubProfile(login="torvalds"))
    captured = {}

    def fake_request(url, token="", *, timeout=10.0):
        captured["url"] = url
        return {"login": "torvalds", "name": "Linus"}

    monkeypatch.setattr(github_identity, "_request", fake_request)
    profile = github_identity.fetch_profile("")
    assert profile.authenticated is False
    assert captured["url"].endswith("/users/torvalds")


def test_fetch_profile_without_token_or_login_raises(store):
    from lib.github_identity import GitHubIdentityError, fetch_profile

    with pytest.raises(GitHubIdentityError):
        fetch_profile("")


def test_apply_signer_fills_only_when_absent(store):
    from lib import github_identity

    github_identity.save_profile(github_identity.GitHubProfile(login="octocat"))
    assert github_identity.apply_signer({"app": "x"})["signer"] == "octocat"
    assert github_identity.apply_signer({"app": "x", "signer": "otro"})["signer"] == "otro"


def test_apply_signer_noop_without_session(store):
    from lib import github_identity

    metadata = {"app": "x"}
    assert github_identity.apply_signer(metadata) == metadata


def test_clear_identity_removes_token_and_profile(store):
    from lib import github_identity

    github_identity.save_token("ghp_secret")
    github_identity.save_profile(github_identity.GitHubProfile(login="octocat"))
    github_identity.clear_identity()
    assert github_identity.load_token() == ""
    assert github_identity.load_profile().login == ""


def test_sanitize_token_strips_invisible_characters():
    """Copiar el token desde la web cuela NBSP/ZWSP/BOM; no deben provocar 401."""
    from lib.github_identity import sanitize_token

    assert sanitize_token("  ghp_abc  ") == "ghp_abc"
    assert sanitize_token("ghp_abc\u00a0") == "ghp_abc"
    assert sanitize_token("\ufeffghp_abc") == "ghp_abc"
    assert sanitize_token("ghp_a\u200bb\u200cc") == "ghp_abc"


def test_saved_token_is_cleaned_and_persisted(store):
    from lib import github_identity

    github_identity.save_token("ghp_secret\u00a0")
    assert github_identity.load_token() == "ghp_secret"
    # Persistido en disco: un almacén nuevo lo vuelve a leer.
    from lib.pm_data import PMDataStore

    assert PMDataStore(path=store.path).get_user("github_token") == "ghp_secret"


def test_fetch_profile_sanitizes_token_before_request(store, monkeypatch):
    from lib import github_identity

    captured = {}

    def fake_request(url, token="", *, timeout=10.0):
        captured["token"] = token
        return {"login": "octocat"}

    monkeypatch.setattr(github_identity, "_request", fake_request)
    github_identity.fetch_profile("ghp_token\u00a0")
    assert captured["token"] == "ghp_token"


def test_request_invalid_header_reports_friendly_error(monkeypatch):
    """Una cabecera no ASCII lanzaba ValueError sin capturar; debe ser legible."""
    import urllib.request

    from lib import github_identity

    def boom(*_args, **_kwargs):
        raise ValueError("Invalid header value")

    monkeypatch.setattr(urllib.request, "urlopen", boom)
    with pytest.raises(github_identity.GitHubIdentityError) as exc:
        github_identity._request("https://api.github.com/user", "ghp_token")
    assert "caracteres" in str(exc.value)


def test_save_token_empty_clears_persisted_token(store):
    from lib import github_identity

    github_identity.save_token("ghp_secret")
    github_identity.save_token("")
    assert github_identity.load_token() == ""
    from lib.pm_data import PMDataStore

    assert not PMDataStore(path=store.path).get_user("github_token")


def test_avatar_cache_roundtrip(store, monkeypatch):
    from lib import github_identity

    monkeypatch.setattr(github_identity, "_avatar_cache_dir", lambda: store.path.parent / "avatars")
    (store.path.parent / "avatars").mkdir(exist_ok=True)
    assert github_identity.load_cached_avatar("octocat") is None
    github_identity.cache_avatar("octocat", b"\x89PNGdata")
    assert github_identity.load_cached_avatar("octocat") == b"\x89PNGdata"


def test_buildthread_injects_github_signer(store, tmp_path, monkeypatch):
    from lib import github_identity
    from lib.blindcubeEngine.BuildThread import FlangCompiler

    github_identity.save_profile(github_identity.GitHubProfile(login="JesusQuijada34"))
    project = tmp_path / "proj"
    project.mkdir()
    (project / "details.xml").write_text(
        "<?xml version=\"1.0\"?><app>"
        "<publisher>Influent</publisher><app>demo</app><name>Demo</name>"
        "<version>v1.0</version><platform>AlphaCube</platform><author>Jesus</author>"
        "</app>",
        encoding="utf-8",
    )
    compiler = FlangCompiler(project, tmp_path / "out", log_callback=lambda _m: None, sandbox=False)
    assert compiler.parse_details_xml() is True
    assert compiler.metadata["signer"] == "JesusQuijada34"
