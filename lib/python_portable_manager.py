"""
Gestor de Python portables para pmCodeEditor.
Descarga e instala builds embed de python.org (Windows).
"""

import json
import platform
import shutil
import subprocess
import tarfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional

import requests
from PyQt6.QtCore import QObject, QThread, pyqtSignal

# =============================================================================
# CONSTANTES
# =============================================================================

PYTHON_VERSIONS = {
    "3.8": {
        "version": "3.8.10",
        "windows_url": "https://www.python.org/ftp/python/3.8.10/python-3.8.10-embed-amd64.zip",
        "recommended": False,
    },
    "3.9": {
        "version": "3.9.13",
        "windows_url": "https://www.python.org/ftp/python/3.9.13/python-3.9.13-embed-amd64.zip",
        "recommended": False,
    },
    "3.10": {
        "version": "3.10.11",
        "windows_url": "https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip",
        "recommended": False,
    },
    "3.11": {
        "version": "3.11.9",
        "windows_url": "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip",
        "recommended": False,
    },
    "3.12": {
        "version": "3.12.10",
        "windows_url": "https://www.python.org/ftp/python/3.12.10/python-3.12.10-embed-amd64.zip",
        "recommended": True,
    },
    "3.13": {
        "version": "3.13.3",
        "windows_url": "https://www.python.org/ftp/python/3.13.3/python-3.13.3-embed-amd64.zip",
        "recommended": False,
    },
}

GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"


@dataclass
class PythonInstallation:
    version: str
    path: Path
    python_exe: Path
    pip_exe: Path
    is_installed: bool = False
    size_mb: float = 0.0


