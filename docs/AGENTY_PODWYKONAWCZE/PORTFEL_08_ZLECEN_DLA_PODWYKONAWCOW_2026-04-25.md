# Portfel 08 Zlecen Dla Podwykonawcow 2026-04-25

Ten portfel powstaje po odbiorze zadan `17-22`.

Jego celem nie jest juz samo dopisywanie kontraktow.
Teraz trzeba dowiezc rzeczy, ktore przesuwaja `Project 13` z "mamy dobre dokumenty" do "mamy czytelny gate przed realnym pilotem i pierwsze wykonawcze powierzchnie dla dalszych packow".

## Kolejnosc pracy

Najpierw dawaj zadania z priorytetu `A`, potem `B`.

## Portfel

1. `A` - `ZLECENIE_GLOWNE_23_PROJECT13_VERIFICATION_THRESHOLD_TUNING_AND_STATUS_RESOLUTION_PACKET.md`
   - zaleznosci: wyniki `17`, `18`, `verify_candidates.py`, `verification_triage.jsonl`
   - odbior: acceptance criteria z pliku zadania
2. `A` - `ZLECENIE_GLOWNE_24_PROJECT13_CURATION_REVIEW_QUEUE_AND_EXPORT_GATE_PACKET.md`
   - zaleznosci: wyniki `18`, wynik `23`, `curate_candidates.py`, `build_catalog_artifacts.py`
   - odbior: acceptance criteria z pliku zadania
3. `A` - `ZLECENIE_GLOWNE_25_PROJECT13_VOLUNTEER_PREFLIGHT_AND_NOTEBOOK_SELF_CHECK_PACKET.md`
   - zaleznosci: wynik `19`, `PUBLIC_VOLUNTEER_RUN_READINESS.md`, onboarding wolontariusza
   - odbior: acceptance criteria z pliku zadania
4. `A` - `ZLECENIE_GLOWNE_26_PROJECT13_CODEOWNERS_AND_REVIEW_ENFORCEMENT_BASELINE.md`
   - zaleznosci: wynik `20`, `.github/workflows/pr_secret_scan.yml`, operator packet branch protection
   - odbior: acceptance criteria z pliku zadania
5. `B` - `ZLECENIE_GLOWNE_27_PROJECT13_BLUEPRINT_MINIMAL_EXECUTION_SURFACE_DRY_RUN.md`
   - zaleznosci: wynik `21`, `validate_design_brief.py`, `pack-project13-blueprint-design-01`
   - odbior: acceptance criteria z pliku zadania
6. `B` - `ZLECENIE_GLOWNE_28_PROJECT13_ESP_RUNTIME_SIMULATED_PRECHECK_AND_BENCH_REPORT_TEMPLATE.md`
   - zaleznosci: wynik `22`, `ESP32_RECOVERED_BOARD_PROFILE_TEMPLATE.md`, `pack-project13-esp-runtime-01`
   - odbior: acceptance criteria z pliku zadania

## Zasada dla glownego agenta

Glowny agent:

- traktuje odbior portfela `07` jako nowy stan bazowy,
- najpierw sprawdza, czy pojawily sie wyniki zadan `23-28`,
- odbiera je wzgledem acceptance criteria,
- wpisuje do kolejnego handoffu, co zostalo przyjete, co wymaga poprawek i co nadal blokuje publiczny pilot.

Najwyzsza dzwignia jest teraz w zadaniach `23-26`.
Zadania `27-28` maja sens dopiero wtedy, gdy nie odwracaja uwagi od realnego domykania toru `verification -> curation -> export` i od integrity gate dla wolontariusza.
