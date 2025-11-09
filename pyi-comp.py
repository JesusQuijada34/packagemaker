import sys, os, subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QLineEdit, QTextEdit, QCheckBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class PyInstallerCompiler(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Compilador Embestido de Python")
        self.setFixedSize(600, 500)
        self.setStyleSheet("background-color: #0d1117; color: #2ecc71;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Compilador Embestido con PyInstaller")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Ruta del script
        self.script_path = QLineEdit()
        self.script_path.setPlaceholderText("Selecciona tu archivo .py")
        layout.addWidget(self.script_path)

        browse_btn = QPushButton("📂 Buscar script")
        browse_btn.clicked.connect(self.buscar_script)
        layout.addWidget(browse_btn)

        # Nombre del ejecutable
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nombre del ejecutable (opcional)")
        layout.addWidget(self.name_input)

        # Ícono
        self.icon_input = QLineEdit()
        self.icon_input.setPlaceholderText("Ruta del ícono .ico (opcional)")
        layout.addWidget(self.icon_input)

        # Carpeta de salida
        self.output_input = QLineEdit()
        self.output_input.setPlaceholderText("Carpeta de salida (opcional)")
        layout.addWidget(self.output_input)

        # Opciones
        self.onefile_cb = QCheckBox("Generar como --onefile")
        self.windowed_cb = QCheckBox("Modo ventana (--windowed)")
        layout.addWidget(self.onefile_cb)
        layout.addWidget(self.windowed_cb)

        # Botón compilar
        compile_btn = QPushButton("🚀 Compilar")
        compile_btn.clicked.connect(self.compilar)
        layout.addWidget(compile_btn)

        # Comando generado
        self.command_display = QTextEdit()
        self.command_display.setReadOnly(True)
        self.command_display.setPlaceholderText("Aquí verás el comando generado y la salida")
        layout.addWidget(self.command_display)

        self.setLayout(layout)

    def buscar_script(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecciona script", "", "Python (*.py)")
        if path:
            self.script_path.setText(path)

    def compilar(self):
        script = self.script_path.text().strip()
        if not script or not os.path.exists(script):
            self.command_display.setText("❌ Script no válido.")
            return

        cmd = ["pyinstaller"]

        if self.onefile_cb.isChecked():
            cmd.append("--onefile")
        if self.windowed_cb.isChecked():
            cmd.append("--windowed")

        name = self.name_input.text().strip()
        if name:
            cmd += ["--name", name]

        icon = self.icon_input.text().strip()
        if icon and os.path.exists(icon):
            cmd += ["--icon", icon]

        output = self.output_input.text().strip()
        if output:
            cmd += ["--distpath", output]

        cmd.append(script)

        self.command_display.setText("🧠 Comando generado:\n" + " ".join(cmd) + "\n\n⏳ Compilando…")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            output = result.stdout + "\n" + result.stderr
            self.command_display.append("✅ Resultado:\n" + output)
        except Exception as e:
            self.command_display.append(f"❌ Error: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = PyInstallerCompiler()
    ventana.show()
    sys.exit(app.exec_())
