#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Influent Package Maker - Shell Handler
Maneja las invocaciones desde el menú contextual del explorador
"""

import sys
import os
import json
import traceback
from datetime import datetime

# Log de debug
LOG_FILE = os.path.join(os.path.expanduser("~"), "ipm-shell-debug.log")

def log(mensaje):
    """Escribe en el archivo de log"""
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {mensaje}\n")
    except:
        pass

log("=" * 60)
log("INICIO DE EJECUCIÓN")
log(f"Argumentos: {sys.argv}")
log(f"Python: {sys.executable}")
log(f"CWD: {os.getcwd()}")

# Detectar si estamos en un ejecutable compilado
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    sys.path.insert(0, BASE_DIR)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, BASE_DIR)

log(f"BASE_DIR: {BASE_DIR}")

try:
    from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
                                 QLabel, QLineEdit, QTextEdit, QPushButton, 
                                 QWidget, QCheckBox, QMessageBox, QListWidget,
                                 QListWidgetItem, QGroupBox, QScrollArea, QFrame,
                                 QFileDialog, QComboBox)
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont, QIcon
    log("PyQt5 importado correctamente")
except Exception as e:
    log(f"ERROR importando PyQt5: {e}")
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error", f"Error importando PyQt5:\n{e}\n\nInstala con: pip install PyQt5")
    sys.exit(1)

# Intentar importar LeviathanUI para efectos visuales
try:
    from leviathan_ui import LeviathanDialog, get_accent_color
    LEVIATHAN_AVAILABLE = True
    log("LeviathanUI importado correctamente")
except Exception as e:
    LEVIATHAN_AVAILABLE = False
    log(f"LeviathanUI no disponible: {e}")

# Configuración
Fluthin_APPS = os.path.join(os.path.expanduser("~"), "Documents", "Fluthin Apps")
BTN_STYLES = {
    "default": (
        "background-color: rgba(243,246,251,0.85);"
        "color: rgba(32,33,36,0.96);"
        "border-radius: 9px;"
        "padding: 10px 20px;"
        "font-weight: 600;"
        "border: 1px solid rgba(209,215,224,0.65);"
    ),
    "success": (
        "background-color: rgba(230,244,234,0.82);"
        "color: rgba(5,98,55,0.99);"
        "border-radius: 9px;"
        "padding: 10px 20px;"
        "font-weight: 600;"
        "border: 1px solid rgba(199,232,206,0.60);"
    ),
    "danger": (
        "background-color: rgba(253,231,231,0.80);"
        "color: rgba(185,29,29,1.0);"
        "border-radius: 9px;"
        "padding: 10px 20px;"
        "font-weight: 600;"
        "border: 1px solid rgba(255,180,180,0.68);"
    ),
    "best": (
        "background-color: qlineargradient(y1:0, y2:1, stop:0 #e6f4fa, stop:1 #c4e6fb);"
        "color: #0853c4;"
        "border-radius: 11px;"
        "padding: 12px 22px;"
        "font-weight: 700;"
        "border: 2px solid #99d3f7;"
        "font-size: 15px;"
    )
}


class SimpleDialog(QDialog):
    """Diálogo simple sin dependencias complejas"""
    
    def __init__(self, parent=None, title="IPM"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(600, 500)
        self.setStyleSheet("""
            QDialog { background-color: #1a1f2e; }
            QLabel { color: white; font-size: 13px; }
            QLineEdit, QTextEdit {
                background-color: rgba(255,255,255,0.1);
                color: white;
                border: 2px solid rgba(255,255,255,0.2);
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
            }
            QLineEdit:focus, QTextEdit:focus { border: 2px solid #2486ff; }
            QPushButton { min-height: 40px; border-radius: 8px; font-weight: bold; }
            QCheckBox { color: white; font-size: 13px; }
        """)
        log(f"Diálogo creado: {title}")


def crearProyecto(rutaProyecto, app):
    """Ventana para crear un nuevo proyecto"""
    log(f"crearProyecto llamado con: {rutaProyecto}")
    
    try:
        log("Creando diálogo...")
        dialogo = SimpleDialog(title="🆕 Crear Proyecto Aquí")
        layout = QVBoxLayout(dialogo)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        lblTitulo = QLabel("Crear Nuevo Proyecto")
        lblTitulo.setStyleSheet("color: white; font-size: 22px; font-weight: bold;")
        lblTitulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(lblTitulo)
        
        lblRuta = QLabel(f"📁 {rutaProyecto}")
        lblRuta.setStyleSheet("color: #aaa; font-size: 12px;")
        lblRuta.setWordWrap(True)
        layout.addWidget(lblRuta)
        
        lblNombre = QLabel("Nombre del Proyecto:")
        lblNombre.setStyleSheet("font-weight: bold;")
        layout.addWidget(lblNombre)
        
        txtNombre = QLineEdit(os.path.basename(rutaProyecto))
        layout.addWidget(txtNombre)
        
        lblVersion = QLabel("Versión:")
        lblVersion.setStyleSheet("font-weight: bold;")
        layout.addWidget(lblVersion)
        
        txtVersion = QLineEdit("1.0")
        layout.addWidget(txtVersion)
        
        lblAutor = QLabel("Autor:")
        lblAutor.setStyleSheet("font-weight: bold;")
        layout.addWidget(lblAutor)
        
        txtAutor = QLineEdit()
        txtAutor.setPlaceholderText("Tu nombre")
        layout.addWidget(txtAutor)
        
        lblDesc = QLabel("Descripción:")
        lblDesc.setStyleSheet("font-weight: bold;")
        layout.addWidget(lblDesc)
        
        txtDesc = QTextEdit()
        txtDesc.setPlaceholderText("Describe tu proyecto...")
        txtDesc.setMaximumHeight(80)
        layout.addWidget(txtDesc)
        
        layout.addStretch()
        
        layoutBotones = QHBoxLayout()
        btnCancelar = QPushButton("❌ Cancelar")
        btnCancelar.setStyleSheet(BTN_STYLES["default"])
        btnCancelar.clicked.connect(dialogo.reject)
        
        btnCrear = QPushButton("✨ Crear Proyecto")
        btnCrear.setStyleSheet(BTN_STYLES["best"])
        
        def crear():
            log("Botón Crear presionado")
            nombre = txtNombre.text().strip()
            if not nombre:
                log("Error: nombre vacío")
                QMessageBox.warning(dialogo, "Error", "El nombre no puede estar vacío")
                return
            
            try:
                rutaFinal = os.path.join(rutaProyecto, nombre)
                log(f"Creando proyecto en: {rutaFinal}")
                os.makedirs(rutaFinal, exist_ok=True)
                
                for carpeta in ["app", "assets", "config", "docs", "lib", "source"]:
                    os.makedirs(os.path.join(rutaFinal, carpeta), exist_ok=True)
                
                xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<package>
    <app>{nombre}</app>
    <version>{txtVersion.text()}</version>
    <platform>Windows</platform>
    <author>{txtAutor.text() or 'Unknown'}</author>
    <description>{txtDesc.toPlainText() or 'Proyecto creado con IPM'}</description>
</package>"""
                
                with open(os.path.join(rutaFinal, "details.xml"), 'w', encoding='utf-8') as f:
                    f.write(xml)
                
                py = f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
{nombre}
"""

def main():
    print("¡Hola desde {nombre}!")

if __name__ == "__main__":
    main()
'''
                with open(os.path.join(rutaFinal, f"{nombre}.py"), 'w', encoding='utf-8') as f:
                    f.write(py)
                
                log("Proyecto creado exitosamente")
                QMessageBox.information(dialogo, "✅ Éxito", f"Proyecto creado en:\n{rutaFinal}")
                dialogo.accept()
                
            except Exception as e:
                log(f"Error creando proyecto: {e}")
                QMessageBox.critical(dialogo, "❌ Error", f"Error:\n{e}")
        
        btnCrear.clicked.connect(crear)
        layoutBotones.addWidget(btnCancelar)
        layoutBotones.addWidget(btnCrear)
        layout.addLayout(layoutBotones)
        
        log("Mostrando diálogo...")
        resultado = dialogo.exec_()
        log(f"Diálogo cerrado con resultado: {resultado}")
        return resultado
        
    except Exception as e:
        log(f"ERROR en crearProyecto: {e}")
        log(traceback.format_exc())
        # Mostrar error con messagebox básico
        try:
            QMessageBox.critical(None, "Error", f"Error:\n{e}\n\n{traceback.format_exc()}")
        except:
            pass
        return 1


def crearMexf(rutaCarpeta, app):
    """Ventana para crear archivo MEXF"""
    log(f"crearMexf llamado con: {rutaCarpeta}")
    
    try:
        dialogo = SimpleDialog(title="📝 Crear Archivo MEXF")
        layout = QVBoxLayout(dialogo)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        lblTitulo = QLabel("Crear Archivo de Extensiones MEXF")
        lblTitulo.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        lblTitulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(lblTitulo)
        
        lblInfo = QLabel(f"📁 {rutaCarpeta}")
        lblInfo.setStyleSheet("color: #aaa; font-size: 12px;")
        lblInfo.setWordWrap(True)
        layout.addWidget(lblInfo)
        
        lblNombre = QLabel("Nombre del archivo:")
        lblNombre.setStyleSheet("font-weight: bold;")
        layout.addWidget(lblNombre)
        
        txtNombre = QLineEdit("extension")
        layout.addWidget(txtNombre)
        
        lblDesc = QLabel("Descripción:")
        lblDesc.setStyleSheet("font-weight: bold;")
        layout.addWidget(lblDesc)
        
        txtDesc = QTextEdit()
        txtDesc.setPlaceholderText("Describe las extensiones...")
        txtDesc.setMaximumHeight(100)
        layout.addWidget(txtDesc)
        
        layout.addStretch()
        
        layoutBotones = QHBoxLayout()
        btnCancelar = QPushButton("❌ Cancelar")
        btnCancelar.setStyleSheet(BTN_STYLES["default"])
        btnCancelar.clicked.connect(dialogo.reject)
        
        btnCrear = QPushButton("📝 Crear MEXF")
        btnCrear.setStyleSheet(BTN_STYLES["best"])
        
        def crear():
            log("Botón Crear MEXF presionado")
            nombre = txtNombre.text().strip()
            if not nombre:
                log("Error: nombre vacío")
                QMessageBox.warning(dialogo, "Error", "El nombre no puede estar vacío")
                return
            
            try:
                rutaMexf = os.path.join(rutaCarpeta, f"{nombre}.mexf")
                log(f"Creando MEXF en: {rutaMexf}")
                
                if os.path.exists(rutaMexf):
                    respuesta = QMessageBox.question(dialogo, "Archivo Existente", 
                        f"El archivo '{nombre}.mexf' ya existe.\n¿Sobrescribir?",
                        QMessageBox.Yes | QMessageBox.No)
                    if respuesta == QMessageBox.No:
                        return
                
                contenido = {
                    "name": nombre,
                    "version": "1.0",
                    "description": txtDesc.toPlainText() or "Extensiones personalizadas",
                    "mimetypes": [],
                    "context_menus": [],
                    "shell_extensions": {}
                }
                
                with open(rutaMexf, 'w', encoding='utf-8') as f:
                    json.dump(contenido, f, indent=4, ensure_ascii=False)
                
                log("MEXF creado exitosamente")
                QMessageBox.information(dialogo, "✅ Éxito", f"Archivo MEXF creado:\n{rutaMexf}")
                dialogo.accept()
                
            except Exception as e:
                log(f"Error creando MEXF: {e}")
                QMessageBox.critical(dialogo, "❌ Error", f"Error:\n{e}")
        
        btnCrear.clicked.connect(crear)
        layoutBotones.addWidget(btnCancelar)
        layoutBotones.addWidget(btnCrear)
        layout.addLayout(layoutBotones)
        
        log("Mostrando diálogo MEXF...")
        resultado = dialogo.exec_()
        log(f"Diálogo MEXF cerrado con resultado: {resultado}")
        return resultado
        
    except Exception as e:
        log(f"ERROR en crearMexf: {e}")
        log(traceback.format_exc())
        try:
            QMessageBox.critical(None, "Error", f"Error:\n{e}\n\n{traceback.format_exc()}")
        except:
            pass
        return 1


def compilarProyecto(rutaProyecto, app):
    """Ventana para compilar proyecto"""
    log(f"compilarProyecto llamado con: {rutaProyecto}")
    
    try:
        dialogo = SimpleDialog(title="🔨 Compilar Proyecto")
        layout = QVBoxLayout(dialogo)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        lblTitulo = QLabel("Compilar Proyecto")
        lblTitulo.setStyleSheet("color: white; font-size: 22px; font-weight: bold;")
        lblTitulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(lblTitulo)
        
        lblInfo = QLabel(f"📁 {os.path.basename(rutaProyecto)}")
        lblInfo.setStyleSheet("color: #aaa; font-size: 12px;")
        layout.addWidget(lblInfo)
        
        lblMensaje = QLabel("Esta función compilará el proyecto seleccionado.\n\n(Función en desarrollo)")
        lblMensaje.setStyleSheet("color: white; font-size: 14px;")
        lblMensaje.setWordWrap(True)
        lblMensaje.setAlignment(Qt.AlignCenter)
        layout.addWidget(lblMensaje)
        
        layout.addStretch()
        
        btnCerrar = QPushButton("Cerrar")
        btnCerrar.setStyleSheet(BTN_STYLES["default"])
        btnCerrar.clicked.connect(dialogo.accept)
        layout.addWidget(btnCerrar)
        
        log("Mostrando diálogo compilar...")
        resultado = dialogo.exec_()
        log(f"Diálogo compilar cerrado con resultado: {resultado}")
        return resultado
        
    except Exception as e:
        log(f"ERROR en compilarProyecto: {e}")
        log(traceback.format_exc())
        return 1


def instalarCarpeta(rutaCarpeta, app):
    """Ventana para instalar carpeta"""
    log(f"instalarCarpeta llamado con: {rutaCarpeta}")
    
    try:
        dialogo = SimpleDialog(title="📦 Instalar Carpeta")
        layout = QVBoxLayout(dialogo)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        lblTitulo = QLabel("Instalar como Fluthin Package")
        lblTitulo.setStyleSheet("color: white; font-size: 22px; font-weight: bold;")
        lblTitulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(lblTitulo)
        
        lblInfo = QLabel(f"📁 {os.path.basename(rutaCarpeta)}")
        lblInfo.setStyleSheet("color: #aaa; font-size: 12px;")
        layout.addWidget(lblInfo)
        
        lblMensaje = QLabel("Esta función instalará la carpeta como un paquete Fluthin.\n\n(Función en desarrollo)")
        lblMensaje.setStyleSheet("color: white; font-size: 14px;")
        lblMensaje.setWordWrap(True)
        lblMensaje.setAlignment(Qt.AlignCenter)
        layout.addWidget(lblMensaje)
        
        layout.addStretch()
        
        btnCerrar = QPushButton("Cerrar")
        btnCerrar.setStyleSheet(BTN_STYLES["default"])
        btnCerrar.clicked.connect(dialogo.accept)
        layout.addWidget(btnCerrar)
        
        log("Mostrando diálogo instalar...")
        resultado = dialogo.exec_()
        log(f"Diálogo instalar cerrado con resultado: {resultado}")
        return resultado
        
    except Exception as e:
        log(f"ERROR en instalarCarpeta: {e}")
        log(traceback.format_exc())
        return 1


def repararProyecto(rutaProyecto, app):
    """Ventana para reparar proyecto"""
    log(f"repararProyecto llamado con: {rutaProyecto}")
    
    try:
        dialogo = SimpleDialog(title="🌙 MoonFix")
        layout = QVBoxLayout(dialogo)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        lblTitulo = QLabel("Reparar Proyecto (MoonFix)")
        lblTitulo.setStyleSheet("color: white; font-size: 22px; font-weight: bold;")
        lblTitulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(lblTitulo)
        
        lblInfo = QLabel(f"📁 {os.path.basename(rutaProyecto)}")
        lblInfo.setStyleSheet("color: #aaa; font-size: 12px;")
        layout.addWidget(lblInfo)
        
        lblMensaje = QLabel("Esta función reparará automáticamente el proyecto.\n\n(Función en desarrollo)")
        lblMensaje.setStyleSheet("color: white; font-size: 14px;")
        lblMensaje.setWordWrap(True)
        lblMensaje.setAlignment(Qt.AlignCenter)
        layout.addWidget(lblMensaje)
        
        layout.addStretch()
        
        btnCerrar = QPushButton("Cerrar")
        btnCerrar.setStyleSheet(BTN_STYLES["default"])
        btnCerrar.clicked.connect(dialogo.accept)
        layout.addWidget(btnCerrar)
        
        log("Mostrando diálogo reparar...")
        resultado = dialogo.exec_()
        log(f"Diálogo reparar cerrado con resultado: {resultado}")
        return resultado
        
    except Exception as e:
        log(f"ERROR en repararProyecto: {e}")
        log(traceback.format_exc())
        return 1


def main():
    """Punto de entrada principal"""
    log("Función main iniciada")
    
    try:
        import argparse
        
        # Crear aplicación Qt primero
        log("Creando QApplication")
        app = QApplication(sys.argv)
        
        parser = argparse.ArgumentParser(description='IPM Shell Handler')
        parser.add_argument('--create-project', metavar='PATH', help='Crear proyecto')
        parser.add_argument('--create-mexf', metavar='PATH', help='Crear archivo MEXF')
        parser.add_argument('--compile-project', metavar='PATH', help='Compilar proyecto')
        parser.add_argument('--install-folder', metavar='PATH', help='Instalar carpeta')
        parser.add_argument('--repair-project', metavar='PATH', help='Reparar proyecto')
        
        args = parser.parse_args()
        log(f"Argumentos parseados: {args}")
        
        result = 1
        if args.create_project:
            log(f"Ejecutando crearProyecto con: {args.create_project}")
            result = crearProyecto(args.create_project, app)
        elif args.create_mexf:
            log(f"Ejecutando crearMexf con: {args.create_mexf}")
            result = crearMexf(args.create_mexf, app)
        elif args.compile_project:
            log(f"Ejecutando compilarProyecto con: {args.compile_project}")
            result = compilarProyecto(args.compile_project, app)
        elif args.install_folder:
            log(f"Ejecutando instalarCarpeta con: {args.install_folder}")
            result = instalarCarpeta(args.install_folder, app)
        elif args.repair_project:
            log(f"Ejecutando repararProyecto con: {args.repair_project}")
            result = repararProyecto(args.repair_project, app)
        else:
            log("No se proporcionaron argumentos válidos")
            QMessageBox.information(None, "IPM Shell Handler", 
                "Uso:\n"
                "  --create-project PATH\n"
                "  --create-mexf PATH\n"
                "  --compile-project PATH\n"
                "  --install-folder PATH\n"
                "  --repair-project PATH\n")
            result = 1
        
        log(f"Resultado final: {result}")
        return result
        
    except Exception as e:
        log(f"ERROR en main: {e}")
        log(traceback.format_exc())
        try:
            QMessageBox.critical(None, "Error Fatal", f"Error:\n{e}\n\n{traceback.format_exc()}")
        except:
            pass
        return 1


if __name__ == "__main__":
    try:
        resultado = main()
        log(f"Programa terminado con código: {resultado}")
        sys.exit(resultado)
    except Exception as e:
        log(f"ERROR FATAL: {e}")
        log(traceback.format_exc())
        sys.exit(1)
