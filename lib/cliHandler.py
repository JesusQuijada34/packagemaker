#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CLI handler for Influent Package Maker.
This is a library module, not an entry point.
"""

import os
import sys
import argparse
import re
from pathlib import Path

# Constantes
import xml.etree.ElementTree as ET

from lib.projectNameFormatter import ProjectNameFormatter


def _safe_print(message, stream=None):
    """Imprime mensajes de forma segura incluso si la consola no soporta Unicode."""
    target = stream or sys.stdout
    if target is None:
        return

    mapping = {
        '✔': '[OK]',
        '✖': '[ERROR]',
        '⚠': '[WARN]',
        'ℹ': '[INFO]',
        '●': '*',
        '○': 'o',
        '›': '>',
    }

    safe_message = ''.join(mapping.get(char, char) for char in str(message))
    encoding = getattr(target, 'encoding', None) or 'utf-8'
    try:
        print(safe_message, file=target)
    except UnicodeEncodeError:
        fallback = safe_message.encode(encoding, errors='replace').decode(encoding, errors='replace')
        print(fallback, file=target)


def _find_details_xml() -> Path:
    """Localiza details.xml tanto en fuente como en bundles PyInstaller."""
    candidates = []
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        bundle_root = Path(sys._MEIPASS)
        candidates.extend((bundle_root / "_internal", bundle_root))
    candidates.extend((Path(__file__).resolve().parent.parent, Path.cwd()))
    for root in candidates:
        candidate = root / "details.xml"
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        "No se encontró details.xml en las raíces de recursos: "
        + ", ".join(str(path) for path in candidates)
    )


_DETAILS_XML_PATH = _find_details_xml()
with _DETAILS_XML_PATH.open("r", encoding="utf-8") as f:
    tree = ET.parse(f)
    root_xml = tree.getroot()
    __version__ = root_xml.findtext("version", "")


class CLIHandler:
    """Maneja los argumentos de línea de comandos."""

    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.join(os.path.expanduser("~"), "Documents", "Packagemaker Projects")
        self.parser = argparse.ArgumentParser(
            description='\033[94mInfluent Package Maker - Sistema de gestión de paquetes Fluthin\033[0m',
            epilog="""
