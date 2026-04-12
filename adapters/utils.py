from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DATA_DIR = ROOT / "data" / "sample"
PROVIDER_ID_ALLOWED_ENVIRONMENTS = ("local", "demo", "preview", "staging", "prod")
PROVIDER_KIND_TO_ID_PREFIX = {
    "company": "company",
    "farm": "farm",
    "community": "community",
    "research": "research",
    "edge_node": "edge",
}
PROVIDER_ID_SEGMENT_RE = re.compile(r"^[a-z0-9]+$")


def load_sample_json(filename: str) -> Dict[str, Any]:
    with (SAMPLE_DATA_DIR / filename).open(encoding="utf-8") as handle:
        return json.load(handle)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def validate_provider_id(provider_id: str, provider_kind: str | None = None) -> str:
    if not isinstance(provider_id, str) or not provider_id:
        raise ValueError("Pole provider_id musi być niepustym tekstem.")

    segments = provider_id.split("-")
    if len(segments) < 4:
        raise ValueError(
            "Pole provider_id musi mieć format kind-environment-slug-01, np. community-demo-node-01."
        )

    for segment in segments:
        if not segment or PROVIDER_ID_SEGMENT_RE.fullmatch(segment) is None:
            raise ValueError(
                "Pole provider_id może zawierać tylko małe litery, cyfry i znak '-'."
            )

    environment = segments[1]
    if environment not in PROVIDER_ID_ALLOWED_ENVIRONMENTS:
        allowed = ", ".join(PROVIDER_ID_ALLOWED_ENVIRONMENTS)
        raise ValueError(
            f"Drugi segment provider_id musi oznaczać środowisko: {allowed}."
        )

    if len(segments[-1]) < 2 or not segments[-1].isdigit():
        raise ValueError(
            "Ostatni segment provider_id musi być numerycznym sufiksem, np. 01."
        )

    if provider_kind is not None:
        expected_prefix = PROVIDER_KIND_TO_ID_PREFIX.get(provider_kind)
        if expected_prefix is None:
            raise ValueError(f"Nieobsługiwany provider_kind: {provider_kind}.")
        if segments[0] != expected_prefix:
            raise ValueError(
                "Pierwszy segment provider_id musi odpowiadać provider_kind, "
                f"np. {expected_prefix}-{environment}-..."
            )

    return provider_id


def get_provider_environment(provider_id: str) -> str:
    validate_provider_id(provider_id)
    return provider_id.split("-")[1]


def replace_provider_environment(provider_id: str, environment: str) -> str:
    if environment not in PROVIDER_ID_ALLOWED_ENVIRONMENTS:
        allowed = ", ".join(PROVIDER_ID_ALLOWED_ENVIRONMENTS)
        raise ValueError(f"Nieobsługiwane środowisko providera. Dozwolone: {allowed}.")
    validate_provider_id(provider_id)
    segments = provider_id.split("-")
    segments[1] = environment
    return "-".join(segments)


def append_provider_suffix(provider_id: str, suffix: str) -> str:
    validate_provider_id(provider_id)
    safe_suffix = str(suffix).strip()
    if not safe_suffix or PROVIDER_ID_SEGMENT_RE.fullmatch(safe_suffix) is None:
        raise ValueError("Sufiks provider_id może zawierać tylko małe litery i cyfry.")
    return f"{provider_id}-{safe_suffix}"


def parse_allowed_provider_environments(
    value: str | None,
    deployment_environment: str | None = None,
) -> set[str] | None:
    if deployment_environment is not None and deployment_environment not in PROVIDER_ID_ALLOWED_ENVIRONMENTS:
        allowed = ", ".join(PROVIDER_ID_ALLOWED_ENVIRONMENTS)
        raise ValueError(f"Nieobsługiwane deployment environment. Dozwolone: {allowed}.")

    if value is None or not value.strip():
        if deployment_environment is None:
            return None
        return {deployment_environment}

    normalized = value.strip().lower()
    if normalized == "*":
        return None

    result: set[str] = set()
    for item in normalized.split(","):
        environment = item.strip()
        if environment not in PROVIDER_ID_ALLOWED_ENVIRONMENTS:
            allowed = ", ".join(PROVIDER_ID_ALLOWED_ENVIRONMENTS)
            raise ValueError(f"Nieobsługiwane środowisko providera. Dozwolone: {allowed}.")
        result.add(environment)
    return result


