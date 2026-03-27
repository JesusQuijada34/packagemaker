@echo off
echo ========================================
echo LOG DE DEBUG - IPM SHELL
echo ========================================
echo.

set LOGFILE=%USERPROFILE%\ipm-shell-debug.log

if exist "%LOGFILE%" (
    echo Mostrando contenido del log:
    echo.
    type "%LOGFILE%"
    echo.
    echo ========================================
    echo.
    echo Para limpiar el log, presiona cualquier tecla...
    pause >nul
    del "%LOGFILE%"
    echo Log limpiado.
) else (
    echo No se encontro el archivo de log.
    echo.
    echo El log se creara en: %LOGFILE%
    echo.
    echo Prueba hacer click en una opcion del menu contextual
    echo y luego ejecuta este script de nuevo.
)

echo.
pause
