# Cola de bugs y reportes — Influent Package Maker

Última actualización: 2026-11-22
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
| R-2e83a7bd | Bug — `compile` ignora salida Termux | Alta | Resuelto |
| R-4b7e91a2 | Bug — banner contamina salida JSON | Media | Resuelto |
| R-9c1d5f60 | Bug — icono no copiado fuera del repo | Media | Resuelto |
| R-a5f06c38 | Bug — `--harden` inválido silencioso | Media | Resuelto |
| R-d74e0b19 | Bug — `--ide-compile` duplica salida | Baja | Resuelto |
| R-b3f71a6c | Bug — metadatos no canónicos rompen el CLI | Alta | Resuelto |
| R-7c1e4a90 | Bug — `compile`/`moonfix` eligen mal el proyecto | Alta | Resuelto |
| R-91b6d2f4 | Bug — verificación sandbox con `--password` | Media | Resuelto |
| R-3a7c5e18 | Bug — avisos de importación contaminan JSON | Alta | Resuelto |
| R-9f2b64d1 | Bug — avisos auxiliares contaminan JSON | Media | Resuelto |
| R-6e04c8ab | Bug — aviso de MoonFix no codificable (cp1252) | Media | Resuelto |
| R-7d5b91c4 | Bug — MoonFix rompe la marca temporal canónica | Media | Resuelto |
| R-3f9a2c71 | Bug — dropper lanza `updater.py` en builds zipapp | Media | Resuelto |
| R-7b1d4e92 | Bug — `--inspect` acepta cabeceras truncadas | Baja | Resuelto |
| R-8a4f1c6d | Bug — cabeceras con tipos inesperados rompen `--inspect` | Baja | Resuelto |
| R-1c93e4b7 | Bug — stdlib tratada como dependencia PyPI en el editor | Media | Resuelto |
| R-4d7b2e91 | Bug — `updater.py` aborta sin `leviathan_ui` | Alta | Resuelto |
| R-6b1f8d20 | Bug — `--force-fonts` ignorado y cae en la TUI | Media | Resuelto |
| R-9e2a5c73 | Bug — `--app-version` reporta una versión fija | Media | Resuelto |
| R-2a7f6b41 | Bug — plataforma de la cabecera ≠ `details.xml` | Baja | Resuelto |
| R-6f2b9d31 | Bug — `--harden obfuscate` generaba Python inválido | Alta | Resuelto |
| R-8c4e1a72 | Bug — contenedores de motor con cabecera corrupta | Media | Resuelto |
| R-1f4a7c92 | Bug — `pm.data`/`settings.json` con forma no-objeto tumban el arranque | Alta | Resuelto |
| R-2b6d8e13 | Bug — cabeceras `.asksome` malformadas rompen `--shell-info` | Media | Resuelto |
| R-3c9e1a57 | Bug — extracción `.asksome` acepta rutas de unidad y errores crudos | Media | Resuelto |
| R-5f8c2d91 | Bug — errores de `--inspect`/`--shell-info` contaminan el JSON | Media | Resuelto |
| R-7e3a9c14 | Bug — accesos `.desktop` con rutas con espacios | Alta | Resuelto |
| R-4b8d2f61 | Bug — `install.json` corrupto rompe `--build-removeme` | Media | Resuelto |
| R-9c5f1e28 | Bug — `.mexf` legacy con tipos inesperados rompe `--shell-plan` | Media | Resuelto |
| R-4a1e7b93 | Bug — limpieza del build sin reintentos (`WinError 32`) | Alta | Resuelto |
| R-8d2c5f60 | Bug — `blindcubeEngine` acoplado a `makeselfEngine` | Media | Resuelto |
| R-9b4e7a52 | Bug — `.mexf` v1 con secciones mal tipadas rompe `--compile-mexf`/`--debug-mexf` | Alta | Resuelto |
| R-2f7c8d31 | Bug — el identificador `.mexf` escapa del directorio de integración | Alta | Resuelto |
| R-6a1d3c94 | Bug — `.mexf` no UTF-8 provoca traceback en el CLI | Media | Resuelto |
| R-8e5b2f17 | Bug — `lib.native_shell --info` sin archivo lanza traceback | Baja | Resuelto |
| R-d23039c0 | Mejora — telemetría | Media | Pendiente de aprobación |
| R-5d8e2a41 | Mejora — nombres con acentos | Media | Pendiente de aprobación |
| R-4c8e1f27 | Mejora — capitalización del publisher | Baja | Pendiente de aprobación |
| R-3e7d1c58 | Mejora — `compile-only` deja el fuente en el paquete | Baja | Pendiente de aprobación |
| — | Cambios de engine (`bugs.txt`) | — | Pendiente de aprobación |

No hay bugs críticos ni de alta prioridad abiertos. Los reportes de auditoría
interna de los ciclos de mantenimiento (R-8f2c41d9, R-c47a9e12 y los cinco del
ciclo CLI, más R-b3f71a6c, R-7c1e4a90, R-91b6d2f4, R-3a7c5e18, R-9f2b64d1,
R-6e04c8ab, R-7d5b91c4, R-3f9a2c71, R-7b1d4e92, R-8a4f1c6d, R-1c93e4b7,
R-4d7b2e91, R-6b1f8d20, R-9e2a5c73, R-2a7f6b41, R-6f2b9d31, R-8c4e1a72,
R-1f4a7c92, R-2b6d8e13, R-3c9e1a57, R-5f8c2d91, R-7e3a9c14, R-4b8d2f61,
R-9c5f1e28, R-4a1e7b93, R-8d2c5f60, R-9b4e7a52, R-2f7c8d31, R-6a1d3c94 y
R-8e5b2f17)
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

## R-2e83a7bd — El subcomando `compile` ignoraba la salida de Termux

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Descripción:** `--buildthis` exporta al almacenamiento compartido en
  Termux/Android desde R-dd68f3f4, pero el subcomando moderno `compile`
  conservaba una ruta fija `~/Documents/Packagemaker Projects/Compiled`. En
  Termux ese home es privado de la app, así que el `.iflapp` quedaba
  inaccesible para el resto del dispositivo: la misma regresión reportada,
  por otra puerta de entrada.
- **Pasos para reproducir:** en Termux, `python packagemaker.py compile --name Demo --shortname demo --headless` y buscar el artefacto en Download.
- **Estado:** Resuelto.
- **Prioridad:** Alta (el artefacto no es accesible en Android/Termux).
- **Solución aplicada:** la ruta de salida se obtiene de
  `lib/platform_detect.compile_output_directory()`, compartida con
  `--buildthis`; en escritorio devuelve la misma ruta histórica.
- **Pruebas:** `tests/test_maintenance_cli_regressions.py::CompileSubcommandOutputDirectoryTests`.
- **Commit:** `d2670a1`.
- **Fecha de resolución:** 2026-11-21.

## R-4b7e91a2 — El banner de plataforma contaminaba la salida JSON

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Descripción:** `--inspect-json`, `--shell-info-json` y `--ide-scan-json`
  prometen JSON en stdout, pero las tres líneas del banner
  (`[PackageMaker] Platform detected…`, `BASE_DIR`, `Fluthin_APPS`) se
  imprimían en stdout y rompían a cualquier consumidor que hiciera
  `json.loads(stdout)`.
- **Pasos para reproducir:** `python packagemaker.py --inspect paquete.iflapp --inspect-json | python -m json.tool`.
- **Estado:** Resuelto.
- **Prioridad:** Media (rompe automatización y CI; la salida humana no cambia).
- **Solución aplicada:** el banner y sus mensajes de fallback se escriben en
  `stderr`; stdout queda reservado para el resultado de la acción.
- **Pruebas:** `tests/test_maintenance_cli_regressions.py::JsonOutputPurityTests`.
- **Commit:** `d2670a1`.
- **Fecha de resolución:** 2026-11-21.

## R-9c1d5f60 — `create` no copiaba el icono fuera de la raíz del repo

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Descripción:** el subcomando `create --headless` copiaba el icono desde la
  ruta relativa `app/app-icon.ico`. Si se ejecutaba desde otro directorio de
  trabajo (caso normal de un comando instalado), el proyecto se creaba sin
  icono y sin aviso; el `.iflapp` resultante llevaba `Icono: 0 bytes`.
- **Pasos para reproducir:** `cd /tmp && python /ruta/packagemaker.py create --name Demo --shortname demo --headless` y comprobar `app/app-icon.ico`.
- **Estado:** Resuelto.
- **Prioridad:** Media (artefacto final sin icono, fallo silencioso).
- **Solución aplicada:** `_bundled_app_icon()` busca el icono en la raíz del
  repositorio, el bundle de PyInstaller, el directorio del ejecutable y el CWD;
  si no lo encuentra, avisa en lugar de callar.
