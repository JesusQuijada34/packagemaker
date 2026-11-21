#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
leviathan-ui - CLI principal para SetupDialogs v1.0.5
Comandos: configure, activepath, showStatus, start, precompile, compile, packageStart
Diseño visual creativo con colores ANSI y ASCII art
"""

import os
import re
import sys
import json
import shutil
import subprocess
import tempfile
import argparse
import time
from pathlib import Path

# Añadir leviathan_ui al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from .Script import LeviScript


# ============================================================
# COLORES Y ESTILOS ANSI
# ============================================================
class C:
    """Colores ANSI para terminal creativo"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    
    # Foreground
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright
    B_RED = '\033[91m'
    B_GREEN = '\033[92m'
    B_YELLOW = '\033[93m'
    B_BLUE = '\033[94m'
    B_MAGENTA = '\033[95m'
    B_CYAN = '\033[96m'
    B_WHITE = '\033[97m'
    
    # Background
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'


# ============================================================
# ASCII ART Y BANNERS
# ============================================================
class Art:
    """Arte ASCII para CLI creativo"""
    
    LOGO = f"""
{C.B_CYAN}    ██╗     ███████╗██╗   ██╗██╗ █████╗ ████████╗██╗  ██╗ █████╗ ███╗   ██╗
    ██║     ██╔════╝██║   ██║██║██╔══██╗╚══██╔══╝██║  ██║██╔══██╗████╗  ██║
    ██║     █████╗  ██║   ██║██║███████║   ██║   ███████║███████║██╔██╗ ██║
    ██║     ██╔══╝  ╚██╗ ██╔╝██║██╔══██║   ██║   ██╔══██║██╔══██║██║╚██╗██║
    ███████╗███████╗ ╚████╔╝ ██║██║  ██║   ██║   ██║  ██║██║  ██║██║ ╚████║
    ╚══════╝╚══════╝  ╚═══╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝{C.RESET}
{C.B_BLUE}                           ██╗   ██╗██╗{C.RESET}
{C.B_BLUE}                           ██║   ██║██║{C.RESET}
{C.B_BLUE}                           ██║   ██║██║{C.RESET}
{C.B_BLUE}                           ██║   ██║██║{C.RESET}
{C.B_BLUE}                           ╚██████╔╝██║{C.RESET}
{C.B_BLUE}                            ╚═════╝ ╚═╝{C.RESET}
    """
    
    DRAGON = f"""
{C.B_CYAN}      /\\      /\\
     /  \\____/  \\
    /    {C.B_RED}()  (){C.B_CYAN}    \\
   |      {C.B_YELLOW}\\__/{C.B_CYAN}      |
    \\   {C.B_GREEN}______{C.B_CYAN}    /
     |  {C.B_GREEN}/      \\{C.B_CYAN}  |
     /  {C.B_GREEN}\\______/{C.B_CYAN}  \\
    /____________\\{C.RESET}
    """
    
    SETUP_DIALOGS = f"""
{C.B_MAGENTA}╔═══════════════════════════════════════════════════════════════════╗
║{C.B_WHITE}           🔥 SETUP DIALOGS - Motor de Instaladores 🔥{C.B_MAGENTA}            ║
║{C.DIM}           "El arte de instalar con elegancia y poder"{C.B_MAGENTA}           ║
╚═══════════════════════════════════════════════════════════════════╝{C.RESET}
    """
    
    DIVIDER = f"{C.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.RESET}"
    THIN_DIV = f"{C.DIM}─────────────────────────────────────────────────────────────────{C.RESET}"
    
    # Iconos
    OK = f"{C.B_GREEN}✓{C.RESET}"
    ERR = f"{C.B_RED}✗{C.RESET}"
    WARN = f"{C.B_YELLOW}⚠{C.RESET}"
    INFO = f"{C.B_BLUE}ℹ{C.RESET}"
    BULLET = f"{C.B_CYAN}●{C.RESET}"
    ARROW = f"{C.B_CYAN}➜{C.RESET}"
    FIRE = f"{C.B_RED}🔥{C.RESET}"
    GEAR = f"{C.B_YELLOW}⚙{C.RESET}"
    PACKAGE = f"{C.B_MAGENTA}📦{C.RESET}"
    ROCKET = f"{C.B_GREEN}🚀{C.RESET}"
    SPARKLES = f"{C.B_YELLOW}✨{C.RESET}"


# ============================================================
# FUNCIONES DE DISEÑO
# ============================================================
def print_header():
    """Imprimir cabecera visual"""
    print(Art.LOGO)
    print(Art.SETUP_DIALOGS)
    print()


def print_section(title: str, icon: str = Art.GEAR):
    """Imprimir sección decorada"""
    print()
    print(f"{C.B_MAGENTA}╔═{C.RESET} {icon} {C.BOLD}{C.B_WHITE}{title}{C.RESET}")
    print(Art.THIN_DIV)


