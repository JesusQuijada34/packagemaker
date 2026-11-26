# Confirmaciones del propietario — Influent Package Maker

- **Última revisión:** 2026-11-26 (sexagésimo ciclo)
- **Último commit de `CONFIRM.MD` procesado:** `73dcdcd` (2026-11-26, autor `JesusQuijada34 <jesusquijada34.gh@gmail.com>`, autoría verificada con la API de GitHub; el commit sólo toca este archivo). Aprobó Q-015, Q-017, Q-018, Q-019, Q-020 y Q-021…Q-031, más las seis confirmaciones finales `F-001`…`F-006`, varias con instrucciones adicionales. **Q-016** quedó escrita como `[B] SÍ`, que no es una casilla válida del canal (`[x] SÍ` / `[ ] NO`): no se aplica y se vuelve a preguntar.
- **Único aprobador:** JesusQuijada34 (GitHub `JesusQuijada34`)
- **Estado:** 1 pregunta pendiente de respuesta válida (Q-016); 18 aprobadas pendientes de implementación (Q-004, Q-007, Q-011…Q-015 y Q-017…Q-031, con confirmación final `F-001`, `F-002`, `F-004`, `F-005` y `F-006`); Q-008/F-003 aplicada en parte este ciclo (splash de nivel superior, `destroy()` y fin de las ventanas vacías); 8 aprobadas y aplicadas antes; 0 rechazadas.

Cómo responder: marca exactamente una casilla por bloque (`[x] SÍ` o `[ ] NO`)
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
- **Respuesta del propietario (JesusQuijada34):** `[x] SÍ`  `[ ] NO`
- **Nota del propietario (commit `bba72d6`):** «opción A (el corchete original indicaba la opción elegida)»
- **Estado:** aprobada el 2026-11-25 (commit `bba72d6`) y confirmada en **F-001** el 2026-11-26 (commit `73dcdcd`); pendiente de implementación.

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
- **Respuesta del propietario (JesusQuijada34):** `[x] SÍ`  `[ ] NO`
- **Nota del propietario (commit `bba72d6`):** «Si, pero hazlo cuidadosamente, dejando lib/ sin engines revueltos por todo eso, por lo menos encierras a cada oveja en su corral, asi que procede»
- **Estado:** aprobada el 2026-11-25 (commit `bba72d6`) y confirmada en **F-002** el 2026-11-26 (commit `73dcdcd`); pendiente de implementación, empezando por clasificar los módulos de motor.

