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
| R-d23039c0 | Mejora — telemetría | Media | Pendiente de aprobación |
| R-5d8e2a41 | Mejora — nombres con acentos | Media | Pendiente de aprobación |
| R-4c8e1f27 | Mejora — capitalización del publisher | Baja | Pendiente de aprobación |
| — | Cambios de engine (`bugs.txt`) | — | Pendiente de aprobación |

No hay bugs críticos ni de alta prioridad abiertos. Los reportes de auditoría
interna de los ciclos de mantenimiento (R-8f2c41d9, R-c47a9e12 y los cinco del
ciclo CLI, más R-b3f71a6c, R-7c1e4a90, R-91b6d2f4, R-3a7c5e18, R-9f2b64d1,
R-6e04c8ab, R-7d5b91c4, R-3f9a2c71 y R-7b1d4e92) quedaron corregidos y
probados. No se prepara release: el periodo de observación y el requisito de 7
días sin reportes nuevos siguen en curso.

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
  `325c0e9` y `850de5c`), no reportes de usuario; el contador de 7 días no se
  reinicia.
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
- Release: **no preparado**. No se generaron `flat cube` ni `blind cube` en este
  ciclo. El periodo de observación de 3 días y el requisito de 7 días sin
  reportes nuevos siguen en curso.