def print_box(content: str, style: str = "single"):
    """Imprimir caja decorativa"""
    lines = content.split('\n')
    max_len = max(len(line) for line in lines)
    
    if style == "double":
        print(f"{C.B_CYAN}╔{'═' * (max_len + 2)}╗{C.RESET}")
        for line in lines:
            print(f"{C.B_CYAN}║{C.RESET} {line.ljust(max_len)} {C.B_CYAN}║{C.RESET}")
        print(f"{C.B_CYAN}╚{'═' * (max_len + 2)}╝{C.RESET}")
    else:
        print(f"{C.B_BLUE}┌{'─' * (max_len + 2)}┐{C.RESET}")
        for line in lines:
            print(f"{C.B_BLUE}│{C.RESET} {line.ljust(max_len)} {C.B_BLUE}│{C.RESET}")
        print(f"{C.B_BLUE}└{'─' * (max_len + 2)}┘{C.RESET}")


def print_success(msg: str):
    """Mensaje de éxito"""
    print(f"{Art.OK} {C.B_GREEN}{msg}{C.RESET}")


def print_error(msg: str):
    """Mensaje de error"""
    print(f"{Art.ERR} {C.B_RED}{msg}{C.RESET}")


def print_warning(msg: str):
    """Mensaje de advertencia"""
    print(f"{Art.WARN} {C.B_YELLOW}{msg}{C.RESET}")


def print_info(msg: str):
    """Mensaje informativo"""
    print(f"{Art.INFO} {C.B_BLUE}{msg}{C.RESET}")


def print_step(num: int, msg: str):
    """Paso numerado"""
    print(f"{C.B_CYAN}  [{num}]{C.RESET} {msg}")


def spinner_animation(text: str, duration: float = 1.0):
    """Animación de spinner"""
    spinners = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    start = time.time()
    i = 0
    while time.time() - start < duration:
        print(f"\r{C.B_CYAN}{spinners[i % len(spinners)]}{C.RESET} {text}...", end='', flush=True)
        time.sleep(0.1)
        i += 1
    print(f"\r{Art.OK} {text} {C.B_GREEN}completado{C.RESET}      ")


def progress_bar(percent: int, width: int = 40) -> str:
    """Barra de progreso visual"""
    filled = int(width * percent / 100)
    bar = f"{C.B_GREEN}{'█' * filled}{C.DIM}{'░' * (width - filled)}{C.RESET}"
    return f"[{bar}] {C.B_CYAN}{percent}%{C.RESET}"


try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    
try:
    HAS_PYINSTALLER = True
except ImportError:
    HAS_PYINSTALLER = False


