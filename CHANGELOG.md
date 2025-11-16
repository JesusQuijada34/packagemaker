# CHANGELOG - Influent Package Maker

## v3.2.3 - Import, Theme & Titlebar Polish (2025-11-15)

### 🚀 Novedades y Mejoras
- **Nuevo encabezado y organización de imports:** 
  - Añadido encabezado shebang (`#!/usr/bin/env/python`), codificación UTF-8 y un bloque de imports explícito para mayor claridad y portabilidad.
  - Importación clara de librerías estándar (`sys`, `os`, `time`, `hashlib`, `shutil`, `zipfile`, `xml.etree.ElementTree`, `urllib.request`, `urllib.error`, `subprocess`).
  - Todas las importaciones de PyQt5 ahora centralizadas, incluyendo submódulos para widgets y gráficos, y nuevas importaciones explícitas de `QSvgRenderer`, `QPixmap`, y `QByteArray` para soporte SVG e iconos personalizados en la titlebar.
  - Importación segura y condicional de `winreg` y `pyi_splash` solo si es pertinente.
- **Bloque de configuración y constantes reorganizado:**
  - Defines explícitos para fuentes, estilos de botones, rutas y estructuras usadas en toda la app.
  - Estructura de rutas multiplataforma con detección y creación automática.
- **Nuevas mejoras visuales y de interfaz:**
  - Ajuste de los estilos QSS (PyQt Stylesheet) para mejor visualización en modo claro y oscuro y acentos modernos tipo GitHub.
  - Mejoras y comentarios en custom titlebar con SVG para botones de minimizar, maximizar y cerrar.
  - Lógica detallada para doble clic en la barra de título y arrastre solo cuando la ventana no está maximizada.
- **Importación detallada y comentarios para mejor mantenibilidad**, ideal para nuevos desarrolladores que deseen ubicar rápidamente las dependencias y entradas necesarias.

### 🐞 Correcciones y Refactorizaciones
- Evita imports duplicados y asegura la ordenación lógica en toda la cabecera.
- Añadido control de errores explícito en imports condicionales (p. ej. `winreg`, `pyi_splash` bajo `sys.frozen`).
- Todos los imports para soporte SVG en los iconos de la titlebar ahora son directos y explícitamente comentados.

---

## v3.2.0 - Actualizador Modernizado (2025-11-09)

### 🚀 Novedades y Mejoras
- **Reescritura Completa de `updater.py`:** El script de actualización ha sido reescrito desde cero para una experiencia de usuario moderna y eficiente.
- **Interfaz Gráfica con PyQt5:** Se implementó una interfaz de usuario moderna y atractiva, inspirada en el estilo de GitHub, utilizando la librería PyQt5.
- **Verificación de Actualización Silenciosa:** El actualizador ahora verifica la disponibilidad de una nueva versión en segundo plano y **solo muestra la interfaz si se encuentra una actualización**.
- **Selección de Tipo de Descarga:** La interfaz permite al usuario elegir entre descargar el **Código Fuente** o el **Binario** específico para su sistema operativo (Windows/Linux).
- **Lógica de Reinicio y Verificación de Actualizaciones del Sistema:** Se implementó la lógica para simular el reinicio del actualizador después de una actualización exitosa y la posterior verificación de actualizaciones del sistema en segundo plano.

---

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
