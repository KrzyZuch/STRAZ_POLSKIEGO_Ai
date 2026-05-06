#!/usr/bin/env python3
"""Resource signal scouting and matching engine for Project 15.

Processes external signals (OLX, social media, classifieds) to:
- categorize offers by electronics/AGD/parts/material type
- assess potential value (free, cheap, market-price)
- match supply (offers) with demand (wanted) signals
- export structured recommendations with location-aware scoring

This script does NOT scrape any live source; it works on pre-scraped
JSONL fixtures or data exported by Kaggle notebooks.

Commands:
    ingest-olx-sql --sql <file> --output <jsonl> Parse OLX D1 SQL dump into scout JSONL
    ingest-olx-jsonl --jsonl <file> --output <jsonl> Parse OLX JSONL export into scout JSONL
    ingest-manual --source <jsonl> [--output <jsonl>] Ingest manual/social signals (validate + normalize)
    ingest-facebook --jsonl <file> --output <jsonl> Ingest Facebook group posts (JSONL export)
    ingest-facebook-text --text <file> --output <jsonl> Ingest Facebook group posts (text dump)
    ingest-allegro --jsonl <file> --output <jsonl> Ingest Allegro Lokalnie (JSONL export)
    ingest-allegro-text --html-lines <file> --output <jsonl> Ingest Allegro Lokalnie (HTML-lines dump)
    ingest-pipeline --source-dir <dir> [--output-dir <dir>] Pipeline: ingest→categorize→assess→match→export (OLX+manual)
    ingest-all --source-dir <dir> [--fb-dir <dir>] [--allegro-dir <dir>] Full multi-source pipeline (OLX+FB+Allegro+manual)
    categorize --source <jsonl> Tag each signal with category and subcategory
    assess --source <jsonl> Score potential value per signal
    match --supply <jsonl> --demand <jsonl> Pair supply with demand
    export --source <jsonl> Export full scouting report with receipt
"""

from __future__ import annotations

import argparse
import importlib
import json
import math
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OLX_DATA_DIR = PROJECT_ROOT / "olx_data"
REPORTS_DIR = PROJECT_ROOT / "autonomous_test" / "reports"
FIXTURE_DIR = OLX_DATA_DIR

NOW_ISO = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
TODAY_STR = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

CATEGORIES = {
    "elektronika": {
        "keywords": [
            "laptop", "komputer", "monitor", "drukarka", "telefon", "smartfon",
            "tablet", "telewizor", "tv", "konsola", "playstation", "xbox",
            "nintendo", "klawiatura", "mysz", "myszka", "słuchawki", "głośniki",
            "router", "modem", "switch", "raspberry", "arduino", "esp32",
            "płytka", "układ", "scalony", "tranzystor", "kondensator", "rezystor",
            "dioda", "transformator", "zasilacz", "ładowarka", "powerbank",
            "kabel", "przewód", "adapter", "przejściówka", "pendrive", "dysk",
            "ssd", "hdd", "pamięć", "ram", "procesor", "cpu", "gpu", "karta graficzna",
            "płyta główna", "motherboard", "mainboard", "wentylator", "chłodzenie",
            "obudowa", "elektronika", "elektroniczny", "pcb", "serwer", "ups",
            "kamera", "aparat", "mikrofon", "gimbal", "dron", "czujnik", "sensor",
            "wyświetlacz", "ekran", "matryca", "lcd", "led", "oled",
        ],
        "subcategories": {
            "czesci_elektroniczne": [
                "układ scalony", "tranzystor", "kondensator", "rezystor",
                "dioda", "transformator", "płytka", "pcb", "zasilacz",
                "moduł", "przetwornica", "sterownik",
            ],
            "urzadzenia": [
                "laptop", "komputer", "monitor", "drukarka", "telefon",
                "tablet", "telewizor", "router", "konsola", "serwer",
            ],
            "peryferia": [
                "klawiatura", "mysz", "myszka", "słuchawki", "głośniki",
                "kamera", "mikrofon", "pendrive", "dysk zewnętrzny",
            ],
            "czesci_komputerowe": [
                "procesor", "cpu", "gpu", "karta graficzna", "płyta główna",
                "motherboard", "pamięć ram", "ssd", "hdd", "dysk twardy",
                "wentylator", "chłodzenie", "obudowa",
            ],
        },
    },
    "agd": {
        "keywords": [
            "pralka", "lodówka", "zmywarka", "piekarnik", "kuchenka",
            "mikrofalówka", "odkurzacz", "żelazko", "czajnik", "ekspres",
            "toster", "blender", "robot kuchenny", "suszarka", "pralkosuszarka",
            "okap", "płyta grzewcza", "indukcja", "gazówka", "termowentylator",
            "grzejnik", "klimatyzator", "nawilżacz", "oczyszczacz",
            "agd", "sprzęt gospodarstwa", "gospodarstwo domowe",
        ],
    },
    "narzedzia_i_warsztat": {
        "keywords": [
            "wiertarka", "szlifierka", "piła", "młot", "klucz", "śrubokręt",
            "imadło", "spawarka", "tokarka", "frezarka", "multimetr",
            "oscyloskop", "lutownica", "stacja lutownicza", "miernik",
            "narzędzie", "narzędzia", "wkrętarka", "pilarka", "strug",
            "kompresor", "pistolet", "sprężarka", "podnośnik", "lewarek",
            "zestaw narzędzi", "skrzynka narzędziowa", "warsztat",
        ],
    },
    "materialy_i_konstrukcje": {
        "keywords": [
            "deska", "drewno", "sklejka", "płyta", "metal", "stal",
            "aluminium", "profil", "kątownik", "ceownik", "rurka",
            "blacha", "siatka", "pleksi", "plexiglas", "tworzywo",
            "plastik", "guma", "silikon", "pianka", "styropian",
            "śruba", "nakrętka", "podkładka", "nit", "kołek",
            "materiał", "budowlany", "budowlane", "konstrukcyjny",
        ],
    },
    "pojazdy_i_transport": {
        "keywords": [
            "rower", "hulajnoga", "skuter", "motor", "motocykl",
            "quad", "części samochodowe", "akumulator", "alternator",
            "rozrusznik", "opona", "felga", "koło", "bagażnik",
            "uchwyt", "fotelik", "przyczepa", "przyczepka",
        ],
    },
}

DEMAND_KEYWORDS = {
    "potrzebuje": 3,
    "szukam": 3,
    "kupię": 2,
    "poszukuję": 3,
    "odkupię": 2,
    "przyjmę": 2,
    "zabiorę": 1,
    "zamienię": 1,
    "przygarnę": 1,
}

FREE_KEYWORDS = [
    "oddam za darmo", "oddam za free", "za darmo", "gratis",
    "do oddania", "oddam", "za free", "odbiór za darmo",
    "za odbiór", "za darmo odbiór",
]

LOW_PRICE_THRESHOLD_PLN = 50

NON_RESOURCE_TITLE_PATTERNS = [
    "kocurek", "kot ", "koty ", "pies", "pieski", "szczeniaki",
    "adopcj", "do adopcji", "zwierza", "zwierzaka", "kotek",
    "szczeniak", "piesek", "królik", "chomik", "papuga",
    "rybki", "żółw", "gad", "kotka",
]


