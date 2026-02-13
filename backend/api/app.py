# backend/api/app_sqlite.py

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import pandas as pd
import sqlite3
import logging
import math
from job_manager import job_manager

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(
    filename='../logs/backend.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

DATA_DIR = '../data'
DB_PATH = os.path.join(DATA_DIR, 'stocks.db')
SP500_CSV = os.path.join(DATA_DIR, 'sp500_companies.csv')
CONFIG_DIR = '../config'
INDICATORS_CONFIG = os.path.join(CONFIG_DIR, 'indicators_config.json')

# Field mapping: database column names to JSON field names (for backward compatibility)
FIELD_MAP = {
    'symbol': 'Symbol',
    'date': 'Date',
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume',
    'data_age_days': 'Data_Age_Days',
    'williams_r_14': 'Williams_R_14',
    'williams_r_21': 'Williams_R_21',
    'ema_13_williams_r': 'EMA_13_Williams_R',
    'rsi_14': 'RSI_14',
    'rsi_21': 'RSI_21',
    'macd': 'MACD',
    'macd_signal': 'MACD_Signal',
    'macd_hist': 'MACD_Hist',
    'stoch_k': 'Stoch_K',
    'stoch_d': 'Stoch_D',
    'roc_10': 'ROC_10',
    'roc_20': 'ROC_20',
    'cci_14': 'CCI_14',
    'cci_20': 'CCI_20',
    'mfi_14': 'MFI_14',
    'ema_9': 'EMA_9',
    'ema_20': 'EMA_20',
    'ema_50': 'EMA_50',
    'ema_200': 'EMA_200',
    'sma_20': 'SMA_20',
    'sma_50': 'SMA_50',
    'sma_200': 'SMA_200',
    'adx_14': 'ADX_14',
    'plus_di': 'Plus_DI',
    'minus_di': 'Minus_DI',
    'sar': 'SAR',
    'atr_14': 'ATR_14',
    'atr_20': 'ATR_20',
    'bb_upper': 'BB_Upper',
    'bb_middle': 'BB_Middle',
    'bb_lower': 'BB_Lower',
    'stddev_20': 'StdDev_20',
    'bb_width': 'BB_Width',
    'atr_pct': 'ATR_Pct',
    'hist_volatility_20': 'Hist_Volatility_20',
    'obv': 'OBV',
    'ad': 'AD',
    'adosc': 'ADOSC',
    'volume_ma_20': 'Volume_MA_20',
    'volume_ma_50': 'Volume_MA_50',
    'relative_volume': 'Relative_Volume',
    'price_vs_sma20_pct': 'Price_vs_SMA20_Pct',
    'price_vs_sma50_pct': 'Price_vs_SMA50_Pct',
    'price_vs_sma200_pct': 'Price_vs_SMA200_Pct',
    'bb_position': 'BB_Position',
    'high_52w': 'High_52w',
    'low_52w': 'Low_52w',
    'pct_from_52w_high': 'Pct_From_52w_High',
    'pct_from_52w_low': 'Pct_From_52w_Low',
    'range_52w_position': 'Range_52w_Position'
}

# Reverse mapping for query building
JSON_TO_DB_MAP = {v: k for k, v in FIELD_MAP.items()}

def get_db_connection():
    """Get SQLite database connection with proper row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Ensure text is returned as str, not bytes
    conn.text_factory = str
    return conn

def row_to_dict(row):
    """Convert SQLite row to dictionary with proper field names and JSON-safe values."""
    if row is None:
        return None

    result = {}
    for key in row.keys():
        db_field = key
        json_field = FIELD_MAP.get(db_field, db_field)
        value = row[db_field]

        # Convert bytes to string (with error handling)
        if isinstance(value, bytes):
            try:
                value = value.decode('utf-8')
            except UnicodeDecodeError:
                # Try Windows-1252 encoding as fallback
                try:
                    value = value.decode('cp1252')
                except:
                    # Last resort: replace invalid characters
                    value = value.decode('utf-8', errors='replace')

        # Convert memoryview to bytes first, then to appropriate type
        if isinstance(value, memoryview):
            value = bytes(value)

        # Handle NaN and Infinity for valid JSON
        if isinstance(value, float):
            if math.isnan(value) or math.isinf(value):
                value = None

        # Store value with proper type
        result[json_field] = value

    return result

def load_sp500_companies():
    try:
        df = pd.read_csv(SP500_CSV)
        companies = df.to_dict(orient='records')
        logging.info("Loaded S&P 500 companies.")
        return companies
    except Exception as e:
        logging.error(f"Error loading S&P 500 companies: {e}")
        return []

def load_stock_data_from_db(symbol=None, filters=None, max_age=None, sort_by=None, sort_order='asc', limit=None):
    """
    Load stock data from SQLite database with optional filtering.

    Args:
        symbol: Optional specific symbol to fetch
        filters: Dict of indicator filters {'RSI_14': {'from': 30, 'to': 70}}
        max_age: Maximum data age in days
        sort_by: Field to sort by
        sort_order: 'asc' or 'desc'
        limit: Maximum number of results
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Build query
        query = "SELECT * FROM stock_indicators WHERE 1=1"
        params = []

        # Symbol filter
        if symbol:
            query += " AND symbol = ?"
            params.append(symbol.upper())

        # Data age filter
        if max_age is not None:
            query += " AND data_age_days <= ?"
            params.append(max_age)

        # Indicator filters
        if filters:
            for indicator, bounds in filters.items():
                # Convert JSON field name to database column name
                db_field = JSON_TO_DB_MAP.get(indicator, indicator.lower())

                from_val = bounds.get('from')
                to_val = bounds.get('to')

                if from_val is not None:
                    query += f" AND {db_field} >= ?"
                    params.append(from_val)

                if to_val is not None:
                    query += f" AND {db_field} <= ?"
                    params.append(to_val)

        # Sorting
        if sort_by:
            db_sort_field = JSON_TO_DB_MAP.get(sort_by, sort_by.lower())
            order = 'DESC' if sort_order.lower() == 'desc' else 'ASC'
            query += f" ORDER BY {db_sort_field} {order}"
        else:
            query += " ORDER BY symbol ASC"

        # Limit
        if limit:
            query += f" LIMIT {int(limit)}"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Convert to dicts
        results = [row_to_dict(row) for row in rows]

        conn.close()
        return results

    except Exception as e:
        logging.error(f"Error loading stock data from DB: {e}")
        return []

def load_indicators_config():
    """Load indicators configuration from JSON file"""
    try:
        with open(INDICATORS_CONFIG, 'r') as f:
            config = json.load(f)
        logging.info("Loaded indicators configuration.")
        return config
    except Exception as e:
        logging.error(f"Error loading indicators configuration: {e}")
        return None

@app.route('/api/config/indicators', methods=['GET'])
def get_indicators_config():
    """Get the indicators configuration"""
    config = load_indicators_config()
    if config:
        return jsonify(config), 200
    else:
        return jsonify({"error": "Configuration not available"}), 500

@app.route('/api/config/presets', methods=['GET'])
def get_presets():
    """Get all preset strategies"""
    config = load_indicators_config()
    if config and 'preset_strategies' in config:
        return jsonify(config['preset_strategies']), 200
    else:
        return jsonify({"error": "Presets not available"}), 500

@app.route('/api/sp500', methods=['GET'])
def get_sp500():
    companies = load_sp500_companies()
    return jsonify(companies), 200

@app.route('/api/stock-all-data', methods=['GET'])
def get_all_stock_data():
    """
    Enhanced endpoint that supports dynamic filtering on any indicator.
    Query params: <indicator>_from and <indicator>_to for range filters
    Special params: preset (apply a preset strategy), max_age (filter by data freshness)
    """
    try:
        # Check if a preset is requested
        preset_name = request.args.get('preset')
        filters = {}

        if preset_name:
            # Load preset configuration
            config = load_indicators_config()
            if config and 'preset_strategies' in config:
                preset = config['preset_strategies'].get(preset_name)
                if preset:
                    filters = preset.get('filters', {})
                    logging.info(f"Applying preset: {preset_name}")
                else:
                    return jsonify({"error": f"Preset '{preset_name}' not found"}), 400
        else:
            # Build filters from query parameters dynamically
            for key in request.args.keys():
                if key.endswith('_from'):
                    indicator = key[:-5]  # Remove '_from'
                    from_val = request.args.get(key, type=float)
                    if indicator not in filters:
                        filters[indicator] = {}
                    filters[indicator]['from'] = from_val
                elif key.endswith('_to'):
                    indicator = key[:-3]  # Remove '_to'
                    to_val = request.args.get(key, type=float)
                    if indicator not in filters:
                        filters[indicator] = {}
                    filters[indicator]['to'] = to_val

        # Data age filter (optional)
        max_age = request.args.get('max_age', type=int)

        # Load filtered stock data from database
        stock_data = load_stock_data_from_db(filters=filters, max_age=max_age)

        if not stock_data:
            logging.warning("No stock data available matching filters.")
            return jsonify([]), 200  # Return empty array, not error

        logging.info(f"Served {len(stock_data)} filtered stock data entries.")
        return jsonify(stock_data), 200

    except Exception as e:
        logging.error(f"Error fetching all stock data: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/api/stock-screen', methods=['POST'])
def screen_stocks():
    """
    Advanced screening endpoint that accepts complex filter criteria via POST.
    Request body: {
        "filters": {"RSI_14": {"from": 30, "to": 70}, ...},
        "sort_by": "RSI_14",
        "sort_order": "desc",
        "limit": 50
    }
    """
    try:
        request_data = request.get_json()
        filters = request_data.get('filters', {})
        sort_by = request_data.get('sort_by', 'Symbol')
        sort_order = request_data.get('sort_order', 'asc')
        limit = request_data.get('limit', None)
        max_age = request_data.get('max_age', None)

        # Load filtered and sorted stock data from database
        stock_data = load_stock_data_from_db(
            filters=filters,
            max_age=max_age,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit
        )

        logging.info(f"Screened {len(stock_data)} stocks with POST filters.")
        return jsonify({
            "total": len(stock_data),
            "results": stock_data
        }), 200

    except Exception as e:
        logging.error(f"Error in stock screening: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/api/stock-data/<string:symbol>', methods=['GET'])
def get_stock_data(symbol):
    try:
        data = load_stock_data_from_db(symbol=symbol.upper())
        if data and len(data) > 0:
            return jsonify(data[0]), 200
        else:
            return jsonify({"error": "Symbol not found"}), 404
    except Exception as e:
        logging.error(f"Error fetching data for {symbol}: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# ==================== DATA REFRESH ENDPOINTS ====================

@app.route('/api/refresh-data', methods=['POST'])
def trigger_data_refresh():
    """
    Trigger a background data refresh job.
    Uses incremental fetch from NASDAQ API and recalculates indicators.
    """
    try:
        result = job_manager.start_refresh()
        status_code = 200 if result['success'] else 409  # 409 Conflict if already running
        return jsonify(result), status_code
    except Exception as e:
        logging.error(f"Error triggering data refresh: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/api/refresh-status', methods=['GET'])
def get_refresh_status():
    """
    Get current status of the data refresh job.
    Returns job state, progress, timestamps, and any errors.
    """
    try:
        status = job_manager.get_status()
        return jsonify(status), 200
    except Exception as e:
        logging.error(f"Error getting refresh status: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/refresh-reset', methods=['POST'])
def reset_refresh_status():
    """
    Reset the job status to idle (clears completed/failed states).
    Cannot reset while a job is running.
    """
    try:
        result = job_manager.reset_to_idle()
        status_code = 200 if result['success'] else 409
        return jsonify(result), status_code
    except Exception as e:
        logging.error(f"Error resetting refresh status: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

if __name__ == '__main__':
    # Enable threading to allow background jobs while serving requests
    # Disable reloader to prevent thread issues with werkzeug
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True, use_reloader=False)