def ensure_provider_environment_allowed(
    provider_id: str,
    allowed_environments: set[str] | None,
    deployment_environment: str | None = None,
) -> str:
    provider_environment = get_provider_environment(provider_id)
    if allowed_environments is None:
        return provider_environment
    if provider_environment not in allowed_environments:
        allowed = ", ".join(sorted(allowed_environments))
        if deployment_environment is not None:
            raise ValueError(
                "Provider environment nie jest dozwolony w tym środowisku API. "
                f"provider={provider_environment}, deployment={deployment_environment}, dozwolone={allowed}."
            )
        raise ValueError(
            "Provider environment nie jest dozwolony w tym środowisku API. "
            f"provider={provider_environment}, dozwolone={allowed}."
        )
    return provider_environment


def validate_provider_descriptor_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    required = ["provider_id", "provider_kind", "provider_label"]
    missing = [field for field in required if field not in payload]
    if missing:
        raise ValueError(f"Brak wymaganych pól providera: {', '.join(missing)}")

    validate_provider_id(payload["provider_id"], payload["provider_kind"])
    return payload


def validate_observation_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    required_fields = [
        "schema_version",
        "provider",
        "pond",
        "measurement_time",
        "water_temperature_c",
        "dissolved_oxygen_mg_l",
        "ph",
    ]
    missing = [field for field in required_fields if field not in payload]
    if missing:
        raise ValueError(f"Brak wymaganych pól obserwacji: {', '.join(missing)}")

    if payload["schema_version"] != "v1":
        raise ValueError("Nieobsługiwana wersja schematu obserwacji.")

    provider = payload["provider"]
    pond = payload["pond"]
    if "provider_id" not in provider:
        raise ValueError("Brak provider.provider_id")
    if "pond_id" not in pond:
        raise ValueError("Brak pond.pond_id")
    validate_provider_id(provider["provider_id"], provider.get("provider_kind"))

    ph = payload["ph"]
    oxygen = payload["dissolved_oxygen_mg_l"]
    temperature = payload["water_temperature_c"]
    ammonia = payload.get("ammonia_mg_l")
    flow_rate = payload.get("flow_rate_l_min")

    if not 0 <= ph <= 14:
        raise ValueError("Pole ph musi być w zakresie 0-14.")
    if oxygen < 0:
        raise ValueError("Pole dissolved_oxygen_mg_l nie może być ujemne.")
    if not -5 <= temperature <= 45:
        raise ValueError("Pole water_temperature_c jest poza rozsądnym zakresem.")
    if ammonia is not None and ammonia < 0:
        raise ValueError("Pole ammonia_mg_l nie może być ujemne.")
    if flow_rate is not None and flow_rate < 0:
        raise ValueError("Pole flow_rate_l_min nie może być ujemne.")

    return payload


def validate_event_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    required_fields = ["schema_version", "provider", "pond", "event_time", "event_type"]
    missing = [field for field in required_fields if field not in payload]
    if missing:
        raise ValueError(f"Brak wymaganych pól zdarzenia: {', '.join(missing)}")

    if payload["schema_version"] != "v1":
        raise ValueError("Nieobsługiwana wersja schematu zdarzenia.")

    provider = payload["provider"]
    if "provider_id" not in provider:
        raise ValueError("Brak provider.provider_id")
    validate_provider_id(provider["provider_id"], provider.get("provider_kind"))

    event_type = payload["event_type"]
    if event_type == "fish_behavior_summary" and "behavior_summary" not in payload:
        raise ValueError("Zdarzenie fish_behavior_summary wymaga behavior_summary.")

    return payload


def make_provider_status(
    provider_id: str,
    *,
    status: str = "ok",
    supports_water_quality: bool = True,
    supports_flow_monitoring: bool = True,
    supports_edge_vision_summary: bool = False,
) -> Dict[str, Any]:
    return {
        "provider_id": provider_id,
        "status": status,
        "last_seen_at": utc_now_iso(),
        "schema_version": "v1",
        "supports_water_quality": supports_water_quality,
        "supports_flow_monitoring": supports_flow_monitoring,
        "supports_edge_vision_summary": supports_edge_vision_summary,
    }
