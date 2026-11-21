import io
import tempfile
import unittest
import zipfile
from pathlib import Path

from lib import blindcubeEngine, flatcubeEngine, makeselfEngine
from lib.engines import (
    BLINDCUBE_ID,
    FLATCUBE_ID,
    MAKESELF_ID,
    EngineError,
    available_engines,
    compiler_engines,
    get_engine,
    resolve_engine,
)
from lib.platform_detect import (
    CANONICAL_PLATFORMS,
    base_directories,
    canonical_platform,
    detect_os,
    normalize_platform,
)


class PlatformDetectionTests(unittest.TestCase):
    """La plataforma canónica solo puede ser Danenone/Knosthalij/AlphaCube."""

    def test_canonical_platform_only_returns_allowed_values(self):
        for os_name in ("windows", "linux", "android", "termux", "darwin", "unknown"):
            self.assertIn(canonical_platform(os_name), CANONICAL_PLATFORMS)

    def test_windows_maps_to_knosthalij(self):
        self.assertEqual(canonical_platform("windows"), "Knosthalij")

    def test_everything_else_maps_to_danenone(self):
        for os_name in ("linux", "android", "termux", "darwin"):
            self.assertEqual(canonical_platform(os_name), "Danenone")

    def test_detect_os_returns_a_known_token(self):
        self.assertIn(
            detect_os(),
            {"windows", "linux", "android", "termux", "darwin", "unknown"},
        )

    def test_normalize_platform_accepts_ui_aliases(self):
        self.assertEqual(normalize_platform("Windows"), "Knosthalij")
        self.assertEqual(normalize_platform("Linux"), "Danenone")
        self.assertEqual(normalize_platform("Multi"), "AlphaCube")
        self.assertEqual(normalize_platform("termux"), "Danenone")
        self.assertEqual(normalize_platform("android"), "Danenone")

    def test_normalize_platform_rejects_unknown(self):
        with self.assertRaises(ValueError):
            normalize_platform("StoneCube")

    def test_base_directories_are_environment_appropriate(self):
        termux_base, _ = base_directories("termux")
        self.assertIn(".packagemaker", termux_base)
        win_base, _ = base_directories("windows")
        self.assertIn("Packagemaker Projects", win_base)
        lin_base, _ = base_directories("linux")
        self.assertIn("Documents", lin_base)


class EngineRegistryTests(unittest.TestCase):
    def test_registry_has_the_three_engines(self):
        self.assertEqual(set(available_engines()), {MAKESELF_ID, FLATCUBE_ID, BLINDCUBE_ID})

    def test_compiler_engines_are_flatcube_and_blindcube(self):
        self.assertEqual([e.id for e in compiler_engines()], [BLINDCUBE_ID, FLATCUBE_ID])

    def test_default_engine_is_blindcube(self):
        self.assertEqual(resolve_engine(None).id, BLINDCUBE_ID)


