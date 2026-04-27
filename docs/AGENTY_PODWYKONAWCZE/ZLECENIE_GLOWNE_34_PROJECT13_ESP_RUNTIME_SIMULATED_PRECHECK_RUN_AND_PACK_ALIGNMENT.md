# Zlecenie Glowne 34 Project13 ESP Runtime Simulated Precheck Run And Pack Alignment

## 1. Misja zadania

Domknij to, czego zabraklo przy `28`: skoro `simulated_precheck_esp_runtime.py` juz istnieje, uruchom go na sample board profile, zapisz output artifacts i doprowadz `pack-project13-esp-runtime-01` do stanu, w ktorym pack nie udaje juz placeholdera, ale tez nie udaje realnego hardware pass.

## 2. Wyzszy cel organizacji

To zadanie zamienia `esp-runtime` z "mamy juz skrypt, ale pack dalej o tym nie wie" w uczciwy simulated-precheck-ready stan. Dzieki temu kolejny agent widzi, co juz da sie wykonac bez plytki, a co nadal jest twardo zablokowane na realnym hardware.

## 3. Read First

- `docs/AGENTY_PODWYKONAWCZE/ODBIOR_PORTFELA_08_ZADAN_23_28_2026-04-27.md`
- `docs/AGENTY_PODWYKONAWCZE/MINI_HANDOFF_ZADANIE_22.md`
- `PROJEKTY/13_baza_czesci_recykling/scripts/simulated_precheck_esp_runtime.py`
- `PROJEKTY/13_baza_czesci_recykling/docs/SAMPLE_ESP32_BOARD_PROFILE_DEVKITC_V4.md`
- `PROJEKTY/13_baza_czesci_recykling/docs/BENCH_TEST_CONTRACT_ESP_RUNTIME_01.md`
- `PROJEKTY/13_baza_czesci_recykling/docs/SIMULATION_VS_REAL_HARDWARE_POLICY_ESP_RUNTIME_01.md`
- `PROJEKTY/13_baza_czesci_recykling/execution_packs/pack-project13-esp-runtime-01/`

## 4. Write Scope

- `PROJEKTY/13_baza_czesci_recykling/scripts/`
- `PROJEKTY/13_baza_czesci_recykling/execution_packs/pack-project13-esp-runtime-01/`
- `PROJEKTY/13_baza_czesci_recykling/docs/`
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/`

## 5. Deliverables

- wygenerowany simulated precheck output dla sample board profile
- zaktualizowany `RUNBOOK.md`, `manifest.json`, `readiness_gate.json` i `task.json`
- jesli to pomaga: skopiowany report do `autonomous_test/reports/`
- mini-handoff z tym, co pack umie juz zrobic bez plytki i co nadal blokuje realny runtime

## 6. Acceptance Criteria

- pack nie opisuje juz execution surface jako czystego PLACEHOLDERa, jesli surface realnie istnieje
- output artifact z simulated precheck istnieje i da sie zreviewowac
- dokumenty wprost mowia, ze to nadal nie jest bench test na realnym hardware
- status packa po zmianie jest bardziej wykonawczy niz `draft`, ale nie przeskakuje sztucznie na `pass`

## 7. Walidacja

- `python3 -m py_compile PROJEKTY/13_baza_czesci_recykling/scripts/simulated_precheck_esp_runtime.py`
- lokalny dry-run na `SAMPLE_ESP32_BOARD_PROFILE_DEVKITC_V4.md`
- parsowanie JSON-ow packa po zmianie
- kontrola spojnosci z `BENCH_TEST_CONTRACT_ESP_RUNTIME_01.md`
- `git diff --check`

## 8. Blokery

Brak realnej plytki nie blokuje tego zadania.
Nie wolno jednak udawac, ze simulated precheck rozstrzyga juz `bench_test_real_hardware_pass`.

## 9. Mini-handoff

Zapisz:

- jaki output artifact powstal,
- jaki jest nowy status packa,
- co da sie zrobic bez plytki,
- co nadal musi czekac na realny hardware.
