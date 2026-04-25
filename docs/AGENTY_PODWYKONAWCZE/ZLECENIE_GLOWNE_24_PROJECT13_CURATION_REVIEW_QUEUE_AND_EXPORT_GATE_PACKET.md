# Zlecenie Glowne 24 Project13 Curation Review Queue And Export Gate Packet

## 1. Misja zadania

Na bazie wynikow `18` i najlepiej `23` przygotuj review-ready packet dla curation i exportu: jawna kolejka review, jawny export gate i czytelna odpowiedz, co jeszcze musi sie wydarzyc, zanim `build_catalog_artifacts.py export-all` bedzie uczciwym nastepnym krokiem.

## 2. Wyzszy cel organizacji

To zadanie chroni repo przed przedwczesnym exportem, ale tez konczy etap "wszystko jeszcze jest tylko eksperymentem". Po nim powinno byc jasne, co jest gotowe do review, a co jeszcze nie.

## 3. Read First

- `docs/HANDOFF_DLA_NASTEPNEGO_AGENTA_2026-04-25.md`
- `docs/AGENTY_PODWYKONAWCZE/ODBIOR_PORTFELA_07_ZADAN_17_22_2026-04-25.md`
- `docs/AGENTY_PODWYKONAWCZE/MINI_HANDOFF_ZADANIE_18.md`
- `docs/AGENTY_PODWYKONAWCZE/ZLECENIE_GLOWNE_23_PROJECT13_VERIFICATION_THRESHOLD_TUNING_AND_STATUS_RESOLUTION_PACKET.md`
- `PROJEKTY/13_baza_czesci_recykling/scripts/curate_candidates.py`
- `PROJEKTY/13_baza_czesci_recykling/scripts/build_catalog_artifacts.py`
- `PROJEKTY/13_baza_czesci_recykling/execution_packs/pack-project13-curation-01/RUNBOOK.md`
- `PROJEKTY/13_baza_czesci_recykling/execution_packs/pack-project13-catalog-export-01/RUNBOOK.md`

## 4. Write Scope

- `PROJEKTY/13_baza_czesci_recykling/scripts/curate_candidates.py`
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/`
- `PROJEKTY/13_baza_czesci_recykling/execution_packs/pack-project13-curation-01/`
- `PROJEKTY/13_baza_czesci_recykling/execution_packs/pack-project13-catalog-export-01/`
- ewentualnie `PROJEKTY/13_baza_czesci_recykling/docs/`

## 5. Deliverables

- review queue dla rekordow `accept`, `defer`, `reject`
- jawny export gate packet albo zaktualizowany report curation/export
- jesli to uczciwe po review: gotowy przebieg `apply` albo instrukcja, dlaczego jeszcze nie
- mini-handoff z ostatnimi blockerami przed exportem

## 6. Acceptance Criteria

- curation nie opiera sie juz na cichym auto-promote bez jawnego review queue
- istnieje dokument albo report, ktory wprost mowi, kiedy wolno uruchomic export, a kiedy nie
- export pack nie udaje gotowosci, jesli nadal brakuje OCR, manual review albo integrity approval
- counts i statusy po stronie curation sa latwe do odczytania przez kolejnego agenta

## 7. Walidacja

- `python3 PROJEKTY/13_baza_czesci_recykling/scripts/curate_candidates.py review`
- `python3 PROJEKTY/13_baza_czesci_recykling/scripts/curate_candidates.py dry-run`
- jesli zmiana dochodzi do export gate: sensowny dry-run kroku export albo jawne wyjasnienie, czemu nie
- `git diff --check`

## 8. Blokery

Jesli `23` nie zostalo jeszcze wykonane, nie zatrzymuj zadania.
Zostaw packet w formie uczciwej kolejki review i jawnie nazwij zaleznosc od `23`.

## 9. Mini-handoff

Zapisz:

- jaki jest aktualny stan kolejki `accept`, `defer`, `reject`,
- czy export gate zostal juz zdefiniowany operacyjnie,
- co dokladnie blokuje `export-all`,
- jaki jest najkrotszy nastepny ruch do pierwszego uczciwego exportu.
