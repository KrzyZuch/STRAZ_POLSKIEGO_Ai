function jsonResponse(payload, status = 200) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
    },
  });
}

function isTruthy(value) {
  if (typeof value !== "string") {
    return false;
  }
  return ["1", "true", "yes", "on"].includes(value.trim().toLowerCase());
}

function parseAllowedIds(rawValue) {
  if (!rawValue || !rawValue.trim()) {
    return null;
  }
  if (rawValue.trim() === "*") {
    return null;
  }

  const allowlist = new Set();
  for (const item of rawValue.split(",")) {
    const normalized = item.trim();
    if (normalized) {
      allowlist.add(normalized);
    }
  }
  return allowlist.size ? allowlist : null;
}

function parsePositiveInteger(rawValue, fallback) {
  const parsed = Number.parseInt(rawValue, 10);
  if (Number.isFinite(parsed) && parsed > 0) {
    return parsed;
  }
  return fallback;
}

function stripPrefix(messageText) {
  if (typeof messageText !== "string") {
    return null;
  }
  const trimmed = messageText.trim();
  if (!trimmed) {
    return null;
  }

  const matchers = [
    {
      kind: "idea",
      prefix: "Pomysl",
      pattern: /^\s*(pomysl|pomysł)\s*:\s*/iu,
    },
    {
      kind: "feedback",
      prefix: "Uwaga",
      pattern: /^\s*(uwaga|zastrzezenie|zastrzeżenie)\s*:\s*/iu,
    },
  ];

  for (const matcher of matchers) {
    if (matcher.pattern.test(trimmed)) {
      const content = trimmed.replace(matcher.pattern, "").trim();
      if (!content) {
        return null;
      }
      return {
        kind: matcher.kind,
        prefix: matcher.prefix,
        content,
      };
    }
  }

  return null;
}

function summarizeTitle(prefix, content) {
  const shortened = content.replace(/\s+/g, " ").trim().slice(0, 80);
  return `[${prefix}] ${shortened || "zgloszenie z telegrama"}`;
}

function getConfiguredLabels(kind, env) {
  const labels = [];
  const channelLabel = (env.TELEGRAM_CHANNEL_LABEL || "").trim();
  const kindLabel =
    kind === "idea"
      ? (env.TELEGRAM_IDEA_LABEL || "").trim()
      : (env.TELEGRAM_FEEDBACK_LABEL || "").trim();

  if (kindLabel) {
    labels.push(kindLabel);
  }
  if (channelLabel) {
    labels.push(channelLabel);
  }
  return labels;
}

function formatActor(message) {
  if (message.username) {
    return `@${message.username}`;
  }
  if (message.user_id) {
    return `user_id:${message.user_id}`;
  }
  return "nieznany";
}

function buildIssueDraft(message, classification, env) {
  const title = summarizeTitle(classification.prefix, classification.content);
  const labels = getConfiguredLabels(classification.kind, env);

  const body = [
    "## Kanał wejścia",
    "",
    "Telegram",
    "",
    "## Treść wiadomości",
    "",
    classification.content,
    "",
    "## Zgłaszający",
    "",
    `- nadawca: ${formatActor(message)}`,
    `- chat_id: ${message.chat_id || "brak"}`,
    `- message_id: ${message.message_id || "brak"}`,
    `- chat_type: ${message.chat_type || "brak"}`,
  ].join("\n");

  return { title, body, labels };
}

function getTelegramThrottleKey(message) {
  if (message.chat_id && message.user_id) {
    return `${message.chat_id}:${message.user_id}`;
  }
  if (message.chat_id) {
    return `chat:${message.chat_id}`;
  }
  if (message.user_id) {
    return `user:${message.user_id}`;
  }
  return "unknown";
}

function elapsedSecondsSince(isoTimestamp) {
  if (typeof isoTimestamp !== "string" || !isoTimestamp.trim()) {
    return null;
  }
  const parsed = Date.parse(isoTimestamp);
  if (Number.isNaN(parsed)) {
    return null;
  }
  return Math.floor((Date.now() - parsed) / 1000);
}

