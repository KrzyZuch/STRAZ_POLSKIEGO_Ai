# Reports

Ten katalog jest przeznaczony na raporty i snapshoty wiedzy wyprowadzone z bazy operacyjnej.

## Zasada

Nie zapisujemy tutaj pełnych, surowych odczytów providerów. Zapisujemy jedynie:

- raporty zbiorcze,
- anonimizowane wnioski,
- snapshoty wiedzy,
- materiały pomocne dla rozwoju modeli i dokumentacji.

## Generator raportu

Minimalny eksport można wygenerować poleceniem:

```bash
python3 pipelines/export_knowledge_snapshot.py
```

Lub do pliku:

```bash
python3 pipelines/export_knowledge_snapshot.py /tmp/straz_fish_pond_v1.db reports/latest_fish_pond_snapshot.md
```
