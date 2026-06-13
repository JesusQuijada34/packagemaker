#!/usr/bin/env python3
"""
Script de validación y optimización de PackageMaker para Linux.
Ejecutar antes de compilar para asegurar configuración correcta.
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def check_system() -> dict:
    """Verifica requisitos del sistema"""
    result = {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "python_path": sys.executable,
        "platform": sys.platform,
        "venv_active": hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix),
    }
    return result


def check_dependencies() -> dict:
    """Verifica dependencias necesarias"""
    deps = {
        "PyQt6": False,
        "PyInstaller": False,
        "PIL": False,
        "requests": False,
        "leviathan_ui": False,
    }
    
    for dep in deps:
        try:
            __import__(dep.lower().replace("-", "_"))
            deps[dep] = True
        except ImportError:
            deps[dep] = False
    
    return deps


def check_system_tools() -> dict:
    """Verifica herramientas del sistema"""
    tools = {
        "convert": False,  # ImageMagick
        "dpkg-architecture": False,  # Para multiarch en Debian
        "gtk-update-icon-cache": False,
        "update-desktop-database": False,
    }
    
    for tool in tools:
        try:
            result = subprocess.run(
                ["which", tool],
                capture_output=True,
                timeout=2
            )
            tools[tool] = result.returncode == 0
        except Exception:
            tools[tool] = False
    
    return tools


def check_icons() -> dict:
    """Verifica archivos de icono"""
    icons_dir = Path(__file__).parent.parent / "app"
    return {
        "ico_exists": (icons_dir / "app-icon.ico").exists(),
        "png_exists": (icons_dir / "app-icon.png").exists(),
        "path": str(icons_dir),
    }


def suggest_optimizations() -> list:
    """Sugiere optimizaciones basadas en el sistema"""
    suggestions = []
    
    deps = check_dependencies()
    if not deps["PIL"]:
        suggestions.append("Instalar Pillow para mejor conversión de iconos: pip install Pillow")
    
    tools = check_system_tools()
    if not tools["convert"]:
        suggestions.append("Instalar ImageMagick para conversión de iconos: sudo apt-get install imagemagick")
    
    if not tools["gtk-update-icon-cache"]:
        suggestions.append("Instalar herramientas GTK: sudo apt-get install libgtk-3-0")
    
    return suggestions


def main():
    print("=" * 60)
    print("PackageMaker Linux - Sistema de Validación")
    print("=" * 60)
    
    print("\n[SISTEMA]")
    system_info = check_system()
    for key, value in system_info.items():
        print(f"  {key}: {value}")
    
    print("\n[DEPENDENCIAS]")
    deps = check_dependencies()
    for dep, installed in deps.items():
        status = "✓" if installed else "✗"
        print(f"  {status} {dep}")
    
    print("\n[HERRAMIENTAS DEL SISTEMA]")
    tools = check_system_tools()
    for tool, available in tools.items():
        status = "✓" if available else "✗"
        print(f"  {status} {tool}")
    
    print("\n[ICONOS]")
    icons = check_icons()
    for key, value in icons.items():
        print(f"  {key}: {value}")
    
    print("\n[SUGERENCIAS]")
    suggestions = suggest_optimizations()
    if suggestions:
        for i, sugg in enumerate(suggestions, 1):
            print(f"  {i}. {sugg}")
    else:
        print("  ✓ Sistema configurado correctamente")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
