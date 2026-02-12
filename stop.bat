@echo off
setlocal enabledelayedexpansion

echo 🛑 Stopping Stock Screener Application...
echo.

:: Function-like behavior for killing by port
call :KillByPort 5001 "Backend (Flask)"
call :KillByPort 3001 "Frontend (React)"
call :KillByPort 3000 "Frontend (React - alternate)"

echo.
echo Checking for any remaining python processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Stock Screener Backend*" 2>nul
if !errorlevel! equ 0 (
    echo   ✓ Cleaned up remaining python processes
) else (
    echo   ℹ️  No matching python processes found (or access denied)
)

echo.
echo Checking for any remaining node processes...
taskkill /F /IM node.exe 2>nul
if !errorlevel! equ 0 (
    echo   ✓ Cleaned up remaining node processes
) else (
    echo   ℹ️  No matching node processes found
)

echo.
echo ✅ Stock Screener stopped successfully!
echo.
echo To start again, run: start.bat
pause
goto :EOF

:KillByPort
set port=%1
set name=%2
echo Checking for %name% on port %port%...

:: Find PID using netstat
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%port%') do (
    set pid=%%a
)

if "%pid%"=="" (
    echo   ℹ️  No %name% process found on port %port%
) else (
    echo   🔍 Found %name% process (PID: %pid%)
    taskkill /F /PID %pid% 2>nul
    if !errorlevel! equ 0 (
        echo   ✓ %name% stopped
    ) else (
        echo   ⚠️  Failed to stop %name% (PID: %pid%)
    )
    set pid=
)
exit /b 0
