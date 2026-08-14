#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Formato canónico de nombres de PackageMaker.

Todos los artefactos públicos deben usar exactamente:
    publisher.appname.vX.x-YY.MM-HH.MM

Las plataformas admitidas son Danenone, Knosthalij y AlphaCube.
"""

from __future__ import annotations

import re
import time
from typing import Dict, Optional, Tuple


class ProjectNameFormatter:
    """Centraliza, valida y analiza nombres de proyectos y paquetes."""

    ALLOWED_PLATFORMS = ("Danenone", "Knosthalij", "AlphaCube")
    _VERSION_PATTERN = re.compile(
        r"^v?(?P<base>\d+\.\d+(?:\.\d+)*)"
        r"(?:-(?P<timestamp>\d{2}\.\d{2}-\d{2}\.\d{2}))?"
        r"(?:-(?P<platform>Danenone|Knosthalij|AlphaCube))?$"
    )
    _PROJECT_PATTERN = re.compile(
        r"^(?P<publisher>[^.]+)\.(?P<app>[^.]+)\.v"
        r"(?P<version>\d+\.\d+(?:\.\d+)?)-"
        r"(?P<timestamp>\d{2}\.\d{2}-\d{2}\.\d{2})$"
    )

    @staticmethod
    def get_timestamp() -> str:
        """Genera la marca temporal requerida, con formato ``YY.MM-HH.MM``."""
        return time.strftime("%y.%m-%H.%M")

    @staticmethod
    def normalize_publisher(publisher: str) -> str:
        """Normaliza el publisher sin perder la capitalización declarada."""
        value = str(publisher or "").strip().replace(" ", "-")
        if not value:
            return "influent"
        if any(part in {"", ".", ".."} for part in value.split(".")):
            raise ValueError("Publisher inválido")
        if any(ch in value for ch in "/\\\\\n\r\t"):
            raise ValueError("Publisher inválido")
        return value

    @staticmethod
    def normalize_app_id(app_id: str) -> str:
        """Normaliza el identificador de aplicación en un segmento válido."""
        value = str(app_id or "").strip().lower().replace(" ", "-")
        return value or "myapp"

    @classmethod
    def normalize_platform(cls, platform: str) -> str:
        """Convierte alias de plataforma al conjunto canónico permitido."""
        value = str(platform or "").strip().lower()
        if value in {"win", "windows", "knosthalij"} or "win" in value:
            return "Knosthalij"
        if value in {"linux", "danenone"} or "lin" in value or "danen" in value:
            return "Danenone"
        if value in {"all", "multi", "multiplataforma", "alphacube", "alpha"} or "multi" in value or "alpha" in value:
            return "AlphaCube"
        raise ValueError(
            "Plataforma no compatible. Use Danenone, Knosthalij o AlphaCube."
        )

    @classmethod
    def version_components(cls, version: str) -> Tuple[str, Optional[str]]:
        """Extrae la versión completa y su timestamp.

        Acepta ``1.0``, ``1.0.0``, ``v1.0-26.08-15.38`` y la forma histórica
        con plataforma. Conserva los componentes de parche, por lo que
        ``v3.2.7-26.05-20.13`` no se trunca a ``v3.2-26.05-20.13``.
        """
        candidate = str(version or "").strip()
        match = cls._VERSION_PATTERN.fullmatch(candidate)
        if not match:
            raise ValueError(
                "Versión inválida. Use X.x o X.x.z, opcionalmente con timestamp, "
                "seguida de -YY.MM-HH.MM."
            )
        return match.group("base"), match.group("timestamp")

    @classmethod
    def format_version_vso(
        cls, version_base: str, timestamp: Optional[str] = None
    ) -> str:
        """Devuelve ``vXx.xx-YY.MM-HH.MM`` sin plataforma."""
        base, existing_timestamp = cls.version_components(version_base)
        return f"v{base}-{timestamp or existing_timestamp or cls.get_timestamp()}"

    @classmethod
    def format_version_full(
        cls, version_base: str, platform: str, timestamp: Optional[str] = None
    ) -> str:
        """Devuelve ``vX.x-YY.MM-HH.MM`` sin plataforma."""
        cls.normalize_platform(platform)  # valida la plataforma interna
        return cls.format_version_vso(version_base, timestamp)

    @classmethod
    def format_project_folder(
        cls,
        publisher: str,
        app_id: str,
        version_base: str,
        platform: str,
        timestamp: Optional[str] = None,
    ) -> str:
        """Devuelve el nombre canónico de proyecto, paquete o directorio."""
        publisher_norm = cls.normalize_publisher(publisher)
        app_norm = cls.normalize_app_id(app_id)
        version_full = cls.format_version_full(version_base, platform, timestamp)
        return f"{publisher_norm}.{app_norm}.{version_full}"

    @classmethod
    def format_package_folder(
        cls,
        publisher: str,
        app_id: str,
        version: str,
        platform: str,
        timestamp: Optional[str] = None,
    ) -> str:
        """Devuelve el mismo formato canónico para el directorio del paquete."""
        return cls.format_project_folder(publisher, app_id, version, platform, timestamp)

    @classmethod
    def format_iflapp_filename(
        cls,
        publisher: str,
        app_id: str,
        version: str,
        platform: str,
        timestamp: Optional[str] = None,
    ) -> str:
        """Devuelve el nombre canónico de archivo ``.iflapp``."""
        package_name = cls.format_package_folder(
            publisher, app_id, version, platform, timestamp
        )
        return f"{package_name}.iflapp"

    @classmethod
    def format_from_metadata(cls, metadata: Dict[str, str]) -> Dict[str, str]:
        """Genera todas las variantes sin perder la marca temporal existente."""
        publisher = metadata.get("publisher", metadata.get("empresa", "influent"))
        app_id = metadata.get("app", metadata.get("name", "myapp"))
        version = metadata.get("version", "1.0.0")
        platform = metadata.get("platform", metadata.get("plataforma", "Knosthalij"))
        version_base, timestamp = cls.version_components(version)
        timestamp = timestamp or cls.get_timestamp()
        version_vso = cls.format_version_vso(version_base, timestamp)
        version_full = cls.format_version_full(version_base, platform, timestamp)
        project_folder = cls.format_project_folder(
            publisher, app_id, version_base, platform, timestamp
        )
        return {
            "project_folder": project_folder,
            "package_folder": project_folder,
            "iflapp_filename": f"{project_folder}.iflapp",
            "version_vso": version_vso,
            "version_full": version_full,
        }

    @classmethod
    def parse_project_folder(cls, folder_name: str) -> Optional[Dict[str, str]]:
        """Analiza exclusivamente el formato público sin plataforma."""
        match = cls._PROJECT_PATTERN.fullmatch(str(folder_name or ""))
        if not match:
            return None
        return {
            "publisher": match.group("publisher"),
            "app": match.group("app"),
            "version": match.group("version"),
            "timestamp": match.group("timestamp"),
            "platform": None,
        }
