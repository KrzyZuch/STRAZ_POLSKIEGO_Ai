# 01. Inteligentna Akwakultura (Smart Fish Farming)

## Opis Projektu
Koncepcja "Smart Fish Farming" opiera się na stworzeniu w pełni autonomicznych systemów hodowli ryb, w których ludzka praca jest wspierana przez Sztuczną Inteligencję oraz Internet Rzeczy (IoT). System ten ma na celu zapewnienie stabilnego i wydajnego źródła żywności przy minimalnym nakładzie pracy i zasobów.

### Kluczowe funkcjonalności:
- **Pełna autonomia i monitoring:** Czujniki IoT na bieżąco badają jakość wody (poziom pH, tlenu, amoniaku) i błyskawicznie reagują na zagrożenia.
- **Optymalizacja zasobów:** Algorytmy AI analizują wiek, rozmiar i zachowanie ryb, precyzyjnie dawkując pokarm, co eliminuje marnotrawstwo.
- **Bezpieczeństwo i ekologia:** Wczesne wykrywanie chorób oraz inteligentne zarządzanie wodą i energią (zasilanie OZE).

## Wizja Straży Przyszłości
Właśnie tego typu skalowalne, bezobsługowe rozwiązania są jednym z głównych celów **Narodowych Sił Intelektualnych Polski**. Naszym celem jest zaprojektowanie i uruchomienie całkowicie autonomicznych węzłów produkcji żywności, które będą tworzyć technologiczną "gospodarkę bis". Wygenerowane w ten sposób nadwyżki i tania żywność mają docelowo zasilać fundusz **Bezwarunkowego Dochodu Podstawowego (UBI)**.

## Dwa kanały wejścia do projektu

Ten projekt potrzebuje dwóch osobnych onboardingów:

1. **onboardingu Strażnika**, czyli wejścia nowej osoby do inicjatywy przez zewnętrzną ankietę i rekomendator zadań,
2. **onboardingu providera**, czyli technicznej ścieżki dla węzłów i uczestników, którzy chcą wysyłać dane do API.

To rozróżnienie jest ważne, bo większość nowych osób nie zacznie od rejestracji providera. Najpierw potrzebują zrozumieć, gdzie w projekcie mogą wnieść najlepszy wkład: w hardware, analizę danych, dokumentację, edge vision, API albo organizację.

Dlatego zewnętrzna strona inicjatywy powinna działać jako rekomendator ścieżek wejścia, a to repozytorium powinno utrzymywać:

- katalog rekomendacji zadań,
- projekty i dokumenty startowe,
- backlog pierwszych Issues,
- osobny onboarding providera dla tych, którzy chcą zasilać wspólne API.

## Minimalne API `v1` dla pilotażu stawu hodowlanego

Pierwsza wersja interfejsu powinna być minimalistyczna i skupiona na dwóch rzeczach:

1. monitoringu jakości i przepływu wody,
2. odbieraniu wyników lokalnej analizy zachowania ryb.

Jeżeli Strażnicy Przyszłości mają rzeczywiście dostarczać dane do wspólnego systemu, to ten kontrakt musi być obsługiwany przez **działający serwer**, a nie tylko dokumentację. Dlatego minimalna architektura projektu zakłada punkt rejestracji providerów i żywe endpointy HTTP, przez które węzły terenowe, stare smartfony, gospodarstwa i partnerzy zewnętrzni będą mogli włączać się do wspólnej warstwy wiedzy.

Repozytorium nie powinno być miejscem składowania surowych, bieżących odczytów providerów. Te dane powinny trafiać do działającego serwera i bazy operacyjnej, natomiast do repozytorium powinny trafiać tylko dane przykładowe, dane opracowane, przypadki użycia, dokumentacja i wiedza wyprowadzona z analizy.

Na tym etapie nie zakładamy przesyłania ciągłego strumienia wideo przez publiczne API. Byłoby to zbyt ciężkie infrastrukturalnie, kosztowne energetycznie i trudne do utrzymania w warunkach społecznościowych oraz terenowych.

### Publiczne ścieżki API

Minimalna powierzchnia API dla projektu:

```text
POST /v1/providers/register
POST /v1/providers/{provider_id}/tokens/rotate
POST /v1/observations
POST /v1/events
POST /v1/recommendations/fish-pond
GET /v1/providers/{provider_id}/status
```

### Punkt rejestracji providerów

Endpoint `POST /v1/providers/register` jest potrzebny po to, aby każdy provider mógł jawnie zgłosić się do systemu z informacją:

- kim jest,
- jakie typy danych obsługuje,
- czy działa jako firma, gospodarstwo, provider społecznościowy lub stary smartfon,
- czy wspiera monitoring jakości wody, przepływu i edge vision.

To ważne, ponieważ w naszym modelu providerem może zostać każdy, a nie tylko duży partner zewnętrzny.

Po rejestracji provider powinien otrzymywać jednorazowo `write_token`, który następnie służy do autoryzacji zapisów przez nagłówek `X-Provider-Token`.

