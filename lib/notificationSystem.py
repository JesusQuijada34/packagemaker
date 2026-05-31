"""
Sistema de Notificaciones estilo Windows 11 para Package Maker
Notificaciones fluidas que aparecen desde el borde derecho con animaciones suaves.
"""
import os
import sys
from typing import Optional, List, Callable, Dict, Any
from dataclasses import dataclass, field
try:
    from PyQt6.QtCore import (
        Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QSize,
        pyqtSignal, QObject, QParallelAnimationGroup, QSequentialAnimationGroup
    )
    from PyQt6.QtWidgets import (
        QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
        QGraphicsDropShadowEffect, QApplication, QFrame, QSizePolicy
    )
    from PyQt6.QtGui import QColor, QIcon, QPixmap, QPainter, QFont, QFontMetrics
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    class QObject: pass
    class pyqtSignal:
        def __init__(self, *args): pass
        def connect(self, func): pass
        def emit(self, *args): pass
    class QWidget: pass


@dataclass
class NotificationAction:
    """Accion personalizada para la notificacion"""
    text: str
    callback: Callable[[], None]
    style: str = "default"  # default, primary, danger


@dataclass
class NotificationData:
    """Datos de una notificacion"""
    title: str
    message: str
    notification_type: str = "info"  # info, warning, error, success
    icon_path: Optional[str] = None
    duration: int = 5000  # ms, 0 = persistente
    actions: List[NotificationAction] = field(default_factory=list)
    show_close_button: bool = True
    clickable: bool = False
    on_click: Optional[Callable[[], None]] = None
    show_progress: bool = False  # Mostrar barra de progreso/marquee
    progress_value: int = -1  # -1 = marquee/indeterminado, 0-100 = valor fijo


