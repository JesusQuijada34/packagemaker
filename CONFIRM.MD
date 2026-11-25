# Confirmaciones del propietario — Influent Package Maker

- **Última revisión:** 2026-11-25 (quincuagésimo ciclo: R-7e2d9c14, R-3a8f6b25 y R-9d5c1e73; ningún cambio de engine aplicado)
- **Último commit de `CONFIRM.MD` procesado:** `0667204` (2026-11-25), autor `openhands <openhands@all-hands.dev>` (cuadragésimo noveno ciclo). No aportó respuestas nuevas del propietario; sólo contiene la cabecera y Q-018. La última respuesta del propietario sigue siendo `0ac5457` (2026-11-23), autor `JesusQuijada34 <jesusquijada34.gh@gmail.com>`; el clon es superficial (*graft*) y `git log -- CONFIRM.MD` sólo muestra `0667204`, así que no hay ninguna respuesta nueva que aplicar. Las 11 preguntas siguen sin marcar.
- **Único aprobador:** JesusQuijada34 (GitHub `JesusQuijada34`)
- **Estado:** 11 preguntas pendientes, 7 aprobadas y aplicadas, 0 rechazadas.

Cómo responder: marca exactamente una casilla por bloque (`[x] SÍ` o `[x] NO`)
con un commit normal (sin force push). Solo se aplican las respuestas cuyo
último commit que toca este archivo tenga como autor a `JesusQuijada34`; el
silencio, una casilla ambigua o una aprobación de otro usuario se tratan como
no respondidas. El detalle técnico de cada punto vive en `bugs.md`
(secciones «Mejoras: estado de aprobación» y «Cambios de engine pendientes»).

---

## Pendientes

### Q-004 — `compile-only` y el fuente del paquete (necesita aclaración)
- **Tipo:** mejora
- **Fecha:** 2026-11-23
- **Tu respuesta anterior (commit `0ac5457`):** «decide tu, un zip app no debe de contener archivos python, solamente el ejecutable compilado con pyinstaller y ya» + `SÍ`.
- **Por qué no se ha aplicado:** contiene dos instrucciones incompatibles.
  «Decide tú» delega la decisión, pero «un zip app no debe contener archivos
  Python» no es viable: el backend `zipapp` empaqueta por definición módulos
  `.py`/`.pyc` y sin ellos el artefacto no arranca. El resto de la frase habla
  de PyInstaller, que no es zipapp.
- **Qué se propone (opción A, la recomendada):** `compile-only` retira el `.py`
  del árbol del paquete tras generar el `.pyc` O2, **salvo** en builds `zipapp`,
  donde se conserva el fuente y se documenta el motivo. Si prefieres la
  opción B (solo añadir el `.pyc` y documentar que el `.py` permanece) o una C
  distinta, escríbelo junto a la casilla.
- **Archivos/componentes afectados:** `lib/hardening.py`, `lib/BuildThread.py`,
  `tests/test_hardening.py`.
- **Riesgo y efectos secundarios:** borrado destructivo dentro del paquete; un
  zipapp sin `.py` deja de arrancar. Por eso la opción A excluye ese backend.
- **Respuesta del propietario (JesusQuijada34):** `[ ] SÍ`  `[ ] NO`

### Q-007 — Reorganización de `lib/` y renombrado a GlassCube
- **Tipo:** cambio de engine
- **Fecha:** 2026-11-22
- **Qué se propone:** mover módulos a `blindcubesEngine/`, `flatcubeEngine/` y
  `makeselfEngine/`, integrar la librería de UI en `lib/` y renombrar
  `leviathan-ui` a **GlassCube**.
- **Archivos/componentes afectados:** todo `lib/`, `packagemaker.py`,
  `requirements.txt`, imports y tests.
- **Riesgo y efectos secundarios:** rotura masiva de imports y del empaquetado.
  Riesgo alto.
- **Respuesta del propietario (JesusQuijada34):** `[ ] SÍ`  `[ ] NO`

