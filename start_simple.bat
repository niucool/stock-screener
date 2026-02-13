@echo off
echo.
echo ========================================
echo   Stock Screener - Simple Startup
echo ========================================
echo.

REM Create logs directory
if not exist "logs" mkdir logs

echo [1/3] Starting Flask backend server (port 5001)...
cd backend\api
start "Stock Screener Backend" cmd /k "python app.py 2>&1 | tee ..\..\logs\backend-console.log"
cd ..\..

timeout /t 5 /nobreak >nul

echo [2/3] Starting React frontend server (port 3001)...
cd frontend
start "Stock Screener Frontend" cmd /k "set PORT=3001 && set BROWSER=none && npm start 2>&1 | tee ..\logs\frontend-console.log"
cd ..

timeout /t 8 /nobreak >nul

echo [3/3] Application started!
echo.
echo ========================================
echo   Access URLs:
echo.
echo   Frontend: http://localhost:3001
echo   Backend API: http://localhost:5001/api
echo.
echo   Logs directory: logs\
echo ========================================
echo.
echo Press any key to stop servers...
pause >nul

echo.
echo Stopping servers...
taskkill /FI "WINDOWTITLE eq Stock Screener Backend" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Stock Screener Frontend" /F >nul 2>&1

echo Done!
pause