def is_resource_offer(record: dict[str, Any]) -> bool:
    title = (record.get("title") or "").lower()
    desc = (record.get("description") or "").lower()
    text = title + " " + desc
    for pattern in NON_RESOURCE_TITLE_PATTERNS:
        if pattern in text:
            return False
    return True


BASE_LOCATION = {
    "city": "Kłodzko",
    "lat": 50.4346,
    "lon": 16.6614,
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


def load_source(path: Path) -> list[dict[str, Any]]:
    if path.exists():
        return read_jsonl(path)
    print(f"  ⚠️  {path} nie istnieje, generuje fixture danych testowych")
    return generate_test_fixture()


def generate_test_fixture() -> list[dict[str, Any]]:
    return [
        {"id": "fix-001", "title": "Oddam za darmo stary laptop Dell Latitude",
         "description": "Działa, bez dysku. Odbiór osobisty Kłodzko.",
         "price_value": 0, "price_currency": "PLN", "price_label": "Za darmo",
         "city_name": "Kłodzko", "region_name": "dolnośląskie",
         "lat": 50.4346, "lon": 16.6614,
         "source": "olx", "created_time": "2026-04-28", "olx_url": "https://olx.pl/fixture/001"},
        {"id": "fix-002", "title": "Sprzedam procesor Intel i5-3470 — tanio",
         "description": "Sprawny, wyjęty z działającego komputera. 50zł.",
         "price_value": 50, "price_currency": "PLN", "price_label": "50 zł",
         "city_name": "Kłodzko", "region_name": "dolnośląskie",
         "lat": 50.4346, "lon": 16.6614,
         "source": "olx", "created_time": "2026-04-29", "olx_url": "https://olx.pl/fixture/002"},
        {"id": "fix-003", "title": "Oddam pralkę whirlpool do naprawy",
         "description": "Nie wiruje, może do rozebrania na części. Kłodzko.",
         "price_value": 0, "price_currency": "PLN", "price_label": "Za darmo",
         "city_name": "Kłodzko", "region_name": "dolnośląskie",
         "lat": 50.4346, "lon": 16.6614,
         "source": "olx", "created_time": "2026-04-30", "olx_url": "https://olx.pl/fixture/003"},
        {"id": "fix-004", "title": "Szukam zasilacza 12V 5A do LED-ów",
         "description": "Potrzebuję sprawnego zasilacza. Mogę odebrać w Kłodzku lub okolicy.",
         "price_value": None, "price_currency": "PLN", "price_label": "",
         "city_name": "Kłodzko", "region_name": "dolnośląskie",
         "lat": 50.4346, "lon": 16.6614,
         "source": "olx", "created_time": "2026-04-28", "olx_url": "https://olx.pl/fixture/004"},
        {"id": "fix-005", "title": "Oddam za darmo telewizor LCD 32 cale",
         "description": "Działa, brak pilota. Stoi w piwnicy. Odbiór Kłodzko centrum.",
         "price_value": 0, "price_currency": "PLN", "price_label": "Za darmo",
         "city_name": "Kłodzko", "region_name": "dolnośląskie",
         "lat": 50.4346, "lon": 16.6614,
         "source": "olx", "created_time": "2026-04-29", "olx_url": "https://olx.pl/fixture/005"},
        {"id": "fix-006", "title": "Kupię płytę główną do laptopa HP ProBook 450 G3",
         "description": "Poszukuję sprawnej lub do odzysku części. Dolnośląskie.",
         "price_value": None, "price_currency": "PLN", "price_label": "",
         "city_name": "Wrocław", "region_name": "dolnośląskie",
         "lat": 51.1079, "lon": 17.0385,
         "source": "olx", "created_time": "2026-04-30", "olx_url": "https://olx.pl/fixture/006"},
        {"id": "fix-007", "title": "Elektrośmieci do oddania — komputer, monitor CRT, drukarka",
         "description": "Stare, nieużywane. Monitor CRT 17\", drukarka HP, pecet. Do odbioru Nowa Ruda.",
         "price_value": 0, "price_currency": "PLN", "price_label": "Za darmo",
         "city_name": "Nowa Ruda", "region_name": "dolnośląskie",
         "lat": 50.5796, "lon": 16.5010,
         "source": "olx", "created_time": "2026-04-27", "olx_url": "https://olx.pl/fixture/007"},
        {"id": "fix-008", "title": "Potrzebuję części do zmywarki Bosch — pompa myjąca",
         "description": "Zmywarka Bosch SMS40E32EU. Szukam pompy myjącej, może być używana sprawna.",
         "price_value": None, "price_currency": "PLN", "price_label": "",
         "city_name": "Kłodzko", "region_name": "dolnośląskie",
         "lat": 50.4346, "lon": 16.6614,
         "source": "olx", "created_time": "2026-04-29", "olx_url": "https://olx.pl/fixture/008"},
        {"id": "fix-009", "title": "Oddam deski i kantówkę po remoncie",
         "description": "Sosnowe, różne długości. Do odbioru z garażu Polanica-Zdrój.",
         "price_value": 0, "price_currency": "PLN", "price_label": "Za darmo",
         "city_name": "Polanica-Zdrój", "region_name": "dolnośląskie",
         "lat": 50.4047, "lon": 16.5146,
         "source": "olx", "created_time": "2026-04-30", "olx_url": "https://olx.pl/fixture/009"},
        {"id": "fix-010", "title": "Szukam tanio - Raspberry Pi 4 lub 5",
         "description": "Do projektu domowego. Może być używany, najważniejsze żeby działał. Okolice Kłodzka.",
         "price_value": None, "price_currency": "PLN", "price_label": "",
         "city_name": "Kłodzko", "region_name": "dolnośląskie",
         "lat": 50.4346, "lon": 16.6614,
         "source": "olx", "created_time": "2026-05-01", "olx_url": "https://olx.pl/fixture/010"},
        {"id": "fix-011", "title": "Sprzedam stację lutowniczą WEP 937D tanio 40zł",
         "description": "Sprawna, używana okazyjnie. Kompletna z grotami. Kłodzko.",
         "price_value": 40, "price_currency": "PLN", "price_label": "40 zł",
         "city_name": "Kłodzko", "region_name": "dolnośląskie",
         "lat": 50.4346, "lon": 16.6614,
         "source": "olx", "created_time": "2026-04-30", "olx_url": "https://olx.pl/fixture/011"},
        {"id": "fix-012", "title": "Oddam silniki krokowe i prowadnice z drukarki 3D",
         "description": "Po upgrade. Silniki NEMA17, prowadnice liniowe 8mm, śruby trapezowe. Odbiór osobisty Bystrzyca Kłodzka.",
         "price_value": 0, "price_currency": "PLN", "price_label": "Za darmo",
         "city_name": "Bystrzyca Kłodzka", "region_name": "dolnośląskie",
         "lat": 50.3008, "lon": 16.6480,
         "source": "olx", "created_time": "2026-04-29", "olx_url": "https://olx.pl/fixture/012"},
    ]


def text_lower(record: dict[str, Any]) -> str:
    return (record.get("title", "") + " " + record.get("description", "")).lower()


def categorize_record(record: dict[str, Any]) -> dict[str, Any]:
    text = text_lower(record)
    primary = None
    subcategory = None

    for cat_name, cat_def in CATEGORIES.items():
        for kw in cat_def["keywords"]:
            if kw.lower() in text:
                primary = cat_name
                break
        if primary:
            break

    if primary and "subcategories" in CATEGORIES.get(primary, {}):
        for sub_name, sub_kws in CATEGORIES[primary]["subcategories"].items():
            for kw in sub_kws:
                if kw.lower() in text:
                    subcategory = sub_name
                    break
            if subcategory:
                break

    result = dict(record)
    result["scout_category"] = primary or "inne"
    result["scout_subcategory"] = subcategory
    return result


def is_demand_signal(record: dict[str, Any]) -> bool:
    text = text_lower(record)
    for kw, weight in DEMAND_KEYWORDS.items():
        if kw in text:
            return True
    if record.get("price_value") is None and record.get("price_label", "") == "":
        return True
    return False


def classify_signal_type(record: dict[str, Any]) -> str:
    if is_demand_signal(record):
        return "demand"
    return "supply"


def is_free(record: dict[str, Any]) -> bool:
    text = text_lower(record)
    price = record.get("price_value")
    if price is not None and price == 0:
        return True
    if record.get("price_label", "").lower() in ("za darmo", "gratis", ""):
        for kw in FREE_KEYWORDS:
            if kw in text:
                return True
    return False


def is_cheap(record: dict[str, Any]) -> bool:
    if is_free(record):
        return True
    price = record.get("price_value")
    if price is not None and 0 < price <= LOW_PRICE_THRESHOLD_PLN:
        price_label = record.get("price_label", "").lower()
        if any(kw in price_label for kw in ("tanio", "okazja", "promocja")):
            return True
        if "sprzedam" in text_lower(record) and "tanio" in text_lower(record):
            return True
        return True
    return False


def assess_potential(record: dict[str, Any]) -> dict[str, Any]:
    result = dict(record)
    text = text_lower(record)

    if is_free(record):
        result["scout_tier"] = "tier1_free"
        result["scout_score"] = 100
        result["scout_signals"] = ["darmo", "natychmiastowa okazja"]
    elif is_cheap(record):
        result["scout_tier"] = "tier2_cheap"
        result["scout_score"] = 60
        result["scout_signals"] = ["tanio", "ponizej progu 50zl"]
    elif is_demand_signal(record):
        result["scout_tier"] = "demand_signal"
        result["scout_score"] = 30
        result["scout_signals"] = ["zapotrzebowanie"]
    else:
        result["scout_tier"] = "tier3_review"
        result["scout_score"] = 10
        result["scout_signals"] = ["do recznej oceny"]

    if result.get("scout_category") == "elektronika":
        result["scout_score"] += 5
    if "do naprawy" in text or "do odzysku" in text or "na części" in text:
        result["scout_score"] += 10
        result.setdefault("scout_signals", []).append("potencjal odzysku/reuse")

    result["scout_signal_type"] = classify_signal_type(record)
    return result


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    import math
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def compute_distance_km(rec_a: dict[str, Any], rec_b: dict[str, Any]) -> float | None:
    lat_a = rec_a.get("lat")
    lon_a = rec_a.get("lon")
    lat_b = rec_b.get("lat")
    lon_b = rec_b.get("lon")
    if None in (lat_a, lon_a, lat_b, lon_b):
        return None
    return haversine_km(float(lat_a), float(lon_a), float(lat_b), float(lon_b))


def overlap_score(text_a: str, text_b: str) -> int:
    score = 0
    for kw_set in CATEGORIES.values():
        for kw in kw_set["keywords"]:
            kw_l = kw.lower()
            if kw_l in text_a and kw_l in text_b:
                score += 1
    subcats = set()
    for cat_def in CATEGORIES.values():
        for sub_kws in cat_def.get("subcategories", {}).values():
            for kw in sub_kws:
                subcats.add(kw.lower())
    for kw in subcats:
        if kw in text_a and kw in text_b:
            score += 3
    return score


def match_signals(supply: list[dict[str, Any]], demand: list[dict[str, Any]]) -> list[dict[str, Any]]:
    matches = []
    for s_rec in supply:
        s_text = text_lower(s_rec)
        s_cat = s_rec.get("scout_category", "inne")
        for d_rec in demand:
            d_text = text_lower(d_rec)
            d_cat = d_rec.get("scout_category", "inne")
            kw_score = overlap_score(s_text, d_text)
            if kw_score < 2 and s_cat != d_cat:
                continue
            dist = compute_distance_km(s_rec, d_rec)
            dist_score = 0.0
            if dist is not None:
                if dist <= 5:
                    dist_score = 1.0
                elif dist <= 20:
                    dist_score = 0.7
                elif dist <= 50:
                    dist_score = 0.4
                elif dist <= 100:
                    dist_score = 0.2
                else:
                    dist_score = 0.05

            price_score = 1.0 if s_rec.get("scout_tier") in ("tier1_free", "tier2_cheap") else 0.3
            demand_score = (d_rec.get("scout_score", 10) / 100.0)
            match_score = round((kw_score * 0.3 + dist_score * 0.3 + price_score * 0.25 + demand_score * 0.15) * 100, 1)

            matches.append({
                "match_id": f"match-{len(matches)+1:04d}",
                "supply_id": s_rec.get("id"),
                "demand_id": d_rec.get("id"),
                "supply_title": s_rec.get("title"),
                "demand_title": d_rec.get("title"),
                "supply_location": s_rec.get("city_name") or "?",
                "demand_location": d_rec.get("city_name") or "?",
                "distance_km": round(dist, 2) if dist is not None else None,
                "keyword_overlap": kw_score,
                "supply_tier": s_rec.get("scout_tier"),
                "match_score": match_score,
                "recommendation": "PRIORYTET" if match_score >= 60 else ("ROZWAZ" if match_score >= 30 else "SLABY"),
                "matched_at": NOW_ISO,
            })
    matches.sort(key=lambda m: m["match_score"], reverse=True)
    return matches


def parse_olx_sql_inserts(sql_path: Path) -> list[dict[str, Any]]:
    db = sqlite3.connect(":memory:")
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("""CREATE TABLE IF NOT EXISTS olx_offers (
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
        raw_params_json TEXT, raw_delivery_json TEXT)""")
    db.execute("""CREATE TABLE IF NOT EXISTS olx_offer_photos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, offer_id INTEGER NOT NULL,
        photo_id INTEGER, cdn_url TEXT NOT NULL,
        width INTEGER, height INTEGER, rotation INTEGER DEFAULT 0,
        sort_order INTEGER DEFAULT 0,
        FOREIGN KEY (offer_id) REFERENCES olx_offers(id) ON DELETE CASCADE)""")
    with open(sql_path, encoding="utf-8") as f:
        sql_text = f.read()
    statements = []
    for line in sql_text.split("\n"):
        stripped = line.strip()
        if stripped.upper().startswith("INSERT"):
            statements.append(stripped)
    if statements:
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


def normalize_olx_record(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": f"olx-{raw.get('id', 'unknown')}",
        "title": raw.get("title", ""),
        "description": (raw.get("description") or "").replace("<br />", " ").replace("<br/>", " "),
        "price_value": raw.get("price_value"),
        "price_currency": raw.get("price_currency", "PLN"),
        "price_label": raw.get("price_label", ""),
        "price_negotiable": raw.get("price_negotiable", 0),
        "state": raw.get("state", ""),
        "category_id": raw.get("category_id"),
        "category_type": raw.get("category_type", ""),
        "city_name": raw.get("city_name", ""),
        "city_normalized": raw.get("city_normalized", ""),
        "region_name": raw.get("region_name", ""),
        "lat": raw.get("lat"),
        "lon": raw.get("lon"),
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


def normalize_olx_jsonl_record(raw: dict[str, Any]) -> dict[str, Any]:
    mapping = {
        "id": "id", "olx_url": "olx_url", "title": "title", "description": "description",
        "price_value": "price_value", "price_currency": "price_currency",
        "price_label": "price_label", "price_negotiable": "price_negotiable",
        "state": "state", "category_id": "category_id", "category_type": "category_type",
        "city_name": "city_name", "city_normalized": "city_normalized",
        "region_name": "region_name", "lat": "lat", "lon": "lon",
        "user_name": "user_name", "user_business": "user_business",
        "has_phone": "has_phone", "has_chat": "has_chat",
        "photo_count": "photo_count", "status": "status", "created_time": "created_time",
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


def normalize_manual_record(raw: dict[str, Any]) -> dict[str, Any]:
    sig_id = raw.get("id", f"manual-{hash(raw.get('title',''))%100000:05d}")
    return {
        "id": sig_id,
        "title": raw.get("title", ""),
        "description": raw.get("description", ""),
        "price_value": raw.get("price_value"),
        "price_currency": raw.get("price_currency", "PLN"),
        "price_label": raw.get("price_label", ""),
        "city_name": raw.get("city_name", ""),
        "region_name": raw.get("region_name", ""),
        "lat": raw.get("lat"),
        "lon": raw.get("lon"),
        "source": raw.get("source", "manual"),
        "source_detail": raw.get("source_detail", ""),
        "contact_method": raw.get("contact_method", ""),
        "contact_note": raw.get("contact_note", ""),
        "status": raw.get("status", "active"),
        "created_time": raw.get("created_time", NOW_ISO[:10]),
        "olx_url": raw.get("url", ""),
        "ingested_at": NOW_ISO,
    }


def validate_manual_record(rec: dict[str, Any]) -> list[str]:
    errors = []
    if not rec.get("title"):
        errors.append("missing title")
    if rec.get("price_value") is not None:
        try:
            float(rec["price_value"])
        except (ValueError, TypeError):
            errors.append(f"invalid price_value: {rec['price_value']}")
    return errors


def cmd_ingest_olx_sql(sql_path: Path, output: Path) -> None:
    print(f"Ingestia OLX SQL dump: {sql_path}")
    raw_records = parse_olx_sql_inserts(sql_path)
    print(f"  Rekordow w SQL: {len(raw_records)}")
    if not raw_records:
        print("  ⚠️  Brak rekordow olx_offers w SQL dump. Sprawdz format INSERT.")
        return
    normalized = [normalize_olx_record(r) for r in raw_records]
    sources: dict[str, int] = {}
    cities: dict[str, int] = {}
    free_count = 0
    for r in normalized:
        sources[r.get("source", "?")] = sources.get(r.get("source", "?"), 0) + 1
        city = r.get("city_name") or "?"
        cities[city] = cities.get(city, 0) + 1
        if r.get("price_value") == 0 or "za darmo" in (r.get("price_label") or "").lower():
            free_count += 1
    print(f"  Normalized: {len(normalized)}")
    print(f"  Darmo: {free_count}, Platne/puste: {len(normalized) - free_count}")
    print(f"  Miasta: {dict(sorted(cities.items(), key=lambda x: -x[1]))}")
    write_jsonl(normalized, output)
    print(f"  Zapisano: {output}")


def cmd_ingest_manual(source: Path, output: Path | None = None) -> None:
    print(f"Ingestia manual/social signals: {source}")
    raw_records = read_jsonl(source)
    print(f"  Rekordow w zrodle: {len(raw_records)}")
    errors_all: list[str] = []
    normalized = []
    for i, raw in enumerate(raw_records):
        errs = validate_manual_record(raw)
        if errs:
            errors_all.append(f"  [{i}] {raw.get('id', '?')}: {', '.join(errs)}")
            continue
        normalized.append(normalize_manual_record(raw))
    if errors_all:
        print(f"  ⚠️  Bledy walidacji ({len(errors_all)}):")
        for e in errors_all[:10]:
            print(e)
    sources: dict[str, int] = {}
    for r in normalized:
        src = r.get("source", "manual")
        sources[src] = sources.get(src, 0) + 1
    print(f"  Znormalizowano: {len(normalized)}")
    print(f"  Zrodla: {sources}")
    if output:
        write_jsonl(normalized, output)
        print(f"  Zapisano: {output}")
    else:
        for r in normalized[:5]:
            print(f" {r.get('id')}: {r.get('title', '')[:60]}...")


def cmd_ingest_olx_jsonl(jsonl_path: Path, output: Path) -> None:
    print(f"Ingestia OLX JSONL export: {jsonl_path}")
    raw_records = read_jsonl(jsonl_path)
    print(f" Rekordow w JSONL: {len(raw_records)}")
    normalized = [normalize_olx_jsonl_record(r) for r in raw_records]
    errors_all: list[str] = []
    valid = []
    for i, rec in enumerate(normalized):
        errs = []
        if not rec.get("title"):
            errs.append("missing title")
        if errs:
            errors_all.append(f" [{i}] {rec.get('id', '?')}: {', '.join(errs)}")
        else:
            valid.append(rec)
    if errors_all:
        print(f" Bledy walidacji ({len(errors_all)}):")
        for e in errors_all[:10]:
            print(e)
    sources: dict[str, int] = {}
    cities: dict[str, int] = {}
    free_count = 0
    for r in valid:
        src = r.get("source", "olx")
        sources[src] = sources.get(src, 0) + 1
        city = r.get("city_name") or "?"
        cities[city] = cities.get(city, 0) + 1
        if r.get("price_value") == 0 or "za darmo" in (r.get("price_label") or "").lower():
            free_count += 1
    print(f" Znormalizowano: {len(valid)}")
    print(f" Darmo: {free_count}, Platne/puste: {len(valid) - free_count}")
    print(f" Miasta: {dict(sorted(cities.items(), key=lambda x: -x[1]))}")
    write_jsonl(valid, output)
    print(f" Zapisano: {output}")


def cmd_ingest_pipeline(source_dir: Path, output_dir: Path | None = None) -> dict[str, Any]:
    print("=" * 60)
    print("SCOUT INGEST PIPELINE (Zadanie 57)")
    print("=" * 60)
    output_dir = output_dir or REPORTS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    ingested_path = output_dir / f"scout_ingested_{TODAY_STR}.jsonl"

    all_records: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    ingest_sources: list[str] = []

    sql_files = sorted(source_dir.glob("*.sql"))
    for sql_path in sql_files:
        print(f"\n[1/5] Ingest SQL: {sql_path.name}")
        raw = parse_olx_sql_inserts(sql_path)
        normalized = [normalize_olx_record(r) for r in raw]
        for rec in normalized:
            rid = rec.get("id", "")
            if rid and rid not in seen_ids:
                if not is_resource_offer(rec):
                    continue
                seen_ids.add(rid)
                all_records.append(rec)
        ingest_sources.append(f"sql:{sql_path.name}:{len(normalized)}")
        print(f" {len(raw)} raw → {len(normalized)} normalized")

    jsonl_files = sorted(source_dir.glob("*.jsonl"))
    for jsonl_path in jsonl_files:
        print(f"\n[1/5] Ingest JSONL: {jsonl_path.name}")
        raw = read_jsonl(jsonl_path)
        normalized = [normalize_olx_jsonl_record(r) for r in raw]
        before = len(all_records)
        for rec in normalized:
            rid = rec.get("id", "")
            if rid and rid not in seen_ids:
                if not is_resource_offer(rec):
                    continue
                seen_ids.add(rid)
                all_records.append(rec)
        added = len(all_records) - before
        ingest_sources.append(f"jsonl:{jsonl_path.name}:{added}")
        print(f" {len(raw)} raw → {added} new (deduped+filtered)")

    manual_dir = source_dir.parent / "scout_data" / "signals_manual"
    if manual_dir.exists():
        for tmpl_path in sorted(manual_dir.glob("template_*.jsonl")):
            print(f"\n[1/5] Ingest manual: {tmpl_path.name}")
            raw = read_jsonl(tmpl_path)
            normalized = [normalize_manual_record(r) for r in raw]
            before = len(all_records)
            for rec in normalized:
                rid = rec.get("id", "")
                if rid and rid not in seen_ids:
                    if not is_resource_offer(rec):
                        continue
                    seen_ids.add(rid)
                    all_records.append(rec)
            added = len(all_records) - before
            ingest_sources.append(f"manual:{tmpl_path.name}:{added}")
            print(f" {len(raw)} raw → {added} new (deduped+filtered)")

    write_jsonl(all_records, ingested_path)
    print(f"\n[1/5] Ingest complete: {len(all_records)} records → {ingested_path}")

    print(f"\n[2/5] Categorize...")
    categorized = [categorize_record(r) for r in all_records]
    categories: dict[str, int] = {}
    for r in categorized:
        c = r.get("scout_category", "inne")
        categories[c] = categories.get(c, 0) + 1
    print(f" {len(categorized)} records → {len(categories)} categories")
    for cat, cnt in sorted(categories.items()):
        print(f" {cat}: {cnt}")

    print(f"\n[3/5] Assess...")
    assessed = [assess_potential(r) for r in categorized]
    supply = [r for r in assessed if r.get("scout_signal_type") == "supply"]
    demand = [r for r in assessed if r.get("scout_signal_type") == "demand"]
    tiers: dict[str, int] = {}
    for r in assessed:
        t = r.get("scout_tier", "?")
        tiers[t] = tiers.get(t, 0) + 1
    print(f" supply: {len(supply)}, demand: {len(demand)}")
    for tier, cnt in sorted(tiers.items()):
        print(f" {tier}: {cnt}")

    print(f"\n[4/5] Match...")
    matches = match_signals(supply, demand)
    priorities = [m for m in matches if m["recommendation"] == "PRIORYTET"]
    consider = [m for m in matches if m["recommendation"] == "ROZWAZ"]
    weak = [m for m in matches if m["recommendation"] == "SLABY"]
    print(f" {len(matches)} matches: PRIORYTET={len(priorities)}, ROZWAZ={len(consider)}, SLABY={len(weak)}")

    print(f"\n[5/5] Export...")
    receipt = {
        "receipt_type": "resource_scouting_57_pipeline",
        "generated_at": NOW_ISO,
        "ingest_sources": ingest_sources,
        "summary": {
            "total_records": len(assessed),
            "supply_signals": len(supply),
            "demand_signals": len(demand),
            "matches_total": len(matches),
            "matches_priority": len(priorities),
            "matches_consider": len(consider),
            "matches_weak": len(weak),
            "categories": categories,
            "tiers": tiers,
        },
        "top_matches": matches[:10],
        "blockers": [
            "Dane OLX ograniczone do SQL dump + JSONL fixture (brak pelnego scrapa)",
            "Facebook Marketplace / grupy: brak integracji (tylko szablony manual)",
            "Allegro Lokalnie: brak integracji",
            "Punktacja matchingu heurystyczna (30/30/25/15) — wymaga kalibracji na realnych danych",
        ],
        "next_steps": [
            "Uruchomic realny scrap OLX przez notebook na Kaggle z internetem ON",
            "Uzupelnic szablony manualne realnymi sygnalami z grup Facebook",
            "Podpiac wyniki pod bota Telegram (powiadomienia PRIORYTET)",
            "Import scouting results to D1 SQLite for query endpoint",
        ],
    }
    receipt_path = output_dir / f"resource_scouting_receipt_57_{TODAY_STR}.json"
    with open(receipt_path, "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=2)
    print(f" Receipt: {receipt_path}")

    assessed_path = output_dir / f"scout_assessed_57_{TODAY_STR}.jsonl"
    write_jsonl(assessed, assessed_path)
    print(f" Assessed: {assessed_path}")

    matches_path = output_dir / f"scout_matches_57_{TODAY_STR}.jsonl"
    write_jsonl(matches, matches_path)
    print(f"  Matches: {matches_path}")
    
    ingested_copy = output_dir / f"scout_ingested_57_{TODAY_STR}.jsonl"
    write_jsonl(all_records, ingested_copy)
    print(f"  Ingested: {ingested_copy}")
    
    print(f"\n{'=' * 60}")
    print(f"PIPELINE COMPLETE")
    print(f"  Ingest: {len(all_records)} records from {len(ingest_sources)} sources")
    print(f"  Categories: {categories}")
    print(f"  Matches: {len(matches)} (PRIORYTET={len(priorities)}, ROZWAZ={len(consider)})")
    print(f"{'=' * 60}")
    
    return receipt
    
    
def cmd_categorize(source: Path, output: Path | None = None) -> None:
    records = load_source(source)
    categorized = [categorize_record(r) for r in records]
    categories: dict[str, int] = {}
    for r in categorized:
        c = r.get("scout_category", "inne")
        categories[c] = categories.get(c, 0) + 1
    print(f"Kategoryzacja: {len(categorized)} rekordów → {len(categories)} kategorii")
    for cat, cnt in sorted(categories.items()):
        print(f"  {cat}: {cnt}")
    if output:
        write_jsonl(categorized, output)
        print(f"  Zapisano: {output}")


def cmd_assess(source: Path, output: Path | None = None) -> None:
    records = load_source(source)
    categorized = [categorize_record(r) for r in records]
    assessed = [assess_potential(r) for r in categorized]
    supply = [r for r in assessed if r.get("scout_signal_type") == "supply"]
    demand = [r for r in assessed if r.get("scout_signal_type") == "demand"]
    tiers: dict[str, int] = {}
    for r in assessed:
        t = r.get("scout_tier", "?")
        tiers[t] = tiers.get(t, 0) + 1
    print(f"Ocena potencjału: {len(assessed)} rekordów")
    print(f"  podaż (supply): {len(supply)}, popyt (demand): {len(demand)}")
    for tier, cnt in sorted(tiers.items()):
        print(f"  {tier}: {cnt}")
    if output:
        write_jsonl(assessed, output)
        print(f"  Zapisano: {output}")


def cmd_match(supply_path: Path, demand_path: Path | None, output: Path | None = None) -> None:
    supply = load_source(supply_path)
    supply = [categorize_record(r) for r in supply]
    supply = [assess_potential(r) for r in supply]
    supply = [r for r in supply if r.get("scout_signal_type") == "supply"]

    if demand_path:
        demand = load_source(demand_path)
        demand = [categorize_record(r) for r in demand]
        demand = [assess_potential(r) for r in demand]
        demand = [r for r in demand if r.get("scout_signal_type") == "demand"]
    else:
        all_records = load_source(supply_path)
        all_records = [categorize_record(r) for r in all_records]
        all_records = [assess_potential(r) for r in all_records]
        supply = [r for r in all_records if r.get("scout_signal_type") == "supply"]
        demand = [r for r in all_records if r.get("scout_signal_type") == "demand"]

    if not demand:
        print("  ⚠️  Brak sygnałów popytu (demand) w danych. Szukam potencjalnego popytu z opisów...")
        demand = [r for r in supply if "potrzebuj" in text_lower(r) or "szukam" in text_lower(r)]
        supply = [r for r in supply if r not in demand]

    matches = match_signals(supply, demand)
    print(f"Dopasowania: {len(matches)} par podaż-popyt")
    priorities = [m for m in matches if m["recommendation"] == "PRIORYTET"]
    consider = [m for m in matches if m["recommendation"] == "ROZWAZ"]
    weak = [m for m in matches if m["recommendation"] == "SLABY"]
    print(f"  PRIORYTET: {len(priorities)}, ROZWAZ: {len(consider)}, SLABY: {len(weak)}")
    if priorities:
        print("  Top rekomendacje:")
        for m in priorities[:5]:
            print(f"    [{m['match_score']}] {m['supply_title'][:50]}... ↔ {m['demand_title'][:50]}...")
    if output:
        write_jsonl(matches, output)
        print(f"  Zapisano: {output}")


def cmd_export(source: Path, output_dir: Path | None = None) -> dict[str, Any]:
    records = load_source(source)
    categorized = [categorize_record(r) for r in records]
    assessed = [assess_potential(r) for r in categorized]

    supply = [r for r in assessed if r.get("scout_signal_type") == "supply"]
    demand = [r for r in assessed if r.get("scout_signal_type") == "demand"]
    matches = match_signals(supply, demand)

    categories: dict[str, int] = {}
    tiers: dict[str, int] = {}
    for r in assessed:
        c = r.get("scout_category", "inne")
        categories[c] = categories.get(c, 0) + 1
        t = r.get("scout_tier", "?")
        tiers[t] = tiers.get(t, 0) + 1

    output_dir = output_dir or REPORTS_DIR
    receipt = {
        "receipt_type": "resource_scouting_56",
        "generated_at": NOW_ISO,
        "summary": {
            "total_records": len(assessed),
            "supply_signals": len(supply),
            "demand_signals": len(demand),
            "matches_total": len(matches),
            "matches_priority": len([m for m in matches if m["recommendation"] == "PRIORYTET"]),
            "matches_consider": len([m for m in matches if m["recommendation"] == "ROZWAZ"]),
            "matches_weak": len([m for m in matches if m["recommendation"] == "SLABY"]),
            "categories": categories,
            "tiers": tiers,
        },
        "top_matches": matches[:10],
        "blockers": [
            "Brak danych z zywych zrodel: OLX, Facebook, Allegro Lokalnie",
            "Scrapowanie wymaga konta Kaggle z internetem i/lub sekretow API",
            "Matching lokalizacyjny zalezy od jakosci danych GPS w ogloszeniach",
        ],
        "next_steps": [
            "Uruchomic realny scrap OLX przez notebook na Kaggle z internetem ON",
            "Dodac zrodlo Facebook Marketplace / grupy facebookowe",
            "Zintegrowac wyniki scoutingu z D1 SQLite dla query endpointu bota Telegram",
            "Dodac powiadomienia bota o nowych dopasowaniach priorytetowych",
        ],
    }
    receipt_path = output_dir / f"resource_scouting_receipt_56_{TODAY_STR}.json"
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(receipt_path, "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=2)
    print(f"Receipt: {receipt_path}")

    assessed_path = output_dir / f"scout_assessed_{TODAY_STR}.jsonl"
    write_jsonl(assessed, assessed_path)
    print(f"Assessed: {assessed_path}")

    matches_path = output_dir / f"scout_matches_{TODAY_STR}.jsonl"
    write_jsonl(matches, matches_path)
    print(f"Matches: {matches_path}")

    return receipt


FB_DATA_DIR = PROJECT_ROOT / "scout_data" / "facebook"
ALLEGRO_DATA_DIR = PROJECT_ROOT / "scout_data" / "allegro_lokalnie"


def _load_fb_module():
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    return importlib.import_module("scout_ingest_facebook")


def _load_allegro_module():
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    return importlib.import_module("scout_ingest_allegro_lokalnie")


def cmd_ingest_facebook(jsonl_path: Path, output: Path) -> None:
    fb = _load_fb_module()
    fb.ingest_jsonl(jsonl_path, output, filter_non_resource=True)


def cmd_ingest_facebook_text(text_path: Path, output: Path) -> None:
    fb = _load_fb_module()
    fb.ingest_text(text_path, output, filter_non_resource=True)


def cmd_ingest_allegro(jsonl_path: Path, output: Path) -> None:
    al = _load_allegro_module()
    al.ingest_jsonl(jsonl_path, output, filter_non_resource=True)


def cmd_ingest_allegro_text(html_lines_path: Path, output: Path) -> None:
    al = _load_allegro_module()
    al.ingest_html_lines(html_lines_path, output, filter_non_resource=True)


def cmd_ingest_all(
    source_dir: Path,
    fb_dir: Path | None,
    allegro_dir: Path | None,
    output_dir: Path | None,
) -> dict[str, Any]:
    print("=" * 60)
    print("SCOUT MULTI-SOURCE INGEST PIPELINE (Zadanie 58)")
    print("=" * 60)
    output_dir = output_dir or REPORTS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    ingested_path = output_dir / f"scout_ingested_58_{TODAY_STR}.jsonl"

    all_records: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    ingest_sources: list[str] = []

    sql_files = sorted(source_dir.glob("*.sql"))
    for sql_path in sql_files:
        print(f"\n[1/5] Ingest OLX SQL: {sql_path.name}")
        raw = parse_olx_sql_inserts(sql_path)
        normalized = [normalize_olx_record(r) for r in raw]
        before = len(all_records)
        for rec in normalized:
            rid = rec.get("id", "")
            if rid and rid not in seen_ids:
                if not is_resource_offer(rec):
                    continue
                seen_ids.add(rid)
                all_records.append(rec)
        added = len(all_records) - before
        ingest_sources.append(f"olx-sql:{sql_path.name}:{added}")
        print(f" {len(raw)} raw → {added} new (deduped+filtered)")

    jsonl_files = sorted(source_dir.glob("*.jsonl"))
    for jsonl_path in jsonl_files:
        print(f"\n[1/5] Ingest OLX JSONL: {jsonl_path.name}")
        raw = read_jsonl(jsonl_path)
        normalized = [normalize_olx_jsonl_record(r) for r in raw]
        before = len(all_records)
        for rec in normalized:
            rid = rec.get("id", "")
            if rid and rid not in seen_ids:
                if not is_resource_offer(rec):
                    continue
                seen_ids.add(rid)
                all_records.append(rec)
        added = len(all_records) - before
        ingest_sources.append(f"olx-jsonl:{jsonl_path.name}:{added}")
        print(f" {len(raw)} raw → {added} new (deduped+filtered)")

    manual_dir = source_dir.parent / "scout_data" / "signals_manual"
    if manual_dir.exists():
        for tmpl_path in sorted(manual_dir.glob("template_*.jsonl")):
            print(f"\n[1/5] Ingest manual: {tmpl_path.name}")
            raw = read_jsonl(tmpl_path)
            normalized = [normalize_manual_record(r) for r in raw]
            before = len(all_records)
            for rec in normalized:
                rid = rec.get("id", "")
                if rid and rid not in seen_ids:
                    if not is_resource_offer(rec):
                        continue
                    seen_ids.add(rid)
                    all_records.append(rec)
            added = len(all_records) - before
            ingest_sources.append(f"manual:{tmpl_path.name}:{added}")
            print(f" {len(raw)} raw → {added} new (deduped+filtered)")

    fb_search_dir = fb_dir or FB_DATA_DIR
    if fb_search_dir.exists():
        fb = _load_fb_module()
        fb_jsonl_files = sorted(fb_search_dir.glob("*.jsonl"))
        for fb_jf in fb_jsonl_files:
            print(f"\n[1/5] Ingest Facebook JSONL: {fb_jf.name}")
            raw = fb.read_jsonl(fb_jf)
            filtered = [r for r in raw if fb.is_resource_offer(r)]
            normalized = [fb.normalize_fb_jsonl_record(r, len(all_records) + i + 1) for i, r in enumerate(filtered)]
            before = len(all_records)
            for rec in normalized:
                rid = rec.get("id", "")
                if rid and rid not in seen_ids:
                    seen_ids.add(rid)
                    all_records.append(rec)
            added = len(all_records) - before
            ingest_sources.append(f"facebook-jsonl:{fb_jf.name}:{added}")
            print(f" {len(raw)} raw → {added} new (deduped)")

        fb_text_files = sorted(fb_search_dir.glob("*.txt"))
        for fb_tf in fb_text_files:
            print(f"\n[1/5] Ingest Facebook text: {fb_tf.name}")
            raw_posts = fb.parse_text_dump(fb_tf)
            filtered = [r for r in raw_posts if fb.is_resource_offer(r)]
            before = len(all_records)
            for rec in filtered:
                rid = rec.get("id", "")
                if rid and rid not in seen_ids:
                    rec["ingested_at"] = NOW_ISO
                    seen_ids.add(rid)
                    all_records.append(rec)
            added = len(all_records) - before
            ingest_sources.append(f"facebook-text:{fb_tf.name}:{added}")
            print(f" {len(raw_posts)} raw → {added} new (deduped)")
    else:
        print(f"\n[1/5] Facebook dir not found: {fb_search_dir} (skipping)")

    al_search_dir = allegro_dir or ALLEGRO_DATA_DIR
    if al_search_dir.exists():
        al = _load_allegro_module()
        al_jsonl_files = sorted(al_search_dir.glob("*.jsonl"))
        for al_jf in al_jsonl_files:
            print(f"\n[1/5] Ingest Allegro JSONL: {al_jf.name}")
            raw = al.read_jsonl(al_jf)
            filtered = [r for r in raw if al.is_resource_offer(r)]
            normalized = [al.normalize_allegro_jsonl_record(r, len(all_records) + i + 1) for i, r in enumerate(filtered)]
            before = len(all_records)
            for rec in normalized:
                rid = rec.get("id", "")
                if rid and rid not in seen_ids:
                    seen_ids.add(rid)
                    all_records.append(rec)
            added = len(all_records) - before
            ingest_sources.append(f"allegro-jsonl:{al_jf.name}:{added}")
            print(f" {len(raw)} raw → {added} new (deduped)")

        al_text_files = sorted(al_search_dir.glob("*.txt"))
        for al_tf in al_text_files:
            print(f"\n[1/5] Ingest Allegro text: {al_tf.name}")
            raw_offers = al.parse_html_lines_dump(al_tf)
            filtered = [r for r in raw_offers if al.is_resource_offer(r)]
            before = len(all_records)
            for rec in filtered:
                rid = rec.get("id", "")
                if rid and rid not in seen_ids:
                    rec["ingested_at"] = NOW_ISO
                    seen_ids.add(rid)
                    all_records.append(rec)
            added = len(all_records) - before
            ingest_sources.append(f"allegro-text:{al_tf.name}:{added}")
            print(f" {len(raw_offers)} raw → {added} new (deduped)")
    else:
        print(f"\n[1/5] Allegro dir not found: {al_search_dir} (skipping)")

    write_jsonl(all_records, ingested_path)
    print(f"\n[1/5] Ingest complete: {len(all_records)} records from {len(ingest_sources)} sources → {ingested_path}")

    print(f"\n[2/5] Categorize...")
    categorized = [categorize_record(r) for r in all_records]
    categories: dict[str, int] = {}
    for r in categorized:
        c = r.get("scout_category", "inne")
        categories[c] = categories.get(c, 0) + 1
    print(f" {len(categorized)} records → {len(categories)} categories")
    for cat, cnt in sorted(categories.items()):
        print(f" {cat}: {cnt}")

    print(f"\n[3/5] Assess...")
    assessed = [assess_potential(r) for r in categorized]
    supply = [r for r in assessed if r.get("scout_signal_type") == "supply"]
    demand = [r for r in assessed if r.get("scout_signal_type") == "demand"]
    tiers: dict[str, int] = {}
    for r in assessed:
        t = r.get("scout_tier", "?")
        tiers[t] = tiers.get(t, 0) + 1
    print(f" supply: {len(supply)}, demand: {len(demand)}")
    for tier, cnt in sorted(tiers.items()):
        print(f" {tier}: {cnt}")

    print(f"\n[4/5] Match...")
    matches = match_signals(supply, demand)
    priorities = [m for m in matches if m["recommendation"] == "PRIORYTET"]
    consider = [m for m in matches if m["recommendation"] == "ROZWAZ"]
    weak = [m for m in matches if m["recommendation"] == "SLABY"]
    print(f" {len(matches)} matches: PRIORYTET={len(priorities)}, ROZWAZ={len(consider)}, SLABY={len(weak)}")

    print(f"\n[5/5] Export...")
    receipt = {
        "receipt_type": "resource_scouting_58_multi_source",
        "generated_at": NOW_ISO,
        "ingest_sources": ingest_sources,
        "summary": {
            "total_records": len(assessed),
            "supply_signals": len(supply),
            "demand_signals": len(demand),
            "matches_total": len(matches),
            "matches_priority": len(priorities),
            "matches_consider": len(consider),
            "matches_weak": len(weak),
            "categories": categories,
            "tiers": tiers,
        },
        "top_matches": matches[:10],
        "blockers": [
            "Facebook API wymaga FB_ACCESS_TOKEN (obecnie dziala na JSONL/text fixture)",
            "Allegro Lokalnie API wymaga ALLEGRO_API_KEY (obecnie dziala na JSONL/text fixture)",
            "Punktacja matchingu heurystyczna (30/30/25/15) — wymaga kalibracji na realnych danych",
        ],
        "next_steps": [
            "Uzupelnic FB fixture o realne posty z grup (kopie z Graph API lub recznie)",
            "Podpiac wyniki pod bota Telegram (zadanie 59)",
            "Import scouting results to D1 SQLite (zadanie 60)",
            "Kalibracja punktacji na wiekszym zbiorze danych",
        ],
    }
    receipt_path = output_dir / f"resource_scouting_receipt_58_{TODAY_STR}.json"
    with open(receipt_path, "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=2)
    print(f" Receipt: {receipt_path}")

    assessed_path = output_dir / f"scout_assessed_58_{TODAY_STR}.jsonl"
    write_jsonl(assessed, assessed_path)
    print(f" Assessed: {assessed_path}")

    matches_path = output_dir / f"scout_matches_58_{TODAY_STR}.jsonl"
    write_jsonl(matches, matches_path)
    print(f" Matches: {matches_path}")

    print(f"\n{'=' * 60}")
    print(f"MULTI-SOURCE PIPELINE COMPLETE")
    print(f" Ingest: {len(all_records)} records from {len(ingest_sources)} sources")
    print(f" Categories: {categories}")
    print(f" Matches: {len(matches)} (PRIORYTET={len(priorities)}, ROZWAZ={len(consider)})")
    print(f"{'=' * 60}")

    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Resource signal scouting and matching engine (Project 15)",
    )
    sub = parser.add_subparsers(dest="command")

    ing_sql_p = sub.add_parser("ingest-olx-sql", help="Parsuj OLX SQL dump do scouting JSONL")
    ing_sql_p.add_argument("--sql", type=Path, required=True)
    ing_sql_p.add_argument("--output", type=Path, required=True)

    ing_man_p = sub.add_parser("ingest-manual", help="Ingestia recznych sygnalow (Facebook, grupy)")
    ing_man_p.add_argument("--source", type=Path, required=True)
    ing_man_p.add_argument("--output", type=Path)

    ing_jsonl_p = sub.add_parser("ingest-olx-jsonl", help="Parsuj OLX JSONL export do scouting JSONL")
    ing_jsonl_p.add_argument("--jsonl", type=Path, required=True)
    ing_jsonl_p.add_argument("--output", type=Path, required=True)

    pipe_p = sub.add_parser("ingest-pipeline", help="Pelny pipeline: ingest→categorize→assess→match→export")
    pipe_p.add_argument("--source-dir", type=Path, required=True)
    pipe_p.add_argument("--output-dir", type=Path)

    ing_fb_p = sub.add_parser("ingest-facebook", help="Ingest Facebook group posts (JSONL export)")
    ing_fb_p.add_argument("--jsonl", type=Path, required=True)
    ing_fb_p.add_argument("--output", type=Path, required=True)

    ing_fb_txt_p = sub.add_parser("ingest-facebook-text", help="Ingest Facebook group posts (text dump)")
    ing_fb_txt_p.add_argument("--text", type=Path, required=True)
    ing_fb_txt_p.add_argument("--output", type=Path, required=True)

    ing_al_p = sub.add_parser("ingest-allegro", help="Ingest Allegro Lokalnie (JSONL export)")
    ing_al_p.add_argument("--jsonl", type=Path, required=True)
    ing_al_p.add_argument("--output", type=Path, required=True)

    ing_al_txt_p = sub.add_parser("ingest-allegro-text", help="Ingest Allegro Lokalnie (HTML-lines dump)")
    ing_al_txt_p.add_argument("--html-lines", type=Path, required=True)
    ing_al_txt_p.add_argument("--output", type=Path, required=True)

    all_p = sub.add_parser("ingest-all", help="Full multi-source pipeline: OLX+FB+Allegro+manual")
    all_p.add_argument("--source-dir", type=Path, required=True)
    all_p.add_argument("--fb-dir", type=Path)
    all_p.add_argument("--allegro-dir", type=Path)
    all_p.add_argument("--output-dir", type=Path)

    cat_p = sub.add_parser("categorize", help="Kategoryzuj sygnały wg słów kluczowych")
    cat_p.add_argument("--source", type=Path, default=FIXTURE_DIR / "olx_offers_export.jsonl")
    cat_p.add_argument("--output", type=Path)

    ass_p = sub.add_parser("assess", help="Oceń potencjał każdego sygnału")
    ass_p.add_argument("--source", type=Path, default=FIXTURE_DIR / "olx_offers_export.jsonl")
    ass_p.add_argument("--output", type=Path)

    mat_p = sub.add_parser("match", help="Dopasuj podaż do popytu")
    mat_p.add_argument("--supply", type=Path, default=FIXTURE_DIR / "olx_offers_export.jsonl")
    mat_p.add_argument("--demand", type=Path)
    mat_p.add_argument("--output", type=Path)

    exp_p = sub.add_parser("export", help="Pełny eksport z receiptem")
    exp_p.add_argument("--source", type=Path, default=FIXTURE_DIR / "olx_offers_export.jsonl")
    exp_p.add_argument("--output-dir", type=Path)

    args = parser.parse_args()

    if args.command == "ingest-olx-sql":
        cmd_ingest_olx_sql(args.sql, args.output)
    elif args.command == "ingest-manual":
        cmd_ingest_manual(args.source, args.output)
    elif args.command == "ingest-olx-jsonl":
        cmd_ingest_olx_jsonl(args.jsonl, args.output)
    elif args.command == "ingest-pipeline":
        cmd_ingest_pipeline(args.source_dir, args.output_dir)
    elif args.command == "ingest-facebook":
        cmd_ingest_facebook(args.jsonl, args.output)
    elif args.command == "ingest-facebook-text":
        cmd_ingest_facebook_text(args.text, args.output)
    elif args.command == "ingest-allegro":
        cmd_ingest_allegro(args.jsonl, args.output)
    elif args.command == "ingest-allegro-text":
        cmd_ingest_allegro_text(args.html_lines, args.output)
    elif args.command == "ingest-all":
        cmd_ingest_all(args.source_dir, args.fb_dir, args.allegro_dir, args.output_dir)
    elif args.command == "categorize":
        cmd_categorize(args.source, args.output)
    elif args.command == "assess":
        cmd_assess(args.source, args.output)
    elif args.command == "match":
        cmd_match(args.supply, args.demand, args.output)
    elif args.command == "export":
        cmd_export(args.source, args.output_dir)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()