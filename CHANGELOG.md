# Changelog

## 2026-11-22

### Corregido — robustez del IDE headless (escaneo, compilación y depuración)

Hallazgos del decimocuarto ciclo de mantenimiento (sin reporte externo; reportados por JesusQuijada34 en la auditoría interna). Commit `38f0791`.

- **R-7f3a9c21 — Un `config/settings.json` con `build` no-objeto rompía `--ide-scan`:** `_declared_scripts()` hacía `data.get("build", {}).get("scripts")`. Si el fichero era un objeto pero `build` era una lista, una cadena, `null` o un número, la segunda llamada lanzaba `AttributeError`: `--ide-scan` terminaba en traceback, `--ide-scan-json` contaminaba la salida JSON y la página del IDE no podía construir el proyecto. Ahora `build` debe ser un objeto para leer `scripts`; en caso contrario se usa el descubrimiento de `.py` de la raíz.
- **R-2c8e5d14 — `--ide-compile` lanzaba traceback con una carpeta inexistente:** `IflappIdeHelper.compile()` llamaba a `compile_project()` sin protección. `scan_project()` lanza `FileNotFoundError` si la ruta no es un proyecto y `mkdir()` puede lanzar `OSError` si `--ide-output` apunta a un archivo. Ahora el helper captura `OSError` y responde `[ERROR] No se pudo compilar el proyecto: …` con código 1.
- **R-5a1f8e63 — `--ide-debug` dejaba escapar las excepciones del guion depurado:** `debug_script()` solo capturaba `OSError` y `SyntaxError`, así que un `ZeroDivisionError`, un `RuntimeError` o un `SystemExit` del guion llegaban al CLI o al hilo de la UI en lugar de rellenar `DebugOutcome.error`. Ahora cualquier fallo del guion, incluido `SystemExit`, se devuelve como error del resultado de depuración.

### Verificación — decimocuarto ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 804 pasan, 1 omitido, 43 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Las 6 pruebas nuevas fallan con el código anterior (comprobado con `git stash` de `lib/iflapp_ide.py` y `lib/cliHandler.py`).
- `--ide-scan --ide-scan-json` con `{"build": []}` emite JSON parseable; `--ide-compile /tmp/no-existe` responde `[ERROR]` y código 1 sin traceback; `debug_script()` sobre un guion con `1/0` devuelve `DebugOutcome(error=…)`.

### Aprobaciones — `CONFIRM.MD`

- `CONFIRM.MD` revisado: `Q-001`…`Q-010` siguen sin casillas marcadas y el último commit que toca el archivo no es de `JesusQuijada34`, así que no hay respuestas que aplicar. No se implementó ninguna mejora ni cambio de engine.

## 2026-11-22

### Corregido — configuraciones locales corruptas tumbaban el arranque y el editor

Hallazgos del decimotercer ciclo de mantenimiento (sin reporte externo; reportados por JesusQuijada34 en la auditoría interna). Commit `7ce7a84`.

- **R-4e7c2b91 — Una caché de sesión o un fichero de idioma corruptos impedían arrancar:** `session_cache.load_session()` hacía `data.get("token")` sin comprobar que el JSON descifrado fuera un objeto y `dict(profile)` sin comprobar que el perfil fuera un objeto. Un documento `[]` lanzaba `AttributeError` y un perfil como `["login"]`, `ValueError`. La llamada ocurre en `start_session_gate()` al terminar el splash, sin `try`, así que la GUI abortaba al arrancar. Del mismo modo, `i18n._load_lang_file()` devolvía cualquier JSON y `_flatten_translations()` hacía `.items()`: un `lang/es.json` con `[]` reventaba en `i18n.initialize()`, antes de crear la ventana. Ahora `load_session()` descarta documentos que no sean objeto y degrada un `profile` no-objeto a `{}`; `_load_lang_file()` ignora ficheros que no contengan un objeto y `_flatten_translations()` devuelve `{}` ante una entrada no-objeto.
- **R-9a3d6f20 — Una configuración local con forma no-objeto rompía el editor y «Abrir con»:** `pm_dashboard.load_config()` asignaba la lista a `self.config` y después llamaba `.get()` (`AttributeError`), y un `recent_projects` no-lista reventaba al iterarlo; `python_portable_manager._load_config()` hacía `.get().items()` y `data["path"]` sobre formas inesperadas (`AttributeError`/`TypeError`), de modo que el gestor de intérpretes no se podía construir; y `ProjectConfig` (`get_project_editor`, `set_project_editor`, `get_editor_path`, `set_editor_path`) asumía que `projects`/`editors` eran objetos, así que `_on_accept()` de «Abrir con» fallaba al pulsar «Siempre». Ahora cada lector exige un objeto JSON, degrada las secciones no-objeto (`recent_projects`, `installations`, `projects`, `editors`) a su valor por defecto e ignora entradas de instalación incompletas.