### Q-008 — Coreografía de splash y ciclo de vida de ventanas (repetida)
- **Tipo:** cambio de engine
- **Fecha:** 2026-11-23 (repetida: la respuesta anterior quedó partida por el conflicto de merge del commit `0ac5457`, con una casilla vacía en un lado y una marcada en el otro)
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
- **Respuesta del propietario (JesusQuijada34):** `[x] SÍ`  `[ ] NO`
- **Nota del propietario (commit `bba72d6`):** «Si, y quita el arranque de multiples ventanas python antes de correr la interfaz, ya que al abrir el programa lo primero que se ejecuta varias veces es como 5 ventanas python vacias, pequeñas y sin titulo»
- **Estado:** aprobada el 2026-11-25 (commit `bba72d6`) y confirmada en **F-003** el 2026-11-26 (commit `73dcdcd`); **aplicada en parte** el 2026-11-26 (ciclo 60): splash de nivel superior pintado antes de la ventana principal, `destroy()` al cerrarlo y fin de las ventanas vacías de Windows. El triple clic de la titlebar queda con **F-004**.

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
- **Respuesta del propietario (JesusQuijada34):** `[x] SÍ`  `[ ] NO`
- **Estado:** aprobada el 2026-11-25 (commit `bba72d6`) y confirmada en **F-004** el 2026-11-26 (commit `73dcdcd`); pendiente de implementación.

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
- **Respuesta del propietario (JesusQuijada34):** `[x] SÍ`  `[ ] NO`
- **Estado:** aprobada el 2026-11-25 (commit `bba72d6`) y confirmada en **F-005** el 2026-11-26 (commit `73dcdcd`); pendiente de implementación.

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
- **Respuesta del propietario (JesusQuijada34):** `[x] SÍ`  `[ ] NO`
- **Nota del propietario (commit `bba72d6`):** «si y con registros y diff de archivos que no fueron actualizados, para lo mejor, dejar el actualizador de ultimo, eso si, se debe de comprobar si esta compilado o no, si no esta compilado, ofrecer el ultimo commit y un metodo para saber en que commit se encuentra usando regresiones y adelantamientos y al mismo tiempo un diff para ver, si todos los diff pasan a 1, saber que hay que actualizar la app y dejar una marca del commit para saber el estado, pero si esta compilado guiarse del release o del commit del release y compararlo con el ultimo commit en el repo para saber como actualizar, pero se usara blindcube en si mismo para instalar el paquete y reemplazar los archivos»
- **Estado:** aprobada el 2026-11-25 (commit `bba72d6`) y confirmada en **F-006** el 2026-11-26 (commit `73dcdcd`); pendiente de implementación.

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
- **Respuesta del propietario (JesusQuijada34):** `[x] SÍ`  `[ ] NO`
- **Nota del propietario (commit `bba72d6`):** «si, reemplazando por completo el recuadro del sidebar"Contexto"»
- **Estado:** aprobada el 2026-11-25 (commit `bba72d6`); pendiente de planificación (mejora de UI, no cambia el engine y no requiere confirmación final).

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
- **Respuesta del propietario (JesusQuijada34):** `[x] SÍ`  `[ ] NO`
- **Estado:** aprobada el 2026-11-26 (commit `73dcdcd`, autoría verificada); pendiente de implementación.

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
- **Nota del agente (2026-11-26):** el commit `73dcdcd` escribió `[B] SÍ`, que no es una casilla válida del canal, así que **no se aplica**. Si la intención era la **opción B** (`--force` para sobrescribir y rechazo sin él), marca `[x] SÍ` y escribe «opción B» junto a la casilla.

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
- **Respuesta del propietario (JesusQuijada34):** `[x] SÍ`  `[ ] NO`
- **Estado:** aprobada el 2026-11-26 (commit `73dcdcd`, autoría verificada); pendiente de implementación.

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
- **Respuesta del propietario (JesusQuijada34):** `[x] SÍ`  `[ ] NO`
- **Estado:** aprobada el 2026-11-26 (commit `73dcdcd`, autoría verificada); pendiente de implementación.

### Q-019 — Entorno aislado de compilación (reporte del propietario)

- **Tipo:** cambio de engine
- **Fecha:** 2026-11-25
- **Qué se propone:** que el build descargue en la carpeta del proyecto la
  versión de Python correspondiente a la plataforma, cree un entorno aislado,
  instale las dependencias, ejecute las pruebas, compile y mueva el resultado
  fuera del entorno. Hoy Nuitka y PyInstaller se ejecutan «embebidos» en el
  intérprete actual y el reporte del propietario indica errores al compilar con
  Nuitka. El propietario pide conservar el formato de compilación actual.
- **Archivos/componentes afectados:** `lib/blindcubeEngine/BuildThread.py`,
  `lib/blindcubeEngine/compilers.py`,
  `lib/blindcubeEngine/nuitka_embedded.py`,
  `lib/flatcubeEngine/pyinstaller_embedded.py`,
  `lib/blindcubeEngine/build_preflight.py`, `packagemaker.py` y pruebas.
- **Riesgo y efectos secundarios:** descargas de red, más tiempo y espacio de
  build, dependencia de la disponibilidad de los binarios de Python y posible
  divergencia entre lo probado y lo empaquetado. Riesgo alto.
- **Respuesta del propietario (JesusQuijada34):** `[x] SÍ`  `[ ] NO`
- **Nota del propietario (commit `73dcdcd`):** «Pero si se ajusta un nuevo switch en configuracion llamado Red, se puede poner un modo de red de uso medido para usar el emebebido pero avisar que requiere python en el sistema, y da indicaciones para instalarlo y proceder de forma offline»
- **Estado:** aprobada el 2026-11-26 (commit `73dcdcd`) con la instrucción de añadir un interruptor **Red** en Configuración: modo de uso medido que use el entorno embebido, avise de que requiere el Python del sistema y dé indicaciones para instalarlo y seguir sin conexión; pendiente de implementación.

### Q-020 — Traducir toda la interfaz al cambiar de idioma

