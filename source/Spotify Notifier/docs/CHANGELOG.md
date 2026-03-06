# Changelog - Spotify Notifier

## [2.0.0] - 2026-03-06

### Added
- **Integración con VLC**: Implementación de `python-vlc` para una gestión de audio profesional y estable.
- **Workbench Nativo**: Rediseño completo del reproductor principal con una estructura de capas más limpia.
- **Tipografía Roboto**: Implementación de la fuente Roboto para una apariencia más moderna y profesional.

### Fixed
- **UpdateLayeredWindowIndirect**: Corregida la lógica de renderizado para evitar discrepancias en el tamaño del buffer de Windows.
- **Visibilidad GhostBlur**: Ajustada la opacidad y el color de fondo de las capas de renderizado para asegurar que el contenido sea legible sobre el efecto de desenfoque.
- **Estabilidad de UI**: Uso de `QRectF` y conversiones explícitas a float para evitar errores de tipo en el dibujado de rectángulos redondeados.

### Changed
- **Estructura de Proyecto**: Organización profesional de carpetas siguiendo los estándares establecidos.
- **Lógica de Posicionamiento**: Mejora en el algoritmo de interpolación (Lerp) para el movimiento de las notificaciones.
