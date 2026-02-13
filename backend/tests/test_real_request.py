
import requests
import json

def test_real_connection():
    url = "http://localhost:5001/api/stock-all-data"
    print(f"Connecting to {url}...")
    try:
        response = requests.get(url, timeout=5)
        print(f"Status Code: {response.status_code}")
        print("Headers:")
        for k, v in response.headers.items():
            print(f"  {k}: {v}")
            
        print("\nRaw Content (first 200 chars):")
        print(response.text[:200])
        
        print("\nDecoding JSON...")
        if "NaN" in response.text:
            print("FOUND 'NaN' IN RESPONSE TEXT! This is likely the cause.")
        
        try:
            data = response.json()
            print(f"Successfully decoded JSON. Type: {type(data)}")
            if isinstance(data, list):
                print(f"It is a list of length {len(data)}")
            elif isinstance(data, str):
                print("It decoded to a STRING. This means double encoding!")
        except Exception as e:
            print(f"Failed to decode JSON: {e}")
            
    except Exception as e:
        print(f"Request failed: {e}")
        print("Make sure the server is actually running on port 5001.")

if __name__ == "__main__":
    test_real_connection()
