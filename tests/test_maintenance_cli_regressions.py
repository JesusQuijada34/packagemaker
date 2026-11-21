# -*- coding: utf-8 -*-
"""Regresiones de mantenimiento del CLI headless.

Cubre defectos detectados en la auditoría de este ciclo:

- ``R-4b7e91a2``: el banner de plataforma contaminaba la salida JSON.
- ``R-9c1d5f60``: ``create`` no copiaba el icono si se lanzaba fuera del repo.
- ``R-2e83a7bd``: el subcomando ``compile`` ignoraba la salida de Termux.
- ``R-a5f06c38``: un método de ``--harden`` mal escrito desactivaba el blindaje
  en silencio.
- ``R-d74e0b19``: ``--ide-compile`` imprimía cada línea dos veces.
- ``R-3a7c5e18``: la ausencia de ``leviathan_ui`` contaminaba stdout y rompía
  todas las acciones ``*-json``.
- ``R-9f2b64d1``: ``--inspect-extract``/``--shell-preview`` añadían texto humano
  al JSON de stdout.
- ``R-6e04c8ab``: el aviso de ``moonfix`` con ``details.xml`` corrupto usaba un
  símbolo no representable en consolas cp1252 y abortaba el comando.
"""

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

DETAILS = """<?xml version="1.0" encoding="utf-8"?>
<app>
  <publisher>Influent</publisher>
  <app>demo</app>
  <name>demo</name>
  <version>1.0.0</version>
  <platform>Danenone</platform>
  <author>JesusQuijada34</author>
</app>
"""


class CreateIconOutsideRepoRootTests(unittest.TestCase):
    """R-9c1d5f60: el icono debe copiarse aunque el CWD no sea la raíz."""

    def test_create_copies_icon_from_any_working_directory(self):
        from lib.cliHandler import handle_cli_action

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "projects"
            base.mkdir()
            elsewhere = Path(tmp) / "elsewhere"
            elsewhere.mkdir()
            original = os.getcwd()
            os.chdir(elsewhere)
            try:
                with redirect_stdout(io.StringIO()):
                    handle_cli_action(
                        "create_project",
                        {
                            "path": str(base),
                            "name": "Cwd Test",
                            "shortname": "cwd-test",
                            "version": "1.0.0",
                            "author": "JesusQuijada34",
                            "publisher": "Influent",
                            "platform": "Danenone",
                            "description": "proyecto de prueba",
                        },
                        None,
                        headless=True,
                    )
            finally:
                os.chdir(original)

            projects = list(base.glob("influent.cwd-test.*"))
            self.assertEqual(len(projects), 1, "no se creó el proyecto")
            icon = projects[0] / "app" / "app-icon.ico"
            self.assertTrue(icon.is_file(), "el icono por defecto no se copió")
            self.assertGreater(icon.stat().st_size, 0)


