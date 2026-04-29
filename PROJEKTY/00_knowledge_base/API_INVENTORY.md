# 🔌 API Inventory — STRAŻ PRZYSZŁOŚCI

_Skanowano: 2026-04-28 | Status: Kompletny_

---

## 1. Aktywne API & Serwisy (używane w kodzie)

| # | API / Serwis | Endpoint | Env Var / Klucz | Plik(i) | Status | Free Tier |
|---|---|---|---|---|---|---|
| 1 | **Google Gemini AI** | `generativelanguage.googleapis.com/v1beta/models/{model}:generateContent` | `GEMINI_API_KEY` (CF secret) | `cloudflare/src/ai_providers.js`, `PROJEKTY/13_*/scripts/yt_*.py` | ✅ AKTYWNY | Free (15 RPM) |
| 2 | **NVIDIA NIM** (Gemma via NIM) | `integrate.api.nvidia.com/v1/chat/completions` | `NVIDIA_API_KEY` (CF secret) | `cloudflare/src/ai_providers.js` | ✅ AKTYWNY (fallback) | Free (1000 req/mo) |
| 3 | **YouTube Data API v3** | `www.googleapis.com/youtube/v3/search` | `YOUTUBE_API_KEY` (runtime arg) | `PROJEKTY/13_*/scripts/yt_autonomous_hunter.py` | ✅ AKTYWNY | Free (10K units/dzień) |
| 4 | **Google GenAI File API** | Upload wideo → analizuj multimodalnie | via `google.genai.Client` | `PROJEKTY/13_*/scripts/yt_parts_extractor.py` | ✅ AKTYWNY | Free (limit upload) |
| 5 | **GitHub API** (Issues) | `api.github.com/repos/{owner}/{repo}/issues` | `GITHUB_TOKEN` (CF secret) | `cloudflare/src/github_issues.js`, `cloudflare/src/telegram_issues.js` | ✅ AKTYWNY | Free (5000 req/h) |
| 6 | **Telegram Bot API** | `api.telegram.org/bot{token}/{method}` | `TELEGRAM_BOT_TOKEN` (CF secret) | `cloudflare/src/telegram_utils.js`, `cloudflare/src/telegram_issues.js`, `cloudflare/src/worker.js` | ✅ AKTYWNY | Free |
| 7 | **WhatsApp Business API** | Webhook (Meta) | `WHATSAPP_APP_SECRET`, `WHATSAPP_VERIFY_TOKEN` (CF secrets) | `cloudflare/src/github_issues.js` | ⚠️ WYŁĄCZONY (`WHATSAPP_ISSUES_ENABLED=false`) | Free (Meta platform) |
| 8 | **Cloudflare D1** (SQLite) | Binding `DB` | Internal CF binding | `cloudflare/src/worker.js`, `cloudflare/src/telegram_issues.js`, `cloudflare/src/recycled_catalog.js` | ✅ AKTYWNY | Free (5GB, 5M reads/d) |
| 9 | **Cloudflare Workers** | Edge runtime | — | `cloudflare/src/worker.js` | ✅ AKTYWNY | Free (100K req/d) |
| 10 | **Datasheet Scraping** | LCSC, DigiKey, Mouser, SparkFun | Brak klucza | `cloudflare/src/datasheet.js` | ✅ AKTYWNY (no-auth scrape) | Free |

---

## 2. Modele AI używane w kodzie

| Model | Provider | Zastosowanie | Plik | Free? |
|---|---|---|---|---|
| `gemini-3.1-flash-lite-preview` | Google AI Studio | Telegram AI (główny) | `wrangler.toml`, `ai_providers.js` | ✅ |
| `google/gemma-4-31b-it` | NVIDIA NIM | Telegram AI (fallback) | `wrangler.toml`, `ai_providers.js` | ✅ |
| `gemma-4-31b-it` | Google AI Studio | YT video analysis (Faza 1+2) | `yt_parts_extractor.py` (pipeline) | ✅ |
| `gemini-3.1-flash-lite-preview` | Google AI Studio | YT video analysis (hunter — nowsza wersja) | `yt_autonomous_hunter.py` | ✅ |

---

## 3. Sekrety Cloudflare Workers (z `wrangler.toml` vars + secrets)