class NotificationWidget(QWidget):
    """
    Widget de notificacion individual estilo Windows 11.
    Animacion suave desde el borde derecho, efecto hover hundido.
    """
    
    closed = pyqtSignal()
    clicked = pyqtSignal()
    
    # Colores estilo Windows 11
    COLORS = {
        "info": {
            "bg": "#ffffff",
            "border": "#e1e4e8",
            "accent": "#0078d4",
            "icon": "#0078d4",
            "text": "#1f1f1f",
            "subtext": "#5f5f5f"
        },
        "warning": {
            "bg": "#fff9e6",
            "border": "#ffd966",
            "accent": "#ffc107",
            "icon": "#ffc107",
            "text": "#1f1f1f",
            "subtext": "#5f5f5f"
        },
        "error": {
            "bg": "#fef2f2",
            "border": "#fecaca",
            "accent": "#ef4444",
            "icon": "#ef4444",
            "text": "#1f1f1f",
            "subtext": "#5f5f5f"
        },
        "success": {
            "bg": "#f0fdf4",
            "border": "#bbf7d0",
            "accent": "#22c55e",
            "icon": "#22c55e",
            "text": "#1f1f1f",
            "subtext": "#5f5f5f"
        }
    }
    
    # Iconos por defecto (Unicode)
    ICONS = {
        "info": "ℹ️",
        "warning": "⚠️",
        "error": "❌",
        "success": "✅"
    }
    
    def __init__(self, data: NotificationData, parent=None):
        super().__init__(parent)
        self.data = data
        self.is_hovered = False
        self._opacity = 1.0
        
        self._setup_window()
        self._setup_ui()
        self._setup_animations()
        self._setup_shadow()
        
    def _setup_window(self):
        """Configurar ventana sin bordes, siempre encima"""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # Tamaño fijo estilo Windows 11
        self.setFixedSize(360, 100)
        
    def _setup_ui(self):
        """Configurar UI con estilo Windows 11"""
        colors = self.COLORS.get(self.data.notification_type, self.COLORS["info"])
        
        # Container principal con bordes redondeados
        self.container = QFrame(self)
        self.container.setGeometry(10, 10, 340, 80)
        self.container.setObjectName("notificationContainer")
        
        # Estilo con bordes redondeados y sombra suave
        self.container.setStyleSheet(f"""
            #notificationContainer {{
                background-color: {colors['bg']};
                border: 1px solid {colors['border']};
                border-radius: 8px;
                border-left: 4px solid {colors['accent']};
            }}
        """)
        
        # Layout principal
        layout = QHBoxLayout(self.container)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)
        
        # Icono
        icon_label = QLabel()
        if self.data.icon_path and os.path.exists(self.data.icon_path):
            pixmap = QPixmap(self.data.icon_path).scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        else:
            icon_label.setText(self.ICONS.get(self.data.notification_type, "ℹ️"))
            icon_label.setStyleSheet(f"font-size: 24px; color: {colors['icon']}; background: transparent;")
        icon_label.setFixedSize(32, 32)
        layout.addWidget(icon_label)
        
        # Contenido (titulo + mensaje)
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Titulo
        title_label = QLabel(self.data.title)
        title_label.setStyleSheet(f"""
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 14px;
            font-weight: 600;
            color: {colors['text']};
            background: transparent;
            padding: 0;
            margin: 0;
        """)
        title_label.setWordWrap(False)
        content_layout.addWidget(title_label)
        
        # Mensaje
        msg_label = QLabel(self.data.message)
        msg_label.setStyleSheet(f"""
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 12px;
            color: {colors['subtext']};
            background: transparent;
            padding: 0;
            margin: 0;
        """)
        msg_label.setWordWrap(True)
        msg_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        content_layout.addWidget(msg_label)
        
        # Barra de progreso/marquee
        if self.data.show_progress:
            from PyQt6.QtWidgets import QProgressBar
            self.progress_bar = QProgressBar()
            self.progress_bar.setFixedHeight(4)
            self.progress_bar.setTextVisible(False)
            if self.data.progress_value == -1:
                # Modo marquee/indeterminado
                self.progress_bar.setRange(0, 0)
            else:
                self.progress_bar.setRange(0, 100)
                self.progress_bar.setValue(self.data.progress_value)
            # Estilo minimalista
            accent_color = colors['accent']
            self.progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    background-color: rgba(0, 0, 0, 0.1);
                    border: none;
                    border-radius: 2px;
                }}
                QProgressBar::chunk {{
                    background-color: {accent_color};
                    border-radius: 2px;
                }}
            """)
            content_layout.addWidget(self.progress_bar)
        
        # Botones de accion
        if self.data.actions:
            actions_layout = QHBoxLayout()
            actions_layout.setSpacing(8)
            for action in self.data.actions:
                btn = self._create_action_button(action, colors)
                actions_layout.addWidget(btn)
            actions_layout.addStretch()
            content_layout.addLayout(actions_layout)
        
        layout.addLayout(content_layout, stretch=1)
        
        # Boton X minimalista
        if self.data.show_close_button:
            close_btn = QPushButton("✕")
            close_btn.setFixedSize(20, 20)
            close_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    color: {colors['subtext']};
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 12px;
                    font-weight: 500;
                    border-radius: 4px;
                    padding: 0;
                    margin: 0;
                }}
                QPushButton:hover {{
                    background-color: rgba(0, 0, 0, 0.08);
                    color: {colors['text']};
                }}
                QPushButton:pressed {{
                    background-color: rgba(0, 0, 0, 0.15);
                }}
            """)
            close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            close_btn.clicked.connect(self.close_notification)
            layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignTop)
        
        # Click en la notificacion
        if self.data.clickable or self.data.on_click:
            self.container.setCursor(Qt.CursorShape.PointingHandCursor)
            
    def _create_action_button(self, action: NotificationAction, colors: Dict[str, str]) -> QPushButton:
        """Crear boton de accion estilizado"""
        btn = QPushButton(action.text)
        btn.setFixedHeight(24)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Estilos segun tipo
        if action.style == "primary":
            bg = colors['accent']
            text = "#ffffff"
            hover_bg = self._darken_color(colors['accent'], 0.9)
        elif action.style == "danger":
            bg = "#ef4444"
            text = "#ffffff"
            hover_bg = "#dc2626"
        else:  # default
            bg = "transparent"
            text = colors['accent']
            hover_bg = f"{colors['accent']}20"  # 20 = ~12% opacity en hex
            
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {text};
                border: {'none' if action.style != 'default' else f'1px solid {colors["border"]}'};
                border-radius: 4px;
                padding: 0 12px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 11px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
            }}
            QPushButton:pressed {{
                opacity: 0.8;
            }}
        """)
        
        btn.clicked.connect(lambda: self._handle_action(action))
        return btn
        
    def _darken_color(self, hex_color: str, factor: float) -> str:
        """Oscurecer un color hex"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(int(c * factor) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
        
    def _handle_action(self, action: NotificationAction):
        """Manejar click en accion"""
        try:
            action.callback()
        except Exception as e:
            print(f"Error en accion de notificacion: {e}")
        self.close_notification()
        
    def _setup_shadow(self):
        """Configurar sombra suave tipo Windows 11"""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.container.setGraphicsEffect(shadow)
        
    def _setup_animations(self):
        """Configurar animaciones de entrada y salida"""
        # Animacion de entrada: deslizar desde la derecha + fade in
        self.anim_group = QParallelAnimationGroup(self)
        
        # Animacion de posicion (desde fuera de pantalla)
        self.anim_pos = QPropertyAnimation(self, b"pos")
        self.anim_pos.setDuration(350)
        self.anim_pos.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Animacion de opacidad (fade in)
        self.anim_opacity = QPropertyAnimation(self, b"windowOpacity")
        self.anim_opacity.setDuration(300)
        self.anim_opacity.setStartValue(0.0)
        self.anim_opacity.setEndValue(1.0)
        self.anim_opacity.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.anim_group.addAnimation(self.anim_pos)
        self.anim_group.addAnimation(self.anim_opacity)
        
        # Animacion de salida
        self.anim_out = QParallelAnimationGroup()
        
        self.anim_out_pos = QPropertyAnimation(self, b"pos")
        self.anim_out_pos.setDuration(250)
        self.anim_out_pos.setEasingCurve(QEasingCurve.Type.InCubic)
        
        self.anim_out_opacity = QPropertyAnimation(self, b"windowOpacity")
        self.anim_out_opacity.setDuration(200)
        self.anim_out_opacity.setStartValue(1.0)
        self.anim_out_opacity.setEndValue(0.0)
        
        self.anim_out.addAnimation(self.anim_out_pos)
        self.anim_out.addAnimation(self.anim_out_opacity)
        self.anim_out.finished.connect(self._on_close_complete)
        
    def enterEvent(self, event):
        """Efecto hover: se 'hunde' (scale down ligeramente + sombra mas pronunciada)"""
        self.is_hovered = True
        
        # Animacion de escala suave (efecto hundido)
        self._scale_animation = QPropertyAnimation(self.container, b"geometry")
        self._scale_animation.setDuration(150)
        self._scale_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        current_geo = self.container.geometry()
        # Reducir ligeramente (2px en cada lado)
        new_geo = current_geo.adjusted(2, 2, -2, -2)
        
        self._scale_animation.setStartValue(current_geo)
        self._scale_animation.setEndValue(new_geo)
        self._scale_animation.start()
        
        # Sombra mas pronunciada
        shadow = self.container.graphicsEffect()
        if shadow:
            shadow.setBlurRadius(25)
            shadow.setYOffset(6)
            shadow.setColor(QColor(0, 0, 0, 60))
            
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Restaurar al salir del hover"""
        self.is_hovered = False
        
        # Restaurar escala
        if hasattr(self, '_scale_animation') and self._scale_animation:
            self._scale_animation.stop()
            
        current_geo = self.container.geometry()
        original_geo = self.rect().adjusted(10, 10, -10, -10)
        
        self._restore_animation = QPropertyAnimation(self.container, b"geometry")
        self._restore_animation.setDuration(150)
        self._restore_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._restore_animation.setStartValue(current_geo)
        self._restore_animation.setEndValue(original_geo)
        self._restore_animation.start()
        
        # Restaurar sombra
        shadow = self.container.graphicsEffect()
        if shadow:
            shadow.setBlurRadius(20)
            shadow.setYOffset(4)
            shadow.setColor(QColor(0, 0, 0, 40))
            
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        """Manejar click en la notificacion"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.data.on_click:
                try:
                    self.data.on_click()
                except Exception as e:
                    print(f"Error en click de notificacion: {e}")
            self.clicked.emit()
        super().mousePressEvent(event)
        
    def show_notification(self, target_pos: QPoint):
        """Mostrar la notificacion con animacion"""
        # Posicion inicial (fuera de pantalla a la derecha)
        screen = QApplication.primaryScreen().geometry()
        start_x = screen.width()
        start_y = target_pos.y()
        
        # Posicion final
        end_x = target_pos.x()
        end_y = target_pos.y()
        
        # Configurar animacion
        self.anim_pos.setStartValue(QPoint(start_x + 50, start_y))  # 50px fuera
        self.anim_pos.setEndValue(QPoint(end_x, end_y))
        
        # Mostrar y animar
        self.move(start_x + 50, start_y)
        self.setWindowOpacity(0.0)
        self.show()
        
        self.anim_group.start()
        
        # Timer para auto-cerrar (si no es persistente)
        if self.data.duration > 0 and not self.is_hovered:
            QTimer.singleShot(self.data.duration, self.close_notification)
            
        # Timer para pausar cierre al hacer hover
        self._check_hover_timer = QTimer(self)
        self._check_hover_timer.timeout.connect(self._check_hover)
        self._check_hover_timer.start(100)
        
    def _check_hover(self):
        """Verificar si el mouse esta sobre la notificacion"""
        if self.is_hovered:
            # Resetear el timer de cierre
            pass  # Implementar logica de pausa si es necesario
            
    def close_notification(self):
        """Cerrar notificacion con animacion"""
        # Detener timer
        if hasattr(self, '_check_hover_timer'):
            self._check_hover_timer.stop()
            
        # Si esta en hover, esperar a que salga
        if self.is_hovered:
            QTimer.singleShot(500, self.close_notification)
            return
            
        # Animar salida
        current_pos = self.pos()
        self.anim_out_pos.setStartValue(current_pos)
        self.anim_out_pos.setEndValue(QPoint(current_pos.x() + 100, current_pos.y()))
        
        self.anim_out.start()
        
    def _on_close_complete(self):
        """Llamado cuando termina la animacion de cierre"""
        self.closed.emit()
        self.close()
        self.deleteLater()


