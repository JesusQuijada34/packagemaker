import os
import shutil
import zipfile
from PyQt6.QtCore import Qt
from PyQt6 import QtCore
from PyQt6.QtWidgets import QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton
from PyQt6.QtGui import QPixmap, QIcon
from leviathan_ui import CustomTitleBar, LeviathanDialog
from lib.BuildThread import BuildThread
from lib.outputTerminalDialog import OutputTerminalDialog
from lib.moonFixWizard import detectar_modo_sistema

# These need to be imported from the main module or defined here
# For now, I'll assume they are available or need to be moved
# get_github_style, find_python_executable, BASE_DIR, Fluthin_APPS, TAB_ICONS

def get_github_style(is_dark):
    """Genera estilos CSS para botones al estilo GitHub (Action Naranja, Normal B/W)"""
    if is_dark:
        # Action (Orange) - Dark
        action_style = """
            QPushButton {
                background-color: #d2691e;
                color: #ffffff;
                border: 1px solid #c15c1d;
                border-radius: 6px;
                padding: 5px 16px;
                font-family: 'Segoe UI', sans-serif;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e07b3e;
                border-color: #d96d27;
            }
            QPushButton:pressed {
                background-color: #bd5a17;
            }
        """
        # Normal (Black/Dark Grey) - Dark
        normal_style = """
            QPushButton {
                background-color: #21262d;
                color: #c9d1d9;
                border: 1px solid rgba(240, 246, 252, 0.1);
                border-radius: 6px;
                padding: 5px 16px;
                font-family: 'Segoe UI', sans-serif;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                color: #d96d27;
                border: 1px solid #d96d27;
                background-color: transparent;
            }
        """
    else:
        # Action (Orange) - Light
        action_style = """
            QPushButton {
                background-color: #d2691e;
                color: #ffffff;
                border: 1px solid #c15c1d;
                border-radius: 6px;
                padding: 5px 16px;
                font-family: 'Segoe UI', sans-serif;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e07b3e;
                border-color: #d96d27;
            }
            QPushButton:pressed {
                background-color: #bd5a17;
            }
        """
        # Normal (Black/Dark Grey) - Light
        normal_style = """
            QPushButton {
                background-color: #f6f8fa;
                color: #24292e;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                padding: 5px 16px;
                font-family: 'Segoe UI', sans-serif;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e1e4e8;
                border-color: #d1d5da;
            }
        """
    return action_style, normal_style


