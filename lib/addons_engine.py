"""Motor de addons del sidebar.

Cada entrada del sidebar es un addon declarado en ``addons/<id>.yaml``. El YAML
manifiesta *qué* es el addon; este módulo decide *cómo* se construye.

Manifiesto mínimo::

    id: report
    order: 50
    section: tools            # main | tools | footer
    label: sidebar.report     # clave de i18n, no texto literal
    description: sidebar_desc.6
    icon: report
    builder: build_report_page

Campos:

``id``
    Identificador estable. Es también el nombre del fichero y la clave con la
    que se guarda el estado, así que no debe cambiar al reordenar.
``order``
    Posición dentro de su sección. Los huecos (10, 20, 30…) dejan sitio para
    insertar addons ajenos sin renumerar.
``section``
    ``main`` (arriba), ``tools`` (bajo el bloque de contexto) o ``footer``
    (al final, junto a «Acerca de»).
``label`` / ``description`` / ``icon``
    Claves de traducción y nombre del icono en ``lib/app_icons.py``.
``builder``
    Método de ``PackageTodoGUI`` que devuelve el ``QWidget`` de la página.
``class``
    Alternativa a ``builder``: ``ruta.del.modulo:Clase``. Se instancia sin
    argumentos y debe ser un ``QWidget``.
``plugin``
    Alternativa a las dos anteriores: ruta a un ``.py`` que define
    ``build(host)``.
``enabled``
    ``false`` deja el addon fuera del sidebar sin borrar su fichero.
``requires``
    Dependencias que deben importarse para que el addon se cargue.
"""

from __future__ import annotations

import importlib
import importlib.util
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

try:  # PyYAML es una dependencia de la app, pero el motor no debe romperse sin ella.
    import yaml
except Exception:  # pragma: no cover - sólo en entornos mínimos
    yaml = None


SECTIONS = ("main", "tools", "footer")

_ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")


class AddonError(ValueError):
    """Manifiesto inválido. El mensaje nombra el fichero para poder corregirlo."""


