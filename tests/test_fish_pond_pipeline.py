import unittest

from adapters.mock.adapter import fetch_or_receive as mock_fetch_or_receive
from adapters.mock.adapter import normalize as mock_normalize
from adapters.mock.adapter import validate as mock_validate
from adapters.provider_a.adapter import fetch_or_receive as provider_a_fetch_or_receive
from adapters.provider_a.adapter import normalize as provider_a_normalize
from adapters.provider_a.adapter import validate as provider_a_validate
from models.fish_pond.recommendation_engine import generate_recommendation


class FishPondPipelineTests(unittest.TestCase):
    def test_mock_observation_is_valid(self) -> None:
        observation = mock_validate(mock_normalize(mock_fetch_or_receive("observation")))
        self.assertEqual(observation["schema_version"], "v1")
        self.assertIn("provider", observation)
        self.assertIn("pond", observation)

    def test_mock_event_is_valid(self) -> None:
        event = mock_validate(mock_normalize(mock_fetch_or_receive("event")))
        self.assertEqual(event["event_type"], "fish_behavior_summary")
        self.assertIn("behavior_summary", event)

    def test_different_providers_produce_same_recommendation_shape(self) -> None:
        mock_observation = mock_validate(mock_normalize(mock_fetch_or_receive("observation")))
        mock_event = mock_validate(mock_normalize(mock_fetch_or_receive("event")))
        provider_observation = provider_a_validate(
            provider_a_normalize(provider_a_fetch_or_receive("observation"))
        )
        provider_event = provider_a_validate(
            provider_a_normalize(provider_a_fetch_or_receive("event"))
        )

        mock_result = generate_recommendation(mock_observation, last_event=mock_event)
        provider_result = generate_recommendation(provider_observation, last_event=provider_event)

        self.assertEqual(mock_result["schema_version"], "v1")
        self.assertEqual(provider_result["schema_version"], "v1")
        self.assertEqual(mock_result["risk_level"], provider_result["risk_level"])
        self.assertEqual(mock_result["recommendation"], provider_result["recommendation"])
        self.assertEqual(mock_result["reason_codes"], provider_result["reason_codes"])

    def test_missing_required_field_fails_validation(self) -> None:
        bad_payload = {
            "schema_version": "v1",
            "provider": {"provider_id": "x"},
            "pond": {"pond_id": "pond-alpha"},
            "water_temperature_c": 20.0,
            "dissolved_oxygen_mg_l": 7.0,
            "ph": 7.1,
        }
        with self.assertRaises(ValueError):
            mock_validate(bad_payload)


if __name__ == "__main__":
    unittest.main()
