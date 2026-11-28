## 2026-11-28 — octogésimo segundo ciclo

### Corregido — perfil duplicado y recuento de repositorios perdido (R-5e9c1d87, issue #24)

Reportado por **JesusQuijada34** en el [issue #24](https://github.com/JesusQuijada34/packagemaker/issues/24):
«está duplicado los apartados del perfil, aparece 2 veces el logo del perfil y
el botón de salir y nada está limpiado, y no aparecen cuántos repositorios en
total hay en el perfil usando conteo por api token».

- **Síntoma.** La página Perfil mostraba dos identidades (dos avatares y dos
  botones «Salir») y, tras reiniciar, el resumen decía 0 repositorios y la
  biografía salía vacía.
- **Causa raíz (dos defectos independientes).**
  1. `build_profile_page()` pasaba a `ProfilePage` la tarjeta compacta
     `GitHubProfileCard` del sidebar y la página, además, construía su propia
     identidad (`_build_identity()`), así que las dos se apilaban.
  2. `github_identity.save_profile()` guardaba login, nombre, avatar y correo,
     pero no `GitHubProfile.extras`; `load_profile()` lo devolvía vacío, de modo
     que `public_repos`, `followers`, `following` y `bio` se perdían en cuanto
     la página se refrescaba desde el almacén.
- **Solución.** La identidad vive sólo en la página: `ProfilePage` ya no acepta
  ni pinta la tarjeta compacta, `packagemaker.py` deja de construirla y
  `_refresh_github_card()` se limita a refrescar la página y la tarjeta de
  cuenta de Configuración. Los extras se guardan como `github_extras` en
  `data/pm.data` y `clear_identity()` los elimina con el resto de la sesión.
- **Pruebas.** `tests/test_profile_page.py`:
  `test_profile_extras_survive_the_store_round_trip`,
  `test_clear_identity_removes_the_saved_extras`,
  `test_profile_page_draws_a_single_identity_and_logout` y
  `test_window_profile_page_has_no_duplicate_account_card` (las dos últimas y
  la primera fallaban con el código anterior).
- **Verificado** con captura offscreen de la página con un perfil guardado: un
  solo avatar, un solo botón «Salir» y «7 repositorios · 12 seguidores · 3
  siguiendo» después de recargar desde el almacén.
- **Sin cambios de motor:** no se toca compilación, empaquetado, blindaje ni el
  contenido de los paquetes.

### Registrados — once reportes nuevos (issues #17–#27)

El propietario reportó desde la aplicación los issues #17 a #26 y la cuenta
externa JoseSuppini34 el #27. Todos quedan en `bugs.md` con su ID y su estado:

| Issue | ID | Tipo | Estado |
|---|---|---|---|
| #17 splash, titlebar y pantalla completa | R-7e3a1b95 | Bug | Pendiente |
| #18 el tema claro no se aplica al contenido | R-2f9b7c14 | Bug | Diagnosticado; alcance en Q-036 |
| #19 arranque con tirones (10,3 s en «ventana») | R-6d1e4a83 | Bug | Pendiente |
| #20 pestañas con color invertido por tema | R-4c8a2f61 | Mejora | Depende de Q-036 |
| #21 borde del sidebar | R-9b5d3e72 | Bug | Pendiente |
| #22 más temas de ayuda | R-1a7c6d94 | Mejora | Pendiente |
| #23 AIDE como chatbot | R-8f2e5b13 | Mejora | Pendiente |
| #25 instancia única | R-3d6a8f25 | Mejora | Pendiente |
| #26 método de compilación de la 3.2.6 | R-7c4b9e36 | Cambio de engine | **Q-037** |
| #27 README con capturas e instalación | R-0b8d2c47 | Documentación | Espera revisión del propietario |

El #18 se diagnosticó con evidencia: `system_theme_mode()` devuelve `light` y
el sidebar resuelve su blanco translúcido, pero el `QStackedWidget` del
contenido conserva `CONTENT_BG` oscuro (`packagemaker_008`) y ~40 estilos de
página llevan `color:white`; invertir sólo la superficie deja los títulos
invisibles. El alcance se pregunta en **Q-036** en lugar de cambiarlo a ciegas.
El #26 no se implementa: es un cambio de engine y queda en **Q-037** a la espera
de la marca `[x] SÍ` del propietario.

## 2026-11-28 — octogésimo primer ciclo

### Aplicado — los campos de AIDE se configuran en Configuración (Q-029 / R-2a8d4b73, issue #14)

Aprobación del propietario en `CONFIRM.MD` (commit `73dcdcd`, autoría
verificada con la API de GitHub), que pedía en el issue #14 un asistente «con un
backend/API/servidor y puerto configurables desde Configuración». El asistente
ya existía desde el ciclo 56 (dos proveedores, clave propia y contexto
saneado); lo que faltaba era exponer sus campos en Configuración.

- **Qué cambia.** Nueva tarjeta **Configuración → AIDE** entre Privacidad y
  Extensiones, con proveedor (GitHub Copilot o endpoint compatible con OpenAI),
  URL del endpoint, modelo, clave de API y la casilla de adjuntar contexto del
  proyecto. La página AIDE conserva sus campos y ambos editores escriben en el
  mismo almacén (`aide_backend.save_settings` → `data/pm.data`), de modo que no
  hay dos fuentes de verdad: la tarjeta avisa con `aideSettingsChanged` y la
  página se refresca con `AidePage.refresh_settings()`.
- **La clave nunca vuelve al widget.** Ni la tarjeta ni la página reescriben la
  clave guardada; el campo queda vacío y su marcador dice «Clave guardada;
  escriba otra para cambiarla». Al escribir una nueva se guarda y se limpia el
  campo, igual que ya hacía la página.
- **Idiomas.** Claves nuevas `config.section_aide*`, `config.aide_*` y
  `aide.api_key_saved` en los 14 catálogos, con traducciones curadas en el
  módulo nuevo `tools/translations_aide.py` (el generador las aplica como las de
  `translations_updates`).
- **Pruebas.** `tests/test_aide_settings_card.py` (9): la tarjeta existe y está
  en su sitio, guarda endpoint, clave, proveedor y contexto, emite la señal, la
  página recoge lo guardado sin copiar la clave y la retraducción mantiene los
  textos.
- **Verificado** en la ventana real (offscreen): «Configuración → AIDE» muestra
  proveedor, URL, modelo, clave y casilla; en inglés el título, las etiquetas y
  el proveedor cambian sin reiniciar.
- **Sin cambios de motor:** no se toca compilación, empaquetado, blindaje ni el
  contenido de los paquetes, y no se envía nada a la red sin configuración.

### Corregido — el subtítulo de la barra mostraba el Markdown de los catálogos (R-8b5c1d47)

Bug encontrado en la auditoría visual de este ciclo. No hay reporte externo.

- **Síntoma.** La descripción bajo el título de la página de creación se leía
  «metadatos para el ecosistema **Influent OS** de forma guiada», con los
  asteriscos a la vista; Construir Paquete mostraba además `` `.iflapp` `` con
  las comillas invertidas. El resto de la interfaz no usa Markdown.
- **Causa raíz.** Los catálogos de idioma guardan las descripciones del sidebar
  (`sidebar_desc.0`, `.1`, `.5`) con Markdown en línea, y
  `set_action_bar_subtitle()` las pasaba tal cual a un `QLabel`, que no
  interpreta Markdown.
- **Solución.** `lib/page_action_bar.inline_markup()` escapa el texto (los
  catálogos no son HTML) y convierte `**negrita**` en `<b>` y `` `código` `` en
  un tramo monoespaciado; el `QLabel` lo dibuja como texto enriquecido. El texto
  sin marcas sale idéntico.
- **Pruebas.** `tests/test_activity_bar_and_subtitle.py::test_subtitle_renders_the_catalog_markdown`
  y `::test_subtitle_escapes_html_and_leaves_plain_text_alone` (la primera falla
  con el código anterior).
- **Verificado** con captura offscreen de la página de creación: «Influent OS»
  sale en negrita y no queda ningún asterisco ni comilla invertida en los
  subtítulos de las cinco páginas.
- **Sin cambios de motor:** sólo cambia cómo se dibuja un texto ya existente.

## 2026-11-28 — octogésimo ciclo

### Corregido — la vigilancia de parches sólo consultaba al arrancar (R-4a9d1c63)

Bug encontrado en la auditoría interna de este ciclo, sobre la primera etapa de
Q-013 entregada en el ciclo 79. No hay reporte externo.

- **Síntoma.** La promesa del ajuste es avisar «en segundo plano» de commits y
  parches nuevos, y el intervalo declarado son 6 horas. En la práctica la
  consulta ocurría **una sola vez**, al construir la ventana; después sólo se
  repetía si el usuario pulsaba «Comprobar ahora». Una ventana abierta todo el
  día nunca volvía a mirar el repositorio.
- **Causa raíz.** `_start_patch_watch()` tenía exactamente dos llamadas —
  `PackageTodoGUI.__init__` y `_check_patches_now()`— y no existía ningún
  `QTimer` que la repitiese, así que `should_check()` y
  `DEFAULT_INTERVAL_HOURS = 6` sólo se evaluaban al arrancar.
- **Solución.** `lib/patch_watch.py` expone `CHECK_TICK_SECONDS = 600` (cada
  cuánto reconsulta la ventana, distinto del intervalo de 6 h) y
  `PackageTodoGUI._install_patch_timer()` crea un `QTimer` hijo de la ventana
  que llama a `_start_patch_watch()` en cada tick. Ese método sigue aplicando
  el ajuste del usuario, el modo red «uso medido» y el intervalo de 6 h, y no
  abre un segundo hilo si el anterior sigue vivo: el temporizador no cambia
  cuándo se consulta, sólo asegura que se vuelva a evaluar.
- **Pruebas.** `tests/test_patch_watch.py::StateTests::test_tick_is_shorter_than_the_check_interval`
  y `tests/test_patch_watch_ui.py::test_watch_rechecks_on_a_timer_without_user_action`
  (las dos fallan antes del arreglo).
- **Verificado** en la ventana real (offscreen): `_patch_timer` activo con
  `600000` ms; con `last_check` de hace 7 h el tick produce una consulta; con
  el ajuste «Avisar de parches y commits nuevos» apagado no consulta.
- **Sin cambios de motor:** no se toca la ley de nombres, el formato `.iflapp`,
  las plantillas ni el contenido de los paquetes, y no se descarga nada.

### Aplicado — el splash vive dentro de la ventana principal, estilo UWP (Q-032 / R-5c9a3e17, issue #15)

Aprobación del propietario en `CONFIRM.MD` (commit `0addecb`, autoría
verificada con la API de GitHub), que pedía en el issue #15 «un uwp tiene su
splash dentro de la misma ventana y detras de el dibuja la interfaz y luego
corre todo normal». El splash deja de ser una ventana propia a pantalla
completa y pasa a ser un overlay hijo de la ventana principal.

- **`lib/splash_window.py`.** `IntegratedSplash` gana el modo overlay: con
  padre **no** es ventana (ni `FramelessWindowHint` ni `WindowStaysOnTopHint`)
  y es **opaco** —sin `WA_TranslucentBackground`, que en Windows creaba
  ventanas nativas auxiliares y anulaba el fondo QSS—, con
  `WA_StyledBackground` en el overlay y en su contenedor. Cubre el rectángulo
  del anfitrión y sigue sus redimensionados con un filtro de eventos (el
  contenedor se sincroniza también al cambiar la geometría porque un widget
  oculto no recibe `resizeEvent` hasta mostrarse).
- **Fundido correcto en un hijo.** `windowOpacity` no tiene efecto sobre un
  widget hijo, así que el desvanecido va por un `QGraphicsOpacityEffect`
  animado sobre la propiedad `opacity`; el cierre ya no llama a `destroy()`
  sobre un hijo —borraba el objeto C++ y el siguiente acceso lanzaba
  `RuntimeError: wrapped C/C++ object of type IntegratedSplash has been
  deleted`—, sólo oculta, retira el efecto y encola `deleteLater()`.
- **`packagemaker.py` (`main`).** La verificación de errores internos pasa a
  ejecutarse **antes** de crear la ventana, de modo que un fallo de arranque se
  reporta sin dejar un marco vacío (el riesgo que advertía la ficha). Después
  se construye `PackageTodoGUI`, se crea el splash como hijo de
  `main_window.content_container` y se muestra la ventana; el primer fotograma
  ya trae el marco y el tamaño finales, la interfaz queda detrás y la cortina
  se retira sin abrir ni cerrar ninguna ventana adicional. La titlebar queda
  visible. El modo de nivel superior se conserva para el splash suelto del
  `updater.py`.
- **Pacing intacto (Q-027).** `SplashWaiter` sigue retrasando el cierre hasta
  el mínimo calculado y el reporte de tirones se encola igual que antes.
- **Verificación.** Captura offscreen de la ventana real: el centro del área de
  contenido sale con el acento exacto `(0, 120, 212)` y la titlebar conserva su
  propio píxel, es decir, el splash no tapa el marco. Arranque real por
  subproceso: una sola ventana, splash hijo de `content_container`, visible al
  mostrarse y salida 0.
- **Pruebas.** `tests/test_splash_top_level.py` reescrito (13 casos): overlay
  hijo opaco, geometría y redimensionado, orden z, fundido por efecto gráfico,
  cierre sin destruir el objeto, modo de nivel superior intacto y coreografía
  de `main` (incluido que el error de arranque se reporte antes de crear la
  ventana). Suite completa en verde y `pyflakes` limpio.
- **Sin cambios de motor:** no se toca compilación, empaquetado ni blindaje.
- **Riesgo residual declarado.** La ventana se construye entera antes de su
  primer `show` (0,44 s medidos en offscreen; más en un equipo lento), así que
  durante esa construcción no hay ningún fotograma visible: el primer
  fotograma de la ventana ya trae el splash, que es lo que pide el patrón UWP,
  pero no hay realimentación visual antes de que la ventana exista. Separar la
  construcción en armazón y contenido —mostrar el armazón con el splash y
  construir el contenido detrás— es el siguiente paso si el retardo se nota en
  Windows; exige su propio ciclo por el riesgo que tiene en el arranque.

## 2026-11-27 — septuagésimo noveno ciclo

### Aplicado en parte — vigilancia de parches y commits nuevos (Q-013 / F-006, etapa 1)

Aprobación Q-013 del propietario, que pidió en su último reporte que
«updater.py notificara en segundo plano estando compilado o no sobre nuevos
commits y parches de seguridad». Esta etapa es **sólo de lectura**: avisa, no
descarga, no compila y no reemplaza ningún archivo.

- **`lib/patch_watch.py` (nuevo, sólo biblioteca estándar).**
  `fetch_latest_commit()` hace un `GET` anónimo a
  `api.github.com/repos/JesusQuijada34/packagemaker/commits/main` —sin token y
  sin datos del usuario— y `check_for_patch()` devuelve uno de seis estados:
  `up_to_date`, `available`, `unknown` (no se pudo determinar el commit local),
  `offline`, `metered` y `disabled`. `local_commit()` usa la marca
  `applied_commit` de `data/patch_state.json` y, si no existe, lee `HEAD` de
  `.git` sin lanzar `git` (referencia suelta, `packed-refs` y HEAD separado).
  El estado se escribe tolerando una instalación de sólo lectura.
- **Sin bloquear la interfaz.** La consulta corre en un hilo daemon y el
  resultado vuelve por la señal `patchChecked` (conexión en cola). Un fallo de
  red, un `HTTPError` o una respuesta ilegible se convierten en `offline`: la
  interfaz nunca recibe una excepción. Se comprueba al arrancar cada 6 horas,
  se salta en modo red «uso medido» y se apaga con `PM_PATCH_CHECK=0`.
- **Configuración → Notificaciones.** Casilla «Avisar de parches y commits
  nuevos» (`patch_check_enabled`, activada por defecto), botón «Comprobar
  ahora» y una línea con el resultado. El aviso también aparece en la barra de
  estado y, cuando hay parche, como notificación nativa si el usuario las tiene
  activas. El estado se recompone al cambiar de idioma.
- **Traducciones.** Diez claves nuevas (`config.patch_check`,
  `config.patch_check_hint` y `updates.*`) en los 14 catálogos, con
  `tools/translations_updates.py` y el generador `tools/generate_lang_files.py`
  actualizados.
- **Privacidad.** `docs/privacy.md` documenta la consulta: un `GET` a
  `api.github.com`, sin token, sin datos del proyecto y sin nada del usuario, y
  cómo desactivarla.
- **Pruebas.** `tests/test_patch_watch.py` (21, sin red: `opener` falso) y
  `tests/test_patch_watch_ui.py` (9, ventana real con la consulta sustituida).
  `tests/conftest.py` apaga la vigilancia para toda la suite, así que ninguna
  prueba sale del equipo.
- **Verificado** con la consulta real: el commit local (`52e9c89`) coincide con
  el último de `main`, estado `up_to_date`, y el estado queda en
  `data/patch_state.json` (ignorado por git).
- **Pendiente (etapa 2).** Descargar y aplicar el parche con verificación de
  integridad y reinicio controlado, y marcar el commit en los paquetes
  compilados para que también ellos puedan comparar. Forma parte de F-006, ya
  confirmada: no requiere una aprobación nueva.
- **Sin cambios de motor en compilación, empaquetado ni blindaje:** no se toca
  la ley de nombres, el formato `.iflapp` ni el contenido de los paquetes.

### Documentación — la cola de trabajo queda al día

- **Q-029 (AIDE como chatbot, issue #14)** figuraba como pendiente, pero el
  asistente ya existe desde el ciclo 56: dos proveedores (Copilot y endpoint
  compatible con OpenAI), clave propia, contexto saneado y respuesta desde un
  hilo daemon. Sólo falta trasladar los campos del endpoint a Configuración;
  se anota así en `bugs.md` y `CONFIRM.MD` en vez de darla por implementada.
- **Q-014 (eventos y temas de temporada)** está aprobada, pero el propietario
  la aplaza en `bugs.txt` hasta tener «un release estable funcionando» sin
  reportes. Se deja constancia y no se implementa.
- Se corrige el recuento de la cola (`bugs.md` decía 11 entradas y la tabla
  suma 10).

### Verificación

- Suite completa: **1511 pruebas pasan**, 1 omitida y 64 subtests
  (`QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`, 240 s).
- `python -m pyflakes` limpio en todo el árbol; `python -m py_compile` sin
  errores.
- Consulta real contra GitHub: `up_to_date` con el commit `52e9c89`.
- Sin cambios de comportamiento del engine: no se toca la ley de nombres, el
  formato `.iflapp`, las plantillas ni el contenido de los paquetes.

## 2026-11-27 — septuagésimo octavo ciclo

### Aplicado — perfil de GitHub como extensión y orden del sidebar (Q-030 / R-6f1c8e35)

Aprobación Q-030 del issue #14 (JesusQuijada34): la tarjeta de cuenta dejó de
ocupar el hueco entre MoonFix y las herramientas, el perfil pasa a ser una
extensión propia y su inicio de sesión se traslada a Configuración.

- **Orden del sidebar:** las extensiones (`section: tools`) van justo debajo de
  las páginas de trabajo y antes del hueco elástico; «Acerca de» sigue al pie.
  La tarjeta de identidad ya no se inserta en el sidebar, así que la fila queda
  create, build, config, moonfix, report, help, aide, **perfil**, about.
- **Página nueva `lib/profile_page.py`:** barra de acciones propia con
  «Actualizar», tarjeta de identidad (avatar de 72 px, nombre, `@login`,
  descripción, repositorios/seguidores/seguidos), la tarjeta de cuenta existente
  y la lista de repositorios con botón «Abrir» por cada uno. Estado de invitado
  con el botón de acceso cuando no hay sesión.
- **Sin bloquear la interfaz:** los repositorios se piden en un `QThread` al
  entrar por primera vez en la página o al pulsar «Actualizar»; la barra de
  acciones muestra su marquee mientras dura la petición y los errores se
  escriben en la propia tarjeta, no en un diálogo modal.
- **Identidad:** `github_identity.fetch_repositories()` usa `/user/repos` con
  token (incluye los privados) y `/users/<login>/repos` sin él, y devuelve sólo
  los campos que pinta el perfil (nombre, descripción, URL, lenguaje, privado y
  fecha). `fetch_profile()` guarda `bio`, `public_repos`, `followers` y
  `following` en `GitHubProfile.extras`.
- **Configuración → Cuenta:** tarjeta nueva con el estado de la sesión
  («Conectado como @login» o «Sin sesión»), inicio y cierre de sesión delegados
  al anfitrión y el aviso de que el perfil completo está en la extensión.
  `_refresh_github_card()` refresca a la vez la tarjeta, la página y la tarjeta
  de Configuración, así que iniciar o cerrar sesión se ve en los tres sitios.
- **Navegación:** el botón «ver perfil» de la tarjeta abre la página Perfil (con
  el diálogo clásico como respaldo si la extensión no está cargada).
- **Traducciones:** claves `sidebar.profile`, `sidebar_desc.9`, `profile.*` y
  `config.section_account*`/`config.account_*` en los 14 catálogos de `lang/` y
  en `tools/translations_curated.py`. `config.section_account` y
  `profile.repositories` se añaden a los cognados aceptados de
  `tests/test_i18n_curated.py` («Account» en italiano y neerlandés,
  «Repositories» en neerlandés).
- **Pruebas:** `tests/test_profile_page.py` (endpoint con y sin token, mapeo de
  campos, sesión ausente, carga real del perfil, invitado, pintado de perfil y
  repositorios, error de red, hilo de descarga, retraducción, manifiesto de la
  extensión, orden del sidebar y construcción de la ventana con la tarjeta de
  cuenta). Se actualizan las listas de ids del sidebar en
  `tests/test_addons_engine.py`, `tests/test_addons_install.py`,
  `tests/test_auto_author_and_sidebar.py` y la comprobación del modo contraído
  en `tests/test_design_system_phase3.py`.
- **Verificación:** suite completa en verde (1481 pruebas, 1 omitida, 64
  subtests) y `pyflakes` limpio. Ventana real (offscreen): el sidebar queda
  create, build, config, moonfix, report, help, aide, perfil, about, la tarjeta
  de cuenta cuelga de la página Perfil y Configuración lista las tarjetas
  general, cuenta, idioma, apariencia, notificaciones, tipografías, red,
  privacidad, extensiones y restablecer.
- **Sin cambios de motor:** no se toca compilación, empaquetado ni blindaje.

## 2026-11-27 — septuagésimo séptimo ciclo

### Aplicado — instalar extensiones `.yaml` desde Configuración (Q-022 / R-2c8d4f71)

Segunda mitad de la aprobación Q-022 del issue #11 («las extensiones del
sidebar pueden ir por sistema en `lib/addons/`» y poder instalarlas desde la
aplicación). La primera mitad (manifiestos en `lib/addons/`) se aplicó en el
ciclo 76.

- **Motor:** nuevos `USER_ADDONS_DIR`, `user_addons_dir()`, `all_addons_dirs()`,
  `installed_addons()` e `install_addon()` en `lib/addons_engine.py`. El
  directorio de usuario (`data/addons/`, o `PM_USER_ADDONS_DIR`) se carga
  **después** de `lib/addons/` y de `addons/`, así que una extensión instalada
  nunca suplanta una página base.
- **Validación previa:** `install_addon()` reutiliza `parse_manifest()` —la
  misma puerta que el cargador— y además rechaza los ids de addons incluidos,
  los manifiestos desactivados (`enabled: false`), un `builder` que el
  anfitrión no tenga y los manifiestos con `plugin` suelto: ese `.py` viajaría
  junto al YAML y se ejecutaría al arrancar, que es el alcance de Q-031
  (extensiones empaquetadas con lista de confianza y firma). `class` debe ser
  `modulo:Clase` y no se importa durante la validación.
- **Copia atómica:** se escribe un temporal en el directorio destino y se
  sustituye con `os.replace()`; un fallo deja intacto el manifiesto anterior y
  no quedan ficheros temporales.
- **Interfaz:** nueva tarjeta **Configuración → Extensiones** con el botón
  «Instalar extensión…», la lista de extensiones instaladas, el resultado de la
  operación y un aviso sobre las extensiones con `class`. La tarjeta se
  retraduce al cambiar de idioma.
- **Consumidores:** `packagemaker.py` (`ADDONS_DIRS = all_addons_dirs()`) y el
  CLI `--list-addons` cargan también `data/addons/`.
- **Traducciones:** claves `config.section_addons`, `config.section_addons_hint`
  y `config.addons_install/installed/none/ok/error/warning` en los 14 catálogos
  de `lang/` y en `tools/translations_curated.py`.
- **Pruebas:** `tests/test_addons_install.py` (copia válida, sin temporales,
  reinstalación, ids incluidos, `builder` inexistente, `class`, `plugin`,
  desactivado, YAML inválido, extensión distinta de `.yaml`, directorio de
  usuario y respaldo integrado) y `tests/test_addons_settings_ui.py` (tarjeta
  registrada, instalación correcta, error visible sin copiar y cancelación).
- **Verificación:** la ventana real (offscreen) arranca con el sidebar
  create, build, config, moonfix, report, help, aide, extra, about y la tarjeta
  muestra «Instaladas: extra»; `--list-addons` sigue listando los 8 addons
  incluidos.
- **Reporte:** JesusQuijada34 (issue #11). Sin cambios de comportamiento del
  engine, del formato `.iflapp` ni del nombre canónico.

### Suite

1466 pasan, 1 omitida, 64 subtests; `pyflakes` limpio. No se prepara
release: siguen pendientes los cambios de engine aprobados y R-7f2b9c41
espera la decisión de Q-034.

## 2026-11-27 — septuagésimo sexto ciclo

### Aplicado en parte — addons en `lib/addons/` (Q-022 / R-2c8d4f71)

Los manifiestos del sidebar se trasladan de `addons/` (raíz) a `lib/addons/`,
la ubicación que pidió el propietario en el issue #11 («las extensiones del
sidebar pueden ir por sistema en `lib/addons/`»), conservando `addons/` como
ruta de compatibilidad.

- **Resolución:** nuevos `SHIPPED_ADDONS_DIR`, `LEGACY_ADDONS_DIR`,
  `shipped_addons_dirs()` y `load_addons_from_dirs()` en
  `lib/addons_engine.py`. Se combinan los directorios existentes; el primero
  gana por `id`, así que `lib/addons/` manda y `addons/` sólo aporta lo que
  falte (bundles antiguos). Si no hay ninguno, se mantiene el respaldo
  integrado `DEFAULT_ADDONS`.
- **Consumidores:** `packagemaker.py` (`ADDONS_DIRS` +
  `load_addons_from_dirs`) y el CLI `--list-addons` usan el resolutor; la
  ayuda del CLI apunta a `lib/addons/*.yaml`.
- **Pruebas:** `tests/test_addons_engine.py` valida la nueva ubicación y añade
  `ShippedDirsTest` (precedencia entre directorios, sin ids duplicados,
  directorios ausentes ignorados y respaldo integrado);
  `tests/test_help_page.py` lee de `lib/addons/`.
- **Pendiente:** instalar un addon `.yaml` desde Configuración con validación
  previa (segunda mitad de Q-022). Requiere UI nueva y claves en los 14
  catálogos de `lang/`; se hará en un ciclo propio para no mezclar el cambio
  de rutas con una función de interfaz.
- **Reporte:** JesusQuijada34 (issue #11). Sin cambios de comportamiento del
  engine ni del formato de paquetes.

### Suite

1444 pasan, 2 omitidas, 64 subtests; `pyflakes` limpio. No se prepara release:
siguen pendientes los cambios de engine aprobados y R-7f2b9c41 espera Q-034.

## 2026-11-27 — septuagésimo quinto ciclo

### Corregido — el sidebar nunca pintaba su fondo QSS (R-8f4b2d61)

Encontrado por la auditoría interna al aplicar **Q-026** (R-5a7d2f16). El
sidebar se creaba con `WA_TranslucentBackground`, que activa
`WA_NoSystemBackground` y **anula el fondo QSS** del widget: la regla
`QWidget#NavigationSidebar { background: … }` se aplicaba pero no se pintaba,
así que el panel quedaba transparente y el blanco translúcido que pidió el
propietario en el issue #11 nunca llegaba a verse.

- **Tokens:** `SIDEBAR_BG` pasa a `rgba(28, 28, 30, 0.45)` y se añade
  `SIDEBAR_BG_LIGHT = "rgba(255, 255, 255, 0.45)"` (alfa dentro del 0,3–0,5
  pedido). El sidebar invierte su color con el tema.
- **QSS:** los roles `sidebar-light` y `sidebar-frame-light` de
  `source/qss/qwidget.qss` usan `__SIDEBAR_BG_LIGHT__` en vez del literal
  `rgba(242,242,247,.9)`; `sidebar_qss()`, `sidebar_stylesheet()` y `applyget()`
  resuelven el token por tema.
- **Widget:** el sidebar se construye con `WA_StyledBackground` y sin
  `WA_TranslucentBackground`; la transparencia la aporta el alfa del token.
- **Verificación:** capturas offscreen: sidebar `(255,255,255,α)` en tema claro
  y `(29,29,29,α)` en oscuro, con el texto gris legible. El panel de páginas
  sigue oscuro y su texto no cambia (ver más abajo).
- **Pruebas:** `tests/test_theme_surfaces.py` (6 casos: alfa pedido, inversión
  por tema, QSS sin literal claro, `applyget` por tema, guarda contra
  `WA_TranslucentBackground` y pintado real del sidebar en ambos temas).
- **Reporte:** auditoría interna de mantenimiento (ciclo 75); no hay reporte
  externo.

### Aplicado en parte — sidebar translúcido de Q-026 (R-5a7d2f16)

La mitad del sidebar de **Q-026** queda implementada con el arreglo anterior.
La otra mitad —invertir la superficie de las pestañas y pasar su texto a gris
claro/oscuro— **no se aplica todavía**: las páginas llevan ~40 estilos con
`color:white` en `lib/fluent_theme.py`, así que una superficie clara deja el
título, las etiquetas y la descripción invisibles (comprobado con una captura
offscreen). El alcance se pregunta en **Q-036** de `CONFIRM.MD`.

### Suite

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: **1441 pasan**,
  1 omitida, 64 subtests.
- `python -m pyflakes $(git ls-files '*.py')`: limpio.
- `python -m py_compile $(git ls-files '*.py')`: correcto.
- Commit del código: `804c50c`.

## 2026-11-27 — septuagésimo cuarto ciclo

### Implementado — página de ayuda global con buscador (R-7b3e9a52 / Q-021)

Solicitado por JesusQuijada34 (issue #11, 2026-11-25): «un apartado de ayuda
relacionado con toda la app», no una ayuda por página. Aprobado como **Q-021**
(commit `73dcdcd`, autoría verificada). Prioridad media; es una página nueva y
no toca el comportamiento del engine.

- **Qué se añade:** el addon `help` (`addons/help.yaml`, sección `tools`,
  `order: 15`) coloca «Ayuda» en el sidebar entre Reportes y AIDE. La página
  (`lib/help_page.py`) tiene barra de acciones propia, buscador y cuatro temas
  —crear, compilar, blindar y reportar— con el texto real de cada área.
- **Buscador:** filtra en vivo por título y cuerpo, sin distinguir mayúsculas;
  cuando no queda ningún tema muestra un aviso en vez de una página vacía.
- **Textos:** `help.intro`, `help.search_placeholder`, `help.empty` y
  `help.topics.<tema>.{title,body}` en los **14** catálogos de `lang/`, más
  `sidebar.help` y `sidebar_desc.8`. `retranslate()` reaplica todo al cambiar
  de idioma desde `apply_ui_language()`.
- **Icono:** `help` en `lib/app_icons.py` (mismo gris de sidebar que el resto)
  y en `TAB_ICON_KEYS`.
- **Respaldo:** `DEFAULT_ADDONS` de `lib/addons_engine.py` incluye el addon, de
  modo que un bundle sin `addons/` sigue abriendo con la página.
- **Verificación:** ventana real en offscreen: sidebar `create, build, config,
  moonfix, report, help, aide, about`, subtítulo tomado del manifiesto y la
  búsqueda «upx» deja sólo el tema de blindaje.
- **Pruebas:** `tests/test_help_page.py` (manifiesto, icono, claves en los 14
  catálogos, temas, filtro, estado vacío y retraducción). Se actualizan las
  listas de addons de `tests/test_addons_engine.py` y
  `tests/test_auto_author_and_sidebar.py`.
- **Suite:** 1435 pasan, 1 omitida, 64 subtests; `pyflakes` limpio.

## 2026-11-27 — septuagésimo tercer ciclo

### Implementado — duración mínima del splash y reporte de tirones del arranque (R-7b2c9e51 / Q-027)

Reportado por JesusQuijada34 (issue #13, 2026-11-26): «se abren primero 5
ventanas gui python vacías y pequeñas» y tirones al arrancar. Las ventanas
vacías ya se corrigieron en R-6c4d1f87; esta entrega cubre lo que faltaba:
que el splash no se retire hasta que la interfaz esté dibujada y que los
tirones reales se reporten con datos. Prioridad alta; aprobado como **Q-027**
(commit `73dcdcd`, nota «perfecto»).

- **Comportamiento anterior:** el splash se cerraba en cuanto la compuerta de
  sesión decidía, sin espera mínima, y no se medía ninguna fase del arranque.
  Un equipo lento veía el primer fotograma de la interfaz a medio pintar y no
  quedaba rastro de qué había tardado.
- **Solución** (`lib/startup_timing.py`, nuevo; sin Qt):
  - `minimum_splash_seconds()` parte de **5 s** y suma hasta **1 s** según los
    puntos de rendimiento (`performance_points()`: uno por cada 4 GB de RAM y
    uno por cada 4 núcleos, con tope de 8), redondeado a múltiplos de 0,25 s.
    En este equipo (16 GB, 4 núcleos) da **5,50 s**.
  - `StartupTimeline` mide cada tramo del arranque (`estilos`, `fuente`,
    `idioma`, `splash_visible`, `verificacion`, `ventana`, `idioma_ui`, `show`,
    `compuerta`) y sólo cuenta hasta la decisión de la compuerta: la espera
    deliberada del splash no se confunde con un tirón.
  - `SplashWaiter` retrasa el cierre con `QTimer.singleShot` (sin bloquear el
    bucle de eventos) y guarda `ready_seconds`, el tiempo real de arranque.
    Sin planificador, o con mínimo 0, cierra de inmediato.
  - `startup_lag_report()` arma la entrada `StartupLag` si una fase supera
    **0,5 s** o si la interfaz no estuvo lista dentro del mínimo. El cuerpo
    lleva las fases más lentas, el mínimo esperado, el tiempo real y los
    errores restantes del arranque.
- **Cableado** (`packagemaker.py`): marcas de tiempo en el arranque de la GUI y
  `close_splash()` pasa por `SplashWaiter`; al cerrar, `report_startup_lags()`
  encola el reporte **sólo** si el envío automático está activo (mismo ajuste
  que la captura de fallos) y no repite una huella ya enviada o en cola. La
  entrada se reintenta desde la página de Reportes, nunca se envía durante el
  arranque.
- **Desarrollo y pruebas:** `PM_SPLASH_MIN_SECONDS` acorta o anula la espera.
- **Verificación real:** arranque completo en offscreen con la instrumentación
  activa: mínimo calculado **5,50 s**, `splash.finish()` a los **5,61 s** y
  cola de reportes vacía (arranque sano). Forzando `PM_SPLASH_MIN_SECONDS=0.05`
  aparece en la cola la entrada `[auto] Arranque lento…` con
  `Interfaz lista en: 0,59 s` y las fases medidas (`ventana` 0,37 s,
  `idioma_ui` 0,17 s).
- **Pruebas nuevas:** `tests/test_startup_timing.py` (30 casos): puntos de
  rendimiento, mínimo acotado y redondeado, sobrescritura por entorno,
  cronómetro por fases, compuerta temporal (no cierra antes del mínimo, cierra
  al cumplirlo, cierre inmediato sin planificador), contenido y huella del
  reporte, opt-in desactivado, deduplicación, y que el splash real no se cierra
  antes del mínimo con un `QTimer` de verdad.
- **Riesgo:** el arranque tarda al menos 5 s incluso en equipos rápidos, como
  pidió el propietario. R-7b2c9e51 queda en observación.

## 2026-11-27 — septuagésimo segundo ciclo

### Implementado — compilación en un entorno aislado por proyecto (R-4d9e2b61 / Q-019)

Reportado por JesusQuijada34 (`bugs.txt`, commit `bba72d6`, 2026-11-25): «nada
tiene el entorno aislado». Prioridad alta; aprobado como **Q-019** (commit
`73dcdcd`) con la instrucción de añadir un interruptor **Red** en Configuración.

- **Comportamiento anterior:** el build ejecutaba Nuitka o PyInstaller
  «embebidos» dentro del propio proceso de PackageMaker, con los módulos del
  intérprete anfitrión. El registro decía «embebido» y el proyecto no tenía
  entorno propio, así que una dependencia distinta a la del sistema no se podía
  compilar.
- **Solución** (`lib/blindcubeEngine/build_sandbox.py`, nuevo):
  - `plan_sandbox()` describe el entorno:
    `<proyecto>/build/pm-sandbox/<backend>/venv`. Vive bajo `build/`, que el
    empaquetado ya excluye, así que nunca entra en el `.iflapp`.
  - `BuildSandbox.prepare()` crea el venv con el intérprete del sistema,
    instala las dependencias del proyecto (`requirements.txt`) y las del
    backend (`nuitka`, `ordered-set`, `zstandard`; `pyinstaller`), deja una
    marca con el conjunto instalado para no repetir la descarga y comprueba que
    el backend se importa **dentro** del entorno.
  - `BuildSandbox.compile()` ejecuta `python -m nuitka` o
    `python -m PyInstaller` como subproceso en ese intérprete y devuelve el
    binario, que `_compile_binary` copia a `dist` como antes.
  - `wrap_backend()` envuelve el backend resuelto (`IsolatedBackend`) y lo usan
    `FlangCompiler._ensure_compiler()` y `iflapp_ide.compile_project()`. Si el
    venv no se puede crear, `pip` falla o la compilación aislada devuelve error,
    se registra el motivo y se reintenta con el backend embebido: el build
    nunca se queda sin salida.
  - El plugin `pyqt6` de Nuitka sólo se pide si el venv declara PyQt6 entre sus
    requisitos (el constructor embebido lo decidía por el entorno del proceso,
    lo que abortaba la compilación en un venv sin Qt).
  - Si Nuitka aborta por falta de `patchelf` en `--onefile` (Linux), el error
    incluye la indicación `sudo apt install patchelf`.
- **Interruptor Red (nota del propietario en Q-019):** nueva tarjeta
  **Configuración → Red**, con la preferencia `network_mode` en `data/pm.data`:
  - *Sin restricción*: entorno aislado por proyecto (valor por defecto).
  - *Uso medido*: no descarga nada; compila con el backend embebido y avisa de
    que hace falta Python instalado en el sistema y de que, sin conexión, las
    dependencias deben estar ya instaladas.
  Traducida en los 14 catálogos de `lang/`.
- **Pruebas:** `tests/test_build_sandbox.py` (18 casos: plan, modo de red,
  preparación con `runner` falso, reutilización de la marca, filtrado del plugin
  Qt, argumentos de PyInstaller, caída al backend embebido y envoltura desde
  `FlangCompiler`) y cuatro casos nuevos en
  `tests/test_settings_navigation_bar.py` (tarjeta Red, guardado en `pm.data` y
  retraducción). `tests/conftest.py` desactiva el aislamiento durante la suite
  (`PM_BUILD_ISOLATION=0`) para no crear venvs reales en cada build de prueba.
- **Verificación real:** dos builds completos con el sandbox de verdad en esta
  máquina — PyInstaller (10,9 s) y Nuitka (60,5 s) —; en ambos casos el binario
  producido se ejecutó y escribió su salida. Suite: 1398 pasan, 1 omitida, 64
  subtests; `pyflakes` y `py_compile` limpios.
- **Commit:** `fc24df3` en `main`.

## 2026-11-27 — septuagésimo primer ciclo

### Corregido — las cuatro ventanas del updater morían al construirse (R-6b4d2f81)

Encontrado por la auditoría interna de este ciclo al reproducir R-3a9c6e28; no
hay reporte externo. Prioridad alta: la actualización con interfaz nunca llegaba
a abrirse.

- **Síntoma:** al abrir la ventana del updater con PyQt6 instalado, el proceso
  moría en el constructor. Reproducción en offscreen:
  `AttributeError: type object 'Qt' has no attribute 'WindowFlags'`.
- **Causa raíz:** `lib/coreUpdater/windows.py` acumulaba cuatro usos de API que
  no existen:
  1. `Qt.WindowFlags(Qt.WindowType.Dialog | ...)`: en PyQt6 el tipo de las
     banderas es el propio `Qt.WindowType`; `Qt.WindowFlags` no existe.
  2. `CustomTitleBar(self, title=..., is_main=True)`: la clase de
     `leviathan_ui` (vendorizada y de PyPI) acepta
     `parent, title, icon, hide_max, back_callback`, no `is_main`.
  3. `self.title_bar.set_color(QColor(0,0,0,0))`: el método no existe; la
     propia titlebar ya nace con fondo transparente.
  4. `self.pbar.setValue(...)` sobre `LeviathanProgressBar`, que expone
     `value` como propiedad y no tiene `setValue`.
  Las cuatro ventanas (`ModernUpdaterWindow`, `IFLAPPInstallerWindow`,
  `LicenseTermsDialog` y `EXEInstallerWindow`) tenían los tres primeros
  defectos y las dos de instalación también el cuarto.
- **Solución** (`lib/coreUpdater/windows.py`):
  - las banderas se pasan directamente (`Qt.WindowType.Dialog |
    Qt.WindowType.FramelessWindowHint`);
  - `CustomTitleBar` se construye sólo con `parent` y `title`;
  - se retira la llamada a `set_color` y el import de `QColor`, ya sin uso;
  - se añade el parche de compatibilidad que ya usaba `packagemaker.py`:
    si `LeviathanProgressBar` no tiene `setValue`, se le asigna uno que
    escribe en la propiedad `value`.
- **Pruebas:** `tests/test_updater_windows_construct.py` construye las cuatro
  ventanas con Qt real en offscreen y comprueba que son frameless; los cuatro
  casos fallan con el código anterior.
- **Verificación:** 1376 pruebas pasan, 1 omitida, 64 subtests; `pyflakes` y
  `py_compile` limpios. Con Qt real la ventana del updater se muestra y vive en
  el hilo de la interfaz.
- **Commit:** `70cf903` en `main`.

### Corregido — el updater de plantilla crea la interfaz en el hilo principal (R-3a9c6e28)

Reportado por la auditoría interna del ciclo 70 (2026-11-27).

- **Síntoma:** en el modo vigilancia (`updater.py` sin argumentos) la
  `QApplication` y la ventana de instalación se construían dentro del hilo que
  consulta GitHub. Qt exige que la interfaz viva en el hilo principal; en
  Windows puede abortar el proceso o dejar la ventana sin pintar.
- **Causa raíz:** `ciclo_embestido()` lanzaba `verificar()` en un hilo y era
  `verificar()` quien hacía `QApplication(sys.argv)` y `app.exec()`.
- **Solución** (`src/templates/project/updater.py.template`):
  - `verificar()` hace una sola pasada y devuelve `(datos, url)` o `None`; no
    crea la aplicación.
  - `UpdateWatcher` (un `QObject` con `pyqtSignal`) consulta GitHub en un hilo
    y emite `encontrada(datos, url)`; la conexión encolada ejecuta el slot en el
    hilo de la interfaz.
  - `ciclo_embestido(app)` conecta ese slot, que crea la ventana con
    `WA_DeleteOnClose` y cierra la aplicación al destruirse.
  - `main()` crea la `QApplication` en el hilo principal y termina con
    `app.exec()`, en lugar del `while True: time.sleep(100)` anterior.
  - La plantilla también recibe el arreglo de titlebar y barra de progreso de
    R-6b4d2f81, porque copiaba el mismo código defectuoso.
- **Pruebas:** `tests/test_template_updater_gui_thread.py` carga la plantilla
  real con un PyQt6 falso que anota el hilo de cada construcción: comprueba que
  la `QApplication` sólo se crea en el hilo principal, que la ventana se
  construye en él y que `verificar()` no crea la aplicación.
- **Verificación:** con Qt real y offscreen, `ciclo_embestido(app)` abre la
  ventana y `w.thread() is app.thread()` es `True`.
- **Commit:** `70cf903` en `main`.

## 2026-11-27 — septuagésimo ciclo

### Implementado — el `updater.py` de los proyectos nuevos ya tiene CLI (Q-017)

Aprobado por JesusQuijada34 en `CONFIRM.MD` (commit `73dcdcd`, autoría
verificada). No hay reporte externo: es la ficha **Q-017** de la cola de
cambios de engine de `bugs.md`.

- **Síntoma:** el `updater.py` que `create_project_from_templates()` copia a
  cada proyecto nuevo ignoraba los argumentos y no terminaba nunca.
  `python updater.py --check`, `--version` o `--install` se quedaban en
  `while True: time.sleep(100)` y había que matar el proceso.
- **Reproducción:** crear un proyecto con las plantillas y ejecutar
  `timeout 6 python updater.py --check` → código **124** (el proceso sigue
  vivo). Con `--version` y `--install`, lo mismo.
- **Causa raíz:** la plantilla sólo tenía el modo vigilancia (hilo en segundo
  plano más un bucle infinito en el `__main__`), sin `argparse` ni códigos de
  salida. El bucle interno de `verificar()` tampoco terminaba cuando no había
  PyQt6, así que el updater era inutilizable como herramienta de línea de
  órdenes y, sin interfaz, se quedaba colgado para siempre.
- **Solución** (`src/templates/project/updater.py.template`):
  - `main()` con `argparse`: `--check` (una pasada, `UPDATE_AVAILABLE`/
    `NO_UPDATE` con `TYPE` y `DOWNLOAD_URL`, código 0/1), `--install FILE`
    con `--target DIR`, `--silent` (actualización sin interfaz, código 0/1) y
    `--version`. `--accept-license` y `--no-cache` se aceptan por
    compatibilidad con la interfaz del updater de PackageMaker y se documentan
    como sin efecto en esta plantilla.
  - `check_update()` concentra la pasada de verificación que antes vivía dentro
    del bucle; la usan `--check`, `--silent` y la vigilancia.
  - `install_archive()` instala un paquete `.zip` sobre el destino (extracción
    en un directorio temporal, sin tocar el updater en ejecución) y devuelve
    `(ok, mensaje)`; `InstallerWorker` la reutiliza en lugar de duplicar la
    lógica de descompresión y sobrescritura.
  - `verificar()` hace **una** pasada y termina; sin PyQt6 registra un aviso
    claro y devuelve `False` en vez de esperar en bucle. `ciclo_embestido()`
    tampoco arranca el hilo de vigilancia sin interfaz.
  - La plantilla sigue usando sólo la biblioteca estándar más PyQt6/leviathan
    opcionales: se puede copiar a un proyecto sin arrastrar módulos de
    PackageMaker.
- **Pruebas:** `tests/test_template_updater_cli.py` (5 casos; los 5 fallan con
  la plantilla anterior, todos por `TimeoutExpired`): `--version` y `--check`
  terminan y reportan la actualización disponible con un `requests` falso
  (sin red), `NO_UPDATE` cuando las versiones coinciden, `--install` de un
  `.zip` reemplaza los archivos del proyecto, un contenedor que no es ZIP
  aborta con `ERROR:` y código 1, y sin PyQt6 y sin argumentos el proceso sale
  con código 1 en lugar de colgarse.
- **Verificación:** 1370 pruebas pasan, 1 omitida, 64 subtests; `pyflakes` y
  `py_compile` limpios.
- **Limitación conocida:** la plantilla sólo extrae `.zip`; las releases de
  PackageMaker son contenedores `.iflapp` v2 y no se pueden descomprimir con
  `zipfile`. Queda registrado como **R-7f2b9c41** y la decisión de cómo
  resolverlo (lector embebido, delegar o dejar sólo `.zip`) se pide en
  **Q-034** de `CONFIRM.MD`.
- **Commit:** `861d1ec` en `main`.

## 2026-11-27 — sexagésimo noveno ciclo

### Corregido — guardar ajustes ya no re-pule hojas de estilo idénticas (R-7c4a1e95)

Reportado por JesusQuijada34 en `bugs.txt` (commit `bba72d6`, 2026-11-25):
«al cambiar opciones de Configuración la interfaz se congela un momento
mientras se guardan y se aplican».

- **Síntoma:** cambiar una opción de apariencia en Configuración (por ejemplo
  el ancho del acento del sidebar) bloqueaba la ventana una fracción de
  segundo perceptible. Guardar una ruta o un aviso no se notaba.
- **Evidencia (offscreen, ventana real):** `PMDataStore.save()` tarda **0,5 ms**
  y un guardado que sólo cambia una ruta, **1,7 ms**: el guardado de archivos no
  era el culpable. Un guardado que cambia la apariencia tardaba **120 ms**.
  Perfilado: `apply_theme()` volvía a llamar a `setStyleSheet()` con la **misma**
  hoja en la página central (35 ms) y en otros widgets; Qt re-pule el árbol
  entero aunque no cambie un píxel.
- **Causa raíz:** `lib/fluent_theme.set_qss()` aplicaba siempre la hoja, sin
  comparar con la que el widget ya tenía. Reaplicar el tema tras guardar
  reinstalaba hojas idénticas en cada widget y cada una disparaba un
  `QEvent.StyleChange` en cascada.
- **Solución:** `set_qss()` es idempotente: resuelve la plantilla (incluido
  `append=True`), compara con `widget.styleSheet()` y **no** vuelve a llamar a
  `setStyleSheet()` si el resultado es idéntico. No cambia ningún color, radio
  ni texto: sólo evita el re-pulido que no produce cambios. Medido: el mismo
  guardado pasa de **120 ms a ~5 ms** y la página central ya no recibe ningún
  `StyleChange`.
- **Pruebas:** `tests/test_settings_save_repolish.py` (4 casos; 3 fallan con el
  código anterior): `set_qss` no repule una hoja idéntica, sí aplica una
  distinta, conserva la acumulación de `append` y un guardado que sólo cambia
  el ancho del acento no genera `StyleChange` en `central`; un cambio real de
  acento sigue repintando. Se actualizó
  `tests/test_settings_save_guards.py::test_path_only_save_does_not_repaint_theme`
  para comprobar el efecto (no se llama a `apply_theme`) en vez de medir el
  tiempo, porque reaplicar el mismo tema ahora es barato.
- **Verificación:** 1365 pruebas pasan, 1 omitida, 64 subtests; `pyflakes` y
  `py_compile` limpios.
- **Nota sobre Q-012:** mover el guardado a un hilo aparte no habría cambiado
  nada: la escritura son 0,5 ms. Lo que congelaba la interfaz era el re-pulido
  redundante, ya eliminado. Q-012 sigue pendiente sólo por la barra marquee
  permanente y las notificaciones nativas (PushBox), que son mejora visible y
  no un fallo de rendimiento.
- **Commit:** ver el commit de este ciclo en `main`.

## 2026-11-27 — sexagésimo octavo ciclo

### Corregido — `compile-only` no retiraba el fuente del paquete (R-3e7d1c58, Q-004/F-001)

Reportado por JesusQuijada34 (auditoría interna de mantenimiento) y aprobado en
**Q-004** (commit `bba72d6`) con la confirmación final **F-001** (commit
`73dcdcd`), opción A: `compile-only` debe retirar el `.py` del árbol del
paquete, salvo en builds `zipapp`.

- **Síntoma:** con el blindaje `compile-only` el paquete `.iflapp` seguía
  llevando los `.py` legibles del proyecto; el método sólo añadía un `.pyc` O2
  junto a cada fuente, así que la promesa «sin fuentes legibles» no se cumplía.
- **Causa raíz:** `hardening.compile_to_bytecode()` compilaba y devolvía el
  `.pyc`, pero nunca retiraba el `.py`; además `BuildThread.apply_hardening()`
  sólo compilaba el primer `.py` que encontraba con `rglob`.
- **Solución:**
  1. `compile_to_bytecode(script, *, remove_source=True)` retira el `.py`
     compilado. El `.pyc` queda en la ubicación clásica (junto al fuente), que
     Python importa sin el original; si el borrado falla, el informe lo dice en
     vez de dar el trabajo por bueno.
  2. `apply_all(..., remove_source=True)` compila **todos** los `.py` del árbol
     del paquete y retira sus fuentes, salvo `updater.py`, que pertenece al
     contrato de estructura obligatorio del paquete.
  3. `BuildThread.apply_hardening()` pasa `remove_source=False` cuando el
     backend es `zipapp`, que empaqueta módulos `.py` por definición.
  4. `apply_all()` ejecuta `compile-only` después de las transformaciones de
     fuente (`anti-debug`, `obfuscate`) y **antes** de `checksum`/`integrity`,
     para que los manifiestos describan el árbol final; los informes conservan
     el orden solicitado.
- **Pruebas:** `tests/test_hardening.py::CompileOnlySourceRemovalTests` (7
  casos): retirada por defecto, conservación con `remove_source=False`, árbol
  completo con `updater.py` intacto, backend `zipapp` frente a `nuitka` en
  `BuildThread.apply_hardening()` y manifiestos de digests coherentes con el
  árbol final. Con el código anterior fallan cinco de ellos.
- **Verificación:** 1361 pruebas pasan, 1 omitida, 64 subtests; `pyflakes` y
  `py_compile` limpios.
- **Commit:** ver el commit de este ciclo en `main`.

## 2026-11-26 — sexagésimo séptimo ciclo

### Corregido — maximizar o restaurar congelaba la interfaz (R-7d4b2c95, R-7c4a1e95)

Reportado por JesusQuijada34 en `bugs.txt` (commit `bba72d6`, 2026-11-25): «hay
mal renderizado al maximizar y restaurar, la interfaz se congela un momento» y
«al maximizar o restaurar o al cambiar opciones en configuración, ¿por qué se
queda congelado un rato?».

- **Síntoma:** cada maximizar o restaurar congelaba la ventana una fracción de
  segundo, y lo mismo al cambiar de modo de visualización en Configuración.
- **Causa raíz:** `toggle_frameless_maximize()` invocaba
  `_pm_reapply_display_mode`, que era `_apply_leviathan_and_personalization()` →
  `apply_theme()`. `apply_theme()` reinstala la hoja global con
  `QApplication.setStyleSheet(global_stylesheet(...))`, y Qt re-pule entonces
  todos los widgets de la aplicación. Medido en offscreen con la ventana real:
  **185 ms** sólo en `app.setStyleSheet`, **269 ms** en `apply_theme` y
  **274 ms** por gesto. En el gesto sólo cambia el radio de las esquinas.
- **Solución:**
  1. `PackageTodoGUI._refresh_window_corners()` sustituye al reaplicado
     completo en `_pm_reapply_display_mode`: refresca el radio del efecto
     (`apply_personalization_effects`), el QSS `packagemaker_010` de la ventana
     y el chrome de la titlebar. No reinstala la hoja global ni reconstruye el
     efecto `WipeWindow`. El gesto baja a **~59 ms**.
  2. `lib/fluent_theme.apply_global_stylesheet(app, accent, dark)` instala la
     hoja global sólo si cambió el acento o el tema; una hoja idéntica no se
     reinstala (ahorra ~185 ms al cambiar de modo de visualización o guardar
     ajustes que no tocan la paleta). `main` y `apply_theme` usan el helper.
  3. `_window_base_and_radius()` centraliza el fondo y el radio para que
     `apply_theme` y el refresco de esquinas no puedan divergir.
- **Pruebas:** `tests/test_maximize_without_theme_reapply.py` (2 casos): el
  gesto no llama a `apply_theme` ni a `QApplication.setStyleSheet`, el radio del
  QSS pasa a 0 al maximizar y vuelve a `WINDOW_RADIUS` al restaurar, y cambiar
  de modo de visualización no re-pule la aplicación. Con el código anterior el
  primero falla (1 llamada a `setStyleSheet` por gesto).
  `tests/test_design_system_phase3.py` añade el caso de caché del helper y sus
  dos aserciones de cableado apuntan ya a `apply_global_stylesheet`.
- **Verificación:** 1354 pruebas pasan, 1 omitida, 64 subtests; `pyflakes` y
  `py_compile` limpios.
- **Commit:** ver el commit de este ciclo en `main`.
- **Observación:** la corrección se mide en offscreen (Linux). En Windows queda
  por confirmar visualmente que no hay parpadeo al cambiar las esquinas. La
  otra mitad de R-7c4a1e95 (guardar en segundo plano) sigue en Q-012.

## 2026-11-26 — sexagésimo sexto ciclo

### Corregido — el backend Nuitka no podía compilar (R-8d3f6a21, R-4d9e2b61)

Reportado por JesusQuijada34 en el issue #15 («error de implementacion») y en
`bugs.txt` (commit `bba72d6`, 2026-11-25): «la compilación quedó corrupta, todo
dice embebido, hay errores al compilar con Nuitka». Es la parte del reporte
R-4d9e2b61 que se podía reproducir y corregir sin el log del equipo del
propietario.

- **Síntoma:** con Nuitka instalado, `--list-compilers` mostraba la versión
  «desconocida» y cualquier build con el backend por defecto (Nuitka) fallaba.
- **Causa raíz (tres defectos independientes, reproducidos con Nuitka 4.4):**
  1. `build_arguments()` emitía `--output-dir <dir>` y `--output-filename
     <nombre>` separados por espacio. Nuitka 4.x exige la forma
     `--opción=valor` y abortaba con «The '--output-dir' option requires an
     argument with '--output-dir='».
  2. Pedía `--include-qt-plugins=sensible,styles`. Nuitka valida cada familia
     contra la instalación de Qt y abortaba con «FATAL: pyqt6: Error, there is
     no Qt plugin family 'styles'».
  3. `from nuitka import MainControl` lanza `AssertionError`
     (`states.is_full_compat is not None`) fuera del `__main__` de Nuitka, y la
     importación quedaba **fuera** del `try/except`, así que la excepción
     escapaba de `compile_to_exe` en lugar de degradar al subproceso que el
     propio módulo documenta.
  La versión se leía de `nuitka.__main__._getNuitkaVersion`, retirado en 4.x, y
  de `nuitka.__version__`, que no existe: de ahí «desconocida».
- **Solución:** las opciones de salida van con `=`; sólo se pide la familia
  `sensible` (el conjunto por defecto) y el plugin `pyqt6` sólo se activa si el
  binding está instalado; la importación de `MainControl` está protegida y, si
  falla, la compilación continúa con `python -m nuitka` como subproceso
  (documentado en el módulo), con el error de la API embebida anexado al
  mensaje final; la versión se lee de `nuitka.Version.getNuitkaVersion()` con
  respaldo en `importlib.metadata`.
- **Pruebas:** `tests/test_nuitka_backend_arguments.py` (6 casos: forma `=` de
  las opciones, familias Qt existentes en la instalación, versión real,
  argumentos deterministas, degradación a subproceso y error reportado sin
  excepción). Los cinco casos que describen el fallo fallan con el código
  anterior.
- **Verificación real:** compilación `--standalone --onefile` de un guion de
  prueba con Nuitka 4.4 y gcc: `compile_to_exe()` devuelve el binario y el
  ejecutable imprime su salida (`hola`, código 0). Antes del arreglo la misma
  llamada abortaba en la importación de `MainControl`.
- **Commit:** ver el commit de este ciclo en `main`.
- **Observación:** la corrección se comprueba en Linux; el build de Windows
  (Nuitka + MSVC) queda pendiente de la confirmación del propietario. El
  **entorno aislado por proyecto** que pide el mismo reporte sigue pendiente en
  Q-019 y no se ha tocado en este ciclo.
- **Release:** no se prepara. Quedan bugs de prioridad alta pendientes y 19
  aprobaciones de `CONFIRM.MD` sin aplicar.

## 2026-11-26 — sexagésimo quinto ciclo

### Corregido — la titlebar no llegaba a pantalla completa con tres gestos (R-2f8b6a31, Q-011/F-004)

Reportado por JesusQuijada34 en `bugs.txt` (2026-11-23: «tienes y debes
preparar bien el engine de la titlebar, ya que tienes que hacer que espere como
maximo los 3 gestos, si la entrada fueron 2 maximizar o restaurar, pero si
llego al maximo, full Screen») y aprobado en `CONFIRM.MD` (Q-011, commit
`bba72d6`, confirmación final F-004 en `73dcdcd`).

- **Síntoma:** el triple clic sobre la barra de título nunca entraba en modo
  inmersivo/pantalla completa; el único gesto que funcionaba era el doble clic
  (maximizar o restaurar). Además, entrar en modo inmersivo desde una ventana
  normal sólo ocultaba la barra y ponía la ventana en primer plano: la ventana
  se quedaba con su tamaño, sin barra de título, así que no era «pantalla
  completa».
- **Causa raíz:** `_make_titlebar_filter()` reiniciaba la racha de pulsaciones
  en `MouseButtonDblClick`. Qt entrega un triple clic como *pulsación, doble
  clic, pulsación*, de modo que el doble clic ponía el contador a cero y el
  tercer gesto volvía a contar como primero: nunca se alcanzaba
  `TRIPLE_CLICK`. `ImmersiveTitleBar.enter()` tampoco maximizaba la ventana.
- **Solución:** el filtro cuenta el doble clic como **segundo** gesto (y lo deja
  pasar, así que el doble clic sigue maximizando o restaurando) y dispara el
  modo inmersivo en el tercero. `ImmersiveTitleBar._ensure_maximized()`
  maximiza la ventana al entrar si no lo estaba, usando el helper
  `toggle_frameless_maximize` para conservar las esquinas rectas. El puente
  (`WindowManagerBridge`) ignora el doble clic mientras la ventana está en modo
  inmersivo, para que el tercer gesto salga sin dejar antes una ventana normal
  sin barra de título.
- **Pruebas:** `TestTitleBarGestureLimit` en `tests/test_startup_sequence.py`
  (secuencia real de Qt `press → dblclick → press` llega a pantalla completa, el
  doble clic se detiene en dos gestos y entrar maximiza una ventana normal) e
  `ImmersiveDoubleClickTests` en `tests/test_window_manager_bridge.py` (el
  doble clic alterna la ventana fuera de pantalla completa y no la toca dentro).
  Los tres casos que describen el fallo fallan con el código anterior.
- **Cola de bugs:** a petición del propietario en el issue #15 se compactó
  `bugs.md` (38 KB → 12 KB): fuera lo resuelto, los cambios de engine reducidos
  a un índice con su ficha en `CONFIRM.MD` y la cola con solo lo pendiente.
- **Commit:** ver el commit de este ciclo en `main`.
- **Verificación:** 1345 pasan, 1 omitido, 64 subtests; `pyflakes` y
  `py_compile` limpios.
- **Observación:** el gesto se comprueba en Linux/offscreen; R-2f8b6a31 queda en
  observación hasta la confirmación visual en Windows. El snap a media pantalla
  de Q-011 sigue a cargo del gestor de ventanas nativo.
- **Release:** no se prepara. Quedan bugs de prioridad alta pendientes de
  implementación y 19 aprobaciones de `CONFIRM.MD` sin aplicar.

## 2026-11-26 — sexagésimo cuarto ciclo

### Corregido — arrastrar la titlebar maximizada movía la ventana (R-6a1f8c23, Q-011/F-004)

Reportado por JesusQuijada34 en `bugs.txt` (2026-11-23: «al jalar la barra de
titulo a un lado estando maximizada, se mueve? en vez de quedar quieta y
bloqueada») y aprobado en `CONFIRM.MD` (Q-011, commit `bba72d6`, confirmación
final F-004 en `73dcdcd`).

- **Síntoma:** con la ventana maximizada, arrastrar la barra de título la
  desplazaba conservando el tamaño de la pantalla, en lugar de restaurarla a su
  tamaño normal. La ventana se quedaba sin bordes accesibles y con el tamaño
  del escritorio.
- **Causa raíz:** `WindowManagerBridge._wire_titlebar()` sustituye el
  `mousePressEvent` de la titlebar y llamaba a `start_system_move()` sin mirar
  el estado de la ventana. El manejador original de `lib/TitleBar.py` sí
  comprobaba `not is_maximized()`, pero el puente lo reemplazaba, así que esa
  guarda nunca llegaba a ejecutarse.
- **Solución:** `restore_for_drag()` restaura la ventana maximizada (con el
  helper `toggle_frameless_maximize`, o `showNormal()` si no existe), la coloca
  para que el cursor quede en la misma posición relativa de la titlebar
  (`TITLEBAR_GRAB_HEIGHT`, sin salirse del área ocupada) y sólo después se
  inicia el arrastre. El gesto se confirma al superar 4 px
  (`DRAG_START_DISTANCE`), de modo que un clic suelto sobre la titlebar no
  desmaximiza la ventana; el estado pendiente se cancela al soltar el botón.
  Si `startSystemMove()` no está disponible, el arrastre continúa con el
  manejador de `TitleBar` (`_begin_manual_drag`).
- **Pruebas:** `MaximizedDragTests` en `tests/test_window_manager_bridge.py`
  (8 casos): clic suelto sin restaurar, temblor de 1 px sin restaurar,
  movimiento sin el botón pulsado sin restaurar, restauración antes de mover,
  posición relativa del cursor, ventana dentro de la pantalla, arrastre normal
  sin cambios y respaldo de arrastre manual. Los
  casos de arrastre fallan con el código anterior. Comprobado además con
  widgets reales en `offscreen`: maximizar, pulsar (sigue maximizada) y
  arrastrar 60 px (vuelve a 900x600 y empieza el arrastre).
- **Commit:** `c346946`.
- **Verificación:** 1340 pasan, 1 omitido, 64 subtests; `pyflakes` y
  `py_compile` limpios.
- **Observación:** el defecto se ve en Windows y aquí sólo se verifica en
  Linux/offscreen; R-6a1f8c23 queda en observación hasta la confirmación
  visual. El límite de tres gestos de la titlebar (R-2f8b6a31) sigue pendiente.
- **Release:** no se prepara. Quedan bugs de prioridad alta pendientes de
  implementación y 19 aprobaciones de `CONFIRM.MD` sin aplicar.

## 2026-11-26 — sexagésimo tercer ciclo

### Corregido — `updater.py --silent` con `.iflapp` abría una ventana y no instalaba (R-7e3a9c25, Q-015)

Reportado por JesusQuijada34 en la auditoría interna de mantenimiento
(2026-11-25) y aprobado en `CONFIRM.MD` (Q-015, commit `73dcdcd`).

- **Síntoma:** `updater.py --silent` con un paquete `.iflapp` debía actualizar
  sin interfaz. En su lugar creaba una `QApplication` y una
  `ModernUpdaterWindow`, mostraba la ventana y se quedaba bloqueado en
  `app.exec()`. En un servidor sin pantalla (tarea programada, SSH sin X,
  `QT_QPA_PLATFORM=offscreen`) la actualización desatendida no instalaba nada y
  el updater devolvía éxito.
- **Causa raíz:** la rama silenciosa de
  `lib/coreUpdater/installer._update_from_iflapp` ignoraba el parámetro
  `silent` y usaba el mismo camino que el modo gráfico, terminando con
  `return True` incondicional.
- **Solución:** en modo silencioso se descarga el `.iflapp` a un archivo
  temporal (`_download_iflapp_package`, `urllib` de la biblioteca estándar y
  tiempo límite de 60 s), se instala con `install_iflapp(..., silent=True)` en
  el directorio actual y se devuelve el resultado real. El temporal se borra
  siempre, también si falla la descarga o la instalación. No se crea ninguna
  ventana. El modo gráfico no cambia.
- **Pruebas:** `tests/test_updater_silent_iflapp_update.py` (5 casos) verifica
  que no se instancia Qt en modo silencioso, que el destino es el directorio
  actual, que se propaga el fallo de instalación y de descarga, que el temporal
  se elimina y que el modo gráfico sigue abriendo la ventana. Los cuatro
  primeros casos fallan con el código anterior.
- **Commit:** `02a6786`.
- **Verificación:** 1332 pasan, 1 omitido, 64 subtests; `pyflakes` y
  `py_compile` limpios.
- **Release:** no se prepara. Quedan bugs de prioridad alta pendientes de
  implementación y 20 aprobaciones de `CONFIRM.MD` sin aplicar.

## 2026-11-26 — sexagésimo segundo ciclo

### Corregido — las ventanas vacías del arranque (R-6c4d1f87, issues #15 y #16)

Reportado por JesusQuijada34 en el issue #16 («error de gui») y en el issue #15
(«error de implementacion»), ambos del 2026-11-26 y contra el commit `d9d3c48`.

- **Síntoma:** al abrir la aplicación aparecían alrededor de nueve ventanas
  pequeñas y vacías, abriéndose y cerrándose en cadena, antes del splash.
- **Causa raíz:** `SettingsCard` y `SettingsOptionRow` (`lib/settings_cards.py`)
  construían sus rótulos con `QLabel(...)` **sin padre**. Un widget sin padre es
  una ventana de nivel superior, así que
  `self.subtitle_lbl.setVisible(bool(subtitle))` (línea 140) y
  `self.check_lbl.setVisible(self._checked)` (línea 474) mostraban un `QLabel`
  vacío de 640x480 antes de que `layout.addWidget()` lo reparentara.
  `SettingsPanel._build_cards()` monta siete tarjetas y varias filas de opción:
  el arranque abría nueve de esas ventanas.
- **Evidencia:** con un espía sobre `QWidget.setVisible` en un arranque real
  (`QT_QPA_PLATFORM=offscreen`) se registraron nueve `VISIBLE-> QLabel
  size=640x480` con la pila `SettingsPanel._build_cards → _register_card →
  SettingsCard.__init__` y `_build_cards → SettingsOptionRow.__init__`. Antes
  del arreglo el arranque mostraba once ventanas; después, sólo el splash y la
  ventana principal. El arreglo del splash de nivel superior (F-003, ciclo 60)
  era correcto pero no era la causa de estas nueve ventanas.
- **Solución:** los rótulos de `SettingsCard` (icono, título, subtítulo y
  flecha) y de `SettingsOptionRow` (texto y marca) nacen con su tarjeta como
  padre, de modo que `setVisible()` nunca saca una ventana a la pantalla. No
  cambian el aspecto ni la API pública de las tarjetas.
- **Pruebas:** `tests/test_startup_stray_windows.py` (4 casos) instala el espía
  en `QWidget.setVisible` y exige que construir una tarjeta con subtítulo, una
  sin subtítulo, una opción marcada y el panel de Configuración completo no
  muestre ningún widget sin padre. Los tres primeros casos fallan con el código
  anterior.
- **Verificación:** 1327 pasan, 1 omitido, 64 subtests; `pyflakes` y
  `py_compile` limpios; arranque real sin ventanas intermedias.

### Mantenimiento — cola de bugs bajo el límite y bitácora archivada

- Se retiran de `bugs.md` las tres entradas resueltas que seguían en la cola
  (R-d23039c0, R-5d8e2a41 y R-4c8e1f27, todas del ciclo 25) y se indexan en
  `docs/bugs_resueltos.md` (162 → 166 entradas).
- La bitácora de ciclos que vivía al final de `bugs.md` se traslada completa a
  `docs/ciclos_mantenimiento.md`; `bugs.md` pasa de 87 KB a 40 KB y queda sólo
  con lo pendiente, lo aprobado sin implementar y la tabla `En observación`.
- **Issues #15 y #16:** se documenta la causa raíz real y la verificación. El
  issue #16 queda cerrado; el #15 sigue abierto por el splash dentro de la
  ventana (Q-032), que es un cambio de engine sin aprobar.
- **Release:** no se prepara. Quedan bugs de prioridad alta pendientes de
  implementación y 21 aprobaciones de engine sin aplicar.

## 2026-11-26 — purga de bugs resueltos y skills de detective/CEO

- `bugs.md` queda como cola activa: 17 pendientes y una tabla compacta de
  `En observación`. Los 162 resueltos se indexan en `docs/bugs_resueltos.md`
  (53 KB) y el detalle completo vive en este changelog y en los issues.
- Se añaden las skills `.agents/skills/detective/SKILL.md` (causa raíz con
  evidencia) y `.agents/skills/ceo/SKILL.md` (priorización por impacto, riesgo
  y esfuerzo).
- Los prompts de mantenimiento, push y Telegram incorporan la autorización del
  propietario sin confirmación para bugs y mejoras normales, y la purga
  inmediata de los resueltos en el mismo ciclo.

## 2026-11-26 — sexagésimo primer ciclo

### Corregido — `create` del CLI ya no sobrescribe un proyecto existente sin `--force` (Q-016, R-6d2a8f19)

Reportado por JesusQuijada34 en `CONFIRM.MD` (Q-016, 2026-11-25). Aprobado con
la **opción B** en el commit `71e50f7` (2026-11-26, push que sólo toca
`CONFIRM.MD`; autoría verificada con `git log` y la API de GitHub) y aplicado en
este ciclo.

- **Síntoma:** `packagemaker.py create` escribía en la carpeta canónica aunque
  ya existiera. El dashboard y el asistente gráfico preguntaban antes de
  sobrescribir, pero el CLI headless pisaba el trabajo del usuario en silencio.
- **Causa raíz:** la rama headless de `handle_cli_action` no comprobaba la ruta
  de destino antes de llamar a `create_project_from_templates`, que crea la
  carpeta con `mkdir(parents=True, exist_ok=True)` y reescribe los archivos.
- **Solución:** el subparser `create` acepta `--force` y `get_action` lo
  propaga como opción. Si la carpeta canónica existe y no se pasó `--force`, el
  comando imprime `[ERROR] El proyecto ya existe: <ruta>`, recuerda
  `Usa --force para sobrescribirlo.` y sale con código 1. Con `--force` avisa
  con `[WARN] Sobrescribiendo el proyecto existente: <ruta>` y regenera el
  proyecto. El dashboard y el asistente gráfico no cambian.
- **Pruebas:** `tests/test_maintenance_cli_regressions.py` gana
  `CreateOverwriteGuardTests` (6 casos): rechazo con código 1 sin tocar el
  guion del usuario, mensaje con la sugerencia de `--force`, sobrescritura
  forzada con aviso, creación limpia sin aviso y el cableado de `--force` en el
  parser (presente y ausente).
- **Verificación:** `QT_QPA_PLATFORM=offscreen python -m pytest
  tests/test_maintenance_cli_regressions.py tests/test_confirm_channel.py
  tests/test_splash_top_level.py -q` → 46 pasan; `pyflakes` y `py_compile`
  limpios.
- **Nota de compatibilidad:** los scripts que recrean un proyecto a propósito
  deben añadir `--force`; sin él reciben un error explícito en vez de una
  sobrescritura silenciosa.

### Mantenimiento — cola de bugs más corta y issues #15/#16 atendidos

- Se retiran de `bugs.md` las entradas ya resueltas y verificadas sin
  reaparición: **R-4c1a9e72** (catálogos de `lang/`, ciclo 58) y **R-4e7a1d92**
  (Configuración con una sola barra, ciclo 59). Su detalle queda en
  `docs/bugs_resueltos.md` y en este changelog. La cola pasa de 19 a 20
  entradas: se archivan dos resueltas y se añaden R-6d2a8f19 (este ciclo) y
  R-5c9a3e17 (splash UWP, pendiente de aprobación).
- **Issues #15 y #16** («se abren varias ventanas de Python vacías antes de la
  interfaz»): reportados contra el commit `d9d3c48`, que ya incluye el arreglo
  del splash de nivel superior del ciclo 60 (F-003). Se respondió en ambos con
  el commit del arreglo y la petición de confirmación en una ejecución nueva;
  no se declaran resueltos hasta verificarlos en Windows.
- **Q-032 (nuevo):** la petición del issue #15 de un splash **dentro** de la
  ventana principal, al estilo UWP, es un cambio de engine: queda registrada en
  `CONFIRM.MD` y en `bugs.md` (R-5c9a3e17) a la espera de aprobación. No se
  tocó el ciclo de vida de ventanas en este ciclo.
- No se prepara release: siguen abiertos bugs de prioridad alta y 21
  aprobaciones de engine pendientes de implementación.

## 2026-11-26 — sexagésimo ciclo

### Corregido — Splash de nivel superior y fin de las ventanas vacías del arranque (R-4f8a2c60, Q-008/F-003)

Reportado por JesusQuijada34 en `bugs.txt` (commit `bed2e83`) y repetido en el
[issue #13](https://github.com/JesusQuijada34/packagemaker/issues/13) («Bug de
codigo»). Cambio de engine **aprobado** en Q-008 (commit `bba72d6`, 2026-11-25)
y **confirmado** en F-003 (commit `73dcdcd`, 2026-11-26; autoría verificada con
la API de GitHub). No toca la ley de nombres, el formato `.iflapp`, las
plantillas ni el contenido de los paquetes.

- **Síntoma:** al abrir la aplicación aparecían unas cinco ventanas vacías
  antes de la interfaz, el splash se dibujaba a la vez que la ventana principal
  y, en Windows, la consola mostraba
  `QWidgetWindow(...) must be a top level window` y
  `UpdateLayeredWindowIndirect failed for ptDst=...`.
- **Causa raíz:** `IntegratedSplash` se creaba con `parent=main_window` y
  `WA_TranslucentBackground`, así que era un widget **hijo** translúcido; Qt
  necesita una ventana de nivel superior para una superficie por capas. Además
  se construía después de `PackageTodoGUI()`, no antes.
- **Solución:** el splash se crea y se muestra antes de la ventana principal,
  sin padre, y ocupa la pantalla disponible (`_sync_geometry`). Al cerrarse
  llama a `destroy()` antes de `deleteLater()` para liberar la ventana nativa.
  La ventana principal se muestra debajo y la revela el desvanecido. El
  `IntegratedSplash` de `updater.py` recibe el mismo arreglo.
- **`WipeWindow`:** se sigue aplicando sólo a ventanas top-level (diálogos y
  ventana principal); el splash ya no es un hijo.
- **Pruebas:** `tests/test_splash_top_level.py` (9 casos): splash de nivel
  superior sin padre, geometría de pantalla completa, recolocación al
  redimensionar, modo con padre heredado, acento recibido, `destroy()` al
  cerrar, el del updater y un arranque real en subproceso que comprueba que el
  splash ya está visible y es de nivel superior cuando se construye la ventana
  principal.
- **Verificación:** `1317 pasan, 1 omitido, 64 subtests`; `pyflakes` y
  `py_compile` limpios; arranque real
  (`DISPLAY=:0 QT_QPA_PLATFORM=offscreen python packagemaker.py`) sin avisos de
  nivel superior.
- **Pendiente:** verificación visual en Windows (el bug sigue en observación) y
  el triple clic de la titlebar, que va con F-004.

### Aprobaciones del propietario procesadas (push `73dcdcd`)

El push `73dcdcd` sólo modificó `CONFIRM.MD`. Autoría verificada con la API de
GitHub (`JesusQuijada34`). Respuestas procesadas:

- **Aprobadas:** Q-015, Q-017, Q-018, Q-019, Q-020 y Q-021…Q-031, más las
  confirmaciones finales F-001, F-002, F-004, F-005 y F-006.
- **Con instrucciones adicionales:** Q-019 (interruptor **Red** con modo de uso
  medido, aviso de que requiere el Python del sistema e indicaciones para
  seguir sin conexión), Q-023 (manifestar el backend de la rama `render` para el
  inicio de sesión con GitHub), Q-027 («perfecto»), Q-028 («hazlo con
  compatibilidad»), Q-031 (sandbox de DLL sospechosas y restricción del acceso a
  claves y credenciales) y F-006 (un fallo debe reportarse con la cuenta
  logueada y mejor contraste).
- **No aplicada:** **Q-016**, escrita como `[B] SÍ`, que no es una casilla
  válida (`[x] SÍ` / `[ ] NO`). Se dejó sin marcar y se volvió a preguntar.
- **Aplicada este ciclo:** Q-008 / F-003 (el arreglo del splash).
- **Pendientes de implementación:** el resto, empezando por clasificar los
  módulos de motor (F-002) como pidió el propietario.

No se prepara release: siguen abiertos bugs de prioridad alta y el periodo de
7 días sin reportes no se ha cumplido.

## 2026-11-26 — quincuagésimo noveno ciclo

### Corregido — Configuración con una sola barra de acciones y retroceso con nombre (R-4e7a1d92)

Reportado por JesusQuijada34 en el [issue #14](https://github.com/JesusQuijada34/packagemaker/issues/14)
(«Tarjetas y problema de interfaz»). Triaje además del
[issue #13](https://github.com/JesusQuijada34/packagemaker/issues/13) («Bug de
codigo»). **Ningún cambio de comportamiento del engine**: la ley de nombres, el
formato `.iflapp`, las plantillas y el contenido de los paquetes siguen igual.

- **R-4e7a1d92 (Media, issue #14):** la página **Configuración** mostraba dos
  barras de acciones (la de la página y la cabecera propia del panel, con la
  cápsula «‹ Privacidad») y repartía los botones entre ambas; al entrar en una
  tarjeta después de cambiar el idioma, el botón de retroceso se quedaba como
  «‹» sin nombre. Tres causas acumuladas:
  1. `SettingsPanel` montaba su propia `SettingsHeader` además de la barra
     compartida que instala `init_config_tab`.
  2. `SettingsPanel.retranslate()` reconstruía `_titles` con una lista fija de
     cinco tarjetas que no incluía **privacy**, así que `_open("privacy")`
     pintaba `""`. El prefijo «‹» impide que `live_i18n.retranslate_tree()`
     recupere el texto por valor, de modo que nada lo reparaba después.
  3. `apply_soft_shadow()` sobre la cabecera translúcida dibujaba un halo gris
     alrededor del texto de la cápsula (el «texto con fondo detrás» del
     reporte).
  - **Solución:** una sola barra por página. `SettingsPanel` ya no crea
    cabecera: emite `navigationChanged(título, profundidad, confirmar)` y
    expone `go_back()`/`confirm_and_go_back()`. `init_config_tab()` instala la
    barra compartida con un retroceso **con nombre** (`‹  Configuración`, de
    `config.title`) y `Confirmar` (`config.confirm`), visibles sólo dentro de un
    detalle, sincronizados por `_on_config_navigation()`. Los títulos de las
    tarjetas se guardan con su clave i18n y `retranslate()` los reconstruye
    desde ella (siete tarjetas, Privacidad incluida). `SettingsNavigator`
    anuncia la profundidad definitiva al terminar el deslizamiento y expone
    `busy()`, así que pulsar atrás durante la animación no desfasa la barra. Se
    retiró la clase `SettingsHeader`, ya sin uso.
  - **Pruebas:** `tests/test_settings_navigation_bar.py` (11 casos). Los 11
    fallan con el código anterior (comprobado con `git stash` de
    `packagemaker.py`, `lib/settings_panel.py` y `lib/settings_cards.py`).
- **Issue #13 (R-4f8a2c60, sin cambios de código):** las «varias ventanas de
  python» del arranque no las crea el *Application Frame Host* de Windows, sino
  Qt: `IntegratedSplash` se construye con `parent=main_window` y
  `WA_TranslucentBackground`, y `WipeWindow` se aplica sobre un widget hijo, lo
  que obliga a crear ventanas nativas auxiliares. Es el defecto ya registrado en
  R-4f8a2c60, aprobado en Q-008 y bloqueado por la confirmación final **F-003**.
  La duración mínima del splash (~5 s escalada por RAM/CPU) y el reporte de
  tirones que pide el mismo issue quedan como **Q-027** (R-7b2c9e51).
- **Resto del issue #14 (sin implementar, requiere aprobación):** librería de
  paneles y pestañas verticales con action bar propia (**Q-028**), AIDE como
  chatbot con backend/API/servidor (**Q-029**), perfil de GitHub como extensión
  y reordenación del sidebar (**Q-030**) y addons empaquetados en `lib/addons/`
  con addons DLL (**Q-031**). Se documentan en `bugs.md` y `CONFIRM.MD`.
- **Verificación:** `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` →
  1308 pasan, 1 omitido, 64 subtests. `pyflakes` y `py_compile` limpios.
  Comprobación visual con la ventana real en `offscreen`: la página
  Configuración muestra una única barra; el detalle «Privacidad» pinta
  «‹  Configuración · Privacidad · Confirmar» y se retraduce a inglés
  («‹  Settings · Privacy · Confirm») y a japonés («‹  設定 · プライバシー ·
  確定»).

No se prepara release: hay bugs de prioridad alta abiertos (R-4f8a2c60,
R-6a1f8c23, R-4d9e2b61, R-7c4a1e95) bloqueados por la confirmación final del
propietario, y el periodo de observación sigue abierto.

## 2026-11-26 — quincuagésimo octavo ciclo

### Corregido — claves sobrantes en los catálogos de idioma (R-4c1a9e72)

Auditoría interna, sin reporte externo nuevo: los issues #10 y #11 siguen
abiertos y `CONFIRM.MD` no tiene respuestas nuevas del propietario, así que
**ningún cambio de comportamiento del engine**. La ley de nombres, el formato
`.iflapp`, las plantillas y el contenido de los paquetes siguen igual.

- **R-4c1a9e72 (Media, auditoría interna):** con la interfaz en inglés, al
  cambiar de idioma la casilla «Enviar los fallos automáticamente…» y su pista
  de la página **Reportes** se quedaban en inglés. Doce catálogos de `lang/`
  llevaban claves planas sobrantes (`report.auto_send`,
  `report.auto_send_hint` dentro del objeto `report`, y
  `form.author_placeholder` dentro de `create`) que al aplanarse creaban
  claves inexistentes o colisionaban con las reales. `live_i18n` indexa por
  valor, así que el texto inglés ganaba el índice bajo `report.report.auto_send`
  y el catálogo destino devolvía ese mismo texto inglés: la retraducción no
  cambiaba nada.
  - **Datos:** se retiraron las claves planas de los 13 catálogos afectados.
    El valor traducido de `form.author_placeholder` se trasladó a su clave
    anidada `create.form.author_placeholder`, que hasta ahora guardaba el texto
    español en todos los idiomas y sólo se veía bien por la colisión. El texto
    aplanado de cada catálogo queda idéntico salvo las dos claves sobrantes
    eliminadas (comprobado contra `git show HEAD:lang/<x>.json`).
  - **Código:** `lib/live_i18n.py` sólo indexa claves que existen en el
    catálogo español (lista canónica), en `reverse_index()` y en
    `template_index()`. Una clave sobrante ya no puede ganar el índice.
  - **Pruebas:** `tests/test_translation_catalog_hygiene.py` (5 casos: sin
    claves planas con punto, mismas claves que `es.json`, marcador de Autor
    traducido, índice inverso sólo con claves canónicas y retraducción del
    texto inglés del envío automático a de/fr/ja/zh). Tres fallan con los
    catálogos anteriores y con `live_i18n` sin el filtro.
- **Verificación:** `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` →
  1297 pasan, 1 omitido, 64 subtests. `pyflakes` y `py_compile` limpios.
  Build real de extremo a extremo: `create` headless →
  `--buildthis --compiler zipapp --harden integrity` → `--inspect` (identidad
  canónica `AuditCo.auditdemo.v1.0-26.11-…-Danenone`, 21 archivos, raíz Merkle
  correcta) → `verify_iflapp()` → `valid`.

No se prepara release: hay bugs de prioridad alta abiertos (R-4f8a2c60,
R-6a1f8c23, R-4d9e2b61, R-7c4a1e95) bloqueados por la confirmación final del
propietario, y el periodo de observación sigue abierto.

## 2026-11-25 — quincuagésimo séptimo ciclo

### Verificado — cierre del issue #12 y triaje del issue #11

Ciclo de verificación y triaje. **Ningún cambio de código ni de comportamiento
del engine**: se revisa lo entregado en el ciclo anterior, se cierra lo que
está probado y se separa lo que exige aprobación del propietario.

- **Issue #12 (R-9b3e7a41) cerrado:** la tabla del entorno ya se rotula en el
  idioma activo. Verificado en vivo con `_env_label()` sobre `lang/*.json`
  (`es` → `Sistema operativo`/`Idioma`, `en` → `Operating system`/`Language`,
  `ja` → `オペレーティングシステム`/`言語`, `ar` → `نظام التشغيل`/`اللغة`).
  La suite completa pasa (1292 + 1 omitido, 64 subtests) y `pyflakes`/
  `py_compile` están limpios.
- **Issue #11 (R-1f6c9d38) primera parte verificada:** el cuadro «Contexto» ya
  no existe en el sidebar y la descripción se dibuja bajo el título de la barra
  de acciones. El issue **sigue abierto**: el resto de su texto pide una
  sección de ayuda, addons en `lib/addons/`, conectar proyectos a repositorios
  de GitHub (público/privado), la extensión CloudCube, el updater como
  extensión, terminar el motor Leviathan y cambios de tema del sidebar. Todo
  eso queda registrado como `Q-021`…`Q-026` en `CONFIRM.MD`; no se implementa
  nada sin aprobación.
- **Issue #10 (R-8c4f1a72) en observación:** la corrección está en `main` y
  probada en Linux/offscreen; el issue sigue abierto hasta la comprobación
  visual en Windows.

No se prepara release: el periodo de observación sigue abierto y no han pasado
7 días sin reportes nuevos.

## 2026-11-25 — quincuagésimo sexto ciclo

### Corregido — tabla del entorno traducida (issue #12) y descripción de página fuera del sidebar (issue #11)

Dos reportes nuevos de JesusQuijada34. **Ningún cambio de comportamiento del
engine**: la ley de nombres, el formato `.iflapp`, las plantillas y el contenido
de los paquetes siguen igual.

- **R-9b3e7a41 — Issue #12 «problema de idioma» (Media):** la tabla de entorno
  que se adjunta a los reportes salía siempre en español (`Dato`/`Valor`)
  aunque la interfaz estuviera en otro idioma. `lib/report_telemetry.py` ahora resuelve las
  etiquetas con `_env_label()` contra las claves `env.*` de los 14 catálogos de
  `lang/` y publica el campo `language` en el snapshot, de modo que el issue
  indica en qué idioma se estaba usando la aplicación. Verificado en vivo:
  es `Dato/Valor`, en `Field/Value`, ja `項目/値`, ar `البيان/القيمة`.
- **R-1f6c9d38 — Issue #11 «Orden», primera parte (Media):** el cuadro de
  contexto del sidebar desaparece (`desc_card`, `sidebar_desc_text` y las
  reglas `QWidget#SidebarContextCard`). La descripción de la página se dibuja ahora
  **bajo el título de su barra de acciones y fuera de la píldora**, con
  `install_page_action_bar()` exponiendo `subtitle_label` y
  `set_action_bar_subtitle()`. El manifiesto guarda `### Título\nDetalle`; bajo
  el título de la página ese encabezado sobraba, así que sólo se muestra el
  detalle. AIDE y Configuración, que no tenían barra, la reciben.
- **R-7d2a5b84 — Barra de actividad (bugs.txt), Media:** `lib/activity_bar.py`
  añade un marquee fino bajo cada barra de acciones, siempre presente pero
  inactivo, que se anima cuando hay trabajo en segundo plano. Sustituye al diálogo con barra de
  progreso; el guardado automático de Configuración ya lo enciende.
- **R-4b8f1e27 — Sin PyYAML la ventana no abría (Alta):** `load_addons()`
  devolvía una lista vacía en vez de los addons integrados, así que el sidebar
  quedaba sin botones y `__init__` reventaba en `self.btn_create.setChecked(True)`. Ahora recurre a
  `fallback_addons()`.

Commit: `1655007`. Pruebas nuevas en `tests/test_activity_bar_and_subtitle.py`
(estado del marquee, subtítulo fuera de la píldora, pintura en ambos estados) y
dos más en `tests/test_report_extension.py` (idioma de la tabla) y
`tests/test_privacy_switch_and_addons_ui.py` (la descripción vive en la barra y
el sidebar ya no tiene cuadro de contexto).

## 2026-11-25 — quincuagésimo quinto ciclo

### Corregido — la página de Reportes no respetaba el fondo, el scrollbar ni la tabla del entorno

Primer reporte externo recibido a través de la propia extensión de reportes: el
issue #10 llegó enviado desde la aplicación con la cuenta de JesusQuijada34.
**Ningún cambio de comportamiento del engine**: la ley de nombres, el formato
`.iflapp`, las plantillas y el contenido de los paquetes siguen igual.

- **R-8c4f1a72 — la pestaña Reportes rompía el fondo y no se leía el scrollbar
  (Media, issue #10):** la franja situada por encima de la barra de acciones
  pintaba una capa distinta al resto de la pestaña porque el viewport del
  `QScrollArea` conservaba el color base de la paleta y la página no usaba
  `WA_StyledBackground`. El scrollbar global (10 px, mango al 24 % de opacidad)
  apenas se distinguía y todo el contenido iba en una sola columna, con el
  formulario muy abajo. Ahora la página usa el mismo fondo que las demás, el
  viewport es transparente, el contenido se reparte en dos columnas (izquierda:
  sesión y formulario; derecha: cola y entorno) y el scrollbar usa la nueva
  variante `prominent` de `source/qss/qscrollbar.qss` (mango de 12 px y más
  opaco) expuesta por `design_tokens.scrollbar_qss()`. La tabla markdown del
  entorno se convierte a HTML con `_environment_html()` y se muestra como tabla
  enriquecida, con los valores escapados. Reportado por JesusQuijada34
  (issue #10, reporte enviado desde la aplicación). Queda **pendiente de
  verificación visual en Windows**, así que no se marca como resuelto del todo.

Commit: `b5378ad`. Pruebas nuevas en `tests/test_report_page_ui.py` (dos
columnas, tabla enriquecida, viewport transparente, scrollbar visible y
escapado de valores) y en `tests/test_qss_loader.py` (la variante `prominent`
resuelve todos sus marcadores). Suite completa: 1219 pasan, 1 omitido, 64
subtests. `pyflakes` y `py_compile` limpios. Además se verificó con una captura
offscreen que la franja superior y el contenido comparten ahora el mismo color
(`rgb(28,28,30)`) y que el scrollbar aparece al reducir la altura de la
ventana.

No se prepara release: siguen abiertos R-4f8a2c60 (Q-008/F-003), R-6a1f8c23
(Q-011/F-004), R-4d9e2b61 (Q-019), R-7c4a1e95 (Q-012), R-2f8b6a31
(Q-011/F-004), R-8c4f1a72 (a la espera de la comprobación visual en Windows),
R-5a7d2f16 y R-3c8e4b72. Los seis cambios de engine aprobados siguen sin
confirmación final (`F-001`…`F-006`).
## 2026-11-18 — quincuagésimo sexto ciclo

### Añadido — addons del sidebar, switch de privacidad y asistente AIDE

Tres funciones nuevas pedidas por el propietario. **Ningún cambio de
comportamiento del engine**: la ley de nombres, el formato `.iflapp`, las
plantillas y el contenido de los paquetes siguen igual.

- **Sistema de addons.** El sidebar ya no está escrito a mano en
  `packagemaker.py`: cada página es un manifiesto YAML en `addons/` con
  `id`, `order`, `section`, `label`, `icon` y `builder`. `lib/addons_engine.py`
  los lee, valida y ordena por sección (`main`, `tools`, `footer`); un manifiesto
  roto se ignora y se anota en `Addon.skipped` para que la ventana siga
  abriendo. Si falta `addons/` por completo (bundle incompleto) se usan los
  addons integrados, así que el sidebar nunca queda vacío. Nueva acción
  headless `--list-addons` para inspeccionarlos sin abrir la GUI.
- **Switch de privacidad.** Nueva tarjeta «Privacidad» en Configuración con dos
  interruptores independientes —envío automático de fallos al repositorio
  (`auto_report_errors`) y envío a un servidor propio (`telemetry_enabled`)—
  más el campo con la URL del servidor (`telemetry_endpoint`), que antes no
  existía y hacía inutilizable la segunda opción: `errorReporter.is_enabled()`
  exige URL y switch. Ambos valores se cargan del almacén al abrir la ventana
  (antes el panel arrancaba siempre con los valores por defecto).
- **AIDE.** Asistente dentro de la app con dos proveedores: GitHub Copilot por
  el SDK oficial (`microsoft-copilot-sdk`) o cualquier endpoint compatible con
  OpenAI con clave propia. `lib/aide_backend.py` informa del estado real —sin
  SDK, sin sesión, sin URL, sin clave— con un código de motivo que la interfaz
  traduce; nunca finge que funciona. Sólo se envía el prompt y el contexto que
  el usuario marque, saneado con `lib/report_telemetry.sanitize()`. La respuesta
  llega desde un hilo daemon, así que cruza a la GUI por una señal Qt y no
  tocando widgets desde el hilo del backend.

- **Pruebas:** `tests/test_addons_engine.py` (22), `tests/test_aide_backend.py`
  (16) y `tests/test_privacy_switch_and_addons_ui.py` (21). Las claves nuevas
  están en los 14 idiomas con traducciones curadas
  (`tools/translations_extension.py`), no con texto en inglés.

## 2026-11-25 — quincuagésimo cuarto ciclo

### Corregido — copia del paquete ante bloqueos y estados de los radios

Sin reportes externos nuevos. Se atienden dos de los ocho reportes que el
propietario dejó en el commit `bba72d6`. **Ningún cambio de comportamiento del
engine**: la ley de nombres, el formato `.iflapp`, las plantillas y el contenido
de los paquetes siguen igual.

- **R-6b2f8d43 — el build fallaba con «archivo en uso por otro proceso»
  (Alta):** `create_package()` y `_copy_package_files()` copiaban el paquete con
  `shutil` crudo (`shutil.rmtree(dest)` sin reintentos, `shutil.copytree` y
  `shutil.copy2`), y al fallar la verificación limpiaban con
  `shutil.rmtree(..., ignore_errors=True)`. En Windows, un archivo del paquete
  anterior abierto por otro proceso (antivirus, ejecutable todavía en marcha)
  hacía que la copia lanzara `WinError 32`; la excepción escapaba de `run()`,
  que sólo tiene `finally`, y mataba la QThread del build. Ahora hay un
  `copy_tree()` en `lib/file_ops.py` que reintenta incluso cuando `copytree`
  agrupa los fallos en `shutil.Error` y refresca un paquete existente con
  `dirs_exist_ok=True`; `_copy_package_files()` usa `remove_tree`, `copy_tree` y
  `copy_file` para el proyecto, los archivos obligatorios y los binarios de
  `dist`, y `create_package()` limpia con `remove_tree` y lista con
  `list_directory`. Un fichero que no se libera se registra con `[WARN]` y el
  build termina con un error legible. Queda pendiente de verificación en Windows
  con la traza original, así que **no se marca como resuelto del todo**.
  Reportado por JesusQuijada34 (commit `bba72d6`; caso #4).
- **R-9e5c3d84 — los radios no seguían los estados normal/hover/pressed
  (Baja):** `source/qss/qradiobutton.qss` sólo definía reposo, un hover que
  cambiaba el borde a blanco y checked. Ahora el indicador tiene borde gris en
  reposo, hover con borde y relleno del acento, pressed con borde de 3px del
  mismo acento (crecimiento hacia dentro) y relleno de acento, checked con
  anillo de 5px, `checked:hover`/`checked:pressed` con `ACCENT_HOVER` y
  `disabled` atenuado. `radio_qss()` pasa `TEXT_DIM`, `TEXT_FAINT` y
  `ACCENT_HOVER`. Reportado por JesusQuijada34 (commit `bba72d6`; caso #4).

Pruebas nuevas: `tests/test_engine_isolation.py` (5 casos de copia con bloqueos
simulados `WinError 32`, todos fallan con el código anterior) y
`tests/test_qss_loader.py` (estados del indicador). Suite completa:
1178 pasan, 1 omitido, 64 subtests. `pyflakes` y `py_compile` limpios.
Además, un build real (`create_project_from_templates` + `FlangCompiler.run()`
con backend zipapp) produjo un `.iflapp` de 59 KB que `verify_iflapp()` acepta
(`valid: True`), lo que ejercita de extremo a extremo la copia modificada.

No se prepara release: siguen abiertos R-4f8a2c60 (Q-008/F-003), R-6a1f8c23
(Q-011/F-004), R-8a3f1c72 (Q-020), R-4d9e2b61 (Q-019), R-7c4a1e95 (Q-012),
R-2f8b6a31 (Q-011/F-004), R-5a7d2f16 y R-3c8e4b72. Los seis cambios de engine
aprobados siguen sin confirmación final (`F-001`…`F-006`).

## 2026-11-25 — quincuagésimo tercer ciclo

### Corregido — traducción cruda en el registro de compilación, interfaz sin Pillow y notificación de error sin `pyperclip`

Al cierre del ciclo se integró el commit del propietario `bba72d6`, que aportó
7 aprobaciones con instrucciones y 8 reportes nuevos. De los tres bugs
corregidos en este ciclo, ninguno cambia el comportamiento del engine: la ley
de nombres, el formato `.iflapp`, las plantillas y los paquetes siguen
exactamente igual.

- **R-9c7e4a21 — el aviso de carpeta bloqueada mostraba la clave cruda:** en
  español (idioma por defecto) e inglés, `tr("build_log.folder_locked")`
  devolvía el identificador porque la clave existía en los 12 idiomas
  traducidos pero faltaba en `lang/es.json` y `lang/en.json`. El aviso real era
  «No se pudo eliminar build: build_log.folder_locked». Se añadió la clave a
  ambos catálogos («todavía en uso por otro proceso» / «still in use by another
  process»). La auditoría de i18n ahora recorre también los subpaquetes del
  motor (`lib/blindcubeEngine/`, etc.) y una prueba nueva exige que toda clave
  usada por `tr()` exista en `es.json` y `en.json`. Reportado por
  JesusQuijada34 (auditoría interna; caso #4).
- **R-4b8f2d63 — el framework vendorizado se desactivaba sin Pillow:**
  `lib/leviathan_ui/inmojiTrx.py` importaba `PIL` al cargarse y
  `lib/leviathan_ui/__init__.py` importa ese módulo, así que sin Pillow fallaba
  el `import` de todo el framework: `leviathan_bridge` devolvía `None` y la
  aplicación perdía la barra de título, el splash y los efectos de ventana sin
  avisar. Pillow sólo hace falta para generar iconos. El import quedó protegido,
  `generate_ico()` devuelve `None` con un mensaje claro y `apply_to_app()` usa
  un `QIcon()` vacío; además, `Pillow` se declara en `lib/requirements.txt`.
  Reportado por JesusQuijada34 (auditoría interna; caso #4).
- **R-2e6d9b14 — la notificación de error revienta sin `pyperclip`:**
  `error_handler()` importaba `pyperclip` antes de crear la notificación, y esa
  biblioteca no es una dependencia del proyecto. Sin ella, el propio aviso de
  error lanzaba `ModuleNotFoundError` (y desde un slot de Qt habría abortado el
  proceso). El import vive ahora dentro del botón «Copiar», con el portapapeles
  de Qt como respaldo y un mensaje de log si tampoco está disponible. Reportado
  por JesusQuijada34 (auditoría interna; caso #4).

Pruebas: `tests/test_i18n_curated.py` (nueva comprobación de catálogos de origen
y recorrido recursivo), `tests/test_engine_packages_layout.py` (framework sin
Pillow) y `tests/test_notification_error_handler.py` (2 casos). Suite completa:
1172 pasan, 1 omitido, 64 subtests. `pyflakes` y `py_compile` limpios.

### Integración del commit del propietario `bba72d6`

- Los cambios de este ciclo se rebasaron sobre `bba72d6` sin reescribir el
  commit del propietario (sin force push).
- Se registraron sus 7 respuestas afirmativas: Q-004 (opción A), Q-007, Q-008,
  Q-011, Q-012, Q-013 y Q-014. **Ninguna se aplicó en este ciclo**: la regla de
  mantenimiento exige una confirmación final antes de tocar el engine, y se
  añadieron los bloques `F-001`…`F-006` en `CONFIRM.MD`.
- Se registraron sus 8 reportes nuevos en `bugs.md` (R-8a3f1c72, R-4d9e2b61,
  R-6b2f8d43, R-7c4a1e95, R-2f8b6a31, R-9e5c3d84, R-5a7d2f16 y R-3c8e4b72).
  Quedan pendientes; ninguno se marca como resuelto.
- Se añadieron Q-019 (entorno aislado de compilación) y Q-020 (traducción
  completa al cambiar de idioma) a `CONFIRM.MD`.

No se prepara release: siguen abiertos R-4f8a2c60 (pendiente de Q-008) y
R-6a1f8c23 (pendiente de Q-011); además, el commit `bba72d6` reinició el
periodo de observación con 8 reportes nuevos el 2026-11-25.

## 2026-11-25 — quincuagésimo segundo ciclo

### Corregido — el programa vuelve a arrancar en máquinas sin PyQt6

Sin reportes externos nuevos. Dos hallazgos de la auditoría interna sobre el
arranque sin la dependencia gráfica. Ningún cambio de comportamiento del
engine: la GUI usa PyQt6 como siempre y sólo cambia la rama de respaldo.

- **R-7a5d2c94 — el programa no arrancaba sin PyQt6:** `packagemaker.py`
  abortaba con `NameError: name 'QPushButton' is not defined` (o `pyqtSignal`,
  `QGroupBox`, `QGridLayout`, `Qt`…) al importarse, antes de leer los
  argumentos, así que `--app-version`, `--list-compilers`, `--inspect` y la
  propia TUI no llegaban a ejecutarse; `main()` tiene una rama explícita para
  `not PYQT6_AVAILABLE` que nunca se alcanzaba. Los respaldos de
  `except ImportError` de `packagemaker.py`, `lib/settings_cards.py`,
  `lib/github_login_landing.py`, `lib/github_profile_card.py`,
  `lib/iflapp_ide_dialog.py` y `lib/pm_dashboard.py` estaban incompletos.
  Ahora todos ellos declaran un sustituto inerte `_QtStub` para cada nombre
  importado en el `try`. Esto también cubre el caso real de una máquina con
  PyQt6 instalado pero con `libEGL.so.1` ausente, donde el import falla igual.
  Reportado por JesusQuijada34 (auditoría interna).
- **R-2f6c8a13 — ruido de depuración en cada arranque sin Qt:** la rama sin
  PyQt6 ejecutaba `print("font: none", file=sys.stderr)` al importarse el
  módulo. Se eliminó; `app_font()`/`code_font()` ya devuelven `None`.
  Reportado por JesusQuijada34 (auditoría interna).

Pruebas: `tests/test_cli_without_pyqt6.py` (7 casos nuevos; 6 fallan con el
código anterior). Suite completa: 1168 pasan, 1 omitido, 64 subtests.
`pyflakes` y `py_compile` limpios. Verificado además sin Qt en ejecución real:
`--app-version`, `--list-compilers`, `--list-engines`, `--list-hardening`,
`--list-fonts`, `--ide-scan`, `create --headless` y el menú de la TUI.

No se prepara release: siguen abiertos R-4f8a2c60 (pendiente de Q-008) y
R-6a1f8c23 (pendiente de Q-011), y el requisito de 7 días sin reportes nuevos
continúa en curso desde el 2026-11-22.

## 2026-11-25 — quincuagésimo primer ciclo

### Corregido — los proyectos generados ya declaran su propia versión, su nombre visible y un lanzador que funciona

Sin reportes externos nuevos. Tres hallazgos de la auditoría interna sobre los
artefactos que producen `create` y las plantillas de proyecto. Ningún cambio de
comportamiento del engine: la ley canónica de nombres, el formato `.iflapp` y el
contenido de los paquetes siguen exactamente igual.

- **R-2c7e5a91 — `version.res` declaraba la versión de PackageMaker en todos
  los proyectos:** la plantilla traía `FILEVERSION 5,15,3,0` y
  `PRODUCTVERSION 5,15,3,0` fijos, así que cualquier aplicación creada —por
  ejemplo con versión `2.4.1`— mostraba «Versión de archivo 5.15.3.0» en
  Windows, mientras `StringFileInfo` sí decía `2.4.1`. Ahora
  `build_variables()` publica `FILE_VERSION_NUMERIC`/`PRODUCT_VERSION_NUMERIC`
  mediante el nuevo `numeric_version()` (`1.0.0` → `1,0,0,0`, relleno a cuatro
  campos y límite de `WORD` a 65535) y `lib/projectFactory.create_version_res()`
  rellena las mismas variables en la ruta heredada. Reportado por
  JesusQuijada34 (auditoría interna).
- **R-8d4b1f63 — `create` descartaba el nombre visible (`--name`):** el CLI (y
  la pantalla de creación del TUI, que lo invoca) pasaba el *shortname* también
  como nombre visible, de modo que `details.xml` quedaba con
  `<name>demo</name>`, el README se titulaba `# demo`, el `ProductName` era
  «Influent demo …» y la cabecera `.iflapp` mostraba «App: demo (demo)». Ahora
  se usa el nombre indicado en `--name` (con el *shortname* como respaldo si
  viene vacío); la carpeta y el ejecutable siguen saliendo del *shortname*.
  Reportado por JesusQuijada34 (auditoría interna).
- **R-5a3e9d72 — los `autorun`/`autorun.bat` generados no lanzaban la
  aplicación:** ejecutaban `/usr/bin/python3 ./<app>.py`, una ruta que no
  existe en Termux, macOS o contenedores con otro prefijo, y un `.py` que el
  paquete no incluye (el artefacto es `<app>` o `<app>.pyz`). Además el guion se
  creaba con permisos `0644`, así que `./autorun` respondía «Permission
  denied». Las plantillas ahora se sitúan en su propio directorio y eligen, por
  orden, el binario nativo, el `.pyz` y el guion fuente (con `python3` o
  `python`); `_make_executable()` marca el `autorun` como ejecutable al crear y
  al reparar el proyecto. Reportado por JesusQuijada34 (auditoría interna).

Pruebas: `tests/test_project_template_metadata.py` (11 casos nuevos; los 11
fallan con el código anterior). Suite completa: 1161 pasan, 1 omitido, 64
subtests. `pyflakes` y `py_compile` limpios.

No se prepara release: siguen abiertos R-4f8a2c60 (pendiente de Q-008) y
R-6a1f8c23 (pendiente de Q-011), y el requisito de 7 días sin reportes nuevos
continúa en curso desde el 2026-11-22.

## 2026-11-25 — quincuagésimo ciclo

### Corregido — tres dependencias opcionales dejan de ser obligatorias

Sin reportes externos nuevos. Tres hallazgos de la auditoría interna, todos de
la misma familia: un `import` de una dependencia opcional en el nivel superior
(o dentro de un slot de Qt) impedía arrancar el programa antes de leer los
argumentos. Ningún cambio de comportamiento del engine: el formato de los
paquetes, la ley de nombres y las plantillas siguen exactamente igual.

- **R-7e2d9c14 — el CLI no arrancaba sin `requests`:** `packagemaker.py` hacía
  `import requests` en el nivel superior, aunque sólo se usa para descargar un
  icono por URL. En una máquina sin esa biblioteca, hasta `--app-version`
  terminaba en `ImportError`. Ahora el import está protegido
  (`requests = None`) y la descarga de iconos avisa con
  «requests no está instalado: no se puede descargar el icono» en vez de fallar
  con `AttributeError`. Reportado por JesusQuijada34 (auditoría interna).
- **R-3a8f6b25 — la consola del editor abortaba el proceso con comillas sin
  cerrar:** el campo de entrada de `pmCodeEditor` llama a `shlex.split`, que
  lanza `ValueError` con `pip install "paquete`. La excepción escapaba del slot
  `returnPressed` y PyQt6 abortaba el editor, perdiendo el trabajo sin guardar.
  `_execute_input` y `run_command` capturan el error y escriben
  «[ERROR] Comando no válido: …» en la consola; `run_command` devuelve `False`.
  Reportado por JesusQuijada34 (auditoría interna).
- **R-9d5c1e73 — el updater headless no arrancaba sin PyQt6:** `updater.py` y
  `lib/coreUpdater/workers.py` importaban PyQt6 sin respaldo, así que
  `--version`, `--check` y `--install --silent` fallaban en un servidor sin
  interfaz. Ahora el updater usa sustitutos inertes cuando falta Qt, el worker
  de instalación silenciosa se ejecuta de verdad y las rutas que exigen ventana
  responden «esta operación necesita PyQt6 … usa --silent» con código 1. Con
  PyQt6 instalado el comportamiento es idéntico. Reportado por
  JesusQuijada34 (auditoría interna).

Pruebas: `tests/test_cli_without_requests.py` (2 nuevas),
`tests/test_editor_console_command_parsing.py` (4 nuevas) y 6 casos nuevos en
`tests/test_updater_optional_dependencies.py`. Suite completa: 1150 pasan, 1
omitido, 64 subtests. `pyflakes` y `py_compile` limpios.

No se prepara release: siguen abiertos R-4f8a2c60 (pendiente de Q-008) y
R-6a1f8c23 (pendiente de Q-011), y el requisito de 7 días sin reportes nuevos
continúa en curso desde el 2026-11-22.

## 2026-11-25 — cuadragésimo noveno ciclo

### Corregido — los acentos vuelven a pasar la puerta estricta y el updater deja de lanzar tracebacks con metadatos no canónicos

Sin reportes externos nuevos. Tres hallazgos de la auditoría interna sobre la
validación previa a crear/compilar y sobre el actualizador. Ningún cambio de
comportamiento del engine: el nombre canónico, las plantillas y el contenido de
los paquetes siguen exactamente igual.

- **R-6f3a9d21 — un fabricante o nombre interno con acentos bloqueaba la
  creación y la compilación:** `lib/blindcubeEngine/build_validation.py`
  comparaba el texto tal cual con `^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$`, así que
  `Jesús`, `Ñandú` o `café` se rechazaban con «usa solo letras, números o
  guiones» aunque la ley de nombres los translitera a ASCII desde Q-002
  (`Jesús` → `Jesus`, `Ñandú` → `Nandu`). La puerta estricta juzgaba un valor
  distinto del que produce el formatter. Ahora valida
  `ProjectNameFormatter.transliterate(value)`: los segmentos realmente
  inválidos (`My Company.`, `a_b`, `in fluent`, `a/b`) siguen bloqueados y un
  valor compuesto sólo por marcas combinantes sigue contando como vacío.
  Reportado por JesusQuijada34 (auditoría interna).
- **R-9b4c7e52 — `updater.py --check`/`--silent` lanzaba `ValueError` con
  metadatos remotos no canónicos:** `_fR()` (`lib/coreUpdater/core.py`) pasaba
  la versión, el publisher y el app remotos a
  `ProjectNameFormatter.format_iflapp_filename()`, que lanza `ValueError` con
  una etiqueta como `1.0 beta` o un publisher como `My Company.`. La excepción
  escapaba del CLI y del `update_app()` silencioso. Ahora se registra
  `[WARN] Metadatos remotos no canónicos; se omite el .iflapp` y se devuelve
  `None`, que los llamadores ya interpretaban como «no hay paquete»; un nombre
  canónico produce exactamente la misma URL que antes. Reportado por
  JesusQuijada34 (auditoría interna).
- **R-2e8f4a17 — la sonda de URL del updater dejaba escapar errores de
  validación sin `requests`:** `_check_url_exists()` sólo capturaba
  `OSError`/`URLError` en el respaldo `urllib`. Una URL con acentos
  (`Jesús.iflapp`) lanzaba `UnicodeEncodeError` y una con espacios o un byte
  NUL `http.client.InvalidURL`. Ahora el respaldo captura
  `(OSError, ValueError, urllib.error.URLError, http.client.HTTPException)` y
  la rama de `requests` añade `ValueError`: una URL imposible se trata como
  «no existe», igual que un 404. Reportado por JesusQuijada34 (auditoría
  interna).

Registrado sin implementar (pendiente de aprobación en `CONFIRM.MD`):

- **Q-018 — el build del CLI no valida `details.xml`:** con
  `<version></version>`, `packagemaker.py --buildthis` termina con éxito,
  empaqueta `…v1.0-…` cayendo a `v1.0` en silencio y deja dentro del paquete un
  `details.xml` con la versión vacía. Es un cambio de comportamiento del
  comando, así que se pregunta si debe rechazar (`[ERROR]`, código 1) o sólo
  avisar.

Pruebas: `tests/test_build_validation_accents.py` (11 nuevas) y
`tests/test_updater_noncanonical_metadata.py` (9 nuevas); 16 de las 20 fallan
con el código anterior (comprobado con `git stash` de
`lib/blindcubeEngine/build_validation.py` y `lib/coreUpdater/core.py`). Suite
completa: 1138 pasan, 1 omitido, 64 subtests. `pyflakes` y `py_compile` limpios.

## 2026-11-25 — cuadragésimo octavo ciclo

### Corregido — el asistente ya avisa antes de sobrescribir un proyecto, los iconos SVG vuelven a dibujarse y la suite deja de tocar la configuración del usuario

Sin reportes externos nuevos. Tres hallazgos de la auditoría interna sobre el
diálogo de creación de proyectos, el gestor de iconos y el aislamiento de la
propia suite. Ningún cambio de comportamiento del engine: el nombre canónico,
las plantillas y el contenido de los paquetes siguen exactamente igual.

- **R-4f7a2c91 — crear un proyecto existente lo sobrescribía sin preguntar:**
  `_ejecutarCreacionProyecto` comprobaba `rutaBase/nombreProyecto` (el nombre
  libre del formulario) pero escribía en la carpeta canónica
  `Publisher.app.vX.x-YY.MM-HH.MM-Plataforma`. Las dos rutas nunca coinciden,
  así que el aviso «¿Deseas sobrescribirla?» no aparecía y se regeneraban el
  guion del usuario, `details.xml` y el resto de archivos. Ahora el nombre
  canónico y su marca temporal se calculan antes de la comprobación y el aviso
  usa esa misma ruta. Reportado por JesusQuijada34 (auditoría interna).
- **R-8b2d4e17 — todos los iconos del gestor se perdían y una instalación de
  solo lectura lo abortaba:** `lib/iconManager.py` importaba `QSvgRenderer`
  desde `PyQt6.QtSvgWidgets` (que sólo expone el widget), así que
  `PYQT6_AVAILABLE` quedaba en `False` y `load_svg()` devolvía `None` siempre;
  la tarjeta «Abrir con» se quedaba sin icono. Además el constructor creaba
  `assets/icons` sin protección y `Path.exists()` propagaba `PermissionError`
  con un padre inaccesible. Ahora el renderer se importa de `PyQt6.QtSvg` (con
  respaldo), el `mkdir` tolera `OSError` y las rutas se comprueban con
  `lib.file_ops.path_exists`. Reportado por JesusQuijada34 (auditoría interna).
- **R-5a9c3e72 — la suite escribía en el `data/pm.data` real y desviaba
  `BASE_DIR` a `/tmp`:** los tests que construyen la GUI guardaban ajustes en
  el almacén global, que al ejecutar `pytest` es el archivo real del usuario.
  El guardado dejaba `BASE_DIR` con la ruta temporal del test y un test
  posterior la persistía, de modo que el CLI creaba los proyectos dentro de
  `…/pytest-N/.../proyectos`. `tests/conftest.py` instala ahora un almacén en
  una carpeta temporal antes de importar `packagemaker`; la configuración real
  queda intacta. Reportado por JesusQuijada34 (auditoría interna).

Pruebas: `tests/test_create_project_overwrite_guard.py` (3 nuevas),
`tests/test_icon_manager_readonly.py` (5 nuevas) y
`tests/test_suite_store_isolation.py` (3 nuevas); 10 de las 11 fallan con el
código anterior (comprobado restaurando los tres archivos con `git checkout`).
Suite completa: 1118 pasan, 1 omitido, 64 subtests.

## 2026-11-25 — cuadragésimo séptimo ciclo

### Corregido — el updater silencioso ya no miente, la desinstalación de Python portable borra de verdad y el TUI sobrevive a una versión corta

Sin reportes externos nuevos. Tres hallazgos de la auditoría interna sobre el
actualizador en modo silencioso, el gestor de Python portable y el asistente de
creación de la TUI. Ningún cambio de comportamiento del engine: las ventanas de
actualización, el descubrimiento de instalaciones y el nombre canónico de los
proyectos siguen exactamente igual; sólo dejan de reportarse como éxito las
operaciones que no lo fueron.

- **R-2d5b8f41 — `updater.py --install --silent` daba por instalado un paquete
  corrupto:** `install_iflapp(..., silent=True)` ignoraba el resultado del
  worker, que captura la excepción y emite `finished(False, …)`; en modo
  silencioso nadie escucha esa señal. Un `.iflapp` ilegible terminaba con
  `OK: Instalación completada` y código de salida `0`. Igual en
  `_update_from_exe(..., silent=True)` con un setup que devolvía un código
  distinto de cero. Ahora los tres workers devuelven `True`/`False` y guardan el
  mensaje en `self.error`, y el instalador propaga el fallo. Reportado por
  JesusQuijada34 (auditoría interna).
- **R-9f3c1a72 — desinstalar un Python portable decía «desinstalado» sin
  borrar la carpeta:** `uninstall_version()` usaba
  `shutil.rmtree(..., ignore_errors=True)`, que descarta los errores y devolvía
  `True` con el árbol intacto, además de eliminar el registro de la instalación;
  `Path.exists()` sobre un padre inaccesible lanzaba `PermissionError` desde el
  slot de Qt. Ahora usa `lib.file_ops.remove_tree` (reintenta y confirma), sólo
  borra el registro si el borrado se verificó, no lanza con rutas ilegibles y
  el diálogo de intérpretes avisa del fallo con un `QMessageBox` en lugar de
  callarse. Reportado por JesusQuijada34 (auditoría interna).
- **R-6b8e4d25 — el TUI moría al crear un proyecto con versión de un solo
  componente:** tras un `create` correcto, `_screen_create` recalculaba el
  nombre con `version.split("-")[0]`; con `2` el formatter lanzaba `ValueError`
  y el TUI terminaba en traceback. Además pasaba publisher y slug en
  minúsculas, así que la ruta mostrada no coincidía con la carpeta real. Ahora
  usa `normalize_version_base` y los mismos valores que la CLI. Reportado por
  JesusQuijada34 (auditoría interna).

Pruebas: `tests/test_updater_silent_status.py` (4 nuevas),
`tests/test_python_portable_uninstall.py` (4 nuevas) y
`tests/test_tui_create_naming.py` (3 nuevas); 7 de ellas fallan con el código
anterior. Suite completa: 1107 pasan, 1 omitido, 64 subtests.

## 2026-11-25 — cuadragésimo sexto ciclo

### Corregido — traductor automático sin caídas ni congelaciones, y zipapp con la codificación declarada

Sin reportes externos nuevos. Tres hallazgos de la auditoría interna sobre la
ruta de traducción automática y sobre la detección del punto de entrada del
backend `zipapp`. Ningún cambio de comportamiento del engine: un guion UTF-8 se
lee igual que antes, las traducciones locales no cambian y la compilación sólo
recupera la clasificación correcta de los guiones con cookie de codificación.

- **R-7b2e9c41 — una respuesta no UTF-8 del traductor abortaba `tr()`:**
  `_auto_translate_google` no capturaba `UnicodeDecodeError` (cuerpo en
  latin-1 desde un portal cautivo o un proxy) ni `http.client.HTTPException`
  (cuerpo truncado), así que la excepción escapaba de `tr()` hasta el
  constructor de la ventana: con la interfaz en un idioma distinto de español,
  la aplicación no llegaba a abrirse. Ahora la captura es
  `(OSError, ValueError, TypeError, KeyError, IndexError,
  http.client.HTTPException)` y se devuelve el texto original. Reportado por
  JesusQuijada34 (auditoría interna).
- **R-4e8a1d63 — el traductor automático repetía el timeout en cada cadena:**
  cada `tr()` sin traducción local lanzaba una petición nueva y, sin red,
  pagaba hasta 8 s de timeout en el hilo de la interfaz (páginas con decenas de
  etiquetas quedaban congeladas y volvían a pagarlo al repintar). Ahora un
  fallo de transporte deja el par de idiomas en enfriamiento durante 60 s
  (`_AUTO_TRANSLATE_COOLDOWN_SECONDS`); cambiar de idioma lo borra y reintenta
  al momento, y una respuesta 200 con formato inesperado no activa el
  enfriamiento. Reportado por JesusQuijada34 (auditoría interna).
- **R-9c3f6a25 — un guion con codificación declarada perdía el `main` en
  zipapp:** `compilers._defines_main()` leía el guion con
  `read_text(encoding="utf-8")`, así que un proyecto guardado en ANSI (cookie
  `# -*- coding: cp1252 -*-`) no se podía decodificar y el backend concluía que
  no había `main()`: el `.pyz` se generaba con el punto de entrada de reserva.
  Ahora usa `read_python_source` (PEP 263), como el resto del motor. Reportado
  por JesusQuijada34 (auditoría interna).

Pruebas: `tests/test_i18n_translate_robustness.py` (8 nuevas) y
`tests/test_page_action_bar_and_compilers.py` (2 nuevas); 7 de ellas fallan con
el código anterior. Suite completa: 1096 pasan, 1 omitido, 64 subtests.

## 2026-11-24 — cuadragésimo quinto ciclo

### Corregido — rutas bloqueadas que aún escapaban de `pathlib`

Sin reportes externos nuevos. Tres hallazgos de la auditoría interna en la
familia de R-9e3b7a51, R-6f4b8a92 y R-8c4a1f62: comprobaciones con
`Path.is_file()`/`exists()`/`is_dir()` heredadas de antes del endurecimiento, y
un `OSError` sin traducir en el sandbox y en el removedor generado. En Python
3.13 esas llamadas propagan `PermissionError` cuando el directorio padre no es
accesible. Ningún cambio de comportamiento del engine: un proyecto legible, un
workspace accesible y una instalación normal se tratan exactamente igual.

- **R-7b4e2c19 — `--ide-scan`/IDE se negaba a escanear un proyecto con rutas
  ilegibles:** `lib/iflapp_ide.py` comprobaba `details.xml`,
  `config/settings.json`, el icono y la estructura con `pathlib` sin protección,
  y `read_details()` sólo capturaba `ET.ParseError`. Con `details.xml` sin
  permiso de lectura, el CLI respondía `[ERROR] [Errno 13] Permission denied`
  sin listar guiones y el panel del IDE no abría el proyecto. Ahora
  `read_details()` captura `(ET.ParseError, OSError)` y el escaneo usa
  `lib.file_ops` (`path_exists`, `path_is_file`, `path_is_dir`), que degradan a
  «no existe»: se listan los guiones y se usan metadatos por defecto. Reportado
  por JesusQuijada34 (auditoría interna).
- **R-3c9d5e21 — el sandbox dejaba escapar `PermissionError`:** `run()` sólo
  traducía `FileNotFoundError` y `TimeoutExpired`. Con un *workspace* que
  existe pero no es accesible, `subprocess.run(cwd=...)` lanzaba
  `PermissionError`, rompiendo el contrato de devolver siempre un
  `SandboxResult` y pudiendo abortar la `QThread` del build. Ahora
  `except OSError` devuelve código 126 (no ejecutable), igual que
  `mexf_debugger`; `run_and_verify_binary()` informa de un binario no accesible
  con `-1` en vez de lanzar. Reportado por JesusQuijada34 (auditoría interna).
- **R-8e1f6a24 — el removedor generado abortaba con un acceso directo o árbol
  bloqueado:** el `removeme.py` autónomo comprobaba los accesos directos con
  `Path.is_file()` y borraba con `unlink()`/`rmtree()` sin protección. Un
  acceso directo en una carpeta sin permisos o un árbol de instalación
  bloqueado lanzaba `PermissionError` con traceback (y en modo GUI podía
  abortar el removedor). Ahora los accesos directos ilegibles se omiten con
  aviso, el árbol se trata de forma defensiva y `main()` traduce `OSError` a
  código 1 sin traceback; `--silent` sigue sin ruido. Reportado por
  JesusQuijada34 (auditoría interna).

Pruebas: `tests/test_iflapp_ide.py` (3 nuevas), `tests/test_iflapp_dropper_sandbox.py`
(2 nuevas) y `tests/test_mexf_asksome.py` (2 nuevas); todas fallan con el código
anterior. Suite completa: 1086 pasan, 1 omitido, 64 subtests.

## 2026-11-24 — cuadragésimo cuarto ciclo

### Corregido — un `details.xml` ilegible ya no aborta MoonFix ni el dashboard

Sin reportes externos nuevos. Dos hallazgos de la auditoría interna, en la
familia de R-9e3b7a51 y R-6f4b8a92: `ET.parse()` protegido sólo contra
`ET.ParseError` cuando el archivo existe pero no se puede leer. En POSIX
permisos, en Windows un bloqueo exclusivo; en ambos casos el `PermissionError`
escapaba de un slot de Qt y PyQt6 abortaba el proceso. Ningún cambio de
comportamiento del engine: un `details.xml` legible se procesa exactamente
igual.

- **R-7a2c9e14 — el asistente MoonFix cae con `details.xml` ilegible:**
  `MoonFixWizard.create_project_page()` construye la página del proyecto dentro
  del `__init__` del diálogo. Si `details.xml` no se podía leer, la excepción
  subía desde la construcción y mataba la aplicación. Ahora captura también
  `OSError` y la página se crea con los valores por defecto; MoonFix puede
  regenerar el archivo desde las plantillas. Reportado por JesusQuijada34
  (auditoría interna).
- **R-8f3d1b62 — «Abrir proyecto» del dashboard cae con `details.xml`
  ilegible:** `DashboardWindow._open_as_pm_project()` hacía lo mismo en el slot
  del botón «Proyecto PackageMaker». Ahora captura `(ET.ParseError, OSError)` y,
  sin metadatos, cae al escaneo de guiones `.py`, que ya toleraba `OSError`.
  Reportado por JesusQuijada34 (auditoría interna).

Pruebas: `tests/test_gui_unreadable_paths.py` (2 nuevas; fallan con el código
anterior). Suite completa: 1079 pasan, 1 omitido, 64 subtests.

## 2026-11-24 — cuadragésimo tercer ciclo

### Corregido — un `.mexf` con `.nan`/`.inf` emitía JSON no válido

Sin reportes externos nuevos. Un hallazgo de auditoría interna en la misma
familia que R-7b3a9e58 y R-8d4c1e67: datos externos con números no finitos que
llegan a una salida JSON. Ningún cambio de comportamiento del engine: un
`.mexf` cuyos valores son finitos o de texto se procesa exactamente igual.

- **R-4c9e2b71 — `--shell-plan-json` y el `.mexf` canónico podían emitir
  `NaN`/`Infinity`:** `yaml.safe_load()` convierte `.nan`, `.inf` y `-.inf` en
  `float` no finitos, y el JSON legacy puede producirlos con `1e400`
  (decodifica a `inf`). `_json_safe()` los devolvía tal cual porque son
  `float`, así que `json.dumps()` los escribía como `NaN`/`Infinity`, que no
  son JSON válido (RFC 8259). Los consumidores estrictos (`jq`, `JSON.parse`)
  rechazaban la salida de `--shell-plan-json`, y el `.mexf` canónico que
  `--compile-mexf` incrusta en el `.asksome` quedaba con la misma marca. Ahora
  `_json_safe()` convierte los `float` no finitos a su texto (`"nan"`, `"inf"`,
  `"-inf"`), coherente con lo que ya hacía `plan_from_document()` con
  `environments`; el parseo del JSON legacy aplica la misma normalización que
  el YAML. Reportado por JesusQuijada34 (auditoría interna).

### Corregido — una ruta no textual en `pm.data` tumbaba el arranque

Otro hallazgo de la auditoría interna, en la misma familia que R-1f4a7c92 y
R-9c1e5b74: valores de `data/pm.data` con el tipo equivocado que llegaban a una
API del sistema antes de pintar la ventana. Sin cambios de comportamiento del
engine: una configuración válida se lee exactamente igual.

- **R-4a7f2c93 — `base_dir`/`fluthin_apps` como objeto, lista o número:** el
  `os.makedirs()` que `packagemaker.py` ejecuta al importarse recibía el valor
  tal cual y moría con `TypeError: expected str, bytes or os.PathLike object`.
  Una cadena con byte NUL lanzaba `ValueError: embedded null byte`, que el
  `except OSError` tampoco capturaba. Afectaba a la GUI y a cualquier acción del
  CLI. Ahora `pm_data.coerce_text()` filtra los valores no textuales,
  `load_merged_app_config()` repara las rutas corruptas con el valor por defecto
  y la migración desde `config/settings.json` ignora rutas no textuales; el
  `makedirs` de arranque captura también `TypeError`/`ValueError` como red
  final. Reportado por JesusQuijada34 (auditoría interna).

### Corregido — un `language` no textual abortaba el arranque

- **R-8d3e6b15 — `AttributeError: 'dict' object has no attribute 'lower'`:**
  el arranque pasaba `config["LANGUAGE"]` a `i18n.initialize()`, que hacía
  `lang.lower()`. Un idioma guardado como objeto, lista o número cerraba la
  aplicación antes de mostrar la ventana. `to_legacy_app_config()` devuelve
  ahora `"es"` para valores no textuales y `I18nManager.load_translation()`
  normaliza con `str()` y cae a `"es"` si el código no está en
  `SUPPORTED_LANGUAGES`. Reportado por JesusQuijada34 (auditoría interna).

### Corregido — un acento no hexadecimal abortaba las notificaciones

- **R-2f5c9a71 — `ValueError` al construir una notificación con acción
  `primary`:** `NotificationWidget._darken_color()` parseaba el acento con
  `int(valor[i:i+2], 16)` sin validar. Con un `custom_accent_color` que no era
  `#RRGGBB`, el botón «Copiar error» del reporte o «Ver detalles» de un fallo
  de compilación lanzaba `ValueError` dentro de un slot y PyQt6 abortaba el
  proceso. `design_tokens.normalize_accent()` valida el formato y lo aplican
  `active_accent()` y `packagemaker.get_accent_color()`; `_darken_color()`
  devuelve la entrada sin cambios si no es hexadecimal. Reportado por
  JesusQuijada34 (auditoría interna).

### Revisión de reportes e issues

- Sin reportes nuevos en `bugs.txt` ni en el issue #4 y sin pull requests
  abiertos.
- Bugs abiertos: **R-4f8a2c60** (splash, espera Q-008) y **R-6a1f8c23**
  (arrastre con la ventana maximizada, espera Q-011). No se han tocado: ambos
  son cambios de engine pendientes de aprobación.
- `CONFIRM.MD`: sin respuestas nuevas del propietario desde `0ac5457`. Las
  preguntas Q-004, Q-007, Q-008 y Q-011…Q-014 siguen pendientes.
- Hallazgo sin cambio de código: `--engine flatcube` sobrescribe el
  `--compiler` explícito con `pyinstaller` (`get_engine()` fuerza
  `engine.backend`). Es el backend declarado por el motor legacy; no se
  modifica sin aprobación y queda como observación, no como solicitud.

### Verificación

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 1077 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios.
- Pruebas nuevas del primer bloque: 3 (2 en `tests/test_mexf_shell.py` y 1 en
  `tests/test_mexf_asksome.py`); las 3 fallan con el código anterior
  (comprobado con `git checkout` de `lib/mexf_parser.py`).
- Reproducción real del primer bloque: `--shell-plan-json` con
  `shortcuts: {Ctrl+N: .nan}` y con el JSON legacy
  `{"shortcuts": {"Ctrl+O": 1e400}}` imprimía `NaN`/`Infinity`; ahora imprime
  `"nan"`/`"inf"` y un parser estricto lo acepta.
- Pruebas nuevas del segundo bloque: 31 en
  `tests/test_corrupt_user_config_startup.py`. Reproducción previa: un
  `data/pm.data` con `base_dir` como objeto daba `TypeError` en `os.makedirs`
  al importar `packagemaker`; `language` como objeto daba `AttributeError` en
  `i18n.load_translation`; `custom_accent_color: "azul"` daba `ValueError` al
  construir una notificación con acción `primary`. Tras el arreglo,
  `--app-version` arranca con la carpeta por defecto, el idioma cae a `es` y la
  notificación se construye sin error.
- No se prepara release: el periodo de observación sigue en curso y el
  requisito de 7 días sin reportes nuevos no se cumple.

## 2026-11-24 — cuadragésimo segundo ciclo

### Corregido — comandos `.mexf` con byte NUL y escalares YAML no JSON

Sin reportes externos nuevos. Dos hallazgos de auditoría interna en la misma
familia que el ciclo anterior: un `ValueError` de `subprocess` que escapaba del
depurador y un `TypeError` de `json.dumps` que escapaba de la compilación.
Ningún cambio de comportamiento del engine: un `.mexf` con comandos lanzables y
escalares JSON funciona exactamente igual.

- **R-3a7f2d84 — un comando `.mexf` con byte NUL lanzaba traceback en el
  depurador:** `default_runner()` traducía `FileNotFoundError` a 127,
  `TimeoutExpired` a 124 y `OSError` a 126, pero `subprocess` señala con
  `ValueError: embedded null byte` un `executable`, un argumento, un valor de
  entorno o un `cwd` con un byte NUL. Un `.mexf` puede declarar ese texto, así
  que `--debug-mexf --debug-run` mostraba el traceback completo y, desde el
  diálogo del editor (slot de Qt), PyQt6 abortaba el proceso. Ahora
  `default_runner()` captura también `ValueError` y devuelve 126 con el
  mensaje; el paso queda `failed` y el depurador continúa. Reportado por
  JesusQuijada34 (auditoría interna).
- **R-8d4c1e67 — un `.mexf` con escalares YAML no JSON lanzaba `TypeError` al
  compilar:** `yaml.safe_load()` produce fechas, `set`, `bytes` y tuplas, y
  permite alias recursivos; `parse_mexf()` los aceptaba y
  `canonicalize_mexf()` fallaba después con `TypeError: Object of type date is
  not JSON serializable` o `ValueError: Circular reference detected`.
  `--compile-mexf` mostraba el traceback porque sólo captura
  `MexfCompileError`/`OSError`, y en la GUI no se generaba el artefacto.
  Ahora `_json_safe()` normaliza el documento al leerlo y antes de
  serializarlo (fechas a ISO 8601, `set` a lista ordenada, `bytes` a base64,
  tuplas a listas, claves y tipos desconocidos a texto) y rechaza la recursión
  con `MexfError`. Reportado por JesusQuijada34 (auditoría interna).

### Revisión de reportes e issues

- Sin reportes nuevos en `bugs.txt` ni en el issue #4 y sin pull requests
  abiertos.
- Bugs abiertos: **R-4f8a2c60** (splash, espera Q-008) y **R-6a1f8c23**
  (arrastre con la ventana maximizada, espera Q-011). No se han tocado: ambos
  son cambios de engine pendientes de aprobación.
- `CONFIRM.MD`: sin respuestas nuevas del propietario desde `0ac5457`. Q-004,
  Q-007, Q-008 y Q-011…Q-014 siguen pendientes.

### Verificación

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 1043 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios.
- Pruebas nuevas: 7 (4 en `tests/test_mexf_asksome.py` y 3 en
  `tests/test_mexf_debugger.py`); las 7 fallan con el código anterior
  (comprobado con `git stash` de `lib/mexf_parser.py` y
  `lib/mexf_debugger.py`).
- Reproducción real: `--debug-mexf --debug-run` con `executable:
  "python\u0000x"` respondía `ValueError: embedded null byte`; ahora informa
  `[ failed] … 126`. Un `.mexf` con `released: 2024-01-01` abortaba
  `--compile-mexf` con `TypeError`; ahora genera el `.asksome`, y un alias
  recursivo responde `[ERROR] … referencia circular`.
- No se prepara release: el periodo de observación sigue en curso y el
  requisito de 7 días sin reportes nuevos no se cumple.

## 2026-11-24 — cuadragésimo primer ciclo

### Corregido — `.mexf` YAML con claves legacy y traductor automático

Sin reportes externos nuevos. Dos hallazgos de auditoría interna: una
excepción fuera del contrato del parser `.mexf` y un `TypeError` que escapaba
de un slot de Qt al cambiar de idioma. Ningún cambio de comportamiento del
engine: un `.mexf` YAML v1 válido y una traducción correcta funcionan
exactamente igual.

- **R-5d1c7a83 — un `.mexf` YAML con claves legacy lanzaba `JSONDecodeError`
  con traceback:** `detect_mexf_format()` clasificaba como `legacy-json`
  cualquier documento con `extensions`, `file_associations` o `context_menus`
  en la raíz, aunque el texto fuera YAML. `parse_mexf()` volvía a leer el
  archivo y lo pasaba a `json.loads()`, que lanzaba `JSONDecodeError`; como no
  es `MexfError` ni `OSError`, `--compile-mexf`, `--shell-plan` y
  `--debug-mexf` mostraban el traceback completo. Ahora la clasificación se
  hace sobre el texto ya leído (`_classify_mexf_text`), sólo es `legacy-json`
  el JSON real, y `parse_mexf()` traduce cualquier fallo del JSON a
  `MexfError`. Reportado por JesusQuijada34 (auditoría interna).
- **R-8c2f4b17 — una respuesta inesperada del traductor automático abortaba la
  interfaz:** `_auto_translate_google()` indexaba la respuesta (`payload[0]`,
  `p[0]`) sin validar su forma. Un portal cautivo o un proxy que contesta 200
  con `5`, `true`, `null` o listas de números provocaba `TypeError`, no
  capturado, dentro de `tr()`; en un slot de Qt eso cierra el proceso con
  `Fatal Python error: Aborted`. Ahora la respuesta debe ser la lista de
  segmentos esperada y, si no lo es, se devuelve el texto original. Reportado
  por JesusQuijada34 (auditoría interna).

### Revisión de reportes e issues

- Sin reportes nuevos en `bugs.txt` ni en el issue #4 y sin pull requests
  abiertos.
- Bugs abiertos: **R-4f8a2c60** (splash, espera Q-008) y **R-6a1f8c23**
  (arrastre con la ventana maximizada, espera Q-011). No se han tocado: ambos
  son cambios de engine pendientes de aprobación.
- `CONFIRM.MD`: sin respuestas nuevas del propietario desde `0ac5457`. Q-004,
  Q-007, Q-008 y Q-011…Q-014 siguen pendientes.

### Verificación

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 1036 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios.
- Pruebas nuevas: 12 (3 en `tests/test_mexf_asksome.py` y 9 en
  `tests/test_i18n_translate_robustness.py`); 8 de ellas fallan con el código
  anterior (comprobado con `git stash` de `lib/mexf_parser.py` y
  `lib/i18n.py`).
- Reproducción real: `--compile-mexf`, `--shell-plan` y `--debug-mexf` sobre un
  `.mexf` YAML con `extensions:` responden `[ERROR] … Formato .mexf
  desconocido` y código 1 (antes `JSONDecodeError` con traceback).
- No se prepara release: el periodo de observación sigue en curso y el
  requisito de 7 días sin reportes nuevos no se cumple.

## 2026-11-24 — cuadragésimo ciclo

### Corregido — tracebacks en `--build-removeme` y en el depurador `.mexf`

Sin reportes externos nuevos. Dos hallazgos de auditoría interna en la misma
familia que los ciclos anteriores: una comprobación de ruta sin proteger y un
`OSError` que escapaba del lanzador de comandos. Ningún cambio de comportamiento
del engine: con una instalación normal y un `.mexf` con comandos ejecutables
todo funciona exactamente igual.

- **R-9e1a4c72 — `--build-removeme` lanzaba traceback con una raíz de
  instalación ilegible:** `read_record()` llamaba a `Path.is_file()` sin
  protección y `pathlib` propaga `PermissionError` cuando el directorio padre no
  es accesible; el CLI sólo captura `AsksomeInstallError`, así que mostraba el
  traceback completo. Ahora el fallo se traduce a `AsksomeInstallError` con un
  mensaje legible y `compile_removeme_binary()` usa `path_is_file()` para
  conservar su contrato de devolver `None` cuando no puede compilar.
- **R-4c8b2e91 — un comando `.mexf` no ejecutable abortaba el depurador:**
  `default_runner()` sólo capturaba `FileNotFoundError` y `TimeoutExpired`.
  Un `executable` sin permiso de ejecución (o un `cwd` inaccesible) hacía que
  `subprocess.run()` lanzara `PermissionError` fuera del motor: el CLI
  `--debug-mexf --debug-run` mostraba un traceback y el botón de ejecución real
  del editor `.mexf` abortaba la app. Ahora devuelve `126` con el mensaje, el
  paso queda `failed` y el resto de la sesión de depuración continúa.

### Revisión de reportes e issues

- Sin reportes nuevos en `bugs.txt` ni en el issue #4 y sin pull requests
  abiertos.
- Bugs abiertos: **R-4f8a2c60** (splash, espera Q-008) y **R-6a1f8c23**
  (arrastre con la ventana maximizada, espera Q-011). No se han tocado: ambos
  son cambios de engine pendientes de aprobación.
- `CONFIRM.MD`: sin respuestas nuevas del propietario desde `0ac5457`. Q-004,
  Q-007, Q-008 y Q-011…Q-014 siguen pendientes.

### Verificación

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 1024 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios.
- Pruebas nuevas: 3 (`tests/test_mexf_asksome.py` y
  `tests/test_mexf_debugger.py`); las 3 fallan con el código anterior
  (comprobado con `git stash` de los dos módulos tocados).
- Reproducción real: `--build-removeme myapp --install-root <raíz 000>` muestra
  «No se pudo acceder al registro de instalación…» y código 1 (antes
  `PermissionError` con traceback); `--debug-mexf … --debug-run` con un
  `executable` `0644` informa «el comando … falló con código 126» (antes
  `PermissionError` con traceback).
- No se prepara release: el periodo de observación sigue en curso y el
  requisito de 7 días sin reportes nuevos no se cumple.

## 2026-11-24 — trigésimo noveno ciclo

### Corregido — depurador, `pm.data` y cabeceras con valores extremos

Sin reportes externos nuevos. Cuatro hallazgos de auditoría interna; dos
completan la familia PEP 263 del ciclo anterior y dos cierran huecos de
robustez ante JSON válido con números no finitos. Ningún cambio de
comportamiento del engine: un proyecto UTF-8 y un `pm.data`/paquete normal se
comportan exactamente igual que antes.

- **R-2a9f4d17 — el depurador rechazaba fuentes con declaración PEP 263:**
  `trace_script()` (base de `--ide-debug` y del depurador del IDE) leía con
  `encoding="utf-8"` fijo, así que un `app.py` en ANSI con su *coding cookie*
  daba `[ERROR] UnicodeDecodeError`. Ahora compila con `read_python_source()` y
  un fuente no decodificable se reporta como `SyntaxError` legible.
- **R-9c4d2f61 — el detector de dependencias del editor ignoraba PEP 263:**
  `DependencyChecker._detect_imports()` (pmCodeEditor) lanzaba
  `UnicodeDecodeError` dentro de la QThread y `_write_requirements_txt()` no
  podía leer un `requirements.txt` no UTF-8. Ahora usa `read_python_source()`
  (con escaneo tolerante si el fuente no es decodificable) y tolera
  `OSError`/`UnicodeDecodeError` al leer el archivo previo.
- **R-5e8c1b42 — `pm.data` con números no finitos impedía arrancar:**
  `coerce_int()`/`coerce_float()` no capturaban `OverflowError`. `1e400` es
  JSON válido y se decodifica como infinito, así que `"sidebar_accent_width":
  1e400` mataba el arranque de la GUI y `"card_opacity": 1e400` rompía el
  guardado de Configuración (`int(inf * 100)` en un slot). Las coerciones
  rechazan ahora los valores no finitos con `math.isfinite()` y conservan los
  enteros grandes legítimos.
- **R-7b3a9e58 — cabeceras `.iflapp`/`.run` con números no finitos:**
  `_require_int()` y `_read_section()` no capturaban `OverflowError`, así que
  una cabecera con `"size": 1e400` mostraba «cannot convert float infinity to
  integer» en vez de `IflappError`; `read_dropper_header()` además dejaba
  escapar el `OSError` del `.run`. Ambos traducen ahora a `IflappError`.

### Revisión de reportes e issues

- Sin reportes nuevos en `bugs.txt` ni en el issue #4 y sin pull requests
  abiertos.
- Bugs abiertos: **R-4f8a2c60** (splash, espera Q-008) y **R-6a1f8c23**
  (arrastre con la ventana maximizada, espera Q-011). No se han tocado: ambos
  son cambios de engine pendientes de aprobación.
- `CONFIRM.MD`: sin respuestas nuevas del propietario desde `0ac5457`. Q-004,
  Q-007, Q-008 y Q-011…Q-014 siguen pendientes.

### Verificación

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 1021 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios.
- Pruebas nuevas: 12 (7 en `tests/test_non_utf8_sources.py`, 2 en
  `tests/test_local_config_robustness.py`, 2 en `tests/test_iflapp_format.py`
  y 2 en `tests/test_iflapp_dropper_sandbox.py`); todas fallan con el código
  anterior (comprobado con `git stash` de los cinco módulos tocados).
- Reproducción real: `--ide-debug` sobre un `app.py` cp1252 traza el guion
  (antes `[ERROR] UnicodeDecodeError`); `read_iflapp_header()` sobre una
  cabecera con `1e400` devuelve `IflappError` (antes `OverflowError`).
- No se prepara release: el periodo de observación sigue en curso y el
  requisito de 7 días sin reportes nuevos no se cumple.

## 2026-11-24 — trigésimo octavo ciclo

### Corregido — proyectos con fuentes no UTF-8 (declaración PEP 263)

Sin reportes externos nuevos. Tres hallazgos de auditoría interna con la misma
causa raíz: el motor leía los guiones del proyecto con `encoding="utf-8"` fijo.
Python acepta fuentes en otra codificación si la primera o la segunda línea lo
declaran (`# -*- coding: cp1252 -*-`), así que un proyecto guardado por un
editor de Windows en ANSI era válido para Python y, sin embargo, rompía
PackageMaker: en la GUI abortaba el proceso y en el CLI imprimía un traceback.
Ningún cambio de comportamiento del engine: un proyecto UTF-8 se comporta
exactamente igual que antes.

- **R-3f8a7c21 — el IDE abortaba al abrir un proyecto en ANSI:**
  `IflappIdePanel._on_script_selected()` leía con `utf-8-sig` y sólo capturaba
  `OSError`; al cargar el proyecto, `_refresh_tree()` selecciona el primer guion
  y el `UnicodeDecodeError` escapaba del slot (PyQt6 aborta el proceso).
  `_declared_scripts()` repetía el problema con `config/settings.json` en ANSI.
  Ahora el editor lee con `read_python_source()` y, si el archivo no es fuente
  Python válida, limpia el editor y muestra `iflapp_ide.load_failed`;
  `settings.json` se lee con `utf-8-sig` (acepta el BOM del Bloc de notas).
- **R-9d2b6e45 — `--ide-compile` ignoraba la declaración de codificación:**
  `detect_hidden_imports()`, la inyección del bootloader
  (`prepare_for_build()`/`write_injected_copy()`/`inject_file()`) y el preflight
  (`check_syntax()`) leían en UTF-8 fijo, así que `compile_project()` propagaba
  `UnicodeDecodeError` y el CLI (que sólo captura `OSError`) lo imprimía como
  traceback. Ahora los cuatro puntos leen con `read_python_source()` y la copia
  inyectada se escribe **con la codificación original**, de modo que la *cookie*
  siga siendo válida; un archivo que no es fuente Python válida se degrada con
  un mensaje legible (sin imports ocultos, sin copia inyectada, preflight con el
  error de codificación) en vez de lanzar.
- **R-6c4a1f83 — blindaje y build fallaban con fuentes/`settings.json` no
  UTF-8:** `hardening.inject_anti_debug()` y `obfuscate_strings()` leían y
  reescribían en UTF-8 fijo (habrían dejado la *cookie* mintiendo);
  `BuildThread._load_explicit_scripts()` y `_persist_env_payload()` no
  capturaban `UnicodeDecodeError` al leer `settings.json`. Ambos métodos de
  blindaje usan ahora `read_python_source()` y escriben con la codificación
  detectada (o devuelven un `HardeningReport` no aplicado), y las dos lecturas
  de `settings.json` usan `utf-8-sig` con `UnicodeDecodeError` capturado.
- **Nuevo módulo** `lib/blindcubeEngine/source_io.py`:
  `read_python_source()` detecta la codificación como el propio intérprete
  (`tokenize.detect_encoding`) y `SourceEncodingError` distingue «no es fuente
  Python» de un `OSError`.

### Revisión de reportes e issues

- Sin reportes nuevos en `bugs.txt` ni en el issue #4 y sin pull requests
  abiertos.
- Bugs abiertos: **R-4f8a2c60** (splash, espera Q-008) y **R-6a1f8c23**
  (arrastre con la ventana maximizada, espera Q-011). No se han tocado: ambos
  son cambios de engine pendientes de aprobación.
- `CONFIRM.MD`: sin respuestas nuevas del propietario desde `0ac5457`. Q-004,
  Q-007, Q-008 y Q-011…Q-014 siguen pendientes.

### Verificación

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 1009 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios.
- Pruebas nuevas: 17 en `tests/test_non_utf8_sources.py`; 11 fallan con el
  código anterior y la prueba del panel del IDE aborta el proceso (comprobado
  con `git stash` de los seis módulos tocados).
- Reproducción real: `--ide-scan --ide-scan-json` y `--ide-compile
  --ide-backend zipapp` sobre un proyecto con `app.py` y `settings.json` en
  cp1252 terminan con código 0 y generan el `.pyz` (antes
  `UnicodeDecodeError`); la copia `<guion>_pmboot.py` conserva la *cookie* y el
  acento del fuente.
- No se prepara release: el periodo de observación sigue en curso y el
  requisito de 7 días sin reportes nuevos no se cumple.

## 2026-11-24 — trigésimo séptimo ciclo

### Corregido — la GUI y la TUI dejan de abortar ante rutas inaccesibles

Sin reportes externos nuevos. Tres hallazgos de auditoría interna sobre puntos
de entrada que ejecutaban comprobaciones del sistema de archivos (o el
lanzamiento de un programa externo) fuera de cualquier `try`. PyQt6 aborta el
proceso ante una excepción no capturada en un slot o en `QThread.run`, así que
el fallo se veía como un cierre sin mensaje. Ningún cambio de comportamiento del
engine: el camino feliz produce el mismo artefacto.

- **R-6f4b8a92 — empaquetar un proyecto inaccesible abortaba la GUI:** al pulsar
  BlindCube sobre una carpeta cuyo padre no es accesible, `find_env_file()`
  (`Path.is_file()`) lanzaba `PermissionError` dentro del slot del botón y
  `BuildThread.run()` lo hacía en `repo_path.exists()`, antes del `try` que
  traduce errores. `app_icon_for()` repetía la comprobación sin proteger. Ahora
  `find_env_file()`/`app_icon_for()` degradan a «sin `.env`»/«sin icono» y
  `BuildThread.run()` envuelve la ruta personalizada y la preflight para emitir
  la señal `error` con la causa.
- **R-1e7c3d58 — «Ejecutar» del gestor caía con una carpeta ilegible:**
  `ProjectDetailsDialog._run_installed_app()` listaba con `os.listdir()` y
  lanzaba con `subprocess.Popen()` sin `try/except`; una carpeta `chmod 000` o
  un ejecutable desaparecido escapaba del slot. El bloque completo traduce ahora
  `OSError` a un aviso `manager.error_status`.
- **R-9b5f2a74 — «Abrir carpeta» de la TUI caía sin `xdg-open`:** el
  `subprocess.Popen(["xdg-open", …])` (o `open`/`os.startfile`) no estaba
  protegido, así que un sistema mínimo terminaba en `FileNotFoundError` con
  traceback. La resolución y el lanzamiento van dentro de `try/except OSError`
  y muestran `manager.open_folder_failed_title` con la causa.

### Revisión de reportes e issues

- Sin reportes nuevos en `bugs.txt` ni en el issue #4 y sin pull requests
  abiertos.
- Bugs abiertos: **R-4f8a2c60** (splash, espera Q-008) y **R-6a1f8c23**
  (arrastre con la ventana maximizada, espera Q-011). No se han tocado: ambos
  son cambios de engine pendientes de aprobación.
- `CONFIRM.MD`: sin respuestas nuevas del propietario desde `0ac5457`. Q-004,
  Q-007, Q-008 y Q-011…Q-014 siguen pendientes.

### Verificación

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 992 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios.
- Pruebas nuevas: 6 en `tests/test_unreadable_build_and_launch.py`; 5 de ellas
  fallan con el código anterior (comprobado con `git stash`).
- Build real `create` + `--buildthis --compiler zipapp --no-sandbox`: `.iflapp`
  de 21 archivos, `verify_iflapp() → valid: True`.
- No se prepara release: el periodo de observación sigue en curso y el
  requisito de 7 días sin reportes nuevos no se cumple.

## 2026-11-24 — trigésimo sexto ciclo

### Corregido — el CLI ya no muestra tracebacks ante carpetas sin permisos

Sin reportes externos nuevos. Tres hallazgos de auditoría interna sobre las
acciones headless de creación, reparación y compilación. Ningún cambio de
comportamiento del engine: el camino feliz produce el mismo artefacto.

- **R-4a7e2c91 — `create` lanzaba traceback con una carpeta base sin permisos:**
  el subcomando headless llamaba a `create_project_from_templates()` sin
  proteger el sistema de archivos. Con `BASE_DIR` en una carpeta sin permiso de
  escritura, `project_path.mkdir()` propagaba `PermissionError` y el CLI moría
  con traceback. Ahora la creación y la copia del icono por defecto van dentro
  de un `try/except OSError` que imprime
  `[ERROR] No se pudo crear el proyecto en …` y sale con código 1.
- **R-6c9d3f52 — `moonfix`/`repair` lanzaban traceback con un proyecto de solo
  lectura:** el manejador sólo traducía `ValueError`. Si al proyecto le faltaba
  una subcarpeta del contrato (`docs/`, marcadores `.container`) y la raíz era
  de solo lectura, `folder_path.mkdir()` lanzaba `PermissionError` sin
  traducción. El asistente MoonFix de la GUI ya estaba protegido (R-7d2f8b14);
  el CLI no. Se añade `except OSError` con
  `[ERROR] No se pudo reparar el proyecto …` y salida 1.
- **R-8e2b7d64 — `compile`/`--buildthis` lanzaban traceback con `dist/`
  bloqueado:** los dos bloques headless sólo tenían `try/finally`, sin
  `except`. Un proyecto de solo lectura hacía fallar `dist_dir.mkdir()` dentro
  de `FlangCompiler._compile_binary()` y el `PermissionError` escapaba como
  traceback; en la GUI la QThread lo reducía a un «Error inesperado» sin
  indicar el directorio. `_compile_binary()` protege ahora la preparación del
  árbol, la lectura de `details.xml`/`lib/` y la creación de `dist/` y
  temporales, devolviendo `False` con `last_error` legible. Los dos bloques del
  CLI añaden `except OSError` con
  `[ERROR] La compilación falló por un problema del sistema de archivos: …` y
  código 1.

### Revisión de reportes e issues

- Sin reportes nuevos en `bugs.txt` ni en el issue #4 y sin pull requests
  abiertos.
- Bugs abiertos: **R-4f8a2c60** (splash, espera Q-008) y **R-6a1f8c23**
  (arrastre con la ventana maximizada, espera Q-011). No se han tocado: ambos
  son cambios de engine pendientes de aprobación.
- `CONFIRM.MD`: sin respuestas nuevas del propietario desde `0ac5457`. Q-004,
  Q-007, Q-008 y Q-011…Q-014 siguen pendientes.

### Verificación

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 986 pasan, 1
  omitido, 64 subtests; `pyflakes` y `py_compile` limpios.
- Pruebas nuevas: 5 en `tests/test_unreadable_paths.py`; las 5 fallan con el
  código anterior (comprobado con `git stash`).
- Build real `create` + `--buildthis --compiler zipapp --no-sandbox`: `.iflapp`
  de 20 archivos, `verify_iflapp() → valid: True`.

## 2026-11-24 — trigésimo quinto ciclo

### Corregido — instalación/desinstalación `.asksome` con carpetas sin permisos

Sin reportes externos nuevos. Tres hallazgos de auditoría interna sobre la ruta
de instalación y desinstalación de `.asksome` y sobre la limpieza del build.
Ningún cambio de comportamiento del engine.

- **R-3f7c1a94 — una carpeta de accesos directos no escribible abortaba
  `--install-asksome`:** `create_shortcuts()` documenta que devuelve sólo los
  accesos que se pudieron crear, pero `_write_linux_desktop()` y
  `_write_windows_shortcut()` sólo protegían `mkdir()`. Con
  `~/.local/share/applications` existente y sin permiso de escritura (instalación
  del sistema, HOME inmutable, contenedor), `entry.write_text()` lanzaba
  `PermissionError` **después** de extraer el payload: instalación a medias y
  traceback en el CLI. Ahora la escritura y el `chmod` del acceso se toleran y
  se devuelve `None`.
- **R-6b2e9d47 — `uninstall_asksome` filtraba `PermissionError`/`OSError`
  crudos:** `target.is_dir()`, `record_path.is_file()`,
  `shortcut_path.is_file()`/`unlink()` y `shutil.rmtree()` no estaban
  protegidos, así que `--uninstall-asksome` moría con traceback cuando la raíz
  de instalación no era accesible o un fichero estaba bloqueado. Ahora la
  comprobación se traduce a `AsksomeInstallError`, los accesos directos
  bloqueados se omiten sin abortar la purga, el árbol se borra con
  `remove_tree()` y, si sobrevive, se informa de la ruta. `build_removeme()`
  traduce también sus dos escrituras.
- **R-8c4a1f62 — `remove_tree` informaba de un borrado que no ocurrió:**
  `shutil.rmtree()` con `onexc` no lanza cuando el callback consume el error,
  de modo que `_clear_readonly()` se tragaba los fallos, `_retry()` nunca veía
  el bloqueo (los reintentos de `WinError 32` de R-4a1e7b93 no se ejecutaban) y
  `remove_tree()` devolvía `True` con el árbol intacto. Ahora el callback
  propaga el fallo conservando los bits del `chmod`, y `remove_tree()` confirma
  que el árbol ya no existe antes de devolver `True`.

### Revisión de reportes e issues

- Sin reportes nuevos en `bugs.txt` ni en el issue #4 (el último comentario
  sigue siendo el del ciclo anterior) y sin pull requests abiertos.
- Bugs pendientes que no se tocan por depender de aprobación en `CONFIRM.MD`:
  **R-4f8a2c60** (splash, espera Q-008) y **R-6a1f8c23** (arrastre con la
  ventana maximizada, espera Q-011).
- `CONFIRM.MD`: sin respuestas nuevas del propietario (el último commit que
  toca el archivo es de `openhands-agent`); Q-004, Q-007, Q-008 y
  Q-011…Q-014 siguen pendientes.

### Verificación — trigésimo quinto ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 981 pasan, 1 omitido,
  64 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Pruebas nuevas: 6 (5 en `tests/test_mexf_asksome.py` y 1 en
  `tests/test_engine_isolation.py`).
- Reproducción real por CLI: `--install-asksome` con
  `~/.local/share/applications` en `chmod 555` terminaba en `PermissionError`;
  ahora instala y omite el acceso directo. `--uninstall-asksome` con la raíz en
  `chmod 000` terminaba en traceback; ahora responde
  `[ERROR] Desinstalación .asksome fallida: No se pudo acceder a …`.

## 2026-11-23 — trigésimo cuarto ciclo

### Corregido — el compilador `.mexf` filtraba `PermissionError` crudo

Sin reportes externos nuevos. Un hallazgo de auditoría interna, continuación de
la familia de R-6d2f8a41: aquel ciclo protegió el parseo de `details.xml` y de
los `.mexf`, pero no las comprobaciones de existencia. En Python 3.13
`Path.is_file()`/`is_dir()` propagan `PermissionError` cuando el directorio
padre no es accesible. Ningún cambio de comportamiento del engine.

- **R-4b9e2c71 — `.mexf` con raíz o carpeta `app/` ilegible filtraba
  `PermissionError` crudo:** `read_project_details()`, `compile_mexf_project()`
  y `MexfCompiler.run()` dejaban escapar `PermissionError` en lugar de
  `MexfCompileError`, y `MexfCompiler.run()` incumplía su contrato (devolver
  `None` y rellenar `last_error`). El paso opcional `.mexf` del build abortaba
  el `FlangCompiler` completo en vez de omitirse, y una carpeta `app/` ilegible
  abortaba el empaquetado aunque el icono es opcional. Ahora `is_file()`/`is_dir()`
  se traducen a `MexfCompileError`/`[WARN]`, `_find_project_icon()` tolera
  `OSError` y `MexfCompiler.run()` captura `(MexfCompileError, OSError)`.

### Revisión de reportes e issues

- Sin reportes nuevos en `bugs.txt` ni en el issue #4 (el último comentario
  sigue siendo el del ciclo anterior) y sin pull requests abiertos.
- Bugs pendientes que no se tocan por depender de aprobación en `CONFIRM.MD`:
  **R-4f8a2c60** (splash, espera Q-008) y **R-6a1f8c23** (arrastre con la
  ventana maximizada, espera Q-011).
- `CONFIRM.MD`: sin respuestas nuevas del propietario; Q-004, Q-007, Q-008 y
  Q-011…Q-014 siguen pendientes.

### Verificación — trigésimo cuarto ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 975 pasan, 1 omitido,
  64 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Pruebas nuevas: 5 en `tests/test_unreadable_paths.py` (las 5 fallan con el
  código anterior, comprobado con `git stash` de `lib/mexf_compiler.py` y
  `lib/blindcubeEngine/BuildThread.py`).

## 2026-11-23 — trigésimo tercer ciclo

### Corregido — `PermissionError` en slots de GUI y en el splash

Sin reportes externos nuevos. Tres hallazgos de auditoría interna de la misma
familia que los ciclos 23 y 29–32: en Python 3.13 las comprobaciones de rutas y
las escrituras propagan `PermissionError` cuando el proyecto o el directorio de
trabajo no son accesibles. Dos de los fallos ocurrían dentro de slots de Qt, que
en PyQt6 terminan el proceso si la excepción escapa. Ningún cambio de
comportamiento del engine.

- **R-4e9c1a73 — el IDE `.iflapp` cerraba la aplicación al compilar un
  proyecto ilegible:** `IflappIdePanel.run_compile()` llamaba a
  `compile_project()` sin proteger el `OSError` de `scan_project()` (lectura de
  `details.xml`) o de la creación de `build/`. Ahora el fallo se muestra en la
  consola y en la barra de estado y el método devuelve `False`.
- **R-7d2f8b14 — MoonFix cerraba la aplicación con un proyecto de solo
  lectura:** `apply_project_fixes()` (invocado desde el slot `go_next()`)
  delegaba en `repair_project_from_templates()`, que crea carpetas y escribe
  plantillas. Ahora devuelve `bool`, captura `OSError`/`ValueError` y avisa con
  `LeviathanDialog`; el wizard no avanza si la reparación falla.
- **R-6b3e9c52 — el splash del paquete no arrancaba con un proyecto o `cwd` sin
  permisos:** `splash_bootloader._resolve_icon()` comprobaba los iconos con
  `Path.is_file()` sin protección. Ahora tolera `OSError`, devuelve `None` y el
  splash usa el acento del sistema; el módulo sigue siendo autocontenido (solo
  stdlib + PyQt6).

### Revisión de reportes e issues

- Sin reportes nuevos en `bugs.txt` ni en el issue #4: el último comentario
  sigue siendo el del ciclo anterior (2026-11-23T18:12Z) y no hay pull requests
  abiertos.
- Bugs pendientes que no se tocan: **R-4f8a2c60** (splash, espera Q-008) y
  **R-6a1f8c23** (arrastre con la ventana maximizada, espera Q-011).

### Verificación — trigésimo tercer ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 970 pasan, 1 omitido,
  64 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Pruebas nuevas: 3 (`tests/test_gui_unreadable_paths.py` ×2 y
  `tests/test_splash_bootloader_injection.py` ×1). Los 3 casos fallan con el
  código anterior (comprobado con `git stash` de `lib/iflapp_ide_dialog.py`,
  `lib/moonFixWizard.py` y `lib/blindcubeEngine/splash_bootloader.py`).

### Aprobaciones — `CONFIRM.MD`

- Revisado: no hay respuestas nuevas del propietario. Q-004, Q-007, Q-008 y
  Q-011…Q-014 siguen pendientes; no se aplicó ninguna mejora ni cambio de
  engine.

## 2026-11-23 — trigésimo segundo ciclo

### Corregido — rutas de configuración ilegibles (caché de sesión y build)

Sin reportes externos nuevos. Tres hallazgos de auditoría interna de la misma
familia que los ciclos 23, 29, 30 y 31: en Python 3.13 `Path.is_file()`
propaga `PermissionError` cuando el directorio padre no es accesible. Ningún
cambio de comportamiento del engine.

- **R-7e4c1a92 — el arranque caía si `data/` impedía leer la caché de
  sesión:** `session_cache.load_session()` comprobaba `data/session.cache` con
  `Path.is_file()` fuera de un `try`. Se invoca en el arranque desde
  `github_identity.restore_cached_session()`, `has_cached_session()` y
  `load_token()` dentro de `start_session_gate()`, así que un `data/` ilegible
  abortaba la decisión entre landing e IDE. Ahora la comprobación y la lectura
  se envuelven en `try/except OSError` y sin caché se devuelve `None`.
- **R-2d8b6f31 — `compile`/`--buildthis` lanzaban traceback con `config/` del
  proyecto ilegible:** `FlangCompiler.__init__` llama a
  `_load_scripts_to_compile()`, que comprobaba `config/settings.json` con
  `Path.is_file()` sin protección. El CLI construye el compilador fuera de un
  `try`, así que el fallo escapaba con `PermissionError`. Ahora se registra
  `last_error` y se devuelve una lista vacía, como cuando el archivo existe
  pero no se puede leer; el CLI responde `[ERROR] …` con código 1.
- **R-9a5c3e74 — «Abrir con» caía con `config/` de la aplicación ilegible:**
  `editorDetector.get_default_editor()` y `save_default_editor()` comprobaban
  `config/settings.json` con `Path.is_file()` sin protección. Con `config/`
  ilegible, abrir el diálogo o guardar la preferencia lanzaba
  `PermissionError` dentro de un slot de Qt. Ahora `get_default_editor()`
  devuelve `None` y `save_default_editor()` omite la lectura previa sin romper
  el slot.

### Revisión de reportes e issues

- Sin reportes nuevos en `bugs.txt` ni en el issue #4: el último comentario
  sigue siendo el del ciclo anterior (2026-11-23T16:17Z) y no hay pull requests
  abiertos.
- Bugs pendientes que no se tocan: **R-4f8a2c60** (splash, espera Q-008) y
  **R-6a1f8c23** (arrastre con la ventana maximizada, espera Q-011).

### Verificación — trigésimo segundo ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 967 pasan, 1 omitido,
  64 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Pruebas nuevas: `tests/test_unreadable_config_paths.py` (3). Los 3 casos
  fallan con el código anterior (comprobado con `git stash` de
  `lib/session_cache.py`, `lib/blindcubeEngine/BuildThread.py` y
  `lib/.walkcube/editorDetector.py`). Reproducción real: `--buildthis` sobre un
  proyecto con `config/` `chmod 000` terminaba en `PermissionError` con
  traceback; ahora responde `[ERROR] No se pudo leer config/settings.json: …`
  con código 1.

### Aprobaciones — `CONFIRM.MD`

- Revisado: no hay respuestas nuevas del propietario. El último commit que toca
  el archivo es `b25d7d4` (openhands, trigésimo primer ciclo); la última
  respuesta del propietario sigue siendo `0ac5457`. Q-004, Q-007, Q-008 y
  Q-011…Q-014 siguen pendientes. No se aplicó ninguna mejora ni cambio de
  engine sin aprobación.

### Release — no preparado

- El último reporte externo sigue siendo del 2026-11-22 (`bugs.txt`), así que
  el requisito de 7 días sin reportes nuevos y el periodo de observación de 3
  días siguen en curso. No se generaron `flat cube` ni `blind cube`.

## 2026-11-23 — trigésimo primer ciclo

### Corregido — robustez de arranque, GUI y salida en Termux

Sin reportes externos nuevos. Tres hallazgos de auditoría interna de la misma
familia que los ciclos 23, 29 y 30: en Python 3.13 `Path.exists()`, `is_file()`
e `is_dir()` propagan `PermissionError` cuando el directorio padre no es
accesible. Ningún cambio de comportamiento del engine.

- **R-4d8a6c12 — el arranque caía si `data/` no se podía crear o leer:**
  `_data_dir()` creaba `data/` con `mkdir()` sin protección y
  `PMDataStore.load()` usaba `Path.is_file()` y `load_merged_app_config()`
  hacía lo propio con `config/settings.json`. En una instalación de solo
  lectura sin `data/`, o con `data/`/`config/` ilegibles, `get_pm_data()`
  abortaba al resolver el acento o el idioma. Ahora `_data_dir()` degrada con
  un `except OSError`, `load()`, `_detect_app_version()` y
  `load_merged_app_config()` usan `path_is_file()` y `save()` sigue
  devolviendo `False` sin lanzar.
- **R-9e3b7a51 — acciones de GUI con rutas sin permisos:** el asistente de
  nuevo proyecto (`create_project`), la selección de guion del IDE
  (`_on_script_selected`) y `ProjectConfig.__init__`/`get_config` comprobaban
  rutas del usuario dentro de slots de Qt. Una carpeta base `chmod 000` o un
  guion ilegible terminaban en traceback. Se usa `path_exists()` en el
  asistente y en las carpetas por defecto de los diálogos, la lectura del guion
  se protege con `try/except OSError` (aviso `iflapp_ide.load_failed`) y
  `ProjectConfig` tolera una base no escribible.
- **R-6a2d8f43 — Termux sin almacenamiento compartido:**
  `compile_output_directory()` comprobaba `~/storage/downloads` con
  `Path.is_dir()`; sin `termux-setup-storage` esa ruta está bajo un padre
  inaccesible y el CLI abortaba. Ahora usa `os.path.isdir()` y mantiene
  `/storage/emulated/0/Download` como respaldo.

### Revisión de reportes e issues

- Sin reportes nuevos en `bugs.txt` ni en el issue #4: el último comentario
  sigue siendo el del ciclo anterior (2026-11-23T14:14Z) y no hay pull requests
  abiertos.
- Bugs pendientes que no se tocan: **R-4f8a2c60** (splash, espera Q-008) y
  **R-6a1f8c23** (arrastre con la ventana maximizada, espera Q-011).

### Verificación — trigésimo primer ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 964 pasan, 1 omitido,
  64 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Pruebas nuevas: `tests/test_pm_data_readonly_startup.py` (4),
  `tests/test_gui_unreadable_paths.py` (3) y
  `tests/test_platform_detect_storage.py` (2). Con el código anterior fallan 7
  de las 9 (comprobado con `git stash` de los cinco módulos).

### Aprobaciones — `CONFIRM.MD`

- Revisado: no hay respuestas nuevas del propietario. El último commit que toca
  el archivo es `a11f6e8` (openhands, trigésimo ciclo); la última respuesta del
  propietario sigue siendo `0ac5457`. Q-004, Q-007, Q-008 y Q-011…Q-014 siguen
  pendientes. No se aplicó ninguna mejora ni cambio de engine sin aprobación.

### Release — no preparado

- El último reporte externo sigue siendo del 2026-11-22 (`bugs.txt`), así que
  el requisito de 7 días sin reportes nuevos y el periodo de observación de 3
  días siguen en curso. No se generaron `flat cube` ni `blind cube`.

## 2026-11-23 — trigésimo ciclo

### Corregido — la TUI caía con rutas sin permisos

Sin reportes externos nuevos. Un hallazgo de auditoría interna de la misma
familia que los ciclos 23 y 29: en Python 3.13 `Path.exists()` propaga
`PermissionError` cuando el directorio padre no es accesible. Ningún cambio de
comportamiento del engine.

- **R-9a4c1e27 — una carpeta bloqueada cerraba la TUI con traceback:**
  `_screen_build()`, `_screen_moonfix()`, `_project_actions()`,
  `_show_details_xml()` y `_get_version()` comprobaban con `Path.exists()` las
  rutas escritas por el usuario o el directorio de trabajo. Con un proyecto
  `chmod 000` (o bajo un padre sin permiso) la excepción escapaba y terminaba
  la sesión de terminal. Se añade `_safe_exists()` en `lib/tui.py`, que traduce
  `OSError` a `False`, y todas esas comprobaciones lo usan. `_list_projects()`
  ignora las entradas cuyo `stat()` falla en lugar de abortar el listado.

### Revisión de reportes e issues

- Sin reportes nuevos en `bugs.txt` ni en el issue #4 desde el vigésimo noveno
  ciclo (último comentario: 2026-11-23T12:12Z).
- Sin pull requests abiertos. Sigue abierto solo el issue #4 (backlog).
- Bugs pendientes que no se tocan: **R-4f8a2c60** (splash, espera Q-008) y
  **R-6a1f8c23** (arrastre con la ventana maximizada, espera Q-011).

### Verificación — trigésimo ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 955 pasan, 1 omitido,
  64 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Pruebas nuevas: `tests/test_tui_unreadable_paths.py` (7). Con el código
  anterior fallan las 7 (comprobado con `git stash` de `lib/tui.py`).

### Aprobaciones — `CONFIRM.MD`

- Revisado: no hay respuestas nuevas del propietario desde `0ac5457`. El último
  commit que toca el archivo es `ffeef10` (openhands, vigésimo noveno ciclo).
  Q-004, Q-007, Q-008 y Q-011…Q-014 siguen pendientes. No se aplicó ninguna
  mejora ni cambio de engine sin aprobación.

### Release — no preparado

- El último reporte externo sigue siendo del 2026-11-22 (`bugs.txt`), así que
  el requisito de 7 días sin reportes nuevos y el periodo de observación de 3
  días siguen en curso. No se generaron `flat cube` ni `blind cube`.

## 2026-11-23 — vigésimo noveno ciclo

### Corregido — `data/pmCodeEditor` de solo lectura

Sin reportes externos nuevos. Dos hallazgos de auditoría interna que completan
la robustez frente a una instalación de solo lectura ya tratada en el ciclo
anterior para las cachés de fuentes y avatares. Ninguno cambia el
comportamiento del engine.

- **R-4a7c2e91 — el gestor de Python portable reventaba con `data` no
  escribible:** `PythonPortableManager.__init__` creaba
  `data/pmCodeEditor/packages` con `mkdir()` sin `try/except`, y esa carpeta no
  se distribuye en el repositorio. En una instalación de solo lectura
  (Program Files, AppImage, `/opt`), `pmCodeEditor.main()` →
  `resolve_python_path()` → `get_python_manager()` salía con `PermissionError`
  y los diálogos de intérprete lanzaban la excepción dentro de un slot de Qt.
  Ahora `_ensure_directories()` degrada con `[WARN]`, `_load_config()` usa
  `is_file()` dentro del `try`, `_discover_installations()` protege
  `iterdir()`/`is_dir()`, `_save_config()` devuelve `False` cuando no puede
  escribir, `_is_file()` centraliza la comprobación del intérprete,
  `_get_dir_size()` ignora entradas inaccesibles e `install_version()` informa
  del fallo al preparar el destino.
- **R-8f1d3b62 — guardar `editor_config.json` abortaba con `data` de solo
  lectura:** `DashboardWindow.save_config()` y
  `EditorWindow._save_editor_config()` hacían `mkdir()` + `open(..., "w")` sin
  `try/except`; se invocan al abrir un proyecto reciente y al aceptar el
  diálogo de intérpretes, así que un `OSError` subía desde un slot de Qt.
  Ambos guardados capturan `OSError`, avisan con `[WARN]` y devuelven `False`;
  `load_config()` y `_load_editor_config()` comprueban `is_file()` dentro del
  `try` (en Python 3.13 `exists()` propaga `PermissionError`).

### Revisión de reportes e issues

- Sin reportes nuevos en `bugs.txt` ni en el issue #4 desde el vigésimo octavo
  ciclo (último comentario: 2026-11-23T10:13Z).
- Sin pull requests abiertos. Sigue abierto solo el issue #4 (backlog).
- Bugs pendientes que no se tocan: **R-4f8a2c60** (splash, espera Q-008) y
  **R-6a1f8c23** (arrastre con la ventana maximizada, espera Q-011).

### Verificación — vigésimo noveno ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 948 pasan, 1 omitido,
  64 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Pruebas nuevas: `tests/test_readonly_data_dir_robustness.py` (6). Con el
  código anterior fallan 5 de las 6 (comprobado con `git stash` de
  `lib/python_portable_manager.py`, `lib/pm_dashboard.py` y `pmCodeEditor.py`).

### Aprobaciones — `CONFIRM.MD`

- Revisado: el último commit que toca el archivo es `38dea0b` (openhands,
  vigésimo séptimo ciclo) y no hay respuestas nuevas del propietario desde
  `0ac5457`. Q-004, Q-007, Q-008 y Q-011…Q-014 siguen pendientes. No se aplicó
  ninguna mejora ni cambio de engine sin aprobación.

### Release — no preparado

- El último reporte externo sigue siendo del 2026-11-22 (`bugs.txt`), así que
  el requisito de 7 días sin reportes nuevos y el periodo de observación no han
  terminado. No se generaron `flat cube` ni `blind cube`.

## 2026-11-23 — vigésimo octavo ciclo

### Corregido — cachés de solo lectura y respuestas de GitHub

Sin reportes externos nuevos. Dos hallazgos de auditoría interna de la misma
familia (una instalación cuyo directorio `data/` no se puede escribir), más la
validación de la respuesta de la API de GitHub. Ninguno cambia el
comportamiento del engine.

- **R-3b6f9d24 — una caché de fuentes de solo lectura tumbaba el CLI y la
  interfaz:** `cached_path()` creaba `data/fonts` como efecto secundario, así
  que `--list-fonts` y `--download-fonts` terminaban en `PermissionError` con
  traceback y el botón «Descargar fuentes» de Configuración abortaba la
  aplicación (`OSError` dentro de un slot de Qt). Ahora las consultas usan
  `font_cache_dir(create=False)`/`cached_path(..., create=False)`,
  `is_cached()`/`verify_file()`/`available_fonts_report()`/`load_cached_fonts()`
  y `ensure_fonts()` degradan a «ausente», `download_font()` comprueba la
  escritura antes de descargar, `write_license_notice()` devuelve `None` y el
  slot muestra el fallo en su etiqueta de estado en vez de cerrar el proceso.
- **R-9f4c2a71 — caché de avatares no escribible y respuestas de GitHub
  no-JSON:** `cache_avatar()`/`load_cached_avatar()` capturan `OSError` (el
  avatar es opcional), `_request()` separa la lectura del cuerpo del parseo y
  responde «GitHub devolvió una respuesta que no es JSON» ante un portal
  cautivo, y `_profile_from_payload()` exige un objeto en vez de fallar con
  `AttributeError`.

### Revisión de reportes e issues

- Sin reportes nuevos en `bugs.txt` ni en el issue #4 desde el vigésimo séptimo
  ciclo (último comentario: 2026-11-23T08:10Z).
- Sin pull requests abiertos. Sigue abierto solo el issue #4 (backlog).
- Bugs pendientes que no se tocan: **R-4f8a2c60** (splash, espera Q-008) y
  **R-6a1f8c23** (arrastre con la ventana maximizada, espera Q-011).

### Verificación — vigésimo octavo ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 942 pasan, 1 omitido,
  64 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Pruebas nuevas: `tests/test_font_cache_robustness.py` (9) y tres casos en
  `tests/test_github_identity.py`. Con el código anterior fallan 8 de las 9 del
  primer archivo y los 3 del segundo (comprobado con `git stash`).
- Build real `create` + `--buildthis --compiler zipapp --no-sandbox --dropper`:
  genera `.iflapp` y `.run`; `verify_iflapp()` → `valid: True` (20 archivos) y
  `--inspect` coincide con el `details.xml` interno.

### Aprobaciones — `CONFIRM.MD`

- Revisado: el último commit que toca el archivo es `38dea0b` (openhands,
  vigésimo séptimo ciclo) y no hay respuestas nuevas del propietario desde
  `0ac5457`. Q-004, Q-007, Q-008 y Q-011…Q-014 siguen pendientes. No se aplicó
  ninguna mejora ni cambio de engine sin aprobación.

### Release — no preparado

- El último reporte externo sigue siendo del 2026-11-23 (`bugs.txt`), así que
  el requisito de 7 días sin reportes nuevos y el periodo de observación no han
  terminado. No se generaron `flat cube` ni `blind cube`.

## 2026-11-23 — vigésimo séptimo ciclo

### Corregido — editor predeterminado, removedor generado y vista previa `.mexf`

Sin reportes externos nuevos. Tres hallazgos de auditoría interna, corregidos y
probados; ninguno cambia el comportamiento del engine.

- **R-2e7c4a91 — la preferencia de editor se guardaba dentro de `lib/` y un
  `settings.json` no-objeto rompía «Abrir con»:** `_config_file_path()` partía
  de `lib/.walkcube/` y resolvía `lib/config/settings.json`, fuera de la
  configuración canónica; en un ejecutable congelado el archivo caía en el
  bundle temporal y se perdía. Ahora apunta a `config/settings.json` de la raíz
  (o junto a `sys.executable` si está congelado). `get_default_editor()` y
  `save_default_editor()` exigen un objeto JSON: un archivo con `[]`, texto o
  número devuelve `None` al leer y se reescribe como objeto al guardar, sin
  `AttributeError`/`TypeError`.
- **R-8b4d1f62 — el removedor generado revienta si `install.json` no es un
  objeto:** `_shortcuts()` del stub `removeme.py` hacía `data.get()` sin
  comprobar el tipo; un registro con `[]`, texto o `{"shortcuts": 5}` detenía la
  desinstalación con traceback y dejaba la app instalada. Ahora sólo acepta un
  objeto con una lista en `shortcuts` y cae a los accesos directos incrustados
  en cualquier otro caso.
- **R-5c9a3e27 — metadatos `.mexf` ilegibles abortaban el diálogo de
  instalación:** la vista previa sólo capturaba `OSError`/`KeyError`, así que un
  `JSONDecodeError` o un JSON no-objeto escapaba al `except` exterior y cerraba
  el diálogo entero. El nuevo `_mexf_preview_metadata()` valida el objeto y
  devuelve `None`; el diálogo se abre igual y omite los detalles.

### Revisión de reportes e issues

- Sin reportes nuevos en `bugs.txt` ni en el issue #4 desde el vigésimo sexto
  ciclo (último comentario: 2026-11-23T06:23Z).
- Sin pull requests abiertos. Sigue abierto solo el issue #4 (backlog).
- Bugs pendientes que no se tocan: **R-4f8a2c60** (splash, espera Q-008) y
  **R-6a1f8c23** (arrastre con la ventana maximizada, espera Q-011).

### Verificación — vigésimo séptimo ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 930 pasan, 1 omitido,
  64 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Pruebas nuevas: `tests/test_config_and_removeme_robustness.py` (21). Con el
  código anterior fallan 17 de las 21 (comprobado con `git stash` de los tres
  archivos tocados); las 4 restantes cubren rutas y el camino válido que no
  cambiaban.

### Aprobaciones — `CONFIRM.MD`

- Revisado: el último commit que toca el archivo es `b5e269d` (openhands,
  vigésimo sexto ciclo) y no hay respuestas nuevas del propietario desde
  `0ac5457`. Q-004, Q-007, Q-008 y Q-011…Q-014 siguen pendientes. No se aplicó
  ninguna mejora ni cambio de engine sin aprobación.

### Release — no preparado

- El último reporte externo sigue siendo del 2026-11-23 (`bugs.txt`), así que
  el requisito de 7 días sin reportes nuevos y el periodo de observación no han
  terminado. No se generaron `flat cube` ni `blind cube`.

## 2026-11-23 — vigésimo sexto ciclo

### Corregido — el guardado de Configuración abortaba la aplicación y congelaba la ventana

Reportado por **JesusQuijada34** en `bugs.txt` («al maximizar o restaurar o al
cambiar opciones en configuración, porque se queda congelado un rato?»).
Registrados como **R-3c7a1e90** y **R-9e2b4d17**.

- **R-3c7a1e90 — una ruta de proyecto imposible cerraba la aplicación:** el
  guardado automático llamaba a `os.makedirs()` sin capturar `OSError`. Como el
  guardado corre dentro de un slot de PyQt6, escribir una carpeta que no se
  puede crear (unidad inexistente, ruta bajo un archivo, carpeta sin permisos)
  terminaba en `Fatal Python error: Aborted` sin mensaje. Ahora
  `ensure_config_directories()` crea y valida las dos carpetas antes de
  persistir; si falla, el guardado se cancela, la configuración anterior queda
  intacta y el aviso sale por el `Reporter` (barra de estado en el guardado
  automático, diálogo cuando el guardado es explícito).
- **R-9e2b4d17 — cada cambio repintaba el tema dos veces y reiniciaba el
  motor:** `_save_app_config_compact()` reaplicaba siempre
  `apply_ui_language()`, `_apply_leviathan_and_personalization()` y
  `apply_theme()`. Como la personalización ya termina en `apply_theme()`, el
  tema se repintaba dos veces por guardado, y `apply_ui_language()` volvía a
  poblar el selector de motores dejándolo en BlindCube. Ahora
  `settings_appearance_state()` captura sólo los valores visuales antes y
  después de guardar y `settings_reapply_plan()` decide qué reaplicar: nada si
  el cambio fue una ruta o un aviso, `apply_theme()` una sola vez si cambió un
  valor visual, la personalización si cambió el modo de presentación y la
  retraducción sólo cuando cambió el idioma.

### Registrado — pendientes y no reproducidos

- **R-6a1f8c23 — arrastrar la titlebar con la ventana maximizada la mueve:**
  `lib/window_manager_bridge._wire_titlebar()` llama a `startSystemMove()` sin
  comprobar el estado de la ventana; el manejador original de `lib/TitleBar.py`
  sí lo comprobaba. Cambia el ciclo de vida de la ventana (restaurar al
  arrastrar, maximizar al soltar arriba, ajuste a media pantalla), así que se
  acumula como **Q-011** y **no se ha modificado**.
- **R-4d8f2b61 — botón Guardar en Configuración:** no se reproduce. La pestaña
  Configuración no instala barra de acciones y `SettingsPanel` no tiene ningún
  botón «Guardar»; el guardado es automático. Se añade una prueba de regresión
  para que el botón no reaparezca.

### Registrado — cambios de engine pendientes

Se añaden a `bugs.md` y a `CONFIRM.MD` sin implementar: **Q-011** (ventana:
arrastre, maximizado y media pantalla), **Q-012** (tareas en segundo plano y
barra marquee en las barras de acción), **Q-013** (actualizaciones silenciosas
de parches de seguridad) y **Q-014** (eventos en el sidebar y temas de
temporada).

### Verificación — vigésimo sexto ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 909 pasan, 1 omitido,
  64 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Pruebas nuevas: `tests/test_settings_save_guards.py` (13). Las 13 fallan con
  el código anterior (comprobado con `git stash` de `packagemaker.py`) y la
  ejecución termina en `Fatal Python error: Aborted`, que es el cierre que
  sufría la aplicación.
- Medición real offscreen con la ventana construida (348 widgets): guardar sólo
  una ruta pasa de 0,20 s a 0,002 s; un cambio de densidad o de modo de
  presentación repinta el tema una vez (0,10 s) en lugar de dos; un cambio de
  idioma retraduce en 0,006 s; y la elección de FlatCube sobrevive al guardado.

### Aprobaciones — `CONFIRM.MD`

- Revisado: el último commit del archivo sigue siendo `0ac5457`
  (`JesusQuijada34 <jesusquijada34.gh@gmail.com>`, verificado con la API de
  GitHub) y no hay respuestas nuevas. Q-004, Q-007 y Q-008 siguen pendientes;
  se añaden Q-011, Q-012, Q-013 y Q-014. No se aplicó ninguna mejora ni cambio
  de engine sin aprobación.

### Release — no preparado

- El último reporte externo es del 2026-11-23 (`bugs.txt`), así que el
  requisito de 7 días sin reportes nuevos sigue en curso y el periodo de
  observación no ha terminado. No se generaron `flat cube` ni `blind cube`.

## 2026-11-23 — vigésimo quinto ciclo

### Corregido — el hover del sidebar parpadeaba y los iconos quedaban apretados

Reportado por **JesusQuijada34** en su respuesta a Q-010 de `CONFIRM.MD` (commit `0ac5457`). Registrado como **R-5b1d9e47**.

- **R-5b1d9e47 — el ítem de la barra lateral cambiaba de color a destiempo:** `_HoverFade` reescribía la hoja de estilo del ítem en cada fotograma. Cada `setStyleSheet()` fuerza un re-polish y, mientras se reevaluaba el estilo, se aplicaba la regla heredada `QWidget#NavigationSidebar QPushButton:hover` (y `:checked`, con borde de acento), de modo que el fondo saltaba entre el color de hover y el gris de reposo. Además, el fondo de selección del tema claro era un azul fijo `rgba(0, 120, 212, 0.18)` ajeno al acento configurado. Ahora `SidebarItem` pinta el resalte en `paintEvent` con la propiedad animada `hoverProgress` (una sola `QPropertyAnimation` reutilizada) sin tocar el QSS, su selector `QPushButton#SidebarNavItem[pmNavItem="true"]` se impone a la regla heredada, el fondo de selección se deriva del acento con `with_alpha()` y, al seleccionar un ítem, se retira el tinte de hover.
- **R-5b1d9e47 — iconos apretados:** el ancho por defecto de la barra lateral pasa de 260 a 270 px (`SIDEBAR_MAX_WIDTH`, `DEFAULT_USER["sidebar_width"]`) y el padding derecho del ítem de 10 a 14 px. Los perfiles con el valor heredado 260 se migran una sola vez (clave `sidebar_width_migrated`), sin tocar un ancho elegido a mano por el usuario.

### Añadido — mejoras aprobadas por el propietario

Aprobadas con `[x] SÍ` en `CONFIRM.MD` (commit `0ac5457`, autoría verificada con la API de GitHub).

- **R-d23039c0 (Q-001) — reporte de errores opcional:** nuevo `lib/errorReporter.py`. Sólo envía si `telemetry_enabled` es verdadero **y** `telemetry_endpoint` está configurado; lo hace en un hilo daemon con 5 s de límite. `sanitize()` sustituye la carpeta personal por `~`, cualquier ruta absoluta por `<path>` y los valores con pinta de credencial por `<redacted>`; nunca envía variables de entorno. `install_excepthook()` se encadena al hook original sin alterar su comportamiento y se instala en `main()`. Desactivado por defecto; documentado en `docs/privacy.md`.
- **R-5d8e2a41 (Q-002) — acentos en publisher y appname:** `ProjectNameFormatter.transliterate()` (NFKD sin marcas diacríticas) se aplica en `normalize_publisher()` y `normalize_app_id()`. `Jesús` → `Jesus`, `Ñandú Labs` → `Nandu-Labs`. El nombre canónico sigue siendo ASCII, así que la lectura de proyectos existentes no cambia.
- **R-4c8e1f27 (Q-003) — el publisher conserva su capitalización:** `handle_cli_action('create_project')`, `_ejecutarCreacionProyecto()`, `DashboardWindow`, la TUI y las acciones `compile`/`repair` dejan de forzar `.lower()` y pasan el publisher por `normalize_publisher()`. Los proyectos nuevos se llaman `Influent.demo.…` y su `details.xml` declara `<publisher>Influent</publisher>`; la búsqueda sigue sin distinguir mayúsculas, así que los proyectos antiguos se localizan igual.

### Reparado — canal de aprobación

- **R-7a3e1d92 — `CONFIRM.MD` tenía marcadores de conflicto de merge:** el bloque Q-008 contenía `<<<<<<< HEAD`/`=======`/`>>>>>>> 418c3e3` con dos respuestas contradictorias. Se reparó el archivo, se registraron las decisiones verificadas en `Historial` y Q-008 vuelve a `Pendientes` como pregunta única. `tests/test_confirm_channel.py` impide que vuelva a committearse con conflictos o con preguntas duplicadas.

### Registrado — bug pendiente de aprobación de engine

- **R-4f8a2c60 — splash simultáneo y avisos de ventana en Windows:** `IntegratedSplash` se crea con `parent=main_window` y `WA_TranslucentBackground`, y el efecto `WipeWindow` (ventana por capas) se aplica sobre un widget hijo; de ahí los avisos `QWidgetWindow(...) must be a top level window` y `UpdateLayeredWindowIndirect failed for ptDst=...`, y que el splash se dibuje a la vez que la ventana principal. Depende del cambio de engine Q-008, cuya respuesta quedó ambigua por el conflicto de merge, así que **no se ha tocado el ciclo de vida de ventanas**.

### Verificación — vigésimo quinto ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 892 pasan, 1 omitido, 64 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Pruebas nuevas: `tests/test_error_reporter.py` (6), `AccentTransliterationTests` (5), `AccentedPublisherCreateTests` (1), las cuatro de sidebar en `tests/test_hover_and_tokens.py` y `tests/test_confirm_channel.py`.
- Comprobación real offscreen: un `SidebarItem` dentro de un `QWidget#NavigationSidebar` pasa de `(40, 40, 40)` en reposo a `(55, 55, 55)` con `hoverProgress = 1.0`, sin reaplicar la hoja de estilo; `Jesús` + `Aplicación Demo` crea `Jesus.aplicacion-demo.…-Danenone` con `<publisher>Jesus</publisher>`; e `Influent` + `cwd-test` crea `Influent.cwd-test.…` con `<publisher>Influent</publisher>`.

### Aprobaciones — `CONFIRM.MD`

- `CONFIRM.MD` revisado (último commit del archivo: `0ac5457`, autor `JesusQuijada34 <jesusquijada34.gh@gmail.com>`, verificado con la API de GitHub). Aplicadas Q-001, Q-002 y Q-003; Q-005, Q-006, Q-009 y Q-010 quedan verificadas como ya implementadas. Q-004 se reenvía para aclaración (la respuesta mezcla una decisión delegada con una condición incompatible con el backend zipapp); Q-007 sigue sin marcar y Q-008 se repite porque su respuesta estaba partida por el conflicto.

### Release — no preparado

- El último reporte externo es del 2026-11-22 y este ciclo añade R-4f8a2c60, así que el requisito de 7 días sin reportes nuevos y el periodo de observación de 3 días siguen en curso. No se generaron `flat cube` ni `blind cube`.

## 2026-11-23

### Corregido — configuración y proyectos corruptos tumbaban el arranque

Hallazgo del vigésimo cuarto ciclo de mantenimiento (sin reporte externo; reportado por JesusQuijada34 en la auditoría interna). Commit `4e78f2e`.

- **R-9c1e5b74 — valores numéricos corruptos en `pm.data` impedían arrancar la GUI:** el panel de configuración, `apply_theme()`, el ancho inicial de la barra lateral y el aviso de reinicio convertían `sidebar_width`, `sidebar_accent_width`, `card_opacity`, `dpi_scale` y `applied_dpi_scale` con `int()`/`float()` directos. Como `data/pm.data` es editable a mano, un texto, una lista o `null` en esas claves lanzaba `ValueError`/`TypeError` al construir la ventana principal. `lib/pm_data.py` gana `coerce_int()`, `coerce_float()`, `PMDataStore.get_user_int()` y `get_user_float()`: aceptan números o texto numérico y caen al valor por defecto con cualquier otro tipo.
- **R-2b7d4a90 — `find_flarm_project()` revienta con la carpeta de proyectos ilegible o un `package_config.json` corrupto:** `pmCodeEditor` recorría `~/Documents/Packagemaker Projects` con `os.listdir()` sin capturar `OSError` y leía cada configuración capturando solo `(OSError, KeyError)`. Un JSON truncado (`JSONDecodeError`), un JSON que no era objeto (`AttributeError`) o un campo no textual (`.lower()` sobre un número) cortaban el arranque del editor con un traceback. Ahora la carpeta se lista una sola vez dentro de `try/except OSError`, la lectura captura `(OSError, ValueError)`, exige un objeto y normaliza los campos a texto.
- **R-5d8f1c36 — la depuración del editor `.mexf` lanzaba `yaml.YAMLError` dentro de un slot de Qt:** `MexfEditorDialog._document()` llamaba a `yaml.safe_load()` sin protegerlo. Con un documento a medio escribir, «Paso», «Continuar», «Detener» o el punto de ruptura provocaban una excepción no controlada y PyQt6 abortaba la aplicación. Ahora `_document()` captura `yaml.YAMLError` y devuelve un documento vacío; el lint sigue señalando el error y la depuración termina con «depuración finalizada».
- **R-8a2f6d51 — `uninstall_plan` (rama Windows) dejaba escapar `OSError`:** la rama Linux captura `OSError` por objetivo, pero la de Windows comprobaba `reg.exists()` y llamaba a `unlink()` fuera de todo `try`, rompiendo el contrato de la función. Ahora registra el motivo en `skipped`.

### Verificación — vigésimo cuarto ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 877 pasan, 1 omitido, 64 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Las pruebas nuevas fallan con el código anterior (18 fallos, comprobado revirtiendo los seis archivos fuente a `6a8a977`): `CoercionTests` (4), `SettingsPanelRobustnessTests` (5 subtests), `FindFlarmProjectTests` (5), el caso de YAML inválido del editor `.mexf` y el de `uninstall_plan` en Windows.
- Reproducción real (Python 3.13, `QT_QPA_PLATFORM=offscreen`): `SettingsPanel` con `sidebar_accent_width="tres"`/`card_opacity=None`/`[1]` lanzaba `ValueError`/`TypeError`; `find_flarm_project` con `{no es json`, `[1, 2]`, `{"titulo": 5}` o la carpeta en modo `000` lanzaba `JSONDecodeError`/`AttributeError`/`PermissionError`; los botones de depuración `.mexf` lanzaban `yaml.ParserError`; y `uninstall_plan(..., platform_name="win32")` con un directorio ilegible lanzaba `PermissionError`. Ahora todos degradan a valores por defecto, lista vacía, «depuración finalizada» o `skipped`.

### Aprobaciones — `CONFIRM.MD`

- `CONFIRM.MD` revisado (último commit del archivo: `6a8a977`, autor `openhands <openhands@all-hands.dev>` verificado con la API de GitHub): `Q-001`…`Q-010` siguen sin casillas marcadas, así que no hay respuestas válidas que aplicar. No se implementó ninguna mejora ni cambio de engine.

### Release — no preparado

- El último reporte externo sigue siendo el del propietario del 2026-11-22, de modo que el requisito de 7 días sin reportes nuevos y el periodo de observación de 3 días siguen en curso. No se generaron `flat cube` ni `blind cube`.

### Corregido — las rutas sin permisos terminaban en traceback

Hallazgo del vigésimo tercer ciclo de mantenimiento (sin reporte externo; reportado por JesusQuijada34 en la auditoría interna). Commit `743c914`.

En Python 3.13 `Path.exists()`, `Path.is_file()`, `Path.is_dir()` y `Path.iterdir()` propagan `PermissionError` cuando el directorio padre no es accesible. La CLI y la GUI comprobaban rutas del usuario con esas llamadas directas, así que un archivo o carpeta sin permisos rompía comandos que debían responder con un mensaje legible.

- **R-4c7a9e13 — `--inspect --inspect-extract` con un destino bloqueado:** `export_header_assets()` llamaba a `mkdir()`/`write_bytes()` fuera de todo `try`; un destino ocupado por un archivo normal lanzaba `FileExistsError` y uno sin permiso, `PermissionError`. Ahora la función traduce `OSError` a `IflappError` y el helper responde `[ERROR] …` con código 1 (en modo JSON el error va a stderr).
- **R-8e2b5c43 — `--list-asksome` con una raíz ilegible:** `list_installed()` recorría `root.iterdir()` sin capturar `OSError`. Ahora una raíz ilegible se trata como vacía y el CLI informa «Sin artefactos .asksome instalados» con código 0.
- **R-3d9f1a76 — `compile`/TUI con la carpeta base ilegible:** `iter_projects()`, `list_projects()`, `is_project_directory()` y `locate_project()` propagaban `PermissionError` desde `iterdir()`/`is_dir()`/`is_file()`. Ahora usan los envoltorios de `lib/file_ops.py` y el CLI responde `[ERROR] No se encontró proyecto que coincida con …`.
- **R-6c1e8b52 — `--buildthis`/`--ide-run`/`--shell-info` con rutas ilegibles:** las comprobaciones `Path.exists()`/`is_file()`/`is_dir()` se sustituyen por `path_exists()`/`path_is_file()`/`path_is_dir()`, con mensajes que distinguen «no existe» de «no es accesible».
- **R-7b3e9c28 — `--install-asksome` con un artefacto ilegible:** `artifact.is_file()` quedaba fuera del `try` y `_read_container()` no traducía `OSError`. Ahora la comprobación es segura y el lector lanza `AsksomeError` con la ruta y el motivo.
- **R-5a9d2f74 — abrir una carpeta genérica o lanzar MoonFix por lotes tumbaba la GUI:** `DashboardWindow._open_as_generic_project()` y `PackageTodoGUI.mf_start_scan()` llamaban a `os.listdir()` sin capturar `OSError`; en PyQt6 una excepción no controlada en un slot aborta la aplicación. Ahora el panel abre el editor sin guion y MoonFix muestra un diálogo de error.
- **R-2f8a4d61 — `remove_tree()` lanzaba `PermissionError` pese a prometer que no lanza:** usaba `Path.exists()` al empezar y al terminar. `_tree_exists()` emplea `os.lstat()` y distingue «no existe» de «no se puede comprobar»; `remove_tree()` devuelve `False` cuando no puede verificar el borrado.

`lib/file_ops.py` gana los envoltorios `path_exists()`, `path_is_file()`, `path_is_dir()` y `list_directory()`, que degradan un `OSError` a `False`/lista vacía y son la vía recomendada para rutas que vienen del usuario.

### Verificación — vigésimo tercer ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 865 pasan, 1 omitido, 55 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Las 14 pruebas nuevas de `tests/test_unreadable_paths.py` pasan; 13 de ellas fallan con el código anterior (comprobado con `git stash` de `lib/file_ops.py`, `lib/project_locator.py`, `lib/blindcubeEngine/asksome_installer.py`, `lib/blindcubeEngine/asksome_format.py`, `lib/blindcubeEngine/iflapp_format.py`, `lib/cliHandler.py`, `lib/pm_dashboard.py` y `packagemaker.py`).
- Reproducción real (Python 3.13, permisos POSIX): `--inspect … --inspect-extract <archivo>`, `--list-asksome --install-root <dir 000>`, `compile` con `BASE_DIR` `000`, `--buildthis <proyecto 000>`, `--ide-run <dir 000>/app.py`, `--shell-info <dir 000>/demo.asksome` y `--install-asksome <dir 000>/demo.asksome` terminaban en `PermissionError` con traceback; ahora responden con `[ERROR] …` y código 1, o con «Sin artefactos .asksome instalados» y código 0. Abrir una carpeta `000` como proyecto genérico o lanzar MoonFix por lotes sobre ella tumbaba la GUI; ahora no.

### Aprobaciones — `CONFIRM.MD`

- `CONFIRM.MD` revisado (último commit del archivo: `8a21a4f`, autor `openhands-agent` verificado con la API de GitHub): `Q-001`…`Q-010` siguen sin casillas marcadas, así que no hay respuestas válidas que aplicar. No se implementó ninguna mejora ni cambio de engine.

### Release — no preparado

- El último reporte externo sigue siendo el del propietario del 2026-11-22, de modo que el requisito de 7 días sin reportes nuevos y el periodo de observación de 3 días siguen en curso. No se generaron `flat cube` ni `blind cube`.

## 2026-11-22

### Corregido — `--compile-mexf` lanzaba traceback con entradas ilegibles

Hallazgo del vigésimo segundo ciclo de mantenimiento (sin reporte externo; reportado por JesusQuijada34 en la auditoría interna). Commit `f8ea814`.

- **R-6d2f8a41 — `--compile-mexf` no traducía los fallos del sistema de archivos:** `compile_mexf_project()` leía `details.xml` con `ET.parse()` y los módulos `.mexf` con `Path.read_text()` sin capturar `OSError`. Un `details.xml` sin permiso de lectura terminaba en `PermissionError`; un `.mexf/main.mexf` ilegible hacía lo propio desde `parse_mexf()`; y un directorio `.mexf/` sin permiso reventaba en `main.is_file()` dentro de `discover_mexf_modules()`. `MexfCompileHelper.compile()` solo capturaba `MexfCompileError`, de modo que el CLI mostraba un traceback. Ahora `parse_mexf()` traduce `OSError` a `MexfError`, `detect_mexf_format()` devuelve `"unknown"` cuando no puede leer, `read_project_details()` y `discover_mexf_modules()` convierten los fallos en `MexfCompileError`, y el helper del CLI responde `[ERROR] Compilación .mexf fallida: …` con código 1. Un proyecto legible sigue generando el `.asksome` firmado.

### Verificación — vigésimo segundo ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 851 pasan, 1 omitido, 55 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Las 5 pruebas nuevas de `tests/test_mexf_asksome.py` fallan con el código anterior (comprobado con `git stash` de `lib/mexf_parser.py`, `lib/mexf_compiler.py` y `lib/cliHandler.py`) y pasan con `f8ea814`.
- Reproducción real: `--compile-mexf` sobre un proyecto con `details.xml`, `.mexf/main.mexf` o el directorio `.mexf/` sin permisos terminaba en `PermissionError` con traceback; ahora imprime `[ERROR] Compilación .mexf fallida: …` y devuelve 1. Un proyecto legible sigue generando el `.asksome` (`[OK] Artefacto .asksome generado`, código 0).

### Aprobaciones — `CONFIRM.MD`

- `CONFIRM.MD` revisado (último commit del archivo: `5fde875`, autor `openhands <openhands@all-hands.dev>`): `Q-001`…`Q-010` siguen sin casillas marcadas, así que no hay respuestas válidas que aplicar. No se implementó ninguna mejora ni cambio de engine.

### Release — no preparado

- El último reporte externo sigue siendo el del propietario del 2026-11-22, de modo que el requisito de 7 días sin reportes nuevos y el periodo de observación de 3 días siguen en curso. No se generaron `flat cube` ni `blind cube`.

## 2026-11-22

### Corregido — `--shell-info` y la vista previa lanzaban traceback con rutas inaccesibles

Hallazgo del vigésimo primer ciclo de mantenimiento (sin reporte externo; reportado por JesusQuijada34 en la auditoría interna). Commit `edb049f`.

- **R-4e8b2d17 — `--shell-info` y `--shell-preview` terminaban en traceback con un paquete ilegible o un destino bloqueado:** `NativeShellHelper.info()` solo capturaba `ValueError`, pero `native_shell.package_info()` lee el archivo con `Path.read_bytes()`, de modo que un paquete sin permiso de lectura escapaba como `PermissionError`. Además, `export_icon_preview()` crea el directorio de destino con `mkdir()` fuera del `try`, así que `--shell-preview` sobre una ruta ocupada por un archivo normal terminaba en `FileExistsError` (y sobre una ruta sin permiso, en `PermissionError`). El propio `python -m lib.native_shell --info` ya trataba `(ValueError, OSError)` como error esperado. Ahora `NativeShellHelper.info()` captura `(ValueError, OSError)` en ambos pasos y responde `[ERROR] …` / `[ERROR] No se pudo exportar la vista previa: …` con código 1; en modo `--shell-info-json` el error va a stderr y stdout queda vacío. `native_shell._thumbnail_main()` también traduce esos fallos a código 1 para que el generador de miniaturas del escritorio no muestre traceback.

### Verificación — vigésimo primer ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 846 pasan, 1 omitido, 55 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Las 4 pruebas nuevas de `tests/test_native_shell.py` fallan con el código anterior (comprobado con `git stash` de `lib/cliHandler.py` y `lib/native_shell.py`) y pasan con `edb049f`.
- Reproducción real: `--shell-info` sobre un archivo `.iflapp` con permisos `000` respondía con `PermissionError` y traceback; ahora imprime `[ERROR] [Errno 13] Permission denied: …` y devuelve 1. `--shell-info <asksome> --shell-preview <archivo normal>` respondía `FileExistsError`; ahora imprime `[ERROR] No se pudo exportar la vista previa: [Errno 17] File exists: …` sin traceback. `--shell-info-json` mantiene stdout vacío y el error en stderr.

### Aprobaciones — `CONFIRM.MD`

- `CONFIRM.MD` revisado (último commit del archivo: `ee13356`, autor `openhands <openhands@all-hands.dev>`): `Q-001`…`Q-010` siguen sin casillas marcadas, así que no hay respuestas válidas que aplicar. No se implementó ninguna mejora ni cambio de engine.

### Release — no preparado

- El último reporte externo sigue siendo el del propietario del 2026-11-22, de modo que el requisito de 7 días sin reportes nuevos y el periodo de observación de 3 días siguen en curso. No se generaron `flat cube` ni `blind cube`.

## 2026-11-22

### Corregido — `editor_config.json` con forma no válida rompía el arranque

Hallazgo del vigésimo ciclo de mantenimiento (sin reporte externo; reportado por JesusQuijada34 en la auditoría interna). Commit `6f45dd0`.

- **R-7c9e2a45 — Un `data/pmCodeEditor/editor_config.json` válido pero con forma inesperada tumbaba el panel y el editor:** el panel (`DashboardWindow`) y el editor (`EditorWindow`) comparten ese archivo. Un `default_interpreter` que no era texto (`123`, `["x"]`, `{...}`) se asignaba a `os.environ`, que lanza `TypeError: str expected`, de modo que el panel no se construía. En el editor, un documento no-objeto (`[]`, `"texto"`) reventaba en `cfg.get()` con `AttributeError`, y un `default_interpreter` lista/objeto lo hacía en `os.path.isfile()` con `TypeError`. La corrección anterior R-9a3d6f20 solo cubrió el caso no-objeto del panel, no el valor mal tipado ni el editor. Ahora `DashboardWindow.load_config()` adopta el intérprete solo si es una cadena no vacía, y `EditorWindow._load_editor_config()` descarta los documentos que no son objeto y exige una cadena no vacía antes de `os.path.isfile()`.

### Verificación — vigésimo ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 842 pasan, 1 omitido, 55 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Las 3 pruebas nuevas de `tests/test_local_config_robustness.py` (`test_non_string_interpreter_is_ignored` del panel y las dos de `TestEditorConfigShapes`) fallan con el código anterior (comprobado con `git stash` de `lib/pm_dashboard.py` y `pmCodeEditor.py`) y pasan con `6f45dd0`.
- Reproducción real: con `{"default_interpreter": 123}` el panel terminaba en `TypeError: str expected, not int`; con `[]` el editor en `AttributeError: 'list' object has no attribute 'get'`; con `{"default_interpreter": ["x"]}` en `TypeError: stat: path should be string...`. Ahora ambos abren y conservan un `python_path` textual.

### Aprobaciones — `CONFIRM.MD`

- `CONFIRM.MD` revisado (último commit del archivo: `a593c75`, autor `openhands <openhands@all-hands.dev>`): `Q-001`…`Q-010` siguen sin casillas marcadas, así que no hay respuestas válidas que aplicar. No se implementó ninguna mejora ni cambio de engine.

### Release — no preparado

- El último reporte externo sigue siendo el del propietario del 2026-11-22, de modo que el requisito de 7 días sin reportes nuevos y el periodo de observación de 3 días siguen en curso. No se generaron `flat cube` ni `blind cube`.

## 2026-11-22

### Corregido — el dropper `.run` lanzaba traceback con un paquete corrupto

Hallazgo del decimonoveno ciclo de mantenimiento (sin reporte externo; reportado por JesusQuijada34 en la auditoría interna). Commit `caeef80`.

- **R-7f2b9c63 — Un `.run` con el `.iflapp` embebido corrupto lanzaba traceback:** el stub autónomo generado por `create_dropper()` confiaba en la cabecera embebida. Una descarga cortada o un payload alterado hacía que `_header()` decodificara JSON sin comprobar longitud y que `_extract_v2()` indexara `header["payload"]` sin validar el tipo, así que el usuario final veía `UnicodeDecodeError`, `JSONDecodeError`, `KeyError`, `binascii.Error` o `IndexError` en lugar de un mensaje legible. Ahora `_decode_header()` valida JSON y objeto, `_header()` valida longitudes y truncamiento, y `_extract_v2()` valida `payload`/`offset`/`size` y traduce los fallos de descifrado, `lzma` y `tar` a `SystemExit` legible. `_extract_zip()` y `main()` hacen lo propio con ZIP y con `--password` sin valor; `read_dropper_header()` devuelve `IflappError` en vez de `binascii.Error`. Un dropper válido sigue ejecutando la app con código 0.

### Verificación — decimonoveno ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 839 pasan, 1 omitido, 55 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Los 4 casos nuevos de `tests/test_iflapp_dropper_sandbox.py` (payload corrupto, payload truncado, `--password` sin valor y base64 corrupto en el lector) fallan con el código anterior (comprobado con `git stash` de `dropper.py`).
- Reproducción real: un `.run` con el bloque base64 sustituido por bytes aleatorios terminaba en `UnicodeDecodeError`/`JSONDecodeError` con traceback; ahora responde `Cabecera .iflapp truncada.` o `Cabecera .iflapp corrupta: …` y código 1. El dropper válido imprime `Hola desde demo!` y devuelve 0.

### Aprobaciones — `CONFIRM.MD`

- `CONFIRM.MD` revisado: `Q-001`…`Q-010` siguen sin casillas marcadas, así que no hay respuestas válidas que aplicar. No se implementó ninguna mejora ni cambio de engine.

### Release — no preparado

- El último reporte externo sigue siendo el del propietario del 2026-11-22, de modo que el requisito de 7 días sin reportes nuevos y el periodo de observación de 3 días siguen en curso. No se generaron `flat cube` ni `blind cube`.

## 2026-11-22

### Corregido — el build de la GUI moría en silencio y la carpeta de salida lanzaba traceback

Hallazgos del decimoctavo ciclo de mantenimiento (sin reporte externo; reportados por JesusQuijada34 en la auditoría interna). Commits `3920254` y `81e1aec`.

- **R-2c7e9b41 — Metadatos no canónicos mataban la QThread del build sin aviso:** el CLI valida la ley de nombres con `_validate_compiler_metadata()`, pero la GUI no. Un `details.xml` con `<publisher>Jesús</publisher>`, un `app` con caracteres no admitidos o una versión sin `X.x` hacía que `ProjectNameFormatter.format_package_folder()` lanzara `ValueError` dentro de `QThread.run()`. La excepción no emitía `error`, así que la interfaz quedaba en «compilando» sin mensaje. Ahora `FlangCompiler._validate_metadata_naming()` valida publisher/app/versión al inicio de `run()` y convierte el fallo en `last_error` con `[ERROR]`; además, `BuildThread.run()` envuelve la construcción y ejecución del compilador en un `try/except` que emite `error`, de modo que ninguna excepción imprevista deja la GUI colgada.
- **R-5b3d8f27 — Una carpeta de salida inaccesible lanzaba traceback:** `--buildthis --output`, el subcomando `compile`, `FlangCompiler.__init__` y `create_package()` llamaban a `mkdir()` sin proteger `OSError`. Una ruta bajo un archivo, sin permisos o en una unidad inexistente terminaba en `FileNotFoundError`/`NotADirectoryError`/`PermissionError` con traceback (y en la GUI, con el hilo muerto sin `error`). Ahora `_prepare_output_directory()` en el CLI responde `[ERROR] No se pudo preparar la carpeta de salida …` con código 1, y el compilador registra el fallo en `last_error`/`output_path_ready` para publicarlo sin lanzar. La persistencia del payload `.env` también avisa si `config/` está bloqueado en vez de lanzar desde la QThread.

### Verificación — decimoctavo ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 835 pasan, 1 omitido, 55 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Reproducción real: `--buildthis <proyecto> --output /tmp/blocker/out` (con `/tmp/blocker` como archivo normal) responde `[ERROR] No se pudo preparar la carpeta de salida /tmp/blocker/out: [Errno 20] Not a directory` con código 1, sin traceback.
- Un proyecto con `<publisher>Jesús</publisher>` ya no mata la QThread: `BuildThread.run()` emite `Metadatos de proyecto no válidos: Publisher inválido…` y `FlangCompiler.run()` devuelve `None` sin excepción. 3 de los 6 casos nuevos fallan con el código anterior (comprobado con `git stash` de `BuildThread.py`).

### Aprobaciones — `CONFIRM.MD`

- `CONFIRM.MD` revisado (último commit del archivo: `3f36cc9`, autor `openhands <openhands@all-hands.dev>`): `Q-001`…`Q-010` siguen sin casillas marcadas, así que no hay respuestas válidas que aplicar. No se implementó ninguna mejora ni cambio de engine.

### Release — no preparado

- El último reporte externo sigue siendo el del propietario del 2026-11-22, de modo que el requisito de 7 días sin reportes nuevos y el periodo de observación de 3 días siguen en curso. No se generaron `flat cube` ni `blind cube`.

## 2026-11-22

### Corregido — configuración de build y raíz de instalación no válidas

Hallazgos del decimoséptimo ciclo de mantenimiento (sin reporte externo; reportados por JesusQuijada34 en la auditoría interna). Commit `b656928`.

- **R-6c2a8f14 — Un `config/settings.json` no-objeto tumbaba la compilación:** `FlangCompiler._load_scripts_to_compile()` llamaba a `settings.get("build")` sin comprobar el tipo del documento. Un archivo editado a mano que seguía siendo JSON válido pero no era un objeto (`[]`, `"texto"`, `5`) lanzaba `AttributeError` en el constructor del compilador, así que la GUI y `--buildthis`/`compile` se interrumpían con un traceback antes de la validación de metadatos. Ahora un documento no-objeto degrada al descubrimiento histórico de guiones; un `build` no-objeto o unos `scripts` mal tipados siguen rechazándose con el mensaje existente.
- **R-8b3d1e57 — Una raíz de instalación `.asksome` inválida lanzaba traceback:** `install_asksome()` no protegía `root.mkdir()` ni `shutil.rmtree(target)`. Si `--install-root` apuntaba a un archivo, a una ruta sin permisos o el destino era un archivo, el CLI terminaba con `FileExistsError`/`PermissionError`/`NotADirectoryError` en lugar de un `[ERROR]` legible. Ahora la preparación de la raíz, la limpieza del destino y la extracción traducen `OSError` a `AsksomeInstallError`; el CLI responde `[ERROR] Instalación .asksome fallida: …` con código 1. El `app_id` se sigue validando antes de tocar el disco.

### Verificación — decimoséptimo ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 829 pasan, 1 omitido, 55 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- El subtest de `settings.json` no-objeto falla con el código anterior (`AttributeError: 'list' object has no attribute 'get'`) y la prueba de la raíz de instalación falla con `FileExistsError`; ambas pasan con `b656928`.
- Reproducción real: `--install-asksome demo.asksome --install-root /tmp/blocked-root` (archivo normal) responde `[ERROR] Instalación .asksome fallida: No se pudo preparar la raíz de instalación …` con código 1, sin traceback.

### Aprobaciones — `CONFIRM.MD`

- `CONFIRM.MD` revisado (último commit del archivo: `3f36cc9`, autor `openhands <openhands@all-hands.dev>`): `Q-001`…`Q-010` siguen sin casillas marcadas, así que no hay respuestas válidas que aplicar. No se implementó ninguna mejora ni cambio de engine.

### Release — no preparado

- El último reporte externo sigue siendo el del propietario del 2026-11-22, de modo que el requisito de 7 días sin reportes nuevos y el periodo de observación de 3 días siguen en curso. No se generaron `flat cube` ni `blind cube`.

## 2026-11-22

### Corregido — la versión canónica del proyecto bloqueaba la compilación

Reporte del propietario (JesusQuijada34) en `bugs.txt`, commit `bed2e83`. Commit `2011588`.

- **R-9d4c2f18 — Pegar la versión exacta de `details.xml` impedía compilar:** la validación estricta de la página de compilación (`lib/blindcubeEngine/build_validation.py`) solo admitía `X.x[.z]`, así que una versión canónica como `v1.0-26.11-22.00` —el valor que guarda el propio proyecto— se rechazaba con «Versión inválida: usa X.x o X.x.z» y el build no arrancaba. El usuario lo describió como una rotura de la búsqueda exacta del proyecto. Ahora la validación acepta el timestamp canónico `-YY.MM-HH.MM` y el sufijo opcional de plataforma, igual que `ProjectNameFormatter`; `normalize_version_base()` sigue reduciendo la versión a su base antes de construir el nombre del artefacto. Los timestamps malformados y las plataformas desconocidas siguen bloqueados.

### Verificación — ciclo de R-9d4c2f18

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 827 pasan, 1 omitido, 51 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Los 4 casos nuevos de versión canónica con timestamp fallan con el código anterior (comprobado con `git stash` de `build_validation.py`).
- Reproducción real: `validate_build_fields("influent", "jalen", "v1.0-26.11-22.00", "Knosthalij")` devolvía `version` inválida; ahora devuelve una lista vacía y `normalize_version_base()` produce `1.0`.

### Registrado — reporte de coreografía del splash

- El mismo reporte del propietario (`bugs.txt`, commit `bed2e83`) describe que el splash integrado se dibuja a la vez que la ventana principal y no antes, con avisos de Windows `QWidgetWindow(...) must be a top level window` y `UpdateLayeredWindowIndirect failed`. Es un cambio de comportamiento del engine: queda anotado en «Cambios de engine pendientes» nº 4 y en `CONFIRM.MD` (`Q-008`), sin implementar.

### Aprobaciones — `CONFIRM.MD`

- `CONFIRM.MD` revisado (último commit del archivo: `6028ac4`, autor `openhands-agent`): `Q-001`…`Q-010` siguen sin casillas marcadas, así que no hay respuestas válidas que aplicar. No se implementó ninguna mejora ni cambio de engine.

## 2026-11-22

### Corregido — el identificador de `.asksome` podía borrar datos fuera de la raíz de instalación

Hallazgos del decimosexto ciclo de mantenimiento (sin reporte externo; reportados por JesusQuijada34 en la auditoría interna). Commits `3f89823` y `f9f635a`.

- **R-4f9b2c81 — Un `.asksome` con id `.`/`..` borraba fuera de la raíz de instalación:** `_safe_app_id()` sustituía los caracteres no alfanuméricos por `_` pero conservaba los puntos, así que un artefacto con `metadata.id: ".."` producía `target = install_root/..`; `install_asksome()` lo veía existente y ejecutaba `shutil.rmtree()`, borrando el directorio **padre** de la raíz de instalación antes de fallar con `FileNotFoundError`. Con `id: "."` borraba la propia raíz, es decir, todas las apps instaladas. Ahora `_safe_app_id()` devuelve `asksome.app` cuando el identificador queda vacío al quitar los puntos y un nuevo `_validated_app_id()` exige un único componente de ruta antes de crear o borrar el destino.
- **R-2b9e4f73 — `--compile-mexf` lanzaba traceback si no podía escribir el `.asksome`:** `compile_mexf_project()` empaquetaba sin proteger la escritura, así que un `--mexf-output` que apuntaba a una carpeta (`IsADirectoryError`), a una ruta bajo un archivo (`NotADirectoryError`) o a un destino sin permisos (`PermissionError`) escapaba como traceback porque el CLI solo captura `MexfCompileError`. Ahora el staging, el empaquetado y los envoltorios se traducen a `MexfCompileError` con la ruta de destino y el CLI responde `[ERROR] Compilación .mexf fallida: …` con código 1.
- **R-7a3d5e62 — `--uninstall-asksome`/`--build-removeme` aceptaban `app_id` con traversal:** `uninstall_asksome()`, `read_record()` y `build_removeme()` construían la ruta con `install_root / app_id` sin validar el valor recibido por la CLI. `--uninstall-asksome "../victima"` borraba un directorio externo y una ruta absoluta (`/etc`, `C:...`) se usaba tal cual; `--build-removeme` escribía `removeme.py` fuera de la raíz. Los tres puntos de entrada validan ahora el identificador y lanzan `AsksomeInstallError`, que el CLI presenta como `[ERROR]` con código 1.

### Verificación — decimosexto ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 819 pasan, 1 omitido, 51 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Los 6 casos nuevos fallan con el código anterior (comprobado con `git stash` de `lib/blindcubeEngine/asksome_installer.py` y `lib/mexf_compiler.py`).
- Reproducción real: instalar un `.asksome` con `id: ".."` borraba el padre de la raíz de instalación; ahora se instala en `<root>/asksome.app` y el marcador externo sobrevive. `--uninstall-asksome "../victim"` y `--build-removeme "../victim"` responden `[ERROR] Identificador de app inválido` con código 1 y dejan intacto el directorio externo. `--compile-mexf PROYECTO --mexf-output /tmp` responde `[ERROR] Compilación .mexf fallida: … Is a directory` con código 1 (antes: traceback).

### Aprobaciones — `CONFIRM.MD`

- `CONFIRM.MD` revisado: `Q-001`…`Q-010` siguen sin casillas marcadas y el último commit que toca el archivo no es de `JesusQuijada34`, así que no hay respuestas que aplicar. No se implementó ninguna mejora ni cambio de engine.

## 2026-11-22

### Corregido — parámetros y registros mal tipados en contenedores y `.asksome`

Hallazgos del decimoquinto ciclo de mantenimiento (sin reporte externo; reportados por JesusQuijada34 en la auditoría interna). Commit `e9437cb`.

- **R-3b8e5c71 — Un `install.json` con campos mal tipados rompía `--uninstall-asksome`:** `InstallRecord(**data)` no valida tipos, así que un registro con `"shortcuts": 5` se aceptaba y `uninstall_asksome()` reventaba al iterarlo (`TypeError: 'int' object is not iterable`); `"shortcuts": "texto"` iteraba caracteres e intentaba borrar rutas inexistentes. La desinstalación quedaba bloqueada justo cuando se necesita: para retirar una instalación dañada. Ahora `_record_from_mapping()` valida los campos de texto obligatorios y degrada `shortcuts`, `files` y `metadata` a su valor por defecto; `read_record()`, `list_installed()` y `uninstall_asksome()` lo usan. Un campo obligatorio no textual sigue produciendo `AsksomeInstallError` legible.
- **R-7c4d2a96 — Parámetros criptográficos mal tipados en `.blindkpkg`:** `_decrypt_parameters()` solo capturaba `KeyError`/`ValueError`. Un contenedor con `"salt": 5` o `"nonce": 5` lanzaba `TypeError` desde `bytes.fromhex()`, y `"mac": 5` lanzaba `TypeError` en `hmac.compare_digest()`, en lugar del `BlindCubeError` que la API promete para cabeceras corruptas. Ahora se exige texto y se traducen los fallos de decodificación; un MAC no textual se trata como ausente.
- **R-1d9f6b34 — Parámetros criptográficos mal tipados en `.iflapp`:** `_decrypt_payload()` hacía `base64.b64decode(params["salt"])` sin validar. Una cabecera dañada con `salt`/`nonce` numéricos lanzaba `TypeError`, su ausencia `KeyError`, un valor no base64 `binascii.Error` y un `mac` numérico `TypeError` en `compare_digest`; ninguno es un `IflappError`, así que la extracción (verificación en sandbox, actualizador, instalación desde el gestor) terminaba en traceback. Ahora `_decode_parameter()` valida el tipo y traduce los errores a `IflappError`; un MAC no textual produce `IflappSignatureError`. El `.asksome` cifrado hereda el arreglo porque delega en este módulo.

### Verificación — decimoquinto ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 809 pasan, 1 omitido, 51 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Los 5 casos nuevos fallan con el código anterior (comprobado con `git stash` de los tres módulos corregidos).
- `--uninstall-asksome` sobre un `install.json` con `"shortcuts": 5`, `"files": "x"` y `"metadata": []` elimina la instalación con `[OK]` y código 0 (antes: `TypeError`).
- `--inspect-json` lee el `.iflapp` real generado por `create` + `--buildthis --compiler zipapp --no-sandbox --harden integrity` (21 archivos, lzma, sin cifrado).

### Aprobaciones — `CONFIRM.MD`

- `CONFIRM.MD` revisado: `Q-001`…`Q-010` siguen sin casillas marcadas y el último commit que toca el archivo no es de `JesusQuijada34`, así que no hay respuestas que aplicar. No se implementó ninguna mejora ni cambio de engine.

## 2026-11-22

### Corregido — robustez del IDE headless (escaneo, compilación y depuración)

Hallazgos del decimocuarto ciclo de mantenimiento (sin reporte externo; reportados por JesusQuijada34 en la auditoría interna). Commit `38f0791`.

- **R-7f3a9c21 — Un `config/settings.json` con `build` no-objeto rompía `--ide-scan`:** `_declared_scripts()` hacía `data.get("build", {}).get("scripts")`. Si el fichero era un objeto pero `build` era una lista, una cadena, `null` o un número, la segunda llamada lanzaba `AttributeError`: `--ide-scan` terminaba en traceback, `--ide-scan-json` contaminaba la salida JSON y la página del IDE no podía construir el proyecto. Ahora `build` debe ser un objeto para leer `scripts`; en caso contrario se usa el descubrimiento de `.py` de la raíz.
- **R-2c8e5d14 — `--ide-compile` lanzaba traceback con una carpeta inexistente:** `IflappIdeHelper.compile()` llamaba a `compile_project()` sin protección. `scan_project()` lanza `FileNotFoundError` si la ruta no es un proyecto y `mkdir()` puede lanzar `OSError` si `--ide-output` apunta a un archivo. Ahora el helper captura `OSError` y responde `[ERROR] No se pudo compilar el proyecto: …` con código 1.
- **R-5a1f8e63 — `--ide-debug` dejaba escapar las excepciones del guion depurado:** `debug_script()` solo capturaba `OSError` y `SyntaxError`, así que un `ZeroDivisionError`, un `RuntimeError` o un `SystemExit` del guion llegaban al CLI o al hilo de la UI en lugar de rellenar `DebugOutcome.error`. Ahora cualquier fallo del guion, incluido `SystemExit`, se devuelve como error del resultado de depuración.

### Verificación — decimocuarto ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 804 pasan, 1 omitido, 43 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Las 6 pruebas nuevas fallan con el código anterior (comprobado con `git stash` de `lib/iflapp_ide.py` y `lib/cliHandler.py`).
- `--ide-scan --ide-scan-json` con `{"build": []}` emite JSON parseable; `--ide-compile /tmp/no-existe` responde `[ERROR]` y código 1 sin traceback; `debug_script()` sobre un guion con `1/0` devuelve `DebugOutcome(error=…)`.

### Aprobaciones — `CONFIRM.MD`

- `CONFIRM.MD` revisado: `Q-001`…`Q-010` siguen sin casillas marcadas y el último commit que toca el archivo no es de `JesusQuijada34`, así que no hay respuestas que aplicar. No se implementó ninguna mejora ni cambio de engine.

## 2026-11-22

### Corregido — configuraciones locales corruptas tumbaban el arranque y el editor

Hallazgos del decimotercer ciclo de mantenimiento (sin reporte externo; reportados por JesusQuijada34 en la auditoría interna). Commit `7ce7a84`.

- **R-4e7c2b91 — Una caché de sesión o un fichero de idioma corruptos impedían arrancar:** `session_cache.load_session()` hacía `data.get("token")` sin comprobar que el JSON descifrado fuera un objeto y `dict(profile)` sin comprobar que el perfil fuera un objeto. Un documento `[]` lanzaba `AttributeError` y un perfil como `["login"]`, `ValueError`. La llamada ocurre en `start_session_gate()` al terminar el splash, sin `try`, así que la GUI abortaba al arrancar. Del mismo modo, `i18n._load_lang_file()` devolvía cualquier JSON y `_flatten_translations()` hacía `.items()`: un `lang/es.json` con `[]` reventaba en `i18n.initialize()`, antes de crear la ventana. Ahora `load_session()` descarta documentos que no sean objeto y degrada un `profile` no-objeto a `{}`; `_load_lang_file()` ignora ficheros que no contengan un objeto y `_flatten_translations()` devuelve `{}` ante una entrada no-objeto.
- **R-9a3d6f20 — Una configuración local con forma no-objeto rompía el editor y «Abrir con»:** `pm_dashboard.load_config()` asignaba la lista a `self.config` y después llamaba `.get()` (`AttributeError`), y un `recent_projects` no-lista reventaba al iterarlo; `python_portable_manager._load_config()` hacía `.get().items()` y `data["path"]` sobre formas inesperadas (`AttributeError`/`TypeError`), de modo que el gestor de intérpretes no se podía construir; y `ProjectConfig` (`get_project_editor`, `set_project_editor`, `get_editor_path`, `set_editor_path`) asumía que `projects`/`editors` eran objetos, así que `_on_accept()` de «Abrir con» fallaba al pulsar «Siempre». Ahora cada lector exige un objeto JSON, degrada las secciones no-objeto (`recent_projects`, `installations`, `projects`, `editors`) a su valor por defecto e ignora entradas de instalación incompletas.

### Verificación — decimotercer ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 799 pasan, 1 omitido, 39 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- 7 de las 11 pruebas nuevas fallan con el código anterior (comprobado con `git stash` de los cinco módulos corregidos).
- Build real `create` + `--buildthis --compiler zipapp --no-sandbox --harden integrity`: `.iflapp` válido (`verify_iflapp() → valid: True`, 21 archivos) y `--inspect-json` lo lee.

### Corregido — robustez de `.mexf` y del shell nativo

Hallazgos del duodécimo ciclo de mantenimiento (sin reporte externo; reportados por JesusQuijada34 en la auditoría interna). Commit `935da3c`.

- **R-9b4e7a52 — Un `.mexf` v1 con secciones mal tipadas rompía `--compile-mexf` y `--debug-mexf`:** `validate_mexf()` solo comprobaba `triggers`, `commands` y `assets`. Un documento con `shortcuts`/`environments` no-objeto o `file_associations`/`context_menus`/`registry`/`runtime` no-lista pasaba la validación y reventaba después en `merge_documents()` (`dict(valor)`/`list(valor)`) o en `MexfDebugger.__init__()` (`.items()` sobre `environments`). Ahora la validación rechaza esas formas con un `MexfError` legible y las rutas de fusión y depuración normalizan cada sección con `isinstance`, de modo que el CLI responde `[ERROR]` con código 1 en vez de un traceback.
- **R-2f7c8d31 — El identificador `.mexf` escapaba del directorio de integración:** `install_plan()`, `uninstall_plan()` y los renderizadores de `.desktop` usaban `metadata.id` como nombre de fichero sin sanear. Un `id` con `../` escribía el XML MIME y los lanzadores fuera de `share/applications` y `--uninstall-mexf-shell` podía borrar archivos ajenos; además, los valores con saltos de línea podían inyectar claves en el `.desktop`. Ahora un nombre saneado (`_file_stem`) se usa en todas las rutas y `_flat_value()` aplana `Name`/`Exec`/`Icon` y `environment.d`. El identificador visible del plan no cambia.
- **R-6a1d3c94 — Un `.mexf` no UTF-8 provocaba traceback:** `parse_mexf()` leía con `utf-8-sig` sin capturar `UnicodeDecodeError`, así que un archivo binario abortaba `--shell-plan`, `--compile-mexf` y `--debug-mexf`. Ahora se traduce a `MexfError` y `detect_mexf_format()` devuelve `"unknown"`.
- **R-8e5b2f17 — `lib.native_shell --info` sin archivo lanzaba traceback:** el entrypoint hacía `args[1]` sin comprobar la longitud y no capturaba los errores de `package_info()`. Ahora responde con uso (código 2) o `[ERROR]` (código 1).

### Aprobaciones — `CONFIRM.MD`

- Se creó `CONFIRM.MD` como canal único de aprobación del propietario, con 10 preguntas pendientes: `Q-001`…`Q-004` (telemetría, acentos, capitalización del publisher y `compile-only`) y `Q-005`…`Q-010` (aislamiento BlindCube/FlatCube, pruebas y `.env`, reorganización y GlassCube, coreografía de splash, rediseño de UI y sidebar). Ninguna está aprobada y no se aplicó ningún cambio de engine.

### Verificación — duodécimo ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 788 pasan, 1 omitido, 39 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Los 16 casos nuevos fallan con el código anterior (comprobado con `git stash` de los módulos corregidos).
- `--compile-mexf` y `--debug-mexf` con `shortcuts: 5` o `environments: [A, B]` terminan en `[ERROR]` y código 1; un `.mexf` binario ya no lanza traceback; `install_plan()`/`uninstall_plan()` con `id: "../../evil/demo"` mantienen todas las rutas dentro de `base_dir` y no borran archivos externos; `python -m lib.native_shell --info` sin argumento devuelve uso (2) y con archivo desconocido `[ERROR]` (1).

### Corregido — accesos directos `.asksome` y robustez de `.mexf` legacy

Hallazgos del undécimo ciclo de mantenimiento (sin reporte externo; reportados por JesusQuijada34 en la auditoría interna). Commit `6fa3c51`.

- **R-7e3a9c14 — Los accesos directos `.desktop` no citaban rutas con espacios:** `_write_linux_desktop()` escribía `Exec={sys.executable} {launcher}` sin comillas. Si la carpeta de instalación (`--install-root`) o el home contienen espacios (`/home/ana/My Apps/...`), el lanzador parte la ruta en varios argumentos e intenta ejecutar una ruta truncada, así que la aplicación instalada no abre desde el menú. `create_desktop_file()` de `lib/linux_icon_handler.py` tenía el mismo defecto. Además, `Name` y `Comment` copiaban el nombre sin aplanar, de modo que un `name` con saltos de línea inyectaba claves nuevas en el `.desktop`. Ahora `_desktop_exec_quote()` cita cada argumento del campo `Exec` y escapa `\`, `"`, backtick, `$` y los códigos de campo (`%` → `%%`); `_desktop_text()` aplana nombre y comentario.
- **R-4b8d2f61 — Un `install.json` corrupto rompía `--build-removeme`:** `read_record()` hacía `json.loads()` y `InstallRecord(**data)` sin validar. Un registro truncado lanzaba `JSONDecodeError`; un documento que no era objeto o al que le faltaban campos lanzaba `TypeError`. Como el CLI solo captura `AsksomeInstallError`, ambos casos terminaban en un traceback. Ahora `read_record()` valida la lectura y la forma del documento y traduce los fallos a `AsksomeInstallError` legible, que el CLI muestra como `[ERROR]` con código 1.
- **R-9c5f1e28 — Un `.mexf` legacy con tipos inesperados rompía `--shell-plan`:** los documentos JSON legacy se convertían sin validar sus tipos. `shell_commands` como entero lanzaba `TypeError` al iterarlo; una sección `extensions`/`context_menus` no iterable, `environments` que no fuera objeto o `shortcuts` que no fuera diccionario rompían igualmente el plan con `TypeError`/`AttributeError`/`ValueError`. Ahora `_legacy_to_v1()` normaliza las secciones a lista o diccionario y convierte los metadatos a texto, y `plan_from_document()` usa `_as_list()`/`_as_dict()` para no confiar en el tipo de ninguna sección.

### Verificación — undécimo ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 547 pasan, 1 omitido, 39 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Las 6 pruebas nuevas fallan con el código anterior (comprobado con `git stash` de los archivos corregidos).
- Instalación real de un `.asksome` en `/tmp/pm e2e/My Installed Apps` con accesos en `My Shortcuts`: el `.desktop` generado contiene `Exec="…" "…"` citado (antes la ruta con espacios quedaba sin comillas).
- `--build-removeme` sobre un `install.json` corrupto termina con `[ERROR]` y código 1, sin traceback.
- `--shell-plan` sobre un `.mexf` legacy con `extensions`, `shell_commands` y `context_menus` de tipo inesperado funciona sin traceback.

## 2026-11-21

### Corregido — robustez de arranque y contenedores `.asksome`

Hallazgos del octavo ciclo de mantenimiento (sin reporte externo; reportados por JesusQuijada34 en la auditoría interna). Commit `543e173`.

- **R-1f4a7c92 — Un `pm.data` o `settings.json` con forma no-objeto impedía arrancar:** `PMDataStore.load()` solo capturaba errores de sintaxis u E/S. Un `data/pm.data` que seguía siendo JSON válido pero no un objeto (`[]`, `"texto"`, `42`, `null`) reventaba en `_ensure_structure()` con `TypeError`, y como `packagemaker.py` carga `APP_CONFIG` al importarse, la aplicación no arrancaba ni en GUI ni en CLI. Lo mismo ocurría con `user`, `readonly` o `translation_cache` de otro tipo y con un `config/settings.json` que fuera una lista (`AttributeError` en la migración). Ahora el documento no-objeto se descarta, cada sección se reconstruye conservando las claves válidas de las demás y la migración ignora un `settings.json` no-objeto.
- **R-2b6d8e13 — Las cabeceras `.asksome` malformadas rompían `--shell-info` y la verificación:** `read_asksome_header()` no comprobaba que el tamaño declarado cupiera en el archivo ni la forma del JSON. Una cabecera `[]` terminaba en `AttributeError` en `verify_asksome()`, `extract_asksome()`, `package_info()` e `icon_bytes()`; `metadata` como lista o `manifest` no lista daban `TypeError`; un icono base64 inválido abortaba el hover del shell. Ahora una lectura única valida tamaño, JSON y tipos, y el shell ignora iconos no decodificables.
- **R-3c9e1a57 — La extracción `.asksome` aceptaba rutas de unidad y exponía errores crudos:** `_safe_member()` solo rechazaba rutas POSIX absolutas y `..`, así que una entrada `C:/Windows/...` o `C:archivo` pasaba y en Windows resolvía fuera del destino. Además, un payload LZMA/TAR corrupto salía como `LZMAError`/`ReadError`. Ahora se rechazan rutas absolutas, unidades de Windows, `..` y cualquier resolución que escape, se comprueban symlinks preexistentes y los errores se traducen a `AsksomeError`.

### Corregido

Reportes del [issue #4](https://github.com/JesusQuijada34/packagemaker/issues/4), reportados por JesusQuijada34.

- **R-dd68f3f4 — Exportación en Termux/Android:** `compile_output_directory()` en `lib/platform_detect.py` exporta los `.iflapp` al almacenamiento compartido (Download) en Termux/Android y conserva la ruta histórica en escritorio. La CLI usa esa carpeta como salida por defecto y la TUI toma su carpeta base del detector de plataforma. Commit `b305945`.
- **R-e2d317ce — Gestor de apps:** `list_projects()`/`is_project_directory()` en `lib/project_locator.py` exigen `details.xml` y excluyen `dist`, `build`, `releases`, cachés, entornos virtuales y restos de Nuitka. El gestor y MoonFix de la TUI listan solo proyectos fuente. Commit `b305945`.
- **R-f478fbef — Empaquetado con proyecto abierto:** regresión que empaqueta `.iflapp` con archivos del proyecto abiertos y confirma que la fuente se conserva; la limpieza solo elimina artefactos de compilación. Commit `b305945`.
- **R-e1a87de9 — Persistencia de ajustes:** regresión de ida y vuelta sobre `PMDataStore` que verifica que `save_app_config()` persiste rutas, idioma y preferencias y que se releen en una instancia nueva. Commit `b305945`.
- **R-730ee37a, R-062ec1b5, R-739d5fec:** verificados como ya resueltos en `main` (cursor Qt6, validación del editor externo y salida Unicode segura) con sus pruebas existentes.

### Corregido — auditoría interna

Hallazgos de la revisión de mantenimiento de este ciclo (sin reporte externo; reportados por JesusQuijada34 en la auditoría interna).

- **R-8f2c41d9 — Empaquetado con el backend zipapp:** `zipapp` es el backend de reserva siempre disponible, pero `create_package()` solo aceptaba `<guion>`/`<guion>.exe` y rechazaba el `<guion>.pyz` que produce el backend, así que ningún build con `--compiler zipapp` llegaba a generar paquete. Ahora `_copy_package_files()` copia los `.pyz` al paquete y `create_package()` los acepta; la detección de artefactos ausentes se conserva. Commit `5aa823b`.
- **R-c47a9e12 — `--harden` ignorado en CLI headless:** las rutas de `buildthis` y `compile` no invocaban `apply_hardening()`, por lo que los métodos de blindaje se descartaban sin aviso. Ahora se aplican sobre el árbol del paquete antes de comprimir, igual que la GUI. Commit `5aa823b`.

### Corregido — auditoría interna del CLI

Hallazgos del segundo ciclo de mantenimiento (sin reporte externo; reportados por JesusQuijada34 en la auditoría interna). Commit `d2670a1`.

- **R-2e83a7bd — El subcomando `compile` ignoraba la salida de Termux:** usaba una ruta fija `~/Documents/…`, inaccesible en Android/Termux. Ahora toma la salida de `compile_output_directory()`, igual que `--buildthis`; en escritorio la ruta no cambia.
- **R-4b7e91a2 — El banner contaminaba la salida JSON:** las líneas `[PackageMaker] …` se imprimían en stdout y rompían `--inspect-json`, `--shell-info-json` y `--ide-scan-json`. Ahora van a stderr.
- **R-9c1d5f60 — `create` no copiaba el icono fuera de la raíz:** el icono se buscaba con una ruta relativa al CWD; ejecutado desde otro directorio el proyecto quedaba sin icono y el `.iflapp` salía con `Icono: 0 bytes`. Ahora se resuelve contra la raíz del repo, el bundle, el ejecutable y el CWD, y se avisa si no aparece.
- **R-a5f06c38 — `--harden` inválido en silencio:** un método mal escrito se descartaba sin aviso y podía dejar el build sin blindaje aparentando tenerlo. Ahora se informa de los métodos ignorados y de la desactivación total.
- **R-d74e0b19 — `--ide-compile` duplicaba la salida:** el log se imprimía por el callback y otra vez al recorrer `outcome.log`. Ahora se imprime una sola vez.

### Corregido — metadatos no canónicos en el CLI

Hallazgo del tercer ciclo de mantenimiento (sin reporte externo; reportado por JesusQuijada34 en la auditoría interna). Commit `e84e367`.

- **R-b3f71a6c — Un publisher o identificador fuera de la ley de nombres rompía el CLI:** `create`, `--buildthis`, `compile` y `moonfix` llamaban a `format_project_folder()` sin capturar el `ValueError`, así que un publisher como `Jesús` terminaba en un traceback. En `--buildthis` el proyecto se compilaba completo y el fallo aparecía al final, sin generar artefacto. Ahora `_canonical_folder_or_exit()` valida antes de compilar y aborta con `[ERROR] Metadatos de proyecto no válidos: …` y código 1; `create` y `moonfix` usan la misma validación. La ley de nombres no cambia.

### Corregido — selección de proyecto y verificación cifrada

Hallazgos del cuarto ciclo de mantenimiento (sin reporte externo; reportados por JesusQuijada34 en la auditoría interna). Commit `ab79f4a`.

- **R-7c1e4a90 — `compile`/`moonfix` compilaban el proyecto equivocado:** la búsqueda usaba `publisher in nombre and app in nombre`, así que con `demo` y `demo2` en la misma carpeta elegía `demo2`; además, si la carpeta base no existía, `iterdir()` terminaba en un traceback. Ahora ambos usan `locate_project()`, que compara la identidad canónica de la carpeta, cae a `details.xml` solo para carpetas no canónicas y devuelve un error legible si no hay carpeta base.
- **R-91b6d2f4 — La verificación en sandbox no descifraba los paquetes con `--password`:** el script del sandbox llamaba a `extract_iflapp()` sin contraseña, así que todo build cifrado avisaba «verificación incompleta» y quedaba sin verificar. La contraseña viaja por `IFLAPP_VERIFY_PASSWORD` (entorno, no `argv`) y se pasa a `extract_iflapp(..., password=...)`.

### Corregido — pureza de salida del CLI

Hallazgos del quinto ciclo de mantenimiento (sin reporte externo; reportados por JesusQuijada34 en la auditoría interna). Commit `7f708bb`.

- **R-3a7c5e18 — Los avisos de importación contaminaban las acciones JSON:** la falta de `leviathan_ui` imprimía `[WARN] Leviathan UI unavailable…` en stdout (y sin PyQt6 se añadía `font: none`), así que `--inspect-json`, `--shell-plan-json`, `--shell-info-json` y `--ide-scan-json` dejaban de ser parseables. Ahora esos avisos van a stderr. Es una regresión de la misma clase que R-4b7e91a2.
- **R-9f2b64d1 — Los avisos auxiliares rompían el JSON:** `--inspect-extract` y `--shell-preview` añadían su `[OK]`/`[INFO]` a stdout después del documento. Ahora van a stderr en modo JSON y a stdout en modo humano.
- **R-6e04c8ab — El aviso de MoonFix no era codificable en cp1252:** un `details.xml` corrupto hacía `print("⚠ …")`, que lanzaba `UnicodeEncodeError` en consolas Windows y abortaba la reparación. Ahora usa `_safe_print` y escribe en stderr; el fallback a los metadatos del CLI no cambia.

### Corregido — reparación MoonFix

Hallazgo del sexto ciclo de mantenimiento (sin reporte externo; reportado por JesusQuijada34 en la auditoría interna). Commit `c36df67`.

- **R-7d5b91c4 — MoonFix regeneraba la marca temporal y rompía la ley canónica:** `repair_project_from_templates()` escribía `details.xml` con una marca temporal nueva porque ningún llamador pasaba `timestamp`. Tras `moonfix`, una carpeta `influent.demo.v1.0-26.11-10.05-Danenone` contenía `<version>v1.0-26.11-10.06</version>`, así que carpeta y metadatos dejaban de coincidir y cada reparación volvía a mover la marca. Ahora la reparación conserva el timestamp de la carpeta canónica o, si la carpeta es legacy, el de `details.xml`; solo genera uno nuevo cuando el proyecto no tiene ninguno. El arreglo es central y cubre CLI, GUI y `moonFixWizard`.

### Corregido — dropper autoextraíble

Hallazgo del séptimo ciclo de mantenimiento (sin reporte externo; reportado por JesusQuijada34 en la auditoría interna). Commit `325c0e9`.

- **R-3f9a2c71 — El dropper lanzaba `updater.py` en los builds zipapp:** el stub solo probaba `<guion>`, `<guion>.exe` y `<guion>.py`, pero el backend zipapp entrega `<guion>.pyz`. Al no encontrar el punto de entrada, el respaldo ejecutaba el primer `.py` de la raíz del paquete (`updater.py`) y el `.run` quedaba en el actualizador en lugar de arrancar la aplicación. Ahora los candidatos incluyen `.pyz` y el respaldo prefiere artefactos Python compilados antes que los guiones auxiliares.

### Corregido — cabeceras `.iflapp` truncadas

Hallazgo del mismo ciclo de mantenimiento (sin reporte externo; reportado por JesusQuijada34 en la auditoría interna). Commit `850de5c`.

- **R-7b1d4e92 — `--inspect` aceptaba cabeceras truncadas como paquete válido:** `read_iflapp_header()` no comprobaba que la cabecera declarada cupiera en el archivo, así que un `.iflapp` cortado se inspeccionaba con código 0 y `format_version: 0`/identidad vacía; faltando los 4 bytes de longitud lanzaba `struct.error`, y un JSON que no fuera objeto o metadatos de sección no numéricos terminaban en `AttributeError`/`ValueError`. Ahora todos esos casos producen un `IflappError` legible.

### Mantenimiento

- `lib/requirements-dev.txt` resuelve correctamente su include (`-r requirements.txt`) y la documentación usa la ruta real `lib/requirements-dev.txt`.

### Verificación

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 484 pasan, 1 omitido (la dependencia opcional `leviathan_ui` está instalada en este entorno).
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- `--inspect-json` sobre un `.iflapp` con cabecera cortada, JSON `null` o sección fuera del archivo termina con código 1 y un error legible (antes: código 0 con cabecera vacía o excepción cruda).
- Build real con `--compiler zipapp --no-sandbox --dropper`: genera `.iflapp` y `.run`; el `.run` ejecuta `demo.pyz` e imprime `Hola desde demo!` (antes lanzaba `updater.py` y no terminaba).
- Build real con `--compiler zipapp --harden integrity`: `.iflapp` válido con `.iflapp.integrity` en el manifiesto.
- Build real con `--compiler zipapp --password` y sandbox activo: `.iflapp` cifrado y verificación en sandbox `[OK]` (antes «incompleta»).
- `compile` con `demo` y `demo2` elige `demo`; `compile`/`moonfix` sin carpeta base abortan con error legible y código 1, sin traceback.
- `--inspect-json` emite JSON parseable en stdout (banner en stderr).
- Las cuatro acciones JSON emiten JSON parseable sin `leviathan_ui`, incluso combinadas con `--inspect-extract` o `--shell-preview`.
- `moonfix` con `details.xml` truncado y stdout en `cp1252` avisa en stderr y repara sin traceback.
- `create`, `--buildthis` y `moonfix` con metadatos no canónicos abortan con error legible y código 1, sin traceback.
- `create` + `moonfix` reales conservan el mismo sufijo temporal en la carpeta y en `<version>` de `details.xml` (R-7d5b91c4).

### Corregido — robustez del lector de cabeceras `.iflapp`

Hallazgo del octavo ciclo de mantenimiento (sin reporte externo; reportado por JesusQuijada34 en la auditoría interna). Commit `f60f9ac`.

- **R-8a4f1c6d — Una cabecera `.iflapp` con tipos inesperados rompía `--inspect` con traceback:** `read_iflapp_header()` solo validaba que la cabecera fuera un objeto JSON. Un `manifest` que no fuera lista terminaba en `TypeError`; un `payload` que no fuera objeto, en `AttributeError` al leer compresión, cifrado o número de archivos; un `file_count` no numérico, en `ValueError`; una sección mal tipada rompía `--inspect-extract`; y un offset negativo producía un `OSError [Errno 22]` críptico. Ahora `_validate_header_shape()` valida tipos y metadatos numéricos, `_read_section()` y `_payload_bounds()` validan los límites contra el archivo, y las propiedades de `IflappHeader` y `export_header_assets()` toleran formas inesperadas. Todos los casos devuelven un `IflappError` legible.

### Corregido — dependencias del editor, updater y metadatos del CLI

Hallazgos del noveno ciclo de mantenimiento (sin reporte externo; reportados por JesusQuijada34 en la auditoría interna).

- **R-1c93e4b7 — El editor trataba módulos estándar como dependencias de PyPI:** `lib/dependency_manager.py` usaba una lista fija de módulos estándar que omitía `hmac`, `asyncio`, `ctypes`, `email`, `decimal`, `tomllib`, `sysconfig`, `operator`, `shlex`, `signal` o `zoneinfo`. Un script con `import hmac` hacía que el editor escribiera `hmac` en `requirements.txt` e intentara `pip install hmac`. Ahora la lista se une con `sys.stdlib_module_names` (autoridad desde Python 3.10), conservando la lista histórica como respaldo.
- **R-4d7b2e91 — `updater.py` abortaba sin `leviathan_ui`:** el updater se copia a todos los proyectos empaquetados y se usa en modo headless (`--version`, `--check`, `--install`), pero importaba `leviathan_ui` de forma incondicional. Ahora `WipeWindow` tiene un respaldo no-op (mismo patrón que `packagemaker.py` y `lib/window_chrome.py`) y `get_accent_color()` cae a `#0078D4`; `--version` y la validación de argumentos funcionan sin la dependencia opcional.
- **R-6b1f8d20 — `--force-fonts` se ignoraba y abría la TUI:** el flag solo se leía dentro de la rama de `--download-fonts`, así que usado solo no resolvía ninguna acción y arrancaba la interfaz de texto. Ahora implica `--download-fonts all` con `force=True` y respeta las claves si se combinan ambos flags.
- **R-9e2a5c73 — `--app-version` reportaba una versión fija:** el entrypoint importaba el inexistente `version.VERSION` y caía en `3.2.7`, ignorando `details.xml`; `show_version` además imprimía `vv…`. Ahora ambos caminos leen la versión canónica de `details.xml` (`lib.cliHandler.__version__`), normalizan el prefijo y usan «desconocida» si falta. El formato `Influent Package Maker v<versión>` no cambia.
- **R-2a7f6b41 — La cabecera `.iflapp` no coincidía con su `details.xml`:** `create_package()` reescribe `<platform>` con la plataforma objetivo, pero la cabecera conservaba la del proyecto. Un proyecto `AlphaCube` compilado en Linux mostraba `Plataforma: AlphaCube` en `--inspect` y `Danenone` dentro del contenedor. `package_identity()` alinea la cabecera con el XML empaquetado y conserva los metadatos si el XML falta o está dañado.

Commit `64c083a`.

### Verificación — noveno ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 509 pasan, 1 omitido, 35 subtests.
- `python -m pyflakes`, `python -m py_compile` y `ruff` (`F821/F822/F823/F811/F841/B006/B008/B017/B904/E722`) limpios.
- Las 18 pruebas nuevas fallan con el código anterior (comprobado con `git stash` de cada archivo corregido).
- Build real `create` + `--buildthis --compiler zipapp --no-sandbox --harden integrity`: `.iflapp` válido (`verify_iflapp() → valid: True`), `--inspect` muestra la misma plataforma que el `details.xml` interno y `--app-version` informa `v3.2.7-26.05-20.13`.
- `updater.py --version` y `updater.py --accept-license` funcionan con `leviathan_ui` inaccesible (antes: `ModuleNotFoundError`).

### Corregido — blindaje por ofuscación y contenedores de motor

Hallazgos del décimo ciclo de mantenimiento (sin reporte externo; reportados por JesusQuijada34 en la auditoría interna).

- **R-6f2b9d31 — `--harden obfuscate` podía dejar el paquete inservible:** `obfuscate_strings()` localizaba los literales con una expresión regular. Con concatenación implícita (`("parte uno " "parte dos")`) la sustitución producía dos llamadas seguidas, un `SyntaxError`; el blindaje informaba `OK` y el build terminaba, pero el `updater.py` empaquetado ya no se ejecutaba. El patrón además reescribía texto entre comillas dentro de docstrings y f-strings. Ahora el fuente se analiza con `ast` y solo se sustituyen los `ast.Constant` de texto completos; se omiten docstrings, partes literales de f-strings, patrones de `match` y valores de `Literal`/`Annotated`. Un fuente no analizable devuelve `applied=False` sin tocarlo.
- **R-8c4e1a72 — Los contenedores `.blindkpkg`/`.flatkpkg` lanzaban excepciones crudas:** `BuildEngine.read_header()` y `blindcubeEngine.read_header()` no comprobaban que la cabecera declarada cupiera en el archivo (`struct.error`), ni que el JSON fuera un objeto (`TypeError`); un payload LZMA corrupto o parámetros de cifrado incompletos salían como `LZMAError`/`KeyError`, y `flatcubeEngine.unpack()` devolvía `BadZipFile`, `JSONDecodeError` o un manifiesto que no era diccionario. Ahora los tres lectores validan longitudes y tipos y traducen esos fallos a `EngineError`/`BlindCubeError`/`FlatCubeError`. El formato válido no cambia.

### Verificación — décimo ciclo

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`: 521 pasan, 1 omitido, 35 subtests.
- `python -m pyflakes $(git ls-files '*.py')` y `python -m py_compile` limpios.
- Las 12 pruebas nuevas fallan con el código anterior (ofuscación por `SyntaxError`; contenedores por `struct.error`/`BadZipFile`).
- Build real `create` + `--buildthis --compiler zipapp --no-sandbox --harden obfuscate`: `.iflapp` válido (`verify_iflapp() → valid: True`), el `updater.py` empaquetado compila con `py_compile`, el `.pyz` del proyecto imprime `Hola desde demoobf!` y la fuente del proyecto queda intacta.

### Pendiente de aprobación

- **R-d23039c0 — Telemetría de errores:** no implementada (envía datos a un servidor externo).
- **R-5d8e2a41 — Acentos en publisher/appname:** no implementada; cambia la ley de nombres.
- **R-4c8e1f27 — Capitalización del publisher:** `create` y la GUI pasan el publisher a minúsculas, así que la carpeta y `details.xml` no conservan la capitalización que exige la ley de nombres. No implementado: cambia los nombres visibles y las rutas de build.
- **R-3e7d1c58 — `compile-only` no retira el fuente del paquete:** el método solo añade el `.pyc` optimizado y el `.py` legible sigue en el artefacto. No implementado: borrar el fuente es destructivo y puede romper el punto de entrada de un build zipapp.
- **Cambios de engine de `bugs.txt`:** registrados en `bugs.md`, sin implementar.

## 2026-11-15

### Corregido

- Importación de `Qt` en `lib/fluent_theme.py` para evitar el `NameError` al consultar `Qt.ColorScheme`.
- Legibilidad del tema claro: los tokens de texto principal y texto atenuado usan negro para conservar contraste.
- Fondo del splash integrado: usa el color de acento configurado en la aplicación en lugar de un color fijo.
- Pila tipográfica: Roboto pasa a ser la primera opción de la interfaz.
- Claves de traducción faltantes en los idiomas disponibles, con fallback controlado a inglés/español.

### Verificación

- La auditoría de tema, diálogos, checkboxes, barra de estado y regresiones visuales pasa con `QT_QPA_PLATFORM=offscreen`.
- La extracción completa de textos hardcodeados en español sigue pendiente y permanece señalada en `bugs.txt`.

### Arquitectura `.mexf` / `.asksome`

- Se añadió un parser YAML v1 declarativo con validación de metadatos, IDs, assets y argumentos argv.
- El formato JSON de `example.mexf` se detecta como legacy y puede migrarse explícitamente a YAML.
- Se añadió un contenedor `.asksome` determinista con manifiesto, digest, firma local y extracción contra traversal/enlaces.
- Se declaró PyYAML como dependencia del parser.