Ponowna rejestracja tego samego `provider_id` nie powinna służyć do odzyskiwania dostępu. Wymiana sekretu powinna odbywać się wyłącznie przez dedykowany endpoint rotacji tokenu.

### Zakres `POST /v1/observations`

Ten endpoint przyjmuje podstawowe pomiary stawu. W pierwszej wersji powinien obsługiwać:

```text
pond_id
measurement_time
water_temperature
dissolved_oxygen
pH
optional ammonia
optional flow_rate
```

To jest rdzeń minimalnego monitoringu, który pozwala:

- wykrywać ryzyko przyduchy,
- sygnalizować pogorszenie jakości wody,
- porównywać stan stawu między pomiarami i providerami,
- budować wspólną bazę wiedzy w repozytorium.

### Zakres `POST /v1/events`

Ten endpoint powinien przyjmować zdarzenia z analizy lokalnej i z warstwy terenowej, na przykład:

- `fish_behavior_summary`
- `water_quality_alert`
- `flow_anomaly`
- `manual_inspection_note`
- `edge_vision_low_confidence`

To właśnie tutaj powinny trafiać wyniki analizy obrazu ryb wykonywanej lokalnie na urządzeniu brzegowym.

### Zakres `POST /v1/recommendations/fish-pond`

Ten endpoint powinien zwracać wynik analityczny w ujednoliconej postaci:

```text
risk_level
recommendation
confidence
reason_codes
provider_id
schema_version
```

Wynik ma służyć budowie bazy wiedzy, porównywaniu przypadków i dokumentowaniu sytuacji w stawie. Nie jest to kanał zdalnego sterowania urządzeniami.

## Analiza obrazu ryb: podejście `edge-first`

Najbardziej sensowny model dla tego projektu to analiza obrazowa wykonywana lokalnie, blisko kamery, a nie przesyłanie surowego obrazu do centralnego API.

### Dlaczego nie surowe wideo w `v1`

Ciągłe przesyłanie wideo ze stawu jest na tym etapie karkołomne, ponieważ:

- wymaga dużej przepustowości i stabilnego łącza,
- szybko zużywa energię na urządzeniu terenowym,
- komplikuje archiwizację i przegląd materiału,
- utrudnia udział społeczności korzystającej z tanich i starych urządzeń,
- daje dużo danych o niskiej wartości, jeśli nie ma wcześniej selekcji zdarzeń.

### Zalecany model działania

Wersja minimalna powinna działać tak:

1. kamera lub stary smartfon obserwuje wybrany fragment stawu,
2. lokalny moduł robi analizę na małej liczbie klatek lub krótkich oknach czasowych,
3. urządzenie wylicza wskaźniki zachowania ryb,
4. do API trafia tylko wynik analizy, a nie pełny materiał wideo.

### Jakie wyniki analizy obrazu warto wysyłać

W pierwszej wersji warto wysyłać tylko lekkie metryki i flagi, na przykład:

- poziom aktywności ryb,
- wykrycie nietypowego skupiania się przy powierzchni,
- sygnał możliwego łapania powietrza,
- anomalię ruchu lub nagły spadek aktywności,
- liczbę wykrytych martwych lub nieruchomych obiektów, jeśli model daje radę,
- poziom pewności wyniku.

Takie wyniki są wystarczające, by zasilać wspólny model wiedzy i porównywać przypadki między stawami.

## Stare smartfony jako urządzenia brzegowe

Stare smartfony są tu bardzo ciekawym kandydatem, ale tylko przy dobrze dobranym zakresie zadań. Najbardziej realistyczny scenariusz to:

- prosty model skwantyzowany,
- analiza co kilka sekund lub na ograniczonej liczbie klatek,
- praca na wycinku obrazu zamiast pełnej rozdzielczości,
- wysyłka jedynie wyników liczbowych i zdarzeń,
- opcjonalny zapis bardzo krótkich klipów tylko przy wykryciu anomalii.

Na starszym urządzeniu trzeba unikać:

- ciągłej analizy pełnego wideo w wysokiej rozdzielczości,
- ciągłego uploadu nagrań,
- zbyt ciężkich modeli wymagających nowoczesnego NPU lub GPU.

## Oficjalna architektura: stare smartfony + centralne API + wspólna baza wiedzy

Najbardziej realistyczny i najcenniejszy dla Straży Przyszłości model nie polega na budowie ciężkiego klastra obliczeniowego ze smartfonów, lecz na budowie **rozproszonej sieci węzłów edge**.

W tym modelu:

1. stary smartfon lub lekki węzeł z ESP32 zbiera dane z czujników,
2. smartfon pełni rolę providera lub bramki danych,
3. smartfon może wykonać lekką analizę lokalną, np. zachowania ryb,
4. dane i zdarzenia trafiają do centralnego API z rejestracją providerów,
5. centralna warstwa operacyjna przechowuje bieżące odczyty i zwraca wyniki analityczne,
6. repozytorium przechowuje standard, modele, dokumentację i wiedzę opracowaną.