### Verificación — decimotercer ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 799 pasan, 1 omitido, 39 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- 7 de las 11 pruebas nuevas fallan con el código anterior (comprobado con `git stash` de los cinco módulos corregidos).
- Build real `create` + `--buildthis --compiler zipapp --no-sandbox --harden integrity`: `.iflapp` válido (`verify_iflapp() → valid: True`, 21 archivos) y `--inspect-json` lo lee.

### Corregido — robustez de `.mexf` y del shell nativo

Hallazgos del duodécimo ciclo de mantenimiento (sin reporte externo; reportados por JesusQuijada34 en la auditoría interna). Commit `935da3c`.

- **R-9b4e7a52 — Un `.mexf` v1 con secciones mal tipadas rompía `--compile-mexf` y `--debug-mexf`:** `validate_mexf()` solo comprobaba `triggers`, `commands` y `assets`. Un documento con `shortcuts`/`environments` no-objeto o `file_associations`/`context_menus`/`registry`/`runtime` no-lista pasaba la validación y reventaba después en `merge_documents()` (`dict(valor)`/`list(valor)`) o en `MexfDebugger.__init__()` (`.items()` sobre `environments`). Ahora la validación rechaza esas formas con un `MexfError` legible y las rutas de fusión y depuración normalizan cada sección con `isinstance`, de modo que el CLI responde `[ERROR]` con código 1 en vez de un traceback.
- **R-2f7c8d31 — El identificador `.mexf` escapaba del directorio de integración:** `install_plan()`, `uninstall_plan()` y los renderizadores de `.desktop` usaban `metadata.id` como nombre de fichero sin sanear. Un `id` con `../` escribía el XML MIME y los lanzadores fuera de `share/applications` y `--uninstall-mexf-shell` podía borrar archivos ajenos; además, los valores con saltos de línea podían inyectar claves en el `.desktop`. Ahora un nombre saneado (`_file_stem`) se usa en todas las rutas y `_flat_value()` aplana `Name`/`Exec`/`Icon` y `environment.d`. El identificador visible del plan no cambia.
- **R-6a1d3c94 — Un `.mexf` no UTF-8 provocaba traceback:** `parse_mexf()` leía con `utf-8-sig` sin capturar `UnicodeDecodeError`, así que un archivo binario abortaba `--shell-plan`, `--compile-mexf` y `--debug-mexf`. Ahora se traduce a `MexfError` y `detect_mexf_format()` devuelve `"unknown"`.
- **R-8e5b2f17 — `lib.native_shell --info` sin archivo lanzaba traceback:** el entrypoint hacía `args[1]` sin comprobar la longitud y no capturaba los errores de `package_info()`. Ahora responde con uso (código 2) o `[ERROR]` (código 1).

### Aprobaciones — `CONFIRM.MD`

- Se creó `CONFIRM.MD` como canal único de aprobación del propietario, con 10 preguntas pendientes: `Q-001`…`Q-004` (telemetría, acentos, capitalización del publisher y `compile-only`) y `Q-005`…`Q-010` (aislamiento BlindCube/FlatCube, pruebas y `.env`, reorganización y GlassCube, coreografía de splash, rediseño de UI y sidebar). Ninguna está aprobada y no se aplicó ningún cambio de engine.

