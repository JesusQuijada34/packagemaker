#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Launcher de shell para Influent Package Maker.
Este script invoca packagemaker.py con parámetros compactos para modo shell.
"""

import os
import sys
import argparse
import subprocess

SHELL_ACTIONS_COMPACT = {
    'create_project',
    'install_folder',
    'compile_project',
    'repair_project',
    'create_mexf',
}

ARG_TO_FLAG = {
    'create_project': '--create-project',
    'install_folder': '--install-folder',
    'compile_project': '--compile-project',
    'repair_project': '--repair-project',
    'install_package': '--install-package',
    'open_package': '--open-package',
    'install_mexf': '--install-mexf',
    'edit_mexf': '--edit-mexf',
    'create_mexf': '--create-mexf',
}


def find_packagemaker_entry():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(current_dir, '..'))
    packagemaker_py = os.path.join(root_dir, 'packagemaker.py')
    if os.path.exists(packagemaker_py):
        return packagemaker_py
    raise FileNotFoundError('No se encontró packagemaker.py en la ruta esperada.')


def resolve_python_executable():
    if getattr(sys, 'frozen', False):
        return sys.executable
    python_exe = sys.executable
    if python_exe.lower().endswith('python.exe'):
        pythonw_exe = python_exe[:-10] + 'pythonw.exe'
        if os.path.exists(pythonw_exe):
            return pythonw_exe
    return python_exe


def build_packagemaker_command(args):
    target = find_packagemaker_entry()
    if getattr(sys, 'frozen', False):
        command = [sys.executable, target]
    else:
        command = [resolve_python_executable(), target]
    command.extend(args)
    return command


def main():
    parser = argparse.ArgumentParser(description='Shell launcher para Influent Package Maker')
    parser.add_argument('--create-project', metavar='PATH', help='Crear un nuevo proyecto en la ruta especificada')
    parser.add_argument('--install-folder', metavar='PATH', help='Instalar una carpeta como paquete')
    parser.add_argument('--compile-project', metavar='PATH', help='Compilar un proyecto existente')
    parser.add_argument('--repair-project', metavar='PATH', help='Reparar un proyecto con MoonFix')
    parser.add_argument('--install-package', metavar='PATH', help='Instalar un archivo .iflapp')
    parser.add_argument('--open-package', metavar='PATH', help='Abrir un paquete con IPM')
    parser.add_argument('--install-mexf', metavar='PATH', help='Instalar un archivo .mexf')
    parser.add_argument('--edit-mexf', metavar='PATH', help='Editar un archivo .mexf')
    parser.add_argument('--create-mexf', metavar='PATH', help='Crear un archivo .mexf')
    args = parser.parse_args()

    shell_args = []
    provided = False
    for key, flag in ARG_TO_FLAG.items():
        value = getattr(args, key)
        if value:
            shell_args.extend([flag, value])
            provided = True
            if key in SHELL_ACTIONS_COMPACT:
                shell_args.append('--compact')
            shell_args.append('--shell-mode')
            break

    if not provided:
        parser.print_help()
        return 1

    command = build_packagemaker_command(shell_args)
    try:
        subprocess.Popen(command, shell=False, close_fds=True)
        return 0
    except Exception as e:
        print(f"Error iniciando packagemaker: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
