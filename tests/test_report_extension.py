# -*- coding: utf-8 -*-
"""Extensión de reportes: issues de GitHub firmados con la cuenta del usuario.

Se prueba con dobles de la red (``_request`` sustituido), pero todo lo demás
es código real: saneado, huella, cola, cuerpo del issue y captura de fallos.
"""

import json
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib import (  # noqa: E402
    crash_capture,
    github_issue_reporter,
    report_queue,
    report_telemetry,
)


class TelemetrySanitizeTest(unittest.TestCase):
    def test_absolute_paths_are_removed(self):
        text = "fallo en /home/jesus/Documents/app.py y en C:\\Users\\Jesus\\app.py"
        cleaned = report_telemetry.sanitize(text)
        self.assertNotIn("/home/jesus", cleaned)
        self.assertNotIn("C:\\Users\\Jesus", cleaned)
        self.assertIn("<path>", cleaned)

    def test_home_is_replaced_even_with_spaces(self):
        cleaned = report_telemetry.sanitize(
            "ruta /home/Jesus Quijada/proyecto/x.py", home="/home/Jesus Quijada"
        )
        self.assertNotIn("Jesus Quijada", cleaned)

    def test_credentials_are_redacted(self):
        cleaned = report_telemetry.sanitize("token=ghp_secreto123 password: hunter2")
        self.assertNotIn("ghp_secreto123", cleaned)
        self.assertNotIn("hunter2", cleaned)
        self.assertIn("<redacted>", cleaned)

    def test_environment_has_no_personal_data(self):
        environment = report_telemetry.collect_environment()
        blob = json.dumps(environment).lower()
        for forbidden in ("home", "user", "hostname", "token", "password"):
            self.assertNotIn(forbidden, blob)
        # Sí debe traer lo que sirve para diagnosticar.
        for required in ("app_version", "python_version", "os", "architecture"):
            self.assertIn(required, environment)

    def test_fingerprint_is_stable_and_discriminating(self):
        first = report_telemetry.fingerprint("ValueError", "boom")
        self.assertEqual(first, report_telemetry.fingerprint("ValueError", "boom"))
        self.assertNotEqual(first, report_telemetry.fingerprint("TypeError", "boom"))
        self.assertNotEqual(first, report_telemetry.fingerprint("ValueError", "otro"))


class IssueBodyTest(unittest.TestCase):
    def test_body_includes_environment_and_sanitizes_description(self):
        report = github_issue_reporter.Report(
            title="Fallo",
            description="pasa en /home/jesus/x.py con token=abc",
            attachments=[("log.txt", "detalle en /home/jesus/y.py")],
        )
        body = github_issue_reporter.build_issue_body(report)
        self.assertIn("## Entorno", body)
        self.assertIn("| PackageMaker |", body)
        self.assertNotIn("/home/jesus", body)
        self.assertNotIn("token=abc", body)
        self.assertIn("Archivos adjuntos", body)

    def test_fingerprint_marker_is_present(self):
        report = github_issue_reporter.Report(
            title="Fallo", description="x", fingerprint="abc123"
        )
        self.assertIn("<!-- pm-fingerprint: abc123 -->",
                      github_issue_reporter.build_issue_body(report))

    def test_attachment_name_is_sanitized(self):
        report = github_issue_reporter.Report(
            title="t", description="d", attachments=[("../../etc/passwd", "x")]
        )
        body = github_issue_reporter.build_issue_body(report)
        self.assertNotIn("../../etc/passwd", body)


