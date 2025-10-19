@echo off
REM ReddyFit Photo Analysis API - Fly.io Deployment Script (Windows)

echo.
echo ============================================================
echo   ReddyFit Photo Analysis API - Fly.io Deployment
echo ============================================================
echo.

REM Navigate to the correct directory
cd /d "%~dp0"

echo [1/6] Checking Fly.io CLI installation...
echo.

where flyctl >nul 2>&1
if errorlevel 1 (
    echo Fly.io CLI not found. Installing...
    echo.
    echo Please install Fly.io CLI manually:
    echo   1. Visit: https://fly.io/docs/hands-on/install-flyctl/
    echo   2. Or run: powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
    echo.
    echo After installation, run this script again.
    pause
    exit /b 1
)

echo ✅ Fly.io CLI found
flyctl version
echo.

echo [2/6] Checking Fly.io authentication...
echo.

flyctl auth whoami >nul 2>&1
if errorlevel 1 (
    echo Please log in to Fly.io:
    flyctl auth login
)

echo ✅ Authenticated
echo.

echo [3/6] Checking if app exists...
echo.

flyctl apps list | findstr "reddyfit-api" >nul 2>&1
if errorlevel 1 (
    echo Creating new Fly.io app: reddyfit-api
    flyctl apps create reddyfit-api
    echo ✅ App created
) else (
    echo ✅ App already exists
)

echo.

echo [4/6] Setting environment secrets...
echo.
echo IMPORTANT: You'll need to set these secrets manually:
echo.
echo   flyctl secrets set ANTHROPIC_API_KEY=sk-ant-api03-...
echo   flyctl secrets set FIREBASE_PROJECT_ID=reddyfit-dev
echo   flyctl secrets set FIREBASE_STORAGE_BUCKET=reddyfit-dev.appspot.com
echo   flyctl secrets set FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
echo.

choice /C YN /M "Have you already set the secrets"
if errorlevel 2 (
    echo.
    echo Please set the secrets using the commands above, then run this script again.
    pause
    exit /b 1
)

echo.

echo [5/6] Deploying to Fly.io...
echo.
echo This will:
echo   - Build Docker image with Python 3.11
echo   - Push to Fly.io registry
echo   - Deploy to production
echo.
echo This may take 3-5 minutes...
echo.

flyctl deploy --ha=false

if errorlevel 1 (
    echo.
    echo ❌ Deployment failed!
    echo Check logs with: flyctl logs
    pause
    exit /b 1
)

echo.
echo ✅ Deployment successful!
echo.

echo [6/6] Testing deployment...
echo.

timeout /t 5 /nobreak >nul

REM Get app info
flyctl info

echo.
echo ============================================================
echo   🎉 Deployment Complete!
echo ============================================================
echo.
echo Your API is now live!
echo.
echo Open in browser:
echo   flyctl open /api/docs
echo.
echo Useful commands:
echo   flyctl logs             - View application logs
echo   flyctl status           - Check app status
echo   flyctl open /api/docs   - Open Swagger UI
echo   flyctl ssh console      - SSH into container
echo.

pause