To właśnie ten model daje społeczności realny wkład w inicjatywę:

- każdy może uruchomić własny węzeł,
- każdy może zasilać wspólne API,
- każdy może rozwijać adaptery i logikę analityczną,
- wspólny dorobek zostaje po stronie Straży Przyszłości.

## Wariant wdrożeniowy Cloudflare Workers

Jednym z najbardziej praktycznych wariantów `v1` jest lekka warstwa koordynacyjna typu edge/cloud, np. **Cloudflare Workers**.

W tym wariancie:

- rejestracja providerów odbywa się przez publiczny endpoint,
- provider po rejestracji otrzymuje `write_token`,
- obserwacje i zdarzenia trafiają do centralnego API,
- operacyjne dane są przechowywane poza repozytorium,
- stare smartfony i węzły społecznościowe nie muszą wystawiać własnych publicznych serwerów,
- wspólny standard pozostaje pod kontrolą Straży Przyszłości.

Artefakty dla tego wariantu są utrzymywane w katalogu:

- [`cloudflare/README.md`](../cloudflare/README.md)
- [`cloudflare/wrangler.toml`](../cloudflare/wrangler.toml)
- [`cloudflare/src/worker.js`](../cloudflare/src/worker.js)
- [`cloudflare/src/recommendation.js`](../cloudflare/src/recommendation.js)
- [`cloudflare/migrations/0001_init.sql`](../cloudflare/migrations/0001_init.sql)
- [`cloudflare/provider_smoke_test.py`](../cloudflare/provider_smoke_test.py)
- [`docs/RUNBOOK_WDROZENIA_CLOUDFLARE_D1.md`](../docs/RUNBOOK_WDROZENIA_CLOUDFLARE_D1.md)

## Inteligentne podejście do wideo

Jeśli kiedyś wideo ma wejść do projektu, to nie jako domyślny strumień do API, lecz jako mechanizm wyjątków:

- zapis krótkiego klipu tylko przy wykryciu anomalii,
- lokalny bufor kołowy nadpisujący stare nagrania,
- wysyłka wyłącznie miniatury, metadanych albo referencji do lokalnego pliku,
- ręczne lub okresowe zgrywanie materiału do analizy badawczej.

To pozwala zachować użyteczny materiał dowodowy bez zamieniania całego systemu w ciężką platformę wideo.

## Artefakty techniczne w repozytorium

Dla tego projektu warstwa minimalnej integracji powinna być utrzymywana jako:

- [`schemas/fish_pond_v1.yaml`](../schemas/fish_pond_v1.yaml)
- [`openapi/fish_pond_api_v1.yaml`](../openapi/fish_pond_api_v1.yaml)
- [`api/server.py`](../api/server.py)
- [`api/README.md`](../api/README.md)
- [`api/storage.py`](../api/storage.py)
- [`cloudflare/README.md`](../cloudflare/README.md)
- [`data/sample/fish_pond_observation.json`](../data/sample/fish_pond_observation.json)
- [`data/sample/fish_behavior_event.json`](../data/sample/fish_behavior_event.json)
- [`data/sample/fish_pond_recommendation.json`](../data/sample/fish_pond_recommendation.json)
- [`pipelines/export_knowledge_snapshot.py`](../pipelines/export_knowledge_snapshot.py)
- [`reports/README.md`](../reports/README.md)

## Eksport wiedzy z warstwy operacyjnej

To, że repozytorium nie przechowuje surowych odczytów providerów, nie oznacza utraty wartości poznawczej tych danych. Przeciwnie, potrzebna jest jawna ścieżka:

1. provider przesyła dane do warstwy operacyjnej,
2. dane są przechowywane poza repozytorium,
3. z danych wyprowadzany jest snapshot wiedzy lub raport zbiorczy,
4. dopiero taki opracowany materiał trafia do repozytorium jako wkład społeczności.

W praktyce oznacza to, że stary smartfon, węzeł ESP32 albo provider zewnętrzny dokłada realne pomiary do wspólnego systemu, a Straż Przyszłości zachowuje w repozytorium to, co najcenniejsze: standard, interpretację, modele i wiedzę.

Operacyjna obsługa dostępu providera również musi być częścią tego dorobku. Dlatego w repozytorium powinny być utrzymywane nie tylko schematy i modele, ale także jawne runbooki i narzędzia dla maintainera, które pozwalają bezpiecznie odzyskać działanie społecznościowego węzła bez publikowania sekretów.

Równie ważna jest wspólna konwencja `provider_id`, bo to ona pozwala odróżnić środowiska `local`, `demo`, `preview`, `staging` i `prod`, a także uniknąć chaosu wśród społecznościowych węzłów oraz partnerów zewnętrznych.

Sama poprawna nazwa to jeszcze nie wszystko. Publiczne API powinno dodatkowo pilnować, czy environment wpisany w `provider_id` jest dopuszczony w danym deploymentcie. Dzięki temu środowisko `prod` nie przyjmie przez pomyłkę providerów z `demo`.

