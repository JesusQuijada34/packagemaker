#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import argparse
from pathlib import Path

# Añadir el directorio raíz al path para importar lib
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from lib.BuildThread import FlangCompiler
from lib.projectNameFormatter import ProjectNameFormatter

def main():
    parser = argparse.ArgumentParser(description='PackageMaker Headless Builder')
    parser.add_argument('--project', type=str, default='.', help='Ruta del proyecto')
    parser.add_argument('--output', type=str, default='./dist', help='Carpeta de salida')
    parser.add_argument('--platform', type=str, choices=['Windows', 'Linux'], help='Plataforma objetivo')
    
    args = parser.parse_args()
    
    project_path = Path(args.project).resolve()
    output_path = Path(args.output).resolve()
    target_platform = args.platform or ("Windows" if os.name == 'nt' else "Linux")
    
    print(f"🚀 Iniciando compilación headless...")
    print(f"📂 Proyecto: {project_path}")
    print(f"📦 Salida: {output_path}")
    print(f"💻 Plataforma objetivo: {target_platform}")
    
    compiler = FlangCompiler(project_path, output_path, log_callback=print)
    
    if not compiler.parse_details_xml():
        print("❌ Error al parsear details.xml")
        sys.exit(1)
        
    if not compiler.find_scripts():
        print("❌ No se encontraron scripts para compilar")
        sys.exit(1)
        
    print("🔨 Compilando binarios...")
    if not compiler.compile_binaries(target_platform):
        print(f"❌ Error en la compilación: {compiler.last_error}")
        sys.exit(1)
        
    print("📦 Creando paquete...")
    if not compiler.create_package(target_platform):
        print("❌ Error al crear el paquete")
        sys.exit(1)
        
    # Usar ProjectNameFormatter para formato consistente
    publisher = compiler.metadata['publisher']
    app = compiler.metadata['app']
    version = compiler.metadata['version']
    platform_suffix = "Knosthalij" if target_platform == "Windows" else "Danenone"
    
    package_dir_name = ProjectNameFormatter.format_package_folder(publisher, app, version, platform_suffix)
    package_path = output_path / package_dir_name
    
    iflapp_file = output_path / ProjectNameFormatter.format_iflapp_filename(publisher, app, version, platform_suffix)
    
    print(f"🗜️ Comprimiendo a .iflapp: {iflapp_file}")
    if not compiler.compress_to_iflapp(package_path, iflapp_file):
        print("❌ Error al comprimir el paquete")
        sys.exit(1)
        
    print(f"✨ Proceso completado con éxito: {iflapp_file}")

if __name__ == "__main__":
    main()
