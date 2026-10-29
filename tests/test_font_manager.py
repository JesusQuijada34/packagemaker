"""Pruebas del gestor de fuentes: registro, integridad y modo offline.

La red se sustituye por un doble controlado en ``_fetch``: es la única
frontera externa. Todo lo demás (verificación SHA-256, escritura atómica,
registro en Qt y resolución de familias) se ejercita con código real.
"""
import hashlib
import os
import subprocess
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from lib import font_manager  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


class RegistryTests(unittest.TestCase):
    def test_every_spec_has_a_valid_sha256_and_mirrors(self):
        for key, spec in font_manager.FONT_REGISTRY.items():
            with self.subTest(key=key):
                self.assertEqual(len(spec.sha256), 64)
                int(spec.sha256, 16)
                self.assertTrue(spec.family)
                self.assertTrue(spec.filename)
                self.assertGreater(spec.size, 0)
                # Al menos un espejo raw y otro CDN.
                self.assertGreaterEqual(len(spec.urls()), 2)

    def test_ui_and_mono_preferences_reference_known_keys(self):
        for key in list(font_manager.UI_PREFERENCE) + list(font_manager.MONO_PREFERENCE):
            self.assertIn(key, font_manager.FONT_REGISTRY)

    def test_spec_for_rejects_unknown_key(self):
        with self.assertRaises(KeyError):
            font_manager.spec_for("no-existe")


class IntegrityTests(unittest.TestCase):
    def setUp(self):
        self.spec = font_manager.FONT_REGISTRY["jetbrainsmono"]
        self.payload = b"fuente de prueba" * 64
        self.spec_sha = hashlib.sha256(self.payload).hexdigest()

    def test_verify_file_accepts_matching_hash(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ok.ttf"
            path.write_bytes(self.payload)
            self.assertTrue(font_manager.verify_file(path, self.spec_sha))

    def test_verify_file_rejects_wrong_hash_and_missing_file(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.ttf"
            path.write_bytes(self.payload)
            self.assertFalse(font_manager.verify_file(path, "0" * 64))
            self.assertFalse(font_manager.verify_file(Path(tmp) / "ausente.ttf", self.spec_sha))


class DownloadTests(unittest.TestCase):
    """Descarga con red simulada: valida integridad y escritura atómica."""

    def setUp(self):
        import tempfile

        self._tmp = tempfile.TemporaryDirectory()
        self.cache = Path(self._tmp.name) / "fonts"
        self.cache.mkdir()
        self._orig_dir = font_manager.font_cache_dir
        self._orig_fetch = font_manager._fetch
        font_manager.font_cache_dir = lambda: self.cache
        self.addCleanup(self._restore)

    def _restore(self):
        font_manager.font_cache_dir = self._orig_dir
        font_manager._fetch = self._orig_fetch
        self._tmp.cleanup()

    def test_download_rejects_corrupted_payload(self):
        calls = []

        def fake_fetch(url, timeout):
            calls.append(url)
            return b"contenido corrupto"

        font_manager._fetch = fake_fetch
        result = font_manager.download_font("jetbrainsmono")
        self.assertIsNone(result)
        # Se probaron todos los espejos antes de rendirse.
        self.assertEqual(len(calls), len(font_manager.FONT_REGISTRY["jetbrainsmono"].urls()))

    def test_download_accepts_valid_payload_and_is_cached(self):
        spec = font_manager.FONT_REGISTRY["jetbrainsmono"]
        payload = b"contenido valido" * 128
        good = hashlib.sha256(payload).hexdigest()

        patched = font_manager.FontSpec(
            key=spec.key,
            family=spec.family,
            filename=spec.filename,
            sha256=good,
            size=len(payload),
            license=spec.license,
            license_url=spec.license_url,
            paths=spec.paths,
            kind=spec.kind,
        )
        font_manager.FONT_REGISTRY["jetbrainsmono"] = patched
        self.addCleanup(
            font_manager.FONT_REGISTRY.__setitem__, "jetbrainsmono", spec
        )
        font_manager._fetch = lambda url, timeout: payload

        path = font_manager.download_font("jetbrainsmono")
        self.assertIsNotNone(path)
        self.assertTrue(font_manager.is_cached("jetbrainsmono"))
        self.assertEqual(path.read_bytes(), payload)
        # No quedan archivos temporales sueltos.
        leftovers = [p for p in self.cache.iterdir() if p.suffix == ".part"]
        self.assertEqual(leftovers, [])

    def test_ensure_fonts_offline_returns_none_without_download(self):
        results = font_manager.ensure_fonts(download=False)
        self.assertTrue(results)
        self.assertTrue(all(path is None for path in results.values()))

    def test_ensure_fonts_offline_uses_existing_cache(self):
        spec = font_manager.FONT_REGISTRY["jetbrainsmono"]
        target = self.cache / spec.filename
        target.write_bytes(b"x")
        # Huella real no coincide: debe considerarse ausente.
        self.assertFalse(font_manager.is_cached("jetbrainsmono"))
        results = font_manager.ensure_fonts(["jetbrainsmono"], download=False)
        self.assertIsNone(results["jetbrainsmono"])


class OfflineImportTests(unittest.TestCase):
    def test_importing_font_manager_needs_no_network_or_application(self):
        env = dict(os.environ, QT_QPA_PLATFORM="offscreen")
        code = "import lib.font_manager as fm; print(sorted(fm.FONT_REGISTRY))"
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("roboto", result.stdout)
        self.assertNotIn("QFontDatabase", result.stderr)


if __name__ == "__main__":
    unittest.main()
