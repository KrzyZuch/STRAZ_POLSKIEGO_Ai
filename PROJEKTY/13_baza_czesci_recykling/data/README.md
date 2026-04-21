# Dane projektu 13

Ten katalog jest zaprojektowany jako `GitHub-first`.

## Zrodla prawdy

- `devices.jsonl` - urzadzenia-dawcy
- `parts_master.jsonl` - kanoniczne czesci niezalezne od dawcy
- `device_parts.jsonl` - relacje czesc -> urzadzenie-dawca

Te trzy pliki sa kanoniczne i powinny byc recznie kuratorowane przez review.

## Artefakty generowane

- `inventory.csv` - eksport do `ecoEDA`
- `recycled_parts_seed.sql` - wsad do `Cloudflare D1`
- `mcp_reuse_catalog.json` - lookup reuse dla warstwy MCP
- `inventree_import.jsonl` - eksport pod `Ki-nTree` / `InvenTree`

Wszystkie pliki generowane odtwarzamy komenda:

```bash
python3 ../scripts/build_catalog_artifacts.py export-all
```

## Uwagi operacyjne

- D1 jest tylko indeksem roboczym, nie zastepuje danych w repo.
- Surowe marketplace'y, grupy i niepotwierdzone zgłoszenia nie powinny trafiać tu jeden do jednego.
- Do katalogu zapisujemy tylko znormalizowane rekordy po review.
- `parts_master.jsonl` moze zawierac czesci bez znanego dawcy; takie rekordy nie trafiaja jeszcze do `inventory.csv` dla `ecoEDA`.
