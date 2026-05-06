-- Migration: 0016_discord_platform
-- Dodanie kolumny platform do tabel z prefixem telegram_ aby umożliwić współdzielenie D1 przez bota Discord i Telegram

ALTER TABLE telegram_chat_messages ADD COLUMN platform TEXT NOT NULL DEFAULT 'telegram';
ALTER TABLE telegram_chat_limits ADD COLUMN platform TEXT NOT NULL DEFAULT 'telegram';
ALTER TABLE telegram_issue_throttle ADD COLUMN platform TEXT NOT NULL DEFAULT 'telegram';
ALTER TABLE telegram_issue_moderation_audit ADD COLUMN platform TEXT NOT NULL DEFAULT 'telegram';
ALTER TABLE telegram_user_sessions ADD COLUMN platform TEXT NOT NULL DEFAULT 'telegram';