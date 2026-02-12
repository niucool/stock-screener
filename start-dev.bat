@echo off
setlocal enabledelayedexpansion

echo 🚀 Starting Stock Screener in Development Mode...
echo.
echo Starting backend and frontend servers...
echo Backend will run on: http://localhost:5001
echo Frontend will run on: http://localhost:3001
echo.
echo Press any key to stop all servers (this script will attempt to close them)
echo ================================================
echo.

:: Get directory of this script
set "SCRIPT_DIR=%~dp0"
:: Remove trailing backslash if present
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: Start Backend Server in a new window
echo Starting Backend...
start "Stock Screener Backend" /D "%SCRIPT_DIR%\backend\api" cmd /k "python app.py"

:: Start Frontend Server in a new window
echo Starting Frontend...
start "Stock Screener Frontend" /D "%SCRIPT_DIR%\frontend" cmd /k "set PORT=3001 && set BROWSER=none && npm start"

echo.
echo Servers started in separate windows.
echo To stop everything, close the windows or run stop.bat.
echo.
pause
