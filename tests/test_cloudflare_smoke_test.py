import unittest

from cloudflare.provider_smoke_test import (
    build_provider_id,
    normalize_base_url,
    prepare_demo_payloads,
)


class CloudflareSmokeTestHelpers(unittest.TestCase):
    def test_normalize_base_url_adds_scheme_and_trims_slash(self) -> None:
        self.assertEqual(
            normalize_base_url(" fish-pond-api.example.workers.dev/ "),
            "https://fish-pond-api.example.workers.dev",
        )
        self.assertEqual(
            normalize_base_url("http://127.0.0.1:8787/"),
            "http://127.0.0.1:8787",
        )

    def test_build_provider_id_uses_suffix(self) -> None:
        self.assertEqual(
            build_provider_id("community-demo-node-01", "12345"),
            "community-demo-node-01-12345",
        )

    def test_prepare_demo_payloads_uses_consistent_provider_id(self) -> None:
        registration, observation, event_payload = prepare_demo_payloads("12345")
        self.assertEqual(registration["provider_id"], "community-demo-node-01-12345")
        self.assertEqual(
            observation["provider"]["provider_id"],
            registration["provider_id"],
        )
        self.assertEqual(
            event_payload["provider"]["provider_id"],
            registration["provider_id"],
        )

    def test_prepare_demo_payloads_can_switch_environment(self) -> None:
        registration, observation, event_payload = prepare_demo_payloads(
            "12345",
            provider_environment="prod",
        )
        self.assertEqual(registration["provider_id"], "community-prod-node-01-12345")
        self.assertEqual(observation["provider"]["provider_id"], registration["provider_id"])
        self.assertEqual(event_payload["provider"]["provider_id"], registration["provider_id"])


if __name__ == "__main__":
    unittest.main()
