# Product Requirements Document (PRD): Gemini RAG Manager

## 1. Wprowadzenie
Aplikacja "Gemini RAG Manager" to wewnętrzne narzędzie umożliwiające tworzenie tematycznych baz wiedzy (Stores) opartych na plikach, które są przetwarzane przez Google Gemini File Search API. Użytkownik może zarządzać grupami plików i prowadzić konwersacje z agentem AI, który posiada kontekst wyłącznie z wybranego Store'a, wykorzystując semantyczne wyszukiwanie.

## 2. Problem Statement
Użytkownicy potrzebują sposobu na logiczne grupowanie dokumentów (np. "Dokumentacja HR", "Projekt X") i zadawanie pytań modelowi Gemini w oparciu o te konkretne zbiory, bez konieczności ręcznego dołączania plików przy każdym zapytaniu. System powinien automatycznie wykorzystywać semantic search do znalezienia najbardziej relevantnych fragmentów dokumentów.

## 3. Wymagania Techniczne i Stos Technologiczny
*   **Backend:** Python 3.11+, FastAPI, Pydantic.
*   **Frontend:** React (Vite), Tailwind CSS, Shadcn/UI (opcjonalnie), Axios.
*   **Baza Danych:** SQLite (przechowywanie mappingów `display_name` ↔ `google_store_name` oraz metadanych dokumentów).
*   **AI/LLM:** Google Gemini API with FileSearchStore (via `google-genai` SDK v0.3.0+).
*   **Model:** Domyślnie używamy `gemini-2.5-flash` lub `gemini-2.5-pro` (wspierają File Search).
*   **Embedding:** Automatyczne embeddingi przez `gemini-embedding-001` (zarządzane przez Google).
*   **Bezpieczeństwo:** Klucz API przechowywany w `.env`. Aplikacja działa w sieci wewnętrznej.

## 4. User Stories i Kryteria Akceptacji

### US1: Zarządzanie Store'ami (Bazy Wiedzy)
**Jako** użytkownik, **chcę** tworzyć, usuwać i wybierać "Store" (grupę plików), **aby** móc organizować dokumenty tematycznie.

**Ważne:** Store'y są tworzone jako Google FileSearchStore, co oznacza:
- Przechowywane po stronie Google (nie lokalnie)
- Wymagają globalnie unikalnej nazwy (strategia: `store_{timestamp}_{sanitized_display_name}`)
- Aplikacja mapuje lokalny `display_name` → `google_store_name`

*   **Kryteria Akceptacji:**
    *   [Pozytywny] Użytkownik podaje `display_name`, backend tworzy FileSearchStore w Google z unikalną nazwą i zapisuje mapowanie w SQLite. Store pojawia się na liście wyboru.
    *   [Negatywny] Próba utworzenia Store'a o `display_name`, która już istnieje *lokalnie*, zwraca komunikat błędu "Nazwa musi być unikalna".
    *   [Brzegowy] Usunięcie Store'a usuwa zarówno lokalny rekord jak i FileSearchStore w Google Cloud (z opcją `force: true`).

### US2: Upload i Zarządzanie Plikami w Store
**Jako** użytkownik, **chcę** wgrać plik (PDF, TXT, CSV, itp.) do wybranego Store'a, **aby** agent miał do niego dostęp.

*   **Kryteria Akceptacji:**
    *   [Pozytywny] Użytkownik wybiera plik z dysku, backend wywołuje `upload_to_file_search_store()` API, które:
        1. Uploaduje plik do Google
        2. Automatycznie chunkuje dokument
        3. Tworzy embeddingi (gemini-embedding-001)
        4. Indeksuje w FileSearchStore
        
        Backend zapisuje w SQLite: `document_id`, `display_name`, `store_id`, `status` ("IMPORTING" → "COMPLETED").
    *   [Negatywny] Próba wgrania pliku w formacie nieobsługiwanym przez File Search kończy się błędem walidacji.
        
        **Obsługiwane typy:**
        - **Dokumenty:** PDF, DOCX, PPTX, XLSX, ODT
        - **Tekst:** TXT, MD, CSV, TSV, RTF, HTML
        - **Kod:** Python, JavaScript, Java, C++, JSON, XML, YAML i wiele innych
        - **Kompresja:** ZIP (automatycznie rozpakowane)
        
        Pełna lista: https://ai.google.dev/gemini-api/docs/file-search#supported-file-types
    *   [Brzegowy] Wgranie pliku powyżej limitu wielkości API zwraca odpowiedni komunikat błędu z API Google.

