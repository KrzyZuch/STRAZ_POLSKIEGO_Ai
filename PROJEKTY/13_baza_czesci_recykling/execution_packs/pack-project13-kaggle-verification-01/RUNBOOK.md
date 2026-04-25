# Runbook Dla Pack Project13 Kaggle Verification 01

## Cel

Ten pack domyka etap `verification chain` po wstepnym discovery i enrichment.

Docelowy przeplyw:

```text
candidate snapshot -> rule-based MPN validation -> OCR frame check (optional) -> disagreement scoring -> disputed triage -> status resolution -> verified snapshot + report + disagreement log + triage report + status resolution packet
```

## Execution surface

Skrypt: `scripts/verify_candidates.py`

## Jak uruchomic

### Wymagania

- Python 3.10+
- Kandydacki snapshot z enrichment: `autonomous_test/results/test_db.jsonl`
- (Opcjonalnie) `GEMINI_API_KEY` — dla OCR weryfikacji rekordow spornych

### Dry-run (bez modyfikacji kanonicznych plikow)

```bash
python3 PROJEKTY/13_baza_czesci_recykling/scripts/verify_candidates.py dry-run
```

Outputy zapisane z sufiksem `.dry-run`. Kanoniczne pliki niezmienione.

### Pelny run

```bash
python3 PROJEKTY/13_baza_czesci_recykling/scripts/verify_candidates.py run
```

Zapisuje kanoniczne outputy do:
- `autonomous_test/results/test_db_verified.jsonl`
- `autonomous_test/reports/verification_report.md`
- `autonomous_test/reports/verification_disagreements.jsonl`
- `autonomous_test/reports/verification_triage.jsonl`
- `autonomous_test/reports/status_resolution_packet.json`

### Z OCR verification (dla rekordow spornych)

```bash
GEMINI_API_KEY=... python3 PROJEKTY/13_baza_czesci_recykling/scripts/verify_candidates.py run
```

Albo:

```bash
python3 PROJEKTY/13_baza_czesci_recykling/scripts/verify_candidates.py ocr-check --api-key YOUR_KEY
```

### Pojedyncze kroki

```bash
python3 scripts/verify_candidates.py load
python3 scripts/verify_candidates.py validate
python3 scripts/verify_candidates.py score
python3 scripts/verify_candidates.py triage
python3 scripts/verify_candidates.py resolve-status
python3 scripts/verify_candidates.py snapshot
python3 scripts/verify_candidates.py report
```

## Input contract

| Pole | Wymagane | Opis |
|------|----------|------|
| `device` | tak | Nazwa urzadzenia zrodlowego |
| `part_name` | tak | Opis czesci |
| `part_number` | tak | Claimed MPN |
| `confidence` | nie | Enrichment confidence (0.0-1.0) |
| `verification.verified` | nie | Flag z enrichment OCR |
| `verification.observed_text` | nie | Tekst z OCR frame check |
| `yt_link` / `source_video` | nie | Link do zrodla wideo |

## Output contract

| Artefakt | Sciezka | Opis |
|----------|---------|------|
| Verified snapshot | `autonomous_test/results/test_db_verified.jsonl` | Wszystkie rekordy z `verification_status`, `disagreement_score`, `status_resolution` |
| Verification report | `autonomous_test/reports/verification_report.md` | Markdown: counts, metoda, sporne przypadki, status resolution summary, ograniczenia |
| Disagreement log | `autonomous_test/reports/verification_disagreements.jsonl` | Subset: tylko rekordy `disputed` |
| Triage report | `autonomous_test/reports/verification_triage.jsonl` | Disputed records classified by triage category |
| Status resolution packet | `autonomous_test/reports/status_resolution_packet.json` | Jawna lista zmian statusow, remaining blockers, audit trail |

### Pole `verification_status`

- `confirmed` — MPN valid, niski disagreement, gotowy do curation (w tym ex-likely_confirmed po status resolution)
- `disputed` — Nadal wymaga rozstrzygniecia: ocr_needed lub manual_review
- `rejected` — MPN invalid albo wysoki disagreement; odrzucony z verification (w tym ex-threshold_tuning po status resolution)

### Pole `triage_category` (tylko dla disputed)

