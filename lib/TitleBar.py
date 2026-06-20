try:
    from PyQt6.QtWidgets import QPushButton, QWidget, QHBoxLayout, QLabel
    from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter
    from PyQt6.QtCore import Qt, QSize, QVariantAnimation, QAbstractAnimation, QPoint
    from PyQt6.QtGui import QShowEvent
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    class QPushButton:
        def __init__(self, *args, **kwargs): pass
        def setFixedSize(self, *args): pass
        def setIconSize(self, *args): pass
        def setFlat(self, *args): pass
        def setIcon(self, *args): pass
        def update(self): pass
    class QWidget:
        def __init__(self, *args, **kwargs): pass
        def setFixedHeight(self, *args): pass
        def setLayout(self, *args): pass
        def setContentsMargins(self, *args): pass
        def setStyleSheet(self, *args): pass
    class Qt:
        class AlignmentFlag: AlignVCenter = 0; AlignLeft = 0
        class MouseButton: LeftButton = 0
    class QSize:
        def __init__(self, *args, **kwargs): pass
    class QColor:
        def __init__(self, *args, **kwargs): pass
    class QPoint:
        def __init__(self, *args, **kwargs): pass
    class QVariantAnimation:
        def __init__(self, *args, **kwargs): pass
        def setDuration(self, *args): pass
        def setStartValue(self, *args): pass
        def setEndValue(self, *args): pass
        class valueChanged:
            @staticmethod
            def connect(func): pass
    class QPainter:
        class RenderHint: Antialiasing = 0
        def __init__(self, *args, **kwargs): pass
        def setRenderHint(self, *args): pass
        def fillRect(self, *args): pass
    class QAbstractAnimation:
        class Direction: Forward = 0; Backward = 0
    class QLabel:
        def __init__(self, *args, **kwargs): pass
        def setPixmap(self, *args): pass
        def setFixedSize(self, *args): pass
        def setAlignment(self, *args): pass
        def setStyleSheet(self, *args): pass
        def setObjectName(self, *args): pass
    class QHBoxLayout:
        def __init__(self, *args, **kwargs): pass
        def setContentsMargins(self, *args): pass
        def setSpacing(self, *args): pass
        def addWidget(self, *args): pass
        def addStretch(self, *args): pass
    class QShowEvent: pass
    class QIcon:
        def __init__(self, *args): pass
    class QPixmap:
        def __init__(self, *args, **kwargs): pass
        def loadFromData(self, *args): pass

class AnimTitleButton(QPushButton):
    """Boton de titulo con animación de fondo suave (UWP Style)"""
    def __init__(self, icon_svg, hover_color, parent=None):
        super().__init__(parent)
        self.setFixedSize(46, 32)
        self.setIconSize(QSize(16, 16))
        self.setFlat(True)
        self.hover_color = hover_color
        self.default_color = QColor(0, 0, 0, 0)
        
        # Guardar el SVG para crear el QPixmap más tarde
        self.icon_svg = icon_svg
        self._icon_created = False

        self._bg_color = self.default_color
        self.anim = QVariantAnimation(self)
        self.anim.setDuration(150)
        self.anim.setStartValue(self.default_color)
        self.anim.setEndValue(QColor(self.hover_color))
        self.anim.valueChanged.connect(self._update_bg)
    
    def _create_icon(self):
        """Crea el icono solo cuando sea necesario y seguro"""
        if not self._icon_created:
            try:
                pm = QPixmap()
                pm.loadFromData(self.icon_svg)
                self.setIcon(QIcon(pm))
                self._icon_created = True
            except Exception as e:
                print(f"Warning: Could not create icon: {e}")
                # Crear un icono vacío como fallback
                self.setIcon(QIcon())

    def _update_bg(self, color):
        self._bg_color = color
        self.update()

    def showEvent(self, event):
        """Asegurar que el icono se cree cuando el widget se muestra"""
        super().showEvent(event)
        self._create_icon()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), self._bg_color)
        super().paintEvent(event)

    def enterEvent(self, event):
        self.anim.setDirection(QAbstractAnimation.Direction.Forward)
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.anim.setDirection(QAbstractAnimation.Direction.Backward)
        self.anim.start()
        super().leaveEvent(event)

class TitleBar(QWidget):
    """Custom non-native title bar with UWP-style animated buttons."""

    def __init__(self, parent=None, app_icon=None, title=""):
        super().__init__(parent)
        self._parent = parent
        self.setFixedHeight(40)
        self.setObjectName("customTitleBar")
        self._drag_active = False
        self._drag_offset = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 0, 0)
        layout.setSpacing(10)

        if app_icon:
            icon_lbl = QLabel()
            icon_lbl.setPixmap(app_icon.pixmap(20, 20))
            icon_lbl.setFixedSize(20, 20)
            layout.addWidget(icon_lbl)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.title_label.setStyleSheet("font-size: 13px; font-weight: 500; font-family: 'Segoe UI'; color: #eeeeee;")
        layout.addWidget(self.title_label)
        layout.addStretch()

        self.setMouseTracking(True)

        btnc = QWidget()
        btnl = QHBoxLayout(btnc)
        btnl.setContentsMargins(0, 0, 0, 0)
        btnl.setSpacing(0)

        self.svg_min = b'''\
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <line x1="7" y1="12" x2="17" y2="12" stroke="#ffffff" stroke-width="1"/>
        </svg>
        '''
        self.svg_max = b'''\
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="7.5" y="7.5" width="9" height="9" stroke="#ffffff" stroke-width="1" fill="none"/>
        </svg>
        '''
        self.svg_close = b'''\
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M7 7L17 17M17 7L7 17" stroke="#ffffff" stroke-width="1.2"/>
        </svg>
        '''

        self.btn_min = AnimTitleButton(self.svg_min, "rgba(255, 255, 255, 0.1)")
        self.btn_max = AnimTitleButton(self.svg_max, "rgba(255, 255, 255, 0.1)")
        self.btn_close = AnimTitleButton(self.svg_close, "#e81123")

        btnl.addWidget(self.btn_min)
        btnl.addWidget(self.btn_max)
        btnl.addWidget(self.btn_close)
        layout.addWidget(btnc)

        self.btn_min.clicked.connect(lambda: self.window().showMinimized())
        self.btn_close.clicked.connect(lambda: self.window().close())

        def toggle_maximize():
            win = self.window()
            if win.isMaximized():
                win.showNormal()
            else:
                win.showMaximized()

        self.btn_max.clicked.connect(toggle_maximize)

        def is_maximized():
            return self.window().isMaximized()

        def mousePressEvent(event):
            if event.button() == Qt.LeftButton and not is_maximized():
                self._drag_active = True
                self._drag_offset = event.globalPos() - self.window().frameGeometry().topLeft()
            event.accept()

        def mouseMoveEvent(event):
            if self._drag_active and not is_maximized():
                self.window().move(event.globalPos() - self._drag_offset)
            event.accept()

        def mouseReleaseEvent(event):
            if event.button() == Qt.LeftButton:
                self._drag_active = False
                self._drag_offset = None
            event.accept()

        def mouseDoubleClickEvent(event):
            if event.button() == Qt.LeftButton:
                toggle_maximize()

        self.mousePressEvent = mousePressEvent
        self.mouseMoveEvent = mouseMoveEvent
        self.mouseReleaseEvent = mouseReleaseEvent
        self.mouseDoubleClickEvent = mouseDoubleClickEvent
