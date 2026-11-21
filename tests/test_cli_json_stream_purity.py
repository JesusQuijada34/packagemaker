# -*- coding: utf-8 -*-
"""Regresión: los errores de ``--inspect``/``--shell-info`` no contaminan stdout.

En modo JSON stdout es el documento que consume el shell; si el mensaje de
error se imprime ahí, el ``json.load`` del cliente revienta. Es la misma clase
de bug que R-4b7e91a2 y R-9f2b64d1 (avisos auxiliares en la salida JSON).
"""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from lib.cliHandler import IflappIdeHelper, MexfShellHelper, NativeShellHelper, PackageInspectHelper


class JsonStreamPurityTests(unittest.TestCase):
    def _run(self, helper, data):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            result = helper(data)
        return result, out.getvalue(), err.getvalue()

    def test_inspect_json_keeps_stdout_empty_on_missing_file(self):
        result, out, err = self._run(
            PackageInspectHelper.inspect,
            {"path": "/nonexistent/paquete.iflapp", "json": True},
        )
        self.assertFalse(result)
        self.assertEqual(out, "", "stdout debe quedar vacío en modo JSON")
        self.assertIn("No se pudo leer la cabecera", err)

    def test_inspect_json_without_path_reports_on_stderr(self):
        result, out, err = self._run(PackageInspectHelper.inspect, {"json": True})
        self.assertFalse(result)
        self.assertEqual(out, "")
        self.assertIn("--inspect", err)

    def test_shell_info_json_keeps_stdout_empty_on_missing_file(self):
        result, out, err = self._run(
            NativeShellHelper.info, {"path": "/nonexistent/paquete.iflapp", "json": True}
        )
        self.assertFalse(result)
        self.assertEqual(out, "")
        self.assertIn("No existe el archivo", err)

    def test_shell_plan_json_keeps_stdout_empty_on_missing_file(self):
        result, out, err = self._run(
            MexfShellHelper.plan, {"path": "/nonexistent/app.mexf", "json": True}
        )
        self.assertFalse(result)
        self.assertEqual(out, "")
        self.assertIn("No se pudo leer el plan de shell", err)

    def test_ide_scan_json_keeps_stdout_empty_on_missing_dir(self):
        result, out, err = self._run(
            IflappIdeHelper.scan, {"path": "/nonexistent/proyecto", "as_json": True}
        )
        self.assertFalse(result)
        self.assertEqual(out, "")
        self.assertTrue(err.strip(), "el motivo debe llegar por stderr")

    def test_inspect_json_output_is_parseable(self):
        from lib.blindcubeEngine.iflapp_format import pack_iflapp

        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            src.mkdir()
            (src / "app.py").write_text("print(1)\n", encoding="utf-8")
            package = Path(tmp) / "demo.iflapp"
            pack_iflapp(
                src,
                str(package),
                identity={
                    "publisher": "Jesus",
                    "app": "Demo",
                    "version": "1.0.0",
                    "platform": "Danenone",
                },
            )
            result, out, _ = self._run(
                PackageInspectHelper.inspect, {"path": str(package), "json": True}
            )

        self.assertTrue(result)
        payload = json.loads(out)
        self.assertEqual(payload["identity"]["publisher"], "Jesus")
        self.assertEqual(payload["identity"]["app"], "Demo")


if __name__ == "__main__":
    unittest.main()
