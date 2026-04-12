from __future__ import annotations

from typing import Any, Dict

from adapters.utils import (
    load_sample_json,
    make_provider_status,
    validate_event_payload,
    validate_observation_payload,
)

CANONICAL_PROVIDER_ID = "company-demo-provider-a-01"


def fetch_or_receive(resource: str = "observation") -> Dict[str, Any]:
    mapping = {
        "observation": "provider_a_raw_observation.json",
        "event": "provider_a_raw_event.json",
    }
    if resource not in mapping:
        raise ValueError(f"Nieznany zasób provider-a: {resource}")
    return load_sample_json(mapping[resource])


def normalize(payload: Dict[str, Any]) -> Dict[str, Any]:
    if "waterTempC" in payload:
        return {
            "schema_version": "v1",
            "provider": {
                "provider_id": CANONICAL_PROVIDER_ID,
                "provider_kind": "company",
                "provider_label": payload["providerLabel"],
                "node_class": "cloud_connector",
                "supports_water_quality": True,
                "supports_flow_monitoring": True,
                "supports_edge_vision_summary": True,
            },
            "pond": {
                "pond_id": payload["pondCode"],
                "site_id": payload.get("siteCode"),
                "pond_label": payload.get("pondLabel"),
                "species": payload.get("species"),
            },
            "measurement_time": payload["capturedAt"],
            "water_temperature_c": payload["waterTempC"],
            "dissolved_oxygen_mg_l": payload["oxygenMgL"],
            "ph": payload["phValue"],
            "ammonia_mg_l": payload.get("nh3MgL"),
            "flow_rate_l_min": payload.get("flowLpm"),
            "source_quality": "measured",
            "raw_reference": payload.get("recordId"),
        }

    return {
        "schema_version": "v1",
        "provider": {
            "provider_id": CANONICAL_PROVIDER_ID,
            "provider_kind": "company",
            "provider_label": payload["providerLabel"],
            "node_class": "cloud_connector",
            "supports_water_quality": True,
            "supports_flow_monitoring": True,
            "supports_edge_vision_summary": True,
        },
        "pond": {
            "pond_id": payload["pondCode"],
            "site_id": payload.get("siteCode"),
            "pond_label": payload.get("pondLabel"),
            "species": payload.get("species"),
        },
        "event_time": payload["capturedAt"],
        "event_type": "fish_behavior_summary",
        "severity": payload.get("severity", "warning"),
        "behavior_summary": {
            "activity_level": payload["visionSummary"]["activity"],
            "surface_gasping_score": payload["visionSummary"]["surfaceGasping"],
            "school_dispersion_score": payload["visionSummary"]["dispersion"],
            "feeding_response_score": payload["visionSummary"]["feedingResponse"],
            "visible_mortality_count": payload["visionSummary"]["deadVisible"],
            "anomaly_score": payload["visionSummary"]["anomalyScore"],
            "confidence": payload["visionSummary"]["confidence"],
            "clip_reference": payload["visionSummary"].get("clipRef"),
            "notes": payload["visionSummary"].get("notes"),
        },
    }


def validate(payload: Dict[str, Any]) -> Dict[str, Any]:
    if "measurement_time" in payload:
        return validate_observation_payload(payload)
    if "event_time" in payload:
        return validate_event_payload(payload)
    raise ValueError("Nie rozpoznano typu payloadu provider-a.")


def send_result(result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "provider_id": CANONICAL_PROVIDER_ID,
        "status": "accepted",
        "result": result,
    }


def check_status() -> Dict[str, Any]:
    return make_provider_status(
        CANONICAL_PROVIDER_ID,
        supports_water_quality=True,
        supports_flow_monitoring=True,
        supports_edge_vision_summary=True,
    )