## Najrozsądniejsza ścieżka wdrożenia

1. Najpierw uruchomić stabilny monitoring jakości i przepływu wody.
2. Następnie dodać lekką analizę zachowania ryb na urządzeniu brzegowym.
3. Dopiero później rozważać anomaliowe klipy wideo jako materiał pomocniczy.

Taka kolejność daje największą szansę na działający system, który realnie zasili bazę wiedzy Straży Przyszłości i Narodowych Sił Intelektualnych.

## Repozytoria do adaptacji i dalszej pracy Strażników Przyszłości

Najważniejsza wiadomość dla pasjonatów jest prosta: **kod już istnieje**. Nie musimy zaczynać od zera. Naszym zadaniem jest wyszukiwanie, rozumienie, łączenie i adaptacja gotowych rozwiązań do warunków polskich, do realnych stawów hodowlanych oraz do wspólnego API Straży Przyszłości.

Co równie ważne, nie każdy Strażnik musi zaczynać od posiadania własnego urządzenia pomiarowego albo własnego sterownika. Jeżeli dane są dostarczane przez providerów i społeczność przez wspólne API, to można wnosić pełnoprawny wkład również przez:

- projektowanie schematów i kontraktów,
- budowę adapterów,
- walidację jakości danych,
- analizę przypadków i reguł rekomendacyjnych,
- dokumentację i porządkowanie wiedzy,
- kurację gotowego kodu do adaptacji.

Dlatego obok repozytoriów stricte sensorowych warto pokazywać również przykłady otwartych ekosystemów danych.

## Przykład referencyjny: openSenseMap

Jednym z najlepszych przykładów, które warto pokazywać nowym Strażnikom, jest `openSenseMap`.

