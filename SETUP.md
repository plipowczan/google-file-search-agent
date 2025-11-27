# Setup Instructions - Gemini RAG Manager

## 1. Google Cloud Project Setup and API Key

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a project** → **New Project**
3. Enter project name (e.g., "gemini-rag-manager")
4. Click **Create**

### Step 2: Enable Gemini API

1. In the Google Cloud Console, navigate to **APIs & Services** → **Library**
2. Search for "Generative Language API" or "Gemini API"
3. Click on the API and press **Enable**

### Step 3: Create API Key

1. Navigate to **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **API Key**
3. Copy the generated API key immediately
4. (Optional but recommended) Click **Edit API key** to:
   - Restrict the key to "Generative Language API"
   - Add application restrictions (IP addresses, HTTP referrers, etc.)

### Step 4: Configure Billing (Required)

> **Important:** Gemini API requires a billing account to be enabled.

1. Navigate to **Billing** in the Google Cloud Console
2. Link a billing account to your project
3. Review the [Gemini API pricing](https://ai.google.dev/pricing)

### Step 5: Save API Key to `.env`

1. In the project root directory, create a `.env` file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API key:
   ```env
   GOOGLE_API_KEY=your_api_key_here
   DATABASE_URL=sqlite:///./gemini_rag.db
   ```

3. **Never commit `.env` to version control** (already in `.gitignore`)

---

## 2. Local Environment Setup

### Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: 18.x or higher (for frontend)
- **Git**: Latest version

### Step 1: Verify Python Installation

```bash
python --version
# Should output: Python 3.11.x or higher
```

If Python is not installed:
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **macOS**: `brew install python@3.11`
- **Linux**: `sudo apt install python3.11 python3.11-venv`

### Step 2: Verify Node.js Installation

```bash
node --version
# Should output: v18.x.x or higher
```

If Node.js is not installed:
- Download from [nodejs.org](https://nodejs.org/)
- Or use [nvm](https://github.com/nvm-sh/nvm) (recommended)

### Step 3: Clone Repository (if not already done)

```bash
git clone <repository-url>
cd google-file-search-agent
```

### Step 4: Backend Setup

1. **Create Python virtual environment:**
   ```bash
   cd backend
   python -m venv venv
   ```

2. **Activate virtual environment:**
   - **Windows (PowerShell):**
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **Windows (CMD):**
     ```cmd
     .\venv\Scripts\activate.bat
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Initialize database:**
   ```bash
   # Database will be created automatically on first run
   # Tables are created via SQLAlchemy on startup
   ```

### Step 5: Frontend Setup (Coming Soon)

Once the frontend is implemented:

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

---

## 3. Running the Application

### Backend Only (Current State)

1. **Ensure `.env` is configured** (see Step 5 of Google Cloud setup)

2. **Start the backend server:**
   ```bash
   cd backend
   # Activate venv if not already active
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

```json
{
  "status": "healthy",
  "service": "gemini-rag-manager",
  "database": "connected"
}
```

### Test 2: Create a Store

```bash
curl -X POST http://localhost:8000/stores/ \
  -H "Content-Type: application/json" \
  -d '{"display_name": "Test Store"}'
```

Expected response:
```json
{
  "id": 1,
  "display_name": "Test Store",
  "google_store_name": "fileSearchStores/...",
  "created_at": "2025-11-27T...",
  "updated_at": "2025-11-27T..."
}
```

### Test 3: List Stores

```bash
curl http://localhost:8000/stores/
```

---

## 5. Troubleshooting

### Issue: "GOOGLE_API_KEY not found"

**Solution:** Ensure `.env` file exists in the project root and contains:
```env
GOOGLE_API_KEY=your_actual_api_key
```

### Issue: "Module not found" errors

**Solution:** Ensure virtual environment is activated and dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: "Permission denied" on scripts

**Solution (macOS/Linux):**
```bash
chmod +x start.sh
```

### Issue: Database errors

**Solution:** Delete the database file and restart:
```bash
rm gemini_rag.db
# Restart the server - tables will be recreated
```

### Issue: Port 8000 already in use

**Solution:** Change the port in the start command:
```bash
uvicorn app.main:app --reload --port 8001
```

---

## 6. Next Steps

1. ✅ Complete Google Cloud setup
2. ✅ Complete local environment setup
3. ✅ Test backend API
4. ⏳ Implement Chat endpoint (US4)
5. ⏳ Build Frontend (React + Vite)
6. ⏳ End-to-end testing

---

## 7. Additional Resources

- [Google Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
- [File Search API Guide](https://ai.google.dev/gemini-api/docs/file-search)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

---

## 8. Security Reminders

- ⚠️ **Never commit `.env` to version control**
- ⚠️ **Never share your API key publicly**
- ⚠️ **Restrict API key usage in Google Cloud Console**
- ⚠️ **Use environment-specific API keys** (dev, staging, prod)
- ⚠️ **Monitor API usage and set billing alerts**
