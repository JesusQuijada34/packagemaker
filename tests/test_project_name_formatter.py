import unittest
from unittest.mock import patch

from lib.projectNameFormatter import ProjectNameFormatter
from lib.makeselfEngine.template_engine import build_variables


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
        for platform in ("MacOS", "Darwin", "Windows Server-ish"):
            with self.subTest(platform=platform):
                with self.assertRaises(ValueError):
                    ProjectNameFormatter.format_project_folder(
                        "Acme", "Hello", "1.2", platform
                    )

    @patch.object(ProjectNameFormatter, "get_timestamp", return_value=TIMESTAMP)
    def test_missing_publisher_uses_canonical_influent_capitalization(self, _timestamp):
        names = ProjectNameFormatter.format_from_metadata(
            {"app": "Demo", "version": "1.2", "platform": "Linux"}
        )
        self.assertTrue(names["project_folder"].startswith("Influent.demo."))

    def test_unsafe_segments_are_rejected(self):
        for publisher, app in (("../escape", "hello"), ("Acme", "../escape"), ("Acme Inc", "hello_world")):
            with self.subTest(publisher=publisher, app=app):
                with self.assertRaises(ValueError):
                    ProjectNameFormatter.format_project_folder(
                        publisher, app, "1.2", "Linux"
                    )


if __name__ == "__main__":
    unittest.main()


class VersionNormalizationTests(unittest.TestCase):
    """Regresión: el campo de versión libre (``1``, ``v2``) rompía la creación.

    Traza original: ``ValueError: Versión inválida`` al crear un proyecto
    porque ``version_base`` llegaba como ``"1"`` sin el componente ``X.x``.
    """

    def test_bare_major_version_is_completed(self):
        self.assertEqual(ProjectNameFormatter.normalize_version_base("1"), "1.0")
        self.assertEqual(ProjectNameFormatter.normalize_version_base("v2"), "2.0")
        self.assertEqual(ProjectNameFormatter.normalize_version_base("3"), "3.0")

    def test_valid_versions_pass_through(self):
        for value in ("1.0", "1.0.0", "3.2.7", "v3.2.7"):
            self.assertEqual(
                ProjectNameFormatter.normalize_version_base(value),
                value.lstrip("v"),
            )

    def test_empty_or_garbage_falls_back_to_default(self):
        self.assertEqual(ProjectNameFormatter.normalize_version_base(""), "1.0")
        self.assertEqual(ProjectNameFormatter.normalize_version_base(None), "1.0")
        self.assertEqual(ProjectNameFormatter.normalize_version_base("abc"), "1.0")

    def test_timestamp_and_platform_suffix_are_stripped(self):
        self.assertEqual(
            ProjectNameFormatter.normalize_version_base("v3.2.7-26.05-20.13"),
            "3.2.7",
        )
        self.assertEqual(
            ProjectNameFormatter.normalize_version_base("1.0.0-Knosthalij"),
            "1.0.0",
        )

    @patch.object(ProjectNameFormatter, "get_timestamp", return_value="26.08-15.38")
    def test_build_variables_accepts_a_bare_major_version(self, _timestamp):
        variables = build_variables(
            "influent", "myapp", "My App", "octocat", "Knosthalij", "1"
        )
        self.assertEqual(variables["VERSION_BASE"], "1.0")
        self.assertEqual(variables["FOLDER_NAME"], "influent.myapp.v1.0-26.08-15.38-Knosthalij")

    @patch.object(ProjectNameFormatter, "get_timestamp", return_value="26.08-15.38")
    def test_build_variables_never_raises_on_garbage_version(self, _timestamp):
        variables = build_variables(
            "influent", "myapp", "My App", "octocat", "Danenone", "not-a-version"
        )
        self.assertEqual(variables["VERSION_BASE"], "1.0")
