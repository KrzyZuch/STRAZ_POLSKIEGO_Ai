-- Migration: 0015_olx_parts_market.sql
-- Description: OLX Parts Market — track electronics/parts offers scraped from OLX Poland API
-- This enables the Straż bot to answer "gdzie kupić część X" queries with live OLX data
-- and powers the INFO_GROUP portals with local market intelligence

-- ============================================================
-- 1. olx_offers — core offer data from OLX API
-- ============================================================
CREATE TABLE IF NOT EXISTS olx_offers (
  id INTEGER PRIMARY KEY,              -- OLX offer ID (from API, e.g. 1065604927)
  olx_url TEXT NOT NULL,                -- Full OLX URL
  title TEXT NOT NULL,                  -- Offer title
  description TEXT,                     -- Full description (HTML from API)
  price_value INTEGER,                  -- Price in PLN grosze (API returns value in PLN, not grosze!)
  price_currency TEXT DEFAULT 'PLN',    -- Currency code
  price_label TEXT,                     -- Human-readable price label e.g. "1 299 zł"
  price_negotiable INTEGER DEFAULT 0,  -- 1 = price negotiable ("do negocjacji")
  price_arranged INTEGER DEFAULT 0,    -- 1 = "do uzgodnienia"
  state TEXT,                           -- "used" / "new" (from params)
  category_id INTEGER,                 -- OLX category ID (99=Elektronika, 1151=Oddam za darmo, etc.)
  category_type TEXT,                  -- "electronics", "goods", etc.
  city_id INTEGER,                     -- OLX city ID
  city_name TEXT,                       -- City display name
  city_normalized TEXT,                 -- Normalized city name (for matching)
  region_id INTEGER,                   -- OLX region ID
  region_name TEXT,                     -- Region display name
  lat REAL,                             -- GPS latitude (from map field)
  lon REAL,                             -- GPS longitude (from map field)
  map_radius REAL,                      -- Map accuracy radius in km
  user_id INTEGER,                     -- OLX user ID
  user_name TEXT,                       -- Seller display name
  user_business INTEGER DEFAULT 0,     -- 1 = business seller
  user_online INTEGER DEFAULT 0,       -- 1 = seller currently online
  user_last_seen TEXT,                  -- ISO timestamp of last seller activity
  has_phone INTEGER DEFAULT 0,         -- 1 = phone contact available
  has_chat INTEGER DEFAULT 0,          -- 1 = OLX chat available
  delivery_active INTEGER DEFAULT 0,   -- 1 = OLX delivery option available
  delivery_mode TEXT,                   -- Delivery mode e.g. "BuyWithDelivery"
  photo_count INTEGER DEFAULT 0,       -- Number of photos
  thumbnail_url TEXT,                   -- First photo CDN URL (template with {width}x{height})
  promotion_top INTEGER DEFAULT 0,     -- 1 = top ad promotion
  promotion_urgent INTEGER DEFAULT 0,  -- 1 = urgent promotion
  promotion_highlighted INTEGER DEFAULT 0, -- 1 = highlighted promotion
  status TEXT DEFAULT 'active',        -- "active" / "closed" / "removed"
  created_time TEXT,                    -- Offer creation ISO timestamp
  valid_to_time TEXT,                   -- Offer expiration ISO timestamp
  last_refresh_time TEXT,              -- Last refresh/pushup ISO timestamp
  first_seen_at TEXT NOT NULL,          -- When WE first scraped this offer
  last_seen_at TEXT NOT NULL,           -- When WE last saw this offer still active
  scan_batch_id TEXT,                   -- Which scrape batch captured this offer
  raw_params_json TEXT,                 -- Full params array as JSON (for unknown future params)
  raw_delivery_json TEXT,              -- Full delivery object as JSON
  CONSTRAINT olx_offer_unique UNIQUE (id)
);

-- ============================================================
-- 2. olx_offer_photos — individual photo records
-- ============================================================
CREATE TABLE IF NOT EXISTS olx_offer_photos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  offer_id INTEGER NOT NULL,           -- FK → olx_offers.id
  photo_id INTEGER,                    -- OLX photo ID
  cdn_url TEXT NOT NULL,               -- Photo CDN URL template
  width INTEGER,                       -- Original width
  height INTEGER,                      -- Original height
  rotation INTEGER DEFAULT 0,          -- Rotation in degrees
  sort_order INTEGER DEFAULT 0,        -- Photo order in listing
  FOREIGN KEY (offer_id) REFERENCES olx_offers(id) ON DELETE CASCADE
);

-- ============================================================
-- 3. olx_offer_tags — extracted keywords/tags from title+description
--    Enables semantic search: "ESP32", "Arduino", "rezystor", etc.
-- ============================================================
CREATE TABLE IF NOT EXISTS olx_offer_tags (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  offer_id INTEGER NOT NULL,           -- FK → olx_offers.id
  tag TEXT NOT NULL,                    -- Normalized lowercase tag
  tag_source TEXT NOT NULL DEFAULT 'title', -- 'title', 'description', 'params', 'auto'
  confidence REAL DEFAULT 1.0,          -- Extraction confidence (0-1)
  FOREIGN KEY (offer_id) REFERENCES olx_offers(id) ON DELETE CASCADE,
  CONSTRAINT olx_tag_unique UNIQUE (offer_id, tag, tag_source)
);

