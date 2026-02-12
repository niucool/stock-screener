#!/usr/bin/env python
"""
Data Migration Script
Migrates existing JSON data (historical stock prices) into the SQLite database.
"""

import os
import json
import sqlite3
import pandas as pd
import glob
from datetime import datetime

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '../data')
DB_PATH = os.path.join(DATA_DIR, 'stocks.db')
SP500_CSV = os.path.join(DATA_DIR, 'sp500_companies.csv')
HISTORICAL_DIR = os.path.join(DATA_DIR, 'stocks/historical')

def connect_db():
    """Connect to SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def migrate_companies(conn):
    """Import S&P 500 companies from CSV to 'stocks' table."""
    print(f"Importing companies from {SP500_CSV}...")
    
    if not os.path.exists(SP500_CSV):
        print(f"Error: CSV file not found at {SP500_CSV}")
        return

    try:
        df = pd.read_csv(SP500_CSV)
        cursor = conn.cursor()
        
        count = 0
        for _, row in df.iterrows():
            cursor.execute('''
                INSERT OR IGNORE INTO stocks 
                (symbol, company_name, sector, industry, last_updated)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                row['Symbol'],
                row['Security'],
                row['GICS Sector'],
                row['GICS Sub-Industry'],
                datetime.now().isoformat()
            ))
            count += 1
            
        conn.commit()
        print(f"[OK] Imported {count} companies into 'stocks' table.")
    except Exception as e:
        print(f"Error importing companies: {e}")

def migrate_historical_data(conn):
    """Import JSON files from historical directory to 'historical_prices' table."""
    print(f"\nImporting historical data from {HISTORICAL_DIR}...")
    
    if not os.path.exists(HISTORICAL_DIR):
        print(f"Error: Historical data directory not found at {HISTORICAL_DIR}")
        return

    json_files = glob.glob(os.path.join(HISTORICAL_DIR, '*.json'))
    print(f"Found {len(json_files)} JSON files.")
    
    cursor = conn.cursor()
    total_records = 0
    files_processed = 0
    
    for file_path in json_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            symbol = data.get('Symbol')
            historical_data = data.get('Historical_Data', [])
            
            if not symbol or not historical_data:
                print(f"Skipping {os.path.basename(file_path)}: Missing symbol or data")
                continue
                
            # Ensure stock exists in stocks table (if not in CSV)
            cursor.execute('INSERT OR IGNORE INTO stocks (symbol, last_updated) VALUES (?, ?)', 
                           (symbol, datetime.now().isoformat()))
            
            # Prepare bulk insert
            records = []
            for row in historical_data:
                records.append((
                    symbol,
                    row['Date'],
                    row['Open'],
                    row['High'],
                    row['Low'],
                    row['Close'],
                    row['Volume'],
                    row.get('Dividends', 0.0),
                    row.get('Stock Splits', 0.0)
                ))
                
            cursor.executemany('''
                INSERT OR REPLACE INTO historical_prices 
                (symbol, date, open, high, low, close, volume, dividends, stock_splits)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', records)
            
            total_records += len(records)
            files_processed += 1
            
            if files_processed % 50 == 0:
                print(f"Processed {files_processed}/{len(json_files)} files...")
                conn.commit()  # Commit periodically
                
        except Exception as e:
            print(f"Error processing {os.path.basename(file_path)}: {e}")
            
    conn.commit()
    print(f"[OK] Successfully imported {total_records} records from {files_processed} files.")

def main():
    print("="*60)
    print("STOCK DATA MIGRATION")
    print("="*60)
    
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}.")
        print("Please run 'python init_database.py' first.")
        return

    try:
        conn = connect_db()
        migrate_companies(conn)
        migrate_historical_data(conn)
        conn.close()
        print("\nMigration completed successfully!")
    except Exception as e:
        print(f"\nCritical Error: {e}")

if __name__ == "__main__":
    main()
