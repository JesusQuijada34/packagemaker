import unittest
from unittest.mock import patch

from lib.cliHandler import handle_cli_action


class CliShellActionStatusTests(unittest.TestCase):
    @patch("lib.cliHandler.ShellIntegrationHelper.install", return_value=False)
    def test_shell_action_failure_is_propagated(self, install):
        self.assertFalse(handle_cli_action("shellpatch_install", None, None))
        install.assert_called_once_with()

    @patch("lib.cliHandler.ShellIntegrationHelper.install", return_value=True)
    def test_shell_action_success_is_propagated(self, install):
        self.assertTrue(handle_cli_action("shellpatch_install", None, None))
        install.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