class CompileSubcommandOutputDirectoryTests(unittest.TestCase):
    """R-2e83a7bd: ``compile`` usa la misma salida que ``--buildthis``."""

    def test_compile_uses_platform_output_directory(self):
        from lib.cliHandler import handle_cli_action

        class _RecordingCompiler:
            instances = []

            def __init__(self, project_path, output_path, **kwargs):
                self.output_path = Path(output_path)
                type(self).instances.append(self)

            def parse_details_xml(self):
                return False

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "projects"
            project = base / "influent.demoapp.v1.0.0-26.11-04.08-Danenone"
            project.mkdir(parents=True)
            (project / "details.xml").write_text(DETAILS, encoding="utf-8")
            shared_output = Path(tmp) / "shared-download"

            _RecordingCompiler.instances = []
            with patch("lib.blindcubeEngine.BuildThread.FlangCompiler", _RecordingCompiler), patch(
                "lib.platform_detect.compile_output_directory",
                return_value=str(shared_output),
            ):
                with redirect_stdout(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        handle_cli_action(
                            "compile_project",
                            {
                                "path": str(base),
                                "name": "Demo App",
                                "shortname": "demoapp",
                                "publisher": "Influent",
                            },
                            None,
                            headless=True,
                        )

            self.assertTrue(_RecordingCompiler.instances)
            compiler = _RecordingCompiler.instances[0]
            self.assertEqual(compiler.output_path, shared_output.resolve())
            self.assertTrue(shared_output.is_dir())


class IdeCompileLoggingTests(unittest.TestCase):
    """R-d74e0b19: cada línea del log debe imprimirse una sola vez."""

    def test_ide_compile_prints_each_line_once(self):
        from lib.cliHandler import IflappIdeHelper

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "influent.demo.v1.0.0-26.11-04.08-Danenone"
            project.mkdir()
            (project / "details.xml").write_text(DETAILS, encoding="utf-8")
            (project / "demo.py").write_text("print('demo')\n", encoding="utf-8")
            output = Path(tmp) / "out"

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                ok = IflappIdeHelper.compile(
                    {"path": str(project), "backend": "zipapp", "output": str(output)}
                )
            text = buffer.getvalue()

            self.assertTrue(ok)
            self.assertEqual(text.count("[INFO] Compilando demo.py"), 1)
            self.assertEqual(text.count("[OK]"), 1)


class HardeningParseWarningTests(unittest.TestCase):
    """R-a5f06c38: los métodos desconocidos no deben pasar en silencio."""

    def test_unknown_method_is_reported_and_filtered(self):
        from lib.cliHandler import CLIHandler

        handler = CLIHandler()
        buffer = io.StringIO()
        with redirect_stderr(buffer):
            parsed = handler._parse_hardening("strip,bogus")
        self.assertEqual(parsed, ["strip"])
        self.assertIn("bogus", buffer.getvalue())

    def test_all_unknown_methods_disable_hardening_with_warning(self):
        from lib.cliHandler import CLIHandler

        handler = CLIHandler()
        buffer = io.StringIO()
        with redirect_stderr(buffer):
            parsed = handler._parse_hardening("bogus")
        self.assertEqual(parsed, [])
        self.assertIn("blindaje queda desactivado", buffer.getvalue())


class InvalidCanonicalMetadataTests(unittest.TestCase):
    """La ley de nombres debe fallar antes de compilar y sin traceback."""

    def test_create_reports_invalid_publisher_without_traceback(self):
        from lib.cliHandler import handle_cli_action

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "projects"
            base.mkdir()
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                with self.assertRaises(SystemExit) as ctx:
                    handle_cli_action(
                        "create_project",
                        {
                            "path": str(base),
                            "name": "Demo",
                            "shortname": "demo",
                            "version": "1.0.0",
                            "author": "JesusQuijada34",
                            "publisher": "Jesús",
                            "platform": "Danenone",
                        },
                        None,
                        headless=True,
                    )
            self.assertEqual(ctx.exception.code, 1)
            self.assertIn("[ERROR] Metadatos de proyecto no válidos", buffer.getvalue())
            self.assertEqual(list(base.iterdir()), [], "no debe crear el proyecto")

    def test_buildthis_validates_before_compiling(self):
        from lib.cliHandler import handle_cli_action

        class _RecordingCompiler:
            instances = []

            def __init__(self, project_path, output_path, **kwargs):
                self.metadata = {
                    "publisher": "Jesús",
                    "app": "demo",
                    "version": "v1.0.0-26.11-06.07",
                    "platform": "Danenone",
                }
                self.compiled = False
                type(self).instances.append(self)

            def parse_details_xml(self):
                return True

            def find_scripts(self):
                return True

            def compile_binaries(self, platform):
                self.compiled = True
                return True

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "influent.demo.v1.0.0-26.11-06.07-Danenone"
            project.mkdir()
            (project / "details.xml").write_text(DETAILS, encoding="utf-8")

            _RecordingCompiler.instances = []
            buffer = io.StringIO()
            with patch("lib.blindcubeEngine.BuildThread.FlangCompiler", _RecordingCompiler):
                with redirect_stdout(buffer):
                    with self.assertRaises(SystemExit) as ctx:
                        handle_cli_action(
                            "buildthis",
                            {"path": str(project)},
                            None,
                            headless=True,
                            output=str(Path(tmp) / "out"),
                            sandbox=False,
                        )

            self.assertEqual(ctx.exception.code, 1)
            self.assertIn("[ERROR] Metadatos de proyecto no válidos", buffer.getvalue())
            self.assertTrue(_RecordingCompiler.instances)
            self.assertFalse(
                _RecordingCompiler.instances[0].compiled,
                "debe abortar antes de compilar binarios",
            )

    def test_repair_reports_invalid_publisher_without_traceback(self):
        from lib.cliHandler import handle_cli_action

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "influent.demo.v1.0.0-26.11-06.07-Danenone"
            project.mkdir()
            (project / "details.xml").write_text(
                DETAILS.replace("<publisher>Influent</publisher>", "<publisher>Jesús</publisher>"),
                encoding="utf-8",
            )
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                with self.assertRaises(SystemExit) as ctx:
                    handle_cli_action(
                        "repair_project",
                        {
                            "path": tmp,
                            "name": "demo",
                            "shortname": "demo",
                            "publisher": "Influent",
                        },
                        None,
                        headless=True,
                    )
            self.assertEqual(ctx.exception.code, 1)
            self.assertIn("[ERROR] Metadatos de proyecto no válidos", buffer.getvalue())


class JsonOutputPurityTests(unittest.TestCase):
    """R-4b7e91a2: stdout de las acciones ``*-json`` debe ser JSON válido."""

    def test_inspect_json_stdout_is_parseable(self):
        from lib.blindcubeEngine.iflapp_format import pack_iflapp

        with tempfile.TemporaryDirectory() as tmp:
            payload = Path(tmp) / "payload"
            payload.mkdir()
            (payload / "hello.txt").write_text("hola\n", encoding="utf-8")
            artifact = Path(tmp) / "demo.iflapp"
            pack_iflapp(
                payload,
                artifact,
                details=DETAILS.encode("utf-8"),
                identity={
                    "publisher": "Influent",
                    "app": "demo",
                    "name": "demo",
                    "version": "v1.0.0-26.11-04.08",
                    "platform": "Danenone",
                },
            )

            result = subprocess.run(
                [sys.executable, str(ROOT / "packagemaker.py"), "--inspect", str(artifact), "--inspect-json"],
                cwd=tmp,
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data["identity"]["app"], "demo")
            self.assertIn("Platform detected", result.stderr)



class CompileProjectSelectionTests(unittest.TestCase):
    """El subcomando ``compile`` debe elegir el proyecto exacto y no reventar."""

    def _make_project(self, base: Path, app: str) -> Path:
        project = base / f"influent.{app}.v1.0.0-26.11-08.00-Danenone"
        project.mkdir()
        (project / "details.xml").write_text(
            DETAILS.replace("<app>demo</app>", f"<app>{app}</app>").replace(
                "<name>demo</name>", f"<name>{app}</name>"
            ),
            encoding="utf-8",
        )
        return project

    def test_compile_selects_exact_app_not_prefix(self):
        from lib.cliHandler import handle_cli_action

        class _RecordingCompiler:
            chosen = []

            def __init__(self, project_path, output_path, **kwargs):
                type(self).chosen.append(Path(project_path))

            def parse_details_xml(self):
                return False

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "projects"
            base.mkdir()
            # ``demo2`` se crea primero para que el orden del directorio lo
            # devuelva antes; la coincidencia por subcadena elegía ese proyecto.
            self._make_project(base, "demo2")
            self._make_project(base, "demo")
            _RecordingCompiler.chosen = []

            with patch("lib.blindcubeEngine.BuildThread.FlangCompiler", _RecordingCompiler), patch(
                "lib.platform_detect.compile_output_directory",
                return_value=str(Path(tmp) / "out"),
            ):
                with redirect_stdout(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        handle_cli_action(
                            "compile_project",
                            {
                                "path": str(base),
                                "name": "Demo",
                                "shortname": "demo",
                                "publisher": "Influent",
                            },
                            None,
                            headless=True,
                        )

            self.assertEqual(len(_RecordingCompiler.chosen), 1)
            self.assertIn("influent.demo.v", _RecordingCompiler.chosen[0].name)
            self.assertNotIn("demo2", _RecordingCompiler.chosen[0].name)

    def test_compile_missing_base_dir_reports_error_without_traceback(self):
        from lib.cliHandler import handle_cli_action

        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "does-not-exist"
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                with self.assertRaises(SystemExit) as ctx:
                    handle_cli_action(
                        "compile_project",
                        {
                            "path": str(missing),
                            "name": "Demo",
                            "shortname": "demo",
                            "publisher": "Influent",
                        },
                        None,
                        headless=True,
                    )
            self.assertEqual(ctx.exception.code, 1)
            self.assertIn("No se encontró proyecto", buffer.getvalue())

    def test_moonfix_missing_base_dir_reports_error_without_traceback(self):
        from lib.cliHandler import handle_cli_action

        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "does-not-exist"
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                with self.assertRaises(SystemExit) as ctx:
                    handle_cli_action(
                        "repair_project",
                        {
                            "path": str(missing),
                            "name": "Demo",
                            "shortname": "demo",
                            "publisher": "Influent",
                        },
                        None,
                        headless=True,
                    )
            self.assertEqual(ctx.exception.code, 1)
            self.assertIn("No se encontró proyecto", buffer.getvalue())


class EncryptedSandboxVerificationTests(unittest.TestCase):
    """La verificación en sandbox debe descifrar los paquetes con ``--password``."""

    def test_encrypted_package_verifies_inside_sandbox(self):
        from lib.blindcubeEngine.BuildThread import FlangCompiler
        from lib.blindcubeEngine.hardware_sandbox import SandboxResult
        from lib.blindcubeEngine.iflapp_format import pack_iflapp

        class _RealRunSandbox:
            backend = "fake"

            def __init__(self, workspace):
                self.workspace = Path(workspace)

            def describe(self):
                return {"selected": "fake", "hardware_virtualization": False}

            def prepare_workspace(self, output_path, *, writable=True):
                self.workspace.mkdir(parents=True, exist_ok=True)
                return self.workspace

            def run(self, argv, workspace, *, env=None, **kwargs):
                run_env = os.environ.copy()
                run_env.update(env or {})
                proc = subprocess.run(
                    list(argv),
                    cwd=str(workspace),
                    env=run_env,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                return SandboxResult(
                    proc.returncode, proc.stdout, proc.stderr, "fake", list(argv)
                )

            def cleanup(self, workspace):
                pass

        with tempfile.TemporaryDirectory() as tmp:
            payload = Path(tmp) / "payload"
            payload.mkdir()
            (payload / "app.py").write_text("print('hola')\n", encoding="utf-8")
            artifact = Path(tmp) / "demo.iflapp"
            pack_iflapp(
                payload,
                artifact,
                details=DETAILS.encode("utf-8"),
                identity={"publisher": "Influent", "app": "demo"},
                password="secreto",
            )

            project = Path(tmp) / "project"
            project.mkdir()
            output = Path(tmp) / "out"
            logs = []
            compiler = FlangCompiler(
                project,
                output,
                log_callback=logs.append,
                sandbox=False,
                package_password="secreto",
            )
            compiler._sandbox = _RealRunSandbox(Path(tmp) / "sandbox")

            self.assertTrue(compiler.verify_in_sandbox(artifact))
            joined = "\n".join(logs)
            self.assertNotIn("incompleta", joined)
            self.assertTrue((Path(tmp) / "sandbox" / "unpacked" / "app.py").is_file())


class JsonPurityWithoutOptionalUiTests(unittest.TestCase):
    """R-3a7c5e18: sin ``leviathan_ui`` stdout sigue siendo JSON válido."""

    def test_shell_plan_json_stays_parseable_without_leviathan(self):
        with tempfile.TemporaryDirectory() as tmp:
            stub = Path(tmp) / "leviathan_ui.py"
            stub.write_text(
                "raise ImportError('leviathan_ui ausente en la prueba')\n",
                encoding="utf-8",
            )
            env = os.environ.copy()
            env["PYTHONPATH"] = os.pathsep.join(
                part for part in (tmp, env.get("PYTHONPATH")) if part
            )
            # La copia vendorizada de ``lib/leviathan_ui`` daría el framework por
            # disponible; el escenario a probar es su ausencia real.
            env["PACKAGEMAKER_NO_VENDORED_FRAMEWORK"] = "1"

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "packagemaker.py"),
                    "--shell-plan",
                    str(ROOT / "example.mexf"),
                    "--shell-plan-json",
                ],
                cwd=tmp,
                capture_output=True,
                text=True,
                env=env,
                timeout=120,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data["id"], "com.fluthin.packagemaker")
            self.assertIn("Leviathan UI unavailable", result.stderr)
            self.assertNotIn("Leviathan UI unavailable", result.stdout)


