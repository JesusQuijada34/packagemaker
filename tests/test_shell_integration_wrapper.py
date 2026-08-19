import sys
import unittest


class ShellIntegrationWrapperTests(unittest.TestCase):
    @unittest.skipIf(sys.platform.startswith("win"), "La integración nativa está disponible en Windows")
    def test_wrapper_imports_and_reports_non_windows_platform(self):
        from lib.shell_integration import ShellIntegration

        with self.assertRaises(ImportError):
            ShellIntegration()


if __name__ == "__main__":
    unittest.main()
