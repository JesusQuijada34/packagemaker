#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar las ventanas de IPM
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from packagemaker import PackageTodoGUI

def test_ventanas():
    """Prueba las ventanas implementadas"""
    app = QApplication(sys.argv)
    
    # Crear instancia de la GUI
    window = PackageTodoGUI()
    window.show()
    
    # Probar cada ventana (comentar/descomentar según necesites)
    
    # 1. Crear Proyecto
    # window.showCreateProjectDialog(r"C:\Users\Jesus Quijada\Documents\GitHub\test_project")
    
    # 2. Instalar Carpeta
    # window.showInstallFolderDialog(r"C:\Users\Jesus Quijada\Documents\GitHub\packagemaker")
    
    # 3. Compilar Proyecto
    # window.showCompileDialog(r"C:\Users\Jesus Quijada\Documents\GitHub\packagemaker")
    
    # 4. Reparar Proyecto (MoonFix)
    # window.showRepairDialog(r"C:\Users\Jesus Quijada\Documents\GitHub\packagemaker")
    
    # 5. Instalar Paquete .iflapp
    # window.showInstallPackageDialog(r"C:\Users\Jesus Quijada\Documents\test.iflapp")
    
    # 6. Crear Archivo MEXF
    # window.showCreateMexfDialog(r"C:\Users\Jesus Quijada\Documents\GitHub\packagemaker")
    
    # 7. Instalar Extensiones MEXF
    # window.showInstallMexfDialog(r"C:\Users\Jesus Quijada\Documents\GitHub\packagemaker\example.mexf")
    
    # 8. Abrir Paquete
    # window.openPackageFile(r"C:\Users\Jesus Quijada\Documents\test.iflapp")
    
    # 9. Editor MEXF
    # window.openMexfEditor(r"C:\Users\Jesus Quijada\Documents\GitHub\packagemaker\example.mexf")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    print("=== Test de Ventanas IPM ===")
    print("Descomenta las líneas en test_ventanas() para probar cada ventana")
    print("=" * 50)
    test_ventanas()
