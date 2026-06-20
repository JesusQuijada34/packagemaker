# -*- coding: utf-8 -*-
"""
Detector de modo de ejecución para PackageMaker.
Detecta si la aplicación está ejecutándose como script Python o como ejecutable compilado (frozen).
"""

import sys
import os
import platform
from pathlib import Path


class ExecutionMode:
    """Detecta y gestiona el modo de ejecución de la aplicación."""
    
    def __init__(self):
        """Inicializa el detector de modo de ejecución."""
        self._is_frozen = self._detect_frozen()
        self._executable_path = self._get_executable_path()
        self._executable_name = self._get_executable_name()
        self._system = platform.system().lower()
    
    def _detect_frozen(self) -> bool:
        """
        Detecta si la aplicación está ejecutándose como ejecutable compilado (frozen).
        
        Returns:
            True si está frozen, False si está ejecutándose como script Python
        """
        # PyInstaller, cx_Freeze, etc. establecen sys.frozen
        if getattr(sys, 'frozen', False):
            return True
        
        # Detectar PyInstaller
        if hasattr(sys, '_MEIPASS'):
            return True
        
        # Detectar cx_Freeze
        if hasattr(sys, 'cx_Freeze'):
            return True
        
        # Detectar Nuitka
        if '__compiled__' in globals():
            return True
        
        return False
    
    def _get_executable_path(self) -> str:
        """
        Obtiene la ruta del ejecutable actual.
        
        Returns:
            Ruta del ejecutable o script
        """
        if self._is_frozen:
            return sys.executable
        else:
            return os.path.abspath(sys.argv[0])
    
    def _get_executable_name(self) -> str:
        """
        Obtiene el nombre del ejecutable con extensión apropiada.
        
        Returns:
            Nombre del ejecutable (ej: packagemaker.exe, packagemaker.elf, packagemaker)
        """
        if self._is_frozen:
            # Usar el nombre del ejecutable actual
            return os.path.basename(sys.executable)
        else:
            # Como script, usar nombre del script con extensión .py
            script_name = os.path.basename(sys.argv[0])
            if script_name.endswith('.py'):
                return script_name
            return f"{script_name}.py"
    
    def get_executable_extension(self) -> str:
        """
        Obtiene la extensión del ejecutable según el sistema operativo y modo.
        
        Returns:
            Extensión del ejecutable (ej: .exe, .elf, .app, '')
        """
        if self._is_frozen:
            # Si está frozen, usar la extensión actual
            _, ext = os.path.splitext(self._executable_name)
            return ext
        else:
            # Como script, extensión depende del sistema
            if self._system == 'windows':
                return '.exe'
            elif self._system == 'linux':
                return '.elf'
            elif self._system == 'darwin':
                return '.app'
            else:
                return ''
    
    def get_command_name(self) -> str:
        """
        Obtiene el nombre del comando para mostrar en la línea de comandos.
        
        Returns:
            Nombre del comando (ej: packagemaker, packagemaker.exe, etc.)
        """
        base_name = os.path.splitext(self._executable_name)[0]
        
        if self._is_frozen:
            # Si está frozen, usar el nombre completo con extensión
            return self._executable_name
        else:
            # Como script, mostrar como si fuera ejecutable
            ext = self.get_executable_extension()
            return f"{base_name}{ext}"
    
    def get_base_directory(self) -> str:
        """
        Obtiene el directorio base de la aplicación.
        
        Returns:
            Ruta del directorio base
        """
        if self._is_frozen:
            # PyInstaller: sys._MEIPASS contiene el directorio temporal
            if hasattr(sys, '_MEIPASS'):
                return sys._MEIPASS
            # cx_Freeze: sys.executable está en el directorio de la app
            return os.path.dirname(sys.executable)
        else:
            # Como script: directorio del script
            return os.path.dirname(os.path.abspath(sys.argv[0]))
    
    def is_frozen(self) -> bool:
        """Retorna si la aplicación está ejecutándose como ejecutable compilado."""
        return self._is_frozen
    
    def get_system(self) -> str:
        """Retorna el sistema operativo."""
        return self._system
    
    def get_platform_info(self) -> dict:
        """
        Retorna información completa de la plataforma y modo de ejecución.
        
        Returns:
            Diccionario con información de la plataforma
        """
        return {
            'frozen': self._is_frozen,
            'executable_path': self._executable_path,
            'executable_name': self._executable_name,
            'command_name': self.get_command_name(),
            'executable_extension': self.get_executable_extension(),
            'base_directory': self.get_base_directory(),
            'system': self._system,
            'python_version': sys.version,
            'platform': platform.platform(),
        }
    
    def adjust_paths_for_mode(self, *paths: str) -> tuple:
        """
        Ajusta las rutas según el modo de ejecución.
        
        Args:
            *paths: Rutas a ajustar
        
        Returns:
            Tupla de rutas ajustadas
        """
        base_dir = self.get_base_directory()
        adjusted_paths = []
        
        for path in paths:
            if os.path.isabs(path):
                # Ruta absoluta, mantenerla
                adjusted_paths.append(path)
            else:
                # Ruta relativa, ajustar al directorio base
                adjusted_paths.append(os.path.join(base_dir, path))
        
        return tuple(adjusted_paths)


# Instancia global del detector de modo de ejecución
_execution_mode_instance = None

def get_execution_mode() -> 'ExecutionMode':
    """Retorna la instancia global del detector de modo de ejecución (singleton)."""
    global _execution_mode_instance
    if _execution_mode_instance is None:
        _execution_mode_instance = ExecutionMode()
    return _execution_mode_instance


def is_frozen() -> bool:
    """Función de conveniencia para verificar si está frozen."""
    return get_execution_mode().is_frozen()


def get_command_name() -> str:
    """Función de conveniencia para obtener el nombre del comando."""
    return get_execution_mode().get_command_name()
