import inspect
import unittest

try:
    from PyQt6 import QtGui
    from lib.outputTerminalDialog import OutputTerminalDialog
except ImportError:  # PyQt6 es opcional para la suite headless.
    QtGui = None
    OutputTerminalDialog = None


@unittest.skipUnless(QtGui is not None, "PyQt6 no está instalado en este entorno")
class OutputTerminalDialogQt6Tests(unittest.TestCase):
    def test_output_handlers_use_qt6_cursor_move_operation(self):
        self.assertTrue(hasattr(QtGui.QTextCursor.MoveOperation, "End"))
        source = inspect.getsource(OutputTerminalDialog)
        self.assertEqual(source.count("QTextCursor.MoveOperation.End"), 2)
        self.assertNotIn("QTextCursor.End", source)


if __name__ == "__main__":
    unittest.main()
