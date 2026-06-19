# -*- coding: utf-8 -*-
"""
Diálogo "Abrir con..." estilo lista plana de aplicaciones para PackageMaker.
Muestra editores disponibles incluyendo el editor integrado de PackageMaker.
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Callable

try:
    from PyQt6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
        QPushButton, QLabel, QWidget, QFrame, QScrollArea, QSizePolicy, QMessageBox
    )
    from PyQt6.QtCore import Qt, QSize
    from PyQt6.QtGui import QIcon, QPixmap, QFont
    PYQT6_AVAILABLE = True
except ImportError as e:
    print(f"[ERROR] No se pudo importar PyQt6: {e}")
    PYQT6_AVAILABLE = False
    raise

# Importar detector de editores y utilidades de i18n
try:
    from .editorDetector import EditorDetector, EditorInfo, get_available_editors, save_default_editor, get_default_editor
    from .i18n import tr
    from .iconManager import load_svg_icon
    from .projectConfig import get_project_config
except ImportError:
    from editorDetector import EditorDetector, EditorInfo, get_available_editors, save_default_editor, get_default_editor
    from i18n import tr
    try:
        from iconManager import load_svg_icon
    except ImportError:
        load_svg_icon = None
    try:
        from projectConfig import get_project_config
    except ImportError:
        get_project_config = None

import sys
import subprocess
import platform


def detect_executable_type(file_path: str) -> str:
    if not file_path or not os.path.exists(file_path):
        return 'unknown'
    
    # Detectar por extensión
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.exe':
        return 'exe'
    elif ext == '.app':
        return 'app'
    elif ext in ('.sh', '.bash', '.zsh', '.fish'):
        return 'script'
    elif ext in ('.py', '.py3'):
        return 'python'
    elif ext in ('.js', '.node'):
        return 'node'
    
    # Detectar ELF (Linux/Unix) por magic bytes
    try:
        with open(file_path, 'rb') as f:
            header = f.read(4)
            if header == b'\x7fELF':
                return 'elf'
    except:
        pass
    
    # Detectar Mach-O (Mac) por magic bytes
    try:
        with open(file_path, 'rb') as f:
            header = f.read(4)
            if header in (b'\xfe\xed\xfa\xce', b'\xfe\xed\xfa\xcf', b'\xce\xfa\xed\xfe', b'\xcf\xfa\xed\xfe'):
                return 'macho'
    except:
        pass
    
    # Detectar si es ejecutable por permisos (Linux/Mac sin extensión)
    if os.access(file_path, os.X_OK):
        return 'executable'
    
    return 'unknown'




def check_executable_exists(exe_path: str) -> bool:
    """
    Verifica si un ejecutable existe usando ping o verificación de archivo.
    
    Args:
        exe_path: Ruta del ejecutable a verificar
    
    Returns:
        True si el ejecutable existe y es accesible, False en caso contrario
    """
    if not exe_path:
        return False
    
    # Primero verificar si el archivo existe
    if os.path.exists(exe_path):
        return True
    
    # Si no existe, intentar verificar si es un comando del sistema usando shutil.which
    try:
        import shutil
        return shutil.which(exe_path) is not None
    except Exception as e:
        print(f"[ERROR] Error verificando ejecutable {exe_path}: {e}")
    
    return False


class PackageMakerEditor:
    """Editor integrado pmCodeEditor (siempre disponible)."""

    def __init__(self):
        self.name = "pmcodeeditor"
        self.display_name = "pmCodeEditor"
        self.icon_path = self._find_icon()
        self.exe_path = self._find_executable()
    
    def _find_icon(self) -> str:
        """Busca el icono del editor en la carpeta app/."""
        possible_paths = [
            Path(__file__).parent.parent / "app" / "pmCodeEditor-icon.ico",
            Path(__file__).parent.parent / "assets" / "pmCodeEditor-icon.ico",
            Path(__file__).parent.parent / "pmCodeEditor-icon.ico",
        ]
        for path in possible_paths:
            if path.exists():
                return str(path)
        return ""
    
    def _find_executable(self) -> str:
        """Busca el ejecutable del editor según la plataforma."""
        base_dir = Path(__file__).parent.parent
        
        if sys.platform.startswith("win"):
            # Buscar .exe en Windows
            possible_names = ["pmCodeEditor.exe", "PackageMaker.exe", "packagemaker.exe"]
            for name in possible_names:
                exe_path = base_dir / name
                if exe_path.exists():
                    return str(exe_path)
        else:
            # Linux/Mac: buscar .elf o sin extensión
            possible_names = ["pmCodeEditor.elf", "pmCodeEditor", "packagemaker", "PackageMaker"]
            for name in possible_names:
                exe_path = base_dir / name
                if exe_path.exists():
                    # Verificar que sea ejecutable
                    if os.access(exe_path, os.X_OK):
                        return str(exe_path)
        
        # Si no se encuentra ejecutable, devolver el script Python
        script_path = base_dir / "pmCodeEditor.py"
        if script_path.exists():
            return str(script_path)
        
        return ""


class EditorListItem(QWidget):
    """Item personalizado para mostrar un editor en la lista tipo Material Design."""
    
    def __init__(self, editor_info, exe_path: str, parent=None, is_default: bool = False):
        super().__init__(parent)
        self.editor_info = editor_info
        self.exe_path = exe_path
        self.is_default = is_default
        self._is_selected = False
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        # Icono del editor (tamaño estándar de Windows)
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(48, 48)
        self.icon_label.setStyleSheet("""
            background-color: transparent;
            border: none;
        """)
        
        # Cargar icono
        icon = self._load_icon()
        if icon:
            self.icon_label.setPixmap(icon.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            # Icono por defecto con letra inicial
            initial = self.editor_info.display_name[0].upper() if self.editor_info.display_name else "?"
            self.icon_label.setStyleSheet(f"""
                background: transparent;
                border-radius: 8px;
                color: white;
                font-weight: bold;
                font-size: 24px;
            """)
            self.icon_label.setText(initial)
            self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.icon_label)
        
        # Nombre del editor y descripción
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        # Nombre
        name_label = QLabel(self.editor_info.display_name)
        name_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        name_label.setStyleSheet("color: white;")
        text_layout.addWidget(name_label)
        
        # Indicador de predeterminado
        if self.is_default:
            default_label = QLabel(tr("Predeterminado"))
            default_label.setFont(QFont("Segoe UI", 10))
            default_label.setStyleSheet("color: #4CAF50;")
            text_layout.addWidget(default_label)
        
        layout.addLayout(text_layout, 1)
        
        # Estilo base del widget (Windows 11 / Fluent Design)
        self.setStyleSheet("""
            EditorListItem {
                background-color: #2d2d2d;
                border-radius: 8px;
                border-left: 4px solid transparent;
                color: white;
            }
            EditorListItem:hover {
                background-color: #3a3a3a;
                border-left: 4px solid rgba(0, 120, 212, 0.5);
            }
            EditorListItem:pressed {
                background-color: #252525;
                border-left: 4px solid rgba(0, 120, 212, 0.7);
            }
            EditorListItem[selected="true"] {
                background-color: #404040;
                border-left: 4px solid #0078d4;
            }
            EditorListItem[selected="true"]:hover {
                background-color: #4a4a4a;
                border-left: 4px solid #0078d4;
            }
            EditorListItem[selected="true"]:pressed {
                background-color: #353535;
                border-left: 4px solid #0078d4;
            }
            QLabel {
                color: white;
            }
        """)
    
    def _load_icon(self) -> Optional[QPixmap]:
        """Carga el icono del editor usando IconManager o métodos alternativos."""
        if getattr(self.editor_info, "name", "") == "pmcodeeditor":
            try:
                from lib.app_icons import svg_to_pixmap, ICONS_SVG
                return svg_to_pixmap(ICONS_SVG["pmcodeeditor"], 48)
            except ImportError:
                pass
        
        # Intentar usar IconManager para icono por defecto
        if load_svg_icon:
            default_icon = load_svg_icon("app", 48)
            if default_icon:
                return default_icon
        
        if hasattr(self.editor_info, 'icon_path') and self.editor_info.icon_path and os.path.exists(self.editor_info.icon_path):
            try:
                return QPixmap(self.editor_info.icon_path)
            except:
                pass
        
        # Usar QFileIconProvider para obtener el icono del sistema operativo
        if self.exe_path and os.path.exists(self.exe_path):
            try:
                from PyQt6.QtWidgets import QFileIconProvider
                from PyQt6.QtCore import QFileInfo
                
                provider = QFileIconProvider()
                icon = provider.icon(QFileInfo(self.exe_path))
                if not icon.isNull():
                    return icon.pixmap(48, 48)
            except Exception as e:
                print(f"[DEBUG] Error cargando icono para {self.exe_path}: {e}")
        
        return None
    
    def set_selected(self, selected: bool):
        """Actualiza el estado visual de selección usando propiedades dinámicas QSS."""
        self._is_selected = selected
        # Forzar actualización del estilo
        self.setProperty("selected", "true" if selected else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
        # Forzar repintado inmediato
        self.repaint()


class OpenWithDialog(QDialog):
    """
    Diálogo estilo "Abrir con..." de Windows 11.
    Muestra editores disponibles con opciones "Solo una vez" y "Siempre".
    """
    
    def __init__(self, parent=None, project_path: str = "", project_name: str = ""):
        super().__init__(parent)
        self.project_path = project_path
        self.project_name = project_name
        self.selected_editor: Optional[Tuple[EditorInfo, str]] = None
        self.result_action: str = ""  # "once" o "always"
        self.editors: List[Tuple[EditorInfo, str]] = []
        self.use_native_dialog = False  # Opción para usar diálogo nativo
        self.project_config = get_project_config() if get_project_config else None
        
        self._setup_ui()
        self._detect_editors()
        self._check_project_config()
    
    def _setup_ui(self):
        """Configura la interfaz del diálogo estilo Windows 11 / Fluent Design."""
        self.setWindowTitle(tr("Abrir con..."))
        self.setFixedSize(540, 580)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Contenedor central con estilo Windows 11
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #1f1f1f;
                border: none;
                border-radius: 8px;
            }
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Header (sin bordes, texto plano sobre fondo)
        header_container = QFrame()
        header_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(28, 28, 28, 20)
        header_layout.setSpacing(6)
        
        title = QLabel(tr("Abrir con..."))
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.DemiBold))
        title.setStyleSheet("color: white;")
        header_layout.addWidget(title)
        
        # Subtítulo con nombre del proyecto
        if self.project_name:
            subtitle = QLabel(f'{tr("Proyecto")}: "{self.project_name}"')
            subtitle.setFont(QFont("Segoe UI", 12))
            subtitle.setStyleSheet("color: #757575;")
            header_layout.addWidget(subtitle)
        
        # Detectar y mostrar tipo de ejecutable si hay project_path
        if self.project_path:
            exe_type = detect_executable_type(self.project_path)
            if exe_type != 'unknown':
                type_label = QLabel(f'{tr("Tipo")}: {exe_type.upper()}')
                type_label.setFont(QFont("Segoe UI", 10))
                type_label.setStyleSheet("color: #757575;")
                header_layout.addWidget(type_label)
        
        container_layout.addWidget(header_container)
        
        # Scroll area para la lista de editores (estilo lista plana)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #333333;
                width: 12px;
                margin: 12px 0 12px 0;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #00aaff;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #0088cc;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
                border: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # Widget contenedor de la lista
        list_container = QWidget()
        self.list_layout = QVBoxLayout(list_container)
        self.list_layout.setContentsMargins(20, 20, 20, 20)
        self.list_layout.setSpacing(8)
        self.list_layout.addStretch()
        
        scroll.setWidget(list_container)
        container_layout.addWidget(scroll, 1)
        
        # Indicador de carga
        self.loading_label = QLabel(tr("Buscando editores..."))
        self.loading_label.setFont(QFont("Segoe UI", 10))
        self.loading_label.setStyleSheet("color: rgba(255, 255, 255, 0.5); font-style: italic;")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.loading_label)
        
        # Separador antes de botones
        btn_separator = QFrame()
        btn_separator.setFrameShape(QFrame.Shape.HLine)
        btn_separator.setStyleSheet("background-color: rgba(255, 255, 255, 0.08);")
        btn_separator.setFixedHeight(1)
        container_layout.addWidget(btn_separator)
        
        # Botones de acción (Windows 11 / Fluent Design)
        buttons_container = QFrame()
        buttons_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border-top: 1px solid #333;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }
        """)
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(20, 20, 20, 20)
        buttons_layout.setSpacing(8)
        
        buttons_layout.addStretch()
        
        # Botón para editar proyecto (solo si existe configuración)
        self.btn_edit_project = QPushButton(tr("Editar"))
        self.btn_edit_project.setFixedHeight(36)
        self.btn_edit_project.setFont(QFont("Segoe UI", 10))
        self.btn_edit_project.setMinimumWidth(80)
        self.btn_edit_project.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #0064b8;
            }
        """)
        self.btn_edit_project.clicked.connect(self._on_edit_project)
        self.btn_edit_project.setVisible(False)  # Oculto por defecto
        buttons_layout.addWidget(self.btn_edit_project)
        
        # Botón Cancelar
        self.btn_cancel = QPushButton(tr("Cancelar"))
        self.btn_cancel.setFixedHeight(36)
        self.btn_cancel.setFont(QFont("Segoe UI", 10))
        self.btn_cancel.setMinimumWidth(80)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QPushButton:pressed {
                background-color: #1d1d1d;
            }
        """)
        self.btn_cancel.clicked.connect(self.reject)
        buttons_layout.addWidget(self.btn_cancel)
        
        # Botón "Solo una vez"
        self.btn_once = QPushButton(tr("Solo una vez"))
        self.btn_once.setFixedHeight(36)
        self.btn_once.setFont(QFont("Segoe UI", 10))
        self.btn_once.setMinimumWidth(100)
        self.btn_once.setEnabled(False)
        self.btn_once.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QPushButton:pressed {
                background-color: #1d1d1d;
            }
            QPushButton:disabled {
                color: rgba(255, 255, 255, 0.3);
                background-color: #1d1d1d;
            }
        """)
        self.btn_once.clicked.connect(lambda: self._on_accept("once"))
        buttons_layout.addWidget(self.btn_once)
        
        # Botón "Siempre" (primario - acento Windows 11)
        self.btn_always = QPushButton(tr("Siempre"))
        self.btn_always.setFixedHeight(36)
        self.btn_always.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        self.btn_always.setMinimumWidth(100)
        self.btn_always.setEnabled(False)
        self.btn_always.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #0064b8;
            }
            QPushButton:disabled {
                background-color: rgba(0, 120, 212, 0.3);
                color: rgba(255, 255, 255, 0.5);
            }
        """)
        self.btn_always.clicked.connect(lambda: self._on_accept("always"))
        buttons_layout.addWidget(self.btn_always)
        
        container_layout.addWidget(buttons_container)
        
        main_layout.addWidget(container)
        
        # Estilo del diálogo
        self.setStyleSheet("""
            QDialog {
                background-color: transparent;
            }
        """)
        
        # Almacenar widgets de items para manejar selección
        self._editor_items = []
        self._selected_item = None
    
    def _detect_editors(self):
        """Detecta los editores disponibles incluyendo el editor de PackageMaker."""
        detector = EditorDetector()
        self.editors = []
        
        pm_editor = PackageMakerEditor()
        pm_info = EditorInfo(
            name=pm_editor.name,
            display_name=pm_editor.display_name,
            executable=pm_editor.exe_path,
            icon_path=pm_editor.icon_path,
            priority=200,
        )
        self.editors.append((pm_info, pm_editor.exe_path))
        
        # Luego detectar editores externos
        external_editors = detector.detect_editors()
        self.editors.extend(external_editors)
        
        # Limpiar lista actual
        while self.list_layout.count() > 1:  # Dejar el stretch al final
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._editor_items.clear()
        
        if not self.editors:
            self.loading_label.setText(tr("No se encontraron editores de código."))
            self.loading_label.setStyleSheet("color: #ff6b6b;")
            return
        
        self.loading_label.hide()
        
        # Obtener editor predeterminado
        default_editor = get_default_editor()
        
        # Crear items para cada editor
        for i, (editor_info, exe_path) in enumerate(self.editors):
            is_default = default_editor and editor_info.name == default_editor
            
            # Crear widget de item
            item_widget = EditorListItem(editor_info, exe_path, is_default=is_default)
            item_widget.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # Estilo del item contenedor (tarjeta Material Design)
            item_container = QFrame()
            item_container.setStyleSheet(f"""
                QFrame {{
                    background-color: transparent;
                    border: none;
                    border-radius: 8px;
                }}
            """)
            
            item_layout = QVBoxLayout(item_container)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(0)
            item_layout.addWidget(item_widget)
            
            # Guardar referencias
            item_data = {
                'container': item_container,
                'widget': item_widget,
                'editor_info': editor_info,
                'exe_path': exe_path,
                'index': i
            }
            self._editor_items.append(item_data)
            
            # Conectar eventos de clic usando event filter
            from PyQt6.QtCore import QEvent, QObject
            
            click_filter = QObject(self)
            click_filter.index = i
            click_filter.callback = self._on_editor_clicked
            
            def filter_event(obj, event):
                if event.type() == QEvent.Type.MouseButtonPress:
                    click_filter.callback(click_filter.index)
                    return True
                return False
            
            click_filter.eventFilter = filter_event
            item_container.installEventFilter(click_filter)
            item_widget.installEventFilter(click_filter)
            
            # Insertar antes del stretch
            self.list_layout.insertWidget(self.list_layout.count() - 1, item_container)
        
        # Seleccionar el primero o el predeterminado
        default_idx = 0
        for i, item_data in enumerate(self._editor_items):
            if default_editor and item_data['editor_info'].name == default_editor:
                default_idx = i
                break
        
        self._on_editor_clicked(default_idx)
    
    def _on_editor_clicked(self, index: int):
        """Maneja la selección de un editor."""
        # Desmarcar el anterior
        if self._selected_item is not None:
            prev_data = self._editor_items[self._selected_item]
            prev_data['widget'].set_selected(False)
        
        # Marcar el nuevo
        self._selected_item = index
        item_data = self._editor_items[index]
        item_data['widget'].set_selected(True)
        
        # Actualizar selección
        self.selected_editor = (item_data['editor_info'], item_data['exe_path'])
        self.btn_once.setEnabled(True)
        self.btn_always.setEnabled(True)
    
    def _on_editor_double_clicked(self, index: int):
        """Callback para doble clic - abrir con 'Solo una vez'."""
        self._on_editor_clicked(index)
        self._on_accept("once")
    
    def _check_project_config(self):
        """Verifica si existe configuración para el proyecto y muestra el botón de editar."""
        if not self.project_config or not self.project_path:
            return
        
        try:
            # Verificar si existe configuración para este proyecto
            editor_name = self.project_config.get_project_editor(self.project_path)
            if editor_name:
                # Verificar si el ejecutable existe
                exe_path = self.project_config.get_editor_path(editor_name)
                if exe_path and check_executable_exists(exe_path):
                    # Mostrar botón de editar
                    self.btn_edit_project.setVisible(True)
                    self.btn_edit_project.setText(f"{tr('Editar')} ({editor_name})")
        except Exception as e:
            print(f"[ERROR] Error verificando configuración del proyecto: {e}")
    
    def _on_edit_project(self):
        """Edita el proyecto con el editor configurado."""
        if not self.project_config or not self.project_path:
            return
        
        try:
            # Obtener el editor configurado
            editor_name = self.project_config.get_project_editor(self.project_path)
            if not editor_name:
                QMessageBox.warning(
                    self,
                    tr("Error"),
                    tr("No hay configuración de editor para este proyecto.")
                )
                return
            
            # Obtener la ruta del ejecutable
            exe_path = self.project_config.get_editor_path(editor_name)
            if not exe_path:
                QMessageBox.warning(
                    self,
                    tr("Error"),
                    tr("No hay ruta de ejecutable configurada para este editor.")
                )
                return
            
            # Verificar si el ejecutable existe
            if not check_executable_exists(exe_path):
                QMessageBox.warning(
                    self,
                    tr("Error"),
                    tr("El ejecutable del editor no existe. Se abrirá el diálogo 'Abrir con' para seleccionar otro editor.")
                )
                # No cerrar el diálogo, permitir al usuario seleccionar otro editor
                return
            
            # Abrir el proyecto con el editor
            subprocess.Popen([exe_path, self.project_path])
            
            self.accept()
        
        except Exception as e:
            QMessageBox.warning(
                self,
                tr("Error"),
                tr(f"Error al abrir el proyecto: {e}")
            )
    
    def _on_accept(self, action: str):
        """Acepta el diálogo con la acción especificada."""
        self.result_action = action
        
        if action == "always" and self.selected_editor:
            # Guardar como predeterminado
            editor_info, exe_path = self.selected_editor
            save_default_editor(editor_info.name)
            
            # Guardar en configuración JSON del proyecto
            if self.project_config and self.project_path:
                self.project_config.set_project_editor(self.project_path, editor_info.name)
                self.project_config.set_editor_path(editor_info.name, exe_path)
        
        self.accept()
    
    def keyPressEvent(self, event):
        """Maneja navegación por teclado."""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self._selected_item is not None and self.btn_once.isEnabled():
                self._on_accept("once")
        elif event.key() == Qt.Key.Key_Up:
            if self._selected_item is not None and self._selected_item > 0:
                self._on_editor_clicked(self._selected_item - 1)
        elif event.key() == Qt.Key.Key_Down:
            if self._selected_item is not None and self._selected_item < len(self._editor_items) - 1:
                self._on_editor_clicked(self._selected_item + 1)
        else:
            super().keyPressEvent(event)
    
    def get_result(self) -> Tuple[Optional[Tuple[EditorInfo, str]], str]:
        """Retorna el resultado del diálogo."""
        return self.selected_editor, self.result_action


