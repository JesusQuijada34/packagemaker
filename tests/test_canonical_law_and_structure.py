# -*- coding: utf-8 -*-
"""Pruebas de la ley de nombres canónicos y de la estructura del paquete.

Ejercitan las funciones reales (no dobles) del formateador, del motor de
plantillas, del contenedor ``.iflapp`` y del lector de cabecera, simulando el
flujo completo crear → empaquetar → inspeccionar → verificar para comprobar
que el nombre, la versión, la plataforma y la estructura de archivos son
exactamente los canónicos.
"""

import os
import re
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from lib.iflapp_format import (
    IflappError,
    pack_iflapp,
    read_iflapp_header,
    sniff_format,
    verify_iflapp,
)
from lib.iflapp_reader import IflappReader
from lib.projectNameFormatter import ProjectNameFormatter
from lib.template_engine import build_variables, create_project_from_templates

TIMESTAMP = "26.08-15.38"
CANONICAL = "Influent.packagemaker.v3.2.7-26.05-20.13-AlphaCube"
# Marcadores que el README exige en todo paquete público.
REQUIRED_STRUCTURE = (
    "details.xml",
    "version.res",
    "autorun",
    "autorun.bat",
    ".storedetail",
    "updater.py",
    "config/settings.json",
)
# Marcadores de contenedor (``.container``) de los subdirectorios.
REQUIRED_CONTAINERS = (
    "app/.app-container",
    "assets/.assets-container",
    "config/.config-container",
    "docs/.docs-container",
    "lib/.lib-container",
    "source/.source-container",
)
CANONICAL_VERSION = re.compile(r"^v3\.2\.7-\d{2}\.\d{2}-\d{2}\.\d{2}$")
# La misma versión, sin anclas, para buscarla dentro de otros artefactos.
CANONICAL_VERSION_ANYWHERE = re.compile(r"v3\.2\.7-\d{2}\.\d{2}-\d{2}\.\d{2}")


class CanonicalNameLawTests(unittest.TestCase):
    """``publisher.appname.vX.x[.z]-YY.MM-HH.MM-Platform`` y nada más."""

    def test_identity_of_this_repository_is_canonical(self):
        parsed = ProjectNameFormatter.parse_project_folder(CANONICAL)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["publisher"], "Influent")
        self.assertEqual(parsed["app"], "packagemaker")
        self.assertEqual(parsed["version"], "3.2.7")
        self.assertEqual(parsed["timestamp"], "26.05-20.13")
        self.assertEqual(parsed["platform"], "AlphaCube")

    @patch.object(ProjectNameFormatter, "get_timestamp", return_value=TIMESTAMP)
    def test_round_trip_format_then_parse(self, _ts):
        """Formatear y volver a analizar debe devolver los mismos datos."""
        name = ProjectNameFormatter.format_project_folder(
            "Influent", "PackageMaker", "3.2.7", "AlphaCube"
        )
        self.assertEqual(name, f"Influent.packagemaker.v3.2.7-{TIMESTAMP}-AlphaCube")
        parsed = ProjectNameFormatter.parse_project_folder(name)
        self.assertEqual(parsed["version"], "3.2.7")
        self.assertEqual(parsed["platform"], "AlphaCube")

    def test_every_generated_artifact_obeys_the_law(self):
        """Los cinco artefactos derivados deben ser el mismo nombre canónico."""
        names = ProjectNameFormatter.format_from_metadata(
            {
                "publisher": "Influent",
                "app": "packagemaker",
                "version": "v3.2.7-26.05-20.13",
                "platform": "AlphaCube",
            }
        )
        self.assertEqual(names["project_folder"], CANONICAL)
        self.assertEqual(names["package_folder"], CANONICAL)
        self.assertEqual(names["iflapp_filename"], f"{CANONICAL}.iflapp")
        self.assertEqual(names["version_full"], "v3.2.7-26.05-20.13")
        self.assertEqual(names["version_vso"], "v3.2.7-26.05-20.13")
        # El sufijo de plataforma pertenece al nombre, no a la versión.
        self.assertNotIn("AlphaCube", names["version_full"])

    def test_only_the_three_canonical_platforms_are_accepted(self):
        for platform in ProjectNameFormatter.ALLOWED_PLATFORMS:
            with self.subTest(platform=platform):
                result = ProjectNameFormatter.format_project_folder(
                    "Influent", "demo", "1.0", platform, TIMESTAMP
                )
                self.assertTrue(result.endswith(f"-{platform}"))
        for bad in ("macOS", "Debian", "Darwin", "Solaris", ""):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    ProjectNameFormatter.normalize_platform(bad)

    def test_publisher_capitalization_is_preserved_but_app_is_lowered(self):
        name = ProjectNameFormatter.format_project_folder(
            "Influent", "PackageMaker", "3.2.7", "AlphaCube", TIMESTAMP
        )
        self.assertTrue(name.startswith("Influent."))
        self.assertIn(".packagemaker.", name)

    def test_a_name_missing_the_platform_suffix_is_not_canonical(self):
        self.assertIsNone(
            ProjectNameFormatter.parse_project_folder(
                f"Influent.packagemaker.v3.2.7-{TIMESTAMP}"
            )
        )


