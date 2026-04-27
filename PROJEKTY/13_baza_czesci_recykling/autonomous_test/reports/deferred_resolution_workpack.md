# Deferred Resolution Workpack

Generated: 2026-04-27T17:04:48Z
Pack: pack-project13-kaggle-verification-01

## Summary

9 deferred verification cases need resolution.

| Track | Count | Requirement |
|-------|-------|-------------|
| ocr_needed | 7 | GEMINI_API_KEY |
| manual_review | 2 | Human reviewer decision |

## OCR-Needed Cases

### 1. 3336220400007 — RAM slots (Dell Precision M4800)

- **candidate_id**: candidate-0008
- **disagreement**: 0.18, **confidence**: 0.9
- **evidence_url**: https://www.youtube.com/watch?v=7ZbFOgtHvFg&t=127s
- **observed_text**: 3336220400007
- **next_action**: run_ocr_check
- **next_action_detail**: GEMINI_API_KEY required. Run: GEMINI_API_KEY=... python3 scripts/verify_candidates.py ocr-check. Verify '3336220400007' against video frame for RAM slots on Dell Precision M4800.
- **if confirmed**: promote to confirmed -> re-run curation pipeline
- **if rejected**: reject -> update status_resolution -> re-run curation
- **if inconclusive**: escalate to manual_review

### 2. UE50MU6102KXXH — Płyta główna (Mainboard) (Samsung UE50MU6102K)

- **candidate_id**: candidate-0012
- **disagreement**: 0.12, **confidence**: 0.95
- **evidence_url**: https://www.youtube.com/watch?v=OONXjU17iNc&t=9s
- **observed_text**: UE50MU6102KXXH
- **next_action**: run_ocr_check
- **next_action_detail**: GEMINI_API_KEY required. Run: GEMINI_API_KEY=... python3 scripts/verify_candidates.py ocr-check. Verify 'UE50MU6102KXXH' against video frame for Płyta główna (Mainboard) on Samsung UE50MU6102K.
- **if confirmed**: promote to confirmed -> re-run curation pipeline
- **if rejected**: reject -> update status_resolution -> re-run curation
- **if inconclusive**: escalate to manual_review

### 3. 1244-2 — Speaker (Samsung UE32EH4000)

- **candidate_id**: candidate-0018
- **disagreement**: 0.18, **confidence**: 0.9
- **evidence_url**: https://www.youtube.com/watch?v=IJYjZasRQ6w&t=227s
- **observed_text**: 1244-2
- **next_action**: run_ocr_check
- **next_action_detail**: GEMINI_API_KEY required. Run: GEMINI_API_KEY=... python3 scripts/verify_candidates.py ocr-check. Verify '1244-2' against video frame for Speaker on Samsung UE32EH4000.
- **if confirmed**: promote to confirmed -> re-run curation pipeline
- **if rejected**: reject -> update status_resolution -> re-run curation
- **if inconclusive**: escalate to manual_review

### 4. LF80537 — Heat Sink / Heat Pipe (Laptop (Generic/Unspecified))

- **candidate_id**: candidate-0073
- **disagreement**: 0.38, **confidence**: 0.95
- **evidence_url**: https://www.youtube.com/watch?v=WRKu1dDCVEw&t=306s
- **observed_text**: 
- **footprint**: PGA478
- **next_action**: run_ocr_check
- **next_action_detail**: GEMINI_API_KEY required. Run: GEMINI_API_KEY=... python3 scripts/verify_candidates.py ocr-check. Verify 'LF80537' against video frame for Heat Sink / Heat Pipe on Laptop (Generic/Unspecified).
- **if confirmed**: promote to confirmed -> re-run curation pipeline
- **if rejected**: reject -> update status_resolution -> re-run curation
- **if inconclusive**: escalate to manual_review

### 5. TS8121K — CPU (Laptop (Generic/Unspecified))