def show_open_with_dialog(parent=None, project_path: str = "", project_name: str = "") -> Tuple[Optional[Tuple[EditorInfo, str]], str]:
    """
    Muestra el diálogo "Abrir con..." y retorna el resultado.
    
    Returns:
        Tupla de ((EditorInfo, exe_path) o None, action)
        action puede ser "once" o "always"
    """
    dialog = OpenWithDialog(parent, project_path, project_name)
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_result()
    
    return None, ""


# Función de conveniencia para abrir proyecto directamente
def open_project_with_editor(parent=None, project_path: str = "", project_name: str = "", 
                             use_default: bool = True) -> bool:
    """
    Abre un proyecto con un editor.
    Si use_default es True y hay un editor predeterminado, lo usa directamente.
    Si no, muestra el diálogo de selección.
    
    Returns:
        True si se abrió correctamente, False en caso contrario
    """
    if not os.path.exists(project_path):
        print(f"[ERROR] El proyecto no existe: {project_path}")
        return False
    
    detector = EditorDetector()
    
    # Construir lista completa incluyendo editor de PackageMaker
    pm_editor = PackageMakerEditor()
    all_editors = []
    if pm_editor.exe_path:
        pm_info = EditorInfo(
            name=pm_editor.name,
            display_name=pm_editor.display_name,
            executable=pm_editor.exe_path,
            icon_path=pm_editor.icon_path
        )
        all_editors.append((pm_info, pm_editor.exe_path))
    all_editors.extend(detector.detect_editors())
    
    # Intentar usar editor predeterminado
    if use_default:
        default_name = get_default_editor()
        if default_name:
            for editor_info, exe_path in all_editors:
                if editor_info.name == default_name:
                    # Si es el editor de PackageMaker, usar método especial
                    if editor_info.name == "pmcodeeditor":
                        return _launch_pm_editor(exe_path, project_path)
                    return detector.launch_editor(editor_info, exe_path, project_path)
    
    # Mostrar diálogo
    selected, action = show_open_with_dialog(parent, project_path, project_name)
    
    if selected and action:
        editor_info, exe_path = selected
        # Si es el editor de PackageMaker, usar método especial
        if editor_info.name == "pmcodeeditor":
            return _launch_pm_editor(exe_path, project_path)
        return detector.launch_editor(editor_info, exe_path, project_path)
    
    return False


