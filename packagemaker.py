# -*- coding: utf-8 -*-
# Packagemaker - Herramienta para crear paquetes .iflapp (Normales)
# Versión GUI "Todo en Uno"

import sys
import os
import time
import hashlib
import shutil
import zipfile
import xml.etree.ElementTree as ET
import subprocess
import socket # Para detección de conexión
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QListWidget, QListWidgetItem, QFileDialog, QDialog, QStyle, QSizePolicy, QSplitter, QGroupBox, QMessageBox, QGridLayout
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# ----------- CONFIGURABLE VARIABLES -----------
APP_TITLE = "Influent Package Maker (.iflapp) - Todo en Uno"
APP_FONT = QFont('Roboto', 13)
TAB_FONT = QFont('Roboto', 12)
BUTTON_FONT = QFont('Arial', 12, QFont.Bold)
TAB_ICONS = {
    "crear": "./app/package_add.ico",
    "construir": "./app/package_build.ico",
    "gestor": "./app/package_fm.ico",
    "ayuda": "./app/package_about.ico",
}
# ESTILOS: Se mantienen los estilos visuales
BTN_STYLES = {
    "default": "background-color: #29b6f6;color: #000000;border-radius:5px;padding:10px 18px;font-weight:bold;border: 1px solid #45addc;",
    "success": "background-color: #43a047;color: #000000;border-radius:5px;padding:10px 18px;font-weight:bold;border: 1px solid #22863a;",
    "danger":  "background-color: #c62828;color: #000000;border-radius:5px;padding:10px 18px;font-weight:bold;border: 1px solid #B52222;",
    "warning": "background-color: #ffd54f;color: #212121;border-radius:5px;padding:10px 18px;font-weight:bold;border: 1px solid #E6BD3A;",
    "info":    "background-color: #5c6bc0;color: #000000;border-radius:5px;padding:10px 18px;font-weight:bold;border: 1px solid #3A4DB9;",
}

# Rutas base (Se mantiene la lógica multiplataforma de rutas)
plataforma_platform = sys.platform
if plataforma_platform.startswith("win"):
    BASE_DIR = os.path.join(os.environ["USERPROFILE"], "My Documents", "Influent Packages")
    FLATR_APPS = os.path.join(os.environ["USERPROFILE"], "My Documents", "Flatr Apps")
else:
    BASE_DIR = os.path.expanduser("~/Documentos/Influent Packages")
    FLATR_APPS = os.path.expanduser("~/Documentos/Flatr Apps")

IPM_ICON_PATH = "app/app-icon.ico"
DEFAULT_FOLDERS = "app,assets,config,docs,source,lib"
PACKAGE_EXT = ".iflapp"

# Clasificación por edad (simplificada)
AGE_RATINGS = {
    "adult": "ADULTS ONLY",
    "kids": "FOR KIDS",
    "social": "PUBLIC CONTENT",
    "ai": "PUBLIC ALL",
    "default": "EVERYONE"
}

# --- Utilidades ---

