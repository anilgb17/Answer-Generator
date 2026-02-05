@echo off
echo Setting up Question Answer Generator...
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker Compose is not installed or not in PATH
    exit /b 1
)

echo Docker and Docker Compose found!
echo.

REM Create .env file if it doesn't exist
if not exist backend\.env (
    echo Creating backend/.env from template...
    copy backend\.env.example backend\.env
    echo.
    echo IMPORTANT: Please edit backend/.env and add your API keys
    echo.
) else (
    echo backend/.env already exists, skipping...
)

echo Setup complete!
echo.
echo To start the application:
echo   docker-compose up
echo.
echo The application will be available at:
echo   Frontend: http://localhost:3000
echo   Backend API: http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
pause
