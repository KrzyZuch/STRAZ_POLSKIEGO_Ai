# Odbior Portfela 07 Zadan 17 22 2026-04-25

Ten odbior zapisuje stan po dostarczeniu wynikow zadan `17-22`.

Werdykt dotyczy artefaktow i mini-handoffow obecnych w repo na dzien `2026-04-25`.
To nie jest jeszcze dowod, ze wszystkie zmiany zostaly przetestowane na zewnetrznym upstreamie ani na realnym wolontariuszu.

## Werdykty

1. `17` - `PASS z uwaga`
   - triage disputed rekordow istnieje i jest jawnie opisany
   - verification przestalo konczyc sie surowym workiem przypadkow spornych
   - uwaga: nadal brak domkniecia OCR dla `ocr_needed` i brak ostatecznej decyzji dla `likely_confirmed`
2. `18` - `PASS z uwaga`
   - curation zostala uruchomiona na realnym `test_db_verified.jsonl`
   - handoff `verification -> curation` jest juz praktycznie stabilny
   - uwaga: export nadal jest zablokowany przez OCR, manual review i auto-promoted `likely_confirmed`
3. `19` - `PASS z uwaga`
   - publiczna instrukcja sekretow i `.env.example` zostaly dowiezione
   - onboarding wolontariusza jest wyraznie latwiejszy
   - uwaga: brak jeszcze pre-flight check scope `GITHUB_PAT`, quota i testu z realnym wolontariuszem
4. `20` - `PASS z uwaga`
   - baseline secret scan i packet branch protection istnieja
   - readiness publicznego pilota jest lepiej domknieta niz poprzednio
   - uwaga: branch protection nadal wymaga recznego potwierdzenia na upstreamie, a `CODEOWNERS` wciaz nie istnieje
5. `21` - `PASS`
   - `blueprint-design-01` ma juz validator i schema baseline
   - sample brief przechodzi walidacje
6. `22` - `PASS z uwaga`
   - `esp-runtime-01` ma jawny bench test contract i polityke `simulated vs real hardware`
   - uwaga: nadal nie ma execution surface, bench report template i realnego hardware pass

## Co faktycznie zostalo odblokowane

- verification daje teraz triage-ready output zamiast nieczytelnego `disputed`
- curation pracuje juz na realnym verified snapshotcie
- wolontariusz dostaje jawna instrukcje sekretow zamiast domyslania sie setupu
- secret scan i operator packet zmniejszaja ryzyko wycieku sekretow i obchodzenia review
- `blueprint` i `esp-runtime` maja mocniejsze kontrakty wejscia zanim dostana execution surface

## Najwazniejsze luki po przyjeciu

- brak rozstrzygniecia `ocr_needed`, `manual_review` i `likely_confirmed` przed exportem
- brak jawnego pre-flight checku dla wolontariusza przed odpaleniem notebooka
- brak `CODEOWNERS` i brak potwierdzenia branch protection na upstreamie
- brak minimalnego execution surface dla `blueprint-design-01`
- brak simulated precheck runnera i bench report template dla `esp-runtime-01`

## Rekomendacja portfelowa

Nie wracaj teraz do kolejnych szerokich scaffoldow.
Nastepny portfel ma dowiezc:

1. stabilniejszy status resolution `verification -> curation -> export`,
2. realniejszy pre-flight dla publicznego pilota,
3. review enforcement dla toru PR,
4. pierwszy minimalny execution surface dla `blueprint` i sensowny precheck dla `esp-runtime`.