- **Tipo:** cambio de engine (UI)
- **Fecha:** 2026-11-25
- **Qué se propone:** el reporte del propietario confirma que al cambiar de
  idioma la mayor parte de la interfaz sigue en español. `apply_ui_language()`
  sólo actualiza el sidebar, la descripción, el interruptor de sandbox y el
  selector de motor; las páginas de creación, compilación y configuración, las
  tarjetas, «Acerca de» y el botón de cerrar sesión de GitHub se construyen una
  sola vez con `tr()` o con texto fijo. Opciones: **A)** reconstruir las páginas
  en caliente conservando la página activa y los datos del formulario (mejor
  UX, más riesgo); **B)** reiniciar la aplicación automáticamente tras guardar
  el idioma (simple y fiable, pero cierra la ventana); **C)** mantener la
  actualización instantánea actual y mostrar el banner de reinicio para el
  resto (menor riesgo, no cumple del todo el reporte). Recomendación: A, con B
  como respaldo si la reconstrucción falla.
- **Archivos/componentes afectados:** `packagemaker.py`
  (`apply_ui_language` y construcción de páginas), `lib/pm_dashboard.py`,
  `lib/settings_panel.py`, `lib/settings_cards.py`,
  `lib/github_profile_card.py`, `lib/alert_dialog.py`, `lang/*.json`.
- **Riesgo y efectos secundarios:** pérdida del estado de los formularios,
  widgets duplicados o referencias colgantes si la reconstrucción no es
  completa. Riesgo medio-alto.
- **Respuesta del propietario (JesusQuijada34):** `[x] SÍ`  `[ ] NO`
  (indica A, B o C junto a la casilla)
- **Nota del agente (2026-11-25):** se aplicó la **opción A sin reconstruir
  páginas**, que evita el riesgo que describía este punto (widgets duplicados y
  pérdida del formulario). `lib/live_i18n.py` resuelve el texto visible a su
  clave y lo retraduce en el sitio; `apply_ui_language()` lo invoca al final.
  El bug R-8a3f1c72 queda resuelto con esta implementación.
- **Estado:** aprobada el 2026-11-26 (commit `73dcdcd`); la opción A ya se aplicó sin reconstruir páginas (ciclos 58 y 59) y falta completar los textos que siguen sin traducir.


### Q-021 — Sección de ayuda global de la aplicación
- **Tipo:** mejora
- **Fecha:** 2026-11-25
- **Qué se propone:** el issue #11 pide «un apartado de ayuda relacionado con
  toda la app». Se propone una página de ayuda en el sidebar (addon
  `help.yaml`) con buscador y temas por área (crear, compilar, blindar,
  reportar), con los textos en los catálogos de `lang/`.
- **Archivos/componentes afectados:** `addons/help.yaml`,
  `lib/help_page.py`, `lang/*.json`, `tests/`.
- **Riesgo y efectos secundarios:** bajo; es una página nueva y no toca el
  engine.
- **Respuesta del propietario (JesusQuijada34):** `[x] SÍ`  `[ ] NO`
- **Estado:** aprobada el 2026-11-26 (commit `73dcdcd`, autoría verificada); pendiente de implementación.

### Q-022 — Addons en `lib/addons/` e instalación desde la aplicación
- **Tipo:** mejora
- **Fecha:** 2026-11-25
- **Qué se propone:** mover los manifiestos de addons de `addons/` (raíz) a
  `lib/addons/`, conservando una ruta de compatibilidad, y permitir que el
  usuario instale un addon `.yaml` desde Configuración con validación previa.
- **Archivos/componentes afectados:** `lib/addons_engine.py`,
  `addons/*.yaml`, `packagemaker.py`, `lib/settings_panel.py`,
  `tests/test_privacy_switch_and_addons_ui.py`.
- **Riesgo y efectos secundarios:** medio; cambian las rutas de carga y hay
  que actualizar el empaquetado y las pruebas.
- **Respuesta del propietario (JesusQuijada34):** `[x] SÍ`  `[ ] NO`
- **Estado:** aprobada el 2026-11-26 (commit `73dcdcd`, autoría verificada); pendiente de implementación.

### Q-023 — Conectar proyectos a repositorios de GitHub y extensión CloudCube
- **Tipo:** cambio de engine
- **Fecha:** 2026-11-25
- **Qué se propone:** vincular un proyecto a un repositorio de GitHub eligiendo
  si es público o privado, y añadir una extensión de sidebar llamada
  **CloudCube** que reserve los datos en la cuenta del usuario y garantice que
  la aplicación no se pierde con datos privados en el túnel.
- **Archivos/componentes afectados:** `lib/github_identity.py`,
  `lib/github_issue_reporter.py`, `addons/*.yaml`, `packagemaker.py`,
  `docs/privacy.md`, `tests/`.
