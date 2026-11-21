# Changelog

## 2026-11-21

### Corregido

Reportes del [issue #4](https://github.com/JesusQuijada34/packagemaker/issues/4), reportados por JesusQuijada34.

- **R-dd68f3f4 — Exportación en Termux/Android:** `compile_output_directory()` en `lib/platform_detect.py` exporta los `.iflapp` al almacenamiento compartido (Download) en Termux/Android y conserva la ruta histórica en escritorio. La CLI usa esa carpeta como salida por defecto y la TUI toma su carpeta base del detector de plataforma. Commit `b305945`.
- **R-e2d317ce — Gestor de apps:** `list_projects()`/`is_project_directory()` en `lib/project_locator.py` exigen `details.xml` y excluyen `dist`, `build`, `releases`, cachés, entornos virtuales y restos de Nuitka. El gestor y MoonFix de la TUI listan solo proyectos fuente. Commit `b305945`.
- **R-f478fbef — Empaquetado con proyecto abierto:** regresión que empaqueta `.iflapp` con archivos del proyecto abiertos y confirma que la fuente se conserva; la limpieza solo elimina artefactos de compilación. Commit `b305945`.
- **R-e1a87de9 — Persistencia de ajustes:** regresión de ida y vuelta sobre `PMDataStore` que verifica que `save_app_config()` persiste rutas, idioma y preferencias y que se releen en una instancia nueva. Commit `b305945`.
- **R-730ee37a, R-062ec1b5, R-739d5fec:** verificados como ya resueltos en `main` (cursor Qt6, validación del editor externo y salida Unicode segura) con sus pruebas existentes.

### Mantenimiento

- `lib/requirements-dev.txt` resuelve correctamente su include (`-r requirements.txt`) y la documentación usa la ruta real `lib/requirements-dev.txt`.

### Verificación

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 454 pasan, 1 omitido.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.

### Pendiente de aprobación

- **R-d23039c0 — Telemetría de errores:** no implementada (envía datos a un servidor externo).
- **Cambios de engine de `bugs.txt`:** registrados en `bugs.md`, sin implementar.

## 2026-11-15

### Corregido

- Importación de `Qt` en `lib/fluent_theme.py` para evitar el `NameError` al consultar `Qt.ColorScheme`.
- Legibilidad del tema claro: los tokens de texto principal y texto atenuado usan negro para conservar contraste.
- Fondo del splash integrado: usa el color de acento configurado en la aplicación en lugar de un color fijo.
- Pila tipográfica: Roboto pasa a ser la primera opción de la interfaz.
- Claves de traducción faltantes en los idiomas disponibles, con fallback controlado a inglés/español.

### Verificación

- La auditoría de tema, diálogos, checkboxes, barra de estado y regresiones visuales pasa con `QT_QPA_PLATFORM=offscreen`.
- La extracción completa de textos hardcodeados en español sigue pendiente y permanece señalada en `bugs.txt`.

### Arquitectura `.mexf` / `.asksome`

- Se añadió un parser YAML v1 declarativo con validación de metadatos, IDs, assets y argumentos argv.
- El formato JSON de `example.mexf` se detecta como legacy y puede migrarse explícitamente a YAML.
- Se añadió un contenedor `.asksome` determinista con manifiesto, digest, firma local y extracción contra traversal/enlaces.
- Se declaró PyYAML como dependencia del parser.