class JsonPurityWithAuxiliaryOutputTests(unittest.TestCase):
    """R-9f2b64d1: los avisos auxiliares no rompen el JSON de stdout."""

    @staticmethod
    def _artifact(tmp: Path) -> Path:
        from lib.blindcubeEngine.iflapp_format import pack_iflapp

        payload = tmp / "payload"
        payload.mkdir()
        (payload / "hello.txt").write_text("hola\n", encoding="utf-8")
        artifact = tmp / "demo.iflapp"
        pack_iflapp(
            payload,
            artifact,
            details=DETAILS.encode("utf-8"),
            identity={
                "publisher": "Influent",
                "app": "demo",
                "name": "demo",
                "version": "v1.0.0-26.11-04.08",
                "platform": "Danenone",
            },
        )
        return artifact

    def test_inspect_json_with_extract_stays_parseable(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            artifact = self._artifact(tmp_path)
            extract_dir = tmp_path / "extract"

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "packagemaker.py"),
                    "--inspect",
                    str(artifact),
                    "--inspect-json",
                    "--inspect-extract",
                    str(extract_dir),
                ],
                cwd=tmp,
                capture_output=True,
                text=True,
                timeout=120,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data["identity"]["app"], "demo")
            self.assertIn("Recursos de cabecera exportados", result.stderr)
            self.assertTrue((extract_dir / "details.xml").is_file())

    def test_shell_info_json_with_preview_stays_parseable(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            artifact = self._artifact(tmp_path)
            preview_dir = tmp_path / "preview"

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "packagemaker.py"),
                    "--shell-info",
                    str(artifact),
                    "--shell-info-json",
                    "--shell-preview",
                    str(preview_dir),
                ],
                cwd=tmp,
                capture_output=True,
                text=True,
                timeout=120,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data["identity"]["app"], "demo")
            self.assertIn("icono exportable", result.stderr)


