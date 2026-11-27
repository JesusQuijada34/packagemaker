# Bitácora de ciclos de mantenimiento — Influent Package Maker

Histórico de ciclos (estado de casos, verificaciones y decisiones de
release). Se trasladó aquí desde `bugs.md` para que la cola activa quede
por debajo de ~40 KB, según la regla de mantenimiento. No se lee en los
ciclos: es un registro de auditoría.

---

## Periodo de observación y release

- Casos abiertos (quincuagésimo octavo ciclo): 14 — los bugs R-4f8a2c60
  (Q-008/F-003), R-6a1f8c23 (Q-011/F-004), R-4d9e2b61 (Q-019), R-7c4a1e95
  (Q-012/Q-011), R-2f8b6a31 (Q-011/F-004), R-8c4f1a72 (en observación, issue
  #10) y R-4c1a9e72 (corregido en este ciclo, en observación); las mejoras
  R-5a7d2f16 (Q-026), R-3c8e4b72, R-7b3e9a52 (Q-021) y R-2c8d4f71 (Q-022); y
  los cambios de engine R-9a4e2c83 (Q-023), R-5f1b8d24 (Q-024) y R-8e6a3c15
  (Q-025). R-4d8f2b61 se cerró como no reproducido.
- Vigésimo séptimo ciclo (2026-11-23): R-2e7c4a91, R-8b4d1f62 y R-5c9a3e27
  corregidos y probados; no se prepara release.
- Vigésimo octavo ciclo (2026-11-23): R-3b6f9d24 y R-9f4c2a71 corregidos y
  probados (robustez de cachés con `data` de solo lectura); no se prepara
  release.
- Vigésimo noveno ciclo (2026-11-23): R-4a7c2e91 y R-8f1d3b62 corregidos y
  probados (robustez de `data/pmCodeEditor` de solo lectura); no se prepara
  release.
- Trigésimo ciclo (2026-11-23): R-9a4c1e27 corregido y probado (robustez de la
  TUI con rutas sin permisos); no se prepara release.
- Trigésimo primer ciclo (2026-11-23): R-4d8a6c12, R-9e3b7a51 y R-6a2d8f43
  corregidos y probados (arranque con `data/` inaccesible, GUI con rutas sin
  permisos y salida de Termux); no se prepara release.
- Trigésimo segundo ciclo (2026-11-23): R-7e4c1a92, R-2d8b6f31 y R-9a5c3e74
  corregidos y probados (caché de sesión, `config/` del proyecto y `config/`
  de la aplicación ilegibles); no se prepara release.
- Trigésimo tercer ciclo (2026-11-23): R-4e9c1a73, R-7d2f8b14 y R-6b3e9c52
  corregidos y probados (compilación del IDE, reparación de MoonFix y splash
  con proyectos/directorios sin permisos); no se prepara release.
- Trigésimo cuarto ciclo (2026-11-23): R-4b9e2c71 corregido y probado (el
  compilador `.mexf` traduce `PermissionError` a `MexfCompileError`, el paso
  `.mexf` del build se omite en vez de abortar y el icono opcional tolera una
  carpeta `app/` ilegible); no se prepara release.
- Trigésimo quinto ciclo (2026-11-24): R-3f7c1a94, R-6b2e9d47 y R-8c4a1f62
  corregidos y probados (instalación y desinstalación `.asksome` con carpetas
  sin permisos, y `remove_tree` que ya no informa de un borrado inexistente); no
  se prepara release.
- Trigésimo sexto ciclo (2026-11-24): R-4a7e2c91, R-6c9d3f52 y R-8e2b7d64
  corregidos y probados (el CLI `create`, `moonfix`/`repair` y
  `compile`/`--buildthis` ya no muestran tracebacks ante carpetas sin permisos;
  la QThread del build traduce el `OSError` de `dist/` a un fallo con mensaje);
  no se prepara release.
- Trigésimo séptimo ciclo (2026-11-24): R-6f4b8a92, R-1e7c3d58 y R-9b5f2a74
  corregidos y probados (empaquetado de un proyecto inaccesible, «Ejecutar» del
  gestor y «Abrir carpeta» de la TUI dejan de abortar la app); no se prepara
  release.
- Trigésimo octavo ciclo (2026-11-24): R-3f8a7c21, R-9d2b6e45 y R-6c4a1f83
  corregidos y probados (el IDE, el CLI `--ide-compile`, el preflight y el
  blindaje respetan la declaración de codificación PEP 263; un proyecto en ANSI
  ya no aborta la GUI ni imprime tracebacks); no se prepara release.
- Trigésimo noveno ciclo (2026-11-24): R-2a9f4d17, R-5e8c1b42, R-7b3a9e58 y
  R-9c4d2f61 corregidos y probados (el depurador y el detector de dependencias
  respetan PEP 263; un `pm.data` con números no finitos ya no impide arrancar;
  las cabeceras `.iflapp`/`.run` con números no finitos dan `IflappError`); no
  se prepara release.
- Cuadragésimo ciclo (2026-11-24): R-9e1a4c72 y R-4c8b2e91 corregidos y
  probados (`--build-removeme` responde con `[ERROR]` ante una raíz ilegible y
  el depurador `.mexf` trata un comando no ejecutable como fallo con código
  126 en vez de abortar); no se prepara release.
- Cuadragésimo tercer ciclo (2026-11-24): R-4c9e2b71, R-4a7f2c93, R-8d3e6b15 y
  R-2f5c9a71 corregidos y probados (un `.mexf` con `.nan`/`.inf` ya no emite
  `NaN`/`Infinity`; un `pm.data` con rutas o idioma no textuales ya no impide
  arrancar; un acento no hexadecimal ya no aborta las notificaciones con acción
  primaria); no se prepara release.
- Cuadragésimo cuarto ciclo (2026-11-24): R-7a2c9e14 y R-8f3d1b62 corregidos y
  probados (el asistente MoonFix y «Abrir proyecto» del dashboard dejan de
  abortar la app cuando `details.xml` existe pero no se puede leer); no se
  prepara release.
- Verificación del ciclo de R-7a2c9e14 y R-8f3d1b62 (2026-11-24):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 1079 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios. Las 2 pruebas nuevas
  fallan con el código anterior (comprobado con `git stash` de
  `lib/pm_dashboard.py` y `lib/moonFixWizard.py`), con
  `PermissionError: [Errno 13] Permission denied: .../details.xml`.
- Verificación del ciclo de R-4c9e2b71 (2026-11-24):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 1046 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios. Las 3 pruebas nuevas
  fallan con el código anterior (comprobado con `git stash` de
  `lib/mexf_parser.py`). Reproducción real: `--shell-plan-json` con
  `shortcuts: {Ctrl+N: .nan}` y con el JSON legacy `1e400` imprimía `NaN`/
  `Infinity` (rechazado por un parser estricto); ahora imprime `"nan"`/`"inf"`
  y `json.loads(..., parse_constant=...)` lo acepta.
- Verificación del ciclo de R-4a7f2c93…R-2f5c9a71 (2026-11-24):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 1077 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios. Las 31 pruebas nuevas
  de `tests/test_corrupt_user_config_startup.py` pasan; la reproducción previa a
  la corrección dio `TypeError` en `os.makedirs` al importar `packagemaker`,
  `AttributeError` en `i18n.load_translation` y `ValueError` en
  `NotificationWidget` con acento `azul` y acción `primary`. Tras el arreglo,
  `--app-version` arranca con la carpeta por defecto, el idioma cae a `es` y la
  notificación se construye sin error.
- Verificación del ciclo de R-9e1a4c72 y R-4c8b2e91 (2026-11-24):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 1024 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios. Las 3 pruebas nuevas
  fallan con el código anterior (comprobado con `git stash` de
  `lib/blindcubeEngine/asksome_installer.py` y `lib/mexf_debugger.py`).
  Reproducción real: `--build-removeme myapp --install-root <raíz 000>` muestra
  «No se pudo acceder al registro de instalación…» (antes `PermissionError` con
  traceback); `--debug-mexf … --debug-run` con un `executable` `0644` informa
  «falló con código 126» (antes `PermissionError` con traceback).
- Verificación del ciclo de R-2a9f4d17…R-9c4d2f61 (2026-11-24):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 1021 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios. Las 12 pruebas nuevas
  fallan con el código anterior (comprobado con `git stash` de los cinco módulos
  tocados). Reproducción real: `--ide-debug` sobre un `app.py` cp1252 traza el
  guion (antes `[ERROR] UnicodeDecodeError`).
- Verificación del ciclo de R-3f8a7c21…R-6c4a1f83 (2026-11-24):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 1009 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios. De las 17 pruebas
  nuevas de `tests/test_non_utf8_sources.py`, 11 fallan con el código anterior y
  la prueba del panel del IDE **aborta el proceso** (`Fatal Python error:
  Aborted`), comprobado con `git stash` de los seis módulos tocados.
  Reproducción real: `--ide-compile` y `--ide-scan --ide-scan-json` sobre un
  proyecto con `app.py` y `settings.json` en cp1252 responden código 0 y
  compilan el `.pyz` (antes `UnicodeDecodeError`); la copia inyectada
  `<guion>_pmboot.py` conserva la *cookie* cp1252 y el acento del fuente.
- Verificación del ciclo de R-6f4b8a92…R-9b5f2a74 (2026-11-24):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 992 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios. Las 6 pruebas nuevas
  de `tests/test_unreadable_build_and_launch.py` pasan y 5 de ellas fallan con
  el código anterior (comprobado con `git stash` de los cinco módulos tocados).
  Build real `create` + `--buildthis --compiler zipapp --no-sandbox`: `.iflapp`
  de 21 archivos, `verify_iflapp() → valid: True` y `--inspect` coincide con el
  `details.xml` interno.
- Verificación del ciclo de R-4a7e2c91…R-8e2b7d64 (2026-11-24):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 986 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios. Las 5 pruebas nuevas
  de `tests/test_unreadable_paths.py` fallan con el código anterior (comprobado
  con `git stash` de `lib/cliHandler.py` y
  `lib/blindcubeEngine/BuildThread.py`). Reproducción real por CLI: `create` con
  `BASE_DIR` en `chmod 555`, `moonfix` sobre un proyecto `chmod 555` al que le
  falta `docs/` y `--buildthis` sobre un proyecto `chmod -R a-w` terminaban en
  `PermissionError` con traceback; ahora salen con `[ERROR]` y código 1. Build
  real `create` + `--buildthis --compiler zipapp --no-sandbox`: `.iflapp` de 20
  archivos, `verify_iflapp() → valid: True` y `--inspect` coincide con el
  `details.xml` interno.
- Cuadragésimo noveno ciclo (2026-11-25): R-6f3a9d21, R-9b4c7e52 y R-2e8f4a17
  corregidos y probados (los acentos vuelven a pasar la puerta estricta y el
  updater deja de lanzar tracebacks con metadatos remotos no canónicos o URL
  imposibles); se registra además el hallazgo Q-018 (el build del CLI no valida
  `details.xml`) como cambio de comportamiento pendiente de aprobación; no se
  prepara release.
- Verificación del cuadragésimo noveno ciclo (2026-11-25):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 1138 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios. 16 de las 20 pruebas
  nuevas fallan con el código anterior (comprobado con `git stash` de
  `lib/blindcubeEngine/build_validation.py` y `lib/coreUpdater/core.py`).
  Reproducción real: `validate_build_fields("jesús", "ñandú", "1.0",
  "AlphaCube")` devolvía los errores `empresa` y `nombre` (ahora `[]`);
  `_fR("Influent", "demo", "1.0 beta", "Danenone", "Influent")` lanzaba
  `ValueError: Versión inválida…` (ahora `None` + `[WARN]`); con `requests =
  None`, `_check_url_exists("https://example.invalid/Jesús.iflapp")` lanzaba
  `UnicodeEncodeError` y con un espacio o `\x00` `http.client.InvalidURL` (ahora
  `False`).
- Quincuagésimo ciclo (2026-11-25): R-7e2d9c14, R-3a8f6b25 y R-9d5c1e73
  corregidos y probados (el CLI arranca sin `requests`; la consola del editor
  informa de las comillas sin cerrar en vez de abortar el proceso; y el updater
  headless funciona sin PyQt6, avisando cuando la operación necesita ventana);
  no se prepara release.
- Verificación del quincuagésimo ciclo (2026-11-25):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 1150 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios. Reproducción real:
  con un `requests` que lanza `ImportError`, `--app-version` terminaba en
  `ImportError` (ahora código 0); `ConsolePanel._normalize_shell_command_list`
  con `python "sin cerrar` lanzaba `ValueError` dentro del slot (ahora
  `[ERROR] Comando no válido`); y con un paquete `PyQt6` que lanza
  `ImportError`, `updater.py --version`/`--check`/`--install --silent`
  terminaban en traceback (ahora código 0/1 con mensaje, y las rutas de GUI
  explican que necesitan PyQt6).
- Quincuagésimo primer ciclo (2026-11-25): R-2c7e5a91, R-8d4b1f63 y R-5a3e9d72
  corregidos y probados (la versión de Windows de los proyectos generados, el
  nombre visible del CLI/TUI y el lanzador `autorun`); no se prepara release.
- Verificación del quincuagésimo primer ciclo (2026-11-25):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 1161 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios. Las 11 pruebas nuevas
  de `tests/test_project_template_metadata.py` fallan con el código anterior
  (comprobado con `git stash` de los siete archivos tocados). Reproducción real:
  un proyecto `2.4.1` declaraba `FILEVERSION 5,15,3,0` (ahora `2,4,1,0`);
  `create --name "Demo App" --shortname demo` escribía `<name>demo</name>`
  (ahora `Demo App` en `details.xml`, README y `ProductName`); `sh autorun`
  dentro del paquete extraído respondía `/usr/bin/python3: not found` y
  `./autorun` «Permission denied» (ahora ejecuta el artefacto compilado).
- Quincuagésimo segundo ciclo (2026-11-25): R-7a5d2c94 y R-2f6c8a13 corregidos y
  probados (arranque sin PyQt6 y ruido de depuración en stderr); no se prepara
  release.
- Verificación del quincuagésimo segundo ciclo (2026-11-25):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 1168 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios. 6 de las 7 pruebas
  nuevas de `tests/test_cli_without_pyqt6.py` fallan con el código anterior
  (comprobado con `git stash` de los seis archivos tocados). Reproducción real:
  con un paquete `PyQt6` que lanza `ImportError`, `--app-version` abortaba con
  `NameError: name 'QPushButton' is not defined` (ahora imprime la versión y
  sale con 0); `--list-compilers`, `--list-engines`, `--list-hardening`,
  `--list-fonts`, `--ide-scan` y `create --headless` funcionan sin Qt, y la TUI
  arranca en su menú principal. `lib/application_frame_host.py` sigue
  requiriendo PyQt6, pero no lo importa ningún módulo del programa.
- Release: **no preparado**. No se generaron `flat cube` ni `blind cube` en este
  ciclo. El periodo de observación de 3 días y el requisito de 7 días sin
  reportes nuevos siguen en curso.
- Inicio del periodo de observación (3 días): 2026-11-21.
- Requisito de release sin reportes nuevos: 7 días consecutivos.
- Último reporte externo conocido: 2026-11-22, reporte manual del propietario
  en `bugs.txt` (commit `bed2e83`): versión canónica rechazada (corregido como
  R-9d4c2f18) y coreografía del splash (registrada como cambio de engine
  pendiente nº 4, sin implementar). El contador de 7 días sin reportes se
  reinicia el 2026-11-22.
- Verificación del ciclo de R-2e7c4a91…R-5c9a3e27 (2026-11-23):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 930 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios. Con el código
  anterior fallan 17 de las 21 pruebas nuevas de
  `tests/test_config_and_removeme_robustness.py` (comprobado con `git stash` de
  los tres archivos tocados). Reproducción real: `_config_file_path()` devolvía
  `lib/config/settings.json`; un `settings.json` con `[]` daba
  `AttributeError` al leer y `TypeError` al guardar; el `removeme.py` generado
  salía con código 1 y dejaba la app instalada ante un `install.json` con `[]`;
  y la vista previa `.mexf` sólo toleraba `OSError`/`KeyError`.
- Verificación del ciclo de R-4c7a9e13…R-2f8a4d61 (2026-11-23):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 865 pasan, 1
  omitido, 55 subtests; `pyflakes` y `py_compile` limpios. 13 de las 14 pruebas
  nuevas de `tests/test_unreadable_paths.py` fallan con el código anterior
  (comprobado con `git stash` de los 8 archivos tocados). Reproducción real en
  Python 3.13: `--inspect-extract <archivo>`, `--list-asksome` con raíz
  `chmod 000`, `compile` con `BASE_DIR` `chmod 000`, `--buildthis`/`--ide-run`/
  `--shell-info`/`--install-asksome` sobre rutas sin permiso y las dos acciones
  de GUI sobre una carpeta ilegible terminaban en `PermissionError` con
  traceback; ahora responden con `[ERROR] …`, diálogo o «sin artefactos», con
  código 1 (o 0 cuando el resultado es una lista vacía).
- Verificación del ciclo de R-6d2f8a41 (2026-11-22):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 851 pasan, 1
  omitido, 55 subtests; `pyflakes` y `py_compile` limpios. Con el código
  anterior, `--compile-mexf` sobre un proyecto con `details.xml`, `.mexf/main.mexf`
  o el directorio `.mexf/` sin permisos terminaba en `PermissionError` con
  traceback; ahora responde `[ERROR] Compilación .mexf fallida: …` y código 1.
  Las 5 pruebas nuevas fallan con el código anterior (comprobado con
  `git stash` de `lib/mexf_parser.py`, `lib/mexf_compiler.py` y
  `lib/cliHandler.py`). Un proyecto legible sigue generando el `.asksome`
  firmado (`--compile-mexf` → `[OK] Artefacto .asksome generado`, código 0).
- Verificación del ciclo de R-7f2b9c63 (2026-11-22):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 839 pasan, 1
  omitido, 55 subtests; `pyflakes` y `py_compile` limpios. Un `.run` con el
  bloque base64 alterado terminaba en `UnicodeDecodeError`/`JSONDecodeError`
  con traceback; ahora responde `Cabecera .iflapp truncada.`/`Cabecera .iflapp
  corrupta: …` y código 1. Los 4 casos nuevos fallan con el código anterior
  (comprobado con `git stash` de `dropper.py`). Un dropper válido sigue
  ejecutando la app (`Hola desde demo!`, código 0).
- Verificación del ciclo de R-2c7e9b41 y R-5b3d8f27 (2026-11-22):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 835 pasan, 1
  omitido, 55 subtests; `pyflakes` y `py_compile` limpios. Con el código
  anterior, `--buildthis <proyecto> --output /tmp/blocker/out` (archivo normal
  en el camino) termina en `FileNotFoundError`/`NotADirectoryError` con
  traceback; ahora responde `[ERROR] No se pudo preparar la carpeta de salida
  …` y código 1. Un proyecto con `<publisher>Jesús</publisher>` hacía que la
  QThread del build muriera sin emitir `error`; ahora
  `BuildThread.run()` emite `Metadatos de proyecto no válidos: Publisher
  inválido…` y `FlangCompiler.run()` devuelve `None` sin excepción (3 de los 6
  casos nuevos fallan con el código anterior, comprobado con `git stash` de
  `BuildThread.py`).
- Verificación del ciclo de R-6c2a8f14 y R-8b3d1e57 (2026-11-22):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 829 pasan, 1
  omitido, 55 subtests; `pyflakes` y `py_compile` limpios. El subtest de
  `settings.json` no-objeto falla con el código anterior (`AttributeError:
  'list' object has no attribute 'get'`) y la prueba de la raíz de instalación
  falla con `FileExistsError`; ambas pasan con `b656928`. Reproducción real:
  `--install-asksome demo.asksome --install-root /tmp/blocked-root` (archivo
  normal) responde `[ERROR] Instalación .asksome fallida: No se pudo preparar
  la raíz de instalación …` con código 1, sin traceback.
- Verificación del ciclo de R-9d4c2f18 (2026-11-22):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 827 pasan, 1
  omitido, 51 subtests; `pyflakes` y `py_compile` limpios; los 4 casos de
  versión canónica con timestamp fallan con el código anterior (comprobado con
  `git stash` de `build_validation.py`). Reproducción: `v1.0-26.11-22.00`
  bloqueaba la compilación con «Versión inválida»; ahora no produce errores y
  se normaliza a `1.0` para el nombre del artefacto.
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
- Aprobaciones (2026-11-23, vigésimo quinto ciclo): el propietario marcó
  `[x] SÍ` en Q-001, Q-002, Q-003, Q-005, Q-006, Q-009 y Q-010 (commit
  `0ac5457`, autoría verificada con la API de GitHub). Se aplicaron Q-001
  (telemetría opcional), Q-002 (acentos) y Q-003 (capitalización del
  publisher). Q-005/Q-006/Q-009/Q-010 ya estaban implementados y quedan
  verificados. Q-004 se reenvía para aclaración; Q-007 sigue sin aprobar y
  Q-008 se repite porque su respuesta estaba partida por un conflicto de merge.
- Verificación del vigésimo quinto ciclo (2026-11-23):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 892 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios.
- Verificación del vigésimo sexto ciclo (2026-11-23):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 909 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios. Las 13 pruebas
  nuevas de `tests/test_settings_save_guards.py` fallan con el código anterior
  (comprobado con `git stash` de `packagemaker.py`) y la ejecución termina en
  `Fatal Python error: Aborted`, que es exactamente el cierre que sufría la
  aplicación. Medición real offscreen con la ventana construida (348 widgets):
  guardar sólo una ruta pasó de 0,20 s a 0,002 s; un cambio de densidad o de
  modo de presentación repinta el tema una vez (0,10 s) en lugar de dos; un
  cambio de idioma retraduce en 0,006 s; y la elección de FlatCube sobrevive al
  guardado.
- Fuera del repositorio: el propietario pidió añadir el ciclo de recolección de
  mejoras (lunes recoger, viernes probar, sábado revisión visual, domingo
  release) a su automatización «Updater/Update». Esa automatización no vive en
  este repositorio, así que no se puede modificar desde aquí; queda anotado
  para que él lo configure en la plataforma de automatizaciones.
- Verificación del ciclo de R-4f9b2c81, R-7a3d5e62 y R-2b9e4f73 (2026-11-22):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 819 pasan, 1
  omitido, 51 subtests; `pyflakes` y `py_compile` limpios; los 6 casos nuevos
  fallan con el código anterior (comprobado con `git stash` de
  `asksome_installer.py` y `mexf_compiler.py`). Reproducción real: un `.asksome`
  con `id: ".."` borró el padre de la raíz de instalación antes del arreglo;
  ahora se instala en `asksome.app` y el marcador externo sobrevive.
  `--uninstall-asksome "../victim"` y `--build-removeme "../victim"` responden
  `[ERROR] Identificador de app inválido` con código 1 y no tocan el directorio
  externo. `--compile-mexf PROYECTO --mexf-output /tmp` responde `[ERROR]
  Compilación .mexf fallida: … Is a directory` con código 1 (antes traceback).
- Verificación del ciclo de R-3b8e5c71, R-7c4d2a96 y R-1d9f6b34 (2026-11-22):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 809 pasan, 1
  omitido, 51 subtests; `pyflakes` y `py_compile` limpios; los 5 casos nuevos
  fallan con el código anterior (comprobado con `git stash` de los tres
  módulos corregidos). `--uninstall-asksome` con `"shortcuts": 5` en
  `install.json` elimina la instalación sin traceback; un `.blindkpkg` y un
  `.iflapp` con `salt`/`nonce`/`mac` mal tipados devuelven
  `BlindCubeError`/`IflappError`; build real `create` +
  `--buildthis --compiler zipapp --no-sandbox --harden integrity` genera un
  `.iflapp` válido (21 archivos) que `--inspect-json` lee.
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
- Verificación del ciclo de R-4e7c2b91 y R-9a3d6f20 (2026-11-22):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 799 pasan, 1
  omitido, 39 subtests; `pyflakes` y `py_compile` limpios; 7 de las 11 pruebas
  nuevas fallan con el código anterior (comprobado con `git stash` de los cinco
  módulos). Build real `create` + `--buildthis --compiler zipapp --no-sandbox
  --harden integrity` genera un `.iflapp` válido (`verify_iflapp() →
  valid: True`, 21 archivos) e `--inspect-json` lo lee.
- Verificación del ciclo de R-7f3a9c21, R-2c8e5d14 y R-5a1f8e63 (2026-11-22):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 804 pasan, 1
  omitido, 43 subtests; `pyflakes` y `py_compile` limpios; las 6 pruebas nuevas
  fallan con el código anterior (comprobado con `git stash` de
  `lib/iflapp_ide.py` y `lib/cliHandler.py`). `--ide-scan --ide-scan-json` con
  `{"build": []}` emite JSON parseable (antes `AttributeError`);
  `--ide-compile /tmp/no-existe` responde `[ERROR]` y código 1 (antes
  traceback); `debug_script()` sobre un guion con `1/0` devuelve
  `DebugOutcome(error=…)` (antes `ZeroDivisionError`).
- Verificación del ciclo de R-4e8b2d17 (2026-11-22):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 846 pasan, 1
  omitido, 55 subtests; `pyflakes` y `py_compile` limpios; las 4 pruebas nuevas
  fallan con el código anterior (comprobado con `git stash` de
  `lib/cliHandler.py` y `lib/native_shell.py`). `--shell-info` sobre un
  `.iflapp` con permisos `000` responde `[ERROR] … Permission denied` y código
  1 (antes `PermissionError` con traceback); `--shell-info-json` deja stdout
  vacío y el error en stderr; `--shell-preview` sobre un archivo normal responde
  `[ERROR] No se pudo exportar la vista previa: … File exists` sin traceback.
- Verificación del vigésimo noveno ciclo (2026-11-23):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 948 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios. Con el código
  anterior fallan 5 de las 6 pruebas nuevas de
  `tests/test_readonly_data_dir_robustness.py` (comprobado con `git stash` de
  `lib/python_portable_manager.py`, `lib/pm_dashboard.py` y `pmCodeEditor.py`).
  Reproducción real: `PythonPortableManager(base_dir=<carpeta no escribible>)`
  lanzaba `PermissionError` al crear `packages`; apuntar `EDITOR_CONFIG_PATH`
  bajo un archivo lanzaba `NotADirectoryError` en `save_config()` y en
  `_save_editor_config()`.
- Verificación del trigésimo ciclo (2026-11-23):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 955 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios. Los 7 casos de
  `tests/test_tui_unreadable_paths.py` fallan con el código anterior
  (comprobado con `git stash` de `lib/tui.py`). Reproducción real: con
  `chmod 000` sobre el proyecto, `_show_details_xml()`, `_screen_build()` y
  `_screen_moonfix()` lanzaban `PermissionError` con traceback; ahora muestran
  «details.xml no encontrado» o «ruta no válida».
- Verificación del trigésimo primer ciclo (2026-11-23):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 964 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios. Con el código
  anterior fallan 7 de los 9 casos nuevos (comprobado con `git stash` de los
  cinco módulos tocados): arranque con `data/` o `config/` no creable/legible,
  asistente de nuevo proyecto con base `chmod 000`, guion ilegible en el IDE,
  `ProjectConfig` sobre base inaccesible y salida de Termux sin almacenamiento.
- Verificación del trigésimo segundo ciclo (2026-11-23):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 967 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios. Los 3 casos nuevos
  de `tests/test_unreadable_config_paths.py` fallan con el código anterior
  (comprobado con `git stash` de `lib/session_cache.py`,
  `lib/blindcubeEngine/BuildThread.py` y `lib/.walkcube/editorDetector.py`).
  Reproducción real: `--buildthis` sobre un proyecto con `config/` `chmod 000`
  terminaba en `PermissionError` con traceback; ahora responde `[ERROR] No se
  pudo leer config/settings.json: …` y código 1. Con `data/` ilegible,
  `session_cache.load_session()` devuelve `None`; con `config/` de la
  aplicación ilegible, `get_default_editor()` devuelve `None` y
  `save_default_editor()` no lanza.
- Verificación del cuadragésimo primer ciclo (2026-11-24):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 1036 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios. Con el código
  anterior fallan 2 de las 3 pruebas nuevas de `tests/test_mexf_asksome.py` y 6
  de las 9 de `tests/test_i18n_translate_robustness.py` (comprobado con
  `git stash` de `lib/mexf_parser.py` y `lib/i18n.py`). Reproducción real:
  `--compile-mexf`, `--shell-plan` y `--debug-mexf` sobre un `.mexf` YAML con
  `extensions:` mostraban `JSONDecodeError` con traceback; ahora responden
  `[ERROR] … Formato .mexf desconocido` y código 1.
- Verificación del cuadragésimo segundo ciclo (2026-11-24):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 1043 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios. Las 7 pruebas nuevas
  fallan con el código anterior (comprobado con `git stash` de
  `lib/mexf_parser.py` y `lib/mexf_debugger.py`). Reproducción real:
  `--debug-mexf --debug-run` con un `executable` que contiene `\u0000` mostraba
  `ValueError: embedded null byte`; ahora informa `[ failed] … 126`. Un
  `.mexf` con `released: 2024-01-01` abortaba `--compile-mexf` con
  `TypeError: Object of type date is not JSON serializable`; ahora genera el
  `.asksome` y un alias recursivo responde
  `[ERROR] … referencia circular`.
- Verificación del cuadragésimo quinto ciclo (2026-11-24):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 1086 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios. Las 7 pruebas nuevas
  fallan con el código anterior (comprobado con `git stash` de
  `lib/iflapp_ide.py`, `lib/blindcubeEngine/hardware_sandbox.py` y
  `lib/blindcubeEngine/asksome_installer.py`). Reproducción real: con
  `chmod 000` sobre `details.xml`, `--ide-scan` respondía
  `[ERROR] [Errno 13] Permission denied` sin datos (ahora lista `demo.py`);
  `HardwareSandbox().run()` con un *workspace* `chmod 000` propagaba
  `PermissionError` (ahora devuelve 126); el `removeme.py` generado con un
  acceso directo bloqueado mostraba `Traceback ... PermissionError` (ahora
  imprime `omitido: …` y purga la instalación), y con la carpeta de instalación
  de solo lectura responde `error al desinstalar: …` con código 1.
- Release: **no preparado**. No se generaron `flat cube` ni `blind cube` en este
  ciclo. El periodo de observación de 3 días y el requisito de 7 días sin
  reportes nuevos siguen en curso.
- Cuadragésimo séptimo ciclo (2026-11-25): R-2d5b8f41, R-9f3c1a72 y
  R-6b8e4d25 corregidos y probados (updater silencioso veraz, desinstalación de
  Python portable y nombre canónico en el TUI); no se prepara release.
- Verificación del cuadragésimo sexto ciclo (2026-11-25):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 1096 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios. Las 7 pruebas nuevas
  fallan con el código anterior (comprobado con `git stash` de `lib/i18n.py` y
  `lib/blindcubeEngine/compilers.py`). Reproducción real: con un cuerpo de
  respuesta en latin-1, `tr()` lanzaba `UnicodeDecodeError` (ahora devuelve el
  texto original); sin red, cuatro cadenas sin traducir hacían cuatro intentos
  de red (ahora uno por minuto y por idioma); un `main.py` en cp1252 no
  detectaba `main` (ahora el `.pyz` ejecuta `main`).
- Cuadragésimo octavo ciclo (2026-11-25): R-4f7a2c91, R-8b2d4e17 y R-5a9c3e72
  corregidos y probados (aviso de sobrescritura del asistente, iconos SVG y
  aislamiento del almacén en la suite); no se prepara release.
- Verificación del cuadragésimo octavo ciclo (2026-11-25):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 1118 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios. 10 de las 11 pruebas
  nuevas fallan con el código anterior (comprobado restaurando
  `packagemaker.py`, `lib/iconManager.py` y `tests/conftest.py` con
  `git checkout`). Reproducción real: con `IconManager` el icono de 40 px
  devolvía `None` (ahora `QPixmap` 40×40 no nulo); un `data/pm.data` centinela
  se conservaba intacto tras la suite completa; la GUI construye sus 5 páginas
  y el diálogo «Abrir con» sin errores.
- Quincuagésimo tercer ciclo (2026-11-25): R-9c7e4a21, R-4b8f2d63 y
  R-2e6d9b14 corregidos y probados (la clave `build_log.folder_locked` vuelve a
  existir en español e inglés; el framework vendorizado carga sin Pillow y los
  iconos avisan en vez de deshabilitar la interfaz; la notificación de error ya
  no depende de `pyperclip`); no se prepara release.
- Verificación del quincuagésimo tercer ciclo (2026-11-25):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 1172 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios. Las 4 pruebas nuevas
  (i18n de origen, framework sin Pillow y dos del portapapeles) fallan con el
  código anterior; además, la auditoría de i18n ampliada al recorrer los
  subpaquetes del motor detecta la clave ausente. Reproducción real:
  `tr('build_log.folder_locked')` devolvía el identificador crudo; con un `PIL`
  que lanza `ImportError`, `from lib.leviathan_ui import WipeWindow` terminaba
  en `ModuleNotFoundError`; sin `pyperclip`, `error_handler()` lanzaba
  `ModuleNotFoundError`.

- Quincuagésimo tercer ciclo — reportes nuevos (2026-11-25): el commit del
  propietario `bba72d6` añadió 8 reportes (R-8a3f1c72…R-3c8e4b72) y aprobó
  Q-004 (opción A), Q-007, Q-008, Q-011, Q-012, Q-013 y Q-014. Los 8 reportes
  quedan en la cola (5 bugs y 3 mejoras/UI) y **ninguno se marca como resuelto**.
  El periodo de observación de 7 días sin reportes se reinicia en esta fecha;
  no se prepara release.
- Quincuagésimo cuarto ciclo (2026-11-25): R-6b2f8d43 corregido (la copia y la
  limpieza del paquete reintentan ante bloqueos; pendiente de verificación en
  Windows) y R-9e5c3d84 resuelto (estados de los radios). De los 8 reportes del
  commit `bba72d6` siguen abiertos 5 (R-4d9e2b61, R-7c4a1e95, R-2f8b6a31,
  R-5a7d2f16 y R-3c8e4b72), además de R-4f8a2c60 y R-6a1f8c23. No se prepara
  release.
- Limpieza de cola (2026-11-25): se retiraron de este archivo las **156
  entradas resueltas** (conservadas en `docs/bugs_resueltos.md` y detalladas en
  `CHANGELOG.md`) para dejar solo lo abierto, como pidió el propietario
  («ve eliminando los bugs reportados que ya son resueltos y no se repiten
  mas»). Quedan **7 entradas**. En este mismo round se resolvió R-8a3f1c72
  (traducción en vivo: de 72 textos sin traducir a 16, todos ellos marcas,
  versión, licencia, autor y valores crudos) y se retiró también a
  `docs/bugs_resueltos.md`.
- Verificación del quincuagésimo cuarto ciclo (2026-11-25):
  `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` → 1178 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios. Las 5 pruebas nuevas
  de bloqueo de `tests/test_engine_isolation.py` fallan con el código anterior
  (comprobado con `git stash` de `lib/file_ops.py` y
  `lib/blindcubeEngine/BuildThread.py`), y la prueba de los radios falla con el
  `qradiobutton.qss` anterior. Build real `create_project_from_templates` +
  `FlangCompiler.run()` (zipapp): `.iflapp` de 59 KB con `verify_iflapp()` →
  `valid: True`, ejercitando la copia del paquete de extremo a extremo.
- Quincuagésimo sexto ciclo (2026-11-25, commit `1655007`): R-9b3e7a41
  (tabla del entorno traducida, issue #12), R-1f6c9d38 (descripción de página
  bajo el título de la barra de acciones, issue #11), R-7d2a5b84 (barra de
  actividad marquee) y R-4b8f1e27 (sin PyYAML la ventana no abría)
  corregidos y probados; 1292 pasan, 1 omitido, 64 subtests; no se prepara
  release.
- Quincuagésimo séptimo ciclo (2026-11-25): verificación de lo anterior sin
  cambios de código. R-9b3e7a41, R-1f6c9d38, R-7d2a5b84 y R-4b8f1e27 se
  retiran de la cola (probados, en `main`, registrados en `CHANGELOG.md` y en
  `docs/bugs_resueltos.md`, sin reaparición en la suite). Issue #12 cerrado;
  issues #11 y #10 permanecen abiertos (el primero por los cambios de
  engine/mejoras Q-021…Q-026, el segundo por la verificación visual en
  Windows). Suite: 1292 pasan, 1 omitido, 64 subtests; `pyflakes` y
  `py_compile` limpios. No se prepara release: el periodo de observación sigue
  abierto y no han pasado 7 días sin reportes nuevos.
