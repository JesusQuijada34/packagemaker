# -*- coding: utf-8 -*-
"""Extensión Perfil: la cuenta de GitHub dentro de su propia página (Q-030).

La tarjeta de identidad dejó de vivir en el sidebar —ocupaba el hueco entre
MoonFix y las herramientas— y pasa a esta página, junto con la descripción, el
avatar, el ``@login`` y los repositorios del usuario.

Los repositorios se piden en un hilo aparte: la página se construye y responde
aunque GitHub no conteste, y la ventana nunca se queda congelada esperando a la
red. Sin sesión la página muestra el estado de invitado y el botón de acceso.

Todo el color sale de ``lib/design_tokens``.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

try:
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
    from PyQt6.QtGui import QPixmap
    from PyQt6.QtWidgets import (
        QFrame,
        QHBoxLayout,
        QLabel,
        QScrollArea,
        QVBoxLayout,
        QWidget,
    )

    PYQT6_AVAILABLE = True
except ImportError:  # pragma: no cover - entorno sin Qt (CLI headless)
    PYQT6_AVAILABLE = False

    class QWidget:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            pass


from lib.design_tokens import (
    CONTENT_PADDING,
    TEXT,
    TEXT_DIM,
    TEXT_SOFT,
    card_qss,
    scrollbar_qss,
    uwp_button_qss,
)
from lib.i18n import tr
from lib.page_action_bar import (
    install_page_action_bar,
    make_action_button,
    set_action_bar_busy,
)

#: Tamaño del avatar grande de la cabecera de perfil.
AVATAR_SIZE = 72
#: Repositorios que se listan de una vez.
REPOSITORY_LIMIT = 12


class _RepositoryWorker(QThread):
    """Descarga los repositorios fuera del hilo de la interfaz."""

    finished_ok = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, fetch: Callable[[], List[Dict[str, Any]]], parent=None):
        super().__init__(parent)
        self._fetch = fetch

    def run(self) -> None:  # pragma: no cover - se ejercita en la ventana real
        try:
            self.finished_ok.emit(self._fetch())
        except Exception as exc:  # red, token, JSON…: la página sólo lo muestra
            self.failed.emit(str(exc))


class ProfilePage(QWidget):
    """Perfil de GitHub, repositorios y acceso a la cuenta."""

    def __init__(
        self,
        parent=None,
        *,
        card: Optional[QWidget] = None,
        on_login: Optional[Callable[[], None]] = None,
        on_logout: Optional[Callable[[], None]] = None,
        profile_loader: Optional[Callable[[], Any]] = None,
        avatar_loader: Optional[Callable[[str], Optional[bytes]]] = None,
        repositories_fetcher: Optional[Callable[[], List[Dict[str, Any]]]] = None,
    ):
        super().__init__(parent)
        self.setObjectName("ProfilePage")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._on_login = on_login
        self._on_logout = on_logout
        self._profile_loader = profile_loader or _default_profile_loader
        self._avatar_loader = avatar_loader or _default_avatar_loader
        self._repositories_fetcher = repositories_fetcher or _default_repositories_fetcher
        self._worker: Optional[_RepositoryWorker] = None
        self._repositories: List[Dict[str, Any]] = []
        self._profile: Any = None
        self._loaded_once = False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(
            CONTENT_PADDING, CONTENT_PADDING, CONTENT_PADDING, CONTENT_PADDING
        )
        outer.setSpacing(10)

        self.refresh_button = make_action_button(tr("profile.refresh"), "secondary")
        self.refresh_button.clicked.connect(self.refresh_repositories)
        self.action_bar, self.bar_title = install_page_action_bar(
            outer, tr("sidebar.profile"), buttons=(self.refresh_button,)
        )

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll.setStyleSheet(
            "QScrollArea{background:transparent;border:none;}" + scrollbar_qss()
        )
        # Sin esto el viewport pinta el color base de la paleta y deja una banda
        # distinta del resto de la página (mismo defecto que el issue #10).
        self.scroll.viewport().setAutoFillBackground(False)
        self.scroll.viewport().setStyleSheet("background:transparent;")
        outer.addWidget(self.scroll, 1)

        body = QWidget()
        body.setObjectName("ProfileBody")
        body.setStyleSheet("background:transparent;")
        self.scroll.setWidget(body)

        layout = QVBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        self.card = card
        if self.card is not None:
            layout.addWidget(self.card)

        layout.addWidget(self._build_identity())
        layout.addWidget(self._build_repositories())
        layout.addStretch(1)

        self.refresh()

    def showEvent(self, event) -> None:
        """Primera visita: pide los repositorios una sola vez."""
        super().showEvent(event)
        if not self._loaded_once:
            self._loaded_once = True
            self.refresh_repositories()

    # ── construcción ────────────────────────────────────────────────────────

    def _build_identity(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("ProfileIdentity")
        frame.setStyleSheet(card_qss())

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(18)

        self.avatar = QLabel()
        self.avatar.setObjectName("ProfileAvatar")
        self.avatar.setFixedSize(AVATAR_SIZE, AVATAR_SIZE)
        self.avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar.setStyleSheet(
            f"border-radius:{AVATAR_SIZE // 2}px;background:{TEXT_DIM}33;"
        )
        layout.addWidget(self.avatar, 0, Qt.AlignmentFlag.AlignTop)

        column = QVBoxLayout()
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(4)

        self.name_label = QLabel("")
        self.name_label.setObjectName("ProfileName")
        self.name_label.setWordWrap(True)
        self.name_label.setStyleSheet(f"color:{TEXT};font-size:18px;font-weight:600;")
        column.addWidget(self.name_label)

        self.login_label = QLabel("")
        self.login_label.setObjectName("ProfileLogin")
        self.login_label.setWordWrap(True)
        self.login_label.setStyleSheet(f"color:{TEXT_DIM};font-size:12px;")
        column.addWidget(self.login_label)

        self.bio_label = QLabel("")
        self.bio_label.setObjectName("ProfileBio")
        self.bio_label.setWordWrap(True)
        self.bio_label.setStyleSheet(f"color:{TEXT_SOFT};font-size:13px;")
        column.addWidget(self.bio_label)

        self.stats_label = QLabel("")
        self.stats_label.setObjectName("ProfileStats")
        self.stats_label.setWordWrap(True)
        self.stats_label.setStyleSheet(f"color:{TEXT_DIM};font-size:12px;")
        column.addWidget(self.stats_label)

        self.guest_label = QLabel(tr("profile.guest"))
        self.guest_label.setObjectName("ProfileGuest")
        self.guest_label.setWordWrap(True)
        self.guest_label.setStyleSheet(f"color:{TEXT_DIM};font-size:13px;")
        column.addWidget(self.guest_label)

        actions = QHBoxLayout()
        actions.setContentsMargins(0, 0, 0, 0)
        actions.setSpacing(8)
        self.login_button = self._make_button(tr("github.sign_in"), self._login)
        self.logout_button = self._make_button(tr("github.logout"), self._logout)
        actions.addWidget(self.login_button)
        actions.addWidget(self.logout_button)
        actions.addStretch(1)
        column.addLayout(actions)

        layout.addLayout(column, 1)
        return frame

    def _build_repositories(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("ProfileRepositories")
        frame.setStyleSheet(card_qss())

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        self.repositories_title = QLabel(tr("profile.repositories"))
        self.repositories_title.setStyleSheet(
            f"color:{TEXT};font-size:15px;font-weight:600;"
        )
        layout.addWidget(self.repositories_title)

        self.status_label = QLabel("")
        self.status_label.setObjectName("ProfileRepositoriesStatus")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet(f"color:{TEXT_DIM};font-size:12px;")
        layout.addWidget(self.status_label)

        self._repository_rows = QVBoxLayout()
        self._repository_rows.setContentsMargins(0, 0, 0, 0)
        self._repository_rows.setSpacing(8)
        layout.addLayout(self._repository_rows)
        return frame

    def _make_button(self, text: str, handler: Optional[Callable[[], None]]):
        from PyQt6.QtWidgets import QPushButton

        button = QPushButton(text)
        button.setFixedHeight(32)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(uwp_button_qss())
        if handler is not None:
            button.clicked.connect(lambda: handler())
        return button

    # ── estado ──────────────────────────────────────────────────────────────

    def refresh(self) -> None:
        """Lee el perfil guardado y lo pinta (sin tocar la red)."""
        try:
            profile = self._profile_loader()
        except Exception:
            profile = None
        self.set_profile(profile)

    def set_profile(self, profile: Any) -> None:
        self._profile = profile
        login = str(getattr(profile, "login", "") or "")
        if not login:
            self._render_guest()
            return

        extras = getattr(profile, "extras", {}) or {}
        name = str(getattr(profile, "display_name", lambda: login)() or login)
        self.name_label.setText(name)
        self.login_label.setText(f"@{login}")
        self.bio_label.setText(str(extras.get("bio", "") or ""))
        self.stats_label.setText(
            tr("profile.stats").format(
                repositories=extras.get("public_repos", 0) or 0,
                followers=extras.get("followers", 0) or 0,
                following=extras.get("following", 0) or 0,
            )
        )
        self.bio_label.setVisible(bool(self.bio_label.text()))
        self.guest_label.setVisible(False)
        self.login_button.setVisible(False)
        self.logout_button.setVisible(True)
        self._apply_avatar(login)

    def _render_guest(self) -> None:
        self.name_label.setText(tr("github.no_session"))
        self.login_label.setText("")
        self.bio_label.setText("")
        self.bio_label.setVisible(False)
        self.stats_label.setText("")
        self.guest_label.setVisible(True)
        self.login_button.setVisible(True)
        self.logout_button.setVisible(False)
        self.avatar.clear()
        self._clear_repositories()
        self.status_label.setText(tr("profile.guest_hint"))

    def _apply_avatar(self, login: str) -> None:
        data = self._avatar_loader(login)
        if not data:
            self.avatar.clear()
            return
        pixmap = QPixmap()
        if pixmap.loadFromData(data):
            self.avatar.setPixmap(
                pixmap.scaled(
                    AVATAR_SIZE,
                    AVATAR_SIZE,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

    # ── repositorios ────────────────────────────────────────────────────────

    def refresh_repositories(self) -> None:
        """Pide los repositorios en segundo plano (una sola petición a la vez)."""
        if not getattr(self._profile, "login", ""):
            self.status_label.setText(tr("profile.guest_hint"))
            return
        if self._worker is not None and self._worker.isRunning():
            return
        self.status_label.setText(tr("profile.repositories_loading"))
        set_action_bar_busy(self.action_bar, True)
        self._worker = _RepositoryWorker(self._repositories_fetcher, self)
        self._worker.finished_ok.connect(self._apply_repositories)
        self._worker.failed.connect(self._apply_repositories_error)
        self._worker.finished.connect(self._release_worker)
        self._worker.start()

    def _release_worker(self) -> None:
        worker, self._worker = self._worker, None
        set_action_bar_busy(self.action_bar, False)
        if worker is not None:
            worker.deleteLater()

    def _apply_repositories(self, repositories: List[Dict[str, Any]]) -> None:
        self._clear_repositories()
        self._repositories = list(repositories or [])
        if not self._repositories:
            self.status_label.setText(tr("profile.repositories_empty"))
            return
        self.status_label.setText("")
        for repository in self._repositories:
            self._repository_rows.addWidget(self._build_repository_row(repository))

    def _apply_repositories_error(self, message: str) -> None:
        self._clear_repositories()
        self.status_label.setText(
            tr("profile.repositories_error").format(error=message)
        )

    def _clear_repositories(self) -> None:
        self._repositories = []
        while self._repository_rows.count():
            item = self._repository_rows.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _build_repository_row(self, repository: Dict[str, Any]) -> QWidget:
        from PyQt6.QtWidgets import QPushButton

        row = QWidget()
        row.setStyleSheet("background:transparent;")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        name = str(repository.get("name", "") or "")
        description = str(repository.get("description", "") or "")
        language = str(repository.get("language", "") or "")
        text = QLabel(f"<b>{name}</b>" + (f" — {description}" if description else ""))
        text.setObjectName(f"ProfileRepository_{name}")
        text.setWordWrap(True)
        text.setStyleSheet(f"color:{TEXT_SOFT};font-size:12px;background:transparent;")
        if language:
            text.setToolTip(language)
        layout.addWidget(text, 1)

        url = str(repository.get("html_url", "") or "")
        if url:
            open_button = QPushButton(tr("profile.open"))
            open_button.setFixedHeight(26)
            open_button.setCursor(Qt.CursorShape.PointingHandCursor)
            open_button.setStyleSheet(uwp_button_qss())
            open_button.clicked.connect(lambda _=False, link=url: _open_url(link))
            layout.addWidget(open_button, 0)
        return row

    # ── sesión ──────────────────────────────────────────────────────────────

    def _login(self) -> None:
        if self._on_login is not None:
            self._on_login()

    def _logout(self) -> None:
        if self._on_logout is not None:
            self._on_logout()

    # ── idioma ──────────────────────────────────────────────────────────────

    def retranslate(self) -> None:
        """Reaplica los textos al idioma activo."""
        self.bar_title.setText(tr("sidebar.profile"))
        self.refresh_button.setText(tr("profile.refresh"))
        self.repositories_title.setText(tr("profile.repositories"))
        self.login_button.setText(tr("github.sign_in"))
        self.logout_button.setText(tr("github.logout"))
        self.guest_label.setText(tr("profile.guest"))
        self.set_profile(self._profile)
        if self._repositories:
            self._apply_repositories(self._repositories)
        elif getattr(self._profile, "login", ""):
            self.status_label.setText(tr("profile.repositories_loading"))
        else:
            self.status_label.setText(tr("profile.guest_hint"))


def _default_profile_loader() -> Any:
    from lib import github_identity

    return github_identity.load_profile()


def _default_avatar_loader(login: str) -> Optional[bytes]:
    from lib import github_identity

    return github_identity.load_cached_avatar(login)


def _default_repositories_fetcher() -> List[Dict[str, Any]]:
    from lib import github_identity

    return github_identity.fetch_repositories(limit=REPOSITORY_LIMIT)


def _open_url(url: str) -> None:
    from PyQt6.QtCore import QUrl
    from PyQt6.QtGui import QDesktopServices

    QDesktopServices.openUrl(QUrl(url))
