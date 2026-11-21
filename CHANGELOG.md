# Changelog

## 2026-11-21

### Corregido

Reportes del [issue #4](https://github.com/JesusQuijada34/packagemaker/issues/4), reportados por JesusQuijada34.

- **R-dd68f3f4 — Exportación en Termux/Android:** `compile_output_directory()` en `lib/platform_detect.py` exporta los `.iflapp` al almacenamiento compartido (Download) en Termux/Android y conserva la ruta histórica en escritorio. La CLI usa esa carpeta como salida por defecto y la TUI toma su carpeta base del detector de plataforma. Commit `b305945`.
- **R-e2d317ce — Gestor de apps:** `list_projects()`/`is_project_directory()` en `lib/project_locator.py` exigen `details.xml` y excluyen `dist`, `build`, `releases`, cachés, entornos virtuales y restos de Nuitka. El gestor y MoonFix de la TUI listan solo proyectos fuente. Commit `b305945`.
- **R-f478fbef — Empaquetado con proyecto abierto:** regresión que empaqueta `.iflapp` con archivos del proyecto abiertos y confirma que la fuente se conserva; la limpieza solo elimina artefactos de compilación. Commit `b305945`.
- **R-e1a87de9 — Persistencia de ajustes:** regresión de ida y vuelta sobre `PMDataStore` que verifica que `save_app_config()` persiste rutas, idioma y preferencias y que se releen en una instancia nueva. Commit `b305945`.
- **R-730ee37a, R-062ec1b5, R-739d5fec:** verificados como ya resueltos en `main` (cursor Qt6, validación del editor externo y salida Unicode segura) con sus pruebas existentes.

### Corregido — auditoría interna

Hallazgos de la revisión de mantenimiento de este ciclo (sin reporte externo; reportados por JesusQuijada34 en la auditoría interna).

- **R-8f2c41d9 — Empaquetado con el backend zipapp:** `zipapp` es el backend de reserva siempre disponible, pero `create_package()` solo aceptaba `<guion>`/`<guion>.exe` y rechazaba el `<guion>.pyz` que produce el backend, así que ningún build con `--compiler zipapp` llegaba a generar paquete. Ahora `_copy_package_files()` copia los `.pyz` al paquete y `create_package()` los acepta; la detección de artefactos ausentes se conserva. Commit `5aa823b`.
- **R-c47a9e12 — `--harden` ignorado en CLI headless:** las rutas de `buildthis` y `compile` no invocaban `apply_hardening()`, por lo que los métodos de blindaje se descartaban sin aviso. Ahora se aplican sobre el árbol del paquete antes de comprimir, igual que la GUI. Commit `5aa823b`.

### Corregido — auditoría interna del CLI

Hallazgos del segundo ciclo de mantenimiento (sin reporte externo; reportados por JesusQuijada34 en la auditoría interna). Commit `d2670a1`.

- **R-2e83a7bd — El subcomando `compile` ignoraba la salida de Termux:** usaba una ruta fija `~/Documents/…`, inaccesible en Android/Termux. Ahora toma la salida de `compile_output_directory()`, igual que `--buildthis`; en escritorio la ruta no cambia.
- **R-4b7e91a2 — El banner contaminaba la salida JSON:** las líneas `[PackageMaker] …` se imprimían en stdout y rompían `--inspect-json`, `--shell-info-json` y `--ide-scan-json`. Ahora van a stderr.
- **R-9c1d5f60 — `create` no copiaba el icono fuera de la raíz:** el icono se buscaba con una ruta relativa al CWD; ejecutado desde otro directorio el proyecto quedaba sin icono y el `.iflapp` salía con `Icono: 0 bytes`. Ahora se resuelve contra la raíz del repo, el bundle, el ejecutable y el CWD, y se avisa si no aparece.
- **R-a5f06c38 — `--harden` inválido en silencio:** un método mal escrito se descartaba sin aviso y podía dejar el build sin blindaje aparentando tenerlo. Ahora se informa de los métodos ignorados y de la desactivación total.
- **R-d74e0b19 — `--ide-compile` duplicaba la salida:** el log se imprimía por el callback y otra vez al recorrer `outcome.log`. Ahora se imprime una sola vez.

### Corregido — metadatos no canónicos en el CLI

Hallazgo del tercer ciclo de mantenimiento (sin reporte externo; reportado por JesusQuijada34 en la auditoría interna).

- **R-b3f71a6c — Un publisher o identificador fuera de la ley de nombres rompía el CLI:** `create`, `--buildthis`, `compile` y `moonfix` llamaban a `format_project_folder()` sin capturar el `ValueError`, así que un publisher como `Jesús` terminaba en un traceback. En `--buildthis` el proyecto se compilaba completo y el fallo aparecía al final, sin generar artefacto. Ahora `_canonical_folder_or_exit()` valida antes de compilar y aborta con `[ERROR] Metadatos de proyecto no válidos: …` y código 1; `create` y `moonfix` usan la misma validación. La ley de nombres no cambia.

### Mantenimiento

- `lib/requirements-dev.txt` resuelve correctamente su include (`-r requirements.txt`) y la documentación usa la ruta real `lib/requirements-dev.txt`.

### Verificación

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 467 pasan, 1 omitido (el omitido depende de `leviathan_ui`).
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Build real con `--compiler zipapp --harden integrity`: `.iflapp` válido con `.iflapp.integrity` en el manifiesto.
- `--inspect-json` emite JSON parseable en stdout (banner en stderr).
- `create`, `--buildthis` y `moonfix` con metadatos no canónicos abortan con error legible y código 1, sin traceback.

### Pendiente de aprobación

- **R-d23039c0 — Telemetría de errores:** no implementada (envía datos a un servidor externo).
- **R-5d8e2a41 — Acentos en publisher/appname:** no implementada; cambia la ley de nombres.
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
