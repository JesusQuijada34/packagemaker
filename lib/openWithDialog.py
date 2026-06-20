# -*- coding: utf-8 -*-
"""
Diálogo "Abrir con..." estilo Windows 11 / UWP para PackageMaker.
Proporciona una interfaz de selección de aplicaciones con tarjetas interactivas e indicadores estables.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional, Callable

try:
    from PyQt6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
        QWidget, QFrame, QScrollArea, QSizePolicy, QMessageBox,
        QApplication
    )
    from PyQt6.QtCore import Qt, QSize, pyqtSignal, QEvent, QPoint, QPropertyAnimation, QEasingCurve
    from PyQt6.QtGui import QIcon, QPixmap, QFont, QColor, QPainter, QBrush, QPen
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    # Mock classes for TUI compatibility
    class QFrame:
        def __init__(self, *args, **kwargs): pass
    class QDialog:
        def __init__(self, *args, **kwargs): pass
    class pyqtSignal:
        def __init__(self, *args, **kwargs): pass
        def emit(self, *args, **kwargs): pass
    class Qt:
        class CursorShape: PointingHandCursor = 0
        class AspectRatioMode: KeepAspectRatio = 0
        class TransformationMode: SmoothTransformation = 0
        class AlignmentFlag: AlignCenter = 0
        class WidgetAttribute: WA_TranslucentBackground = 0; WA_TransparentForMouseEvents = 0
        class WindowType: Dialog = 0; FramelessWindowHint = 0
        class MouseButton: LeftButton = 0
        class Shape: NoFrame = 0

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


def detect_executable_type(file_path: str) -> str:
    if not file_path or not os.path.exists(file_path):
        return 'unknown'
    
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.exe': return 'exe'
    elif ext == '.app': return 'app'
    elif ext in ('.sh', '.bash', '.zsh', '.fish'): return 'script'
    elif ext in ('.py', '.py3'): return 'python'
    elif ext in ('.js', '.node'): return 'node'
    
    try:
        with open(file_path, 'rb') as f:
            header = f.read(4)
            if header == b'\x7fELF': return 'elf'
    except: pass
    
    if os.access(file_path, os.X_OK): return 'executable'
    return 'unknown'


def check_executable_exists(exe_path: str) -> bool:
    if not exe_path: return False
    if os.path.exists(exe_path): return True
    try:
        import shutil
        return shutil.which(exe_path) is not None
    except: return False


class PackageMakerEditor:
    """Editor integrado pmCodeEditor."""
    def __init__(self):
        self.name = "pmcodeeditor"
        self.display_name = "pmCodeEditor"
        self.icon_path = self._find_icon()
        self.exe_path = self._find_executable()
    
    def _find_icon(self) -> str:
        base = Path(__file__).parent.parent
        for p in ["app/pmCodeEditor-icon.ico", "assets/pmCodeEditor-icon.ico", "pmCodeEditor-icon.ico"]:
            path = base / p
            if path.exists(): return str(path)
        return ""
    
    def _find_executable(self) -> str:
        base_dir = Path(__file__).parent.parent
        if sys.platform.startswith("win"):
            for name in ["pmCodeEditor.exe", "PackageMaker.exe", "packagemaker.exe"]:
                exe_path = base_dir / name
                if exe_path.exists(): return str(exe_path)
        else:
            for name in ["pmCodeEditor.elf", "pmCodeEditor", "packagemaker", "PackageMaker"]:
                exe_path = base_dir / name
                if exe_path.exists() and os.access(exe_path, os.X_OK): return str(exe_path)
        
        script_path = base_dir / "pmCodeEditor.py"
        return str(script_path) if script_path.exists() else ""


class EditorCard(QFrame):
    """Tarjeta interactiva estilo UWP para un editor."""
    clicked = pyqtSignal(int)
    doubleClicked = pyqtSignal(int)

    def __init__(self, index: int, editor_info, exe_path: str, is_default: bool = False, parent=None):
        super().__init__(parent)
        self.index = index
        self.editor_info = editor_info
        self.exe_path = exe_path
        self.is_default = is_default
        self._is_selected = False
        self._is_hovered = False
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(72)
        self.setMinimumWidth(400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 16, 0)
        layout.setSpacing(12)

        # Indicador de selección (Barra naranja estable)
        self.indicator = QFrame()
        self.indicator.setFixedWidth(4)
        self.indicator.setFixedHeight(32)
        self.indicator.setStyleSheet("background-color: #FF6B00; border-radius: 2px;")
        self.indicator.setVisible(False)
        
        # Contenedor para centrar el indicador verticalmente
        indicator_container = QVBoxLayout()
        indicator_container.setContentsMargins(0, 0, 0, 0)
        indicator_container.addStretch()
        indicator_container.addWidget(self.indicator)
        indicator_container.addStretch()
        layout.addLayout(indicator_container)

        # Icono
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(40, 40)
        pixmap = self._load_icon()
        if pixmap:
            self.icon_label.setPixmap(pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            initial = self.editor_info.display_name[0].upper() if self.editor_info.display_name else "?"
            self.icon_label.setText(initial)
            self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.icon_label.setStyleSheet("color: white; font-weight: bold; font-size: 18px; background: #333; border-radius: 4px;")
        layout.addWidget(self.icon_label)

        # Textos
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.setContentsMargins(0, 12, 0, 12)
        
        self.name_label = QLabel(self.editor_info.display_name)
        self.name_label.setFont(QFont("Segoe UI Variable Display", 11, QFont.Weight.Medium))
        self.name_label.setStyleSheet("color: #FFFFFF; background: transparent;")
        text_layout.addWidget(self.name_label)

        if self.is_default:
            self.status_label = QLabel(tr("Predeterminado"))
            self.status_label.setFont(QFont("Segoe UI Variable Small", 9))
            self.status_label.setStyleSheet("color: #A0A0A0; background: transparent;")
            text_layout.addWidget(self.status_label)
        
        layout.addLayout(text_layout, 1)
        self._update_style()

    def _load_icon(self) -> Optional['QPixmap']:
        if getattr(self.editor_info, "name", "") == "pmcodeeditor":
            try:
                from lib.app_icons import svg_to_pixmap, ICONS_SVG
                return svg_to_pixmap(ICONS_SVG["pmcodeeditor"], 40)
            except: pass
        
        if load_svg_icon:
            icon = load_svg_icon("app", 40)
            if icon: return icon

        if hasattr(self.editor_info, 'icon_path') and self.editor_info.icon_path and os.path.exists(self.editor_info.icon_path):
            return QPixmap(self.editor_info.icon_path)

        if self.exe_path and os.path.exists(self.exe_path):
            try:
                from PyQt6.QtWidgets import QFileIconProvider
                from PyQt6.QtCore import QFileInfo
                provider = QFileIconProvider()
                icon = provider.icon(QFileInfo(self.exe_path))
                if not icon.isNull(): return icon.pixmap(40, 40)
            except: pass
        return None

    def _update_style(self):
        bg_color = "transparent"
        if self._is_selected:
            bg_color = "rgba(255, 255, 255, 0.08)"
            self.indicator.setVisible(True)
        elif self._is_hovered:
            bg_color = "rgba(255, 255, 255, 0.05)"
            self.indicator.setVisible(False)
        else:
            self.indicator.setVisible(False)

        self.setStyleSheet(f"""
            EditorCard {{
                background-color: {bg_color};
                border-radius: 4px;
                border: none;
            }}
        """)

    def set_selected(self, selected: bool):
        self._is_selected = selected
        self._update_style()

    def enterEvent(self, event):
        self._is_hovered = True
        self._update_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._is_hovered = False
        self._update_style()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.index)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.doubleClicked.emit(self.index)
        super().mouseDoubleClickEvent(event)


class OpenWithDialog(QDialog):
    def __init__(self, parent=None, project_path: str = "", project_name: str = ""):
        super().__init__(parent)
        self.project_path = project_path
        self.project_name = project_name
        self.selected_editor: Optional[Tuple[EditorInfo, str]] = None
        self.result_action: str = ""
        self.cards: List[EditorCard] = []
        self._selected_index = -1
        
        self.project_config = get_project_config() if get_project_config else None
        
        self._setup_ui()
        self._detect_editors()
        self._check_project_config()

    def _setup_ui(self):
        self.setWindowTitle(tr("Abrir con..."))
        self.setFixedSize(520, 600)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Contenedor Principal (Sombra y Fondo)
        self.main_frame = QFrame(self)
        self.main_frame.setGeometry(10, 10, 500, 580)
        self.main_frame.setStyleSheet("""
            QFrame {
                background-color: #1C1C1C;
                border: 1px solid #333333;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(self.main_frame)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(0)

        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        
        title = QLabel(tr("Abrir con..."))
        title.setFont(QFont("Segoe UI Variable Display", 20, QFont.Weight.DemiBold))
        title.setStyleSheet("color: white; border: none;")
        header_layout.addWidget(title)

        if self.project_name:
            subtitle = QLabel(f'{tr("Proyecto")}: "{self.project_name}"')
            subtitle.setFont(QFont("Segoe UI Variable Text", 10))
            subtitle.setStyleSheet("color: #A0A0A0; border: none;")
            header_layout.addWidget(subtitle)
        
        layout.addLayout(header_layout)
        layout.addSpacing(24)

        # Scroll Area para la lista
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent; border: none;")
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.list_layout.setContentsMargins(0, 0, 8, 0)
        self.list_layout.setSpacing(4)
        self.list_layout.addStretch()
        
        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll)
        
        layout.addSpacing(24)

        # Botón Editar Proyecto (si ya tiene editor configurado)
        self.btn_edit_project = QPushButton()
        self.btn_edit_project.setVisible(False)
        self.btn_edit_project.setFixedHeight(36)
        self.btn_edit_project.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_edit_project.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #0078D4;
                border: none;
                text-align: left;
                font-size: 10pt;
            }
            QPushButton:hover { text-decoration: underline; }
        """)
        self.btn_edit_project.clicked.connect(self._on_edit_project)
        layout.addWidget(self.btn_edit_project)
        layout.addSpacing(12)

        # Botones de Acción
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)
        
        self.btn_cancel = QPushButton(tr("Cancelar"))
        self.btn_once = QPushButton(tr("Solo una vez"))
        self.btn_always = QPushButton(tr("Siempre"))
        
        for btn in [self.btn_cancel, self.btn_once, self.btn_always]:
            btn.setFixedHeight(32)
            btn.setMinimumWidth(100)
            btn.setFont(QFont("Segoe UI", 9))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_cancel.setStyleSheet("""
            QPushButton { background-color: #333; color: white; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: #444; }
        """)
        self.btn_once.setStyleSheet("""
            QPushButton { background-color: #333; color: white; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: #444; }
            QPushButton:disabled { color: #555; background-color: #222; }
        """)
        self.btn_always.setStyleSheet("""
            QPushButton { background-color: #0078D4; color: white; border: none; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #1084D8; }
            QPushButton:disabled { background-color: rgba(0, 120, 212, 0.3); color: #777; }
        """)

        self.btn_once.setEnabled(False)
        self.btn_always.setEnabled(False)

        self.btn_cancel.clicked.connect(self.reject)
        self.btn_once.clicked.connect(lambda: self._on_accept("once"))
        self.btn_always.clicked.connect(lambda: self._on_accept("always"))

        actions_layout.addStretch()
        actions_layout.addWidget(self.btn_cancel)
        actions_layout.addWidget(self.btn_once)
        actions_layout.addWidget(self.btn_always)
        layout.addLayout(actions_layout)

    def _detect_editors(self):
        detector = EditorDetector()
        editors_data = []
        
        # Editor integrado
        pm_editor = PackageMakerEditor()
        if pm_editor.exe_path:
            pm_info = EditorInfo(name=pm_editor.name, display_name=pm_editor.display_name, 
                                 executable=pm_editor.exe_path, icon_path=pm_editor.icon_path, priority=200)
            editors_data.append((pm_info, pm_editor.exe_path))
        
        # Externos
        editors_data.extend(detector.detect_editors())
        
        default_name = get_default_editor()
        
        for i, (info, path) in enumerate(editors_data):
            is_default = (info.name == default_name)
            card = EditorCard(i, info, path, is_default, self)
            card.clicked.connect(self._on_card_clicked)
            card.doubleClicked.connect(self._on_card_double_clicked)
            self.cards.append(card)
            self.list_layout.insertWidget(self.list_layout.count() - 1, card)

        if self.cards:
            # Seleccionar el predeterminado o el primero
            initial_idx = 0
            for i, card in enumerate(self.cards):
                if card.is_default:
                    initial_idx = i
                    break
            self._on_card_clicked(initial_idx)

    def _on_card_clicked(self, index: int):
        if self._selected_index != -1:
            self.cards[self._selected_index].set_selected(False)
        
        self._selected_index = index
        self.cards[index].set_selected(True)
        
        info = self.cards[index].editor_info
        path = self.cards[index].exe_path
        self.selected_editor = (info, path)
        
        self.btn_once.setEnabled(True)
        self.btn_always.setEnabled(True)

    def _on_card_double_clicked(self, index: int):
        self._on_card_clicked(index)
        self._on_accept("once")

    def _check_project_config(self):
        if not self.project_config or not self.project_path: return
        try:
            editor_name = self.project_config.get_project_editor(self.project_path)
            if editor_name:
                exe_path = self.project_config.get_editor_path(editor_name)
                if exe_path and check_executable_exists(exe_path):
                    self.btn_edit_project.setVisible(True)
                    self.btn_edit_project.setText(f"{tr('Editar con')} {editor_name}")
        except: pass

    def _on_edit_project(self):
        if not self.project_config or not self.project_path: return
        try:
            editor_name = self.project_config.get_project_editor(self.project_path)
            exe_path = self.project_config.get_editor_path(editor_name)
            if exe_path and check_executable_exists(exe_path):
                subprocess.Popen([exe_path, self.project_path])
                self.accept()
        except Exception as e:
            QMessageBox.warning(self, tr("Error"), f"{tr('Error al abrir el proyecto')}: {e}")

    def _on_accept(self, action: str):
        self.result_action = action
        if action == "always" and self.selected_editor:
            info, path = self.selected_editor
            save_default_editor(info.name)
            if self.project_config and self.project_path:
                self.project_config.set_project_editor(self.project_path, info.name)
                self.project_config.set_editor_path(info.name, path)
        self.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self._selected_index != -1: self._on_accept("once")
        elif event.key() == Qt.Key.Key_Up:
            if self._selected_index > 0: self._on_card_clicked(self._selected_index - 1)
        elif event.key() == Qt.Key.Key_Down:
            if self._selected_index < len(self.cards) - 1: self._on_card_clicked(self._selected_index + 1)
        else:
            super().keyPressEvent(event)

    def get_result(self) -> Tuple[Optional[Tuple[EditorInfo, str]], str]:
        return self.selected_editor, self.result_action


def show_open_with_dialog(parent=None, project_path: str = "", project_name: str = "") -> Tuple[Optional[Tuple[EditorInfo, str]], str]:
    dialog = OpenWithDialog(parent, project_path, project_name)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_result()
    return None, ""


def open_project_with_editor(parent=None, project_path: str = "", project_name: str = "", use_default: bool = True) -> bool:
    if not os.path.exists(project_path): return False
    
    # Intentar usar predeterminado si se solicita
    if use_default:
        default_name = get_default_editor()
        if default_name:
            detector = EditorDetector()
            pm_editor = PackageMakerEditor()
            all_editors = []
            if pm_editor.exe_path:
                all_editors.append((EditorInfo(name=pm_editor.name, display_name=pm_editor.display_name, 
                                               executable=pm_editor.exe_path), pm_editor.exe_path))
            all_editors.extend(detector.detect_editors())
            
            for info, path in all_editors:
                if info.name == default_name and check_executable_exists(path):
                    subprocess.Popen([path, project_path])
                    return True

    # Mostrar diálogo
    res, action = show_open_with_dialog(parent, project_path, project_name)
    if res:
        info, path = res
        subprocess.Popen([path, project_path])
        return True
    return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Test
    print(show_open_with_dialog(None, "test_project", "Test Project"))
