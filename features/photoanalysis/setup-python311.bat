@echo off
REM Automated Python 3.11 Virtual Environment Setup
REM For ReddyFit Photo Analysis API

echo.
echo ============================================================
echo   ReddyFit API - Python 3.11 Setup Script
echo ============================================================
echo.

REM Navigate to the correct directory
cd /d "%~dp0"

echo [Step 1/6] Checking Python 3.11 installation...
echo.

REM Check if Python 3.11 is installed
py -3.11 --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.11 not found!
    echo.
    echo Please install Python 3.11 first:
    echo   1. Visit: https://www.python.org/downloads/release/python-3119/
    echo   2. Download: Windows installer (64-bit)
    echo   3. During installation, CHECK "Add Python to PATH"
    echo   4. Run this script again after installation
    echo.
    pause
    exit /b 1
)

echo [SUCCESS] Python 3.11 found:
py -3.11 --version
echo.

echo [Step 2/6] Checking if virtual environment exists...
echo.

if exist "venv311" (
    echo [INFO] Virtual environment already exists: venv311
    echo.
    choice /C YN /M "Do you want to recreate it (this will delete existing venv)"
    if errorlevel 2 (
        echo Skipping virtual environment creation...
        goto activate_venv
    )
    if errorlevel 1 (
        echo Deleting existing virtual environment...
        rmdir /s /q venv311
    )
)

echo [Step 3/6] Creating Python 3.11 virtual environment...
echo.

py -3.11 -m venv venv311

if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment!
    echo.
    pause
    exit /b 1
)

echo [SUCCESS] Virtual environment created: venv311
echo.

:activate_venv

echo [Step 4/6] Activating virtual environment...
echo.

call venv311\Scripts\activate.bat

if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment!
    echo.
    pause
    exit /b 1
)

echo [SUCCESS] Virtual environment activated
echo.

echo [Step 5/6] Verifying Python version in venv...
echo.

python --version
echo.

echo [Step 6/6] Installing dependencies...
echo.
echo This may take 3-5 minutes. Please wait...
echo.

REM Upgrade pip first
python -m pip install --upgrade pip --quiet

REM Install all dependencies
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ERROR] Dependency installation failed!
    echo.
    echo Try running manually:
    echo   venv311\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] All dependencies installed!
echo.

echo.
echo ============================================================
echo   Setup Complete!
echo ============================================================
echo.

echo [Next Steps]
echo.
echo 1. Keep this terminal open (venv311 is activated)
echo.
echo 2. Start the API server:
echo    cd ..\..
echo    python -m uvicorn features.photoanalysis.api.main:app --host 0.0.0.0 --port 8000 --reload
echo.
echo 3. Or use the quick start script:
echo    start-api-python311.bat
echo.
echo 4. Access the API:
echo    - Swagger Docs: http://localhost:8000/api/docs
echo    - Health Check: http://localhost:8000/api/health
echo.

echo Press any key to exit (venv311 will remain activated in this terminal)...
pause >nul
