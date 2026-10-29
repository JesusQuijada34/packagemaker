"""Shared QML animation controller for QWidget-based interfaces."""

from __future__ import annotations

import itertools
import sys
from pathlib import Path
from typing import Callable, Dict, Optional

try:
    from PyQt6.QtCore import QEasingCurve, QObject, QUrl, QPropertyAnimation
    from PyQt6.QtQml import QQmlComponent, QQmlEngine
    from PyQt6.QtWidgets import QWidget
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    QObject = object
    QWidget = object


if PYQT6_AVAILABLE:
    _EASING_NAMES = {
        QEasingCurve.Type.OutCubic: "outCubic",
        QEasingCurve.Type.OutExpo: "outExpo",
        QEasingCurve.Type.OutBounce: "outBounce",
        QEasingCurve.Type.InOutCubic: "inOutCubic",
        QEasingCurve.Type.Linear: "linear",
    }
else:
    _EASING_NAMES = {}


def resolve_qml_resource_path() -> Path:
    """Find the shared QML animation controller in source and frozen builds."""
    candidates = []
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        candidates.extend([
            Path(sys._MEIPASS) / "lib" / "animation_controller.qml",
            Path(sys._MEIPASS) / "animation_controller.qml",
        ])
    candidates.extend([
        Path(__file__).resolve().with_name("animation_controller.qml"),
        Path(__file__).resolve().parent.parent / "lib" / "animation_controller.qml",
    ])
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return candidates[0]


class QmlAnimationController(QObject):
    """Loads one QML controller and routes property animations through it."""

    def __init__(self):
        if not PYQT6_AVAILABLE:
            raise RuntimeError("QtQml/PyQt6 is required for QML animations.")
        super().__init__()
        self._engine = QQmlEngine()
        self._component = QQmlComponent(self._engine)
        qml_path = resolve_qml_resource_path()
        if not qml_path.is_file():
            raise RuntimeError(f"No se encontró el controlador QML en: {qml_path}")
        self._component.setData(qml_path.read_bytes(), QUrl.fromLocalFile(str(qml_path)))
        if self._component.isError():
            errors = "\n".join(error.toString() for error in self._component.errors())
            raise RuntimeError(f"No se pudo cargar el controlador QML:\n{errors}")
        self._root = self._component.create()
        if self._root is None:
            errors = "\n".join(error.toString() for error in self._component.errors())
            raise RuntimeError(f"No se pudo crear el controlador QML:\n{errors}")
        self._root.animationFinished.connect(self._on_animation_finished)
        self._callbacks: Dict[int, Callable[[], None]] = {}
        self._active_animations: Dict[tuple, int] = {}
        self._animation_keys: Dict[int, tuple] = {}
        self._ids = itertools.count(1)

    def animate(
        self,
        target: QWidget,
        property_name: str,
        start_value,
        end_value,
        duration_ms: int = 240,
        easing=None,
        on_finished: Optional[Callable[[], None]] = None,
    ) -> int:
        animation_id = next(self._ids)
        animation_key = (id(target), property_name)
        previous_id = self._active_animations.get(animation_key)
        if previous_id is not None:
            self._root.cancelRequested.emit(previous_id)
            self._callbacks.pop(previous_id, None)
            self._animation_keys.pop(previous_id, None)
        if on_finished:
            self._callbacks[animation_id] = on_finished
        easing_name = _EASING_NAMES.get(easing, "outCubic")
        try:
            self._active_animations[animation_key] = animation_id
            self._animation_keys[animation_id] = animation_key
            self._root.animateRequested.emit(
                target,
                property_name,
                start_value,
                end_value,
                int(duration_ms),
                easing_name,
                animation_id,
            )
        except (AttributeError, RuntimeError, TypeError) as exc:
            self._callbacks.pop(animation_id, None)
            self._animation_keys.pop(animation_id, None)
            if self._active_animations.get(animation_key) == animation_id:
                self._active_animations.pop(animation_key, None)
            raise RuntimeError(f"No se pudo iniciar una animación QML: {exc}") from exc
        return animation_id

    def _on_animation_finished(self, animation_id):
        animation_id = int(animation_id)
        animation_key = self._animation_keys.pop(animation_id, None)
        if animation_key and self._active_animations.get(animation_key) == animation_id:
            self._active_animations.pop(animation_key, None)
        callback = self._callbacks.pop(animation_id, None)
        if callback:
            callback()


_controller: Optional[QmlAnimationController] = None
_fallback_animations = set()
_fallback_by_target_property = {}


def _animate_with_qt(
    target,
    property_name,
    start_value,
    end_value,
    duration_ms,
    easing,
    on_finished,
):
    if easing is None:
        easing = QEasingCurve.Type.OutCubic
    animation_key = (id(target), property_name)
    previous_animation = _fallback_by_target_property.get(animation_key)
    if previous_animation is not None:
        _fallback_animations.discard(previous_animation)
        previous_animation.stop()
    animation = QPropertyAnimation(target, property_name.encode("ascii"))
    animation.setDuration(max(0, int(duration_ms)))
    animation.setStartValue(start_value)
    animation.setEndValue(end_value)
    animation.setEasingCurve(easing)
    if on_finished:
        animation.finished.connect(on_finished)
    def clear_animation():
        _fallback_animations.discard(animation)
        if _fallback_by_target_property.get(animation_key) is animation:
            _fallback_by_target_property.pop(animation_key, None)

    animation.finished.connect(clear_animation)
    _fallback_animations.add(animation)
    _fallback_by_target_property[animation_key] = animation
    animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
    return animation


def animate_property(
    target: QWidget,
    property_name: str,
    start_value,
    end_value,
    duration_ms: int = 240,
    easing=None,
    on_finished: Optional[Callable[[], None]] = None,
):
    """Animate a QObject property through the shared QML controller."""
    global _controller
    if not PYQT6_AVAILABLE:
        raise RuntimeError("PyQt6 QtQml is unavailable; cannot animate this interface.")
    if _controller is None:
        try:
            _controller = QmlAnimationController()
        except (OSError, RuntimeError) as exc:
            print(f"[WARN] QML animation controller unavailable; using Qt fallback: {exc}")
            return _animate_with_qt(
                target, property_name, start_value, end_value, duration_ms, easing, on_finished
            )
    try:
        return _controller.animate(
            target,
            property_name,
            start_value,
            end_value,
            duration_ms,
            easing,
            on_finished,
        )
    except RuntimeError as exc:
        print(f"[WARN] QML property animation failed; using Qt fallback: {exc}")
        return _animate_with_qt(
            target, property_name, start_value, end_value, duration_ms, easing, on_finished
        )
