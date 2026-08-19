import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from lib import tui


class TuiBuildCommandTests(unittest.TestCase):
    def test_build_project_command_uses_project_path(self):
        project_path = Path("C:/tmp/demo-project")
        command = tui._build_project_command(project_path, python_exe="python")

        self.assertEqual(command[0], "python")
        self.assertEqual(command[1], str(Path(os.getcwd()) / "packagemaker.py"))
        self.assertEqual(command[2:], ["--buildthis", str(project_path)])

    @patch("lib.tui._run_live")
    @patch("lib.tui._detect_platform")
    @patch("lib.tui._pause")
    @patch("lib.tui._info")
    @patch("lib.tui._ok")
    def test_build_project_direct_uses_correct_command(
        self, mock_ok, mock_info, mock_pause, mock_detect_platform, mock_run_live
    ):
        project_path = Path("C:/tmp/demo-project")
        mock_detect_platform.return_value = "Knosthalij"
        mock_run_live.return_value = 0

        tui._build_project_direct(project_path)

        mock_run_live.assert_called_once()
        command = mock_run_live.call_args[0][0]
        self.assertTrue(Path(command[0]).name.lower().startswith("python"))
        self.assertIn("packagemaker.py", command[1])
        self.assertEqual(command[2:], ["--buildthis", str(project_path)])
        mock_pause.assert_called_once()
        mock_ok.assert_called_once()

    @patch("lib.tui._run_live", return_value=0)
    @patch("lib.tui._detect_platform", return_value="Knosthalij")
    @patch("lib.tui._pause")
    @patch("lib.tui._prompt")
    @patch("lib.tui._prompt_choice", return_value=0)
    @patch("lib.tui._base_dir")
    def test_screen_build_auto_mode_skips_manual_prompts(
        self,
        mock_base_dir,
        mock_prompt_choice,
        mock_prompt,
        mock_pause,
        mock_detect_platform,
        mock_run_live,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir) / "projects"
            project = base / "Acme.demo.v1.0-26.08-15.38-Danenone"
            project.mkdir(parents=True)
            (project / "details.xml").write_text(
                "<app><publisher>Acme</publisher><app>demo</app>"
                "<version>v1.0-26.08-15.38</version></app>",
                encoding="utf-8",
            )
            mock_base_dir.return_value = base

            tui._screen_build()

            mock_prompt_choice.assert_called_once()
            mock_prompt.assert_not_called()
            mock_run_live.assert_called_once()
            mock_pause.assert_called_once()
            command = mock_run_live.call_args[0][0]
            self.assertEqual(command[2:], ["--buildthis", str(project)])

    @patch("lib.tui._moonfix_project_direct")
    @patch("lib.tui._prompt_bool", return_value=True)
    @patch("lib.tui._prompt_choice", return_value=0)
    @patch("lib.tui._base_dir")
    @patch("lib.tui._pause")
    @patch("lib.tui._info")
    @patch("lib.tui._banner")
    @patch("lib.tui._clear")
    def test_screen_moonfix_delegates_to_supported_cli_path(
        self,
        mock_clear,
        mock_banner,
        mock_info,
        mock_pause,
        mock_base_dir,
        mock_prompt_choice,
        mock_prompt_bool,
        mock_moonfix,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir) / "projects"
            project = base / "Influent.demo.v1.2-26.08-15.38-Danenone"
            project.mkdir(parents=True)
            (project / "details.xml").write_text(
                "<app><publisher>Influent</publisher><app>demo</app>"
                "<name>Demo</name><version>v1.2-26.08-15.38</version></app>",
                encoding="utf-8",
            )
            mock_base_dir.return_value = base

            tui._screen_moonfix()

            mock_moonfix.assert_called_once_with(project)


if __name__ == "__main__":
    unittest.main()
