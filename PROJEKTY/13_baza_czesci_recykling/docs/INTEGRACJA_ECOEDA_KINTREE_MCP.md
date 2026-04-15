# Integracja ecoEDA, Ki-nTree i KiCAD-MCP-Server

## 1. ecoEDA

`ecoEDA` oczekuje katalogu czesci w CSV i z tego generuje biblioteke `ecoEDA.kicad_sym`.

Mapowanie z naszego katalogu:

- `part_name` -> `Component Name`
- `species` -> `Species`
- `genus` -> `Genus`
- `mounting` -> `SMD vs THT`
- `value` -> `Value`
- `keywords` -> `Keywords`
- `description` -> `Description`
- `kicad_symbol` -> `Symbol-KICAD-URL`
- `kicad_footprint` -> `Footprint-KICAD-URL`
- `datasheet_url` -> `Datasheet`
- `canonical_name` urzadzenia -> `Source`
- `source_url` lub `teardown_url` -> `Teardown Link`
- `quantity` -> `Quantity`
- `designators` -> `PCB Designator`

W praktyce oznacza to, ze `inventory.csv` powinien byc zawsze generowany z katalogu GitHub, a nie edytowany recznie.

## 2. Ki-nTree

`Ki-nTree` najlepiej wykorzystac jako warstwe publikacji rekordow czesci do `KiCad` i `InvenTree`.

Co przygotowujemy po naszej stronie:

- nazwe czesci i aliasy / numery katalogowe,
- footprint i symbol KiCad,
- datasheet URL,
- kategorie typu `IC`, `Resistor`, `Regulator`,
- link do zrodla i opis odzysku.

To pozwala zautomatyzowac dalsze mapowanie do kategorii `InvenTree`, parametrow i bibliotek KiCad.

## 3. KiCAD-MCP-Server

`KiCAD-MCP-Server` ma juz szeroki zestaw narzedzi projektowych, ale nie ma natywnego strumienia reuse z elektroodpadow. Dlatego ten projekt przygotowuje lekki kontrakt integracyjny:

- zasob: `mcp_reuse_catalog.json`
- przyszle narzedzie: `query_recycled_parts`

Przykladowy kontrakt narzedzia:

```json
{
  "name": "query_recycled_parts",
  "input": {
    "query": "ATmega328P",
    "required_symbol": "MCU_Microchip_ATmega:ATmega328P-PU",
    "required_footprint": "Package_DIP:DIP-28_W7.62mm"
  },
  "output": {
    "matches": [
      {
        "part_name": "ATmega328P",
        "aliases": ["ATMEGA328P-PU"],
        "donor_devices": [
          {
            "canonical_name": "Arduino Uno Clone",
            "quantity": 1,
            "designators": ["U1"]
          }
        ]
      }
    ]
  }
}
```

## Rekomendowany model integracji

1. Katalog jest wersjonowany w GitHub.
2. Generator buduje `mcp_reuse_catalog.json`.
3. MCP czyta ten zasob albo przez wrapper, albo przez przyszly resource provider.
4. AI projektujace w KiCadzie najpierw sprawdza reuse, a dopiero potem klasyczne biblioteki i nowe zakupy.

To jest najbezpieczniejsza droga do efektu "projektowanie ze smieci", bez pakowania calej logiki scrapingu bezposrednio do serwera MCP.
