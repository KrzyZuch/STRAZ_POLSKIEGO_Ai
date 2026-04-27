# Zlecenie Glowne 33 Project13 Blueprint Brief Row Validation And Smoke Test Baseline

## 1. Misja zadania

Utwardz execution surface `blueprint-design-01` po zadaniu `27`: dodaj brakujaca walidacje wierszy sekcji briefu i minimalny smoke-test baseline, tak zeby dry-run nie przyjmowal zbyt latwo zlego inputu tylko dlatego, ze glowne pola sa formalnie obecne.

## 2. Wyzszy cel organizacji

To zadanie zmniejsza ryzyko, ze nowy dry-run `blueprint` bedzie wygladal wiarygodnie mimo zlego briefu. Po nim pack ma byc nie tylko uruchamialny, ale tez troche bardziej odporny na bledy wejscia.

## 3. Read First

- `docs/AGENTY_PODWYKONAWCZE/ODBIOR_PORTFELA_08_ZADAN_23_28_2026-04-27.md`
- `docs/AGENTY_PODWYKONAWCZE/MINI_HANDOFF_ZADANIE_27.md`
- `PROJEKTY/13_baza_czesci_recykling/scripts/validate_design_brief.py`
- `PROJEKTY/13_baza_czesci_recykling/scripts/dry_run_blueprint_design.py`
- `PROJEKTY/13_baza_czesci_recykling/docs/SAMPLE_DESIGN_BRIEF_WIFI_TEMP_SENSOR.md`
- `PROJEKTY/13_baza_czesci_recykling/execution_packs/pack-project13-blueprint-design-01/`

## 4. Write Scope

- `PROJEKTY/13_baza_czesci_recykling/scripts/`
- `PROJEKTY/13_baza_czesci_recykling/docs/`
- `PROJEKTY/13_baza_czesci_recykling/execution_packs/pack-project13-blueprint-design-01/`
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/`

## 5. Deliverables

- mocniejsza walidacja wierszy sekcji reuse parts / missing parts / assumptions
- minimalny smoke-test baseline dla nowego dry-run surface
- jesli potrzeba: nowy invalid sample albo check opisany w runbooku
- mini-handoff z tym, jakie klasy bledow briefu sa teraz lapane wczesniej

## 6. Acceptance Criteria

- zle sformatowane albo wewnetrznie sprzeczne wiersze briefu sa wychwytywane przed dry-runem albo bardzo jawnie raportowane
- sample brief dalej przechodzi sensowny dry-run
- istnieje minimalny, powtarzalny sposob smoke-testu dla execution surface `blueprint`
- zadanie nie probuje udawac pelnego generatora CAD ani rozszerzac scope packa poza dry-run

## 7. Walidacja

- `python3 -m py_compile PROJEKTY/13_baza_czesci_recykling/scripts/validate_design_brief.py`
- `python3 -m py_compile PROJEKTY/13_baza_czesci_recykling/scripts/dry_run_blueprint_design.py`
- lokalny dry-run na `SAMPLE_DESIGN_BRIEF_WIFI_TEMP_SENSOR.md`
- jesli dodasz invalid sample albo smoke-test helper: uruchom go i zapisz wynik
- `git diff --check`

## 8. Blokery

Nie rozwijaj tego zadania w strone wielkiego frameworka testowego.
Ma dowiezc praktyczne utwardzenie obecnego surface, nie nowy poboczny projekt.

## 9. Mini-handoff

Zapisz:

- jaka walidacja zostala dodana,
- jaki jest nowy smoke-test baseline,
- jakie klasy bledow briefu sa teraz lapane,
- czego nadal nie obejmuje ten dry-run.
