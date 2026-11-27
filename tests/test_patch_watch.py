# -*- coding: utf-8 -*-
"""Vigilancia de parches (Q-013/F-006, primera etapa).

Todo se prueba con un ``opener`` falso: ni red, ni descargas, ni cambios en la
instalación. El estado se escribe siempre en una carpeta temporal.
"""

import json
import sys
import unittest
import urllib.error
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib import patch_watch  # noqa: E402


class _Response:
    def __init__(self, payload):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _opener(payload=None, error=None):
    calls = []

    def opener(url, timeout=8.0):
        calls.append({"url": url, "timeout": timeout})
        if error is not None:
            raise error
        return _Response(payload)

    opener.calls = calls
    return opener


def _payload(sha="a" * 40, message="fix: parche de seguridad\n\ncuerpo"):
    return {
        "sha": sha,
        "commit": {"message": message, "author": {"date": "2026-11-27T20:00:00Z"}},
    }


class _NoEnvDisable(unittest.TestCase):
    def setUp(self):
        import os

        self._previous = os.environ.pop(patch_watch.DISABLE_ENV, None)

    def tearDown(self):
        import os

        if self._previous is None:
            os.environ.pop(patch_watch.DISABLE_ENV, None)
        else:
            os.environ[patch_watch.DISABLE_ENV] = self._previous


class PayloadTests(unittest.TestCase):
    def test_parses_sha_message_and_date(self):
        commit = patch_watch.parse_commit_payload(_payload())
        self.assertEqual(commit.sha, "a" * 40)
        self.assertEqual(commit.short, "aaaaaaa")
        self.assertEqual(commit.message, "fix: parche de seguridad")
        self.assertEqual(commit.date, "2026-11-27T20:00:00Z")

    def test_rejects_unexpected_payloads(self):
        for payload in (None, [], {}, {"sha": "abc"}, {"sha": 12}):
            with self.assertRaises(patch_watch.PatchWatchError):
                patch_watch.parse_commit_payload(payload)


class FetchTests(unittest.TestCase):
    def test_reads_latest_commit_without_credentials(self):
        opener = _opener(_payload("b" * 40))
        commit = patch_watch.fetch_latest_commit(opener=opener, timeout=3.0)
        self.assertEqual(commit.sha, "b" * 40)
        self.assertEqual(opener.calls[0]["url"], patch_watch.API_URL)
        self.assertEqual(opener.calls[0]["timeout"], 3.0)
        self.assertNotIn("token", patch_watch.API_URL.lower())

    def test_network_errors_become_patch_watch_error(self):
        opener = _opener(error=urllib.error.URLError("sin red"))
        with self.assertRaises(patch_watch.PatchWatchError):
            patch_watch.fetch_latest_commit(opener=opener)

    def test_http_errors_become_patch_watch_error(self):
        error = urllib.error.HTTPError(patch_watch.API_URL, 403, "forbidden", {}, None)
        opener = _opener(error=error)
        with self.assertRaises(patch_watch.PatchWatchError):
            patch_watch.fetch_latest_commit(opener=opener)

    def test_unreadable_body_becomes_patch_watch_error(self):
        class Broken(_Response):
            def read(self):
                return b"<html>no json</html>"

        opener = lambda url, timeout=8.0: Broken({})  # noqa: E731
        with self.assertRaises(patch_watch.PatchWatchError):
            patch_watch.fetch_latest_commit(opener=opener)


