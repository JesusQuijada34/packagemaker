"""
Panel de configuración de intérpretes Python para pmCodeEditor.
"""

import os
import sys
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QMessageBox,
    QProgressBar,
    QGroupBox,
    QComboBox,
    QCheckBox,
)
from PyQt6.QtCore import Qt, pyqtSignal

from lib.python_portable_manager import get_python_manager

DARK_PANEL_QSS = """
QDialog {
    background-color: #1e1e2e;
    color: #d4d4d4;
}
QGroupBox {
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 8px;
    font-weight: bold;
    color: #ff5722;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 8px;
}
QListWidget {
    background-color: #252526;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 5px;
}
QListWidget::item {
    padding: 8px;
    border-radius: 4px;
}
QListWidget::item:selected {
    background-color: #ff5722;
    color: white;
}
QPushButton {
    background-color: #2d2d2d;
    color: #cccccc;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #3c3c3c;
}
QPushButton#primary {
    background-color: #ff5722;
    color: white;
    border: none;
}
QPushButton#primary:hover {
    background-color: #ff7043;
}
QPushButton#danger {
    background-color: #d32f2f;
    color: white;
}
QPushButton#danger:hover {
    background-color: #f44336;
}
QProgressBar {
    background-color: #333;
    border: none;
    border-radius: 4px;
    height: 6px;
}
QProgressBar::chunk {
    background-color: #ff5722;
    border-radius: 4px;
}
QComboBox, QCheckBox {
    color: #cccccc;
}
"""


