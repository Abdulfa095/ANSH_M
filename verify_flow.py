import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_flow():
    print("=== ANSH-M Full Flow Verification ===")
    
    # 1. Health Check
    try:
        resp = requests.get("http://localhost:8000/")
        print(f"[1] Root health check: {resp.status_code} - {resp.json().get('message')}")
    except Exception as e:
        print(f"[1] Root health check FAILED: {e}")
        return

    # 2. Auth Flow: Signup
    test_user = {
        "name": "Test User",
        "phone": "+919999999999",
        "password": "password123"
    }
    
    print("\n[2] Auth Flow: Signup")
    resp = requests.post(f"{BASE_URL}/auth/signup", json=test_user)
    if resp.status_code == 200:
        print("    Signup successful")
    elif resp.status_code == 400:
        print(f"    Signup status: {resp.json().get('detail')} (probably already exists)")
    else:
        print(f"    Signup FAILED: {resp.status_code} - {resp.text}")

    print("[2] Auth Flow: Login")
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "phone": test_user["phone"],
        "password": test_user["password"]
    })
    if resp.status_code == 200:
        token = resp.json().get("access_token")
        print("    Login successful. Token received.")
    else:
        print(f"    Login FAILED: {resp.status_code} - {resp.text}")
        return

    # 3. Mandi Suggestion Flow
    print("\n[3] Mandi Suggestion Flow")
    suggestion_payload = {
        "farmer_lat": 11.0168, # Coimbatore
        "farmer_lon": 76.9558,
        "commodity": "Onion",
        "variety": "Red",
        "quantity_quintals": 10,
        "state": "Tamil Nadu"
    }
    resp = requests.post(f"{BASE_URL}/mandi/suggest", json=suggestion_payload)
    if resp.status_code == 200:
        results = resp.json()
        print(f"    Mandi suggestions received: {len(results)} found")
        if results:
            print(f"    Top Mandi: {results[0]['mandi']} (Profit: ₹{results[0]['net_profit']:,.2f})")
    else:
        print(f"    Mandi suggestion FAILED: {resp.status_code} - {resp.text}")

    # 4. Alert Registration Flow
    print("\n[4] Alert Registration Flow")
    alert_payload = {
        "name": test_user["name"],
        "phone": test_user["phone"],
        "commodity": "Onion",
        "state": "Tamil Nadu",
        "mandi": "Madurai"
    }
    resp = requests.post(f"{BASE_URL}/alerts/register", json=alert_payload)
    if resp.status_code == 200:
        print("    Alert registration successful")
    else:
        print(f"    Alert registration FAILED: {resp.status_code} - {resp.text}")

    # 5. Admin Flow: Check registrations
    print("\n[5] Admin Flow: Verify registrations")
    resp = requests.get(f"{BASE_URL}/admin/registrations")
    if resp.status_code == 200:
        regs = resp.json()
        print(f"    Total active registrations: {len(regs)}")
        found = any(r['phone'] == test_user['phone'] for r in regs)
        print(f"    Test user found in registrations: {found}")
    else:
        print(f"    Admin check FAILED: {resp.status_code} - {resp.text}")

    # 6. Market Summary Ticker
    print("\n[6] Market Summary (Ticker)")
    resp = requests.get(f"{BASE_URL}/market/summary")
    if resp.status_code == 200:
        summary = resp.json()
        items = summary.get('items', [])
        print(f"    Ticker items: {len(items)}")
        if items:
            print(f"    Example item: {items[0]['commodity']} - ₹{items[0]['price_per_qtl']}/qtl")
    else:
        print(f"    Market summary FAILED: {resp.status_code} - {resp.text}")

    # 7. Prediction Flow
    print("\n[7] Price Prediction Flow")
    params = {
        "commodity": "Onion",
        "state": "Tamil Nadu",
        "mandi": "Madurai",
        "days": 7
    }
    resp = requests.get(f"{BASE_URL}/predict/", params=params)
    if resp.status_code == 200:
        predictions = resp.json()
        print(f"    Prediction received for {len(predictions)} days")
        if predictions:
            print(f"    Day 1 Predicted Price: ₹{predictions[0]['price_p50']:,.2f}")
    else:
        print(f"    Prediction FAILED: {resp.status_code} - {resp.text}")

    print("\n=== Verification Complete ===")

if __name__ == "__main__":
    test_flow()
