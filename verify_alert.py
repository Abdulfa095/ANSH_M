import requests
BASE_URL = "http://localhost:8000/api/v1"
payload = {
    "name": "Test User",
    "phone": "+919999999999",
    "commodity": "Onion",
    "state": "Tamil Nadu",
    "mandi": "Madurai"
}
resp = requests.post(f"{BASE_URL}/alerts/register", json=payload)
print(f"Status: {resp.status_code}")
print(f"Body: {resp.text}")