\033[96mEjemplos:\033[0m
  \033[1m\033[94mpython packagemaker.py create --name "Mi App" --shortname "mi-app" --author "GitHub" --publisher "Tesla-Inc" --version "1.0" --platform win\033[0m
  \033[1m\033[94mpython packagemaker.py compile --name "Mi App" --shortname "mi-app" --author "GitHub" --publisher "Tesla-Inc" --version "1.0"\033[0m
  \033[1m\033[94mpython packagemaker.py moonfix --name "Mi App" --shortname "mi-app" --author "GitHub" --publisher "Tesla-Inc" --version "1.0"\033[0m
  \033[1m\033[94mpython packagemaker.py --shell-plan example.mexf\033[0m
  \033[1m\033[94mpython packagemaker.py --install-mexf-shell example.mexf\033[0m
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

        # === Shell Integration (declarada en .mexf) ===
        shell_group = self.parser.add_argument_group('Integración con Shell')
        shell_group.add_argument('--shell-plan', metavar='MEXF', help='Mostrar el plan de shell (asociaciones, menús, atajos) declarado en un .mexf o carpeta de proyecto')
        shell_group.add_argument('--shell-plan-json', action='store_true', help='Salida JSON para --shell-plan')
        shell_group.add_argument('--install-mexf-shell', metavar='MEXF', help='Instalar la integración de shell declarada en un .mexf')
        shell_group.add_argument('--uninstall-mexf-shell', metavar='MEXF', help='Retirar la integración de shell declarada en un .mexf')

        # === Compatibilidad legacy ===
        legacy_group = self.parser.add_argument_group('Compatibilidad legacy')
        legacy_group.add_argument(
            '--compile-project', metavar='PATH',
            help='Alias legacy de --buildthis para menús contextuales y shell integration'
        )

        # === Build This ===
        buildthis_group = self.parser.add_argument_group('Build This')
        buildthis_group.add_argument('--buildthis', nargs='?', const='.', metavar='PATH', help='Compilar el proyecto en la carpeta actual o en la ruta especificada')
        buildthis_group.add_argument('--output', metavar='PATH', help='Directorio externo para el artefacto `.iflapp`')
        buildthis_group.add_argument('--platform', choices=['Linux', 'Windows'], help='Plataforma objetivo; por defecto se detecta el sistema actual')
        try:
            from lib.blindcubeEngine.compilers import backend_names as _backend_names

            _compiler_choices = _backend_names()
        except Exception:
            _compiler_choices = ['nuitka', 'pyinstaller']
        buildthis_group.add_argument('--compiler', choices=_compiler_choices, help='Backend de compilación (por defecto: nuitka)')
        try:
            from lib.engines import compiler_engines as _compiler_engines

            _engine_choices = [e.id for e in _compiler_engines()]
        except Exception:
            _engine_choices = ['flatcube', 'blindcube']
        buildthis_group.add_argument('--engine', choices=_engine_choices, help='Motor de compilación explícito (flatcube v1 legacy o blindcube v2 estándar)')
        buildthis_group.add_argument('--password', metavar='PASS', help='Cifrar el payload del .iflapp con esta contraseña')
        buildthis_group.add_argument('--no-sandbox', action='store_true', help='Desactivar la verificación en sandbox virtualizado')
        buildthis_group.add_argument('--dropper', action='store_true', help='Generar además un dropper autoextraíble (.run)')
        buildthis_group.add_argument(
            '--harden', metavar='METHODS',
            help='Métodos de blindaje separados por comas: strip,upx,checksum,anti-debug,obfuscate,resource,sign,integrity,compile-only,rename-symbols (por defecto: todos)'
        )

        # === Inspección de paquetes ===
        inspect_group = self.parser.add_argument_group('Inspección de paquetes')
        inspect_group.add_argument('--inspect', metavar='IFLAPP', help='Leer cabecera, icono y detalles de un .iflapp sin descomprimir')
        inspect_group.add_argument('--inspect-json', action='store_true', help='Salida JSON para --inspect')
        inspect_group.add_argument('--inspect-extract', metavar='DIR', help='Extraer icono y detalles de la cabecera a DIR')
        inspect_group.add_argument('--shell-info', metavar='FILE', help='Metadatos de shell (hover) de un .iflapp/.asksome sin descifrar')
        inspect_group.add_argument('--shell-info-json', action='store_true', help='Salida JSON para --shell-info')
        inspect_group.add_argument('--shell-preview', metavar='DIR', help='Exportar la vista previa de icono a DIR junto con --shell-info')
        inspect_group.add_argument('--install-shell-integration', action='store_true', help='Registrar la asociación MIME y el generador de miniaturas del SO')
        inspect_group.add_argument('--list-compilers', action='store_true', help='Mostrar compiladores disponibles y su estado')
        inspect_group.add_argument('--list-engines', action='store_true', help='Mostrar los motores de Package Maker (MakeSelf / FlatCube v1 / BlindCube v2) y su estado')
        inspect_group.add_argument('--list-hardening', action='store_true', help='Mostrar métodos de blindaje disponibles y su estado')

        mexf_group = self.parser.add_argument_group('Proyectos .mexf')
        mexf_group.add_argument('--compile-mexf', metavar='PATH', help='Compilar un proyecto .mexf a un artefacto .asksome (carpeta con details.xml y .mexf/main.mexf)')
        mexf_group.add_argument('--mexf-output', metavar='FILE', help='Ruta del .asksome de salida para --compile-mexf')
        mexf_group.add_argument('--mexf-password', metavar='PASS', help='Cifra el payload del .asksome con esta contraseña')
        mexf_group.add_argument('--mexf-wrappers', action='store_true', help='Generar envoltorios de prueba de sintaxis y entorno junto al .asksome')
        mexf_group.add_argument('--install-asksome', metavar='FILE', help='Instalar un artefacto .asksome (extrae payload firmado y crea accesos directos)')
        mexf_group.add_argument('--uninstall-asksome', metavar='APP_ID', help='Desinstalar un .asksome instalado por su app id')
        mexf_group.add_argument('--install-root', metavar='DIR', help='Carpeta raíz de instalación para --install-asksome/--uninstall-asksome')
        mexf_group.add_argument('--asksome-password', metavar='PASS', help='Contraseña del payload cifrado para --install-asksome')
        mexf_group.add_argument('--removeme-binary', action='store_true', help='Generar además el removedor nativo removeme.exe/.elf al instalar')
        mexf_group.add_argument('--removeme-backend', choices=['nuitka', 'pyinstaller', 'zipapp', 'cxfreeze', 'pyoxidizer'], help='Backend para compilar el removedor nativo (por defecto: auto)')
        mexf_group.add_argument('--build-removeme', metavar='APP_ID', help='Compilar el removedor nativo de un .asksome ya instalado')
        mexf_group.add_argument('--list-asksome', action='store_true', help='Listar los artefactos .asksome instalados')
        mexf_group.add_argument('--no-shortcuts', action='store_true', help='No crear accesos directos al instalar')
        mexf_group.add_argument('--debug-mexf', metavar='MEXF', help='Depurar el plan de un .mexf: muestra cada comando y su punto de ruptura')
        mexf_group.add_argument('--debug-run', action='store_true', help='Ejecutar de verdad los comandos del plan (por defecto solo se simula)')
        mexf_group.add_argument('--debug-break', metavar='IDS', help='Puntos de ruptura separados por comas (ids de comando) para --debug-mexf')

        ide_group = self.parser.add_argument_group('IDE de proyectos iflapp')
        ide_group.add_argument('--ide-scan', metavar='PATH', help='Inspeccionar un proyecto iflapp: metadatos, guiones, .mexf e icono')
        ide_group.add_argument('--ide-scan-json', action='store_true', help='Salida JSON para --ide-scan')
        ide_group.add_argument('--ide-compile', metavar='PATH', help='Compilar los guiones de un proyecto iflapp con el backend elegido')
        ide_group.add_argument('--ide-backend', choices=['auto', 'nuitka', 'pyinstaller', 'zipapp', 'cxfreeze', 'pyoxidizer'], help='Backend para --ide-compile (por defecto: auto)')
        ide_group.add_argument('--ide-output', metavar='DIR', help='Carpeta de salida para --ide-compile (por defecto: <proyecto>/dist)')
        ide_group.add_argument('--ide-run', metavar='SCRIPT', help='Ejecutar un guion del proyecto y capturar su salida')
        ide_group.add_argument('--ide-debug', metavar='SCRIPT', help='Depurar un guion del proyecto por línea y listar las paradas')
        ide_group.add_argument('--ide-break', metavar='LINES', help='Líneas de ruptura separadas por comas para --ide-debug')

        font_group = self.parser.add_argument_group('Fuentes')
        font_group.add_argument('--list-fonts', action='store_true', help='Mostrar el estado de las fuentes de la interfaz')
        font_group.add_argument('--download-fonts', nargs='?', const='all', metavar='KEYS', help='Descargar fuentes (todas o lista separada por comas)')
        font_group.add_argument('--force-fonts', action='store_true', help='Forzar la redescarga aunque estén en caché')

    @staticmethod
    def _parse_hardening(value):
        """Convierte la lista de métodos de blindaje separada por comas.

        ``None`` desactiva el blindaje; ``'all'`` o una cadena vacía solicitan
        todos los métodos soportados.
        """
        if value is None:
            return None
        from lib.blindcubeEngine.hardening import method_names

        text = str(value).strip().lower()
        if text in ('', 'all', 'todos'):
            return method_names()
        requested = [part.strip() for part in text.split(',') if part.strip()]
        valid = set(method_names())
        return [name for name in requested if name in valid]

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
        
        # === Shell Integration (declarada en .mexf) ===
        elif getattr(args, 'shell_plan', None):
            return (
                'shell_plan',
                {
                    'path': args.shell_plan,
                    'json': getattr(args, 'shell_plan_json', False),
                },
                shell_options,
            )
        elif getattr(args, 'install_mexf_shell', None):
            return (
                'install_mexf_shell',
                {'path': args.install_mexf_shell},
                shell_options,
            )
        elif getattr(args, 'uninstall_mexf_shell', None):
            return (
                'uninstall_mexf_shell',
                {'path': args.uninstall_mexf_shell},
                shell_options,
            )
        
        # === Versión ===
        elif args.app_version:
            return ('show_version', None, shell_options)

        # === Inspección de paquetes ===
        elif getattr(args, 'inspect', None):
            return (
                'inspect_iflapp',
                {
                    'path': args.inspect,
                    'json': getattr(args, 'inspect_json', False),
                    'extract': getattr(args, 'inspect_extract', None),
                },
                shell_options,
            )

        elif getattr(args, 'list_compilers', False):
            return ('list_compilers', None, shell_options)

        elif getattr(args, 'list_engines', False):
            return ('list_engines', None, shell_options)

        elif getattr(args, 'shell_info', None):
            return (
                'shell_info',
                {
                    'path': args.shell_info,
                    'json': getattr(args, 'shell_info_json', False),
                    'preview': getattr(args, 'shell_preview', None),
                },
                shell_options,
            )

        elif getattr(args, 'install_shell_integration', False):
            return ('install_shell_integration', None, shell_options)

        elif getattr(args, 'list_hardening', False):
            return ('list_hardening', None, shell_options)

        elif getattr(args, 'list_fonts', False):
            return ('list_fonts', None, shell_options)

        elif getattr(args, 'compile_mexf', None):
            return (
                'compile_mexf',
                {
                    'path': args.compile_mexf,
                    'output': getattr(args, 'mexf_output', None),
                    'password': getattr(args, 'mexf_password', None),
                    'wrappers': getattr(args, 'mexf_wrappers', False),
                },
                shell_options,
            )

        elif getattr(args, 'install_asksome', None):
            return (
                'install_asksome',
                {
                    'path': args.install_asksome,
                    'root': getattr(args, 'install_root', None),
                    'shortcuts': not getattr(args, 'no_shortcuts', False),
                    'password': getattr(args, 'asksome_password', None),
                    'removeme_binary': getattr(args, 'removeme_binary', False),
                    'removeme_backend': getattr(args, 'removeme_backend', None),
                },
                shell_options,
            )

        elif getattr(args, 'build_removeme', None):
            return (
                'build_removeme',
                {
                    'app_id': args.build_removeme,
                    'root': getattr(args, 'install_root', None),
                    'backend': getattr(args, 'removeme_backend', None),
                },
                shell_options,
            )

        elif getattr(args, 'uninstall_asksome', None):
            return (
                'uninstall_asksome',
                {
                    'app_id': args.uninstall_asksome,
                    'root': getattr(args, 'install_root', None),
                },
                shell_options,
            )

        elif getattr(args, 'debug_mexf', None):
            return (
                'debug_mexf',
                {
                    'path': args.debug_mexf,
                    'execute': getattr(args, 'debug_run', False),
                    'breakpoints': getattr(args, 'debug_break', None),
                },
                shell_options,
            )

        elif getattr(args, 'list_asksome', False):
            return (
                'list_asksome',
                {'root': getattr(args, 'install_root', None)},
                shell_options,
            )

        elif getattr(args, 'ide_scan', None):
            return (
                'ide_scan',
                {
                    'path': args.ide_scan,
                    'as_json': getattr(args, 'ide_scan_json', False),
                },
                shell_options,
            )

        elif getattr(args, 'ide_compile', None):
            return (
                'ide_compile',
                {
                    'path': args.ide_compile,
                    'backend': getattr(args, 'ide_backend', None),
                    'output': getattr(args, 'ide_output', None),
                },
                shell_options,
            )

        elif getattr(args, 'ide_run', None):
            return (
                'ide_run',
                {
                    'path': args.ide_run,
                    'debug': False,
                    'breakpoints': None,
                },
                shell_options,
            )

        elif getattr(args, 'ide_debug', None):
            return (
                'ide_debug',
                {
                    'path': args.ide_debug,
                    'debug': True,
                    'breakpoints': getattr(args, 'ide_break', None),
                },
                shell_options,
            )

        elif getattr(args, 'download_fonts', None):
            return (
                'download_fonts',
                {
                    'keys': args.download_fonts,
                    'force': getattr(args, 'force_fonts', False),
                },
                shell_options,
            )
        
        # === Version Update ===
        elif args.version_update:
            return ('version_update', None, shell_options)
        
        # === Compatibilidad legacy: compile-project ===
        elif getattr(args, 'compile_project', None):
            return (
                'buildthis',
                {'path': args.compile_project},
                {
                    'compact': False,
                    'shell_mode': False,
                    'headless': True,
                    'output': getattr(args, 'output', None),
                    'platform': getattr(args, 'platform', None),
                    'compiler': getattr(args, 'compiler', None),
                    'engine': getattr(args, 'engine', None),
                    'password': getattr(args, 'password', None),
                    'sandbox': not getattr(args, 'no_sandbox', False),
                    'dropper': getattr(args, 'dropper', False),
                    'hardening': self._parse_hardening(getattr(args, 'harden', None)),
                }
            )

        # === Build This ===
        elif getattr(args, 'buildthis', None) is not None:
            project_path = getattr(args, 'buildthis', '.')
            # Si es '.', usar el directorio actual
            if project_path == '.':
                project_path = os.getcwd()
            return (
                'buildthis',
                {'path': project_path},
                {
                    'compact': False,
                    'shell_mode': False,
                    'headless': True,
                    'output': getattr(args, 'output', None),
                    'platform': getattr(args, 'platform', None),
                    'compiler': getattr(args, 'compiler', None),
                    'engine': getattr(args, 'engine', None),
                    'password': getattr(args, 'password', None),
                    'sandbox': not getattr(args, 'no_sandbox', False),
                    'dropper': getattr(args, 'dropper', False),
                    'hardening': self._parse_hardening(getattr(args, 'harden', None)),
                }
            )
        
        # Sin acción
        else:
            return (None, None, shell_options)


# === Shell Integration Helper (declarada en .mexf) ===
class MexfShellHelper:
    """Instala/inspecciona la integración de shell declarada en un ``.mexf``."""

    @staticmethod
    def plan(data):
        import json

        from lib.mexf_parser import MexfError
        from lib.mexf_shell import load_shell_plan

        try:
            plan = load_shell_plan(data['path'])
        except (MexfError, FileNotFoundError, OSError) as exc:
            print(f"[ERROR] No se pudo leer el plan de shell: {exc}")
            return False
        payload = plan.to_dict()
        if data.get('json'):
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return True
        print(f"Shell: {payload['name']}  ({payload['id']})")
        print(f"Asociaciones : {len(payload['file_associations'])}")
        for assoc in payload['file_associations']:
            print(f"  - {assoc['extension']}  {assoc['mime_type']}")
        print(f"Menús        : {len(payload['context_menus'])}")
        for menu in payload['context_menus']:
            print(f"  - [{menu['target']}] {menu['label']}")
        if payload['environments']:
            print(f"Entorno      : {len(payload['environments'])} variables")
        return True

    @staticmethod
    def _install_or_remove(action, data):
        from lib.mexf_parser import MexfError
        from lib.mexf_shell import install_plan, load_shell_plan, uninstall_plan

        try:
            plan = load_shell_plan(data['path'])
        except (MexfError, FileNotFoundError, OSError) as exc:
            print(f"[ERROR] No se pudo leer el plan de shell: {exc}")
            return False
        try:
            if action == 'install':
                result = install_plan(plan)
                verb = "escrito"
            else:
                result = uninstall_plan(plan)
                verb = "eliminado"
        except OSError as exc:
            print(f"[ERROR] {exc}")
            return False
        for path in result.get('written', result.get('removed', [])):
            print(f"[OK] {verb}: {path}")
        for skipped in result.get('skipped', []):
            print(f"[WARN] Omitido: {skipped}")
        return True

    @classmethod
    def install(cls, data):
        return cls._install_or_remove('install', data)

    @classmethod
    def uninstall(cls, data):
        return cls._install_or_remove('uninstall', data)


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


# === Compiler Report Helper ===
class CompilerReportHelper:
    """Lista los backends de compilación disponibles."""

    @staticmethod
    def report():
        from lib.blindcubeEngine.compilers import available_backends

        report = available_backends(log_callback=_safe_print)
        print("Compiladores disponibles:")
        for name, info in report.items():
            status = "OK" if info["available"] else "NO DISPONIBLE"
            print(f"  - {name:12s} {status:15s} {info['version']} ({info['display_name']})")
        return True


# === Engine Report Helper ===
class EngineReportHelper:
    """Lista los motores de Package Maker (MakeSelf / FlatCube v1 / BlindCube v2)."""

    @staticmethod
    def report():
        from lib.engines import describe_engines

        print("Motores de Package Maker:")
        for row in describe_engines():
            status = {"legacy": "LEGACY / SIN SOPORTE"}.get(row["status"], "ESTÁNDAR")
            print(
                f"  - {row['id']:10s} {row['name']:14s} {row['role']:10s} "
                f"{status:22s} py{row['python']} backend={row['backend']} formato={row['format']}"
            )
            print(f"      {row['notes']}")
        return True


# === Hardening Report Helper ===
class HardeningReportHelper:
    """Lista los métodos de blindaje disponibles."""

    @staticmethod
    def report():
        from lib.blindcubeEngine.hardening import available_methods, method_names

        status = available_methods()
        print("Métodos de blindaje disponibles:")
        for name in method_names():
            state = "OK" if status.get(name) else "SIN HERRAMIENTA"
            print(f"  - {name:12s} {state}")
        return True


# === Font Report Helper ===
class FontReportHelper:
    """Lista y descarga las fuentes de la interfaz."""

    @staticmethod
    def report():
        from lib.font_manager import available_fonts_report

        print("Fuentes de la interfaz:")
        for key, info in available_fonts_report().items():
            cache = "EN CACHÉ" if info["cached"] else "AUSENTE"
            registered = info["registered"] or "-"
            print(
                f"  - {key:14s} {info['family']:14s} {cache:9s} "
                f"licencia={info['license']:11s} registrada={registered}"
            )
        return True

    @staticmethod
    def download(data):
        from lib.font_manager import (
            FONT_REGISTRY,
            ensure_fonts,
            write_license_notice,
        )

        raw = (data or {}).get("keys") or "all"
        text = str(raw).strip().lower()
        if text in ("", "all", "todas"):
            keys = list(FONT_REGISTRY)
        else:
            keys = [part.strip() for part in text.split(",") if part.strip()]
            unknown = [key for key in keys if key not in FONT_REGISTRY]
            if unknown:
                print(f"[ERROR] Fuentes desconocidas: {', '.join(unknown)}")
                print(f"        Disponibles: {', '.join(FONT_REGISTRY)}")
                return False

        force = bool((data or {}).get("force"))
        print(f"Descargando {len(keys)} fuente(s) desde Google Fonts...")
        results = ensure_fonts(
            keys,
            download=True,
            force=force,
            log_callback=_safe_print,
        )
        ok = [key for key, path in results.items() if path]
        missing = [key for key, path in results.items() if not path]
        if ok:
            notice = write_license_notice()
            print(f"[OK] Fuentes disponibles: {', '.join(ok)}")
            print(f"[OK] Aviso de licencias: {notice}")
        if missing:
            print(f"[WARN] No se pudieron obtener: {', '.join(missing)}")
        return not missing


# === Package Inspect Helper ===
class PackageInspectHelper:
    """Lee la cabecera de un .iflapp sin descomprimir ni descifrar."""

    @staticmethod
    def inspect(data):
        import json as _json

        from lib.blindcubeEngine import iflapp_format

        path = data.get("path")
        if not path:
            print("[ERROR] Debes indicar la ruta del .iflapp con --inspect")
            return False
        try:
            header = iflapp_format.read_iflapp_header(path)
        except Exception as exc:
            print(f"[ERROR] No se pudo leer la cabecera: {exc}")
            return False

        identity = header.identity()
        if data.get("json"):
            print(
                _json.dumps(
                    {
                        "identity": identity,
                        "format_version": header.format_version,
                        "compression": header.compression,
                        "encryption": header.encryption,
                        "file_count": header.file_count,
                        "icon_bytes": len(header.icon),
                        "details": header.details_text(),
                        "manifest": header.manifest,
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            )
        else:
            print(f"Paquete   : {path}")
            print(f"Formato   : iflapp v{header.format_version} ({header.compression}/{header.encryption})")
            print(f"Publisher : {identity['publisher']}")
            print(f"App       : {identity['app']}  ({identity['name']})")
            print(f"Version   : {identity['version']}")
            print(f"Autor     : {identity['author']}")
            print(f"Plataforma: {identity['platform']}")
            print(f"Icono     : {len(header.icon)} bytes")
            print(f"Archivos  : {header.file_count}")
            print("Detalles  :")
            for line in header.details_text().splitlines():
                print(f"  {line}")

        extract_dir = data.get("extract")
        if extract_dir:
            written = iflapp_format.export_header_assets(path, extract_dir)
            print(f"[OK] Recursos de cabecera exportados: {written}")
        return True


class NativeShellHelper:
    """Expone metadatos de shell y registra la integración del SO."""

    @staticmethod
    def info(data):
        import json as _json
        from pathlib import Path

        from lib import native_shell

        path = data.get("path")
        if not path:
            print("[ERROR] Debes indicar un archivo con --shell-info")
            return False
        target = Path(path).expanduser()
        if not target.is_file():
            print(f"[ERROR] No existe el archivo: {target}")
            return False
        try:
            info = native_shell.package_info(target)
        except ValueError as exc:
            print(f"[ERROR] {exc}")
            return False

        if data.get("json"):
            print(_json.dumps(info, indent=2, ensure_ascii=False))
        else:
            identity = info["identity"]
            print(f"Paquete   : {info['path']}")
            print(f"Tipo      : {info['kind']} v{info['format_version']} ({info['compression']}/{info['encryption']})")
            print(f"Publisher : {identity.get('publisher', '')}")
            print(f"App       : {identity.get('app', '')}  ({identity.get('name', '')})")
            print(f"Version   : {identity.get('version', '')}")
            if identity.get("signer"):
                print(f"Firmante  : {identity['signer']}")
            print(f"MIME      : {info['mime_type']}")
            print(f"Icono     : {info['icon_bytes']} bytes")
            print(f"Archivos  : {info['file_count']}")

        preview_dir = data.get("preview")
        if preview_dir:
            png = native_shell.export_icon_preview(target, preview_dir)
            if png:
                print(f"[OK] Vista previa exportada: {png}")
            else:
                print("[INFO] El paquete no tiene icono exportable (o falta Pillow).")
        return True

    @staticmethod
    def install():
        from lib import native_shell

        result = native_shell.install_shell_integration()
        for path in result["written"]:
            print(f"[OK] Integración escrita: {path}")
        for item in result["skipped"]:
            print(f"[AVISO] Omitido: {item}")
        if not result["written"]:
            print("[ERROR] No se pudo registrar la integración del shell.")
            return False
        return True


class MexfCompileHelper:
    """Compila un proyecto ``.mexf`` a un artefacto ``.asksome`` firmado."""

    @staticmethod
    def compile(data):
        from pathlib import Path

        from lib.mexf_compiler import MexfCompileError, compile_mexf_project

        path = data.get("path")
        if not path:
            print("[ERROR] Debes indicar la carpeta del proyecto con --compile-mexf")
            return False

        project_root = Path(path).expanduser().resolve()
        if not project_root.is_dir():
            print(f"[ERROR] La ruta no es una carpeta: {project_root}")
            return False

        output = data.get("output")
        output_path = Path(output).expanduser().resolve() if output else None
        try:
            result = compile_mexf_project(
                project_root,
                output_path,
                password=data.get("password"),
                wrappers=bool(data.get("wrappers")),
            )
        except MexfCompileError as exc:
            print(f"[ERROR] Compilación .mexf fallida: {exc}")
            return False

        print(f"Proyecto  : {project_root}")
        print(f"Módulos   : {', '.join(result.modules)}")
        print(f"Publisher : {result.metadata['publisher']}")
        print(f"App       : {result.metadata['app']}  ({result.metadata['name']})")
        print(f"Version   : {result.metadata['version']}")
        print(f"Plataforma: {result.metadata['platform']}")
        print(f"[OK] Artefacto .asksome generado: {result.output}")
        return True


class MexfDebugHelper:
    """Depura el plan declarado en un ``.mexf`` (pasos, puntos de ruptura)."""

    @staticmethod
    def debug(data):
        from pathlib import Path

        from lib.mexf_debugger import MexfDebugger
        from lib.mexf_parser import MexfError, parse_mexf

        path = data.get("path")
        if not path:
            print("[ERROR] Debes indicar un .mexf con --debug-mexf")
            return False
        source = Path(path).expanduser().resolve()
        project_root = source.parent.parent if source.parent.name == ".mexf" else source.parent
        try:
            document = parse_mexf(source, project_root=project_root)
        except (MexfError, FileNotFoundError, OSError) as exc:
            print(f"[ERROR] No se pudo leer el .mexf: {exc}")
            return False

        debugger = MexfDebugger(document, dry_run=not data.get("execute"))
        breakpoints = data.get("breakpoints") or ""
        for command_id in (item.strip() for item in breakpoints.split(",")):
            if command_id:
                debugger.set_breakpoint(command_id)

        mode = "ejecución real" if data.get("execute") else "simulado"
        print(f"Debug de {source.name}  ({mode})  comandos={len(debugger.commands)}")
        if debugger.breakpoints:
            print(f"Puntos de ruptura: {', '.join(debugger.breakpoints)}")
        debugger.start()
        while debugger.state != "finished":
            debugger.resume()
            if debugger.state == "paused":
                current = debugger.current_command()
                print(f"  [PAUSA] punto de ruptura en {current['id']}")
        for frame in debugger.frames:
            print(f"  [{frame.status:>7}] {frame.command_id}: {frame.executable} {' '.join(frame.args)}")
            if frame.output.strip():
                print(f"            {frame.output.strip()}")
        variables = debugger.variables()
        print(f"Estado: {variables['state']}  pc={variables['pc']}/{variables['total']}")
        if debugger.error:
            print(f"[ERROR] {debugger.error}")
            return False
        return True


class IflappIdeHelper:
    """Acciones headless del IDE de proyectos ``iflapp``."""

    @staticmethod
    def scan(data):
        import json

        from lib.iflapp_ide import scan_project

        path = data.get("path")
        if not path:
            print("[ERROR] Debes indicar la carpeta del proyecto con --ide-scan")
            return False
        try:
            project = scan_project(path)
        except (FileNotFoundError, OSError) as exc:
            print(f"[ERROR] {exc}")
            return False
        info = project.as_dict()
        if data.get("as_json"):
            print(json.dumps(info, ensure_ascii=False, indent=2))
            return True
        meta = info["metadata"]
        print(f"Proyecto  : {info['root']}")
        print(f"Identidad : {meta.get('publisher', '?')}.{meta.get('app', '?')} {meta.get('version', '?')}")
        print(f"Plataforma: {meta.get('platform', '?')}")
        print(f"Guiones   : {', '.join(info['scripts']) or '(ninguno)'}")
        print(f"Entrada   : {info['entry'] or '(sin punto de entrada)'}")
        print(f".mexf     : {'sí' if info['has_mexf'] else 'no'}")
        print(f"Icono     : {info['icon'] or '(sin icono)'}")
        if info["missing"]:
            print(f"[WARN] Faltan: {', '.join(info['missing'])}")
        return True

    @staticmethod
    def compile(data):
        from lib.iflapp_ide import compile_project

        path = data.get("path")
        if not path:
            print("[ERROR] Debes indicar la carpeta del proyecto con --ide-compile")
            return False
        backend = data.get("backend")
        outcome = compile_project(
            path,
            backend=None if backend in (None, "auto") else backend,
            output_dir=data.get("output"),
            log=print,
        )
        for line in outcome.log:
            print(line)
        print(f"Backend   : {outcome.backend}")
        print(f"Artefactos: {len(outcome.outputs)}")
        if outcome.failures:
            for failure in outcome.failures:
                print(f"[ERROR] {failure}")
            return False
        return True

    @staticmethod
    def execute(data):
        from pathlib import Path

        from lib.iflapp_ide import debug_script, run_script

        path = data.get("path")
        if not path:
            print("[ERROR] Debes indicar el guion con --ide-run o --ide-debug")
            return False
        script = Path(path).expanduser().resolve()
        if not script.is_file():
            print(f"[ERROR] No existe el guion: {script}")
            return False
        if data.get("debug"):
            breaks = data.get("breakpoints")
            lines = None
            if breaks:
                lines = [int(item) for item in str(breaks).split(",") if str(item).strip().isdigit()]
            outcome = debug_script(script, breakpoints=lines)
            if outcome.error:
                print(f"[ERROR] {outcome.error}")
                return False
            print(f"Depurando {script.name}: {len(outcome.stops)} parada(s)")
            for stop in outcome.stops:
                variables = ", ".join(f"{k}={v!r}" for k, v in list(stop.locals.items())[:6])
                print(f"  L{stop.line} {stop.function}  {variables}")
            return True
        code, output = run_script(script)
        print(output)
        print(f"[{'OK' if code == 0 else 'ERROR'}] código de salida: {code}")
        return code == 0


class AsksomeInstallHelper:
    """Instala, desinstala y lista artefactos ``.asksome``."""

    @staticmethod
    def _root(data):
        from pathlib import Path

        root = data.get("root")
        if root:
            return Path(root).expanduser().resolve()
        return Path.home() / ".packagemaker" / "apps"

    @staticmethod
    def install(data):
        from pathlib import Path

        from lib.blindcubeEngine.asksome_format import AsksomeError
        from lib.blindcubeEngine.asksome_installer import AsksomeInstallError, install_asksome
        from lib.blindcubeEngine.iflapp_format import IflappError

        path = data.get("path")
        if not path:
            print("[ERROR] Debes indicar el artefacto .asksome con --install-asksome")
            return False
        artifact = Path(path).expanduser().resolve()
        if not artifact.is_file():
            print(f"[ERROR] No existe el artefacto: {artifact}")
            return False
        root = AsksomeInstallHelper._root(data)
        try:
            record = install_asksome(
                artifact,
                root,
                create_desktop_shortcuts=bool(data.get("shortcuts", True)),
                password=data.get("password"),
                removeme_binary=bool(data.get("removeme_binary", False)),
                backend=data.get("removeme_backend"),
                log_callback=print,
            )
        except (AsksomeError, AsksomeInstallError, IflappError) as exc:
            print(f"[ERROR] Instalación .asksome fallida: {exc}")
            return False
        print(f"App       : {record.name} ({record.app_id})")
        print(f"Version   : {record.version}")
        print(f"Instalado : {record.install_dir}")
        if record.shortcuts:
            print(f"Accesos   : {', '.join(record.shortcuts)}")
        print(f"[OK] Removedor: {record.install_dir}/{record.remover}")
        return True

    @staticmethod
    def build_removeme(data):
        from lib.blindcubeEngine.asksome_installer import AsksomeInstallError, build_removeme

        app_id = data.get("app_id")
        if not app_id:
            print("[ERROR] Debes indicar el app id con --build-removeme")
            return False
        root = AsksomeInstallHelper._root(data)
        try:
            binary = build_removeme(
                app_id,
                root,
                preferred_backend=data.get("backend"),
                log_callback=print,
            )
        except AsksomeInstallError as exc:
            print(f"[ERROR] No se pudo compilar el removedor: {exc}")
            return False
        if binary is None:
            print("[ERROR] No hay ningún backend de compilación disponible; queda removeme.py")
            return False
        print(f"[OK] Removedor nativo: {binary}")
        return True

    @staticmethod
    def uninstall(data):
        from lib.blindcubeEngine.asksome_installer import AsksomeInstallError, uninstall_asksome

        app_id = data.get("app_id")
        if not app_id:
            print("[ERROR] Debes indicar el app id con --uninstall-asksome")
            return False
        root = AsksomeInstallHelper._root(data)
        try:
            removed = uninstall_asksome(app_id, root)
        except AsksomeInstallError as exc:
            print(f"[ERROR] Desinstalación .asksome fallida: {exc}")
            return False
        for item in removed:
            print(f"eliminado: {item}")
        print(f"[OK] {app_id} desinstalado")
        return True

    @staticmethod
    def list_installed(data):
        from lib.blindcubeEngine.asksome_installer import list_installed

        root = AsksomeInstallHelper._root(data)
        records = list_installed(root)
        if not records:
            print(f"Sin artefactos .asksome instalados en {root}")
            return True
        print(f"Instalados en {root}:")
        for record in records:
            print(f"  - {record.app_id}  {record.name}  {record.version}")
        return True


# === Action Handlers ===
def _handle_shell_actions(action, data=None):
    """Maneja acciones de shell que no requieren GUI. Retorna True si se manejó."""
    if action == 'shell_plan':
        return MexfShellHelper.plan(data or {})

    elif action == 'install_mexf_shell':
        return MexfShellHelper.install(data or {})

    elif action == 'uninstall_mexf_shell':
        return MexfShellHelper.uninstall(data or {})

    elif action == 'show_version':
        print(f"Influent Package Maker v{__version__}")
        print("https://github.com/JesusQuijada34/packagemaker")
        return True
    
    elif action == 'version_update':
        return VersionUpdateHelper.update()

    elif action == 'list_compilers':
        return CompilerReportHelper.report()

    elif action == 'list_engines':
        return EngineReportHelper.report()

    elif action == 'list_hardening':
        return HardeningReportHelper.report()

    elif action == 'list_fonts':
        return FontReportHelper.report()

    elif action == 'download_fonts':
        return FontReportHelper.download(data or {})

    elif action == 'inspect_iflapp':
        return PackageInspectHelper.inspect(data or {})

    elif action == 'shell_info':
        return NativeShellHelper.info(data or {})

    elif action == 'install_shell_integration':
        return NativeShellHelper.install()

    elif action == 'compile_mexf':
        return MexfCompileHelper.compile(data or {})

    elif action == 'debug_mexf':
        return MexfDebugHelper.debug(data or {})

    elif action == 'install_asksome':
        return AsksomeInstallHelper.install(data or {})

    elif action == 'build_removeme':
        return AsksomeInstallHelper.build_removeme(data or {})

    elif action == 'uninstall_asksome':
        return AsksomeInstallHelper.uninstall(data or {})

    elif action == 'list_asksome':
        return AsksomeInstallHelper.list_installed(data or {})

    elif action == 'ide_scan':
        return IflappIdeHelper.scan(data or {})

    elif action == 'ide_compile':
        return IflappIdeHelper.compile(data or {})

    elif action in ('ide_run', 'ide_debug'):
        return IflappIdeHelper.execute(data or {})

    return None  # No es acción de shell


def _handle_gui_actions(window, action, data):
    """Maneja acciones que requieren GUI."""
    action_map = {
        'create_project': (0, 'showCreateProjectDialog'),
        'install_folder': (None, 'showInstallFolderDialog'),
        'compile_project': (1, 'showCompileDialog'),
        'repair_project': (3, 'showRepairDialog'),
        'install_package': (None, 'showInstallPackageDialog'),
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
        Instancia de ventana GUI, True/False para acciones de shell o None

    """
    # Primero intentar manejar como acción de shell (sin GUI)
    shell_result = _handle_shell_actions(action, data)
    if shell_result is not None:
        # Es acción de shell, no requiere GUI; propagar True/False al entrypoint.
        return shell_result
    
    # Manejar acciones headless (create, compile, repair)
    if action == 'create_project' and kwargs.get('headless'):
        from lib.makeselfEngine.template_engine import create_project_from_templates, normalize_platform
        project_source = data if isinstance(data, dict) else {'path': data}
        base_path = Path(project_source.get('path')).resolve()
        
        # Obtener valores de proyecto
        publisher = (project_source.get('publisher') or project_source.get('author') or 'influent').strip().lower().replace(' ', '-')
        app_id = project_source.get('shortname') or (project_source.get('name') or base_path.name).strip().lower().replace(' ', '-')
        version_base = ProjectNameFormatter.normalize_version_base(project_source.get('version') or '1.0.0')
        platform_value = normalize_platform(project_source.get('platform')) if project_source.get('platform') else normalize_platform('Knosthalij')
        description = project_source.get('description') or 'Proyecto creado con Influent Package Maker'
        author_val = project_source.get('author') or 'Unknown'
        
        # Usar ProjectNameFormatter para formato consistente
        timestamp = ProjectNameFormatter.get_timestamp()
        folder_name = ProjectNameFormatter.format_project_folder(
            publisher, app_id, version_base, platform_value, timestamp
        )
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
            timestamp=timestamp,
        )
        
        # Copiar icono por defecto
        icon_dest = project_path / "app" / "app-icon.ico"
        icon_source = Path("app/app-icon.ico")
        if icon_source.exists():
            import shutil
            shutil.copy(str(icon_source), str(icon_dest))
            print(f"[OK] Icono copiado a: {icon_dest}")
        
        _safe_print(f"\n  ✔ Proyecto creado en: {project_path}\n")
        return None
    
    elif action == 'compile_project' and kwargs.get('headless'):
        from lib.blindcubeEngine.BuildThread import FlangCompiler
        
        project_source = data if isinstance(data, dict) else {'path': data}
        base_path = Path(project_source.get('path')).resolve()
        
        # Construir nombre de carpeta para buscar el proyecto
        publisher = (project_source.get('publisher') or project_source.get('author') or 'influent').strip().lower().replace(' ', '-')
        app_id = project_source.get('shortname') or (project_source.get('name') or '').strip().lower().replace(' ', '-')
        version_base = ProjectNameFormatter.normalize_version_base(project_source.get('version') or '1.0.0')
        
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

        print("[INFO] Iniciando compilación headless...")
        print(f"[INFO] Proyecto: {project_path}")
        print(f"[INFO] Salida: {output_path}")
        print(f"[INFO] Plataforma objetivo (detectada): {target_platform}")
        compiler = FlangCompiler(
            project_path,
            output_path,
            log_callback=print,
            compiler_name=kwargs.get('compiler'),
            sandbox=kwargs.get('sandbox', True),
            package_password=kwargs.get('password'),
            build_dropper=kwargs.get('dropper', False),
            hardening=kwargs.get('hardening'),
        )
        if scripts:
            compiler.scripts_to_compile = [s.strip() for s in scripts.split(',') if s.strip()]

        if not compiler.parse_details_xml():
            sys.exit(1)

        if not compiler.find_scripts():
            sys.exit(1)
        try:
            if not compiler.compile_binaries(target_platform):
                sys.exit(1)
            if not compiler.create_package(target_platform):
                sys.exit(1)

            publisher = compiler.metadata['publisher']
            app = compiler.metadata['app']
            version = compiler.metadata['version']
            platform_suffix = "Knosthalij" if target_platform == "Windows" else "Danenone"
            
            # Usar ProjectNameFormatter para formato consistente
            package_name = ProjectNameFormatter.format_package_folder(publisher, app, version, platform_suffix)
            package_path = output_path / package_name
            iflapp_file = output_path / ProjectNameFormatter.format_iflapp_filename(publisher, app, version, platform_suffix)

            if not compiler.compress_to_iflapp(package_path, iflapp_file):
                sys.exit(1)

            if optimize:
                print("[INFO] Optimizando binarios...")
                if not compiler.optimize_binaries():
                    sys.exit(1)

            compiler.verify_in_sandbox(iflapp_file)
            if kwargs.get('dropper'):
                compiler.create_dropper(iflapp_file)

            print("[OK] Compilación completada exitosamente")
            print(f"[INFO] Paquete generado: {iflapp_file}")
            
            # El artefacto ya existe; limpiar paquete temporal y proyecto fuente.
            compiler._cleanup_package_folder(package_path, iflapp_file)
            compiler.cleanup_processed_project(iflapp_file)
        finally:
            if hasattr(compiler, '_cleanup_build_artifacts'):
                compiler._cleanup_build_artifacts()
        return None
    
    elif action == 'buildthis' and kwargs.get('headless'):
        from lib.blindcubeEngine.BuildThread import FlangCompiler
        
        project_source = data if isinstance(data, dict) else {'path': data}
        project_path = Path(project_source.get('path')).resolve()
        
        # Verificar que la ruta existe y tiene details.xml
        if not project_path.exists():
            print(f"[ERROR] La ruta especificada no existe: {project_path}")
            sys.exit(1)
        
        if not (project_path / 'details.xml').exists():
            print(f"[ERROR] La ruta especificada no es un proyecto válido (no tiene details.xml): {project_path}")
            sys.exit(1)
        
        # Usar la salida explícita de CI cuando se proporciona; de lo contrario,
        # conservar la ruta predeterminada de la GUI.
        output_arg = kwargs.get('output')
        if output_arg:
            output_path = Path(output_arg).expanduser().resolve()
        else:
            output_path = Path(os.path.expanduser("~")).resolve()
            output_path = output_path / "Documents" / "Packagemaker Projects" / "Compiled"
        output_path.mkdir(parents=True, exist_ok=True)

        # Detectar plataforma automáticamente salvo que el llamador la fije.
        target_platform = kwargs.get('platform') or (
            'Windows' if sys.platform.startswith('win') else 'Linux'
        )

        print("[INFO] Iniciando compilación del proyecto actual...")

        # Motor explícito: si se indica, su backend manda; si no, se conserva el
        # comportamiento previo (backend por defecto, Nuitka).
        compiler_name = kwargs.get('compiler')
        engine_id = kwargs.get('engine')
        if engine_id:
            from lib.engines import get_engine

            engine = get_engine(engine_id)
            compiler_name = engine.backend or compiler_name
            print(f"[INFO] Motor: {engine.display_name} (py{engine.python_version}, backend={engine.backend})")
            if engine.is_legacy:
                print("[WARN] FlatCube v1 es legacy y no recibe soporte.")

        print(f"[INFO] Proyecto: {project_path}")
        print(f"[INFO] Salida: {output_path}")
        print(f"[INFO] Plataforma objetivo (detectada): {target_platform}")
        compiler = FlangCompiler(
            project_path,
            output_path,
            log_callback=print,
            compiler_name=compiler_name,
            sandbox=kwargs.get('sandbox', True),
            package_password=kwargs.get('password'),
            build_dropper=kwargs.get('dropper', False),
            hardening=kwargs.get('hardening'),
        )

        if not compiler.parse_details_xml():
            sys.exit(1)

        if not compiler.find_scripts():
            sys.exit(1)
        try:
            if not compiler.compile_binaries(target_platform):
                sys.exit(1)
            if not compiler.create_package(target_platform):
                sys.exit(1)

            publisher = compiler.metadata['publisher']
            app = compiler.metadata['app']
            version = compiler.metadata['version']
            platform_suffix = "Knosthalij" if target_platform == "Windows" else "Danenone"
            
            # Usar ProjectNameFormatter para formato consistente
            package_name = ProjectNameFormatter.format_package_folder(publisher, app, version, platform_suffix)
            package_path = output_path / package_name
            iflapp_file = output_path / ProjectNameFormatter.format_iflapp_filename(publisher, app, version, platform_suffix)

            if not compiler.compress_to_iflapp(package_path, iflapp_file):
                sys.exit(1)

            compiler.verify_in_sandbox(iflapp_file)
            if kwargs.get('dropper'):
                compiler.create_dropper(iflapp_file)

            print("[OK] Compilación completada exitosamente")
            print(f"[INFO] Paquete generado: {iflapp_file}")
            
            # El artefacto ya existe; limpiar paquete temporal y proyecto fuente.
            compiler._cleanup_package_folder(package_path, iflapp_file)
            compiler.cleanup_processed_project(iflapp_file)
        finally:
            if hasattr(compiler, '_cleanup_build_artifacts'):
                compiler._cleanup_build_artifacts()
        return None
    
    elif action == 'repair_project' and kwargs.get('headless'):
        from lib.makeselfEngine.template_engine import normalize_platform, repair_project_from_templates
        from xml.etree import ElementTree as ET
        
        project_source = data if isinstance(data, dict) else {'path': data}
        base_path = Path(project_source.get('path')).resolve()
        
        # Construir nombre de carpeta para buscar el proyecto
        publisher = (project_source.get('publisher') or project_source.get('author') or 'influent').strip().lower().replace(' ', '-')
        app_id = project_source.get('shortname') or (project_source.get('name') or '').strip().lower().replace(' ', '-')
        version_raw_input = str(project_source.get('version') or '1.0.0').strip()
        try:
            version_base, _ = ProjectNameFormatter.version_components(version_raw_input)
        except ValueError:
            # Compatibilidad con proyectos antiguos: v1-YY.MM-HH.MM-platform,
            # que todavía no tienen una versión base con punto.
            match = re.match(r'^v?(\d+)(?:\.(\d+))?(?:\.(\d+))?', version_raw_input)
            if match:
                major, minor, patch = match.groups()
                version_base = f"{major}.{minor or '0'}"
                if patch is not None:
                    version_base += f".{patch}"
            else:
                version_base = '1.0'
        
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
                version_raw = (root.findtext('version') or version_raw_input).strip()
                try:
                    version_base, _ = ProjectNameFormatter.version_components(version_raw)
                except ValueError:
                    match = re.match(r'^v?(\d+)(?:\.(\d+))?(?:\.(\d+))?', version_raw)
                    if match:
                        major, minor, patch = match.groups()
                        version_base = f"{major}.{minor or '0'}"
                        if patch is not None:
                            version_base += f".{patch}"
                # Los proyectos antiguos pueden declarar la plataforma como <with>
                # o <target> en lugar de usar <platform>. No asumir Windows cuando
                # el metadato Linux ya está presente.
                platform_text = (
                    root.findtext('platform')
                    or root.findtext('with')
                    or root.findtext('target')
                    or ''
                )
                platform_value = normalize_platform(platform_text)
            except Exception as e:
                print(f"⚠ Advertencia: no se pudo leer details.xml: {e}")

        if not platform_value:
            if sys.platform.startswith('linux'):
                platform_value = 'Danenone'
            elif sys.platform.startswith('win'):
                platform_value = 'Knosthalij'
            else:
                platform_value = 'AlphaCube'

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
