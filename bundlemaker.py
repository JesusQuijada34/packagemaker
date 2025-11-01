# -*- coding: utf-8 -*-
# Bundlemaker - Herramienta para crear bundles .iflappb (APK/UWP estilo)
# Versión: Solo creación de bundles .iflappb
# Tema: Azul estilo GitHub con modo claro/oscuro automático

import sys
import os
import time
import hashlib
import shutil
import zipfile
import xml.etree.ElementTree as ET
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QMessageBox, QGridLayout, QTabWidget, QListWidget,
    QListWidgetItem, QFileDialog, QSplitter, QDialog, QAbstractItemView
)
from PyQt5.QtGui import QFont, QIcon, QPalette
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtWidgets import QStyle

# Detectar tema del sistema (claro/oscuro)
def is_dark_mode():
    """Detecta si el sistema está en modo oscuro"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    palette = app.palette()
    window_color = palette.color(QPalette.Window)
    return window_color.lightness() < 128

# Obtener tema actual
_is_dark = is_dark_mode()

# ----------- CONFIGURABLE VARIABLES -----------
APP_TITLE = "Influent Bundle Maker (.iflappb) - Creador de Bundles"
APP_FONT = QFont('Roboto', 13)
BUTTON_FONT = QFont('Arial', 12, QFont.Bold)

# Tema Azul estilo GitHub - Modo Claro
THEME_LIGHT = {
    "bg": "#ffffff",
    "fg": "#24292e",
    "border": "#e1e4e8",
    "input_bg": "#ffffff",
    "input_border": "#d1d5da",
    "button_default": "#0366d6",  # Azul GitHub
    "button_hover": "#0256c2",
    "button_text": "#ffffff",
    "success": "#28a745",
    "danger": "#d73a49",
    "group_bg": "#f6f8fa",
}

# Tema Azul estilo GitHub - Modo Oscuro
THEME_DARK = {
    "bg": "#0d1117",
    "fg": "#c9d1d9",
    "border": "#30363d",
    "input_bg": "#161b22",
    "input_border": "#21262d",
    "button_default": "#58a6ff",  # Azul claro GitHub oscuro
    "button_hover": "#79c0ff",
    "button_text": "#ffffff",
    "success": "#3fb950",
    "danger": "#f85149",
    "group_bg": "#161b22",
}

# Seleccionar tema según modo del sistema
THEME = THEME_DARK if _is_dark else THEME_LIGHT

# Rutas base - BundleMaker Projects
if sys.platform.startswith("win"):
    BASE_DIR = os.path.join(os.environ["USERPROFILE"], "My Documents", "BundleMaker Projects")
else:
    BASE_DIR = os.path.expanduser("~/Documentos/BundleMaker Projects")

IPM_ICON_PATH = "app/app-icon.ico"
# Estructura tipo APK/UWP
BUNDLE_FOLDERS = ["res", "data", "code", "manifest", "activity", "theme", "blob"]
BUNDLE_EXT = ".iflappb"

# Clasificación por edad
AGE_RATINGS = {
    "adult": "ADULTS ONLY",
    "kids": "FOR KIDS",
    "social": "PUBLIC CONTENT",
    "ai": "PUBLIC ALL",
    "default": "EVERYONE"
}

# --- Utilidades ---

def getversion_stamp():
    return time.strftime("%y.%m-%H.%M")

def get_age_rating(name, title):
    search_string = (name + title).lower()
    for keyword, rate in AGE_RATINGS.items():
        if keyword in search_string:
            return rate
    return AGE_RATINGS["default"]

def create_bundle_details_xml(path, empresa, nombre_logico, nombre_completo, version):
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
    ET.SubElement(root, "knosthalij").text = newversion  # Entorno Bundle
    ET.SubElement(root, "correlationid").text = hash_val
    ET.SubElement(root, "rate").text = rating

    tree = ET.ElementTree(root)
    tree.write(os.path.join(path, "details.xml"), encoding="utf-8", xml_declaration=True)

def create_bundle_manifest_json(path, nombre_logico, version):
    """Crea manifest.json estilo APK/UWP"""
    manifest = {
        "package": nombre_logico,
        "version": version,
        "name": nombre_logico,
        "activities": [
            {
                "name": "MainActivity",
                "entry": "code/main.py",
                "type": "python"
            }
        ],
        "resources": {
            "icons": "res/",
            "layouts": "res/layouts/",
            "strings": "res/values/strings.xml"
        }
    }
    
    manifest_path = os.path.join(path, "manifest", "manifest.json")
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

def create_bundle_manifest_xml(path, nombre_logico):
    """Crea manifest.xml estilo UWP"""
    root = ET.Element("Package")
    root.set("xmlns", "http://schemas.microsoft.com/appx/manifest/foundation/windows10")
    
    identity = ET.SubElement(root, "Identity")
    identity.set("Name", nombre_logico)
    identity.set("Version", "1.0.0.0")
    identity.set("Publisher", "CN=Influent")
    
    properties = ET.SubElement(root, "Properties")
    ET.SubElement(properties, "DisplayName").text = nombre_logico
    ET.SubElement(properties, "PublisherDisplayName").text = "Influent"
    
    applications = ET.SubElement(root, "Applications")
    application = ET.SubElement(applications, "Application")
    application.set("Id", "App")
    
    visual_elements = ET.SubElement(application, "VisualElements")
    visual_elements.set("DisplayName", nombre_logico)
    visual_elements.set("Square150x150Logo", "res/logo.png")
    visual_elements.set("Square44x44Logo", "res/logo.png")
    
    tree = ET.ElementTree(root)
    tree.write(os.path.join(path, "manifest", "Package.appxmanifest"), encoding="utf-8", xml_declaration=True)

def create_activity_xml(path, nombre_logico):
    """Crea activity.xml para definir actividades"""
    root = ET.Element("Activities")
    activity = ET.SubElement(root, "Activity")
    activity.set("name", "MainActivity")
    activity.set("type", "python")
    
    ET.SubElement(activity, "EntryPoint").text = "code/main.py"
    ET.SubElement(activity, "Icon").text = "res/icon.png"
    
    tree = ET.ElementTree(root)
    tree.write(os.path.join(path, "activity", "activities.xml"), encoding="utf-8", xml_declaration=True)

def create_bundle_structure(full_path, empresa, nombre_logico, nombre_completo, version):
    """Crea la estructura de carpetas y archivos iniciales para un bundle .iflappb (estilo APK/UWP)"""
    # Crear estructura de carpetas
    for folder in BUNDLE_FOLDERS:
        os.makedirs(os.path.join(full_path, folder.strip()), exist_ok=True)
    
    # Carpetas adicionales estilo APK/UWP
    os.makedirs(os.path.join(full_path, "res", "values"), exist_ok=True)
    os.makedirs(os.path.join(full_path, "res", "layouts"), exist_ok=True)
    os.makedirs(os.path.join(full_path, "res", "drawable"), exist_ok=True)
    os.makedirs(os.path.join(full_path, "data", "databases"), exist_ok=True)
    os.makedirs(os.path.join(full_path, "data", "shared_prefs"), exist_ok=True)
    
    # Archivo principal Python
    main_script = os.path.join(full_path, "code", "main.py")
    with open(main_script, "w", encoding="utf-8") as f:
        f.write("""# -*- coding: utf-8 -*-
