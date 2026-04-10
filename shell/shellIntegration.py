#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Shell integration helpers for Influent Package Maker.
Todas las acciones del shell usan el launcher localizado en shell/packagemakerShell.py.
"""

import os
import sys
import winreg
import json
import ctypes
import subprocess

class ShellIntegration:
    """Maneja la integración con el shell de Windows."""

    def __init__(self):
        self.applicationName = "Influent Package Maker"
        self.applicationId = "InfluentPackageMaker"

        if getattr(sys, 'frozen', False):
            self.executablePath = sys.executable
            self.baseDir = os.path.dirname(sys.executable)
            self.shellScript = self.executablePath
        else:
            currentDir = os.path.dirname(os.path.abspath(__file__))
            shellScriptPath = os.path.join(currentDir, "packagemakerShell.py")
            if not os.path.exists(shellScriptPath):
                shellScriptPath = os.path.abspath(os.path.join(currentDir, "..", "shell", "packagemakerShell.py"))
            self.executablePath = shellScriptPath
            self.shellScript = shellScriptPath
            self.baseDir = os.path.dirname(shellScriptPath)

        self.iconPath = self._find_icon()

        print(f"[ShellIntegration] Ruta script shell: {self.shellScript}")
        print(f"[ShellIntegration] Ruta icono: {self.iconPath}")

    def _find_icon(self):
        possible_paths = [
            os.path.join(self.baseDir, "app", "app-icon.ico"),
            os.path.join(self.baseDir, "app-icon.ico"),
            os.path.join(self.baseDir, "..", "app", "app-icon.ico"),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return os.path.abspath(path)
        return "%SystemRoot%\\System32\\shell32.dll,3"

    def _get_command(self, args):
        if getattr(sys, 'frozen', False):
            return f'"{self.shellScript}" {args}'
        pythonExe = sys.executable
        if pythonExe.lower().endswith("python.exe"):
            pythonwExe = pythonExe[:-10] + "pythonw.exe"
            if os.path.exists(pythonwExe):
                pythonExe = pythonwExe
        return f'"{pythonExe}" "{self.shellScript}" {args}'

    def install_all(self):
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
        try:
            self._register_folder_menu("IPM_CreateProject", "🆕 Crear Proyecto Aquí", "--create-project \"%1\"")
            self._register_folder_menu("IPM_InstallFolder", "📦 Instalar como Fluthin Package", "--install-folder \"%1\"")
            self._register_folder_menu("IPM_CompileProject", "🔨 Compilar Proyecto", "--compile-project \"%1\"")
            self._register_folder_menu("IPM_RepairProject", "🌙 Reparar Proyecto (MoonFix)", "--repair-project \"%1\"")
            self._register_background_menu("IPM_CreateProjectHere", "🆕 Nuevo Proyecto IPM", "--create-project \"%V\"")
            self._register_iflapp_menus()
            return True
        except Exception as e:
            print(f"Error instalando menús contextuales: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _register_folder_menu(self, keyName, displayName, argument):
        try:
            keyPath = f"Directory\\shell\\{keyName}"
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, keyPath) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, displayName)
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, self.iconPath)
            commandPath = f"{keyPath}\\command"
            command = self._get_command(argument)
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, commandPath) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, command)
            print(f"  ✓ Registrado: {displayName}")
            print(f"    Comando: {command}")
        except Exception as e:
            print(f"  ✗ Error registrando {displayName}: {e}")

    def _register_background_menu(self, keyName, displayName, argument):
        try:
            keyPath = f"Directory\\Background\\shell\\{keyName}"
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, keyPath) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, displayName)
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, self.iconPath)
            commandPath = f"{keyPath}\\command"
            command = self._get_command(argument)
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, commandPath) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, command)
            print(f"  ✓ Registrado: {displayName}")
        except Exception as e:
            print(f"  ✗ Error registrando {displayName}: {e}")

    def _register_iflapp_menus(self):
        try:
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, ".iflapp") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "InfluentPackage")
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "InfluentPackage") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Fluthin Package")
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "InfluentPackage\\DefaultIcon") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, self.iconPath)
            keyPath = "InfluentPackage\\shell\\install"
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, keyPath) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "📥 Instalar Paquete")
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, self.iconPath)
            command = self._get_command('--install-package "%1"')
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{keyPath}\\command") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, command)
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
        try:
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, ".mexf") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "MarkedExtensionsFile")
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "MarkedExtensionsFile") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Archivo de Extensiones Marcadas")
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "MarkedExtensionsFile\\DefaultIcon") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, self.iconPath)
            keyPath = "MarkedExtensionsFile\\shell\\install"
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, keyPath) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "🔧 Instalar Extensiones")
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, self.iconPath)
            command = self._get_command('--install-mexf "%1"')
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{keyPath}\\command") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, command)
            keyPath = "MarkedExtensionsFile\\shell\\edit"
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, keyPath) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "✏️ Editar con IPM")
            command = self._get_command('--edit-mexf "%1"')
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{keyPath}\\command") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, command)
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

    def create_shortcuts(self):
        try:
            start_menu = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Influent')
            desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
            os.makedirs(start_menu, exist_ok=True)
            target = self.executablePath if getattr(sys, 'frozen', False) else os.path.abspath(os.path.join(self.baseDir, '..', 'packagemaker.py'))
            shortcut_name = "Package Maker"

            try:
                import pythoncom
                from win32com.shell import shell
                shell_obj = pythoncom.CoCreateInstance(shell.CLSID_ShellLink, None, pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
                shell_obj.SetPath(target)
                shell_obj.SetDescription("Influent Package Maker")
                persist_file = shell_obj.QueryInterface(pythoncom.IID_IPersistFile)
                shortcut_path = os.path.join(desktop, f"{shortcut_name}.lnk")
                persist_file.Save(shortcut_path, 0)
                shortcut_path = os.path.join(start_menu, f"{shortcut_name}.lnk")
                persist_file.Save(shortcut_path, 0)
            except Exception:
                powershell_cmd = (
                    "$s=(New-Object -COM WScript.Shell);"
                    f"$lnk=$s.CreateShortcut('{desktop.replace('\\','\\\\')}\\{shortcut_name}.lnk');"
                    f"$lnk.TargetPath='{target.replace('\\','\\\\')}';"
                    "$lnk.Save();"
                )
                subprocess.check_call(["powershell", "-NoProfile", "-Command", powershell_cmd], shell=False)
                powershell_cmd = (
                    "$s=(New-Object -COM WScript.Shell);"
                    f"$lnk=$s.CreateShortcut('{os.path.join(start_menu, f'{shortcut_name}.lnk').replace('\\','\\\\')}');"
                    f"$lnk.TargetPath='{target.replace('\\','\\\\')}';"
                    "$lnk.Save();"
                )
                subprocess.check_call(["powershell", "-NoProfile", "-Command", powershell_cmd], shell=False)

            print("  ✓ Atajos creados")
            return True
        except Exception as e:
            print(f"  ✗ Error creando atajos: {e}")
            return False

    def uninstall_all(self):
        try:
            print("[ShellIntegration] Desinstalando integración...")
            keys_to_remove = [
                "Directory\\shell\\IPM_CreateProject",
                "Directory\\shell\\IPM_InstallFolder",
                "Directory\\shell\\IPM_CompileProject",
                "Directory\\shell\\IPM_RepairProject",
                "Directory\\Background\\shell\\IPM_CreateProjectHere",
                "Directory\\Background\\shell\\IPM_CreateMEXF",
                ".iflapp",
                "InfluentPackage",
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
        try:
            key = winreg.OpenKey(root, path, 0, winreg.KEY_ALL_ACCESS)
            subkeys = []
            try:
                i = 0
                while True:
                    subkeys.append(winreg.EnumKey(key, i))
                    i += 1
            except OSError:
                pass
            for subkey in subkeys:
                self._delete_registry_key(root, f"{path}\\{subkey}")
            winreg.CloseKey(key)
            winreg.DeleteKey(root, path)
        except Exception:
            pass

    def notify_shell_change(self):
        try:
            SHCNE_ASSOCCHANGED = 0x08000000
            SHCNF_IDLIST = 0x0000
            ctypes.windll.shell32.SHChangeNotify(SHCNE_ASSOCCHANGED, SHCNF_IDLIST, None, None)
            print("  ✓ Sistema notificado de cambios")
            return True
        except Exception as e:
            print(f"  ✗ Error notificando cambios: {e}")
            return False


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--install":
            ShellIntegration().install_all()
        elif sys.argv[1] == "--uninstall":
            ShellIntegration().uninstall_all()
        elif sys.argv[1] == "--create-shortcuts":
            ShellIntegration().create_shortcuts()
        else:
            print("Uso: python shellIntegration.py --install|--uninstall|--create-shortcuts")
    else:
        print("Uso: python shellIntegration.py --install|--uninstall|--create-shortcuts")
