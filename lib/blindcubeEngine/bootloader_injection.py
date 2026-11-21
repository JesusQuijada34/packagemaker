# -*- coding: utf-8 -*-
"""Inyección de un *bootloader* de splash en los guiones de un proyecto iflapp.

Fase 3 de ``bugs.md``. Al compilar un proyecto que usa PyQt6 o ``leviathan_ui``,
PackageMaker debe:

1. **Copiar** :mod:`lib.splash_bootloader` a la carpeta ``lib/`` del proyecto.
2. **Inyectar** en el guion dos bloques (AST, no regex):

   * *Cabecera (post-imports)*: arma el bootloader justo después del bloque de
     ``import``, para que el splash se dibuje antes que la UI pesada.
   * *Cierre (post-UI init)*: arranca el splash tras crear la ``QApplication``
     y lo desvanece justo antes del bucle de eventos (o tras el primer
     ``.show()``).

El guion nunca se modifica en el sitio: se escribe una copia
``<guion>_pmboot.py`` junto al original (para que los assets relativos sigan
resolviéndose) y esa copia es la que se compila. La copia se elimina al
terminar.
"""

from __future__ import annotations

import ast
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

SPLASH_MODULE = "lib.splash_bootloader"
_SPLASH_FILENAME = "splash_bootloader.py"
_SUFFIX = "_pmboot.py"
# Marcadores que hacen la inyección idempotente y detectable.
_HEADER_MARKER = "# [PackageMaker] bootloader de splash (inyectado)"
_SENTINEL = "_pm_splash"

# Frameworks GUI que declaran el punto de entrada y la ventana principal.
FRAMEWORK_MODULES = ("PyQt6", "leviathan_ui")


def _header_block() -> str:
    return (
        f"{_HEADER_MARKER}\n"
        "try:\n"
        f"    from {SPLASH_MODULE} import bootloader as {_SENTINEL}\n"
        f"    {_SENTINEL}.arm(__file__)\n"
        "except Exception:\n"
        f"    {_SENTINEL} = None\n"
    )


def _start_block() -> str:
    return (
        f"if {_SENTINEL} is not None:\n"
        f"    {_SENTINEL}.start()\n"
    )


def _finish_block() -> str:
    return (
        f"if {_SENTINEL} is not None:\n"
        f"    {_SENTINEL}.finish()\n"
    )


def _iter_top_level(tree: ast.Module):
    for node in tree.body:
        yield node


def _header_insert_line(tree: ast.Module) -> int:
    """Línea (1-based) tras la que va la cabecera del bootloader.

    Se salta el docstring del módulo y los ``from __future__`` y avanza por el
    bloque contiguo de ``import``/``from ... import`` de nivel superior.
    """
    line = 0
    seen_import = False
    for node in _iter_top_level(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str) and not seen_import and line == 0:
            line = getattr(node, "end_lineno", node.lineno)
            continue
        if isinstance(node, ast.ImportFrom) and node.module == "__future__" and not seen_import:
            line = getattr(node, "end_lineno", node.lineno)
            continue
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            line = getattr(node, "end_lineno", node.lineno)
            seen_import = True
            continue
        break
    return line


