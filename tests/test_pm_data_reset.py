import tempfile
import unittest
from pathlib import Path

from lib.pm_data import DEFAULT_USER, PMDataStore


class PMDataResetTests(unittest.TestCase):
    def test_reset_removes_user_preferences_and_translation_cache(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_path = Path(temp_dir) / "pm.data"
            store = PMDataStore(data_path)
            store.set_user("language", "en")
            store.set_user("base_dir", "/custom/projects")
            store.set_translation_cache_entry("en", "Hola", "Hello")
            self.assertTrue(store.save())

            self.assertTrue(store.reset_user_configuration())
            reloaded = PMDataStore(data_path)

            self.assertEqual(reloaded.get_user("language"), DEFAULT_USER["language"])
            self.assertEqual(reloaded.get_user("base_dir"), DEFAULT_USER["base_dir"])
            self.assertEqual(reloaded.get_translation_cache("en"), {})
            self.assertIn("readonly", reloaded._data)


if __name__ == "__main__":
    unittest.main()
