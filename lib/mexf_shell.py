# -*- coding: utf-8 -*-
"""Shell nuevo, declarado íntegramente en documentos YAML ``.mexf``.

Sustituye al shell antiguo (``shell/shellIntegration.py`` +
``shell/packagemakerShell.py``): en vez de código de registro disperso, la
integración se **declara** en el ``.mexf`` y este módulo la traduce a acciones
reales del sistema operativo:

* asociaciones de archivos y tipos MIME (``shared-mime-info`` de freedesktop y
  claves ``HKEY_CLASSES_ROOT`` en Windows);
* menús contextuales (``servicemenus`` de KDE y claves ``shell`` en Windows);
* accesos directos de escritorio y menú de aplicaciones;
* variables de entorno (``environment.d`` en Linux);
* el generador de miniaturas, reutilizado de :mod:`lib.native_shell`.

Todo es puro salvo la escritura de los ficheros de integración, de modo que el
plan se puede inspeccionar (``--shell-plan``) sin tocar el sistema.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from xml.sax.saxutils import escape

from lib.mexf_parser import parse_mexf

DEFAULT_MIME_PREFIX = "application/x-"

# Comandos declarados en el .mexf usan marcadores de shell de Windows; en
# freedesktop el fichero a abrir se pasa con ``%f``.
_EXEC_MARKER_RE = re.compile(r"%[1V]")


def _slug(value: str, fallback: str = "item") -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "-", value or "").strip("-")
    return cleaned or fallback


def _file_stem(value: str, fallback: str = "mexf") -> str:
    """Nombre de fichero seguro: sin separadores de ruta ni componentes ``..``."""
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", str(value or "")).strip(".-_")
    return cleaned or fallback


def _flat_value(value: str) -> str:
    """Aplana saltos de línea para que un valor no inyecte claves ``.desktop``."""
    return " ".join(str(value or "").splitlines())


def _default_mime(extension: str) -> str:
    ext = extension.lstrip(".").lower()
    return f"{DEFAULT_MIME_PREFIX}{ext}" if ext else ""


def _freedesktop_exec(command: str) -> str:
    return _EXEC_MARKER_RE.sub("%f", command)


@dataclass
class FileAssociation:
    extension: str
    mime_type: str = ""
    prog_id: str = ""
    description: str = ""
    icon: str = ""
    open_command: str = ""


@dataclass
class ContextMenu:
    target: str
    label: str
    command: str
    extensions: List[str] = field(default_factory=list)
    icon: str = ""


@dataclass
class ShellPlan:
    identifier: str
    name: str
    version: str = ""
    icon: str = ""
    associations: List[FileAssociation] = field(default_factory=list)
    context_menus: List[ContextMenu] = field(default_factory=list)
    shortcuts: Dict[str, Any] = field(default_factory=dict)
    environments: Dict[str, str] = field(default_factory=dict)
    registry: List[Dict[str, Any]] = field(default_factory=list)
    source_path: str = ""

    @property
    def mime_types(self) -> List[str]:
        seen: List[str] = []
        for assoc in self.associations:
            if assoc.mime_type and assoc.mime_type not in seen:
                seen.append(assoc.mime_type)
        return seen

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.identifier,
            "name": self.name,
            "version": self.version,
            "icon": self.icon,
            "source": self.source_path,
            "file_associations": [vars(a) for a in self.associations],
            "context_menus": [vars(c) for c in self.context_menus],
            "shortcuts": dict(self.shortcuts),
            "environments": dict(self.environments),
            "registry": list(self.registry),
        }


def _as_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def plan_from_document(data: Dict[str, Any], *, source_path: str = "") -> ShellPlan:
    """Normaliza las secciones de shell de un documento ``.mexf`` v1."""
    metadata = _as_dict(data.get("metadata"))
    identifier = str(metadata.get("id") or metadata.get("name") or "mexf.shell")
    name = str(metadata.get("name") or identifier)
    icon = str(data.get("icon") or "")

    associations: List[FileAssociation] = []
    for item in _as_list(data.get("file_associations") or data.get("extensions") or []):
        if not isinstance(item, dict):
            continue
        raw_ext = str(item.get("extension") or item.get("ext") or "")
        if not raw_ext:
            continue
        extension = raw_ext if raw_ext.startswith(".") else f".{raw_ext}"
        associations.append(
            FileAssociation(
                extension=extension,
                mime_type=str(item.get("mime_type") or _default_mime(extension)),
                prog_id=str(item.get("prog_id") or item.get("progid") or ""),
                description=str(item.get("description") or name),
                icon=str(item.get("default_icon") or item.get("icon") or icon),
                open_command=str(item.get("open_command") or ""),
            )
        )

    context_menus: List[ContextMenu] = []
    for item in _as_list(data.get("context_menus") or []):
        if not isinstance(item, dict):
            continue
        label = str(item.get("label") or item.get("name") or "")
        command = str(item.get("command") or item.get("exec") or "")
        if not (label and command):
            continue
        raw_exts = _as_list(item.get("extensions") or (
            [item["extension"]] if item.get("extension") else []
        ))
        extensions = [
            value if str(value).startswith(".") else f".{value}" for value in raw_exts
        ]
        context_menus.append(
            ContextMenu(
                target=str(item.get("target") or "file").lower(),
                label=label,
                command=command,
                extensions=extensions,
                icon=str(item.get("icon") or icon),
            )
        )

    environments = {
        str(key): str(value)
        for key, value in _as_dict(data.get("environments")).items()
    }
    registry = [
        item
        for item in _as_list(data.get("registry") or data.get("registry_keys") or [])
        if isinstance(item, dict)
    ]
    return ShellPlan(
        identifier=identifier,
        name=name,
        version=str(metadata.get("version") or ""),
        icon=icon,
        associations=associations,
        context_menus=context_menus,
        shortcuts=dict(_as_dict(data.get("shortcuts"))),
        environments=environments,
        registry=registry,
        source_path=source_path,
    )


def load_shell_plan(path: Path | str) -> ShellPlan:
    """Carga el plan de shell desde un ``.mexf`` o un directorio de proyecto.

    En un directorio se usa ``.mexf/main.mexf`` como documento raíz.
    """
    source = Path(path)
    if source.is_dir():
        source = source / ".mexf" / "main.mexf"
    document = parse_mexf(source, project_root=source.parent.parent if source.parent.name == ".mexf" else source.parent)
    return plan_from_document(document.data, source_path=str(source))


def render_mime_xml(plan: ShellPlan) -> str:
    """XML de ``shared-mime-info`` que declara cada asociación de archivos."""
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">',
    ]
    for assoc in plan.associations:
        if not assoc.mime_type:
            continue
        lines.append(f'  <mime-type type="{escape(assoc.mime_type)}">')
        lines.append(f"    <comment>{escape(assoc.description or plan.name)}</comment>")
        lines.append(f'    <glob pattern="*{escape(assoc.extension)}"/>')
        if assoc.icon:
            lines.append(f'    <icon name="{escape(Path(assoc.icon).stem)}"/>')
        lines.append("  </mime-type>")
    lines.append("</mime-info>")
    return "\n".join(lines) + "\n"


def _desktop_entry(*, name: str, exec_cmd: str, mime_types: List[str], icon: str) -> str:
    mime = "".join(f"{_flat_value(value)};" for value in mime_types)
    return (
        "[Desktop Entry]\n"
        "Type=Application\n"
        f"Name={_flat_value(name)}\n"
        f"Exec={_flat_value(exec_cmd)}\n"
        f"Icon={_flat_value(icon) or 'application-x-executable'}\n"
        f"MimeType={mime}\n"
        "NoDisplay=true\n"
        "Terminal=false\n"
    )


def render_desktop_entries(plan: ShellPlan) -> Dict[str, str]:
    """Un ``.desktop`` por asociación con comando de apertura."""
    entries: Dict[str, str] = {}
    stem = _file_stem(plan.identifier)
    for assoc in plan.associations:
        if not assoc.open_command:
            continue
        key = _slug(assoc.prog_id or assoc.extension.lstrip("."))
        entries[f"{stem}--{key}.desktop"] = _desktop_entry(
            name=f"{plan.name} ({assoc.description or assoc.extension})",
            exec_cmd=_freedesktop_exec(assoc.open_command),
            mime_types=[assoc.mime_type] if assoc.mime_type else [],
            icon=assoc.icon,
        )
    return entries


def render_servicemenus(plan: ShellPlan) -> Dict[str, str]:
    """``servicemenus`` de KDE a partir de los menús contextuales declarados."""
    menus: Dict[str, str] = {}
    stem = _file_stem(plan.identifier)
    for index, menu in enumerate(plan.context_menus):
        action = _slug(menu.label, f"action{index}")
        mime_types = (
            [_default_mime(ext) for ext in menu.extensions]
            if menu.target == "file" and menu.extensions
            else ["inode/directory"]
        )
        mime = "".join(f"{_flat_value(value)};" for value in mime_types)
        menus[f"{stem}--{_slug(menu.label, str(index))}.desktop"] = (
            "[Desktop Entry]\n"
            "Type=Service\n"
            "ServiceTypes=KonqPopupMenu/Plugin\n"
            f"MimeType={mime}\n"
            f"Actions={action};\n"
            f"Icon={_flat_value(menu.icon) or 'application-x-executable'}\n"
            "\n"
            f"[Desktop Action {action}]\n"
            f"Name={_flat_value(menu.label)}\n"
            f"Exec={_flat_value(_freedesktop_exec(menu.command))}\n"
        )
    return menus


def render_shortcuts(plan: ShellPlan) -> Dict[str, str]:
    """``.desktop`` de lanzador para los accesos directos declarados."""
    if not (plan.shortcuts.get("desktop") or plan.shortcuts.get("start_menu")):
        return {}
    launcher = next((a.open_command for a in plan.associations if a.open_command), "")
    if not launcher:
        return {}
    return {
        f"{_file_stem(plan.identifier)}.desktop": (
            "[Desktop Entry]\n"
            "Type=Application\n"
            f"Name={_flat_value(plan.name)}\n"
            f"Exec={_flat_value(_freedesktop_exec(launcher))}\n"
            f"Icon={_flat_value(plan.icon) or 'application-x-executable'}\n"
            "Terminal=false\n"
        )
    }


def render_environment_d(plan: ShellPlan) -> str:
    """Fichero ``environment.d`` con las variables declaradas."""
    return "".join(
        f"{_flat_value(key)}={_flat_value(value)}\n"
        for key, value in plan.environments.items()
    )


def _reg_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _reg_section(lines: List[str], path: str, values: Dict[str, str]) -> None:
    lines.append(f"[{path}]")
    for key, value in values.items():
        lines.append(f'"{key}"="{_reg_escape(str(value))}"' if key else f'@="{_reg_escape(str(value))}"')
    lines.append("")


def render_registry(plan: ShellPlan) -> str:
    """Fichero ``.reg`` con asociaciones, menús contextuales y entorno."""
    lines = ["Windows Registry Editor Version 5.00", ""]
    for assoc in plan.associations:
        prog = assoc.prog_id or assoc.mime_type
        _reg_section(lines, rf"HKEY_CLASSES_ROOT\{assoc.extension}", {"": prog})
        values = {"": assoc.description or plan.name}
        if assoc.icon:
            values["DefaultIcon"] = assoc.icon
        _reg_section(lines, rf"HKEY_CLASSES_ROOT\{prog}", values)
        if assoc.open_command:
            _reg_section(
                lines,
                rf"HKEY_CLASSES_ROOT\{prog}\shell\open\command",
                {"": assoc.open_command},
            )
    for menu in plan.context_menus:
        key = _slug(menu.label)
        if menu.target == "background":
            base = rf"Directory\Background\shell\{key}"
        elif menu.target == "folder":
            base = rf"Directory\shell\{key}"
        else:
            prog = menu.extensions[0] if menu.extensions else menu.label
            base = rf"{_slug(prog)}\shell\{key}"
        values = {"": menu.label}
        if menu.icon:
            values["Icon"] = menu.icon
        _reg_section(lines, rf"HKEY_CLASSES_ROOT\{base}", values)
        _reg_section(lines, rf"HKEY_CLASSES_ROOT\{base}\command", {"": menu.command})
    for entry in plan.registry:
        root = str(entry.get("root") or "HKEY_CLASSES_ROOT")
        path = str(entry.get("path") or "")
        raw_values = entry.get("values") or {}
        if not path or not isinstance(raw_values, dict):
            continue
        _reg_section(lines, rf"{root}\{path}", {str(k): str(v) for k, v in raw_values.items()})
    if plan.environments:
        _reg_section(lines, r"HKEY_CURRENT_USER\Environment", dict(plan.environments))
    return "\n".join(lines).rstrip() + "\n"


def _write(path: Path, content: str, written: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    written.append(str(path))


def install_plan(
    plan: ShellPlan,
    *,
    base_dir: Optional[Path | str] = None,
    platform_name: Optional[str] = None,
    thumbnailer: bool = True,
) -> Dict[str, List[str]]:
    """Escribe la integración de shell descrita por *plan*.

    Devuelve ``{"written": [...], "skipped": [...]}``; nunca lanza si el
    directorio destino no se puede escribir, informa en ``skipped``.
    """
    platform_name = platform_name or sys.platform
    written: List[str] = []
    skipped: List[str] = []

    if platform_name.startswith("win"):
        directory = Path(base_dir) if base_dir else Path.cwd()
        try:
            reg = directory / f"{_slug(plan.identifier, 'mexf')}-shell.reg"
            reg.parent.mkdir(parents=True, exist_ok=True)
            reg.write_text(render_registry(plan), encoding="utf-16")
            written.append(str(reg))
        except OSError as exc:
            skipped.append(f"{directory}: {exc}")
        return {"written": written, "skipped": skipped}

    base = Path(base_dir) if base_dir else Path.home() / ".local" / "share"
    stem = _file_stem(plan.identifier)
    try:
        if plan.associations:
            _write(base / "mime" / "packages" / f"{stem}.xml", render_mime_xml(plan), written)
        for name, content in render_desktop_entries(plan).items():
            _write(base / "applications" / name, content, written)
        for name, content in render_servicemenus(plan).items():
            _write(base / "kio" / "servicemenus" / name, content, written)
        if plan.environments:
            _write(
                Path.home() / ".config" / "environment.d" / f"{stem}.conf",
                render_environment_d(plan),
                written,
            )
        if thumbnailer:
            from lib.native_shell import write_thumbnailer

            written.append(str(write_thumbnailer(base / "thumbnailers")))
        for name, content in render_shortcuts(plan).items():
            _write(base / "applications" / name, content, written)
    except OSError as exc:
        skipped.append(f"{base}: {exc}")
    return {"written": written, "skipped": skipped}


def uninstall_plan(
    plan: ShellPlan,
    *,
    base_dir: Optional[Path | str] = None,
    platform_name: Optional[str] = None,
) -> Dict[str, List[str]]:
    """Retira los ficheros escritos por :func:`install_plan`."""
    platform_name = platform_name or sys.platform
    removed: List[str] = []
    skipped: List[str] = []

    if platform_name.startswith("win"):
        directory = Path(base_dir) if base_dir else Path.cwd()
        reg = directory / f"{_slug(plan.identifier, 'mexf')}-shell.reg"
        try:
            if reg.exists():
                reg.unlink()
                removed.append(str(reg))
        except OSError as exc:
            skipped.append(f"{reg}: {exc}")
        return {"removed": removed, "skipped": skipped}

    base = Path(base_dir) if base_dir else Path.home() / ".local" / "share"
    stem = _file_stem(plan.identifier)
    targets = [base / "mime" / "packages" / f"{stem}.xml"]
    targets += [base / "applications" / name for name in render_desktop_entries(plan)]
    targets += [base / "kio" / "servicemenus" / name for name in render_servicemenus(plan)]
    targets += [base / "applications" / name for name in render_shortcuts(plan)]
    targets.append(Path.home() / ".config" / "environment.d" / f"{stem}.conf")
    for target in targets:
        try:
            if target.exists():
                target.unlink()
                removed.append(str(target))
        except OSError as exc:
            skipped.append(f"{target}: {exc}")
    return {"removed": removed, "skipped": skipped}


if __name__ == "__main__":
    import json

    args = sys.argv[1:]
    if args and args[0] == "--plan":
        print(json.dumps(load_shell_plan(args[1]).to_dict(), indent=2, ensure_ascii=False))
        raise SystemExit(0)
    print("uso: -m lib.mexf_shell --plan MEXF", file=sys.stderr)
    raise SystemExit(2)
