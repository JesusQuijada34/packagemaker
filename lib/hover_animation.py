# -*- coding: utf-8 -*-
"""Transiciones suaves de fondo para botones e ítems de la interfaz.

Qt no admite ``transition`` en QSS, así que la fluidez se consigue animando el
color de fondo con :class:`QPropertyAnimation` y regenerando la hoja de estilo
en cada fotograma. Para no duplicar estilos, el animador **parte del QSS que ya
tiene el widget** y sólo sustituye las declaraciones de fondo, de modo que
texto, borde, radios e iconos se siguen pintando con las reglas originales.

Uso típico::

    from lib.hover_animation import enable_hover_fade
    enable_hover_fade(button, hover_color="#1084D8")

Si el widget no tiene ninguna declaración de fondo, la función no hace nada.
"""

from __future__ import annotations

import re
from typing import Optional

try:
    from PyQt6.QtCore import (
        QEasingCurve,
        QEvent,
        QObject,
        QPropertyAnimation,
        pyqtProperty,
    )
    from PyQt6.QtGui import QColor
    from PyQt6.QtWidgets import QWidget

    PYQT6_AVAILABLE = True
except ImportError:  # pragma: no cover - entorno sin Qt
    PYQT6_AVAILABLE = False
    QObject = object  # type: ignore[assignment,misc]
    QColor = None  # type: ignore[assignment]
    QWidget = object  # type: ignore[assignment,misc]
    QEvent = None  # type: ignore[assignment]

    def pyqtProperty(*args, **kwargs):  # type: ignore[misc]
        """Respaldo sin Qt: la propiedad se comporta como un atributo normal."""
        def _decorator(func):
            return property(func)
        return _decorator

# ``background: <valor>;`` o ``background-color: <valor>;``
_BACKGROUND_RE = re.compile(
    r"(background(?:-color)?\s*:\s*)([^;]+)(;)", re.IGNORECASE
)
# Sólo se reescriben valores que son realmente un color.
_COLOR_VALUE_RE = re.compile(
    r"^\s*(#[0-9a-fA-F]{3,8}|rgba?\([^)]*\))\s*$"
)
# Un bloque de regla: ``selector { declaraciones }``.
_RULE_RE = re.compile(r"([^{}]*)\{([^{}]*)\}", re.DOTALL)
_HOVER_MARKER = ":hover"


def _blend(start: str, end: str, progress: float) -> str:
    """Interpola dos colores y devuelve un ``rgba(...)`` legible por QSS."""
    a = QColor(start)
    b = QColor(end)
    if not a.isValid() or not b.isValid():
        return end if progress >= 0.5 else start
    r = round(a.red() + (b.red() - a.red()) * progress)
    g = round(a.green() + (b.green() - a.green()) * progress)
    bl = round(a.blue() + (b.blue() - a.blue()) * progress)
    alpha = a.alpha() + (b.alpha() - a.alpha()) * progress
    return f"rgba({r}, {g}, {bl}, {alpha / 255:.3f})"


def _replace_background(body: str, color: str) -> str:
    """Sustituye las declaraciones de fondo por *color* dentro de un bloque."""

    def _replace(decl: "re.Match[str]") -> str:
        if not _COLOR_VALUE_RE.match(decl.group(2)):
            return decl.group(0)
        return f"{decl.group(1)}{color}{decl.group(3)}"

    return _BACKGROUND_RE.sub(_replace, body)


def _base_background_color(qss: str) -> Optional[str]:
    """Color de fondo del estado de reposo (una regla sin ``:hover``)."""
    for match in _RULE_RE.finditer(qss):
        if _HOVER_MARKER in match.group(1):
            continue
        for decl in _BACKGROUND_RE.finditer(match.group(2)):
            value = decl.group(2).strip()
            if _COLOR_VALUE_RE.match(value):
                return value
    return None


def _base_selector(qss: str) -> Optional[str]:
    """Primer selector sin pseudo-estado, para inyectar una regla ``:hover``."""
    for match in _RULE_RE.finditer(qss):
        selector = match.group(1).strip()
        if selector and _HOVER_MARKER not in selector:
            return selector
    return None


def _is_pure_hover(selector: str) -> bool:
    """¿Es una regla ``:hover`` sin otro pseudo-estado?

    ``QPushButton:hover`` sí; ``QPushButton:checked:hover`` no. Así un ítem ya
    seleccionado conserva su color de selección al pasar el ratón.
    """
    if _HOVER_MARKER not in selector:
        return False
    without_hover = selector.replace(_HOVER_MARKER, "")
    return not any(
        marker in without_hover
        for marker in (":checked", ":pressed", ":focus", ":disabled", ":selected", "::")
    )


