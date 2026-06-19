# Notas de Versión - Influent Package Maker v3.3.0

## 🚀 Novedades y Mejoras

Esta versión de Influent Package Maker se centra en mejorar la experiencia del desarrollador, la flexibilidad en la elección de editores y la limpieza del entorno de compilación.

### 🛠️ Mejoras en la Detección y Uso de Editores

- **Soporte Extendido para Editores**: Hemos ampliado significativamente la lista de editores de código soportados en el diálogo "Abrir con". Ahora puedes integrar y lanzar tus proyectos directamente con:
    - **Zed**
    - **Fleet**
    - **Emacs**
    - **Geany**
    - **Kate**
    - **Gedit**

- **Renderizado de Iconos Mejorado en Linux**: Se ha implementado una lógica más robusta para la detección y visualización de iconos de editores en sistemas operativos Linux (como Ubuntu). Esto asegura que los iconos de tus editores favoritos se muestren correctamente en la interfaz de Package Maker.

### 📦 Gestión de Compilación y Limpieza

- **Integración con `.gitignore`**: El proceso de compilación y empaquetado ahora respeta automáticamente las reglas definidas en tu archivo `.gitignore`. Esto significa que los archivos y directorios especificados en `.gitignore` (incluyendo elementos comunes de desarrollo como `.git`, `.github`, `.vscode`, `__pycache__`, `build/`, `dist/`, etc.) serán excluidos del paquete final, resultando en distribuciones más limpias y ligeras.

- **Limpieza Automática de Artefactos de Compilación**: Para mantener tu directorio de proyecto ordenado, Package Maker ahora realiza una limpieza automática después de cada proceso de compilación y empaquetado. Esto incluye la eliminación de:
    - Carpetas `build/` generadas por PyInstaller.
    - Carpetas `dist/` que contienen los ejecutables temporales.
    - Archivos `.spec` creados por PyInstaller.
    Esta limpieza se aplica tanto al compilar desde la interfaz gráfica como desde la línea de comandos (comandos `compile` y `--buildthis`).

### 🐛 Correcciones de Errores

- **`TypeError` en `EditorInfo`**: Se ha corregido un error que causaba un `TypeError` al inicializar la información del editor `pmCodeEditor` en `lib/openWithDialog.py`, asegurando que el campo `executable` se pase correctamente.
- **Fondo Blanco al Maximizar**: Se ha resuelto un problema visual donde el fondo de la aplicación se volvía blanco al maximizar la ventana. Ahora, la interfaz mantiene su consistencia visual con el tema oscuro en todo momento.
- **Gradiente Radial en Iconos**: Se ha eliminado un gradiente radial innecesario en los estilos CSS de los iconos de los editores, lo que contribuye a una apariencia más limpia y moderna del diálogo "Abrir con".

## ✨ Próximos Pasos

Continuaremos trabajando en optimizaciones de rendimiento, más opciones de personalización y soporte para plataformas adicionales. ¡Agradecemos tus comentarios y contribuciones!