@dataclass
class Addon:
    """Un addon ya validado, listo para construir su página."""

    id: str
    order: int
    section: str
    label: str
    icon: str
    description: str = ""
    builder: str = ""
    class_path: str = ""
    plugin: str = ""
    requires: List[str] = field(default_factory=list)
    source: Path = Path()

    @property
    def kind(self) -> str:
        if self.class_path:
            return "class"
        if self.plugin:
            return "plugin"
        return "builder"

    def build(self, host: Any) -> Any:
        """Construye la página. Propaga el error para que el llamante decida."""
        if self.class_path:
            module_name, _, attr = self.class_path.partition(":")
            if not attr:
                raise AddonError(f"{self.source.name}: 'class' debe ser 'modulo:Clase'")
            return getattr(importlib.import_module(module_name), attr)()
        if self.plugin:
            path = (self.source.parent / self.plugin).resolve()
            if not path.is_file():
                raise AddonError(f"{self.source.name}: no existe el plugin {self.plugin}")
            spec = importlib.util.spec_from_file_location(
                f"pm_addon_{self.id}", path
            )
            if spec is None or spec.loader is None:
                raise AddonError(f"{self.source.name}: plugin ilegible {self.plugin}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            entry = getattr(module, "build", None)
            if not callable(entry):
                raise AddonError(f"{self.source.name}: el plugin no define build(host)")
            return entry(host)
        if not self.builder:
            raise AddonError(f"{self.source.name}: sin builder, class ni plugin")
        factory: Optional[Callable] = getattr(host, self.builder, None)
        if not callable(factory):
            raise AddonError(f"{self.source.name}: el host no tiene {self.builder}()")
        return factory()


def _require(mapping: Dict[str, Any], key: str, source: Path) -> Any:
    if key not in mapping or mapping[key] in (None, ""):
        raise AddonError(f"{source.name}: falta el campo obligatorio '{key}'")
    return mapping[key]


def parse_manifest(data: Any, source: Path) -> Optional[Addon]:
    """Valida un manifiesto ya deserializado. Devuelve ``None`` si está desactivado."""
    if not isinstance(data, dict):
        raise AddonError(f"{source.name}: el manifiesto debe ser un mapa YAML")

    addon_id = str(_require(data, "id", source))
    if not _ID_RE.match(addon_id):
        raise AddonError(
            f"{source.name}: 'id' debe ser minúsculas, dígitos o guion bajo"
        )
    if addon_id != source.stem:
        raise AddonError(
            f"{source.name}: 'id' ({addon_id}) debe coincidir con el nombre del fichero"
        )

    section = str(data.get("section") or "tools")
    if section not in SECTIONS:
        raise AddonError(
            f"{source.name}: 'section' debe ser uno de {', '.join(SECTIONS)}"
        )

    try:
        order = int(data.get("order", 100))
    except (TypeError, ValueError) as exc:
        raise AddonError(f"{source.name}: 'order' debe ser un entero") from exc

    if data.get("enabled", True) is False:
        return None

    kinds = [k for k in ("builder", "class", "plugin") if data.get(k)]
    if len(kinds) > 1:
        raise AddonError(
            f"{source.name}: usa sólo uno de builder, class o plugin (hay {len(kinds)})"
        )
    if not kinds:
        raise AddonError(
            f"{source.name}: necesita builder, class o plugin para construir la página"
        )

    requires = data.get("requires") or []
    if isinstance(requires, str):
        requires = [requires]
    if not isinstance(requires, list):
        raise AddonError(f"{source.name}: 'requires' debe ser una lista")

    return Addon(
        id=addon_id,
        order=order,
        section=section,
        label=str(_require(data, "label", source)),
        icon=str(data.get("icon") or addon_id),
        description=str(data.get("description") or ""),
        builder=str(data.get("builder") or ""),
        class_path=str(data.get("class") or ""),
        plugin=str(data.get("plugin") or ""),
        requires=[str(r) for r in requires],
        source=source,
    )


#: Respaldo si falta ``addons/`` (bundle incompleto, instalación a medias).
#: Sin él la ventana abriría con el sidebar vacío y sin páginas.
DEFAULT_ADDONS = (
    ("create", 10, "main", "sidebar.create", "sidebar_desc.0", "crear", "build_create_page"),
    ("build", 20, "main", "sidebar.build", "sidebar_desc.1", "construir", "build_build_page"),
    ("config", 30, "main", "sidebar.config", "sidebar_desc.3", "config", "build_config_page"),
    ("moonfix", 40, "main", "sidebar.moonfix", "sidebar_desc.4", "moonfix", "build_moonfix_page"),
    ("report", 10, "tools", "sidebar.report", "sidebar_desc.6", "report", "build_report_page"),
    ("help", 15, "tools", "sidebar.help", "sidebar_desc.8", "help", "build_help_page"),
    ("aide", 20, "tools", "sidebar.aide", "sidebar_desc.7", "aide", "build_aide_page"),
    ("about", 10, "footer", "sidebar.about", "sidebar_desc.5", "about", "build_about_page"),
)


def fallback_addons() -> List[Addon]:
    """Addons por defecto, equivalentes a los manifiestos que viajan con la app."""
    addons = [
        Addon(
            id=addon_id,
            order=order,
            section=section,
            label=label,
            icon=icon,
            description=description,
            builder=builder,
        )
        for addon_id, order, section, label, description, icon, builder in DEFAULT_ADDONS
    ]
    return sorted(addons, key=lambda a: (SECTIONS.index(a.section), a.order, a.id))


def load_addons(directory: Path, *, strict: bool = False) -> List[Addon]:
    """Carga y ordena los manifiestos de *directory*.

    Un manifiesto roto se ignora y se anota en ``Addon.skipped`` para que la
    interfaz siga abriendo: perder una extensión no debe impedir usar la app.
    Con ``strict=True`` el error se propaga, que es lo que quieren los tests y
    el CLI de validación.
    """
    directory = Path(directory)
    errors: List[str] = []
    addons: List[Addon] = []

    if yaml is None:
        if strict:
            raise AddonError("PyYAML no está instalado: no se pueden leer los addons")
        # Sin PyYAML no se pueden leer los manifiestos, pero la ventana debe
        # abrir: se usan los addons integrados en vez de dejar el sidebar vacío.
        Addon.skipped = ["PyYAML no está instalado: se usan los addons por defecto"]
        return fallback_addons()

    if not directory.is_dir():
        if strict:
            return addons
        Addon.skipped = [f"no existe {directory}: se usan los addons por defecto"]
        return fallback_addons()

    for path in sorted(directory.glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            addon = parse_manifest(data, path)
        except AddonError as exc:
            if strict:
                raise
            errors.append(str(exc))
            continue
        except Exception as exc:  # YAML inválido, permisos, encoding…
            if strict:
                raise AddonError(f"{path.name}: {exc}") from exc
            errors.append(f"{path.name}: {exc}")
            continue
        if addon is not None:
            addons.append(addon)

    addons.sort(key=lambda a: (SECTIONS.index(a.section), a.order, a.id))
    Addon.skipped = errors  # type: ignore[attr-defined]
    if not addons and not strict:
        errors.append(f"sin manifiestos en {directory}: se usan los addons por defecto")
        return fallback_addons()
    return addons


def validate_directory(directory: Path) -> List[str]:
    """Devuelve la lista de problemas; vacía si todo está correcto."""
    try:
        load_addons(directory, strict=True)
    except AddonError as exc:
        return [str(exc)]
    return []


def missing_requirements(addon: Addon) -> List[str]:
    """Módulos de ``requires`` que no se pueden importar ahora mismo."""
    missing = []
    for module_name in addon.requires:
        try:
            importlib.import_module(module_name)
        except Exception:
            missing.append(module_name)
    return missing
