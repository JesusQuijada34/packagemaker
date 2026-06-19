#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Window classes for the updater GUI.
"""
import os
import sys
import subprocess
import time
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, 
    QProgressBar, QPushButton, QTextEdit, QHBoxLayout, QCheckBox
)
from PyQt6.QtGui import QFont, QIcon, QPixmap, QColor, QGuiApplication
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from .workers import InstallerWorker, IFLAPPInstallerWorker, EXEInstallerWorker
from .system_tray import get_tray_icon, set_tray_icon, get_updater_window, set_updater_window
from .core import log

# --- LEVIATHAN UI CHECK ---
try:
    from leviathan_ui import LeviathanDialog, WipeWindow, LeviathanProgressBar, CustomTitleBar, InmersiveSplash
    HAS_LEVIATHAN = True
except ImportError:
    HAS_LEVIATHAN = False


class ModernUpdaterWindow(QMainWindow):
    def __init__(self, app_data, url):
        super().__init__()
        self.app_data = app_data
        self.url = url
        self.setWindowFlags(Qt.WindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint))
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(480, 320)
        if HAS_LEVIATHAN:
            WipeWindow.create().set_mode("ghostBlur").apply(self)
        self.init_ui()
        self.center()
        
        # Setup system tray
        from .system_tray import SystemTrayIcon
        set_updater_window(self)
        if not get_tray_icon():
            tray = SystemTrayIcon()
            set_tray_icon(tray)
            tray.show()
        
        QTimer.singleShot(500, self.start_install)

    def center(self):
        screen = QGuiApplication.primaryScreen()
        if screen:
            self.move(screen.availableGeometry().center() - self.rect().center())

    def init_ui(self):
        central = QWidget()
        central.setObjectName("Central")
        central.setStyleSheet("QWidget#Central { background: rgba(18, 24, 34, 0.85); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; }")
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if HAS_LEVIATHAN:
            self.title_bar = CustomTitleBar(self, title="System Updater", is_main=True)
            self.title_bar.set_color(QColor(0,0,0,0))
            layout.addWidget(self.title_bar)

        content = QWidget()
        c_lay = QVBoxLayout(content)
        c_lay.setContentsMargins(30, 10, 30, 30)
        c_lay.setSpacing(15)
        
        self.icon_lbl = QLabel("🔄")
        self.icon_lbl.setStyleSheet("font-size: 48px; color: #2486ff;")
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_lay.addWidget(self.icon_lbl)
        
        self.lbl_main = QLabel(f"Actualizando {self.app_data['app']}")
        self.lbl_main.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_main.setStyleSheet("font-family: 'Segoe UI'; font-weight: 700; font-size: 18px; color: white;")
        c_lay.addWidget(self.lbl_main)
        
        self.lbl_status = QLabel("Preparando...")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setStyleSheet("color: #aaa; font-size: 13px;")
        c_lay.addWidget(self.lbl_status)
        
        if HAS_LEVIATHAN:
            self.pbar = LeviathanProgressBar(self)
        else:
            self.pbar = QProgressBar()
            self.pbar.setStyleSheet("QProgressBar { background: #333; border: none; height: 6px; } QProgressBar::chunk { background: #2486ff; }")
            self.pbar.setTextVisible(False)
        c_lay.addWidget(self.pbar)
        
        # Add hide button
        self.btn_hide = QPushButton("Ocultar")
        self.btn_hide.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.1);
                color: white;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.2);
            }
        """)
        self.btn_hide.clicked.connect(self.hide_to_tray)
        c_lay.addWidget(self.btn_hide)
        
        layout.addWidget(content)

    def start_install(self):
        self.thread = QThread()
        self.worker = InstallerWorker(self.url, self.app_data)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.pbar.setValue)
        self.worker.status.connect(self.lbl_status.setText)
        self.worker.finished.connect(self.on_fin)
        self.thread.start()

    def on_fin(self, ok, msg):
        self.thread.quit()
        if ok:
            self.lbl_status.setText("¡Actualización completada!")
            # Relaunch
            exe = f"{self.app_data['app']}.exe"
            if os.path.exists(exe): subprocess.Popen(exe)
            QTimer.singleShot(1500, self.close)
        else:
            self.lbl_status.setText(f"Error: {msg}")
            self.lbl_status.setStyleSheet("color: #ff5252;")
    
    def hide_to_tray(self):
        """Hide window to system tray."""
        from PyQt6.QtWidgets import QSystemTrayIcon
        tray = get_tray_icon()
        self.hide()
        if tray:
            tray.showMessage(
                "PackageMaker Updater",
                "El actualizador sigue ejecutándose en segundo plano. Haga doble clic en el icono de la bandeja para mostrarlo.",
                QSystemTrayIcon.MessageIcon.Information,
                3000
            )


