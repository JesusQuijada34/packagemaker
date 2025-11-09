import sys
import os
import json
import platform
import requests
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton,
    QPushButton, QGroupBox, QSizePolicy, QSpacerItem, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl, QTimer
from PyQt5.QtGui import QFont, QDesktopServices

# --- Configuración ---
# URL base para la verificación de actualizaciones. Esto debe apuntar a un archivo JSON
# que contenga la información de la última versión.
# Ejemplo de estructura del JSON remoto:
# {
#     "latest_version": "1.0.1",
#     "release_notes": "Corrección de errores y mejoras de rendimiento.",
#     "download_links": {
#         "source": "https://github.com/JesusQuijada34/packagemaker/archive/refs/tags/v1.0.1.zip",
#         "windows": "https://github.com/JesusQuijada34/packagemaker/releases/download/v1.0.1/packagemaker-win.zip",
#         "linux": "https://github.com/JesusQuijada34/packagemaker/releases/download/v1.0.1/packagemaker-linux.zip"
#     }
# }
UPDATE_CHECK_URL = "https://raw.githubusercontent.com/JesusQuijada34/packagemaker/main/update_info.json"
# Leer la versión actual de details.xml
def get_current_version():
    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse('details.xml')
        root = tree.getroot()
        return root.findtext('version', '0.0.0')
    except Exception:
        return "0.0.0"

CURRENT_VERSION = get_current_version()
APP_NAME = "Packagemaker"

# --- Lógica de Verificación de Actualización (Silenciosa) ---

class UpdateChecker(QThread):
    """Hilo para verificar actualizaciones en segundo plano."""
    update_available = pyqtSignal(dict)
    no_update = pyqtSignal()
    error = pyqtSignal(str)

    def run(self):
        try:
            response = requests.get(UPDATE_CHECK_URL, timeout=10)
            response.raise_for_status()
            update_info = response.json()

            latest_version = update_info.get("latest_version")
            if not latest_version:
                self.error.emit("Error: No se encontró 'latest_version' en la información de actualización.")
                return

            # Comparación simple de versiones (asumiendo formato X.Y.Z)
            def version_to_tuple(v):
                v = v.lstrip('v') # Eliminar prefijo 'v' si existe
                try:
                    return tuple(map(int, v.split('.')))
                except ValueError:
                    # Manejar versiones no estándar (ej. "beta", "rc")
                    print(f"Advertencia: Versión no estándar '{v}'. Usando 0.0.0 para comparación.")
                    return (0, 0, 0)

            if version_to_tuple(latest_version) > version_to_tuple(CURRENT_VERSION):
                self.update_available.emit(update_info)
            else:
                self.no_update.emit()

        except requests.exceptions.RequestException as e:
            self.error.emit(f"Error al verificar actualizaciones: {e}")
        except json.JSONDecodeError:
            self.error.emit("Error: La respuesta de actualización no es un JSON válido.")
        except Exception as e:
            self.error.emit(f"Error inesperado en la verificación: {e}")

# --- Interfaz de Usuario (Estilo GitHub) ---

