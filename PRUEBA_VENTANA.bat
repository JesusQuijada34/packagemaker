@echo off
echo ========================================
echo PRUEBA DE VENTANAS IPM
echo ========================================
echo.
echo Si ves una ventana de IPM, la integracion funciona!
echo Cierra la ventana para continuar...
echo.
python packagemaker-shell.py --create-project "%TEMP%\test_ipm"
echo.
echo ========================================
echo Prueba completada!
echo ========================================
pause
