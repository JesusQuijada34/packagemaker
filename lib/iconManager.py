# -*- coding: utf-8 -*-
"""
IconManager - Sistema de carga de iconos SVG dinámicos con color adaptable.
Implementa iconos estilo Fluent System Icons con soporte para currentColor.
"""

import os
import re
from pathlib import Path
from typing import Optional
from xml.etree import ElementTree as ET

try:
    from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
    from PyQt6.QtCore import Qt, QSize
    from PyQt6.QtSvgWidgets import QSvgRenderer
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False


class IconManager:
    """Gestor centralizado para cargar y procesar iconos SVG con color dinámico."""
    
    def __init__(self, base_dir: str = None):
        """Inicializa el IconManager con el directorio base del proyecto."""
        if base_dir is None:
            self.base_dir = Path(__file__).parent.parent
        else:
            self.base_dir = Path(base_dir)
        
        self.icons_dir = self.base_dir / "assets" / "icons"
        self._ensure_icons_dir()
    
    def _ensure_icons_dir(self):
        """Asegura que el directorio de iconos exista."""
        self.icons_dir.mkdir(parents=True, exist_ok=True)
    
    def load_svg(self, icon_name: str, size: int = 24, color_role: str = 'primary') -> Optional[QPixmap]:
        """
        Carga un icono SVG y lo procesa para usar currentColor.
        
        Args:
            icon_name: Nombre del archivo SVG (sin extensión)
            size: Tamaño del icono en píxeles
            color_role: Rol de color ('primary', 'secondary', 'accent', etc.)
        
        Returns:
            QPixmap con el icono procesado, o None si falla
        """
        if not PYQT6_AVAILABLE:
            return None
        
        svg_path = self.icons_dir / f"{icon_name}.svg"
        
        if not svg_path.exists():
            # Intentar crear un icono por defecto
            return self._create_default_icon(icon_name, size)
        
        try:
            # Leer el contenido SVG
            with open(svg_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()
            
            # Procesar el SVG para asegurar currentColor
            processed_svg = self._process_svg_for_currentcolor(svg_content)
            
            # Renderizar el SVG a QPixmap
            return self._render_svg_to_pixmap(processed_svg, size)
        
        except Exception as e:
            print(f"[ERROR] Error cargando icono {icon_name}: {e}")
            return self._create_default_icon(icon_name, size)
    
    def _process_svg_for_currentcolor(self, svg_content: str) -> str:
        """
        Procesa el contenido SVG para usar currentColor en lugar de colores fijos.
        
        Args:
            svg_content: Contenido original del SVG
        
        Returns:
            Contenido SVG procesado con currentColor
        """
        # Reemplazar colores hex comunes por currentColor
        # Esto permite que el icono tome el color del widget padre vía QSS
        color_patterns = [
            (r'#000000', 'currentColor'),
            (r'#000', 'currentColor'),
            (r'fill="#[0-9a-fA-F]{6}"', 'fill="currentColor"'),
            (r'stroke="#[0-9a-fA-F]{6}"', 'stroke="currentColor"'),
        ]
        
        processed = svg_content
        for pattern, replacement in color_patterns:
            processed = re.sub(pattern, replacement, processed)
        
        return processed
    
    def _render_svg_to_pixmap(self, svg_content: str, size: int) -> QPixmap:
        """
        Renderiza contenido SVG a un QPixmap del tamaño especificado.
        
        Args:
            svg_content: Contenido SVG procesado
            size: Tamaño del pixmap resultante
        
        Returns:
            QPixmap con el SVG renderizado
        """
        renderer = QSvgRenderer()
        renderer.load(svg_content.encode('utf-8'))
        
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        renderer.render(painter)
        painter.end()
        
        return pixmap
    
    def _create_default_icon(self, name: str, size: int) -> Optional[QPixmap]:
        """
        Crea un icono por defecto simple cuando no existe el archivo.
        
        Args:
            name: Nombre del icono (para referencia)
            size: Tamaño del icono
        
        Returns:
            QPixmap con un icono por defecto
        """
        if not PYQT6_AVAILABLE:
            return None
        
        # SVG simple de un cuadrado con bordes redondeados
        default_svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="3" y="3" width="18" height="18" rx="4" fill="currentColor"/>
</svg>'''
        
        return self._render_svg_to_pixmap(default_svg, size)
    
    def get_icon_path(self, icon_name: str) -> Optional[str]:
        """
        Retorna la ruta completa de un icono SVG.
        
        Args:
            icon_name: Nombre del icono (sin extensión)
        
        Returns:
            Ruta completa al archivo SVG, o None si no existe
        """
        svg_path = self.icons_dir / f"{icon_name}.svg"
        return str(svg_path) if svg_path.exists() else None


# Instancia global del IconManager
_icon_manager_instance = None

def get_icon_manager(base_dir: str = None) -> IconManager:
    """Retorna la instancia global del IconManager (singleton)."""
    global _icon_manager_instance
    if _icon_manager_instance is None:
        _icon_manager_instance = IconManager(base_dir)
    return _icon_manager_instance


def load_svg_icon(icon_name: str, size: int = 24, color_role: str = 'primary') -> Optional[QPixmap]:
    """
    Función de conveniencia para cargar un icono SVG.
    
    Args:
        icon_name: Nombre del icono (sin extensión)
        size: Tamaño del icono
        color_role: Rol de color para QSS
    
    Returns:
        QPixmap con el icono procesado
    """
    manager = get_icon_manager()
    return manager.load_svg(icon_name, size, color_role)


# Iconos Fluent System Icons básicos (para referencia)
FLUENT_ICONS = {
    'open': 'Icono de abrir/carpeta',
    'app': 'Icono de aplicación genérico',
    'checkmark': 'Icono de check/marca',
    'chevron_right': 'Flecha hacia derecha',
    'chevron_down': 'Flecha hacia abajo',
    'filter': 'Icono de filtro',
    'sort': 'Icono de orden',
    'settings': 'Icono de configuración',
    'close': 'Icono de cerrar',
    'add': 'Icono de agregar',
    'remove': 'Icono de eliminar',
}
