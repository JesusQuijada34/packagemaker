# AGENTS.md — PackageMaker

Identidad: `Influent.packagemaker.v3.2.7-26.05-20.13-AlphaCube` (JesusQuijada34).
Repo: `https://github.com/JesusQuijada34/packagemaker.git`, rama de trabajo `main`.

## Flujo de trabajo
- Ejecutar la suite: `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`.
- Análisis estático: `python -m pyflakes .` (los `imported but unused` suelen ser
  ruido aceptable; las redefiniciones dentro de funciones son imports locales).
- Compilar sin arrancar la GUI: `python -m py_compile $(git ls-files '*.py')`.
- CLI headless (sin ventana): `--list-compilers`, `--list-hardening`,
  `--inspect <archivo>`, `--list-fonts`. Cualquier acción nueva "de shell" debe
  añadirse a la lista headless de `main()` en `packagemaker.py`, o el flujo
  seguirá como si fuera una ventana.

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
