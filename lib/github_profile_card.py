"""Tarjeta de perfil de GitHub para el panel lateral del IDE.

Muestra el avatar, el nombre visible y el ``login`` del usuario autenticado, y
ofrece iniciar/cerrar sesión. Sin PyQt6 degrada a un marcador que no revienta la
construcción de la ventana, siguiendo la convención del resto del proyecto.
"""
from __future__ import annotations

try:
    from PyQt6.QtCore import Qt, pyqtSignal
    from PyQt6.QtGui import QPixmap
    from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget
    PYQT6_AVAILABLE = True
except ImportError:  # pragma: no cover - entorno sin GUI
    PYQT6_AVAILABLE = False

    class QWidget:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

_AVATAR_SIZE = 34


class GitHubProfileCard(QWidget):
    """Tarjeta compacta con el perfil de GitHub y acciones de sesión."""

    profile_requested = pyqtSignal()

    def __init__(self, parent=None, on_login=None, on_logout=None, dark: bool = True):
        super().__init__(parent)
        self.setObjectName("GitHubProfileCard")
        self._on_login = on_login
        self._on_logout = on_logout
        self._avatar_bytes: bytes | None = None

        # La barra lateral admite desde ~180 px. Separamos la identidad y la
        # acción en filas distintas para que el texto no compita con el botón.
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(7)

        identity_row = QHBoxLayout()
        identity_row.setContentsMargins(0, 0, 0, 0)
        identity_row.setSpacing(9)

        self.avatar = QLabel()
        self.avatar.setObjectName("GitHubProfileAvatar")
        self.avatar.setFixedSize(_AVATAR_SIZE, _AVATAR_SIZE)
        self.avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        identity_row.addWidget(self.avatar)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(1)
        self.lbl_name = QLabel()
        self.lbl_name.setObjectName("GitHubProfileName")
        self.lbl_name.setMinimumWidth(0)
        self.lbl_name.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.lbl_login = QLabel()
        self.lbl_login.setObjectName("GitHubProfileLogin")
        self.lbl_login.setMinimumWidth(0)
        self.lbl_login.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        text_col.addWidget(self.lbl_name)
        text_col.addWidget(self.lbl_login)
        identity_row.addLayout(text_col, 1)
        layout.addLayout(identity_row)

        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, 0, 0, 0)
        action_row.addStretch(1)
        self.btn_action = QPushButton()
        self.btn_action.setObjectName("GitHubProfileAction")
        self.btn_action.setMinimumWidth(104)
        self.btn_action.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.btn_action.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_action.clicked.connect(self._handle_action)
        action_row.addWidget(self.btn_action)
        layout.addLayout(action_row)

        self.set_profile(None)

    def _handle_action(self) -> None:
        if self._current_login:
            if self._on_logout:
                self._on_logout()
        elif self._on_login:
            self._on_login()

    def set_profile(self, profile) -> None:
        """Actualiza la tarjeta con un ``GitHubProfile`` (o ``None`` sin sesión)."""
        from lib.i18n import tr

        self._current_login = getattr(profile, "login", "") if profile else ""
        if profile and self._current_login:
            self.lbl_name.setText(profile.display_name())
            self.lbl_login.setText(f"@{profile.login}")
            self.btn_action.setText(tr("github.logout"))
            self.setToolTip(profile.html_url or "")
        else:
            self.lbl_name.setText(tr("github.sign_in_prompt"))
            self.lbl_login.setText(tr("github.no_session"))
            self.btn_action.setText(tr("github.sign_in"))
            self.setToolTip("")

    def set_avatar_bytes(self, data: bytes | None) -> None:
        """Carga el avatar desde bytes; sin datos deja el marcador vacío."""
        self._avatar_bytes = data
        if not data:
            self.avatar.clear()
            return
        pixmap = QPixmap()
        if pixmap.loadFromData(data):
            from lib.app_icons import circular_pixmap

            rounded = circular_pixmap(pixmap, _AVATAR_SIZE)
            if not rounded.isNull():
                self.avatar.setPixmap(rounded)

    def mousePressEvent(self, event):  # noqa: N802 - API Qt
        if self._current_login and event.button() == Qt.MouseButton.LeftButton:
            self.profile_requested.emit()
        super().mousePressEvent(event)
