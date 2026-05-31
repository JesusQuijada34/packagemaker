# -*- coding: utf-8 -*-
"""Animaciones de cierre estilo UWP (bounce down)."""

try:
    from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QPoint
    from PyQt6.QtWidgets import QWidget
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    class QWidget: pass


def play_bounce_down_close(widget: QWidget, on_finished=None, drop_px: int = 72, duration_ms: int = 420):
    """Anima cierre: desliza hacia abajo con rebote y desvanece."""
    if getattr(widget, "_uwp_closing", False):
        return False
    widget._uwp_closing = True

    group = QParallelAnimationGroup(widget)

    anim_pos = QPropertyAnimation(widget, b"pos")
    anim_pos.setDuration(duration_ms)
    anim_pos.setStartValue(widget.pos())
    anim_pos.setEndValue(QPoint(widget.x(), widget.y() + drop_px))
    anim_pos.setEasingCurve(QEasingCurve.Type.OutBounce)

    anim_fade = QPropertyAnimation(widget, b"windowOpacity")
    anim_fade.setDuration(max(280, duration_ms - 80))
    anim_fade.setStartValue(widget.windowOpacity())
    anim_fade.setEndValue(0.0)
    anim_fade.setEasingCurve(QEasingCurve.Type.OutCubic)

    group.addAnimation(anim_pos)
    group.addAnimation(anim_fade)

    def _done():
        widget._uwp_closing = False
        if on_finished:
            on_finished()

    group.finished.connect(_done)
    group.start(QParallelAnimationGroup.DeletionPolicy.DeleteWhenStopped)
    return True
