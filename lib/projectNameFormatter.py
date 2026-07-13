#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Project Name Formatter - Centraliza la lógica de formato de nombres para proyectos y paquetes.
Esta clase asegura consistencia en todos los formatos de nombres en el sistema.
"""

import time
from typing import Dict, Optional
from pathlib import Path


class ProjectNameFormatter:
    """Centraliza el formato de nombres para proyectos, paquetes y archivos .iflapp."""
    
    @staticmethod
    def get_timestamp() -> str:
        """Genera timestamp en formato YY.MM-HH.MM"""
        return time.strftime("%y.%m-%H.%M")
    
    @staticmethod
    def normalize_publisher(publisher: str) -> str:
        """Normaliza el nombre del publisher: minúsculas, guiones en lugar de espacios."""
        return publisher.strip().lower().replace(" ", "-") or "influent"
    
    @staticmethod
    def normalize_app_id(app_id: str) -> str:
        """Normaliza el ID de la aplicación: minúsculas, guiones en lugar de espacios."""
        return app_id.strip().lower().replace(" ", "-") or "myapp"
    
    @staticmethod
    def normalize_platform(platform: str) -> str:
        """Normaliza el nombre de plataforma al formato estándar."""
        p = (platform or "").strip().lower()
        if "win" in p or p in ("knosthalij", "windows"):
            return "Knosthalij"
        if "lin" in p or "danen" in p or p == "linux":
            return "Danenone"
        if "multi" in p or "alpha" in p:
            return "AlphaCube"
        return platform.strip() if platform else "Knosthalij"
    
    @staticmethod
    def format_version_vso(version_base: str) -> str:
        """Formatea la versión con timestamp: version_base-YY.MM-HH.MM"""
        version_clean = version_base.split("-")[0] if "-" in str(version_base) else str(version_base)
        return f"{version_clean}-{ProjectNameFormatter.get_timestamp()}"
    
    @staticmethod
    def format_version_full(version_base: str, platform: str) -> str:
        """Formatea la versión completa: version_base-YY.MM-HH.MM-Plataforma"""
        version_vso = ProjectNameFormatter.format_version_vso(version_base)
        platform_norm = ProjectNameFormatter.normalize_platform(platform)
        return f"{version_vso}-{platform_norm}"
    
    @classmethod
    def format_project_folder(
        cls, 
        publisher: str, 
        app_id: str, 
        version_base: str, 
        platform: str
    ) -> str:
        """
        Formatea el nombre de la carpeta del proyecto.
        Formato: publisher.app.vversion_base-YY.MM-HH.MM-Plataforma
        
        Args:
            publisher: Nombre del publisher/empresa
            app_id: ID corto de la aplicación
            version_base: Versión base (ej: "1.0.0")
            platform: Plataforma (Windows, Linux, etc.)
        
        Returns:
            Nombre formateado de la carpeta del proyecto
        """
        publisher_norm = cls.normalize_publisher(publisher)
        app_norm = cls.normalize_app_id(app_id)
        version_full = cls.format_version_full(version_base, platform)
        
        return f"{publisher_norm}.{app_norm}.v{version_full}"
    
    @classmethod
    def format_package_folder(
        cls,
        publisher: str,
        app_id: str,
        version: str,
        platform: str
    ) -> str:
        """
        Formatea el nombre de la carpeta del paquete compilado.
        Formato: publisher.app.version-Plataforma
        
        Args:
            publisher: Nombre del publisher/empresa
            app_id: ID corto de la aplicación
            version: Versión completa (con timestamp si viene de details.xml)
            platform: Plataforma (Windows, Linux, etc.)
        
        Returns:
            Nombre formateado de la carpeta del paquete
        """
        publisher_norm = cls.normalize_publisher(publisher)
        app_norm = cls.normalize_app_id(app_id)
        platform_norm = cls.normalize_platform(platform)
        
        # Limpiar versión de prefijos 'v' si existen
        version_clean = version.lstrip("v")
        
        return f"{publisher_norm}.{app_norm}.{version_clean}-{platform_norm}"
    
    @classmethod
    def format_iflapp_filename(
        cls,
        publisher: str,
        app_id: str,
        version: str,
        platform: str
    ) -> str:
        """
        Formatea el nombre del archivo .iflapp.
        Formato: publisher.app.version-Plataforma.iflapp
        
        Args:
            publisher: Nombre del publisher/empresa
            app_id: ID corto de la aplicación
            version: Versión completa (con timestamp si viene de details.xml)
            platform: Plataforma (Windows, Linux, etc.)
        
        Returns:
            Nombre formateado del archivo .iflapp
        """
        package_name = cls.format_package_folder(publisher, app_id, version, platform)
        return f"{package_name}.iflapp"
    
    @classmethod
    def format_from_metadata(cls, metadata: Dict[str, str]) -> Dict[str, str]:
        """
        Genera todos los formatos de nombres a partir de metadatos.
        
        Args:
            metadata: Diccionario con claves: publisher, app, version, platform
        
        Returns:
            Diccionario con todos los formatos de nombres:
            - project_folder: Nombre de carpeta del proyecto
            - package_folder: Nombre de carpeta del paquete
            - iflapp_filename: Nombre del archivo .iflapp
            - version_vso: Versión con timestamp
            - version_full: Versión completa con plataforma
        """
        publisher = metadata.get("publisher", metadata.get("empresa", "influent"))
        app_id = metadata.get("app", metadata.get("name", "myapp"))
        version = metadata.get("version", "1.0.0")
        platform = metadata.get("platform", metadata.get("plataforma", "Knosthalij"))
        
        version_base = version.split("-")[0] if "-" in str(version) else str(version)
        
        return {
            "project_folder": cls.format_project_folder(publisher, app_id, version_base, platform),
            "package_folder": cls.format_package_folder(publisher, app_id, version, platform),
            "iflapp_filename": cls.format_iflapp_filename(publisher, app_id, version, platform),
            "version_vso": cls.format_version_vso(version_base),
            "version_full": cls.format_version_full(version_base, platform),
        }
    
    @classmethod
    def parse_project_folder(cls, folder_name: str) -> Optional[Dict[str, str]]:
        """
        Intenta parsear un nombre de carpeta de proyecto para extraer metadatos.
        
        Args:
            folder_name: Nombre de la carpeta del proyecto
        
        Returns:
            Diccionario con metadatos extraídos o None si no se puede parsear
        """
        try:
            # Formato esperado: publisher.app.vversion-YY.MM-HH.MM-Plataforma
            if not folder_name.startswith("v"):
                return None
            
            parts = folder_name.split(".")
            if len(parts) < 3:
                return None
            
            publisher = parts[0]
            app = parts[1]
            version_part = ".".join(parts[2:])
            
            # Extraer versión y plataforma
            if "-" in version_part:
                version_platform = version_part.split("-")
                version = "-".join(version_platform[:-1])
                platform = version_platform[-1]
            else:
                version = version_part
                platform = "Knosthalij"
            
            return {
                "publisher": publisher,
                "app": app,
                "version": version.lstrip("v"),
                "platform": platform,
            }
        except Exception:
            return None
