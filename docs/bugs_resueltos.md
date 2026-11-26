# Archivo de bugs resueltos — Influent Package Maker

Entradas **ya resueltas**, retiradas de `bugs.md` el 2026-11-25 para
dejar la cola activa manejable. El detalle de cada corrección vive
también en `CHANGELOG.md`. Este archivo es histórico: se consulta y sólo
recibe entradas cuando una corrección verificada se retira de `bugs.md`.

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

## R-4e7c2b91 — Una caché de sesión o un fichero de idioma corruptos impedían arrancar

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** `session_cache.load_session()` hacía `data.get("token")` sin
  comprobar que el JSON descifrado fuera un objeto y `dict(profile)` sin
  comprobar que el perfil fuera un objeto. Un documento `[]` lanzaba
  `AttributeError` y un perfil como `["login"]`, `ValueError`. La llamada se
  hace en `start_session_gate()` al terminar el splash, sin `try`, así que el
  arranque de la GUI abortaba. Del mismo modo, `i18n._load_lang_file()` devolvía
  cualquier JSON y `_flatten_translations()` hacía `.items()`: un `lang/es.json`
  con `[]` reventaba en `i18n.initialize()`, antes de crear la ventana.
- **Pasos para reproducir:** escribir `data/session.cache` con `_encrypt(b"[]")`
  (o `lang/es.json` con `[]`) y arrancar la aplicación.
- **Estado:** Resuelto.
- **Prioridad:** Alta (impide el arranque).
- **Solución aplicada:** `load_session()` descarta documentos que no sean objeto
  y degrada un `profile` no-objeto a `{}`; `_load_lang_file()` ignora ficheros
  que no contengan un objeto y `_flatten_translations()` devuelve `{}` ante una
  entrada no-objeto.
- **Pruebas:** `tests/test_local_config_robustness.py::TestSessionCacheShapes` y
  `::TestLanguageFileShapes`.
- **Commit:** `7ce7a84`.
- **Fecha de resolución:** 2026-11-22.

## R-9a3d6f20 — Una configuración local con forma no-objeto rompía el editor y «Abrir con»

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** tres lectores de configuración aceptaban cualquier JSON.
  `pm_dashboard.load_config()` asignaba la lista a `self.config` y luego llamaba
  `.get()` (`AttributeError`), y `recent_projects` no-lista reventaba al
  iterarla; `python_portable_manager._load_config()` hacía `.get().items()` y
  `data["path"]` sobre formas inesperadas (`AttributeError`/`TypeError`), con lo
  que el gestor de intérpretes no se podía construir; y `ProjectConfig`
  (`get_project_editor`, `set_project_editor`, `get_editor_path`,
  `set_editor_path`) asumía que `projects`/`editors` eran objetos, así que
  `_on_accept()` de «Abrir con» fallaba al pulsar «Siempre».
- **Pasos para reproducir:** escribir `data/pmCodeEditor/config.json` o
  `config/project_config.json` con `[]`, `"texto"` o `{"projects": []}` y abrir
  la página del editor o el diálogo «Abrir con».
- **Estado:** Resuelto.
- **Prioridad:** Media (afecta a la UI del editor, no al arranque).
- **Solución aplicada:** cada lector exige un objeto JSON, degrada las secciones
  no-objeto (`recent_projects`, `installations`, `projects`, `editors`) a su
  valor por defecto e ignora entradas de instalación incompletas.
- **Pruebas:** `tests/test_local_config_robustness.py::TestPortableManagerConfigShapes`,
  `::TestDashboardConfigShapes` y `::TestProjectConfigShapes`.
- **Commit:** `7ce7a84`.
- **Fecha de resolución:** 2026-11-22.

## R-7f3a9c21 — Un `settings.json` con `build` no-objeto rompía `--ide-scan`

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** `_declared_scripts()` hacía `data.get("build", {}).get("scripts")`.
  Si `config/settings.json` era un objeto pero `build` era una lista, una cadena,
  `null` o un número (edición manual o corrupción), la segunda llamada a `.get()`
  lanzaba `AttributeError` y `--ide-scan` terminaba en traceback. En modo
  `--ide-scan-json` el traceback además contaminaba la salida que consume el
  shell, y la página del IDE no podía construir el proyecto.
- **Pasos para reproducir:** escribir `config/settings.json` con `{"build": []}`
  y ejecutar `python packagemaker.py --ide-scan <carpeta> --ide-scan-json`.
- **Estado:** Resuelto.
- **Prioridad:** Alta (rompe una acción headless y la página del IDE).
- **Solución aplicada:** `_declared_scripts()` exige que `build` sea un objeto
  antes de leer `scripts`; si no lo es, cae al descubrimiento de `.py` de la raíz.
- **Pruebas:** `tests/test_iflapp_ide.py::IdeProjectTests::test_find_scripts_tolerates_non_object_build_settings`
  y `tests/test_cli_json_stream_purity.py::JsonStreamPurityTests::test_ide_scan_json_tolerates_non_object_build_settings`.
- **Commit:** `38f0791`.
- **Fecha de resolución:** 2026-11-22.

## R-2c8e5d14 — `--ide-compile` lanzaba traceback con una carpeta inexistente

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** `IflappIdeHelper.compile()` llamaba a `compile_project()` sin
  protección. `scan_project()` lanza `FileNotFoundError` cuando la ruta no es
  una carpeta de proyecto y `mkdir()` puede lanzar `OSError` si `--ide-output`
  apunta a un archivo; ambos terminaban en un traceback en lugar de un mensaje
  `[ERROR]` con código 1.
- **Pasos para reproducir:** `python packagemaker.py --ide-compile /tmp/no-existe`.
- **Estado:** Resuelto.
- **Prioridad:** Media (acción headless, sin pérdida de datos).
- **Solución aplicada:** el helper captura `OSError` (incluye
  `FileNotFoundError`) y responde `[ERROR] No se pudo compilar el proyecto: …`
  devolviendo `False`.
- **Pruebas:** `tests/test_cli_json_stream_purity.py::JsonStreamPurityTests::test_ide_compile_missing_dir_reports_error_without_traceback`.
- **Commit:** `38f0791`.
- **Fecha de resolución:** 2026-11-22.

## R-5a1f8e63 — `--ide-debug` dejaba escapar las excepciones del guion depurado

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** `debug_script()` solo capturaba `OSError` y `SyntaxError`.
  Si el guion depurado lanzaba una excepción en tiempo de ejecución
  (`ZeroDivisionError`, `RuntimeError`, `SystemExit`…), la excepción escapaba de
  `trace_script()` y llegaba al CLI o al hilo de la UI, en lugar de rellenar
  `DebugOutcome.error`, que existe precisamente para eso.
- **Pasos para reproducir:** `--ide-debug` sobre un guion con `1/0`.
- **Estado:** Resuelto.
- **Prioridad:** Alta (puede tumbar el IDE al depurar código con errores).
- **Solución aplicada:** `debug_script()` captura el fallo del guion, incluido
  `SystemExit`, y lo devuelve en `DebugOutcome(error=...)`.
- **Pruebas:** `tests/test_iflapp_ide.py::IdeDebugTests::test_debug_script_reports_runtime_error`
  y `::test_debug_script_reports_system_exit`.
- **Commit:** `38f0791`.
- **Fecha de resolución:** 2026-11-22.

---

## R-3b8e5c71 — `install.json` con campos mal tipados rompía `--uninstall-asksome`

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** `InstallRecord(**data)` no valida tipos, así que un
  `install.json` editado a mano o corrompido con `"shortcuts": 5` se aceptaba y
  `uninstall_asksome()` reventaba al iterarlo
  (`TypeError: 'int' object is not iterable`). Un `"shortcuts": "texto"`
  iteraba los caracteres e intentaba borrar rutas inexistentes, y
  `--list-asksome` mostraba el registro dañado como si fuera válido. La
  desinstalación quedaba bloqueada justo cuando más falta hace: para retirar
  una instalación dañada.
- **Pasos para reproducir:** escribir
  `<install_root>/<app>/install.json` con los campos obligatorios y
  `"shortcuts": 5`, y ejecutar `--uninstall-asksome <app>`.
- **Estado:** Resuelto.
- **Prioridad:** Media.
- **Solución aplicada:** `_record_from_mapping()` construye el registro
  validando los campos de texto obligatorios y degradando `shortcuts`, `files`
  y `metadata` a su valor por defecto cuando no tienen el tipo esperado.
  `read_record()`, `list_installed()` y `uninstall_asksome()` lo usan, así que
  la desinstalación funciona aunque el registro esté parcialmente dañado y un
  campo obligatorio no textual sigue produciendo `AsksomeInstallError` legible.
- **Pruebas:** `tests/test_mexf_asksome.py::test_uninstall_tolerates_wrong_field_types_in_record`
  y `::test_read_record_rejects_non_text_required_fields`.
- **Commit:** `e9437cb`.
- **Fecha de resolución:** 2026-11-22.

## R-7c4d2a96 — Parámetros criptográficos mal tipados en `.blindkpkg`

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** `_decrypt_parameters()` solo capturaba `KeyError` y
  `ValueError`. Un contenedor `.blindkpkg` con `"salt": 5` o `"nonce": 5`
  lanzaba `TypeError` desde `bytes.fromhex()` y un `"mac": 5` lanzaba
  `TypeError` en `hmac.compare_digest()`, en lugar del `BlindCubeError`
  legible que la API promete para cabeceras corruptas.
- **Pasos para reproducir:** `blindcubeEngine.unpack(build_header(0, {"encryption": "hmac-sha256-ctr", "salt": 5, "nonce": "00"}), password="pw")`.
- **Estado:** Resuelto.
- **Prioridad:** Media.
- **Solución aplicada:** `_decrypt_parameters()` exige `salt`/`nonce` de tipo
  texto y traduce los fallos de decodificación a `BlindCubeError`; el MAC no
  textual se trata como ausente y produce el error de contraseña/payload.
- **Pruebas:** `tests/test_engines_and_platform.py::MalformedEngineContainerTests::test_blindcube_non_text_crypto_parameters_are_reported`.
- **Commit:** `e9437cb`.
- **Fecha de resolución:** 2026-11-22.

## R-1d9f6b34 — Parámetros criptográficos mal tipados en `.iflapp`

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** `_decrypt_payload()` hacía
  `base64.b64decode(params["salt"])` sin validar el tipo. Una cabecera
  `.iflapp` dañada con `salt`/`nonce` numéricos lanzaba `TypeError`, su ausencia
  `KeyError`, un valor no base64 `binascii.Error` y un `mac` numérico
  `TypeError` en `compare_digest`. Ninguno de esos fallos es un `IflappError`,
  así que la extracción (verificación del sandbox, actualizador, instalación
  desde el gestor) terminaba en traceback en vez de en un mensaje legible.
  El `.asksome` cifrado hereda el mismo arreglo porque delega en este módulo.
- **Pasos para reproducir:** empaquetar un `.iflapp` con `--password`, cambiar
  `payload.salt` por un entero en la cabecera y ejecutar
  `read_iflapp_payload(path, password=...)`.
- **Estado:** Resuelto.
- **Prioridad:** Media.
- **Solución aplicada:** `_decode_parameter()` valida que `salt`/`nonce` sean
  texto y traduce los errores de base64 a `IflappError`; un `mac` no textual se
  trata como ausente y produce `IflappSignatureError`.
- **Pruebas:** `tests/test_iflapp_format.py::MalformedEncryptionParameterTests`.
- **Commit:** `e9437cb`.
- **Fecha de resolución:** 2026-11-22.

---

## R-4f9b2c81 — Un `.asksome` con id `.`/`..` borraba fuera de la raíz de instalación

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** `_safe_app_id()` sólo sustituía los caracteres no alfanuméricos
  por `_`, pero conservaba `.` y `..`. `install_asksome()` hacía
  `target = install_root / app_id` y, si el destino existía, `shutil.rmtree(target)`.
  Un `.asksome` con `metadata.id` igual a `..` apuntaba al **directorio padre** de
  la raíz de instalación y lo borraba antes de fallar; con `.` borraba la propia
  raíz, es decir, todas las apps instaladas. El id viaja en la cabecera del
  artefacto, así que un paquete manipulado podía destruir datos del usuario.
- **Pasos para reproducir:** empaquetar un `.asksome` con
  `metadata={"id": ".."}` e instalarlo con `--install-asksome --install-root DIR`;
  el directorio padre de `DIR` desaparecía y la instalación terminaba en
  `FileNotFoundError`.
- **Estado:** Resuelto.
- **Prioridad:** Crítica.
- **Solución aplicada:** `_safe_app_id()` devuelve `asksome.app` cuando el
  identificador queda vacío al quitar los puntos; `_validated_app_id()` exige un
  único componente de ruta (`^[A-Za-z0-9._-]+$`, sin `.`/`..`) y
  `install_asksome()` lo aplica antes de crear o borrar el destino.
- **Pruebas:** `tests/test_mexf_asksome.py::test_install_rejects_dot_app_id_without_deleting_parent`.
- **Commit:** `3f89823`.
- **Fecha de resolución:** 2026-11-22.

---

## R-7a3d5e62 — `--uninstall-asksome`/`--build-removeme` aceptaban `app_id` con traversal

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** `uninstall_asksome()`, `read_record()` y `build_removeme()`
  construían la ruta con `install_root / app_id` sin validar el identificador
  recibido por la CLI. `--uninstall-asksome "../victima"` borraba con
  `shutil.rmtree()` un directorio **fuera** de la raíz de instalación, y una ruta
  absoluta (`/etc`, `C:...`) se usaba tal cual. `--build-removeme` escribía
  `removeme.py` fuera de la raíz con el mismo truco.
- **Pasos para reproducir:** crear `ROOT/victima/importante.txt` y ejecutar
  `--uninstall-asksome "../victima" --install-root ROOT`; el directorio externo
  se eliminaba y el comando informaba `[OK]`.
- **Estado:** Resuelto.
- **Prioridad:** Alta.
- **Solución aplicada:** los tres puntos de entrada validan el `app_id` con
  `_validated_app_id()` y lanzan `AsksomeInstallError`, que el CLI traduce a
  `[ERROR]` con código 1. El `app_id` de instalación también pasa por el validador.
- **Pruebas:** `tests/test_mexf_asksome.py::test_uninstall_rejects_app_id_that_escapes_install_root`
  y `::test_read_record_and_build_removeme_reject_unsafe_app_id`.
- **Commit:** `3f89823`.
- **Fecha de resolución:** 2026-11-22.

---

## R-2b9e4f73 — `--compile-mexf` lanzaba traceback si no podía escribir el `.asksome`

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** `compile_mexf_project()` llamaba a `pack_asksome()` sin proteger
  la escritura. Con `--mexf-output` apuntando a una carpeta existente,
  `Path.write_bytes()` lanzaba `IsADirectoryError`; con una ruta bajo un archivo
  normal, `mkdir(parents=True)` lanzaba `NotADirectoryError`; y un destino sin
  permisos lanzaba `PermissionError`. `MexfCompileHelper.compile()` sólo captura
  `MexfCompileError`, así que la CLI terminaba en traceback en lugar de `[ERROR]`.
  El mismo fallo afectaba a `MexfCompiler.run()` y al encadenado del build.
- **Pasos para reproducir:** `python packagemaker.py --compile-mexf PROYECTO
  --mexf-output /tmp` sobre un proyecto `.mexf` válido.
- **Estado:** Resuelto.
- **Prioridad:** Media.
- **Solución aplicada:** el staging, el empaquetado y los envoltorios de prueba se
  ejecutan dentro de un `try/except OSError` que los traduce a `MexfCompileError`
  con la ruta de destino; el CLI responde `[ERROR] Compilación .mexf fallida: …`
  con código 1.
- **Pruebas:** `tests/test_mexf_asksome.py::test_compile_mexf_project_reports_unwritable_output_as_compile_error`.
- **Commit:** `f9f635a`.
- **Fecha de resolución:** 2026-11-22.

---

## R-9d4c2f18 — La versión canónica bloqueaba la compilación

- **Usuario:** JesusQuijada34 (reporte manual en `bugs.txt`, commit `bed2e83`)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** al compilar, el propietario pegó la versión exacta del
  proyecto (`v1.0-26.11-22.00`, tal como la guarda `details.xml`) y la
  compilación se bloqueó con «Versión inválida: usa X.x o X.x.z». El validador
  estricto añadido para impedir datos fantasma (`_VERSION`) solo admitía
  `X.x[.z]`, aunque `ProjectNameFormatter` y `normalize_version_base` aceptan
  la forma canónica completa con timestamp y sufijo de plataforma. El usuario
  lo percibió como que la búsqueda exacta del proyecto se había roto.
- **Pasos para reproducir:** abrir la página de compilación, escribir en
  «Versión» `v1.0-26.11-22.00` (o `1.0-26.11-22.00`) y pulsar compilar; la
  alerta «Datos de compilación incompletos» impide continuar.
- **Estado:** Resuelto.
- **Prioridad:** Alta (bloquea el build con un valor legítimo).
- **Solución aplicada:** `_VERSION` acepta ahora `X.x[.z]` con un timestamp
  canónico opcional `-YY.MM-HH.MM` y el sufijo opcional `-Danenone`,
  `-Knosthalij` o `-AlphaCube`, igual que la autoridad de nombres. La base se
  sigue normalizando con `normalize_version_base()` antes de compilar, así que
  el timestamp se descarta para el nombre del artefacto. Los timestamps
  malformados y las plataformas desconocidas siguen rechazándose.
- **Pruebas:** `tests/test_build_validation.py::test_canonical_versions_with_timestamp_are_accepted`
  (4 casos), `::test_malformed_timestamp_versions_are_rejected` (3 casos) y
  `::test_canonical_version_normalizes_to_base_for_the_build`.
- **Commit:** `2011588`.
- **Fecha de resolución:** 2026-11-22.

---

## R-6c2a8f14 — Un `config/settings.json` no-objeto tumbaba la compilación

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** `FlangCompiler._load_scripts_to_compile()` leía
  `config/settings.json` y llamaba directamente a `settings.get("build")`. Un
  archivo editado a mano o truncado que seguía siendo JSON válido pero no era
  un objeto (`[]`, `"texto"`, `5`) lanzaba `AttributeError` en el constructor
  del compilador. El build de la GUI y el de `--buildthis`/`compile` se
  interrumpían con un traceback antes de poder mostrar un error legible, y el
  proyecto ni siquiera llegaba a la validación de metadatos.
- **Pasos para reproducir:** escribir `[]` en `config/settings.json` de un
  proyecto y ejecutar `--buildthis` (o instanciar `FlangCompiler`).
- **Estado:** Resuelto.
- **Prioridad:** Alta (bloquea la compilación de un proyecto dañado).
- **Solución aplicada:** si el documento no es un objeto se devuelve `None` y
  se conserva el descubrimiento histórico de guiones, igual que hace
  `_persist_env_payload()` y la lectura de `--ide-scan`. Un `build` que no sea
  objeto o unos `scripts` mal tipados siguen rechazándose con el mensaje ya
  existente.
- **Pruebas:** `tests/test_explicit_build_scripts.py::test_non_object_settings_fall_back_to_script_discovery`
  (4 subtests: lista, cadena, número y `build` no-objeto).
- **Commit:** `b656928`.
- **Fecha de resolución:** 2026-11-22.

## R-8b3d1e57 — Una raíz de instalación `.asksome` inválida lanzaba traceback

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** `install_asksome()` hacía `root.mkdir()` y
  `shutil.rmtree(target)` sin proteger los fallos del sistema de archivos. Si
  `--install-root` apuntaba a un archivo existente, a una ruta sin permisos o
  el destino era un archivo, el CLI terminaba con `FileExistsError`,
  `PermissionError` o `NotADirectoryError` en lugar de un `[ERROR]` legible.
  `AsksomeInstallHelper.install()` solo captura `AsksomeError`,
  `AsksomeInstallError` e `IflappError`, así que el traceback llegaba al
  usuario.
- **Pasos para reproducir:** crear un `.asksome` válido, crear un archivo
  normal en `/tmp/blocked-root` y ejecutar
  `--install-asksome demo.asksome --install-root /tmp/blocked-root`.
- **Estado:** Resuelto.
- **Prioridad:** Media (error de uso del CLI, sin pérdida de datos).
- **Solución aplicada:** la preparación de la raíz, la limpieza del destino y
  la extracción traducen `OSError` a `AsksomeInstallError` con la ruta
  afectada. El CLI responde `[ERROR] Instalación .asksome fallida: …` con
  código 1. El identificador de la app sigue validándose antes de tocar el
  disco.
- **Pruebas:** `tests/test_mexf_asksome.py::test_install_reports_unusable_install_root`
  (raíz que es un archivo y destino bloqueado por un archivo).
- **Commit:** `b656928`.
- **Fecha de resolución:** 2026-11-22.

## R-2c7e9b41 — Metadatos no canónicos matan la QThread del build sin aviso

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** el CLI valida la ley de nombres con
  `_validate_compiler_metadata()` antes de compilar, pero la GUI no. En
  `BuildThread.run()` se construye `FlangCompiler` y se llama a `run()`; cuando
  `details.xml` traía un publisher con acentos (`Jesús`), un `app` con
  caracteres no admitidos o una versión sin `X.x`,
  `ProjectNameFormatter.format_package_folder()` lanzaba `ValueError` al crear
  el nombre del paquete. La excepción escapaba de `QThread.run()`, que no
  emite `error` al terminar por excepción: la interfaz quedaba en «compilando»
  sin mensaje ni forma de reintentar. En el CLI el mismo proyecto sí mostraba
  un error legible.
- **Pasos para reproducir:** crear un proyecto con
  `<publisher>Jesús</publisher>` en `details.xml`, abrirlo en la GUI y pulsar
  Compilar.
- **Estado:** Resuelto.
- **Prioridad:** Alta (build inutilizable sin diagnóstico para proyectos con
  metadatos no canónicos, incluido el caso de acentos de la mejora R-5d8e2a41).
- **Solución aplicada:** `FlangCompiler._validate_metadata_naming()` valida
  publisher/app/versión con la misma autoridad (`ProjectNameFormatter`) al
  inicio de `run()` y convierte el `ValueError` en `last_error` con
  `[ERROR]`, de modo que la GUI emite `error` y el CLI conserva su mensaje.
  Además, `BuildThread.run()` envuelve la construcción y ejecución del
  compilador en un `try/except` que emite `error`: una QThread nunca debe
  morir en silencio ante una excepción imprevista.
- **Pruebas:** `tests/test_maintenance_cli_regressions.py::BuildThreadMetadataGuardTests`
  (4 casos: error emitido por la QThread, `FlangCompiler.run()` sin excepción,
  excepción inesperada convertida en `error` y payload `.env` con `config/`
  bloqueado).
- **Commit:** `3920254` y `81e1aec`.
- **Fecha de resolución:** 2026-11-22.

## R-5b3d8f27 — Carpeta de salida inaccesible lanza traceback al compilar

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** `--buildthis --output <ruta>` y el subcomando `compile`
  hacían `output_path.mkdir(parents=True, exist_ok=True)` sin proteger
  `OSError`. Una ruta bajo un archivo (`/tmp/blocker/out`), una unidad
  inexistente o una carpeta sin permisos terminaba en
  `FileNotFoundError`/`NotADirectoryError`/`PermissionError` con traceback
  antes de compilar. En la GUI, `FlangCompiler.__init__` hacía el mismo
  `mkdir` dentro de la QThread, con el mismo efecto de hilo muerto sin
  `error`. `create_package()` repetía el patrón al crear la carpeta del
  paquete.
- **Pasos para reproducir:** crear un archivo normal `/tmp/blocker` y ejecutar
  `--buildthis <proyecto> --output /tmp/blocker/out`.
- **Estado:** Resuelto.
- **Prioridad:** Media (error de uso, sin pérdida de datos).
- **Solución aplicada:** `_prepare_output_directory()` en `cliHandler` crea la
  carpeta o responde `[ERROR] No se pudo preparar la carpeta de salida …` con
  código 1. `FlangCompiler` registra el fallo en `last_error` y
  `output_path_ready`, y `run()` lo publica sin lanzar; `create_package()`
  traduce el fallo de `mkdir` a un `False` con mensaje.
- **Pruebas:** `tests/test_maintenance_cli_regressions.py::UnwritableOutputDirectoryTests`
  (2 casos: CLI con código 1 y compilador que difiere el error a `run()`) y
  `BuildThreadMetadataGuardTests` (guardado de `.env` sin excepción).
