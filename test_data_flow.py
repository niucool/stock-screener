#!/usr/bin/env python
"""
Test script to diagnose data freshness issues
"""

import yfinance as yf
import json
from datetime import datetime
import sys

def test_yahoo_finance():
    """Test what data Yahoo Finance actually returns"""
    print("=" * 60)
    print("TESTING YAHOO FINANCE DATA FRESHNESS")
    print("=" * 60)
    print()

    symbols = ['AAPL', 'GOOGL', 'MSFT']

    for symbol in symbols:
        print(f"\nTesting {symbol}...")
        try:
            stock = yf.Ticker(symbol)

            # Get last 5 days
            hist = stock.history(period='5d', interval='1d')

            if hist.empty:
                print(f"  ❌ No data returned!")
                continue

            print(f"  ✓ Got {len(hist)} days of data")
            print(f"  Date range: {hist.index[0].date()} to {hist.index[-1].date()}")
            print(f"  Latest close: ${hist['Close'].iloc[-1]:.2f}")

            # Check if data is recent
            latest_date = hist.index[-1].date()
            today = datetime.now().date()
            days_old = (today - latest_date).days

            if days_old == 0:
                print(f"  ✓ Data is from today!")
            elif days_old <= 3:
                print(f"  ⚠️  Data is {days_old} day(s) old (weekend/holiday?)")
            else:
                print(f"  ❌ Data is {days_old} days old - STALE!")

        except Exception as e:
            print(f"  ❌ Error: {e}")

def check_local_files():
    """Check what's in our local data files"""
    print("\n" + "=" * 60)
    print("CHECKING LOCAL DATA FILES")
    print("=" * 60)
    print()

    files_to_check = [
        'backend/data/stocks/historical/AAPL.json',
        'backend/data/stocks/processed/AAPL.json'
    ]

    for filepath in files_to_check:
        print(f"\n{filepath}:")
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            if 'Historical_Data' in data:
                # Historical file
                latest = data['Historical_Data'][-1]
                print(f"  Latest date: {latest['Date']}")
                print(f"  Close: ${latest['Close']:.2f}")
            elif 'Date' in data:
                # Processed file
                print(f"  Date: {data['Date']}")
                print(f"  Close: ${data['Close']:.2f}")
                print(f"  RSI_14: {data.get('RSI_14', 'N/A')}")

        except FileNotFoundError:
            print(f"  ❌ File not found")
        except Exception as e:
            print(f"  ❌ Error: {e}")

def diagnose():
    """Run full diagnosis"""
    print(f"\nToday is: {datetime.now().strftime('%A, %B %d, %Y %H:%M:%S')}")
    print()

    test_yahoo_finance()
    check_local_files()

    print("\n" + "=" * 60)
    print("DIAGNOSIS COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    diagnose()
