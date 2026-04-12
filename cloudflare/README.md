# Cloudflare Workers: wariant wdrożeniowy `v1`

Ten katalog zawiera wariant wdrożeniowy dla centralnego API pilotażu stawu hodowlanego oparty o **Cloudflare Workers** i **D1**.

## Po co ten wariant

Ten wariant ma umożliwić szybkie wystawienie publicznego API dla providerów danych bez konieczności utrzymywania klasycznego serwera od pierwszego dnia.

To szczególnie dobrze pasuje do modelu:

- stary smartfon lub ESP32 zbiera dane,
- provider rejestruje się w centralnym API,
- obserwacje i zdarzenia trafiają do wspólnej warstwy operacyjnej,
- repozytorium przechowuje wiedzę i standard, a nie surowy strumień danych.

## Co zawiera katalog

- `wrangler.toml` — konfiguracja Worker'a,
- `src/worker.js` — implementacja endpointów API,
- `src/recommendation.js` — lekka logika rekomendacyjna,
- `migrations/0001_init.sql` — inicjalizacja bazy D1.

## Obsługiwane endpointy

```text
POST /v1/providers/register
POST /v1/observations
POST /v1/events
POST /v1/recommendations/fish-pond
GET /v1/providers/{provider_id}/status
```

## Jak wdrożyć

1. Zainstaluj `wrangler`.
2. Utwórz bazę D1.
3. Podepnij binding `DB` w `wrangler.toml`.
4. Uruchom migrację.
5. Wdróż Worker'a.

Przykładowy przebieg:

```bash
wrangler d1 create fish-pond-v1
wrangler d1 migrations apply DB
wrangler deploy
```

## Uwaga architektoniczna

To jest warstwa operacyjna. Surowe bieżące dane providerów trafiają tutaj, a nie do repozytorium. Repozytorium pozostaje miejscem dla:

- schematów,
- adapterów,
- modeli,
- sample data,
- dokumentacji,
- wiedzy opracowanej.