class LocalCommitTests(unittest.TestCase):
    def test_state_mark_wins(self):
        with TemporaryDirectory() as tmp:
            state = Path(tmp) / "patch_state.json"
            patch_watch.mark_applied("c" * 40, state)
            self.assertEqual(patch_watch.local_commit(tmp, state), "c" * 40)

    def test_reads_git_head_from_ref(self):
        with TemporaryDirectory() as tmp:
            git = Path(tmp) / ".git"
            (git / "refs" / "heads").mkdir(parents=True)
            (git / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
            (git / "refs" / "heads" / "main").write_text("d" * 40 + "\n", encoding="utf-8")
            self.assertEqual(patch_watch.local_commit(tmp), "d" * 40)

    def test_reads_packed_refs_and_detached_head(self):
        with TemporaryDirectory() as tmp:
            git = Path(tmp) / ".git"
            git.mkdir()
            (git / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
            (git / "packed-refs").write_text(
                "# pack-refs with: peeled\n" + "e" * 40 + " refs/heads/main\n",
                encoding="utf-8",
            )
            self.assertEqual(patch_watch.local_commit(tmp), "e" * 40)
            (git / "HEAD").write_text("f" * 40 + "\n", encoding="utf-8")
            self.assertEqual(patch_watch.local_commit(tmp), "f" * 40)

    def test_unknown_without_git_or_mark(self):
        with TemporaryDirectory() as tmp:
            self.assertEqual(patch_watch.local_commit(tmp), "")


class CheckTests(_NoEnvDisable):
    def _check(self, tmp, **kwargs):
        state = Path(tmp) / "patch_state.json"
        return patch_watch.check_for_patch(
            tmp, path=state, opener=kwargs.pop("opener", None),
            now=kwargs.pop("now", 1000.0), **kwargs
        ), state

    def test_available_when_remote_moved(self):
        with TemporaryDirectory() as tmp:
            patch_watch.mark_applied("1" * 40, Path(tmp) / "patch_state.json")
            status, state = self._check(tmp, opener=_opener(_payload("2" * 40)))
            self.assertTrue(status.has_patch)
            self.assertEqual(status.kind, patch_watch.STATUS_AVAILABLE)
            self.assertEqual(status.local, "1" * 40)
            self.assertEqual(status.short_remote, "2222222")
            self.assertEqual(status.message, "fix: parche de seguridad")
            saved = patch_watch.read_state(state)
            self.assertEqual(saved["last_remote"], "2" * 40)
            self.assertEqual(saved["last_check"], 1000.0)

    def test_up_to_date_when_same_commit(self):
        with TemporaryDirectory() as tmp:
            patch_watch.mark_applied("3" * 40, Path(tmp) / "patch_state.json")
            status, _ = self._check(tmp, opener=_opener(_payload("3" * 40)))
            self.assertEqual(status.kind, patch_watch.STATUS_UP_TO_DATE)
            self.assertFalse(status.has_patch)

    def test_unknown_when_local_commit_is_not_known(self):
        with TemporaryDirectory() as tmp:
            status, _ = self._check(tmp, opener=_opener(_payload("4" * 40)))
            self.assertEqual(status.kind, patch_watch.STATUS_UNKNOWN)
            self.assertEqual(status.remote, "4" * 40)
            self.assertFalse(status.has_patch)

    def test_offline_keeps_previous_state_untouched(self):
        with TemporaryDirectory() as tmp:
            status, state = self._check(
                tmp, opener=_opener(error=urllib.error.URLError("sin red"))
            )
            self.assertEqual(status.kind, patch_watch.STATUS_OFFLINE)
            self.assertIn("sin red", status.detail)
            self.assertFalse(state.exists())

    def test_disabled_does_not_touch_the_network(self):
        with TemporaryDirectory() as tmp:
            opener = _opener(_payload())
            status, _ = self._check(tmp, opener=opener, enabled=False)
            self.assertEqual(status.kind, patch_watch.STATUS_DISABLED)
            self.assertEqual(opener.calls, [])

    def test_metered_network_does_not_touch_the_network(self):
        with TemporaryDirectory() as tmp:
            opener = _opener(_payload())
            status, _ = self._check(tmp, opener=opener, network_mode="metered")
            self.assertEqual(status.kind, patch_watch.STATUS_METERED)
            self.assertEqual(opener.calls, [])

    def test_env_switch_disables_the_check(self):
        import os

        with TemporaryDirectory() as tmp:
            os.environ[patch_watch.DISABLE_ENV] = "0"
            try:
                opener = _opener(_payload())
                status, _ = self._check(tmp, opener=opener)
            finally:
                os.environ.pop(patch_watch.DISABLE_ENV, None)
            self.assertEqual(status.kind, patch_watch.STATUS_DISABLED)
            self.assertEqual(opener.calls, [])


class StateTests(unittest.TestCase):
    def test_should_check_respects_the_interval(self):
        with TemporaryDirectory() as tmp:
            state = Path(tmp) / "patch_state.json"
            patch_watch.write_state({"last_check": 1000.0}, state)
            self.assertFalse(patch_watch.should_check(6, state, now=1000.0 + 60))
            self.assertFalse(patch_watch.should_check(6, state, now=1000.0 + 6 * 3600 - 1))
            self.assertTrue(patch_watch.should_check(6, state, now=1000.0 + 6 * 3600))
            self.assertTrue(patch_watch.should_check(6, Path(tmp) / "missing.json", now=0))

    def test_write_state_tolerates_read_only_locations(self):
        with TemporaryDirectory() as tmp:
            blocker = Path(tmp) / "file"
            blocker.write_text("x", encoding="utf-8")
            self.assertFalse(patch_watch.write_state({"a": 1}, blocker / "state.json"))
            self.assertEqual(patch_watch.read_state(blocker / "state.json"), {})

    def test_mark_applied_rejects_short_values(self):
        with TemporaryDirectory() as tmp:
            state = Path(tmp) / "patch_state.json"
            self.assertFalse(patch_watch.mark_applied("abc", state))
            self.assertTrue(patch_watch.mark_applied("9" * 40, state))
            self.assertEqual(patch_watch.read_state(state)["applied_commit"], "9" * 40)

    def test_frozen_detection_reads_the_interpreter(self):
        previous = getattr(sys, "frozen", None)
        try:
            sys.frozen = True
            self.assertTrue(patch_watch.is_frozen())
        finally:
            if previous is None:
                del sys.frozen
            else:
                sys.frozen = previous
        self.assertFalse(patch_watch.is_frozen())


if __name__ == "__main__":
    unittest.main()
