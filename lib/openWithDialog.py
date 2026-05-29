# -*- coding: utf-8 -*-
"""
Diálogo "Abrir con..." estilo lista plana de aplicaciones para PackageMaker.
Muestra editores disponibles incluyendo el editor integrado de PackageMaker.
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Callable

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QWidget, QFrame, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap, QFont

# Importar detector de editores y utilidades de i18n
try:
    from .editorDetector import EditorDetector, EditorInfo, get_available_editors, save_default_editor, get_default_editor
    from .i18n import tr
except ImportError:
    from editorDetector import EditorDetector, EditorInfo, get_available_editors, save_default_editor, get_default_editor
    from i18n import tr


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
    """Item personalizado para mostrar un editor en la lista tipo Windows 11."""
    
    def __init__(self, editor_info, exe_path: str, parent=None, is_default: bool = False):
        super().__init__(parent)
        self.editor_info = editor_info
        self.exe_path = exe_path
        self.is_default = is_default
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)
        
        # Icono del editor (tamaño más grande para mejor visibilidad)
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(40, 40)
        self.icon_label.setStyleSheet("""
            background-color: transparent;
            border: none;
        """)
        
        # Cargar icono
        icon = self._load_icon()
        if icon:
            self.icon_label.setPixmap(icon.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            # Icono por defecto con letra inicial
            initial = self.editor_info.display_name[0].upper() if self.editor_info.display_name else "?"
            self.icon_label.setStyleSheet(f"""
                background: transparent;
                border-radius: 8px;
                color: white;
                font-weight: bold;
                font-size: 18px;
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
        
        # Radio button visual (círculo de selección)
        self.radio = QLabel("○")
        self.radio.setFont(QFont("Segoe UI", 16))
        self.radio.setStyleSheet("color: rgba(255, 255, 255, 0.5);")
        self.radio.setFixedWidth(24)
        layout.addWidget(self.radio)
    
    def _load_icon(self) -> Optional[QPixmap]:
        """Carga el icono del editor usando QFileIconProvider o icon_path."""
        if getattr(self.editor_info, "name", "") == "pmcodeeditor":
            try:
                from lib.app_icons import svg_to_pixmap, ICONS_SVG
                return svg_to_pixmap(ICONS_SVG["pmcodeeditor"], 40)
            except ImportError:
                pass
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
                    return icon.pixmap(40, 40)
            except Exception as e:
                print(f"[DEBUG] Error cargando icono para {self.exe_path}: {e}")
        
        return None
    
    def set_selected(self, selected: bool):
        """Actualiza el estado visual de selección."""
        if selected:
            self.radio.setText("●")
            self.radio.setStyleSheet("color: #0078d4;")
        else:
            self.radio.setText("○")
            self.radio.setStyleSheet("color: rgba(255, 255, 255, 0.5);")


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
        
        self._setup_ui()
        self._detect_editors()
    
    def _setup_ui(self):
        """Configura la interfaz del diálogo estilo lista plana de apps."""
        self.setWindowTitle(tr("Abrir con..."))
        self.setFixedSize(420, 520)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Contenedor central con estilo acrílico
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #252526;
                border: none;
                border-radius: 8px;
            }
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Header con fondo sutil
        header_container = QFrame()
        header_container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.02);
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
        """)
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(20, 20, 20, 16)
        header_layout.setSpacing(4)
        
        title = QLabel(tr("Abrir con..."))
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        header_layout.addWidget(title)
        
        # Subtítulo con nombre del proyecto
        if self.project_name:
            subtitle = QLabel(f'{tr("Proyecto")}: "{self.project_name}"')
            subtitle.setFont(QFont("Segoe UI", 11))
            subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.5);")
            header_layout.addWidget(subtitle)
        
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
                background-color: transparent;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        
        # Widget contenedor de la lista
        list_container = QWidget()
        self.list_layout = QVBoxLayout(list_container)
        self.list_layout.setContentsMargins(8, 8, 8, 8)
        self.list_layout.setSpacing(2)
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
        
        # Botones de acción (estilo Windows 11 moderno)
        buttons_container = QFrame()
        buttons_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }
        """)
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(16, 16, 16, 16)
        buttons_layout.setSpacing(8)
        
        # Botón Cancelar
        self.btn_cancel = QPushButton(tr("Cancelar"))
        self.btn_cancel.setFixedHeight(32)
        self.btn_cancel.setFont(QFont("Segoe UI", 9))
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 4px;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.05);
                border-color: rgba(255, 255, 255, 0.25);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        self.btn_cancel.clicked.connect(self.reject)
        buttons_layout.addWidget(self.btn_cancel)
        
        buttons_layout.addStretch()
        
        # Botón "Solo una vez"
        self.btn_once = QPushButton(tr("Solo una vez"))
        self.btn_once.setFixedHeight(32)
        self.btn_once.setFont(QFont("Segoe UI", 9))
        self.btn_once.setEnabled(False)
        self.btn_once.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 4px;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.05);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QPushButton:disabled {
                color: rgba(255, 255, 255, 0.3);
                border-color: rgba(255, 255, 255, 0.08);
            }
        """)
        self.btn_once.clicked.connect(lambda: self._on_accept("once"))
        buttons_layout.addWidget(self.btn_once)
        
        # Botón "Siempre" (primario)
        self.btn_always = QPushButton(tr("Siempre"))
        self.btn_always.setFixedHeight(32)
        self.btn_always.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        self.btn_always.setEnabled(False)
        self.btn_always.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #006cbd;
            }
            QPushButton:pressed {
                background-color: #005a9e;
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
            
            # Estilo del item contenedor
            item_container = QFrame()
            is_pm = editor_info.name == "pmcodeeditor"
            idle_border = "rgba(0, 120, 212, 0.45)" if is_pm else "transparent"
            item_container.setStyleSheet(f"""
                QFrame {{
                    background-color: {"rgba(255, 87, 34, 0.06)" if is_pm else "transparent"};
                    border: 1px solid {idle_border};
                    border-radius: 4px;
                }}
                QFrame:hover {{
                    background-color: rgba(255, 255, 255, 0.04);
                    border-color: rgba(0, 120, 212, 0.35);
                }}
            """)
            
            item_layout = QVBoxLayout(item_container)
            item_layout.setContentsMargins(4, 2, 4, 2)
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
            
            # Conectar eventos de clic
            item_container.mousePressEvent = lambda e, idx=i: self._on_editor_clicked(idx)
            item_widget.mousePressEvent = lambda e, idx=i: self._on_editor_clicked(idx)
            
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
            prev_data['container'].setStyleSheet("""
                QFrame {
                    background-color: transparent;
                    border: 1px solid transparent;
                    border-radius: 4px;
                }
                QFrame:hover {
                    background-color: rgba(255, 255, 255, 0.04);
                    border-color: rgba(255, 255, 255, 0.08);
                }
            """)
        
        # Marcar el nuevo
        self._selected_item = index
        item_data = self._editor_items[index]
        item_data['widget'].set_selected(True)
        is_pm = item_data["editor_info"].name == "pmcodeeditor"
        item_data["container"].setStyleSheet(f"""
            QFrame {{
                background-color: {"rgba(255, 87, 34, 0.12)" if is_pm else "rgba(0, 120, 212, 0.15)"};
                border: 1px solid {"rgba(255, 87, 34, 0.55)" if is_pm else "rgba(0, 120, 212, 0.45)"};
                border-radius: 4px;
            }}
        """)
        
        # Actualizar selección
        self.selected_editor = (item_data['editor_info'], item_data['exe_path'])
        self.btn_once.setEnabled(True)
        self.btn_always.setEnabled(True)
    
    def _on_editor_double_clicked(self, index: int):
        """Callback para doble clic - abrir con 'Solo una vez'."""
        self._on_editor_clicked(index)
        self._on_accept("once")
    
    def _on_accept(self, action: str):
        """Acepta el diálogo con la acción especificada."""
        self.result_action = action
        
        if action == "always" and self.selected_editor:
            # Guardar como predeterminado
            editor_info, _ = self.selected_editor
            save_default_editor(editor_info.name)
        
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
            subprocess.Popen([python_exe, exe_path, project_path], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0)
        else:
            # Es un ejecutable
            subprocess.Popen([exe_path, project_path],
                           creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0)
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
