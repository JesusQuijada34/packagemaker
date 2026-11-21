# Cola de bugs y reportes — Influent Package Maker

Última actualización: 2026-11-21
Fuente: [issue #4 — Backlog de Reportes Técnicos](https://github.com/JesusQuijada34/packagemaker/issues/4)
Rama de trabajo: `main`

Este archivo es la cola autoritativa de reportes. `bugs.txt` se conserva como
documento de origen y plan histórico; no se elimina mientras tenga información
de auditoría.

## Resumen

| ID | Tipo | Prioridad | Estado |
|---|---|---|---|
| R-dd68f3f4 | Bug — rutas Termux | Alta | Resuelto |
| R-730ee37a | Bug — crash UI Qt6 | Crítica | Resuelto |
| R-f478fbef | Bug — empaquetado con proyecto abierto | Alta | Resuelto |
| R-062ec1b5 | Bug — crash al abrir IDE | Alta | Resuelto |
| R-e2d317ce | Bug — gestor de apps | Media | Resuelto |
| R-739d5fec | Bug — consola Windows | Media | Resuelto |
| R-e1a87de9 | Bug — persistencia de ajustes | Alta | Resuelto |
| R-8f2c41d9 | Bug — empaquetado con backend zipapp | Alta | Resuelto |
| R-c47a9e12 | Bug — `--harden` ignorado en CLI headless | Media | Resuelto |
| R-d23039c0 | Mejora — telemetría | Media | Pendiente de aprobación |
| — | Cambios de engine (`bugs.txt`) | — | Pendiente de aprobación |

No hay bugs críticos ni de alta prioridad abiertos. Los dos últimos reportes
proceden de la auditoría interna de este ciclo (no de un usuario externo) y
quedaron corregidos y probados. No se prepara release: el periodo de
observación y el requisito de 7 días sin reportes nuevos siguen en curso.

---

## R-dd68f3f4 — Ruta de exportación en Termux/Android

- **Usuario:** JesusQuijada34 (issue #4)
- **Fecha del reporte:** 2026-07-05
- **Descripción:** en Termux la salida de compilación quedaba en el home privado
  de la app, inaccesible para el resto del dispositivo. Se pidió forzar el
  almacenamiento compartido (`/storage/emulated/0/Download/` o
  `~/storage/downloads`).
- **Pasos para reproducir:** ejecutar `--buildthis` en Termux sin `--output` y
  comprobar que el `.iflapp` no aparece en Descargas.
- **Estado:** Resuelto.
- **Prioridad:** Alta.
- **Solución aplicada:** `lib/platform_detect.compile_output_directory()`
  devuelve el Download compartido en Termux/Android y conserva la ruta histórica
  en escritorio. `lib/cliHandler.py` la usa como salida por defecto. La TUI
  obtiene además su carpeta base de `platform_detect`.
- **Pruebas:** `tests/test_issue4_reports.py::CompileOutputDirectoryTests`.
- **Commit:** `b305945`.
- **Fecha de resolución:** 2026-11-21.

## R-730ee37a — `QTextCursor.End` en PyQt6

- **Usuario:** JesusQuijada34 (issue #4)
- **Fecha del reporte:** 2026-07-05
- **Descripción:** `AttributeError: type object 'QTextCursor' has no attribute
  'End'` en `lib/outputTerminalDialog.py` al recibir stdout.
- **Pasos para reproducir:** abrir el diálogo de terminal y ejecutar un script
  que escriba en stdout con PyQt6.
- **Estado:** Resuelto (ya presente en `main` antes de este ciclo; verificado).
- **Prioridad:** Crítica.
- **Solución aplicada:** los manejadores usan
  `QtGui.QTextCursor.MoveOperation.End`.
- **Pruebas:** `tests/test_output_terminal_dialog_qt6.py`.
- **Commit:** verificado en `b305945` (código previo, sin cambios adicionales).
- **Fecha de resolución:** 2026-11-21 (verificación).

## R-f478fbef — Empaquetado `.iflapp` con proyecto abierto

- **Usuario:** JesusQuijada34 (issue #4)
- **Fecha del reporte:** 2026-07-05
- **Descripción:** el empaquetado `.iflapp` fallaba o se ignoraba cuando el
  proyecto estaba abierto en el workspace.
- **Pasos para reproducir:** abrir el proyecto en el editor y lanzar la
  compilación `.iflapp` sobre la misma carpeta.
- **Estado:** Resuelto.
- **Prioridad:** Alta.
- **Solución aplicada:** el empaquetado lee los archivos sin exigir acceso
  exclusivo y la limpieza es conservadora: `cleanup_processed_project()`
  conserva la fuente por defecto y `_cleanup_build_artifacts()` solo elimina
  `dist`/`build`/`*.spec`/artefactos de Nuitka. Se añadió una regresión que
  empaqueta con descriptores abiertos y verifica que la fuente sigue intacta.
- **Pruebas:** `tests/test_issue4_reports.py::OpenProjectPackagingTests` y
  `tests/test_processed_project_cleanup.py`.
- **Commit:** `b305945`.
- **Fecha de resolución:** 2026-11-21.

## R-062ec1b5 — `WinError 193` al abrir el IDE

- **Usuario:** JesusQuijada34 (issue #4)
- **Fecha del reporte:** 2026-07-05
- **Descripción:** `OSError: [WinError 193]` al ejecutar
  `subprocess.Popen([path, project_path])` cuando `path` no era un ejecutable.
- **Pasos para reproducir:** configurar como editor una carpeta, un archivo no
  ejecutable o una ruta vacía y pulsar «Abrir con».
- **Estado:** Resuelto (ya presente en `main`; verificado).
- **Prioridad:** Alta.
- **Solución aplicada:** `check_executable_exists()` valida archivo y permisos
  antes de lanzar; `launch_editor_or_default()` cae al abridor nativo del SO.
- **Pruebas:** `tests/test_open_with_editor_validation.py`.
- **Commit:** verificado en `b305945` (código previo).
- **Fecha de resolución:** 2026-11-21 (verificación).

## R-e2d317ce — Gestor de apps lista artefactos compilados

- **Usuario:** JesusQuijada34 (issue #4)
- **Fecha del reporte:** 2026-07-05
- **Descripción:** el gestor de aplicaciones listaba cualquier subcarpeta
  (`dist`, `build`, cachés, etc.) en lugar de solo proyectos fuente.
- **Pasos para reproducir:** abrir el gestor de apps en una carpeta base con
  salidas de compilación y comprobar que aparecen como proyectos.
- **Estado:** Resuelto.
- **Prioridad:** Media.
- **Solución aplicada:** `lib/project_locator.list_projects()` e
  `is_project_directory()` exigen `details.xml` y excluyen carpetas ocultas,
  salidas de compilación, entornos virtuales, cachés y restos de Nuitka. El
  gestor y MoonFix de la TUI usan ese listado filtrado.
- **Pruebas:** `tests/test_issue4_reports.py::ProjectListingTests`.
- **Commit:** `b305945`.
- **Fecha de resolución:** 2026-11-21.

## R-739d5fec — `UnicodeEncodeError` en consola Windows

- **Usuario:** JesusQuijada34 (issue #4)
- **Fecha del reporte:** 2026-07-05
- **Descripción:** imprimir `✔` fallaba en terminales `cp1252`.
- **Pasos para reproducir:** crear un proyecto desde la CLI con
  `sys.stdout.encoding == "cp1252"`.
- **Estado:** Resuelto (ya presente en `main`; verificado).
- **Prioridad:** Media.
- **Solución aplicada:** helper de salida segura que degrada caracteres no
  representables a ASCII cuando la codificación no es UTF-8.
- **Pruebas:** `tests/test_cli_unicode_output.py`.
- **Commit:** verificado en `b305945` (código previo).
- **Fecha de resolución:** 2026-11-21 (verificación).

## R-e1a87de9 — Persistencia y aplicación de ajustes

- **Usuario:** JesusQuijada34 (issue #4)
- **Fecha del reporte:** 2026-07-05
- **Descripción:** los cambios de rutas, idioma y preferencias no se guardaban
  o no surtían efecto en caliente.
- **Pasos para reproducir:** cambiar la carpeta de proyectos o el idioma en
  Configuración, guardar y reiniciar la aplicación.
- **Estado:** Resuelto.
- **Prioridad:** Alta.
- **Solución aplicada:** `save_app_config()` vuelca en `PMDataStore`
  (`data/pm.data`) y `_save_app_config_compact()` aplica idioma, tema y
  personalización tras guardar. Se añadió una regresión de ida y vuelta sobre un
  almacén real y una instancia nueva.
- **Pruebas:** `tests/test_issue4_reports.py::SettingsPersistenceTests` y
  `tests/test_pm_data_reset.py`.
- **Commit:** `b305945`.
- **Fecha de resolución:** 2026-11-21.

## R-8f2c41d9 — El backend zipapp no podía empaquetarse

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Descripción:** `zipapp` es el backend de reserva y el único siempre
  disponible (stdlib), pero cualquier build con `--compiler zipapp` abortaba en
  `create_package()` con «El paquete no contiene todos los binarios compilados
  esperados». El backend entrega `<guion>.pyz` y el pipeline solo aceptaba
  `<guion>` (Linux) o `<guion>.exe` (Windows): nunca había paquete.
- **Pasos para reproducir:** crear un proyecto y ejecutar
  `python packagemaker.py --buildthis <proyecto> --output <dir> --platform Linux --compiler zipapp --no-sandbox`.
- **Estado:** Resuelto.
- **Prioridad:** Alta (deja sin build a quien no tenga Nuitka/PyInstaller).
- **Solución aplicada:** `_copy_package_files()` copia los `.pyz` de `dist/` al
  paquete y `create_package()` los acepta como artefacto compilado del guion.
  La validación de artefactos ausentes se conserva.
- **Pruebas:** `tests/test_zipapp_packaging.py` (3 casos; los dos de empaquetado
  fallan sin la corrección).
- **Commit:** `5aa823b`.
- **Fecha de resolución:** 2026-11-21.

## R-c47a9e12 — `--harden` ignorado en compilaciones headless

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Descripción:** la CLI aceptaba `--harden` y lo pasaba a `FlangCompiler`,
  pero las rutas headless de `buildthis` y `compile` no llamaban a
  `apply_hardening()`: el blindaje se descartaba en silencio. Solo la GUI lo
  aplicaba (`FlangCompiler.run`).
- **Pasos para reproducir:** `python packagemaker.py --buildthis <proyecto> --compiler zipapp --harden integrity`
  y comprobar que el `.iflapp` no contiene `.iflapp.integrity`.
- **Estado:** Resuelto.
- **Prioridad:** Media (opción documentada sin efecto; no rompe el build).
- **Solución aplicada:** ambas rutas headless aplican `apply_hardening()`
  sobre el árbol del paquete antes de `compress_to_iflapp()`, en el mismo orden
  que la GUI, e informan de los métodos aplicados.
- **Pruebas:** `tests/test_cli_hardening.py::CliBuildHardeningTests`.
- **Commit:** `5aa823b`.
- **Fecha de resolución:** 2026-11-21.

---

## Mejoras pendientes de aprobación

### R-d23039c0 — Telemetría centralizada de errores

- **Usuario:** JesusQuijada34 (issue #4)
- **Fecha del reporte:** 2026-07-05
- **Estado:** Pendiente de aprobación explícita. No implementado.
- **Motivo:** envía tracebacks y datos de entorno a un servidor externo. Es una
  funcionalidad nueva con implicaciones de privacidad y red; no debe mezclarse
  con correcciones de bugs ni activarse por defecto sin decisión del
  responsable.
- **Propuesta mínima si se aprueba:** módulo `lib/errorReporter.py` con envío
  asíncrono opcional, consentimiento explícito, sin rutas de usuario ni
  credenciales, y URL configurable.

---

## Cambios de engine pendientes

Los siguientes puntos provienen de `bugs.txt`. Cambian comportamiento
fundamental, UI o empaquetado; **no se implementan sin aprobación explícita**.

### 1. Aislamiento estricto BlindCube / FlatCube y formato `.blindkpkg`

- **Actual:** `lib/compilers.py` resuelve backend con fallback Nuitka →
  PyInstaller → zipapp; `.iflapp` es el contenedor de salida.
- **Solicitado:** BlindCube compila siempre con Nuitka en entorno aislado y
  firma `.blindkpkg`; FlatCube compila con PyInstaller instalando requisitos en
  el venv del proyecto. Eliminar bloqueos `WinError 32` en `BuildThread`.
- **Efectos secundarios:** nuevo formato de artefacto, cambios en verificación,
  instalación y compatibilidad con `.iflapp` existentes.
- **Archivos:** `lib/BuildThread.py`, `lib/compilers.py`, `lib/engines.py`,
  `lib/blindcubeEngine/`, `lib/flatcubeEngine/`, `lib/iflapp_format.py`.
- **Riesgo:** alto (compatibilidad de artefactos y CI).

### 2. Pruebas previas y diálogo `.env` en BlindCube

- **Actual:** el build no ejecuta pruebas de sintaxis/offscreen ni pregunta por
  la inyección de `.env`.
- **Solicitado:** pruebas automáticas antes de compilar y diálogo con backdrop
  blur para inyección parcial/personalizada de variables.
- **Efectos secundarios:** más tiempo de build, nueva UI modal, ejecución de
  código del proyecto antes de empaquetar.
- **Archivos:** `lib/BuildThread.py`, `lib/projectConfig.py`,
  `lib/projectDetailsDialog.py`, `lib/alert_dialog.py`.
- **Riesgo:** alto (ejecuta código del usuario y altera el flujo de build).

### 3. Reorganización de `lib/` y GlassCube

- **Actual:** módulos en `lib/` y dependencia opcional `leviathan_ui`.
- **Solicitado:** mover a `blindcubesEngine/`, `flatcubeEngine/`,
  `makeselfEngine/`, integrar la librería y renombrar `leviathan-ui` a
  **GlassCube**.
- **Efectos secundarios:** imports, empaquetado, documentación y tests.
- **Archivos:** todo `lib/`, `packagemaker.py`, `requirements.txt`.
- **Riesgo:** alto (rotura masiva de imports).

### 4. Coreografía de splash y ventanas

- **Actual:** splash y titlebar existentes, sin la secuencia completa
  splash → login → verificación interna → ventana principal.
- **Solicitado:** fade tipo cortina, splash convertido en ventana de error,
  `destroy()` tras códigos de salida y triple clic en la titlebar para
  pantalla completa con ocultación animada.
- **Efectos secundarios:** ciclo de vida de ventanas y manejo de errores.
- **Archivos:** `lib/splash_bootloader.py`, `lib/splash_window.py`,
  `lib/window_chrome.py`, `lib/window_manager_bridge.py`, `packagemaker.py`.
- **Riesgo:** medio-alto.

### 5. Rediseño de UI (acento naranja, tarjetas iOS, configuración)

- **Actual:** acento azul `#0078D4`, configuración con botones Guardar/Restaurar,
  opción de editor de código y selector de modo de ventana.
- **Solicitado:** acento naranja corporativo, tarjetas con navegación en
  cascada, guardado automático, eliminar editor de código y modo de ventana,
  mover información del sistema a «Acerca de», notificaciones nativas y
  selección manual de fuentes.
- **Efectos secundarios:** cambia la identidad visual y elimina opciones que
  algunos usuarios pueden usar; afecta traducciones y tests de auditoría.
- **Archivos:** `lib/design_tokens.py`, `source/qss/*`, `lib/fluent_theme.py`,
  `packagemaker.py`, `lib/pm_dashboard.py`, `lib/font_manager.py`, `lang/*`.
- **Riesgo:** alto (regresiones visuales y de accesibilidad).

### 6. Sidebar: hover y modo contraído

- **Actual:** el hover se anima con `hover_animation.py`; el login permanece en
  la barra lateral contraída.
- **Solicitado:** corregir el parpadeo azul/gris y ocultar el bloque de login al
  contraer, mostrando solo iconos.
- **Efectos secundarios:** estados visuales del sidebar.
- **Archivos:** `lib/SidebarItem.py`, `lib/hover_animation.py`, `packagemaker.py`.
- **Riesgo:** medio.

---

## Periodo de observación y release

- Bugs abiertos: 0.
- Inicio del periodo de observación (3 días): 2026-11-21.
- Requisito de release sin reportes nuevos: 7 días consecutivos.
- Último reporte externo conocido: issue #4 (2026-07-05). El ciclo actual solo
  añadió dos correcciones de auditoría interna (commits `5aa823b`), no reportes
  de usuario; el contador de 7 días no se reinicia.
- Verificación de este ciclo: `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`
  → 457 pasan, 2 omitidos; `pyflakes` y `py_compile` limpios; build real con
  `--compiler zipapp` + `--harden integrity` produce un `.iflapp` válido con
  `.iflapp.integrity`.
- Release: **no preparado**. No se generaron `flat cube` ni `blind cube` en este
  ciclo.
