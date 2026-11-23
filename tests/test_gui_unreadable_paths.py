# -*- coding: utf-8 -*-
"""La GUI no debe caer con rutas sin permisos (R-9e3b7a51).

Tres acciones de ventana comprobaban rutas con ``Path.exists()``/``is_file()``
dentro de un slot de Qt. En Python 3.13 esas llamadas propagan
``PermissionError``, así que una carpeta base de solo lectura o un guion que el
usuario no puede leer terminaban en traceback en lugar de mostrar el aviso.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PyQt6.QtWidgets import QApplication
except ImportError:  # pragma: no cover
    QApplication = None

_UNREADABLE_SKIP = unittest.skipIf(
    os.name == "nt" or (hasattr(os, "geteuid") and os.geteuid() == 0),
    "los permisos POSIX no bloquean la lectura en Windows ni como root",
)

_APP = None


def _ensure_app():
    global _APP
    if QApplication is None:
        raise unittest.SkipTest("PyQt6 no disponible")
    if _APP is None:
        _APP = QApplication.instance() or QApplication([])
    return _APP


def _restore(path: Path, mode: int = 0o755) -> None:
    try:
        path.chmod(mode)
    except OSError:
        pass


@unittest.skipIf(QApplication is None, "PyQt6 no disponible")
class GuiUnreadablePathTests(unittest.TestCase):
    def setUp(self):
        _ensure_app()

    @_UNREADABLE_SKIP
    def test_new_project_wizard_reports_unwritable_base(self):
        from lib.pm_dashboard import NewProjectWizard

        base = Path(tempfile.mkdtemp()) / "locked"
        base.mkdir()
        base.chmod(0o000)
        try:
            wizard = NewProjectWizard()
            wizard.input_publisher.setText("Influent")
            wizard.input_app.setText("demo")
            wizard.input_name.setText("Demo")
            wizard.input_location.setText(str(base))
            notes = []
            with patch.object(wizard, "_notify", lambda *args, **kwargs: notes.append(args)):
                wizard.create_project()
            self.assertTrue(notes, "el fallo debe avisarse al usuario")
            self.assertEqual(notes[0][0], "error")
            self.assertIsNone(wizard.get_project_path())
        finally:
            _restore(base)

    @_UNREADABLE_SKIP
    def test_ide_panel_reports_unreadable_script(self):
        from lib.iflapp_ide_dialog import IflappIdePanel

        root = Path(tempfile.mkdtemp()) / "proj"
        root.mkdir()
        (root / "details.xml").write_text(
            "<app><publisher>Influent</publisher><app>demo</app>"
            "<version>v1.0</version></app>",
            encoding="utf-8",
        )
        script = root / "demo.py"
        script.write_text("print('hola')\n", encoding="utf-8")

        panel = IflappIdePanel()
        self.assertTrue(panel.load_project(str(root)))
        script.chmod(0o000)
        try:
            panel._on_script_selected("demo.py")
            self.assertEqual(panel.editor.toPlainText(), "")
            self.assertTrue(panel.status.text(), "debe informar del fallo de lectura")
        finally:
            _restore(script, 0o644)

    @_UNREADABLE_SKIP
    def test_ide_panel_reports_unreadable_project_on_compile(self):
        from lib.iflapp_ide_dialog import IflappIdePanel

        root = Path(tempfile.mkdtemp()) / "proj"
        root.mkdir()
        (root / "details.xml").write_text(
            "<app><publisher>Influent</publisher><app>demo</app>"
            "<version>v1.0</version></app>",
            encoding="utf-8",
        )
        (root / "demo.py").write_text("print('hola')\n", encoding="utf-8")

        panel = IflappIdePanel()
        self.assertTrue(panel.load_project(str(root)))
        root.chmod(0o000)
        try:
            self.assertFalse(panel.run_compile())
            self.assertTrue(panel.status.text(), "debe informar del fallo de compilación")
        finally:
            _restore(root)

    @_UNREADABLE_SKIP
    def test_moonfix_reports_unwritable_project(self):
        from lib.moonFixWizard import MoonFixWizard

        proj = Path(tempfile.mkdtemp()) / "moonproj"
        proj.mkdir()
        wizard = MoonFixWizard(
            None,
            [{"path": str(proj), "issues": [{"type": "missing_dir", "path": "app"}]}],
        )
        proj.chmod(0o500)
        try:
            with patch("lib.moonFixWizard.LeviathanDialog.launch") as launch:
                self.assertFalse(wizard.apply_project_fixes(0))
            self.assertTrue(launch.called, "el fallo debe avisarse al usuario")
        finally:
            _restore(proj)

    @_UNREADABLE_SKIP
    def test_project_config_tolerates_unwritable_base(self):
        from lib.projectConfig import ProjectConfig

        base = Path(tempfile.mkdtemp()) / "locked"
        base.mkdir()
        base.chmod(0o000)
        try:
            config = ProjectConfig(str(base))
            self.assertEqual(config.get_config(), {})
            config.set_editor_path("demo", "/bin/true")
        finally:
            _restore(base)


if __name__ == "__main__":
    unittest.main()
