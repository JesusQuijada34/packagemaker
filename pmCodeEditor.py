#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pmCodeEditor - Editor de código profesional para PackageMaker
Versión 3.0 - Optimizada y simplificada
Uso: python pmCodeEditor.py [archivo|proyecto_flarm]
"""

import sys
import os
import re
import shutil
import subprocess
import json
import difflib
import shlex
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

EDITOR_CONFIG_PATH = Path(__file__).resolve().parent / "data" / "pmCodeEditor" / "editor_config.json"

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPlainTextEdit, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox,
    QDialog, QTextEdit, QLineEdit, QSplitter, QStatusBar,
    QTreeView, QFrame, QMenuBar, QMenu, QGroupBox, QScrollArea, QGridLayout,
    QInputDialog, QRadioButton, QListWidget, QListWidgetItem, QProgressBar,
)
from PyQt6.QtGui import (
    QFont, QSyntaxHighlighter, QTextCharFormat, QTextFormat, QColor, QKeySequence,
    QPainter, QFileSystemModel, QIcon, QAction, QTextCursor, QPalette, QTextDocument,
)
from PyQt6.QtCore import (
    Qt,
    QRect,
    QDir,
    QSize,
    QModelIndex,
    QPoint,
    QUrl,
    QByteArray,
    QRegularExpression,
    QTimer,
    pyqtSignal,
    QProcess,
    QPropertyAnimation,
    QEasingCurve,
    QParallelAnimationGroup,
)

from lib.python_portable_manager import get_python_manager
from lib.dependency_manager import get_dependency_manager

# =============================================================================
# CONSTANTES Y CONFIGURACIÓN
# =============================================================================
VERSION = "3.0.0"
APP_NAME = "pmCodeEditor"

# Hoja de estilos global oscura
DARK_QSS = """
QMainWindow, QDialog, QWidget {
    background-color: #1E1E2E;
    color: #D4D4D4;
}
QLabel {
    color: #D4D4D4;
}
QTreeView, QListView, QPlainTextEdit, QTextEdit {
    background-color: #252526;
    color: #D4D4D4;
    border: 1px solid #3C3C3C;
    selection-background-color: #ff5722;
}
QTreeView::item:selected {
    background-color: #ff5722;
    color: white;
}
QPushButton {
    background-color: #ff5722;
    color: white;
    border: none;
    padding: 5px 10px;
    border-radius: 4px;
}
QPushButton:hover {
    background-color: #ff784e;
}
QPushButton:pressed {
    background-color: #e64a19;
}
QPushButton:disabled {
    background-color: #555555;
    color: #888888;
}
QTabWidget::pane {
    border: 1px solid #3C3C3C;
    background: #1E1E2E;
}
QTabBar::tab {
    background: #2D2D30;
    color: #CCCCCC;
    padding: 6px 12px;
}
QTabBar::tab:selected {
    background: #1E1E2E;
    border-bottom: 2px solid #ff5722;
}
QTabBar::tab:hover:!selected {
    background: #3E3E42;
}
QStatusBar {
    background-color: #ff5722;
    color: white;
}
QLineEdit {
    background-color: #252526;
    color: #D4D4D4;
    border: 1px solid #3C3C3C;
    border-radius: 3px;
    padding: 4px;
}
QLineEdit:focus {
    border: 1px solid #ff5722;
}
QMenuBar {
    background-color: #252526;
    color: #D4D4D4;
    border-bottom: 1px solid #3C3C3C;
}
QMenuBar::item:selected {
    background-color: #ff5722;
    color: white;
}
QMenu {
    background-color: #252526;
    color: #D4D4D4;
    border: 1px solid #3C3C3C;
}
QMenu::item:selected {
    background-color: #ff5722;
    color: white;
}
QMenu::separator {
    height: 1px;
    background-color: #3C3C3C;
    margin: 4px 0px;
}
QGroupBox {
    border: 1px solid #3C3C3C;
    border-radius: 4px;
    margin-top: 8px;
    padding-top: 8px;
    color: #ff5722;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
}
QScrollArea {
    border: none;
}
QComboBox {
    background-color: #252526;
    color: #D4D4D4;
    border: 1px solid #3C3C3C;
    padding: 4px;
}
QComboBox:focus {
    border: 1px solid #ff5722;
}
QCheckBox {
    color: #D4D4D4;
}
QSpinBox {
    background-color: #252526;
    color: #D4D4D4;
    border: 1px solid #3C3C3C;
}
QProgressBar {
    border: 1px solid #3C3C3C;
    border-radius: 4px;
    text-align: center;
    color: white;
}
QProgressBar::chunk {
    background-color: #ff5722;
    border-radius: 4px;
}
"""

# =============================================================================
# FUNCIONES UTILITARIAS
# =============================================================================
def find_flarm_project(project_name: str) -> Optional[str]:
    """Busca un proyecto FLARM en la carpeta de proyectos de PackageMaker."""
    # Determinar carpeta base de proyectos según el sistema
    user_profile = os.path.expanduser("~")
    plataforma = sys.platform
    
    if plataforma.startswith("win"):
        doc_folder = "Documents"
        if not os.path.exists(os.path.join(user_profile, doc_folder)):
            doc_folder = "Documentos"
        base_dir = os.path.join(user_profile, doc_folder, "Packagemaker Projects")
    elif plataforma.startswith("linux"):
        base_dir = os.path.expanduser("~/Documents/Packagemaker Projects")
    else:
        base_dir = os.path.expanduser("~/Documents/Packagemaker Projects")
    
    if not os.path.exists(base_dir):
        return None
    
    # Buscar por nombre exacto de carpeta
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path):
            # Coincidencia exacta
            if item.lower() == project_name.lower():
                return item_path
            # Buscar en el identificador largo (formato: empresa.titulo.id)
            try:
                config_path = os.path.join(item_path, "package_config.json")
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        titulo = config.get('titulo', '')
                        empresa = config.get('empresa', '')
                        pkg_id = config.get('id', '')
                        # Coincidir por título, empresa o ID
                        if (titulo and titulo.lower() == project_name.lower()) or \
                           (empresa and empresa.lower() == project_name.lower()) or \
                           (pkg_id and pkg_id.lower() == project_name.lower()):
                            return item_path
            except:
                pass
    
    # Búsqueda parcial
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path):
            if project_name.lower() in item.lower():
                return item_path
            # Buscar en configuración
            try:
                config_path = os.path.join(item_path, "package_config.json")
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        full_id = f"{config.get('empresa', '')}.{config.get('titulo', '')}.{config.get('id', '')}"
                        if project_name.lower() in full_id.lower():
                            return item_path
            except:
                pass
    
    return None


# =============================================================================
# RESALTADOR DE SINTAXIS MEJORADO
# =============================================================================
class PythonHighlighter(QSyntaxHighlighter):
    """Resaltador de sintaxis Python avanzado con soporte para:
    - Decoradores
    - F-strings
    - Type hints
    - Docstrings
    - Anotaciones
    - Clases especiales
    """
    
    def __init__(self, document):
        super().__init__(document)
        self.error_lines = set()
        self._setup_formats()
        self._setup_rules()
    
    def _setup_formats(self):
        """Configura los formatos de colores."""
        self.formats = {
            "keyword": self._create_format("#569CD6", bold=True),
            "operator": self._create_format("#D4D4D4"),
            "brace": self._create_format("#D4D4D4"),
            "definition": self._create_format("#4EC9B0"),
            "string": self._create_format("#CE9178"),
            "string2": self._create_format("#CE9178"),
            "comment": self._create_format("#6A9955", italic=True),
            "numbers": self._create_format("#B5CEA8"),
            "builtin": self._create_format("#C586C0"),
            "decorator": self._create_format("#DCDCAA", bold=True),
            "type_hint": self._create_format("#4EC9B0", italic=True),
            "f_string": self._create_format("#CE9178"),
            "f_expression": self._create_format("#9CDCFE"),
            "docstring": self._create_format("#6A9955", italic=True),
            "class_name": self._create_format("#4EC9B0", bold=True),
            "function_name": self._create_format("#DCDCAA"),
            "self": self._create_format("#569CD6", italic=True),
            "error": self._create_format("#F44747", underline=True),
            "magic_method": self._create_format("#DCDCAA"),
        }
    
    def _create_format(self, color, bold=False, italic=False, underline=False):
        """Crea un formato de texto."""
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        if bold:
            fmt.setFontWeight(QFont.Weight.Bold)
        if italic:
            fmt.setFontItalic(True)
        if underline:
            fmt.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SpellCheckUnderline)
        return fmt
    
    def _setup_rules(self):
        """Configura las reglas de start_install."""
        self.rules = []
        
        # Palabras clave
        keywords = [
            "and", "as", "assert", "async", "await", "break", "class", "continue", 
            "def", "del", "elif", "else", "except", "finally", "for", "from", 
            "global", "if", "import", "in", "is", "lambda", "nonlocal", "not", 
            "or", "pass", "raise", "return", "try", "while", "with", "yield",
            "True", "False", "None"
        ]
        for word in keywords:
            pattern = QRegularExpression(f"\\b{word}\\b")
            self.rules.append((pattern, self.formats["keyword"]))
        
        # Builtins
        builtins = [
            "abs", "all", "any", "ascii", "bin", "bool", "breakpoint", "bytearray", 
            "bytes", "callable", "chr", "classmethod", "compile", "complex", "delattr",
            "dict", "dir", "divmod", "enumerate", "eval", "exec", "filter",
            "float", "format", "frozenset", "getattr", "globals", "hasattr",
            "hash", "help", "hex", "id", "input", "int", "isinstance", "issubclass",
            "iter", "len", "list", "locals", "map", "max", "memoryview", "min",
            "next", "object", "oct", "open", "ord", "pow", "print", "property",
            "range", "repr", "reversed", "round", "set", "setattr", "slice",
            "sorted", "staticmethod", "str", "sum", "super", "tuple", "type",
            "vars", "zip", "__import__", "__name__", "__file__", "__doc__",
            "__package__", "__spec__", "__annotations__", "__builtins__", "__cached__"
        ]
        for word in builtins:
            pattern = QRegularExpression(f"\\b{word}\\b")
            self.rules.append((pattern, self.formats["builtin"]))
        
        # Definiciones de clase
        self.rules.append((
            QRegularExpression(r"\bclass\b\s*(\w+)"), 
            self.formats["class_name"]
        ))
        
        # Definiciones de función
        self.rules.append((
            QRegularExpression(r"\bdef\b\s*(\w+)"), 
            self.formats["function_name"]
        ))
        
        # Métodos mágicos
        magic_methods = ["__init__", "__str__", "__repr__", "__call__", "__getattr__",
                        "__setattr__", "__delattr__", "__getitem__", "__setitem__",
                        "__delitem__", "__iter__", "__next__", "__contains__", "__len__",
                        "__eq__", "__ne__", "__lt__", "__le__", "__gt__", "__ge__",
                        "__add__", "__sub__", "__mul__", "__truediv__", "__floordiv__",
                        "__mod__", "__pow__", "__and__", "__or__", "__xor__", "__lshift__",
                        "__rshift__", "__invert__", "__neg__", "__pos__", "__abs__",
                        "__enter__", "__exit__", "__new__", "__del__"]
        for method in magic_methods:
            pattern = QRegularExpression(f"\\b{method}\\b")
            self.rules.append((pattern, self.formats["magic_method"]))
        
        # Decoradores
        self.rules.append((
            QRegularExpression(r"^\s*@(\w+(?:\.\w+)*)"),
            self.formats["decorator"]
        ))
        
        # Self y cls
        self.rules.append((QRegularExpression(r"\bself\b"), self.formats["self"]))
        self.rules.append((QRegularExpression(r"\bcls\b"), self.formats["self"]))
        
        # Type hints (básico)
        type_hints = ["int", "str", "float", "bool", "list", "dict", "tuple", "set",
                     "frozenset", "bytes", "bytearray", "memoryview", "object",
                     "Optional", "List", "Dict", "Tuple", "Set", "Union", "Any",
                     "Callable", "Iterator", "Iterable", "Generator", "Coroutine"]
        for hint in type_hints:
            pattern = QRegularExpression(f"\\b{hint}\\b")
            self.rules.append((pattern, self.formats["type_hint"]))
        
        # Cadenas simples y dobles
        self.rules.append((
            QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'),
            self.formats["string"]
        ))
        self.rules.append((
            QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"),
            self.formats["string2"]
        ))
        
        # F-strings (detección básica)
        self.rules.append((
            QRegularExpression(r'f"[^"]*"'),
            self.formats["f_string"]
        ))
        self.rules.append((
            QRegularExpression(r"f'[^']*'"),
            self.formats["f_string"]
        ))
        
        # Comentarios
        self.rules.append((
            QRegularExpression(r"#[^\n]*"),
            self.formats["comment"]
        ))
        
        # Números
        self.rules.append((
            QRegularExpression(r"\b[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b"),
            self.formats["numbers"]
        ))
        self.rules.append((
            QRegularExpression(r"\b0[xX][0-9a-fA-F]+\b"),
            self.formats["numbers"]
        ))
        self.rules.append((
            QRegularExpression(r"\b0[oO]?[0-7]+\b"),
            self.formats["numbers"]
        ))
        self.rules.append((
            QRegularExpression(r"\b0[bB][01]+\b"),
            self.formats["numbers"]
        ))
    
    def highlightBlock(self, text):
        """Resalta un bloque de texto."""
        # Procesar reglas básicas
        for pattern, fmt in self.rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                start = match.capturedStart()
                length = match.capturedLength()
                self.setFormat(start, length, fmt)
        
        # Resaltar líneas con errores
        block = self.currentBlock()
        if block.blockNumber() in self.error_lines:
            fmt = self.formats["error"]
            self.setFormat(0, len(text), fmt)
        
        # Procesar docstrings (triple comillas)
        self._highlight_docstrings(text)
    
    def _highlight_docstrings(self, text):
        """Resalta docstrings de triple comillas."""
        docstring_pattern = QRegularExpression(r'""".*?"""', QRegularExpression.PatternOption.DotMatchesEverythingOption)
        match_iterator = docstring_pattern.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            start = match.capturedStart()
            length = match.capturedLength()
            self.setFormat(start, length, self.formats["docstring"])
        
        docstring_pattern2 = QRegularExpression(r"'''.*?'''", QRegularExpression.PatternOption.DotMatchesEverythingOption)
        match_iterator = docstring_pattern2.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            start = match.capturedStart()
            length = match.capturedLength()
            self.setFormat(start, length, self.formats["docstring"])
    
    def set_error_line(self, line_num: int, has_error: bool = True):
        """Marca/desmarca una línea con error."""
        if has_error:
            self.error_lines.add(line_num)
        else:
            self.error_lines.discard(line_num)
        self.rehighlight()


# =============================================================================
# EDITOR DE CÓDIGO CON NÚMEROS DE LÍNEA
# =============================================================================
class LineNumberArea(QWidget):
    """Área de números de línea."""
    
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor
        self.setFixedWidth(50)
    
    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)
    
    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """Editor de código con resaltado de línea actual y números de línea."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        
        # Conectar señales
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        
        # Configuración inicial
        self.update_line_number_area_width(0)
        self.highlight_current_line()
        
        # Configuración de fuente
        font = QFont("Consolas", 11)
        font.setFixedPitch(True)
        self.setFont(font)
        
        # Tabulación
        self.setTabStopDistance(40)
        
        # Configurar colores de selección
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#264F78"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
        self.setPalette(palette)
    
    def line_number_area_width(self):
        """Calcula el ancho del área de números de línea."""
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
    
    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))
    
    def line_number_area_paint_event(self, event):
        """Pinta los números de línea."""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#1E1E1E"))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#858585"))
                painter.drawText(0, int(top), self.line_number_area.width() - 5, 
                               self.fontMetrics().height(),
                               Qt.AlignmentFlag.AlignRight, number)
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1
        
        painter.end()
    
    def highlight_current_line(self):
        """Resalta la línea actual."""
        extra_selections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#2D2D30")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)
    
    def get_line_number(self):
        """Obtiene el número de línea actual."""
        return self.textCursor().blockNumber() + 1
    
    def get_column_number(self):
        """Obtiene el número de columna actual."""
        return self.textCursor().columnNumber() + 1