- **Pruebas:** `tests/test_maintenance_cli_regressions.py::CreateIconOutsideRepoRootTests`.
- **Commit:** `d2670a1`.
- **Fecha de resolución:** 2026-11-21.

## R-a5f06c38 — Un método de `--harden` mal escrito desactivaba el blindaje

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Descripción:** `_parse_hardening()` descartaba en silencio los métodos
  desconocidos. `--harden strip,bogus` aplicaba solo `strip` sin avisar y
  `--harden bogus` dejaba el build sin ningún blindaje, con apariencia de
  haberlo aplicado.
- **Pasos para reproducir:** `python packagemaker.py --buildthis <proyecto> --harden bogus` y revisar el `.iflapp`.
- **Estado:** Resuelto.
- **Prioridad:** Media (fallo silencioso con implicación de seguridad).
- **Solución aplicada:** se informa por `stderr` de los métodos ignorados y, si
  no queda ninguno válido, de que el blindaje queda desactivado. La selección
  de métodos válidos no cambia.
- **Pruebas:** `tests/test_maintenance_cli_regressions.py::HardeningParseWarningTests`.
- **Commit:** `d2670a1`.
- **Fecha de resolución:** 2026-11-21.

## R-d74e0b19 — `--ide-compile` imprimía cada línea dos veces

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Descripción:** `IflappIdeHelper.compile()` pasaba `log=print` (que ya
  escribe cada mensaje) y después recorría `outcome.log` volviendo a imprimirlo,
  duplicando la salida de `--ide-compile`.
- **Pasos para reproducir:** `python packagemaker.py --ide-compile <proyecto> --ide-backend zipapp` y contar las líneas `[INFO] Compilando…`.
- **Estado:** Resuelto.
- **Prioridad:** Baja (cosmético; no altera el artefacto).
- **Solución aplicada:** se deja de pasar `log=print`; el log se imprime una
  sola vez desde `outcome.log`.
- **Pruebas:** `tests/test_maintenance_cli_regressions.py::IdeCompileLoggingTests`.
- **Commit:** `d2670a1`.
- **Fecha de resolución:** 2026-11-21.

## R-b3f71a6c — Metadatos no canónicos rompían el CLI con un traceback

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Descripción:** la ley de nombres valida publisher e identificador con
  `_SAFE_SEGMENT_PATTERN` (solo ASCII), pero `create`, `--buildthis`, `compile` y
  `moonfix` llamaban a `format_project_folder()` sin capturar el `ValueError`.
  Un publisher natural en español (`Jesús`), un acento en el shortname o
  cualquier carácter fuera del patrón terminaba en un traceback de Python.
  En `--buildthis` era peor: el proyecto se compilaba completo y solo al final,
  al calcular el nombre del paquete, saltaba el error; no se generaba artefacto.
- **Pasos para reproducir:** `python packagemaker.py create --name Demo --shortname demo --publisher "Jesús" --headless`
  o `python packagemaker.py --buildthis <proyecto con publisher acentuado> --compiler zipapp`.
- **Estado:** Resuelto.
- **Prioridad:** Alta (pierde el build completo sin artefacto y sin mensaje útil).
- **Solución aplicada:** helper `_canonical_folder_or_exit()` en `lib/cliHandler.py`
  valida la ley de nombres y aborta con `[ERROR] Metadatos de proyecto no válidos: …`
  y código 1. `_validate_compiler_metadata()` la aplica tras `parse_details_xml()`
  y antes de `compile_binaries()`, tanto en `--buildthis` como en `compile`;
  `create` y `moonfix` también la usan. La ley de nombres no cambia.
- **Pruebas:** `tests/test_maintenance_cli_regressions.py::InvalidCanonicalMetadataTests`
  (3 casos; los 3 fallan en el código anterior).
- **Commit:** `e84e367`.
- **Fecha de resolución:** 2026-11-21.

## R-7c1e4a90 — `compile`/`moonfix` compilaban el proyecto equivocado

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Descripción:** los subcomandos `compile` y `moonfix`/`repair` localizaban el
  proyecto recorriendo la carpeta base con `publisher in nombre and app in
  nombre`. Con `demo` y `demo2` en la misma carpeta, el prefijo elegía `demo2`
  (el primero que devolviera el sistema de archivos) y compilaba el proyecto
  equivocado. Además, si la carpeta base aún no existía, `iterdir()` lanzaba
  `FileNotFoundError` con traceback en lugar de un error legible.
- **Pasos para reproducir:** crear `influent.demo2…` y `influent.demo…` en la
  carpeta base y ejecutar `python packagemaker.py compile --name Demo --shortname demo --publisher Influent`;
  o ejecutar `compile` en una instalación nueva sin carpeta de proyectos.
- **Estado:** Resuelto.
- **Prioridad:** Alta (puede compilar y publicar el proyecto equivocado).
- **Solución aplicada:** ambos subcomandos usan `locate_project()`, que compara
  la identidad canónica de la carpeta (`parse_project_folder`) y cae a
  `details.xml` solo para carpetas no canónicas. La búsqueda no depende del orden
  del sistema de archivos, sigue encontrando proyectos con metadatos inválidos
  (necesario para MoonFix) y devuelve `None` si la carpeta base no existe.
- **Pruebas:** `tests/test_maintenance_cli_regressions.py::CompileProjectSelectionTests`
  (3 casos; el de selección falla en el código anterior con `demo2`).
- **Commit:** `ab79f4a`.
- **Fecha de resolución:** 2026-11-21.

## R-91b6d2f4 — La verificación en sandbox no descifraba los paquetes con `--password`

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Descripción:** `FlangCompiler.verify_in_sandbox()` genera un script que llama
  a `extract_iflapp(pkg, dest)` sin pasar la contraseña. En cualquier build con
  `--password` la extracción fallaba (`IflappError` de descifrado) y la
  verificación se degradaba a `[WARN] Verificación en sandbox incompleta`, de
  modo que los paquetes cifrados nunca se verificaban.
- **Pasos para reproducir:** `python packagemaker.py --buildthis <proyecto> --compiler zipapp --password secret123`
  y revisar el aviso de verificación incompleta.
- **Estado:** Resuelto.
- **Prioridad:** Media (el build se genera, pero se omite la verificación de un
  paquete cifrado).
- **Solución aplicada:** la contraseña viaja por la variable de entorno
  `IFLAPP_VERIFY_PASSWORD` (no por `argv`) y el script del sandbox la pasa a
  `extract_iflapp(..., password=...)`. Sin contraseña el comportamiento no cambia.
- **Pruebas:** `tests/test_maintenance_cli_regressions.py::EncryptedSandboxVerificationTests`
  (ejecuta el script real del sandbox contra un `.iflapp` cifrado).
- **Commit:** `ab79f4a`.
- **Fecha de resolución:** 2026-11-21.

## R-3a7c5e18 — Los avisos de importación contaminaban las acciones JSON

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Descripción:** al importar `packagemaker.py`, la falta de la dependencia
  opcional `leviathan_ui` imprimía `[WARN] Leviathan UI unavailable or syntax
  error: …` en **stdout**; sin PyQt6 se añadía además `font: none`. Cualquier
  acción que promete JSON en stdout (`--inspect-json`, `--shell-plan-json`,
  `--shell-info-json`, `--ide-scan-json`) quedaba precedida por esas líneas y
  dejaba de ser parseable. Es una regresión de la misma clase que R-4b7e91a2,
  por otra fuente de salida, y la propia prueba
  `JsonOutputPurityTests::test_inspect_json_stdout_is_parseable` fallaba en un
  entorno limpio sin `leviathan_ui`.
- **Pasos para reproducir:** en un entorno sin `leviathan_ui`,
  `python packagemaker.py --shell-plan example.mexf --shell-plan-json | python -m json.tool`.
- **Estado:** Resuelto.
- **Prioridad:** Alta (rompe toda la automatización que consume JSON; afecta a
  cuatro acciones documentadas).
- **Solución aplicada:** los avisos de importación de `leviathan_ui`, el de
  registro de fuentes y el de ausencia de PyQt6 se escriben en `stderr`.
  `stdout` queda reservado para el resultado de la acción.
- **Pruebas:** `tests/test_maintenance_cli_regressions.py::JsonPurityWithoutOptionalUiTests`
  (inyecta un `leviathan_ui` que falla al importar y valida el JSON).
- **Commit:** `7f708bb`.
- **Fecha de resolución:** 2026-11-21.

## R-9f2b64d1 — Los avisos auxiliares rompían el JSON de `--inspect`/`--shell-info`

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Descripción:** en modo JSON, `--inspect-extract` añadía
  `[OK] Recursos de cabecera exportados: …` a stdout después del documento, y
  `--shell-preview` añadía `[OK] Vista previa exportada: …` o
  `[INFO] El paquete no tiene icono exportable …`. Las dos combinaciones
  producían una salida que `json.loads(stdout)` no podía leer, aunque el
  comando terminara con código 0.
