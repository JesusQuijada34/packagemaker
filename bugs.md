# Cola de bugs y reportes — Influent Package Maker

Última actualización: 2026-11-23 (vigésimo séptimo ciclo)
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
| R-4e7c2b91 | Bug — caché de sesión o idioma corruptos impiden arrancar | Alta | Resuelto |
| R-9a3d6f20 | Bug — configuración local no-objeto rompe el editor y «Abrir con» | Media | Resuelto |
| R-7f3a9c21 | Bug — `--ide-scan` revienta con `settings.json` `build` no-objeto | Alta | Resuelto |
| R-2c8e5d14 | Bug — `--ide-compile` lanza traceback con una carpeta inexistente | Media | Resuelto |
| R-5a1f8e63 | Bug — `--ide-debug` deja escapar las excepciones del guion | Alta | Resuelto |
| R-3b8e5c71 | Bug — `install.json` con campos mal tipados rompe `--uninstall-asksome` | Media | Resuelto |
| R-7c4d2a96 | Bug — parámetros criptográficos mal tipados en `.blindkpkg` | Media | Resuelto |
| R-1d9f6b34 | Bug — parámetros criptográficos mal tipados en `.iflapp` | Media | Resuelto |
| R-4f9b2c81 | Bug — `.asksome` con id `.`/`..` borra fuera de la raíz de instalación | Crítica | Resuelto |
| R-7a3d5e62 | Bug — `--uninstall-asksome`/`--build-removeme` aceptan `app_id` con traversal | Alta | Resuelto |
| R-2b9e4f73 | Bug — `--compile-mexf` lanza traceback si no puede escribir el `.asksome` | Media | Resuelto |
| R-9d4c2f18 | Bug — la versión canónica bloquea la compilación | Alta | Resuelto |
| R-6c2a8f14 | Bug — `settings.json` no-objeto tumba el build | Alta | Resuelto |
| R-8b3d1e57 | Bug — raíz de instalación `.asksome` inválida lanza traceback | Media | Resuelto |
| R-2c7e9b41 | Bug — metadatos no canónicos matan la QThread del build sin aviso | Alta | Resuelto |
| R-5b3d8f27 | Bug — carpeta de salida inaccesible lanza traceback al compilar | Media | Resuelto |
| R-7f2b9c63 | Bug — `.run` con `.iflapp` corrupto lanza traceback | Media | Resuelto |
| R-7c9e2a45 | Bug — `editor_config.json` con forma no válida rompe el arranque | Media | Resuelto |
| R-4e8b2d17 | Bug — `--shell-info` lanza traceback con paquete ilegible o vista previa bloqueada | Media | Resuelto |
| R-6d2f8a41 | Bug — `--compile-mexf` lanza traceback con entradas ilegibles | Media | Resuelto |
| R-4c7a9e13 | Bug — `--inspect-extract` lanza traceback con destino bloqueado | Media | Resuelto |
| R-8e2b5c43 | Bug — `--list-asksome` lanza traceback con raíz ilegible | Media | Resuelto |
| R-3d9f1a76 | Bug — `compile`/TUI lanzan traceback con carpeta base ilegible | Alta | Resuelto |
| R-6c1e8b52 | Bug — `--buildthis`/`--ide-run`/`--shell-info` lanzan traceback con rutas ilegibles | Alta | Resuelto |
| R-7b3e9c28 | Bug — `--install-asksome` lanza traceback con artefacto ilegible | Media | Resuelto |
| R-5a9d2f74 | Bug — abrir carpeta genérica o MoonFix por lotes tumba la GUI con carpeta ilegible | Media | Resuelto |
| R-2f8a4d61 | Bug — `remove_tree` lanza `PermissionError` pese a prometer que no lanza | Baja | Resuelto |
| R-9c1e5b74 | Bug — `pm.data` con números corruptos impide arrancar la GUI | Alta | Resuelto |
| R-2b7d4a90 | Bug — `find_flarm_project` revienta con carpeta o config ilegible | Alta | Resuelto |
| R-5d8f1c36 | Bug — depuración `.mexf` lanza `yaml.YAMLError` en un slot | Media | Resuelto |
| R-8a2f6d51 | Bug — `uninstall_plan` (Windows) deja escapar `OSError` | Baja | Resuelto |
| R-d23039c0 | Mejora — telemetría | Media | Resuelto (Q-001) |
| R-5d8e2a41 | Mejora — nombres con acentos | Media | Resuelto (Q-002) |
| R-4c8e1f27 | Mejora — capitalización del publisher | Baja | Resuelto (Q-003) |
| R-3e7d1c58 | Mejora — `compile-only` deja el fuente en el paquete | Baja | Pendiente de aclaración (Q-004) |
| — | Cambios de engine (`bugs.txt`) | — | Q-005/Q-006/Q-009/Q-010 aplicados; Q-007/Q-008 pendientes |
| R-5b1d9e47 | Bug — parpadeo del hover del sidebar y ancho escaso | Media | Resuelto |
| R-7a3e1d92 | Bug — `CONFIRM.MD` con marcadores de conflicto | Alta | Resuelto |
| R-4f8a2c60 | Bug — splash simultáneo y avisos de ventana en Windows | Alta | Pendiente de aprobación (Q-008) |
| R-3c7a1e90 | Bug — el guardado de Configuración abortaba la app con una ruta imposible | Alta | Resuelto |
| R-9e2b4d17 | Bug — Configuración repintaba el tema dos veces y reiniciaba el motor | Media | Resuelto |
| R-6a1f8c23 | Bug — la titlebar arrastra la ventana maximizada | Media | Pendiente de aprobación (Q-011) |
| R-4d8f2b61 | Bug — botón Guardar en Configuración (no reproducido) | Baja | Cerrado sin cambios de UI |
| R-2e7c4a91 | Bug — editor predeterminado guardado en `lib/config` y JSON no-objeto | Media | Resuelto |
| R-8b4d1f62 | Bug — el removedor generado revienta con `install.json` corrupto | Media | Resuelto |
| R-5c9a3e27 | Bug — metadatos `.mexf` ilegibles abortan el diálogo de instalación | Baja | Resuelto |

