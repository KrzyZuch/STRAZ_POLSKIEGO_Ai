# Zlecenie Glowne 57 — Project15 OLX→Scout Bridge + Multi-Source Ingestion + Manual Signal Templates

## 1. Cel wykonawczy

Zbudowac most (bridge) miedzy danymi OLX (SQL dump / JSONL export z notebooka Kaggle) a silnikiem scoutingowym `scout_resource_signals.py`, dodac komendy ingest pipeline do istniejacego silnika, oraz stworzyc strukture szablonow dla recznie wprowadzanych sygnalow (Facebook groups, Allegro Lokalnie, posty spolecznosciowe).

## 2. Wyzszy cel organizacji

Zadanie 57 kontynuuje Portfel 14 — pivot z zablokowanego canary/ESP na praktyczna warstwe scoutingu. Zadanie 56 zbudowalo silnik, ale dziala on na fixture. Zadanie 57 laczy realne dane OLX (z SQL dump i JSONL) ze silnikiem, tworzy pipeline ingest→categorize→assess→match→export, i przygotowuje strukture dla sygnalow z innych zrodel.

## 3. Read First

- `docs/AGENTY_PODWYKONAWCZE/MINI_HANDOFF_ZADANIE_56.md` — wyniki zadania 56, plan Portfela 14
- `docs/AGENTY_PODWYKONAWCZE/INSTRUKCJA_DLA_AGENTA_PODWYKONAWCZEGO.md`
- `PROJEKTY/13_baza_czesci_recykling/scripts/scout_resource_signals.py` — istniejacy silnik scoutingowy
- `PROJEKTY/13_baza_czesci_recykling/olx_data/olx_d1_import_smoke_z52.sql` — SQL dump z realnymi danymi OLX
- `PROJEKTY/13_baza_czesci_recykling/olx-oddam-za-darmo-scraper.ipynb` — wzorzec OLX scraper

## 4. Write Scope

- `PROJEKTY/13_baza_czesci_recykling/scripts/scout_ingest_olx.py` — NOWY: samodzielny skrypt normalizujacy OLX SQL/JSONL do scout JSONL
- `PROJEKTY/13_baza_czesci_recykling/scripts/scout_resource_signals.py` — ROZSZERZENIE: dodanie komendy `ingest-pipeline` i `ingest-olx-jsonl`
- `PROJEKTY/13_baza_czesci_recykling/scout_data/signals_manual/` — NOWY: katalog z szablonami sygnalow manualnych
- `PROJEKTY/13_baza_czesci_recykling/scout_data/signals_manual/template_facebook_group.jsonl` — NOWY: szablon sygnalow z grup FB
- `PROJEKTY/13_baza_czesci_recykling/scout_data/signals_manual/template_allegro_lokalnie.jsonl` — NOWY: szablon sygnalow Allegro
- `PROJEKTY/13_baza_czesci_recykling/scout_data/signals_manual/template_community_post.jsonl` — NOWY: szablon postow spolecznosciowych
- `PROJEKTY/13_baza_czesci_recykling/scout_data/signals_manual/README.md` — NOWY: instrukcja uzupelniania szablonow
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/resource_scouting_receipt_57_*.json` — NOWY: receipt z pipeline
- `docs/AGENTY_PODWYKONAWCZE/ZLECENIE_GLOWNE_57_*.md` — ten plik
- `docs/AGENTY_PODWYKONAWCZE/MINI_HANDOFF_ZADANIE_57.md` — NOWY: mini-handoff
- `PROJEKTY/15_analiza_social_media_recykling.md` — aktualizacja statusu

## 5. Out Of Scope

- Nie scrapowac OLX na zywo (to robi notebook Kaggle)
- Nie tworzyc nowego notebooka Kaggle
- Nie integrowac z Facebook API (tylko szablon)
- Nie integrowac z Allegro API (tylko szablon)
- Nie ruszac canary/ESP/hardware blockera
- Nie wymagac sekretow API ani kredensow

## 6. Deliverables

1. **`scout_ingest_olx.py`** — samodzielny skrypt normalizujacy:
   - Odczytuje OLX SQL dump (INSERT statements) do tymczasowego SQLite
   - Odczytuje OLX JSONL export (z notebooka Kaggle)
   - Normalizuje do ujednoliconego scout JSONL schema
   - Waliduje strukture i raportuje statystyki
2. **Rozszerzenie `scout_resource_signals.py`** — nowe komendy:
   - `ingest-olx-jsonl` — ingest JSONL exportu OLX
   - `ingest-pipeline` — pelny pipeline: ingest → categorize → assess → match → export
3. **Szablony sygnalow manualnych** — 3 pliki JSONL template + README:
   - `template_facebook_group.jsonl` — struktura dla postow z grup FB
   - `template_allegro_lokalnie.jsonl` — struktura dla ogloszen Allegro
   - `template_community_post.jsonl` — struktura dla postow spolecznosciowych
4. **Receipt z pipeline** — wynik uruchomienia pipeline na realnych danych SQL
5. **Mini-handoff**

## 7. Acceptance Criteria

- `python3 -m py_compile` obu skryptow przechodzi bez bledow
- `scout_ingest_olx.py` poprawnie parsuje `olx_d1_import_smoke_z52.sql` i generuje JSONL
- `scout_ingest_olx.py` poprawnie parsuje JSONL (z fixture lub realnych danych)
- `scout_resource_signals.py ingest-pipeline` uruchamia caly pipeline na realnych danych SQL
- Szablony manualne sa poprawnym JSONL z przykladowymi rekordami
- Zadne sekrety nie trafiaja do repo
- Receipt jest poprawnym JSON
- `git diff --check` przechodzi bez bledow whitespace

## 8. Walidacja

- `python3 -m py_compile PROJEKTY/13_baza_czesci_recykling/scripts/scout_ingest_olx.py`
- `python3 -m py_compile PROJEKTY/13_baza_czesci_recykling/scripts/scout_resource_signals.py`
- `python3 PROJEKTY/13_baza_czesci_recykling/scripts/scout_ingest_olx.py --sql PROJEKTY/13_baza_czesci_recykling/olx_data/olx_d1_import_smoke_z52.sql --output /tmp/scout_ingest_test.jsonl`
- `python3 PROJEKTY/13_baza_czesci_recykling/scripts/scout_ingest_olx.py --jsonl <input.jsonl> --output /tmp/scout_ingest_test2.jsonl`
- `python3 PROJEKTY/13_baza_czesci_recykling/scripts/scout_resource_signals.py ingest-pipeline --source-dir PROJEKTY/13_baza_czesci_recykling/olx_data`
- `python3 -m json.tool PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/resource_scouting_receipt_57_*.json`
- `python3 -m json.tool PROJEKTY/13_baza_czesci_recykling/scout_data/signals_manual/template_facebook_group.jsonl` (line by line)
- `git diff --check`

## 9. Blokery i eskalacja

- Jesli SQL dump ma niekompatybilna strukture: dostosowac schema w `parse_olx_sql_inserts` (juz istnieje w zadaniu 56)
- Jesli JSONL export z notebooka nie istnieje: uzyc SQL dump jako jedynego zrodla, JSONL obsluga jako opcjonalna
- Nie probowac realnego API OLX bez sekretow
- Jesli pipeline nie znajdzie dopasowan na realnych danych (malo rekordow): odnotowac w receipt, nie sztucznie zawyzac wynikow

## 10. Mini-handoff

Na koniec agent zapisuje:
- co zmienil,
- jakie pliki dotknal,
- co zweryfikowal,
- co zostalo otwarte.
