@echo off
setlocal
title DiaBeat AI Neural Bridge

echo ==========================================
echo    DiaBeat AI - Neural Bridge Controller
echo ==========================================
echo.

:: Check if python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python to continue.
    pause
    exit /b 1
)

echo Starting Neural Bridge (Backend Server)...
:: Use a separate window for uvicorn so it doesn't close if the main script finishes
:: but we want to keep it visible for logs.
start "DiaBeat AI Backend" /i cmd /k "python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

echo Waiting for Neural Core to initialize (5s)...
timeout /t 5 /nobreak > nul

echo.
echo Launching Neural Interface (Frontend)...
start http://127.0.0.1:8000

echo.
echo ------------------------------------------
echo Status: Neural Link ACTIVE
echo ------------------------------------------
echo.
echo Keep the backend window open to maintain connectivity.
echo If you see 'Neural Link Offline', check the other window for errors.
echo.
pause
