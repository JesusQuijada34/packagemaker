import os
try:
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtWidgets import QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QProgressBar
    from PyQt6.QtGui import QFont
    from PyQt6 import QtGui
    from PyQt6.QtCore import QProcess
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    class QDialog:
        def __init__(self, *args, **kwargs): pass
from lib.TitleBar import TitleBar


class OutputTerminalDialog(QDialog):
    """Dialogo de terminal para mostrar salida de scripts"""
    def __init__(self, script_path, interpreter, parent=None):
        super().__init__(parent)
        self.script_path = script_path
        self.interpreter = interpreter
        self.interpreter = interpreter
        self.is_running_in_background = False
        self.last_line = ""
        # Fix: Ensure Qt.WindowType.Dialog flag is present so self.window() in TitleBar returns THIS dialog, not the parent main window
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(900, 600)
        self.init_ui()
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        self.start_process()

    def init_ui(self):
        # Fondo y borde
        self.container = QWidget(self)
        self.container.setObjectName("TerminalContainer")
        self.container.setStyleSheet("""
            #TerminalContainer {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 8px;
            }
        """)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.container)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Barra de titulo
        self.titlebar = TitleBar(self, title=f"Terminal: {os.path.basename(self.script_path)}")
        self.titlebar.setStyleSheet("background-color: #161b22; border-top-left-radius: 8px; border-top-right-radius: 8px;")
        layout.addWidget(self.titlebar)

        # Area de texto de terminal (solo última línea)
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setFont(QFont("Consolas", 10))
        self.terminal_output.setMaximumHeight(100)
        self.terminal_output.setStyleSheet("""
            QTextEdit {
                background-color: #0d1117;
                color: #c9d1d9;
                border: none;
                padding: 10px;
                selection-background-color: #58a6ff;
                selection-color: #0d1117;
            }
        """)
        layout.addWidget(self.terminal_output)

        # Barra de progreso marquee
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Modo indeterminado (marquee)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 4px;
                height: 8px;
            }
            QProgressBar::chunk {
                background-color: #58a6ff;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Botones de control
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        buttons_layout.setContentsMargins(10, 10, 10, 10)

        # Botón ocultar/segundo plano
        self.btn_background = QPushButton("Ocultar (Segundo plano)")
        self.btn_background.setStyleSheet("""
            QPushButton {
                background-color: #238636;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2ea043;
            }
            QPushButton:pressed {
                background-color: #1f7a2e;
            }
        """)
        self.btn_background.clicked.connect(self._on_background_mode)
        buttons_layout.addWidget(self.btn_background)

        # Botón detener
        self.btn_stop = QPushButton("Detener")
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background-color: #da3633;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #f85149;
            }
            QPushButton:pressed {
                background-color: #b62324;
            }
        """)
        self.btn_stop.clicked.connect(self._on_stop)
        buttons_layout.addWidget(self.btn_stop)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        # Barra estado inferior
        self.status_bar = QLabel("Iniciando...")
        self.status_bar.setStyleSheet("color: #8b949e; padding: 5px 10px; border-top: 1px solid #30363d; font-family: Segoe UI; font-size: 11px;")
        layout.addWidget(self.status_bar)

        # Timer para verificar estado en segundo plano
        self.background_check_timer = QTimer()
        self.background_check_timer.timeout.connect(self._check_background_status)
        self.background_check_timer.setInterval(1000)  # Verificar cada segundo

    def start_process(self):
        self.terminal_output.append(f"<span style='color: #8b949e;'>$ {self.interpreter} \"{self.script_path}\"</span><br>")
        self.status_bar.setText("Ejecutando script...")
        self.process.start(self.interpreter, [self.script_path])

        # Setup working directory to script dir
        self.process.setWorkingDirectory(os.path.dirname(self.script_path))

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode('utf-8', errors='replace')
        # Mostrar solo la última línea
        lines = data.split('\n')
        for line in lines:
            if line.strip():
                self.last_line = line
                self.terminal_output.clear()
                self.terminal_output.append(f"<span style='color: #c9d1d9;'>{line}</span>")
        self.terminal_output.moveCursor(QtGui.QTextCursor.End)

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode('utf-8', errors='replace')
        # Mostrar solo la última línea de error
        lines = data.split('\n')
        for line in lines:
            if line.strip():
                self.last_line = line
                self.terminal_output.clear()
                self.terminal_output.append(f"<span style='color: #ff7b72;'>{line}</span>")
        self.terminal_output.moveCursor(QtGui.QTextCursor.End)

    def handle_finished(self, exit_code, exit_status):
        color = "#3fb950" if exit_code == 0 else "#ff7b72"
        msg = "Completado con éxito" if exit_code == 0 else f"Falló con código {exit_code}"
        self.terminal_output.clear()
        self.terminal_output.append(f"<span style='color: {color}; font-weight:bold;'>Process finished: {msg}</span>")
        self.status_bar.setText(f"Estado: {msg}")
        self.progress_bar.setVisible(False)
        
        # Si está en segundo plano, mostrar messagebox
        if self.is_running_in_background:
            self._show_completion_message(exit_code == 0, msg)
            self.is_running_in_background = False
            self.background_check_timer.stop()

    def _on_background_mode(self):
        """Oculta el diálogo y ejecuta en segundo plano."""
        self.is_running_in_background = True
        self.hide()
        self.background_check_timer.start()
        self.status_bar.setText("Ejecutando en segundo plano...")

    def _on_stop(self):
        """Detiene el proceso."""
        if self.process.state() == QProcess.ProcessState.Running:
            self.process.kill()
            self.status_bar.setText("Proceso detenido")
            self.progress_bar.setVisible(False)
            self.terminal_output.clear()
            self.terminal_output.append("<span style='color: #ff7b72; font-weight:bold;'>Proceso detenido por el usuario</span>")
            
            if self.is_running_in_background:
                self._show_completion_message(False, "Proceso detenido")
                self.is_running_in_background = False
                self.background_check_timer.stop()

    def _check_background_status(self):
        """Verifica el estado del proceso en segundo plano."""
        if self.process.state() == QProcess.ProcessState.NotRunning:
            # El proceso ha terminado
            self.background_check_timer.stop()
            # El handler_finished ya manejará la notificación

    def _show_completion_message(self, success: bool, message: str):
        """Muestra un messagebox cuando el proceso termina en segundo plano."""
        try:
            from PyQt6.QtWidgets import QMessageBox
            if success:
                QMessageBox.information(
                    None,
                    "Compilación Completada",
                    f"El proceso ha terminado exitosamente:\n{message}"
                )
            else:
                QMessageBox.warning(
                    None,
                    "Error en Compilación",
                    f"El proceso ha terminado con errores:\n{message}"
                )
        except ImportError:
            pass