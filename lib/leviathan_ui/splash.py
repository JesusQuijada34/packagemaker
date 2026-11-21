import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QRect, QEasingCurve, QParallelAnimationGroup
from PyQt6.QtGui import QFont, QColor, QPainter, QIcon

from .title_bar import get_accent_color, is_icon_file



class InmersiveSplash(QWidget):
    """
    🌊 InmersiveSplash: Ciclo de vida completo del Bot.
    Modos: 
    - adaptive: Ocupa toda la pantalla respetando la barra de tareas.
    - full: Ocupa absolutamente toda la pantalla (Kiosk).
    - appx: Integrado en ventana principal (estilo APPX/UWP).
    """
    def __init__(self, title="Sincronizando...", subtitle=None, logo="🐉", icon_text=None,
                 color="auto", bg_color=None, accent_color=None, is_exit=False, 
                 splash_type="LV", parent=None, show_progress=True):
        super().__init__(parent=parent)
        self._target_window = parent
        self.is_exit = is_exit
        self._title = title
        self._subtitle = subtitle
        self._logo = logo
        self._icon_text = icon_text
        self._color_cfg = color
        self._bg_color = bg_color
        self._accent_color = accent_color
        self._type = splash_type.upper()
        self._mode = "adaptive"
        self._phrases = []
        self._callback = None
        self._marquee = False
        self._final_color = accent_color or "#0078d4"
        self._show_progress = show_progress
        self._embedded_mode = False
        
        # Flags de ventana
        if self._target_window:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        else:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)


    def set_mode(self, mode):
        """'adaptive' o 'full'."""
        self._mode = mode
        return self

    def set_phrases(self, phrases):
        """Lista de strings que se mostrarán durante la carga."""
        self._phrases = phrases
        return self

    def on_finish(self, callback):
        self._callback = callback
        return self

    def set_progress_mode(self, marquee=False):
        self._marquee = marquee
        return self

    def launch(self):
        # 1. Ajuste de Pantalla
        if self._target_window:
            self.setParent(self._target_window)
            self.setGeometry(self._target_window.rect())
            self._target_window.setEnabled(False)
        else:
            screen = QApplication.primaryScreen()
            if screen is None:
                geom = QRect(0, 0, 480, 320)
            else:
                # Splash centrado de tamaño fijo, no pantalla completa
                screen_geom = screen.availableGeometry()
                splash_w, splash_h = 480, 320
                x = screen_geom.x() + (screen_geom.width() - splash_w) // 2
                y = screen_geom.y() + (screen_geom.height() - splash_h) // 2
                geom = QRect(x, y, splash_w, splash_h)
            self.setGeometry(geom)
        
        # 2. Color de Fondo
        self._final_color = get_accent_color() if self._color_cfg == "auto" else self._color_cfg
        
        # 3. UI
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Botones de control si es UWP o BUNDLED
        if self._type in ["UWP", "BUNDLED"]:
            from .title_bar import CustomTitleBar
            self.title_bar = CustomTitleBar(self, title="", icon="", hide_max=False)
            self.title_bar.setStyleSheet("background: transparent;")
            self.title_bar.title_lbl.hide()
            self.title_bar.icon_lbl.hide()
            self.main_layout.addWidget(self.title_bar, alignment=Qt.AlignmentFlag.AlignTop)

        content_layout = QVBoxLayout()
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.setSpacing(30)
        self.main_layout.addLayout(content_layout, 1)
        
        # Configuración según TYPE
        if self._type == "UWP":
            self._logo = "app/app-icon.ico" if os.path.exists("app/app-icon.ico") else self._logo
            self._marquee = True
            # Usar color configurado si existe, si no usar el del sistema
            if self._color_cfg == "auto":
                self._final_color = get_accent_color()
            else:
                self._final_color = self._color_cfg
        elif self._type == "BUNDLED":
            self._logo = "assets/splash.png" if os.path.exists("assets/splash.png") else self._logo
            self._marquee = True
            if self._color_cfg == "auto":
                self._final_color = get_accent_color()
            else:
                self._final_color = self._color_cfg

        self.logo_lbl = QLabel()
        if is_icon_file(self._logo):
            icon_obj = QIcon(self._logo)
            size_px = 192 if self._type in ["UWP", "BUNDLED"] else 256
            pixmap = icon_obj.pixmap(size_px, size_px)
            
            if not pixmap.isNull():
                self.logo_lbl.setPixmap(pixmap)
            else:
                self.logo_lbl.setText(self._logo)
                self.logo_lbl.setFont(QFont("Segoe UI Variable Display", 120))

        else:
            self.logo_lbl.setText(self._logo)
            self.logo_lbl.setFont(QFont("Segoe UI Variable Display", 120))

        self.logo_lbl.setStyleSheet("color: white; background: transparent;")
        content_layout.addWidget(self.logo_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        
        from .progress_bar import LeviathanProgressBar
        self.pbar = LeviathanProgressBar()
        self.pbar.setFixedWidth(int(self.width() * 0.4))
        self.pbar.setFixedHeight(8)
        if self._marquee:
            self.pbar.setMarquee(True)
        else:
            self.pbar.setRange(0, 100)
        content_layout.addWidget(self.pbar, alignment=Qt.AlignmentFlag.AlignCenter)
        
        if self._type == "LV":
            # Mostrar título
            self.status_lbl = QLabel(self._title)
            self.status_lbl.setStyleSheet("color: white; font-family: 'Segoe UI'; font-size: 22px; font-weight: 600; background: transparent;")
            content_layout.addWidget(self.status_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
            
            # Mostrar subtitle si existe
            if self._subtitle:
                self.subtitle_lbl = QLabel(self._subtitle)
                self.subtitle_lbl.setStyleSheet("color: rgba(255,255,255,0.7); font-family: 'Segoe UI'; font-size: 14px; background: transparent;")
                content_layout.addWidget(self.subtitle_lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        # 4. Animación de Entrada
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(800)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.start()
        
        # 5. Lógica de Pasos / Timer
        self._current_step = 0
        self.timer = QTimer()
        
        if self._type in ["UWP", "BUNDLED"]:
            # Esperar a que termine el fade-in, LUEGO mostrar por 3 segundos
            self.fade_in.finished.connect(lambda: QTimer.singleShot(3000, self._close_splash))
        else:
            # Modo LV clásico con frases
            self.timer.timeout.connect(self._update_progress)
            self.timer.start(800) 
        
        self.show()
        self.raise_()
        return self


    def _update_progress(self):
        if not self._phrases:
            self._phrases = ["Analizando datos...", "Sincronizando...", "Preparando interfaz..."]
            
        if self._current_step < len(self._phrases):
            msg = self._phrases[self._current_step]
            prog = int(((self._current_step + 1) / len(self._phrases)) * 100)
            self.status_lbl.setText(msg)
            self.pbar.value = prog
            self._current_step += 1
        else:
            self.timer.stop()
            QTimer.singleShot(600, self._close_splash)

    def _close_splash(self):
        self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out.setDuration(600)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.Type.InOutQuad)

        if self._target_window:
            self.slide_out = QPropertyAnimation(self, b"pos")
            self.slide_out.setDuration(600)
            self.slide_out.setStartValue(self.pos())
            self.slide_out.setEndValue(self.pos() + QPoint(0, 48))
            self.slide_out.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.slide_out.start()

        self.fade_out.finished.connect(self._finalize)
        self.fade_out.start()

    def _finalize(self):
        if self._target_window:
            self._target_window.setEnabled(True)
        self.close()
        if self.is_exit:
            QApplication.instance().quit()
        elif self._callback:
            self._callback()

    def set_show_progress(self, show):
        """Mostrar u ocultar la barra de progreso."""
        self._show_progress = show
        return self

    def attach_to_main_window(self, main_window, content_container):
        """
        Modo APPX: Muestra el splash como overlay en el contenedor de contenido.
        El splash cubre solo el área de contenido dejando visible titlebar y buttonbar.
        """
        self._embedded_mode = True
        self._target_window = main_window

        # Crear el splash como widget overlay sobre el content_container
        self.setParent(content_container)
        self.setGeometry(content_container.rect())
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)  # No bloquear clicks

        # Color de fondo - usar el configurado o el del sistema
        if self._color_cfg == "auto":
            self._final_color = get_accent_color()
        else:
            self._final_color = self._color_cfg
        
        # Layout vertical para el contenido del splash
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Espaciador superior (para centrar verticalmente)
        self.main_layout.addStretch(1)
        
        # Logo
        self.logo_lbl = QLabel()
        if is_icon_file(self._logo):
            icon_obj = QIcon(self._logo)
            pixmap = icon_obj.pixmap(128, 128)
            if not pixmap.isNull():
                self.logo_lbl.setPixmap(pixmap)
            else:
                self.logo_lbl.setText(self._logo)
                self.logo_lbl.setFont(QFont("Segoe UI Variable Display", 80))
        else:
            self.logo_lbl.setText(self._logo)
            self.logo_lbl.setFont(QFont("Segoe UI Variable Display", 80))
        
        self.logo_lbl.setStyleSheet("color: white; background: transparent;")
        self.logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.logo_lbl)
        
        # Título y subtítulo (siempre mostrar en setup)
        self.status_lbl = QLabel(self._title)
        self.status_lbl.setStyleSheet("color: white; font-family: 'Segoe UI'; font-size: 18px; font-weight: 600; background: transparent;")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.status_lbl)

        if self._subtitle:
            self.subtitle_lbl = QLabel(self._subtitle)
            self.subtitle_lbl.setStyleSheet("color: rgba(255,255,255,0.7); font-family: 'Segoe UI'; font-size: 13px; background: transparent;")
            self.subtitle_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.main_layout.addWidget(self.subtitle_lbl)
        
        # Barra de progreso (opcional)
        if self._show_progress:
            from .progress_bar import LeviathanProgressBar
            self.pbar = LeviathanProgressBar()
            self.pbar.setFixedWidth(300)
            self.pbar.setFixedHeight(4)
            self.pbar.setMarquee(True)
            self.pbar_container = QWidget()
            pbar_layout = QVBoxLayout(self.pbar_container)
            pbar_layout.setContentsMargins(50, 0, 50, 0)
            pbar_layout.addWidget(self.pbar, alignment=Qt.AlignmentFlag.AlignCenter)
            self.main_layout.addWidget(self.pbar_container)
        
        # Espaciador inferior
        self.main_layout.addStretch(1)
        
        # Efecto de opacidad
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)  # Comienza completamente visible
        
        # Mostrar inmediatamente
        self.show()
        self.raise_()
        
        return self
    
    def finish_loading(self, delay_ms=1500):
        """Finaliza el splash con animación de fade out."""
        if not self._embedded_mode:
            return
            
        def do_fade_out():
            self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
            self.fade_out.setDuration(600)
            self.fade_out.setStartValue(1.0)
            self.fade_out.setEndValue(0.0)
            self.fade_out.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.fade_out.finished.connect(self._remove_splash)
            self.fade_out.start()
        
        QTimer.singleShot(delay_ms, do_fade_out)
    
    def _remove_splash(self):
        """Elimina el splash del layout y libera recursos."""
        self.hide()
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setParent(None)
        self.deleteLater()
        if self._callback:
            self._callback()
        
    def resizeEvent(self, event):
        """Ajustar tamaño cuando el contenedor cambia de tamaño"""
        super().resizeEvent(event)
        if self._embedded_mode and self.parent():
            self.setGeometry(self.parent().rect())

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self._embedded_mode:
            # Fondo sólido oscuro para modo APPX
            p.fillRect(self.rect(), QColor(self._final_color))
        else:
            if self._target_window:
                overlay_color = QColor(self._final_color)
                overlay_color.setAlpha(255)
                p.fillRect(self.rect(), overlay_color)
            else:
                p.fillRect(self.rect(), QColor(self._final_color))

    def attach_to_window(self, window, exit_phrases=None):
        """Asigna un cierre animado hacia abajo para la ventana target."""
        original_close_event = getattr(window, 'closeEvent', None)

        def animate_close():
            start_pos = window.pos()
            end_pos = QPoint(start_pos.x(), start_pos.y() + 48)

            anim_opacity = QPropertyAnimation(window, b'windowOpacity')
            anim_opacity.setDuration(320)
            anim_opacity.setStartValue(window.windowOpacity())
            anim_opacity.setEndValue(0.0)
            anim_opacity.setEasingCurve(QEasingCurve.Type.InQuad)

            anim_pos = QPropertyAnimation(window, b'pos')
            anim_pos.setDuration(320)
            anim_pos.setStartValue(start_pos)
            anim_pos.setEndValue(end_pos)
            anim_pos.setEasingCurve(QEasingCurve.Type.InQuad)

            group = QParallelAnimationGroup(window)
            group.addAnimation(anim_opacity)
            group.addAnimation(anim_pos)

            def on_finished():
                window._closing_animation_running = True
                window.close()

            group.finished.connect(on_finished)
            group.start(QParallelAnimationGroup.DeletionPolicy.DeleteWhenStopped)

        def on_close(event):
            if getattr(window, '_closing_animation_running', False):
                if original_close_event:
                    original_close_event(event)
                else:
                    event.accept()
                return
            event.ignore()
            window._closing_animation_running = False
            animate_close()

        window.closeEvent = on_close
        return self

    def start(self): return self.launch()
    @staticmethod
    def create(): return InmersiveSplash()
