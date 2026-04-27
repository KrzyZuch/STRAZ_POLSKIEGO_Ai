# Zlecenie Glowne 32 Project13 Public Volunteer Canary Packet And Retro Template

## 1. Misja zadania

Przeloz nowy pre-flight i review baseline na kontrolowany packet pierwszego pilota wolontariackiego: jeden material przed sesja, jedna checklista stop conditions w trakcie i jeden retro template po sesji. Nie chodzi o udawanie, ze pilot juz byl, tylko o przygotowanie go bez chaosu.

## 2. Wyzszy cel organizacji

To zadanie zmniejsza ryzyko, ze pierwszy wolontariusz wejdzie w proces, ktory technicznie jest opisany, ale organizacyjnie dalej jest rozproszony po kilku plikach. Canary packet ma zrobic z tego jedna wspolna sekwencje.

## 3. Read First

- `docs/WOLONTARIUSZE_GOTOWE_PRZYDZIALY.md`
- `docs/AGENTY_PODWYKONAWCZE/ODBIOR_PORTFELA_08_ZADAN_23_28_2026-04-27.md`
- `docs/AGENTY_PODWYKONAWCZE/MINI_HANDOFF_ZADANIE_25.md`
- `docs/AGENTY_PODWYKONAWCZE/MINI_HANDOFF_ZADANIE_26.md`
- `PROJEKTY/13_baza_czesci_recykling/docs/VOLUNTEER_PREFLIGHT_CHECKLIST.md`
- `PROJEKTY/13_baza_czesci_recykling/docs/PUBLIC_VOLUNTEER_RUN_READINESS.md`
- `PROJEKTY/13_baza_czesci_recykling/docs/PILOT_REVIEW_ASSIGNMENT_AND_APPROVAL_PATH.md`
- `PROJEKTY/13_baza_czesci_recykling/execution_packs/pack-project13-kaggle-enrichment-01/RUNBOOK.md`

## 4. Write Scope

- `docs/WOLONTARIUSZE_GOTOWE_PRZYDZIALY.md`
- `PROJEKTY/13_baza_czesci_recykling/docs/`
- `PROJEKTY/13_baza_czesci_recykling/README.md`
- `PROJEKTY/13_baza_czesci_recykling/execution_packs/pack-project13-kaggle-enrichment-01/`

## 5. Deliverables

- canary pilot packet dla pierwszego wolontariusza
- retro template po pierwszej sesji
- jawne stop conditions i escalation points
- aktualizacja onboardingowych i readiness materialow tam, gdzie trzeba
- mini-handoff z tym, czego nadal nie da sie zasymulowac bez realnego pilota

## 6. Acceptance Criteria

- pierwszy pilot jest opisany jako `controlled canary`, a nie zwykly publiczny run
- wolontariusz i maintainer widza te sama sekwencje: przed sesja, w trakcie, po sesji
- istnieja jawne stop conditions, kiedy przerwac run zamiast "przepychac na sile"
- retro i feedback capture sa przygotowane, ale zadanie nie udaje, ze retro juz zostalo wykonane

## 7. Walidacja

- kontrola spojnosci miedzy `WOLONTARIUSZE_GOTOWE_PRZYDZIALY.md`, readiness, runbookiem i nowym packetem
- jesli powstaja nowe checklisty lub template'y: sprawdz, czy sa referencjonowane z kanonicznych plikow
- `git diff --check`

## 8. Blokery

Brak realnego wolontariusza nie blokuje tego zadania.
Blokerem byloby dopiero udawanie, ze gotowosc organizacyjna sama wynika z istnienia kilku rozproszonych dokumentow.

## 9. Mini-handoff

Zapisz:

- jaki canary packet dodano,
- jakie sa stop conditions i escalation points,
- jak ma wygladac retro po pierwszej sesji,
- czego nadal nie potwierdzono bez realnego wolontariusza.
