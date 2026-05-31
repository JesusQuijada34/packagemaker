"""
Gestor de dependencias automático para pmCodeEditor.
Detecta imports, genera requirements.txt, instala librerías faltantes.
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable, List, Optional, Set

try:
    from PyQt6.QtCore import QThread, pyqtSignal
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    class QThread: pass
    class pyqtSignal:
        def __init__(self, *args): pass
        def connect(self, func): pass
        def emit(self, *args): pass

IMPORT_TO_PIP = {
    "PIL": "Pillow",
    "cv2": "opencv-python",
    "sklearn": "scikit-learn",
    "yaml": "PyYAML",
    "dotenv": "python-dotenv",
    "bs4": "beautifulsoup4",
    "dateutil": "python-dateutil",
    "OpenSSL": "pyOpenSSL",
    "gi": "PyGObject",
}

STDLIB_MODULES = {
    "sys", "os", "re", "json", "csv", "time", "datetime", "math", "random",
    "collections", "itertools", "functools", "typing", "pathlib", "tempfile",
    "subprocess", "threading", "multiprocessing", "socket", "ssl", "hashlib",
    "base64", "codecs", "io", "struct", "xml", "html", "urllib", "http",
    "argparse", "logging", "unittest", "doctest", "pickle", "shelve", "sqlite3",
    "zlib", "gzip", "zipfile", "tarfile", "shutil", "glob", "fnmatch", "locale",
    "string", "pprint", "copy", "weakref", "abc", "enum", "dataclasses",
    "contextlib", "ast", "tokenize", "traceback", "warnings", "inspect",
    "importlib", "pkgutil", "platform", "errno", "stat", "queue", "heapq",
    "bisect", "array", "secrets", "uuid", "configparser", "getpass", "textwrap",
}

IDE_BUNDLED_MODULES = {
    "PyQt6", "PyQt5", "PyQt", "PySide6", "PySide2", "PySide",
    "leviathan_ui", "leviathan",
}


def is_ide_bundled_module(module_name: str, exclude_pyqt: bool = True) -> bool:
    if not exclude_pyqt:
        return module_name in {"leviathan_ui", "leviathan"}
    if module_name in IDE_BUNDLED_MODULES:
        return True
    if module_name.startswith("PyQt6") or module_name.startswith("PyQt5"):
        return True
    if module_name.startswith("PyQt") or module_name.startswith("PySide"):
        return True
    if module_name.startswith("leviathan_ui"):
        return True
    return False


def is_local_module(module_name: str, project_dirs: List[Path]) -> bool:
    for directory in project_dirs:
        if not directory.is_dir():
            continue
        if (directory / f"{module_name}.py").is_file():
            return True
        if (directory / module_name / "__init__.py").is_file():
            return True
    return False


def collect_project_search_dirs(script_path: Optional[str]) -> List[Path]:
    if not script_path:
        return []
    script = Path(script_path).resolve()
    dirs = [script.parent]
    root = script.parent
    for _ in range(4):
        dirs.append(root)
        for sub in ("app", "lib", "src"):
            candidate = root / sub
            if candidate.is_dir():
                dirs.append(candidate)
        if root.parent == root:
            break
        root = root.parent
    unique: List[Path] = []
    seen = set()
    for d in dirs:
        key = str(d)
        if key not in seen:
            seen.add(key)
            unique.append(d)
    return unique


def detect_imports_from_source(
    content: str,
    script_path: Optional[str] = None,
    exclude_pyqt: bool = True,
    exclude_local: bool = True,
) -> Set[str]:
    found: Set[str] = set()
    project_dirs = collect_project_search_dirs(script_path) if exclude_local else []

    patterns = [
        r"^\s*import\s+([\w.]+)",
        r"^\s*from\s+([\w.]+)\s+import",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, content, re.MULTILINE):
            module = match.group(1).split(".")[0]
            if not module or module in STDLIB_MODULES:
                continue
            if exclude_pyqt and is_ide_bundled_module(module, exclude_pyqt=True):
                continue
            if exclude_local and is_local_module(module, project_dirs):
                continue
            found.add(module)
    return found


def pip_package_name(import_name: str) -> str:
    return IMPORT_TO_PIP.get(import_name, import_name)


class DependencyChecker(QThread):
    progress = pyqtSignal(str, int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    package_installed = pyqtSignal(str, bool)

    def __init__(
        self,
        script_path: str,
        python_path: Optional[str] = None,
        project_dir: Optional[str] = None,
        exclude_pyqt: bool = True,
        exclude_local: bool = True,
    ):
        super().__init__()
        self.script_path = script_path
        self.python_path = python_path or sys.executable
        self.project_dir = Path(project_dir or Path(script_path).parent)
        self.exclude_pyqt = exclude_pyqt
        self.exclude_local = exclude_local
        self.detected_imports: Set[str] = set()
        self.missing_packages: Set[str] = set()
        self.installed_packages: Set[str] = set()

    def run(self):
        try:
            self.status.emit("Analizando imports del script...")
            self.progress.emit("Analizando código", 10)
            self._detect_imports()

            if not self.detected_imports:
                self.finished.emit(True, "No se detectaron dependencias externas")
                return

            self._write_requirements_txt()
            self.status.emit(f"Detectados {len(self.detected_imports)} imports")
            self.progress.emit("Verificando dependencias", 30)
            self._check_installed_packages()

            if not self.missing_packages:
                self.finished.emit(
                    True,
                    f"Todas las dependencias instaladas ({len(self.detected_imports)} paquetes)",
                )
                return

            self.status.emit(f"Instalando {len(self.missing_packages)} paquetes...")
            self.progress.emit("Instalando dependencias", 50)
            self._install_missing_packages()
            self.progress.emit("Completado", 100)
            self.finished.emit(
                True,
                f"Instalados {len(self.installed_packages)}/{len(self.missing_packages)} paquetes",
            )
        except Exception as e:
            self.finished.emit(False, str(e))

    def _detect_imports(self):
        with open(self.script_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.detected_imports = detect_imports_from_source(
            content,
            script_path=self.script_path,
            exclude_pyqt=self.exclude_pyqt,
            exclude_local=self.exclude_local,
        )

    def _write_requirements_txt(self):
        req_path = self.project_dir / "requirements.txt"
        lines = sorted(pip_package_name(m) for m in self.detected_imports)
        header = "# Generado automáticamente por pmCodeEditor\n"
        body = "\n".join(lines) + ("\n" if lines else "")
        existing = ""
        if req_path.exists():
            existing = req_path.read_text(encoding="utf-8")
        if body.strip() and body not in existing:
            req_path.write_text(header + body, encoding="utf-8")
            self.status.emit(f"Actualizado {req_path.name}")

    def _is_installed(self, import_name: str) -> bool:
        try:
            result = subprocess.run(
                [self.python_path, "-c", f"import {import_name}"],
                capture_output=True,
                timeout=30,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, OSError):
            return False

    def _check_installed_packages(self):
        for package in sorted(self.detected_imports):
            if self._is_installed(package):
                self.progress.emit(f"OK {package}", 35)
            else:
                self.missing_packages.add(package)
                self.status.emit(f"Falta: {package}")

    def _install_missing_packages(self):
        total = len(self.missing_packages)
        for i, package in enumerate(sorted(self.missing_packages)):
            pip_name = pip_package_name(package)
            self.status.emit(f"Instalando {pip_name} ({i + 1}/{total})...")
            self.package_installed.emit(package, False)
            try:
                result = subprocess.run(
                    [self.python_path, "-m", "pip", "install", pip_name],
                    capture_output=True,
                    text=True,
                    timeout=180,
                )
                if result.returncode == 0:
                    self.installed_packages.add(package)
                    self.package_installed.emit(package, True)
                    self.status.emit(f"{pip_name} instalado")
                else:
                    err = (result.stderr or result.stdout or "")[:200]
                    self.status.emit(f"Error {pip_name}: {err}")
            except subprocess.TimeoutExpired:
                self.status.emit(f"Timeout instalando {pip_name}")
            except OSError as e:
                self.status.emit(f"Error: {e}")
            progress = 50 + int((i + 1) * 50 / total)
            self.progress.emit(f"{i + 1}/{total}", progress)


class DependencyManager:
    def __init__(self, parent=None):
        self.parent = parent
        self.checker: Optional[DependencyChecker] = None
        self.exclude_pyqt = True
        self.exclude_local = True

    def check_and_install(
        self,
        script_path: str,
        python_path: Optional[str] = None,
        callback: Optional[Callable[[bool, str], None]] = None,
    ) -> DependencyChecker:
        project_dir = str(Path(script_path).parent)
        self.checker = DependencyChecker(
            script_path,
            python_path,
            project_dir,
            exclude_pyqt=self.exclude_pyqt,
            exclude_local=self.exclude_local,
        )
        self.checker.progress.connect(self._on_progress)
        self.checker.status.connect(self._on_status)
        self.checker.package_installed.connect(self._on_package_installed)
        self.checker.finished.connect(lambda ok, msg: self._on_finished(ok, msg, callback))
        self.checker.start()
        return self.checker

    def _on_progress(self, message: str, percent: int):
        if self.parent and hasattr(self.parent, "status_bar"):
            self.parent.status_bar.showMessage(f"📦 {message}")
        if self.parent and hasattr(self.parent, "progress_bar"):
            self.parent.progress_bar.setVisible(True)
            self.parent.progress_bar.setValue(percent)

    def _on_status(self, message: str):
        if self.parent and hasattr(self.parent, "console_panel"):
            self.parent.console_panel.append_output(f"[DEP] {message}")

    def _on_package_installed(self, package: str, success: bool):
        if self.parent and hasattr(self.parent, "console_panel"):
            mark = "OK" if success else "ERR"
            self.parent.console_panel.append_output(f"[DEP] [{mark}] {package}")

    def _on_finished(self, success: bool, message: str, callback: Optional[Callable]):
        if self.parent:
            if hasattr(self.parent, "deps_label"):
                self.parent.deps_label.setText(f"Deps: {'OK' if success else 'Error'}")
            if hasattr(self.parent, "progress_bar"):
                self.parent.progress_bar.setVisible(False)
            if hasattr(self.parent, "status_bar"):
                prefix = "✅" if success else "❌"
                self.parent.status_bar.showMessage(f"{prefix} {message}", 8000)
        if callback:
            callback(success, message)


_dependency_manager: Optional[DependencyManager] = None


def get_dependency_manager(parent=None) -> DependencyManager:
    global _dependency_manager
    if _dependency_manager is None:
        _dependency_manager = DependencyManager(parent)
    elif parent is not None:
        _dependency_manager.parent = parent
    return _dependency_manager
