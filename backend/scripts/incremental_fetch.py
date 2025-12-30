#!/usr/bin/env python3
"""
Incremental Stock Data Fetcher
Only fetches new data since the last update, making daily updates fast and efficient.
"""

import sqlite3
import requests
import pandas as pd
from datetime import datetime, timedelta
import logging
import concurrent.futures
import time
import re

# Configure logging
logging.basicConfig(
    filename='../logs/backend.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

DB_PATH = '../data/stocks.db'

def get_sp500_symbols(csv_path='../data/sp500_companies.csv'):
    """Read S&P 500 symbols from CSV."""
    try:
        df = pd.read_csv(csv_path)
        return df['Symbol'].tolist()
    except Exception as e:
        logging.error(f"Error reading S&P 500 companies: {e}")
        return []

def get_latest_date(symbol, conn):
    """Get the latest date we have data for this symbol."""
    cursor = conn.cursor()
    cursor.execute('''
        SELECT MAX(date) FROM historical_prices WHERE symbol = ?
    ''', (symbol,))
    result = cursor.fetchone()
    return result[0] if result[0] else None

def fetch_nasdaq_incremental(symbol, start_date, end_date=None):
    """
    Fetch data from NASDAQ API for date range.

    Args:
        symbol: Stock ticker
        start_date: Start date (YYYY-MM-DD or datetime)
        end_date: End date (defaults to today)
    """
    if end_date is None:
        end_date = datetime.now()

    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

    date_range = f"{start_date.strftime('%Y-%m-%d')}~{end_date.strftime('%Y-%m-%d')}"

    url = "https://charting.nasdaq.com/data/charting/historical"
    params = {"symbol": symbol, "date": date_range}
    headers = {
        "accept": "*/*",
        "referer": "https://charting.nasdaq.com/dynamic/chart.html",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)

        if response.status_code == 200:
            data = response.json()
            if 'marketData' in data and len(data['marketData']) > 0:
                market_data = data['marketData']
                df = pd.DataFrame(market_data)
                df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
                df['Dividends'] = 0.0
                df['Stock Splits'] = 0.0
                return df
            else:
                return None
        else:
            logging.error(f"NASDAQ API error for {symbol}: HTTP {response.status_code}")
            return None

    except Exception as e:
        logging.error(f"Error fetching {symbol}: {e}")
        return None

def insert_historical_data(symbol, df, conn):
    """Insert new historical price data into database."""
    if df is None or len(df) == 0:
        return 0

    cursor = conn.cursor()
    inserted = 0

    for _, row in df.iterrows():
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO historical_prices
                (symbol, date, open, high, low, close, volume, dividends, stock_splits)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
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
            inserted += 1
        except sqlite3.IntegrityError:
            pass  # Already exists
        except Exception as e:
            logging.error(f"Error inserting {symbol} {row['Date']}: {e}")

    conn.commit()
    return inserted

def ensure_stock_exists(symbol, conn):
    """Ensure stock entry exists in stocks table."""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO stocks (symbol, last_updated)
        VALUES (?, ?)
    ''', (symbol, datetime.now().isoformat()))
    conn.commit()

def incremental_fetch_symbol(symbol, conn, force_full=False):
    """
    Fetch only new data for a symbol since last update.

    Args:
        symbol: Stock ticker
        conn: Database connection
        force_full: If True, fetch all 2 years of data
    """
    ensure_stock_exists(symbol, conn)

    if force_full:
        # Fetch 2 years of data
        start_date = datetime.now() - timedelta(days=730)
        logging.info(f"{symbol}: Full fetch (2 years)")
    else:
        # Get latest date we have
        latest_date = get_latest_date(symbol, conn)

        if latest_date:
            # Fetch from day after latest date
            start_date = datetime.strptime(latest_date, '%Y-%m-%d') + timedelta(days=1)
            days_behind = (datetime.now() - start_date).days

            if days_behind <= 0:
                logging.info(f"{symbol}: Up to date (latest: {latest_date})")
                return 0

            logging.info(f"{symbol}: Incremental fetch ({days_behind} days behind)")
        else:
            # No data yet, fetch 2 years
            start_date = datetime.now() - timedelta(days=730)
            logging.info(f"{symbol}: Initial fetch (2 years)")

    # Fetch data
    df = fetch_nasdaq_incremental(symbol, start_date)

    if df is not None:
        inserted = insert_historical_data(symbol, df, conn)
        logging.info(f"{symbol}: Inserted {inserted} new records")
        return inserted
    else:
        logging.warning(f"{symbol}: No new data available")
        return 0

def incremental_fetch_all(symbols, max_workers=5, force_full=False):
    """
    Incrementally fetch new data for all symbols.

    Args:
        symbols: List of stock symbols
        max_workers: Number of parallel workers
        force_full: If True, fetch full 2 years for all stocks
    """
    print(f"Starting {'FULL' if force_full else 'INCREMENTAL'} fetch for {len(symbols)} symbols...")
    print(f"Workers: {max_workers}")
    print()

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)

    total_inserted = 0
    success_count = 0
    fail_count = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(incremental_fetch_symbol, symbol, conn, force_full): symbol
            for symbol in symbols
        }

        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            symbol = futures[future]
            try:
                inserted = future.result()
                total_inserted += inserted
                success_count += 1

                # Progress
                if i % 50 == 0:
                    print(f"Progress: {i}/{len(symbols)} symbols processed...")

                # Rate limiting
                time.sleep(0.3)

            except Exception as e:
                fail_count += 1
                logging.error(f"Error processing {symbol}: {e}")

    conn.close()

    return total_inserted, success_count, fail_count

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Incrementally fetch new stock data')
    parser.add_argument('--full', action='store_true', help='Force full 2-year fetch for all stocks')
    parser.add_argument('--workers', type=int, default=5, help='Number of parallel workers')
    args = parser.parse_args()

    print("=" * 60)
    print("INCREMENTAL STOCK DATA FETCH")
    print("=" * 60)
    print()
    print(f"Mode: {'FULL (2 years)' if args.full else 'INCREMENTAL (new data only)'}")
    print(f"Database: {DB_PATH}")
    print(f"Source: NASDAQ Charting API")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    symbols = get_sp500_symbols()
    if not symbols:
        print("❌ No symbols found")
        return

    start_time = time.time()
    total_inserted, success, failed = incremental_fetch_all(
        symbols,
        max_workers=args.workers,
        force_full=args.full
    )
    elapsed = time.time() - start_time

    print()
    print("=" * 60)
    print("FETCH COMPLETE")
    print("=" * 60)
    print(f"Total symbols: {len(symbols)}")
    print(f"Success: {success}")
    print(f"Failed: {failed}")
    print(f"New records inserted: {total_inserted}")
    print(f"Time elapsed: {elapsed:.1f} seconds")
    print()
    print("Next step: Run process_indicators.py to calculate indicators")
    print("=" * 60)

if __name__ == "__main__":
    main()
