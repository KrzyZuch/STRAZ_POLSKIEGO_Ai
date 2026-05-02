#!/usr/bin/env python3
"""OLX → Scout bridge: normalizer from OLX SQL dumps and JSONL exports to scout schema JSONL.

Reads OLX data from two possible sources:
1. SQL dump with INSERT statements (from D1 import / manual export)
2. JSONL export (from Kaggle notebook olx-oddam-za-darmo-scraper.ipynb)

Normalizes to the unified scout schema used by scout_resource_signals.py:
  id, title, description, price_value, price_currency, price_label,
  city_name, region_name, lat, lon, source, created_time, olx_url

Usage:
  python3 scout_ingest_olx.py --sql <file.sql> --output <scout_incoming.jsonl>
  python3 scout_ingest_olx.py --jsonl <export.jsonl> --output <scout_incoming.jsonl>
  python3 scout_ingest_olx.py --auto --source-dir <olx_data/> --output <scout_incoming.jsonl>
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

NOW_ISO = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
TODAY_STR = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

OLX_SQL_TABLE_SCHEMA = """CREATE TABLE IF NOT EXISTS olx_offers (
    id INTEGER PRIMARY KEY, olx_url TEXT NOT NULL, title TEXT NOT NULL,
    description TEXT, price_value INTEGER, price_currency TEXT DEFAULT 'PLN',
    price_label TEXT, price_negotiable INTEGER DEFAULT 0, price_arranged INTEGER DEFAULT 0,
    state TEXT, category_id INTEGER, category_type TEXT,
    city_id INTEGER, city_name TEXT, city_normalized TEXT,
    region_id INTEGER, region_name TEXT,
    lat REAL, lon REAL, map_radius REAL,
    user_id INTEGER, user_name TEXT, user_business INTEGER DEFAULT 0,
    user_online INTEGER DEFAULT 0, user_last_seen TEXT,
    has_phone INTEGER DEFAULT 0, has_chat INTEGER DEFAULT 0,
    delivery_active INTEGER DEFAULT 0, delivery_mode TEXT,
    photo_count INTEGER DEFAULT 0, thumbnail_url TEXT,
    promotion_top INTEGER DEFAULT 0, promotion_urgent INTEGER DEFAULT 0,
    promotion_highlighted INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active', created_time TEXT, valid_to_time TEXT,
    last_refresh_time TEXT, first_seen_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL, scan_batch_id TEXT,
    raw_params_json TEXT, raw_delivery_json TEXT)"""

OLX_SQL_PHOTOS_SCHEMA = """CREATE TABLE IF NOT EXISTS olx_offer_photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT, offer_id INTEGER NOT NULL,
    photo_id INTEGER, cdn_url TEXT NOT NULL,
    width INTEGER, height INTEGER, rotation INTEGER DEFAULT 0,
    sort_order INTEGER DEFAULT 0,
    FOREIGN KEY (offer_id) REFERENCES olx_offers(id) ON DELETE CASCADE)"""

SCOUT_REQUIRED_FIELDS = [
    "id", "title", "description", "price_value", "price_currency",
    "price_label", "city_name", "region_name", "lat", "lon",
    "source", "created_time", "olx_url",
]

NON_RESOURCE_CATEGORY_IDS = {
    1884, 1888,
}

NON_RESOURCE_CATEGORY_TYPES = set()

NON_RESOURCE_TITLE_PATTERNS = [
    "kocurek", "kot ", "koty ", "pies", "pieski", "szczeniaki",
    "adopcj", "do adopcji",
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def write_jsonl(records: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def parse_olx_sql_inserts(sql_path: Path) -> list[dict[str, Any]]:
    db = sqlite3.connect(":memory:")
    db.execute("PRAGMA journal_mode=WAL")
    db.execute(OLX_SQL_TABLE_SCHEMA)
    db.execute(OLX_SQL_PHOTOS_SCHEMA)

    with open(sql_path, encoding="utf-8") as f:
        sql_text = f.read()

    statements = []
    for line in sql_text.split("\n"):
        stripped = line.strip()
        if stripped.upper().startswith("INSERT"):
            statements.append(stripped)

    if not statements:
        db.close()
        return []

    for stmt in statements:
        try:
            db.execute(stmt)
        except sqlite3.Error:
            pass
    db.commit()

    rows = db.execute("SELECT * FROM olx_offers").fetchall()
    cols = [d[0] for d in db.execute("SELECT * FROM olx_offers LIMIT 0").description]
    db.close()
    return [dict(zip(cols, row)) for row in rows]


def is_resource_offer(raw: dict[str, Any]) -> bool:
    cat_id = raw.get("category_id")
    if cat_id in NON_RESOURCE_CATEGORY_IDS:
        return False

    title = (raw.get("title") or "").lower()
    for pattern in NON_RESOURCE_TITLE_PATTERNS:
        if pattern in title:
            return False

    return True


def normalize_olx_record(raw: dict[str, Any]) -> dict[str, Any]:
    desc = (raw.get("description") or "").replace("<br />", " ").replace("<br/>", " ").replace("<br>", " ")
    desc = " ".join(desc.split())

    price_value = raw.get("price_value")
    if price_value is not None:
        try:
            price_value = int(price_value)
        except (ValueError, TypeError):
            price_value = None

    lat = raw.get("lat")
    lon = raw.get("lon")
    if lat is not None:
        try:
            lat = float(lat)
        except (ValueError, TypeError):
            lat = None
    if lon is not None:
        try:
            lon = float(lon)
        except (ValueError, TypeError):
            lon = None

    return {
        "id": f"olx-{raw.get('id', 'unknown')}",
        "title": (raw.get("title") or "").strip(),
        "description": desc.strip(),
        "price_value": price_value,
        "price_currency": raw.get("price_currency", "PLN"),
        "price_label": raw.get("price_label", ""),
        "price_negotiable": raw.get("price_negotiable", 0),
        "state": raw.get("state", ""),
        "category_id": raw.get("category_id"),
        "category_type": raw.get("category_type", ""),
        "city_name": raw.get("city_name", ""),
        "city_normalized": raw.get("city_normalized", ""),
        "region_name": raw.get("region_name", ""),
        "lat": lat,
        "lon": lon,
        "user_name": raw.get("user_name", ""),
        "user_business": raw.get("user_business", 0),
        "has_phone": raw.get("has_phone", 0),
        "has_chat": raw.get("has_chat", 0),
        "photo_count": raw.get("photo_count", 0),
        "status": raw.get("status", "active"),
        "created_time": raw.get("created_time", ""),
        "olx_url": raw.get("olx_url", ""),
        "source": "olx",
        "ingested_at": NOW_ISO,
    }


def validate_scout_record(rec: dict[str, Any]) -> list[str]:
    errors = []
    if not rec.get("id"):
        errors.append("missing id")
    if not rec.get("title"):
        errors.append("missing title")
    if rec.get("price_value") is not None:
        try:
            float(rec["price_value"])
        except (ValueError, TypeError):
            errors.append(f"invalid price_value: {rec['price_value']}")
    return errors


def normalize_jsonl_record(raw: dict[str, Any]) -> dict[str, Any]:
    mapping = {
        "id": "id",
        "olx_url": "olx_url",
        "title": "title",
        "description": "description",
        "price_value": "price_value",
        "price_currency": "price_currency",
        "price_label": "price_label",
        "price_negotiable": "price_negotiable",
        "state": "state",
        "category_id": "category_id",
        "category_type": "category_type",
        "city_name": "city_name",
        "city_normalized": "city_normalized",
        "region_name": "region_name",
        "lat": "lat",
        "lon": "lon",
        "user_name": "user_name",
        "user_business": "user_business",
        "has_phone": "has_phone",
        "has_chat": "has_chat",
        "photo_count": "photo_count",
        "status": "status",
        "created_time": "created_time",
    }
    mapped: dict[str, Any] = {}
    for src_key, dst_key in mapping.items():
        if src_key in raw:
            mapped[dst_key] = raw[src_key]

    mapped.setdefault("price_currency", "PLN")
    mapped.setdefault("source", "olx")
    mapped.setdefault("status", "active")
    mapped["ingested_at"] = NOW_ISO

    if "id" in mapped and not str(mapped["id"]).startswith("olx-"):
        mapped["id"] = f"olx-{mapped['id']}"

    desc = (mapped.get("description") or "").replace("<br />", " ").replace("<br/>", " ").replace("<br>", " ")
    mapped["description"] = " ".join(desc.split())

    if mapped.get("price_value") is not None:
        try:
            mapped["price_value"] = int(mapped["price_value"])
        except (ValueError, TypeError):
            mapped["price_value"] = None

    for coord in ("lat", "lon"):
        if mapped.get(coord) is not None:
            try:
                mapped[coord] = float(mapped[coord])
            except (ValueError, TypeError):
                mapped[coord] = None

    return mapped


def ingest_sql(sql_path: Path, output: Path, *, filter_non_resource: bool = True) -> dict[str, Any]:
    print(f"[scout_ingest_olx] SQL dump: {sql_path}")
    raw_records = parse_olx_sql_inserts(sql_path)
    print(f"  Rekordow w SQL: {len(raw_records)}")

    if filter_non_resource:
        before = len(raw_records)
        raw_records = [r for r in raw_records if is_resource_offer(r)]
        filtered = before - len(raw_records)
        if filtered:
            print(f"  Odfiltrowano non-resource: {filtered} (zwierzeta, adopcje)")

    normalized = [normalize_olx_record(r) for r in raw_records]

    errors_all: list[str] = []
    valid = []
    for i, rec in enumerate(normalized):
        errs = validate_scout_record(rec)
        if errs:
            errors_all.append(f"  [{i}] {rec.get('id', '?')}: {', '.join(errs)}")
        else:
            valid.append(rec)

    if errors_all:
        print(f"  Bledy walidacji ({len(errors_all)}):")
        for e in errors_all[:10]:
            print(e)

    stats = compute_stats(valid)
    print(f"  Znormalizowano: {len(valid)}")
    print_stats(stats)

    write_jsonl(valid, output)
    print(f"  Zapisano: {output}")

    return {
        "source_type": "sql",
        "source_path": str(sql_path),
        "raw_count": len(raw_records) + (len(errors_all) if errors_all else 0),
        "valid_count": len(valid),
        "errors": len(errors_all),
        "stats": stats,
        "output_path": str(output),
        "ingested_at": NOW_ISO,
    }


def ingest_jsonl(jsonl_path: Path, output: Path, *, filter_non_resource: bool = True) -> dict[str, Any]:
    print(f"[scout_ingest_olx] JSONL export: {jsonl_path}")
    raw_records = read_jsonl(jsonl_path)
    print(f"  Rekordow w JSONL: {len(raw_records)}")

    if filter_non_resource:
        before = len(raw_records)
        raw_records = [r for r in raw_records if is_resource_offer(r)]
        filtered = before - len(raw_records)
        if filtered:
            print(f"  Odfiltrowano non-resource: {filtered}")

    normalized = [normalize_jsonl_record(r) for r in raw_records]

    errors_all: list[str] = []
    valid = []
    for i, rec in enumerate(normalized):
        errs = validate_scout_record(rec)
        if errs:
            errors_all.append(f"  [{i}] {rec.get('id', '?')}: {', '.join(errs)}")
        else:
            valid.append(rec)

    if errors_all:
        print(f"  Bledy walidacji ({len(errors_all)}):")
        for e in errors_all[:10]:
            print(e)

    stats = compute_stats(valid)
    print(f"  Znormalizowano: {len(valid)}")
    print_stats(stats)

    write_jsonl(valid, output)
    print(f"  Zapisano: {output}")

    return {
        "source_type": "jsonl",
        "source_path": str(jsonl_path),
        "raw_count": len(raw_records),
        "valid_count": len(valid),
        "errors": len(errors_all),
        "stats": stats,
        "output_path": str(output),
        "ingested_at": NOW_ISO,
    }


def ingest_auto(source_dir: Path, output: Path) -> dict[str, Any]:
    print(f"[scout_ingest_olx] Auto-detect sources in: {source_dir}")

    all_normalized: list[dict[str, Any]] = []
    ingest_log: list[dict[str, Any]] = []

    sql_files = sorted(source_dir.glob("*.sql"))
    jsonl_files = sorted(source_dir.glob("*.jsonl"))

    for sql_path in sql_files:
        print(f"  Found SQL: {sql_path.name}")
        raw = parse_olx_sql_inserts(sql_path)
        filtered = [r for r in raw if is_resource_offer(r)]
        normalized = [normalize_olx_record(r) for r in filtered]
        valid = [r for r in normalized if not validate_scout_record(r)]
        print(f"    {len(raw)} raw → {len(valid)} valid scout records")
        all_normalized.extend(valid)
        ingest_log.append({
            "source": str(sql_path),
            "type": "sql",
            "raw": len(raw),
            "valid": len(valid),
        })

    for jsonl_path in jsonl_files:
        print(f"  Found JSONL: {jsonl_path.name}")
        raw = read_jsonl(jsonl_path)
        filtered = [r for r in raw if is_resource_offer(r)]
        normalized = [normalize_jsonl_record(r) for r in filtered]
        valid = [r for r in normalized if not validate_scout_record(r)]
        print(f"    {len(raw)} raw → {len(valid)} valid scout records")
        all_normalized.extend(valid)
        ingest_log.append({
            "source": str(jsonl_path),
            "type": "jsonl",
            "raw": len(raw),
            "valid": len(valid),
        })

    seen_ids: set[str] = set()
    deduped = []
    for rec in all_normalized:
        rid = rec.get("id", "")
        if rid in seen_ids:
            continue
        seen_ids.add(rid)
        deduped.append(rec)

    dupes = len(all_normalized) - len(deduped)
    if dupes:
        print(f"  Deduplikacja: {dupes} duplikatow usunietych")

    stats = compute_stats(deduped)
    print(f"  Laczone: {len(deduped)} scout records z {len(ingest_log)} zrodel")
    print_stats(stats)

    write_jsonl(deduped, output)
    print(f"  Zapisano: {output}")

    return {
        "source_type": "auto",
        "source_dir": str(source_dir),
        "sources_processed": len(ingest_log),
        "source_details": ingest_log,
        "total_raw": sum(s["raw"] for s in ingest_log),
        "total_valid": len(deduped),
        "duplicates_removed": dupes,
        "stats": stats,
        "output_path": str(output),
        "ingested_at": NOW_ISO,
    }


def compute_stats(records: list[dict[str, Any]]) -> dict[str, Any]:
    cities: dict[str, int] = {}
    free_count = 0
    has_gps = 0
    for r in records:
        city = r.get("city_name") or "?"
        cities[city] = cities.get(city, 0) + 1
        if r.get("price_value") == 0 or "za darmo" in (r.get("price_label") or "").lower():
            free_count += 1
        if r.get("lat") is not None and r.get("lon") is not None:
            has_gps += 1
    return {
        "total": len(records),
        "free": free_count,
        "paid_or_empty": len(records) - free_count,
        "has_gps": has_gps,
        "cities": dict(sorted(cities.items(), key=lambda x: -x[1])),
    }


def print_stats(stats: dict[str, Any]) -> None:
    print(f"  Darmo: {stats['free']}, Platne/puste: {stats['paid_or_empty']}")
    print(f"  Z GPS: {stats['has_gps']}/{stats['total']}")
    print(f"  Miasta: {stats['cities']}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="OLX → Scout bridge: normalize OLX SQL/JSONL to scout schema JSONL",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--sql", type=Path, help="Path to OLX SQL dump")
    group.add_argument("--jsonl", type=Path, help="Path to OLX JSONL export")
    group.add_argument("--auto", action="store_true", help="Auto-detect SQL and JSONL in source-dir")

    parser.add_argument("--source-dir", type=Path, help="Directory for --auto mode")
    parser.add_argument("--output", type=Path, required=True, help="Output scout JSONL path")
    parser.add_argument("--no-filter", action="store_true", help="Disable non-resource filtering (keep animals etc.)")

    args = parser.parse_args()
    filter_non_resource = not args.no_filter

    if args.auto:
        if not args.source_dir:
            parser.error("--auto requires --source-dir")
        result = ingest_auto(args.source_dir, args.output)
    elif args.sql:
        result = ingest_sql(args.sql, args.output, filter_non_resource=filter_non_resource)
    elif args.jsonl:
        result = ingest_jsonl(args.jsonl, args.output, filter_non_resource=filter_non_resource)
    else:
        parser.print_help()
        sys.exit(1)

    receipt_path = Path(args.output).parent / f"ingest_receipt_57_{TODAY_STR}.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    with open(receipt_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Receipt: {receipt_path}")


if __name__ == "__main__":
    main()
