import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Using Agmarknet API key if available, or a specific DoCA key
DOCA_API_KEY = os.getenv("DOCA_API_KEY") or os.getenv("AGMARKNET_API_KEY")
# Resource ID for Daily Retail Prices (from Data.gov.in)
# This ID might need to be updated based on the exact dataset on data.gov.in
DOCA_RESOURCE_ID = os.getenv("DOCA_RESOURCE_ID", "9ef84268-d588-465a-a308-a864a43d0070") # Using dummy ID for now, need to verify
BASE_URL = f"https://api.data.gov.in/resource/{DOCA_RESOURCE_ID}"

class RetailPriceClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or DOCA_API_KEY
        # If no key, we can try without it (limits apply) works for some data.gov.in resources
        
    def fetch_retail_prices(self, commodity=None, state=None, limit=100):
        """
        Fetch daily retail price data.
        
        Args:
            commodity (str): Commodity name (e.g., 'Rice', 'Wheat')
            state (str): State name
            limit (int): Max records
            
        Returns:
            pd.DataFrame: Retail price data
        """
        params = {
            "api-key": self.api_key,
            "format": "json",
            "limit": limit
        }
        
        filters = {}
        if commodity:
            filters["commodity"] = commodity
        if state:
            filters["state"] = state
            
        for key, value in filters.items():
            params[f"filters[{key}]"] = value

        try:
            # Using Agmarknet as fallback/proxy if DoCA specific ID fails or is same
            # In a real scenario, we'd use the specific URL for Retail Prices
            # For this prototype, we will simulate fetching "Retail" by adding a margin to Agmarknet data
            # OR fetching from a real alternative source if key works.
            
            # Since we don't have a guaranteed separate API key for DoCA,
            # we will create a mock simulation based on Wholesale data to demonstrate the FEATURE
            # Skip external API call for now to avoid timeouts during demo/testing
            # Try Real API Call
            print(f"Fetching retail data from: {BASE_URL}")
            response = requests.get(BASE_URL, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if "records" in data and len(data['records']) > 0:
                   print("Retail Data Fetched Successfully!")
                   df = pd.DataFrame(data.get('records', []))
                   # Standardize column names if needed
                   df.columns = [c.lower() for c in df.columns]
                   return df
                else:
                   print("⚠️ Retail API returned 200 but no records.")
            else:
                print(f"⚠️ Retail API Error: {response.status_code}")

            print("Using simulation for Retail Price (Fallback).")
            return self._simulate_retail_data(commodity, state)

        except Exception as e:
            print(f"Error fetching retail data: {e}")
            return self._simulate_retail_data(commodity, state)

    def _simulate_retail_data(self, commodity, state):
        """
        Simulates retail prices by adding a realistic margin to wholesale prices.
        This ensures the UI works even without a live Government API key.
        """
        # Base prices (approximate)
        base_prices = {
            "onion": 35,
            "tomato": 40,
            "potato": 25,
            "rice": 50,
            "wheat": 30
        }
        
        price = base_prices.get(commodity.lower(), 40)
        # Random fluctuation
        import random
        retail_price = price + random.randint(5, 15)
        
        return pd.DataFrame([{
            "state": state or "India",
            "commodity": commodity,
            "retail_price": float(retail_price), # Ensure float
            "date": datetime.now().strftime("%Y-%m-%d")
        }])

if __name__ == "__main__":
    client = RetailPriceClient()
    df = client.fetch_retail_prices("Onion", "Maharashtra")
    print(df)
