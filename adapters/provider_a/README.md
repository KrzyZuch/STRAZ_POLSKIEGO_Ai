# Provider A

Ten katalog pokazuje przykładową integrację z pierwszym providerem zewnętrznym bez naruszania kontraktu publicznego repozytorium.

Założenia demonstracyjne:

- `provider-a` ma własny, natywny format pól,
- adapter mapuje ten format do wspólnego schematu `fish_pond_v1`,
- model rekomendacyjny nie zna formatu providera,
- wynik może wrócić do providera w jego własnej kopercie integracyjnej.

Ten adapter jest przykładem zasady: provider jest wymienialny, a centrum architektury pozostaje po stronie Straży Przyszłości.
