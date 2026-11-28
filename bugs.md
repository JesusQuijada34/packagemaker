# Cola de bugs y reportes — Influent Package Maker

Última actualización: 2026-11-28 (ciclo 85: se corrige **R-9b5d3e72**
—borde del sidebar, issue #21—, el único bug abierto que no dependía de una
decisión del propietario. El separador derecho llevaba `#333333` sobre un fondo
`#1C1C1E`: contraste 1,4:1 e invisible, justo lo que reporta el issue. Ahora es
blanco en tema oscuro y conserva el gris `#D1D1D6` en tema claro, mediante los
tokens nuevos `SIDEBAR_BORDER_DARK`/`SIDEBAR_BORDER_LIGHT`; ningún QSS vuelve a
escribir el color a mano. Verificado con capturas offscreen y una prueba que
muestrea el píxel del borde. Siguen pendientes los casos bloqueados por
decisiones del propietario: **R-6d1e4a83** espera el desglose real de Windows,
**R-7e3a1b95** está bloqueado por la coreografía de Q-032, **R-6c2e4d91** espera
Q-038, **R-7f2b9c41** espera Q-034 y **R-2f9b7c14** espera Q-036. No hay
respuestas nuevas del propietario en `CONFIRM.MD`; el issue #27 (cuenta externa)
queda preparado con propuesta, sin push, hasta que la revise el propietario).
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
| R-7e3a1b95 | Bug — el splash no aparece primero: la ventana se pinta antes (issue #17) | Alta | Bloqueado: orden de Q-032; falta captura de Windows |
| R-6c2e4d91 | Bug — la titlebar se maximiza en el segundo gesto del triple clic (issue #17) | Media | Pendiente de decisión (Q-038) |
| R-2f9b7c14 | Bug — el tema claro no se aplica al contenido (issue #18) | Alta | Diagnosticado; alcance en Q-036 |
| R-6d1e4a83 | Bug — arranque con tirones: 10,3 s en la fase «ventana» (issue #19) | Alta | Mitigado en parte (ciclo 84); falta desglose de Windows |
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

**18 entradas en la cola**: 5 bugs (R-6d1e4a83
mitigado en parte, a la espera del desglose de Windows; R-7e3a1b95 bloqueado por
la coreografía de Q-032), 6 mejoras, 1 tarea de documentación externa y 6
cambios de engine (5 aprobados y pendientes, más R-7c4b9e36 que espera Q-037).
Q-013 sigue «aplicada en parte»: la consulta y el aviso de parches ya están en
`main`; la descarga y la aplicación siguen pendientes. El reparto de Q-013/Q-026
no cambia: el tema claro y las pestañas dependen del alcance que fije el
propietario en Q-036. Siguen archivados Q-029 (AIDE en Configuración), Q-030
(perfil como extensión), Q-022 (addons), Q-021 (ayuda), Q-027 (splash mínimo),
Q-019 (entorno aislado) y Q-032 (splash dentro de la ventana).

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

### R-7e3a1b95 — El splash no aparece primero (issue #17)

- **Usuario:** JesusQuijada34 (issue #17, reporte desde la aplicación).
- **Fecha del reporte:** 2026-11-28
- **Prioridad:** Alta.
- **Descripción:** al arrancar, la ventana se oculta primero y luego «salta» el
  splash, en vez de que el splash sea lo primero que se ve. El resto de
  síntomas del issue (titlebar y pantalla completa) se corrigió como
  **R-4b8e2c76** (ciclo 83); AIDE como chatbot se sigue en **R-8f2e5b13**
  (issue #23); el gesto de maximizar antes del tercer clic es **R-6c2e4d91**.
- **Pasos para reproducirlo:** arrancar la aplicación en Windows y observar la
  secuencia de ventana y splash (reporte de `v3.2.7-26.05-20.13`, commit
  `a1e52d2`, que ya incluye el splash dentro de la ventana de Q-032).
- **Evidencia recogida (ciclo 84):**
  - `main()` crea el splash → muestra la ventana (`main_window.show()`) →
    muestra el splash (`splash.show_splash()`). El orden está fijado por
    `tests/test_splash_top_level.py::test_main_attaches_the_splash_to_the_main_window`,
    que exige `window_at < splash_at < show_at < splash_show_at`, y por la
    coreografía aprobada de Q-032: la cortina es un hijo del área de contenido y
    no puede mostrarse antes que su ventana.
  - Traza de eventos en offscreen: al mostrar la ventana, el splash ya recibe
    `Show` (es hijo) y en el mismo ciclo de pintura se pinta al final, encima de
    la pila de páginas. Aquí no hay fotograma con la ventana descubierta ni
    salto de geometría (el filtro de `Resize` la sincroniza antes de pintar).
  - Si no hay sesión cacheada, `show_github_landing()` sube el landing sobre el
    splash (`landing.raise_()`): esa sí es una ruta donde la cortina queda
    debajo. No es el caso del reporte (usuario con sesión), pero explica un
    splash que «no se ve».
- **Estado:** **bloqueado**. No se puede reproducir el fotograma intermedio en
  Linux/offscreen y cualquier cambio de orden contradice la coreografía de
  Q-032 aprobada por el propietario. Hace falta una captura o grabación del
  arranque en el equipo del reporte (¿se ve la ventana completa, sólo la
  titlebar o el landing?) y el desglose de `StartupTimeline` que ya emite el
  ciclo 84.
- **Solución aplicada:** ninguna todavía (no se toca sin evidencia).
- **Commit / fecha de resolución:** —

### R-6c2e4d91 — La titlebar se maximiza en el segundo gesto del triple clic (issue #17)

- **Usuario:** JesusQuijada34 (issue #17).
- **Fecha del reporte:** 2026-11-28
- **Prioridad:** Media.
- **Descripción:** «antes de tocar 3 veces, ya se maximiza sin esperar por el
  transponedor». El doble clic en la titlebar maximiza (comportamiento nativo de
  Windows) y el tercer gesto entra en modo inmersivo, así que el usuario ve un
  maximizado intermedio. No está claro si espera conservar el doble clic o
  retrasarlo hasta confirmar que no hay un tercer gesto.
- **Pasos para reproducirlo:** tres clics seguidos sobre la titlebar y observar
  el maximizado que ocurre tras el segundo.
- **Estado:** pendiente de la decisión del propietario (**Q-038** en
  `CONFIRM.MD`): mantener el doble clic nativo o retrasar el maximizado.
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
- **Reproducción:** `PM_SPLASH_MIN_SECONDS=0.05` no reproduce el tiempo real y
  los tiempos offscreen no son comparables (aquí la ventana tarda ~0,5 s). Se
  perfila la construcción para separar el trabajo que no depende de la máquina.
- **Evidencia y causa parcial (ciclo 84, medido en offscreen con cProfile e
  instrumentación):**
  1. **i18n cuadrático.** `_lookup_key()` aplanaba el catálogo completo en cada
     `tr()` (y otra vez el de `es` de respaldo): **24.816 aplanados** durante
     construcción + `apply_ui_language` en este equipo (566 consultas). Cada
     `tr()` pagaba O(n) sobre ~1.000 claves.
  2. **QSS releídos del disco.** `qss_loader.read_qss_file()` abría el fichero
     en cada llamada, sin caché: 97 lecturas por ventana. En Windows con
     antivirus cada apertura cuesta más.
  3. **`git rev-parse` en bucle.** El panel Reportes llama a
     `collect_environment()` al construirse y en cada refresco; cada llamada
     lanzaba un subproceso `git` (timeout de 3 s). En Windows el arranque de un
     proceso se nota.
  4. Desglose interno añadido: `ventana_paginas`, `ventana_tema` y
     `ventana_landing`. En offscreen el tramo dominante es `ventana_tema`
     (0,234 s de 0,475 s), que es el pulido de Qt y depende del equipo.
- **Resultado medido (offscreen, mismo equipo):** ventana 0,603 s → 0,475 s
  (−21 %); `idioma_ui` 0,210 s → 0,139 s (−34 %); total 0,759 s → 0,614 s.
- **Estado:** **mitigado en parte**, sigue pendiente. No se puede confirmar la
  desaparición de los 10,32 s sin el desglose de Windows: el siguiente reporte
  `StartupLag` ya trae `ventana_paginas`/`ventana_tema`/`ventana_landing` y
  dirá qué tramo queda.
- **Solución aplicada:** `lib/i18n.py` (`_flat_catalog` con invalidación por
  identidad del catálogo), `lib/qss_loader.py` (`_TEXT_CACHE` por mtime y
  tamaño), `lib/report_telemetry.py` (`_git_commit_cache`), y
  `lib/startup_timing.py` + `packagemaker.py` (desglose de la fase «ventana»).
- **Commit / fecha de resolución:** — (mitigación del ciclo 84).

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
| R-4b8e2c76 | Modo inmersivo: la titlebar no se revelaba, el icono de salir era inalcanzable y la ventana no cubría la barra de tareas (issue #17) | Alta | ciclo 83, 2026-11-28 | `tests/test_immersive_fullscreen.py` |
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

- **Cola:** 18 entradas (ver Resumen). R-6d1e4a83 queda **mitigado en parte**
  en el ciclo 84 (i18n, QSS y `git rev-parse` ya no repiten trabajo, y la fase
  «ventana» emite su desglose) pero no se cierra sin el reporte de Windows.
  R-7e3a1b95 queda **bloqueado** por el orden aprobado en Q-032. R-6c2e4d91
  espera Q-038; R-7f2b9c41 espera Q-034; el tema claro (R-2f9b7c14, issue #18)
  espera Q-036; R-7c4b9e36 (issue #26) espera Q-037. R-4d9e2b61 (Q-019) y
  R-7b2c9e51 (Q-027) siguen en observación tras verificarse con arranques y
  compilaciones reales.
- **Release:** no se prepara. Hay cambios de engine de prioridad alta pendientes
  de implementación, bugs de prioridad alta recién reportados y no ha pasado el
  periodo sin reportes nuevos.
- **Nuevo en el ciclo 85:** **R-9b5d3e72** (issue #21) queda corregido y
  archivado. Sólo cambian los tokens y el QSS del marco del sidebar: el borde
  oscuro pasa de `#333333` a blanco y el claro conserva `#D1D1D6`; no toca
  compilación, empaquetado, blindaje ni el motor. Prueba:
  `tests/test_theme_surfaces.py::test_sidebar_edge_is_white_on_dark_and_gray_on_light`
  (muestrea el píxel del borde con la ventana real offscreen; falla con el
  código anterior).
- **Nuevo en el ciclo 85:** el issue #27, abierto por una cuenta externa
  (`JoseSuppini34`), pregunta si el README incluye capturas y pasos de
  instalación. Corresponde a **R-0b8d2c47**, que ya espera la revisión del
  propietario: se responde con el estado real y no se hace push de la mejora de
  documentación sin su visto bueno.
- **Nuevo en el ciclo 84:** **R-6d1e4a83** queda mitigado en parte. Tres
  repeticiones medidas desaparecen: el catálogo i18n se aplana una vez por
  idioma, cada QSS se lee una vez mientras no cambie y `git rev-parse` se
  consulta una vez por sesión. Además `main` inyecta en `StartupTimeline` los
  tramos `ventana_paginas`, `ventana_tema` y `ventana_landing`, así que el
  próximo reporte `StartupLag` señalará el tramo culpable. Medido en offscreen:
  ventana −21 %, `idioma_ui` −34 %. No toca compilación, empaquetado ni
  blindaje; es seguro y reversible.
- **Nuevo en el ciclo 84:** **R-7e3a1b95** queda bloqueado sin cambio de
  código. El orden ventana→splash está impuesto por Q-032 (el splash es hijo del
  área de contenido) y la traza offscreen no reproduce el fotograma intermedio.
  Se pide al propietario una captura del arranque y el desglose de
  `StartupTimeline`.
- **Nuevo en el ciclo 83:** **R-4b8e2c76** (issue #17) queda en observación. Sólo
  cambia la coreografía del modo inmersivo de `lib/immersive_titlebar.py`: un
  sondeo del puntero de 80 ms mientras el modo está activo, la ocultación al
  abandonar la barra y la geometría de pantalla completa con vuelta al área
  disponible. No toca compilación, empaquetado ni blindaje, y el estado de la
  ventana sigue siendo coherente con `_pm_maximized`.
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

- Octogésimo cuarto ciclo (2026-11-28): sin respuestas nuevas en `CONFIRM.MD`,
  se ataca la fase «ventana» de **R-6d1e4a83** (issue #19) con perfilado. Tres
  repeticiones: `_lookup_key()` aplanaba el catálogo i18n en cada `tr()`
  (24.816 aplanados por arranque), `qss_loader.read_qss_file()` releía el
  fichero en cada widget (97 lecturas) y `collect_environment()` lanzaba
  `git rev-parse` en cada refresco del panel Reportes. Ahora hay caché de
  catálogo aplanado (invalidada por identidad), de texto QSS (por mtime y
  tamaño) y de commit (por sesión), y la ventana mide e inyecta sus tramos
  `ventana_paginas`/`ventana_tema`/`ventana_landing` en el reporte de tirones.
  Medido offscreen: ventana 0,603→0,475 s e `idioma_ui` 0,210→0,139 s. Queda
  mitigado en parte hasta ver el desglose de Windows. **R-7e3a1b95** (splash
  primero) queda bloqueado: el orden está fijado por Q-032 y no se reproduce en
  offscreen. No se prepara release.

- Octogésimo tercer ciclo (2026-11-28): sin reportes nuevos ni respuestas en
  `CONFIRM.MD`, se corrige **R-4b8e2c76**, extraído del issue #17: el modo
  inmersivo ocultaba la titlebar y no la revelaba (el filtro de la ventana no
  veía los `MouseMove` que llegan al contenido), `conceal_titlebar()` no se
  llamaba desde ningún sitio y la ventana se maximizaba al área disponible, así
  que la barra de tareas seguía activa en la franja inferior. Ahora el puntero
  se consulta con un `QTimer` de 80 ms sólo en modo inmersivo, la barra se
  oculta al abandonarla y la ventana cubre la pantalla completa; al salir
  vuelve al área disponible. Queda en observación. El resto del issue #17 se
  reparte entre R-7e3a1b95 (splash), R-6c2e4d91 (gesto de maximizar, con
  Q-038) y R-8f2e5b13 (AIDE). No se prepara release: siguen pendientes los
  cambios de engine aprobados y los bugs de prioridad alta del ciclo 82.

- Octogésimo segundo ciclo (2026-11-28): once reportes nuevos (issues #17–#27)
  registrados; se corrige **R-5e9c1d87** (issue #24: perfil duplicado y recuento
  de repositorios perdido) y pasa a observación. El detalle vive en
