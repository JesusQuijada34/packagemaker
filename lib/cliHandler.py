#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CLI handler for Influent Package Maker.
"""

import sys
import argparse

class CLIHandler:
    """Maneja los argumentos de línea de comandos."""

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Influent Package Maker - Sistema de gestión de paquetes Fluthin'
        )
        self._setup_arguments()

    def _setup_arguments(self):
        self.parser.add_argument('--create-project', metavar='PATH', help='Crear un nuevo proyecto en la ruta especificada')
        self.parser.add_argument('--install-folder', metavar='PATH', help='Instalar una carpeta como Fluthin Package')
        self.parser.add_argument('--compile-project', metavar='PATH', help='Compilar un proyecto existente')
        self.parser.add_argument('--headless', action='store_true', help='Ejecutar compilación en modo headless (sin GUI)')
        self.parser.add_argument('--output', metavar='PATH', help='Carpeta de salida para el modo headless')
        self.parser.add_argument('--platform', metavar='PLATFORM', choices=['Windows', 'Linux'], help='Plataforma objetivo para el modo headless')
        self.parser.add_argument('--repair-project', metavar='PATH', help='Reparar un proyecto usando MoonFix')
        self.parser.add_argument('--install-package', metavar='FILE', help='Instalar un archivo .iflapp')
        self.parser.add_argument('--open-package', metavar='FILE', help='Abrir un paquete con IPM')
        self.parser.add_argument('--install-mexf', metavar='FILE', help='Instalar extensiones desde un archivo .mexf')
        self.parser.add_argument('--edit-mexf', metavar='FILE', help='Editar un archivo .mexf')
        self.parser.add_argument('--create-mexf', metavar='PATH', help='Crear un nuevo archivo .mexf en la ruta especificada')
        self.parser.add_argument('--install-shell', action='store_true', help='Instalar integración con el shell de Windows')
        self.parser.add_argument('--uninstall-shell', action='store_true', help='Desinstalar integración con el shell de Windows')
        self.parser.add_argument('--create-shortcuts', action='store_true', help='Crear accesos directos en el sistema')
        self.parser.add_argument('--compact', action='store_true', help='Ejecutar en modo compacto para invocaciones de shell')
        self.parser.add_argument('--shell-mode', action='store_true', help='Ejecutar en modo shell integrado')
        self.parser.add_argument('--version', action='store_true', help='Mostrar la versión de la aplicación')

    def parse(self):
        return self.parser.parse_args()

    def has_cli_args(self):
        return len(sys.argv) > 1

    def get_action(self, args):
        if args.create_project:
            return ('create_project', args.create_project, {'compact': args.compact, 'shell_mode': args.shell_mode})
        elif args.install_folder:
            return ('install_folder', args.install_folder, {'compact': args.compact, 'shell_mode': args.shell_mode})
        elif args.compile_project:
            return ('compile_project', args.compile_project, {
                'compact': args.compact, 
                'shell_mode': args.shell_mode,
                'headless': args.headless,
                'output': args.output,
                'platform': args.platform
            })
        elif args.repair_project:
            return ('repair_project', args.repair_project, {'compact': args.compact, 'shell_mode': args.shell_mode})
        elif args.install_package:
            return ('install_package', args.install_package, {'compact': args.compact, 'shell_mode': args.shell_mode})
        elif args.open_package:
            return ('open_package', args.open_package, {'compact': args.compact, 'shell_mode': args.shell_mode})
        elif args.install_mexf:
            return ('install_mexf', args.install_mexf, {'compact': args.compact, 'shell_mode': args.shell_mode})
        elif args.edit_mexf:
            return ('edit_mexf', args.edit_mexf, {'compact': args.compact, 'shell_mode': args.shell_mode})
        elif args.create_mexf:
            return ('create_mexf', args.create_mexf, {'compact': args.compact, 'shell_mode': args.shell_mode})
        elif args.install_shell:
            return ('install_shell', None, {'compact': False, 'shell_mode': False})
        elif args.uninstall_shell:
            return ('uninstall_shell', None, {'compact': False, 'shell_mode': False})
        elif args.create_shortcuts:
            return ('create_shortcuts', None, {'compact': False, 'shell_mode': False})
        else:
            return (None, None, {'compact': False, 'shell_mode': False})


def handle_cli_action(action, data, gui_class, compact=False, shell_mode=False, **kwargs):
    if kwargs.get('headless') or action in ['shellpatch_install', 'shellpatch_remove', 'shellpatch_shortcuts', 'install_shell', 'uninstall_shell', 'create_shortcuts']:
        # No instanciar GUI para estas acciones
        pass
    else:
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

    window = gui_class(compact_mode=compact, shell_mode=shell_mode) if gui_class else None

    if action == 'create_project':
        window.switch_page(0)
        if data:
            window.showCreateProjectDialog(data)

    elif action == 'install_folder':
        window.switch_page(2)
        if data:
            window.showInstallFolderDialog(data)

    elif action == 'compile_project':
        if kwargs.get('headless'):
            # Lógica headless sin necesidad de GUI
            from lib.BuildThread import FlangCompiler
            from pathlib import Path
            project_path = Path(data).resolve()
            output_path = Path(kwargs.get('output') or './dist').resolve()
            target_platform = kwargs.get('platform') or ("Windows" if sys.platform.startswith('win') else "Linux")
            
            print(f"🚀 Iniciando compilación headless...")
            compiler = FlangCompiler(project_path, output_path, log_callback=print)
            if not compiler.parse_details_xml():
                sys.exit(1)
            if not compiler.find_scripts():
                sys.exit(1)
            if not compiler.compile_binaries(target_platform):
                sys.exit(1)
            if not compiler.create_package(target_platform):
                sys.exit(1)
            
            publisher = compiler.metadata['publisher']
            app = compiler.metadata['app']
            version = compiler.metadata['version']
            platform_suffix = "Knosthalij" if target_platform == "Windows" else "Danenone"
            package_path = output_path / f"{publisher}.{app}.{version}.{platform_suffix}"
            iflapp_file = output_path / f"{publisher}.{app}.{version}.{platform_suffix}.iflapp"
            
            if not compiler.compress_to_iflapp(package_path, iflapp_file):
                sys.exit(1)
            print(f"✨ Proceso completado con éxito: {iflapp_file}")
            return None

        window.switch_page(1)
        if data:
            window.showCompileDialog(data)

    elif action == 'repair_project':
        window.switch_page(4)
        if data:
            window.showRepairDialog(data)

    elif action == 'install_package':
        window.switch_page(2)
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
        from shell.shellIntegration import ShellIntegration
        shell = ShellIntegration()
        if shell.install_context_menus() and shell.install_mexf_support():
            print("Integración con shell instalada correctamente")
            return None
        print("Error al instalar integración con shell")
        return None

    elif action == 'uninstall_shell':
        from shell.shellIntegration import ShellIntegration
        shell = ShellIntegration()
        if shell.uninstall_all():
            print("Integración con shell desinstalada correctamente")
            return None
        print("Error al desinstalar integración con shell")
        return None

    elif action == 'create_shortcuts':
        from shell.shellIntegration import ShellIntegration
        shell = ShellIntegration()
        if shell.create_shortcuts():
            print("Accesos directos creados correctamente")
            return None
        print("Error al crear accesos directos")
        return None

    return window
