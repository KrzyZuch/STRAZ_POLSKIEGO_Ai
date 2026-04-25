# Verification Report

Generated: 2026-04-25T13:49:30Z
Pack: pack-project13-kaggle-verification-01
Execution surface: scripts/verify_candidates.py

## Input

- Source snapshot: `/home/krzysiek/Dokumenty/INFO_GROUP/STRAZ_POLSKIEGO_Ai/PROJEKTY/13_baza_czesci_recykling/autonomous_test/results/test_db.jsonl`
- Records loaded: 82
- Unique devices: 26

## Results

| Status | Count |
|--------|-------|
| Confirmed | 23 |
| Disputed | 9 |
| Rejected | 50 |
| **Total** | 82 |

## Disagreement summary

- Disputed records: 9
- Disagreement log: `/home/krzysiek/Dokumenty/INFO_GROUP/STRAZ_POLSKIEGO_Ai/PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/verification_disagreements.jsonl`

### Key disputed cases

- **3336220400007** (device: Dell Precision M4800) — disagreement: 0.18, triage: ocr_needed, indicators: video_source_available_for_ocr
- **UE50MU6102KXXH** (device: Samsung UE50MU6102K) — disagreement: 0.12, triage: ocr_needed, indicators: board_model_number, video_source_available_for_ocr
- **1244-2** (device: Samsung UE32EH4000) — disagreement: 0.18, triage: ocr_needed, indicators: video_source_available_for_ocr
- **LF80537** (device: Laptop (Generic/Unspecified)) — disagreement: 0.38, triage: ocr_needed, indicators: enrichment_v2_with_video_source
- **TS8121K** (device: Laptop (Generic/Unspecified)) — disagreement: 0.38, triage: ocr_needed, indicators: enrichment_v2_with_video_source
- **BN44-00213A** (device: Samsung Power Supply Board (BN44-00213A)) — disagreement: 0.38, triage: manual_review, indicators: board_model_number
- **QHAD01249** (device: Samsung Power Supply Board (BN44-00213A)) — disagreement: 0.38, triage: manual_review, indicators: custom_wound_transformer_no_datasheet
- **BD243C** (device: Samsung Power Supply Board (BN44-00213A)) — disagreement: 0.38, triage: ocr_needed, indicators: enrichment_v2_with_video_source
- **QHA001249** (device: Samsung Power Supply Board (BN44-00213A)) — disagreement: 0.38, triage: ocr_needed, indicators: enrichment_v2_with_video_source

## Disputed triage summary

| Triage category | Count | Description |
|----------------|-------|-------------|
| likely_confirmed | 14 | High MPN confidence, low disagreement; safe to auto-promote after review |
| ocr_needed | 7 | OCR frame check could resolve; requires GEMINI_API_KEY |
| manual_review | 2 | Human reviewer needed; no automated resolution path |
| threshold_tuning | 1 | Record should be rejected or recategorized by improved MPN heuristics |

- Triage report: `/home/krzysiek/Dokumenty/INFO_GROUP/STRAZ_POLSKIEGO_Ai/PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/verification_triage.jsonl`
- GEMINI_API_KEY available: False
- OCR-actionable records: 7

## Status resolution summary

| Status | Before | After | Delta |
|--------|--------|-------|-------|
| confirmed | 9 | 23 | +14 |
| disputed | 24 | 9 | -15 |
| rejected | 49 | 50 | +1 |

- Resolutions applied: 15
- Still deferred (ocr_needed): 7
- Still deferred (manual_review): 2
- Blocked for clean verified snapshot: 9
- Resolution packet: `/home/krzysiek/Dokumenty/INFO_GROUP/STRAZ_POLSKIEGO_Ai/PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/status_resolution_packet.json`
- Policy version: v2

## Verification method

1. Rule-based MPN validation (pattern matching, rejection heuristics)
2. Enrichment field cross-check (verification flag, observed text, confidence)
3. Disagreement score computation (0.0 = full agreement, 1.0 = maximum disagreement)
4. Status assignment: confirmed / disputed / rejected
5. OCR frame check (optional, requires GEMINI_API_KEY — disputed records only)
6. Disputed triage (classify disputed into: likely_confirmed, ocr_needed, manual_review, threshold_tuning)

## Output contract

- Verified snapshot: `/home/krzysiek/Dokumenty/INFO_GROUP/STRAZ_POLSKIEGO_Ai/PROJEKTY/13_baza_czesci_recykling/autonomous_test/results/test_db_verified.jsonl`
- This report: `/home/krzysiek/Dokumenty/INFO_GROUP/STRAZ_POLSKIEGO_Ai/PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/verification_report.md`
- Disagreement log: `/home/krzysiek/Dokumenty/INFO_GROUP/STRAZ_POLSKIEGO_Ai/PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/verification_disagreements.jsonl`
- Triage report: `/home/krzysiek/Dokumenty/INFO_GROUP/STRAZ_POLSKIEGO_Ai/PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/verification_triage.jsonl`
- Status resolution packet: `/home/krzysiek/Dokumenty/INFO_GROUP/STRAZ_POLSKIEGO_Ai/PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/status_resolution_packet.json`

## Limitations

- OCR-based verification requires GEMINI_API_KEY and was skipped if not available
- Rule-based validation may produce false positives for short or ambiguous MPNs
- threshold_tuning records are now rejected by improved MPN heuristics (status resolution policy v2)
- likely_confirmed records are now promoted to confirmed by status resolution policy v2
- ocr_needed records remain deferred until GEMINI_API_KEY is available
- manual_review records remain deferred until human reviewer decides
- Verification is separate from curation and export (no downstream promotion)
- Verification pack does NOT handle export gate; that is curation's responsibility

## Handoff to curation

After review of this report and disagreement log, run:

```bash
python3 scripts/curate_candidates.py review --snapshot /home/krzysiek/Dokumenty/INFO_GROUP/STRAZ_POLSKIEGO_Ai/PROJEKTY/13_baza_czesci_recykling/autonomous_test/results/test_db_verified.jsonl
python3 scripts/curate_candidates.py dry-run --fallback-test-db
```