### Verificación — duodécimo ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 788 pasan, 1 omitido, 39 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Los 16 casos nuevos fallan con el código anterior (comprobado con `git stash` de los módulos corregidos).
- `--compile-mexf` y `--debug-mexf` con `shortcuts: 5` o `environments: [A, B]` terminan en `[ERROR]` y código 1; un `.mexf` binario ya no lanza traceback; `install_plan()`/`uninstall_plan()` con `id: "../../evil/demo"` mantienen todas las rutas dentro de `base_dir` y no borran archivos externos; `python -m lib.native_shell --info` sin argumento devuelve uso (2) y con archivo desconocido `[ERROR]` (1).

### Corregido — accesos directos `.asksome` y robustez de `.mexf` legacy

Hallazgos del undécimo ciclo de mantenimiento (sin reporte externo; reportados por JesusQuijada34 en la auditoría interna). Commit `6fa3c51`.

- **R-7e3a9c14 — Los accesos directos `.desktop` no citaban rutas con espacios:** `_write_linux_desktop()` escribía `Exec={sys.executable} {launcher}` sin comillas. Si la carpeta de instalación (`--install-root`) o el home contienen espacios (`/home/ana/My Apps/...`), el lanzador parte la ruta en varios argumentos e intenta ejecutar una ruta truncada, así que la aplicación instalada no abre desde el menú. `create_desktop_file()` de `lib/linux_icon_handler.py` tenía el mismo defecto. Además, `Name` y `Comment` copiaban el nombre sin aplanar, de modo que un `name` con saltos de línea inyectaba claves nuevas en el `.desktop`. Ahora `_desktop_exec_quote()` cita cada argumento del campo `Exec` y escapa `\`, `"`, backtick, `$` y los códigos de campo (`%` → `%%`); `_desktop_text()` aplana nombre y comentario.
- **R-4b8d2f61 — Un `install.json` corrupto rompía `--build-removeme`:** `read_record()` hacía `json.loads()` y `InstallRecord(**data)` sin validar. Un registro truncado lanzaba `JSONDecodeError`; un documento que no era objeto o al que le faltaban campos lanzaba `TypeError`. Como el CLI solo captura `AsksomeInstallError`, ambos casos terminaban en un traceback. Ahora `read_record()` valida la lectura y la forma del documento y traduce los fallos a `AsksomeInstallError` legible, que el CLI muestra como `[ERROR]` con código 1.
- **R-9c5f1e28 — Un `.mexf` legacy con tipos inesperados rompía `--shell-plan`:** los documentos JSON legacy se convertían sin validar sus tipos. `shell_commands` como entero lanzaba `TypeError` al iterarlo; una sección `extensions`/`context_menus` no iterable, `environments` que no fuera objeto o `shortcuts` que no fuera diccionario rompían igualmente el plan con `TypeError`/`AttributeError`/`ValueError`. Ahora `_legacy_to_v1()` normaliza las secciones a lista o diccionario y convierte los metadatos a texto, y `plan_from_document()` usa `_as_list()`/`_as_dict()` para no confiar en el tipo de ninguna sección.

### Verificación — undécimo ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 547 pasan, 1 omitido, 39 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Las 6 pruebas nuevas fallan con el código anterior (comprobado con `git stash` de los archivos corregidos).
- Instalación real de un `.asksome` en `/tmp/pm e2e/My Installed Apps` con accesos en `My Shortcuts`: el `.desktop` generado contiene `Exec="…" "…"` citado (antes la ruta con espacios quedaba sin comillas).
- `--build-removeme` sobre un `install.json` corrupto termina con `[ERROR]` y código 1, sin traceback.
- `--shell-plan` sobre un `.mexf` legacy con `extensions`, `shell_commands` y `context_menus` de tipo inesperado funciona sin traceback.

## 2026-11-21

### Corregido — robustez de arranque y contenedores `.asksome`

Hallazgos del octavo ciclo de mantenimiento (sin reporte externo; reportados por JesusQuijada34 en la auditoría interna). Commit `543e173`.

