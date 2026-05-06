import {
  buildCommandReply,
  buildIssueModerationReply,
  buildIssueThrottleReply,
  buildChatThrottleReply,
  checkTelegramChatRateLimit,
  clearTelegramChatHistory,
  draftIssueBody,
  generateChatReply,
  isTruthy,
  loadTelegramChatHistory,
  moderateIssueCandidate,
  parsePositiveInteger,
  recordIssueModerationAudit,
  recommendOnboardingPath,
  routeTelegramIntent,
  saveTelegramConversation,
  handleRecycledKnowledgeLookup,
  recognizeDeviceAndListParts,
  getUserSession,
  upsertUserSession,
  closeUserSession,
  closeAllUserSessions,
  handleResistorAnalysis,
  initDatasheetWorkflow,
  buildIssueTitle,
  buildIssueBody,
} from "./telegram_ai.js";
import { sanitizeTelegramReply } from "./telegram_utils.js";

const DISCORD_PLATFORM = "discord";

function jsonReply(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json; charset=utf-8" },
  });
}

function convertKeyboardToButtons(inlineKeyboard) {
  if (!inlineKeyboard || !inlineKeyboard.length) return null;
  return {
    buttons: inlineKeyboard.map((row) =>
      row.map((btn) => ({
        label: btn.text.slice(0, 80),
        action: btn.url ? "url" : "callback",
        value: btn.callback_data || btn.url,
        style: "primary",
      }))
    ),
  };
}

function buildDiscordResponse(replyData) {
  const markup = convertKeyboardToButtons(replyData.reply_markup?.inline_keyboard);
  return {
    reply_text: replyData.reply_text,
    reply_markup: markup,
    provider_name: replyData.provider_name,
    model_name: replyData.model_name,
  };
}

function parseDiscordBody(body) {
  const text = body.text || body.content || "";
  const stripped = text.trim();

  let command = null;
  let classification = null;

  if (stripped.startsWith("!")) {
    const spaceIdx = stripped.indexOf(" ");
    command = spaceIdx > 1 ? stripped.slice(1, spaceIdx) : stripped.slice(1);
  }

  const lower = stripped.toLowerCase();
  if (!command && (lower.startsWith("pomysl:") || lower.startsWith("pomysł:"))) {
    classification = { kind: "idea", label: "Pomysł", content: stripped };
  } else if (!command && (lower.startsWith("uwaga:") || lower.startsWith("problem:") || lower.startsWith("błąd:") || lower.startsWith("blad:"))) {
    classification = { kind: "feedback", label: "Uwaga", content: stripped };
  }

  return {
    chat_id: body.chat_id || "",
    user_id: body.user_id || "",
    message_id: body.message_id || "",
    text: stripped,
    command,
    classification,
    attachments: body.attachments || [],
    username: body.username || "",
    callback_data: body.callback_data || null,
    type: body.type || "message",
  };
}

async function handleMessage(env, message) {
  if (!message.text && !message.attachments?.length && !message.callback_data) {
    return jsonReply({ reply_text: null });
  }

  const routing = routeTelegramIntent(message);
  let replyData;

  if (routing.intent === "command") {
    replyData = await handleCommand(env, message, routing.command);
  } else if (routing.intent === "issue") {
    replyData = await handleIssue(env, message, routing.classification);
  } else {
    replyData = await handleConversation(env, message, routing.intent);
  }

  return jsonReply(buildDiscordResponse(replyData));
}

