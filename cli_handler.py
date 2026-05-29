# -*- coding: utf-8 -*-
"""
CLI handler for Influent Package Maker.
This is a library module, not an entry point.
"""

import sys
import os
import argparse

# Constantes
__version__ = "2.0.0"

# Mapeo de comandos legacy a acciones modernas
LEGACY_COMMAND_MAP = {
    '--install-shell': ('shellpatch_install', None),
    '--uninstall-shell': ('shellpatch_remove', None),
    '--create-shortcuts': ('shellpatch_shortcuts', None),
}


class CLIHandler:
    """Maneja los argumentos de línea de comandos."""

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Influent Package Maker - Sistema de gestión de paquetes Fluthin',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Ejemplos:
  packagemaker.py --create-project "C:/Proyectos/MiApp"
  packagemaker.py --repair-project "C:/Proyectos/MiApp"
  packagemaker.py --shellpatch install
  packagemaker.py --version
            """
        )
        self._setup_arguments()

    def _setup_arguments(self):
        """Configura todos los argumentos CLI."""
        # === Comandos de Proyecto ===
        project_group = self.parser.add_argument_group('Comandos de Proyecto')
        project_group.add_argument('--create-project', metavar='PATH', 
                                   help='Crear un nuevo proyecto en la ruta especificada')
        project_group.add_argument('--compile-project', metavar='PATH', 
                                   help='Compilar un proyecto existente')
        project_group.add_argument('--repair-project', metavar='PATH', 
                                   help='Reparar un proyecto usando MoonFix')
        project_group.add_argument('--install-folder', metavar='PATH', 
                                   help='Instalar una carpeta como Fluthin Package')
        
        # === Comandos de Paquetes ===
        package_group = self.parser.add_argument_group('Comandos de Paquetes')
        package_group.add_argument('--install-package', metavar='FILE', 
                                   help='Instalar un archivo .iflapp')
        package_group.add_argument('--open-package', metavar='FILE', 
                                   help='Abrir un paquete con IPM')
        
        # === Comandos de Extensiones ===
        mexf_group = self.parser.add_argument_group('Comandos de Extensiones (MEXF)')
        mexf_group.add_argument('--install-mexf', metavar='FILE', 
                                help='Instalar extensiones desde un archivo .mexf')
        mexf_group.add_argument('--edit-mexf', metavar='FILE', 
                                help='Editar un archivo .mexf')
        mexf_group.add_argument('--create-mexf', metavar='PATH', 
                                help='Crear un nuevo archivo .mexf')
        
        # === Shell Integration ===
        shell_group = self.parser.add_argument_group('Integración con Shell')
        shell_group.add_argument('--shellpatch', metavar='ACTION', 
                                 choices=['install', 'remove', 'shortcuts'], 
                                 help='Gestión de integración shell: install, remove, shortcuts')
        # Legacy (deprecated)
        shell_group.add_argument('--install-shell', action='store_true', 
                                 help=argparse.SUPPRESS)  # Legacy, oculto
        shell_group.add_argument('--uninstall-shell', action='store_true', 
                                 help=argparse.SUPPRESS)  # Legacy, oculto
        shell_group.add_argument('--create-shortcuts', action='store_true', 
                                 help=argparse.SUPPRESS)  # Legacy, oculto
        
        # === Opciones de Modo ===
        mode_group = self.parser.add_argument_group('Opciones de Modo')
        mode_group.add_argument('--compact', action='store_true', 
                                help='Ejecutar en modo compacto para invocaciones de shell')
        mode_group.add_argument('--shell-mode', action='store_true', 
                                help='Ejecutar en modo shell integrado')
        
        # === Información ===
        info_group = self.parser.add_argument_group('Información')
        info_group.add_argument('--version', action='store_true', 
                                help='Mostrar la versión de la aplicación')

    def parse(self):
        """Parsea los argumentos de línea de comandos."""
        return self.parser.parse_args()

    def has_cli_args(self):
        """Verifica si hay argumentos CLI."""
        return len(sys.argv) > 1

    def get_action(self, args):
        """
        Determina la acción a ejecutar basada en los argumentos.
        Retorna: (action_name, data, action_options)
        """
        # Opciones comunes para todas las acciones GUI
        gui_options = {'compact': args.compact, 'shell_mode': args.shell_mode}
        # Opciones para acciones shell (sin GUI)
        shell_options = {'compact': False, 'shell_mode': False}
        
        # === Acciones de Proyecto ===
        if args.create_project:
            return ('create_project', args.create_project, gui_options)
        elif args.compile_project:
            return ('compile_project', args.compile_project, gui_options)
        elif args.repair_project:
            return ('repair_project', args.repair_project, gui_options)
        elif args.install_folder:
            return ('install_folder', args.install_folder, gui_options)
        
        # === Acciones de Paquetes ===
        elif args.install_package:
            return ('install_package', args.install_package, gui_options)
        elif args.open_package:
            return ('open_package', args.open_package, gui_options)
        
        # === Acciones de Extensiones ===
        elif args.install_mexf:
            return ('install_mexf', args.install_mexf, gui_options)
        elif args.edit_mexf:
            return ('edit_mexf', args.edit_mexf, gui_options)
        elif args.create_mexf:
            return ('create_mexf', args.create_mexf, gui_options)
        
        # === Shell Integration (con --shellpatch) ===
        elif args.shellpatch == 'install':
            return ('shellpatch_install', None, shell_options)
        elif args.shellpatch == 'remove':
            return ('shellpatch_remove', None, shell_options)
        elif args.shellpatch == 'shortcuts':
            return ('shellpatch_shortcuts', None, shell_options)
        
        # === Legacy Shell Integration (deprecated) ===
        elif args.install_shell:
            print("[AVISO] --install-shell está deprecated, use --shellpatch install")
            return ('shellpatch_install', None, shell_options)
        elif args.uninstall_shell:
            print("[AVISO] --uninstall-shell está deprecated, use --shellpatch remove")
            return ('shellpatch_remove', None, shell_options)
        elif args.create_shortcuts:
            print("[AVISO] --create-shortcuts está deprecated, use --shellpatch shortcuts")
            return ('shellpatch_shortcuts', None, shell_options)
        
        # === Versión ===
        elif args.version:
            return ('show_version', None, shell_options)
        
        # Sin acción
        else:
            return (None, None, shell_options)


# === Shell Integration Helper ===
class ShellIntegrationHelper:
    """Helper para manejar shell integration desde CLI sin import circular."""
    
    @staticmethod
    def _get_shell_integration():
        """Importa y retorna ShellIntegration con path correcto."""
        # Agregar directorio raíz al path para importar shell_integration
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        try:
            from shell_integration import ShellIntegration
            return ShellIntegration()
        except ImportError as e:
            print(f"[ERROR] No se pudo importar shell_integration: {e}")
            return None
    
    @classmethod
    def install(cls):
        shell = cls._get_shell_integration()
        if shell is None:
            return False
        try:
            result = shell.install_all()
            if result:
                print("[OK] Integración con shell instalada correctamente")
            else:
                print("[ERROR] Falló la instalación de la integración con shell")
            return result
        except Exception as e:
            print(f"[ERROR] {e}")
            return False
    
    @classmethod
    def uninstall(cls):
        shell = cls._get_shell_integration()
        if shell is None:
            return False
        try:
            result = shell.uninstall_all()
            if result:
                print("[OK] Integración con shell desinstalada correctamente")
            else:
                print("[ERROR] Falló la desinstalación de la integración con shell")
            return result
        except Exception as e:
            print(f"[ERROR] {e}")
            return False
    
    @classmethod
    def create_shortcuts(cls):
        shell = cls._get_shell_integration()
        if shell is None:
            return False
        try:
            result = shell.create_shortcuts()
            if result:
                print("[OK] Accesos directos creados correctamente")
            else:
                print("[ERROR] Falló la creación de accesos directos")
            return result
        except Exception as e:
            print(f"[ERROR] {e}")
            return False


# === Action Handlers ===
def _handle_shell_actions(action):
    """Maneja acciones de shell que no requieren GUI. Retorna True si se manejó."""
    if action == 'shellpatch_install':
        return ShellIntegrationHelper.install()
    
    elif action == 'shellpatch_remove':
        return ShellIntegrationHelper.uninstall()
    
    elif action == 'shellpatch_shortcuts':
        return ShellIntegrationHelper.create_shortcuts()
    
    elif action == 'show_version':
        print(f"Influent Package Maker v{__version__}")
        print("https://github.com/Influent-PackageMaker")
        return True
    
    return None  # No es acción de shell


def _handle_gui_actions(window, action, data):
    """Maneja acciones que requieren GUI."""
    action_map = {
        'create_project': (0, 'showCreateProjectDialog'),
        'install_folder': (2, 'showInstallFolderDialog'),
        'compile_project': (1, 'showCompileDialog'),
        'repair_project': (4, 'showRepairDialog'),
        'install_package': (2, 'showInstallPackageDialog'),
        'install_mexf': (None, 'showInstallMexfDialog'),
        'edit_mexf': (None, 'openMexfEditor'),
        'create_mexf': (None, 'showCreateMexfDialog'),
        'open_package': (None, 'openPackageFile'),
    }
    
    if action not in action_map:
        return False
    
    page_idx, method_name = action_map[action]
    
    # Cambiar página si aplica
    if page_idx is not None:
        window.switch_page(page_idx)
    
    # Llamar método con data si existe
    if data and hasattr(window, method_name):
        method = getattr(window, method_name)
        method(data)
    elif hasattr(window, method_name):
        method = getattr(window, method_name)
        method()
    
    return True


def handle_cli_action(action, data, gui_class, compact=False, shell_mode=False):
    """
    Maneja una acción CLI.
    
    Args:
        action: Nombre de la acción
        data: Datos asociados a la acción
        gui_class: Clase GUI a instanciar (None para acciones sin GUI)
        compact: Modo compacto
        shell_mode: Modo shell
    
    Returns:
        Instancia de ventana GUI o None
    """
    # Primero intentar manejar como acción de shell (sin GUI)
    shell_result = _handle_shell_actions(action)
    if shell_result is not None:
        # Es acción de shell, no requiere GUI
        return None
    
    # Si no es shell action, necesitamos GUI
    if gui_class is None:
        print(f"[ERROR] Acción '{action}' requiere GUI pero no se proporcionó clase")
        return None
    
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    window = gui_class(compact_mode=compact, shell_mode=shell_mode)
    
    # Manejar acción GUI
    if not _handle_gui_actions(window, action, data):
        print(f"[AVISO] Acción desconocida: {action}")
    
    return window
