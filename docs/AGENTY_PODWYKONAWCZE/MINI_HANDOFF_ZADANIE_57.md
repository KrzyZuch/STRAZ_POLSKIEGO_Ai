# Mini-Handoff ZADANIE 57

## Co zostalo zrobione

1. **Stworzono `scout_ingest_olx.py`** — samodzielny skrypt normalizujacy OLX SQL dump i JSONL export do scout schema JSONL
   - `--sql` — parsowanie INSERT statements z tymczasowym SQLite in-memory
   - `--jsonl` — parsowanie JSONL exportu z notebooka Kaggle
   - `--auto` — auto-detect SQL i JSONL w katalogu zrodlowym
   - Filtrowanie non-resource (zwierzeta, adopcje) — domyslnie wlaczone, `--no-filter` wylacza
   - Deduplikacja po ID w trybie `--auto`
   - Walidacja scout schema i receipt JSON
2. **Rozszerzono `scout_resource_signals.py`** o 2 nowe komendy:
   - `ingest-olx-jsonl` — ingest JSONL exportu OLX z normalizacja do scout schema
   - `ingest-pipeline` — pelny pipeline 5-stopniowy: ingest → categorize → assess → match → export
     - Automatycznie szuka SQL + JSONL w `--source-dir`
     - Automatycznie szuka szablonow manualnych w `scout_data/signals_manual/template_*.jsonl`
     - Deduplikacja po ID, receipt z lista zrodel i statystykami
3. **Stworzono strukture szablonow manualnych** — `scout_data/signals_manual/`:
   - `template_facebook_group.jsonl` — 5 rekordow (oddam laptop, pralka, szukam zasilacza, drewno paletowe, szukam ESP32)
   - `template_allegro_lokalnie.jsonl` — 3 rekordy (ThinkPad T430, zestaw narzedzi, drukarka HP)
   - `template_community_post.jsonl` — 3 rekordy (szukam transformatora, oddam CD/kable, szukam blachy)
   - `README.md` — instrukcja uzupelniania szablonow z dokumentacja schematu
4. **Uruchomiono pipeline na realnych danych** — 24 records z 6 zrodel:
   - SQL: 6 raw → 6 normalized (4 resource po odfiltrowaniu zwierzat w scout_ingest_olx.py; pipeline nie filtruje zwierzat)
   - JSONL: 7 existing fixture records + 0 new (dedup z SQL)
   - Manual: 11 records (5 FB + 3 Allegro + 3 community)
   - Wynik: 57 matches (26 PRIORYTET, 31 ROZWAZ, 0 SLABY)
   - Kategorii: 5 (elektronika=15, inne=4, agd=2, materialy=2, narzedzia=1)
   - Tier: 13 tier1_free, 7 demand_signal, 3 tier2_cheap, 1 tier3_review
5. **Stworzono receipt pipeline** — `resource_scouting_receipt_57_20260502-130738.json`

## Jakie pliki zmieniono / stworzono

- `PROJEKTY/13_baza_czesci_recykling/scripts/scout_ingest_olx.py` — NOWY
- `PROJEKTY/13_baza_czesci_recykling/scripts/scout_resource_signals.py` — ROZSZERZONY (ingest-olx-jsonl, ingest-pipeline, normalize_olx_jsonl_record)
- `PROJEKTY/13_baza_czesci_recykling/scout_data/signals_manual/template_facebook_group.jsonl` — NOWY
- `PROJEKTY/13_baza_czesci_recykling/scout_data/signals_manual/template_allegro_lokalnie.jsonl` — NOWY
- `PROJEKTY/13_baza_czesci_recykling/scout_data/signals_manual/template_community_post.jsonl` — NOWY
- `PROJEKTY/13_baza_czesci_recykling/scout_data/signals_manual/README.md` — NOWY
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/resource_scouting_receipt_57_20260502-130738.json` — NOWY
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/scout_assessed_57_20260502-130738.jsonl` — NOWY
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/scout_matches_57_20260502-130738.jsonl` — NOWY
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/scout_ingested_57_20260502-130738.jsonl` — NOWY
- `docs/AGENTY_PODWYKONAWCZE/ZLECENIE_GLOWNE_57_PROJECT15_OLX_BRIDGE_MULTI_SOURCE_INGESTION.md` — NOWY
- `docs/AGENTY_PODWYKONAWCZE/MINI_HANDOFF_ZADANIE_57.md` — ten plik