# Bundle Main Activity
# Estructura estilo APK/UWP escrita en Python

def main():
    print("¡Bundle iniciado! Estructura APK/UWP en Python")
    # Tu código aquí
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
""")

    # Archivo de configuración
    config_script = os.path.join(full_path, "code", "config.py")
    with open(config_script, "w", encoding="utf-8") as f:
        f.write("# -*- coding: utf-8 -*-\n# Configuración del Bundle\n")
    
    # Archivo de recursos strings.xml (estilo Android)
    strings_xml = os.path.join(full_path, "res", "values", "strings.xml")
    with open(strings_xml, "w", encoding="utf-8") as f:
        f.write("""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">"""+ nombre_logico + """</string>
    <string name="app_title">"""+ nombre_completo + """</string>
</resources>
""")
    
    # Archivo README.md
    readme_path = os.path.join(full_path, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(f"""# Bundle: {nombre_completo}

Creado por: {empresa}
Versión: v{version}

Este es un bundle .iflappb con estructura estilo APK/UWP.

## Estructura
- `res/` - Recursos (imágenes, layouts, strings)
- `data/` - Datos de la aplicación
- `code/` - Código Python
- `manifest/` - Manifiestos (manifest.json y Package.appxmanifest)
- `activity/` - Definiciones de actividades
- `theme/` - Temas y estilos
- `blob/` - Archivos binarios grandes
""")
    
    # Crear archivos de manifiesto
    create_bundle_details_xml(full_path, empresa, nombre_logico, nombre_completo, version)
    create_bundle_manifest_json(full_path, nombre_logico, version)
    create_bundle_manifest_xml(full_path, nombre_logico)
    create_activity_xml(full_path, nombre_logico)

class BuildThread(QThread):
    """Thread para construir bundles .iflappb"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, empresa, nombre, version, parent=None):
        super().__init__(parent)
        self.empresa = empresa
        self.nombre = nombre
        self.version = version
    
    def run(self):
        folder = f"{self.empresa}.{self.nombre}.v{self.version}"
        path = os.path.join(BASE_DIR, folder)
        output_file = os.path.join(BASE_DIR, folder + BUNDLE_EXT)
        zip_path = output_file.replace(BUNDLE_EXT, "") + ".zip"
        
        if not os.path.exists(path):
            self.error.emit("No se encontró la carpeta del bundle.")
            return
        
        try:
            file_list = []
            for root, _, files in os.walk(path):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, path)
                    file_list.append((full_path, arcname))
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for i, (full_path, arcname) in enumerate(file_list):
                    zipf.write(full_path, arcname)
                    self.progress.emit(f"Empaquetando archivo {i+1}/{len(file_list)}: {arcname}")
            
            os.rename(zip_path, output_file)
            self.finished.emit(f"Bundle .iflappb construido: {output_file}")
        except Exception as e:
            self.error.emit(str(e))

# --- Clase Principal de la Aplicación (GUI) ---
class BundlemakerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        from PyQt5.QtWidgets import QTabWidget
        
        self.setWindowTitle(APP_TITLE)
        self.setWindowIcon(QIcon(IPM_ICON_PATH))
        self.resize(1200, 750)
        self.setFont(APP_FONT)
        self.statusBar().showMessage("Iniciando...")
        
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.layout = QVBoxLayout(self.central)
        
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont('Roboto', 12))
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(True)
        self.layout.addWidget(self.tabs)
        
        self.init_tabs()
        self.setMinimumSize(700, 500)
        
        # Aplicar tema
        self.apply_theme()
        
    def init_tabs(self):
        self.tab_create = QWidget()
        self.tabs.addTab(self.tab_create, QIcon("./app/package_add.ico"), "Crear Bundle")
        self.init_create_tab()
        
        self.tab_build = QWidget()
        self.tabs.addTab(self.tab_build, QIcon("./app/package_build.ico"), "Construir Bundle")
        self.init_build_tab()
        
        self.tab_manager = QWidget()
        self.tabs.addTab(self.tab_manager, QIcon("./app/package_fm.ico"), "Gestor de Bundles")
        self.init_manager_tab()
        
        self.tab_about = QWidget()
        self.tabs.addTab(self.tab_about, QIcon("./app/package_about.ico"), "Acerca de")
        self.init_about_tab()
        
        self.statusBar().showMessage("Preparable!...")

    def apply_theme(self):
        """Aplica el tema azul estilo GitHub con modo claro/oscuro automático"""
        from PyQt5.QtGui import QPalette
        app = QApplication.instance()
        palette = app.palette()
        is_dark = palette.color(QPalette.Window).lightness() < 128
        
        # Tema Azul estilo GitHub - Modo Claro
        theme_light = {
            "bg": "#ffffff",
            "fg": "#24292e",
            "border": "#e1e4e8",
            "input_bg": "#ffffff",
            "input_border": "#d1d5da",
            "button_default": "#0366d6",  # Azul GitHub
            "button_hover": "#0256c2",
            "button_text": "#ffffff",
            "group_bg": "#f6f8fa",
        }
        
        # Tema Azul estilo GitHub - Modo Oscuro
        theme_dark = {
            "bg": "#0d1117",
            "fg": "#c9d1d9",
            "border": "#30363d",
            "input_bg": "#161b22",
            "input_border": "#21262d",
            "button_default": "#58a6ff",  # Azul claro GitHub oscuro
            "button_hover": "#79c0ff",
            "button_text": "#ffffff",
            "group_bg": "#161b22",
        }
        
        theme = theme_dark if is_dark else theme_light
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme["bg"]};
                color: {theme["fg"]};
            }}
            QWidget {{
                background-color: {theme["bg"]};
                color: {theme["fg"]};
            }}
            QTabWidget::pane {{
                border: 1px solid {theme["border"]};
                background-color: {theme["bg"]};
            }}
            QTabBar::tab {{
                background-color: {theme["group_bg"]};
                color: {theme["fg"]};
                padding: 10px;
                border: 1px solid {theme["border"]};
                border-bottom: none;
                border-radius: 6px 6px 0 0;
            }}
            QTabBar::tab:selected {{
                background-color: {theme["bg"]};
                border-bottom: 2px solid {theme["button_default"]};
            }}
            QGroupBox {{
                background-color: {theme["group_bg"]};
                color: {theme["fg"]};
                border: 1px solid {theme["border"]};
                border-radius: 6px;
                padding: 10px;
                margin-top: 10px;
                font-weight: bold;
            }}
            QLabel {{
                color: {theme["fg"]};
                font-size: 15px;
            }}
            QLineEdit {{
                background-color: {theme["input_bg"]};
                color: {theme["fg"]};
                border: 1px solid {theme["input_border"]};
                border-radius: 6px;
                padding: 6px;
            }}
            QLineEdit:focus {{
                border: 1px solid {theme["button_default"]};
            }}
            QPushButton {{
                background-color: {theme["button_default"]};
                color: {theme["button_text"]};
                border: none;
                border-radius: 6px;
                padding: 10px 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme["button_hover"]};
            }}
            QListWidget {{
                background-color: {theme["input_bg"]};
                color: {theme["fg"]};
                font-size: 12px;
                border-radius: 5px;
                border: 1px solid {theme["border"]};
            }}
            QStatusBar {{
                background-color: {theme["group_bg"]};
                color: {theme["fg"]};
                border-top: 1px solid {theme["border"]};
            }}
        """)

    def init_create_tab(self):
        layout = QVBoxLayout()
        form_group = QGroupBox("Datos del Bundle")
        form_layout = QVBoxLayout(form_group)
        
        self.input_empresa = QLineEdit()
        self.input_empresa.setPlaceholderText("Ejemplo: influent")
        form_layout.addWidget(QLabel("Fabricante:"))
        form_layout.addWidget(self.input_empresa)
        
        self.input_nombre_logico = QLineEdit()
        self.input_nombre_logico.setPlaceholderText("Ejemplo: mybundle")
        form_layout.addWidget(QLabel("Nombre interno:"))
        form_layout.addWidget(self.input_nombre_logico)
        
        self.input_version = QLineEdit()
        self.input_version.setPlaceholderText("Ejemplo: 1.0")
        form_layout.addWidget(QLabel("Versión:"))
        form_layout.addWidget(self.input_version)
        
        self.input_titulo = QLineEdit()
        self.input_titulo.setPlaceholderText("Ejemplo: MyBundle")
        form_layout.addWidget(QLabel("Título completo:"))
        form_layout.addWidget(self.input_titulo)
        
        self.btn_create = QPushButton("Crear Bundle")
        self.btn_create.setFont(BUTTON_FONT)
        self.btn_create.clicked.connect(self.create_bundle_action)
        self.create_status = QLabel("")
        self.create_status.setStyleSheet("color:#28a745;")
        layout.addWidget(form_group)
        layout.addWidget(self.btn_create)
        layout.addWidget(self.create_status)
        self.tab_create.setLayout(layout)
        self.statusBar().showMessage("Preparando entorno...")
    
    def init_build_tab(self):
        layout = QVBoxLayout()
        form_group = QGroupBox("Construir Bundle")
        form_layout = QVBoxLayout(form_group)
        
        self.input_build_empresa = QLineEdit()
        self.input_build_empresa.setPlaceholderText("Ejemplo: influent")
        form_layout.addWidget(QLabel("Fabricante:"))
        form_layout.addWidget(self.input_build_empresa)
        
        self.input_build_nombre = QLineEdit()
        self.input_build_nombre.setPlaceholderText("Ejemplo: mybundle")
        form_layout.addWidget(QLabel("Nombre interno:"))
        form_layout.addWidget(self.input_build_nombre)
        
        self.input_build_version = QLineEdit()
        self.input_build_version.setPlaceholderText("Ejemplo: 1.0")
        form_layout.addWidget(QLabel("Versión:"))
        form_layout.addWidget(self.input_build_version)
        
        self.btn_build = QPushButton("Construir bundle .iflappb")
        self.btn_build.setFont(BUTTON_FONT)
        self.btn_build.clicked.connect(self.build_bundle_action)
        
        self.build_status = QLabel("")
        self.build_status.setStyleSheet("color:#0366d6;")
        layout.addWidget(form_group)
        layout.addWidget(self.btn_build)
        layout.addWidget(self.build_status)
        self.tab_build.setLayout(layout)

    def create_bundle_action(self):
        self.statusBar().showMessage("Creando Bundle .iflappb...")
        empresa = self.input_empresa.text().strip().lower().replace(" ", "-") or "influent"
        nombre_logico = self.input_nombre_logico.text().strip().lower() or "mybundle"
        version = self.input_version.text().strip()
        if version == "":
            version = f"1-{getversion_stamp()}-knosthalij"
        else:
            version = f"{version}-{getversion_stamp()}-knosthalij"
        nombre_completo = self.input_titulo.text() or nombre_logico.strip().upper()
        folder_name = f"{empresa}.{nombre_logico}.v{version}"
        full_path = os.path.join(BASE_DIR, folder_name)
        
        if os.path.exists(full_path):
            reply = QMessageBox.question(self, 'Bundle Existente',
                f"El bundle '{nombre_logico}' ya existe. ¿Desea sobrescribirlo?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return
            shutil.rmtree(full_path)
        
        try:
            os.makedirs(BASE_DIR, exist_ok=True)
            os.makedirs(full_path, exist_ok=True)
            create_bundle_structure(full_path, empresa, nombre_logico, nombre_completo, version)
            fn = f"{empresa}.{nombre_logico}.v{version}"
            hv = hashlib.sha256(fn.encode()).hexdigest()
            self.create_status.setText(f"✅ Bundle creado en: {folder_name}/\n🔐 Protegido con sha256: {hv}")
            self.statusBar().showMessage(f"Bundle creado como {empresa}.{nombre_logico}.v{version}!")
        except Exception as e:
            self.create_status.setText(f"❌ Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Fallo al crear el bundle: {e}")

    def build_bundle_action(self):
        empresa = self.input_build_empresa.text().strip().lower() or "influent"
        nombre = self.input_build_nombre.text().strip().lower() or "mybundle"
        version = self.input_build_version.text().strip() or "1"
        # Siempre compila .iflappb
        self.build_status.setText("🔨 Construyendo bundle .iflappb...")
        self.build_thread = BuildThread(empresa, nombre, version)
        self.build_thread.progress.connect(lambda msg: self.build_status.setText(msg))
        self.build_thread.finished.connect(lambda msg: self.build_status.setText(msg))
        self.build_thread.error.connect(lambda msg: self.build_status.setText(f"❌ Error: {msg}"))
        self.build_thread.start()
        self.statusBar().showMessage(f"Bundle .iflappb armado como {empresa}.{nombre}.v{version}!")

    def init_manager_tab(self):
        layout = QVBoxLayout()
        splitter = QSplitter(Qt.Horizontal)
        proj_group = QGroupBox("Bundles locales")
        proj_layout = QVBoxLayout(proj_group)
        self.projects_list = QListWidget()
        self.projects_list.setIconSize(QSize(32, 32))
        self.projects_list.setAlternatingRowColors(True)
        self.projects_list.setSelectionMode(QAbstractItemView.SingleSelection)
        proj_layout.addWidget(self.projects_list)
        splitter.addWidget(proj_group)

        apps_group = QGroupBox("Bundles instalados")
        apps_layout = QVBoxLayout(apps_group)
        self.apps_list = QListWidget()
        self.apps_list.setIconSize(QSize(32, 32))
        self.apps_list.setAlternatingRowColors(True)
        self.apps_list.setSelectionMode(QAbstractItemView.SingleSelection)
        apps_layout.addWidget(self.apps_list)
        splitter.addWidget(apps_group)

        splitter.setSizes([1, 1])
        layout.addWidget(splitter)
        btn_row = QHBoxLayout()
        btn_refresh = QPushButton("Refrescar listas")
        btn_refresh.setFont(BUTTON_FONT)
        btn_refresh.clicked.connect(self.load_manager_lists)
        btn_row.addWidget(btn_refresh)

        btn_install = QPushButton("Instalar bundle")
        btn_install.setFont(BUTTON_FONT)
        btn_install.clicked.connect(self.install_bundle_action)
        btn_row.addWidget(btn_install)

        btn_uninstall = QPushButton("Desinstalar bundle")
        btn_uninstall.setFont(BUTTON_FONT)
        btn_uninstall.clicked.connect(self.uninstall_bundle_action)
        btn_row.addWidget(btn_uninstall)
        layout.addLayout(btn_row)

        self.manager_status = QLabel("")
        self.manager_status.setWordWrap(True)
        layout.addWidget(self.manager_status)
        self.tab_manager.setLayout(layout)
        self.load_manager_lists()

    def get_bundle_list(self, base):
        bundles = []
        if not os.path.exists(base):
            return bundles
        for d in os.listdir(base):
            folder = os.path.join(base, d)
            details_path = os.path.join(folder, "details.xml")
            if os.path.isdir(folder) and os.path.exists(details_path):
                try:
                    tree = ET.parse(details_path)
                    root = tree.getroot()
                    details = {child.tag: child.text for child in root}
                    empresa = details.get("publisher", "Origen Desconocido")
                    titulo = details.get("name", d)
                    version = details.get("version", "v?")
                    bundles.append({
                        "folder": folder,
                        "empresa": empresa,
                        "titulo": titulo,
                        "version": version,
                        "name": d,
                    })
                except Exception:
                    continue
        return bundles

    def load_manager_lists(self):
        self.projects_list.clear()
        self.apps_list.clear()
        bundles = self.get_bundle_list(BASE_DIR)
        for b in bundles:
            icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
            text = f"{b['empresa'].capitalize()} {b['titulo']} | {b['version']}"
            item = QListWidgetItem(icon, text)
            item.setData(Qt.UserRole, b)
            self.projects_list.addItem(item)

    def install_bundle_action(self):
        files = QFileDialog.getOpenFileNames(self, "Selecciona bundles para instalar", BASE_DIR, "Bundles (*.iflappb)")[0]
        for file_path in files:
            if not file_path:
                continue
            bundle_name = os.path.basename(file_path).replace(".iflappb", "")
            target_dir = os.path.join(BASE_DIR, bundle_name)
            os.makedirs(target_dir, exist_ok=True)
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(target_dir)
                self.manager_status.setText(f"✅ Instalado: {bundle_name}")
            except Exception as e:
                self.manager_status.setText(f"❌ Error al instalar {bundle_name}: {e}")
        self.load_manager_lists()

    def uninstall_bundle_action(self):
        item = self.apps_list.currentItem()
        if not item:
            self.manager_status.setText("Selecciona un bundle instalado para desinstalar.")
            return
        bundle = item.data(Qt.UserRole)
        try:
            shutil.rmtree(bundle["folder"])
            self.manager_status.setText(f"🗑️ Desinstalado: {bundle['titulo']}")
        except Exception as e:
            self.manager_status.setText(f"❌ Error al desinstalar: {e}")
        self.load_manager_lists()

    def init_about_tab(self):
        layout = QVBoxLayout()
        about_text = (
            "<b>Influent Bundle Maker (.iflappb)</b><br>"
            "Creador y empaquetador de bundles Influent (.iflappb) con estructura estilo APK/UWP.<br><br>"
            "<b>Funciones:</b><ul>"
            "<li>Estructura tipo APK/UWP (res/, data/, code/, manifest/, activity/, theme/, blob/)</li>"
            "<li>Manifiestos JSON y XML (manifest.json y Package.appxmanifest)</li>"
            "<li>Definición de actividades XML</li>"
            "<li>Recursos tipo Android (strings.xml, layouts)</li>"
            "<li>Interfaz estilo GitHub con tema azul</li>"
            "<li>Modo claro/oscuro automático</li>"
            "<li>Construcción exclusiva de bundles .iflappb</li>"
            "</ul>"
            "<b>Desarrollador:</b> <a href='https://t.me/JesusQuijada34/'>Jesus Quijada (@JesusQuijada34)</a><br>"
            "<b>GitHub:</b> <a href='https://github.com/jesusquijada34/packagemaker/'>packagemaker</a><br>"
        )
        about_label = QLabel(about_text)
        about_label.setOpenExternalLinks(True)
        layout.addWidget(about_label)
        self.tab_about.setLayout(layout)

# --- Ejecución ---
if __name__ == '__main__':
    os.makedirs("app", exist_ok=True)
    
    app = QApplication(sys.argv)
    ex = BundlemakerApp()
    ex.show()
    sys.exit(app.exec_())
