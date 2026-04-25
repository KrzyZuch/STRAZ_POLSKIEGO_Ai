# Zlecenie Glowne 26 Project13 Codeowners And Review Enforcement Baseline

## 1. Misja zadania

Domknij kolejny krok po `20`: dodaj review ownership baseline i uporzadkuj, jak `CODEOWNERS`, secret scan i branch protection maja razem wspierac uczciwy review toru wolontariackiego.

## 2. Wyzszy cel organizacji

To zadanie zmniejsza ryzyko, ze review pozostanie zwyczajem jednej osoby zamiast jawnego mechanizmu.

## 3. Read First

- `docs/HANDOFF_DLA_NASTEPNEGO_AGENTA_2026-04-25.md`
- `docs/AGENTY_PODWYKONAWCZE/ODBIOR_PORTFELA_07_ZADAN_17_22_2026-04-25.md`
- `docs/AGENTY_PODWYKONAWCZE/MINI_HANDOFF_ZADANIE_20.md`
- `PROJEKTY/13_baza_czesci_recykling/docs/BRANCH_PROTECTION_OPERATOR_PACKET.md`
- `PROJEKTY/13_baza_czesci_recykling/docs/PILOT_REVIEW_ASSIGNMENT_AND_APPROVAL_PATH.md`
- `PROJEKTY/13_baza_czesci_recykling/docs/PUBLIC_VOLUNTEER_RUN_READINESS.md`
- `.github/workflows/pr_secret_scan.yml`

## 4. Write Scope

- `.github/`
- `PROJEKTY/13_baza_czesci_recykling/docs/`
- `PROJEKTY/13_baza_czesci_recykling/execution_packs/pack-project13-kaggle-enrichment-01/`
- ewentualnie `README.md`

## 5. Deliverables

- baseline `.github/CODEOWNERS`
- doprecyzowany packet lub README review enforcement dla maintainera
- aktualizacja readiness i checklist review tam, gdzie to potrzebne
- mini-handoff z tym, co dalej musi byc zrobione po stronie upstream

## 6. Acceptance Criteria

- review ownership nie jest juz tylko opisane tekstowo, ale ma jawny baseline w repo
- dokumenty jasno mowia, jak `CODEOWNERS`, secret scan i branch protection sie uzupelniaja
- nie jest udawane, ze upstream branch protection zostalo juz wymuszone, jesli nadal trzeba to zrobic recznie
- wynik zmniejsza przynajmniej jedna praktyczna niejasnosc dla maintainera przygotowujacego pilota

## 7. Walidacja

- kontrola spojnosci z `PUBLIC_VOLUNTEER_RUN_READINESS.md`
- kontrola spojnosci z `PILOT_REVIEW_ASSIGNMENT_AND_APPROVAL_PATH.md`
- jesli powstaje `.github/CODEOWNERS`, sprawdz czy pokrywa krytyczne sciezki pilota
- `git diff --check`

## 8. Blokery

Jesli nie da sie nazwac konkretnych osob w `CODEOWNERS`, dowiez baseline oparty o role albo katalogi wymagajace review i jawnie opisz, co musi uzupelnic maintainer.

## 9. Mini-handoff

Zapisz:

- jaki baseline review enforcement dodano,
- jak `CODEOWNERS` mapuje sie na pilotowy tor review,
- ktore pozycje readiness przesunely sie do przodu,
- co nadal zostaje po stronie upstream albo maintainera.
