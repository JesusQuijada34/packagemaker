# Confirmaciones del propietario — Influent Package Maker

- **Última revisión:** 2026-11-22
- **Último commit de `CONFIRM.MD` procesado:** ninguno con casillas marcadas; revisado de nuevo el 2026-11-22 en el ciclo del commit de código `3f89823` (el último commit que toca este archivo no es de `JesusQuijada34`, así que no hay respuestas válidas que aplicar)
- **Único aprobador:** JesusQuijada34 (GitHub `JesusQuijada34`)
- **Estado:** 10 preguntas pendientes, 0 aprobadas, 0 rechazadas.

Cómo responder: marca exactamente una casilla por bloque (`[x] SÍ` o `[x] NO`)
con un commit normal (sin force push). Solo se aplican las respuestas cuyo
último commit que toca este archivo tenga como autor a `JesusQuijada34`; el
silencio, una casilla ambigua o una aprobación de otro usuario se tratan como
no respondidas. El detalle técnico de cada punto vive en `bugs.md`
(secciones «Mejoras pendientes de aprobación» y «Cambios de engine pendientes»).

---

## Pendientes

### Q-001 — Telemetría centralizada de errores (R-d23039c0)
- **Tipo:** mejora
- **Fecha:** 2026-11-22
- **Qué se propone:** añadir `lib/errorReporter.py` con envío asíncrono y
  opcional de tracebacks a un servidor externo, con consentimiento explícito,
  sin rutas de usuario ni credenciales y con URL configurable. Desactivado por
  defecto.
- **Archivos/componentes afectados:** `lib/errorReporter.py` (nuevo),
  `packagemaker.py`, `lib/pm_data.py`, `lib/cliHandler.py`, tests y
  documentación de privacidad.
- **Riesgo y efectos secundarios:** implica red y privacidad; si se activa por
  error enviaría datos de entorno. Requiere decisión del responsable.
- **Respuesta del propietario (JesusQuijada34):** `[ ] SÍ`  `[ ] NO`

### Q-002 — Acentos en publisher y appname (R-5d8e2a41)
- **Tipo:** mejora
- **Fecha:** 2026-11-22
- **Qué se propone:** admitir acentos en `publisher`/`appname` transliterándolos
  (`Jesús` → `Jesus`) en el nombre canónico, en lugar de rechazar el proyecto.
- **Archivos/componentes afectados:** `lib/projectNameFormatter.py`
  (`_PROJECT_PATTERN`), `lib/cliHandler.py`, `packagemaker.py`,
  `tests/test_project_name_formatter.py`, `tests/test_canonical_law_and_structure.py`.
- **Riesgo y efectos secundarios:** cambia la ley de nombres y la resolución de
  proyectos existentes con acentos; puede alterar nombres de carpeta, paquete y
  artefacto. Compatibilidad de lectura debe verificarse antes de aplicar.
- **Respuesta del propietario (JesusQuijada34):** `[ ] SÍ`  `[ ] NO`

### Q-003 — Conservar la capitalización del publisher al crear proyectos (R-4c8e1f27)
- **Tipo:** mejora
- **Fecha:** 2026-11-22
- **Qué se propone:** dejar de forzar `.lower()` en el publisher en
  `handle_cli_action('create_project')` y en `_ejecutarCreacionProyecto()`, de
  modo que `Influent` produzca `Influent.demo.…` y `<publisher>Influent</publisher>`.
- **Archivos/componentes afectados:** `lib/cliHandler.py`, `packagemaker.py`,
  `tests/test_maintenance_cli_regressions.py`, `tests/test_issue4_reports.py`.
- **Riesgo y efectos secundarios:** cambia nombres visibles y rutas de build de
  los proyectos nuevos (`influent.*` → `Influent.*`). Los proyectos existentes
  siguen siendo legibles porque la comparación del publisher ignora mayúsculas.
- **Respuesta del propietario (JesusQuijada34):** `[ ] SÍ`  `[ ] NO`

### Q-004 — `compile-only` elimina el fuente del paquete (R-3e7d1c58)
- **Tipo:** mejora
- **Fecha:** 2026-11-22
- **Qué se propone:** tras generar el `.pyc` O2, retirar el `.py` del árbol del
  paquete (nunca del proyecto fuente) o, alternativamente, documentar que solo
  se añade bytecode.
- **Archivos/componentes afectados:** `lib/hardening.py`, `lib/BuildThread.py`,
  `tests/test_hardening.py`.
