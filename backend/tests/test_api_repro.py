
import sys
import os
import json
import logging

# Add the api directory to path so we can import app
sys.path.append(os.path.join(os.path.dirname(__file__), '../api'))

try:
    from app import app
except ImportError:
    print("Error: Could not import app. Make sure you are running this from backend/tests or similar.")
    sys.exit(1)

def test_stock_all_data():
    client = app.test_client()
    
    print("Testing /api/stock-all-data...")
    try:
        response = client.get('/api/stock-all-data')
        print(f"Status Code: {response.status_code}")
        
        data = response.get_json()
        print(f"Response Type: {type(data)}")
        
        if isinstance(data, list):
            print(f"Response is a list with {len(data)} items.")
            if len(data) > 0:
                print("First item sample:")
                print(json.dumps(data[0], indent=2))
        elif isinstance(data, dict):
            print("Response is a dictionary (This might be the problem if frontend expects list!)")
            print(json.dumps(data, indent=2))
        else:
            print(f"Response data: {data}")
            
    except Exception as e:
        print(f"Exception during request: {e}")

if __name__ == "__main__":
    # Disable logging to keep output clean
    logging.disable(logging.CRITICAL)
    test_stock_all_data()
