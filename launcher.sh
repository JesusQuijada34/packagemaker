#!/bin/bash

# Launcher.sh - Lanzador de Influent Package Maker (Linux)
# Permite al usuario elegir entre Packagemaker y Bundlemaker.

# --- Variables ---
PACKAGEMAKER_GUI="packagemaker.py"
BUNDLEMAKER_GUI="bundlemaker.py"
PACKAGEMAKER_TERM="packagemaker-term.py"
BUNDLEMAKER_TERM="bundlemaker-term.py"

# --- Funciones ---

function clear_screen() {
    clear
}

function show_menu() {
    clear_screen
    echo "======================================================"
    echo "  INFLUENT PACKAGE MAKER - SELECCIÓN DE HERRAMIENTA"
    echo "======================================================"
    echo " [1] Packagemaker GUI (.iflapp)"
    echo " [2] Bundlemaker GUI (.iflappb)"
    echo " [3] Packagemaker Terminal (CLI)"
    echo " [4] Bundlemaker Terminal (CLI)"
    echo " [0] Salir"
    echo "======================================================"
}

function run_tool() {
    local tool_script=$1
    echo "Iniciando $tool_script..."
    # Ejecutar el script con el intérprete de Python
    python3 "$tool_script"
    echo "El proceso de $tool_script ha finalizado. Presione Enter para volver al menú."
    read -r
}

# --- Bucle Principal ---

while true; do
    show_menu
    read -r -p "Seleccione una opción: " choice

    case "$choice" in
        1)
            run_tool "$PACKAGEMAKER_GUI"
            ;;
        2)
            run_tool "$BUNDLEMAKER_GUI"
            ;;
        3)
            run_tool "$PACKAGEMAKER_TERM"
            ;;
        4)
            run_tool "$BUNDLEMAKER_TERM"
            ;;
        0)
            echo "Saliendo del lanzador."
            exit 0
            ;;
        *)
            echo "Opción no válida. Intente de nuevo."
            sleep 1
            ;;
    esac
done
