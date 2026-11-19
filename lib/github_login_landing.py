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
    from PyQt6.QtCore import (
        QEasingCurve,
        QPropertyAnimation,
        QTimer,
        Qt,
        pyqtSignal,
    )
    from PyQt6.QtGui import QColor, QPainter, QPixmap
    from PyQt6.QtWidgets import (
        QFrame,
        QGraphicsOpacityEffect,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )
except ImportError:  # pragma: no cover
    QWidget = object

from lib.app_icons import ICONS_SVG, circular_pixmap, svg_to_pixmap
from lib.design_tokens import (
    AVATAR_ICON_SIZE,
    AVATAR_SIZE,
    BUTTON_HEIGHT,
    INPUT_HEIGHT,
)
from lib.i18n import tr
from lib.landing_assistant import ANIMATION_MS, PANEL_WIDTH, LandingAssistant, detect_default_browser

CARD_WIDTH = 460
CARD_EXPAND = 48


def _default_avatar_pixmap():
    """Isotipo vectorial de GitHub (blanco) para el avatar sin sesión."""
    try:
        return svg_to_pixmap(ICONS_SVG["github"], AVATAR_ICON_SIZE)
    except Exception:
        return QPixmap()


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
        self._assistant_flow = ""
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
        """Ajusta la capa al padre y la pone por encima de todos sus hijos.

        No fuerza ``show()``: reposicionar un landing oculto no debe revivirlo
        como capa fantasma. Quien quiera mostrarlo usa ``reveal()`` o
        ``setVisible(True)``.
        """
        parent = self.parentWidget()
        if parent is not None:
            self.setGeometry(parent.rect())
        if self.isVisible():
            self.raise_()
            self.setFocus(Qt.FocusReason.OtherFocusReason)

    def reveal(self):
        """Muestra el landing con un fundido y recupera el contraste original."""
        self.setWindowOpacity(0.0)
        self.show()
        self.lock_to_parent()
        animation = QPropertyAnimation(self, b"windowOpacity", self)
        animation.setDuration(360)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._reveal_animation = animation
        animation.start()

    def reset_to_initial_state(self):
        """Devuelve el landing al estado 'primera vez' tras cerrar sesión."""
        self._spinner_timer.stop()
        self._status_message = ""
        self.username_input.clear()
        self.token_input.clear()
        self._set_form_enabled(True)
        self.status.hide()
        self.welcome.hide()
        self.subtitle.setText(tr("github.landing_subtitle"))
        self.avatar.setGraphicsEffect(None)
        self.avatar.setPixmap(_default_avatar_pixmap())
        self.card.setFixedWidth(CARD_WIDTH)
        self.setWindowOpacity(1.0)
        self._reset_assistant()

    def _reset_assistant(self) -> None:
        """Pliega el asistente de inmediato (sin animación) al cerrar sesión."""
        self._assistant_flow = ""
        self._sync_assistant_links()
        animation = getattr(self, "_row_animation", None)
        if animation is not None:
            animation.stop()
        self.row.setMaximumWidth(self._closed_row_width())
        self.assistant.hide()

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
        self.avatar.setPixmap(_default_avatar_pixmap())
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

        # Enlaces del asistente (Fase 3.3): abren el panel lateral.
        self.token_link = QPushButton(tr("github.assistant_token_link"), self.card)
        self.token_link.setObjectName("GitHubAssistantLink")
        self.token_link.setCursor(Qt.CursorShape.PointingHandCursor)
        self.token_link.setFlat(True)
        self.token_link.clicked.connect(lambda: self._toggle_assistant("token"))
        card_layout.addWidget(self.token_link)

        self.account_link = QPushButton(tr("github.assistant_account_link"), self.card)
        self.account_link.setObjectName("GitHubAssistantLink")
        self.account_link.setCursor(Qt.CursorShape.PointingHandCursor)
        self.account_link.setFlat(True)
        self.account_link.clicked.connect(lambda: self._toggle_assistant("account"))
        card_layout.addWidget(self.account_link)

        # La tarjeta y el panel viven en una fila que se ensancha al desplegar.
        self.row = QWidget(self)
        row_layout = QHBoxLayout(self.row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(12)
        row_layout.addWidget(self.card)
        self.assistant = LandingAssistant(self.row, detect_default_browser())
        self.assistant.setObjectName("GitHubAssistantPanel")
        self.assistant.hide()
        row_layout.addWidget(self.assistant)
        outer.addWidget(self.row, 0, Qt.AlignmentFlag.AlignCenter)

    # ── asistente lateral (Fase 3.3) ──────────────────────────────────────
    def _toggle_assistant(self, flow: str) -> None:
        """Despliega el panel lateral o lo pliega si ya está abierto."""
        if self._assistant_flow == flow:
            self._collapse_assistant()
            return
        self._assistant_flow = flow
        self.assistant.start_flow(flow)
        self.assistant.show()
        self._animate_row(self._closed_row_width() + PANEL_WIDTH)
        self._sync_assistant_links()

    def _collapse_assistant(self) -> None:
        self._assistant_flow = ""
        self._sync_assistant_links()
        # Se contrae con animación y el panel se oculta al terminar: ocultarlo de
        # inmediato dejaba un salto brusco en el que el recuadro no se recogía.
        self._animate_row(self._closed_row_width(), on_finished=self.assistant.hide)

    def _closed_row_width(self) -> int:
        return CARD_WIDTH + 2 * self.layout().contentsMargins().left()

    def _animate_row(self, target: int, on_finished=None) -> None:
        animation = QPropertyAnimation(self.row, b"maximumWidth", self)
        animation.setDuration(ANIMATION_MS)
        animation.setStartValue(self.row.width())
        animation.setEndValue(target)
        animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        if on_finished is not None:
            animation.finished.connect(on_finished)
        # Se detiene la animación anterior: sin esto, alternar el panel a media
        # transición dejaba dos animaciones compitiendo por ``maximumWidth``.
        previous = getattr(self, "_row_animation", None)
        if previous is not None:
            previous.stop()
        self._row_animation = animation
        animation.start()

    def _sync_assistant_links(self) -> None:
        token_open = self._assistant_flow == "token"
        account_open = self._assistant_flow == "account"
        self.token_link.setText(
            tr("github.assistant_token_link_active") if token_open
            else tr("github.assistant_token_link")
        )
        self.account_link.setText(
            tr("github.assistant_account_link_active") if account_open
            else tr("github.assistant_account_link")
        )

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
        self._set_avatar(avatar_bytes)

    def _set_avatar(self, avatar_bytes: bytes | None):
        """Coloca el avatar circular del usuario (o el isotipo si no hay bytes)."""
        if avatar_bytes:
            pixmap = QPixmap()
            if pixmap.loadFromData(avatar_bytes):
                self._animate_avatar_swap(pixmap)
                return
        self.avatar.setPixmap(_default_avatar_pixmap())

    def _animate_avatar_swap(self, pixmap: QPixmap):
        """Transición suave del isotipo de GitHub al avatar circular del usuario."""
        scaled = circular_pixmap(pixmap, AVATAR_SIZE)
        if scaled.isNull():
            self.avatar.setPixmap(_default_avatar_pixmap())
            return
        self.avatar.setPixmap(scaled)
        effect = QGraphicsOpacityEffect(self.avatar)
        self.avatar.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity", self)
        animation.setDuration(320)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._avatar_animation = animation
        animation.start()

    def begin_loading(self, message: str = ""):
        self._expand_card()
        self._set_form_enabled(False)
        self.welcome.hide()
        self._status_message = message or tr("github.landing_starting")
        self.status.setText(self._status_message)
        self.status.show()
        self._spinner_index = 0
        self._spinner_timer.start(110)

    def _expand_card(self):
        """Ensancha la tarjeta suavemente al iniciar sesión."""
        target = CARD_WIDTH + CARD_EXPAND
        animation = QPropertyAnimation(self.card, b"minimumWidth", self)
        animation.setDuration(280)
        animation.setStartValue(self.card.width())
        animation.setEndValue(target)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._card_animation = animation
        # max a target de inmediato y min creciendo: así el ancho se anima.
        self.card.setMaximumWidth(target)
        animation.start()

    def show_error(self, message: str):
        self._spinner_timer.stop()
        self._set_form_enabled(True)
        self._status_message = ""
        self.status.setText(message)
        self.status.show()
        self.token_input.setFocus(Qt.FocusReason.OtherFocusReason)

    def show_welcome(self, profile):
        self._spinner_timer.stop()
        # El indicador de estado se transforma en el nombre de la cuenta.
        self.subtitle.setText(profile.display_name())
        self.status.setText(tr("github.welcome").format(name=profile.display_name()))
        self.status.show()
        self.welcome.hide()
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