def check_internet_connection(host="8.8.8.8", port=53, timeout=3):
    """Verifica si hay conexión a Internet."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

def install_dependencies(requirements_file):
    """Instala dependencias si hay conexión a Internet."""
    if not os.path.exists(requirements_file):
        return True # No hay dependencias que instalar

    if check_internet_connection():
        # Intenta instalar con pip
        try:
            print(f"Conexión a Internet detectada. Instalando dependencias desde {requirements_file}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
            return True
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(None, "Error de Instalación", f"Fallo al instalar dependencias: {e}")
            return False
    else:
        QMessageBox.warning(None, "Sin Conexión", "No se detectó conexión a Internet. Usando versiones fallback (si existen).")
        return True

def getversion_stamp():
    return time.strftime("%y.%m-%H.%M")

def get_age_rating(name, title):
    search_string = (name + title).lower()
    for keyword, rate in AGE_RATINGS.items():
        if keyword in search_string:
            return rate
    return AGE_RATINGS["default"]

def create_details_xml(path, empresa, nombre_logico, nombre_completo, version):
    newversion = getversion_stamp()
    empresa = empresa.capitalize()
    full_name = f"{empresa}.{nombre_logico}.v{version}"
    hash_val = hashlib.sha256(full_name.encode()).hexdigest()
    rating = get_age_rating(nombre_logico, nombre_completo)

    root = ET.Element("app")
    ET.SubElement(root, "publisher").text = empresa
    ET.SubElement(root, "app").text = nombre_logico
    ET.SubElement(root, "name").text = nombre_completo
    ET.SubElement(root, "version").text = f"v{version}"
    ET.SubElement(root, "platform").text = sys.platform
    ET.SubElement(root, "danenone").text = newversion
    ET.SubElement(root, "correlationid").text = hash_val
    ET.SubElement(root, "rate").text = rating

    tree = ET.ElementTree(root)
    tree.write(os.path.join(path, "details.xml"), encoding="utf-8", xml_declaration=True)

def create_package_structure(full_path, empresa, nombre_logico, nombre_completo, version):
    """Crea la estructura de carpetas y archivos iniciales para un paquete .iflapp."""
    for folder in DEFAULT_FOLDERS.split(","):
        os.makedirs(os.path.join(full_path, folder.strip()), exist_ok=True)
        
    # Archivo principal .py
    main_script = os.path.join(full_path, f"{nombre_logico}.py")
    with open(main_script, "w") as f:
        f.write("# -*- coding: utf-8 -*-\n")
        f.write(f"# Script principal para el paquete {nombre_logico}\n")
        f.write("import sys\n")
        f.write("from PyQt5.QtWidgets import QApplication, QLabel\n")
        f.write("\n")
        f.write("app = QApplication(sys.argv)\n")
        f.write(f"label = QLabel('¡Hola desde {nombre_logico}! Paquete .iflapp creado con éxito.')\n")
        f.write("label.show()\n")
        f.write("sys.exit(app.exec_())\n")

    # Archivo README.md
    with open(os.path.join(full_path, "README.md"), "w") as f:
        f.write(f"# Paquete: {nombre_completo}\n\n")
        f.write(f"Creado por: {empresa}\n")
        f.write(f"Versión: v{version}\n\n")
        f.write("Este es un paquete modular .iflapp de Influent Package Maker.\n")

    # Archivo requirements.txt
    with open(os.path.join(full_path, "lib", "requirements.txt"), "w") as f:
        f.write("PyQt5\n") # Dependencia base

    create_details_xml(full_path, empresa, nombre_logico, nombre_completo, version)

# --- Clase Principal de la Aplicación (GUI) ---
class PackagemakerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setWindowIcon(QIcon(IPM_ICON_PATH))
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #212121; color: #ffffff;")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.tabs = QTabWidget()
        self.tabs.setFont(TAB_FONT)
        self.tabs.setStyleSheet("QTabWidget::pane { border: 0; } QTabBar::tab { background: #333333; color: #ffffff; padding: 10px; } QTabBar::tab:selected { background: #424242; }")
        self.main_layout.addWidget(self.tabs)

        self.create_tab = self.create_creation_tab()
        self.build_tab = self.create_build_tab()
        self.manager_tab = self.create_manager_tab()
        self.help_tab = self.create_help_tab()
        
        self.tabs.addTab(self.create_tab, QIcon(TAB_ICONS["crear"]), "Crear Paquete")
        self.tabs.addTab(self.build_tab, QIcon(TAB_ICONS["construir"]), "Construir")
        self.tabs.addTab(self.manager_tab, QIcon(TAB_ICONS["gestor"]), "Gestor de Proyectos")
        self.tabs.addTab(self.help_tab, QIcon(TAB_ICONS["ayuda"]), "Ayuda")
        
        # Estado de conexión
        self.status_bar = self.statusBar()
        self.connection_status = QLabel("Verificando conexión...")
        self.status_bar.addWidget(self.connection_status)
        self.check_connection_status()

    def check_connection_status(self):
        if check_internet_connection():
            self.connection_status.setText("Conexión: ONLINE")
            self.connection_status.setStyleSheet("color: #43a047;")
        else:
            self.connection_status.setText("Conexión: OFFLINE (Usando Fallback)")
            self.connection_status.setStyleSheet("color: #ffd54f;")

    def create_creation_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Inputs
        input_group = QGroupBox("Metadatos del Paquete")
        input_layout = QGridLayout()
        
        self.empresa_input = QLineEdit("MiEmpresa")
        self.nombre_logico_input = QLineEdit("MiApp")
        self.nombre_completo_input = QLineEdit("Mi Aplicación de Ejemplo")
        self.version_input = QLineEdit("1.0.0")
        
        input_layout.addWidget(QLabel("Empresa (Publisher):"), 0, 0)
        input_layout.addWidget(self.empresa_input, 0, 1)
        input_layout.addWidget(QLabel("Nombre Lógico (Script):"), 1, 0)
        input_layout.addWidget(self.nombre_logico_input, 1, 1)
        input_layout.addWidget(QLabel("Nombre Completo (Título):"), 2, 0)
        input_layout.addWidget(self.nombre_completo_input, 2, 1)
        input_layout.addWidget(QLabel("Versión:"), 3, 0)
        input_layout.addWidget(self.version_input, 3, 1)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Botón de Creación
        create_btn = QPushButton("Crear Estructura de Proyecto")
        create_btn.setFont(BUTTON_FONT)
        create_btn.setStyleSheet(BTN_STYLES["default"])
        create_btn.clicked.connect(self.create_project)
        layout.addWidget(create_btn)
        
        layout.addStretch()
        return tab

    def create_build_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Lógica de Construcción (Simulación)
        layout.addWidget(QLabel("Funcionalidad de Construcción: Seleccione un proyecto de la pestaña 'Gestor de Proyectos' para construirlo en formato .iflapp."))
        layout.addStretch()
        return tab

    def create_manager_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Lógica de Gestor (Simulación)
        layout.addWidget(QLabel("Gestor de Proyectos: Muestra y permite la gestión de proyectos en el directorio 'Influent Packages'."))
        layout.addStretch()
        return tab

    def create_help_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Lógica de Ayuda
        layout.addWidget(QLabel("Ayuda y Documentación: Herramienta modular todo-en-uno para crear, empaquetar y gestionar proyectos Influent (.iflapp)."))
        layout.addStretch()
        return tab

    def create_project(self):
        empresa = self.empresa_input.text()
        nombre_logico = self.nombre_logico_input.text()
        nombre_completo = self.nombre_completo_input.text()
        version = self.version_input.text()
        
        if not (empresa and nombre_logico and nombre_completo and version):
            QMessageBox.warning(self, "Datos Incompletos", "Por favor, complete todos los campos.")
            return

        project_dir = os.path.join(BASE_DIR, nombre_logico)
        
        if os.path.exists(project_dir):
            reply = QMessageBox.question(self, 'Proyecto Existente',
                f"El proyecto '{nombre_logico}' ya existe. ¿Desea sobrescribirlo?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.No:
                return
            shutil.rmtree(project_dir)

        try:
            os.makedirs(project_dir, exist_ok=True)
            create_package_structure(project_dir, empresa, nombre_logico, nombre_completo, version)
            QMessageBox.information(self, "Éxito", f"Estructura del proyecto '{nombre_logico}' creada en:\n{project_dir}")
        except Exception as e:
            QMessageBox.critical(self, "Error de Creación", f"Fallo al crear el proyecto: {e}")

# --- Ejecución ---
if __name__ == '__main__':
    # Aseguramos que la carpeta de iconos exista para que la GUI no falle
    os.makedirs("app", exist_ok=True)
    if not os.path.exists(IPM_ICON_PATH):
        # Crear un placeholder si el icono no existe
        icon_placeholder = QtGui.QPixmap(32, 32)
        icon_placeholder.fill(QtGui.QColor("#29b6f6"))
        icon_placeholder.save(IPM_ICON_PATH)

    app = QApplication(sys.argv)
    ex = PackagemakerApp()
    ex.show()
    sys.exit(app.exec_())

