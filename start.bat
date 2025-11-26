@echo off
REM Start script for Gemini RAG Manager (Windows)
REM This script sets up and starts the backend server

echo ========================================
echo   Gemini RAG Manager - Startup
echo ========================================
echo.

REM Check if .env exists in root
if not exist .env (
    echo [ERROR] Plik .env nie istnieje!
    echo [INFO] Skopiuj .env.example do .env i uzupelnij GOOGLE_API_KEY
    echo.
    pause
    exit /b 1
)

REM Navigate to backend
cd backend

REM Check if virtual environment exists
if not exist venv (
    echo [INFO] Tworzenie srodowiska wirtualnego...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Nie udalo sie utworzyc venv
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo [INFO] Aktywacja srodowiska wirtualnego...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo [INFO] Instalacja zaleznosci...
pip install -r requirements.txt --prefer-binary
if errorlevel 1 (
    echo [ERROR] Nie udalo sie zainstalowac zaleznosci
    pause
    exit /b 1
)

REM Start the server
echo.
echo ========================================
echo   Uruchamianie serwera FastAPI
echo ========================================
echo.
echo [INFO] Server: http://localhost:8000
echo [INFO] Swagger UI: http://localhost:8000/docs
echo [INFO] ReDoc: http://localhost:8000/redoc
echo.

uvicorn app.main:app --reload

pause
