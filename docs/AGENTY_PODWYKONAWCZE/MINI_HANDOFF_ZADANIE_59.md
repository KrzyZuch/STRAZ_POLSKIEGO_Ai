# Mini-Handoff ZADANIE 59

## Co zostalo zrobione

1. **Stworzono `scout_ingest_facebook.py`** — normalizer Facebook group posts do scout schema JSONL
- `--jsonl` — parsowanie eksportu JSONL z FB Graph API / web scraper
- `--text` — parsowanie copy-paste text dump z grup FB (heuristic: `---` separator, Grupa: header, title/desc extraction, price regex, city lookup)
- `--auto` — auto-detect JSONL + TXT w katalogu zrodlowym
- Filtrowanie non-resource (zwierzeta, adopcje) — domyslnie wlaczone, `--no-filter` wylacza
- Deduplikacja po ID w trybie `--auto`
- Walidacja scout schema i receipt JSON
- Resolution city→coords dla 8 miast ziemi kłodzkiej
- Obsluga roznych wariantow pol FB JSONL (price/price_value, city/city_name, contact/contact_method, message/description)

2. **Stworzono `scout_ingest_allegro_lokalnie.py`** — normalizer Allegro Lokalnie do scout schema JSONL
- `--jsonl` — parsowanie eksportu JSONL z API
- `--html-lines` — parsowanie text dump z HTML (heuristic: `[Ogloszenie N]` header, `---` separator, title/desc/price extraction, city lookup)
- `--auto` — auto-detect JSONL + TXT w katalogu zrodlowym
- Filtrowanie non-resource + deduplikacja po ID
- Obsluga pol Allegro JSONL (category, condition, seller, url)

3. **Naprawiono `scout_resource_signals.py`** — fix indentation (tabs→spaces, 1-space→4-space indent)
- Komendy `ingest-facebook`, `ingest-facebook-text`, `ingest-allegro`, `ingest-allegro-text`, `ingest-all` byly juz zaimplementowane w zadaniu 58 ale mialy bledy indentacji (tab zamiast spaces, 1-space indent zamiast 4)
- Po naprawie: `py_compile` przechodzi bez bledow
- Komendy poprawnie laduja moduly `scout_ingest_facebook` i `scout_ingest_allegro_lokalnie` przez `importlib`

4. **Uruchomiono pelny pipeline `ingest-all`** — 58 records z 10 zrodel:
- OLX SQL: 6 raw → 4 normalized (filtered non-resource)
- OLX JSONL: 7 fixture + 0 new (dedup)
- Manual templates: 11 records (5 FB + 3 Allegro + 3 community)
- Facebook JSONL: 12 new (fb-101..fb-112)
- Facebook text: 7 new (fb-txt-*)
- Allegro JSONL: 12 new (al-101..al-112)
- Allegro text: 5 new (al-txt-*)
- Wynik: 286 matches (131 PRIORYTET, 150 ROZWAZ, 5 SLABY)
- Kategorii: 6 (elektronika=35, inne=11, narzedzia=5, agd=3, materialy=3, pojazdy=1)
- Tier: 25 tier1_free, 15 tier2_cheap, 13 demand_signal, 5 tier3_review

5. **Stworzono receipt pipeline** — `resource_scouting_receipt_58_20260502-202329.json`

## Jakie pliki zmieniono / stworzono

- `PROJEKTY/13_baza_czesci_recykling/scripts/scout_ingest_facebook.py` — NOWY
- `PROJEKTY/13_baza_czesci_recykling/scripts/scout_ingest_allegro_lokalnie.py` — NOWY
- `PROJEKTY/13_baza_czesci_recykling/scripts/scout_resource_signals.py` — NAPRAWIONY (tabs→spaces, 1-space→4-space indent)
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/resource_scouting_receipt_58_20260502-202329.json` — NOWY
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/scout_assessed_58_20260502-202329.jsonl` — NOWY
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/scout_matches_58_20260502-202329.jsonl` — NOWY
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/scout_ingested_58_20260502-202329.jsonl` — NOWY
- `docs/AGENTY_PODWYKONAWCZE/MINI_HANDOFF_ZADANIE_59.md` — ten plik

## Jakie komendy walidacyjne przeszly