def _is_qapplication_call(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if isinstance(func, ast.Name):
        return func.id == "QApplication"
    if isinstance(func, ast.Attribute):
        return func.attr == "QApplication"
    return False


def _find_qapplication_line(tree: ast.Module) -> Optional[int]:
    for node in ast.walk(tree):
        if _is_qapplication_call(node):
            return getattr(node, "end_lineno", node.lineno)
    return None


def _is_event_loop_call(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in ("exec", "exec_")
    )


def _find_event_loop_line(tree: ast.Module) -> Optional[int]:
    found = None
    for node in ast.walk(tree):
        if _is_event_loop_call(node):
            line = getattr(node, "lineno", None)
            if line is not None and (found is None or line < found):
                found = line
    return found


def _is_show_call(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "show"
    )


def _find_show_line(tree: ast.Module) -> Optional[int]:
    found = None
    for node in ast.walk(tree):
        if _is_show_call(node):
            line = getattr(node, "end_lineno", node.lineno)
            if found is None or line < found:
                found = line
    return found


def script_uses_framework(source: str) -> bool:
    """``True`` si el guion importa PyQt6 o ``leviathan_ui``."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name.split(".")[0] in FRAMEWORK_MODULES for alias in node.names):
                return True
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] in FRAMEWORK_MODULES:
                return True
    return False


def _indent_block(block: str, indent: str) -> str:
    """Indenta cada línea no vacía de *block* con *indent*."""
    if not indent:
        return block
    return "".join(
        (indent + line) if line.strip() else line
        for line in block.splitlines(keepends=True)
    )


def _leading_ws(line: str) -> str:
    return line[: len(line) - len(line.lstrip())]


def inject_source(source: str) -> Tuple[str, bool]:
    """Devuelve ``(fuente, cambiada)`` con los bloques del bootloader.

    Idempotente: si la sentinela ya está presente no toca nada. Ante un error
    de sintaxis devuelve la fuente original sin cambios. Cada bloque se indenta
    al nivel de la línea de referencia para no romper el cuerpo de funciones.
    """
    if _SENTINEL in source:
        return source, False
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source, False

    lines = source.splitlines(keepends=True)
    insertions: List[Tuple[int, str, str]] = []

    header_at = _header_insert_line(tree)
    header_ref = lines[header_at - 1] if 0 < header_at <= len(lines) else ""
    insertions.append((header_at, _header_block(), _leading_ws(header_ref)))

    app_line = _find_qapplication_line(tree)
    if app_line is not None:
        app_ref = lines[app_line - 1] if 0 < app_line <= len(lines) else ""
        insertions.append((app_line, _start_block(), _leading_ws(app_ref)))

    finish_at = _find_event_loop_line(tree)
    if finish_at is not None:
        finish_ref = lines[finish_at - 1] if 0 < finish_at <= len(lines) else ""
        insertions.append((finish_at - 1, _finish_block(), _leading_ws(finish_ref)))
    else:
        show_at = _find_show_line(tree)
        if show_at is not None:
            show_ref = lines[show_at - 1] if 0 < show_at <= len(lines) else ""
            insertions.append((show_at, _finish_block(), _leading_ws(show_ref)))

    # De abajo hacia arriba para no desplazar los índices pendientes.
    for at, block, indent in sorted(insertions, key=lambda item: item[0], reverse=True):
        at = max(0, min(at, len(lines)))
        text = _indent_block(block, indent)
        if not text.endswith("\n"):
            text += "\n"
        lines.insert(at, text)
    return "".join(lines), True


def inject_file(path: Path | str) -> bool:
    """Inyecta el bootloader en *path* (in situ). ``True`` si hubo cambios."""
    path = Path(path)
    try:
        source = path.read_text(encoding="utf-8")
    except OSError:
        return False
    new_source, changed = inject_source(source)
    if changed:
        path.write_text(new_source, encoding="utf-8")
    return changed


def copy_splash_library(project_root: Path | str) -> List[Path]:
    """Copia el módulo de splash a ``<proyecto>/lib`` y garantiza el paquete.

    Devuelve las rutas escritas (``__init__.py`` incluido si faltaba).
    """
    project_root = Path(project_root)
    lib_dir = project_root / "lib"
    lib_dir.mkdir(parents=True, exist_ok=True)
    written: List[Path] = []

    init = lib_dir / "__init__.py"
    if not init.exists():
        init.write_text(
            '# -*- coding: utf-8 -*-\n"""Paquete del proyecto (generado)."""\n',
            encoding="utf-8",
        )
        written.append(init)

    target = lib_dir / _SPLASH_FILENAME
    source = Path(__file__).resolve().parent / _SPLASH_FILENAME
    if source.is_file():
        shutil.copy2(source, target)
        written.append(target)
    return written


def write_injected_copy(script_path: Path | str) -> Optional[Path]:
    """Escribe ``<guion>_pmboot.py`` con la inyección y devuelve su ruta.

    ``None`` si el guion no usa un framework soportado o no se pudo leer. La
    copia se coloca junto al original para que los assets relativos sigan
    resolviéndose durante la compilación.
    """
    script_path = Path(script_path)
    try:
        source = script_path.read_text(encoding="utf-8")
    except OSError:
        return None
    if not script_uses_framework(source):
        return None
    new_source, _ = inject_source(source)
    target = script_path.with_name(f"{script_path.stem}{_SUFFIX}")
    target.write_text(new_source, encoding="utf-8")
    return target


def prepare_for_build(
    script_path: Path | str,
    project_root: Path | str,
) -> Optional[Path]:
    """Prepara el guion a compilar: copia la librería e inyecta el bootloader.

    Devuelve la ruta del guion a compilar (la copia inyectada) o ``None`` si no
    procede inyectar, en cuyo caso debe compilarse el original.
    """
    project_root = Path(project_root)
    injected = write_injected_copy(script_path)
    if injected is None:
        return None
    copy_splash_library(project_root)
    return injected


def cleanup_injected_copy(script_path: Path | str) -> None:
    """Elimina la copia ``_pmboot`` si existe (no toca el original)."""
    script_path = Path(script_path)
    target = script_path.with_name(f"{script_path.stem}{_SUFFIX}")
    try:
        if target.is_file():
            target.unlink()
    except OSError:
        pass
