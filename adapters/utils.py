from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DATA_DIR = ROOT / "data" / "sample"


def load_sample_json(filename: str) -> Dict[str, Any]:
    with (SAMPLE_DATA_DIR / filename).open(encoding="utf-8") as handle:
        return json.load(handle)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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
