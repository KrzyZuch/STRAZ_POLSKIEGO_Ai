from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _append_reason(reasons: List[str], code: str) -> None:
    if code not in reasons:
        reasons.append(code)


def _calculate_confidence(observation: Dict[str, Any], last_event: Optional[Dict[str, Any]]) -> float:
    confidence = 0.55
    if observation.get("ammonia_mg_l") is not None:
        confidence += 0.08
    if observation.get("flow_rate_l_min") is not None:
        confidence += 0.08
    if last_event and "behavior_summary" in last_event:
        confidence += min(float(last_event["behavior_summary"].get("confidence", 0.0)) * 0.15, 0.12)
    return min(round(confidence, 2), 0.95)


def _summarize(risk_level: str, recommendation: str, reasons: List[str]) -> str:
    if not reasons:
        return "Brak istotnych anomalii w obserwacji stawu."
    readable = ", ".join(reasons[:3])
    return f"Poziom ryzyka: {risk_level}. Zalecenie: {recommendation}. Powody: {readable}."


def generate_recommendation(
    observation: Dict[str, Any],
    *,
    context: Optional[Dict[str, Any]] = None,
    last_event: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    del context  # v1 nie wykorzystuje jeszcze osobnej warstwy kontekstu.

    risk_score = 0
    reasons: List[str] = []

    oxygen = float(observation["dissolved_oxygen_mg_l"])
    ph = float(observation["ph"])
    temperature = float(observation["water_temperature_c"])
    ammonia = observation.get("ammonia_mg_l")
    flow_rate = observation.get("flow_rate_l_min")

    if oxygen < 4.0:
        risk_score += 5
        _append_reason(reasons, "LOW_DISSOLVED_OXYGEN_CRITICAL")
    elif oxygen < 5.0:
        risk_score += 3
        _append_reason(reasons, "LOW_DISSOLVED_OXYGEN")
    elif oxygen < 6.0:
        risk_score += 1
        _append_reason(reasons, "DISSOLVED_OXYGEN_TREND_DOWN")

    if ammonia is not None:
        ammonia_value = float(ammonia)
        if ammonia_value >= 0.2:
            risk_score += 3
            _append_reason(reasons, "AMMONIA_HIGH")
        elif ammonia_value >= 0.05:
            risk_score += 1
            _append_reason(reasons, "AMMONIA_ELEVATED")

    if ph < 6.5 or ph > 8.5:
        risk_score += 2
        _append_reason(reasons, "PH_OUT_OF_RANGE")
    elif ph < 6.8 or ph > 8.2:
        risk_score += 1
        _append_reason(reasons, "PH_DRIFT")

    if flow_rate is not None:
        flow_value = float(flow_rate)
        if flow_value < 60:
            risk_score += 2
            _append_reason(reasons, "FLOW_RATE_LOW")
        elif flow_value < 100:
            risk_score += 1
            _append_reason(reasons, "FLOW_RATE_BELOW_TARGET")

    if temperature > 28:
        risk_score += 1
        _append_reason(reasons, "WATER_TEMPERATURE_HIGH")

    if last_event and last_event.get("event_type") == "fish_behavior_summary":
        behavior = last_event.get("behavior_summary", {})
        if float(behavior.get("surface_gasping_score", 0.0)) >= 0.6:
            risk_score += 2
            _append_reason(reasons, "SURFACE_ACTIVITY_ANOMALY")
        if float(behavior.get("anomaly_score", 0.0)) >= 0.7:
            risk_score += 2
            _append_reason(reasons, "FISH_BEHAVIOR_ANOMALY")
        if behavior.get("activity_level") in {"very_low", "erratic"}:
            risk_score += 1
            _append_reason(reasons, "ACTIVITY_PATTERN_ABNORMAL")
        if int(behavior.get("visible_mortality_count", 0)) > 0:
            risk_score += 4
            _append_reason(reasons, "VISIBLE_MORTALITY_DETECTED")

    if risk_score >= 8:
        risk_level = "critical"
    elif risk_score >= 5:
        risk_level = "high"
    elif risk_score >= 2:
        risk_level = "medium"
    else:
        risk_level = "low"

    if (
        "LOW_DISSOLVED_OXYGEN_CRITICAL" in reasons
        or "LOW_DISSOLVED_OXYGEN" in reasons
        or "SURFACE_ACTIVITY_ANOMALY" in reasons
    ):
        recommendation = "check_aeration"
    elif "AMMONIA_HIGH" in reasons or "PH_OUT_OF_RANGE" in reasons:
        recommendation = "consider_water_exchange"
    elif "FLOW_RATE_LOW" in reasons or "FLOW_RATE_BELOW_TARGET" in reasons:
        recommendation = "inspect_pond"
    elif reasons:
        recommendation = "inspect_pond"
    else:
        recommendation = "observe"

    confidence = _calculate_confidence(observation, last_event)

    return {
        "schema_version": observation["schema_version"],
        "provider_id": observation["provider"]["provider_id"],
        "pond_id": observation["pond"]["pond_id"],
        "analysis_time": _utc_now_iso(),
        "risk_level": risk_level,
        "recommendation": recommendation,
        "confidence": confidence,
        "reason_codes": reasons,
        "summary": _summarize(risk_level, recommendation, reasons),
    }
