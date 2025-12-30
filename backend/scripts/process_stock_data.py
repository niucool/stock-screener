# backend/scripts/process_stock_data.py

import pandas as pd
import talib
import json
import os
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

def load_historical_data(symbol, input_dir='../data/stocks/historical'):
    """
    Loads historical stock data from a JSON file.
    """
    try:
        safe_symbol = sanitize_filename(symbol)
        filename = f"{safe_symbol}.json"
        file_path = os.path.join(input_dir, filename)
        with open(file_path, 'r') as f:
            data = json.load(f)
        logging.info(f"Loaded historical data for {symbol} from {file_path}")
        return data['Historical_Data']
    except Exception as e:
        logging.error(f"Error loading historical data for {symbol}: {e}")
        return None

def calculate_indicators(symbol, historical_data, output_dir='../data/stocks/processed'):
    """
    Calculates comprehensive technical indicators using TA-Lib and saves the processed data as a separate JSON file.
    Includes momentum, trend, volume, volatility indicators and price action metrics.
    """
    try:
        df = pd.DataFrame(historical_data)
        # Ensure necessary columns are present
        required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
        if not all(col in df.columns for col in required_columns):
            logging.error(f"Missing required columns for {symbol}. Skipping.")
            return

        # Convert data types
        df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
        df['High'] = pd.to_numeric(df['High'], errors='coerce')
        df['Low'] = pd.to_numeric(df['Low'], errors='coerce')
        df['Open'] = pd.to_numeric(df['Open'], errors='coerce')
        df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')

        # Drop rows with NaN values in critical columns
        df.dropna(subset=['Close', 'High', 'Low', 'Open', 'Volume'], inplace=True)

        if df.empty or len(df) < 200:  # Need sufficient data for long-period indicators
            logging.error(f"❌ Insufficient data for {symbol}: Only {len(df)} data points available (need 200+). This stock will be skipped.")
            return

        # ==================== MOMENTUM INDICATORS ====================

        # Williams %R (14 and 21 periods)
        df['Williams_R_14'] = talib.WILLR(df['High'], df['Low'], df['Close'], timeperiod=14)
        df['Williams_R_21'] = talib.WILLR(df['High'], df['Low'], df['Close'], timeperiod=21)

        # EMA of Williams %R
        df['EMA_13_Williams_R'] = talib.EMA(df['Williams_R_21'], timeperiod=13)

        # RSI (14 and 21 periods)
        df['RSI_14'] = talib.RSI(df['Close'], timeperiod=14)
        df['RSI_21'] = talib.RSI(df['Close'], timeperiod=21)

        # MACD (12, 26, 9)
        df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = talib.MACD(
            df['Close'], fastperiod=12, slowperiod=26, signalperiod=9
        )

        # Stochastic Oscillator (14, 3, 3)
        df['Stoch_K'], df['Stoch_D'] = talib.STOCH(
            df['High'], df['Low'], df['Close'],
            fastk_period=14, slowk_period=3, slowk_matype=0,
            slowd_period=3, slowd_matype=0
        )

        # ROC (Rate of Change) - 10 and 20 periods
        df['ROC_10'] = talib.ROC(df['Close'], timeperiod=10)
        df['ROC_20'] = talib.ROC(df['Close'], timeperiod=20)

        # CCI (Commodity Channel Index)
        df['CCI_14'] = talib.CCI(df['High'], df['Low'], df['Close'], timeperiod=14)
        df['CCI_20'] = talib.CCI(df['High'], df['Low'], df['Close'], timeperiod=20)

        # MFI (Money Flow Index) - volume-weighted RSI
        df['MFI_14'] = talib.MFI(df['High'], df['Low'], df['Close'], df['Volume'], timeperiod=14)

        # ==================== TREND INDICATORS ====================

        # Moving Averages - EMA
        df['EMA_9'] = talib.EMA(df['Close'], timeperiod=9)
        df['EMA_20'] = talib.EMA(df['Close'], timeperiod=20)
        df['EMA_50'] = talib.EMA(df['Close'], timeperiod=50)
        df['EMA_200'] = talib.EMA(df['Close'], timeperiod=200)

        # Moving Averages - SMA
        df['SMA_20'] = talib.SMA(df['Close'], timeperiod=20)
        df['SMA_50'] = talib.SMA(df['Close'], timeperiod=50)
        df['SMA_200'] = talib.SMA(df['Close'], timeperiod=200)

        # ADX (Average Directional Index)
        df['ADX_14'] = talib.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
        df['Plus_DI'] = talib.PLUS_DI(df['High'], df['Low'], df['Close'], timeperiod=14)
        df['Minus_DI'] = talib.MINUS_DI(df['High'], df['Low'], df['Close'], timeperiod=14)

        # Parabolic SAR
        df['SAR'] = talib.SAR(df['High'], df['Low'], acceleration=0.02, maximum=0.2)

        # ==================== VOLATILITY INDICATORS ====================

        # ATR (Average True Range)
        df['ATR_14'] = talib.ATR(df['High'], df['Low'], df['Close'], timeperiod=14)
        df['ATR_20'] = talib.ATR(df['High'], df['Low'], df['Close'], timeperiod=20)

        # Bollinger Bands (20, 2)
        df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = talib.BBANDS(
            df['Close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0
        )

        # Standard Deviation
        df['StdDev_20'] = talib.STDDEV(df['Close'], timeperiod=20)

        # Bollinger Band Width (volatility measure)
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle'] * 100

        # ==================== VOLUME INDICATORS ====================

        # OBV (On Balance Volume)
        df['OBV'] = talib.OBV(df['Close'], df['Volume'])

        # AD (Accumulation/Distribution)
        df['AD'] = talib.AD(df['High'], df['Low'], df['Close'], df['Volume'])

        # ADOSC (Chaikin A/D Oscillator)
        df['ADOSC'] = talib.ADOSC(df['High'], df['Low'], df['Close'], df['Volume'], fastperiod=3, slowperiod=10)

        # Volume Moving Average
        df['Volume_MA_20'] = talib.SMA(df['Volume'], timeperiod=20)
        df['Volume_MA_50'] = talib.SMA(df['Volume'], timeperiod=50)

        # ==================== PRICE ACTION & CUSTOM METRICS ====================

        # Price position relative to moving averages (%)
        df['Price_vs_SMA20_Pct'] = ((df['Close'] - df['SMA_20']) / df['SMA_20']) * 100
        df['Price_vs_SMA50_Pct'] = ((df['Close'] - df['SMA_50']) / df['SMA_50']) * 100
        df['Price_vs_SMA200_Pct'] = ((df['Close'] - df['SMA_200']) / df['SMA_200']) * 100

        # Bollinger Band position (0-100 scale)
        df['BB_Position'] = ((df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])) * 100

        # Relative Volume
        df['Relative_Volume'] = df['Volume'] / df['Volume_MA_20']

        # Average True Range as % of price (normalized ATR)
        df['ATR_Pct'] = (df['ATR_14'] / df['Close']) * 100

        # 52-week high/low
        df['High_52w'] = df['High'].rolling(window=252, min_periods=1).max()
        df['Low_52w'] = df['Low'].rolling(window=252, min_periods=1).min()
        df['Pct_From_52w_High'] = ((df['Close'] - df['High_52w']) / df['High_52w']) * 100
        df['Pct_From_52w_Low'] = ((df['Close'] - df['Low_52w']) / df['Low_52w']) * 100

        # Distance from 52-week range (0-100 scale)
        df['Range_52w_Position'] = ((df['Close'] - df['Low_52w']) / (df['High_52w'] - df['Low_52w'])) * 100

        # Historical Volatility (20-day annualized)
        df['Returns'] = df['Close'].pct_change()
        df['Hist_Volatility_20'] = df['Returns'].rolling(window=20).std() * (252 ** 0.5) * 100

        # ==================== DATA QUALITY CHECKS ====================

        # Keep only the latest day's data
        latest = df.iloc[-1].to_dict()

        # Data quality flags
        data_age_days = (pd.Timestamp.now() - pd.to_datetime(latest['Date'])).days

        processed_data = {
            'Symbol': symbol,
            'Date': latest['Date'],
            'Open': latest['Open'],
            'High': latest['High'],
            'Low': latest['Low'],
            'Close': latest['Close'],
            'Volume': latest['Volume'],

            # Data Quality
            'Data_Age_Days': data_age_days,

            # Momentum Indicators
            'Williams_R_14': latest.get('Williams_R_14'),
            'Williams_R_21': latest.get('Williams_R_21'),
            'EMA_13_Williams_R': latest.get('EMA_13_Williams_R'),
            'RSI_14': latest.get('RSI_14'),
            'RSI_21': latest.get('RSI_21'),
            'MACD': latest.get('MACD'),
            'MACD_Signal': latest.get('MACD_Signal'),
            'MACD_Hist': latest.get('MACD_Hist'),
            'Stoch_K': latest.get('Stoch_K'),
            'Stoch_D': latest.get('Stoch_D'),
            'ROC_10': latest.get('ROC_10'),
            'ROC_20': latest.get('ROC_20'),
            'CCI_14': latest.get('CCI_14'),
            'CCI_20': latest.get('CCI_20'),
            'MFI_14': latest.get('MFI_14'),

            # Trend Indicators
            'EMA_9': latest.get('EMA_9'),
            'EMA_20': latest.get('EMA_20'),
            'EMA_50': latest.get('EMA_50'),
            'EMA_200': latest.get('EMA_200'),
            'SMA_20': latest.get('SMA_20'),
            'SMA_50': latest.get('SMA_50'),
            'SMA_200': latest.get('SMA_200'),
            'ADX_14': latest.get('ADX_14'),
            'Plus_DI': latest.get('Plus_DI'),
            'Minus_DI': latest.get('Minus_DI'),
            'SAR': latest.get('SAR'),

            # Volatility Indicators
            'ATR_14': latest.get('ATR_14'),
            'ATR_20': latest.get('ATR_20'),
            'BB_Upper': latest.get('BB_Upper'),
            'BB_Middle': latest.get('BB_Middle'),
            'BB_Lower': latest.get('BB_Lower'),
            'StdDev_20': latest.get('StdDev_20'),
            'BB_Width': latest.get('BB_Width'),
            'ATR_Pct': latest.get('ATR_Pct'),
            'Hist_Volatility_20': latest.get('Hist_Volatility_20'),

            # Volume Indicators
            'OBV': latest.get('OBV'),
            'AD': latest.get('AD'),
            'ADOSC': latest.get('ADOSC'),
            'Volume_MA_20': latest.get('Volume_MA_20'),
            'Volume_MA_50': latest.get('Volume_MA_50'),
            'Relative_Volume': latest.get('Relative_Volume'),

            # Price Action Metrics
            'Price_vs_SMA20_Pct': latest.get('Price_vs_SMA20_Pct'),
            'Price_vs_SMA50_Pct': latest.get('Price_vs_SMA50_Pct'),
            'Price_vs_SMA200_Pct': latest.get('Price_vs_SMA200_Pct'),
            'BB_Position': latest.get('BB_Position'),
            'High_52w': latest.get('High_52w'),
            'Low_52w': latest.get('Low_52w'),
            'Pct_From_52w_High': latest.get('Pct_From_52w_High'),
            'Pct_From_52w_Low': latest.get('Pct_From_52w_Low'),
            'Range_52w_Position': latest.get('Range_52w_Position')
        }

        # Save processed data
        os.makedirs(output_dir, exist_ok=True)
        safe_symbol = sanitize_filename(symbol)
        filename = f"{safe_symbol}.json"
        file_path = os.path.join(output_dir, filename)

        with open(file_path, 'w') as f:
            json.dump(processed_data, f, indent=4)

        logging.info(f"Processed data for {symbol} has been saved to {file_path}")

    except Exception as e:
        logging.error(f"Error processing data for {symbol}: {e}")

