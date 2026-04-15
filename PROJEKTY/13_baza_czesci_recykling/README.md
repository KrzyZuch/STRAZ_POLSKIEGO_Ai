# [PROJEKT 13] GitHub-First Baza Czesci z Recyklingu

Ten projekt zamienia elektroodpady w publicznie dostepny katalog czesci dla AI, KiCada i spolecznosci. Glowna zasada jest prosta:

- `GitHub` przechowuje kanoniczna, kuratorowana baze wiedzy o urzadzeniach-dawcach i czesciach.
- `Cloudflare D1` sluzy tylko jako operacyjny indeks do szybkich lookupow w Telegramie i przyszlych rekomendacji AI.
- `ecoEDA`, `Ki-nTree` i `KiCAD-MCP-Server` sa zasilane z tego samego katalogu zrodlowego.

## Zweryfikowane zalozenia

Plan jest zgodny z realnymi rolami zewnetrznych projektow:

- [`ecoEDA`](https://github.com/humancomputerintegration/ecoEDA) nie jest baza danych magazynowej. To narzedzie do KiCada, ktore generuje biblioteke z pliku `.csv`, a potem robi sugestie reuse i `Bill of Teardowns`.
- [`Ki-nTree`](https://github.com/sparkmicro/Ki-nTree) automatyzuje tworzenie czesci dla `KiCad` i `InvenTree`, korzysta z konfiguracji kategorii i mapowania parametrow, ale nie utrzymuje sam z siebie katalogu "urzadzenie -> odzyskiwane czesci".
- [`KiCAD-MCP-Server`](https://github.com/mixelpixx/KiCAD-MCP-Server) daje narzedzia MCP i zasoby projektowe dla KiCada, ale nie ma natywnego feedu z czesciami z elektroodpadow. Dlatego rekomendacje reuse trzeba podpiac jako osobny zasob albo dodatkowe narzedzie.

Wniosek: najczystsza architektura to osobny katalog donorow i czesci w tym repo, a dopiero z niego eksport do `ecoEDA`, `Ki-nTree` i warstwy MCP.

## Architektura

Przeplyw danych:

1. `Telegram / OCR / scraping forow / PDF / teardowny` dostarczaja surowe sygnaly.
2. Sygnaly trafiaja do kolejki kuracji i sa porzadkowane do katalogu w `data/devices.jsonl` oraz `data/device_parts.jsonl`.
3. Skrypt budujacy generuje artefakty:
   - `data/inventory.csv` dla `ecoEDA`
   - `data/recycled_parts_seed.sql` do zasilenia `Cloudflare D1`
   - `data/mcp_reuse_catalog.json` jako zasob do lookupow reuse po stronie MCP
4. `Cloudflare Worker` korzysta z D1 do szybkich odpowiedzi bota i logowania zgloszen.
5. `Ki-nTree` pobiera z katalogu dane o czesciach i mapuje je do KiCad/InvenTree.
6. `KiCAD-MCP-Server` moze czytac `mcp_reuse_catalog.json` albo przyszle narzedzie `query_recycled_parts`.

## Dlaczego GitHub jako source of truth

To jest wymagane nie tylko organizacyjnie, ale i technicznie:

- katalog jest publiczny, przegladalny i wersjonowany,
- zmiany mozna recenzowac przez commit / PR zamiast przepisywac dane w ciszy do prywatnej bazy,
- eksport do `ecoEDA` i D1 da sie odtworzyc z jednego zrodla,
- spolecznosc moze dokladac rekordy urzadzen i czesci bez dostepu operatorskiego do chmury.

## Struktura projektu

- `data/devices.jsonl`: kanoniczny katalog urzadzen-dawcow
- `data/device_parts.jsonl`: kanoniczny katalog czesci i ich donorow
- `data/inventory.csv`: wygenerowany eksport zgodny z `ecoEDA`
- `data/recycled_parts_seed.sql`: wygenerowany seed dla `Cloudflare D1`
- `data/mcp_reuse_catalog.json`: wygenerowany katalog lookupow dla MCP
- `schemas/`: schematy rekordow katalogu
- `scripts/build_catalog_artifacts.py`: generator artefaktow z danych GitHub
- `docs/`: opis przeplywu scrapingu i kontraktu integracyjnego

## Komendy

Walidacja katalogu:

```bash
python3 PROJEKTY/13_baza_czesci_recykling/scripts/build_catalog_artifacts.py validate
```

Przebudowa wszystkich artefaktow:

```bash
python3 PROJEKTY/13_baza_czesci_recykling/scripts/build_catalog_artifacts.py export-all
```

Tylko eksport `ecoEDA`:

```bash
python3 PROJEKTY/13_baza_czesci_recykling/scripts/build_catalog_artifacts.py export-ecoeda
```

Tylko seed do D1:

```bash
python3 PROJEKTY/13_baza_czesci_recykling/scripts/build_catalog_artifacts.py export-d1-sql
```

## Rekomendacje projektowe

- Marketplace i grupy spolecznosciowe warto traktowac jako strumien sygnalow, nie jako kanoniczna baze wiedzy. Do GitHub najlepiej zapisywac rekordy znormalizowane, a nie surowe ogloszenia.
- Zdjecia, OCR i wpisy z Telegrama powinny najpierw trafic do kolejki kuracji. Dopiero po potwierdzeniu warto dopisywac je do katalogu zrodlowego w repo.
- `ecoEDA` powinna dostawac wygenerowany `inventory.csv`, a nie recznie edytowany plik.
- `Ki-nTree` najlepiej traktowac jako warstwe publikacji danych o czesciach do `KiCad` i `InvenTree`, a nie jako miejsce kuracji wiedzy o donorach.
- `KiCAD-MCP-Server` powinien dostac lekki, deterministyczny zasob reuse, zamiast bezposrednio czytac rozproszone fora, PDF-y i marketplace'y.

## Kolejny etap

Po dopieciu katalogu GitHub-first nastepny logiczny krok to automatyczna kuracja:

1. zdjecie / model / numer czesci w Telegramie,
2. zapis do kolejki w D1,
3. review,
4. commit lub PR do katalogu w GitHub,
5. regeneracja `ecoEDA`, D1 i zasobu MCP z jednego polecenia.
