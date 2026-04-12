# Konwencja Provider ID i Środowisk

## Cel dokumentu

Ten dokument ustala prostą, wspólną konwencję nadawania `provider_id` w ekosystemie Straży Przyszłości.

Celem jest:

- unikanie kolizji nazw między społecznością, partnerami i środowiskami testowymi,
- łatwiejsza diagnostyka i administracja,
- spójność między lokalnym API, Cloudflare Workers, dokumentacją i bazą wiedzy.

## Format `provider_id`

Obowiązujący format:

```text
kind-environment-slug-01
```

Przykłady:

```text
community-demo-node-01
farm-prod-mazury-pond-01
research-preview-lab-vision-02
edge-local-gateway-01
company-staging-acme-bridge-01
```

## Znaczenie segmentów

### 1. `kind`

Pierwszy segment musi odpowiadać `provider_kind`:

- `company` dla `provider_kind=company`
- `farm` dla `provider_kind=farm`
- `community` dla `provider_kind=community`
- `research` dla `provider_kind=research`
- `edge` dla `provider_kind=edge_node`

### 2. `environment`

Drugi segment oznacza środowisko pracy providera.

Dozwolone wartości:

- `local`
- `demo`
- `preview`
- `staging`
- `prod`

To nie jest opis typu instytucji, tylko miejsca w cyklu wdrożeniowym i operacyjnym.

### 3. `slug`

Kolejne segmenty opisują providera, lokalizację, rolę węzła albo most integracyjny.

Zasady:

- tylko małe litery,
- cyfry są dozwolone,
- słowa rozdzielamy myślnikami,
- bez spacji, polskich znaków, podkreśleń i wielkich liter.

### 4. Sufiks numeryczny

Ostatni segment musi być numeryczny i mieć co najmniej dwie cyfry, np.:

- `01`
- `02`
- `15`
- `101`

Sufiks pozwala odróżnić kolejne węzły lub integracje w tej samej rodzinie nazw.

## Jak wybierać środowisko

- `local`:
  tylko lokalne eksperymenty developera lub maintainera
- `demo`:
  przykłady repozytoryjne, sample workflow, pokazowe węzły społecznościowe
- `preview`:
  środowiska testowe dostępne zdalnie, ale jeszcze nieprodukcyjne
- `staging`:
  środowiska przedprodukcyjne z bardziej realistyczną konfiguracją
- `prod`:
  środowiska rzeczywiste, gotowe do pracy z realnymi providerami i danymi operacyjnymi

## Zasady praktyczne

- nie używaj tego samego `provider_id` w dwóch różnych środowiskach,
- nie zmieniaj `provider_id` tylko po to, żeby obrócić token,
- nie próbuj odzyskiwać dostępu przez ponowną rejestrację istniejącego `provider_id`,
- jeśli tworzysz nowy węzeł społecznościowy, zacznij zwykle od `community-demo-...`,
- jeśli węzeł przechodzi do środowiska realnego, utwórz docelowy identyfikator `...-prod-...`.

## Relacja do `provider_label`

`provider_id` służy do integracji i diagnostyki.

`provider_label` służy do czytelnego opisu dla ludzi. Może być bardziej przyjazny i opisowy, np.:

- `Mazury Community Old Smartphone Gateway`
- `Acme Fish Farm Main Bridge`
- `Research Vision Node South Pond`

## Gdzie ta konwencja obowiązuje

- w rejestracji providera,
- w obserwacjach i zdarzeniach,
- w statusach providera,
- w odpowiedziach rekomendacyjnych,
- w testach i sample data repozytorium,
- w runbookach operatorskich.

## Polityka środowiska API

Samo poprawne `provider_id` nie wystarcza jeszcze do wejścia do systemu. Warstwa operacyjna może dodatkowo ograniczać, które environment są dopuszczone w danym deploymentcie.

Przykład:

- lokalne API może przyjmować `local,demo`,
- środowisko preview może przyjmować `demo,preview`,
- środowisko staging może przyjmować tylko `staging`,
- środowisko prod powinno przyjmować tylko `prod`.

To pozwala oddzielić publiczne demo od ruchu rzeczywistego i ograniczyć przypadkowe pomyłki operatorów.
