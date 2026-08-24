import os
import tempfile
import time
import unittest
from unittest.mock import patch

from lib.device_link import DeviceLinkStore


class DeviceLinkStoreTests(unittest.TestCase):
    def test_code_is_single_use_and_ticket_validates(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = DeviceLinkStore(os.path.join(temp_dir, "links.db"))
            request = store.create_auth_request()
            display_code = store.complete_authorization(
                request.request_id,
                "github-token-kept-on-server",
                {"login": "octocat", "id": 1, "name": "The Octocat"},
            )
            status, profile, ticket, remaining = store.poll_code(display_code)
            self.assertEqual(status, "complete")
            self.assertEqual(profile["login"], "octocat")
            self.assertGreater(remaining, 0)
            self.assertIsNotNone(ticket)
            self.assertEqual(store.poll_code(display_code)[0], "linked")
            validated_profile, remaining = store.validate_ticket(ticket)
            self.assertEqual(validated_profile["login"], "octocat")
            self.assertGreater(remaining, 0)

    def test_expired_request_is_not_usable(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = DeviceLinkStore(os.path.join(temp_dir, "links.db"))
            request = store.create_auth_request()
            with patch("lib.device_link.time.time", return_value=request.expires_at + 1):
                self.assertEqual(store.get(request.request_id), None)
                self.assertEqual(store.poll_code("AAAA-BBBB")[0], "invalid")


if __name__ == "__main__":
    unittest.main()
