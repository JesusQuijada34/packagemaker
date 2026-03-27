@echo off
echo ========================================
echo TEST DE INTEGRACION SHELL - IPM
echo ========================================
echo.

echo [1/4] Verificando Python...
python --version
if errorlevel 1 (
    echo ERROR: Python no encontrado
    pause
    exit /b 1
)
echo OK
echo.

echo [2/4] Verificando archivos...
if not exist "packagemaker.py" (
    echo ERROR: packagemaker.py no encontrado
    pause
    exit /b 1
)
if not exist "shell_integration.py" (
    echo ERROR: shell_integration.py no encontrado
    pause
    exit /b 1
)
echo OK
echo.

echo [3/4] Probando shell_integration.py...
python shell_integration.py
echo.

echo [4/4] Instalando integracion...
echo NOTA: Esto requiere permisos de administrador
echo.
python shell_integration.py --install
echo.

echo ========================================
echo TEST COMPLETADO
echo ========================================
echo.
echo Ahora prueba en el Explorador de Windows:
echo 1. Abre una carpeta
echo 2. Click derecho
echo 3. Deberias ver opciones de IPM
echo.
pause
