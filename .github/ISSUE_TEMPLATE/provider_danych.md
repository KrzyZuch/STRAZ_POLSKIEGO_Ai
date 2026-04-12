---
name: Provider danych / węzeł pomiarowy
about: Zgłoszenie nowego providera danych lub społecznościowego węzła pomiarowego do API Straży Przyszłości
title: "[provider] "
---

## Typ zgłoszenia

- [ ] nowy provider danych
- [ ] nowy węzeł pomiarowy
- [ ] stary smartfon jako bramka danych
- [ ] integracja z istniejącą platformą

## Kim jesteś

Opisz krótko, czy jesteś:

- członkiem społeczności,
- gospodarstwem,
- zespołem badawczym,
- partnerem zewnętrznym,
- autorem projektu DIY.

## Opis providera lub węzła

- `provider_id`:
- `provider_kind`:
- `provider_label`:
- `node_class`:

## Jakie dane chcesz dostarczać

Zaznacz lub opisz:

- [ ] temperatura wody
- [ ] dissolved oxygen
- [ ] pH
- [ ] amoniak
- [ ] przepływ
- [ ] poziom wody
- [ ] edge vision / fish_behavior_summary
- [ ] inne:

## Jak działa Twój węzeł

Opisz architekturę:

- sprzęt,
- czujniki,
- komunikacja,
- źródło zasilania,
- czy używasz starego smartfona,
- czy dane są lokalnie buforowane.

## Integracja z API

- [ ] chcę wysyłać `POST /v1/providers/register`
- [ ] chcę wysyłać `POST /v1/observations`
- [ ] chcę wysyłać `POST /v1/events`
- [ ] chcę odbierać `POST /v1/recommendations/fish-pond`
- [ ] potrzebuję pomocy z mapowaniem do schematu `fish_pond_v1`

## Przykładowy payload lub opis formatu danych

Wklej przykładowy payload, CSV albo opisz format danych.

```json
{}
```

## Ograniczenia i uwagi

Opisz wszystko, co może być ważne dla integracji:

- ograniczenia sprzętowe,
- niestabilne łącze,
- niska częstotliwość odczytu,
- brak pełnej kalibracji,
- charakter eksperymentalny rozwiązania.

## Co chcesz wnieść do Straży Przyszłości

Opisz, jaki realny wkład chcesz wnieść:

- dane,
- dokumentację,
- adapter,
- testy,
- know-how,
- architekturę węzła,
- analizę zachowania ryb,
- inne.
