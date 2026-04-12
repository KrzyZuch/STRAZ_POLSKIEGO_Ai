import { generateRecommendation } from "./recommendation.js";

function jsonResponse(payload, status = 200) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "access-control-allow-origin": "*",
      "access-control-allow-methods": "GET,POST,OPTIONS",
      "access-control-allow-headers": "content-type",
    },
  });
}

function nowIso() {
  return new Date().toISOString();
}

function badRequest(message) {
  return jsonResponse({ error: message }, 400);
}

function validateProviderDescriptor(payload) {
  const required = ["provider_id", "provider_kind", "provider_label"];
  const missing = required.filter((field) => payload[field] === undefined);
  if (missing.length) {
    throw new Error(`Brak wymaganych pól providera: ${missing.join(", ")}`);
  }
  return payload;
}

function validateObservation(payload) {
  const required = [
    "schema_version",
    "provider",
    "pond",
    "measurement_time",
    "water_temperature_c",
    "dissolved_oxygen_mg_l",
    "ph",
  ];
  const missing = required.filter((field) => payload[field] === undefined);
  if (missing.length) {
    throw new Error(`Brak wymaganych pól obserwacji: ${missing.join(", ")}`);
  }
  if (payload.schema_version !== "v1") {
    throw new Error("Nieobsługiwana wersja schematu obserwacji.");
  }
  return payload;
}

function validateEvent(payload) {
  const required = ["schema_version", "provider", "pond", "event_time", "event_type"];
  const missing = required.filter((field) => payload[field] === undefined);
  if (missing.length) {
    throw new Error(`Brak wymaganych pól zdarzenia: ${missing.join(", ")}`);
  }
  if (payload.schema_version !== "v1") {
    throw new Error("Nieobsługiwana wersja schematu zdarzenia.");
  }
  return payload;
}

async function upsertProvider(env, provider) {
  const currentTime = nowIso();
  await env.DB.prepare(
    `
    INSERT INTO providers (
      provider_id, provider_kind, provider_label, node_class,
      supports_water_quality, supports_flow_monitoring, supports_edge_vision_summary,
      schema_version, registered_at, last_seen_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'v1', ?, ?)
    ON CONFLICT(provider_id) DO UPDATE SET
      provider_kind = excluded.provider_kind,
      provider_label = excluded.provider_label,
      node_class = excluded.node_class,
      supports_water_quality = excluded.supports_water_quality,
      supports_flow_monitoring = excluded.supports_flow_monitoring,
      supports_edge_vision_summary = excluded.supports_edge_vision_summary,
      last_seen_at = excluded.last_seen_at
    `
  )
    .bind(
      provider.provider_id,
      provider.provider_kind,
      provider.provider_label,
      provider.node_class || null,
      provider.supports_water_quality ? 1 : 0,
      provider.supports_flow_monitoring ? 1 : 0,
      provider.supports_edge_vision_summary ? 1 : 0,
      currentTime,
      currentTime
    )
    .run();
}

async function saveObservation(env, observation) {
  await env.DB.prepare(
    `
    INSERT INTO observations (provider_id, pond_id, measurement_time, payload_json, created_at)
    VALUES (?, ?, ?, ?, ?)
    `
  )
    .bind(
      observation.provider.provider_id,
      observation.pond.pond_id,
      observation.measurement_time,
      JSON.stringify(observation),
      nowIso()
    )
    .run();
}

async function saveEvent(env, eventPayload) {
  await env.DB.prepare(
    `
    INSERT INTO events (provider_id, pond_id, event_time, event_type, payload_json, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    `
  )
    .bind(
      eventPayload.provider.provider_id,
      eventPayload.pond.pond_id,
      eventPayload.event_time,
      eventPayload.event_type,
      JSON.stringify(eventPayload),
      nowIso()
    )
    .run();
}

async function saveRecommendation(env, recommendation) {
  await env.DB.prepare(
    `
    INSERT INTO recommendations (provider_id, pond_id, analysis_time, payload_json, created_at)
    VALUES (?, ?, ?, ?, ?)
    `
  )
    .bind(
      recommendation.provider_id,
      recommendation.pond_id,
      recommendation.analysis_time,
      JSON.stringify(recommendation),
      nowIso()
    )
    .run();
}

async function readJson(request) {
  try {
    return await request.json();
  } catch {
    throw new Error("Nieprawidłowy JSON.");
  }
}

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return jsonResponse({ ok: true }, 200);
    }

    const url = new URL(request.url);

    try {
      if (request.method === "POST" && url.pathname === "/v1/providers/register") {
        const provider = validateProviderDescriptor(await readJson(request));
        await upsertProvider(env, provider);
        return jsonResponse(
          {
            provider_id: provider.provider_id,
            registration_status: "registered",
            schema_version: "v1",
            message: "Provider został zarejestrowany.",
          },
          201
        );
      }

      if (request.method === "POST" && url.pathname === "/v1/observations") {
        const observation = validateObservation(await readJson(request));
        await upsertProvider(env, observation.provider);
        await saveObservation(env, observation);
        return jsonResponse(
          {
            status: "accepted",
            provider_id: observation.provider.provider_id,
            pond_id: observation.pond.pond_id,
          },
          202
        );
      }

      if (request.method === "POST" && url.pathname === "/v1/events") {
        const eventPayload = validateEvent(await readJson(request));
        await upsertProvider(env, eventPayload.provider);
        await saveEvent(env, eventPayload);
        return jsonResponse(
          {
            status: "accepted",
            provider_id: eventPayload.provider.provider_id,
            pond_id: eventPayload.pond.pond_id,
          },
          202
        );
      }

      if (request.method === "POST" && url.pathname === "/v1/recommendations/fish-pond") {
        const payload = await readJson(request);
        if (!payload.observation) {
          throw new Error("Brak pola observation.");
        }
        const observation = validateObservation(payload.observation);
        const lastEvent = payload.last_behavior_event
          ? validateEvent(payload.last_behavior_event)
          : null;
        const recommendation = generateRecommendation(observation, lastEvent);
        await saveRecommendation(env, recommendation);
        return jsonResponse(recommendation, 200);
      }

      const statusMatch = url.pathname.match(/^\/v1\/providers\/([^/]+)\/status$/);
      if (request.method === "GET" && statusMatch) {
        const providerId = statusMatch[1];
        const result = await env.DB.prepare(
          `
          SELECT provider_id, schema_version, last_seen_at,
                 supports_water_quality, supports_flow_monitoring, supports_edge_vision_summary
          FROM providers
          WHERE provider_id = ?
          `
        )
          .bind(providerId)
          .first();

        if (!result) {
          return jsonResponse({ error: "Nie znaleziono providera." }, 404);
        }

        return jsonResponse(
          {
            provider_id: result.provider_id,
            status: "ok",
            last_seen_at: result.last_seen_at,
            schema_version: result.schema_version,
            supports_water_quality: Boolean(result.supports_water_quality),
            supports_flow_monitoring: Boolean(result.supports_flow_monitoring),
            supports_edge_vision_summary: Boolean(result.supports_edge_vision_summary),
          },
          200
        );
      }

      return jsonResponse({ error: "Nie znaleziono zasobu." }, 404);
    } catch (error) {
      return badRequest(error.message || "Błąd żądania.");
    }
  },
};
