# -*- coding: utf-8 -*-
"""Panel de configuración en tarjetas con navegación en cascada (Fase 3.2).

El panel raíz es una lista de tarjetas —icono SVG a la izquierda, flecha a la
derecha— y cada tarjeta abre su detalle con un desplazamiento horizontal: la
lista sale por la izquierda y el detalle entra desde la derecha. El detalle se
cierra con una cápsula que une la flecha de retroceso y el título.

Dos tipos de detalle, como pide el plan:

* **Selección múltiple** (varios ajustes en la misma tarjeta): hay un botón de
  confirmación arriba y el guardado se valida al retroceder.
* **Selección única** (una opción entre varias): al pulsar se marca, se aplica
  al instante y se vuelve solo.

Todo el color sale de ``lib/design_tokens``: ningún widget escribe un color a
mano.
"""

from __future__ import annotations

from typing import Optional

try:
    from PyQt6.QtCore import (
        QEasingCurve,
        QPoint,
        QPropertyAnimation,
        QRect,
        Qt,
        pyqtProperty,
        pyqtSignal,
    )
    from PyQt6.QtGui import QColor, QPainter, QPen
    from PyQt6.QtWidgets import (
        QFrame,
        QGraphicsDropShadowEffect,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QScrollArea,
        QSizePolicy,
        QVBoxLayout,
        QWidget,
    )

    PYQT6_AVAILABLE = True
except ImportError:  # pragma: no cover - entorno sin Qt
    # Sin PyQt6 el CLI headless debe seguir arrancando: los sustitutos inertes
    # evitan el ``NameError`` que abortaba el import de nivel superior.
    PYQT6_AVAILABLE = False

    class _QtStubMeta(type):
        def __getattr__(cls, name):
            return _QtStub

    class _QtStub(metaclass=_QtStubMeta):
        def __init__(self, *args, **kwargs):
            pass

        def __getattr__(self, name):
            return _QtStub()

        def __call__(self, *args, **kwargs):
            return _QtStub()

    QFrame = QWidget = QLabel = QPushButton = QScrollArea = _QtStub
    QHBoxLayout = QVBoxLayout = QSizePolicy = QGraphicsDropShadowEffect = _QtStub
    QPropertyAnimation = QEasingCurve = QPoint = QRect = _QtStub
    QColor = QPainter = QPen = Qt = _QtStub
    pyqtSignal = pyqtProperty = _QtStub

from lib.design_tokens import (
    ACCENT,
    BORDER,
    CARD_RADIUS,
    FONT_STACK,
    SIDEBAR_TEXT_GRAY,
    SURFACE_ELEVATED,
    SURFACE_HOVER,
    TEXT,
    TEXT_DIM,
    TITLE_SIZE,
    with_alpha,
)

CARD_HEIGHT = 58
INDICATOR_WIDTH = 3
ARROW_FORWARD = "\u2192"   # →
ARROW_EXTERNAL = "\u2197"  # ↗
ARROW_BACK = "\u2039"      # ‹
SLIDE_MS = 260