class CreateIssueTest(unittest.TestCase):
    def setUp(self):
        self.calls = []

    def _fake_request(self, method, url, token, payload=None, **kwargs):
        self.calls.append((method, url, payload))
        if "/search/issues" in url:
            return {"items": []}
        return {"number": 42, "html_url": "https://github.com/x/y/issues/42"}

    def test_without_token_nothing_is_sent(self):
        with mock.patch.object(github_issue_reporter, "_token", return_value=""):
            result = github_issue_reporter.create_issue(
                github_issue_reporter.Report(title="t", description="d")
            )
        self.assertFalse(result.ok)
        self.assertEqual(self.calls, [])

    def test_issue_is_created_with_labels(self):
        with mock.patch.object(github_issue_reporter, "_token", return_value="tok"), \
                mock.patch.object(github_issue_reporter, "_request", self._fake_request):
            result = github_issue_reporter.create_issue(
                github_issue_reporter.Report(title="t", description="d", kind="bug")
            )
        self.assertTrue(result.ok)
        self.assertEqual(result.issue_number, 42)
        method, url, payload = self.calls[-1]
        self.assertEqual(method, "POST")
        self.assertTrue(url.endswith("/repos/JesusQuijada34/packagemaker/issues"))
        self.assertIn("bug", payload["labels"])

    def test_duplicate_fingerprint_comments_instead_of_opening(self):
        def _request(method, url, token, payload=None, **kwargs):
            self.calls.append((method, url, payload))
            if "/search/issues" in url:
                return {"items": [{"number": 7, "body": "<!-- pm-fingerprint: abc -->"}]}
            return {"html_url": "https://github.com/x/y/issues/7#comment"}

        with mock.patch.object(github_issue_reporter, "_token", return_value="tok"), \
                mock.patch.object(github_issue_reporter, "_request", _request):
            result = github_issue_reporter.create_issue(
                github_issue_reporter.Report(
                    title="t", description="d", fingerprint="abc"
                )
            )
        self.assertTrue(result.ok)
        self.assertTrue(result.deduplicated)
        self.assertTrue(self.calls[-1][1].endswith("/issues/7/comments"))

    def test_network_error_is_reported_not_raised(self):
        def _boom(*args, **kwargs):
            raise RuntimeError("Sin conexión con GitHub")

        with mock.patch.object(github_issue_reporter, "_token", return_value="tok"), \
                mock.patch.object(github_issue_reporter, "_request", _boom):
            result = github_issue_reporter.create_issue(
                github_issue_reporter.Report(title="t", description="d")
            )
        self.assertFalse(result.ok)
        self.assertIn("conexión", result.error)


class QueueTest(unittest.TestCase):
    def setUp(self):
        self._original = report_queue._queue_path
        self.tmp = Path(self.id().replace(".", "_") + "_queue.json")
        report_queue._queue_path = lambda: self.tmp
        self.tmp.unlink(missing_ok=True)

    def tearDown(self):
        report_queue._queue_path = self._original
        self.tmp.unlink(missing_ok=True)
        self.tmp.with_name("report_sent.json").unlink(missing_ok=True)

    def test_enqueue_and_count(self):
        self.assertTrue(report_queue.enqueue({"title": "t", "description": "d"}))
        self.assertEqual(report_queue.count(), 1)

    def test_entry_without_title_is_rejected(self):
        self.assertFalse(report_queue.enqueue({"description": "sin titulo"}))

    def test_drain_keeps_failures(self):
        report_queue.enqueue({"title": "a"})
        report_queue.enqueue({"title": "b"})
        outcome = report_queue.drain(lambda entry: entry["title"] == "a")
        self.assertEqual(outcome, {"sent": 1, "failed": 1})
        remaining = report_queue.pending()
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0]["title"], "b")

    def test_sent_fingerprints_are_remembered(self):
        self.assertFalse(report_queue.already_sent("abc"))
        report_queue.record_sent("abc")
        self.assertTrue(report_queue.already_sent("abc"))


class CrashCaptureTest(unittest.TestCase):
    def setUp(self):
        self._original = report_queue._queue_path
        self.tmp = Path(self.id().replace(".", "_") + "_crash.json")
        report_queue._queue_path = lambda: self.tmp
        self.tmp.unlink(missing_ok=True)
        self.tmp.with_name("report_sent.json").unlink(missing_ok=True)
        crash_capture.reset_for_tests()

    def tearDown(self):
        report_queue._queue_path = self._original
        self.tmp.unlink(missing_ok=True)
        self.tmp.with_name("report_sent.json").unlink(missing_ok=True)

    def test_failure_without_session_is_queued(self):
        calls = []

        def _spy(*args, **kwargs):
            calls.append(args)
            return github_issue_reporter.Result(ok=True, issue_number=1)

        with mock.patch.object(github_issue_reporter, "_token", return_value=""), \
                mock.patch.object(github_issue_reporter, "report_exception", _spy):
            try:
                raise ValueError("fallo de prueba en /home/jesus/app.py")
            except ValueError:
                crash_capture.capture(*sys.exc_info(), where="arranque")

        self.assertEqual(calls, [], "sin sesión no se debe intentar publicar nada")
        pending = report_queue.pending()
        self.assertEqual(len(pending), 1)
        self.assertTrue(pending[0]["auto"])
        self.assertIn("ValueError", pending[0]["title"])
        self.assertNotIn("/home/jesus", pending[0]["title"])
        self.assertNotIn("/home/jesus", pending[0]["traceback"])

    def test_failure_with_session_is_sent_once(self):
        sent = []

        def _fake_report(exc_type, exc_value, exc_tb, context="", token=""):
            sent.append(context)
            return github_issue_reporter.Result(ok=True, issue_number=9)

        with mock.patch.object(github_issue_reporter, "_token", return_value="tok"), \
                mock.patch.object(github_issue_reporter, "report_exception", _fake_report):
            try:
                raise RuntimeError("boom")
            except RuntimeError:
                crash_capture.capture(*sys.exc_info(), where="interfaz")
                crash_capture.capture(*sys.exc_info(), where="interfaz")

        self.assertEqual(sent, ["interfaz"], "el mismo fallo no se envía dos veces")
        self.assertEqual(report_queue.count(), 0)

    def test_capture_never_raises(self):
        def _boom(*args, **kwargs):
            raise RuntimeError("el reportero falló")

        with mock.patch.object(github_issue_reporter, "has_session", _boom):
            try:
                raise ValueError("original")
            except ValueError:
                crash_capture.capture(*sys.exc_info())  # no debe propagar