class IFLAPPInstallerWindow(QMainWindow):
    """Ventana para instalar archivos .iflapp en un contenedor."""
    
    finished = pyqtSignal(bool, str)
    
    def __init__(self, iflapp_path, target_dir=None, parent=None):
        super().__init__(parent)
        self.iflapp_path = iflapp_path
        self.target_dir = target_dir or os.path.join(os.getcwd(), "installed_app")
        self.setWindowFlags(Qt.WindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint))
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(480, 280)
        if HAS_LEVIATHAN:
            WipeWindow.create().set_mode("ghostBlur").apply(self)
        self.init_ui()
        self.center()
        QTimer.singleShot(500, self.start_installation)
    
    def center(self):
        screen = QGuiApplication.primaryScreen()
        if screen:
            self.move(screen.availableGeometry().center() - self.rect().center())
    
    def init_ui(self):
        central = QWidget()
        central.setObjectName("Central")
        central.setStyleSheet("QWidget#Central { background: rgba(18, 24, 34, 0.85); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; }")
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if HAS_LEVIATHAN:
            self.title_bar = CustomTitleBar(self, title="Instalador IFLAPP", is_main=True)
            self.title_bar.set_color(QColor(0,0,0,0))
            layout.addWidget(self.title_bar)
        
        content = QWidget()
        c_lay = QVBoxLayout(content)
        c_lay.setContentsMargins(30, 10, 30, 30)
        c_lay.setSpacing(15)
        
        self.icon_lbl = QLabel("📦")
        self.icon_lbl.setStyleSheet("font-size: 48px;")
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_lay.addWidget(self.icon_lbl)
        
        self.lbl_main = QLabel("Instalando paquete...")
        self.lbl_main.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_main.setStyleSheet("font-family: 'Segoe UI'; font-weight: 700; font-size: 18px; color: white;")
        c_lay.addWidget(self.lbl_main)
        
        self.lbl_status = QLabel(f"Destino: {self.target_dir}")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setStyleSheet("color: #aaa; font-size: 13px;")
        c_lay.addWidget(self.lbl_status)
        
        if HAS_LEVIATHAN:
            self.pbar = LeviathanProgressBar(self)
        else:
            self.pbar = QProgressBar()
            self.pbar.setStyleSheet("QProgressBar { background: #333; border: none; height: 6px; } QProgressBar::chunk { background: #2486ff; }")
            self.pbar.setTextVisible(False)
        self.pbar.setValue(0)
        c_lay.addWidget(self.pbar)
        
        layout.addWidget(content)
    
    def start_installation(self):
        """Inicia la instalación del archivo .iflapp."""
        self.thread = QThread()
        self.worker = IFLAPPInstallerWorker(self.iflapp_path, self.target_dir)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.pbar.setValue)
        self.worker.status.connect(self.lbl_status.setText)
        self.worker.finished.connect(self.on_finished)
        self.thread.start()
    
    def on_finished(self, ok, msg):
        self.thread.quit()
        if ok:
            self.lbl_status.setText("¡Instalación completada!")
            self.lbl_main.setText("Paquete instalado")
            self.icon_lbl.setText("✅")
            QTimer.singleShot(2000, self.close)
        else:
            self.lbl_status.setText(f"Error: {msg}")
            self.lbl_status.setStyleSheet("color: #ff5252;")
        self.finished.emit(ok, msg)


