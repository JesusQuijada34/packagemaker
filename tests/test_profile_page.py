# -*- coding: utf-8 -*-
"""Q-030 — el perfil de GitHub como extensión del sidebar (issue #14).

Cubre tres piezas con código real:

- ``github_identity.fetch_repositories`` (URL, token y mapeo de campos);
- ``lib/profile_page.ProfilePage`` (invitado, perfil, repositorios y error);
- el orden del sidebar (las extensiones justo debajo de MoonFix) y la tarjeta
  de cuenta en Configuración.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

pytest.importorskip("PyQt6.QtWidgets")

from PyQt6.QtWidgets import QApplication  # noqa: E402

import lib.i18n as i18n  # noqa: E402
from lib import pm_data  # noqa: E402

_APP = None


def _ensure_app():
    """Qt aborta el proceso si la QApplication se recolecta a mitad de test."""
    global _APP
    if _APP is None:
        _APP = QApplication.instance() or QApplication(sys.argv)
    return _APP


@pytest.fixture(scope="session")
def qt_app():
    app = _ensure_app()
    i18n.i18n.initialize(app, "es")
    return app


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr(pm_data, "_data_dir", lambda: tmp_path)
    store = pm_data.PMDataStore(path=tmp_path / "pm.data")
    monkeypatch.setattr(pm_data, "_store", store)
    return store


# ── identidad: repositorios ────────────────────────────────────────────────


def test_fetch_repositories_uses_the_authenticated_endpoint(isolated_store, monkeypatch):
    from lib import github_identity

    captured = {}

    def fake_request(url, token="", *, timeout=10.0):
        captured["url"] = url
        captured["token"] = token
        return [
            {
                "name": "packagemaker",
                "description": "Empaquetador",
                "html_url": "https://github.com/JesusQuijada34/packagemaker",
                "language": "Python",
                "private": False,
                "updated_at": "2026-11-27T00:00:00Z",
                "extra": "no se propaga",
            },
            "no es un objeto",
        ]

    monkeypatch.setattr(github_identity, "_request", fake_request)
    repositories = github_identity.fetch_repositories(token="ghp_secret", limit=5)

    assert captured["url"].endswith("/user/repos?per_page=5&sort=updated")
    assert captured["token"] == "ghp_secret"
    assert repositories == [
        {
            "name": "packagemaker",
            "description": "Empaquetador",
            "html_url": "https://github.com/JesusQuijada34/packagemaker",
            "language": "Python",
            "private": False,
            "updated_at": "2026-11-27T00:00:00Z",
        }
    ]


def test_fetch_repositories_without_token_uses_the_public_login(isolated_store, monkeypatch):
    from lib import github_identity

    captured = {}

    def fake_request(url, token="", *, timeout=10.0):
        captured["url"] = url
        captured["token"] = token
        return []

    monkeypatch.setattr(github_identity, "_request", fake_request)
    github_identity.save_profile(github_identity.GitHubProfile(login="octocat"))

    assert github_identity.fetch_repositories() == []
    assert captured["url"].endswith("/users/octocat/repos?per_page=12&sort=updated")
    assert captured["token"] == ""


def test_fetch_repositories_without_session_raises(isolated_store):
    from lib import github_identity

    with pytest.raises(github_identity.GitHubIdentityError):
        github_identity.fetch_repositories()


def test_fetch_repositories_rejects_a_non_list_payload(isolated_store, monkeypatch):
    from lib import github_identity

    monkeypatch.setattr(github_identity, "_request", lambda *a, **k: {"message": "?"})
    with pytest.raises(github_identity.GitHubIdentityError):
        github_identity.fetch_repositories(token="ghp_secret")


def test_profile_extras_carry_the_description_and_followers(isolated_store, monkeypatch):
    from lib import github_identity

    monkeypatch.setattr(
        github_identity,
        "_request",
        lambda *a, **k: {
            "login": "octocat",
            "bio": "Constructor de paquetes",
            "public_repos": 7,
            "followers": 12,
            "following": 3,
        },
    )
    profile = github_identity.fetch_profile(token="ghp_secret")
    assert profile.extras["bio"] == "Constructor de paquetes"
    assert profile.extras["public_repos"] == 7
    assert profile.extras["followers"] == 12
    assert profile.extras["following"] == 3


# ── página Perfil ──────────────────────────────────────────────────────────


def _page(**kwargs):
    from lib.profile_page import ProfilePage

    return ProfilePage(**kwargs)


def test_profile_page_starts_as_guest(qt_app):
    page = _page(profile_loader=lambda: None, avatar_loader=lambda login: None)
    assert page.login_button.isVisibleTo(page)
    assert not page.logout_button.isVisibleTo(page)
    assert page.guest_label.isVisibleTo(page)
    assert page.name_label.text() == i18n.tr("github.no_session")


def test_profile_page_renders_the_saved_profile(qt_app):
    from lib.github_identity import GitHubProfile

    profile = GitHubProfile(
        login="octocat",
        name="The Octocat",
        extras={"bio": "Constructor", "public_repos": 4, "followers": 9, "following": 2},
    )
    page = _page(profile_loader=lambda: profile, avatar_loader=lambda login: None)

    assert page.name_label.text() == "The Octocat"
    assert page.login_label.text() == "@octocat"
    assert page.bio_label.text() == "Constructor"
    assert page.stats_label.text() == i18n.tr("profile.stats").format(
        repositories=4, followers=9, following=2
    )
    assert page.logout_button.isVisibleTo(page)
    assert not page.login_button.isVisibleTo(page)
    assert not page.guest_label.isVisibleTo(page)


def test_profile_page_lists_repositories(qt_app):
    from lib.github_identity import GitHubProfile

    profile = GitHubProfile(login="octocat")
    page = _page(profile_loader=lambda: profile, avatar_loader=lambda login: None)
    page._apply_repositories(
        [
            {"name": "uno", "description": "primero", "html_url": "https://x/uno"},
            {"name": "dos", "description": "", "html_url": ""},
        ]
    )

    assert page.status_label.text() == ""
    assert [repo["name"] for repo in page._repositories] == ["uno", "dos"]
    assert page._repository_rows.count() == 2

    page._apply_repositories([])
    assert page._repository_rows.count() == 0
    assert page.status_label.text() == i18n.tr("profile.repositories_empty")


def test_profile_page_shows_the_repository_error(qt_app):
    from lib.github_identity import GitHubProfile

    page = _page(profile_loader=lambda: GitHubProfile(login="octocat"))
    page._apply_repositories_error("sin red")
    assert page.status_label.text() == i18n.tr("profile.repositories_error").format(
        error="sin red"
    )


def test_guest_page_does_not_ask_for_repositories(qt_app):
    calls = []

    def fetcher():
        calls.append(1)
        return []

    page = _page(profile_loader=lambda: None, repositories_fetcher=fetcher)
    page.refresh_repositories()
    assert calls == []
    assert page.status_label.text() == i18n.tr("profile.guest_hint")


def test_repositories_fetch_runs_out_of_the_interface_thread(qt_app):
    """El hilo real de la página entrega la lista por señal (sin red)."""
    from lib.github_identity import GitHubProfile

    page = _page(
        profile_loader=lambda: GitHubProfile(login="octocat"),
        repositories_fetcher=lambda: [{"name": "uno", "html_url": ""}],
    )
    page.refresh_repositories()
    assert page._worker is not None
    page._worker.wait(5000)
    qt_app.processEvents()
    page._release_worker()
    qt_app.processEvents()

    assert page._repositories == [{"name": "uno", "html_url": ""}]
    assert page._repository_rows.count() == 1


def test_profile_page_retranslates(qt_app):
    from lib.github_identity import GitHubProfile

    page = _page(profile_loader=lambda: GitHubProfile(login="octocat"))
    i18n.i18n.initialize(qt_app, "en")
    try:
        page.retranslate()
        assert page.bar_title.text() == i18n.tr("sidebar.profile")
        assert page.repositories_title.text() == i18n.tr("profile.repositories")
        assert page.login_label.text() == "@octocat"
    finally:
        i18n.i18n.initialize(qt_app, "es")
        page.retranslate()


# ── sidebar y Configuración ────────────────────────────────────────────────


def test_profile_addon_is_shipped_below_the_main_pages():
    from lib.addons_engine import load_addons_from_dirs, shipped_addons_dirs

    addons = load_addons_from_dirs(shipped_addons_dirs(), strict=True)
    ids = [addon.id for addon in addons]
    assert "profile" in ids
    profile = next(addon for addon in addons if addon.id == "profile")
    assert profile.section == "tools"
    assert profile.builder == "build_profile_page"
    assert profile.label == "sidebar.profile"
    # Justo después de las páginas de trabajo (MoonFix es la última) y antes
    # de «Acerca de».
    assert ids.index("profile") > ids.index("moonfix")
    assert ids.index("profile") < ids.index("about")


def test_sidebar_puts_the_extensions_before_the_stretch():
    text = (ROOT / "packagemaker.py").read_text(encoding="utf-8")
    block = text.split("for addon, button in self._sidebar_items:\n            if addon.section == \"main\"", 1)[1]
    block = block.split("self.sidebar_collapse_button", 1)[0]
    tools_at = block.index('if addon.section == "tools"')
    stretch_at = block.index("self.sidebar_layout.addStretch()")
    assert tools_at < stretch_at, "las extensiones deben ir antes del hueco"
    assert "self.sidebar_layout.addWidget(self.github_card)" not in block


def test_window_builds_the_profile_page_and_account_card(qt_app, isolated_store):
    import packagemaker as pm

    win = pm.PackageTodoGUI()
    try:
        assert hasattr(win, "page_profile")
        assert win.page_profile.objectName() == "ProfilePage"
        # La identidad vive sólo en la página (R-5e9c1d87): no hay tarjeta
        # compacta duplicada en el sidebar ni apilada sobre el perfil.
        assert win.github_card is None
        panel = win.settings_panel
        assert "account" in panel._cards
        assert panel.widgets["conf_account_status"].text() == i18n.tr(
            "config.account_missing"
        )
    finally:
        win.close()
        qt_app.processEvents()


# ── R-5e9c1d87: identidad única y estadísticas persistentes ─────────────────


def test_profile_extras_survive_the_store_round_trip(isolated_store):
    """El recuento de repositorios y la bio deben seguir ahí tras reiniciar."""
    from lib import github_identity

    profile = github_identity.GitHubProfile(
        login="octocat",
        name="The Octocat",
        extras={
            "bio": "Constructor de paquetes",
            "public_repos": 7,
            "followers": 12,
            "following": 3,
        },
    )
    github_identity.save_profile(profile)

    restored = github_identity.load_profile()
    assert restored.extras == {
        "bio": "Constructor de paquetes",
        "public_repos": 7,
        "followers": 12,
        "following": 3,
    }


def test_clear_identity_removes_the_saved_extras(isolated_store):
    from lib import github_identity

    github_identity.save_profile(
        github_identity.GitHubProfile(login="octocat", extras={"public_repos": 7})
    )
    github_identity.clear_identity()

    assert github_identity.load_profile().extras == {}


def test_profile_page_draws_a_single_identity_and_logout(qt_app):
    """La tarjeta compacta del sidebar ya no se apila sobre la identidad."""
    from PyQt6.QtWidgets import QPushButton

    from lib.github_identity import GitHubProfile
    from lib.github_profile_card import GitHubProfileCard

    page = _page(
        profile_loader=lambda: GitHubProfile(login="octocat"),
        avatar_loader=lambda login: None,
    )

    assert page.findChildren(GitHubProfileCard) == []
    logout_buttons = [
        button
        for button in page.findChildren(QPushButton)
        if button.text() == i18n.tr("github.logout")
    ]
    assert len(logout_buttons) == 1
    assert len(page.findChildren(type(page.avatar), "ProfileAvatar")) == 1


def test_window_profile_page_has_no_duplicate_account_card(qt_app, isolated_store):
    import packagemaker as pm
    from lib.github_profile_card import GitHubProfileCard

    win = pm.PackageTodoGUI()
    try:
        assert win.page_profile.findChildren(GitHubProfileCard) == []
        assert getattr(win, "github_card", None) is None
    finally:
        win.close()
        qt_app.processEvents()
