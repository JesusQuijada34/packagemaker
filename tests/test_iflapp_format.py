import json
import struct
import tempfile
import unittest
from pathlib import Path

from lib.blindcubeEngine import iflapp_format
from lib.blindcubeEngine.iflapp_reader import IflappReader


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


class TruncatedContainerTests(unittest.TestCase):
    """Una descarga cortada no debe parecer un paquete válido y vacío."""

    def _write(self, root: Path, name: str, data: bytes) -> Path:
        path = root / name
        path.write_bytes(data)
        return path

    def test_magic_without_header_length_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), "cut.iflapp", iflapp_format.MAGIC)
            with self.assertRaises(iflapp_format.IflappError):
                iflapp_format.read_iflapp_header(path)

    def test_declared_header_longer_than_file_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(
                Path(tmp),
                "cut.iflapp",
                iflapp_format.MAGIC + struct.pack("<I", 1024) + b"{}",
            )
            with self.assertRaises(iflapp_format.IflappError):
                iflapp_format.read_iflapp_header(path)

    def test_header_must_be_a_json_object(self):
        with tempfile.TemporaryDirectory() as tmp:
            blob = b"null"
            path = self._write(
                Path(tmp),
                "bad.iflapp",
                iflapp_format.MAGIC + struct.pack("<I", len(blob)) + blob,
            )
            with self.assertRaises(iflapp_format.IflappError):
                iflapp_format.read_iflapp_header(path)

    def test_section_beyond_end_of_file_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            header = {"format_version": 2, "sections": {"icon": {"offset": 4096, "size": 8}}}
            blob = json.dumps(header).encode("utf-8")
            path = self._write(
                Path(tmp),
                "cut.iflapp",
                iflapp_format.MAGIC + struct.pack("<I", len(blob)) + blob,
            )
            with self.assertRaises(iflapp_format.IflappError):
                iflapp_format.read_iflapp_header(path)

    def test_invalid_section_metadata_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            header = {"sections": {"icon": {"offset": "nope", "size": 8}}}
            blob = json.dumps(header).encode("utf-8")
            path = self._write(
                Path(tmp),
                "bad.iflapp",
                iflapp_format.MAGIC + struct.pack("<I", len(blob)) + blob,
            )
            with self.assertRaises(iflapp_format.IflappError):
                iflapp_format.read_iflapp_header(path)


class MalformedHeaderShapeTests(unittest.TestCase):
    """Campos de cabecera con tipos inesperados deben dar IflappError, no traceback."""

    def _write(self, root: Path, header) -> Path:
        blob = json.dumps(header).encode("utf-8")
        path = root / "bad.iflapp"
        path.write_bytes(iflapp_format.MAGIC + struct.pack("<I", len(blob)) + blob)
        return path

    def test_payload_must_be_object(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), {"format_version": 2, "payload": []})
            with self.assertRaises(iflapp_format.IflappError):
                iflapp_format.read_iflapp_header(path)

    def test_sections_must_be_object(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), {"format_version": 2, "sections": []})
            with self.assertRaises(iflapp_format.IflappError):
                iflapp_format.read_iflapp_header(path)

    def test_manifest_must_be_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), {"format_version": 2, "manifest": 5})
            with self.assertRaises(iflapp_format.IflappError):
                iflapp_format.read_iflapp_header(path)

    def test_non_numeric_payload_metadata_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(
                Path(tmp), {"format_version": 2, "payload": {"file_count": "x"}}
            )
            with self.assertRaises(iflapp_format.IflappError):
                iflapp_format.read_iflapp_header(path)

    def test_negative_section_offset_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(
                Path(tmp),
                {"format_version": 2, "sections": {"icon": {"offset": -5, "size": 10}}},
            )
            with self.assertRaises(iflapp_format.IflappError):
                iflapp_format.read_iflapp_header(path)

    def test_non_finite_section_size_raises(self):
        # ``1e400`` es JSON válido y se decodifica como infinito: ``int(inf)``
        # lanzaba OverflowError en vez de IflappError.
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(
                Path(tmp),
                {"format_version": 2, "sections": {"icon": {"offset": 0, "size": 1e400}}},
            )
            with self.assertRaises(iflapp_format.IflappError):
                iflapp_format.read_iflapp_header(path)

    def test_non_finite_payload_offset_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(
                Path(tmp), {"format_version": 2, "payload": {"offset": 1e400, "size": 0}}
            )
            with self.assertRaises(iflapp_format.IflappError):
                iflapp_format.read_iflapp_header(path)

    def test_export_header_assets_does_not_crash_on_odd_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self._write(root, {"format_version": 2, "sections": {"icon": []}})
            with self.assertRaises(iflapp_format.IflappError):
                iflapp_format.export_header_assets(path, root / "out")

    def test_header_properties_tolerate_unexpected_shapes(self):
        header = iflapp_format.IflappHeader(raw={"payload": [], "manifest": 5})
        self.assertEqual(header.compression, "none")
        self.assertEqual(header.encryption, "none")
        self.assertEqual(header.file_count, 0)
        self.assertEqual(header.manifest, [])


