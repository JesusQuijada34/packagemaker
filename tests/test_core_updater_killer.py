import unittest
from unittest.mock import patch

from lib.coreUpdater.core import KillerLogic


class KillerLogicTests(unittest.TestCase):
    @patch("lib.coreUpdater.core.subprocess.run")
    @patch("lib.coreUpdater.core.sys.platform", "linux")
    def test_kill_target_uses_exact_non_shell_command(self, run):
        run.return_value.returncode = 0

        self.assertTrue(
            KillerLogic.kill_target("packagemaker;touch /tmp/should-not-run")
        )

        run.assert_called_once_with(
            ["pkill", "-9", "-x", "should-not-run"],
            capture_output=True,
            text=True,
            shell=False,
            check=False,
        )

    @patch("lib.coreUpdater.core.subprocess.run")
    def test_empty_process_name_is_rejected(self, run):
        self.assertFalse(KillerLogic.kill_target("   "))
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
