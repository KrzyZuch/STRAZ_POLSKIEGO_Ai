-- Migration: 0004_recycled_parts.sql
-- Description: Tables for e-waste recycling database

CREATE TABLE IF NOT EXISTS recycled_devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model TEXT UNIQUE NOT NULL,
    brand TEXT,
    description TEXT,
    teardown_url TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS recycled_parts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    part_name TEXT NOT NULL,
    species TEXT, -- Resistor, IC, Capacitor, etc.
    value TEXT, -- 100k, 5V, etc.
    designator TEXT, -- R1, U2
    description TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (device_id) REFERENCES recycled_devices(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_recycled_parts_device_id ON recycled_parts(device_id);
CREATE INDEX IF NOT EXISTS idx_recycled_devices_model ON recycled_devices(model);
