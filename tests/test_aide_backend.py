# -*- coding: utf-8 -*-
"""AIDE: disponibilidad honesta, saneado del contexto y privacidad."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib import aide_backend
from lib.i18n import tr


class AvailabilityTest(unittest.TestCase):
    def test_copilot_without_sdk_reports_missing_sdk(self):
        with mock.patch.dict(sys.modules, {"copilot": None}):
            state = aide_backend.copilot_available()
        self.assertFalse(state.ok)
        self.assertEqual(state.reason, "missing_sdk")
        # La interfaz traduce el motivo; el backend no lleva texto de usuario.
        self.assertTrue(tr("aide.state_missing_sdk").startswith("Falta"))

    def test_openai_without_endpoint_is_unavailable(self):
        state = aide_backend.openai_available({"endpoint": "", "api_key": "k"})
        self.assertFalse(state.ok)
        self.assertEqual(state.reason, "no_endpoint")

    def test_openai_without_key_is_unavailable(self):
        state = aide_backend.openai_available(
            {"endpoint": "https://x/v1", "api_key": ""}
        )
        self.assertFalse(state.ok)
        self.assertEqual(state.reason, "no_key")

    def test_openai_with_endpoint_and_key_is_available(self):
        state = aide_backend.openai_available(
            {"endpoint": "https://x/v1", "api_key": "k"}
        )
        self.assertTrue(state.ok)
        self.assertTrue(bool(state))

    def test_availability_routes_by_provider(self):
        with mock.patch.object(
            aide_backend,
            "openai_available",
            return_value=aide_backend.Availability(True, "ready"),
        ) as spy:
            aide_backend.availability({"provider": "openai"})
        spy.assert_called_once()

    def test_ask_refuses_when_provider_unavailable(self):
        answer = aide_backend.ask(
            "hola", settings={"provider": "openai", "endpoint": "", "api_key": ""}
        )
        self.assertFalse(answer.ok)
        self.assertTrue(answer.error)


class PromptTest(unittest.TestCase):
    def test_system_prompt_mentions_repo_rules(self):
        prompt = aide_backend.build_system_prompt("3.2.7")
        self.assertIn("PackageMaker", prompt)
        self.assertIn("3.2.7", prompt)
        self.assertIn("projectNameFormatter", prompt)

    def test_prompt_without_files_has_no_context_block(self):
        prompt = aide_backend.compose_prompt("solo esto")
        self.assertIn("solo esto", prompt)
        self.assertNotIn("Contexto del proyecto", prompt)

    def test_context_block_sanitises_credentials(self):
        files = {"config.py": "TOKEN=ghp_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"}
        block = aide_backend.build_context_block(files)
        self.assertNotIn("ghp_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", block)
        self.assertIn("config.py", block)

    def test_compose_prompt_orders_system_context_message(self):
        prompt = aide_backend.compose_prompt("pregunta", {"a.py": "x = 1"})
        self.assertLess(prompt.index("PackageMaker"), prompt.index("Contexto del proyecto"))
        self.assertLess(prompt.index("Contexto del proyecto"), prompt.index("pregunta"))


class CollectContextTest(unittest.TestCase):
    def test_collects_only_allowed_text_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "main.py").write_text("print(1)\n", encoding="utf-8")
            (root / "datos.json").write_text("{}\n", encoding="utf-8")
            (root / "foto.png").write_bytes(b"\x89PNG\r\n")
            (root / ".env").write_text("SECRETO=1\n", encoding="utf-8")
            (root / ".git").mkdir()
            (root / ".git" / "config").write_text("x", encoding="utf-8")
            context = aide_backend.collect_project_context(root)
        self.assertEqual(sorted(context), ["datos.json", "main.py"])

    def test_respects_file_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for i in range(10):
                (root / f"f{i}.py").write_text("x = 1\n", encoding="utf-8")
            context = aide_backend.collect_project_context(root, max_files=3)
        self.assertEqual(len(context), 3)

    def test_truncates_long_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "largo.py").write_text("x" * 5000, encoding="utf-8")
            context = aide_backend.collect_project_context(root, max_chars=100)
        self.assertEqual(len(context["largo.py"]), 100)

    def test_missing_directory_returns_empty(self):
        self.assertEqual(aide_backend.collect_project_context("/no/existe"), {})


class OpenAITransportTest(unittest.TestCase):
    def test_ask_openai_parses_content(self):
        payload = b'{"choices": [{"message": {"content": "hola"}}]}'

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return payload

        with mock.patch.object(
            aide_backend.urllib.request, "urlopen", return_value=FakeResponse()
        ):
            answer = aide_backend._ask_openai(
                "x",
                {"endpoint": "https://x/v1", "api_key": "k", "model": "m"},
                timeout=5,
            )
        self.assertTrue(answer.ok)
        self.assertEqual(answer.text, "hola")
        self.assertEqual(answer.model, "m")

    def test_ask_openai_reports_unexpected_shape(self):
        payload = b'{"nada": 1}'

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return payload

        with mock.patch.object(
            aide_backend.urllib.request, "urlopen", return_value=FakeResponse()
        ):
            answer = aide_backend._ask_openai(
                "x", {"endpoint": "https://x/v1", "api_key": "k"}, timeout=5
            )
        self.assertFalse(answer.ok)
        self.assertIn("inesperada", answer.error)


if __name__ == "__main__":
    unittest.main()
