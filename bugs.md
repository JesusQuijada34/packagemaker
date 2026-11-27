# Cola de bugs y reportes — Influent Package Maker

Última actualización: 2026-11-27 (ciclo 73: aplicada Q-027, la duración mínima
del splash y el reporte de tirones del arranque; R-7b2c9e51 queda en
observación).
Fuente: [issue #4 — Backlog de Reportes Técnicos](https://github.com/JesusQuijada34/packagemaker/issues/4),
[issue #11](https://github.com/JesusQuijada34/packagemaker/issues/11),
[issue #13](https://github.com/JesusQuijada34/packagemaker/issues/13),
[issue #14](https://github.com/JesusQuijada34/packagemaker/issues/14) y
[issue #15](https://github.com/JesusQuijada34/packagemaker/issues/15)
Rama de trabajo: `main`

Este archivo es la **cola activa**: sólo contiene lo pendiente. Los bugs ya
resueltos se retiran en el mismo ciclo y se archivan en
`docs/bugs_resueltos.md` (índice) y en `CHANGELOG.md`; el detalle y la
conversación quedan en el issue. Las fichas de las aprobaciones del propietario
viven en `CONFIRM.MD`, que es la única autoridad para responderlas.

## Resumen

| ID | Tipo | Prioridad | Estado |
|---|---|---|---|
| R-7f2b9c41 | Bug — el updater de los proyectos no puede instalar un `.iflapp` | Alta | Pendiente de decisión (Q-034) |
| R-5a7d2f16 | Mejora — fondo translúcido y colores de pestañas por tema | Media | Aprobado Q-026; pendiente de implementación |
| R-3c8e4b72 | Mejora — faltan ajustes en Configuración | Baja | Pendiente (mejora sin pregunta) |
| R-7b3e9a52 | Mejora — sección de ayuda global (issue #11) | Media | Aprobado Q-021; pendiente de implementación |
| R-2c8d4f71 | Mejora — addons en `lib/addons/` e instalación desde la app (issue #11) | Baja | Aprobado Q-022; pendiente de implementación |
| R-9a4e2c83 | Cambio de engine — GitHub y CloudCube (issue #11) | Media | Aprobado Q-023; pendiente de implementación |
| R-5f1b8d24 | Cambio de engine — updater como extensión (issue #11) | Media | Aprobado Q-024; pendiente de implementación |
| R-8e6a3c15 | Cambio de engine — Leviathan y action bar como control (issue #11) | Media | Aprobado Q-025; pendiente de implementación |
| R-9c3f5a28 | Cambio de engine — librería de paneles y pestañas (issue #14) | Media | Aprobado Q-028; pendiente de implementación |
| R-2a8d4b73 | Cambio de engine — AIDE como chatbot (issue #14) | Media | Aprobado Q-029; pendiente de implementación |
| R-6f1c8e35 | Cambio de engine — perfil de GitHub como extensión (issue #14) | Media | Aprobado Q-030; pendiente de implementación |
| R-3b7e2d94 | Cambio de engine — addons en `lib/addons/` y DLL (issue #14) | Media | Aprobado Q-031; pendiente de implementación |
| R-5c9a3e17 | Cambio de engine — splash UWP dentro de la ventana (issue #15) | Media | **Sin aprobar** (Q-032) |

**13 entradas en la cola**: 1 bug, 4 mejoras de producto y 8 cambios de engine
(7 aprobados y pendientes de implementación, 1 esperando la marca `[x] SÍ`).
R-7b2c9e51 salió de la cola en este ciclo: Q-027 quedó implementada, probada y
verificada con un arranque real (splash cerrado a los 5,61 s con un mínimo de
5,50 s) y con el reporte de tirones en la cola de reportes.
R-4d9e2b61 salió en el ciclo 72 con Q-019 (entorno aislado de compilación).

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

## Mejoras pendientes

### R-5a7d2f16 — Fondo blanco/negro translúcido sobre el blur

- **Usuario:** JesusQuijada34 (`bugs.txt` y issue #11)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Media.
- **Descripción:** fondo blanco o negro según el modo del sistema con
  transparencia (0,3–0,5) combinado con el blur; sidebar blanco translúcido y
  pestañas gris claro con texto gris en modo claro, invertido en oscuro.
- **Estado:** Pendiente (Q-026). No es un fallo reproducible, es una mejora
  visual aprobada.
- **Archivos:** `lib/design_tokens.py`, `source/qss/*`, `lib/fluent_theme.py`.
- **Solución aplicada:** ninguna todavía.

### R-3c8e4b72 — Faltan ajustes en Configuración

- **Usuario:** JesusQuijada34 (`bugs.txt`, commit `bba72d6`)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Baja.
- **Descripción:** agregar más ajustes para que Configuración no quede vacía,
  pero sólo cuando hayan bajado los bugs.
- **Estado:** Pendiente. El propio propietario la condiciona a que bajen los
  bugs; no entra en un ciclo con bugs de prioridad alta abiertos.

### R-7b3e9a52 — Sección de ayuda global de la aplicación (Q-021)

- **Usuario:** JesusQuijada34 (issue #11)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Media.
- **Descripción:** «un apartado de ayuda relacionado con toda la app», no una
  ayuda por página.
- **Estado:** Aprobada (Q-021); pendiente de implementación.
- **Archivos:** `addons/help.yaml`, `lib/help_page.py`, `lang/*.json`, `tests/`.
- **Riesgo:** bajo.

### R-2c8d4f71 — Addons en `lib/addons/` e instalación desde la app (Q-022)

- **Usuario:** JesusQuijada34 (issue #11)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Baja.
- **Descripción:** mover los manifiestos a `lib/addons/` conservando
  compatibilidad con `addons/` y añadir importación/validación de un `.yaml`
  desde Configuración.
- **Estado:** Aprobada (Q-022); pendiente de implementación.
- **Archivos:** `lib/addons_engine.py`, `addons/*.yaml`, `packagemaker.py`,
  `lib/settings_panel.py`, `tests/test_privacy_switch_and_addons_ui.py`.
- **Riesgo:** medio (rutas de carga y empaquetado).

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
| 9 | Q-013 / F-006 | Actualizaciones silenciosas de parches | Aprobado; pendiente | alto |
| 10 | Q-014 | Eventos del sidebar y temas de temporada | Aprobado; pendiente | medio |
| 13 | Q-018 | El build del CLI no valida `details.xml` | Aprobado; pendiente de elegir opción (Q-035) | medio |
| 14 | Q-019 (R-4d9e2b61) | Entorno aislado de compilación | **Aplicado** (ciclo 72); R-4d9e2b61 en observación | alto |
| 15 | Q-020 | Traducción completa al cambiar de idioma | Aprobado; aplicado en parte | medio-alto |
| 16 | Q-023 (R-9a4e2c83) | Conectar proyectos a GitHub y extensión CloudCube | Aprobado; pendiente | alto |
| 17 | Q-024 (R-5f1b8d24) | El updater como extensión con notificaciones | Aprobado; pendiente | alto |
| 18 | Q-025 (R-8e6a3c15) | Completar Leviathan y el action bar como control | Aprobado; pendiente | alto |
| 19 | Q-027 (R-7b2c9e51) | Duración mínima del splash y reporte de tirones | **Aplicado** (ciclo 73); R-7b2c9e51 en observación | medio |
| 20 | Q-028 (R-9c3f5a28) | Librería de paneles y pestañas verticales | Aprobado; pendiente | alto |
| 21 | Q-029 (R-2a8d4b73) | AIDE como chatbot con backend/API/servidor | Aprobado; pendiente | alto |
| 22 | Q-030 (R-6f1c8e35) | Perfil de GitHub como extensión y panel de cuenta | Aprobado; pendiente | medio |
| 23 | Q-031 (R-3b7e2d94) | Addons empaquetados en `lib/addons/` y addons DLL | Aprobado; pendiente | alto |
| 24 | Q-032 (R-5c9a3e17) | Splash dentro de la ventana principal, estilo UWP | **Sin aprobar** | medio-alto |

Ya implementados y verificados: aislamiento BlindCube/FlatCube y `.blindkpkg`
(Q-005), pruebas previas y diálogo `.env` (Q-006), rediseño de UI (Q-009),
sidebar con hover y modo contraído (Q-010), la ventana con arrastre, snap y
límite de tres gestos (Q-011/F-004, R-6a1f8c23 y R-2f8b6a31), el CLI del
`updater.py` de las plantillas (Q-017, ciclo 70), el entorno de compilación
aislado por proyecto con la tarjeta Red (Q-019, ciclo 72) y la duración mínima
del splash con el reporte de tirones (Q-027, ciclo 73).

## En observación

Las correcciones aplicadas y probadas se archivan en `CHANGELOG.md` (detalle) y
en `docs/bugs_resueltos.md` (índice); su conversación queda en el issue. Cuando
reaparezca un caso archivado, se vuelve a abrir aquí con su ID y la referencia
al ciclo anterior.

| ID | Título | Prioridad | Corregido | Prueba de regresión |
|---|---|---|---|---|
| R-8d3f6a21 | El backend Nuitka no podía compilar (opciones inválidas y API embebida sin proteger) | Alta | ciclo 66, 2026-11-26 | `tests/test_nuitka_backend_arguments.py` |
| R-7d4b2c95 | Maximizar o restaurar congelaba la interfaz (~270 ms por gesto) | Alta | ciclo 67, 2026-11-26 | `tests/test_maximize_without_theme_reapply.py` |
| R-3e7d1c58 | `compile-only` no retiraba el fuente del paquete | Media | ciclo 68, 2026-11-27 | `tests/test_hardening.py::CompileOnlySourceRemovalTests` |
| R-7c4a1e95 | La interfaz se congelaba al guardar ajustes (~120 ms por re-pulido redundante) | Alta | ciclo 69, 2026-11-27 | `tests/test_settings_save_repolish.py` |
| R-6b4d2f81 | Las cuatro ventanas del updater morían al construirse (`Qt.WindowFlags`, `is_main`, `set_color`, `setValue`) | Alta | ciclo 71, 2026-11-27 | `tests/test_updater_windows_construct.py` |
| R-3a9c6e28 | El updater de plantilla creaba la `QApplication` en el hilo de vigilancia | Media | ciclo 71, 2026-11-27 | `tests/test_template_updater_gui_thread.py` |
| R-4d9e2b61 | El build no usaba un entorno aislado por proyecto (Q-019) | Alta | ciclo 72, 2026-11-27 | `tests/test_build_sandbox.py`, `tests/test_settings_navigation_bar.py` |
| R-7b2c9e51 | El splash se retiraba antes de que la interfaz estuviera dibujada y los tirones del arranque no se reportaban (Q-027) | Alta | ciclo 73, 2026-11-27 | `tests/test_startup_timing.py` |

## Periodo de observación y release

- **Cola:** 13 entradas (ver Resumen). No hay bugs críticos reportados sin
  atender. El único bug abierto, R-7f2b9c41, espera la decisión de Q-034.
  R-4d9e2b61 (Q-019, entorno aislado) y R-7b2c9e51 (Q-027, splash mínimo y
  reporte de tirones) quedan en observación tras verificarse con arranques y
  compilaciones reales. De Q-012 sólo quedan la barra marquee permanente y las
  notificaciones nativas (mejora, no fallo de rendimiento).
- **Release:** no se prepara. Hay cambios de engine de prioridad alta pendientes
  de implementación y no ha pasado el periodo sin reportes nuevos.
- La bitácora completa de ciclos vive en `docs/ciclos_mantenimiento.md`.

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
