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
- `migrations/0001_init.sql` — inicjalizacja bazy D1,
- `provider_smoke_test.py` — smoke test publicznego endpointu po wdrożeniu.

## Obsługiwane endpointy

```text
POST /v1/providers/register
POST /v1/providers/{provider_id}/tokens/rotate
POST /v1/observations
POST /v1/events
POST /v1/recommendations/fish-pond
GET /v1/providers/{provider_id}/status
```

## Autoryzacja providera

Po rejestracji provider otrzymuje jednorazowo `write_token`.

Ten token należy przekazywać w nagłówku:

```text
X-Provider-Token
```

Token jest wymagany dla:

- `POST /v1/providers/{provider_id}/tokens/rotate`
- `POST /v1/observations`
- `POST /v1/events`
- `POST /v1/recommendations/fish-pond`

Powtórna rejestracja tego samego `provider_id` nie służy do odnowienia dostępu. Worker zwraca w takiej sytuacji `409`, a prawidłową ścieżką jest rotacja tokenu.

## Jak wdrożyć

Pełny proces operatorski jest opisany w:

- [`docs/RUNBOOK_WDROZENIA_CLOUDFLARE_D1.md`](../docs/RUNBOOK_WDROZENIA_CLOUDFLARE_D1.md)

Najkrótsza ścieżka wygląda tak:

```bash
npx wrangler d1 create fish-pond-v1 --location=weur
npx wrangler d1 migrations list DB --remote
npx wrangler d1 migrations apply DB --remote
npx wrangler deploy
python3 cloudflare/provider_smoke_test.py https://fish-pond-api-v1.<twoj-subdomain>.workers.dev --provider-environment preview
```

## Polityka środowisk providera

Worker może ograniczać, jakie `provider_id` są dopuszczone w danym środowisku przez:

- `DEPLOYMENT_ENVIRONMENT`
- `ALLOWED_PROVIDER_ENVIRONMENTS`

Przykładowa polityka:

- `preview` przyjmuje `demo,preview`
- `staging` przyjmuje `staging`
- `prod` przyjmuje `prod`

Dlatego smoke test powinien używać environment zgodnego z aktywną konfiguracją Worker'a.

## Uwaga architektoniczna

To jest warstwa operacyjna. Surowe bieżące dane providerów trafiają tutaj, a nie do repozytorium. Repozytorium pozostaje miejscem dla:

- schematów,
- adapterów,
- modeli,
- sample data,
- dokumentacji,
- wiedzy opracowanej.

## Eksport wiedzy

Zgromadzone dane operacyjne powinny być okresowo przekształcane w snapshoty wiedzy, anonimizowane raporty i przypadki opisane w repozytorium, a nie kopiowane tam w postaci pełnych dumpów.

## Utrata tokenu

W wersji `v1` odzyskiwanie dostępu bez aktualnego tokenu nie jest jeszcze zautomatyzowane. To celowo minimalny model bezpieczeństwa.

Jeżeli provider ma ważny token, powinien obrócić go przez:

```text
POST /v1/providers/{provider_id}/tokens/rotate
```

Szczegóły procesu organizacyjnego są opisane w:

- [`docs/RUNBOOK_ODZYSKIWANIA_DOSTEPU_PROVIDERA.md`](../docs/RUNBOOK_ODZYSKIWANIA_DOSTEPU_PROVIDERA.md)

## Pierwszy publiczny deployment

Pierwsze środowisko publiczne nie powinno być uznane za gotowe tylko dlatego, że `wrangler deploy` zakończył się bez błędu. Warunkiem wejścia w pracę z realnymi providerami jest przejście smoke testu end-to-end.
