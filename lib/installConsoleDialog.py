# -*- coding: utf-8 -*-
"""
Diálogo de consola para mostrar progreso de instalación.
Consola aparte para registro/debug de compilación e instalación.
"""

import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QPushButton, QLabel
)
from leviathan_ui import CustomTitleBar


class InstallConsoleDialog(QDialog):
    """Consola de progreso para compilación e instalación"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(600, 400)
        self.init_ui()
        
    def init_ui(self):
        # Container principal
        self.container = QWidget(self)
        self.container.setObjectName("ConsoleContainer")
        
        # Detectar modo oscuro
        is_dark = self._is_dark_mode()
        
        if is_dark:
            self.container.setStyleSheet("""
                #ConsoleContainer {
                    background-color: #0d1117;
                    border: 1px solid #30363d;
                    border-radius: 8px;
                }
            """)
        else:
            self.container.setStyleSheet("""
                #ConsoleContainer {
                    background-color: #ffffff;
                    border: 1px solid #d1d5da;
                    border-radius: 8px;
                }
            """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.container)
        
        content_layout = QVBoxLayout(self.container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Title bar
        self.titlebar = CustomTitleBar(self, title="Progreso de Instalación", icon="")
        content_layout.addWidget(self.titlebar)
        
        # Área de log
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        
        if is_dark:
            self.log_area.setStyleSheet("""
                QTextEdit {
                    background-color: #161b22;
                    color: #c9d1d9;
                    border: 1px solid #30363d;
                    border-radius: 6px;
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 12px;
                    padding: 10px;
                }
            """)
        else:
            self.log_area.setStyleSheet("""
                QTextEdit {
                    background-color: #f6f8fa;
                    color: #24292e;
                    border: 1px solid #e1e4e8;
                    border-radius: 6px;
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 12px;
                    padding: 10px;
                }
            """)
        
        content_layout.addWidget(self.log_area, stretch=1)
        
        # Botón limpiar consola
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(10, 10, 10, 10)
        
        self.btn_clear = QPushButton("Limpiar Consola")
        self.btn_clear.setFixedHeight(32)
        self.btn_clear.clicked.connect(self.clear_log)
        self.btn_clear.setEnabled(True)
        
        if is_dark:
            self.btn_clear.setStyleSheet("""
                QPushButton {
                    background-color: #21262d;
                    color: #c9d1d9;
                    border: 1px solid #30363d;
                    border-radius: 6px;
                    padding: 5px 16px;
                }
                QPushButton:hover {
                    background-color: #30363d;
                }
            """)
        else:
            self.btn_clear.setStyleSheet("""
                QPushButton {
                    background-color: #f6f8fa;
                    color: #24292e;
                    border: 1px solid #e1e4e8;
                    border-radius: 6px;
                    padding: 5px 16px;
                }
                QPushButton:hover {
                    background-color: #e1e4e8;
                }
            """)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_clear)
        content_layout.addLayout(btn_layout)
        
    def _is_dark_mode(self):
        """Detectar si el sistema está en modo oscuro"""
        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return value == 0
        except:
            return False
    
    def log(self, message):
        """Agregar mensaje al log"""
        from PyQt6.QtCore import QDateTime
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.log_area.append(f"[{timestamp}] {message}")
        # Auto-scroll al final
        scrollbar = self.log_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_log(self):
        """Limpiar el área de log"""
        self.log_area.clear()
        self.log("🧹 Consola limpiada.")


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dlg = InstallConsoleDialog()
    dlg.log("Prueba de consola de instalación")
    dlg.show()
    sys.exit(app.exec())
