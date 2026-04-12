import unittest

from adapters.utils import (
    append_provider_suffix,
    ensure_provider_environment_allowed,
    get_provider_environment,
    parse_allowed_provider_environments,
    replace_provider_environment,
    validate_provider_id,
)


class ProviderIdConventionTests(unittest.TestCase):
    def test_valid_provider_id_passes(self) -> None:
        provider_id = validate_provider_id("community-demo-node-01", "community")
        self.assertEqual(provider_id, "community-demo-node-01")

    def test_invalid_environment_fails(self) -> None:
        with self.assertRaises(ValueError):
            validate_provider_id("community-public-node-01", "community")

    def test_invalid_prefix_for_kind_fails(self) -> None:
        with self.assertRaises(ValueError):
            validate_provider_id("company-demo-node-01", "community")

    def test_invalid_suffix_fails(self) -> None:
        with self.assertRaises(ValueError):
            validate_provider_id("community-demo-node-aa", "community")

    def test_get_provider_environment(self) -> None:
        self.assertEqual(
            get_provider_environment("community-staging-node-01"),
            "staging",
        )

    def test_replace_provider_environment(self) -> None:
        self.assertEqual(
            replace_provider_environment("community-demo-node-01", "prod"),
            "community-prod-node-01",
        )

    def test_append_provider_suffix(self) -> None:
        self.assertEqual(
            append_provider_suffix("community-demo-node-01", "12345"),
            "community-demo-node-01-12345",
        )

    def test_parse_allowed_environments_defaults_to_deployment(self) -> None:
        self.assertEqual(
            parse_allowed_provider_environments(None, "prod"),
            {"prod"},
        )

    def test_parse_allowed_environments_star_means_all(self) -> None:
        self.assertIsNone(parse_allowed_provider_environments("*", "prod"))

    def test_environment_gate_rejects_non_allowed_environment(self) -> None:
        with self.assertRaises(ValueError):
            ensure_provider_environment_allowed(
                "community-demo-node-01",
                {"prod"},
                "prod",
            )


if __name__ == "__main__":
    unittest.main()
