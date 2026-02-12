@echo off
setlocal enabledelayedexpansion

echo 🚀 Starting Stock Screener Application...
echo.

:: Get directory of this script
set "SCRIPT_DIR=%~dp0"
:: Remove trailing backslash
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: Ensure logs directory exists
if not exist "%SCRIPT_DIR%\logs" mkdir "%SCRIPT_DIR%\logs"

echo 📡 Starting Flask backend server (port 5001)...
:: Start backend in background using start /B, redirecting output is tricky in batch with start /B
:: We will use 'start' minimized to run it and redirect output
start "Stock Screener Backend" /MIN /D "%SCRIPT_DIR%\backend\api" cmd /c "set FLASK_ENV=development && python app.py > ..\..\logs\backend-console.log 2>&1"

:: Wait a bit for backend
timeout /t 3 /nobreak >nul

echo ⚛️  Starting React frontend server (port 3001)...
:: Start frontend minimized
start "Stock Screener Frontend" /MIN /D "%SCRIPT_DIR%\frontend" cmd /c "set PORT=3001 && set BROWSER=none && npm start > ..\..\logs\frontend-console.log 2>&1"

:: Wait a bit for frontend
timeout /t 5 /nobreak >nul

echo.
echo ✅ Stock Screener is running!
echo.
echo 📊 Application URLs:
echo    Frontend: http://localhost:3001
echo    Backend API: http://localhost:5001/api
echo.
echo 📝 Logs:
echo    Backend: %SCRIPT_DIR%\logs\backend-console.log
echo    Frontend: %SCRIPT_DIR%\logs\frontend-console.log
echo.
echo Press any key to exist this script (servers will continue running)...
echo Run stop.bat to stop all servers.
echo.
pause
