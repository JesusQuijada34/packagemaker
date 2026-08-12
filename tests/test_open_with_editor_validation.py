import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from lib.openWithDialog import check_executable_exists, launch_editor_or_default


class OpenWithEditorValidationTests(unittest.TestCase):
    def test_directory_is_not_accepted_as_an_editor(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.assertFalse(check_executable_exists(temp_dir))

    def test_posix_executable_file_is_accepted(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            executable = Path(temp_dir) / "editor"
            executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            executable.chmod(0o755)
            self.assertTrue(check_executable_exists(str(executable)))

    @patch("lib.openWithDialog._open_with_system_default", return_value=True)
    @patch("lib.openWithDialog.subprocess.Popen")
    def test_invalid_editor_uses_system_fallback(self, popen, fallback):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.assertTrue(launch_editor_or_default(temp_dir, temp_dir))
        popen.assert_not_called()
        fallback.assert_called_once()


if __name__ == "__main__":
    unittest.main()
