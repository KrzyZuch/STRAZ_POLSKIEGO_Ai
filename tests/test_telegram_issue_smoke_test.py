import unittest

from cloudflare.telegram_issue_smoke_test import (
    build_text_update,
    build_webhook_url,
    normalize_base_url,
)


class TelegramIssueSmokeTestHelpers(unittest.TestCase):
    def test_normalize_base_url_adds_scheme_and_trims_slash(self) -> None:
        self.assertEqual(
            normalize_base_url(" fish-pond-api.example.workers.dev/ "),
            "https://fish-pond-api.example.workers.dev",
        )
        self.assertEqual(
            normalize_base_url("http://127.0.0.1:8787/"),
            "http://127.0.0.1:8787",
        )

    def test_build_webhook_url_supports_optional_secret_path(self) -> None:
        self.assertEqual(
            build_webhook_url("https://example.workers.dev"),
            "https://example.workers.dev/integrations/telegram/webhook",
        )
        self.assertEqual(
            build_webhook_url("https://example.workers.dev", "sekret"),
            "https://example.workers.dev/integrations/telegram/webhook/sekret",
        )

    def test_build_text_update_contains_message_text(self) -> None:
        payload = build_text_update("500100200", "pomysl: test")
        self.assertEqual(payload["message"]["chat"]["id"], 500100200)
        self.assertEqual(payload["message"]["text"], "pomysl: test")


if __name__ == "__main__":
    unittest.main()