- Quincuagésimo octavo ciclo (2026-11-26): R-4c1a9e72 corregido y probado
  (claves planas sobrantes en `lang/` y filtro de claves canónicas en
  `live_i18n`); 1297 pasan, 1 omitido, 64 subtests; `pyflakes` y `py_compile`
  limpios. Build real de extremo a extremo verificado (`create` → `--buildthis
  --compiler zipapp --harden integrity` → `--inspect` → `verify_iflapp`:
  `valid`). Sin respuestas nuevas del propietario en `CONFIRM.MD`, así que
  sigue bloqueado todo cambio de engine (F-001…F-006 y Q-015…Q-026). No se
  prepara release: hay bugs abiertos de prioridad alta.
- Quincuagésimo noveno ciclo (2026-11-26): aparecen los issues **#13** («Bug de
  codigo») y **#14** («Tarjetas y problema de interfaz»). Se corrige
  **R-4e7a1d92** (Configuración con una sola barra de acciones y retroceso con
  nombre; 11 pruebas nuevas en `tests/test_settings_navigation_bar.py`, todas
  fallan con el código anterior) y se deja en observación. El resto del issue
  #14 y la duración mínima del splash del issue #13 quedan como preguntas
  **Q-027…Q-031** en `CONFIRM.MD`; sin aprobación no se toca el engine.
  Verificación: 1308 pasan, 1 omitido, 64 subtests; `pyflakes` y `py_compile`
  limpios. No se prepara release.
