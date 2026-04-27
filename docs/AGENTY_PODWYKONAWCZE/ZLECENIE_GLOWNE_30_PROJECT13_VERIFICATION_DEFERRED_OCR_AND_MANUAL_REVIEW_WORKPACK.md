# Zlecenie Glowne 30 Project13 Verification Deferred OCR And Manual Review Workpack

## 1. Misja zadania

Zamien pozostale deferred cases z verification w operator-ready workpack: `7` rekordow `ocr_needed` i `2` rekordy `manual_review` maja dostac jawny packet z evidence, komenda lub procedura nastepnego kroku i miejscem na decyzje, tak zeby kolejna sesja nie musiala odtwarzac kontekstu od zera.

## 2. Wyzszy cel organizacji

To zadanie zmniejsza koszt poznawczy wokol ostatnich `9` blokad verified snapshotu. Zamiast "wiemy, ze cos jeszcze blokuje", repo ma miec gotowy pakiet operacyjny do domkniecia tych przypadkow.

## 3. Read First

- `docs/AGENTY_PODWYKONAWCZE/ODBIOR_PORTFELA_08_ZADAN_23_28_2026-04-27.md`
- `docs/AGENTY_PODWYKONAWCZE/MINI_HANDOFF_ZADANIE_23.md`
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/status_resolution_packet.json`
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/verification_report.md`
- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/verification_triage.jsonl`
- `PROJEKTY/13_baza_czesci_recykling/scripts/verify_candidates.py`
- `PROJEKTY/13_baza_czesci_recykling/execution_packs/pack-project13-kaggle-verification-01/RUNBOOK.md`

## 4. Write Scope

- `PROJEKTY/13_baza_czesci_recykling/autonomous_test/reports/`
- `PROJEKTY/13_baza_czesci_recykling/execution_packs/pack-project13-kaggle-verification-01/`
- `PROJEKTY/13_baza_czesci_recykling/docs/`
- ewentualnie `PROJEKTY/13_baza_czesci_recykling/scripts/verify_candidates.py`

## 5. Deliverables

- jawny deferred resolution packet dla `ocr_needed` i `manual_review`
- lista `candidate_id` / `part_number` / `device` / `evidence_url` / `next_action`
- jasna procedura: co uruchomic przy dostepnym `GEMINI_API_KEY`, a co wymaga czlowieka
- jesli to pomaga: drobny helper lub ujednolicony format packetu
- mini-handoff z tym, ile cases jest gotowych do nastepnego ruchu

## 6. Acceptance Criteria

- kazdy z `9` deferred cases ma jawnie zapisany nastepny krok, a nie tylko etykiete
- packet rozroznia `ocr_needed` od `manual_review` i nie miesza tych torow
- dokumenty nie udaja, ze OCR albo review juz sie wydarzyly
- kolejny agent moze zamknac case po samym packetcie, bez ponownego sledztwa w wielu plikach

## 7. Walidacja

- kontrola zgodnosci counts z `status_resolution_packet.json`
- kontrola zgodnosci evidence URLs / part numbers z verified snapshotem
- jesli dodajesz helper: `python3 -m py_compile PROJEKTY/13_baza_czesci_recykling/scripts/verify_candidates.py`
- `git diff --check`

## 8. Blokery

Brak `GEMINI_API_KEY` nie blokuje tego zadania.
Nie wolno jednak oznaczac OCR cases jako rozwiazane bez realnego przebiegu OCR.

## 9. Mini-handoff

Zapisz:

- ile cases jest `ocr_needed`, a ile `manual_review`,
- jaki packet lub helper dodano,
- co dokladnie trzeba zrobic, gdy pojawi sie `GEMINI_API_KEY`,
- ktore decisions nadal wymagaja czlowieka.
