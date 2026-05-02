#!/usr/bin/env python3
"""Facebook Groups -> Scout bridge: normalizer from Facebook group post exports to scout schema JSONL.

Reads Facebook group data from two possible sources:
1. JSONL export from FB Graph API / web scraper (structured posts)
2. Text dump from copy-paste of FB group posts (heuristic parsing)

Normalizes to the unified scout schema used by scout_resource_signals.py:
id, title, description, price_value, price_currency, price_label,
city_name, region_name, lat, lon, source, created_time, source_detail,
contact_method, contact_note

Usage:
python3 scout_ingest_facebook.py --jsonl <fb_export.jsonl> --output <scout_fb.jsonl>
python3 scout_ingest_facebook.py --text <fb_text_dump.txt> --output <scout_fb.jsonl>
python3 scout_ingest_facebook.py --auto --source-dir <fb_data/> --output <scout_fb.jsonl>
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

NOW_ISO = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
TODAY_STR = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

FB_JSONL_FIELD_MAP = {
    "id": "id",
    "post_id": "id",
    "message": "description",
    "title": "title",
    "name": "title",
    "price": "price_value",
    "price_value": "price_value",
    "price_text": "price_label",
    "price_label": "price_label",
    "location": "city_name",
    "city_name": "city_name",
    "city": "city_name",
    "region": "region_name",
    "region_name": "region_name",
    "lat": "lat",
    "latitude": "lat",
    "lon": "lon",
    "longitude": "lon",
    "group_name": "source_detail",
    "source_detail": "source_detail",
    "group": "source_detail",
    "created_time": "created_time",
    "created_at": "created_time",
    "timestamp": "created_time",
    "url": "url",
    "post_url": "url",
    "contact_method": "contact_method",
    "contact": "contact_method",
    "contact_note": "contact_note",
}

FB_TEXT_POST_SEPARATOR = re.compile(
    r"(?:^|\n)(?:-{3,}|={3,}|#+\s|\[POST\s|#\d{3,})",
)

FB_TEXT_PRICE_PATTERNS = [
    re.compile(r"(?i)(?:cena|za|sprzedam|koszt)\s*:?\s*(\d+)\s*z[lł]",),
    re.compile(r"(?i)(\d+)\s*z[lł]\b",),
    re.compile(r"(?i)za\s+darmo|gratis|za\s+free|oddam\s+za\s+free|oddam\s+za\s+darmo",),
]

FB_TEXT_FREE_PATTERNS = [
    re.compile(r"(?i)za\s+darmo|gratis|za\s+free|oddam\s+za\s+free|oddam\s+za\s+darmo|do\s+oddania|oddam\s+darmo"),
]

FB_TEXT_DEMAND_PATTERNS = [
    re.compile(r"(?i)szukam|potrzebuj[eę]|kupi[eę]|poszukuj[eę]|przygarn[eę]|zabior[eę]|szukam\s+tanio"),
]

NON_RESOURCE_TITLE_PATTERNS = [
    "kocurek", "kot ", "koty ", "pies", "pieski", "szczeniaki",
    "adopcj", "do adopcji", "zwierza", "zwierzaka", "kotek",
    "szczeniak", "piesek", "królik", "chomik", "papuga",
    "rybki", "żółw", "gad", "kotka",
]

POLISH_CITIES_WITH_COORDS: dict[str, dict[str, Any]] = {
    "kłodzko": {"lat": 50.4346, "lon": 16.6614, "region": "dolnośląskie"},
    "nowa ruda": {"lat": 50.5796, "lon": 16.5010, "region": "dolnośląskie"},
    "polanica-zdrój": {"lat": 50.4047, "lon": 16.5146, "region": "dolnośląskie"},
    "polanica zdrój": {"lat": 50.4047, "lon": 16.5146, "region": "dolnośląskie"},
    "duszniki-zdrój": {"lat": 50.4078, "lon": 16.3869, "region": "dolnośląskie"},
    "duszniki zdrój": {"lat": 50.4078, "lon": 16.3869, "region": "dolnośląskie"},
    "bystrzyca kłodzka": {"lat": 50.3008, "lon": 16.6480, "region": "dolnośląskie"},
    "kudowa-zdrój": {"lat": 50.4406, "lon": 16.2404, "region": "dolnośląskie"},
    "kudowa zdrój": {"lat": 50.4406, "lon": 16.2404, "region": "dolnośląskie"},
    "złoty stok": {"lat": 50.4478, "lon": 16.8783, "region": "dolnośląskie"},
    "lwówek śląski": {"lat": 51.1167, "lon": 15.6000, "region": "dolnośląskie"},
    "wrocław": {"lat": 51.1079, "lon": 17.0385, "region": "dolnośląskie"},
}


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
    title = (raw.get("title") or "").lower()
    desc = (raw.get("description") or "").lower()
    text = title + " " + desc
    for pattern in NON_RESOURCE_TITLE_PATTERNS:
        if pattern in text:
            return False
    return True


def _fb_id(raw: dict[str, Any], idx: int) -> str:
    raw_id = raw.get("id") or raw.get("post_id") or ""
    if raw_id:
        s = str(raw_id)
        if s.startswith("fb-"):
            return s
        return f"fb-{s}"
    return f"fb-{idx:05d}"


def _parse_price_value(raw: dict[str, Any]) -> tuple[int | None, str]:
    pv = raw.get("price_value") or raw.get("price")
    if pv is not None:
        try:
            v = int(float(str(pv).replace(",", ".")))
            label = raw.get("price_label") or raw.get("price_text") or ""
            if v == 0 and not label:
                label = "Za darmo"
            elif v > 0 and not label:
                label = f"{v} zł"
            return v, label
        except (ValueError, TypeError):
            pass
    label = raw.get("price_label") or raw.get("price_text") or ""
    if not label:
        desc = (raw.get("description") or "") + " " + (raw.get("title") or "")
        for pat in FB_TEXT_FREE_PATTERNS:
            if pat.search(desc):
                return 0, "Za darmo"
    return None, label


def _resolve_location(raw: dict[str, Any]) -> dict[str, Any]:
    city = raw.get("city_name") or raw.get("city") or raw.get("location") or ""
    region = raw.get("region_name") or raw.get("region") or ""
    lat = raw.get("lat") or raw.get("latitude")
    lon = raw.get("lon") or raw.get("longitude")
    if lat is not None and lon is not None:
        try:
            lat = float(lat)
            lon = float(lon)
        except (ValueError, TypeError):
            lat = None
            lon = None
    if lat is None and city:
        city_key = city.lower().strip()
        if city_key in POLISH_CITIES_WITH_COORDS:
            coords = POLISH_CITIES_WITH_COORDS[city_key]
            lat = coords["lat"]
            lon = coords["lon"]
            if not region:
                region = coords["region"]
    if not region:
        region = "dolnośląskie"
    return {"city_name": city, "region_name": region, "lat": lat, "lon": lon}


def normalize_fb_jsonl_record(raw: dict[str, Any], idx: int) -> dict[str, Any]:
    mapped: dict[str, Any] = {}
    for src_key, dst_key in FB_JSONL_FIELD_MAP.items():
        if src_key in raw:
            if dst_key not in mapped or raw[src_key] is not None:
                mapped[dst_key] = raw[src_key]

    if "title" not in mapped or not mapped["title"]:
        desc = mapped.get("description") or mapped.get("message") or ""
        first_line = desc.split("\n")[0].strip() if desc else ""
        mapped["title"] = first_line[:120] if first_line else f"FB post {idx}"

    sig_id = _fb_id(raw, idx)
    price_value, price_label = _parse_price_value(mapped)
    loc = _resolve_location(mapped)

    description = (mapped.get("description") or "").replace("<br />", " ").replace("<br/>", " ").replace("<br>", " ")
    description = " ".join(description.split())

    return {
        "id": sig_id,
        "title": (mapped.get("title") or "").strip()[:200],
        "description": description.strip()[:2000],
        "price_value": price_value,
        "price_currency": mapped.get("price_currency", "PLN"),
        "price_label": price_label,
        "city_name": loc["city_name"],
        "region_name": loc["region_name"],
        "lat": loc["lat"],
        "lon": loc["lon"],
        "source": "facebook_group",
        "source_detail": mapped.get("source_detail") or mapped.get("group_name") or "",
        "contact_method": mapped.get("contact_method") or "facebook_pm",
        "contact_note": mapped.get("contact_note") or "",
        "url": mapped.get("url") or mapped.get("post_url") or "",
        "status": "active",
        "created_time": mapped.get("created_time") or NOW_ISO[:10],
        "ingested_at": NOW_ISO,
    }


def parse_text_dump(text_path: Path) -> list[dict[str, Any]]:
    with open(text_path, encoding="utf-8") as f:
        content = f.read()

    chunks = FB_TEXT_POST_SEPARATOR.split(content)
    if len(chunks) <= 1:
        blocks = re.split(r"\n{2,}", content)
    else:
        blocks = []
        for chunk in chunks:
            chunk = chunk.strip()
            if len(chunk) > 20:
                blocks.append(chunk)

    posts: list[dict[str, Any]] = []
    for i, block in enumerate(blocks):
        block = block.strip()
        if len(block) < 15:
            continue
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if not lines:
            continue
        title = lines[0][:200]
        desc = " ".join(lines[1:])[:2000] if len(lines) > 1 else ""
        price_value = None
        price_label = ""
        city_name = ""
        for pat in FB_TEXT_FREE_PATTERNS:
            if pat.search(block):
                price_value = 0
                price_label = "Za darmo"
                break
        if price_value is None:
            for pat in FB_TEXT_PRICE_PATTERNS:
                m = pat.search(block)
                if m and pat is not FB_TEXT_FREE_PATTERNS[0]:
                    try:
                        price_value = int(m.group(1))
                        price_label = f"{price_value} zł"
                    except (ValueError, IndexError):
                        pass
                    break
        for city_key, coords in POLISH_CITIES_WITH_COORDS.items():
            if city_key in block.lower():
                city_name = city_key.title()
                break
        posts.append({
            "id": f"fb-txt-{i+1:05d}",
            "title": title,
            "description": desc,
            "price_value": price_value,
            "price_currency": "PLN",
            "price_label": price_label,
            "city_name": city_name,
            "region_name": "dolnośląskie",
            "source": "facebook_group",
            "source_detail": "",
            "contact_method": "facebook_pm",
            "contact_note": "",
            "created_time": NOW_ISO[:10],
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
    has_gps = 0
    groups: dict[str, int] = {}
    for r in records:
        city = r.get("city_name") or "?"
        cities[city] = cities.get(city, 0) + 1
        if r.get("price_value") == 0 or "za darmo" in (r.get("price_label") or "").lower():
            free_count += 1
        if r.get("lat") is not None and r.get("lon") is not None:
            has_gps += 1
        grp = r.get("source_detail") or "?"
        groups[grp] = groups.get(grp, 0) + 1
    return {
        "total": len(records),
        "free": free_count,
        "paid_or_empty": len(records) - free_count,
        "has_gps": has_gps,
        "cities": dict(sorted(cities.items(), key=lambda x: -x[1])),
        "groups": dict(sorted(groups.items(), key=lambda x: -x[1])),
    }


def print_stats(stats: dict[str, Any]) -> None:
    print(f" Darmo: {stats['free']}, Platne/puste: {stats['paid_or_empty']}")
    print(f" Z GPS: {stats['has_gps']}/{stats['total']}")
    print(f" Miasta: {stats['cities']}")
    print(f" Grupy: {stats['groups']}")


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

    normalized = [normalize_fb_jsonl_record(r, i + 1) for i, r in enumerate(raw_records)]

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
        "filtered_non_resource": before - len(raw_records) if filter_non_resource else 0,
        "stats": stats,
        "output_path": str(output),
        "ingested_at": NOW_ISO,
    }


def ingest_text(text_path: Path, output: Path, *, filter_non_resource: bool = True) -> dict[str, Any]:
    print(f"[scout_ingest_facebook] Text dump: {text_path}")
    raw_posts = parse_text_dump(text_path)
    print(f" Znaleziono postow (heuristic): {len(raw_posts)}")

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
    print(f"[scout_ingest_facebook] Auto-detect in: {source_dir}")

    all_valid: list[dict[str, Any]] = []
    ingest_log: list[dict[str, Any]] = []

    jsonl_files = sorted(source_dir.glob("*.jsonl"))
    for jf in jsonl_files:
        print(f" Found JSONL: {jf.name}")
        raw = read_jsonl(jf)
        if filter_non_resource:
            raw = [r for r in raw if is_resource_offer(r)]
        normalized = [normalize_fb_jsonl_record(r, len(all_valid) + i + 1) for i, r in enumerate(raw)]
        valid = [r for r in normalized if not validate_scout_record(r)]
        print(f" {len(raw)} raw -> {len(valid)} valid scout records")
        all_valid.extend(valid)
        ingest_log.append({"source": str(jf), "type": "jsonl", "raw": len(raw), "valid": len(valid)})

    text_files = sorted(source_dir.glob("*.txt"))
    for tf in text_files:
        print(f" Found text: {tf.name}")
        raw = parse_text_dump(tf)
        if filter_non_resource:
            raw = [r for r in raw if is_resource_offer(r)]
        valid = [r for r in raw if not validate_scout_record(r)]
        print(f" {len(raw)} raw -> {len(valid)} valid scout records")
        all_valid.extend(valid)
        ingest_log.append({"source": str(tf), "type": "text", "raw": len(raw), "valid": len(valid)})

    seen_ids: set[str] = set()
    deduped = []
    for rec in all_valid:
        rid = rec.get("id", "")
        if rid in seen_ids:
            continue
        seen_ids.add(rid)
        deduped.append(rec)

    dupes = len(all_valid) - len(deduped)
    if dupes:
        print(f" Deduplikacja: {dupes} duplikatow usunietych")

    stats = compute_stats(deduped)
    print(f" Laczone: {len(deduped)} scout records z {len(ingest_log)} zrodel")
    print_stats(stats)

    write_jsonl(deduped, output)
    print(f" Zapisano: {output}")

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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Facebook Groups -> Scout bridge: normalize FB posts to scout schema JSONL",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--jsonl", type=Path, help="Path to FB JSONL export")
    group.add_argument("--text", type=Path, help="Path to FB text dump (copy-paste)")
    group.add_argument("--auto", action="store_true", help="Auto-detect JSONL and text in source-dir")

    parser.add_argument("--source-dir", type=Path, help="Directory for --auto mode")
    parser.add_argument("--output", type=Path, required=True, help="Output scout JSONL path")
    parser.add_argument("--no-filter", action="store_true", help="Disable non-resource filtering")

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

    receipt_path = Path(args.output).parent / f"ingest_receipt_fb_58_{TODAY_STR}.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    with open(receipt_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Receipt: {receipt_path}")


if __name__ == "__main__":
    main()
