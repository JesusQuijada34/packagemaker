import os
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon

class SidebarItem(QPushButton):
    """Boton de navegación lateral estilo Start11"""
    def __init__(self, text, icon_path, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(50)
        self.setIconSize(QSize(24, 24))
        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
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
                background-color: rgba(255, 255, 255, 0.05);
                color: #ffffff;
            }
            QPushButton:checked {
                background-color: rgba(255, 255, 255, 0.08);
                color: #ffffff;
                border-left: 3px solid #ff5722;
            }
            QPushButton:focus {
                border: none;
                outline: none;
            }
        """)
