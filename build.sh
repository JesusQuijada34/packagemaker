#!/bin/bash

# Este script simula el proceso de construcción usando PyInstaller
# y aplica las reglas de nombrado y ubicación solicitadas por el usuario.

# 1. Instalar PyInstaller si no está presente (asumiendo un entorno de construcción)
# pip install pyinstaller

# 2. Limpiar el directorio de distribución anterior
rm -rf dist/*

# 3. Construir packagemaker (GUI)
# --onefile: crea un solo ejecutable
# --name: nombre del ejecutable
# --distpath: directorio de salida (la raíz de dist/)
# --hidden-import: para asegurar que se incluyan módulos necesarios (ej. PyQt5)
pyinstaller --onefile \
            --name packagemaker \
            --distpath dist \
            --hidden-import PyQt5.QtSvg \
            --hidden-import PyQt5.QtNetwork \
            packagemaker.py

# 4. Construir bundlemaker (GUI)
pyinstaller --onefile \
            --name bundlemaker \
            --distpath dist \
            --hidden-import PyQt5.QtSvg \
            --hidden-import PyQt5.QtNetwork \
            bundlemaker.py

# 5. Construir packagemaker (Terminal)
pyinstaller --onefile \
            --name packagemaker-term \
            --distpath dist \
            packagemaker-term.py

# 6. Construir bundlemaker (Terminal)
pyinstaller --onefile \
            --name bundlemaker-term \
            --distpath dist \
            bundlemaker-term.py

echo "Construcción simulada completada. Los ejecutables 'packagemaker', 'bundlemaker', 'packagemaker-term' y 'bundlemaker-term' se encontrarían ahora en el directorio 'dist/'."
