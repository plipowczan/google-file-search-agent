# Gemini RAG Manager - Backend

Backend API dla aplikacji Gemini RAG Manager - narzędzia do zarządzania bazami wiedzy (Stores) i prowadzenia konwersacji z Google Gemini AI.

## Wymagania

- Python 3.11+
- Google Gemini API Key

## Instalacja i Konfiguracja

### 1. Utwórz środowisko wirtualne

```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Zainstaluj zależności

```bash
pip install -r requirements.txt
```

### 3. Konfiguracja zmiennych środowiskowych

Skopiuj plik `.env.example` do `.env`:

```bash
cp .env.example .env
```

Edytuj plik `.env` i dodaj swój klucz API Google Gemini:

```env
GOOGLE_API_KEY=your_actual_api_key_here
DATABASE_URL=sqlite:///./gemini_rag.db
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True
```

### 4. Uruchom serwer

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Serwer będzie dostępny pod adresem: `http://localhost:8000`

## Dokumentacja API

Po uruchomieniu serwera, dokumentacja API jest dostępna pod:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Struktura Projektu

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Główna aplikacja FastAPI
│   ├── database/
│   │   ├── __init__.py
│   │   └── database.py      # Konfiguracja SQLAlchemy
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py        # Modele bazy danych (Store, File)
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── store_schemas.py # Schematy Pydantic
│   ├── routes/
│   │   ├── __init__.py
│   │   └── stores.py        # Endpointy dla Store'ów
│   └── services/
│       └── __init__.py      # Logika biznesowa (future)
├── .env.example             # Przykładowa konfiguracja
├── .gitignore
└── requirements.txt         # Zależności Python
```

## Endpointy API (US1 - Zarządzanie Store'ami)

### Utworzenie nowego Store'a

```http
POST /stores/
Content-Type: application/json

{
  "name": "Dokumentacja HR"
}
```

**Odpowiedź (201 Created):**
```json
{
  "id": 1,
  "name": "Dokumentacja HR",
  "created_at": "2025-11-25T19:40:00",
  "updated_at": "2025-11-25T19:40:00"
}
```

**Błąd (409 Conflict)** - nazwa już istnieje:
```json
{
  "detail": "Nazwa musi być unikalna"
}
```

### Lista wszystkich Store'ów

```http
GET /stores/
```

**Odpowiedź (200 OK):**
```json
{
  "stores": [
    {
      "id": 1,
      "name": "Dokumentacja HR",
      "created_at": "2025-11-25T19:40:00",
      "updated_at": "2025-11-25T19:40:00"
    }
  ],
  "total": 1
}
```

### Pobranie konkretnego Store'a

```http
GET /stores/{store_id}
```

### Usunięcie Store'a

```http
DELETE /stores/{store_id}
```

**Odpowiedź (204 No Content)** - Store usunięty pomyślnie

## Bezpieczeństwo

- **Walidacja nazw Store'ów**: Automatyczna sanityzacja zapobiegająca SQL Injection
- **Obsługa błędów**: API nie zwraca pełnych stack trace'ów do klienta
- **Klucz API**: Przechowywany w pliku `.env` (nie commitowany do repo)

## Baza Danych

Aplikacja używa SQLite. Baza danych jest automatycznie tworzona przy pierwszym uruchomieniu serwera.

### Modele:

**Store** - Grupa plików (baza wiedzy)
- `id`: Integer (Primary Key)
- `name`: String (Unique, Not Null)
- `created_at`: DateTime
- `updated_at`: DateTime

**File** - Plik przypisany do Store'a (przygotowane na US2)
- `id`: Integer (Primary Key)
- `store_id`: Integer (Foreign Key)
- `google_file_uri`: String
- `google_file_name`: String
- `upload_date`: DateTime
- `status`: String (PROCESSING, ACTIVE, FAILED, UNAVAILABLE)

## Rozwój

### Health Check

```http
GET /
GET /health
```

Sprawdza, czy serwer działa prawidłowo.

## Następne Kroki (TODO)

- [ ] US2: Implementacja uploadu plików do Google Gemini API
- [ ] US3: Endpoint do listowania plików w Store
- [ ] US4: Integracja z Google Gemini do prowadzenia konwersacji
- [ ] Testy jednostkowe i integracyjne