class MoonfixEncodingWarningTests(unittest.TestCase):
    """R-6e04c8ab: un details.xml corrupto no aborta MoonFix en cp1252."""

    def test_corrupt_details_xml_warns_without_unicode_error(self):
        from lib.cliHandler import handle_cli_action

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "influent.demo.v1.0.0-26.11-09.00-Danenone"
            project.mkdir()
            (project / "details.xml").write_text("<details>\n", encoding="utf-8")

            out_buffer = io.BytesIO()
            out = io.TextIOWrapper(out_buffer, encoding="cp1252")
            err_buffer = io.BytesIO()
            err = io.TextIOWrapper(err_buffer, encoding="cp1252")
            try:
                with redirect_stdout(out), redirect_stderr(err):
                    handle_cli_action(
                        "repair_project",
                        {
                            "path": tmp,
                            "name": "Demo",
                            "shortname": "demo",
                            "publisher": "Influent",
                            "version": "1.0.0",
                            "author": "Unknown",
                        },
                        None,
                        headless=True,
                    )
                out.flush()
                err.flush()
                stdout_text = out_buffer.getvalue().decode("cp1252")
                stderr_text = err_buffer.getvalue().decode("cp1252")
            finally:
                out.close()
                err.close()

            self.assertIn("MoonFix completado", stdout_text)
            self.assertIn("no se pudo leer details.xml", stderr_text)
            self.assertIn("<publisher>", (project / "details.xml").read_text(encoding="utf-8"))


