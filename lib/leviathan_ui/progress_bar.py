from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRect, pyqtProperty
from PyQt6.QtGui import QColor, QPainter, QBrush, QLinearGradient

from .title_bar import get_accent_color

class LeviathanProgressBar(QWidget):
    """
    📊 LeviathanProgressBar: Barra de progreso moderna con soporte para modo Marquee.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(8)
        self._value = 0
        self._min = 0
        self._max = 100
        self._is_marquee = False
        self._marquee_pos = -100
        self._accent = get_accent_color()
        
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_marquee)
        
    @pyqtProperty(int)
    def value(self):
        return self._value
        
    @value.setter
    def value(self, val):
        self._value = max(self._min, min(self._max, val))
        self.update()
        
    def setRange(self, min_val, max_val):
        self._min = min_val
        self._max = max_val
        self.update()
        
    def setMarquee(self, enabled):
        self._is_marquee = enabled
        if enabled:
            self._timer.start(20)
        else:
            self._timer.stop()
        self.update()
        
    def _update_marquee(self):
        self._marquee_pos += 5
        if self._marquee_pos > self.width():
            self._marquee_pos = -100
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fondo
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(40, 40, 40)))
        painter.drawRoundedRect(self.rect(), 4, 4)
        
        if self._is_marquee:
            # Dibujar barra marquee
            gradient = QLinearGradient(self._marquee_pos, 0, self._marquee_pos + 100, 0)
            gradient.setColorAt(0, QColor(self._accent).lighter(150))
            gradient.setColorAt(0.5, QColor(self._accent))
            gradient.setColorAt(1, QColor(self._accent).lighter(150))
            
            painter.setBrush(QBrush(gradient))
            painter.drawRoundedRect(QRect(self._marquee_pos, 0, 100, self.height()), 4, 4)
        else:
            # Dibujar barra normal
            if self._max > self._min:
                width = int((self._value - self._min) / (self._max - self._min) * self.width())
                if width > 0:
                    painter.setBrush(QBrush(QColor(self._accent)))
                    painter.drawRoundedRect(QRect(0, 0, width, self.height()), 4, 4)
        painter.end()
