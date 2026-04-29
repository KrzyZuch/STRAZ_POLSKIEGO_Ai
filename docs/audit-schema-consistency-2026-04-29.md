# Audyt Spójności Schemy Bazy Danych — Straż Przyszłości D1
# Data: 2026-04-29 | Autor: Kimi (Hermes AI)

## PODSUMOWANIE

Przeanalizowano 12 tabel w 3 warstwach:
- **Migracje SQL** (0001–0013)
- **Inline fallback** (telegram_ai.js, input_sanitizer.js)
- **Seed data** (recycled_parts_seed.sql)
- **Kod aplikacji** (datasheet.js, sessions.js, history.js, recycled_catalog.js)

---

## ✅ SPÓJNE TABELE (bez problemów)

| # | Tabela | Migracja | Inline JS | Seed | Status |
|---|--------|----------|-----------|------|--------|
| 1 | recycled_devices | 0004+0005 | ✅ | ✅ | OK |
| 2 | recycled_parts | 0004+0005+ALTERs | ✅ | ✅ | OK |
| 3 | recycled_part_master | 0005 | ✅ | ✅ | OK |
| 4 | recycled_device_parts | 0005 | ✅ | ✅ | OK |
| 5 | recycled_device_aliases | 0005 | ✅ | ✅ | OK |
| 6 | recycled_part_aliases | 0005 | ✅ | ✅ | OK |
| 7 | recycled_device_evidence | 0005 | ✅ | — (pusta) | OK |
| 8 | recycled_device_submissions | 0005+0008 | ✅ | — | OK |
| 9 | telegram_user_sessions | 0006+0007 | ✅ | — | OK* |
| 10 | recycled_devices_fts | 0009 | — | — | OK |
| 11 | providers/observations/events/recommendations | 0001 | ✅ | — | OK |
| 12 | telegram_issue_throttle | 0002 | ✅ | — | OK |
| 13 | telegram_chat_messages/limits/moderation_audit | 0003 | ✅ | — | OK |
| 14 | organization_* (8 tabel) | 0012 | — | — | OK |

*Session hack: active_device_name = pipe-delimited metadata

---

## 🔴 KRYTYCZNE PROBLEMY

### 1. `datasheets` — BRAK inline fallback w telegram_ai.js

**Co:** Nowa tabela z migracji 0013 nie ma `CREATE TABLE IF NOT EXISTS` w `ensureRecycledKnowledgeSchema()`.

**Efekt:** Jeśli migracja 0013 nie została zaaplikowana na D1, KAŻDY INSERT do `datasheets` zawiedzie z błędem "no such table".

**Rozwiązanie:** Dodać inline fallback + ensureColumn w telegram_ai.js

---

## 🟡 ŚREDNIE PROBLEMY

### 2. `parameters_json` vs `parameters` — niespójność nazewnictwa

**Co:**
- `recycled_part_master.parameters` (TEXT, JSON)
- `recycled_parts.parameters` (TEXT, JSON)
- `datasheets.parameters_json` (TEXT, JSON)

**Efekt:** Te same dane (parametry części) mają inną nazwę kolumny w różnych tabelach. Kod syncujący datasheets → master musi mapować `parameters_json` → `parameters`.

**Rozwiązanie:** Zmienić `datasheets.parameters_json` na `datasheets.parameters` (spójność) LUB zostawić z dokumentacją mapowania.

### 3. `injection_audit_log` — BRAK migracji

**Co:** Tabela istnieje TYLKO jako inline `CREATE TABLE IF NOT EXISTS` w input_sanitizer.js. Nie ma oficjalnej migracji.

**Efekt:** Brak gwarancji spójności między środowiskami (local dev vs D1 remote). Inline fallback zadziała, ale jeśli kiedyś usuniemy kod, dane znikną.

**Rozwiązanie:** Dodać migrację 0014 dla injection_audit_log.

### 4. Brak kolumny `package` w recycled_part_master i recycled_parts

**Co:** Tabela `datasheets` ma kolumnę `package` (np. SOT-23, SOIC-8), ale `recycled_part_master` i `recycled_parts` jej nie mają.

**Efekt:** Informacja o obudowie fizycznej jest dostępna tylko w datasheets. W master/parts można ją wyciągnąć z `kicad_footprint`, ale to jest KICAD REF (np. `Package_TO_SOT_THT:TO-220-3_Vertical`), nie czysty package type.

**Rozwiązanie:** Dodać `package` TEXT do recycled_part_master i recycled_parts przez ensureColumn + nową migrację.

---

## 🟢 NISKIE PROBLEMY

### 5. `active_device_name` jako pipe-delimited hack

**Co:** Pole `active_device_name` w `telegram_user_sessions` przechowuje pipe-delimited stringi typu `"ESP8266|ESP8266EX|PDF|LCSC"` zamiast strukturalnego JSON.

**Efekt:** Działa, ale jest trudne do utrzymania i podatne na błędy parsowania.

**Rozwiązanie:** Niski priorytet — zamienić na JSON blob kiedyś.

### 6. datasheet.js nie wypełnia wszystkich kolumn w submissions

**Co:** `recordRecycledSubmission` z datasheet.js nie ustawia `master_part_id`, `ingest_source`, `evidence_url`, `evidence_timecode`.

**Efekt:** Te kolumny są NULL — akceptowalne, bo są opcjonalne.

**Rozwiązanie:** Dodać `ingest_source='datasheet_bot'` dla lepszej identyfikacji źródła.

---

## REKOMENDOWANA KOLEJNOŚĆ NAPRAW

1. 🔴 Dodać inline fallback dla `datasheets` w telegram_ai.js
2. 🟡 Zmienić `parameters_json` → `parameters` w migracji 0013 (zanim jest zaaplikowana!)
3. 🟡 Dodać migrację 0014 dla `injection_audit_log`
4. 🟡 Dodać kolumnę `package` do recycled_part_master + recycled_parts
5. 🟢 Dodać `ingest_source='datasheet_bot'` w datasheet.js