def process_symbol(symbol, input_dir='../data/stocks/historical', output_dir='../data/stocks/processed'):
    """
    Processes a single stock symbol: loads historical data, calculates indicators, and saves processed data.
    """
    historical_data = load_historical_data(symbol, input_dir)
    if historical_data:
        calculate_indicators(symbol, historical_data, output_dir)

def process_all_symbols(symbols, input_dir='../data/stocks/historical', output_dir='../data/stocks/processed'):
    """
    Processes all stock symbols concurrently.
    """
    try:
        logging.info("Starting to process stock data...")
        os.makedirs(output_dir, exist_ok=True)

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(process_symbol, symbol, input_dir, output_dir): symbol for symbol in symbols}
            for future in concurrent.futures.as_completed(futures):
                symbol = futures[future]
                try:
                    future.result()
                    # Optional: Add a short sleep to manage resource usage
                    time.sleep(0.05)
                except Exception as e:
                    logging.error(f"Unhandled exception during processing of {symbol}: {e}")

        logging.info("Completed processing all stock data.")

    except Exception as e:
        logging.error(f"Error during processing all symbols: {e}")

def main():
    print("=" * 60)
    print("STOCK DATA PROCESSING - Starting...")
    print("=" * 60)

    symbols = get_sp500_symbols()
    if symbols:
        print(f"\nProcessing {len(symbols)} symbols...")
        print("Calculating 50+ technical indicators per stock...")
        print("This will take approximately 5-10 minutes.\n")
        process_all_symbols(symbols)
        print("\n" + "=" * 60)
        print("✓ Processing completed successfully!")
        print("=" * 60)
    else:
        logging.error("No symbols to process.")
        print("❌ Error: No symbols found in S&P 500 companies list.")

if __name__ == "__main__":
    main()
