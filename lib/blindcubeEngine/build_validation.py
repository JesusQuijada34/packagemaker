# -*- coding: utf-8 -*-
"""Validación estricta de los campos que alimentan una compilación.

El formulario de compilación aceptaba cualquier cosa y rellenaba los huecos con
valores por defecto (``influent``, ``mycoolapp``, ``1.0``), de modo que al dejar
un campo vacío el sistema "adivinaba" y compilaba con los datos del proyecto
anterior. Este módulo es la puerta única: si un campo clave está vacío o no
cumple el formato, la compilación se bloquea.

``ProjectNameFormatter`` sigue siendo permisivo a propósito (normaliza lo que el
usuario teclea en la creación); aquí se valida lo que ya debería estar escrito
antes de empaquetar.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

from lib.i18n import tr
from lib.projectNameFormatter import ProjectNameFormatter

_SEGMENT = re.compile(r"^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$")
# Se acepta ``1`` y ``v2`` porque el campo es libre y
# ``normalize_version_base`` completa el componente menor; lo que se bloquea es
# el campo vacío o un valor sin números (que antes caía en silencio a ``1.0``).
_VERSION = re.compile(r"^v?\d+(?:\.\d+)*$")


@dataclass(frozen=True)
class FieldError:
    """Un campo inválido y el motivo, listos para mostrarse en la alerta."""

    field: str
    message: str


def _segment_error(field: str, value: str, *, label_key: str) -> Optional[FieldError]:
    label = tr(label_key)
    if not value:
        return FieldError(field, tr("build.validation_empty").format(field=label))
    if not _SEGMENT.fullmatch(value):
        return FieldError(field, tr("build.validation_segment").format(field=label))
    return None


def validate_build_fields(
    empresa: str,
    nombre: str,
    version: str,
    plataforma: str = "",
) -> List[FieldError]:
    """Devuelve los errores que impiden compilar; lista vacía si todo es válido.

    Es intencionadamente estricta: no completa componentes que falten ni
    sustituye valores ausentes por defectos, para no heredar datos fantasma.
    """
    errors: List[FieldError] = []

    for field, value, label_key in (
        ("empresa", str(empresa or "").strip(), "build.field_company"),
        ("nombre", str(nombre or "").strip().lower(), "build.field_app"),
    ):
        error = _segment_error(field, value, label_key=label_key)
        if error is not None:
            errors.append(error)

    candidate = str(version or "").strip()
    if not candidate:
        errors.append(
            FieldError(
                "version",
                tr("build.validation_empty").format(field=tr("build.version")),
            )
        )
    elif not _VERSION.fullmatch(candidate):
        errors.append(FieldError("version", tr("build.validation_version")))

    platform = str(plataforma or "").strip()
    if platform:
        try:
            ProjectNameFormatter.normalize_platform(platform)
        except ValueError:
            errors.append(FieldError("plataforma", tr("build.validation_platform")))

    return errors


def format_errors(errors: List[FieldError]) -> str:
    """Une los errores en un texto legible para la alerta nativa."""
    return "\n".join(f"• {error.message}" for error in errors)


__all__ = ["FieldError", "validate_build_fields", "format_errors"]
