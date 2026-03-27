# Integración con Windows Shell - Influent Package Maker

## Descripción

Este módulo proporciona integración completa con el shell de Windows, permitiendo acceder a las funcionalidades de Influent Package Maker directamente desde el explorador de archivos mediante menús contextuales.

## Características

### Menús Contextuales

#### Para Carpetas
- **Crear Proyecto Aquí**: Crea un nuevo proyecto IPM en la carpeta seleccionada
- **Instalar como Fluthin Package**: Instala una carpeta como paquete Fluthin
- **Compilar Proyecto**: Compila el proyecto para Windows/Knosthalij
- **Reparar Proyecto (MoonFix)**: Analiza y repara el proyecto automáticamente

#### Para Archivos .iflapp
- **Instalar Paquete**: Instala un paquete Fluthin
- **Abrir con IPM**: Abre el paquete en el gestor de IPM

#### Para Archivos .mexf
- **Instalar Extensiones**: Instala las extensiones definidas en el archivo
- **Editar con IPM**: Abre el editor de archivos MEXF

#### En el Fondo de Carpetas
- **Nuevo Proyecto IPM**: Crea un nuevo proyecto en la ubicación actual
- **Crear Archivo de Extensiones (.mexf)**: Crea un nuevo archivo MEXF

### Archivos .mexf (Marked Extensions File)

Los archivos .mexf son archivos JSON que definen extensiones de archivo, menús contextuales y asociaciones para aplicaciones. Similar a los archivos .desktop de Linux pero más específicos para Windows.

#### Estructura de un archivo .mexf

```json
{
    "version": "1.0",
    "app_name": "Mi Aplicación",
    "app_id": "com.example.myapp",
    "extensions": [
        {
            "extension": ".myext",
            "description": "Mi Extensión",
            "icon": "path/to/icon.ico",
            "mime_type": "application/x-myext"
        }
    ],
    "context_menus": [
        {
            "target": "file",
            "extensions": [".myext"],
            "label": "Abrir con Mi App",
            "command": "myapp.exe \"%1\"",
            "icon": "path/to/icon.ico"
        }
    ],
    "file_associations": [
        {
            "extension": ".myext",
            "prog_id": "MyApp.Document",
            "description": "Documento de Mi App",
            "default_icon": "path/to/icon.ico",
            "open_command": "myapp.exe \"%1\""
        }
    ]
}
```

## Instalación

### Método 1: Script de Python

```bash
python install_integration.py
```

### Método 2: Archivo de Registro

1. Edita `install_shell_integration.reg` y ajusta las rutas según tu instalación
2. Haz doble clic en el archivo
3. Acepta el mensaje de confirmación

### Método 3: Desde la Aplicación

```bash
packagemaker.exe --install-shell
```

## Desinstalación

### Método 1: Script de Python

```bash
python uninstall_integration.py
```

### Método 2: Archivo de Registro

1. Haz doble clic en `uninstall_shell_integration.reg`
2. Acepta el mensaje de confirmación

### Método 3: Desde la Aplicación

```bash
packagemaker.exe --uninstall-shell
```

## Uso desde Línea de Comandos

### Crear un Proyecto

```bash
packagemaker.exe --create-project "C:\Ruta\Al\Proyecto"
```

### Instalar una Carpeta como Paquete

```bash
packagemaker.exe --install-folder "C:\Ruta\A\Carpeta"
```

### Compilar un Proyecto

```bash
packagemaker.exe --compile-project "C:\Ruta\Al\Proyecto"
```

### Reparar un Proyecto (MoonFix)

```bash
packagemaker.exe --repair-project "C:\Ruta\Al\Proyecto"
```

### Instalar un Paquete .iflapp

```bash
packagemaker.exe --install-package "archivo.iflapp"
```

### Instalar Extensiones desde .mexf

```bash
packagemaker.exe --install-mexf "archivo.mexf"
```

### Crear un Archivo .mexf