async function ensureTelegramThrottleSchema(db) {
  await db.prepare(
    `
    CREATE TABLE IF NOT EXISTS telegram_issue_throttle (
      throttle_key TEXT PRIMARY KEY,
      last_accepted_at TEXT NOT NULL,
      last_message_id TEXT,
      last_update_id TEXT,
      message_count INTEGER NOT NULL DEFAULT 0
    )
    `
  ).run();
}

async function checkTelegramThrottle(env, message) {
  const db = env.DB;
  if (!db) {
    return { allowed: true, reason: "no_db" };
  }

  const throttleWindowSeconds = parsePositiveInteger(
    env.TELEGRAM_MIN_INTERVAL_SECONDS,
    60
  );
  if (throttleWindowSeconds <= 0) {
    return { allowed: true, reason: "disabled" };
  }

  await ensureTelegramThrottleSchema(db);

  const throttleKey = getTelegramThrottleKey(message);
  const row = await db.prepare(
    `
    SELECT last_accepted_at
    FROM telegram_issue_throttle
    WHERE throttle_key = ?
    `
  ).bind(throttleKey).first();

  if (row?.last_accepted_at) {
    const elapsedSeconds = elapsedSecondsSince(row.last_accepted_at);
    if (elapsedSeconds !== null && elapsedSeconds < throttleWindowSeconds) {
      return {
        allowed: false,
        reason: "too_many_requests",
        retry_after_seconds: throttleWindowSeconds - elapsedSeconds,
      };
    }
  }

  return {
    allowed: true,
    throttleKey,
    throttleWindowSeconds,
  };
}

async function recordTelegramThrottle(env, message, throttleKey) {
  const db = env.DB;
  if (!db) {
    return;
  }

  await ensureTelegramThrottleSchema(db);
  await db.prepare(
    `
    INSERT INTO telegram_issue_throttle (
      throttle_key,
      last_accepted_at,
      last_message_id,
      last_update_id,
      message_count
    ) VALUES (?, ?, ?, ?, 1)
    ON CONFLICT(throttle_key) DO UPDATE SET
      last_accepted_at = excluded.last_accepted_at,
      last_message_id = excluded.last_message_id,
      last_update_id = excluded.last_update_id,
      message_count = telegram_issue_throttle.message_count + 1
    `
  ).bind(
    throttleKey,
    new Date().toISOString(),
    message.message_id || null,
    message.update_id || null
  ).run();
}

function collectInboundMessages(payload) {
  const result = [];
  const candidates = [
    payload.message,
    payload.edited_message,
    payload.channel_post,
    payload.edited_channel_post,
  ];

  for (const item of candidates) {
    const text = item?.text;
    if (typeof text !== "string") {
      continue;
    }

    result.push({
      update_id: payload.update_id || null,
      message_id: item.message_id || null,
      text,
      date: item.date || null,
      chat_id: item.chat?.id !== undefined ? String(item.chat.id) : null,
      chat_type: item.chat?.type || null,
      user_id: item.from?.id !== undefined ? String(item.from.id) : null,
      username: item.from?.username || null,
      first_name: item.from?.first_name || null,
    });
  }

  return result;
}

async function createGitHubIssue(env, draft) {
  const owner = (env.GITHUB_REPO_OWNER || "").trim();
  const repo = (env.GITHUB_REPO_NAME || "").trim();
  const token = env.GITHUB_TOKEN;

  if (!owner || !repo) {
    throw new Error("Brak konfiguracji repozytorium GitHub dla integracji Telegram.");
  }
  if (!token) {
    throw new Error("Brak sekretu GITHUB_TOKEN dla integracji Telegram.");
  }

  const response = await fetch(`https://api.github.com/repos/${owner}/${repo}/issues`, {
    method: "POST",
    headers: {
      accept: "application/vnd.github+json",
      authorization: `Bearer ${token}`,
      "content-type": "application/json; charset=utf-8",
      "user-agent": "straz-przyszlosci-telegram-bridge",
      "x-github-api-version": "2022-11-28",
    },
    body: JSON.stringify({
      title: draft.title,
      body: draft.body,
      labels: draft.labels,
    }),
  });

  const payload = await response.json();
  if (!response.ok) {
    const message =
      payload?.message || "GitHub API odrzuciło próbę utworzenia Issue.";
    throw new Error(message);
  }

  return payload;
}