- **Commit:** `3920254` y `81e1aec`.
- **Fecha de resolución:** 2026-11-22.

## R-7f2b9c63 — Un `.run` con el `.iflapp` corrupto lanza traceback

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** `create_dropper()` genera un `.run` que embebe el `.iflapp`
  en base64. Si la descarga se corta o el bloque embebido se altera, el stub
  llamaba a `_header()` sin comprobar longitud ni JSON y `_extract_v2()`
  indexaba `header["payload"]` sin validar el tipo. El usuario final veía un
  traceback con `UnicodeDecodeError`, `JSONDecodeError`, `KeyError`,
  `binascii.Error` o `IndexError` en lugar de un mensaje legible. Además,
  `--password` sin valor terminaba en `IndexError`, y `read_dropper_header()`
  dejaba escapar `binascii.Error` en vez de `IflappError`.
- **Pasos para reproducir:** crear un dropper válido, sustituir el bloque
  base64 embebido por bytes aleatorios y ejecutar `python demo.run`.
- **Estado:** Resuelto.
- **Prioridad:** Media (el paquete no arranca, pero no hay pérdida de datos).
- **Solución aplicada:** `_decode_header()` valida JSON y tipo de objeto;
  `_header()` valida longitudes y truncamiento; `_extract_v2()` valida el
  bloque `payload`, el rango `offset`/`size` y traduce los fallos de
  descifrado, `lzma` y `tar` a `SystemExit` legible; `_extract_zip()` y
  `main()` hacen lo propio con ZIP y con `--password` sin valor.
  `read_dropper_header()` convierte el payload base64 inválido en
  `IflappError`.
- **Pruebas:** `tests/test_iflapp_dropper_sandbox.py::DropperTests` (4 casos:
  payload corrupto, payload truncado, `--password` sin valor y base64
  corrupto en el lector). Los 4 fallan con el código anterior.
- **Commit:** `caeef80`.
- **Fecha de resolución:** 2026-11-22.

---

## R-7c9e2a45 — Un `editor_config.json` con forma no válida rompía el arranque

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** el panel (`DashboardWindow`) y el editor (`EditorWindow`)
  comparten `data/pmCodeEditor/editor_config.json`. Un archivo editado a mano o
  escrito a medias que sigue siendo JSON válido pero no tiene la forma esperada
  tumbaba la ventana al construirla: en el panel, un `default_interpreter` que
  no era texto (`123`, `["x"]`, `{...}`) se asignaba a `os.environ`, que lanza
  `TypeError: str expected`; en el editor, un documento no-objeto (`[]`,
  `"texto"`) reventaba en `cfg.get()` con `AttributeError`, y un
  `default_interpreter` lista/objeto lo hacía en `os.path.isfile()` con
  `TypeError`. La corrección anterior R-9a3d6f20 solo cubrió el caso no-objeto
  del panel, no el valor mal tipado ni el editor.
- **Pasos para reproducir:** escribir
  `data/pmCodeEditor/editor_config.json` con `{"default_interpreter": 123}` y
  abrir el panel, o con `[]`/`{"default_interpreter": ["x"]}` y abrir el
  editor; la ventana no se construye y el arranque termina en traceback.
- **Estado:** Resuelto.
- **Prioridad:** Media (impide abrir el panel/editor, pero no hay pérdida de datos).
- **Solución aplicada:** `DashboardWindow.load_config()` solo adopta el
  intérprete si es una cadena no vacía antes de exportarlo a `PM_PYTHON_PATH`;
  `EditorWindow._load_editor_config()` descarta los documentos que no son
  objeto y exige que `default_interpreter` sea una cadena no vacía antes de
  comprobarla con `os.path.isfile()`.
- **Pruebas:** `tests/test_local_config_robustness.py` —
  `TestDashboardConfigShapes::test_non_string_interpreter_is_ignored`,
  `TestEditorConfigShapes::test_non_object_config_is_ignored` y
  `TestEditorConfigShapes::test_non_string_interpreter_is_ignored`. Las tres
  fallan con el código anterior (comprobado con `git stash` de
  `lib/pm_dashboard.py` y `pmCodeEditor.py`).
- **Commit:** `6f45dd0`.
- **Fecha de resolución:** 2026-11-22.

---

## R-4e8b2d17 — `--shell-info` lanzaba traceback con un paquete ilegible o una vista previa bloqueada

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** `NativeShellHelper.info()` solo traducía `ValueError`, pero
  `native_shell.package_info()` lee el archivo con `Path.read_bytes()`. Un
  paquete sin permiso de lectura escapaba como `PermissionError` con traceback.
  Del mismo modo, `export_icon_preview()` crea el directorio de destino con
  `mkdir()` fuera del `try`, así que `--shell-preview` con una ruta ocupada por
  un archivo normal (o sin permiso de escritura) terminaba en
  `FileExistsError`/`PermissionError`. El propio
  `python -m lib.native_shell --info` ya trataba `(ValueError, OSError)` como
  error esperado, de modo que el CLI era inconsistente con su contrato.
- **Pasos para reproducir:** `chmod 000 paquete.iflapp && python packagemaker.py
  --shell-info paquete.iflapp`; o `python packagemaker.py --shell-info
  paquete.asksome --shell-preview /ruta/a/archivo_normal`.
- **Estado:** Resuelto.
- **Prioridad:** Media (el comando termina en traceback, pero no hay pérdida de
  datos ni corrupción).
- **Solución aplicada:** `NativeShellHelper.info()` captura `(ValueError,
  OSError)` al leer los metadatos y al exportar la vista previa, e informa
  `[ERROR] …` / `[ERROR] No se pudo exportar la vista previa: …` con código 1.
  En modo `--shell-info-json` el error va a stderr y stdout queda vacío, así que
  el documento JSON sigue siendo parseable. `native_shell._thumbnail_main()`
  también traduce `(ValueError, OSError)` a código 1 para que el generador de
  miniaturas del escritorio no muestre traceback.
- **Pruebas:** `tests/test_native_shell.py` —
  `test_shell_info_reports_unreadable_package_without_traceback`,
  `test_shell_info_json_keeps_stdout_clean_when_package_unreadable`,
  `test_shell_info_reports_blocked_preview_directory` y
  `test_thumbnail_main_handles_unreadable_source`. Las cuatro fallan con el
  código anterior (comprobado con `git stash` de `lib/cliHandler.py` y
  `lib/native_shell.py`).
- **Commit:** `edb049f`.
- **Fecha de resolución:** 2026-11-22.

---

## R-6d2f8a41 — `--compile-mexf` lanzaba traceback con entradas ilegibles

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte externo)
- **Fecha del reporte:** 2026-11-22
- **Descripción:** `compile_mexf_project()` leía `details.xml`, descubría los
  módulos y parseaba cada `.mexf` sin traducir los fallos del sistema de
  archivos. Un `details.xml` sin permiso de lectura escapaba desde
  `ET.parse()` como `PermissionError`; un `.mexf/main.mexf` ilegible hacía lo
  propio desde `Path.read_text()` en `parse_mexf()`; y un directorio `.mexf/`
  sin permiso reventaba en `main.is_file()` dentro de
  `discover_mexf_modules()`. `MexfCompileHelper.compile()` solo capturaba
  `MexfCompileError`, así que el CLI mostraba un traceback en vez de un mensaje
  legible. `detect_mexf_format()` también dejaba escapar `OSError` pese a que su
  contrato es devolver `"unknown"` cuando no puede leer el documento.
- **Pasos para reproducir:** `chmod 000 proyecto/.mexf/main.mexf && python
  packagemaker.py --compile-mexf proyecto`; repetir con `details.xml` o con el
  directorio `.mexf/` sin permisos.
- **Estado:** Resuelto.
- **Prioridad:** Media (el comando termina en traceback, pero no hay pérdida de
  datos ni corrupción).
- **Solución aplicada:** `parse_mexf()` traduce `OSError` a `MexfError` con la
  ruta y el motivo; `detect_mexf_format()` trata `(UnicodeDecodeError, OSError)`
  como `"unknown"`; `read_project_details()` captura `(ET.ParseError, OSError)`
  y `discover_mexf_modules()` envuelve la comprobación y el `rglob` para
  devolver `MexfCompileError`. `compile_mexf_project()` acepta
  `(MexfError, OSError)` al parsear los módulos y `MexfCompileHelper.compile()`
  responde `[ERROR] Compilación .mexf fallida: …` con código 1. Un proyecto
  legible sigue generando el `.asksome` firmado.
- **Pruebas:** `tests/test_mexf_asksome.py` —
  `test_parse_mexf_reports_unreadable_source_as_mexf_error`,
  `test_compile_mexf_project_reports_unreadable_module_as_compile_error`,
  `test_compile_mexf_project_reports_unreadable_details_as_compile_error`,
  `test_compile_mexf_project_reports_unreadable_module_directory` y
  `test_compile_mexf_helper_reports_unreadable_input_without_traceback`. Las
  cinco fallan con el código anterior (comprobado con `git stash` de
  `lib/mexf_parser.py`, `lib/mexf_compiler.py` y `lib/cliHandler.py`).
- **Commit:** `f8ea814`.
- **Fecha de resolución:** 2026-11-22.

## R-4c7a9e13 — `--inspect-extract` lanzaba traceback con un destino bloqueado

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte externo)
- **Fecha del reporte:** 2026-11-23
- **Descripción:** `PackageInspectHelper.inspect()` exportaba los recursos de la
  cabecera con `iflapp_format.export_header_assets()` sin capturar los fallos del
  sistema de archivos. Un destino ocupado por un archivo normal terminaba en
  `FileExistsError` desde `mkdir()` y uno sin permiso, en `PermissionError`.
  Como el `try` del helper solo cubría la lectura de la cabecera, el CLI
  mostraba un traceback incluso en modo `--inspect-json`.
- **Pasos para reproducir:** `touch /tmp/blocker && python packagemaker.py
  --inspect demo.iflapp --inspect-extract /tmp/blocker`.
- **Estado:** Resuelto.
- **Prioridad:** Media.
- **Solución aplicada:** `export_header_assets()` envuelve la lectura y la
  escritura y traduce `OSError` a `IflappError`; el helper responde
  `[ERROR] …` con código 1 y, en modo JSON, escribe el error en stderr para no
  contaminar stdout.
- **Pruebas:** `tests/test_unreadable_paths.py` —
  `test_export_header_assets_translates_oserror` y
  `test_inspect_extract_reports_blocked_destination`.
- **Commit:** `743c914`.
- **Fecha de resolución:** 2026-11-23.

## R-8e2b5c43 — `--list-asksome` lanzaba traceback con una raíz ilegible

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte externo)
- **Fecha del reporte:** 2026-11-23
- **Descripción:** `list_installed()` comprobaba `root.is_dir()` y recorría
  `root.iterdir()` sin capturar `OSError`. Con una raíz de instalación sin
  permiso de lectura, Python 3.13 propagaba `PermissionError` y el CLI de
  `--list-asksome` terminaba en traceback.
- **Pasos para reproducir:** `chmod 000 /tmp/installs && python packagemaker.py
  --list-asksome --install-root /tmp/installs`.
- **Estado:** Resuelto.
- **Prioridad:** Media.
- **Solución aplicada:** `list_installed()` usa `path_is_dir()`,
  `list_directory()`, `path_is_dir()` y `path_is_file()` de `lib/file_ops.py`,
  que degradan un `OSError` a «no hay entradas». El CLI informa «Sin artefactos
  .asksome instalados» con código 0.
- **Pruebas:** `tests/test_unreadable_paths.py` —
  `test_list_installed_ignores_unreadable_root` y
  `test_list_installed_cli_reports_empty_root`.
- **Commit:** `743c914`.
- **Fecha de resolución:** 2026-11-23.

## R-3d9f1a76 — `compile`/TUI lanzaban traceback con la carpeta base ilegible

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte externo)
- **Fecha del reporte:** 2026-11-23
- **Descripción:** `lib/project_locator.py` listaba la carpeta de proyectos con
  `sorted(base.iterdir())` y comprobaba cada entrada con `is_dir()`/`is_file()`.
  Si `BASE_DIR` existía pero no era legible, `iter_projects()`/`list_projects()`
  propagaban `PermissionError`; el subcomando `compile` y la TUI mostraban un
  traceback en lugar de «no se encontró proyecto».
- **Pasos para reproducir:** `chmod 000 "$BASE_DIR" && python packagemaker.py
  compile --name Demo --shortname demo`.
- **Estado:** Resuelto.
- **Prioridad:** Alta (rompe el flujo principal de compilación headless).
- **Solución aplicada:** `iter_projects()`, `list_projects()`,
  `is_project_directory()` y `locate_project()` usan los envoltorios de
  `lib/file_ops.py`; una carpeta ilegible se trata como vacía y el CLI responde
  `[ERROR] No se encontró proyecto que coincida con …` con código 1.
- **Pruebas:** `tests/test_unreadable_paths.py` —
  `test_project_listing_ignores_unreadable_base_dir`.
- **Commit:** `743c914`.
- **Fecha de resolución:** 2026-11-23.

## R-6c1e8b52 — `--buildthis`/`--ide-run`/`--shell-info` lanzaban traceback con rutas ilegibles

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte externo)
- **Fecha del reporte:** 2026-11-23
- **Descripción:** tres comprobaciones de ruta de la CLI usaban `Path.exists()`,
  `Path.is_file()` e `Path.is_dir()` directamente sobre rutas del usuario. En
  Python 3.13 esas llamadas propagan `PermissionError` cuando el directorio
  padre no es accesible, así que `--buildthis`, `--ide-run` y `--shell-info`
  terminaban en traceback en lugar de un mensaje legible.
- **Pasos para reproducir:** `chmod 000 /tmp/locked && python packagemaker.py
  --buildthis /tmp/locked/proj --output /tmp/out` (y los equivalentes con
  `--ide-run /tmp/locked/app.py` y `--shell-info /tmp/locked/demo.asksome`).
- **Estado:** Resuelto.
- **Prioridad:** Alta (`--buildthis` es la vía de compilación de CI).
- **Solución aplicada:** las comprobaciones usan `path_exists()`,
  `path_is_file()` y `path_is_dir()` de `lib/file_ops.py` y los mensajes
  distinguen «no existe» de «no es accesible».
- **Pruebas:** `tests/test_unreadable_paths.py` —
  `test_buildthis_rejects_unreadable_project`,
  `test_ide_run_rejects_unreadable_script` y
  `test_shell_info_rejects_unreadable_target`.
- **Commit:** `743c914`.
- **Fecha de resolución:** 2026-11-23.

## R-7b3e9c28 — `--install-asksome` lanzaba traceback con un artefacto ilegible

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte externo)
- **Fecha del reporte:** 2026-11-23
- **Descripción:** `AsksomeInstallHelper.install()` comprobaba el artefacto con
  `artifact.is_file()` fuera de cualquier `try`; con el padre sin permisos,
  Python 3.13 propagaba `PermissionError`. Además, `_read_container()` leía el
  archivo con `Path.read_bytes()` sin traducir `OSError`, de modo que un
  artefacto ilegible escapaba como excepción cruda en lugar de `AsksomeError`.
- **Pasos para reproducir:** `chmod 000 /tmp/locked && python packagemaker.py
  --install-asksome /tmp/locked/demo.asksome --install-root /tmp/root`.
- **Estado:** Resuelto.
- **Prioridad:** Media.
- **Solución aplicada:** la comprobación usa `path_is_file()` y
  `_read_container()` traduce `OSError` a `AsksomeError` con la ruta y el
  motivo; el CLI responde `[ERROR] No existe el artefacto o no es accesible: …`
  con código 1.
- **Pruebas:** `tests/test_unreadable_paths.py` —
  `test_asksome_reader_translates_oserror` y
  `test_install_asksome_rejects_unreadable_artifact`.
- **Commit:** `743c914`.
- **Fecha de resolución:** 2026-11-23.

## R-5a9d2f74 — Abrir una carpeta genérica o lanzar MoonFix por lotes tumbaba la GUI

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte externo)
- **Fecha del reporte:** 2026-11-23
- **Descripción:** `DashboardWindow._open_as_generic_project()` hacía
  `sorted(os.listdir(path))` y `PackageTodoGUI.mf_start_scan()` recorría la
  carpeta con `os.listdir(path)` sin capturar `OSError`. Al elegir una carpeta
  sin permiso de lectura desde «Abrir repositorio GitHub» o al lanzar MoonFix
  en modo lote, el slot de Qt lanzaba `PermissionError`; en PyQt6 una excepción
  no controlada en un slot aborta la aplicación.
- **Pasos para reproducir:** con una carpeta `chmod 000`, abrirla desde el
  panel como proyecto genérico o ejecutar MoonFix en modo lote sobre ella.
- **Estado:** Resuelto.
- **Prioridad:** Media (crash de la GUI, sin pérdida de datos).
- **Solución aplicada:** ambos puntos capturan `OSError`; el panel abre el
  editor sin guion y MoonFix muestra un diálogo de error con el motivo.
- **Pruebas:** `tests/test_unreadable_paths.py` —
  `test_dashboard_generic_open_survives_unreadable_folder` y
  `test_moonfix_batch_scan_reports_unreadable_folder`.
- **Commit:** `743c914`.
- **Fecha de resolución:** 2026-11-23.

## R-2f8a4d61 — `remove_tree` lanzaba `PermissionError` pese a prometer que no lanza

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte externo)
- **Fecha del reporte:** 2026-11-23
- **Descripción:** el docstring de `lib/file_ops.remove_tree()` garantiza que no
  lanza, pero empezaba con `target.exists()` y terminaba con `not
  target.exists()`. En Python 3.13 `Path.exists()` propaga `PermissionError`,
  así que la limpieza de un directorio temporal bajo un padre inaccesible
  rompía el contrato y abortaba el flujo de build que confiaba en él.
- **Pasos para reproducir:** llamar `remove_tree()` sobre una ruta cuyo padre
  no es accesible.
- **Estado:** Resuelto.
- **Prioridad:** Baja.
- **Solución aplicada:** `_tree_exists()` usa `os.lstat()` y distingue «no
  existe» de «no se puede comprobar»; `remove_tree()` devuelve `True` solo si
  el árbol desapareció y `False` cuando no pudo verificarlo.
- **Pruebas:** `tests/test_unreadable_paths.py` —
  `test_remove_tree_keeps_its_no_raise_contract`.
- **Commit:** `743c914`.
- **Fecha de resolución:** 2026-11-23.

## R-9c1e5b74 — Valores numéricos corruptos en `pm.data` impedían arrancar la GUI

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte externo)
- **Fecha del reporte:** 2026-11-23
- **Descripción:** `SettingsPanel._build_cards()` convertía
  `sidebar_accent_width` con `int(...)` y `card_opacity` con
  `int(float(...) * 100)`; `PackageTodoGUI.apply_theme()` hacía lo propio con
  `sidebar_accent_width`, el sidebar con `sidebar_width` y
  `_update_restart_banner()` con `dpi_scale`/`applied_dpi_scale`. `data/pm.data`
  es editable a mano, así que un texto, una lista o `null` en esas claves
  lanzaba `ValueError`/`TypeError` durante la construcción de la ventana
  principal (`init_config_tab` se ejecuta al arrancar) y la aplicación no
  abría.
- **Pasos para reproducir:** escribir `"sidebar_accent_width": "tres"`,
  `"card_opacity": null` o `"sidebar_width": [260]` en `data/pm.data` y
  arrancar la aplicación.
- **Estado:** Resuelto.
- **Prioridad:** Alta (impide arrancar; la recuperación exige editar el archivo).
- **Solución aplicada:** `lib/pm_data.py` gana `coerce_int()` y
  `coerce_float()` (más `PMDataStore.get_user_int()`/`get_user_float()`), que
  aceptan números o texto numérico y caen al valor por defecto con cualquier
  otro tipo. Los cinco puntos de lectura usan esos getters y
  `SettingsPanel` importa los conversores.
- **Pruebas:** `tests/test_startup_corruption_robustness.py` —
  `CoercionTests` y `SettingsPanelRobustnessTests`.
- **Commit:** `4e78f2e`.
- **Fecha de resolución:** 2026-11-23.

## R-2b7d4a90 — `find_flarm_project` revienta con una carpeta de proyectos ilegible o un `package_config.json` corrupto

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte externo)
- **Fecha del reporte:** 2026-11-23
- **Descripción:** al arrancar `pmCodeEditor` con un nombre de proyecto,
  `find_flarm_project()` recorría `~/Documents/Packagemaker Projects` con
  `os.listdir()` sin capturar `OSError` (en Python 3.13 una carpeta `chmod 000`
  lanza `PermissionError`) y leía cada `package_config.json` capturando solo
  `(OSError, KeyError)`. Un JSON truncado lanzaba `JSONDecodeError`, un JSON que
  no era objeto lanzaba `AttributeError` en `.get()` y un campo no textual
  rompía en `.lower()`. El traceback cortaba el arranque del editor.
- **Pasos para reproducir:** con un `package_config.json` con `{no es json`, con
  `[1, 2]` o con `{"titulo": 5}`, ejecutar `find_flarm_project("demo")`; repetir
  con la carpeta de proyectos en modo `000`.
- **Estado:** Resuelto.
- **Prioridad:** Alta (traceback en el arranque del editor).
- **Solución aplicada:** la carpeta se lista una sola vez dentro de `try/except
  OSError`; las lecturas de configuración capturan `(OSError, ValueError)`,
  exigen un objeto JSON y convierten los campos a texto antes de compararlos.
- **Pruebas:** `tests/test_startup_corruption_robustness.py` —
  `FindFlarmProjectTests` (config corrupta, config no-objeto, campos no
  textuales, caso válido y carpeta ilegible).
- **Commit:** `4e78f2e`.
- **Fecha de resolución:** 2026-11-23.

## R-5d8f1c36 — La depuración del editor `.mexf` lanzaba `yaml.YAMLError` en un slot de Qt

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte externo)
- **Fecha del reporte:** 2026-11-23
- **Descripción:** `MexfEditorDialog._document()` convertía el texto con
  `yaml.safe_load()` sin capturar `yaml.YAMLError`. Los botones «Paso»,
  «Continuar», «Detener» y el punto de ruptura llaman a `_ensure_debugger()` →
  `MexfDebugger(self._document())`, de modo que un documento a medio escribir
  (por ejemplo `metadata: [unclosed`) lanzaba la excepción dentro del slot y
  PyQt6 abortaba la aplicación. La ruta CLI de `--debug-mexf` ya lo gestionaba.
- **Pasos para reproducir:** abrir el editor `.mexf`, escribir un YAML inválido
  y pulsar «Paso» o marcar un punto de ruptura.
- **Estado:** Resuelto.
- **Prioridad:** Media (crash de la GUI mientras se edita).
- **Solución aplicada:** `_document()` captura `yaml.YAMLError` y devuelve un
  documento vacío; el lint sigue mostrando el diagnóstico y la depuración
  informa «depuración finalizada» en lugar de abortar.
- **Pruebas:** `tests/test_mexf_editor_dialog.py` —
  `test_invalid_yaml_does_not_break_debug_controls`.
- **Commit:** `4e78f2e`.
- **Fecha de resolución:** 2026-11-23.

## R-8a2f6d51 — `uninstall_plan` (rama Windows) dejaba escapar `OSError`

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte externo)
- **Fecha del reporte:** 2026-11-23
- **Descripción:** `lib.mexf_shell.uninstall_plan()` documenta que retira lo que
  pueda y acumula el resto en `skipped`; la rama Linux captura `OSError` por
  objetivo, pero la rama Windows comprobaba `reg.exists()` y llamaba a
  `unlink()` fuera de todo `try`. Un directorio base ilegible (o un `.reg` sin
  permiso de borrado) lanzaba `PermissionError` y rompía el contrato.
- **Pasos para reproducir:** `uninstall_plan(plan, base_dir=<dir 000>,
  platform_name="win32")`.
- **Estado:** Resuelto.
- **Prioridad:** Baja (inconsistencia de contrato; sin pérdida de datos).
- **Solución aplicada:** la rama Windows envuelve la comprobación y el borrado
  en `try/except OSError` y registra el motivo en `skipped`.
- **Pruebas:** `tests/test_mexf_shell.py` —
  `test_uninstall_plan_windows_survives_unreadable_directory`.
