@echo off
echo ========================================
echo Question Answer Generator - Startup
echo ========================================
echo.

REM Check if Redis is running
echo [1/4] Checking Redis...
docker ps | findstr redis >nul 2>&1
if %errorlevel% neq 0 (
    echo Redis not running. Starting Redis...
    docker-compose up redis -d
    timeout /t 3 >nul
) else (
    echo Redis is already running.
)
echo.

REM Start Backend
echo [2/4] Starting Backend Server...
start "Backend Server" cmd /k "cd backend && python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 5 >nul
echo.

REM Start Frontend
echo [3/4] Starting Frontend Server...
start "Frontend Server" cmd /k "cd frontend && npm run dev"
timeout /t 3 >nul
echo.

echo [4/4] Opening browser...
timeout /t 5 >nul
start http://localhost:3000
echo.

echo ========================================
echo Application Started Successfully!
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Frontend: http://localhost:3000
echo.
echo Press any key to stop all services...
pause >nul

echo.
echo Stopping services...
taskkill /FI "WINDOWTITLE eq Backend Server*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Frontend Server*" /F >nul 2>&1
docker-compose stop redis >nul 2>&1

echo Services stopped.
