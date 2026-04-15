-- Migration: 0005_recycled_parts_catalog.sql
-- Description: Extend recycled parts catalog for GitHub-first donor knowledge

ALTER TABLE recycled_devices ADD COLUMN device_category TEXT;
ALTER TABLE recycled_devices ADD COLUMN source_url TEXT;
ALTER TABLE recycled_devices ADD COLUMN donor_rank REAL;

ALTER TABLE recycled_parts ADD COLUMN genus TEXT;
ALTER TABLE recycled_parts ADD COLUMN mounting TEXT;
ALTER TABLE recycled_parts ADD COLUMN keywords TEXT;
ALTER TABLE recycled_parts ADD COLUMN kicad_symbol TEXT;
ALTER TABLE recycled_parts ADD COLUMN kicad_footprint TEXT;
ALTER TABLE recycled_parts ADD COLUMN datasheet_url TEXT;
ALTER TABLE recycled_parts ADD COLUMN quantity INTEGER;
ALTER TABLE recycled_parts ADD COLUMN source_url TEXT;
ALTER TABLE recycled_parts ADD COLUMN confidence REAL;

CREATE TABLE IF NOT EXISTS recycled_device_aliases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    alias TEXT NOT NULL,
    alias_type TEXT NOT NULL DEFAULT 'device_alias',
    source TEXT,
    created_at TEXT NOT NULL,
    UNIQUE (device_id, alias, alias_type),
    FOREIGN KEY (device_id) REFERENCES recycled_devices(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS recycled_part_aliases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_id INTEGER NOT NULL,
    alias TEXT NOT NULL,
    alias_type TEXT NOT NULL DEFAULT 'part_alias',
    source TEXT,
    created_at TEXT NOT NULL,
    UNIQUE (part_id, alias, alias_type),
    FOREIGN KEY (part_id) REFERENCES recycled_parts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS recycled_device_evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    part_id INTEGER,
    source_type TEXT NOT NULL,
    source_url TEXT,
    excerpt TEXT,
    confidence REAL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (device_id) REFERENCES recycled_devices(id) ON DELETE CASCADE,
    FOREIGN KEY (part_id) REFERENCES recycled_parts(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS recycled_device_submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id TEXT,
    user_id TEXT,
    message_id TEXT,
    lookup_kind TEXT NOT NULL,
    query_text TEXT,
    recognized_brand TEXT,
    recognized_model TEXT,
    matched_device_id INTEGER,
    matched_part_name TEXT,
    attachment_file_id TEXT,
    attachment_mime_type TEXT,
    provider_name TEXT,
    model_name TEXT,
    status TEXT NOT NULL DEFAULT 'queued',
    raw_payload_json TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (matched_device_id) REFERENCES recycled_devices(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_recycled_device_aliases_alias
    ON recycled_device_aliases(alias);
CREATE INDEX IF NOT EXISTS idx_recycled_part_aliases_alias
    ON recycled_part_aliases(alias);
CREATE INDEX IF NOT EXISTS idx_recycled_parts_part_name
    ON recycled_parts(part_name);
CREATE INDEX IF NOT EXISTS idx_recycled_device_submissions_status
    ON recycled_device_submissions(status, created_at DESC);