## Jakie komendy walidacyjne przeszly

- `python3 -m py_compile scout_ingest_olx.py` — PASS
- `python3 -m py_compile scout_resource_signals.py` — PASS
- `python3 scout_ingest_olx.py --sql olx_d1_import_smoke_z52.sql --output /tmp/test.jsonl` — PASS (6 raw, 4 resource after filter)
- `python3 scout_ingest_olx.py --auto --source-dir olx_data --output /tmp/test.jsonl` — PASS (11 records, 3 sources, 4 deduped)
- `python3 scout_resource_signals.py ingest-pipeline --source-dir olx_data` — PASS (24 records, 57 matches)
- `python3 scout_resource_signals.py ingest-olx-sql --sql ... --output ...` — PASS
- `python3 scout_resource_signals.py ingest-manual --source template_facebook_group.jsonl --output ...` — PASS
- `python3 -m json.tool resource_scouting_receipt_57_*.json` — PASS
- `python3 -m json.tool` na wszystkich JSONL (24+24+57 valid records) — PASS
- `git diff --check` — PASS (no whitespace errors)

## Otwarte ryzyka / blokery

1. **Dane OLX ograniczone do SQL dump (6 ofert) + fixture** — pelny scrap wymaga uruchomienia notebooka Kaggle z internetem ON
2. **Pipeline nie filtruje zwierzat/adopcji** — `scout_ingest_olx.py` samodzielnie filtruje, ale `ingest-pipeline` w `scout_resource_signals.py` nie ma tej logiki (kocurek i pieski trafiaja do kategorii `inne`)
3. **Szablony manualne sa przykladowe** — realne sygnaly z FB/Allegro musza byc wprowadzone recznie lub przez API (zadanie 58)
4. **Punktacja matchingu heurystyczna** — wysoki odsetek PRIORYTET (26/57) sugeruje ze wagi moga byc zbyt wysokie dla tier1_free
5. **Brak integracji z botem Telegram** — matching nie jest podpiety pod powiadomienia (zadanie 59)
6. **Brak D1 import** — wyniki scoutingu nie sa importowane do bazy Cloudflare D1 (zadanie 60)

## Co powinien zrobic kolejny wykonawca

1. **Zadanie 58**: Dodac realne zrodla — Facebook Marketplace API, automatyczne pobieranie z grup FB, integracja Allegro Lokalnie
2. **Zadanie 59**: Podpiac wyniki matchingu pod bota Telegram — powiadomienia o nowych dopasowaniach PRIORYTET
3. **Zadanie 60**: Zintegrowac scouting z D1 SQLite dla query endpointu
4. **Kalibracja punktacji**: Przejrzec wagi matchingu (30/30/25/15) na realnych danych z pelnego scrapa OLX
5. **Dodac filtrowanie non-resource do ingest-pipeline**: Przeniesc logike `is_resource_offer` z `scout_ingest_olx.py` do `scout_resource_signals.py`

## Portfel 14 — status

| ID | Cel | Status |
|----|-----|--------|
| 56 | Silnik scoutingowy i matching | WYKONANE |
| 57 | OLX→scout bridge + multi-source ingestion + manual templates | WYKONANE |
| 58 | Integracja Facebook/Inne zrodla | OPEN |
| 59 | Integracja z botem Telegram (powiadomienia) | OPEN |
| 60 | D1 import i query endpoint dla scoutingu | OPEN |