### Vars (non-secret config):
- `DEPLOYMENT_ENVIRONMENT`, `ALLOWED_PROVIDER_ENVIRONMENTS`
- `GITHUB_REPO_OWNER=StrazPrzyszlosci`, `GITHUB_REPO_NAME=STRAZ_PRZYSZLOSCI`
- `TELEGRAM_AI_*` (model, timeout, temperature, rate limits, memory)
- `TELEGRAM_ISSUES_ENABLED`, `TELEGRAM_AI_ENABLED`, `WHATSAPP_ISSUES_*`

### Secrets (wymagane w CF Dashboard):
- `GEMINI_API_KEY` — Google AI Studio
- `NVIDIA_API_KEY` — NVIDIA NIM
- `GITHUB_TOKEN` — GitHub PAT (do tworzenia Issues)
- `TELEGRAM_BOT_TOKEN` — Telegram Bot
- `TELEGRAM_WEBHOOK_SECRET_TOKEN` — weryfikacja webhooka
- `WHATSAPP_APP_SECRET` — Meta webhook verify
- `WHATSAPP_VERIFY_TOKEN` — Meta webhook challenge

---

## 4. Narzędzia CLI używane w skryptach

| Narzędzie | Wersja/Ścieżka | Zastosowanie | Plik |
|---|---|---|---|
| `yt-dlp` | system | Pobieranie wideo YT (low-res + high-res) | `yt_parts_extractor.py`, `yt_autonomous_hunter.py` |
| `ffmpeg` | system | Wycinanie klatek, kompresja, time-lapse | j.w. |
| `ffprobe` | system | Sprawdzanie długości wideo | `yt_autonomous_hunter.py` |
| `node` | `v24.13.1` (nvm) | JS runtime dla yt-dlp remote components | j.w. |

---

## 5. Zewnętrzne repozytoria / dependencje

| Repo / Projekt | Kontekst | Zaimportowane? | Uwagi |
|---|---|---|---|
| `StrazPrzyszlosci/STRAZ_PRZYSZLOSCI` | Główny repo (self) | — | GitHub Issues jako kanban |
| Antigravity (`~/.gemini/antigravity/`) | Gemini CLI workspace | Częściowo | `parse_mistral.py` czyta z antigravity brain |
| `google-genai` (PyPI) | Python SDK | Tak (pip) | `from google import genai` |
| `node` nvm | JS runtime | Tak (system) | v24.13.1 |

---

## 6. Możliwości niewykorzystane (potencjał)

| Możliwość | Status | Opis |
|---|---|---|
| WhatsApp → GitHub Issues | Skonfigurowany, ale WYŁĄCZONY | Gotowy do aktywacji — wymaga `WHATSAPP_ISSUES_ENABLED=true` + `WHATSAPP_ALLOWED_SENDERS` |
| Vision AI (rezystory) | ✅ Działa | `vision.js` — rozpoznawanie rezystorów + części ze zdjęć |
| Datasheet auto-search | ✅ Działa | `datasheet.js` — LCSC/DigiKey/Mouser/SparkFun |
| YouTube autonomous hunter | ✅ Działa | Pełny pipeline: kanały → słowa kluczowe → analizuj wideo → weryfikuj klatkami HQ |
| Kaggle enrichment | ✅ Działa | `pack-project13-kaggle-enrichment-01` — enrich bazy części z Kaggle |
| Cloudflare D1 backup/split | ✅ Działa | `pipelines/split_d1_backup.py`, `pipelines/sync_organization_entities_to_sqlite.py` |
| Knowledge bundle export | ✅ Działa | `pipelines/export_chatbot_knowledge_bundle.py`, `pipelines/export_knowledge_snapshot.py` |

---

## 7. Priorytety nauki — kolejne API do opanowania (FREE)

1. **Firecrawl** — web scraping z AI (mamy skill w Hermes) — do content research portali
2. **NotebookLM audio** — AI-narrated podcasts z artykułów (za darmo)
3. **YouTube Data API v3** — pełne wykorzystanie (transkrypcje, stats, playlisty)
4. **Google Custom Search API** — 100 queries/dzień za darmo
5. **Cloudflare KV / R2** — darmowy storage statyczny dla portalu
6. **GitHub Actions** — CI/CD już skonfigurowane, można dodać automatyzacje