- **Commit:** `4e78f2e`.
- **Fecha de resolución:** 2026-11-23.

---

## R-5b1d9e47 — El hover del sidebar parpadeaba y los iconos quedaban apretados

- **Usuario:** JesusQuijada34 (respuesta a Q-010 en `CONFIRM.MD`, commit `0ac5457`)
- **Fecha del reporte:** 2026-11-23
- **Prioridad:** Media
- **Descripción:** al pasar el ratón, el ítem alternaba entre el azul/gris
  heredado y el gris de reposo («el parpadeo sigue»), y los iconos quedaban muy
  apretados: faltaban unos 10 px de ancho.
- **Pasos para reproducirlo:** abrir la aplicación, pasar el ratón por los
  ítems del sidebar y hacer clic en uno mientras el puntero sigue encima.
- **Causa raíz:** `_HoverFade` reescribía la hoja de estilo del ítem en cada
  fotograma; cada `setStyleSheet()` fuerza un re-polish y, en ese intervalo, se
  reevaluaba la regla heredada `QWidget#NavigationSidebar QPushButton:hover` (y
  `:checked` con borde de acento). Además, el fondo de selección del tema claro
  era un azul fijo `rgba(0, 120, 212, 0.18)` ajeno al token de acento.
- **Solución aplicada:** el resalte se pinta en `paintEvent` con la propiedad
  animada `hoverProgress` (una sola `QPropertyAnimation` reutilizada) y sin
  tocar el QSS; el selector propio
  `QPushButton#SidebarNavItem[pmNavItem="true"]` se impone a la regla heredada;
  el fondo de selección se deriva del acento con `with_alpha()`; el ancho por
  defecto pasa a 270 px (migración única desde 260) y el padding derecho a
  14 px. Al seleccionar un ítem se retira el tinte de hover.
- **Pruebas:** `tests/test_hover_and_tokens.py` (hover sin re-polish, ítem
  seleccionado sin tinte, fondo derivado del acento, ancho por defecto).
- **Commit:** vigésimo quinto ciclo.
- **Fecha de resolución:** 2026-11-23.

## R-7a3e1d92 — `CONFIRM.MD` quedó commiteado con marcadores de conflicto

- **Usuario:** JesusQuijada34 (commit `0ac5457`)
- **Fecha del reporte:** 2026-11-23
- **Prioridad:** Alta (rompe el único canal de aprobación)
- **Descripción:** el bloque Q-008 contenía `<<<<<<< HEAD`, `=======` y
  `>>>>>>> 418c3e3`, con `[ ] SÍ` en un lado y `[x] SÍ` en el otro. Las demás
  respuestas convivían con ese texto ilegible.
- **Solución aplicada:** se repara el archivo, se registran las decisiones
  verificadas en `Historial` y Q-008 vuelve a `Pendientes` como pregunta única.
  La autoría del commit se verificó con la API de GitHub
  (`author.login == "JesusQuijada34"`).
- **Pruebas:** `tests/test_confirm_channel.py` (sin marcadores de conflicto y
  sin preguntas duplicadas).
- **Fecha de resolución:** 2026-11-23.

## R-3c7a1e90 — El guardado de Configuración abortaba la aplicación con una ruta imposible

- **Usuario:** JesusQuijada34 (reporte de congelamientos en Configuración,
  `bugs.txt`; hallazgo de la auditoría interna al reproducirlo)
- **Fecha del reporte:** 2026-11-23
- **Prioridad:** Alta
- **Descripción:** escribir en «Configuración → Rutas» una carpeta que no se
  puede crear (unidad inexistente, ruta bajo un archivo, carpeta sin permisos)
  cerraba la aplicación en el acto, sin mensaje. El guardado es automático y
  corre dentro de un slot de PyQt6, así que el `OSError` no controlado de
  `os.makedirs()` se convertía en `Fatal Python error: Aborted`.
- **Pasos para reproducir:** abrir Configuración, escribir
  `/proc/pm-no-puede/crear` (o cualquier ruta bajo un archivo) en la carpeta de
  proyectos y esperar el guardado automático.
- **Causa raíz:** `_save_app_config_compact()` llamaba a `os.makedirs()` sin
  `try/except` y sin validar la ruta antes de persistirla. El arranque del
  módulo sí protegía sus `makedirs`, pero el guardado del panel no.
- **Estado:** Resuelto.
- **Solución aplicada:** `ensure_config_directories()` crea y valida las dos
  carpetas antes de guardar; si falla, el guardado se cancela, la configuración
  anterior queda intacta y el aviso sale por el `Reporter` (barra de estado, o
  diálogo si el guardado fue explícito). Nunca se propaga la excepción al slot.
- **Pruebas:** `tests/test_settings_save_guards.py`
  (`TestEnsureConfigDirectories`, `test_uncreatable_path_reports_instead_of_aborting`).
- **Commit:** vigésimo sexto ciclo.
- **Fecha de resolución:** 2026-11-23.

## R-9e2b4d17 — Configuración repintaba el tema dos veces y reiniciaba el motor elegido

- **Usuario:** JesusQuijada34 (`bugs.txt`: «al maximizar o restaurar o al
  cambiar opciones en configuración, porque se queda congelado un rato?»)
- **Fecha del reporte:** 2026-11-23
- **Prioridad:** Media
- **Descripción:** cualquier cambio en Configuración —incluso escribir una ruta
  o activar un aviso— congelaba la ventana un instante perceptible. Además, la
  elección de motor (FlatCube/BlindCube) volvía sola a BlindCube después de
  cambiar un ajuste.
- **Pasos para reproducir:** en la pestaña Compilar elegir FlatCube v1, ir a
  Configuración, cambiar cualquier opción y volver a Compilar.
- **Causa raíz:** `_save_app_config_compact()` reaplicaba siempre
  `apply_ui_language()`, `_apply_leviathan_and_personalization()` y
  `apply_theme()`. Como `_apply_display_mode_by_name()` ya termina en
  `apply_theme()`, el tema se repintaba dos veces por guardado (≈0,10 s cada
  uno offscreen, más en Windows con la ventana real). `apply_ui_language()`
  vuelve a poblar el selector de motores y lo deja en BlindCube.
- **Estado:** Resuelto.
- **Solución aplicada:** `settings_appearance_state()` captura sólo los valores
  que obligan a repintar (acento, ancho del indicador, densidad, modo de
  presentación y fuente) antes y después de guardar, y
  `settings_reapply_plan()` decide qué reaplicar: nada si no cambió la
  apariencia, `apply_theme()` una sola vez si cambió un valor visual,
  `_apply_leviathan_and_personalization()` si cambió el modo de presentación y
  la retraducción sólo cuando cambió el idioma.
- **Pruebas:** `tests/test_settings_save_guards.py`
  (`TestSettingsReapplyPlan`, `TestAppearanceState`,
  `test_path_only_save_does_not_repaint_theme`,
  `test_engine_choice_survives_an_autosave`).
- **Commit:** vigésimo sexto ciclo.
- **Fecha de resolución:** 2026-11-23.

## R-4d8f2b61 — Botón Guardar en Configuración con opciones automáticas

- **Usuario:** JesusQuijada34 (`bugs.txt`: «en configuracion aparece el boton
  guardar cuando las opciones son automaticas lo cual no deberia de ser»)
- **Fecha del reporte:** 2026-11-23
- **Prioridad:** Baja
- **Descripción:** el reporte indica que Configuración muestra un botón Guardar
  aunque el guardado es automático.
- **Pasos para reproducir:** abrir Configuración y buscar el botón.
- **Estado:** Cerrado sin cambios de UI: no se reproduce en el código actual.
  La pestaña Configuración no instala barra de acciones (`init_config_tab` no
  llama a `install_page_action_bar`) y `SettingsPanel` no contiene ningún botón
  «Guardar»; el guardado es automático y «Restablecer» es una tarjeta. Se deja
  una prueba de regresión para que el botón no reaparezca.
- **Solución aplicada:** ninguna en la UI; guardia
  `test_config_page_has_no_save_button`.
- **Pruebas:** `tests/test_settings_save_guards.py`.
- **Commit:** vigésimo sexto ciclo.
- **Fecha de resolución:** 2026-11-23 (verificado como no reproducido).

## R-2e7c4a91 — La preferencia de editor se guardaba dentro de `lib/` y un JSON no-objeto rompía «Abrir con»

- **Usuario:** auditoría interna del ciclo de mantenimiento (sin reporte externo)
- **Fecha del reporte:** 2026-11-23
- **Prioridad:** Media
- **Descripción:** `lib/.walkcube/editorDetector.py` resolvía `settings.json`
  con `Path(__file__).resolve().parent.parent`, que desde `lib/.walkcube/`
  apunta a `lib/config/settings.json`. La opción «Siempre» de «Abrir con»
  escribía allí, fuera de la configuración canónica, y en un ejecutable
  congelado el archivo caía en el bundle temporal y se perdía al cerrar.
  Además, `get_default_editor()` hacía `.get()` sobre el JSON sin comprobar el
  tipo (un archivo con `[]` lanzaba `AttributeError`) y
  `save_default_editor()` asignaba una clave sobre una lista (`TypeError`).
- **Pasos para reproducir:** elegir «Siempre» en «Abrir con» y comprobar que
  aparece `lib/config/settings.json`; después escribir `[]` en ese archivo y
  abrir de nuevo «Abrir con» (traceback `AttributeError`).
- **Estado:** Resuelto.
- **Solución aplicada:** la ruta pasa a `<raíz de la app>/config/settings.json`
  (o junto a `sys.executable` si está congelado). Las dos funciones exigen un
  objeto JSON, degradan a `{}` o `None` y tratan `OSError` al crear o escribir
  como preferencia no guardada, sin romper el diálogo.
- **Pruebas:** `tests/test_config_and_removeme_robustness.py` (ruta normal,
  ruta congelada, cinco formas no-objeto, reescritura y conservación de claves).
- **Commit:** vigésimo séptimo ciclo (2026-11-23).
- **Fecha de resolución:** 2026-11-23.

## R-8b4d1f62 — El removedor generado revienta si `install.json` no es un objeto

- **Usuario:** auditoría interna del ciclo de mantenimiento (sin reporte externo)
- **Fecha del reporte:** 2026-11-23
- **Prioridad:** Media
- **Descripción:** el stub `removeme.py` generado por `build_removeme()` leía
  `install.json` y hacía `data.get("shortcuts")` sin validar el tipo. Un
  registro corrupto (`[]`, `"texto"`, `5` o `{"shortcuts": 5}`) lanzaba
  `AttributeError`/`TypeError` y la desinstalación se detenía con traceback,
  dejando la aplicación instalada.
- **Pasos para reproducir:** generar el removedor, escribir `[]` en
  `install.json` y ejecutar `removeme.py --silent` (código 1 y rastro de
  `AttributeError`).
- **Estado:** Resuelto.
- **Solución aplicada:** `_shortcuts()` sólo acepta un objeto JSON con una
  lista en `shortcuts`; cualquier otra forma cae a los accesos directos
  incrustados y la desinstalación continúa.
- **Pruebas:** `tests/test_config_and_removeme_robustness.py` (seis formas
  corruptas y un acceso directo real que sigue borrándose).
- **Commit:** vigésimo séptimo ciclo (2026-11-23).
- **Fecha de resolución:** 2026-11-23.

## R-5c9a3e27 — Metadatos `.mexf` ilegibles abortaban el diálogo de instalación

- **Usuario:** auditoría interna del ciclo de mantenimiento (sin reporte externo)
- **Fecha del reporte:** 2026-11-23
- **Prioridad:** Baja
- **Descripción:** la vista previa de `showInstallMexfDialog()` envolvía la
  lectura en `except (OSError, KeyError, ET.ParseError)`, que no incluye
  `json.JSONDecodeError` ni `AttributeError`. Un `.mexf` que no fuera JSON u
  objeto escapaba al `except` exterior y cerraba el diálogo entero con
  «Error showing install-MEXF dialog», en vez de abrirlo sin detalles.
- **Pasos para reproducir:** elegir «Instalar extensiones MEXF» y seleccionar
  un archivo con texto no JSON.
- **Estado:** Resuelto.
- **Solución aplicada:** `_mexf_preview_metadata()` lee y valida el objeto una
  sola vez y devuelve `None` cuando no se puede; el diálogo se abre igual y
  omite el bloque de detalles.
- **Pruebas:** `tests/test_config_and_removeme_robustness.py` (texto no JSON,
  lista, cadena, número, archivo ausente y objeto válido).
- **Commit:** vigésimo séptimo ciclo (2026-11-23).
- **Fecha de resolución:** 2026-11-23.

## R-3b6f9d24 — Una caché de fuentes de solo lectura tumbaba el CLI y la interfaz

- **Usuario:** auditoría interna del ciclo de mantenimiento (sin reporte externo)
- **Fecha del reporte:** 2026-11-23
- **Prioridad:** Media
- **Descripción:** `cached_path()` llamaba a `font_cache_dir()`, que creaba
  `data/fonts` con `mkdir()`. En una instalación de solo lectura (Program Files
  en Windows, `/usr` en Linux, `data` sin permisos) `--list-fonts` y
  `--download-fonts` terminaban en `PermissionError` con traceback, y el botón
  de descarga de Configuración abortaba la aplicación: el `OSError` subía desde
  un slot de Qt y Python cerraba el proceso.
- **Pasos para reproducir:** con `data/fonts` inexistente y `data` sin permiso
  de escritura, ejecutar `python packagemaker.py --list-fonts` (antes:
  traceback, código 1) o pulsar «Descargar fuentes» en Configuración.
- **Causa raíz:** las rutas de **lectura** del estado de la caché creaban el
  directorio como efecto secundario y no traducían `OSError`; la escritura del
  aviso de licencias tampoco.
- **Estado:** Resuelto.
- **Solución aplicada:** `font_cache_dir(create=False)` y
  `cached_path(..., create=False)` permiten consultar sin tocar el disco;
  `is_cached()`, `verify_file()`, `available_fonts_report()`,
  `load_cached_fonts()` y `ensure_fonts()` degradan a «ausente» con `OSError`;
  `download_font()` comprueba la escritura antes de descargar y devuelve
  `None`; `write_license_notice()` devuelve `None`; el CLI avisa
  `[WARN] No se pudo escribir el aviso de licencias` y el slot
  `_download_ui_fonts()` captura `OSError` y lo muestra en la etiqueta de
  estado en vez de abortar.
- **Pruebas:** `tests/test_font_cache_robustness.py` (9 casos, incluido el slot
  de Configuración y el CLI con la caché bloqueada).
- **Commit:** vigésimo octavo ciclo (2026-11-23).
- **Fecha de resolución:** 2026-11-23.

## R-9f4c2a71 — Caché de avatares no escribible y respuestas de GitHub no-JSON

- **Usuario:** auditoría interna del ciclo de mantenimiento (sin reporte externo)
- **Fecha del reporte:** 2026-11-23
- **Prioridad:** Baja
- **Descripción:** dos caminos del inicio de sesión de GitHub escapaban con
  excepciones crudas: (1) `cache_avatar()` escribía en `data/avatars` sin
  `try/except`, así que un `data` de solo lectura lanzaba `OSError` dentro del
  slot de login y podía cerrar la aplicación; `load_cached_avatar()` tampoco
  protegía la creación del directorio, y se llama al refrescar la tarjeta del
  sidebar al arrancar. (2) `_request()` devolvía `json.loads(...)` sin validar
  la forma: un portal cautivo que responde HTML con código 200 producía el
  mensaje engañoso «el token contiene caracteres no válidos», y un JSON que no
  fuera objeto lanzaba `AttributeError` en `_profile_from_payload()`.
- **Pasos para reproducir:** con `data` sin permiso de escritura, iniciar
  sesión de GitHub (antes: aborto del proceso al cachear el avatar). Con un
  proxy que responde `200 <html>…</html>`, llamar a `_request()` (antes:
  mensaje erróneo) o devolver `["octocat"]` desde `/user` (antes:
  `AttributeError`).
- **Estado:** Resuelto.
- **Solución aplicada:** `cache_avatar()` y `load_cached_avatar()` capturan
  `OSError` y devuelven `None` (el avatar es opcional); `_request()` separa la
  lectura del cuerpo del parseo y traduce el fallo a «GitHub devolvió una
  respuesta que no es JSON»; `_profile_from_payload()` exige un objeto.
- **Pruebas:** `tests/test_github_identity.py` (3 casos nuevos: cuerpo no-JSON,
  carga no-objeto y caché de avatares bloqueada).
- **Commit:** vigésimo octavo ciclo (2026-11-23).
- **Fecha de resolución:** 2026-11-23.

## R-4a7c2e91 — `PythonPortableManager` reventaba con `data/pmCodeEditor` no escribible

- **Usuario:** auditoría interna del ciclo de mantenimiento (sin reporte externo)
- **Fecha del reporte:** 2026-11-23
- **Prioridad:** Alta (impide arrancar el editor y sus diálogos)
- **Descripción:** `PythonPortableManager.__init__` creaba `data/pmCodeEditor` y
  `data/pmCodeEditor/packages` con `mkdir()` sin `try/except`. El repositorio no
  incluye `packages`, así que en una instalación de solo lectura (Program Files,
  AppImage, `/opt`) la construcción del gestor lanzaba `PermissionError`.
  `get_python_manager()` se llama en `pmCodeEditor.main()` a través de
  `resolve_python_path()`, y también desde `PythonSetupDialog`,
  `InterpreterConfigDialog` y el desplegable de intérpretes del editor: el
  primero sale con traceback y los demás lanzan la excepción dentro de un slot
  de Qt. `_discover_installations()` iteraba `python_dir` sin proteger
  `iterdir()`, `_save_config()` escribía sin capturar `OSError`, y
  `get_installed_versions()`/`get_installation_status()` llamaban a
  `Path.exists()` sobre una ruta potencialmente inaccesible.
- **Pasos para reproducir:** con `data` sin permiso de escritura (o
  `PythonPortableManager(base_dir=<carpeta no escribible>)`), abrir el editor
  (`python pmCodeEditor.py`) o el diálogo de intérpretes: antes,
  `PermissionError: … /packages`.
- **Causa raíz:** rutas de datos opcionales tratadas como obligatorias y
  ausencia de traducción de `OSError` en un componente que se construye al
  arrancar y dentro de slots de Qt.
- **Estado:** Resuelto.
- **Solución aplicada:** `_ensure_directories()` captura `OSError` y sigue en
  modo degradado; `_load_config()` usa `is_file()` dentro del `try`;
  `_discover_installations()` protege `iterdir()`/`is_dir()`;
  `_save_config()` devuelve `False` y avisa con `[WARN]` cuando no puede
  escribir; `_is_file()` centraliza la comprobación de `python_exe`;
  `_get_dir_size()` ignora entradas inaccesibles e `install_version()` informa
  del fallo al preparar el destino en vez de lanzarlo.
- **Pruebas:** `tests/test_readonly_data_dir_robustness.py::TestPortableManagerReadOnlyDataDir`
  (3 casos; los 3 fallan con el código anterior).
- **Commit:** vigésimo noveno ciclo (2026-11-23).
- **Fecha de resolución:** 2026-11-23.

## R-8f1d3b62 — Guardar `editor_config.json` abortaba con `data` de solo lectura

- **Usuario:** auditoría interna del ciclo de mantenimiento (sin reporte externo)
- **Fecha del reporte:** 2026-11-23
- **Prioridad:** Media
- **Descripción:** `DashboardWindow.save_config()` y
  `EditorWindow._save_editor_config()` hacían `mkdir()` + `open(..., "w")` sin
  `try/except`. `save_config()` se invoca al añadir un proyecto reciente
  (`_add_to_recent`) y al aceptar el diálogo de intérpretes; el segundo, tras
  el mismo diálogo. Con `data/pmCodeEditor` de solo lectura, el `OSError`
  subía desde un slot de Qt y podía cerrar el proceso. Las lecturas
  (`load_config()` y `_load_editor_config()`) comprobaban `exists()` fuera del
  `try`, que en Python 3.13 propaga `PermissionError` si el padre no es
  accesible.
- **Pasos para reproducir:** con `data` sin permiso de escritura, abrir un
  proyecto en el panel del editor o cambiar el intérprete: antes, `OSError` en
  el slot. En pruebas, apuntar `EDITOR_CONFIG_PATH` bajo un archivo
  (`mkdir()` lanza `NotADirectoryError`).
- **Estado:** Resuelto.
- **Solución aplicada:** ambos guardados capturan `OSError`, avisan con
  `[WARN]` y devuelven `False`; las dos lecturas usan `is_file()` dentro del
  `try`.
- **Pruebas:** `tests/test_readonly_data_dir_robustness.py::TestEditorConfigReadOnlyDataDir`
  (3 casos; 2 fallan con el código anterior).
- **Commit:** vigésimo noveno ciclo (2026-11-23).
- **Fecha de resolución:** 2026-11-23.

## R-9a4c1e27 — La TUI cae con rutas sin permisos

- **Usuario:** auditoría interna del ciclo de mantenimiento (sin reporte externo)
- **Fecha del reporte:** 2026-11-23
- **Prioridad:** Media
- **Descripción:** las pantallas de la TUI comprobaban las rutas escritas por
  el usuario con `Path.exists()` (`_screen_build`, `_screen_moonfix`,
  `_project_actions`, `_show_details_xml`, `_get_version`). En Python 3.13
  `Path.exists()` propaga `PermissionError` cuando el directorio padre no es
  accesible, así que una carpeta bloqueada terminaba en traceback y cerraba la
  TUI. `_list_projects()` ordenaba además con `p.stat()` fuera de cualquier
  `try`, de modo que una entrada que desaparecía o no se podía consultar
  abortaba el listado.
- **Pasos para reproducir:** `chmod 000` sobre un proyecto (o sobre su carpeta
  padre) y abrir «Ver details.xml», «Construir paquete» o «MoonFix» con esa
  ruta; antes, `PermissionError` con traceback. En pruebas, patchear
  `list_projects` para devolver una entrada cuyo `stat()` falla.
- **Estado:** Resuelto.
- **Solución aplicada:** nuevo `_safe_exists()` en `lib/tui.py` que traduce
  `OSError` a `False`; todas las comprobaciones de rutas del usuario lo usan.
  `_list_projects()` ignora las entradas cuyo `stat()` falla en vez de
  propagar el error.
- **Pruebas:** `tests/test_tui_unreadable_paths.py` (7 casos; los 7 fallan con
  el código anterior).
- **Commit:** trigésimo ciclo (2026-11-23).
- **Fecha de resolución:** 2026-11-23.

## R-4d8a6c12 — El arranque cae si `data/` no se puede crear o leer

- **Usuario:** auditoría interna del ciclo de mantenimiento (sin reporte externo)
- **Fecha del reporte:** 2026-11-23
- **Prioridad:** Alta
- **Descripción:** `_data_dir()` creaba la carpeta con `mkdir()` sin
  `try/except`, `PMDataStore.load()` comprobaba el archivo con
  `Path.is_file()` y `load_merged_app_config()` hacía lo propio con
  `config/settings.json`. En una instalación de solo lectura sin `data/`, o con
  `data/`/`config/` ilegibles, la primera llamada a `get_pm_data()` —que ocurre
  al resolver el acento o el idioma— lanzaba `PermissionError` y abortaba el
  arranque.
- **Pasos para reproducir:** `chmod 555` sobre la raíz de la app sin carpeta
  `data/` y ejecutar `python -c "from lib import pm_data; pm_data.PMDataStore()"`;
  o `chmod 000` sobre `data/` y repetir.
- **Estado:** Resuelto.
- **Solución aplicada:** `_data_dir()` degrada con `except OSError` y devuelve
  la ruta igualmente; `load()`, `_detect_app_version()` y
  `load_merged_app_config()` usan `path_is_file()`, que traduce `OSError` a
  `False`. `save()` ya devolvía `False` sin lanzar.
- **Pruebas:** `tests/test_pm_data_readonly_startup.py` (4 casos; 3 fallan con
  el código anterior).
- **Commit:** trigésimo primer ciclo (2026-11-23).
- **Fecha de resolución:** 2026-11-23.

## R-9e3b7a51 — Las acciones de GUI caen con rutas sin permisos

