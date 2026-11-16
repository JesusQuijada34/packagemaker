"""Landing de autenticación GitHub para el arranque de Package Maker.

El widget sólo define estructura y estados; la apariencia llega del QSS raíz
mediante objectName, de modo que los controles nuevos heredan el lenguaje visual
de la aplicación sin estilos locales dispersos.

El diseño es un login moderno centrado: isotipo circular que se convierte en el
avatar tras autenticar, campo de usuario, campo de token, botón píldora y una
línea de estado con spinner. No hay botón de regresión: la única acción es
iniciar sesión.
"""
from __future__ import annotations

try:
    from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QTimer, Qt, pyqtSignal
    from PyQt6.QtGui import QColor, QPainter, QPixmap
    from PyQt6.QtWidgets import QFrame, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
except ImportError:  # pragma: no cover
    QWidget = object

from lib.i18n import tr

AVATAR_SIZE = 88
CARD_WIDTH = 460
INPUT_HEIGHT = 46
BUTTON_HEIGHT = 48


class GitHubLoginLanding(QWidget):
    login_requested = pyqtSignal(str, str)
    finished = pyqtSignal(object)
    profile_requested = pyqtSignal()

    def __init__(self, parent=None, background_path: str = ""):
        super().__init__(parent)
        self.setObjectName("GitHubLoginLanding")
        # El landing cubre el contenido completo (sidebar + páginas). No puede
        # ser translúcido: de lo contrario las etiquetas y el formulario que
        # quedan debajo se mezclan visualmente, justo el artefacto de la captura.
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        self.setAutoFillBackground(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._background = QPixmap(background_path) if background_path else QPixmap()
        self._spinner_index = 0
        self._status_message = ""
        self._spinner_timer = QTimer(self)
        self._spinner_timer.timeout.connect(self._tick_spinner)
        self._build_ui()

    def paintEvent(self, event):  # noqa: N802 - API Qt
        """Pinta el fondo difuminado (si existe) con un velo para dar contraste."""
        super().paintEvent(event)
        if self._background.isNull():
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        scaled = self._background.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        painter.drawPixmap(self.rect(), scaled)
        # Velo uniforme para que la tarjeta y el texto siempre se lean.
        painter.fillRect(self.rect(), QColor(0, 0, 0, 120))
        painter.end()

    def lock_to_parent(self):
        """Ajusta la capa al padre y la pone por encima de todos sus hijos."""
        parent = self.parentWidget()
        if parent is not None:
            self.setGeometry(parent.rect())
        self.raise_()
        self.show()
        self.setFocus(Qt.FocusReason.OtherFocusReason)

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.card = QFrame(self)
        self.card.setObjectName("GitHubLoginCard")
        self.card.setFixedWidth(CARD_WIDTH)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(38, 42, 38, 42)
        card_layout.setSpacing(16)

        self.avatar = QLabel(self.card)
        self.avatar.setObjectName("GitHubLandingAvatar")
        self.avatar.setFixedSize(AVATAR_SIZE, AVATAR_SIZE)
        self.avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar.setText("GH")
        self.avatar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.avatar.mousePressEvent = lambda event: self.profile_requested.emit()
        card_layout.addWidget(self.avatar, 0, Qt.AlignmentFlag.AlignHCenter)

        self.title = QLabel(self.card)
        self.title.setObjectName("GitHubLandingTitle")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setText(tr("github.landing_title"))
        card_layout.addWidget(self.title)

        self.subtitle = QLabel(self.card)
        self.subtitle.setObjectName("GitHubLandingSubtitle")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle.setWordWrap(True)
        self.subtitle.setText(tr("github.landing_subtitle"))
        card_layout.addWidget(self.subtitle)

        self.username_input = QLineEdit(self.card)
        self.username_input.setObjectName("GitHubUsernameInput")
        self.username_input.setPlaceholderText(tr("github.landing_username_placeholder"))
        self.username_input.setClearButtonEnabled(True)
        self.username_input.setMinimumHeight(INPUT_HEIGHT)
        card_layout.addWidget(self.username_input)

        self.token_input = QLineEdit(self.card)
        self.token_input.setObjectName("GitHubTokenInput")
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.token_input.setPlaceholderText(tr("github.landing_token_placeholder"))
        self.token_input.setToolTip(tr("github.landing_token_hint"))
        self.token_input.setMinimumHeight(INPUT_HEIGHT)
        self.token_input.returnPressed.connect(self._emit_login)
        card_layout.addWidget(self.token_input)

        self.login_button = QPushButton(tr("github.sign_in"), self.card)
        self.login_button.setObjectName("GitHubLoginButton")
        self.login_button.setDefault(True)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.setMinimumHeight(BUTTON_HEIGHT)
        self.login_button.clicked.connect(self._emit_login)
        card_layout.addWidget(self.login_button)

        self.prompt = QLabel(self.card)
        self.prompt.setObjectName("GitHubLandingPrompt")
        self.prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prompt.setWordWrap(True)
        self.prompt.setText(tr("github.landing_token_hint"))
        card_layout.addWidget(self.prompt)

        self.status = QLabel(self.card)
        self.status.setObjectName("GitHubLoginStatus")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setWordWrap(True)
        self.status.hide()
        card_layout.addWidget(self.status)

        self.welcome = QLabel(self.card)
        self.welcome.setObjectName("GitHubWelcomeLabel")
        self.welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.welcome.setWordWrap(True)
        self.welcome.hide()
        card_layout.addWidget(self.welcome)

        outer.addWidget(self.card, 0, Qt.AlignmentFlag.AlignCenter)

    # ── estado ────────────────────────────────────────────────────────────
    def _emit_login(self):
        self.login_requested.emit(
            self.username_input.text().strip(),
            self.token_input.text().strip(),
        )

    def _set_form_enabled(self, enabled: bool):
        for widget in (self.username_input, self.token_input, self.login_button):
            widget.setEnabled(enabled)
            widget.setVisible(enabled)

    def set_profile(self, profile, avatar_bytes: bytes | None = None):
        if not profile:
            return
        self.subtitle.setText(profile.display_name())
        if avatar_bytes:
            pixmap = QPixmap()
            if pixmap.loadFromData(avatar_bytes):
                self.avatar.setPixmap(
                    pixmap.scaled(
                        AVATAR_SIZE,
                        AVATAR_SIZE,
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
                return
        self.avatar.setText((profile.login or "GH")[:2].upper())

    def begin_loading(self, message: str = ""):
        self._set_form_enabled(False)
        self.welcome.hide()
        self._status_message = message or tr("github.landing_starting")
        self.status.setText(self._status_message)
        self.status.show()
        self._spinner_index = 0
        self._spinner_timer.start(110)

    def show_error(self, message: str):
        self._spinner_timer.stop()
        self._set_form_enabled(True)
        self._status_message = ""
        self.status.setText(message)
        self.status.show()
        self.token_input.setFocus(Qt.FocusReason.OtherFocusReason)

    def show_welcome(self, profile):
        self._spinner_timer.stop()
        self.status.hide()
        self.welcome.setText(tr("github.welcome").format(name=profile.display_name()))
        self.welcome.show()
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
        self.status.setText(f"{self._status_message} {'·' * (self._spinner_index + 1)}")
