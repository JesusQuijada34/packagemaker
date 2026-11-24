# -*- coding: utf-8 -*-
"""Proyectos con fuentes que no están en UTF-8 (declaración PEP 263).

Regresiones de R-3f8a7c21, R-9d2b6e45 y R-6c4a1f83: el motor leía los guiones
del proyecto con ``encoding="utf-8"`` fijo. Un proyecto guardado por un editor
de Windows en ANSI (``cp1252``), con su ``# -*- coding: cp1252 -*-`` como exige
Python, lanzaba ``UnicodeDecodeError`` desde un slot de Qt (PyQt6 aborta el
proceso) o desde el CLI (traceback).

Las pruebas ejercitan el código real: lectura de fuentes, inyección del
bootloader, preflight, ofuscación y compilación con ``zipapp``.
"""

import ast
import json
from pathlib import Path

import pytest

from lib.blindcubeEngine import bootloader_injection, build_preflight, hardening
from lib.blindcubeEngine.source_io import SourceEncodingError, read_python_source
from lib.dependency_manager import DependencyChecker
from lib.iflapp_ide import (
    compile_project,
    debug_script,
    detect_hidden_imports,
    scan_project,
    trace_script,
)

CP1252_SOURCE = (
    "# -*- coding: cp1252 -*-\n"
    "# Año nuevo\n"
    "import os\n"
    "import json\n"
    "print('hola')\n"
)

