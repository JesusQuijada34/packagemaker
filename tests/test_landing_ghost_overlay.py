# -*- coding: utf-8 -*-
"""Regresiones del "landing fantasma" y del material del avatar.

Cubre con código real los defectos reportados:

* al redimensionar/maximizar (o arrastrar el sidebar) reaparecía el landing de
  login oculto como una capa a pantalla completa no interactiva;
* el avatar del usuario salía cuadrado porque el ``border-radius`` del QSS no
  recorta el ``pixmap`` de un ``QLabel``;
* al plegar el asistente lateral el panel se ocultaba de golpe, sin recoger el
  recuadro.
"""

import os
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="module")
def qapp():
    qt = pytest.importorskip("PyQt6.QtWidgets")
    app = qt.QApplication.instance() or qt.QApplication([])
    yield app
    app.processEvents()


def _settle(app, ms=500):
    deadline = time.time() + ms / 1000.0
    while time.time() < deadline:
        app.processEvents()
        time.sleep(0.01)


def test_lock_to_parent_does_not_reveal_hidden_landing(qapp):
    """Reposicionar un landing oculto no debe volver a mostrarlo."""
    from lib.github_login_landing import GitHubLoginLanding

    landing = GitHubLoginLanding()
    try:
        landing.hide()
        landing.lock_to_parent()
        assert not landing.isVisible()
    finally:
        landing.close()
        qapp.processEvents()


def test_resize_does_not_resurrect_landing_when_inactive(qapp):
    """El resize de la ventana no revive el landing ya cerrado.

    Regresión: ``PackageTodoGUI.resizeEvent`` llamaba ``lock_to_parent()`` sin
    comprobar ``_landing_active`` y ``lock_to_parent`` hacía ``show()``; al
    maximizar aparecía el landing fantasma.
    """
    import packagemaker

    window = packagemaker.PackageTodoGUI()
    window.show()
    try:
        window._enter_with_cached_session()
        qapp.processEvents()
        assert not window.github_landing.isVisible()

        window.resize(1280, 820)
        _settle(qapp)
        assert not window.github_landing.isVisible()

        window.github_landing.lock_to_parent()
        assert not window.github_landing.isVisible()
    finally:
        window.close()
        qapp.processEvents()


def test_circular_pixmap_masks_corners(qapp):
    """La máscara deja las esquinas transparentes y el centro opaco."""
    from PyQt6.QtGui import QColor, QPixmap

    from lib.app_icons import circular_pixmap

    pixmap = QPixmap(64, 64)
    pixmap.fill(QColor("red"))
    rounded = circular_pixmap(pixmap, 88)
    assert not rounded.isNull()
    image = rounded.toImage()
    assert image.pixelColor(1, 1).alpha() == 0
    assert image.pixelColor(44, 44).alpha() == 255


def test_landing_avatar_is_masked_round(qapp):
    """El avatar del perfil se sustituye por un recorte circular."""
    from PyQt6.QtCore import QBuffer
    from PyQt6.QtGui import QPixmap

    from lib.github_identity import GitHubProfile
    from lib.github_login_landing import GitHubLoginLanding

    landing = GitHubLoginLanding()
    try:
        pixmap = QPixmap(64, 64)
        pixmap.fill()
        buf = QBuffer()
        buf.open(QBuffer.OpenModeFlag.ReadWrite)
        pixmap.save(buf, "PNG")
        landing.set_profile(GitHubProfile(login="octocat", name="The Octocat"), bytes(buf.data()))
        _settle(qapp, 500)
        avatar = landing.avatar.pixmap().toImage()
        assert avatar.pixelColor(1, 1).alpha() == 0
        assert avatar.pixelColor(avatar.width() // 2, avatar.height() // 2).alpha() == 255
    finally:
        landing.close()
        qapp.processEvents()


def test_assistant_collapse_animates_before_hiding(qapp):
    """Al plegar, el panel se recoge y se oculta al terminar la animación."""
    from lib.github_login_landing import CARD_WIDTH, GitHubLoginLanding

    landing = GitHubLoginLanding()
    landing.resize(1400, 900)
    landing.show()
    try:
        _settle(qapp)
        landing._toggle_assistant("token")
        _settle(qapp)
        assert landing.assistant.isVisible()
        assert landing.row.maximumWidth() > CARD_WIDTH

        landing._collapse_assistant()
        assert landing._assistant_flow == ""
        # Aún visible mientras se recoge el recuadro.
        assert landing.assistant.isVisible()
        _settle(qapp)
        assert not landing.assistant.isVisible()
        assert landing.row.maximumWidth() <= landing._closed_row_width() + 2
    finally:
        landing.close()
        qapp.processEvents()
