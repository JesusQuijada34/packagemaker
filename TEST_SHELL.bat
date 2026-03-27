@echo off
echo ========================================
echo TEST DE PACKAGEMAKER-SHELL.PY
echo ========================================
echo.

echo [1/3] Verificando archivo...
if not exist "packagemaker-shell.py" (
    echo ERROR: packagemaker-shell.py no encontrado
    pause
    exit /b 1
)
echo OK
echo.

echo [2/3] Probando crear proyecto...
echo Abriendo ventana de crear proyecto...
python packagemaker-shell.py --create-project "%CD%\test_project"
echo.

echo [3/3] Probando crear MEXF...
echo Abriendo ventana de crear MEXF...
python packagemaker-shell.py --create-mexf "%CD%"
echo.

echo ========================================
echo TEST COMPLETADO
echo ========================================
echo.
echo Si las ventanas se abrieron correctamente,
echo la integracion shell funcionara bien.
echo.
pause