class BlindCubeContainerTests(unittest.TestCase):
    def test_magic_header_round_trip(self):
        payload = b"package-maker" * 64
        container = blindcubeEngine.pack(payload, meta={"app": "demo"})
        self.assertTrue(container.startswith(b"BLINDCUB"))
        meta, restored = blindcubeEngine.unpack(container)
        self.assertEqual(restored, payload)
        self.assertEqual(meta["app"], "demo")
        self.assertEqual(meta["compression"], "lzma")

    def test_encrypted_round_trip_and_wrong_password(self):
        payload = b"top-secret" * 100
        container = blindcubeEngine.pack(payload, password="correcta")
        self.assertNotIn(b"top-secret", container)  # el payload no filtra en claro
        meta, restored = blindcubeEngine.unpack(container, password="correcta")
        self.assertEqual(restored, payload)
        self.assertIn(meta["encryption"], ("aes-256-gcm", "hmac-sha256-ctr"))
        with self.assertRaises(blindcubeEngine.BlindCubeError):
            blindcubeEngine.unpack(container, password="incorrecta")

    def test_encrypted_without_password_is_rejected(self):
        container = blindcubeEngine.pack(b"data", password="x")
        with self.assertRaises(blindcubeEngine.BlindCubeError):
            blindcubeEngine.unpack(container)

    def test_pack_directory_produces_readable_container(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "app"
            source.mkdir()
            (source / "main.py").write_text("print('hola')", encoding="utf-8")
            (source / "assets").mkdir()
            (source / "assets" / "logo.txt").write_text("logo", encoding="utf-8")
            out = Path(tmp) / "app.blindkpkg"
            blindcubeEngine.pack_directory(source, out, meta={"app": "demo"})
            self.assertTrue(out.is_file())
            meta, payload = blindcubeEngine.unpack(out.read_bytes())
            self.assertIn("main.py", meta["entries"])
            self.assertIn("assets/logo.txt", meta["entries"])
            self.assertTrue(payload.startswith(b"PK"))


class FlatCubeContainerTests(unittest.TestCase):
    def test_zip_payload_passes_through(self):
        zip_bytes = b"PK\x03\x04demo"
        self.assertEqual(flatcubeEngine.pack(zip_bytes), zip_bytes)

    def test_pack_directory_creates_zip_with_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "app"
            source.mkdir()
            (source / "main.py").write_text("print('hola')", encoding="utf-8")
            out = Path(tmp) / "app.flatkpkg"
            flatcubeEngine.pack_directory(source, out)
            self.assertTrue(out.is_file())
            manifest = flatcubeEngine.read_manifest(out.read_bytes())
            self.assertEqual(manifest["engine"], "flatcube")
            self.assertIn("main.py", manifest["entries"])

    def test_non_zip_is_rejected(self):
        with self.assertRaises(flatcubeEngine.FlatCubeError):
            flatcubeEngine.unpack(b"not-a-zip")


class MakeSelfEngineTests(unittest.TestCase):
    def test_validate_canonical_name(self):
        self.assertTrue(
            makeselfEngine.validate_canonical_name("Influent.demo.v1.0-24.01-10.00-AlphaCube")
        )
        self.assertFalse(makeselfEngine.validate_canonical_name("Influent.demo"))

    def test_build_variables_exposed(self):
        variables = makeselfEngine.build_variables(
            "Influent", "demo", "Demo", "octocat", "Danenone", "1.0"
        )
        self.assertIn("FOLDER_NAME", variables)
        self.assertIn("Danenone", variables["FOLDER_NAME"])


class MalformedEngineContainerTests(unittest.TestCase):
    """Un contenedor cortado o con tipos inesperados no debe lanzar excepciones crudas."""

    def test_blindcube_short_header_is_reported(self):
        for raw in (blindcubeEngine.MAGIC, blindcubeEngine.MAGIC + b"\x00\x01\x02"):
            with self.assertRaises(blindcubeEngine.BlindCubeError):
                blindcubeEngine.read_header(raw)

    def test_blindcube_declared_header_beyond_file_is_reported(self):
        raw = blindcubeEngine.MAGIC.ljust(8, b"\x00") + b"\x00\x00\x00\x00" + b"\xff\xff\xff\x7f"
        with self.assertRaises(blindcubeEngine.BlindCubeError):
            blindcubeEngine.read_header(raw)

    def test_blindcube_non_object_header_is_reported(self):
        raw = (
            blindcubeEngine.MAGIC.ljust(8, b"\x00")
            + b"\x00\x00\x00\x00"
            + b"\x04\x00\x00\x00"
            + b"null"
        )
        with self.assertRaises(blindcubeEngine.BlindCubeError):
            blindcubeEngine.read_header(raw)

    def test_blindcube_corrupt_payload_is_reported(self):
        container = blindcubeEngine.container.build_header(4, {"encryption": "none"}) + b"no-es-lzma"
        with self.assertRaises(blindcubeEngine.BlindCubeError):
            blindcubeEngine.unpack(container)

    def test_blindcube_missing_crypto_parameters_are_reported(self):
        container = blindcubeEngine.container.build_header(0, {"encryption": "hmac-sha256-ctr"})
        with self.assertRaises(blindcubeEngine.BlindCubeError):
            blindcubeEngine.unpack(container, password="pw")

    def test_engine_core_read_header_rejects_truncated_input(self):
        engine = get_engine(BLINDCUBE_ID)
        for raw in (blindcubeEngine.MAGIC, blindcubeEngine.MAGIC + b"\x00\x00\x00\x00"):
            with self.assertRaises(EngineError):
                engine.read_header(raw)

    def test_flatcube_corrupt_zip_is_reported(self):
        with self.assertRaises(flatcubeEngine.FlatCubeError):
            flatcubeEngine.unpack(b"PK\x03\x04" + b"\x00" * 12)

    def test_flatcube_non_object_manifest_is_reported(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr(flatcubeEngine.container.MANIFEST_NAME, "[1, 2]")
        with self.assertRaises(flatcubeEngine.FlatCubeError):
            flatcubeEngine.unpack(buffer.getvalue())

    def test_flatcube_unparsable_manifest_is_reported(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr(flatcubeEngine.container.MANIFEST_NAME, "no es json")
        with self.assertRaises(flatcubeEngine.FlatCubeError):
            flatcubeEngine.unpack(buffer.getvalue())


if __name__ == "__main__":
    unittest.main()
