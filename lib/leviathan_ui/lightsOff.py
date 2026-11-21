from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QObject, QEvent
from PyQt6.QtGui import QColor

class LightsOff(QObject):
    """
    💡 LightsOff: Efecto de iluminación interactiva (Glow) para controles.
    Utiliza un EventFilter para interceptar el mouse sin romper el objeto original.
    """
    def __init__(self, target):
        super().__init__(target)
        self.target = target
        
        # Efecto de brillo
        self.glow = QGraphicsDropShadowEffect(target)
        self.glow.setBlurRadius(0)
        self.glow.setOffset(0, 0)
        self.target.setGraphicsEffect(self.glow)
        
        # Animación de intensidad
        self.anim = QPropertyAnimation(self.glow, b"blurRadius")
        self.anim.setDuration(400)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._intensity = 25
        
        # Instalamos el filtro de eventos
        self.target.installEventFilter(self)

    def set_glow(self, color="#0078d4", intensity=25):
        self.glow.setColor(QColor(color))
        self._intensity = intensity
        return self

    def eventFilter(self, obj, event):
        if obj == self.target:
            if event.type() == QEvent.Type.Enter:
                self.illuminate()
            elif event.type() == QEvent.Type.Leave:
                self.extinguish()
        return super().eventFilter(obj, event)

    def illuminate(self):
        self.anim.stop()
        self.anim.setStartValue(self.glow.blurRadius())
        self.anim.setEndValue(self._intensity)
        self.anim.start()

    def extinguish(self):
        self.anim.stop()
        self.anim.setStartValue(self.glow.blurRadius())
        self.anim.setEndValue(0)
        self.anim.start()

    @staticmethod
    def light_up(widget, color="#0078d4", intensity=25):
        lo = LightsOff(widget)
        lo.set_glow(color, intensity)
        return lo

def illuminate_item(widget, color="#0078d4", intensity=25):
    return LightsOff.light_up(widget, color, intensity)
