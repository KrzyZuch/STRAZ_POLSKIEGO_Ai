-- Migration: 0011_recycled_parts_normalized.sql
-- Description: Normalize recycled parts into canonical parts + donor relations while keeping recycled_parts as compatibility read-model

CREATE TABLE IF NOT EXISTS recycled_part_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_slug TEXT NOT NULL UNIQUE,
    part_number TEXT NOT NULL,
    normalized_part_number TEXT NOT NULL,
    part_name TEXT NOT NULL,
    species TEXT,
    genus TEXT,
    mounting TEXT,
    value TEXT,
    description TEXT,
    keywords TEXT,
    datasheet_url TEXT,
    datasheet_file_id TEXT,
    ipn TEXT,
    category TEXT,
    parameters TEXT,
    kicad_symbol TEXT,
    kicad_footprint TEXT,
    kicad_reference TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_recycled_part_master_part_number
    ON recycled_part_master(normalized_part_number);

CREATE TABLE IF NOT EXISTS recycled_device_parts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    master_part_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    designator TEXT NOT NULL DEFAULT '',
    source_url TEXT,
    confidence REAL,
    stock_location TEXT NOT NULL DEFAULT '',
    evidence_url TEXT,
    evidence_timecode REAL,
    created_at TEXT NOT NULL,
    UNIQUE(device_id, master_part_id, designator, stock_location),
    FOREIGN KEY (device_id) REFERENCES recycled_devices(id) ON DELETE CASCADE,
    FOREIGN KEY (master_part_id) REFERENCES recycled_part_master(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_recycled_device_parts_device
    ON recycled_device_parts(device_id);

CREATE INDEX IF NOT EXISTS idx_recycled_device_parts_master
    ON recycled_device_parts(master_part_id);

ALTER TABLE recycled_parts ADD COLUMN master_part_id INTEGER;
ALTER TABLE recycled_device_submissions ADD COLUMN master_part_id INTEGER;
ALTER TABLE recycled_device_submissions ADD COLUMN ingest_source TEXT;
ALTER TABLE recycled_device_submissions ADD COLUMN evidence_url TEXT;
ALTER TABLE recycled_device_submissions ADD COLUMN evidence_timecode REAL;

INSERT INTO recycled_part_master (
    part_slug,
    part_number,
    normalized_part_number,
    part_name,
    species,
    genus,
    mounting,
    value,
    description,
    keywords,
    datasheet_url,
    datasheet_file_id,
    ipn,
    category,
    parameters,
    kicad_symbol,
    kicad_footprint,
    kicad_reference,
    created_at,
    updated_at
)
SELECT
    LOWER(REPLACE(REPLACE(COALESCE(ipn, part_name), ' ', '-'), '/', '-')) as part_slug,
    COALESCE(ipn, part_name) as part_number,
    LOWER(REPLACE(REPLACE(COALESCE(ipn, part_name), ' ', ''), '-', '')) as normalized_part_number,
    part_name,
    species,
    genus,
    mounting,
    value,
    description,
    keywords,
    datasheet_url,
    datasheet_file_id,
    ipn,
    category,
    parameters,
    kicad_symbol,
    kicad_footprint,
    kicad_reference,
    COALESCE(created_at, CURRENT_TIMESTAMP),
    COALESCE(created_at, CURRENT_TIMESTAMP)
FROM recycled_parts
WHERE NOT EXISTS (
    SELECT 1 FROM recycled_part_master rpm
    WHERE rpm.normalized_part_number = LOWER(REPLACE(REPLACE(COALESCE(recycled_parts.ipn, recycled_parts.part_name), ' ', ''), '-', ''))
);

UPDATE recycled_parts
SET master_part_id = (
    SELECT rpm.id
    FROM recycled_part_master rpm
    WHERE rpm.normalized_part_number = LOWER(REPLACE(REPLACE(COALESCE(recycled_parts.ipn, recycled_parts.part_name), ' ', ''), '-', ''))
    LIMIT 1
)
WHERE master_part_id IS NULL;

INSERT INTO recycled_device_parts (
    device_id,
    master_part_id,
    quantity,
    designator,
    source_url,
    confidence,
    stock_location,
    created_at
)
SELECT
    device_id,
    master_part_id,
    COALESCE(quantity, 1),
    COALESCE(designator, ''),
    source_url,
    confidence,
    COALESCE(stock_location, ''),
    COALESCE(created_at, CURRENT_TIMESTAMP)
FROM recycled_parts
WHERE master_part_id IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM recycled_device_parts rdp
      WHERE rdp.device_id = recycled_parts.device_id
        AND rdp.master_part_id = recycled_parts.master_part_id
        AND rdp.designator = COALESCE(recycled_parts.designator, '')
        AND rdp.stock_location = COALESCE(recycled_parts.stock_location, '')
  );
