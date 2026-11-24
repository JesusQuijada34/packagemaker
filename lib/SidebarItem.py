# -*- coding: utf-8 -*-
"""Ítem de navegación lateral con indicador de selección propio.

El indicador es una barra corta y redondeada pegada al borde izquierdo y
centrada verticalmente, en vez del ``border-left`` de altura completa. El texto
y el icono usan el **mismo gris oscuro** en ambos temas; la selección se
distingue por el fondo y por el indicador de acento, que crece y aparece con
una transición al cambiar de página. El resalte del ratón se pinta directamente
en ``paintEvent``: reescribir la hoja de estilo en cada fotograma producía un
re-polish que hacía parpadear el ítem.
"""

from __future__ import annotations

import os

try:
    from PyQt6.QtCore import (
        QEasingCurve,
        QPropertyAnimation,
        QRect,
        QSize,
        Qt,
        pyqtProperty,
    )
    from PyQt6.QtGui import QColor, QIcon, QPainter
    from PyQt6.QtWidgets import QPushButton

    PYQT6_AVAILABLE = True
except ImportError:  # pragma: no cover - entorno sin Qt
    PYQT6_AVAILABLE = False

    class QPushButton:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            pass

        def setFixedHeight(self, *args):
            pass

        def setIconSize(self, *args):
            pass

        def setIcon(self, *args):
            pass

    class QIcon:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            pass

    def pyqtProperty(*args, **kwargs):  # type: ignore[no-redef]
        return property(*args, **kwargs)

    QPropertyAnimation = None  # type: ignore[assignment]
    QEasingCurve = None  # type: ignore[assignment]
    QPainter = None  # type: ignore[assignment]
    QRect = None  # type: ignore[assignment]
    QColor = None  # type: ignore[assignment]


from lib.design_tokens import (
    ACCENT,
    CONTROL_RADIUS,
    FONT_STACK,
    SIDEBAR_ICON_INSET,
    SIDEBAR_INDICATOR_HEIGHT,
    SIDEBAR_INDICATOR_WIDTH,
    SIDEBAR_ITEM_HEIGHT,
    SIDEBAR_TEXT_DARK,
    SIDEBAR_TEXT_LIGHT,
    SIDEBAR_TEXT_SELECTED_DARK,
    SIDEBAR_TEXT_SELECTED_LIGHT,
    with_alpha,
)

# Paletas por tema para el texto del ítem (normal, seleccionado). El texto y el
# icono usan el **mismo gris oscuro** en ambos temas; la selección se distingue
# por el fondo y por el indicador de acento.
TEXT_COLORS = {
    True: {"normal": SIDEBAR_TEXT_DARK, "selected": SIDEBAR_TEXT_SELECTED_DARK},
    False: {"normal": SIDEBAR_TEXT_LIGHT, "selected": SIDEBAR_TEXT_SELECTED_LIGHT},
}
# Tinte del resalte al pasar el ratón: (rojo, verde, azul, alfa 0-255). Se pinta
# en ``paintEvent`` en vez de reescribir la hoja de estilo en cada fotograma:
# cada ``setStyleSheet`` fuerza un re-polish y el ítem parpadeaba entre el color
# de la regla heredada de la barra y el gris de reposo.
HOVER_TINTS = {
    True: (255, 255, 255, 18),
    False: (15, 23, 42, 18),
}
# Duración del crecimiento/desvanecido del indicador de selección.
INDICATOR_FADE_MS = 180
HOVER_FADE_MS = 140
# Selector propio: incluye id y atributo dinámico para superar en especificidad
# a la regla ``QWidget#NavigationSidebar QPushButton:hover`` heredada.
_ITEM_SELECTOR = 'QPushButton#SidebarNavItem[pmNavItem="true"]'



