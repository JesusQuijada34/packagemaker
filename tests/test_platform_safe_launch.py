import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from lib import tui
from lib.editorDetector import EditorInfo, EditorDetector
from lib.projectDetailsDialog import _open_path_in_file_manager


class PlatformSafeLaunchTests(unittest.TestCase):
    def test_editor_launch_uses_argument_list_without_shell(self):
        detector = EditorDetector.__new__(EditorDetector)
        detector.platform = "win32"
        editor = EditorInfo(
            name="code",
            display_name="Code",
            executable="Code.exe",
            command_template='"{exe}" "{path}"',
        )
        executable = r"C:\Program Files\Editor\Code.exe"
        project = r"C:\Users\User Name\project & data"

        with patch("subprocess.Popen") as popen:
            self.assertTrue(detector.launch_editor(editor, executable, project))

        popen.assert_called_once_with(
            [executable, project], shell=False, close_fds=False
        )

    @patch("subprocess.Popen")
    def test_linux_folder_open_uses_xdg_open(self, popen):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(sys, "platform", "linux"):
                _open_path_in_file_manager(Path(temp_dir) / "folder with spaces")

        popen.assert_called_once()
        args, kwargs = popen.call_args
        self.assertEqual(args[0][0], "xdg-open")
        self.assertTrue(args[0][1].endswith("folder with spaces"))
        self.assertEqual(kwargs, {"close_fds": True})

    @patch("lib.tui.subprocess.Popen")
    @patch("lib.tui._pause")
    @patch("lib.tui._ok")
    def test_tui_folder_open_uses_argument_list(self, mock_ok, mock_pause, popen):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir) / "folder with spaces"
            folder.mkdir()
            with patch.object(tui.sys, "platform", "linux"):
                tui._open_folder(folder)

        popen.assert_called_once_with(["xdg-open", str(folder.resolve())], close_fds=True)
        mock_ok.assert_called_once()
        mock_pause.assert_called_once()


if __name__ == "__main__":
    unittest.main()
