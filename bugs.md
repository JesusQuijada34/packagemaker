# Cola de bugs y reportes — Influent Package Maker

Última actualización: 2026-11-26 (ciclo 67: R-7d4b2c95 corregido y en
observación — maximizar/restaurar ya no congela la interfaz; R-7c4a1e95 queda
sólo por el guardado en segundo plano de Q-012).
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
| R-4d9e2b61 | Bug — el build no usa un entorno aislado por proyecto | Alta | Aprobado Q-019; pendiente de implementación (el fallo de Nuitka se corrigió en R-8d3f6a21) |
| R-7c4a1e95 | Bug — la interfaz se congela al guardar ajustes | Alta | Aprobado Q-012; pendiente de implementación (maximizar/restaurar ya corregido en R-7d4b2c95) |
| R-5a7d2f16 | Mejora — fondo translúcido y colores de pestañas por tema | Media | Aprobado Q-026; pendiente de implementación |
| R-3c8e4b72 | Mejora — faltan ajustes en Configuración | Baja | Pendiente (mejora sin pregunta) |
| R-7b3e9a52 | Mejora — sección de ayuda global (issue #11) | Media | Aprobado Q-021; pendiente de implementación |
| R-2c8d4f71 | Mejora — addons en `lib/addons/` e instalación desde la app (issue #11) | Baja | Aprobado Q-022; pendiente de implementación |
| R-3e7d1c58 | Mejora — `compile-only` no elimina el fuente del paquete | Media | Aprobado Q-004/F-001; pendiente de implementación |
| R-9a4e2c83 | Cambio de engine — GitHub y CloudCube (issue #11) | Media | Aprobado Q-023; pendiente de implementación |
| R-5f1b8d24 | Cambio de engine — updater como extensión (issue #11) | Media | Aprobado Q-024; pendiente de implementación |
| R-8e6a3c15 | Cambio de engine — Leviathan y action bar como control (issue #11) | Media | Aprobado Q-025; pendiente de implementación |
| R-7b2c9e51 | Cambio de engine — splash mínimo y reporte de lags (issue #13) | Alta | Aprobado Q-027; pendiente de implementación |
| R-9c3f5a28 | Cambio de engine — librería de paneles y pestañas (issue #14) | Media | Aprobado Q-028; pendiente de implementación |
| R-2a8d4b73 | Cambio de engine — AIDE como chatbot (issue #14) | Media | Aprobado Q-029; pendiente de implementación |
| R-6f1c8e35 | Cambio de engine — perfil de GitHub como extensión (issue #14) | Media | Aprobado Q-030; pendiente de implementación |
| R-3b7e2d94 | Cambio de engine — addons en `lib/addons/` y DLL (issue #14) | Media | Aprobado Q-031; pendiente de implementación |
| R-5c9a3e17 | Cambio de engine — splash UWP dentro de la ventana (issue #15) | Media | **Sin aprobar** (Q-032) |

**16 entradas en la cola**: 4 bugs/mejoras de producto y 12 cambios de engine
(11 aprobados y pendientes de implementación, 1 esperando la marca `[x] SÍ`).

## Bugs pendientes

### R-4d9e2b61 — La compilación con Nuitka falla y el build no usa un entorno aislado

- **Usuario:** JesusQuijada34 (`bugs.txt`, commit `bba72d6`)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Alta.
- **Descripción:** «la compilación quedó corrupta, todo dice embebido, hay
  errores al compilar con Nuitka, nada tiene el entorno aislado». Pide que el
  build descargue el Python del proyecto, cree un entorno aislado, instale
  dependencias, pruebe, compile y saque el resultado fuera, sin cambiar el
  formato de compilación.
- **Pasos para reproducirlo:** compilar un proyecto con Nuitka y revisar el
  log: los backends se anuncian como «embebidos» y no hay venv por proyecto.
- **Causa raíz:** hay dos causas distintas. Los «errores al compilar con
  Nuitka» eran del backend (R-8d3f6a21: opciones `--output-dir`/
  `--output-filename` sin `=`, familia Qt `styles` inexistente e importación de
  `MainControl` sin proteger), ya corregidos en el ciclo 66. El entorno aislado
  por proyecto simplemente no existe todavía (Q-019).
- **Estado:** Pendiente sólo por Q-019 (entorno aislado por proyecto). El fallo
  de compilación de Nuitka está corregido y en observación como R-8d3f6a21.
- **Solución aplicada:** backend Nuitka corregido y verificado con una
  compilación real `--standalone --onefile`.
- **Commit / fecha de resolución:** — (el entorno aislado sigue abierto).

### R-7c4a1e95 — La interfaz se congela al guardar ajustes

- **Usuario:** JesusQuijada34 (`bugs.txt`, commit `bba72d6`)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Alta.
- **Descripción:** al cambiar opciones de Configuración la interfaz se congela
  un momento mientras se guardan y se aplican. El otro síntoma del reporte
  (maximizar y restaurar) quedó corregido en R-7d4b2c95.
- **Pasos para reproducirlo:** cambiar varias opciones de apariencia en
  Configuración y pulsar guardar.
- **Causa raíz:** el guardado (`pm.data`, `settings.json`) y la reaplicación
  del tema corren en el hilo de la interfaz. La hoja global de la aplicación ya
  no se reinstala cuando el acento y el tema no cambian (ciclo 67); lo que
  queda es mover el guardado a segundo plano, que es Q-012.
- **Estado:** Pendiente (Q-012/F-005). El arrastre, los tres gestos de la
  titlebar y el re-pulido innecesario al cambiar de modo de visualización ya
  están aplicados (R-6a1f8c23, R-2f8b6a31, R-7d4b2c95).
- **Solución aplicada:** parcial (gestos, arrastre y hoja global con caché).
- **Commit / fecha de resolución:** `c346946`, `d6a832a`, ciclo 65; ciclo 67 / —

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

### R-3e7d1c58 — `compile-only` no elimina el fuente original del paquete (Q-004)

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento)
- **Fecha del reporte:** 2026-11-21
- **Prioridad:** Media.
- **Descripción:** `hardening.compile_to_bytecode()` escribe el `.pyc` O2 junto
  al `.py`, pero no retira el fuente; el método promete «sin fuentes legibles».
- **Solicitado:** opción A aprobada en Q-004/F-001: retirar el `.py` del árbol
  del paquete tras generar el `.pyc`, salvo en builds `zipapp`.
- **Estado:** Aprobada y pendiente de implementación.
- **Archivos:** `lib/hardening.py`, `lib/BuildThread.py`,
  `tests/test_hardening.py`.
- **Riesgo:** medio (borrado dentro del paquete).

## Cambios de engine pendientes

Cambian comportamiento fundamental, UI o empaquetado y **sólo se implementan
con la marca `[x] SÍ` del propietario en `CONFIRM.MD`**. La ficha de cada uno
(comportamiento actual, solicitado, efectos secundarios y archivos) vive en su
bloque `Q-xxx` de `CONFIRM.MD`; aquí queda el índice.

| Punto | ID / ficha | Tema | Estado | Riesgo |
|---|---|---|---|---|
| 3 | Q-007 / F-002 | Reorganización de `lib/` y renombrado a GlassCube | Aprobado; pendiente | alto |
| 4 | Q-008 / F-003 (R-4f8a2c60) | Coreografía de splash y ventanas | Aprobado en parte; pendiente | medio-alto |
| 8 | Q-012 / F-005 (R-7c4a1e95) | Tareas en segundo plano y barra marquee | Aprobado; pendiente | alto |
| 9 | Q-013 / F-006 | Actualizaciones silenciosas de parches | Aprobado; pendiente | alto |
| 10 | Q-014 | Eventos del sidebar y temas de temporada | Aprobado; pendiente | medio |
| 12 | Q-017 | CLI en el `updater.py` de las plantillas | Aprobado; pendiente | medio |
| 13 | Q-018 | El build del CLI no valida `details.xml` | Aprobado; pendiente | medio |
| 14 | Q-019 (R-4d9e2b61) | Entorno aislado de compilación | Aprobado; pendiente | alto |
| 15 | Q-020 | Traducción completa al cambiar de idioma | Aprobado; aplicado en parte | medio-alto |
| 16 | Q-023 (R-9a4e2c83) | Conectar proyectos a GitHub y extensión CloudCube | Aprobado; pendiente | alto |
| 17 | Q-024 (R-5f1b8d24) | El updater como extensión con notificaciones | Aprobado; pendiente | alto |
| 18 | Q-025 (R-8e6a3c15) | Completar Leviathan y el action bar como control | Aprobado; pendiente | alto |
| 19 | Q-027 (R-7b2c9e51) | Duración mínima del splash y reporte de lags | Aprobado; pendiente | medio |
| 20 | Q-028 (R-9c3f5a28) | Librería de paneles y pestañas verticales | Aprobado; pendiente | alto |
| 21 | Q-029 (R-2a8d4b73) | AIDE como chatbot con backend/API/servidor | Aprobado; pendiente | alto |
| 22 | Q-030 (R-6f1c8e35) | Perfil de GitHub como extensión y panel de cuenta | Aprobado; pendiente | medio |
| 23 | Q-031 (R-3b7e2d94) | Addons empaquetados en `lib/addons/` y addons DLL | Aprobado; pendiente | alto |
| 24 | Q-032 (R-5c9a3e17) | Splash dentro de la ventana principal, estilo UWP | **Sin aprobar** | medio-alto |

Ya implementados y verificados: aislamiento BlindCube/FlatCube y `.blindkpkg`
(Q-005), pruebas previas y diálogo `.env` (Q-006), rediseño de UI (Q-009),
sidebar con hover y modo contraído (Q-010) y la ventana con arrastre, snap y
límite de tres gestos (Q-011/F-004, R-6a1f8c23 y R-2f8b6a31).

## En observación

Las correcciones aplicadas y probadas se archivan en `CHANGELOG.md` (detalle) y
en `docs/bugs_resueltos.md` (índice); su conversación queda en el issue. Cuando
reaparezca un caso archivado, se vuelve a abrir aquí con su ID y la referencia
al ciclo anterior.

| ID | Título | Prioridad | Corregido | Prueba de regresión |
|---|---|---|---|---|
| R-8d3f6a21 | El backend Nuitka no podía compilar (opciones inválidas y API embebida sin proteger) | Alta | ciclo 66, 2026-11-26 | `tests/test_nuitka_backend_arguments.py` |
| R-7d4b2c95 | Maximizar o restaurar congelaba la interfaz (~270 ms por gesto) | Alta | ciclo 67, 2026-11-26 | `tests/test_maximize_without_theme_reapply.py` |

## Periodo de observación y release

- **Cola:** 16 entradas (ver Resumen). No hay bugs críticos reportados sin
  atender; R-4d9e2b61 (sólo el entorno aislado de Q-019) y R-7c4a1e95 (guardado
  en segundo plano, Q-012) siguen aprobados y pendientes de implementación.
- **Release:** no se prepara. Hay bugs de prioridad alta pendientes de
  implementación y no ha pasado el periodo sin reportes nuevos.
- La bitácora completa de ciclos vive en `docs/ciclos_mantenimiento.md`.

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
