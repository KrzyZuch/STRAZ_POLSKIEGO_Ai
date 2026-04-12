# Architektura mostu Telegram -> GitHub Issues

## Cel dokumentu

Ten dokument opisuje prosty model kanału mobilnego dla społeczności Straży Przyszłości:

- użytkownik pisze do bota Telegram,
- Worker odbiera webhook,
- wiadomość staje się `GitHub Issue`.

To jest rekomendowana ścieżka szybkiego startu wtedy, gdy konfiguracja `WhatsApp Business Platform` byłaby zbyt ciężka lub zbyt wolna na etap `v1`.

## Dlaczego Telegram jest dobrym wariantem na start

Telegram ma niższy próg wejścia operacyjnego niż `WhatsApp Business Platform`, ponieważ:

- bot tworzy się przez `@BotFather`,
- nie trzeba przechodzić przez rozbudowaną konfigurację biznesową Meta,
- webhook ustawia się jedną komendą do `setWebhook`,
- użytkownik może od razu pisać z telefonu zwykłym tekstem albo dyktować treść przez klawiaturę głosową.

## Najważniejsza zasada

`Telegram` jest tylko kanałem wejścia. Miejscem docelowym pozostaje repozytorium i `GitHub Issues`.

## Minimalny model `v1`

W pierwszej wersji most obsługuje tylko dwa prefiksy:

```text
Pomysl: ...
Uwaga: ...
```

Dopuszczalne są również:

```text
pomysł: ...
zastrzezenie: ...
zastrzeżenie: ...
```

## Przepływ danych

1. Użytkownik wysyła wiadomość do bota Telegram.
2. Telegram przekazuje `Update` do webhooka Worker'a.
3. Worker rozpoznaje typ zgłoszenia.
4. Worker tworzy `Issue` w repozytorium Straży Przyszłości.
5. Repozytorium pozostaje kanonicznym miejscem dalszej pracy.

## Oficjalne źródła Telegram

Ten wariant opiera się na oficjalnych materiałach Telegram:

- Bot API: https://core.telegram.org/bots/api
- Bot tutorial: https://core.telegram.org/bots/tutorial
- Bots FAQ: https://core.telegram.org/bots/faq

Z oficjalnych wyników wyszukiwania Telegram wynika między innymi:

- `setWebhook` jest właściwą metodą do ustawienia webhooka,
- Bot API wspiera parametr `secret_token`,
- FAQ rekomenduje także używanie sekretnej ścieżki webhooka w URL.

## Wymagane elementy techniczne

- bot utworzony przez `@BotFather`,
- `TELEGRAM_BOT_TOKEN`,
- publiczny `Cloudflare Worker`,
- `GITHUB_TOKEN` do tworzenia `Issues`,
- opcjonalny `TELEGRAM_WEBHOOK_SECRET_TOKEN`,
- opcjonalny `TELEGRAM_WEBHOOK_PATH_SEGMENT`.

## Minimalne zabezpieczenia

Wersja `v1` powinna mieć:

- włączany i wyłączany bridge przez zmienną środowiskową,
- tryb `dry-run`,
- ograniczenie do wybranych `chat_id`,
- opcjonalny sekret webhooka,
- opcjonalną sekretną ścieżkę webhooka.

## Jakiego typu wiadomości wspieramy

Na start tylko:

- tekstowe wiadomości prywatne,
- tekstowe wiadomości z prostymi prefiksami.

Nie wspieramy jeszcze:

- notatek głosowych,
- automatycznej transkrypcji audio,
- załączników,
- długich konwersacji typu support.

## Rekomendacja dla Straży Przyszłości

Najbardziej praktyczna kolejność:

1. uruchomić bota Telegram,
2. włączyć `dry-run`,
3. przetestować 2-3 wiadomości własne,
4. dopiero potem włączyć realne tworzenie `Issues`.

## Runbook wdrożeniowy

Praktyczna instrukcja uruchomienia bota, webhooka i testu znajduje się tutaj:

- [Runbook uruchomienia kanału Telegram -> GitHub Issues](RUNBOOK_URUCHOMIENIA_TELEGRAM_ISSUES.md)
