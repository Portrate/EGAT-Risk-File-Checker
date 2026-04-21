@echo off
chcp 65001 >nul
title Build - Risk File Checker

echo ========================================
echo   Building Risk File Checker EXE
echo ========================================
echo.

REM --- Check Python ---
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found.
    pause
    exit /b 1
)

REM --- Install build deps ---
echo [1/3] Installing build dependencies...
pip install pyinstaller --quiet
pip install -r requirements.txt --quiet

echo.
echo [2/3] Running PyInstaller...
pyinstaller ^
    --onefile ^
    --console ^
    --name "RiskFileChecker" ^
    --add-data "static;static" ^
    --add-data "templates;templates" ^
    --hidden-import uvicorn.logging ^
    --hidden-import uvicorn.loops ^
    --hidden-import uvicorn.loops.auto ^
    --hidden-import uvicorn.protocols ^
    --hidden-import uvicorn.protocols.http ^
    --hidden-import uvicorn.protocols.http.auto ^
    --hidden-import uvicorn.protocols.websockets ^
    --hidden-import uvicorn.protocols.websockets.auto ^
    --hidden-import uvicorn.lifespan ^
    --hidden-import uvicorn.lifespan.on ^
    --hidden-import fastapi ^
    --hidden-import pymupdf ^
    --hidden-import httpx ^
    --hidden-import jinja2 ^
    --hidden-import aiofiles ^
    --hidden-import pytesseract ^
    --hidden-import PIL ^
    --hidden-import PIL.Image ^
    --collect-all pymupdf ^
    --collect-all PIL ^
    run.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed.
    pause
    exit /b 1
)

echo.
echo [3/3] Done!
echo.
echo ========================================
echo   Output: dist\RiskFileChecker.exe
echo ========================================
echo.
pause