### Q-008 — Coreografía de splash y ciclo de vida de ventanas (repetida)
- **Tipo:** cambio de engine
- **Fecha:** 2026-11-23 (repetida: la respuesta anterior quedó partida por el conflicto de merge del commit `0ac5457`, con `[ ] SÍ` en un lado y `[x] SÍ` en el otro)
- **Qué se propone:** completar la secuencia splash → login → verificación
  interna → ventana principal, con desvanecido tipo cortina, splash convertido
  en ventana de error, `destroy()` tras los códigos de salida y triple clic en
  la titlebar para pantalla completa con ocultación animada.
- **Evidencia del propietario (2026-11-22, `bugs.txt` commit `bed2e83`):** el
  splash integrado se ejecuta a la vez que la ventana principal en lugar de
  primero, y en Windows aparecen los avisos `QWidgetWindow(...) must be a top
  level window` y `UpdateLayeredWindowIndirect failed for ptDst=...`.
- **Diagnóstico de este ciclo (R-4f8a2c60):** `IntegratedSplash` se crea con
  `parent=main_window` y `WA_TranslucentBackground`, y `WipeWindow` (ventana por
  capas) se aplica sobre un widget hijo; `UpdateLayeredWindowIndirect` exige una
  ventana de nivel superior. El arreglo propuesto es un splash de nivel
  superior mostrado antes de `main_window.show()`, aplicar `WipeWindow` solo a
  ventanas top-level y cerrar con `destroy()`.
- **Archivos/componentes afectados:** `lib/splash_bootloader.py`,
  `lib/splash_window.py`, `lib/window_chrome.py`,
  `lib/window_manager_bridge.py`, `packagemaker.py`.
- **Riesgo y efectos secundarios:** cambia el ciclo de vida de ventanas y el
  manejo de errores de arranque. No se puede verificar visualmente en Windows
  desde este entorno. Riesgo medio-alto.
- **Respuesta del propietario (JesusQuijada34):** `[ ] SÍ`  `[ ] NO`

### Q-011 — Ventana: arrastre con la ventana maximizada y ajuste a media pantalla
- **Tipo:** cambio de engine
- **Fecha:** 2026-11-23
- **Qué se propone:** con la ventana maximizada, arrastrar la titlebar no debe
  moverla: se restaura a tamaño normal y sigue el cursor. Subirla al borde
  superior maximiza y llevarla a un borde lateral la ajusta a media pantalla,
  con transiciones suaves.
- **Archivos/componentes afectados:** `lib/window_manager_bridge.py`,
  `lib/TitleBar.py`, `lib/immersive_titlebar.py`, `packagemaker.py`.
- **Riesgo y efectos secundarios:** hoy el puente llama a `startSystemMove()`
  aunque la ventana esté maximizada (el manejador original de `TitleBar` sí lo
  comprobaba). Cambia el ciclo de vida de la ventana y depende de los gestos
  nativos de Windows, que no se pueden verificar desde este entorno. Riesgo
  medio-alto. Detalle en `bugs.md` (R-6a1f8c23).
- **Respuesta del propietario (JesusQuijada34):** `[ ] SÍ`  `[ ] NO`

### Q-012 — Tareas en segundo plano y barra marquee en las barras de acción
- **Tipo:** mejora
- **Fecha:** 2026-11-23
- **Qué se propone:** que el guardado y las acciones largas trabajen en segundo
  plano sin colgar la interfaz; mientras haya trabajo, oscurecer la ventana y
  animar una barra marquee fina bajo todas las barras de acción (siempre
  presente, inactiva hasta que haya una tarea). Las notificaciones nativas
  sustituyen al diálogo iOS, elegible en «Aspecto → PushBox».
- **Archivos/componentes afectados:** `lib/page_action_bar.py`,
  `lib/settings_panel.py`, `lib/ios_progress_dialog.py`,
  `lib/notificationSystem.py`, `lib/report.py`, `packagemaker.py`.