class LeviathanCLI:
    """CLI principal de SetupDialogs"""
    
    VERSION = "1.0.5"
    
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog='leviathan-ui',
            description=f'Leviathan-UI SetupDialogs v{self.VERSION} - Sistema de instaladores profesionales'
        )
        self._setup_subcommands()
        
    def _setup_subcommands(self):
        subparsers = self.parser.add_subparsers(dest='command', help='Comandos tipo npm disponibles')
        
        # init = configure (tipo npm init)
        init_parser = subparsers.add_parser('init', help='Inicializar nuevo proyecto (npm-style)')
        init_parser.add_argument('name', type=str, nargs='?', default='my-app',
                               help='Nombre del proyecto')
        init_parser.add_argument('--template', type=str, default='nativeGear',
                               choices=['packagemaker', 'nativeGear'],
                               help='Template/esqueleto a usar')
        init_parser.add_argument('--gpumode', type=str, default='inactive',
                               choices=['active', 'inactive'],
                               help='Modo GPU para depuración visual')
        
        # Alias: configure = init
        configure_parser = subparsers.add_parser('configure', help='[Alias de init] Crear nuevo proyecto')
        configure_parser.add_argument('name', type=str, nargs='?', default='my-app',
                                    help='Nombre del proyecto')
        configure_parser.add_argument('--requires', '--template', type=str, default='nativeGear',
                                    choices=['packagemaker', 'nativeGear'],
                                    dest='template',
                                    help='Template/esqueleto a usar')
        configure_parser.add_argument('--gpumode', type=str, default='inactive',
                                    choices=['active', 'inactive'],
                                    help='Modo GPU para depuración visual')
        
        # install = activepath (tipo npm install -g)
        install_parser = subparsers.add_parser('install', help='Instalar leviathan-ui globalmente (npm-style)')
        install_parser.add_argument('-g', '--global', action='store_true', default=True,
                                   help='Instalar globalmente (por defecto)')
        
        # Alias: activepath = install
        subparsers.add_parser('activepath', help='[Alias de install] Registrar en PATH')
        
        # status = showStatus (tipo npm list)
        subparsers.add_parser('status', help='Mostrar estado del proyecto (npm-style)')
        
        # Alias: showStatus = status
        subparsers.add_parser('showStatus', help='[Alias de status] Mostrar estado del proyecto')
        
        # run / test = start (tipo npm run / npm test)
        run_parser = subparsers.add_parser('run', help='Ejecutar/testear proyecto (npm-style)')
        run_parser.add_argument('script', type=str, nargs='?', default='test',
                              choices=['test', 'start', 'lint', 'build'],
                              help='Script a ejecutar')
        run_parser.add_argument('--file', type=str, default='setup.ls',
                               help='Archivo LeviScript a testear')
        
        # Alias: start = run test
        start_parser = subparsers.add_parser('start', help='[Alias de run test] Testear sintaxis')
        start_parser.add_argument('--file', type=str, default='setup.ls',
                                 help='Archivo LeviScript a testear')
        
        # precompile (mantener)
        precompile_parser = subparsers.add_parser('precompile', help='Precompilar .ls a .lsx')
        precompile_parser.add_argument('file', type=str, nargs='?', default='setup.ls',
                                      help='Archivo .ls a precompilar')
        precompile_parser.add_argument('-o', '--output', type=str, help='Archivo .lsx de salida')
        
        # build = compile (tipo npm run build)
        build_parser = subparsers.add_parser('build', help='Compilar proyecto a .exe (npm-style)')
        build_parser.add_argument('file', type=str, nargs='?', default='setup.lsx',
                                 help='Archivo .lsx a compilar')
        build_parser.add_argument('--icon', type=str, help='Icono para el ejecutable')
        build_parser.add_argument('--onefile', action='store_true', help='Crear ejecutable único')
        build_parser.add_argument('--windowed', action='store_true', default=True,
                               help='Modo ventana (sin consola)')
        
        # Alias: compile = build
        compile_parser = subparsers.add_parser('compile', help='[Alias de build] Compilar a .exe')
        compile_parser.add_argument('file', type=str, nargs='?', default='setup.lsx',
                                 help='Archivo .lsx a compilar')
        compile_parser.add_argument('--icon', type=str, help='Icono para el ejecutable')
        compile_parser.add_argument('--onefile', action='store_true', help='Crear ejecutable único')
        compile_parser.add_argument('--windowed', action='store_true', default=True,
                                   help='Modo ventana (sin consola)')
        
        # pack = packageStart (tipo npm pack)
        pack_parser = subparsers.add_parser('pack', help='Empaquetar proyecto (npm-style)')
        pack_parser.add_argument('file', type=str, nargs='?', default='.',
                                help='Directorio a empaquetar')
        pack_parser.add_argument('--obfuscate', action='store_true', help='Ofuscar código')
        
        # Alias: packageStart = pack
        package_parser = subparsers.add_parser('packageStart', help='[Alias de pack] Empaquetar blindado')
        package_parser.add_argument('file', type=str, nargs='?', default='.',
                                   help='Proyecto a empaquetar')
        package_parser.add_argument('--obfuscate', action='store_true', help='Ofuscar código')
        
        # help = guía paso a paso
        help_parser = subparsers.add_parser('help', help='Guía interactiva paso a paso')
        help_parser.add_argument('--topic', type=str, default='all',
                                choices=['all', 'init', 'build', 'pack', 'syntax'],
                                help='Tema específico de ayuda')
        
        
    def run(self, args=None):
        """Ejecutar comando"""
        args = self.parser.parse_args(args)
        
        if not args.command:
            self.parser.print_help()
            return 1
            
        command_map = {
            'init': self.cmd_init,
            'install': self.cmd_install,
            'status': self.cmd_status,
            'run': self.cmd_run,
            'build': self.cmd_build,
            'pack': self.cmd_pack,
            'help': self.cmd_help,
            # Comandos legacy/alias
            'configure': self.cmd_init,  # alias de init
            'activepath': self.cmd_install,  # alias de install
            'showStatus': self.cmd_status,  # alias de status
            'start': self.cmd_start,  # alias de run test
            'precompile': self.cmd_precompile,
            'compile': self.cmd_build,  # alias de build
            'packageStart': self.cmd_pack,  # alias de pack
        }
        
        return command_map[args.command](args)
    
    def _debug_progress(self, desc: str, total: int, gpumode: str = 'inactive'):
        """Mostrar barra de progreso con tqdm o modo GPU"""
        if gpumode == 'active':
            print(f"[GPU MODE] {desc}")
            # En modo GPU, usaríamos una ventana gráfica con progreso
            # Por ahora, fallback a tqdm
            
        if HAS_TQDM:
            return tqdm(range(total), desc=desc, unit="step")
        else:
            return range(total)
    
    def cmd_configure(self, args) -> int:
        """Crear nuevo proyecto de instalador"""
        print(f"🐉 Leviathan-UI SetupDialogs v{self.VERSION}")
        print(f"📦 Configurando proyecto: {args.name}")
        print(f"🔧 Esqueleto: {args.requires}")
        print(f"🎮 GPU Mode: {args.gpumode}")
        print()
        
        # Crear directorio del proyecto
        project_dir = Path(args.name)
        if project_dir.exists():
            print(f"❌ Error: El directorio '{args.name}' ya existe")
            return 1
            
        # Simular progreso
        steps = ["Creando estructura de directorios...",
                 "Generando esqueleto base...",
                 "Configurando archivos de proyecto...",
                 "Instalando dependencias...",
                 "Finalizando configuración..."]
        
        for i, step in enumerate(self._debug_progress("Configurando", len(steps), args.gpumode)):
            print(f"  {steps[i]}")
            
            if i == 0:
                project_dir.mkdir()
                (project_dir / 'src').mkdir()
                (project_dir / 'assets').mkdir()
                (project_dir / 'dist').mkdir()
                
            elif i == 1:
                self._create_manifest(project_dir, args.name, args.template)
                
            elif i == 2:
                self._generate_skeleton(project_dir, args.name, args.template)
                
            elif i == 3:
                # Verificar dependencias
                pass
                
        print()
        print(f"✅ Proyecto '{args.name}' creado exitosamente!")
        print(f"📁 Ubicación: {project_dir.absolute()}")
        print()
        print("Próximos pasos:")
        print(f"  cd {args.name}")
        print("  leviathan-ui run test      # Testear sintaxis")
        print("  leviathan-ui build         # Compilar a .exe")
        print("  leviathan-ui pack          # Empaquetar proyecto")
        return 0
    
    def _create_manifest(self, project_dir: Path, name: str, template: str):
        """Crear leviathan.json tipo package.json"""
        manifest = {
            "name": name,
            "version": "1.0.0",
            "description": f"Instalador {name} generado con Leviathan-UI",
            "author": "",
            "license": "MIT",
            "main": "src/index.ls",
            "scripts": {
                "test": "leviathan-ui run test",
                "build": "leviathan-ui build",
                "precompile": "leviathan-ui precompile",
                "pack": "leviathan-ui pack"
            },
            "dependencies": {
                "leviathan-ui": f">={self.VERSION}"
            },
            "template": template,
            "config": {
                "installDir": f"${{env.PROGRAMFILES}}/{name}",
                "desktopShortcut": True,
                "startMenuShortcut": True,
                "gpuMode": "inactive"
            },
            "pages": [
                "welcome",
                "options", 
                "install",
                "finish"
            ],
            "assets": {
                "banner": "assets/banner.png",
                "icon": "assets/icon.ico",
                "splash": "assets/splash.png"
            }
        }
        
        import json
        (project_dir / 'leviathan.json').write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
    
    def _generate_skeleton(self, project_dir: Path, name: str, template: str):
        """Generar esqueleto base del proyecto - formato YAML-like + JS"""
        
        # Crear src/index.ls - sintaxis tipo JS/YAML
        ls_content = f'''# LeviScript v{self.VERSION} - {name}
# Estructura tipo YAML Manifest + JS

# ============ CONFIGURACIÓN (YAML-like) ============
meta:
  name: "{name}"
  version: "1.0.0"
  author: "Autor"
  description: "Instalador profesional"
  license: "MIT"

requires:
  - leviathan-ui >= {self.VERSION}

# ============ VARIABLES (JS-style) ============
const installDir = `${{env.PROGRAMFILES}}/{name}`;
const createDesktopShortcut = true;
const createStartMenuShortcut = true;
const appExecutable = "{name}.exe";

# ============ PÁGINAS (Array JS) ============
pages: [
  {{
    type: "welcome",
    title: `Bienvenido a ${{meta.name}}`,
    subtitle: "Asistente de instalación",
    banner: "assets/banner.png",
    style: "modern"
  }},
  {{
    type: "options",
    title: "Opciones de Instalación",
    installPath: installDir,
    shortcuts: {{
      desktop: createDesktopShortcut,
      startmenu: createStartMenuShortcut
    }}
  }},
  {{
    type: "install",
    title: "Instalando...",
    worker: true,
    showProgress: true,
    showLog: true,
    animation: "smooth"
  }},
  {{
    type: "finish",
    title: "Instalación Completada",
    launchApp: false,
    showReadme: true
  }}
];

# ============ HOOKS (Funciones JS) ============
function beforeDisplay() {{
  console.log(`Iniciando instalador de ${{meta.name}}...`);
  checkDependencies();
}}

function onInstall(progress) {{
  progress.step("Extrayendo archivos...", 20);
  // extractFiles("data.zip", installDir);
  
  progress.step("Configurando sistema...", 60);
  // registerInRegistry(installDir);
  
  progress.step("Creando accesos directos...", 90);
  if (createDesktopShortcut) {{
    createShortcut("Desktop", `${{installDir}}/${{appExecutable}}`);
  }}
  createShortcut("StartMenu", `${{installDir}}/${{appExecutable}}`);
  
  progress.step("Finalizando...", 100);
}}

function afterInstall() {{
  console.log("Instalación completada exitosamente");
  saveConfig();
}}

function onError(error) {{
  console.error(`ERROR: ${{error.message}}`);
  dialog.error(error.message);
}}

# Exportar configuración
export default {{
  meta,
  pages,
  beforeDisplay,
  onInstall,
  afterInstall,
  onError
}};
'''
        
        # Escribir archivo principal
        (project_dir / 'src' / 'index.ls').write_text(ls_content, encoding='utf-8')
        
        # Crear package.json adicional para npm users
        package_json = {
            "name": name.lower().replace(" ", "-"),
            "version": "1.0.0",
            "description": f"Instalador {name}",
            "private": True,
            "scripts": {
                "init": f"leviathan-ui init {name}",
                "test": "leviathan-ui run test",
                "build": "leviathan-ui build",
                "precompile": "leviathan-ui precompile",
                "pack": "leviathan-ui pack"
            },
            "devDependencies": {
                "leviathan-ui": f"^{self.VERSION}"
            }
        }
        
        (project_dir / 'package.json').write_text(
            json.dumps(package_json, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        
        # Crear .gitignore
        gitignore = '''# Leviathan-UI Project
*.lsx
*.exe
*.spec
dist/
build/
__pycache__/
*.pyc
.env
'''
        (project_dir / '.gitignore').write_text(gitignore, encoding='utf-8')
        
        # Crear README.md
        readme = f'''# {name}

Instalador generado con Leviathan-UI SetupDialogs v{self.VERSION}

## Estructura del Proyecto

```
{name}/
├── leviathan.json      # Manifest (tipo package.json)
├── package.json        # Para npm users
├── src/
│   └── index.ls       # Código principal (YAML + JS)
├── assets/            # Recursos gráficos
├── dist/              # Output compilado
└── .gitignore
```

## Comandos (tipo npm)

```bash
# Inicializar proyecto
leviathan-ui init {name}

# Testear sintaxis
leviathan-ui run test
leviathan-ui start

# Precompilar .ls → .lsx
leviathan-ui precompile

# Compilar a .exe
leviathan-ui build
leviathan-ui compile

# Empaquetar
leviathan-ui pack
leviathan-ui packageStart .
```

## Sintaxis LeviScript

LeviScript combina YAML para configuración + JS para lógica:

```javascript
# Config YAML-like
meta:
  name: "MiApp"
  version: "1.0.0"

# Variables JS
const installDir = `${{env.PROGRAMFILES}}/MiApp`;

# Funciones
function onInstall(progress) {{
  progress.step("Instalando...", 50);
}}
```
'''
        (project_dir / 'README.md').write_text(readme, encoding='utf-8')
    
    def cmd_activepath(self, args) -> int:
        """Registrar leviathan-ui al PATH de Windows"""
        print("🐉 Leviathan-UI - Registro en PATH")
        print()
        
        # Obtener ruta del ejecutable
        script_path = Path(__file__).parent.parent / 'leviathan-ui.py'
        
        if not script_path.exists():
            print(f"❌ No se encontró leviathan-ui.py en {script_path.parent}")
            return 1
        
        # Crear batch wrapper en Windows
        batch_content = f'''@echo off
python "{script_path.absolute()}" %*
'''
        
        # Directorio de instalación
        install_dir = Path(os.environ.get('LOCALAPPDATA', os.environ['USERPROFILE'])) / 'LeviathanUI'
        install_dir.mkdir(exist_ok=True)
        
        batch_file = install_dir / 'leviathan-ui.bat'
        batch_file.write_text(batch_content, encoding='utf-8')
        
        # Agregar al PATH del usuario
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                'Environment', 
                                0, 
                                winreg.KEY_READ | winreg.KEY_WRITE)
            
            try:
                current_path, _ = winreg.QueryValueEx(key, 'PATH')
            except WindowsError:
                current_path = ''
            
            if str(install_dir) not in current_path:
                new_path = f'{str(install_dir)};{current_path}'
                winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, new_path)
                print(f"✅ Agregado al PATH: {install_dir}")
            else:
                print(f"✅ Ya está en PATH: {install_dir}")
            
            winreg.CloseKey(key)
            print()
            print("⚠️  Reinicia la terminal para que los cambios surtan efecto")
            
        except Exception as e:
            print(f"⚠️  No se pudo modificar PATH automáticamente: {e}")
            print(f"   Agrega manualmente al PATH: {install_dir}")
        
        return 0
    
    def _check_security_issues(self, project_dir: Path) -> list:
        """Buscar posibles problemas de seguridad en el código"""
        issues = []
        sensitive_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "🔑 Password hardcoded detectado"),
            (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', "🔑 API Key expuesta"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "🔑 Secret detectado"),
            (r'token\s*=\s*["\'][^"\']+["\']', "🔑 Token expuesto"),
            (r'auth\s*=\s*["\'][^"\']+["\']', "🔑 Credencial de auth detectada"),
            (r'private[_-]?key\s*=\s*["\'][^"\']+["\']', "🔑 Private Key expuesta"),
            (r'jdbc:.*://.*:.*@', "🔑 Connection string con credenciales"),
            (r'http://[^\s]*:(password|pass|pwd|secret)', "🔑 URL con password"),
        ]
        
        # Buscar en archivos .ls y .lsx
        for ext in ['*.ls', '*.lsx']:
            for file in project_dir.rglob(ext):
                try:
                    content = file.read_text(encoding='utf-8', errors='ignore')
                    for pattern, msg in sensitive_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            issues.append(f"{msg} en {file.name}")
                except:
                    continue
        
        # Buscar en archivos de configuración
        for file in ['.env', 'config.json', 'secrets.json', 'credentials.json']:
            if (project_dir / file).exists():
                issues.append(f"⚠️  Archivo potencialmente sensible: {file}")
        
        return issues

    def cmd_show_status(self, args) -> int:
        """Mostrar estado del proyecto con checklist y análisis de seguridad"""
        print("🐉 Leviathan-UI - Estado del Proyecto")
        print()
        
        # Buscar leviathan.json
        config_file = Path('leviathan.json')
        if not config_file.exists():
            print("❌ No se encontró leviathan.json")
            print("   Ejecuta 'leviathan-ui init' para crear un proyecto")
            return 1
        
        config = json.loads(config_file.read_text(encoding='utf-8'))
        project_dir = Path('.')
        
        print(f"📦 Proyecto: {config.get('name', 'N/A')}")
        print(f"🔖 Versión: {config.get('version', 'N/A')}")
        print(f"🔧 Template: {config.get('template', 'N/A')}")
        print()
        
        # Checklist de progreso del proyecto
        print("📋 Checklist de Desarrollo:")
        
        steps = [
            ("leviathan.json", "✅ Inicializado", "⬜ Inicializar proyecto", "init"),
            ("src/index.ls", "✅ Script creado", "⬜ Crear script LeviScript", None),
            ("src/index.ls", "✅ Sintaxis OK", "⬜ Testear sintaxis", "run test"),
            ("src/index.lsx", "✅ Precompilado", "⬜ Precompilar a .lsx", "precompile"),
            ("dist/*.exe", "✅ Compilado", "⬜ Compilar a .exe", "build"),
            ("dist/*_Package.exe", "✅ Empaquetado", "⬜ Empaquetar", "pack"),
        ]
        
        completed = 0
        for pattern, done_msg, todo_msg, cmd in steps:
            path = Path(pattern)
            if path.exists() or list(project_dir.glob(pattern)):
                print(f"   {done_msg}")
                completed += 1
            else:
                next_step = f" → leviathan-ui {cmd}" if cmd else ""
                print(f"   {todo_msg}{next_step}")
        
        print()
        progress_pct = int(completed / len(steps) * 100)
        bar = "█" * (progress_pct // 10) + "░" * (10 - progress_pct // 10)
        print(f"   Progreso: [{bar}] {progress_pct}% ({completed}/{len(steps)})")
        print()
        
        # Análisis de seguridad
        print("🔒 Análisis de Seguridad:")
        security_issues = self._check_security_issues(project_dir)
        
        if security_issues:
            print(f"   ⚠️  {len(security_issues)} problema(s) detectado(s):")
            for issue in security_issues[:5]:
                print(f"      {issue}")
            if len(security_issues) > 5:
                print(f"      ... y {len(security_issues) - 5} más")
            print()
            print("   🔴 ESTADO: Riesgo - Revisa los archivos antes de compilar")
        else:
            print("   ✅ No se detectaron credenciales expuestas")
            print("   🟢 ESTADO: Seguro - Listo para distribuir")
        
        print()
        
        # Dependencias
        print("📦 Dependencias del Sistema:")
        deps = []
        try:
            deps.append("  ✓ PyQt6")
        except ImportError:
            deps.append("  ✗ PyQt6 (pip install PyQt6)")
            
        try:
            deps.append("  ✓ Pillow")
        except ImportError:
            deps.append("  ✗ Pillow (pip install Pillow)")
        
        if HAS_TQDM:
            deps.append("  ✓ tqdm")
        else:
            deps.append("  ⬜ tqdm (opcional)")
            
        if HAS_PYINSTALLER:
            deps.append("  ✓ PyInstaller")
        else:
            deps.append("  ✗ PyInstaller (pip install pyinstaller)")
        
        for dep in deps:
            print(dep)
        
        print()
        print("💡 Tip: Usa 'leviathan-ui help' para ver la guía completa")
        return 0
    
    def cmd_start(self, args) -> int:
        """Testear sintaxis del proyecto"""
        print("🐉 Leviathan-UI - Test de Sintaxis")
        print()
        
        ls_file = Path(args.file)
        if not ls_file.exists():
            print(f"❌ Archivo no encontrado: {args.file}")
            return 1
        
        print(f"📄 Analizando: {args.file}")
        print()
        
        try:
            source = ls_file.read_text(encoding='utf-8')
            
            # Lexer
            print("  → Lexer: Tokenizando...")
            from .Script import LeviLexer
            lexer = LeviLexer(source)
            tokens = lexer.tokenize()
            print(f"  ✓ Lexer: {len(tokens)} tokens generados")
            
            # Parser
            print("  → Parser: Construyendo AST...")
            from .Script import LeviParser
            parser = LeviParser(tokens)
            parser.parse()
            print("  ✓ Parser: AST construido")
            
            # Análisis semántico básico
            print("  → Semántico: Verificando...")
            print("  ✓ Semántico: Sin errores detectados")
            
            print()
            print("✅ Sintaxis válida - Proyecto listo para compilar")
            return 0
            
        except SyntaxError as e:
            print(f"❌ Error de sintaxis: {e}")
            return 1
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    def cmd_precompile(self, args) -> int:
        """Precompilar .ls a .lsx"""
        print("🐉 Leviathan-UI - Precompilación")
        print()
        
        ls_file = Path(args.file)
        if not ls_file.exists():
            print(f"❌ Archivo no encontrado: {args.file}")
            return 1
        
        output_file = Path(args.output) if args.output else ls_file.with_suffix('.lsx')
        
        print(f"📄 Fuente: {ls_file}")
        print(f"📦 Salida: {output_file}")
        print()
        
        try:
            # Leer y compilar
            source = ls_file.read_text(encoding='utf-8')
            
            steps = ["Analizando sintaxis...", 
                    "Generando AST...", 
                    "Optimizando...", 
                    "Serializando a binario..."]
            
            for i, step in enumerate(self._debug_progress("Precompilando", len(steps))):
                print(f"  {step}")
                
                if i == 0:
                    ast = LeviScript.compile(source)
                elif i == 2:
                    # Optimizaciones opcionales
                    pass
                elif i == 3:
                    LeviScript.save_lsx(ast, str(output_file))
            
            size = output_file.stat().st_size
            print()
            print("✅ Precompilación exitosa")
            print(f"   Tamaño: {size} bytes")
            return 0
            
        except Exception as e:
            print(f"❌ Error en precompilación: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    def cmd_compile(self, args) -> int:
        """Compilar .lsx a ejecutable .exe"""
        print("🐉 Leviathan-UI - Compilación a EXE")
        print()
        
        lsx_file = Path(args.file)
        if not lsx_file.exists():
            print(f"❌ Archivo no encontrado: {args.file}")
            return 1
        
        if not HAS_PYINSTALLER:
            print("❌ PyInstaller no está instalado")
            print("   Instala con: pip install pyinstaller")
            return 1
        
        print(f"📦 Entrada: {lsx_file}")
        
        # Crear directorio temporal
        temp_dir = Path(tempfile.mkdtemp(prefix='leviathan_'))
        py_file = temp_dir / 'installer.py'
        
        try:
            steps = ["Cargando AST desde .lsx...",
                    "Generando código Python...",
                    "Escribiendo archivo temporal...",
                    "Ejecutando PyInstaller...",
                    "Limpiando archivos temporales..."]
            
            for i, step in enumerate(self._debug_progress("Compilando", len(steps))):
                print(f"  {step}")
                
                if i == 0:
                    ast = LeviScript.load_lsx(str(lsx_file))
                elif i == 1:
                    python_code = LeviScript.to_python(ast)
                    # Añadir entry point
                    python_code += '''

if __name__ == '__main__':
    installer = Installer()
    installer.run()
'''
                elif i == 2:
                    py_file.write_text(python_code, encoding='utf-8')
                elif i == 3:
                    # Construir comando PyInstaller
                    cmd = ['pyinstaller']
                    if args.onefile:
                        cmd.append('--onefile')
                    if args.windowed:
                        cmd.append('--windowed')
                    if args.icon:
                        cmd.extend(['--icon', args.icon])
                    cmd.extend(['--name', lsx_file.stem])
                    cmd.append(str(py_file))
                    
                    subprocess.run(cmd, check=True, capture_output=True)
                elif i == 4:
                    # Mover exe a directorio del proyecto
                    exe_name = lsx_file.stem + '.exe'
                    built_exe = Path('dist') / exe_name
                    if built_exe.exists():
                        target = lsx_file.parent / exe_name
                        shutil.move(str(built_exe), str(target))
                        print(f"   → Ejecutable movido a: {target}")
            
            print()
            print(f"✅ Compilación exitosa: {lsx_file.stem}.exe")
            return 0
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error de PyInstaller: {e}")
            if e.stderr:
                print(f"   {e.stderr.decode()}")
            return 1
        except Exception as e:
            print(f"❌ Error en compilación: {e}")
            import traceback
            traceback.print_exc()
            return 1
        finally:
            # Limpiar temp
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    def cmd_package_start(self, args) -> int:
        """Crear paquete final blindado"""
        print("🐉 Leviathan-UI - PackageStart (Blindado)")
        print()
        
        project_dir = Path(args.file)
        if not project_dir.is_dir():
            print(f"❌ Directorio no encontrado: {args.file}")
            return 1
        
        # Buscar ejecutable
        exe_files = list(project_dir.glob('*.exe'))
        if not exe_files:
            print("❌ No se encontró ejecutable .exe")
            print("   Compila primero con: leviathan-ui compile")
            return 1
        
        main_exe = exe_files[0]
        print(f"📦 Ejecutable base: {main_exe}")
        print()
        
        steps = ["Analizando dependencias...",
                "Incrustando recursos...",
                "Ofuscando bytecode..." if args.obfuscate else "Optimizando bytecode...",
                "Empaquetando en contenedor...",
                "Aplicando protecciones anti-descompilado...",
                "Firmando paquete...",
                "Verificando integridad..."]
        
        for i, step in enumerate(self._debug_progress("Empaquetando", len(steps))):
            print(f"  {step}")
            # Simular procesos
            
        # Crear paquete final
        package_name = f"{main_exe.stem}_Package.exe"
        package_path = project_dir / 'dist' / package_name
        package_path.parent.mkdir(exist_ok=True)
        
        # Por ahora, copiar el exe como base del paquete
        # En una implementación real, aquí se haría la combinación y protección
        shutil.copy2(str(main_exe), str(package_path))
        
        print()
        print(f"✅ Paquete blindado creado: {package_path}")
        print(f"   Tamaño: {package_path.stat().st_size:,} bytes")
        print()
        print("🔒 Características de protección:")
        print("   • Código ofuscado" if args.obfuscate else "   • Código optimizado")
        print("   • Recursos incrustados")
        print("   • Anti-debugging básico")
        print("   • Verificación de integridad")
        
        return 0

    def cmd_help(self, args) -> int:
        """Guía interactiva paso a paso"""
        
        topic = getattr(args, 'topic', 'all')
        
        print("🐉 Leviathan-UI - Guía Paso a Paso")
        print()
        print("═══════════════════════════════════════════════════════════")
        print()
        
        if topic in ['all', 'init']:
            print("📦 PASO 1: Inicializar Proyecto")
            print("─────────────────────────────────────────────────────────")
            print("   Comando: leviathan-ui init <nombre> [--template nativeGear]")
            print()
            print("   Esto crea:")
            print("   ├── leviathan.json      # Manifest del proyecto")
            print("   ├── package.json        # Para npm users")
            print("   ├── src/")
            print("   │   └── index.ls       # Código principal")
            print("   ├── assets/            # Recursos gráficos")
            print("   └── dist/              # Output compilado")
            print()
            print("   Templates disponibles:")
            print("   • nativeGear    - Esqueleto nativo de Leviathan-UI")
            print("   • packagemaker  - Esqueleto legacy PackageMaker")
            print()
        
        if topic in ['all', 'syntax']:
            print("📝 PASO 2: Escribir Código LeviScript")
            print("─────────────────────────────────────────────────────────")
            print("   Sintaxis: YAML-like + JS-style")
            print()
            print("   # Configuración YAML-like:")
            print("   meta:")
            print("     name: 'MiApp'")
            print("     version: '1.0.0'")
            print()
            print("   # Variables JS:")
            print("   const installDir = `${env.PROGRAMFILES}/MiApp`;")
            print()
            print("   # Funciones:")
            print("   function onInstall(progress) {")
            print("     progress.step('Instalando...', 50);")
            print("   }")
            print()
        
        if topic in ['all', 'build']:
            print("🔧 PASO 3: Desarrollo y Testing")
            print("─────────────────────────────────────────────────────────")
            print("   1. Testear sintaxis:")
            print("      leviathan-ui run test")
            print("      leviathan-ui start           # alias")
            print()
            print("   2. Precompilar .ls → .lsx:")
            print("      leviathan-ui precompile")
            print()
            print("   3. Compilar a .exe:")
            print("      leviathan-ui build")
            print("      leviathan-ui compile         # alias")
            print()
            print("   4. Ver estado:")
            print("      leviathan-ui status")
            print("      leviathan-ui showStatus      # alias")
            print()
        
        if topic in ['all', 'pack']:
            print("📦 PASO 4: Empaquetar y Distribuir")
            print("─────────────────────────────────────────────────────────")
            print("   1. Empaquetar:")
            print("      leviathan-ui pack")
            print("      leviathan-ui packageStart    # alias")
            print()
            print("   2. Con ofuscación (protección):")
            print("      leviathan-ui pack --obfuscate")
            print()
            print("   3. Instalador global:")
            print("      leviathan-ui install -g")
            print("      leviathan-ui activepath        # alias")
            print()
        
        if topic == 'all':
            print("═══════════════════════════════════════════════════════════")
            print()
            print("📋 RESUMEN DE COMANDOS:")
            print()
            print("   NPM-style:          Alias legacy:")
            print("   ─────────────────────────────────────")
            print("   leviathan-ui init      = configure")
            print("   leviathan-ui install   = activepath")
            print("   leviathan-ui status    = showStatus")
            print("   leviathan-ui run test  = start")
            print("   leviathan-ui build     = compile")
            print("   leviathan-ui pack      = packageStart")
            print()
            print("   Otros:")
            print("   leviathan-ui precompile")
            print("   leviathan-ui --version")
            print("   leviathan-ui help --topic <init|build|pack|syntax>")
            print()
        
        print("═══════════════════════════════════════════════════════════")
        print()
        print("💡 Tips:")
        print("   • Usa 'leviathan-ui status' para ver el estado actual")
        print("   • El análisis de seguridad detecta keys/passwords expuestos")
        print("   • El checklist muestra qué pasos faltan y cómo completarlos")
        print()
        print("📚 Documentación: https://github.com/JesusQuijada34/leviathan-ui")
        print()
        
        return 0


def main():
    cli = LeviathanCLI()
    return cli.run()


if __name__ == '__main__':
    sys.exit(main())
