# -*- coding: utf-8 -*-
"""Descarga, caché y registro versátil de las fuentes de la interfaz.

Las familias preferidas (Roboto, Inter, Noto Sans, Open Sans) no están
instaladas en todos los sistemas. Este módulo las obtiene de Google Fonts,
las guarda en ``data/fonts/`` y las registra en Qt con
``QFontDatabase.addApplicationFont``, de modo que la interfaz use siempre la
tipografía prevista sin depender de lo que traiga el sistema operativo.

Garantías:

* **Integridad**: cada fuente tiene un SHA-256 esperado; una descarga que no
  coincida se descarta.
* **Espejos**: se prueban varias URL (raw.githubusercontent + CDN jsDelivr)
  antes de rendirse.
* **Sin bloqueos**: si no hay red, se usan las copias en caché o el sistema.
* **Sin efectos en import**: el registro en Qt sólo ocurre tras crear
  ``QGuiApplication``.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence

try:  # pragma: no cover - dependencia opcional en entornos headless
    from PyQt6.QtGui import QFontDatabase, QGuiApplication

    QT_AVAILABLE = True
except ImportError:  # pragma: no cover
    QFontDatabase = None
    QGuiApplication = None
    QT_AVAILABLE = False


_GF = "https://raw.githubusercontent.com/google/fonts/main"
_CDN = "https://cdn.jsdelivr.net/gh/google/fonts@main"
_USER_AGENT = "PackageMaker/3.2.7 (+https://github.com/JesusQuijada34/packagemaker)"


@dataclass(frozen=True)
class FontSpec:
    """Fuente descargable con sus espejos y su huella de integridad."""

    key: str
    family: str
    filename: str
    sha256: str
    size: int
    license: str
    license_url: str
    paths: Sequence[str] = field(default_factory=tuple)
    kind: str = "ui"

    def urls(self) -> List[str]:
        """URLs candidatas, en orden de preferencia."""
        urls: List[str] = []
        for path in self.paths:
            urls.append(f"{_GF}/{path}")
        for path in self.paths:
            urls.append(f"{_CDN}/{path}")
        return urls


# Variantes variables (un solo archivo cubre todos los pesos).
FONT_REGISTRY: Dict[str, FontSpec] = {
    "roboto": FontSpec(
        key="roboto",
        family="Roboto",
        filename="Roboto[wdth,wght].ttf",
        sha256="d7598e12c5dbef095ff8272cfc55da0250bd07fbdecbac8a530b9b277872a134",
        size=488584,
        license="Apache-2.0",
        license_url="https://github.com/google/fonts/blob/main/ofl/roboto/LICENSE.txt",
        paths=("ofl/roboto/Roboto%5Bwdth,wght%5D.ttf",),
        kind="ui",
    ),
    "inter": FontSpec(
        key="inter",
        family="Inter",
        filename="Inter[opsz,wght].ttf",
        sha256="29160a80ff49ddcab2c97711247e08b1fab27a484a329ce8b813d820dc559031",
        size=876576,
        license="OFL-1.1",
        license_url="https://github.com/google/fonts/blob/main/ofl/inter/OFL.txt",
        paths=("ofl/inter/Inter%5Bopsz,wght%5D.ttf",),
        kind="ui",
    ),
    "notosans": FontSpec(
        key="notosans",
        family="Noto Sans",
        filename="NotoSans[wdth,wght].ttf",
        sha256="bfb7bb691513f12e734dc346c03a03f784912432d7e3fa8e56efcf906fe86b3d",
        size=2049096,
        license="OFL-1.1",
        license_url="https://github.com/google/fonts/blob/main/ofl/notosans/OFL.txt",
        paths=("ofl/notosans/NotoSans%5Bwdth,wght%5D.ttf",),
        kind="ui",
    ),
    "opensans": FontSpec(
        key="opensans",
        family="Open Sans",
        filename="OpenSans[wdth,wght].ttf",
        sha256="36643644f318a812aab2d2ed3bb98f8cf0872527f835fe9398d95fe6b9adb878",
        size=532636,
        license="OFL-1.1",
        license_url="https://github.com/google/fonts/blob/main/ofl/opensans/OFL.txt",
        paths=("ofl/opensans/OpenSans%5Bwdth,wght%5D.ttf",),
        kind="ui",
    ),
    "jetbrainsmono": FontSpec(
        key="jetbrainsmono",
        family="JetBrains Mono",
        filename="JetBrainsMono[wght].ttf",
        sha256="48715a42ec242c21e9f02692891e147d022299a52e48d5e413e1a942193ffeda",
        size=187208,
        license="OFL-1.1",
        license_url="https://github.com/google/fonts/blob/main/ofl/jetbrainsmono/OFL.txt",
        paths=("ofl/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf",),
        kind="mono",
    ),
}

# Orden de preferencia de las familias de interfaz.
UI_PREFERENCE: Sequence[str] = ("roboto", "inter", "notosans", "opensans")
# Orden de preferencia de las familias monoespaciadas.
MONO_PREFERENCE: Sequence[str] = ("jetbrainsmono",)

# Familias registradas desde disco en esta sesión (key -> familia Qt).
_loaded: Dict[str, str] = {}
# Rutas de archivos ya registrados, para no repetir addApplicationFont.
_registered_paths: set = set()


def font_cache_dir() -> Path:
    """Directorio de caché de fuentes (``data/fonts``)."""
    if getattr(sys, "frozen", False):
        root = Path(sys.executable).resolve().parent
    else:
        root = Path(__file__).resolve().parent.parent
    directory = root / "data" / "fonts"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def spec_for(key: str) -> FontSpec:
    try:
        return FONT_REGISTRY[key]
    except KeyError as exc:
        raise KeyError(f"Fuente desconocida: {key!r}") from exc


def cached_path(key: str) -> Path:
    return font_cache_dir() / spec_for(key).filename


def verify_file(path: Path, expected_sha256: str) -> bool:
    """Comprueba la huella SHA-256 de un archivo."""
    if not path.is_file():
        return False
    digest = hashlib.sha256()
    try:
        with open(path, "rb") as handle:
            for chunk in iter(lambda: handle.read(1 << 20), b""):
                digest.update(chunk)
    except OSError:
        return False
    return digest.hexdigest().lower() == expected_sha256.lower()


def is_cached(key: str) -> bool:
    """True si la fuente está en caché y su integridad es correcta."""
    spec = spec_for(key)
    return verify_file(cached_path(key), spec.sha256)


def cached_keys() -> List[str]:
    return [key for key in FONT_REGISTRY if is_cached(key)]


def _fetch(url: str, timeout: float) -> Optional[bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return None


def download_font(
    key: str,
    *,
    timeout: float = 30.0,
    force: bool = False,
    log_callback=None,
) -> Optional[Path]:
    """Descarga una fuente a la caché verificando su SHA-256.

    Devuelve la ruta local o ``None`` si ningún espejo sirvió un archivo
    íntegro. La escritura es atómica: se descarga a un temporal y se renombra
    sólo tras validar la huella.
    """
    spec = spec_for(key)

    def log(message: str) -> None:
        if log_callback:
            log_callback(message)

    destination = cached_path(key)
    if not force and is_cached(key):
        log(f"[FONT] {spec.family}: ya en caché ({destination.name})")
        return destination

    for url in spec.urls():
        payload = _fetch(url, timeout)
        if not payload:
            log(f"[FONT] {spec.family}: fallo al descargar desde {url}")
            continue
        digest = hashlib.sha256(payload).hexdigest()
        if digest.lower() != spec.sha256.lower():
            log(f"[FONT] {spec.family}: huella inválida desde {url}, se descarta")
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        handle, tmp_name = tempfile.mkstemp(
            dir=str(destination.parent), prefix=f".{spec.key}.", suffix=".part"
        )
        try:
            with os.fdopen(handle, "wb") as tmp_file:
                tmp_file.write(payload)
            shutil.move(tmp_name, destination)
        except OSError as exc:
            log(f"[FONT] {spec.family}: no se pudo guardar ({exc})")
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
            continue
        log(f"[FONT] {spec.family}: descargada y verificada ({len(payload)} bytes)")
        return destination

    log(f"[FONT] {spec.family}: no disponible (sin red o espejos caídos)")
    return None


def ensure_fonts(
    keys: Optional[Sequence[str]] = None,
    *,
    download: bool = True,
    timeout: float = 30.0,
    force: bool = False,
    log_callback=None,
) -> Dict[str, Optional[Path]]:
    """Garantiza que las fuentes indicadas estén en caché.

    Con ``download=False`` sólo se consideran las copias ya presentes, lo que
    permite arranques totalmente offline.
    """
    selected = list(keys) if keys else list(UI_PREFERENCE) + list(MONO_PREFERENCE)
    result: Dict[str, Optional[Path]] = {}
    for key in selected:
        spec_for(key)  # valida que la clave exista
        if is_cached(key):
            result[key] = cached_path(key)
            continue
        if not download:
            result[key] = None
            continue
        result[key] = download_font(
            key, timeout=timeout, force=force, log_callback=log_callback
        )
    return result


def register_font_file(path: Path) -> Optional[str]:
    """Registra un archivo de fuente en Qt. Devuelve la familia o ``None``.

    Requiere una ``QGuiApplication`` viva: ``addApplicationFont`` no funciona
    sin ella.
    """
    if not QT_AVAILABLE or QGuiApplication.instance() is None:
        return None
    resolved = str(Path(path).resolve())
    if resolved in _registered_paths:
        return _loaded.get(Path(path).stem)
    font_id = QFontDatabase.addApplicationFont(resolved)
    if font_id == -1:
        return None
    families = QFontDatabase.applicationFontFamilies(font_id)
    if not families:
        return None
    _registered_paths.add(resolved)
    return families[0]


def load_cached_fonts(log_callback=None) -> Dict[str, str]:
    """Registra en Qt todas las fuentes disponibles en caché.

    Debe invocarse **después** de crear ``QApplication``. Devuelve el mapa
    ``key -> familia Qt`` de las fuentes registradas.
    """
    for key, spec in FONT_REGISTRY.items():
        path = cached_path(key)
        if not verify_file(path, spec.sha256):
            continue
        family = register_font_file(path)
        if family:
            _loaded[key] = family
            if log_callback:
                log_callback(f"[FONT] Registrada {family} desde {path.name}")
    return dict(_loaded)


def loaded_families() -> Dict[str, str]:
    """Familias registradas desde disco en esta sesión."""
    return dict(_loaded)


def installed_system_families() -> set:
    """Familias conocidas por Qt (sistema + registradas)."""
    if not QT_AVAILABLE or QGuiApplication.instance() is None:
        return set()
    return {name.casefold() for name in QFontDatabase.families()}


def resolve_family(preference: Sequence[str], kind: str = "ui") -> Optional[str]:
    """Devuelve la mejor familia disponible para ``preference``.

    Prioriza las fuentes registradas desde la caché del proyecto sobre las del
    sistema, para que el aspecto sea idéntico en cualquier máquina.
    """
    for key in preference:
        family = _loaded.get(key)
        if family:
            return family
    installed = installed_system_families()
    if not installed:
        return None
    for key in preference:
        spec = FONT_REGISTRY.get(key)
        if spec and spec.family.casefold() in installed:
            return spec.family
    return None


def available_fonts_report() -> Dict[str, Dict[str, object]]:
    """Estado de cada fuente: caché, integridad y registro en Qt."""
    report: Dict[str, Dict[str, object]] = {}
    for key, spec in FONT_REGISTRY.items():
        path = cached_path(key)
        cached = verify_file(path, spec.sha256)
        report[key] = {
            "family": spec.family,
            "kind": spec.kind,
            "license": spec.license,
            "cached": cached,
            "path": str(path) if cached else None,
            "registered": _loaded.get(key),
            "expected_size": spec.size,
        }
    return report


def write_license_notice(directory: Optional[Path] = None) -> Path:
    """Escribe el aviso de licencias de las fuentes descargadas."""
    target_dir = directory or font_cache_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    notice = target_dir / "FONT-LICENSES.txt"
    lines = [
        "Fuentes descargadas por PackageMaker (Google Fonts)",
        "=" * 60,
        "",
    ]
    for spec in FONT_REGISTRY.values():
        lines.append(f"{spec.family} ({spec.filename})")
        lines.append(f"  Licencia: {spec.license}")
        lines.append(f"  Texto:    {spec.license_url}")
        lines.append("")
    notice.write_text("\n".join(lines), encoding="utf-8")
    return notice