class SidebarItem(QPushButton):
    """Botón de navegación lateral con modo compacto Fluent."""

    def __init__(self, text, icon=None, parent=None, dark=True, icon_key=None):
        super().__init__(text, parent)
        self._label_text = text
        self._compact = False
        self._dark = bool(dark)
        self._icon_key = icon_key
        # Acento del indicador: el token por defecto, o el que fije la app al
        # reaplicar el tema (la preferencia del usuario manda sobre el token).
        self._accent = ACCENT
        # Progreso del indicador (0.0 oculto, 1.0 visible). Se anima para que el
        # cambio de página tenga una transición en vez de aparecer de golpe.
        self._indicator_progress = 1.0 if self.isChecked() else 0.0
        self._indicator_animation = None
        self._hover_progress = 0.0
        self._hover_animation = None
        self.setObjectName("SidebarNavItem")
        self.setProperty("pmNavItem", "true")
        self.setFixedHeight(SIDEBAR_ITEM_HEIGHT)
        self.setIconSize(QSize(24, 24))
        self._set_icon(icon)
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style()
        self.toggled.connect(self._on_toggled)

    # -- indicador animado --------------------------------------------
    def _get_indicator_progress(self) -> float:
        return self._indicator_progress

    def _set_indicator_progress(self, value: float) -> None:
        self._indicator_progress = max(0.0, min(1.0, float(value)))
        self.update()

    indicatorProgress = pyqtProperty(
        float, _get_indicator_progress, _set_indicator_progress
    )

    # -- resalte del ratón (pintado, sin re-polish) --------------------
    def _get_hover_progress(self) -> float:
        return self._hover_progress

    def _set_hover_progress(self, value: float) -> None:
        self._hover_progress = max(0.0, min(1.0, float(value)))
        self.update()

    hoverProgress = pyqtProperty(float, _get_hover_progress, _set_hover_progress)

    def _animate_hover(self, target: float) -> None:
        # El ítem seleccionado ya se distingue por el fondo y el indicador: no
        # se le añade otro tinte al pasar el ratón.
        if target > 0.0 and self.isChecked():
            return
        if not PYQT6_AVAILABLE or QPropertyAnimation is None:
            self._set_hover_progress(target)
            return
        if self._hover_animation is None:
            self._hover_animation = QPropertyAnimation(self, b"hoverProgress", self)
            self._hover_animation.setDuration(HOVER_FADE_MS)
            self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation = self._hover_animation
        animation.stop()
        animation.setStartValue(self._hover_progress)
        animation.setEndValue(float(target))
        animation.start()

    def enterEvent(self, event):  # noqa: N802 (API Qt)
        self._animate_hover(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event):  # noqa: N802 (API Qt)
        self._animate_hover(0.0)
        super().leaveEvent(event)

    def _on_toggled(self, checked: bool) -> None:
        self._animate_indicator(1.0 if checked else 0.0)
        if checked:
            # Al seleccionar el ítem se retira el tinte de hover: si no, el
            # fondo de selección y el de hover se sumaban mientras el puntero
            # seguía encima.
            if self._hover_animation is not None:
                self._hover_animation.stop()
            self._set_hover_progress(0.0)

    def _animate_indicator(self, target: float) -> None:
        """Lleva el indicador a *target* con una transición corta."""
        if not PYQT6_AVAILABLE or QPropertyAnimation is None:
            self._set_indicator_progress(target)
            return
        if self._indicator_animation is None:
            # Una sola animación reutilizada: con ``DeleteWhenStopped`` Qt
            # destruiría el objeto C++ y el siguiente ``stop()`` fallaría.
            self._indicator_animation = QPropertyAnimation(
                self, b"indicatorProgress", self
            )
            self._indicator_animation.setDuration(INDICATOR_FADE_MS)
            self._indicator_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation = self._indicator_animation
        animation.stop()
        animation.setStartValue(self._indicator_progress)
        animation.setEndValue(float(target))
        animation.start()

    def _set_icon(self, icon=None):
        """Asigna el icono, repintando el SVG con el color de la barra lateral.

        Cuando se conoce la clave del icono (``icon_key``) se regenera con el
        gris de la barra lateral; sin clave se usa el icono tal cual.
        """
        if self._icon_key:
            from lib.app_icons import get_sidebar_icon

            self.setIcon(get_sidebar_icon(self._icon_key, 24, dark=self._dark))
            return
        if isinstance(icon, QIcon):
            self.setIcon(icon)
        elif icon and os.path.exists(str(icon)):
            self.setIcon(QIcon(str(icon)))

    def set_label_text(self, text):
        self._label_text = text
        self.setText("" if self._compact else text)
        self.setToolTip(text if self._compact else "")

    def set_accent(self, accent: str) -> None:
        """Fija el color del indicador y del fondo de selección."""
        if accent and str(accent) != self._accent:
            self._accent = str(accent)
            self._apply_style()
            self.update()

    def set_compact(self, compact):
        self._compact = bool(compact)
        self.set_label_text(self._label_text)
        self._apply_style()

    def set_dark(self, dark):
        """Ajusta los colores al tema activo (claro u oscuro)."""
        dark = bool(dark)
        if dark == self._dark:
            return
        self._dark = dark
        self._set_icon()
        self._apply_style()
        self.update()

    def _apply_style(self):
        palette = TEXT_COLORS[self._dark]
        # El indicador y el resalte del ratón los pinta ``paintEvent``; el QSS
        # sólo fija texto, relleno de selección y tipografía. El selector lleva
        # id y atributo para imponerse a la regla heredada de la barra lateral.
        self.setStyleSheet(f"""
            {_ITEM_SELECTOR} {{
                background-color: transparent;
                color: {palette['normal']};
                text-align: left;
                padding: 0 14px 0 {SIDEBAR_ICON_INSET}px;
                border: none;
                border-radius: {CONTROL_RADIUS}px;
                font-family: {FONT_STACK};
                font-size: 14px;
                font-weight: 500;
            }}
            {_ITEM_SELECTOR}:hover {{
                background-color: transparent;
                border: none;
                color: {palette['selected']};
            }}
            {_ITEM_SELECTOR}:checked {{
                background-color: {with_alpha(self._accent, 0.18)};
                border: none;
                color: {palette['selected']};
            }}
            {_ITEM_SELECTOR}:focus {{
                outline: none;
            }}
        """)
        if self._compact:
            self.setStyleSheet(self.styleSheet() + f"""
                {_ITEM_SELECTOR} {{
                    text-align: center;
                    padding: 0;
                }}
            """)

    def _paint_hover_background(self) -> None:
        if self._hover_progress <= 0.0 or not PYQT6_AVAILABLE:
            return
        red, green, blue, alpha = HOVER_TINTS[self._dark]
        color = QColor(red, green, blue)
        color.setAlphaF((alpha / 255.0) * self._hover_progress)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawRoundedRect(self.rect(), CONTROL_RADIUS, CONTROL_RADIUS)
        painter.end()

    # -- indicador de selección ---------------------------------------
    def paintEvent(self, event):  # noqa: N802 (API Qt)
        self._paint_hover_background()
        super().paintEvent(event)
        progress = self._indicator_progress
        if progress <= 0.0 or not PYQT6_AVAILABLE:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        # El indicador crece y aparece con el progreso animado; el color azul
        # mantiene su intensidad plena al final de la transición.
        color = QColor(self._accent)
        color.setAlphaF(progress)
        painter.setBrush(color)
        height = max(1.0, SIDEBAR_INDICATOR_HEIGHT * progress)
        y = (self.height() - height) / 2.0
        radius = SIDEBAR_INDICATOR_WIDTH / 2
        painter.drawRoundedRect(
            QRect(0, int(y), SIDEBAR_INDICATOR_WIDTH, int(height)),
            radius,
            radius,
        )
        painter.end()
