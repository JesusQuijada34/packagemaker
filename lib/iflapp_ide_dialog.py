# -*- coding: utf-8 -*-
"""IDE visual de proyectos ``iflapp``.

Editor nuevo que reúne, sobre el motor de ``lib.iflapp_ide``:

* árbol del proyecto (guiones y metadatos de ``details.xml``),
* editor de código con resaltado del guion activo,
* compilación con los motores base de ``packagemaker`` (selector de backend),
* depurador por línea con puntos de ruptura, ejecución y consola.

Todo el estado sin GUI vive en ``lib.iflapp_ide``; aquí solo se orquesta.
"""
from __future__ import annotations

import os

try:
    from PyQt6.QtWidgets import (
        QDialog,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QLabel,
        QPlainTextEdit,
        QPushButton,
        QListWidget,
        QListWidgetItem,
        QFileDialog,
        QSplitter,
        QComboBox,
    )
    from PyQt6.QtCore import Qt, pyqtSignal
    PYQT6_AVAILABLE = True
except ImportError:  # pragma: no cover - entorno sin GUI
    PYQT6_AVAILABLE = False

    class QWidget:  # type: ignore
        def __init__(self, *args, **kwargs):
            raise ImportError("El IDE de proyectos iflapp requiere PyQt6.")

    class QDialog:  # type: ignore
        def __init__(self, *args, **kwargs):
            raise ImportError("El IDE de proyectos iflapp requiere PyQt6.")

from lib.i18n import tr
from lib.iflapp_ide import (
    IfappProject,
    compile_project,
    debug_script,
    detect_hidden_imports,
    run_script,
    scan_project,
)


