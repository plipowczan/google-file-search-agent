# Gemini RAG Manager - Startup Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Gemini RAG Manager - Startup"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "[ERROR] Plik .env nie istnieje!" -ForegroundColor Red
    Write-Host "[INFO] Skopiuj .env.example do .env i uzupelnij GOOGLE_API_KEY" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit..."
    exit 1
}

# Function to check if a port is listening
function Test-PortListening {
    param (
        [int]$Port
    )
    $tcpConnections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    return $tcpConnections -ne $null
}

# Start Backend
if (Test-PortListening -Port 8000) {
    Write-Host "[INFO] Backend (port 8000) is already running. Skipping start." -ForegroundColor Yellow
}
else {
    Write-Host "[INFO] Starting Backend..." -ForegroundColor Green
    $backendBatContent = @"
@echo off
title Gemini Backend
cd backend
if not exist venv python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt --prefer-binary
uvicorn app.main:app --reload
pause
"@
    Set-Content -Path ".start_backend.bat" -Value $backendBatContent
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c .start_backend.bat" -WindowStyle Normal
}

# Start Frontend
if (Test-PortListening -Port 5173) {
    Write-Host "[INFO] Frontend (port 5173) is already running. Skipping start." -ForegroundColor Yellow
}
else {
    Write-Host "[INFO] Starting Frontend..." -ForegroundColor Green
    $frontendBatContent = @"
@echo off
title Gemini Frontend
cd frontend
npm install
npm run dev
pause
"@
    Set-Content -Path ".start_frontend.bat" -Value $frontendBatContent
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c .start_frontend.bat" -WindowStyle Normal
}

Write-Host ""
Write-Host "[INFO] Waiting for services to initialize (10s)..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "[INFO] Running Verification Script..." -ForegroundColor Cyan

# Run verification in the current window
Push-Location backend
try {
    # Activate venv and run script
    & .\venv\Scripts\python.exe ..\verify_backend.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] Verification passed!" -ForegroundColor Green
    }
    else {
        Write-Host "[WARNING] Verification script encountered errors." -ForegroundColor Yellow
    }
}
catch {
    Write-Host "[ERROR] Failed to run verification script: $_" -ForegroundColor Red
}
finally {
    Pop-Location
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Gemini RAG Manager is Running"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[INFO] Backend: http://localhost:8000"
Write-Host "[INFO] Frontend: http://localhost:5173"
Write-Host ""
Read-Host "Press Enter to exit..."