class AutoReportSettingTest(unittest.TestCase):
    def setUp(self):
        self._original = report_queue._queue_path
        self.tmp = Path(self.id().replace(".", "_") + "_auto.json")
        report_queue._queue_path = lambda: self.tmp
        self.tmp.unlink(missing_ok=True)
        self.tmp.with_name("report_sent.json").unlink(missing_ok=True)
        crash_capture.reset_for_tests()

    def tearDown(self):
        report_queue._queue_path = self._original
        self.tmp.unlink(missing_ok=True)
        self.tmp.with_name("report_sent.json").unlink(missing_ok=True)

    def test_disabled_setting_prevents_sending(self):
        sent = []

        def _fake_report(*args, **kwargs):
            sent.append(1)
            return github_issue_reporter.Result(ok=True, issue_number=1)

        with mock.patch.object(crash_capture, "auto_report_enabled", lambda: False), \
                mock.patch.object(github_issue_reporter, "_token", return_value="tok"), \
                mock.patch.object(github_issue_reporter, "report_exception", _fake_report):
            try:
                raise ValueError("boom")
            except ValueError:
                crash_capture.capture(*sys.exc_info())

        self.assertEqual(sent, [], "con el envío automático apagado no se publica nada")
        self.assertEqual(report_queue.count(), 1, "pero el fallo no se pierde")

    def test_setting_defaults_to_enabled(self):
        with mock.patch("lib.pm_data.get_pm_data") as store:
            store.return_value.get_user.return_value = True
            self.assertTrue(crash_capture.auto_report_enabled())

    def test_broken_store_falls_back_to_enabled(self):
        with mock.patch("lib.pm_data.get_pm_data", side_effect=RuntimeError("x")):
            self.assertTrue(crash_capture.auto_report_enabled())


class HookTest(unittest.TestCase):
    def test_install_wraps_excepthook(self):
        original = sys.excepthook
        try:
            crash_capture.reset_for_tests()
            crash_capture.install()
            self.assertIsNot(sys.excepthook, original)
            # El hook original sigue ejecutándose: se restaura aquí.
            sys.excepthook = original
        finally:
            sys.excepthook = original


if __name__ == "__main__":
    unittest.main()


def test_environment_table_follows_the_interface_language(_qt_app):
    """Issue #12: la tabla del entorno salía siempre en español."""
    import lib.i18n as i18n_mod
    from lib import report_telemetry

    if i18n_mod.i18n._app is None:
        i18n_mod.i18n.initialize(_qt_app, "es")
    original = i18n_mod.i18n.get_current_lang()
    try:
        i18n_mod.i18n.load_translation("en")
        env = report_telemetry.collect_environment()
        table = report_telemetry.environment_markdown(env)

        assert env["language"] == "en"
        assert "Operating system" in table
        assert "Sistema operativo" not in table
        assert "CPU cores" in table
    finally:
        i18n_mod.i18n.load_translation(original)


def test_environment_table_reports_the_active_language(_qt_app):
    """El propio entorno debe decir en qué idioma ve la app el usuario."""
    import lib.i18n as i18n_mod
    from lib import report_telemetry

    if i18n_mod.i18n._app is None:
        i18n_mod.i18n.initialize(_qt_app, "es")
    original = i18n_mod.i18n.get_current_lang()
    try:
        i18n_mod.i18n.load_translation("ja")
        env = report_telemetry.collect_environment()
        assert env["language"] == "ja"
        assert "言語" in report_telemetry.environment_markdown(env)
    finally:
        i18n_mod.i18n.load_translation(original)
