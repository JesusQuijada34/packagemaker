"""Fase 3 de bugs.md: librería de splash compartida e inyección bootloader.

Ejercita el código real de :mod:`lib.bootloader_injection` (AST) y de
:mod:`lib.splash_bootloader` (autocontenido), sin mocks.
"""

from __future__ import annotations

import ast
import os
import unittest
from pathlib import Path

from lib.blindcubeEngine import bootloader_injection, splash_bootloader

_UNREADABLE_SKIP = unittest.skipIf(
    os.name == "nt" or (hasattr(os, "geteuid") and os.geteuid() == 0),
    "los permisos POSIX no bloquean la lectura en Windows ni como root",
)

_SAMPLE = '''"""Demo app."""
from __future__ import annotations
import sys
from PyQt6 import QtWidgets


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QWidget()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
'''


def test_inject_keeps_source_valid_and_idempotent():
    injected, changed = bootloader_injection.inject_source(_SAMPLE)
    assert changed
    ast.parse(injected)  # no debe romper la sintaxis
    again, changed_again = bootloader_injection.inject_source(injected)
    assert again == injected
    assert changed_again is False


def test_inject_places_header_after_imports():
    injected, _ = bootloader_injection.inject_source(_SAMPLE)
    lines = injected.splitlines()
    last_import = max(i for i, l in enumerate(lines) if l.startswith(("import ", "from ")))
    header = next(i for i, l in enumerate(lines) if "bootloader de splash" in l)
    assert header == last_import + 1


def test_inject_respects_function_indentation():
    injected, _ = bootloader_injection.inject_source(_SAMPLE)
    inside_main = [l for l in injected.splitlines() if "_pm_splash.start()" in l]
    assert inside_main, "debía inyectarse el arranque del splash"
    assert inside_main[0].startswith("        ")


def test_inject_finish_before_event_loop():
    injected, _ = bootloader_injection.inject_source(_SAMPLE)
    assert injected.index("_pm_splash.finish()") < injected.index("app.exec()")


def test_inject_skips_non_framework_script():
    plain = "import os\nprint(os.getcwd())\n"
    out, changed = bootloader_injection.inject_source(plain)
    # La inyección de texto siempre añade el header; lo que no debe es fallar.
    assert changed
    ast.parse(out)
    assert bootloader_injection.script_uses_framework(plain) is False


def test_script_uses_framework_detects_pyqt6_and_leviathan():
    assert bootloader_injection.script_uses_framework("from PyQt6 import QtWidgets\n")
    assert bootloader_injection.script_uses_framework("import leviathan_ui\n")
    assert not bootloader_injection.script_uses_framework("import json\n")


def test_write_injected_copy_creates_sidecar(tmp_path: Path):
    script = tmp_path / "demo.py"
    script.write_text(_SAMPLE, encoding="utf-8")
    copy = bootloader_injection.write_injected_copy(script)
    assert copy is not None and copy.name == "demo_pmboot.py"
    assert "bootloader de splash" in copy.read_text(encoding="utf-8")
    # El original queda intacto.
    assert script.read_text(encoding="utf-8") == _SAMPLE
    bootloader_injection.cleanup_injected_copy(script)
    assert not copy.exists()


def test_write_injected_copy_returns_none_for_plain_script(tmp_path: Path):
    script = tmp_path / "plain.py"
    script.write_text("import json\n", encoding="utf-8")
    assert bootloader_injection.write_injected_copy(script) is None


def test_prepare_for_build_copies_splash_library(tmp_path: Path):
    script = tmp_path / "app.py"
    script.write_text(_SAMPLE, encoding="utf-8")
    injected = bootloader_injection.prepare_for_build(script, tmp_path)
    assert injected is not None
    assert (tmp_path / "lib" / "splash_bootloader.py").is_file()
    assert (tmp_path / "lib" / "__init__.py").is_file()


def test_splash_module_is_self_contained():
    """La librería copiada no puede depender de módulos de PackageMaker."""
    source = (Path(splash_bootloader.__file__)).read_text(encoding="utf-8")
    tree = ast.parse(source)
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            modules.add(node.module.split(".")[0])
    forbidden = modules - {"os", "sys", "pathlib", "PyQt6", "subprocess", "winreg", "collections", "typing", "__future__"}
    assert not forbidden, f"imports no permitidos: {forbidden}"


def test_system_accent_color_returns_hex():
    color = splash_bootloader.system_accent_color()
    assert color.startswith("#") and len(color) == 7


def test_bootloader_arm_resolves_context(tmp_path: Path):
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "app-icon.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    loader = splash_bootloader.SplashBootloader().arm(str(tmp_path / "main.py"))
    assert loader._icon_path is not None
    assert loader._accent.startswith("#")


def test_bootloader_start_without_qt_returns_bool(tmp_path: Path):
    loader = splash_bootloader.SplashBootloader().arm(str(tmp_path / "main.py"))
    assert loader.start() in (True, False)
    loader.finish()  # nunca debe lanzar


@_UNREADABLE_SKIP
def test_bootloader_arm_tolerates_unreadable_project(tmp_path: Path, monkeypatch):
    """Un proyecto o cwd sin permisos no impide armar el splash."""
    monkeypatch.chdir(tmp_path)
    locked = tmp_path / "locked"
    (locked / "app").mkdir(parents=True)
    script = locked / "main.py"
    script.write_text("print('hola')\n", encoding="utf-8")
    locked.chmod(0o000)
    try:
        loader = splash_bootloader.SplashBootloader().arm(str(script))
    finally:
        locked.chmod(0o755)
    assert loader._icon_path is None
    assert loader._accent.startswith("#")
