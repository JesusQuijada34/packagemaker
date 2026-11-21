import platform

try:
    import winreg
except ImportError:
    winreg = None

from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import QLabel

try:
    from PyQt6.QtGui import QTouchDevice
except ImportError:
    QTouchDevice = None


class TouchScreen:
    """Driver táctil de Leviathan UI.
    Detecta si el equipo dispone de pantalla táctil y aplica ajustes compactos,
    transiciones tipo UWP y soporte para navegación atrás con snapshot en RAM.
    """
    def __init__(self, parent=None):
        self.parent = parent
        self.enabled = self.detect_touch_device()
        self.history = []

    @staticmethod
    def detect_touch_device() -> bool:
        # 1. Prefer native Qt touchscreen enumeration if available.
        try:
            if QTouchDevice is not None:
                devices = QTouchDevice.devices()
                if len(devices) > 0:
                    return True
        except Exception:
            pass

        # 2. Fallback: Windows registry compatibility hints.
        if platform.system() != "Windows" or winreg is None:
            return False

        registry_paths = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Wisp\Touch", "TouchGate"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Pen\Touch", "TouchGate"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Wisp\Touch", "EnableTouch"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\TabletPC\Sensors\Touch", "Enabled")
        ]

        for root, path, value_name in registry_paths:
            try:
                with winreg.OpenKey(root, path, 0, winreg.KEY_READ) as key:
                    value, _ = winreg.QueryValueEx(key, value_name)
                    if isinstance(value, int) and value != 0:
                        return True
            except FileNotFoundError:
                continue
            except Exception:
                continue

        return False

    def capture_snapshot(self, widget):
        if not self.enabled or widget is None:
            return None
        try:
            return widget.grab()
        except Exception:
            return None

    def animate_snapshot_transition(self, pixmap):
        if not self.enabled or pixmap is None or self.parent is None:
            return

        overlay = QLabel(self.parent)
        overlay.setPixmap(pixmap)
        overlay.setScaledContents(True)
        overlay.setGeometry(self.parent.rect())
        overlay.show()
        overlay.raise_()

        fade = QPropertyAnimation(overlay, b"windowOpacity")
        fade.setDuration(420)
        fade.setStartValue(1.0)
        fade.setEndValue(0.0)
        fade.setEasingCurve(QEasingCurve.Type.InOutQuad)
        fade.finished.connect(overlay.deleteLater)
        fade.start()

    def apply_touch_layout(self, window):
        if not self.enabled or window is None:
            return

        # Forzar ventana a pantalla completa y compactar márgenes.
        window.setMinimumSize(720, 540)
        window.setWindowState(Qt.WindowState.WindowFullScreen)
        window.root_layout.setContentsMargins(14, 14, 14, 14)
        window.root_layout.setSpacing(10)

        if hasattr(window, 'bottom_bar'):
            window.bottom_bar.setFixedHeight(110)
        if hasattr(window, 'progress_bar'):
            window.progress_bar.setFixedHeight(10)
        if hasattr(window, 'btn_next'):
            window.btn_next.setFixedSize(190, 48)
            window.btn_next.setStyleSheet("QPushButton { font-size: 15px; padding: 0 20px; }")

        # Compactar cada página para mejor uso táctil.
        for page in getattr(window, 'pages', []):
            if hasattr(page, 'layout'):
                page.layout.setContentsMargins(18, 18, 18, 18)
                page.layout.setSpacing(14)

    def prepare_back_button(self, title_bar, callback):
        if not self.enabled or title_bar is None or callback is None:
            return
        title_bar.enable_back_button(callback)
