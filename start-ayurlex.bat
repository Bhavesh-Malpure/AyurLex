@echo off
title Ayurlex - Launching Localhost Servers
echo ===================================================
echo     🌿 Launching Ayurlex (Backend + Frontend)
echo ===================================================
echo.

cd /d "%~dp0"

echo [1/2] Starting Ayurlex FastAPI Backend on port 8000...
start "Ayurlex Backend (FastAPI)" cmd /k "cd backend && .venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] Starting Ayurlex Frontend (Vite) on port 5173...
start "Ayurlex Frontend (Vite)" cmd /k "cd frontend && npm run dev"

timeout /t 2 /nobreak >nul

echo.
echo ===================================================
echo   Ayurlex is running!
echo   Frontend: http://localhost:5173
echo   Backend API: http://localhost:8000/docs
echo ===================================================
echo Opening Ayurlex in default browser...
start http://localhost:5173

