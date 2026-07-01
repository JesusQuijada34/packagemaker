# Notas de Versión - Influent Package Maker v3.2.7-26.05-20.13

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

### 📦 Gestión de Compilación y Nomenclatura

- **Estandarización de Nomenclatura**: Hemos implementado una nueva fórmula de nomenclatura para los paquetes generados: `empresa.shortname.version-platform`. Este formato ahora se aplica de manera consistente tanto en la interfaz gráfica (GUI) como en la interfaz de texto (TUI) y la línea de comandos (CLI).

- **Integración con `.gitignore`**: El proceso de compilación y empaquetado ahora respeta automáticamente las reglas definidas en tu archivo `.gitignore`. Esto significa que los archivos y directorios especificados en `.gitignore` (incluyendo elementos comunes de desarrollo como `.git`, `.github`, `.vscode`, `__pycache__`, `build/`, `dist/`, etc.) serán excluidos del paquete final, resultando en distribuciones más limpias y ligeras.

- **Limpieza Automática de Artefactos de Compilación**: Para mantener tu directorio de proyecto ordenado, Package Maker ahora realiza una limpieza automática después de cada proceso de compilación y empaquetado. Esto incluye la eliminación de carpetas `build/`, `dist/` y archivos `.spec`.

### 🐛 Depuración y Estabilidad

- **Corrección de API de Configuración**: Se ha implementado el método `remove_user` en el motor de datos para evitar cierres inesperados al restablecer la configuración de la aplicación.
- **Estabilidad de Interfaz**: Se han corregido las firmas de los componentes de la interfaz de usuario (`CustomTitleBar`) para asegurar que todos los diálogos se abran correctamente sin errores de argumentos.
- **Gestión de Tipado y Código**: Se han resuelto errores de importación y referencias indefinidas en el motor de compilación y en el asistente MoonFix, mejorando la robustez general del código.
- **`TypeError` en `EditorInfo`**: Se ha corregido un error que causaba un `TypeError` al inicializar la información del editor `pmCodeEditor`.
- **Fondo Blanco al Maximizar**: Se ha resuelto un problema visual donde el fondo de la aplicación se volvía blanco al maximizar la ventana.
- **Gradiente Radial en Iconos**: Se ha eliminado un gradiente radial innecesario en los estilos CSS de los iconos de los editores.

## ✨ Próximos Pasos

Continuaremos trabajando en optimizaciones de rendimiento, más opciones de personalización y soporte para plataformas adicionales. ¡Agradecemos tus comentarios y contribuciones!
