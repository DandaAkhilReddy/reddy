@echo off
REM Quick Start Script for ReddyFit API with Python 3.11
REM Use this after running setup-python311.bat

echo.
echo ============================================================
echo   ReddyFit Photo Analysis API - Starting Server
echo ============================================================
echo.

REM Navigate to the correct directory
cd /d "%~dp0"

echo [1/5] Checking Python 3.11 virtual environment...
echo.

if not exist "venv311" (
    echo [ERROR] Virtual environment not found!
    echo.
    echo Please run setup-python311.bat first to create the environment.
    echo.
    pause
    exit /b 1
)

echo [SUCCESS] Virtual environment found: venv311
echo.

echo [2/5] Activating virtual environment...
echo.

call venv311\Scripts\activate.bat

if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment!
    pause
    exit /b 1
)

echo [SUCCESS] Virtual environment activated
echo.

echo [3/5] Verifying Python version...
echo.

python --version
echo.

echo [4/5] Checking .env file...
echo.

cd ..\..

if not exist ".env" (
    echo [WARNING] .env file not found in reddy directory!
    echo The server may fail to start without environment variables.
    echo.
    choice /C YN /M "Continue anyway"
    if errorlevel 2 exit /b 1
)

echo.
echo [5/5] Starting FastAPI server...
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
echo Server is starting... (this may take 10-15 seconds)
echo.
echo Press Ctrl+C to stop the server
echo.
echo ============================================================
echo.

REM Start the server with uvicorn
python -m uvicorn features.photoanalysis.api.main:app --host 0.0.0.0 --port 8000 --reload

REM If server stops, show message
echo.
echo ============================================================
echo   Server Stopped
echo ============================================================
echo.

pause
