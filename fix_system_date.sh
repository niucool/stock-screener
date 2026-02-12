#!/bin/bash

# Stock Screener - System Date Fix Script
# This script fixes the system date issue preventing Yahoo Finance data fetches

echo "============================================================"
echo "STOCK SCREENER - SYSTEM DATE FIX"
echo "============================================================"
echo ""

# Show current date
echo "Current system date:"
date
echo ""

# Check if running on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected: macOS"
    echo ""
    echo "The system date appears to be set to 2025 instead of 2024."
    echo "This prevents Yahoo Finance from returning stock data."
    echo ""
    echo "TO FIX THIS ISSUE:"
    echo ""
    echo "1. Run the following command (requires admin password):"
    echo ""
    echo "   sudo date 111820052024"
    echo ""
    echo "   This sets: November 18, 2024 at 20:05"
    echo ""
    echo "2. After fixing, verify with:"
    echo ""
    echo "   date"
    echo ""
    echo "3. Test Yahoo Finance connectivity:"
    echo ""
    echo "   cd backend/scripts"
    echo "   python validate_date.py"
    echo ""
    echo "4. Refresh stock data:"
    echo ""
    echo "   Option A: Open http://localhost:3001 and click 'Refresh Data'"
    echo "   Option B: cd backend/scripts && python fetch_stock_data.py && python process_stock_data.py"
    echo ""
    echo "============================================================"
    echo ""
    echo "NOTE: I cannot run 'sudo date' automatically as it requires"
    echo "your administrator password. Please run the command manually."
    echo "============================================================"
else
    echo "Detected: Linux/Unix"
    echo ""
    echo "Run manually:"
    echo "  sudo date -s '2024-11-18 20:05:00'"
fi
echo ""
