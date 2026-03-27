# Guía de Inicio Rápido - Integración Shell

## Instalación en 3 Pasos

### Paso 1: Instalar Integración
```bash
# Opción A: Usando script batch (recomendado)
INSTALL_SHELL.bat

# Opción B: Usando Python
python install_integration.py

# Opción C: Usando archivo de registro
# 1. Edita install_shell_integration.reg con tus rutas
# 2. Doble clic en el archivo
# 3. Acepta el mensaje
```

### Paso 2: Reiniciar Explorador (opcional)
```bash
taskkill /f /im explorer.exe
start explorer.exe
```

### Paso 3: ¡Listo!
Ahora puedes hacer clic derecho en carpetas y archivos para usar IPM.

## Uso Rápido

### Crear un Proyecto
1. Navega a una carpeta en el explorador
2. Clic derecho → "Crear Proyecto Aquí"
3. Completa los detalles
4. Clic en "Crear Proyecto"

### Compilar un Proyecto
1. Clic derecho en carpeta del proyecto
2. Selecciona "Compilar Proyecto"
3. Elige plataforma (Windows/Knosthalij)
4. Clic en "Compilar"

### Reparar un Proyecto (MoonFix)
1. Clic derecho en carpeta del proyecto
2. Selecciona "Reparar Proyecto (MoonFix)"
3. Clic en "Iniciar Reparación"
4. Revisa el log de reparaciones

### Instalar un Paquete
1. Clic derecho en archivo .iflapp
2. Selecciona "Instalar Paquete"
3. Clic en "Instalar"
4. Espera a que termine

## Comandos CLI Rápidos

```bash
# Crear proyecto
packagemaker.exe --create-project "C:\MiProyecto"

# Compilar proyecto
packagemaker.exe --compile-project "C:\MiProyecto"

# Reparar proyecto
packagemaker.exe --repair-project "C:\MiProyecto"

# Instalar paquete
packagemaker.exe --install-package "paquete.iflapp"

# Crear archivo MEXF
packagemaker.exe --create-mexf "C:\Destino"
```

## Solución Rápida de Problemas

### Los menús no aparecen
```bash
# Reiniciar explorador
taskkill /f /im explorer.exe && start explorer.exe
```

### Error de permisos
```bash
# Ejecutar como administrador
# Clic derecho en INSTALL_SHELL.bat → Ejecutar como administrador
```

### Desinstalar
```bash
# Opción A: Script batch
UNINSTALL_SHELL.bat

# Opción B: Python
python uninstall_integration.py

# Opción C: Archivo de registro
# Doble clic en uninstall_shell_integration.reg
```

## Archivos Importantes

- `shell_integration.py` - Módulo principal
- `cli_handler.py` - Manejador de comandos
- `example.mexf` - Ejemplo de archivo MEXF
- `SHELL_INTEGRATION.md` - Documentación completa
- `DEBUG_GUIDE.md` - Guía de debugging

## Soporte

¿Problemas? Revisa:
1. `DEBUG_GUIDE.md` - Guía de debugging
2. `SHELL_INTEGRATION.md` - Documentación completa
3. Logs en `%APPDATA%\InfluentPackageMaker\logs\`

## Siguiente Paso

Lee `SHELL_INTEGRATION.md` para documentación completa.