Tras el vigésimo cuarto ciclo no quedaban bugs abiertos. El vigésimo quinto
registra R-5b1d9e47 y R-7a3e1d92 (corregidos) y R-4f8a2c60 (prioridad alta),
que depende de la aprobación Q-008 y por eso no se ha modificado. El vigésimo sexto ciclo registra R-3c7a1e90 y R-9e2b4d17
(corregidos y probados), R-6a1f8c23 (pendiente de la aprobación Q-011) y
R-4d8f2b61 (no reproducido en el código actual). Los reportes de auditoría
interna de los ciclos de mantenimiento (R-8f2c41d9, R-c47a9e12 y los cinco del
ciclo CLI, más R-b3f71a6c, R-7c1e4a90, R-91b6d2f4, R-3a7c5e18, R-9f2b64d1,
R-6e04c8ab, R-7d5b91c4, R-3f9a2c71, R-7b1d4e92, R-8a4f1c6d, R-1c93e4b7,
R-4d7b2e91, R-6b1f8d20, R-9e2a5c73, R-2a7f6b41, R-6f2b9d31, R-8c4e1a72,
R-1f4a7c92, R-2b6d8e13, R-3c9e1a57, R-5f8c2d91, R-7e3a9c14, R-4b8d2f61,
R-9c5f1e28, R-4a1e7b93, R-8d2c5f60, R-9b4e7a52, R-2f7c8d31, R-6a1d3c94,
R-8e5b2f17, R-4e7c2b91, R-9a3d6f20, R-7f3a9c21, R-2c8e5d14, R-5a1f8e63,
R-3b8e5c71, R-7c4d2a96, R-1d9f6b34, R-4f9b2c81, R-7a3d5e62, R-2b9e4f73 y
R-9d4c2f18) quedaron corregidos y probados. El 2026-11-22 el propietario
reportó en `bugs.txt` (commit `bed2e83`) el bloqueo por versión canónica; se
corrigió el mismo día como R-9d4c2f18. El vigésimo séptimo ciclo registra
R-2e7c4a91, R-8b4d1f62 y R-5c9a3e27 (corregidos y probados, sin cambios de
comportamiento del engine). No se prepara release: ese reporte reinicia el
requisito de 7 días sin reportes nuevos y el periodo de observación sigue en
curso.

