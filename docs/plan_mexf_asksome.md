# Plan: shell MEXF, compilador `.asksome`, instalador y `removeme`

Plan por partes de las funciones grandes descritas en `bugs.txt`. No forma
parte de la ronda de bugfixes ya aplicada: es un mapa de trabajo por fases, con
el estado actual del repositorio como punto de partida.

## Punto de partida (lo que ya existe)

- `example.mexf` — hoy es **JSON** con `extensions`, `context_menus`,
  `shell_commands`, `file_associations`, `shortcuts`, `registry_keys`.
- `shell/shellIntegration.py`, `shell/packagemakerShell.py` — integración de
  shell multiplataforma (registro/acciones directas/contexto).
- `lib/cliHandler.py` — acciones `install_mexf`, `edit_mexf`, `create_mexf` y el
  conjunto headless (`--list-compilers`, `--inspect`, ...).
- `lib/compilers.py` — backends `nuitka`/`pyinstaller`/`zipapp`/`cxfreeze`/
  `pyoxidizer` con firma única `CompilerBackend.compile(...)`.
- `lib/iflapp_format.py` — contenedor `.iflapp` v2 (cabecera + payload firmado
  HMAC-SHA256), `verify_iflapp`, `read_iflapp_header`.
- `lib/dropper.py` — dropper `.run` autoextraíble con el `.iflapp` embebido.
- `lib/BuildThread.py` — orquesta compilar → empaquetar → verificar → limpiar y
  ahora registra el procedimiento real detrás del `.iflapp`.

## Fase 1 — Lenguaje MEXF (YAML) y parser

1. Definir el esquema YAML: `metadata`, `imports`, `triggers`, `commands`,
   `registry`, `extensions`, `shortcuts`, `strings`, `environments`,
   `file_associations`, `context_menus`, `actions`, `install`/`uninstall`.
2. `lib/mexf/parser.py`: cargar `details.xml` → `/.mexf/main.mexf` → resto de
   `*.mexf` de la carpeta; permitir `imports:` de otros mexf como librerías.
3. `lib/mexf/schema.py`: validación con errores localizados (línea/columna).
4. Migrar `example.mexf` a YAML y conservar un lector de compatibilidad JSON.

## Fase 2 — Compilador MEXF → `.asksome`

1. `lib/mexf/compiler.py`: MEXF → binario propio `.asksome` con cabecera
   encriptada, launcher independiente y *assets* por rutas.
2. Reutilizar `lib/compilers.py` para producir el *engine* por plataforma
   (Nuitka por defecto; `zipapp` como respaldo siempre disponible).
3. Manifiesto basado en `metadata`/`title`; generación de registros
   multiplataforma y scripts de comando por SO.
4. Integrar en `FlangCompiler.run()` **antes** de compilar los `.iflapp`:
   compilar todos los `.asksome`, envolver para probar sintaxis/entorno y luego
   empaquetar.

## Fase 3 — Instalador `.iflapp` tipo AppX

1. `lib/installer.py`: instalar el `.iflapp` con accesos directos (escritorio,
   menú inicio, taskbar) y registro de instalación multiplataforma.
2. Registrar en `details.xml` la sección de instalación y reutilizar
   `updater.py`/`updater.exe`/`updater.elf` para el ciclo de vida.
3. Entrada headless nueva en `main()` (`--install-package`, ...) y acciones de
   shell correspondientes.

## Fase 4 — `removeme.py` (desinstalador)

1. Plantilla `templates/removeme.py`: proceso inverso (elimina shell asksome,
   integraciones, archivos y accesos directos) con líneas de comando silenciosas
   y personalizadas.
2. Interfaz PyQt6 basada en `leviathan_ui` para los pasos en tiempo real, con
   respaldo no-op cuando la dependencia no está instalada (regla del repo).

## Fase 5 — Editor MEXF y debugger

1. Editor con resaltado YAML, probador de sintaxis y debugger, usando los
   *engines* de PackageMaker.
2. Botón/acción en la página correspondiente + acción headless.

## Fase 6 — Extras

- Shell nativo (py/dll/so) para revelar iconos e info de cada paquete al hacer
  hover y en el panel de propiedades de cada SO.
- Editor de proyectos `.iflapp` desde cero con debugger y compilador.

## Reglas transversales

- La ley de nombres y la estructura obligatoria se aplican a **todo** artefacto
  nuevo (`ProjectNameFormatter`, `tests/test_canonical_law_and_structure.py`).
- Cualquier acción "de shell" nueva debe añadirse a la lista headless de
  `main()` en `packagemaker.py`.
- `lib/design_tokens.py` sigue siendo la única fuente de estilos.
