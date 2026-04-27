# Bench Test Report: recovered-esp-devkitc-v4-01

## Metryka

- Data testu: [DO_UZUPELNIENIA]
- board_id: `recovered-esp-devkitc-v4-01`
- board_variant: `ESP32-WROOM-32D`
- flash_method: `USB-CDC (onboard CP2102)`
- Tester: [DO_UZUPELNIENIA — osoba albo automated]

## Wyniki

| Test ID | Test | Kategoria | Status | Wartosc zmierzona | Wartosc oczekiwana | Delta |
|---------|------|-----------|--------|-------------------|-------------------|-------|
| BT-PWR-01 | Pomiar napiecia wejsciowego vs input_voltage | real_hardware | PENDING | | | |
| BT-PWR-02 | Pomiar napiecia roboczego MCU vs operating_voltage | real_hardware | PENDING | | | |
| BT-PWR-03 | Pomiar pradu idle vs power_consumption_idle | real_hardware | PENDING | | | |
| BT-PWR-04 | Pomiar pradu Wi-Fi TX vs power_consumption_wifi_tx | real_hardware | PENDING | | | |
| BT-PWR-05 | Stabilnosc zasilania pod obciazeniem | real_hardware | PENDING | | | |
| BT-FLS-01 | Flash firmware przez zadeklarowana metode | real_hardware | PENDING | | | |
| BT-FLS-02 | Wejscie w download mode przez boot_mode_entry | real_hardware | PENDING | | | |
| BT-FLS-03 | Recovery po brick | real_hardware | PENDING | | | |
| BT-FLS-04 | Backup oryginalnego firmware istnieje lub NIE DOTYCZY | either | [DO_UZUPELNIENIA] | | | |
| BT-GPIO-01 | Piny free odpowiadaja na toggle | real_hardware | PENDING | | | |
| BT-GPIO-02 | Piny damaged wykluczone z pin map | either | [DO_UZUPELNIENIA] | | | |
| BT-GPIO-03 | ADC1 odczyt z napiecia referencyjnego | real_hardware | PENDING | | | |
| BT-GPIO-04 | I2C scan — wykrycie slave | real_hardware | PENDING | | | |
| BT-GPIO-05 | UART0 komunikacja serial | real_hardware | PENDING | | | |
| BT-NET-01 | Wi-Fi scan — plytka widzi sieci 2.4GHz | real_hardware | PENDING | | | |
| BT-NET-02 | Wi-Fi connect do testowego AP | real_hardware | PENDING | | | |
| BT-NET-03 | MQTT publish do testowego broker | real_hardware | PENDING | | | |
| BT-NET-04 | Antena — jakosc sygnalu (RSSI) | real_hardware | PENDING | | | |
| BT-STO-01 | Rozmiar flash vs flash_size z board profile | real_hardware | PENDING | | | |
| BT-STO-02 | Odczyt tabeli partycji | real_hardware | PENDING | | | |

## Podsumowanie

- PASS: 0
- FAIL: 0
- PENDING: 18
- SKIP: 0
- NOT_APPLICABLE: 0

## Werdykt

- [ ] Runtime bundle moze byc promowany (wszystkie real_hardware = PASS albo NOT_APPLICABLE)
- [x] Runtime bundle NIE MOZE byc promowany (istnieje PENDING na real_hardware — brak fizycznej plytki albo brak wynikow)

> **UWAGA**: To jest template wygenerowany przez simulated precheck. Wszystkie testy `real_hardware`
> sa PENDING dopoki nie zostana wykonane na fizycznej plytce ESP32. Symulacja NIE zastepuje
> realnego bench testu. Patrz: `docs/BENCH_TEST_CONTRACT_ESP_RUNTIME_01.md`
> i `docs/SIMULATION_VS_REAL_HARDWARE_POLICY_ESP_RUNTIME_01.md`.
