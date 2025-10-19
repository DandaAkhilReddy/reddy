@echo off
REM Test ReddyFit Photo Analysis API
REM Quick health check and endpoint verification

echo.
echo ============================================================
echo   ReddyFit Photo Analysis API - Testing Endpoints
echo ============================================================
echo.

echo [1/3] Testing Health Check Endpoint...
curl -s http://localhost:8000/api/health
echo.
echo.

echo [2/3] Testing Detailed Health Check...
curl -s http://localhost:8000/api/health/detailed
echo.
echo.

echo [3/3] Opening Swagger Documentation in browser...
start http://localhost:8000/api/docs
echo.

echo ============================================================
echo   Test Complete!
echo ============================================================
echo.
echo If you see JSON responses above, the API is working correctly!
echo.
echo Available URLs:
echo   - API Docs: http://localhost:8000/api/docs
echo   - ReDoc:    http://localhost:8000/api/redoc
echo   - Health:   http://localhost:8000/api/health
echo.

pause
