import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from lib import pm_data
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


class PMDataCorruptionTests(unittest.TestCase):
    """Un pm.data válido como JSON pero con forma inesperada no debe tumbar la app."""

    def _load(self, temp_dir, payload):
        path = Path(temp_dir) / "pm.data"
        path.write_text(payload, encoding="utf-8")
        return PMDataStore(path)

    def test_non_object_document_falls_back_to_defaults(self):
        for payload in ("[]", '"text"', "42", "null"):
            with self.subTest(payload=payload), tempfile.TemporaryDirectory() as temp_dir:
                store = self._load(temp_dir, payload)
                self.assertEqual(store.get_user("language"), DEFAULT_USER["language"])
                self.assertIsInstance(store._data["user"], dict)
                self.assertIsInstance(store._data["readonly"], dict)

    def test_non_object_sections_are_rebuilt(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = self._load(
                temp_dir,
                json.dumps({"schema_version": 1, "user": [], "readonly": "x", "translation_cache": 5}),
            )
            self.assertEqual(store.get_user("language"), DEFAULT_USER["language"])
            self.assertEqual(store.get_translation_cache("en"), {})
            self.assertIsInstance(store.get_readonly(), dict)

    def test_valid_user_values_survive_section_repair(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = self._load(
                temp_dir,
                json.dumps({"user": {"language": "en"}, "readonly": [], "translation_cache": {}}),
            )
            self.assertEqual(store.get_user("language"), "en")
            self.assertEqual(store.to_legacy_app_config()["LANGUAGE"], "en")

    def test_non_object_legacy_settings_are_ignored(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = self._load(temp_dir, "{}")
            store.migrate_from_legacy_config([1, 2, 3])
            store.migrate_from_legacy_config("text")
            self.assertEqual(store.get_user("language"), DEFAULT_USER["language"])

    def test_merged_config_survives_non_object_settings(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            legacy = root / "settings.json"
            legacy.write_text("[1, 2, 3]", encoding="utf-8")
            store = PMDataStore(root / "pm.data")
            with patch.object(pm_data, "_store", store):
                config = pm_data.load_merged_app_config(legacy_config_path=legacy)
            self.assertEqual(config["LANGUAGE"], DEFAULT_USER["language"])


if __name__ == "__main__":
    unittest.main()
