# API: Inteligentna Akwakultura

Ten katalog zawiera minimalny, działający serwer HTTP dla pilotażu stawu hodowlanego.

## Dlaczego serwer jest potrzebny

Jeżeli Strażnicy Przyszłości mają naprawdę dostarczać dane do wspólnego systemu, to sam schemat i OpenAPI nie wystarczą. Potrzebny jest punkt wejścia, przez który provider może:

- zarejestrować się w systemie,
- przesłać obserwacje,
- przesłać zdarzenia,
- odebrać rekomendację,
- sprawdzić swój status.

## Retencja operacyjna

Serwer przechowuje bieżące dane operacyjne w bazie SQLite poza repozytorium. Domyślna ścieżka lokalna:

```text
/tmp/straz_fish_pond_v1.db
```

To rozdzielenie jest celowe:

- surowe bieżące odczyty zostają w warstwie operacyjnej,
- repozytorium przechowuje wyłącznie schematy, modele, przykłady i wiedzę opracowaną.

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

Token należy przechowywać po stronie providera lub węzła edge. Repozytorium nie jest miejscem przechowywania sekretnych danych operacyjnych.

Powtórna rejestracja tego samego `provider_id` nie służy do odnowienia dostępu. Jeżeli provider już istnieje, serwer zwróci konflikt `409`, a poprawną ścieżką wymiany sekretu jest rotacja tokenu.

## Jak uruchomić

Z katalogu głównego repozytorium:

```bash
python3 api/server.py
```

Domyślnie serwer startuje na:

```text
http://127.0.0.1:8000
```

Możesz podać inny port:

```bash
python3 api/server.py 8080
```

Możesz też podać własną ścieżkę bazy:

```bash
python3 api/server.py 8080 /tmp/straz_fish_pond_custom.db
```

Możesz też włączyć politykę środowisk providera:

```bash
DEPLOYMENT_ENVIRONMENT=local ALLOWED_PROVIDER_ENVIRONMENTS=local,demo python3 api/server.py
```

## Minimalny przepływ

1. Provider rejestruje się przez `POST /v1/providers/register`.
2. Provider bezpiecznie przechowuje `write_token`.
3. W razie potrzeby provider obraca token przez `POST /v1/providers/{provider_id}/tokens/rotate`.
4. Provider przesyła dane wody przez `POST /v1/observations`.
5. Provider może przesłać wynik lokalnej analizy zachowania ryb przez `POST /v1/events`.
6. Provider pobiera rekomendację przez `POST /v1/recommendations/fish-pond`.
7. Provider sprawdza stan integracji przez `GET /v1/providers/{provider_id}/status`.

## Materiały onboardingowe

W repozytorium są gotowe materiały dla pierwszego wejścia providera:

- [`data/sample/provider_registration.json`](../data/sample/provider_registration.json)
- [`api/examples/provider_demo_flow.py`](examples/provider_demo_flow.py)

Przykładowy przebieg:

1. uruchamiasz lokalny serwer,
2. wysyłasz przykładową rejestrację providera,
3. obracasz token providera,
4. wysyłasz obserwację i zdarzenie,
5. pobierasz rekomendację,
6. sprawdzasz status providera.

Skrypt demo:

```bash
python3 api/examples/provider_demo_flow.py
```

Wymuszenie innego environment dla providera demo:

```bash
python3 api/examples/provider_demo_flow.py 8000 local
```

## Eksport wiedzy z bazy operacyjnej

Surowe dane bieżące zostają w bazie operacyjnej, ale można z nich wyprowadzić raport wiedzy do repozytorium lub do dalszej analizy.

Eksport do standardowego wyjścia:

```bash
python3 pipelines/export_knowledge_snapshot.py
```

Eksport do pliku:

```bash
python3 pipelines/export_knowledge_snapshot.py /tmp/straz_fish_pond_v1.db reports/latest_fish_pond_snapshot.md
```

## Utrata tokenu

W wersji `v1` publiczne API nie ma jeszcze samodzielnego procesu odzyskiwania tokenu bez wcześniejszego sekretu.

To oznacza, że:

- jeśli provider ma ważny token, powinien użyć endpointu rotacji,
- jeśli provider utracił token, odzyskiwanie dostępu odbywa się ręcznie w procesie organizacyjnym Straży Przyszłości,
- nie należy próbować odzyskiwać dostępu przez ponowną rejestrację tego samego `provider_id`.

Do ręcznej obsługi providerów w wariancie lokalnym służy narzędzie:

```bash
python3 api/admin_provider_access.py list
python3 api/admin_provider_access.py status community-demo-node-01
python3 api/admin_provider_access.py rotate-token community-demo-node-01
```

Pełny proces jest opisany w:

- [`docs/RUNBOOK_ODZYSKIWANIA_DOSTEPU_PROVIDERA.md`](../docs/RUNBOOK_ODZYSKIWANIA_DOSTEPU_PROVIDERA.md)
- [`docs/KONWENCJA_PROVIDER_ID_I_SRODOWISK.md`](../docs/KONWENCJA_PROVIDER_ID_I_SRODOWISK.md)

## Założenia tej wersji

- serwer jest minimalny i działa bez zewnętrznych zależności,
- rejestr providerów i dane operacyjne są trzymane w lokalnej bazie SQLite,
- to nie jest jeszcze wersja produkcyjna,
- ta warstwa ma przede wszystkim umożliwić eksperymenty, integrację społeczności i rozwój wspólnego API.