class DownloadWorker(QThread):
    progress = pyqtSignal(int, int)
    finished = pyqtSignal(bool, str)
    status = pyqtSignal(str)

    def __init__(self, url: str, destination: Path):
        super().__init__()
        self.url = url
        self.destination = destination

    def run(self):
        try:
            self.status.emit(f"Descargando {self.url.split('/')[-1]}...")
            response = requests.get(self.url, stream=True, timeout=60)
            response.raise_for_status()
            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0
            self.destination.parent.mkdir(parents=True, exist_ok=True)
            with open(self.destination, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            self.progress.emit(downloaded, total_size)
            self.finished.emit(True, str(self.destination))
        except Exception as e:
            self.finished.emit(False, str(e))


class PythonPortableManager(QObject):
    installation_progress = pyqtSignal(str, int)
    installation_finished = pyqtSignal(str, bool)
    status_message = pyqtSignal(str)

    def __init__(self, base_dir: Optional[Path] = None):
        super().__init__()
        if base_dir is None:
            base_dir = Path(__file__).resolve().parent.parent / "data" / "pmCodeEditor"
        self.base_dir = Path(base_dir)
        self.python_dir = self.base_dir / "python"
        self.packages_dir = self.base_dir / "packages"
        self.config_file = self.base_dir / "config.json"
        self.installations: Dict[str, PythonInstallation] = {}
        self.current_downloads: Dict[str, DownloadWorker] = {}
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.packages_dir.mkdir(parents=True, exist_ok=True)
        self._load_config()
        self._discover_installations()

    def _version_dir_name(self, version: str) -> str:
        return f"python{version.replace('.', '')}"

    def _load_config(self):
        if not self.config_file.exists():
            return
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            for ver, data in config.get("installations", {}).items():
                self.installations[ver] = PythonInstallation(
                    version=ver,
                    path=Path(data["path"]),
                    python_exe=Path(data["python_exe"]),
                    pip_exe=Path(data["pip_exe"]),
                    is_installed=data.get("is_installed", False),
                    size_mb=data.get("size_mb", 0),
                )
        except (json.JSONDecodeError, KeyError, OSError):
            pass

    def _save_config(self):
        config = {
            "installations": {},
            "default_version": self.get_default_version(),
        }
        for ver, install in self.installations.items():
            config["installations"][ver] = {
                "path": str(install.path),
                "python_exe": str(install.python_exe),
                "pip_exe": str(install.pip_exe),
                "is_installed": install.is_installed,
                "size_mb": install.size_mb,
            }
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

    def _discover_installations(self):
        if not self.python_dir.exists():
            return
        for folder in self.python_dir.iterdir():
            if not folder.is_dir() or not folder.name.startswith("python"):
                continue
            ver_key = folder.name.replace("python", "")
            if len(ver_key) >= 2:
                version = f"{ver_key[0]}.{ver_key[1:]}"
            else:
                continue
            python_exe = folder / "python.exe"
            if not python_exe.exists():
                found = list(folder.rglob("python.exe"))
                if found:
                    python_exe = found[0]
            if python_exe.exists():
                pip_exe = folder / "Scripts" / "pip.exe"
                if not pip_exe.exists():
                    pip_exe = folder / "pip.exe"
                if version not in self.installations or not self.installations[version].is_installed:
                    self.installations[version] = PythonInstallation(
                        version=version,
                        path=folder,
                        python_exe=python_exe,
                        pip_exe=pip_exe,
                        is_installed=True,
                        size_mb=self._get_dir_size(folder) / (1024 * 1024),
                    )

    def get_available_versions(self) -> List[str]:
        return list(PYTHON_VERSIONS.keys())

    def get_installation_status(self, version: str) -> bool:
        if version in self.installations:
            inst = self.installations[version]
            return inst.is_installed and inst.python_exe.exists()
        return False

    def get_python_exe(self, version: str) -> Optional[Path]:
        if self.get_installation_status(version):
            return self.installations[version].python_exe
        return None

    def get_default_version(self) -> str:
        for ver, info in PYTHON_VERSIONS.items():
            if info.get("recommended"):
                return ver
        return "3.12"

    def _get_download_url(self, version: str) -> Optional[str]:
        ver_info = PYTHON_VERSIONS.get(version)
        if not ver_info:
            return None
        if platform.system().lower() == "windows":
            return ver_info.get("windows_url")
        return None

    def install_version(self, version: str, callback: Optional[Callable[[bool, str], None]] = None):
        if self.get_installation_status(version):
            self.status_message.emit(f"Python {version} ya está instalado")
            self.installation_finished.emit(version, True)
            if callback:
                callback(True, version)
            return

        if platform.system().lower() != "windows":
            msg = "La descarga portable solo está disponible en Windows por ahora."
            self.status_message.emit(msg)
            self.installation_finished.emit(version, False)
            if callback:
                callback(False, version)
            return

        url = self._get_download_url(version)
        if not url:
            self.status_message.emit(f"No hay URL de descarga para Python {version}")
            self.installation_finished.emit(version, False)
            if callback:
                callback(False, version)
            return

        dest_dir = self.python_dir / self._version_dir_name(version)
        dest_dir.mkdir(parents=True, exist_ok=True)
        temp_file = dest_dir / f"python-{version}-embed.zip"

        self.status_message.emit(f"Descargando Python {version}...")
        worker = DownloadWorker(url, temp_file)
        worker.progress.connect(
            lambda curr, total: self.installation_progress.emit(
                version, int(curr * 100 / total) if total > 0 else 0
            )
        )
        worker.finished.connect(
            lambda success, result: self._on_download_finished(
                version, success, result, dest_dir, temp_file, callback
            )
        )
        worker.start()
        self.current_downloads[version] = worker

    def _on_download_finished(
        self,
        version: str,
        success: bool,
        result: str,
        dest_dir: Path,
        temp_file: Path,
        callback: Optional[Callable[[bool, str], None]],
    ):
        self.current_downloads.pop(version, None)
        if not success:
            self.status_message.emit(f"Error descargando Python {version}: {result}")
            self.installation_finished.emit(version, False)
            if callback:
                callback(False, version)
            return

        self.status_message.emit(f"Extrayendo Python {version}...")
        self.installation_progress.emit(version, 50)

        try:
            with zipfile.ZipFile(temp_file, "r") as zf:
                zf.extractall(dest_dir)
            temp_file.unlink(missing_ok=True)

            python_exe, pip_exe = self._configure_windows_embed(dest_dir)
            size_mb = self._get_dir_size(dest_dir) / (1024 * 1024)

            install = PythonInstallation(
                version=version,
                path=dest_dir,
                python_exe=python_exe,
                pip_exe=pip_exe,
                is_installed=True,
                size_mb=size_mb,
            )
            self.installations[version] = install
            self._save_config()

            self.status_message.emit(
                f"Python {version} instalado correctamente ({size_mb:.1f} MB)"
            )
            self.installation_progress.emit(version, 100)
            self.installation_finished.emit(version, True)
            if callback:
                callback(True, version)
        except Exception as e:
            self.status_message.emit(f"Error extrayendo Python {version}: {e}")
            self.installation_finished.emit(version, False)
            if callback:
                callback(False, version)

    def _configure_windows_embed(self, dest_dir: Path) -> tuple:
        python_exe = dest_dir / "python.exe"
        if not python_exe.exists():
            candidates = list(dest_dir.rglob("python.exe"))
            if not candidates:
                raise FileNotFoundError("python.exe no encontrado tras extraer")
            python_exe = candidates[0]
            dest_dir = python_exe.parent

        pth_files = set(dest_dir.glob("python*._pth")) | set(dest_dir.glob("python*.pth"))
        for pth_file in pth_files:
            content = pth_file.read_text(encoding="utf-8")
            if "#import site" in content:
                content = content.replace("#import site", "import site")
            elif "import site" not in content:
                content = content.strip() + "\nimport site\n"
            pth_file.write_text(content, encoding="utf-8")

        self._install_pip_for_python(python_exe)
        pip_exe = dest_dir / "Scripts" / "pip.exe"
        if not pip_exe.exists():
            pip_exe = dest_dir / "pip.exe"
        return python_exe, pip_exe

    def _install_pip_for_python(self, python_exe: Path):
        get_pip_path = python_exe.parent / "get-pip.py"
        try:
            response = requests.get(GET_PIP_URL, timeout=60)
            response.raise_for_status()
            get_pip_path.write_bytes(response.content)
            subprocess.run(
                [str(python_exe), str(get_pip_path), "--no-warn-script-location"],
                capture_output=True,
                check=False,
                timeout=120,
            )
            get_pip_path.unlink(missing_ok=True)
        except Exception as e:
            print(f"[WARN] No se pudo instalar pip para {python_exe}: {e}")

    def _get_dir_size(self, path: Path) -> int:
        total = 0
        for entry in path.rglob("*"):
            if entry.is_file():
                total += entry.stat().st_size
        return total

    def uninstall_version(self, version: str) -> bool:
        if version not in self.installations:
            return False
        install = self.installations[version]
        if install.path.exists():
            shutil.rmtree(install.path, ignore_errors=True)
        del self.installations[version]
        self._save_config()
        self.status_message.emit(f"Python {version} desinstalado")
        return True

    def get_installed_versions(self) -> List[str]:
        return [v for v, i in self.installations.items() if i.is_installed and i.python_exe.exists()]

    def get_all_versions_info(self) -> Dict[str, dict]:
        result = {}
        for ver, info in PYTHON_VERSIONS.items():
            result[ver] = {
                "version": info["version"],
                "recommended": info.get("recommended", False),
                "installed": self.get_installation_status(ver),
                "url": self._get_download_url(ver),
                "size_mb": self.installations[ver].size_mb if ver in self.installations else 0,
                "platform_supported": platform.system().lower() == "windows",
            }
        return result


_python_manager: Optional[PythonPortableManager] = None


def get_python_manager() -> PythonPortableManager:
    global _python_manager
    if _python_manager is None:
        _python_manager = PythonPortableManager()
    return _python_manager
