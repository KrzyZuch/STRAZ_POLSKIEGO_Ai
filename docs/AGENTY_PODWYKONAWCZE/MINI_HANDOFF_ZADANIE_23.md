# Mini-Handoff Zadanie 23

## Co zostalo zrobione

Domkniety status resolution packet dla verification pipeline. Triage z zadania 17 zostal zamieniony z rekomendacji w realny mechanizm, ktory zmienia statusy rekordow.

### Nowe MPN rejection patterns

Dodano do `MPN_REJECTION_PATTERNS` i `MPN_REJECTION_BROAD_PATTERNS` patterny, ktore wczesniej byly tylko wskazywane przez triage indicators:
- `patent_number` — "PATENT #..." odrzucane na etapie validate
- `model_label_not_mpn` — "MODEL: ..." odrzucane na etapie validate
- `full_model_string_not_mpn` — "Lenovo NOK ..." odrzucane na etapie validate
- `date_code_in_part_number` — daty produkcji odrzucane na etapie validate
- `bom_label_in_part_number` — "BOM:..." odrzucane na etapie validate
- `spec_annotation_not_mpn` — "FSB", "Rev.", "REV." odrzucane na etapie validate
- `comma_separated_list` — 3+ przecinki w part_number odrzucane na etapie validate

### Nowa komenda `resolve-status`

Dodano komende `resolve-status`, ktora stosuje jawna `STATUS_RESOLUTION_POLICY` v2:

| Kategoria | Resolution | Nowy status |
|-----------|-----------|-------------|
| likely_confirmed | promote_to_confirmed | confirmed |
| threshold_tuning | reject_by_heuristics | rejected |
| ocr_needed | defer_pending_ocr | disputed (unchanged) |
| manual_review | defer_pending_human | disputed (unchanged) |

Kazda zmiana statusu dostaje pole `status_resolution` z audit trail (policy, from, to, audit_note, resolved_at).

### Nowy artefakt: status_resolution_packet.json

Zawiera:
- `status_before` / `status_after` — counts przed i po resolution
- `resolution_log` — lista rekordow ze zmienionym statusem
- `ocr_needed_remaining` — lista rekordow nadal wymagajacych OCR
- `manual_review_remaining` — lista rekordow nadal wymagajacych human review
- `blocked_for_clean_snapshot` — jawna lista tego, co blokuje czysty verified snapshot

### Pipeline zaktualizowany

Komenda `run` i `dry-run` teraz wykonuja: load + validate + score + triage + **resolve-status** + snapshot + report.

## Jakie pliki zmieniono

Zmienione:
- `PROJEKTY/13_baza_czesci_recykling/scripts/verify_candidates.py` — dodano: `MPN_REJECTION_BROAD_PATTERNS`, nowe wzorce w `MPN_REJECTION_PATTERNS`, `STATUS_RESOLUTION_POLICY`, `STATUS_RESOLUTION_PACKET_PATH`, `cmd_resolve_status()`, zaktualizowano `classify_mpn_quality()` (broad patterns + comma check), zaktualizowano `cmd_run()` (krok resolve-status), zaktualizowano `cmd_report()` (sekcja status resolution), zaktualizowano `main()` (komenda resolve-status), zaktualizowano docstring
- `PROJEKTY/13_baza_czesci_recykling/execution_packs/pack-project13-kaggle-verification-01/RUNBOOK.md` — zaktualizowany: przeplyw, output contract, status resolution policy, co pack robi, co nie robi, co blokuje, co zostalo rozstrzygniete

Wygenerowane artefakty (po `run`):
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/status_resolution_packet.json`
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/verification_triage.jsonl` — zaktualizowany (24 disputed, w tym 14 likely_confirmed, 7 ocr_needed, 2 manual_review, 1 threshold_tuning)
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/verification_scored.jsonl` — zaktualizowany z triage i status_resolution
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/results/test_db_verified.jsonl` — zaktualizowany (23 confirmed, 9 disputed, 50 rejected)
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/verification_disagreements.jsonl` — zaktualizowany (9 disputed)
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/verification_report.md` — zaktualizowany z sekcja status resolution

## Jakie komendy walidacyjne przeszly

- `python3 -m py_compile PROJEKTY/13_baza_czesci_recykling/scripts/verify_candidates.py` — OK
- `python3 PROJEKTY/13_baza_czesci_recykling/scripts/verify_candidates.py dry-run` — OK (82 kandydatow, 24 disputed z triage, 15 status changes, 0 bledow)
- `python3 PROJEKTY/13_baza_czesci_recykling/scripts/verify_candidates.py run` (bez GEMINI_API_KEY) — OK
- `git diff --check` — OK

## Counts przed i po zmianie (na 82 kandydatach)

| Status | Przed | Po | Delta |
|--------|-------|----|-------|
| confirmed | 9 | 23 | +14 |
| disputed | 30 | 9 | -21* |
| rejected | 43 | 50 | +7 |

*Uwaga: przed zmiana bylo 30 disputed (z triage z zadania 17). Po dodaniu nowych rejection patterns do validate, 6 z 7 threshold_tuning zostaje odrzuconych juz na etapie validate (zamiast trafiac do triage jako disputed). Pozostale 14 likely_confirmed promotowane do confirmed, 1 threshold_tuning w triage rejectowany do rejected.

## Co nadal blokuje czysty verified snapshot

1. **7 rekordow ocr_needed** — wymagaja GEMINI_API_KEY do OCR check: 3336220400007, UE50MU6102KXXH, 1244-2, LF80537, TS8121K, BD243C, QHA001249
2. **2 rekordy manual_review** — wymagaja ludzkiego reviewera: BN44-00213A (board model), QHAD01249 (custom transformer)

Nie udawano, ze OCR zostal wykonany.

## Czy threshold_tuning zostalo realnie wyciszone

Tak. 6 z 7 rekordow threshold_tuning jest teraz odrzucanych na etapie validate przez nowe `MPN_REJECTION_PATTERNS`. 1 pozostaly (z `date_code_in_part_number`) jest odrzucany przez `resolve-status`. Zadna kategoria threshold_tuning nie zostaje juz tylko jako rekomendacja w opisie — wszystkie maja realny skutek w pipeline.

## Jaki jest nowy status likely_confirmed

14 rekordow likely_confirmed zostalo auto-promotowanych do confirmed przez `resolve-status` z audit trail. Promocja jest warunkowa: wymaga mpn_valid i braku threshold indicators. Jesli likely_confirmed ma threshold indicators, jest rejectowany zamiast promowany.

## Co powinien zrobic kolejny wykonawca

- Jesli GEMINI_API_KEY bedzie dostepny: `GEMINI_API_KEY=... python3 scripts/verify_candidates.py ocr-check` dla 7 ocr_needed, a nastepnie ponownie `run`
- Zdecydowac o 2 manual_review rekordach (BN44-00213A, QHAD01249)
- Uruchomic curation na zaktualizowanym verified snapshot: `python3 scripts/curate_candidates.py review --snapshot autonomous_test/results/test_db_verified.jsonl`
- Zadanie 24 (curation review queue + export gate) moze teraz pracowac na stabilniejszym verified snapshot (23 confirmed, 9 disputed, 50 rejected)
