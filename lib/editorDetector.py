# -*- coding: utf-8 -*-
"""
Detector de editores de código para PackageMaker.
Detecta editores instalados en Windows y Linux.
"""

import os
import sys
import glob
import platform
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple


@dataclass
class EditorInfo:
    """Información de un editor detectado."""
    name: str
    display_name: str
    executable: str
    icon_path: Optional[str] = None
    command_template: str = "{exe} {path}"
    priority: int = 0


# Definición de editores soportados
EDITORS_CONFIG = {
    # Editores populares
    "code": EditorInfo(
        name="code",
        display_name="Visual Studio Code",
        executable="code" if sys.platform != "win32" else "Code.exe",
        command_template='"{exe}" "{path}"',
        priority=100
    ),
    "cursor": EditorInfo(
        name="cursor",
        display_name="Cursor",
        executable="Cursor" if sys.platform != "win32" else "Cursor.exe",
        command_template='"{exe}" "{path}"',
        priority=95
    ),
    "windsurf": EditorInfo(
        name="windsurf",
        display_name="Windsurf",
        executable="windsurf" if sys.platform != "win32" else "Windsurf.exe",
        command_template='"{exe}" "{path}"',
        priority=90
    ),
    "trae": EditorInfo(
        name="trae",
        display_name="Trae AI",
        executable="Trae" if sys.platform != "win32" else "Trae.exe",
        command_template='"{exe}" "{path}"',
        priority=85
    ),
    # Editores IA/Especializados
    "antigravity": EditorInfo(
        name="antigravity",
        display_name="Antigravity",
        executable="Antigravity.exe" if sys.platform == "win32" else "antigravity",
        command_template='"{exe}" "{path}"',
        priority=82,
    ),
    "anigravity": EditorInfo(
        name="anigravity",
        display_name="Antigravity",
        executable="Antigravity.exe" if sys.platform == "win32" else "anigravity",
        command_template='"{exe}" "{path}"',
        priority=81,
    ),
    "kiro": EditorInfo(
        name="kiro",
        display_name="Kiro",
        executable="kiro" if sys.platform != "win32" else "Kiro.exe",
        command_template='"{exe}" "{path}"',
        priority=75
    ),
    "codex": EditorInfo(
        name="codex",
        display_name="Codex",
        executable="codex" if sys.platform != "win32" else "Codex.exe",
        command_template='"{exe}" "{path}"',
        priority=70
    ),
    "pear": EditorInfo(
        name="pear",
        display_name="Pear AI",
        executable="pear" if sys.platform != "win32" else "PearAI.exe",
        command_template='"{exe}" "{path}"',
        priority=65
    ),
    "claude": EditorInfo(
        name="claude",
        display_name="Claude Code",
        executable="claude" if sys.platform != "win32" else "claude.exe",
        command_template='"{exe}" "{path}"',
        priority=60
    ),
    # Editores tradicionales
    "sublime_text": EditorInfo(
        name="sublime_text",
        display_name="Sublime Text",
        executable="subl" if sys.platform != "win32" else "subl.exe",
        command_template='"{exe}" "{path}"',
        priority=55
    ),
    "atom": EditorInfo(
        name="atom",
        display_name="Atom",
        executable="atom" if sys.platform != "win32" else "atom.exe",
        command_template='"{exe}" "{path}"',
        priority=50
    ),
    "notepad++": EditorInfo(
        name="notepad++",
        display_name="Notepad++",
        executable="notepad++.exe",
        command_template='"{exe}" "{path}"',
        priority=45
    ),
    "nvim": EditorInfo(
        name="nvim",
        display_name="Neovim",
        executable="nvim" if sys.platform != "win32" else "nvim.exe",
        command_template='"{exe}" "{path}"',
        priority=40
    ),
    "vim": EditorInfo(
        name="vim",
        display_name="Vim",
        executable="vim" if sys.platform != "win32" else "vim.exe",
        command_template='"{exe}" "{path}"',
        priority=35
    ),
    # IDEs completos
    "pycharm": EditorInfo(
        name="pycharm",
        display_name="PyCharm",
        executable="pycharm" if sys.platform != "win32" else "pycharm64.exe",
        command_template='"{exe}" "{path}"',
        priority=30
    ),
    "intellij": EditorInfo(
        name="intellij",
        display_name="IntelliJ IDEA",
        executable="idea" if sys.platform != "win32" else "idea64.exe",
        command_template='"{exe}" "{path}"',
        priority=25
    ),
    "webstorm": EditorInfo(
        name="webstorm",
        display_name="WebStorm",
        executable="webstorm" if sys.platform != "win32" else "webstorm64.exe",
        command_template='"{exe}" "{path}"',
        priority=20
    ),
    "zed": EditorInfo(
        name="zed",
        display_name="Zed",
        executable="zed" if sys.platform != "win32" else "zed.exe",
        command_template='"{exe}" "{path}"',
        priority=18
    ),
    "fleet": EditorInfo(
        name="fleet",
        display_name="Fleet",
        executable="fleet" if sys.platform != "win32" else "fleet.exe",
        command_template='"{exe}" "{path}"',
        priority=15
    ),
    "emacs": EditorInfo(
        name="emacs",
        display_name="Emacs",
        executable="emacs" if sys.platform != "win32" else "emacs.exe",
        command_template='"{exe}" "{path}"',
        priority=12
    ),
    "geany": EditorInfo(
        name="geany",
        display_name="Geany",
        executable="geany" if sys.platform != "win32" else "geany.exe",
        command_template='"{exe}" "{path}"',
        priority=10
    ),
    "kate": EditorInfo(
        name="kate",
        display_name="Kate",
        executable="kate" if sys.platform != "win32" else "kate.exe",
        command_template='"{exe}" "{path}"',
        priority=8
    ),
    "gedit": EditorInfo(
        name="gedit",
        display_name="Gedit",
        executable="gedit" if sys.platform != "win32" else "gedit.exe",
        command_template='"{exe}" "{path}"',
        priority=5
    ),
}


