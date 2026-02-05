@echo off
setlocal

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="up" goto up
if "%1"=="down" goto down
if "%1"=="logs" goto logs
if "%1"=="test-backend" goto test_backend
if "%1"=="test-frontend" goto test_frontend
if "%1"=="clean" goto clean
goto help

:help
echo Question Answer Generator - Command Runner
echo.
echo Usage: run.bat [command]
echo.
echo Commands:
echo   up              Start all services with Docker Compose
echo   down            Stop all services
echo   logs            View logs from all services
echo   test-backend    Run backend tests
echo   test-frontend   Run frontend tests
echo   clean           Remove all containers, volumes, and generated files
echo   help            Show this help message
goto end

:up
echo Starting all services...
docker-compose up -d
echo.
echo Services started!
echo   Frontend: http://localhost:3000
echo   Backend API: http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo To view logs: run.bat logs
goto end

:down
echo Stopping all services...
docker-compose down
echo Services stopped.
goto end

:logs
echo Showing logs (Ctrl+C to exit)...
docker-compose logs -f
goto end

:test_backend
echo Running backend tests...
cd backend
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    pytest
) else (
    echo Virtual environment not found. Running tests in Docker...
    docker-compose run --rm backend pytest
)
cd ..
goto end

:test_frontend
echo Running frontend tests...
cd frontend
if exist node_modules (
    call npm test
) else (
    echo Node modules not found. Running tests in Docker...
    docker-compose run --rm frontend npm test
)
cd ..
goto end

:clean
echo WARNING: This will remove all containers, volumes, and generated files!
set /p confirm="Are you sure? (y/N): "
if /i not "%confirm%"=="y" goto end
echo Cleaning up...
docker-compose down -v
if exist backend\uploads rmdir /s /q backend\uploads
if exist backend\outputs rmdir /s /q backend\outputs
if exist backend\logs rmdir /s /q backend\logs
if exist backend\data rmdir /s /q backend\data
echo Cleanup complete.
goto end

:end
endlocal
