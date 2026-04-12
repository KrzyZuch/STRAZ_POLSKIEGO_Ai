# Runbook Odzyskiwania Dostępu Providera

## Cel dokumentu

Ten dokument opisuje minimalny, operacyjny proces odzyskiwania dostępu do istniejącego providera danych w ekosystemie Straży Przyszłości.

Wersja `v1` nie udostępnia publicznego, samoobsługowego resetu tokenu bez wcześniejszego sekretu. Z tego powodu odzyskiwanie dostępu musi być realizowane przez maintainera lub operatora warstwy operacyjnej.

## Kiedy używać tego runbooka

Użyj tego procesu, gdy:

- provider utracił `write_token`,
- węzeł edge zmienił urządzenie i nie ma już starego sekretu,
- społecznościowy provider potrzebuje ręcznej rotacji dostępu,
- trzeba sprawdzić, czy `provider_id` istnieje przed dalszą diagnostyką.

## Zasady bezpieczeństwa

- nie publikuj aktywnego `write_token` w Issue, README ani komentarzach,
- nie resetuj dostępu przez ponowną rejestrację tego samego `provider_id`,
- najpierw ustal, czy osoba zgłaszająca ma prawo reprezentować danego providera,
- nowy token przekazuj poza publicznym repozytorium, bezpiecznym kanałem organizacyjnym.

## Kanał zgłoszenia

Provider powinien otworzyć zgłoszenie przez szablon:

- [Utrata dostępu providera](../.github/ISSUE_TEMPLATE/utrata_dostepu_providera.md)

To zgłoszenie ma służyć zebraniu bezpiecznego kontekstu, a nie przekazywaniu sekretów.

## Minimalna procedura maintainera

1. Zweryfikuj `provider_id` i sprawdź, czy provider rzeczywiście istnieje w bazie operacyjnej.
2. Oceń, czy zgłoszenie jest wiarygodne i czy dotyczy właściwego podmiotu.
3. Jeśli to uzasadnione, wykonaj ręczną rotację tokenu w warstwie operacyjnej.
4. Przekaż nowy `write_token` bezpiecznym kanałem poza publicznym repozytorium.
5. Poproś providera o natychmiastową aktualizację sekretu w urządzeniu, smartfonie lub bramce danych.
6. Zamknij zgłoszenie dopiero po potwierdzeniu odzyskania działania.

## Narzędzie administracyjne dla lokalnej bazy SQLite

W wariancie lokalnym maintainer może użyć:

```bash
python3 api/admin_provider_access.py list
python3 api/admin_provider_access.py status community-demo-node-01
python3 api/admin_provider_access.py rotate-token community-demo-node-01
```

Własna ścieżka bazy:

```bash
python3 api/admin_provider_access.py --db-path /tmp/straz_fish_pond_v1.db rotate-token community-demo-node-01
```

## Oczekiwany rezultat rotacji

Po rotacji:

- stary token przestaje działać,
- nowy token jest zwracany jednorazowo,
- `provider_id` pozostaje bez zmian,
- historia obserwacji i powiązanie z bazą wiedzy pozostają ciągłe.

## Wariant Cloudflare / D1

W środowisku Cloudflare utrata dostępu również powinna być obsługiwana ręcznie. Publiczny Worker nie udostępnia jeszcze samoobsługowego resetu bez ważnego sekretu.

Przy pracy z D1 należy zachować te same zasady:

- najpierw weryfikacja tożsamości providera,
- następnie ręczna rotacja dostępu przez operatora,
- na końcu bezpieczne przekazanie nowego tokenu poza publicznym repozytorium.

## Co trafia do repozytorium po incydencie

Do repozytorium mogą trafić:

- opis przypadku,
- wnioski procesowe,
- poprawki dokumentacji,
- nowe testy i usprawnienia runbooka.

Do repozytorium nie trafiają:

- aktywne tokeny,
- pełne dane operacyjne z incydentu,
- zrzuty z sekretami lub konfiguracją prywatną providera.
