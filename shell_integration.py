#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Shell Integration Module for Influent Package Maker
Handles Windows Shell Extensions, Context Menus, and Registry Operations
"""

import os
import sys
import winreg
import json
import ctypes
from pathlib import Path

class ShellIntegration:
    """Maneja la integración completa con el shell de Windows"""
    
    def __init__(self):
        self.applicationName = "Influent Package Maker"
        self.applicationId = "InfluentPackageMaker"
        
        # Detectar la ruta correcta del ejecutable/script
        if getattr(sys, 'frozen', False):
            # Ejecutable compilado
            self.executablePath = sys.executable
            self.baseDir = os.path.dirname(sys.executable)
            self.shellScript = self.executablePath  # Usar el mismo ejecutable
        else:
            # Script Python - buscar packagemaker-shell.py
            currentDir = os.path.dirname(os.path.abspath(__file__))
            shellScriptPath = os.path.join(currentDir, "packagemaker-shell.py")
            
            if not os.path.exists(shellScriptPath):
                # Buscar en directorio padre
                shellScriptPath = os.path.abspath(os.path.join(currentDir, "..", "packagemaker-shell.py"))
            
            self.executablePath = shellScriptPath
            self.shellScript = shellScriptPath
            self.baseDir = os.path.dirname(shellScriptPath)
        
        # Buscar icono
        self.iconPath = self._find_icon()
        
        print(f"[ShellIntegration] Ruta script shell: {self.shellScript}")
        print(f"[ShellIntegration] Ruta icono: {self.iconPath}")
    
    def _find_icon(self):
        """Busca el icono de la aplicación"""
        possible_paths = [
            os.path.join(self.baseDir, "app", "app-icon.ico"),
            os.path.join(self.baseDir, "app-icon.ico"),
            os.path.join(self.baseDir, "..", "app", "app-icon.ico"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return os.path.abspath(path)
        
        # Usar icono del sistema como fallback
        return "%SystemRoot%\\System32\\shell32.dll,3"
    
    def _get_command(self, args):
        """Genera el comando correcto para ejecutar IPM Shell"""
        if getattr(sys, 'frozen', False):
            # Ejecutable compilado
            return f'"{self.shellScript}" {args}'
        else:
            # Script Python - usar pythonw.exe para no mostrar consola
            pythonExe = sys.executable.replace("python.exe", "pythonw.exe")
            if not os.path.exists(pythonExe):
                pythonExe = sys.executable
            return f'"{pythonExe}" "{self.shellScript}" {args}'
    
    def install_all(self):
        """Instala toda la integración con el shell"""
        try:
            print("[ShellIntegration] Instalando menús contextuales...")
            self.install_context_menus()
            
            print("[ShellIntegration] Instalando soporte MEXF...")
            self.install_mexf_support()
            
            print("[ShellIntegration] Notificando cambios al sistema...")
            self.notify_shell_change()
            
            print("[ShellIntegration] ✓ Integración completada")
            return True
        except Exception as e:
            print(f"[ShellIntegration] ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def install_context_menus(self):
        """Instala todos los menús contextuales"""
        try:
            # Menús para carpetas
            self._register_folder_menu("IPM_CreateProject", "🆕 Crear Proyecto Aquí", "--create-project")
            self._register_folder_menu("IPM_InstallFolder", "📦 Instalar como Fluthin Package", "--install-folder")
            self._register_folder_menu("IPM_CompileProject", "🔨 Compilar Proyecto", "--compile-project")
            self._register_folder_menu("IPM_RepairProject", "🌙 Reparar Proyecto (MoonFix)", "--repair-project")
            
            # Menú para fondo de carpeta
            self._register_background_menu("IPM_CreateProjectHere", "🆕 Nuevo Proyecto IPM", "--create-project")
            
            # Menús para archivos .iflapp
            self._register_iflapp_menus()
            
            return True
        except Exception as e:
            print(f"Error instalando menús contextuales: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _register_folder_menu(self, keyName, displayName, argument):
        """Registra un menú contextual para carpetas"""
        try:
            keyPath = f"Directory\\shell\\{keyName}"
            
            # Crear clave principal
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, keyPath) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, displayName)
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, self.iconPath)
            
            # Crear comando
            commandPath = f"{keyPath}\\command"
            command = self._get_command(f'{argument} "%1"')
            
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, commandPath) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, command)
            
            print(f"  ✓ Registrado: {displayName}")
            print(f"    Comando: {command}")
        except Exception as e:
            print(f"  ✗ Error registrando {displayName}: {e}")
    
    def _register_background_menu(self, keyName, displayName, argument):
        """Registra un menú contextual para el fondo de carpetas"""
        try:
            keyPath = f"Directory\\Background\\shell\\{keyName}"
            
            # Crear clave principal
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, keyPath) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, displayName)
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, self.iconPath)
            
            # Crear comando (usar %V para directorio actual)
            commandPath = f"{keyPath}\\command"
            command = self._get_command(f'{argument} "%V"')
            
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, commandPath) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, command)
            
            print(f"  ✓ Registrado: {displayName}")
        except Exception as e:
            print(f"  ✗ Error registrando {displayName}: {e}")
    
    def _register_iflapp_menus(self):
        """Registra menús para archivos .iflapp"""
        try:
            # Registrar extensión
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, ".iflapp") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "InfluentPackage")
            
            # Configurar tipo de archivo
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "InfluentPackage") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Fluthin Package")
            
            # Icono por defecto
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "InfluentPackage\\DefaultIcon") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, self.iconPath)
            
            # Menú: Instalar Paquete
            keyPath = "InfluentPackage\\shell\\install"
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, keyPath) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "📥 Instalar Paquete")
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, self.iconPath)
            
            command = self._get_command('--install-package "%1"')
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{keyPath}\\command") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, command)
            
            # Menú: Abrir con IPM (por defecto)
            keyPath = "InfluentPackage\\shell\\open"
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, keyPath) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "📄 Abrir con IPM")
            
            command = self._get_command('--open-package "%1"')
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{keyPath}\\command") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, command)
            
            print("  ✓ Registrados menús para .iflapp")
        except Exception as e:
            print(f"  ✗ Error registrando .iflapp: {e}")
    
    def install_mexf_support(self):
        """Instala soporte para archivos .mexf"""
        try:
            # Registrar extensión
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, ".mexf") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "MarkedExtensionsFile")
            
            # Configurar tipo de archivo
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "MarkedExtensionsFile") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Archivo de Extensiones Marcadas")
            
            # Icono por defecto
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "MarkedExtensionsFile\\DefaultIcon") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, self.iconPath)
            
            # Menú: Instalar Extensiones
            keyPath = "MarkedExtensionsFile\\shell\\install"
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, keyPath) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "🔧 Instalar Extensiones")
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, self.iconPath)
            
            command = self._get_command('--install-mexf "%1"')
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{keyPath}\\command") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, command)
            
            # Menú: Editar con IPM
            keyPath = "MarkedExtensionsFile\\shell\\edit"
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, keyPath) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "✏️ Editar con IPM")
            
            command = self._get_command('--edit-mexf "%1"')
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{keyPath}\\command") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, command)
            
            # Menú en fondo: Crear MEXF
            keyPath = "Directory\\Background\\shell\\IPM_CreateMEXF"
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, keyPath) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "📝 Crear Archivo MEXF")
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, self.iconPath)
            
            command = self._get_command('--create-mexf "%V"')
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{keyPath}\\command") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, command)
            
            print("  ✓ Registrado soporte MEXF")
            return True
        except Exception as e:
            print(f"  ✗ Error instalando MEXF: {e}")
            return False
    
    def uninstall_all(self):
        """Desinstala toda la integración"""
        try:
            print("[ShellIntegration] Desinstalando integración...")
            
            keys_to_remove = [
                # Menús de carpetas
                "Directory\\shell\\IPM_CreateProject",
                "Directory\\shell\\IPM_InstallFolder",
                "Directory\\shell\\IPM_CompileProject",
                "Directory\\shell\\IPM_RepairProject",
                # Menús de fondo
                "Directory\\Background\\shell\\IPM_CreateProjectHere",
                "Directory\\Background\\shell\\IPM_CreateMEXF",
                # Archivos .iflapp
                ".iflapp",
                "InfluentPackage",
                # Archivos .mexf
                ".mexf",
                "MarkedExtensionsFile"
            ]
            
            for keyPath in keys_to_remove:
                try:
                    self._delete_registry_key(winreg.HKEY_CLASSES_ROOT, keyPath)
                    print(f"  ✓ Eliminado: {keyPath}")
                except:
                    pass
            
            self.notify_shell_change()
            print("[ShellIntegration] ✓ Desinstalación completada")
            return True
        except Exception as e:
            print(f"[ShellIntegration] ✗ Error: {e}")
            return False
    
    def _delete_registry_key(self, root, path):
        """Elimina una clave del registro recursivamente"""
        try:
            key = winreg.OpenKey(root, path, 0, winreg.KEY_ALL_ACCESS)
            subkeys = []
            try:
                i = 0
                while True:
                    subkeys.append(winreg.EnumKey(key, i))
                    i += 1
            except WindowsError:
                pass
            
            for subkey in subkeys:
                self._delete_registry_key(root, f"{path}\\{subkey}")
            
            winreg.CloseKey(key)
            winreg.DeleteKey(root, path)
        except:
            pass
    
    def notify_shell_change(self):
        """Notifica al shell de Windows sobre cambios"""
        try:
            # Notificar cambios en asociaciones de archivo
            SHCNE_ASSOCCHANGED = 0x08000000
            SHCNF_IDLIST = 0x0000
            ctypes.windll.shell32.SHChangeNotify(SHCNE_ASSOCCHANGED, SHCNF_IDLIST, None, None)
            print("  ✓ Sistema notificado de cambios")
            return True
        except Exception as e:
            print(f"  ✗ Error notificando cambios: {e}")
            return False


# Función de prueba
if __name__ == "__main__":
    print("=== Test de Shell Integration ===\n")
    shell = ShellIntegration()
    
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--install":
            shell.install_all()
        elif sys.argv[1] == "--uninstall":
            shell.uninstall_all()
    else:
        print("Uso:")
        print("  python shell_integration.py --install")
        print("  python shell_integration.py --uninstall")
