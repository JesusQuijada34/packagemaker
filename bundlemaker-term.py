# -*- coding: utf-8 -*-
# Bundlemaker for Terminal - Herramienta CLI para crear paquetes .iflappb (Bundles)
# Inspirado en la estética y lógica de packagemaker-term.py

import os
import sys
import time
import json
import shutil
import hashlib
import zipfile
import xml.etree.ElementTree as ET
import subprocess
import socket

# --- Colores ANSI ---
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
RESET = "\033[0m"

# --- Utilidades de Dependencias ---

def check_internet_connection(host="8.8.8.8", port=53, timeout=3):
    """Verifica si hay conexión a Internet."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

def install_dependencies(requirements_file):
    """Instala dependencias si hay conexión a Internet. Si no, usa fallback."""
    if not os.path.exists(requirements_file):
        print(f"{YELLOW}INFO:{RESET} No se encontró archivo de dependencias.")
        return True

    if check_internet_connection():
        # Intenta instalar con pip
        try:
            print(f"{CYAN}INFO:{RESET} Conexión a Internet detectada. Instalando dependencias...")
            # Usamos el mismo requirements.txt para la versión de terminal
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
            print(f"{GREEN}ÉXITO:{RESET} Dependencias instaladas.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"{RED}ERROR:{RESET} Fallo al instalar dependencias: {e}")
            return False
    else:
        print(f"{YELLOW}ADVERTENCIA:{RESET} No se detectó conexión a Internet. Usando versiones fallback (si existen).")
        return True

# --- Configuración y Constantes ---
DEFAULT_PUBLISHER = "influent"
BUNDLE_FOLDERS = ["res", "data", "code", "manifest", "activity", "theme", "blob", "bundle"] # Añadida carpeta 'bundle'
BUNDLE_EXT = ".iflappb"

# Rutas base
if sys.platform.startswith("win"):
    BASE_DIR = os.path.join(os.environ["USERPROFILE"], "My Documents", "Influent Bundles")
else:
    BASE_DIR = os.path.expanduser("~/Documentos/Influent Bundles")

# --- Utilidades ---

def clearkmd():
    """Limpia la consola."""
    os.system('cls' if os.name == 'nt' else 'clear')

def getversion_stamp():
    """Genera la marca de tiempo para la versión."""
    return time.strftime("%y.%m-%H.%M")

def log_info(message):
    """Imprime un mensaje de información con color."""
    print(f"{CYAN}INFO:{RESET} {message}")

def log_success(message):
    """Imprime un mensaje de éxito con color."""
    print(f"{GREEN}ÉXITO:{RESET} {message}")

def log_error(message):
    """Imprime un mensaje de error con color."""
    print(f"{RED}ERROR:{RESET} {message}")

# --- Lógica de Generación de Archivos ---

def create_bundle_manifest_xml(bundle_path, bundle_name):
    """Crea el archivo bundleManifest.xml para la asociación de archivos y ejecutables."""
    root = ET.Element("bundleManifest")
    ET.SubElement(root, "comment").text = "Este archivo define los ejecutables dentro del Bundle para el Launcher."
    
    # Ejecutable principal de ejemplo
    main_exe = ET.SubElement(root, "executable")
    ET.SubElement(main_exe, "name").text = "Lanzador Principal"
    ET.SubElement(main_exe, "path").text = "code/main.py"
    ET.SubElement(main_exe, "icon").text = f"bundle/{bundle_name}.ico" # Icono específico
    ET.SubElement(main_exe, "command").text = "%PYTHON_EXE% %SCRIPT_PATH% %1"
    
    # Segundo ejecutable de ejemplo (ej. una herramienta de configuración)
    config_exe = ET.SubElement(root, "executable")
    ET.SubElement(config_exe, "name").text = "Herramienta de Configuración"
    ET.SubElement(config_exe, "path").text = "code/config_tool.py"
    ET.SubElement(config_exe, "icon").text = "bundle/config_tool.ico"
    ET.SubElement(config_exe, "command").text = "%PYTHON_EXE% %SCRIPT_PATH%"
    
    tree = ET.ElementTree(root)
    xml_path = os.path.join(bundle_path, "bundleManifest.xml")
    tree.write(xml_path, encoding="utf-8", xml_declaration=True)
    log_info(f"Creado bundleManifest.xml en: {xml_path}")

def create_bundle_details_xml(bundle_path, publisher, bundle_name, version):
    """Crea el archivo details.xml para el bundle (Metadatos)."""
    root = ET.Element("bundle")
    ET.SubElement(root, "publisher").text = publisher
    ET.SubElement(root, "name").text = bundle_name
    ET.SubElement(root, "version").text = version
    ET.SubElement(root, "dateCreated").text = time.strftime("%Y-%m-%d %H:%M:%S")
    tree = ET.ElementTree(root)
    details_path = os.path.join(bundle_path, "details.xml")
    tree.write(details_path, encoding="utf-8", xml_declaration=True)
    log_info(f"Creado details.xml en: {details_path}")

def create_bundle_manifest_json(bundle_path, bundle_name, version):
    """Crea el archivo manifest.json para el bundle (Estructura interna)."""
    manifest_data = {
        "bundleName": bundle_name,
        "publisher": DEFAULT_PUBLISHER,
        "version": version,
        "files": ["res/", "data/", "code/", "manifest/", "activity/", "theme/", "blob/", "bundle/"],
        "executables": ["code/main.py", "code/config_tool.py"]
    }
    json_path = os.path.join(bundle_path, "manifest", "manifest.json")
    with open(json_path, 'w') as f:
        json.dump(manifest_data, f, indent=4)
    log_info(f"Creado manifest.json en: {json_path}")

def create_bundle_structure(bundle_name, publisher, version):
    full_path = os.path.join(BASE_DIR, bundle_name)
    
    if os.path.exists(full_path):
        print(f"{YELLOW}ADVERTENCIA:{RESET} El Bundle ya existe. ¿Desea sobrescribirlo? (s/n)")
        if input().lower() != 's':
            return
        shutil.rmtree(full_path)

    try:
        log_info(f"Creando estructura de Bundle en {full_path}...")
        for folder in BUNDLE_FOLDERS:
            os.makedirs(os.path.join(full_path, folder), exist_ok=True)
            
        # Archivos de código de ejemplo
        with open(os.path.join(full_path, "code", "main.py"), "w") as f:
            f.write(f"# Script principal del Bundle {bundle_name}\nprint('Ejecutando Bundle: {bundle_name}')")
        with open(os.path.join(full_path, "code", "config_tool.py"), "w") as f:
            f.write(f"# Herramienta de configuración del Bundle {bundle_name}\nprint('Ejecutando Herramienta de Configuración')")

        # Archivos de manifiesto
        create_bundle_details_xml(full_path, publisher, bundle_name, version)
        create_bundle_manifest_json(full_path, bundle_name, version)
        create_bundle_manifest_xml(full_path, bundle_name)
        
        # Archivos de icono de ejemplo
        with open(os.path.join(full_path, "bundle", f"{bundle_name}.ico"), "w") as f:
            f.write("# Icono principal del Bundle (Placeholder)")
        with open(os.path.join(full_path, "bundle", "config_tool.ico"), "w") as f:
            f.write("# Icono de la herramienta de configuración (Placeholder)")

        log_success("Estructura del Bundle creada.")
    except Exception as e:
        log_error(f"Fallo al crear el Bundle: {e}")

def build_bundle(bundle_name):
    bundle_path = os.path.join(BASE_DIR, bundle_name)
    if not os.path.exists(bundle_path):
        log_error(f"El Bundle '{bundle_name}' no existe en {BASE_DIR}")
        return

    try:
        # 1. Leer detalles del XML
        tree = ET.parse(os.path.join(bundle_path, "details.xml"))
        root = tree.getroot()
        app_name = root.find('name').text
        
        output_zip = os.path.join(BASE_DIR, f"{app_name}{BUNDLE_EXT}")
        
        log_info(f"Construyendo Bundle {output_zip}...")
        
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root_dir, _, files in os.walk(bundle_path):
                for file in files:
                    file_path = os.path.join(root_dir, file)
                    arcname = os.path.relpath(file_path, bundle_path)
                    zipf.write(file_path, arcname)
        
        log_success(f"Bundle construido en {output_zip}")

    except Exception as e:
        log_error(f"Fallo al construir el Bundle: {e}")

# --- Interfaz de Terminal ---

def main_menu():
    clearkmd()
    print(f"""{CYAN}═📦═ {MAGENTA}INFLUENT BUNDLE MAKER (CLI){CYAN} ═#══════════════════════════════
{MAGENTA} 1  {GREEN}Crear Nuevo Bundle (.iflappb)
{MAGENTA} 2  {GREEN}Construir Bundle (.iflappb)
{MAGENTA} 3  {CYAN}Listar Bundles
{MAGENTA} 0  {RED}Salir
{CYAN}════════════════════════════════════════════════════════════{RESET}""")
    
    choice = input(f"{YELLOW}Opción:{RESET} ")
    
    if choice == '1':
        log_info("--- CREAR NUEVO BUNDLE ---")
        publisher = input("Empresa (Publisher): ")
        bundle_name = input("Nombre del Bundle (ej: MiBundle): ")
        version = input("Versión: ")
        create_bundle_structure(bundle_name, publisher, version)
        input("Presione Enter para continuar...")
    elif choice == '2':
        log_info("--- CONSTRUIR BUNDLE ---")
        bundle_name = input("Nombre del Bundle a construir: ")
        build_bundle(bundle_name)
        input("Presione Enter para continuar...")
    elif choice == '3':
        log_info("--- LISTAR BUNDLES ---")
        if os.path.exists(BASE_DIR):
            bundles = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
            if bundles:
                log_success(f"Bundles encontrados en {BASE_DIR}:")
                for b in bundles:
                    print(f"- {b}")
            else:
                log_info("No se encontraron Bundles.")
        else:
            log_info("El directorio base no existe.")
        input("Presione Enter para continuar...")
    elif choice == '0':
        log_info("Saliendo...")
        sys.exit()
    else:
        log_error("Opción no válida.")
        time.sleep(1)
        
    main_menu()

if __name__ == '__main__':
    # Se añade la comprobación de dependencias al inicio
    # El requirements.txt debe contener las dependencias necesarias para la CLI y la GUI
    install_dependencies(os.path.join(os.path.dirname(__file__), "lib", "requirements.txt"))
    main_menu()
