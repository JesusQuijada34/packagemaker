#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CLI handler for Influent Package Maker.
"""

import os
import sys
import argparse
from pathlib import Path

class CLIHandler:
    """Maneja los argumentos de línea de comandos."""

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Influent Package Maker - Sistema de gestión de paquetes Fluthin',
            epilog='Ejemplos:\n  python packagemaker.py create /home/user/projects --name MiApp --author "Jesús" --publisher "Influent" --platform Linux\n  python packagemaker.py compile /home/user/projects/MiApp --output ./dist --target Linux --headless\n  python packagemaker.py moonfix /home/user/projects/MiApp --platform Linux --headless'
        )
        self._setup_arguments()

    def _setup_arguments(self):
        self.parser.add_argument('--compact', action='store_true', help='Ejecutar en modo compacto para invocaciones de shell')
        self.parser.add_argument('--shell-mode', action='store_true', help='Ejecutar en modo shell integrado')
        self.parser.add_argument('--version', action='store_true', help='Mostrar la versión de la aplicación')

        subparsers = self.parser.add_subparsers(dest='command', help='Comandos principales')

        create_parser = subparsers.add_parser('create', help='Crear un proyecto desde la terminal')
        create_parser.add_argument('path', help='Ruta del proyecto o carpeta base donde se creará el proyecto')
        create_parser.add_argument('--name', help='Nombre del proyecto (si no se especifica, usa el nombre de la carpeta)')
        create_parser.add_argument('--project-version', default='1.0.0', help='Versión del proyecto')
        create_parser.add_argument('--author', default='Unknown', help='Autor del proyecto')
        create_parser.add_argument('--publisher', help='Publisher o empresa del proyecto')
        create_parser.add_argument('--description', default='Proyecto creado con Influent Package Maker', help='Descripción para details.xml')
        create_parser.add_argument('--project-platform', default='Knosthalij', choices=['Knosthalij', 'Danenone', 'AlphaCube', 'Windows', 'Linux', 'Multi'], help='Plataforma base del proyecto')
        create_parser.add_argument('--headless', action='store_true', help='Crear el proyecto sin abrir la UI')

        compile_parser = subparsers.add_parser('compile', help='Compilar un proyecto desde la terminal')
        compile_parser.add_argument('project', help='Ruta del proyecto a compilar')
        compile_parser.add_argument('--output', default='./dist', help='Carpeta de salida para paquetes (.iflapp)')
        compile_parser.add_argument('--target', default='Auto', choices=['Auto', 'Windows', 'Linux'], help='Plataforma objetivo; Auto detecta según el sistema y details.xml')
        compile_parser.add_argument('--optimize', action='store_true', help='Optimizar binarios después de compilar')
        compile_parser.add_argument('--scripts', help='Lista de scripts a compilar manualmente, separada por comas (si no se usa, detecta automáticamente)')
        compile_parser.add_argument('--headless', action='store_true', help='Compilar sin abrir la UI')

        repair_parser = subparsers.add_parser('moonfix', aliases=['repair'], help='Reparar un proyecto con MoonFix desde la terminal')
        repair_parser.add_argument('project', help='Ruta del proyecto a reparar')
        repair_parser.add_argument('--verify-files', action='store_true', help='Verificar archivos faltantes')
        repair_parser.add_argument('--update-config', action='store_true', help='Actualizar configuraciones antiguas')
        repair_parser.add_argument('--repair-structure', action='store_true', help='Reparar estructura de carpetas')
        repair_parser.add_argument('--check-deps', action='store_true', help='Verificar dependencias del proyecto')
        repair_parser.add_argument('--description', help='Descripción alternativa para el proyecto reparado')
        repair_parser.add_argument('--platform', choices=['Knosthalij', 'Danenone', 'AlphaCube', 'Windows', 'Linux', 'Multi'], help='Plataforma objetivo de MoonFix')
        repair_parser.add_argument('--headless', action='store_true', help='Reparar sin abrir la UI')

        self.parser.add_argument('--create-project', metavar='PATH', help='Crear un nuevo proyecto en la ruta especificada')
        self.parser.add_argument('--compile-project', metavar='PATH', help='Compilar un proyecto existente')
        self.parser.add_argument('--repair-project', metavar='PATH', help='Reparar un proyecto usando MoonFix')
        self.parser.add_argument('--install-folder', metavar='PATH', help='Instalar una carpeta como Fluthin Package')
        self.parser.add_argument('--install-package', metavar='FILE', help='Instalar un archivo .iflapp')
        self.parser.add_argument('--open-package', metavar='FILE', help='Abrir un paquete con IPM')
        self.parser.add_argument('--install-mexf', metavar='FILE', help='Instalar extensiones desde un archivo .mexf')
        self.parser.add_argument('--edit-mexf', metavar='FILE', help='Editar un archivo .mexf')
        self.parser.add_argument('--create-mexf', metavar='PATH', help='Crear un nuevo archivo .mexf en la ruta especificada')
        self.parser.add_argument('--install-shell', action='store_true', help='Instalar integración con el shell de Windows')
        self.parser.add_argument('--uninstall-shell', action='store_true', help='Desinstalar integración con el shell de Windows')
        self.parser.add_argument('--create-shortcuts', action='store_true', help='Crear accesos directos en el sistema')
        self.parser.add_argument('--headless', action='store_true', help='Ejecutar en modo headless (sin GUI)')
        self.parser.add_argument('--output', metavar='PATH', help='Carpeta de salida para el modo headless')
        self.parser.add_argument('--platform', metavar='PLATFORM', choices=['Windows', 'Linux'], help='Plataforma objetivo para el modo headless')

    def parse(self):
        return self.parser.parse_args()

    def has_cli_args(self):
        return len(sys.argv) > 1

    def _normalize_target_platform(self, platform_value):
        if not platform_value:
            return None
        p = str(platform_value).strip().lower()
        if p in ('auto', 'default'):
            return None
        if p in ('windows', 'knosthalij'):
            return 'Windows'
        if p in ('linux', 'danenone'):
            return 'Linux'
        if p in ('multi', 'multicube', 'alphacube', 'alpha'):
            return None
        return 'Windows' if 'win' in p else 'Linux' if 'lin' in p else None

    def _normalize_project_platform(self, platform_value):
        if not platform_value:
            return 'Knosthalij'
        p = str(platform_value).strip().lower()
        if p in ('windows', 'knosthalij'):
            return 'Knosthalij'
        if p in ('linux', 'danenone'):
            return 'Danenone'
        if p in ('multi', 'multiplataforma', 'alphacube', 'alpha'):
            return 'AlphaCube'
        return platform_value

    def get_action(self, args):
        if getattr(args, 'command', None) == 'create':
            target_platform = self._normalize_project_platform(getattr(args, 'project_platform', None))
            return (
                'create_project',
                {
                    'path': args.path,
                    'name': args.name,
                    'version': getattr(args, 'project_version', '1.0.0'),
                    'author': args.author,
                    'publisher': args.publisher,
                    'description': args.description,
                    'platform': target_platform,
                },
                {'compact': args.compact, 'shell_mode': args.shell_mode, 'headless': args.headless}
            )
        elif getattr(args, 'command', None) == 'compile':
            return (
                'compile_project',
                args.project,
                {
                    'compact': args.compact,
                    'shell_mode': args.shell_mode,
                    'headless': args.headless,
                    'output': args.output,
                    'platform': self._normalize_target_platform(getattr(args, 'target', None)),
                    'scripts': getattr(args, 'scripts', None),
                    'optimize': getattr(args, 'optimize', False),
                }
            )
        elif getattr(args, 'command', None) in ('moonfix', 'repair'):
            return (
                'repair_project',
                args.project,
                {
                    'compact': args.compact,
                    'shell_mode': args.shell_mode,
                    'headless': args.headless,
                    'verify_files': getattr(args, 'verify_files', False),
                    'update_config': getattr(args, 'update_config', False),
                    'repair_structure': getattr(args, 'repair_structure', False),
                    'check_deps': getattr(args, 'check_deps', False),
                    'description': args.description,
                    'platform': args.platform,
                },
            )
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
                'platform': args.platform,
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
        window = None
    else:
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        window = gui_class(compact_mode=compact, shell_mode=shell_mode) if gui_class else None

    if action == 'install_folder':
        if window and data:
            window.switch_page(2)
            window.showInstallFolderDialog(data)
        return window

    if action == 'create_project':
        if kwargs.get('headless'):
            from lib.template_engine import create_project_from_templates, normalize_platform
            project_source = data if isinstance(data, dict) else {'path': data}
            base_path = Path(project_source.get('path')).resolve()
            project_name = (project_source.get('name') or base_path.name).strip()
            if base_path.exists() and base_path.is_dir() and not project_source.get('name'):
                project_path = base_path / project_name
            else:
                project_path = base_path
            publisher = (project_source.get('publisher') or project_source.get('author') or 'influent').strip().lower().replace(' ', '-')
            app_id = project_name.strip().lower().replace(' ', '-')
            version_base = str(project_source.get('version') or '1.0.0').strip().split('-')[0]
            platform_value = normalize_platform(project_source.get('platform')) if project_source.get('platform') else normalize_platform('Knosthalij')
            description = project_source.get('description') or 'Proyecto creado con Influent Package Maker'

            print(f"🚀 Creando proyecto en: {project_path}")
            create_project_from_templates(
                project_path,
                publisher,
                app_id,
                project_name,
                project_source.get('author') or 'Unknown',
                platform_value,
                version_base=version_base,
                description=description,
            )
            print(f"✨ Proyecto creado correctamente: {project_path}")
            return None

        if window and data:
            window.switch_page(0)
            window.showCreateProjectDialog(data)
        return window

    if action == 'compile_project':
        if kwargs.get('headless'):
            from lib.BuildThread import FlangCompiler
            project_path = Path(data).resolve()
            output_path = Path(kwargs.get('output') or './dist').resolve()
            target_platform = kwargs.get('platform')
            scripts = kwargs.get('scripts')
            optimize = kwargs.get('optimize')

            print(f"🚀 Iniciando compilación headless...")
            print(f"📂 Proyecto: {project_path}")
            print(f"📦 Salida: {output_path}")
            compiler = FlangCompiler(project_path, output_path, log_callback=print)
            if scripts:
                compiler.scripts_to_compile = [s.strip() for s in scripts.split(',') if s.strip()]

            if not compiler.parse_details_xml():
                sys.exit(1)

            if target_platform is None:
                project_platform = compiler.metadata.get('platform', '').strip().lower()
                if project_platform in ('knosthalij', 'windows'):
                    target_platform = 'Windows'
                elif project_platform in ('danenone', 'linux'):
                    target_platform = 'Linux'
                else:
                    target_platform = 'Windows' if sys.platform.startswith('win') else 'Linux'
                print(f"🔎 Objetivo detectado automáticamente: {target_platform}")
            else:
                print(f"💻 Objetivo: {target_platform}")

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

        if window and data:
            window.switch_page(1)
            window.showCompileDialog(data)
        return window

    if action == 'repair_project':
        if kwargs.get('headless'):
            from lib.template_engine import normalize_platform, repair_project_from_templates
            from xml.etree import ElementTree as ET
            project_path = Path(data).resolve()
            details_path = project_path / 'details.xml'
            publisher = 'influent'
            app_id = project_path.name
            name = project_path.name
            author = 'Unknown'
            version_raw = '1.0.0'
            platform_value = None

            if details_path.exists():
                try:
                    tree = ET.parse(details_path)
                    root = tree.getroot()
                    publisher = root.findtext('publisher') or root.findtext('empresa') or publisher
                    app_id = root.findtext('app') or root.findtext('name') or app_id
                    name = root.findtext('name') or app_id
                    author = root.findtext('author') or root.findtext('autor') or author
                    version_raw = (root.findtext('version') or version_raw).strip().lstrip('v').split('-')[0] or version_raw
                    platform_value = normalize_platform(root.findtext('platform') or '')
                except Exception as e:
                    print(f"⚠ Advertencia: no se pudo leer details.xml: {e}")

            if kwargs.get('platform'):
                platform_value = normalize_platform(kwargs['platform'])
            if not platform_value:
                platform_value = 'Knosthalij'

            description = kwargs.get('description') or 'Proyecto reparado por MoonFix'
            print(f"🌙 Ejecutando MoonFix para: {project_path}")
            print(f"📌 Plataforma objetivo: {platform_value}")
            if kwargs.get('verify_files'):
                print("🔎 Verificando archivos faltantes...")
            if kwargs.get('update_config'):
                print("⚙️ Actualizando configuraciones antiguas...")
            if kwargs.get('repair_structure'):
                print("🏗️ Reparando estructura de carpetas...")
            if kwargs.get('check_deps'):
                print("📦 Verificando dependencias...")

            result = repair_project_from_templates(
                project_path,
                publisher,
                app_id,
                name,
                author,
                platform_value,
                version_base=version_raw,
                description=description,
            )
            repaired_files = result.get('files', [])
            print(f"✨ MoonFix completado. Archivos reparados/restaurados: {len(repaired_files)}")
            for item in repaired_files:
                print(f"  - {item}")
            return None

        if window and data:
            window.switch_page(4)
            window.showRepairDialog(data)
        return window

    if action == 'install_package':
        if window and data:
            window.switch_page(2)
            window.showInstallPackageDialog(data)
        return window

    if action == 'open_package':
        if window and data:
            window.openPackageFile(data)
        return window

    if action == 'install_mexf':
        if window and data:
            window.showInstallMexfDialog(data)
        return window

    if action == 'edit_mexf':
        if window and data:
            window.openMexfEditor(data)
        return window

    if action == 'create_mexf':
        if window and data:
            window.showCreateMexfDialog(data)
        return window

    if action == 'install_shell':
        from shell.shellIntegration import ShellIntegration
        shell = ShellIntegration()
        if shell.install_context_menus() and shell.install_mexf_support():
            print("Integración con shell instalada correctamente")
            return None
        print("Error al instalar integración con shell")
        return None

    if action == 'uninstall_shell':
        from shell.shellIntegration import ShellIntegration
        shell = ShellIntegration()
        if shell.uninstall_all():
            print("Integración con shell desinstalada correctamente")
            return None
        print("Error al desinstalar integración con shell")
        return None

    if action == 'create_shortcuts':
        from shell.shellIntegration import ShellIntegration
        shell = ShellIntegration()
        if shell.create_shortcuts():
            print("Accesos directos creados correctamente")
            return None
        print("Error al crear accesos directos")
        return None

    return window