# =============================================================================
# EXPLORADOR DE ARCHIVOS (PROYECTO ACTUAL)
# =============================================================================
class FileExplorer(QWidget):
    """Panel de explorador de archivos - muestra solo el proyecto actual."""
    
    fileSelected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._project_path = None
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header con nombre de proyecto
        self.header = QLabel("Proyecto")
        self.header.setStyleSheet("font-weight: bold; padding: 5px; color: #ff5722;")
        layout.addWidget(self.header)
        
        # Tree view
        self.tree = QTreeView()
        self.tree.setHeaderHidden(True)
        self.model = QFileSystemModel()
        self.model.setRootPath("")
        self.model.setFilter(
            QDir.Filter.AllEntries |
            QDir.Filter.NoDotAndDotDot |
            QDir.Filter.AllDirs
        )
        self.tree.setModel(self.model)
        self.tree.setAnimated(False)  # Desactivar animación para mejor rendimiento
        self.tree.setIndentation(12)
        self.tree.setSortingEnabled(True)
        
        # Ocultar columnas excepto nombre
        for i in range(1, self.model.columnCount()):
            self.tree.hideColumn(i)
        
        self.tree.doubleClicked.connect(self._on_file_double_clicked)
        layout.addWidget(self.tree)
    
    def set_project_path(self, path):
        """Establece la ruta del proyecto actual."""
        self._project_path = path
        if path and os.path.exists(path):
            self.header.setText(f"Proyecto: {os.path.basename(path)}")
            self.tree.setRootIndex(self.model.index(path))
            self.tree.expandToDepth(1)
        else:
            self.header.setText("Sin proyecto")
            self.tree.setRootIndex(QModelIndex())
    
    def get_project_path(self):
        """Obtiene la ruta del proyecto actual."""
        return self._project_path
    
    def _on_file_double_clicked(self, index):
        """Maneja doble clic en archivo."""
        path = self.model.filePath(index)
        if os.path.isfile(path):
            self.fileSelected.emit(path)