- **R-1f4a7c92 — Un `pm.data` o `settings.json` con forma no-objeto impedía arrancar:** `PMDataStore.load()` solo capturaba errores de sintaxis u E/S. Un `data/pm.data` que seguía siendo JSON válido pero no un objeto (`[]`, `"texto"`, `42`, `null`) reventaba en `_ensure_structure()` con `TypeError`, y como `packagemaker.py` carga `APP_CONFIG` al importarse, la aplicación no arrancaba ni en GUI ni en CLI. Lo mismo ocurría con `user`, `readonly` o `translation_cache` de otro tipo y con un `config/settings.json` que fuera una lista (`AttributeError` en la migración). Ahora el documento no-objeto se descarta, cada sección se reconstruye conservando las claves válidas de las demás y la migración ignora un `settings.json` no-objeto.
- **R-2b6d8e13 — Las cabeceras `.asksome` malformadas rompían `--shell-info` y la verificación:** `read_asksome_header()` no comprobaba que el tamaño declarado cupiera en el archivo ni la forma del JSON. Una cabecera `[]` terminaba en `AttributeError` en `verify_asksome()`, `extract_asksome()`, `package_info()` e `icon_bytes()`; `metadata` como lista o `manifest` no lista daban `TypeError`; un icono base64 inválido abortaba el hover del shell. Ahora una lectura única valida tamaño, JSON y tipos, y el shell ignora iconos no decodificables.
- **R-3c9e1a57 — La extracción `.asksome` aceptaba rutas de unidad y exponía errores crudos:** `_safe_member()` solo rechazaba rutas POSIX absolutas y `..`, así que una entrada `C:/Windows/...` o `C:archivo` pasaba y en Windows resolvía fuera del destino. Además, un payload LZMA/TAR corrupto salía como `LZMAError`/`ReadError`. Ahora se rechazan rutas absolutas, unidades de Windows, `..` y cualquier resolución que escape, se comprueban symlinks preexistentes y los errores se traducen a `AsksomeError`.

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

Hallazgo del tercer ciclo de mantenimiento (sin reporte externo; reportado por JesusQuijada34 en la auditoría interna). Commit `e84e367`.

- **R-b3f71a6c — Un publisher o identificador fuera de la ley de nombres rompía el CLI:** `create`, `--buildthis`, `compile` y `moonfix` llamaban a `format_project_folder()` sin capturar el `ValueError`, así que un publisher como `Jesús` terminaba en un traceback. En `--buildthis` el proyecto se compilaba completo y el fallo aparecía al final, sin generar artefacto. Ahora `_canonical_folder_or_exit()` valida antes de compilar y aborta con `[ERROR] Metadatos de proyecto no válidos: …` y código 1; `create` y `moonfix` usan la misma validación. La ley de nombres no cambia.

### Corregido — selección de proyecto y verificación cifrada

Hallazgos del cuarto ciclo de mantenimiento (sin reporte externo; reportados por JesusQuijada34 en la auditoría interna). Commit `ab79f4a`.

- **R-7c1e4a90 — `compile`/`moonfix` compilaban el proyecto equivocado:** la búsqueda usaba `publisher in nombre and app in nombre`, así que con `demo` y `demo2` en la misma carpeta elegía `demo2`; además, si la carpeta base no existía, `iterdir()` terminaba en un traceback. Ahora ambos usan `locate_project()`, que compara la identidad canónica de la carpeta, cae a `details.xml` solo para carpetas no canónicas y devuelve un error legible si no hay carpeta base.
- **R-91b6d2f4 — La verificación en sandbox no descifraba los paquetes con `--password`:** el script del sandbox llamaba a `extract_iflapp()` sin contraseña, así que todo build cifrado avisaba «verificación incompleta» y quedaba sin verificar. La contraseña viaja por `IFLAPP_VERIFY_PASSWORD` (entorno, no `argv`) y se pasa a `extract_iflapp(..., password=...)`.

### Corregido — pureza de salida del CLI

Hallazgos del quinto ciclo de mantenimiento (sin reporte externo; reportados por JesusQuijada34 en la auditoría interna). Commit `7f708bb`.

