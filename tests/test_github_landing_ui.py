"""Regresiones visuales del landing de GitHub y su tarjeta lateral.

Estos tests cubren el defecto visible en la captura: el contenido principal se
transparentaba a través del landing y la acción de sesión se comprimía en la
misma fila que el nombre de usuario.
"""
import pytest


@pytest.fixture(scope="module")
def qapp():
    qt = pytest.importorskip("PyQt6.QtWidgets")
    app = qt.QApplication.instance() or qt.QApplication([])
    yield app
    app.processEvents()


def test_root_stylesheet_paints_github_landing_and_card():
    from lib.fluent_theme import applyget

    stylesheet = applyget("#0078D4", dark=True)
    assert "QWidget#GitHubLoginLanding" in stylesheet
    assert "QFrame#GitHubLoginCard" in stylesheet
    assert "background-color: #1C1C1E" in stylesheet
    assert "QLineEdit#GitHubTokenInput" in stylesheet
    assert "QPushButton#GitHubLoginButton" in stylesheet


def test_root_stylesheet_keeps_github_landing_opaque_in_light_mode():
    from lib.fluent_theme import applyget

    stylesheet = applyget("#0078D4", dark=False)
    landing = stylesheet.split("QWidget#GitHubLoginLanding", 1)[1].split("}", 1)[0]
    assert "background-color: #F5F7FB" in landing
    assert "color: #000000" in landing


def test_github_landing_is_an_opaque_overlay(qapp):
    from PyQt6.QtCore import Qt
    from lib.github_login_landing import GitHubLoginLanding

    landing = GitHubLoginLanding()
    try:
        assert not landing.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        assert landing.testAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        assert landing.testAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
    finally:
        landing.close()
        qapp.processEvents()


def test_github_landing_has_modern_login_controls(qapp):
    """El rediseño exige isotipo, campo de usuario, token y píldora."""
    from lib.github_login_landing import AVATAR_SIZE, GitHubLoginLanding

    landing = GitHubLoginLanding()
    try:
        assert landing.avatar.width() == AVATAR_SIZE == landing.avatar.height()
        assert landing.avatar.objectName() == "GitHubLandingAvatar"
        assert landing.username_input.objectName() == "GitHubUsernameInput"
        assert landing.token_input.objectName() == "GitHubTokenInput"
        assert landing.login_button.objectName() == "GitHubLoginButton"
        assert landing.card.objectName() == "GitHubLoginCard"
        # No debe existir un botón de regresión en el diseño nuevo.
        assert not hasattr(landing, "back_button")
    finally:
        landing.close()
        qapp.processEvents()


def test_github_landing_emits_username_and_token(qapp):
    from lib.github_login_landing import GitHubLoginLanding

    landing = GitHubLoginLanding()
    captured = {}
    landing.login_requested.connect(lambda user, token: captured.update(user=user, token=token))
    try:
        landing.username_input.setText("octocat")
        landing.token_input.setText("ghp_token")
        landing.login_button.click()
        qapp.processEvents()
        assert captured == {"user": "octocat", "token": "ghp_token"}
    finally:
        landing.close()
        qapp.processEvents()


def test_github_landing_error_reenables_form(qapp):
    from lib.github_login_landing import GitHubLoginLanding

    landing = GitHubLoginLanding()
    try:
        landing.begin_loading()
        assert not landing.login_button.isEnabled()
        landing.show_error("Token de GitHub inválido o caducado")
        assert landing.login_button.isEnabled()
        assert landing.token_input.isEnabled()
        assert "inválido" in landing.status.text()
    finally:
        landing.close()
        qapp.processEvents()


def test_github_profile_action_has_its_own_sidebar_row(qapp):
    from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout
    from lib.github_profile_card import GitHubProfileCard

    card = GitHubProfileCard()
    try:
        layout = card.layout()
        assert isinstance(layout, QVBoxLayout)
        assert layout.count() == 2
        assert isinstance(layout.itemAt(0).layout(), QHBoxLayout)
        assert isinstance(layout.itemAt(1).layout(), QHBoxLayout)
        assert card.btn_action.minimumWidth() >= 104
        assert card.btn_action.objectName() == "GitHubProfileAction"
    finally:
        card.close()
        qapp.processEvents()