class NotificationManager(QObject):
    """
    Manager de notificaciones. Gestiona posicionamiento, cola, 
    y multiples notificaciones en pantalla.
    """
    
    MAX_NOTIFICATIONS = 5
    NOTIFICATION_HEIGHT = 100
    NOTIFICATION_SPACING = 10
    MARGIN_RIGHT = 20
    MARGIN_BOTTOM = 20
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.notifications: List[NotificationWidget] = []
        self.queue: List[NotificationData] = []
        
    def notify(
        self,
        title: str,
        message: str,
        notification_type: str = "info",
        icon_path: Optional[str] = None,
        duration: int = 5000,
        actions: List[NotificationAction] = None,
        show_close: bool = True,
        on_click: Optional[Callable[[], None]] = None,
        clickable: bool = False,
        show_progress: bool = False,
        progress_value: int = -1
    ) -> NotificationWidget:
        """
        Mostrar una notificacion.
        
        Args:
            title: Titulo de la notificacion
            message: Mensaje/descripcion
            notification_type: info, warning, error, success
            icon_path: Ruta a icono personalizado (opcional)
            duration: Duracion en ms (0 = persistente)
            actions: Lista de acciones/botones
            show_close: Mostrar boton X
            on_click: Callback al hacer click
            clickable: Si es clickable
            show_progress: Mostrar barra de progreso/marquee
            progress_value: Valor del progreso (-1 = marquee)
        """
        data = NotificationData(
            title=title,
            message=message,
            notification_type=notification_type,
            icon_path=icon_path,
            duration=duration,
            actions=actions or [],
            show_close_button=show_close,
            on_click=on_click,
            clickable=clickable,
            show_progress=show_progress,
            progress_value=progress_value
        )
        
        return self._show_notification(data)
        
    def info(self, title: str, message: str, **kwargs) -> NotificationWidget:
        """Notificacion informativa"""
        return self.notify(title, message, "info", **kwargs)
        
    def warning(self, title: str, message: str, **kwargs) -> NotificationWidget:
        """Notificacion de advertencia"""
        return self.notify(title, message, "warning", **kwargs)
        
    def error(self, title: str, message: str, **kwargs) -> NotificationWidget:
        """Notificacion de error"""
        return self.notify(title, message, "error", **kwargs)
        
    def success(self, title: str, message: str, **kwargs) -> NotificationWidget:
        """Notificacion de exito"""
        return self.notify(title, message, "success", **kwargs)
        
    def _show_notification(self, data: NotificationData) -> NotificationWidget:
        """Crear y mostrar widget de notificacion"""
        # Si hay demasiadas notificaciones, encolar
        if len(self.notifications) >= self.MAX_NOTIFICATIONS:
            self.queue.append(data)
            return None
            
        # Crear widget
        notification = NotificationWidget(data)
        notification.closed.connect(lambda: self._on_notification_closed(notification))
        
        # Calcular posicion
        pos = self._calculate_position(len(self.notifications))
        
        # Agregar a lista y mostrar
        self.notifications.append(notification)
        notification.show_notification(pos)
        
        return notification
        
    def _calculate_position(self, index: int) -> QPoint:
        """Calcular posicion en pantalla para la notificacion"""
        screen = QApplication.primaryScreen().geometry()
        
        # X: alineado a la derecha con margen
        x = screen.width() - 360 - self.MARGIN_RIGHT  # 360 = ancho notificacion
        
        # Y: desde abajo hacia arriba
        y = screen.height() - self.MARGIN_BOTTOM - (index + 1) * (self.NOTIFICATION_HEIGHT + self.NOTIFICATION_SPACING)
        
        return QPoint(x, y)
        
    def _on_notification_closed(self, notification: NotificationWidget):
        """Manejar cierre de notificacion"""
        if notification in self.notifications:
            self.notifications.remove(notification)
            
        # Reposicionar notificaciones restantes
        self._reposition_notifications()
        
        # Procesar cola
        if self.queue:
            next_data = self.queue.pop(0)
            QTimer.singleShot(100, lambda: self._show_notification(next_data))
            
    def _reposition_notifications(self):
        """Animar reposicionamiento de notificaciones"""
        for i, notification in enumerate(self.notifications):
            new_pos = self._calculate_position(i)
            
            # Animar a nueva posicion
            anim = QPropertyAnimation(notification, b"pos")
            anim.setDuration(250)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.setStartValue(notification.pos())
            anim.setEndValue(new_pos)
            anim.start()


