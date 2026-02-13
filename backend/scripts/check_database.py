#!/usr/bin/env python
"""
Check database status and update if needed.
"""

import os
import sqlite3
import sys
from datetime import datetime

def check_database():
    """Check if database exists and has fresh data."""
    
    db_path = '../data/stocks.db'
    
    if not os.path.exists(db_path):
        print("Database not found. Need to run data refresh.")
        return False, "no_database"
    
    print(f"Database found: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if stock_indicators table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stock_indicators'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("stock_indicators table not found.")
            conn.close()
            return False, "no_table"
        
        # Check data count
        cursor.execute("SELECT COUNT(*) FROM stock_indicators")
        count = cursor.fetchone()[0]
        print(f"Rows in stock_indicators: {count}")
        
        if count == 0:
            print("No data in stock_indicators table.")
            conn.close()
            return False, "empty_table"
        
        # Check data freshness
        cursor.execute("SELECT MAX(data_age_days) FROM stock_indicators")
        max_age = cursor.fetchone()[0]
        
        if max_age is None:
            print("Cannot determine data age.")
            conn.close()
            return False, "unknown_age"
        
        print(f"Maximum data age: {max_age} days")
        
        # Data is fresh if ≤1 day old
        if max_age <= 1:
            print("Data is fresh (≤1 day old).")
            conn.close()
            return True, "fresh"
        else:
            print(f"Data needs refresh ({max_age} days old).")
            conn.close()
            return False, "stale"
            
    except Exception as e:
        print(f"Error checking database: {e}")
        conn.close()
        return False, "error"

def run_data_refresh():
    """Run the data refresh script."""
    print("\nRunning data refresh...")
    
    # Try to run the existing refresh script
    refresh_script = '../api/refresh_stocks.py'
    
    if os.path.exists(refresh_script):
        print(f"Found refresh script: {refresh_script}")
        
        # Import and run the refresh
        import subprocess
        try:
            result = subprocess.run(
                ['python', refresh_script],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(refresh_script)
            )
            
            print(f"Refresh script output:\n{result.stdout}")
            if result.stderr:
                print(f"Errors:\n{result.stderr}")
            
            if result.returncode == 0:
                print("Data refresh completed successfully.")
                return True
            else:
                print(f"Data refresh failed with code {result.returncode}.")
                return False
                
        except Exception as e:
            print(f"Error running refresh script: {e}")
            return False
    else:
        print(f"Refresh script not found: {refresh_script}")
        
        # Try alternative location
        refresh_script2 = 'refresh_stocks.py'
        if os.path.exists(refresh_script2):
            print(f"Found alternative script: {refresh_script2}")
            # Similar execution logic...
            return False
        else:
            print("No refresh script found. Manual data update needed.")
            return False

def main():
    """Main function."""
    print("=" * 60)
    print("Stock Screener Database Check")
    print("=" * 60)
    
    # Check database status
    is_ok, status = check_database()
    
    if not is_ok:
        print(f"\nDatabase status: {status}")
        
        if status in ["no_database", "no_table", "empty_table", "stale"]:
            response = input("\nDo you want to run data refresh? (y/n): ")
            if response.lower() == 'y':
                success = run_data_refresh()
                if success:
                    print("\n✅ Data refresh completed. Ready to run screener.")
                else:
                    print("\n❌ Data refresh failed. Please check logs.")
            else:
                print("\nSkipping data refresh. Screener may not work properly.")
        else:
            print("\nCannot proceed with current database state.")
    else:
        print("\n✅ Database is ready for screening.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()