class ProjectDetailsDialog(QDialog):
    """Dialogo detallado para gestión de proyectos/apps"""
    def __init__(self, parent, pkg_data, is_app=False, manager_ref=None):
        super().__init__(parent)
        self.pkg = pkg_data
        self.is_app = is_app
        self.manager = manager_ref
        # Fix: Ensure Qt.WindowType.Dialog flag is present
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(550, 450) # Reduced size slightly
        self.init_ui()

    def init_ui(self):
        self.container = QWidget(self)
        self.container.setObjectName("DetailsContainer")
        # Base container style
        self.container.setStyleSheet("""
            #DetailsContainer {
                background-color: #ffffff;
                border: 1px solid #d1d5da;
                border-radius: 8px;
            }
        """)

        is_dark = detect_dark = detectar_modo_sistema()
        if is_dark:
             self.container.setStyleSheet("""
            #DetailsContainer {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 8px;
                color: #c9d1d9;
            }
            QLabel { color: #c9d1d9; font-family: 'Segoe UI', sans-serif; }
            QListWidget {
                background-color: #161b22;
                border: 1px solid #30363d;
                color: #c9d1d9;
                border-radius: 6px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #1f2428;
                border: 1px solid #58a6ff;
                border-radius: 4px;
            }
        """)
        else:
            # Light mode styles for list
            self.container.setStyleSheet(self.container.styleSheet() + """
            QListWidget {
                background-color: #f6f8fa;
                border: 1px solid #e1e4e8;
                color: #24292e;
                border-radius: 6px;
                padding: 4px;
            }
            QListWidget::item { padding: 5px; }
            QListWidget::item:selected {
                background-color: #e1e4e8;
                border: 1px solid #0366d6;
                border-radius: 4px;
            }
            """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.container)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title Bar
        title = f"App: {self.pkg.get('titulo', 'Unknown')}" if self.is_app else f"Proyecto: {self.pkg.get('titulo', 'Unknown')}"
        icon_path = self.pkg.get("icon")
        icon_pm = QIcon(icon_path) if icon_path else None

        self.titlebar = CustomTitleBar(self, title=title, icon=icon_path or "")
        # Usamos el estilo nativo de LeviathanUI
        # self.titlebar.setStyleSheet(...)
        layout.addWidget(self.titlebar)

        # Contenido
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        # Info Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)

        # Icono grande
        icon_lbl = QLabel()
        pm = QPixmap(icon_path) if icon_path else QPixmap(80, 80)
        if not icon_path: pm.fill(Qt.transparent)
        icon_lbl.setPixmap(pm.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        icon_lbl.setFixedSize(80, 80)
        header_layout.addWidget(icon_lbl)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        title_lbl = QLabel(f"<h2 style='margin:0; font-size: 20px;'>{self.pkg.get('titulo')}</h2>")
        title_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        ver = self.pkg.get('version', '0.0')
        pub = self.pkg.get('empresa', 'Unknown').capitalize()
        categ = self.pkg.get('rating', 'Unknown') if not self.is_app else "Instalado"

        # Determine colors for meta text
        color_pub = "#58a6ff" if is_dark else "#0366d6"
        color_meta = "#8b949e" if is_dark else "#586069"

        meta_html = f"<span style='color:{color_pub}; font-weight:bold;'>{pub}</span> &bull; <span style='color:{color_meta};'>{ver}</span> &bull; <span style='color:{color_meta};'>{categ}</span>"
        meta_lbl = QLabel(meta_html)
        meta_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        folder_path = self.pkg.get('folder', '')
        # Truncate path if too long for display nicely
        short_path = (folder_path[:60] + '...') if len(folder_path) > 60 else folder_path

        folder_lbl = QLabel(short_path)
        folder_lbl.setToolTip(folder_path)
        folder_lbl.setStyleSheet(f"color: {color_meta}; font-size: 11px;")
        folder_lbl.setWordWrap(True)
        folder_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        info_layout.addWidget(title_lbl)
        info_layout.addWidget(meta_lbl)
        info_layout.addWidget(folder_lbl)
        info_layout.addStretch()

        header_layout.addLayout(info_layout)
        header_layout.addStretch() # Push everything to left
        content_layout.addLayout(header_layout)

        content_layout.addWidget(QLabel("<b>Scripts ejecutables:</b>"))

        self.scripts_list = QListWidget()
        self.scripts_list.setIconSize(QtCore.QSize(20,20))
        # Populamos
        if os.path.exists(self.pkg["folder"]):
            for root, _, files in os.walk(self.pkg["folder"]):
                for f in files:
                    if f.endswith(".py"):
                        full_p = os.path.join(root, f)
                        rel_p = os.path.relpath(full_p, self.pkg["folder"])
                        item = QListWidgetItem(QIcon("app/python-icon.png"), rel_p) # Placeholder icon if null
                        item.setData(QtCore.Qt.ItemDataRole.UserRole, full_p)
                        self.scripts_list.addItem(item)

        # Limit list height to avoid taking too much space
        self.scripts_list.setFixedHeight(120)
        content_layout.addWidget(self.scripts_list)

        content_layout.addWidget(self.scripts_list)

        # Botones de accion
        # Obtener estilos GitHub
        action_style, normal_style = get_github_style(is_dark)

        # Helper/Closure para botones
        def mk_btn(text, is_primary=False, icon_str=None):
            btn = QPushButton(text)
            btn.setFixedHeight(36)
            # No establecemos font aquí porque el stylesheet lo maneja mejor para coherencia
            if icon_str and icon_str in TAB_ICONS:
                # Opcional: Podríamos no usar iconos para ser mas fiel al estilo "limpio" de GitHub,
                # pero los conservamos por usabilidad.
                btn.setIcon(QIcon(TAB_ICONS[icon_str]))

            btn.setStyleSheet(action_style if is_primary else normal_style)
            return btn

        self.btn_run = mk_btn("Ejecutar", is_primary=False, icon_str="construir")
        self.btn_run.clicked.connect(self.run_selected_script)

        # Layout principal de botones
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        # Botones izquierdos
        btn_layout.addWidget(self.btn_run)

        if self.is_app:
            self.btn_uninstall = mk_btn("Desinstalar", is_primary=False, icon_str="desinstalar")
            self.btn_uninstall.clicked.connect(self.uninstall_action)
            btn_layout.addWidget(self.btn_uninstall)
        else:
            self.btn_install = mk_btn("Instalar", is_primary=False, icon_str="instalar")
            self.btn_install.clicked.connect(self.install_action)

            self.btn_delete = mk_btn("Eliminar", is_primary=False, icon_str="desinstalar")
            self.btn_delete.clicked.connect(self.delete_action)

            btn_layout.addWidget(self.btn_install)
            btn_layout.addWidget(self.btn_delete)

        content_layout.addLayout(btn_layout)

        # Boton de compilar (Solo para proyectos locales)
        if not self.is_app:
            content_layout.addSpacing(10)
            self.btn_compile = mk_btn("Compilar Proyecto", is_primary=True, icon_str="construir")
            self.btn_compile.setFixedHeight(40)
            self.btn_compile.clicked.connect(self.compile_action)
            content_layout.addWidget(self.btn_compile)

        self.lbl_status = QLabel("")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        content_layout.addWidget(self.lbl_status) # Add status label below buttons
        content_layout.addStretch()
        layout.addLayout(content_layout)

    def run_selected_script(self):
        item = self.scripts_list.currentItem()
        if not item:
            return
        script_path = item.data(QtCore.Qt.ItemDataRole.UserRole)

        python = find_python_executable()
        if not python:
             LeviathanDialog.launch(self, "Python no encontrado", "No se detectó una instalación de Python válida para ejecutar el script.", mode="error")
             return

        # Abrir terminal
        self.terminal = OutputTerminalDialog(script_path, python, self)
        self.terminal.exec()

    def install_action(self):
        # Logica de buscar .iflapp y descomprimir
        base_name = self.pkg.get("name", "")
        valid_file = None
        for f in os.listdir(BASE_DIR):
            if (f.endswith(".iflapp") or f.endswith(".iflappb")) and base_name in f:
                valid_file = os.path.join(BASE_DIR, f)
                break

        if not valid_file:
            LeviathanDialog.launch(
                self,
                "No encontrado",
                "No se encontró el paquete compilado (.iflapp) en la carpeta de proyectos. Primero compílalo.",
                mode="warning"
            )
            return

        target_dir = os.path.join(Fluthin_APPS, self.pkg['name'])
        try:
            os.makedirs(target_dir, exist_ok=True)
            with zipfile.ZipFile(valid_file, 'r') as zf:
                zf.extractall(target_dir)
            LeviathanDialog.launch(self, "Éxito", "App instalada correctamente.", mode="success")
            if hasattr(self.manager, "load_manager_lists"): self.manager.load_manager_lists()
        except Exception as e:
            LeviathanDialog.launch(self, "Error", str(e), mode="error")

    def uninstall_action(self):
         def do_uninstall(res):
             if res == "SÍ":
                 try:
                     shutil.rmtree(self.pkg["folder"])
                     self.accept()
                     if hasattr(self.manager, "load_manager_lists"): self.manager.load_manager_lists()
                 except Exception as e:
                     LeviathanDialog.launch(self, "Error", str(e), mode="error")

         LeviathanDialog.launch(self, "Desinstalar", "¿Estás seguro de eliminar esta app?", mode="warning", buttons=["SÍ", "NO"], callback=do_uninstall)

    def delete_action(self):
         def do_delete(res):
             if res == "SÍ":
                 try:
                     shutil.rmtree(self.pkg["folder"])
                     self.accept()
                     if hasattr(self.manager, "load_manager_lists"): self.manager.load_manager_lists()
                 except Exception as e:
                     LeviathanDialog.launch(self, "Error", str(e), mode="error")

         LeviathanDialog.launch(self, "Eliminar", "¿Estás seguro de eliminar este proyecto y todos sus archivos? Esta acción no se puede deshacer.", mode="error", buttons=["SÍ", "NO"], callback=do_delete)

    def compile_action(self):
        # Trigger compilation using BuildThread
        self.btn_compile.setEnabled(False)
        self.lbl_status.setText("Compilando...")

        # Extract metadata
        empresa = self.pkg.get('empresa', 'influent')
        nombre = self.pkg.get('app', self.pkg.get('name', 'unknown'))
        version = self.pkg.get('version', '1.0').replace("v", "").split("-")[0]
        plataforma = self.pkg.get('platform', 'Windows')

        self.build_thread = BuildThread(
            empresa,
            nombre,
            version,
            plataforma,
            parent=self,
            custom_path=self.pkg.get('folder'),
            base_dir=BASE_DIR,
            build_mode="portable"
        )
        self.build_thread.progress.connect(lambda msg: self.lbl_status.setText(msg))
        self.build_thread.finished.connect(self.on_compile_finished)
        self.build_thread.error.connect(self.on_compile_error)
        self.build_thread.start()

    def on_compile_finished(self, msg):
        self.lbl_status.setText(msg)
        self.btn_compile.setEnabled(True)
        LeviathanDialog.launch(self, "Compilación", msg, mode="info")

    def on_compile_error(self, msg):
        self.lbl_status.setText(f"Error: {msg}")
        self.btn_compile.setEnabled(True)
        LeviathanDialog.launch(self, "Error de compilación", msg, mode="error")