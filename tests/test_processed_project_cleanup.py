import tempfile
import unittest
import zipfile
from pathlib import Path

from lib.BuildThread import FlangCompiler


class ProcessedProjectCleanupTests(unittest.TestCase):
    def _create_valid_iflapp(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("details.xml", "<app />")

    def test_valid_external_iflapp_preserves_processed_project_by_default(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source-project"
            source.mkdir()
            (source / "details.xml").write_text("<app />", encoding="utf-8")
            output = root / "output"
            output.mkdir()
            artifact = output / "publisher.app.v1.0-26.08-15.38-Danenone.iflapp"
            self._create_valid_iflapp(artifact)

            compiler = FlangCompiler(source, output)
            self.assertFalse(compiler.cleanup_processed_project(artifact))
            self.assertTrue(source.exists())
            self.assertTrue(artifact.exists())

    def test_valid_external_iflapp_is_removed_only_when_explicitly_authorized(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source-project"
            source.mkdir()
            (source / "details.xml").write_text("<app />", encoding="utf-8")
            output = root / "output"
            output.mkdir()
            artifact = output / "publisher.app.v1.0-26.08-15.38-Danenone.iflapp"
            self._create_valid_iflapp(artifact)

            compiler = FlangCompiler(source, output)
            self.assertTrue(compiler.cleanup_processed_project(artifact, allow_delete=True))
            self.assertFalse(source.exists())
            self.assertTrue(artifact.exists())

    def test_invalid_or_internal_artifact_preserves_source_project(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source-project"
            source.mkdir()
            (source / "details.xml").write_text("<app />", encoding="utf-8")
            compiler = FlangCompiler(source, root / "output")

            invalid_artifact = root / "invalid.iflapp"
            invalid_artifact.write_text("not a zip", encoding="utf-8")
            self.assertFalse(compiler.cleanup_processed_project(invalid_artifact, allow_delete=True))
            self.assertTrue(source.exists())

            internal_artifact = source / "internal.iflapp"
            self._create_valid_iflapp(internal_artifact)
            self.assertFalse(compiler.cleanup_processed_project(internal_artifact, allow_delete=True))
            self.assertTrue(source.exists())

    def test_compress_to_iflapp_rejects_empty_package_and_accepts_valid_package(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source-project"
            source.mkdir()
            output = root / "output"
            output.mkdir()
            compiler = FlangCompiler(source, output)

            empty_package = root / "empty-package"
            empty_package.mkdir()
            empty_artifact = output / "empty.iflapp"
            self.assertFalse(compiler.compress_to_iflapp(empty_package, empty_artifact))
            self.assertFalse(empty_artifact.exists())

            valid_package = root / "valid-package"
            valid_package.mkdir()
            (valid_package / "details.xml").write_text("<app />", encoding="utf-8")
            valid_artifact = output / "valid.iflapp"
            self.assertTrue(compiler.compress_to_iflapp(valid_package, valid_artifact))
            self.assertTrue(valid_artifact.exists())
            with zipfile.ZipFile(valid_artifact) as archive:
                self.assertEqual(archive.namelist(), ["details.xml"])

    def test_gui_compiler_runner_preserves_source_after_packaging(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source-project"
            source.mkdir()
            output = root / "output"
            output.mkdir()
            compiler = FlangCompiler(source, output)
            compiler.current_platform = "Linux"
            compiler.metadata = {
                "publisher": "Acme",
                "app": "demo",
                "version": "v1.0-26.08-15.38-Danenone",
                "platform": "Danenone",
            }
            compiler.parse_details_xml = lambda: True
            compiler.find_scripts = lambda: True
            compiler.should_compile_for_platform = lambda target: target == "Linux"
            compiler.compile_binaries = lambda target: True

            def create_package(target):
                package = output / "Acme.demo.v1.0-26.08-15.38-Danenone"
                package.mkdir()
                (package / "details.xml").write_text("<app />", encoding="utf-8")
                return True

            compiler.create_package = create_package
            artifact = compiler.run()

            self.assertIsNotNone(artifact)
            self.assertTrue(artifact.exists())
            self.assertTrue(source.exists())


if __name__ == "__main__":
    unittest.main()
