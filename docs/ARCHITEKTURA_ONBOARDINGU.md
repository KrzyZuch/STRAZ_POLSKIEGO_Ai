# Architektura Onboardingu

## Cel dokumentu

Ten dokument rozdziela dwa różne procesy wejścia do ekosystemu **Straży Przyszłości / Narodowych Sił Intelektualnych**. To rozróżnienie jest ważne, bo nie każda osoba wchodząca do inicjatywy chce od razu zostać providerem danych, a nie każdy provider musi przechodzić przez tę samą ścieżkę co nowy Strażnik.

## Dwa osobne onboardingi

W projekcie funkcjonują dwa niezależne, ale powiązane procesy:

1. **Onboarding Strażnika**
   Pierwsze wejście nowej osoby do inicjatywy. Jego celem jest rozpoznanie pasji, kompetencji, zasobów i czasu danej osoby oraz skierowanie jej do odpowiednich sekcji repozytorium i pierwszych zadań.
2. **Onboarding providera danych**
   Techniczne wejście do wspólnego API dla węzłów pomiarowych, starych smartfonów, gospodarstw, partnerów zewnętrznych i projektów społecznościowych, które chcą dostarczać dane lub odbierać wyniki analityczne.

Te dwa onboardingi nie powinny być mieszane w jednej instrukcji, jednym formularzu ani jednym komunikacie na stronie.

## Onboarding Strażnika

Onboarding Strażnika powinien być realizowany na **zewnętrznej stronie inicjatywy** jako ankieta i rekomendator zadań.

Ta ścieżka musi być zaprojektowana w sposób merytokratyczny również wobec osób, które nie mają klasycznej pozycji zawodowej, ale potrafią skutecznie pracować z pomocą nowoczesnych narzędzi agentowych i generatywnych, takich jak `Codex`. Jeżeli ktoś umie osiągać realne cele, łączyć zasoby, adaptować kod i dowozić efekty, powinien być traktowany jako pełnoprawny współtwórca sieci intelektualnej, a nie jako uczestnik drugiej kategorii.

Jego rola:

- przyjąć zgłoszenie osoby, która chce włączyć się do inicjatywy po raz pierwszy,
- rozpoznać obszar pasji i typ wkładu, jaki dana osoba chce wnieść,
- skierować tę osobę do właściwej sekcji tego repozytorium,
- zaproponować pierwsze dokumenty, pierwsze projekty i pierwsze Issues.

Minimalne dane wejściowe dla rekomendatora:

- pasje i obszary zainteresowań,
- kompetencje techniczne lub organizacyjne,
- sposób pracy i używane narzędzia, także narzędzia AI-native,
- dostępny czas,
- dostępne zasoby, na przykład stary smartfon, ESP32, czujniki, kamera, wiedza domenowa,
- preferowany rodzaj wkładu: kod, hardware, dokumentacja, analiza, marketing, badania, provider danych.

Minimalne dane wyjściowe rekomendatora:

- rekomendowana ścieżka wejścia,
- lista dokumentów startowych,
- lista projektów do przeczytania,
- lista pierwszych zadań lub Issues,
- wskazanie, czy dana osoba powinna przejść dalej do onboardingu providera.

## Onboarding providera danych

Onboarding providera jest procesem technicznym i operacyjnym. Dotyczy tylko tych osób, zespołów i węzłów, które chcą zasilać wspólne API danymi albo odbierać wyniki analityczne jako uczestnicy warstwy integracyjnej.

Ta ścieżka obejmuje między innymi:

- zapoznanie się z kontraktem `v1`,
- mapowanie danych do wspólnego schematu,
- rejestrację providera,
- odbiór `write_token`,
- przesyłanie obserwacji i zdarzeń,
- utrzymanie jakości danych,
- ewentualną rotację tokenu i proces odzyskiwania dostępu.

Szczegóły tej ścieżki opisuje dokument:

- [Jak Zostać Dostawcą Danych](JAK_ZOSTAC_DOSTAWCA_DANYCH.md)

## Punkt styku obu ścieżek

Najważniejsza zasada brzmi: **nie każdy Strażnik jest providerem, ale każdy provider może być Strażnikiem**.

W praktyce oznacza to:

- nowa osoba może wejść do inicjatywy tylko jako analityk, dokumentalista, autor modeli, hardware hacker albo organizator,
- dopiero później może zdecydować, że chce budować własny węzeł pomiarowy i zostać providerem,
- onboarding Strażnika ma pomóc odkryć najlepszy pierwszy wkład,
- onboarding providera ma dopiero uruchomić bezpieczną ścieżkę techniczną do API.

## Integracja ze stroną inicjatywy

Repozytorium strony inicjatywy powinno utrzymywać **ankietę i rekomendator zadań**, ale nie powinno duplikować całej wiedzy z tego repozytorium. Strona zewnętrzna ma być warstwą wejścia, a to repozytorium pozostaje źródłem prawdy dla treści merytorycznej i zadań.

Dlatego rekomendator powinien:

- korzystać z katalogu rekomendacji utrzymywanego w tym repozytorium,
- przekierowywać użytkownika do właściwych dokumentów, projektów i szablonów Issue,
- rozróżniać ścieżkę ogólnego zaangażowania od ścieżki providera danych.

Kanoniczny katalog dla tej warstwy jest utrzymywany tutaj:

- [Katalog rekomendatora zadań Strażnika](../data/onboarding/straznik_rekomendator_v1.json)

## Artefakty repozytorium

Aktualna warstwa onboardingowa w repozytorium obejmuje:

- [Architektura Onboardingu](ARCHITEKTURA_ONBOARDINGU.md)
- [Jak Zostać Dostawcą Danych](JAK_ZOSTAC_DOSTAWCA_DANYCH.md)
- [Nowy Strażnik / pierwsze zaangażowanie](../.github/ISSUE_TEMPLATE/nowy_straznik.md)
- [Nowy provider danych / węzeł pomiarowy](../.github/ISSUE_TEMPLATE/provider_danych.md)
- [Katalog rekomendatora zadań Strażnika](../data/onboarding/straznik_rekomendator_v1.json)

## Kryteria sukcesu

Onboarding jest zaprojektowany poprawnie, gdy:

- nowa osoba nie trafia od razu do technicznej dokumentacji API bez kontekstu,
- strona zewnętrzna potrafi skierować Strażnika do konkretnego projektu i pierwszego zadania,
- provider danych ma osobną, czytelną ścieżkę techniczną,
- oba procesy są ze sobą kompatybilne, ale nie są mylone,
- repozytorium pozostaje źródłem prawdy dla zadań, dokumentów i standardów.
