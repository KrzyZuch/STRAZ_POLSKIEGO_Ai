import { toIsoNow } from "./base_utils.js";

export async function upsertUserSession(env, chat_id, user_id, session_type, device_id, device_name = null, platform = "telegram") {
  const db = env.DB;
  const now = toIsoNow();
  const prefixedChatId = platform === "discord" ? `dc:${chat_id}` : chat_id;
  const prefixedUserId = platform === "discord" ? `dc:${user_id}` : user_id;
  await db.prepare(
    `
INSERT INTO telegram_user_sessions (chat_id, user_id, session_type, active_device_id, active_device_name, status, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, 'active', ?, ?)
ON CONFLICT(chat_id, user_id, session_type) DO UPDATE SET
  active_device_id = EXCLUDED.active_device_id,
  active_device_name = EXCLUDED.active_device_name,
  status = 'active',
  updated_at = EXCLUDED.updated_at
`
  ).bind(prefixedChatId, prefixedUserId, session_type, device_id, device_name, now, now).run();
}

export async function getUserSession(env, chat_id, user_id, session_type, platform = "telegram") {
  const db = env.DB;
  const prefixedChatId = platform === "discord" ? `dc:${chat_id}` : chat_id;
  const prefixedUserId = platform === "discord" ? `dc:${user_id}` : user_id;
  return await db.prepare(
    `SELECT * FROM telegram_user_sessions
WHERE chat_id = ? AND user_id = ? AND session_type = ? AND status = 'active'
AND updated_at > datetime('now', '-1 hour')`
  ).bind(prefixedChatId, prefixedUserId, session_type).first();
}

export async function closeUserSession(env, chat_id, user_id, session_type, platform = "telegram") {
  const db = env.DB;
  const now = toIsoNow();
  const prefixedChatId = platform === "discord" ? `dc:${chat_id}` : chat_id;
  const prefixedUserId = platform === "discord" ? `dc:${user_id}` : user_id;
  await db.prepare(
    `UPDATE telegram_user_sessions SET status = 'closed', updated_at = ? WHERE chat_id = ? AND user_id = ? AND session_type = ?`
  ).bind(now, prefixedChatId, prefixedUserId, session_type).run();
}

export async function closeAllUserSessions(env, chat_id, user_id, platform = "telegram") {
  const db = env.DB;
  const now = toIsoNow();
  const prefixedChatId = platform === "discord" ? `dc:${chat_id}` : chat_id;
  const prefixedUserId = platform === "discord" ? `dc:${user_id}` : user_id;
  await db.prepare(
    `UPDATE telegram_user_sessions SET status = 'closed', updated_at = ? WHERE chat_id = ? AND user_id = ?`
  ).bind(now, prefixedChatId, prefixedUserId).run();
}