class UpdateWindow(QWidget):
    """Ventana principal que se muestra solo si hay una actualización."""
    def __init__(self, update_info):
        super().__init__()
        self.update_info = update_info
        self.download_links = update_info.get("download_links", {})
        self.latest_version = update_info.get("latest_version", "Desconocida")
        self.release_notes = update_info.get("release_notes", "Notas de la versión no disponibles.")
        self.system_os = platform.system().lower()

        self.setWindowTitle(f"Actualización de {APP_NAME} Disponible")
        self.setFixedSize(550, 450)
        self.setWindowFlags(Qt.WindowStaysOnTopHint) # Mantener encima para asegurar visibilidad
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # 1. Encabezado (Estilo GitHub)
        header_label = QLabel(f"🎉 ¡Nueva versión de {APP_NAME} disponible!")
        header_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header_label.setStyleSheet("color: #24292e;")
        main_layout.addWidget(header_label)

        version_label = QLabel(f"Versión actual: {CURRENT_VERSION} → <b>{self.latest_version}</b>")
        version_label.setFont(QFont("Segoe UI", 12))
        version_label.setStyleSheet("color: #586069;")
        main_layout.addWidget(version_label)

        # 2. Notas de la Versión
        notes_group = QGroupBox("Notas de la Versión")
        notes_group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                margin-top: 10px; 
                border: 1px solid #e1e4e8; 
                border-radius: 6px; 
                padding-top: 15px; 
                background-color: #f6f8fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
            }
        """)
        notes_layout = QVBoxLayout(notes_group)
        notes_label = QLabel(self.release_notes)
        notes_label.setWordWrap(True)
        notes_label.setStyleSheet("color: #24292e; background-color: transparent;")
        notes_layout.addWidget(notes_label)
        main_layout.addWidget(notes_group)

        # 3. Opciones de Descarga (Radio Buttons)
        options_group = QGroupBox("Selecciona el tipo de descarga")
        options_group.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 10px; border: none; }")
        options_layout = QVBoxLayout(options_group)

        self.radio_source = QRadioButton("Código Fuente (Source Code)")
        self.radio_source.setFont(QFont("Segoe UI", 10))
        self.radio_source.setChecked(True)
        options_layout.addWidget(self.radio_source)

        os_name = "Windows" if "win" in self.system_os else "Linux" if "linux" in self.system_os else "Otro OS"
        self.radio_os = QRadioButton(f"Binario para {os_name} ({self.latest_version})")
        self.radio_os.setFont(QFont("Segoe UI", 10))
        options_layout.addWidget(self.radio_os)

        main_layout.addWidget(options_group)

        # Espaciador
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # 4. Botones de Acción
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignRight)

        # Botón de "Saltar"
        skip_button = QPushButton("Saltar por ahora")
        skip_button.setStyleSheet("""
            QPushButton {
                background-color: #f6f8fa;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                padding: 8px 16px;
                color: #24292e;
            }
            QPushButton:hover {
                background-color: #f3f4f6;
            }
        """)
        skip_button.clicked.connect(self.close)
        button_layout.addWidget(skip_button)

        # Botón de "Actualizar"
        update_button = QPushButton("Actualizar Ahora")
        update_button.setFont(QFont("Segoe UI", 10, QFont.Bold))
        update_button.setStyleSheet("""
            QPushButton {
                background-color: #2ea44f;
                border: 1px solid #2ea44f;
                border-radius: 6px;
                padding: 8px 16px;
                color: white;
            }
            QPushButton:hover {
                background-color: #2c974b;
            }
        """)
        update_button.clicked.connect(self.start_download)
        button_layout.addWidget(update_button)

        main_layout.addLayout(button_layout)

    def start_download(self):
        """Determina el enlace de descarga y lo abre en el navegador (simulación)."""
        download_url = None
        download_type = "source"

        if self.radio_source.isChecked():
            download_url = self.download_links.get("source")
            download_type = "source"
        elif self.radio_os.isChecked():
            if "win" in self.system_os:
                download_url = self.download_links.get("windows")
                download_type = "windows"
            elif "linux" in self.system_os:
                download_url = self.download_links.get("linux")
                download_type = "linux"

        if download_url:
            QMessageBox.information(self, "Iniciando Descarga", 
                                    f"Se iniciará la descarga de la versión {self.latest_version} ({download_type}).\n\n"
                                    f"URL: {download_url}\n\n"
                                    "En un entorno real, la descarga y aplicación se realizaría aquí, seguido del reinicio del actualizador.")
            
            # SIMULACIÓN: Abrir el enlace en el navegador y simular el proceso de actualización
            QDesktopServices.openUrl(QUrl(download_url))
            
            # SIMULACIÓN: Establecer variable de entorno para el reinicio
            os.environ["PACKAGEMAKER_UPDATED"] = "true"
            
            # Cerrar la ventana y salir para simular el reinicio del actualizador
            self.close()
            QApplication.quit()
            
        else:
            QMessageBox.warning(self, "Error de Descarga", 
                                "No se encontró un enlace de descarga válido para la selección. Por favor, inténtalo de nuevo o selecciona el código fuente.")

# --- Lógica Principal de Ejecución ---

def check_system_updates_background():
    """Simulación de la verificación de actualizaciones del sistema en segundo plano."""
    print("--- INICIANDO VERIFICACIÓN DE ACTUALIZACIONES DEL SISTEMA EN SEGUNDO PLANO ---")
    
    # En un entorno real, esto podría ser un proceso separado o un servicio.
    # Aquí, simplemente simulamos la ejecución de un comando de actualización del sistema.
    
    if platform.system().lower() == "linux":
        # Simulación de un comando de actualización de Linux
        print("Ejecutando simulación de 'sudo apt update && sudo apt upgrade -y'...")
        # subprocess.Popen(["sudo", "apt", "update", "-y"]) # No ejecutar en el sandbox
    elif platform.system().lower() == "windows":
        # Simulación de un comando de actualización de Windows (ej. PowerShell)
        print("Ejecutando simulación de 'Windows Update'...")
    
    print("La verificación de actualizaciones del sistema se está ejecutando en segundo plano.")
    print("-----------------------------------------------------------------------------")

def main():
    """Función principal para ejecutar el actualizador."""
    
    # 1. Lógica de reinicio para la verificación de actualizaciones del sistema
    if os.environ.get("PACKAGEMAKER_UPDATED") == "true":
        # Limpiar la variable de entorno inmediatamente
        del os.environ["PACKAGEMAKER_UPDATED"]
        
        # Iniciar la verificación de actualizaciones del sistema y salir
        check_system_updates_background()
        sys.exit(0)

    # 2. Lógica de verificación de actualización de la aplicación
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False) # No salir automáticamente

    # Iniciar la verificación de actualización en un hilo
    checker = UpdateChecker()

    def on_update_available(update_info):
        """Muestra la ventana si hay una actualización."""
        checker.quit()
        print(f"Actualización disponible: {update_info['latest_version']}. Mostrando interfaz.")
        global update_window
        update_window = UpdateWindow(update_info)
        update_window.show()

    def on_no_update():
        """Sale silenciosamente si no hay actualización."""
        checker.quit()
        print("No hay actualizaciones disponibles. Saliendo silenciosamente.")
        QApplication.quit()

    def on_error(message):
        """Sale silenciosamente en caso de error."""
        checker.quit()
        print(f"Error silencioso en la verificación: {message}")
        QApplication.quit()

    checker.update_available.connect(on_update_available)
    checker.no_update.connect(on_no_update)
    checker.error.connect(on_error)

    checker.start()

    # Usar un QTimer para asegurar que la aplicación no se cierre inmediatamente
    # si el hilo tarda un poco en terminar.
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(100)

    sys.exit(app.exec_())

if __name__ == "__main__":
    # Asegurarse de que el directorio actual sea el del proyecto para leer details.xml
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir("..") # Moverse al directorio packagemaker
    
    # Crear un archivo details.xml de prueba si no existe para la simulación
    if not os.path.exists('details.xml'):
        with open('details.xml', 'w') as f:
            f.write('<app><version>1.0.0</version><shortName>packagemaker</shortName></app>')
            
    # Crear un archivo update_info.json de prueba para la simulación
    if not os.path.exists('update_info.json'):
        with open('update_info.json', 'w') as f:
            json.dump({
                "latest_version": "1.0.1",
                "release_notes": "Se ha mejorado la interfaz de usuario y se corrigieron errores menores.",
                "download_links": {
                    "source": "https://github.com/JesusQuijada34/packagemaker/archive/refs/tags/v1.0.1.zip",
                    "windows": "https://github.com/JesusQuijada34/packagemaker/releases/download/v1.0.1/packagemaker-win.zip",
                    "linux": "https://github.com/JesusQuijada34/packagemaker/releases/download/v1.0.1/packagemaker-linux.zip"
                }
            }, f, indent=4)
            
    # La URL de verificación apunta a un archivo remoto, pero para la prueba inicial
    # usaremos el archivo local. En un entorno real, el archivo remoto es necesario.
    # Para simular la verificación remota, crearemos un archivo de prueba en el directorio raíz
    # y lo usaremos como URL de verificación.
    
    # Nota: En el código final, la URL remota real debe ser usada.
    # Para esta simulación, el código usa la URL remota, asumiendo que existe.
    
    main()
