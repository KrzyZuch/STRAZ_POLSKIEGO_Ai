# 08. Autonomiczne Maszyny Rolnicze (OpenBot)

## **Intelekt wyprzedza Kapitał!**

## Opis Projektu
Wykorzystanie projektu **OpenBot** oraz zaawansowanych sterowników typu **Open-Source** do transformacji używanych smartfonów w zaawansowane mózgi dla autonomicznych systemów rolniczych. Projekt obejmuje zarówno jednostki mobilne (pielniki, siewniki), jak i stacjonarne systemy automatyzacji upraw (hydroponika, aeroponika).

## Dlaczego OpenBot?
OpenBot, opracowany przez zespół badawczy Intel, udowadnia, że moc obliczeniowa nowoczesnego smartfona jest w zupełności wystarczająca do obsługi zaawansowanych obciążeń robotycznych:
- **Nawigacja w czasie rzeczywistym:** Wykorzystanie AI do śledzenia ścieżek i omijania przeszkód.
- **Computer Vision:** Rozpoznawanie obiektów (np. odróżnianie chwastów od roślin uprawnych).
- **Niski koszt:** Wykorzystanie elektroniki, która już istnieje, zamiast kupowania drogich, dedykowanych komputerów przemysłowych.

## Automatyzacja Upraw: Hydroponika i Aeroponika

Smartfon jako sterownik Edge Computing idealnie nadaje się do zarządzania precyzyjnymi systemami upraw bezglebowych. Dzięki gotowym projektom we wspólnocie Open-Source, możemy wdrażać:
- **[Hydruino](https://github.com/NachtRaveVL/Simple-Hydroponics-Arduino):** Profesjonalny sterownik automatyzacji hydroponiki, obsługujący pompy, czujniki pH, EC i temperatury.
- **[HydroTek](https://github.com/tangles-0/HydroTek):** System IoT, który można zintegrować ze smartfonem jako lokalnym serwerem danych i interfejsem AI.
- **Monitorowanie AI:** Smartfon (kamera) analizuje stan liści i korzeni, wykrywając niedobory składników odżywczych szybciej niż standardowe czujniki.

## Architektura Systemu (Uniwersalność)
1. **Mózg (Smartfon):** Obsługuje stos OpenBot dla maszyn mobilnych LUB aplikację zarządzającą uprawami.
2. **Mostek (Arduino/ESP32):** Na bazie kodu z [Projektu 07 (PhoneUAV)](07_uniwersalna_platforma_sterowania.md) – komunikacja USB/Wi-Fi ze światem fizycznym.
3. **Efektor:** Silniki maszyn polowych LUB pompy i dozowniki w systemach hydroponicznych.

## Korzyści dla Inicjatywy
- **Skalowalność:** Technologia ta pozwala na budowę floty tanich robotów, które mogą pracować 24/7.
- **Otwartość:** Całość oparta na modelu Open-Source, co pozwala każdemu polskiemu rolnikowi na adaptację systemu do własnych potrzeb bez opłat licencyjnych.
- **Intelektualny Wkład:** Dokumentowanie procesu adaptacji OpenBot do warunków rolniczych (np. praca w pyle, zmienne oświetlenie) to kluczowa wartość naszego repozytorium.

## IV. Autonomiczne Maszyny Terenowe (Open Hardware)

Wdrażamy i adaptujemy najbardziej zaawansowane otwarte projekty mechaniczne, które stanowią uzupełnienie cyfrowego "mózgu" OpenBot:

*   **Acorn Precision Farming Rover (Twisted Fields):** Solarny, autonomiczny łazik terenowy. Precyzyjna platforma zorientowana na budowę i utrzymanie upraw bez paliw kopalnych.
    - *Repo:* [Twisted-Fields/acorn-precision-farming-rover](https://github.com/Twisted-Fields/acorn-precision-farming-rover)
    - *Mechanika:* [Twisted-Fields/acorn-mechanical-designs](https://github.com/Twisted-Fields/acorn-mechanical-designs)

---

### Zasoby techniczne:
- **Repozytorium OpenBot:** [https://github.com/ob-f/OpenBot](https://github.com/ob-f/OpenBot)
- **Oficjalna strona:** [www.openbot.org](https://www.openbot.org)
- **Acorn Precision Farming Rover (Twisted Fields):** Solarny, autonomiczny łazik terenowy. Precyzyjna platforma zorientowana na budowę i utrzymanie upraw bez paliw kopalnych.
    - *Repo:* [Twisted-Fields/acorn-precision-farming-rover](https://github.com/Twisted-Fields/acorn-precision-farming-rover)
    - *Mechanika:* [Twisted-Fields/acorn-mechanical-designs](https://github.com/Twisted-Fields/acorn-mechanical-designs)

---
*Intelekt wyprzedza Kapitał!*

**Nawet kod już jest, brakuje tylko Ciebie.**
