# Cola de bugs y reportes — Influent Package Maker

Última actualización: 2026-11-26 (sexagésimo primer ciclo: Q-016 aplicada — `create` exige `--force`; limpieza de resueltos pedida en el issue #15)
Fuente: [issue #4 — Backlog de Reportes Técnicos](https://github.com/JesusQuijada34/packagemaker/issues/4),
[issue #13](https://github.com/JesusQuijada34/packagemaker/issues/13) y
[issue #14](https://github.com/JesusQuijada34/packagemaker/issues/14)
Rama de trabajo: `main`

Este archivo es la **cola activa** de reportes: solo contiene lo que sigue
abierto. Las 156 entradas ya resueltas se retiraron el 2026-11-25 a
`docs/bugs_resueltos.md` para poder trabajar sin ruido; su detalle también
vive en `CHANGELOG.md`. `bugs.txt` se conserva como documento de origen y plan
histórico.

## Resumen

| ID | Tipo | Prioridad | Estado |
|---|---|---|---|
| R-4f8a2c60 | Bug — splash simultáneo y avisos de ventana en Windows | Alta | Corregido (ciclo 60); en observación; verificación visual en Windows pendiente (issues #15/#16) |
| R-6a1f8c23 | Bug — arrastrar la titlebar maximizada mueve la ventana | Alta | Aprobado Q-011 (F-004); pendiente de implementación |
| R-4d9e2b61 | Bug — Nuitka falla y el build no usa entorno aislado | Alta | Aprobado Q-019; pendiente de implementación |
| R-7c4a1e95 | Bug — la interfaz se congela al maximizar/restaurar | Alta | Aprobado Q-012/Q-011; pendiente de implementación |
| R-2f8b6a31 | Bug — la titlebar no limita los gestos a tres | Media | Aprobado Q-011/F-004; pendiente de implementación |
| R-8c4f1a72 | Bug — la página de Reportes rompe el fondo y no se lee el scrollbar | Media | En observación; verificación visual en Windows (issue #10) |
| R-6d2a8f19 | Bug — `create` del CLI sobrescribía un proyecto existente sin avisar | Baja | Corregido con `--force` (ciclo 61); en observación |
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

**20 entradas en la cola** (bugs, mejoras y cambios de engine). Dos
correcciones ya verificadas se retiraron este ciclo — R-4c1a9e72 (ciclo 58) y
R-4e7a1d92 (ciclo 59), sin reaparición — y quedan archivadas en
`docs/bugs_resueltos.md` y en `CHANGELOG.md`; las 156 anteriores ya estaban
allí. R-6d2a8f19 se corrigió en este ciclo y queda en observación.
---

## Extensión de Reportes (sidebar)

- **Solicitud:** JesusQuijada34 — extensión «reports» en el sidebar que
  comunique con GitHub y envíe issues al repositorio con el token ya
  autenticado, con envío automático al ocurrir errores y telemetría del
  dispositivo (SO, versión, Python, versión de PackageMaker, commit, adjuntos).
- **Estado:** Implementado el 2026-11-18.
- **Módulos nuevos:**
  - `lib/report_telemetry.py` — recoge el entorno y sanea texto libre: la
    carpeta personal pasa a `~`, cualquier ruta absoluta a `<path>` y los
    valores con pinta de credencial a `<redacted>`. No recoge usuario del SO,
    hostname, rutas ni variables de entorno.
  - `lib/github_issue_reporter.py` — publica issues en
    `JesusQuijada34/packagemaker` con el token de `lib/github_identity`.
    Agrupa fallos por huella (comenta en el issue abierto en vez de duplicar) y
    convierte todo error de red o permisos en un resultado, nunca en excepción.
  - `lib/report_queue.py` — cola local (`data/report_queue.json`) para fallos
    sin sesión o sin red, con reintento y registro de huellas ya enviadas.
  - `lib/crash_capture.py` — `sys.excepthook`, `threading.excepthook` y
    manejador de mensajes críticos de Qt. Se instala al principio de `main()`,
    así que también captura fallos anteriores a la ventana (se encolan).
  - `lib/report_page.py` — página del sidebar con sesión, formulario,
    adjuntos, cola pendiente y vista previa del entorno.
- **Ajuste:** `auto_report_errors` (`data/pm.data`, por defecto `true`) y su
  casilla en la página; apagado, los fallos sólo se guardan en local.
- **Privacidad:** documentado en `docs/privacy.md`.
- **Pruebas:** `tests/test_report_extension.py` (23) y
  `tests/test_report_page_ui.py` (14), incluidos el saneado de rutas y
  credenciales, la no publicación sin sesión, la deduplicación y la cola.

### R-8c4f1a72 — La página de Reportes rompe el fondo y el scrollbar no se lee

- **Usuario:** JesusQuijada34 (issue #10, reporte enviado desde la aplicación)
- **Fecha del reporte:** 2026-11-25
- **Prioridad:** Media
- **Estado:** Corregido y probado en Linux/offscreen; **pendiente de
  verificación visual en Windows** (el issue #10 sigue abierto).
- **Descripción:** la pestaña Reportes no coincidía con el resto en el fondo:
  desde la línea superior de la barra de acciones hasta el borde superior se
  veía una banda más oscura. El scrollbar apenas se distinguía y el formulario
  quedaba muy abajo, obligando a desplazarse. La tabla markdown del entorno se
  mostraba con los pipes en crudo.
- **Pasos para reproducirlo:** abrir la pestaña «Reportes» en Windows y
  comparar la franja situada por encima de la barra de acciones con el fondo de
  las demás pestañas; reducir la altura de la ventana para ver el scrollbar.
- **Causa raíz:** la página no tenía `WA_StyledBackground`, usaba un contenedor
  de cabecera con relleno propio y el viewport del `QScrollArea` conservaba el
  color base de la paleta, así que pintaba una capa distinta a la del resto de
  la pila. Todo el contenido iba en una sola columna y el entorno se volcaba
  como markdown en un `QLabel` de texto plano.
- **Solución aplicada:** la página usa el mismo fondo que las demás
  (`WA_StyledBackground`), el viewport del scroll es transparente, el
  contenido se reparte en dos columnas (izquierda: sesión y formulario;
  derecha: cola y entorno) y el scrollbar usa la nueva variante `prominent` de
  `source/qss/qscrollbar.qss` (mango de 12 px y más opaco). La tabla del
  entorno se convierte a HTML con `_environment_html()` y se muestra como tabla
  enriquecida, escapando los valores.
- **Pruebas:** `tests/test_report_page_ui.py` (dos columnas, tabla enriquecida,
  viewport transparente y scrollbar visible) y `tests/test_qss_loader.py`
  (variante `prominent` sin marcadores).
- **Commit:** `b5378ad` (2026-11-25).
- **Fecha de resolución:** pendiente de confirmación visual en Windows.

---

## Mejoras: estado de aprobación

Las propuestas de esta sección y los cambios de engine están recogidos como
preguntas `Q-001`…`Q-020` en `CONFIRM.MD`, el único canal de aprobación válido
(solo JesusQuijada34). El 2026-11-23 el propietario marcó
`[x] SÍ` en Q-001, Q-002, Q-003, Q-005, Q-006, Q-009 y Q-010 (commit `0ac5457`,
autoría verificada con la API de GitHub). Q-001, Q-002 y Q-003 se aplicaron en
el vigésimo quinto ciclo; Q-005, Q-006, Q-009 y Q-010 ya estaban implementados
y quedan verificados por la suite.

El 2026-11-25 el propietario aprobó con instrucciones adicionales Q-004
(opción A), Q-007, Q-008, Q-011, Q-012, Q-013 y Q-014 en el commit `bba72d6`
(autoría verificada con la API de GitHub). Ninguna de esas siete se ha
implementado todavía: la regla de mantenimiento exige una confirmación final
antes de tocar el engine, y esas confirmaciones viven en la sección
«Confirmación final» de `CONFIRM.MD` (`F-001`…`F-006`). Q-014 es una mejora de
UI y queda pendiente de planificación. Q-015…Q-018 siguen sin responder y
Q-019/Q-020 son nuevas. Q-021…Q-026 se añadieron el 2026-11-25 a partir del
issue #11 y también siguen sin responder.

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

### Q-015 — `updater.py --update --silent` con `.iflapp` sigue abriendo una ventana

- **Usuario:** JesusQuijada34 (auditoría interna de mantenimiento; sin reporte
  externo)
- **Fecha del reporte:** 2026-11-25
- **Estado:** Pendiente de aprobación (`Q-015` en `CONFIRM.MD`). **No
  implementado**: cambiaría el comportamiento visible de `--update --silent`.
- **Descripción:** `_update_from_iflapp` ignora el parámetro `silent` y siempre
  construye `IFLAPPInstallerWindow` (o el splash). Sin pantalla, la
  actualización desatendida no instala nada o aborta al crear la ventana.
- **Solución propuesta:** en modo silencioso llamar a
  `install_iflapp(..., silent=True)`, que ya devuelve el resultado real desde
  R-2d5b8f41, y no crear ninguna ventana.
- **Archivos afectados:** `lib/coreUpdater/installer.py`, `updater.py`.

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

### 11. `create` del CLI sobrescribía un proyecto existente sin avisar (R-6d2a8f19)

- **Estado:** Aprobado con la **opción B** en Q-016 (commit `71e50f7`) y
  **corregido** en el ciclo 61; en observación.
- **Actual (antes):** `packagemaker.py create` escribía en la carpeta canónica
  aunque ya existiera y contuviera el guion del usuario. El dashboard y el
  asistente gráfico rechazaban o preguntaban; el CLI lo pisaba en silencio (el
  asistente gráfico se alineó en R-4f7a2c91, pero el CLI seguía igual).
- **Solución aplicada:** el subparser `create` acepta `--force`. Sin él, si la
  carpeta canónica existe, el comando imprime
  `[ERROR] El proyecto ya existe: <ruta>`, sugiere `Usa --force para
  sobrescribirlo.` y sale con código 1; con `--force` avisa con
  `[WARN] Sobrescribiendo el proyecto existente` y regenera el proyecto.
- **Efectos secundarios:** cambia el código de salida de un comando existente;
  los scripts que recrean proyectos a propósito necesitan añadir `--force`.
- **Archivos:** `lib/cliHandler.py`, `tests/test_maintenance_cli_regressions.py`.
- **Riesgo:** bajo para el motor, medio para scripts existentes.

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
- **Estado:** **Corregido el 2026-11-26 (ciclo 60)**; en observación, pendiente
  de la verificación visual en Windows. Aprobado en Q-008 (commit `bba72d6`) y
  confirmado en **F-003** (commit `73dcdcd`).
- **Causa raíz confirmada:** `IntegratedSplash` se creaba con
  `parent=main_window` y `WA_TranslucentBackground` (widget hijo translúcido) y
  se construía después de la ventana principal. El **issue #13** (2026-11-26)
  repite el síntoma («se abren varias ventanas de python antes de la
  interfaz») y sospecha del *Application Frame Host* de Windows; el análisis
  del ciclo 59 lo descarta como causa. La duración mínima del splash que pide
  el mismo issue se registra aparte en **Q-027** (R-7b2c9e51).
- **Solución aplicada:** el splash se crea y se muestra **antes** de
  `PackageTodoGUI()`, sin padre y sobre la superficie disponible; al cerrarse
  llama a `destroy()` y después a `deleteLater()`. La ventana principal se
  muestra debajo y la revela el desvanecido. `updater.py` recibe el mismo
  arreglo. `WipeWindow` sigue aplicándose sólo a ventanas top-level.
- **Pruebas:** `tests/test_splash_top_level.py` (9 casos), incluido el arranque
  real en un subproceso que comprueba que el splash ya está visible y es de
  nivel superior cuando se construye la ventana principal.
- **Commit:** `667780a` (ciclo 60).
- **Fecha de resolución:** 2026-11-26 (Linux/offscreen); verificación visual en
  Windows pendiente.

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

## Issue #13 — Varias ventanas de Python antes de la interfaz

- **Usuario:** JesusQuijada34 ([issue #13](https://github.com/JesusQuijada34/packagemaker/issues/13),
  etiquetas `app-report` y `crash`)
- **Fecha del reporte:** 2026-11-26 (commit `c5d1792`, Windows 10.0.19045,
  2 núcleos, Qt 6.11.0)
- **Descripción:** «al abrir se abren varias ventanas de python antes de la
  interfaz, sera culpa de el application frame host?».
- **Análisis del ciclo 59:** el *Application Frame Host*
  (`ApplicationFrameHost.exe`) es el proceso que aloja las ventanas UWP y sólo
  aparece cuando la aplicación crea ventanas de ese tipo; no es el origen de
  las ventanas vacías. Las ventanas que se ven son las que crea el propio Qt:
  `IntegratedSplash` se construye con `parent=main_window` y
  `WA_TranslucentBackground`, y `WipeWindow` (ventana por capas) se aplica
  sobre un widget hijo. En Windows eso obliga a Qt a crear ventanas nativas
  auxiliares que aparecen y desaparecen antes del primer fotograma. La consola
  lo confirma con `QWidgetWindow(...) must be a top level window` y
  `UpdateLayeredWindowIndirect failed for ptDst=...`.
- **Estado:** Corregido en el ciclo 60 (F-003): el splash es una ventana de
  nivel superior pintada antes de la interfaz. **Siguen abiertos los issues
  #15 y #16**, reportados contra el commit `d9d3c48` (que ya incluye ese
  arreglo): si las ventanas vacías persisten en una ejecución nueva, hace falta
  el detalle de cómo se lanza la aplicación (fuente o compilada) y una captura
  del orden de aparición. La petición de splash **dentro** de la ventana al
  estilo UWP queda como **Q-032** (R-5c9a3e17).
- **Petición añadida (Q-027 / R-7b2c9e51):** duración mínima del splash de ~5 s,
  escalada por RAM/CPU, y reporte de los tirones del arranque (qué se ejecutó,
  cuánto tardó y los errores restantes).

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
