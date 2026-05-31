"""
Dashboard UWP y asistente de nuevo proyecto para pmCodeEditor.
"""

import os
import sys
import json
import platform
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Callable

try:
    from PyQt6.QtWidgets import (
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QFileDialog,
        QMessageBox,
        QDialog,
        QLineEdit,
        QStatusBar,
        QGroupBox,
        QGridLayout,
        QListWidget,
        QListWidgetItem,
        QComboBox,
        QFormLayout,
        QGraphicsDropShadowEffect,
    )
    from PyQt6.QtGui import QColor
    from PyQt6.QtCore import Qt, pyqtSignal
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    class QMainWindow: pass
    class QWidget: pass
    class QDialog: pass
    class pyqtSignal:
        def __init__(self, *args): pass
        def connect(self, func): pass
        def emit(self, *args): pass

EDITOR_CONFIG_PATH = Path(__file__).resolve().parent.parent / "data" / "pmCodeEditor" / "editor_config.json"

DARK_QSS = """
QMainWindow, QDialog, QWidget {
    background-color: #1E1E2E;
    color: #D4D4D4;
}
QLabel { color: #D4D4D4; }
QPushButton {
    background-color: #ff5722;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
}
QPushButton:hover { background-color: #ff784e; }
QLineEdit, QComboBox {
    background-color: #252526;
    color: #D4D4D4;
    border: 1px solid #3C3C3C;
    padding: 6px;
    border-radius: 4px;
}
QGroupBox {
    border: 1px solid #3C3C3C;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 10px;
    color: #ff5722;
    font-weight: bold;
}
"""


class DashboardCard(QPushButton):
    """Tarjeta estilo UWP para el dashboard."""

    def __init__(self, title: str, description: str, icon: str, parent=None):
        super().__init__(parent)
        self.setFixedSize(280, 180)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(32, 32, 40, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: rgba(45, 45, 55, 0.95);
                border: 1px solid rgba(255, 87, 34, 0.35);
            }
            QPushButton:pressed {
                background-color: rgba(25, 25, 30, 0.95);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 32px; border: none; background: transparent;")
        icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            "font-size: 17px; font-weight: bold; color: white; border: none; background: transparent;"
        )
        title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setStyleSheet(
            "font-size: 12px; color: #aaaaaa; border: none; background: transparent;"
        )
        desc_label.setWordWrap(True)
        desc_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        layout.addWidget(desc_label)
        layout.addStretch()

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)