-- ============================================================
-- 4. olx_scan_batches — track each scraping session
-- ============================================================
CREATE TABLE IF NOT EXISTS olx_scan_batches (
  id TEXT PRIMARY KEY,                 -- Batch ID (UUID or timestamp-based)
  started_at TEXT NOT NULL,            -- When the scan started
  finished_at TEXT,                    -- When the scan completed
  status TEXT NOT NULL DEFAULT 'running', -- 'running' / 'completed' / 'failed'
  category_id INTEGER,                 -- Which category was scanned
  city_id INTEGER,                     -- Which city was the center
  distance_km INTEGER,                 -- Search radius
  total_available INTEGER,             -- total_elements from API metadata
  offers_scanned INTEGER DEFAULT 0,    -- How many offers we fetched
  offers_new INTEGER DEFAULT 0,        -- New offers not seen before
  offers_updated INTEGER DEFAULT 0,    -- Existing offers with changed data
  offers_expired INTEGER DEFAULT 0,    -- Offers gone since last scan
  error_message TEXT,                  -- If failed, why
  notebook_run_url TEXT,               -- Kaggle notebook run URL (if applicable)
  scraper_version TEXT DEFAULT '1.0'   -- Scraper version for tracking
);

-- ============================================================
-- 5. olx_price_history — track price changes over time
-- ============================================================
CREATE TABLE IF NOT EXISTS olx_price_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  offer_id INTEGER NOT NULL,           -- FK → olx_offers.id
  price_value INTEGER,                 -- Price at this point in time
  price_label TEXT,                    -- Human-readable price
  observed_at TEXT NOT NULL,           -- When we observed this price
  scan_batch_id TEXT,                  -- Which batch captured this
  FOREIGN KEY (offer_id) REFERENCES olx_offers(id) ON DELETE CASCADE
);

-- ============================================================
-- 6. olx_offer_parts_xref — cross-reference OLX offers with our recycled parts
--    Links market offers to known electronic components in our DB
-- ============================================================
CREATE TABLE IF NOT EXISTS olx_offer_parts_xref (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  offer_id INTEGER NOT NULL,           -- FK → olx_offers.id
  master_part_id INTEGER,              -- FK → recycled_part_master.id (nullable)
  matched_part_name TEXT,              -- What part name we matched
  match_method TEXT NOT NULL DEFAULT 'keyword', -- 'keyword', 'part_number', 'ai_classification'
  match_confidence REAL DEFAULT 0.5,   -- 0-1 confidence score
  created_at TEXT NOT NULL,
  FOREIGN KEY (offer_id) REFERENCES olx_offers(id) ON DELETE CASCADE,
  FOREIGN KEY (master_part_id) REFERENCES recycled_part_master(id) ON DELETE SET NULL,
  CONSTRAINT olx_xref_unique UNIQUE (offer_id, master_part_id, match_method)
);

-- ============================================================
-- INDEXES
-- ============================================================

-- Fast lookups by category + city
CREATE INDEX IF NOT EXISTS idx_olx_offers_category_city
  ON olx_offers(category_id, city_id);

-- Fast lookups by price range
CREATE INDEX IF NOT EXISTS idx_olx_offers_price
  ON olx_offers(price_value, category_id);

-- Find offers by region
CREATE INDEX IF NOT EXISTS idx_olx_offers_region
  ON olx_offers(region_id, category_id);

-- Find offers by status (active/closed)
CREATE INDEX IF NOT EXISTS idx_olx_offers_status
  ON olx_offers(status, last_seen_at);

-- Find offers by user (track seller behavior)
CREATE INDEX IF NOT EXISTS idx_olx_offers_user
  ON olx_offers(user_id);

-- Full-text search on title and description
CREATE INDEX IF NOT EXISTS idx_olx_offers_title
  ON olx_offers(title);

-- Time-based queries (newest first, expiring soon)
CREATE INDEX IF NOT EXISTS idx_olx_offers_created
  ON olx_offers(created_time DESC);

CREATE INDEX IF NOT EXISTS idx_olx_offers_valid_to
  ON olx_offers(valid_to_time);

-- Tag lookups (reverse: find all offers with a given tag)
CREATE INDEX IF NOT EXISTS idx_olx_offer_tags_tag
  ON olx_offer_tags(tag, confidence DESC);

-- Price history per offer
CREATE INDEX IF NOT EXISTS idx_olx_price_history_offer
  ON olx_price_history(offer_id, observed_at DESC);

-- Cross-reference lookups: find market offers for a known part
CREATE INDEX IF NOT EXISTS idx_olx_xref_master_part
  ON olx_offer_parts_xref(master_part_id);

-- Cross-reference: find parts mentioned in an offer
CREATE INDEX IF NOT EXISTS idx_olx_xref_offer
  ON olx_offer_parts_xref(offer_id);

-- Scan batch status tracking
CREATE INDEX IF NOT EXISTS idx_olx_scan_batches_status
  ON olx_scan_batches(status, started_at DESC);

-- Photo lookups
CREATE INDEX IF NOT EXISTS idx_olx_offer_photos_offer
  ON olx_offer_photos(offer_id, sort_order);