class EditorDetector:
    """Detecta editores instalados en el sistema."""
    
    def __init__(self):
        self.platform = sys.platform
        self.found_editors: List[Tuple[EditorInfo, str]] = []
        self._search_paths: List[str] = []
        self._setup_search_paths()
    
    def _setup_search_paths(self):
        """Configura las rutas de búsqueda según la plataforma."""
        if self.platform == "win32":
            # Windows: Rutas comunes de instalación
            program_files = [
                os.environ.get("ProgramFiles", "C:\\Program Files"),
                os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
                os.environ.get("LOCALAPPDATA", ""),
                os.environ.get("APPDATA", ""),
                os.path.expanduser("~"),
            ]
            
            # Editor-specific paths for Windows
            editor_paths = [
                # VS Code
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Microsoft VS Code"),
                # VS Code Insiders
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Microsoft VS Code Insiders"),
                # Cursor
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "cursor"),
                # Windsurf
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Windsurf"),
                # Trae
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Trae"),
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Trae AI"),
                # Antigravity
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Antigravity"),
                # Pear AI
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "PearAI"),
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "pearai"),
                # Kiro
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Kiro"),
                # Sublime Text
                os.path.join(os.environ.get("ProgramFiles", ""), "Sublime Text"),
                os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Sublime Text"),
                # Notepad++
                os.path.join(os.environ.get("ProgramFiles", ""), "Notepad++"),
                # PyCharm
                os.path.join(os.environ.get("ProgramFiles", ""), "JetBrains", "PyCharm"),
                # IntelliJ
                os.path.join(os.environ.get("ProgramFiles", ""), "JetBrains", "IntelliJ IDEA"),
            ]
            
            self._search_paths = program_files + editor_paths
            
        else:
            # Linux/macOS: PATH + rutas comunes
            path_env = os.environ.get("PATH", "")
            self._search_paths = path_env.split(os.pathsep) + [
                "/usr/bin",
                "/usr/local/bin",
                "/opt",
                "/snap/bin",
                os.path.expanduser("~/.local/bin"),
                os.path.expanduser("~/.npm-global/bin"),
                "/Applications",  # macOS
                "/Applications/Visual Studio Code.app/Contents/Resources/app/bin",
                "/Applications/Cursor.app/Contents/Resources/app/bin",
                "/Applications/Windsurf.app/Contents/Resources/app/bin",
                "/Applications/Antigravity.app/Contents/MacOS",
                "/Applications/PearAI.app/Contents/MacOS",
                "/Applications/Kiro.app/Contents/MacOS",
            ]
    
    def _find_executable(self, editor_info: EditorInfo) -> Optional[str]:
        """Busca el ejecutable de un editor en el sistema."""
        exe_name = editor_info.executable
        
        if self.platform == "win32":
            # En Windows, buscar en rutas específicas y PATH
            for search_path in self._search_paths:
                if not search_path:
                    continue
                    
                # Buscar exacto
                full_path = os.path.join(search_path, exe_name)
                if os.path.isfile(full_path):
                    return full_path
                
                # Buscar con glob para variantes
                pattern = os.path.join(search_path, exe_name.replace(".exe", "*.exe"))
                matches = glob.glob(pattern)
                if matches:
                    return matches[0]
            
            # Buscar en PATH usando where
            try:
                import subprocess
                result = subprocess.run(
                    ["where", exe_name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    paths = result.stdout.strip().split("\n")
                    if paths:
                        return paths[0].strip()
            except:
                pass
                
        else:
            # Linux/macOS: usar which o buscar en PATH
            try:
                import subprocess
                result = subprocess.run(
                    ["which", exe_name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return result.stdout.strip()
            except:
                pass
            
            # Buscar manualmente en rutas
            for search_path in self._search_paths:
                if not search_path:
                    continue
                full_path = os.path.join(search_path, exe_name)
                if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                    return full_path
        
        return None
    
    def _extract_icon(self, exe_path: str) -> Optional[str]:
        """Extrae el icono de un ejecutable (Windows) o busca iconos en Linux."""
        if self.platform == "win32":
            try:
                # Guardar icono temporalmente
                import tempfile
                temp_dir = tempfile.gettempdir()
                icon_path = os.path.join(temp_dir, f"editor_icon_{os.path.basename(exe_path)}.ico")
                
                # Intentar extraer icono usando win32api si está disponible
                try:
                    import win32api
                    import win32con
                    
                    # Cargar el icono del ejecutable
                    large_icon, small_icon = win32api.ExtractIconEx(exe_path, 0, 1, 1)
                    if large_icon:
                        # Guardar como ICO (simplificado - en producción usar PIL)
                        return None  # TODO: Implementar extracción real
                except ImportError:
                    pass
                
                # Fallback: buscar icono en carpeta del ejecutable
                exe_dir = os.path.dirname(exe_path)
                possible_icons = [
                    os.path.join(exe_dir, "resources", "app", "icon.ico"),
                    os.path.join(exe_dir, "resources", "icon.ico"),
                    os.path.join(exe_dir, "icon.ico"),
                    os.path.join(exe_dir, "app.ico"),
                ]
                
                for icon in possible_icons:
                    if os.path.exists(icon):
                        return icon
            except Exception:
                pass
        elif self.platform.startswith("linux"):
            # En Linux, buscar en rutas de iconos estándar
            icon_name = os.path.basename(exe_path).lower()
            # Casos especiales de nombres de iconos
            icon_map = {
                "code": "visual-studio-code",
                "subl": "sublime-text",
                "nvim": "nvim",
                "vim": "vim",
                "pycharm": "pycharm",
                "idea": "intellij-idea-ultimate",
                "zed": "zed",
            }
            search_name = icon_map.get(icon_name, icon_name)
            
            # Buscar en directorios de iconos comunes
            icon_dirs = [
                "/usr/share/icons/hicolor/48x48/apps",
                "/usr/share/icons/hicolor/64x64/apps",
                "/usr/share/icons/hicolor/128x128/apps",
                "/usr/share/icons/hicolor/scalable/apps",
                "/usr/share/pixmaps",
                os.path.expanduser("~/.local/share/icons"),
            ]
            
            for d in icon_dirs:
                if not os.path.isdir(d): continue
                for ext in [".png", ".svg", ".ico"]:
                    icon_path = os.path.join(d, search_name + ext)
                    if os.path.exists(icon_path):
                        return icon_path
                        
            # Si no se encuentra, intentar buscar por nombre parcial
            for d in icon_dirs:
                if not os.path.isdir(d): continue
                matches = glob.glob(os.path.join(d, f"*{search_name}*"))
                if matches:
                    return matches[0]
                    
        return None
    
    def detect_editors(self) -> List[Tuple[EditorInfo, str]]:
        """Detecta todos los editores instalados."""
        found = []
        
        seen_paths = set()
        for editor_id, editor_info in EDITORS_CONFIG.items():
            exe_path = self._find_executable(editor_info)
            if exe_path and exe_path not in seen_paths:
                seen_paths.add(exe_path)
                icon = self._extract_icon(exe_path)
                info = EditorInfo(
                    name=editor_info.name,
                    display_name=editor_info.display_name,
                    executable=editor_info.executable,
                    icon_path=icon,
                    command_template=editor_info.command_template,
                    priority=editor_info.priority,
                )
                found.append((info, exe_path))
        
        # Ordenar por prioridad
        found.sort(key=lambda x: x[0].priority, reverse=True)
        
        self.found_editors = found
        return found
    
    def get_command(self, editor_info: EditorInfo, exe_path: str, project_path: str) -> str:
        """Genera el comando para abrir un proyecto."""
        return editor_info.command_template.format(exe=exe_path, path=project_path)
    
    def launch_editor(self, editor_info: EditorInfo, exe_path: str, project_path: str) -> bool:
        """Abre un proyecto con el editor especificado."""
        import subprocess
        
        try:
            cmd = self.get_command(editor_info, exe_path, project_path)
            # Usar shell=True en Windows para manejar paths con espacios
            subprocess.Popen(cmd, shell=(self.platform == "win32"), close_fds=True)
            return True
        except Exception as e:
            print(f"[ERROR] No se pudo lanzar {editor_info.display_name}: {e}")
            return False


def get_available_editors() -> List[Tuple[EditorInfo, str]]:
    """Función de conveniencia para obtener editores disponibles."""
    detector = EditorDetector()
    return detector.detect_editors()


def _config_file_path() -> Path:
    return Path(__file__).resolve().parent.parent / "config" / "settings.json"


def save_default_editor(editor_name: str):
    """Guarda el editor predeterminado en settings.json."""
    import json
    cfg_path = _config_file_path()
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    data = {}
    if cfg_path.is_file():
        try:
            data = json.loads(cfg_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {}
    data["default_editor"] = editor_name
    cfg_path.write_text(json.dumps(data, indent=4), encoding="utf-8")


def get_default_editor() -> Optional[str]:
    """Obtiene el editor predeterminado de settings.json."""
    import json
    cfg_path = _config_file_path()
    if not cfg_path.is_file():
        return None
    try:
        return json.loads(cfg_path.read_text(encoding="utf-8")).get("default_editor")
    except (json.JSONDecodeError, OSError):
        return None


if __name__ == "__main__":
    # Test
    print("Detectando editores...")
    detector = EditorDetector()
    editors = detector.detect_editors()
    
    print(f"\nEditores encontrados ({len(editors)}):")
    for editor, path in editors:
        print(f"  - {editor.display_name}: {path}")
        if editor.icon_path:
            print(f"    Icono: {editor.icon_path}")