class NewProjectWizard(QDialog):
    """Asistente para crear proyectos PackageMaker desde src/templates/."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Proyecto PackageMaker")
        self.setMinimumSize(520, 560)
        self.setStyleSheet(DARK_QSS)
        self.project_path: Optional[str] = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        title = QLabel("Crear nuevo proyecto")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #ff5722;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)

        self.input_publisher = QLineEdit()
        self.input_publisher.setPlaceholderText("Ej: influent")
        form.addRow("Publisher:", self.input_publisher)

        self.input_app = QLineEdit()
        self.input_app.setPlaceholderText("Ej: my-app")
        form.addRow("ID interno:", self.input_app)

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Ej: Mi Aplicacion")
        form.addRow("Nombre:", self.input_name)

        self.input_version = QLineEdit("1.0.0")
        form.addRow("Version:", self.input_version)

        self.input_author = QLineEdit()
        self.input_author.setPlaceholderText("GitHub username")
        form.addRow("Autor:", self.input_author)

        self.input_platform = QComboBox()
        self.input_platform.addItems(["Windows", "Linux", "Multiplataforma"])
        form.addRow("Plataforma:", self.input_platform)

        self.input_location = QLineEdit()
        default_loc = Path.home() / "Documents" / "Packagemaker Projects"
        self.input_location.setPlaceholderText(str(default_loc))
        btn_browse = QPushButton("...")
        btn_browse.setFixedWidth(36)
        btn_browse.clicked.connect(self.browse_location)
        loc_row = QHBoxLayout()
        loc_row.addWidget(self.input_location)
        loc_row.addWidget(btn_browse)
        form.addRow("Ubicacion:", loc_row)

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btn_create = QPushButton("Crear proyecto")
        btn_create.clicked.connect(self.create_project)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_create)
        layout.addLayout(btn_row)

    def browse_location(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar ubicacion")
        if folder:
            self.input_location.setText(folder)

    def create_project(self):
        publisher = self.input_publisher.text().strip()
        app_id = self.input_app.text().strip().replace(" ", "-")
        name = self.input_name.text().strip()
        version = self.input_version.text().strip() or "1.0.0"
        author = self.input_author.text().strip()

        if not publisher or not app_id or not name:
            QMessageBox.warning(self, "Campos requeridos", "Publisher, ID y Nombre son obligatorios.")
            return

        platform_map = {
            "Windows": "Knosthalij",
            "Linux": "Danenone",
            "Multiplataforma": "AlphaCube",
        }
        plat = platform_map.get(self.input_platform.currentText(), "Knosthalij")

        base_dir = self.input_location.text().strip() or str(
            Path.home() / "Documents" / "Packagemaker Projects"
        )
        pub_slug = publisher.strip().lower().replace(" ", "-")
        project_path = Path(base_dir) / f"{pub_slug}.{app_id}"

        if project_path.exists():
            QMessageBox.warning(self, "Ya existe", f"La carpeta ya existe:\n{project_path}")
            return

        try:
            from lib.template_engine import create_project_from_templates

            create_project_from_templates(
                project_path,
                publisher,
                app_id,
                name,
                author or "Unknown",
                plat,
                version_base=version,
                description="Aplicacion creada con PackageMaker IDE",
            )
            self.project_path = str(project_path)
            self.accept()
        except (OSError, FileNotFoundError) as e:
            QMessageBox.critical(self, "Error", f"No se pudo crear el proyecto:\n{e}")

    def get_project_path(self) -> Optional[str]:
        return self.project_path


class DashboardWindow(QMainWindow):
    """Ventana principal con dashboard estilo UWP."""

    def __init__(self, python_path: Optional[str] = None, launch_editor: Callable = None):
        super().__init__()
        self.python_path = python_path or os.environ.get("PM_PYTHON_PATH", sys.executable)
        self._launch_editor = launch_editor
        self.current_project: Optional[str] = None
        self.config: dict = {}
        self.setWindowTitle("PackageMaker IDE")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        self.setStyleSheet(DARK_QSS)
        self._build_ui()
        self.load_config()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(40, 32, 40, 32)
        layout.setSpacing(24)

        layout.addWidget(self._create_header())

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(24)

        card_github = DashboardCard(
            "Modificar repositorio",
            "Abre un repositorio clonado de GitHub para editarlo y compilarlo",
            "📂",
        )
        card_github.clicked.connect(self.open_github_repo)
        cards_layout.addWidget(card_github)

        card_pm = DashboardCard(
            "Proyecto PackageMaker",
            "Abre un proyecto con details.xml, depuracion y compilacion",
            "📦",
        )
        card_pm.clicked.connect(self.open_pm_project)
        cards_layout.addWidget(card_pm)

        card_new = DashboardCard(
            "Nuevo proyecto",
            "Crea un proyecto desde cero con plantillas optimizadas",
            "✨",
        )
        card_new.clicked.connect(self.new_project)
        cards_layout.addWidget(card_new)

        cards_layout.addStretch()
        layout.addLayout(cards_layout)

        layout.addWidget(self._create_recent_panel())
        layout.addStretch()

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo")

    def _create_header(self) -> QWidget:
        header = QWidget()
        row = QHBoxLayout(header)
        row.setContentsMargins(0, 0, 0, 8)

        title = QLabel("PackageMaker IDE")
        title.setStyleSheet("font-size: 30px; font-weight: bold; color: #ff5722;")
        row.addWidget(title)
        row.addStretch()

        py_label = QLabel(f"Python: {Path(self.python_path).name} | {platform.system()}")
        py_label.setStyleSheet("color: #aaaaaa; font-size: 12px;")
        py_label.setToolTip(self.python_path)
        row.addWidget(py_label)

        config_btn = QPushButton("⚙")
        config_btn.setFixedSize(36, 36)
        config_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255,255,255,0.06);
                border-radius: 18px;
                font-size: 16px;
            }
            QPushButton:hover { background-color: rgba(255,255,255,0.12); }
        """)
        config_btn.clicked.connect(self.show_interpreter_config)
        row.addWidget(config_btn)
        return header

    def _create_recent_panel(self) -> QGroupBox:
        group = QGroupBox("Proyectos recientes")
        box = QVBoxLayout(group)
        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(140)
        self.recent_list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                color: #cccccc;
            }
            QListWidget::item { padding: 6px; border-radius: 4px; }
            QListWidget::item:selected {
                background: rgba(255, 87, 34, 0.25);
                color: #ff5722;
            }
        """)
        self.recent_list.itemDoubleClicked.connect(self._on_recent_double_click)
        box.addWidget(self.recent_list)
        return group

    def open_github_repo(self):
        default = Path.home() / "Documents" / "GitHub"
        if not default.exists():
            default = Path.home()
        repo_path = QFileDialog.getExistingDirectory(
            self, "Seleccionar repositorio GitHub", str(default)
        )
        if repo_path:
            self._open_project(repo_path)

    def open_pm_project(self):
        default = Path.home() / "Documents" / "Packagemaker Projects"
        if not default.exists():
            default = Path.home()
        project_path = QFileDialog.getExistingDirectory(
            self, "Seleccionar proyecto PackageMaker", str(default)
        )
        if project_path:
            self._open_project(project_path, force_pm=True)

    def new_project(self):
        wizard = NewProjectWizard(self)
        if wizard.exec() == QDialog.DialogCode.Accepted:
            path = wizard.get_project_path()
            if path:
                self._add_to_recent(path)
                self._open_as_pm_project(path)

    def _open_project(self, path: str, force_pm: bool = False):
        self._add_to_recent(path)
        if force_pm or os.path.exists(os.path.join(path, "details.xml")):
            self._open_as_pm_project(path)
        else:
            self._open_as_generic_project(path)

    def _open_as_pm_project(self, path: str):
        main_script = None
        details_path = os.path.join(path, "details.xml")
        if os.path.exists(details_path):
            try:
                root = ET.parse(details_path).getroot()
                app_name = root.findtext("app", "")
                if app_name:
                    for candidate in (
                        os.path.join(path, f"{app_name}.py"),
                        os.path.join(path, "app", f"{app_name}.py"),
                    ):
                        if os.path.isfile(candidate):
                            main_script = candidate
                            break
            except ET.ParseError:
                pass

        if not main_script:
            for root_dir, _, files in os.walk(path):
                for fname in sorted(files):
                    if fname.endswith(".py") and fname not in ("setup.py",):
                        main_script = os.path.join(root_dir, fname)
                        break
                if main_script:
                    break

        self._launch_editor(main_script, path)

    def _open_as_generic_project(self, path: str):
        main_script = None
        for fname in sorted(os.listdir(path)):
            if fname.endswith(".py"):
                main_script = os.path.join(path, fname)
                break
        self._launch_editor(main_script, path)

    def _launch_editor(self, file_path: Optional[str], project_path: str):
        self.current_project = project_path
        if self._launch_editor:
            self._launch_editor(file_path, project_path, self.python_path)
        self.close()

    def _on_recent_double_click(self, item: QListWidgetItem):
        path = item.data(Qt.ItemDataRole.UserRole)
        if path and os.path.exists(path):
            self._open_project(path)

    def _add_to_recent(self, path: str):
        recents = self.config.get("recent_projects", [])
        if path in recents:
            recents.remove(path)
        recents.insert(0, path)
        self.config["recent_projects"] = recents[:10]
        self.save_config()
        self._update_recent_list()

    def _update_recent_list(self):
        self.recent_list.clear()
        for path in self.config.get("recent_projects", []):
            if os.path.isdir(path):
                item = QListWidgetItem(f"{os.path.basename(path)}\n{path}")
                item.setData(Qt.ItemDataRole.UserRole, path)
                self.recent_list.addItem(item)

    def load_config(self):
        if EDITOR_CONFIG_PATH.exists():
            try:
                with open(EDITOR_CONFIG_PATH, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except (json.JSONDecodeError, OSError):
                self.config = {}
        if not self.config:
            self.config = {
                "recent_projects": [],
                "default_interpreter": self.python_path,
                "exclude_pyqt": True,
                "exclude_local": True,
                "auto_check": True,
            }
        if self.config.get("default_interpreter"):
            self.python_path = self.config["default_interpreter"]
            os.environ["PM_PYTHON_PATH"] = self.python_path
        self._update_recent_list()

    def save_config(self):
        self.config["default_interpreter"] = self.python_path
        EDITOR_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(EDITOR_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)

    def show_interpreter_config(self):
        from lib.interpreter_config_dialog import InterpreterConfigDialog

        dialog = InterpreterConfigDialog(self, self.python_path)
        dialog.apply_editor_settings({
            "exclude_pyqt": self.config.get("exclude_pyqt", True),
            "exclude_local": self.config.get("exclude_local", True),
            "auto_check": self.config.get("auto_check", True),
            "default_interpreter": self.python_path,
        })

        def on_changed(path: str):
            self.python_path = path
            os.environ["PM_PYTHON_PATH"] = path
            self.save_config()

        dialog.interpreter_changed.connect(on_changed)
        dialog.exec()
        settings = dialog.get_settings()
        self.config.update(settings)
        if settings.get("default_interpreter"):
            self.python_path = settings["default_interpreter"]
        self.save_config()
