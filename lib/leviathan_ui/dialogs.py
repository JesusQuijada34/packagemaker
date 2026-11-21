from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QEvent
from PyQt6.QtGui import QFont, QPixmap

from .title_bar import CustomTitleBar, get_accent_color, is_icon_file

from .wipeWindow import WipeWindow
from .lightsOff import LightsOff

class LeviathanDialog(QWidget):
    """
    💠 LeviathanDialog: Reemplazo moderno para QMessageBox.
    Integra Blur Overlay, TitleBar personalizada y efecto LightsOff.
    """
    
    TYPES = {
        "info": {"icon": "ℹ️", "color": "auto"},
        "success": {"icon": "✅", "color": "#28a745"},
        "warning": {"icon": "⚠️", "color": "#ffc107"},
        "error": {"icon": "❌", "color": "#dc3545"}
    }

    def __init__(self, parent, title, message, mode="info", buttons=None):
        super().__init__(None) # Dialog flotante
        self._parent_win = parent
        self._mode_cfg = self.TYPES.get(mode, self.TYPES["info"])
        self._accent = get_accent_color() if self._mode_cfg["color"] == "auto" else self._mode_cfg["color"]
        self._buttons = buttons or ["ENTENDIDO"]
        self._result = None
        self._callback = None
        
        self.setWindowTitle(title)
        self.setFixedSize(450, 240)
        self.setWindowModality(Qt.WindowModality.WindowModal if parent else Qt.WindowModality.NonModal)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        
        # 1. Overlay Blur (Cubre la ventana principal)
        if self._parent_win:
            self.overlay = QWidget(self._parent_win)
            self.overlay.setGeometry(self._parent_win.rect())
            # Nos aseguramos que el overlay redimensione con el padre
            self._parent_win.installEventFilter(self) 
            WipeWindow.create().set_mode("ghostBlur").set_blur(40).apply(self.overlay)
            self.overlay.show()
        else:
            self.overlay = None

        # 2. Configuración de Ventana (WipeWindow)
        WipeWindow.create()\
            .set_mode("polished")\
            .set_background("#181818")\
            .set_radius(20)\
            .apply(self)
        
        # 3. Layout Principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Barra de Título
        self.title_bar = CustomTitleBar(self, title=title, icon=self._mode_cfg["icon"], hide_max=True)
        self.main_layout.addWidget(self.title_bar)

        
        # Contenido
        content_frame = QFrame()
        content_lay = QVBoxLayout(content_frame)
        content_lay.setContentsMargins(30, 20, 30, 25)
        content_lay.setSpacing(20)
        
        msg_lay = QHBoxLayout()
        
        # Soporte para iconos reales o emojis
        icon_val = self._mode_cfg["icon"]
        icon_lbl = QLabel()
        if is_icon_file(icon_val):

            pixmap = QPixmap(icon_val)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                icon_lbl.setPixmap(pixmap)
            else:
                icon_lbl.setText(icon_val)
                icon_lbl.setFont(QFont("Segoe UI Emoji", 32))
        else:
            icon_lbl.setText(icon_val)
            icon_lbl.setFont(QFont("Segoe UI Emoji", 32))

        
        icon_lbl.setStyleSheet("background: transparent;")
        
        self.msg_lbl = QLabel(message)
        self.msg_lbl.setWordWrap(True)
        self.msg_lbl.setStyleSheet("color: #eeeeee; font-size: 14px; font-family: 'Segoe UI'; background: transparent;")
        
        msg_lay.addWidget(icon_lbl)
        msg_lay.addSpacing(15)
        msg_lay.addWidget(self.msg_lbl, 1)
        content_lay.addLayout(msg_lay)
        
        # Botones Dinámicos
        btn_container = QHBoxLayout()
        btn_container.addStretch()
        
        for btn_text in self._buttons:
            btn = QPushButton(btn_text)
            btn.setFixedSize(110, 36)
            
            # Estilo basado en acento
            is_main = btn_text == self._buttons[-1]
            bg = self._accent if is_main else "transparent"
            fg = "black" if is_main else "white"
            border = f"2px solid {self._accent}"
            
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg};
                    color: {fg};
                    border: {border};
                    border-radius: 8px;
                    font-weight: bold;
                    font-family: 'Segoe UI';
                }}
                QPushButton:hover {{
                    background-color: white;
                    color: black;
                    border: 2px solid white;
                }}
            """)
            
            # Efecto Glow
            LightsOff.light_up(btn, color=self._accent if not is_main else "#ffffff", intensity=15)
            
            btn.clicked.connect(lambda checked, t=btn_text: self._on_btn_clicked(t))
            btn_container.addWidget(btn)
        
        content_lay.addLayout(btn_container)
        self.main_layout.addWidget(content_frame)
        
        # Centrar respecto al padre
        self._update_position()
            
        # 5. Animaciones combinadas (Opacidad + Escala/Posición)
        self.setWindowOpacity(0)
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(350)
        self.fade_anim.setStartValue(0)
        self.fade_anim.setEndValue(1)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _update_position(self):
        if self._parent_win:
            center = self._parent_win.geometry().center()
            self.move(center.x() - self.width() // 2, center.y() - self.height() // 2)

    def eventFilter(self, obj, event):
        # Sincronizar overlay con el padre si este cambia de tamaño
        try:
            if obj == self._parent_win and event.type() == QEvent.Type.Resize:
                if self.overlay: 
                    self.overlay.setGeometry(self._parent_win.rect())
        except: pass
        return super().eventFilter(obj, event)

    def _on_btn_clicked(self, text):
        self._result = text
        self.close()
        # El callback se ejecuta DESPUÉS del close para que la UI esté limpia
        if self._callback: self._callback(text)

    def showEvent(self, event):
        self.fade_anim.start()
        super().showEvent(event)

    def closeEvent(self, event):
        # MUY IMPORTANTE: Remover el filtro antes de cerrar para evitar punteros rotos
        if self._parent_win:
            self._parent_win.removeEventFilter(self)
        if self.overlay:
            self.overlay.close()
            self.overlay.deleteLater()
        event.accept()
        self.deleteLater() # Asegura que Python libere el objeto

    @staticmethod
    def launch(parent, title, message, mode="info", buttons=None, callback=None):
        dlg = LeviathanDialog(parent, title, message, mode, buttons)
        dlg._callback = callback
        dlg.show()
        return dlg
