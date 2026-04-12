# Runbook Wdrożenia Cloudflare Workers + D1

## Cel dokumentu

Ten dokument opisuje minimalny, praktyczny proces uruchomienia pierwszego publicznego środowiska dla pilotażu stawu hodowlanego przy użyciu **Cloudflare Workers** i **D1**.

Runbook dotyczy warstwy operacyjnej. Repozytorium pozostaje centrum standardu, logiki, dokumentacji i wiedzy opracowanej, natomiast bieżące dane providerów trafiają do wdrożonego API.

## Co powinno być gotowe przed wdrożeniem

- zaktualizowany kod Worker'a w `cloudflare/src/worker.js`,
- gotowa migracja bazy w `cloudflare/migrations/0001_init.sql`,
- uzupełniony `cloudflare/wrangler.toml`,
- przygotowany operator środowiska,
- ustalony kanał bezpiecznego przekazywania `write_token` po rejestracji providerów.

## 1. Zweryfikuj narzędzie Wrangler

Cloudflare zaleca uruchamianie Wranglera lokalnie w projekcie przez `npx wrangler`.

Minimalne sprawdzenie:

```bash
npx wrangler --version
```

Jeżeli trzeba, zaloguj operatora do Cloudflare zgodnie z lokalnym procesem organizacyjnym.

## 2. Utwórz bazę D1

Oficjalna komenda tworzenia bazy:

```bash
npx wrangler d1 create fish-pond-v1 --location=weur
```

Po utworzeniu bazy:

- zapisz `database_id`,
- uzupełnij `database_id` w `cloudflare/wrangler.toml`,
- ustaw `preview_database_id`.

Przed deploymentem wybierz też politykę środowiska providera:

- `preview` zwykle przyjmuje `demo,preview`,
- `staging` zwykle przyjmuje `staging`,
- `prod` powinno przyjmować `prod`.

Jeżeli nie używasz osobnej bazy preview, możesz tymczasowo ustawić `preview_database_id` na to samo ID co produkcyjne, ale dla środowisk rozwijanych długoterminowo lepiej rozdzielić preview i production.

## 3. Zweryfikuj konfigurację `wrangler.toml`

Repozytorium utrzymuje konfigurację w `wrangler.toml`, mimo że Cloudflare dla nowych projektów promuje też `wrangler.jsonc`.

W tym projekcie kluczowe elementy to:

- `name`
- `main`
- `compatibility_date`
- `workers_dev`
- `observability`
- `vars`
- `[[d1_databases]]`

Szczególnie ważne:

- `preview_database_id` jest wymagane przy `wrangler dev --remote`,
- `DEPLOYMENT_ENVIRONMENT` i `ALLOWED_PROVIDER_ENVIRONMENTS` określają, jakie `provider_id` będą wpuszczane do API,
- `observability` pomaga od początku zbierać logi i diagnostykę środowiska.

## 4. Sprawdź migracje przed wdrożeniem

Lista migracji do zastosowania na zdalnej bazie:

```bash
npx wrangler d1 migrations list DB --remote
```

Zastosowanie migracji:

```bash
npx wrangler d1 migrations apply DB --remote
```

Cloudflare dokumentuje, że przy `migrations apply` po zastosowaniu migracji tworzony jest backup, a w razie błędu bieżąca migracja jest wycofywana.

## 5. Wdróż Worker

Pierwsze i kolejne wdrożenia:

```bash
npx wrangler deploy
```

Po udanym wdrożeniu zapisz:

- publiczny adres `workers.dev`,
- czas wdrożenia,
- wersję commita repozytorium,
- operatora wykonującego deployment.

## 6. Uruchom smoke test publicznego endpointu

Po wdrożeniu od razu wykonaj pełny test ścieżki providera:

```bash
python3 cloudflare/provider_smoke_test.py https://fish-pond-api-v1.<twoj-subdomain>.workers.dev --provider-environment preview
```

Skrypt sprawdza:

- rejestrację providera,
- rotację tokenu,
- przyjęcie obserwacji,
- przyjęcie zdarzenia,
- wygenerowanie rekomendacji,
- odczyt statusu providera.

Smoke test powinien przejść w całości przed zaproszeniem pierwszych realnych providerów.

## 7. Co zrobić po pierwszym udanym deploymencie

- zapisać wynik smoke testu w notatce operatorskiej,
- otworzyć Issue lub wpis wiedzy, jeśli pojawiły się problemy,
- nie publikować aktywnych `write_token`,
- przekazać adres API i zasady onboardingu pierwszym providerom.

## 8. Procedura rollback

Jeżeli nowy deployment okaże się błędny, Cloudflare udostępnia rollback wersji Worker'a:

```bash
npx wrangler rollback
```

Lub do konkretnej wersji:

```bash
npx wrangler rollback <VERSION_ID>
```

Rollback Worker'a nie cofa automatycznie zmian procesowych po stronie providerów, dlatego po rollbacku trzeba ponownie wykonać smoke test.

## 9. Minimalna checklista operatora

- [ ] `database_id` i `preview_database_id` są ustawione
- [ ] `DEPLOYMENT_ENVIRONMENT` i `ALLOWED_PROVIDER_ENVIRONMENTS` są zgodne z celem środowiska
- [ ] migracje zdalne zostały sprawdzone
- [ ] migracje zdalne zostały zastosowane
- [ ] `wrangler deploy` zakończył się powodzeniem
- [ ] smoke test przeszedł end-to-end
- [ ] wynik deploymentu został odnotowany
- [ ] żaden aktywny token nie trafił do repozytorium

## 10. Czego nie robić

- nie używać ponownej rejestracji tego samego `provider_id` jako obejścia utraty dostępu,
- nie publikować sekretów w Issue ani dokumentacji,
- nie wpuszczać realnych providerów przed przejściem smoke testu,
- nie traktować repozytorium jako bazy surowych danych operacyjnych.