class MalformedEncryptionParameterTests(unittest.TestCase):
    """Parámetros de cifrado con tipos inesperados deben dar IflappError."""

    def _mutate_payload(self, path: Path, **overrides) -> Path:
        raw = bytearray(path.read_bytes())
        header_len = struct.unpack("<I", raw[8:12])[0]
        header = json.loads(bytes(raw[12 : 12 + header_len]).decode("utf-8"))
        header["payload"].update(overrides)
        blob = json.dumps(header, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertLessEqual(len(blob), header_len)
        raw[12 : 12 + header_len] = blob + b" " * (header_len - len(blob))
        path.write_bytes(bytes(raw))
        return path

    def test_non_text_crypto_parameters_are_reported(self):
        cases = (
            {"salt": 5},
            {"nonce": 5},
            {"salt": "no-es-base64"},
            {"salt": None},
        )
        for overrides in cases:
            with tempfile.TemporaryDirectory() as tmp:
                path = _make_package(Path(tmp), password="secreto")
                self._mutate_payload(path, **overrides)
                with self.subTest(overrides=overrides):
                    with self.assertRaises(iflapp_format.IflappError):
                        iflapp_format.read_iflapp_payload(path, password="secreto")

    def test_non_text_mac_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _make_package(Path(tmp), password="secreto")
            self._mutate_payload(path, encryption="hmac-sha256-ctr", mac=5)
            with self.assertRaises(iflapp_format.IflappSignatureError):
                iflapp_format.read_iflapp_payload(path, password="secreto")


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


class IflappHeaderHandlerTests(unittest.TestCase):
    """El handler debe leer icono y detalles de la cabecera sin descifrar."""

    PNG = bytes.fromhex(
        "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
        "1f15c4890000000d4944415478da63f8cfc0f01f00050001ff9d5c1b7e"
        "0000000049454e44ae426082"
    )

    def _pack(self, root, *, icon, details):
        package = root / "pkg"
        package.mkdir()
        (package / "main.py").write_text("print('hola')", encoding="utf-8")
        out = root / "demo.iflapp"
        iflapp_format.pack_iflapp(
            package_dir=package,
            output_file=out,
            icon=icon,
            details=details,
            identity={"name": "Demo", "version": "1.0.0", "author": "me"},
        )
        return out

    def test_header_exposes_icon_and_details_without_decrypting(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            details = b"<details><name>Demo</name></details>"
            out = self._pack(root, icon=self.PNG, details=details)

            header = iflapp_format.read_iflapp_header(out)
            self.assertEqual(header.icon, self.PNG)
            self.assertEqual(header.details, details)
            self.assertEqual(header.identity()["name"], "Demo")
            # Con contraseña: el payload queda cifrado, la cabecera no.
            locked = root / "locked.iflapp"
            iflapp_format.pack_iflapp(
                package_dir=root / "pkg",
                output_file=locked,
                icon=self.PNG,
                details=details,
                password="secreto",
                identity={"name": "Demo"},
            )
            self.assertEqual(iflapp_format.read_iflapp_header(locked).icon, self.PNG)

    def test_accepts_paths_or_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            icon_path = root / "icon.png"
            icon_path.write_bytes(self.PNG)
            details_path = root / "details.xml"
            details_path.write_text("<details/>", encoding="utf-8")

            from_paths = self._pack(root, icon=icon_path, details=details_path)
            self.assertTrue(iflapp_format.is_iflapp_v2(from_paths))
            self.assertEqual(iflapp_format.read_iflapp_header(from_paths).icon, self.PNG)

    def test_bad_blob_raises_clear_error(self):
        with self.assertRaises(iflapp_format.IflappError):
            iflapp_format._as_bytes("/no/existe/icono.png", what="icon")


if __name__ == "__main__":
    unittest.main()


class HeaderIdentityFallbackTests(unittest.TestCase):
    """La identidad debe derivarse de details.xml sin descifrar el payload."""

    def test_identity_falls_back_to_details_xml_in_header(self):
        from lib.blindcubeEngine import iflapp_format
        from lib.blindcubeEngine.iflapp_reader import IflappReader

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pkg = root / "pkg"
            pkg.mkdir()
            (pkg / "main.py").write_text("print('x')\n", encoding="utf-8")
            details = (
                b"<?xml version='1.0'?><app><publisher>Influent</publisher>"
                b"<app>packagemaker</app><name>Package Maker</name></app>"
            )
            out = root / "Demo.iflapp"
            # Sin ``identity``: la cabecera no lleva campos planos.
            iflapp_format.pack_iflapp(pkg, out, icon=b"\x89PNG" + b"x" * 32, details=details)
            info = IflappReader(out).info()
            self.assertEqual(info.identity["publisher"], "Influent")
            self.assertEqual(info.identity["app"], "packagemaker")

    def test_reader_exposes_summary(self):
        from lib.blindcubeEngine import iflapp_format
        from lib.blindcubeEngine.iflapp_reader import IflappReader

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pkg = root / "pkg"
            pkg.mkdir()
            (pkg / "main.py").write_text("print('x')\n", encoding="utf-8")
            out = root / "Demo.iflapp"
            iflapp_format.pack_iflapp(pkg, out, identity={"name": "Demo"})
            text = IflappReader(out).summary()
            self.assertIn("Demo", text)
            self.assertIn("Formato", text)
