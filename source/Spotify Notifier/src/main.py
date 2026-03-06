import sys
import os
import json
import requests
import ctypes
import vlc
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QFrame, QSizePolicy)
from PyQt5.QtCore import QTimer, Qt, QPropertyAnimation, pyqtSignal, QPoint, QRectF, QSize
from PyQt5.QtGui import QFont, QPainter, QColor, QPixmap, QPainterPath, QPen, QBrush, QRegion
from PyQt5.QtSvg import QSvgRenderer
import icons

# --- CONFIGURACIÓN ---
NOTIF_WIDTH = 350
NOTIF_HEIGHT = 100
WORKBENCH_WIDTH = 320
WORKBENCH_HEIGHT = 180

# --- LÓGICA DE GHOSTBLUR (CORREGIDA) ---
class AccentPolicy(ctypes.Structure):
    _fields_ = [("AccentState", ctypes.c_int),
                ("AccentFlags", ctypes.c_int),
                ("GradientColor", ctypes.c_int),
                ("AnimationId", ctypes.c_int)]

class WindowCompositionAttributeData(ctypes.Structure):
    _fields_ = [("Attribute", ctypes.c_int),
                ("Data", ctypes.c_void_p),
                ("SizeOfData", ctypes.c_size_t)]

def apply_ghost_blur(widget):
    """Aplica el efecto de desenfoque nativo de Windows (Acrylic/BlurBehind)"""
    if sys.platform != "win32":
        return
    
    try:
        hwnd = int(widget.winId())
        # AccentState 3 = BlurBehind, 4 = Acrylic
        accent = AccentPolicy(3, 2, 0x01000000, 0)
        data = WindowCompositionAttributeData(19, ctypes.cast(ctypes.pointer(accent), ctypes.c_void_p), ctypes.sizeof(accent))
        ctypes.windll.user32.SetWindowCompositionAttribute(hwnd, ctypes.byref(data))
    except Exception as e:
        print(f"[DEBUG] Error aplicando GhostBlur: {e}")
    
    widget.setAttribute(Qt.WA_TranslucentBackground)
    widget.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)

# --- COMPONENTES UI ---
class SVGButton(QPushButton):
    def __init__(self, svg_content, size=30, color="#1a1a1a", hover_color="#1DB954"):
        super().__init__()
        self.setFixedSize(size, size)
        self.svg_content = svg_content
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.update_svg()
        self.setStyleSheet("border: none; background: transparent;")

    def enterEvent(self, event):
        self.current_color = self.hover_color
        self.update_svg()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.current_color = self.color
        self.update_svg()
        super().leaveEvent(event)

    def update_svg(self):
        self.renderer = QSvgRenderer(self.svg_content.replace('currentColor', self.current_color).encode())
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        self.renderer.render(painter)

class BaseGhostWidget(QWidget):
    """Base para ventanas con GhostBlur y renderizado robusto"""
    def __init__(self, width, height, radius=12, bg_color=QColor(255, 255, 255, 180)):
        super().__init__()
        self.setFixedSize(width, height)
        self.radius = radius
        self.bg_color = bg_color
        apply_ghost_blur(self)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Dibujar el fondo con transparencia controlada para evitar errores de buffer
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, self.width(), self.height()), self.radius, self.radius)
        
        # Capa de fondo sólida/traslúcida para asegurar visibilidad del contenido
        painter.fillPath(path, QBrush(self.bg_color))
        
        # Borde sutil
        painter.setPen(QPen(QColor(0, 0, 0, 30), 1))
        painter.drawPath(path)