def _with_hover_background(qss: str, color: str) -> str:
    """Pinta el fondo de la regla ``:hover`` con *color*.

    Qt aplica la regla ``:hover`` mientras el puntero está encima, así que
    animar la regla base sería invisible: el color animado debe escribirse en
    el bloque ``:hover``. Sólo se toca la regla ``:hover`` pura; los estados
    combinados (``:checked:hover``) quedan intactos. Si el widget no declara
    ningún ``:hover``, se añade uno.
    """
    found = False

    def _patch_rule(match: "re.Match[str]") -> str:
        nonlocal found
        selector, body = match.group(1), match.group(2)
        if not _is_pure_hover(selector):
            return match.group(0)
        found = True
        return f"{selector}{{{_replace_background(body, color)}}}"

    patched = _RULE_RE.sub(_patch_rule, qss)
    if found:
        return patched
    selector = _base_selector(qss)
    if selector is None:
        return patched
    return f"{patched}\n{selector}{_HOVER_MARKER}{{background-color:{color};}}"


class _HoverFade(QObject):
    """Anima el fondo de un widget entre su color base y el de resalte."""

    def __init__(
        self,
        widget: "QWidget",
        hover_color: str,
        duration_ms: int,
        only_when: Optional[object] = None,
    ):
        super().__init__(widget)
        self._widget = widget
        self._hover_color = hover_color
        self._duration_ms = max(0, int(duration_ms))
        self._only_when = only_when
        # El QSS base se captura al entrar el puntero, no al construir: la app
        # re-aplica estilos (tema, acento, densidad) después de crear los
        # widgets, y un snapshot temprano restauraría un estilo obsoleto.
        self._base_qss = widget.styleSheet()
        self._base_color = _base_background_color(self._base_qss)
        self._hovered = False
        self._animation: Optional[QPropertyAnimation] = None
        widget.installEventFilter(self)

    # -- propiedad animada ------------------------------------------------ #
    def _get_progress(self) -> float:
        return self._progress

    def _set_progress(self, value: float) -> None:
        self._progress = float(value)
        color = _blend(self._base_color, self._hover_color, self._progress)
        self._widget.setStyleSheet(_with_hover_background(self._base_qss, color))

    _progress = 0.0
    progress = pyqtProperty(float, _get_progress, _set_progress)

    def refresh(self) -> None:
        """Vuelve a leer el QSS base del widget tras un cambio de estilo."""
        self._base_qss = self._widget.styleSheet()
        self._base_color = _base_background_color(self._base_qss)
        self._progress = 0.0

    def set_hover_color(self, hover_color: str) -> None:
        """Cambia el color de destino (p. ej. al alternar el tema)."""
        self._hover_color = hover_color
        self.refresh()

    # -- eventos ---------------------------------------------------------- #
    def eventFilter(self, obj, event):  # noqa: N802 - firma de Qt
        if QEvent is None:  # pragma: no cover - entorno sin Qt
            return False
        if event.type() == QEvent.Type.Enter:
            self._animate(1.0)
        elif event.type() == QEvent.Type.Leave:
            self._animate(0.0)
        return False

    def _animate(self, target: float) -> None:
        if self._only_when is not None and not self._only_when():
            return
        if self._hovered == (target > 0.5):
            return
        if target > 0.5:
            # Re-captura el estilo actual justo antes de animar.
            self.refresh()
            if self._base_color is None:
                return
        self._hovered = target > 0.5
        if self._animation is not None:
            self._animation.stop()
        animation = QPropertyAnimation(self, b"progress")
        animation.setDuration(self._duration_ms)
        animation.setStartValue(self._progress)
        animation.setEndValue(target)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        self._animation = animation


def enable_hover_fade(
    widget: "QWidget",
    hover_color: str,
    duration_ms: int = 150,
    only_when: Optional[object] = None,
) -> Optional["_HoverFade"]:
    """Añade una transición de fondo al pasar el ratón sobre *widget*.

    ``hover_color`` es el color de destino; el de partida se toma del propio
    QSS del widget en el momento del primer hover. ``only_when`` permite
    desactivar la animación (por ejemplo, en un ítem de barra lateral ya
    seleccionado). Devuelve el animador, o ``None`` si Qt no está disponible.
    """
    if not PYQT6_AVAILABLE:
        return None
    fade = _HoverFade(widget, hover_color, duration_ms, only_when=only_when)
    widget._hover_fade = fade  # mantiene viva la referencia
    return fade
