import os
import tempfile
import unittest

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
        with self.client.session_transaction() as browser_session:
            session_id = self.app_module.DEVICE_LINK_STORE.save_github_session(
                "server-only-github-token",
                {"login": "octocat", "id": 1, "name": "The Octocat"},
            )
            browser_session["github_session_id"] = session_id

        page = self.client.get("/linkdevice", follow_redirects=False)
        self.assertEqual(page.status_code, 302)
        request_id = page.headers["Location"].split("request_id=", 1)[1]

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


if __name__ == "__main__":
    unittest.main()
