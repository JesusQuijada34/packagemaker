"""
Gestor de iconos para Linux - Convierte y coloca iconos correctamente
para que se muestren en ventanas y gestor de aplicaciones.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional


def convert_ico_to_png(ico_path: str, png_path: str, size: int = 64) -> bool:
    """Convierte ICO a PNG usando ImageMagick o pillow."""
    try:
        # Intentar con ImageMagick (convert command)
        if shutil.which("convert"):
            subprocess.run(
                ["convert", f"{ico_path}[0]", "-resize", f"{size}x{size}", png_path],
                check=True,
                capture_output=True,
                timeout=10
            )
            return os.path.exists(png_path)
    except Exception:
        pass

    try:
        # Intentar con Pillow
        from PIL import Image
        with Image.open(ico_path) as img:
            img.thumbnail((size, size), Image.Resampling.LANCZOS)
            img = img.convert("RGBA")
            img.save(png_path, "PNG")
        return os.path.exists(png_path)
    except Exception:
        pass

    # Si ambas fallan, simplemente copiar el .ico (fallback)
    try:
        shutil.copy(ico_path, png_path)
        return os.path.exists(png_path)
    except Exception:
        return False


def get_linux_icon_path(project_path: str, app_name: str) -> Optional[str]:
    """
    Obtiene la ruta del icono PNG para Linux.
    Convierte ICO a PNG si es necesario.
    """
    project_path = Path(project_path)
    app_dir = project_path / "app"
    
    # Buscar icono existente
    ico_path = app_dir / "app-icon.ico"
    png_path = app_dir / "app-icon.png"
    
    if not ico_path.exists():
        return None
    
    # Si ya existe PNG, devolverlo
    if png_path.exists():
        return str(png_path)
    
    # Convertir ICO a PNG
    if convert_ico_to_png(str(ico_path), str(png_path)):
        return str(png_path)
    
    # Fallback: devolver el ICO (aunque no sea ideal en Linux)
    return str(ico_path)


def install_icon_to_system(ico_path: str, app_name: str, size: int = 64) -> bool:
    """
    Instala el icono en ~/.local/share/icons/ (sin necesidad de sudo).
    Esto lo hace disponible en el gestor de aplicaciones.
    """
    try:
        # Crear directorio ~/.local/share/icons/hicolor/64x64/apps/
        icons_dir = Path.home() / ".local" / "share" / "icons" / "hicolor" / f"{size}x{size}" / "apps"
        icons_dir.mkdir(parents=True, exist_ok=True)
        
        # Convertir ICO a PNG si es necesario
        png_name = f"{app_name}.png"
        png_path = icons_dir / png_name
        
        if convert_ico_to_png(ico_path, str(png_path), size):
            # Actualizar base de datos de iconos
            try:
                if shutil.which("gtk-update-icon-cache"):
                    subprocess.run(
                        ["gtk-update-icon-cache", "-t", "-i", str(icons_dir.parent.parent)],
                        timeout=5
                    )
            except Exception:
                pass
            
            return True
    except Exception:
        pass
    
    return False


def create_desktop_file(project_path: str, app_name: str, display_name: str, executable_path: str) -> Optional[str]:
    """
    Crea un archivo .desktop para que la aplicación aparezca en el menú de aplicaciones.
    Retorna la ruta del archivo creado, o None si falla.
    """
    try:
        desktop_dir = Path.home() / ".local" / "share" / "applications"
        desktop_dir.mkdir(parents=True, exist_ok=True)
        
        desktop_file = desktop_dir / f"{app_name}.desktop"
        
        content = f"""[Desktop Entry]
Type=Application
Name={display_name}
Exec={executable_path}
Icon={app_name}
Categories=Development;Utility;
Comment=Application created with PackageMaker
Version=1.0
Terminal=false
"""
        
        desktop_file.write_text(content, encoding="utf-8")
        
        # Hacer ejecutable
        os.chmod(desktop_file, 0o644)
        
        # Actualizar base de datos de aplicaciones
        try:
            if shutil.which("update-desktop-database"):
                subprocess.run(
                    ["update-desktop-database", str(desktop_dir)],
                    timeout=5
                )
        except Exception:
            pass
        
        return str(desktop_file)
    except Exception:
        return None


def ensure_linux_icon_support(project_path: str, app_name: str = None) -> Optional[str]:
    """
    Asegura que los iconos se muestren correctamente en Linux:
    1. Convierte ICO a PNG si es necesario
    2. Instala el icono en ~/.local/share/icons/
    3. Crea archivo .desktop si es necesario
    
    Retorna la ruta del icono que puede usarse en PyQt6.
    """
    if app_name is None:
        app_name = Path(project_path).name.lower().replace(" ", "-")
    
    icon_path = get_linux_icon_path(project_path, app_name)
    
    if icon_path:
        install_icon_to_system(icon_path, app_name, 64)
        install_icon_to_system(icon_path, app_name, 128)
    
    return icon_path