class SettingsCard(QFrame):
    """Tarjeta pulsable: icono, título, subtítulo y flecha de acción."""

    clicked = pyqtSignal()

    def __init__(self, title, icon=None, trailing=ARROW_FORWARD, subtitle="", parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsCard")
        self.setFixedHeight(CARD_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        self._accent = ACCENT
        self._selected = False
        self._hovered = False
        self._progress = 0.0
        self._indicator_anim: Optional["QPropertyAnimation"] = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        self.icon_lbl = QLabel(self)
        self.icon_lbl.setFixedSize(22, 22)
        self.icon_lbl.setStyleSheet("background:transparent;border:none;")
        if icon is not None:
            try:
                self.icon_lbl.setPixmap(icon.pixmap(20, 20))
            except Exception:
                pass
        layout.addWidget(self.icon_lbl)

        text_box = QVBoxLayout()
        text_box.setContentsMargins(0, 0, 0, 0)
        text_box.setSpacing(1)
        self.title_lbl = QLabel(title, self)
        self.title_lbl.setStyleSheet(
            f"color:{TEXT};font-family:{FONT_STACK};font-size:13px;"
            "font-weight:600;background:transparent;border:none;"
        )
        text_box.addWidget(self.title_lbl)
        self.subtitle_lbl = QLabel(subtitle, self)
        self.subtitle_lbl.setStyleSheet(
            f"color:{TEXT_DIM};font-family:{FONT_STACK};font-size:11px;"
            "background:transparent;border:none;"
        )
        self.subtitle_lbl.setVisible(bool(subtitle))
        text_box.addWidget(self.subtitle_lbl)
        layout.addLayout(text_box, 1)

        self.arrow_lbl = QLabel(trailing, self)
        self.arrow_lbl.setStyleSheet(
            f"color:{SIDEBAR_TEXT_GRAY};font-family:{FONT_STACK};font-size:15px;"
            "background:transparent;border:none;"
        )
        layout.addWidget(self.arrow_lbl)

    # --- Estado visual -------------------------------------------------
    def set_accent(self, accent: str) -> None:
        if accent:
            self._accent = str(accent)
            self.update()

    def set_trailing(self, glyph: str) -> None:
        self.arrow_lbl.setText(glyph)

    def set_subtitle(self, text: str) -> None:
        self.subtitle_lbl.setText(text or "")
        self.subtitle_lbl.setVisible(bool(text))

    def set_title(self, text: str) -> None:
        self.title_lbl.setText(text)

    def set_selected(self, selected: bool) -> None:
        """Marca la tarjeta: indicador naranja a la izquierda y contorno activo."""
        self._selected = bool(selected)
        self._animate_indicator(1.0 if self._selected else 0.0)

    def is_selected(self) -> bool:
        return self._selected

    def _get_indicator(self) -> float:
        return self._progress

    def _set_indicator(self, value: float) -> None:
        self._progress = float(value)
        self.update()

    indicatorProgress = pyqtProperty(float, _get_indicator, _set_indicator)

    def _animate_indicator(self, target: float) -> None:
        if not PYQT6_AVAILABLE:
            self._set_indicator(target)
            return
        if self._indicator_anim is None:
            # Una sola animación reutilizada: con ``DeleteWhenStopped`` Qt
            # destruye el objeto C++ y el siguiente ``stop()`` revienta.
            self._indicator_anim = QPropertyAnimation(self, b"indicatorProgress", self)
            self._indicator_anim.setDuration(180)
            self._indicator_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._indicator_anim.stop()
        self._indicator_anim.setStartValue(self._progress)
        self._indicator_anim.setEndValue(float(target))
        self._indicator_anim.start()

    def enterEvent(self, event):  # noqa: N802 - API de Qt
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):  # noqa: N802 - API de Qt
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event):  # noqa: N802 - API de Qt
        if event.button() == Qt.MouseButton.LeftButton and self.rect().contains(
            event.position().toPoint()
        ):
            self.clicked.emit()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):  # noqa: N802 - API de Qt
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(0, 0, -1, -1)

        painter.setBrush(QColor(SURFACE_HOVER if self._hovered else SURFACE_ELEVATED))
        pen = QPen(QColor(self._accent if self._selected else BORDER))
        pen.setWidth(2 if self._selected else 1)
        painter.setPen(pen)
        painter.drawRoundedRect(rect, CARD_RADIUS, CARD_RADIUS)

        if self._progress > 0.01:
            height = int((rect.height() - 20) * min(1.0, self._progress))
            top = rect.center().y() - height // 2
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(self._accent))
            painter.drawRoundedRect(
                QRect(4, top, INDICATOR_WIDTH, max(2, height)), 2, 2
            )


class SettingsBackButton(QPushButton):
    """Cápsula que une la flecha de retroceso y el título del detalle."""

    def __init__(self, title: str, parent=None):
        super().__init__(f"{ARROW_BACK}  {title}", parent)
        self.setObjectName("SettingsBackButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(34)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(
            "QPushButton#SettingsBackButton {"
            f" background:{with_alpha('#FFFFFF', 0.06)};"
            f" border:1px solid {BORDER}; border-radius:17px;"
            f" color:{TEXT}; font-family:{FONT_STACK}; font-size:13px;"
            " font-weight:600; padding:0 16px; text-align:left; }"
            "QPushButton#SettingsBackButton:hover {"
            f" background:{with_alpha('#FFFFFF', 0.12)}; }}"
        )

    def set_title(self, title: str) -> None:
        self.setText(f"{ARROW_BACK}  {title}")


