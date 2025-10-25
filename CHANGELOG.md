# CHANGELOG - Influent Package Maker

## v3.1.0 - Refactorización Mayor y Consolidación (2025-10-25)

### 🚀 Novedades y Mejoras
- **Consolidación "Todo en Uno":** Los scripts principales `packagemaker.py` y `bundlemaker.py` (GUI) y sus versiones de terminal (`-term.py`) han sido refactorizados y consolidados para incluir toda la lógica necesaria para la creación y construcción de paquetes, eliminando la dependencia de scripts de administración externos.
- **Lanzadores Multiplataforma:** Se añadieron `launcher.sh` (Linux) y `launcher.bat` (Windows) con un menú interactivo para seleccionar la herramienta a ejecutar (Packagemaker GUI/CLI o Bundlemaker GUI/CLI), mejorando la curva de aprendizaje y el acceso.
- **Compilados de Linux:** Se incluyeron ejecutables compilados con PyInstaller para Linux (en `dist/linux/`) para la ejecución sin necesidad de instalar Python.
- **Librerías Offline:** Se creó el directorio `offline_libs/` con librerías de Qt5 para facilitar la ejecución offline de los scripts en entornos sin conexión.

### 🗑️ Eliminaciones
- **Proyectos APK:** Se eliminó por completo el proyecto Android (carpeta `android/`, `packagemaker.apk` y `packagemaker_mobile.py`) para enfocarse en la versión de escritorio.
- **Asociador de Extensiones:** Se eliminó la lógica y los archivos del asociador de extensiones (`*-association.iflapp`, `*-setup.iflapp`, y directorios relacionados) para simplificar la base de código.

### 🐛 Corrección de Errores
- **Rutas de Dependencias (CLI):** Se corrigió la lógica de la ruta del archivo `lib/requirements.txt` en `packagemaker-term.py` y `bundlemaker-term.py` para que la detección e instalación de dependencias funcione correctamente.
- **Sintaxis:** Se corrigió un error de sintaxis en `bundlemaker-term.py` tras la refactorización inicial.
