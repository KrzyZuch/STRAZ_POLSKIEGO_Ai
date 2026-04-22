# Model Wolontariackich Notebookow Kaggle

## Cel dokumentu

Ten dokument opisuje model, w ktorym `Kaggle` jest traktowane jako **darmowy dostawca zasobow obliczeniowych uruchamianych przez wolontariuszy**, a nie jako centralna infrastruktura inicjatywy.

W tym modelu:

- Straż Przyszłości przygotowuje gotowe notebooki lub szkielety notebookow,
- lokalny agent wolontariusza prowadzi go przez uruchomienie,
- wolontariusz uruchamia notebook na swoim koncie `Kaggle`,
- notebook zuzywa jego darmowe limity i tokeny,
- wynik wraca do inicjatywy przez fork i `Pull Request`.

To jest praktyczny sposob na uruchamianie lancuchow automatyzacji bez centralnego budzetu na GPU i bez budowy drogiej infrastruktury.

## Najwazniejsze zalozenie

Kaggle nie jest tutaj "chmura inicjatywy". Kaggle jest **warstwa wykonawcza dostarczana dobrowolnie przez wolontariuszy**.

Czyli:

- inicjatywa dostarcza kontekst, notebook, prompt i kryteria odbioru,
- agent pomaga wolontariuszowi wykonac prace,
- wolontariusz decyduje, czy chce zuzyc swoje zasoby,
- wynik wraca do wspolnego repozytorium dopiero po review.

## Kanoniczny przebieg

```text
repo -> execution pack -> notebook Kaggle -> fork wolontariusza -> commit -> PR -> review -> merge
```

Praktycznie:

1. repo publikuje `KaggleNotebookPack`,
2. agent wolontariusza czyta pack i instruuje go krok po kroku,
3. wolontariusz importuje notebook do `Kaggle`,
4. ustawia wymagane `Kaggle Secrets`,
5. uruchamia notebook na swoim koncie,
6. notebook generuje artefakty,
7. artefakty trafiaja do forka wolontariusza,
8. z forka powstaje `PR` do glownego repo.

## Kaggle jako dostawca zasobow dla lancuchow automatyzacji

Wazne jest myslenie nie o pojedynczym notebooku, ale o **lancuchach automatyzacji**, ktore da sie uruchamiac przez notebooki na roznych kontach wolontariuszy.

Przyklad:

```text
chain discovery -> chain verification -> chain enrichment -> chain curation -> chain export
```

Kazdy etap moze miec osobny notebook albo osobny tryb notebooka:

- `discovery`: wyszukiwanie kandydatow i materialow zrodlowych,
- `verification`: OCR, frame check, cross-check i scoring,
- `enrichment`: datasheety, parametry, aliasy, kategorie,
- `curation`: przygotowanie kandydatow do kolejki review,
- `export`: przebudowa artefaktow i przygotowanie danych do downstream.

W ten sposob `Kaggle` staje sie darmowym dostawca zasobow dla wolontariackiej siatki wykonawczej, a nie tylko miejscem pojedynczych eksperymentow.

## Standard `KaggleNotebookPack`

Kazdy pack powinien zawierac:

- `goal`: co notebook ma osiagnac,
- `scope`: jaki fragment lancucha automatyzacji uruchamia,
- `input_context`: jakie dane, README i zrodla RAG sa potrzebne,
- `required_secrets`: jakie sekrety wolontariusz musi ustawic,
- `resource_cost_hint`: orientacyjny koszt czasu i limitow,
- `expected_outputs`: jakie pliki lub rekordy maja powstac,
- `fork_target`: gdzie wynik ma zostac zapisany,
- `pr_template`: jak opisac wynik w `PR`,
- `acceptance_criteria`: co musi przejsc, zeby wynik nadawal sie do review.

## Rola lokalnego agenta wolontariusza

Lokalny agent powinien:

- wyjasnic wolontariuszowi sens uruchomienia notebooka,
- sprawdzic, czy pack jest zgodny z jego zainteresowaniami i zasobami,
- poprowadzic go przez ustawienie sekretow,
- przypomniec, jakie artefakty maja powstac,
- pomoc uporzadkowac wynik do forka i `PR`,
- pilnowac, zeby wolontariusz nie wykonywal niejasnych krokow poza zakresem packa.

To jest bardzo wazne: agent nie tylko "pisze kod", ale jest tez **operatorem pracy wolontariusza**.

## Najbardziej naturalne zastosowania w Project 13

W `Project 13` ten model najlepiej pasuje do:

- huntingu filmow i kandydatow donor devices,
- generowania timestampow i kandydatow parts,
- OCR i HQ frame verification,
- batchowego wyszukiwania datasheetow,
- generowania kandydatow do kolejki kuracji,
- porownywania promptow i workflowow na tej samej probce danych.

Pierwszym naturalnym punktem startu jest:

- [youtube-databaseparts.ipynb](../youtube-databaseparts.ipynb)

Docelowo powinny z niego wynikac mniejsze, bardziej wyspecjalizowane notebooki dla osobnych etapow lancucha.

## Co notebook powinien robic z wynikami

Notebook nie powinien w ciemno promowac danych do glownego repozytorium.

Powinien:

- zapisac wynik do artefaktow roboczych,
- przygotowac czytelny output dla review,
- zapisac dane do forka wolontariusza,
- pozostawic slady wykonania: log, licznik przetworzonych rekordow, status, timestamp,
- dopiero potem umozliwic przygotowanie `PR`.

Preferowana kolejnosc to:

```text
artifact -> fork -> commit -> PR -> review -> merge
```

## Zasady bezpieczenstwa

Model musi pozostac jawnie dobrowolny i bezpieczny:

- wolontariusz sam decyduje, czy chce wykorzystac swoje darmowe limity `Kaggle`,
- sekrety sa ustawiane tylko na jego koncie jako `Kaggle Secrets`,
- repozytorium nie przechowuje prywatnych kluczy wolontariusza,
- notebook ma miec minimalny potrzebny zakres uprawnien,
- preferowany jest zapis do forka wolontariusza, nie do upstream,
- `PR` powinien zawierac opis przebiegu, artefakty i ograniczenia wyniku.

## Kryteria sukcesu

Model dziala poprawnie, gdy:

- wolontariusz z lokalnym agentem potrafi uruchomic notebook bez chaosu,
- inicjatywa dostaje z tego uporzadkowany `PR`, a nie przypadkowe pliki,
- koszt obliczen jest ponoszony dobrowolnie przez wolontariusza,
- wyniki sa reviewowalne i porownywalne,
- lancuchy automatyzacji da sie uruchamiac wielokrotnie na roznych kontach bez zmiany logiki procesu.

Najwazniejsze jest to, ze w tym modelu **darmowe zasoby Kaggle i praca wolontariusza zamieniaja sie w powtarzalny, agentowo wspierany wkład do wspolnej bazy wiedzy**.