- Sexagésimo ciclo (2026-11-26, push `73dcdcd`): el propietario respondió en
  `CONFIRM.MD` y aprobó **Q-015, Q-017, Q-018, Q-019, Q-020 y Q-021…Q-031**,
  más las confirmaciones finales **F-001, F-002, F-004, F-005 y F-006**, con
  instrucciones adicionales en Q-019 (interruptor **Red**), Q-023 (login por la
  rama `render`), Q-028 (con compatibilidad) y Q-031 (sandbox de DLL y
  restricciones sobre credenciales). **Q-016** quedó escrita como `[B] SÍ`, que
  no es una casilla válida del canal: no se aplica y se vuelve a preguntar. Se
  aplica **R-4f8a2c60** (Q-008/**F-003**): el splash pasa a ser una ventana de
  nivel superior pintada antes de la ventana principal, con `destroy()` al
  cerrar y el mismo arreglo en `updater.py`; queda en observación a la espera
  de la verificación visual en Windows. El resto de aprobaciones (F-001, F-002,
  F-004…F-006 y Q-015, Q-017…Q-031) siguen pendientes de implementación y no se
  mezclan con este arreglo. Verificación: 1317 pasan, 1 omitido, 64 subtests; `pyflakes` y `py_compile`
  limpios; arranque real sin los avisos `must be a top level window`. No se
  prepara release: siguen abiertos bugs de prioridad alta.

- Sexagésimo primer ciclo (2026-11-26, push `71e50f7`): el push sólo toca
  `CONFIRM.MD` y marca **Q-016** como `[X, la B] SÍ` (opción B). Autoría
  verificada (`JesusQuijada34`, `git log -1` y la API de GitHub). Se aplica
  **Q-016**: `create` acepta `--force`, rechaza con `[ERROR] El proyecto ya
  existe` y código 1 cuando la carpeta canónica existe y avisa con `[WARN]` al
  sobrescribir (R-6d2a8f19). Seis pruebas nuevas en
  `tests/test_maintenance_cli_regressions.py` (`CreateOverwriteGuardTests`).
  Limpieza pedida en el issue #15: se retiran de la cola R-4c1a9e72 (ciclo 58) y
  R-4e7a1d92 (ciclo 59), ya resueltas y sin reaparición, archivadas en
  `docs/bugs_resueltos.md`. Los issues **#15** y **#16** (ventanas vacías y
  splash UWP) se atienden con una respuesta en cada uno: el arreglo del splash
  de nivel superior ya está en `main` y la petición de splash dentro de la
  ventana queda como **Q-032**, sin tocar el engine hasta que se apruebe. No se
  prepara release: siguen abiertos bugs de prioridad alta y 21 aprobaciones de
  engine pendientes de implementación.

- Sexagésimo tercer ciclo (2026-11-26): sin respuestas nuevas del propietario
  en `CONFIRM.MD` (sigue sólo **Q-032** pendiente). Se aplica **Q-015**
  (R-7e3a9c25): `_update_from_iflapp(silent=True)` descarga el `.iflapp`, lo
  instala con `install_iflapp(..., silent=True)` en el directorio actual,
  devuelve el resultado real y borra el temporal, sin crear `QApplication` ni
  `ModernUpdaterWindow`. `tests/test_updater_silent_iflapp_update.py` (5 casos;
  los 4 primeros fallan con el código anterior). Se retira de la cola y se
  archiva en `docs/bugs_resueltos.md`. Verificación: 1332 pasan, 1 omitido, 64
  subtests; `pyflakes` y `py_compile` limpios. No se prepara release: quedan
  bugs de prioridad alta y 20 aprobaciones pendientes de implementación.

- Sexagésimo cuarto ciclo (2026-11-26): sin respuestas nuevas en `CONFIRM.MD`
  (sigue sólo **Q-032** pendiente). Se aplica la parte de arrastre de
  **Q-011/F-004** y se corrige **R-6a1f8c23**: el puente ya no llama a
  `start_system_move()` sobre una ventana maximizada. Un clic suelto no la
  toca; al superar 4 px de arrastre se restaura a su tamaño normal bajo el
  cursor y se inicia el movimiento, con respaldo de arrastre manual cuando el
  sistema no ofrece `startSystemMove`. `tests/test_window_manager_bridge.py`
  gana `MaximizedDragTests` (7 casos). La ficha sale de la cola (15
  pendientes) y queda en observación hasta la verificación visual en Windows.
  Verificación: 1340 pasan, 1 omitido, 64 subtests; `pyflakes` y `py_compile`
  limpios. No se prepara release: quedan bugs de prioridad alta y 19
  aprobaciones pendientes de implementación.

- Sexagésimo quinto ciclo (2026-11-26): sin respuestas nuevas en `CONFIRM.MD`
  (sigue sólo **Q-032** pendiente). Se aplica la parte de gestos de
  **Q-011/F-004** y se corrige **R-2f8b6a31**: el filtro de la titlebar contaba
  mal porque Qt entrega el triple clic como pulsación, doble clic y pulsación y
  el doble clic reiniciaba la racha, así que nunca se alcanzaba el tercer
  gesto; ahora el doble clic cuenta como segundo gesto y sigue maximizando o
  restaurando, y el tercero entra en pantalla completa, que además maximiza la
  ventana al entrar (`_ensure_maximized`). El puente ignora el doble clic en
  modo inmersivo para no dejar una ventana sin barra de título.
  `TestTitleBarGestureLimit` (3 casos) e `ImmersiveDoubleClickTests` (2 casos);
  los tres que describen el fallo fallan con el código anterior. A petición del
  propietario en el issue #15 se compactó `bugs.md` (38 KB → 12 KB) y se archivó
  lo resuelto. Verificación: 1345 pasan, 1 omitido, 64 subtests; `pyflakes` y
  `py_compile` limpios. No se prepara release: quedan bugs de prioridad alta y
  19 aprobaciones pendientes de implementación.

- Sexagésimo sexto ciclo (2026-11-26): sin respuestas nuevas en `CONFIRM.MD`
  (sigue sólo **Q-032** pendiente). Se corrige **R-8d3f6a21**, la parte
  reproducible de R-4d9e2b61 («hay errores al compilar con Nuitka»): con
  Nuitka 4.4 se reprodujeron tres defectos del backend — las opciones
  `--output-dir`/`--output-filename` se emitían separadas por espacio y Nuitka
  exige `=`, se pedía la familia de plugins Qt `styles` que la instalación no
  tiene (aborta con FATAL) y la importación de `nuitka.MainControl` lanzaba
  `AssertionError` fuera del `try`, escapando de `compile_to_exe` en lugar de
  degradar al subproceso documentado. Además la versión se leía de símbolos
  retirados en 4.x y salía «desconocida». Ahora las opciones van con `=`, sólo
  se pide `sensible`, el plugin `pyqt6` se activa sólo si el binding existe, la
  importación está protegida con degradación a `python -m nuitka` y la versión
  sale de `nuitka.Version`. `tests/test_nuitka_backend_arguments.py` (6 casos;
  los cinco que describen el fallo fallan con el código anterior) y
  comprobación real: `--standalone --onefile` produce un binario que ejecuta y
  `--list-compilers` muestra 4.4. Verificación: 1351 pasan, 1 omitido, 64
  subtests; `pyflakes` y `py_compile` limpios. R-4d9e2b61 queda abierto sólo por
  el entorno aislado de Q-019. No se prepara release: quedan bugs de prioridad
  alta y 19 aprobaciones pendientes de implementación.

- Sexagésimo séptimo ciclo (2026-11-26): sin respuestas nuevas en
  `CONFIRM.MD` (sigue sólo **Q-032** pendiente). Se corrige **R-7d4b2c95**, la
  mitad reproducible de R-7c4a1e95: maximizar o restaurar llamaba a
  `apply_theme`, que reinstala la hoja global de la aplicación y re-pule todos
  los widgets (185 ms en `app.setStyleSheet`, 269 ms en `apply_theme`, 274 ms
  por gesto, medidos en offscreen). El gesto ahora refresca sólo el radio de las
  esquinas (~59 ms) mediante `_refresh_window_corners()`, y
  `lib/fluent_theme.apply_global_stylesheet()` no reinstala una hoja idéntica
  (ahorra ~185 ms al cambiar de modo de visualización). `tests/
  test_maximize_without_theme_reapply.py` describe el fallo (con el código
  anterior el gesto hacía 1 llamada a `setStyleSheet`) y el caso de caché vive
  en `tests/test_design_system_phase3.py`. Verificación: 1354 pasan, 1 omitido,
  64 subtests; `pyflakes` y `py_compile` limpios. R-7c4a1e95 sigue abierto por
  el guardado en segundo plano (Q-012). No se prepara release: quedan bugs de
  prioridad alta y 19 aprobaciones pendientes de implementación.

- Sexagésimo octavo ciclo (2026-11-27): sin respuestas nuevas en `CONFIRM.MD`
  (sigue sólo **Q-032** pendiente). Se corrige **R-3e7d1c58** (Q-004/F-001,
  opción A): `compile-only` compilaba un único `.py` y dejaba el fuente en el
  paquete. Ahora `compile_to_bytecode(..., remove_source=True)` retira el `.py`
  compilado, `apply_all()` compila todos los `.py` del árbol salvo el
  `updater.py` obligatorio y `BuildThread.apply_hardening()` conserva el fuente
  cuando el backend es `zipapp`; `compile-only` se ejecuta antes de
  `checksum`/`integrity` para que los manifiestos describan el árbol final.
  `tests/test_hardening.py::CompileOnlySourceRemovalTests` (7 casos) describe el
  fallo; cinco fallan con el código anterior. Verificación: 1361 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios. No se prepara
  release: quedan bugs de prioridad alta y 18 aprobaciones pendientes de
  implementación.

- Sexagésimo noveno ciclo (2026-11-27): sin respuestas nuevas en `CONFIRM.MD`
  (siguen **Q-032** y la nueva **Q-033** pendientes). Se corrige **R-7c4a1e95**
  (la interfaz se congelaba al guardar ajustes): medido en offscreen,
  `PMDataStore.save()` tarda 0,5 ms y un guardado de ruta 1,7 ms, pero un cambio
  de apariencia 120 ms porque `lib/fluent_theme.set_qss()` reinstalaba hojas
  idénticas y Qt re-pulía el árbol (35 ms sólo en `central`). `set_qss()` ahora
  compara con `widget.styleSheet()` y no vuelve a llamar a `setStyleSheet()` si
  el resultado no cambió: el guardado baja a ~5 ms y `central` deja de recibir
  `StyleChange`. `tests/test_settings_save_repolish.py` (4 casos; 3 fallan con el
  código anterior) y se ajustó `test_path_only_save_does_not_repaint_theme` para
  comprobar el efecto en vez del tiempo. Verificación: 1365 pasan, 1 omitido, 64
  subtests; `pyflakes` y `py_compile` limpios. No se prepara release: sigue
  pendiente el entorno aislado de Q-019 y el resto de cambios de engine
  aprobados.

- Septuagésimo ciclo (2026-11-27): sin reportes nuevos en los issues #4, #10,
  #11, #13, #14 y #15 y sin respuestas nuevas en `CONFIRM.MD` (el último commit
  que toca el archivo es del mantenimiento del ciclo 68), así que se aplica una
  aprobación pendiente de riesgo contenido: **Q-017**. El `updater.py` que
  `create_project_from_templates()` copia a cada proyecto nuevo no tenía CLI
  (cualquier argumento se ignoraba) y terminaba en
  `while True: time.sleep(100)`; reproducido con `timeout 6` → código 124.
  Ahora tiene `main()` con `argparse` (`--check`, `--install`/`--target`,
  `--silent`, `--version`), `check_update()` de una pasada, `install_archive()`
  reutilizada por `InstallerWorker` y `verificar()` que termina sin GUI, con
  códigos de salida 0/1. `tests/test_template_updater_cli.py` (5 casos; los 5
  fallan con la plantilla anterior). Verificación: 1370 pasan, 1 omitida, 64
  subtests; `pyflakes` y `py_compile` limpios. La auditoría del ciclo deja dos
  hallazgos nuevos en la cola: **R-7f2b9c41** (la plantilla trata el `.iflapp`
  de la release como ZIP, así que nunca pudo aplicar una actualización; la
  decisión de cómo resolverlo queda en **Q-034**) y **R-3a9c6e28**
  (`verificar()` crea la `QApplication` en un hilo de trabajo). Se añade
  **Q-035** porque Q-018 quedó aprobada sin indicar cuál de sus dos opciones se
  aplica, y una aprobación ambigua no se implementa. No se prepara release.

- Septuagésimo primer ciclo (2026-11-27): sin reportes nuevos en los issues #4,
  #10, #11, #13, #14 y #15, sin pull requests abiertas y sin respuestas nuevas
  en `CONFIRM.MD` (el último commit que toca el archivo es del mantenimiento del
  ciclo 70), así que el ciclo se dedica a bugs. Se corrige **R-3a9c6e28**: el
  `updater.py` de las plantillas creaba la `QApplication` dentro del hilo de
  vigilancia; ahora `main()` crea la aplicación en el hilo principal,
  `UpdateWatcher` consulta GitHub en un hilo y emite `encontrada(datos, url)`
  por señal encolada, y la ventana nace en el hilo de la interfaz
  (`w.thread() is app.thread()` con Qt real en offscreen). Al reproducirlo
  aparece **R-6b4d2f81**, de prioridad alta: las cuatro ventanas de
  `lib/coreUpdater/windows.py` morían al construirse porque usaban
  `Qt.WindowFlags` (no existe en PyQt6), `CustomTitleBar(..., is_main=True)`,
  `title_bar.set_color()` y `LeviathanProgressBar.setValue()`; se pasan las
  banderas directamente, la titlebar se construye sólo con `parent` y `title`,
  se retira `set_color` y se aplica el parche de `setValue` que ya usaba
  `packagemaker.py`. La plantilla recibe los mismos arreglos porque copiaba el
  código. Pruebas nuevas: `tests/test_updater_windows_construct.py` (4 casos) y
  `tests/test_template_updater_gui_thread.py` (2 casos). Verificación: 1376
  pasan, 1 omitida, 64 subtests; `pyflakes` y `py_compile` limpios. Ambas
  quedan en observación. No se prepara release: sigue pendiente el entorno
  aislado de Q-019 y el resto de cambios de engine aprobados, y R-7f2b9c41
  espera la decisión de Q-034.

- Septuagésimo segundo ciclo (2026-11-27): sin reportes nuevos en los issues
  #4, #10, #11, #13, #14 ni #15, sin pull requests abiertas y sin respuestas
  nuevas en `CONFIRM.MD`, así que se aplica la aprobación de prioridad alta
  **Q-019** (R-4d9e2b61: «nada tiene el entorno aislado»). Nuevo
  `lib/blindcubeEngine/build_sandbox.py`: plan del entorno
  (`<proyecto>/build/pm-sandbox/<backend>/venv`), preparación (venv, `pip
  install` de las dependencias del proyecto y del backend, comprobación de que
  el backend se importa dentro), compilación por subproceso y copia del binario
  fuera del entorno. `wrap_backend()` envuelve el backend en
  `FlangCompiler._ensure_compiler()` y en `iflapp_ide.compile_project()`; si el
  entorno falla, se registra el motivo y se compila con el backend embebido.
  Nueva tarjeta Configuración → Red con `network_mode` (sin restricción /
  uso medido, este último con aviso de Python del sistema e indicaciones
  offline), traducida en los 14 catálogos. Verificación real: build aislado con
  PyInstaller (10,9 s) y con Nuitka (60,5 s), con el binario ejecutado en ambos
  casos; la falta de `patchelf` en Linux ahora se explica en el error. Suite:
  1398 pasan, 1 omitida, 64 subtests; `pyflakes` y `py_compile` limpios.
  R-4d9e2b61 queda en observación. No se prepara release: siguen pendientes los
  cambios de engine aprobados y R-7f2b9c41 espera la decisión de Q-034.

- Septuagésimo tercer ciclo (2026-11-27): sin reportes nuevos en los issues #4,
  #10, #11, #13, #14 ni #15, sin pull requests abiertas y sin respuestas nuevas
  en `CONFIRM.MD`, así que se aplica la aprobación de prioridad alta **Q-027**
  (R-7b2c9e51). Nuevo `lib/startup_timing.py`: `minimum_splash_seconds()` parte
  de 5 s y suma hasta 1 s según los puntos de rendimiento (RAM y núcleos,
  redondeo de 0,25 s); `StartupTimeline` mide las fases del arranque hasta la
  decisión de la compuerta; `SplashWaiter` retrasa el cierre del splash con
  `QTimer.singleShot` sin bloquear el bucle de eventos y guarda el tiempo real
  de arranque antes de la espera; `startup_lag_report()` arma la entrada
  `StartupLag` (fases más lentas, mínimo esperado, tiempo real y errores
  restantes) cuando una fase supera 0,5 s o la interfaz no llega dentro del
  mínimo. `packagemaker.py` instrumenta el arranque y encola el reporte sólo
  con el opt-in activo y sin huellas repetidas; `PM_SPLASH_MIN_SECONDS` acorta
  la espera en pruebas. Verificación real: mínimo 5,50 s, `splash.finish()` a
  los 5,61 s y cola vacía en un arranque sano; con el mínimo forzado a 0,05 s
  aparece el reporte con `Interfaz lista en: 0,59 s`. Pruebas:
  `tests/test_startup_timing.py` (30 casos). R-7b2c9e51 queda en observación.
  No se prepara release: siguen pendientes los cambios de engine aprobados y
  R-7f2b9c41 espera la decisión de Q-034.