async function handleCommand(env, message, command) {
  switch (command) {
    case "start":
    case "menu":
    case "help":
    case "reset":
    case "stop": {
      await closeAllUserSessions(env, message.chat_id, message.user_id, DISCORD_PLATFORM);
      const reply = buildCommandReply(command);
      return reply;
    }
    case "scan":
    case "skanuj": {
      if (message.attachments?.length) {
        const attachment = message.attachments[0];
        const mimeType = attachment.contentType || "image/jpeg";
        if (mimeType.startsWith("image/")) {
          const base64 = await fetchDiscordAttachmentBase64(attachment.url);
          if (base64) {
            const msg = {
              ...message,
              file_id: attachment.url,
              mime_type: mimeType,
              file_name: attachment.name,
            };
            const result = await recognizeDeviceAndListParts(env, msg, base64);
            await upsertUserSession(env, message.chat_id, message.user_id, "recycled_parts", null, null, DISCORD_PLATFORM);
            return result;
          }
        }
      }
      return {
        reply_text: "Wyślij zdjęcie urządzenia/elektrośmiecia, a rozpoznam model i pokażę katalog części reuse. Możesz też dodać model jako podpis pod zdjęciem.",
      };
    }
    case "datasheet":
    case "pdf": {
      if (message.attachments?.length) {
        const att = message.attachments[0];
        const mimeType = att.contentType || "";
        if (mimeType === "application/pdf" || att.name?.toLowerCase().endsWith(".pdf")) {
          const msg = {
            ...message,
            file_id: att.url,
            mime_type: "application/pdf",
            file_name: att.name,
            caption: message.text,
          };
          return await initDatasheetWorkflow(env, msg, "datasheet");
        }
      }
      return {
        reply_text: [
          "📄 **Analiza Datasheet**",
          "",
          "Wyślij PDF datasheetu lub wpisz oznaczenie części.",
          "Przykład: `!datasheet LM358`",
        ].join("\n"),
      };
    }
    case "resistor":
    case "rezystor": {
      const result = await handleResistorAnalysis(env, message);
      return result;
    }
    case "search":
    case "szukaj": {
      const rest = message.text.replace(/^!\w+\s*/, "").trim();
      if (rest) {
        const lookupMsg = { ...message, text: rest };
        return await handleRecycledKnowledgeLookup(env, lookupMsg);
      }
      return {
        reply_text: "🔍 **Szukaj w katalogu reuse** — wpisz model urządzenia lub oznaczenie części po komendzie, np. `!search ESP32`.",
      };
    }
    case "issue":
    case "zglos":
    case "pomysl":
    case "pomysł": {
      return {
        reply_text: [
          "💡 **Zgłoś pomysł/problem**",
          "",
          "Wpisz wiadomość z prefixem `Pomysl:` lub `Uwaga:`, np.:",
          "`Pomysl: dodać integrację z OctoPrint`",
          "`Uwaga: strona ładuje się wolno na Firefox`",
        ].join("\n"),
      };
    }
    default: {
      await closeAllUserSessions(env, message.chat_id, message.user_id, DISCORD_PLATFORM);
      const reply = buildCommandReply("start");
      return reply;
    }
  }
}

async function handleIssue(env, message, classification) {
  const dryRun = isTruthy(env.TELEGRAM_ISSUES_DRY_RUN || "");
  const issuesEnabled = isTruthy(env.TELEGRAM_ISSUES_ENABLED || "");

  if (!issuesEnabled && !dryRun) {
    return {
      reply_text: "Zgłaszanie pomysłów i uwag jest tymczasowo wyłączone.",
    };
  }

  const throttleWindow = parsePositiveInteger(env.TELEGRAM_MIN_INTERVAL_SECONDS, 60);
  if (throttleWindow > 0) {
    const throttle = await checkTelegramIssueThrottle(env, message, throttleWindow);
    if (!throttle.allowed) {
      return {
        reply_text: buildIssueThrottleReply(throttle.retry_after_seconds),
      };
    }
  }

  let history;
  try {
    history = await loadTelegramChatHistory(env, message, DISCORD_PLATFORM);
  } catch (_e) {
    history = [];
  }

  let moderation;
  try {
    moderation = await moderateIssueCandidate(env, classification, message, history);
  } catch (_e) {
    return {
      reply_text: "Przepraszam, nie mogę teraz przeanalizować Twojego zgłoszenia. Spróbuj ponownie za chwilę.",
    };
  }

  await recordIssueModerationAudit(env, moderation, DISCORD_PLATFORM);
  const reason = buildIssueModerationReply(moderation);

  if (reason) {
    return { reply_text: reason };
  }

  let draft;
  try {
    draft = await draftIssueBody(env, classification, history);
  } catch (_e) {
    return {
      reply_text: "Zaakceptowano zgłoszenie, ale wystąpił błąd przy redakcji treści. Zgłoszenie zostanie utworzone w trybie podstawowym.",
      provider_name: "local",
      model_name: "fallback",
    };
  }

  const actor = message.username || message.user_id;
  const title = buildIssueTitle(classification);
  const body = buildIssueBody(message, classification, draft);

  if (dryRun) {
    return {
      reply_text: [
        "📝 **Nowe zgłoszenie (DRY RUN)**",
        "",
        `**Tytuł**: ${title}`,
        `**Typ**: ${classification.label}`,
        "",
        "```",
        body.slice(0, 1800),
        "```",
        "",
        "Tryb dry-run — zgłoszenie NIE zostało utworzone na GitHub.",
        `Autor: ${actor}`,
      ].join("\n"),
    };
  }

  const githubResult = await createGitHubIssue(env, title, body, classification, ["discord", actor]);
  return {
    reply_text: githubResult.reply_text,
    provider_name: "github",
    model_name: "issues",
  };
}