- **R-3a7c5e18 — Los avisos de importación contaminaban las acciones JSON:** la falta de `leviathan_ui` imprimía `[WARN] Leviathan UI unavailable…` en stdout (y sin PyQt6 se añadía `font: none`), así que `--inspect-json`, `--shell-plan-json`, `--shell-info-json` y `--ide-scan-json` dejaban de ser parseables. Ahora esos avisos van a stderr. Es una regresión de la misma clase que R-4b7e91a2.
- **R-9f2b64d1 — Los avisos auxiliares rompían el JSON:** `--inspect-extract` y `--shell-preview` añadían su `[OK]`/`[INFO]` a stdout después del documento. Ahora van a stderr en modo JSON y a stdout en modo humano.
- **R-6e04c8ab — El aviso de MoonFix no era codificable en cp1252:** un `details.xml` corrupto hacía `print("⚠ …")`, que lanzaba `UnicodeEncodeError` en consolas Windows y abortaba la reparación. Ahora usa `_safe_print` y escribe en stderr; el fallback a los metadatos del CLI no cambia.

### Corregido — reparación MoonFix

Hallazgo del sexto ciclo de mantenimiento (sin reporte externo; reportado por JesusQuijada34 en la auditoría interna). Commit `c36df67`.

- **R-7d5b91c4 — MoonFix regeneraba la marca temporal y rompía la ley canónica:** `repair_project_from_templates()` escribía `details.xml` con una marca temporal nueva porque ningún llamador pasaba `timestamp`. Tras `moonfix`, una carpeta `influent.demo.v1.0-26.11-10.05-Danenone` contenía `<version>v1.0-26.11-10.06</version>`, así que carpeta y metadatos dejaban de coincidir y cada reparación volvía a mover la marca. Ahora la reparación conserva el timestamp de la carpeta canónica o, si la carpeta es legacy, el de `details.xml`; solo genera uno nuevo cuando el proyecto no tiene ninguno. El arreglo es central y cubre CLI, GUI y `moonFixWizard`.

### Corregido — dropper autoextraíble

Hallazgo del séptimo ciclo de mantenimiento (sin reporte externo; reportado por JesusQuijada34 en la auditoría interna). Commit `325c0e9`.

- **R-3f9a2c71 — El dropper lanzaba `updater.py` en los builds zipapp:** el stub solo probaba `<guion>`, `<guion>.exe` y `<guion>.py`, pero el backend zipapp entrega `<guion>.pyz`. Al no encontrar el punto de entrada, el respaldo ejecutaba el primer `.py` de la raíz del paquete (`updater.py`) y el `.run` quedaba en el actualizador en lugar de arrancar la aplicación. Ahora los candidatos incluyen `.pyz` y el respaldo prefiere artefactos Python compilados antes que los guiones auxiliares.

### Corregido — cabeceras `.iflapp` truncadas

Hallazgo del mismo ciclo de mantenimiento (sin reporte externo; reportado por JesusQuijada34 en la auditoría interna). Commit `850de5c`.

- **R-7b1d4e92 — `--inspect` aceptaba cabeceras truncadas como paquete válido:** `read_iflapp_header()` no comprobaba que la cabecera declarada cupiera en el archivo, así que un `.iflapp` cortado se inspeccionaba con código 0 y `format_version: 0`/identidad vacía; faltando los 4 bytes de longitud lanzaba `struct.error`, y un JSON que no fuera objeto o metadatos de sección no numéricos terminaban en `AttributeError`/`ValueError`. Ahora todos esos casos producen un `IflappError` legible.

### Mantenimiento

- `lib/requirements-dev.txt` resuelve correctamente su include (`-r requirements.txt`) y la documentación usa la ruta real `lib/requirements-dev.txt`.

