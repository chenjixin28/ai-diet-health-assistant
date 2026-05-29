@echo off
chcp 65001 >nul
title AI Diet Health Assistant - Starting...

echo.
echo ============================================
echo   AI Diet Health Assistant - Startup
echo ============================================
echo.

set PYTHON_PATH=C:\Users\hgdcy\AppData\Local\Programs\Python\Python313\python.exe

echo [1/4] Checking Python...
"%PYTHON_PATH%" --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found, please install Python 3.10+
    pause
    exit /b 1
)

echo [2/4] Checking Node.js...
node --version
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found, please install Node.js 18+
    pause
    exit /b 1
)

echo [3/4] Installing backend dependencies...
cd /d "%~dp0backend"
"%PYTHON_PATH%" -m pip install -r requirements.txt -q

echo [4/4] Installing frontend dependencies...
cd /d "%~dp0frontend"
if not exist "node_modules\" (
    call npm install
)

echo.
echo ============================================
echo   Starting services...
echo ============================================
echo.
echo   Backend API:  http://localhost:8000
echo   Frontend:     http://localhost:5173
echo   API Docs:     http://localhost:8000/docs
echo.
echo   Press Ctrl+C to stop all services
echo ============================================
echo.

cd /d "%~dp0backend"
start "AI Diet - Backend" cmd /k ""%PYTHON_PATH%" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

cd /d "%~dp0frontend"
start "AI Diet - Frontend" cmd /k "npm run dev"

echo Services started, opening browser...
timeout /t 3 /nobreak >nul
start http://localhost:5173

pause
