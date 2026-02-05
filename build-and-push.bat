@echo off
REM Build and Push Script for Question Answer Generator (Windows)
REM This script builds Docker images and pushes them to a registry

setlocal enabledelayedexpansion

REM Configuration
set REGISTRY=your-registry
set VERSION=latest
set BACKEND_IMAGE=%REGISTRY%/question-answer-backend
set FRONTEND_IMAGE=%REGISTRY%/question-answer-frontend

REM Parse command line arguments
set BUILD_ONLY=false
set PUSH_ONLY=false
set SCAN=false

:parse_args
if "%~1"=="" goto end_parse
if "%~1"=="--build-only" (
    set BUILD_ONLY=true
    shift
    goto parse_args
)
if "%~1"=="--push-only" (
    set PUSH_ONLY=true
    shift
    goto parse_args
)
if "%~1"=="--scan" (
    set SCAN=true
    shift
    goto parse_args
)
if "%~1"=="--registry" (
    set REGISTRY=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--version" (
    set VERSION=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--help" (
    echo Usage: %~nx0 [OPTIONS]
    echo.
    echo Options:
    echo   --build-only       Only build images, don't push
    echo   --push-only        Only push images, don't build
    echo   --scan             Scan images for vulnerabilities
    echo   --registry REGISTRY  Set registry (default: your-registry^)
    echo   --version VERSION    Set version tag (default: latest^)
    echo   --help             Show this help message
    echo.
    echo Examples:
    echo   %~nx0                                    # Build and push with defaults
    echo   %~nx0 --build-only                       # Only build images
    echo   %~nx0 --registry myregistry --version v1.0  # Custom registry and version
    echo   %~nx0 --scan                             # Build and scan for vulnerabilities
    exit /b 0
)
echo Unknown option: %~1
echo Use --help for usage information
exit /b 1

:end_parse

echo ============================================
echo Question Answer Generator - Build and Push
echo ============================================
echo.
echo Registry: %REGISTRY%
echo Version: %VERSION%
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running
    echo Please start Docker Desktop and try again
    exit /b 1
)

if "%PUSH_ONLY%"=="true" goto push_images
if "%BUILD_ONLY%"=="true" goto build_images

REM Build and push
:build_and_push
call :build_backend
if errorlevel 1 exit /b 1
call :build_frontend
if errorlevel 1 exit /b 1
if "%SCAN%"=="true" call :scan_images
call :push_images
if errorlevel 1 exit /b 1
call :show_info
goto end

REM Build only
:build_images
call :build_backend
if errorlevel 1 exit /b 1
call :build_frontend
if errorlevel 1 exit /b 1
if "%SCAN%"=="true" call :scan_images
call :show_info
goto end

REM Push only
:push_images
echo Pushing images to registry...
docker push %BACKEND_IMAGE%:%VERSION%
docker push %BACKEND_IMAGE%:latest
echo Backend image pushed
docker push %FRONTEND_IMAGE%:%VERSION%
docker push %FRONTEND_IMAGE%:latest
echo Frontend image pushed
echo.
if "%PUSH_ONLY%"=="true" goto end
exit /b 0

REM Functions
:build_backend
echo Building backend image...
docker build -f backend\Dockerfile.prod -t %BACKEND_IMAGE%:%VERSION% -t %BACKEND_IMAGE%:latest .\backend
if errorlevel 1 (
    echo Error building backend image
    exit /b 1
)
echo Backend image built
echo.
exit /b 0

:build_frontend
echo Building frontend image...
docker build -f frontend\Dockerfile.prod -t %FRONTEND_IMAGE%:%VERSION% -t %FRONTEND_IMAGE%:latest .\frontend
if errorlevel 1 (
    echo Error building frontend image
    exit /b 1
)
echo Frontend image built
echo.
exit /b 0

:scan_images
echo Scanning images for vulnerabilities...
where trivy >nul 2>&1
if errorlevel 1 (
    echo Trivy not installed. Skipping vulnerability scan.
    echo Install Trivy: https://github.com/aquasecurity/trivy
) else (
    echo Scanning backend image...
    trivy image %BACKEND_IMAGE%:%VERSION%
    echo Scanning frontend image...
    trivy image %FRONTEND_IMAGE%:%VERSION%
    echo Image scanning complete
)
echo.
exit /b 0

:show_info
echo ============================================
echo Build complete!
echo ============================================
echo.
echo Images built:
echo   Backend:  %BACKEND_IMAGE%:%VERSION%
echo   Frontend: %FRONTEND_IMAGE%:%VERSION%
echo.
echo Image sizes:
docker images | findstr question-answer
echo.
exit /b 0

:end
echo Done!
endlocal
