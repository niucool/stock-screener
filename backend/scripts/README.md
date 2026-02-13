# Backend Scripts Documentation

This directory contains Python scripts for fetching, processing, and analyzing stock data. The system supports two workflows: the **Modern Database Workflow** (recommended) and the **Legacy File-Based Workflow**.

## 🚀 Recommended Workflow (Database-Based)

These scripts interact directly with the SQLite database (`stocks.db`). Use this workflow for the most efficient and up-to-date operation.

### 1. `migrate_data.py` (One-Time Setup)
*   **Purpose**: Imports existing JSON data (from the legacy workflow) into the SQLite database.
*   **When to run**: Only once, after creating the database with `init_database.py`.
*   **Input**: JSON files in `../data/stocks/historical`
*   **Output**: `stocks.db`

### 2. `incremental_fetch.py` (Daily Update)
*   **Purpose**: Fetches *only new* data since the last update from the NASDAQ API. Much faster than re-downloading full history.
*   **When to run**: Daily (e.g., via cron or scheduled task).
*   **Input**: NASDAQ API
*   **Output**: Updates `historical_prices` table in `stocks.db`.

### 3. `process_indicators.py` (Daily Update)
*   **Purpose**: Calculates technical indicators (RSI, MACD, Bollinger Bands, etc.) based on the latest historical data in the database.
*   **When to run**: Daily, immediately after `incremental_fetch.py`.
*   **Input**: `historical_prices` table in `stocks.db`
*   **Output**: Updates `stock_indicators` table in `stocks.db`.

### 4. `analyze_oversold.py` (Analysis)
*   **Purpose**: Scans the database for stocks meeting specific "oversold" criteria (e.g., Williams %R < -80) and categorizes them by risk/reward potential.
*   **When to run**: Ad-hoc, whenever you want to find trading candidates.
*   **Input**: `stock_indicators` table in `stocks.db`
*   **Output**: Console report of Top Buy Candidates and High Risk stocks.

---

## 📂 Legacy Workflow (File-Based)
These scripts work with JSON files on the disk. They are slower and less efficient but kept for reference or backup.

### 1. `validate_date.py`
*   **Purpose**: Checks if the system date is correct. Important because fetching data with an incorrect system date can cause API errors.

### 2. `fetch_stock_data.py`
*   **Purpose**: Downloads full 2-year historical data for all S&P 500 companies from Yahoo Finance.
*   **Output**: JSON files in `../data/stocks/historical`.
*   **Note**: Slower than `incremental_fetch.py` as it re-downloads everything.

### 3. `process_stock_data.py`
*   **Purpose**: Reads the historical JSON files, calculates indicators, and saves processed data to new JSON files.
*   **Output**: JSON files in `../data/stocks/processed`.

### 4. `validate_data.py`
*   **Purpose**: Checks the processed JSON files for data integrity, missing fields, and freshness.

---

## 📋 Execution Order Summary

**For Daily Maintenance:**
1.  `python incremental_fetch.py`
2.  `python process_indicators.py`

**For Finding Trades:**
1.  `python analyze_oversold.py`

**For Initial Setup (if migrating):**
1.  `python migrate_data.py`
