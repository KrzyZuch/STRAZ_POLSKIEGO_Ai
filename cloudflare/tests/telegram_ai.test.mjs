import test from "node:test";
import assert from "node:assert/strict";

import {
  buildIssueBody,
  buildIssueTitle,
  callProviderWithFallback,
  extractJsonObject,
  handleRecycledKnowledgeLookup,
  moderateIssueCandidate,
  recognizeDeviceAndListParts,
  recommendOnboardingRouteFromText,
  redactSensitiveContent,
  routeTelegramIntent,
  sanitizeTelegramReply,
} from "../src/telegram_ai.js";
import { handleTelegramWebhook } from "../src/telegram_issues.js";

function jsonResponse(payload, status = 200) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
    },
  });
}

function withMockedFetch(impl, callback) {
  const originalFetch = globalThis.fetch;
  globalThis.fetch = impl;
  return Promise.resolve()
    .then(callback)
    .finally(() => {
      globalThis.fetch = originalFetch;
    });
}

function createRecycledCatalogDbMock() {
  const recycledDevicesColumns = [
    "id",
    "model",
    "brand",
    "description",
    "teardown_url",
    "created_at",
    "device_category",
    "source_url",
    "donor_rank",
  ].map((name) => ({ name }));
  const recycledPartsColumns = [
    "id",
    "device_id",
    "part_name",
    "species",
    "value",
    "designator",
    "description",
    "created_at",
    "genus",
    "mounting",
    "keywords",
    "kicad_symbol",
    "kicad_footprint",
    "datasheet_url",
    "quantity",
    "source_url",
    "confidence",
  ].map((name) => ({ name }));
  const recycledPartMasterColumns = [
    "id",
    "part_slug",
    "part_number",
    "normalized_part_number",
    "part_name",
    "species",
    "genus",
    "mounting",
    "value",
    "description",
    "keywords",
    "datasheet_url",
    "datasheet_file_id",
    "ipn",
    "category",
    "parameters",
    "kicad_symbol",
    "kicad_footprint",
    "kicad_reference",
  ].map((name) => ({ name }));
  const recycledDevicePartsColumns = [
    "id",
    "device_id",
    "master_part_id",
    "quantity",
    "designator",
    "source_url",
    "confidence",
    "stock_location",
  ].map((name) => ({ name }));

  return {
    prepare(sql) {
      const normalizedSql = String(sql).replace(/\s+/g, " ").trim();
      const statement = {
        async run() {
          return { success: true };
        },
        async first() {
          return null;
        },
        async all() {
          return { results: [] };
        },
      };
      return {
        ...statement,
        bind(...args) {
          return {
            ...statement,
            async first() {
              if (normalizedSql.includes("FROM recycled_devices d")) {
                const query = String(args[0] || "");
                if (/sonoff basic/i.test(query) || /^basic$/i.test(query)) {
                  return {
                    id: 3,
                    model: "Basic",
                    brand: "Sonoff",
                    description: "Popular Wi-Fi relay board and reliable seed donor for ESP8266-based reuse workflows.",
                    teardown_url: "https://tasmota.github.io/docs/devices/Sonoff-Basic/",
                    device_category: "smart_switch",
                    source_url: "https://tasmota.github.io/docs/devices/Sonoff-Basic/",
                    donor_rank: 0.88,
                  };
                }
              }
              return null;
            },
            async all() {
              if (normalizedSql.includes("PRAGMA table_info(recycled_devices)")) {
                return { results: recycledDevicesColumns };
              }
              if (normalizedSql.includes("PRAGMA table_info(recycled_parts)")) {
                return { results: recycledPartsColumns };
              }
              if (normalizedSql.includes("PRAGMA table_info(recycled_part_master)")) {
                return { results: recycledPartMasterColumns };
              }
              if (normalizedSql.includes("PRAGMA table_info(recycled_device_parts)")) {
                return { results: recycledDevicePartsColumns };
              }
              if (
                normalizedSql.includes("FROM recycled_device_parts rdp") &&
                normalizedSql.includes("JOIN recycled_part_master pm")
              ) {
                return {
                  results: [
                    {
                      part_name: "ESP8266EX",
                      species: "IC",
                      value: "",
                      designator: "U1",
                      description: "Highly integrated Wi-Fi SoC commonly reused in automation and telemetry prototypes.",
                      quantity: 1,
                      datasheet_url:
                        "https://www.espressif.com/sites/default/files/documentation/0a-esp8266ex_datasheet_en.pdf",
                      kicad_symbol: "MCU_Espressif:ESP8266EX",
                      kicad_footprint:
                        "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.3x3.3mm",
                      part_number: "ESP8266EX",
                      ipn: "ESP8266EX",
                      category: "wifi_soc",
                      parameters: "{\"WiFi\":\"2.4GHz\"}",
                      datasheet_file_id: "",
                      kicad_reference: "U",
                      stock_location: "",
                    },
                  ],
                };
              }
              if (
                normalizedSql.includes("FROM recycled_parts") &&
                normalizedSql.includes("WHERE device_id = ?")
              ) {
                return {
                  results: [
                    {
                      part_name: "ESP8266EX",
                      species: "IC",
                      value: "",
                      designator: "U1",
                      description: "Highly integrated Wi-Fi SoC commonly reused in automation and telemetry prototypes.",
                      quantity: 1,
                      datasheet_url:
                        "https://www.espressif.com/sites/default/files/documentation/0a-esp8266ex_datasheet_en.pdf",
                      kicad_symbol: "MCU_Espressif:ESP8266EX",
                      kicad_footprint:
                        "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.3x3.3mm",
                    },
                  ],
                };
              }
              if (normalizedSql.includes("FROM recycled_parts p")) {
                const query = String(args[0] || "");
                if (/atmega328p/i.test(query)) {
                  return {
                    results: [
                      {
                        part_name: "ATmega328P",
                        species: "IC",
                        value: "",
                        designator: "U1",
                        description:
                          "8-bit AVR microcontroller frequently reused from Arduino-compatible boards.",
                        quantity: 1,
                        datasheet_url:
                          "https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-7810-Automotive-Microcontrollers-ATmega328P_Datasheet.pdf",
                        kicad_symbol: "MCU_Microchip_ATmega:ATmega328P-PU",
                        kicad_footprint: "Package_DIP:DIP-28_W7.62mm",
                        device_id: 4,
                        model: "Uno Clone",
                        brand: "Arduino Compatible",
                        device_description:
                          "Seed donor entry for DIP AVR microcontrollers and prototyping support parts.",
                        teardown_url: "",
                      },
                    ],
                  };
                }
              }
              if (normalizedSql.includes("FROM recycled_part_master pm")) {
                const query = String(args[0] || "");
                if (/atmega328p/i.test(query)) {
                  return {
                    results: [
                      {
                        id: 5,
                        part_slug: "atmega328p-pu",
                        part_number: "ATMEGA328P-PU",
                        normalized_part_number: "ATMEGA328P-PU",
                        part_name: "ATmega328P",
                        species: "IC",
                        genus: "microcontroller",
                        mounting: "THT",
                        value: "",
                        description:
                          "8-bit AVR microcontroller frequently reused from Arduino-compatible boards.",
                        keywords: "ATmega328P, AVR, DIP",
                        datasheet_url:
                          "https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-7810-Automotive-Microcontrollers-ATmega328P_Datasheet.pdf",
                        datasheet_file_id: "",
                        ipn: "ATMEGA328P-PU",
                        category: "mcu",
                        parameters: "{\"Flash\":\"32KB\"}",
                        kicad_symbol: "MCU_Microchip_ATmega:ATmega328P-PU",
                        kicad_footprint: "Package_DIP:DIP-28_W7.62mm",
                        kicad_reference: "U",
                        donor_count: 1,
                      },
                    ],
                  };
                }
              }
              return { results: [] };
            },
          };
        },
      };
    },
  };
}