- **Riesgo y efectos secundarios:** alto; crea repositorios y sube contenido
  del usuario, requiere permisos de escritura del token y una política de
  privacidad clara. Un fallo podría publicar datos privados.
- **Respuesta del propietario (JesusQuijada34):** `[x] SÍ`  `[ ] NO`
- **Nota del propietario (commit `73dcdcd`):** «pero hay que manifestar el backend de la rama render para que se inicie sesion con github y enviar un codigo a la app para hacer un inicio de sesion mucho mas mejor y directo»
- **Estado:** aprobada el 2026-11-26 (commit `73dcdcd`) con la instrucción de manifestar el backend de la rama `render` para iniciar sesión con GitHub y enviar un código a la aplicación; pendiente de implementación.

### Q-024 — El updater como extensión con notificaciones de Leviathan
- **Tipo:** cambio de engine
- **Fecha:** 2026-11-25
- **Qué se propone:** incrustar el actualizador como extensión del sidebar y
  usar el permiso de notificaciones del motor Leviathan.
- **Archivos/componentes afectados:** `updater.py`, `lib/coreUpdater/`,
  `lib/leviathan_ui/`, `addons/*.yaml`, `packagemaker.py`, `tests/`.
- **Riesgo y efectos secundarios:** alto; se solapa con Q-013/F-006 (el
  programa se reemplaza a sí mismo) y cambia el punto de entrada del updater.
- **Respuesta del propietario (JesusQuijada34):** `[x] SÍ`  `[ ] NO`
- **Estado:** aprobada el 2026-11-26 (commit `73dcdcd`, autoría verificada); pendiente de implementación.

### Q-025 — Completar el motor Leviathan y el action bar como control
- **Tipo:** cambio de engine
- **Fecha:** 2026-11-25
- **Qué se propone:** terminar Leviathan para reducir las líneas de creación de
  controles y layouts, de modo que Leviathan envíe los QSS a cada control y
  layout, con el action bar como control personalizado.
- **Archivos/componentes afectados:** `lib/leviathan_ui/`,
  `lib/page_action_bar.py`, `lib/design_tokens.py`, `lib/fluent_theme.py`,
  `packagemaker.py`, `tests/`.
- **Riesgo y efectos secundarios:** alto; reescribe la construcción de toda la
  interfaz y su sistema de estilos, con riesgo de regresiones visuales y de
  compatibilidad con el respaldo sin `leviathan_ui`.
- **Respuesta del propietario (JesusQuijada34):** `[x] SÍ`  `[ ] NO`
- **Estado:** aprobada el 2026-11-26 (commit `73dcdcd`, autoría verificada); pendiente de implementación.

### Q-026 — Sidebar translúcido y colores de pestañas por tema
- **Tipo:** mejora
- **Fecha:** 2026-11-25
- **Qué se propone:** el issue #11 concreta el fondo translúcido de R-5a7d2f16:
  sidebar con fondo blanco translúcido para combinar con el blur y mantener la
  legibilidad, y pestañas en gris claro con texto gris en modo claro,
  invertido en modo oscuro.
- **Archivos/componentes afectados:** `lib/design_tokens.py`,
  `source/qss/qwidget.qss`, `source/qss/qframe.qss`, `lib/SidebarItem.py`,
  `packagemaker.py`, `tests/`.
- **Riesgo y efectos secundarios:** medio; cambios visuales amplios y
  dependencia del blur del sistema operativo, que no se puede verificar en
  Linux.
- **Respuesta del propietario (JesusQuijada34):** `[x] SÍ`  `[ ] NO`
- **Estado:** aprobada el 2026-11-26 (commit `73dcdcd`, autoría verificada); pendiente de implementación.