class InterpreterConfigDialog(QDialog):
    interpreter_changed = pyqtSignal(str)

    def __init__(self, parent=None, current_interpreter: Optional[str] = None):
        super().__init__(parent)
        self.current_interpreter = current_interpreter
        self.manager = get_python_manager()
        self._download_version: Optional[str] = None
        self.init_ui()
        self.load_interpreters()

    def init_ui(self):
        self.setWindowTitle("Configuración de intérpretes Python")
        self.setMinimumSize(650, 500)
        self.setStyleSheet(DARK_PANEL_QSS)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("Gestión de intérpretes Python")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #ff5722;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        installed_group = QGroupBox("Intérpretes instalados")
        installed_layout = QVBoxLayout(installed_group)

        self.interpreters_list = QListWidget()
        self.interpreters_list.currentItemChanged.connect(self._update_buttons)
        installed_layout.addWidget(self.interpreters_list)

        btn_layout = QHBoxLayout()
        self.btn_set_default = QPushButton("Establecer como predeterminado")
        self.btn_set_default.setObjectName("primary")
        self.btn_set_default.clicked.connect(self.set_as_default)

        self.btn_uninstall = QPushButton("Desinstalar")
        self.btn_uninstall.setObjectName("danger")
        self.btn_uninstall.clicked.connect(self.uninstall_interpreter)

        btn_layout.addWidget(self.btn_set_default)
        btn_layout.addWidget(self.btn_uninstall)
        btn_layout.addStretch()
        installed_layout.addLayout(btn_layout)
        layout.addWidget(installed_group)

        download_group = QGroupBox("Descargar nuevo intérprete")
        download_layout = QVBoxLayout(download_group)

        version_layout = QHBoxLayout()
        version_layout.addWidget(QLabel("Versión:"))
        self.version_combo = QComboBox()
        self.version_combo.setMinimumWidth(150)
        version_layout.addWidget(self.version_combo)
        version_layout.addStretch()
        download_layout.addLayout(version_layout)

        self.download_progress = QProgressBar()
        self.download_progress.setVisible(False)
        download_layout.addWidget(self.download_progress)

        self.download_status = QLabel("")
        self.download_status.setStyleSheet("color: #aaaaaa; font-size: 12px;")
        download_layout.addWidget(self.download_status)

        self.btn_download = QPushButton("Descargar e instalar")
        self.btn_download.setObjectName("primary")
        self.btn_download.clicked.connect(self.download_interpreter)
        download_layout.addWidget(self.btn_download)
        layout.addWidget(download_group)

        settings_group = QGroupBox("Configuración de detección")
        settings_layout = QVBoxLayout(settings_group)

        self.check_pyqt = QCheckBox("Excluir PyQt6 de la verificación automática")
        self.check_pyqt.setChecked(True)
        settings_layout.addWidget(self.check_pyqt)

        self.check_local = QCheckBox("Excluir módulos locales del proyecto")
        self.check_local.setChecked(True)
        settings_layout.addWidget(self.check_local)

        self.auto_check = QCheckBox("Verificar dependencias automáticamente al abrir archivos")
        self.auto_check.setChecked(True)
        settings_layout.addWidget(self.auto_check)
        layout.addWidget(settings_group)

        final_btn_layout = QHBoxLayout()
        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.accept)
        final_btn_layout.addStretch()
        final_btn_layout.addWidget(btn_close)
        layout.addLayout(final_btn_layout)

        self._load_available_versions()

    def apply_editor_settings(self, settings: dict):
        self.check_pyqt.setChecked(settings.get("exclude_pyqt", True))
        self.check_local.setChecked(settings.get("exclude_local", True))
        self.auto_check.setChecked(settings.get("auto_check", True))
        if settings.get("default_interpreter"):
            self.current_interpreter = settings["default_interpreter"]

    def _load_available_versions(self):
        self.version_combo.clear()
        for ver in self.manager.get_available_versions():
            info = self.manager.get_all_versions_info().get(ver, {})
            suffix = " (instalado)" if info.get("installed") else ""
            self.version_combo.addItem(f"Python {ver}{suffix}", ver)

    def load_interpreters(self):
        self.interpreters_list.clear()
        current_norm = os.path.normpath(self.current_interpreter) if self.current_interpreter else ""

        for name, path, version, is_portable in self._get_all_interpreters():
            is_default = os.path.normpath(path) == current_norm
            mark = "* " if is_default else "  "
            item = QListWidgetItem(f"{mark}{name}\n{path}")
            item.setData(
                Qt.ItemDataRole.UserRole,
                {"name": name, "path": path, "version": version, "portable": is_portable},
            )
            self.interpreters_list.addItem(item)
            if is_default:
                item.setSelected(True)

        self._update_buttons()

    def _get_all_interpreters(self) -> List[Tuple[str, str, Optional[str], bool]]:
        rows: List[Tuple[str, str, Optional[str], bool]] = []
        seen = set()

        for version in self.manager.get_installed_versions():
            python_exe = self.manager.get_python_exe(version)
            if python_exe and python_exe.exists():
                path = str(python_exe)
                if path not in seen:
                    rows.append((f"Python {version} (Portable)", path, version, True))
                    seen.add(path)

        for label, finder in (("Python del sistema", "python"), ("Python3 del sistema", "python3")):
            found = shutil.which(finder)
            if found and found not in seen:
                rows.append((label, found, None, False))
                seen.add(found)

        if sys.executable not in seen:
            rows.append(
                (
                    f"Python del editor ({sys.version_info.major}.{sys.version_info.minor})",
                    sys.executable,
                    None,
                    False,
                )
            )
        return rows

    def _update_buttons(self):
        item = self.interpreters_list.currentItem()
        has_selection = item is not None
        portable = False
        if item:
            portable = item.data(Qt.ItemDataRole.UserRole).get("portable", False)
        self.btn_set_default.setEnabled(has_selection)
        self.btn_uninstall.setEnabled(has_selection and portable)

    def set_as_default(self):
        item = self.interpreters_list.currentItem()
        if not item:
            return
        data = item.data(Qt.ItemDataRole.UserRole)
        path = data["path"]
        self.current_interpreter = path
        self.interpreter_changed.emit(path)
        self.load_interpreters()
        QMessageBox.information(self, "Predeterminado", f"Intérprete activo:\n{data['name']}\n{path}")

    def uninstall_interpreter(self):
        item = self.interpreters_list.currentItem()
        if not item:
            return
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data.get("portable") or not data.get("version"):
            QMessageBox.warning(
                self,
                "No se puede desinstalar",
                "Solo se pueden desinstalar intérpretes portables descargados.",
            )
            return

        reply = QMessageBox.question(
            self,
            "Confirmar desinstalación",
            f"¿Desinstalar {data['name']}?\n\n{data['path']}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            if self.manager.uninstall_version(data["version"]):
                if self.current_interpreter == data["path"]:
                    self.current_interpreter = None
                self.load_interpreters()
                self._load_available_versions()
                QMessageBox.information(self, "Desinstalado", f"{data['name']} eliminado.")

    def download_interpreter(self):
        version = self.version_combo.currentData()
        if not version:
            return
        if self.manager.get_installation_status(version):
            QMessageBox.information(self, "Ya instalado", f"Python {version} ya está instalado.")
            return

        self._download_version = version
        self.btn_download.setEnabled(False)
        self.download_progress.setVisible(True)
        self.download_progress.setValue(0)

        self.manager.installation_progress.connect(self._on_download_progress)
        self.manager.installation_finished.connect(self._on_download_finished)
        self.manager.status_message.connect(self.download_status.setText)
        self.manager.install_version(version)

    def _on_download_progress(self, ver: str, percent: int):
        if ver == self._download_version:
            self.download_progress.setValue(percent)

    def _on_download_finished(self, ver: str, success: bool):
        if ver != self._download_version:
            return
        self.download_progress.setVisible(False)
        self.btn_download.setEnabled(True)
        if success:
            self.download_status.setText(f"Python {ver} instalado correctamente")
            exe = self.manager.get_python_exe(ver)
            if exe:
                self.current_interpreter = str(exe)
                self.interpreter_changed.emit(str(exe))
            self.load_interpreters()
            self._load_available_versions()
        else:
            self.download_status.setText(f"Error instalando Python {ver}")

    def get_settings(self) -> dict:
        return {
            "exclude_pyqt": self.check_pyqt.isChecked(),
            "exclude_local": self.check_local.isChecked(),
            "auto_check": self.auto_check.isChecked(),
            "default_interpreter": self.current_interpreter,
        }
