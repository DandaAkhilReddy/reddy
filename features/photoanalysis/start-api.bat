@echo off
REM ReddyFit Photo Analysis API - Startup Script
REM Generated: 2025-10-17

echo.
echo ============================================================
echo   ReddyFit Photo Analysis API - Starting Server
echo ============================================================
echo.

REM Navigate to the correct directory
cd /d "%~dp0"

echo [1/4] Checking directory...
echo Current directory: %CD%
echo.

REM Check if .env file exists
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo Please create .env file with your API keys.
    echo.
    pause
    exit /b 1
)

echo [2/4] Environment file found: .env
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python and add it to PATH.
    echo.
    pause
    exit /b 1
)

echo [3/4] Python found:
python --version
echo.

echo [4/4] Starting FastAPI server...
echo.
echo ============================================================
echo   Server Information
echo ============================================================
echo   API Base URL:     http://localhost:8000
echo   Swagger Docs:     http://localhost:8000/api/docs
echo   ReDoc:            http://localhost:8000/api/redoc
echo   Health Check:     http://localhost:8000/api/health
echo ============================================================
echo.
echo Press Ctrl+C to stop the server
echo.

REM Need to run from parent directory for proper imports
cd ..\..\..

echo Starting from: %CD%
echo.

REM Start the server with uvicorn (using full module path)
python -m uvicorn features.photoanalysis.api.main:app --host 0.0.0.0 --port 8000 --reload

REM If that fails, try alternative
if errorlevel 1 (
    echo.
    echo [WARNING] Trying alternative startup method...
    echo.
    cd features\photoanalysis
    python -m api.main
)

pause
