import os
import re
import tempfile
import unittest
from unittest.mock import patch

from lib.device_link import DeviceLinkStore


class LinkDeviceRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.setdefault("FLASK_SECRET_KEY", "test-secret")
        os.environ["GITHUB_CLIENT_ID"] = "test-client"
        os.environ["GITHUB_CLIENT_SECRET"] = "test-secret"
        os.environ["RENDER_AUTH_BASE_URL"] = "https://packagemaker.onrender.com"
        import app as app_module

        cls.app_module = app_module

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.app_module.DEVICE_LINK_STORE = DeviceLinkStore(
            os.path.join(self.temp_dir.name, "links.db")
        )
        self.client = self.app_module.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_web_code_poll_and_success_state(self):
        page = self.client.get("/linkdevice")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"Continuar con GitHub", page.data)
        request_id = re.search(rb'const requestId = "([^"\\]+)"', page.data).group(1).decode()
        request = self.app_module.DEVICE_LINK_STORE.get(request_id)

        with patch.object(
            self.app_module,
            "exchange_github_code",
            return_value=("server-only-github-token", {"login": "octocat", "id": 1, "name": "The Octocat"}),
        ):
            callback = self.client.get(
                "/auth/github/device-callback",
                query_string={"state": self._raw_state(request), "code": "temporary-code"},
            )
        self.assertEqual(callback.status_code, 302)

        status = self.client.get(f"/api/linkdevice/status?request_id={request_id}").get_json()
        self.assertEqual(status["status"], "ready")
        code = status["code"]
        poll = self.client.post("/api/linkdevice/poll", json={"code": code})
        self.assertEqual(poll.status_code, 200)
        payload = poll.get_json()
        self.assertEqual(payload["profile"]["login"], "octocat")
        self.assertTrue(payload["session"]["ticket"])

        final_status = self.client.get(f"/api/linkdevice/status?request_id={request_id}").get_json()
        self.assertEqual(final_status["status"], "linked")

    def _raw_state(self, request):
        # Test-only lookup: create a matching temporary authorization request
        # and replace the current row's hash with its known raw state.
        raw_state = "test-state-for-callback"
        with self.app_module.DEVICE_LINK_STORE._connect() as connection:
            connection.execute(
                "UPDATE device_links SET state_hash = ? WHERE request_id = ?",
                (self.app_module.DEVICE_LINK_STORE.digest(raw_state), request["request_id"]),
            )
        return raw_state


if __name__ == "__main__":
    unittest.main()