- **Pasos para reproducir:** `python packagemaker.py --inspect demo.iflapp --inspect-json --inspect-extract out`
  o `python packagemaker.py --shell-info demo.iflapp --shell-info-json --shell-preview preview`.
- **Estado:** Resuelto.
- **Prioridad:** Media (fallo silencioso para el consumidor; el artefacto y la
  exportación sí se generan).
- **Solución aplicada:** ambos avisos se escriben en `stderr` cuando la salida
  es JSON y en `stdout` en modo humano; el JSON de stdout no cambia.
- **Pruebas:** `tests/test_maintenance_cli_regressions.py::JsonPurityWithAuxiliaryOutputTests`
  (2 casos).
- **Commit:** `7f708bb`.
- **Fecha de resolución:** 2026-11-21.

## R-6e04c8ab — El aviso de MoonFix con `details.xml` corrupto abortaba en cp1252

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Descripción:** cuando `moonfix` no podía leer `details.xml`, avisaba con
  `print(f"⚠ Advertencia: …")` en stdout. En consolas Windows `cp1252` el
  símbolo `⚠` no es representable y el `print` lanzaba `UnicodeEncodeError`,
  abortando la reparación con traceback en lugar de continuar con los metadatos
  de la línea de comandos. Es la misma clase de fallo que R-739d5fec, que ya se
  había corregido en otras rutas.
- **Pasos para reproducir:** con `details.xml` truncado y stdout en `cp1252`,
  ejecutar `python packagemaker.py moonfix --name Demo --shortname demo --publisher Influent`.
- **Estado:** Resuelto.
- **Prioridad:** Media (aborta una reparación que debería degradar con aviso).
- **Solución aplicada:** el aviso usa `_safe_print` y se escribe en `stderr`.
  El flujo de reparación y el fallback a los metadatos del CLI no cambian.
- **Pruebas:** `tests/test_maintenance_cli_regressions.py::MoonfixEncodingWarningTests`
  (stdout/stderr reales en `cp1252`).
- **Commit:** `7f708bb`.
- **Fecha de resolución:** 2026-11-21.

## R-7d5b91c4 — MoonFix regeneraba la marca temporal y rompía la ley canónica

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Descripción:** `repair_project_from_templates()` regeneraba `details.xml` con
  una marca temporal nueva (`ProjectNameFormatter.get_timestamp()`) porque
  ninguno de sus llamadores pasaba `timestamp`. El nombre de carpeta no cambia
  durante la reparación, así que, tras ejecutar `moonfix`, la carpeta
  `influent.demo.v1.0-26.11-10.05-Danenone` contenía un `details.xml` con
  `<version>v1.0-26.11-10.06</version>`. Carpeta y metadatos dejaban de
  compartir timestamp, en contra de la ley de nombres canónicos, y cada
  reparación volvía a mover la marca. Además, el artefacto compilado tomaba la
  identidad de la carpeta mientras `details.xml` declaraba otra distinta.
- **Pasos para reproducir:** crear un proyecto canónico, ejecutar
  `python packagemaker.py moonfix --name "Mi App" --shortname mi-app --publisher Influent`
  y comparar el sufijo de la carpeta con `<version>` en `details.xml`.
- **Estado:** Resuelto.
- **Prioridad:** Media (no impide compilar, pero corrompe la identidad canónica
  del proyecto en cada reparación).
- **Causa raíz:** `repair_project_from_templates()` llamaba a `build_variables()`
  sin `timestamp`; `build_variables()` genera uno nuevo cuando no lo recibe.
  Los tres llamadores (CLI, diálogo de MoonFix y wizard) solo conservaban la
  versión base, nunca la marca temporal.
- **Solución aplicada:** `repair_project_from_templates()` acepta `timestamp` y,
  si no se le pasa, recupera el existente con `_existing_timestamp()`: primero
  del nombre canónico de la carpeta (`parse_project_folder`) y, si la carpeta no
  es canónica, de `<version>` en `details.xml`. Solo genera una marca nueva si
  el proyecto no tiene ninguna. El arreglo es central, así que cubre la CLI, la
  GUI y `moonFixWizard` sin cambiar sus flujos.
- **Pruebas:** `tests/test_maintenance_cli_regressions.py::MoonFixPreservesCanonicalTimestampTests`
  (3 casos: carpeta canónica, carpeta legacy con `details.xml` y ruta real del
  CLI; los 3 fallan con el comportamiento anterior).
- **Commit:** `c36df67`.
- **Fecha de resolución:** 2026-11-21.

## R-3f9a2c71 — El dropper lanzaba `updater.py` en los builds zipapp

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Descripción:** con `--compiler zipapp` (el backend de reserva, único siempre
  disponible) el paquete contiene `<guion>.pyz`, no `<guion>`. El stub del
  dropper solo probaba `<guion>`, `<guion>.exe` y `<guion>.py`; al no
  encontrarlos, el respaldo lanzaba el primer `.py` de la raíz del paquete, que
  es `updater.py`. El `.run` abría el actualizador y quedaba esperando en vez de
  arrancar la aplicación.
- **Pasos para reproducir:** crear un proyecto y ejecutar
  `python packagemaker.py --buildthis <proyecto> --output <dir> --platform Linux --compiler zipapp --no-sandbox --dropper`;
  después ejecutar el `.run` generado y comprobar que no aparece la salida de la
  aplicación (`Hola desde demo!`) y que el proceso no termina.
- **Estado:** Resuelto.
- **Prioridad:** Media (el `.iflapp` es correcto; solo el `.run` no arranca la
  aplicación, pero afecta a quien depende de zipapp).
- **Causa raíz:** `_launch()` del stub no consideraba `.pyz` entre los puntos de
  entrada y el respaldo elegía cualquier `.py` de la raíz, incluido el
  actualizador auxiliar.
- **Solución aplicada:** los candidatos incluyen `<app>.pyz` y `<stem>.pyz`, y
  `.py`/`.pyz` se ejecutan con `sys.executable`. El respaldo prueba primero los
  `.pyz`, después los `.py` y deja los ejecutables nativos al final.
- **Pruebas:** `tests/test_iflapp_dropper_sandbox.py::DropperTests::test_dropper_launches_zipapp_entrypoint`
  (con el código anterior imprime `wrong-entrypoint`; con la corrección ejecuta
  `demo.pyz`).
- **Commit:** `325c0e9`.
- **Fecha de resolución:** 2026-11-21.

## R-7b1d4e92 — `--inspect` aceptaba cabeceras truncadas como paquete válido

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Descripción:** `read_iflapp_header()` no comprobaba que la cabecera declarada
  cupiera en el archivo. Un `.iflapp` cortado justo después de la longitud
  declarada se inspeccionaba con código 0 y un JSON aparentemente válido
  (`format_version: 0`, identidad vacía), así que una descarga incompleta
  parecía un paquete legítimo. Si faltaban los cuatro bytes de longitud, el
  error era `struct.error`; un JSON que no fuera objeto producía
  `AttributeError` y metadatos de sección no numéricos, `ValueError`.
- **Pasos para reproducir:** escribir `IFLAPP2\0` + longitud 1000 + `{}` en un
  archivo y ejecutar `python packagemaker.py --inspect <archivo> --inspect-json`;
  terminaba con código 0 y una cabecera vacía.
- **Estado:** Resuelto.
- **Prioridad:** Baja (no corrompe nada; oculta un paquete truncado y da un
  diagnóstico engañoso).
- **Solución aplicada:** `read_iflapp_header()` valida los cuatro bytes de
  longitud, que el blob leído mida exactamente lo declarado, que el JSON sea un
  objeto y que la cabecera de cola también esté completa. `_read_section()`
  valida el tipo de `sections`, los metadatos numéricos y que la sección no
  exceda el archivo. Todos los casos producen `IflappError` legible.
- **Pruebas:** `tests/test_iflapp_format.py::TruncatedContainerTests` (5 casos;
  los 5 fallan con el código anterior).
- **Commit:** `850de5c`.
- **Fecha de resolución:** 2026-11-21.

---

## R-8a4f1c6d — Cabeceras con tipos inesperados rompían `--inspect`

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Descripción:** `read_iflapp_header()` comprobaba que la cabecera fuera un
  objeto JSON, pero no los tipos de sus campos. Un `manifest` que no fuera lista
  lanzaba `TypeError: 'int' object is not iterable`; un `payload` que no fuera
  objeto lanzaba `AttributeError` en `compression`/`encryption`/`file_count`; un
  `file_count` no numérico lanzaba `ValueError`; `sections` con una sección que
  no fuera objeto rompía `export_header_assets()` con `AttributeError`; y un
  offset negativo terminaba en `OSError [Errno 22]`. `--inspect`,
  `--inspect-json` y `--inspect-extract` morían con traceback en lugar de dar un
  diagnóstico de formato.
