#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Muestra el comando que se registrará en el shell
"""

import sys
import os

# Agregar directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shell_integration import ShellIntegration

print("=" * 60)
print("COMANDO QUE SE REGISTRARÁ EN EL SHELL")
print("=" * 60)
print()

shell = ShellIntegration()

print("Información detectada:")
print(f"  Script shell: {shell.shellScript}")
print(f"  Icono: {shell.iconPath}")
print()

# Mostrar comando que se generará
comando_crear = shell._get_command('--create-project "%1"')
print("Comando para 'Crear Proyecto Aquí':")
print(f"  {comando_crear}")
print()

comando_mexf = shell._get_command('--create-mexf "%V"')
print("Comando para 'Crear Archivo MEXF':")
print(f"  {comando_mexf}")
print()

print("=" * 60)
print("PRUEBA MANUAL")
print("=" * 60)
print()
print("Para probar si el comando funciona, ejecuta:")
print()
print(f'  {comando_crear.replace("%1", "C:\\\\temp\\\\test")}')
print()
print("Esto debería abrir la ventana de crear proyecto.")
print()