class SettingsDetailPage(QWidget):
    """Página de detalle: sólo el cuerpo desplazable.

    El botón de retroceso y el de confirmación viven en la barra superior de la
    página de configuración, unificados con el título (ver ``bugs.txt`` 3.2).
    """

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.body = QVBoxLayout()
        self.body.setContentsMargins(0, 0, 0, 0)
        self.body.setSpacing(10)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea{background:transparent;border:none;}")
        content = QWidget()
        content.setStyleSheet("background:transparent;")
        content.setLayout(self.body)
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

    def add_widget(self, widget) -> None:
        self.body.addWidget(widget)

    def add_layout(self, layout) -> None:
        self.body.addLayout(layout)

    def add_stretch(self) -> None:
        self.body.addStretch()


class SettingsListPage(QWidget):
    """Página raíz: lista vertical de tarjetas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)
        self._cards = []
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setStyleSheet("QScrollArea{background:transparent;border:none;}")
        content = QWidget()
        content.setStyleSheet("background:transparent;")
        self._layout = QVBoxLayout(content)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(8)
        self._scroll.setWidget(content)
        root.addWidget(self._scroll, 1)

    def add_card(self, card: SettingsCard) -> SettingsCard:
        self._cards.append(card)
        self._layout.addWidget(card)
        return card

    def add_stretch(self) -> None:
        self._layout.addStretch()

    def cards(self):
        return list(self._cards)

    def set_accent(self, accent: str) -> None:
        for card in self._cards:
            card.set_accent(accent)


class SettingsNavigator(QWidget):
    """Pila de páginas con desplazamiento horizontal al entrar y al salir."""

    depthChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsNavigator")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("QWidget#SettingsNavigator{background:transparent;border:none;}")
        self._pages = []
        self._anim: Optional["QPropertyAnimation"] = None
        self._busy = False

    # --- Pila ----------------------------------------------------------
    def set_root(self, page) -> None:
        for old in self._pages:
            old.setParent(None)
            old.deleteLater()
        self._pages = [page]
        page.setParent(self)
        page.resize(self.size())
        page.move(0, 0)
        page.show()
        self.depthChanged.emit(0)

    def push(self, page) -> None:
        if self._busy or not self._pages:
            return
        current = self._pages[-1]
        page.setParent(self)
        page.resize(self.size())
        page.move(self.width(), 0)
        page.show()
        page.raise_()
        self._pages.append(page)
        self._slide(current, page, forward=True)
        self.depthChanged.emit(len(self._pages) - 1)

    def pop(self) -> None:
        if self._busy or len(self._pages) < 2:
            return
        current = self._pages[-1]
        target = self._pages[-2]
        target.setParent(self)
        target.resize(self.size())
        target.move(-self.width(), 0)
        target.show()
        target.raise_()
        self._slide(current, target, forward=False)
        self.depthChanged.emit(len(self._pages) - 2)

    def depth(self) -> int:
        return max(0, len(self._pages) - 1)

    def busy(self) -> bool:
        """Indica si hay una transición en curso (no admite otra navegación)."""
        return bool(self._busy)

    def current(self):
        return self._pages[-1] if self._pages else None

    # --- Animación -----------------------------------------------------
    def _slide(self, leaving, entering, forward: bool) -> None:
        if not PYQT6_AVAILABLE:
            leaving.hide()
            entering.move(0, 0)
            if not forward:
                self._pages.pop()
            return
        self._busy = True
        self._anim = QPropertyAnimation(leaving, b"pos", self)
        self._anim.setDuration(SLIDE_MS)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.setStartValue(leaving.pos())
        self._anim.setEndValue(QPoint(-self.width() if forward else self.width(), 0))

        self._anim_enter = QPropertyAnimation(entering, b"pos", self)
        self._anim_enter.setDuration(SLIDE_MS)
        self._anim_enter.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim_enter.setStartValue(entering.pos())
        self._anim_enter.setEndValue(QPoint(0, 0))

        def _finished():
            # La página que sale se conserva: sus controles son los que el
            # anfitrión usa para leer la configuración, y destruirla dejaba
            # referencias colgando (``RuntimeError: wrapped C/C++ object ...``).
            leaving.hide()
            leaving.move(0, 0)
            entering.move(0, 0)
            if not forward:
                self._pages.pop()
            self._busy = False
            # La pila se estabiliza al final de la animación: se anuncia la
            # profundidad definitiva para que el anfitrión refresque su barra.
            self.depthChanged.emit(self.depth())

        self._anim.finished.connect(_finished)
        self._anim.start()
        self._anim_enter.start()

    def resizeEvent(self, event):  # noqa: N802 - API de Qt
        super().resizeEvent(event)
        for page in self._pages:
            page.resize(self.size())
        if self._pages and not self._busy:
            self._pages[-1].move(0, 0)


class SettingsOptionRow(QFrame):
    """Opción de selección única: al pulsarla se aplica y se vuelve solo."""

    chosen = pyqtSignal(str)

    def __init__(self, label: str, value: str, checked: bool = False, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsOptionRow")
        self.setFixedHeight(48)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._value = value
        self._checked = bool(checked)
        self._hovered = False
        self._accent = ACCENT

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)
        self.label_lbl = QLabel(label, self)
        self.label_lbl.setStyleSheet(
            f"color:{TEXT};font-family:{FONT_STACK};font-size:13px;"
            "background:transparent;border:none;"
        )
        layout.addWidget(self.label_lbl, 1)
        self.check_lbl = QLabel("\u2713", self)
        self.check_lbl.setStyleSheet(
            f"color:{ACCENT};font-family:{FONT_STACK};font-size:14px;"
            "font-weight:700;background:transparent;border:none;"
        )
        self.check_lbl.setVisible(self._checked)
        layout.addWidget(self.check_lbl)

    def value(self) -> str:
        return self._value

    def set_accent(self, accent: str) -> None:
        if accent:
            self._accent = str(accent)
            self.check_lbl.setStyleSheet(
                f"color:{self._accent};font-family:{FONT_STACK};font-size:14px;"
                "font-weight:700;background:transparent;border:none;"
            )
            self.update()

    def set_checked(self, checked: bool) -> None:
        self._checked = bool(checked)
        self.check_lbl.setVisible(self._checked)
        self.update()

    def is_checked(self) -> bool:
        return self._checked

    def enterEvent(self, event):  # noqa: N802 - API de Qt
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):  # noqa: N802 - API de Qt
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event):  # noqa: N802 - API de Qt
        if event.button() == Qt.MouseButton.LeftButton and self.rect().contains(
            event.position().toPoint()
        ):
            self.chosen.emit(self._value)
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):  # noqa: N802 - API de Qt
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(0, 0, -1, -1)
        painter.setBrush(QColor(SURFACE_HOVER if self._hovered else SURFACE_ELEVATED))
        pen = QPen(QColor(self._accent if self._checked else BORDER))
        pen.setWidth(2 if self._checked else 1)
        painter.setPen(pen)
        painter.drawRoundedRect(rect, CARD_RADIUS, CARD_RADIUS)


def apply_soft_shadow(widget, blur: int = 24, offset: int = 6, alpha: int = 140) -> None:
    """Sombra suave bajo un widget, como el relieve del logo de ``Acerca de``."""
    if not PYQT6_AVAILABLE:
        return
    try:
        shadow = QGraphicsDropShadowEffect(widget)
        shadow.setBlurRadius(blur)
        shadow.setOffset(0, offset)
        shadow.setColor(QColor(0, 0, 0, alpha))
        widget.setGraphicsEffect(shadow)
    except Exception:
        pass


def card_icon(key: str, size: int = 20, dark: bool = True):
    """Icono de tarjeta; nunca lanza si el tema no está disponible."""
    try:
        from lib.app_icons import get_icon

        return get_icon(key, size, dark=dark)
    except Exception:
        return None


def section_caption(text: str) -> "QLabel":
    """Rótulo diminuto en mayúsculas sobre un grupo de tarjetas."""
    lbl = QLabel(text.upper())
    lbl.setStyleSheet(
        f"color:{TEXT_DIM};font-family:{FONT_STACK};font-size:10px;"
        "font-weight:700;letter-spacing:0.8px;background:transparent;"
        "padding-left:4px;"
    )
    return lbl


def title_size() -> int:
    return TITLE_SIZE