- **Pasos para reproducir:** escribir `IFLAPP2\0` + longitud 4096 +
  `{"format_version": 2, "manifest": 5}` y ejecutar
  `python packagemaker.py --inspect <archivo> --inspect-json`; terminaba con
  `TypeError` y traceback.
- **Estado:** Resuelto.
- **Prioridad:** Baja (no corrompe nada; un paquete dañado o manipulado provoca
  un traceback en vez de un error legible).
- **Solución aplicada:** `_validate_header_shape()` valida los tipos de
  `format_version`, `sections`, `payload`, `manifest` y de los metadatos
  numéricos. `_read_section()` y `_payload_bounds()` rechazan offsets y tamaños
  negativos o fuera del archivo. Las propiedades de `IflappHeader` y
  `export_header_assets()` toleran formas inesperadas. Todos los casos producen
  `IflappError` con un mensaje legible.
- **Pruebas:** `tests/test_iflapp_format.py::MalformedHeaderShapeTests` (7 casos;
  los 7 fallan con el código anterior).
- **Commit:** `f60f9ac`.
- **Fecha de resolución:** 2026-11-21.

---

## R-1c93e4b7 — El editor trataba módulos de la biblioteca estándar como dependencias de PyPI

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Descripción:** `lib/dependency_manager.py` decide qué imports externos
  necesita el proyecto del editor con una lista fija de módulos estándar.
  Esa lista omite módulos como `hmac`, `asyncio`, `ctypes`, `email`, `decimal`,
  `tomllib`, `sysconfig`, `operator`, `shlex`, `signal` o `zoneinfo`, así que un
  script que los importe hace que el editor escriba `hmac`, `email`, etc. en
  `requirements.txt` e intente `pip install` de paquetes que no existen.
- **Pasos para reproducir:** en el editor, abrir un script con
  `import hmac` + `import requests` y ejecutar «Verificar dependencias»;
  `requirements.txt` termina con `hmac` y `requests`, y la instalación de
  `hmac` falla.
- **Estado:** Resuelto.
- **Prioridad:** Media (falso positivo en todos los proyectos que usan stdlib
  moderna; ensucia `requirements.txt` y muestra errores de instalación).
- **Solución aplicada:** `_STDLIB_MODULES` une la lista histórica con
  `sys.stdlib_module_names` (autoridad desde Python 3.10). La lista antigua se
  conserva como respaldo para intérpretes anteriores.
- **Pruebas:** `tests/test_dependency_manager_stdlib.py` (6 casos; los de
  detección fallan con el código anterior).
- **Commit:** `64c083a`.
- **Fecha de resolución:** 2026-11-21.

---

## R-4d7b2e91 — `updater.py` abortaba sin `leviathan_ui`

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Descripción:** el updater se copia a todos los proyectos empaquetados y se
  usa en modo headless (`--version`, `--check`, `--install`), pero importaba
  `leviathan_ui` de forma incondicional en la cabecera. En una máquina sin esa
  dependencia opcional (CI, Linux mínimo, proyecto recién creado) terminaba con
  `ModuleNotFoundError` antes de leer los argumentos, así que ni siquiera
  `updater.py --version` funcionaba. `get_accent_color()` tenía el mismo
  problema.
- **Pasos para reproducir:** con un `leviathan_ui` que no se puede importar,
  `python updater.py --version` termina con traceback y código 1.
- **Estado:** Resuelto.
- **Prioridad:** Alta (el actualizador queda inutilizable sin la dependencia
  opcional, incluidos los flujos headless).
- **Solución aplicada:** `WipeWindow` tiene un respaldo no-op en el
  `except ImportError` (mismo patrón que `packagemaker.py` y
  `lib/window_chrome.py`), se expone `LEVIATHAN_AVAILABLE` y
  `get_accent_color()` cae a `#0078D4` cuando el import falla.
- **Pruebas:** `tests/test_updater_optional_dependencies.py` (3 casos; los 3
  fallan con el código anterior).
- **Commit:** `64c083a`.
- **Fecha de resolución:** 2026-11-21.

---

## R-6b1f8d20 — `--force-fonts` se ignoraba y abría la TUI

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Descripción:** el flag está documentado como «forzar la redescarga aunque
  estén en caché», pero `get_action()` solo lo leía dentro de la rama de
  `--download-fonts`. Usado solo, ninguna acción coincidía y el flujo principal
  abría la TUI (o la GUI), sin descargar nada. En un script o en CI quedaba
  esperando entrada.
- **Pasos para reproducir:** `python packagemaker.py --force-fonts` con
  `stdin` cerrado: arranca la TUI en lugar de descargar las fuentes.
- **Estado:** Resuelto.
- **Prioridad:** Media (opción documentada sin efecto y arranque inesperado de
  la interfaz).
- **Solución aplicada:** `get_action()` trata `--force-fonts` como
  `--download-fonts all` con `force=True`; combinado con
  `--download-fonts <claves>` conserva las claves indicadas.
- **Pruebas:** `tests/test_cli_font_flags.py` (3 casos; el de `--force-fonts`
  solo falla con el código anterior).
- **Commit:** `64c083a`.
- **Fecha de resolución:** 2026-11-21.

---

## R-9e2a5c73 — `--app-version` reportaba una versión fija

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Descripción:** el entrypoint intentaba `from version import VERSION`, módulo
  que no existe en el repositorio, y caía en `version = "3.2.7"`. El comando
  ignoraba la versión canónica de `details.xml` y quedaría obsoleto tras
  cualquier release, justo cuando se usa para verificar el número de versión.
  Además, `show_version` (rama muerta porque `main()` intercepta el flag)
  imprimía `v` + `__version__` y producía `vv3.2.7-…`.
- **Pasos para reproducir:** `python packagemaker.py --app-version` imprime
  `Influent Package Maker v3.2.7` aunque `details.xml` declare
  `v3.2.7-26.05-20.13`.
- **Estado:** Resuelto.
- **Prioridad:** Media (información de versión incorrecta; afecta a la
  verificación previa al release).
- **Solución aplicada:** ambos caminos leen `lib.cliHandler.__version__`
  (derivada de `details.xml`), normalizan el prefijo `v` y usan
  «desconocida» si falta el dato. El formato de salida sigue siendo
  `Influent Package Maker v<versión>`.
- **Pruebas:** `tests/test_cli_version_reporting.py` (2 casos).
- **Commit:** `64c083a`.
- **Fecha de resolución:** 2026-11-21.

---

## R-2a7f6b41 — La plataforma de la cabecera no coincidía con el `details.xml` empaquetado

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Descripción:** `create_package()` reescribe `<platform>` en el
  `details.xml` del paquete con la plataforma objetivo, pero la cabecera
  `.iflapp` recibía `self.metadata`, que conserva la plataforma declarada del
  proyecto. Al compilar un proyecto `AlphaCube` en Linux, `--inspect` mostraba
  `Plataforma: AlphaCube` y, en el mismo contenedor, un `details.xml` con
  `Danenone`.
- **Pasos para reproducir:** crear un proyecto con `--platform all`, compilar
  con `--compiler zipapp` en Linux y ejecutar
  `python packagemaker.py --inspect <artefacto>`.
- **Estado:** Resuelto.
- **Prioridad:** Baja (metadatos contradictorios; no impide abrir ni verificar).
- **Solución aplicada:** `package_identity()` alinea la identidad de la
  cabecera con el `<platform>` del `details.xml` que se empaqueta; si el XML
  falta, está corrupto o no declara plataforma, se conservan los metadatos.
- **Pruebas:** `tests/test_package_identity_platform.py` (4 casos).
- **Commit:** `64c083a`.
- **Fecha de resolución:** 2026-11-21.

## R-6f2b9d31 — `--harden obfuscate` generaba Python inválido

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Descripción:** `obfuscate_strings()` localizaba los literales con una
  expresión regular que sustituía cada cadena por una llamada a
  `b64decode()`. Con literales concatenados de forma implícita
  (`("parte uno " "parte dos")`) la sustitución producía
  `(...) (...)`, un `SyntaxError`; el blindaje informaba `OK` y el build
  terminaba bien, pero el `updater.py` empaquetado ya no se podía ejecutar.
  Además, el patrón también reescribía texto entre comillas que vivía dentro
  de un docstring o de un f-string, alterando su contenido sin avisar.
- **Pasos para reproducir:** empaquetar un proyecto cuyo `updater.py` (o
  cualquier `.py` del paquete) use concatenación implícita de cadenas y
  compilar con `--compiler zipapp --harden obfuscate`; extraer el `.iflapp` y
  ejecutar `python -m py_compile updater.py`.
- **Estado:** Resuelto.
- **Prioridad:** Alta (el artefacto publicado queda inservible sin que el build
  falle).
