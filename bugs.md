# Cola de bugs y reportes — Influent Package Maker

Última actualización: 2026-11-26 (ciclo 63: Q-015 aplicada y archivada)
Fuente: [issue #4 — Backlog de Reportes Técnicos](https://github.com/JesusQuijada34/packagemaker/issues/4),
[issue #13](https://github.com/JesusQuijada34/packagemaker/issues/13) y
[issue #14](https://github.com/JesusQuijada34/packagemaker/issues/14)
Rama de trabajo: `main`

Este archivo es la **cola activa**: solo contiene lo pendiente y una tabla
compacta de lo que está en observación. Los bugs ya resueltos se retiran en el
mismo ciclo y se archivan en `docs/bugs_resueltos.md` (índice) y en
`CHANGELOG.md`; el detalle y la conversación quedan en el issue. No se acumulan
resueltos aquí.


## Resumen

| ID | Tipo | Prioridad | Estado |
|---|---|---|---|
| R-6a1f8c23 | Bug — arrastrar la titlebar maximizada mueve la ventana | Alta | Aprobado Q-011 (F-004); pendiente de implementación |
| R-4d9e2b61 | Bug — Nuitka falla y el build no usa entorno aislado | Alta | Aprobado Q-019; pendiente de implementación |
| R-7c4a1e95 | Bug — la interfaz se congela al maximizar/restaurar | Alta | Aprobado Q-012/Q-011; pendiente de implementación |
| R-2f8b6a31 | Bug — la titlebar no limita los gestos a tres | Media | Aprobado Q-011/F-004; pendiente de implementación |
| R-5a7d2f16 | Mejora — fondo translúcido y colores de pestañas por tema | Media | Aprobado Q-026; pendiente de implementación |
| R-3c8e4b72 | Mejora — faltan ajustes en Configuración | Baja | Pendiente (mejora sin pregunta) |
| R-7b3e9a52 | Mejora — sección de ayuda global de la aplicación (issue #11) | Media | Aprobado Q-021; pendiente de implementación |
| R-2c8d4f71 | Mejora — addons en `lib/addons/` e instalación desde la app (issue #11) | Baja | Aprobado Q-022; pendiente de implementación |
| R-9a4e2c83 | Cambio de engine — conectar proyecto a repo GitHub y CloudCube (issue #11) | Media | Aprobado Q-023; pendiente de implementación |
| R-5f1b8d24 | Cambio de engine — updater como extensión con notificaciones (issue #11) | Media | Aprobado Q-024; pendiente de implementación |
| R-8e6a3c15 | Cambio de engine — completar Leviathan y action bar como control (issue #11) | Media | Aprobado Q-025; pendiente de implementación |
| R-7b2c9e51 | Cambio de engine — duración mínima del splash y reporte de lags (issue #13) | Alta | Aprobado Q-027; pendiente de implementación |
| R-9c3f5a28 | Cambio de engine — librería de paneles y pestañas verticales con action bar (issue #14) | Media | Aprobado Q-028; pendiente de implementación |
| R-2a8d4b73 | Cambio de engine — AIDE como chatbot con backend/API/servidor (issue #14) | Media | Aprobado Q-029; pendiente de implementación |
| R-6f1c8e35 | Cambio de engine — perfil de GitHub como extensión y panel de cuenta (issue #14) | Media | Aprobado Q-030; pendiente de implementación |
| R-3b7e2d94 | Cambio de engine — addons empaquetados en `lib/addons/` y addons DLL (issue #14) | Media | Aprobado Q-031; pendiente de implementación |
| R-5c9a3e17 | Cambio de engine — splash dentro de la ventana principal, estilo UWP (issue #15) | Media | Pendiente de aprobación (Q-032) |

**16 entradas pendientes en la cola** (bugs, mejoras y cambios de engine). Las 4 correcciones en observación están en la tabla de abajo, con enlace al issue; su detalle vive en `CHANGELOG.md`.

---

## Mejoras: estado de aprobación

Estado real (ciclo 63, 2026-11-26): `CONFIRM.MD` es la única autoridad y solo
JesusQuijada34 puede aprobar. Las aprobaciones vigentes llegan de los commits
`0ac5457`, `bba72d6` y `73dcdcd`; Q-001…Q-003, Q-005, Q-006, Q-009, Q-010,
Q-015 y Q-016 ya están aplicadas. Las que siguen abiertas permanecen
**pendientes de implementación** y no se mezclan con los bugfixes. Q-032
(splash UWP, issue #15) sigue sin marcar.

### R-7b3e9a52 — Sección de ayuda global de la aplicación (Q-021)

- **Usuario:** JesusQuijada34 (issue #11, «Orden»)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Media
- **Descripción:** el issue pide «un apartado de ayuda relacionado con toda la
  app», no una ayuda por página.
- **Estado:** Pendiente (Q-021). Es una mejora de producto; no se implementa
  sin aprobación.
- **Solución propuesta:** página de ayuda del sidebar (addon `help.yaml`) con
  buscador, temas por área (crear, compilar, blindar, reportar) y textos desde
  los catálogos de `lang/`.
- **Archivos:** `addons/help.yaml`, `lib/help_page.py`, `lang/*.json`,
  `tests/`.
- **Riesgo:** bajo (página nueva, sin tocar el engine).

### R-2c8d4f71 — Addons en `lib/addons/` e instalación desde la app (Q-022)

- **Usuario:** JesusQuijada34 (issue #11)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Baja
- **Descripción:** el issue pide que «las extensiones del sidebar pueden ir por
  sistema en `lib/addons/`» y que un usuario pueda instalar un addon.
- **Estado:** Pendiente (Q-022). Hoy los manifiestos viven en `addons/` (raíz) y
  `lib/addons_engine.py` los carga desde ahí; no hay instalación desde la app.
- **Solución propuesta:** mover los manifiestos a `lib/addons/` conservando una
  ruta de compatibilidad para `addons/`, y añadir importación/validación de un
  `.yaml` desde Configuración.
- **Archivos:** `lib/addons_engine.py`, `addons/*.yaml`, `packagemaker.py`,
  `lib/settings_panel.py`, `tests/test_privacy_switch_and_addons_ui.py`.
- **Riesgo:** medio (rutas de carga y empaquetado de los addons).

### R-3e7d1c58 — `compile-only` no elimina el fuente original del paquete

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin issue externo)
- **Fecha del reporte:** 2026-11-21
- **Estado:** Aprobada la opción A (Q-004) el 2026-11-25 (commit `bba72d6`);
  pendiente de confirmación final **F-001** e implementación. El propietario
  eligió retirar el `.py` tras generar el `.pyc`, conservándolo en zipapp.
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

El punto 11 (R-6d2a8f19) quedó resuelto en el ciclo 61 y se movió a «En observación».

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

- **Estado:** Aprobado (Q-007) el 2026-11-25 (commit `bba72d6`) con la nota
  «cada oveja en su corral»; pendiente de confirmación final **F-002** e
  implementación. No se ha movido ningún módulo.
- **Actual:** módulos en `lib/` y dependencia opcional `leviathan_ui`.
- **Solicitado:** mover a `blindcubesEngine/`, `flatcubeEngine/`,
  `makeselfEngine/`, integrar la librería y renombrar `leviathan-ui` a
  **GlassCube**.
- **Efectos secundarios:** imports, empaquetado, documentación y tests.
- **Archivos:** todo `lib/`, `packagemaker.py`, `requirements.txt`.
- **Riesgo:** alto (rotura masiva de imports).

### 4. Coreografía de splash y ventanas

- **Estado:** Aprobado (Q-008) el 2026-11-25 (commit `bba72d6`), con la
  petición adicional de eliminar las ventanas Python vacías que aparecen al
  arrancar; pendiente de confirmación final **F-003** e implementación. El
  defecto se registra como R-4f8a2c60. No se ha tocado el ciclo de vida de
  ventanas.

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

- **Estado:** Aprobado (Q-011) el 2026-11-25 (commit `bba72d6`);
  pendiente de confirmación final **F-004** e implementación. Registrado
  como R-6a1f8c23. El propietario añadió el límite de tres gestos: dos
  maximizar/restaurar y el máximo para pantalla completa.
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

- **Estado:** Aprobado (Q-012) el 2026-11-25 (commit `bba72d6`);
  pendiente de confirmación final **F-005** e implementación.
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

- **Estado:** Aprobado (Q-013) el 2026-11-25 (commit `bba72d6`) con las
  condiciones de registro, diff de archivos no actualizados y detección de
  si el programa está compilado; pendiente de confirmación final **F-006**
  e implementación.
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

- **Estado:** Aprobado (Q-014) el 2026-11-25 (commit `bba72d6`) con la nota
  «reemplazando por completo el recuadro del sidebar "Contexto"»; pendiente de
  planificación (mejora de UI, sin confirmación final de engine).
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

### 12. El `updater.py` generado en los proyectos no tiene CLI

- **Estado:** Pendiente (Q-017).
- **Actual:** `src/templates/project/updater.py.template` sólo arranca la GUI;
  ejecutado en un proyecto recién creado se queda en el bucle de `verificar()`
  y no termina. El `updater.py` de la raíz del repositorio sí tiene CLI
  (`--install`, `--update`, `--silent`, códigos de salida).
- **Solicitado:** dar a la plantilla la misma interfaz de línea de órdenes y un
  final claro para `verificar()` cuando no hay GUI.
- **Efectos secundarios:** cambia el contenido de los proyectos nuevos; hay que
  mantener sincronizadas plantilla y actualizador del repositorio.
- **Archivos:** `src/templates/project/updater.py.template`, `updater.py`,
  `tests/test_lifecycle_end_to_end.py`.
- **Riesgo:** medio.

### 13. El build del CLI no valida `details.xml` (versión vacía se adivina)

- **Estado:** Pendiente (Q-018). Detectado en la auditoría del cuadragésimo
  noveno ciclo; no se ha tocado porque rechazar builds que hoy funcionan es un
  cambio de comportamiento.
- **Actual:** la interfaz bloquea la creación y la compilación con
  `validate_build_fields`, pero `packagemaker.py --buildthis` no valida
  `details.xml`. Con `<version></version>` el build **termina con éxito** y
  empaqueta `Influent.demo.v1.0-…` (el motor cae a `v1.0` en silencio) dejando
  dentro del paquete un `details.xml` con la versión vacía; el `updater.py` del
  paquete compara entonces contra una versión vacía. Igual ocurre con un
  publisher o un app no canónicos, que fallan más tarde con otro mensaje.
- **Solicitado:** validar los metadatos de `details.xml` en el build headless
  con la misma puerta que la GUI y responder `[ERROR]` + código 1 (o, si se
  prefiere, sólo avisar y seguir compilando con la versión normalizada).
- **Efectos secundarios:** los scripts que compilan proyectos con metadatos
  incompletos dejarían de funcionar; hay que decidir si el rechazo es duro o
  un aviso. No toca el nombre canónico ni las plantillas.
- **Archivos:** `lib/cliHandler.py` (rama de build), `packagemaker.py`
  (`--buildthis`), `lib/blindcubeEngine/BuildThread.py`,
  `lib/blindcubeEngine/build_validation.py`, `tests/test_build_validation.py`.
- **Riesgo:** medio (comportamiento visible de un comando existente).

### 14. Entorno aislado de compilación (Q-019)

- **Estado:** Pendiente (Q-019). Proviene del reporte del propietario en
  `bugs.txt` (commit `bba72d6`): «la compilación quedó corrupta, todo dice
  embebido, hay errores al compilar con nuitka, nada tiene el entorno aislado».
- **Actual:** Nuitka y PyInstaller se ejecutan «embebidos» en el intérprete
  actual; no se descarga un Python por proyecto ni se crea un entorno aislado.
- **Solicitado:** descargar en la carpeta del proyecto la versión de Python
  correspondiente, crear un entorno aislado, instalar dependencias, ejecutar
  pruebas, compilar, sacar el resultado del entorno y moverlo fuera, sin
  cambiar el formato de compilación.
- **Efectos secundarios:** red, tiempo y espacio de build, dependencia de los
  binarios oficiales de Python y posible divergencia entre lo probado y lo
  empaquetado.
- **Archivos:** `lib/blindcubeEngine/BuildThread.py`,
  `lib/blindcubeEngine/compilers.py`,
  `lib/blindcubeEngine/nuitka_embedded.py`,
  `lib/flatcubeEngine/pyinstaller_embedded.py`,
  `lib/blindcubeEngine/build_preflight.py`, `packagemaker.py`, pruebas.
- **Riesgo:** alto.

### 15. Traducción completa de la interfaz al cambiar de idioma (Q-020)

- **Estado:** Pendiente (Q-020). Proviene del reporte del propietario en
  `bugs.txt` (commit `bba72d6`): «las traducciones están incompletas y la
  mayoría de la interfaz está en español al cambiar de idioma».
- **Actual:** `apply_ui_language()` sólo actualiza sidebar, descripción,
  sandbox y selector de motor; el resto de páginas se construye una sola vez
  con `tr()` o con texto fijo.
- **Solicitado:** elegir entre reconstruir las páginas en caliente (A),
  reiniciar la aplicación al guardar el idioma (B) o mantener el banner de
  reinicio (C). Recomendación: A con B como respaldo.
- **Efectos secundarios:** pérdida del estado de los formularios, widgets
  duplicados o referencias colgantes.
- **Archivos:** `packagemaker.py`, `lib/pm_dashboard.py`,
  `lib/settings_panel.py`, `lib/settings_cards.py`,
  `lib/github_profile_card.py`, `lib/alert_dialog.py`, `lang/*.json`.
- **Riesgo:** medio-alto.

### 16. Conectar proyectos a repositorios de GitHub y extensión CloudCube (Q-023)

- **Estado:** Pendiente (Q-023). Proviene del issue #11.
- **Actual:** el usuario puede autenticarse con GitHub para reportar issues,
  pero no hay forma de vincular un proyecto a un repositorio ni de elegir
  visibilidad pública/privada.
- **Solicitado:** conectar un proyecto a un repositorio de GitHub indicando si
  debe ser público o privado, y una extensión de sidebar llamada **CloudCube**
  que reserve los datos en la cuenta del usuario y garantice que la app no se
  pierde con datos privados en el túnel.
- **Efectos secundarios:** crea repositorios y sube contenido del usuario;
  requiere permisos de escritura del token y una política de privacidad clara.
  Un fallo podría publicar datos privados.
- **Archivos:** `lib/github_identity.py`, `lib/github_issue_reporter.py`,
  `addons/*.yaml`, `packagemaker.py`, `docs/privacy.md`, `tests/`.
- **Riesgo:** alto (datos privados y operaciones remotas destructivas).

### 17. El updater como extensión con notificaciones de Leviathan (Q-024)

- **Estado:** Pendiente (Q-024). Proviene del issue #11.
- **Actual:** `updater.py` y `lib/coreUpdater/` viven fuera del sistema de
  addons y usan sus propios avisos.
- **Solicitado:** incrustar el updater como extensión del sidebar y usar el
  permiso de notificaciones del motor Leviathan.
- **Efectos secundarios:** depende de Q-013/F-006 (actualizaciones silenciosas)
  y del permiso de notificaciones; cambia el punto de entrada del updater.
- **Archivos:** `updater.py`, `lib/coreUpdater/`, `lib/leviathan_ui/`,
  `addons/*.yaml`, `packagemaker.py`, `tests/`.
- **Riesgo:** alto (se solapa con el reemplazo de archivos del propio programa).

### 18. Completar el motor Leviathan y el action bar como control (Q-025)

- **Estado:** Pendiente (Q-025). Proviene del issue #11.
- **Actual:** las páginas construyen sus controles y layouts con PyQt6 y
  aplican QSS desde `lib/design_tokens.py`; la barra de acciones es un helper
  (`lib/page_action_bar.py`), no un control del motor.
- **Solicitado:** terminar el motor Leviathan para reducir las líneas de
  creación de controles y layouts, de modo que Leviathan envíe los QSS a cada
  control y layout, con el action bar como control personalizado.
- **Efectos secundarios:** reescribe la construcción de toda la interfaz y su
  sistema de estilos; riesgo alto de regresiones visuales y de
  compatibilidad con el respaldo sin `leviathan_ui`.
- **Archivos:** `lib/leviathan_ui/`, `lib/page_action_bar.py`,
  `lib/design_tokens.py`, `lib/fluent_theme.py`, `packagemaker.py`, `tests/`.
- **Riesgo:** alto.

### 19. Duración mínima del splash y reporte de lags (Q-027)

- **Estado:** Pendiente (Q-027). Proviene del issue #13.
- **Actual:** `IntegratedSplash` se cierra en cuanto termina la carga
  (`packagemaker.py` llama a `splash.close()` al final de `__init__`), sin
  duración mínima ni medida de rendimiento del arranque.
- **Solicitado:** el splash espera ~5 s antes de retirarse; el redondeo de esos
  5 s se calcula con la RAM y los núcleos de CPU (más puntos de rendimiento =
  más espera) para dar tiempo a que la interfaz se dibuje. Si el arranque sufre
  tirones, se envía un reporte con qué se ejecutó, cuánto tardó y los errores
  del resto del arranque.
- **Efectos secundarios:** el arranque tarda al menos 5 s en todos los equipos
  (incluidos los rápidos); el reporte de lags añade tráfico al túnel de
  reportes, que hoy es opt-in. Se solapa con el ciclo de vida de ventanas de
  Q-008/F-003 (R-4f8a2c60), así que conviene implementarlo junto.
- **Archivos:** `packagemaker.py` (arranque y `IntegratedSplash`),
  `lib/splash_window.py`, `lib/splash_bootloader.py`, `lib/report.py`,
  `lib/crash_capture.py`, `tests/test_startup_sequence.py`.
- **Riesgo:** medio.

### 20. Librería de paneles y pestañas verticales con action bar propia (Q-028)

- **Estado:** Pendiente (Q-028). Proviene del issue #14.
- **Actual:** cada página arma su layout y su barra con
  `install_page_action_bar()`; no existe un control reutilizable de
  panel/pestaña vertical.
- **Solicitado:** una librería de paneles y pestañas verticales como las de
  Configuración, donde cada panel traiga su propio action bar y el título por
  defecto sea el nombre de la extensión.
- **Efectos secundarios:** reescribe la estructura de las cinco páginas y de
  los addons; riesgo alto de regresiones visuales. Depende de Q-025.
- **Archivos:** `lib/page_action_bar.py`, `lib/settings_cards.py`,
  `lib/settings_panel.py`, `packagemaker.py`, `addons/*.yaml`, `tests/`.
- **Riesgo:** alto.

### 21. AIDE como chatbot con backend/API/servidor y puerto (Q-029)

- **Estado:** Pendiente (Q-029). Proviene del issue #14.
- **Actual:** `lib/aide_page.py` es una página estática de ayuda.
- **Solicitado:** AIDE responde como chat (idealmente ya autenticado) o con un
  backend/API/servidor y puerto configurables; los prompts llegan al chat como
  contexto.
- **Efectos secundarios:** introduce credenciales y tráfico de red nuevos,
  además de un cliente HTTP con timeouts y manejo de errores; hay que decidir
  dónde se guardan las claves y qué se envía fuera del equipo.
- **Archivos:** `lib/aide_page.py`, `lib/i18n.py` (contexto),
  `lib/pm_data.py` (ajustes), `addons/aide.yaml`, `tests/`.
- **Riesgo:** alto.

### 22. Perfil de GitHub como extensión y panel de cuenta (Q-030)

- **Estado:** Pendiente (Q-030). Proviene del issue #14.
- **Actual:** el sidebar dibuja las extensiones (Crear Proyecto, Construir
  Paquete, Configuración, MoonFix, Reportes, AIDE, Acerca de) y, entre MoonFix
  y Reportes, la tarjeta «Conecta GitHub». El orden lo fija
  `lib/addons_engine.py` + `packagemaker.py`.
- **Solicitado:** las extensiones restantes van justo debajo de MoonFix, sin la
  tarjeta de cuenta en medio; la tarjeta de perfil pasa a ser una extensión con
  perfil, repositorios, descripción, avatar y arroba de GitHub, y su
  configuración vive en Configuración.
- **Efectos secundarios:** cambia el orden visible del sidebar y añade una
  página con datos de la API de GitHub (límites de peticiones, sesión
  caducada). Es un cambio de interfaz, no de motor, pero toca el manifiesto de
  extensiones.
- **Archivos:** `lib/addons_engine.py`, `addons/*.yaml`, `packagemaker.py`,
  `lib/settings_panel.py`, `tests/`.
- **Riesgo:** medio.

### 23. Addons empaquetados en `lib/addons/` y addons DLL externos (Q-031)

- **Estado:** Pendiente (Q-031). Proviene del issue #14.
- **Actual:** los addons son manifiestos `addons/*.yaml` con código Python en
  `lib/` (p. ej. `lib/aide_page.py`); no hay instalador de extensiones.
- **Solicitado:** extensiones de sistema empaquetadas en carpetas dentro de
  `lib/addons/`, con su YAML ejecutor (funciones, clases e importaciones
  definidas en YAML) y un apartado para instalar extensiones basadas en DLL:
  ZIP con starter, SVG para el sidebar y el YAML que añade su configuración a
  Configuración; los addons que fallan deben reportar el error.
- **Efectos secundarios:** cargar DLL arbitrarias es una superficie de riesgo
  (código nativo de terceros, sin firma); el intérprete YAML sustituiría a
  Python para las extensiones. Muy alto impacto en el motor de addons y en la
  seguridad.
- **Archivos:** `lib/addons_engine.py`, `addons/`, `lib/settings_panel.py`,
  `lib/hardening.py` (firma), `packagemaker.py`, `tests/`.
- **Riesgo:** alto.

---

### 24. Splash dentro de la ventana principal, estilo UWP (Q-032)

- **Estado:** Pendiente de aprobación (Q-032), pedido en el
  [issue #15](https://github.com/JesusQuijada34/packagemaker/issues/15).
- **Actual:** el splash es una ventana de nivel superior que ocupa la pantalla
  disponible (F-003) y se desvanece para revelar la ventana principal.
- **Solicitado:** el patrón de una app UWP: splash dibujado **dentro** de la
  misma ventana, interfaz construida detrás y retirada del splash sin abrir ni
  cerrar ventanas adicionales.
- **Efectos secundarios:** reabre la coreografía aprobada en F-003; la ventana
  principal quedaría visible antes de validar la sesión.
- **Archivos:** `lib/splash_window.py`, `packagemaker.py`, `lib/window_chrome.py`,
  `tests/test_splash_top_level.py`.
- **Riesgo:** medio-alto; no verificable en Windows desde este entorno.

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
- **Estado:** Aprobado Q-011 el 2026-11-25 (commit `bba72d6`); pendiente de
  confirmación final **F-004** e implementación. No se ha modificado el
  comportamiento de la ventana.
- **Propuesta:** ignorar `startSystemMove()` mientras la ventana esté
  maximizada y restaurarla antes de mover; añadir las zonas de ajuste
  (arriba = maximizar, laterales = media pantalla) con transiciones suaves.
- **Archivos afectados:** `lib/window_manager_bridge.py`, `lib/TitleBar.py`,
  `lib/immersive_titlebar.py`, `packagemaker.py`.
- **Riesgo:** medio-alto (snap y maximizado nativos; difícil de verificar sin
  Windows).

## R-4d9e2b61 — La compilación con Nuitka falla y el build no usa un entorno aislado

- **Usuario:** JesusQuijada34 (reporte en `bugs.txt`, commit `bba72d6`)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Alta.
- **Descripción:** el propietario reporta que «la compilación quedó corrupta,
  todo dice embebido, hay errores al compilar con Nuitka, nada tiene el entorno
  aislado». Pide que el build descargue en la carpeta del proyecto la versión
  de Python correspondiente, cree un entorno aislado, instale dependencias,
  ejecute pruebas, compile y saque el resultado fuera del entorno, sin cambiar
  el formato de compilación.
- **Pasos para reproducirlo:** compilar un proyecto con el backend Nuitka y
  revisar el log: los backends se anuncian como «embebidos» y no se crea un
  entorno virtual por proyecto. Se necesita el log completo del fallo de Nuitka
  para confirmar la causa concreta.
- **Causa raíz:** el aislamiento por proyecto es una funcionalidad que aún no
  existe (Q-019); el fallo concreto de Nuitka está pendiente de reproducción en
  un entorno con ese backend instalado.
- **Estado:** Pendiente. La parte de entorno aislado es un cambio de engine
  (Q-019); el error de Nuitka requiere más datos del reporte.
- **Solución aplicada:** Ninguna todavía.
- **Commit:** —
- **Fecha de resolución:** —

## R-7c4a1e95 — La interfaz se congela y renderiza mal al maximizar/restaurar

- **Usuario:** JesusQuijada34 (reporte en `bugs.txt`, commit `bba72d6`)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Media.
- **Descripción:** al maximizar, restaurar o cambiar opciones de configuración,
  la interfaz se queda congelada un momento y el renderizado se ve mal. El
  propietario sugiere animar la interfaz completa, posicionando y estirando o
  contrayendo los controles según el evento.
- **Pasos para reproducirlo:** maximizar y restaurar la ventana varias veces, y
  cambiar opciones de Configuración; se observa el congelamiento.
- **Causa raíz:** la reubicación de widgets y el guardado se ejecutan en el
  hilo de la interfaz; forma parte del cambio de tareas en segundo plano y de
  las transiciones de ventana (Q-012 y Q-011).
- **Estado:** Pendiente (Q-012/Q-011). Depende de las confirmaciones F-005 y
  F-004.
- **Solución aplicada:** Ninguna todavía.
- **Commit:** —
- **Fecha de resolución:** —

## R-2f8b6a31 — La titlebar no limita los gestos a tres (max/restore/fullscreen)

- **Usuario:** JesusQuijada34 (reporte en `bugs.txt`, commit `bba72d6`)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Media.
- **Descripción:** el propietario pide preparar bien el engine de la titlebar:
  debe esperar como máximo tres gestos; dos entradas maximizan o restauran y,
  al llegar al máximo, se pasa a pantalla completa.
- **Pasos para reproducirlo:** hacer doble clic y clics repetidos en la
  titlebar; no hay un límite explícito de gestos ni el paso a pantalla completa.
- **Causa raíz:** el manejador actual no cuenta los gestos ni distingue el
  tercero; está relacionado con R-6a1f8c23 y Q-011/F-004.
- **Estado:** Pendiente (Q-011/F-004). Se implementará junto con el arrastre y
  el ajuste a media pantalla, tras la confirmación final.
- **Solución aplicada:** Ninguna todavía.
- **Commit:** —
- **Fecha de resolución:** —

## R-5a7d2f16 — Fondo blanco/negro translúcido sobre el blur

- **Usuario:** JesusQuijada34 (reporte en `bugs.txt`, commit `bba72d6`)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Baja.
- **Descripción:** el propietario propone un fondo blanco o negro según el modo
  del sistema, con transparencia (0,3–0,5), combinado suavemente con el blur
  para dar el toque macOS, y texto gris en claro y blanco en oscuro. El issue
  #11 concreta el alcance: el **sidebar** con fondo blanco translúcido para
  combinar con el blur y mantener la legibilidad, y las **pestañas** en gris
  claro con texto gris en modo claro, invertido en modo oscuro.
- **Pasos para reproducirlo:** no es un fallo reproducible; es una mejora
  visual solicitada.
- **Causa raíz:** el material actual no superpone una capa translúcida al blur.
- **Estado:** Pendiente (Q-026). Se planificará cuando bajen los bugs; incluye
  el color de las pestañas por tema del issue #11.
- **Solución aplicada:** Ninguna todavía.
- **Commit:** —
- **Fecha de resolución:** —

## R-3c8e4b72 — Faltan ajustes en Configuración

- **Usuario:** JesusQuijada34 (reporte en `bugs.txt`, commit `bba72d6`)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Baja.
- **Descripción:** el propietario pide agregar más ajustes para que
  Configuración no quede vacía, pero sólo cuando los bugs hayan bajado.
- **Pasos para reproducirlo:** no es un fallo; es una mejora de producto.
- **Causa raíz:** la página de Configuración tiene pocas opciones.
- **Estado:** Pendiente (mejora). El propio propietario la condiciona a que
  bajen los bugs; no se implementa en este ciclo.
- **Solución aplicada:** Ninguna todavía.
- **Commit:** —
- **Fecha de resolución:** —

## En observación

Correcciones ya aplicadas y probadas, pendientes de confirmación visual o de
que pase el periodo de observación. El detalle completo está en `CHANGELOG.md`
y en el issue.

| ID | Título | Estado | Seguimiento |
|---|---|---|---|
| R-4f8a2c60 | Splash simultáneo y avisos de ventana en Windows | Corregido (ciclo 60) | issues #13/#15 |
| R-8c4f1a72 | La página de Reportes rompe el fondo y el scrollbar | Corregido (`b5378ad`) | issue #10 |
| R-6d2a8f19 | `create` del CLI sobrescribía un proyecto sin avisar | Corregido con `--force` (ciclo 61) | issue #15 / Q-016 |
| R-6c4d1f87 | Nueve ventanas vacías antes del splash | Corregido (ciclo 62) | issues #15/#16 |

## Periodo de observación y release

- Casos abiertos (sexagésimo tercer ciclo): **16 pendientes** en la cola —
  R-6a1f8c23 (Q-011/F-004), R-4d9e2b61 (Q-019), R-7c4a1e95 (Q-012/Q-011),
  R-2f8b6a31 (Q-011/F-004), R-5a7d2f16 (Q-026), R-3c8e4b72, R-7b3e9a52
  (Q-021), R-2c8d4f71 (Q-022), R-9a4e2c83 (Q-023), R-5f1b8d24 (Q-024),
  R-8e6a3c15 (Q-025), R-7b2c9e51 (Q-027), R-9c3f5a28 (Q-028), R-2a8d4b73
  (Q-029), R-6f1c8e35 (Q-030), R-3b7e2d94 (Q-031) y R-5c9a3e17 (Q-032, sin
  aprobar). Las 20 aprobaciones restantes siguen sin implementar; no se toca
  el engine sin la marca del propietario.
- **En observación:** R-4f8a2c60 (splash de nivel superior), R-8c4f1a72
  (página de Reportes), R-6d2a8f19 (`create --force`) y R-6c4d1f87 (ventanas
  vacías del arranque).
- La bitácora completa de ciclos (del primero al sexagésimo tercero) vive en
  `docs/ciclos_mantenimiento.md`.
- **Release:** no se prepara. Hay bugs de prioridad alta pendientes de
  implementación y no ha pasado el periodo sin reportes nuevos.

- Sexagésimo segundo ciclo (2026-11-26): se corrige **R-6c4d1f87** (los
  issues #15 y #16: nueve ventanas vacías antes del splash) y se archiva en
  `docs/bugs_resueltos.md`. Se purgan de la cola las tres entradas resueltas
  R-d23039c0, R-5d8e2a41 y R-4c8e1f27 y la bitácora se traslada a
  `docs/ciclos_mantenimiento.md`. Verificación: 1327 pasan, 1 omitido, 64
  subtests; `pyflakes` y `py_compile` limpios; arranque real sólo con el
  splash y la ventana principal.
- Sexagésimo tercer ciclo (2026-11-26, commit `02a6786`): se aplica **Q-015** (R-7e3a9c25): el
  updater silencioso con `.iflapp` descarga el paquete, lo instala con
  `install_iflapp(..., silent=True)` y devuelve el resultado real, sin abrir
  ninguna ventana. Se archiva en `docs/bugs_resueltos.md`. Verificación: 1332
  pruebas (5 nuevas), `pyflakes` y `py_compile` limpios.