En el ciclo de mantenimiento del 2026-11-22 se añadieron dos hallazgos de
auditoría interna: R-6c2a8f14 (un `config/settings.json` válido pero no-objeto
abortaba la compilación con `AttributeError`) y R-8b3d1e57 (una raíz de
instalación `.asksome` que era un archivo o un destino bloqueado escapaba como
`FileExistsError`/`NotADirectoryError`). Ambos quedaron corregidos en el commit
`b656928`. El mismo día, el decimoctavo ciclo añadió R-2c7e9b41 (los metadatos
no canónicos mataban la QThread del build sin emitir `error`) y R-5b3d8f27 (una
carpeta de salida inaccesible lanzaba traceback en el CLI y en la GUI); ambos
quedaron corregidos y probados en este ciclo. El vigésimo ciclo añadió
R-7c9e2a45: un `data/pmCodeEditor/editor_config.json` con forma no válida (no
objeto, o `default_interpreter` que no es texto) rompía el arranque del panel y
del editor. Queda corregido y probado; no hay bugs abiertos, solo las mejoras y
los cambios de engine pendientes de aprobación en `CONFIRM.MD`.

El vigésimo primer ciclo añadió R-4e8b2d17: `--shell-info` solo traducía
`ValueError`, así que un paquete sin permiso de lectura escapaba como
`PermissionError` con traceback; `--shell-preview` hacía lo propio con un
destino ocupado por un archivo (`FileExistsError`). Queda corregido y probado en
el commit `edb049f`; la cola sigue sin bugs abiertos.

El vigésimo segundo ciclo añadió R-6d2f8a41: `--compile-mexf` dejaba escapar
`PermissionError`/`IsADirectoryError` con traceback cuando `details.xml`, un
`.mexf` o el propio directorio `.mexf/` no se podían leer. Queda corregido y
probado en el commit `f8ea814`; la cola sigue sin bugs abiertos.

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

## Mejoras: estado de aprobación

Las cuatro propuestas de esta sección y los seis cambios de engine están
recogidos como preguntas `Q-001`…`Q-010` en `CONFIRM.MD`, el único canal de
aprobación válido (solo JesusQuijada34). El 2026-11-23 el propietario marcó
`[x] SÍ` en Q-001, Q-002, Q-003, Q-005, Q-006, Q-009 y Q-010 (commit `0ac5457`,
autoría verificada con la API de GitHub). Q-001, Q-002 y Q-003 se aplicaron en
el vigésimo quinto ciclo; Q-005, Q-006, Q-009 y Q-010 ya estaban implementados
y quedan verificados por la suite. Q-004 necesita aclaración y Q-007/Q-008
siguen pendientes.

### R-d23039c0 — Telemetría centralizada de errores

