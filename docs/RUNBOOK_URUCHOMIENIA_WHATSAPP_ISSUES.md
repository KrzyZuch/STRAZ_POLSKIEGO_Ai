# Runbook uruchomienia kanału WhatsApp -> GitHub Issues

## Cel

Ten runbook opisuje, jak uruchomić numer `WhatsApp`, na który społeczność będzie mogła wysyłać:

- `Pomysl: ...`
- `Uwaga: ...`
- `zastrzezenie: ...`

Wiadomości mają trafiać do repozytorium Straży Przyszłości jako `GitHub Issues` przez `Cloudflare Worker`.

## Co już jest gotowe w repo

Warstwa integracyjna została przygotowana w:

- [`cloudflare/src/worker.js`](../cloudflare/src/worker.js)
- [`cloudflare/src/github_issues.js`](../cloudflare/src/github_issues.js)
- [`cloudflare/wrangler.toml`](../cloudflare/wrangler.toml)
- [`cloudflare/README.md`](../cloudflare/README.md)
- [`docs/ARCHITEKTURA_MOSTU_WHATSAPP_GITHUB_ISSUES.md`](ARCHITEKTURA_MOSTU_WHATSAPP_GITHUB_ISSUES.md)
- [`cloudflare/whatsapp_issue_smoke_test.py`](../cloudflare/whatsapp_issue_smoke_test.py)

## Ograniczenie wersji `v1`

Wersja `v1` obsługuje tylko wiadomości tekstowe. To dobrze pasuje do wpisywania albo dyktowania treści przez `Gboard`.

Nie obsługujemy jeszcze:

- notatek głosowych jako wejścia,
- automatycznej transkrypcji audio,
- obrazów i załączników jako pełnoprawnych zgłoszeń,
- automatycznych odpowiedzi do użytkownika.

## Oficjalne źródła Meta

Ten runbook opiera się na oficjalnej dokumentacji Meta:

- `Get Started`: https://developers.facebook.com/documentation/business-messaging/whatsapp/get-started
- `About the platform`: https://developers.facebook.com/documentation/business-messaging/whatsapp/about-the-platform
- `Business phone numbers`: https://developers.facebook.com/documentation/business-messaging/whatsapp/business-phone-numbers/phone-numbers
- `Register a phone number`: https://developers.facebook.com/documentation/business-messaging/whatsapp/business-phone-numbers/registration
- `Create a webhook endpoint`: https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/create-webhook-endpoint
- `Pricing`: https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing

## Warianty numeru

Masz dwa realistyczne warianty startu.

### Wariant A: numer testowy

To najlepsza ścieżka na start. Dokumentacja Meta podaje, że po przejściu przez `Get Started` testowy numer biznesowy jest generowany i rejestrowany automatycznie.

Ten wariant wybierz, jeśli chcesz:

- szybko sprawdzić webhook,
- zrobić pierwsze testy `dry-run`,
- nie zaczynać od własnego numeru publicznego.

### Wariant B: własny numer produkcyjny

To ścieżka właściwa dla publicznego kanału Straży Przyszłości.

Dokumentacja Meta podaje, że numer musi być:

- posiadany przez Was,
- mieć krajowy i kierunkowy kod,
- móc odbierać `SMS` lub połączenia głosowe,
- spełniać warunki kwalifikacyjne platformy.

Po dodaniu numeru do `WABA` samo dodanie nie wystarcza do pracy z `Cloud API`. Numer trzeba jeszcze zarejestrować przez endpoint `PHONE_NUMBER_ID/register`.

## Krok 1. Załóż konto deweloperskie Meta

1. Wejdź do: https://developers.facebook.com/
2. Zaloguj się i dokończ rejestrację deweloperską.
3. Przygotuj lub wybierz `Meta Business Portfolio`.

## Krok 2. Utwórz aplikację z use case WhatsApp

Według `Get Started`:

1. Otwórz `Meta App Dashboard`: https://developers.facebook.com/apps
2. Kliknij `Create App`.
3. Wybierz use case `Connect with customers through WhatsApp`.
4. Przypisz aplikację do istniejącego lub nowego `Business Portfolio`.
5. Po utworzeniu przejdź do `Customize use case > Connect on WhatsApp > Quickstart`.

## Krok 3. Wybierz, czy startujesz od numeru testowego czy własnego

### Numer testowy

1. W dashboardzie przejdź do `WhatsApp > API Setup`.
2. Kliknij `Start using the API`.
3. Zapisz:
   - `WhatsApp Business Account ID`
   - `Phone Number ID`
4. Wygeneruj tymczasowy token i wykonaj pierwszy test.

To jest najszybsza droga do sprawdzenia mostu `WhatsApp -> Issues`.

### Własny numer

1. W `App Dashboard > WhatsApp > API Setup` dodaj numer telefonu.
2. Przejdź weryfikację numeru przez `SMS` albo połączenie.
3. Ustal `display name`.
4. Zapisz `Phone Number ID`.
5. Zarejestruj numer dla `Cloud API`.