```bash
packagemaker.exe --create-mexf "C:\Ruta\Destino"
```

### Crear Accesos Directos

```bash
packagemaker.exe --create-shortcuts
```

## MoonFix - Sistema de Reparación Automática

MoonFix es un sistema inteligente que analiza proyectos en busca de:

- **Carpetas faltantes**: Crea las carpetas estándar (app, assets, config, docs, source, lib)
- **Archivos de configuración**: Verifica y crea details.xml si falta
- **Dependencias**: Verifica requirements.txt
- **Archivos principales**: Detecta archivos .py principales
- **Configuraciones antiguas**: Actualiza configuraciones obsoletas

### Uso de MoonFix

1. Haz clic derecho en una carpeta de proyecto
2. Selecciona "Reparar Proyecto (MoonFix)"
3. Revisa el análisis en la ventana de log
4. Haz clic en "Iniciar Reparación"

## Estructura de Carpetas de Proyecto

Un proyecto IPM típico tiene la siguiente estructura:

```
MiProyecto/
├── app/                    # Iconos y recursos de la aplicación
│   └── app-icon.ico
├── assets/                 # Recursos multimedia
│   ├── images/
│   └── sounds/
├── config/                 # Archivos de configuración
├── docs/                   # Documentación
│   └── index.html
├── source/                 # Código fuente adicional
├── lib/                    # Bibliotecas y dependencias
│   └── requirements.txt
├── details.xml             # Metadatos del proyecto
└── miproyecto.py          # Archivo principal
```

## Ubicación de Instalación

Los paquetes instalados se guardan en:

```
%USERPROFILE%\Documents\Fluthin Apps\
```

O en español:

```
%USERPROFILE%\Documentos\Fluthin Apps\
```

Cada paquete instalado mantiene su nombre original de carpeta.

## Claves del Registro

Las claves del registro se crean en:

- `HKEY_CLASSES_ROOT\.iflapp`
- `HKEY_CLASSES_ROOT\.mexf`
- `HKEY_CLASSES_ROOT\Directory\shell\IPM_*`
- `HKEY_CLASSES_ROOT\Directory\Background\shell\IPM_*`

## Requisitos

- Windows 7 o superior
- Python 3.7+ (para desarrollo)
- PyQt5
- leviathan-ui
- Permisos de administrador (para instalación de integración shell)

## Solución de Problemas

### Los menús contextuales no aparecen

1. Verifica que ejecutaste la instalación con permisos de administrador
2. Reinicia el explorador de Windows (taskkill /f /im explorer.exe && start explorer)
3. Verifica las rutas en el archivo .reg

### Error al instalar extensiones

1. Verifica que el archivo .mexf tenga formato JSON válido
2. Asegúrate de tener permisos de administrador
3. Revisa que las rutas en el archivo .mexf sean correctas

### MoonFix no detecta problemas

1. Verifica que la carpeta sea un proyecto válido
2. Asegúrate de tener permisos de escritura en la carpeta
3. Revisa el log de errores en la ventana de MoonFix

## Desarrollo

### Agregar Nuevos Menús Contextuales

Edita `shell_integration.py` y agrega nuevos métodos en la clase `ShellIntegration`:

```python
def _add_custom_context_menu(self):
    key_path = r"Directory\shell\IPM_CustomAction"
    with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path) as key:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Mi Acción Personalizada")
        winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, self.icon_path)
    
    cmd_path = key_path + r"\command"
    with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, cmd_path) as key:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'"{self.exe_path}" --custom-action "%1"')
```

### Agregar Nuevos Comandos CLI

Edita `cli_handler.py` y agrega nuevos argumentos:

```python
self.parser.add_argument(
    '--custom-action',
    metavar='PATH',
    help='Ejecuta una acción personalizada'
)
```

## Licencia

GNU GPL v3 - Ver LICENSE para más detalles

## Autor

Jesus Quijada

## Soporte

Para reportar problemas o sugerencias, visita el repositorio del proyecto.