- `python3 -m py_compile scout_ingest_facebook.py` — PASS
- `python3 -m py_compile scout_ingest_allegro_lokalnie.py` — PASS
- `python3 -m py_compile scout_resource_signals.py` — PASS
- `python3 scout_ingest_facebook.py --jsonl fb_group_posts_klodzko.jsonl --output /tmp/test_fb.jsonl` — PASS (12 records)
- `python3 scout_ingest_facebook.py --text fb_group_posts_text_dump.txt --output /tmp/test_fb_text.jsonl` — PASS (7 posts)
- `python3 scout_ingest_allegro_lokalnie.py --jsonl allegro_lokalnie_klodzko.jsonl --output /tmp/test_al.jsonl` — PASS (12 records)
- `python3 scout_ingest_allegro_lokalnie.py --html-lines allegro_lokalnie_html_dump.txt --output /tmp/test_al_text.jsonl` — PASS (5 offers)
- `python3 scout_ingest_facebook.py --auto --source-dir scout_data/facebook --output /tmp/test_fb_auto.jsonl` — PASS (19 records: 12 JSONL + 7 text)
- `python3 scout_resource_signals.py ingest-facebook --jsonl ... --output ...` — PASS
- `python3 scout_resource_signals.py ingest-allegro --jsonl ... --output ...` — PASS
- `python3 scout_resource_signals.py ingest-all --source-dir olx_data --fb-dir scout_data/facebook --allegro-dir scout_data/allegro_lokalnie` — PASS (58 records, 286 matches)
- `python3 -m json.tool resource_scouting_receipt_58_*.json` — PASS
- `python3 -m json.tool` na ingested JSONL (58 records) — PASS
- No secrets in output — PASS
- `git diff --check` — PASS (no whitespace errors)

## Otwarte ryzyka / blokery

1. **FB JSONL fixture ma niespojne pole price** — niektore rekordy uzywaja `price`/`price_text` zamiast `price_value`/`price_label` (fb-102, fb-110) — normalizer obsluguje oba warianty, ale przyszle API eksporty moga miec inna strukture
2. **Text dump heuristic ograniczona** — parsowanie textowe FB/Allegro opiera sie na `---` separatorach, brak gwarancji ze realne zrzuty beda w tym formacie
3. **Wysoki odsetek PRIORYTET (131/286)** — sugeruje ze wagi matchingu (30/30/25/15) moga byc zbyt wysokie dla tier1_free
4. **Brak integracji z botem Telegram** — matching nie jest podpiety pod powiadomienia (zadanie 59 w numeracji MINI_HANDOFF_ZADANIE_57)
5. **Brak D1 import** — wyniki scoutingu nie sa importowane do bazy Cloudflare D1
6. **Filtr non-resource w `ingest-pipeline` (zadanie 57) nie obsluguje FB/Allegro pol** — filtr w `scout_resource_signals.py` sprawdza `title` + `description`, ale FB rekordy moga miec `message` zamiast `description`

## Co powinien zrobic kolejny wykonawca

1. **Zadanie 59 (Telegram bot)**: Podpiac wyniki matchingu pod bota Telegram — powiadomienia o nowych dopasowaniach PRIORYTET
2. **Zadanie 60 (D1 import)**: Zintegrowac scouting z D1 SQLite dla query endpointu
3. **Kalibracja punktacji**: Przejrzec wagi matchingu (30/30/25/15) na realnych danych z pelnego scrapa OLX — obecnie 46% PRIORYTET to za duzo
4. **Ujednolicenie pol FB**: Wybrac kanoniczny format JSONL (price_value/price_label vs price/price_text) w fixture i docelowym API
5. **Dodac `is_resource_offer` do ingest-pipeline**: Przeniesc logike filtrowania z modulow FB/AL do glownego pipeline zeby dzialala na polach `message` FB

## Portfel 14 — status

| ID | Cel | Status |
|----|-----|--------|
| 56 | Silnik scoutingowy i matching | WYKONANE |
| 57 | OLX→scout bridge + multi-source ingestion + manual templates | WYKONANE |
| 58 | Integracja Facebook/Allegro (normalizery + ingest-all) | WYKONANE |
| 59 | Integracja z botem Telegram (powiadomienia) | OPEN |
| 60 | D1 import i query endpoint dla scoutingu | OPEN |
