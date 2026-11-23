# -*- coding: utf-8 -*-
"""El editor ``.mexf`` con debugger: lint, puntos de ruptura y pasos (GUI)."""
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PyQt6.QtWidgets import QApplication
except ImportError:  # pragma: no cover
    QApplication = None

from lib.mexf_editor_dialog import MexfEditorDialog  # noqa: E402

_APP = None


def _ensure_app():
    global _APP
    if QApplication is None:
        raise unittest.SkipTest("PyQt6 no disponible")
    if _APP is None:
        _APP = QApplication.instance() or QApplication([])
    return _APP


SOURCE = """format: mexf
version: 1
metadata:
  id: influent.demo
  name: Demo
  version: v1.0
commands:
  - id: demo.uno
    executable: uno
    args: [a]
  - id: demo.dos
    executable: dos
    args: []
"""


@unittest.skipIf(QApplication is None, "PyQt6 no disponible")
class MexfEditorDialogTests(unittest.TestCase):
    def setUp(self):
        _ensure_app()

    def test_valid_source_has_no_diagnostics(self):
        dialog = MexfEditorDialog(source=SOURCE)
        self.assertTrue(dialog.run_lint())
        self.assertEqual(dialog.diagnostics.count(), 0)

    def test_invalid_source_reports_diagnostic(self):
        dialog = MexfEditorDialog(source="format: mexf\nversion: 1\n")
        self.assertFalse(dialog.run_lint())
        self.assertGreaterEqual(dialog.diagnostics.count(), 1)

    def test_breakpoint_selector_lists_commands(self):
        dialog = MexfEditorDialog(source=SOURCE)
        items = [dialog.break_selector.itemText(i) for i in range(dialog.break_selector.count())]
        self.assertEqual(items, ["demo.uno", "demo.dos"])

    def test_toggle_breakpoint_records_state(self):
        dialog = MexfEditorDialog(source=SOURCE)
        dialog.break_selector.setCurrentText("demo.dos")
        dialog.toggle_breakpoint()
        self.assertEqual(dialog.debugger.breakpoints, ["demo.dos"])
        dialog.toggle_breakpoint()
        self.assertEqual(dialog.debugger.breakpoints, [])

    def test_step_executes_one_command_at_a_time(self):
        from lib.mexf_debugger import MexfDebugger

        dialog = MexfEditorDialog(source=SOURCE)
        dialog.debugger = MexfDebugger(dialog._document(), runner=lambda *a, **k: (0, "ok"))
        dialog.debugger.start()
        dialog._debug_step(False)
        self.assertEqual(dialog.debugger.frames[0].command_id, "demo.uno")

    def test_stop_debug_clears_session(self):
        dialog = MexfEditorDialog(source=SOURCE)
        dialog.debugger = dialog._ensure_debugger()
        dialog.stop_debug()
        self.assertIsNone(dialog.debugger)

    def test_invalid_yaml_does_not_break_debug_controls(self):
        """R-5d8f1c36: un YAML a medio escribir no debe reventar en los slots."""
        dialog = MexfEditorDialog(source="format: mexf\nversion: 1\nmetadata: [unclosed\n")
        self.assertEqual(dialog._document(), {})
        debugger = dialog._ensure_debugger()
        self.assertEqual(debugger.commands, [])
        dialog._debug_step(False)
        dialog._debug_step(True)
        self.assertIsNone(dialog.debugger)
        self.assertGreaterEqual(dialog.debug_output.count(), 2)


if __name__ == "__main__":
    unittest.main()
