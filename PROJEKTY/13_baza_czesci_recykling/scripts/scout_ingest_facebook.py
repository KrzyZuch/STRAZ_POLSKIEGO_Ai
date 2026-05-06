#!/usr/bin/env python3
"""Facebook Groups → Scout bridge: normalizer from FB Graph API JSONL / text dumps to scout schema JSONL.

Reads Facebook group data from two possible sources:
1. JSONL export (from FB Graph API / web scraper)
2. Text dump (copy-paste from Facebook groups, heuristic parsing)

Normalizes to the unified scout schema used by scout_resource_signals.py:
id, title, description, price_value, price_currency, price_label,
city_name, region_name, lat, lon, source, created_time, olx_url

Usage:
python3 scout_ingest_facebook.py --jsonl <fb_export.jsonl> --output <scout_incoming.jsonl>
python3 scout_ingest_facebook.py --text <fb_text_dump.txt> --output <scout_incoming.jsonl>
python3 scout_ingest_facebook.py --auto --source-dir <scout_data/facebook/> --output <scout_incoming.jsonl>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

NOW_ISO = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
TODAY_STR = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

NON_RESOURCE_TITLE_PATTERNS = [
    "kocurek", "kot ", "koty ", "pies", "pieski", "szczeniaki",
    "adopcj", "do adopcji", "zwierza", "zwierzaka", "kotek",
    "szczeniak", "piesek", "królik", "chomik", "papuga",
    "rybki", "żółw", "gad", "kotka",
]

DEFAULT_LOCATION = {
    "city": "Kłodzko",
    "region": "dolnośląskie",
    "lat": 50.4346,
    "lon": 16.6614,
}

CITY_COORDS = {
    "kłodzko": {"lat": 50.4346, "lon": 16.6614, "region": "dolnośląskie"},
    "nowa ruda": {"lat": 50.5796, "lon": 16.5010, "region": "dolnośląskie"},
    "polanica-zdrój": {"lat": 50.4047, "lon": 16.5146, "region": "dolnośląskie"},
    "duszniki-zdrój": {"lat": 50.4078, "lon": 16.3869, "region": "dolnośląskie"},
    "bystrzyca kłodzka": {"lat": 50.3008, "lon": 16.6480, "region": "dolnośląskie"},
    "kudowa-zdrój": {"lat": 50.4406, "lon": 16.2404, "region": "dolnośląskie"},
    "złoty stok": {"lat": 50.4478, "lon": 16.8783, "region": "dolnośląskie"},
    "wrocław": {"lat": 51.1079, "lon": 17.0385, "region": "dolnośląskie"},
}

FREE_KEYWORDS = ["oddam za darmo", "oddam za free", "za darmo", "gratis", "do oddania", "oddam", "za free"]

DEMAND_KEYWORDS = ["szukam", "potrzebuje", "kupię", "poszukuję", "odkupię", "przyjmę", "zabiorę"]


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


def is_resource_offer(raw: dict[str, Any]) -> bool:
    title = (raw.get("title") or raw.get("message") or "").lower()
    desc = (raw.get("description") or raw.get("message") or "").lower()
    text = title + " " + desc
    for pattern in NON_RESOURCE_TITLE_PATTERNS:
        if pattern in text:
            return False
    return True


def _extract_price(raw: dict[str, Any]) -> tuple[int | None, str, str]:
    for key in ("price_value", "price"):
        val = raw.get(key)
        if val is not None:
            try:
                pv = int(val)
                label = raw.get("price_label") or raw.get("price_text") or f"{pv} zł"
                return pv, "PLN", label
            except (ValueError, TypeError):
                pass
    label = raw.get("price_label") or raw.get("price_text") or ""
    if label:
        m = re.search(r"(\d+)", label)
        if m:
            return int(m.group(1)), "PLN", label
    return None, "PLN", ""


def _resolve_city(raw: dict[str, Any]) -> tuple[str, str, float | None, float | None]:
    city = raw.get("city_name") or raw.get("city") or ""
    region = raw.get("region_name") or raw.get("region") or ""
    lat = raw.get("lat")
    lon = raw.get("lon")

    if lat is not None and lon is not None:
        try:
            return city or DEFAULT_LOCATION["city"], region or DEFAULT_LOCATION["region"], float(lat), float(lon)
        except (ValueError, TypeError):
            pass

    if city:
        key = city.lower().strip()
        if key in CITY_COORDS:
            coords = CITY_COORDS[key]
            return city, region or coords["region"], coords["lat"], coords["lon"]

    return city or DEFAULT_LOCATION["city"], region or DEFAULT_LOCATION["region"], DEFAULT_LOCATION["lat"], DEFAULT_LOCATION["lon"]


def normalize_fb_jsonl_record(raw: dict[str, Any], seq: int = 0) -> dict[str, Any]:
    raw_id = raw.get("id", "")
    if not raw_id:
        raw_id = f"fb-{hashlib.md5((raw.get('title','') + raw.get('message','')).encode()).hexdigest()[:12]}"

    if not raw_id.startswith("fb-"):
        raw_id = f"fb-{raw_id}"

    title = (raw.get("title") or "").strip()
    description = (raw.get("message") or raw.get("description") or "").strip()
    price_value, price_currency, price_label = _extract_price(raw)
    city_name, region_name, lat, lon = _resolve_city(raw)

    return {
        "id": raw_id,
        "title": title,
        "description": description,
        "price_value": price_value,
        "price_currency": price_currency,
        "price_label": price_label,
        "city_name": city_name,
        "region_name": region_name,
        "lat": lat,
        "lon": lon,
        "source": "facebook_group",
        "source_detail": raw.get("group_name", ""),
        "contact_method": raw.get("contact_method") or raw.get("contact", ""),
        "contact_note": raw.get("contact_note", ""),
        "status": "active",
        "created_time": raw.get("created_time", "")[:10] if raw.get("created_time") else "",
        "olx_url": "",
        "ingested_at": NOW_ISO,
    }


def parse_text_dump(text_path: Path) -> list[dict[str, Any]]:
    with open(text_path, encoding="utf-8") as f:
        content = f.read()

    blocks = re.split(r"\n---\n", content)
    posts: list[dict[str, Any]] = []
    current_group = ""

    group_match = re.search(r"Grupa:\s*(.+)", content)
    if group_match:
        current_group = group_match.group(1).strip()

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        lines = [l.strip() for l in block.split("\n") if l.strip()]

        if not lines:
            continue

        if lines[0].startswith("Grupa:"):
            current_group = lines[0].replace("Grupa:", "").strip()
            lines = lines[1:]
            if not lines:
                continue

        title = lines[0] if lines else ""
        description = " ".join(lines[1:]) if len(lines) > 1 else ""

        if not title:
            continue

        price_value = None
        price_label = ""
        price_match = re.search(r"(\d+)\s*z[łl]", title + " " + description)
        if price_match:
            price_value = int(price_match.group(1))
            price_label = f"{price_value} zł"

        is_free = any(kw in title.lower() or kw in description.lower() for kw in FREE_KEYWORDS)
        if is_free and price_value is None:
            price_value = 0
            price_label = "Za darmo"

        city_name = DEFAULT_LOCATION["city"]
        region_name = DEFAULT_LOCATION["region"]
        lat = DEFAULT_LOCATION["lat"]
        lon = DEFAULT_LOCATION["lon"]

        for city_key, coords in CITY_COORDS.items():
            if city_key in (title + " " + description).lower():
                city_name = city_key.title()
                region_name = coords["region"]
                lat = coords["lat"]
                lon = coords["lon"]
                break

        contact = "comment"
        if "priv" in (title + " " + description).lower() or "pm" in (title + " " + description).lower():
            contact = "facebook_pm"
        elif "tel" in (title + " " + description).lower():
            contact = "phone"

        post_id = f"fb-txt-{hashlib.md5(title.encode()).hexdigest()[:8]}"

        posts.append({
            "id": post_id,
            "title": title.strip(),
            "description": description.strip(),
            "price_value": price_value,
            "price_label": price_label,
            "city_name": city_name,
            "region_name": region_name,
            "lat": lat,
            "lon": lon,
            "source": "facebook_group",
            "source_detail": current_group,
            "contact_method": contact,
            "contact_note": "",
            "status": "active",
            "created_time": "",
            "olx_url": "",
            "ingested_at": NOW_ISO,
        })

    return posts


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


def compute_stats(records: list[dict[str, Any]]) -> dict[str, Any]:
    cities: dict[str, int] = {}
    free_count = 0
    demand_count = 0
    has_gps = 0
    for r in records:
        city = r.get("city_name") or "?"
        cities[city] = cities.get(city, 0) + 1
        if r.get("price_value") == 0 or "za darmo" in (r.get("price_label") or "").lower():
            free_count += 1
        text = (r.get("title", "") + " " + r.get("description", "")).lower()
        if any(kw in text for kw in DEMAND_KEYWORDS):
            demand_count += 1
        if r.get("lat") is not None and r.get("lon") is not None:
            has_gps += 1
    return {
        "total": len(records),
        "free": free_count,
        "demand": demand_count,
        "supply": len(records) - demand_count,
        "paid_or_empty": len(records) - free_count,
        "has_gps": has_gps,
        "cities": dict(sorted(cities.items(), key=lambda x: -x[1])),
    }


def print_stats(stats: dict[str, Any]) -> None:
    print(f" Darmo: {stats['free']}, Platne/puste: {stats['paid_or_empty']}")
    print(f" Popyt: {stats['demand']}, Podaż: {stats['supply']}")
    print(f" Z GPS: {stats['has_gps']}/{stats['total']}")
    print(f" Miasta: {stats['cities']}")


def ingest_jsonl(jsonl_path: Path, output: Path, *, filter_non_resource: bool = True) -> dict[str, Any]:
    print(f"[scout_ingest_facebook] JSONL export: {jsonl_path}")
    raw_records = read_jsonl(jsonl_path)
    print(f" Rekordow w JSONL: {len(raw_records)}")

    if filter_non_resource:
        before = len(raw_records)
        raw_records = [r for r in raw_records if is_resource_offer(r)]
        filtered = before - len(raw_records)
        if filtered:
            print(f" Odfiltrowano non-resource: {filtered} (zwierzeta, adopcje)")

    normalized = [normalize_fb_jsonl_record(r, i) for i, r in enumerate(raw_records)]

    errors_all: list[str] = []
    valid = []
    for i, rec in enumerate(normalized):
        errs = validate_scout_record(rec)
        if errs:
            errors_all.append(f" [{i}] {rec.get('id', '?')}: {', '.join(errs)}")
        else:
            valid.append(rec)

    if errors_all:
        print(f" Bledy walidacji ({len(errors_all)}):")
        for e in errors_all[:10]:
            print(e)

    stats = compute_stats(valid)
    print(f" Znormalizowano: {len(valid)}")
    print_stats(stats)

    write_jsonl(valid, output)
    print(f" Zapisano: {output}")

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


def ingest_text(text_path: Path, output: Path, *, filter_non_resource: bool = True) -> dict[str, Any]:
    print(f"[scout_ingest_facebook] Text dump: {text_path}")
    raw_posts = parse_text_dump(text_path)
    print(f" Postow w text dump: {len(raw_posts)}")

    if filter_non_resource:
        before = len(raw_posts)
        raw_posts = [r for r in raw_posts if is_resource_offer(r)]
        filtered = before - len(raw_posts)
        if filtered:
            print(f" Odfiltrowano non-resource: {filtered}")

    errors_all: list[str] = []
    valid = []
    for i, rec in enumerate(raw_posts):
        errs = validate_scout_record(rec)
        if errs:
            errors_all.append(f" [{i}] {rec.get('id', '?')}: {', '.join(errs)}")
        else:
            valid.append(rec)

    if errors_all:
        print(f" Bledy walidacji ({len(errors_all)}):")
        for e in errors_all[:10]:
            print(e)

    stats = compute_stats(valid)
    print(f" Znormalizowano: {len(valid)}")
    print_stats(stats)

    write_jsonl(valid, output)
    print(f" Zapisano: {output}")

    return {
        "source_type": "text",
        "source_path": str(text_path),
        "raw_count": len(raw_posts),
        "valid_count": len(valid),
        "errors": len(errors_all),
        "stats": stats,
        "output_path": str(output),
        "ingested_at": NOW_ISO,
    }


def ingest_auto(source_dir: Path, output: Path, *, filter_non_resource: bool = True) -> dict[str, Any]:
    print(f"[scout_ingest_facebook] Auto-detect sources in: {source_dir}")

    all_normalized: list[dict[str, Any]] = []
    ingest_log: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    jsonl_files = sorted(source_dir.glob("*.jsonl"))
    for jsonl_path in jsonl_files:
        print(f" Found JSONL: {jsonl_path.name}")
        raw = read_jsonl(jsonl_path)
        if filter_non_resource:
            raw = [r for r in raw if is_resource_offer(r)]
        normalized = [normalize_fb_jsonl_record(r, i) for i, r in enumerate(raw)]
        valid = [r for r in normalized if not validate_scout_record(r)]
        before = len(all_normalized)
        for rec in valid:
            rid = rec.get("id", "")
            if rid and rid not in seen_ids:
                seen_ids.add(rid)
                all_normalized.append(rec)
        added = len(all_normalized) - before
        print(f" {len(raw)} raw → {added} new (deduped)")
        ingest_log.append({
            "source": str(jsonl_path),
            "type": "jsonl",
            "raw": len(raw),
            "valid": added,
        })

    text_files = sorted(source_dir.glob("*.txt"))
    for text_path in text_files:
        print(f" Found text: {text_path.name}")
        raw_posts = parse_text_dump(text_path)
        if filter_non_resource:
            raw_posts = [r for r in raw_posts if is_resource_offer(r)]
        before = len(all_normalized)
        for rec in raw_posts:
            rid = rec.get("id", "")
            if rid and rid not in seen_ids:
                if validate_scout_record(rec):
                    continue
                seen_ids.add(rid)
                all_normalized.append(rec)
        added = len(all_normalized) - before
        print(f" {len(raw_posts)} raw → {added} new (deduped)")
        ingest_log.append({
            "source": str(text_path),
            "type": "text",
            "raw": len(raw_posts),
            "valid": added,
        })

    stats = compute_stats(all_normalized)
    print(f" Laczone: {len(all_normalized)} scout records z {len(ingest_log)} zrodel")
    print_stats(stats)

    write_jsonl(all_normalized, output)
    print(f" Zapisano: {output}")

    return {
        "source_type": "auto",
        "source_dir": str(source_dir),
        "sources_processed": len(ingest_log),
        "source_details": ingest_log,
        "total_raw": sum(s["raw"] for s in ingest_log),
        "total_valid": len(all_normalized),
        "stats": stats,
        "output_path": str(output),
        "ingested_at": NOW_ISO,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Facebook Groups → Scout bridge: normalize FB JSONL/text to scout schema JSONL",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--jsonl", type=Path, help="Path to FB JSONL export (Graph API / scraper)")
    group.add_argument("--text", type=Path, help="Path to FB text dump (copy-paste)")
    group.add_argument("--auto", action="store_true", help="Auto-detect JSONL and text in source-dir")

    parser.add_argument("--source-dir", type=Path, help="Directory for --auto mode")
    parser.add_argument("--output", type=Path, required=True, help="Output scout JSONL path")
    parser.add_argument("--no-filter", action="store_true", help="Disable non-resource filtering (keep animals etc.)")

    args = parser.parse_args()
    filter_non_resource = not args.no_filter

    if args.auto:
        if not args.source_dir:
            parser.error("--auto requires --source-dir")
        result = ingest_auto(args.source_dir, args.output, filter_non_resource=filter_non_resource)
    elif args.jsonl:
        result = ingest_jsonl(args.jsonl, args.output, filter_non_resource=filter_non_resource)
    elif args.text:
        result = ingest_text(args.text, args.output, filter_non_resource=filter_non_resource)
    else:
        parser.print_help()
        sys.exit(1)

    receipt_path = Path(args.output).parent / f"ingest_receipt_fb_59_{TODAY_STR}.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    with open(receipt_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Receipt: {receipt_path}")


if __name__ == "__main__":
    main()
