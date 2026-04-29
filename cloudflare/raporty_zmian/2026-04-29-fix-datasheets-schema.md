# Raport Zmian w Repozytorium — Straż Przyszłości
## Data: 2026-04-29 | Sesja: fix datasheets + schema consistency

---

## 📁 ZMODYFIKOWANE PLIKI

### 1. `migrations/0013_datasheets_cache.sql`
**Co:** Zmiana nazwy kolumny `parameters_json` → `parameters`  
**Dlaczego:** Spójność z `recycled_part_master.parameters` — ta sama kolumna w obu tabelach powinna nazywać się tak samo. Kolumny JSON-suffix (`pinout_json`) pozostają bo mają specyficzny format.  
**Diff:**
```diff
- parameters_json TEXT, -- JSON: all extracted InvenTree-compatible params
+ parameters TEXT, -- JSON: all extracted InvenTree-compatible params (consistent with recycled_part_master.parameters)
```

---

### 2. `src/telegram_ai.js` (linie ~2224-2291)
**Co:** Dodano inline fallback dla tabeli `datasheets` + kolumny `package`  
**Dlaczego:** D1 nie uruchamia migracji automatycznie — `ensureColumn()` w Workerze gwarantuje, że schemat istnieje niezależnie od stanu migracji. To standardowy pattern w Strażu (każda migracja ma też inline fallback).  
**Dodano:**
- `CREATE TABLE IF NOT EXISTS datasheets (...)` — pełna definicja inline
- 11 wywołań `ensureColumn()` dla datasheets (pinout_json, parameters, cross_references, application_notes, safety_notes, ai_model, ai_confidence, analysis_status, analysis_error, last_analyzed_at, analysis_count, master_part_id)
- `ensureColumn(db, "recycled_part_master", "package", "package TEXT")` — package w master
- `ensureColumn(db, "recycled_parts", "package", "package TEXT")` — package w parts

---

### 3. `src/datasheet.js` (linia ~375)
**Co:** Dodano `ingest_source: "datasheet_bot"` do `recordRecycledSubmission()`  
**Dlaczego:** Kolumna `ingest_source` istnieje w `recycled_device_submissions` i jest wypełniana przez inne flows (`telegram_pdf`, `database_or_web`). Datasheet flow nie miał tego pola = null w DB. Teraz spójnie oznaczony jako `datasheet_bot`.  
**Diff:**
```diff
  matched_part_number: partQuery,
+ ingest_source: "datasheet_bot",
  status: "approved",
```

---

## 📁 NOWE PLIKI

### 4. `migrations/0014_injection_audit_and_package.sql` ⭐ NOWY
**Co:** Oficjalna migracja dla 3 zmian schematu  
**Dlaczego:** `injection_audit_log` był tworzony tylko inline (w input_sanitizer.js). Ta migracja zapewnia jego istnienie w D1 nawet bez Worker running. Plus package + dodatkowe indexy.  
**Zawartość:**
```sql
-- 1. injection_audit_log (CREATE TABLE IF NOT EXISTS + 3 indeksy)
-- 2. ALTER TABLE recycled_part_master ADD COLUMN package TEXT
-- 3. ALTER TABLE recycled_parts ADD COLUMN package TEXT
-- 4. CREATE INDEX idx_datasheets_manufacturer ON datasheets(manufacturer)
-- 5. CREATE INDEX idx_datasheets_mounting ON datasheets(mounting, package)
```

---

## 📊 PODSUMOWANIE

| Plik | Typ | Zmian |
|------|-----|-------|
| `migrations/0013_datasheets_cache.sql` | MODIFIED | 1 rename kolumny |
| `src/telegram_ai.js` | MODIFIED | +67 linii (inline fallback + package) |
| `src/datasheet.js` | MODIFIED | +1 linia (ingest_source) |
| `migrations/0014_injection_audit_and_package.sql` | **NEW** | +50 linii (pełna migracja) |

**Łącznie:** 3 pliki zmodyfikowane, 1 nowy plik, ~119 linii dodanych

---

## ⚠️ UWAGI DO WDROŻENIA

1. **Migracja 0014** należy uruchomić na D1: `wrangler d1 execute DB --file=migrations/0014_injection_audit_and_package.sql`
2. **Inline fallback** w telegram_ai.js zadziała automatycznie po deployu — zero ryzyka bo używa `IF NOT EXISTS` i `ensureColumn()`
3. **Zmiana `parameters_json` → `parameters`** nie psuje istniejących danych bo tabela `datasheets` jest nowa (jeszcze nie w produkcji)
