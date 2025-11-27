---
trigger: always_on
---

# Cursor Rules for Gemini RAG Manager Project

You are an expert Senior Python/React Developer specializing in AI integrations.

## Tech Stack & Preferences

- **Backend:** Python (FastAPI), Pydantic, SQLite (via SQLAlchemy or raw SQL depending on simplicity).
- **Frontend:** React (Vite), Tailwind CSS, Lucide React (icons).
- **AI SDK:** `google-genai` v0.3.0+ (Python) - używamy **File Search API**.
- **Architecture:** Google-Native FileSearchStore (semantic search, auto-chunking, embeddings).
- **Language:** Polish (for UI labels and comments), English (for variable names and code structure).

## Project Context

We are building an internal tool leveraging **Google File Search API**. Stores are actually
**FileSearchStore** objects in Google Cloud. Our backend maps user-friendly names to Google store names
and orchestrates file uploads with automatic chunking, embedding (gemini-embedding-001), and semantic search.
The source of truth for requirements is `PRD.md`.

## Coding Standards

### Python (Backend)

- Use `FastAPI` for the REST API.
- Use `pydantic` models for all request/response schemas.
- **CRITICAL:** When using `google-genai` File Search API:
  - Import: `from google import genai` oraz `from google.genai import types`
  - Initialize client: `client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))`
  - Use `client.file_search_stores.create()` to create stores (not local DB only)
  - Use `client.file_search_stores.upload_to_file_search_store()` for uploads
  - Always monitor operation with `operation.done` loop after upload (import takes time)
  - Store mapping: SQLite `display_name` ↔ Google `file_search_store_name` (e.g., "fileSearchStores/abc-123")
  - Use `FileSearch` tool in `generate_content()` config, passing `file_search_store_names`
  - Handle `google.api_core.exceptions` gracefully
  - **Models:** Use `gemini-2.5-flash` or `gemini-2.5-pro` (support File Search)
- Use Type Hints for all functions.
- Project structure:
  - `backend/app/main.py` (FastAPI app entry)
  - `backend/app/database/database.py` (SQLAlchemy setup)
  - `backend/app/models/models.py` (SQLAlchemy models: Store, File)
  - `backend/app/schemas/` (Pydantic request/response schemas)
  - `backend/app/routes/` (API endpoints)
  - `backend/app/services/google_file_search_service.py` (Google FileSearchStore API interactions)

### React (Frontend)

- Use Functional Components with Hooks.
- Use `axios` or `fetch` for API calls.
- **UI/UX:**
  - Create a sidebar or top bar for "Store Selection".
  - The main view should change based on selection: "File List" tab and "Chat" tab.
  - Show loading states (spinners) when uploading files to Google (it takes time).
- Use Tailwind CSS for styling.

## Workflow

1. Always read `PRD.md` before generating code to understand the specific User Story.
2. If a file upload fails, ensure the UI explains WHY (e.g., "File too large", "API Error").
3. Do not hallucinate API methods. Refer to File Search documentation:
   - `client.file_search_stores.create(config={...})`
   - `client.file_search_stores.upload_to_file_search_store(file, file_search_store_name, config)`
   - `client.models.generate_content(model, contents, config=types.GenerateContentConfig(tools=[...]))`
   - Documentation: <https://ai.google.dev/gemini-api/docs/file-search>

## File Search Specifics

### Store Creation Strategy

Stores have **globally unique names** in Google Cloud. Implement naming strategy:

```python
# User provides: display_name = "Dokumentacja HR"
# Backend generates: google_store_name = f"store_{int(time.time())}_{sanitize(display_name)}"
# Save both in SQLite for mapping
```

### Upload  Workflow

1. User uploads file → Backend
2. Backend calls `upload_to_file_search_store()`
3. Operation starts (returns `operation` object)
4. Loop: wait until `operation.done == True`
5. Extract `document_id` from `operation.metadata`
6. Save to SQLite: `document_id`, `display_name`, `store_id`, `status="COMPLETED"`

### Query with File Search

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
# response.text contains answer with citations
```

### Supported File Types

File Search supports extensive file types. Always validate on backend:

- Documents: PDF, DOCX, PPTX, XLSX, ODT
- Text: TXT, MD, CSV, TSV, HTML, RTF
- Code: PY, JS, JAVA, JSON, XML, YAML, etc.
- Archives: ZIP (auto-extracted)

Full list: <https://ai.google.dev/gemini-api/docs/file-search#supported-file-types>

## Security

- Never hardcode API Keys. Expect `GOOGLE_API_KEY` in `os.environ`.
- Validate file types on backend before sending to Google.