"""Motor de addons del sidebar.

Cada entrada del sidebar es un addon declarado en ``lib/addons/<id>.yaml``. El YAML
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
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional

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


#: Respaldo si falta ``lib/addons/`` (bundle incompleto, instalación a medias).
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


def _read_directory(directory: Path, *, strict: bool, errors: List[str]) -> List[Addon]:
    addons: List[Addon] = []
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
    return addons


#: ``lib/addons/`` es la ubicación de los manifiestos que viajan con la app.
#: ``addons/`` en la raíz se conserva para bundles antiguos (compatibilidad).
SHIPPED_ADDONS_DIR = Path(__file__).resolve().parent / "addons"
LEGACY_ADDONS_DIR = Path(__file__).resolve().parent.parent / "addons"
#: Extensiones instaladas desde Configuración. Va la última: un addon del
#: usuario nunca puede suplantar una entrada incluida (el primero gana por id).
USER_ADDONS_DIR = Path(__file__).resolve().parent.parent / "data" / "addons"


def shipped_addons_dirs() -> List[Path]:
    """Directorios de manifiestos incluidos, por precedencia (primero gana)."""
    return [d for d in (SHIPPED_ADDONS_DIR, LEGACY_ADDONS_DIR) if d.is_dir()]


def user_addons_dir() -> Path:
    """Directorio de extensiones instaladas por el usuario (puede no existir)."""
    override = os.environ.get("PM_USER_ADDONS_DIR")
    return Path(override) if override else USER_ADDONS_DIR


def all_addons_dirs() -> List[Path]:
    """Directorios de carga: incluidos, compatibilidad y usuario, en ese orden."""
    directories = shipped_addons_dirs()
    user = user_addons_dir()
    if user not in directories:
        directories.append(user)
    return directories


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

    addons = _read_directory(directory, strict=strict, errors=errors)
    addons.sort(key=lambda a: (SECTIONS.index(a.section), a.order, a.id))
    Addon.skipped = errors  # type: ignore[attr-defined]
    if not addons and not strict:
        errors.append(f"sin manifiestos en {directory}: se usan los addons por defecto")
        return fallback_addons()
    return addons


def load_addons_from_dirs(directories: Iterable[Path], *, strict: bool = False) -> List[Addon]:
    """Carga manifiestos de varios directorios; el primero gana por ``id``.

    Sirve para combinar la ubicación incluida (``lib/addons/``) con la ruta de
    compatibilidad (``addons/``) sin duplicar entradas. Los directorios que no
    existan se ignoran.
    """
    if yaml is None:
        if strict:
            raise AddonError("PyYAML no está instalado: no se pueden leer los addons")
        Addon.skipped = ["PyYAML no está instalado: se usan los addons por defecto"]
        return fallback_addons()

    merged: Dict[str, Addon] = {}
    errors: List[str] = []
    for directory in directories:
        directory = Path(directory)
        if not directory.is_dir():
            continue
        for addon in _read_directory(directory, strict=strict, errors=errors):
            merged.setdefault(addon.id, addon)

    addons = sorted(merged.values(), key=lambda a: (SECTIONS.index(a.section), a.order, a.id))
    Addon.skipped = errors  # type: ignore[attr-defined]
    if not addons and not strict:
        errors.append("sin manifiestos: se usan los addons por defecto")
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


def installed_addons() -> List[Addon]:
    """Manifiestos instalados por el usuario, sin el respaldo integrado.

    ``load_addons()`` cae a ``DEFAULT_ADDONS`` cuando el directorio no existe;
    para listar sólo lo que instaló el usuario hace falta leer el directorio
    tal cual.
    """
    directory = user_addons_dir()
    if yaml is None or not directory.is_dir():
        return []
    return _read_directory(directory, strict=False, errors=[])


def install_addon(
    source: Path, *, target_dir: Optional[Path] = None, host: Any = None
) -> Path:
    """Valida e instala un manifiesto ``.yaml`` en el directorio de usuario.

    La validación es la misma que aplica el cargador (``parse_manifest``) más
    las comprobaciones que evitan dejar una extensión que no pueda construirse:

    - el ``id`` no puede pertenecer a un addon incluido (nunca se suplanta una
      página del sistema);
    - un ``builder`` debe existir en el anfitrión cuando se pasa ``host``;
    - ``class`` debe tener el formato ``modulo:Clase``;
    - ``plugin`` se rechaza: el ``.py`` viajaría junto al manifiesto y se
      ejecutaría al arrancar, que es el alcance de Q-031 (extensiones
      empaquetadas con lista de confianza y firma).

    Devuelve la ruta del manifiesto instalado. Lanza ``AddonError`` con el
    motivo si no se puede instalar.
    """
    source = Path(source)
    if source.suffix.lower() not in (".yaml", ".yml"):
        raise AddonError(f"{source.name}: la extensión debe ser un fichero .yaml")
    if not source.is_file():
        raise AddonError(f"{source.name}: no existe el fichero")
    if yaml is None:
        raise AddonError("PyYAML no está instalado: no se pueden validar extensiones")

    try:
        text = source.read_text(encoding="utf-8")
    except OSError as exc:
        raise AddonError(f"{source.name}: {exc}") from exc
    try:
        data = yaml.safe_load(text)
    except Exception as exc:
        raise AddonError(f"{source.name}: YAML inválido ({exc})") from exc

    addon = parse_manifest(data, source)
    if addon is None:
        raise AddonError(f"{source.name}: el manifiesto está desactivado (enabled: false)")

    shipped_ids = {a.id for a in load_addons_from_dirs(shipped_addons_dirs())}
    if addon.id in shipped_ids:
        raise AddonError(
            f"{source.name}: el id '{addon.id}' pertenece a un addon incluido "
            "y no se puede reemplazar"
        )
    if addon.kind == "plugin":
        raise AddonError(
            f"{source.name}: las extensiones con 'plugin' se instalan como paquete "
            "firmado, no como manifiesto suelto"
        )
    if addon.kind == "class":
        module_name, _, attr = addon.class_path.partition(":")
        if not module_name or not attr:
            raise AddonError(f"{source.name}: 'class' debe ser 'modulo:Clase'")
    if addon.kind == "builder" and host is not None:
        if not callable(getattr(host, addon.builder, None)):
            raise AddonError(f"{source.name}: el anfitrión no tiene {addon.builder}()")

    directory = Path(target_dir) if target_dir is not None else user_addons_dir()
    destination = directory / f"{addon.id}.yaml"
    temporary = destination.with_name(f".{addon.id}.yaml.tmp")
    try:
        directory.mkdir(parents=True, exist_ok=True)
        temporary.write_text(text, encoding="utf-8")
        os.replace(temporary, destination)
    except OSError as exc:
        raise AddonError(f"{source.name}: no se pudo copiar a {directory} ({exc})") from exc
    finally:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
    return destination
