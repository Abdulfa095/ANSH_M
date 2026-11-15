import requests
import json

payload = {
    "farmer_lat": 9.9452,
    "farmer_lon": 78.1518,
    "commodity": "Rice",
    "variety": "",
    "date": "2026-03-08",
    "quantity_quintals": 10,
    "state": "Tamil Nadu"
}

print(f"Sending request: {json.dumps(payload, indent=2)}")
try:
    res = requests.post("http://localhost:8000/api/v1/mandi/suggest", json=payload)
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.text[:500]}")
except Exception as e:
    print(f"Failed to fetch! {e}")
