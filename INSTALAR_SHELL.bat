@echo off
echo ========================================
echo INSTALADOR DE SHELL INTEGRATION - IPM
echo ========================================
echo.
echo Este script instalara la integracion con el shell de Windows.
echo Requiere permisos de administrador.
echo.
pause

:: Verificar si ya es administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Ya tienes permisos de administrador.
    goto :install
) else (
    echo Solicitando permisos de administrador...
    powershell -Command "Start-Process cmd -ArgumentList '/c cd /d %CD% && %~f0 admin' -Verb RunAs"
    exit /b
)

:install
echo.
echo [1/2] Instalando integracion...
python shell_integration.py --install
echo.

echo [2/2] Verificando instalacion...
echo.
echo Abre el Explorador de Windows y verifica que aparezcan
echo las opciones de IPM al hacer click derecho en una carpeta.
echo.
echo ========================================
echo INSTALACION COMPLETADA
echo ========================================
pause
