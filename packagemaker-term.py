# -*- coding: utf-8 -*-
# Packagemaker - Herramienta para crear paquetes .iflapp (Normales)
# Versión de Terminal "Todo en Uno"

import os
import time
import shutil
import hashlib
import zipfile
import xml.etree.ElementTree as ET
import subprocess
import sys
import socket

# 🎨 Colores ANSI
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
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
            print(f"{GREEN}ÉXITO:{RESET} Dependencias instaladas.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"{RED}ERROR:{RESET} Fallo al instalar dependencias: {e}")
            return False
    else:
        print(f"{YELLOW}ADVERTENCIA:{RESET} No se detectó conexión a Internet. Usando versiones fallback (si existen).")
        return True

# --- Configuración de Rutas ---

plataforma = sys.platform
if plataforma.startswith("win"):
    BASE_DIR = os.path.join(os.environ["USERPROFILE"], "My Documents", "Influent Packages")
else:
    BASE_DIR = os.path.expanduser("~/Documentos/Influent Packages")

# 📁 Carpetas predeterminadas
DEFAULT_FOLDERS = "app,assets,config,docs,source,lib"
PACKAGE_EXT = ".iflapp"

# 🧠 Clasificación por edad (simplificada para la CLI)
AGE_RATINGS = {
    "adult": "ADULTS ONLY",
    "kids": "FOR KIDS",
    "social": "PUBLIC CONTENT",
    "ai": "PUBLIC ALL",
    "default": "EVERYONE"
}

# --- Utilidades de Empaquetado ---

def getversion():
    return time.strftime("%y.%m-%H.%M")

def get_age_rating(nombre_logico, nombre_completo):
    search_string = (nombre_logico + nombre_completo).lower()
    for keyword, rate in AGE_RATINGS.items():
        if keyword in search_string:
            return rate
    return AGE_RATINGS["default"]

def create_details_xml(path, empresa, nombre_logico, nombre_completo, version):
    newversion = getversion()
    empresa = empresa.capitalize()
    full_name = f"{empresa}.{nombre_logico}.v{version}"
    hash_val = hashlib.sha256(full_name.encode()).hexdigest()
    rating = get_age_rating(nombre_logico, nombre_completo)

    root = ET.Element("app")
    ET.SubElement(root, "publisher").text = empresa
    ET.SubElement(root, "app").text = nombre_logico
    ET.SubElement(root, "name").text = nombre_completo
    ET.SubElement(root, "version").text = f"v{version}"
    ET.SubElement(root, "platform").text = sys.platform
    ET.SubElement(root, "danenone").text = newversion
    ET.SubElement(root, "correlationid").text = hash_val
    ET.SubElement(root, "rate").text = rating

    tree = ET.ElementTree(root)
    tree.write(os.path.join(path, "details.xml"), encoding="utf-8", xml_declaration=True)
    print(f"{GREEN}ÉXITO:{RESET} Archivo details.xml creado.")

def create_project_structure(nombre_logico, empresa, version, nombre_completo):
    full_path = os.path.join(BASE_DIR, nombre_logico)
    
    if os.path.exists(full_path):
        print(f"{YELLOW}ADVERTENCIA:{RESET} El proyecto ya existe. ¿Desea sobrescribirlo? (s/n)")
        if input().lower() != 's':
            return
        shutil.rmtree(full_path)

    try:
        print(f"{CYAN}INFO:{RESET} Creando estructura de carpetas en {full_path}...")
        os.makedirs(BASE_DIR, exist_ok=True)
        for folder in DEFAULT_FOLDERS.split(","):
            os.makedirs(os.path.join(full_path, folder.strip()), exist_ok=True)
            
        # Archivo principal .py
        main_script = os.path.join(full_path, f"{nombre_logico}.py")
        with open(main_script, "w") as f:
            f.write(f"# Script principal para el paquete {nombre_logico}\nprint('Ejecutando {nombre_logico}')")

        # Archivo requirements.txt
        os.makedirs(os.path.join(full_path, "lib"), exist_ok=True)
        with open(os.path.join(full_path, "lib", "requirements.txt"), "w") as f:
            f.write("PyQt5\n")

        create_details_xml(full_path, empresa, nombre_logico, nombre_completo, version)
        print(f"{GREEN}ÉXITO:{RESET} Estructura del proyecto creada.")
    except Exception as e:
        print(f"{RED}ERROR:{RESET} Fallo al crear el proyecto: {e}")

def build_package(project_name):
    project_path = os.path.join(BASE_DIR, project_name)
    if not os.path.exists(project_path):
        print(f"{RED}ERROR:{RESET} El proyecto '{project_name}' no existe en {BASE_DIR}")
        return

    try:
        # 1. Leer detalles del XML
        tree = ET.parse(os.path.join(project_path, "details.xml"))
        root = tree.getroot()
        app_name = root.find('app').text
        
        output_zip = os.path.join(BASE_DIR, f"{app_name}{PACKAGE_EXT}")
        
        print(f"{CYAN}INFO:{RESET} Construyendo paquete {output_zip}...")
        
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root_dir, _, files in os.walk(project_path):
                for file in files:
                    file_path = os.path.join(root_dir, file)
                    arcname = os.path.relpath(file_path, project_path)
                    zipf.write(file_path, arcname)
        
        print(f"{GREEN}ÉXITO:{RESET} Paquete construido en {output_zip}")

    except Exception as e:
        print(f"{RED}ERROR:{RESET} Fallo al construir el paquete: {e}")

# --- Interfaz de Terminal ---

def main_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"""{GREEN}═📦═ {CYAN}INFLUENT PACKAGE MAKER (CLI){GREEN} ═#══════════════════════════════
{MAGENTA} 1  {GREEN}Crear Nuevo Proyecto (.iflapp)
{MAGENTA} 2  {GREEN}Construir Paquete (.iflapp)
{MAGENTA} 3  {CYAN}Listar Proyectos
{MAGENTA} 0  {RED}Salir
{GREEN}════════════════════════════════════════════════════════════{RESET}""")
    
    choice = input(f"{YELLOW}Opción:{RESET} ")
    
    if choice == '1':
        print(f"{CYAN}--- CREAR NUEVO PROYECTO ---{RESET}")
        empresa = input("Empresa (Publisher): ")
        nombre_logico = input("Nombre Lógico (ej: MiApp): ")
        nombre_completo = input("Nombre Completo (Título): ")
        version = input("Versión: ")
        create_project_structure(nombre_logico, empresa, version, nombre_completo)
        input("Presione Enter para continuar...")
    elif choice == '2':
        print(f"{CYAN}--- CONSTRUIR PAQUETE ---{RESET}")
        project_name = input("Nombre Lógico del Proyecto a construir: ")
        build_package(project_name)
        input("Presione Enter para continuar...")
    elif choice == '3':
        print(f"{CYAN}--- LISTAR PROYECTOS ---{RESET}")
        if os.path.exists(BASE_DIR):
            projects = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
            if projects:
                print(f"{GREEN}Proyectos encontrados en {BASE_DIR}:{RESET}")
                for p in projects:
                    print(f"- {p}")
            else:
                print(f"{YELLOW}ADVERTENCIA:{RESET} No se encontraron proyectos.")
        else:
            print(f"{YELLOW}ADVERTENCIA:{RESET} El directorio base no existe.")
        input("Presione Enter para continuar...")
    elif choice == '0':
        print(f"{GREEN}Saliendo...{RESET}")
        sys.exit()
    else:
        print(f"{RED}ERROR:{RESET} Opción no válida.")
        time.sleep(1)
        
    main_menu()

if __name__ == '__main__':
    # Se añade la comprobación de dependencias al inicio
    # Se asume que el requirements.txt está en el directorio lib/ del proyecto principal
    # Si el usuario quiere que esté en el mismo directorio, habría que modificar esta ruta.
    requirements_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib", "requirements.txt")
    install_dependencies(requirements_path)
    main_menu()