function getExpectedTelegramWebhookPath(env) {
  const pathSegment = (env.TELEGRAM_WEBHOOK_PATH_SEGMENT || "").trim();
  if (pathSegment) {
    return `/integrations/telegram/webhook/${pathSegment}`;
  }
  return "/integrations/telegram/webhook";
}

export function isTelegramWebhookRequest(url, env) {
  return url.pathname === getExpectedTelegramWebhookPath(env);
}

function verifyTelegramSecretToken(request, env) {
  const expected = (env.TELEGRAM_WEBHOOK_SECRET_TOKEN || "").trim();
  if (!expected) {
    return true;
  }

  const received =
    request.headers.get("X-Telegram-Bot-Api-Secret-Token") ||
    request.headers.get("x-telegram-bot-api-secret-token");
  return received === expected;
}

export async function handleTelegramWebhook(request, env) {
  if (!isTruthy(env.TELEGRAM_ISSUES_ENABLED || "")) {
    return jsonResponse(
      {
        status: "disabled",
        message: "Integracja Telegram -> GitHub Issues jest wyłączona.",
      },
      200
    );
  }

  if (!verifyTelegramSecretToken(request, env)) {
    return jsonResponse({ error: "Nieprawidłowy sekret webhooka Telegram." }, 403);
  }

  let payload;
  try {
    payload = await request.json();
  } catch {
    return jsonResponse({ error: "Nieprawidłowy JSON webhooka Telegram." }, 400);
  }

  const messages = collectInboundMessages(payload);
  const dryRun = isTruthy(env.TELEGRAM_ISSUES_DRY_RUN || "");
  const allowedChatIds = parseAllowedIds(env.TELEGRAM_ALLOWED_CHAT_IDS || "");
  const results = [];

  for (const message of messages) {
    if (allowedChatIds && !allowedChatIds.has(String(message.chat_id))) {
      results.push({
        update_id: message.update_id,
        message_id: message.message_id,
        status: "ignored_chat_not_allowed",
      });
      continue;
    }

    const classification = stripPrefix(message.text);
    if (!classification) {
      results.push({
        update_id: message.update_id,
        message_id: message.message_id,
        status: "ignored_unrecognized_format",
      });
      continue;
    }

    const throttleCheck = await checkTelegramThrottle(env, message);
    if (!throttleCheck.allowed) {
      results.push({
        update_id: message.update_id,
        message_id: message.message_id,
        status: "throttled",
        retry_after_seconds: throttleCheck.retry_after_seconds || null,
        kind: classification.kind,
      });
      continue;
    }

    const draft = buildIssueDraft(message, classification, env);
    if (dryRun) {
      await recordTelegramThrottle(env, message, throttleCheck.throttleKey);
      results.push({
        update_id: message.update_id,
        message_id: message.message_id,
        status: "dry_run",
        kind: classification.kind,
        title: draft.title,
      });
      continue;
    }

    const issue = await createGitHubIssue(env, draft);
    await recordTelegramThrottle(env, message, throttleCheck.throttleKey);
    results.push({
      update_id: message.update_id,
      message_id: message.message_id,
      status: "created",
      kind: classification.kind,
      issue_number: issue.number,
      issue_url: issue.html_url,
    });
  }

  return jsonResponse(
    {
      status: "accepted",
      processed_messages: messages.length,
      dry_run: dryRun,
      results,
    },
    200
  );
}
