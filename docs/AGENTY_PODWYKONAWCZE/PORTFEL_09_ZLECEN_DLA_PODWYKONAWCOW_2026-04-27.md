# Portfel 09 Zlecen Dla Podwykonawcow 2026-04-27

Ten portfel powstaje po odbiorze portfela `08`.

Nie sluzy do poszerzania zakresu dla samego poszerzania.
Ma zamienic czesciowo dowiezione execution surface w operacyjne gate'y, review receipts i canary-ready packet przed pierwszym uczciwym exportem oraz przed pierwszym sensownym pilotem wolontariackim.

## Kolejnosc pracy

Najpierw dawaj zadania z priorytetu `A`, potem `B`.

## Portfel

1. `A` - `ZLECENIE_GLOWNE_29_PROJECT13_CURATION_REVIEW_QUEUE_EXECUTION_AND_EXPORT_GATE_RECEIPT.md`
   - zaleznosci: wynik `23`, nieodebrane `24`, `curate_candidates.py`, `status_resolution_packet.json`
   - odbior: acceptance criteria z pliku zadania
2. `A` - `ZLECENIE_GLOWNE_30_PROJECT13_VERIFICATION_DEFERRED_OCR_AND_MANUAL_REVIEW_WORKPACK.md`
   - zaleznosci: wynik `23`, `verification_report.md`, `status_resolution_packet.json`, deferred cases z verified snapshot
   - odbior: acceptance criteria z pliku zadania
3. `A` - `ZLECENIE_GLOWNE_31_PROJECT13_CURATION_HUMAN_APPROVAL_LEDGER_AND_REVIEW_RECORDING.md`
   - zaleznosci: wynik `29`, `curation_review_queue.jsonl`, `PILOT_REVIEW_ASSIGNMENT_AND_APPROVAL_PATH.md`
   - odbior: acceptance criteria z pliku zadania
4. `A` - `ZLECENIE_GLOWNE_32_PROJECT13_PUBLIC_VOLUNTEER_CANARY_PACKET_AND_RETRO_TEMPLATE.md`
   - zaleznosci: wyniki `25`, `26`, `VOLUNTEER_PREFLIGHT_CHECKLIST.md`, `PUBLIC_VOLUNTEER_RUN_READINESS.md`
   - odbior: acceptance criteria z pliku zadania
5. `B` - `ZLECENIE_GLOWNE_33_PROJECT13_BLUEPRINT_BRIEF_ROW_VALIDATION_AND_SMOKE_TEST_BASELINE.md`
   - zaleznosci: wynik `27`, `validate_design_brief.py`, `dry_run_blueprint_design.py`, sample brief
   - odbior: acceptance criteria z pliku zadania
6. `B` - `ZLECENIE_GLOWNE_34_PROJECT13_ESP_RUNTIME_SIMULATED_PRECHECK_RUN_AND_PACK_ALIGNMENT.md`
   - zaleznosci: nieodebrane `28`, `simulated_precheck_esp_runtime.py`, sample board profile, `pack-project13-esp-runtime-01`
   - odbior: acceptance criteria z pliku zadania

## Zasada dla glownego agenta

Glowny agent:

- traktuje `ODBIOR_PORTFELA_08_ZADAN_23_28_2026-04-27.md` jako nowy stan bazowy,
- najpierw sprawdza, czy pojawily sie wyniki zadan `29-34`,
- odbiera je wzgledem acceptance criteria,
- wpisuje do kolejnego handoffu, co zostalo przyjete, co zostalo zwrocone i co nadal blokuje eksport lub pilot.

Najwyzsza dzwignia jest teraz w zadaniach `29-31`.
`32` ma przygotowac pierwszy kontrolowany pilot bez udawania, ze pilot juz sie wydarzy.
`33-34` maja utwardzic execution surface dla `blueprint` i `esp-runtime`, ale nie powinny wypchnac z pola widzenia export gate i review gate.
