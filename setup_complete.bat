@echo off
echo ========================================
echo Question Answer Generator - Complete Setup
echo ========================================
echo.

echo Step 1: Installing Backend Dependencies...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)
cd ..
echo ✓ Backend dependencies installed
echo.

echo Step 2: Installing Frontend Dependencies...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install frontend dependencies
    pause
    exit /b 1
)
cd ..
echo ✓ Frontend dependencies installed
echo.

echo Step 3: Setting up Authentication System...
python setup_auth.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to setup authentication
    pause
    exit /b 1
)
echo ✓ Authentication system configured
echo.

echo ========================================
echo Setup Complete! ✓
echo ========================================
echo.
echo Next steps:
echo 1. Start Redis:     docker-compose up redis -d
echo 2. Start Backend:   cd backend ^&^& uvicorn src.main:app --reload
echo 3. Start Frontend:  cd frontend ^&^& npm run dev
echo 4. Open browser:    http://localhost:3000
echo.
echo Default admin login:
echo   Email: admin@example.com
echo   Password: admin123
echo   ⚠️  Change this password immediately!
echo.
pause
