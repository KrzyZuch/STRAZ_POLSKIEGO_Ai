function appendReason(reasons, code) {
  if (!reasons.includes(code)) {
    reasons.push(code);
  }
}

function calculateConfidence(observation, lastEvent) {
  let confidence = 0.55;
  if (observation.ammonia_mg_l !== undefined && observation.ammonia_mg_l !== null) {
    confidence += 0.08;
  }
  if (observation.flow_rate_l_min !== undefined && observation.flow_rate_l_min !== null) {
    confidence += 0.08;
  }
  if (lastEvent && lastEvent.behavior_summary) {
    const eventConfidence = Number(lastEvent.behavior_summary.confidence || 0);
    confidence += Math.min(eventConfidence * 0.15, 0.12);
  }
  return Math.min(Number(confidence.toFixed(2)), 0.95);
}

function summarize(riskLevel, recommendation, reasons) {
  if (reasons.length === 0) {
    return "Brak istotnych anomalii w obserwacji stawu.";
  }
  return `Poziom ryzyka: ${riskLevel}. Zalecenie: ${recommendation}. Powody: ${reasons.slice(0, 3).join(", ")}.`;
}

export function generateRecommendation(observation, lastEvent) {
  let riskScore = 0;
  const reasons = [];

  const oxygen = Number(observation.dissolved_oxygen_mg_l);
  const ph = Number(observation.ph);
  const temperature = Number(observation.water_temperature_c);
  const ammonia = observation.ammonia_mg_l;
  const flowRate = observation.flow_rate_l_min;

  if (oxygen < 4.0) {
    riskScore += 5;
    appendReason(reasons, "LOW_DISSOLVED_OXYGEN_CRITICAL");
  } else if (oxygen < 5.0) {
    riskScore += 3;
    appendReason(reasons, "LOW_DISSOLVED_OXYGEN");
  } else if (oxygen < 6.0) {
    riskScore += 1;
    appendReason(reasons, "DISSOLVED_OXYGEN_TREND_DOWN");
  }

  if (ammonia !== undefined && ammonia !== null) {
    const ammoniaValue = Number(ammonia);
    if (ammoniaValue >= 0.2) {
      riskScore += 3;
      appendReason(reasons, "AMMONIA_HIGH");
    } else if (ammoniaValue >= 0.05) {
      riskScore += 1;
      appendReason(reasons, "AMMONIA_ELEVATED");
    }
  }

  if (ph < 6.5 || ph > 8.5) {
    riskScore += 2;
    appendReason(reasons, "PH_OUT_OF_RANGE");
  } else if (ph < 6.8 || ph > 8.2) {
    riskScore += 1;
    appendReason(reasons, "PH_DRIFT");
  }

  if (flowRate !== undefined && flowRate !== null) {
    const flowValue = Number(flowRate);
    if (flowValue < 60) {
      riskScore += 2;
      appendReason(reasons, "FLOW_RATE_LOW");
    } else if (flowValue < 100) {
      riskScore += 1;
      appendReason(reasons, "FLOW_RATE_BELOW_TARGET");
    }
  }

  if (temperature > 28) {
    riskScore += 1;
    appendReason(reasons, "WATER_TEMPERATURE_HIGH");
  }

  if (lastEvent && lastEvent.event_type === "fish_behavior_summary") {
    const behavior = lastEvent.behavior_summary || {};
    if (Number(behavior.surface_gasping_score || 0) >= 0.6) {
      riskScore += 2;
      appendReason(reasons, "SURFACE_ACTIVITY_ANOMALY");
    }
    if (Number(behavior.anomaly_score || 0) >= 0.7) {
      riskScore += 2;
      appendReason(reasons, "FISH_BEHAVIOR_ANOMALY");
    }
    if (["very_low", "erratic"].includes(behavior.activity_level)) {
      riskScore += 1;
      appendReason(reasons, "ACTIVITY_PATTERN_ABNORMAL");
    }
    if (Number(behavior.visible_mortality_count || 0) > 0) {
      riskScore += 4;
      appendReason(reasons, "VISIBLE_MORTALITY_DETECTED");
    }
  }

  let riskLevel = "low";
  if (riskScore >= 8) {
    riskLevel = "critical";
  } else if (riskScore >= 5) {
    riskLevel = "high";
  } else if (riskScore >= 2) {
    riskLevel = "medium";
  }

  let recommendation = "observe";
  if (
    reasons.includes("LOW_DISSOLVED_OXYGEN_CRITICAL") ||
    reasons.includes("LOW_DISSOLVED_OXYGEN") ||
    reasons.includes("SURFACE_ACTIVITY_ANOMALY")
  ) {
    recommendation = "check_aeration";
  } else if (reasons.includes("AMMONIA_HIGH") || reasons.includes("PH_OUT_OF_RANGE")) {
    recommendation = "consider_water_exchange";
  } else if (reasons.includes("FLOW_RATE_LOW") || reasons.includes("FLOW_RATE_BELOW_TARGET")) {
    recommendation = "inspect_pond";
  } else if (reasons.length > 0) {
    recommendation = "inspect_pond";
  }

  return {
    schema_version: observation.schema_version,
    provider_id: observation.provider.provider_id,
    pond_id: observation.pond.pond_id,
    analysis_time: new Date().toISOString(),
    risk_level: riskLevel,
    recommendation,
    confidence: calculateConfidence(observation, lastEvent),
    reason_codes: reasons,
    summary: summarize(riskLevel, recommendation, reasons),
  };
}