- **Usuario:** auditoría interna del ciclo de mantenimiento (sin reporte externo)
- **Fecha del reporte:** 2026-11-23
- **Prioridad:** Media
- **Descripción:** tres acciones de ventana comprobaban rutas con
  `Path.exists()`/`is_file()`/`mkdir()`/`read_text()` dentro de un slot de Qt:
  `NewProjectWizard.create_project()` (carpeta base ilegible),
  `IflappIdePanel._on_script_selected()` (guion ilegible) y
  `ProjectConfig.__init__()`/`get_config()` (base de solo lectura). En Python
  3.13 esas llamadas propagan `PermissionError`, así que el usuario veía un
  traceback en lugar del aviso.
- **Pasos para reproducir:** `chmod 000` sobre la carpeta base del asistente o
  sobre un guion del IDE y ejecutar la acción; antes, `PermissionError`.
- **Estado:** Resuelto.
- **Solución aplicada:** `path_exists()` en el asistente (también en las
  carpetas por defecto de los diálogos); `_on_script_selected()` lee dentro de
  `try/except OSError` y muestra `iflapp_ide.load_failed`; `ProjectConfig`
  protege `mkdir()` e `is_file()` y devuelve `{}` cuando la base es
  inaccesible.
- **Pruebas:** `tests/test_gui_unreadable_paths.py` (3 casos; los 3 fallan con
  el código anterior).
- **Commit:** trigésimo primer ciclo (2026-11-23).
- **Fecha de resolución:** 2026-11-23.

## R-6a2d8f43 — Termux sin almacenamiento compartido se queda sin salida

- **Usuario:** auditoría interna del ciclo de mantenimiento (sin reporte externo)
- **Fecha del reporte:** 2026-11-23
- **Prioridad:** Media
- **Descripción:** `compile_output_directory()` comprobaba
  `~/storage/downloads` con `Path.is_dir()`. En Termux sin
  `termux-setup-storage` ese camino está bajo un padre inaccesible y Python
  3.13 propaga `PermissionError`; el CLI abortaba en lugar de usar
  `/storage/emulated/0/Download`.
- **Pasos para reproducir:** `chmod 000` sobre el padre de
  `~/storage/downloads` y llamar `compile_output_directory("termux")`.
- **Estado:** Resuelto.
- **Solución aplicada:** la comprobación usa `os.path.isdir()`, que traduce
  cualquier `OSError` a `False`; se mantiene `/storage/emulated/0/Download`
  como respaldo.
- **Pruebas:** `tests/test_platform_detect_storage.py` (2 casos; 1 falla con el
  código anterior).
- **Commit:** trigésimo primer ciclo (2026-11-23).
- **Fecha de resolución:** 2026-11-23.

## R-7e4c1a92 — El arranque cae si `data/` impide leer la caché de sesión

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-23
- **Descripción:** `session_cache.load_session()` comprobaba
  `data/session.cache` con `Path.is_file()` fuera de cualquier `try`. En
  Python 3.13 esa llamada propaga `PermissionError` cuando `data/` no es
  accesible. `load_session()` se invoca en el arranque desde
  `github_identity.restore_cached_session()`, `has_cached_session()` y
  `load_token()`, dentro de `start_session_gate()`; el fallo dejaba el arranque
  sin llegar a decidir entre landing o IDE.
- **Pasos para reproducir:** `chmod 000 data/` con `data/session.cache`
  existente y llamar `session_cache.load_session()` (o arrancar la app).
- **Estado:** Resuelto.
- **Prioridad:** Alta (rompe el arranque).
- **Solución aplicada:** la comprobación y la lectura de la caché se envuelven
  en `try/except OSError`; sin caché legible se devuelve `None` y el arranque
  continúa con `pm.data` o con el formulario de login.
- **Pruebas:** `tests/test_unreadable_config_paths.py`
  (`test_session_cache_ignores_unreadable_data_dir`).
- **Commit:** trigésimo segundo ciclo (2026-11-23).
- **Fecha de resolución:** 2026-11-23.

## R-2d8b6f31 — El build lanza traceback con `config/` del proyecto ilegible

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-23
- **Descripción:** `FlangCompiler.__init__` llama a `_load_scripts_to_compile()`,
  que comprobaba `config/settings.json` con `Path.is_file()` sin protección. Con
  el directorio `config/` del proyecto sin permisos, `compile` y `--buildthis`
  terminaban en `PermissionError` con traceback (el CLI construye el compilador
  fuera de un `try`). En la GUI lo absorbía el `except` de la QThread, pero el
  mensaje era «Error inesperado».
- **Pasos para reproducir:** `chmod 000 PROYECTO/config && python
  packagemaker.py --buildthis PROYECTO --compiler zipapp --no-sandbox`.
- **Estado:** Resuelto.
- **Prioridad:** Alta (rompe la compilación headless).
- **Solución aplicada:** la comprobación se envuelve en `try/except OSError`; se
  registra `last_error` («No se pudo leer config/settings.json: …») y se
  devuelve una lista vacía, igual que cuando el archivo existe pero no se puede
  leer. El CLI responde `[ERROR] …` con código 1.
- **Pruebas:** `tests/test_unreadable_config_paths.py`
  (`test_flang_compiler_reports_unreadable_project_config`).
- **Commit:** trigésimo segundo ciclo (2026-11-23).
- **Fecha de resolución:** 2026-11-23.

## R-9a5c3e74 — «Abrir con» cae con `config/` de la aplicación ilegible

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-23
- **Descripción:** `editorDetector.get_default_editor()` y
  `save_default_editor()` comprobaban `config/settings.json` de la aplicación
  con `Path.is_file()` sin protección. Con `config/` ilegible, abrir el diálogo
  «Abrir con» o guardar la preferencia lanzaba `PermissionError` dentro de un
  slot de Qt.
- **Pasos para reproducir:** `chmod 000 config/` junto al ejecutable y llamar
  `get_default_editor()`/`save_default_editor("vim")`.
- **Estado:** Resuelto.
- **Prioridad:** Media.
- **Solución aplicada:** ambas comprobaciones se envuelven en `try/except
  OSError`; `get_default_editor()` devuelve `None` y `save_default_editor()`
  omite la lectura previa y deja que el `except OSError` de la escritura avise
  sin romper el slot.
- **Pruebas:** `tests/test_unreadable_config_paths.py`
  (`test_editor_detector_ignores_unreadable_config_dir`).
- **Commit:** trigésimo segundo ciclo (2026-11-23).
- **Fecha de resolución:** 2026-11-23.

## R-4e9c1a73 — el IDE `.iflapp` cae al compilar un proyecto ilegible

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-23
- **Descripción:** `IflappIdePanel.run_compile()` llamaba a
  `iflapp_ide.compile_project()` sin proteger el `OSError` que produce
  `scan_project()` al leer `details.xml` o al crear `build/` cuando el proyecto
  dejó de ser legible o escribible. El método está conectado a
  `btn_compile.clicked`; en PyQt6 una excepción no controlada en un slot
  termina el proceso.
- **Pasos para reproducir:** abrir un proyecto en el IDE `.iflapp`, aplicar
  `chmod 000` a la carpeta del proyecto y pulsar «Compilar». Se obtenía
  `PermissionError: [Errno 13] …/details.xml`.
- **Estado:** Resuelto.
- **Prioridad:** Alta.
- **Solución aplicada:** la llamada a `compile_project()` se envuelve en
  `try/except OSError`; el error se escribe en la consola y en la barra de
  estado y el método devuelve `False` sin cerrar la aplicación.
- **Pruebas:** `tests/test_gui_unreadable_paths.py`
  (`test_ide_panel_reports_unreadable_project_on_compile`).
- **Commit:** trigésimo tercer ciclo (2026-11-23).
- **Fecha de resolución:** 2026-11-23.

## R-7d2f8b14 — MoonFix cae con un proyecto de solo lectura

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-23
- **Descripción:** `MoonFixWizard.go_next()` llamaba a `apply_project_fixes()`
  desde un slot; esa función delega en `repair_project_from_templates()`, que
  crea carpetas y escribe `details.xml` y las plantillas. Con la carpeta del
  proyecto sin permiso de escritura, `Path.mkdir()`/`write_text()` lanzaban
  `PermissionError` y el wizard cerraba la aplicación en lugar de avisar.
- **Pasos para reproducir:** abrir MoonFix sobre un proyecto, aplicar
  `chmod 500` a su carpeta y pulsar «Siguiente». Se obtenía
  `PermissionError: [Errno 13] …/app`.
- **Estado:** Resuelto.
- **Prioridad:** Alta.
- **Solución aplicada:** `apply_project_fixes()` ahora devuelve `bool` y
  envuelve la reparación en `try/except (OSError, ValueError)`, mostrando el
  error con `LeviathanDialog`; `go_next()` no avanza de página si la reparación
  falla.
- **Pruebas:** `tests/test_gui_unreadable_paths.py`
  (`test_moonfix_reports_unwritable_project`).
- **Commit:** trigésimo tercer ciclo (2026-11-23).
- **Fecha de resolución:** 2026-11-23.

## R-6b3e9c52 — el splash del paquete no arranca con un proyecto sin permisos

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-23
- **Descripción:** `splash_bootloader._resolve_icon()` comprobaba los iconos
  candidatos con `Path.is_file()` y resolvía `Path.cwd()` sin protección. El
  bootloader se ejecuta antes de construir la ventana del programa compilado,
  así que un directorio de trabajo o un proyecto sin permisos lanzaba
  `PermissionError` antes de mostrar el splash.
- **Pasos para reproducir:** llamar a
  `SplashBootloader().arm("<proyecto>/main.py")` con la carpeta del proyecto en
  `chmod 000` (y un `cwd` sin iconos). Se obtenía
  `PermissionError: [Errno 13] …/app/app-icon.ico`.
- **Estado:** Resuelto.
- **Prioridad:** Media.
- **Solución aplicada:** `_resolve_icon()` envuelve `Path.resolve()`/`Path.cwd()`
  en `try/except OSError` y cada `is_file()` en su propio `try`; si no hay
  icono legible devuelve `None` y el splash usa el acento del sistema. El
  módulo sigue siendo autocontenido (solo stdlib + PyQt6).
- **Pruebas:** `tests/test_splash_bootloader_injection.py`
  (`test_bootloader_arm_tolerates_unreadable_project`).
- **Commit:** trigésimo tercer ciclo (2026-11-23).
- **Fecha de resolución:** 2026-11-23.

## R-4b9e2c71 — El compilador `.mexf` filtra `PermissionError` crudo con una raíz o una carpeta `app/` ilegible

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte externo)
- **Fecha del reporte:** 2026-11-23
- **Descripción:** el ciclo de R-6d2f8a41 protegió el parseo de `details.xml`
  y de los `.mexf`, pero dejó sin traducir las comprobaciones de existencia. En
  Python 3.13 `Path.is_file()`/`is_dir()` propagan `PermissionError` cuando el
  directorio padre no es accesible, así que `read_project_details()`,
  `compile_mexf_project()` y `MexfCompiler.run()` dejaban escapar
  `PermissionError` en lugar de `MexfCompileError`. `MexfCompiler.run()` además
  incumplía su contrato (debe devolver `None` y rellenar `last_error`) y el paso
  opcional `.mexf` del build abortaba el `FlangCompiler` completo en vez de
  omitirse. `_find_project_icon()` leía los iconos sin protección: una carpeta
  `app/` ilegible abortaba el empaquetado aunque el icono es opcional.
- **Pasos para reproducir:** crear un proyecto con `details.xml` y `.mexf/`,
  `chmod 000` sobre la raíz y ejecutar `read_project_details(root)`,
  `MexfCompiler(root).run()` y `compile_mexf_project(root)`; con la raíz legible
  pero `app/` en `chmod 000`, `compile_mexf_project(root)` también fallaba.
- **Estado:** Resuelto.
- **Prioridad:** Media (mensaje de error crudo y contrato roto; el CLI ya
  envolvía `OSError`, pero el build abortaba el paso `.mexf` en vez de omitirlo).
- **Solución aplicada:** `read_project_details()` envuelve `is_file()` y lanza
  `MexfCompileError`; `_find_project_icon()` tolera `OSError` y devuelve `None`;
  `MexfCompiler.run()` protege `is_dir()` y captura `(MexfCompileError, OSError)`
  devolviendo `None`; `BuildThread._compile_mexf_if_present()` protege el
  `is_dir()` del `.mexf/` y lo omite con un `[WARN]`.
- **Pruebas:** `tests/test_unreadable_paths.py` —
  `test_mexf_read_details_converts_permission_error`,
  `test_mexf_compiler_run_skips_unreadable_root`,
  `test_mexf_compile_project_converts_permission_error`,
  `test_buildthread_mexf_step_skips_unreadable_dir` y
  `test_mexf_compile_without_readable_icon_still_builds` (las 5 fallan con el
  código anterior).
- **Commit:** se registra en el cierre del trigésimo cuarto ciclo.
- **Fecha de resolución:** 2026-11-23.

## R-3f7c1a94 — Una carpeta de accesos directos no escribible aborta `--install-asksome`

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** `create_shortcuts()` documenta que devuelve sólo los accesos
  directos que se pudieron crear, pero `_write_linux_desktop()` y
  `_write_windows_shortcut()` sólo protegían `mkdir()`. Si la carpeta de
  destinos existe y no es escribible (`~/.local/share/applications` de una
  instalación del sistema, HOME inmutable o contenedor), `entry.write_text()`
  lanzaba `PermissionError` y abortaba `install_asksome()` **después** de haber
  extraído el payload: la instalación quedaba a medias y el CLI moría con un
  traceback en vez de un `[ERROR]`.
- **Pasos para reproducir:** instalar un `.asksome` con
  `shortcut_dirs=[<carpeta en chmod 555>]`; con el CLI,
  `HOME=<tmp>/home` con `<tmp>/home/.local/share/applications` en `chmod 555` y
  `python packagemaker.py --install-asksome demo.asksome --install-root <raíz>`.
- **Estado:** Resuelto.
- **Prioridad:** Media (instalación a medias y traceback; los accesos directos
  son opcionales).
- **Solución aplicada:** ambas funciones envuelven la escritura y el `chmod` del
  acceso en `try/except OSError` y devuelven `None`, de modo que
  `create_shortcuts()` sigue con el resto de carpetas.
- **Pruebas:** `tests/test_mexf_asksome.py` —
  `test_install_asksome_skips_unwritable_shortcut_dir`.
- **Commit:** se registra en el cierre del trigésimo quinto ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-6b2e9d47 — `uninstall_asksome` filtra `PermissionError` y `OSError` crudos

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** `uninstall_asksome()` usaba `target.is_dir()`,
  `record_path.is_file()`, `shortcut_path.is_file()`/`unlink()` y
  `shutil.rmtree()` sin protección. En Python 3.13 los `is_*()` propagan
  `PermissionError` cuando el directorio padre no es accesible, y `rmtree`
  falla con ficheros en uso (Windows) o directorios sin permiso de escritura.
  El CLI sólo captura `AsksomeInstallError`, así que
  `--uninstall-asksome` terminaba en traceback en lugar de informar.
- **Pasos para reproducir:** instalar un `.asksome`, poner la raíz de
  instalación en `chmod 000` (o un subdirectorio con un fichero dentro en
  `chmod 555`) y ejecutar `uninstall_asksome("demo.app", raíz)` o
  `python packagemaker.py --uninstall-asksome demo.app --install-root raíz`.
- **Estado:** Resuelto.
- **Prioridad:** Media (mensaje crudo, sin pérdida de datos: la app sigue
  instalada).
- **Solución aplicada:** `target.is_dir()` se traduce a `AsksomeInstallError`;
  el registro se comprueba con `path_is_file()`; cada acceso directo se borra
  dentro de `try/except OSError` (un acceso bloqueado no impide purgar la
  instalación); el árbol se borra con `lib.file_ops.remove_tree()` y, si
  sobrevive, se lanza `AsksomeInstallError` con la ruta. `build_removeme()`
  traduce también los `OSError` de sus dos escrituras.
- **Pruebas:** `tests/test_mexf_asksome.py` —
  `test_uninstall_asksome_reports_unreadable_root`,
  `test_uninstall_asksome_skips_blocked_shortcut`,
  `test_uninstall_asksome_reports_blocked_tree` y
  `test_install_asksome_reports_unreadable_artifact`.
- **Commit:** se registra en el cierre del trigésimo quinto ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-8c4a1f62 — `remove_tree` informa de un borrado que no ocurrió

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** `remove_tree()` promete devolver `True` sólo si el árbol ya
  no existe, pero `shutil.rmtree()` con `onexc` **no lanza**: si el callback
  `_clear_readonly()` consumía el error, `rmtree` continuaba y terminaba sin
  excepción. `_retry()` nunca veía el fallo (los reintentos de `WinError 32` de
  R-4a1e7b93 no llegaban a ejecutarse) y `remove_tree()` devolvía `True` con el
  árbol intacto. Los llamadores del build daban la limpieza por buena y podían
  reutilizar artefactos obsoletos.
- **Pasos para reproducir:** crear `<tmp>/locked/f.txt`, poner `locked` en
  `chmod 555` y llamar a `remove_tree(locked)`; devolvía `True` con el
  directorio todavía presente.
- **Estado:** Resuelto.
- **Prioridad:** Alta (contrato roto en la limpieza del build; podía dejar
  restos entre compilaciones).
- **Solución aplicada:** `_clear_readonly()` ya no se traga el error: si el
  reintento falla, la excepción llega a `_retry()` (que espera ante bloqueos
  reales) y el `chmod` conserva los bits originales (`mode | S_IWRITE`) en vez
  de fijar `0o600` sobre un directorio. `remove_tree()` confirma el resultado
  comprobando que el árbol ya no existe antes de devolver `True`.
- **Pruebas:** `tests/test_engine_isolation.py` —
  `test_remove_tree_reports_a_tree_that_survived` (falla con el código
  anterior).
- **Commit:** se registra en el cierre del trigésimo quinto ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-4a7e2c91 — `create` lanza traceback con una carpeta base sin permisos

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** el subcomando headless `create` llamaba a
  `create_project_from_templates()` sin proteger el sistema de archivos. Con
  `BASE_DIR` en una carpeta sin permiso de escritura (HOME inmutable,
  almacenamiento desmontado, ruta bajo un archivo), `project_path.mkdir()`
  lanzaba `PermissionError` y el CLI terminaba con traceback en vez de un
  mensaje. La GUI ya lo trataba, pero el CLI quedaba fuera.
- **Pasos para reproducir:** fijar `base_dir` en `data/pm.data` a una carpeta
  `chmod 555` y ejecutar
  `python packagemaker.py create --name Demo --shortname demo --publisher Influent --headless`.
- **Estado:** Resuelto.
- **Prioridad:** Media (robustez del CLI; no había pérdida de datos).
- **Solución aplicada:** la creación y la copia del icono por defecto van dentro
  de un `try/except OSError` que imprime
  `[ERROR] No se pudo crear el proyecto en …` y sale con código 1.
- **Pruebas:** `tests/test_unreadable_paths.py` —
  `test_create_project_reports_unwritable_base_dir` (falla con el código
  anterior).
- **Commit:** se registra en el cierre del trigésimo sexto ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-6c9d3f52 — `moonfix`/`repair` lanzan traceback con un proyecto de solo lectura

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** el manejador headless de `repair_project` sólo traducía
  `ValueError`. `repair_project_from_templates()` crea las subcarpetas del
  contrato (`docs/`, marcadores `.container`, etc.); si al proyecto le faltaba
  una carpeta y la raíz era de solo lectura, `folder_path.mkdir()` lanzaba
  `PermissionError` y `moonfix` moría con traceback. El asistente MoonFix de la
  GUI ya se había corregido (R-7d2f8b14); el CLI no.
- **Pasos para reproducir:** crear un proyecto canónico, borrar `docs/`, poner la
  carpeta del proyecto en `chmod 555` y ejecutar
  `python packagemaker.py moonfix --name Demo --shortname demo --publisher Influent`.
- **Estado:** Resuelto.
- **Prioridad:** Media (robustez del CLI; la GUI ya estaba protegida).
- **Solución aplicada:** se añade `except OSError` junto al de `ValueError`, con
  el mensaje `[ERROR] No se pudo reparar el proyecto …` y salida 1.
- **Pruebas:** `tests/test_unreadable_paths.py` —
  `test_repair_project_reports_unreadable_project` (falla con el código
  anterior).
- **Commit:** se registra en el cierre del trigésimo sexto ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-8e2b7d64 — `compile`/`--buildthis` lanzan traceback con `dist/` bloqueado

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** los bloques headless de `compile_project` y `buildthis` sólo
  tenían `try/finally`, sin `except`. Un proyecto de solo lectura hacía que
  `FlangCompiler._compile_binary()` fallara en `dist_dir.mkdir()` con
  `PermissionError`, que escapaba del CLI como traceback. En la GUI la QThread
  lo capturaba con un mensaje genérico («Error inesperado»), sin indicar el
  directorio ni la causa.
- **Pasos para reproducir:** poner el proyecto en `chmod -R a-w` y ejecutar
  `python packagemaker.py --buildthis <proyecto> --compiler zipapp --no-sandbox`.
- **Estado:** Resuelto.
- **Prioridad:** Alta (la compilación es la acción principal; el fallo llegaba
  sin mensaje útil).
- **Solución aplicada:** `_compile_binary()` protege la preparación del árbol
  (`_prepare_pyinstaller_data_dirs()`), la lectura de `details.xml`, `lib/` y la
  creación de `dist/`/temporales; devuelve `False` con `last_error` legible. Los
  dos bloques del CLI añaden `except OSError` que imprime
  `[ERROR] La compilación falló por un problema del sistema de archivos: …` y
  sale con código 1. El camino feliz no cambia.
- **Pruebas:** `tests/test_unreadable_paths.py` —
  `test_compile_reports_filesystem_error_without_traceback[buildthis]`,
  `[compile_project]` y `test_compile_binary_translates_unwritable_build_dir`
  (las tres fallan con el código anterior).
- **Commit:** se registra en el cierre del trigésimo sexto ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-6f4b8a92 — Empaquetar un proyecto inaccesible aborta la GUI

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** al pulsar BlindCube sobre un proyecto cuyo directorio padre
  no es accesible, la excepción escapaba antes del `try` del build. En el slot
  del botón, `_ask_env_injection()` llamaba a `find_env_file()`, que comprobaba
  `.env` con `Path.is_file()` y propagaba `PermissionError`; en la QThread,
  `BuildThread.run()` hacía `repo_path.exists()` (y la preflight)
  **fuera** del `try` que traduce errores. PyQt6 aborta el proceso ante una
  excepción no capturada en un slot o en `QThread.run`, así que la aplicación
  moría sin mensaje. `env_injection_dialog.app_icon_for()` tenía la misma
  comprobación sin proteger.
- **Pasos para reproducir:** crear
  `<tmp>/locked/Influent.demo.v1.0-26.05-20.13-AlphaCube/` con `details.xml`,
  poner `locked` en `chmod 000` y empaquetar indicando esa carpeta (o llamar a
  `BuildThread(..., custom_path=...).run()`); se obtiene `PermissionError` en
  `Path.exists()` dentro de `run`.
- **Estado:** Resuelto.
- **Prioridad:** Alta (la acción principal de la app terminaba en un aborto del
  proceso, no en un error).
- **Solución aplicada:** `find_env_file()` y `app_icon_for()` tratan `OSError`
  como «no hay `.env`»/«no hay icono»; `BuildThread.run()` envuelve la
  comprobación de `custom_path` y la preflight en `try/except OSError` y emite
  la señal `error` con la ruta o el detalle. El camino feliz no cambia.
- **Pruebas:** `tests/test_unreadable_build_and_launch.py` —
  `test_find_env_file_tolerates_unreadable_project`,
  `test_app_icon_for_tolerates_unreadable_project` y
  `test_build_thread_reports_unreadable_custom_path` (las tres fallan con el
  código anterior).
- **Commit:** se registra en el cierre del trigésimo séptimo ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-1e7c3d58 — «Ejecutar» del gestor cae con una carpeta ilegible

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** `ProjectDetailsDialog._run_installed_app()` listaba la
  carpeta instalada con `os.listdir()` y lanzaba el proceso con
  `subprocess.Popen()` sin `try/except`. Una carpeta sin permiso de lectura
  (`PermissionError`) o un ejecutable que desaparece entre la comprobación y el
  `Popen` (`FileNotFoundError`/`OSError`) escapaba del slot y PyQt6 abortaba
  la aplicación.
