import unittest
from unittest.mock import patch

from lib.projectNameFormatter import ProjectNameFormatter
from lib.template_engine import build_variables


class ProjectNameFormatterTests(unittest.TestCase):
    TIMESTAMP = "26.08-15.38"
    EXPECTED = "Acme-Labs.hello-world.v1.2-26.08-15.38-Danenone"

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
                "version": "v1.2-26.08-15.38",
                "platform": "Linux",
            }
        )

        self.assertEqual(names["project_folder"], self.EXPECTED)
        self.assertEqual(names["package_folder"], self.EXPECTED)
        self.assertEqual(names["iflapp_filename"], f"{self.EXPECTED}.iflapp")
        self.assertEqual(names["version_full"], "v1.2-26.08-15.38")

    @patch.object(ProjectNameFormatter, "get_timestamp", return_value=TIMESTAMP)
    def test_project_template_persists_the_canonical_full_version(self, _timestamp):
        variables = build_variables(
            "Acme Labs", "Hello World", "Hello World", "Tester", "Linux", "1.2"
        )
        self.assertEqual(variables["VERSION"], "v1.2-26.08-15.38")
        self.assertEqual(variables["VERSION_FULL"], "v1.2-26.08-15.38")
        self.assertEqual(variables["VERSION_VSO"], "v1.2-26.08-15.38")

    def test_parse_accepts_the_exact_canonical_format(self):
        parsed = ProjectNameFormatter.parse_project_folder(self.EXPECTED)
        self.assertEqual(
            parsed,
            {
                "publisher": "Acme-Labs",
                "app": "hello-world",
                "version": "1.2",
                "timestamp": self.TIMESTAMP,
                "platform": "Danenone",
            },
        )
        self.assertIsNone(ProjectNameFormatter.parse_project_folder("acme.hello.1.2-Linux"))

    def test_parse_preserves_patch_versions(self):
        parsed = ProjectNameFormatter.parse_project_folder(
            "Influent.packagemaker.v3.2.7-26.05-20.13-AlphaCube"
        )
        self.assertEqual(parsed["version"], "3.2.7")
        self.assertEqual(parsed["platform"], "AlphaCube")

    def test_influent_capitalization_is_preserved(self):
        result = ProjectNameFormatter.format_project_folder(
            "Influent", "Foundstore", "1.1-26.08-22.31", "Danenone"
        )
        self.assertTrue(result.startswith("Influent.foundstore."))

    def test_invalid_platform_is_rejected(self):
        with self.assertRaises(ValueError):
            ProjectNameFormatter.format_project_folder(
                "Acme", "Hello", "1.2", "MacOS"
            )

    def test_unsafe_segments_are_rejected(self):
        for publisher, app in (("../escape", "hello"), ("Acme", "../escape"), ("Acme Inc", "hello_world")):
            with self.subTest(publisher=publisher, app=app):
                with self.assertRaises(ValueError):
                    ProjectNameFormatter.format_project_folder(
                        publisher, app, "1.2", "Linux"
                    )


if __name__ == "__main__":
    unittest.main()