### Verificación

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 484 pasan, 1 omitido (la dependencia opcional `leviathan_ui` está instalada en este entorno).
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- `--inspect-json` sobre un `.iflapp` con cabecera cortada, JSON `null` o sección fuera del archivo termina con código 1 y un error legible (antes: código 0 con cabecera vacía o excepción cruda).
- Build real con `--compiler zipapp --no-sandbox --dropper`: genera `.iflapp` y `.run`; el `.run` ejecuta `demo.pyz` e imprime `Hola desde demo!` (antes lanzaba `updater.py` y no terminaba).
- Build real con `--compiler zipapp --harden integrity`: `.iflapp` válido con `.iflapp.integrity` en el manifiesto.
- Build real con `--compiler zipapp --password` y sandbox activo: `.iflapp` cifrado y verificación en sandbox `[OK]` (antes «incompleta»).
- `compile` con `demo` y `demo2` elige `demo`; `compile`/`moonfix` sin carpeta base abortan con error legible y código 1, sin traceback.
- `--inspect-json` emite JSON parseable en stdout (banner en stderr).
- Las cuatro acciones JSON emiten JSON parseable sin `leviathan_ui`, incluso combinadas con `--inspect-extract` o `--shell-preview`.
- `moonfix` con `details.xml` truncado y stdout en `cp1252` avisa en stderr y repara sin traceback.
- `create`, `--buildthis` y `moonfix` con metadatos no canónicos abortan con error legible y código 1, sin traceback.
- `create` + `moonfix` reales conservan el mismo sufijo temporal en la carpeta y en `<version>` de `details.xml` (R-7d5b91c4).

### Corregido — robustez del lector de cabeceras `.iflapp`

Hallazgo del octavo ciclo de mantenimiento (sin reporte externo; reportado por JesusQuijada34 en la auditoría interna). Commit `f60f9ac`.

- **R-8a4f1c6d — Una cabecera `.iflapp` con tipos inesperados rompía `--inspect` con traceback:** `read_iflapp_header()` solo validaba que la cabecera fuera un objeto JSON. Un `manifest` que no fuera lista terminaba en `TypeError`; un `payload` que no fuera objeto, en `AttributeError` al leer compresión, cifrado o número de archivos; un `file_count` no numérico, en `ValueError`; una sección mal tipada rompía `--inspect-extract`; y un offset negativo producía un `OSError [Errno 22]` críptico. Ahora `_validate_header_shape()` valida tipos y metadatos numéricos, `_read_section()` y `_payload_bounds()` validan los límites contra el archivo, y las propiedades de `IflappHeader` y `export_header_assets()` toleran formas inesperadas. Todos los casos devuelven un `IflappError` legible.

### Corregido — dependencias del editor, updater y metadatos del CLI

Hallazgos del noveno ciclo de mantenimiento (sin reporte externo; reportados por JesusQuijada34 en la auditoría interna).

- **R-1c93e4b7 — El editor trataba módulos estándar como dependencias de PyPI:** `lib/dependency_manager.py` usaba una lista fija de módulos estándar que omitía `hmac`, `asyncio`, `ctypes`, `email`, `decimal`, `tomllib`, `sysconfig`, `operator`, `shlex`, `signal` o `zoneinfo`. Un script con `import hmac` hacía que el editor escribiera `hmac` en `requirements.txt` e intentara `pip install hmac`. Ahora la lista se une con `sys.stdlib_module_names` (autoridad desde Python 3.10), conservando la lista histórica como respaldo.
- **R-4d7b2e91 — `updater.py` abortaba sin `leviathan_ui`:** el updater se copia a todos los proyectos empaquetados y se usa en modo headless (`--version`, `--check`, `--install`), pero importaba `leviathan_ui` de forma incondicional. Ahora `WipeWindow` tiene un respaldo no-op (mismo patrón que `packagemaker.py` y `lib/window_chrome.py`) y `get_accent_color()` cae a `#0078D4`; `--version` y la validación de argumentos funcionan sin la dependencia opcional.
- **R-6b1f8d20 — `--force-fonts` se ignoraba y abría la TUI:** el flag solo se leía dentro de la rama de `--download-fonts`, así que usado solo no resolvía ninguna acción y arrancaba la interfaz de texto. Ahora implica `--download-fonts all` con `force=True` y respeta las claves si se combinan ambos flags.
- **R-9e2a5c73 — `--app-version` reportaba una versión fija:** el entrypoint importaba el inexistente `version.VERSION` y caía en `3.2.7`, ignorando `details.xml`; `show_version` además imprimía `vv…`. Ahora ambos caminos leen la versión canónica de `details.xml` (`lib.cliHandler.__version__`), normalizan el prefijo y usan «desconocida» si falta. El formato `Influent Package Maker v<versión>` no cambia.
- **R-2a7f6b41 — La cabecera `.iflapp` no coincidía con su `details.xml`:** `create_package()` reescribe `<platform>` con la plataforma objetivo, pero la cabecera conservaba la del proyecto. Un proyecto `AlphaCube` compilado en Linux mostraba `Plataforma: AlphaCube` en `--inspect` y `Danenone` dentro del contenedor. `package_identity()` alinea la cabecera con el XML empaquetado y conserva los metadatos si el XML falta o está dañado.