- **Solución aplicada:** `obfuscate_strings()` analiza el fuente con `ast` y
  sustituye únicamente los `ast.Constant` de texto que son expresiones
  completas. Se omiten docstrings, partes literales de f-strings, patrones de
  `match` y valores de `Literal`/`Annotated`. Un fuente no analizable devuelve
  `applied=False` sin modificar el archivo. La concatenación implícita se
  reemplaza como un único literal, conservando el valor.
- **Pruebas:** `tests/test_hardening.py::ObfuscateRobustnessTests` (3 casos:
  validez y equivalencia de salida, omisión de docstrings/f-strings/patrones y
  rechazo de fuentes no analizables).
- **Commit:** `f8fe305`.
- **Fecha de resolución:** 2026-11-21.

## R-8c4e1a72 — Los contenedores de motor lanzaban excepciones crudas con cabeceras corruptas

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Descripción:** `BuildEngine.read_header()` y
  `blindcubeEngine.read_header()` desestructuraban longitudes sin comprobar
  que la cabecera cupiera en el archivo: un contenedor cortado lanzaba
  `struct.error`; un JSON que no fuera objeto terminaba en `TypeError`; un
  payload LZMA corrupto o unos parámetros de cifrado incompletos salían como
  `LZMAError`/`KeyError`. `flatcubeEngine.unpack()` devolvía `BadZipFile`,
  `JSONDecodeError` o un manifiesto que no era diccionario.
- **Pasos para reproducir:** `blindcubeEngine.read_header(blindcubeEngine.MAGIC)`,
  `blindcubeEngine.unpack(build_header(...) + b"no-es-lzma")` o
  `flatcubeEngine.unpack(b"PK\x03\x04" + bytes(12))`.
- **Estado:** Resuelto.
- **Prioridad:** Media (solo afecta a contenedores dañados o manipulados; el
  formato válido no cambia).
- **Solución aplicada:** los tres lectores validan longitud mínima, tamaño
  declarado, decodificación UTF-8 y que el JSON sea un objeto, y traducen
  `LZMAError`, `KeyError`/`ValueError` de cifrado, `BadZipFile` y errores de
  manifiesto a `EngineError`/`BlindCubeError`/`FlatCubeError` legibles.
- **Pruebas:** `tests/test_engines_and_platform.py::MalformedEngineContainerTests`
  (9 casos).
- **Commit:** `f8fe305`.
- **Fecha de resolución:** 2026-11-21.

---

## R-1f4a7c92 — Un `pm.data` o `settings.json` con forma no-objeto impedía arrancar

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Descripción:** `PMDataStore.load()` solo capturaba `JSONDecodeError` y
  `OSError`. Un `data/pm.data` que seguía siendo JSON válido pero no un objeto
  (`[]`, `"texto"`, `42`, `null`) llegaba a `_ensure_structure()` y lanzaba
  `TypeError: list indices must be integers or slices, not str`; lo mismo
  ocurría si `user`, `readonly` o `translation_cache` tenían otro tipo. Como
  `packagemaker.py` construye `APP_CONFIG = load_app_config()` al importarse,
  la aplicación no arrancaba ni en GUI ni en CLI (`--app-version`,
  `--list-compilers`, builds). Un `config/settings.json` con forma de lista
  también abortaba la migración con `AttributeError: 'list' object has no
  attribute 'get'`.
- **Pasos para reproducir:** escribir `[]` en `data/pm.data` y ejecutar
  `python packagemaker.py --app-version`; o dejar `config/settings.json` con
  `[1, 2, 3]` y arrancar la aplicación.
- **Estado:** Resuelto.
- **Prioridad:** Alta (bloquea por completo el arranque).
- **Solución aplicada:** `load()` descarta un documento que no sea diccionario;
  `_ensure_structure()` reconstruye cualquier sección (`user`, `readonly`,
  `translation_cache`) que no sea un objeto conservando las claves válidas de
  las demás. Los accesores y `migrate_from_legacy_config()` validan el tipo
  antes de operar, y `load_merged_app_config()` ignora un `settings.json` que
  no sea un objeto. No se borran preferencias válidas.
- **Pruebas:** `tests/test_pm_data_reset.py::PMDataCorruptionTests` (5 casos).
- **Commit:** `543e173`.
- **Fecha de resolución:** 2026-11-21.

---

## R-2b6d8e13 — Las cabeceras `.asksome` malformadas rompían `--shell-info` y la verificación

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Descripción:** `read_asksome_header()` devolvía el JSON sin comprobar su
  forma ni que el tamaño declarado cupiera en el archivo. Una cabecera `[]`
  hacía que `verify_asksome()`, `extract_asksome()`, `package_info()` y
  `icon_bytes()` fallaran con `AttributeError: 'list' object has no attribute
  'get'`; `metadata` como lista rompía `dict(...)` con `TypeError`; `manifest`
  no lista rompía `len(...)`; un `icon` no textual o base64 inválido abortaba
  el hover del shell; y una cabecera truncada se aceptaba como válida.
- **Pasos para reproducir:** `verify_asksome()` o
  `python packagemaker.py --shell-info archivo.asksome` sobre un contenedor con
  cabecera `[]`, `{"metadata": []}` o un tamaño declarado mayor que el archivo.
- **Estado:** Resuelto.
- **Prioridad:** Media (solo afecta a artefactos dañados o manipulados; el
  formato válido no cambia).
- **Solución aplicada:** un único `_read_container()` valida el tamaño
  declarado, decodifica el JSON y exige un objeto; `_validate_header()`
  comprueba los tipos de `metadata`, `manifest`, `encryption_params`,
  `format_version` y de los campos textuales. `verify_asksome()` y
  `extract_asksome()` comparten la lectura validada. `native_shell` decodifica
  el icono con un helper que devuelve `None` ante base64 inválido.
- **Pruebas:** `tests/test_mexf_asksome.py::TestAsksomeMalformedHeaderTests`
  (13 casos) y `tests/test_native_shell.py::test_package_info_rejects_malformed_header`,
  `test_invalid_base64_icon_does_not_break_shell_info`.
- **Commit:** `543e173`.
- **Fecha de resolución:** 2026-11-21.

---

## R-3c9e1a57 — La extracción `.asksome` aceptaba rutas de unidad y exponía errores crudos

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Descripción:** `_safe_member()` solo rechazaba rutas POSIX absolutas y
  `..`; una entrada `C:/Windows/...` o `C:archivo` pasaba la validación y en
  Windows `Path(destino) / "C:/..."` resuelve fuera del destino (escritura
  arbitraria durante `--install-asksome`). Además, un payload LZMA/TAR
  corrupto salía como `lzma.LZMAError`/`tarfile.ReadError` en lugar de un
  `AsksomeError` legible. La clave de firma `.asksome` es local y pública, así
  que un artefacto de terceros puede estar manipulado.
- **Pasos para reproducir:** instalar un `.asksome` cuyo TAR contenga
  `C:/Windows/evil.txt`, o extraer uno con payload LZMA corrupto.
- **Estado:** Resuelto.
- **Prioridad:** Media (seguridad y robustez; no afecta a artefactos válidos).
- **Solución aplicada:** `_safe_member_target()` rechaza rutas absolutas,
  unidades de Windows, componentes `..`, nombres vacíos y cualquier resolución
  que escape del destino, igual que `lib/iflapp_format.py`; `extract_asksome()`
  comprueba también symlinks preexistentes y traduce `LZMAError`/`EOFError` y
  `TarError` a `AsksomeError`.
- **Pruebas:** `tests/test_mexf_asksome.py::TestAsksomeMalformedHeaderTests::test_unsafe_member_paths_are_rejected`
  (5 rutas) y `test_corrupt_payload_raises_asksome_error`.
- **Commit:** `543e173`.
- **Fecha de resolución:** 2026-11-21.

---

## R-5f8c2d91 — Los errores de `--inspect`/`--shell-info` contaminaban la salida JSON

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Descripción:** con `--inspect-json` y `--shell-info-json` el documento JSON
  se imprime en stdout, pero las rutas de error (`[ERROR] No se pudo leer la
  cabecera…`, `[ERROR] No existe el archivo…`) seguían yendo a stdout. Un
  consumidor que hiciera `json.loads(stdout)` recibía
  `JSONDecodeError: Expecting value: line 1 column 1`. Es la misma clase de bug
  que R-4b7e91a2 y R-9f2b64d1, que solo cubrieron los avisos auxiliares.
- **Pasos para reproducir:** `python packagemaker.py --inspect /noexiste.iflapp --inspect-json | python -m json.tool`.
- **Estado:** Resuelto.
- **Prioridad:** Media (rompe automatización; la salida humana no cambia).
- **Solución aplicada:** las cuatro acciones con salida JSON
  (`PackageInspectHelper.inspect`, `NativeShellHelper.info`,
  `MexfShellHelper.plan`/`_install_or_remove` e `IflappIdeHelper.scan`) eligen
  el flujo de los errores según su bandera (`json`/`as_json`): a `stderr` en
  modo JSON y a `stdout` en modo texto.
