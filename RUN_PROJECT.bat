@echo off
TITLE ANSH-M Project Starter
echo ----------------------------------------------------------------
echo   ANSH-M Agriculture Intelligence System - ONE-CLICK START
echo ----------------------------------------------------------------
echo.

echo [1/2] Starting Backend (FastAPI) on Port 8000...
start "ANSH-M BACKEND" cmd /k "cd backend && echo Installing dependencies (please wait)... && pip install -r requirements.txt && echo Starting Server... && uvicorn app.main:app --reload --port 8000"

echo [2/2] Starting Frontend (Next.js) on Port 3000...
start "ANSH-M FRONTEND" cmd /k "cd frontend && echo Starting Developer Server... && npm run dev"

echo.
echo ----------------------------------------------------------------
echo   SUCCESS: Servers are starting in separate windows.
echo   1. Keep those windows open while using the app.
echo   2. Wait about 10-20 seconds for the "Ready" message.
echo   3. Visit: http://localhost:3000
echo ----------------------------------------------------------------
echo.
pause
