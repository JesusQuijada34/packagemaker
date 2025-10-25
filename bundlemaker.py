#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Bundlemaker - Herramienta para crear paquetes .iflappb (Bundles)
# Versión GUI "Todo en Uno"

import sys
import os
import time
import json
import shutil
import zipfile
import hashlib
import xml.etree.ElementTree as ET
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QListWidget, QListWidgetItem, QFileDialog, QDialog, QStyle, QSizePolicy, QSplitter, QGroupBox, QMessageBox, QGridLayout
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# ----------- CONFIGURACIÓN DE ESTILO AZUL -----------
APP_TITLE = "Influent Bundle Maker (.iflappb) - Todo en Uno"
APP_FONT = QFont('Roboto', 13)
TAB_FONT = QFont('Roboto', 12)
BUTTON_FONT = QFont('Arial', 12, QFont.Bold)
TAB_ICONS = {
    "crear": "./app/package_add.ico",
    "construir": "./app/package_build.ico",
    "gestor": "./app/package_fm.ico",
    "ayuda": "./app/package_about.ico",
}
# Tema Azul (Réplica de Packagemaker, pero con acentos azules)
BTN_STYLES = {
    "default": "background-color: #45a0ff;color: #000000;border-radius:5px;padding:10px 18px;font-weight:bold;border: 1px solid #3a8ee6;",
    "success": "background-color: #00bfff;color: #000000;border-radius:5px;padding:10px 18px;font-weight:bold;border: 1px solid #0099cc;",
    "danger":  "background-color: #c62828;color: #000000;border-radius:5px;padding:10px 18px;font-weight:bold;border: 1px solid #B52222;",
    "warning": "background-color: #ffd54f;color: #212121;border-radius:5px;padding:10px 18px;font-weight:bold;border: 1px solid #E6BD3A;",
    "info":    "background-color: #5c6bc0;color: #000000;border-radius:5px;padding:10px 18px;font-weight:bold;border: 1px solid #3A4DB9;",
}

# Rutas base
plataforma_platform = sys.platform
if plataforma_platform.startswith("win"):
    BASE_DIR = os.path.join(os.environ["USERPROFILE"], "My Documents", "Influent Bundles") # Directorio diferente
    FLATR_APPS = os.path.join(os.environ["USERPROFILE"], "My Documents", "Flatr Apps")
else:
    BASE_DIR = os.path.expanduser("~/Documentos/Influent Bundles") # Directorio diferente
    FLATR_APPS = os.path.expanduser("~/Documentos/Flatr Apps")

IPM_ICON_PATH = "app/package_build.ico" # Usar un ícono diferente o el mismo
BUNDLE_FOLDERS = ["res", "data", "code", "manifest", "activity", "theme", "blob", "bundle"] # Añadida carpeta 'bundle'
BUNDLE_EXT = ".iflappb"

# --- Utilidades de Bundle ---

def getversion_stamp():
    return time.strftime("%y.%m-%H.%M")

def create_bundle_details_xml(path, empresa, nombre_logico, nombre_completo, version):
    """Crea el archivo details.xml para el bundle."""
    newversion = getversion_stamp()
    empresa = empresa.capitalize()
    
    root = ET.Element("bundle")
    ET.SubElement(root, "publisher").text = empresa
    ET.SubElement(root, "name").text = nombre_logico
    ET.SubElement(root, "title").text = nombre_completo
    ET.SubElement(root, "version").text = f"v{version}"
    ET.SubElement(root, "platform").text = sys.platform
    ET.SubElement(root, "core").text = "knosthalij" # Núcleo diferente para Bundles
    ET.SubElement(root, "date").text = newversion
    
    tree = ET.ElementTree(root)
    tree.write(os.path.join(path, "details.xml"), encoding="utf-8", xml_declaration=True)

def create_bundle_manifest_json(path, nombre_logico, version):
    """Crea el archivo manifest.json para el bundle."""
    manifest_data = {
        "bundleName": nombre_logico,
        "version": version,
        "activities": [
            {"id": "main", "entryPoint": "code/main.py", "type": "python"},
            {"id": "settings", "entryPoint": "activity/settings.xml", "type": "xml"}
        ],
        "permissions": ["network", "storage"],
        "theme": "theme/default.css"
    }
    manifest_path = os.path.join(path, "manifest/manifest.json")
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    with open(manifest_path, "w") as f:
        json.dump(manifest_data, f, indent=4)

