# Guía de Debugging - Influent Package Maker

## Verificación de Instalación

### 1. Verificar Claves del Registro

Abre el Editor del Registro (regedit.exe) y verifica las siguientes claves:

```
HKEY_CLASSES_ROOT\.iflapp
HKEY_CLASSES_ROOT\InfluentPackage
HKEY_CLASSES_ROOT\.mexf
HKEY_CLASSES_ROOT\MarkedExtensionsFile
HKEY_CLASSES_ROOT\Directory\shell\IPM_CreateProject
HKEY_CLASSES_ROOT\Directory\shell\IPM_InstallFolder
HKEY_CLASSES_ROOT\Directory\shell\IPM_CompileProject
HKEY_CLASSES_ROOT\Directory\shell\IPM_RepairProject
HKEY_CLASSES_ROOT\Directory\Background\shell\IPM_CreateProjectHere
HKEY_CLASSES_ROOT\Directory\Background\shell\IPM_CreateMEXF
```

### 2. Verificar Rutas de Archivos

Asegúrate de que las siguientes rutas existan:

- `app/app-icon.ico` - Icono de la aplicación
- `packagemaker.exe` o `packagemaker.py` - Ejecutable principal
- `shell_integration.py` - Módulo de integración
- `cli_handler.py` - Manejador de CLI

### 3. Probar Comandos CLI

```bash
# Probar ayuda
packagemaker.exe --help

# Probar instalación de shell
packagemaker.exe --install-shell

# Probar creación de proyecto
packagemaker.exe --create-project "C:\Test"

# Probar instalación de MEXF
packagemaker.exe --install-mexf "example.mexf"
```

## Errores Comunes

### Error: "No se puede encontrar el módulo 'shell_integration'"

**Causa**: El archivo shell_integration.py no está en el mismo directorio que packagemaker.py

**Solución**:
1. Verifica que shell_integration.py esté en la carpeta correcta
2. Si usas PyInstaller, asegúrate de incluir el módulo en el .spec:
   ```python
   a = Analysis(
       ['packagemaker.py'],
       pathex=[],
       binaries=[],
       datas=[('shell_integration.py', '.')],
       ...
   )
   ```

### Error: "Acceso denegado al registro"

**Causa**: No tienes permisos de administrador

**Solución**:
1. Cierra la aplicación
2. Haz clic derecho en packagemaker.exe
3. Selecciona "Ejecutar como administrador"
4. Intenta la instalación nuevamente

### Error: "Los menús contextuales no aparecen"

**Causa**: El explorador de Windows no ha actualizado el caché

**Solución**:
1. Abre el Administrador de Tareas (Ctrl+Shift+Esc)
2. Busca "Explorador de Windows"
3. Haz clic derecho y selecciona "Reiniciar"

O desde CMD:
```bash
taskkill /f /im explorer.exe
start explorer.exe
```

### Error: "El icono no se muestra en los menús"

**Causa**: La ruta del icono es incorrecta o el archivo no existe

**Solución**:
1. Verifica que `app/app-icon.ico` exista
2. Usa rutas absolutas en el registro:
   ```
   "C:\\Program Files\\InfluentPackageMaker\\app\\app-icon.ico"
   ```
3. Asegúrate de que el archivo .ico sea válido

### Error: "El comando no se ejecuta al hacer clic"

**Causa**: La ruta del ejecutable es incorrecta

**Solución**:
1. Verifica la ruta en el registro
2. Asegúrate de usar comillas dobles:
   ```
   "C:\\Program Files\\InfluentPackageMaker\\packagemaker.exe" --create-project "%1"
   ```
3. Prueba el comando manualmente desde CMD

## Debugging de MoonFix

### Activar Logging Detallado

Modifica `shell_integration.py` para agregar más logs:

```python
import logging

logging.basicConfig(
    filename='moonfix_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def _repair_from_dialog(self, path, progress, log_text, btn_repair):
    logging.debug(f"Iniciando reparación de: {path}")
    # ... resto del código
```

### Verificar Permisos de Carpeta

```python
import os
import stat

def check_permissions(path):
    try:
        # Intentar crear un archivo de prueba
        test_file = os.path.join(path, '.test_write')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        return True
    except:
        return False
```

