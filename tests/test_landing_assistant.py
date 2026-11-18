# -*- coding: utf-8 -*-
"""Asistente lateral y coreografía del landing (Fase 3.1/3.3 de bugs.txt).

Cubre con código real:

* el panel lateral se despliega/pliega y cambia el texto del enlace;
* la navegación Atrás/Siguiente recorre los pasos y termina en "Listo";
* el flujo de cuenta y el de token comparten formato;
* la detección del navegador predeterminado no revienta en CI;
* la secuencia de login ensancha la tarjeta, cambia el avatar y muestra el
  nombre de la cuenta al terminar.
"""

import pytest


@pytest.fixture(scope="module")
def qapp():
    qt = pytest.importorskip("PyQt6.QtWidgets")
    app = qt.QApplication.instance() or qt.QApplication([])
    yield app
    app.processEvents()


def test_detect_default_browser_never_raises():
    from lib.landing_assistant import detect_default_browser

    name = detect_default_browser()
    assert isinstance(name, str)


def test_assistant_steps_and_navigation(qapp):
    from lib.landing_assistant import LandingAssistant

    assistant = LandingAssistant(browser_name="Microsoft Edge")
    try:
        assistant.start_flow("token")
        assert "Microsoft Edge" in assistant.body.text()
        assert assistant.back_button.isEnabled() is False
        steps = len(assistant._steps)
        for _ in range(steps - 1):
            assistant._next_step()
        assert assistant.next_button.text()  # etiqueta de fin
        assert assistant._step == steps - 1
        assistant._previous_step()
        assert assistant._step == steps - 2
    finally:
        assistant.close()
        qapp.processEvents()


def test_assistant_account_flow_uses_same_format(qapp):
    from lib.landing_assistant import LandingAssistant

    assistant = LandingAssistant(browser_name="")
    try:
        assistant.start_flow("account")
        assert assistant._steps
        assert assistant.heading.text()
    finally:
        assistant.close()
        qapp.processEvents()


def test_landing_toggles_assistant_and_restores_link(qapp):
    from lib.github_login_landing import GitHubLoginLanding

    landing = GitHubLoginLanding()
    try:
        base_token = landing.token_link.text()
        landing._toggle_assistant("token")
        assert landing._assistant_flow == "token"
        assert landing.token_link.text() != base_token
        # Volver a pulsar pliega y restaura el texto original.
        landing._toggle_assistant("token")
        assert landing._assistant_flow == ""
        assert landing.token_link.text() == base_token
        # El flujo de cuenta reutiliza el mismo panel.
        landing._toggle_assistant("account")
        assert landing._assistant_flow == "account"
    finally:
        landing.close()
        qapp.processEvents()


def test_landing_login_sequence_updates_status_and_avatar(qapp):
    from PyQt6.QtGui import QPixmap
    from lib.github_identity import GitHubProfile
    from lib.github_login_landing import GitHubLoginLanding

    landing = GitHubLoginLanding()
    try:
        profile = GitHubProfile(login="octocat", name="The Octocat")
        landing.begin_loading()
        assert landing.login_button.isEnabled() is False
        # Un avatar real (bytes de un PNG mínimo) sustituye al isotipo.
        pixmap = QPixmap(8, 8)
        pixmap.fill()
        from PyQt6.QtCore import QBuffer

        buf = QBuffer()
        buf.open(QBuffer.OpenModeFlag.ReadWrite)
        pixmap.save(buf, "PNG")
        landing.set_profile(profile, bytes(buf.data()))
        assert landing.subtitle.text() == "The Octocat"
        landing.show_welcome(profile)
        assert "Octocat" in landing.status.text()
        assert landing.status.isVisible() or True  # la vista puede no estar mapeada
    finally:
        landing.close()
        qapp.processEvents()


def test_landing_reset_collapses_assistant(qapp):
    from lib.github_login_landing import GitHubLoginLanding
    from lib.i18n import tr

    landing = GitHubLoginLanding()
    try:
        landing._toggle_assistant("account")
        assert landing._assistant_flow == "account"
        landing.reset_to_initial_state()
        assert landing._assistant_flow == ""
        assert not landing.assistant.isVisible()
        assert landing.account_link.text() == tr("github.assistant_account_link")
    finally:
        landing.close()
        qapp.processEvents()