# =============================================================================
# PANEL DE CONSOLA MEJORADO
# =============================================================================
class ConsolePanel(QWidget):
    """Panel de consola avanzado con salida en tiempo real y soporte ANSI."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._process = None
        self._python_path = sys.executable
        self._setup_ui()

    def set_python_path(self, python_path: str):
        self._python_path = python_path or sys.executable
        self.input_field.setPlaceholderText(
            "Python, pip (!cmd) o código — ej: pip install requests"
        )
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Consola")
        title.setStyleSheet("font-weight: bold; padding: 5px; color: #ff5722;")
        header.addWidget(title)
        
        # Botones de control
        self.clear_btn = QPushButton("Limpiar")
        self.clear_btn.setMaximumWidth(70)
        self.clear_btn.clicked.connect(self.clear)
        header.addWidget(self.clear_btn)
        
        self.stop_btn = QPushButton("Detener")
        self.stop_btn.setMaximumWidth(70)
        self.stop_btn.clicked.connect(self.stop_process)
        self.stop_btn.setEnabled(False)
        header.addWidget(self.stop_btn)
        
        header.addStretch()
        
        # Indicador de estado
        self.status_label = QLabel("●")
        self.status_label.setStyleSheet("color: #4CAF50; font-size: 12px;")
        self.status_label.setToolTip("Listo")
        header.addWidget(self.status_label)
        
        layout.addLayout(header)
        
        # Output area
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("""
            QTextEdit {
                background-color: #0C0C0C;
                color: #CCCCCC;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 12px;
                border: none;
            }
        """)
        layout.addWidget(self.output)
        
        # Input area
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(5, 2, 5, 2)
        
        prompt = QLabel(">")
        prompt.setStyleSheet("color: #ff5722; font-weight: bold; font-family: Consolas;")
        input_layout.addWidget(prompt)
        
        self.input_field = QLineEdit()
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #1E1E1E;
                color: #CCCCCC;
                border: 1px solid #3C3C3C;
                padding: 4px;
                font-family: Consolas, monospace;
            }
        """)
        self.input_field.setPlaceholderText("Comando Python o shell...")
        self.input_field.returnPressed.connect(self._execute_input)
        input_layout.addWidget(self.input_field)
        
        self.run_btn = QPushButton("Ejecutar")
        self.run_btn.setMaximumWidth(80)
        self.run_btn.clicked.connect(self._execute_input)
        input_layout.addWidget(self.run_btn)
        
        layout.addLayout(input_layout)
    
    def _ansi_to_html(self, text: str) -> str:
        """Convierte códigos ANSI a HTML."""
        # Mapeo básico de colores ANSI
        ansi_colors = {
            '30': '#000000',  # Negro
            '31': '#F44747',  # Rojo
            '32': '#4CAF50',  # Verde
            '33': '#FFC107',  # Amarillo
            '34': '#2196F3',  # Azul
            '35': '#9C27B0',  # Magenta
            '36': '#00BCD4',  # Cyan
            '37': '#CCCCCC',  # Blanco
            '90': '#666666',  # Gris oscuro
            '91': '#FF6B6B',  # Rojo claro
            '92': '#69F0AE',  # Verde claro
            '93': '#FFD54F',  # Amarillo claro
            '94': '#64B5F6',  # Azul claro
            '95': '#CE93D8',  # Magenta claro
            '96': '#4DD0E1',  # Cyan claro
            '97': '#FFFFFF',  # Blanco brillante
        }
        
        import html
        text = html.escape(text)
        
        # Reemplazar códigos ANSI
        import re
        result = []
        current_color = None
        
        # Patrón para códigos ANSI escape
        pattern = r'\x1b\[([0-9;]*)m'
        
        last_end = 0
        for match in re.finditer(pattern, text):
            # Texto antes del código
            if match.start() > last_end:
                segment = text[last_end:match.start()]
                if current_color:
                    result.append(f'<span style="color: {current_color};">{segment}</span>')
                else:
                    result.append(segment)
            
            # Procesar código ANSI
            codes = match.group(1).split(';')
            for code in codes:
                if code == '0':  # Reset
                    current_color = None
                elif code in ansi_colors:
                    current_color = ansi_colors[code]
            
            last_end = match.end()
        
        # Resto del texto
        if last_end < len(text):
            segment = text[last_end:]
            if current_color:
                result.append(f'<span style="color: {current_color};">{segment}</span>')
            else:
                result.append(segment)
        
        return ''.join(result)
    
    def append_output(self, text: str, is_error: bool = False, use_ansi: bool = False):
        """Añade texto a la consola (texto plano por defecto; evita &quot; en rutas)."""
        if use_ansi and not is_error:
            self.output.append(self._ansi_to_html(text))
        else:
            cursor = self.output.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            fmt = cursor.charFormat()
            fmt.setForeground(QColor("#F44747" if is_error else "#CCCCCC"))
            cursor.insertText(text.rstrip() + "\n", fmt)
            self.output.setTextCursor(cursor)

        scrollbar = self.output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def append_html(self, html: str):
        """Añade HTML directo a la consola."""
        self.output.append(html)
        scrollbar = self.output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear(self):
        """Limpia la consola."""
        self.output.clear()
    
    def _set_running(self, running: bool):
        """Actualiza el estado de ejecución."""
        self.stop_btn.setEnabled(running)
        if running:
            self.status_label.setStyleSheet("color: #FFC107; font-size: 12px;")
            self.status_label.setToolTip("Ejecutando...")
        else:
            self.status_label.setStyleSheet("color: #4CAF50; font-size: 12px;")
            self.status_label.setToolTip("Listo")
    
    def stop_process(self):
        """Detiene el proceso en ejecución."""
        if self._process and self._process.state() != QProcess.ProcessState.NotRunning:
            self._process.terminate()
            self._process.waitForFinished(2000)
            if self._process.state() != QProcess.ProcessState.NotRunning:
                self._process.kill()
            self.append_output("[Proceso detenado por el usuario]", is_error=True)
            self._set_running(False)
    
    def _get_working_dir(self) -> str:
        parent = self.parent()
        if parent and getattr(parent, "file_path", None):
            return os.path.dirname(parent.file_path)
        if parent and getattr(parent, "project_path", None):
            return parent.project_path
        return os.getcwd()

    def _normalize_shell_command_list(self, command: str) -> List[str]:
        """Convierte un comando de consola a lista de argumentos (sin comillas escapadas)."""
        command = command.strip()
        if command.startswith("!"):
            shell_cmd = command[1:].strip()
            if sys.platform == "win32":
                return ["cmd", "/c", shell_cmd]
            return ["sh", "-c", shell_cmd]

        py = self._python_path
        if command in ("pip", "pip3"):
            return [py, "-m", "pip"]
        if command.startswith("pip ") or command.startswith("pip3 "):
            extra = command.split(None, 1)[1] if " " in command else ""
            return [py, "-m", "pip"] + (shlex.split(extra, posix=False) if extra else [])
        if command in ("python", "py", "python3"):
            return [py]
        if command.startswith("python ") or command.startswith("py ") or command.startswith("python3 "):
            rest = command.split(None, 1)[1]
            return [py] + shlex.split(rest, posix=False)
        if command.startswith("python -m ") or command.startswith("py -m "):
            rest = command.split("-m ", 1)[1]
            return [py, "-m"] + shlex.split(rest, posix=False)
        if sys.platform == "win32":
            return ["cmd", "/c", command]
        return ["sh", "-c", command]

    def _is_shell_command(self, command: str) -> bool:
        if command.startswith("!"):
            return True
        first = command.split()[0] if command.split() else ""
        if first in ("pip", "pip3", "python", "py", "python3", "conda"):
            return True
        return command.startswith(("pip ", "pip3 ", "python ", "py ", "python3 ", "python -m ", "py -m "))

    def _execute_input(self):
        """Ejecuta el comando ingresado en el campo de input."""
        command = self.input_field.text().strip()
        if not command:
            return

        self.input_field.clear()
        self.append_output(f">>> {command}", is_error=False)

        if self._is_shell_command(command):
            cmd_list = self._normalize_shell_command_list(command)
            self.run_command_list(cmd_list, working_dir=self._get_working_dir())
        else:
            self._execute_python_code(command)
    
    def _execute_python_code(self, code: str):
        """Ejecuta código Python directamente."""
        import io
        import contextlib
        
        # Capturar stdout y stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            with contextlib.redirect_stdout(stdout_capture):
                with contextlib.redirect_stderr(stderr_capture):
                    exec(code, {"__name__": "__console__"})
            
            output = stdout_capture.getvalue()
            errors = stderr_capture.getvalue()
            
            if output:
                self.append_output(output)
            if errors:
                self.append_output(errors, is_error=True)
                
        except Exception as e:
            import traceback
            self.append_output(f"Error: {e}", is_error=True)
            self.append_output(traceback.format_exc(), is_error=True)
    
    def run_command_list(self, cmd: List[str], working_dir: str = None) -> bool:
        """Ejecuta un comando como lista (sin problemas de comillas)."""
        if not cmd:
            return False
        self.append_output(f"$ {' '.join(cmd)}")
        self._set_running(True)

        self._process = QProcess(self)
        self._process.setWorkingDirectory(working_dir or os.getcwd())
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self._process.readyReadStandardOutput.connect(self._read_output)
        self._process.readyReadStandardError.connect(self._read_error)
        self._process.finished.connect(self._process_finished)

        program = cmd[0]
        args = cmd[1:]
        self._process.start(program, args)

        if not self._process.waitForStarted(5000):
            self.append_output("Error: no se pudo iniciar el proceso", is_error=True)
            self._set_running(False)
            return False
        return True

    def run_command(self, command: str, working_dir: str = None) -> bool:
        """Ejecuta un comando string (se convierte a lista)."""
        if self._is_shell_command(command):
            parts = self._normalize_shell_command_list(command)
        elif sys.platform == "win32":
            parts = shlex.split(command, posix=False)
        else:
            parts = shlex.split(command)
        return self.run_command_list(parts, working_dir) if parts else False
    
    def _read_output(self):
        """Lee la salida estándar del proceso."""
        if self._process:
            data = self._process.readAllStandardOutput().data().decode('utf-8', errors='replace')
            if data:
                self.append_output(data.rstrip(), use_ansi=True)
    
    def _read_error(self):
        """Lee la salida de error del proceso."""
        if self._process:
            data = self._process.readAllStandardError().data().decode('utf-8', errors='replace')
            if data:
                self.append_output(data.rstrip(), is_error=True)
    
    def _process_finished(self, exit_code, exit_status):
        """Maneja la finalización del proceso."""
        self._set_running(False)
        if exit_code == 0:
            self.append_output(f"[Proceso finalizado exitosamente]")
        else:
            self.append_output(f"[Proceso finalizado con código: {exit_code}]", is_error=True)


