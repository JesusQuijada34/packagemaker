import unittest
from unittest.mock import patch

from lib.projectNameFormatter import ProjectNameFormatter
from lib.template_engine import build_variables


class ProjectNameFormatterTests(unittest.TestCase):
    TIMESTAMP = "26.08-15.38"
    EXPECTED = "acme-labs.hello-world.v1.2-26.08-15.38-Danenone"

    @patch.object(ProjectNameFormatter, "get_timestamp", return_value=TIMESTAMP)
    def test_all_artifacts_use_the_exact_canonical_format(self, _timestamp):
        project = ProjectNameFormatter.format_project_folder(
            "Acme Labs", "Hello World", "1.2", "Linux"
        )
        package = ProjectNameFormatter.format_package_folder(
            "Acme Labs", "Hello World", "1.2", "Danenone"
        )
        iflapp = ProjectNameFormatter.format_iflapp_filename(
            "Acme Labs", "Hello World", "v1.2-26.08-15.38-Danenone", "Linux"
        )

        self.assertEqual(project, self.EXPECTED)
        self.assertEqual(package, self.EXPECTED)
        self.assertEqual(iflapp, f"{self.EXPECTED}.iflapp")

    @patch.object(ProjectNameFormatter, "get_timestamp", return_value=TIMESTAMP)
    def test_metadata_keeps_one_shared_timestamp_and_platform(self, _timestamp):
        names = ProjectNameFormatter.format_from_metadata(
            {
                "publisher": "Acme Labs",
                "app": "Hello World",
                "version": "v1.2-26.08-15.38-Danenone",
                "platform": "Linux",
            }
        )

        self.assertEqual(names["project_folder"], self.EXPECTED)
        self.assertEqual(names["package_folder"], self.EXPECTED)
        self.assertEqual(names["iflapp_filename"], f"{self.EXPECTED}.iflapp")
        self.assertEqual(names["version_full"], "v1.2-26.08-15.38-Danenone")

    @patch.object(ProjectNameFormatter, "get_timestamp", return_value=TIMESTAMP)
    def test_project_template_persists_the_canonical_full_version(self, _timestamp):
        variables = build_variables(
            "Acme Labs", "Hello World", "Hello World", "Tester", "Linux", "1.2"
        )
        self.assertEqual(variables["VERSION"], "v1.2-26.08-15.38-Danenone")
        self.assertEqual(variables["VERSION_FULL"], "v1.2-26.08-15.38-Danenone")
        self.assertEqual(variables["VERSION_VSO"], "v1.2-26.08-15.38")

    def test_parse_accepts_only_the_exact_canonical_format(self):
        parsed = ProjectNameFormatter.parse_project_folder(self.EXPECTED)
        self.assertEqual(
            parsed,
            {
                "publisher": "acme-labs",
                "app": "hello-world",
                "version": "1.2",
                "timestamp": self.TIMESTAMP,
                "platform": "Danenone",
            },
        )
        self.assertIsNone(ProjectNameFormatter.parse_project_folder("acme.hello.1.2-Linux"))

    def test_invalid_platform_is_rejected(self):
        with self.assertRaises(ValueError):
            ProjectNameFormatter.format_project_folder(
                "Acme", "Hello", "1.2", "MacOS"
            )


if __name__ == "__main__":
    unittest.main()
