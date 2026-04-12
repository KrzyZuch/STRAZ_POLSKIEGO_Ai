import unittest

from cloudflare.whatsapp_issue_smoke_test import (
    build_text_message_payload,
    normalize_base_url,
    sign_payload,
)


class WhatsAppIssueSmokeTestHelpers(unittest.TestCase):
    def test_normalize_base_url_adds_scheme_and_trims_slash(self) -> None:
        self.assertEqual(
            normalize_base_url(" fish-pond-api.example.workers.dev/ "),
            "https://fish-pond-api.example.workers.dev",
        )
        self.assertEqual(
            normalize_base_url("http://127.0.0.1:8787/"),
            "http://127.0.0.1:8787",
        )

    def test_build_text_message_payload_contains_text_message(self) -> None:
        payload = build_text_message_payload("48500100200", "pomysl: test")
        message = payload["entry"][0]["changes"][0]["value"]["messages"][0]
        self.assertEqual(message["from"], "48500100200")
        self.assertEqual(message["text"]["body"], "pomysl: test")
        self.assertEqual(message["type"], "text")

    def test_sign_payload_uses_sha256_prefix(self) -> None:
        signature = sign_payload('{"hello":"world"}', "secret")
        self.assertTrue(signature.startswith("sha256="))
        self.assertEqual(
            signature,
            "sha256=2677ad3e7c090b2fa2c0fb13020d66d5420879b8316eb356a2d60fb9073bc778",
        )


if __name__ == "__main__":
    unittest.main()
