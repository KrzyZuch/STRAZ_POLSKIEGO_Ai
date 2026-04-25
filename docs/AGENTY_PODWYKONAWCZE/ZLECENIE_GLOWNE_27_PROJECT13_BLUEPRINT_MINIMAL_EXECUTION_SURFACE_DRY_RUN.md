# Zlecenie Glowne 27 Project13 Blueprint Minimal Execution Surface Dry Run

## 1. Misja zadania

Po walidatorze z zadania `21` dowiez pierwszy minimalny execution surface dla `pack-project13-blueprint-design-01`, ktory bierze poprawny brief i generuje review-ready, suchy artefakt zamiast zostawiac pack w stanie czysto kontraktowym.

## 2. Wyzszy cel organizacji

To zadanie przesuwa `blueprint-design-01` z "umiemy sprawdzic input" do "umiemy zrobic pierwszy kontrolowany dry-run".

## 3. Read First

- `docs/HANDOFF_DLA_NASTEPNEGO_AGENTA_2026-04-25.md`
- `docs/AGENTY_PODWYKONAWCZE/ODBIOR_PORTFELA_07_ZADAN_17_22_2026-04-25.md`
- `docs/AGENTY_PODWYKONAWCZE/MINI_HANDOFF_ZADANIE_21.md`
- `PROJEKTY/13_baza_czesci_recykling/scripts/validate_design_brief.py`
- `PROJEKTY/13_baza_czesci_recykling/docs/SAMPLE_DESIGN_BRIEF_WIFI_TEMP_SENSOR.md`
- `PROJEKTY/13_baza_czesci_recykling/execution_packs/pack-project13-blueprint-design-01/`

## 4. Write Scope

- `PROJEKTY/13_baza_czesci_recykling/scripts/`
- `PROJEKTY/13_baza_czesci_recykling/execution_packs/pack-project13-blueprint-design-01/`
- `PROJEKTY/13_baza_czesci_recykling/docs/`
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/`

## 5. Deliverables

- minimalny skrypt dry-run dla `blueprint-design-01`
- review-ready output artifact albo report z dry-run
- aktualizacja runbooka, manifestu i readiness gate packa
- mini-handoff z tym, czego nadal brakuje do prawdziwego execution surface

## 6. Acceptance Criteria

- pack potrafi przetworzyc poprawny brief w kontrolowany dry-run
- dry-run nie udaje jeszcze finalnego generatora CAD/BOM, jesli repo nie jest na to gotowe
- output artifact ma czytelny kontrakt i da sie go zreviewowac
- status packa po zmianie jest bardziej wykonawczy niz `draft`, ale bez sztucznego przeskakiwania gate'ow

## 7. Walidacja

- `python3 -m py_compile` dla nowego skryptu, jesli powstal
- lokalny dry-run na `SAMPLE_DESIGN_BRIEF_WIFI_TEMP_SENSOR.md`
- `git diff --check`

## 8. Blokery

Nie probuj generowac "prawdziwych" wynikow CAD, jesli repo nie ma jeszcze takich zaleznosci i danych.
Dowiez minimalny, uczciwy execution surface.

## 9. Mini-handoff

Zapisz:

- jaki dry-run surface dodano,
- jaki artefakt powstaje z poprawnego briefu,
- jaki jest nowy status `blueprint-design-01`,
- czego nadal brakuje do pierwszego realnego runu.
