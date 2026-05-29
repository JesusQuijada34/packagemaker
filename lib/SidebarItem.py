import os
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon

class SidebarItem(QPushButton):
    """Boton de navegación lateral estilo Start11"""
    def __init__(self, text, icon=None, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(50)
        self.setIconSize(QSize(24, 24))
        if isinstance(icon, QIcon):
            self.setIcon(icon)
        elif icon and os.path.exists(str(icon)):
            self.setIcon(QIcon(str(icon)))
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #b0b0b0;
                text-align: left;
                padding-left: 17px;
                border: none;
                border-left: 3px solid transparent;
                outline: none;
                border-radius: 8px;
                font-family: 'Segoe UI Variable Display', 'Segoe UI', sans-serif;
                font-size: 15px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: transparent;
                color: #ffffff;
            }
            QPushButton:checked {
                background-color: transparent;
                color: #ffffff;
                border-left: 3px solid #ff5722;
            }
            QPushButton:focus {
                border: none;
                outline: none;
            }
        """)
