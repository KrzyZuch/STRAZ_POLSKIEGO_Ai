CREATE TABLE IF NOT EXISTS telegram_issue_throttle (
  throttle_key TEXT PRIMARY KEY,
  last_accepted_at TEXT NOT NULL,
  last_message_id TEXT,
  last_update_id TEXT,
  message_count INTEGER NOT NULL DEFAULT 0
);
