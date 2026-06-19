#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CLI handler for Influent Package Maker.
This is a library module, not an entry point.
"""

import os
import sys
import argparse
from pathlib import Path

# Constantes
import xml.etree.ElementTree as ET

with open(Path(__file__).parent / "../details.xml", "r") as f:
    tree = ET.parse(f)
    root_xml = tree.getroot()
    __version__ = root_xml.find("version").text

# Mapeo de comandos legacy a acciones modernas
LEGACY_COMMAND_MAP = {
    '--install-shell': ('shellpatch_install', None),
    '--uninstall-shell': ('shellpatch_remove', None),
    '--create-shortcuts': ('shellpatch_shortcuts', None),
}

class CLIHandler:
    """Maneja los argumentos de línea de comandos."""

    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.join(os.path.expanduser("~"), "Documents", "Packagemaker Projects")
        self.parser = argparse.ArgumentParser(
            description=f'\033[94mInfluent Package Maker - Sistema de gestión de paquetes Fluthin\033[0m',
            epilog=f"""
\033[96mEjemplos:\033[0m
  \033[1m\033[94mpython packagemaker.py create --name "Mi App" --shortname "mi-app" --author "GitHub" --publisher "Tesla-Inc" --version "1.0" --platform win\033[0m
  \033[1m\033[94mpython packagemaker.py compile --name "Mi App" --shortname "mi-app" --author "GitHub" --publisher "Tesla-Inc" --version "1.0"\033[0m
  \033[1m\033[94mpython packagemaker.py moonfix --name "Mi App" --shortname "mi-app" --author "GitHub" --publisher "Tesla-Inc" --version "1.0"\033[0m
  \033[1m\033[94mpython packagemaker.py --shellpatch install\033[0m
  \033[1m\033[94mpython packagemaker.py --app-version\033[0m
""",
            formatter_class=argparse.RawTextHelpFormatter
        )
        self._setup_arguments()

    def _setup_arguments(self):
        # === Opciones de Modo ===
        mode_group = self.parser.add_argument_group('Opciones de Modo')
        mode_group.add_argument('--compact', action='store_true', help='Ejecutar en modo compacto para invocaciones de shell')
        mode_group.add_argument('--shell-mode', action='store_true', help='Ejecutar en modo shell integrado')
        mode_group.add_argument('--headless', action='store_true', help='Ejecutar en modo headless (sin GUI)')
        mode_group.add_argument('--tui', action='store_true', help='Iniciar interfaz de texto (TUI) en la terminal')

        # === Información ===
        info_group = self.parser.add_argument_group('Información')
        info_group.add_argument('--app-version', action='store_true', help='Mostrar la versión de la aplicación')
        info_group.add_argument('--version-update', action='store_true', help='Actualizar la versión usando la lógica del updater')

        # === Subparsers modernos ===
        subparsers = self.parser.add_subparsers(dest='command', help='Comandos principales')

        create_parser = subparsers.add_parser('create', help='Crear un nuevo proyecto en la ruta predeterminada')
        create_parser.add_argument('--name', required=True, help='Nombre del proyecto (ej: "Mi App")')
        create_parser.add_argument('--shortname', required=True, help='Nombre corto del proyecto (ej: "mi-app")')
        create_parser.add_argument('--author', default='Unknown', help='Autor del proyecto (ej: "GitHub")')
        create_parser.add_argument('--publisher', help='Publisher o empresa del proyecto (ej: "Tesla-Inc")')
        create_parser.add_argument('--version', default='1.0.0', help='Versión del proyecto (ej: "1.0")')
        create_parser.add_argument('--platform', default='win', choices=['win', 'linux', 'all'], help='Plataforma objetivo: win, linux, all')
        create_parser.add_argument('--description', default='Proyecto creado con Influent Package Maker', help='Descripción para details.xml')
        create_parser.add_argument('--headless', action='store_true', help='Crear el proyecto sin abrir la UI')

        compile_parser = subparsers.add_parser('compile', help='Compilar un proyecto en la ruta predeterminada')
        compile_parser.add_argument('--name', required=True, help='Nombre del proyecto (ej: "Mi App")')
        compile_parser.add_argument('--shortname', required=True, help='Nombre corto del proyecto (ej: "mi-app")')
        compile_parser.add_argument('--author', default='Unknown', help='Autor del proyecto (ej: "GitHub")')
        compile_parser.add_argument('--publisher', help='Publisher o empresa del proyecto (ej: "Tesla-Inc")')
        compile_parser.add_argument('--version', default='1.0.0', help='Versión del proyecto (ej: "1.0")')
        compile_parser.add_argument('--optimize', action='store_true', help='Optimizar binarios después de compilar')
        compile_parser.add_argument('--scripts', help='Lista de scripts a compilar manualmente, separada por comas')

        repair_parser = subparsers.add_parser('moonfix', aliases=['repair'], help='Reparar un proyecto con MoonFix')
        repair_parser.add_argument('--name', required=True, help='Nombre del proyecto (ej: "Mi App")')
        repair_parser.add_argument('--shortname', required=True, help='Nombre corto del proyecto (ej: "mi-app")')
        repair_parser.add_argument('--author', default='Unknown', help='Autor del proyecto (ej: "GitHub")')
        repair_parser.add_argument('--publisher', help='Publisher o empresa del proyecto (ej: "Tesla-Inc")')
        repair_parser.add_argument('--version', default='1.0.0', help='Versión del proyecto (ej: "1.0")')

        # === Shell Integration ===
        shell_group = self.parser.add_argument_group('Integración con Shell')
        shell_group.add_argument('--shellpatch', metavar='ACTION', choices=['install', 'remove', 'shortcuts'], help='Gestión de integración shell: install, remove, shortcuts')

    def parse(self):
        return self.parser.parse_args()

    def has_cli_args(self):
        return len(sys.argv) > 1

    def _normalize_target_platform(self, platform_value):
        """Normaliza plataforma de destino (win/linux/all -> Windows/Linux/None)"""
        if not platform_value:
            if sys.platform.startswith('darwin'):
                return 'Linux'
            if sys.platform.startswith('win'):
                return 'Windows'
            if sys.platform.startswith('linux'):
                return 'Linux'
        p = str(platform_value).strip().lower()
        if p in ('auto', 'default'):
            return None
        if p in ('win', 'windows', 'knosthalij'):
            return 'Windows'
        if p in ('linux', 'danenone'):
            return 'Linux'
        if p in ('all', 'multi', 'multicube', 'alphacube', 'alpha'):
            return None
        return 'Windows' if 'win' in p else 'Linux' if 'lin' in p else None

    def _normalize_project_platform(self, platform_value):
        """Normaliza plataforma de proyecto (win/linux/all -> Knosthalij/Danenone/AlphaCube)"""
        if not platform_value:
            if sys.platform.startswith('win'):
                return 'Knosthalij'
            elif sys.platform.startswith('linux'):
                return 'Danenone'
            else:
                return 'AlphaCube'
        p = str(platform_value).strip().lower()
        if p in ('win', 'windows', 'knosthalij'):
            return 'Knosthalij'
        if p in ('linux', 'danenone'):
            return 'Danenone'
        if p in ('all', 'multi', 'multiplataforma', 'alphacube', 'alpha'):
            return 'AlphaCube'
        return platform_value

    def get_action(self, args):
        """
        Determina la acción a ejecutar basada en los argumentos.
        Retorna: (action_name, data, action_options)
        """
        # Opciones comunes para todas las acciones GUI
        gui_options = {'compact': args.compact, 'shell_mode': args.shell_mode}
        # Opciones para acciones shell (sin GUI)
        shell_options = {'compact': False, 'shell_mode': False}
        
        # === Subparsers modernos ===
        if getattr(args, 'command', None) == 'create':
            target_platform = self._normalize_project_platform(getattr(args, 'platform', None))
            return (
                'create_project',
                {
                    'path': self.base_dir,  # Usar ruta predeterminada
                    'name': getattr(args, 'name', None),
                    'shortname': getattr(args, 'shortname', None),
                    'version': getattr(args, 'version', '1.0.0'),
                    'author': getattr(args, 'author', 'Unknown'),
                    'publisher': getattr(args, 'publisher', None),
                    'description': getattr(args, 'description', 'Proyecto creado con Influent Package Maker'),
                    'platform': target_platform,
                },
                {'compact': args.compact, 'shell_mode': args.shell_mode, 'headless': getattr(args, 'headless', False)}
            )
        elif getattr(args, 'command', None) == 'compile':
            return (
                'compile_project',
                {
                    'path': self.base_dir,  # Usar ruta predeterminada
                    'name': getattr(args, 'name', None),
                    'shortname': getattr(args, 'shortname', None),
                    'version': getattr(args, 'version', '1.0.0'),
                    'author': getattr(args, 'author', 'Unknown'),
                    'publisher': getattr(args, 'publisher', None),
                },
                {
                    'compact': args.compact,
                    'shell_mode': args.shell_mode,
                    'headless': getattr(args, 'headless', False),
                    'scripts': getattr(args, 'scripts', None),
                    'optimize': getattr(args, 'optimize', False),
                }
            )
        elif getattr(args, 'command', None) in ('moonfix', 'repair'):
            return (
                'repair_project',
                {
                    'path': self.base_dir,  # Usar ruta predeterminada
                    'name': getattr(args, 'name', None),
                    'shortname': getattr(args, 'shortname', None),
                    'version': getattr(args, 'version', '1.0.0'),
                    'author': getattr(args, 'author', 'Unknown'),
                    'publisher': getattr(args, 'publisher', None),
                },
                {
                    'compact': args.compact,
                    'shell_mode': args.shell_mode,
                    'headless': getattr(args, 'headless', False),
                },
            )
        
        # === Shell Integration (con --shellpatch) ===
        elif getattr(args, 'shellpatch', None) == 'install':
            return ('shellpatch_install', None, shell_options)
        elif getattr(args, 'shellpatch', None) == 'remove':
            return ('shellpatch_remove', None, shell_options)
        elif getattr(args, 'shellpatch', None) == 'shortcuts':
            return ('shellpatch_shortcuts', None, shell_options)
        
        # === Versión ===
        elif args.app_version:
            return ('show_version', None, shell_options)
        
        # === Version Update ===
        elif args.version_update:
            return ('version_update', None, shell_options)
        
        # Sin acción
        else:
            return (None, None, shell_options)


# === Shell Integration Helper ===
class ShellIntegrationHelper:
    """Helper para manejar shell integration desde CLI sin import circular."""
    
    @staticmethod
    def _get_shell_integration():
        """Importa y retorna ShellIntegration con path correcto."""
        try:
            from lib.shell_integration import ShellIntegration
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


# === Version Update Helper ===
class VersionUpdateHelper:
    """Helper para manejar actualización de versión usando la lógica del updater."""
    
    @staticmethod
    def update():
        """Ejecuta la actualización usando la lógica de updater.py"""
        try:
            # Importar updater.py
            import updater
            
            print("[INFO] Iniciando actualización de versión...")
            print("[INFO] Verificando actualizaciones disponibles...")
            
            # Ejecutar update_app con GUI (no silent)
            success = updater.update_app(silent=False, accept_license=False, cache_in_memory=True)
            
            if success:
                print("[OK] Actualización completada exitosamente")
                return True
            else:
                print("[INFO] No se encontraron actualizaciones o la actualización fue cancelada")
                return True  # Return True even if no update found, as it's not an error
                
        except Exception as e:
            print(f"[ERROR] Error durante la actualización: {e}")
            import traceback
            traceback.print_exc()
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
        print("https://github.com/JesusQuijada34/packagemaker")
        return True
    
    elif action == 'version_update':
        return VersionUpdateHelper.update()
    
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


def _find_project_path(base_dir, project_name=None):
    """
    Encuentra la ruta de un proyecto en base_dir.
    Si project_name es None, retorna el proyecto más reciente modificado.
    Si project_name es especificado, busca el proyecto que coincida con el nombre.
    """
    if not base_dir or not base_dir.exists():
        return None
    
    projects = []
    for item in base_dir.iterdir():
        if item.is_dir() and (item / 'details.xml').exists():
            projects.append((item, item.stat().st_mtime))
    
    if not projects:
        return None
    
    if project_name:
        # Buscar proyecto por nombre
        project_name_lower = project_name.lower()
        for project_path, _ in projects:
            if project_name_lower in project_path.name.lower():
                return project_path
        return None
    else:
        # Retornar el proyecto más reciente
        projects.sort(key=lambda x: x[1], reverse=True)
        return projects[0][0]


def handle_cli_action(action, data, gui_class, compact=False, shell_mode=False, **kwargs):
    """
    Maneja una acción CLI.
    
    Args:
        action: Nombre de la acción
        data: Datos asociados a la acción
        gui_class: Clase GUI a instanciar (None para acciones sin GUI)
        compact: Modo compacto
        shell_mode: Modo shell
        **kwargs: Opciones adicionales (headless, output, platform, etc.)
    
    Returns:
        Instancia de ventana GUI o None
    """
    # Primero intentar manejar como acción de shell (sin GUI)
    shell_result = _handle_shell_actions(action)
    if shell_result is not None:
        # Es acción de shell, no requiere GUI
        return None
    
    # Manejar acciones headless (create, compile, repair)
    if action == 'create_project' and kwargs.get('headless'):
        from lib.template_engine import create_project_from_templates, normalize_platform, build_variables
        project_source = data if isinstance(data, dict) else {'path': data}
        base_path = Path(project_source.get('path')).resolve()
        
        # Obtener valores de proyecto
        publisher = (project_source.get('publisher') or project_source.get('author') or 'influent').strip().lower().replace(' ', '-')
        app_id = project_source.get('shortname') or (project_source.get('name') or base_path.name).strip().lower().replace(' ', '-')
        version_base = str(project_source.get('version') or '1.0.0').strip().split('-')[0]
        platform_value = normalize_platform(project_source.get('platform')) if project_source.get('platform') else normalize_platform('Knosthalij')
        description = project_source.get('description') or 'Proyecto creado con Influent Package Maker'
        author_val = project_source.get('author') or 'Unknown'
        
        # Construir nombre de carpeta igual que la GUI: empresa.slug.vVERSION_FULL
        variables = build_variables(publisher, app_id, app_id, author_val, platform_value, version_base, description)
        folder_name = f"{publisher}.{app_id}.v{variables['VERSION_FULL']}"
        project_path = base_path / folder_name
        
        print(f"[INFO] Creando proyecto en: {project_path}")
        create_project_from_templates(
            project_path,
            publisher,
            app_id,
            app_id,
            author_val,
            platform_value,
            version_base=version_base,
            description=description,
        )
        
        # Copiar icono por defecto
        icon_dest = project_path / "app" / "app-icon.ico"
        icon_source = Path("app/app-icon.ico")
        if icon_source.exists():
            import shutil
            shutil.copy(str(icon_source), str(icon_dest))
            print(f"[OK] Icono copiado a: {icon_dest}")
        
        print(f"[OK] Proyecto creado correctamente: {project_path}")
        return None
    
    elif action == 'compile_project' and kwargs.get('headless'):
        from lib.BuildThread import FlangCompiler
        
        project_source = data if isinstance(data, dict) else {'path': data}
        base_path = Path(project_source.get('path')).resolve()
        
        # Construir nombre de carpeta para buscar el proyecto
        publisher = (project_source.get('publisher') or project_source.get('author') or 'influent').strip().lower().replace(' ', '-')
        app_id = project_source.get('shortname') or (project_source.get('name') or '').strip().lower().replace(' ', '-')
        version_base = str(project_source.get('version') or '1.0.0').strip().split('-')[0]
        
        # Buscar proyecto que coincida con el patrón
        project_path = None
        for item in base_path.iterdir():
            if item.is_dir() and (item / 'details.xml').exists():
                if publisher.lower() in item.name.lower() and app_id.lower() in item.name.lower():
                    project_path = item
                    break
        
        if not project_path:
            print(f"[ERROR] No se encontró proyecto que coincida con {publisher}.{app_id} en {base_path}")
            sys.exit(1)
        
        # Usar ruta predeterminada para salida (misma que usa la GUI)
        output_path = Path(os.path.expanduser("~")).resolve()
        if sys.platform.startswith('win'):
            output_path = output_path / "Documents" / "Packagemaker Projects" / "Compiled"
        else:
            output_path = output_path / "Documents" / "Packagemaker Projects" / "Compiled"
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Detectar plataforma automáticamente según el sistema operativo
        target_platform = 'Windows' if sys.platform.startswith('win') else 'Linux'
        scripts = kwargs.get('scripts')
        optimize = kwargs.get('optimize')

        print(f"[INFO] Iniciando compilación headless...")
        print(f"[INFO] Proyecto: {project_path}")
        print(f"[INFO] Salida: {output_path}")
        print(f"[INFO] Plataforma objetivo (detectada): {target_platform}")
        compiler = FlangCompiler(project_path, output_path, log_callback=print)
        if scripts:
            compiler.scripts_to_compile = [s.strip() for s in scripts.split(',') if s.strip()]

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
        if optimize:
            print("⚡ Optimización completada (opción headless no implementada en detalle).")
        print(f"✨ Proceso completado con éxito: {iflapp_file}")
        return None
    
    elif action == 'repair_project' and kwargs.get('headless'):
        from lib.template_engine import normalize_platform, repair_project_from_templates
        from xml.etree import ElementTree as ET
        
        project_source = data if isinstance(data, dict) else {'path': data}
        base_path = Path(project_source.get('path')).resolve()
        
        # Construir nombre de carpeta para buscar el proyecto
        publisher = (project_source.get('publisher') or project_source.get('author') or 'influent').strip().lower().replace(' ', '-')
        app_id = project_source.get('shortname') or (project_source.get('name') or '').strip().lower().replace(' ', '-')
        version_base = str(project_source.get('version') or '1.0.0').strip().split('-')[0]
        
        # Buscar proyecto que coincida con el patrón
        project_path = None
        for item in base_path.iterdir():
            if item.is_dir() and (item / 'details.xml').exists():
                if publisher.lower() in item.name.lower() and app_id.lower() in item.name.lower():
                    project_path = item
                    break
        
        if not project_path:
            print(f"[ERROR] No se encontró proyecto que coincida con {publisher}.{app_id} en {base_path}")
            sys.exit(1)
        
        details_path = project_path / 'details.xml'
        name = project_source.get('name') or project_path.name
        author = project_source.get('author') or 'Unknown'
        platform_value = None

        if details_path.exists():
            try:
                tree = ET.parse(details_path)
                root = tree.getroot()
                publisher = root.findtext('publisher') or root.findtext('empresa') or publisher
                app_id = root.findtext('app') or root.findtext('name') or app_id
                name = root.findtext('name') or name
                author = root.findtext('author') or root.findtext('autor') or author
                version_raw = (root.findtext('version') or version_base).strip().lstrip('v').split('-')[0] or version_base
                platform_value = normalize_platform(root.findtext('platform') or '')
            except Exception as e:
                print(f"⚠ Advertencia: no se pudo leer details.xml: {e}")

        if not platform_value:
            platform_value = 'Knosthalij'

        description = 'Proyecto reparado por MoonFix'
        print(f"[INFO] Ejecutando MoonFix para: {project_path}")
        print(f"[INFO] Plataforma objetivo (leída del paquete): {platform_value}")

        result = repair_project_from_templates(
            project_path,
            publisher,
            app_id,
            name,
            author,
            platform_value,
            version_base=version_base,
            description=description,
        )
        repaired_files = result.get('files', [])
        print(f"[OK] MoonFix completado. Archivos reparados/restaurados: {len(repaired_files)}")
        for item in repaired_files:
            print(f"  - {item}")
        return None
    
    # Si no es shell action ni headless, necesitamos GUI
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
    return window
