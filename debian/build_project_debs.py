#!/usr/bin/env python3
"""Build source-oriented Debian packages for audited projects."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

DEFAULT_ARCHES = ("amd64", "arm64", "armhf", "i386")
EXCLUDE_DIRS = {".git", "__pycache__", "dist", "build", ".pytest_cache", ".mypy_cache", "node_modules"}
EXCLUDE_FILES = {".env", ".env.local", ".env.production"}


def metadata(project: Path) -> tuple[str, str, str, str, str, str]:
    root = ET.parse(project / "details.xml").getroot()
    publisher = (root.findtext("publisher") or "influent").strip().lower()
    app = (root.findtext("app") or project.name).strip()
    full_version = (root.findtext("version") or "v1.0-26.08-00.00").strip()
    author = (root.findtext("author") or "JesusQuijada34").strip()
    platform = (root.findtext("platform") or "Danenone").strip()
    deb_version = full_version.lstrip("v").replace("-", "+", 1).replace("-", ".")
    return publisher, app, full_version, author, platform, deb_version


def copy_project(project: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for source in project.iterdir():
        if source.name in EXCLUDE_DIRS or source.name in EXCLUDE_FILES:
            continue
        target = destination / source.name
        if source.is_dir():
            shutil.copytree(source, target, ignore=shutil.ignore_patterns(*EXCLUDE_DIRS, *EXCLUDE_FILES))
        else:
            shutil.copy2(source, target)


def build_one(project: Path, output: Path, architecture: str) -> Path:
    publisher, app, full_version, author, platform, deb_version = metadata(project)
    stem = f"{publisher}-{app.lower()}"
    identity = f"{publisher}.{app}.{full_version}"
    filename = f"{identity}_{architecture}.deb"
    with tempfile.TemporaryDirectory(prefix="audited-deb-") as temporary:
        stage = Path(temporary) / stem
        payload = stage / "opt" / stem
        copy_project(project, payload)
        bin_dir = stage / "usr" / "bin"
        bin_dir.mkdir(parents=True)
        launcher = bin_dir / app
        launcher.write_text(
            "#!/bin/sh\n"
            f"exec /usr/bin/env sh /opt/{stem}/autorun \"$@\"\n",
            encoding="utf-8",
        )
        launcher.chmod(0o755)
        control_dir = stage / "DEBIAN"
        control_dir.mkdir()
        control = (
            f"Package: {stem}\nVersion: {deb_version}\nArchitecture: {architecture}\n"
            f"Section: misc\nPriority: optional\nMaintainer: {author}\n"
            f"Description: Audited {app} source package ({platform})\n"
            " MoonFix-normalized source bundle. Runtime dependencies remain project-specific.\n"
        )
        (control_dir / "control").write_text(control, encoding="utf-8")
        output.mkdir(parents=True, exist_ok=True)
        target = output / filename
        subprocess.run(["dpkg-deb", "--build", "--root-owner-group", str(stage), str(target)], check=True)
        return target


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--arch", action="append", choices=DEFAULT_ARCHES)
    args = parser.parse_args()
    arches = args.arch or list(DEFAULT_ARCHES)
    for architecture in arches:
        print(build_one(args.project.resolve(), args.output.resolve(), architecture))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