class MoonFixPreservesCanonicalTimestampTests(unittest.TestCase):
    """R-7d5b91c4: reparar no debe regenerar la marca temporal del proyecto."""

    TIMESTAMP = "26.11-10.05"

    def _create_project(self, root: Path, folder: str | None = None):
        from lib.makeselfEngine.template_engine import create_project_from_templates

        project = root / (folder or f"Influent.demo.v1.0-{self.TIMESTAMP}-Danenone")
        create_project_from_templates(
            project,
            publisher="Influent",
            app_id="demo",
            name="Demo",
            author="JesusQuijada34",
            platform="Danenone",
            version_base="1.0",
            timestamp=self.TIMESTAMP,
        )
        return project

    def _details_version(self, project: Path) -> str:
        import xml.etree.ElementTree as ET

        return (ET.parse(project / "details.xml").getroot().findtext("version") or "").strip()

    def test_repair_keeps_the_folder_timestamp(self):
        from lib.makeselfEngine.template_engine import repair_project_from_templates

        with tempfile.TemporaryDirectory() as tmp:
            project = self._create_project(Path(tmp))
            result = repair_project_from_templates(
                project,
                "Influent",
                "demo",
                "Demo",
                "JesusQuijada34",
                "Danenone",
                version_base="1.0",
            )
            self.assertEqual(self._details_version(project), f"v1.0-{self.TIMESTAMP}")
            self.assertEqual(result["variables"]["FOLDER_NAME"], project.name)

    def test_repair_falls_back_to_details_timestamp_for_legacy_folder(self):
        from lib.makeselfEngine.template_engine import repair_project_from_templates

        with tempfile.TemporaryDirectory() as tmp:
            project = self._create_project(Path(tmp), folder="legacy-demo")
            repair_project_from_templates(
                project,
                "Influent",
                "demo",
                "Demo",
                "JesusQuijada34",
                "Danenone",
                version_base="1.0",
            )
            self.assertEqual(self._details_version(project), f"v1.0-{self.TIMESTAMP}")

    def test_cli_repair_preserves_the_canonical_identity(self):
        from lib.cliHandler import handle_cli_action
        from lib.projectNameFormatter import ProjectNameFormatter

        with tempfile.TemporaryDirectory() as tmp:
            project = self._create_project(Path(tmp))
            with redirect_stdout(io.StringIO()):
                handle_cli_action(
                    "repair_project",
                    {
                        "path": tmp,
                        "name": "Demo",
                        "shortname": "demo",
                        "publisher": "Influent",
                        "version": "1.0",
                    },
                    None,
                    headless=True,
                )
            parsed = ProjectNameFormatter.parse_project_folder(project.name)
            self.assertEqual(self._details_version(project), f"v1.0-{parsed['timestamp']}")


if __name__ == "__main__":
    unittest.main()
