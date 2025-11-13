# Historial de Cambios (CHANGELOG)

Este documento registra todos los cambios notables realizados en el proyecto **Packagemaker** (anteriormente conocido como Influent Package Maker).

## [3.2.0] - 2025-11-09 - Actualizador Modernizado

### Añadido
- **Interfaz Gráfica para el Actualizador:** Implementación de una interfaz de usuario moderna y atractiva para el actualizador (`updater.py`) utilizando **PyQt5**, inspirada en el estilo de GitHub.
- **Selección de Tipo de Descarga:** La nueva interfaz permite al usuario elegir entre descargar el **Código Fuente** o el **Binario** específico para su sistema operativo (Windows/Linux).

### Cambiado
- **Reescritura Completa de `updater.py`:** El script de actualización ha sido reescrito desde cero para una experiencia de usuario más eficiente y moderna.
- **Verificación de Actualización Silenciosa:** El actualizador ahora verifica la disponibilidad de una nueva versión en segundo plano y **solo muestra la interfaz si se encuentra una actualización**, mejorando la experiencia de usuario.
- **Lógica de Reinicio y Verificación:** Se implementó la lógica para simular el reinicio del actualizador y la posterior verificación de actualizaciones del sistema tras una actualización exitosa.

---

## [3.1.0] - 2025-10-25 - Refactorización Mayor y Consolidación

### Añadido
- **Consolidación "Todo en Uno":** Los scripts principales (`packagemaker.py`, `bundlemaker.py` y sus versiones de terminal) han sido refactorizados para incluir toda la lógica de creación y construcción de paquetes, eliminando la dependencia de scripts de administración externos.
- **Lanzadores Multiplataforma:** Se añadieron `launcher.sh` (Linux) y `launcher.bat` (Windows) con un menú interactivo para seleccionar la herramienta a ejecutar (Packagemaker GUI/CLI o Bundlemaker GUI/CLI).
- **Compilados de Linux:** Se incluyeron ejecutables compilados con PyInstaller para Linux (en `dist/linux/`) para la ejecución sin necesidad de instalar Python.
- **Librerías Offline:** Se creó el directorio `offline_libs/` con librerías de Qt5 para facilitar la ejecución offline de los scripts en entornos sin conexión.

### Eliminado
- **Proyectos APK:** Se eliminó por completo el proyecto Android (carpeta `android/`, `packagemaker.apk` y `packagemaker_mobile.py`) para enfocar el desarrollo en la versión de escritorio.
- **Asociador de Extensiones:** Se eliminó la lógica y los archivos del asociador de extensiones (`*-association.iflapp`, `*-setup.iflapp`, y directorios relacionados) para simplificar la base de código.

### Corregido
- **Rutas de Dependencias (CLI):** Se corrigió la lógica de la ruta del archivo `lib/requirements.txt` en los scripts de terminal para que la detección e instalación de dependencias funcione correctamente.
- **Sintaxis:** Se corrigió un error de sintaxis en `bundlemaker-term.py` tras la refactorización inicial.