test("routeTelegramIntent keeps onboarding separate from issues", () => {
  assert.deepEqual(routeTelegramIntent("Pomysl: zróbmy panel porównań").intent, "issue");
  assert.deepEqual(routeTelegramIntent("Gdzie mogę pomóc jako backendowiec?").intent, "onboarding");
  assert.deepEqual(routeTelegramIntent("Opowiedz mi więcej o inicjatywie").intent, "chat");
});

test("routeTelegramIntent detects recycled-parts lookup from text", () => {
  assert.equal(routeTelegramIntent("ATmega328P").intent, "device_lookup");
  assert.equal(routeTelegramIntent({ text: "Jakie części są w Sonoff Basic?" }).intent, "device_lookup");
});

test("recommendOnboardingRouteFromText finds data path without hardware", () => {
  const result = recommendOnboardingRouteFromText(
    "Nie mam własnego sprzętu, ale znam backend, API, walidację i mogę pomagać w architekturze danych."
  );
  assert.ok(result);
  assert.equal(result.route.route_id, "data_architecture_without_hardware");
  assert.equal(result.should_suggest_provider_path, true);
});

test("buildIssueTitle keeps original message trimmed without AI rewrite", () => {
  const title = buildIssueTitle({
    content:
      "To jest bardzo długi oryginalny wpis użytkownika, który powinien zostać przycięty, ale bez przepisywania przez AI i bez dodawania prefiksu.",
  });
  assert.equal(title.startsWith("To jest bardzo długi oryginalny wpis użytkownika"), true);
  assert.equal(title.length, 96);
});

