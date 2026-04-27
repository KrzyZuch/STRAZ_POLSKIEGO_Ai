# Zlecenie Glowne 29 Project13 Curation Review Queue Execution And Export Gate Receipt

## 1. Misja zadania

Domknij operacyjnie to, co w zadaniu `24` zostalo juz prawie zaimplementowane: wygeneruj jawna review queue i jawny export gate packet dla aktualnego verified snapshotu po `23`, odswiez report curation i usun sprzeczny sygnal "mozna eksportowac", jesli gate wciaz jest zablokowany.

## 2. Wyzszy cel organizacji

To zadanie zamienia curation z dobrego execution surface w realny, audytowalny prog przed exportem. Po nim kolejny agent ma widziec nie "chyba juz mozna", tylko jasne `TAK/NIE` i dlaczego.

## 3. Read First

- `docs/AGENTY_PODWYKONAWCZE/ODBIOR_PORTFELA_08_ZADAN_23_28_2026-04-27.md`
- `docs/AGENTY_PODWYKONAWCZE/MINI_HANDOFF_ZADANIE_23.md`
- `PROJEKTY/13_baza_czesci_recykling/scripts/curate_candidates.py`
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/status_resolution_packet.json`
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/curation_report.md`
- `PROJEKTY/13_baza_czesci_recykling/execution_packs/pack-project13-curation-01/RUNBOOK.md`
- `PROJEKTY/13_baza_czesci_recykling/execution_packs/pack-project13-catalog-export-01/RUNBOOK.md`

## 4. Write Scope

- `PROJEKTY/13_baza_czesci_recykling/scripts/curate_candidates.py`
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/`
- `PROJEKTY/13_baza_czesci_recykling/execution_packs/pack-project13-curation-01/`
- `PROJEKTY/13_baza_czesci_recykling/execution_packs/pack-project13-catalog-export-01/`
- ewentualnie `PROJEKTY/13_baza_czesci_recykling/docs/`

## 5. Deliverables

- wygenerowany `curation_review_queue.jsonl`
- wygenerowany `export_gate_packet.json`
- odswiezony `curation_report.md` zgodny z gate packetem
- jesli potrzebne: zaktualizowane runbooki lub manifesty packow curation/export
- mini-handoff z gate status i blockerami

## 6. Acceptance Criteria

- review queue istnieje jako artefakt i rozdziela przynajmniej: `auto_approved`, `pending_human_approval`, `deferred`, `auto_rejected`
- export gate packet mowi wprost, czy export jest dozwolony, a jesli nie, to co go blokuje
- `curation_report.md` nie oglasza juz gotowosci exportu wbrew gate packetowi
- zadanie nie udaje OCR ani ludzkich approvali, jesli ich nie ma
- counts i statusy sa czytelne dla kolejnego agenta bez wchodzenia w kod

## 7. Walidacja

- `python3 PROJEKTY/13_baza_czesci_recykling/scripts/curate_candidates.py review`
- `python3 PROJEKTY/13_baza_czesci_recykling/scripts/curate_candidates.py review-queue`
- `python3 PROJEKTY/13_baza_czesci_recykling/scripts/curate_candidates.py export-gate`
- `python3 PROJEKTY/13_baza_czesci_recykling/scripts/curate_candidates.py report`
- jesli zmieniasz flow: `python3 PROJEKTY/13_baza_czesci_recykling/scripts/curate_candidates.py dry-run`
- `git diff --check`

## 8. Blokery

Jesli nie ma jeszcze ludzkich approvali albo OCR/manual review nadal wisza, gate ma pozostac zablokowany.
To nie jest porazka zadania.
Porazka byloby dopiero ukrycie tego faktu.

## 9. Mini-handoff

Zapisz:

- counts dla review queue,
- stan export gate (`allowed` / `blocked`),
- jaka jest lista blockerow,
- jaki jest najkrotszy uczciwy ruch do pierwszego exportu.
