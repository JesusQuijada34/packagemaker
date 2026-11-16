"""Landing de autenticación GitHub para el arranque de Package Maker.

El widget sólo define estructura y estados; la apariencia llega del QSS raíz
mediante objectName, de modo que los controles nuevos heredan el lenguaje visual
de la aplicación sin estilos locales dispersos.
"""
from __future__ import annotations

try:
    from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QTimer, Qt, pyqtSignal
    from PyQt6.QtGui import QPixmap
    from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
except ImportError:  # pragma: no cover
    QWidget = object

from lib.i18n import tr


class GitHubLoginLanding(QWidget):
    login_requested = pyqtSignal(str)
    finished = pyqtSignal(object)
    profile_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("GitHubLoginLanding")
        self._spinner_index = 0
        self._spinner_timer = QTimer(self)
        self._spinner_timer.timeout.connect(self._tick_spinner)
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(32, 32, 32, 32)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.card = QFrame(self)
        self.card.setObjectName("GitHubLoginCard")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(42, 38, 42, 38)
        card_layout.setSpacing(14)

        self.avatar = QLabel(self.card)
        self.avatar.setObjectName("GitHubLandingAvatar")
        self.avatar.setFixedSize(112, 112)
        self.avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar.setText("GH")
        self.avatar.mousePressEvent = lambda event: self.profile_requested.emit()
        card_layout.addWidget(self.avatar, 0, Qt.AlignmentFlag.AlignHCenter)

        self.name = QLabel(self.card)
        self.name.setObjectName("GitHubLandingName")
        self.name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name.setText("GitHub")
        card_layout.addWidget(self.name)

        self.prompt = QLabel(self.card)
        self.prompt.setObjectName("GitHubLandingPrompt")
        self.prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prompt.setText(tr("github.landing_prompt"))
        card_layout.addWidget(self.prompt)

        self.credentials_row = QHBoxLayout()
        self.token_input = QLineEdit(self.card)
        self.token_input.setObjectName("GitHubTokenInput")
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.token_input.setPlaceholderText(tr("github.landing_token_placeholder"))
        self.token_input.setToolTip(tr("github.landing_token_hint"))
        self.credentials_row.addWidget(self.token_input, 1)
        self.login_button = QPushButton(tr("github.sign_in"), self.card)
        self.login_button.setObjectName("GitHubLoginButton")
        self.login_button.setDefault(True)
        self.login_button.clicked.connect(lambda: self.login_requested.emit(self.token_input.text().strip()))
        self.credentials_row.addWidget(self.login_button)
        card_layout.addLayout(self.credentials_row)

        self.progress_row = QHBoxLayout()
        self.progress_text = QLabel(self.card)
        self.progress_text.setObjectName("GitHubLoginStatus")
        self.progress_text.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.progress_row.addWidget(self.progress_text, 1)
        self.spinner = QLabel(self.card)
        self.spinner.setObjectName("GitHubLoginSpinner")
        self.spinner.setFixedWidth(28)
        self.spinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_row.addWidget(self.spinner)
        card_layout.addLayout(self.progress_row)

        self.welcome = QLabel(self.card)
        self.welcome.setObjectName("GitHubWelcomeLabel")
        self.welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.welcome.setWordWrap(True)
        self.welcome.hide()
        card_layout.addWidget(self.welcome)

        outer.addWidget(self.card, 0, Qt.AlignmentFlag.AlignCenter)
        self.progress_row_widget = self.progress_text
        self.progress_text.hide()
        self.spinner.hide()

    def set_profile(self, profile, avatar_bytes: bytes | None = None):
        if not profile:
            return
        self.name.setText(profile.display_name())
        if avatar_bytes:
            pixmap = QPixmap()
            if pixmap.loadFromData(avatar_bytes):
                self.avatar.setPixmap(pixmap.scaled(112, 112, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
        else:
            self.avatar.setText((profile.login or "GH")[:2].upper())

    def begin_loading(self, message: str = ""):
        self.credentials_row.setEnabled(False)
        self.token_input.hide()
        self.login_button.hide()
        self.progress_text.setText(message or tr("github.landing_starting"))
        self.progress_text.show()
        self.spinner.show()
        self._spinner_timer.start(110)

    def show_error(self, message: str):
        self._spinner_timer.stop()
        self.spinner.hide()
        self.progress_text.setText(message)
        self.progress_text.show()
        self.credentials_row.setEnabled(True)
        self.token_input.show()
        self.login_button.show()

    def show_welcome(self, profile):
        self._spinner_timer.stop()
        self.progress_text.setText("")
        self.progress_text.hide()
        self.welcome.setText(tr("github.welcome").format(name=profile.display_name()))
        self.welcome.show()
        self.spinner.show()
        QTimer.singleShot(900, lambda: self._finish(profile))

    def _finish(self, profile):
        animation = QPropertyAnimation(self, b"windowOpacity", self)
        animation.setDuration(420)
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        animation.finished.connect(lambda: self._complete(profile, animation))
        self._exit_animation = animation
        animation.start()

    def _complete(self, profile, animation):
        self.hide()
        self.setWindowOpacity(1.0)
        self.finished.emit(profile)
        animation.deleteLater()

    def _tick_spinner(self):
        self._spinner_index = (self._spinner_index + 1) % 4
        self.spinner.setText("·" * (self._spinner_index + 1))