- **Riesgo y efectos secundarios:** cambia el modelo de avisos y el ciclo de
  guardado; escribir `pm.data` desde varios hilos puede provocar carreras.
  Riesgo alto. (La parte de rendimiento que ya era un bug está corregida:
  R-9e2b4d17.)
- **Respuesta del propietario (JesusQuijada34):** `[ ] SÍ`  `[ ] NO`

### Q-013 — Actualizaciones silenciosas de parches de seguridad
- **Tipo:** cambio de engine
- **Fecha:** 2026-11-23
- **Qué se propone:** si no hay release nueva, descargar en silencio el último
  commit, ejecutar las pruebas de BlindCube, compilar, abrir el programa con la
  salida oculta y, si no hay errores, ofrecer «Reiniciar para aplicar el
  parche»; al reiniciar se reemplazan los archivos y se notifica
  `{versión}-{commit}`. Sin estar compilado, descargar el ZIP del último commit
  y reemplazar archivos.
- **Archivos/componentes afectados:** `updater.py`, `lib/coreUpdater/`,
  `lib/blindcubeEngine/`, `version.res`, `details.xml`.
- **Riesgo y efectos secundarios:** el programa se reemplaza a sí mismo;
  requiere red, permisos de escritura y verificación de integridad, y un fallo
  puede dejar la instalación a medias. Riesgo alto.
- **Respuesta del propietario (JesusQuijada34):** `[ ] SÍ`  `[ ] NO`

### Q-014 — Eventos en el sidebar y temas de temporada
- **Tipo:** mejora
- **Fecha:** 2026-11-23
- **Qué se propone:** mostrar banners de eventos/anuncios en el sidebar y
  cambiar adhesivos, fuentes y detalles de la interfaz y la titlebar según la
  temporada (p. ej. Halloween).
- **Archivos/componentes afectados:** `lib/notificationSystem.py`,
  `lib/app_icons.py`, `lib/design_tokens.py`, `source/qss/*`,
  `packagemaker.py`.
- **Riesgo y efectos secundarios:** introduce contenido remoto (descarga y
  caché de imágenes) y cambios visuales estacionales. Tú mismo lo aparcaste
  hasta tener un release estable sin reportes. Riesgo medio.
- **Respuesta del propietario (JesusQuijada34):** `[ ] SÍ`  `[ ] NO`

### Q-015 — `updater.py --update --silent` con `.iflapp` sigue abriendo una ventana
- **Tipo:** mejora
- **Fecha:** 2026-11-25
- **Qué se propone:** cuando la actualización se lanza con `--silent` y el
  paquete publicado es un `.iflapp`, `_update_from_iflapp` ignora `silent` y
  crea la ventana `IFLAPPInstallerWindow` (o el splash). En un servidor sin
  pantalla (`QT_QPA_PLATFORM=offscreen`, SSH sin X, tarea programada) eso
  significa que la actualización desatendida no instala nada o aborta al
  construir la ventana. Se propone que `silent=True` use
  `install_iflapp(..., silent=True)` (que ya devuelve el resultado real desde
  R-2d5b8f41) y no cree ninguna ventana; sin `--silent` todo sigue igual.
- **Archivos/componentes afectados:** `lib/coreUpdater/installer.py`
  (`_update_from_iflapp`), `updater.py` (salida y código de retorno).
- **Riesgo y efectos secundarios:** cambia el comportamiento visible de
  `--update --silent` para los paquetes `.iflapp` (deja de haber ventana de
  progreso). Quien dependa de ver el instalador debe quitar `--silent`. No
  afecta al modo gráfico ni al motor. Riesgo bajo.
- **Respuesta del propietario (JesusQuijada34):** `[ ] SÍ`  `[ ] NO`