# =============================================================================
# DIÁLOGO DE DIFERENCIAS (DIFF)
# =============================================================================
class DiffDialog(QDialog):
    """Diálogo para comparar dos archivos o versiones."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Comparar Archivos - Diff")
        self.setMinimumSize(900, 600)
        self.setStyleSheet(DARK_QSS)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header
        header = QHBoxLayout()
        
        self.file1_btn = QPushButton("Seleccionar Archivo Original")
        self.file1_btn.clicked.connect(self._select_file1)
        header.addWidget(self.file1_btn)
        
        header.addWidget(QLabel("VS"))
        
        self.file2_btn = QPushButton("Seleccionar Archivo Nuevo")
        self.file2_btn.clicked.connect(self._select_file2)
        header.addWidget(self.file2_btn)
        
        self.compare_btn = QPushButton("Comparar")
        self.compare_btn.clicked.connect(self._do_compare)
        self.compare_btn.setEnabled(False)
        header.addWidget(self.compare_btn)
        
        layout.addLayout(header)
        
        # Diff display
        self.diff_display = QTextEdit()
        self.diff_display.setReadOnly(True)
        self.diff_display.setFont(QFont("Consolas", 10))
        layout.addWidget(self.diff_display)
        
        # Info label
        self.info_label = QLabel("Selecciona dos archivos para comparar")
        layout.addWidget(self.info_label)
        
        self.file1_path = None
        self.file2_path = None
    
    def _select_file1(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo original")
        if path:
            self.file1_path = path
            self.file1_btn.setText(f"Original: {os.path.basename(path)}")
            self._check_ready()
    
    def _select_file2(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo nuevo")
        if path:
            self.file2_path = path
            self.file2_btn.setText(f"Nuevo: {os.path.basename(path)}")
            self._check_ready()
    
    def _check_ready(self):
        self.compare_btn.setEnabled(self.file1_path and self.file2_path)
    
    def _do_compare(self):
        """Realiza la comparación usando difflib."""
        if not self.file1_path or not self.file2_path:
            return
        
        try:
            with open(self.file1_path, 'r', encoding='utf-8') as f1:
                lines1 = f1.readlines()
            with open(self.file2_path, 'r', encoding='utf-8') as f2:
                lines2 = f2.readlines()
            
            # Generar diff
            diff = list(difflib.unified_diff(
                lines1, lines2,
                fromfile=os.path.basename(self.file1_path),
                tofile=os.path.basename(self.file2_path),
                lineterm=''
            ))
            
            # Colorear el diff
            html_lines = []
            added_count = 0
            removed_count = 0
            
            for line in diff:
                if line.startswith('+'):
                    html_lines.append(f'<span style="color: #4CAF50; background: #1B5E20;">{self._escape_html(line)}</span>')
                    added_count += 1
                elif line.startswith('-'):
                    html_lines.append(f'<span style="color: #F44336; background: #B71C1C;">{self._escape_html(line)}</span>')
                    removed_count += 1
                elif line.startswith('@@'):
                    html_lines.append(f'<span style="color: #2196F3;">{self._escape_html(line)}</span>')
                elif line.startswith('---'):
                    html_lines.append(f'<span style="color: #F44336;">{self._escape_html(line)}</span>')
                elif line.startswith('+++'):
                    html_lines.append(f'<span style="color: #4CAF50;">{self._escape_html(line)}</span>')
                else:
                    html_lines.append(self._escape_html(line))
            
            self.diff_display.setHtml('<pre>' + '\n'.join(html_lines) + '</pre>')
            self.info_label.setText(
                f"<b>Resultado:</b> {added_count} líneas agregadas, {removed_count} líneas eliminadas"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo comparar: {e}")
    
    def _escape_html(self, text: str) -> str:
        """Escapa caracteres HTML especiales."""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;'))
    
    def compare_with_content(self, file_path: str, content: str):
        """Compara un archivo con contenido en memoria."""
        self.file1_path = file_path
        self.file1_btn.setText(f"Original: {os.path.basename(file_path)}")
        self.file2_path = "[Actual en editor]"
        self.file2_btn.setText("Nuevo: [Actual en editor]")
        self._check_ready()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines1 = f.readlines()
            lines2 = content.split('\n')
            lines2 = [line + '\n' for line in lines2]
            
            diff = list(difflib.unified_diff(
                lines1, lines2,
                fromfile=os.path.basename(file_path),
                tofile="[Actual en editor]",
                lineterm=''
            ))
            
            html_lines = []
            for line in diff:
                if line.startswith('+'):
                    html_lines.append(f'<span style="color: #4CAF50; background: #1B5E20;">{self._escape_html(line)}</span>')
                elif line.startswith('-'):
                    html_lines.append(f'<span style="color: #F44336; background: #B71C1C;">{self._escape_html(line)}</span>')
                elif line.startswith('@@'):
                    html_lines.append(f'<span style="color: #2196F3;">{self._escape_html(line)}</span>')
                else:
                    html_lines.append(self._escape_html(line))
            
            self.diff_display.setHtml('<pre>' + '\n'.join(html_lines) + '</pre>')
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo comparar: {e}")


# =============================================================================
# DIÁLOGO DE MÉTRICAS DE CÓDIGO
# =============================================================================
class CodeMetrics:
    """Calcula métricas de código Python."""
    
    def __init__(self, code: str, file_path: Optional[str] = None):
        self.code = code
        self.file_path = file_path
        self.lines = code.split('\n')
    
    def calculate(self) -> Dict[str, Any]:
        """Calcula todas las métricas."""
        return {
            'total_lines': len(self.lines),
            'code_lines': self._count_code_lines(),
            'comment_lines': self._count_comment_lines(),
            'blank_lines': self._count_blank_lines(),
            'words': self._count_words(),
            'characters': len(self.code),
            'functions': self._count_functions(),
            'classes': self._count_classes(),
            'imports': self._count_imports(),
            'complexity': self._calculate_complexity(),
            'avg_line_length': self._avg_line_length(),
        }
    
    def _count_code_lines(self) -> int:
        return sum(1 for line in self.lines if line.strip() and not line.strip().startswith('#'))
    
    def _count_comment_lines(self) -> int:
        return sum(1 for line in self.lines if line.strip().startswith('#'))
    
    def _count_blank_lines(self) -> int:
        return sum(1 for line in self.lines if not line.strip())
    
    def _count_words(self) -> int:
        return len(self.code.split())
    
    def _count_functions(self) -> int:
        return len(re.findall(r'^\s*def\s+\w+', self.code, re.MULTILINE))
    
    def _count_classes(self) -> int:
        return len(re.findall(r'^\s*class\s+\w+', self.code, re.MULTILINE))
    
    def _count_imports(self) -> int:
        return len(re.findall(r'^(?:from|import)\s+', self.code, re.MULTILINE))
    
    def _calculate_complexity(self) -> int:
        """Cálculo simple de complejidad ciclomática."""
        complexity = 1
        complexity += len(re.findall(r'\bif\b', self.code))
        complexity += len(re.findall(r'\belif\b', self.code))
        complexity += len(re.findall(r'\bfor\b', self.code))
        complexity += len(re.findall(r'\bwhile\b', self.code))
        complexity += len(re.findall(r'\bexcept\b', self.code))
        complexity += len(re.findall(r'\band\b|\bor\b', self.code))
        return complexity
    
    def _avg_line_length(self) -> float:
        non_empty = [len(line) for line in self.lines if line.strip()]
        return sum(non_empty) / len(non_empty) if non_empty else 0


class MetricsDialog(QDialog):
    """Diálogo para mostrar métricas de código."""
    
    def __init__(self, code: str, file_path: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Métricas de Código")
        self.setMinimumSize(500, 400)
        self.setStyleSheet(DARK_QSS)
        self._setup_ui()
        self._calculate_and_display(code, file_path)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Métricas del Archivo")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ff5722;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Grid de métricas
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        self.grid = QGridLayout(container)
        self.grid.setSpacing(15)
        
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        # Botón cerrar
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def _calculate_and_display(self, code: str, file_path: Optional[str]):
        metrics = CodeMetrics(code, file_path)
        data = metrics.calculate()
        
        items = [
            ("Líneas Totales", str(data['total_lines'])),
            ("Líneas de Código", str(data['code_lines'])),
            ("Líneas de Comentarios", str(data['comment_lines'])),
            ("Líneas en Blanco", str(data['blank_lines'])),
            ("Palabras", str(data['words'])),
            ("Caracteres", str(data['characters'])),
            ("Funciones", str(data['functions'])),
            ("Clases", str(data['classes'])),
            ("Imports", str(data['imports'])),
            ("Complejidad Ciclomática", str(data['complexity'])),
            ("Longitud Promedio", f"{data['avg_line_length']:.1f}"),
        ]
        
        for i, (label, value) in enumerate(items):
            label_widget = QLabel(f"<b>{label}:</b>")
            label_widget.setStyleSheet("color: #D4D4D4;")
            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: #ff5722; font-weight: bold;")
            value_widget.setAlignment(Qt.AlignmentFlag.AlignRight)
            
            self.grid.addWidget(label_widget, i, 0)
            self.grid.addWidget(value_widget, i, 1)


# =============================================================================
# DIÁLOGO DE BÚSQUEDA Y REEMPLAZO
# =============================================================================
class FindDialog(QDialog):
    """Diálogo de búsqueda y reemplazo."""
    
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.setWindowTitle("Buscar y Reemplazar")
        self.setMinimumSize(400, 150)
        self.setStyleSheet(DARK_QSS)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Buscar
        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel("Buscar:"))
        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("Texto a buscar...")
        self.find_input.returnPressed.connect(self.find_next)
        find_layout.addWidget(self.find_input)
        layout.addLayout(find_layout)
        
        # Reemplazar
        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel("Reemplazar:"))
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Texto de reemplazo...")
        replace_layout.addWidget(self.replace_input)
        layout.addLayout(replace_layout)
        
        # Opciones
        options_layout = QHBoxLayout()
        self.case_sensitive = QCheckBox("Distinguir mayúsculas")
        self.whole_words = QCheckBox("Palabras completas")
        options_layout.addWidget(self.case_sensitive)
        options_layout.addWidget(self.whole_words)
        options_layout.addStretch()
        layout.addLayout(options_layout)
        
        # Botones
        btn_layout = QHBoxLayout()
        self.find_btn = QPushButton("Buscar siguiente")
        self.find_btn.clicked.connect(self.find_next)
        self.replace_btn = QPushButton("Reemplazar")
        self.replace_btn.clicked.connect(self.replace)
        self.replace_all_btn = QPushButton("Reemplazar todo")
        self.replace_all_btn.clicked.connect(self.replace_all)
        self.close_btn = QPushButton("Cerrar")
        self.close_btn.clicked.connect(self.close)
        
        btn_layout.addWidget(self.find_btn)
        btn_layout.addWidget(self.replace_btn)
        btn_layout.addWidget(self.replace_all_btn)
        btn_layout.addWidget(self.close_btn)
        layout.addLayout(btn_layout)
    
    def find_next(self):
        """Busca la siguiente ocurrencia."""
        text = self.find_input.text()
        if not text:
            return
        
        flags = QTextDocument.FindFlag(0)
        if self.case_sensitive.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if self.whole_words.isChecked():
            flags |= QTextDocument.FindFlag.FindWholeWords
        
        if not self.editor.find(text, flags):
            # Si no encuentra, volver al inicio
            cursor = self.editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.editor.setTextCursor(cursor)
            self.editor.find(text, flags)
    
    def replace(self):
        """Reemplaza la selección actual."""
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            cursor.insertText(self.replace_input.text())
        self.find_next()
    
    def replace_all(self):
        """Reemplaza todas las ocurrencias."""
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()
        if not find_text:
            return
        
        content = self.editor.toPlainText()
        count = content.count(find_text)
        new_content = content.replace(find_text, replace_text)
        self.editor.setPlainText(new_content)
        
        QMessageBox.information(self, "Reemplazo completo", 
                               f"Se reemplazaron {count} ocurrencias.")


# =============================================================================
# CONFIGURACIÓN DE PYTHON PORTABLE
# =============================================================================
class PythonSetupDialog(QDialog):
    """Diálogo de configuración inicial de Python portable."""

    setup_complete = pyqtSignal(bool, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = get_python_manager()
        self.selected_version = None
        self._python_path = None
        self.init_ui()
        self.load_versions()

    def init_ui(self):
        self.setWindowTitle("Configuración de Python - PackageMaker IDE")
        self.setMinimumSize(620, 520)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #1E1E2E;
                border: 1px solid #3C3C3C;
                border-radius: 10px;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("Bienvenido a PackageMaker IDE")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #ff5722;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        desc = QLabel(
            "Para funcionar de forma autónoma, el IDE puede descargar un intérprete Python portable.\n"
            "Selecciona una opción:"
        )
        desc.setStyleSheet("color: #ccc; font-size: 13px;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        if sys.platform != "win32":
            warn = QLabel(
                "En este sistema se usará el Python del sistema. "
                "La descarga portable solo está disponible en Windows."
            )
            warn.setStyleSheet("color: #FFC107; font-size: 12px;")
            warn.setWordWrap(True)
            layout.addWidget(warn)

        options_group = QGroupBox("Opciones de instalación")
        options_layout = QVBoxLayout(options_group)

        self.radio_recommended = QRadioButton(
            f"Descargar versión recomendada (Python {self.manager.get_default_version()})"
        )
        self.radio_recommended.setChecked(True)
        self.radio_recommended.setEnabled(sys.platform == "win32")
        options_layout.addWidget(self.radio_recommended)

        self.radio_choose = QRadioButton("Elegir versión específica")
        self.radio_choose.setEnabled(sys.platform == "win32")
        options_layout.addWidget(self.radio_choose)

        self.version_list = QListWidget()
        self.version_list.setMaximumHeight(160)
        self.version_list.setVisible(False)
        options_layout.addWidget(self.version_list)

        layout.addWidget(options_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #aaa; font-size: 12px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_skip = QPushButton("Usar Python del sistema")
        self.btn_skip.clicked.connect(self.on_use_system_python)
        btn_layout.addWidget(self.btn_skip)

        self.btn_next = QPushButton("Siguiente →")
        self.btn_next.setFixedSize(120, 40)
        self.btn_next.clicked.connect(self.on_next)
        btn_layout.addWidget(self.btn_next)

        layout.addLayout(btn_layout)
        outer.addWidget(panel)

        self.radio_choose.toggled.connect(self.on_choose_toggled)

    def load_versions(self):
        self.version_list.clear()
        for ver, info in self.manager.get_all_versions_info().items():
            status = "✅ " if info["installed"] else "📦 "
            size = f" ({info['size_mb']:.0f} MB)" if info["size_mb"] > 0 else ""
            rec = " ⭐" if info["recommended"] else ""
            item = QListWidgetItem(f"{status}Python {ver} - {info['version']}{size}{rec}")
            item.setData(Qt.ItemDataRole.UserRole, ver)
            self.version_list.addItem(item)

    def on_choose_toggled(self, checked):
        self.version_list.setVisible(checked)

    def on_use_system_python(self):
        self._python_path = sys.executable
        os.environ["PM_PYTHON_PATH"] = self._python_path
        self.setup_complete.emit(True, self._python_path)
        self.accept()

    def on_next(self):
        if sys.platform != "win32":
            self.on_use_system_python()
            return

        if self.radio_recommended.isChecked():
            version = self.manager.get_default_version()
        else:
            selected = self.version_list.currentItem()
            if not selected:
                QMessageBox.warning(self, "Selección requerida", "Selecciona una versión de Python.")
                return
            version = selected.data(Qt.ItemDataRole.UserRole)

        if self.manager.get_installation_status(version):
            python_exe = self.manager.get_python_exe(version)
            self._finish_success(str(python_exe))
            return

        self.selected_version = version
        self.btn_next.setEnabled(False)
        self.btn_skip.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText(f"Descargando Python {version}...")

        self.manager.installation_progress.connect(self.on_installation_progress)
        self.manager.installation_finished.connect(self.on_installation_finished)
        self.manager.status_message.connect(self.status_label.setText)
        self.manager.install_version(version)

    def on_installation_progress(self, version: str, percent: int):
        if version == self.selected_version:
            self.progress_bar.setValue(percent)

    def on_installation_finished(self, version: str, success: bool):
        if version != self.selected_version:
            return
        if success:
            python_exe = self.manager.get_python_exe(version)
            if python_exe:
                self._finish_success(str(python_exe))
            else:
                self._finish_error(version)
        else:
            self._finish_error(version)

    def _finish_success(self, python_path: str):
        self._python_path = python_path
        os.environ["PM_PYTHON_PATH"] = python_path
        self.setup_complete.emit(True, python_path)
        self.accept()

    def _finish_error(self, version: str):
        self.status_label.setText(f"Error instalando Python {version}")
        self.btn_next.setEnabled(True)
        self.btn_skip.setEnabled(True)
        self.progress_bar.setVisible(False)


def resolve_python_path() -> Optional[str]:
    """Resuelve el intérprete Python para el IDE (portable o sistema)."""
    manager = get_python_manager()
    installed = manager.get_installed_versions()
    if installed:
        version = manager.get_default_version()
        if version not in installed:
            version = installed[0]
        exe = manager.get_python_exe(version)
        if exe:
            path = str(exe)
            os.environ["PM_PYTHON_PATH"] = path
            return path

    dialog = PythonSetupDialog()
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return None
    return os.environ.get("PM_PYTHON_PATH") or dialog._python_path


# =============================================================================
# VENTANA PRINCIPAL DEL EDITOR
# =============================================================================
class EditorWindow(QMainWindow):
    """Ventana principal del editor mini-IDE con menubar completo."""
    
    def __init__(self, file_path=None, project_path=None, python_path=None):
        super().__init__()
        self.file_path = file_path
        self.project_path = project_path
        self.python_path = python_path or os.environ.get("PM_PYTHON_PATH", sys.executable)
        self._auto_check_deps = True
        self._load_editor_config()
        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Aplicar hoja de estilos global
        self.setStyleSheet(DARK_QSS)
        
        # Configurar UI
        self.setup_ui()
        self.setup_menubar()
        self.setup_shortcuts()
        
        # Cargar archivo si se proporciona
        if file_path and os.path.exists(file_path):
            self.open_file(file_path)
            if project_path:
                self.file_explorer.set_project_path(project_path)
            else:
                self.file_explorer.set_project_path(os.path.dirname(file_path))
        elif project_path and os.path.exists(project_path):
            self.file_explorer.set_project_path(project_path)
            self._open_first_python_file(project_path)
        else:
            self.update_title()
        
        # Configurar highlighter
        self.highlighter = PythonHighlighter(self.editor.document())
        self.check_syntax()
        self._update_python_status()
    
    def _open_first_python_file(self, project_path):
        """Abre el primer archivo Python encontrado en el proyecto."""
        for root, _, files in os.walk(project_path):
            for file in sorted(files):
                if file.endswith('.py'):
                    self.open_file(os.path.join(root, file))
                    return
    
    def setup_ui(self):
        """Configura la interfaz con layout de paneles optimizado."""
        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Splitter horizontal (explorador | editor)
        self.h_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panel izquierdo: Explorador de archivos
        self.file_explorer = FileExplorer(self)
        self.file_explorer.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.file_explorer.setMinimumWidth(180)
        self.file_explorer.setMaximumWidth(400)
        self.file_explorer.fileSelected.connect(self.open_file)
        self.h_splitter.addWidget(self.file_explorer)
        
        # Panel central: Editor + Consola
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)
        
        # Editor
        self.editor = CodeEditor()
        self.editor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        center_layout.addWidget(self.editor, 1)
        
        # Panel inferior: Consola
        self.console_panel = ConsolePanel(self)
        self.console_panel.set_python_path(self.python_path)
        get_dependency_manager(self)
        self.console_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.console_panel.setMinimumHeight(120)
        self.console_panel.setMaximumHeight(300)
        center_layout.addWidget(self.console_panel)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        center_layout.addWidget(self.progress_bar)

        self.h_splitter.addWidget(center_widget)
        
        # Configurar tamaños iniciales del splitter
        self.h_splitter.setSizes([250, 950])
        
        layout.addWidget(self.h_splitter)
        
        # Status bar
        self.setup_statusbar()
    
    def setup_menubar(self):
        """Configura el menubar completo con todas las opciones."""
        menubar = self.menuBar()
        
        # === MENÚ ARCHIVO ===
        file_menu = menubar.addMenu("&Archivo")

        dashboard_action = QAction("Volver al &dashboard", self)
        dashboard_action.setShortcut(QKeySequence("Ctrl+Shift+D"))
        dashboard_action.triggered.connect(self.back_to_dashboard)
        file_menu.addAction(dashboard_action)

        file_menu.addSeparator()
        
        new_action = QAction("&Nuevo", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Abrir...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)
        
        open_project_action = QAction("Abrir &Proyecto...", self)
        open_project_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        open_project_action.triggered.connect(self.open_project_dialog)
        file_menu.addAction(open_project_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("&Guardar", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Guardar &como...", self)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Salir", self)
        exit_action.setShortcut(QKeySequence("Alt+F4"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # === MENÚ EDITAR ===
        edit_menu = menubar.addMenu("&Editar")
        
        undo_action = QAction("&Deshacer", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Rehacer", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Cor&tar", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self.editor.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("&Copiar", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.editor.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("&Pegar", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.editor.paste)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        find_action = QAction("&Buscar...", self)
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        find_action.triggered.connect(self.show_find_dialog)
        edit_menu.addAction(find_action)
        
        goto_action = QAction("Ir a línea...", self)
        goto_action.setShortcut(QKeySequence("Ctrl+G"))
        goto_action.triggered.connect(self.goto_line)
        edit_menu.addAction(goto_action)
        
        # === MENÚ VER ===
        view_menu = menubar.addMenu("&Ver")
        
        explorer_action = QAction("Panel &Explorador", self)
        explorer_action.setCheckable(True)
        explorer_action.setChecked(True)
        explorer_action.triggered.connect(self.toggle_explorer)
        view_menu.addAction(explorer_action)
        
        console_action = QAction("Panel &Consola", self)
        console_action.setCheckable(True)
        console_action.setChecked(True)
        console_action.triggered.connect(self.toggle_console)
        view_menu.addAction(console_action)
        
        view_menu.addSeparator()
        
        metrics_action = QAction("&Métricas de código", self)
        metrics_action.triggered.connect(self.show_metrics)
        view_menu.addAction(metrics_action)
        
        # === MENÚ HERRAMIENTAS ===
        tools_menu = menubar.addMenu("Herra&mientas")
        
        run_action = QAction("&Ejecutar script", self)
        run_action.setShortcut(QKeySequence("F5"))
        run_action.triggered.connect(self.run_script)
        tools_menu.addAction(run_action)
        
        tools_menu.addSeparator()
        
        diff_action = QAction("&Comparar archivos (Diff)", self)
        diff_action.triggered.connect(self.show_diff_dialog)
        tools_menu.addAction(diff_action)
        
        diff_current_action = QAction("Comparar con &archivo...", self)
        diff_current_action.triggered.connect(self.diff_current_file)
        tools_menu.addAction(diff_current_action)
        
        tools_menu.addSeparator()
        
        syntax_action = QAction("Verificar &sintaxis", self)
        syntax_action.setShortcut(QKeySequence("F6"))
        syntax_action.triggered.connect(self.check_syntax)
        tools_menu.addAction(syntax_action)

        tools_menu.addSeparator()

        select_interpreter_action = QAction("Seleccionar intérprete Python...", self)
        select_interpreter_action.triggered.connect(self.select_python_interpreter)
        tools_menu.addAction(select_interpreter_action)

        config_interpreter_action = QAction("Configurar intérpretes...", self)
        config_interpreter_action.triggered.connect(self.show_interpreter_config)
        tools_menu.addAction(config_interpreter_action)

        tools_menu.addSeparator()

        check_deps_action = QAction("Verificar &dependencias", self)
        check_deps_action.setShortcut(QKeySequence("F7"))
        check_deps_action.triggered.connect(self.check_dependencies)
        tools_menu.addAction(check_deps_action)

        gen_req_action = QAction("Generar requirements.txt", self)
        gen_req_action.triggered.connect(self.check_dependencies)
        tools_menu.addAction(gen_req_action)
        
        # === MENÚ AYUDA ===
        help_menu = menubar.addMenu("A&yuda")
        
        about_action = QAction("&Acerca de", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        shortcuts_action = QAction("Ata&jos de teclado", self)
        shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts_action)
    
    def setup_statusbar(self):
        """Configura la barra de estado."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.cursor_label = QLabel("Ln 1, Col 1")
        self.status_bar.addWidget(self.cursor_label)
        
        self.status_bar.addWidget(QLabel(" | "))
        
        self.encoding_label = QLabel("UTF-8")
        self.status_bar.addWidget(self.encoding_label)
        
        self.file_type_label = QLabel("Python")
        self.status_bar.addWidget(self.file_type_label)

        self.status_bar.addWidget(QLabel(" | "))

        self.python_label = QLabel("Python: …")
        self.python_label.setToolTip(self.python_path)
        self.status_bar.addWidget(self.python_label)

        self.env_label = QLabel("Entorno: …")
        self.status_bar.addWidget(self.env_label)

        self.deps_label = QLabel("Deps: —")
        self.status_bar.addWidget(self.deps_label)

        self.editor.cursorPositionChanged.connect(self.update_cursor_position)
    
    def setup_shortcuts(self):
        pass
    
    def back_to_dashboard(self):
        from lib.pm_dashboard import DashboardWindow

        python_path = self.python_path or resolve_python_path()
        if not python_path:
            return
        dashboard = DashboardWindow(
            python_path=python_path,
            launch_editor=_open_editor_from_dashboard,
        )
        dashboard.show()
        self.close()

    def new_file(self):
        self.file_path = None
        self.editor.setPlainText("")
        self.update_title()
        self.highlighter.error_lines.clear()
        self.highlighter.rehighlight()
    
    def open_project_dialog(self):
        from PyQt6.QtWidgets import QFileDialog
        path = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de proyecto")
        if path:
            self.project_path = path
            self.file_explorer.set_project_path(path)
            self._open_first_python_file(path)
    
    def open_file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Abrir archivo", "",
            "Todos los archivos (*.*)"
        )
        if path:
            self.open_file(path)
    
    def open_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.editor.setPlainText(f.read())
            self.file_path = path
            self.update_title()
            self.status_bar.showMessage(f"Abierto: {os.path.basename(path)}", 3000)
            self.check_syntax()
            
            ext = os.path.splitext(path)[1].lower()
            type_map = {
                '.py': 'Python', '.txt': 'Texto', '.md': 'Markdown',
                '.json': 'JSON', '.xml': 'XML', '.yaml': 'YAML', '.yml': 'YAML'
            }
            self.file_type_label.setText(type_map.get(ext, 'Texto'))

            if ext == '.py' and self._auto_check_deps:
                QTimer.singleShot(500, self.check_dependencies)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo:\n{e}")

    def _update_python_status(self):
        """Actualiza etiquetas de Python/entorno en la barra de estado."""
        py = self.python_path
        portable_root = str(Path(__file__).resolve().parent / "data" / "pmCodeEditor")
        is_portable = portable_root.replace("\\", "/") in py.replace("\\", "/")
        self.env_label.setText("Portable" if is_portable else "Sistema")
        self.python_label.setToolTip(py)
        try:
            result = subprocess.run(
                [py, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            version = (result.stdout or result.stderr or "").strip()
            short = Path(py).name
            self.python_label.setText(f"Python: {version or short}")
        except (subprocess.TimeoutExpired, OSError):
            self.python_label.setText(f"Python: {Path(py).name}")

    def _load_editor_config(self):
        if not EDITOR_CONFIG_PATH.exists():
            return
        try:
            with open(EDITOR_CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            self._auto_check_deps = cfg.get("auto_check", True)
            if cfg.get("default_interpreter") and os.path.isfile(cfg["default_interpreter"]):
                self.python_path = cfg["default_interpreter"]
                os.environ["PM_PYTHON_PATH"] = self.python_path
            dep = get_dependency_manager(self)
            dep.exclude_pyqt = cfg.get("exclude_pyqt", True)
            dep.exclude_local = cfg.get("exclude_local", True)
        except (json.JSONDecodeError, OSError):
            pass

    def _save_editor_config(self, settings: dict):
        EDITOR_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(EDITOR_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)

    def show_interpreter_config(self):
        from lib.interpreter_config_dialog import InterpreterConfigDialog

        dialog = InterpreterConfigDialog(self, self.python_path)
        dialog.apply_editor_settings({
            "exclude_pyqt": get_dependency_manager(self).exclude_pyqt,
            "exclude_local": get_dependency_manager(self).exclude_local,
            "auto_check": self._auto_check_deps,
            "default_interpreter": self.python_path,
        })

        def on_interpreter_changed(new_path: str):
            self._apply_python_interpreter(new_path)

        dialog.interpreter_changed.connect(on_interpreter_changed)
        dialog.exec()

        settings = dialog.get_settings()
        self._auto_check_deps = settings["auto_check"]
        dep = get_dependency_manager(self)
        dep.exclude_pyqt = settings["exclude_pyqt"]
        dep.exclude_local = settings["exclude_local"]
        if settings.get("default_interpreter"):
            self._apply_python_interpreter(settings["default_interpreter"])
        self._save_editor_config(settings)

    def check_dependencies(self):
        """Verifica e instala dependencias del script actual."""
        if not self.file_path or not self.file_path.endswith(".py"):
            self.console_panel.append_output("[DEP] Abra un archivo .py para verificar dependencias")
            return

        self.console_panel.append_output(
            f"[DEP] Analizando {os.path.basename(self.file_path)}..."
        )
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.deps_label.setText("Deps: verificando…")

        dep = get_dependency_manager(self)
        dep.check_and_install(
            self.file_path,
            self.python_path,
            self._on_dependency_check_finished,
        )

    def _on_dependency_check_finished(self, success: bool, message: str):
        self.progress_bar.setVisible(False)
        mark = "OK" if success else "ERR"
        self.console_panel.append_output(f"[DEP] [{mark}] {message}")
        self.deps_label.setText(f"Deps: {'OK' if success else 'pendiente'}")
    
    def save_file(self):
        if self.file_path:
            self._write_file(self.file_path)
        else:
            self.save_file_as()
    
    def save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar archivo", "",
            "Todos los archivos (*.*)"
        )
        if path:
            self._write_file(path)
            self.file_path = path
            self.update_title()
    
    def _write_file(self, path):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            self.status_bar.showMessage(f"Guardado: {os.path.basename(path)}", 3000)
            self.console_panel.append_output(f"Archivo guardado: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar:\n{e}")
    
    def show_find_dialog(self):
        dialog = FindDialog(self.editor, self)
        dialog.show()
    
    def goto_line(self):
        line, ok = QInputDialog.getInt(self, "Ir a línea", "Número de línea:", 1, 1, 999999)
        if ok:
            cursor = self.editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            for _ in range(line - 1):
                cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
            self.editor.setTextCursor(cursor)
    
    def toggle_console(self, checked):
        self.console_panel.setVisible(checked)
    
    def toggle_explorer(self, checked):
        self.file_explorer.setVisible(checked)
    
    def show_metrics(self):
        dialog = MetricsDialog(self.editor.toPlainText(), self.file_path, self)
        dialog.exec()
    
    def _get_available_interpreters(self) -> List[Tuple[str, str]]:
        """Lista de intérpretes disponibles: (nombre, ruta)."""
        interpreters: List[Tuple[str, str]] = []
        seen = set()

        manager = get_python_manager()
        for version in manager.get_installed_versions():
            python_exe = manager.get_python_exe(version)
            if python_exe and python_exe.exists():
                path = str(python_exe)
                if path not in seen:
                    interpreters.append((f"Python {version} (Portable)", path))
                    seen.add(path)

        for label, finder in (
            ("Python del sistema", "python"),
            ("Python3 del sistema", "python3"),
        ):
            found = shutil.which(finder)
            if found and found not in seen:
                interpreters.append((label, found))
                seen.add(found)

        current = sys.executable
        if current not in seen:
            interpreters.append((f"Python del editor ({sys.version_info.major}.{sys.version_info.minor})", current))
            seen.add(current)

        if self.python_path and self.python_path not in seen:
            interpreters.append(("Python seleccionado", self.python_path))

        return interpreters

    def _select_python_interpreter(self) -> Optional[str]:
        """Diálogo para elegir intérprete cuando hay varios disponibles."""
        interpreters = self._get_available_interpreters()
        if not interpreters:
            QMessageBox.warning(self, "Error", "No hay intérpretes de Python disponibles.")
            return None
        if len(interpreters) == 1:
            return interpreters[0][1]

        dialog = QDialog(self)
        dialog.setWindowTitle("Seleccionar intérprete Python")
        dialog.setMinimumWidth(520)
        dialog.setStyleSheet(DARK_QSS)

        layout = QVBoxLayout(dialog)
        label = QLabel("Selecciona el intérprete para ejecutar el script:")
        layout.addWidget(label)

        list_widget = QListWidget()
        current_path = os.path.normpath(self.python_path)
        for i, (name, path) in enumerate(interpreters):
            item = QListWidgetItem(f"{name}\n{path}")
            item.setData(Qt.ItemDataRole.UserRole, path)
            list_widget.addItem(item)
            if os.path.normpath(path) == current_path:
                list_widget.setCurrentRow(i)
        layout.addWidget(list_widget)

        btn_row = QHBoxLayout()
        btn_download = QPushButton("Descargar otro intérprete...")
        btn_download.clicked.connect(lambda: self._download_new_interpreter(dialog))
        btn_row.addWidget(btn_download)
        btn_row.addStretch()
        btn_ok = QPushButton("Usar seleccionado")
        btn_ok.setDefault(True)
        btn_cancel = QPushButton("Cancelar")
        btn_ok.clicked.connect(dialog.accept)
        btn_cancel.clicked.connect(dialog.reject)
        btn_row.addWidget(btn_ok)
        btn_row.addWidget(btn_cancel)
        layout.addLayout(btn_row)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        selected = list_widget.currentItem()
        if not selected:
            return None
        return selected.data(Qt.ItemDataRole.UserRole)

    def select_python_interpreter(self):
        """Menú: elegir intérprete y aplicarlo al editor."""
        path = self._select_python_interpreter()
        if path:
            self._apply_python_interpreter(path)

    def _apply_python_interpreter(self, python_path: str):
        self.python_path = python_path
        os.environ["PM_PYTHON_PATH"] = python_path
        self.console_panel.set_python_path(python_path)
        self._update_python_status()
        self.status_bar.showMessage(f"Intérprete: {python_path}", 5000)

    def _download_new_interpreter(self, parent_dialog: Optional[QDialog] = None):
        if parent_dialog:
            parent_dialog.reject()
        setup_dialog = PythonSetupDialog(self)

        def on_setup_complete(success: bool, path: str):
            if success:
                self._apply_python_interpreter(path)
                self.console_panel.append_output(f"[INFO] Nuevo intérprete: {path}")

        setup_dialog.setup_complete.connect(on_setup_complete)
        setup_dialog.exec()

    def run_script(self):
        if not self.file_path:
            QMessageBox.warning(self, "Advertencia", "Guarde el archivo antes de ejecutar.")
            return

        python_path = self._select_python_interpreter()
        if not python_path:
            return

        self._apply_python_interpreter(python_path)

        self.console_panel.clear()
        self.console_panel.append_output(f"Ejecutando: {self.file_path}")
        self.console_panel.append_output(f"Usando Python: {python_path}")

        cmd = [python_path, self.file_path]
        self.console_panel.run_command_list(cmd, os.path.dirname(self.file_path))
    
    def check_syntax(self):
        code = self.editor.toPlainText()
        if not code.strip():
            return
        
        try:
            compile(code, '<string>', 'exec')
            self.highlighter.error_lines.clear()
            self.highlighter.rehighlight()
            self.status_bar.showMessage("Sintaxis OK", 2000)
        except SyntaxError as e:
            line_num = e.lineno - 1 if e.lineno else 0
            self.highlighter.set_error_line(line_num)
            self.status_bar.showMessage(f"Error de sintaxis en línea {e.lineno}: {e.msg}", 5000)
            self.console_panel.append_output(
                f"Error de sintaxis: {e.msg} (línea {e.lineno})", is_error=True
            )
    
    def show_diff_dialog(self):
        dialog = DiffDialog(self)
        dialog.exec()
    
    def diff_current_file(self):
        if not self.file_path:
            QMessageBox.warning(self, "Advertencia", "Guarde el archivo antes de comparar.")
            return
        
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo para comparar")
        if path:
            dialog = DiffDialog(self)
            dialog.compare_with_content(path, self.editor.toPlainText())
            dialog.exec()
    
    def show_about(self):
        QMessageBox.about(self, f"Acerca de {APP_NAME}",
            f"<h2>{APP_NAME} v{VERSION}</h2>"
            f"<p>Editor de código profesional para PackageMaker</p>"
            f"<p>Características:</p>"
            f"<ul>"
            f"<li>Resaltado de sintaxis avanzado</li>"
            f"<li>Explorador de proyecto integrado</li>"
            f"<li>Sistema Diff integrado</li>"
            f"<li>Métricas de código</li>"
            f"<li>Consola mejorada con soporte ANSI</li>"
            f"</ul>"
        )
    
    def show_shortcuts(self):
        shortcuts = [
            ("Ctrl+N", "Nuevo archivo"),
            ("Ctrl+O", "Abrir archivo"),
            ("Ctrl+S", "Guardar"),
            ("Ctrl+Shift+S", "Guardar como"),
            ("Ctrl+Z", "Deshacer"),
            ("Ctrl+Y", "Rehacer"),
            ("Ctrl+X", "Cortar"),
            ("Ctrl+C", "Copiar"),
            ("Ctrl+V", "Pegar"),
            ("Ctrl+F", "Buscar"),
            ("Ctrl+G", "Ir a línea"),
            ("F5", "Ejecutar script"),
            ("F6", "Verificar sintaxis"),
        ]
        
        text = "<h2>Atajos de teclado</h2><tr>"
        for key, desc in shortcuts:
            text += f"<tr><td><b>{key}</b></td><td>{desc}</td></tr>"
        text += "</table>"
        
        QMessageBox.information(self, "Atajos de teclado", text)
    
    def update_cursor_position(self):
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.cursor_label.setText(f"Ln {line}, Col {col}")
    
    def update_title(self):
        name = os.path.basename(self.file_path) if self.file_path else "Sin título"
        self.setWindowTitle(f"{name} - {APP_NAME} v{VERSION}")
    
    def closeEvent(self, event):
        if hasattr(self, 'console_panel') and self.console_panel._process:
            if self.console_panel._process.state() != QProcess.ProcessState.NotRunning:
                self.console_panel._process.terminate()
                self.console_panel._process.waitForFinished(1000)
        event.accept()


# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================
def _open_editor_from_dashboard(file_path, project_path, python_path):
    """Abre el editor de codigo y cierra el dashboard."""
    editor = EditorWindow(
        file_path=file_path,
        project_path=project_path,
        python_path=python_path,
    )
    editor.show()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_QSS)

    python_path = resolve_python_path()
    if not python_path:
        print("[INFO] Configuracion de Python cancelada")
        sys.exit(0)

    file_arg = None
    project_arg = None

    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if os.path.isfile(arg):
            file_arg = arg
        elif os.path.isdir(arg):
            project_arg = arg
        else:
            project_path = find_flarm_project(arg)
            if project_path:
                project_arg = project_path
                print(f"[INFO] Proyecto FLARM encontrado: {project_path}")
            else:
                print(f"[AVISO] No se encontro el archivo o proyecto: {arg}")

    if file_arg or project_arg:
        window = EditorWindow(
            file_path=file_arg,
            project_path=project_arg,
            python_path=python_path,
        )
        window.show()
    else:
        from lib.pm_dashboard import DashboardWindow

        dashboard = DashboardWindow(
            python_path=python_path,
            launch_editor=_open_editor_from_dashboard,
        )
        dashboard.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