## Debugging de Instalación de Paquetes

### Verificar Estructura del .iflapp

Un archivo .iflapp es un ZIP con la siguiente estructura:

```
paquete.iflapp (ZIP)
├── app/
├── assets/
├── config/
├── docs/
├── source/
├── lib/
├── details.xml
└── main.py
```

### Probar Extracción Manual

```python
import zipfile

def test_extract(iflapp_path):
    try:
        with zipfile.ZipFile(iflapp_path, 'r') as zip_ref:
            zip_ref.extractall('test_extract')
        print("Extracción exitosa")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
```

## Debugging de Archivos .mexf

### Validar JSON

```python
import json

def validate_mexf(mexf_path):
    try:
        with open(mexf_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Verificar campos requeridos
        required = ['version', 'app_name', 'app_id']
        for field in required:
            if field not in data:
                print(f"Campo faltante: {field}")
                return False
        
        print("MEXF válido")
        return True
    except json.JSONDecodeError as e:
        print(f"Error de JSON: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False
```

## Herramientas de Debugging

### 1. Process Monitor (Sysinternals)

Descarga: https://docs.microsoft.com/en-us/sysinternals/downloads/procmon

Útil para:
- Ver accesos al registro en tiempo real
- Detectar errores de permisos
- Monitorear acceso a archivos

### 2. Registry Workshop

Útil para:
- Editar el registro de forma segura
- Exportar/importar claves
- Buscar claves relacionadas

### 3. Python Debugger

```python
import pdb

def problematic_function():
    pdb.set_trace()  # Punto de interrupción
    # ... código a debuggear
```

## Logs del Sistema

### Ubicación de Logs

- Windows Event Viewer: `eventvwr.msc`
- Logs de aplicación: `%APPDATA%\InfluentPackageMaker\logs\`
- Logs de instalación: `install_log.txt`

### Crear Sistema de Logs

```python
import logging
from datetime import datetime

def setup_logging():
    log_dir = os.path.join(os.getenv('APPDATA'), 'InfluentPackageMaker', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f'ipm_{datetime.now():%Y%m%d}.log')
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
```

## Testing Automatizado

### Test de Integración Shell

```python
import unittest
from shell_integration import ShellIntegration

class TestShellIntegration(unittest.TestCase):
    def setUp(self):
        self.shell = ShellIntegration()
    
    def test_install_context_menus(self):
        result = self.shell.install_context_menus()
        self.assertTrue(result)
    
    def test_uninstall_context_menus(self):
        result = self.shell.uninstall_context_menus()
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
```

### Test de CLI Handler

```python
import unittest
from cli_handler import CLIHandler

class TestCLIHandler(unittest.TestCase):
    def setUp(self):
        self.cli = CLIHandler()
    
    def test_parse_create_project(self):
        import sys
        sys.argv = ['packagemaker.py', '--create-project', 'C:\\Test']
        args = self.cli.parse()
        self.assertEqual(args.create_project, 'C:\\Test')

if __name__ == '__main__':
    unittest.main()
```

## Checklist de Debugging

- [ ] Verificar permisos de administrador
- [ ] Verificar rutas de archivos
- [ ] Verificar claves del registro
- [ ] Reiniciar explorador de Windows
- [ ] Verificar logs de error
- [ ] Probar comandos CLI manualmente
- [ ] Verificar formato de archivos .mexf
- [ ] Verificar estructura de archivos .iflapp
- [ ] Verificar iconos y recursos
- [ ] Probar en carpeta de prueba primero

## Contacto y Soporte

Si encuentras un error que no puedes resolver:

1. Revisa esta guía completamente
2. Verifica los logs del sistema
3. Crea un issue en el repositorio con:
   - Descripción del error
   - Pasos para reproducir
   - Logs relevantes
   - Versión de Windows
   - Versión de IPM

## Recursos Adicionales

- Documentación de Windows Registry: https://docs.microsoft.com/en-us/windows/win32/sysinfo/registry
- PyQt5 Documentation: https://www.riverbankcomputing.com/static/Docs/PyQt5/
- Python winreg module: https://docs.python.org/3/library/winreg.html
