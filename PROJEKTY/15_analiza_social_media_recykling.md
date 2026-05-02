# [PROJEKT 15] Automatyczna Analiza AI Polskich Sieci Społecznościowych i Portali Aukcyjnych dla Recyklingu

## Cel Projektu
Głównym celem projektu jest stworzenie inteligentnego systemu monitorującego polskie grupy społecznościowe (np. grupy "Oddam za darmo", "Śmieciarka jedzie") oraz portale aukcyjne (OLX, Allegro Lokalnie) w celu identyfikacji ofert darmowych lub bardzo tanich urządzeń elektronicznych oraz zgłoszeń indywidualnego zapotrzebowania na konkretne części.

## Projekt 15 jako warstwa resource scoutingu o wysokiej dzwigni

Ten projekt nie powinien byc traktowany jako poboczny dodatek do recyklingu. To jedna z warstw o najwyzszym potencjale, bo pozwala AI wykrywac i laczyc okazje zanim jeszcze trzeba budowac kosztowny hardware albo odpalac ciezsze wdrozenia.

Najwieksza wartosc nie zawsze lezy w pojedynczym ogloszeniu. Często powstaje dopiero wtedy, gdy system polaczy:

- ogloszenie `oddam za darmo`,
- ogloszenie `sprzedam tanio`,
- post `potrzebuje czesci` albo `szukam urzadzenia`,
- lokalizacje i czas odbioru,
- wiedze o potencjale odzysku, naprawy albo dalszego reuse.

To oznacza, ze analiza social media i ogloszen powinna byc traktowana jako pelnoprawny element warstwy `analizy potencjalu`, a nie tylko jako zrodlo leadow do katalogu.

## Kluczowe Funkcjonalności
1.  **Skanowanie Ofert:** Automatyczne pobieranie i analiza postów oraz ogłoszeń pod kątem słów kluczowych związanych z elektroniką i elektrośmieciami.
2.  **Matching Potrzeb:** System będzie łączyć osoby posiadające zbędny sprzęt z osobami, które zgłosiły zapotrzebowanie na konkretne podzespoły (np. matryca do laptopa, zasilacz).
3.  **Redukcja Marnotrawstwa:** Poprzez efektywne łączenie dawców i biorców, projekt realnie zmniejsza ilość elektrośmieci trafiających na wysypiska.
4.  **Integracja z Botem Telegram:**
    *   Użytkownicy bota `@straz_przyszlosci_bot` będą mogli zgłaszać swoje zapotrzebowanie na części.
    *   Bot będzie automatycznie rekomendował transakcje/odbiory między użytkownikami na podstawie zebranych danych.
5.  **Ocena Potencjału Relacyjnego:**
    *   System nie ocenia tylko pojedynczych ogloszen, ale rowniez potencjal wynikajacy z ich polaczenia.
    *   Najwyzszy priorytet powinny dostawac okazje, gdzie wystepuje jednoczesnie darmowa lub bardzo tania podaz, realny popyt, bliska logistyka i znana sciezka wykorzystania zasobu.
6.  **Wzbogacanie Bazy Wiedzy:**
    *   Automatyczne pobieranie danych katalogowych i specyfikacji technicznych części ze schematów dostępnych online.
    *   **Multimodalna Analiza Wideo:** System będzie analizował filmy z napraw sprzętu na YouTube. Wykorzystując model AI od Google (np. Gemini), system będzie generował stopklatki z rzutem na części elektroniczne i automatycznie rozpoznawał komponenty, wzbogacając bazę zamienników i rzadkich części.

## Architektura Danych
Baza danych części tworzona przez bota będzie centralnym punktem odniesienia, łączącym fizyczne przedmioty z ich cyfrowym śladem (schematy, stopklatki z napraw, parametry techniczne), ale docelowo powinna rowniez laczyc:

- sygnaly darmowej lub taniej podazy,
- sygnaly zapotrzebowania,
- potencjal odzysku i reuse,
- lokalizacje i koszty przejecia,
- rekomendacje co warto aktywowac najpierw.

## Status implementacji (2026-05-02)

- **Silnik scoutingowy**: `PROJEKTY/13_baza_czesci_recykling/scripts/scout_resource_signals.py` (Zadanie 56, Portfel 14)
- `categorize` — kategoryzacja sygnalow wg slow kluczowych (elektronika, AGD, narzedzia, materialy, transport)
- `assess` — ocena potencjalu (tier1_free, tier2_cheap, demand_signal, tier3_review)
- `match` — laczenie podazy z popytem z punktacja (keyword overlap + odleglosc + cena)
- `export` — pelny eksport z receiptem
- `ingest-olx-sql` — parsowanie OLX SQL dump do scout JSONL
- `ingest-olx-jsonl` — parsowanie OLX JSONL export do scout JSONL
- `ingest-manual` — ingestia recznych sygnalow (Facebook, grupy, community)
- `ingest-pipeline` — pelny pipeline: ingest→categorize→assess→match→export (Zadanie 57)
- **OLX bridge**: `PROJEKTY/13_baza_czesci_recykling/scripts/scout_ingest_olx.py` (Zadanie 57)
- Samodzielny skrypt normalizujacy OLX SQL/JSONL do scout schema
- Tryb `--auto` z deduplikacja i filtrowaniem non-resource (zwierzeta, adopcje)
- Receipt z statystykami ingesti
- **Szablony sygnalow manualnych**: `PROJEKTY/13_baza_czesci_recykling/scout_data/signals_manual/` (Zadanie 57)
- `template_facebook_group.jsonl` — 5 przykladowych sygnalow z grup FB
- `template_allegro_lokalnie.jsonl` — 3 przykladowe sygnaly Allegro
- `template_community_post.jsonl` — 3 przykladowe posty spolecznosciowe
- `README.md` — instrukcja uzupelniania
- **Status zrodel danych**:
- OLX: notebook `olx-oddam-za-darmo-scraper.ipynb` gotowy, wymaga runu na Kaggle z internetem ON; SQL dump z 6 realnymi ofertami dostepny
- Facebook Marketplace / grupy: brak integracji, szablon manualny dostepny
- Allegro Lokalnie: brak integracji, szablon manualny dostepny
- **Wyniki pipeline (Zadanie 57)**: 24 records z 6 zrodel, 57 matches (26 PRIORYTET, 31 ROZWAZ)
- **Blokery**: dostep do zywych API wymaga konta Kaggle + internetu; sekrety nie powinny trafiac do repo
