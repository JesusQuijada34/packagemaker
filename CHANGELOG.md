# Historial de Cambios - Package Maker

## [v3.2.6] - 2026-01-25
Esta versión expande el ecosistema hacia dispositivos móviles y fortalece la integridad de los paquetes mediante la nueva Suite MoonFix.

### ✨ Nuevas Características
*   **Android Mobile Replica**: Lanzamiento de la interfaz móvil premium en `android/index.html`. Una réplica exacta con diseño adaptativo, animaciones fluidas y navegación por gestos para dispositivos Android.
*   **MoonFix Suite**: Nueva herramienta de diagnóstico profundo que escanea, detecta y repara automáticamente inconsistencias en la estructura de carpetas, archivos XML y activos visuales.
*   **Priorización de Recursos Remotos**: El sistema de previsualización ahora prioriza las URLs `raw.githubusercontent.com` para cargar splash screens y logos, garantizando que la documentación web siempre sea funcional independientemente de la ubicación local.

### 🚀 Mejoras
*   **Unificación de Documentación**: La generación de `docs/index.html` ahora está centralizada y automatiza la inyección de metadatos (Autor, Repositorio, Versión) en cada proyecto.
*   **Efectos Visuales Premium**: Aplicación de `GhostBlur` y `WipeWindow` de Leviathan-UI para una estética acrílica de alta gama.
*   **Optimización de Red**: Implementación de User-Agents personalizados para las descargas de iconos via `requests` para evitar bloqueos por parte de CDNs.

---

## [v3.2.0] - 2026-01-17
*   **Integración con Leviathan-UI v1.1.0**: Actualización de dependencias críticas.
*   **Barra de Progreso Marquee**: Feedback visual mejorado durante la compilación.
*   **Diálogos Modernos**: Reemplazo total de diálogos nativos por `LeviathanDialog`.

---

## [3.1.5] - 2025-12-17
*   **Real-time Project Watcher**: Actualización dinámica de listas de proyectos.
*   **Icon Selection**: Selector de archivos `.ico` integrado.
*   **Autocomplete**: Autocompletado recursivo en campos de construcción.