async function handleConversation(env, message, intent) {
  const aiEnabled = isTruthy(env.TELEGRAM_AI_ENABLED || "");
  if (!aiEnabled) {
    return {
      reply_text: "AI chat jest tymczasowo wyłączony.",
    };
  }

  const rateLimit = await checkTelegramChatRateLimit(env, message, DISCORD_PLATFORM);
  if (!rateLimit.allowed) {
    return {
      reply_text: buildChatThrottleReply(rateLimit.retry_after_seconds),
    };
  }

  const history = await loadTelegramChatHistory(env, message, DISCORD_PLATFORM);

  const onboardingIntent = intent === "onboarding";
  let reply;
  if (onboardingIntent) {
    reply = await recommendOnboardingPath(env, message, history);
  } else {
    const sanitized = (message.text || "").slice(0, 4000);
    const msg = { ...message, text: sanitized };
    reply = await recommendOnboardingPath(env, msg, history);
    if (!reply || !reply.reply_text || reply.reply_text.length < 20) {
      reply = await generateChatReply(env, msg, history);
    }
  }

  await saveTelegramConversation(env, message, intent, message.text, reply.reply_text, DISCORD_PLATFORM);

  return reply;
}

async function checkTelegramIssueThrottle(env, message, windowSeconds) {
  const db = env.DB;
  if (!db) return { allowed: true };

  const throttleKey = `${message.chat_id}:${message.user_id}`;

  const row = await db.prepare(
    `SELECT last_accepted_at FROM telegram_issue_throttle WHERE throttle_key = ? AND platform = ?`
  ).bind(throttleKey, DISCORD_PLATFORM).first();

  const now = Date.now();
  if (row?.last_accepted_at) {
    const elapsed = now - Date.parse(row.last_accepted_at);
    if (!Number.isNaN(elapsed) && elapsed < windowSeconds * 1000) {
      return {
        allowed: false,
        retry_after_seconds: Math.ceil((windowSeconds * 1000 - elapsed) / 1000),
      };
    }
  }

  const nowIso = new Date(now).toISOString();
  await db.prepare(
    `
    INSERT INTO telegram_issue_throttle (throttle_key, last_accepted_at, platform)
    VALUES (?, ?, ?)
    ON CONFLICT(throttle_key) DO UPDATE SET
      last_accepted_at = excluded.last_accepted_at,
      platform = excluded.platform
    `
  ).bind(throttleKey, nowIso, DISCORD_PLATFORM).run();

  return { allowed: true };
}

async function fetchDiscordAttachmentBase64(url) {
  try {
    const resp = await fetch(url);
    if (!resp.ok) return null;
    const arrayBuffer = await resp.arrayBuffer();
    const uint8 = new Uint8Array(arrayBuffer);
    let binary = "";
    for (let i = 0; i < uint8.length; i++) {
      binary += String.fromCharCode(uint8[i]);
    }
    return btoa(binary);
  } catch (_e) {
    return null;
  }
}

async function createGitHubIssue(env, title, body, classification, labels = []) {
  const token = env.GITHUB_TOKEN;
  const owner = env.GITHUB_REPO_OWNER;
  const repo = env.GITHUB_REPO_NAME;

  if (!token || !owner || !repo) {
    return { reply_text: "Brak konfiguracji GitHub. Zgłoszenie nie zostało utworzone." };
  }

  try {
    const resp = await fetch(`https://api.github.com/repos/${owner}/${repo}/issues`, {
      method: "POST",
      headers: {
        accept: "application/vnd.github+json",
        authorization: `Bearer ${token}`,
        "content-type": "application/json",
        "x-github-api-version": "2022-11-28",
      },
      body: JSON.stringify({ title, body, labels }),
    });

    const data = await resp.json();
    if (resp.ok && data.html_url) {
      return {
        reply_text: `✅ Zgłoszenie utworzone: ${data.html_url}`,
      };
    }
    return {
      reply_text: `Błąd GitHub (${resp.status}): ${data.message || "Nieznany błąd"}. Spróbuj ponownie później.`,
    };
  } catch (error) {
    return {
      reply_text: "Nie udało się połączyć z GitHub. Spróbuj ponownie później.",
    };
  }
}

export async function handleDiscordWebhook(request, env) {
  const secret = request.headers.get("X-Discord-Bot-Secret");
  const expected = env.DISCORD_BOT_SECRET;

  if (!expected) {
    return jsonReply({ error: "Discord integration not configured on server." }, 503);
  }

  if (!secret || secret !== expected) {
    return jsonReply({ error: "Unauthorized" }, 401);
  }

  let body;
  try {
    body = await request.json();
  } catch (_e) {
    return jsonReply({ error: "Invalid JSON body" }, 400);
  }

  const message = parseDiscordBody(body);
  return await handleMessage(env, message);
}