# Instancia global del manager
_notification_manager: Optional[NotificationManager] = None


def get_notification_manager() -> NotificationManager:
    """Obtener instancia global del manager de notificaciones"""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager


# Funciones de conveniencia para usar facilmente
def notify(
    title: str,
    message: str,
    notification_type: str = "info",
    duration: int = 5000,
    **kwargs
) -> NotificationWidget:
    """Mostrar notificacion"""
    return get_notification_manager().notify(
        title, message, notification_type, duration=duration, **kwargs
    )


def info(title: str, message: str, duration: int = 5000, **kwargs) -> NotificationWidget:
    """Notificacion informativa"""
    return get_notification_manager().info(title, message, duration=duration, **kwargs)


def warning(title: str, message: str, duration: int = 5000, **kwargs) -> NotificationWidget:
    """Notificacion de advertencia"""
    return get_notification_manager().warning(title, message, duration=duration, **kwargs)


def error(title: str, message: str, duration: int = 0, **kwargs) -> NotificationWidget:
    """Notificacion de error (persistente por defecto)"""
    return get_notification_manager().error(title, message, duration=duration, **kwargs)


def success(title: str, message: str, duration: int = 5000, **kwargs) -> NotificationWidget:
    """Notificacion de exito"""
    return get_notification_manager().success(title, message, duration=duration, **kwargs)


