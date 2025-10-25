@echo off
REM launcher.bat - Lanzador de Influent Package Maker (Windows)
REM Permite al usuario elegir entre Packagemaker y Bundlemaker.

:MENU
cls
echo ======================================================
echo   INFLUENT PACKAGE MAKER - SELECCIÓN DE HERRAMIENTA
echo ======================================================
echo  [1] Packagemaker GUI (.iflapp)
echo  [2] Bundlemaker GUI (.iflappb)
echo  [3] Packagemaker Terminal (CLI)
echo  [4] Bundlemaker Terminal (CLI)
echo  [0] Salir
echo ======================================================

set /p choice="Seleccione una opción: "

if "%choice%"=="1" goto RUN_PM_GUI
if "%choice%"=="2" goto RUN_BM_GUI
if "%choice%"=="3" goto RUN_PM_TERM
if "%choice%"=="4" goto RUN_BM_TERM
if "%choice%"=="0" goto EXIT
goto INVALID_CHOICE

:RUN_PM_GUI
echo Iniciando packagemaker.py...
python packagemaker.py
pause
goto MENU

:RUN_BM_GUI
echo Iniciando bundlemaker.py...
python bundlemaker.py
pause
goto MENU

:RUN_PM_TERM
echo Iniciando packagemaker-term.py...
python packagemaker-term.py
pause
goto MENU

:RUN_BM_TERM
echo Iniciando bundlemaker-term.py...
python bundlemaker-term.py
pause
goto MENU

:INVALID_CHOICE
echo Opción no válida. Presione cualquier tecla para intentar de nuevo.
pause >nul
goto MENU

:EXIT
echo Saliendo del lanzador.
exit
