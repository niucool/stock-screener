#!/usr/bin/env python3
"""
Stock Screener Database Initialization Script
Creates SQLite database schema for efficient stock data storage and incremental updates.
"""

import sqlite3
import os

DB_PATH = 'stocks.db'

def create_database():
    """Creates SQLite database with optimized schema for stock data."""

    # Remove existing database if present
    if os.path.exists(DB_PATH):
        print(f"Removing existing database: {DB_PATH}")
        os.remove(DB_PATH)

    print(f"Creating new database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Table 1: Stock metadata
    cursor.execute('''
        CREATE TABLE stocks (
            symbol TEXT PRIMARY KEY,
            company_name TEXT,
            sector TEXT,
            industry TEXT,
            last_updated TIMESTAMP,
            active INTEGER DEFAULT 1
        )
    ''')

    # Table 2: Historical OHLCV data (raw market data)
    cursor.execute('''
        CREATE TABLE historical_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            dividends REAL DEFAULT 0.0,
            stock_splits REAL DEFAULT 0.0,
            UNIQUE(symbol, date),
            FOREIGN KEY (symbol) REFERENCES stocks(symbol)
        )
    ''')

    # Table 3: Latest processed indicators (what the UI displays)
    cursor.execute('''
        CREATE TABLE stock_indicators (
            symbol TEXT PRIMARY KEY,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            data_age_days INTEGER,

            -- Momentum Indicators
            williams_r_14 REAL,
            williams_r_21 REAL,
            ema_13_williams_r REAL,
            rsi_14 REAL,
            rsi_21 REAL,
            macd REAL,
            macd_signal REAL,
            macd_hist REAL,
            stoch_k REAL,
            stoch_d REAL,
            roc_10 REAL,
            roc_20 REAL,
            cci_14 REAL,
            cci_20 REAL,
            mfi_14 REAL,

            -- Trend Indicators
            ema_9 REAL,
            ema_20 REAL,
            ema_50 REAL,
            ema_200 REAL,
            sma_20 REAL,
            sma_50 REAL,
            sma_200 REAL,
            adx_14 REAL,
            plus_di REAL,
            minus_di REAL,
            sar REAL,

            -- Volatility Indicators
            atr_14 REAL,
            atr_20 REAL,
            bb_upper REAL,
            bb_middle REAL,
            bb_lower REAL,
            stddev_20 REAL,
            bb_width REAL,
            atr_pct REAL,
            hist_volatility_20 REAL,

            -- Volume Indicators
            obv REAL,
            ad REAL,
            adosc REAL,
            volume_ma_20 REAL,
            volume_ma_50 REAL,
            relative_volume REAL,

            -- Price Action Metrics
            price_vs_sma20_pct REAL,
            price_vs_sma50_pct REAL,
            price_vs_sma200_pct REAL,
            bb_position REAL,
            high_52w REAL,
            low_52w REAL,
            pct_from_52w_high REAL,
            pct_from_52w_low REAL,
            range_52w_position REAL,

            last_calculated TIMESTAMP,
            FOREIGN KEY (symbol) REFERENCES stocks(symbol)
        )
    ''')

    # Create indexes for fast queries
    print("Creating indexes...")
    cursor.execute('CREATE INDEX idx_historical_symbol_date ON historical_prices(symbol, date)')
    cursor.execute('CREATE INDEX idx_historical_date ON historical_prices(date)')
    cursor.execute('CREATE INDEX idx_indicators_date ON stock_indicators(date)')

    # Indexes for common filters
    cursor.execute('CREATE INDEX idx_rsi_14 ON stock_indicators(rsi_14)')
    cursor.execute('CREATE INDEX idx_williams_r_21 ON stock_indicators(williams_r_21)')
    cursor.execute('CREATE INDEX idx_adx_14 ON stock_indicators(adx_14)')

    conn.commit()
    conn.close()

    print("✓ Database schema created successfully!")
    print()
    print("Tables created:")
    print("  - stocks: Stock metadata")
    print("  - historical_prices: Raw OHLCV data by date")
    print("  - stock_indicators: Latest processed indicators (50+ indicators)")
    print()
    print("Indexes created for optimal query performance")

def verify_database():
    """Verifies database was created correctly."""
    print("\nVerifying database structure...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"Tables: {[t[0] for t in tables]}")

    # Get all indexes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
    indexes = cursor.fetchall()
    print(f"Indexes: {len(indexes)} created")

    conn.close()
    print("✓ Verification complete!")

if __name__ == "__main__":
    print("=" * 60)
    print("STOCK SCREENER - DATABASE INITIALIZATION")
    print("=" * 60)
    print()

    create_database()
    verify_database()

    print()
    print("=" * 60)
    print("Next steps:")
    print("1. Run migration script to import existing data")
    print("2. Run incremental fetch to get latest data")
    print("3. Update Flask API to use SQLite")
    print("=" * 60)