- **Usuario:** JesusQuijada34 (issue #4)
- **Fecha del reporte:** 2026-07-05
- **Estado:** Resuelto (Q-001 aprobada el 2026-11-23, commit `0ac5457`).
- **Solución aplicada:** `lib/errorReporter.py` con envío asíncrono en un hilo
  daemon (límite de 5 s), consentimiento explícito (`telemetry_enabled` +
  `telemetry_endpoint`) y `sanitize()`, que sustituye la carpeta personal por
  `~`, cualquier ruta absoluta por `<path>` y los valores con pinta de
  credencial por `<redacted>`. Desactivado por defecto; `install_excepthook()`
  se encadena al hook original y nunca altera su comportamiento. Documentado en
  `docs/privacy.md`.
- **Pruebas:** `tests/test_error_reporter.py`.
- **Fecha de resolución:** 2026-11-23.

### R-5d8e2a41 — Acentos en publisher e identificador de aplicación

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Estado:** Resuelto (Q-002 aprobada el 2026-11-23, commit `0ac5457`).
- **Solución aplicada:** `ProjectNameFormatter.transliterate()` (NFKD sin
  marcas diacríticas) se aplica en `normalize_publisher()` y
  `normalize_app_id()`. `Jesús` → `Jesus`, `Ñandú Labs` → `Nandu-Labs`. El
  nombre canónico sigue siendo ASCII, así que `_PROJECT_PATTERN` y la lectura
  de proyectos existentes no cambian.
- **Pruebas:** `AccentTransliterationTests` en
  `tests/test_project_name_formatter.py` y
  `AccentedPublisherCreateTests` en `tests/test_maintenance_cli_regressions.py`.
- **Fecha de resolución:** 2026-11-23.

### R-4c8e1f27 — El publisher pierde su capitalización al crear proyectos

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Estado:** Resuelto (Q-003 aprobada el 2026-11-23, commit `0ac5457`).
- **Solución aplicada:** `handle_cli_action('create_project')`,
  `_ejecutarCreacionProyecto()`, `DashboardWindow`, la TUI y las acciones
  `compile`/`repair` pasan el publisher por
  `ProjectNameFormatter.normalize_publisher()` en vez de forzar `.lower()`. La
  búsqueda de proyectos sigue sin distinguir mayúsculas, así que los proyectos
  existentes se localizan igual.
- **Pruebas:** `test_create_copies_icon_from_any_working_directory` (ahora
  espera `Influent.cwd-test.*`) y `AccentTransliterationTests`.
- **Fecha de resolución:** 2026-11-23.
- **Situación histórica:** la ley de nombres exige que el publisher conserve la
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
- **Estado:** Pendiente de aclaración (Q-004). La respuesta del propietario
  («decide tú, un zip app no debe contener archivos python, solamente el
  ejecutable compilado con pyinstaller y ya») mezcla una decisión delegada con
  una condición que contradice el propio backend zipapp, que por definición
  empaqueta código Python. No se aplica hasta desambiguar.
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

- **Estado:** Aprobado (Q-005) e implementado en `main`
  (`lib/engines.py`, `lib/blindcubeEngine/container.py` con `.blindkpkg`,
  `lib/engine_isolation.py`, `lib/flatcubeEngine/pyinstaller_embedded.py`).
  Verificado por `tests/test_engines_and_platform.py`,
  `tests/test_engine_isolation.py` y `tests/test_engine_packages_layout.py`.

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

- **Estado:** Aprobado (Q-006) e implementado en `main`
  (`lib/blindcubeEngine/build_preflight.py`, `lib/env_injection_dialog.py`,
  cableado en `BuildThread` y `packagemaker.py`). Verificado por
  `tests/test_build_preflight.py`.

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

- **Estado:** Pendiente. La respuesta de Q-008 quedó partida por un conflicto
  de merge (`[ ] SÍ` en un lado, `[x] SÍ` en el otro), así que se trata como no
  respondida y se ha vuelto a preguntar. El defecto se registra como
  R-4f8a2c60. No se ha tocado el ciclo de vida de ventanas.

- **Actual:** splash y titlebar existentes, sin la secuencia completa
  splash → login → verificación interna → ventana principal.
- **Solicitado:** fade tipo cortina, splash convertido en ventana de error,
  `destroy()` tras códigos de salida y triple clic en la titlebar para
  pantalla completa con ocultación animada.
- **Reporte del propietario (2026-11-22, `bugs.txt` commit `bed2e83`):** el
  splash integrado se dibuja a la vez que la ventana principal en lugar de
  ejecutarse primero, y en Windows la consola muestra avisos
  `QWidgetWindow(...) must be a top level window` y
  `UpdateLayeredWindowIndirect failed for ptDst=...`. Se registran aquí como
  evidencia del cambio de engine pendiente; no se han modificado el splash ni
  el ciclo de vida de ventanas.
- **Efectos secundarios:** ciclo de vida de ventanas y manejo de errores.
- **Archivos:** `lib/splash_bootloader.py`, `lib/splash_window.py`,
  `lib/window_chrome.py`, `lib/window_manager_bridge.py`, `packagemaker.py`.
- **Riesgo:** medio-alto.

### 5. Rediseño de UI (acento naranja, tarjetas iOS, configuración)

- **Estado:** Aprobado (Q-009) e implementado en `main`: acento naranja
  `#FF6B00`, tarjetas de configuración (`lib/settings_cards.py`,
  `lib/settings_panel.py`), guardado automático, sin editor de código ni
  selector de modo de ventana, notificaciones (`lib/notificationSystem.py`) y
  selección de fuentes (`lib/font_manager.py`).

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

- **Estado:** Aprobado (Q-010) y aplicado. El parpadeo se corrigió pintando el
  resalte en `paintEvent` (sin re-polish) y el ancho por defecto pasó a 270 px;
  el modo contraído ya ocultaba texto, tarjeta de contexto y login. Detalle en
  R-5b1d9e47.

- **Actual:** el hover se anima con `hover_animation.py`; el login permanece en
  la barra lateral contraída.
- **Solicitado:** corregir el parpadeo azul/gris y ocultar el bloque de login al
  contraer, mostrando solo iconos.
- **Efectos secundarios:** estados visuales del sidebar.
- **Archivos:** `lib/SidebarItem.py`, `lib/hover_animation.py`, `packagemaker.py`.
- **Riesgo:** medio.

---

### 7. Ventana: arrastre, maximizado y ajuste a media pantalla

- **Estado:** Pendiente (Q-011). Registrado como R-6a1f8c23.
- **Actual:** `window_manager_bridge` inicia `startSystemMove()` siempre que se
  pulsa la titlebar, incluso maximizada, así que la ventana se desplaza.
- **Solicitado:** con la ventana maximizada, arrastrar la titlebar la restaura
  a tamaño normal; subirla al borde superior maximiza; llevarla a un borde
  lateral la ajusta a media pantalla, con transiciones suaves.
- **Efectos secundarios:** gestos nativos de Windows (snap), maximizado sin
  marco y bordes de redimensionado; fácil de romper sin probarlo en Windows.
- **Archivos:** `lib/window_manager_bridge.py`, `lib/TitleBar.py`,
  `lib/immersive_titlebar.py`, `packagemaker.py`.
- **Riesgo:** medio-alto.

### 8. Tareas en segundo plano y barra marquee en las barras de acción

- **Estado:** Pendiente (Q-012).
- **Actual:** el guardado automático y la descarga de fuentes corren en el hilo
  de la interfaz; el diálogo iOS con barra de progreso sigue siendo el aviso
  principal de acciones largas.
- **Solicitado:** ejecutar en segundo plano, oscurecer la ventana mientras se
  aplica un cambio y mostrar una barra marquee fina bajo todas las barras de
  acción (siempre presente, inactiva hasta que hay trabajo). Las notificaciones
  nativas sustituyen al diálogo iOS, elegible en «Aspecto → PushBox».
- **Efectos secundarios:** cambia el modelo de avisos y el ciclo de guardado;
  riesgo de carreras al escribir `pm.data` desde varios hilos.
- **Archivos:** `lib/page_action_bar.py`, `lib/settings_panel.py`,
  `lib/ios_progress_dialog.py`, `lib/notificationSystem.py`,
  `lib/report.py`, `packagemaker.py`.
- **Riesgo:** alto (concurrencia y estados visuales nuevos).

### 9. Actualizaciones silenciosas de parches de seguridad (`updater.py`)

- **Estado:** Pendiente (Q-013).
- **Actual:** `updater.py` consulta releases publicadas y no aplica parches.
- **Solicitado:** si no hay release nueva, descargar en silencio el último
  commit, ejecutar las pruebas de BlindCube, compilar, abrir el programa con la
  salida oculta, y si no hay errores ofrecer «Reiniciar para aplicar el
  parche»; al reiniciar, reemplazar archivos y notificar
  `{versión}-{commit}`. Sin estar compilado, descargar el ZIP del último commit
  y reemplazar archivos.
- **Efectos secundarios:** el programa se reemplaza a sí mismo; requiere
  verificación de integridad, red y permisos de escritura. Riesgo de dejar la
  instalación a medias.
- **Archivos:** `updater.py`, `lib/coreUpdater/`, `lib/blindcubeEngine/`,
  `version.res`, `details.xml`.
- **Riesgo:** alto.

### 10. Eventos en el sidebar y temas de temporada

- **Estado:** Pendiente (Q-014). Aparcado por el propietario hasta que haya un
  release estable sin reportes.
- **Actual:** el sidebar no muestra banners de eventos y la interfaz no cambia
  con la temporada.
- **Solicitado:** banners de eventos/anuncios en el sidebar y adhesivos,
  fuentes y detalles de temporada (p. ej. Halloween) en la interfaz y la
  titlebar.
- **Efectos secundarios:** nuevo contenido remoto (descarga y caché de
  imágenes), cambios visuales estacionales y consumo de red.
- **Archivos:** `lib/notificationSystem.py`, `lib/app_icons.py`,
  `lib/design_tokens.py`, `source/qss/*`, `packagemaker.py`.
- **Riesgo:** medio.

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

## R-4f8a2c60 — Splash simultáneo y avisos de ventana en Windows

- **Usuario:** JesusQuijada34 (`bugs.txt`, commit `bed2e83`; evidencia en Q-008)
- **Fecha del reporte:** 2026-11-22
- **Prioridad:** Alta
- **Descripción:** al abrir la aplicación aparecen varias ventanas vacías que
  se abren y cierran, el splash se dibuja a la vez que la ventana principal en
  lugar de primero, y en Windows la consola muestra
  `QWidgetWindow(...) must be a top level window` y
  `UpdateLayeredWindowIndirect failed for ptDst=...`.
- **Causa probable:** `IntegratedSplash` se crea con `parent=main_window` y
  `WA_TranslucentBackground`, y el efecto `WipeWindow` (ventana por capas) se
  aplica sobre un widget hijo. `UpdateLayeredWindowIndirect` y el gestor de
  ventanas de Qt exigen una ventana de nivel superior.
- **Estado:** Pendiente. Depende del cambio de engine Q-008, cuya respuesta
  quedó ambigua; no se ha modificado el ciclo de vida de ventanas.
- **Propuesta:** splash de nivel superior (sin padre) mostrado antes de
  `main_window.show()`, aplicar `WipeWindow` solo a ventanas top-level y
  cerrar con `destroy()`.
- **Riesgo:** alto sin verificación visual en Windows.

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

## R-6a1f8c23 — Arrastrar la titlebar con la ventana maximizada mueve la ventana

- **Usuario:** JesusQuijada34 (`bugs.txt`: «porque al jalar la barra de titulo a
  un lado estando maximizada, se mueve? en vez de quedar quieta y bloqueada»)
- **Fecha del reporte:** 2026-11-23
- **Prioridad:** Media
- **Descripción:** con la ventana maximizada, arrastrar la barra de título
  desplaza la ventana en lugar de mantenerla fija; el usuario pide además que
  arrastrarla la devuelva a tamaño normal, que subirla al borde superior
  maximice y que llevarla a un borde lateral la ajuste a media pantalla.
- **Pasos para reproducir:** maximizar la ventana y arrastrar la titlebar hacia
  un lado.
- **Causa raíz:** `lib/window_manager_bridge._wire_titlebar()` sustituye
  `mousePressEvent` de la titlebar y llama a `start_system_move()` sin
  comprobar el estado de la ventana. El manejador original de
  `lib/TitleBar.py` sí lo comprobaba (`not is_maximized()`), así que el puente
  anuló esa guarda.
- **Estado:** Pendiente. Cambia el ciclo de vida y el comportamiento de la
  ventana (restaurar al arrastrar, maximizar al soltar arriba, ajuste a media
  pantalla), así que se acumula como pregunta **Q-011** en `CONFIRM.MD` y no se
  ha modificado.
- **Propuesta:** ignorar `startSystemMove()` mientras la ventana esté
  maximizada y restaurarla antes de mover; añadir las zonas de ajuste
  (arriba = maximizar, laterales = media pantalla) con transiciones suaves.
- **Archivos afectados:** `lib/window_manager_bridge.py`, `lib/TitleBar.py`,
  `lib/immersive_titlebar.py`, `packagemaker.py`.
- **Riesgo:** medio-alto (snap y maximizado nativos; difícil de verificar sin
  Windows).

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

## Periodo de observación y release

- Bugs abiertos: 2 (R-4f8a2c60 pendiente de Q-008 y R-6a1f8c23 pendiente de
  Q-011). R-4d8f2b61 se cerró como no reproducido.
- Vigésimo séptimo ciclo (2026-11-23): R-2e7c4a91, R-8b4d1f62 y R-5c9a3e27
  corregidos y probados; no se prepara release.
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
- Release: **no preparado**. No se generaron `flat cube` ni `blind cube` en este
  ciclo. El periodo de observación de 3 días y el requisito de 7 días sin
  reportes nuevos siguen en curso.
