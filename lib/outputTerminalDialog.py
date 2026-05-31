import os
try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QDialog, QWidget, QVBoxLayout, QLabel, QTextEdit
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

        # Area de texto de terminal
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setFont(QFont("Consolas", 10))
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

        # Barra estado inferior
        self.status_bar = QLabel("Iniciando...")
        self.status_bar.setStyleSheet("color: #8b949e; padding: 5px 10px; border-top: 1px solid #30363d; font-family: Segoe UI; font-size: 11px;")
        layout.addWidget(self.status_bar)

    def start_process(self):
        self.terminal_output.append(f"<span style='color: #8b949e;'>$ {self.interpreter} \"{self.script_path}\"</span><br>")
        self.status_bar.setText("Ejecutando script...")
        self.process.start(self.interpreter, [self.script_path])

        # Setup working directory to script dir
        self.process.setWorkingDirectory(os.path.dirname(self.script_path))

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode('utf-8', errors='replace')
        self.terminal_output.moveCursor(QtGui.QTextCursor.End)
        self.terminal_output.insertPlainText(data)
        self.terminal_output.moveCursor(QtGui.QTextCursor.End)

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode('utf-8', errors='replace')
        self.terminal_output.moveCursor(QtGui.QTextCursor.End)
        # Estilo rojo para errores
        self.terminal_output.insertHtml(f"<span style='color: #ff7b72;'>{data}</span>")
        self.terminal_output.moveCursor(QtGui.QTextCursor.End)

    def handle_finished(self, exit_code, exit_status):
        color = "#3fb950" if exit_code == 0 else "#ff7b72"
        msg = "Completado con éxito" if exit_code == 0 else f"Falló con código {exit_code}"
        self.terminal_output.append(f"<br><span style='color: {color}; font-weight:bold;'>Process finished: {msg}</span>")
        self.status_bar.setText(f"Estado: {msg}")