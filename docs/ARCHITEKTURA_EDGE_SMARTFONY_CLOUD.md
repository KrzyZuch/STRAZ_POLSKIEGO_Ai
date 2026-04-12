# Architektura Edge: Smartfony + Centralne API + Baza Wiedzy

## Cel dokumentu

Ten dokument opisuje oficjalny kierunek architektoniczny dla projektów Straży Przyszłości, w których społeczność ma dostarczać dane do wspólnego API przy użyciu starych smartfonów, prostych węzłów pomiarowych i lekkiej warstwy centralnej.

## Najważniejsze założenie

Nie budujemy klasycznego klastra obliczeniowego ze starych smartfonów. Budujemy **rozproszoną sieć węzłów edge**, które:

- zbierają dane,
- wykonują lekką analizę lokalną,
- buforują obserwacje,
- rejestrują się jako providerzy,
- przesyłają wyniki do centralnego API.

To podejście jest znacznie bardziej realistyczne, energooszczędne i użyteczne dla inicjatywy.

## Rola starego smartfona

Stary smartfon może pełnić jedną lub kilka ról:

- bramka danych dla ESP32 i czujników terenowych,
- samodzielny provider danych,
- urządzenie do lekkiej analizy obrazu,
- lokalny bufor w razie utraty łączności,
- terminal diagnostyczny i terenowy interfejs operatora.

Smartfon nie musi dźwigać całej analityki. Wystarczy, że wykona to, co ma sens lokalnie, a resztę przekaże do wspólnej warstwy.

## Rola centralnego API

Centralne API odpowiada za:

- rejestrację providerów,
- przyjmowanie obserwacji i zdarzeń,
- zwracanie rekomendacji,
- utrzymywanie operacyjnej bazy danych poza repozytorium,
- spójny punkt wejścia dla wszystkich providerów.

To API jest centrum koordynacji, ale nie centrum własności danych społeczności. Repozytorium pozostaje centrum standardu i logiki.

## Rola repozytorium

Repozytorium przechowuje:

- schematy,
- OpenAPI,
- adaptery,
- modele referencyjne,
- sample data,
- dokumentację,
- checklisty i onboardingi,
- wiedzę opracowaną na podstawie danych operacyjnych.

Repozytorium nie powinno przechowywać hurtowo surowych, bieżących odczytów providerów.

## Przepływ danych

Docelowy przepływ powinien wyglądać tak:

```text
czujnik -> ESP32 lub stary smartfon -> provider registration -> observations/events -> central API -> rekomendacje -> baza operacyjna -> wiedza opracowana w repo
```

## Wariant Cloudflare Workers

Jednym z praktycznych wariantów wdrożeniowych dla `v1` jest lekka warstwa centralna oparta o Cloudflare Workers i D1.

Dlaczego to ma sens:

- nie wymaga utrzymywania pełnego serwera VPS na start,
- pozwala szybko wystawić publiczne API,
- dobrze pasuje do krótkich żądań typu `register`, `observe`, `event`, `recommend`,
- odciąża społecznościowe węzły edge,
- pozwala oddzielić warstwę operacyjną od repozytorium.

## Wkład społeczności

Ten model jest cenny dla Narodowych Sił Intelektualnych, bo:

- każdy może uruchomić własny węzeł,
- każdy może dołączyć do wspólnego systemu jako provider danych,
- każdy może dokumentować i ulepszać tanią architekturę pomiarową,
- wspólny dorobek pozostaje otwarty i rozwijany w repozytorium.

To właśnie jest realny, trwały wkład do inicjatywy, a nie jednorazowa demonstracja sprzętowa.
