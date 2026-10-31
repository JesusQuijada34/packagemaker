# AGENTS.md — PackageMaker

Identidad: `Influent.packagemaker.v3.2.7-26.05-20.13-AlphaCube` (JesusQuijada34).
Repo: `https://github.com/JesusQuijada34/packagemaker.git`, rama de trabajo `main`.

## Flujo de trabajo
- **Nunca crear ramas**: se trabaja y se sube directamente a `main`.
- Ejecutar la suite: `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`.
- Análisis estático: `python -m pyflakes $(git ls-files '*.py')` debe salir limpio.
  Limpiar imports muertos con
  `python -m autoflake --in-place --remove-all-unused-imports <archivos>`.
- Compilar sin arrancar la GUI: `python -m py_compile $(git ls-files '*.py')`.
- CLI headless (sin ventana): `--list-compilers`, `--list-hardening`,
  `--inspect <archivo>`, `--list-fonts`. Cualquier acción nueva "de shell" debe
  añadirse a la lista headless de `main()` en `packagemaker.py`, o el flujo
  seguirá como si fuera una ventana.

## Sistema de diseño (macOS + UWP)
- `lib/design_tokens.py` es la **única fuente** de paleta, radios, espaciados y
  tipografía. Ningún widget debe escribir colores a mano: pide su QSS aquí
  (`input_qss`, `primary_button_qss`, `checkbox_qss`, `radio_qss`, `slider_qss`,
  `mono_value_qss`, ...). Cambiar `ACCENT` o un radio se propaga a toda la UI.
- Híbrido: radios amplios y píldoras de macOS (ventana 12px, píldora 18px),
  materiales oscuros, foco de 2px y controles planos de UWP.
- Acento por defecto `#0078D4` (azul Windows 11), definido en
  `lib/pm_data.py` (`custom_accent_color`). `get_accent_color()` en
  `packagemaker.py` prioriza la preferencia del usuario, luego `leviathan_ui` y,
  en último término, ese azul.
- `lib/fluent_theme.py` mantiene los grupos de QSS por área
  (`WINDOW_CHROME_STYLES`, `PROJECT_CREATION_STYLES`, ...) pero sus valores
  salen de los tokens.
- **Ningún QSS con acento se escribe literal**: `pmCodeEditor.py`,
  `lib/pm_dashboard.py` e `lib/interpreter_config_dialog.py` exponen un
  `ACCENT_COLOR`/`EDITOR_ACCENT` calculado una vez (preferencia del usuario →
  token `ACCENT`) y lo interpolan con f-strings. Al añadir un bloque QSS con
  llaves, recuerda convertirlo a `f"""..."""` y duplicar las llaves (`{{ }}`).
- `lib/hover_animation.py` aplica un desvanecido de fondo al pasar el ratón.
  Reescribe **sólo** la regla `:hover` pura y respeta `:checked:hover`. Para
  saltarte un estado usa `only_when` (p. ej. el ítem de la barra lateral
  seleccionado no se anima). El animador **reutiliza una sola
  `QPropertyAnimation`** creada en `__init__`: con
  `DeletionPolicy.DeleteWhenStopped` Qt destruía el objeto C++ al terminar y el
  siguiente `stop()` lanzaba
  `RuntimeError: wrapped C/C++ object of type QPropertyAnimation has been deleted`.
- `lib/app_icons.py` genera los SVG con un color incrustado. `get_sidebar_icon(key,
  size, dark=...)` lo sustituye por el **gris uniforme** `SIDEBAR_TEXT_GRAY`
  (`#6E6E73`), el mismo en tema claro y oscuro. `SidebarItem(..., icon_key=...)`
  guarda la clave para poder repintar el icono en `set_dark()`; sin `icon_key` el
  icono se queda con el color fijo `#ffffff` y desaparece en tema claro.
- `lib/SidebarItem.py` pinta el indicador azul en `paintEvent` con un progreso
  animado (`indicatorProgress`, 0→1). La selección **no** cambia el color del
  texto: el texto y el icono son siempre gris y lo que distingue al ítem activo
  es el fondo más el indicador. La animación se crea de forma perezosa y se
  reutiliza (misma razón que en `hover_animation`).
- `lib/window_manager_bridge.py`: la titlebar queda **excluida** del área de
  redimensionado (`_position_over_titlebar`) y el cursor se **restaura** al salir
  de un borde o de la ventana (`_reset_cursor`). Sin eso el cursor de
  redimensionado se quedaba pegado al pasar el ratón por la titlebar, porque los
  hijos heredan el cursor de la ventana. El filtro se instala también sobre la
  titlebar.

## Ley de nombres canónicos y estructura
- Todo artefacto público debe ser exactamente
  `publisher.appname.vX.x[.z]-YY.MM-HH.MM-Platform`. Las tres únicas
  plataformas válidas son `Danenone`, `Knosthalij` y `AlphaCube` (los alias
  `Linux`/`Windows`/`multi` se normalizan a ellas). El publisher conserva su
  capitalización; el appname se pasa a minúsculas. El sufijo de plataforma
  **pertenece al nombre, no a la versión** (`version_full` nunca lo lleva).
- `lib/projectNameFormatter.py` es la autoridad; `parse_project_folder()`
  devuelve `None` si el nombre no es canónico (p. ej. sin sufijo de plataforma).
- Estructura obligatoria del proyecto/paquete: `details.xml`, `version.res`,
  `autorun`, `autorun.bat`, `.storedetail`, `updater.py`,
  `config/settings.json` y los marcadores `.container` de cada subdirectorio.
