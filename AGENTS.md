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
  seleccionado no se anima).

## Arquitectura relevante
- `lib/compilers.py` — **solo dos** backends embebidos: `nuitka` (por defecto,
  traduce a C/C++) y `pyinstaller` (bytecode). `available_backends()` reporta
  estado real. Los nombres históricos `cx_freeze`/`pyoxidizer` siguen
  resolviendo por alias, pero ya no se anuncian.
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
- `lib/hardening.py` — `strip/upx/checksum/anti-debug/obfuscate/resource`.
- `lib/dropper.py` — dropper `.run` con el `.iflapp` embebido.
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
- Los tests de UI necesitan `PyQt6` y las libs de sistema `libegl1`,
  `libgl1`, `libxkbcommon-x11-0` (en un contenedor Debian:
  `sudo apt-get install -y libegl1 libgl1 libxkbcommon-x11-0`).
- En tests con Qt, conserva una referencia a la `QApplication` (patrón
  `_ensure_app`): si se recolecta, Qt aborta el proceso con *Fatal Python
  error: Aborted* en la siguiente llamada.
- `iflapp_format.pack_iflapp()` acepta `icon`/`details` como `bytes` **o** ruta
  (`_as_bytes` los normaliza); pasar una ruta sin coercer daba un `TypeError`
  críptico en `len(icon)`.
- Las capturas de `assets/screenshots/` se regeneran con
  `QT_QPA_PLATFORM=offscreen python scripts/capture_screenshots.py`.
