# Scraping Pipeline

Projekt zaklada dwa poziomy danych:

- `surowe sygnaly`: fora, PDF-y, teardowny, OCR, marketplace'y, Telegram
- `kuratorowany katalog`: rekordy zapisane w GitHub jako `devices.jsonl` i `device_parts.jsonl`

## Strumienie wejsciowe

1. Fora i teardowny
   - wpisy z forow elektronicznych
   - blogi i teardowny wideo
   - komentarze zawierajace identyfikatory czesci i modele urzadzen

2. PDF-y i dokumentacja
   - service manuale
   - schematy serwisowe
   - instrukcje serwisowe z listami elementow

3. Marketplace i grupy
   - Allegro, OLX, Facebook Marketplace
   - ogloszenia traktowane jako sygnal dostepnosci dawcy, nie jako baza glowna

4. Telegram
   - model urzadzenia wpisany tekstowo
   - numer seryjny
   - numer czesci
   - zdjecie etykiety lub PCB

## Docelowy przeplyw

1. Surowe dane sa zbierane do plikow pomocniczych albo kolejki D1.
2. AI i/lub operator normalizuje dane do:
   - `device_slug`
   - `brand`
   - `model`
   - `part_name`
   - `part_aliases`
   - `kicad_symbol`
   - `kicad_footprint`
   - `datasheet`
   - `source_url`
   - `confidence`
3. Znormalizowane rekordy trafiaja do GitHub.
4. Generator buduje artefakty dla `ecoEDA`, D1 i MCP.

## Zasady kuracji

- Nie zapisujemy do katalogu surowych komentarzy ani niezweryfikowanych listingow.
- Dla kazdej czesci powinien zostac przynajmniej jeden `source_url` albo czytelna notatka o pochodzeniu.
- Marketplace powinien dawac `donor hints`, nie zmieniac glownych rekordow urzadzen bez review.
- Numer seryjny sam w sobie nie wystarcza, jesli nie daje powtarzalnego modelu albo wariantu plyty.