### Q-016 — `packagemaker.py create` sobrescribe un proyecto existente sin avisar
- **Tipo:** cambio de engine (política de creación)
- **Fecha:** 2026-11-25
- **Qué se propone:** el CLI `create` escribe en la carpeta canónica aunque ya
  exista y contenga el trabajo del usuario. El dashboard
  (`pm_dashboard.NewProjectWizard`) y el asistente gráfico rechazan o
  preguntan, pero el CLI headless lo pisa en silencio. Opciones:
  A) rechazar con `[ERROR] ya existe` y código 1 (coherente con el dashboard;
  puede romper scripts que recrean proyectos a propósito);
  B) añadir `--force` para sobrescribir y rechazar sin él (compatible: quien
  necesite recrear lo añade); C) dejarlo como está y sólo documentarlo.
  Recomendación: B.
- **Archivos/componentes afectados:** `lib/cliHandler.py` (rama `create`),
  `packagemaker.py` (`main`, subparser `create`), `tests/test_cli_*`.
- **Riesgo y efectos secundarios:** cambia el código de salida y el mensaje de
  un comando existente; los scripts que dependan de sobrescribir dejarían de
  funcionar sin `--force`. No toca el nombre canónico ni las plantillas.
- **Respuesta del propietario (JesusQuijada34):** `[ ] SÍ`  `[ ] NO`

### Q-017 — El `updater.py` que se genera en los proyectos no tiene CLI
- **Tipo:** cambio de engine (plantilla de proyectos)
- **Fecha:** 2026-11-25
- **Qué se propone:** `src/templates/project/updater.py.template` genera un
  actualizador que sólo arranca la GUI (`updater.py` ejecutado dentro de un
  proyecto recién creado se queda en un bucle de `verificar()` y no termina).
  El `updater.py` de la raíz del repositorio sí tiene CLI
  (`--install`, `--update`, `--silent`, códigos de salida). Se propone que la
  plantilla use la misma interfaz de línea de órdenes (sin `--silent` no
  cambia nada para el usuario final) y que `verificar()` tenga un final claro
  cuando no hay GUI. Afecta a los proyectos que se creen a partir de ahora;
  los ya creados conservan su copia.
- **Archivos/componentes afectados:** `src/templates/project/updater.py.template`,
  `updater.py`, `tests/test_lifecycle_end_to_end.py`.
- **Riesgo y efectos secundarios:** cambia el contenido de las plantillas y,
  por tanto, el de los proyectos nuevos; hay que mantener sincronizadas la
  plantilla y el actualizador del repositorio. Riesgo medio.
- **Respuesta del propietario (JesusQuijada34):** `[ ] SÍ`  `[ ] NO`

### Q-018 — El build del CLI no valida `details.xml` y adivina la versión
- **Tipo:** cambio de engine (comportamiento del build headless)
- **Fecha:** 2026-11-25
- **Qué se propone:** la interfaz bloquea la creación y la compilación con
  `validate_build_fields`, pero `packagemaker.py --buildthis` no valida
  `details.xml`. Auditado en el cuadragésimo noveno ciclo: con
  `<version></version>` el build **termina con éxito**, empaqueta
  `Influent.demo.v1.0-…` (el motor cae a `v1.0` en silencio) y deja dentro del
  paquete un `details.xml` con la versión vacía, con lo que el `updater.py` del
  paquete compara contra una versión vacía. Se propone aplicar la misma puerta
  estricta en el build headless: `[ERROR]` + código 1, o —si se prefiere no
  romper scripts— un aviso `[WARN]` y seguir compilando con la versión
  normalizada. Indica en la respuesta cuál de las dos opciones quieres.
- **Archivos/componentes afectados:** `lib/cliHandler.py` (rama de build),
  `packagemaker.py` (`--buildthis`), `lib/blindcubeEngine/BuildThread.py`,
  `lib/blindcubeEngine/build_validation.py`, `tests/test_build_validation.py`.
- **Riesgo y efectos secundarios:** cambia el resultado de un comando existente;
  los scripts que compilan proyectos con metadatos incompletos dejarían de
  funcionar (opción dura) o seguirían funcionando con un aviso (opción blanda).
  No toca el nombre canónico ni las plantillas. Riesgo medio.
- **Respuesta del propietario (JesusQuijada34):** `[ ] SÍ`  `[ ] NO`

---