- **candidate_id**: candidate-0074
- **disagreement**: 0.38, **confidence**: 0.95
- **evidence_url**: https://www.youtube.com/watch?v=WRKu1dDCVEw&t=442s
- **observed_text**: 
- **footprint**: SOIC-8
- **next_action**: run_ocr_check
- **next_action_detail**: GEMINI_API_KEY required. Run: GEMINI_API_KEY=... python3 scripts/verify_candidates.py ocr-check. Verify 'TS8121K' against video frame for CPU on Laptop (Generic/Unspecified).
- **if confirmed**: promote to confirmed -> re-run curation pipeline
- **if rejected**: reject -> update status_resolution -> re-run curation
- **if inconclusive**: escalate to manual_review

### 6. BD243C — Transistor (Samsung Power Supply Board (BN44-00213A))

- **candidate_id**: candidate-0079
- **disagreement**: 0.38, **confidence**: 0.95
- **evidence_url**: https://www.youtube.com/watch?v=Abhlw8diSrk&t=486s
- **observed_text**: 
- **footprint**: TO-220
- **next_action**: run_ocr_check
- **next_action_detail**: GEMINI_API_KEY required. Run: GEMINI_API_KEY=... python3 scripts/verify_candidates.py ocr-check. Verify 'BD243C' against video frame for Transistor on Samsung Power Supply Board (BN44-00213A).
- **if confirmed**: promote to confirmed -> re-run curation pipeline
- **if rejected**: reject -> update status_resolution -> re-run curation
- **if inconclusive**: escalate to manual_review

### 7. QHA001249 — Capacitor (Samsung Power Supply Board (BN44-00213A))

- **candidate_id**: candidate-0080
- **disagreement**: 0.38, **confidence**: 0.8
- **evidence_url**: https://www.youtube.com/watch?v=Abhlw8diSrk&t=1559s
- **observed_text**: 
- **footprint**: Custom Transformer
- **next_action**: run_ocr_check
- **next_action_detail**: GEMINI_API_KEY required. Run: GEMINI_API_KEY=... python3 scripts/verify_candidates.py ocr-check. Verify 'QHA001249' against video frame for Capacitor on Samsung Power Supply Board (BN44-00213A).
- **if confirmed**: promote to confirmed -> re-run curation pipeline
- **if rejected**: reject -> update status_resolution -> re-run curation
- **if inconclusive**: escalate to manual_review

## Manual Review Cases

### 1. BN44-00213A — Power Supply Board (Samsung Power Supply Board (BN44-00213A))

- **candidate_id**: candidate-0076
- **disagreement**: 0.38, **confidence**: 1.0
- **evidence_url**: https://www.youtube.com/watch?v=Abhlw8diSrk&t=6s
- **observed_text**: 
- **footprint**: PCB
- **next_action**: human_review_decision
- **decision_options**: accept, reject, defer

### 2. QHAD01249 — Transformer (Samsung Power Supply Board (BN44-00213A))

- **candidate_id**: candidate-0077
- **disagreement**: 0.38, **confidence**: 0.95
- **evidence_url**: https://www.youtube.com/watch?v=Abhlw8diSrk&t=8s
- **observed_text**: 
- **footprint**: Custom Transformer Package
- **next_action**: human_review_decision
- **decision_options**: accept, reject, defer

## Procedures

### When GEMINI_API_KEY becomes available

```bash
GEMINI_API_KEY=... python3 scripts/verify_candidates.py ocr-check
python3 scripts/verify_candidates.py run
python3 scripts/curate_candidates.py dry-run --fallback-test-db
python3 scripts/curate_candidates.py export-gate
```

### For human reviewer decisions

1. Read case details above
2. Choose one of the decision_options
3. Update `curation_review_queue.jsonl`: set `reviewed_by`, `reviewed_at`, `review_status`
4. Re-run: `python3 scripts/curate_candidates.py export-gate`

JSON workpack: `/home/krzysiek/Dokumenty/INFO_GROUP/STRAZ_POLSKIEGO_Ai/PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/deferred_resolution_workpack.json`
