# backend/scripts/fetch_stock_data.py

import pandas as pd
import yfinance as yf
import os
import json
from datetime import datetime
import logging
import concurrent.futures
import re
import time

# Configure logging
logging.basicConfig(
    filename='../logs/backend.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

def sanitize_filename(symbol):
    """
    Sanitizes the stock symbol to create a safe filename.
    Replaces any character that's not alphanumeric or '-' with '_'.
    """
    return re.sub(r'[^\w\-]', '_', symbol)

def get_sp500_symbols(csv_path='../data/sp500_companies.csv'):
    """
    Reads the S&P 500 companies CSV and returns a list of ticker symbols.
    """
    try:
        df = pd.read_csv(csv_path)
        symbols = df['Symbol'].tolist()
        logging.info(f"Retrieved {len(symbols)} symbols from {csv_path}.")
        return symbols
    except Exception as e:
        logging.error(f"Error reading S&P 500 companies CSV: {e}")
        return []

def fetch_and_save_historical(symbol, output_dir='../data/stocks/historical'):
    """
    Fetches the last 2 years of stock data for a given symbol and saves it as a JSON file.
    2 years provides ~500 trading days, ensuring sufficient data for long-period indicators like SMA_200.
    """
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period='2y', interval='1d')  # Fetch the last 2 years (~500 trading days)

        if hist.empty:
            logging.error(f"❌ FAILED to fetch data for {symbol}: Yahoo Finance returned no data. Possible causes: delisted stock, API issue, or incorrect system date.")
            return

        # Reset index to get 'Date' as a column
        hist.reset_index(inplace=True)

        # Convert Timestamp to string for JSON serialization
        hist['Date'] = hist['Date'].dt.strftime('%Y-%m-%d')

        # Convert DataFrame to dictionary
        data = hist.to_dict(orient='records')
        data = {
            'Symbol': symbol,
            'Historical_Data': data
        }

        # Sanitize filename
        safe_symbol = sanitize_filename(symbol)
        filename = f"{safe_symbol}.json"
        file_path = os.path.join(output_dir, filename)

        # Save to JSON
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

        logging.info(f"Fetched and saved historical data for {symbol} to {file_path}")

    except Exception as e:
        logging.error(f"Error fetching data for {symbol}: {e}")

def fetch_stock_data(symbols, output_dir='../data/stocks/historical'):
    """
    Fetches historical stock price data for the given symbols using yfinance and saves each as a separate JSON file.
    Utilizes multithreading for faster execution while respecting rate limits.
    """
    try:
        logging.info("Starting to fetch historical stock data...")
        os.makedirs(output_dir, exist_ok=True)

        # To respect rate limits, limit the number of workers and add slight delays if necessary
        max_workers = 10  # Adjust based on system capabilities and rate limits
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(fetch_and_save_historical, symbol, output_dir): symbol for symbol in symbols}
            for future in concurrent.futures.as_completed(futures):
                symbol = futures[future]
                try:
                    future.result()
                    # Optional: Add a short sleep to prevent hitting rate limits
                    time.sleep(0.1)
                except Exception as e:
                    logging.error(f"Unhandled exception for {symbol}: {e}")

        logging.info("Completed fetching historical stock data.")

    except Exception as e:
        logging.error(f"Error during stock data fetching: {e}")

def validate_system_date_check():
    """Quick system date validation before fetching data."""
    now = datetime.now()
    current_year = now.year

    # Check if year is in the future beyond reasonable bounds
    if current_year > 2025:
        error_msg = f"❌ CRITICAL: System year ({current_year}) is too far in the future! Yahoo Finance cannot provide data for future dates. Please fix your system date before fetching stock data."
        logging.error(error_msg)
        print(error_msg)
        print(f"Current system date: {now.strftime('%A, %B %d, %Y %H:%M:%S')}")
        print(f"Expected year range: 2020-2025")
        return False

    # Check if year is too far in the past
    if current_year < 2020:
        error_msg = f"⚠️ WARNING: System year ({current_year}) seems too old. Data might be stale."
        logging.warning(error_msg)
        print(error_msg)

    return True

def main():
    print("=" * 60)
    print("STOCK DATA FETCH - Starting...")
    print("=" * 60)

    # Validate system date before proceeding
    if not validate_system_date_check():
        print("\n❌ Aborting fetch due to system date issue.")
        print("To fix: Run 'sudo date MMDDhhmmYYYY' with correct date")
        print("Example: sudo date 111820052024  # Nov 18, 2024 at 20:05")
        import sys
        sys.exit(1)

    symbols = get_sp500_symbols()
    if symbols:
        print(f"\nFetching data for {len(symbols)} symbols...")
        print("This will take approximately 5-10 minutes.\n")
        fetch_stock_data(symbols)
        print("\n" + "=" * 60)
        print("✓ Fetch completed successfully!")
        print("=" * 60)
    else:
        logging.error("No symbols to fetch.")
        print("❌ Error: No symbols found in S&P 500 companies list.")

if __name__ == "__main__":
    main()