- **Pruebas:** `tests/test_cli_json_stream_purity.py` (6 casos: stdout vacío al
  fallar en las cuatro acciones y documento parseable en el camino feliz).
- **Commit:** `78f9c28`.
- **Fecha de resolución:** 2026-11-21.

## R-7e3a9c14 — Los accesos directos `.desktop` no citaban rutas con espacios

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** `_write_linux_desktop()` escribía
  `Exec={sys.executable} {launcher}` sin comillas. Si la carpeta de instalación
  (`--install-root`) o el home contienen espacios (`/home/ana/My Apps/...`), el
  lanzador parte la ruta en varios argumentos e intenta ejecutar una ruta
  truncada, así que la aplicación instalada no abre desde el menú.
  `create_desktop_file()` de `lib/linux_icon_handler.py` tenía el mismo defecto.
  Además, `Name` y `Comment` copiaban el nombre sin aplanar, de modo que un
  `name` con saltos de línea inyectaba claves nuevas en el `.desktop`.
- **Pasos para reproducir:** instalar un `.asksome` con
  `--install-root "/tmp/Mis Apps"` y revisar la línea `Exec` del `.desktop`
  generado (sin comillas) o abrir el acceso desde el menú (no arranca).
- **Estado:** Resuelto.
- **Prioridad:** Alta (el acceso directo queda inservible en rutas con espacios).
- **Solución aplicada:** `_desktop_exec_quote()` cita cada argumento del campo
  `Exec` y escapa `\`, `"`, backtick, `$` y los códigos de campo (`%` → `%%`);
  `_desktop_text()` aplana nombre y comentario. `linux_icon_handler` usa el
  mismo citado.
- **Pruebas:** `tests/test_mexf_asksome.py::test_linux_desktop_quotes_exec_arguments_with_spaces`,
  `::test_linux_desktop_name_cannot_inject_new_keys` y
  `::test_desktop_exec_quote_escapes_field_codes`.
- **Commit:** `6fa3c51`.
- **Fecha de resolución:** 2026-11-22.

## R-4b8d2f61 — Un `install.json` corrupto rompía `--build-removeme`

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** `read_record()` hacía `json.loads()` y
  `InstallRecord(**data)` sin validar. Un `install.json` truncado lanzaba
  `JSONDecodeError`; un documento que no era objeto o al que le faltaban campos
  lanzaba `TypeError`. `--build-removeme` solo captura `AsksomeInstallError`,
  así que ambos casos terminaban en un traceback.
- **Pasos para reproducir:** escribir `{bad` en
  `<install_root>/<app_id>/install.json` y ejecutar
  `--build-removeme <app_id> --install-root <install_root>`.
- **Estado:** Resuelto.
- **Prioridad:** Media (robustez del CLI; no afecta a instalaciones sanas).
- **Solución aplicada:** `read_record()` valida la lectura y la forma del
  documento y traduce los fallos a `AsksomeInstallError` con un mensaje
  legible, que el CLI ya muestra como `[ERROR]` con código 1.
- **Pruebas:** `tests/test_mexf_asksome.py::test_read_record_rejects_corrupt_and_incomplete`
  y `::test_build_removeme_reports_corrupt_record`.
- **Commit:** `6fa3c51`.
- **Fecha de resolución:** 2026-11-22.

## R-9c5f1e28 — Un `.mexf` legacy con tipos inesperados rompía `--shell-plan`

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** los documentos JSON legacy se convertían sin validar sus
  tipos. `shell_commands` como entero lanzaba `TypeError` al iterarlo; una
  sección `extensions`/`context_menus` no iterable, `environments` que no fuera
  objeto o `shortcuts` que no fuera diccionario rompían igualmente
  `--shell-plan` con `TypeError`/`AttributeError`/`ValueError`.
- **Pasos para reproducir:** crear un `.mexf` con
  `{"extensions": 3, "shell_commands": 5, "context_menus": "x"}` y ejecutar
  `--shell-plan <archivo>`.
- **Estado:** Resuelto.
- **Prioridad:** Media (robustez del CLI ante documentos antiguos dañados).
- **Solución aplicada:** `_legacy_to_v1()` normaliza las secciones a lista o
  diccionario y convierte los metadatos a texto; `plan_from_document()` usa
  `_as_list()`/`_as_dict()` para no confiar en el tipo de ninguna sección.
- **Pruebas:** `tests/test_mexf_asksome.py::test_legacy_mexf_with_wrong_section_types_is_normalized`.
- **Commit:** `6fa3c51`.
- **Fecha de resolución:** 2026-11-22.

## R-4a1e7b93 — La limpieza del build se rendía ante el primer `WinError 32`

