# Polityka Partnerska

## Cel dokumentu

Ten dokument określa zasady współpracy Straży Przyszłości z partnerami zewnętrznymi, providerami danych oraz członkami społeczności. Celem jest umożliwienie realnej współpracy bez utraty kontroli nad dorobkiem intelektualnym, standardem integracyjnym i marką inicjatywy.

## Role w ekosystemie

### Partner strategiczny

Podmiot, który wnosi istotny zasób wspierający rozwój inicjatywy, np. dostęp do danych, infrastruktury, środowiska pilotażowego, wiedzy domenowej lub kanału wdrożeniowego.

### Provider danych

Każdy podmiot lub osoba, która potrafi dostarczać dane do wspólnego schematu API i odbierać wyniki analityczne. Providerem może być zarówno firma, jak i gospodarstwo, członek społeczności, zespół badawczy czy węzeł pomiarowy oparty o stary smartfon.

### Współtwórca repozytorium

Osoba lub zespół rozwijający dokumentację, schematy, adaptery, modele, testy, dane przykładowe lub opis przypadków użycia.

## Zasady ogólne

1. Współpraca z partnerem nie daje partnerowi kontroli nad repozytorium ani kierunkiem rozwoju inicjatywy.
2. Żaden partner nie uzyskuje prawa wyłączności do wspólnego schematu, dokumentacji ani warstwy referencyjnej.
3. Repozytorium pozostaje wielodostawcowe. Każda integracja musi być budowana tak, aby możliwe było późniejsze podłączenie innych providerów.
4. Partner może korzystać z publicznego standardu i dokumentacji, ale nie przejmuje marki ani autorstwa inicjatywy.
5. Współpraca ma wzmacniać wspólną bazę wiedzy NSI, a nie zamykać ją w pojedynczym wdrożeniu.

## Granica między warstwą publiczną a prywatną

Do warstwy publicznej należą:

- dokumentacja strategii i współpracy,
- publiczny schemat danych,
- publiczny kontrakt API,
- adaptery referencyjne, szablony i tryb `mock`,
- modele referencyjne,
- dane przykładowe,
- opisy przypadków użycia i wnioski analityczne.

Do warstwy prywatnej mogą należeć:

- dane poufne lub wrażliwe partnera,
- sekrety, tokeny, klucze i konfiguracje produkcyjne,
- szczegóły komercyjnego wdrożenia,
- ustalenia biznesowe i SLA,
- niepubliczne środowiska operacyjne.

## Zasady własności i kontroli

1. Partner nie przejmuje wcześniejszego dorobku repozytorium.
2. Wniesienie danych, konsultacji lub środowiska pilotażowego nie oznacza przejęcia kontroli nad standardem integracyjnym.
3. Zmiany w publicznym schemacie i dokumentacji są oceniane pod kątem dobra całego ekosystemu, a nie wygody jednego partnera.
4. Każdy adapter partnera powinien być projektowany tak, aby izolować jego format od wspólnej warstwy logiki.
5. Wycofanie partnera nie może unieważniać prawa społeczności do dalszego rozwijania schematu, modeli i dokumentacji.

## Zasady dotyczące danych i wyników

1. Dane dostarczane przez providerów mają służyć budowie wspólnej bazy wiedzy, walidacji modeli i dokumentowaniu realnych przypadków użycia.
2. Wyniki zwracane przez system mają charakter analityczny, rekomendacyjny i dokumentacyjny.
3. Repozytorium Straży Przyszłości nie jest systemem zdalnego sterowania cudzymi urządzeniami i nie powinno być tak prezentowane.
4. Jeśli partner lub provider wykorzystuje wyniki lokalnie w swoim środowisku, odpowiedzialność za warstwę wykonawczą pozostaje po jego stronie.
5. Surowe, bieżące odczyty providerów nie powinny być składowane bezpośrednio w repozytorium. Powinny być przyjmowane przez działający serwer i bazę operacyjną, a do repozytorium trafiają jedynie dane przykładowe, opracowane lub anonimizowane.

## Zasady komunikacji i widoczności partnerów

1. Partner może być publicznie wymieniany jako provider, partner pilotażowy lub współpracujący podmiot, jeżeli strony na to pozwalają.
2. Komunikacja nie może sugerować, że partner jest właścicielem inicjatywy, repozytorium lub marki.
3. Providerzy ze społeczności mają prawo do uznania ich wkładu na tych samych zasadach co partnerzy instytucjonalni.
4. Integracja z jednym podmiotem nie może zamykać możliwości integracji z innymi.

## Minimalne oczekiwania wobec partnera lub providera

- gotowość do mapowania danych na wspólny schemat,
- poszanowanie zasad wielodostawcowości,
- brak prób wymuszania zamknięcia publicznego standardu,
- jasne określenie granicy między danymi publicznymi a prywatnymi,
- poszanowanie nazwy, marki i reguł komunikacyjnych Straży Przyszłości.

## Zakończenie współpracy

Współpraca z partnerem może się zakończyć bez wpływu na dalszy rozwój repozytorium. Standard, dokumentacja, modele i adaptery referencyjne pozostają częścią wspólnego dorobku inicjatywy, o ile nie zawierają cudzych tajemnic lub danych, które miały być prywatne.
