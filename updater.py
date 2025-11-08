#!/usr/bin/env python3
# updater.py - Proceso huérfano embestido que lanza interfaz animada
# Autor: Jesús Quijada Hernández David

import os
import sys
import subprocess
import time
import platform

SOURCE_FRAME = "source-frame.exe" if platform.system() == "Windows" else "./source-frame"

def launch_source_frame(title="Influent Packagemaker", message="Interfaz embestida activa", duration=10):
    cmd = [
        SOURCE_FRAME,
        f"--title={title}",
        f"--message={message}",
        f"--duration={duration}"
    ]
    try:
        subprocess.Popen(cmd)
    except Exception as e:
        print("Error al lanzar source-frame:", e)

def main():
    # Espera inicial para asegurar que el sistema esté listo
    time.sleep(2)

    # Lógica de verificación embestida (puedes expandirla con lectura de details.xml si lo deseas)
    print("✅ Updater embestido activo en segundo plano")

    # Lanzar interfaz visual
    launch_source_frame()

    # Mantener proceso vivo 24/7
    while True:
        time.sleep(60)  # Ciclo silencioso cada minuto

if __name__ == "__main__":
    main()