class IflappIdePanel(QWidget):
    """Panel del IDE: se embebe en la página del sidebar y en el diálogo."""

    close_requested = pyqtSignal()

    def __init__(self, parent=None, project_root: str | None = None):
        super().__init__(parent)
        self.project: IfappProject | None = None
        self.breakpoints: set[int] = set()
        self._build_ui()
        if project_root:
            self.load_project(project_root)

    # ── Construcción ─────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        self.setObjectName("IflappIdePanel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        top = QHBoxLayout()
        self.header = QLabel(tr("iflapp_ide.no_project"))
        self.header.setObjectName("IflappIdeHeader")
        top.addWidget(self.header)
        top.addStretch()
        self.btn_open = QPushButton(tr("iflapp_ide.open"))
        self.btn_open.clicked.connect(self.choose_project)
        top.addWidget(self.btn_open)
        self.btn_open_with = QPushButton(tr("iflapp_ide.open_with"))
        self.btn_open_with.setToolTip(tr("iflapp_ide.open_with_hint"))
        self.btn_open_with.clicked.connect(self.open_with_package_maker)
        self.btn_open_with.setEnabled(False)
        top.addWidget(self.btn_open_with)
        layout.addLayout(top)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.tree = QListWidget()
        self.tree.currentTextChanged.connect(self._on_script_selected)
        splitter.addWidget(self.tree)

        self.editor = QPlainTextEdit()
        self.editor.setObjectName("IflappIdeEditor")
        splitter.addWidget(self.editor)
        splitter.setSizes([240, 760])
        layout.addWidget(splitter)

        controls = QHBoxLayout()
        controls.addWidget(QLabel(tr("iflapp_ide.backend")))
        self.backend_selector = QComboBox()
        for name in ("auto", "nuitka", "pyinstaller", "zipapp"):
            self.backend_selector.addItem(name)
        controls.addWidget(self.backend_selector)

        self.btn_compile = QPushButton(tr("iflapp_ide.compile"))
        self.btn_compile.clicked.connect(self.run_compile)
        controls.addWidget(self.btn_compile)

        self.btn_run = QPushButton(tr("iflapp_ide.run"))
        self.btn_run.clicked.connect(self.run_current)
        controls.addWidget(self.btn_run)

        self.btn_debug = QPushButton(tr("iflapp_ide.debug"))
        self.btn_debug.clicked.connect(self.debug_current)
        controls.addWidget(self.btn_debug)

        self.btn_break = QPushButton(tr("iflapp_ide.breakpoint"))
        self.btn_break.clicked.connect(self.toggle_breakpoint)
        controls.addWidget(self.btn_break)
        controls.addStretch()
        layout.addLayout(controls)

        self.console = QListWidget()
        self.console.setMaximumHeight(150)
        layout.addWidget(self.console)

        bottom = QHBoxLayout()
        self.status = QLabel(tr("iflapp_ide.ready"))
        self.status.setObjectName("IflappIdeStatus")
        bottom.addWidget(self.status)
        bottom.addStretch()
        self.btn_close = QPushButton(tr("common.close"))
        self.btn_close.clicked.connect(self.close_requested.emit)
        bottom.addWidget(self.btn_close)
        layout.addLayout(bottom)

        self.meta_label = QLabel("")
        self.meta_label.setObjectName("IflappIdeMetadata")
        self.meta_label.setProperty("role", "monospace")
        layout.addWidget(self.meta_label)

    # ── Carga de proyecto ────────────────────────────────────────────────
    def choose_project(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, tr("iflapp_ide.open"))
        if folder:
            self.load_project(folder)

    def load_project(self, root: str) -> bool:
        try:
            self.project = scan_project(root)
        except (FileNotFoundError, OSError) as exc:
            self.status.setText(tr("iflapp_ide.load_failed").format(error=exc))
            return False
        self.header.setText(str(self.project.root))
        self._refresh_tree()
        self._refresh_metadata()
        self.btn_open_with.setEnabled(True)
        self.console.clear()
        self.status.setText(
            tr("iflapp_ide.loaded").format(count=len(self.project.scripts))
        )
        return True

    def open_with_package_maker(self) -> bool:
        """Abre el proyecto seleccionado mediante el diálogo oficial.

        El IDE mantiene una única raíz activa; el diálogo decide qué editor
        registrado se usa y conserva la preferencia por proyecto.
        """
        if self.project is None:
            self.status.setText(tr("iflapp_ide.no_project"))
            return False
        from lib.openWithDialog import open_project_with_editor

        opened = open_project_with_editor(
            self,
            str(self.project.root),
            self.project.root.name,
            use_default=False,
        )
        if opened:
            self.status.setText(tr("iflapp_ide.opened_with"))
        return bool(opened)

    def _refresh_tree(self) -> None:
        self.tree.clear()
        if self.project is None:
            return
        for script in self.project.scripts:
            self.tree.addItem(QListWidgetItem(script))
        if self.tree.count():
            self.tree.setCurrentRow(0)

    def _refresh_metadata(self) -> None:
        if self.project is None:
            self.meta_label.setText("")
            return
        meta = self.project.metadata
        self.meta_label.setText(
            f"{meta.get('publisher', '?')}.{meta.get('app', '?')}  "
            f"{meta.get('version', '?')}  {meta.get('platform', '?')}"
            + (f"   faltan: {', '.join(self.project.missing)}" if self.project.missing else "")
        )

    def _on_script_selected(self, name: str) -> None:
        if not name or self.project is None:
            return
        path = self.project.root / name
        if path.is_file():
            self.editor.setPlainText(path.read_text(encoding="utf-8-sig"))

    def current_script(self) -> str | None:
        item = self.tree.currentItem()
        return item.text() if item else None

    def _current_path(self):
        name = self.current_script()
        if not name or self.project is None:
            return None
        return self.project.root / name

    # ── Acciones ─────────────────────────────────────────────────────────
    def run_compile(self) -> bool:
        if self.project is None:
            self.status.setText(tr("iflapp_ide.no_project"))
            return False
        backend = self.backend_selector.currentText()
        outcome = compile_project(
            self.project.root,
            backend=None if backend == "auto" else backend,
            log=self._log,
        )
        for line in outcome.log:
            self.console.addItem(line)
        if outcome.ok:
            self.status.setText(
                tr("iflapp_ide.compiled").format(count=len(outcome.outputs), backend=outcome.backend)
            )
            return True
        self.status.setText(tr("iflapp_ide.compile_failed").format(error="; ".join(outcome.failures)))
        return False

    def run_current(self) -> None:
        path = self._current_path()
        if path is None:
            self.status.setText(tr("iflapp_ide.no_script"))
            return
        code, output = run_script(path)
        for line in output.splitlines():
            self.console.addItem(line)
        self.status.setText(
            tr("iflapp_ide.ran").format(code=code)
            if code == 0
            else tr("iflapp_ide.run_failed").format(code=code)
        )

    def debug_current(self) -> None:
        path = self._current_path()
        if path is None:
            self.status.setText(tr("iflapp_ide.no_script"))
            return
        outcome = debug_script(path, breakpoints=self.breakpoints or None)
        if outcome.error:
            self.status.setText(tr("iflapp_ide.run_failed").format(code=outcome.error))
            return
        for stop in outcome.stops:
            variables = ", ".join(f"{k}={v!r}" for k, v in list(stop.locals.items())[:6])
            self.console.addItem(f"L{stop.line} {stop.function}  {variables}")
        if not outcome.stops:
            self.console.addItem(tr("iflapp_ide.no_stops"))
        self.status.setText(tr("iflapp_ide.debugged").format(count=len(outcome.stops)))

    def toggle_breakpoint(self) -> None:
        line = self.editor.textCursor().blockNumber() + 1
        if line in self.breakpoints:
            self.breakpoints.discard(line)
            self.console.addItem(tr("iflapp_ide.break_off").format(line=line))
        else:
            self.breakpoints.add(line)
            self.console.addItem(tr("iflapp_ide.break_on").format(line=line))

    def hidden_imports(self) -> list[str]:
        path = self._current_path()
        return detect_hidden_imports(path) if path else []

    def _log(self, message: str) -> None:
        self.console.addItem(str(message))


class IflappIdeDialog(QDialog):
    """Diálogo contenedor del panel del IDE (para abrirlo desde menús)."""

    def __init__(self, parent=None, project_root: str | None = None):
        super().__init__(parent)
        self.setWindowTitle(tr("iflapp_ide.title"))
        self.resize(1080, 700)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.panel = IflappIdePanel(self, project_root=project_root)
        self.panel.close_requested.connect(self.reject)
        layout.addWidget(self.panel)


def open_iflapp_ide(parent=None, project_root: str | None = None) -> "IflappIdeDialog":
    """Abre el IDE de proyectos, cargando la carpeta indicada si existe."""
    if project_root and not os.path.isdir(project_root):
        project_root = None
    dialog = IflappIdeDialog(parent, project_root=project_root)
    dialog.exec()
    return dialog
