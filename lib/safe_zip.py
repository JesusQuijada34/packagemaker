"""Secure ZIP extraction helpers for PackageMaker archives and downloads."""

from __future__ import annotations

import stat
import zipfile
from pathlib import Path, PurePosixPath


class UnsafeZipMemberError(ValueError):
    """Raised when a ZIP member could escape the requested destination."""


def _safe_target(destination: Path, member_name: str) -> Path:
    """Resolve a ZIP member under *destination* or raise for unsafe names."""
    normalized = member_name.replace("\\", "/")
    if not normalized or normalized == ".":
        return destination

    if normalized.startswith("/") or (
        len(normalized) >= 2
        and normalized[0].isalpha()
        and normalized[1] == ":"
    ):
        raise UnsafeZipMemberError(f"Ruta absoluta no permitida en ZIP: {member_name!r}")

    parts = [part for part in PurePosixPath(normalized).parts if part not in ("", ".")]
    if any(part == ".." for part in parts):
        raise UnsafeZipMemberError(f"Path traversal detectado en ZIP: {member_name!r}")

    target = destination.joinpath(*parts)
    try:
        target.resolve().relative_to(destination)
    except ValueError as exc:
        raise UnsafeZipMemberError(
            f"La entrada ZIP escapa del destino: {member_name!r}"
        ) from exc
    return target


def _is_symlink(info: zipfile.ZipInfo) -> bool:
    """Return whether a ZIP member advertises a Unix symbolic-link mode."""
    mode = (info.external_attr >> 16) & 0o170000
    return stat.S_ISLNK(mode)


def safe_extract_zip(archive: zipfile.ZipFile, destination: Path | str) -> list[Path]:
    """Extract *archive* below *destination* after validating every member.

    The archive is fully validated before the first write. Backslash separators,
    absolute paths, ``..`` components, symlink members, and pre-existing symlink
    targets are rejected to prevent writes outside the destination.
    """
    destination_path = Path(destination)
    destination_path.mkdir(parents=True, exist_ok=True)
    destination_path = destination_path.resolve()

    planned: list[tuple[zipfile.ZipInfo, Path]] = []
    for info in archive.infolist():
        if _is_symlink(info):
            raise UnsafeZipMemberError(f"Symlink no permitido en ZIP: {info.filename!r}")
        target = _safe_target(destination_path, info.filename)
        if target != destination_path and target.exists() and target.is_symlink():
            raise UnsafeZipMemberError(
                f"El destino ya contiene un symlink: {info.filename!r}"
            )
        planned.append((info, target))

    extracted: list[Path] = []
    for info, target in planned:
        if info.is_dir() or info.filename.endswith(("/", "\\")):
            target.mkdir(parents=True, exist_ok=True)
            extracted.append(target)
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.is_symlink():
            raise UnsafeZipMemberError(
                f"El destino ya contiene un symlink: {info.filename!r}"
            )
        with archive.open(info, "r") as source, target.open("wb") as output:
            output.write(source.read())
        extracted.append(target)

    return extracted
