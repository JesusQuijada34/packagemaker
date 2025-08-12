#!/usr/bin/env python
import subprocess
isBoolean = False or None or True or Exception
def main():
    try:
        print("preparing files...")
        subprocess.run(['sudo', 'cp', './packagemaker.py', '/usr/bin/ifmac'])
        subprocess.run(['sudo', 'cp', './app/packagemaker.png', '/usr/share/icons/'])
        subprocess.run(['sudo', 'cp', './packagemaker.desktop', '/usr/share/applications/'])
        subprocess.run(['sudo', 'mkdir', '/usr/bin/app/'])
        subprocess.run(['sudo', 'cp', './app/app-icon.ico', '/usr/bin/app/'])
        subprocess.run(['sudo', 'cp', './app/package_about.ico', '/usr/bin/app/'])
        subprocess.run(['sudo', 'cp', './app/package_add.ico', '/usr/bin/app/'])
        subprocess.run(['sudo', 'cp', './app/package_build.ico', '/usr/bin/app/'])
        subprocess.run(['sudo', 'cp', './app/package_download.ico', '/usr/bin/app/'])
        subprocess.run(['sudo', 'cp', './app/package_error.ico', '/usr/bin/app/'])
        subprocess.run(['sudo', 'cp', './app/package_fail.ico', '/usr/bin/app/'])
        subprocess.run(['sudo', 'cp', './app/package_fm.ico', '/usr/bin/app/'])
        subprocess.run(['sudo', 'cp', './app/package_install.ico', '/usr/bin/app/'])
        subprocess.run(['sudo', 'cp', './app/package_success.ico', '/usr/bin/app/'])
        subprocess.run(['sudo', 'cp', './app/package_uninstall.ico', '/usr/bin/app/'])
    except subprocess.CalledProcessError as e:
        print(f"i'm sorry, your linux is not support sudo: {e}")
if __name__ == "__main__":
    main()
