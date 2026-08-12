import inspect
import unittest

from PyQt6 import QtGui

from lib.outputTerminalDialog import OutputTerminalDialog


class OutputTerminalDialogQt6Tests(unittest.TestCase):
    def test_output_handlers_use_qt6_cursor_move_operation(self):
        self.assertTrue(hasattr(QtGui.QTextCursor.MoveOperation, "End"))
        source = inspect.getsource(OutputTerminalDialog)
        self.assertEqual(source.count("QTextCursor.MoveOperation.End"), 2)
        self.assertNotIn("QTextCursor.End", source)


if __name__ == "__main__":
    unittest.main()
