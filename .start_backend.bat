@echo off
title Gemini Backend
cd backend
if not exist venv python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt --prefer-binary
uvicorn app.main:app --reload
pause
