import requests
import json

try:
    url = "http://localhost:8000/api/v1/predict/?commodity=Rice&variety=&state=Tamil%20Nadu&mandi=Madurai&date=2026-03-08&days=7"
    res = requests.get(url)
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.text[:500]}")
except Exception as e:
    print(f"Failed to fetch! {e}")
