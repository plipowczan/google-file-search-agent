#!/bin/bash
# Start script for Gemini RAG Manager (Linux/Mac)
# This script sets up and starts the backend server

echo "========================================"
echo "  Gemini RAG Manager - Startup"
echo "========================================"
echo ""

# Check if .env exists in root
if [ ! -f .env ]; then
    echo "[ERROR] Plik .env nie istnieje!"
    echo "[INFO] Skopiuj .env.example do .env i uzupełnij GOOGLE_API_KEY"
    echo ""
    exit 1
fi

# Navigate to backend
cd backend || exit 1

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[INFO] Tworzenie środowiska wirtualnego..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Nie udało się utworzyć venv"
        exit 1
    fi
fi

# Activate virtual environment
echo "[INFO] Aktywacja środowiska wirtualnego..."
source venv/bin/activate

# Install/upgrade dependencies
echo "[INFO] Instalacja zależności..."
pip install -r requirements.txt --prefer-binary
if [ $? -ne 0 ]; then
    echo "[ERROR] Nie udało się zainstalować zależności"
    exit 1
fi

# Start the server
echo ""
echo "========================================"
echo "  Uruchamianie serwera FastAPI"
echo "========================================"
echo ""
echo "[INFO] Server: http://localhost:8000"
echo "[INFO] Swagger UI: http://localhost:8000/docs"
echo "[INFO] ReDoc: http://localhost:8000/redoc"
echo ""

uvicorn app.main:app --reload