- **Pasos para reproducir:** instalar una app en `Fluthin Apps/demo/`, poner
  `demo` en `chmod 000` y pulsar «Ejecutar» en el gestor (o invocar
  `_run_installed_app()` con un objeto que apunte a esa carpeta).
- **Estado:** Resuelto.
- **Prioridad:** Media (acción secundaria, pero tumbaba todo el proceso).
- **Solución aplicada:** el listado y el `Popen` van dentro de un
  `try/except OSError` que muestra el aviso
  `manager.error_status` con la causa; la carpeta inexistente conserva su
  mensaje propio.
- **Pruebas:** `tests/test_unreadable_build_and_launch.py` —
  `test_run_installed_app_reports_unreadable_dir` (falla con el código
  anterior).
- **Commit:** se registra en el cierre del trigésimo séptimo ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-9b5f2a74 — La TUI cae al abrir una carpeta sin `xdg-open`

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** «Abrir carpeta» de la TUI resolvía la ruta y llamaba a
  `subprocess.Popen(["xdg-open", …])` (o `open`/`os.startfile`) sin proteger el
  lanzamiento. En un sistema mínimo sin `xdg-open`, o con una ruta cuyo
  `resolve()` falla, la TUI terminaba con traceback en vez de avisar. Es la
  misma familia que R-9a4c1e27, que sólo cubrió las comprobaciones de rutas.
- **Pasos para reproducir:** ejecutar la TUI en un entorno sin `xdg-open` y
  elegir «Abrir carpeta»; `FileNotFoundError: xdg-open` sube hasta `main`.
- **Estado:** Resuelto.
- **Prioridad:** Media (TUI usable, pero el flujo terminaba en traceback).
- **Solución aplicada:** el lanzamiento y la resolución van dentro de
  `try/except OSError`; se muestra
  `manager.open_folder_failed_title` con la causa y se vuelve al menú.
- **Pruebas:** `tests/test_unreadable_build_and_launch.py` —
  `test_tui_open_folder_survives_missing_opener` (falla con el código anterior)
  y `test_tui_open_folder_opens_accessible_folder` (regresión del camino feliz).
