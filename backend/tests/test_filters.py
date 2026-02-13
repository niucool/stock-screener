
import requests
import json

BASE_URL = "http://localhost:5001/api/stock-all-data"

def test_filters():
    # 1. Test with CURRENT Frontend names (Expected to FAIL or result in improper filtering)
    print("\nTest 1: Wrong Filter Names (williamsR)")
    params = {"williamsR_from": -100, "williamsR_to": 0}
    try:
        resp = requests.get(BASE_URL, params=params)
        print(f"URL: {resp.url}")
        data = resp.json()
        print(f"Results count: {len(data)}")
        # If the backend treats unknown fields as nothing, it might return ALL data, or empty if it tries to map it
        # Actually in app.py logic:
        # db_field = JSON_TO_DB_MAP.get(indicator, indicator.lower())
        # 'williamsR' -> 'williamsr' (not in DB) -> SQL error? or 0 results?
    except Exception as e:
        print(f"Error: {e}")

    # 2. Test with CORRECT Backend names
    print("\nTest 2: Correct Filter Names (Williams_R_21)")
    params = {"Williams_R_21_from": -100, "Williams_R_21_to": 0}
    try:
        resp = requests.get(BASE_URL, params=params)
        print(f"URL: {resp.url}")
        data = resp.json()
        print(f"Results count: {len(data)}")
    except Exception as e:
        print(f"Error: {e}")
        
    print("\nTest 3: Correct Filter Names (RSI_14)")
    params = {"RSI_14_from": 0, "RSI_14_to": 100}
    try:
        resp = requests.get(BASE_URL, params=params)
        print(f"URL: {resp.url}")
        data = resp.json()
        print(f"Results count: {len(data)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_filters()
