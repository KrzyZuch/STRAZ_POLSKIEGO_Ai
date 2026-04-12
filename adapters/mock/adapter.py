from __future__ import annotations

from typing import Any, Dict

from adapters.utils import (
    load_sample_json,
    make_provider_status,
    validate_event_payload,
    validate_observation_payload,
)


def fetch_or_receive(resource: str = "observation") -> Dict[str, Any]:
    mapping = {
        "observation": "fish_pond_observation.json",
        "event": "fish_behavior_event.json",
    }
    if resource not in mapping:
        raise ValueError(f"Nieznany zasób mock adaptera: {resource}")
    return load_sample_json(mapping[resource])


def normalize(payload: Dict[str, Any]) -> Dict[str, Any]:
    return payload


def validate(payload: Dict[str, Any]) -> Dict[str, Any]:
    if "measurement_time" in payload:
        return validate_observation_payload(payload)
    if "event_time" in payload:
        return validate_event_payload(payload)
    raise ValueError("Nie rozpoznano typu payloadu do walidacji.")


def send_result(result: Dict[str, Any]) -> Dict[str, Any]:
    return result


def check_status() -> Dict[str, Any]:
    return make_provider_status(
        "community-demo-mock-01",
        supports_water_quality=True,
        supports_flow_monitoring=True,
        supports_edge_vision_summary=True,
    )
