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

class SidebarItem(QPushButton):
    """Botón de navegación lateral con modo compacto Fluent."""
    def __init__(self, text, icon=None, parent=None):
        super().__init__(text, parent)
        self._label_text = text
        self._compact = False
        self.setFixedHeight(50)
        self.setIconSize(QSize(24, 24))
        if isinstance(icon, QIcon):
            self.setIcon(icon)
        elif icon and os.path.exists(str(icon)):
            self.setIcon(QIcon(str(icon)))
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style()

    def set_label_text(self, text):
        self._label_text = text
        self.setText("" if self._compact else text)
        self.setToolTip(text if self._compact else "")

    def set_compact(self, compact):
        self._compact = bool(compact)
        self.set_label_text(self._label_text)
        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #c4cad4;
                text-align: left;
                padding: 0 10px 0 16px;
                border: none;
                border-left: 3px solid transparent;
                border-radius: 9px;
                font-family: 'Segoe UI Variable Display', 'Segoe UI', sans-serif;
                font-size: 15px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.07);
                color: #ffffff;
            }
            QPushButton:checked {
                background-color: rgba(255, 255, 255, 0.09);
                color: #ffffff;
                border-left: 3px solid #ff7043;
            }
            QPushButton:checked:hover {
                background-color: rgba(255, 255, 255, 0.12);
            }
        """)
        if self._compact:
            self.setStyleSheet(self.styleSheet() + """
                QPushButton {
                    text-align: center;
                    padding: 0;
                    border-left-color: transparent;
                    border-radius: 10px;
                }
                QPushButton:checked {
                    border-left-color: #ff7043;
                }
            """)
