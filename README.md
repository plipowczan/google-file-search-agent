# Gemini RAG Manager

Aplikacja do zarządzania bazami wiedzy (Stores) i prowadzenia konwersacji z Google Gemini AI w oparciu o zgrupowane dokumenty.

## Struktura Projektu

```
gemini-rag-manager/
├── backend/          # Python FastAPI backend
│   ├── app/         # Kod aplikacji
│   ├── requirements.txt
│   └── README.md    # Szczegółowa dokumentacja backendu
├── frontend/         # React frontend (do wdrożenia)
└── PRD.md           # Product Requirements Document
```

## Quick Start

### Backend

Przejdź do katalogu `backend/` i postępuj zgodnie z instrukcjami w [backend/README.md](backend/README.md).

```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
cp .env.example .env  # Dodaj swój GOOGLE_API_KEY
uvicorn app.main:app --reload
```

API będzie dostępne pod: `http://localhost:8000`
Dokumentacja: `http://localhost:8000/docs`

### Frontend

Wkrótce...

## Funkcjonalności

### ✅ US1: Zarządzanie Store'ami
- Tworzenie nowych Store'ów (baz wiedzy)
- Lista wszystkich Store'ów
- Usuwanie Store'ów
- Walidacja unikalności nazw

### 🚧 US2: Upload i Zarządzanie Plikami (TODO)
### 🚧 US3: Podgląd zawartości Store (TODO)
### 🚧 US4: Czat z Agentem (TODO)

## Technologie

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, Google Gemini AI SDK
- **Frontend**: React, Vite, Tailwind CSS (planowane)
- **Baza Danych**: SQLite

## Dokumentacja

- [PRD.md](PRD.md) - Product Requirements Document
- [backend/README.md](backend/README.md) - Dokumentacja backendu
