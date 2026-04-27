# Zlecenie Glowne 31 Project13 Curation Human Approval Ledger And Review Recording

## 1. Misja zadania

Dodaj uczciwa i wygodna sciezke zapisywania ludzkich approvali dla kandydatow `pending_human_approval`, tak zeby `export-gate` nie zalezalo od recznej, niesformatowanej edycji JSON-a. Chodzi o ledger albo helper review recording, nie o fikcyjne approvale.

## 2. Wyzszy cel organizacji

To zadanie zamienia "wiemy, ze czlowiek musi kliknac approve" w audytowalny mechanizm review. Dzieki temu curation i export nie zostaja zakladnikiem wiedzy jednej osoby o tym, gdzie cos dopisac recznie.

## 3. Read First

- `docs/AGENTY_PODWYKONAWCZE/ODBIOR_PORTFELA_08_ZADAN_23_28_2026-04-27.md`
- wynik zadania `29` albo aktualny `curation_review_queue.jsonl`
- `PROJEKTY/13_baza_czesci_recykling/scripts/curate_candidates.py`
- `PROJEKTY/13_baza_czesci_recykling/docs/PILOT_REVIEW_ASSIGNMENT_AND_APPROVAL_PATH.md`
- `PROJEKTY/13_baza_czesci_recykling/docs/REVIEW_ENFORCEMENT_BASELINE.md`
- `PROJEKTY/13_baza_czesci_recykling/execution_packs/pack-project13-curation-01/RUNBOOK.md`

## 4. Write Scope

- `PROJEKTY/13_baza_czesci_recykling/scripts/curate_candidates.py`
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/`
- `PROJEKTY/13_baza_czesci_recykling/execution_packs/pack-project13-curation-01/`
- `PROJEKTY/13_baza_czesci_recykling/docs/`

## 5. Deliverables

- ledger lub helper do zapisu review decisions dla `pending_human_approval`
- jawny format: `approved` / `rejected` / `defer`, `reviewed_by`, `reviewed_at`, `note`
- instrukcja, jak po review odswiezyc export gate
- mini-handoff z nowym flow review recording

## 6. Acceptance Criteria

- istnieje jedna jawna sciezka zapisu ludzkiego review dla pending candidates
- export gate potrafi skonsumowac ten review record albo ma jasno opisany handoff do niego
- nie trzeba juz zgadywac, gdzie i w jakim formacie dopisac approval
- zadanie nie wpisuje zadnych fikcyjnych reviewerow ani approvali

## 7. Walidacja

- `python3 -m py_compile PROJEKTY/13_baza_czesci_recykling/scripts/curate_candidates.py` jesli skrypt byl zmieniany
- `python3 PROJEKTY/13_baza_czesci_recykling/scripts/curate_candidates.py review-queue`
- sensowny przebieg helpera lub odswiezonego export gate
- `git diff --check`

## 8. Blokery

Jesli nie ma jeszcze prawdziwych osob do review, przygotuj mechanizm i placeholder packet, ale nie uznawaj review za wykonane.

## 9. Mini-handoff

Zapisz:

- jaki ledger albo helper dodano,
- jak wyglada nowy flow `pending_human_approval -> approved/rejected/defer`,
- co musi zrobic prawdziwy reviewer,
- jak ten record wplywa na export gate.
