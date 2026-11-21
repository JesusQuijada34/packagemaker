import sys
import ctypes
from PyQt6.QtCore import Qt, QObject, QEvent
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen
import difflib

# Importamos el capturador de acento desde la librería base
from .title_bar import get_accent_color

class WipeWindow(QObject):
    """
    ✨ WipeWindow: Premium Aesthetics for Windows.
    Modes:
    - 'polished': Solid background with rounded corners and shadow.
    - 'ghost': Completely invisible window (ideal for overlays).
    - 'ghostBlur': Transparent with blur effect (frosted glass).
    - 'mica': Windows 11 Mica material effect.
    """

    def __getattr__(self, name):
        valid_methods = [m for m in dir(self) if m.startswith('set_') or m in ['apply', 'create']]
        suggestions = difflib.get_close_matches(name, valid_methods)
        def error_handler(*args, **kwargs):
            hint = f" 🤔 Did you mean: '{suggestions[0]}'?" if suggestions else ""
            raise AttributeError(f"❌ WipeWindow: '{name}' does not exist.{hint}")
        return error_handler

    def __init__(self, parent=None):
        super().__init__(parent)
        self._bg_source = "auto" 
        self._radius = 15
        self._shadow_blur = 35
        self._mode = "polished" # "polished", "ghost", or "ghostBlur"
        self._target = None
        self._blur_radius = 30  # For ghostBlur mode

    def set_mode(self, mode):
        """'polished', 'ghost', or 'ghostBlur'."""
        self._mode = mode
        return self

    def set_background(self, source):
        """Hex Color or 'auto'."""
        self._bg_source = source
        return self

    def set_radius(self, radius):
        """Set corner radius for rounded edges."""
        self._radius = radius
        return self

    def set_blur(self, blur_radius):
        """Set blur intensity for ghostBlur mode."""
        self._blur_radius = blur_radius
        return self

    def apply(self, widget):
        """Applies high-fidelity polishing with GC safety."""
        self._target = widget
        # IMPORTANT: We anchor this object to the widget to prevent Garbage Collection
        self.setParent(widget)
        
        # 1. Window Configuration
        widget.setWindowFlags(widget.windowFlags() | Qt.WindowType.FramelessWindowHint)
        widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 2. Install event filter for custom painting
        widget.installEventFilter(self)
        
        # 3. Adjust margins for shadow - shadows render OUTSIDE the content area
        # Top margin is 0 to allow title bar to sit at the edge
        if self._mode == "polished" and widget.layout():
            # Increased margin to ensure shadows are fully outside
            m = self._shadow_blur + 5
            widget.layout().setContentsMargins(m, 0, m, m)
        elif self._mode in ["ghost", "ghostBlur"] and widget.layout():
            widget.layout().setContentsMargins(0, 0, 0, 0)

        # 4. Windows 11 Corners (If polished) - We use winId() to force handle creation without showing
        if sys.platform == "win32" and self._mode == "polished":
            try:
                hWnd = int(widget.winId())
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hWnd, 33, ctypes.byref(ctypes.c_int(2)), 4)
            except: pass

        # 5. Apply Windows 11 Mica Backdrop
        if sys.platform == "win32" and self._mode == "mica":
            try:
                hWnd = int(widget.winId())
                # DWM_SYSTEMBACKDROP_TYPE: 2 = Mica, 3 = Acrylic, 4 = MicaAlt
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hWnd, 38, ctypes.byref(ctypes.c_int(2)), 4)
            except: pass

        # 6. Apply Windows Acrylic/Blur effect for ghostBlur mode
        if self._mode == "ghostBlur":
            try:
                hWnd = int(widget.winId())
                # Enable blur behind (DWM_BLURBEHIND)
                
                class AccentPolicy(ctypes.Structure):
                    _fields_ = [
                        ("AccentState", ctypes.c_int),
                        ("AccentFlags", ctypes.c_int),
                        ("GradientColor", ctypes.c_int),
                        ("AnimationId", ctypes.c_int)
                    ]
                
                class WindowCompositionAttributeData(ctypes.Structure):
                    _fields_ = [
                        ("Attribute", ctypes.c_int),
                        ("Data", ctypes.POINTER(ctypes.c_int)),
                        ("SizeOfData", ctypes.c_size_t)
                    ]
                
                accent = AccentPolicy(3, 2, 0x01000000, 0)
                data = WindowCompositionAttributeData(
                    19,  # WCA_ACCENT_POLICY
                    ctypes.cast(ctypes.pointer(accent), ctypes.POINTER(ctypes.c_int)),
                    ctypes.sizeof(accent)
                )
                
                ctypes.windll.user32.SetWindowCompositionAttribute(hWnd, ctypes.byref(data))
            except:
                pass  # Fallback if Windows API not available
            
        widget.update()
        return self

    def eventFilter(self, obj, event):
        if obj == self._target and event.type() == QEvent.Type.Paint:
            self._paint_logic(obj)
            return False # Let children paint on top
        return super().eventFilter(obj, event)

    def _paint_logic(self, widget):
        painter = QPainter(widget)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self._mode == "ghost":
            painter.end()
            return

        if self._mode == "mica":
            # For Mica, we need to let the system backdrop show through.
            # Painting a very subtle transparent layer can help with visibility of content.
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(0, 0, 0, 1))) 
            painter.drawRect(widget.rect())
            painter.end()
            return

        if self._mode == "ghostBlur":
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(255, 255, 255, 35)))  # Light glass tint
            painter.drawRoundedRect(widget.rect(), self._radius, self._radius)
            painter.setBrush(QBrush(QColor(255, 255, 255, 20)))
            painter.drawRoundedRect(widget.rect().adjusted(1, 1, -1, -1), self._radius - 1, self._radius - 1)
            painter.end()
            return

        # Polished Mode: Paint background to FULL widget size, shadows outside
        full_rect = widget.rect()
        
        # Draw shadows AROUND the full rect (they extend into the transparent area)
        shadow_offset = self._shadow_blur // 2
        for i in range(shadow_offset):
            opacity = int((140 / shadow_offset) * (shadow_offset - i) * 0.3)
            painter.setPen(QPen(QColor(0, 0, 0, opacity), 1))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            shadow_rect = full_rect.adjusted(-i, -i, i, i)
            painter.drawRoundedRect(shadow_rect, self._radius + i, self._radius + i)

        # Solid Background fills the ENTIRE widget rect
        bg_color = get_accent_color() if self._bg_source == "auto" else self._bg_source
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(bg_color)))
        painter.drawRoundedRect(full_rect, self._radius, self._radius)
        painter.end()

    @staticmethod
    def create(): return WipeWindow()