- `tests/test_canonical_law_and_structure.py` ejerce la ley de extremo a extremo
  con las funciones reales: `format_*` → `create_project_from_templates()` →
  `pack_iflapp()` → `read_iflapp_header()` → `verify_iflapp()`, incluyendo que el
  payload cifrado no filtre texto en claro y que el manifiesto no acepte
  traversal.

## Arquitectura relevante
- `lib/compilers.py` — backends de compilación: `nuitka` (por defecto, traduce
  a C/C++), `pyinstaller` (bytecode), `zipapp` (stdlib, siempre disponible),
  `cxfreeze` y `pyoxidizer` (herramientas externas). `available_backends()`
  reporta estado real. `resolve_backend()` cae a Nuitka → PyInstaller → zipapp,
  así que siempre hay un backend operativo.
- `lib/nuitka_embedded.py` — backend Nuitka embebido (`build_arguments()`
  construye la línea de comandos sin lanzar procesos).
- `lib/page_action_bar.py` — barra de acciones superior estilo macOS compartida
  por las 5 páginas (`install_page_action_bar`/`make_action_button`). Cada
  página instala la suya; no reutilices nombres de atributo entre páginas
  (p. ej. `btn_build` es del sidebar, el botón de la página es
  `btn_build_action`).
- `lib/iflapp_format.py` — contenedor `.iflapp` v2 (cabecera en claro con icono
  y `details.xml`, firma HMAC-SHA256). `verify_iflapp()` devuelve clave `"valid"`.
- `lib/iflapp_reader.py` — `IflappReader` lee cabecera sin descompilar.
- `lib/hardware_sandbox.py` — aislamiento jerárquico
  (qemu-kvm → systemd-nspawn → docker/podman → bwrap/firejail → unshare → local).
  `qemu-kvm` sólo se anuncia con kernel/initrd (`IFLAPP_QEMU_KERNEL`/`_INITRD`).
- `lib/hardening.py` — blindaje: `strip/upx/checksum/anti-debug/obfuscate/resource`
  más `sign` (sello HMAC-SHA256 + Authenticode opcional), `integrity` (manifiesto
  con raíz Merkle), `compile-only` (`.pyc` O2) y `rename-symbols`.
- `lib/dropper.py` — dropper `.run` con el `.iflapp` embebido. El stub resuelve
  el punto de entrada probando `app`/`main`/`app`/`run`/`__main__`/`start` en
  raíz y `bin/`; sin esto sólo extraía e imprimía la ruta.
- `lib/BuildThread.py` — orquesta build + `verify_in_sandbox()`.

## Trampas conocidas
- El script de verificación del sandbox importa `lib`, por lo que se ejecuta con
  `PYTHONPATH` apuntando a la raíz del repo.
- `QDialog.accept()` no dispara `closeEvent`; la limpieza de overlay vive en
  `accept`/`reject`/`done`/`closeEvent` (idempotente) en `lib/alert_dialog.py`.
- `leviathan_ui` **no está instalado** en CI ni en Linux sin la dependencia. Todo
  módulo que use `WipeWindow`, `LightsOff`, `InmersiveSplash`, `CustomTitleBar`,
  `TouchScreen` o `LeviathanProgressBar` debe definir un respaldo no-op en su
  propio `except ImportError` (`packagemaker.py` y `lib/window_chrome.py` ya lo
  hacen). Sin ese respaldo la app revienta al construir la ventana.
- Los tests de UI necesitan `PyQt6` y las libs de sistema `libegl1`, `libgl1`,
  `libxkbcommon-x11-0` (en un contenedor Debian:
  `sudo apt-get update && sudo apt-get install -y libegl1 libgl1 libxkbcommon-x11-0`).
  `PyQt6` sin `libEGL.so.1` falla al importar `PyQt6.QtSvg`. El entorno puede
  reiniciarse y perder `pytest`/`pyflakes`/`requests`/`PyQt6`: reinstálalos con
  `pip install -r requirements-dev.txt requests PyQt6`.
- En tests con Qt, conserva una referencia a la `QApplication` (patrón
  `_ensure_app`): si se recolecta, Qt aborta el proceso con *Fatal Python
  error: Aborted* en la siguiente llamada.
- `iflapp_format.pack_iflapp()` acepta `icon`/`details` como `bytes` **o** ruta
  (`_as_bytes` los normaliza); pasar una ruta sin coercer daba un `TypeError`
  críptico en `len(icon)`.
- `IflappHeader.identity()` deriva la identidad del `details.xml` de la cabecera
  cuando no hay campos planos (empaquetado sin `identity`); así `--inspect`
  muestra publisher/app reales sin descifrar. `IflappReader.summary()` existe y
  delega en `IflappInfo.summary()`.
- Las capturas de `assets/screenshots/` se regeneran con
  `QT_QPA_PLATFORM=offscreen python scripts/capture_screenshots.py`.
- **Ley de nombres**: el nombre de la carpeta de proyecto debe salir siempre de
  `ProjectNameFormatter.format_project_folder(...)` (o de la clave `FOLDER_NAME`
  de `build_variables(...)`). Nunca lo recompongas a mano con `f"{publisher}.{app}.{VERSION_FULL}"`:
  `VERSION_FULL` **no** lleva el sufijo de plataforma y el nombre deja de ser
  canónico (regresión histórica del commit `60c5cc0`). Toda ruta que cree un
  proyecto (`create_package_action`, `pm_dashboard`, diálogo de creación, CLI
  headless) debe pasar además el mismo `timestamp` a
  `create_project_from_templates` para que `details.xml` y el directorio
  compartan la marca temporal.
- `create_project_from_templates` valida `templates_available()` **antes** de
  crear la carpeta: sin plantillas (p. ej. bundle sin `src/templates`) lanza
  `FileNotFoundError` en vez de dejar un proyecto vacío.
