import sys
import tempfile
import unittest
from pathlib import Path

from lib.cliHandler import CLIHandler
from lib import iflapp_format


class CliHardeningParseTests(unittest.TestCase):
    def setUp(self):
        self.handler = CLIHandler()

    def test_none_disables_hardening(self):
        self.assertIsNone(self.handler._parse_hardening(None))

    def test_all_keywords_select_every_method(self):
        from lib.hardening import method_names

        for token in ("", "all", "todos"):
            self.assertEqual(self.handler._parse_hardening(token), method_names())

    def test_comma_list_filters_unknown_methods(self):
        parsed = self.handler._parse_hardening("strip, unknown ,checksum")
        self.assertEqual(parsed, ["strip", "checksum"])

    def test_list_hardening_action_is_dispatched(self):
        original = sys.argv
        try:
            sys.argv = ["packagemaker.py", "--list-hardening"]
            args = self.handler.parse()
            action, data, options = self.handler.get_action(args)
        finally:
            sys.argv = original
        self.assertEqual(action, "list_hardening")
        self.assertIsNone(data)

    def test_buildthis_parses_compiler_dropper_and_hardening(self):
        original = sys.argv
        try:
            sys.argv = [
                "packagemaker.py", "--buildthis", ".", "--compiler", "nuitka",
                "--dropper", "--harden", "strip,checksum", "--password", "pw",
            ]
            args = self.handler.parse()
            action, _, options = self.handler.get_action(args)
        finally:
            sys.argv = original
        self.assertEqual(action, "buildthis")
        self.assertEqual(options.get("compiler"), "nuitka")
        self.assertTrue(options.get("dropper"))
        self.assertEqual(options.get("hardening"), ["strip", "checksum"])
        self.assertEqual(options.get("password"), "pw")


class InspectHelperTests(unittest.TestCase):
    def _make_package(self, root: Path) -> Path:
        pkg = root / "pkg"
        (pkg / "app").mkdir(parents=True)
        (pkg / "app" / "main.py").write_text("print('hi')\n", encoding="utf-8")
        (pkg / "details.xml").write_text(
            "<app><publisher>Acme</publisher><app>demo</app><version>1.0</version>"
            "<platform>Danenone</platform><author>Test</author></app>",
            encoding="utf-8",
        )
        output = root / "demo.iflapp"
        iflapp_format.pack_iflapp(
            pkg,
            output,
            identity={
                "publisher": "Acme", "app": "demo", "version": "1.0",
                "name": "Demo", "author": "Test", "platform": "Danenone",
            },
        )
        return output

    def test_inspect_reads_header_without_extracting_payload(self):
        from lib.cliHandler import PackageInspectHelper

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = self._make_package(root)
            self.assertTrue(PackageInspectHelper.inspect({"path": str(package)}))
            export_dir = root / "assets"
            self.assertTrue(
                PackageInspectHelper.inspect({"path": str(package), "extract": str(export_dir)})
            )
            self.assertTrue((export_dir / "details.xml").is_file())

    def test_inspect_without_path_returns_false(self):
        from lib.cliHandler import PackageInspectHelper

        self.assertFalse(PackageInspectHelper.inspect({}))


if __name__ == "__main__":
    unittest.main()