- `likely_confirmed` — Wysoka confidence MPN, niski disagreement; auto-promotowany do confirmed przez status resolution policy v2
- `ocr_needed` — OCR frame check moglby rozstrzygnac; wymaga GEMINI_API_KEY; pozostaje disputed
- `manual_review` — Human reviewer potrzebny; brak automatycznej sciezki rozwiazania; pozostaje disputed
- `threshold_tuning` — Rekord odrzucany przez improved MPN heuristics; auto-rejectowany do rejected przez status resolution policy v2

### Pole `status_resolution` (dla rekordow z rozstrzygnietym statusem)

- `policy` — Ktora zasada z STATUS_RESOLUTION_POLICY zostala zastosowana
- `from` / `to` — Zmiana statusu
- `triage_category` — Kategoria triage ktora wyzwolila resolution
- `audit_note` — Czytelny opis powodu zmiany
- `resolved_at` — Timestamp resolution

## Status resolution policy v2

| Kategoria triage | Resolution | Nowy status | Warunek |
|-----------------|------------|-------------|---------|
| likely_confirmed | promote_to_confirmed | confirmed | mpn_valid AND no threshold indicators |
| likely_confirmed (blocked) | reject | rejected | threshold indicators present despite likely_confirmed |
| threshold_tuning | reject_by_heuristics | rejected | improved MPN rejection patterns |
| ocr_needed | defer_pending_ocr | disputed (unchanged) | GEMINI_API_KEY not available |
| manual_review | defer_pending_human | disputed (unchanged) | board_model OR custom_transformer |

## Co pack robi

1. Wczytuje kandydacki snapshot z etapu enrichment.
2. Waliduje MPN kazdego rekordu przez rule-based pattern matching (z improved rejection patterns: patent, model label, date code, BOM label, FSB/Rev spec annotations, comma lists >=3).
3. Cross-checkuje pola z enrichment (verification flag, observed text, confidence).
4. Oblicza disagreement score (0.0 = pelna zgodnosc, 1.0 = maksymalna rozbieznosc).
5. Przypisuje `verification_status`: confirmed / disputed / rejected.
6. Klasyfikuje disputed rekordy do kategorii triage: likely_confirmed / ocr_needed / manual_review / threshold_tuning.
7. Stosuje status resolution policy: likely_confirmed -> confirmed, threshold_tuning -> rejected, ocr_needed/manual_review -> zostaje disputed z audit trail.
8. (Opcjonalnie) Uruchamia OCR frame check dla rekordow disputed przez GEMINI_API_KEY.
9. Zapisuje verified snapshot, verification report, disagreement log, triage report i status resolution packet.

## Czego pack nie robi

- nie buduje downstream exportow (ecoEDA, InvenTree, D1)
- nie miesza rekordow confirmed z disputed bez jawnego statusu
- nie promuje danych do upstream bez PR
- nie wymaga GEMINI_API_KEY (rule-based flow dziala bez API key)
- nie udaje, ze OCR zostal wykonany gdy GEMINI_API_KEY nie jest dostepny
- nie miesza swojej odpowiedzialnosci z finalnym exportem (export gate to curation's job)

## Walidacja

```bash
python3 -m py_compile PROJEKTY/13_baza_czesci_recykling/scripts/verify_candidates.py
python3 PROJEKTY/13_baza_czesci_recykling/scripts/verify_candidates.py dry-run
```

Dry-run na 82 kandydatach z `test_db.jsonl` przechodzi bez bledow.

## Handoff do curation

Po review verification report, disagreement log i status resolution packet:

```bash
python3 scripts/curate_candidates.py review --snapshot autonomous_test/results/test_db_verified.jsonl
python3 scripts/curate_candidates.py dry-run --fallback-test-db
```

## Co nadal blokuje czysty verified snapshot

- 7 rekordow `ocr_needed` czeka na GEMINI_API_KEY (3336220400007, UE50MU6102KXXH, 1244-2, LF80537, TS8121K, BD243C, QHA001249)
- 2 rekordy `manual_review` wymagaja ludzkiego reviewera (BN44-00213A, QHAD01249)
- Gdy GEMINI_API_KEY bedzie dostepny: `GEMINI_API_KEY=... python3 scripts/verify_candidates.py ocr-check`

## Co zostalo rozstrzygniete przez status resolution policy v2

- 14 rekordow `likely_confirmed` -> `confirmed` (auto-promote)
- 1 rekord `threshold_tuning` -> `rejected` (improved heuristics; 6 innych threshold_tuning juz odrzuconych na etapie validate przez nowe MPN_REJECTION_PATTERNS)
- 9 rekordow pozostaje `disputed` (7 ocr_needed + 2 manual_review)