### US3: Podgląd zawartości Store
**Jako** użytkownik, **chcę** widzieć listę plików przypisanych do wybranego Store'a, **aby** wiedzieć, co znajduje się w kontekście.

*   **Kryteria Akceptacji:**
    *   [Pozytywny] Po wybraniu Store'a z listy rozwijanej, wyświetla się tabela z nazwami plików, datą dodania i statusem (np. "COMPLETED", "IMPORTING").
    *   [Negatywny] Jeśli Store jest pusty, wyświetla się komunikat "Brak plików w tym Store".
    *   [Brzegowy] Jeśli dokument został usunięty z FileSearchStore, aplikacja oznacza go jako "Niedostępny" przy próbie odświeżenia statusu.

### US4: Czat z Agentem (Kontekstowy)
**Jako** użytkownik, **chcę** zadać pytanie agentowi w kontekście wybranego Store'a, **aby** uzyskać odpowiedź opartą na zgromadzonych dokumentach.

**Semantic Search:** Zapytania są przetwarzane przez semantic search (nie keyword matching). Model otrzymuje automatycznie najbardziej relevantne chunki dokumentów z FileSearchStore oraz **cytowania** źródeł w odpowiedzi.

*   **Kryteria Akceptacji:**
    *   [Pozytywny] Użytkownik wybiera Store, wpisuje pytanie. Backend używa `FileSearch` tool w `generate_content()` call, przekazując `file_search_store_names`. Model zwraca odpowiedź z cytatami ze źródeł.
    *   [Negatywny] Próba zadania pytania bez wybrania Store'a zwraca "Wybierz Store przed zadaniem pytania".
    *   [Brzegowy] Jeśli Store jest pusty (brak dokumentów), zwraca "Dodaj pliki do Store'a przed konwersacją".
    *   [Pozytywny] Odpowiedzi zawierają cytowania z nazwami dokumentów, które zostały użyte.

## 4.5. Architektura Google File Search

Aplikacja korzysta z Google File Search API, które zapewnia:

### Automatyczny Workflow

1. **Upload + Import**: Plik jest wysyłany i automatycznie przetwarzany:
   - Chunking dokumentu na mniejsze fragmenty
   - Tworzenie embeddingów (gemini-embedding-001)
   - Indeksowanie w specjalizowanej bazie wektorowej

2. **Semantic Search**: Podczas zapytania:
   - Pytanie użytkownika jest konwertowane na embedding
   - System wyszukuje najbardziej podobne chunki semantycznie
   - Relevantne fragmenty są dostarczane jako kontekst do modelu

3. **Generowanie Odpowiedzi**:
   - Model (gemini-2.5-flash/pro) otrzymuje kontekst z File Search
   - Generuje odpowiedź opartą na znalezionych dokumentach
   - Zwraca cytowania źródeł

### Persistence

- **FileSearchStore**: Dane są przechowywane nieskończenie długo (brak TTL)
- **Temporary File Objects**: Usuwane po 48h (nie potrzebne po imporcie)
- **Embeddings**: Zarządzane i optymalizowane przez Google

### Diagram

```
                    ┌─────────────┐
                    │   Backend   │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
    ┌─────────┐   ┌──────────────────┐   ┌────────────┐
    │ SQLite  │   │ Google Cloud     │   │   Gemini   │
    │         │   │ FileSearchStore  │   │   Model    │
    │Mappings │   │                  │   │ (2.5-flash)│
    └─────────┘   │ - Chunking       │   └────────────┘
                  │ - Embeddings     │
                  │ - Vector Index   │
                  │ - Documents      │
                  └──────────────────┘
```

