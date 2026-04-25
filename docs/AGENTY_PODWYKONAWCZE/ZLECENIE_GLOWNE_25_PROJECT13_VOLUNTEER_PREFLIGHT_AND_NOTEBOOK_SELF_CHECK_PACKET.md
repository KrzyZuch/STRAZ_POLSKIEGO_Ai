# Zlecenie Glowne 25 Project13 Volunteer Preflight And Notebook Self Check Packet

## 1. Misja zadania

Domknij praktyczny pre-flight dla wolontariusza: zanim ktos odpali notebook albo lokalny run, ma wiedziec jak sprawdzic scope `GITHUB_PAT`, obecnosci sekretow, ryzyko quota i podstawowe self-checki notebooka.

## 2. Wyzszy cel organizacji

To zadanie zmniejsza koszt wejscia i liczbe falszywych startow. Wolontariusz ma szybciej dojsc do sensownej pracy, a nie dopiero po nieudanym odpaleniu zorientowac sie, ze brakuje mu scope albo quota.

## 3. Read First

- `docs/HANDOFF_DLA_NASTEPNEGO_AGENTA_2026-04-25.md`
- `docs/WOLONTARIUSZE_GOTOWE_PRZYDZIALY.md`
- `docs/AGENTY_PODWYKONAWCZE/ODBIOR_PORTFELA_07_ZADAN_17_22_2026-04-25.md`
- `docs/AGENTY_PODWYKONAWCZE/MINI_HANDOFF_ZADANIE_19.md`
- `PROJEKTY/13_baza_czesci_recykling/README.md`
- `PROJEKTY/13_baza_czesci_recykling/docs/PUBLIC_VOLUNTEER_RUN_READINESS.md`
- `PROJEKTY/13_baza_czesci_recykling/execution_packs/pack-project13-kaggle-enrichment-01/RUNBOOK.md`

## 4. Write Scope

- `PROJEKTY/13_baza_czesci_recykling/README.md`
- `PROJEKTY/13_baza_czesci_recykling/docs/PUBLIC_VOLUNTEER_RUN_READINESS.md`
- `PROJEKTY/13_baza_czesci_recykling/docs/`
- `PROJEKTY/13_baza_czesci_recykling/execution_packs/pack-project13-kaggle-enrichment-01/`
- `docs/WOLONTARIUSZE_GOTOWE_PRZYDZIALY.md`
- ewentualnie `PROJEKTY/13_baza_czesci_recykling/scripts/`

## 5. Deliverables

- jawny pre-flight checklist albo packet dla wolontariusza
- instrukcja self-check: scope `GITHUB_PAT`, obecne sekrety, quota warning, minimalny smoke check notebooka
- aktualizacja readiness i kanonicznych materialow onboardingowych
- mini-handoff z tym, czego nadal nie da sie sprawdzic bez realnego wolontariusza

## 6. Acceptance Criteria

- wolontariusz dostaje prosty pre-flight przed pierwszym runem
- scope `GITHUB_PAT` i problem quota nie pozostaja juz tylko uwaga w mini-handoffie
- kanoniczny onboarding dalej startuje z `docs/WOLONTARIUSZE_GOTOWE_PRZYDZIALY.md`
- dokumenty nie udaja, ze quota lub sekret mozna potwierdzic bez realnego konta, jesli to niemozliwe

## 7. Walidacja

- kontrola spojnosci miedzy `README.md`, readiness, runbookiem i onboardingiem wolontariusza
- jesli powstanie skrypt pre-flight: lokalny dry-run bez sekretow ma dawac czytelny wynik
- `git diff --check`

## 8. Blokery

Nie tworz fikcyjnego "automatycznego sprawdzacza quota", jesli nie ma wiarygodnego sposobu zrobienia tego offline.
Dowiez przynajmniej uczciwy packet self-check i nazwy rzeczy, ktore musi potwierdzic wolontariusz.

## 9. Mini-handoff

Zapisz:

- jaki pre-flight dodano,
- jak wolontariusz ma sprawdzic scope i sekrety,
- ktore punkty readiness to domknelo,
- czego nadal nie da sie potwierdzic bez realnego runu.
