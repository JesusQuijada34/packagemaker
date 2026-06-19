#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
System tray icon functionality for the updater.
"""
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QColor, QAction
from PyQt6.QtCore import Qt

# --- GLOBAL VARIABLES FOR SYSTEM TRAY ---
_tray_icon = None
_updater_window = None

class SystemTrayIcon(QSystemTrayIcon):
    """System tray icon for the updater with hide/show functionality."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(self._create_icon())
        self.setToolTip("PackageMaker Updater")
        
        # Create context menu
        menu = QMenu()
        
        show_action = QAction("Mostrar", self)
        show_action.triggered.connect(self.show_window)
        menu.addAction(show_action)
        
        hide_action = QAction("Ocultar", self)
        hide_action.triggered.connect(self.hide_window)
        menu.addAction(hide_action)
        
        menu.addSeparator()
        
        quit_action = QAction("Salir", self)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)
        
        self.setContextMenu(menu)
        
        # Activate on double click
        self.activated.connect(self.on_activated)
    
    def _create_icon(self):
        """Create a simple icon for the system tray."""
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor("#2486ff"))
        return QIcon(pixmap)
    
    def on_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window()
    
    def show_window(self):
        """Show the updater window."""
        global _updater_window
        if _updater_window:
            _updater_window.show()
            _updater_window.raise_()
            _updater_window.activateWindow()
    
    def hide_window(self):
        """Hide the updater window (minimize to tray)."""
        global _updater_window
        if _updater_window:
            _updater_window.hide()
    
    def quit_app(self):
        """Quit the application."""
        global _updater_window
        if _updater_window:
            _updater_window.close()
        from PyQt6.QtWidgets import QApplication
        QApplication.quit()

def get_tray_icon():
    """Get the global tray icon instance."""
    global _tray_icon
    return _tray_icon

def set_tray_icon(icon):
    """Set the global tray icon instance."""
    global _tray_icon
    _tray_icon = icon

def get_updater_window():
    """Get the global updater window instance."""
    global _updater_window
    return _updater_window

def set_updater_window(window):
    """Set the global updater window instance."""
    global _updater_window
    _updater_window = window