- **Usuario:** JesusQuijada34 (auditoría de la Fase 1.2 de `bugs.txt`; sin issue externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** `lib/file_ops.py` ya reintentaba ante bloqueos, pero
  `BuildThread` seguía llamando a `shutil.rmtree` crudo en los cuatro puntos
  donde el bloqueo es más probable: la limpieza de `dist/` y `build/`, los
  restos de Nuitka (`*.build`, `*.onefile-build`, `*.dist`, `*.build-cache`), la
  carpeta temporal del paquete tras crear el `.iflapp` y el borrado autorizado
  del proyecto fuente. En Windows los procesos hijos pueden mantener el binario
  abierto al terminar, así que el primer intento fallaba y quedaba basura en el
  proyecto (o el paquete sin recoger) sin reintento.
- **Pasos para reproducir:** compilar en Windows con un antivirus que retenga
  el `.exe` recién creado y observar el `[WARN]` de carpeta no eliminada.
- **Estado:** Resuelto.
- **Prioridad:** Alta (deja artefactos y rompe el contrato de "sólo queda el `.iflapp`").
- **Solución aplicada:** los cuatro puntos usan `remove_tree`, que reintenta con
  espera creciente y limpia el bit de sólo lectura. Nueva clave
  `build_log.folder_locked` en los 12 idiomas para explicar el motivo.
- **Pruebas:** `tests/test_engine_isolation.py::test_build_thread_cleanup_uses_retrying_removal`
  (los tres métodos no vuelven a llamar a `shutil.rmtree`), más el test
  existente que simula dos pasadas bloqueadas.
- **Fecha de resolución:** 2026-11-22.

## R-8d2c5f60 — `blindcubeEngine` importaba `ProjectNameFormatter` de otro motor

- **Usuario:** JesusQuijada34 (auditoría de la Fase 2.1 de `bugs.txt`; sin issue externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** al agrupar los módulos por motor, `build_validation.py` quedó
  dentro de `blindcubeEngine` pero seguía importando
  `lib.makeselfEngine.naming.ProjectNameFormatter` en la cabecera. El motor
  BlindCube dependía así de otro motor, contra el aislamiento que pide la Fase
  2.1; empaquetar o sustituir un motor arrastraba el otro.
- **Pasos para reproducir:** `python -c "import lib.blindcubeEngine.build_validation"`
  con `makeselfEngine` eliminado del árbol.
- **Estado:** Resuelto.
- **Prioridad:** Media (deuda de arquitectura; no rompía la ejecución normal).
- **Solución aplicada:** se usa la fachada transversal
  `lib.projectNameFormatter`, que reexporta la autoridad de la ley de nombres.
- **Pruebas:** `tests/test_engine_packages_layout.py::test_engines_do_not_couple_to_other_engines_at_import_time`
  (parametrizado por motor; permite las dependencias perezosas del registro de
  compiladores).
- **Fecha de resolución:** 2026-11-22.

---

## R-5b1e9d47 — El asistente de proyecto avisaba con `QMessageBox` secos

- **Usuario:** JesusQuijada34 (auditoría de la Fase 3.3 de `bugs.txt`; sin issue externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** la Fase 3.3 pide sustituir las alertas rudimentarias por
  notificaciones con transiciones y animaciones. `NewProjectWizard` seguía
  usando cuatro `QMessageBox` (campos vacíos, nombre no canónico, carpeta
  existente y fallo de plantillas), de modo que crear un proyecto desde el
  dashboard rompía el lenguaje visual del resto de la app.
- **Pasos para reproducir:** abrir el dashboard, pulsar «Crear» sin rellenar
  editorial/ID/nombre y observar el diálogo modal del sistema.
- **Estado:** Resuelto.
- **Prioridad:** Baja (cosmética; la validación era correcta).
- **Solución aplicada:** `NewProjectWizard._notify()` envía la notificación
  animada (`warning`/`error` de `lib.notificationSystem`) y, si el manager no
  puede construirse, cae al `QMessageBox` de siempre para no perder el aviso.
  El texto del fallo de plantillas pasa a la clave i18n
  `dashboard.create_failed`, traducida en los 14 idiomas.
- **Pruebas:** `tests/test_dashboard_notifications.py` (5 casos: tres rutas de
  error, el aviso de carpeta existente y el respaldo cuando la notificación
  falla).
- **Fecha de resolución:** 2026-11-22.

---

## R-9b4e7a52 — `.mexf` v1 con secciones mal tipadas rompía `--compile-mexf` y `--debug-mexf`

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** `validate_mexf()` solo comprobaba `triggers`, `commands` y
  `assets`. Un documento v1 con `shortcuts`/`environments` no-objeto o
  `file_associations`/`context_menus`/`registry`/`runtime` no-lista pasaba la
  validación y reventaba después: `merge_documents()` hacía `dict(valor)` o
  `list(valor)` y `MexfDebugger.__init__()` llamaba `.items()` sobre
  `environments`.
- **Pasos para reproducir:** un `.mexf` con `shortcuts: 5` y
  `python packagemaker.py --compile-mexf <carpeta>` terminaba en
  `TypeError: 'int' object is not iterable`; con `environments: [A, B]` y
  `--debug-mexf` terminaba en `AttributeError: 'list' object has no attribute 'items'`.
- **Estado:** Resuelto.
- **Prioridad:** Alta (el CLI abortaba con traceback en vez de dar un error legible).
- **Solución aplicada:** `validate_mexf()` valida la forma de `file_associations`,
  `context_menus`, `registry`, `shortcuts`, `environments` y `runtime`;
  `merge_documents()` normaliza cada sección con `isinstance`; `load_commands()`
  y `MexfDebugger` ignoran metadatos, entorno, `args`, `env` y `cwd` con tipos
  inesperados.
- **Pruebas:** `tests/test_mexf_asksome.py::test_wrong_typed_sections_are_rejected`
  (6 casos), `::test_merge_documents_normalizes_unexpected_sections` y
  `tests/test_mexf_debugger.py::MalformedDocumentTests` (2 casos).
- **Commit:** `935da3c`.
- **Fecha de resolución:** 2026-11-22.

---

## R-2f7c8d31 — El identificador `.mexf` permitía escribir y borrar fuera del directorio de integración

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** `install_plan()`/`uninstall_plan()` y los renderizadores de
  `.desktop` usaban `plan.identifier` (tomado de `metadata.id`) como nombre de
  fichero sin sanear. Un `.mexf` con `id: "../../evil/demo"` escribía el XML
  MIME y los `.desktop` fuera de `share/applications` (incluso fuera del home con
  más `../`) y `--uninstall-mexf-shell` podía borrar archivos ajenos. Además,
  `Name`/`Exec`/`Icon` no aplanaban saltos de línea, de modo que un valor podía
  inyectar claves nuevas en el `.desktop`.
- **Pasos para reproducir:** `plan_from_document({"metadata": {"id": "../../evil/demo"}, ...})`
  + `install_plan(plan, base_dir=...)` escribía en `share/evil/demo.xml`; con el
  directorio `applications` creado, `uninstall_plan()` eliminaba
  `share/victim--txt.desktop` fuera de `applications`.
- **Estado:** Resuelto.
- **Prioridad:** Alta (escritura y borrado arbitrario inducidos por el documento).
- **Solución aplicada:** nuevo `_file_stem()` que conserva `[A-Za-z0-9._-]` y
  sustituye separadores, espacios y `..`; se usa en el XML MIME, los
  `.desktop`, los `servicemenus` y `environment.d` de instalación y desinstalación.
  `_flat_value()` aplana los saltos de línea de los valores `.desktop` y de
  `environment.d`. El identificador visible del plan no cambia. Efecto
  secundario: un identificador que ya usaba espacios u otros caracteres no
  seguros cambia de nombre de fichero, así que una desinstalación de la versión
  anterior no retira esos ficheros previos (reinstalar la integración los deja
  en su sitio).
- **Pruebas:** `tests/test_mexf_shell.py::test_install_plan_keeps_identifier_from_escaping_base`,
  `::test_uninstall_plan_does_not_remove_files_outside_base`,
  `::test_desktop_entries_flatten_values_that_would_inject_keys` y
  `::test_environment_d_flattens_values`.
- **Commit:** `935da3c`.
- **Fecha de resolución:** 2026-11-22.

---

## R-6a1d3c94 — Un `.mexf` no UTF-8 provocaba traceback en el CLI

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** `parse_mexf()` leía el documento con `utf-8-sig` sin capturar
  `UnicodeDecodeError`. Un `.mexf` binario o con otra codificación abortaba
  `--shell-plan`, `--compile-mexf` y `--debug-mexf` con un traceback de codecs.
- **Pasos para reproducir:** `printf '\xff\xfe\x00binario' > bad.mexf` y
  `python packagemaker.py --shell-plan bad.mexf`.
- **Estado:** Resuelto.
- **Prioridad:** Media (entrada inválida; el proceso no quedaba estable).
- **Solución aplicada:** `parse_mexf()` traduce `UnicodeDecodeError` a `MexfError`
  con mensaje legible y `detect_mexf_format()` devuelve `"unknown"` en vez de
  lanzar.
- **Pruebas:** `tests/test_mexf_asksome.py::test_binary_mexf_is_reported_without_traceback`.
- **Commit:** `935da3c`.
- **Fecha de resolución:** 2026-11-22.

---

## R-8e5b2f17 — `lib.native_shell --info` sin archivo lanzaba traceback

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** el entrypoint `python -m lib.native_shell --info` hacía
  `args[1]` sin comprobar la longitud (`IndexError`) y no capturaba el
  `ValueError`/`OSError` de `package_info()` para rutas desconocidas o
  ilegibles, así que el integrador del gestor de archivos recibía un traceback.
- **Pasos para reproducir:** `python -m lib.native_shell --info` y
  `python -m lib.native_shell --info archivo-no-paquete`.
- **Estado:** Resuelto.
- **Prioridad:** Baja (herramienta auxiliar, no afecta a la GUI).
- **Solución aplicada:** se valida el argumento (uso y código 2) y los errores
  de lectura se imprimen como `[ERROR] …` con código 1.
- **Pruebas:** `tests/test_native_shell.py::test_info_cli_without_argument_reports_usage`
  y `::test_info_cli_with_unknown_file_reports_error`.
- **Commit:** `935da3c`.
- **Fecha de resolución:** 2026-11-22.

---

## Mejoras pendientes de aprobación

Las cuatro propuestas de esta sección y los seis cambios de engine están
recogidos como preguntas `Q-001`…`Q-010` en `CONFIRM.MD`, el único canal de
aprobación válido (solo JesusQuijada34). Ninguna se implementa sin una casilla
`[x] SÍ` verificada por autoría.

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

### R-5d8e2a41 — Acentos en publisher e identificador de aplicación

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Estado:** Pendiente de aprobación explícita. No implementado.
- **Situación actual:** la ley de nombres solo admite `A-Za-z0-9` y guiones en
  publisher y appname. Un publisher como `Jesús` se rechaza (R-b3f71a6c ya
  evita el traceback y muestra un error legible, pero el proyecto no se puede
  crear ni compilar).
- **Solicitado:** admitir acentos transliterándolos (`Jesús` → `Jesus`) o
  permitiéndolos en el nombre canónico.
- **Motivo de la espera:** cambia la ley de nombres y los nombres de carpeta,
  paquete y artefacto; afecta a `_PROJECT_PATTERN`, a la compatibilidad con
  proyectos existentes y a los tests de la ley canónica.

### R-4c8e1f27 — El publisher pierde su capitalización al crear proyectos

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Estado:** Pendiente de aprobación explícita. No implementado.
- **Situación actual:** la ley de nombres exige que el publisher conserve la
  capitalización declarada (`Influent.packagemaker.v3.2.7-…`), y
  `ProjectNameFormatter` lo cumple. Sin embargo, los dos puntos de creación
  pasan el publisher ya en minúsculas: `handle_cli_action('create_project')` y
  `_ejecutarCreacionProyecto()` en `packagemaker.py` hacen
  `.strip().lower().replace(' ', '-')`. El resultado es una carpeta
  `influent.demox.…` y un `details.xml` con `<publisher>influent</publisher>`
  aunque el usuario escriba `Influent`.
- **Comportamiento solicitado:** conservar la capitalización del publisher en
  la carpeta, el paquete, el `.iflapp` y `details.xml`, como ya hace el
  formatter.
- **Efectos secundarios:** cambia el nombre de los proyectos nuevos
  (`influent.*` → `Influent.*`) y las rutas de build; los proyectos existentes
  siguen siendo válidos porque `parse_project_folder` no distingue mayúsculas
  en el publisher. Hay que revisar los tests que construyen carpetas con
  publisher en minúsculas y cualquier CI que espere la ruta histórica.
- **Archivos:** `lib/cliHandler.py`, `packagemaker.py`,
  `tests/test_maintenance_cli_regressions.py`, `tests/test_issue4_reports.py`.
- **Riesgo:** medio (no rompe artefactos, pero altera nombres visibles y rutas
  de compilación; requiere decisión del responsable).

### R-3e7d1c58 — `compile-only` no elimina el fuente original del paquete

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Estado:** Pendiente de aprobación explícita. No implementado.
- **Situación actual:** `hardening.compile_to_bytecode()` escribe el `.pyc`
  optimizado (O2) junto al `.py`, pero no retira el fuente. El paquete sigue
  conteniendo el `.py` legible, así que el método no cumple lo que promete su
  documentación («sin fuentes legibles»).
- **Comportamiento solicitado:** tras compilar, eliminar el `.py` del árbol del
  paquete (nunca del proyecto fuente) o registrar explícitamente que solo se
  añade el bytecode.
- **Efectos secundarios:** borrar archivos del paquete es destructivo; si el
  `.py` es el punto de entrada del backend zipapp, el artefacto deja de
  arrancar. Requiere verificar el tipo de backend y excluir los `.pyz`.
- **Archivos:** `lib/hardening.py`, `lib/BuildThread.py`,
  `tests/test_hardening.py`.
- **Riesgo:** medio (puede romper el arranque de paquetes que dependan del
  fuente; no se implementa sin aprobación).

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
- Último reporte externo conocido: issue #4 (2026-07-05). Los ciclos actuales
  solo añadieron correcciones de auditoría interna (commits `5aa823b`,
  `d2670a1`, el de R-b3f71a6c, `ab79f4a`, `7f708bb`, el de R-7d5b91c4,
  `325c0e9`, `850de5c`, `f60f9ac`, `543e173` y `6fa3c51`), no reportes de usuario; el
  contador de 7 días no se reinicia.
- Verificación del ciclo de R-9b4e7a52, R-2f7c8d31, R-6a1d3c94 y R-8e5b2f17
  (2026-11-22): `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 788
  pasan, 1 omitido, 39 subtests; `pyflakes` y `py_compile` limpios; los 16 casos
  nuevos fallan con el código anterior (comprobado con `git stash` de los
  módulos corregidos). `--compile-mexf` y `--debug-mexf` con `shortcuts: 5` o
  `environments: [A, B]` terminan en `[ERROR]` legible y código 1; un `.mexf`
  binario ya no lanza traceback; `install_plan()`/`uninstall_plan()` con
  `id: "../../evil/demo"` mantienen todas las rutas dentro de `base_dir` y no
  borran archivos externos; `python -m lib.native_shell --info` sin argumento
  devuelve uso (código 2) y con archivo desconocido `[ERROR]` (código 1).
- Aprobaciones (2026-11-22): se creó `CONFIRM.MD` con 10 preguntas pendientes
  (`Q-001`…`Q-010`: las 4 mejoras y los 6 cambios de engine). Ninguna está
  aprobada; no se aplicó ningún cambio de engine.
- Verificación del ciclo de R-7e3a9c14, R-4b8d2f61 y R-9c5f1e28 (2026-11-22):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 547 pasan, 1
  omitido, 39 subtests; `pyflakes` y `py_compile` limpios; los 6 casos nuevos
  fallan con el código anterior. Instalación real de un `.asksome` en
  `/tmp/pm e2e/My Installed Apps` con accesos en `My Shortcuts` genera un
  `.desktop` con `Exec="…" "…"` citado (antes la ruta con espacios quedaba sin
  comillas); `--build-removeme` sobre un `install.json` corrupto termina con
  `[ERROR]` y código 1 sin traceback; `--shell-plan` sobre un `.mexf` legacy
  con `extensions`/`shell_commands`/`context_menus` de tipo inesperado
  funciona sin traceback.
- Verificación del ciclo de R-3a7c5e18, R-9f2b64d1 y R-6e04c8ab (2026-11-21):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 474 pasan, 2
  omitidos; `pyflakes` y `py_compile` limpios; las cuatro acciones JSON
  (`--inspect-json`, `--shell-plan-json`, `--shell-info-json`,
  `--ide-scan-json`) emiten JSON parseable sin `leviathan_ui`, incluso con
  `--inspect-extract` y `--shell-preview`; `moonfix` con `details.xml`
  truncado y stdout en `cp1252` avisa en stderr y repara sin traceback; build
  real con `--compiler zipapp` genera el `.iflapp` y `--inspect` lo lee.
- Verificación del ciclo de R-7d5b91c4 (2026-11-21):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 477 pasan, 2
  omitidos; `pyflakes` y `py_compile` limpios; `create` + `moonfix` reales
  conservan el sufijo `26.11-10.07` tanto en la carpeta como en
  `<version>` de `details.xml`; build real con `--compiler zipapp
  --harden integrity` genera un `.iflapp` válido e `--inspect-json` lo lee.
- Verificación del ciclo de R-3f9a2c71 (2026-11-21):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 479 pasan, 1
  omitido (la dependencia opcional `leviathan_ui` está instalada en este
  entorno); `pyflakes` y `py_compile` limpios; build real
  `--compiler zipapp --no-sandbox --dropper` genera `.iflapp` y `.run`, y el
  `.run` regenerado con el stub corregido ejecuta `demo.pyz` e imprime
  `Hola desde demo!` (antes lanzaba `updater.py` y no terminaba). La prueba
  nueva falla con el código anterior (`wrong-entrypoint`).
- Verificación del ciclo de R-7b1d4e92 (2026-11-21):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 484 pasan, 1
  omitido; `pyflakes` y `py_compile` limpios; `--inspect-json` sobre una
  cabecera cortada, un JSON `null` o una sección fuera del archivo termina con
  código 1 y un `IflappError` legible (antes: código 0 con cabecera vacía o
  `struct.error`/`AttributeError`/`ValueError`).
- Verificación del ciclo de R-8a4f1c6d (2026-11-21):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 491 pasan, 1
  omitido; `pyflakes` y `py_compile` limpios; `--inspect-json` sobre cabeceras
  con `manifest` no lista, `payload`/`sections` no objeto, metadatos no
  numéricos u offset negativo termina con código 1 y un `IflappError` legible
  (antes: traceback `TypeError`/`AttributeError`/`ValueError` u `OSError`
  críptico); `--inspect-extract` ya no rompe con secciones mal tipadas. Build
  real `--compiler zipapp --no-sandbox` genera el `.iflapp`, `--inspect-json`
  lo lee, `--inspect-extract` exporta icono y `details.xml`, y
  `verify_iflapp()` devuelve `valid: True`.
- Verificación del ciclo de R-1c93e4b7, R-4d7b2e91, R-6b1f8d20, R-9e2a5c73 y
  R-2a7f6b41 (2026-11-21): `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`
  → 509 pasan, 1 omitido, 35 subtests; `pyflakes`, `py_compile` y `ruff`
  (`F821/F822/F823/F811/F841/B006/B008/B017/B904/E722`) limpios; build real
  `create` + `--buildthis --compiler zipapp --no-sandbox --harden integrity`
  genera un `.iflapp` válido (`verify_iflapp() → valid: True`), `--inspect`
  coincide ahora con el `details.xml` interno (`Plataforma: Danenone`) y
  `--app-version` informa `v3.2.7-26.05-20.13` desde `details.xml`.
- Verificación del ciclo de R-6f2b9d31 y R-8c4e1a72 (2026-11-21):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 521 pasan, 1
  omitido, 35 subtests; `pyflakes` y `py_compile` limpios; los 12 casos nuevos
  fallan con el código anterior (el de ofuscación por `SyntaxError` y los de
  motor por `struct.error`/`BadZipFile`). Build real
  `create` + `--buildthis --compiler zipapp --no-sandbox --harden obfuscate`
  genera un `.iflapp` válido (`verify_iflapp() → valid: True`), el `updater.py`
  empaquetado compila con `py_compile` y el `.pyz` del proyecto imprime
  `Hola desde demoobf!`; la fuente del proyecto no se modifica. Además,
  `obfuscate_strings()` sobre una copia del `updater.py` del repo (54
  literales) produce un archivo compilable.
- Verificación del ciclo de R-1f4a7c92, R-2b6d8e13 y R-3c9e1a57 (2026-11-21):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 541 pasan, 1
  omitido, 39 subtests; `pyflakes` y `py_compile` limpios; los 20 casos nuevos
  fallan con el código anterior. Con `data/pm.data` = `[]`, `--app-version` y
  `--list-compilers` arrancan (antes `TypeError`); `--compile-mexf` +
  `--shell-info-json` + `--install-asksome`/`--uninstall-asksome` reales
  funcionan sobre un `.asksome` firmado; una cabecera `[]`, una truncada o con
  `metadata` no objeto termina en `AsksomeError` legible (antes
  `AttributeError`/`TypeError`) y una entrada `C:/...`/`C:...` se rechaza.
- Release: **no preparado**. No se generaron `flat cube` ni `blind cube` en este
  ciclo. El periodo de observación de 3 días y el requisito de 7 días sin
  reportes nuevos siguen en curso.
