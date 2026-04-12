# Provider Template

Ten katalog jest wzorcem dla kolejnych integracji z providerami danych.

Każdy nowy adapter powinien implementować ten sam kontrakt:

```text
fetch_or_receive
normalize
validate
send_result
check_status
```

Zasady:

- adapter może znać natywny format providera,
- adapter nie może przenosić natywnego formatu do warstwy modeli,
- po `normalize()` payload musi być zgodny ze schematem `fish_pond_v1`,
- `send_result()` odsyła wynik analityczny, ale nie odpowiada za sterowanie urządzeniami,
- `check_status()` ma zwracać prosty, diagnostyczny stan połączenia i obsługiwanych możliwości.

## Trzy źródła referencyjne do adaptacji

Przy budowie kolejnych adapterów i węzłów pomiarowych warto analizować przede wszystkim trzy repozytoria:

- **KnowFlow_AWM**  
  [https://github.com/KnowFlow/KnowFlow_AWM](https://github.com/KnowFlow/KnowFlow_AWM)  
  Warto przejmować wzorce odczytu temperatury, pH i dissolved oxygen oraz modułowość firmware.

- **IoT-WQMS**  
  [https://github.com/pkErbynn/IoT-WQMS](https://github.com/pkErbynn/IoT-WQMS)  
  Warto przejmować wzorce przesyłania pomiarów, prostego backendu i toru od danych do alertu.

- **IoT-Water-Quality-Monitoring**  
  [https://github.com/JuliaSteiwer/IoT-Water-Quality-Monitoring](https://github.com/JuliaSteiwer/IoT-Water-Quality-Monitoring)  
  Warto przejmować wzorce pracy rozproszonej, energooszczędnej i terenowej.

## Zasada adaptacji

Przejmujemy:

- sterowniki i sposób odczytu,
- logikę kalibracji,
- wzorce buforowania i transportu danych,
- podejście do stabilnej pracy węzła terenowego.

Nie przejmujemy jako rdzenia:

- obcego modelu danych,
- obcego kontraktu API,
- obcego backendu jako formatu nadrzędnego całego systemu.

To adapter ma się dostosować do schematu Straży Przyszłości, a nie schemat Straży Przyszłości do przypadkowej struktury obcego repozytorium.
