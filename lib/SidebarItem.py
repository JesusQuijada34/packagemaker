import os
try:
    from PyQt6.QtWidgets import QPushButton
    from PyQt6.QtCore import QSize, Qt
    from PyQt6.QtGui import QIcon
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    class QPushButton:
        def __init__(self, *args, **kwargs): pass
        def setFixedHeight(self, *args): pass
        def setIconSize(self, *args): pass
        def setIcon(self, *args): pass
    class QIcon:
        def __init__(self, *args, **kwargs): pass

from lib.design_tokens import (
    ACCENT,
    CONTROL_RADIUS,
    FONT_STACK,
    SIDEBAR_ICON_INSET,
    SIDEBAR_ITEM_HEIGHT,
    TEXT,
    TEXT_MUTED,
)
from lib.hover_animation import enable_hover_fade


class SidebarItem(QPushButton):
    """Botón de navegación lateral con modo compacto Fluent."""
    def __init__(self, text, icon=None, parent=None):
        super().__init__(text, parent)
        self._label_text = text
        self._compact = False
        self.setFixedHeight(SIDEBAR_ITEM_HEIGHT)
        self.setIconSize(QSize(24, 24))
        if isinstance(icon, QIcon):
            self.setIcon(icon)
        elif icon and os.path.exists(str(icon)):
            self.setIcon(QIcon(str(icon)))
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style()
        # El ítem seleccionado ya tiene su propio color; no se anima su fondo.
        self._hover_fade = enable_hover_fade(
            self, "rgba(255, 255, 255, 0.07)", only_when=lambda: not self.isChecked()
        )

    def set_label_text(self, text):
        self._label_text = text
        self.setText("" if self._compact else text)
        self.setToolTip(text if self._compact else "")

    def set_compact(self, compact):
        self._compact = bool(compact)
        self.set_label_text(self._label_text)
        self._apply_style()
        fade = getattr(self, "_hover_fade", None)
        if fade is not None:
            fade.refresh()

    def _apply_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_MUTED};
                text-align: left;
                padding: 0 10px 0 {SIDEBAR_ICON_INSET}px;
                border: none;
                border-left: 3px solid transparent;
                border-radius: {CONTROL_RADIUS}px;
                font-family: {FONT_STACK};
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.07);
                color: {TEXT};
            }}
            QPushButton:checked {{
                background-color: rgba(255, 255, 255, 0.09);
                color: {TEXT};
                border-left: 3px solid {ACCENT};
            }}
            QPushButton:checked:hover {{
                background-color: rgba(255, 255, 255, 0.12);
            }}
        """)
        if self._compact:
            self.setStyleSheet(self.styleSheet() + f"""
                QPushButton {{
                    text-align: center;
                    padding: 0;
                    border-left-color: transparent;
                    border-radius: {CONTROL_RADIUS}px;
                }}
                QPushButton:checked {{
                    border-left-color: {ACCENT};
                }}
            """)