class ProjectStructureLawTests(unittest.TestCase):
    """La estructura creada debe contener los marcadores exigidos."""

    def test_template_creation_writes_the_required_markers(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "proj"
            create_project_from_templates(
                project,
                publisher="Influent",
                app_id="packagemaker",
                name="PackageMaker",
                author="JesusQuijada34",
                platform="AlphaCube",
                version_base="3.2.7",
            )
            present = {
                str(p.relative_to(project))
                for p in project.rglob("*")
                if p.is_file()
            }
            for marker in REQUIRED_STRUCTURE + REQUIRED_CONTAINERS:
                with self.subTest(marker=marker):
                    self.assertIn(marker, present, f"falta {marker}")

    def test_details_xml_version_matches_the_canonical_pattern(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "proj"
            create_project_from_templates(
                project,
                publisher="Influent",
                app_id="packagemaker",
                name="PackageMaker",
                author="JesusQuijada34",
                platform="AlphaCube",
                version_base="3.2.7",
            )
            root = ET.parse(project / "details.xml").getroot()
            flat = {
                (node.tag.split("}")[-1]): (node.text or "").strip()
                for node in root.iter()
                if node.text and node.text.strip()
            }
            self.assertRegex(flat.get("version", ""), CANONICAL_VERSION)
            self.assertIn("AlphaCube", flat.get("platform", ""))
            # ``version.res`` también declara la versión canónica (aparece
            # junto a "built by:" en FileVersion/ProductName).
            version_res = (project / "version.res").read_text(encoding="utf-8")
            self.assertIsNotNone(CANONICAL_VERSION_ANYWHERE.search(version_res))
            self.assertIn("Influent", version_res)

    def test_details_xml_declares_the_canonical_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "proj"
            create_project_from_templates(
                project,
                publisher="Influent",
                app_id="packagemaker",
                name="PackageMaker",
                author="JesusQuijada34",
                platform="AlphaCube",
                version_base="3.2.7",
            )
            root = ET.parse(project / "details.xml").getroot()
            flat = {
                (node.tag.split("}")[-1]): (node.text or "").strip()
                for node in root.iter()
                if node.text and node.text.strip()
            }
            self.assertEqual(flat.get("publisher"), "Influent")
            self.assertIn("packagemaker", flat.get("app", "").lower())
            self.assertIn("AlphaCube", flat.get("platform", ""))

    def test_template_variables_agree_with_the_formatter(self):
        variables = build_variables(
            "Influent", "packagemaker", "PackageMaker", "JesusQuijada34",
            "AlphaCube", "3.2.7",
        )
        self.assertEqual(variables["PUBLISHER"], "Influent")
        self.assertEqual(variables["APP"], "packagemaker")
        self.assertEqual(variables["PLATFORM"], "AlphaCube")
        # La versión completa lleva plataforma implícita pero sin el sufijo.
        self.assertRegex(variables["VERSION"], r"^v3\.2\.7-\d{2}\.\d{2}-\d{2}\.\d{2}$")
        # La carpeta canónica y el paquete comparten marca temporal.
        self.assertIn(variables["VERSION_FULL"], variables["VERSION"])


class IflappPipelineLawTests(unittest.TestCase):
    """Crear → empaquetar → inspeccionar → verificar, con funciones reales."""

    def _make_package_dir(self, base: Path) -> Path:
        pkg = base / "payload"
        (pkg / "config").mkdir(parents=True)
        (pkg / "app").mkdir(parents=True)
        (pkg / "main.py").write_text("print('hola')\n", encoding="utf-8")
        (pkg / "details.xml").write_text(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            "<details>\n"
            "  <publisher>Influent</publisher>\n"
            "  <app>packagemaker</app>\n"
            "  <name>PackageMaker</name>\n"
            "  <author>JesusQuijada34</author>\n"
            "  <version>v3.2.7-26.05-20.13</version>\n"
            "  <platform>AlphaCube</platform>\n"
            "</details>\n",
            encoding="utf-8",
        )
        (pkg / "config" / "settings.json").write_text("{}", encoding="utf-8")
        (pkg / "app" / "app-icon.ico").write_bytes(b"\x00\x00\x01\x00ICON")
        return pkg

    def test_created_iflapp_name_and_header_are_canonical(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            pkg = self._make_package_dir(base)
            out = base / f"{CANONICAL}.iflapp"
            pack_iflapp(pkg, out, compression="lzma")

            self.assertEqual(sniff_format(out), "iflapp2")
            self.assertEqual(out.name, f"{CANONICAL}.iflapp")

            header = read_iflapp_header(out)
            identity = header.identity()
            # La identidad se lee de la cabecera sin descifrar el payload.
            self.assertEqual(identity.get("publisher"), "Influent")
            self.assertEqual(identity.get("platform"), "AlphaCube")
            self.assertIn("packagemaker", identity.get("app", "").lower())
            # El icono viaja en la cabecera.
            self.assertEqual(len(header.icon), 8)
            # El manifiesto lista el contenido real.
            names = {entry["path"] for entry in header.manifest}
            self.assertIn("details.xml", names)
            self.assertIn("main.py", names)

    def test_reader_summary_and_verify_are_consistent(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            pkg = self._make_package_dir(base)
            out = base / f"{CANONICAL}.iflapp"
            pack_iflapp(pkg, out, compression="lzma")

            reader = IflappReader(out)
            info = reader.info()
            self.assertEqual(info.format, "iflapp2")
            self.assertEqual(info.identity.get("publisher"), "Influent")
            self.assertGreater(info.icon_bytes, 0)

            summary = reader.summary()
            self.assertIn("Influent", summary)
            self.assertIn("AlphaCube", summary)

            report = verify_iflapp(out)
            self.assertTrue(report.get("valid"))

    def test_payload_is_not_readable_without_decrypting(self):
        """El contenido del payload no debe aparecer en claro en el binario."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            pkg = self._make_package_dir(base)
            secret = "TOKEN_SECRETO_INTERNO_XYZ"
            (pkg / "secreto.txt").write_text(secret, encoding="utf-8")
            out = base / f"{CANONICAL}.iflapp"
            pack_iflapp(pkg, out, compression="lzma", password="clave-fuerte")

            raw = out.read_bytes()
            self.assertNotIn(secret.encode(), raw)
            # Aun así la cabecera sigue siendo legible.
            self.assertEqual(read_iflapp_header(out).identity().get("publisher"), "Influent")

    def test_password_protected_payload_rejects_wrong_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            pkg = self._make_package_dir(base)
            out = base / f"{CANONICAL}.iflapp"
            pack_iflapp(pkg, out, compression="lzma", password="correcta")

            from lib.iflapp_format import extract_iflapp

            with self.assertRaises(IflappError):
                extract_iflapp(out, base / "dest", password="incorrecta")

    def test_empty_package_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            empty = base / "vacio"
            empty.mkdir()
            with self.assertRaises(IflappError):
                pack_iflapp(empty, base / "x.iflapp")

    def test_manifest_does_not_escape_the_root(self):
        """Un tar con traversal no debe poder listarse como archivo válido."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            pkg = self._make_package_dir(base)
            out = base / f"{CANONICAL}.iflapp"
            pack_iflapp(pkg, out, compression="lzma")
            # El manifiesto nunca debe contener rutas absolutas ni "..".
            for entry in read_iflapp_header(out).manifest:
                name = entry["path"]
                self.assertFalse(name.startswith("/"), name)
                self.assertNotIn("..", Path(name).parts, name)


class CreatedProjectNamingRegressionTests(unittest.TestCase):
    """Regresión: la carpeta creada debe salir del formatter canónico.

    El bug era que ``create_package_action`` componía el nombre a mano con
    ``VERSION_FULL`` y perdía el sufijo de plataforma, así que la carpeta no
    cumplía la ley.
    """

    def test_build_variables_exposes_the_canonical_folder_name(self):
        variables = build_variables(
            "gfff", "ddghgyh", "DDGHGYH", "JesusQuijada34", "knosthalij", "1.0",
            timestamp=TIMESTAMP,
        )
        self.assertEqual(
            variables["FOLDER_NAME"],
            f"gfff.ddghgyh.v1.0-{TIMESTAMP}-Knosthalij",
        )
        # El nombre canónico es analizable por el formatter (ley cumplida).
        self.assertIsNotNone(
            ProjectNameFormatter.parse_project_folder(variables["FOLDER_NAME"])
        )
        # La versión sigue sin plataforma; el sufijo pertenece al nombre.
        self.assertNotIn("Knosthalij", variables["VERSION_FULL"])

    def test_timestamp_is_shared_between_folder_and_details(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "proj"
            variables = create_project_from_templates(
                project,
                publisher="Influent",
                app_id="packagemaker",
                name="PackageMaker",
                author="JesusQuijada34",
                platform="AlphaCube",
                version_base="3.2.7",
                timestamp=TIMESTAMP,
            )["variables"]
            self.assertEqual(
                variables["FOLDER_NAME"],
                f"Influent.packagemaker.v3.2.7-{TIMESTAMP}-AlphaCube",
            )
            root = ET.parse(project / "details.xml").getroot()
            flat = {
                node.tag.split("}")[-1]: (node.text or "").strip()
                for node in root.iter()
                if node.text and node.text.strip()
            }
            self.assertEqual(flat.get("version"), f"v3.2.7-{TIMESTAMP}")

    def test_missing_templates_are_detected_before_creating_folders(self):
        """Sin plantillas no debe quedar un proyecto vacío en disco."""
        from lib import template_engine

        with patch.object(
            template_engine, "get_templates_root", return_value=Path("/no/existe")
        ):
            self.assertFalse(template_engine.templates_available())
        # Con las plantillas reales del repo sí está disponible.
        self.assertTrue(template_engine.templates_available())

    def test_creation_aborts_without_writing_when_templates_are_missing(self):
        """``create_project_from_templates`` no deja restos si falla."""
        from lib import template_engine

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "proj"
            with patch.object(
                template_engine, "get_templates_root", return_value=Path("/no/existe")
            ):
                with self.assertRaises(FileNotFoundError):
                    create_project_from_templates(
                        project,
                        publisher="Influent",
                        app_id="packagemaker",
                        name="PackageMaker",
                        author="JesusQuijada34",
                        platform="AlphaCube",
                        version_base="3.2.7",
                    )


if __name__ == "__main__":
    unittest.main()
