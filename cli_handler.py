#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CLI Handler for Influent Package Maker
Maneja los argumentos de línea de comandos y lanza la GUI apropiada
"""

import sys
import os
import argparse
from pathlib import Path

class CLIHandler:
    """Maneja los argumentos de línea de comandos"""
    
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Influent Package Maker - Sistema de gestión de paquetes Fluthin'
        )
        self._setup_arguments()
    
    def _setup_arguments(self):
        """Configura los argumentos de línea de comandos"""
        self.parser.add_argument(
            '--create-project',
            metavar='PATH',
            help='Crear un nuevo proyecto en la ruta especificada'
        )
        self.parser.add_argument(
            '--install-folder',
            metavar='PATH',
            help='Instalar una carpeta como Fluthin Package'
        )
        self.parser.add_argument(
            '--compile-project',
            metavar='PATH',
            help='Compilar un proyecto existente'
        )
        self.parser.add_argument(
            '--repair-project',
            metavar='PATH',
            help='Reparar un proyecto usando MoonFix'
        )
        self.parser.add_argument(
            '--install-package',
            metavar='FILE',
            help='Instalar un archivo .iflapp'
        )
        self.parser.add_argument(
            '--open-package',
            metavar='FILE',
            help='Abrir un paquete con IPM'
        )
        self.parser.add_argument(
            '--install-mexf',
            metavar='FILE',
            help='Instalar extensiones desde un archivo .mexf'
        )
        self.parser.add_argument(
            '--edit-mexf',
            metavar='FILE',
            help='Editar un archivo .mexf'
        )
        self.parser.add_argument(
            '--create-mexf',
            metavar='PATH',
            help='Crear un nuevo archivo .mexf en la ruta especificada'
        )
        self.parser.add_argument(
            '--install-shell',
            action='store_true',
            help='Instalar integración con el shell de Windows'
        )
        self.parser.add_argument(
            '--uninstall-shell',
            action='store_true',
            help='Desinstalar integración con el shell de Windows'
        )
        self.parser.add_argument(
            '--create-shortcuts',
            action='store_true',
            help='Crear accesos directos en el sistema'
        )
    
    def parse(self):
        """Parsea los argumentos y retorna el resultado"""
        return self.parser.parse_args()
    
    def has_cli_args(self):
        """Verifica si se pasaron argumentos de línea de comandos"""
        return len(sys.argv) > 1
    
    def get_action(self, args):
        """Determina qué acción ejecutar basándose en los argumentos"""
        if args.create_project:
            return ('create_project', args.create_project)
        elif args.install_folder:
            return ('install_folder', args.install_folder)
        elif args.compile_project:
            return ('compile_project', args.compile_project)
        elif args.repair_project:
            return ('repair_project', args.repair_project)
        elif args.install_package:
            return ('install_package', args.install_package)
        elif args.open_package:
            return ('open_package', args.open_package)
        elif args.install_mexf:
            return ('install_mexf', args.install_mexf)
        elif args.edit_mexf:
            return ('edit_mexf', args.edit_mexf)
        elif args.create_mexf:
            return ('create_mexf', args.create_mexf)
        elif args.install_shell:
            return ('install_shell', None)
        elif args.uninstall_shell:
            return ('uninstall_shell', None)
        elif args.create_shortcuts:
            return ('create_shortcuts', None)
        else:
            return (None, None)


def handle_cli_action(action, data, gui_class):
    """
    Maneja una acción de CLI y lanza la GUI apropiada
    
    Args:
        action: Tipo de acción a ejecutar
        data: Datos asociados a la acción (ruta, archivo, etc.)
        gui_class: Clase de la GUI principal
    
    Returns:
        Instancia de la GUI configurada para la acción
    """
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Crear instancia de la GUI
    window = gui_class()
    
    # Configurar la GUI según la acción
    if action == 'create_project':
        window.switch_page(0)  # Ir a la pestaña de crear proyecto
        if data:
            window.showCreateProjectDialog(data)
    
    elif action == 'install_folder':
        window.switch_page(2)  # Ir a la pestaña de gestor
        if data:
            window.showInstallFolderDialog(data)
    
    elif action == 'compile_project':
        window.switch_page(1)  # Ir a la pestaña de construir
        if data:
            window.showCompileDialog(data)
    
    elif action == 'repair_project':
        window.switch_page(4)  # Ir a la pestaña de MoonFix
        if data:
            window.showRepairDialog(data)
    
    elif action == 'install_package':
        window.switch_page(2)  # Ir a la pestaña de gestor
        if data:
            window.showInstallPackageDialog(data)
    
    elif action == 'open_package':
        if data:
            window.openPackageFile(data)
    
    elif action == 'install_mexf':
        if data:
            window.showInstallMexfDialog(data)
    
    elif action == 'edit_mexf':
        if data:
            window.openMexfEditor(data)
    
    elif action == 'create_mexf':
        if data:
            window.showCreateMexfDialog(data)
    
    elif action == 'install_shell':
        from shell_integration import ShellIntegration
        shell = ShellIntegration()
        if shell.install_context_menus() and shell.install_mexf_support():
            print("Integración con shell instalada correctamente")
            return None
        else:
            print("Error al instalar integración con shell")
            return None
    
    elif action == 'uninstall_shell':
        from shell_integration import ShellIntegration
        shell = ShellIntegration()
        if shell.uninstall_context_menus():
            print("Integración con shell desinstalada correctamente")
            return None
        else:
            print("Error al desinstalar integración con shell")
            return None
    
    elif action == 'create_shortcuts':
        from shell_integration import ShellIntegration
        shell = ShellIntegration()
        if shell.create_shortcuts():
            print("Accesos directos creados correctamente")
            return None
        else:
            print("Error al crear accesos directos")
            return None
    
    return window
