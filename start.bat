@echo off
chcp 65001 >nul
title Risk File Checker

echo ========================================
echo   Risk File Checker - Setup ^& Start
echo ========================================
echo.

REM --- Check Python ---
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

REM --- Check Ollama ---
ollama --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Ollama not found. Please install from https://ollama.com
    pause
    exit /b 1
)

REM --- Create venv if not exists ---
if not exist "venv" (
    echo [1/3] Creating virtual environment...
    python -m venv venv
)

REM --- Activate venv and install deps ---
echo [2/3] Installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet

REM --- Pull model if needed ---
echo [3/3] Checking Ollama model...
ollama list | findstr "gemma4:26b" >nul 2>&1
if errorlevel 1 (
    echo Pulling gemma4:26b model (this may take a while on first run)...
    ollama pull gemma4:26b
)

REM --- Start ---
echo.
echo ========================================
echo   Starting server at http://localhost:8000
echo   Press Ctrl+C to stop
echo ========================================
echo.
start http://localhost:8000
uvicorn main:app --host 0.0.0.0 --port 8000
pause