class LicenseTermsDialog(QMainWindow):
    """Diálogo de aceptación de términos de licencia."""
    
    accepted = pyqtSignal()
    rejected = pyqtSignal()
    
    def __init__(self, app_name="Aplicación", license_text=None, parent=None):
        super().__init__(parent)
        self.app_name = app_name
        self.setWindowFlags(Qt.WindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint))
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(600, 450)
        if HAS_LEVIATHAN:
            WipeWindow.create().set_mode("ghostBlur").apply(self)
        self.init_ui(license_text)
        self.center()
    
    def center(self):
        screen = QGuiApplication.primaryScreen()
        if screen:
            self.move(screen.availableGeometry().center() - self.rect().center())
    
    def init_ui(self, license_text):
        central = QWidget()
        central.setObjectName("Central")
        central.setStyleSheet("""
            QWidget#Central { 
                background: rgba(18, 24, 34, 0.95); 
                border: 1px solid rgba(255,255,255,0.1); 
                border-radius: 16px; 
            }
            QPushButton {
                background: #2486ff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover { background: #1a6fd4; }
            QPushButton:disabled { background: #555; color: #888; }
            QPushButton#rejectBtn {
                background: transparent;
                border: 1px solid rgba(255,255,255,0.2);
                color: #aaa;
            }
            QPushButton#rejectBtn:hover { 
                background: rgba(255,255,255,0.1); 
                color: white;
            }
            QTextEdit {
                background: rgba(0,0,0,0.3);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                color: #ddd;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                padding: 10px;
            }
            QCheckBox {
                color: #ddd;
                font-size: 13px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #2486ff;
            }
            QCheckBox::indicator:checked {
                background: #2486ff;
            }
        """)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if HAS_LEVIATHAN:
            self.title_bar = CustomTitleBar(self, title="Términos de Licencia", is_main=True)
            self.title_bar.set_color(QColor(0,0,0,0))
            layout.addWidget(self.title_bar)
        
        content = QWidget()
        c_lay = QVBoxLayout(content)
        c_lay.setContentsMargins(30, 20, 30, 30)
        c_lay.setSpacing(15)
        
        # Título
        lbl_title = QLabel(f"📜 Términos de Licencia - {self.app_name}")
        lbl_title.setStyleSheet("font-family: 'Segoe UI'; font-weight: 700; font-size: 16px; color: white;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_lay.addWidget(lbl_title)
        
        # Texto de licencia
        default_license = f"""Licencia de Uso de {self.app_name}

Al instalar o utilizar este software, usted acepta los siguientes términos:

1. CONCESIÓN DE LICENCIA
   Se otorga una licencia no exclusiva para usar este software.

2. RESTRICCIONES
   - No distribuir sin autorización
   - No realizar ingeniería inversa
   - No eliminar avisos de copyright

3. ACTUALIZACIONES
   Este software puede conectarse a servidores para verificar actualizaciones.

4. EXENCIÓN DE RESPONSABILIDAD
   El software se proporciona "tal cual" sin garantías.

5. PRIVACIDAD
   No se recolecta información personal sin consentimiento.

Para continuar con la instalación, debe aceptar estos términos."""
        
        self.txt_license = QTextEdit()
        self.txt_license.setReadOnly(True)
        self.txt_license.setText(license_text or default_license)
        self.txt_license.setMinimumHeight(200)
        c_lay.addWidget(self.txt_license)
        
        # Checkbox de aceptación
        self.chk_accept = QCheckBox("He leído y acepto los términos de licencia")
        self.chk_accept.stateChanged.connect(self.on_accept_changed)
        c_lay.addWidget(self.chk_accept)
        
        # Botones
        btn_layout = QHBoxLayout()
        
        self.btn_reject = QPushButton("Rechazar y Salir")
        self.btn_reject.setObjectName("rejectBtn")
        self.btn_reject.clicked.connect(self.on_reject)
        btn_layout.addWidget(self.btn_reject)
        
        btn_layout.addStretch()
        
        self.btn_accept = QPushButton("Aceptar y Continuar ✓")
        self.btn_accept.setEnabled(False)
        self.btn_accept.clicked.connect(self.on_accept)
        btn_layout.addWidget(self.btn_accept)
        
        c_lay.addLayout(btn_layout)
        layout.addWidget(content)
    
    def on_accept_changed(self, state):
        self.btn_accept.setEnabled(state == Qt.CheckState.Checked.value)
    
    def on_accept(self):
        self.accepted.emit()
        self.close()
    
    def on_reject(self):
        self.rejected.emit()
        self.close()


class EXEInstallerWindow(QMainWindow):
    """Ventana para instalar ejecutable setup descargado."""
    
    finished = pyqtSignal(bool, str)
    
    def __init__(self, url, filename, parent=None, cache_in_memory=True):
        super().__init__(parent)
        self.url = url
        self.filename = filename
        self.cache_in_memory = cache_in_memory
        self.setWindowFlags(Qt.WindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint))
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(480, 280)
        if HAS_LEVIATHAN:
            WipeWindow.create().set_mode("ghostBlur").apply(self)
        self.init_ui()
        self.center()
        QTimer.singleShot(500, self.start_installation)
    
    def center(self):
        screen = QGuiApplication.primaryScreen()
        if screen:
            self.move(screen.availableGeometry().center() - self.rect().center())
    
    def init_ui(self):
        central = QWidget()
        central.setObjectName("Central")
        central.setStyleSheet("QWidget#Central { background: rgba(18, 24, 34, 0.85); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; }")
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if HAS_LEVIATHAN:
            self.title_bar = CustomTitleBar(self, title="Instalador Setup", is_main=True)
            self.title_bar.set_color(QColor(0,0,0,0))
            layout.addWidget(self.title_bar)
        
        content = QWidget()
        c_lay = QVBoxLayout(content)
        c_lay.setContentsMargins(30, 10, 30, 30)
        c_lay.setSpacing(15)
        
        self.icon_lbl = QLabel("📥")
        self.icon_lbl.setStyleSheet("font-size: 48px;")
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_lay.addWidget(self.icon_lbl)
        
        self.lbl_main = QLabel("Instalando desde setup...")
        self.lbl_main.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_main.setStyleSheet("font-family: 'Segoe UI'; font-weight: 700; font-size: 18px; color: white;")
        c_lay.addWidget(self.lbl_main)
        
        self.lbl_status = QLabel(f"Archivo: {self.filename}")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setStyleSheet("color: #aaa; font-size: 13px;")
        c_lay.addWidget(self.lbl_status)
        
        if HAS_LEVIATHAN:
            self.pbar = LeviathanProgressBar(self)
        else:
            self.pbar = QProgressBar()
            self.pbar.setStyleSheet("QProgressBar { background: #333; border: none; height: 6px; } QProgressBar::chunk { background: #2486ff; }")
            self.pbar.setTextVisible(False)
        self.pbar.setValue(0)
        c_lay.addWidget(self.pbar)
        
        layout.addWidget(content)
    
    def start_installation(self):
        self.thread = QThread()
        self.worker = EXEInstallerWorker(self.url, self.filename, self.cache_in_memory)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.pbar.setValue)
        self.worker.status.connect(self.lbl_status.setText)
        self.worker.finished.connect(self.on_finished)
        self.thread.start()
    
    def on_finished(self, ok, msg):
        self.thread.quit()
        if ok:
            self.lbl_status.setText("¡Instalación completada!")
            self.lbl_main.setText("Setup instalado")
            self.icon_lbl.setText("✅")
            QTimer.singleShot(2000, self.close)
        else:
            self.lbl_status.setText(f"Error: {msg}")
            self.lbl_status.setStyleSheet("color: #ff5252;")
        self.finished.emit(ok, msg)
