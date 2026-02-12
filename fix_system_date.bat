@echo off
setlocal

echo ============================================================
echo STOCK SCREENER - SYSTEM DATE FIX
echo ============================================================
echo.

echo Current system date:
date /t
time /t
echo.

echo This script helps fix issues where the system date is incorrect,
echo which prevents Yahoo Finance data fetches.
echo.
echo TO FIX THIS ISSUE:
echo.
echo 1. Open PowerShell as Administrator
echo.
echo 2. Run the following command:
echo.
echo    Set-Date -Date "2024-11-18 20:05:00"
echo.
echo 3. Verify with:
echo.
echo    Get-Date
echo.
echo 4. Test Yahoo Finance connectivity:
echo.
echo    cd backend\scripts
echo    python validate_date.py
echo.
echo 5. Refresh stock data:
echo.
echo    Option A: Open http://localhost:3001 and click 'Refresh Data'
echo    Option B: cd backend\scripts ^&^& python fetch_stock_data.py ^&^& python process_stock_data.py
echo.
echo ============================================================
echo NOTE: You must run the date change command as Administrator.
echo ============================================================
echo.
pause