test("buildIssueBody stores original and edited text in separate sections", () => {
  const body = buildIssueBody(
    {
      username: "tester",
      chat_id: "123",
      message_id: "7",
      chat_type: "private",
    },
    {
      label: "pomysł",
      content: "surowa tresc telegramowa",
    },
    {
      edited_description: "Uporządkowany opis bez zmiany sensu.",
      additional_context: "Warto powiązać to z istniejącym projektem.",
    }
  );

  assert.match(body, /## Oryginalna wiadomość/);
  assert.match(body, /surowa tresc telegramowa/);
  assert.match(body, /## Zredagowany opis/);
  assert.match(body, /Uporządkowany opis bez zmiany sensu\./);
  assert.match(body, /## Dodatkowe objaśnienie AI/);
});

test("extractJsonObject parses fenced JSON payloads", () => {
  const parsed = extractJsonObject('```json\n{"decision":"accept","reason_code":"ok","reason_text":"OK"}\n```');
  assert.equal(parsed.decision, "accept");
  assert.equal(parsed.reason_code, "ok");
});

test("redaction hides tokens and secret variable names", () => {
  const redacted = redactSensitiveContent(
    "Sekret AIzaSyBardzoTajny123456789012345 i GITHUB_TOKEN oraz Bearer abcdefghijklmnopqrstuvwxyz0123456789"
  );
  assert.doesNotMatch(redacted, /AIza/);
  assert.doesNotMatch(redacted, /GITHUB_TOKEN/);
  assert.doesNotMatch(redacted, /Bearer\s+[A-Za-z0-9._-]{20,}/);
});

test("sanitizeTelegramReply clamps long responses", () => {
  const text = "A".repeat(4000);
  const sanitized = sanitizeTelegramReply(text, { TELEGRAM_AI_MAX_REPLY_CHARS: "200" });
  assert.ok(sanitized.length <= 220);
  assert.match(sanitized, /\[odpowiedź skrócona\]/);
});

test("moderateIssueCandidate returns structured decision from Google provider", async () => {
  const env = {
    TELEGRAM_AI_ENABLED: "true",
    TELEGRAM_AI_PRIMARY_PROVIDER: "google",
    TELEGRAM_AI_FALLBACK_PROVIDER: "nvidia",
    TELEGRAM_AI_GOOGLE_MODEL: "gemma-3-27b-it",
    GEMINI_API_KEY: "test-key",
  };

  const result = await moderateIssueCandidate(
    env,
    {
      kind: "idea",
      label: "pomysł",
      content: "Zróbmy prosty dashboard dla porównań przypadków.",
    },
    {
      chat_id: "123",
      user_id: "456",
      message_id: "9",
      text: "Pomysl: Zróbmy prosty dashboard dla porównań przypadków.",
    },
    [],
    {
      fetchImpl: async () =>
        jsonResponse({
          candidates: [
            {
              content: {
                parts: [
                  {
                    text: '{"decision":"accept","reason_code":"ok","reason_text":"Treść jest konkretna i merytoryczna."}',
                  },
                ],
              },
            },
          ],
        }),
    }
  );

  assert.equal(result.decision, "accept");
  assert.equal(result.reason_code, "ok");
});

test("callProviderWithFallback switches from Google to NVIDIA on 429", async () => {
  const env = {
    TELEGRAM_AI_PRIMARY_PROVIDER: "google",
    TELEGRAM_AI_FALLBACK_PROVIDER: "nvidia",
    TELEGRAM_AI_GOOGLE_MODEL: "gemma-3-27b-it",
    TELEGRAM_AI_NVIDIA_MODEL: "google/gemma-4-31b-it",
    GEMINI_API_KEY: "google-key",
    NVIDIA_API_KEY: "nvidia-key",
  };

  const calls = [];
  const response = await callProviderWithFallback(
    env,
    {
      systemInstruction: "system",
      userPrompt: "user",
      maxTokens: 100,
      temperature: 0.2,
      responseMimeType: "application/json",
    },
    {
      fetchImpl: async (url) => {
        calls.push(url);
        if (url.includes("generativelanguage.googleapis.com")) {
          return jsonResponse(
            {
              error: {
                message: "rate limited",
              },
            },
            429
          );
        }
        return jsonResponse({
          choices: [
            {
              message: {
                content: '{"decision":"accept"}',
              },
            },
          ],
        });
      },
    }
  );

  assert.equal(response.provider_name, "nvidia");
  assert.equal(calls.length, 2);
  assert.ok(calls[0].includes("generativelanguage.googleapis.com"));
  assert.ok(calls[1].includes("integrate.api.nvidia.com"));
});

test("callProviderWithFallback retries Google without developer instruction when model rejects it", async () => {
  const env = {
    TELEGRAM_AI_PRIMARY_PROVIDER: "google",
    TELEGRAM_AI_FALLBACK_PROVIDER: "nvidia",
    TELEGRAM_AI_GOOGLE_MODEL: "gemma-3-27b-it",
    GEMINI_API_KEY: "google-key",
  };

  const requestBodies = [];
  const response = await callProviderWithFallback(
    env,
    {
      systemInstruction: "system guidance",
      userPrompt: "user question",
      maxTokens: 100,
      temperature: 0.2,
      responseMimeType: "application/json",
    },
    {
      fetchImpl: async (_url, init = {}) => {
        requestBodies.push(JSON.parse(init.body));
        if (requestBodies.length === 1) {
          return jsonResponse(
            {
              error: {
                message: "Developer instruction is not enabled for models/gemma-3-27b-it",
              },
            },
            400
          );
        }

        return jsonResponse({
          candidates: [
            {
              content: {
                parts: [
                  {
                    text: '{"decision":"accept"}',
                  },
                ],
              },
            },
          ],
        });
      },
    }
  );

  assert.equal(response.provider_name, "google");
  assert.equal(requestBodies.length, 2);
  const firstPromptText = requestBodies[0].contents[0].parts.map((part) => part.text || "").join(" ");
  const retriedPromptText = requestBodies[1].contents[0].parts.map((part) => part.text || "").join(" ");
  assert.match(firstPromptText, /system guidance/);
  assert.equal(requestBodies[1].systemInstruction, undefined);
  assert.match(retriedPromptText, /system guidance/);
  assert.match(retriedPromptText, /user question/);
});

test("callProviderWithFallback falls back to NVIDIA when Google still rejects developer instruction mode", async () => {
  const env = {
    TELEGRAM_AI_PRIMARY_PROVIDER: "google",
    TELEGRAM_AI_FALLBACK_PROVIDER: "nvidia",
    TELEGRAM_AI_GOOGLE_MODEL: "gemma-3-27b-it",
    TELEGRAM_AI_NVIDIA_MODEL: "google/gemma-4-31b-it",
    GEMINI_API_KEY: "google-key",
    NVIDIA_API_KEY: "nvidia-key",
  };

  const calls = [];
  const response = await callProviderWithFallback(
    env,
    {
      systemInstruction: "system guidance",
      userPrompt: "user question",
      maxTokens: 100,
      temperature: 0.2,
      responseMimeType: "application/json",
    },
    {
      fetchImpl: async (url, init = {}) => {
        calls.push({
          url,
          body: init.body ? JSON.parse(init.body) : null,
        });
        if (url.includes("generativelanguage.googleapis.com")) {
          return jsonResponse(
            {
              error: {
                message: "Developer instruction is not enabled for models/gemma-3-27b-it",
              },
            },
            400
          );
        }

        return jsonResponse({
          choices: [
            {
              message: {
                content: '{"decision":"accept","reason_code":"ok","reason_text":"Przyjęte przez fallback."}',
              },
            },
          ],
        });
      },
    }
  );

  assert.equal(response.provider_name, "nvidia");
  assert.equal(calls.length, 3);
  assert.ok(calls[0].url.includes("generativelanguage.googleapis.com"));
  assert.ok(calls[1].url.includes("generativelanguage.googleapis.com"));
  assert.ok(calls[2].url.includes("integrate.api.nvidia.com"));
});

test("handleRecycledKnowledgeLookup returns device catalog entry from local DB", async () => {
  const response = await handleRecycledKnowledgeLookup(
    {
      DB: createRecycledCatalogDbMock(),
    },
    {
      chat_id: "4",
      user_id: "3",
      message_id: "2",
      text: "Jakie części są w Sonoff Basic?",
    }
  );

  assert.equal(response.provider_name, "local");
  assert.match(response.reply_text, /Sonoff Basic/);
  assert.match(response.reply_text, /ESP8266EX/);
});

test("handleRecycledKnowledgeLookup returns donor devices for part query", async () => {
  const response = await handleRecycledKnowledgeLookup(
    {
      DB: createRecycledCatalogDbMock(),
    },
    {
      chat_id: "7",
      user_id: "8",
      message_id: "9",
      text: "ATmega328P",
    }
  );

  assert.equal(response.provider_name, "local");
  assert.match(response.reply_text, /ATmega328P/);
  assert.match(response.reply_text, /Arduino Compatible Uno Clone/);
});

test("recognizeDeviceAndListParts sends inline media to Google provider", async () => {
  const env = {
    DB: null,
    GEMINI_API_KEY: "google-key",
    TELEGRAM_AI_PRIMARY_PROVIDER: "google",
    TELEGRAM_AI_FALLBACK_PROVIDER: "nvidia",
    TELEGRAM_AI_GOOGLE_MODEL: "gemma-3-27b-it",
  };

  let requestBody = null;
  await withMockedFetch(async (url, init = {}) => {
    if (url.includes("generativelanguage.googleapis.com")) {
      requestBody = JSON.parse(init.body);
      return jsonResponse({
        candidates: [
          {
            content: {
              parts: [
                {
                  text: '{"brand":"Sonoff","model":"Basic","confidence":0.95}',
                },
              ],
            },
          },
        ],
      });
    }
    throw new Error(`Unexpected URL: ${url}`);
  }, async () => {
    const response = await recognizeDeviceAndListParts(
      env,
      { mime_type: "image/jpeg" },
      "AQID"
    );

    assert.ok(
      requestBody.contents[0].parts.some(
        (part) => part.inline_data?.mime_type === "image/jpeg" && part.inline_data?.data === "AQID"
      )
    );
    assert.match(response.reply_text, /Sonoff Basic/);
  });
});

test("handleTelegramWebhook routes onboarding without creating GitHub issue", async () => {
  const env = {
    DB: null,
    TELEGRAM_AI_ENABLED: "true",
    TELEGRAM_ISSUES_ENABLED: "true",
    TELEGRAM_ALLOWED_CHAT_IDS: "*",
    TELEGRAM_BOT_TOKEN: "telegram-token",
    GEMINI_API_KEY: "google-key",
    TELEGRAM_AI_PRIMARY_PROVIDER: "google",
    TELEGRAM_AI_FALLBACK_PROVIDER: "nvidia",
  };
  const calls = [];

  await withMockedFetch(async (url, init = {}) => {
    calls.push(url);
    if (url.includes("api.telegram.org")) {
      return jsonResponse({ ok: true });
    }
    if (url.includes("generativelanguage.googleapis.com")) {
      return jsonResponse({
        candidates: [
          {
            content: {
              parts: [
                {
                  text: "Rekomendowana ścieżka: API, adaptery i integracja danych.\nPierwszy materiał: https://github.com/StrazPrzyszlosci/STRAZ_PRZYSZLOSCI/blob/main/docs/PRZYKLADY_GOTOWEGO_KODU.md\nPierwsze zadania: issue:aq-09, issue:aq-13",
                },
              ],
            },
          },
        ],
      });
    }
    throw new Error(`Unexpected URL: ${url}`);
  }, async () => {
    const request = new Request("https://example.workers.dev/integrations/telegram/webhook", {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify({
        update_id: 1,
        message: {
          message_id: 2,
          from: { id: 3, username: "tester" },
          chat: { id: 4, type: "private" },
          text: "Gdzie mogę pomóc, jeśli znam backend i API?",
        },
      }),
    });
    const response = await handleTelegramWebhook(request, env);
    const payload = await response.json();

    assert.equal(payload.results[0].status, "onboarding_replied");
    assert.equal(calls.some((url) => String(url).includes("/repos/")), false);
  });
});

test("handleTelegramWebhook routes recycled-parts lookup without AI provider call", async () => {
  const env = {
    DB: null,
    TELEGRAM_AI_ENABLED: "true",
    TELEGRAM_ISSUES_ENABLED: "true",
    TELEGRAM_ALLOWED_CHAT_IDS: "*",
    TELEGRAM_BOT_TOKEN: "telegram-token",
  };
  const calls = [];

  await withMockedFetch(async (url) => {
    calls.push(url);
    if (url.includes("api.telegram.org")) {
      return jsonResponse({ ok: true });
    }
    throw new Error(`Unexpected URL: ${url}`);
  }, async () => {
    const request = new Request("https://example.workers.dev/integrations/telegram/webhook", {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify({
        update_id: 1,
        message: {
          message_id: 2,
          from: { id: 3, username: "tester" },
          chat: { id: 4, type: "private" },
          text: "ATmega328P",
        },
      }),
    });
    const response = await handleTelegramWebhook(request, env);
    const payload = await response.json();

    assert.equal(payload.results[0].status, "lookup_replied");
    assert.equal(
      calls.some((url) => String(url).includes("generativelanguage.googleapis.com")),
      false
    );
  });
});

test("handleTelegramWebhook creates issue after accepted moderation", async () => {
  const env = {
    DB: null,
    TELEGRAM_AI_ENABLED: "true",
    TELEGRAM_ISSUES_ENABLED: "true",
    TELEGRAM_ISSUES_DRY_RUN: "false",
    TELEGRAM_ALLOWED_CHAT_IDS: "*",
    TELEGRAM_BOT_TOKEN: "telegram-token",
    GEMINI_API_KEY: "google-key",
    GITHUB_TOKEN: "github-token",
    GITHUB_REPO_OWNER: "StrazPrzyszlosci",
    GITHUB_REPO_NAME: "STRAZ_PRZYSZLOSCI",
  };
  const calls = [];
  let googleCall = 0;

  await withMockedFetch(async (url, init = {}) => {
    calls.push(url);
    if (url.includes("api.telegram.org")) {
      return jsonResponse({ ok: true });
    }
    if (url.includes("generativelanguage.googleapis.com")) {
      googleCall += 1;
      if (googleCall === 1) {
        return jsonResponse({
          candidates: [
            {
              content: {
                parts: [
                  {
                    text: '{"decision":"accept","reason_code":"ok","reason_text":"Merytoryczne zgłoszenie."}',
                  },
                ],
              },
            },
          ],
        });
      }
      return jsonResponse({
        candidates: [
          {
            content: {
              parts: [
                {
                  text: '{"edited_description":"Uporządkowany opis pomysłu.","additional_context":"Może być powiązane z dokumentacją adapterów."}',
                },
              ],
            },
          },
        ],
      });
    }
    if (url.includes("api.github.com/repos/StrazPrzyszlosci/STRAZ_PRZYSZLOSCI/issues")) {
      const draft = JSON.parse(init.body);
      assert.equal(draft.title, "Zróbmy prosty dashboard porównujący przypadki.");
      assert.match(draft.body, /## Oryginalna wiadomość/);
      assert.match(draft.body, /## Zredagowany opis/);
      return jsonResponse({
        number: 321,
        html_url: "https://github.com/StrazPrzyszlosci/STRAZ_PRZYSZLOSCI/issues/321",
      });
    }
    throw new Error(`Unexpected URL: ${url}`);
  }, async () => {
    const request = new Request("https://example.workers.dev/integrations/telegram/webhook", {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify({
        update_id: 1,
        message: {
          message_id: 2,
          from: { id: 3, username: "tester" },
          chat: { id: 4, type: "private" },
          text: "Pomysl: Zróbmy prosty dashboard porównujący przypadki.",
        },
      }),
    });
    const response = await handleTelegramWebhook(request, env);
    const payload = await response.json();

    assert.equal(payload.results[0].status, "created");
    assert.equal(calls.some((url) => String(url).includes("api.github.com/repos/StrazPrzyszlosci/STRAZ_PRZYSZLOSCI/issues")), true);
  });
});

test("handleTelegramWebhook rejects off-topic issue without GitHub call", async () => {
  const env = {
    DB: null,
    TELEGRAM_AI_ENABLED: "true",
    TELEGRAM_ISSUES_ENABLED: "true",
    TELEGRAM_ISSUES_DRY_RUN: "false",
    TELEGRAM_ALLOWED_CHAT_IDS: "*",
    TELEGRAM_BOT_TOKEN: "telegram-token",
    GEMINI_API_KEY: "google-key",
  };
  const calls = [];

  await withMockedFetch(async (url) => {
    calls.push(url);
    if (url.includes("api.telegram.org")) {
      return jsonResponse({ ok: true });
    }
    if (url.includes("generativelanguage.googleapis.com")) {
      return jsonResponse({
        candidates: [
          {
            content: {
              parts: [
                {
                  text: '{"decision":"reject_off_topic","reason_code":"off_topic","reason_text":"Treść nie dotyczy inicjatywy ani repozytorium."}',
                },
              ],
            },
          },
        ],
      });
    }
    throw new Error(`Unexpected URL: ${url}`);
  }, async () => {
    const request = new Request("https://example.workers.dev/integrations/telegram/webhook", {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify({
        update_id: 1,
        message: {
          message_id: 2,
          from: { id: 3, username: "tester" },
          chat: { id: 4, type: "private" },
          text: "Pomysl: sprzedam używany rower.",
        },
      }),
    });
    const response = await handleTelegramWebhook(request, env);
    const payload = await response.json();

    assert.equal(payload.results[0].status, "reject_off_topic");
    assert.equal(calls.some((url) => String(url).includes("api.github.com/repos/")), false);
  });
});
