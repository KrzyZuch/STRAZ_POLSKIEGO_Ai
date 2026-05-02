# Szablony Sygnałów Manualnych — Scout Data

## Cel

Ten katalog zawiera szablony JSONL do recznego wprowadzania sygnalow z rozych zrodel
do systemu scoutingowego `scout_resource_signals.py`. Szablony sluza jako przyklady
struktury danych i moga byc uzupelniane o realne sygnaly z grup Facebook, Allegro
Lokalnie, forow lokalnych i innych zrodel.

## Jak uzupelniac szablony

1. Skopiuj odpowiedni plik szablonu (np. `template_facebook_group.jsonl`)
2. Dodaj nowe rekordy w formacie JSONL (jeden JSON na linie)
3. Zachowaj wymagane pola (patrz schemat ponizej)
4. Uruchom ingest: `python3 scout_resource_signals.py ingest-manual --source <plik> --output <out.jsonl>`

## Schemat rekordu

Kazdy rekord JSONL musi zawierac:

| Pole | Typ | Wymagane | Opis |
|------|-----|----------|------|
| `id` | string | TAK | Unikalny identyfikator, np. `fb-006`, `allegro-004` |
| `title` | string | TAK | Tytul ogloszenia / posta |
| `description` | string | nie | Opis szczegolowy |
| `price_value` | int/null | nie | Cena w PLN (0=darmo, null=nie podano) |
| `price_currency` | string | nie | Domyslnie `PLN` |
| `price_label` | string | nie | Etykieta ceny, np. `Za darmo`, `50 zł` |
| `city_name` | string | nie | Nazwa miejscowosci |
| `region_name` | string | nie | Nazwa wojewodztwa |
| `lat` | float | nie | Szerokosc geograficzna |
| `lon` | float | nie | Dlugosc geograficzna |
| `source` | string | TAK | Zrodlo: `facebook_group`, `allegro_lokalnie`, `community_post`, `manual` |
| `source_detail` | string | nie | Szczegol zrodla (nazwa grupy FB, portal) |
| `contact_method` | string | nie | Sposob kontaktu: `facebook_pm`, `phone`, `email`, `comment`, `allegro_chat` |
| `contact_note` | string | nie | Dodatkowe info o kontakcie |
| `created_time` | string | nie | Data sygnalu, format `YYYY-MM-DD` |

## Dostepne szablony

| Plik | Zrodlo | Rekordow |
|------|--------|----------|
| `template_facebook_group.jsonl` | Grupy Facebook (Oddam za darmo, Smieciarka jedzie) | 5 |
| `template_allegro_lokalnie.jsonl` | Allegro Lokalnie | 3 |
| `template_community_post.jsonl` | Fora lokalne, portale spolecznosciowe | 3 |

## Pipeline ingest

Szablony sa automatycznie wykrywane przez komend `ingest-pipeline`:

```bash
python3 scout_resource_signals.py ingest-pipeline --source-dir PROJEKTY/13_baza_czesci_recykling/olx_data
```

Pipeline szuka szablonow manualnych w `scout_data/signals_manual/template_*.jsonl`.

## Ograniczenia

- Nie scrapujemy zywych API (Facebook, Allegro) — dane wprowadzamy recznie
- Szablony sluza jako wzorzec, nie jako zrodlo produkcyjne
- Realne integracje API wymagaja osobnych zadan (zadanie 58+)
