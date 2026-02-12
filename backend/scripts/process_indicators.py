#!/usr/bin/env python
"""
Process Stock Indicators from SQLite Database
Calculates 50+ technical indicators and stores in stock_indicators table.
"""

import sqlite3
import pandas as pd
import talib
from datetime import datetime
import logging
import concurrent.futures
import time

# Configure logging
logging.basicConfig(
    filename='../logs/backend.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

DB_PATH = '../data/stocks.db'

def get_all_symbols(conn):
    """Get all stock symbols from database."""
    cursor = conn.cursor()
    cursor.execute('SELECT symbol FROM stocks WHERE active = 1')
    return [row[0] for row in cursor.fetchall()]

def load_historical_data(symbol, conn):
    """Load historical OHLCV data for a symbol from database."""
    query = '''
        SELECT date, open, high, low, close, volume
        FROM historical_prices
        WHERE symbol = ?
        ORDER BY date ASC
    '''
    df = pd.read_sql_query(query, conn, params=(symbol,))
    return df

def calculate_and_store_indicators(symbol, conn):
    """
    Calculate all technical indicators for a symbol and store latest values.
    """
    try:
        df = load_historical_data(symbol, conn)

        if df.empty or len(df) < 200:
            logging.warning(f"{symbol}: Insufficient data ({len(df)} rows, need 200+)")
            return False

        # Convert to numeric
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df['high'] = pd.to_numeric(df['high'], errors='coerce')
        df['low'] = pd.to_numeric(df['low'], errors='coerce')
        df['open'] = pd.to_numeric(df['open'], errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce')

        df.dropna(subset=['close', 'high', 'low', 'open', 'volume'], inplace=True)

        if len(df) < 200:
            logging.warning(f"{symbol}: Insufficient valid data after cleanup")
            return False

        # ==================== MOMENTUM INDICATORS ====================
        df['williams_r_14'] = talib.WILLR(df['high'], df['low'], df['close'], timeperiod=14)
        df['williams_r_21'] = talib.WILLR(df['high'], df['low'], df['close'], timeperiod=21)
        df['ema_13_williams_r'] = talib.EMA(df['williams_r_21'], timeperiod=13)
        df['rsi_14'] = talib.RSI(df['close'], timeperiod=14)
        df['rsi_21'] = talib.RSI(df['close'], timeperiod=21)

        df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(
            df['close'], fastperiod=12, slowperiod=26, signalperiod=9
        )

        df['stoch_k'], df['stoch_d'] = talib.STOCH(
            df['high'], df['low'], df['close'],
            fastk_period=14, slowk_period=3, slowk_matype=0,
            slowd_period=3, slowd_matype=0
        )

        df['roc_10'] = talib.ROC(df['close'], timeperiod=10)
        df['roc_20'] = talib.ROC(df['close'], timeperiod=20)
        df['cci_14'] = talib.CCI(df['high'], df['low'], df['close'], timeperiod=14)
        df['cci_20'] = talib.CCI(df['high'], df['low'], df['close'], timeperiod=20)
        df['mfi_14'] = talib.MFI(df['high'], df['low'], df['close'], df['volume'], timeperiod=14)

        # ==================== TREND INDICATORS ====================
        df['ema_9'] = talib.EMA(df['close'], timeperiod=9)
        df['ema_20'] = talib.EMA(df['close'], timeperiod=20)
        df['ema_50'] = talib.EMA(df['close'], timeperiod=50)
        df['ema_200'] = talib.EMA(df['close'], timeperiod=200)
        df['sma_20'] = talib.SMA(df['close'], timeperiod=20)
        df['sma_50'] = talib.SMA(df['close'], timeperiod=50)
        df['sma_200'] = talib.SMA(df['close'], timeperiod=200)

        df['adx_14'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=14)
        df['plus_di'] = talib.PLUS_DI(df['high'], df['low'], df['close'], timeperiod=14)
        df['minus_di'] = talib.MINUS_DI(df['high'], df['low'], df['close'], timeperiod=14)
        df['sar'] = talib.SAR(df['high'], df['low'], acceleration=0.02, maximum=0.2)

        # ==================== VOLATILITY INDICATORS ====================
        df['atr_14'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
        df['atr_20'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=20)

        df['bb_upper'], df['bb_middle'], df['bb_lower'] = talib.BBANDS(
            df['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0
        )

        df['stddev_20'] = talib.STDDEV(df['close'], timeperiod=20)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle'] * 100

        # ==================== VOLUME INDICATORS ====================
        df['obv'] = talib.OBV(df['close'], df['volume'])
        df['ad'] = talib.AD(df['high'], df['low'], df['close'], df['volume'])
        df['adosc'] = talib.ADOSC(df['high'], df['low'], df['close'], df['volume'], fastperiod=3, slowperiod=10)
        df['volume_ma_20'] = talib.SMA(df['volume'], timeperiod=20)
        df['volume_ma_50'] = talib.SMA(df['volume'], timeperiod=50)

        # ==================== CUSTOM PRICE ACTION METRICS ====================
        df['price_vs_sma20_pct'] = ((df['close'] - df['sma_20']) / df['sma_20']) * 100
        df['price_vs_sma50_pct'] = ((df['close'] - df['sma_50']) / df['sma_50']) * 100
        df['price_vs_sma200_pct'] = ((df['close'] - df['sma_200']) / df['sma_200']) * 100
        df['bb_position'] = ((df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])) * 100
        df['relative_volume'] = df['volume'] / df['volume_ma_20']
        df['atr_pct'] = (df['atr_14'] / df['close']) * 100

        # 52-week metrics
        df['high_52w'] = df['high'].rolling(window=252, min_periods=1).max()
        df['low_52w'] = df['low'].rolling(window=252, min_periods=1).min()
        df['pct_from_52w_high'] = ((df['close'] - df['high_52w']) / df['high_52w']) * 100
        df['pct_from_52w_low'] = ((df['close'] - df['low_52w']) / df['low_52w']) * 100
        df['range_52w_position'] = ((df['close'] - df['low_52w']) / (df['high_52w'] - df['low_52w'])) * 100

        # Historical volatility
        df['returns'] = df['close'].pct_change()
        df['hist_volatility_20'] = df['returns'].rolling(window=20).std() * (252 ** 0.5) * 100

        # Get latest row
        latest = df.iloc[-1]
        latest_date = latest['date']
        data_age_days = (pd.Timestamp.now() - pd.to_datetime(latest_date)).days

        # Convert volume to Python int (from numpy int64)
        volume_value = int(latest['volume']) if pd.notna(latest['volume']) else 0

        # Insert/update stock_indicators table
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO stock_indicators (
                symbol, date, open, high, low, close, volume, data_age_days,
                williams_r_14, williams_r_21, ema_13_williams_r, rsi_14, rsi_21,
                macd, macd_signal, macd_hist, stoch_k, stoch_d,
                roc_10, roc_20, cci_14, cci_20, mfi_14,
                ema_9, ema_20, ema_50, ema_200, sma_20, sma_50, sma_200,
                adx_14, plus_di, minus_di, sar,
                atr_14, atr_20, bb_upper, bb_middle, bb_lower, stddev_20, bb_width, atr_pct, hist_volatility_20,
                obv, ad, adosc, volume_ma_20, volume_ma_50, relative_volume,
                price_vs_sma20_pct, price_vs_sma50_pct, price_vs_sma200_pct, bb_position,
                high_52w, low_52w, pct_from_52w_high, pct_from_52w_low, range_52w_position,
                last_calculated
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?
            )
        ''', (
            symbol, latest_date, latest['open'], latest['high'], latest['low'], latest['close'], volume_value, data_age_days,
            latest.get('williams_r_14'), latest.get('williams_r_21'), latest.get('ema_13_williams_r'),
            latest.get('rsi_14'), latest.get('rsi_21'),
            latest.get('macd'), latest.get('macd_signal'), latest.get('macd_hist'),
            latest.get('stoch_k'), latest.get('stoch_d'),
            latest.get('roc_10'), latest.get('roc_20'), latest.get('cci_14'), latest.get('cci_20'), latest.get('mfi_14'),
            latest.get('ema_9'), latest.get('ema_20'), latest.get('ema_50'), latest.get('ema_200'),
            latest.get('sma_20'), latest.get('sma_50'), latest.get('sma_200'),
            latest.get('adx_14'), latest.get('plus_di'), latest.get('minus_di'), latest.get('sar'),
            latest.get('atr_14'), latest.get('atr_20'),
            latest.get('bb_upper'), latest.get('bb_middle'), latest.get('bb_lower'),
            latest.get('stddev_20'), latest.get('bb_width'), latest.get('atr_pct'), latest.get('hist_volatility_20'),
            latest.get('obv'), latest.get('ad'), latest.get('adosc'),
            latest.get('volume_ma_20'), latest.get('volume_ma_50'), latest.get('relative_volume'),
            latest.get('price_vs_sma20_pct'), latest.get('price_vs_sma50_pct'), latest.get('price_vs_sma200_pct'),
            latest.get('bb_position'),
            latest.get('high_52w'), latest.get('low_52w'),
            latest.get('pct_from_52w_high'), latest.get('pct_from_52w_low'), latest.get('range_52w_position'),
            datetime.now().isoformat()
        ))

        conn.commit()
        logging.info(f"{symbol}: Indicators calculated and stored (date: {latest_date})")
        return True

    except Exception as e:
        logging.error(f"{symbol}: Error calculating indicators: {e}")
        return False

def process_all_indicators(symbols, max_workers=10):
    """Process indicators for all symbols in parallel."""
    print(f"Processing indicators for {len(symbols)} symbols...")
    print(f"Workers: {max_workers}")
    print()

    # Use a connection per worker (SQLite doesn't like sharing across threads)
    success_count = 0
    fail_count = 0

    def process_symbol(symbol):
        conn = sqlite3.connect(DB_PATH)
        result = calculate_and_store_indicators(symbol, conn)
        conn.close()
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_symbol, symbol): symbol for symbol in symbols}

        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            symbol = futures[future]
            try:
                success = future.result()
                if success:
                    success_count += 1
                else:
                    fail_count += 1

                if i % 50 == 0:
                    print(f"Progress: {i}/{len(symbols)} symbols processed...")

                time.sleep(0.05)

            except Exception as e:
                fail_count += 1
                logging.error(f"{symbol}: Unhandled error: {e}")

    return success_count, fail_count

def main():
    print("=" * 60)
    print("PROCESS STOCK INDICATORS")
    print("=" * 60)
    print()
    print(f"Database: {DB_PATH}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    conn = sqlite3.connect(DB_PATH)
    symbols = get_all_symbols(conn)
    conn.close()

    if not symbols:
        print("❌ No symbols found in database")
        return

    start_time = time.time()
    success, failed = process_all_indicators(symbols, max_workers=10)
    elapsed = time.time() - start_time

    print()
    print("=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Total symbols: {len(symbols)}")
    print(f"Success: {success}")
    print(f"Failed: {failed}")
    print(f"Time elapsed: {elapsed:.1f} seconds")
    print()
    print("Indicators calculated: 50+")
    print("Data stored in: stock_indicators table")
    print("=" * 60)

if __name__ == "__main__":
    main()
