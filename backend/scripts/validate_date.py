#!/usr/bin/env python
"""
Validate system date before fetching stock data
"""

from datetime import datetime
import yfinance as yf
import sys

def validate_system_date():
    """Check if system date is reasonable for stock data fetching"""
    now = datetime.now()
    current_year = now.year

    print(f"System date: {now.strftime('%A, %B %d, %Y %H:%M:%S')}")

    # Check if year is in the future beyond reasonable bounds
    if current_year > 2025:
        print(f"\n❌ ERROR: System year ({current_year}) is too far in the future!")
        print("Yahoo Finance cannot provide data for future dates.")
        print("\nPlease fix your system date before fetching stock data.")
        print(f"Expected year range: 2020-2025")
        return False

    # Test Yahoo Finance connectivity
    print("\nTesting Yahoo Finance connectivity...")
    try:
        test_stock = yf.Ticker('AAPL')
        test_data = test_stock.history(period='1d')

        if test_data.empty:
            print("⚠️  WARNING: Yahoo Finance returned no data!")
            print("This usually means:")
            print("  1. System date is incorrect (too far in future/past)")
            print("  2. Network connectivity issues")
            print("  3. Yahoo Finance API is down")
            print("  4. Market is closed and no recent data available")
            return False
        else:
            latest_date = test_data.index[-1].date()
            print(f"✓ Yahoo Finance is working! Latest data: {latest_date}")
            return True

    except Exception as e:
        print(f"❌ ERROR: Failed to connect to Yahoo Finance: {e}")
        return False

if __name__ == '__main__':
    if not validate_system_date():
        sys.exit(1)
    else:
        print("\n✓ System date validation passed!")
        sys.exit(0)
