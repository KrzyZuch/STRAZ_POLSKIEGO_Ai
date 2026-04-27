# Runbook Dla Pack Project13 Catalog Export 01

## Cel

Ten pack przebudowuje downstream artefakty po review kanonicznego katalogu.

Docelowy przeplyw:

```text
reviewed catalog -> export-all -> review-ready diff -> PR
```

## Co trzeba miec przed startem

- lokalne repo z reviewowanym katalogiem `Project 13`
- dzialajace skrypty `build_catalog_artifacts.py`
- czysty kontekst, w ktorym wiadomo, jakie zmiany w katalogu zostaly juz przyjete
- **export gate OPEN** — uruchom `python3 scripts/curate_candidates.py export-gate` i sprawdz, ze `gate_result` w `autonomous_test/reports/export_gate_packet.json` jest `"OPEN"`. Jesli gate jest BLOCKED, nie uruchamiaj exportu.

## Komenda glowna

```bash
python3 PROJEKTY/13_baza_czesci_recykling/scripts/build_catalog_artifacts.py export-all
```

Przed otwarciem PR wykonaj tez:

```bash
python3 PROJEKTY/13_baza_czesci_recykling/scripts/build_catalog_artifacts.py validate
```

## Co pack powinien zrobic

1. Wziac jako wejscie kanoniczny katalog po review.
2. Przebudowac downstream artefakty.
3. Sprawdzic, czy wynik nie wymaga recznej edycji wygenerowanych plikow.
4. Otworzyc PR tylko z diffem downstream i jawnym opisem provenance.

## Czego pack nie powinien robic

- nie powinien uruchamiac discovery ani OCR
- nie powinien recznie poprawiac wygenerowanych plikow exportowych
- nie powinien pomijac walidacji katalogu przed otwarciem PR

## Minimalne kryterium sukcesu

Pack jest wykonany poprawnie, gdy:

- downstream artefakty sa przebudowane z jednego polecenia,
- walidacja przechodzi,
- reviewer widzi czysty diff i rozumie, skad on pochodzi.
