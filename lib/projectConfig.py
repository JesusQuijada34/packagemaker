# -*- coding: utf-8 -*-
"""
Gestor de configuración de proyectos en formato JSON.
Almacena opciones predeterminadas para abrir proyectos con editores específicos.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any


class ProjectConfig:
    """Gestiona la configuración de proyectos en formato JSON."""
    
    def __init__(self, base_dir: str = None):
        """Inicializa el gestor de configuración."""
        if base_dir is None:
            self.base_dir = Path(__file__).parent.parent
        else:
            self.base_dir = Path(base_dir)
        
        self.config_dir = self.base_dir / "config"
        self.config_file = self.config_dir / "project_config.json"
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Asegura que el directorio de configuración exista."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            # Base de proyecto de solo lectura: se opera con la configuración
            # vacía y ``save_config`` avisará si tampoco puede escribir.
            print(f"[WARN] No se pudo crear {self.config_dir}: {exc}")
    
    def get_config(self) -> Dict[str, Any]:
        """Carga la configuración desde el archivo JSON."""
        try:
            if not self.config_file.is_file():
                return {}
        except OSError:
            # Base inaccesible: se opera con la configuración vacía.
            return {}
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            return loaded if isinstance(loaded, dict) else {}
        except Exception as e:
            print(f"[ERROR] Error cargando configuración: {e}")
            return {}
    
    def save_config(self, config: Dict[str, Any]):
        """Guarda la configuración en el archivo JSON."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[ERROR] Error guardando configuración: {e}")
    
    def get_project_editor(self, project_path: str) -> Optional[str]:
        """
        Obtiene el editor preferido para un proyecto específico.
        
        Args:
            project_path: Ruta del proyecto
        
        Returns:
            Nombre del editor preferido, o None si no hay configuración
        """
        config = self.get_config()
        projects = config.get('projects', {})
        if not isinstance(projects, dict):
            return None
        
        # Usar la ruta como clave
        return projects.get(project_path)
    
    def set_project_editor(self, project_path: str, editor_name: str):
        """
        Establece el editor preferido para un proyecto.
        
        Args:
            project_path: Ruta del proyecto
            editor_name: Nombre del editor
        """
        config = self.get_config()
        
        if not isinstance(config.get('projects'), dict):
            config['projects'] = {}
        
        config['projects'][project_path] = editor_name
        self.save_config(config)
    
    def remove_project_editor(self, project_path: str):
        """
        Elimina la configuración de editor para un proyecto.
        
        Args:
            project_path: Ruta del proyecto
        """
        config = self.get_config()
        
        projects = config.get('projects')
        if isinstance(projects, dict) and project_path in projects:
            del projects[project_path]
            self.save_config(config)
    
    def get_editor_path(self, editor_name: str) -> Optional[str]:
        """
        Obtiene la ruta del ejecutable de un editor.
        
        Args:
            editor_name: Nombre del editor
        
        Returns:
            Ruta del ejecutable, o None si no hay configuración
        """
        config = self.get_config()
        editors = config.get('editors', {})
        if not isinstance(editors, dict):
            return None
        
        return editors.get(editor_name)
    
    def set_editor_path(self, editor_name: str, exe_path: str):
        """
        Establece la ruta del ejecutable de un editor.
        
        Args:
            editor_name: Nombre del editor
            exe_path: Ruta del ejecutable
        """
        config = self.get_config()
        
        if not isinstance(config.get('editors'), dict):
            config['editors'] = {}
        
        config['editors'][editor_name] = exe_path
        self.save_config(config)


# Instancia global del gestor de configuración
_project_config_instance = None

def get_project_config(base_dir: str = None) -> ProjectConfig:
    """Retorna la instancia global del gestor de configuración (singleton)."""
    global _project_config_instance
    if _project_config_instance is None:
        _project_config_instance = ProjectConfig(base_dir)
    return _project_config_instance
