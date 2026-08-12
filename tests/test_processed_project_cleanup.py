import tempfile
import unittest
import zipfile
from pathlib import Path

from lib.BuildThread import FlangCompiler


class ProcessedProjectCleanupTests(unittest.TestCase):
    def _create_valid_iflapp(self, path: Path) -> None:
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("details.xml", "<app />")

    def test_valid_external_iflapp_removes_processed_project(self):
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
            self.assertTrue(compiler.cleanup_processed_project(artifact))
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
            self.assertFalse(compiler.cleanup_processed_project(invalid_artifact))
            self.assertTrue(source.exists())

            internal_artifact = source / "internal.iflapp"
            self._create_valid_iflapp(internal_artifact)
            self.assertFalse(compiler.cleanup_processed_project(internal_artifact))
            self.assertTrue(source.exists())

    def test_gui_compiler_runner_removes_source_after_packaging(self):
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
                package = output / "acme.demo.v1.0-26.08-15.38-Danenone"
                package.mkdir()
                (package / "details.xml").write_text("<app />", encoding="utf-8")
                return True

            compiler.create_package = create_package
            artifact = compiler.run()

            self.assertIsNotNone(artifact)
            self.assertTrue(artifact.exists())
            self.assertFalse(source.exists())


if __name__ == "__main__":
    unittest.main()
