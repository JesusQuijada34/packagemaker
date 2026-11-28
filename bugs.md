# Cola de bugs y reportes — Influent Package Maker

Última actualización: 2026-11-28 (ciclo 82: llegan once reportes nuevos del
propietario —issues #17 a #26— y uno externo (#27). Se corrige **R-5e9c1d87**
(issue #24: perfil duplicado y recuento de repositorios perdido) y el resto
entra en la cola. El tema claro (issue #18) queda diagnosticado y pendiente de
la decisión de alcance Q-036; el método de compilación de la 3.2.6 (issue #26)
se registra como cambio de engine en **Q-037**).
Fuente: [issue #4 — Backlog de Reportes Técnicos](https://github.com/JesusQuijada34/packagemaker/issues/4),
[issue #11](https://github.com/JesusQuijada34/packagemaker/issues/11),
[issue #13](https://github.com/JesusQuijada34/packagemaker/issues/13),
[issue #14](https://github.com/JesusQuijada34/packagemaker/issues/14),
[issue #15](https://github.com/JesusQuijada34/packagemaker/issues/15) y
[issues #17 a #27](https://github.com/JesusQuijada34/packagemaker/issues?q=is%3Aissue+is%3Aopen)
Rama de trabajo: `main`

Este archivo es la **cola activa**: sólo contiene lo pendiente. Los bugs ya
resueltos se retiran en el mismo ciclo y se archivan en
`docs/bugs_resueltos.md` (índice) y en `CHANGELOG.md`; el detalle y la
conversación quedan en el issue. Las fichas de las aprobaciones del propietario
viven en `CONFIRM.MD`, que es la única autoridad para responderlas.

## Resumen

| ID | Tipo | Prioridad | Estado |
|---|---|---|---|
| R-7e3a1b95 | Bug — splash, titlebar, pantalla completa y AIDE (issue #17) | Alta | Pendiente |
| R-2f9b7c14 | Bug — el tema claro no se aplica al contenido (issue #18) | Alta | Diagnosticado; alcance en Q-036 |
| R-6d1e4a83 | Bug — arranque con tirones: 10,3 s en la fase «ventana» (issue #19) | Alta | Pendiente |
| R-9b5d3e72 | Bug — el borde del sidebar no se ve como en Reportes (issue #21) | Baja | Pendiente |
| R-7f2b9c41 | Bug — el updater de los proyectos no puede instalar un `.iflapp` | Alta | Pendiente de decisión (Q-034) |
| R-1a7c6d94 | Mejora — faltan temas de ayuda y explicar cada artefacto (issue #22) | Media | Pendiente |
| R-8f2e5b13 | Mejora — AIDE como chatbot de la base de código (issue #23) | Media | Pendiente |
| R-3d6a8f25 | Mejora — instancia única en código y compilado (issue #25) | Media | Pendiente |
| R-4c8a2f61 | Mejora — pestañas con color invertido por tema (issue #20) | Media | Depende de Q-036 |
| R-5a7d2f16 | Mejora — fondo translúcido y colores de pestañas por tema | Media | Aplicada en parte (sidebar, R-8f4b2d61); falta superficie/texto de pestañas (Q-036) |
| R-3c8e4b72 | Mejora — faltan ajustes en Configuración | Baja | Pendiente (mejora sin pregunta) |
| R-0b8d2c47 | Documentación — README con capturas e instalación (issue #27) | Baja | Reporte externo; espera revisión del propietario |
| R-7c4b9e36 | Cambio de engine — método de compilación y rastreo de la 3.2.6 (issue #26) | Alta | Pendiente de aprobación (Q-037) |
| R-9a4e2c83 | Cambio de engine — GitHub y CloudCube (issue #11) | Media | Aprobado Q-023; pendiente de implementación |
| R-5f1b8d24 | Cambio de engine — updater como extensión (issue #11) | Media | Aprobado Q-024; pendiente de implementación |
| R-8e6a3c15 | Cambio de engine — Leviathan y action bar como control (issue #11) | Media | Aprobado Q-025; pendiente de implementación |
| R-9c3f5a28 | Cambio de engine — librería de paneles y pestañas (issue #14) | Media | Aprobado Q-028; pendiente de implementación |
| R-3b7e2d94 | Cambio de engine — addons en `lib/addons/` y DLL (issue #14) | Media | Aprobado Q-031; pendiente de implementación |

**18 entradas en la cola**: 6 bugs (R-5e9c1d87 se corrige en este ciclo y pasa
a observación), 6 mejoras, 1 tarea de documentación externa y 6 cambios de
engine (5 aprobados y pendientes, más R-7c4b9e36 que espera Q-037). Q-013 sigue
«aplicada en parte»: la consulta y el aviso de parches ya están en `main`; la
descarga y la aplicación siguen pendientes. Los once issues nuevos no cambian
el reparto de Q-013/Q-026: el tema claro y las pestañas dependen del alcance que
fije el propietario en Q-036. Siguen archivados Q-029 (AIDE en Configuración),
Q-030 (perfil como extensión), Q-022 (addons), Q-021 (ayuda), Q-027 (splash
mínimo), Q-019 (entorno aislado) y Q-032 (splash dentro de la ventana).

## Bugs pendientes

### R-7f2b9c41 — El updater de los proyectos no puede instalar un `.iflapp`

- **Usuario:** auditoría interna de mantenimiento (ciclo 70, al implementar
  Q-017); no hay reporte externo.
- **Fecha del reporte:** 2026-11-27
- **Prioridad:** Alta.
- **Descripción:** el `updater.py` que se copia a cada proyecto descarga el
  artefacto de la release y lo trata como un ZIP. Las releases de PackageMaker
  son contenedores `.iflapp` v2 (cabecera `IFLAPP2\0`), así que la extracción
  falla siempre y el updater nunca ha podido aplicar una actualización.
- **Pasos para reproducirlo:** crear un proyecto con las plantillas, generar un
  paquete con `pack_iflapp()` y ejecutar
  `python updater.py --install <paquete>.iflapp`; responde
  `ERROR: el paquete no es un .zip …` y código 1.
- **Evidencia:** el contenedor empieza por `IFLAPP2\x00\x00` y
  `zipfile.ZipFile()` lanza `BadZipFile: File is not a zip file`; el mismo
  fallo tenía el antiguo `InstallerWorker` al descomprimir la descarga.
- **Causa raíz:** la plantilla no incluye lector del contenedor `.iflapp` y
  `lib/blindcubeEngine/iflapp_format.py` no se copia a los proyectos, así que
  no puede leer la carga útil (TAR + LZMA, opcionalmente cifrada).
- **Estado:** pendiente de decisión del propietario (**Q-034** en
  `CONFIRM.MD`): lector embebido en la plantilla, delegar en el updater de
  PackageMaker o dejar `.zip` como único formato documentado.
- **Solución aplicada:** ninguna todavía. El CLI de Q-017 ya informa del
  formato no soportado en vez de fallar con un traceback.
- **Commit / fecha de resolución:** —

### R-7e3a1b95 — Splash, titlebar y pantalla completa (issue #17)

- **Usuario:** JesusQuijada34 (issue #17, reporte desde la aplicación).
- **Fecha del reporte:** 2026-11-28
- **Prioridad:** Alta.
- **Descripción:** el splash no se muestra primero (la ventana se oculta y
  luego salta el splash), los gestos de la titlebar se adelantan al tercer
  clic, al entrar en pantalla completa la titlebar no sale desde arriba, no
  aparece el icono de salir y queda un borde inferior que deja la barra de
  tareas activa; además AIDE debe parecer un chatbot y no una pestaña con fondo
  detrás del texto.
- **Pasos para reproducirlo:** arrancar la aplicación en Windows y observar la
  secuencia; hacer tres gestos sobre la titlebar y pasar el cursor por el borde
  superior en pantalla completa; abrir AIDE.
- **Estado:** pendiente. Son varios síntomas de UI; se separará el arreglo del
  splash/titlebar del rediseño de AIDE.
- **Solución aplicada:** ninguna todavía.
- **Commit / fecha de resolución:** —

### R-2f9b7c14 — El tema claro no se aplica al contenido (issue #18)

- **Usuario:** JesusQuijada34 (issue #18).
- **Fecha del reporte:** 2026-11-28
- **Prioridad:** Alta.
- **Descripción:** en Windows en modo claro todo se ve oscuro y el sidebar no
  muestra la capa blanca translúcida 0,3–0,5.
- **Evidencia recogida (ciclo 82, offscreen):** `system_theme_mode()` devuelve
  `light`, la hoja del `central` sí lleva `#F5F7FB` y el sidebar sí resuelve
  `SIDEBAR_BG_LIGHT` (alfa 177), pero el `QStackedWidget` del contenido conserva
  `background:rgba(28,28,30,0.82)` porque `packagemaker_008` usa `CONTENT_BG`
  literal y `apply_theme()` nunca lo re-resuelve. Medido: píxel del stack
  `#1c1c1e` en tema claro. Además ~40 estilos de `lib/fluent_theme.py` llevan
  `color:white`, así que pasar la superficie a clara sin resolver el texto deja
  los títulos invisibles (visto en captura).
- **Causa raíz:** dos capas de estilo sin tema: la superficie del stack y los
  estilos de página en línea.
- **Estado:** diagnosticado; el alcance (qué superficies y textos se invierten)
  se decide en **Q-036**. No se toca hasta la respuesta del propietario.
- **Solución aplicada:** ninguna todavía.
- **Commit / fecha de resolución:** —

### R-6d1e4a83 — Arranque con tirones: 10,3 s en la fase «ventana» (issue #19)

- **Usuario:** JesusQuijada34 (issue #19, reporte automático `StartupLag`).
- **Fecha del reporte:** 2026-11-28
- **Prioridad:** Alta.
- **Descripción:** el arranque tarda 16,21 s en dejar lista la interfaz; la
  fase «ventana» consume 10,32 s, seguida de `idioma_ui` (2,93 s) y `fuente`
  (1,22 s). Equipo de 2 núcleos con Windows 10.
- **Reproducción:** `PM_SPLASH_MIN_SECONDS=0.05` no reproduce el tiempo real;
  hace falta medir la construcción de la ventana con `StartupTimeline` en el
  equipo del reporte.
- **Estado:** pendiente. No se puede atribuir la causa sin el desglose interno
  de la fase «ventana» en Windows (los tiempos offscreen no son comparables).
- **Solución aplicada:** ninguna todavía.
- **Commit / fecha de resolución:** —

### R-9b5d3e72 — El borde del sidebar no se ve como en Reportes (issue #21)

- **Usuario:** JesusQuijada34 (issue #21).
- **Fecha del reporte:** 2026-11-28
- **Prioridad:** Baja.
- **Descripción:** el separador del sidebar no se distingue como el del panel
  de Reportes; pide gris en modo claro y blanco en modo oscuro.
- **Estado:** pendiente. La regla actual usa `#D1D1D6` (claro) y `#333333`
  (oscuro); falta confirmar si el reporte habla del borde, del fondo o de la
  barra de desplazamiento antes de cambiarlo.
- **Solución aplicada:** ninguna todavía.
- **Commit / fecha de resolución:** —

## Mejoras pendientes

### R-5a7d2f16 — Fondo blanco/negro translúcido sobre el blur

- **Usuario:** JesusQuijada34 (`bugs.txt` y issue #11)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Media.
- **Descripción:** fondo blanco o negro según el modo del sistema con
  transparencia (0,3–0,5) combinado con el blur; sidebar blanco translúcido y
  pestañas gris claro con texto gris en modo claro, invertido en oscuro.
- **Estado:** **Aplicada en parte** (Q-026). El sidebar ya pinta su fondo
  translúcido por tema con el arreglo R-8f4b2d61. La inversión de la superficie
  de las pestañas queda pendiente de Q-036: los ~40 estilos de
  `lib/fluent_theme.py` llevan `color:white` y una superficie clara dejaría el
  texto invisible (comprobado en captura offscreen).
- **Archivos:** `lib/design_tokens.py`, `source/qss/*`, `lib/fluent_theme.py`,
  `packagemaker.py`, `tests/`.
- **Solución aplicada:** `SIDEBAR_BG = rgba(28,28,30,0.45)`,
  `SIDEBAR_BG_LIGHT = rgba(255,255,255,0.45)`, sidebar con
  `WA_StyledBackground` (sin `WA_TranslucentBackground`) y QSS resuelto por
  tema. Commit `804c50c` (ciclo 75).
- **Commit / fecha de resolución:** sidebar `804c50c` (2026-11-27); pestañas
  pendientes de Q-036.

### R-3c8e4b72 — Faltan ajustes en Configuración

- **Usuario:** JesusQuijada34 (`bugs.txt`, commit `bba72d6`)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Baja.
- **Descripción:** agregar más ajustes para que Configuración no quede vacía,
  pero sólo cuando hayan bajado los bugs.
- **Estado:** Pendiente. El propio propietario la condiciona a que bajen los
  bugs; no entra en un ciclo con bugs de prioridad alta abiertos.

### R-1a7c6d94 — Faltan temas de ayuda y explicar cada artefacto (issue #22)

- **Usuario:** JesusQuijada34 (issue #22).
- **Fecha del reporte:** 2026-11-28
- **Prioridad:** Media.
- **Descripción:** la ayuda está resumida y no explica qué significa cada
  artefacto ni cada botón; hay usuarios que no pueden adivinarlo.
- **Estado:** pendiente. Es contenido, no motor: exige temas nuevos en
  `lib/help_page.py` y claves en los 14 catálogos de `lang/`.
- **Solución aplicada:** ninguna todavía.
- **Commit / fecha de resolución:** —

### R-8f2e5b13 — AIDE como chatbot de la base de código (issue #23)

- **Usuario:** JesusQuijada34 (issue #23).
- **Fecha del reporte:** 2026-11-28
- **Prioridad:** Media.
- **Descripción:** AIDE debe ser un chatbot tipo ChatGPT para hablar con la IA
  sobre la base del código, no una pestaña con fondo detrás del texto.
- **Estado:** pendiente. El backend, la clave y el contexto ya se configuran
  (Q-029); falta la interfaz de conversación. Se separa del bug visual de #17.
- **Solución aplicada:** ninguna todavía.
- **Commit / fecha de resolución:** —

### R-3d6a8f25 — Instancia única en código y compilado (issue #25)

- **Usuario:** JesusQuijada34 (issue #25).
- **Fecha del reporte:** 2026-11-28
- **Prioridad:** Media.
- **Descripción:** se pueden abrir varias instancias del programa; pide
  limitarlo a una sola tanto en código fuente como compilado.
- **Estado:** pendiente. Requiere un cerrojo (socket o fichero con PID) y una
  decisión sobre qué hacer al segundo arranque (enfocar o salir).
- **Solución aplicada:** ninguna todavía.
- **Commit / fecha de resolución:** —

### R-4c8a2f61 — Pestañas con color invertido por tema (issue #20)

- **Usuario:** JesusQuijada34 (issue #20).
- **Fecha del reporte:** 2026-11-28
- **Prioridad:** Media.
- **Descripción:** si el sidebar es blanco en modo claro, las pestañas deben
  ser blancas con texto oscuro; en oscuro, al contrario.
- **Estado:** depende de **Q-036**, que fija el alcance de la inversión de
  superficie y texto (R-5a7d2f16).
- **Solución aplicada:** ninguna todavía.
- **Commit / fecha de resolución:** —

### R-0b8d2c47 — README con capturas e instalación (issue #27)

- **Usuario:** JoseSuppini34 (issue #27), cuenta externa.
- **Fecha del reporte:** 2026-11-28
- **Prioridad:** Baja.
- **Descripción:** pregunta si el README está completo para leer con capturas
  de la aplicación y pide pasos de instalación.
- **Estado:** pendiente de revisión del propietario (el reporte no es suyo). Se
  responde al issue con la información disponible; no se modifica el README sin
  su visto bueno.
- **Solución aplicada:** ninguna todavía.
- **Commit / fecha de resolución:** —

## Cambios de engine pendientes

Cambian comportamiento fundamental, UI o empaquetado y **sólo se implementan
con la marca `[x] SÍ` del propietario en `CONFIRM.MD`**. La ficha de cada uno
(comportamiento actual, solicitado, efectos secundarios y archivos) vive en su
bloque `Q-xxx` de `CONFIRM.MD`; aquí queda el índice.

| Punto | ID / ficha | Tema | Estado | Riesgo |
|---|---|---|---|---|
| 3 | Q-007 / F-002 | Reorganización de `lib/` y renombrado a GlassCube | Aprobado; pendiente | alto |
| 4 | Q-008 / F-003 (R-4f8a2c60) | Coreografía de splash y ventanas | Aprobado en parte; pendiente | medio-alto |
| 8 | Q-012 / F-005 | Tareas en segundo plano y barra marquee | Aprobado; pendiente (el congelado de R-7c4a1e95 ya está corregido) | alto |
| 9 | Q-013 / F-006 | Actualizaciones silenciosas de parches | **Aplicada en parte** (etapa 1: vigilancia y aviso, ciclo 79); falta descargar y aplicar el parche | alto |
| 10 | Q-014 | Eventos del sidebar y temas de temporada | Aprobado, pero **aplazado por el propietario** hasta tener un release estable sin reportes | medio |
| 13 | Q-018 | El build del CLI no valida `details.xml` | Aprobado; pendiente de elegir opción (Q-035) | medio |
| 14 | Q-019 (R-4d9e2b61) | Entorno aislado de compilación | **Aplicado** (ciclo 72); R-4d9e2b61 en observación | alto |
| 15 | Q-020 | Traducción completa al cambiar de idioma | Aprobado; aplicado en parte | medio-alto |
| 16 | Q-023 (R-9a4e2c83) | Conectar proyectos a GitHub y extensión CloudCube | Aprobado; pendiente | alto |
| 17 | Q-024 (R-5f1b8d24) | El updater como extensión con notificaciones | Aprobado; pendiente | alto |
| 18 | Q-025 (R-8e6a3c15) | Completar Leviathan y el action bar como control | Aprobado; pendiente | alto |
| 19 | Q-027 (R-7b2c9e51) | Duración mínima del splash y reporte de tirones | **Aplicado** (ciclo 73); R-7b2c9e51 en observación | medio |
| 20 | Q-028 (R-9c3f5a28) | Librería de paneles y pestañas verticales | Aprobado; pendiente | alto |
| 23 | Q-031 (R-3b7e2d94) | Addons empaquetados en `lib/addons/` y addons DLL | Aprobado; pendiente | alto |
| 24 | Q-037 (R-7c4b9e36) | Portar el método de compilación y rastreo de la 3.2.6 | **Pendiente de aprobación** (issue #26) | alto |

Ya implementados y verificados: splash dentro de la ventana principal, estilo
UWP (Q-032, ciclo 80), perfil de GitHub como extensión y panel de
cuenta (Q-030, ciclo 78), aislamiento BlindCube/FlatCube y `.blindkpkg`
(Q-005), pruebas previas y diálogo `.env` (Q-006), rediseño de UI (Q-009),
sidebar con hover y modo contraído (Q-010), la ventana con arrastre, snap y
límite de tres gestos (Q-011/F-004, R-6a1f8c23 y R-2f8b6a31), el CLI del
`updater.py` de las plantillas (Q-017, ciclo 70), el entorno de compilación
aislado por proyecto con la tarjeta Red (Q-019, ciclo 72), la duración mínima
del splash con el reporte de tirones (Q-027, ciclo 73) y la página de ayuda
global con buscador (Q-021, ciclo 74). Q-029 (AIDE como chatbot) ya estaba
cubierta por el asistente del ciclo 56 —dos proveedores, clave propia y
contexto saneado—; sólo queda trasladar sus campos a Configuración.

## En observación

Las correcciones aplicadas y probadas se archivan en `CHANGELOG.md` (detalle) y
en `docs/bugs_resueltos.md` (índice); su conversación queda en el issue. Cuando
reaparezca un caso archivado, se vuelve a abrir aquí con su ID y la referencia
al ciclo anterior.

| ID | Título | Prioridad | Corregido | Prueba de regresión |
|---|---|---|---|---|
| R-5e9c1d87 | Perfil duplicado (avatar y «Salir» dos veces) y recuento de repositorios perdido (issue #24) | Alta | ciclo 82, 2026-11-28 | `tests/test_profile_page.py::test_profile_page_draws_a_single_identity_and_logout`, `::test_profile_extras_survive_the_store_round_trip` |
| R-8b5c1d47 | El subtítulo de la barra mostraba el Markdown de los catálogos | Baja | ciclo 81, 2026-11-28 | `tests/test_activity_bar_and_subtitle.py::test_subtitle_renders_the_catalog_markdown` |
| R-4a9d1c63 | La vigilancia de parches sólo consultaba al arrancar (Q-013, etapa 1) | Media | ciclo 80, 2026-11-28 | `tests/test_patch_watch_ui.py::test_watch_rechecks_on_a_timer_without_user_action` |
| R-8d3f6a21 | El backend Nuitka no podía compilar (opciones inválidas y API embebida sin proteger) | Alta | ciclo 66, 2026-11-26 | `tests/test_nuitka_backend_arguments.py` |
| R-7d4b2c95 | Maximizar o restaurar congelaba la interfaz (~270 ms por gesto) | Alta | ciclo 67, 2026-11-26 | `tests/test_maximize_without_theme_reapply.py` |
| R-3e7d1c58 | `compile-only` no retiraba el fuente del paquete | Media | ciclo 68, 2026-11-27 | `tests/test_hardening.py::CompileOnlySourceRemovalTests` |
| R-7c4a1e95 | La interfaz se congelaba al guardar ajustes (~120 ms por re-pulido redundante) | Alta | ciclo 69, 2026-11-27 | `tests/test_settings_save_repolish.py` |
| R-6b4d2f81 | Las cuatro ventanas del updater morían al construirse (`Qt.WindowFlags`, `is_main`, `set_color`, `setValue`) | Alta | ciclo 71, 2026-11-27 | `tests/test_updater_windows_construct.py` |
| R-3a9c6e28 | El updater de plantilla creaba la `QApplication` en el hilo de vigilancia | Media | ciclo 71, 2026-11-27 | `tests/test_template_updater_gui_thread.py` |
| R-4d9e2b61 | El build no usaba un entorno aislado por proyecto (Q-019) | Alta | ciclo 72, 2026-11-27 | `tests/test_build_sandbox.py`, `tests/test_settings_navigation_bar.py` |
| R-7b2c9e51 | El splash se retiraba antes de que la interfaz estuviera dibujada y los tirones del arranque no se reportaban (Q-027) | Alta | ciclo 73, 2026-11-27 | `tests/test_startup_timing.py` |
| R-5c9a3e17 | El splash era una ventana propia a pantalla completa en vez de vivir dentro de la ventana (Q-032) | Media | ciclo 80, 2026-11-28 | `tests/test_splash_top_level.py` |

## Periodo de observación y release

- **Cola:** 18 entradas (ver Resumen). Llegaron once reportes nuevos (issues
  #17–#27) y el ciclo atiende el más contenido: R-5e9c1d87 (issue #24), que pasa
  a observación. R-7f2b9c41 sigue esperando Q-034; el tema claro (R-2f9b7c14,
  issue #18) queda diagnosticado y espera el alcance de Q-036; R-7c4b9e36
  (issue #26) espera Q-037. R-4d9e2b61 (Q-019) y R-7b2c9e51 (Q-027) siguen en
  observación tras verificarse con arranques y compilaciones reales.
- **Release:** no se prepara. Hay cambios de engine de prioridad alta pendientes
  de implementación, bugs de prioridad alta recién reportados y no ha pasado el
  periodo sin reportes nuevos.
- **Nuevo en el ciclo 82:** **R-5e9c1d87** (issue #24) queda en observación. El
  perfil pintaba la tarjeta compacta del sidebar y su propia identidad a la vez
  (dos avatares y dos botones «Salir»), y `save_profile()` no guardaba `extras`,
  así que tras reiniciar el perfil mostraba 0 repositorios y sin biografía. Sólo
  cambia la página Perfil y el almacén de identidad; no toca compilación,
  empaquetado ni blindaje.
- **Nuevo en el ciclo 79:** la vigilancia de parches (Q-013, etapa 1) no cambia
  compilación, empaquetado ni blindaje: sólo hace un `GET` de lectura y avisa.
  No entra en observación porque no sustituye nada; su verificación es la
  consulta real (`up_to_date` con el commit `52e9c89`) y las 30 pruebas nuevas.
- **Nuevo en el ciclo 80:** el splash UWP (Q-032) cambia sólo la coreografía de
  arranque: una ventana, el splash dentro de ella y sin ventanas adicionales.
  No toca compilación, empaquetado ni blindaje; su verificación es la captura
  offscreen (acento exacto en el contenido, titlebar intacta) y las 13 pruebas
  de `tests/test_splash_top_level.py`, incluido un arranque real por
  subproceso.
- **Nuevo en el ciclo 80:** **R-4a9d1c63** (la vigilancia de parches sólo
  consultaba al arrancar) queda en observación con su prueba de regresión. Es
  un método corto en `packagemaker.py` más la constante `CHECK_TICK_SECONDS`;
  no sustituye nada del empaquetado.
- **Nuevo en el ciclo 81:** **R-8b5c1d47** (el subtítulo de la barra mostraba el
  Markdown de los catálogos) queda en observación con su prueba de regresión.
  Sólo cambia cómo se dibuja un texto existente: no toca compilación,
  empaquetado ni blindaje.
- **Nuevo en el ciclo 81:** **Q-029** añade la tarjeta Configuración → AIDE.
  Escribe en `data/pm.data` con el mismo backend que la página AIDE y no envía
  nada a la red por sí misma; no entra en observación como cambio de motor
  porque no altera compilación, empaquetado ni blindaje.
- La bitácora completa de ciclos vive en `docs/ciclos_mantenimiento.md`.

- Octogésimo segundo ciclo (2026-11-28): once reportes nuevos (issues #17–#27)
  registrados; se corrige **R-5e9c1d87** (issue #24: perfil duplicado y recuento
  de repositorios perdido) y pasa a observación. El detalle vive en
  `CHANGELOG.md` y en `docs/ciclos_mantenimiento.md`.

- Septuagésimo primer ciclo (2026-11-27): se corrige **R-6b4d2f81**, encontrado
  al reproducir R-3a9c6e28: las cuatro ventanas de `lib/coreUpdater/windows.py`
  morían al construirse (`Qt.WindowFlags` no existe en PyQt6, `CustomTitleBar`
  no acepta `is_main` ni expone `set_color`, y `LeviathanProgressBar` no tiene
  `setValue`), así que la actualización con interfaz nunca llegaba a abrirse.
  También se corrige **R-3a9c6e28**: el `updater.py` de las plantillas creaba la
  `QApplication` dentro del hilo de vigilancia; ahora `main()` crea la
  aplicación y `UpdateWatcher` avisa por señal encolada, de modo que la ventana
  nace en el hilo de la interfaz. Las dos quedan en observación. No se prepara
  release.
- Septuagésimo ciclo (2026-11-27): se aplica **Q-017**: el `updater.py` de los
  proyectos nuevos ya tiene CLI (`--check`, `--install`, `--target`,
  `--silent`, `--version`) con códigos de salida y termina cuando no hay
  interfaz; antes cualquier argumento se ignoraba y el proceso se quedaba en un
  bucle infinito (reproducido: `timeout 6` devuelve 124). La auditoría del mismo
  ciclo deja dos hallazgos nuevos: **R-7f2b9c41** (la plantilla trata el
  `.iflapp` de la release como ZIP, así que nunca podía instalar una
  actualización; decisión en **Q-034**) y **R-3a9c6e28** (`verificar()` crea la
  `QApplication` en un hilo). Se añade **Q-035** para que el propietario elija
  entre la opción dura y la blanda de Q-018, que quedó marcada sin indicar
  cuál. No se prepara release.
- Sexagésimo noveno ciclo (2026-11-27): se corrige **R-7c4a1e95** (guardar
  ajustes congelaba la interfaz). Medido: `store.save()` 0,5 ms y un guardado de
  ruta 1,7 ms, pero un cambio de apariencia 120 ms porque `set_qss()` reinstalaba
  hojas idénticas y Qt re-pulía el árbol. `set_qss()` ahora es idempotente: el
  guardado baja a ~5 ms y `central` ya no recibe `StyleChange`. Queda en
  observación. No se prepara release: sigue pendiente el entorno aislado de
  Q-019 y el resto de cambios de engine aprobados.

- Sexagésimo octavo ciclo (2026-11-27): se corrige **R-3e7d1c58** y se archiva
  (Q-004/F-001, opción A): `compile-only` compila todos los `.py` del paquete,
  retira sus fuentes (salvo el `updater.py` obligatorio) y conserva el fuente
  sólo en builds `zipapp`; los manifiestos de digests se calculan después de la
  retirada. Queda en observación. No se prepara release: siguen pendientes los
  cambios de engine aprobados Q-019 y Q-012.
- Sexagésimo séptimo ciclo (2026-11-26): se corrige **R-7d4b2c95**, la mitad
  reproducible de R-7c4a1e95: maximizar o restaurar llamaba a `apply_theme`,
  que reinstala la hoja global de la aplicación y re-pule todos los widgets
  (~270 ms por gesto, medidos en offscreen). El gesto ahora sólo refresca el
  radio de las esquinas (~59 ms) y `apply_global_stylesheet()` no reinstala una
  hoja idéntica (ahorra ~185 ms al cambiar de modo de visualización). Queda en
  observación; R-7c4a1e95 sigue abierto por el guardado en segundo plano
  (Q-012). No se prepara release.
- Sexagésimo sexto ciclo (2026-11-26): se corrige **R-8d3f6a21**, el backend
  Nuitka que no compilaba (opciones de salida sin `=`, familia de plugins Qt
  inexistente e importación de `MainControl` fuera del `try`), y se verifica con
  una compilación real `--standalone --onefile`. Queda en observación; R-4d9e2b61
  sigue abierto sólo por el entorno aislado de Q-019.
- Sexagésimo quinto ciclo (2026-11-26): se corrige **R-2f8b6a31** (el triple
  gesto de la titlebar nunca llegaba a pantalla completa y el modo inmersivo no
  maximizaba la ventana) y se archiva en `docs/bugs_resueltos.md`. Se compacta
  esta cola a petición del propietario en el issue #15: fuera los resueltos,
  los cambios de engine reducidos a su índice y las fichas en `CONFIRM.MD`.

- Septuagésimo segundo ciclo (2026-11-27): no había reportes nuevos en los
  issues #4, #10, #11, #13, #14 ni #15, no había pull requests abiertas y
  `CONFIRM.MD` no tenía respuestas nuevas, así que el ciclo aplica una
  aprobación de prioridad alta: **Q-019** (R-4d9e2b61, «nada tiene el entorno
  aislado»). El build compila ahora dentro de un venv por proyecto
  (`<proyecto>/build/pm-sandbox/<backend>/venv`): instala las dependencias del
  proyecto y las del backend, comprueba que el backend se importa dentro del
  entorno y lanza Nuitka o PyInstaller como subproceso; el binario se copia a
  `dist` como antes y, si el entorno falla, se reintenta con el backend
  embebido. Se añade la tarjeta **Configuración → Red** con el modo de uso
  medido que pidió el propietario (sin descargas, aviso de que hace falta Python
  del sistema y de cómo seguir sin conexión). Verificado con dos compilaciones
  reales (PyInstaller 10,9 s y Nuitka 60,5 s) cuyos binarios se ejecutaron
  correctamente. R-4d9e2b61 queda en observación. No se prepara release: siguen
  pendientes los cambios de engine aprobados y R-7f2b9c41 espera Q-034.
- Septuagésimo tercer ciclo (2026-11-27): sin reportes nuevos en los issues #4,
  #10, #11, #13, #14 ni #15, sin pull requests abiertas y sin respuestas nuevas
  en `CONFIRM.MD`, así que se aplica la aprobación de prioridad alta **Q-027**
  (R-7b2c9e51, issue #13: el splash se retiraba antes de que la interfaz
  estuviera dibujada y los tirones no se reportaban). Nuevo
  `lib/startup_timing.py`: mínimo del splash de 5 s más hasta 1 s según los
  puntos de rendimiento (RAM y núcleos), redondeado a 0,25 s; `StartupTimeline`
  mide cada fase y `SplashWaiter` retrasa el cierre sin bloquear el bucle de
  eventos, guardando el tiempo real de arranque antes de la espera. Si una fase
  supera 0,5 s o la interfaz no está lista dentro del mínimo, se encola un
  reporte `StartupLag` con las fases medidas y los errores restantes, con el
  opt-in de Reportes y sin duplicar entradas. Verificado con el arranque real
  (mínimo 5,50 s, cierre a los 5,61 s; con `PM_SPLASH_MIN_SECONDS=0.05` el
  reporte aparece en la cola con las fases medidas). R-7b2c9e51 queda en
  observación. No se prepara release: siguen pendientes los cambios de engine
  aprobados y R-7f2b9c41 espera Q-034.
- Septuagésimo cuarto ciclo (2026-11-27): sin reportes nuevos en los issues #4,
  #10, #11, #13, #14 ni #15, sin pull requests abiertas y sin respuestas nuevas
  en `CONFIRM.MD`, así que se aplica la mejora aprobada **Q-021** (R-7b3e9a52,
  issue #11: «un apartado de ayuda relacionado con toda la app»). Nuevo addon
  `help` (`addons/help.yaml`) y página `lib/help_page.py`: cuatro temas (crear,
  compilar, blindar, reportar) con buscador que filtra por título y cuerpo,
  barra de acciones propia y retraducción en vivo. Los textos viven en
  `help.*` de los 14 catálogos de `lang/` y el icono se añade a
  `lib/app_icons.py`. Sin cambios de comportamiento del engine. Verificado en
  la ventana real (offscreen): el sidebar queda create, build, config, moonfix,
  report, help, aide, about; el subtítulo sale del manifiesto y «upx» deja sólo
  el tema de blindaje. Pruebas: `tests/test_help_page.py`. R-7b3e9a52 sale de
  la cola. No se prepara release: siguen pendientes los cambios de engine
  aprobados y R-7f2b9c41 espera la decisión de Q-034.
- Septuagésimo quinto ciclo (2026-11-27): sin reportes nuevos en los issues #4,
  #10, #11, #13, #14 ni #15, sin pull requests abiertas y sin respuestas nuevas
  en `CONFIRM.MD`. Se aplica la mitad segura de **Q-026** (R-5a7d2f16): el
  sidebar se creaba con `WA_TranslucentBackground`, que anula el fondo QSS del
  widget, así que el blanco translúcido nunca se pintaba. Ahora usa
  `WA_StyledBackground`, `SIDEBAR_BG` pasa a `rgba(28,28,30,0.45)` y se añade
  `SIDEBAR_BG_LIGHT` `rgba(255,255,255,0.45)`, con los roles
  `sidebar-light`/`sidebar-frame-light` resueltos por tema. Verificado con
  capturas offscreen (blanco en claro, oscuro en oscuro) y
  `tests/test_theme_surfaces.py`. La superficie y el texto de las pestañas no se
  invierten: los ~40 estilos de `lib/fluent_theme.py` llevan `color:white` y el
  texto quedaría invisible sobre un fondo claro; el alcance se pregunta en
  Q-036. R-8f4b2d61 se archiva en `docs/bugs_resueltos.md`. Suite: 1441 pasan,
  1 omitida, 64 subtests; `pyflakes` limpio. No se prepara release: siguen
  pendientes los cambios de engine aprobados y R-7f2b9c41 espera Q-034.
- Septuagésimo sexto ciclo (2026-11-27): sin reportes nuevos en los issues #4,
  #10, #11, #13, #14 ni #15, sin pull requests abiertas y sin respuestas nuevas
  en `CONFIRM.MD`. Se aplica en parte **Q-022** (R-2c8d4f71): los manifiestos
  del sidebar pasan de `addons/` a `lib/addons/` —la ubicación que pidió el
  propietario en el issue #11— y `addons/` se conserva como ruta de
  compatibilidad. El nuevo `load_addons_from_dirs()` combina los directorios
  existentes sin duplicar ids (gana el primero); `packagemaker.py` y
  `--list-addons` usan el resolutor. Pruebas: `ShippedDirsTest` (precedencia,
  compatibilidad y respaldo) y `tests/test_help_page.py` apunta a la nueva
  ruta. La instalación de un addon `.yaml` desde Configuración sigue pendiente:
  exige UI nueva y claves en los 14 catálogos, así que se hará en un ciclo
  propio. Suite: 1444 pasan, 2 omitidas, 64 subtests; `pyflakes` limpio. No se
  prepara release: siguen pendientes los cambios de engine aprobados y
  R-7f2b9c41 espera Q-034.
- Septuagésimo séptimo ciclo (2026-11-27): sin reportes nuevos en los issues #4,
  #10, #11, #13, #14 ni #15, sin pull requests abiertas y sin respuestas nuevas
  en `CONFIRM.MD`, así que se completa **Q-022** (R-2c8d4f71, issue #11) con su
  segunda mitad: instalar un addon `.yaml` desde Configuración → Extensiones.
  Nuevos `user_addons_dir()`, `all_addons_dirs()`, `installed_addons()` e
  `install_addon()` en `lib/addons_engine.py`: el manifiesto se valida con el
  mismo `parse_manifest()` del cargador y se rechazan los ids de addons
  incluidos, los manifiestos desactivados, un `builder` que el anfitrión no
  tenga y los `plugin` sueltos (su `.py` se ejecutaría al arrancar; eso queda
  para Q-031). La copia es atómica en `data/addons/`, que se carga después de
  `lib/addons/` y de `addons/`, así que una extensión del usuario nunca
  suplanta una página base. `packagemaker.py` y `--list-addons` usan el nuevo
  resolutor y la tarjeta nueva trae claves en los 14 catálogos. Verificado con
  la ventana real (offscreen): sidebar create, build, config, moonfix, report,
  help, aide, extra, about y la tarjeta muestra «Instaladas: extra». Suite:
  1466 pasan, 1 omitida, 64 subtests; `pyflakes` limpio. No se prepara release: siguen pendientes los
  cambios de engine aprobados y R-7f2b9c41 espera Q-034.
- Septuagésimo octavo ciclo (2026-11-27): sin reportes nuevos en los issues #4,
  #10, #11, #13, #14 ni #15, sin pull requests abiertas y sin respuestas nuevas
  en `CONFIRM.MD`, así que se aplica **Q-030** (R-6f1c8e35, issue #14): la
  tarjeta de cuenta sale del sidebar, las extensiones quedan justo debajo de
  MoonFix y el perfil pasa a ser la extensión «Perfil»
  (`lib/addons/profile.yaml` + `lib/profile_page.py`) con avatar, nombre,
  `@login`, descripción, seguidores y repositorios. La descarga de repositorios
  corre en un `QThread` (`github_identity.fetch_repositories()`: `/user/repos`
  con token y `/users/<login>/repos` sin él) y `GitHubProfile.extras` guarda
  `bio`, `public_repos`, `followers` y `following`. Configuración gana la
  tarjeta **Cuenta** con el estado de la sesión y los botones de acceso y
  cierre, que delegan en el anfitrión; `_refresh_github_card()` refresca
  tarjeta, página y panel a la vez. Claves `sidebar.profile`, `sidebar_desc.9`,
  `profile.*` y `config.account_*` en los 14 catálogos y en
  `tools/translations_curated.py`. Verificado con la ventana real (offscreen):
  sidebar create, build, config, moonfix, report, help, aide, perfil, about.
  Suite: 1481 pasan, 1 omitida, 64 subtests; `pyflakes` limpio. Commit
  `8ac30ad` en `main`. No se prepara release: siguen pendientes los cambios de
  engine aprobados y R-7f2b9c41 espera Q-034.
- Octogésimo ciclo (2026-11-28): sin reportes nuevos en los issues #4, #10,
  #11, #13, #14 ni #15 y sin pull requests abiertas. `CONFIRM.MD` sí trae una
  respuesta nueva del propietario (`0addecb`, autoría verificada): **Q-032
  aprobada** (splash dentro de la ventana, estilo UWP). Además se audita la
  entrega del ciclo anterior y se corrige
  **R-4a9d1c63**: la vigilancia de parches de Q-013 se lanzaba sólo al
  construir la ventana, así que el intervalo de 6 h nunca se reevaluaba y una
  ventana abierta no avisaba de commits nuevos. `CHECK_TICK_SECONDS = 600` y
  `PackageTodoGUI._install_patch_timer()` añaden un `QTimer` hijo de la ventana
  que llama a `_start_patch_watch()` cada 10 minutos; ese método sigue
  aplicando el ajuste del usuario, el modo red «uso medido» y el intervalo de
  6 h. Verificado en la ventana real (offscreen): temporizador activo con
  600000 ms, una consulta con `last_check` de hace 7 h y ninguna con el ajuste
  apagado. Pruebas nuevas en `tests/test_patch_watch.py` y
  `tests/test_patch_watch_ui.py`. No se prepara release: siguen pendientes los
  cambios de engine aprobados, la segunda etapa de Q-013 y R-7f2b9c41 espera la
  decisión de Q-034.
- Septuagésimo noveno ciclo (2026-11-27): sin reportes nuevos en los issues #4,
  #10, #11, #13, #14 ni #15, sin pull requests abiertas y sin respuestas nuevas
  en `CONFIRM.MD` (el último commit que toca el archivo sigue siendo
  mantenimiento de `openhands`). Se aplica la **primera etapa de Q-013**
  (F-006, issue del propietario: «que updater.py notificara en segundo plano
  estando compilado o no sobre nuevos commits y parches de seguridad»). Nuevo
  `lib/patch_watch.py`, sólo biblioteca estándar: un `GET` anónimo a
  `api.github.com/repos/JesusQuijada34/packagemaker/commits/main`, comparación
  con el commit local (marca `applied_commit` de `data/patch_state.json` o
  `HEAD` leído de `.git` sin lanzar git) y seis estados (`up_to_date`,
  `available`, `unknown`, `offline`, `metered`, `disabled`). La consulta corre
  en un hilo daemon y vuelve por la señal `patchChecked`; al arrancar se hace
  cada 6 h, se salta en modo red «uso medido» y se apaga con
  `PM_PATCH_CHECK=0`. Configuración → Notificaciones gana la casilla
  «Avisar de parches y commits nuevos», el botón «Comprobar ahora» y una línea
  con el resultado; el aviso también sale en la barra de estado y como
  notificación nativa si están activas. Diez claves nuevas en los 14 catálogos
  (`tools/translations_updates.py`). Verificado con la consulta real: commit
  local `52e9c89` = último de `main`, estado `up_to_date`. Pruebas:
  `tests/test_patch_watch.py` (21) y `tests/test_patch_watch_ui.py` (9); el
  `conftest` apaga la vigilancia durante la suite para que ningún test salga del
  equipo. La cola queda al día: **Q-029** ya estaba cubierta por el asistente
  AIDE del ciclo 56 (falta sólo trasladar sus campos a Configuración) y
  **Q-014** la aplaza el propietario en `bugs.txt` hasta tener un release
  estable sin reportes. No se prepara release: siguen pendientes los cambios de
  engine aprobados, la segunda etapa de Q-013 (descargar y aplicar el parche) y
  R-7f2b9c41 espera la decisión de Q-034.
