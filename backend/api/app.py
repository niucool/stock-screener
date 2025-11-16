# backend/api/app.py

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import pandas as pd
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(
    filename='../logs/backend.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

DATA_DIR = '../data'
PROCESSED_DIR = os.path.join(DATA_DIR, 'stocks', 'processed')
SP500_CSV = os.path.join(DATA_DIR, 'sp500_companies.csv')
CONFIG_DIR = '../config'
INDICATORS_CONFIG = os.path.join(CONFIG_DIR, 'indicators_config.json')

def load_sp500_companies():
    try:
        df = pd.read_csv(SP500_CSV)
        symbols = df['Symbol'].tolist()
        companies = df.to_dict(orient='records')
        logging.info("Loaded S&P 500 companies.")
        return companies
    except Exception as e:
        logging.error(f"Error loading S&P 500 companies: {e}")
        return []

def load_stock_data(symbol=None):
    """
    Load stock data. If symbol is provided, load data for that symbol.
    Otherwise, load all stock data.
    """
    if symbol:
        file_path = os.path.join(PROCESSED_DIR, f"{symbol}.json")
        if not os.path.exists(file_path):
            logging.warning(f"Data file for symbol {symbol} not found.")
            return None
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            logging.error(f"Error loading data for symbol {symbol}: {e}")
            return None
    else:
        # Load all stock data
        stock_data = []
        for filename in os.listdir(PROCESSED_DIR):
            if filename.endswith('.json'):
                symbol = filename.replace('.json', '')
                data = load_stock_data(symbol)
                if data:
                    stock_data.append(data)
        return stock_data


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

def apply_filters(data, filters):
    """
    Generic filter application function that works with any indicator.
    Filters format: {'indicator_name': {'from': value, 'to': value}}
    """
    for indicator, bounds in filters.items():
        if indicator not in data:
            continue

        value = data[indicator]
        if value is None:
            return False

        from_val = bounds.get('from')
        to_val = bounds.get('to')

        if from_val is not None and value < from_val:
            return False
        if to_val is not None and value > to_val:
            return False

    return True

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

        # Load all stock data
        stock_data = load_stock_data()

        if not stock_data:
            logging.warning("No stock data available to filter.")
            return jsonify({"error": "No stock data available"}), 404

        # Apply filters
        filtered_data = []
        for data in stock_data:
            # Check data age if specified
            if max_age is not None:
                data_age = data.get('Data_Age_Days', float('inf'))
                if data_age > max_age:
                    continue

            # Apply indicator filters
            if apply_filters(data, filters):
                filtered_data.append(data)

        # Sort by symbol
        filtered_data.sort(key=lambda x: x.get('Symbol', ''))

        logging.info(f"Served {len(filtered_data)} filtered stock data entries out of {len(stock_data)} total.")
        return jsonify(filtered_data), 200

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

        # Load all stock data
        stock_data = load_stock_data()

        if not stock_data:
            logging.warning("No stock data available to filter.")
            return jsonify({"error": "No stock data available"}), 404

        # Apply filters
        filtered_data = []
        for data in stock_data:
            # Check data age if specified
            if max_age is not None:
                data_age = data.get('Data_Age_Days', float('inf'))
                if data_age > max_age:
                    continue

            # Apply indicator filters
            if apply_filters(data, filters):
                filtered_data.append(data)

        # Sort results
        if sort_by in filtered_data[0] if filtered_data else {}:
            reverse = (sort_order.lower() == 'desc')
            filtered_data.sort(
                key=lambda x: x.get(sort_by, 0) if x.get(sort_by) is not None else (float('-inf') if reverse else float('inf')),
                reverse=reverse
            )

        # Apply limit
        if limit:
            filtered_data = filtered_data[:limit]

        logging.info(f"Screened {len(filtered_data)} stocks with POST filters.")
        return jsonify({
            "total": len(filtered_data),
            "results": filtered_data
        }), 200

    except Exception as e:
        logging.error(f"Error in stock screening: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/api/stock-data/<string:symbol>', methods=['GET'])
def get_stock_data(symbol):
    try:
        data = load_stock_data(symbol.upper())
        if data:
            return jsonify(data), 200
        else:
            return jsonify({"error": "Symbol not found"}), 404
    except Exception as e:
        logging.error(f"Error fetching data for {symbol}: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
