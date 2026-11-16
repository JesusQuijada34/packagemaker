import unittest
from unittest.mock import patch

from lib.cliHandler import handle_cli_action


class CliShellActionStatusTests(unittest.TestCase):
    @patch("lib.cliHandler.MexfShellHelper.install", return_value=False)
    def test_shell_action_failure_is_propagated(self, install):
        self.assertFalse(handle_cli_action("install_mexf_shell", {"path": "x.mexf"}, None))
        install.assert_called_once_with({"path": "x.mexf"})

    @patch("lib.cliHandler.MexfShellHelper.install", return_value=True)
    def test_shell_action_success_is_propagated(self, install):
        self.assertTrue(handle_cli_action("install_mexf_shell", {"path": "x.mexf"}, None))
        install.assert_called_once_with({"path": "x.mexf"})

    @patch("lib.cliHandler.MexfShellHelper.plan", return_value=True)
    def test_shell_plan_is_dispatched(self, plan):
        self.assertTrue(handle_cli_action("shell_plan", {"path": "x.mexf"}, None))
        plan.assert_called_once_with({"path": "x.mexf"})


if __name__ == "__main__":
    unittest.main()
