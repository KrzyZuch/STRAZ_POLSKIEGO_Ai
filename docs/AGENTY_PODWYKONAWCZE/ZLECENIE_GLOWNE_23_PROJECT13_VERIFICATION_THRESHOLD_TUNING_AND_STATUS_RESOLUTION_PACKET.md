# Zlecenie Glowne 23 Project13 Verification Threshold Tuning And Status Resolution Packet

## 1. Misja zadania

Domknij to, czego nie zamknelo samo triage z zadania `17`: popraw heurystyki albo jawny status resolution packet tak, zeby `threshold_tuning` nie wisial dalej jako problem opisany tylko w raporcie, a `likely_confirmed` mialy czytelna sciezke do review i promocji.

## 2. Wyzszy cel organizacji

To zadanie zamienia triage z dobrego raportu w stabilniejszy verified snapshot, na ktorym da sie uczciwie budowac curation i export.

## 3. Read First

- `docs/HANDOFF_DLA_NASTEPNEGO_AGENTA_2026-04-25.md`
- `docs/AGENTY_PODWYKONAWCZE/ODBIOR_PORTFELA_07_ZADAN_17_22_2026-04-25.md`
- `docs/AGENTY_PODWYKONAWCZE/MINI_HANDOFF_ZADANIE_17.md`
- `docs/AGENTY_PODWYKONAWCZE/MINI_HANDOFF_ZADANIE_18.md`
- `PROJEKTY/13_baza_czesci_recykling/scripts/verify_candidates.py`
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/verification_triage.jsonl`
- `PROJEKTY/13_baza_czesci_recykling/execution_packs/pack-project13-kaggle-verification-01/RUNBOOK.md`

## 4. Write Scope

- `PROJEKTY/13_baza_czesci_recykling/scripts/verify_candidates.py`
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/`
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/results/`
- `PROJEKTY/13_baza_czesci_recykling/execution_packs/pack-project13-kaggle-verification-01/`
- ewentualnie `PROJEKTY/13_baza_czesci_recykling/docs/`

## 5. Deliverables

- poprawione heurystyki albo jawny policy packet dla `threshold_tuning` i `likely_confirmed`
- odswiezony verification run albo review-ready resolution packet
- jawna lista rekordow, ktore po zmianach nadal zostaja `ocr_needed` albo `manual_review`
- mini-handoff z counts przed i po zmianie

## 6. Acceptance Criteria

- `threshold_tuning` nie pozostaje juz tylko rekomendacja w opisie, ale ma realny skutek w pipeline albo w review packetcie
- `likely_confirmed` ma czytelny, reviewowalny sposob promocji do `confirmed` albo jawnie opisany powod, czemu dalej nie mozna ich promowac
- po zmianie nadal nie jest ukrywane, ktore rekordy zalezne sa od OCR i manual review
- verification pack nie miesza swojej odpowiedzialnosci z finalnym exportem

## 7. Walidacja

- `python3 -m py_compile PROJEKTY/13_baza_czesci_recykling/scripts/verify_candidates.py` jesli skrypt byl zmieniany
- `python3 PROJEKTY/13_baza_czesci_recykling/scripts/verify_candidates.py dry-run`
- sensowny przebieg `report` albo `triage`
- `git diff --check`

## 8. Blokery

Jesli nie ma `GEMINI_API_KEY`, nie probuj sztucznie zamykac `ocr_needed`.
Dowiez stabilniejszy packet status resolution bez udawania, ze OCR jest juz wykonane.

## 9. Mini-handoff

Zapisz:

- jak zmienily sie counts `confirmed`, `disputed`, `rejected`,
- czy `threshold_tuning` zostalo realnie wyciszone przez heurystyki lub review packet,
- jaki jest nowy status `likely_confirmed`,
- co nadal blokuje czysty verified snapshot.