def create_bundle_manifest_xml(path, nombre_logico):
    """Crea el archivo bundleManifest.xml para la asociación de archivos y ejecutables."""
    root = ET.Element("bundleManifest")
    ET.SubElement(root, "comment").text = "Este archivo define los ejecutables dentro del Bundle para el Launcher."
    
    # Ejecutable principal de ejemplo
    main_exe = ET.SubElement(root, "executable")
    ET.SubElement(main_exe, "name").text = "Lanzador Principal"
    ET.SubElement(main_exe, "path").text = "code/main.py"
    ET.SubElement(main_exe, "icon").text = f"{nombre_logico}.ico" # Icono específico
    ET.SubElement(main_exe, "command").text = "%PYTHON_EXE% %SCRIPT_PATH% %1"
    
    # Segundo ejecutable de ejemplo (ej. una herramienta de configuración)
    config_exe = ET.SubElement(root, "executable")
    ET.SubElement(config_exe, "name").text = "Herramienta de Configuración"
    ET.SubElement(config_exe, "path").text = "code/config_tool.py"
    ET.SubElement(config_exe, "icon").text = "config_tool.ico"
    ET.SubElement(config_exe, "command").text = "%PYTHON_EXE% %SCRIPT_PATH%"
    
    tree = ET.ElementTree(root)
    tree.write(os.path.join(path, "bundleManifest.xml"), encoding="utf-8", xml_declaration=True)

def create_bundle_structure(full_path, empresa, nombre_logico, version):
    """Crea la estructura de carpetas y archivos iniciales para un bundle .iflappb."""
    for folder in BUNDLE_FOLDERS:
        os.makedirs(os.path.join(full_path, folder.strip()), exist_ok=True)
    
    # Archivos específicos de Bundle
    create_bundle_details_xml(full_path, empresa, nombre_logico, nombre_logico, version)
    create_bundle_manifest_json(full_path, nombre_logico, version)
    create_bundle_manifest_xml(full_path, nombre_logico) # Nuevo manifiesto XML
    
    # Script de ejemplo
    main_script = os.path.join(full_path, "code/main.py")
    os.makedirs(os.path.dirname(main_script), exist_ok=True)
    with open(main_script, "w") as f:
        f.write(f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Bundle {empresa}.{nombre_logico}.v{version}
# Creado con Influent Bundle Maker (.iflappb)

print("¡El Bundle {nombre_logico} ha sido inicializado!")
# La lógica del bundle se basa en el manifiesto y las actividades.
""")
    # Script de configuración de ejemplo
    config_script = os.path.join(full_path, "code/config_tool.py")
    with open(config_script, "w") as f:
        f.write(f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Herramienta de configuración para {nombre_logico}

print("Herramienta de configuración iniciada.")
# Agregue su lógica de configuración aquí.
""")

    # Icono de ejemplo para el bundle
    # Usamos un placeholder, el usuario debe reemplazarlo con un .ico real
    os.makedirs(os.path.join(full_path, "bundle"), exist_ok=True)
    with open(os.path.join(full_path, "bundle", f"{nombre_logico}.ico"), "w") as f:
        f.write("ICON_PLACEHOLDER")
    with open(os.path.join(full_path, "bundle", "config_tool.ico"), "w") as f:
        f.write("ICON_PLACEHOLDER")

# --- QThread para Construcción (solo .iflappb) ---

class BuildThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    def __init__(self, project_path, output_path, parent=None):
        super().__init__(parent)
        self.project_path = project_path
        self.output_path = output_path
        
    def run(self):
        project_name = os.path.basename(self.project_path)
        output_file = os.path.join(self.output_path, project_name + BUNDLE_EXT)
        zip_path = output_file.replace(BUNDLE_EXT, "") + ".zip"
        
        if not os.path.exists(self.project_path):
            self.error.emit("No se encontró la carpeta del Bundle.")
            return
            
        try:
            file_list = []
            for root, _, files in os.walk(self.project_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, self.project_path)
                    file_list.append((full_path, arcname))
                    
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for i, (full_path, arcname) in enumerate(file_list):
                    zipf.write(full_path, arcname)
                    self.progress.emit(f"Empaquetando archivo {i+1}/{len(file_list)}: {arcname}")
                    
            os.rename(zip_path, output_file)
            shutil.rmtree(self.project_path) # Eliminar carpeta temporal después de empaquetar
            self.finished.emit(f"Bundle construido: {output_file}")
            
        except Exception as e:
            self.error.emit(f"Error al construir: {str(e)}")

# --- Interfaz Gráfica (PyQt5) ---

class BundleMakerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1000, 650)
        self.setFont(APP_FONT)
        self.setWindowIcon(QIcon(IPM_ICON_PATH) if os.path.exists(IPM_ICON_PATH) else QIcon())
        self.statusBar().showMessage("Listo para crear Bundles .iflappb")
        
        # Asegurar directorios
        os.makedirs(BASE_DIR, exist_ok=True)
        os.makedirs(FLATR_APPS, exist_ok=True)

        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.layout = QVBoxLayout(self.central)
        
        self.tabs = QTabWidget()
        self.tabs.setFont(TAB_FONT)
        self.tabs.setTabPosition(QTabWidget.North)
        self.layout.addWidget(self.tabs)
        
        self.setup_tabs()
        
    def setup_tabs(self):
        # 1. Tab CREAR
        self.tab_create = QWidget()
        self.tabs.addTab(self.tab_create, QIcon(TAB_ICONS["crear"]), "Crear Bundle")
        self.setup_create_tab()
        
        # 2. Tab CONSTRUIR
        self.tab_build = QWidget()
        self.tabs.addTab(self.tab_build, QIcon(TAB_ICONS["construir"]), "Construir")
        self.setup_build_tab()
        
        # 3. Tab GESTOR (Simulación)
        self.tab_manager = QWidget()
        self.tabs.addTab(self.tab_manager, QIcon(TAB_ICONS["gestor"]), "Gestor de Bundles")
        self.setup_manager_tab()
        
        # 4. Tab AYUDA
        self.tab_help = Qixi = QWidget()
        self.tabs.addTab(self.tab_help, QIcon(TAB_ICONS["ayuda"]), "Ayuda")
        self.setup_help_tab()

    # --- Pestaña CREAR ---
    def setup_create_tab(self):
        layout = QVBoxLayout(self.tab_create)
        
        # Campos de entrada
        self.create_publisher = QLineEdit("influent")
        self.create_name = QLineEdit("mybundle")
        self.create_version = QLineEdit("1.0")
        self.create_title = QLineEdit("My Cool Bundle")
        
        # Layout de campos
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("Fabricante:", self.create_publisher)
        form_layout.addRow("Nombre Interno:", self.create_name)
        form_layout.addRow("Versión:", self.create_version)
        form_layout.addRow("Título:", self.create_title)
        
        layout.addLayout(form_layout)
        
        # Botón de crear
        create_btn = QPushButton("Crear Estructura de Bundle")
        create_btn.setFont(BUTTON_FONT)
        create_btn.setStyleSheet(BTN_STYLES["default"])
        create_btn.clicked.connect(self.create_bundle_project)
        layout.addWidget(create_btn)
        
        layout.addStretch()

    def create_bundle_project(self):
        empresa = self.create_publisher.text()
        nombre_logico = self.create_name.text()
        nombre_completo = self.create_title.text()
        version = self.create_version.text()
        
        if not (empresa and nombre_logico and nombre_completo and version):
            QMessageBox.warning(self, "Datos Incompletos", "Por favor, complete todos los campos.")
            return

        project_dir = os.path.join(BASE_DIR, nombre_logico)
        
        if os.path.exists(project_dir):
            reply = QMessageBox.question(self, 'Proyecto Existente',
                f"El Bundle '{nombre_logico}' ya existe. ¿Desea sobrescribirlo?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.No:
                return
            shutil.rmtree(project_dir)

        try:
            os.makedirs(project_dir, exist_ok=True)
            create_bundle_structure(project_dir, empresa, nombre_logico, version)
            QMessageBox.information(self, "Éxito", f"Estructura del Bundle '{nombre_logico}' creada en:\n{project_dir}")
        except Exception as e:
            QMessageBox.critical(self, "Error de Creación", f"Fallo al crear el Bundle: {e}")

    # --- Pestaña CONSTRUIR ---
    def setup_build_tab(self):
        layout = QVBoxLayout(self.tab_build)
        
        # Lógica de Construcción (Simulación)
        layout.addWidget(QLabel("Funcionalidad de Construcción: Seleccione un proyecto de la pestaña 'Gestor de Bundles' para construirlo en formato .iflappb."))
        layout.addStretch()

    # --- Pestaña GESTOR ---
    def setup_manager_tab(self):
        layout = QVBoxLayout(self.tab_manager)
        
        # Lógica de Gestor (Simulación)
        layout.addWidget(QLabel("Gestor de Bundles: Muestra y permite la gestión de proyectos en el directorio 'Influent Bundles'."))
        layout.addStretch()

    # --- Pestaña AYUDA ---
    def setup_help_tab(self):
        layout = QVBoxLayout(self.tab_help)
        
        # Lógica de Ayuda
        layout.addWidget(QLabel("Ayuda y Documentación: Herramienta modular todo-en-uno para crear, empaquetar y gestionar Bundles Influent (.iflappb)."))
        layout.addStretch()

# --- Ejecución ---
if __name__ == '__main__':
    # Aseguramos que la carpeta de iconos exista para que la GUI no falle
    os.makedirs("app", exist_ok=True)
    if not os.path.exists(IPM_ICON_PATH):
        # Crear un placeholder si el icono no existe
        icon_placeholder = QtGui.QPixmap(32, 32)
        icon_placeholder.fill(QtGui.QColor("#45a0ff"))
        icon_placeholder.save(IPM_ICON_PATH)

    app = QApplication(sys.argv)
    ex = BundleMakerGUI()
    ex.show()
    sys.exit(app.exec_())
