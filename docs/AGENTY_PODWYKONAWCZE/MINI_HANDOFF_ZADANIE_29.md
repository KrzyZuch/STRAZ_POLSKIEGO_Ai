# Mini-Handoff Zadanie 29

## Co zostalo zrobione

Domknieta operacyjna czesc curation pipeline: wygenerowana review queue i export gate packet, raport curation zaktualizowany tak, ze nie oglasza gotowosci exportu wbrew faktom.

### Nowe artefakty

- `autonomous_test/reports/curation_review_queue.jsonl` — 82 wpisy z podzialem na:
  - `auto_approved`: 9 (confirmed z verification, bez dodatkowego review)
  - `pending_human_approval`: 14 (auto-promotowane z disputed/likely_confirmed, wymagaja ludzkiego potwierdzenia)
  - `deferred`: 9 (7 ocr_needed + 2 manual_review, nie wchodza do exportu)
  - `auto_rejected`: 50 (rejected z verification lub niewazny MPN)
- `autonomous_test/reports/export_gate_packet.json` — gate_result: **BLOCKED**, z lista blockerow i next steps
- `autonomous_test/reports/curation_report.md` — zaktualizowany z sekcja "Export gate status" zamiast optymistycznego "export is safe to run"

### Zmiany w kodzie

- `scripts/curate_candidates.py`:
  - dodana funkcja `write_json()` (brakowala, cmd_export_gate ja wywolywal),
  - komendy `review-queue` i `export-gate` zarejestrowane w CLI dispatcherze w `main()`,
  - `dry-run` rozszerzony o review-queue + export-gate,
  - `cmd_report()` zaktualizowany: sekcja "Handoff to export" zastapiona sekcja "Export gate status" czytajaca z export_gate_packet.json,
  - docstring zaktualizowany na 9 komend.

### Zmiany w runbookach

- `pack-project13-curation-01/RUNBOOK.md`:
  - dodany Krok 6: review queue i export gate,
  - zaktualizowany Krok 7 (byly Krok 6): handoff do exportu warunkowany gate OPEN,
  - zaktualizowana sekcja "Aktualny status" (9 komend, review queue, export gate),
  - zaktualizowana sekcja "Minimalne kryterium sukcesu" (review queue, export gate, curation_report.md nie oglasza gotowosci),
  - dodana dokumentacja komend `review-queue` i `export-gate` w Execution surface,
  - zaktualizowany opis `dry-run`,
  - docelowy przeplyw zaktualizowany o review queue i export gate.
- `pack-project13-catalog-export-01/RUNBOOK.md`:
  - dodany warunek "export gate OPEN" w sekcji "Co trzeba miec przed startem".

## Counts review queue

| review_status | Count |
|---------------|-------|
| auto_approved | 9 |
| pending_human_approval | 14 |
| deferred | 9 |
| auto_rejected | 50 |
| **Total** | 82 |

## Stan export gate

**BLOCKED**

### Blockers (2)

1. 14 accepted candidates still pending human approval (auto-promotowane z disputed/likely_confirmed)
2. No human review approval recorded for pending candidates

### Warnings (3)

1. 9 deferred candidates not in export (7 ocr_needed + 2 manual_review)
2. 7 records still deferred by verification (ocr_needed)
3. 2 records still deferred by verification (manual_review)

### Gate checks

| Check | Result |
|-------|--------|
| no_pending_approvals | FAIL |
| no_unresolved_deferrals | FAIL |
| catalog_validation_passes | PASS |
| human_review_recorded | FAIL |

## Lista blockerow

1. **14 pending_human_approval** — kandydaci auto-promotowani z disputed (triage=likely_confirmed) per status resolution policy v2. Wymagaja ludzkiego potwierdzenia ze strony reviewera:
   - M425R1GB4BB0-CWM0D, P28A41E, 230130 2R2 33 25V H33, K6100 1124 08.24, M51413ASP, MT1588AE 0311-ARS HF986, MINIJST E DC546134603 ST, JKB1 JKB2, INTEL 08 i7-628M, BD82HM55 SLGZR, 775i65G, RM 121, LDF-12V16W, V17081
2. **9 deferred** — nie wchodza do exportu, ale nie blokuja gate bezposrednio (gate check no_unresolved_deferrals jest FAIL, ale jest warning):
   - ocr_needed: 3336220400007, UE50MU6102KXXH, 1244-2, LF80537, TS8121K, BD243C, QHA001249
   - manual_review: BN44-00213A, QHAD01249

## Najkrotszy uczciwy ruch do pierwszego exportu

1. Ustaw `reviewed_by` i `reviewed_at` w `curation_review_queue.jsonl` dla 14 pending_human_approval (ludzki reviewer zatwierdza auto-promotowane likely_confirmed).
2. Re-run: `python3 scripts/curate_candidates.py export-gate`
3. Jesli gate przejdzie na OPEN: `python3 scripts/curate_candidates.py apply` + `python3 scripts/build_catalog_artifacts.py export-all`
4. 9 deferred zostaje poza eksportem — to jest poprawne, nie udajemy ze sa rozstrzygniete.

## Jakie komendy walidacyjne przeszly

- `python3 -m py_compile PROJEKTY/13_baza_czesci_recykling/scripts/curate_candidates.py` — OK
- `python3 PROJEKTY/13_baza_czesci_recykling/scripts/curate_candidates.py review` — OK
- `python3 PROJEKTY/13_baza_czesci_recykling/scripts/curate_candidates.py review-queue` — OK
- `python3 PROJEKTY/13_baza_czesci_recykling/scripts/curate_candidates.py export-gate` — OK (BLOCKED, poprawnie)
- `python3 PROJEKTY/13_baza_czesci_recykling/scripts/curate_candidates.py dry-run` — OK (align + decide + review-queue + export-gate + validate + report)
- `git diff --check` — OK