- Repozytorium GitHub: [https://github.com/sensebox/openSenseMap](https://github.com/sensebox/openSenseMap)
- Strona projektu: [https://sensebox.github.io/en/osem](https://sensebox.github.io/en/osem)
- FAQ i dokumentacja: [https://docs.sensebox.de/docs/misc/opensensemap/faq/](https://docs.sensebox.de/docs/misc/opensensemap/faq/)
- Film YouTube: [https://www.youtube.com/watch?v=I8ZeT6hzjKQ](https://www.youtube.com/watch?v=I8ZeT6hzjKQ)

To nie jest projekt stawowy jeden do jednego, ale jest bardzo ważny jako wzorzec architektury opartej na danych dostarczanych przez API. Pokazuje, że:

- otwarta platforma może gromadzić dane sensoryczne od społeczności,
- różne urządzenia i aplikacje mogą zasilać wspólny system,
- wartość projektu rośnie dzięki danym, API i pracy interpretacyjnej, a nie tylko dzięki samemu hardware,
- osoby bez własnego sprzętu mogą nadal budować warstwę wiedzy, integracji i analizy.

Właśnie dlatego `openSenseMap` powinien być traktowany u nas nie jako ciekawostka, ale jako **dowód, że model współpracy oparty na wspólnym API i społecznościowych danych badawczych jest realny**.

Poniższe repozytoria są szczególnie cenne, bo mogą przyspieszyć budowę monitoringu jakości wody, lekkich węzłów terenowych i warstwy edge dla akwakultury:

### 1. Gotowe systemy monitoringu jakości wody

- **KnowFlow_AWM**  
  Link: [https://github.com/KnowFlow/KnowFlow_AWM](https://github.com/KnowFlow/KnowFlow_AWM)  
  Bardzo wartościowy punkt startowy dla otwartego monitoringu jakości wody. Obejmuje pomiary takich parametrów jak temperatura, pH i dissolved oxygen. To świetny materiał do adaptacji dla osób, które chcą zrozumieć architekturę całego urządzenia i firmware.

- **IoT-WQMS**  
  Link: [https://github.com/pkErbynn/IoT-WQMS](https://github.com/pkErbynn/IoT-WQMS)  
  Dobry przykład kompletnego przepływu: czujniki, mikrokontroler, backend, baza danych, dashboard i alerty. Repo może być szczególnie cenne dla tych, którzy chcą budować pełny tor `pomiar -> przesył -> analiza -> wizualizacja`.

- **IoT-Water-Quality-Monitoring**  
  Link: [https://github.com/JuliaSteiwer/IoT-Water-Quality-Monitoring](https://github.com/JuliaSteiwer/IoT-Water-Quality-Monitoring)  
  Bardzo ciekawy projekt dla rozproszonych węzłów pomiarowych. Zawiera wątki związane z LoRaWAN, deep sleep i wieloma parametrami jakości wody, w tym pH i dissolved oxygen. To może być skarb dla osób myślących o czujnikach terenowych o niskim poborze energii.

### 2. Klocki do budowy własnych węzłów i driverów sensorów

- **atlas_scientific**  
  Link: [https://github.com/jvsalo/atlas_scientific](https://github.com/jvsalo/atlas_scientific)  
  Zestaw narzędzi CLI do obsługi czujników Atlas Scientific dla pH, EC i dissolved oxygen. Bardzo wartościowy dla osób, które chcą budować stabilny pomiar na Raspberry Pi lub innym lekkim węźle Linuxowym.

- **Renke_DissolvedOxygen_Sensor**  
  Link: [https://github.com/bartzdev/Renke_DissolvedOxygen_Sensor](https://github.com/bartzdev/Renke_DissolvedOxygen_Sensor)  
  Konkretny klocek do priorytetowego dla nas parametru, czyli natlenienia. Jeśli ktoś chce zająć się przede wszystkim warstwą `dissolved oxygen`, to tu jest bardzo dobry materiał startowy pod ESP32 i urządzenia terenowe.

- **M5StickC_PH_sensor**  
  Link: [https://github.com/McOrts/M5StickC_PH_sensor](https://github.com/McOrts/M5StickC_PH_sensor)  
  Prosty i bardzo praktyczny przykład pod pH na ESP32. Może być szczególnie interesujący dla tych, którzy chcą szybko zbudować tani moduł pomiarowy lub przetestować odczyt pH bez wchodzenia od razu w duży system.

- **Open-Water-Level**  
  Link: [https://github.com/COAST-Lab/Open-Water-Level](https://github.com/COAST-Lab/Open-Water-Level)  
  To nie jest system stricte do chemii wody, ale może być bardzo cenny dla poziomu wody, ubytków i kontekstu przepływu. Dla części stawów i kanałów doprowadzających taki komponent może być niezwykle ważny.

### 3. Projekty pokrewne, z których można brać wzorce modułowości

- **Aquareo**  
  Link: [https://github.com/fnandes/aquareo](https://github.com/fnandes/aquareo)  
  Projekt akwaryjny, ale bardzo wartościowy jako przykład modułowej architektury na ESP32. Pokazuje, jak budować monitoring parametrów wody i lekkie komponenty terenowe bez zamykania się w jednym ciężkim systemie.

## Jak Strażnicy Przyszłości powinni z tego korzystać

Te repozytoria nie mają być traktowane jako gotowy „produkt końcowy”, tylko jako **surowiec strategiczny** dla Narodowych Sił Intelektualnych.

## Trzy repozytoria priorytetowe do realnego reuse

Jeżeli mamy zacząć od najbardziej użytecznych źródeł kodu, to na ten moment najlepsza trójka wygląda tak:

### 1. KnowFlow_AWM

Link: [https://github.com/KnowFlow/KnowFlow_AWM](https://github.com/KnowFlow/KnowFlow_AWM)

To jest najlepszy kandydat do przejęcia wzorców sprzętowych i firmware dla podstawowego monitoringu jakości wody.

Co warto z niego adaptować:

- architekturę urządzenia pomiarowego,
- obsługę czujników temperatury, pH i dissolved oxygen,
- logikę cyklicznego odczytu parametrów,
- podejście do modułowości sensorów i późniejszej rozbudowy,
- wzorce dla węzłów terenowych budowanych przez społeczność.

Do czego u nas to pasuje:

- do `POST /v1/observations`,
- do budowy społecznościowych węzłów pomiarowych,
- do pierwszych eksperymentów z natlenieniem i pH w realnym stawie.

### 2. IoT-WQMS

Link: [https://github.com/pkErbynn/IoT-WQMS](https://github.com/pkErbynn/IoT-WQMS)

To jest najlepszy kandydat do przejęcia wzorców pełnego przepływu danych od sensora do backendu.

Co warto z niego adaptować:

- logikę przesyłania danych z mikrokontrolera do serwera,
- strukturę prostego backendu i przechowywania obserwacji,
- wzorce alertów i wizualizacji wyników,
- pomysł na prosty tor `pomiar -> zapis -> analiza -> odczyt wyniku`.

Do czego u nas to pasuje:

- do `openapi/fish_pond_api_v1.yaml`,
- do budowy `adapters/provider_template/`,
- do późniejszego `pipelines/demo/` i prostego dashboardu lub eksportu danych.

### 3. IoT-Water-Quality-Monitoring

Link: [https://github.com/JuliaSteiwer/IoT-Water-Quality-Monitoring](https://github.com/JuliaSteiwer/IoT-Water-Quality-Monitoring)

To jest najlepszy kandydat do przejęcia wzorców dla rozproszonych i energooszczędnych węzłów danych.

Co warto z niego adaptować:

- wzorce komunikacji dla czujników pracujących daleko od infrastruktury,
- podejście do niskiego poboru energii i pracy okresowej,
- logikę rozproszonego zbierania pomiarów,
- pomysły na stacje terenowe, które nie muszą mieć stałego Wi-Fi.

Do czego u nas to pasuje:

- do stawów oddalonych od zabudowań,
- do społecznościowych instalacji DIY,
- do budowy tanich węzłów z ESP32, LoRa i ewentualnie starym smartfonem jako bramką danych.

## Co konkretnie powinniśmy z tych repo wyciągać

Najlepsza ścieżka pracy nie polega na kopiowaniu całych cudzych systemów. Lepiej wyciągać z nich tylko to, co wzmacnia nasz własny standard.

Z repozytoriów zewnętrznych warto przejmować:

- sterowniki i biblioteki do sensorów,
- przykłady kalibracji czujników,
- struktury odczytu i próbkowania danych,
- lekkie wzorce transmisji HTTP, MQTT albo LoRa,
- rozwiązania dla pracy w terenie i przy słabym zasilaniu,
- wzorce zapisu lokalnego przy chwilowej utracie łączności.

Nie powinniśmy bezrefleksyjnie przejmować:

- całej obcej architektury backendowej jako naszego rdzenia,
- cudzych modeli danych jako formatu nadrzędnego,
- zamkniętych zależności sprzętowych lub usługowych,
- logiki, która związałaby nas z jednym dostawcą albo jedną platformą.

## Jak to przełożyć na zadania dla społeczności

Każdy zainteresowany Strażnik Przyszłości może wejść w ten projekt jedną z trzech ścieżek:

### Ścieżka 1: sensory i elektronika

- testowanie sterowników pH, DO, temperatury i przepływu,
- porównywanie jakości odczytów,
- dokumentowanie kalibracji i stabilności pomiarów,
- budowa węzłów terenowych na ESP32 lub Raspberry Pi.

### Ścieżka 2: integracja i API

- mapowanie danych z cudzych repo do naszego schematu `fish_pond_v1`,
- tworzenie adapterów providerów,
- dopracowanie payloadów dla `observations` i `events`,
- budowa prostych mostów dla importu danych z istniejących systemów.

### Ścieżka 3: edge i analiza zachowania ryb

- szukanie lekkich modeli pod stare smartfony,
- testowanie analizy obrazu na małej liczbie klatek,
- zamiana obrazu na lekkie wyniki analityczne,
- budowa warstwy `fish_behavior_summary`, bez pchania surowego wideo do API.

Najbardziej wartościowe działania społeczności to:

- analiza, które fragmenty kodu są stabilne i warte przejęcia,
- mapowanie gotowych sterowników i formatów danych do naszego wspólnego API,
- dokumentowanie kalibracji czujników pH, DO, temperatury, amoniaku i przepływu,
- przygotowanie lekkich wersji dla ESP32, Raspberry Pi i starych smartfonów,
- wyciąganie z obcych repo tego, co uniwersalne, bez uzależniania się od ich całej architektury.

## Ważny przekaz dla pasjonatów

Jeżeli interesuje Cię elektronika, IoT, sensory, ESP32, Raspberry Pi, stare smartfony, akwakultura albo analiza obrazu w terenie, to ten obszar jest prawdopodobnie jednym z największych skarbów całego repozytorium.

Tutaj naprawdę nie chodzi o „wymyślanie wszystkiego od nowa”. Chodzi o to, żeby:

- znaleźć gotowy kod,
- zrozumieć go,
- dopracować go do naszych warunków,
- opisać go porządnie,
- a potem przekształcić w trwały dorobek Straży Przyszłości.

**Kod już jest. Potrzeba tylko ludzi, którzy potrafią go twórczo zaadaptować.**

## Backlog Issues dla Strażników Przyszłości

Poniżej znajduje się pierwszy operacyjny backlog dla tego projektu. Każdy z tych punktów można zamienić w osobne Issue na GitHubie.

### `issue:aq-01` Adaptacja odczytu dissolved oxygen dla ESP32

- Przeanalizować repo `Renke_DissolvedOxygen_Sensor`.
- Sprawdzić, jak najlepiej mapować odczyt do pola `dissolved_oxygen_mg_l`.
- Udokumentować wymagania sprzętowe, konwertery i kalibrację.

### `issue:aq-02` Adaptacja odczytu pH dla taniego węzła pomiarowego

- Przeanalizować repo `M5StickC_PH_sensor` oraz rozwiązania Atlas Scientific.
- Porównać stabilność i koszt wariantów pH.
- Opisać minimalny tor `czujnik -> odczyt -> normalize()`.

### `issue:aq-03` Węzeł terenowy jakości wody na ESP32

- Połączyć odczyt temperatury, pH i DO w jednym lekkim firmware.
- Zaprojektować format danych zgodny z `fish_pond_v1`.
- Przygotować referencyjny adapter lub eksport JSON.

### `issue:aq-04` Provider społecznościowy oparty o stary smartfon

- Opisać architekturę, w której stary smartfon działa jako bramka danych.
- Sprawdzić komunikację z ESP32 przez Wi-Fi, Bluetooth lub USB OTG.
- Zdefiniować minimalny proces buforowania i wysyłki danych do API.

### `issue:aq-05` Walidacja jakości danych pomiarowych

- Rozszerzyć reguły walidacji o zakresy ostrzegawcze i diagnostyczne.
- Rozróżnić dane `measured`, `estimated` i `simulated`.
- Dodać czytelne komunikaty dla błędnych jednostek i niepełnych pomiarów.

### `issue:aq-06` Reguły rekomendacyjne dla ryzyka przyduchy

- Doprecyzować progi dla `dissolved_oxygen`, `pH`, temperatury i amoniaku.
- Dodać więcej `reason_codes`.
- Porównać zachowanie modelu dla kilku przykładowych scenariuszy stawu.

### `issue:aq-07` Edge-first analiza zachowania ryb

- Poszukać lekkich modeli możliwych do uruchomienia na starych smartfonach.
- Ograniczyć wynik do prostych metryk: aktywność, zachowanie przy powierzchni, anomalie.
- Zasilić endpoint `POST /v1/events` zamiast przesyłać pełne wideo.

### `issue:aq-08` Anomaliowe klipy wideo jako materiał pomocniczy

- Zbadać lokalny bufor kołowy dla krótkich klipów.
- Opracować zasady zapisu tylko przy wykryciu anomalii.
- Nie dopuszczać ciągłego przesyłania strumienia wideo do publicznego API.

### `issue:aq-09` Import danych z zewnętrznego providera do wspólnego schematu

- Rozwinąć `adapters/provider_a/` jako wzorzec realnej integracji.
- Pokazać mapowanie natywnego payloadu providera do `SensorObservation`.
- Udowodnić, że model daje ten sam wynik niezależnie od dostawcy.

### `issue:aq-10` Demo end-to-end dla repozytorium

- Utrzymać działający przepływ `sample data -> adapter -> model -> recommendation`.
- Dodać instrukcję uruchomienia dla nowych współtwórców.
- Użyć tego demo jako punktu wejścia dla nowych Strażników Przyszłości.

### `issue:aq-11` Checklist kalibracji czujników

- Przygotować checklistę dla pH, DO, temperatury i opcjonalnie amoniaku.
- Opisać częstotliwość kalibracji i typowe błędy.
- Związać dokumentację kalibracyjną z jakością danych w repo.

### `issue:aq-12` Dokumentacja przeglądu repozytoriów do adaptacji

- Rozpisać, które moduły z `KnowFlow_AWM`, `IoT-WQMS` i `IoT-Water-Quality-Monitoring` są warte przejęcia.
- Odróżnić elementy przydatne od tych, które nie pasują do naszego standardu.
- Zostawić jasne notatki dla kolejnych osób wchodzących do projektu.

### `issue:aq-32` Adaptacja lekcji z openSenseMap do modelu Straży Przyszłości

- Przeanalizować `sensebox/openSenseMap` jako wzorzec otwartego ekosystemu danych dostarczanych przez API.
- Rozpisać, które elementy warto przejąć na poziomie architektury współpracy, a nie tylko sprzętu.
- Pokazać w onboardingach, że pełnoprawny wkład jest możliwy także bez własnego urządzenia pomiarowego.

### `issue:aq-33` Ścieżka wejścia bez własnego hardware

- Dopiąć onboarding i rekomendator tak, aby osoba bez czujników, sterownika i dostępu do stawu dostawała jasną ścieżkę wejścia przez schematy, API, adaptery, dokumentację i adaptację gotowego kodu.
- Powiązać tę ścieżkę z `docs/PRZYKLADY_GOTOWEGO_KODU.md` oraz backlogiem pierwszych zadań.
- Utrzymać profesjonalny przekaz: brak własnego sprzętu nie obniża rangi wkładu intelektualnego.

### `issue:aq-13` Tokeny providerów i cykl życia rejestracji

- Doprecyzować zasady rotacji `write_token`.
- Opisać odzyskiwanie dostępu po utracie tokenu.
- Rozdzielić środowisko testowe, lokalne i publiczne.

### `issue:aq-14` Snapshot wiedzy z bazy operacyjnej

- Rozszerzyć generator raportu o trendy, histogramy i zakresy ostrzegawcze.
- Dodać anonimizację wybranych pól przed publikacją raportów.
- Opracować zasady, które snapshoty trafiają do repozytorium.

### `issue:aq-15` Wdrożenie D1 dla wariantu Cloudflare

- Spiąć migracje, bindingi i instrukcję wdrożeniową dla pierwszego publicznego środowiska.
- Zweryfikować retencję i limity kosztowe dla ruchu społecznościowego.
- Udokumentować minimalny plan odzyskiwania po awarii.

### `issue:aq-16` Kuracja wiedzy z danych społecznościowych

- Zdefiniować, jak z obserwacji wielu providerów budować porównywalne przypadki.
- Opracować proces ręcznej lub półautomatycznej kuracji przypadków do repozytorium.
- Przygotować pierwszy wzorzec opisu przypadku dla stawu hodowlanego.

### `issue:aq-17` Ręczne odzyskiwanie dostępu providera

- Opracować bezpieczny proces organizacyjny dla utraty tokenu.
- Rozdzielić odzyskiwanie dla providerów społecznościowych, badawczych i partnerskich.
- Udokumentować, kto i na jakiej podstawie może odtworzyć dostęp.

### `issue:aq-18` Audyt stabilności identyfikatorów providerów

- Doprecyzować zasady nadawania `provider_id`.
- Ograniczyć kolizje nazw między społecznością i partnerami.
- Zaproponować konwencję nazewniczą dla stawów, węzłów i providera.

### `issue:aq-19` Narzędzie administracyjne dla maintainera

- Rozwinąć `api/admin_provider_access.py` o dodatkowe operacje diagnostyczne.
- Dodać bezpieczny tryb eksportu statusów bez sekretów.
- Przygotować minimalny workflow dla lokalnej bazy i wariantu edge/cloud.

### `issue:aq-20` Runbook i kanał incydentowy dla utraty dostępu

- Doprecyzować, jak weryfikować tożsamość providera bez publikowania sekretów.
- Spiąć szablon GitHub Issue z runbookiem maintainera.
- Zostawić jasny proces dla społecznościowych węzłów i partnerów zewnętrznych.

### `issue:aq-21` Pierwszy publiczny deployment Cloudflare + D1

- Uzupełnić realne `database_id` i `preview_database_id`.
- Wykonać pierwsze zdalne migracje i deployment Worker'a.
- Zostawić notatkę operatorską z wynikiem deploymentu.

### `issue:aq-22` Smoke test publicznego API

- Utrzymywać `cloudflare/provider_smoke_test.py` jako standard po deploymencie.
- Dodać wynik smoke testu do procesu odbioru środowiska.
- Nie wpuszczać realnych providerów bez pełnego przejścia testu.

### `issue:aq-23` Rollback i gotowość operatorska

- Udokumentować minimalny proces rollbacku Worker'a.
- Określić, kto może wykonać rollback w środowisku publicznym.
- Dodać checklistę po rollbacku, w tym ponowny smoke test.

### `issue:aq-24` Wdrożenie konwencji provider_id w całym repo

- Utrzymywać wspólny format `kind-environment-slug-01`.
- Dopilnować zgodności sample data, testów, dokumentacji i onboardingów.
- Ograniczyć kolizje między środowiskami lokalnymi, demo i produkcyjnymi.

### `issue:aq-25` Konwencja nazw środowisk dla operatorów i providerów

- Spiąć nazwy środowisk `local`, `demo`, `preview`, `staging`, `prod` z praktyką deploymentu.
- Opisać, kiedy provider powinien zmienić identyfikator przy przejściu do innego środowiska.
- Przygotować checklistę migracji węzła z `demo` do `prod`.

### `issue:aq-26` Environment policy w API i Workerze

- Utrzymywać zgodność między `provider_id` a polityką środowiska deploymentu.
- Nie wpuszczać providerów `demo` do `prod`.
- Testować politykę środowisk na lokalnym API i w wariancie Cloudflare.

### `issue:aq-27` Profile deploymentu preview, staging i prod

- Doprecyzować domyślne `ALLOWED_PROVIDER_ENVIRONMENTS` dla każdego profilu.
- Spiąć profile z runbookiem wdrożeniowym.
- Zostawić operatorowi jasną checklistę, kiedy i jak przejść do `prod`.

### `issue:aq-28` Architektura dwóch onboardingów

- Rozdzielić onboarding Strażnika od onboardingu providera we wszystkich dokumentach i punktach wejścia.
- Utrzymać osobną narrację dla pierwszego zaangażowania społeczności i osobną dla integracji danych.
- Dopilnować, żeby nowa osoba nie trafiała od razu do technicznej dokumentacji API bez kontekstu.

### `issue:aq-29` Katalog rekomendatora zadań dla strony zewnętrznej

- Utrzymywać kanoniczny katalog tras wejścia dla zewnętrznej strony inicjatywy.
- Mapować pasje, kompetencje i zasoby Strażnika na konkretne sekcje repozytorium i pierwsze Issues.
- Zostawić format łatwy do wykorzystania przez repo strony `straz_landing`.

### `issue:aq-30` Issue template dla nowego Strażnika

- Przygotować prosty punkt wejścia dla osoby przekierowanej ze strony zewnętrznej.
- Zbierać pasje, kompetencje, zasoby i oczekiwania wobec pierwszego wkładu.
- Łączyć zgłoszenie z katalogiem rekomendacji i opieką społeczności.

### `issue:aq-31` Integracja ankiety z repo strony inicjatywy

- Spiąć repo strony z katalogiem rekomendatora zadań utrzymywanym w tym repozytorium.
- Zaprojektować przekierowania do właściwych projektów, dokumentów i szablonów Issue.
- Rozdzielić przekierowanie dla nowego Strażnika od przekierowania do ścieżki providera danych.

## Inspiracje i źródła:
- [Wideo: Smart Fish Farming](https://www.youtube.com/watch?v=N84PUuxThP4)
- [Projekt Open Source: IFishFarm (GitHub)](https://github.com/HussamElden/IFishFarm)

---
*Intelekt wyprzedza kapitał!*