- **Commit:** se registra en el cierre del trigésimo séptimo ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-3f8a7c21 — El IDE `.iflapp` aborta al abrir un proyecto con fuentes no UTF-8

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** un proyecto guardado por un editor de Windows en ANSI
  (``cp1252``) declara su codificación como exige Python
  (``# -*- coding: cp1252 -*-``). Al abrirlo en el IDE, `_refresh_tree()` marca
  el primer guion y dispara `_on_script_selected()`, que leía con
  `encoding="utf-8-sig"` y sólo capturaba `OSError`: el `UnicodeDecodeError`
  escapaba del slot y **PyQt6 abortaba el proceso** (`Fatal Python error:
  Aborted`). El mismo guion también rompía `_declared_scripts()` al leer
  `config/settings.json` si este venía en ANSI.
- **Pasos para reproducir:** crear un proyecto con `app.py` codificado en
  cp1252 (con su *coding cookie*) y `config/settings.json` en cp1252; abrirlo
  con el IDE (`IflappIdePanel.load_project`) → el proceso muere.
- **Estado:** Resuelto.
- **Prioridad:** Alta (pérdida de la sesión de GUI al abrir un proyecto real).
- **Solución aplicada:** nuevo módulo `lib/blindcubeEngine/source_io.py`
  (`read_python_source()` detecta la codificación como el intérprete, PEP 263,
  y `SourceEncodingError` cuando el archivo no es fuente Python válida).
  `_on_script_selected()` lo usa y captura `(OSError, SourceEncodingError)`
  mostrando `iflapp_ide.load_failed`; `_declared_scripts()` lee con
  `utf-8-sig` (acepta el BOM del Bloc de notas) y captura
  `UnicodeDecodeError`.
- **Pruebas:** `tests/test_non_utf8_sources.py::TestIdePanelSlots` (con el
  código anterior el proceso aborta) y `TestIdeAnalysis` (`scan_project` con
  `settings.json` cp1252 y con BOM).
- **Commit:** se registra en el cierre del trigésimo octavo ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-9d2b6e45 — `--ide-compile` y el análisis del IDE ignoran la declaración PEP 263

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** el motor leía los guiones con `encoding="utf-8"` fijo, así
  que un fuente válido para Python por declarar `cp1252` reventaba en tres
  puntos: `detect_hidden_imports()` (análisis del IDE), la inyección del
  bootloader de splash (`prepare_for_build()` → `write_injected_copy()`) y el
  preflight (`check_syntax()`), que además marcaba el guion como «sintaxis
  rota». `compile_project()` propagaba el `UnicodeDecodeError` y el CLI
  `--ide-compile` (que sólo captura `OSError`) lo imprimía como traceback.
- **Pasos para reproducir:** `--ide-compile <proyecto>` con `app.py` en cp1252
  y cookie → `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf1`.
- **Estado:** Resuelto.
- **Prioridad:** Alta (compilación imposible para proyectos en ANSI).
- **Solución aplicada:** `detect_hidden_imports()`, `inject_file()`,
  `write_injected_copy()` y `check_syntax()` leen con `read_python_source()`.
  La copia inyectada se escribe con **la misma codificación** del original, de
  modo que la *cookie* siga siendo válida; los archivos que no son fuente
  Python válida se degradan con un mensaje legible (imports `[]`, sin copia
  inyectada, preflight con el error de codificación) en vez de lanzar.
  `BuildThread._detect_hidden_imports()` usa el mismo helper.
- **Pruebas:** `tests/test_non_utf8_sources.py` —
  `test_hidden_imports_read_pep263_source`,
  `test_injection_preserves_declared_encoding`,
  `test_compile_project_handles_pep263_source`,
  `test_preflight_accepts_pep263_source` y los casos de degradación.
- **Commit:** se registra en el cierre del trigésimo octavo ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-6c4a1f83 — Blindaje y build fallan con fuentes y `settings.json` no UTF-8

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** `hardening.inject_anti_debug()` y `obfuscate_strings()`
  leían y reescribían el guion en UTF-8 fijo: con un fuente cp1252 lanzaban
  `UnicodeDecodeError` (vía `apply_all()` se degradaba a un informe
  «error: …» genérico; llamadas directas lanzaban) y, de haber reescrito,
  habrían dejado la *cookie* mintiendo sobre la codificación.
  `BuildThread._load_explicit_scripts()` y `_persist_env_payload()` leían
  `config/settings.json` con `utf-8` fijo y no capturaban
  `UnicodeDecodeError`.
- **Pasos para reproducir:** `hardening.obfuscate_strings(<app.py cp1252>)` →
  `UnicodeDecodeError`; `--buildthis` con `settings.json` en cp1252 →
  `UnicodeDecodeError` desde `__init__` de la QThread.
- **Estado:** Resuelto.
- **Prioridad:** Media (el build degrada o falla, sin corrupción de datos).
- **Solución aplicada:** ambos métodos de blindaje leen con
  `read_python_source()` y escriben con la codificación detectada (o devuelven
  un `HardeningReport` no aplicado y legible). Los dos puntos de lectura de
  `settings.json` usan `utf-8-sig` y capturan `UnicodeDecodeError`.
- **Pruebas:** `tests/test_non_utf8_sources.py::TestHardeningEncoding` y
  `test_preflight_reports_undecodable_source`.
- **Commit:** se registra en el cierre del trigésimo octavo ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-2a9f4d17 — El depurador rechaza fuentes con declaración PEP 263

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** `trace_script()` (base de `--ide-debug` y del depurador del
  IDE) leía el guion con `encoding="utf-8"` fijo. Un fuente válido para Python
  que declara `cp1252` fallaba con `UnicodeDecodeError` y el depurador quedaba
  inservible (`--ide-debug` sólo mostraba `[ERROR] UnicodeDecodeError…`).
- **Pasos para reproducir:** `--ide-debug <proyecto>/ansi.py` con
  `# -*- coding: cp1252 -*-` y algún acento → `[ERROR] UnicodeDecodeError`.
- **Estado:** Resuelto.
- **Prioridad:** Media (el resto del IDE y del build ya soportaba PEP 263).
- **Solución aplicada:** `trace_script()` compila con `read_python_source()`;
  un fuente no decodificable se traduce a `SyntaxError` con un mensaje legible
  que `debug_script()` ya reporta como `error`.
- **Pruebas:** `tests/test_non_utf8_sources.py::TestDebuggerEncoding` (traza,
  depuración y error legible).
- **Commit:** se registra en el cierre del trigésimo noveno ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-5e8c1b42 — `pm.data` con números no finitos impide arrancar

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** `coerce_int()`/`coerce_float()` sólo capturaban
  `TypeError`/`ValueError`. `1e400` es JSON válido y se decodifica como
  infinito: `int(inf)` lanza `OverflowError`, que escapaba de
  `get_user_int()`/`get_user_float()`. Con `"sidebar_accent_width": 1e400` el
  arranque de la GUI moría (`settings_appearance_state`, `border_w`), y con
  `"card_opacity": 1e400` el guardado de Configuración hacía
  `int(inf * 100)` dentro de un slot.
- **Pasos para reproducir:** escribir `data/pm.data` con
  `{"user": {"sidebar_accent_width": 1e400}}` y arrancar → `OverflowError`.
- **Estado:** Resuelto.
- **Prioridad:** Alta (un archivo editable a mano impide abrir la aplicación).
- **Solución aplicada:** las coerciones rechazan valores no finitos con
  `math.isfinite()` y capturan `OverflowError`; los enteros grandes legítimos
  se conservan y los números válidos mantienen el comportamiento anterior.
- **Pruebas:** `tests/test_local_config_robustness.py::TestPMDataNumbers`.
- **Commit:** se registra en el cierre del trigésimo noveno ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-7b3a9e58 — Cabecera `.iflapp` con números no finitos escapa como `OverflowError`

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** `_require_int()` (validador de la cabecera) y
  `_read_section()` sólo capturaban `TypeError`/`ValueError`. Una cabecera con
  `"size": 1e400` (JSON válido → infinito) lanzaba `OverflowError` crudo desde
  `read_iflapp_header()`, `verify_iflapp()` y `read_dropper_header()`, que
  documentan devolver `IflappError`. El mensaje que veía el usuario era
  «cannot convert float infinity to integer».
- **Pasos para reproducir:** `--inspect` sobre un `.iflapp` con
  `{"sections": {"icon": {"size": 1e400}}}` → error críptico en vez de
  «cabecera inválida».
- **Estado:** Resuelto.
- **Prioridad:** Media (contenedores ajenos o dañados; sin corrupción).
- **Solución aplicada:** `_require_int()` y `_read_section()` capturan
  `OverflowError` y lo traducen a `IflappError`; `read_dropper_header()` además
  traduce `OSError` al leer el `.run`.
- **Pruebas:** `tests/test_iflapp_format.py::MalformedHeaderShapeTests`
  (`test_non_finite_section_size_raises`,
  `test_non_finite_payload_offset_raises`) y
  `tests/test_iflapp_dropper_sandbox.py::DropperTests`
  (`test_read_dropper_header_translates_non_finite_header`,
  `test_read_dropper_header_reports_missing_file`).
- **Commit:** se registra en el cierre del trigésimo noveno ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-9c4d2f61 — El detector de dependencias del editor ignora PEP 263

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** `DependencyChecker._detect_imports()` (pmCodeEditor) leía el
  guion con `encoding="utf-8"` fijo y `_write_requirements_txt()` leía el
  `requirements.txt` existente igual. Un proyecto en ANSI lanzaba
  `UnicodeDecodeError` dentro de la QThread al pulsar «Comprobar dependencias»
  y un `requirements.txt` no UTF-8 impedía reescribirlo.
- **Pasos para reproducir:** `DependencyChecker(<app.py cp1252>)._detect_imports()`
  → `UnicodeDecodeError`.
- **Estado:** Resuelto.
- **Prioridad:** Media (función del editor inutilizable con proyectos ANSI).
- **Solución aplicada:** `_detect_imports()` usa `read_python_source()` y, si el
  fuente no es decodificable, escanea con `errors="replace"` para no perder
  imports legibles; `_write_requirements_txt()` tolera
  `OSError`/`UnicodeDecodeError` al leer el archivo previo.
- **Pruebas:** `tests/test_non_utf8_sources.py::TestDependencyScanEncoding`.
- **Commit:** se registra en el cierre del trigésimo noveno ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-9e1a4c72 — `--build-removeme` lanza traceback con una raíz de instalación ilegible

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** `read_record()` comprobaba `path.is_file()` sin protección.
  Con una raíz de instalación sin permiso de lectura, `pathlib` lanza
  `PermissionError`; el CLI `--build-removeme` sólo captura
  `AsksomeInstallError`, así que el usuario recibía un traceback completo en
  lugar de un mensaje. `compile_removeme_binary()` tenía la misma comprobación
  sin proteger sobre `removeme.py`.
- **Pasos para reproducir:** `chmod 000 <raíz>` y
  `python packagemaker.py --build-removeme myapp --install-root <raíz>` →
  `PermissionError: [Errno 13] … install.json` con traceback.
- **Estado:** Resuelto.
- **Prioridad:** Media (acción de shell concreta; `--uninstall-asksome` y
  `--list-asksome` ya eran robustos).
- **Solución aplicada:** `read_record()` traduce el `OSError` de `is_file()` a
  `AsksomeInstallError` («No se pudo acceder al registro de instalación…»),
  que el CLI ya muestra como `[ERROR]`; `compile_removeme_binary()` usa
  `path_is_file()` y conserva su contrato de devolver `None` cuando no puede
  compilar.
- **Pruebas:** `tests/test_mexf_asksome.py::test_read_record_reports_unreadable_install_root`.
- **Commit:** se registra en el cierre del cuadragésimo ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-4c8b2e91 — Un comando `.mexf` no ejecutable lanza traceback en `--debug-mexf --debug-run`

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** `default_runner()` sólo capturaba `FileNotFoundError` y
  `TimeoutExpired`. Un `commands[].executable` sin permiso de ejecución (o un
  `cwd` inaccesible) hacía que `subprocess.run()` lanzara `PermissionError`
  fuera del motor: el CLI `--debug-mexf --debug-run` mostraba un traceback y el
  botón de ejecución real del editor `.mexf` abortaba la app.
- **Pasos para reproducir:** `.mexf` con `executable: /ruta/tool.sh` en modo
  `0644` y `python packagemaker.py --debug-mexf main.mexf --debug-run` →
  `PermissionError` con traceback.
- **Estado:** Resuelto.
- **Prioridad:** Media (depurador del editor y CLI; requiere un comando
  declarado no ejecutable o una carpeta de trabajo sin permisos).
- **Solución aplicada:** `default_runner()` captura el resto de `OSError` y
  devuelve `126` con el mensaje, igual que la convención que ya usa el motor
  para un comando sin ejecutable; el paso queda `failed` y el CLI informa
  «el comando … falló con código 126».
- **Pruebas:** `tests/test_mexf_debugger.py::RunnerTests::test_default_runner_reports_non_executable_file`
  y `::test_debugger_step_survives_unlaunchable_command`.
- **Commit:** se registra en el cierre del cuadragésimo ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-5d1c7a83 — Un `.mexf` YAML con claves legacy lanza `JSONDecodeError` con traceback

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** `detect_mexf_format()` clasificaba como `legacy-json`
  cualquier documento que tuviera `extensions`, `file_associations` o
  `context_menus` en la raíz, sin importar si el texto era JSON o YAML. Con un
  `.mexf` YAML que usa esas claves (por ejemplo, un documento al que le falta
  `format: mexf`), `parse_mexf()` volvía a leer el archivo y lo entregaba a
  `json.loads()`, que lanzaba `JSONDecodeError`. Esa excepción no es
  `MexfError` ni `OSError`, así que `compile_mexf_project()` no la traducía y
  `--compile-mexf`, `--shell-plan` y `--debug-mexf` mostraban el traceback
  completo en lugar de `[ERROR]`.
- **Pasos para reproducir:** crear `.mexf/main.mexf` con
  `extensions:\n  - extension: .foo\n` (YAML, sin `format: mexf`) y ejecutar
  `python packagemaker.py --compile-mexf <proyecto>` → `JSONDecodeError:
  Expecting value: line 1 column 1 (char 0)` con traceback.
- **Estado:** Resuelto.
- **Prioridad:** Alta (los tres comandos de shell del formato `.mexf` fallaban
  con un documento que un usuario puede escribir a mano; el editor gráfico no
  se veía afectado porque valida con su propio lint).
- **Solución aplicada:** nueva `_classify_mexf_text()` que decide el formato
  sobre el texto ya leído y sólo devuelve `legacy-json` cuando `json.loads()`
  tuvo éxito; `detect_mexf_format()` y `parse_mexf()` la comparten, de modo que
  ya no hay una segunda lectura (y desaparece la carrera entre ambas).
  `parse_mexf()` además traduce un `JSONDecodeError` o un JSON no-objeto a
  `MexfError`, y un YAML con claves legacy se informa como «Formato .mexf
  desconocido» como cualquier documento no reconocido.
- **Pruebas:** `tests/test_mexf_asksome.py::test_yaml_with_legacy_keys_is_unknown_not_json`,
  `::test_compile_mexf_wraps_legacy_shaped_yaml` y
  `::test_legacy_json_document_still_migrates_after_classification` (las dos
  primeras fallan con el código anterior).
- **Commit:** se registra en el cierre del cuadragésimo primer ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-8c2f4b17 — Una respuesta inesperada del traductor automático aborta la interfaz

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** `_auto_translate_google()` indexaba la respuesta del
  traductor (`payload[0]`, `p[0]`) sin comprobar su forma. El formato esperado
  es `[[[texto, …], …], …]`, pero un portal cautivo o un proxy puede responder
  200 con `5`, `true`, `null` o una lista de números: entonces el indexado
  lanzaba `TypeError`, que no estaba entre las excepciones capturadas. Como
  `tr()` se evalúa en los slots de Qt (por ejemplo al cambiar de idioma en
  Configuración), la excepción abortaba el proceso con
  `Fatal Python error: Aborted`.
- **Pasos para reproducir:** con `auto_translate` activo y un idioma distinto
  de `es`, servir `5` desde el endpoint del traductor y llamar a `tr()` →
  `TypeError: 'int' object is not subscriptable`.
- **Estado:** Resuelto.
- **Prioridad:** Media (requiere una respuesta anómala del servicio externo,
  pero el fallo es duro: cierra la aplicación).
- **Solución aplicada:** `_auto_translate_google()` valida que la respuesta sea
  una lista de segmentos con el primer elemento de texto y devuelve `None` en
  cualquier otra forma; `TypeError` se añade a la captura defensiva. Sin
  respuesta válida, `translate()` devuelve el texto original como ya hacía
  cuando no había red.
- **Pruebas:** `tests/test_i18n_translate_robustness.py` (9 casos; 6 fallan con
  el código anterior).
- **Commit:** se registra en el cierre del cuadragésimo primer ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-3a7f2d84 — Un comando `.mexf` con byte NUL lanza traceback en el depurador

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** `default_runner()` capturaba `FileNotFoundError` (127),
  `TimeoutExpired` (124) y `OSError` (126), pero `subprocess` señala con
  `ValueError: embedded null byte` un `executable`, un argumento, un valor de
  entorno o un `cwd` que contenga un byte NUL. Un `.mexf` puede declarar ese
  texto (`executable: "python\u0000x"`), así que `--debug-mexf --debug-run`
  mostraba el traceback completo y, desde el diálogo del editor (slot de Qt),
  PyQt6 abortaba el proceso.
- **Pasos para reproducir:** crear un `.mexf` con
  `executable: "python\u0000x"` y ejecutar
  `python packagemaker.py --debug-mexf <archivo> --debug-run`.
- **Estado:** Resuelto.
- **Prioridad:** Media (requiere un `.mexf` malformado, pero cierra la GUI).
- **Solución aplicada:** `default_runner()` captura también `ValueError` y
  devuelve `126` con el mensaje, igual que con un binario no ejecutable. El
  depurador marca el paso como `failed` y continúa.
- **Pruebas:** `tests/test_mexf_debugger.py::RunnerTests::test_default_runner_reports_embedded_null_byte`,
  `::test_default_runner_reports_null_byte_in_environment` y
  `::test_debugger_step_survives_null_byte_command` (las tres fallan con el
  código anterior).
- **Commit:** se registra en el cierre del cuadragésimo segundo ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-8d4c1e67 — Un `.mexf` con escalares YAML no JSON lanza `TypeError` al compilar

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** `yaml.safe_load()` produce objetos que `json.dumps()` no
  sabe escribir (fechas, `set`, `bytes`, tuplas) y permite alias recursivos.
  `parse_mexf()` los aceptaba y `canonicalize_mexf()` fallaba después con
  `TypeError: Object of type date is not JSON serializable` (o
  `ValueError: Circular reference detected`). `--compile-mexf` mostraba el
  traceback porque sólo captura `MexfCompileError`/`OSError`; en la GUI el
  error se mostraba pero el artefacto no se generaba.
- **Pasos para reproducir:** añadir `released: 2024-01-01` a `metadata` en
  `.mexf/main.mexf` y ejecutar `--compile-mexf <proyecto>`.
- **Estado:** Resuelto.
- **Prioridad:** Alta (una fecha YAML es un dato corriente y el fallo afecta a
  la compilación de artefactos).
- **Solución aplicada:** `_json_safe()` normaliza el documento al leerlo y
  antes de serializarlo: fechas/horas a ISO 8601, `set`/`frozenset` a lista
  ordenada, `bytes` a base64, tuplas a listas, claves a texto y tipos
  desconocidos a texto. Un alias recursivo se rechaza con `MexfError`
  («referencia circular»), que el CLI ya traduce a un mensaje sin traceback.
  `canonicalize_mexf()` aplica la misma normalización como garantía para
  cualquier llamador.
- **Pruebas:** `tests/test_mexf_asksome.py::test_yaml_native_scalars_are_normalized_for_json`,
  `::test_compile_mexf_project_accepts_yaml_dates`,
  `::test_recursive_yaml_alias_is_reported_as_mexf_error` y
  `::test_canonicalize_rejects_recursive_document` (las cuatro fallan con el
  código anterior).
- **Commit:** se registra en el cierre del cuadragésimo segundo ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-4c9e2b71 — Un `.mexf` con `.nan`/`.inf` emite JSON no válido (`NaN`/`Infinity`)

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** `yaml.safe_load()` convierte `.nan`, `.inf` y `-.inf` en
  `float` no finitos, y el JSON legacy puede producirlos con `1e400` (decodifica
  a `inf`). `_json_safe()` los devolvía tal cual porque son `float`, así que
  `json.dumps()` los escribía como `NaN`/`Infinity`/`-Infinity`, que **no son
  JSON válido** (RFC 8259). Afectaba a `--shell-plan-json` (los consumidores
  estrictos, como `jq` o `JSON.parse` de JavaScript, rechazan la salida) y al
  `.mexf` canónico que `--compile-mexf` incrusta en el `.asksome`.
- **Pasos para reproducir:** crear un `.mexf` con `shortcuts: {Ctrl+N: .nan}`,
  `environments: {A: .inf}` o un `registry` con `.nan`, y ejecutar
  `python packagemaker.py --shell-plan-json --shell-plan <archivo>`. También con
  el JSON legacy `{"extensions": [], "shortcuts": {"Ctrl+O": 1e400}}`.
- **Estado:** Resuelto.
- **Prioridad:** Media (requiere un valor no finito, pero rompe el contrato JSON
  que consumen scripts y herramientas externas).
- **Solución aplicada:** `_json_safe()` convierte los `float` no finitos a su
  texto (`"nan"`, `"inf"`, `"-inf"`), igual que ya hacía `plan_from_document()`
  con `environments`. El parseo de documentos JSON legacy aplica la misma
  normalización que el YAML, de modo que `--shell-plan-json` y
  `canonicalize_mexf()` emiten JSON estricto.
- **Pruebas:** `tests/test_mexf_shell.py::test_shell_plan_json_stays_valid_with_non_finite_yaml`,
  `::test_legacy_json_infinity_keeps_shell_plan_json_valid` y
  `tests/test_mexf_asksome.py::test_non_finite_yaml_scalars_stay_json_safe`
  (las tres fallan con el código anterior).
- **Commit:** se registra en el cierre del cuadragésimo tercer ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-4a7f2c93 — Una ruta no textual en `pm.data` tumba el arranque

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** `to_legacy_app_config()` devolvía `base_dir`/`fluthin_apps`
  tal cual estaban en `data/pm.data`. Si el archivo se editaba a mano y guardaba
  un objeto, una lista o un número, `packagemaker.py` los pasaba a
  `os.makedirs()` al importarse y el proceso moría con `TypeError: expected
  str, bytes or os.PathLike object, not dict` antes de cualquier acción (GUI y
  CLI). Una cadena con byte NUL lanzaba `ValueError: embedded null byte`, que
  tampoco capturaba el `except OSError` de arranque. El mismo valor podía llegar
  desde el `config/settings.json` legacy durante la migración.
- **Pasos para reproducir:** escribir `{"user": {"base_dir": {"x": 1}}}` en
  `data/pm.data` y ejecutar `python packagemaker.py --app-version` (antes:
  traceback en `packagemaker.py`, línea de `os.makedirs`; ahora: arranca y usa
  la carpeta por defecto de la plataforma).
- **Estado:** Resuelto.
- **Prioridad:** Alta (impide arrancar la aplicación, GUI y CLI).
- **Solución aplicada:** `pm_data.coerce_text()` filtra los valores no
  textuales en `to_legacy_app_config()`; `load_merged_app_config()` reemplaza
  rutas no textuales, vacías o con NUL por el valor por defecto y
  `migrate_from_legacy_config()` ignora rutas e idioma no textuales del
  `settings.json` legacy. El `os.makedirs` de arranque captura también
  `TypeError`/`ValueError` como red final.
- **Pruebas:** `tests/test_corrupt_user_config_startup.py::TestTextCoercion`
  (5 casos parametrizados de rutas corruptas, rutas válidas preservadas y
  migración legacy).
- **Commit:** se registra en el cierre del cuadragésimo tercer ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-8d3e6b15 — Un `language` no textual en `pm.data` aborta el arranque

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** el arranque de la GUI pasa `config.get("LANGUAGE")` a
  `i18n.initialize()` → `load_translation()`, que hacía `lang.lower()`. Un
  `language` guardado como objeto, lista o número en `pm.data` lanzaba
  `AttributeError: 'dict' object has no attribute 'lower'` y cerraba la
  aplicación antes de pintar la ventana.
- **Pasos para reproducir:** escribir `{"user": {"language": {"a": 1}}}` en
  `data/pm.data` y arrancar la GUI; o llamar a
  `i18n.initialize(app, {"a": 1})` (antes: `AttributeError`).
- **Estado:** Resuelto.
- **Prioridad:** Alta (impide arrancar la GUI).
- **Solución aplicada:** `to_legacy_app_config()` devuelve `"es"` cuando el
  idioma no es texto; `I18nManager.load_translation()` normaliza con `str()` y
  cae a `"es"` cuando el código no está en `SUPPORTED_LANGUAGES`, de modo que un
  valor corrupto nunca llega a `.lower()` ni genera un idioma inexistente.
- **Pruebas:** `tests/test_corrupt_user_config_startup.py::TestLanguageCoercion`
  (idioma no textual, código desconocido y `load_translation` con objeto).
- **Commit:** se registra en el cierre del cuadragésimo tercer ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-2f5c9a71 — Un acento no hexadecimal aborta las notificaciones

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** `NotificationWidget._darken_color()` parseaba el acento con
  `int(valor[i:i+2], 16)` sin validar. Con un `custom_accent_color` que no es
  `#RRGGBB` (texto libre, lista, cadena de 3/8 dígitos), crear una notificación
  con una acción `primary` —por ejemplo el botón «Copiar error» del reporte o
  «Ver detalles» de un fallo de compilación— lanzaba `ValueError` dentro de un
  slot de Qt, y PyQt6 abortaba el proceso. El acento corrupto también se
  interpolaba en todos los QSS.
- **Pasos para reproducir:** escribir
  `{"user": {"custom_accent_color": "azul"}}` en `data/pm.data` y mostrar una
  notificación con `NotificationAction(..., "primary")` (antes:
  `ValueError: invalid literal for int() with base 16: 'az'`).
- **Estado:** Resuelto.
- **Prioridad:** Media (requiere un acento corrupto, pero mata la aplicación).
- **Solución aplicada:** `design_tokens.normalize_accent()` valida `#RRGGBB`;
  `active_accent()` y `packagemaker.get_accent_color()` lo usan para caer al
  acento corporativo cuando el valor guardado o el del sistema no es válido.
  `_darken_color()` devuelve la entrada sin cambios si no es hexadecimal, como
  red defensiva en el propio widget.
- **Pruebas:** `tests/test_corrupt_user_config_startup.py::TestAccentRobustness`
  (normalización, acento corrupto en `pm.data`, `_darken_color` con entradas
  inválidas y notificación con acción primaria).
- **Commit:** se registra en el cierre del cuadragésimo tercer ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-7a2c9e14 — El asistente MoonFix cae con un `details.xml` ilegible

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** `MoonFixWizard.create_project_page()` leía `details.xml`
  con `ET.parse()` protegido sólo contra `ET.ParseError`. Si el archivo existe
  pero no se puede leer —permisos POSIX o un bloqueo exclusivo en Windows—,
  `ET.parse()` lanza `PermissionError` (un `OSError`) que escapaba de la
  construcción del asistente. Como la página se crea en el `__init__` del
  diálogo, invocado desde un slot de Qt, PyQt6 abortaba el proceso.
- **Pasos para reproducir:** crear un proyecto con `details.xml` y aplicar
  `chmod 000` a ese archivo; abrir MoonFix con el proyecto en la lista. Antes:
  `PermissionError: [Errno 13] Permission denied: .../details.xml`.
- **Estado:** Resuelto.
- **Prioridad:** Media (requiere un `details.xml` ilegible, pero mata la app).
- **Solución aplicada:** `except (ET.ParseError, OSError)` en
  `create_project_page()`; la página se construye con los valores por defecto y
  MoonFix puede regenerar el archivo desde las plantillas.
- **Pruebas:**
  `tests/test_gui_unreadable_paths.py::GuiUnreadablePathTests::test_moonfix_tolerates_unreadable_details_xml`
  (falla con el código anterior).
- **Commit:** se registra en el cierre del cuadragésimo cuarto ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-8f3d1b62 — «Abrir proyecto» del dashboard cae con un `details.xml` ilegible

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** `DashboardWindow._open_as_pm_project()` leía `details.xml`
  con `ET.parse()` y sólo capturaba `ET.ParseError`. Con el archivo presente
  pero sin permiso de lectura (o bloqueado en Windows), `ET.parse()` lanza
  `PermissionError`; como el método se ejecuta en el slot de «Abrir proyecto»,
  la excepción escapaba y PyQt6 abortaba la aplicación.
- **Pasos para reproducir:** crear un proyecto con `details.xml` y `chmod 000`
  sobre ese archivo; pulsar «Proyecto PackageMaker» y elegir la carpeta. Antes:
  `PermissionError: [Errno 13] Permission denied: .../details.xml`.
- **Estado:** Resuelto.
- **Prioridad:** Media (requiere un `details.xml` ilegible, pero mata la app).
- **Solución aplicada:** `except (ET.ParseError, OSError)` en
  `_open_as_pm_project()`; sin metadatos se cae al escaneo de guiones `.py`, que
  ya toleraba `OSError`.
- **Pruebas:**
  `tests/test_gui_unreadable_paths.py::GuiUnreadablePathTests::test_dashboard_tolerates_unreadable_details_xml`
  (falla con el código anterior).
- **Commit:** se registra en el cierre del cuadragésimo cuarto ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-7b4e2c19 — `--ide-scan`/IDE se niega a escanear un proyecto con rutas ilegibles

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** `lib/iflapp_ide.py` comprobaba `details.xml`,
  `config/settings.json`, el icono y la estructura con `Path.is_file()`,
  `Path.exists()` y `Path.is_dir()` dentro de `scan_project()`. En Python 3.13
  esas llamadas propagan `PermissionError` cuando el directorio padre no es
  accesible, y `read_details()` sólo capturaba `ET.ParseError`, así que un
  `details.xml` sin permiso de lectura tumbaba el escaneo completo. El CLI
  respondía `[ERROR] [Errno 13] Permission denied` sin listar guiones y el
  panel del IDE no podía abrir el proyecto.
- **Pasos para reproducir:** crear un proyecto con `details.xml` y `demo.py`,
  aplicar `chmod 000` a `details.xml` y ejecutar `python packagemaker.py
  --ide-scan <proyecto>`. Antes: error de permisos y ningún dato del proyecto.
- **Estado:** Resuelto.
- **Prioridad:** Media (proyecto parcialmente ilegible, pero el escaneo es la
  puerta de entrada del IDE).
- **Solución aplicada:** `read_details()` captura `(ET.ParseError, OSError)` y
  comprueba el archivo con `path_is_file`; `_declared_scripts()`, `find_icon()`
  y `scan_project()` usan `lib.file_ops` (`path_exists`, `path_is_file`,
  `path_is_dir`), que degradan a «no existe» en vez de lanzar. El escaneo
  continúa con los metadatos por defecto y los guiones encontrados.
- **Pruebas:** `tests/test_iflapp_ide.py::IdeUnreadablePathTests` (3 casos;
  fallan con el código anterior).
- **Commit:** se registra en el cierre del cuadragésimo quinto ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-3c9d5e21 — El sandbox deja escapar `PermissionError` con un workspace inaccesible

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** `HardwareSandbox.run()` sólo traducía `FileNotFoundError` y
  `TimeoutExpired`; cualquier otro `OSError` de `subprocess.run` escapaba. Con
  un *workspace* que existe pero no es accesible (permisos POSIX o carpeta
  bloqueada en Windows), `subprocess.run(..., cwd=...)` lanza
  `PermissionError`. Como la verificación corre en el hilo de compilación y en
  el `finally` del build, la excepción rompía el contrato de `run()` (devolver
  siempre un `SandboxResult`) y podía abortar la `QThread`.
- **Pasos para reproducir:** crear un directorio, aplicar `chmod 000` y llamar
  a `HardwareSandbox(backend="local").run(["/bin/echo", "hi"], <directorio>)`.
  Antes: `PermissionError: [Errno 13]`.
- **Estado:** Resuelto.
- **Prioridad:** Alta (rompe el contrato del sandbox y puede matar el build).
- **Solución aplicada:** `except OSError` en `run()` devuelve
  `SandboxResult(returncode=126, stderr=...)`, coherente con
  `mexf_debugger` (126 = no ejecutable). `run_and_verify_binary()` comprueba el
  binario dentro de `try/except OSError` y devuelve `-1` con un mensaje
  legible.
- **Pruebas:**
  `tests/test_iflapp_dropper_sandbox.py::HardwareSandboxTests::test_run_returns_result_when_workspace_is_unreadable`
  y `::test_run_and_verify_binary_reports_unreadable_binary` (fallan con el
  código anterior).
- **Commit:** se registra en el cierre del cuadragésimo quinto ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-8e1f6a24 — El removedor generado aborta con un acceso directo o árbol bloqueado

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-24
- **Descripción:** el `removeme.py` autónomo que genera `asksome_installer`
  comprobaba los accesos directos con `Path.is_file()` y borraba con
  `Path.unlink()`/`shutil.rmtree()` sin protección. Un acceso directo en una
  carpeta sin permisos o un árbol de instalación bloqueado (antivirus,
  `chmod`, Windows) lanzaba `PermissionError` con traceback; en modo GUI la
  excepción escapaba del bucle de eventos y abortaba el removedor. `main()`
  tampoco traducía `OSError` de `_install_dir()`/`target.is_dir()`.
- **Pasos para reproducir:** instalar un `.asksome`, añadir a `install.json` un
  acceso directo bajo una carpeta con `chmod 000` y ejecutar `removeme.py
  --console`. Antes: `Traceback ... PermissionError` al comprobar el acceso
  directo. Si la carpeta que contiene la instalación es de solo lectura, el
  `shutil.rmtree()` final también escapaba.
- **Estado:** Resuelto.
- **Prioridad:** Media (la desinstalación falla con traceback y puede abortar
  la GUI del removedor).
- **Solución aplicada:** `_shortcuts()` y `_self_file()` capturan `OSError`;
  `_remove()` omite los accesos directos ilegibles (informa «omitido») y trata
  el árbol de instalación de forma defensiva; `main()` envuelve
  `_install_dir()`/`is_dir()`/`_remove()` y responde con código 1 y un mensaje
  (`--silent` sigue devolviendo 0/1 sin ruido). Se mantiene la autonomía del
  stub (sólo biblioteca estándar).
- **Pruebas:** `tests/test_mexf_asksome.py::test_generated_removeme_tolerates_blocked_shortcut`
  y `::test_generated_removeme_reports_blocked_tree_without_traceback` (fallan
  con el código anterior).
- **Commit:** se registra en el cierre del cuadragésimo quinto ciclo.
- **Fecha de resolución:** 2026-11-24.

## R-7b2e9c41 — Una respuesta no UTF-8 del traductor automático aborta `tr()`

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-25
- **Descripción:** `_auto_translate_google` capturaba `urllib.error.URLError`,
  `TimeoutError`, `JSONDecodeError`, `IndexError`, `KeyError` y `TypeError`,
  pero no `UnicodeDecodeError` ni las excepciones de `http.client`. Un portal
  cautivo, un proxy corporativo o un antivirus que responde 200 con un cuerpo
  en latin-1 (o cortado) hacía que el `decode("utf-8")` lanzara dentro de
  `tr()`, y la excepción escapaba hasta el constructor de la ventana: con la
  interfaz en cualquier idioma distinto de español, la app no llegaba a
  abrirse.
- **Pasos para reproducir:** con `i18n.i18n._current_lang = "en"` y
  `_auto_translate = True`, sustituir `urlopen` por una respuesta cuyo `read()`
  devuelva `b"\xff\xfe<html>Proxy</html>"` y llamar a `tr("clave.inexistente")`.
  Antes: `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff …`. Lo mismo
  con `http.client.IncompleteRead` (cuerpo truncado).
- **Estado:** Resuelto.
- **Prioridad:** Alta (impide arrancar la interfaz sin red “sana”).
- **Solución aplicada:** la captura de `_auto_translate_google` pasa a
  `(OSError, ValueError, TypeError, KeyError, IndexError,
  http.client.HTTPException)`; `ValueError` cubre el cuerpo no UTF-8 y el JSON
  inválido, y `HTTPException` la respuesta truncada. El resultado sigue siendo
  `None` (el texto original), sin cambio en el comportamiento del motor.
- **Pruebas:** `tests/test_i18n_translate_robustness.py::test_non_utf8_response_returns_none`,
  `::test_truncated_response_returns_none` y `::test_translate_survives_offline`
  (fallan con el código anterior).
- **Commit:** se registra en el cierre del cuadragésimo sexto ciclo.
- **Fecha de resolución:** 2026-11-25.

## R-4e8a1d63 — El traductor automático repite el timeout en cada cadena

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-25
- **Descripción:** cuando el idioma activo no es español y una cadena no tiene
  traducción local, `translate()` llama a `_auto_translate_google` en cada
  `tr()` **sin memorizar el fallo**. Con la red caída, un proxy que traga
  paquetes o sin conexión, cada etiqueta sin traducir pagaba hasta 8 s de
  timeout, en el hilo de la interfaz: abrir una página con 40 cadenas podía
  congelar la ventana durante minutos y volvía a pagarlo al repintar.
- **Pasos para reproducir:** con `_current_lang = "en"`, sustituir `urlopen`
  por una función que lance `urllib.error.URLError` y llamar cuatro veces a
  `_auto_translate_google("hola", "es", "en")`. Antes: 4 intentos de red.
- **Estado:** Resuelto.
- **Prioridad:** Media (congelación perceptible, sin pérdida de datos).
- **Solución aplicada:** `lib/i18n.py` mantiene `_auto_translate_cooldowns`
  (par `(origen, destino)` → instante de fin) con
  `_AUTO_TRANSLATE_COOLDOWN_SECONDS = 60`: tras un fallo **de transporte** no
  se reintenta ese par durante un minuto, así que el resto de cadenas se
  resuelven al instante. Un cambio de idioma explícito
  (`load_translation`) borra los enfriamientos y reintenta de inmediato.
  Una respuesta 200 con formato inesperado no activa el enfriamiento: se sigue
  reintentando en la siguiente cadena. No afecta al motor ni a las
  traducciones locales.
- **Pruebas:** `tests/test_i18n_translate_robustness.py::test_repeated_transport_failures_are_cooldown_limited`,
  `::test_cooldown_expires_and_retries`, `::test_cooldown_is_per_language`,
  `::test_parse_failure_keeps_retrying` y
  `::test_explicit_language_change_resets_cooldown`.
- **Commit:** se registra en el cierre del cuadragésimo sexto ciclo.
- **Fecha de resolución:** 2026-11-25.

## R-9c3f6a25 — Un guion con codificación declarada pierde el `main` en zipapp

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-25
- **Descripción:** `compilers._defines_main()` leía el guion con
  `read_text(encoding="utf-8")`. Un proyecto guardado por un editor de Windows
  en ANSI (cookie `# -*- coding: cp1252 -*-`) no se podía decodificar, la
  lectura fallaba y el backend zipapp concluía que el guion **no** define
  `main()`: el `.pyz` se generaba con el punto de entrada de reserva
  (`__main__.py` + `runpy`) en vez de `modulo:main`. El resto del motor ya lee
  con `read_python_source` (PEP 263); ésta era la única lectura que quedaba
  fijada a UTF-8.
- **Pasos para reproducir:** escribir `main.py` con
  `"# -*- coding: cp1252 -*-\n# ñ á é\ndef main():\n    print('ok')\n"`
  codificado en cp1252 y llamar `_defines_main()` (antes `False`) o compilarlo
  con `--compiler zipapp`.
- **Estado:** Resuelto.
- **Prioridad:** Media (el paquete arranca, pero con otro punto de entrada y sin
  clasificar el guion como con `main`).
- **Solución aplicada:** `_defines_main()` usa
  `lib.blindcubeEngine.source_io.read_python_source` (importado en la cabecera
  del módulo) y captura `(OSError, SourceEncodingError, SyntaxError,
  ValueError)`. Un guion UTF-8 se lee exactamente igual que antes.
- **Pruebas:** `tests/test_page_action_bar_and_compilers.py::EncodedScriptEntryPointTests::test_defines_main_reads_declared_encoding`
  y `::test_zipapp_runs_main_from_encoded_script`.
- **Commit:** se registra en el cierre del cuadragésimo sexto ciclo.
- **Fecha de resolución:** 2026-11-25.

## R-2d5b8f41 — `updater.py --install --silent` daba por instalado un paquete corrupto

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-25
- **Descripción:** `install_iflapp(..., silent=True)` ejecutaba el worker y
  devolvía `(True, "Instalación completada")` sin mirar su resultado.
  `IFLAPPInstallerWorker.run()` captura la excepción, la registra en el log y
  emite `finished(False, …)`, pero en modo silencioso nadie escucha esa señal.
  Un `.iflapp` truncado, un ZIP que no es un contenedor válido o un destino sin
  permisos terminaban con `OK: Instalación completada` y código de salida `0`.
  El mismo patrón existía en `_update_from_exe(..., silent=True)`: un setup
  `.exe` que devolvía un código distinto de cero se reportaba como éxito.
- **Pasos para reproducir:** `printf 'NOTAZIP' > bad.iflapp` y ejecutar
  `python updater.py --install bad.iflapp --target ./destino --silent`.
  Antes: `Traceback … BadZipFile` en el log, `OK: Instalación completada` en
  pantalla y `EXIT=0`.
- **Estado:** Resuelto.
- **Prioridad:** Alta (una instalación fallida se reportaba como correcta y el
  código de salida ocultaba el fallo a scripts y al dropper).
- **Solución aplicada:** `IFLAPPInstallerWorker.run()`, `EXEInstallerWorker.run()`
  e `InstallerWorker.run()` devuelven `True`/`False` y guardan el mensaje en
  `self.error` (las señales se siguen emitiendo igual para la GUI). La
  cancelación devuelve `False` y el setup `.exe` limpia el temporal antes de
  informar. `install_iflapp` y `_update_from_exe` en modo silencioso usan ese
  valor y devuelven el error real. No cambia el comportamiento del engine ni
  el de las ventanas de actualización.
- **Pruebas:** `tests/test_updater_silent_status.py` (4 nuevas; 2 fallan con el
  código anterior). Reproducción real: el paquete corrupto responde
  `ERROR: File is not a zip file` con código 1, y un `.iflapp` válido sigue
  instalándose con código 0.
- **Commit:** se registra en el cierre del cuadragésimo séptimo ciclo.
- **Fecha de resolución:** 2026-11-25.

## R-9f3c1a72 — Desinstalar un Python portable informaba de un borrado que no ocurrió

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-25
- **Descripción:** `PythonPortableManager.uninstall_version()` borraba con
  `shutil.rmtree(..., ignore_errors=True)`: los errores se descartaban y la
  función devolvía `True` aunque la carpeta siguiera en disco (un `python.exe`
  en uso en Windows, un árbol de solo lectura). Además eliminaba el registro de
  `config.json`, así que la interfaz mostraba «eliminado» mientras el
  directorio seguía ocupando espacio y volvía a aparecer en el siguiente
  descubrimiento. La comprobación previa `install.path.exists()` tampoco estaba
  protegida: con el directorio padre inaccesible, `Path.exists()` propaga
  `PermissionError` desde el slot del botón «Desinstalar», y PyQt6 aborta el
  proceso.
- **Pasos para reproducir:** crear `data/pmCodeEditor/python/python312/python.exe`,
  llamar a `_discover_installations()` y a `uninstall_version("3.12")` con el
  directorio `python/` en `chmod 500` (antes: `True` con la carpeta intacta) o
  en `chmod 000` (antes: `PermissionError`).
- **Estado:** Resuelto.
- **Prioridad:** Media (no corrompe datos, pero engaña al usuario y puede
  tumbar la GUI).
- **Solución aplicada:** se usa `lib.file_ops.remove_tree`, que reintenta ante
  bloqueos y confirma el borrado; si el árbol sobrevive, se informa por
  `status_message` y se devuelve `False` **sin** borrar el registro; el
  diálogo de intérpretes añade un `QMessageBox.warning` con la ruta que sigue en
  disco. Con la ruta inaccesible tampoco lanza. `shutil` deja de importarse en
  el módulo.
- **Pruebas:** `tests/test_python_portable_uninstall.py` (4 nuevas; 2 fallan con
  el código anterior, omitidas en Windows/root).
- **Commit:** se registra en el cierre del cuadragésimo séptimo ciclo.
- **Fecha de resolución:** 2026-11-25.

## R-6b8e4d25 — El TUI moría al crear un proyecto con versión de un solo componente

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-25
- **Descripción:** tras un `create` correcto, `_screen_create` recalculaba el
  nombre de la carpeta con `version.strip().split("-")[0]` y los slugs en
  minúsculas. La CLI acepta `--version 2` (`normalize_version_base` lo completa
  a `2.0`), pero `format_project_folder(..., "2", ...)` lanza
  `ValueError: Versión inválida` y la excepción escapaba de `run_tui()`, que
  sólo captura `KeyboardInterrupt`: el TUI terminaba con traceback justo
  después de crear el proyecto. Además, al pasar el publisher en minúsculas el
  nombre mostrado no coincidía con la carpeta real (`Influent` → `influent`) en
  sistemas de archivos sensibles a mayúsculas.
- **Pasos para reproducir:** en la TUI, «Crear proyecto» con versión `2`;
  antes, traceback `ValueError` al final del flujo.
- **Estado:** Resuelto.
- **Prioridad:** Alta (rompe el flujo interactivo y muestra una ruta
  inexistente).
- **Solución aplicada:** la versión se completa con
  `ProjectNameFormatter.normalize_version_base` y se pasan a
  `format_project_folder` los mismos valores que recibió la CLI (sin reescribir
  mayúsculas ni slugs), tal como exige la ley de nombres. Un `ValueError`
  residual se avisa con `_warn` en lugar de tumbar el TUI.
- **Pruebas:** `tests/test_tui_create_naming.py` (3 nuevas; las 3 fallan con el
  código anterior).
- **Commit:** se registra en el cierre del cuadragésimo séptimo ciclo.
- **Fecha de resolución:** 2026-11-25.

## R-4f7a2c91 — El asistente de creación sobrescribía un proyecto existente sin avisar

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-25
- **Descripción:** `_ejecutarCreacionProyecto` comprobaba
  `os.path.join(rutaBase, nombreProyecto)` —el nombre libre que escribe el
  usuario— y, si existía, preguntaba si sobrescribir. Después recalculaba
  `rutaProyecto` con el nombre canónico
  (`Publisher.app.vX.x-YY.MM-HH.MM-Plataforma`) y creaba allí. Las dos rutas
  nunca coinciden, así que el aviso no aparecía y un proyecto ya existente se
  sobrescribía en silencio: `main.py`/`<app>.py`, `details.xml` y el resto de
  archivos de plantilla perdían el trabajo del usuario. En el caso simétrico,
  una carpeta antigua con el nombre libre hacía preguntar «¿sobrescribir?» para
  luego no tocar nada. El dashboard (`pm_dashboard.NewProjectWizard`) y el CLI
  headless ya comprobaban la ruta canónica antes de crear; sólo este diálogo
  quedaba desalineado.
- **Pasos para reproducir:** abrir «Crear proyecto», usar un nombre cuya
  carpeta canónica ya exista (mismo publisher, app y minuto) y confirmar; antes
  no se mostraba ninguna pregunta y el guion del proyecto se regeneraba.
- **Estado:** Resuelto.
- **Prioridad:** Alta (pérdida de datos del usuario).
- **Solución aplicada:** el nombre canónico y su marca temporal se calculan
  antes de comprobar la existencia; el aviso usa `folder_name` y se evalúa
  sobre `rutaProyecto`, la misma ruta que recibe
  `create_project_from_templates`. Sin cambios en el nombre canónico ni en el
  contenido de las plantillas.
- **Pruebas:** `tests/test_create_project_overwrite_guard.py` (3 nuevas; 2
  fallan con el código anterior).
- **Commit:** se registra en el cierre del cuadragésimo octavo ciclo.
- **Fecha de resolución:** 2026-11-25.

## R-8b2d4e17 — Los iconos SVG nunca se dibujaban y una carpeta de solo lectura abortaba el gestor

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-25
- **Descripción:** `lib/iconManager.py` importaba `QSvgRenderer` desde
  `PyQt6.QtSvgWidgets`, que sólo expone `QSvgWidget`; el renderer vive en
  `PyQt6.QtSvg` (así lo importa `lib/app_icons.py`). El `ImportError` dejaba
  `PYQT6_AVAILABLE = False`, de modo que `load_svg()` devolvía `None` siempre:
  la tarjeta «Abrir con» y cualquier consumidor de `load_svg_icon` se quedaban
  sin icono aunque el SVG existiera. Además, el constructor creaba
  `assets/icons` sin protección; en una instalación sin permiso de escritura el
  `mkdir` lanzaba `PermissionError` al construir el widget, y
  `get_icon_path()`/`load_svg()` usaban `Path.exists()`, que también propaga el
  error con un padre inaccesible.
- **Pasos para reproducir:** `IconManager().load_svg("app", 40)` devolvía `None`
  (ahora un `QPixmap` de 40×40 no nulo); `IconManager(<carpeta sin permiso de
  escritura>)` lanzaba `PermissionError: [Errno 13] .../assets`.
- **Estado:** Resuelto.
- **Prioridad:** Media (interfaz sin iconos y caída del widget en instalaciones
  de solo lectura).
- **Solución aplicada:** `QSvgRenderer` se importa de `PyQt6.QtSvg` con
  respaldo a `QtSvgWidgets`; `_ensure_icons_dir` tolera `OSError` y las
  comprobaciones de ruta usan `lib.file_ops.path_exists`.
- **Pruebas:** `tests/test_icon_manager_readonly.py` (5 nuevas; las de
  renderizado fallan con el código anterior).
- **Commit:** se registra en el cierre del cuadragésimo octavo ciclo.
- **Fecha de resolución:** 2026-11-25.

## R-5a9c3e72 — La suite escribía en el `data/pm.data` real y desviaba `BASE_DIR` a `/tmp`

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-25
- **Descripción:** varios tests construyen la GUI real y guardan ajustes a
  través de `get_pm_data()`, que devuelve el almacén global. Al ejecutar
  `pytest tests/` ese almacén es el real (`data/pm.data`), así que la suite
  escribía en la configuración del usuario. Peor aún: el guardado deja
  `packagemaker.BASE_DIR` con la ruta del formulario, de modo que un test
  posterior guardaba ese valor en el archivo real y el `BASE_DIR` quedaba
  apuntando a `…/pytest-N/test_path_only_save_does_not_r0/proyectos`. Tras la
  suite, el CLI creaba los proyectos dentro de la carpeta temporal de pytest
  (y ésta desaparece al limpiar `/tmp`). Comprobado: tras
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`, `data/pm.data`
  contenía esa ruta de pytest.
- **Pasos para reproducir:** anotar el `base_dir` de `data/pm.data`, ejecutar
  la suite y volver a leerlo.
- **Estado:** Resuelto.
- **Prioridad:** Media (corrompe la configuración local del desarrollador y
  desvía los proyectos que se creen después).
- **Solución aplicada:** `tests/conftest.py` instala, antes de importar
  `packagemaker`, un `PMDataStore` en una carpeta temporal con `base_dir` y
  `fluthin_apps` dentro de ella, y lo deja como almacén global de la sesión
  (se borra al terminar). Ningún cambio en el código de la aplicación.
- **Pruebas:** `tests/test_suite_store_isolation.py` (3 nuevas). Verificado
  además con un centinela: el `base_dir` real sobrevive a la suite completa.
- **Commit:** se registra en el cierre del cuadragésimo octavo ciclo.
- **Fecha de resolución:** 2026-11-25.

## R-6f3a9d21 — Los acentos bloqueaban «Crear proyecto» y «Compilar»

- **Usuario:** JesusQuijada34 (auditoría interna; regresión de Q-002/R-5d8e2a41)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Alta (bloquea la creación de proyectos a usuarios que escriben
  su nombre o su marca con acentos; no hay pérdida de datos).
- **Descripción:** al crear un proyecto con un fabricante o un nombre interno
  acentuado (`Jesús`, `Ñandú`, `café`), el asistente respondía «Fabricante: usa
  solo letras, números o guiones» y no creaba nada, aunque la ley de nombres
  admite esos valores: `ProjectNameFormatter.transliterate()` los convierte a
  ASCII (`Jesús` → `Jesus`, `Ñandú` → `Nandu`) desde la aprobación de Q-002.
- **Pasos para reproducirlo:**
  1. Abrir «Crear proyecto», rellenar fabricante `Jesús` y nombre `ñandú`.
  2. Pulsar el botón de creación: el formulario se bloquea con el error de
     fabricante y no se crea la carpeta.
  3. Equivalente por código:
     `validate_build_fields("jesús", "ñandú", "1.0", "AlphaCube")` devolvía dos
     errores (`empresa` y `nombre`).
- **Causa raíz:** `lib/blindcubeEngine/build_validation.py` (`_segment_error`)
  validaba el texto tal cual contra `^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$`, sin la
  transliteración que aplica el formatter. La puerta estricta juzgaba un valor
  distinto del que después se usa para el nombre canónico.
- **Solución aplicada:** `_segment_error` valida
  `ProjectNameFormatter.transliterate(value).strip()`. Los segmentos realmente
  inválidos (`My Company.`, `a_b`, `in fluent`, `a/b`) siguen bloqueados y un
  valor compuesto solo por marcas combinantes sigue contando como vacío. Sin
  cambios en el nombre canónico ni en las plantillas.
- **Pruebas:** `tests/test_build_validation_accents.py` (11 casos; 8 fallan con
  el código anterior).
- **Commit:** se registra en el cierre del cuadragésimo noveno ciclo.
- **Fecha de resolución:** 2026-11-25.

## R-9b4c7e52 — El updater lanzaba `ValueError` con metadatos remotos no canónicos

- **Usuario:** JesusQuijada34 (auditoría interna)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Media (traceback en `updater.py --check`/`--silent`; en la GUI
  el diálogo lo capturaba y sólo mostraba «Exception error»).
- **Descripción:** si el `<version>`, el publisher o el app del proyecto remoto
  no son canónicos (una etiqueta `1.0 beta`, un publisher `My Company.`), la
  búsqueda del `.iflapp` de actualización terminaba con
  `ValueError: Versión inválida…` en lugar de informar de que no hay paquete.
- **Pasos para reproducirlo:**
  1. `_fR("Influent", "demo", "1.0 beta", "Danenone", "Influent")` →
     `ValueError`.
  2. `updater.py --check` con `_rXml_r()` devolviendo `1.0 beta` imprimía el
     traceback completo (la ruta `--silent` también, porque `update_app()` no
     está envuelta).
- **Causa raíz:** `lib/coreUpdater/core.py::_fR` llamaba a
  `ProjectNameFormatter.format_iflapp_filename()` sin proteger el `ValueError`
  que lanza la ley de nombres con metadatos no canónicos.
- **Solución aplicada:** `_fR` captura `ValueError`, registra
  `[WARN] Metadatos remotos no canónicos; se omite el .iflapp: …` y devuelve
  `None`. Los llamadores ya trataban `None` como «no hay paquete», así que el
  updater informa «no hay actualización» en vez de romperse. Un nombre canónico
  produce exactamente la misma URL que antes.
- **Pruebas:** `tests/test_updater_noncanonical_metadata.py` (9 casos; 5 fallan
  con el código anterior).
- **Commit:** se registra en el cierre del cuadragésimo noveno ciclo.
- **Fecha de resolución:** 2026-11-25.

## R-2e8f4a17 — `_check_url_exists` dejaba escapar URL imposibles sin `requests`

- **Usuario:** JesusQuijada34 (auditoría interna)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Baja (sólo afecta a instalaciones sin `requests`, que no es una
  dependencia declarada; el `updater.py` empaquetado puede correr así).
- **Descripción:** el respaldo `urllib` de `_check_url_exists` sólo capturaba
  `OSError`/`URLError`. Una URL con caracteres no ASCII (`Jesús`) lanzaba
  `UnicodeEncodeError` y una con espacios o un byte NUL lanzaba
  `http.client.InvalidURL`; ambas escapaban hasta `updater.py --check`.
- **Pasos para reproducirlo:** con `requests = None`,
  `_check_url_exists("https://example.invalid/Jesús.iflapp")` →
  `UnicodeEncodeError`; con un espacio o `\x00` → `InvalidURL`.
- **Causa raíz:** la sonda es *best-effort* pero no contemplaba los errores de
  validación de URL (`ValueError`/`HTTPException`) que no son `OSError`.
- **Solución aplicada:** el respaldo captura
  `(OSError, ValueError, urllib.error.URLError, http.client.HTTPException)` y
  la rama de `requests` añade `ValueError`; cualquier URL imposible se trata
  como «no existe», igual que un 404.
- **Pruebas:** `tests/test_updater_noncanonical_metadata.py` (9 casos; 3 de las 9
  pruebas de la sonda fallan con el código anterior).
- **Commit:** se registra en el cierre del cuadragésimo noveno ciclo.
- **Fecha de resolución:** 2026-11-25.

## R-7e2d9c14 — El CLI no arranca si falta `requests`

- **Usuario:** JesusQuijada34 (auditoría interna)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Alta.
- **Descripción:** `packagemaker.py` hacía `import requests` en el nivel
  superior aunque esa biblioteca sólo se usa para descargar un icono por URL.
  En una máquina sin `requests` el programa abortaba con `ImportError` antes de
  leer los argumentos, así que ni `--app-version` ni ninguna acción headless
  funcionaban.
- **Pasos para reproducirlo:** con un `requests.py` en `PYTHONPATH` que lanza
  `ImportError`, ejecutar `python packagemaker.py --app-version` → traceback y
  código 1.
- **Causa raíz:** dependencia opcional importada de forma incondicional en el
  punto de entrada; el resto de módulos (`lib/coreUpdater/core.py`,
  `lib/blindcubeEngine/BuildThread.py`, `lib/python_portable_manager.py`) ya la
  trataban como opcional.
- **Solución aplicada:** `try/except ImportError` con `requests = None`. La
  descarga de iconos comprueba el valor y lo informa como aviso
  («requests no está instalado: no se puede descargar el icono») en vez de
  fallar con `AttributeError`; el resto del programa sigue igual.
- **Pruebas:** `tests/test_cli_without_requests.py` (2 casos).
- **Commit:** se registra en el cierre del quincuagésimo ciclo.
- **Fecha de resolución:** 2026-11-25.

## R-3a8f6b25 — La consola del editor abortaba el proceso con comillas sin cerrar

- **Usuario:** JesusQuijada34 (auditoría interna)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Media (pérdida del trabajo sin guardar al abortar el editor).
- **Descripción:** el campo de entrada de la consola de `pmCodeEditor` es el
  slot `returnPressed` → `_execute_input`. Para comandos `pip`/`python` se llama
  a `shlex.split`, que lanza `ValueError: No closing quotation` con una comilla
  sin cerrar; la excepción escapaba del slot y PyQt6 abortaba el proceso.
- **Pasos para reproducirlo:** abrir el editor, escribir en la consola
  `pip install "paquete` y pulsar Intro.
- **Causa raíz:** la división de argumentos no contemplaba el error de sintaxis
  de `shlex` en un punto de entrada de la interfaz.
- **Solución aplicada:** `_execute_input` y `run_command` capturan `ValueError`
  y escriben «[ERROR] Comando no válido: …» en la consola en vez de lanzar;
  `run_command` devuelve `False`. `_normalize_shell_command_list` conserva su
  contrato (sigue lanzando) para quien valide antes de ejecutar.
- **Pruebas:** `tests/test_editor_console_command_parsing.py` (4 casos).
- **Commit:** se registra en el cierre del quincuagésimo ciclo.
- **Fecha de resolución:** 2026-11-25.

## R-9d5c1e73 — El updater headless no arranca sin PyQt6

- **Usuario:** JesusQuijada34 (auditoría interna)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Media.
- **Descripción:** `updater.py` importaba PyQt6 en el nivel superior y
  `lib/coreUpdater/workers.py` lo hacía con `QObject`/`pyqtSignal`, pese a que
  el updater se usa en modo headless (`--version`, `--check`, `--install
  --silent`) y en servidores sin interfaz. Sin PyQt6 abortaba con `ImportError`
  antes de leer los argumentos.
- **Pasos para reproducirlo:** con un paquete `PyQt6` en `PYTHONPATH` que lanza
  `ImportError`, ejecutar `python updater.py --version` → traceback.
- **Causa raíz:** la misma que ya se corrigió para `leviathan_ui`
  (R-4d7b2e91), pero el respaldo no cubría Qt.
- **Solución aplicada:** en `updater.py` el import de Qt va en `try/except` con
  sustitutos inertes y la marca `PYQT6_AVAILABLE`; las rutas que exigen ventana
  (`--install` sin `--silent` y la GUI sin argumentos) llaman a `_require_gui()`,
  que informa «esta operación necesita PyQt6 … usa --silent» y sale con 1.
  `lib/coreUpdater/workers.py` define `QObject`/`pyqtSignal` inertes cuando no
  hay Qt, de modo que `--install --silent` ejecuta el worker de verdad. El
  comportamiento con PyQt6 instalado es idéntico.
- **Pruebas:** `tests/test_updater_optional_dependencies.py` (6 casos nuevos
  con PyQt6 bloqueado).
- **Commit:** se registra en el cierre del quincuagésimo primer ciclo.
- **Fecha de resolución:** 2026-11-25.

## R-2c7e5a91 — `version.res` declaraba `5,15,3,0` en todos los proyectos

- **Usuario:** JesusQuijada34 (auditoría interna del quincuagésimo primer ciclo)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Media.
- **Descripción:** `src/templates/project/version.res.template` traía
  `FILEVERSION 5,15,3,0` y `PRODUCTVERSION 5,15,3,0` escritos a mano, así que
  todo proyecto creado declaraba la versión de Windows del propio PackageMaker
  en lugar de la suya. `version.res` viaja dentro del paquete y es el recurso
  que se compila con `windres`/`rc`, por lo que el ejecutable resultante
  mostraba «Versión de archivo 5.15.3.0» para cualquier aplicación.
- **Pasos para reproducirlo:** crear un proyecto con versión `2.4.1` y abrir
  `version.res` → `FILEVERSION 5,15,3,0` y `PRODUCTVERSION 5,15,3,0`, mientras
  `StringFileInfo` sí decía `2.4.1`.
- **Causa raíz:** la plantilla nunca recibió marcadores para los campos
  numéricos; `build_variables()` sólo calculaba las cadenas `FILE_VERSION` y
  `PRODUCT_VERSION`.
- **Solución aplicada:** nuevo `numeric_version()` en
  `lib/makeselfEngine/templates.py` (``1.0.0`` → ``1,0,0,0``, relleno a cuatro
  campos y límite de `WORD` a 65535) expuesto por
  `lib/makeselfEngine/template_engine.py`; `build_variables()` publica
  `FILE_VERSION_NUMERIC` y `PRODUCT_VERSION_NUMERIC`, y la plantilla los usa.
  `lib/projectFactory.create_version_res()` (ruta heredada) rellena las mismas
  variables con su argumento `version`. La cadena `ProductVersion` no cambia.
- **Pruebas:** `tests/test_project_template_metadata.py`
  (`NumericVersionTests`, `VersionResourceTests`).
- **Commit:** se registra en el cierre del quincuagésimo primer ciclo.
- **Fecha de resolución:** 2026-11-25.

## R-8d4b1f63 — `create` descartaba el nombre visible del proyecto

- **Usuario:** JesusQuijada34 (auditoría interna del quincuagésimo primer ciclo)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Alta.
- **Descripción:** la acción `create` del CLI (y la pantalla de creación del
  TUI, que la invoca) pasaba el *shortname* también como nombre visible a
  `create_project_from_templates()`. El nombre escrito en `--name` /
  «nombre visible» se perdía: `details.xml` quedaba con `<name>demo</name>`,
  el README se titulaba `# demo`, el `ProductName` de `version.res` era
  «Influent demo …» y la cabecera `.iflapp` mostraba «App: demo (demo)».
- **Pasos para reproducirlo:** `python packagemaker.py create --name "Demo App"
  --shortname demo --author Jesus --publisher Influent --version 2.4.1
  --platform linux --headless` → `details.xml` con `<name>demo</name>`.
- **Causa raíz:** en `lib/cliHandler.py` la llamada usaba `app_id` en el cuarto
  argumento (`name`) en lugar del nombre visible; nadie leía
  `project_source['name']` para ese campo.
- **Solución aplicada:** `display_name` se calcula desde `--name` (con
  `app_id` como respaldo si viene vacío) y se pasa a
  `create_project_from_templates()`. El nombre de carpeta y el ejecutable
  siguen saliendo del *shortname*, así que la ley canónica no cambia.
- **Pruebas:** `tests/test_project_template_metadata.py`
  (`CliVisibleNameTests`).
- **Commit:** se registra en el cierre del quincuagésimo primer ciclo.
- **Fecha de resolución:** 2026-11-25.

## R-5a3e9d72 — Los `autorun` generados no lanzaban la aplicación

- **Usuario:** JesusQuijada34 (auditoría interna del quincuagésimo primer ciclo)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Alta.
- **Descripción:** `autorun` (y `autorun.bat`) ejecutaban
  `/usr/bin/python3 ./<app>.py`. Esa ruta absoluta no existe en Termux, en
  macOS ni en contenedores con el intérprete en otro prefijo, y el `.py` no
  viaja en el paquete: el artefacto compilado es `<app>` (nativo) o
  `<app>.pyz` (zipapp), porque `_copy_package_files()` excluye `*.py`. Además
  el guion se creaba con permisos `0644`, así que `./autorun` respondía
  «Permission denied». Resultado: el lanzador de todos los paquetes fallaba.
- **Pasos para reproducirlo:** empaquetar un proyecto, extraer el `.iflapp` y
  ejecutar `sh autorun` → `/usr/bin/python3: not found` (código 127); con
  `./autorun` → permiso denegado.
- **Causa raíz:** plantillas escritas para el árbol de fuentes, sin contemplar
  el artefacto compilado ni el intérprete del sistema, y sin `chmod`.
- **Solución aplicada:** las plantillas `autorun`/`autorun.bat` se colocan en
  su propio directorio y eligen el artefacto disponible en este orden:
  binario nativo (`<app>` / `<app>.exe`), `<app>.pyz` y, por último, el guion
  `<app>.py` con `python3` (o `python` si no hay `python3`). Nuevo
  `_make_executable()` en `lib/makeselfEngine/templates.py` que marca el
  `autorun` como ejecutable al crear y al reparar el proyecto (`OSError` se
  ignora: en Windows no aplica).
- **Pruebas:** `tests/test_project_template_metadata.py` (`AutorunTests`).
- **Commit:** se registra en el cierre del quincuagésimo primer ciclo.
- **Fecha de resolución:** 2026-11-25.

## R-7a5d2c94 — El programa no arranca sin PyQt6

- **Usuario:** JesusQuijada34 (auditoría interna del quincuagésimo segundo ciclo)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Alta.
- **Descripción:** sin PyQt6 —o cuando su import falla por una biblioteca de
  sistema ausente, como `libEGL.so.1`— `packagemaker.py` abortaba con
  `NameError: name 'QPushButton' is not defined` (o `pyqtSignal`,
  `QGroupBox`, `QGridLayout`, `Qt`…) antes de leer los argumentos. Ni
  `--app-version`, ni `--list-compilers`, ni `--inspect`, ni la TUI llegaban a
  ejecutarse, aunque `main()` tiene una rama explícita para `not
  PYQT6_AVAILABLE` que debería caer en la TUI.
- **Pasos para reproducirlo:** en una máquina sin PyQt6 (o con
  `PYTHONPATH` apuntando a un `PyQt6/__init__.py` que lanza `ImportError`):
  `python packagemaker.py --app-version` → traceback con `NameError` y código
  de salida 1.
- **Causa raíz:** los respaldos de `except ImportError` eran incompletos.
  `lib/settings_cards.py` sólo definía `QFrame = QWidget = object` pero usa
  `QPushButton`, `QLabel`, `QHBoxLayout`, `QScrollArea`, `Qt`… en el cuerpo de
  las clases; `lib/github_login_landing.py` sólo definía `QWidget`;
  `lib/github_profile_card.py` no definía `pyqtSignal`; `lib/iflapp_ide_dialog.py`
  tampoco; `lib/pm_dashboard.py` no definía `QGroupBox`; y el bloque de
  `packagemaker.py` no cubría los nombres usados en anotaciones
  (`QGridLayout`, `QTextEdit`, `QStackedWidget`, `QApplication`…).
- **Solución aplicada:** se añadió a cada respaldo el mismo sustituto inerte
  `_QtStub` (metaclase que devuelve el propio sustituto para cualquier
  atributo) y se asignaron a él todos los nombres importados en el `try`, de
  modo que el módulo se puede importar sin Qt y la GUI sigue usando las clases
  reales cuando PyQt6 está disponible. `lib/iflapp_ide_dialog.py` conserva sus
  `QWidget`/`QDialog` que lanzan `ImportError` al instanciarse, porque el
  panel del IDE no puede funcionar sin Qt; sólo se completó `pyqtSignal`.
- **Pruebas:** `tests/test_cli_without_pyqt6.py` (7 casos: `--app-version`,
  `--list-compilers`, `--list-engines`, `--list-hardening`, `--list-fonts`,
  importación de los seis módulos de UI y ausencia de ruido de depuración).
  Con el código anterior fallan 6 de los 7.
- **Commit:** se registra en el cierre del quincuagésimo segundo ciclo.
- **Fecha de resolución:** 2026-11-25.

## R-2f6c8a13 — `print("font: none")` de depuración en cada arranque sin Qt

- **Usuario:** JesusQuijada34 (auditoría interna del quincuagésimo segundo ciclo)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Baja.
- **Descripción:** la rama sin PyQt6 de `packagemaker.py` ejecutaba
  `print("font: none", file=sys.stderr)` al importarse el módulo. Cada
  invocación headless (o la TUI) sin Qt escribía esa línea de depuración en
  stderr, ruido que los scripts que tratan stderr como fallo pueden
  interpretar como error.
- **Pasos para reproducirlo:** `PYTHONPATH=<PyQt6 roto> python
  packagemaker.py --app-version 2>&1` → `font: none` antes de la versión.
- **Causa raíz:** resto de depuración del respaldo de fuentes sin Qt.
- **Solución aplicada:** se eliminó la línea; `app_font()`/`code_font()` ya
  devuelven `None` en ese caso.
- **Pruebas:** `tests/test_cli_without_pyqt6.py::test_no_stray_font_debug_output`.
- **Commit:** se registra en el cierre del quincuagésimo segundo ciclo.
- **Fecha de resolución:** 2026-11-25.

## R-9c7e4a21 — La clave `build_log.folder_locked` faltaba en español e inglés

- **Usuario:** JesusQuijada34 (auditoría interna del quincuagésimo tercer ciclo)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Baja.
- **Descripción:** `BuildThread` compone los avisos de limpieza con
  `tr("build_log.folder_locked")` dentro de `folder_remove_failed`,
  `package_folder_remove_failed` y `source_remove_failed`. La clave existía en
  los 12 idiomas traducidos, pero no en `lang/es.json` ni en `lang/en.json`, así
  que en español (idioma por defecto) y en inglés el aviso mostraba el
  identificador crudo: «No se pudo eliminar build: build_log.folder_locked».
- **Pasos para reproducirlo:** `python -c "from lib.i18n import tr;
  print(tr('build_log.folder_locked'))"` → imprimía `build_log.folder_locked`.
  En un build real basta con que una carpeta temporal siga bloqueada por un
  proceso hijo para que aparezca el aviso.
- **Causa raíz:** la clave se añadió sólo a `tools/translations_curated.py` para
  los idiomas no ingleses, y `tests/test_i18n_curated.py::_used_keys()` sólo
  recorría `lib/*.py`, no los subpaquetes de motor (`lib/blindcubeEngine/`).
  Ninguna prueba exigía que una clave usada por `tr()` existiera en `es.json` o
  `en.json`, sólo que los demás idiomas tuvieran las claves de `es.json`.
- **Solución aplicada:** se añadió `folder_locked` a `lang/es.json` («todavía en
  uso por otro proceso») y a `lang/en.json` («still in use by another
  process»). La auditoría de i18n recorre ahora `lib/**/*.py` y una prueba nueva
  comprueba que toda clave usada por `tr()` existe en los dos catálogos de
  origen.
- **Pruebas:** `tests/test_i18n_curated.py::test_every_used_key_exists_in_the_source_catalogs`
  (con el catálogo anterior informa de `build_log.folder_locked`) y
  `test_every_used_key_has_a_real_translation` con el recorrido recursivo.
- **Commit:** se registra en el cierre del quincuagésimo tercer ciclo.
- **Fecha de resolución:** 2026-11-25.

## R-4b8f2d63 — El framework vendorizado no carga si falta Pillow

- **Usuario:** JesusQuijada34 (auditoría interna del quincuagésimo tercer ciclo)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Media.
- **Descripción:** `lib/leviathan_ui/inmojiTrx.py` importaba `PIL` en el nivel
  del módulo y `lib/leviathan_ui/__init__.py` importa `InmojiTrx`, así que sin
  Pillow fallaba el `import` de todo el framework vendorizado. El puente
  devolvía `None` y la aplicación caía en los respaldos no-op: se perdían la
  barra de título personalizada, el splash y los efectos de ventana sin ningún
  aviso. Pillow sólo hace falta para generar iconos.
- **Pasos para reproducirlo:** con `PYTHONPATH` apuntando a un `PIL` falso que
  lanza `ImportError`, `python -c "from lib.leviathan_ui import WipeWindow"`
  terminaba en `ModuleNotFoundError: No module named 'PIL'`.
- **Causa raíz:** una dependencia opcional (generación de iconos) se importaba
  al cargar el paquete, de modo que su ausencia deshabilitaba el framework
  completo.
- **Solución aplicada:** el import de Pillow está protegido (`Image =
  ImageDraw = ImageFont = None` si falta); `generate_ico()` devuelve `None` con
  un mensaje claro y `apply_to_app()` usa un `QIcon()` vacío. Se declara
  `Pillow` en `lib/requirements.txt`, porque los iconos de la barra de tareas y
  de los accesos `.desktop` sí lo necesitan.
- **Pruebas:** `tests/test_engine_packages_layout.py::test_vendored_framework_imports_without_pillow`
  (subproceso con un `PIL` que lanza `ImportError`; falla con el código
  anterior).
- **Commit:** se registra en el cierre del quincuagésimo tercer ciclo.
- **Fecha de resolución:** 2026-11-25.

## R-2e6d9b14 — La notificación de error revienta si falta `pyperclip`

- **Usuario:** JesusQuijada34 (auditoría interna del quincuagésimo tercer ciclo)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Media.
- **Descripción:** `lib/notificationSystem.error_handler()` ejecutaba
  `import pyperclip` antes de construir la notificación. `pyperclip` no es una
  dependencia del proyecto, así que en una instalación sin él la propia
  notificación de error lanzaba `ModuleNotFoundError` y el usuario no veía el
  error. Al llamarse desde un slot de Qt, PyQt6 habría abortado el proceso.
- **Pasos para reproducirlo:** sin `pyperclip` instalado,
  `python -c "import lib.notificationSystem as n; n.error_handler('Error',
  'fallo')"` → `ModuleNotFoundError: No module named 'pyperclip'`.
- **Causa raíz:** dependencia opcional del portapapeles importada en la ruta
  principal de la notificación, no dentro del botón «Copiar».
- **Solución aplicada:** el import vive ahora dentro de `copy_error()`; si falta
  `pyperclip` se usa `QApplication.clipboard().setText(...)`, y si tampoco hay
  portapapeles se escribe el log traducido sin propagar la excepción.
- **Pruebas:** `tests/test_notification_error_handler.py` (dos casos: copia con
  el portapapeles de Qt sin `pyperclip`, y ausencia total de portapapeles sin
  excepción).
- **Commit:** se registra en el cierre del quincuagésimo tercer ciclo.
- **Fecha de resolución:** 2026-11-25.

## R-8a3f1c72 — Al cambiar de idioma la mayor parte de la interfaz sigue en español

- **Usuario:** JesusQuijada34 (reporte en `bugs.txt`, commit `bba72d6`)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Alta.
- **Descripción:** al cambiar el idioma, sólo se actualizan el sidebar, su
  descripción, el interruptor de sandbox y el selector de motor. Las pestañas
  de creación, compilación y configuración, las descripciones de las tarjetas,
  «Acerca de» y el botón de cerrar sesión de GitHub siguen en español. Además,
  una parte de los textos está escrita directamente en español y no pasa por
  `tr()`.
- **Pasos para reproducirlo:** abrir Configuración → Idioma, elegir English y
  recorrer las cinco páginas: la mayor parte de los textos sigue en español.
- **Causa raíz:** `apply_ui_language()` sólo retraduce un puñado de widgets;
  las páginas se construyen una sola vez al arrancar y no tienen un método de
  retraducción. Hay cadenas fijas en varios módulos de UI.
- **Estado:** Resuelto el 2026-11-25 (quincuagésimo cuarto round).
- **Solución aplicada:** `lib/live_i18n.py` retraduce la ventana **en el sitio**,
  sin reconstruir páginas, así que no se pierde lo escrito en los formularios.
  Construye un índice inverso `texto -> clave` con los 14 ficheros de `lang/`
  (y otro de plantillas tipo `Versión {version}`), recorre el árbol de widgets
  y vuelve a traducir `text`, `placeholderText`, `toolTip`, los ítems de
  `QComboBox` y las pestañas de `QTabWidget`. Nunca toca el texto que escribe
  el usuario (`QLineEdit`, editores). `apply_ui_language()` lo invoca al final.
  Se extrajeron además las cadenas fijas: el botón «Diagnosticar» pasó a
  `moonfix.scan` y la rejilla de información del sistema mostraba las claves
  crudas (`app_version`, `is_compiled`, …) y ahora usa `sysinfo.*` traducidas.
  Medición real con la ventana construida: **de 72 textos sin traducir a 16**,
  y los 16 restantes son marcas, versión, licencia, autor y valores crudos.
- **Commit:** (este round)
- **Fecha de resolución:** 2026-11-25

## R-6b2f8d43 — El build falla con «archivo en uso por otro proceso»

- **Usuario:** JesusQuijada34 (reporte en `bugs.txt`, commit `bba72d6`)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Alta.
- **Descripción:** durante la compilación aparecen errores de que un archivo
  está siendo usado por otro proceso. El propietario sospecha que el flujo
  intenta mover el artefacto en vez de copiarlo.
- **Pasos para reproducirlo:** compilar en Windows con el ejecutable o un
  archivo del paquete abierto por otro proceso y revisar el punto exacto del
  fallo. El reporte no incluye la traza completa.
- **Causa raíz:** `create_package()` y `_copy_package_files()` usaban `shutil`
  crudo: `shutil.rmtree(dest)` sin reintentos, `shutil.copytree`/`copy2` y un
  `shutil.rmtree(package_path, ignore_errors=True)` al fallar el paquete. En
  Windows un archivo del paquete anterior abierto por otro proceso (antivirus,
  ejecutable todavía en marcha) hacía que la copia lanzara `WinError 32`; la
  excepción escapaba de `run()`, que sólo tiene `finally`, y mataba la QThread.
  La limpieza y el movimiento final ya usaban `remove_tree`/`copy_file`, pero la
  copia del paquete no.
- **Estado:** Corregido y probado con bloqueos simulados (`WinError 32`);
  pendiente de verificación en Windows con la traza original. No se marca como
  resuelto del todo hasta esa comprobación.
- **Solución aplicada:** nuevo `copy_tree()` en `lib/file_ops.py`, que reintenta
  ante bloqueos incluso cuando `copytree` los agrupa en `shutil.Error`, y
  `dirs_exist_ok=True` para refrescar un paquete existente sin borrarlo antes.
  `_copy_package_files()` usa `remove_tree`, `copy_tree` y `copy_file` para la
  copia del proyecto, los archivos obligatorios y los binarios de `dist`;
  `create_package()` limpia con `remove_tree` y lista con `list_directory`. Un
  fichero que no se libera se registra con `[WARN]` y la compilación termina con
  un error legible en vez de matar el hilo.
- **Pruebas:** `tests/test_engine_isolation.py`
  (`test_copy_tree_refreshes_an_existing_destination`,
  `test_copy_tree_retries_when_copytree_groups_a_lock`,
  `test_copy_package_files_tolerates_a_locked_destination`,
  `test_copy_package_files_logs_and_continues_when_a_file_stays_locked` y
  `test_package_copy_uses_the_retrying_helpers`). Las cinco fallan con el
  código anterior.
- **Commit:** `main` (quincuagésimo cuarto ciclo, 2026-11-25).
- **Fecha de resolución:** pendiente de verificación en Windows.

## R-9e5c3d84 — Los radios no siguen los estados QSS normal/hover/pressed

- **Usuario:** JesusQuijada34 (reporte en `bugs.txt`, commit `bba72d6`)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Baja.
- **Descripción:** los radios deben definirse en QSS: normal, un círculo con
  borde gris; hover, relleno con el acento del sistema o del programa; pressed,
  el borde crece hacia dentro y se hace más grueso conservando el color del
  hover.
- **Pasos para reproducirlo:** abrir Configuración y pasar el ratón o pulsar
  los radios; los estados no coinciden con la especificación.
- **Causa raíz:** `qradiobutton.qss` sólo definía reposo, hover (cambiaba el
  borde a blanco) y checked; no había relleno de acento en hover, ni estado
  `pressed` con el borde creciendo hacia dentro, ni variantes `checked:hover`,
  `checked:pressed` y `disabled`.
- **Estado:** Resuelto el 2026-11-25 (quincuagésimo cuarto ciclo).
- **Solución aplicada:** `source/qss/qradiobutton.qss` define el indicador en
  reposo con borde gris (`TEXT_DIM`), hover con borde y relleno de acento,
  pressed con borde de 3px del mismo acento (crecimiento hacia dentro) y relleno
  de acento, checked con anillo de 5px, `checked:hover`/`checked:pressed` con
  `ACCENT_HOVER` y `disabled` atenuado. `radio_qss()` pasa `TEXT_DIM`,
  `TEXT_FAINT` y `ACCENT_HOVER`.
- **Pruebas:** `tests/test_qss_loader.py`
  (`test_radio_indicator_defines_normal_hover_and_pressed_states`).
- **Commit:** `main` (quincuagésimo cuarto ciclo, 2026-11-25).
- **Fecha de resolución:** 2026-11-25.


## R-9b3e7a41 — La tabla del entorno se rotulaba siempre en español

- **Usuario:** JesusQuijada34 (issue #12, «problema de idioma»; reporte enviado
  desde la aplicación)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Media
- **Descripción:** al usar la aplicación en otro idioma, la tabla comparativa
  del entorno que se adjunta a los reportes seguía mostrando `Dato`/`Valor` en
  español y no indicaba el idioma activo.
- **Pasos para reproducir:** cambiar la interfaz a inglés, abrir «Reportes» y
  mirar la vista previa del entorno; las etiquetas seguían en español.
- **Causa raíz:** `environment_markdown()` usaba literales en español y el
  snapshot no publicaba el idioma de la interfaz.
- **Estado:** Resuelto y verificado el 2026-11-25 (quincuagésimo séptimo
  ciclo).
- **Solución aplicada:** `lib/report_telemetry.py` resuelve las etiquetas con
  `_env_label()` contra las claves `env.*` de los 14 catálogos de `lang/`,
  publica el campo `language` y cae al texto español si falta la traducción.
  Verificado en vivo: es `Sistema operativo`/`Idioma`, en `Operating
  system`/`Language`, ja `オペレーティングシステム`/`言語`, ar
  `نظام التشغيل`/`اللغة`.
- **Pruebas:** `tests/test_report_extension.py` (idioma de la tabla).
- **Commit:** `1655007` (quincuagésimo sexto ciclo, 2026-11-25).
- **Fecha de resolución:** 2026-11-25.


## R-1f6c9d38 — Descripción de página fuera del sidebar

- **Usuario:** JesusQuijada34 (issue #11, «Orden»; reporte enviado desde la
  aplicación)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Media
- **Descripción:** el issue pide eliminar el cuadro de contexto del sidebar y
  mover la descripción debajo del título de la pestaña, en la barra de
  acciones y fuera del recuadro, como detalle de la opción.
- **Pasos para reproducir:** no es un fallo; es una mejora visual solicitada.
- **Causa raíz:** la descripción vivía en un `desc_card` del sidebar y las
  páginas no tenían un subtítulo en su barra de acciones.
- **Estado:** Resuelto (primera parte del issue #11) y verificado el
  2026-11-25 (quincuagésimo séptimo ciclo). El resto del issue queda como
  Q-021…Q-026.
- **Solución aplicada:** se eliminan `desc_card`, `sidebar_desc_text` y las
  reglas `QWidget#SidebarContextCard`; `install_page_action_bar()` expone
  `subtitle_label` y `set_action_bar_subtitle()` para dibujar el detalle bajo
  el título y fuera de la píldora. AIDE y Configuración reciben barra. El
  subtítulo se retraduce en vivo en todas las páginas.
- **Pruebas:** `tests/test_privacy_switch_and_addons_ui.py` y
  `tests/test_activity_bar_and_subtitle.py`.
- **Commit:** `1655007` (quincuagésimo sexto ciclo, 2026-11-25).
- **Fecha de resolución:** 2026-11-25.


## R-7d2a5b84 — Barra de actividad marquee bajo el action bar

- **Usuario:** JesusQuijada34 (reporte en `bugs.txt`, commit `bba72d6`)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Media
- **Descripción:** se pidió una barra de actividad fina bajo las barras de
  acción que indique trabajo en segundo plano en lugar del diálogo con barra
  de progreso.
- **Pasos para reproducir:** no es un fallo; es una mejora de interfaz.
- **Causa raíz:** las tareas largas mostraban un diálogo bloqueante.
- **Estado:** Resuelto y verificado el 2026-11-25 (quincuagésimo séptimo
  ciclo).
- **Solución aplicada:** `lib/activity_bar.py` añade un marquee fino bajo cada
  barra de acciones, siempre presente pero inactivo hasta que hay trabajo; el
  guardado automático de Configuración ya lo enciende.
- **Pruebas:** `tests/test_activity_bar_and_subtitle.py`.
- **Commit:** `1655007` (quincuagésimo sexto ciclo, 2026-11-25).
- **Fecha de resolución:** 2026-11-25.


## R-4b8f1e27 — Sin PyYAML la ventana no abría

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Alta
- **Descripción:** sin PyYAML, `load_addons()` devolvía una lista vacía, el
  sidebar se quedaba sin botones y la construcción de la ventana reventaba en
  `self.btn_create.setChecked(True)`.
- **Pasos para reproducir:** ejecutar la aplicación en un entorno sin PyYAML.
- **Causa raíz:** el motor de addons sólo tenía la ruta YAML y no un respaldo.
- **Estado:** Resuelto y verificado el 2026-11-25 (quincuagésimo séptimo
  ciclo).
- **Solución aplicada:** `load_addons()` cae a `fallback_addons()` cuando
  PyYAML no está disponible.
- **Pruebas:** `tests/test_privacy_switch_and_addons_ui.py`.
- **Commit:** `1655007` (quincuagésimo sexto ciclo, 2026-11-25).
- **Fecha de resolución:** 2026-11-25.

## R-4c1a9e72 — Claves sobrantes en `lang/` impedían retraducir el envío automático

- **Usuario:** auditoría interna del ciclo 58 (sin reporte externo); misma
  familia que el issue #12 «problema de idioma» y el #11 «Orden», ambos del
  propietario JesusQuijada34.
- **Fecha del reporte:** 2026-11-26
- **Prioridad:** Media
- **Descripción:** con la interfaz en inglés (o en cualquier idioma distinto
  del español), al cambiar de idioma la casilla «Enviar los fallos
  automáticamente…» y su pista de la página **Reportes** se quedaban en inglés.
  Además, 12 de los 14 catálogos de `lang/` llevaban claves planas sobrantes
  (`report.auto_send`, `report.auto_send_hint` dentro del objeto `report`, y
  `form.author_placeholder` dentro de `create`) que al aplanarse creaban
  claves inexistentes o colisionaban con las reales.
- **Pasos para reproducirlo:** abrir la aplicación, poner la interfaz en inglés
  y cambiar a alemán; la casilla y la pista de Reportes siguen en inglés.
  Equivalente en código:
  `live_i18n.key_for("Send failures automatically when a GitHub session exists")`
  devolvía `report.report.auto_send` en vez de `report.auto_send`.
- **Causa raíz:** `live_i18n.reverse_index()` indexa por **valor** sobre todos
  los catálogos. La clave sobrante de `ar.json` (primer fichero por orden
  alfabético) aportaba el texto inglés bajo `report.report.auto_send`; el
  catálogo destino resolvía esa clave al mismo texto inglés, así que
  `target == current` y la retraducción no cambiaba nada.
- **Solución aplicada:** se retiraron las claves planas sobrantes de los 13
  catálogos afectados —el valor traducido de `form.author_placeholder` se
  trasladó a su clave anidada para no perder ninguna traducción— y
  `lib/live_i18n.py` sólo indexa claves que existen en el catálogo español
  (la lista canónica), tanto en `reverse_index()` como en `template_index()`.
  Ningún valor visible cambió salvo el esperado: el texto aplanado de cada
  catálogo es idéntico salvo las dos claves sobrantes eliminadas (comprobado
  con `git show HEAD:lang/<x>.json`).
- **Pruebas:** `tests/test_translation_catalog_hygiene.py` (5 casos: sin claves
  planas con punto, mismas claves que `es.json`, marcador de Autor traducido,
  índice inverso sólo con claves canónicas y retraducción del texto inglés del
  envío automático a de/fr/ja/zh). Tres de ellos fallan con los catálogos
  anteriores y con `live_i18n` sin el filtro.
- **Commit:** el del ciclo 58 en `main` (ver `CHANGELOG.md`).
- **Fecha de resolución:** 2026-11-26
- **Estado:** Resuelto, probado y retirado de `bugs.md` el 2026-11-26 (ciclo 61) tras un ciclo completo sin reaparición.
  No cambia el comportamiento del engine ni el formato de los paquetes.

## R-4e7a1d92 — Configuración con dos barras de acciones y retroceso sin nombre

- **Usuario:** JesusQuijada34 ([issue #14](https://github.com/JesusQuijada34/packagemaker/issues/14),
  «Tarjetas y problema de interfaz»)
- **Fecha del reporte:** 2026-11-26
- **Prioridad:** Media
- **Descripción:** «en configuracion hay dobles action bars y no hay uno solo y
  los botones estan dispersos, al abrir el panel privacidad el boton que
  retrocede a configuracion no tiene nombre». La página dibujaba dos barras
  —la de la página y la cabecera propia del panel— y, tras cualquier
  retraducción, el botón de retroceso de los detalles aparecía como «‹» sin
  texto.
- **Pasos para reproducirlo:** abrir **Configuración** y mirar la parte
  superior (dos barras: «Configuración» y la cápsula del panel con
  «‹ Privacidad»); o cambiar el idioma de la interfaz y entrar en cualquier
  tarjeta: la cápsula queda en «‹  » sin el nombre.
  En código: `SettingsPanel.retranslate()` seguido de `_open("privacy")`
  producía `_titles == {}` y `navigationChanged` con un título vacío.
- **Causa raíz:** tres defectos acumulados.
  1. `SettingsPanel` montaba su propia `SettingsHeader` (cápsula + botón
     Confirmar) **además** de la barra compartida que instala
     `init_config_tab`, así que la página tenía dos barras y los botones
     quedaban repartidos entre ambas.
  2. `SettingsPanel.retranslate()` reconstruía `_titles` con una lista fija de
     cinco tarjetas (general, appearance, fonts, language, notifications) que
     no incluía **privacy**; `_open()` pintaba entonces `""` y la cápsula se
     quedaba sin nombre. Además el prefijo «‹» impide que
     `live_i18n.retranslate_tree()` recupere el texto por valor, así que nada
     lo reparaba después.
  3. La cabecera del panel tenía `apply_soft_shadow()` sobre un widget
     translúcido: la sombra se dibujaba alrededor del texto de la cápsula
     («texto con fondo detrás»).
- **Solución aplicada:** una sola barra por página.
  - `SettingsPanel` ya no crea cabecera: emite `navigationChanged(título,
    profundidad, texto_confirmar)` desde `_on_depth_changed` y expone
    `go_back()`/`confirm_and_go_back()` públicos.
  - `init_config_tab` instala la barra compartida con un botón de retroceso
    **con nombre** (`‹  Configuración`, de `config.title`) y el botón
    `Confirmar` (`config.confirm`), visibles sólo dentro de un detalle;
    `_on_config_navigation()` los sincroniza.
  - Los títulos de las tarjetas se guardan con su clave i18n
    (`_title_keys`) y `retranslate()` los reconstruye desde las claves: las
    siete tarjetas, Privacidad incluida, sobreviven al cambio de idioma.
  - `SettingsNavigator` expone `busy()` y anuncia la profundidad definitiva al
    terminar el deslizamiento, de modo que la barra no se queda desfasada si
    se pulsa atrás durante la animación. Se retiró la clase `SettingsHeader`
    (sin uso) y su sombra.
- **Pruebas:** `tests/test_settings_navigation_bar.py` (11 casos: una sola
  barra, título de raíz, título/retroceso/confirmar del detalle, detalle de
  selección única sin Confirmar, vuelta a la raíz, títulos de las siete
  tarjetas tras `retranslate()`, retroceso con nombre tras retraducir, señal
  de navegación, cambio de idioma a inglés y vuelta a español, doble pulsación
  durante la animación y Confirmar). Los 11 fallan con el código anterior
  (comprobado con `git stash` de los tres ficheros modificados).
- **Commit:** el del ciclo 59 en `main` (ver `CHANGELOG.md`).
- **Fecha de resolución:** 2026-11-26
- **Estado:** Resuelto, probado y retirado de `bugs.md` el 2026-11-26 (ciclo 61) tras un ciclo completo sin reaparición.
  No cambia el comportamiento del engine, la ley de nombres, el formato
  `.iflapp` ni el contenido de los paquetes.
