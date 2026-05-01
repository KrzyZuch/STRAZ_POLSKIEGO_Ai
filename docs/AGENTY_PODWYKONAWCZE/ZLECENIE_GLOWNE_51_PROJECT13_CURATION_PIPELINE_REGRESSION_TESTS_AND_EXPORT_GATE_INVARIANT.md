# Zlecenie Glowne 51 Project13 Curation Pipeline Regression Tests And Export Gate Invariant

## 1. Misja zadania

Dodaj regresyjna ochrone dla curation pipeline: export gate musi pozostac BLOCKED dopoki jest choc jeden pending_human_approval albo 0 human approvals, a review queue nie moze miec starych entries z wczesniejszych runow.

## 2. Wyzszy cel organizacji

Zadanie `50` dodalo testy regresyjne dla verification pipeline (OCR parser + stale packet guard). Curation pipeline nie ma zadnej warstwy testow. Po korekcie audytowej z zadania `42` curation decisions, review queue i export gate byly odswiezane recznie — bez testu regresyjnego przyszla zmiana moze znowu wyprodukowac niespojny stan.

## 3. Read First

- `docs/AGENTY_PODWYKONAWCZE/MINI_HANDOFF_ZADANIE_50.md`
- `docs/AGENTY_PODWYKONAWCZE/ODBIOR_PORTFELA_11_ZADAN_41_45_2026-04-30.md`
- `PROJEKTY/13_baza_czesci_recykling/scripts/curate_candidates.py`
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/curation_review_queue.jsonl`
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/export_gate_packet.json`
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/curation_decisions.jsonl`
- `tests/test_ocr_parser_regression_z50.py` (wzorzec)

## 4. Write Scope

- `tests/test_curation_pipeline_regression_z51.py`
- `docs/AGENTY_PODWYKONAWCZE/ZLECENIE_GLOWNE_51_PROJECT13_CURATION_PIPELINE_REGRESSION_TESTS_AND_EXPORT_GATE_INVARIANT.md` (ten plik)
- `docs/AGENTY_PODWYKONAWCZE/MINI_HANDOFF_ZADANIE_51.md`

## 5. Deliverables

- testy jednostkowe dla `slugify`, `normalize_part_number`, `infer_species`, `infer_genus`, `infer_mounting`, `infer_device_category`, `looks_like_valid_mpn`, `assign_batch`
- test invariantu export gate: BLOCKED gdy pending_human_approval > 0 albo 0 human approvals
- test konstystencji: review queue entries maja unikalne candidate_id
- test: confirmed verification_status -> accept decision, rejected -> reject, disputed + likely_confirmed -> accept

## 6. Acceptance Criteria

- test nie wymaga `GEMINI_API_KEY`
- test nie wykonuje zadnego network call
- test nie wymaga prawdziwego reviewera ani hardware
- test mozna uruchomic z `python3 -m unittest tests/test_curation_pipeline_regression_z51.py`
- export gate invariant: pending_human_approval > 0 => gate BLOCKED
- export gate invariant: 0 human approvals => gate BLOCKED

## 7. Walidacja

- `python3 -m py_compile PROJEKTY/13_baza_czesci_recykling/scripts/curate_candidates.py`
- `python3 -m unittest tests/test_curation_pipeline_regression_z51.py -v`
- `python3 PROJEKTY/13_baza_czesci_recykling/scripts/curate_candidates.py export-gate`
- `python3 PROJEKTY/13_baza_czesci_recykling/scripts/curate_candidates.py review-status`
- `git diff --check`

## 8. Blokery

Brak frameworka testowego nie blokuje zadania. Uzyj `unittest` jak w zadaniu 50.

## 9. Mini-handoff

Zapisz:

- jakie funkcje curation pipeline pokryto testami,
- gdzie jest test,
- jaki jest wynik export gate przy aktualnym stanie,
- czy trzeba jeszcze refaktorowac curation pipeline.
