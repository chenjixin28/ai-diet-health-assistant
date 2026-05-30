@echo off
chcp 65001 >nul
title AI Diet Health - Quick Start

echo ============================================
echo    AI Diet Health - Quick Start
echo ============================================
echo.

echo [1/2] Starting backend...
start "Backend" cmd /k "cd /d f:\ai-diet-health-assistant\backend && C:\Users\hgdcy\AppData\Local\Programs\Python\Python313\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo [2/2] Starting frontend...
timeout /t 3 /nobreak >nul
start "Frontend" cmd /k "cd /d f:\ai-diet-health-assistant\frontend && npm run dev"

echo.
echo ============================================
echo    Services starting...
echo    Frontend: http://localhost:5173
echo    Backend:  http://localhost:8000
echo ============================================
echo.
echo IMPORTANT: Do NOT close the two black windows!
echo.
timeout /t 5 /nobreak >nul
start http://localhost:5173
pause
