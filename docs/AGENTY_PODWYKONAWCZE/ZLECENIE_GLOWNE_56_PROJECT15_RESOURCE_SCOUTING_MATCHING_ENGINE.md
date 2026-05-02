# Zlecenie Glowne 56 Project15 Resource Scouting Matching Engine

## 1. Misja zadania

Aktywowac warstwe resource scoutingu Project 15 — zbudowac silnik przetwarzania sygnalow z roznych zrodel (OLX, Allegro Lokalnie, grupy społecznościowe) i laczenia podazy (oddam/sprzedam tanio) z popytem (potrzebuje czesci/urzadzenia).

## 2. Wyzszy cel organizacji

Po commicie `f9f60f5` strategicznie resource scouting ma laczyc podaz, popyt, logistyke i koszt przejecia, a nie tylko katalogowac obiekty. Zadanie 56 otwiera Portfel 14 — pivot z zablokowanego canary/ESP na praktyczna warstwe scoutingu, ktora nie wymaga maintainera ani hardware.

## 3. Read First

- `docs/AGENTY_PODWYKONAWCZE/MINI_HANDOFF_ZADANIE_55.md` — rekomendacja pivotu
- `docs/HANDOFF_DLA_NASTEPNEGO_AGENTA_2026-04-30.md`
- `docs/HANDOFF_DLA_NASTEPNEGO_AGENTA_2026-04-29_PO_AUDYCIE_OPENCLAW.md`
- `PROJEKTY/15_analiza_social_media_recykling.md`
- `PROJEKTY/13_baza_czesci_recykling/olx-oddam-za-darmo-scraper.ipynb` — istniejacy wzorzec scrapowania OLX
- `PROJEKTY/13_baza_czesci_recykling/olx_data/olx_d1_import_smoke_z52.sql`

## 4. Write Scope

- `PROJEKTY/13_baza_czesci_recykling/scripts/scout_resource_signals.py` — NOWY skrypt silnika scoutingowego
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/resource_scouting_receipt_56_*.json`
- `docs/AGENTY_PODWYKONAWCZE/MINI_HANDOFF_ZADANIE_56.md`
- `PROJEKTY/15_analiza_social_media_recykling.md` — drobna aktualizacja statusu implementacji

## 5. Out Of Scope

- Nie scrapowac OLX na zywo (to robi notebook Kaggle)
- Nie wymagac GEMINI_API_KEY, kredensow OLX ani sekretow
- Nie ruszac canary/ESP/human review blockera (to juz udokumentowane w 46-55)
- Nie tworzyc nowego notebooka (skrypt ma isc jako modul do wykorzystania przez notebooki)

## 6. Deliverables

1. **`scout_resource_signals.py`** — skrypt CLI z komendami:
   - `categorize` — kategoryzacja sygnalow z JSONL OLX wg slow kluczowych (elektronika, AGD, czesci, materialy)
   - `assess` — ocena potencjalu kazdego sygnalu (cena=0 darmo, lokalizacja, typ)
   - `match` — laczenie podazy (offers) z popytem (wants) na podstawie slow kluczowych i lokalizacji
   - `export` — eksport wynikow jako JSONL + summary receipt
2. **Receipt** — z podsumowaniem: ile sygnalow, ile dopasowan, kategorie
3. **Mini-handoff**

## 7. Acceptance Criteria

- `python3 -m py_compile` skryptu przechodzi bez bledow
- Komenda `categorize` poprawnie dzieli sygnaly na kategorie
- Komenda `match` znajduje przynajmniej potencjalne pary podaz-popyt
- Skrypt dziala na fixture danych OLX (nie wymaga realnego scrapa)
- Zadne sekrety nie trafiaja do repo
- Receipt jest poprawnym JSON

## 8. Walidacja

- `python3 -m py_compile PROJEKTY/13_baza_czesci_recykling/scripts/scout_resource_signals.py`
- `python3 PROJEKTY/13_baza_czesci_recykling/scripts/scout_resource_signals.py --help`
- `python3 PROJEKTY/13_baza_czesci_recykling/scripts/scout_resource_signals.py categorize --source <fixture>`
- `python3 PROJEKTY/13_baza_czesci_recykling/scripts/scout_resource_signals.py match --supply <file> --demand <file>`
- `python3 -m json.tool <receipt>.json`

## 9. Blokery i eskalacja

- Jesli OLX nie ma danych fixture: wygeneruj syntetyczny fixture na podstawie znanych kategorii
- Nie probuj realnego API OLX bez sekretow
- Jesli brakuje informacji o lokalizacji: uzyj domyslnej lokalizacji Kłodzko (zgodnie z watchlistami OLX)

## 10. Mini-handoff

Na koniec agent zapisuje:
- co zmienil,
- jakie pliki dotknal,
- co zweryfikowal,
- co zostalo otwarte.