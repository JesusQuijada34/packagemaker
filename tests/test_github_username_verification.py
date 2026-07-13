import unittest
from unittest.mock import patch
import urllib.error

from lib.moonFixWizard import verificar_github_username


class GithubUsernameVerificationTests(unittest.TestCase):
    def test_rate_limit_is_treated_as_warning(self):
        http_error = urllib.error.HTTPError(
            url="https://api.github.com/users/octocat",
            code=429,
            msg="Too Many Requests",
            hdrs=None,
            fp=None,
        )

        with patch("lib.moonFixWizard.urllib.request.urlopen", side_effect=http_error):
            ok, msg = verificar_github_username("octocat")

        self.assertTrue(ok)
        self.assertIn("permite", msg.lower())


if __name__ == "__main__":
    unittest.main()