def _launch_pm_editor(exe_path: str, project_path: str) -> bool:
    """Lanza el editor de PackageMaker con el proyecto especificado."""
    import subprocess
    try:
        # Si es un script Python, lanzar con python
        if exe_path.endswith('.py'):
            python_exe = sys.executable
            creationflags = getattr(subprocess, 'CREATE_NEW_CONSOLE', 0)
            subprocess.Popen([python_exe, exe_path, project_path], creationflags=creationflags)
        else:
            # Es un ejecutable
            creationflags = getattr(subprocess, 'CREATE_NEW_CONSOLE', 0)
            subprocess.Popen([exe_path, project_path], creationflags=creationflags)
        return True
    except Exception as e:
        print(f"[ERROR] No se pudo lanzar el editor de PackageMaker: {e}")
        return False


if __name__ == "__main__":
    # Test
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Simular proyecto
    test_path = os.path.expanduser("~/Documents/test_project")
    os.makedirs(test_path, exist_ok=True)
    
    result = show_open_with_dialog(None, test_path, "Test Project")
    
    if result[0]:
        editor, exe = result[0]
        print(f"Seleccionado: {editor.display_name}")
        print(f"Ejecutable: {exe}")
        print(f"Acción: {result[1]}")
    else:
        print("Cancelado")
    
    sys.exit(0)
