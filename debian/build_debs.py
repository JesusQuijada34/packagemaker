#!/usr/bin/env python3
"""Build reproducible Debian packages for Influent Package Maker.

The application is Python/Qt source, so the package payload is architecture-neutral;
Debian's architecture field is used to publish dependency-resolved variants for each
requested target architecture. Native binary compilation must still happen on a
machine of the target architecture.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARCHES = ("amd64", "arm64", "armhf", "i386")
EXCLUDED_DIRS = {".git", ".github", ".vscode", "__pycache__", ".pytest_cache", "build", "dist", "debian-build", "packagemaker-build-output"}
EXCLUDED_FILES = {"data/pm.data"}
COPY_DIRS = ("app", "assets", "config", "docs", "lang", "lib", "shell", "source", "scripts")
COPY_FILES = ("packagemaker.py", "pmCodeEditor.py", "updater.py", "launcher.sh", "details.xml", "LICENSE", "README.md", "FAQ.md", "CHANGELOG.md", "RELEASE_NOTES.md")


def metadata() -> tuple[str, str, str, str]:
    root = ElementTree.parse(ROOT / "details.xml").getroot()
    publisher = (root.findtext("publisher") or "influent").strip().lower()
    app = (root.findtext("app") or "packagemaker").strip().lower()
    full_version = (root.findtext("version") or "v0.0.0").strip()
    version = full_version.lstrip("v")
    platform = (root.findtext("platform") or "Danenone").strip()
    if platform not in {"Danenone", "Knosthalij", "AlphaCube"}:
        raise ValueError(f"unsupported platform: {platform}")
    return publisher, app, version, platform


def copy_payload(stage: Path, publisher: str, app: str) -> None:
    opt = stage / "opt" / f"{publisher}-{app}"
    opt.mkdir(parents=True)
    ignore = shutil.ignore_patterns(*EXCLUDED_DIRS)
    for name in COPY_DIRS:
        source = ROOT / name
        if source.exists():
            shutil.copytree(source, opt / name, ignore=ignore)
    for name in COPY_FILES:
        source = ROOT / name
        if source.exists() and str(source.relative_to(ROOT)) not in EXCLUDED_FILES:
            destination = opt / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    for path in opt.rglob("*"):
        if path.is_file() and path.suffix in {".sh", ".py"}:
            path.chmod(path.stat().st_mode | 0o111 if path.name in {"packagemaker.py", "launcher.sh"} else path.stat().st_mode)

    bin_dir = stage / "usr" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    launcher = bin_dir / "packagemaker"
    launcher.write_text(
        "#!/bin/sh\n"
        f'exec /usr/bin/python3 /opt/{publisher}-{app}/packagemaker.py "$@"\n',
        encoding="utf-8",
    )
    launcher.chmod(0o755)

    desktop_dir = stage / "usr" / "share" / "applications"
    desktop_dir.mkdir(parents=True, exist_ok=True)
    (desktop_dir / "influent-packagemaker.desktop").write_text(
        "[Desktop Entry]\n"
        "Type=Application\n"
        "Name=Influent Package Maker\n"
        "Comment=Create and manage Influent applications\n"
        "Exec=/usr/bin/packagemaker\n"
        f"Icon=/opt/{publisher}-{app}/app/packagemaker.png\n"
        "Terminal=false\n"
        "Categories=Development;Utility;\n",
        encoding="utf-8",
    )


def build_one(architecture: str, output_dir: Path, publisher: str, app: str, version: str, platform: str) -> Path:
    artifact_stem = f"{publisher}.{app}.v{version}-{platform}"
    package_name = f"{artifact_stem}_{architecture}"
    with tempfile.TemporaryDirectory(prefix="packagemaker-deb-") as temp:
        stage = Path(temp) / package_name
        (stage / "DEBIAN").mkdir(parents=True)
        copy_payload(stage, publisher, app)
        control = (
            f"Package: {publisher}-{app}\n"
            f"Version: {version}\n"
            f"Section: devel\nPriority: optional\nArchitecture: {architecture}\n"
            "Maintainer: JesusQuijada34\n"
            "Depends: python3 (>= 3.10), python3-pyqt6, python3-requests, python3-packaging, python3-pil\n"
            "Description: Influent Package Maker\n"
            " Python/Qt application for creating and managing Influent projects.\n"
        )
        (stage / "DEBIAN" / "control").write_text(control, encoding="utf-8")
        output_dir.mkdir(parents=True, exist_ok=True)
        output = output_dir / f"{package_name}.deb"
        subprocess.run(["dpkg-deb", "--build", "--root-owner-group", str(stage), str(output)], check=True)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arch", action="append", dest="architectures", help="Target architecture; repeatable")
    parser.add_argument("--output", type=Path, default=ROOT / "debian-build")
    args = parser.parse_args()
    architectures = tuple(args.architectures or DEFAULT_ARCHES)
    allowed = set(DEFAULT_ARCHES)
    invalid = set(architectures) - allowed
    if invalid:
        parser.error(f"unsupported architecture(s): {', '.join(sorted(invalid))}")
    publisher, app, version, platform = metadata()
    for architecture in architectures:
        result = build_one(architecture, args.output, publisher, app, version, platform)
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
