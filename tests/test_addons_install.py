# -*- coding: utf-8 -*-
"""Instalación de extensiones del sidebar desde Configuración (Q-022).

La segunda mitad de Q-022 permite instalar un manifiesto ``.yaml`` sin editar
la carpeta de la aplicación. Estas pruebas fijan el contrato del motor: qué se
valida antes de copiar, dónde se instala y qué ids no se pueden suplantar.
"""

import os
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.addons_engine import (  # noqa: E402
    AddonError,
    all_addons_dirs,
    install_addon,
    installed_addons,
    load_addons_from_dirs,
    user_addons_dir,
)


def _write(path: Path, body: str) -> Path:
    path.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")
    return path


VALID = """
id: extra
section: tools
order: 30
label: sidebar.extra
description: sidebar_desc.9
icon: help
builder: build_extra_page
"""


class FakeHost:
    def build_extra_page(self):
        return "page"


class InstallAddonTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.user_dir = self.root / "user"
        self._old_env = os.environ.get("PM_USER_ADDONS_DIR")
        os.environ["PM_USER_ADDONS_DIR"] = str(self.user_dir)

    def tearDown(self):
        if self._old_env is None:
            os.environ.pop("PM_USER_ADDONS_DIR", None)
        else:
            os.environ["PM_USER_ADDONS_DIR"] = self._old_env

    def _source(self, name="extra.yaml", body=VALID) -> Path:
        return _write(self.root / name, body)

    def test_valid_manifest_is_copied_to_the_user_directory(self):
        destination = install_addon(self._source(), host=FakeHost())
        self.assertEqual(destination, self.user_dir / "extra.yaml")
        self.assertTrue(destination.is_file())
        self.assertEqual(
            [a.id for a in load_addons_from_dirs(all_addons_dirs(), strict=True)],
            [
                "create", "build", "config", "moonfix",
                "report", "help", "aide", "extra", "about",
            ],
        )

    def test_install_leaves_no_temporary_file(self):
        install_addon(self._source(), host=FakeHost())
        leftovers = [p.name for p in self.user_dir.iterdir() if p.suffix != ".yaml"]
        self.assertEqual(leftovers, [])

    def test_installed_addons_ignores_the_shipped_fallback(self):
        self.assertEqual(installed_addons(), [])
        install_addon(self._source(), host=FakeHost())
        self.assertEqual([a.id for a in installed_addons()], ["extra"])

    def test_reinstall_replaces_the_previous_manifest(self):
        install_addon(self._source(), host=FakeHost())
        changed = VALID.replace("order: 30", "order: 60")
        install_addon(self._source(body=changed), host=FakeHost())
        addons = installed_addons()
        self.assertEqual([(a.id, a.order) for a in addons], [("extra", 60)])
        self.assertEqual(len(list(self.user_dir.glob("*.yaml"))), 1)

    def test_rejects_a_manifest_without_a_builder(self):
        source = self._source(body=VALID.replace("builder: build_extra_page\n", ""))
        with self.assertRaises(AddonError):
            install_addon(source, host=FakeHost())
        self.assertFalse(self.user_dir.exists())

    def test_rejects_an_id_that_belongs_to_a_shipped_addon(self):
        source = self._source(
            "config.yaml", VALID.replace("id: extra", "id: config")
        )
        with self.assertRaises(AddonError) as caught:
            install_addon(source, host=FakeHost())
        self.assertIn("incluido", str(caught.exception))
        self.assertFalse(self.user_dir.exists())

    def test_rejects_a_builder_the_host_does_not_have(self):
        with self.assertRaises(AddonError) as caught:
            install_addon(self._source(), host=object())
        self.assertIn("build_extra_page", str(caught.exception))

    def test_accepts_a_class_manifest_without_importing_it(self):
        body = """
        id: extra
        section: tools
        order: 30
        label: sidebar.extra
        class: lib.help_page:HelpPage
        """
        destination = install_addon(self._source(body=body), host=FakeHost())
        self.assertTrue(destination.is_file())

    def test_rejects_a_malformed_class_reference(self):
        body = """
        id: extra
        section: tools
        order: 30
        label: sidebar.extra
        class: lib.help_page
        """
        with self.assertRaises(AddonError) as caught:
            install_addon(self._source(body=body), host=FakeHost())
        self.assertIn("modulo:Clase", str(caught.exception))

    def test_rejects_a_plugin_manifest(self):
        body = """
        id: extra
        section: tools
        order: 30
        label: sidebar.extra
        plugin: extra.py
        """
        with self.assertRaises(AddonError) as caught:
            install_addon(self._source(body=body), host=FakeHost())
        self.assertIn("plugin", str(caught.exception))

    def test_rejects_a_disabled_manifest(self):
        source = self._source(body=VALID + "enabled: false\n")
        with self.assertRaises(AddonError):
            install_addon(source, host=FakeHost())

    def test_rejects_a_file_that_is_not_yaml(self):
        source = self._source("extra.txt", VALID)
        with self.assertRaises(AddonError):
            install_addon(source, host=FakeHost())

    def test_rejects_invalid_yaml(self):
        source = self._source(body="id: [sin cerrar\n")
        with self.assertRaises(AddonError):
            install_addon(source, host=FakeHost())

    def test_rejects_a_manifest_whose_id_does_not_match_the_file(self):
        source = self._source("otro.yaml", VALID)
        with self.assertRaises(AddonError):
            install_addon(source, host=FakeHost())


class UserDirectoryTest(unittest.TestCase):
    def test_user_directory_is_the_last_one(self):
        directories = all_addons_dirs()
        self.assertEqual(directories[-1], user_addons_dir())
        self.assertNotIn(user_addons_dir(), directories[:-1])

    def test_environment_override_wins(self):
        old = os.environ.get("PM_USER_ADDONS_DIR")
        try:
            os.environ["PM_USER_ADDONS_DIR"] = "/tmp/pm-addons-test"
            self.assertEqual(user_addons_dir(), Path("/tmp/pm-addons-test"))
        finally:
            if old is None:
                os.environ.pop("PM_USER_ADDONS_DIR", None)
            else:
                os.environ["PM_USER_ADDONS_DIR"] = old

    def test_installed_addons_does_not_need_the_directory(self):
        old = os.environ.get("PM_USER_ADDONS_DIR")
        try:
            os.environ["PM_USER_ADDONS_DIR"] = "/tmp/pm-addons-no-existe"
            self.assertEqual(installed_addons(), [])
        finally:
            if old is None:
                os.environ.pop("PM_USER_ADDONS_DIR", None)
            else:
                os.environ["PM_USER_ADDONS_DIR"] = old


if __name__ == "__main__":
    unittest.main()