### Q-027 — Duración mínima del splash y reporte de tirones del arranque
- **Tipo:** cambio de engine
- **Fecha:** 2026-11-26 (issue #13)
- **Qué se propone:** el splash no se retira hasta pasados ~5 s. El redondeo de
  esos 5 s se calcula con la RAM y los núcleos de CPU (más «puntos de
  rendimiento» = más espera) para dar tiempo a que la interfaz se dibuje. Si el
  arranque sufre tirones, se envía un reporte con qué se ejecutó, cuánto tardó
  y los errores restantes del arranque. Se implementaría junto con Q-008/F-003
  (R-4f8a2c60), que ya está aprobado y elimina las ventanas vacías.
- **Archivos/componentes afectados:** `packagemaker.py` (arranque,
  `IntegratedSplash`), `lib/splash_window.py`, `lib/splash_bootloader.py`,
  `lib/report.py`, `lib/crash_capture.py`, `tests/test_startup_sequence.py`.
- **Riesgo y efectos secundarios:** el arranque tardará al menos 5 s incluso en
  equipos rápidos; el reporte de tirones usa el túnel de reportes, que hoy es
  opt-in, así que se respetará ese ajuste. Si prefieres otro mínimo (p. ej.
  2 s) o que no se envíe nada sin consentimiento explícito, indícalo junto a la
  casilla.
- **Respuesta del propietario (JesusQuijada34):** `[x] SÍ`  `[ ] NO`
- **Nota del propietario (commit `73dcdcd`):** «perfecto»
- **Estado:** aprobada el 2026-11-26 (commit `73dcdcd`, con la nota «perfecto»); pendiente de implementación.

### Q-028 — Librería de paneles y pestañas verticales con action bar propia
- **Tipo:** cambio de engine
- **Fecha:** 2026-11-26 (issue #14)
- **Qué se propone:** extraer una librería de paneles y pestañas verticales como
  las de Configuración, de modo que cada panel traiga su propio action bar y
  lleve por defecto el nombre de la extensión. Las cinco páginas y los addons
  se reconstruirían sobre esa librería.
- **Archivos/componentes afectados:** `lib/page_action_bar.py`,
  `lib/settings_cards.py`, `lib/settings_panel.py`, `packagemaker.py`,
  `addons/*.yaml`, `tests/`.
- **Riesgo y efectos secundarios:** alto; reescribe la estructura de todas las
  páginas y se solapa con Q-025 (action bar como control de Leviathan). No
  cambia la ley de nombres, el formato `.iflapp` ni el contenido de los
  paquetes.
- **Respuesta del propietario (JesusQuijada34):** `[x] SÍ`  `[ ] NO`
- **Nota del propietario (commit `73dcdcd`):** «hazlo con compatibilidad»
- **Estado:** aprobada el 2026-11-26 (commit `73dcdcd`, con la nota «hazlo con compatibilidad»); pendiente de implementación.

### Q-029 — AIDE como chatbot con backend, API, servidor y puerto
- **Tipo:** cambio de engine
- **Fecha:** 2026-11-26 (issue #14)
- **Qué se propone:** AIDE responde como chat (idealmente ya autenticado) o con
  un backend/API/servidor y puerto configurables desde Configuración; los
  prompts de la sesión llegan al chat como contexto.
- **Archivos/componentes afectados:** `lib/aide_page.py`, `lib/pm_data.py`
  (ajustes), `lib/settings_panel.py`, `addons/aide.yaml`, `tests/`.
- **Riesgo y efectos secundarios:** alto; introduce credenciales y tráfico de
  red nuevos. Hay que decidir qué se envía fuera del equipo y dónde se guardan
  las claves; se respetará el ajuste de reportes y no se enviará nada sin
  configuración explícita.
- **Respuesta del propietario (JesusQuijada34):** `[x] SÍ`  `[ ] NO`
- **Estado:** aprobada el 2026-11-26 (commit `73dcdcd`, autoría verificada); pendiente de implementación.

### Q-030 — Perfil de GitHub como extensión y orden del sidebar
- **Tipo:** mejora
- **Fecha:** 2026-11-26 (issue #14)
- **Qué se propone:** las extensiones restantes quedan justo debajo de MoonFix,
  sin la tarjeta de cuenta en medio. La tarjeta de perfil pasa a ser una
  extensión con perfil, repositorios, descripción, avatar y arroba de GitHub, y
  su configuración se añade a Configuración.
- **Archivos/componentes afectados:** `lib/addons_engine.py`, `addons/*.yaml`,
  `packagemaker.py`, `lib/settings_panel.py`, `tests/`.
- **Riesgo y efectos secundarios:** medio; cambia el orden visible del sidebar
  y añade una página que consulta la API de GitHub (límites de peticiones y
  sesión caducada). No toca el motor de compilación.
- **Respuesta del propietario (JesusQuijada34):** `[x] SÍ`  `[ ] NO`
- **Estado:** aprobada el 2026-11-26 (commit `73dcdcd`, autoría verificada); pendiente de implementación.

### Q-031 — Addons empaquetados en `lib/addons/` y addons DLL externos
- **Tipo:** cambio de engine
- **Fecha:** 2026-11-26 (issue #14)
- **Qué se propone:** las extensiones de sistema se empaquetan en carpetas
  dentro de `lib/addons/` (con su YAML ejecutor: funciones, clases e
  importaciones definidas en YAML) y se añade un apartado para instalar
  extensiones basadas en DLL: ZIP con starter, SVG para el sidebar y el YAML que
  añade su configuración a Configuración; los addons que fallan reportan el
  error en vez de romper la ventana.
- **Archivos/componentes afectados:** `lib/addons_engine.py`, `addons/`,
  `lib/settings_panel.py`, `lib/hardening.py` (firma), `packagemaker.py`,
  `tests/`.
- **Riesgo y efectos secundarios:** alto; cargar DLL de terceros es una
  superficie de riesgo (código nativo sin firma) y un intérprete YAML
  sustituiría a Python para las extensiones. Se implementaría con lista de
  confianza y verificación de firma. Recomiendo partir de Q-028 (librería de
  paneles) antes que de esta.
- **Respuesta del propietario (JesusQuijada34):** `[x] SÍ`  `[ ] NO`
- **Nota del propietario (commit `73dcdcd`):** «eso si, tienes razon, porque pueden meter virus de extraccion de datos y fuga, se puede comprometer el programa, tienes que sandboxear las dlls que tienen codigo sospechoso y restringir llamadas a exposiciones de llaves y credenciales del sistema, por ejemplo saber la api de una persona y enviarla a un servidor, debes de ser cuidadoso hasta con los disfraces, de igual se haran parches a la base de datos impulsada por usuarios, para mantener la base limpia y fuerte frente a codigos maliciosos, o tambien ayudarse de un antivirus, aunque antivirus no sabe la base exacta de una fuga de datos»
- **Estado:** aprobada el 2026-11-26 (commit `73dcdcd`) con la instrucción de sandboxear las DLL sospechosas y restringir el acceso a claves y credenciales del sistema; pendiente de implementación.

---

## Confirmación final de cambios de engine aprobados

La regla de mantenimiento exige una confirmación final, indicando exactamente
qué comportamiento cambiará, antes de tocar el engine. Estos seis puntos ya
tienen tu `SÍ` del commit `bba72d6`; marca `SÍ` sólo si quieres que se
implementen tal como se describen. Sin esta marca no se modifica el engine.

### F-001 — Q-004: `compile-only` retira el `.py` del paquete salvo en zipapp

- **Qué cambiará:** `hardening.compile_to_bytecode()` seguirá generando el
  `.pyc` O2 y, además, retirará el `.py` del árbol del paquete (nunca del
  proyecto fuente). En builds `zipapp` el `.py` se conserva porque es el punto
  de entrada del artefacto, y el motivo se registra en el log.
- **Archivos/componentes:** `lib/hardening.py`, `lib/BuildThread.py`,
  `tests/test_hardening.py`.
- **Riesgo:** medio; borrado destructivo dentro del paquete.
- **Respuesta del propietario (JesusQuijada34):** `[x] SÍ`  `[ ] NO`
- **Estado:** confirmación final aprobada el 2026-11-26 (commit `73dcdcd`); pendiente de implementación.

### F-002 — Q-007: reorganizar `lib/` por motores y renombrar a GlassCube

- **Qué cambiará:** los módulos se agruparán en `lib/blindcubeEngine/`,
  `lib/flatcubeEngine/` y `lib/makeselfEngine/`, cada motor en su carpeta, y la
  copia vendorizada de `leviathan_ui` pasará a llamarse **GlassCube**. Se
  actualizarán imports, `requirements.txt` y pruebas.
- **Archivos/componentes:** todo `lib/`, `packagemaker.py`, `updater.py`,
  `tests/`.
- **Riesgo:** alto; rotura masiva de imports y del empaquetado.
- **Respuesta del propietario (JesusQuijada34):** `[x] SÍ`  `[ ] NO`
- **Nota del propietario (commit `73dcdcd`):** «con cuidado, primero clasificar archivos de engine, ordenar y hacer funcionar»
- **Estado:** confirmación final aprobada el 2026-11-26 (commit `73dcdcd`) con la nota «con cuidado, primero clasificar archivos de engine, ordenar y hacer funcionar»; pendiente de implementación.

### F-004 — Q-011: arrastre y ajuste de la ventana maximizada

- **Qué cambiará:** arrastrar la titlebar con la ventana maximizada la
  restaurará a tamaño normal y la moverá con el cursor; subirla al borde
  superior la maximizará y llevarla a un borde lateral la ajustará a media
  pantalla, con transiciones suaves. Se añade el gesto de triple clic para
  pantalla completa. Como máximo se atenderán tres gestos: dos
  maximizar/restaurar y el máximo para pantalla completa.
- **Archivos/componentes:** `lib/window_manager_bridge.py`, `lib/TitleBar.py`,
  `lib/immersive_titlebar.py`, `packagemaker.py`.
- **Riesgo:** medio-alto; depende de gestos nativos que no se pueden verificar
  en Linux.
- **Respuesta del propietario (JesusQuijada34):** `[x] SÍ`  `[ ] NO`
- **Estado:** confirmación final aprobada el 2026-11-26 (commit `73dcdcd`); pendiente de implementación.

### F-005 — Q-012: tareas en segundo plano y barra marquee

- **Qué cambiará:** el guardado y las acciones largas dejarán de bloquear la
  interfaz; mientras haya trabajo se oscurecerá la ventana y se animará una
  barra marquee fina bajo todas las barras de acción. Las notificaciones
  nativas sustituirán al diálogo iOS, elegible en «Aspecto → PushBox».
- **Archivos/componentes:** `lib/page_action_bar.py`, `lib/settings_panel.py`,
  `lib/ios_progress_dialog.py`, `lib/notificationSystem.py`, `lib/report.py`,
  `packagemaker.py`.
- **Riesgo:** alto; escritura concurrente de `pm.data` y cambio del modelo de
  avisos.
- **Respuesta del propietario (JesusQuijada34):** `[x] SÍ`  `[ ] NO`
- **Estado:** confirmación final aprobada el 2026-11-26 (commit `73dcdcd`); pendiente de implementación.

### F-006 — Q-013: actualizaciones silenciosas de parches de seguridad

- **Qué cambiará:** si no hay release nueva, el updater descargará el último
  commit, ejecutará las pruebas de BlindCube, compilará, abrirá el programa con
  salida oculta y, si no hay errores, ofrecerá «Reiniciar para aplicar el
  parche»; al reiniciar se reemplazan los archivos y se notifica
  `{versión}-{commit}`. Sin estar compilado, descargará el ZIP del último
  commit y reemplazará archivos, con registro y diff de lo no actualizado y una
  marca del commit aplicado. Se comprobará si el programa está compilado antes
  de elegir la ruta.
- **Archivos/componentes:** `updater.py`, `lib/coreUpdater/`,
  `lib/blindcubeEngine/`, `version.res`, `details.xml`.
- **Riesgo:** alto; el programa se reemplaza a sí mismo y un fallo puede dejar
  la instalación a medias.
- **Respuesta del propietario (JesusQuijada34):** `[x] SÍ`  `[ ] NO`
- **Nota del propietario (commit `73dcdcd`):** «un fallo reporta algo usando la cuenta logueada, mejor contraste»
- **Estado:** confirmación final aprobada el 2026-11-26 (commit `73dcdcd`) con la nota «un fallo reporta algo usando la cuenta logueada, mejor contraste»; pendiente de implementación.

---

## Historial

### F-003 — Q-008: splash de nivel superior y ciclo de vida de ventanas
- **Decisión:** confirmación final aprobada con `[X] SÍ` en el commit
  `73dcdcd` (2026-11-26; autoría verificada con la API de GitHub).
- **Aplicada:** sexagésimo ciclo (2026-11-26) — `lib/splash_window.py`,
  `updater.py` y `packagemaker.py`.
- **Resultado:** el splash se crea y se muestra **antes** de
  `PackageTodoGUI()`, como ventana de nivel superior (sin padre) que ocupa la
  pantalla disponible; al cerrarse llama a `destroy()` y luego `deleteLater()`.
  El updater hace lo mismo. `WipeWindow` sólo se aplica a ventanas top-level
  (diálogos y ventana principal), que ya era el caso. Las pruebas
  `tests/test_splash_top_level.py` arrancan la aplicación real en un
  subproceso y comprueban que el splash ya está visible y es de nivel superior
  cuando se construye la ventana principal, y que el arranque no emite los
  avisos `must be a top level window`.

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
