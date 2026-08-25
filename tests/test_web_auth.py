import html
import os
import re
import tempfile
import unittest
from unittest.mock import patch

from lib.device_link import DeviceLinkStore


class WebAuthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["GITHUB_CLIENT_ID"] = "test-client"
        os.environ["GITHUB_CLIENT_SECRET"] = "test-secret"
        os.environ["RENDER_AUTH_BASE_URL"] = "https://packagemaker.onrender.com"
        import app as app_module
        cls.app_module = app_module

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.app_module.DEVICE_LINK_STORE = DeviceLinkStore(os.path.join(self.temp_dir.name, "links.db"))
        self.client = self.app_module.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_download_and_linkdevice_require_login(self):
        download = self.client.get("/download", follow_redirects=False)
        self.assertEqual(download.status_code, 302)
        self.assertIn("/login?", download.headers["Location"])
        self.assertIn("next=%2Fdownload", download.headers["Location"])

        link = self.client.get("/linkdevice", follow_redirects=False)
        self.assertEqual(link.status_code, 302)
        self.assertIn("/login?", link.headers["Location"])
        self.assertIn("next=%2Flinkdevice", link.headers["Location"])

    def test_login_callback_caches_session_and_redirects(self):
        login = self.client.get("/login?next=/download")
        self.assertEqual(login.status_code, 200)
        state = re.search(rb'href="https://github.com/login/oauth/authorize\?([^\"]+)', login.data).group(1).decode()
        state = html.unescape(state)
        from urllib.parse import parse_qs
        state_value = parse_qs(state)["state"][0]
        request = self.app_module.DEVICE_LINK_STORE.get_by_state(state_value)

        with patch.object(
            self.app_module,
            "exchange_github_code",
            return_value=("server-token", {"login": "octocat", "id": 1, "name": "The Octocat"}),
        ):
            callback = self.client.get(
                "/auth/github/callback",
                query_string={"state": state_value, "code": "temporary-code"},
                follow_redirects=False,
            )
        self.assertEqual(callback.status_code, 302)
        self.assertEqual(callback.headers["Location"], "/download")

        protected = self.client.get("/download", follow_redirects=False)
        self.assertEqual(protected.status_code, 200)
        self.assertIn("Suite".encode("utf-8"), protected.data)
        self.assertIsNotNone(request)

    def test_linkdevice_uses_cached_profile(self):
        with self.client.session_transaction() as browser_session:
            session_id = self.app_module.DEVICE_LINK_STORE.save_github_session(
                "server-token", {"login": "octocat", "id": 1, "name": "The Octocat"}
            )
            browser_session["github_session_id"] = session_id
        response = self.client.get("/linkdevice", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        request_id = response.headers["Location"].split("request_id=", 1)[1]
        status = self.client.get(f"/api/linkdevice/status?request_id={request_id}").get_json()
        self.assertEqual(status["status"], "ready")
        self.assertRegex(status["code"], r"^[A-Z2-9]{4}-[A-Z2-9]{4}$")


if __name__ == "__main__":
    unittest.main()
