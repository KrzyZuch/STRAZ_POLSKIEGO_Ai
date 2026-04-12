# Architektura mostu WhatsApp -> GitHub Issues

## Cel dokumentu

Ten dokument opisuje prosty i profesjonalny model mobilnego kanału wejścia do repozytorium Straży Przyszłości dla dwóch klas zgłoszeń:

- `pomysł`
- `uwaga` / `zastrzeżenie`

Kanał ten ma umożliwić szybkie przechwycenie wartościowych obserwacji z telefonu, także wtedy, gdy ktoś wpisuje lub dyktuje treść na smartfonie przez `Gboard` albo inny mechanizm mowy na tekst.

## Najważniejsza zasada

`WhatsApp` nie powinien być miejscem docelowym pracy projektowej. Powinien być tylko kanałem wejścia.

Miejscem docelowym pozostaje repozytorium i `GitHub Issues`, ponieważ to tam można:

- zachować historię decyzji,
- linkować zgłoszenie do plików, dokumentów i projektów,
- utrzymywać backlog,
- porządkować wiedzę w sposób trwały i publiczny.

## Minimalny model `v1`

W pierwszej wersji most powinien obsługiwać tylko dwa prefiksy wiadomości:

```text
Pomysl: ...
Uwaga: ...
```

Dopuszczalne powinny być również warianty:

```text
pomysł: ...
zastrzezenie: ...
zastrzeżenie: ...
```

Każda taka wiadomość powinna zostać zamieniona na `Issue` w repozytorium.

## Przepływ danych

Minimalna architektura wygląda tak:

1. Użytkownik wysyła wiadomość tekstową lub dyktowaną przez WhatsApp.
2. `WhatsApp Business Platform` przekazuje webhook do `Cloudflare Worker`.
3. Worker rozpoznaje typ zgłoszenia: `pomysł` albo `uwaga`.
4. Worker tworzy odpowiedni `GitHub Issue`.
5. Repozytorium pozostaje kanonicznym miejscem dalszej pracy.

## Dlaczego nie bezpośrednio z WhatsApp do repo

Bezpośrednie pisanie z komunikatora do repozytorium bez warstwy pośredniej byłoby zbyt kruche i trudne do zabezpieczenia.

Warstwa pośrednia jest potrzebna, żeby:

- zweryfikować webhook,
- odfiltrować wiadomości niezwiązane z projektem,
- rozpoznać typ zgłoszenia,
- nadawać spójny format `Issue`,
- ukrywać w treści repozytorium pełne dane kontaktowe nadawcy,
- w przyszłości dodać moderację i reguły antyspamowe.

## Zakres odpowiedzialności mostu

Most `WhatsApp -> GitHub Issues` nie służy do:

- przesyłania danych pomiarowych providera,
- rejestracji węzłów pomiarowych,
- sterowania urządzeniami,
- odbierania wyników analizy stawu.

To jest wyłącznie lekki kanał wejścia dla:

- pomysłów,
- uwag,
- zastrzeżeń,
- sygnałów o ryzyku,
- krótkich sugestii architektonicznych i organizacyjnych.

## Zalecany porządek kanałów

Najprostsza i najtańsza ścieżka wejścia z telefonu powinna wyglądać tak:

1. **strona inicjatywy -> gotowy link do odpowiedniego Issue template**
2. **opcjonalnie WhatsApp -> Worker -> GitHub Issues**

To ważne, bo bezpośrednie linki do `Issue template` są prostsze, praktycznie darmowe i nie wymagają utrzymywania integracji z zewnętrznym komunikatorem.

`WhatsApp` warto traktować jako drugi etap, gdy:

- kanał mobilny na stronie już działa,
- społeczność rzeczywiście chce zgłaszać rzeczy z komunikatora,
- jest gotowość operatorska do moderacji i utrzymania webhooka.

## Wymagane elementy techniczne

Minimalny wariant wdrożeniowy obejmuje:

- `Cloudflare Worker` jako webhook i logikę klasyfikacji,
- `GitHub token` z uprawnieniem do tworzenia `Issues`,
- `WHATSAPP_VERIFY_TOKEN` do weryfikacji webhooka,
- opcjonalnie `WHATSAPP_APP_SECRET` do weryfikacji podpisu `X-Hub-Signature-256`,
- opcjonalną listę dozwolonych nadawców dla pierwszych testów.

## Minimalne zabezpieczenia

Wersja `v1` powinna mieć przynajmniej:

- weryfikację webhooka Meta,
- opcjonalną weryfikację podpisu żądania,
- tryb `dry-run`,
- możliwość ograniczenia nadawców do listy testowej,
- jasne oznaczenie zgłoszeń pochodzących z WhatsApp.

## Model treści Issue

Issue tworzone przez most powinno zawierać:

- typ zgłoszenia,
- właściwą treść pomysłu albo uwagi,
- kanał pochodzenia: `WhatsApp`,
- zanonimizowany numer nadawcy,
- identyfikator wiadomości,
- znacznik czasu,
- notę, że zgłoszenie zostało utworzone automatycznie.

## Czy to będzie darmowe?

### Wersja rozwojowa i testowa

Na etapie prototypu koszt może być bardzo niski albo praktycznie zerowy:

- `Cloudflare Workers` ma plan `Free`, który według dokumentacji obejmuje `100,000 requests/day`.
- `Cloudflare D1` ma plan `Free`, a dokumentacja podaje między innymi `5 million rows read/day` i `100,000 rows written/day`.
- Meta podaje, że przy starcie z `WhatsApp Cloud API` tworzony jest testowy `WABA` i testowy numer biznesowy.

Źródła:

- https://developers.cloudflare.com/workers/platform/pricing/
- https://developers.cloudflare.com/workers/platform/limits/
- https://developers.cloudflare.com/d1/platform/pricing/
- https://developers.cloudflare.com/d1/reference/faq/
- https://developers.facebook.com/documentation/business-messaging/whatsapp/get-started
- https://developers.facebook.com/documentation/business-messaging/whatsapp/about-the-platform
- https://developers.facebook.com/documentation/business-messaging/whatsapp/business-phone-numbers/phone-numbers

### Wersja produkcyjna

Produkcyjny `WhatsApp` nie powinien być traktowany jako kanał całkowicie darmowy.

Meta publikuje oficjalną dokumentację cenową dla `WhatsApp Business Platform`, a na stronie cenowej wprost opisuje model cenowy i jego zmiany, w tym przejście od `1 lipca 2025` z modelu conversation-based na model per-message.

Źródło:

- https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing

Dlatego najuczciwszy wniosek jest taki:

- **strona -> Issue template**: praktycznie najtańsza i najprostsza droga,
- **Cloudflare Worker jako most**: może działać bardzo tanio na etapie `v1`,
- **produkcyjny WhatsApp**: nie należy zakładać, że będzie darmowy przy realnym użyciu.

## Rekomendacja dla Straży Przyszłości

Najbardziej rozsądna kolejność wdrożenia to:

1. utrzymać prosty mobilny kanał `Zgłoś pomysł` i `Zgłoś zastrzeżenie` ze strony,
2. przygotować Worker z webhookiem i trybem `dry-run`,
3. uruchomić testowy numer `WhatsApp`,
4. dopiero po pozytywnej walidacji uruchomić produkcyjne tworzenie `Issues`.

To pozwala zachować profesjonalny porządek, nie utracić prostoty wejścia i nie wchodzić zbyt wcześnie w kosztowniejszy tor utrzymaniowy.

## Runbook wdrożeniowy

Praktyczna instrukcja uruchomienia numeru, webhooka i pierwszego testu znajduje się tutaj:

- [Runbook uruchomienia kanału WhatsApp -> GitHub Issues](RUNBOOK_URUCHOMIENIA_WHATSAPP_ISSUES.md)
