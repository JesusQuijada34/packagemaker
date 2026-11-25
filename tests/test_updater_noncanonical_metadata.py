# -*- coding: utf-8 -*-
"""El updater no debe lanzar tracebacks con metadatos no canónicos.

Dos defectos del mismo origen:

* ``_fR`` pasaba la versión/publisher/app remotos a
  ``ProjectNameFormatter.format_iflapp_filename``, que lanza ``ValueError`` si no
  son canónicos (una etiqueta ``1.0 beta``, un publisher ``My Company.``). La
  excepción escapaba de ``updater.py --check`` y de ``--silent``.
* ``_check_url_exists`` (respaldo sin ``requests``) dejaba escapar
  ``UnicodeEncodeError`` con una URL no ASCII y ``http.client.InvalidURL`` con
  espacios o un byte NUL.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


class NonCanonicalMetadataTests(unittest.TestCase):
    def setUp(self):
        from lib.coreUpdater import core

        self.core = core

    def test_noncanonical_version_returns_none_without_network(self):
        with mock.patch.object(
            self.core, "_check_url_exists", side_effect=AssertionError("sin red")
        ):
            self.assertIsNone(
                self.core._fR("Influent", "demo", "1.0 beta", "Danenone", "Influent")
            )

    def test_noncanonical_publisher_returns_none(self):
        with mock.patch.object(
            self.core, "_check_url_exists", side_effect=AssertionError("sin red")
        ):
            self.assertIsNone(
                self.core._fR("Influent", "demo", "v1.0", "Danenone", "My Company.")
            )

    def test_noncanonical_app_returns_none(self):
        with mock.patch.object(
            self.core, "_check_url_exists", side_effect=AssertionError("sin red")
        ):
            self.assertIsNone(
                self.core._fR("Influent", "my/app", "v1.0", "Danenone", "Influent")
            )

    def test_canonical_metadata_still_builds_the_url(self):
        with mock.patch.object(self.core, "_check_url_exists", return_value=True):
            url = self.core._fR(
                "Influent", "demo", "v1.0-26.11-06.00", "Danenone", "Influent"
            )
        self.assertIsNotNone(url)
        self.assertTrue(url.endswith("Influent.demo.v1.0-26.11-06.00-Danenone.iflapp"))
        self.assertIn("/releases/download/v1.0-26.11-06.00/", url)


class UrlProbeTests(unittest.TestCase):
    """El respaldo ``urllib`` (sin ``requests``) trata la URL imposible como ausente."""

    def setUp(self):
        from lib.coreUpdater import core

        self.core = core
        patcher = mock.patch.object(core, "requests", None)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_non_ascii_url_does_not_raise(self):
        self.assertFalse(
            self.core._check_url_exists("https://example.invalid/Jes\u00fas.iflapp")
        )

    def test_space_in_url_does_not_raise(self):
        self.assertFalse(
            self.core._check_url_exists("https://example.invalid/Nandu Labs.iflapp")
        )

    def test_null_byte_in_url_does_not_raise(self):
        self.assertFalse(
            self.core._check_url_exists("https://example.invalid/a\x00b.iflapp")
        )


class CheckCommandTests(unittest.TestCase):
    """``updater.py --check`` informa en vez de imprimir un traceback."""

    def setUp(self):
        import updater

        self.updater = updater
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base = Path(self._tmp.name)
        (self.base / "details.xml").write_text(
            "<details><publisher>Influent</publisher><app>demo</app>"
            "<name>Demo</name><version>v1.0</version>"
            "<platform>AlphaCube</platform><author>Influent</author></details>",
            encoding="utf-8",
        )
        self._cwd = os.getcwd()
        os.chdir(self.base)
        self.addCleanup(os.chdir, self._cwd)

    def test_check_with_noncanonical_remote_version_exits_cleanly(self):
        with mock.patch.object(self.updater, "_rXml_r", return_value="1.0 beta"), \
             mock.patch.object(self.updater, "_fR_exe", return_value=(None, None)), \
             mock.patch("sys.argv", ["updater.py", "--check"]):
            with self.assertRaises(SystemExit) as ctx:
                self.updater.main()
        self.assertEqual(ctx.exception.code, 0)

    def test_check_with_accented_remote_version_exits_cleanly(self):
        with mock.patch.object(self.updater, "_rXml_r", return_value="1.0 Jes\u00fas"), \
             mock.patch.object(self.updater, "_fR_exe", return_value=(None, None)), \
             mock.patch("sys.argv", ["updater.py", "--check"]):
            with self.assertRaises(SystemExit) as ctx:
                self.updater.main()
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
