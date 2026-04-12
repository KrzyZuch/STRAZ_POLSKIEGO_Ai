---
name: Utrata dostępu providera
about: Zgłoszenie utraty tokenu lub potrzeby ręcznego odzyskania dostępu do providera danych
title: "[provider-access] "
---

## Typ problemu

- [ ] utrata `write_token`
- [ ] potrzeba ręcznej rotacji tokenu
- [ ] brak dostępu do istniejącego `provider_id`
- [ ] inny problem z dostępem operacyjnym

## Identyfikacja providera

- `provider_id`:
- `provider_label`:
- `provider_kind`:
- `node_class`:

## Co się wydarzyło

Opisz krótko:

- kiedy utracono dostęp,
- czy token był wcześniej aktywny,
- czy provider nadal wysyła dane,
- czy problem dotyczy środowiska lokalnego, testowego czy publicznego.

## Dowody i kontekst

Podaj tylko bezpieczne informacje:

- link do wcześniejszego zgłoszenia providera,
- identyfikatory węzła lub stawu,
- opis ostatnich poprawnych żądań,
- informację, kto utrzymywał węzeł.

Nie wklejaj publicznie aktywnego tokenu ani innych sekretów.

## Wpływ na projekt

Opisz:

- czy zatrzymane jest dostarczanie danych,
- czy potrzebne jest pilne przywrócenie działania,
- czy problem blokuje rozwój adaptera, testów lub dokumentacji.

## Proponowane działanie

- [ ] proszę o ręczną rotację tokenu
- [ ] proszę o weryfikację tożsamości providera
- [ ] proszę o pomoc w migracji na nowy `provider_id`
- [ ] proszę o konsultację architektury dostępu
