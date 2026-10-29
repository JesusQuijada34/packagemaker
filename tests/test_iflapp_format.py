import tempfile
import unittest
from pathlib import Path

from lib import iflapp_format
from lib.iflapp_reader import IflappReader


def _make_package(root: Path, *, password=None, icon=True) -> Path:
    package = root / "pkg"
    (package / "app").mkdir(parents=True)
    (package / "details.xml").write_text(
        "<app><publisher>Acme</publisher><app>demo</app><name>Demo</name>"
        "<version>v1.0</version><author>me</author><platform>Danenone</platform></app>",
        encoding="utf-8",
    )
    (package / "bin").mkdir()
    (package / "bin" / "demo").write_bytes(b"#!/bin/sh\necho hi\n")
    if icon:
        (package / "app" / "app-icon.ico").write_bytes(b"\x00\x00\x01\x00ICON")
    out = root / "demo.iflapp"
    iflapp_format.pack_iflapp(
        package,
        out,
        identity={"publisher": "Acme", "app": "demo", "name": "Demo", "version": "v1.0"},
        password=password,
    )
    return out


class IflappFormatTests(unittest.TestCase):
    def test_pack_produces_signed_v2_container(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = _make_package(Path(tmp))
            self.assertEqual(iflapp_format.sniff_format(out), "iflapp2")
            self.assertTrue(iflapp_format.verify_iflapp(out)["valid"])

    def test_header_is_readable_without_decryption(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = _make_package(Path(tmp), password="secret")
            header = iflapp_format.read_iflapp_header(out)
            self.assertEqual(header.identity()["app"], "demo")
            self.assertTrue(header.icon)
            self.assertIn("details.xml", {e["path"] for e in header.manifest})

    def test_roundtrip_extraction(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = _make_package(root)
            dest = root / "extract"
            files = iflapp_format.extract_iflapp(out, dest)
            self.assertIn(dest / "details.xml", files)
            self.assertTrue((dest / "bin" / "demo").is_file())

    def test_encrypted_roundtrip_requires_password(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = _make_package(root, password="s3cr3t")
            header = iflapp_format.read_iflapp_header(out, include_blobs=False)
            self.assertNotEqual(header.encryption, "none")
            with self.assertRaises(iflapp_format.IflappError):
                iflapp_format.extract_iflapp(out, root / "bad")
            files = iflapp_format.extract_iflapp(out, root / "ok", password="s3cr3t")
            self.assertTrue(files)

    def test_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = _make_package(Path(tmp))
            header = iflapp_format.read_iflapp_header(out, include_blobs=False)
            offset = int(header.raw["payload"]["offset"])
            data = bytearray(out.read_bytes())
            data[offset] ^= 0xFF
            out.write_bytes(bytes(data))
            with self.assertRaises(iflapp_format.IflappError):
                iflapp_format.verify_iflapp(out)

    def test_path_traversal_is_rejected(self):
        with self.assertRaises(iflapp_format.IflappError):
            iflapp_format._safe_member_target(Path("/tmp"), "../evil")


class IflappReaderTests(unittest.TestCase):
    def test_reader_summary_and_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = _make_package(root)
            reader = IflappReader(out)
            info = reader.info()
            self.assertEqual(info.identity["publisher"], "Acme")
            self.assertIn("demo", info.summary())
            exported = reader.export_assets(root / "assets")
            self.assertTrue(Path(exported["icon"]).is_file())
            self.assertTrue(Path(exported["details"]).is_file())


if __name__ == "__main__":
    unittest.main()
