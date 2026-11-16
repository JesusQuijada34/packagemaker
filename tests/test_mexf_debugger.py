# -*- coding: utf-8 -*-
"""Debugger integrado del editor ``.mexf`` (motor + CLI)."""
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from lib.mexf_debugger import (  # noqa: E402
    DebugFrame,
    MexfDebugger,
    debug_document,
    default_runner,
    load_commands,
)

DOCUMENT = {
    "format": "mexf",
    "version": 1,
    "metadata": {"id": "influent.demo", "name": "Demo"},
    "environments": {"DEMO_ENV": "1"},
    "commands": [
        {"id": "demo.uno", "executable": "uno", "args": ["a"]},
        {"id": "demo.dos", "executable": "dos", "args": ["b", "c"]},
        {"id": "demo.tres", "executable": "tres", "args": []},
    ],
}


def _ok_runner(executable, args, **kwargs):
    return 0, f"{executable}:ok"


def _fail_runner(executable, args, **kwargs):
    return 3, "boom"


class LoadCommandsTests(unittest.TestCase):
    def test_extracts_normalized_commands(self):
        commands = load_commands(DOCUMENT)
        self.assertEqual([c["id"] for c in commands], ["demo.uno", "demo.dos", "demo.tres"])
        self.assertEqual(commands[1]["args"], ["b", "c"])

    def test_skips_entries_without_id(self):
        self.assertEqual(load_commands({"commands": [{"executable": "x"}]}), [])


class StepExecutionTests(unittest.TestCase):
    def test_step_advances_one_command_at_a_time(self):
        debugger = MexfDebugger(DOCUMENT, runner=_ok_runner).start()
        first = debugger.step()
        self.assertEqual(first.command_id, "demo.uno")
        self.assertEqual(first.status, "ok")
        self.assertEqual(debugger.pc, 1)
        self.assertEqual(debugger.state, "paused")

    def test_run_executes_every_command(self):
        frames = debug_document(DOCUMENT, runner=_ok_runner)
        self.assertEqual(len(frames), 3)
        self.assertTrue(all(frame.status == "ok" for frame in frames))

    def test_failure_stops_unless_on_error_continue(self):
        document = {
            "metadata": {"id": "x"},
            "commands": [
                {"id": "a", "executable": "a"},
                {"id": "b", "executable": "b"},
            ],
        }
        debugger = MexfDebugger(document, runner=_fail_runner)
        debugger.run()
        self.assertEqual(len(debugger.frames), 1)
        self.assertEqual(debugger.state, "finished")
        self.assertIsNotNone(debugger.error)

        document["commands"][0]["on_error"] = "continue"
        debugger = MexfDebugger(document, runner=_fail_runner)
        debugger.run()
        self.assertEqual(len(debugger.frames), 2)

    def test_breakpoint_pauses_resume(self):
        debugger = MexfDebugger(DOCUMENT, runner=_ok_runner).start()
        debugger.set_breakpoint("demo.dos")
        debugger.resume()  # ejecuta demo.uno y para antes de demo.dos
        self.assertEqual(debugger.pc, 1)
        self.assertEqual(debugger.state, "paused")
        debugger.resume()  # ejecuta el resto
        self.assertEqual(debugger.state, "finished")
        self.assertEqual([f.command_id for f in debugger.frames], ["demo.uno", "demo.dos", "demo.tres"])

    def test_toggle_and_clear_breakpoints(self):
        debugger = MexfDebugger(DOCUMENT, runner=_ok_runner)
        self.assertTrue(debugger.toggle_breakpoint("demo.uno"))
        self.assertFalse(debugger.toggle_breakpoint("demo.uno"))
        debugger.set_breakpoint("demo.dos")
        debugger.clear_breakpoints()
        self.assertEqual(debugger.breakpoints, [])

    def test_dry_run_skips_without_calling_runner(self):
        def _boom(*args, **kwargs):
            raise AssertionError("el runner no debe invocarse en simulación")

        frames = debug_document(DOCUMENT, runner=_boom, dry_run=True)
        self.assertTrue(all(frame.status == "skipped" for frame in frames))


class VariablesTests(unittest.TestCase):
    def test_variables_expose_metadata_and_last_returncode(self):
        debugger = MexfDebugger(DOCUMENT, runner=_ok_runner)
        debugger.run()
        variables = debugger.variables()
        self.assertEqual(variables["metadata"]["id"], "influent.demo")
        self.assertEqual(variables["total"], 3)
        self.assertEqual(variables["last_returncode"], 0)
        self.assertEqual(variables["environments"]["DEMO_ENV"], "1")

    def test_missing_executable_is_a_failure(self):
        frame = MexfDebugger({"commands": [{"id": "x"}]}, runner=_ok_runner).step()
        self.assertEqual(frame.status, "failed")
        self.assertEqual(frame.returncode, 126)


class RunnerTests(unittest.TestCase):
    def test_default_runner_reports_missing_binary(self):
        code, output = default_runner("no-existe-jamas-12345", [])
        self.assertEqual(code, 127)
        self.assertIn("no-existe-jamas-12345", output)

    def test_default_runner_executes_without_shell(self):
        code, output = default_runner(sys.executable, ["-c", "print('hola')"])
        self.assertEqual(code, 0)
        self.assertIn("hola", output)


class DebugFrameTests(unittest.TestCase):
    def test_as_dict_round_trip(self):
        frame = DebugFrame(command_id="a", executable="e", args=["1"], status="ok", returncode=0)
        payload = frame.as_dict()
        self.assertEqual(payload["id"], "a")
        self.assertEqual(payload["args"], ["1"])
        self.assertFalse(frame.failed)


class CliDebugTests(unittest.TestCase):
    def _write(self, tmp_path):
        path = tmp_path / "main.mexf"
        path.write_text(
            "format: mexf\nversion: 1\n"
            "metadata:\n  id: influent.demo\n  name: Demo\n  version: v1.0\n"
            "commands:\n"
            "  - id: demo.uno\n    executable: uno\n    args: [a]\n"
            "  - id: demo.dos\n    executable: dos\n    args: []\n",
            encoding="utf-8",
        )
        return path

    def test_cli_debug_simulated_succeeds(self):
        import io
        import tempfile
        from contextlib import redirect_stdout

        from lib.cliHandler import MexfDebugHelper

        with tempfile.TemporaryDirectory(prefix="mexf-debug-") as tmp:
            path = self._write(Path(tmp))
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                ok = MexfDebugHelper.debug({"path": str(path), "execute": False})
        self.assertTrue(ok)
        self.assertIn("simulado", buffer.getvalue())

    def test_cli_debug_missing_file_fails(self):
        import tempfile

        from lib.cliHandler import MexfDebugHelper

        with tempfile.TemporaryDirectory(prefix="mexf-debug-") as tmp:
            ok = MexfDebugHelper.debug({"path": str(Path(tmp) / "nope.mexf")})
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