## 5. Logika Biznesowa i Ograniczenia

### Architektura Warstw

Aplikacja działa jako **warstwa interfejsu użytkownika** nad Google FileSearchStore API:

```
[UI] → [Backend API] → [SQLite Mappings] → [Google FileSearchStore API]
                              ↓
                    Local: display_name, UI state
                              ↓
                    Google: documents, embeddings, search
```

### Mapowanie Danych

**W SQLite przechowujemy:**
- `id`: Lokalny ID Store'a
- `display_name`: Nazwa wyświetlana użytkownikowi (unikalna lokalnie)
- `google_store_name`: Nazwa FileSearchStore w Google (np. "fileSearchStores/abc-123")
- `created_at`, `updated_at`: Timestampy

**Dla plików w SQLite:**
- `id`: Lokalny ID pliku
- `store_id`: Foreign key do Store
- `document_id`: ID dokumentu w FileSearchStore
- `display_name`: Nazwa pliku dla użytkownika
- `upload_date`: Data uploadu
- `status`: Stan importu ("IMPORTING", "COMPLETED", "FAILED")

### Strategia Nazewnictwa Store'ów

**Problem:** Nazwy FileSearchStore są **globalnie unikalne** (nie per-user).

**Rozwiązanie:**
```python
google_store_name = f"store_{timestamp}_{sanitized_display_name}"
# Przykład: "store_1732561234_dokumentacja_hr"
```

### API Calls

**Tworzenie Store:**
```python
file_search_store = client.file_search_stores.create(
    config={'display_name': user_provided_name}
)
# Zwraca: google_store_name (np. "fileSearchStores/abc-123")
```

**Upload pliku:**
```python
operation = client.file_search_stores.upload_to_file_search_store(
    file=uploaded_file,
    file_search_store_name=store.google_store_name,
    config={'display_name': filename}
)
# Monitoruj operation.done, potem operation.metadata zawiera document_id
```

**Zapytanie z File Search:**
```python
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=user_question,
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[store.google_store_name]
                )
            )
        ]
    )
)
```

### Ograniczenia i Rate Limits

- **File Search store limit**: Sprawdź dokumentację (może być ograniczenie na liczbę store'ów)
- **Document size**: Zależne od planu API  
- **Chunking**: Automatyczne, zarządzane przez Google (brak kontroli nad wielkością chunków bez custom config)

## 6. Bezpieczeństwo (OWASP)

*   **Walidacja rozszerzeń plików:** Whitelist obsługiwanych typów zgodnie z File Search API.
    - Backend weryfikuje MIME type przed wysłaniem
    - Typy bezpieczne: PDF, DOCX, TXT, MD, CSV, TSV, JSON, XML, ZIP i inne z oficjalnej listy
    
*   **Sanityzacja nazw Store'ów:**
    - Walidacja `display_name` (regex, max length)
    - Generowanie bezpiecznego `google_store_name` (bez specjalnych znaków)
    - Zapobieganie SQL Injection (SQLAlchemy ORM + parametryzowane zapytania)
    
*   **Obsługa błędów API:**
    - Nie zwracać pełnych stack trace'ów do UI
    - Logować szczegóły błędów server-side
    - Zwracać użytkownikowi zrozumiałe komunikaty po polsku
    
*   **Rate Limiting:**
    - Monitorować limity Google API
    - Implementować rate limiting na backendzie (opcjonalnie)
    
*   **Klucz API:**
    - Przechowywany w `.env` (gitignored)
    - Nigdy nie wysyłany do frontendu
    - Tylko backend komunikuje się z Google API
    
*   **Walidacja operacji:**
    - Sprawdzać `operation.done` przed uznaniem uploadu za zakończony
    - Obsługiwać timeouty i retries dla długich operacji