class NotificationWidget(BaseGhostWidget):
    closed = pyqtSignal(object)
    
    def __init__(self, title, subtitle, album_art_url=None, is_release=False):
        super().__init__(NOTIF_WIDTH, NOTIF_HEIGHT)
        
        self.is_hovered = False
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(12)
        
        # Album Art
        self.art_label = QLabel()
        self.art_label.setFixedSize(60, 60)
        self.art_label.setStyleSheet("border-radius: 8px; background: rgba(0,0,0,0.1);")
        if album_art_url:
            self.load_image(album_art_url)
        layout.addWidget(self.art_label)
        
        # Info Container
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)
        
        header_layout = QHBoxLayout()
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(16, 16)
        self.logo_renderer = QSvgRenderer(icons.SPOTIFY_LOGO_SVG.encode())
        header_layout.addWidget(self.logo_label)
        
        source_text = "Spotify • " + ("Lanzamiento" if is_release else "Reproduciendo")
        source_label = QLabel(source_text)
        source_label.setStyleSheet("color: #555; font-size: 10px; font-family: 'Roboto', 'Segoe UI'; font-weight: 600;")
        header_layout.addWidget(source_label)
        header_layout.addStretch()
        
        info_layout.addLayout(header_layout)
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #111; font-weight: bold; font-size: 13px; font-family: 'Roboto', 'Segoe UI';")
        self.title_label.setWordWrap(True)
        info_layout.addWidget(self.title_label)
        
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setStyleSheet("color: #444; font-size: 11px; font-family: 'Roboto', 'Segoe UI';")
        info_layout.addWidget(self.subtitle_label)
        
        layout.addWidget(info_container)
        
        # Animación
        self.setWindowOpacity(0)
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(400)
        self.fade_anim.setStartValue(0)
        self.fade_anim.setEndValue(1)
        self.fade_anim.start()
        
        QTimer.singleShot(6000, self.start_close)

    def load_image(self, url):
        try:
            res = requests.get(url, timeout=3)
            pixmap = QPixmap()
            pixmap.loadFromData(res.content)
            scaled = pixmap.scaled(60, 60, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self.art_label.setPixmap(scaled)
            
            path = QPainterPath()
            path.addRoundedRect(0, 0, 60, 60, 8, 8)
            region = QRegion(path.toFillPolygon().toPolygon())
            self.art_label.setMask(region)
        except:
            pass

    def enterEvent(self, event):
        self.is_hovered = True
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        super().leaveEvent(event)

    def start_close(self):
        if self.is_hovered:
            QTimer.singleShot(2000, self.start_close)
            return
        
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(400)
        self.fade_anim.setStartValue(1)
        self.fade_anim.setEndValue(0)
        self.fade_anim.finished.connect(lambda: self.closed.emit(self))
        self.fade_anim.start()

class Workbench(BaseGhostWidget):
    """Workbench Nativo con estructura limpia y controles superiores"""
    def __init__(self):
        # Color crema/beige robusto para el Workbench
        super().__init__(WORKBENCH_WIDTH, WORKBENCH_HEIGHT, radius=20, bg_color=QColor(235, 225, 210, 240))
        
        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 15, 20, 15)
        
        # Header
        header = QHBoxLayout()
        self.logo_renderer = QSvgRenderer(icons.SPOTIFY_LOGO_SVG.encode())
        header.addSpacing(25) # Espacio para el logo que se dibuja en paintEvent
        
        self.source_label = QLabel("Spotify • Daily Mix 1")
        self.source_label.setStyleSheet("color: #666; font-size: 11px; font-family: 'Roboto'; font-weight: 600;")
        header.addWidget(self.source_label)
        header.addStretch()
        
        self.chevron_renderer = QSvgRenderer(icons.CHEVRON_UP.replace('currentColor', '#333').encode())
        header.addSpacing(20)
        self.main_layout.addLayout(header)
        
        # Track Info
        self.title_label = QLabel("Cargando...")
        self.title_label.setStyleSheet("color: #1a1a1a; font-weight: 900; font-size: 18px; font-family: 'Roboto'; margin-top: 5px;")
        self.main_layout.addWidget(self.title_label)
        
        self.artist_label = QLabel("Inicia reproducción")
        self.artist_label.setStyleSheet("color: #555; font-size: 14px; font-family: 'Roboto';")
        self.main_layout.addWidget(self.artist_label)
        
        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 10, 0, 10)
        
        self.btn_heart = SVGButton(icons.HEART_ICON, 24, "#444")
        self.btn_prev = SVGButton(icons.PREV_ICON, 28, "#111")
        self.btn_play = SVGButton(icons.PLAY_ICON, 42, "#111")
        self.btn_next = SVGButton(icons.NEXT_ICON, 28, "#111")
        self.btn_minus = SVGButton(icons.MINUS_ICON, 24, "#444")
        
        controls_layout.addWidget(self.btn_heart)
        controls_layout.addStretch()
        controls_layout.addWidget(self.btn_prev)
        controls_layout.addSpacing(15)
        controls_layout.addWidget(self.btn_play)
        controls_layout.addSpacing(15)
        controls_layout.addWidget(self.btn_next)
        controls_layout.addStretch()
        controls_layout.addWidget(self.btn_minus)
        self.main_layout.addLayout(controls_layout)
        
        # Progress
        progress_container = QVBoxLayout()
        progress_container.setSpacing(4)
        
        self.progress_bar = QFrame()
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setStyleSheet("background: rgba(0,0,0,0.1); border-radius: 2px;")
        
        self.progress_fill = QFrame(self.progress_bar)
        self.progress_fill.setFixedHeight(4)
        self.progress_fill.setFixedWidth(0)
        self.progress_fill.setStyleSheet("background: #1DB954; border-radius: 2px;")
        
        progress_container.addWidget(self.progress_bar)
        
        time_layout = QHBoxLayout()
        self.time_now = QLabel("00:00")
        self.time_total = QLabel("00:00")
        for lbl in [self.time_now, self.time_total]:
            lbl.setStyleSheet("color: #777; font-size: 10px; font-family: 'Roboto'; font-weight: bold;")
        time_layout.addWidget(self.time_now)
        time_layout.addStretch()
        time_layout.addWidget(self.time_total)
        progress_container.addLayout(time_layout)
        
        self.main_layout.addLayout(progress_container)
        
        # Posicionamiento inicial
        self.update_position()

    def update_position(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(30, screen.height() - self.height() - 30)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        # Dibujar logos sobre el fondo ya renderizado por la clase base
        self.logo_renderer.render(painter, QRectF(20.0, 15.0, 18.0, 18.0))
        self.chevron_renderer.render(painter, QRectF(float(self.width() - 35), 15.0, 16.0, 16.0))

# --- INTEGRACIÓN VLC ---
class MediaController:
    def __init__(self, workbench):
        self.workbench = workbench
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(500)
        
        self.workbench.btn_play.clicked.connect(self.toggle_play)

    def play_track(self, url, title, artist):
        media = self.instance.media_new(url)
        self.player.set_media(media)
        self.player.play()
        self.workbench.title_label.setText(title)
        self.workbench.artist_label.setText(artist)
        self.workbench.btn_play.svg_content = icons.PAUSE_ICON
        self.workbench.btn_play.update_svg()

    def toggle_play(self):
        if self.player.is_playing():
            self.player.pause()
            self.workbench.btn_play.svg_content = icons.PLAY_ICON
        else:
            self.player.play()
            self.workbench.btn_play.svg_content = icons.PAUSE_ICON
        self.workbench.btn_play.update_svg()

    def update_ui(self):
        if self.player.is_playing() or self.player.get_state() == vlc.State.Paused:
            curr = self.player.get_time() // 1000
            total = self.player.get_length() // 1000
            
            if total > 0:
                progress = int((curr / total) * (self.workbench.progress_bar.width()))
                self.workbench.progress_fill.setFixedWidth(progress)
                
                self.workbench.time_now.setText(f"{curr//60:02d}:{curr%60:02d}")
                self.workbench.time_total.setText(f"{total//60:02d}:{total%60:02d}")

# --- MANAGER PRINCIPAL ---
class SpotifyNotifierManager:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.notifications = []
        self.workbench = Workbench()
        self.media = MediaController(self.workbench)
        
        self.workbench.show()
        
        self.pos_timer = QTimer()
        self.pos_timer.timeout.connect(self.update_positions)
        self.pos_timer.start(16)
        
        # Demo Data
        QTimer.singleShot(2000, lambda: self.notify("Bodys", "Car Seat Headrest", is_release=True))

    def notify(self, title, subtitle, art=None, is_release=False):
        notif = NotificationWidget(title, subtitle, art, is_release)
        notif.closed.connect(self.remove_notification)
        self.notifications.insert(0, notif)
        notif.show()

    def remove_notification(self, notif):
        if notif in self.notifications:
            self.notifications.remove(notif)
            notif.deleteLater()

    def update_positions(self):
        screen = QApplication.primaryScreen().availableGeometry()
        base_x = screen.width() - NOTIF_WIDTH - 20
        current_y = screen.height() - 60
        
        for notif in self.notifications:
            target_y = current_y - NOTIF_HEIGHT
            pos = notif.pos()
            new_y = pos.y() + (target_y - pos.y()) * 0.15
            notif.move(base_x, int(new_y))
            current_y = target_y - 10

    def run(self):
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    manager = SpotifyNotifierManager()
    manager.run()