## Krok 4. Zarejestruj własny numer dla Cloud API

Dokumentacja Meta wskazuje, że po dodaniu numeru do `WABA` trzeba wywołać:

```text
POST PHONE_NUMBER_ID/register
```

Przykład z dokumentacji:

```bash
curl "https://graph.facebook.com/v25.0/<PHONE_NUMBER_ID>/register" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <META_ACCESS_TOKEN>" \
  -d '{
    "messaging_product": "whatsapp",
    "pin": "212834"
  }'
```

Uwagi:

- `messaging_product` musi mieć wartość `whatsapp`,
- `pin` to 6-cyfrowy PIN dwustopniowej weryfikacji,
- po rejestracji numer powinien uzyskać status `CONNECTED`.

## Krok 5. Wdróż naszego Worker'a

1. Uzupełnij `database_id` i `preview_database_id` w [`cloudflare/wrangler.toml`](../cloudflare/wrangler.toml).
2. Wgraj sekrety:

```bash
npx wrangler secret put GITHUB_TOKEN
npx wrangler secret put WHATSAPP_VERIFY_TOKEN
npx wrangler secret put WHATSAPP_APP_SECRET
```

3. Ustaw bezpieczny start:

```text
WHATSAPP_ISSUES_ENABLED = "true"
WHATSAPP_ISSUES_DRY_RUN = "true"
WHATSAPP_ALLOWED_SENDERS = "<twoj-testowy-numer>"
```

4. Wdróż:

```bash
npx wrangler deploy
```

## Krok 6. Skonfiguruj webhook w Meta

Oficjalna dokumentacja Meta mówi, że webhook musi:

- być publicznie dostępny,
- obsługiwać `GET` i `POST`,
- mieć poprawny certyfikat `TLS/SSL`,
- przy weryfikacji zwracać `200` i `hub.challenge`.

W `App Dashboard` przejdź do:

- `WhatsApp > Configuration`

albo, przy nowym use case:

- `App Dashboard > Use cases > Customize > Configuration`

Ustaw:

- `Callback URL`:

```text
https://<twoj-worker>.workers.dev/integrations/whatsapp/webhook
```

- `Verify token`:

```text
<ta-sama-wartosc-co-WHATSAPP_VERIFY_TOKEN>
```

Po poprawnej weryfikacji wybierz subskrypcję dla wiadomości przychodzących.

## Krok 7. Przetestuj w `dry-run`

Najpierw nie twórz prawdziwych issue produkcyjnie. Zostaw:

```text
WHATSAPP_ISSUES_DRY_RUN = "true"
```

Następnie wyślij na numer testowy wiadomość:

```text
Pomysl: zróbmy prosty dashboard dla porównania trendów pH i natlenienia
```

albo:

```text
Uwaga: onboarding providera jest jeszcze zbyt techniczny dla nowych osób
```

Worker powinien przyjąć webhook i zwrócić status `dry_run`.

Możesz też wykonać kontrolowany test skryptem:

```bash
python3 cloudflare/whatsapp_issue_smoke_test.py \
  https://<twoj-worker>.workers.dev \
  --sender 48500100200 \
  --message "Pomysl: test webhooka WhatsApp do Issues" \
  --app-secret "<WHATSAPP_APP_SECRET>" \
  --verify-token "<WHATSAPP_VERIFY_TOKEN>"
```

## Krok 8. Włącz realne tworzenie Issues

Gdy `dry-run` przejdzie poprawnie:

1. ustaw:

```text
WHATSAPP_ISSUES_DRY_RUN = "false"
```

2. pozostaw na początku `WHATSAPP_ALLOWED_SENDERS` z krótką listą numerów testowych,
3. wykonaj jedną próbę tworzenia prawdziwego issue,
4. dopiero potem zdecyduj, czy otwierasz kanał szerzej.

## Krok 9. Jak ludzie mają pisać

Na stronie i w materiałach warto jasno pokazać tylko dwa wzorce:

```text
Pomysl: ...
Uwaga: ...
```

To powinno być bardzo krótkie i intuicyjne. Nie każ użytkownikom czytać dokumentacji Meta ani GitHub.

## Minimalna polityka operatorska

Na start rekomenduję:

- brak automatycznych odpowiedzi na WhatsApp,
- tylko tekstowe zgłoszenia do repo,
- tylko dwa typy prefiksów,
- początkowo allowlista numerów,
- regularny przegląd nowo utworzonych issue.

## Czy trzeba od razu płacić?

Najuczciwsza odpowiedź jest taka:

- testowy numer i prototyp można uruchamiać bardzo tanio,
- sam `Cloudflare Worker` może zmieścić się w darmowych limitach,
- produkcyjnego `WhatsApp` nie należy zakładać jako zawsze darmowego.

Jeżeli użytkownicy tylko wysyłają wiadomości, a Wy im nie odpisujecie przez WhatsApp, koszt może być bardzo niski albo zerowy na etapie testów. Ale pełny kanał publiczny trzeba traktować jako rzecz, którą trzeba obserwować kosztowo według aktualnej polityki Meta.
