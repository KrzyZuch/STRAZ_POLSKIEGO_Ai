# Zlecenie Glowne 58 Project15 Facebook Allegro Multi-Source Integration

## 1. Misja zadania

Zbudowac normalizery dla Facebook Groups i Allegro Lokalnie, ktore przyjmuja eksportowane dane (JSONL z FB Graph API / copy-paste, HTML scrap Allegro) i normalizuja je do scout schema uzywane przez silnik scoutingowy. Rozszerzyc pipeline o komendy `ingest-facebook` i `ingest-allegro`, dodac filtr non-resource do `ingest-pipeline` i przeprowadzic pelny run na rozszerzonych danych.

## 2. Wyzszy cel organizacji

Zadanie 57 podpielo OLX jako pierwsze zrodlo realnych danych. Zadanie 58 dodaje Facebook i Allegro Lokalnie — dwa najwazniejsze zrodla darmowych i tanich ofert w Polsce. Bez nich scouting jest niepelny, bo w grupach FB typu "Oddam za darmo" i "Smieciarka jedzie" jest wiecej darmowych ofert niz na OLX.

## 3. Read First

- `docs/AGENTY_PODWYKONAWCZE/MINI_HANDOFF_ZADANIE_57.md`
- `docs/AGENTY_PODWYKONAWCZE/MINI_HANDOFF_ZADANIE_56.md`
- `PROJEKTY/13_baza_czesci_recykling/scripts/scout_resource_signals.py`
- `PROJEKTY/13_baza_czesci_recykling/scripts/scout_ingest_olx.py`
- `PROJEKTY/13_baza_czesci_recykling/scout_data/signals_manual/README.md`

## 4. Write Scope

- `PROJEKTY/13_baza_czesci_recykling/scripts/scout_ingest_facebook.py` — NOWY
- `PROJEKTY/13_baza_czesci_recykling/scripts/scout_ingest_allegro_lokalnie.py` — NOWY
- `PROJEKTY/13_baza_czesci_recykling/scripts/scout_resource_signals.py` — ROZSZERZENIE
- `PROJEKTY/13_baza_czesci_recykling/scout_data/` — nowe fixture
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/resource_scouting_receipt_58_*.json`
- `docs/AGENTY_PODWYKONAWCZE/MINI_HANDOFF_ZADANIE_58.md`

## 5. Out Of Scope

- Nie scrapowac FB ani Allegro na zywo (wymaga sekretow, API keys, srodowiska Kaggle)
- Nie wymagac FB_ACCESS_TOKEN ani ALLEGRO_API_KEY
- Nie ruszac notebooka OLX ani D1 migracji
- Nie zmieniac canary/ESP blockera

## 6. Deliverables

1. **`scout_ingest_facebook.py`** — normalizer FB group posts do scout schema JSONL
   - Tryb `--jsonl` — parsowanie eksportu JSONL z FB Graph API / web scraper
   - Tryb `--text` — parsowanie copy-paste text dump z grup FB (heuristic)
   - Tryb `--auto` — auto-detect w katalogu
   - Filtrowanie non-resource (zwierzeta, adopcje)
   - Deduplikacja po ID
2. **`scout_ingest_allegro_lokalnie.py`** — normalizer Allegro Lokalnie do scout schema JSONL
   - Tryb `--jsonl` — parsowanie eksportu JSONL z API
   - Tryb `--html-lines` — parsowanie text dump z HTML (heuristic)
   - Tryb `--auto`
   - Filtrowanie non-resource
   - Deduplikacja po ID
3. **Komendy w `scout_resource_signals.py`**:
   - `ingest-facebook` — uruchomienie normalizera FB
   - `ingest-allegro` — uruchomienie normalizera Allegro
   - `ingest-all` — pelny multi-source pipeline: OLX + FB + Allegro + manual → categorize → assess → match → export
4. **Filtr `is_resource_offer`** przeniesiony z `scout_ingest_olx.py` do `ingest-pipeline`
5. **Realistyczne fixture** FB i Allegro (po 10+ rekordow kazde)
6. **Receipt z pelnym runem** — 58_pipeline
7. **Mini-handoff**

## 7. Acceptance Criteria

- `python3 -m py_compile` przechodzi dla 3 skryptow
- `scout_ingest_facebook.py --jsonl` normalizuje rekordy FB do scout schema
- `scout_ingest_facebook.py --text` parsuje text dump z grup FB
- `scout_ingest_allegro_lokalnie.py --jsonl` normalizuje rekordy Allegro
- `ingest-all` laczy wszystkie zrodla z deduplikacja
- Filtr non-resource dziala w `ingest-pipeline` i `ingest-all`
- Zadne sekrety nie trafiaja do repo
- Receipt jest poprawnym JSON

## 8. Walidacja

- `python3 -m py_compile scout_ingest_facebook.py`
- `python3 -m py_compile scout_ingest_allegro_lokalnie.py`
- `python3 -m py_compile scout_resource_signals.py`
- `python3 scout_ingest_facebook.py --jsonl <fixture> --output /tmp/test_fb.jsonl`
- `python3 scout_ingest_facebook.py --text <text_fixture> --output /tmp/test_fb_text.jsonl`
- `python3 scout_ingest_allegro_lokalnie.py --jsonl <fixture> --output /tmp/test_al.jsonl`
- `python3 scout_resource_signals.py ingest-all --source-dir olx_data --fb-dir scout_data/facebook --allegro-dir scout_data/allegro_lokalnie`
- `python3 -m json.tool <receipt>.json`
- `git diff --check`

## 9. Blokery i eskalacja

- Jesli FB JSONL eksport ma inna strukture niz oczekiwana: dostosowac mapping do faktycznego formatu
- Jesli text dump z FB jest zbyt nieustrukturyzowany: ograniczyc parsowanie do heuristic extraction (title, description, cena, lokalizacja) i zapisac blocker dla API integracji
- Nie probowac zywego API FB/Allegro bez sekretow
- Jesli brakuje danych GPS: uzyc domyslnej lokalizacji Kłodzko

## 10. Mini-handoff

Na koniec agent zapisuje:
- co zmienil,
- jakie pliki dotknal,
- co zweryfikowal,
- co zostalo otwarte.
