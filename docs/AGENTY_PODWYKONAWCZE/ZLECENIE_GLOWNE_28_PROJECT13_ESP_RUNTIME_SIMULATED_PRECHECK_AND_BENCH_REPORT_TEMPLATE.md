# Zlecenie Glowne 28 Project13 Esp Runtime Simulated Precheck And Bench Report Template

## 1. Misja zadania

Po kontrakcie i polityce z zadania `22` dowiez minimalna warstwe wykonawcza dla `esp-runtime-01`: simulated precheck runner albo rownie mocny packet kontrolny oraz bench report template, zeby pack nie konczyl sie tylko na opisach gate'ow.

## 2. Wyzszy cel organizacji

To zadanie tworzy pierwszy praktyczny krok przed realnym hardware, ale bez mieszania symulacji z rzeczywistym potwierdzeniem bezpieczenstwa i dzialania.

## 3. Read First

- `docs/HANDOFF_DLA_NASTEPNEGO_AGENTA_2026-04-25.md`
- `docs/AGENTY_PODWYKONAWCZE/ODBIOR_PORTFELA_07_ZADAN_17_22_2026-04-25.md`
- `docs/AGENTY_PODWYKONAWCZE/MINI_HANDOFF_ZADANIE_22.md`
- `PROJEKTY/13_baza_czesci_recykling/docs/BENCH_TEST_CONTRACT_ESP_RUNTIME_01.md`
- `PROJEKTY/13_baza_czesci_recykling/docs/SIMULATION_VS_REAL_HARDWARE_POLICY_ESP_RUNTIME_01.md`
- `PROJEKTY/13_baza_czesci_recykling/docs/SAMPLE_ESP32_BOARD_PROFILE_DEVKITC_V4.md`
- `PROJEKTY/13_baza_czesci_recykling/execution_packs/pack-project13-esp-runtime-01/`

## 4. Write Scope

- `PROJEKTY/13_baza_czesci_recykling/scripts/`
- `PROJEKTY/13_baza_czesci_recykling/execution_packs/pack-project13-esp-runtime-01/`
- `PROJEKTY/13_baza_czesci_recykling/docs/`
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/`

## 5. Deliverables

- simulated precheck runner albo rownowazny wykonywalny packet
- bench report template dla realnego hardware
- aktualizacja runbooka, readiness gate i checklisty packa
- mini-handoff z tym, czego nadal nie zastapi zadna symulacja

## 6. Acceptance Criteria

- pack ma przynajmniej jeden praktyczny krok wykonywalny przed realnym hardware
- bench report template jest spojny z kontraktem testowym i governance
- dokumenty wprost mowia, czego symulacja nie potwierdza
- pack po zmianie ma czytelniejsza sciezke `simulated precheck -> real hardware bench`

## 7. Walidacja

- `python3 -m py_compile` dla nowego skryptu, jesli powstal
- sensowny dry-run na sample board profile, jesli to mozliwe
- kontrola spojnosci z `BENCH_TEST_CONTRACT_ESP_RUNTIME_01.md`
- `git diff --check`

## 8. Blokery

Brak realnej plytki nie jest blockerem dla tego zadania.
Blokerem jest udawanie, ze symulacja zastapila realny bench test.

## 9. Mini-handoff

Zapisz:

- jaki precheck albo template dodano,
- co pack umie wykonac bez realnej plytki,
- co nadal wymaga realnego hardware,
- jaki jest nowy gate przed pierwszym runtime runem.
