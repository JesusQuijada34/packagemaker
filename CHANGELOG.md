# Historial de Cambios - Influent Package Maker

## v3.2.7-26.05-20.13 - 2026-06-19

### Novedades y Mejoras

- **Estandarización de Nomenclatura**: Implementado el nuevo formato de paquetes `empresa.shortname.version-platform` de forma consistente en GUI, TUI y CLI.
- **Soporte Extendido para Editores**: Se han añadido los siguientes editores al diálogo "Abrir con": Zed, Fleet, Emacs, Geany, Kate y Gedit.
- **Renderizado de Iconos Mejorado en Linux**: Implementada una lógica más robusta para la detección y visualización de iconos de editores en sistemas operativos Linux.
- **Integración con `.gitignore`**: El proceso de compilación y empaquetado ahora respeta las reglas definidas en `.gitignore`, excluyendo archivos y directorios como `.git`, `.github`, `.vscode`, `__pycache__`, `build/`, `dist/`, etc.
- **Limpieza Automática de Artefactos de Compilación**: Se ha implementado la eliminación automática de las carpetas `build/`, `dist/` y los archivos `.spec` generados por PyInstaller después de cada compilación, tanto en la GUI como en la CLI (`compile` y `--buildthis`).

### Correcciones de Errores y Depuración

- **Depuración de API de Configuración**: Se implementó el método faltante `remove_user` en `PMDataStore` para evitar errores en tiempo de ejecución al restablecer configuraciones.
- **Corrección de Firma de UI**: Se eliminó el argumento inesperado `is_main` en las llamadas a `CustomTitleBar`, resolviendo fallos en la inicialización de diálogos.
- **Gestión de Tipado**: Se importó el tipo `List` en `BuildThread.py` para corregir errores de referencia en anotaciones de tipo.
- **Compatibilidad de CLI**: Se añadió el método placeholder `optimize_binaries` en el compilador para evitar errores al usar la opción `--optimize`.
- **Restauración de Estilos**: Se recuperó la definición de `get_github_style` en el script principal para asegurar el renderizado correcto de la interfaz.
- **Refactorización de MoonFix**: Se eliminaron duplicaciones de clases y funciones en el asistente de reparación para mejorar la mantenibilidad.
- **`TypeError` en `EditorInfo`**: Corregido un `TypeError` al inicializar `EditorInfo` para `pmCodeEditor` en `lib/openWithDialog.py`.
- **Fondo Blanco al Maximizar**: Solucionado el problema de fondos blancos al maximizar la ventana, asegurando consistencia visual con el tema oscuro.
- **Gradiente Radial en Iconos**: Eliminado un gradiente radial innecesario en los estilos CSS de los iconos de los editores en `lib/openWithDialog.py`.

## v3.2.7 - 2024-05-20

### Novedades y Mejoras

- **Interface Moderna Windows 11**: Barra de título personalizada, efectos visuales (acrílico, mica, blur), tema oscuro consistente, sin gradientes y fondos sólidos.
- **Sistema de Compilación Avanzado**: Detección automática de scripts, extracción de clases, gestión de dependencias y minificación.
- **Métodos de Blindado**: Simple Blind (`.iflappb`) y Super Blind (clases separadas + encriptación).
- **Multi-Plataforma**: Soporte para Windows (.exe), Android (APK vía Buildozer) y Linux (AppImage y paquetes nativos).

### Correcciones de Errores

- **Error en EditorInfo - TypeError**: Corregido `TypeError` en `lib/openWithDialog.py` al inicializar `EditorInfo`.
- **Bug de Fondo Blanco al Maximizar**: Solucionado el problema de fondos transparentes que causaban un fondo blanco al maximizar la ventana.
- **Iconos de Editores - Gradiente Radial**: Eliminado gradiente radial en los iconos de los editores para una apariencia más limpia.
