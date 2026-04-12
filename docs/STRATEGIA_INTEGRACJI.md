# Strategia Integracji

## Cel dokumentu

Ten dokument określa, w jaki sposób **Straż Przyszłości / Narodowe Siły Intelektualne** mają budować publiczną warstwę integracyjną dla projektów rolniczych i pokrewnych. Celem jest stworzenie wspólnego standardu danych, wspólnej warstwy analitycznej oraz wspólnej bazy wiedzy rozwijanej w tym repozytorium.

Strategia zakłada współpracę zarówno z partnerami zewnętrznymi, jak i ze społecznością. Providerem danych może zostać każdy podmiot, który potrafi dostarczać obserwacje do wspólnego schematu i odbierać wyniki analityczne z systemu.

Jednocześnie trzeba rozróżnić dwa różne wejścia do ekosystemu:

- onboarding Strażnika, czyli pierwsze wejście nowej osoby do inicjatywy przez ankietę i rekomendator zadań,
- onboarding providera, czyli techniczne wejście do warstwy operacyjnej API.

Pierwszy proces powinien być obsługiwany przez zewnętrzną stronę inicjatywy i kierować ludzi do odpowiednich sekcji repozytorium. Drugi proces powinien być obsługiwany przez dokumentację integracyjną, Issue template providera i działające endpointy API.

## Zasady nadrzędne

1. Repozytorium pozostaje publicznym centrum strategii, dokumentacji, schematów i modeli referencyjnych.
2. Partnerzy zewnętrzni dostarczają dane lub kanały integracyjne, ale nie przejmują kontroli nad architekturą, nazwą inicjatywy ani roadmapą repozytorium.
3. Społeczność ma pełne prawo uczestniczyć w systemie jako provider danych, badacz, autor modeli lub dokumentalista.
4. Wyniki zwracane przez system służą budowie wspólnej bazy wiedzy, walidacji hipotez i rozwojowi modeli. Nie są traktowane jako kanał zdalnego sterowania cudzą infrastrukturą.
5. Warstwa logiki i modeli działa wyłącznie na własnym schemacie Straży Przyszłości. Format partnera kończy się na adapterze.
6. Repozytorium nie jest magazynem bieżących, surowych odczytów providerów. Surowe dane operacyjne powinny być przechowywane w działającym serwerze i bazie operacyjnej, a do repozytorium trafiają tylko dane przykładowe, opracowane, anonimizowane lub syntetyczne oraz wiedza wyprowadzona z analizy.
7. Onboarding Strażnika i onboarding providera muszą być rozdzielone na poziomie komunikacji, dokumentacji i narzędzi wejścia.

## Dwa onboardingi

### Onboarding Strażnika

To ścieżka dla osoby, która dopiero wchodzi do inicjatywy i jeszcze nie wie, czy jej wkład będzie dotyczył modeli, hardware, dokumentacji, marketingu, badań czy danych terenowych.

Ta ścieżka powinna być realizowana przez zewnętrzną stronę inicjatywy jako:

- ankieta kompetencyjna,
- rekomendator zadań,
- system przekierowań do właściwych projektów, dokumentów i Issues.

Repozytorium powinno dostarczać tej stronie kanoniczny katalog rekomendacji i punkty wejścia do konkretnych zadań.

### Onboarding providera

To ścieżka dla osoby, zespołu albo urządzenia, które chcą zasilać wspólne API danymi albo odbierać wyniki analityczne jako uczestnik warstwy integracyjnej.

Ta ścieżka obejmuje:

- kontrakt `v1`,
- rejestrację providera,
- token `write_token`,
- przesyłanie obserwacji i zdarzeń,
- walidację danych,
- operacyjne utrzymanie dostępu.

Nie każdy Strażnik musi zostać providerem, ale każdy provider może wejść do ekosystemu również jako Strażnik i współtwórca wiedzy.

## Docelowa struktura repozytorium

Repozytorium powinno być rozwijane jako jedno publiczne monorepo:

```text
docs/
schemas/
openapi/
adapters/mock/
adapters/provider-template/
adapters/provider-a/
models/fish_pond/
pipelines/demo/
data/sample/
```

Rola poszczególnych katalogów:

- `docs/` zawiera zasady współpracy, model integracji i dokumenty ochronne.
- `schemas/` jest źródłem prawdy dla wspólnego modelu danych.
- `openapi/` zawiera publiczny kontrakt HTTP dla providerów i integracji.
- `adapters/` izoluje zewnętrzne źródła danych od logiki NSI.
- `models/` zawiera logikę analityczną i rekomendacyjną działającą wyłącznie na schemacie kanonicznym.
- `pipelines/` spina dane, modele i wyniki w powtarzalny przepływ.
- `data/` przechowuje dane przykładowe i zestawy demonstracyjne bez naruszania cudzej poufności.

## Retencja danych i baza wiedzy

Należy rozdzielić dwie warstwy:

- **warstwę operacyjną**, która przyjmuje bieżące odczyty providerów i przechowuje je w bazie serwera,
- **warstwę repozytoryjną**, która przechowuje tylko schematy, logikę, przykłady, dokumentację i wiedzę opracowaną.

Do repozytorium nie powinny trafiać hurtowo surowe odczyty z API providerów. Do repozytorium mogą trafiać:

- dane przykładowe,
- zanonimizowane próbki,
- zestawy testowe,
- opisane przypadki,
- wnioski analityczne,
- reguły i modele wypracowane na podstawie danych operacyjnych.

Między tymi warstwami powinna istnieć jawna ścieżka eksportu wiedzy, na przykład w postaci snapshotów, raportów zbiorczych i przypadków opisanych w `reports/`.

## Publiczny kontrakt integracyjny `v1`

Wersja `v1` ma opierać się o minimalny, stabilny zestaw typów:

```text
ProviderDescriptor
PondReference
SensorObservation
AquacultureContext
Recommendation
ProviderStatus
SchemaVersion
```

Minimalna publiczna powierzchnia API:

```text
POST /v1/providers/register
POST /v1/providers/{provider_id}/tokens/rotate
POST /v1/observations
POST /v1/events
POST /v1/recommendations/fish-pond
GET /v1/providers/{provider_id}/status
```

Zasady kontraktu:

- każda obserwacja musi być możliwa do zmapowania do `SensorObservation`,
- każda rekomendacja musi być zwracana w postaci `Recommendation`,
- każda integracja musi być wersjonowana i jawnie zgodna z `SchemaVersion`,
- brak zgodności z wersją schematu nie może być ukrywany ani obchodzony poza adapterem.

## Minimalna autoryzacja operacyjna

Warstwa operacyjna powinna od początku rozróżniać dwa poziomy dostępu:

- publiczną dokumentację i jawny kontrakt API,
- zapis danych operacyjnych wykonywany przez zarejestrowanych providerów.

Minimalny model `v1` zakłada, że:

- provider rejestruje się przez `POST /v1/providers/register`,
- `provider_id` jest stabilny i nie może być nadpisywany przez ponowną rejestrację,
- przy rejestracji otrzymuje jednorazowo `write_token`,
- wymiana tokenu odbywa się przez dedykowany endpoint rotacji,
- token jest przekazywany w nagłówku `X-Provider-Token`,
- token jest wymagany do przesyłania obserwacji, zdarzeń i żądań rekomendacji.

Warstwa operacyjna może dodatkowo ograniczać, które environment z `provider_id` są dopuszczone w danym deploymencie, na przykład `preview` dla `demo,preview` albo `prod` wyłącznie dla `prod`.

To nie jest jeszcze pełny model produkcyjny, ale wystarcza, aby odróżnić jawny standard od chronionej warstwy operacyjnej.

W wersji `v1` odzyskiwanie dostępu po utracie tokenu pozostaje procesem organizacyjnym, a nie samoobsługową funkcją publicznego API.

Runbook takiego procesu powinien być utrzymywany jawnie w repozytorium, tak aby społeczność znała zasady działania, ale bez publikowania sekretów.

Konwencja identyfikatorów providerów i środowisk również powinna być jawna i wspólna dla całego repozytorium, aby ograniczać kolizje nazw między społecznością, partnerami i środowiskami wdrożeniowymi.

## Model wielodostawcowy

System od początku ma być wielodostawcowy. Oznacza to, że:

- żaden provider nie staje się centralnym punktem systemu,
- każdy provider jest wymienialny na poziomie integracyjnym,
- wycofanie jednego providera nie może blokować rozwoju repozytorium,
- dane przykładowe, tryb `mock` i ścieżki importu zastępczego muszą istnieć niezależnie od partnerów biznesowych.

Providerem może być:

- firma integracyjna,
- gospodarstwo rolne lub hodowlane,
- członek społeczności,
- zespół badawczy,
- autor projektu DIY,
- stary smartfon działający jako bramka danych,
- dowolny węzeł pomiarowy zdolny do pracy z API Straży Przyszłości.

## Pilot: Inteligentna Akwakultura

Pierwszy pilot integracyjny dotyczy stawu hodowlanego. Celem jest zbudowanie wspólnego przepływu danych i rekomendacji dla bezpieczeństwa hodowli oraz dokumentowania wiedzy operacyjnej w repozytorium.

Stałe wejścia pilota:

```text
pond_id
measurement_time
water_temperature
dissolved_oxygen
pH
optional ammonia
optional flow_rate
```

Stałe wyjścia pilota:

```text
risk_level
recommendation
confidence
reason_codes
provider_id
schema_version
```

Pierwsza wersja pilota ma generować wyniki takie jak:

- ocena ryzyka przyduchy,
- sygnalizacja anomalii w parametrach wody,
- rekomendacja inspekcji lub działań operacyjnych,
- materiał porównawczy do dalszej analizy i rozbudowy bazy wiedzy.

## Rola społeczności

Społeczność nie jest wyłącznie odbiorcą gotowych narzędzi. Ma być współtwórcą danych, schematów, adapterów i interpretacji wyników.

W praktyce oznacza to:

- możliwość dostarczania danych z własnych czujników i węzłów pomiarowych,
- możliwość odbierania wyników analitycznych do walidacji lokalnych obserwacji,
- dokumentowanie konfiguracji czujników, pomiarów i warunków pracy w repozytorium,
- przekształcanie pojedynczych eksperymentów w trwały dorobek społeczności NSI.

Społeczność potrzebuje też pierwszej ścieżki wejścia, która nie zakłada od razu budowy providera. Dlatego nowy Strażnik powinien najpierw otrzymać rekomendację zadań dopasowaną do pasji i zasobów, a dopiero później, jeśli ma ku temu warunki, przejść do ścieżki providera danych.

## Etapy wdrożenia

1. Przygotować dokumentację strategii, współpracy, nazwy oraz rozdzielenia onboardingu Strażnika i onboardingu providera.
2. Zdefiniować `schemas/` oraz `openapi/` dla wersji `v1`.
3. Uruchomić `adapters/mock/`, `data/sample/` i `pipelines/demo/`, aby system działał bez partnera.
4. Dodać pierwszy model referencyjny w `models/fish_pond/`.
5. Przygotować `adapters/provider-template/` jako wzorzec dla kolejnych integracji.
6. Dodać pierwszego realnego providera bez naruszania kontraktu publicznego.
7. Dodać działający serwer z rejestracją providerów i operacyjną bazą danych poza repozytorium.
8. Przygotować wariant wdrożeniowy typu edge/cloud, np. dla Cloudflare Workers.
9. Przygotować runbook pierwszego publicznego deploymentu i smoke test środowiska.
10. Utrzymywać katalog rekomendatora zadań dla strony zewnętrznej i rozbudowywać onboarding Strażnika.
11. Rozszerzać bazę wiedzy repozytorium o kolejne interpretacje, przypadki użycia i dane opracowane.

## Kryteria sukcesu

- repozytorium działa demonstracyjnie bez udziału zewnętrznego partnera,
- dwóch różnych providerów może zasilać ten sam schemat bez zmian w modelu,
- społeczność potrafi dołączyć własne dane bez uzależnienia od komercyjnej platformy,
- nowy Strażnik potrafi trafić ze strony inicjatywy do konkretnego projektu i pierwszego zadania bez czytania całego repozytorium na ślepo,
- pierwsze publiczne środowisko można odtworzyć na podstawie jawnego runbooka operatorskiego,
- wyniki analityczne wracają do providera jako wkład do wiedzy i walidacji, a nie jako kanał sterowania urządzeniami,
- dorobek intelektualny pozostaje po stronie Straży Przyszłości i Narodowych Sił Intelektualnych.