- **Riesgo y efectos secundarios:** borrado destructivo dentro del paquete; si
  el `.py` es el punto de entrada de un build zipapp, el artefacto deja de
  arrancar. Exige excluir `.pyz` y verificar el backend.
- **Respuesta del propietario (JesusQuijada34):** `[ ] SÍ`  `[ ] NO`

### Q-005 — Aislamiento estricto BlindCube/FlatCube y formato `.blindkpkg`
- **Tipo:** cambio de engine
- **Fecha:** 2026-11-22
- **Qué se propone:** BlindCube compila siempre con Nuitka en entorno aislado y
  firma `.blindkpkg`; FlatCube compila con PyInstaller instalando requisitos en
  el venv del proyecto; eliminar los bloqueos `WinError 32` de `BuildThread`.
- **Archivos/componentes afectados:** `lib/BuildThread.py`, `lib/compilers.py`,
  `lib/engines.py`, `lib/blindcubeEngine/`, `lib/flatcubeEngine/`,
  `lib/iflapp_format.py`, CI y tests de empaquetado.
- **Riesgo y efectos secundarios:** nuevo formato de artefacto y cambios en
  verificación, instalación y compatibilidad con `.iflapp` existentes. Riesgo
  alto.
- **Respuesta del propietario (JesusQuijada34):** `[ ] SÍ`  `[ ] NO`

### Q-006 — Pruebas previas y diálogo `.env` en BlindCube
- **Tipo:** cambio de engine
- **Fecha:** 2026-11-22
- **Qué se propone:** ejecutar pruebas de sintaxis y offscreen antes de
  compilar, y preguntar por la inyección parcial o personalizada de variables
  `.env` mediante un diálogo modal con fondo desenfocado.
- **Archivos/componentes afectados:** `lib/BuildThread.py`,
  `lib/projectConfig.py`, `lib/projectDetailsDialog.py`, `lib/alert_dialog.py`.
- **Riesgo y efectos secundarios:** ejecuta código del proyecto antes de
  empaquetar, alarga el build y añade UI modal. Riesgo alto.
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

### Q-008 — Coreografía de splash y ciclo de vida de ventanas
- **Tipo:** cambio de engine
- **Fecha:** 2026-11-22
- **Qué se propone:** completar la secuencia splash → login → verificación
  interna → ventana principal, con desvanecido tipo cortina, splash convertido
  en ventana de error, `destroy()` tras los códigos de salida y triple clic en
  la titlebar para pantalla completa con ocultación animada.
- **Archivos/componentes afectados:** `lib/splash_bootloader.py`,
  `lib/splash_window.py`, `lib/window_chrome.py`,
  `lib/window_manager_bridge.py`, `packagemaker.py`.
- **Riesgo y efectos secundarios:** cambia el ciclo de vida de ventanas y el
  manejo de errores de arranque. Riesgo medio-alto.
- **Respuesta del propietario (JesusQuijada34):** `[ ] SÍ`  `[ ] NO`

### Q-009 — Rediseño de UI (acento naranja, tarjetas iOS, configuración)
- **Tipo:** cambio de engine
- **Fecha:** 2026-11-22
- **Qué se propone:** acento naranja corporativo, tarjetas con navegación en
  cascada, guardado automático, eliminar el editor de código y el selector de
  modo de ventana, mover información del sistema a «Acerca de», notificaciones
  nativas y selección manual de fuentes.
- **Archivos/componentes afectados:** `lib/design_tokens.py`, `source/qss/*`,
  `lib/fluent_theme.py`, `packagemaker.py`, `lib/pm_dashboard.py`,
  `lib/font_manager.py`, `lang/*`.
- **Riesgo y efectos secundarios:** cambia la identidad visual y elimina
  opciones que algunos usuarios usan; afecta traducciones y tests visuales.
  Riesgo alto.
- **Respuesta del propietario (JesusQuijada34):** `[ ] SÍ`  `[ ] NO`

### Q-010 — Sidebar: hover y modo contraído
- **Tipo:** cambio de engine
- **Fecha:** 2026-11-22
- **Qué se propone:** corregir el parpadeo azul/gris del hover y ocultar el
  bloque de login al contraer la barra lateral, mostrando solo iconos.
- **Archivos/componentes afectados:** `lib/SidebarItem.py`,
  `lib/hover_animation.py`, `packagemaker.py`.
- **Riesgo y efectos secundarios:** altera estados visuales del sidebar.
  Riesgo medio.
- **Respuesta del propietario (JesusQuijada34):** `[ ] SÍ`  `[ ] NO`

---

## Historial

Sin decisiones registradas todavía.
