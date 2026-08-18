import os
import tempfile
import unittest
import zipfile
from pathlib import Path

from lib.safe_zip import UnsafeZipMemberError, safe_extract_zip


class SafeZipTests(unittest.TestCase):
    def _archive(self, name: str, payload: bytes = b"payload") -> zipfile.ZipFile:
        fd, archive_path = tempfile.mkstemp(suffix=".zip")
        os.close(fd)
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr(name, payload)
        return zipfile.ZipFile(archive_path, "r")

    def test_extracts_members_inside_destination(self):
        with tempfile.TemporaryDirectory() as temp, self._archive("nested/file.txt") as archive:
            destination = Path(temp) / "destination"
            extracted = safe_extract_zip(archive, destination)
            self.assertTrue((destination / "nested/file.txt").is_file())
            self.assertEqual(extracted[-1], destination / "nested/file.txt")

    def test_rejects_parent_traversal_before_writing(self):
        with tempfile.TemporaryDirectory() as temp, self._archive("../outside.txt") as archive:
            destination = Path(temp) / "destination"
            outside = Path(temp) / "outside.txt"
            with self.assertRaises(UnsafeZipMemberError):
                safe_extract_zip(archive, destination)
            self.assertFalse(outside.exists())

    def test_rejects_absolute_and_windows_traversal_names(self):
        for member_name in ("/tmp/outside.txt", "C:/outside.txt", r"..\\outside.txt"):
            with (
                self.subTest(member_name=member_name),
                tempfile.TemporaryDirectory() as temp,
                self._archive(member_name) as archive,
                self.assertRaises(UnsafeZipMemberError),
            ):
                safe_extract_zip(archive, Path(temp) / "destination")

    def test_rejects_symlink_members(self):
        with tempfile.TemporaryDirectory() as temp:
            fd, archive_path = tempfile.mkstemp(suffix=".zip")
            os.close(fd)
            info = zipfile.ZipInfo("link")
            info.create_system = 3
            info.external_attr = (0o120777 << 16) | 0xA000
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr(info, "../../outside")
            with (
                zipfile.ZipFile(archive_path, "r") as archive,
                self.assertRaises(UnsafeZipMemberError),
            ):
                safe_extract_zip(archive, Path(temp) / "destination")


if __name__ == "__main__":
    unittest.main()
