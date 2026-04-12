# Jak Zostać Dostawcą Danych

## Cel dokumentu

Ten dokument wyjaśnia, kto może zostać providerem danych w ekosystemie Straży Przyszłości i jak dołączyć do wspólnego standardu integracyjnego.

## Kto może zostać providerem

Providerem danych może zostać każdy, kto potrafi przekazać obserwacje do wspólnego schematu API i odbierać wyniki analityczne. W szczególności mogą to być:

- firmy i platformy zewnętrzne,
- gospodarstwa,
- zespoły badawcze,
- członkowie społeczności,
- projekty DIY,
- stare smartfony działające jako bramki danych,
- własne węzły pomiarowe budowane przez społeczność.

Provider nie musi mieć rozbudowanej infrastruktury. Wystarczy zdolność do dostarczenia danych w uzgodnionym formacie lub do przejścia przez warstwę adaptera.

## Co provider dostarcza

Provider dostarcza do systemu:

- pomiary,
- zdarzenia,
- kontekst pomiarowy,
- informacje o źródle danych,
- opcjonalnie dane historyczne do walidacji i porównań.

W przypadku pilotażu stawu hodowlanego minimalny zestaw danych obejmuje:

```text
pond_id
measurement_time
water_temperature
dissolved_oxygen
pH
optional ammonia
optional flow_rate
```

## Co provider otrzymuje z systemu

Provider może odbierać:

- ocenę ryzyka,
- rekomendacje analityczne,
- kody przyczyn i uzasadnienia,
- status walidacji danych,
- wyniki pomocne w dokumentowaniu przypadku i budowie bazy wiedzy.

Wyniki te nie są definiowane jako kanał zdalnego sterowania urządzeniami providera.

## Minimalne poziomy integracji

### Poziom 1: dane przykładowe lub import plikowy

Najprostszy sposób wejścia. Provider dostarcza dane w pliku zgodnym z wymaganym układem pól.

### Poziom 2: adapter lokalny

Provider korzysta z własnego prostego adaptera, który mapuje dane źródłowe do schematu Straży Przyszłości.

### Poziom 3: pełna integracja API

Provider wysyła obserwacje i zdarzenia bezpośrednio do publicznego API oraz odbiera wyniki analityczne przez ustalony kanał.

## Obowiązkowy kontrakt adaptera

Każdy adapter providera musi realizować co najmniej następujące funkcje:

```text
fetch_or_receive
normalize
validate
send_result
check_status
```

Znaczenie funkcji:

- `fetch_or_receive` pobiera lub odbiera dane źródłowe,
- `normalize` mapuje dane do wspólnego schematu,
- `validate` sprawdza kompletność i zgodność,
- `send_result` odsyła wynik analityczny,
- `check_status` raportuje stan integracji.

## Zasady jakości danych

Provider powinien zadbać o:

- poprawne jednostki,
- prawidłowe oznaczanie czasu pomiaru,
- stabilny identyfikator źródła lub stawu,
- dokumentowanie pochodzenia danych,
- rozróżnienie danych rzeczywistych, testowych i symulowanych.

Dane niskiej jakości również mogą być wartościowe, jeżeli są jasno oznaczone i opisane. Ważniejsze od pozornej perfekcji jest uczciwe udokumentowanie warunków pomiaru.

## Ścieżka dołączenia

1. Zapoznaj się ze schematem danych i dokumentacją integracyjną.
2. Ustal, czy chcesz działać przez plik, adapter lokalny czy pełne API.
3. Przygotuj mapowanie swoich danych do wspólnego schematu.
4. Udokumentuj źródło pomiarów i ograniczenia swojej konfiguracji.
5. Otwórz zgłoszenie w repozytorium przez szablon providera danych i opisz swój przypadek.

## Kanał onboardingowy

Pierwszym, rzeczywistym kanałem wejścia do systemu jest zgłoszenie GitHub Issue z wykorzystaniem szablonu:

- [Nowy provider danych / węzeł pomiarowy](../.github/ISSUE_TEMPLATE/provider_danych.md)

To zgłoszenie powinno zawierać:

- typ providera,
- typ węzła,
- obsługiwane sensory,
- sposób łączności,
- przykładowy payload,
- ograniczenia konfiguracji,
- planowaną ścieżkę integracji z API Straży Przyszłości.

## Providerzy społeczni

Szczególnie ważną grupą są providerzy społeczni, którzy budują własne węzły pomiarowe, eksperymentują z czujnikami lub wykorzystują stare smartfony jako bramki danych.

Ich wkład jest pełnoprawną częścią Narodowych Sił Intelektualnych, ponieważ:

- dostarczają realne pomiary,
- dokumentują tanie ścieżki budowy infrastruktury,
- pomagają walidować modele,
- rozbudowują wspólną bazę wiedzy repozytorium.