## Historial

### Q-001 — Telemetría centralizada de errores (R-d23039c0)
- **Decisión:** aprobada. `[x] SÍ` marcado por JesusQuijada34 en el commit
  `0ac5457` (2026-11-23; autoría verificada con la API de GitHub).
- **Aplicada:** vigésimo quinto ciclo (2026-11-23) — `lib/errorReporter.py`,
  `docs/privacy.md`, `tests/test_error_reporter.py` y el enganche en `main()`.
- **Resultado:** desactivada por defecto; sólo envía con consentimiento
  explícito y endpoint configurado, sin rutas de usuario ni credenciales.

### Q-002 — Acentos en publisher y appname (R-5d8e2a41)
- **Decisión:** aprobada. `[x] SÍ` en el commit `0ac5457` (2026-11-23).
- **Aplicada:** vigésimo quinto ciclo — `ProjectNameFormatter.transliterate()`
  en `lib/makeselfEngine/naming.py`; pruebas en
  `tests/test_project_name_formatter.py` y
  `tests/test_maintenance_cli_regressions.py`.
- **Resultado:** `Jesús` → `Jesus`, `Ñandú Labs` → `Nandu-Labs`; el nombre
  canónico sigue siendo ASCII y los proyectos existentes se leen igual.

### Q-003 — Conservar la capitalización del publisher (R-4c8e1f27)
- **Decisión:** aprobada. `[x] SÍ` en el commit `0ac5457` (2026-11-23).
- **Aplicada:** vigésimo quinto ciclo — `lib/cliHandler.py`, `packagemaker.py`,
  `lib/pm_dashboard.py`, `lib/tui.py`; pruebas en
  `tests/test_maintenance_cli_regressions.py`.
- **Resultado:** `Influent` produce `Influent.demo.…` y
  `<publisher>Influent</publisher>`; la búsqueda sigue sin distinguir
  mayúsculas.

### Q-005 — Aislamiento estricto BlindCube/FlatCube y `.blindkpkg`
- **Decisión:** aprobada. `[x] SÍ` en el commit `0ac5457` (2026-11-23).
- **Aplicada:** ya presente en `main` antes de este ciclo; verificada por la
  suite (`tests/test_engines_and_platform.py`, `tests/test_engine_isolation.py`,
  `tests/test_engine_packages_layout.py`). No se introdujeron cambios de
  comportamiento nuevos en el vigésimo quinto ciclo.

### Q-006 — Pruebas previas y diálogo `.env` en BlindCube
- **Decisión:** aprobada. `[x] SÍ` en el commit `0ac5457` (2026-11-23).
- **Aplicada:** ya presente en `main` (`lib/blindcubeEngine/build_preflight.py`,
  `lib/env_injection_dialog.py`, cableado en `BuildThread` y
  `packagemaker.py`); verificada por `tests/test_build_preflight.py`.

### Q-009 — Rediseño de UI (acento naranja, tarjetas iOS, configuración)
- **Decisión:** aprobada con la nota «ya se propuso anteriormente, pero revisa
  igual». `[x] SÍ` en el commit `0ac5457` (2026-11-23).
- **Aplicada:** revisada y ya presente en `main` — acento `#FF6B00`,
  `lib/settings_cards.py`, `lib/settings_panel.py`, `lib/notificationSystem.py`
  y `lib/font_manager.py`.

### Q-010 — Sidebar: hover y modo contraído (R-5b1d9e47)
- **Decisión:** aprobada con la nota «se hizo pero el parpadeo sigue, los iconos
  estan muy apretados y falta mas ancho, calculo yo que faltan como 10 pix por
  ahi». `[x] SÍ` en el commit `0ac5457` (2026-11-23).
- **Aplicada:** vigésimo quinto ciclo — el hover se pinta en `paintEvent` (sin
  re-polish, fin del parpadeo), el ancho por defecto pasa a 270 px con migración
  única desde 260 y el padding derecho a 14 px. Pruebas en
  `tests/test_hover_and_tokens.py`.
