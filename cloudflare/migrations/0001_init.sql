CREATE TABLE IF NOT EXISTS providers (
  provider_id TEXT PRIMARY KEY,
  provider_kind TEXT NOT NULL,
  provider_label TEXT NOT NULL,
  node_class TEXT,
  supports_water_quality INTEGER NOT NULL DEFAULT 0,
  supports_flow_monitoring INTEGER NOT NULL DEFAULT 0,
  supports_edge_vision_summary INTEGER NOT NULL DEFAULT 0,
  schema_version TEXT NOT NULL DEFAULT 'v1',
  registered_at TEXT NOT NULL,
  last_seen_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS observations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  provider_id TEXT NOT NULL,
  pond_id TEXT NOT NULL,
  measurement_time TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  provider_id TEXT NOT NULL,
  pond_id TEXT NOT NULL,
  event_time TEXT NOT NULL,
  event_type TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS recommendations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  provider_id TEXT NOT NULL,
  pond_id TEXT NOT NULL,
  analysis_time TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);