Commit `64c083a`.

### Verificación — noveno ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 509 pasan, 1 omitido, 35 subtests.
- `python -m pyflakes`, `python -m py_compile` y `ruff` (`F821/F822/F823/F811/F841/B006/B008/B017/B904/E722`) limpios.
- Las 18 pruebas nuevas fallan con el código anterior (comprobado con `git stash` de cada archivo corregido).
- Build real `create` + `--buildthis --compiler zipapp --no-sandbox --harden integrity`: `.iflapp` válido (`verify_iflapp() → valid: True`), `--inspect` muestra la misma plataforma que el `details.xml` interno y `--app-version` informa `v3.2.7-26.05-20.13`.
- `updater.py --version` y `updater.py --accept-license` funcionan con `leviathan_ui` inaccesible (antes: `ModuleNotFoundError`).

### Corregido — blindaje por ofuscación y contenedores de motor

Hallazgos del décimo ciclo de mantenimiento (sin reporte externo; reportados por JesusQuijada34 en la auditoría interna).

- **R-6f2b9d31 — `--harden obfuscate` podía dejar el paquete inservible:** `obfuscate_strings()` localizaba los literales con una expresión regular. Con concatenación implícita (`("parte uno " "parte dos")`) la sustitución producía dos llamadas seguidas, un `SyntaxError`; el blindaje informaba `OK` y el build terminaba, pero el `updater.py` empaquetado ya no se ejecutaba. El patrón además reescribía texto entre comillas dentro de docstrings y f-strings. Ahora el fuente se analiza con `ast` y solo se sustituyen los `ast.Constant` de texto completos; se omiten docstrings, partes literales de f-strings, patrones de `match` y valores de `Literal`/`Annotated`. Un fuente no analizable devuelve `applied=False` sin tocarlo.
- **R-8c4e1a72 — Los contenedores `.blindkpkg`/`.flatkpkg` lanzaban excepciones crudas:** `BuildEngine.read_header()` y `blindcubeEngine.read_header()` no comprobaban que la cabecera declarada cupiera en el archivo (`struct.error`), ni que el JSON fuera un objeto (`TypeError`); un payload LZMA corrupto o parámetros de cifrado incompletos salían como `LZMAError`/`KeyError`, y `flatcubeEngine.unpack()` devolvía `BadZipFile`, `JSONDecodeError` o un manifiesto que no era diccionario. Ahora los tres lectores validan longitudes y tipos y traducen esos fallos a `EngineError`/`BlindCubeError`/`FlatCubeError`. El formato válido no cambia.

### Verificación — décimo ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 521 pasan, 1 omitido, 35 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Las 12 pruebas nuevas fallan con el código anterior (ofuscación por `SyntaxError`; contenedores por `struct.error`/`BadZipFile`).
- Build real `create` + `--buildthis --compiler zipapp --no-sandbox --harden obfuscate`: `.iflapp` válido (`verify_iflapp() → valid: True`), el `updater.py` empaquetado compila con `py_compile`, el `.pyz` del proyecto imprime `Hola desde demoobf!` y la fuente del proyecto queda intacta.

### Pendiente de aprobación

- **R-d23039c0 — Telemetría de errores:** no implementada (envía datos a un servidor externo).
- **R-5d8e2a41 — Acentos en publisher/appname:** no implementada; cambia la ley de nombres.
- **R-4c8e1f27 — Capitalización del publisher:** `create` y la GUI pasan el publisher a minúsculas, así que la carpeta y `details.xml` no conservan la capitalización que exige la ley de nombres. No implementado: cambia los nombres visibles y las rutas de build.
- **R-3e7d1c58 — `compile-only` no retira el fuente del paquete:** el método solo añade el `.pyc` optimizado y el `.py` legible sigue en el artefacto. No implementado: borrar el fuente es destructivo y puede romper el punto de entrada de un build zipapp.
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