PYQT_CP1252_SOURCE = '''# -*- coding: cp1252 -*-
# Año nuevo
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


def _write_cp1252(path: Path, text: str) -> Path:
    path.write_bytes(text.encode("cp1252"))
    return path


def _project(root: Path, script: str = CP1252_SOURCE, settings=None) -> Path:
    (root / "config").mkdir(parents=True, exist_ok=True)
    (root / "details.xml").write_text(
        "<project><publisher>Influent</publisher><app>Demo</app><name>Demo</name>"
        "<version>v1.0</version><platform>AlphaCube</platform>"
        "<author>JesusQuijada34</author></project>",
        encoding="utf-8",
    )
    (root / "config" / "settings.json").write_text(
        json.dumps(settings or {"build": {"scripts": ["app.py"]}}), encoding="utf-8"
    )
    _write_cp1252(root / "app.py", script)
    return root


class TestReadPythonSource:
    def test_honours_declared_encoding(self, tmp_path):
        path = _write_cp1252(tmp_path / "app.py", CP1252_SOURCE)
        text, encoding = read_python_source(path)
        assert encoding == "cp1252"
        assert "Año nuevo" in text

    def test_rejects_undecodable_source_with_a_readable_error(self, tmp_path):
        path = tmp_path / "legacy.py"
        path.write_bytes("# año\nimport os\n".encode("latin-1"))
        with pytest.raises(SourceEncodingError):
            read_python_source(path)


class TestIdeAnalysis:
    def test_hidden_imports_read_pep263_source(self, tmp_path):
        path = _write_cp1252(tmp_path / "app.py", CP1252_SOURCE)
        assert detect_hidden_imports(path) == ["json", "os"]

    def test_hidden_imports_ignore_undecodable_source(self, tmp_path):
        path = tmp_path / "legacy.py"
        path.write_bytes("# año\nimport os\n".encode("latin-1"))
        assert detect_hidden_imports(path) == []

    def test_scan_project_tolerates_non_utf8_settings(self, tmp_path):
        root = _project(tmp_path / "proyecto")
        (root / "config" / "settings.json").write_bytes(
            '{"build": {"scripts": ["app.py"]}, "nota": "año"}'.encode("cp1252")
        )
        project = scan_project(root)
        assert project.scripts == ["app.py"]

    def test_scan_project_accepts_settings_with_bom(self, tmp_path):
        root = _project(tmp_path / "proyecto")
        (root / "config" / "settings.json").write_bytes(
            b"\xef\xbb\xbf" + json.dumps({"build": {"scripts": ["app.py"]}}).encode("utf-8")
        )
        assert scan_project(root).scripts == ["app.py"]

    def test_compile_project_handles_pep263_source(self, tmp_path):
        root = _project(tmp_path / "proyecto")
        outcome = compile_project(root, backend="zipapp", output_dir=root / "dist")
        assert outcome.ok, outcome.failures
        assert Path(outcome.outputs[0]).is_file()


class TestBootloaderInjection:
    def test_injection_preserves_declared_encoding(self, tmp_path):
        root = tmp_path / "proyecto"
        root.mkdir()
        source = _write_cp1252(root / "app.py", PYQT_CP1252_SOURCE)

        injected = bootloader_injection.prepare_for_build(source, root)

        assert injected is not None
        text = injected.read_bytes().decode("cp1252")
        assert "_pm_splash" in text
        assert "Año nuevo" in text
        ast.parse(text)

    def test_injection_skips_undecodable_source(self, tmp_path):
        root = tmp_path / "proyecto"
        root.mkdir()
        source = root / "legacy.py"
        source.write_bytes("# año\nimport os\n".encode("latin-1"))
        assert bootloader_injection.prepare_for_build(source, root) is None

    def test_inject_file_reports_false_for_undecodable_source(self, tmp_path):
        source = tmp_path / "legacy.py"
        source.write_bytes("# año\nimport os\n".encode("latin-1"))
        assert bootloader_injection.inject_file(source) is False


class TestPreflight:
    def test_preflight_accepts_pep263_source(self, tmp_path):
        path = _write_cp1252(tmp_path / "app.py", CP1252_SOURCE)
        result = build_preflight.check_syntax([path])
        assert result.ok, result.detail

    def test_preflight_reports_undecodable_source(self, tmp_path):
        path = tmp_path / "legacy.py"
        path.write_bytes("# año\nimport os\n".encode("latin-1"))
        result = build_preflight.check_syntax([path])
        assert not result.ok
        assert "legacy.py" in result.detail


class TestIdePanelSlots:
    def test_panel_compiles_and_reads_hidden_imports_without_aborting(self, tmp_path):
        pytest.importorskip("PyQt6.QtWidgets")
        from lib.iflapp_ide_dialog import IflappIdePanel

        root = _project(tmp_path / "proyecto")
        panel = IflappIdePanel()
        try:
            assert panel.load_project(str(root))
            panel.backend_selector.setCurrentText("zipapp")
            assert panel.run_compile() is True
            assert panel.hidden_imports() == ["json", "os"]
        finally:
            panel.deleteLater()

    def test_panel_reports_undecodable_script(self, tmp_path):
        pytest.importorskip("PyQt6.QtWidgets")
        from lib.iflapp_ide_dialog import IflappIdePanel

        root = _project(tmp_path / "proyecto")
        (root / "app.py").write_bytes("# año\nimport os\n".encode("latin-1"))
        panel = IflappIdePanel()
        try:
            assert panel.load_project(str(root))
            assert panel.editor.toPlainText() == ""
            assert panel.status.text()
            assert panel.hidden_imports() == []
        finally:
            panel.deleteLater()


class TestDebuggerEncoding:
    def test_trace_script_reads_pep263_source(self, tmp_path):
        path = _write_cp1252(
            tmp_path / "app.py",
            "# -*- coding: cp1252 -*-\n# Año\nvalor = 41 + 1\n",
        )
        stops = trace_script(path, max_stops=20)
        assert stops
        assert any(stop.line == 3 for stop in stops)

    def test_debug_script_accepts_pep263_source(self, tmp_path):
        path = _write_cp1252(
            tmp_path / "app.py",
            "# -*- coding: cp1252 -*-\n# Año\nvalor = 7\n",
        )
        outcome = debug_script(path, max_stops=20)
        assert outcome.error is None
        assert outcome.stops

    def test_trace_script_reports_undecodable_source(self, tmp_path):
        path = tmp_path / "legacy.py"
        path.write_bytes("# año\nimport os\n".encode("latin-1"))
        outcome = debug_script(path)
        assert outcome.error is not None
        assert "legacy.py" in outcome.error


class TestDependencyScanEncoding:
    def test_dependency_checker_reads_pep263_source(self, tmp_path):
        script = _write_cp1252(
            tmp_path / "app.py",
            "# -*- coding: cp1252 -*-\n# Año\nimport requests\n",
        )
        checker = DependencyChecker(str(script), project_dir=str(tmp_path))
        checker._detect_imports()
        assert checker.detected_imports == {"requests"}

    def test_dependency_checker_tolerates_undecodable_source(self, tmp_path):
        script = tmp_path / "legacy.py"
        script.write_bytes("# año\nimport requests\n".encode("latin-1"))
        checker = DependencyChecker(str(script), project_dir=str(tmp_path))
        checker._detect_imports()
        assert "requests" in checker.detected_imports

    def test_requirements_txt_with_non_utf8_bytes_is_rewritten(self, tmp_path):
        script = _write_cp1252(
            tmp_path / "app.py",
            "# -*- coding: cp1252 -*-\nimport requests\n",
        )
        (tmp_path / "requirements.txt").write_bytes(b"# a\xf1os\n")
        checker = DependencyChecker(str(script), project_dir=str(tmp_path))
        checker.detected_imports = {"requests"}
        checker._write_requirements_txt()
        assert "requests" in (tmp_path / "requirements.txt").read_text(encoding="utf-8")


class TestHardeningEncoding:
    def test_obfuscate_preserves_declared_encoding(self, tmp_path):
        path = _write_cp1252(
            tmp_path / "app.py",
            "# -*- coding: cp1252 -*-\n# Año\nMENSAJE = 'texto de año'\n",
        )
        report = hardening.obfuscate_strings(path)

        assert report.applied, report.detail
        text = path.read_bytes().decode("cp1252")
        assert "b64decode(" in text
        assert "Año" in text
        ast.parse(text)

    def test_anti_debug_preserves_declared_encoding(self, tmp_path):
        path = _write_cp1252(tmp_path / "app.py", "# -*- coding: cp1252 -*-\n# Año\nprint(1)\n")
        report = hardening.inject_anti_debug(path)

        assert report.applied, report.detail
        text = path.read_bytes().decode("cp1252")
        assert "Año" in text
        assert "_iflapp_guard()" in text

    def test_obfuscate_reports_undecodable_source(self, tmp_path):
        path = tmp_path / "legacy.py"
        path.write_bytes("# año\nMENSAJE = 'texto de año'\n".encode("latin-1"))
        report = hardening.obfuscate_strings(path)
        assert not report.applied
        assert "no analizable" in report.detail
