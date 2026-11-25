# -*- coding: utf-8 -*-
"""Motor de addons: manifiestos YAML, orden y aislamiento de fallos."""

import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib import addons_engine
from lib.addons_engine import Addon, AddonError, load_addons, parse_manifest


def _write(directory: Path, name: str, body: str) -> Path:
    path = directory / name
    path.write_text(textwrap.dedent(body), encoding="utf-8")
    return path


class ManifestValidationTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_minimal_manifest_is_accepted(self):
        path = _write(
            self.dir,
            "demo.yaml",
            """
            id: demo
            label: sidebar.demo
            builder: build_demo_page
            """,
        )
        addon = parse_manifest(
            addons_engine.yaml.safe_load(path.read_text(encoding="utf-8")), path
        )
        self.assertEqual(addon.id, "demo")
        self.assertEqual(addon.section, "tools")
        self.assertEqual(addon.order, 100)
        self.assertEqual(addon.kind, "builder")

    def test_id_must_match_filename(self):
        path = _write(
            self.dir,
            "demo.yaml",
            """
            id: otro
            label: sidebar.demo
            builder: build_demo_page
            """,
        )
        with self.assertRaises(AddonError) as ctx:
            parse_manifest(
                addons_engine.yaml.safe_load(path.read_text(encoding="utf-8")), path
            )
        self.assertIn("nombre del fichero", str(ctx.exception))

    def test_invalid_id_characters_are_rejected(self):
        path = _write(
            self.dir,
            "Demo-2.yaml",
            """
            id: Demo-2
            label: sidebar.demo
            builder: build_demo_page
            """,
        )
        with self.assertRaises(AddonError):
            parse_manifest(
                addons_engine.yaml.safe_load(path.read_text(encoding="utf-8")), path
            )

    def test_missing_label_is_reported(self):
        path = _write(self.dir, "demo.yaml", "id: demo\nbuilder: x\n")
        with self.assertRaises(AddonError) as ctx:
            parse_manifest(
                addons_engine.yaml.safe_load(path.read_text(encoding="utf-8")), path
            )
        self.assertIn("label", str(ctx.exception))

    def test_missing_builder_is_reported(self):
        path = _write(self.dir, "demo.yaml", "id: demo\nlabel: sidebar.demo\n")
        with self.assertRaises(AddonError) as ctx:
            parse_manifest(
                addons_engine.yaml.safe_load(path.read_text(encoding="utf-8")), path
            )
        self.assertIn("builder, class o plugin", str(ctx.exception))

    def test_two_construction_kinds_are_rejected(self):
        path = _write(
            self.dir,
            "demo.yaml",
            """
            id: demo
            label: sidebar.demo
            builder: build_demo_page
            class: "lib.x:Y"
            """,
        )
        with self.assertRaises(AddonError) as ctx:
            parse_manifest(
                addons_engine.yaml.safe_load(path.read_text(encoding="utf-8")), path
            )
        self.assertIn("sólo uno", str(ctx.exception))

    def test_unknown_section_is_rejected(self):
        path = _write(
            self.dir,
            "demo.yaml",
            """
            id: demo
            section: lateral
            label: sidebar.demo
            builder: build_demo_page
            """,
        )
        with self.assertRaises(AddonError):
            parse_manifest(
                addons_engine.yaml.safe_load(path.read_text(encoding="utf-8")), path
            )

    def test_disabled_addon_is_skipped(self):
        path = _write(
            self.dir,
            "demo.yaml",
            """
            id: demo
            enabled: false
            label: sidebar.demo
            builder: build_demo_page
            """,
        )
        self.assertIsNone(
            parse_manifest(
                addons_engine.yaml.safe_load(path.read_text(encoding="utf-8")), path
            )
        )


class LoadOrderTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _manifest(self, name, section, order):
        _write(
            self.dir,
            f"{name}.yaml",
            f"""
            id: {name}
            section: {section}
            order: {order}
            label: sidebar.{name}
            builder: build_{name}_page
            """,
        )

    def test_sections_then_order(self):
        self._manifest("zulu", "footer", 10)
        self._manifest("alfa", "main", 20)
        self._manifest("bravo", "main", 10)
        self._manifest("charlie", "tools", 10)
        ids = [a.id for a in load_addons(self.dir, strict=True)]
        self.assertEqual(ids, ["bravo", "alfa", "charlie", "zulu"])

    def test_gaps_allow_inserting_without_renumbering(self):
        self._manifest("uno", "main", 10)
        self._manifest("tres", "main", 30)
        _write(
            self.dir,
            "dos.yaml",
            """
            id: dos
            section: main
            order: 20
            label: sidebar.dos
            builder: build_dos_page
            """,
        )
        self.assertEqual(
            [a.id for a in load_addons(self.dir, strict=True)], ["uno", "dos", "tres"]
        )

    def test_broken_manifest_is_skipped_but_others_load(self):
        self._manifest("bueno", "main", 10)
        _write(self.dir, "roto.yaml", "id: roto\nlabel: x\n")
        addons = load_addons(self.dir)
        self.assertEqual([a.id for a in addons], ["bueno"])
        self.assertTrue(Addon.skipped)
        self.assertIn("roto.yaml", Addon.skipped[0])

    def test_strict_mode_raises_on_broken_manifest(self):
        _write(self.dir, "roto.yaml", "id: roto\nlabel: x\n")
        with self.assertRaises(AddonError):
            load_addons(self.dir, strict=True)

    def test_missing_directory_falls_back_to_builtin_addons(self):
        # Un bundle sin addons/ no debe abrir la ventana con el sidebar vacío.
        addons = load_addons(self.dir / "no_existe")
        self.assertEqual(
            [a.id for a in addons],
            ["create", "build", "config", "moonfix", "report", "aide", "about"],
        )
        self.assertTrue(all(a.builder for a in addons))

    def test_empty_directory_falls_back_to_builtin_addons(self):
        self.assertEqual(len(load_addons(self.dir)), 7)

    def test_strict_mode_does_not_fall_back(self):
        self.assertEqual(load_addons(self.dir / "no_existe", strict=True), [])

    def test_equal_order_falls_back_to_id(self):
        self._manifest("zulu", "main", 10)
        self._manifest("alfa", "main", 10)
        self.assertEqual(
            [a.id for a in load_addons(self.dir, strict=True)], ["alfa", "zulu"]
        )


class RealAddonsTest(unittest.TestCase):
    """Los manifiestos que viajan con la app deben ser válidos."""

    def test_shipped_addons_are_valid(self):
        directory = Path(__file__).resolve().parents[1] / "addons"
        self.assertTrue(directory.is_dir(), "falta el directorio addons/")
        problems = addons_engine.validate_directory(directory)
        self.assertEqual(problems, [])

    def test_shipped_addons_have_expected_ids(self):
        directory = Path(__file__).resolve().parents[1] / "addons"
        ids = [a.id for a in load_addons(directory, strict=True)]
        self.assertEqual(
            ids, ["create", "build", "config", "moonfix", "report", "aide", "about"]
        )

    def test_every_shipped_addon_points_to_a_real_builder(self):
        directory = Path(__file__).resolve().parents[1] / "addons"
        for addon in load_addons(directory, strict=True):
            self.assertEqual(addon.kind, "builder", addon.id)
            self.assertTrue(addon.builder.startswith("build_"), addon.id)
            self.assertTrue(addon.label.startswith("sidebar."), addon.id)


class PluginTest(unittest.TestCase):
    def test_python_plugin_receives_host(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "extra.py").write_text(
                textwrap.dedent(
                    """
                    def build(host):
                        return ("plugin", host)
                    """
                ),
                encoding="utf-8",
            )
            _write(
                directory,
                "extra.yaml",
                """
                id: extra
                label: sidebar.extra
                plugin: extra.py
                """,
            )
            addon = load_addons(directory, strict=True)[0]
            self.assertEqual(addon.kind, "plugin")
            self.assertEqual(addon.build("host-falso"), ("plugin", "host-falso"))

    def test_plugin_without_build_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "vacio.py").write_text("X = 1\n", encoding="utf-8")
            _write(
                directory,
                "vacio.yaml",
                """
                id: vacio
                label: sidebar.vacio
                plugin: vacio.py
                """,
            )
            addon = load_addons(directory, strict=True)[0]
            with self.assertRaises(AddonError):
                addon.build("host")

    def test_missing_builder_on_host_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            _write(
                directory,
                "fantasma.yaml",
                """
                id: fantasma
                label: sidebar.fantasma
                builder: no_existe
                """,
            )
            addon = load_addons(directory, strict=True)[0]

            class Host:
                pass

            with self.assertRaises(AddonError) as ctx:
                addon.build(Host())
            self.assertIn("no_existe", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
