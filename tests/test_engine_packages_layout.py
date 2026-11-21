# -*- coding: utf-8 -*-
"""Estructura de ``lib/`` por motores y puente de leviathan-ui (Fase 2.1)."""

import importlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

BLINDCUBE = [
    "BuildThread",
    "asksome_format",
    "asksome_installer",
    "bootloader_injection",
    "build_preflight",
    "build_validation",
    "compilers",
    "dropper",
    "hardening",
    "hardware_sandbox",
    "iflapp_format",
    "iflapp_reader",
    "nuitka_embedded",
    "splash_bootloader",
]
FLATCUBE = ["pyinstaller_embedded", "pyinstaller_hooks"]
MAKESELF = ["template_engine"]


@pytest.mark.parametrize("name", BLINDCUBE)
def test_blindcube_modules_live_in_engine_package(name):
    assert (ROOT / "lib" / "blindcubeEngine" / f"{name}.py").is_file()
    assert not (ROOT / "lib" / f"{name}.py").exists()


@pytest.mark.parametrize("name", FLATCUBE)
def test_flatcube_modules_live_in_engine_package(name):
    assert (ROOT / "lib" / "flatcubeEngine" / f"{name}.py").is_file()
    assert not (ROOT / "lib" / f"{name}.py").exists()


@pytest.mark.parametrize("name", MAKESELF)
def test_makeself_modules_live_in_engine_package(name):
    assert (ROOT / "lib" / "makeselfEngine" / f"{name}.py").is_file()
    assert not (ROOT / "lib" / f"{name}.py").exists()


@pytest.mark.parametrize("name", BLINDCUBE + FLATCUBE + MAKESELF)
def test_moved_modules_are_importable(name):
    package = "blindcubeEngine" if name in BLINDCUBE else (
        "flatcubeEngine" if name in FLATCUBE else "makeselfEngine"
    )
    assert importlib.import_module(f"lib.{package}.{name}") is not None


def test_no_source_imports_the_old_flat_paths():
    stale = []
    for path in (ROOT / "lib").rglob("*.py"):
        if "__pycache__" in path.parts or path.parts[-2] in {"blindcubeEngine", "flatcubeEngine", "makeselfEngine"}:
            continue
        text = path.read_text(encoding="utf-8")
        for name in BLINDCUBE + FLATCUBE + MAKESELF:
            if f"from lib.{name} import" in text or f"from lib import {name}" in text:
                stale.append(f"{path.relative_to(ROOT)} -> {name}")
    assert stale == []


def test_leviathan_ui_is_vendored():
    vendor = ROOT / "lib" / "leviathan_ui"
    assert (vendor / "__init__.py").is_file()
    assert (vendor / "LICENSE").is_file()


def test_bridge_prefers_the_vendored_copy():
    from lib import leviathan_bridge

    module = leviathan_bridge.framework()
    assert module is not None
    assert module.__name__ == leviathan_bridge.VENDORED
    assert leviathan_bridge.is_available()


def test_bridge_exposes_the_framework_surface():
    from lib import leviathan_bridge

    for name in ("WipeWindow", "CustomTitleBar", "InmersiveSplash", "LeviathanProgressBar", "LightsOff"):
        assert leviathan_bridge.attribute(name) is not None
    assert leviathan_bridge.submodule("touchscreen").TouchScreen is not None


def test_bridge_reports_missing_framework(monkeypatch):
    from lib import leviathan_bridge

    monkeypatch.setattr(leviathan_bridge, "VENDORED", "lib.no_existe_leviathan")
    monkeypatch.setattr(leviathan_bridge, "INSTALLED", "no_existe_leviathan_tampoco")
    assert leviathan_bridge.framework() is None
    assert not leviathan_bridge.is_available()
    with pytest.raises(ImportError):
        leviathan_bridge.attribute("WipeWindow")


def test_no_module_imports_leviathan_directly():
    offenders = []
    for path in list((ROOT / "lib").rglob("*.py")) + [ROOT / "packagemaker.py", ROOT / "updater.py"]:
        if "__pycache__" in path.parts or path.parts[-2] == "leviathan_ui":
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith(("from leviathan_ui", "import leviathan_ui")):
                offenders.append(f"{path.relative_to(ROOT)}: {stripped}")
    assert offenders == []


def test_vendored_framework_lints_clean():
    import subprocess

    files = sorted(str(p) for p in (ROOT / "lib" / "leviathan_ui").glob("*.py"))
    result = subprocess.run(
        [sys.executable, "-m", "pyflakes", *files],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_vendored_framework_imports_without_the_pypi_package(monkeypatch):
    for name in [n for n in sys.modules if n == "leviathan_ui" or n.startswith("leviathan_ui.")]:
        monkeypatch.delitem(sys.modules, name, raising=False)
    for name in [n for n in sys.modules if n.startswith("lib.leviathan_ui")]:
        monkeypatch.delitem(sys.modules, name, raising=False)

    module = importlib.import_module("lib.leviathan_ui")
    assert hasattr(module, "WipeWindow")
