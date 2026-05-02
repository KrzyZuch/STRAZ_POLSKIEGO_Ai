# Zlecenie Glowne 57 Project15 OLX Data Bridge and Multi-Source Ingest

## 1. Misja zadania

Zbudowac most pomiedzy istniejacym scraperem OLX (notebook Kaggle → SQLite → SQL import) a silnikiem scoutingowym ze zadania 56. Realne dane z smoke SQL z zadania 52 musza byc znormalizowane do formatu scoutingu i przepuszczone przez pelny pipeline: ingest → categorize → assess → match → export. Dodatkowo: szablon dla recznych sygnalow z grup Facebook.

## 2. Wyzszy cel organizacji

Zadanie 56 zbudowalo silnik, ale dziala na syntetycznym fixture. Zadanie 57 podpina realne dane — pierwszy sensowny run scoutingowy na prawdziwych ogloszeniach z regionu Klodzka. To kluczowy krok w aktywacji Project 15 jako warstwy resource scoutingu.

## 3. Read First

- `docs/AGENTY_PODWYKONAWCZE/MINI_HANDOFF_ZADANIE_56.md`
- `docs/AGENTY_PODWYKONAWCZE/MINI_HANDOFF_ZADANIE_52.md` (jesli istnieje)
- `PROJEKTY/13_baza_czesci_recykling/scripts/scout_resource_signals.py`
- `PROJEKTY/13_baza_czesci_recykling/olx_data/olx_d1_import_smoke_z52.sql`
- `PROJEKTY/13_baza_czesci_recykling/olx-oddam-za-darmo-scraper.ipynb` (struktura SQLite)

## 4. Write Scope

- `PROJEKTY/13_baza_czesci_recykling/scripts/scout_resource_signals.py` — dodanie komend `ingest-olx-sql` i `ingest-manual`
- `PROJEKTY/13_baza_czesci_recykling/olx_data/olx_offers_scout_normalized.jsonl` — znormalizowane realne dane
- `PROJEKTY/13_baza_czesci_recykling/olx_data/social_signals_template.jsonl` — szablon dla recznych sygnalow
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/resource_scouting_receipt_57_*.json`
- `docs/AGENTY_PODWYKONAWCZE/MINI_HANDOFF_ZADANIE_57.md`

## 5. Out Of Scope

- Nie scrapowac OLX na zywo
- Nie wymagac GEMINI_API_KEY ani sekretow
- Nie ruszac notebooka OLX ani D1 migracji
- Nie zmieniac canary/ESP blockera

## 6. Deliverables

1. **Komenda `ingest-olx-sql`** w scout_resource_signals.py — parsowanie INSERT statements z SQL dumpu OLX do scouting JSONL
2. **Komenda `ingest-manual`** — ingestia z szablonu recznych sygnalow (Facebook, grupy, telefonicznie)
3. **Szablon `social_signals_template.jsonl`** — przykladowe rekordy z grup "Oddam za darmo", "Smieciarka jedzie"
4. **Realny scouting receipt** — pelny pipeline na znormalizowanych realnych danych z smoke SQL
5. **Mini-handoff**

## 7. Acceptance Criteria

- `python3 -m py_compile` przechodzi
- `ingest-olx-sql` poprawnie parsuje INSERT statements do JSONL
- Znormalizowane dane z smoke SQL przechodza przez categorize/assess/match/export
- Szablon recznych sygnalow jest czytelny i ma przykladowe dane
- Zadne sekrety nie trafiaja do repo
- Receipt jest poprawnym JSON

## 8. Walidacja

- `python3 -m py_compile scout_resource_signals.py`
- `python3 scout_resource_signals.py ingest-olx-sql --sql olx_d1_import_smoke_z52.sql --output olx_offers_scout_normalized.jsonl`
- `python3 scout_resource_signals.py categorize --source olx_offers_scout_normalized.jsonl`
- `python3 scout_resource_signals.py export --source olx_offers_scout_normalized.jsonl`
- `python3 scout_resource_signals.py ingest-manual --source social_signals_template.jsonl`
- `python3 -m json.tool <receipt>.json`
- `git diff --check`

## 9. Blokery i eskalacja

- Jesli SQL dump ma niekompatybilny format: dostosowac parser do faktycznej struktury INSERT
- Nie probowac polaczenia z baza D1 bez sekretow
- Jesli znormalizowane dane sa zbyt malo (tylko 5 rekordow w smoke): uruchomic tez na fixture z zadania 56

## 10. Mini-handoff

Na koniec agent zapisuje:
- co zmienil,
- jakie pliki dotknal,
- co zweryfikowal,
- co zostalo otwarte.