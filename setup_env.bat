@echo off
echo ============================================================
echo    Answer Generator - Environment Setup
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org/
    pause
    exit /b 1
)

REM Run the setup script
python setup_env.py

echo.
echo ============================================================
echo Setup complete! Press any key to exit...
pause >nul