def loading(title: str, message: str, **kwargs) -> NotificationWidget:
    """Notificacion de carga con marquee animado (persistente)"""
    return get_notification_manager().notify(
        title, message, "info", duration=0, show_progress=True, progress_value=-1, **kwargs
    )


def error_handler(title: str, error_message: str, error_details: str = "", duration: int = 0, **kwargs) -> NotificationWidget:
    """Notificacion de error con boton para copiar al portapapeles"""
    import pyperclip
    
    full_error = f"{error_message}\n{error_details}" if error_details else error_message
    
    def copy_error():
        try:
            pyperclip.copy(full_error)
            # Mostrar mini confirmacion
            success("Copiado", "Error copiado al portapapeles", duration=2000)
        except Exception as e:
            print(f"Error copiando: {e}")
    
    actions = kwargs.pop('actions', [])
    actions.insert(0, NotificationAction("📋 Copiar error", copy_error, "primary"))
    
    return get_notification_manager().error(title, error_message, duration=duration, actions=actions, **kwargs)


# Ejemplo de uso:
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget
    
    app = QApplication(sys.argv)
    
    # Ventana de prueba
    window = QWidget()
    window.setWindowTitle("Test Notificaciones Windows 11")
    window.resize(400, 300)
    
    layout = QVBoxLayout()
    
    def test_info():
        info(
            "Descarga completada",
            "El archivo 'proyecto_v2.iflapp' se ha descargado correctamente.",
            actions=[
                NotificationAction("Abrir", lambda: print("Abriendo..."), "primary"),
                NotificationAction("Ver carpeta", lambda: print("Abriendo carpeta..."))
            ]
        )
        
    def test_warning():
        warning(
            "Espacio bajo",
            "Quedan menos de 500MB de espacio en disco."
        )
        
    def test_error():
        error(
            "Error de compilacion",
            "No se pudo compilar el proyecto. Revisa los logs.",
            actions=[
                NotificationAction("Ver logs", lambda: print("Abriendo logs..."), "primary")
            ]
        )
        
    def test_success():
        success(
            "Instalacion exitosa",
            "La aplicacion se ha instalado correctamente en Fluthin Apps."
        )
        
    def test_multiple():
        # Mostrar multiples notificaciones
        for i in range(3):
            QTimer.singleShot(i * 300, lambda idx=i: info(
                f"Notificacion {idx + 1}",
                f"Esta es la notificacion numero {idx + 1}"
            ))
    
    btn_info = QPushButton("Notificacion Info")
    btn_info.clicked.connect(test_info)
    layout.addWidget(btn_info)
    
    btn_warning = QPushButton("Notificacion Warning")
    btn_warning.clicked.connect(test_warning)
    layout.addWidget(btn_warning)
    
    btn_error = QPushButton("Notificacion Error")
    btn_error.clicked.connect(test_error)
    layout.addWidget(btn_error)
    
    btn_success = QPushButton("Notificacion Success")
    btn_success.clicked.connect(test_success)
    layout.addWidget(btn_success)
    
    btn_multiple = QPushButton("Multiples Notificaciones")
    btn_multiple.clicked.connect(test_multiple)
    layout.addWidget(btn_multiple)
    
    window.setLayout(layout)
    window.show()
    
    sys.exit(app.exec())
