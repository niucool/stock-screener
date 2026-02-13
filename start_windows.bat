@echo off
chcp 65001 >nul
echo.
echo 🚀 Starting Stock Screener Application (Windows)...
echo.

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"

REM Create logs directory if it doesn't exist
if not exist "%SCRIPT_DIR%logs" mkdir "%SCRIPT_DIR%logs"

REM Function to cleanup on exit
setlocal enabledelayedexpansion
for /f "tokens=2 delims=;=" %%a in ('set BACKEND_PID 2^>nul') do (
    set "BACKEND_PID=%%a"
)
for /f "tokens=2 delims=;=" %%a in ('set FRONTEND_PID 2^>nul') do (
    set "FRONTEND_PID=%%a"
)

REM Trap Ctrl+C
set "CTRLC_TRAP=1"
if defined CTRLC_TRAP (
    echo Press Ctrl+C to stop all servers...
    echo.
)

REM Start Backend Server
echo 📡 Starting Flask backend server (port 5001)...
cd /d "%SCRIPT_DIR%backend\api"
start "Stock Screener Backend" /B python app.py > "%SCRIPT_DIR%logs\backend-console.log" 2>&1
for /f "tokens=2" %%a in ('tasklist /fi "WINDOWTITLE eq Stock Screener Backend" /fo csv ^| findstr /i "python"') do (
    set "BACKEND_PID=%%~a"
)
echo   ✓ Backend started (PID: !BACKEND_PID!)
timeout /t 3 /nobreak >nul

REM Check if backend is running
tasklist /fi "PID eq !BACKEND_PID!" 2>nul | findstr /i "python" >nul
if errorlevel 1 (
    echo   ✗ Backend failed to start. Check logs\backend-console.log
    goto :cleanup
)

REM Start Frontend Server
echo ⚛️  Starting React frontend server (port 3001)...
cd /d "%SCRIPT_DIR%frontend"
set "PORT=3001"
set "BROWSER=none"
start "Stock Screener Frontend" /B cmd /c "npm start > "%SCRIPT_DIR%logs\frontend-console.log" 2>&1"
for /f "tokens=2" %%a in ('tasklist /fi "WINDOWTITLE eq Stock Screener Frontend" /fo csv ^| findstr /i "cmd"') do (
    set "FRONTEND_PID=%%~a"
)
echo   ✓ Frontend started (PID: !FRONTEND_PID!)
timeout /t 5 /nobreak >nul

REM Check if frontend is running
tasklist /fi "PID eq !FRONTEND_PID!" 2>nul | findstr /i "cmd" >nul
if errorlevel 1 (
    echo   ✗ Frontend failed to start. Check logs\frontend-console.log
    goto :cleanup
)

echo.
echo ✅ Stock Screener is running!
echo.
echo 📊 Application URLs:
echo    Frontend: http://localhost:3001
echo    Backend API: http://localhost:5001/api
echo.
echo 📝 Logs:
echo    Backend: %SCRIPT_DIR%logs\backend-console.log
echo    Frontend: %SCRIPT_DIR%logs\frontend-console.log
echo.
echo Press Ctrl+C to stop all servers...
echo.

REM Wait for user interrupt
pause >nul

:cleanup
echo.
echo 🛑 Shutting down servers...
if defined BACKEND_PID (
    taskkill /PID !BACKEND_PID! /F >nul 2>&1
    echo   ✓ Backend server stopped
)
if defined FRONTEND_PID (
    taskkill /PID !FRONTEND_PID! /F >nul 2>&1
    echo   ✓ Frontend server stopped
)
echo.
echo Application stopped.
pause
exit /b 0