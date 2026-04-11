# 09. Monitoring IoT i Akcelerometria (Smart Health Tracker)

## **Intelekt wyprzedza Kapitał!**

## Opis Projektu
Projekt skupia się na wykorzystaniu sensorów wbudowanych w każdy smartfon (akcelerometr, żyroskop, magnetometr, GPS) oraz wysokiej jakości kamer do stworzenia taniego, inteligentnego systemu monitorowania zdrowia i bezpieczeństwa zwierząt gospodarskich (tzw. Smart Collar / Inteligentna Obroża).

Nawet 10-letni smartfon posiada czujniki o precyzji wystarczającej do wykrywania subtelnych zmian w zachowaniu zwierzęcia, które sygnalizują chorobę, ruję lub zbliżający się poród.

## Kluczowe Filary Technologiczne (Gotowy Kod)

### 1. Wizyjny Monitoring AI (Sentinel)
Zamiast budować system od zera, wykorzystujemy framework **Sentinel**, który zamienia telefony w bezobsługowe węzły kamer AI.
- **Funkcja:** Detekcja ruchu w oborze, monitoring porodówek, nadzór nad paszami.
- **Kod źródłowy:** [suzuran0y/CCTV-Smartphone-AI-Monitoring](https://github.com/suzuran0y/CCTV-Smartphone-AI-Monitoring)
- **Zaleta:** Automatyczne wykrywanie serwera w sieci LAN i obsługa strumieniowania wysokiej klasy.

### 2. Telemetria Sensorowa (Edge Analytics)
Wykorzystanie akcelerometru do analizy "dobrostanu" (welfare monitoring).
- **Funkcja:** Monitorowanie czasu przeżuwania, aktywności ruchowej i wykrywanie upadków.
- **Kod źródłowy:** [mqtt-sensor-android](https://github.com/dc297/mqtt-sensor-android) lub streamowanie przez **Node-RED**.
- **Logika:** Dane są przesyłane przez protokół MQTT do centralnego punktu (np. Raspberry Pi lub inny smartfon działający jako serwer), gdzie AI analizuje wzorce ruchu.

## Implementacja w Straży Przyszłości

### Etap 1: Obudowa i Zasilanie (Upcykling)
- Wykorzystanie wydrukowanych metodą 3D szczelnych obudów (IP67) montowanych na obrożach.
- Zasilanie z dużych ogniw Li-Ion odzyskanych z baterii laptopowych lub małych paneli solarnych.

### Etap 2: Komunikacja
- Wykorzystanie Wi-Fi (na terenie gospodarstwa) lub technologii LoRa (poprzez adaptery USB podłączone do smartfona) do przesyłania danych z pastwisk.

### Etap 3: Analiza AI (Model Narodowy)
- Budowa otwartej bazy danych wzorców ruchu (np. "charakterystyczne ruchy owcy przed porodem"), która pozwoli na szkolenie lokalnych modeli Edge AI.

## Dlaczego to jest przełomowe?
Komercyjne systemy monitorowania krów (np. elektroniczne kolczyki) kosztują tysiące złotych i są zamkniętymi ekosystemami. Nasze rozwiązanie oparte na **repurposed hardware** jest darmowe w warstwie licencyjnej i o rzędy wielkości tańsze sprzętowo, przy zachowaniu wyższej mocy obliczeniowej smartfona.

---
*Intelekt wyprzedza Kapitał!*
